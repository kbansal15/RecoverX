import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, ForeignKey
from app.database import Base
from app.config import settings

def generate_uuid(prefix: str = "id") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("merch"))
    name = Column(String(128), nullable=False, default="Razorpay Test Merchant")
    email = Column(String(128), nullable=False, default="merchant@recoverx.ai")
    demo = Column(Boolean, default=True)
    webhook_secret = Column(String(128), default=settings.RAZORPAY_WEBHOOK_SECRET)
    
    # Merchant Policy Configurations
    max_autonomous_amount = Column(Float, default=settings.DEFAULT_MAX_AUTONOMOUS_AMOUNT)
    recovery_window_hours = Column(Integer, default=settings.DEFAULT_RECOVERY_WINDOW_HOURS)
    max_recovery_attempts = Column(Integer, default=settings.DEFAULT_MAX_RECOVERY_ATTEMPTS)
    max_voice_attempts = Column(Integer, default=settings.DEFAULT_MAX_VOICE_ATTEMPTS)
    voice_enabled = Column(Boolean, default=settings.DEFAULT_VOICE_ENABLED)
    opt_out_behavior = Column(String(64), default=settings.DEFAULT_OPT_OUT_BEHAVIOR)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("cust"))
    merchant_id = Column(String(64), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    email = Column(String(128), nullable=False)
    phone = Column(String(32), nullable=False)
    opted_out = Column(Boolean, default=False)
    
    # Historical telemetry for transparent scoring
    prev_successful_payments = Column(Integer, default=5)
    prev_failed_payments = Column(Integer, default=1)
    prior_recovery_successes = Column(Integer, default=1)
    prior_recovery_attempts = Column(Integer, default=2)
    last_active_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class RecoveryCase(Base):
    __tablename__ = "recovery_cases"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("rc"))
    merchant_id = Column(String(64), nullable=False, index=True)
    customer_id = Column(String(64), nullable=False, index=True)
    
    # Scenarios: PAYMENT_FAILURE | CHECKOUT_DROPOFF | SUBSCRIPTION_MANDATE | B2B_INVOICE
    scenario = Column(String(64), default="PAYMENT_FAILURE")
    amount = Column(Float, nullable=False)
    currency = Column(String(8), default="INR")
    
    # State Machine: RISK_DETECTED -> ANALYZING -> ELIGIBLE -> PENDING_APPROVAL -> ACTION_EXECUTED -> RECOVERED / ESCALATED / STOPPED / EXPIRED
    status = Column(String(64), default="RISK_DETECTED", index=True)
    
    # Root Cause & Diagnosis
    root_cause = Column(String(128), default="UNKNOWN")
    root_cause_reason = Column(Text, default="")
    failure_code = Column(String(64), default="")
    failure_description = Column(Text, default="")
    payment_method = Column(String(64), default="UPI")
    
    # Scoring & Transparent Decision
    recovery_probability = Column(Float, default=0.0)
    recovery_score_reasons = Column(Text, default="[]")  # JSON string array
    decision_explanation = Column(Text, default="")
    
    # Bounded Action Candidates
    candidate_action = Column(String(64), default="")
    approved_action = Column(String(64), default="")
    rejection_reason = Column(String(128), default="")
    
    # Attempts
    attempts = Column(Integer, default=0)
    voice_attempts = Column(Integer, default=0)
    
    # Razorpay Integration fields
    payment_link_id = Column(String(128), default="")
    payment_link_url = Column(String(256), default="")
    recovered_amount = Column(Float, default=0.0)  # ONLY > 0 after verified webhook!
    recovered_at = Column(DateTime, nullable=True)
    
    # Timestamps
    window_expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CheckoutSession(Base):
    __tablename__ = "checkout_sessions"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("chk"))
    merchant_id = Column(String(64), nullable=False, index=True)
    customer_id = Column(String(64), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(8), default="INR")
    cart_items = Column(Text, default="[]")  # JSON items
    
    # Drop-off stage: CART | ADDRESS_STEP | OTP_VERIFICATION | PAYMENT_SELECTION
    dropoff_stage = Column(String(64), default="PAYMENT_SELECTION")
    dropoff_reason = Column(String(128), default="Session timeout during bank OTP")
    
    # Status: ABANDONED | RECOVERED | EXPIRED
    status = Column(String(64), default="ABANDONED")
    recovery_link = Column(String(256), default="")
    abandoned_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class Mandate(Base):
    __tablename__ = "mandates"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("man"))
    merchant_id = Column(String(64), nullable=False, index=True)
    customer_id = Column(String(64), nullable=False)
    subscription_id = Column(String(64), default="")
    mandate_type = Column(String(32), default="UPI_AUTOPAY")  # UPI_AUTOPAY, CARD_MANDATE, E_NACH
    amount = Column(Float, nullable=False)
    frequency = Column(String(32), default="MONTHLY")
    
    last_failure_code = Column(String(64), default="DEBIT_FAILED_INSUFFICIENT_FUNDS")
    retry_count = Column(Integer, default=1)
    optimal_retry_window = Column(String(128), default="Day 1-5 Salary Window, 10:00 AM IST")
    scheduled_retry_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(64), default="SCHEDULED")  # SCHEDULED, RETRIED, RECOVERED, TERMINATED
    created_at = Column(DateTime, default=datetime.utcnow)

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("inv"))
    merchant_id = Column(String(64), nullable=False, index=True)
    customer_id = Column(String(64), nullable=False)
    invoice_number = Column(String(64), nullable=False)
    amount = Column(Float, nullable=False)
    due_date = Column(DateTime, nullable=False)
    days_overdue = Column(Integer, default=5)
    aging_bucket = Column(String(32), default="1_15_DAYS")  # 1_15_DAYS, 16_30_DAYS, 30_PLUS_DAYS
    status = Column(String(32), default="OVERDUE")  # OVERDUE, RECOVERED, ESCALATED
    current_escalation_tier = Column(Integer, default=1)
    payment_link_url = Column(String(256), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

class PromiseToPay(Base):
    __tablename__ = "promises_to_pay"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("ptp"))
    recovery_case_id = Column(String(64), nullable=False, index=True)
    merchant_id = Column(String(64), nullable=False, index=True)
    customer_id = Column(String(64), nullable=False)
    amount = Column(Float, nullable=False)
    promised_date = Column(DateTime, nullable=False)
    grace_period_days = Column(Integer, default=2)
    status = Column(String(32), default="PENDING")  # PENDING, FULFILLED, BROKEN
    source = Column(String(32), default="VOICE_CONVERSATION")  # VOICE_CONVERSATION, MANUAL_AGENT
    notes = Column(Text, default="")
    fulfilled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("aud"))
    merchant_id = Column(String(64), nullable=False, index=True)
    recovery_case_id = Column(String(64), nullable=True, index=True)
    event_type = Column(String(64), nullable=False)
    decision = Column(String(64), nullable=False)
    reason = Column(Text, default="")
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(String(64), primary_key=True, default=lambda: generate_uuid("eval"))
    merchant_id = Column(String(64), nullable=False, index=True)
    total_cases = Column(Integer, default=0)
    recovered_cases = Column(Integer, default=0)
    total_at_risk_amount = Column(Float, default=0.0)
    total_recovered_amount = Column(Float, default=0.0)
    recovery_rate = Column(Float, default=0.0)
    escalated_cases = Column(Integer, default=0)
    stopped_cases = Column(Integer, default=0)
    avg_recovery_score = Column(Float, default=0.0)
    run_duration_ms = Column(Integer, default=0)
    details_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)
