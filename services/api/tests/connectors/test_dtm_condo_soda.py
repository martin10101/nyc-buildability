"""Placeholder suite for the DTM condo resolver (M5-T042); the producer replaces it."""

from app.connectors import dtm_condo_soda


def test_placeholder_module_present() -> None:
    assert "billing-BBL" in (dtm_condo_soda.__doc__ or "")
