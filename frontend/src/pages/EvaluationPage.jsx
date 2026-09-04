import React, { useState } from "react";
import { BarChart3, Play, CheckCircle2, ShieldCheck, Clock, TrendingUp, AlertCircle } from "lucide-react";
import { MetricCard } from "../components/MetricCard";

export function EvaluationPage({ onRunEvaluation, history, loading }) {
  const [caseCount, setCaseCount] = useState(100);
  const [currentRun, setCurrentRun] = useState(history?.[0] || null);
  const [running, setRunning] = useState(false);

  const handleRun = async () => {
    setRunning(true);
    try {
      const res = await onRunEvaluation(caseCount);
      setCurrentRun(res);
    } catch (err) {
      alert(err.message || "Evaluation failed");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Batch Evaluation & Benchmark</h1>
          <p className="page-subtitle">
            Runs the exact production decision and recovery pipeline against a seeded 100-case dataset to measure honest recovery, escalation compliance, and stopping rules.
          </p>
        </div>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <select
            value={caseCount}
            onChange={(e) => setCaseCount(Number(e.target.value))}
            style={{ padding: '8px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--rzp-border)', fontSize: '13px', backgroundColor: '#ffffff' }}
          >
            <option value={50}>50 Cases Cohort</option>
            <option value={100}>100 Cases (Canonical Track 03 Benchmark)</option>
            <option value={150}>150 Cases Stress Test</option>
          </select>
          <button
            onClick={handleRun}
            disabled={running || loading}
            className="btn btn-primary"
          >
            <Play size={14} /> {running ? "Executing Evaluation..." : `Run ${caseCount}-Case Batch`}
          </button>
        </div>
      </div>

      {currentRun && (
        <>
          {/* Metrics */}
          <div className="metrics-grid">
            <MetricCard
              title="Measured Money Recovered"
              value={`₹${(currentRun.total_recovered_amount || 0).toLocaleString('en-IN')}`}
              badge={`${currentRun.recovery_rate_percentage || currentRun.recovery_rate}% Rate`}
              subtext="Honestly derived outcomes"
              icon={CheckCircle2}
              badgeColor="green"
            />

            <MetricCard
              title="Total Revenue at Risk"
              value={`₹${(currentRun.total_at_risk_amount || 0).toLocaleString('en-IN')}`}
              badge={`${currentRun.total_cases} Cases`}
              subtext="Batch cohort total"
              icon={TrendingUp}
              badgeColor="amber"
            />

            <MetricCard
              title="Escalation Compliance"
              value={currentRun.escalated_cases}
              subtext="Amount > ₹50k ceiling held"
              icon={ShieldCheck}
            />

            <MetricCard
              title="Execution Time"
              value={`${currentRun.duration_ms || currentRun.run_duration_ms} ms`}
              subtext="Blazingly fast Python"
              icon={Clock}
            />
          </div>

          {/* Sample Cases Table */}
          <div className="rzp-card">
            <div className="rzp-card-header">
              <span className="rzp-card-title">Detailed Evaluation Sample (25 Cases)</span>
              <span style={{ fontSize: '12px', color: 'var(--rzp-text-secondary)' }}>
                Average Recoverability Score: {currentRun.avg_recovery_score}%
              </span>
            </div>
            <table className="rzp-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Scenario</th>
                  <th>Amount</th>
                  <th>Failure Code</th>
                  <th>Calculated Probability</th>
                  <th>Candidate Action</th>
                  <th>Policy Precedence</th>
                  <th>Observed Status</th>
                </tr>
              </thead>
              <tbody>
                {(currentRun.sample_cases || []).map((sc, i) => (
                  <tr key={i}>
                    <td>{sc.case_index || i + 1}</td>
                    <td>
                      <span style={{ fontSize: '11px', padding: '2px 6px', borderRadius: 4, backgroundColor: '#f1f5f9', fontWeight: 600 }}>
                        {sc.scenario}
                      </span>
                    </td>
                    <td style={{ fontWeight: 700 }}>₹{sc.amount?.toLocaleString('en-IN')}</td>
                    <td style={{ fontSize: '12px', color: '#b91c1c', fontWeight: 500 }}>{sc.failure_code}</td>
                    <td>
                      <span style={{ fontWeight: 700, color: sc.recovery_probability >= 70 ? '#10b981' : '#0c8ce9' }}>
                        {sc.recovery_probability}%
                      </span>
                    </td>
                    <td>
                      <span style={{ fontSize: '12px', fontWeight: 500 }}>{sc.action}</span>
                    </td>
                    <td>
                      <span style={{ fontSize: '11.5px', fontWeight: 600, color: sc.policy_outcome === 'APPROVE' ? '#059669' : '#dc2626' }}>
                        {sc.policy_outcome}
                      </span>
                    </td>
                    <td>
                      <span className={`status-pill ${sc.final_status?.toLowerCase()}`}>
                        {sc.final_status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
