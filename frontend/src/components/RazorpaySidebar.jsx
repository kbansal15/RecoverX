import React from "react";
import {
  LayoutDashboard,
  RotateCcw,
  ShoppingCart,
  Repeat,
  Receipt,
  CalendarCheck,
  BarChart3,
  Sliders,
  Webhook,
  Sparkles
} from "lucide-react";

export function RazorpaySidebar({ activeTab, setActiveTab, counts = {} }) {
  const navItems = [
    { id: "overview", label: "Dashboard", icon: LayoutDashboard, badge: null },
    { id: "cases", label: "Recovery Cases", icon: RotateCcw, badge: counts.pending_approval || null },
    { id: "dropoffs", label: "Checkout Drop-offs", icon: ShoppingCart, badge: counts.checkout_dropoffs || null },
    { id: "mandates", label: "Mandate Sequencer", icon: Repeat, badge: counts.mandates || null },
    { id: "invoices", label: "B2B Receivables", icon: Receipt, badge: counts.invoices || null },
    { id: "ptp", label: "Promise to Pay", icon: CalendarCheck, badge: counts.ptp_pending || null },
    { id: "evaluation", label: "Batch Evaluation", icon: BarChart3, badge: "100" },
    { id: "policy", label: "Merchant Policy", icon: Sliders, badge: null },
    { id: "integration", label: "Webhooks & API", icon: Webhook, badge: null },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="rzp-logo-badge">R</div>
        <div>
          <div style={{ fontWeight: 800, fontSize: '15px', letterSpacing: '-0.01em', color: '#ffffff', display: 'flex', alignItems: 'center', gap: 6 }}>
            RecoverX
          </div>
          <div style={{ fontSize: '11px', color: '#38bdf8', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4 }}>
            <Sparkles size={10} /> AI Revenue Recovery
          </div>
        </div>
      </div>

      <div className="sidebar-nav">
        <div className="nav-category">Recovery Engine</div>
        {navItems.slice(0, 6).map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <div
              key={item.id}
              className={`nav-item ${isActive ? "active" : ""}`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
              {item.badge && <span className="nav-badge">{item.badge}</span>}
            </div>
          );
        })}

        <div className="nav-category">Intelligence & Controls</div>
        {navItems.slice(6).map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <div
              key={item.id}
              className={`nav-item ${isActive ? "active" : ""}`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
              {item.badge && <span className="nav-badge">{item.badge}</span>}
            </div>
          );
        })}
      </div>

      <div style={{ padding: '16px', borderTop: '1px solid rgba(255, 255, 255, 0.08)', fontSize: '11px', color: '#94a3b8' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
          <span>Python Backend</span>
          <span style={{ color: '#10b981', fontWeight: 600 }}>Connected</span>
        </div>
        <div style={{ fontSize: '10px', color: '#64748b' }}>Razorpay Python SDK v1.4.2</div>
      </div>
    </aside>
  );
}
