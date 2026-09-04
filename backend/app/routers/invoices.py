"""
B2B Receivables & Invoices Router.
Manages overdue accounts receivables, aging bucket classification (1-15d, 16-30d, 30+d), and tiered chasers.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.entities import Invoice, Customer, Merchant
from app.routers.auth import get_current_merchant
from app.engine.b2b_chaser import analyze_overdue_invoice
from app.services.recovery_service import recovery_service

router = APIRouter(prefix="/invoices", tags=["B2B Receivables Chaser"])

class SimulateInvoiceRequest(BaseModel):
    customer_id: str
    amount: float
    days_overdue: int = 15
    invoice_number: Optional[str] = None

@router.get("")
def list_invoices(
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    invoices = db.query(Invoice).filter_by(merchant_id=current_merchant.id).order_by(Invoice.days_overdue.desc()).all()
    results = []
    for inv in invoices:
        cust = db.query(Customer).filter_by(id=inv.customer_id).first()
        results.append({
            "id": inv.id,
            "invoice_number": inv.invoice_number,
            "amount": inv.amount,
            "days_overdue": inv.days_overdue,
            "aging_bucket": inv.aging_bucket,
            "status": inv.status,
            "current_escalation_tier": inv.current_escalation_tier,
            "payment_link_url": inv.payment_link_url,
            "due_date": inv.due_date.isoformat(),
            "customer": {
                "id": cust.id if cust else "",
                "name": cust.name if cust else "Corporate Client",
                "email": cust.email if cust else "",
                "phone": cust.phone if cust else ""
            }
        })
    return results

@router.post("/simulate")
def simulate_overdue_invoice(
    req: SimulateInvoiceRequest,
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    cust = db.query(Customer).filter_by(id=req.customer_id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")

    now = datetime.utcnow()
    due_date = now - timedelta(days=req.days_overdue)
    analysis = analyze_overdue_invoice(due_date, req.amount)
    inv_num = req.invoice_number or f"INV-2026-{datetime.utcnow().strftime('%M%S')}"

    inv = Invoice(
        merchant_id=current_merchant.id,
        customer_id=req.customer_id,
        invoice_number=inv_num,
        amount=req.amount,
        due_date=due_date,
        days_overdue=req.days_overdue,
        aging_bucket=analysis["aging_bucket"],
        status="OVERDUE",
        current_escalation_tier=analysis["escalation_tier"],
        payment_link_url=f"https://rzp.io/i/inv_{inv_num}"
    )
    db.add(inv)

    # Ingest into recovery pipeline
    case = recovery_service.create_recovery_case(
        db=db,
        merchant_id=current_merchant.id,
        customer_id=req.customer_id,
        amount=req.amount,
        scenario="B2B_INVOICE",
        failure_code="INVOICE_OVERDUE",
        payment_method="INVOICE",
        description=f"Overdue Invoice #{inv_num} ({req.days_overdue} days overdue)"
    )

    db.commit()
    return {
        "invoice_id": inv.id,
        "recovery_case_id": case.id,
        "aging_bucket": analysis["aging_bucket"],
        "recommended_action": analysis["recommended_action"],
        "message": "Overdue invoice ingested and progressive chaser sequence initialized."
    }

@router.post("/{invoice_id}/chase")
def execute_chase(
    invoice_id: str,
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    inv = db.query(Invoice).filter_by(id=invoice_id, merchant_id=current_merchant.id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if inv.current_escalation_tier < 3:
        inv.current_escalation_tier += 1
    else:
        inv.status = "ESCALATED"

    db.commit()
    return {
        "invoice_id": inv.id,
        "tier": inv.current_escalation_tier,
        "status": inv.status,
        "message": f"Escalation tier updated to Tier {inv.current_escalation_tier}."
    }
