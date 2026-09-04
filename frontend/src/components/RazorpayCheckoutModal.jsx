import React, { useState } from "react";
import { X, CheckCircle, Smartphone, CreditCard, Landmark, Shield } from "lucide-react";
import confetti from "canvas-confetti";

export function RazorpayCheckoutModal({ caseData, onClose, onPaymentSuccess }) {
  const [method, setMethod] = useState("upi");
  const [processing, setProcessing] = useState(false);
  const [paid, setPaid] = useState(false);

  if (!caseData) return null;

  const handlePay = async () => {
    setProcessing(true);
    try {
      await onPaymentSuccess(caseData.id);
      setPaid(true);
      confetti({
        particleCount: 80,
        spread: 70,
        origin: { y: 0.6 }
      });
      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (err) {
      alert(err.message || "Payment simulation failed");
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="checkout-modal-backdrop" onClick={onClose}>
      <div className="checkout-box" onClick={(e) => e.stopPropagation()}>
        {/* Top Header */}
        <div className="checkout-top">
          <div>
            <div style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.06em', color: '#93c5fd' }}>
              Razorpay Standard Checkout (Test Mode)
            </div>
            <div style={{ fontSize: '16px', fontWeight: 800 }}>Apex Digital Store</div>
            <div style={{ fontSize: '12px', color: '#bfdbfe', marginTop: 2 }}>
              Order #{caseData.id?.slice(0, 8)} • {caseData.customer?.name}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '20px', fontWeight: 800 }}>₹{caseData.amount?.toLocaleString('en-IN')}</div>
            <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#ffffff', cursor: 'pointer', marginTop: 4 }}>
              <X size={18} />
            </button>
          </div>
        </div>

        {paid ? (
          <div style={{ padding: '40px 24px', textAlign: 'center' }}>
            <CheckCircle size={56} color="#10b981" style={{ margin: '0 auto 16px' }} />
            <div style={{ fontSize: '20px', fontWeight: 800, color: 'var(--rzp-navy)' }}>
              Payment Successful!
            </div>
            <div style={{ fontSize: '13px', color: 'var(--rzp-text-secondary)', marginTop: 6 }}>
              Verified Webhook delivered with HMAC-SHA256 signature.
              <br />₹{caseData.amount?.toLocaleString('en-IN')} credited to Recovered Revenue!
            </div>
          </div>
        ) : (
          <div style={{ padding: '20px' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--rzp-text-muted)', textTransform: 'uppercase', marginBottom: 10 }}>
              Select Payment Method
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 20 }}>
              <div
                onClick={() => setMethod("upi")}
                style={{
                  padding: '12px 16px',
                  border: `1.5px solid ${method === 'upi' ? 'var(--rzp-blue)' : 'var(--rzp-border)'}`,
                  borderRadius: 'var(--radius-md)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12,
                  cursor: 'pointer',
                  backgroundColor: method === 'upi' ? 'var(--rzp-blue-subtle)' : '#ffffff'
                }}
              >
                <Smartphone size={20} color={method === 'upi' ? '#0c8ce9' : '#64748b'} />
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: '13.5px' }}>UPI (Google Pay, PhonePe, Paytm)</div>
                  <div style={{ fontSize: '11.5px', color: 'var(--rzp-text-secondary)' }}>Instant verification via UPI App</div>
                </div>
                {method === 'upi' && <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#0c8ce9' }}></span>}
              </div>

              <div
                onClick={() => setMethod("card")}
                style={{
                  padding: '12px 16px',
                  border: `1.5px solid ${method === 'card' ? 'var(--rzp-blue)' : 'var(--rzp-border)'}`,
                  borderRadius: 'var(--radius-md)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12,
                  cursor: 'pointer',
                  backgroundColor: method === 'card' ? 'var(--rzp-blue-subtle)' : '#ffffff'
                }}
              >
                <CreditCard size={20} color={method === 'card' ? '#0c8ce9' : '#64748b'} />
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: '13.5px' }}>Credit / Debit Card</div>
                  <div style={{ fontSize: '11.5px', color: 'var(--rzp-text-secondary)' }}>Visa, Mastercard, RuPay, Corporate</div>
                </div>
                {method === 'card' && <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#0c8ce9' }}></span>}
              </div>

              <div
                onClick={() => setMethod("netbanking")}
                style={{
                  padding: '12px 16px',
                  border: `1.5px solid ${method === 'netbanking' ? 'var(--rzp-blue)' : 'var(--rzp-border)'}`,
                  borderRadius: 'var(--radius-md)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12,
                  cursor: 'pointer',
                  backgroundColor: method === 'netbanking' ? 'var(--rzp-blue-subtle)' : '#ffffff'
                }}
              >
                <Landmark size={20} color={method === 'netbanking' ? '#0c8ce9' : '#64748b'} />
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: '13.5px' }}>NetBanking</div>
                  <div style={{ fontSize: '11.5px', color: 'var(--rzp-text-secondary)' }}>HDFC, ICICI, SBI, Axis, Kotak</div>
                </div>
                {method === 'netbanking' && <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#0c8ce9' }}></span>}
              </div>
            </div>

            <button
              onClick={handlePay}
              disabled={processing}
              className="btn btn-primary"
              style={{ width: '100%', justifyContent: 'center', padding: '12px', fontSize: '15px' }}
            >
              {processing ? "Signing & Delivering Webhook..." : `Pay ₹${caseData.amount?.toLocaleString('en-IN')}`}
            </button>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, marginTop: 12, fontSize: '11px', color: '#64748b' }}>
              <Shield size={12} /> Secured by Razorpay • 256-bit Encryption
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
