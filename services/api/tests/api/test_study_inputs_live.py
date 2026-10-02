"""Offline proof of the LIVE study-inputs wiring (lane C, request D-1 slice 2).

Slice 2 binds the route's DEFAULT provider to the resilient PLUTO fetcher the
properties route uses (NB1). These tests prove that wiring WITHOUT any network:

- :func:`default_study_inputs_provider` delegates to
  ``app.api.v1.properties.get_pluto_fetcher`` (the resilient-fetcher seam), so a
  real request reaches PLUTO through the connector-resilience layer;
- a success flows through a REAL ``ResilientPlutoFetcher`` with an INJECTED
  transport (the same fixture-transport seam the connector suite uses), so the
  TTL cache / breaker / retry wrapper is exercised, not bypassed;
- every upstream failure maps to the typed ``StudyInputsUnavailableError`` the
  route turns into a 503;
- a no-match is mapped DISTINCTLY: a condo unit-lot gets ``reason="condo"``, a
  plain no-match ``reason="no_match"``;
- an optional ``selected`` re-pick is threaded VERBATIM to B-07's derive, and a
  BBL B-07 does not recognise raises :class:`LotSelectionError`.

No live calls: every fetch is driven by an injected transport over the recorded
215-16 Northern pack or a synthetic empty/failing response.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

import app.api.v1.properties as properties
import app.api.v1.study_inputs as study_inputs
from app.api.v1.study_inputs import (
    StudyInputsUnavailableError,
    default_study_inputs_provider,
    pluto_study_inputs_provider,
)
from app.connectors.pluto_soda import TransportResponse, fetch_by_bbl
from app.resilience.fetcher import ResilientPlutoFetcher
from app.spatial.multi_lot_site import LotSelectionError

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "benchmark_215_16_northern"
NORTHERN_BBL = "4073340070"
FIXED_CLOCK = lambda: datetime(2026, 9, 30, 12, 0, 0, tzinfo=UTC)  # noqa: E731
LANE_B_ON = {"LANE_B_ENABLED": "1"}


def _northern_body() -> str:
    return (FIXTURE_DIR / "pluto_64uk-42ks_bbl_4073340070.json").read_text(encoding="utf-8")


def _transport_for(body: str, status: int = 200):
    return lambda url, headers, timeout: TransportResponse(status, body)


def _fetcher_over(body: str, status: int = 200):
    """A plain PLUTO fetcher over a fixed transport (no resilience wrapper)."""

    def fetcher(bbl: str, correlation_id: str):
        return fetch_by_bbl(
            bbl,
            transport=_transport_for(body, status),
            sleep=lambda seconds: None,
            clock=FIXED_CLOCK,
            correlation_id=correlation_id,
        )

    return fetcher


def _resilient_fetcher_over(body: str, status: int = 200) -> ResilientPlutoFetcher:
    """A REAL resilient fetcher with the transport injected (offline), so the
    live path's cache/breaker/retry wrapper is actually exercised."""
    return ResilientPlutoFetcher(
        sleep=lambda seconds: None,
        wall_clock=FIXED_CLOCK,
        fetch_kwargs={
            "transport": _transport_for(body, status),
            "sleep": lambda seconds: None,
            "clock": FIXED_CLOCK,
        },
    )


# ---------------------------------------------------------------------------
# The default provider is bound to the properties resilient-fetcher seam (NB1).
# ---------------------------------------------------------------------------
def test_default_provider_delegates_to_properties_get_pluto_fetcher(monkeypatch) -> None:
    monkeypatch.setenv("LANE_B_ENABLED", "1")
    # Stand in for the live resilient fetcher with the recorded pack (offline),
    # and prove the default provider reaches it through properties.get_pluto_fetcher.
    monkeypatch.setattr(properties, "get_pluto_fetcher", lambda: _fetcher_over(_northern_body()))
    study_inputs._live_study_inputs_provider.cache_clear()
    try:
        inputs = default_study_inputs_provider(NORTHERN_BBL, "cid-live")
    finally:
        study_inputs._live_study_inputs_provider.cache_clear()
    assert inputs.site is not None
    assert inputs.lot_choice is not None
    assert [lot.bbl for lot in inputs.site.lots] == [NORTHERN_BBL]


def test_default_provider_is_cached_once(monkeypatch) -> None:
    """The live provider is built once (lru_cache), so the process-wide resilient
    fetcher's cache/breaker/LKG state is shared across requests."""
    study_inputs._live_study_inputs_provider.cache_clear()
    try:
        first = study_inputs._live_study_inputs_provider()
        second = study_inputs._live_study_inputs_provider()
    finally:
        study_inputs._live_study_inputs_provider.cache_clear()
    assert first is second


# ---------------------------------------------------------------------------
# Success through a REAL resilient fetcher with an injected transport (offline).
# ---------------------------------------------------------------------------
def test_live_success_through_the_resilient_fetcher(monkeypatch) -> None:
    monkeypatch.setenv("LANE_B_ENABLED", "1")
    provider = pluto_study_inputs_provider(
        _resilient_fetcher_over(_northern_body()), clock=FIXED_CLOCK, env=LANE_B_ON
    )
    inputs = provider(NORTHERN_BBL, "cid-ok")
    assert [lot.bbl for lot in inputs.site.lots] == [NORTHERN_BBL]
    assert inputs.site_facts  # B-02 facts carried verbatim


# ---------------------------------------------------------------------------
# Every upstream failure maps to the typed 503 (StudyInputsUnavailableError).
# ---------------------------------------------------------------------------
_CONNECTOR_ERROR_TYPES = frozenset(
    {"source_unavailable", "rate_limited", "timeout", "schema_drift"}
)


def test_upstream_failure_through_resilient_fetcher_is_unavailable() -> None:
    provider = pluto_study_inputs_provider(
        _resilient_fetcher_over("server error", status=500), env=LANE_B_ON
    )
    with pytest.raises(StudyInputsUnavailableError) as excinfo:
        provider(NORTHERN_BBL, "cid-down")
    assert excinfo.value.reason in _CONNECTOR_ERROR_TYPES


# ---------------------------------------------------------------------------
# No-match is mapped DISTINCTLY: condo unit-lot vs plain no-match.
# ---------------------------------------------------------------------------
def test_plain_no_match_maps_to_no_match_reason() -> None:
    # Lot 0070 is outside the condo unit-lot range -> a plain no-match.
    provider = pluto_study_inputs_provider(_fetcher_over("[]"), env=LANE_B_ON)
    with pytest.raises(StudyInputsUnavailableError) as excinfo:
        provider("1000010070", "cid-nomatch")
    assert excinfo.value.reason == "no_match"


def test_condo_unit_lot_no_match_maps_to_condo_reason() -> None:
    # Lot 1001 is in the condo unit-lot range (1001-6999): resolve the billing BBL.
    provider = pluto_study_inputs_provider(_fetcher_over("[]"), env=LANE_B_ON)
    with pytest.raises(StudyInputsUnavailableError) as excinfo:
        provider("1000011001", "cid-condo")
    assert excinfo.value.reason == "condo"


# ---------------------------------------------------------------------------
# The re-pick `selected` is threaded VERBATIM to B-07's derive.
# ---------------------------------------------------------------------------
def test_selected_re_pick_is_passed_to_derive(monkeypatch) -> None:
    provider = pluto_study_inputs_provider(
        _fetcher_over(_northern_body()), clock=FIXED_CLOCK, env=LANE_B_ON
    )
    inputs = provider(NORTHERN_BBL, "cid-sel", selected=[NORTHERN_BBL])
    # The single entered lot, re-picked explicitly: B-07's selection verbatim.
    assert inputs.site.selected_bbls == (NORTHERN_BBL,)


def test_selected_unknown_lot_raises_lot_selection_error() -> None:
    provider = pluto_study_inputs_provider(
        _fetcher_over(_northern_body()), clock=FIXED_CLOCK, env=LANE_B_ON
    )
    with pytest.raises(LotSelectionError):
        provider(NORTHERN_BBL, "cid-bad", selected=["1000010001"])
