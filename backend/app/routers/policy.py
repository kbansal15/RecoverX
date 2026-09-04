"""
Merchant Policy Configuration Router.
Allows merchants to inspect and tune autonomous amount ceilings, recovery windows, retry limits, and voice toggles.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.entities import Merchant
from app.routers.auth import get_current_merchant

router = APIRouter(prefix="/merchant/policy", tags=["Merchant Policy Engine"])

class UpdatePolicyRequest(BaseModel):
    max_autonomous_amount: Optional[float] = None
    recovery_window_hours: Optional[int] = None
    max_recovery_attempts: Optional[int] = None
    max_voice_attempts: Optional[int] = None
    voice_enabled: Optional[bool] = None
    opt_out_behavior: Optional[str] = None

@router.get("")
def get_policy(current_merchant: Merchant = Depends(get_current_merchant)):
    return {
        "merchant_id": current_merchant.id,
        "merchant_name": current_merchant.name,
        "max_autonomous_amount": current_merchant.max_autonomous_amount,
        "recovery_window_hours": current_merchant.recovery_window_hours,
        "max_recovery_attempts": current_merchant.max_recovery_attempts,
        "max_voice_attempts": current_merchant.max_voice_attempts,
        "voice_enabled": current_merchant.voice_enabled,
        "opt_out_behavior": current_merchant.opt_out_behavior
    }

@router.put("")
def update_policy(
    req: UpdatePolicyRequest,
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    if req.max_autonomous_amount is not None:
        current_merchant.max_autonomous_amount = max(100.0, req.max_autonomous_amount)
    if req.recovery_window_hours is not None:
        current_merchant.recovery_window_hours = max(1, req.recovery_window_hours)
    if req.max_recovery_attempts is not None:
        current_merchant.max_recovery_attempts = max(1, req.max_recovery_attempts)
    if req.max_voice_attempts is not None:
        current_merchant.max_voice_attempts = max(0, req.max_voice_attempts)
    if req.voice_enabled is not None:
        current_merchant.voice_enabled = req.voice_enabled
    if req.opt_out_behavior is not None:
        current_merchant.opt_out_behavior = req.opt_out_behavior

    db.commit()
    db.refresh(current_merchant)

    return {
        "status": "success",
        "message": "Policy configurations updated successfully.",
        "policy": {
            "max_autonomous_amount": current_merchant.max_autonomous_amount,
            "recovery_window_hours": current_merchant.recovery_window_hours,
            "max_recovery_attempts": current_merchant.max_recovery_attempts,
            "max_voice_attempts": current_merchant.max_voice_attempts,
            "voice_enabled": current_merchant.voice_enabled,
            "opt_out_behavior": current_merchant.opt_out_behavior
        }
    }
