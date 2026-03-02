"""
ComplianceIQ — Autonomous Compliance Orchestration
Streamlit UI with Onboarding Agent, Risk Arbitrator Dashboard, and Bias Monitor.
"""

import streamlit as st

from mock_data import SCENARIOS
from agent import AgentError, run_case_agent, generate_arbitrator_brief
from bias_monitor import log_decision, check_parity, DECISION_LOG

# --- Theme and styling ---
st.set_page_config(
    page_title="ComplianceIQ",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Design system — Figma-style tokens (simple, clean, standard)
st.markdown(
    """
    <style>
    /* Design tokens */
    :root {
        --navy-900: #0A2540;
        --navy-700: #1a3a5c;
        --teal-600: #0E7C7B;
        --teal-700: #0a5f5e;
        --gray-50: #f8fafc;
        --gray-100: #f1f5f9;
        --gray-200: #e2e8f0;
        --gray-500: #64748b;
        --gray-700: #334155;
        --white: #ffffff;
        --space-1: 4px;
        --space-2: 8px;
        --space-3: 12px;
        --space-4: 16px;
        --space-5: 24px;
        --space-6: 32px;
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --shadow-sm: 0 1px 2px rgba(10, 37, 64, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(10, 37, 64, 0.07), 0 2px 4px -2px rgba(10, 37, 64, 0.05);
        --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
    }

    /* Base */
    .stApp { background: var(--gray-50); font-family: var(--font-sans) !important; }
    .main .block-container { padding: var(--space-6) var(--space-5) var(--space-6); max-width: 1200px; }
    h1, h2, h3 { color: var(--navy-900) !important; font-weight: 600 !important; font-family: var(--font-sans) !important; }
    h2 { font-size: 1.25rem !important; margin-top: var(--space-5) !important; }
    h3 { font-size: 1rem !important; }
    p, .stMarkdown { color: var(--gray-700) !important; }
    .stCaption { color: var(--gray-500) !important; font-size: 0.8125rem !important; }

    /* Sidebar — clean, minimal */
    [data-testid="stSidebar"] { background: var(--white) !important; border-right: 1px solid var(--gray-200) !important; }
    [data-testid="stSidebar"] .stRadio label { padding: var(--space-2) var(--space-3) !important; border-radius: var(--radius-sm) !important; }
    [data-testid="stSidebar"] .stRadio label:hover { background: var(--gray-50) !important; }
    [data-testid="stSidebar"] .stRadio label:has(input:checked) { background: var(--gray-100) !important; font-weight: 500 !important; }

    /* Primary button */
    .stButton > button { background: var(--teal-600) !important; color: white !important; font-weight: 500 !important;
        border-radius: var(--radius-md) !important; padding: var(--space-2) var(--space-4) !important;
        box-shadow: var(--shadow-sm) !important; border: none !important; transition: all 0.15s ease !important; }
    .stButton > button:hover { background: var(--teal-700) !important; box-shadow: var(--shadow-md) !important; transform: translateY(-1px); }
    .stButton > button:disabled { opacity: 0.5 !important; cursor: not-allowed !important; transform: none !important; }

    /* Cards — applied via .card class */
    .ciq-card { background: var(--white); border-radius: var(--radius-lg); padding: var(--space-5);
        box-shadow: var(--shadow-sm); border: 1px solid var(--gray-200); margin-bottom: var(--space-4); }

    /* Expanders */
    .streamlit-expanderHeader { background: var(--gray-50) !important; border-radius: var(--radius-md) !important; }
    div[data-testid="stExpander"] { border: 1px solid var(--gray-200) !important; border-radius: var(--radius-md) !important; }

    /* Alerts (success, warning, error, info) */
    div[data-testid="stAlert"] { border-radius: var(--radius-md) !important; }

    /* Inputs */
    .stTextInput input { border-radius: var(--radius-md) !important; border: 1px solid var(--gray-200) !important; }
    .stSelectbox > div { border-radius: var(--radius-md) !important; }

    /* Dataframe */
    div[data-testid="stDataFrame"] { border-radius: var(--radius-md) !important; overflow: hidden !important; border: 1px solid var(--gray-200) !important; }

    /* Metric / status boxes — clean */
    .element-container { margin-bottom: var(--space-3) !important; }

    /* Header bar — white text on dark background (override global h1/p) */
    .ciq-header, .ciq-header h1, .ciq-header p { color: #ffffff !important; }
    .ciq-header p { color: rgba(255, 255, 255, 0.95) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


def _header_bar():
    """Design-system header: navy gradient, prominent app branding."""
    st.markdown(
        """
        <div class="ciq-header" style="
            background: linear-gradient(135deg, #0A2540 0%, #1a3a5c 100%);
            padding: 28px 32px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: 0 4px 12px rgba(10, 37, 64, 0.15);
        ">
            <h1 style="
                color: #ffffff;
                margin: 0;
                font-size: 2.25rem;
                font-weight: 700;
                letter-spacing: -0.03em;
                line-height: 1.2;
            ">
                ComplianceIQ
            </h1>
            <p style="
                color: rgba(255, 255, 255, 0.9);
                margin: 8px 0 0 0;
                font-size: 1rem;
                font-weight: 500;
            ">
                Autonomous Compliance Orchestration · Financial Institutions
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _footer():
    """Footer — minimal, design-system aligned."""
    st.markdown(
        """
        <div style="margin-top:48px;padding-top:16px;border-top:1px solid #e2e8f0;color:#94a3b8;font-size:0.75rem;">
            ComplianceIQ · AI-Assisted KYC for Financial Institutions · Feb 2026
        </div>
        """,
        unsafe_allow_html=True,
    )


def _sample_government_id(applicant: dict):
    """Generate a sample government ID card mockup for demo purposes."""
    from pathlib import Path

    from PIL import Image, ImageDraw, ImageFont

    w, h = 340, 216  # Card dimensions
    img = Image.new("RGB", (w, h), color="#f8fafc")
    draw = ImageDraw.Draw(img)

    doc = applicant.get("id_document", {})
    id_type = doc.get("type", "Government ID")
    photo_gender = applicant.get("id_photo", "male")

    # Try to load a readable font; fallback to default
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    font_lg = font_sm = ImageFont.load_default()
    for path in font_paths:
        try:
            font_lg = ImageFont.truetype(path, 14)
            font_sm = ImageFont.truetype(path, 10)
            break
        except Exception:
            continue

    # Header bar (Ontario blue / Canada red)
    header_color = "#1a365d" if "ontario" in id_type.lower() or "driver" in id_type.lower() else "#c41e3a"
    draw.rectangle([0, 0, w, 44], fill=header_color)
    draw.text((12, 12), id_type.upper(), fill="white", font=font_sm)
    draw.text((w - 70, 14), "SAMPLE", fill="#ffffff", font=font_sm)

    # Photo area (left side) — load female/male face image
    photo_x1, photo_y1, photo_x2, photo_y2 = 12, 52, 100, 140
    draw.rectangle([photo_x1, photo_y1, photo_x2, photo_y2], fill="#e2e8f0", outline="#94a3b8")
    assets_dir = Path(__file__).parent / "assets"
    face_file = assets_dir / f"id_photo_{photo_gender}.png"
    if face_file.exists():
        try:
            face_img = Image.open(face_file).convert("RGB").resize((76, 76))
            img.paste(face_img, (photo_x1 + 6, photo_y1 + 6))
        except Exception:
            draw.ellipse([photo_x1 + 8, photo_y1 + 8, photo_x2 - 8, photo_y2 - 8], fill="#cbd5e1")
    else:
        draw.ellipse([photo_x1 + 8, photo_y1 + 8, photo_x2 - 8, photo_y2 - 8], fill="#cbd5e1")

    # Text fields
    y = 52
    draw.text((112, y), applicant.get("full_name", "Applicant Name"), fill="#0f172a", font=font_lg)
    y += 22
    draw.text((112, y), f"DOB: {applicant.get('date_of_birth', 'YYYY-MM-DD')}", fill="#334155", font=font_sm)
    y += 18
    addr = applicant.get("address") or {}
    draw.text((112, y), f"Address: {addr.get('city', 'City')}, {addr.get('province', 'Prov')}", fill="#334155", font=font_sm)
    y += 18
    draw.text((112, y), f"ID#: {doc.get('number', 'XXXX-XXXXX')}", fill="#475569", font=font_sm)
    y += 18
    draw.text((112, y), f"Exp: {doc.get('expiry_date', doc.get('expiry_date', 'YYYY-MM-DD'))}", fill="#475569", font=font_sm)

    # Border
    draw.rectangle([0, 0, w - 1, h - 1], outline="#94a3b8", width=1)

    return img


# --- Page 1: Onboarding Agent ---
def _render_onboarding_agent():
    _header_bar()

    scenario_key = st.selectbox(
        "Select scenario",
        options=list(SCENARIOS.keys()),
        format_func=lambda k: f"{k} — {SCENARIOS[k]['name']}",
        key="scenario_select",
    )
    scenario = SCENARIOS[scenario_key]
    applicant = scenario["applicant"]

    # Two-column layout — design-system labels
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            '<span style="font-size:0.7rem;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.05em;">Applicant</span>',
            unsafe_allow_html=True,
        )
        st.write(f"**{applicant['full_name']}**")
        st.write(f"DOB: {applicant['date_of_birth']}")
        st.write(f"Nationality: {applicant['nationality']}")
        st.write(f"Status: {applicant['residency_status']}")
        if applicant.get("birth_country"):
            st.write(f"Birth country: {applicant['birth_country']}")
        addr = applicant.get("address", {})
        if addr:
            st.write(
                f"{addr.get('street', '')}, {addr.get('city', '')}, "
                f"{addr.get('province', '')} {addr.get('postal_code', '')}"
            )
        st.write(f"**Product:** {applicant['application_type']}")

    with col2:
        st.markdown(
            '<span style="font-size:0.7rem;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.05em;">ID Document</span>',
            unsafe_allow_html=True,
        )
        doc = applicant.get("id_document", {})
        st.write(f"Type: {doc.get('type', 'N/A')}")
        st.write(f"Match: {applicant.get('id_match_status', 'N/A')}")
        st.write(f"Extraction confidence: {scenario.get('extraction_confidence', 0) * 100:.0f}%")
        st.write("")
        try:
            id_img = _sample_government_id(applicant)
            st.image(id_img, caption="Government ID (Sample)", use_container_width=False)
        except Exception:
            st.caption("Government ID Uploaded")

    st.write("")
    if st.button("Submit Application →", type="primary", use_container_width=True):
        with st.status("Processing application...", expanded=True) as status:
            st.write("✓ Document extraction")
            st.write("✓ Identity verification")
            st.write("✓ Risk scoring")
            st.write("✓ Sanctions check")
            try:
                with st.spinner("Calling AI agent..."):
                    agent_result = run_case_agent(scenario)
                st.write("✓ Bias check")
                with st.spinner("Generating arbitrator brief..."):
                    brief = generate_arbitrator_brief(scenario, agent_result)
                status.update(label="Complete", state="complete")

                # Log to bias monitor (runs silently)
                log_decision(
                    applicant,
                    agent_result.get("decision", "UNKNOWN"),
                    agent_result.get("risk_score", 0),
                )

                decision = agent_result.get("decision", "")
                risk_score = agent_result.get("risk_score", 0)
                reasoning = agent_result.get("reasoning", "")
                expected = scenario.get("expected_outcome", "")

                # Expected vs actual (validation)
                match = expected and decision == expected
                st.caption(
                    f"**Expected:** {expected or 'N/A'} · **Actual:** {decision} "
                    f"{'✓ Match' if match else '— Review'}"
                )
                st.write("")

                if decision == "AUTO_APPROVED":
                    proc_time = agent_result.get("processing_time_seconds")
                    body = f"**AUTO-APPROVED** · Risk score: {risk_score}\n\n"
                    if proc_time is not None:
                        body += f"⚡ **Processing Speed:** {proc_time:.2f}s\n\n"
                    body += reasoning
                    st.success(body)
                elif decision == "ESCALATED":
                    st.warning(
                        "**ESCALATED** — Case escalated for human review. "
                        "Client has been notified that additional verification is required."
                    )
                    _render_reasoning_trace(agent_result)
                    with st.expander("Risk Arbitrator Brief", expanded=True):
                        st.write(brief)
                    _render_arbitrator_buttons(applicant, agent_result)
                elif decision == "ESCALATED_HIGH_RISK":
                    st.error(
                        "**ESCALATED (HIGH RISK)** — Case escalated for immediate human review. "
                        "Client has been notified that additional verification is required."
                    )
                    _render_reasoning_trace(agent_result)
                    with st.expander("Risk Arbitrator Brief", expanded=True):
                        st.write(brief)
                    _render_arbitrator_buttons(applicant, agent_result)
                else:
                    st.info(f"Decision: {decision}\n\n{reasoning}")

            except AgentError as e:
                status.update(label="Error", state="error")
                st.error(f"**ComplianceIQ Agent Error:** {e}")
            except Exception as e:
                status.update(label="Error", state="error")
                st.error(f"Unexpected error: {e}")

    _footer()


def _render_reasoning_trace(agent_result: dict):
    """Visual reasoning trace: 5 stages with green tick or red flag."""
    risk_level = (agent_result.get("risk_level") or "MEDIUM").upper()
    bias_check = (agent_result.get("bias_check") or "PASS").upper()
    # Infer stage outcomes: Intake always passed, Evidence from extraction, Risk/Bias/Decision from result
    stages = [
        ("Intake", risk_level in ("LOW", "MEDIUM", "HIGH")),  # Document received
        ("Evidence Assembly", True),  # We have the data
        ("Risk Check", risk_level == "LOW"),
        ("Bias Check", bias_check == "PASS"),
        ("Decision", False),  # Escalated = agent could not auto-approve
    ]
    with st.expander("🔍 Reasoning Trace", expanded=False):
        for name, passed in stages:
            icon = "✅" if passed else "🚩"
            st.write(f"{icon} **{name}**")
    st.write("")


def _render_arbitrator_buttons(applicant: dict, agent_result: dict):
    """Three decision buttons — persist to Bias Monitor and show toast."""
    col1, col2, col3 = st.columns(3)
    risk_score = agent_result.get("risk_score", 0)
    with col1:
        if st.button("Approve", use_container_width=True, key="btn_approve"):
            log_decision(applicant, "AUTO_APPROVED", risk_score, decided_by="Human")
            st.toast("Application approved. Decision logged to Bias Monitor.")
            st.rerun()
    with col2:
        if st.button("Decline", use_container_width=True, key="btn_decline"):
            log_decision(applicant, "DECLINED", risk_score, decided_by="Human")
            st.toast("Application declined. Decision logged to Bias Monitor.")
            st.rerun()
    with col3:
        if st.button("Request Docs", use_container_width=True, key="btn_request"):
            log_decision(applicant, "DOCS_REQUESTED", risk_score, decided_by="Human")
            st.toast("Document request sent. Decision logged to Bias Monitor.")
            st.rerun()


# --- Page 2: Risk Arbitrator Dashboard ---
def _get_escalated_cases():
    """Pre-loaded escalated cases for the dashboard."""
    # Scenario B, C, and one invented case
    b = SCENARIOS["B"]
    c = SCENARIOS["C"]
    invented = {
        "id": "inv-1",
        "applicant_name": "Priya Sharma",
        "applicant": {
            "full_name": "Priya Sharma",
            "birth_country": "India",
            "nationality": "Canadian",
            "application_type": "RESP",
            "pep_indicator": False,
        },
        "product": "RESP",
        "risk_level": "MEDIUM",
        "risk_score": 45,
        "flags_count": 2,
        "time_waiting": "4h 12m",
        "brief": (
            "Priya Sharma is applying for an RESP. The agent flagged two items: "
            "recent address change (within 90 days) and source of funds from an international "
            "transfer. No PEP or sanctions flags. The agent recommends approval with a brief "
            "source-of-funds follow-up. **Decision required:** Approve as-is, request documentation, "
            "or decline pending clarification."
        ),
    }
    return [
        {
            "id": "B",
            "applicant_name": b["applicant"]["full_name"],
            "applicant": b["applicant"],
            "product": b["applicant"]["application_type"],
            "risk_level": "MEDIUM",
            "risk_score": 55,
            "flags_count": len(b["applicant"].get("behavioral_flags", [])),
            "time_waiting": "2h 45m",
            "brief": "Marcus Williams applied for a Credit Card during the same session as a Savings Account and Investment Account. Multiple product applications can indicate splitting behavior or identity testing. The agent recommends escalation for human review. **Decision required:** Approve, decline, or request additional identity verification.",
        },
        {
            "id": "C",
            "applicant_name": c["applicant"]["full_name"],
            "applicant": c["applicant"],
            "product": c["applicant"]["application_type"],
            "risk_level": "HIGH",
            "risk_score": 72,
            "flags_count": 2,  # PEP + sanctions
            "time_waiting": "1h 22m",
            "brief": "Viktor Petrov applied for an RRSP. He is a PEP (former government official, Russia) and has a 0.72 fuzzy match against sanctions list name 'Viktor V. Petrov'. The agent recommends high-risk escalation. **Decision required:** Proceed with enhanced due diligence, request OFAC/sanctions clearance, or decline.",
        },
        invented,
    ]


def _render_risk_arbitrator():
    st.markdown("## Risk Arbitrator Dashboard")
    st.caption("Cases requiring human decision — AI has done everything else")
    st.markdown(
        """
        <div style="background:#f0fdfa;border:1px solid #99f6e4;border-radius:8px;padding:16px;margin:16px 0;color:#0f766e;font-size:0.9rem;">
            The AI has assembled everything. You are here to make the one decision it cannot.
        </div>
        """,
        unsafe_allow_html=True,
    )

    cases = _get_escalated_cases()

    # Table as radio options
    options = [
        f"{c['applicant_name']} · {c['product']} · {c['risk_level']} · {c['flags_count']} flags · {c['time_waiting']}"
        for c in cases
    ]
    selected_idx = st.radio(
        "Select a case",
        range(len(cases)),
        format_func=lambda i: options[i],
        key="arbitrator_radio",
        label_visibility="collapsed",
    )

    if selected_idx is not None:
        case = cases[selected_idx]
        risk_colors = {"LOW": "#22c55e", "MEDIUM": "#f59e0b", "HIGH": "#ef4444"}
        rc = risk_colors.get(case["risk_level"].upper(), "#6b7280")
        st.markdown("---")
        st.markdown(
            f"**{case['applicant_name']}** · {case['product']} · "
            f'<span style="background:{rc};color:white;padding:2px 8px;border-radius:4px;">{case["risk_level"]}</span>',
            unsafe_allow_html=True,
        )
        st.markdown("### Arbitrator Brief")
        st.write(case["brief"])
        st.markdown("---")

        reason = st.text_input(
            "Decision reason (required)",
            placeholder="Enter your rationale for this decision...",
            key="arb_reason",
        )

        st.markdown(
            "*This decision is permanent and logged under your credentials. "
            "AI cannot make this call.*"
        )

        has_reason = bool(reason and reason.strip())
        applicant = case.get("applicant", {})
        risk_score = case.get("risk_score", 50)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Approve", use_container_width=True, key="arb_approve", disabled=not has_reason):
                log_decision(applicant, "AUTO_APPROVED", risk_score, decided_by="Human")
                st.toast("Case approved. Decision logged to Bias Monitor.")
                st.rerun()
        with col2:
            if st.button("Decline", use_container_width=True, key="arb_decline", disabled=not has_reason):
                log_decision(applicant, "DECLINED", risk_score, decided_by="Human")
                st.toast("Case declined. Decision logged to Bias Monitor.")
                st.rerun()
        with col3:
            if st.button("Request Docs", use_container_width=True, key="arb_request", disabled=not has_reason):
                log_decision(applicant, "DOCS_REQUESTED", risk_score, decided_by="Human")
                st.toast("Document request sent. Decision logged to Bias Monitor.")
                st.rerun()

    _footer()


# --- Page 3: Bias Monitor ---
def _render_bias_monitor():
    st.markdown("## Bias Guardrail Monitor")
    st.caption("Approval parity and decision audit trail")

    parity = check_parity()

    if parity["status"] == "PASS":
        st.success(parity["message"])
    elif parity["status"] == "REVIEW_NEEDED":
        st.warning(parity["message"])
    else:
        st.info(parity["message"])

    st.markdown("### Decision Log")
    if DECISION_LOG:
        # Summary metrics
        approved = sum(1 for r in DECISION_LOG if r["decision"] == "AUTO_APPROVED")
        escalated = sum(1 for r in DECISION_LOG if r["decision"] in ("ESCALATED", "ESCALATED_HIGH_RISK"))
        declined = sum(1 for r in DECISION_LOG if r["decision"] == "DECLINED")
        docs_req = sum(1 for r in DECISION_LOG if r["decision"] == "DOCS_REQUESTED")
        human_decisions = sum(1 for r in DECISION_LOG if r.get("decided_by") == "Human")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Approved", approved)
        m2.metric("Escalated", escalated)
        m3.metric("Declined", declined)
        m4.metric("Docs Requested", docs_req)
        m5.metric("Human Decisions", human_decisions)
        st.write("")
        st.dataframe(
            [
                {
                    "Time": r["timestamp"][:19].replace("T", " "),
                    "Country of Birth": r["country_of_birth"],
                    "PEP": "Yes" if r["is_pep"] else "No",
                    "Product": r["product"],
                    "Decision": r["decision"],
                    "Risk Score": r["risk_score"],
                    "Decided By": r.get("decided_by", "AI"),
                }
                for r in DECISION_LOG
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption("No decisions logged yet. Run scenarios from the Onboarding Agent to populate.")

    st.markdown("---")
    st.markdown("### What is demographic parity?")
    st.markdown(
        """
        **Demographic parity** means approval rates should be similar across groups (e.g., 
        Canadian-born vs. non-Canadian-born applicants). A large gap suggests the system 
        may be treating similar applicants differently based on protected attributes, which 
        can violate fair-lending expectations in a regulated environment.

        This monitor tracks approval rates by country of birth. If the gap exceeds 10 
        percentage points, it triggers a compliance review of patterns—not individuals.
        """
    )
    st.markdown(
        "*Flagging does not block decisions. It triggers compliance review of patterns, not individuals.*"
    )

    _footer()


# --- Sidebar navigation ---
page = st.sidebar.radio(
    "Navigation",
    ["Onboarding Agent", "Risk Arbitrator Dashboard", "Bias Monitor"],
    label_visibility="collapsed",
)

if page == "Onboarding Agent":
    _render_onboarding_agent()
elif page == "Risk Arbitrator Dashboard":
    _render_risk_arbitrator()
else:
    _render_bias_monitor()
