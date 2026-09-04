"""
Auth & Demo Router.
Provides instant zero-friction Demo Merchant login, JWT token issuance, and canonical demo reseeding.
"""

from datetime import datetime, timedelta
import jwt
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.config import settings
from app.models.entities import Merchant
from app.services.demo_seed import seed_demo_data, DEMO_MERCHANT_ID

router = APIRouter(prefix="/auth", tags=["Authentication & Demo"])

class AuthResponse(BaseModel):
    token: str
    merchant: dict

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def get_current_merchant(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Merchant:
    """Extracts merchant from JWT Bearer token; defaults to demo merchant for testing convenience."""
    if not authorization or not authorization.startswith("Bearer "):
        # Fallback to demo merchant if token is missing
        merchant = db.query(Merchant).filter_by(id=DEMO_MERCHANT_ID).first()
        if not merchant:
            seed_demo_data(db)
            merchant = db.query(Merchant).filter_by(id=DEMO_MERCHANT_ID).first()
        return merchant

    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        merchant_id = payload.get("sub")
        if not merchant_id:
            raise HTTPException(status_code=401, detail="Invalid token subject")
        merchant = db.query(Merchant).filter_by(id=merchant_id).first()
        if not merchant:
            raise HTTPException(status_code=401, detail="Merchant not found")
        return merchant
    except jwt.PyJWTError:
        # Fallback to demo merchant for smooth testing
        merchant = db.query(Merchant).filter_by(id=DEMO_MERCHANT_ID).first()
        if merchant:
            return merchant
        raise HTTPException(status_code=401, detail="Invalid authentication token")

@router.post("/demo", response_model=AuthResponse)
def login_demo(db: Session = Depends(get_db)):
    """Enter Demo Mode: Guarantees demo merchant exists, seeds if empty, issues JWT."""
    merchant = db.query(Merchant).filter_by(id=DEMO_MERCHANT_ID).first()
    if not merchant:
        seed_demo_data(db)
        merchant = db.query(Merchant).filter_by(id=DEMO_MERCHANT_ID).first()

    token = create_access_token({"sub": merchant.id, "email": merchant.email})
    return {
        "token": token,
        "merchant": {
            "id": merchant.id,
            "name": merchant.name,
            "email": merchant.email,
            "demo": merchant.demo,
            "max_autonomous_amount": merchant.max_autonomous_amount,
            "recovery_window_hours": merchant.recovery_window_hours,
            "voice_enabled": merchant.voice_enabled
        }
    }

@router.post("/reseed")
def reseed_demo(db: Session = Depends(get_db)):
    """Reseeds demo database to initial pristine canonical state."""
    res = seed_demo_data(db)
    return res

@router.get("/me")
def get_me(current_merchant: Merchant = Depends(get_current_merchant)):
    return {
        "id": current_merchant.id,
        "name": current_merchant.name,
        "email": current_merchant.email,
        "demo": current_merchant.demo,
        "max_autonomous_amount": current_merchant.max_autonomous_amount,
        "recovery_window_hours": current_merchant.recovery_window_hours,
        "voice_enabled": current_merchant.voice_enabled
    }
