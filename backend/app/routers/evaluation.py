"""
Evaluation Router.
Runs the batch evaluation tool on a 100-case synthetic dataset and provides historical benchmark reports.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
import json

from app.database import get_db
from app.models.entities import EvaluationRun, Merchant
from app.routers.auth import get_current_merchant
from app.services.evaluator import run_batch_evaluation

router = APIRouter(prefix="/evaluation", tags=["Batch Evaluation"])

@router.post("/run")
def execute_evaluation(
    cases_count: int = Query(100, ge=10, le=200),
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    results = run_batch_evaluation(db, current_merchant.id, cases_count)
    return results

@router.get("/history")
def get_evaluation_history(
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    runs = db.query(EvaluationRun).filter_by(merchant_id=current_merchant.id).order_by(EvaluationRun.created_at.desc()).limit(10).all()
    return [
        {
            "id": r.id,
            "total_cases": r.total_cases,
            "recovered_cases": r.recovered_cases,
            "total_at_risk_amount": r.total_at_risk_amount,
            "total_recovered_amount": r.total_recovered_amount,
            "recovery_rate": r.recovery_rate,
            "escalated_cases": r.escalated_cases,
            "stopped_cases": r.stopped_cases,
            "avg_recovery_score": r.avg_recovery_score,
            "run_duration_ms": r.run_duration_ms,
            "sample_cases": json.loads(r.details_json or "[]"),
            "created_at": r.created_at.isoformat()
        }
        for r in runs
    ]
