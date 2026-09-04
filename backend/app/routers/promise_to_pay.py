"""
Promise to Pay (PTP) Tracker Router.
Tracks promised payment dates, grace period compliance, fulfillment states (PENDING, FULFILLED, BROKEN).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.entities import PromiseToPay, Customer, Merchant, RecoveryCase
from app.routers.auth import get_current_merchant

router = APIRouter(prefix="/promises-to-pay", tags=["Promise to Pay Tracker"])

class CreatePTPRequest(BaseModel):
    recovery_case_id: str
    promised_days: int = 3
    notes: Optional[str] = "Customer promised payment via agent"

@router.get("")
def list_promises(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    query = db.query(PromiseToPay).filter_by(merchant_id=current_merchant.id)
    if status and status != "ALL":
        query = query.filter_by(status=status)
    ptps = query.order_by(PromiseToPay.promised_date.asc()).all()

    results = []
    now = datetime.utcnow()
    for p in ptps:
        cust = db.query(Customer).filter_by(id=p.customer_id).first()
        is_overdue = (now > p.promised_date and p.status == "PENDING")
        results.append({
            "id": p.id,
            "recovery_case_id": p.recovery_case_id,
            "amount": p.amount,
            "promised_date": p.promised_date.isoformat(),
            "status": "BROKEN" if is_overdue else p.status,
            "source": p.source,
            "notes": p.notes,
            "fulfilled_at": p.fulfilled_at.isoformat() if p.fulfilled_at else None,
            "is_overdue": is_overdue,
            "customer": {
                "id": cust.id if cust else "",
                "name": cust.name if cust else "Customer",
                "phone": cust.phone if cust else ""
            }
        })
    return results

@router.post("")
def record_promise(
    req: CreatePTPRequest,
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    case = db.query(RecoveryCase).filter_by(id=req.recovery_case_id, merchant_id=current_merchant.id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Recovery case not found")

    promised_date = datetime.utcnow() + timedelta(days=req.promised_days)
    ptp = PromiseToPay(
        recovery_case_id=case.id,
        merchant_id=current_merchant.id,
        customer_id=case.customer_id,
        amount=case.amount,
        promised_date=promised_date,
        status="PENDING",
        source="MANUAL_AGENT",
        notes=req.notes
    )
    db.add(ptp)
    case.status = "ACTION_SCHEDULED"
    db.commit()

    return {
        "ptp_id": ptp.id,
        "promised_date": ptp.promised_date.isoformat(),
        "status": "PENDING",
        "message": f"Promise to Pay recorded for {req.promised_days} days from now."
    }

@router.post("/{ptp_id}/fulfill")
def fulfill_promise(
    ptp_id: str,
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    ptp = db.query(PromiseToPay).filter_by(id=ptp_id, merchant_id=current_merchant.id).first()
    if not ptp:
        raise HTTPException(status_code=404, detail="PTP record not found")

    ptp.status = "FULFILLED"
    ptp.fulfilled_at = datetime.utcnow()
    
    # Settle associated case
    case = db.query(RecoveryCase).filter_by(id=ptp.recovery_case_id).first()
    if case:
        case.status = "RECOVERED"
        case.recovered_amount = ptp.amount
        case.recovered_at = datetime.utcnow()

    db.commit()
    return {"ptp_id": ptp.id, "status": "FULFILLED", "message": "Promise fulfilled and revenue credited."}
