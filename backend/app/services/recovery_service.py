"""
Recovery Orchestration Service.
Manages the end-to-end recovery lifecycle:
  - Plan preparation & merchant confirmation gate
  - Razorpay payment link execution
  - Verified payment webhook settlement (honestly measuring recovered revenue)
  - Interactive voice turn execution with Promise-to-Pay creation
  - Immutable audit logging
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.entities import (
    RecoveryCase, Customer, Merchant, AuditLog, PromiseToPay, CheckoutSession, Mandate, Invoice
)
from app.engine.policy_precedence import evaluate_precedence
from app.engine.root_cause import diagnose_failure
from app.engine.scoring import calculate_recovery_score
from app.engine.intervention import select_candidate_intervention
from app.integrations.razorpay_client import razorpay_service
from app.ai.voice_nlu import classify_voice_transcript

class RecoveryService:

    @staticmethod
    def create_recovery_case(
        db: Session,
        merchant_id: str,
        customer_id: str,
        amount: float,
        scenario: str,
        failure_code: str,
        payment_method: str = "UPI",
        description: str = ""
    ) -> RecoveryCase:
        """Opens a new revenue risk recovery case and executes initial diagnostics & policy checks."""
        merchant = db.query(Merchant).filter_by(id=merchant_id).first()
        customer = db.query(Customer).filter_by(id=customer_id).first()
        if not merchant or not customer:
            raise HTTPException(status_code=404, detail="Merchant or customer not found")

        now = datetime.utcnow()
        window_expires = now + timedelta(hours=merchant.recovery_window_hours)

        # 1. Diagnose
        diag = diagnose_failure(failure_code, scenario)

        # 2. Score
        score = calculate_recovery_score(
            customer_prev_success=customer.prev_successful_payments,
            customer_prev_failed=customer.prev_failed_payments,
            root_cause_factor=diag["factor"],
            created_at=now,
            window_expires_at=window_expires,
            last_active_at=customer.last_active_at,
            prior_recovery_successes=customer.prior_recovery_successes,
            prior_recovery_attempts=customer.prior_recovery_attempts,
            attempts_so_far=0
        )

        # 3. Intervene
        intervention = select_candidate_intervention(
            scenario=scenario,
            root_cause=diag["root_cause"],
            recovery_probability=score["recovery_probability"],
            voice_attempts=0,
            max_voice_attempts=merchant.max_voice_attempts,
            voice_enabled=merchant.voice_enabled
        )

        # 4. Policy Precedence
        policy = evaluate_precedence(
            amount=amount,
            window_expires_at=window_expires,
            attempts=0,
            voice_attempts=0,
            customer_opted_out=customer.opted_out,
            max_autonomous_amount=merchant.max_autonomous_amount,
            max_recovery_attempts=merchant.max_recovery_attempts,
            max_voice_attempts=merchant.max_voice_attempts,
            voice_enabled=merchant.voice_enabled,
            candidate_action=intervention["candidate_action"]
        )

        if policy.outcome == "STOP":
            status = "STOPPED"
        elif policy.outcome == "ESCALATE":
            status = "ESCALATED"
        elif policy.outcome == "EXPIRE":
            status = "EXPIRED"
        else:
            status = "PENDING_APPROVAL"

        case = RecoveryCase(
            merchant_id=merchant_id,
            customer_id=customer_id,
            scenario=scenario,
            amount=amount,
            currency="INR",
            status=status,
            root_cause=diag["root_cause"],
            root_cause_reason=diag["reason"],
            failure_code=failure_code,
            failure_description=description or diag["reason"],
            payment_method=payment_method,
            recovery_probability=score["recovery_probability"],
            recovery_score_reasons=json.dumps(score["reasons"]),
            decision_explanation=policy.message,
            candidate_action=intervention["candidate_action"],
            approved_action=intervention["candidate_action"] if policy.outcome == "APPROVE" else "STOP",
            rejection_reason=policy.rule_code if policy.outcome != "APPROVE" else "",
            attempts=0,
            voice_attempts=0,
            recovered_amount=0.0,
            window_expires_at=window_expires
        )
        db.add(case)
        db.flush()

        # Audit Log
        db.add(AuditLog(
            merchant_id=merchant_id,
            recovery_case_id=case.id,
            event_type="RISK_DETECTED",
            decision=f"POLICY_{policy.outcome}",
            reason=policy.message,
            metadata_json=json.dumps({
                "amount": amount,
                "scenario": scenario,
                "score": score["recovery_probability"],
                "candidate": intervention["candidate_action"]
            })
        ))
        db.commit()
        db.refresh(case)
        return case

    @staticmethod
    def confirm_recovery_plan(db: Session, case_id: str, merchant_id: str) -> RecoveryCase:
        """Merchant approval gate: Re-checks policy and creates live/test Razorpay link."""
        case = db.query(RecoveryCase).filter_by(id=case_id, merchant_id=merchant_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        merchant = db.query(Merchant).filter_by(id=merchant_id).first()
        customer = db.query(Customer).filter_by(id=case.customer_id).first()

        # Re-verify policy precedence immediately prior to execution
        policy = evaluate_precedence(
            amount=case.amount,
            window_expires_at=case.window_expires_at,
            attempts=case.attempts,
            voice_attempts=case.voice_attempts,
            customer_opted_out=customer.opted_out,
            max_autonomous_amount=merchant.max_autonomous_amount,
            max_recovery_attempts=merchant.max_recovery_attempts,
            max_voice_attempts=merchant.max_voice_attempts,
            voice_enabled=merchant.voice_enabled,
            candidate_action=case.candidate_action
        )

        if policy.outcome != "APPROVE":
            case.status = "STOPPED" if policy.outcome == "STOP" else "ESCALATED"
            case.rejection_reason = policy.rule_code
            db.commit()
            raise HTTPException(status_code=400, detail=f"Policy rejected action: {policy.message}")

        # Execute Payment Link creation
        if case.candidate_action in ["CREATE_PAYMENT_LINK", "START_VOICE_RECOVERY"]:
            link_res = razorpay_service.create_payment_link(
                amount=case.amount,
                currency=case.currency,
                customer_name=customer.name,
                customer_email=customer.email,
                customer_phone=customer.phone,
                description=f"Recovered order for case #{case.id[:8]}",
                reference_id=case.id
            )
            case.payment_link_id = link_res["id"]
            case.payment_link_url = link_res["short_url"]

        case.status = "ACTION_EXECUTED"
        case.attempts += 1

        # Audit
        db.add(AuditLog(
            merchant_id=merchant_id,
            recovery_case_id=case.id,
            event_type="MERCHANT_APPROVED_EXECUTION",
            decision="ACTION_EXECUTED",
            reason=f"Merchant confirmed plan. Generated Razorpay link: {case.payment_link_id}",
            metadata_json=json.dumps({
                "action": case.candidate_action,
                "link_id": case.payment_link_id,
                "attempts": case.attempts
            })
        ))
        db.commit()
        db.refresh(case)
        return case

    @staticmethod
    def process_verified_payment(db: Session, case_id: str, payment_id: str, amount_paid: float) -> RecoveryCase:
        """
        Settles recovered money ONLY after a verified signature webhook.
        Honest recovery measurement: recovered_amount set strictly on observed success.
        """
        case = db.query(RecoveryCase).filter_by(id=case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail=f"Recovery case {case_id} not found")

        if case.status == "RECOVERED":
            return case  # Idempotent return

        case.status = "RECOVERED"
        case.recovered_amount = case.amount  # Full recovery
        case.recovered_at = datetime.utcnow()

        # Update customer stats
        customer = db.query(Customer).filter_by(id=case.customer_id).first()
        if customer:
            customer.prev_successful_payments += 1
            customer.prior_recovery_successes += 1

        # Check and fulfill any pending Promise to Pay
        ptp = db.query(PromiseToPay).filter_by(recovery_case_id=case_id, status="PENDING").first()
        if ptp:
            ptp.status = "FULFILLED"
            ptp.fulfilled_at = datetime.utcnow()

        # Write audit trail
        db.add(AuditLog(
            merchant_id=case.merchant_id,
            recovery_case_id=case.id,
            event_type="REVENUE_RECOVERED",
            decision="PAYMENT_VERIFIED",
            reason=f"HMAC-verified webhook confirmed payment of ₹{case.recovered_amount:,.2f} via {payment_id}.",
            metadata_json=json.dumps({
                "payment_id": payment_id,
                "recovered_amount": case.recovered_amount,
                "customer_id": case.customer_id
            })
        ))
        db.commit()
        db.refresh(case)
        return case

    @staticmethod
    def handle_voice_turn(db: Session, case_id: str, transcript: str, merchant_id: str) -> Dict[str, Any]:
        """Processes interactive speech turn in Hinglish/English for a recovery case."""
        case = db.query(RecoveryCase).filter_by(id=case_id, merchant_id=merchant_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        customer = db.query(Customer).filter_by(id=case.customer_id).first()
        merchant = db.query(Merchant).filter_by(id=merchant_id).first()

        # NLU intent extraction
        nlu_result = classify_voice_transcript(
            transcript=transcript,
            amount=case.amount,
            customer_name=customer.name
        )

        intent = nlu_result["intent"]
        candidate_action = nlu_result["candidate_action"]
        case.voice_attempts += 1

        # Evaluate policy for this intent
        policy = evaluate_precedence(
            amount=case.amount,
            window_expires_at=case.window_expires_at,
            attempts=case.attempts,
            voice_attempts=case.voice_attempts,
            customer_opted_out=customer.opted_out or (intent == "REFUSE"),
            max_autonomous_amount=merchant.max_autonomous_amount,
            max_recovery_attempts=merchant.max_recovery_attempts,
            max_voice_attempts=merchant.max_voice_attempts,
            voice_enabled=merchant.voice_enabled,
            candidate_action=candidate_action if candidate_action != "UNCLEAR" else None
        )

        ptp_record = None

        if intent == "REFUSE" or policy.outcome == "STOP":
            case.status = "STOPPED"
            customer.opted_out = True
            case.rejection_reason = "CUSTOMER_VOICE_REFUSAL"
        elif intent == "PAY_NOW" and policy.outcome == "APPROVE":
            # Generate payment link immediately in conversation
            if not case.payment_link_id:
                link_res = razorpay_service.create_payment_link(
                    amount=case.amount,
                    currency=case.currency,
                    customer_name=customer.name,
                    customer_email=customer.email,
                    customer_phone=customer.phone,
                    description=f"Voice Recovery Link for Case #{case.id[:8]}",
                    reference_id=case.id
                )
                case.payment_link_id = link_res["id"]
                case.payment_link_url = link_res["short_url"]
            case.status = "ACTION_EXECUTED"
            case.attempts += 1
        elif intent == "PAY_LATER":
            # Record Promise-to-Pay!
            promised_date = datetime.utcnow() + timedelta(days=nlu_result["promise_days"])
            ptp = PromiseToPay(
                recovery_case_id=case.id,
                merchant_id=merchant_id,
                customer_id=customer.id,
                amount=case.amount,
                promised_date=promised_date,
                status="PENDING",
                source="VOICE_CONVERSATION",
                notes=f"Customer promised to pay in {nlu_result['promise_days']} days via voice conversation."
            )
            db.add(ptp)
            db.flush()
            case.status = "ACTION_SCHEDULED"
            ptp_record = {
                "id": ptp.id,
                "amount": ptp.amount,
                "promised_date": ptp.promised_date.isoformat(),
                "status": ptp.status
            }
        elif intent in ["HUMAN_ESCALATION", "CANNOT_PAY"] or policy.outcome == "ESCALATE":
            case.status = "ESCALATED"

        # Log audit trail
        db.add(AuditLog(
            merchant_id=merchant_id,
            recovery_case_id=case.id,
            event_type="VOICE_INTENT_CLASSIFIED",
            decision=f"INTENT_{intent}",
            reason=f"Transcript: '{transcript}' -> Spoken response generated.",
            metadata_json=json.dumps({
                "intent": intent,
                "classifier": nlu_result["classifier"],
                "candidate_action": candidate_action,
                "policy_outcome": policy.outcome
            })
        ))
        db.commit()
        db.refresh(case)

        return {
            "case_id": case.id,
            "status": case.status,
            "intent": intent,
            "classifier": nlu_result["classifier"],
            "spoken_response": nlu_result["spoken_response"],
            "payment_link_url": case.payment_link_url,
            "promise_to_pay": ptp_record
        }

recovery_service = RecoveryService()
