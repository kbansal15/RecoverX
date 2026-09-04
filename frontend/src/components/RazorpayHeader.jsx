import React from "react";
import { Search, RefreshCw, AlertCircle, ShieldCheck, Zap } from "lucide-react";

export function RazorpayHeader({ merchant, onReseed, onSimulateFailure, loading }) {
  return (
    <header className="top-header">
      <div className="header-left">
        <div className="mode-badge test">
          <span style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: '#f59e0b' }}></span>
          TEST MODE
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '13px', color: 'var(--rzp-text-secondary)' }}>
          <span style={{ fontWeight: 600, color: 'var(--rzp-navy)' }}>{merchant?.name || "Razorpay Merchant"}</span>
          <span style={{ color: 'var(--rzp-text-muted)' }}>•</span>
          <span style={{ fontSize: '12px', fontFamily: 'monospace' }}>ID: {merchant?.id || "merch_demo"}</span>
        </div>
      </div>

      <div className="header-search">
        <Search size={15} />
        <input type="text" placeholder="Search cases, customers, orders... (Ctrl+K)" />
      </div>

      <div className="header-right">
        <button
          onClick={onSimulateFailure}
          className="btn btn-secondary btn-sm"
          title="Simulates an inbound failed payment into the recovery agent"
        >
          <Zap size={14} color="#0c8ce9" />
          Simulate Failure
        </button>

        <button
          onClick={onReseed}
          disabled={loading}
          className="btn btn-primary btn-sm"
          title="Reset database to pristine 8-case canonical state"
        >
          <RefreshCw size={14} className={loading ? "spin-animation" : ""} />
          Reset
        </button>
      </div>
    </header>
  );
}
