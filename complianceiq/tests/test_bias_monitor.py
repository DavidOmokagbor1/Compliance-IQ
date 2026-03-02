"""Unit tests for bias_monitor.py — parity logic and logging."""

import json
import os
import tempfile
import pytest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_check_parity_insufficient_data():
    """Fewer than 3 decisions should return INSUFFICIENT_DATA."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("[]")
        log_path = f.name

    try:
        os.environ["COMPLIANCEIQ_DECISION_LOG_PATH"] = log_path
        from importlib import reload
        import bias_monitor
        reload(bias_monitor)

        result = bias_monitor.check_parity()
        assert result["status"] == "INSUFFICIENT_DATA"
        assert result["gap"] is None
    finally:
        del os.environ["COMPLIANCEIQ_DECISION_LOG_PATH"]
        Path(log_path).unlink(missing_ok=True)


def test_check_parity_review_needed():
    """When gap > 10, status should be REVIEW_NEEDED."""
    log_data = [
        {"country_of_birth": "Canadian", "decision": "AUTO_APPROVED", "risk_score": 5, "is_pep": False, "product": "TFSA", "timestamp": "2026-01-01T00:00:00+00:00"},
        {"country_of_birth": "Canadian", "decision": "AUTO_APPROVED", "risk_score": 10, "is_pep": False, "product": "RRSP", "timestamp": "2026-01-01T00:00:00+00:00"},
        {"country_of_birth": "Russia", "decision": "ESCALATED", "risk_score": 60, "is_pep": False, "product": "TFSA", "timestamp": "2026-01-01T00:00:00+00:00"},
        {"country_of_birth": "Russia", "decision": "ESCALATED", "risk_score": 70, "is_pep": True, "product": "RRSP", "timestamp": "2026-01-01T00:00:00+00:00"},
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(log_data, f)
        log_path = f.name

    try:
        os.environ["COMPLIANCEIQ_DECISION_LOG_PATH"] = log_path
        from importlib import reload
        import bias_monitor
        reload(bias_monitor)

        result = bias_monitor.check_parity()
        # Canadian: 100% approved, Russia: 0% approved, gap = 100
        assert result["status"] == "REVIEW_NEEDED"
        assert result["gap"] == 100.0
    finally:
        del os.environ["COMPLIANCEIQ_DECISION_LOG_PATH"]
        Path(log_path).unlink(missing_ok=True)


def test_check_parity_pass():
    """When gap <= 10, status should be PASS."""
    # Canadian 100%, Russia 100% → gap 0
    log_data = [
        {"country_of_birth": "Canadian", "decision": "AUTO_APPROVED", "risk_score": 5, "is_pep": False, "product": "TFSA", "timestamp": "2026-01-01T00:00:00+00:00"},
        {"country_of_birth": "Canadian", "decision": "AUTO_APPROVED", "risk_score": 10, "is_pep": False, "product": "RRSP", "timestamp": "2026-01-01T00:00:00+00:00"},
        {"country_of_birth": "Russia", "decision": "AUTO_APPROVED", "risk_score": 15, "is_pep": False, "product": "TFSA", "timestamp": "2026-01-01T00:00:00+00:00"},
        {"country_of_birth": "Russia", "decision": "AUTO_APPROVED", "risk_score": 20, "is_pep": True, "product": "RRSP", "timestamp": "2026-01-01T00:00:00+00:00"},
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(log_data, f)
        log_path = f.name

    try:
        os.environ["COMPLIANCEIQ_DECISION_LOG_PATH"] = log_path
        from importlib import reload
        import bias_monitor
        reload(bias_monitor)

        result = bias_monitor.check_parity()
        # Canadian: 100%, Russia: 50%, gap = 50... wait that's > 10. Let me fix.
        # For PASS we need gap <= 10. Canadian 100%, Russia 90% = gap 10. Or 75% vs 75% = 0.
        # 2 Canadian both approved, 2 Russian both approved = 100% vs 100% = 0 gap.
        assert result["status"] == "PASS"
        assert result["gap"] == 0.0
    finally:
        del os.environ["COMPLIANCEIQ_DECISION_LOG_PATH"]
        Path(log_path).unlink(missing_ok=True)


def test_log_decision_appends_and_persists():
    """log_decision should append record and persist to file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("[]")
        log_path = f.name

    try:
        os.environ["COMPLIANCEIQ_DECISION_LOG_PATH"] = log_path
        from importlib import reload
        import bias_monitor
        reload(bias_monitor)

        applicant = {"birth_country": "Canada", "pep_indicator": False, "application_type": "TFSA"}
        bias_monitor.log_decision(applicant, "AUTO_APPROVED", 10)

        assert len(bias_monitor.DECISION_LOG) == 1
        r = bias_monitor.DECISION_LOG[0]
        assert r["country_of_birth"] == "Canada"
        assert r["decision"] == "AUTO_APPROVED"
        assert r["risk_score"] == 10

        with open(log_path) as f:
            persisted = json.load(f)
        assert len(persisted) == 1
    finally:
        del os.environ["COMPLIANCEIQ_DECISION_LOG_PATH"]
        Path(log_path).unlink(missing_ok=True)


def test_log_decision_handles_none_applicant():
    """log_decision should not raise when applicant_data is None or invalid."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("[]")
        log_path = f.name

    try:
        os.environ["COMPLIANCEIQ_DECISION_LOG_PATH"] = log_path
        from importlib import reload
        import bias_monitor
        reload(bias_monitor)

        bias_monitor.log_decision(None, "AUTO_APPROVED", 10)
        assert len(bias_monitor.DECISION_LOG) >= 1
        r = bias_monitor.DECISION_LOG[-1]
        assert r["country_of_birth"] == "Unknown"
        assert r["decision"] == "AUTO_APPROVED"
    finally:
        del os.environ["COMPLIANCEIQ_DECISION_LOG_PATH"]
        Path(log_path).unlink(missing_ok=True)


def test_load_log_handles_corrupt_file():
    """_load_log should return [] for corrupt/invalid JSON file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("not valid json {{{")
        log_path = f.name

    try:
        os.environ["COMPLIANCEIQ_DECISION_LOG_PATH"] = log_path
        from importlib import reload
        import bias_monitor
        reload(bias_monitor)

        assert isinstance(bias_monitor.DECISION_LOG, list)
        assert len(bias_monitor.DECISION_LOG) == 0
    finally:
        del os.environ["COMPLIANCEIQ_DECISION_LOG_PATH"]
        Path(log_path).unlink(missing_ok=True)
