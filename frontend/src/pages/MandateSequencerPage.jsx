import React, { useState } from "react";
import { Repeat, Calendar, Clock, Sparkles, Zap, CheckCircle, ShieldCheck } from "lucide-react";

export function MandateSequencerPage({ mandates, onSimulateMandate, onSequenceRetry, loading }) {
  const [subName, setSubName] = useState("Enterprise Cloud Infrastructure (Annual)");
  const [amount, setAmount] = useState(14999);
  const [type, setType] = useState("UPI_AUTOPAY");

  const handleSimulate = async () => {
    await onSimulateMandate({
      customer_id: "cust_karan_07",
      amount: Number(amount),
      mandate_type: type,
      subscription_name: subName
    });
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Mandate Retry Sequencer (Subscriptions)</h1>
          <p className="page-subtitle">
            Intelligent auto-debit scheduling for UPI AutoPay & e-Mandates based on Indian banking clearing windows & salary cycles.
          </p>
        </div>
      </div>

      {/* Simulator Widget */}
      <div className="rzp-card" style={{ padding: '20px', marginBottom: 24, backgroundColor: '#fffbeb', borderColor: '#fde68a' }}>
        <div style={{ fontSize: '14px', fontWeight: 700, color: '#b45309', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
          <Zap size={16} /> Simulate Recurring Auto-Debit Failure
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12, alignItems: 'flex-end' }}>
          <div>
            <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--rzp-text-secondary)' }}>Subscription Plan</label>
            <input
              type="text"
              value={subName}
              onChange={(e) => setSubName(e.target.value)}
              style={{ width: '100%', padding: '8px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--rzp-border)', marginTop: 4, fontSize: '13px' }}
            />
          </div>

          <div>
            <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--rzp-text-secondary)' }}>Recurring Amount (₹)</label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              style={{ width: '100%', padding: '8px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--rzp-border)', marginTop: 4, fontSize: '13px' }}
            />
          </div>

          <div>
            <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--rzp-text-secondary)' }}>Mandate Type</label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              style={{ width: '100%', padding: '8px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--rzp-border)', marginTop: 4, fontSize: '13px', backgroundColor: '#ffffff' }}
            >
              <option value="UPI_AUTOPAY">UPI AutoPay (NPCI)</option>
              <option value="CARD_MANDATE">Credit/Debit Card e-Mandate</option>
              <option value="E_NACH">e-NACH NetBanking Mandate</option>
            </select>
          </div>

          <button
            onClick={handleSimulate}
            disabled={loading}
            className="btn btn-primary"
            style={{ height: 38 }}
          >
            <Repeat size={15} /> Inject Mandate Failure
          </button>
        </div>
      </div>

      {/* Mandate Table */}
      <div className="rzp-card">
        <div className="rzp-card-header">
          <span className="rzp-card-title">Sequenced Mandates ({mandates.length})</span>
          <span style={{ fontSize: '12px', color: 'var(--rzp-text-secondary)' }}>
            RBI Pre-debit Compliant
          </span>
        </div>
        <table className="rzp-table">
          <thead>
            <tr>
              <th>Mandate & Subscriber</th>
              <th>Type & Frequency</th>
              <th>Amount</th>
              <th>Failure Code</th>
              <th>Optimal Banking Retry Window</th>
              <th>Scheduled Time</th>
              <th style={{ textAlign: 'right' }}>Sequencer Action</th>
            </tr>
          </thead>
          <tbody>
            {mandates.map((m) => (
              <tr key={m.id}>
                <td>
                  <div style={{ fontWeight: 600, color: 'var(--rzp-navy)' }}>{m.subscription_id}</div>
                  <div style={{ fontSize: '12px', color: 'var(--rzp-text-secondary)' }}>{m.customer?.name}</div>
                </td>
                <td>
                  <span style={{ fontSize: '11px', padding: '2px 7px', borderRadius: 4, backgroundColor: '#f1f5f9', fontWeight: 600, color: '#475569' }}>
                    {m.mandate_type}
                  </span>
                  <div style={{ fontSize: '11px', color: 'var(--rzp-text-muted)', marginTop: 2 }}>{m.frequency}</div>
                </td>
                <td>
                  <div style={{ fontWeight: 700, fontSize: '14px', color: 'var(--rzp-navy)' }}>
                    ₹{m.amount?.toLocaleString('en-IN')}
                  </div>
                </td>
                <td>
                  <span style={{ fontSize: '11px', color: '#b91c1c', fontWeight: 600 }}>
                    {m.last_failure_code}
                  </span>
                  <div style={{ fontSize: '11px', color: 'var(--rzp-text-secondary)' }}>
                    Attempt #{m.retry_count}
                  </div>
                </td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#0369a1', fontWeight: 600, fontSize: '12.5px' }}>
                    <Sparkles size={14} /> {m.optimal_retry_window}
                  </div>
                  <div style={{ fontSize: '11px', color: '#059669', marginTop: 2 }}>
                    +42% Liquidity Success Boost
                  </div>
                </td>
                <td>
                  <div style={{ fontSize: '12px', fontWeight: 500 }}>
                    {new Date(m.scheduled_retry_at).toLocaleDateString([], { month: 'short', day: 'numeric' })} at 10:00 AM
                  </div>
                </td>
                <td style={{ textAlign: 'right' }}>
                  <button
                    onClick={() => onSequenceRetry(m.id)}
                    className="btn btn-secondary btn-sm"
                  >
                    <Clock size={12} color="#0c8ce9" /> Re-Sequence
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
