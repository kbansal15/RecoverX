# RecoverX — Autonomous AI Revenue Recovery Agent

**Enterprise-grade AI Revenue Recovery for Razorpay Merchants**  
*Built for the Razorpay AI Buildathon — Track 03: AI Revenue Recovery*

---

##  Executive Summary

Every year, merchants lose billions to payment failures, checkout abandonments, failed recurring subscriptions, and aging B2B invoices. **RecoverX** is an autonomous, policy-governed revenue recovery engine designed natively for Razorpay merchants.

Instead of generic blasting of payment links or blind retries, RecoverX executes an intelligent, bounded loop:
1. **Identifies** root causes across 12 distinct banking/gateway failure vectors.
2. **Calculates** a transparent, multi-factor recovery propensity score (0–100%).
3. **Applies** deterministic policy precedence (merchant ceilings, refusal supremacy, attempt caps).
4. **Requires** 1-click merchant confirmation before initiating customer interventions.
5. **Engages** customers through dynamic smart payment links, salary-timed mandate retries, progressive B2B invoice chasers, or an interactive Hinglish voice concierge.
6. **Credits** recovered revenue **strictly and only** upon receipt of a cryptographically verified (`HMAC-SHA256`) Razorpay webhook.

---

##  System Architecture

### Core Recovery Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    REVENUE RECOVERY LIFECYCLE                                    │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
    │
    ├─► 1. INGEST & DETECT
    │      Razorpay Webhook / Cart Abandonment / Mandate Failure / Overdue Invoice
    │
    ├─► 2. ROOT CAUSE DIAGNOSIS
    │      Deterministic classification across 12 banking & gateway error codes
    │
    ├─► 3. TRANSPARENT SCORING ENGINE
    │      Formula: Success Ratio (30%) + Root Cause (20%) + Recency (15%) +
    │               Activity (15%) + Prior Recovery (10%) + Attempt Penalty (10%)
    │
    ├─► 4. POLICY PRECEDENCE GATE (Bounded Autonomy)
    │      OPT_OUT (Supremacy) ➔ AMOUNT_CEILING (₹50,000) ➔ WINDOW (72h) ➔ ATTEMPTS (2 Max)
    │
    ├─► 5. MERCHANT CONFIRMATION GATE
    │      1-Click Approval drawer with full explainability breakdown
    │
    ├─► 6. MULTI-SCENARIO INTERVENTION DISPATCH
    │      ├── Dynamic Razorpay Payment Link (WhatsApp/SMS)
    │      ├── Interactive Hinglish Voice Concierge (Gemini 2.5 Flash + Deterministic Fallback)
    │      ├── Intelligent Mandate Sequencer (Salary cycle & clearing hour scheduler)
    │      └── Tiered B2B Invoice Chaser (Aging buckets: 1–15d, 16–30d, 30+d)
    │
    ├─► 7. VERIFIED WEBHOOK SETTLEMENT
    │      Constant-time HMAC-SHA256 verification (Zero credit without proof of payment)
    │
    └─► 8. IMMUTABLE AUDIT TRAIL
           Cryptographically trackable, tamper-evident recovery history
```

---

##  Key Features & Recovery Vectors

### 1. Payment Failure Recovery (B2C Checkout)
- **12 Failure Root Causes:** Differentiates between technical transient errors (`GATEWAY_ERROR`, `NETWORK_TIMEOUT`), funds/mandate issues (`INSUFFICIENT_FUNDS`, `LIMIT_EXCEEDED`), customer friction (`OTP_TIMEOUT`, `AUTHENTICATION_FAILED`), and fatal card issues (`CARD_EXPIRED`, `CARD_BLOCKED`).
- **Dynamic Payment Links:** Creates instant Razorpay Test Mode Payment Links pre-filled with customer details, item descriptors, and automated WhatsApp/SMS delivery.

### 2. Checkout Drop-offs & Cart Abandonment
- **Funnel Stage Monitoring:** Detects user drop-offs at critical checkout stages (`OTP_VERIFICATION`, `PAYMENT_METHOD_SELECTION`, `ADDRESS_STEP`).
- **1-Click Cart Rehydration:** Generates personalized checkout recovery links preserving cart state and item details to re-engage high-intent buyers.

### 3. Intelligent Mandate & Subscription Sequencer
- **Optimal Debit Window Prediction:** Avoids blind recurring auto-debits that trigger bank penalties.
- **Salary Cycle & Banking Hours:** Automatically schedules retries during national salary disbursement windows (1st–5th of each month) and interbank clearing hours (09:30–11:30 IST).
- **Supports:** UPI AutoPay, e-Mandates, and card-based recurring charges.

### 4. B2B Receivables & Overdue Invoice Chaser
- **Aging Bucket Classification:** Groups receivables into `1–15 days`, `16–30 days`, and `30+ days` overdue.
- **Progressive Dunning Matrix:** Escalates communications from polite reminders (Tier 1) to formal payment link dispatches (Tier 2) and executive account management escalations (Tier 3).

### 5. Promise-to-Pay (PTP) State Machine
- **Lifecycle Management:** Tracks promises through `PENDING` ➔ `FULFILLED` or `BROKEN`.
- **Dunning Grace Period:** Automatically silences outreach until the agreed promised date.
- **Auto-Fulfillment:** Automatically marks promises fulfilled when matching payment settlements arrive.

### 6. Interactive Hinglish Voice Concierge
- **Bilingual Dialogue:** Speaks and understands natural conversational Hinglish, Hindi, and English.
- **Hybrid NLU Engine:** Powered by Gemini 2.5 Flash for nuanced understanding with an instant deterministic regex fallback.
- **Direct Action Execution:**
  - *Customer says "Abhi link bhej do":* Instantly sends a Razorpay payment link.
  - *Customer says "Salary 5 tarikh ko aayegi":* Automatically records a Promise-to-Pay for the 5th and pauses follow-ups.
  - *Customer says "Nahi chahiye, band karo":* Immediately invokes Refusal Supremacy and halts all contact.

### 7. 100-Case Batch Evaluation Benchmark
- **Monte Carlo Simulator:** Evaluates the recovery agent across 100 diverse, realistic synthetic cases spanning all 4 scenarios.
- **Deterministic Metrics:** Measures recovery rate, total money recovered, policy compliance, escalation rate, and average latency per case.

---

##  Bounded Autonomy & Safety Architecture

RecoverX is built on strict **bounded autonomy** principles to ensure AI never harms customer relationships or acts beyond merchant authorization:

| Rule | Policy Guardrail | System Behavior |
|---|---|---|
| **0. Action Allowlist** | Strict finite set | Only 7 explicitly approved actions are executable (`CREATE_PAYMENT_LINK`, `START_VOICE_RECOVERY`, `SCHEDULE_MANDATE_RETRY`, `DISPATCH_INVOICE_CHASER`, `RECORD_PROMISE_TO_PAY`, `ESCALATE`, `STOP`). |
| **1. Refusal Supremacy** | Customer Opt-Out wins unconditionally | If a customer opts out or says "Stop" during voice/SMS, the case is marked `STOPPED` immediately. |
| **2. Autonomous Ceiling** | High-value threshold (₹50,000) | Cases with amounts > ₹50,000 are structurally prevented from autonomous execution and escalated for merchant sign-off. |
| **3. Recovery Window** | Time Horizon (72 Hours) | Once 72 hours have elapsed from the initial failure, the case is marked `EXPIRED` to avoid customer harassment. |
| **4. Contact Frequency** | Hard Cap (Max 2 contacts, 1 voice) | Prevents dunning fatigue. Once limits are met, automated contact halts. |
| **5. Confirmation Gate** | Explicit Merchant Approval | Interventions require 1-click merchant confirmation from the dashboard before dispatch. |

---

##  Scoring Formula & Explainability

Every recovery case receives a deterministic **Recovery Propensity Score** ($S \in [0.0, 1.0]$):

$$S = 0.30 \cdot R_{success} + 0.20 \cdot F_{cause} + 0.15 \cdot F_{recency} + 0.15 \cdot F_{activity} + 0.10 \cdot F_{prior} + 0.10 \cdot F_{penalty}$$

Where:
- **$R_{success}$ (30%):** Historical payment success ratio of the customer ($\frac{\text{successful}}{\text{total}}$).
- **$F_{cause}$ (20%):** Root cause recovery factor (e.g., 0.95 for transient timeouts; 0.10 for blocked cards).
- **$F_{recency}$ (15%):** Linear time decay over the 72-hour recovery window.
- **$F_{activity}$ (15%):** Customer activity recency factor (1.0 if active $\le 30$ days).
- **$F_{prior}$ (10%):** Historical success rate in prior recovery campaigns.
- **$F_{penalty}$ (10%):** Attempt penalty factor reducing score by 0.3 for each prior failed attempt.

Every score is accompanied by human-readable reason codes (e.g., `HIGH_HISTORICAL_SUCCESS_RATIO`, `RETRYABLE_ROOT_CAUSE`).

---

##  Honest Revenue Measurement

A core vulnerability in recovery systems is "hallucinated recovery" (claiming credit for payments that never happened). RecoverX guarantees **cryptographic honesty**:

- **HMAC-SHA256 Verification:** All incoming Razorpay webhook payloads are verified against the merchant's `RAZORPAY_WEBHOOK_SECRET` using `hmac.compare_digest` in constant time.
- **Strict Settlement Trigger:** Recovered revenue is credited **strictly and only** when an authentic `payment_link.paid` event is received and matched to the case notes.

---

##  Tech Stack

- **Backend:** Python 3.10+ / 3.14, FastAPI, SQLite with SQLAlchemy ORM, Pydantic v2
- **Integrations:** Official `razorpay` Python SDK, `google-genai` Python SDK (Gemini 2.5 Flash)
- **Frontend:** React 19, Vite, Lucide React, Custom Razorpay Merchant Design System (`#0c2340` Navy, `#0c8ce9` Blue)
- **Networking:** Unified reverse proxy in Vite forwarding `/api` to port `8000` with zero CORS friction
- **Testing:** `pytest`, `httpx`

---

##  Quick Start (Running on Any PC)

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.14)
- **Node.js 18+** (Tested on Node 22 / 24)

### 2. Install Dependencies
Run these two commands from the project root (`RecoverX`):

```bash
# 1. Install Python Backend Dependencies
pip install -r backend/requirements.txt

# 2. Install React Frontend Dependencies
npm --prefix frontend install
```

### 3. (Optional) Configure Gemini API Key
RecoverX comes with built-in zero-config defaults (SQLite local database + deterministic NLU fallback).  
If you have a Google Gemini API Key, create `backend/.env`:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Launch Application
From the repository root, start both servers concurrently:

```bash
python run.py
```

This single command:
1. Verifies that ports `8000` and `5173` are clear (and safely attaches if already running).
2. Automatically seeds initial canonical demo cases on first startup into the local SQLite database.
3. Concurrently starts the **FastAPI Backend** (`http://localhost:8000`).
4. Starts the **React Vite Frontend** (`http://localhost:5173`).
5. Ensures clean shutdown of all background processes upon pressing `Ctrl+C`.

### 5. Open in Browser
Visit **[http://localhost:5173](http://localhost:5173)** in Chrome or any modern browser.

---

##  Endpoints & API Reference

| Domain | Method | Endpoint | Description |
|---|---|---|---|
| **Auth** | `POST` | `/api/auth/demo` | Authenticate as canonical demo merchant |
| **Auth** | `POST` | `/api/auth/reseed` | Reset database to pristine 8-case canonical state |
| **Dashboard** | `GET` | `/api/dashboard/stats` | Aggregate revenue at risk, recovered amount, and recovery funnel |
| **Cases** | `GET` | `/api/recovery-cases` | List, search, and filter recovery cases |
| **Cases** | `POST` | `/api/recovery-cases` | Ingest and create a new revenue risk case |
| **Cases** | `POST` | `/api/recovery-cases/{id}/confirm-plan` | 1-Click Merchant Confirmation to execute recovery |
| **Cases** | `POST` | `/api/recovery-cases/{id}/escalate` | Manually escalate case to human account manager |
| **Cases** | `POST` | `/api/recovery-cases/{id}/stop` | Immediately halt contact on case |
| **Drop-offs** | `GET` | `/api/checkout-dropoffs` | List abandoned checkout sessions |
| **Drop-offs** | `POST` | `/api/checkout-dropoffs/simulate` | Ingest a simulated cart drop-off event |
| **Drop-offs** | `POST` | `/api/checkout-dropoffs/{id}/recover` | Generate 1-click cart rehydration link |
| **Mandates** | `GET` | `/api/mandates` | List recurring subscription mandates |
| **Mandates** | `POST` | `/api/mandates/simulate-failure` | Simulate UPI AutoPay / e-Mandate debit failure |
| **Mandates** | `POST` | `/api/mandates/{id}/sequence-retry` | Calculate optimal salary debit window and schedule retry |
| **Invoices** | `GET` | `/api/invoices` | List B2B accounts receivable by aging bucket |
| **Invoices** | `POST` | `/api/invoices/simulate` | Simulate overdue B2B invoice |
| **Invoices** | `POST` | `/api/invoices/{id}/chase` | Trigger tiered progressive dunning chaser |
| **PTP** | `GET` | `/api/promises-to-pay` | List active, fulfilled, or broken promises-to-pay |
| **PTP** | `POST` | `/api/promises-to-pay` | Record a new Promise-to-Pay with quiet period |
| **PTP** | `POST` | `/api/promises-to-pay/{id}/fulfill` | Mark promise fulfilled upon receipt of payment |
| **Voice** | `POST` | `/api/voice/session/{id}/turn` | Process interactive Hinglish voice turn with NLU |
| **Webhooks** | `POST` | `/api/webhooks/razorpay` | Real Razorpay webhook with HMAC-SHA256 signature verification |
| **Webhooks** | `POST` | `/api/webhooks/demo/complete-test-payment` | Demo simulator completing payment and triggering webhook |
| **Evaluation** | `POST` | `/api/evaluation/run` | Execute 100-case Monte Carlo benchmark |
| **Policy** | `GET / PUT` | `/api/merchant/policy` | Inspect or modify merchant bounded autonomy policy |
| **Audit** | `GET` | `/api/audit-logs` | Retrieve immutable event audit trail |

---

##  Testing & Verification

Run the complete backend test suite:

```bash
python -m pytest backend/tests/ -v
```

Build the frontend bundle:

```bash
npm --prefix frontend run build
```

---

##  License

Developed for the **Razorpay AI Buildathon (Track 03: AI Revenue Recovery)**. Released under the Apache 2.0 License.
