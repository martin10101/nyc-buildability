"""Condo records channel acceptance pack (task M5-T052, DB-031).

Fully OFFLINE and deterministic: the route's billing- and unit-resolution seams
are overridden via FastAPI dependency injection with recorded typed resolutions
(no test touches the network, mirroring the lot-geometry / record-address
suites). The recorded fixtures include the DB-029c key-absence shape (a resolved
condo whose ``condo_key`` is absent/None - SODA null-omission tolerated).

Coverage:
- Flag off -> generic 404 {detail: Not Found} with no correlation leak;
  include_in_schema False; malformed bbl -> typed 422 with X-Correlation-ID.
- Every resolver outcome is an HONEST 200 records document: resolved_single
  (with the G3-A4 substitution/substrate record), multi_lot (every base lot as a
  record, divergent-zoning notice, NO substitution and NO computed value),
  unresolved / error (honest absence, no fabricated base lot), not_condo_billing
  (empty records, null billing lot).
- Unit-BBL increment (G3-A3): a unit BBL resolves through the resolver's unit
  path to its billing/base outcome (single -> substitution; multi -> records);
  a typed unit-path transport failure is recorded as the ``error`` outcome.
- Cross-boundary token pin (G3-A2): the emitted ``outcome`` literals are exactly
  the resolver's OUTCOME_* vocabulary the web guard/records view branch on.
- CONDO_RECORDS_STATUS_STATE_MATRIX is the emitted (status, state) set; every
  200 body is renderer-parity JSON safe.
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

import app.api.v1.condo_records as condo_records_mod
from app.api.v1.condo_records import (
    CONDO_RECORDS_STATUS_STATE_MATRIX,
    get_condo_billing_resolver,
    get_condo_unit_resolver,
)
from app.config import INTERNAL_RULE_EVAL_ENABLED_ENV_VAR
from app.connectors.condo_base_lot import (
    OUTCOME_ERROR,
    OUTCOME_MULTI_LOT,
    OUTCOME_NOT_CONDO_BILLING,
    OUTCOME_RESOLVED_SINGLE,
    OUTCOME_UNRESOLVED,
    CondoResolution,
)
from app.connectors.dtm_condo_soda import (
    CONDO_DATASET_ID,
    DIVERGENT_ZONING_NOTICE,
    SOURCE_ID,
    STATUS_RESOLVED,
    STATUS_UNRESOLVED,
    CondoBaseLotResult,
    SourceUnavailableError,
)
from app.main import app

BILLING_BBL = "1003037501"  # boro 1, block 00303, lot 7501 -> billing class
BILLING_MULTI_BBL = "1003037502"
UNIT_BBL = "1003031001"  # lot 1001 -> unit class
STANDARD_BBL = "1000010001"  # lot 0001 -> not a condo
RETRIEVED_AT = "2026-09-01T14:05:56Z"
CONDO_KEY = "103343"


def _provenance_entry(query_kind: str) -> dict:
    return {
        "dataset_id": CONDO_DATASET_ID,
        "query_kind": query_kind,
        "request_url": (
            f"https://data.cityofnewyork.us/resource/{CONDO_DATASET_ID}.json"
            f"?condo_billing_bbl={BILLING_BBL}"
        ),
        "retrieved_at": RETRIEVED_AT,
        "record_count": 1,
        "rows_updated_at": None,
    }


def _expected_record_provenance(dataset_version: object = None) -> dict:
    """The per-base-lot provenance EVERY base-lot record must carry (M5-T052
    revision): source id, dataset ids, retrieval timestamp, and dataset version.
    Its provenance reaches every base-lot record, so a base lot whose recorded
    zoning is genuinely absent is an honest, attributable UNKNOWN, not a bare
    blank."""
    return {
        "source_id": SOURCE_ID,
        "dataset_ids": [CONDO_DATASET_ID],
        "retrieved_at": RETRIEVED_AT,
        "dataset_version": dataset_version,
    }


def _base_lot(bbl: str, *, recorded_zoning: object = None) -> dict:
    """The expected base-lot record shape: the recorded BBL, its recorded zoning
    (genuine ``None`` unknown from the DTM condo channel today), an EXPLICIT
    status label for that zoning, and that record's provenance."""
    return {
        "bbl": bbl,
        "recorded_zoning": recorded_zoning,
        "recorded_zoning_status": "recorded" if recorded_zoning is not None else "unknown",
        "provenance": _expected_record_provenance(),
    }


def _resolution(outcome: str, **overrides: object) -> CondoResolution:
    base: dict = {
        "outcome": outcome,
        "input_bbl": BILLING_BBL,
        "correlation_id": "test-corr",
        "source_id": SOURCE_ID,
        "dataset_ids": (CONDO_DATASET_ID,),
        "retrieved_at": RETRIEVED_AT,
        "provenance": (_provenance_entry("condo_billing_bbl"),),
        "divergent_zoning_notice": DIVERGENT_ZONING_NOTICE,
        "condo_key": CONDO_KEY,
        "condo_number": "3343",
    }
    base.update(overrides)
    return CondoResolution(**base)  # type: ignore[arg-type]


def _resolved_single() -> CondoResolution:
    return _resolution(
        OUTCOME_RESOLVED_SINGLE,
        base_bbls=("1003030019",),
        resolved_base_bbl="1003030019",
        resolution_path="billing",
        notes=("billing BBL resolved to a single recorded base lot.",),
    )


def _multi_lot() -> CondoResolution:
    return _resolution(
        OUTCOME_MULTI_LOT,
        input_bbl=BILLING_MULTI_BBL,
        base_bbls=("1003030019", "1003030025"),
        resolved_base_bbl=None,
        resolution_path="billing",
        notes=("multi-lot condo: 2 base lots resolved; never collapsed.",),
    )


def _unit_result(status: str, **overrides: object) -> CondoBaseLotResult:
    base: dict = {
        "status": status,
        "input_value": UNIT_BBL,
        "lot_class": "unit",
        "correlation_id": "test-corr",
        "retrieved_at": RETRIEVED_AT,
        "resolution_path": "unit",
        "provenance": [_provenance_entry("unit_bbl")],
        "condo_key": CONDO_KEY,
        "condo_number": "3343",
    }
    base.update(overrides)
    return CondoBaseLotResult(**base)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Offline seam plumbing
# ---------------------------------------------------------------------------
def install_billing(resolution: CondoResolution) -> None:
    app.dependency_overrides[get_condo_billing_resolver] = lambda: (
        lambda bbl, cid: resolution
    )


def install_unit(result: CondoBaseLotResult) -> None:
    app.dependency_overrides[get_condo_unit_resolver] = lambda: (
        lambda bbl, cid: result
    )


def install_unit_raising(exc: Exception) -> None:
    def _provider():
        def _resolve(bbl: str, cid: str):
            raise exc

        return _resolve

    app.dependency_overrides[get_condo_unit_resolver] = _provider


def install_billing_landmine() -> None:
    """The billing seam must NOT be invoked for a unit-class BBL."""

    def _provider():
        def _resolve(bbl: str, cid: str):
            raise AssertionError("billing resolver must not run for a unit BBL")

        return _resolve

    app.dependency_overrides[get_condo_billing_resolver] = _provider


def install_unit_landmine() -> None:
    """The unit seam must NOT be invoked for a billing/standard BBL."""

    def _provider():
        def _resolve(bbl: str, cid: str):
            raise AssertionError("unit resolver must not run for a billing BBL")

        return _resolve

    app.dependency_overrides[get_condo_unit_resolver] = _provider


def enable_flag(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_RULE_EVAL_ENABLED_ENV_VAR, "1")


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def raw_client():
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _assert_renderer_parity_safe(document: dict) -> None:
    json.dumps(document, allow_nan=False)
    json.dumps(document, ensure_ascii=False, allow_nan=False).encode("utf-8")


def _url(bbl: str) -> str:
    return f"/api/v1/properties/{bbl}/condo-records"


# ---------------------------------------------------------------------------
# Flag gate / validation
# ---------------------------------------------------------------------------
def test_flag_off_is_generic_404_no_leak(client):
    install_unit_landmine()
    install_billing_landmine()
    resp = client.get(_url(BILLING_BBL))
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}
    assert "X-Correlation-ID" not in resp.headers


def test_malformed_bbl_is_typed_422(client, monkeypatch):
    enable_flag(monkeypatch)
    install_billing_landmine()
    install_unit_landmine()
    resp = client.get(_url("not-a-bbl"))
    assert resp.status_code == 422
    assert resp.headers["X-Correlation-ID"]
    body = resp.json()
    assert body["state"] == "validation_error"
    assert "code" in body["detail"]


# ---------------------------------------------------------------------------
# Billing-path outcomes (200 records documents)
# ---------------------------------------------------------------------------
def test_resolved_single_records_substitution(client, monkeypatch):
    enable_flag(monkeypatch)
    install_unit_landmine()  # a billing BBL must not touch the unit path
    install_billing(_resolved_single())
    resp = client.get(_url(BILLING_BBL))
    assert resp.status_code == 200
    assert resp.headers["X-Correlation-ID"]
    body = resp.json()
    _assert_renderer_parity_safe(body)
    assert body["document_kind"] == "condo_records"
    assert body["outcome"] == OUTCOME_RESOLVED_SINGLE
    assert body["bbl"] == BILLING_BBL
    # Distinct identifiers: a billing-class entry IS the billing lot; the entered
    # BBL and its lot class are recorded verbatim; the billing lot is LABELLED
    # recorded (not a bare value a reader must interpret).
    assert body["entered_bbl"] == BILLING_BBL
    assert body["entered_lot_class"] == "billing"
    assert body["billing_bbl"] == BILLING_BBL
    assert body["billing_bbl_status"] == "recorded"
    assert body["base_lots"] == [_base_lot("1003030019")]
    # Available recorded zoning AND its provenance reach every base-lot record;
    # the zoning is a genuine unknown from the DTM condo channel today, LABELLED
    # explicitly ("unknown") rather than a silent null.
    assert body["base_lots"][0]["provenance"]["source_id"] == SOURCE_ID
    assert body["base_lots"][0]["recorded_zoning"] is None
    assert body["base_lots"][0]["recorded_zoning_status"] == "unknown"
    # The genuinely-unavailable zoning is NOT silently deferred: the document names
    # the concrete downstream dependency (ZTLDB / spatial) for the orchestrator.
    assert body["recorded_zoning_dependency"]
    assert "ztldb" in body["recorded_zoning_dependency"].lower()
    # G3-A4 substrate record: entered vs analyzed BBL is explicit and distinct.
    assert body["substitution"]["entered_bbl"] == BILLING_BBL
    assert body["substitution"]["analyzed_bbl"] == "1003030019"
    assert body["substitution"]["analyzed_bbl"] != body["entered_bbl"]
    # Provenance quintuple: source id, dataset ids, retrieved_at, per-query url.
    assert body["provenance"]["source_id"] == SOURCE_ID
    assert body["provenance"]["dataset_ids"] == [CONDO_DATASET_ID]
    assert body["provenance"]["retrieved_at"] == RETRIEVED_AT
    assert body["provenance"]["queries"][0]["request_url"].startswith("https://")
    # No divergent-zoning notice on a clean single resolution.
    assert body["divergent_zoning_notice"] is None
    # RECORDS not allowances: no computed decimal value anywhere in the document.
    assert "far" not in json.dumps(body).lower()


def test_multi_lot_records_every_base_lot_no_substitution(client, monkeypatch):
    enable_flag(monkeypatch)
    install_unit_landmine()
    install_billing(_multi_lot())
    resp = client.get(_url(BILLING_MULTI_BBL))
    assert resp.status_code == 200
    body = resp.json()
    _assert_renderer_parity_safe(body)
    assert body["outcome"] == OUTCOME_MULTI_LOT
    # A billing-class entry: entered BBL == billing lot (labelled recorded); base
    # lots are distinct.
    assert body["entered_bbl"] == BILLING_MULTI_BBL
    assert body["entered_lot_class"] == "billing"
    assert body["billing_bbl"] == BILLING_MULTI_BBL
    assert body["billing_bbl_status"] == "recorded"
    assert body["base_lots"] == [_base_lot("1003030019"), _base_lot("1003030025")]
    assert [lot["bbl"] for lot in body["base_lots"]] == ["1003030019", "1003030025"]
    # Every base lot's zoning is a LABELLED unknown; the dependency is named once.
    assert all(lot["recorded_zoning"] is None for lot in body["base_lots"])
    assert all(lot["recorded_zoning_status"] == "unknown" for lot in body["base_lots"])
    assert body["recorded_zoning_dependency"]
    # Its provenance reaches EVERY base-lot record (M5-T052 revision).
    assert all(
        lot["provenance"] == _expected_record_provenance() for lot in body["base_lots"]
    )
    # A multi-lot outcome exposes NO single analyzed lot - a consumer cannot pick one.
    assert body["substitution"] is None
    # The permanent no-collapse boundary stays visible.
    assert body["divergent_zoning_notice"] == DIVERGENT_ZONING_NOTICE
    # RECORDS not allowances: no computed FAR / allowance vocabulary anywhere.
    assert "far" not in json.dumps(body).lower()


def test_unresolved_is_honest_absence(client, monkeypatch):
    enable_flag(monkeypatch)
    install_unit_landmine()
    install_billing(
        _resolution(
            OUTCOME_UNRESOLVED,
            condo_key=None,
            notes=("matched no base-lot record; honest unresolved result.",),
        )
    )
    resp = client.get(_url(BILLING_BBL))
    assert resp.status_code == 200
    body = resp.json()
    assert body["outcome"] == OUTCOME_UNRESOLVED
    assert body["base_lots"] == []
    assert body["substitution"] is None
    assert body["reason"]  # honest, never blank
    # A billing-class entry: the billing lot IS recorded even on an unresolved
    # outcome; with no base lots there is no unknown zoning to depend on.
    assert body["billing_bbl_status"] == "recorded"
    assert body["recorded_zoning_dependency"] is None


def test_error_outcome_is_typed_record_not_5xx(client, monkeypatch):
    enable_flag(monkeypatch)
    install_unit_landmine()
    install_billing(
        _resolution(
            OUTCOME_ERROR,
            error_type="source_unavailable",
            provenance=(),
            notes=("typed transport error; fail-safe to professional review.",),
        )
    )
    resp = client.get(_url(BILLING_BBL))
    assert resp.status_code == 200  # a typed resolver error is a RECORD, not a route fault
    body = resp.json()
    assert body["outcome"] == OUTCOME_ERROR
    assert body["error_type"] == "source_unavailable"
    assert body["base_lots"] == []
    assert body["reason"]


def test_not_condo_billing_has_empty_records_and_null_billing_lot(client, monkeypatch):
    enable_flag(monkeypatch)
    install_unit_landmine()
    install_billing(
        _resolution(
            OUTCOME_NOT_CONDO_BILLING,
            input_bbl=STANDARD_BBL,
            source_id=None,
            dataset_ids=(),
            retrieved_at=None,
            provenance=(),
            condo_key=None,
            condo_number=None,
            divergent_zoning_notice=None,
            notes=("input is not a condo billing BBL; pass-through.",),
        )
    )
    resp = client.get(_url(STANDARD_BBL))
    assert resp.status_code == 200
    body = resp.json()
    assert body["outcome"] == OUTCOME_NOT_CONDO_BILLING
    assert body["billing_bbl"] is None
    # A non-condo input has no billing lot: LABELLED not_applicable, not "unknown".
    assert body["billing_bbl_status"] == "not_applicable"
    assert body["base_lots"] == []
    assert body["substitution"] is None
    assert body["recorded_zoning_dependency"] is None


def test_recorded_zoning_when_present_is_labelled_recorded(client, monkeypatch):
    # Forward-compatibility: the "unknown" label is DATA-DRIVEN, not a hardcoded
    # blank. When an upstream channel supplies per-base-lot zoning through the one
    # ``_recorded_zoning_for`` seam, the status flips to RECORDED and the
    # dependency note disappears - proving today's universal unknown is an honest
    # reflection of the DTM channel, not a silent stub.
    enable_flag(monkeypatch)
    install_unit_landmine()
    install_billing(_resolved_single())
    monkeypatch.setattr(
        condo_records_mod, "_recorded_zoning_for", lambda base_bbl, resolution: "R6"
    )
    resp = client.get(_url(BILLING_BBL))
    assert resp.status_code == 200
    body = resp.json()
    assert body["base_lots"][0]["recorded_zoning"] == "R6"
    assert body["base_lots"][0]["recorded_zoning_status"] == "recorded"
    # No unknown zoning remains, so the dependency note is absent.
    assert body["recorded_zoning_dependency"] is None


# ---------------------------------------------------------------------------
# Unit-BBL increment (G3-A3): the resolver's unit path
# ---------------------------------------------------------------------------
def test_unit_bbl_resolves_single_through_unit_path(client, monkeypatch):
    enable_flag(monkeypatch)
    install_billing_landmine()  # a unit BBL must not touch the billing seam
    install_unit(_unit_result(STATUS_RESOLVED, base_bbls=["1003030019"]))
    resp = client.get(_url(UNIT_BBL))
    assert resp.status_code == 200
    body = resp.json()
    assert body["outcome"] == OUTCOME_RESOLVED_SINGLE
    # A UNIT-class entry is NOT the billing lot: the entered BBL is the unit lot,
    # its lot class is 'unit', and the billing lot is genuinely unknown from the
    # unit path (null) - LABELLED "unknown", never the entered unit BBL relabelled
    # as billing.
    assert body["entered_bbl"] == UNIT_BBL
    assert body["entered_lot_class"] == "unit"
    assert body["billing_bbl"] is None
    assert body["billing_bbl_status"] == "unknown"
    assert body["base_lots"] == [_base_lot("1003030019")]
    assert body["base_lots"][0]["recorded_zoning_status"] == "unknown"
    assert body["recorded_zoning_dependency"]
    # Three distinct identifiers: entered (unit) != analyzed (base); billing is a
    # labelled unknown, never conflated with either.
    assert body["substitution"]["entered_bbl"] == UNIT_BBL
    assert body["substitution"]["analyzed_bbl"] == "1003030019"
    assert body["substitution"]["analyzed_bbl"] != body["entered_bbl"]
    assert body["billing_bbl"] != body["substitution"]["analyzed_bbl"]
    # DB-029c key-absence tolerated below; here condo_key is present verbatim.
    assert body["condo_key"] == CONDO_KEY


def test_unit_bbl_multi_lot_records_only(client, monkeypatch):
    enable_flag(monkeypatch)
    install_billing_landmine()
    install_unit(
        _unit_result(STATUS_RESOLVED, base_bbls=["1003030019", "1003030025"])
    )
    resp = client.get(_url(UNIT_BBL))
    assert resp.status_code == 200
    body = resp.json()
    assert body["outcome"] == OUTCOME_MULTI_LOT
    # A unit-class entry: the billing lot is a labelled unknown (null); the base
    # lots are records with per-record provenance.
    assert body["entered_bbl"] == UNIT_BBL
    assert body["entered_lot_class"] == "unit"
    assert body["billing_bbl"] is None
    assert body["billing_bbl_status"] == "unknown"
    assert [lot["bbl"] for lot in body["base_lots"]] == [
        "1003030019",
        "1003030025",
    ]
    assert all(
        lot["provenance"] == _expected_record_provenance() for lot in body["base_lots"]
    )
    assert body["substitution"] is None
    assert body["divergent_zoning_notice"] == DIVERGENT_ZONING_NOTICE


def test_unit_bbl_key_absence_db029c_shape_tolerated(client, monkeypatch):
    enable_flag(monkeypatch)
    install_billing_landmine()
    # DB-029c: SODA null-omission - a resolved condo whose condo_key column is
    # absent (None). The route records the base lot honestly and never fabricates
    # a key.
    install_unit(
        _unit_result(STATUS_RESOLVED, base_bbls=["1003030019"], condo_key=None)
    )
    resp = client.get(_url(UNIT_BBL))
    assert resp.status_code == 200
    body = resp.json()
    assert body["outcome"] == OUTCOME_RESOLVED_SINGLE
    assert body["condo_key"] is None
    assert body["base_lots"] == [_base_lot("1003030019")]


def test_unit_bbl_unresolved_is_honest_absence(client, monkeypatch):
    enable_flag(monkeypatch)
    install_billing_landmine()
    install_unit(_unit_result(STATUS_UNRESOLVED, base_bbls=[], condo_key=None))
    resp = client.get(_url(UNIT_BBL))
    assert resp.status_code == 200
    body = resp.json()
    assert body["outcome"] == OUTCOME_UNRESOLVED
    assert body["base_lots"] == []
    assert body["reason"]


def test_unit_path_transport_error_is_error_record(client, monkeypatch):
    enable_flag(monkeypatch)
    install_billing_landmine()
    install_unit_raising(
        SourceUnavailableError("SODA unavailable", correlation_id="c")
    )
    resp = client.get(_url(UNIT_BBL))
    assert resp.status_code == 200
    body = resp.json()
    assert body["outcome"] == OUTCOME_ERROR
    assert body["error_type"] == "source_unavailable"
    assert body["base_lots"] == []


# ---------------------------------------------------------------------------
# Cross-boundary token pin (G3-A2) + emitted (status, state) matrix
# ---------------------------------------------------------------------------
def test_outcome_token_vocabulary_is_the_pinned_literal_set():
    # The api half of the cross-boundary token pin: the resolver's outcome
    # vocabulary is EXACTLY these literals, the same strings the web guard
    # (condoWithholdsAllowances) and the web condo-records client branch on.
    # The web suite pins the identical set; neither side may drift.
    assert OUTCOME_RESOLVED_SINGLE == "resolved_single_base_lot"
    assert OUTCOME_MULTI_LOT == "multi_lot_set"
    assert OUTCOME_UNRESOLVED == "unresolved"
    assert OUTCOME_ERROR == "error"
    assert OUTCOME_NOT_CONDO_BILLING == "not_condo_billing"


def test_status_state_matrix_membership(client, monkeypatch):
    # Every documented (status, state) pair; the 200 carries no ``state``.
    assert (200, None) in CONDO_RECORDS_STATUS_STATE_MATRIX
    assert (404, None) in CONDO_RECORDS_STATUS_STATE_MATRIX
    assert (422, "validation_error") in CONDO_RECORDS_STATUS_STATE_MATRIX
    assert (500, "internal_error") in CONDO_RECORDS_STATUS_STATE_MATRIX

    enable_flag(monkeypatch)
    install_unit_landmine()
    install_billing(_resolved_single())
    resp = client.get(_url(BILLING_BBL))
    assert (resp.status_code, resp.json().get("state")) in CONDO_RECORDS_STATUS_STATE_MATRIX
