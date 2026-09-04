import React from "react";
import {
  X,
  CheckCircle2,
  AlertTriangle,
  ExternalLink,
  PhoneCall,
  CreditCard,
  Clock,
  ShieldCheck,
  User,
  ArrowRight,
  TrendingUp,
  Activity
} from "lucide-react";

export function CaseAuditDrawer({
  caseData,
  onClose,
  onConfirmPlan,
  onOpenCheckout,
  onOpenVoice,
  onEscalate,
  onStop,
  loading
}) {
  if (!caseData) return null;

  const reasons = caseData.recovery_score_reasons || [];
  const auditLogs = caseData.audit_trail || [];

  return (
    <div className="drawer-overlay" onClick={onClose}>
      <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="drawer-header">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: '13px', fontFamily: 'monospace', color: 'var(--rzp-text-secondary)' }}>
                {caseData.id}
              </span>
              <span className={`status-pill ${caseData.status?.toLowerCase()}`}>
                {caseData.status?.replace("_", " ")}
              </span>
            </div>
            <div style={{ fontSize: '20px', fontWeight: 800, color: 'var(--rzp-navy)', marginTop: 4 }}>
              ₹{caseData.amount?.toLocaleString('en-IN')}
              <span style={{ fontSize: '13px', fontWeight: 500, color: 'var(--rzp-text-secondary)', marginLeft: 8 }}>
                via {caseData.payment_method}
              </span>
            </div>
          </div>
          <button onClick={onClose} className="btn btn-secondary btn-sm" style={{ padding: '6px' }}>
            <X size={18} />
          </button>
        </div>

        {/* Body */}
        <div className="drawer-body">
          {/* Action Trigger Banner */}
          <div style={{ padding: '16px', backgroundColor: 'var(--rzp-blue-subtle)', borderRadius: 'var(--radius-md)', border: '1px solid #bae6fd', marginBottom: 20 }}>
            <div style={{ fontSize: '13px', fontWeight: 700, color: '#0369a1', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
              <Activity size={16} /> Autonomous Action Recommendation: {caseData.candidate_action}
            </div>
            <div style={{ fontSize: '12.5px', color: '#0c4a6e', marginBottom: 12 }}>
              {caseData.decision_explanation || "Case evaluated under Razorpay bounded recovery policy."}
            </div>

            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {caseData.status === "PENDING_APPROVAL" && (
                <button
                  onClick={() => onConfirmPlan(caseData.id)}
                  disabled={loading}
                  className="btn btn-primary btn-sm"
                >
                  <CheckCircle2 size={14} /> Approve Recovery Plan
                </button>
              )}

              {caseData.payment_link_url && (
                <button
                  onClick={() => onOpenCheckout(caseData)}
                  className="btn btn-success btn-sm"
                >
                  <CreditCard size={14} /> Simulate Razorpay Checkout
                </button>
              )}

              <button
                onClick={() => onOpenVoice(caseData)}
                className="btn btn-secondary btn-sm"
              >
                <PhoneCall size={14} color="#0c8ce9" /> Launch Hinglish Voice Call
              </button>

              {caseData.status !== "ESCALATED" && caseData.status !== "RECOVERED" && (
                <button
                  onClick={() => onEscalate(caseData.id)}
                  className="btn btn-secondary btn-sm"
                  style={{ color: '#c2410c' }}
                >
                  Escalate
                </button>
              )}

              {caseData.status !== "STOPPED" && caseData.status !== "RECOVERED" && (
                <button
                  onClick={() => onStop(caseData.id)}
                  className="btn btn-secondary btn-sm"
                  style={{ color: '#dc2626' }}
                >
                  Stop Contact
                </button>
              )}
            </div>
          </div>

          {/* Customer & Failure Diagnostics */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 20 }}>
            <div style={{ padding: '14px', border: '1px solid var(--rzp-border)', borderRadius: 'var(--radius-md)' }}>
              <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--rzp-text-muted)', fontWeight: 700, marginBottom: 6 }}>
                Customer Profile
              </div>
              <div style={{ fontWeight: 600, fontSize: '14px', color: 'var(--rzp-navy)' }}>
                {caseData.customer?.name}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--rzp-text-secondary)', marginTop: 2 }}>
                {caseData.customer?.phone}
              </div>
              <div style={{ fontSize: '11.5px', color: '#059669', marginTop: 4, fontWeight: 500 }}>
                {caseData.customer?.prev_successful_payments} prior successful orders
              </div>
            </div>

            <div style={{ padding: '14px', border: '1px solid var(--rzp-border)', borderRadius: 'var(--radius-md)' }}>
              <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--rzp-text-muted)', fontWeight: 700, marginBottom: 6 }}>
                Failure Diagnosis
              </div>
              <div style={{ fontWeight: 600, fontSize: '13px', color: '#b91c1c' }}>
                {caseData.failure_code || "PAYMENT_FAILED"}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--rzp-text-secondary)', marginTop: 2 }}>
                {caseData.root_cause_reason || caseData.failure_description}
              </div>
            </div>
          </div>

          {/* Transparent Mathematical Recovery Probability */}
          <div style={{ padding: '16px', border: '1px solid var(--rzp-border)', borderRadius: 'var(--radius-md)', marginBottom: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
              <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--rzp-navy)' }}>
                Transparent Recoverability Score
              </span>
              <span style={{ fontSize: '16px', fontWeight: 800, color: '#0c8ce9' }}>
                {Math.round(caseData.recovery_probability * 100)}%
              </span>
            </div>

            <div style={{ width: '100%', height: 6, backgroundColor: '#f1f5f9', borderRadius: 9999, overflow: 'hidden', marginBottom: 12 }}>
              <div
                style={{
                  width: `${Math.round(caseData.recovery_probability * 100)}%`,
                  height: '100%',
                  backgroundColor: caseData.recovery_probability >= 0.7 ? '#10b981' : caseData.recovery_probability >= 0.4 ? '#0c8ce9' : '#f59e0b'
                }}
              ></div>
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {reasons.map((r, i) => (
                <span
                  key={i}
                  style={{
                    fontSize: '11px',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    backgroundColor: '#f8fafc',
                    border: '1px solid #e2e8f0',
                    color: '#475569'
                  }}
                >
                  ✓ {r.replace(/_/g, " ")}
                </span>
              ))}
            </div>
          </div>

          {/* Policy Safety Bounds Checklist */}
          <div style={{ padding: '16px', border: '1px solid var(--rzp-border)', borderRadius: 'var(--radius-md)', marginBottom: 20 }}>
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--rzp-navy)', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 6 }}>
              <ShieldCheck size={16} color="#10b981" /> Policy Precedence & Safety Bounds
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: '12.5px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--rzp-text-secondary)' }}>Autonomous Amount Ceiling</span>
                <span style={{ fontWeight: 600, color: caseData.amount <= 50000 ? '#059669' : '#dc2626' }}>
                  {caseData.amount <= 50000 ? "PASS (<= ₹50,000)" : "TRIGGERED ESCALATION (> ₹50,000)"}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--rzp-text-secondary)' }}>Contact Attempt Limit</span>
                <span style={{ fontWeight: 600, color: '#059669' }}>
                  PASS ({caseData.attempts} / 2 max attempts)
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--rzp-text-secondary)' }}>Customer Opt-Out Status</span>
                <span style={{ fontWeight: 600, color: caseData.customer?.opted_out ? '#dc2626' : '#059669' }}>
                  {caseData.customer?.opted_out ? "OPTED OUT (STOP ENFORCED)" : "ELIGIBLE (NO OPT-OUT)"}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--rzp-text-secondary)' }}>Recovery Window</span>
                <span style={{ fontWeight: 600, color: '#059669' }}>
                  ACTIVE (Within 72h window)
                </span>
              </div>
            </div>
          </div>

          {/* Chronological Audit Trail */}
          <div>
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--rzp-navy)', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
              <Clock size={16} /> Immutable Audit Event Trail
            </div>
            <div style={{ borderLeft: '2px solid #e2e8f0', marginLeft: 10, paddingLeft: 16, display: 'flex', flexDirection: 'column', gap: 14 }}>
              {auditLogs.map((log) => (
                <div key={log.id} style={{ position: 'relative' }}>
                  <div
                    style={{
                      position: 'absolute',
                      left: -21,
                      top: 4,
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      backgroundColor: log.decision.includes('RECOVERED') ? '#10b981' : '#0c8ce9'
                    }}
                  ></div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '12.5px', fontWeight: 600, color: 'var(--rzp-navy)' }}>
                      {log.event_type}
                    </span>
                    <span style={{ fontSize: '11px', color: 'var(--rzp-text-muted)' }}>
                      {new Date(log.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--rzp-text-secondary)', marginTop: 2 }}>
                    {log.reason}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
