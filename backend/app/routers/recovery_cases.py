"""
Recovery Cases Router.
Provides endpoints for listing, inspecting, plan confirming, and managing recovery cases.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import json

from app.database import get_db
from app.models.entities import RecoveryCase, Customer, Merchant, AuditLog
from app.routers.auth import get_current_merchant
from app.services.recovery_service import recovery_service

router = APIRouter(prefix="/recovery-cases", tags=["Recovery Cases"])

class CreateCaseRequest(BaseModel):
    customer_id: str
    amount: float
    scenario: str = "PAYMENT_FAILURE"
    failure_code: str = "CARD_INSUFFICIENT_FUNDS"
    payment_method: str = "UPI"
    description: Optional[str] = ""

@router.get("")
def list_recovery_cases(
    scenario: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    query = db.query(RecoveryCase).filter_by(merchant_id=current_merchant.id)
    if scenario and scenario != "ALL":
        query = query.filter_by(scenario=scenario)
    if status and status != "ALL":
        query = query.filter_by(status=status)
        
    cases = query.order_by(RecoveryCase.created_at.desc()).all()
    
    # Attach customer info
    result = []
    for c in cases:
        cust = db.query(Customer).filter_by(id=c.customer_id).first()
        if search and search.lower() not in (c.id + (cust.name if cust else "") + c.failure_code).lower():
            continue
        result.append({
            "id": c.id,
            "scenario": c.scenario,
            "amount": c.amount,
            "currency": c.currency,
            "status": c.status,
            "root_cause": c.root_cause,
            "failure_code": c.failure_code,
            "failure_description": c.failure_description,
            "payment_method": c.payment_method,
            "recovery_probability": c.recovery_probability,
            "recovery_score_reasons": json.loads(c.recovery_score_reasons or "[]"),
            "decision_explanation": c.decision_explanation,
            "candidate_action": c.candidate_action,
            "approved_action": c.approved_action,
            "attempts": c.attempts,
            "voice_attempts": c.voice_attempts,
            "payment_link_id": c.payment_link_id,
            "payment_link_url": c.payment_link_url,
            "recovered_amount": c.recovered_amount,
            "window_expires_at": c.window_expires_at.isoformat() if c.window_expires_at else None,
            "created_at": c.created_at.isoformat(),
            "customer": {
                "id": cust.id if cust else "",
                "name": cust.name if cust else "Unknown",
                "email": cust.email if cust else "",
                "phone": cust.phone if cust else "",
                "opted_out": cust.opted_out if cust else False,
                "prev_successful_payments": cust.prev_successful_payments if cust else 0
            }
        })
    return result

@router.get("/{case_id}")
def get_recovery_case(
    case_id: str,
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    case = db.query(RecoveryCase).filter_by(id=case_id, merchant_id=current_merchant.id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    customer = db.query(Customer).filter_by(id=case.customer_id).first()
    audit_logs = db.query(AuditLog).filter_by(recovery_case_id=case_id).order_by(AuditLog.created_at.asc()).all()

    return {
        "id": case.id,
        "scenario": case.scenario,
        "amount": case.amount,
        "currency": case.currency,
        "status": case.status,
        "root_cause": case.root_cause,
        "root_cause_reason": case.root_cause_reason,
        "failure_code": case.failure_code,
        "failure_description": case.failure_description,
        "payment_method": case.payment_method,
        "recovery_probability": case.recovery_probability,
        "recovery_score_reasons": json.loads(case.recovery_score_reasons or "[]"),
        "decision_explanation": case.decision_explanation,
        "candidate_action": case.candidate_action,
        "approved_action": case.approved_action,
        "rejection_reason": case.rejection_reason,
        "attempts": case.attempts,
        "voice_attempts": case.voice_attempts,
        "payment_link_id": case.payment_link_id,
        "payment_link_url": case.payment_link_url,
        "recovered_amount": case.recovered_amount,
        "window_expires_at": case.window_expires_at.isoformat() if case.window_expires_at else None,
        "created_at": case.created_at.isoformat(),
        "customer": {
            "id": customer.id if customer else "",
            "name": customer.name if customer else "Unknown",
            "email": customer.email if customer else "",
            "phone": customer.phone if customer else "",
            "opted_out": customer.opted_out if customer else False,
            "prev_successful_payments": customer.prev_successful_payments if customer else 0,
            "prev_failed_payments": customer.prev_failed_payments if customer else 0
        },
        "audit_trail": [
            {
                "id": log.id,
                "event_type": log.event_type,
                "decision": log.decision,
                "reason": log.reason,
                "metadata": json.loads(log.metadata_json or "{}"),
                "created_at": log.created_at.isoformat()
            }
            for log in audit_logs
        ]
    }

@router.post("")
def create_case(
    req: CreateCaseRequest,
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    case = recovery_service.create_recovery_case(
        db=db,
        merchant_id=current_merchant.id,
        customer_id=req.customer_id,
        amount=req.amount,
        scenario=req.scenario,
        failure_code=req.failure_code,
        payment_method=req.payment_method,
        description=req.description
    )
    return {"case_id": case.id, "status": case.status, "message": "Recovery case created and evaluated."}

@router.post("/{case_id}/confirm-plan")
def confirm_plan(
    case_id: str,
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    case = recovery_service.confirm_recovery_plan(db, case_id, current_merchant.id)
    return {
        "case_id": case.id,
        "status": case.status,
        "payment_link_url": case.payment_link_url,
        "payment_link_id": case.payment_link_id,
        "message": "Recovery plan approved and executed."
    }

@router.post("/{case_id}/escalate")
def manual_escalate(
    case_id: str,
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    case = db.query(RecoveryCase).filter_by(id=case_id, merchant_id=current_merchant.id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    case.status = "ESCALATED"
    db.commit()
    return {"case_id": case.id, "status": "ESCALATED"}

@router.post("/{case_id}/stop")
def manual_stop(
    case_id: str,
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    case = db.query(RecoveryCase).filter_by(id=case_id, merchant_id=current_merchant.id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    case.status = "STOPPED"
    db.commit()
    return {"case_id": case.id, "status": "STOPPED"}
