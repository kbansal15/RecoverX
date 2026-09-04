import React from "react";
import { CalendarCheck, Clock, CheckCircle2, AlertCircle, PhoneCall } from "lucide-react";

export function PromiseToPayPage({ promises, onFulfillPromise }) {
  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Promise-to-Pay (PTP) Tracker</h1>
          <p className="page-subtitle">
            Records customer commitments made in voice/text calls, tracks grace periods, and enforces stopping rules until due date.
          </p>
        </div>
      </div>

      <div className="rzp-card">
        <div className="rzp-card-header">
          <span className="rzp-card-title">Active Promises to Pay ({promises.length})</span>
        </div>
        <table className="rzp-table">
          <thead>
            <tr>
              <th>Commitment ID</th>
              <th>Customer</th>
              <th>Promised Amount</th>
              <th>Promised Payment Date</th>
              <th>Source</th>
              <th>Status</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {promises.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ textAlign: 'center', padding: '30px', color: 'var(--rzp-text-muted)' }}>
                  No active promises yet. Launch a Hinglish Voice Call to record customer promise dates!
                </td>
              </tr>
            ) : (
              promises.map((p) => (
                <tr key={p.id}>
                  <td>
                    <div style={{ fontWeight: 600, color: 'var(--rzp-navy)' }}>{p.id}</div>
                    <div style={{ fontSize: '11px', color: 'var(--rzp-text-muted)' }}>Case #{p.recovery_case_id?.slice(0, 8)}</div>
                  </td>
                  <td>
                    <div style={{ fontWeight: 600 }}>{p.customer?.name}</div>
                    <div style={{ fontSize: '11px', color: 'var(--rzp-text-secondary)' }}>{p.customer?.phone}</div>
                  </td>
                  <td>
                    <div style={{ fontWeight: 700, fontSize: '14px', color: 'var(--rzp-navy)' }}>
                      ₹{p.amount?.toLocaleString('en-IN')}
                    </div>
                  </td>
                  <td>
                    <div style={{ fontWeight: 600, color: p.is_overdue ? '#dc2626' : '#0369a1' }}>
                      {new Date(p.promised_date).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--rzp-text-muted)' }}>
                      {p.notes}
                    </div>
                  </td>
                  <td>
                    <span style={{ fontSize: '11px', padding: '2px 7px', borderRadius: 4, backgroundColor: '#f1f5f9', fontWeight: 600 }}>
                      {p.source}
                    </span>
                  </td>
                  <td>
                    <span
                      className="status-pill"
                      style={{
                        backgroundColor: p.status === 'FULFILLED' ? '#dcfce7' : p.status === 'BROKEN' ? '#fee2e2' : '#fef3c7',
                        color: p.status === 'FULFILLED' ? '#15803d' : p.status === 'BROKEN' ? '#991b1b' : '#92400e',
                        border: '1px solid',
                        borderColor: p.status === 'FULFILLED' ? '#86efac' : p.status === 'BROKEN' ? '#fca5a5' : '#fde68a'
                      }}
                    >
                      {p.status}
                    </span>
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    {p.status === "PENDING" && (
                      <button
                        onClick={() => onFulfillPromise(p.id)}
                        className="btn btn-success btn-sm"
                      >
                        <CheckCircle2 size={12} /> Mark Fulfilled
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
