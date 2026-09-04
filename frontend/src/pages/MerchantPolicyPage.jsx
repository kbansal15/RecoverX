import React, { useState, useEffect } from "react";
import { Sliders, ShieldCheck, Check, Save } from "lucide-react";

export function MerchantPolicyPage({ policy, onUpdatePolicy, loading }) {
  const [formData, setFormData] = useState({
    max_autonomous_amount: 50000,
    recovery_window_hours: 72,
    max_recovery_attempts: 2,
    max_voice_attempts: 1,
    voice_enabled: true,
    opt_out_behavior: "DO_NOT_CONTACT"
  });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (policy) {
      setFormData({
        max_autonomous_amount: policy.max_autonomous_amount || 50000,
        recovery_window_hours: policy.recovery_window_hours || 72,
        max_recovery_attempts: policy.max_recovery_attempts || 2,
        max_voice_attempts: policy.max_voice_attempts || 1,
        voice_enabled: policy.voice_enabled ?? true,
        opt_out_behavior: policy.opt_out_behavior || "DO_NOT_CONTACT"
      });
    }
  }, [policy]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await onUpdatePolicy({
      max_autonomous_amount: Number(formData.max_autonomous_amount),
      recovery_window_hours: Number(formData.recovery_window_hours),
      max_recovery_attempts: Number(formData.max_recovery_attempts),
      max_voice_attempts: Number(formData.max_voice_attempts),
      voice_enabled: formData.voice_enabled,
      opt_out_behavior: formData.opt_out_behavior
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Merchant Recovery Policy</h1>
          <p className="page-subtitle">
            Configure autonomous boundaries, escalation thresholds, retry ceilings, and customer opt-out behavior.
          </p>
        </div>
      </div>

      <div className="rzp-card" style={{ maxWidth: 700 }}>
        <div className="rzp-card-header">
          <span className="rzp-card-title">Bounded Policy Rules</span>
          <span style={{ fontSize: '12px', color: '#059669', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4 }}>
            <ShieldCheck size={14} /> Authoritative Enforcement
          </span>
        </div>

        <form onSubmit={handleSubmit} style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Max Autonomous Amount */}
          <div>
            <label style={{ fontSize: '13px', fontWeight: 600, color: 'var(--rzp-navy)', display: 'block', marginBottom: 4 }}>
              Autonomous Amount Ceiling (₹)
            </label>
            <div style={{ fontSize: '12px', color: 'var(--rzp-text-secondary)', marginBottom: 8 }}>
              Cases with order amounts exceeding this threshold will NEVER be contacted autonomously; they are queued for mandatory human review.
            </div>
            <input
              type="number"
              value={formData.max_autonomous_amount}
              onChange={(e) => setFormData({ ...formData, max_autonomous_amount: e.target.value })}
              style={{ width: '100%', padding: '10px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--rzp-border)', fontSize: '14px', fontWeight: 600 }}
            />
          </div>

          {/* Recovery Window */}
          <div>
            <label style={{ fontSize: '13px', fontWeight: 600, color: 'var(--rzp-navy)', display: 'block', marginBottom: 4 }}>
              Recovery Eligibility Window (Hours)
            </label>
            <div style={{ fontSize: '12px', color: 'var(--rzp-text-secondary)', marginBottom: 8 }}>
              Time window from initial failure after which cases transition into EXPIRED.
            </div>
            <input
              type="number"
              value={formData.recovery_window_hours}
              onChange={(e) => setFormData({ ...formData, recovery_window_hours: e.target.value })}
              style={{ width: '100%', padding: '10px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--rzp-border)', fontSize: '14px', fontWeight: 600 }}
            />
          </div>

          {/* Retry Limits */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div>
              <label style={{ fontSize: '13px', fontWeight: 600, color: 'var(--rzp-navy)', display: 'block', marginBottom: 4 }}>
                Max Contact Attempts
              </label>
              <input
                type="number"
                value={formData.max_recovery_attempts}
                onChange={(e) => setFormData({ ...formData, max_recovery_attempts: e.target.value })}
                style={{ width: '100%', padding: '10px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--rzp-border)', fontSize: '14px', fontWeight: 600 }}
              />
            </div>
            <div>
              <label style={{ fontSize: '13px', fontWeight: 600, color: 'var(--rzp-navy)', display: 'block', marginBottom: 4 }}>
                Max Voice Calls
              </label>
              <input
                type="number"
                value={formData.max_voice_attempts}
                onChange={(e) => setFormData({ ...formData, max_voice_attempts: e.target.value })}
                style={{ width: '100%', padding: '10px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--rzp-border)', fontSize: '14px', fontWeight: 600 }}
              />
            </div>
          </div>

          {/* Voice Recovery Enabled Toggle */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px', backgroundColor: '#f8fafc', borderRadius: 'var(--radius-md)', border: '1px solid var(--rzp-border)' }}>
            <div>
              <div style={{ fontSize: '13.5px', fontWeight: 600, color: 'var(--rzp-navy)' }}>
                Enable Hinglish Voice Concierge
              </div>
              <div style={{ fontSize: '12px', color: 'var(--rzp-text-secondary)' }}>
                Allow AI voice recovery agent to interactively resolve high-intent cases.
              </div>
            </div>
            <input
              type="checkbox"
              checked={formData.voice_enabled}
              onChange={(e) => setFormData({ ...formData, voice_enabled: e.target.checked })}
              style={{ width: 18, height: 18, cursor: 'pointer' }}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
            >
              <Save size={15} /> Save Policy Configurations
            </button>
            {saved && (
              <span style={{ fontSize: '13px', color: '#059669', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4 }}>
                <Check size={16} /> Saved successfully!
              </span>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}
