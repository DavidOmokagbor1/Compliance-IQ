"""Unit tests for mock_data.py — scenario structure validation."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from mock_data import SCENARIOS


def test_scenarios_not_empty():
    """SCENARIOS should contain at least one scenario."""
    assert len(SCENARIOS) >= 1


def test_each_scenario_has_required_keys():
    """Each scenario must have name, applicant, extraction_confidence, expected_outcome."""
    required = {"name", "applicant", "extraction_confidence", "expected_outcome"}
    for key, scenario in SCENARIOS.items():
        assert isinstance(key, str), f"Scenario key {key} should be string"
        for r in required:
            assert r in scenario, f"Scenario {key} missing {r}"


def test_applicant_has_required_fields():
    """Each applicant must have full_name, date_of_birth, application_type."""
    required = {"full_name", "date_of_birth", "application_type"}
    for key, scenario in SCENARIOS.items():
        applicant = scenario.get("applicant", {})
        for r in required:
            assert r in applicant, f"Applicant in {key} missing {r}"


def test_expected_outcome_valid():
    """expected_outcome must be one of allowed values."""
    allowed = {"AUTO_APPROVED", "ESCALATED", "ESCALATED_HIGH_RISK"}
    for key, scenario in SCENARIOS.items():
        outcome = scenario.get("expected_outcome")
        assert outcome in allowed, f"Scenario {key} has invalid expected_outcome: {outcome}"


def test_extraction_confidence_in_range():
    """extraction_confidence should be between 0 and 1."""
    for key, scenario in SCENARIOS.items():
        conf = scenario.get("extraction_confidence")
        assert 0 <= conf <= 1, f"Scenario {key} extraction_confidence {conf} out of range"
