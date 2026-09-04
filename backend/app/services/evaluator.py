"""
Batch Evaluation Engine.
Runs the exact production recovery pipeline across a 100-case synthetic dataset to measure:
  - Honest money recovered vs revenue at risk
  - Policy safety and escalation compliance
  - Stopping rule adherence
  - Execution speed and pipeline performance
"""

import time
import random
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.entities import EvaluationRun, Merchant
from app.engine.root_cause import diagnose_failure
from app.engine.scoring import calculate_recovery_score
from app.engine.policy_precedence import evaluate_precedence
from app.engine.intervention import select_candidate_intervention

def run_batch_evaluation(db: Session, merchant_id: str, case_count: int = 100) -> dict:
    """Executes full decision & recovery loop on a deterministic synthetic cohort."""
    start_time = time.time()
    rng = random.Random(42)  # Fixed seed for reproducible benchmarks

    merchant = db.query(Merchant).filter_by(id=merchant_id).first()
    max_amount = merchant.max_autonomous_amount if merchant else 50000.0
    recovery_window = merchant.recovery_window_hours if merchant else 72

    total_at_risk = 0.0
    total_recovered = 0.0
    recovered_count = 0
    escalated_count = 0
    stopped_count = 0
    probabilities = []

    case_results = []
    scenarios = ["PAYMENT_FAILURE", "CHECKOUT_DROPOFF", "SUBSCRIPTION_MANDATE", "B2B_INVOICE"]
    failure_codes = [
        "CARD_INSUFFICIENT_FUNDS", "GATEWAY_ERROR", "UPI_COLLECT_EXPIRED",
        "BAD_REQUEST_PAYMENT_DECLINED_BY_BANK", "CHECKOUT_ABANDONED_OTP",
        "MANDATE_DEBIT_FAILED", "CARD_REPORTED_LOST_OR_STOLEN", "CUSTOMER_CANCELLED"
    ]

    for i in range(1, case_count + 1):
        scenario = rng.choice(scenarios)
        code = rng.choice(failure_codes)
        
        # Determine amount: 90% within policy ceiling, 10% high-value
        is_high_value = (i % 10 == 0)
        if is_high_value:
            amount = rng.uniform(55000.0, 150000.0)
        else:
            amount = rng.uniform(500.0, 48000.0)
        amount = round(amount, 2)
        total_at_risk += amount

        is_opted_out = (i % 15 == 0)
        hours_ago = rng.uniform(1.0, 96.0)
        now = datetime.utcnow()
        created_at = now - timedelta(hours=hours_ago)
        window_expires = created_at + timedelta(hours=recovery_window)

        # 1. Diagnose
        diag = diagnose_failure(code, scenario)

        # 2. Score
        succ = rng.randint(0, 15)
        fail = rng.randint(0, 3)
        score_res = calculate_recovery_score(
            customer_prev_success=succ,
            customer_prev_failed=fail,
            root_cause_factor=diag["factor"],
            created_at=created_at,
            window_expires_at=window_expires,
            last_active_at=now - timedelta(days=rng.randint(1, 40)),
            prior_recovery_successes=1 if succ > 3 else 0,
            prior_recovery_attempts=1 if succ > 3 else 0,
            attempts_so_far=0
        )
        prob = score_res["recovery_probability"]
        probabilities.append(prob)

        # 3. Intervene
        intervention = select_candidate_intervention(
            scenario=scenario,
            root_cause=diag["root_cause"],
            recovery_probability=prob,
            voice_attempts=0,
            max_voice_attempts=1,
            voice_enabled=True
        )

        # 4. Policy Precedence
        policy = evaluate_precedence(
            amount=amount,
            window_expires_at=window_expires,
            attempts=0,
            voice_attempts=0,
            customer_opted_out=is_opted_out,
            max_autonomous_amount=max_amount,
            max_recovery_attempts=2,
            max_voice_attempts=1,
            voice_enabled=True,
            candidate_action=intervention["candidate_action"]
        )

        outcome_status = "STOPPED"
        is_recovered = False

        if policy.outcome == "ESCALATE":
            outcome_status = "ESCALATED"
            escalated_count += 1
        elif policy.outcome == "STOP":
            outcome_status = "STOPPED"
            stopped_count += 1
        elif policy.outcome == "EXPIRE":
            outcome_status = "EXPIRED"
            stopped_count += 1
        else:
            # Policy Approved -> Simulate realistic outcome against recovery probability
            roll = rng.random()
            if roll <= prob:
                outcome_status = "RECOVERED"
                total_recovered += amount
                recovered_count += 1
                is_recovered = True
            else:
                outcome_status = "FAILED"

        if i <= 25:  # Store first 25 detailed cases for table preview
            case_results.append({
                "case_index": i,
                "scenario": scenario,
                "amount": amount,
                "failure_code": code,
                "recovery_probability": round(prob * 100, 1),
                "action": intervention["candidate_action"],
                "policy_outcome": policy.outcome,
                "final_status": outcome_status,
                "recovered": is_recovered
            })

    duration_ms = int((time.time() - start_time) * 1000)
    recovery_rate = round((recovered_count / case_count) * 100, 2)
    avg_score = round((sum(probabilities) / len(probabilities)) * 100, 2) if probabilities else 0.0

    eval_run = EvaluationRun(
        merchant_id=merchant_id,
        total_cases=case_count,
        recovered_cases=recovered_count,
        total_at_risk_amount=round(total_at_risk, 2),
        total_recovered_amount=round(total_recovered, 2),
        recovery_rate=recovery_rate,
        escalated_cases=escalated_count,
        stopped_cases=stopped_count,
        avg_recovery_score=avg_score,
        run_duration_ms=duration_ms,
        details_json=json.dumps(case_results)
    )
    db.add(eval_run)
    db.commit()
    db.refresh(eval_run)

    return {
        "run_id": eval_run.id,
        "total_cases": case_count,
        "recovered_cases": recovered_count,
        "total_at_risk_amount": round(total_at_risk, 2),
        "total_recovered_amount": round(total_recovered, 2),
        "recovery_rate_percentage": recovery_rate,
        "escalated_cases": escalated_count,
        "stopped_cases": stopped_count,
        "avg_recovery_score": avg_score,
        "duration_ms": duration_ms,
        "sample_cases": case_results
    }
