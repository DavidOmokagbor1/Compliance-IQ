# ComplianceIQ

**Autonomous compliance orchestration for Wealthsimple** — AI-assisted KYC with human-in-the-loop and bias monitoring.

## Problem

Wealthsimple must scale KYC/AML compliance while staying fair and auditable. Manual review of every application doesn't scale; fully automated decisions risk bias and regulatory gaps.

## Solution

ComplianceIQ combines:

1. **AI Agent** — Assesses applicant risk (FINTRAC-aligned) and recommends approve / escalate
2. **Human Arbitrator** — Makes final decisions on escalated cases; decisions are logged
3. **Bias Monitor** — Tracks approval parity (Canadian-born vs non-Canadian-born) and flags divergence

## Tech Stack

- **UI:** Streamlit
- **AI:** OpenAI GPT-4o (structured JSON output)
- **Persistence:** JSON decision log (Docker volume)
- **Tests:** pytest, Streamlit AppTest

## Setup

```bash
cd complianceiq
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: OPENAI_API_KEY=sk-your-actual-key
```

## Run

```bash
cd complianceiq
source .venv/bin/activate
streamlit run app.py
```

## Docker

```bash
docker compose up --build
```

Open http://localhost:8501. Decision log persists in a Docker volume.

## Tests

```bash
cd complianceiq
source .venv/bin/activate
pytest tests/ -v
```

- **Unit:** agent, bias_monitor, app helpers, mock_data
- **Integration:** agent + bias_monitor flow
- **E2E:** Streamlit AppTest UI

## Known Limitations (Demo)

- **Mock data only** — No real document extraction, ID verification, or sanctions APIs
- **No auth** — Prototype; production would add login and RBAC
- **Single JSON log** — Production would use PostgreSQL + audit tables
- **Bias monitor** — Single dimension (country of birth); production would expand

## Next Steps (Production)

1. Integrate real KYC providers (e.g. Trulioo, Jumio)
2. Add PostgreSQL + audit logging
3. Add authentication and role-based access
4. Expand bias monitoring (race, gender, etc.)
5. Add rule-based checks alongside LLM
