"""
B2B Receivables Chaser Engine.
Automated progressive aging analysis, tier calculation, and recovery workflow for overdue invoices.
"""

from datetime import datetime
from typing import Dict, Any

def analyze_overdue_invoice(due_date: datetime, amount: float) -> Dict[str, Any]:
    """
    Categorizes invoice into aging buckets and recommends compliant escalation tiers:
      - Tier 1 (1 - 15 days overdue): Gentle courtesy reminder & Razorpay 1-click payment link.
      - Tier 2 (16 - 30 days overdue): Finance team notice, partial settlement option, PTP offer.
      - Tier 3 (30+ days overdue): Formal delinquency escalation, credit hold warning, merchant human review.
    """
    now = datetime.utcnow()
    days_overdue = max(1, (now - due_date).days if due_date else 5)

    if days_overdue <= 15:
        bucket = "1_15_DAYS"
        tier = 1
        action_name = "COURTESY_REMINDER_WITH_PAY_LINK"
        tone = "Cordial & Helpful"
        recommended_action = "Dispatch automated email & WhatsApp with 1-click Razorpay payment link."
    elif days_overdue <= 30:
        bucket = "16_30_DAYS"
        tier = 2
        action_name = "FINANCE_NOTICE_WITH_PTP_OFFER"
        tone = "Professional & Direct"
        recommended_action = "Dispatch finance reminder offering structured Promise-to-Pay or 50% split payment link."
    else:
        bucket = "30_PLUS_DAYS"
        tier = 3
        action_name = "MANDATORY_MERCHANT_ESCALATION"
        tone = "Urgent & Formal"
        recommended_action = "Escalate to merchant CFO/Finance team for credit review and direct customer intervention."

    return {
        "days_overdue": days_overdue,
        "aging_bucket": bucket,
        "escalation_tier": tier,
        "action_name": action_name,
        "tone": tone,
        "recommended_action": recommended_action,
        "partial_settlement_eligible": True if amount > 25000 else False
    }
