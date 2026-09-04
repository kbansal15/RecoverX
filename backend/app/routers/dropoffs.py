"""
Checkout Drop-offs Router.
Handles cart & checkout abandonment tracking, drop-off diagnostics, and 1-click cart rehydration recovery.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import json

from app.database import get_db
from app.models.entities import CheckoutSession, Customer, Merchant, RecoveryCase
from app.routers.auth import get_current_merchant
from app.services.recovery_service import recovery_service
from app.integrations.razorpay_client import razorpay_service

router = APIRouter(prefix="/checkout-dropoffs", tags=["Checkout Drop-off Recovery"])

class SimulateDropoffRequest(BaseModel):
    customer_id: str
    amount: float
    dropoff_stage: str = "OTP_VERIFICATION"
    cart_item_name: str = "Premium Leather Laptop Sleeve"

@router.get("")
def list_checkout_dropoffs(
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    dropoffs = db.query(CheckoutSession).filter_by(merchant_id=current_merchant.id).order_by(CheckoutSession.abandoned_at.desc()).all()
    results = []
    for d in dropoffs:
        cust = db.query(Customer).filter_by(id=d.customer_id).first()
        results.append({
            "id": d.id,
            "amount": d.amount,
            "currency": d.currency,
            "dropoff_stage": d.dropoff_stage,
            "dropoff_reason": d.dropoff_reason,
            "status": d.status,
            "recovery_link": d.recovery_link,
            "cart_items": json.loads(d.cart_items or "[]"),
            "abandoned_at": d.abandoned_at.isoformat(),
            "customer": {
                "id": cust.id if cust else "",
                "name": cust.name if cust else "Shopper",
                "email": cust.email if cust else "",
                "phone": cust.phone if cust else ""
            }
        })
    return results

@router.post("/simulate")
def simulate_dropoff(
    req: SimulateDropoffRequest,
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    cust = db.query(Customer).filter_by(id=req.customer_id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")

    session_id = f"chk_{datetime.utcnow().strftime('%H%M%S')}"
    dropoff_reason = "Customer dropped off at OTP screen" if req.dropoff_stage == "OTP_VERIFICATION" else "Cart abandoned at checkout payment step"
    
    chk = CheckoutSession(
        id=session_id,
        merchant_id=current_merchant.id,
        customer_id=req.customer_id,
        amount=req.amount,
        currency="INR",
        cart_items=json.dumps([{"name": req.cart_item_name, "qty": 1, "price": req.amount}]),
        dropoff_stage=req.dropoff_stage,
        dropoff_reason=dropoff_reason,
        status="ABANDONED",
        recovery_link=f"https://rzp.io/i/cart_{session_id}"
    )
    db.add(chk)

    # Ingest directly into recovery pipeline
    case = recovery_service.create_recovery_case(
        db=db,
        merchant_id=current_merchant.id,
        customer_id=req.customer_id,
        amount=req.amount,
        scenario="CHECKOUT_DROPOFF",
        failure_code="CHECKOUT_ABANDONED_OTP" if req.dropoff_stage == "OTP_VERIFICATION" else "CHECKOUT_ABANDONED_PAYMENT_METHOD",
        payment_method="CHECKOUT",
        description=f"Abandoned Cart: {req.cart_item_name}"
    )

    db.commit()
    return {
        "checkout_session_id": chk.id,
        "recovery_case_id": case.id,
        "message": "Checkout drop-off captured and recovery case queued."
    }

@router.post("/{dropoff_id}/recover")
def recover_dropoff(
    dropoff_id: str,
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    chk = db.query(CheckoutSession).filter_by(id=dropoff_id, merchant_id=current_merchant.id).first()
    if not chk:
        raise HTTPException(status_code=404, detail="Session not found")

    chk.status = "RECOVERED"
    db.commit()
    return {"id": chk.id, "status": "RECOVERED", "message": "Cart rehydration link generated and sent."}
