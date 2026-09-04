"""
Audit Log Router.
Exposes immutable chronological audit trail of all AI decisions, policy evaluations, and payment confirmations.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
import json

from app.database import get_db
from app.models.entities import AuditLog, Merchant
from app.routers.auth import get_current_merchant

router = APIRouter(prefix="/audit-logs", tags=["Audit Trail"])

@router.get("")
def list_audit_logs(
    case_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    query = db.query(AuditLog).filter_by(merchant_id=current_merchant.id)
    if case_id:
        query = query.filter_by(recovery_case_id=case_id)
    if event_type:
        query = query.filter_by(event_type=event_type)

    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "recovery_case_id": l.recovery_case_id,
            "event_type": l.event_type,
            "decision": l.decision,
            "reason": l.reason,
            "metadata": json.loads(l.metadata_json or "{}"),
            "created_at": l.created_at.isoformat()
        }
        for l in logs
    ]
