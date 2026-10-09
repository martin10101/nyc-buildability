"""GET /api/v1/properties/{bbl}/parity - internal parity-read route (lane C
packet W4).

Offline and deterministic. The route is now mounted in ``app.main`` (packet W5,
self-gated and default off; the real-app mount is proven in
``tests/api/test_read_router_mounts.py``), and every test builds a LOCAL FastAPI
app over the W4 router and drives it through its INJECTED DOF transport
(``get_dof_transport`` override) reading the RECORDED Bayside DOF pack
(``tests/fixtures/dof_sales_bayside``) for the 215-16 Northern subject
(BBL 4073340070). No network is touched.

Coverage:

- the full ``PARITY_READ_STATUS_STATE_MATRIX`` is driven (exhaustive), and every
  emitted (HTTP status, state) pair is asserted to be documented in it;
- flag-off 404 (byte-identical to an unmounted path), non-true flag tokens;
- malformed BBL -> typed 422 BEFORE any DOF call (the transport must not run);
- per-caller rate limit -> typed 429;
- Lane B gate off -> fail-safe 503 (and NO live DOF call);
- an upstream DOF failure and a subject with no usable recorded sale -> 503;
- the 200 parity document from the recorded pack: comparable sales carry the DOF
  7-key row source verbatim, and the unused-floor-area line reads the exact
  "Not confirmed" wording with the existing-floor-area input UNKNOWN (no number);
- honesty: no average / price-per-square-foot / capacity key appears anywhere,
  and no 485-x / tax-incentive field is introduced;
- the contract guard (a tampered serializer cannot ship an invalid 200) and the
  generic internal-error surfaces.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1 import parity_read
from app.api.v1.parity_read import (
    CANDIDATE_ROW_LIMIT,
    PARITY_READ_STATUS_STATE_MATRIX,
    SUBJECT_SALES_ROW_LIMIT,
    get_dof_transport,
    get_rate_limiter,
    router,
)
from app.config import INTERNAL_PARITY_READ_ENABLED_ENV_VAR, LANE_FLAG_ENV_VARS
from app.connectors.dof_sales_soda import build_by_bbl_url, build_candidates_url
from app.resilience.transport import Transport, TransportResponse

PACK = Path(__file__).resolve().parents[1] / "fixtures" / "dof_sales_bayside"
NORTHERN_BBL = "4073340070"
NEIGHBORHOOD = "BAYSIDE"
BUILDING_CLASS = "22 STORE BUILDINGS"
LANE_B_ENV_VAR = LANE_FLAG_ENV_VARS["B"]

BY_BBL_URL = build_by_bbl_url(NORTHERN_BBL, row_limit=SUBJECT_SALES_ROW_LIMIT)
CANDIDATES_URL = build_candidates_url(NEIGHBORHOOD, BUILDING_CLASS, row_limit=CANDIDATE_ROW_LIMIT)

_VINTAGE = {"x-soda2-truth-last-modified": "2026-09-01"}


def _fixture(name: str) -> str:
    return (PACK / name).read_text(encoding="utf-8")


def _routed_transport(routes: dict[str, str]) -> Transport:
    """A transport that returns the recorded body for an exact request url, else
    fails the test (an unexpected live-shaped url must never be silently served)."""

    def transport(url: str, headers: dict, timeout: float) -> TransportResponse:
        assert url in routes, f"unexpected url {url!r}"
        return TransportResponse(200, routes[url], dict(_VINTAGE))

    return transport


def _bayside_transport() -> Transport:
    return _routed_transport(
        {
            BY_BBL_URL: _fixture("dof_sales_w2pb-icbu_bbl_4073340070.json"),
            CANDIDATES_URL: _fixture("dof_sales_w2pb-icbu_bayside_22_store_buildings.json"),
        }
    )


def _never_called_transport() -> Transport:
    def transport(url: str, headers: dict, timeout: float) -> TransportResponse:
        raise AssertionError("the DOF transport must not be called")

    return transport


def _client(transport: Transport | None = None) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    if transport is not None:
        app.dependency_overrides[get_dof_transport] = lambda: transport
    return TestClient(app)


def _enable(monkeypatch) -> None:
    """Flag the route ON and the Lane B data gate ON (the 200 path needs both)."""
    monkeypatch.setenv(INTERNAL_PARITY_READ_ENABLED_ENV_VAR, "1")
    monkeypatch.setenv(LANE_B_ENV_VAR, "1")


def _assert_pair_documented(response) -> None:
    body = response.json()
    state = body.get("state") if isinstance(body, dict) else None
    assert (response.status_code, state) in PARITY_READ_STATUS_STATE_MATRIX, (
        response.status_code,
        state,
    )


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """The per-route limiter is MODULE-level state keyed by the shared TestClient
    host; reset its windows around every test so cases do not accumulate stamps
    into a spurious 429. ``max_requests`` is mutated (and auto-restored) by
    monkeypatch only in the dedicated 429 test."""
    get_rate_limiter().reset()
    yield
    get_rate_limiter().reset()


def _iter_keys(node: Any):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _iter_keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_keys(item)


# ---------------------------------------------------------------------------
# Flag gating
# ---------------------------------------------------------------------------
def test_flag_off_is_generic_404(monkeypatch) -> None:
    monkeypatch.delenv(INTERNAL_PARITY_READ_ENABLED_ENV_VAR, raising=False)
    response = _client(_never_called_transport()).get(f"/api/v1/properties/{NORTHERN_BBL}/parity")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
    # Byte-indistinguishable from an unmounted path: no correlation id, no hint.
    assert "X-Correlation-ID" not in response.headers
    _assert_pair_documented(response)


@pytest.mark.parametrize("token", ["0", "", "false", "off", "maybe"])
def test_non_true_flag_tokens_stay_404(monkeypatch, token) -> None:
    monkeypatch.setenv(INTERNAL_PARITY_READ_ENABLED_ENV_VAR, token)
    response = _client(_never_called_transport()).get(f"/api/v1/properties/{NORTHERN_BBL}/parity")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# BBL validation (typed 422 before any DOF call)
# ---------------------------------------------------------------------------
def test_malformed_bbl_is_typed_422_before_any_dof_call(monkeypatch) -> None:
    _enable(monkeypatch)
    response = _client(_never_called_transport()).get("/api/v1/properties/NOT-A-BBL/parity")
    assert response.status_code == 422
    body = response.json()
    assert body["state"] == "validation_error"
    assert body["correlation_id"]
    assert response.headers["X-Correlation-ID"] == body["correlation_id"]
    assert "code" in body["detail"] and "raw_value" in body["detail"]
    _assert_pair_documented(response)


# ---------------------------------------------------------------------------
# Per-caller rate limit (typed 429)
# ---------------------------------------------------------------------------
def test_rate_limited_is_typed_429(monkeypatch) -> None:
    _enable(monkeypatch)
    # A zero budget refuses the first caller outright, before any DOF work.
    monkeypatch.setattr(get_rate_limiter(), "max_requests", 0)
    response = _client(_never_called_transport()).get(f"/api/v1/properties/{NORTHERN_BBL}/parity")
    assert response.status_code == 429
    body = response.json()
    assert body["state"] == "rate_limited"
    assert body["correlation_id"]
    assert response.headers["X-Correlation-ID"] == body["correlation_id"]
    _assert_pair_documented(response)


# ---------------------------------------------------------------------------
# Lane B gate off -> fail-safe 503, and NO live DOF call
# ---------------------------------------------------------------------------
def test_lane_b_gate_off_is_fail_safe_503(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_PARITY_READ_ENABLED_ENV_VAR, "1")
    monkeypatch.delenv(LANE_B_ENV_VAR, raising=False)
    response = _client(_never_called_transport()).get(f"/api/v1/properties/{NORTHERN_BBL}/parity")
    assert response.status_code == 503
    body = response.json()
    assert body["state"] == "inputs_unavailable"
    assert body["correlation_id"]
    _assert_pair_documented(response)


# ---------------------------------------------------------------------------
# Upstream DOF failure and no-usable-subject -> 503 (nothing fabricated)
# ---------------------------------------------------------------------------
def test_upstream_dof_failure_is_fail_safe_503(monkeypatch) -> None:
    _enable(monkeypatch)
    # A 400 carrying the Socrata schema-drift errorCode is raised immediately
    # (never retried), so the connector surfaces a typed failure with no sleep.
    drift_body = '{"errorCode":"query.soql.no-such-column","message":"bad column"}'

    def transport(url: str, headers: dict, timeout: float) -> TransportResponse:
        return TransportResponse(400, drift_body, {})

    response = _client(transport).get(f"/api/v1/properties/{NORTHERN_BBL}/parity")
    assert response.status_code == 503
    assert response.json()["state"] == "inputs_unavailable"
    _assert_pair_documented(response)


def test_subject_with_no_recorded_sale_is_503(monkeypatch) -> None:
    _enable(monkeypatch)
    # The subject BBL has no recorded DOF sale -> no usable type/size, so the
    # disclosed "similar type and size" filter has no honest inputs -> withheld.
    transport = _routed_transport({BY_BBL_URL: "[]"})
    response = _client(transport).get(f"/api/v1/properties/{NORTHERN_BBL}/parity")
    assert response.status_code == 503
    assert response.json()["state"] == "inputs_unavailable"


# ---------------------------------------------------------------------------
# 200 success - recorded Bayside pack through the real selection + unused-floor-area
# ---------------------------------------------------------------------------
def test_parity_200_from_recorded_pack(monkeypatch) -> None:
    _enable(monkeypatch)
    response = _client(_bayside_transport()).get(f"/api/v1/properties/{NORTHERN_BBL}/parity")
    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"]
    body = response.json()
    # A 200 carries NO ``state`` (the document speaks for itself).
    assert "state" not in body
    assert body["contract_version"] == "1.0.0"
    assert set(body) == {"contract_version", "comparable_sales", "unused_floor_area"}
    _assert_pair_documented(response)


def test_comparable_sales_carry_the_dof_row_source_verbatim(monkeypatch) -> None:
    _enable(monkeypatch)
    body = _client(_bayside_transport()).get(f"/api/v1/properties/{NORTHERN_BBL}/parity").json()
    comps = body["comparable_sales"]
    # The subject's own recorded type and size (215-16 Northern).
    assert comps["subject"] == {
        "bbl": NORTHERN_BBL,
        "building_class_category": BUILDING_CLASS,
        "gross_square_feet": 5091,
    }
    assert comps["selected"], "the recorded pack should yield at least one comparable"
    # The DOF 7-key ROW source the contract models (NOT the wider 9-key connector
    # provenance). Carried verbatim on the result and on every selected row.
    expected_source_keys = {
        "kind",
        "source_id",
        "dataset_id",
        "dataset",
        "request_url",
        "retrieved_at",
        "dataset_last_modified",
    }
    assert set(comps["source"]) == expected_source_keys
    assert comps["source"]["kind"] == "city_dataset"
    for row in comps["selected"]:
        assert set(row["source"]) == expected_source_keys


def test_comparable_sales_is_not_a_valuation(monkeypatch) -> None:
    _enable(monkeypatch)
    body = _client(_bayside_transport()).get(f"/api/v1/properties/{NORTHERN_BBL}/parity").json()
    comps = body["comparable_sales"]
    assert comps["not_a_valuation"].startswith(
        "These are recorded sales selected by a simple, disclosed filter, not a valuation"
    )


def test_unused_floor_area_reads_only_not_confirmed_with_no_number(monkeypatch) -> None:
    _enable(monkeypatch)
    body = _client(_bayside_transport()).get(f"/api/v1/properties/{NORTHERN_BBL}/parity").json()
    unused = body["unused_floor_area"]
    assert unused["status"] == "not_confirmed"
    assert unused["label"] == "Remaining development capacity: Not confirmed"
    assert unused["reason"] == (
        "Needs verified zoning-lot boundaries and existing zoning floor area."
    )
    # The existing-floor-area INPUT is UNKNOWN for now (B-05 wiring is a later
    # slice): no number, no capacity.
    efa = unused["existing_floor_area_input"]
    assert efa["known"] is False
    assert efa["value_sq_ft"] is None
    assert efa["basis"] == "unknown"


# ---------------------------------------------------------------------------
# Honesty: no derived valuation / capacity key, and no 485-x / tax-incentive field
# ---------------------------------------------------------------------------
_VALUATION_KEYS = {
    "average",
    "avg",
    "mean",
    "price_per_square_foot",
    "price_per_sq_ft",
    "ppsf",
    "dollars_per_square_foot",
    "estimate",
    "estimated_value",
    "valuation",
}
_CAPACITY_KEYS = {
    "capacity",
    "remaining",
    "remaining_floor_area",
    "remaining_development_capacity",
    "allowance",
    "floor_area_allowance",
    "far",
    "unused_floor_area_sq_ft",
    "air_rights",
}
_INCENTIVE_MARKERS = ("485", "exemption", "incentive", "abatement")


def test_no_valuation_or_capacity_or_incentive_keys(monkeypatch) -> None:
    _enable(monkeypatch)
    body = _client(_bayside_transport()).get(f"/api/v1/properties/{NORTHERN_BBL}/parity").json()
    keys = {key.lower() for key in _iter_keys(body)}
    assert not (keys & _VALUATION_KEYS), sorted(keys & _VALUATION_KEYS)
    assert not (keys & _CAPACITY_KEYS), sorted(keys & _CAPACITY_KEYS)
    # 485-x (and any tax exemption/incentive) is out of scope: no such FIELD is
    # introduced. Checked on keys (contract field names), never on DOF values.
    for key in keys:
        for marker in _INCENTIVE_MARKERS:
            assert marker not in key, key


# ---------------------------------------------------------------------------
# Contract guard - a tampered serializer cannot ship an invalid 200
# ---------------------------------------------------------------------------
def test_contract_guard_refuses_an_invalid_document(monkeypatch) -> None:
    _enable(monkeypatch)
    real = parity_read._serialize_comparable_sales

    def tampered(result) -> dict:
        serialized = real(result)
        # Break the pinned not-a-valuation disclosure const; the guard must catch
        # it and refuse to ship (an invalid 200 is impossible).
        serialized["not_a_valuation"] = "tampered - this is my appraisal"
        return serialized

    monkeypatch.setattr(parity_read, "_serialize_comparable_sales", tampered)
    response = _client(_bayside_transport()).get(f"/api/v1/properties/{NORTHERN_BBL}/parity")
    assert response.status_code == 500
    body = response.json()
    assert body["state"] == "internal_contract_error"
    assert body["correlation_id"]
    _assert_pair_documented(response)


def test_fix_moves_the_disclosure_field_red_green(monkeypatch) -> None:
    """Red/green companion to the guard test: with the serializer UNTAMPERED the
    same request is a valid 200, proving the 500 above is caused by the tamper and
    not by an unrelated defect."""
    _enable(monkeypatch)
    response = _client(_bayside_transport()).get(f"/api/v1/properties/{NORTHERN_BBL}/parity")
    assert response.status_code == 200
    assert response.json()["comparable_sales"]["not_a_valuation"].startswith(
        "These are recorded sales"
    )


# ---------------------------------------------------------------------------
# Generic internal error (unexpected defect before send)
# ---------------------------------------------------------------------------
def test_unexpected_serialization_defect_is_generic_500(monkeypatch) -> None:
    _enable(monkeypatch)

    def boom(document: dict) -> None:
        raise ValueError("unexpected serialization defect")

    monkeypatch.setattr(parity_read, "_assert_json_safe", boom)
    response = _client(_bayside_transport()).get(f"/api/v1/properties/{NORTHERN_BBL}/parity")
    assert response.status_code == 500
    body = response.json()
    assert body["state"] == "internal_error"
    assert body["correlation_id"]
    _assert_pair_documented(response)


def test_every_documented_pair_is_exercised() -> None:
    """Guard against an undriven matrix entry: the pairs this suite asserts MUST
    equal PARITY_READ_STATUS_STATE_MATRIX exactly (exhaustive)."""
    driven = {
        (200, None),
        (404, None),
        (422, "validation_error"),
        (429, "rate_limited"),
        (503, "inputs_unavailable"),
        (500, "internal_error"),
        (500, "internal_contract_error"),
    }
    assert driven == set(PARITY_READ_STATUS_STATE_MATRIX)
