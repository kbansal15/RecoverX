"""
Demo Seed Service.
Seeds canonical demo data across all four revenue loss scenarios:
  1. Failed Payments
  2. Checkout Drop-offs
  3. Subscription / Mandate Failures
  4. B2B Overdue Invoices
Allows evaluator to reset to a clean state on demand.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.entities import (
    Merchant, Customer, RecoveryCase, CheckoutSession,
    Mandate, Invoice, PromiseToPay, AuditLog, EvaluationRun
)
from app.engine.root_cause import diagnose_failure
from app.engine.scoring import calculate_recovery_score
from app.engine.policy_precedence import evaluate_precedence
from app.engine.intervention import select_candidate_intervention
import json

DEMO_MERCHANT_ID = "merch_razorpay_demo"

def seed_demo_data(db: Session) -> dict:
    """Wipes and reseeds demo merchant and cases."""
    # 1. Clear existing demo records
    db.query(RecoveryCase).filter_by(merchant_id=DEMO_MERCHANT_ID).delete()
    db.query(CheckoutSession).filter_by(merchant_id=DEMO_MERCHANT_ID).delete()
    db.query(Mandate).filter_by(merchant_id=DEMO_MERCHANT_ID).delete()
    db.query(Invoice).filter_by(merchant_id=DEMO_MERCHANT_ID).delete()
    db.query(PromiseToPay).filter_by(merchant_id=DEMO_MERCHANT_ID).delete()
    db.query(AuditLog).filter_by(merchant_id=DEMO_MERCHANT_ID).delete()
    db.query(Customer).filter_by(merchant_id=DEMO_MERCHANT_ID).delete()
    db.query(Merchant).filter_by(id=DEMO_MERCHANT_ID).delete()
    db.commit()

    # 2. Create Demo Merchant
    merchant = Merchant(
        id=DEMO_MERCHANT_ID,
        name="Apex Digital Store (Razorpay Demo)",
        email="merchant@apexstore.demo",
        demo=True,
        max_autonomous_amount=50000.0,
        recovery_window_hours=72,
        max_recovery_attempts=2,
        max_voice_attempts=1,
        voice_enabled=True,
        opt_out_behavior="DO_NOT_CONTACT"
    )
    db.add(merchant)

    # 3. Seed Customers
    customers_data = [
        {"id": "cust_rahul_01", "name": "Rahul Sharma", "email": "rahul.sharma@recoverx.demo", "phone": "+919876543210", "succ": 8, "fail": 1, "opt": False},
        {"id": "cust_priya_02", "name": "Priya Patel", "email": "priya.patel@recoverx.demo", "phone": "+919812345678", "succ": 12, "fail": 0, "opt": False},
        {"id": "cust_amit_03", "name": "Amit Verma", "email": "amit.verma@recoverx.demo", "phone": "+919988776655", "succ": 1, "fail": 4, "opt": False},
        {"id": "cust_neha_04", "name": "Neha Gupta", "email": "neha.gupta@recoverx.demo", "phone": "+919711223344", "succ": 5, "fail": 2, "opt": True},  # Opted-out
        {"id": "cust_vikram_05", "name": "Vikram Singh (Enterprise)", "email": "vikram@techcorp.demo", "phone": "+919822334455", "succ": 20, "fail": 1, "opt": False},
        {"id": "cust_ananya_06", "name": "Ananya Roy", "email": "ananya.roy@recoverx.demo", "phone": "+919833445566", "succ": 4, "fail": 1, "opt": False},
        {"id": "cust_karan_07", "name": "Karan Malhotra", "email": "karan.m@recoverx.demo", "phone": "+919844556677", "succ": 6, "fail": 0, "opt": False},
    ]

    for c in customers_data:
        cust = Customer(
            id=c["id"],
            merchant_id=DEMO_MERCHANT_ID,
            name=c["name"],
            email=c["email"],
            phone=c["phone"],
            opted_out=c["opt"],
            prev_successful_payments=c["succ"],
            prev_failed_payments=c["fail"],
            prior_recovery_successes=1 if c["succ"] > 3 else 0,
            prior_recovery_attempts=1 if c["succ"] > 3 else 0,
            last_active_at=datetime.utcnow() - timedelta(days=2)
        )
        db.add(cust)
    db.commit()

    # Helper to evaluate case and return initialized case
    now = datetime.utcnow()
    cases_to_create = [
        # Case 1: The Canonical Reference Voice/Link Case (Rahul - ₹2,999 - Insufficient funds - Retryable)
        {
            "id": "rc_canonical_2999",
            "cust_id": "cust_rahul_01",
            "scenario": "PAYMENT_FAILURE",
            "amount": 2999.0,
            "failure_code": "CARD_INSUFFICIENT_FUNDS",
            "desc": "Debit card payment failed due to temporary insufficient funds.",
            "method": "CARD",
            "hours_ago": 2
        },
        # Case 2: High Value Case (> ₹50,000 ceiling -> Must ESCALATE, never autonomous)
        {
            "id": "rc_high_value_74999",
            "cust_id": "cust_vikram_05",
            "scenario": "PAYMENT_FAILURE",
            "amount": 74999.0,
            "failure_code": "GATEWAY_ERROR",
            "desc": "High ticket corporate order failed during gateway handshake.",
            "method": "NETBANKING",
            "hours_ago": 3
        },
        # Case 3: Customer Opted Out (Neha Gupta -> Must STOP, strictly no contact)
        {
            "id": "rc_opt_out_1499",
            "cust_id": "cust_neha_04",
            "scenario": "PAYMENT_FAILURE",
            "amount": 1499.0,
            "failure_code": "PAYMENT_TIMED_OUT",
            "desc": "Customer session expired. Customer has active opt-out flag.",
            "method": "UPI",
            "hours_ago": 1
        },
        # Case 4: Non-retryable Stolen Card (Must STOP)
        {
            "id": "rc_stolen_card_5200",
            "cust_id": "cust_amit_03",
            "scenario": "PAYMENT_FAILURE",
            "amount": 5200.0,
            "failure_code": "CARD_REPORTED_LOST_OR_STOLEN",
            "desc": "Bank reported card lost or stolen. Transaction halted.",
            "method": "CARD",
            "hours_ago": 5
        },
        # Case 5: Standard UPI Timeout (Priya - ₹4,299 - Solid probability -> Payment Link)
        {
            "id": "rc_upi_timeout_4299",
            "cust_id": "cust_priya_02",
            "scenario": "PAYMENT_FAILURE",
            "amount": 4299.0,
            "failure_code": "UPI_COLLECT_EXPIRED",
            "desc": "UPI collect request timed out on PhonePe app.",
            "method": "UPI",
            "hours_ago": 1
        },
        # Case 6: Checkout Drop-off at OTP Step (Ananya - ₹3,499)
        {
            "id": "rc_dropoff_otp_3499",
            "cust_id": "cust_ananya_06",
            "scenario": "CHECKOUT_DROPOFF",
            "amount": 3499.0,
            "failure_code": "CHECKOUT_ABANDONED_OTP",
            "desc": "Customer abandoned checkout at the bank OTP screen.",
            "method": "CHECKOUT",
            "hours_ago": 0.5
        },
        # Case 7: Subscription UPI AutoPay Failure (Karan - ₹1,999)
        {
            "id": "rc_mandate_karan_1999",
            "cust_id": "cust_karan_07",
            "scenario": "SUBSCRIPTION_MANDATE",
            "amount": 1999.0,
            "failure_code": "MANDATE_DEBIT_FAILED",
            "desc": "Recurring monthly subscription debit bounced due to month-end cycle.",
            "method": "UPI_AUTOPAY",
            "hours_ago": 6
        },
        # Case 8: Overdue B2B Invoice (Vikram - ₹48,000 - 12 days overdue)
        {
            "id": "rc_invoice_vikram_48000",
            "cust_id": "cust_vikram_05",
            "scenario": "B2B_INVOICE",
            "amount": 48000.0,
            "failure_code": "INVOICE_OVERDUE",
            "desc": "Invoice INV-2026-089 is 12 days past due date.",
            "method": "INVOICE",
            "hours_ago": 12
        }
    ]

    for c in cases_to_create:
        created_at = now - timedelta(hours=c["hours_ago"])
        window_expires = created_at + timedelta(hours=merchant.recovery_window_hours)
        cust = next(item for item in customers_data if item["id"] == c["cust_id"])

        # 1. Diagnose
        diagnosis = diagnose_failure(c["failure_code"], c["scenario"])
        
        # 2. Score
        score_res = calculate_recovery_score(
            customer_prev_success=cust["succ"],
            customer_prev_failed=cust["fail"],
            root_cause_factor=diagnosis["factor"],
            created_at=created_at,
            window_expires_at=window_expires,
            last_active_at=now - timedelta(days=2),
            prior_recovery_successes=1 if cust["succ"] > 3 else 0,
            prior_recovery_attempts=1 if cust["succ"] > 3 else 0,
            attempts_so_far=0
        )
        
        # 3. Intervene
        intervention = select_candidate_intervention(
            scenario=c["scenario"],
            root_cause=diagnosis["root_cause"],
            recovery_probability=score_res["recovery_probability"],
            voice_attempts=0,
            max_voice_attempts=merchant.max_voice_attempts,
            voice_enabled=merchant.voice_enabled
        )

        # 4. Policy Precedence Check
        policy_res = evaluate_precedence(
            amount=c["amount"],
            window_expires_at=window_expires,
            attempts=0,
            voice_attempts=0,
            customer_opted_out=cust["opt"],
            max_autonomous_amount=merchant.max_autonomous_amount,
            max_recovery_attempts=merchant.max_recovery_attempts,
            max_voice_attempts=merchant.max_voice_attempts,
            voice_enabled=merchant.voice_enabled,
            candidate_action=intervention["candidate_action"]
        )

        # Determine initial status
        if policy_res.outcome == "STOP":
            status = "STOPPED"
            approved_action = "STOP"
        elif policy_res.outcome == "ESCALATE":
            status = "ESCALATED"
            approved_action = "ESCALATE"
        elif policy_res.outcome == "EXPIRE":
            status = "EXPIRED"
            approved_action = "STOP"
        else:
            status = "PENDING_APPROVAL"
            approved_action = intervention["candidate_action"]

        rc = RecoveryCase(
            id=c["id"],
            merchant_id=DEMO_MERCHANT_ID,
            customer_id=c["cust_id"],
            scenario=c["scenario"],
            amount=c["amount"],
            currency="INR",
            status=status,
            root_cause=diagnosis["root_cause"],
            root_cause_reason=diagnosis["reason"],
            failure_code=c["failure_code"],
            failure_description=c["desc"],
            payment_method=c["method"],
            recovery_probability=score_res["recovery_probability"],
            recovery_score_reasons=json.dumps(score_res["reasons"]),
            decision_explanation=policy_res.message,
            candidate_action=intervention["candidate_action"],
            approved_action=approved_action,
            rejection_reason=policy_res.rule_code if policy_res.outcome != "APPROVE" else "",
            attempts=0,
            voice_attempts=0,
            recovered_amount=0.0,
            window_expires_at=window_expires,
            created_at=created_at
        )
        db.add(rc)

        # Add initial audit log
        log = AuditLog(
            merchant_id=DEMO_MERCHANT_ID,
            recovery_case_id=c["id"],
            event_type="CASE_INITIALIZED",
            decision=f"POLICY_{policy_res.outcome}",
            reason=policy_res.message,
            metadata_json=json.dumps({
                "amount": c["amount"],
                "probability": score_res["recovery_probability"],
                "action": intervention["candidate_action"],
                "rule_code": policy_res.rule_code
            }),
            created_at=created_at
        )
        db.add(log)

    # 4. Seed companion domain tables
    # Checkout Session
    db.add(CheckoutSession(
        id="chk_ananya_01",
        merchant_id=DEMO_MERCHANT_ID,
        customer_id="cust_ananya_06",
        amount=3499.0,
        currency="INR",
        cart_items=json.dumps([{"name": "Wireless Noise Cancelling Earbuds", "qty": 1, "price": 3499.0}]),
        dropoff_stage="OTP_VERIFICATION",
        dropoff_reason="Bank 3DS OTP expired without input",
        status="ABANDONED",
        recovery_link="https://rzp.io/i/cart_rehydrate_3499",
        abandoned_at=now - timedelta(minutes=30)
    ))

    # Mandate
    db.add(Mandate(
        id="man_karan_01",
        merchant_id=DEMO_MERCHANT_ID,
        customer_id="cust_karan_07",
        subscription_id="sub_pro_monthly_99",
        mandate_type="UPI_AUTOPAY",
        amount=1999.0,
        frequency="MONTHLY",
        last_failure_code="MANDATE_DEBIT_FAILED",
        retry_count=1,
        optimal_retry_window="Day 1-5 Salary Window, 10:00 AM IST",
        scheduled_retry_at=now + timedelta(days=2),
        status="SCHEDULED"
    ))

    # Invoice
    db.add(Invoice(
        id="inv_vikram_089",
        merchant_id=DEMO_MERCHANT_ID,
        customer_id="cust_vikram_05",
        invoice_number="INV-2026-089",
        amount=48000.0,
        due_date=now - timedelta(days=12),
        days_overdue=12,
        aging_bucket="1_15_DAYS",
        status="OVERDUE",
        current_escalation_tier=1,
        payment_link_url="https://rzp.io/i/inv_pay_48000"
    ))

    db.commit()
    return {"status": "success", "message": "Demo data seeded successfully with 8 canonical multi-scenario cases."}
