# ComplianceIQ — Presentation Guide

**Step-by-step process to present the app** (Wealthsimple demo, ~7–8 minutes)

---

## Before You Start

- [ ] App running (local or Docker): `streamlit run app.py` or `docker compose up`
- [ ] OpenAI API key in `.env`
- [ ] Browser at http://localhost:8501
- [ ] Clear decision log for a fresh demo (optional): delete `complianceiq/decision_log.json`

---

## Step 1: Context (1 min)

**Say:**  
*"ComplianceIQ is a demo of how AI can support KYC compliance at scale. Wealthsimple needs to process applications quickly while staying fair and auditable. This app shows three pieces: an AI agent that assesses risk, a human arbitrator who makes final calls on escalated cases, and a bias monitor that tracks approval parity."*

---

## Step 2: Onboarding Agent — Clean Auto-Approval (2 min)

1. **Navigate:** Sidebar → **Onboarding Agent**
2. **Select:** Scenario **A — Clean Auto-Approval** (Sarah Chen, TFSA)
3. **Point out:** Applicant details, ID document, sample government ID photo
4. **Click:** **Submit Application →**
5. **While it runs:** *"The agent is calling GPT-4o to assess the case. We show expected vs actual outcome for validation."*
6. **Result:** AUTO-APPROVED, risk score low
7. **Highlight:** Expected vs Actual ✓ Match, reasoning, processing speed

---

## Step 3: Onboarding Agent — Escalation (2 min)

1. **Select:** Scenario **C — Sanctions Fuzzy Match** (Viktor Petrov, RRSP)
2. **Point out:** PEP indicator, sanctions flags, Russia birth country
3. **Click:** **Submit Application →**
4. **Result:** ESCALATED (HIGH RISK)
5. **Expand:** Reasoning Trace (Intake ✓, Evidence ✓, Risk 🚩, Bias, Decision)
6. **Expand:** Risk Arbitrator Brief
7. **Click:** **✅ Approve** (or Decline / Request Docs)
8. **Say:** *"That decision is now logged to the Bias Monitor with 'Decided By: Human'."*

---

## Step 4: Risk Arbitrator Dashboard (1 min)

1. **Navigate:** Sidebar → **Risk Arbitrator Dashboard**
2. **Say:** *"Pre-loaded escalated cases. The human reviews the brief and makes the call."*
3. **Select:** A case (e.g. Marcus Williams or Viktor Petrov)
4. **Enter:** A short decision reason
5. **Click:** Approve / Decline / Request Docs
6. **Say:** *"Each decision is persisted and appears in the Bias Monitor."*

---

## Step 5: Bias Monitor (1.5 min)

1. **Navigate:** Sidebar → **Bias Monitor**
2. **Point out:** Metrics — Approved, Escalated, Declined, Docs Requested, Human Decisions
3. **Point out:** Decision Log table with **Decided By** (AI vs Human)
4. **Say:** *"We track approval parity: Canadian-born vs non-Canadian-born. A gap over 10 percentage points triggers a review. This is one dimension; production would add more."*
5. **Read:** The "What is demographic parity?" section if time allows

---

## Step 6: Architecture & Limitations (1 min)

**Say:**  
*"This is a demo. We use mock data — no real document extraction or sanctions APIs. Production would integrate providers like Trulioo or Jumio, use PostgreSQL for audit logs, and add authentication. The bias monitor is a starting point; we'd expand to more protected attributes."*

---

## Step 7: Q&A Prep

**Likely questions:**

| Question | Answer |
|----------|--------|
| Why GPT-4o? | Structured JSON output, good at reasoning. Production might use fine-tuned or smaller models for cost. |
| How do you handle LLM variability? | Expected vs actual validation; production would add rule-based checks. |
| What about audit? | Every decision (AI and human) is logged with timestamp, decision, risk score, decided_by. |
| Bias monitor threshold? | 10pp is a starting point; would be tuned with compliance. |

---

## Timing Summary

| Step | Duration |
|------|----------|
| 1. Context | 1 min |
| 2. Auto-approval (Scenario A) | 2 min |
| 3. Escalation (Scenario C) + Human decision | 2 min |
| 4. Risk Arbitrator Dashboard | 1 min |
| 5. Bias Monitor | 1.5 min |
| 6. Architecture & limitations | 1 min |
| **Total** | **~8.5 min** |

---

## Troubleshooting

- **Agent error:** Check `.env` has valid `OPENAI_API_KEY`
- **Empty decision log:** Run Scenario A or C first, then check Bias Monitor
- **Docker:** Ensure Colima or Docker Desktop is running
