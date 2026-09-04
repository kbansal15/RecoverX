/**
 * RecoverX API Client
 */

const API_BASE = import.meta.env.VITE_API_BASE || "/api";

function getAuthHeaders() {
  const token = localStorage.getItem("recoverx_token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };
}

async function request(endpoint, options = {}) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...(options.headers || {})
    }
  });

  if (!res.ok) {
    let errorDetail = "API Error";
    try {
      const errJson = await res.json();
      errorDetail = errJson.detail || errJson.message || errorDetail;
    } catch {
      errorDetail = await res.text();
    }
    throw new Error(errorDetail);
  }

  return res.json();
}

export const api = {
  // Auth & Demo
  async loginDemo() {
    const data = await request("/auth/demo", { method: "POST" });
    if (data.token) {
      localStorage.setItem("recoverx_token", data.token);
      localStorage.setItem("recoverx_merchant", JSON.stringify(data.merchant));
    }
    return data;
  },
  async reseedDemo() {
    return request("/auth/reseed", { method: "POST" });
  },
  async getMe() {
    return request("/auth/me");
  },

  // Dashboard
  async getDashboardStats() {
    return request("/dashboard/stats");
  },

  // Recovery Cases
  async getRecoveryCases(params = {}) {
    const query = new URLSearchParams();
    if (params.scenario) query.set("scenario", params.scenario);
    if (params.status) query.set("status", params.status);
    if (params.search) query.set("search", params.search);
    return request(`/recovery-cases?${query.toString()}`);
  },
  async getRecoveryCase(caseId) {
    return request(`/recovery-cases/${caseId}`);
  },
  async confirmPlan(caseId) {
    return request(`/recovery-cases/${caseId}/confirm-plan`, { method: "POST" });
  },
  async escalateCase(caseId) {
    return request(`/recovery-cases/${caseId}/escalate`, { method: "POST" });
  },
  async stopCase(caseId) {
    return request(`/recovery-cases/${caseId}/stop`, { method: "POST" });
  },
  async createCase(data) {
    return request("/recovery-cases", {
      method: "POST",
      body: JSON.stringify(data)
    });
  },

  // Simulated Webhook Settle
  async completeTestPayment(caseId) {
    return request("/webhooks/demo/complete-test-payment", {
      method: "POST",
      body: JSON.stringify({ case_id: caseId })
    });
  },

  // Checkout Dropoffs
  async getDropoffs() {
    return request("/checkout-dropoffs");
  },
  async simulateDropoff(data) {
    return request("/checkout-dropoffs/simulate", {
      method: "POST",
      body: JSON.stringify(data)
    });
  },
  async recoverDropoff(id) {
    return request(`/checkout-dropoffs/${id}/recover`, { method: "POST" });
  },

  // Mandates & Recurring
  async getMandates() {
    return request("/mandates");
  },
  async simulateMandateFailure(data) {
    return request("/mandates/simulate-failure", {
      method: "POST",
      body: JSON.stringify(data)
    });
  },
  async sequenceMandate(id) {
    return request(`/mandates/${id}/sequence-retry`, { method: "POST" });
  },

  // Invoices & Receivables
  async getInvoices() {
    return request("/invoices");
  },
  async simulateInvoice(data) {
    return request("/invoices/simulate", {
      method: "POST",
      body: JSON.stringify(data)
    });
  },
  async chaseInvoice(id) {
    return request(`/invoices/${id}/chase`, { method: "POST" });
  },

  // Promise to Pay
  async getPromisesToPay(status = null) {
    const url = status ? `/promises-to-pay?status=${status}` : "/promises-to-pay";
    return request(url);
  },
  async recordPromise(data) {
    return request("/promises-to-pay", {
      method: "POST",
      body: JSON.stringify(data)
    });
  },
  async fulfillPromise(id) {
    return request(`/promises-to-pay/${id}/fulfill`, { method: "POST" });
  },

  // Voice Turn
  async sendVoiceTurn(caseId, transcript) {
    return request(`/voice/session/${caseId}/turn`, {
      method: "POST",
      body: JSON.stringify({ transcript })
    });
  },

  // Evaluation
  async runEvaluation(caseCount = 100) {
    return request(`/evaluation/run?cases_count=${caseCount}`, { method: "POST" });
  },
  async getEvaluationHistory() {
    return request("/evaluation/history");
  },

  // Policy
  async getPolicy() {
    return request("/merchant/policy");
  },
  async updatePolicy(data) {
    return request("/merchant/policy", {
      method: "PUT",
      body: JSON.stringify(data)
    });
  },

  // Audit Logs
  async getAuditLogs(params = {}) {
    const query = new URLSearchParams();
    if (params.case_id) query.set("case_id", params.case_id);
    if (params.event_type) query.set("event_type", params.event_type);
    if (params.limit) query.set("limit", params.limit);
    return request(`/audit-logs?${query.toString()}`);
  }
};
