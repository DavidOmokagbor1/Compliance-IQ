"""Unit tests for agent.py — JSON extraction, structure, and error handling."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import AgentError, _extract_json_from_response, generate_arbitrator_brief, run_case_agent


def test_extract_json_raw():
    """Raw JSON without markdown should parse correctly."""
    text = '{"decision": "AUTO_APPROVED", "risk_score": 5}'
    result = _extract_json_from_response(text)
    assert result["decision"] == "AUTO_APPROVED"
    assert result["risk_score"] == 5


def test_extract_json_markdown_code_block():
    """JSON inside ```json ... ``` should be extracted."""
    text = '''Here is the result:
```json
{"decision": "ESCALATED", "risk_score": 42}
```
'''
    result = _extract_json_from_response(text)
    assert result["decision"] == "ESCALATED"
    assert result["risk_score"] == 42


def test_extract_json_code_block_no_lang():
    """JSON inside ``` ... ``` (no json tag) should be extracted."""
    text = '''
```
{"decision": "AUTO_APPROVED", "risk_score": 0}
```
'''
    result = _extract_json_from_response(text)
    assert result["decision"] == "AUTO_APPROVED"


def test_extract_json_empty_raises():
    """Empty or None input should raise ValueError."""
    with pytest.raises(ValueError, match="Empty"):
        _extract_json_from_response("")
    with pytest.raises(ValueError, match="Empty"):
        _extract_json_from_response("   ")


def test_extract_json_invalid_raises():
    """Invalid JSON should raise ValueError."""
    with pytest.raises(ValueError, match="invalid JSON"):
        _extract_json_from_response("not json at all")


def test_run_case_agent_empty_scenario_raises():
    """Empty scenario should raise AgentError."""
    with pytest.raises(AgentError, match="Scenario data is required"):
        run_case_agent({})
    with pytest.raises(AgentError, match="Scenario data is required"):
        run_case_agent(None)


@patch("agent.OpenAI")
def test_run_case_agent_success(mock_openai):
    """run_case_agent returns parsed JSON when OpenAI responds correctly."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"decision": "AUTO_APPROVED", "risk_score": 5}'
    mock_openai.return_value.chat.completions.create.return_value = mock_response

    result = run_case_agent({"applicant": {"full_name": "Test"}})
    assert result["decision"] == "AUTO_APPROVED"
    assert result["risk_score"] == 5


@patch("agent.OpenAI")
def test_run_case_agent_invalid_json_raises(mock_openai):
    """run_case_agent raises AgentError when response is invalid JSON."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "not valid json"
    mock_openai.return_value.chat.completions.create.return_value = mock_response

    with pytest.raises(AgentError, match="invalid JSON"):
        run_case_agent({"applicant": {"full_name": "Test"}})


@patch("agent.OpenAI")
def test_run_case_agent_api_error_raises_agent_error(mock_openai):
    """run_case_agent raises AgentError when OpenAI API raises."""
    mock_openai.return_value.chat.completions.create.side_effect = Exception("Network error")

    with pytest.raises(AgentError, match="Unexpected error"):
        run_case_agent({"applicant": {"full_name": "Test"}})


@patch("agent.OpenAI")
def test_generate_arbitrator_brief_success(mock_openai):
    """generate_arbitrator_brief returns brief string."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "This is a brief for the arbitrator."
    mock_openai.return_value.chat.completions.create.return_value = mock_response

    result = generate_arbitrator_brief(
        {"applicant": {"full_name": "Test"}},
        {"decision": "ESCALATED", "reasoning": "Risk flags."},
    )
    assert "brief" in result.lower() or "arbitrator" in result.lower() or len(result) > 0
