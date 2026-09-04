import React, { useState, useEffect } from "react";
import { api } from "./api/client";
import { RazorpaySidebar } from "./components/RazorpaySidebar";
import { RazorpayHeader } from "./components/RazorpayHeader";
import { CaseAuditDrawer } from "./components/CaseAuditDrawer";
import { RazorpayCheckoutModal } from "./components/RazorpayCheckoutModal";
import { VoiceAssistantModal } from "./components/VoiceAssistantModal";

// Pages
import { DashboardPage } from "./pages/DashboardPage";
import { RecoveryCasesPage } from "./pages/RecoveryCasesPage";
import { CheckoutDropoffsPage } from "./pages/CheckoutDropoffsPage";
import { MandateSequencerPage } from "./pages/MandateSequencerPage";
import { B2BReceivablesPage } from "./pages/B2BReceivablesPage";
import { PromiseToPayPage } from "./pages/PromiseToPayPage";
import { EvaluationPage } from "./pages/EvaluationPage";
import { MerchantPolicyPage } from "./pages/MerchantPolicyPage";
import { IntegrationPage } from "./pages/IntegrationPage";

export default function App() {
  const [activeTab, setActiveTab] = useState("overview");
  const [merchant, setMerchant] = useState(null);
  const [stats, setStats] = useState(null);
  const [cases, setCases] = useState([]);
  const [dropoffs, setDropoffs] = useState([]);
  const [mandates, setMandates] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [promises, setPromises] = useState([]);
  const [policy, setPolicy] = useState(null);
  const [evalHistory, setEvalHistory] = useState([]);

  // Modals & Drawers
  const [selectedCaseId, setSelectedCaseId] = useState(null);
  const [activeCaseDetails, setActiveCaseDetails] = useState(null);
  const [checkoutCase, setCheckoutCase] = useState(null);
  const [voiceCase, setVoiceCase] = useState(null);
  const [loading, setLoading] = useState(false);

  // Filters
  const [activeScenario, setActiveScenario] = useState("ALL");
  const [activeStatus, setActiveStatus] = useState("ALL");

  // Initial Load
  useEffect(() => {
    bootstrap();
  }, []);

  const bootstrap = async () => {
    setLoading(true);
    try {
      const authData = await api.loginDemo();
      setMerchant(authData.merchant);
      await refreshData();
    } catch (err) {
      console.error("Bootstrap error:", err);
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    try {
      const [
        dashStats,
        caseList,
        dropoffList,
        mandateList,
        invoiceList,
        promiseList,
        policyData,
        historyData
      ] = await Promise.all([
        api.getDashboardStats(),
        api.getRecoveryCases(),
        api.getDropoffs(),
        api.getMandates(),
        api.getInvoices(),
        api.getPromisesToPay(),
        api.getPolicy(),
        api.getEvaluationHistory()
      ]);

      setStats(dashStats);
      setCases(caseList);
      setDropoffs(dropoffList);
      setMandates(mandateList);
      setInvoices(invoiceList);
      setPromises(promiseList);
      setPolicy(policyData);
      setEvalHistory(historyData);

      // If drawer is open, refresh active case
      if (selectedCaseId) {
        const refreshed = await api.getRecoveryCase(selectedCaseId);
        setActiveCaseDetails(refreshed);
      }
    } catch (err) {
      console.error("Refresh error:", err);
    }
  };

  // Case Drawer Trigger
  const handleSelectCase = async (caseId) => {
    setSelectedCaseId(caseId);
    try {
      const details = await api.getRecoveryCase(caseId);
      setActiveCaseDetails(details);
    } catch (err) {
      alert("Could not load case details: " + err.message);
    }
  };

  // Reseed Demo
  const handleReseed = async () => {
    setLoading(true);
    try {
      await api.reseedDemo();
      await refreshData();
    } catch (err) {
      alert("Reseed failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Simulate Inbound Payment Failure
  const handleSimulateFailure = async () => {
    try {
      await api.createCase({
        customer_id: "cust_amit_03",
        amount: 3899.0,
        scenario: "PAYMENT_FAILURE",
        failure_code: "GATEWAY_ERROR",
        payment_method: "UPI",
        description: "HDFC gateway timed out during processing"
      });
      await refreshData();
    } catch (err) {
      alert("Simulate failure error: " + err.message);
    }
  };

  // 1-Click Approve Plan
  const handleConfirmPlan = async (caseId) => {
    try {
      await api.confirmPlan(caseId);
      await refreshData();
    } catch (err) {
      alert("Approval blocked by policy: " + err.message);
    }
  };

  // Complete Payment Simulation
  const handlePaymentSuccess = async (caseId) => {
    await api.completeTestPayment(caseId);
    await refreshData();
  };

  // Hinglish Voice Turn
  const handleVoiceTurn = async (caseId, transcript) => {
    const res = await api.sendVoiceTurn(caseId, transcript);
    await refreshData();
    return res;
  };

  // Escalate & Stop
  const handleEscalate = async (caseId) => {
    await api.escalateCase(caseId);
    await refreshData();
  };

  const handleStop = async (caseId) => {
    await api.stopCase(caseId);
    await refreshData();
  };

  return (
    <div className="app-container">
      {/* Razorpay Sidebar */}
      <RazorpaySidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        counts={{
          pending_approval: stats?.pending_approval_count,
          checkout_dropoffs: stats?.domain_counts?.checkout_dropoffs,
          mandates: stats?.domain_counts?.mandates,
          invoices: stats?.domain_counts?.invoices,
          ptp_pending: stats?.ptp_pending_count
        }}
      />

      {/* Main View Area */}
      <div className="main-content-area">
        <RazorpayHeader
          merchant={merchant}
          onReseed={handleReseed}
          onSimulateFailure={handleSimulateFailure}
          loading={loading}
        />

        <main className="page-viewport">
          {activeTab === "overview" && (
            <DashboardPage
              stats={stats}
              recentCases={cases}
              onSelectCase={handleSelectCase}
              onConfirmPlan={handleConfirmPlan}
              onOpenCheckout={(c) => setCheckoutCase(c)}
              onOpenVoice={(c) => setVoiceCase(c)}
              setActiveTab={setActiveTab}
            />
          )}

          {activeTab === "cases" && (
            <RecoveryCasesPage
              cases={cases}
              onSelectCase={handleSelectCase}
              onConfirmPlan={handleConfirmPlan}
              onOpenCheckout={(c) => setCheckoutCase(c)}
              onOpenVoice={(c) => setVoiceCase(c)}
              onFilterChange={(sc, st) => {
                setActiveScenario(sc);
                setActiveStatus(st);
              }}
              activeScenario={activeScenario}
              activeStatus={activeStatus}
            />
          )}

          {activeTab === "dropoffs" && (
            <CheckoutDropoffsPage
              dropoffs={dropoffs}
              onSimulateDropoff={async (data) => {
                await api.simulateDropoff(data);
                await refreshData();
              }}
              onRecoverDropoff={async (id) => {
                await api.recoverDropoff(id);
                await refreshData();
              }}
              loading={loading}
            />
          )}

          {activeTab === "mandates" && (
            <MandateSequencerPage
              mandates={mandates}
              onSimulateMandate={async (data) => {
                await api.simulateMandateFailure(data);
                await refreshData();
              }}
              onSequenceRetry={async (id) => {
                await api.sequenceMandate(id);
                await refreshData();
              }}
              loading={loading}
            />
          )}

          {activeTab === "invoices" && (
            <B2BReceivablesPage
              invoices={invoices}
              onSimulateInvoice={async (data) => {
                await api.simulateInvoice(data);
                await refreshData();
              }}
              onChaseInvoice={async (id) => {
                await api.chaseInvoice(id);
                await refreshData();
              }}
              loading={loading}
            />
          )}

          {activeTab === "ptp" && (
            <PromiseToPayPage
              promises={promises}
              onFulfillPromise={async (id) => {
                await api.fulfillPromise(id);
                await refreshData();
              }}
            />
          )}

          {activeTab === "evaluation" && (
            <EvaluationPage
              history={evalHistory}
              onRunEvaluation={async (count) => {
                const res = await api.runEvaluation(count);
                await refreshData();
                return res;
              }}
              loading={loading}
            />
          )}

          {activeTab === "policy" && (
            <MerchantPolicyPage
              policy={policy}
              onUpdatePolicy={async (data) => {
                await api.updatePolicy(data);
                await refreshData();
              }}
              loading={loading}
            />
          )}

          {activeTab === "integration" && (
            <IntegrationPage merchant={merchant} />
          )}
        </main>
      </div>

      {/* Slide-out Case Audit Drawer */}
      {selectedCaseId && activeCaseDetails && (
        <CaseAuditDrawer
          caseData={activeCaseDetails}
          onClose={() => {
            setSelectedCaseId(null);
            setActiveCaseDetails(null);
          }}
          onConfirmPlan={handleConfirmPlan}
          onOpenCheckout={(c) => setCheckoutCase(c)}
          onOpenVoice={(c) => setVoiceCase(c)}
          onEscalate={handleEscalate}
          onStop={handleStop}
          loading={loading}
        />
      )}

      {/* Razorpay Standard Checkout Modal Simulation */}
      {checkoutCase && (
        <RazorpayCheckoutModal
          caseData={checkoutCase}
          onClose={() => setCheckoutCase(null)}
          onPaymentSuccess={handlePaymentSuccess}
        />
      )}

      {/* Hinglish Voice Assistant Modal */}
      {voiceCase && (
        <VoiceAssistantModal
          caseData={voiceCase}
          onClose={() => setVoiceCase(null)}
          onVoiceTurn={handleVoiceTurn}
        />
      )}
    </div>
  );
}
