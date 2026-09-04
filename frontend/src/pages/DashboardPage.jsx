import React from "react";
import {
  TrendingUp,
  AlertOctagon,
  CheckCircle2,
  Clock,
  ShieldAlert,
  ArrowUpRight,
  Sparkles,
  PhoneCall,
  CreditCard,
  Zap,
  Repeat,
  Receipt,
  ShoppingCart
} from "lucide-react";
import { MetricCard } from "../components/MetricCard";

export function DashboardPage({
  stats,
  recentCases,
  onSelectCase,
  onConfirmPlan,
  onOpenCheckout,
  onOpenVoice,
  setActiveTab
}) {
  if (!stats) return null;

  return (
    <div>
      {/* Page Title */}
      <div className="page-header">
        <div>
          <h1 className="page-title">AI Revenue Recovery Overview</h1>
          <p className="page-subtitle">
            Autonomous agent tracking degraded payments, abandoned drop-offs, recurring mandates, and overdue receivables.
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => setActiveTab("evaluation")} className="btn btn-secondary btn-sm">
            <Sparkles size={14} color="#0c8ce9" /> Run Batch Evaluation (100 Cases)
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="metrics-grid">
        <MetricCard
          title="Measured Money Recovered"
          value={`₹${(stats.total_revenue_recovered || 0).toLocaleString('en-IN')}`}
          badge={`${stats.recovery_rate_percentage}% Rate`}
          subtext="Verified by webhook"
          icon={CheckCircle2}
          badgeColor="green"
        />

        <MetricCard
          title="Total Revenue at Risk"
          value={`₹${(stats.total_revenue_at_risk || 0).toLocaleString('en-IN')}`}
          badge={`${stats.total_cases_count} cases`}
          subtext="Across all 4 scenarios"
          icon={AlertOctagon}
          badgeColor="amber"
        />

        <MetricCard
          title="Pending Merchant Approval"
          value={stats.pending_approval_count}
          subtext="Requires 1-click confirmation"
          icon={Clock}
        />

        <MetricCard
          title="Escalated for Review"
          value={stats.escalated_cases_count}
          subtext="Exceeds ₹50,000 ceiling"
          icon={ShieldAlert}
        />
      </div>

      {/* 4 Multi-Scenario Domain Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14, marginBottom: 24 }}>
        <div
          onClick={() => setActiveTab("cases")}
          style={{ padding: '16px', background: '#ffffff', border: '1px solid var(--rzp-border)', borderRadius: 'var(--radius-md)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 12 }}
        >
          <div style={{ width: 40, height: 40, borderRadius: '8px', background: 'var(--rzp-blue-subtle)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <CreditCard size={20} color="#0c8ce9" />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--rzp-text-secondary)', fontWeight: 600 }}>Payment Failures</div>
            <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--rzp-navy)' }}>
              {stats.scenario_counts?.PAYMENT_FAILURE || 0} active
            </div>
          </div>
        </div>

        <div
          onClick={() => setActiveTab("dropoffs")}
          style={{ padding: '16px', background: '#ffffff', border: '1px solid var(--rzp-border)', borderRadius: 'var(--radius-md)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 12 }}
        >
          <div style={{ width: 40, height: 40, borderRadius: '8px', background: '#ecfdf5', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <ShoppingCart size={20} color="#10b981" />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--rzp-text-secondary)', fontWeight: 600 }}>Checkout Drop-offs</div>
            <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--rzp-navy)' }}>
              {stats.domain_counts?.checkout_dropoffs || 0} sessions
            </div>
          </div>
        </div>

        <div
          onClick={() => setActiveTab("mandates")}
          style={{ padding: '16px', background: '#ffffff', border: '1px solid var(--rzp-border)', borderRadius: 'var(--radius-md)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 12 }}
        >
          <div style={{ width: 40, height: 40, borderRadius: '8px', background: '#fffbeb', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Repeat size={20} color="#f59e0b" />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--rzp-text-secondary)', fontWeight: 600 }}>Mandate Sequencer</div>
            <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--rzp-navy)' }}>
              {stats.domain_counts?.mandates || 0} recurring
            </div>
          </div>
        </div>

        <div
          onClick={() => setActiveTab("invoices")}
          style={{ padding: '16px', background: '#ffffff', border: '1px solid var(--rzp-border)', borderRadius: 'var(--radius-md)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 12 }}
        >
          <div style={{ width: 40, height: 40, borderRadius: '8px', background: '#f5f3ff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Receipt size={20} color="#8b5cf6" />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: 'var(--rzp-text-secondary)', fontWeight: 600 }}>B2B Receivables</div>
            <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--rzp-navy)' }}>
              {stats.domain_counts?.invoices || 0} invoices
            </div>
          </div>
        </div>
      </div>

      {/* Recovery Funnel Card */}
      <div className="rzp-card">
        <div className="rzp-card-header">
          <span className="rzp-card-title">Bounded Recovery Conversion Funnel</span>
          <span style={{ fontSize: '12px', color: 'var(--rzp-text-secondary)' }}>
            Honest End-to-End Tracking
          </span>
        </div>
        <div style={{ padding: '20px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 12 }}>
            {stats.recovery_funnel?.map((step, i) => (
              <div
                key={i}
                style={{
                  padding: '14px',
                  backgroundColor: i === 4 ? '#ecfdf5' : '#f8fafc',
                  border: `1px solid ${i === 4 ? '#a7f3d0' : '#e2e8f0'}`,
                  borderRadius: 'var(--radius-md)'
                }}
              >
                <div style={{ fontSize: '11px', color: 'var(--rzp-text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
                  Step 0{i + 1}
                </div>
                <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--rzp-navy)', marginTop: 4 }}>
                  {step.stage}
                </div>
                <div style={{ fontSize: '18px', fontWeight: 800, color: i === 4 ? '#059669' : '#0c8ce9', marginTop: 6 }}>
                  {step.count}
                </div>
                <div style={{ fontSize: '11.5px', color: 'var(--rzp-text-secondary)', marginTop: 2 }}>
                  ₹{step.amount?.toLocaleString('en-IN')}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Active Recovery Cases Table */}
      <div className="rzp-card">
        <div className="rzp-card-header">
          <span className="rzp-card-title">Recent Recovery Cases</span>
          <button onClick={() => setActiveTab("cases")} className="btn btn-secondary btn-sm">
            View All Cases <ArrowUpRight size={14} />
          </button>
        </div>
        <table className="rzp-table">
          <thead>
            <tr>
              <th>Case & Scenario</th>
              <th>Customer</th>
              <th>Amount</th>
              <th>Diagnosis</th>
              <th>Recoverability</th>
              <th>Status</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {recentCases?.slice(0, 6).map((c) => (
              <tr key={c.id}>
                <td>
                  <div style={{ fontWeight: 600, color: 'var(--rzp-navy)' }}>{c.id}</div>
                  <div style={{ fontSize: '11px', color: 'var(--rzp-text-muted)' }}>{c.scenario}</div>
                </td>
                <td>
                  <div style={{ fontWeight: 500 }}>{c.customer?.name}</div>
                  <div style={{ fontSize: '11px', color: 'var(--rzp-text-secondary)' }}>{c.customer?.phone}</div>
                </td>
                <td>
                  <div style={{ fontWeight: 700 }}>₹{c.amount?.toLocaleString('en-IN')}</div>
                  <div style={{ fontSize: '11px', color: 'var(--rzp-text-muted)' }}>{c.payment_method}</div>
                </td>
                <td>
                  <div style={{ fontSize: '12px', fontWeight: 500 }}>{c.failure_code}</div>
                  <div style={{ fontSize: '11px', color: 'var(--rzp-text-secondary)', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {c.failure_description}
                  </div>
                </td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <div style={{ width: 40, height: 4, backgroundColor: '#e2e8f0', borderRadius: 2, overflow: 'hidden' }}>
                      <div style={{ width: `${Math.round(c.recovery_probability * 100)}%`, height: '100%', backgroundColor: c.recovery_probability >= 0.7 ? '#10b981' : '#0c8ce9' }}></div>
                    </div>
                    <span style={{ fontSize: '12px', fontWeight: 600 }}>{Math.round(c.recovery_probability * 100)}%</span>
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
                        title="Approve recovery plan"
                      >
                        Approve
                      </button>
                    )}

                    {c.payment_link_url && (
                      <button
                        onClick={() => onOpenCheckout(c)}
                        className="btn btn-success btn-sm"
                        title="Simulate checkout payment"
                      >
                        <CreditCard size={12} /> Pay
                      </button>
                    )}

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
