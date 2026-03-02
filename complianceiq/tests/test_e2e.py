"""End-to-end tests — Streamlit app UI flows."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

# Skip if streamlit testing not available
try:
    from streamlit.testing.v1 import AppTest
    HAS_APP_TEST = True
except ImportError:
    HAS_APP_TEST = False


@pytest.mark.skipif(not HAS_APP_TEST, reason="Streamlit AppTest not available")
def test_app_loads():
    """App should load without error and render main elements."""
    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path))
    at.run()

    assert len(at.markdown) > 0
    assert any("ComplianceIQ" in str(getattr(m, "value", "")) for m in at.markdown)


@pytest.mark.skipif(not HAS_APP_TEST, reason="Streamlit AppTest not available")
def test_scenario_selectbox_present():
    """Scenario selectbox should be present on Onboarding Agent page."""
    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path))
    at.run()

    assert len(at.selectbox) >= 1


@pytest.mark.skipif(not HAS_APP_TEST, reason="Streamlit AppTest not available")
def test_submit_button_present():
    """Submit Application button should be present."""
    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path))
    at.run()

    buttons = [b for b in at.button if "Submit" in (getattr(b, "label", "") or "")]
    assert len(buttons) >= 1
