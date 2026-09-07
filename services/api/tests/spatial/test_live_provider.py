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
    LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR,
    LiveSpatialFetchers,
    _candidate_layer_queries,
    build_live_substrate,
    default_live_substrate,
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
