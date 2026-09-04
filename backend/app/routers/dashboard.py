"""
Dashboard Metrics Router.
Calculates high-level Razorpay Merchant Overview statistics:
  - Revenue at Risk
  - Honestly Measured Recovered Revenue
  - Recovery Conversion Rate
  - Pipeline Funnel Counts
  - Intervention Distribution
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.entities import RecoveryCase, Merchant, PromiseToPay, CheckoutSession, Mandate, Invoice
from app.routers.auth import get_current_merchant

router = APIRouter(prefix="/dashboard", tags=["Dashboard Metrics"])

@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_merchant: Merchant = Depends(get_current_merchant)
):
    cases = db.query(RecoveryCase).filter_by(merchant_id=current_merchant.id).all()
    
    total_at_risk = sum(c.amount for c in cases)
    # Measured recovery: ONLY sum where status == RECOVERED
    total_recovered = sum(c.recovered_amount for c in cases if c.status == "RECOVERED")
    recovery_rate = round((total_recovered / total_at_risk * 100), 1) if total_at_risk > 0 else 0.0

    pending_approval = sum(1 for c in cases if c.status == "PENDING_APPROVAL")
    escalated_count = sum(1 for c in cases if c.status == "ESCALATED")
    recovered_count = sum(1 for c in cases if c.status == "RECOVERED")
    active_executed = sum(1 for c in cases if c.status in ["ACTION_EXECUTED", "ACTION_SCHEDULED"])
    stopped_count = sum(1 for c in cases if c.status in ["STOPPED", "EXPIRED"])

    # Scenario breakdown
    scenarios = {
        "PAYMENT_FAILURE": sum(1 for c in cases if c.scenario == "PAYMENT_FAILURE"),
        "CHECKOUT_DROPOFF": sum(1 for c in cases if c.scenario == "CHECKOUT_DROPOFF"),
        "SUBSCRIPTION_MANDATE": sum(1 for c in cases if c.scenario == "SUBSCRIPTION_MANDATE"),
        "B2B_INVOICE": sum(1 for c in cases if c.scenario == "B2B_INVOICE"),
    }

    # Interventions breakdown
    interventions = {
        "PAYMENT_LINK": sum(1 for c in cases if "PAYMENT_LINK" in (c.approved_action or "")),
        "VOICE_RECOVERY": sum(1 for c in cases if "VOICE" in (c.approved_action or "")),
        "MANDATE_RETRY": sum(1 for c in cases if "MANDATE" in (c.approved_action or "")),
        "INVOICE_CHASER": sum(1 for c in cases if "INVOICE" in (c.approved_action or "")),
        "ESCALATE": escalated_count,
        "STOP": stopped_count
    }

    # Sub-domain counts
    ptp_pending = db.query(PromiseToPay).filter_by(merchant_id=current_merchant.id, status="PENDING").count()
    dropoffs_count = db.query(CheckoutSession).filter_by(merchant_id=current_merchant.id).count()
    mandates_count = db.query(Mandate).filter_by(merchant_id=current_merchant.id).count()
    invoices_count = db.query(Invoice).filter_by(merchant_id=current_merchant.id).count()

    return {
        "total_revenue_at_risk": round(total_at_risk, 2),
        "total_revenue_recovered": round(total_recovered, 2),
        "recovery_rate_percentage": recovery_rate,
        "total_cases_count": len(cases),
        "recovered_cases_count": recovered_count,
        "pending_approval_count": pending_approval,
        "escalated_cases_count": escalated_count,
        "active_interventions_count": active_executed,
        "stopped_cases_count": stopped_count,
        "ptp_pending_count": ptp_pending,
        "scenario_counts": scenarios,
        "intervention_counts": interventions,
        "domain_counts": {
            "checkout_dropoffs": dropoffs_count,
            "mandates": mandates_count,
            "invoices": invoices_count,
            "promises_to_pay": ptp_pending
        },
        "recovery_funnel": [
            {"stage": "Risk Detected", "count": len(cases), "amount": round(total_at_risk, 2)},
            {"stage": "Diagnosed & Scored", "count": len(cases), "amount": round(total_at_risk, 2)},
            {"stage": "Plan Approved", "count": active_executed + recovered_count, "amount": round(sum(c.amount for c in cases if c.status in ["ACTION_EXECUTED", "ACTION_SCHEDULED", "RECOVERED"]), 2)},
            {"stage": "Action Dispatched", "count": active_executed + recovered_count, "amount": round(sum(c.amount for c in cases if c.status in ["ACTION_EXECUTED", "ACTION_SCHEDULED", "RECOVERED"]), 2)},
            {"stage": "Verified Recovered", "count": recovered_count, "amount": round(total_recovered, 2)}
        ]
    }
