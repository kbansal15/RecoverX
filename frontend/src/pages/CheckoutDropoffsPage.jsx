import React, { useState } from "react";
import { ShoppingCart, RefreshCw, Send, CheckCircle2, ArrowRight, Zap, AlertCircle } from "lucide-react";

export function CheckoutDropoffsPage({ dropoffs, onSimulateDropoff, onRecoverDropoff, loading }) {
  const [stage, setStage] = useState("OTP_VERIFICATION");
  const [item, setItem] = useState("Sony WH-1000XM5 Wireless Headphones");
  const [amount, setAmount] = useState(24999);

  const handleSimulate = async () => {
    await onSimulateDropoff({
      customer_id: "cust_rahul_01",
      amount: Number(amount),
      dropoff_stage: stage,
      cart_item_name: item
    });
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Checkout Drop-off Recovery Monitor</h1>
          <p className="page-subtitle">
            Detects cart abandonment, OTP hesitation, and checkout drop-offs; dispatches automated 1-click cart rehydration links.
          </p>
        </div>
      </div>

      {/* Simulator Widget */}
      <div className="rzp-card" style={{ padding: '20px', marginBottom: 24, backgroundColor: '#f0f9ff', borderColor: '#bae6fd' }}>
        <div style={{ fontSize: '14px', fontWeight: 700, color: '#0369a1', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
          <Zap size={16} /> Simulate Abandoned Checkout Session (Scenario B)
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12, alignItems: 'flex-end' }}>
          <div>
            <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--rzp-text-secondary)' }}>Abandoned Cart Item</label>
            <input
              type="text"
              value={item}
              onChange={(e) => setItem(e.target.value)}
              style={{ width: '100%', padding: '8px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--rzp-border)', marginTop: 4, fontSize: '13px' }}
            />
          </div>

          <div>
            <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--rzp-text-secondary)' }}>Amount (₹)</label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              style={{ width: '100%', padding: '8px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--rzp-border)', marginTop: 4, fontSize: '13px' }}
            />
          </div>

          <div>
            <label style={{ fontSize: '11px', fontWeight: 600, color: 'var(--rzp-text-secondary)' }}>Drop-off Stage</label>
            <select
              value={stage}
              onChange={(e) => setStage(e.target.value)}
              style={{ width: '100%', padding: '8px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--rzp-border)', marginTop: 4, fontSize: '13px', backgroundColor: '#ffffff' }}
            >
              <option value="OTP_VERIFICATION">OTP Verification Screen</option>
              <option value="PAYMENT_SELECTION">Payment Method Selection</option>
              <option value="ADDRESS_STEP">Shipping Address Step</option>
            </select>
          </div>

          <button
            onClick={handleSimulate}
            disabled={loading}
            className="btn btn-primary"
            style={{ height: 38 }}
          >
            <ShoppingCart size={15} /> Inject Drop-off
          </button>
        </div>
      </div>

      {/* Active Abandoned Sessions Table */}
      <div className="rzp-card">
        <div className="rzp-card-header">
          <span className="rzp-card-title">Tracked Drop-off Sessions ({dropoffs.length})</span>
        </div>
        <table className="rzp-table">
          <thead>
            <tr>
              <th>Session ID</th>
              <th>Customer</th>
              <th>Abandoned Items</th>
              <th>Amount</th>
              <th>Drop-off Stage & Reason</th>
              <th>Status</th>
              <th style={{ textAlign: 'right' }}>Recovery Action</th>
            </tr>
          </thead>
          <tbody>
            {dropoffs.map((d) => (
              <tr key={d.id}>
                <td>
                  <div style={{ fontWeight: 600, color: 'var(--rzp-navy)' }}>{d.id}</div>
                  <div style={{ fontSize: '11px', color: 'var(--rzp-text-muted)' }}>
                    {new Date(d.abandoned_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </td>
                <td>
                  <div style={{ fontWeight: 600 }}>{d.customer?.name}</div>
                  <div style={{ fontSize: '11px', color: 'var(--rzp-text-secondary)' }}>{d.customer?.phone}</div>
                </td>
                <td>
                  <div style={{ fontSize: '13px', fontWeight: 500 }}>
                    {d.cart_items?.[0]?.name || "Cart Items"}
                  </div>
                </td>
                <td>
                  <div style={{ fontWeight: 700, fontSize: '14px', color: 'var(--rzp-navy)' }}>
                    ₹{d.amount?.toLocaleString('en-IN')}
                  </div>
                </td>
                <td>
                  <span style={{ fontSize: '11px', padding: '2px 7px', borderRadius: 4, backgroundColor: '#fef3c7', color: '#92400e', fontWeight: 600 }}>
                    {d.dropoff_stage}
                  </span>
                  <div style={{ fontSize: '11.5px', color: 'var(--rzp-text-secondary)', marginTop: 3 }}>
                    {d.dropoff_reason}
                  </div>
                </td>
                <td>
                  <span className={`status-pill ${d.status?.toLowerCase()}`}>
                    {d.status}
                  </span>
                </td>
                <td style={{ textAlign: 'right' }}>
                  {d.status === "ABANDONED" ? (
                    <button
                      onClick={() => onRecoverDropoff(d.id)}
                      className="btn btn-primary btn-sm"
                    >
                      <Send size={12} /> Dispatch Rehydration Link
                    </button>
                  ) : (
                    <span style={{ fontSize: '12px', color: '#059669', fontWeight: 600 }}>
                      ✓ Link Dispatched
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
