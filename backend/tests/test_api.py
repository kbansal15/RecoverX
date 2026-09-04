"""
API End-to-End Integration Tests.
Tests FastAPI endpoints:
  - Auth demo login
  - Dashboard stats
  - Recovery case plan confirmation
  - Simulated webhook payment settlement (honestly measuring recovered money)
  - Hinglish Voice conversation turn with Promise-to-Pay creation
  - Batch evaluation run
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_demo_auth_and_dashboard():
    auth_res = client.post("/api/auth/demo")
    assert auth_res.status_code == 200
    token = auth_res.json()["token"]
    assert token is not None

    headers = {"Authorization": f"Bearer {token}"}
    dash_res = client.get("/api/dashboard/stats", headers=headers)
    assert dash_res.status_code == 200
    data = dash_res.json()
    assert "total_revenue_at_risk" in data
    assert "total_revenue_recovered" in data
    assert data["total_cases_count"] >= 8

def test_confirm_plan_and_complete_payment():
    # 1. Get demo token
    auth_res = client.post("/api/auth/demo")
    token = auth_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Find Rahul's canonical pending case (rc_canonical_2999)
    case_res = client.get("/api/recovery-cases/rc_canonical_2999", headers=headers)
    assert case_res.status_code == 200
    assert case_res.json()["amount"] == 2999.0

    # 3. Confirm recovery plan
    confirm_res = client.post("/api/recovery-cases/rc_canonical_2999/confirm-plan", headers=headers)
    assert confirm_res.status_code == 200
    assert confirm_res.json()["status"] == "ACTION_EXECUTED"
    assert confirm_res.json()["payment_link_id"].startswith("plink_test_")

    # 4. Settle payment via verified webhook simulation
    pay_res = client.post("/api/webhooks/demo/complete-test-payment", json={"case_id": "rc_canonical_2999"})
    assert pay_res.status_code == 200
    assert pay_res.json()["status"] == "success"
    assert pay_res.json()["recovered_amount"] == 2999.0

    # 5. Check dashboard updated recovered revenue
    dash_res = client.get("/api/dashboard/stats", headers=headers)
    assert dash_res.json()["total_revenue_recovered"] >= 2999.0

def test_voice_turn_hinglish_ptp():
    auth_res = client.post("/api/auth/demo")
    token = auth_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Customer says they will pay after 3 days in Hinglish
    voice_res = client.post(
        "/api/voice/session/rc_upi_timeout_4299/turn",
        json={"transcript": "Haan main 3 din baad payment kar dunga pakka"},
        headers=headers
    )
    assert voice_res.status_code == 200
    data = voice_res.json()
    assert data["intent"] == "PAY_LATER"
    assert data["promise_to_pay"] is not None
    assert "Promise-to-Pay" in data["spoken_response"]

def test_batch_evaluation_run():
    auth_res = client.post("/api/auth/demo")
    token = auth_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    eval_res = client.post("/api/evaluation/run?cases_count=50", headers=headers)
    assert eval_res.status_code == 200
    data = eval_res.json()
    assert data["total_cases"] == 50
    assert data["total_at_risk_amount"] > 0
    assert data["recovery_rate_percentage"] >= 0
    assert len(data["sample_cases"]) > 0
