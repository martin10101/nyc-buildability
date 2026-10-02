"""GET /api/v1/properties/{bbl}/transit-parking - internal transit/parking read
(lane C packet W3; plan check C-8, queue item B-10).

Offline and deterministic. The route is driven through its INJECTED provider
(``get_transit_parking_provider`` override), so no network is touched:

- the 200 path replays the RECORDED 215-16 Northern benchmark PLUTO body through
  the accepted connector + builder + ``resolve_transit_parking_status``, proving
  the ONE recorded Outer Transit Zone status is produced from recorded official
  data and carries the zone ONLY (no parking outcome);
- a check_needed path replays the SAME pack with the transitzone column omitted
  (SODA drops null fields), proving a missing value is "Check needed" naming the
  source to check, never a guess;
- the contract-guard path injects a status whose envelope fails the contract and
  proves the route refuses to ship it (500 ``internal_contract_error``), never a
  partial or invalid 200.

The router under test is now mounted in the app (packet W5, self-gated and
default off; the real-app mount is proven in ``tests/api/test_read_router_mounts.py``),
and this suite builds a LOCAL FastAPI app and includes the router directly to
isolate its offline provider injection. Every emitted (HTTP status, state) pair is
asserted to be in the route's single source of truth
``TRANSIT_PARKING_STATUS_STATE_MATRIX``, and the suite drives every pair in it
(exhaustive).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.transit_parking_read import (
    TRANSIT_PARKING_STATUS_STATE_MATRIX,
    TransitParkingUnavailableError,
    assemble_transit_parking_status,
    default_transit_parking_provider,
    get_rate_limiter,
    get_transit_parking_provider,
    pluto_transit_parking_provider,
    router,
)
from app.config import INTERNAL_TRANSIT_PARKING_READ_ENABLED_ENV_VAR
from app.connectors.pluto_soda import (
    SourceUnavailableError,
    TransportResponse,
    fetch_by_bbl,
)
from app.contracts.study_contracts import validate_transit_parking_document
from app.profile.transit_parking import TransitParkingStatus

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "benchmark_215_16_northern"
NORTHERN_BBL = "4073340070"
PLUTO_FILE = "pluto_64uk-42ks_bbl_4073340070.json"
FIXED_CLOCK = lambda: datetime(2026, 9, 30, 12, 0, 0, tzinfo=UTC)  # noqa: E731
LANE_B_ON = {"LANE_B_ENABLED": "1"}


def _northern_record() -> dict:
    """The one recorded 215-16 Northern PLUTO record (a fresh copy per call so a
    test that mutates it cannot corrupt the others)."""
    return json.loads((FIXTURE_DIR / PLUTO_FILE).read_text(encoding="utf-8"))[0]


def _fetcher_for(record: dict):
    """A PLUTO fetcher serving ``record`` offline through the accepted connector."""
    body = json.dumps([record])

    def fetcher(bbl: str, correlation_id: str):
        return fetch_by_bbl(
            bbl,
            transport=lambda url, headers, timeout: TransportResponse(200, body),
            sleep=lambda seconds: None,
            clock=FIXED_CLOCK,
            correlation_id=correlation_id,
        )

    return fetcher


def _northern_provider():
    """The recorded Outer Transit Zone status (status == recorded)."""
    return pluto_transit_parking_provider(
        _fetcher_for(_northern_record()), clock=FIXED_CLOCK, env=LANE_B_ON
    )


def _check_needed_provider():
    """The SAME pack with the transitzone column omitted -> check_needed."""
    record = _northern_record()
    assert record.pop("transitzone") == "Outer Transit Zone"  # SYNTHETIC: null omitted
    return pluto_transit_parking_provider(_fetcher_for(record), clock=FIXED_CLOCK, env=LANE_B_ON)


def _app(provider=None) -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    if provider is not None:
        app.dependency_overrides[get_transit_parking_provider] = lambda: provider
    return app


def _client(provider=None) -> TestClient:
    return TestClient(_app(provider))


def _enable(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_TRANSIT_PARKING_READ_ENABLED_ENV_VAR, "1")


def _url(bbl: str = NORTHERN_BBL) -> str:
    return f"/api/v1/properties/{bbl}/transit-parking"


def _assert_pair_documented(response) -> None:
    body = response.json()
    state = body.get("state") if isinstance(body, dict) else None
    assert (response.status_code, state) in TRANSIT_PARKING_STATUS_STATE_MATRIX, (
        response.status_code,
        state,
    )


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """The per-route limiter is MODULE-level state keyed by the shared TestClient
    host; reset its windows around every test so cases do not accumulate stamps
    into a spurious 429."""
    get_rate_limiter().reset()
    yield
    get_rate_limiter().reset()


def _unavailable_provider(reason: str = "no_match"):
    """An offline provider that fails safe (no network), for the typed-503 path."""

    def provider(bbl: str, correlation_id: str):
        raise TransitParkingUnavailableError("withheld (test)", reason=reason)

    return provider


# ---------------------------------------------------------------------------
# Flag gating
# ---------------------------------------------------------------------------
def test_flag_off_is_generic_404(monkeypatch) -> None:
    monkeypatch.delenv(INTERNAL_TRANSIT_PARKING_READ_ENABLED_ENV_VAR, raising=False)
    response = _client(_northern_provider()).get(_url())
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
    # Byte-indistinguishable from an unmounted path: no correlation id, no hint.
    assert "X-Correlation-ID" not in response.headers
    _assert_pair_documented(response)


@pytest.mark.parametrize("token", ["0", "", "false", "off", "maybe"])
def test_non_true_flag_tokens_stay_404(monkeypatch, token) -> None:
    monkeypatch.setenv(INTERNAL_TRANSIT_PARKING_READ_ENABLED_ENV_VAR, token)
    response = _client(_northern_provider()).get(_url())
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# BBL validation (typed 422 before any provider call)
# ---------------------------------------------------------------------------
def test_malformed_bbl_is_typed_422_before_provider(monkeypatch) -> None:
    _enable(monkeypatch)

    def exploding_provider(bbl: str, correlation_id: str) -> TransitParkingStatus:
        raise AssertionError("the provider must not be called for a malformed BBL")

    response = _client(exploding_provider).get(_url("NOT-A-BBL"))
    assert response.status_code == 422
    body = response.json()
    assert body["state"] == "validation_error"
    assert body["correlation_id"]
    assert response.headers["X-Correlation-ID"] == body["correlation_id"]
    assert "code" in body["detail"] and "raw_value" in body["detail"]
    _assert_pair_documented(response)


# ---------------------------------------------------------------------------
# 200 success - recorded 215-16 Northern pack, status == recorded
# ---------------------------------------------------------------------------
def test_recorded_200_from_recorded_pack(monkeypatch) -> None:
    _enable(monkeypatch)
    response = _client(_northern_provider()).get(_url())
    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"]
    body = response.json()
    # A 200 carries NO ``state`` (the document speaks for itself).
    assert "state" not in body
    assert body["contract_version"] == "1.0.0"
    assert body["lot_bbl"] == NORTHERN_BBL
    assert body["status"] == "recorded"
    assert body["status_label"] == "Recorded"
    assert body["transit_zone"] == "Outer Transit Zone"
    assert body["missing_source"] is None
    assert body["source"] is not None and body["source"]["kind"] == "city_dataset"
    # The emitted document honours the published contract.
    validate_transit_parking_document(body)
    _assert_pair_documented(response)


def test_check_needed_200_when_pluto_has_no_transit_zone(monkeypatch) -> None:
    _enable(monkeypatch)
    response = _client(_check_needed_provider()).get(_url())
    assert response.status_code == 200
    body = response.json()
    assert "state" not in body
    assert body["status"] == "check_needed"
    assert body["status_label"] == "Check needed"
    assert body["transit_zone"] is None
    assert body["missing_source"] and "6ztr-wgff" in body["missing_source"]
    assert "Check needed" in body["detail"]
    validate_transit_parking_document(body)
    _assert_pair_documented(response)


# ---------------------------------------------------------------------------
# The zone ONLY - never a parking outcome (spaces, a waiver, an exemption).
# Those are Lane A / G6, never this data layer (plan risk; module boundary).
# ---------------------------------------------------------------------------
_PARKING_OUTCOME_TOKENS = ("space", "waiver", "exempt")


@pytest.mark.parametrize("provider_factory", [_northern_provider, _check_needed_provider])
def test_no_parking_outcome_field_or_text(monkeypatch, provider_factory) -> None:
    _enable(monkeypatch)
    body = _client(provider_factory()).get(_url()).json()
    # No parking-outcome FIELD: the document is exactly the contract key set.
    assert set(body) == {
        "contract_version",
        "lot_bbl",
        "status",
        "status_label",
        "transit_zone",
        "source",
        "detail",
        "missing_source",
    }

    # No parking-outcome TEXT anywhere in the serialized document: it never states a
    # number of spaces, a waiver or an exemption (the zone is carried; applying the
    # ZR parking rules to it is the rule engine's job, Lane A / G6).
    def _strings(node):
        if isinstance(node, str):
            yield node
        elif isinstance(node, dict):
            for value in node.values():
                yield from _strings(value)
        elif isinstance(node, list):
            for item in node:
                yield from _strings(item)

    blob = "\n".join(_strings(body)).lower()
    for token in _PARKING_OUTCOME_TOKENS:
        assert token not in blob, token


# ---------------------------------------------------------------------------
# Inputs unavailable - fail-safe 503, nothing fabricated
# ---------------------------------------------------------------------------
def test_inputs_unavailable_is_fail_safe_503(monkeypatch) -> None:
    _enable(monkeypatch)
    response = _client(_unavailable_provider()).get(_url())
    assert response.status_code == 503
    body = response.json()
    assert body["state"] == "inputs_unavailable"
    assert body["correlation_id"]
    _assert_pair_documented(response)


def test_upstream_connector_failure_is_503(monkeypatch) -> None:
    _enable(monkeypatch)

    def failing_fetcher(bbl: str, correlation_id: str):
        raise SourceUnavailableError("down", correlation_id=correlation_id)

    provider = pluto_transit_parking_provider(failing_fetcher, env=LANE_B_ON)
    response = _client(provider).get(_url())
    assert response.status_code == 503
    assert response.json()["state"] == "inputs_unavailable"


def test_no_match_is_fail_safe_503(monkeypatch) -> None:
    """A valid BBL with no PLUTO record (e.g. a condo unit lot) withholds the
    status rather than fabricating one."""
    _enable(monkeypatch)

    def no_match_fetcher(bbl: str, correlation_id: str):
        return fetch_by_bbl(
            bbl,
            transport=lambda url, headers, timeout: TransportResponse(200, "[]"),
            sleep=lambda seconds: None,
            clock=FIXED_CLOCK,
            correlation_id=correlation_id,
        )

    provider = pluto_transit_parking_provider(no_match_fetcher, clock=FIXED_CLOCK, env=LANE_B_ON)
    response = _client(provider).get(_url())
    assert response.status_code == 503
    assert response.json()["state"] == "inputs_unavailable"


def test_lane_b_gate_off_is_503(monkeypatch) -> None:
    """The transit-zone status is Lane B behaviour: with LANE_B_ENABLED off, the
    status is withheld (fail safe), never fabricated."""
    _enable(monkeypatch)
    provider = pluto_transit_parking_provider(
        _fetcher_for(_northern_record()), clock=FIXED_CLOCK, env={}
    )
    response = _client(provider).get(_url())
    assert response.status_code == 503
    assert response.json()["state"] == "inputs_unavailable"


# ---------------------------------------------------------------------------
# Contract guard - an invalid built document is refused (never an invalid 200)
# ---------------------------------------------------------------------------
def test_invalid_status_is_refused_as_internal_contract_error(monkeypatch) -> None:
    _enable(monkeypatch)
    # Displace a real field: a `recorded` status whose transit_zone is null fails
    # the schema oneOf (recorded must carry a zone). Reverting the None to the real
    # zone restores the 200, so the guard is the thing under test (red/green).
    bad = TransitParkingStatus(
        lot_bbl=NORTHERN_BBL,
        status="recorded",
        transit_zone=None,
        source=None,
        detail="Transit zone: recorded (synthetic broken fixture for the guard test).",
        missing_source=None,
    )
    response = _client(lambda bbl, cid: bad).get(_url())
    assert response.status_code == 500
    assert response.json()["state"] == "internal_contract_error"
    _assert_pair_documented(response)
    # Red/green: the SAME status with the real zone restored is a clean 200.
    good = TransitParkingStatus(
        lot_bbl=NORTHERN_BBL,
        status="recorded",
        transit_zone="Outer Transit Zone",
        source=None,
        detail=bad.detail,
        missing_source=None,
    )
    ok = _client(lambda bbl, cid: good).get(_url())
    assert ok.status_code == 200
    assert ok.json()["transit_zone"] == "Outer Transit Zone"


def test_unexpected_provider_error_is_generic_500(monkeypatch) -> None:
    _enable(monkeypatch)

    def boom(bbl: str, correlation_id: str) -> TransitParkingStatus:
        raise RuntimeError("unexpected")

    response = _client(boom).get(_url())
    assert response.status_code == 500
    body = response.json()
    assert body["state"] == "internal_error"
    # No upstream text leaks into the bounded body.
    assert "unexpected" not in body["message"] or "internal error" in body["message"]
    _assert_pair_documented(response)


# ---------------------------------------------------------------------------
# The route default is the live binding (proven to resolve, not exercised live).
# ---------------------------------------------------------------------------
def test_route_default_provider_is_the_live_binding() -> None:
    assert get_transit_parking_provider() is default_transit_parking_provider


# ---------------------------------------------------------------------------
# The assembly runs resolve ONCE and carries the zone only (check C-8 unit guard).
# ---------------------------------------------------------------------------
def test_assembly_carries_the_zone_from_the_recorded_pack() -> None:
    result = _fetcher_for(_northern_record())(NORTHERN_BBL, "cid")
    status = assemble_transit_parking_status(result, clock=FIXED_CLOCK, env=LANE_B_ON)
    assert status.status == "recorded"
    assert status.transit_zone == "Outer Transit Zone"
    assert status.lot_bbl == NORTHERN_BBL


def test_assembly_lane_b_off_raises_unavailable() -> None:
    result = _fetcher_for(_northern_record())(NORTHERN_BBL, "cid")
    with pytest.raises(TransitParkingUnavailableError) as exc:
        assemble_transit_parking_status(result, clock=FIXED_CLOCK, env={})
    assert exc.value.reason == "lane_b_disabled"


# ---------------------------------------------------------------------------
# The (status, state) matrix is exhaustive: every documented pair is driven, and
# nothing outside it is emitted.
# ---------------------------------------------------------------------------
def test_status_state_matrix_is_exhaustively_driven(monkeypatch) -> None:
    observed: set[tuple[int, str | None]] = set()

    def record(response) -> None:
        body = response.json()
        state = body.get("state") if isinstance(body, dict) else None
        observed.add((response.status_code, state))

    # (404, None): flag off
    monkeypatch.delenv(INTERNAL_TRANSIT_PARKING_READ_ENABLED_ENV_VAR, raising=False)
    record(_client(_northern_provider()).get(_url()))

    _enable(monkeypatch)
    # (422, validation_error)
    record(_client(_northern_provider()).get(_url("NOPE")))
    # (200, None)
    record(_client(_northern_provider()).get(_url()))
    # (503, inputs_unavailable)
    record(_client(_unavailable_provider()).get(_url()))

    # (500, internal_contract_error)
    bad = TransitParkingStatus(
        lot_bbl=NORTHERN_BBL,
        status="recorded",
        transit_zone=None,
        source=None,
        detail="synthetic broken fixture",
        missing_source=None,
    )
    record(_client(lambda bbl, cid: bad).get(_url()))

    # (500, internal_error)
    def boom(bbl: str, correlation_id: str) -> TransitParkingStatus:
        raise RuntimeError("x")

    record(_client(boom).get(_url()))

    # (429, rate_limited): refuse every caller, then one request trips the limit.
    limiter = get_rate_limiter()
    monkeypatch.setattr(limiter, "max_requests", 0)
    limiter.reset()
    record(_client(_northern_provider()).get(_url()))

    assert observed == TRANSIT_PARKING_STATUS_STATE_MATRIX


# ---------------------------------------------------------------------------
# Per-caller rate limit (NB1) - a typed 429 consistent with the sibling route.
# ---------------------------------------------------------------------------
def test_rate_limit_returns_typed_429(monkeypatch) -> None:
    _enable(monkeypatch)
    limiter = get_rate_limiter()
    monkeypatch.setattr(limiter, "max_requests", 2)
    limiter.reset()
    client = _client(_northern_provider())
    assert client.get(_url()).status_code == 200
    assert client.get(_url()).status_code == 200
    limited = client.get(_url())
    assert limited.status_code == 429
    body = limited.json()
    assert body["state"] == "rate_limited"
    assert limited.headers["X-Correlation-ID"] == body["correlation_id"]
    _assert_pair_documented(limited)
    # Mutation (loosen the CONSUMING limiter): a large limit removes the 429.
    monkeypatch.setattr(limiter, "max_requests", 1000)
    limiter.reset()
    assert client.get(_url()).status_code == 200


def test_rate_limit_precedes_validation_and_io(monkeypatch) -> None:
    """The limiter refuses BEFORE validation/I-O: an over-limit caller with a
    malformed BBL still gets the 429, never the 422."""
    _enable(monkeypatch)
    limiter = get_rate_limiter()
    monkeypatch.setattr(limiter, "max_requests", 0)  # refuse every caller
    limiter.reset()

    def exploding_provider(bbl, correlation_id):
        raise AssertionError("provider must not run when rate limited")

    resp = _client(exploding_provider).get(_url("NOT-A-BBL"))
    assert resp.status_code == 429
    assert resp.json()["state"] == "rate_limited"


def test_rate_limit_is_after_the_flag_off_404(monkeypatch) -> None:
    """Hard rule: the flag-off 404 is unchanged - even an over-limit caller gets
    the generic 404 (byte-identical to an unmounted path), never a 429."""
    monkeypatch.delenv(INTERNAL_TRANSIT_PARKING_READ_ENABLED_ENV_VAR, raising=False)
    limiter = get_rate_limiter()
    monkeypatch.setattr(limiter, "max_requests", 0)
    limiter.reset()
    resp = _client(_northern_provider()).get(_url())
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}
    assert "X-Correlation-ID" not in resp.headers


def test_422_message_is_length_capped_server_side(monkeypatch) -> None:
    """Security review NB3: the 422 message is length-capped server-side."""
    from app.api.v1.transit_parking_read import (
        _RAW_VALUE_TRUNCATION_MARKER,
        MAX_MESSAGE_CHARS,
    )

    _enable(monkeypatch)
    response = _client(_northern_provider()).get(_url("NOT-A-BBL"))
    assert response.status_code == 422
    assert len(response.json()["message"]) <= MAX_MESSAGE_CHARS + len(_RAW_VALUE_TRUNCATION_MARKER)
