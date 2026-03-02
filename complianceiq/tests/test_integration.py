"""Integration tests — agent + bias_monitor flow."""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import run_case_agent
from bias_monitor import check_parity, log_decision
from mock_data import SCENARIOS


@pytest.fixture
def temp_log():
    """Provide a temporary decision log file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("[]")
        log_path = f.name
    yield log_path
    Path(log_path).unlink(missing_ok=True)


def test_agent_result_logged_to_bias_monitor(temp_log):
    """When agent runs, log_decision should persist to bias monitor."""
    os.environ["COMPLIANCEIQ_DECISION_LOG_PATH"] = temp_log
    from importlib import reload
    import bias_monitor
    reload(bias_monitor)

    applicant = SCENARIOS["A"]["applicant"]
    log_decision(applicant, "AUTO_APPROVED", 5)

    with open(temp_log) as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["decision"] == "AUTO_APPROVED"
    assert data[0]["risk_score"] == 5

    del os.environ["COMPLIANCEIQ_DECISION_LOG_PATH"]


@patch("agent.OpenAI")
def test_run_agent_then_log_then_check_parity(mock_openai, temp_log):
    """Full flow: run agent (mocked) -> log -> check parity."""
    os.environ["COMPLIANCEIQ_DECISION_LOG_PATH"] = temp_log

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "decision": "AUTO_APPROVED",
        "risk_level": "LOW",
        "risk_score": 10,
        "processing_time_seconds": 1.5,
        "flags": [],
        "reasoning": "Clean case",
        "fintrac_reference": None,
        "agent_recommendation": "Approve",
        "bias_check": "PASS",
        "bias_note": "",
    })
    mock_openai.return_value.chat.completions.create.return_value = mock_response

    from importlib import reload
    import bias_monitor
    reload(bias_monitor)

    scenario = SCENARIOS["A"]
    agent_result = run_case_agent(scenario)
    log_decision(scenario["applicant"], agent_result["decision"], agent_result["risk_score"])

    parity = check_parity()
    assert parity["status"] in ("INSUFFICIENT_DATA", "PASS", "REVIEW_NEEDED")

    del os.environ["COMPLIANCEIQ_DECISION_LOG_PATH"]
