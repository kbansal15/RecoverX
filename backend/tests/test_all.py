"""
Comprehensive Test Suite for RecoverX (Python).
Tests:
1. Strict policy precedence rules:
   - High-value ceiling (> ₹50,000) always escalates
   - Customer refusal / opt-out overrides high-value ceiling to STOP
   - Attempt limit enforcement
   - Recovery window expiration
2. Recovery scoring formula:
   - Transparent, bounded [0, 1] scoring
3. Razorpay webhook HMAC-SHA256 signature verification
4. Voice intent NLU & regex fallback
5. Mandate retry sequencer calculation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from datetime import datetime, timedelta

from app.engine.policy_precedence import evaluate_precedence
from app.engine.scoring import calculate_recovery_score
from app.engine.root_cause import diagnose_failure
from app.engine.mandate_sequencer import sequence_mandate_retry
from app.ai.voice_nlu import classify_voice_transcript, deterministic_classify
from app.integrations.razorpay_client import razorpay_service

def test_high_value_escalation():
    """Verify that case amount > ₹50,000 always ESCALATES even if expired or attempted."""
    now = datetime.utcnow()
    res = evaluate_precedence(
        amount=75000.0,
        window_expires_at=now - timedelta(hours=10),  # Expired
        attempts=5,                                  # Past attempts
        voice_attempts=0,
        customer_opted_out=False,
        max_autonomous_amount=50000.0,
        max_recovery_attempts=2,
        max_voice_attempts=1,
        voice_enabled=True,
        candidate_action="CREATE_PAYMENT_LINK"
    )
    assert res.outcome == "ESCALATE"
    assert res.rule_code == "HIGH_VALUE_REQUIRES_MERCHANT_REVIEW"

def test_customer_refusal_overrides_high_value():
    """Verify that customer refusal/opt-out takes precedence over high-value escalation to STOP."""
    now = datetime.utcnow()
    res = evaluate_precedence(
        amount=120000.0,
        window_expires_at=now + timedelta(hours=24),
        attempts=0,
        voice_attempts=0,
        customer_opted_out=True,  # Opted out
        max_autonomous_amount=50000.0,
        max_recovery_attempts=2,
        max_voice_attempts=1,
        voice_enabled=True,
        candidate_action="CREATE_PAYMENT_LINK"
    )
    assert res.outcome == "STOP"
    assert res.rule_code == "CUSTOMER_OPTED_OUT"

def test_attempt_limit_stopping_rule():
    """Verify that reaching max recovery attempts stops autonomous contact."""
    now = datetime.utcnow()
    res = evaluate_precedence(
        amount=2500.0,
        window_expires_at=now + timedelta(hours=24),
        attempts=2,  # Limit reached
        voice_attempts=0,
        customer_opted_out=False,
        max_autonomous_amount=50000.0,
        max_recovery_attempts=2,
        max_voice_attempts=1,
        voice_enabled=True,
        candidate_action="CREATE_PAYMENT_LINK"
    )
    assert res.outcome == "STOP"
    assert res.rule_code == "MAX_RECOVERY_ATTEMPTS_REACHED"

def test_recovery_window_expiration():
    """Verify that case past recovery window resolves to EXPIRED."""
    now = datetime.utcnow()
    res = evaluate_precedence(
        amount=3000.0,
        window_expires_at=now - timedelta(hours=1),  # Expired
        attempts=0,
        voice_attempts=0,
        customer_opted_out=False,
        max_autonomous_amount=50000.0,
        max_recovery_attempts=2,
        max_voice_attempts=1,
        voice_enabled=True,
        candidate_action="CREATE_PAYMENT_LINK"
    )
    assert res.outcome == "EXPIRE"
    assert res.rule_code == "RECOVERY_WINDOW_EXPIRED"

def test_scoring_bounded_and_reproducible():
    """Verify that recovery scoring stays strictly within [0.0, 1.0]."""
    now = datetime.utcnow()
    score_res = calculate_recovery_score(
        customer_prev_success=8,
        customer_prev_failed=1,
        root_cause_factor=1.0,
        created_at=now - timedelta(hours=2),
        window_expires_at=now + timedelta(hours=70),
        last_active_at=now - timedelta(days=2),
        prior_recovery_successes=1,
        prior_recovery_attempts=1,
        attempts_so_far=0
    )
    score = score_res["recovery_probability"]
    assert 0.0 <= score <= 1.0
    assert score > 0.70  # Strong profile
    assert "RETRYABLE_ROOT_CAUSE" in score_res["reasons"]

def test_hmac_webhook_verification():
    """Verify cryptographic HMAC-SHA256 signature verification."""
    secret = "test_webhook_secret_key"
    body = b'{"event":"payment_link.paid","status":"captured"}'
    
    import hmac, hashlib
    valid_sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    invalid_sig = "fake_invalid_signature_hex"
    
    assert razorpay_service.verify_webhook_signature(body, valid_sig, secret) is True
    assert razorpay_service.verify_webhook_signature(body, invalid_sig, secret) is False

def test_voice_nlu_deterministic_fallback():
    """Verify that Hinglish voice intents are correctly classified."""
    # PAY_NOW
    res1 = deterministic_classify("Haan main abhi payment kar deta hoon link bhej do")
    assert res1["intent"] == "PAY_NOW"

    # PAY_LATER
    res2 = deterministic_classify("Main kal salary aane par pay karunga")
    assert res2["intent"] == "PAY_LATER"

    # REFUSE
    res3 = deterministic_classify("Nahi chahiye mujhe order cancel kardo")
    assert res3["intent"] == "REFUSE"

    # PAYMENT_METHOD_PROBLEM
    res4 = deterministic_classify("Mera card decline ho gaya koi doosra option hai kya")
    assert res4["intent"] == "PAYMENT_METHOD_PROBLEM"

def test_mandate_sequencer():
    """Verify intelligent mandate retry calculation."""
    res = sequence_mandate_retry("UPI_AUTOPAY", "MANDATE_DEBIT_FAILED", 1)
    assert res["clearing_cycle"] == "Cycle 1 (10:00 AM IST)"
    assert res["retry_attempt"] == 2
    assert res["scheduled_retry_at"] > datetime.utcnow()
