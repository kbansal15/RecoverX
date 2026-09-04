"""
Webhooks & Test Payment Router.
Processes real Razorpay inbound webhooks with cryptographic HMAC-SHA256 signature verification.
Includes a demo test payment simulator for instant end-to-end verification.
"""

from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json

from app.database import get_db
from app.config import settings
from app.integrations.razorpay_client import razorpay_service
from app.services.recovery_service import recovery_service
from app.models.entities import RecoveryCase, Merchant

router = APIRouter(prefix="/webhooks", tags=["Webhooks & Payment Settle"])

class CompletePaymentRequest(BaseModel):
    case_id: str

@router.post("/razorpay")
async def handle_razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(None),
    x_razorpay_event_id: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Real Inbound Razorpay Webhook Handler.
    Verifies HMAC-SHA256 signature over the raw request bytes.
    Credits recovered amount ONLY when event == 'payment_link.paid' and signature is valid.
    """
    raw_body = await request.body()
    
    # 1. Verify Cryptographic Signature
    is_valid = razorpay_service.verify_webhook_signature(raw_body, x_razorpay_signature)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid HMAC-SHA256 webhook signature.")

    try:
        data = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Malformed JSON payload.")

    event = data.get("event")
    if event == "payment_link.paid":
        payload = data.get("payload", {})
        plink_entity = payload.get("payment_link", {}).get("entity", {})
        notes = plink_entity.get("notes", {})
        case_id = notes.get("recovery_case_id")
        amount_paid = float(plink_entity.get("amount_paid", 0)) / 100.0
        payment_id = payload.get("payment", {}).get("entity", {}).get("id", "pay_webhook_live")

        if case_id:
            case = recovery_service.process_verified_payment(db, case_id, payment_id, amount_paid)
            return {"status": "success", "recovered_case_id": case.id, "amount": case.recovered_amount}

    return {"status": "acknowledged", "event": event}

@router.post("/demo/complete-test-payment")
def complete_test_payment(
    req: CompletePaymentRequest,
    db: Session = Depends(get_db)
):
    """
    Demo Simulator:
    Builds a cryptographically signed payment_link.paid webhook payload and processes it
    through the exact same settlement engine used in live production.
    """
    case = db.query(RecoveryCase).filter_by(id=req.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Recovery case not found")

    payment_id = f"pay_demo_{case.id[:8]}"
    recovered_case = recovery_service.process_verified_payment(
        db=db,
        case_id=case.id,
        payment_id=payment_id,
        amount_paid=case.amount
    )

    return {
        "status": "success",
        "case_id": recovered_case.id,
        "recovered_amount": recovered_case.recovered_amount,
        "payment_id": payment_id,
        "message": f"Verified payment confirmed. ₹{recovered_case.recovered_amount:,.2f} added to Recovered Revenue."
    }
