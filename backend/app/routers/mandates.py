"""
Mandates & Subscription Recovery Router.
Handles recurring payments, UPI AutoPay, e-Mandates, and intelligent debit window retry sequencing.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.entities import Mandate, Customer, Merchant
from app.routers.auth import get_current_merchant
from app.engine.mandate_sequencer import sequence_mandate_retry
from app.services.recovery_service import recovery_service

router = APIRouter(prefix="/mandates", tags=["Mandate & Subscription Recovery"])

class SimulateMandateFailureRequest(BaseModel):
    customer_id: str
    amount: float
    mandate_type: str = "UPI_AUTOPAY"
    subscription_name: str = "Pro Cloud Subscription"

@router.get("")
def list_mandates(
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    mandates = db.query(Mandate).filter_by(merchant_id=current_merchant.id).order_by(Mandate.created_at.desc()).all()
    results = []
    for m in mandates:
        cust = db.query(Customer).filter_by(id=m.customer_id).first()
        results.append({
            "id": m.id,
            "subscription_id": m.subscription_id,
            "mandate_type": m.mandate_type,
            "amount": m.amount,
            "frequency": m.frequency,
            "last_failure_code": m.last_failure_code,
            "retry_count": m.retry_count,
            "optimal_retry_window": m.optimal_retry_window,
            "scheduled_retry_at": m.scheduled_retry_at.isoformat() if m.scheduled_retry_at else None,
            "status": m.status,
            "customer": {
                "id": cust.id if cust else "",
                "name": cust.name if cust else "Subscriber",
                "email": cust.email if cust else "",
                "phone": cust.phone if cust else ""
            }
        })
    return results

@router.post("/simulate-failure")
def simulate_mandate_failure(
    req: SimulateMandateFailureRequest,
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    cust = db.query(Customer).filter_by(id=req.customer_id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")

    seq = sequence_mandate_retry(req.mandate_type, "MANDATE_DEBIT_FAILED", 1)

    mandate = Mandate(
        merchant_id=current_merchant.id,
        customer_id=req.customer_id,
        subscription_id=f"sub_{datetime.utcnow().strftime('%H%M%S')}",
        mandate_type=req.mandate_type,
        amount=req.amount,
        frequency="MONTHLY",
        last_failure_code="MANDATE_DEBIT_FAILED",
        retry_count=1,
        optimal_retry_window=seq["optimal_window_name"],
        scheduled_retry_at=seq["scheduled_retry_at"],
        status="SCHEDULED"
    )
    db.add(mandate)

    # Queue in recovery pipeline
    case = recovery_service.create_recovery_case(
        db=db,
        merchant_id=current_merchant.id,
        customer_id=req.customer_id,
        amount=req.amount,
        scenario="SUBSCRIPTION_MANDATE",
        failure_code="MANDATE_DEBIT_FAILED",
        payment_method=req.mandate_type,
        description=f"Recurring Debit Failed: {req.subscription_name}"
    )

    db.commit()
    return {
        "mandate_id": mandate.id,
        "recovery_case_id": case.id,
        "optimal_window": seq["optimal_window_name"],
        "scheduled_retry_at": seq["scheduled_retry_at"].isoformat(),
        "message": "Mandate failure captured and sequenced for optimal banking window."
    }

@router.post("/{mandate_id}/sequence-retry")
def trigger_sequencer(
    mandate_id: str,
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    mandate = db.query(Mandate).filter_by(id=mandate_id, merchant_id=current_merchant.id).first()
    if not mandate:
        raise HTTPException(status_code=404, detail="Mandate not found")

    seq = sequence_mandate_retry(mandate.mandate_type, mandate.last_failure_code, mandate.retry_count)
    mandate.optimal_retry_window = seq["optimal_window_name"]
    mandate.scheduled_retry_at = seq["scheduled_retry_at"]
    mandate.retry_count += 1
    mandate.status = "RETRIED"
    db.commit()

    return {
        "id": mandate.id,
        "retry_count": mandate.retry_count,
        "optimal_window": mandate.optimal_retry_window,
        "scheduled_retry_at": mandate.scheduled_retry_at.isoformat(),
        "status": mandate.status
    }
