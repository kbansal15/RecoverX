"""
Root Cause Diagnosis Engine.
Deterministic mapping of Razorpay error codes and scenario failure reasons to categorized root causes.
"""

from typing import Dict, Any

# Root cause categories
RETRYABLE_PAYMENT_FAILURE = "RETRYABLE_PAYMENT_FAILURE"
PAYMENT_METHOD_ISSUE = "PAYMENT_METHOD_ISSUE"
ABANDONMENT = "ABANDONMENT"
MANDATE_INSUFFICIENT_FUNDS = "MANDATE_INSUFFICIENT_FUNDS"
NON_RETRYABLE_PAYMENT_FAILURE = "NON_RETRYABLE_PAYMENT_FAILURE"
CUSTOMER_DECLINED = "CUSTOMER_DECLINED"

FAILURE_CODE_MAP = {
    # Retryable gateway / network / bank timeouts
    "GATEWAY_ERROR": {
        "root_cause": RETRYABLE_PAYMENT_FAILURE,
        "is_retryable": True,
        "reason": "Temporary gateway or issuing bank technical downtime.",
        "factor": 1.0
    },
    "PAYMENT_TIMED_OUT": {
        "root_cause": RETRYABLE_PAYMENT_FAILURE,
        "is_retryable": True,
        "reason": "Customer payment session timed out during 3DS OTP authorization.",
        "factor": 1.0
    },
    "UPI_COLLECT_EXPIRED": {
        "root_cause": RETRYABLE_PAYMENT_FAILURE,
        "is_retryable": True,
        "reason": "UPI collect request timed out in customer's PSP app.",
        "factor": 0.95
    },
    "CARD_INSUFFICIENT_FUNDS": {
        "root_cause": RETRYABLE_PAYMENT_FAILURE,
        "is_retryable": True,
        "reason": "Account or card had temporary insufficient balance.",
        "factor": 0.85
    },
    
    # Payment method degradation
    "BAD_REQUEST_PAYMENT_DECLINED_BY_BANK": {
        "root_cause": PAYMENT_METHOD_ISSUE,
        "is_retryable": True,
        "reason": "Bank declined transaction due to card limits or international flag disabled.",
        "factor": 0.60
    },
    "CARD_EXPIRED": {
        "root_cause": PAYMENT_METHOD_ISSUE,
        "is_retryable": True,
        "reason": "Saved card has expired; alternative payment method required.",
        "factor": 0.60
    },
    "VPA_INACTIVE": {
        "root_cause": PAYMENT_METHOD_ISSUE,
        "is_retryable": True,
        "reason": "Customer UPI ID inactive or bank handle temporarily blocked.",
        "factor": 0.60
    },
    
    # Drop-offs and Abandonment
    "CHECKOUT_ABANDONED_OTP": {
        "root_cause": ABANDONMENT,
        "is_retryable": True,
        "reason": "Customer dropped off at the OTP authentication step.",
        "factor": 0.70
    },
    "CHECKOUT_ABANDONED_PAYMENT_METHOD": {
        "root_cause": ABANDONMENT,
        "is_retryable": True,
        "reason": "Customer exited checkout while reviewing payment options.",
        "factor": 0.50
    },
    
    # Mandates
    "MANDATE_DEBIT_FAILED": {
        "root_cause": MANDATE_INSUFFICIENT_FUNDS,
        "is_retryable": True,
        "reason": "Automated recurring mandate debit failed; optimal window retry recommended.",
        "factor": 0.80
    },
    
    # Non-retryable
    "CARD_REPORTED_LOST_OR_STOLEN": {
        "root_cause": NON_RETRYABLE_PAYMENT_FAILURE,
        "is_retryable": False,
        "reason": "Card reported stolen or fraudulent. Strict stop enforced.",
        "factor": 0.0
    },
    "CUSTOMER_CANCELLED": {
        "root_cause": CUSTOMER_DECLINED,
        "is_retryable": False,
        "reason": "Customer explicitly dismissed the payment modal.",
        "factor": 0.10
    }
}

def diagnose_failure(failure_code: str, scenario: str = "PAYMENT_FAILURE") -> Dict[str, Any]:
    """Diagnoses root cause from failure code with fallback logic."""
    code_info = FAILURE_CODE_MAP.get(failure_code)
    if code_info:
        return code_info
        
    if scenario == "CHECKOUT_DROPOFF":
        return {
            "root_cause": ABANDONMENT,
            "is_retryable": True,
            "reason": "Checkout session abandoned prior to payment completion.",
            "factor": 0.60
        }
    if scenario == "SUBSCRIPTION_MANDATE":
        return {
            "root_cause": MANDATE_INSUFFICIENT_FUNDS,
            "is_retryable": True,
            "reason": "Recurring auto-debit failure under UPI AutoPay / e-Mandate.",
            "factor": 0.80
        }
    if scenario == "B2B_INVOICE":
        return {
            "root_cause": RETRYABLE_PAYMENT_FAILURE,
            "is_retryable": True,
            "reason": "Overdue invoice receivables requiring structured follow-up.",
            "factor": 0.75
        }
        
    return {
        "root_cause": RETRYABLE_PAYMENT_FAILURE,
        "is_retryable": True,
        "reason": f"Standard payment failure with code {failure_code or 'UNKNOWN'}.",
        "factor": 0.70
    }
