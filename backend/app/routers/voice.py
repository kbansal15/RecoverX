"""
Voice Recovery Router.
Interactive conversational audio/text turns with Hinglish NLU, audio dialogue response, and automated action execution.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.entities import Merchant
from app.routers.auth import get_current_merchant
from app.services.recovery_service import recovery_service

router = APIRouter(prefix="/voice", tags=["Hinglish Voice Recovery"])

class VoiceTurnRequest(BaseModel):
    transcript: str

@router.post("/session/{case_id}/turn")
def voice_turn(
    case_id: str,
    req: VoiceTurnRequest,
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    """Processes a single conversational turn in Hinglish or English."""
    result = recovery_service.handle_voice_turn(
        db=db,
        case_id=case_id,
        transcript=req.transcript,
        merchant_id=current_merchant.id
    )
    return result
