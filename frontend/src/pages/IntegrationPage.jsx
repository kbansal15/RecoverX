import React, { useState } from "react";
import { Webhook, Copy, Check, ShieldCheck, Code2 } from "lucide-react";

export function IntegrationPage({ merchant }) {
  const [copiedUrl, setCopiedUrl] = useState(false);
  const [copiedSecret, setCopiedSecret] = useState(false);
  const [revealed, setRevealed] = useState(false);

  const webhookUrl = "http://localhost:8000/api/webhooks/razorpay";
  const secret = merchant?.webhook_secret || "webhook_secret_demo_987654321";

  const copyToClipboard = (text, type) => {
    navigator.clipboard.writeText(text);
    if (type === "url") {
      setCopiedUrl(true);
      setTimeout(() => setCopiedUrl(false), 2000);
    } else {
      setCopiedSecret(true);
      setTimeout(() => setCopiedSecret(false), 2000);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Integration & Razorpay Webhooks</h1>
          <p className="page-subtitle">
            Connect RecoverX to your Razorpay merchant dashboard to stream real-time payment failure and settlement webhooks.
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: 20 }}>
        {/* Webhook Settings Card */}
        <div className="rzp-card">
          <div className="rzp-card-header">
            <span className="rzp-card-title">Inbound Webhook Configuration</span>
            <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: 4, backgroundColor: '#dcfce7', color: '#15803d', fontWeight: 600 }}>
              HMAC-SHA256 Active
            </span>
          </div>
          <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div>
              <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--rzp-text-secondary)', display: 'block', marginBottom: 4 }}>
                Webhook Endpoint URL
              </label>
              <div style={{ display: 'flex', gap: 8 }}>
                <input
                  type="text"
                  readOnly
                  value={webhookUrl}
                  style={{ flex: 1, padding: '8px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--rzp-border)', fontSize: '13px', backgroundColor: '#f8fafc', fontFamily: 'monospace' }}
                />
                <button
                  onClick={() => copyToClipboard(webhookUrl, "url")}
                  className="btn btn-secondary btn-sm"
                >
                  {copiedUrl ? <Check size={14} color="#059669" /> : <Copy size={14} />}
                </button>
              </div>
            </div>

            <div>
              <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--rzp-text-secondary)', display: 'block', marginBottom: 4 }}>
                Webhook Signing Secret
              </label>
              <div style={{ display: 'flex', gap: 8 }}>
                <input
                  type="text"
                  readOnly
                  value={revealed ? secret : "••••••••••••••••••••••••••••••••"}
                  style={{ flex: 1, padding: '8px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--rzp-border)', fontSize: '13px', backgroundColor: '#f8fafc', fontFamily: 'monospace' }}
                />
                <button
                  onClick={() => setRevealed(!revealed)}
                  className="btn btn-secondary btn-sm"
                >
                  {revealed ? "Hide" : "Reveal"}
                </button>
                <button
                  onClick={() => copyToClipboard(secret, "secret")}
                  className="btn btn-secondary btn-sm"
                >
                  {copiedSecret ? <Check size={14} color="#059669" /> : <Copy size={14} />}
                </button>
              </div>
            </div>

            <div style={{ padding: '14px', backgroundColor: '#f8fafc', borderRadius: 'var(--radius-md)', border: '1px solid var(--rzp-border)', fontSize: '12.5px', color: 'var(--rzp-text-secondary)' }}>
              <div style={{ fontWeight: 700, color: 'var(--rzp-navy)', marginBottom: 6 }}>
                Required Webhook Subscriptions:
              </div>
              <ul style={{ paddingLeft: 18, display: 'flex', flexDirection: 'column', gap: 4 }}>
                <li><code>payment.failed</code> — Triggers automated diagnosis & plan formulation</li>
                <li><code>payment_link.paid</code> — Verifies settlement and updates recovered revenue tally</li>
                <li><code>subscription.charged</code> / <code>failed</code> — Tracks mandate debits</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Python SDK Integration Snippet Card */}
        <div className="rzp-card">
          <div className="rzp-card-header">
            <span className="rzp-card-title">Python Integration Example</span>
            <Code2 size={16} color="#0c8ce9" />
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ fontSize: '12.5px', color: 'var(--rzp-text-secondary)', marginBottom: 10 }}>
              Trigger recovery cases directly from your Python backend or webhook worker:
            </div>
            <pre style={{ backgroundColor: '#0f172a', color: '#f8fafc', padding: '14px', borderRadius: 'var(--radius-md)', fontSize: '12px', overflowX: 'auto', lineHeight: 1.5, fontFamily: 'monospace' }}>
{`import requests

# Report payment failure to RecoverX agent
response = requests.post(
    "http://localhost:8000/api/recovery-cases",
    json={
        "customer_id": "cust_9876543210",
        "amount": 2999.0,
        "scenario": "PAYMENT_FAILURE",
        "failure_code": "CARD_INSUFFICIENT_FUNDS",
        "payment_method": "CARD",
        "description": "Debit card declined by issuing bank"
    }
)

case = response.json()
print("Recovery Case Initialized:", case["case_id"])
print("Status:", case["status"]) # PENDING_APPROVAL`}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
