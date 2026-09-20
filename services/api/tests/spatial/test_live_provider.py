"""M2-T020 live spatial-substrate provider tests (scenarios S1-S3).

Offline and deterministic: connector DOUBLES are injected by monkeypatching the
module's ``_ACTIVE_FETCHERS`` seam, so ``default_live_substrate`` - the exact
callable behind the route's DEFAULT ``get_spatial_substrate_provider()`` - is
exercised without FastAPI dependency overrides and without the network. The
happy-path double feeds the REAL accepted connector fixtures (ZF03 nyzd R3-2
polygon) through the accepted MapPLUTO geometry validator, mirroring
tests/spatial/test_spatial_intersection.py.

* S1 default-off parity: flag unset/unknown -> None with ZERO connector calls.
* S2 live path: flag on + doubles -> a real LotIntersectionRecord composed by
  the accepted engine (confident R3-2, ZTLDB crosscheck agreement).
* S3 fail-safe: every connector error / partial page / empty assignment ->
  None (absent substrate), and engine review classes pass through UNMODIFIED -
  never a fabricated or upgraded substrate.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.connectors.condo_base_lot import (
    OUTCOME_ERROR,
    OUTCOME_MULTI_LOT,
    OUTCOME_NOT_CONDO_BILLING,
    OUTCOME_RESOLVED_SINGLE,
    OUTCOME_UNRESOLVED,
    CondoResolution,
)
from app.connectors.mappluto_geometry_arcgis import (
    CRS_STAMP,
    analyze_lot_geometry,
)
from app.connectors.mappluto_geometry_arcgis import (
    UpstreamError as MapPlutoUpstreamError,
)
from app.connectors.zoning_features_arcgis import (
    RateLimitedError as ZoningFeaturesRateLimitedError,
)
from app.connectors.ztldb_soda import UpstreamError as ZtldbUpstreamError
from app.spatial import live_provider
from app.spatial.live_provider import (
    CONDO_BASE_LOT_UNRESOLVED_CAUSE,
    LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR,
    LiveSpatialFetchers,
    LiveSubstrateResult,
    _candidate_layer_queries,
    build_live_substrate,
    build_live_substrate_resolved,
    build_substrate_substitution_stamp,
    default_live_substrate,
    default_live_substrate_resolved,
    live_spatial_provider_enabled,
)
from app.spatial.models import (
    LOT_INVALID_GEOMETRY_REVIEW,
    LOT_SINGLE_DISTRICT_CONFIDENT,
    XCHK_AGREEMENT,
    LotIntersectionRecord,
)

FIX = Path(__file__).resolve().parents[1] / "fixtures"
BBL = "1000010010"
CID = "cid-live-provider-test"

# Deep interior point of the real ZF03 R3-2 polygon (same probe the accepted
# spatial acceptance pack uses).
_R32_X, _R32_Y = 997482.04, 163293.94


# ---------------------------------------------------------------------------
# Doubles (connector-result-shaped, per the accepted adapter contract)
# ---------------------------------------------------------------------------


def _fixture_features(relpath: str) -> list:
    doc = json.loads((FIX / relpath).read_text(encoding="utf-8"))
    return json.loads(doc["response_body_raw"])["features"]


def _r32_features() -> list:
    return _fixture_features("zoning_features/ZF03_query_nyzd_single_R3-2.json")


def _layer_result(features: list, *, layer: str = "nyzd", exceeded: bool = False):
    return SimpleNamespace(
        layer=layer,
        features=features,
        object_id_field="OBJECTID",
        normalized_digest="digest-zf03",
        retrieved_at="2026-09-06T00:00:00Z",
        source_data_last_edited="2026-07-01T00:00:00Z",
        exceeded_transfer_limit=exceeded,
    )


def _lot_result(*, half: float = 25.0):
    """A single-feature lot whose square sits deep inside the real R3-2
    polygon, assessed by the accepted MapPLUTO geometry validator."""
    x, y = _R32_X, _R32_Y
    ring = [
        [x - half, y - half],
        [x - half, y + half],
        [x + half, y + half],
        [x + half, y - half],
        [x - half, y - half],
    ]
    assessment = analyze_lot_geometry({"rings": [ring]}, crs=dict(CRS_STAMP))
    assert assessment.canonical_geometry is not None
    return SimpleNamespace(
        outcome="single_feature",
        geometry=assessment,
        review_required=False,
        requested_bbl=BBL,
        area_sq_ft=assessment.area_sq_ft,
        retrieved_at="2026-09-06T00:00:00Z",
        normalized_digest="digest-lot",
        source_data_last_edited="2026-07-01T00:00:00Z",
        crs=dict(CRS_STAMP),
    )


def _lot_result_no_feature():
    return SimpleNamespace(
        outcome="no_feature",
        geometry=None,
        review_required=False,
        requested_bbl=BBL,
        area_sq_ft=None,
        retrieved_at="2026-09-06T00:00:00Z",
        normalized_digest=None,
        source_data_last_edited=None,
        crs=dict(CRS_STAMP),
    )


def _ztldb_result(*district_values: str):
    return SimpleNamespace(
        status="ok" if district_values else "no_record",
        zoning_assignment=(
            {
                "zoning_districts": [
                    {"position": i + 1, "column": f"zoning_district_{i + 1}", "value": v}
                    for i, v in enumerate(district_values)
                ],
                "commercial_overlays": [],
                "special_districts": [],
                "limited_height_district": None,
            }
            if district_values
            else None
        ),
        dataset_version="rows-2026-09-01",
        source_freshness={"rows_updated_at": "2026-09-01T00:00:00Z"},
    )


class RecordingFetchers:
    """LiveSpatialFetchers double that records every call it receives."""

    def __init__(self, *, lot=None, ztldb=None, layer=None):
        self.lot_calls: list = []
        self.ztldb_calls: list = []
        self.layer_calls: list = []
        self._lot = lot if lot is not None else _lot_result()
        self._ztldb = ztldb if ztldb is not None else _ztldb_result("R3-2")
        self._layer = layer if layer is not None else _layer_result(_r32_features())

    def _resolve(self, value):
        if isinstance(value, Exception):
            raise value
        return value

    def suite(self) -> LiveSpatialFetchers:
        def fetch_lot(bbl, cid):
            self.lot_calls.append((bbl, cid))
            return self._resolve(self._lot)

        def fetch_ztldb(bbl, cid):
            self.ztldb_calls.append((bbl, cid))
            return self._resolve(self._ztldb)

        def fetch_district_layer(layer, field_name, value, cid):
            self.layer_calls.append((layer, field_name, value, cid))
            return self._resolve(self._layer)

        return LiveSpatialFetchers(
            fetch_lot=fetch_lot,
            fetch_ztldb=fetch_ztldb,
            fetch_district_layer=fetch_district_layer,
        )


def _install(monkeypatch, fetchers: LiveSpatialFetchers) -> None:
    monkeypatch.setattr(live_provider, "_ACTIVE_FETCHERS", fetchers)


# ---------------------------------------------------------------------------
# Condo pre-lookup doubles (M5-T045). The condo seam runs BEFORE the zoning-lot
# lookup; these fake it so tests stay offline. A recording resolver captures the
# BBL it was asked to resolve, so a substitution vs pass-through is observable.
# ---------------------------------------------------------------------------


class _RecordingCondo:
    """Condo resolver double returning a fixed CondoResolution and recording the
    BBLs it was asked to resolve."""

    def __init__(self, outcome):
        self._outcome = outcome
        self.calls: list[tuple[str, str]] = []

    def __call__(self, bbl: str, correlation_id: str):
        self.calls.append((bbl, correlation_id))
        return self._outcome


def _condo_pass_through(bbl: str):
    return CondoResolution(
        outcome=OUTCOME_NOT_CONDO_BILLING, input_bbl=bbl, correlation_id=CID
    )


def _install_condo(monkeypatch, resolver) -> None:
    monkeypatch.setattr(live_provider, "_ACTIVE_CONDO_RESOLVER", resolver)


def _fail_safe_lines(caplog) -> list[str]:
    """The provider's fail-safe WARNING lines (payload-only log contract)."""
    return [
        record.getMessage()
        for record in caplog.records
        if record.name == "app.spatial.live_provider"
        and "fail_safe" in record.getMessage()
    ]


# ---------------------------------------------------------------------------
# Flag semantics (fail-safe enablement, mirrors app.config)
# ---------------------------------------------------------------------------


def test_flag_absent_empty_or_unknown_is_disabled() -> None:
    assert live_spatial_provider_enabled(env={}) is False
    for raw in ("", "0", "false", "off", "no", "maybe", "enabled"):
        assert live_spatial_provider_enabled(
            env={LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR: raw}
        ) is False, raw


def test_flag_explicit_true_tokens_enable() -> None:
    for raw in ("1", "true", "TRUE", " yes ", "On"):
        assert live_spatial_provider_enabled(
            env={LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR: raw}
        ) is True, raw


# ---------------------------------------------------------------------------
# S1: default OFF == current behavior (None, zero connector calls)
# ---------------------------------------------------------------------------


def test_s1_default_off_returns_none_without_any_connector_call(monkeypatch) -> None:
    monkeypatch.delenv(LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR, raising=False)
    recording = RecordingFetchers()
    _install(monkeypatch, recording.suite())
    assert default_live_substrate(BBL, CID) is None
    # Counts asserted AFTER the return: an exploding guard raised inside
    # build_live_substrate would be swallowed by its fail-safe except and the
    # None would look like success; a recorded call cannot be hidden.
    assert recording.ztldb_calls == []
    assert recording.lot_calls == []
    assert recording.layer_calls == []


def test_s1_unknown_token_stays_off(monkeypatch) -> None:
    monkeypatch.setenv(LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR, "maybe")
    recording = RecordingFetchers()
    _install(monkeypatch, recording.suite())
    assert default_live_substrate(BBL, CID) is None
    assert recording.ztldb_calls == []
    assert recording.lot_calls == []
    assert recording.layer_calls == []


# ---------------------------------------------------------------------------
# S2: flag ON + doubles -> real engine substrate through the DEFAULT callable
# ---------------------------------------------------------------------------


def test_s2_live_path_composes_confident_real_substrate(monkeypatch) -> None:
    monkeypatch.setenv(LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR, "1")
    recording = RecordingFetchers()
    _install(monkeypatch, recording.suite())

    record = default_live_substrate(BBL, CID)

    assert isinstance(record, LotIntersectionRecord)
    assert record.bbl == BBL
    assert record.lot_overall_class == LOT_SINGLE_DISTRICT_CONFIDENT
    assert record.pairs[0].district_label == "R3-2"
    assert record.crosscheck.outcome == XCHK_AGREEMENT
    # The candidate query came from the OFFICIAL ZTLDB assignment.
    assert recording.ztldb_calls == [(BBL, CID)]
    assert recording.lot_calls == [(BBL, CID)]
    assert recording.layer_calls == [("nyzd", "ZONEDIST", "R3-2", CID)]


def test_candidate_queries_dedupe_and_preserve_official_order() -> None:
    assignment = {
        "zoning_districts": [
            {"position": 1, "column": "zoning_district_1", "value": "R6"},
            {"position": 2, "column": "zoning_district_2", "value": "R6"},
            {"position": 3, "column": "zoning_district_3", "value": "PARK"},
        ],
        "commercial_overlays": [
            {"position": 1, "column": "commercial_overlay_1", "value": "C1-3"},
        ],
        "special_districts": [
            {
                "position": 1,
                "column": "special_district_1",
                "value": "MiD/TA",
                "components": ["MiD", "TA"],
                "tie": True,
            },
        ],
        "limited_height_district": "LH-1A",
    }
    assert _candidate_layer_queries(assignment) == [
        ("nyzd", "ZONEDIST", "R6"),
        ("nyzd", "ZONEDIST", "PARK"),
        ("nyco", "OVERLAY", "C1-3"),
        ("nysp", "SDLBL", "MiD"),
        ("nysp", "SDLBL", "TA"),
        ("nylh", "LHLBL", "LH-1A"),
    ]
    assert _candidate_layer_queries(None) == []
    assert _candidate_layer_queries({}) == []


# ---------------------------------------------------------------------------
# S3: connector failure / partial data -> absent substrate (None), and engine
# review outcomes pass through unmodified. Never fabricated, never raised.
# ---------------------------------------------------------------------------


# The exception messages are CANARIES: the payload-only log contract (M1-T002
# G5 F5) requires the typed error CLASS + correlation id in the fail-safe log
# and forbids str(exc), so each canary must never appear in any log line.
@pytest.mark.parametrize(
    ("kwargs", "expected_error_type", "expected_counts"),
    [
        (
            {"ztldb": ZtldbUpstreamError("canary-ztldb-detail", correlation_id=CID)},
            "UpstreamError",
            (1, 0, 0),
        ),
        (
            {"lot": MapPlutoUpstreamError("canary-lot-detail", correlation_id=CID)},
            "UpstreamError",
            (1, 1, 0),
        ),
        (
            {
                "layer": ZoningFeaturesRateLimitedError(
                    "canary-layer-detail", correlation_id=CID
                )
            },
            "RateLimitedError",
            (1, 1, 1),
        ),
        ({"lot": ValueError("canary-defect-detail")}, "ValueError", (1, 1, 0)),
    ],
    ids=["ztldb-typed-error", "lot-typed-error", "layer-typed-error", "unexpected"],
)
def test_s3_any_connector_failure_yields_absent_substrate(
    kwargs, expected_error_type, expected_counts, caplog
) -> None:
    recording = RecordingFetchers(**kwargs)
    with caplog.at_level(logging.WARNING, logger="app.spatial.live_provider"):
        result = build_live_substrate(BBL, CID, fetchers=recording.suite())
    assert result is None

    # Short-circuit proven by counts AFTER the return (fetch order is ztldb ->
    # lot -> layers): the failing connector was called exactly once and every
    # connector downstream of it was never consulted.
    assert (
        len(recording.ztldb_calls),
        len(recording.lot_calls),
        len(recording.layer_calls),
    ) == expected_counts

    # Exactly one fail-safe line: typed error CLASS + correlation id, no canary.
    lines = _fail_safe_lines(caplog)
    assert len(lines) == 1
    assert "event=connector_error" in lines[0]
    assert f"error_type={expected_error_type}" in lines[0]
    assert f"correlation_id={CID}" in lines[0]
    assert "canary-" not in lines[0]


def test_s3_no_record_assignment_yields_absent_substrate(caplog) -> None:
    recording = RecordingFetchers(ztldb=_ztldb_result())  # no_record, no assignment
    with caplog.at_level(logging.WARNING, logger="app.spatial.live_provider"):
        assert build_live_substrate(BBL, CID, fetchers=recording.suite()) is None
    # No candidates -> the lot and layer connectors are never consulted.
    assert recording.ztldb_calls == [(BBL, CID)]
    assert recording.lot_calls == []
    assert recording.layer_calls == []
    lines = _fail_safe_lines(caplog)
    assert len(lines) == 1
    assert "event=no_candidate_districts" in lines[0]
    assert "error_type=none" in lines[0]
    assert f"correlation_id={CID}" in lines[0]


def test_s3_partial_district_page_yields_absent_substrate(caplog) -> None:
    # TWO candidate districts, but the FIRST layer page is transfer-limited: the
    # composition must stop there, never issuing the second layer query.
    recording = RecordingFetchers(
        ztldb=_ztldb_result("R3-2", "R6"),
        layer=_layer_result(_r32_features(), exceeded=True),
    )
    with caplog.at_level(logging.WARNING, logger="app.spatial.live_provider"):
        assert build_live_substrate(BBL, CID, fetchers=recording.suite()) is None
    assert recording.ztldb_calls == [(BBL, CID)]
    assert recording.lot_calls == [(BBL, CID)]
    assert recording.layer_calls == [("nyzd", "ZONEDIST", "R3-2", CID)]
    lines = _fail_safe_lines(caplog)
    assert len(lines) == 1
    assert "event=district_page_partial" in lines[0]
    assert "error_type=none" in lines[0]
    assert f"correlation_id={CID}" in lines[0]


def test_s3_empty_label_query_flows_to_engine_not_fabricated() -> None:
    """A well-formed EMPTY label query is legitimate official data: the engine
    (not this module) classifies the resulting evidence, and with no matching
    nyzd polygon it must NOT produce a confident single-district record."""
    recording = RecordingFetchers(layer=_layer_result([]))
    record = build_live_substrate(BBL, CID, fetchers=recording.suite())
    assert isinstance(record, LotIntersectionRecord)
    assert record.lot_overall_class != LOT_SINGLE_DISTRICT_CONFIDENT


def test_s3_lot_no_feature_passes_engine_review_class_through() -> None:
    recording = RecordingFetchers(lot=_lot_result_no_feature())
    record = build_live_substrate(BBL, CID, fetchers=recording.suite())
    assert isinstance(record, LotIntersectionRecord)
    assert record.lot_overall_class == LOT_INVALID_GEOMETRY_REVIEW


# ---------------------------------------------------------------------------
# M5-T033 (D-059-R004): the deployed spatial_intersection_absent root cause,
# reproduced at the PROVIDER boundary for both D-059 parcels. The route-level
# reason (spatial_intersection_absent) is IDENTICAL for a disabled flag and for a
# live connector failure - both return None (absent substrate) - so the response
# body alone cannot tell them apart. Here we pin the PROVIDER-level signatures
# that help SEPARATE a future deploy regression from a data failure: branch A
# (flag off) makes ZERO connector calls and NO provider fail-safe log line;
# branch B (flag on + failure) makes calls and logs exactly one connector_error
# line. These call-count / log signatures - read at the runtime boundary, not
# from the response body - are the reliable discriminators. Uniform absence
# across a known-good control and fast latency are SUGGESTIVE observations, never
# decisive: a SHARED connector failure with the flag ON is also uniform and fast
# (reproduced by test_m5t033_shared_connector_failure_is_uniform_absent_flag_on),
# so uniformity alone cannot prove the flag was off. The authoritative runtime
# confirmation is the owner dashboard flag reading plus the correlated typed
# connector logs, not this file.
# ---------------------------------------------------------------------------

# The two D-059-R004 named parcels (BBL 3022647515 is the requirement's parcel;
# 3052960043 is the D-059 start parcel). The flag-off reason is BBL-independent.
_D059_BBLS = ("3052960043", "3022647515")


@pytest.mark.parametrize("bbl", _D059_BBLS)
def test_m5t033_flag_off_absent_for_every_bbl_zero_calls_no_log(
    bbl, monkeypatch, caplog
) -> None:
    """Branch A (deploy regression): with LIVE_SPATIAL_PROVIDER_ENABLED unset the
    DEFAULT provider yields no substrate for EVERY BBL, short-circuiting before any
    network I/O - the uniform-absent signature captured live. Proven by ZERO
    connector calls AND ZERO provider fail-safe log lines (checked after return)."""
    monkeypatch.delenv(LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR, raising=False)
    recording = RecordingFetchers()  # healthy doubles that must never be called
    _install(monkeypatch, recording.suite())
    with caplog.at_level(logging.WARNING, logger="app.spatial.live_provider"):
        assert default_live_substrate(bbl, CID) is None
    assert recording.ztldb_calls == []
    assert recording.lot_calls == []
    assert recording.layer_calls == []
    assert _fail_safe_lines(caplog) == []


@pytest.mark.parametrize("bbl", _D059_BBLS)
def test_m5t033_flag_on_connector_failure_absent_but_calls_and_logs(
    bbl, monkeypatch, caplog
) -> None:
    """Branch B (live data failure): flag on + an injected connector failure also
    returns None, but the DISTINGUISHING per-parcel signature is present - the
    ztldb connector WAS consulted for this BBL and exactly one payload-only
    connector_error line was logged (never the canary detail string)."""
    monkeypatch.setenv(LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR, "1")
    recording = RecordingFetchers(
        ztldb=ZtldbUpstreamError("canary-m5t033", correlation_id=CID)
    )
    _install(monkeypatch, recording.suite())
    # Stub the condo pre-lookup to pass-through so the ztldb-error signature is
    # isolated: parcel 3022647515 is a billing lot, but this test pins the ztldb
    # failure branch, not condo resolution (covered by the M5-T045 tests below).
    _install_condo(monkeypatch, lambda b, c: _condo_pass_through(b))
    with caplog.at_level(logging.WARNING, logger="app.spatial.live_provider"):
        assert default_live_substrate(bbl, CID) is None
    assert recording.ztldb_calls == [(bbl, CID)]
    lines = _fail_safe_lines(caplog)
    assert len(lines) == 1
    assert "event=connector_error" in lines[0]
    assert "error_type=UpstreamError" in lines[0]
    assert "canary-m5t033" not in lines[0]


def test_m5t033_flag_on_healthy_connectors_resolves_not_absent(monkeypatch) -> None:
    """Flag on + HEALTHY connectors -> a real confident substrate, NOT None. This
    shows the flag-on branch CAN resolve a district when its connectors succeed; it
    does NOT prove that uniform absence implies the flag was off. A SHARED connector
    failure (see test_m5t033_shared_connector_failure_is_uniform_absent_flag_on)
    also yields uniform absence with the flag ON, so uniformity is only a suggestive
    signal - the runtime flag reading and the typed connector logs are decisive."""
    monkeypatch.setenv(LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR, "1")
    recording = RecordingFetchers()
    _install(monkeypatch, recording.suite())
    record = default_live_substrate(_D059_BBLS[0], CID)
    assert isinstance(record, LotIntersectionRecord)
    assert record.lot_overall_class == LOT_SINGLE_DISTRICT_CONFIDENT
    assert recording.ztldb_calls == [(_D059_BBLS[0], CID)]


# The known-good control parcel the live capture also saw return absent
# (350 Fifth Ave, Manhattan; resolves cleanly in GeoSearch).
_CONTROL_BBL = "1008350041"


def test_m5t033_shared_connector_failure_is_uniform_absent_flag_on(
    monkeypatch, caplog
) -> None:
    """Counterexample to "uniform absence proves the flag is off": with the flag ON
    and a SHARED connector failure (the SAME injected ZTLDB error for every parcel),
    the provider returns None UNIFORMLY across both D-059 parcels AND the known-good
    control - the exact uniform-across-a-control shape the live capture recorded. So
    flag-off is not the only way to get uniform absence; a shared connector/network
    fault is uniform (and fast) too. What still separates this flag-ON branch from
    flag-off: every parcel WAS consulted (a recorded connector call) and logged
    exactly one payload-only connector_error line - signatures read at the runtime
    boundary, never from the response body."""
    monkeypatch.setenv(LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR, "1")
    # Stub the condo pre-lookup to pass-through so every parcel reaches ztldb and
    # the shared-fault signature is what is under test (billing lot 3022647515
    # included); condo resolution itself is covered by the M5-T045 tests below.
    _install_condo(monkeypatch, lambda b, c: _condo_pass_through(b))
    bbls = (*_D059_BBLS, _CONTROL_BBL)
    results = []
    with caplog.at_level(logging.WARNING, logger="app.spatial.live_provider"):
        for bbl in bbls:
            recording = RecordingFetchers(
                ztldb=ZtldbUpstreamError("canary-shared", correlation_id=CID)
            )
            _install(monkeypatch, recording.suite())
            results.append(default_live_substrate(bbl, CID))
            # Flag ON: the connector WAS consulted for this parcel (unlike the
            # zero-call flag-off branch), proving the failure is a live fault.
            assert recording.ztldb_calls == [(bbl, CID)]
    # Uniform absence across both named parcels and the control - with the flag ON.
    assert results == [None, None, None]
    # One connector_error line per parcel; the canary detail never leaks.
    lines = _fail_safe_lines(caplog)
    assert len(lines) == len(bbls)
    assert all("event=connector_error" in line for line in lines)
    assert all("canary-shared" not in line for line in lines)


# ---------------------------------------------------------------------------
# M5-T045: condo billing-BBL -> base-lot PRE-LOOKUP wiring (AS-1, AS-3..AS-5).
# The condo step runs BEFORE the zoning-lot lookup; a resolved single base lot
# substitutes for the input, and multi-lot / unresolved / typed-error outcomes
# fail-safe to None (absent substrate). Divergent zoning is never collapsed and
# a substrate is never fabricated. Doubles keep the tests offline.
# ---------------------------------------------------------------------------

_BILLING_BBL = "3022647515"  # Brooklyn billing lot 7515 (DB-002 worked case)
_BASE_LOT = "3022640032"


def _condo(outcome, **kwargs) -> CondoResolution:
    return CondoResolution(
        outcome=outcome, input_bbl=_BILLING_BBL, correlation_id=CID, **kwargs
    )


def test_m5t045_as1_resolved_single_runs_pipeline_on_base_lot(caplog) -> None:
    condo = _RecordingCondo(
        _condo(
            OUTCOME_RESOLVED_SINGLE,
            base_bbls=(_BASE_LOT,),
            resolved_base_bbl=_BASE_LOT,
            condo_key="301313",
        )
    )
    recording = RecordingFetchers()
    with caplog.at_level(logging.INFO, logger="app.spatial.live_provider"):
        record = build_live_substrate(
            _BILLING_BBL, CID, fetchers=recording.suite(), condo_resolver=condo
        )
    # A real substrate composed by the engine, with the zoning-lot lookup run on
    # the BASE lot, not the billing BBL.
    assert isinstance(record, LotIntersectionRecord)
    assert condo.calls == [(_BILLING_BBL, CID)]
    assert recording.ztldb_calls == [(_BASE_LOT, CID)]
    assert recording.lot_calls == [(_BASE_LOT, CID)]
    # The substitution is recorded, payload-only (digit BBLs + our correlation id).
    info = [
        r.getMessage()
        for r in caplog.records
        if r.name == "app.spatial.live_provider" and "condo_resolution" in r.getMessage()
    ]
    assert len(info) == 1
    assert f"input_bbl={_BILLING_BBL}" in info[0]
    assert f"base_bbl={_BASE_LOT}" in info[0]
    assert f"correlation_id={CID}" in info[0]


@pytest.mark.parametrize(
    ("outcome", "kwargs", "event"),
    [
        (
            OUTCOME_MULTI_LOT,
            {"base_bbls": (_BASE_LOT, "3022640033")},
            "event=condo_multi_lot_set",
        ),
        (OUTCOME_UNRESOLVED, {}, "event=condo_unresolved"),
        (OUTCOME_ERROR, {"error_type": "rate_limited"}, "event=condo_error"),
    ],
    ids=["multi-lot", "unresolved", "typed-error"],
)
def test_m5t045_condo_fail_safe_yields_absent_substrate_zero_lookups(
    outcome, kwargs, event, caplog
) -> None:
    condo = _RecordingCondo(_condo(outcome, **kwargs))
    recording = RecordingFetchers()  # healthy doubles that must never be reached
    with caplog.at_level(logging.WARNING, logger="app.spatial.live_provider"):
        result = build_live_substrate(
            _BILLING_BBL, CID, fetchers=recording.suite(), condo_resolver=condo
        )
    assert result is None
    # No zoning-lot lookup happens on a fail-safe condo outcome (short-circuit).
    assert condo.calls == [(_BILLING_BBL, CID)]
    assert recording.ztldb_calls == []
    assert recording.lot_calls == []
    assert recording.layer_calls == []
    lines = _fail_safe_lines(caplog)
    assert len(lines) == 1
    assert event in lines[0]
    assert f"correlation_id={CID}" in lines[0]


def test_m5t045_non_condo_passthrough_default_resolver_byte_identical() -> None:
    """A non-condo BBL uses the DEFAULT condo seam (no double): classification is
    pure, so it passes through with ZERO condo I/O and the pipeline runs on the
    input BBL unchanged - byte-identical to the pre-M5-T045 behavior."""
    recording = RecordingFetchers()
    record = build_live_substrate(BBL, CID, fetchers=recording.suite())
    assert isinstance(record, LotIntersectionRecord)
    assert record.bbl == BBL
    assert recording.ztldb_calls == [(BBL, CID)]
    assert recording.lot_calls == [(BBL, CID)]


# ---------------------------------------------------------------------------
# M5-T058: carry the CondoResolution ACROSS the substrate seam so the resolution
# can be STAMPED onto the evaluation document (build_live_substrate_resolved ->
# LiveSubstrateResult) instead of being discarded as a log line, and name a
# condo-caused absent substrate honestly (condo_base_lot_unresolved) rather than
# the generic spatial_intersection_absent. No base lot is ever auto-picked on a
# multi-lot / unresolved outcome (D-078-R002). build_live_substrate stays the
# byte-identical object|None seam the other three route consumers call.
# ---------------------------------------------------------------------------


def _resolved_single_resolution() -> CondoResolution:
    """A resolved-single CondoResolution with EVERY provenance field populated,
    so the stamp's byte-match against the record is unambiguous (AS-5)."""
    return _condo(
        OUTCOME_RESOLVED_SINGLE,
        base_bbls=(_BASE_LOT,),
        resolved_base_bbl=_BASE_LOT,
        condo_key="301313",
        resolution_path="dtm_condo_soda_single_base_lot",
        source_id="dof_dtm_condo",
        dataset_ids=("dtm-condo-2026-09",),
        retrieved_at="2026-09-06T00:00:00Z",
    )


def test_m5t058_as1_resolved_single_carries_stamp_and_provenance() -> None:
    """AS-1/AS-5: a resolved single base lot rides WITH the substrate as a
    substrate_substitution stamp, the pipeline runs on the BASE lot exactly once,
    and every stamp field byte-matches the CondoResolution (nothing invented)."""
    resolution = _resolved_single_resolution()
    condo = _RecordingCondo(resolution)
    recording = RecordingFetchers()
    result = build_live_substrate_resolved(
        _BILLING_BBL, CID, fetchers=recording.suite(), condo_resolver=condo
    )
    assert isinstance(result, LiveSubstrateResult)
    # A real substrate composed on the BASE lot, resolution carried (not discarded).
    assert isinstance(result.substrate, LotIntersectionRecord)
    assert result.fail_safe_cause is None
    assert result.resolution is resolution
    # Single condo-resolver call; the zoning-lot lookup runs on the BASE lot.
    assert condo.calls == [(_BILLING_BBL, CID)]
    assert recording.ztldb_calls == [(_BASE_LOT, CID)]
    assert recording.lot_calls == [(_BASE_LOT, CID)]
    # The stamp equals the pure builder's output for this resolution: every
    # provenance field traces to the record, nothing defaulted or fabricated.
    stamp = result.substitution_stamp
    assert stamp is not None
    assert stamp == build_substrate_substitution_stamp(_BILLING_BBL, resolution)
    assert stamp["entered_bbl"] == _BILLING_BBL
    assert stamp["analyzed_bbl"] == _BASE_LOT
    assert stamp["condo_key"] == "301313"
    assert stamp["resolution_path"] == "dtm_condo_soda_single_base_lot"
    assert stamp["source_id"] == "dof_dtm_condo"
    assert stamp["dataset_ids"] == ["dtm-condo-2026-09"]
    assert isinstance(stamp["dataset_ids"], list)
    assert stamp["retrieved_at"] == "2026-09-06T00:00:00Z"
    assert isinstance(stamp["note"], str) and stamp["note"]
    # Mixed-substrate visibility: base lot supplies geometry, billing lot identity.
    assert stamp["mixed_substrate"]["lot_facts_substrate"] == "analyzed_base_lot"
    assert stamp["mixed_substrate"]["identity_facts_substrate"] == "entered_billing_lot"
    assert isinstance(stamp["mixed_substrate"]["note"], str) and stamp["mixed_substrate"]["note"]


@pytest.mark.parametrize(
    ("outcome", "kwargs"),
    [
        (OUTCOME_MULTI_LOT, {"base_bbls": (_BASE_LOT, "3022640033")}),
        (OUTCOME_UNRESOLVED, {}),
        (OUTCOME_ERROR, {"error_type": "rate_limited"}),
    ],
    ids=["multi-lot", "unresolved", "typed-error"],
)
def test_m5t058_as2_condo_fail_safe_names_cause_no_auto_pick(outcome, kwargs) -> None:
    """AS-2: a multi-lot / unresolved / typed-error condo outcome fail-safes to an
    ABSENT substrate carrying the honest condo cause, with NO base lot auto-picked
    (D-078-R002: zero geometry/lot lookups) and NO substitution stamp."""
    resolution = _condo(outcome, **kwargs)
    condo = _RecordingCondo(resolution)
    recording = RecordingFetchers()  # healthy doubles that must never be reached
    result = build_live_substrate_resolved(
        _BILLING_BBL, CID, fetchers=recording.suite(), condo_resolver=condo
    )
    assert result.substrate is None
    assert result.fail_safe_cause == CONDO_BASE_LOT_UNRESOLVED_CAUSE
    assert result.substitution_stamp is None
    assert result.resolution is resolution
    # No auto-pick of any base lot: the pipeline never runs past the condo step.
    assert condo.calls == [(_BILLING_BBL, CID)]
    assert recording.ztldb_calls == []
    assert recording.lot_calls == []
    assert recording.layer_calls == []


def test_m5t058_as2_genuine_absent_non_condo_keeps_no_condo_cause() -> None:
    """AS-2: a genuinely-absent non-condo substrate (no candidate districts) does
    NOT carry the condo cause - the generic spatial_intersection_absent reason
    survives for it (fail_safe_cause is None)."""
    recording = RecordingFetchers(ztldb=_ztldb_result())  # no districts -> no queries
    result = build_live_substrate_resolved(BBL, CID, fetchers=recording.suite())
    assert result.substrate is None
    assert result.fail_safe_cause is None
    assert result.substitution_stamp is None
    # A non-condo pass-through reached ztldb (proving genuine, not a condo cause).
    assert recording.ztldb_calls == [(BBL, CID)]
    assert recording.lot_calls == []


def test_m5t058_resolved_base_lot_absent_substrate_no_stamp() -> None:
    """A resolved-single condo whose BASE lot then has no candidate districts:
    the substrate is genuinely absent (no single analyzed lot to stamp), so no
    substitution stamp and no condo-unresolved cause - the resolution is still
    carried for provenance."""
    resolution = _resolved_single_resolution()
    condo = _RecordingCondo(resolution)
    recording = RecordingFetchers(ztldb=_ztldb_result())  # base lot: no districts
    result = build_live_substrate_resolved(
        _BILLING_BBL, CID, fetchers=recording.suite(), condo_resolver=condo
    )
    assert result.substrate is None
    assert result.substitution_stamp is None
    assert result.fail_safe_cause is None
    assert result.resolution is resolution
    assert recording.ztldb_calls == [(_BASE_LOT, CID)]


def test_m5t058_as3_build_live_substrate_delegates_substrate_only() -> None:
    """AS-3: the legacy build_live_substrate seam still returns object|None,
    equal to build_live_substrate_resolved(...).substrate, with a SINGLE condo
    call (no double SODA) - the three other route consumers are unwidened."""
    resolution = _resolved_single_resolution()
    condo_legacy = _RecordingCondo(resolution)
    condo_resolved = _RecordingCondo(resolution)
    legacy = build_live_substrate(
        _BILLING_BBL, CID, fetchers=RecordingFetchers().suite(), condo_resolver=condo_legacy
    )
    resolved = build_live_substrate_resolved(
        _BILLING_BBL, CID, fetchers=RecordingFetchers().suite(), condo_resolver=condo_resolved
    )
    assert isinstance(legacy, LotIntersectionRecord)
    assert isinstance(resolved.substrate, LotIntersectionRecord)
    assert legacy.bbl == resolved.substrate.bbl
    # Exactly one condo-resolver call per evaluation on BOTH seams.
    assert condo_legacy.calls == [(_BILLING_BBL, CID)]
    assert condo_resolved.calls == [(_BILLING_BBL, CID)]


def test_m5t058_default_resolved_flag_off_empty_result_zero_calls(monkeypatch) -> None:
    """AS-3: the gated default RESOLVED provider yields an empty LiveSubstrateResult
    (absent substrate, no stamp, no cause) with ZERO connector calls when the flag
    is off - parity with the unresolved default provider's flag-off branch."""
    monkeypatch.delenv(LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR, raising=False)
    recording = RecordingFetchers()
    _install(monkeypatch, recording.suite())
    result = default_live_substrate_resolved(BBL, CID)
    assert isinstance(result, LiveSubstrateResult)
    assert result.substrate is None
    assert result.substitution_stamp is None
    assert result.fail_safe_cause is None
    assert recording.lot_calls == []
    assert recording.ztldb_calls == []
    assert recording.layer_calls == []


def test_m5t058_default_resolved_flag_on_carries_stamp_single_call(monkeypatch) -> None:
    """AS-1/AS-3: flag on, the default RESOLVED provider composes the live
    substrate AND carries the stamp, with exactly one condo-resolver call."""
    monkeypatch.setenv(LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR, "1")
    resolution = _resolved_single_resolution()
    condo = _RecordingCondo(resolution)
    recording = RecordingFetchers()
    _install(monkeypatch, recording.suite())
    _install_condo(monkeypatch, condo)
    result = default_live_substrate_resolved(_BILLING_BBL, CID)
    assert isinstance(result.substrate, LotIntersectionRecord)
    assert result.substitution_stamp == build_substrate_substitution_stamp(
        _BILLING_BBL, resolution
    )
    assert condo.calls == [(_BILLING_BBL, CID)]
