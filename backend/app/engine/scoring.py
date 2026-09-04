"""
Recovery Scoring Engine.
Transparent, documented, weighted recovery probability formula.
Guarantees deterministic, reproducible results without opaque black-box scoring.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List

def calculate_recovery_score(
    customer_prev_success: int,
    customer_prev_failed: int,
    root_cause_factor: float,
    created_at: datetime,
    window_expires_at: datetime,
    last_active_at: datetime,
    prior_recovery_successes: int,
    prior_recovery_attempts: int,
    attempts_so_far: int
) -> Dict[str, Any]:
    """
    Weighted recovery probability formula:
      - successRatio (0.30)
      - rootCauseFactor (0.20)
      - recencyFactor (0.15)
      - activityFactor (0.15)
      - priorRecoveryFactor (0.10)
      - attemptPenalty (0.10)
    """
    # 1. Historical success ratio
    total_txns = customer_prev_success + customer_prev_failed + 1
    success_ratio = customer_prev_success / total_txns

    # 2. Root cause factor [0.0 - 1.0]
    rc_factor = max(0.0, min(1.0, root_cause_factor))

    # 3. Recency factor
    now = datetime.utcnow()
    hours_since_creation = (now - created_at).total_seconds() / 3600.0 if created_at else 0.5
    total_window_hours = (window_expires_at - created_at).total_seconds() / 3600.0 if (window_expires_at and created_at) else 72.0
    
    if hours_since_creation <= 6.0:
        recency_factor = 1.0
    elif hours_since_creation >= total_window_hours:
        recency_factor = 0.0
    else:
        # Linear decay from 1.0 at 6h to 0.0 at total_window_hours
        recency_factor = max(0.0, 1.0 - ((hours_since_creation - 6.0) / max(1.0, total_window_hours - 6.0)))

    # 4. Customer activity factor
    days_since_active = (now - last_active_at).days if last_active_at else 5
    activity_factor = 1.0 if days_since_active <= 30 else 0.3

    # 5. Prior recovery rate factor
    if prior_recovery_attempts > 0:
        prior_recovery_factor = prior_recovery_successes / prior_recovery_attempts
    else:
        prior_recovery_factor = 0.5  # Neutral prior

    # 6. Attempt penalty factor
    attempt_penalty = max(0.0, 1.0 - (0.3 * attempts_so_far))

    # Weighted sum
    score = (
        0.30 * success_ratio +
        0.20 * rc_factor +
        0.15 * recency_factor +
        0.15 * activity_factor +
        0.10 * prior_recovery_factor +
        0.10 * attempt_penalty
    )

    score = max(0.0, min(1.0, round(score, 4)))

    # Explainability reason codes
    reasons: List[str] = []
    if success_ratio >= 0.70:
        reasons.append("HIGH_HISTORICAL_SUCCESS_RATIO")
    if rc_factor >= 0.80:
        reasons.append("RETRYABLE_ROOT_CAUSE")
    if recency_factor >= 0.80:
        reasons.append("FRESH_REVENUE_RISK_WINDOW")
    if activity_factor == 1.0:
        reasons.append("RECENTLY_ACTIVE_CUSTOMER")
    if prior_recovery_factor >= 0.60:
        reasons.append("PROVEN_RECOVERY_HISTORY")
    if attempts_so_far == 0:
        reasons.append("FIRST_INTERVENTION_ATTEMPT")

    return {
        "recovery_probability": score,
        "score_percentage": round(score * 100, 1),
        "reasons": reasons,
        "metrics_breakdown": {
            "success_ratio": round(success_ratio, 2),
            "root_cause_factor": round(rc_factor, 2),
            "recency_factor": round(recency_factor, 2),
            "activity_factor": round(activity_factor, 2),
            "prior_recovery_factor": round(prior_recovery_factor, 2),
            "attempt_penalty": round(attempt_penalty, 2)
        }
    }
