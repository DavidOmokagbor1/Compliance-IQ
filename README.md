# ComplianceIQ

**Autonomous compliance orchestration for financial institutions** — AI-assisted KYC with human-in-the-loop and bias monitoring.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-green.svg)](https://openai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Table of Contents

- [About](#about)
- [Problem](#problem)
- [Solution](#solution)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the App](#running-the-app)
- [Demo Scenarios](#demo-scenarios)
- [Testing](#testing)
- [Known Limitations](#known-limitations)
- [Production Roadmap](#production-roadmap)
- [Troubleshooting](#troubleshooting)

---

## About

ComplianceIQ is a **demo application** that showcases how AI can support Know Your Customer (KYC) and Anti-Money Laundering (AML) compliance at scale. Built for financial institutions, it demonstrates a human-in-the-loop workflow where an AI agent assesses applicant risk, human arbitrators make final decisions on escalated cases, and a bias monitor tracks approval parity across demographics.

---

## Problem

Financial institutions must scale KYC/AML compliance while staying **fair** and **auditable**. Manual review of every application doesn't scale; fully automated decisions risk bias and regulatory gaps. Banks, fintechs, and asset managers need:

- **Speed** — Process applications quickly without bottlenecks
- **Fairness** — Ensure no demographic group is disproportionately approved or declined
- **Auditability** — Full traceability of who decided what and why

---

## Solution

ComplianceIQ combines three components:

| Component | Role |
|-----------|------|
| **AI Agent** | Assesses applicant risk (FINTRAC-aligned), recommends approve / escalate, generates reasoning traces |
| **Human Arbitrator** | Makes final decisions on escalated cases; every decision is logged with `decided_by: Human` |
| **Bias Monitor** | Tracks approval parity (Canadian-born vs non-Canadian-born), flags divergence >10pp for review |

---

## Features

- **Onboarding Agent** — Submit mock KYC scenarios; AI returns structured risk assessment with reasoning trace
- **Expected vs Actual** — Validates AI output against expected outcome for each scenario
- **Risk Arbitrator Dashboard** — Review escalated cases, approve/decline/request docs; decisions persisted
- **Bias Monitor** — Metrics (Approved, Escalated, Declined, Docs Requested, Human Decisions) and decision log with AI vs Human attribution
- **Demographic Parity** — Tracks Canadian-born vs non-Canadian-born approval rates; alerts on >10pp gap
- **Docker Support** — Run with `docker compose up`; decision log persists in a volume

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ComplianceIQ Streamlit App                   │
├─────────────────────────────────────────────────────────────────┤
│  Onboarding Agent    │  Risk Arbitrator Dashboard  │  Bias Monitor │
│  - Scenario select   │  - Escalated cases          │  - Metrics     │
│  - AI assessment     │  - Approve/Decline/Docs    │  - Parity      │
│  - Human override    │  - Decision reason          │  - Decision log│
└──────────┬──────────────────────┬──────────────────────┬───────────┘
           │                      │                      │
           ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  agent.py (OpenAI GPT-4o)  │  bias_monitor.py  │  decision_log.json │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **UI** | Streamlit |
| **AI** | OpenAI GPT-4o (structured JSON output) |
| **Persistence** | JSON decision log (Docker volume for production-like setup) |
| **Tests** | pytest, Streamlit AppTest |
| **Container** | Docker, docker-compose |

---

## Project Structure

```
Compliance IQ/
├── complianceiq/
│   ├── app.py              # Streamlit UI (Onboarding Agent, Arbitrator, Bias Monitor)
│   ├── agent.py            # KYC case agent + arbitrator brief (OpenAI)
│   ├── bias_monitor.py     # Decision logging, parity checks
│   ├── mock_data.py       # Demo scenarios (A, B, C)
│   ├── requirements.txt
│   ├── .env.example
│   ├── .streamlit/config.toml
│   ├── assets/             # ID photos for demo
│   └── tests/
│       ├── test_agent.py
│       ├── test_app.py
│       ├── test_bias_monitor.py
│       ├── test_e2e.py
│       ├── test_integration.py
│       └── test_mock_data.py
├── docker-compose.yml
├── PRESENTATION.md         # Step-by-step demo guide
└── README.md
```

---

## Prerequisites

- **Python 3.12+** (or use Docker)
- **OpenAI API key** — [Create one](https://platform.openai.com/api-keys)
- **Docker** (optional) — For containerized run

---

## Installation

### Option 1: Local (venv)

```bash
cd complianceiq
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Option 2: Docker

```bash
# From project root
docker compose up --build
```

---

## Configuration

1. Copy the example env file:

   ```bash
   cp complianceiq/.env.example complianceiq/.env
   ```

2. Edit `complianceiq/.env` and add your OpenAI API key:

   ```
   OPENAI_API_KEY=sk-your-actual-key
   ```

3. For Docker, ensure `complianceiq/.env` exists before running `docker compose up`.

---

## Running the App

### Local

```bash
cd complianceiq
source .venv/bin/activate
streamlit run app.py
```

### Docker

```bash
docker compose up --build
```

Open **http://localhost:8501** in your browser. The decision log persists in a Docker volume (`complianceiq-data`).

---

## Demo Scenarios

| Scenario | Name | Expected Outcome |
|----------|------|------------------|
| **A** | Clean Auto-Approval | AUTO_APPROVED — Sarah Chen, TFSA, no flags |
| **B** | Multi-Product Complexity | ESCALATED — Marcus Williams, multiple products in one session |
| **C** | Sanctions Fuzzy Match | ESCALATED — Viktor Petrov, PEP indicator, sanctions flags, Russia birth country |

Each scenario includes mock applicant data, ID document, extraction confidence, and expected outcome for validation.

---

## Testing

```bash
cd complianceiq
source .venv/bin/activate
pytest tests/ -v
```

| Test Suite | Coverage |
|------------|----------|
| **Unit** | agent, bias_monitor, app helpers, mock_data |
| **Integration** | agent + bias_monitor flow |
| **E2E** | Streamlit AppTest UI |

---

## Known Limitations (Demo)

- **Mock data only** — No real document extraction, ID verification, or sanctions APIs
- **No auth** — Prototype; production would add login and RBAC
- **Single JSON log** — Production would use PostgreSQL + audit tables
- **Bias monitor** — Single dimension (country of birth); production would expand to race, gender, etc.
- **LLM variability** — Expected vs actual helps validate; production would add rule-based checks

---

## Production Roadmap

1. Integrate real KYC providers (e.g. Trulioo, Jumio)
2. Add PostgreSQL + audit logging
3. Add authentication and role-based access
4. Expand bias monitoring (race, gender, age, etc.)
5. Add rule-based checks alongside LLM
6. Fine-tune or use smaller models for cost optimization

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Agent error** | Ensure `complianceiq/.env` has a valid `OPENAI_API_KEY` |
| **Empty decision log** | Run Scenario A or C first, then check Bias Monitor |
| **Docker build fails** | Ensure Docker Desktop or Colima is running |
| **Port 8501 in use** | Streamlit will use 8502; or stop the other process |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Acknowledgments

Built as a demo for financial institutions' compliance workflows. FINTRAC-aligned risk assessment; bias monitoring inspired by fairness-in-AI best practices.
