import React from "react";

export function MetricCard({ title, value, subtext, badge, icon: Icon, badgeColor = "green" }) {
  return (
    <div className="metric-card">
      <div className="metric-header">
        <span>{title}</span>
        {Icon && <Icon size={18} color="#0c8ce9" />}
      </div>
      <div className="metric-value">{value}</div>
      <div className="metric-subtext">
        {badge && (
          <span className={`metric-badge-${badgeColor}`}>
            {badge}
          </span>
        )}
        <span style={{ color: 'var(--rzp-text-secondary)' }}>{subtext}</span>
      </div>
    </div>
  );
}
