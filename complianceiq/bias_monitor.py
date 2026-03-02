"""
ComplianceIQ bias guardrail monitor.
Runs silently in the background—does not block decisions.
Flags approval-rate parity patterns for human review.
Decisions are persisted to decision_log.json.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Union

# Allow tests to override via env var for isolation
_LOG_FILE = Path(
    os.environ.get("COMPLIANCEIQ_DECISION_LOG_PATH")
    or str(Path(__file__).parent / "decision_log.json")
)


def _load_log() -> list:
    """Load DECISION_LOG from file. Returns empty list if file missing or invalid."""
    if not _LOG_FILE.exists():
        return []
    try:
        with open(_LOG_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_log(log: list) -> None:
    """Persist DECISION_LOG to file. Silently fails on OSError—monitor does not block workflow."""
    try:
        with open(_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2)
    except (OSError, TypeError) as _:
        pass  # Silently fail—monitor does not block workflow


# Persisted log—load from file on startup
DECISION_LOG: list = _load_log()


def log_decision(
    applicant_data: dict,
    decision: str,
    risk_score: Union[int, float],
    decided_by: str = "AI",
) -> None:
    """
    Appends a decision record to DECISION_LOG.
    Extracts country_of_birth, is_pep, and product from applicant_data.

    Does not block or raise—runs silently. Handles None/malformed applicant_data.

    Args:
        applicant_data: Applicant dict (from scenario)
        decision: One of AUTO_APPROVED, ESCALATED, ESCALATED_HIGH_RISK, DECLINED, DOCS_REQUESTED
        risk_score: Numeric risk score
        decided_by: "AI" or "Human" — who made the final decision
    """
    if not isinstance(applicant_data, dict):
        applicant_data = {}
    # Use birth_country when available; some applicants omit it
    country_of_birth = applicant_data.get("birth_country") or applicant_data.get(
        "nationality", "Unknown"
    )
    is_pep = applicant_data.get("pep_indicator", False)
    product = applicant_data.get("application_type", "Unknown")

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "country_of_birth": country_of_birth,
        "is_pep": is_pep,
        "product": product,
        "decision": decision,
        "risk_score": risk_score,
        "decided_by": decided_by,
    }
    DECISION_LOG.append(record)
    _save_log(DECISION_LOG)


def check_parity() -> dict:
    """
    Compares approval rates: Canadian-born vs non-Canadian-born.
    Returns status and message. Does not block any workflow.
    """
    if len(DECISION_LOG) < 3:
        return {
            "status": "INSUFFICIENT_DATA",
            "gap": None,
            "message": "Fewer than 3 decisions logged. Parity check requires more data.",
        }

    # Treat Canada/Canadian as Canadian-born; all else as non-Canadian-born
    canadian_born = [r for r in DECISION_LOG if r["country_of_birth"] in ("Canada", "Canadian")]
    non_canadian_born = [
        r for r in DECISION_LOG if r["country_of_birth"] not in ("Canada", "Canadian", "Unknown")
    ]

    # Exclude "Unknown" from parity—we need known birth country
    if not canadian_born or not non_canadian_born:
        return {
            "status": "INSUFFICIENT_DATA",
            "gap": None,
            "message": "Need decisions from both Canadian-born and non-Canadian-born applicants.",
        }

    def approval_rate(records: list) -> float:
        approved = sum(1 for r in records if r["decision"] == "AUTO_APPROVED")
        return (approved / len(records)) * 100 if records else 0.0

    rate_canadian = approval_rate(canadian_born)
    rate_non_canadian = approval_rate(non_canadian_born)
    gap = abs(rate_canadian - rate_non_canadian)

    if gap > 10:
        return {
            "status": "REVIEW_NEEDED",
            "gap": round(gap, 1),
            "message": (
                f"Approval rate divergence detected: Canadian-born {rate_canadian:.1f}% vs "
                f"non-Canadian-born {rate_non_canadian:.1f}% (gap {gap:.1f}pp). "
                "Review for potential bias."
            ),
        }

    return {
        "status": "PASS",
        "gap": round(gap, 1),
        "message": f"Parity within acceptable range (gap {gap:.1f}pp).",
    }
