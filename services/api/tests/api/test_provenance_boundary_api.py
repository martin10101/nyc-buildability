"""Task M2-T018 AS-1 at the WIRE: an undocumented provenance key can never
produce a 200.

``tests/profile/test_provenance_write_boundary.py`` proves the builder fails
closed. This file proves the consequence the contract actually cares about:
the property route serves a typed 500 with a correlation id instead of a
profile whose provenance quietly carries (or quietly lost) an undocumented
key. The rejected key and its value never appear in the response body.

Offline and deterministic: the route's connector dependency is overridden with
a fetcher bound to the accepted M1-T002 fixture capture, exactly as
tests/api/test_properties_v1.py does. No test touches the network.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.v1.properties import get_pluto_fetcher
from app.connectors.pluto_soda import TransportResponse, fetch_by_bbl
from app.main import app

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "pluto"
FIXED_CLOCK = lambda: datetime(2026, 7, 16, 12, 0, 0, tzinfo=UTC)  # noqa: E731
BBL = "1000010100"
LEAKED_VALUE = "Traceback: token=SUPER_SECRET_abc123 at line 42"  # noqa: S105


@pytest.fixture()
def raw_client():
    """Surfaces server exceptions as real HTTP responses, so the assertions
    below describe the WIRE contract rather than the test harness."""
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _fixture_result(bbl: str, correlation_id: str):
    fixture = json.loads(
        (FIXTURE_DIR / "F01_single_lot_normal.json").read_text(encoding="utf-8")
    )
    responses = [
        TransportResponse(
            status=fixture["http_status"], body=fixture["response_body_raw"]
        )
    ]

    def transport(url: str, headers: dict, timeout: float) -> TransportResponse:
        return responses.pop(0)

    return fetch_by_bbl(
        bbl,
        transport=transport,
        sleep=lambda seconds: None,
        clock=FIXED_CLOCK,
        correlation_id=correlation_id,
    )


def _install_fetcher(mutate_facts=None) -> None:
    def fetcher(bbl: str, correlation_id: str):
        result = _fixture_result(bbl, correlation_id)
        if mutate_facts is not None:
            mutate_facts(result.facts)
        return result

    app.dependency_overrides[get_pluto_fetcher] = lambda: fetcher


def test_clean_official_capture_still_serves_200(raw_client) -> None:
    """Control: the wired boundary does not disturb the happy path."""
    _install_fetcher()
    response = raw_client.get(f"/api/v1/properties/{BBL}")
    assert response.status_code == 200
    assert response.json()["provenance"]


def test_undocumented_provenance_key_yields_a_typed_500_never_a_200(
    raw_client,
) -> None:
    def inject(facts: list[dict]) -> None:
        facts[0]["_debug_stacktrace"] = LEAKED_VALUE

    _install_fetcher(inject)
    response = raw_client.get(f"/api/v1/properties/{BBL}")

    assert response.status_code == 500
    body = response.json()
    # A typed, machine-readable state with the correlation id - not a stack
    # trace, and emphatically not a profile.
    assert body["state"] == "internal_error"
    assert body["correlation_id"]
    assert response.headers["X-Correlation-ID"]
    assert "provenance" not in body

    # Diagnostic-leak safety end to end: neither the rejected key nor its
    # value reaches the client.
    raw = response.text
    assert "_debug_stacktrace" not in raw
    assert "SUPER_SECRET" not in raw
    assert LEAKED_VALUE not in raw


def test_missing_required_provenance_field_yields_a_typed_500(raw_client) -> None:
    def drop_required(facts: list[dict]) -> None:
        del facts[0]["conflict_status"]

    _install_fetcher(drop_required)
    response = raw_client.get(f"/api/v1/properties/{BBL}")
    assert response.status_code == 500
    assert response.json()["state"] == "internal_error"
