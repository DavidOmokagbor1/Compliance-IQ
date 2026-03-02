"""
ComplianceIQ autonomous KYC case agent.
Handles case assessment and Risk Arbitrator brief generation via OpenAI API.
"""

import json
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import APIError, AuthenticationError, OpenAI, RateLimitError

# Load .env from this module's directory (ensures .env is found regardless of CWD)
load_dotenv(Path(__file__).parent / ".env")


class AgentError(Exception):
    """Raised when the agent fails (API, validation, or network)."""

    def __init__(self, message: str, cause: Exception | None = None):
        super().__init__(message)
        self.cause = cause


def _extract_json_from_response(text: str) -> dict:
    """
    Safely extract JSON from the model's response.
    Handles markdown code blocks (```json ... ``` or ``` ... ```).
    """
    text = (text or "").strip()
    if not text:
        raise ValueError("Empty response cannot be parsed as JSON.")

    # Try to extract from markdown code block
    code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if code_block_match:
        text = code_block_match.group(1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model returned invalid JSON: {e}") from e


def run_case_agent(scenario_data: dict) -> dict:
    """
    Runs the autonomous KYC agent on a scenario.
    Calls OpenAI to assess the case and return a structured decision.

    Args:
        scenario_data: A scenario dict from mock_data.SCENARIOS (includes
                       name, applicant, extraction_confidence, expected_outcome)

    Returns:
        Parsed dict with: decision, risk_level, risk_score, processing_time_seconds,
        flags, reasoning, fintrac_reference, agent_recommendation,
        bias_check, bias_note

    Raises:
        AgentError: On API/auth/rate-limit/network or validation failure.
    """
    if not scenario_data:
        raise AgentError("Scenario data is required", cause=None)

    try:
        client = OpenAI()
    except Exception as e:
        raise AgentError(f"Failed to initialize OpenAI client: {e}", cause=e) from e

    system_prompt = """You are ComplianceIQ's autonomous KYC agent for Wealthsimple.
You are regulated under FINTRAC (Financial Transactions and Reports Analysis Centre of Canada).
Assess each applicant case for compliance risk. Be thorough but fair.
Return ONLY valid JSON—no other text before or after."""

    user_message = (
        "Assess this KYC applicant. Return ONLY valid JSON with exactly these fields:\n"
        "- decision (one of: AUTO_APPROVED, ESCALATED, ESCALATED_HIGH_RISK)\n"
        "- risk_level (one of: LOW, MEDIUM, HIGH)\n"
        "- risk_score (integer 0-100)\n"
        "- processing_time_seconds (float)\n"
        "- flags (list of strings)\n"
        "- reasoning (string)\n"
        "- fintrac_reference (string or null)\n"
        "- agent_recommendation (string)\n"
        "- bias_check (one of: PASS, REVIEW_NEEDED)\n"
        "- bias_note (string)\n\n"
        f"Applicant data:\n{json.dumps(scenario_data, indent=2)}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=1024,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
    except AuthenticationError as e:
        raise AgentError("Invalid or missing OpenAI API key. Check .env OPENAI_API_KEY.", cause=e) from e
    except RateLimitError as e:
        raise AgentError("OpenAI rate limit exceeded. Please try again shortly.", cause=e) from e
    except APIError as e:
        raise AgentError(f"OpenAI API error: {e}", cause=e) from e
    except Exception as e:
        raise AgentError(f"Unexpected error calling OpenAI: {e}", cause=e) from e

    response_text = response.choices[0].message.content
    if not response_text:
        raise AgentError("OpenAI returned empty response. Check model/API limits.", cause=None)

    try:
        return _extract_json_from_response(response_text)
    except ValueError as e:
        raise AgentError(f"Agent returned invalid JSON: {e}", cause=e) from e


def generate_arbitrator_brief(scenario_data: dict, agent_result: dict) -> str:
    """
    Generates a plain-language brief for the human Risk Arbitrator.
    Explains the case, the agent's decision, and what the human must decide.

    Args:
        scenario_data: The scenario dict from mock_data.SCENARIOS
        agent_result: The parsed result from run_case_agent()

    Returns:
        A brief string, under 200 words, for the human arbitrator.
    """
    client = OpenAI()

    system_prompt = """You write Risk Arbitrator briefs for ComplianceIQ.
Use plain language. Be direct and concise. Under 200 words.
The brief must tell the human exactly: (1) what case they're reviewing,
(2) what the agent recommended and why, (3) what single decision they need to make."""

    user_message = (
        "Write a Risk Arbitrator brief for this case.\n\n"
        f"Scenario: {json.dumps(scenario_data, indent=2)}\n\n"
        f"Agent result: {json.dumps(agent_result, indent=2)}\n\n"
        "Output the brief only—no labels, no preamble."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=512,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
    except AuthenticationError as e:
        raise AgentError("Invalid or missing OpenAI API key. Check .env OPENAI_API_KEY.", cause=e) from e
    except RateLimitError as e:
        raise AgentError("OpenAI rate limit exceeded. Please try again shortly.", cause=e) from e
    except APIError as e:
        raise AgentError(f"OpenAI API error: {e}", cause=e) from e
    except Exception as e:
        raise AgentError(f"Unexpected error calling OpenAI: {e}", cause=e) from e

    content = response.choices[0].message.content
    if not content:
        raise AgentError("OpenAI returned empty brief. Check model/API limits.", cause=None)
    return content.strip()
