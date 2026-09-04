import React, { useState } from "react";
import { Search, Filter, PhoneCall, CreditCard, CheckCircle2, ShieldAlert, XCircle } from "lucide-react";

export function RecoveryCasesPage({
  cases,
  onSelectCase,
  onConfirmPlan,
  onOpenCheckout,
  onOpenVoice,
  onFilterChange,
  activeScenario,
  activeStatus
}) {
  const [search, setSearch] = useState("");

  const filteredCases = cases.filter((c) => {
    if (activeScenario && activeScenario !== "ALL" && c.scenario !== activeScenario) return false;
    if (activeStatus && activeStatus !== "ALL" && c.status !== activeStatus) return false;
    if (search) {
      const q = search.toLowerCase();
      const match =
        c.id.toLowerCase().includes(q) ||
        (c.customer?.name || "").toLowerCase().includes(q) ||
        (c.failure_code || "").toLowerCase().includes(q);
      if (!match) return false;
    }
    return true;
  });

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Recovery Cases</h1>
          <p className="page-subtitle">
            Autonomous decision pipeline managing revenue recovery across all payment degradation vectors.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 20, flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, backgroundColor: '#ffffff', border: '1px solid var(--rzp-border)', borderRadius: 'var(--radius-md)', padding: '6px 12px', minWidth: 260 }}>
          <Search size={15} color="#94a3b8" />
          <input
            type="text"
            placeholder="Search by case ID, customer, error code..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ border: 'none', outline: 'none', width: '100%', fontSize: '13px' }}
          />
        </div>

        {/* Scenario Pills */}
        <div style={{ display: 'flex', gap: 6 }}>
          {["ALL", "PAYMENT_FAILURE", "CHECKOUT_DROPOFF", "SUBSCRIPTION_MANDATE", "B2B_INVOICE"].map((sc) => (
            <button
              key={sc}
              onClick={() => onFilterChange(sc, activeStatus)}
              style={{
                fontSize: '12px',
                padding: '6px 12px',
                borderRadius: '9999px',
                border: '1px solid',
                borderColor: activeScenario === sc ? 'var(--rzp-blue)' : 'var(--rzp-border)',
                backgroundColor: activeScenario === sc ? 'var(--rzp-blue-subtle)' : '#ffffff',
                color: activeScenario === sc ? 'var(--rzp-blue)' : 'var(--rzp-text-secondary)',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              {sc.replace(/_/g, " ")}
            </button>
          ))}
        </div>

        {/* Status Dropdown */}
        <select
          value={activeStatus}
          onChange={(e) => onFilterChange(activeScenario, e.target.value)}
          style={{
            marginLeft: 'auto',
            padding: '6px 12px',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--rzp-border)',
            fontSize: '13px',
            backgroundColor: '#ffffff',
            color: 'var(--rzp-navy)',
            fontWeight: 500,
            outline: 'none'
          }}
        >
          <option value="ALL">All Statuses</option>
          <option value="PENDING_APPROVAL">Pending Approval</option>
          <option value="ACTION_EXECUTED">Action Executed</option>
          <option value="RECOVERED">Recovered</option>
          <option value="ESCALATED">Escalated</option>
          <option value="STOPPED">Stopped</option>
        </select>
      </div>

      {/* Table */}
      <div className="rzp-card">
        <table className="rzp-table">
          <thead>
            <tr>
              <th>Case ID</th>
              <th>Scenario</th>
              <th>Customer</th>
              <th>Amount</th>
              <th>Diagnosis & Code</th>
              <th>Probability</th>
              <th>Status</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredCases.map((c) => (
              <tr key={c.id}>
                <td>
                  <div style={{ fontWeight: 600, color: 'var(--rzp-navy)' }}>{c.id}</div>
                  <div style={{ fontSize: '11px', color: 'var(--rzp-text-muted)' }}>
                    {new Date(c.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </td>
                <td>
                  <span style={{ fontSize: '11px', padding: '2px 7px', borderRadius: 4, backgroundColor: '#f1f5f9', fontWeight: 600, color: '#475569' }}>
                    {c.scenario}
                  </span>
                </td>
                <td>
                  <div style={{ fontWeight: 600 }}>{c.customer?.name}</div>
                  <div style={{ fontSize: '11.5px', color: 'var(--rzp-text-secondary)' }}>{c.customer?.phone}</div>
                </td>
                <td>
                  <div style={{ fontWeight: 700, fontSize: '14px', color: 'var(--rzp-navy)' }}>
                    ₹{c.amount?.toLocaleString('en-IN')}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--rzp-text-muted)' }}>{c.payment_method}</div>
                </td>
                <td>
                  <div style={{ fontWeight: 600, fontSize: '12.5px', color: '#b91c1c' }}>{c.failure_code}</div>
                  <div style={{ fontSize: '11px', color: 'var(--rzp-text-secondary)', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {c.failure_description}
                  </div>
                </td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <div style={{ width: 44, height: 5, backgroundColor: '#e2e8f0', borderRadius: 2, overflow: 'hidden' }}>
                      <div
                        style={{
                          width: `${Math.round(c.recovery_probability * 100)}%`,
                          height: '100%',
                          backgroundColor: c.recovery_probability >= 0.7 ? '#10b981' : c.recovery_probability >= 0.4 ? '#0c8ce9' : '#f59e0b'
                        }}
                      ></div>
                    </div>
                    <span style={{ fontSize: '12px', fontWeight: 700 }}>
                      {Math.round(c.recovery_probability * 100)}%
                    </span>
                  </div>
                </td>
                <td>
                  <span className={`status-pill ${c.status?.toLowerCase()}`}>
                    {c.status?.replace("_", " ")}
                  </span>
                </td>
                <td style={{ textAlign: 'right' }}>
                  <div style={{ display: 'flex', gap: 6, justifyContent: 'flex-end' }}>
                    {c.status === "PENDING_APPROVAL" && (
                      <button
                        onClick={() => onConfirmPlan(c.id)}
                        className="btn btn-primary btn-sm"
                        title="1-Click Approve Plan"
                      >
                        Approve
                      </button>
                    )}

                    {c.payment_link_url && (
                      <button
                        onClick={() => onOpenCheckout(c)}
                        className="btn btn-success btn-sm"
                        title="Simulate Razorpay Checkout"
                      >
                        <CreditCard size={12} /> Pay Link
                      </button>
                    )}

                    <button
                      onClick={() => onOpenVoice(c)}
                      className="btn btn-secondary btn-sm"
                      title="Launch Hinglish Voice Recovery Call"
                    >
                      <PhoneCall size={12} color="#0c8ce9" />
                    </button>

                    <button
                      onClick={() => onSelectCase(c.id)}
                      className="btn btn-secondary btn-sm"
                    >
                      Audit
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
