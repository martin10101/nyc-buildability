"""Zoning-lot index classifier (backlog DB-232; task M5-T158; record NB-01).

The pure classifier is driven by SYNTHETIC index results (one per state, labelled synthetic
inline) and by the recorded 215-16 Northern benchmark replay. Expected values come from the
source data and draft rule DB232-R1, never from a program run.

This file also carries the study-inputs seam tests (there is no allowed api test file in part A):
the zoning_lot_index carrier defaults to NOT_CHECKED, the route output is byte-identical whether
or not a provider is bound, and the LIVE ACRIS provider maps a connector failure to NOT_READ
(never 503, never NONE_FOUND).
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.v1.study_inputs import (
    acris_zoning_lot_index_provider,
    assemble_study_inputs,
    pluto_study_inputs_provider,
)
from app.api.v1.study_read import get_rate_limiter, get_study_inputs_provider
from app.config import INTERNAL_STUDY_READ_ENABLED_ENV_VAR
from app.connectors.acris_index_soda import (
    AcrisDocument,
    AcrisLegalLot,
    AcrisZoningLotIndexResult,
    build_good_through_url,
    build_legals_by_documents_url,
    build_legals_by_lot_url,
    build_master_url,
    fetch_zoning_lot_index,
)
from app.main import create_app
from app.profile.zoning_lot_index import (
    ZoningLotIndex,
    ZoningLotIndexState,
    classify_zoning_lot_index,
    not_checked,
    not_read,
)
from app.resilience.transport import TransportResponse
from tests.api.test_study_read_api import (
    FIXED_CLOCK,
    LANE_B_ON,
    NORTHERN_BBL,
    _northern_fetcher,
    _northern_provider,
)

PACK = Path(__file__).resolve().parents[1] / "fixtures" / "benchmark_215_16_northern"
SUBJECT_BBL = "4073340070"  # borough 4, block 7334, lot 70


# ---------------------------------------------------------------------------
# Synthetic index builders (all inputs below are SYNTHETIC unless noted).
# ---------------------------------------------------------------------------
def _lot(borough: str, block: str, lot: str, partial: str = "E") -> AcrisLegalLot:
    return AcrisLegalLot(borough=borough, block=block, lot=lot, partial_lot=partial)


def _doc(
    document_id: str,
    doc_type: str,
    indexed_lots: list[AcrisLegalLot],
    *,
    subject_partial: str | None = "E",
    crfn: str | None = None,
) -> AcrisDocument:
    return AcrisDocument(
        document_id=document_id,
        doc_type=doc_type,
        document_date="2016-08-09",
        recorded_datetime="2022-02-08",
        crfn=crfn,
        subject_partial_lot=subject_partial,
        indexed_lots=tuple(indexed_lots),
    )


def _result(documents: list[AcrisDocument], *, as_of: str | None = "2026-09-30"):
    return AcrisZoningLotIndexResult(
        subject_bbl=SUBJECT_BBL,
        subject_borough="4",
        subject_block="7334",
        subject_lot="70",
        documents=tuple(documents),
        as_of_date=as_of,
        correlation_id="synthetic",
        provenance={},
    )


SUBJECT_ENTIRE = _lot("4", "7334", "70", "E")
SUBJECT_PARTIAL = _lot("4", "7334", "70", "P")
SAME_BLOCK_LOT_1 = _lot("4", "7334", "1", "E")
OTHER_BLOCK_LOT = _lot("4", "7335", "1", "E")


# ---------------------------------------------------------------------------
# One test per classifier state + the input/expected table (DB232-R1).
# input state                               -> expected state / condition
# no ZONE (empty)                           -> NONE_FOUND, not conditional
# ZONE subject only (entire)                -> SINGLE_LOT_ONLY, not conditional
# ZONE subject + same-block lot             -> OTHER_LOTS_NAMED (a), conditional
# ZONE subject partial P (subject only)     -> OTHER_LOTS_NAMED (d), conditional
# ZONE subject + other-block lot only       -> SINGLE_LOT_ONLY (c), not conditional
# ZONE subject + same-block + other-block   -> OTHER_LOTS_NAMED (a) on same block only
# DECL/CERT only, several lots, no ZONE     -> NONE_FOUND (b), reminders only, not conditional
# not read / not checked                    -> NOT_READ / NOT_CHECKED
# ---------------------------------------------------------------------------
def test_none_found_when_no_zone_document() -> None:
    index = classify_zoning_lot_index(_result([]))
    assert index.state is ZoningLotIndexState.NONE_FOUND
    assert index.figures_conditional is False
    assert index.reasons == ()
    assert index.as_of_date == "2026-09-30"


def test_single_lot_only_when_zone_names_this_lot_alone() -> None:
    zone = _doc("Z1", "ZONE", [SUBJECT_ENTIRE], crfn="CRFN-Z1")
    index = classify_zoning_lot_index(_result([zone]))
    assert index.state is ZoningLotIndexState.SINGLE_LOT_ONLY
    assert index.figures_conditional is False
    assert index.other_same_block_lots == ()
    assert index.other_block_lots == ()
    assert [z.crfn for z in index.zone_documents] == ["CRFN-Z1"]


def test_other_lots_named_when_zone_names_a_same_block_lot() -> None:
    # Rule (a): a ZONE indexed against the subject AND lot 1 on the same block.
    zone = _doc("Z1", "ZONE", [SUBJECT_ENTIRE, SAME_BLOCK_LOT_1], crfn="CRFN-Z1")
    index = classify_zoning_lot_index(_result([zone]))
    assert index.state is ZoningLotIndexState.OTHER_LOTS_NAMED
    assert index.figures_conditional is True
    assert [lot.bbl for lot in index.other_same_block_lots] == ["4073340001"]
    assert index.other_block_lots == ()
    assert index.reasons == ("other_same_block_lots",)


def test_partial_lot_p_on_a_zone_is_conditional() -> None:
    # Rule (d): a ZONE whose subject row is partial_lot P, even with no other lot named.
    zone = _doc("Z1", "ZONE", [SUBJECT_PARTIAL], subject_partial="P", crfn="CRFN-Z1")
    index = classify_zoning_lot_index(_result([zone]))
    assert index.state is ZoningLotIndexState.OTHER_LOTS_NAMED
    assert index.figures_conditional is True
    assert index.reasons == ("partial_lot",)
    assert index.other_same_block_lots == ()


def test_another_block_zone_is_not_a_same_block_warning() -> None:
    # Rule (c): a lot on another block is listed for checking, never the same-block warning.
    zone = _doc("Z1", "ZONE", [SUBJECT_ENTIRE, OTHER_BLOCK_LOT], crfn="CRFN-Z1")
    index = classify_zoning_lot_index(_result([zone]))
    assert index.state is ZoningLotIndexState.SINGLE_LOT_ONLY
    assert index.figures_conditional is False
    assert index.other_same_block_lots == ()
    assert [lot.bbl for lot in index.other_block_lots] == ["4073350001"]


def test_mixed_document_triggers_only_on_same_block_lots() -> None:
    other_block_lot_5 = _lot("4", "7335", "5", "E")
    zone = _doc("Z1", "ZONE", [SUBJECT_ENTIRE, SAME_BLOCK_LOT_1, other_block_lot_5])
    index = classify_zoning_lot_index(_result([zone]))
    assert index.state is ZoningLotIndexState.OTHER_LOTS_NAMED
    assert [lot.bbl for lot in index.other_same_block_lots] == ["4073340001"]
    assert [lot.bbl for lot in index.other_block_lots] == ["4073350005"]
    assert index.reasons == ("other_same_block_lots",)


def test_decl_or_cert_only_is_reminder_only_no_condition() -> None:
    # Rule (b): DECL/CERT on several lots with no ZONE is a reminder only, never a condition.
    decl = _doc("D1", "DECL", [SUBJECT_ENTIRE, SAME_BLOCK_LOT_1], crfn="CRFN-D1")
    cert = _doc("C1", "CERT", [SUBJECT_ENTIRE, SAME_BLOCK_LOT_1], crfn="CRFN-C1")
    index = classify_zoning_lot_index(_result([decl, cert]))
    assert index.state is ZoningLotIndexState.NONE_FOUND
    assert index.figures_conditional is False
    assert index.zone_documents == ()
    assert {r.doc_type for r in index.reminder_documents} == {"DECL", "CERT"}
    assert index.other_same_block_lots == ()


def test_all_zone_documents_considered_never_a_latest() -> None:
    # Rule (e): two ZONEs - one subject-only, one naming lot 1 - still give OTHER_LOTS_NAMED.
    zone_alone = _doc("Z1", "ZONE", [SUBJECT_ENTIRE], crfn="CRFN-Z1")
    zone_multi = _doc("Z2", "ZONE", [SUBJECT_ENTIRE, SAME_BLOCK_LOT_1], crfn="CRFN-Z2")
    index = classify_zoning_lot_index(_result([zone_alone, zone_multi]))
    assert index.state is ZoningLotIndexState.OTHER_LOTS_NAMED
    assert {z.crfn for z in index.zone_documents} == {"CRFN-Z1", "CRFN-Z2"}
    assert [lot.bbl for lot in index.other_same_block_lots] == ["4073340001"]


def test_not_read_state() -> None:
    index = not_read(SUBJECT_BBL, reason="timeout", as_of_date="2026-09-30")
    assert index.state is ZoningLotIndexState.NOT_READ
    assert index.figures_conditional is True
    assert index.not_read_reason == "timeout"


def test_not_checked_state() -> None:
    index = not_checked()
    assert index.state is ZoningLotIndexState.NOT_CHECKED
    assert index.figures_conditional is False
    assert index.subject_bbl is None


# ---------------------------------------------------------------------------
# Benchmark replay (RECORDED data) -> OTHER_LOTS_NAMED naming lot 1 (S1).
# ---------------------------------------------------------------------------
def _benchmark_result() -> AcrisZoningLotIndexResult:
    subject_ids = sorted([
        "2018013000919001", "2018013000919002", "2022020201551001", "2022020201551002",
        "2022031600431001", "2024011000700001", "2024011000700002"])
    zdc_ids = sorted(["2022020201551001", "2022020201551002", "2022031600431001"])
    routes = {
        build_legals_by_lot_url(4, 7334, 70, limit=1000, offset=0):
            "acris_index_legals_8h5j-fqxa_lot_4-7334-70.json",
        build_master_url(subject_ids, limit=1000, offset=0):
            "acris_index_master_bnx9-e6tj_subject_docs.json",
        build_legals_by_documents_url(zdc_ids, limit=1000, offset=0):
            "acris_index_legals_8h5j-fqxa_zone_decl_cert.json",
        build_good_through_url(): "acris_index_legals_8h5j-fqxa_good_through.json",
    }

    def transport(url: str, headers: dict, timeout: float) -> TransportResponse:
        if url not in routes:
            raise AssertionError(f"unexpected url: {url}")
        return TransportResponse(200, (PACK / routes[url]).read_text(encoding="utf-8"))

    return fetch_zoning_lot_index(
        SUBJECT_BBL, transport=transport, sleep=lambda _s: None,
        clock=lambda: datetime(2026, 10, 11, tzinfo=UTC), correlation_id="benchmark",
    )


def test_benchmark_replay_names_lot_1_with_crfn() -> None:
    index = classify_zoning_lot_index(_benchmark_result())
    assert index.state is ZoningLotIndexState.OTHER_LOTS_NAMED
    assert [lot.bbl for lot in index.other_same_block_lots] == ["4073340001"]
    assert [z.crfn for z in index.zone_documents] == ["2022000059134"]
    assert index.zone_documents[0].recorded_datetime == "2022-02-08"
    assert {r.doc_type for r in index.reminder_documents} == {"CERT", "DECL"}
    assert index.as_of_date == "2026-09-30"


# ---------------------------------------------------------------------------
# Study-inputs seam (no allowed api test file in part A - documented here).
# ---------------------------------------------------------------------------
_STUDY_URL = f"/api/v1/properties/{NORTHERN_BBL}/study"


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    get_rate_limiter().reset()
    yield
    get_rate_limiter().reset()


def _client(provider) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_study_inputs_provider] = lambda: provider
    return TestClient(app)


def _other_lots_named_provider(canonical_bbl: str, correlation_id: str) -> ZoningLotIndex:
    return classify_zoning_lot_index(_benchmark_result())


def test_assemble_defaults_to_not_checked_and_is_inert() -> None:
    baseline = assemble_study_inputs(
        _northern_fetcher(NORTHERN_BBL, "cid"), clock=FIXED_CLOCK, env=LANE_B_ON
    )
    assert baseline.zoning_lot_index.state is ZoningLotIndexState.NOT_CHECKED

    # Explicit None == the default; threading None changes no other field.
    threaded_none = assemble_study_inputs(
        _northern_fetcher(NORTHERN_BBL, "cid"), clock=FIXED_CLOCK, env=LANE_B_ON,
        zoning_lot_index=None,
    )
    assert threaded_none.site_facts == baseline.site_facts
    assert threaded_none.lot_choice == baseline.lot_choice
    assert threaded_none.site == baseline.site
    assert threaded_none.zoning_lot_index.state is ZoningLotIndexState.NOT_CHECKED

    # Threading a populated index changes ONLY the carrier, never the emitted site facts.
    threaded_populated = assemble_study_inputs(
        _northern_fetcher(NORTHERN_BBL, "cid"), clock=FIXED_CLOCK, env=LANE_B_ON,
        zoning_lot_index=classify_zoning_lot_index(_benchmark_result()),
    )
    assert threaded_populated.site_facts == baseline.site_facts
    assert threaded_populated.zoning_lot_index.state is ZoningLotIndexState.OTHER_LOTS_NAMED


def test_route_body_identical_whether_or_not_index_bound(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_STUDY_READ_ENABLED_ENV_VAR, "1")
    provider_unbound = pluto_study_inputs_provider(
        _northern_fetcher, clock=FIXED_CLOCK, env=LANE_B_ON
    )
    provider_bound = pluto_study_inputs_provider(
        _northern_fetcher, clock=FIXED_CLOCK, env=LANE_B_ON,
        zoning_lot_index_provider=_other_lots_named_provider,
    )
    body_unbound = _client(provider_unbound).get(_STUDY_URL).json()
    body_bound = _client(provider_bound).get(_STUDY_URL).json()
    # The carrier is inert: binding a populated OTHER_LOTS_NAMED index changes NO route output.
    assert body_bound == body_unbound
    # And it matches the existing suite's provider body (the pre-wiring study read).
    assert body_unbound == _client(_northern_provider()).get(_STUDY_URL).json()


# ---------------------------------------------------------------------------
# The LIVE ACRIS provider: success classifies; failure -> NOT_READ (never 503/NONE_FOUND).
# ---------------------------------------------------------------------------
def test_live_provider_classifies_on_success() -> None:
    subject_ids = sorted([
        "2018013000919001", "2018013000919002", "2022020201551001", "2022020201551002",
        "2022031600431001", "2024011000700001", "2024011000700002"])
    zdc_ids = sorted(["2022020201551001", "2022020201551002", "2022031600431001"])
    routes = {
        build_legals_by_lot_url(4, 7334, 70, limit=1000, offset=0):
            "acris_index_legals_8h5j-fqxa_lot_4-7334-70.json",
        build_master_url(subject_ids, limit=1000, offset=0):
            "acris_index_master_bnx9-e6tj_subject_docs.json",
        build_legals_by_documents_url(zdc_ids, limit=1000, offset=0):
            "acris_index_legals_8h5j-fqxa_zone_decl_cert.json",
        build_good_through_url(): "acris_index_legals_8h5j-fqxa_good_through.json",
    }

    def transport(url: str, headers: dict, timeout: float) -> TransportResponse:
        return TransportResponse(200, (PACK / routes[url]).read_text(encoding="utf-8"))

    provider = acris_zoning_lot_index_provider(transport=transport)
    index = provider(SUBJECT_BBL, "cid")
    assert index.state is ZoningLotIndexState.OTHER_LOTS_NAMED


def test_live_provider_maps_schema_drift_to_not_read() -> None:
    import json

    def transport(url: str, headers: dict, timeout: float) -> TransportResponse:
        return TransportResponse(400, json.dumps({"errorCode": "query.soql.no-such-column"}))

    index = acris_zoning_lot_index_provider(transport=transport)(SUBJECT_BBL, "cid")
    assert index.state is ZoningLotIndexState.NOT_READ
    assert index.not_read_reason == "schema_drift"
    assert index.figures_conditional is True


def test_live_provider_maps_malformed_bbl_to_not_read() -> None:
    def transport(url: str, headers: dict, timeout: float) -> TransportResponse:
        raise AssertionError("no request should be made for a malformed bbl")

    index = acris_zoning_lot_index_provider(transport=transport)("not-a-bbl", "cid")
    assert index.state is ZoningLotIndexState.NOT_READ
    assert index.not_read_reason == "validation_error"
