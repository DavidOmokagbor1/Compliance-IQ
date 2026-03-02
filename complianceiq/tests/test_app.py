"""Unit tests for app.py helpers — sample ID generation."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from app import _sample_government_id


def test_sample_government_id_returns_image():
    """_sample_government_id should return a PIL Image."""
    from PIL import Image

    applicant = {
        "full_name": "Test User",
        "date_of_birth": "1990-01-01",
        "address": {"city": "Toronto", "province": "Ontario"},
        "id_document": {"type": "Ontario Driver's License", "number": "X123", "expiry_date": "2028-01-01"},
        "id_photo": "male",
    }
    img = _sample_government_id(applicant)
    assert isinstance(img, Image.Image)
    assert img.size == (340, 216)


def test_sample_government_id_handles_missing_address():
    """_sample_government_id should not raise when address is None."""
    applicant = {
        "full_name": "Test User",
        "date_of_birth": "1990-01-01",
        "address": None,
        "id_document": {},
        "id_photo": "female",
    }
    img = _sample_government_id(applicant)
    assert img is not None


def test_sample_government_id_handles_minimal_applicant():
    """_sample_government_id should work with minimal applicant dict."""
    img = _sample_government_id({})
    assert img is not None
