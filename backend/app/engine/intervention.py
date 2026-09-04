"""
Intervention Selector.
Selects the candidate recovery intervention based on scenario, root cause, and recovery probability.
"""

from typing import Dict, Any

def select_candidate_intervention(
    scenario: str,
    root_cause: str,
    recovery_probability: float,
    voice_attempts: int,
    max_voice_attempts: int,
    voice_enabled: bool
) -> Dict[str, Any]:
    """
    Selects candidate action:
      - Non-retryable root causes -> STOP
      - High recovery probability (>= 0.75) and voice eligible -> START_VOICE_RECOVERY
      - Moderate to high (>= 0.40) -> CREATE_PAYMENT_LINK
      - Low (0.15 - 0.39) -> CREATE_PAYMENT_LINK (standard follow-up)
      - Very low (< 0.15) -> STOP
      - Specialized scenarios:
          * SUBSCRIPTION_MANDATE -> SCHEDULE_MANDATE_RETRY
          * B2B_INVOICE -> DISPATCH_INVOICE_CHASER
    """
    # Immediate stopping rules
    if root_cause in ["NON_RETRYABLE_PAYMENT_FAILURE", "CUSTOMER_DECLINED"]:
        return {
            "candidate_action": "STOP",
            "reason": "Root cause is non-retryable or customer declined further attempts."
        }

    # Scenario-specific interventions
    if scenario == "SUBSCRIPTION_MANDATE":
        return {
            "candidate_action": "SCHEDULE_MANDATE_RETRY",
            "reason": "AutoPay recurring failure; sequencing intelligent banking retry window."
        }
    
    if scenario == "B2B_INVOICE":
        return {
            "candidate_action": "DISPATCH_INVOICE_CHASER",
            "reason": "Overdue B2B invoice; selecting progressive receivables chaser sequence."
        }

    if scenario == "CHECKOUT_DROPOFF":
        if recovery_probability >= 0.70 and voice_enabled and voice_attempts < max_voice_attempts:
            return {
                "candidate_action": "START_VOICE_RECOVERY",
                "reason": "High-intent checkout drop-off eligible for concierge Hinglish voice intervention."
            }
        return {
            "candidate_action": "CREATE_PAYMENT_LINK",
            "reason": "Checkout cart rehydration link generated with 1-click payment."
        }

    # Standard Payment Failure scoring bands
    if recovery_probability >= 0.75 and voice_enabled and voice_attempts < max_voice_attempts:
        return {
            "candidate_action": "START_VOICE_RECOVERY",
            "reason": f"High recoverability score ({round(recovery_probability * 100)}%); selecting proactive Hinglish voice agent."
        }
    
    if recovery_probability >= 0.40:
        return {
            "candidate_action": "CREATE_PAYMENT_LINK",
            "reason": f"Solid recovery probability ({round(recovery_probability * 100)}%); generating Razorpay dynamic payment link."
        }

    if recovery_probability >= 0.15:
        return {
            "candidate_action": "CREATE_PAYMENT_LINK",
            "reason": f"Moderate recoverability ({round(recovery_probability * 100)}%); dispatched standard Razorpay payment link."
        }

    return {
        "candidate_action": "STOP",
        "reason": f"Insufficient recovery probability ({round(recovery_probability * 100)}% < 15%); stopping intervention to preserve customer goodwill."
    }
