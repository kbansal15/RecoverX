"""
Policy Precedence Engine.
The deterministic backbone of bounded autonomy for AI Revenue Recovery.
Defines a single authoritative precedence function shared across eligibility and execution gates.
"""

from datetime import datetime
from typing import Optional, NamedTuple

# Allowed Action Allowlist
ALLOWED_ACTIONS = {
    "CREATE_PAYMENT_LINK",
    "START_VOICE_RECOVERY",
    "SCHEDULE_MANDATE_RETRY",
    "DISPATCH_INVOICE_CHASER",
    "RECORD_PROMISE_TO_PAY",
    "ESCALATE",
    "STOP"
}

class PrecedenceDecision(NamedTuple):
    outcome: str          # "APPROVE", "ESCALATE", "STOP", "EXPIRE", "BLOCK", "REJECT"
    rule_code: str        # Reason code
    message: str          # Human-readable policy explanation

def evaluate_precedence(
    amount: float,
    window_expires_at: datetime,
    attempts: int,
    voice_attempts: int,
    customer_opted_out: bool,
    max_autonomous_amount: float,
    max_recovery_attempts: int,
    max_voice_attempts: int,
    voice_enabled: bool,
    candidate_action: Optional[str] = None
) -> PrecedenceDecision:
    """
    Evaluates strict precedence:
    0. Structural Check: Ensure candidate action belongs to strict allowlist.
    1. OPT_OUT: Explicit customer refusal/opt-out always wins. No contact allowed.
    2. HIGH_VALUE_AMOUNT_CHECK: High value cases (> ceiling) require mandatory human review.
       Must be checked BEFORE window expiry or attempt limit so high-value revenue is never silently lost!
    3. RECOVERY_WINDOW: Cases past expiration window resolve to EXPIRED.
    4. ATTEMPT_LIMIT: Maximum contact limits reached resolve to STOP.
    5. ACTION_SPECIFIC RULES: Voice attempt limits or merchant toggle restrictions.
    """
    now = datetime.utcnow()

    # 0. Structural check
    if candidate_action and candidate_action not in ALLOWED_ACTIONS:
        return PrecedenceDecision(
            outcome="REJECT",
            rule_code="INVALID_ACTION",
            message=f"Action '{candidate_action}' is not in the system allowlist."
        )

    # 1. OPT_OUT (Customer preference is supreme)
    if customer_opted_out and candidate_action != "STOP":
        return PrecedenceDecision(
            outcome="STOP",
            rule_code="CUSTOMER_OPTED_OUT",
            message="Customer has opted out of recovery communications. Contact strictly halted."
        )
    if candidate_action == "STOP":
        return PrecedenceDecision(
            outcome="APPROVE",
            rule_code="STOP_APPROVED",
            message="Stopping action is approved as customer requested or terminal state reached."
        )

    # 2. HIGH_VALUE_AMOUNT_CHECK (Runs before window/attempts)
    if amount > max_autonomous_amount:
        return PrecedenceDecision(
            outcome="ESCALATE",
            rule_code="HIGH_VALUE_REQUIRES_MERCHANT_REVIEW",
            message=f"Case amount (₹{amount:,.2f}) exceeds autonomous ceiling (₹{max_autonomous_amount:,.2f}). Escalated to merchant."
        )

    # 3. RECOVERY_WINDOW
    if window_expires_at and now > window_expires_at:
        return PrecedenceDecision(
            outcome="EXPIRE",
            rule_code="RECOVERY_WINDOW_EXPIRED",
            message="The allowed recovery window has elapsed. Case marked EXPIRED."
        )

    # 4. ATTEMPT_LIMIT
    if attempts >= max_recovery_attempts:
        return PrecedenceDecision(
            outcome="STOP",
            rule_code="MAX_RECOVERY_ATTEMPTS_REACHED",
            message=f"Maximum recovery attempts ({max_recovery_attempts}) exhausted. Contact halted."
        )

    # 5. ACTION_SPECIFIC RULES
    if candidate_action == "START_VOICE_RECOVERY":
        if not voice_enabled:
            return PrecedenceDecision(
                outcome="BLOCK",
                rule_code="VOICE_INTERVENTION_DISABLED",
                message="Merchant policy has voice recovery disabled."
            )
        if voice_attempts >= max_voice_attempts:
            return PrecedenceDecision(
                outcome="BLOCK",
                rule_code="MAX_VOICE_ATTEMPTS_REACHED",
                message=f"Voice call limit ({max_voice_attempts}) reached for this case."
            )

    return PrecedenceDecision(
        outcome="APPROVE",
        rule_code="POLICY_APPROVED",
        message="Intervention satisfies all safety bounds and merchant policy rules."
    )
