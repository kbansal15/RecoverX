"""
Razorpay Integration Layer.
Integrates with the official Razorpay Python SDK for Test Mode link creation and HMAC webhook validation.
"""

import hmac
import hashlib
import time
import uuid
from typing import Dict, Any, Optional
from app.config import settings

class RazorpayService:
    def __init__(self):
        self.key_id = settings.RAZORPAY_KEY_ID
        self.key_secret = settings.RAZORPAY_KEY_SECRET
        self.webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
        self._client = None
        
        # Initialize Razorpay Client if credentials provided
        if self.key_id and self.key_secret:
            try:
                import razorpay
                self._client = razorpay.Client(auth=(self.key_id, self.key_secret))
            except Exception as e:
                print(f"[Razorpay Client Warning] Could not initialize SDK: {e}")
                self._client = None

    def create_payment_link(
        self,
        amount: float,
        currency: str,
        customer_name: str,
        customer_email: str,
        customer_phone: str,
        description: str,
        reference_id: str
    ) -> Dict[str, Any]:
        """
        Creates a Razorpay Test Mode Payment Link.
        Converts INR to paise (amount * 100).
        Includes graceful demo fallback if live network is unreachable.
        """
        amount_paise = int(round(amount * 100))
        expire_by = int(time.time()) + (72 * 3600)  # 72 hour link validity

        payload = {
            "amount": amount_paise,
            "currency": currency or "INR",
            "accept_partial": False,
            "description": description or f"Recovery Payment for Order #{reference_id}",
            "customer": {
                "name": customer_name,
                "email": customer_email,
                "contact": customer_phone
            },
            "notify": {
                "sms": True,
                "email": True
            },
            "reminder_enable": True,
            "notes": {
                "recovery_case_id": reference_id,
                "platform": "RecoverX AI Recovery"
            },
            "expire_by": expire_by
        }

        # Attempt SDK call first
        if self._client and self.key_id.startswith("rzp_test_") and not "recoverxDemoKey" in self.key_id:
            try:
                res = self._client.payment_link.create(payload)
                return {
                    "id": res.get("id"),
                    "short_url": res.get("short_url"),
                    "status": res.get("status", "created"),
                    "mode": "RAZORPAY_TEST_MODE"
                }
            except Exception as e:
                print(f"[Razorpay SDK create_payment_link Error] {e}; falling back to demo test mode link.")

        # Canonical Razorpay test mode mock link
        plink_id = f"plink_test_{uuid.uuid4().hex[:14]}"
        short_url = f"https://rzp.io/i/{plink_id[11:]}"
        return {
            "id": plink_id,
            "short_url": short_url,
            "status": "created",
            "mode": "TEST_MODE_SIMULATED"
        }

    def verify_webhook_signature(self, raw_body: bytes, signature: str, secret: Optional[str] = None) -> bool:
        """
        Cryptographic HMAC-SHA256 signature verification over raw request bytes.
        Uses constant-time comparison to prevent timing side-channel attacks.
        """
        if not signature:
            return False
        
        signing_secret = (secret or self.webhook_secret).encode("utf-8")
        expected_sig = hmac.new(signing_secret, raw_body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_sig, signature)

    def generate_signed_test_webhook(self, case_id: str, payment_link_id: str, amount: float) -> Dict[str, Any]:
        """Generates a signature-verified payment_link.paid webhook payload for demo completion."""
        import json
        event_id = f"evt_{uuid.uuid4().hex[:16]}"
        payment_id = f"pay_{uuid.uuid4().hex[:14]}"
        
        payload = {
            "entity": "event",
            "account_id": "acc_razorpay_merchant_demo",
            "event": "payment_link.paid",
            "contains": ["payment_link", "payment"],
            "payload": {
                "payment_link": {
                    "entity": {
                        "id": payment_link_id,
                        "amount": int(round(amount * 100)),
                        "amount_paid": int(round(amount * 100)),
                        "currency": "INR",
                        "status": "paid",
                        "notes": {
                            "recovery_case_id": case_id
                        }
                    }
                },
                "payment": {
                    "entity": {
                        "id": payment_id,
                        "amount": int(round(amount * 100)),
                        "currency": "INR",
                        "status": "captured",
                        "method": "upi",
                        "vpa": "customer@okhdfcbank"
                    }
                }
            },
            "created_at": int(time.time())
        }

        body_bytes = json.dumps(payload).encode("utf-8")
        sig = hmac.new(self.webhook_secret.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()
        
        return {
            "event_id": event_id,
            "raw_body": body_bytes.decode("utf-8"),
            "signature": sig,
            "payload": payload
        }

razorpay_service = RazorpayService()
