import React, { useState } from "react";
import { Receipt, AlertTriangle, ArrowRight, Zap, Send, CreditCard, Shield } from "lucide-react";

export function B2BReceivablesPage({ invoices, onSimulateInvoice, onChaseInvoice, loading }) {
  const [client, setClient] = useState("Acme Technologies Pvt Ltd");
  const [amount, setAmount] = useState(65000);
  const [daysOverdue, setDaysOverdue] = useState(18);

  const handleSimulate = async () => {
    await onSimulateInvoice({
      customer_id: "cust_vikram_05",
      amount: Number(amount),
      days_overdue: Number(daysOverdue),
      invoice_number: `INV-2026-${Math.floor(100 + Math.random() * 900)}`
    });
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">B2B Overdue Receivables Chaser</h1>
          <p className="page-subtitle">
            Progressive aging bucket tracking (1-15d, 16-30d, 30+d), tiered communications, and partial settlement payment links.
          </p>
        </div>
      </div>

      {/* Simulator Widget */}
      <div className="rzp-card" style={{ padding: '20px', marginBottom: 24, backgroundColor: '#faf5ff', borderColor: '#e9d5ff' }}>
        <div style={{ fontSize: '14px', fontWeight: 700, color: '#7e22ce', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
          <Zap size={16} /> Simulate B2B Overdue Invoice
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12, alignItems: 'flex-end' }}>
          <div>
            <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--rzp-text-secondary)' }}>Corporate Client</label>
            <input
              type="text"
              value={client}
              onChange={(e) => setClient(e.target.value)}
              style={{ width: '100%', padding: '8px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--rzp-border)', marginTop: 4, fontSize: '13px' }}
            />
          </div>

          <div>
            <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--rzp-text-secondary)' }}>Invoice Amount (₹)</label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              style={{ width: '100%', padding: '8px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--rzp-border)', marginTop: 4, fontSize: '13px' }}
            />
          </div>

          <div>
            <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--rzp-text-secondary)' }}>Days Overdue</label>
            <input
              type="number"
              value={daysOverdue}
              onChange={(e) => setDaysOverdue(e.target.value)}
              style={{ width: '100%', padding: '8px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--rzp-border)', marginTop: 4, fontSize: '13px' }}
            />
          </div>

          <button
            onClick={handleSimulate}
            disabled={loading}
            className="btn btn-primary"
            style={{ height: 38 }}
          >
            <Receipt size={15} /> Inject Overdue Invoice
          </button>
        </div>
      </div>

      {/* Invoices Table */}
      <div className="rzp-card">
        <div className="rzp-card-header">
          <span className="rzp-card-title">Tracked Receivables ({invoices.length})</span>
        </div>
        <table className="rzp-table">
          <thead>
            <tr>
              <th>Invoice No.</th>
              <th>Client</th>
              <th>Amount</th>
              <th>Days Overdue</th>
              <th>Aging Bucket</th>
              <th>Escalation Tier</th>
              <th style={{ textAlign: 'right' }}>Chaser Action</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map((inv) => (
              <tr key={inv.id}>
                <td>
                  <div style={{ fontWeight: 600, color: 'var(--rzp-navy)' }}>{inv.invoice_number}</div>
                  <div style={{ fontSize: '11px', color: 'var(--rzp-text-muted)' }}>Due: {new Date(inv.due_date).toLocaleDateString()}</div>
                </td>
                <td>
                  <div style={{ fontWeight: 600 }}>{inv.customer?.name}</div>
                  <div style={{ fontSize: '11px', color: 'var(--rzp-text-secondary)' }}>{inv.customer?.phone}</div>
                </td>
                <td>
                  <div style={{ fontWeight: 700, fontSize: '14px', color: 'var(--rzp-navy)' }}>
                    ₹{inv.amount?.toLocaleString('en-IN')}
                  </div>
                </td>
                <td>
                  <span style={{ fontWeight: 700, color: inv.days_overdue > 30 ? '#dc2626' : inv.days_overdue > 15 ? '#b45309' : '#0369a1' }}>
                    {inv.days_overdue} days
                  </span>
                </td>
                <td>
                  <span
                    style={{
                      fontSize: '11px',
                      padding: '2px 8px',
                      borderRadius: 4,
                      fontWeight: 600,
                      backgroundColor: inv.aging_bucket === '30_PLUS_DAYS' ? '#fef2f2' : inv.aging_bucket === '16_30_DAYS' ? '#fffbeb' : '#f0f9ff',
                      color: inv.aging_bucket === '30_PLUS_DAYS' ? '#b91c1c' : inv.aging_bucket === '16_30_DAYS' ? '#92400e' : '#0369a1'
                    }}
                  >
                    {inv.aging_bucket?.replace(/_/g, " ")}
                  </span>
                </td>
                <td>
                  <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--rzp-navy)' }}>
                    Tier {inv.current_escalation_tier}: {inv.current_escalation_tier === 1 ? "Courtesy Reminder" : inv.current_escalation_tier === 2 ? "Finance Notice" : "Credit Hold Review"}
                  </span>
                </td>
                <td style={{ textAlign: 'right' }}>
                  <button
                    onClick={() => onChaseInvoice(inv.id)}
                    className="btn btn-secondary btn-sm"
                  >
                    <Send size={12} color="#0c8ce9" /> Advance Chase Tier
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
