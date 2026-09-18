"""Fully offline tests for the settings-gated live wide-street-determination
provider (task M5-T035, DB-015; acceptance scenarios AS-1, AS-3, AS-4).

No network access occurs anywhere in this suite. Connector results are built
in-memory from synthetic wire bodies through the accepted connectors' own PARSE
surfaces (``parse_segment_page`` / ``parse_segment_geometry_page`` /
``analyze_lot_geometry`` - read-only reuse, never re-implemented) and handed to
the provider through injected fetcher doubles, so the DEFAULT provider path is
exercised without the network.

Observations vs conclusions: each test states the fixture it built and the exact
provider output it asserts. The provider NEVER fabricates a confident
``within_100ft`` determination from live composition (the accepted stack leaves
the B4 EC-5 preconditions unattested); that is a property of the accepted wiring,
re-asserted here, not a claim proven exhaustively for all inputs."""

from __future__ import annotations

import json
import logging
from types import SimpleNamespace

import pytest

from app.connectors.dcm_street_centerline_arcgis import (
    CRS_STAMP as DCM_CRS_STAMP,
)
from app.connectors.dcm_street_centerline_arcgis import (
    DcmTransport,
    UpstreamError,
    parse_segment_page,
)
from app.connectors.dcm_street_centerline_geometry import parse_segment_geometry_page
from app.connectors.mappluto_geometry_arcgis import (
    CRS_STAMP as MAPPLUTO_CRS_STAMP,
)
from app.connectors.mappluto_geometry_arcgis import (
    OUTCOME_MULTIPLE,
    OUTCOME_SINGLE,
    analyze_lot_geometry,
)
from app.connectors.mappluto_geometry_arcgis import (
    UpstreamError as MapPlutoUpstreamError,
)
from app.rules.wide_street_wiring import (
    DETERMINATION_NOT_WITHIN_WIDE,
    DETERMINATION_PROFESSIONAL_REVIEW,
    FAR_ROW_NONE,
    FAR_ROW_STANDARD,
    WideStreetDetermination,
)
from app.spatial import wide_street_live_provider as provider
from app.spatial.wide_street_live_provider import (
    LIVE_WIDE_STREET_PROVIDER_ENABLED_ENV_VAR,
    LiveWideStreetFetchers,
    build_live_wide_street_determination,
    default_live_wide_street_determination,
    live_wide_street_provider_enabled,
)

CID = "m5t035-provider-test"
BBL_FIXTURE = "1000010001"

# Square lot 0..200 x 0..200 (esri clockwise exterior ring; analyze_lot_geometry
# yields status='valid', area_sq_ft=40000.0 - see the accepted M4-T021 suite).
SQUARE_LOT_RINGS = [[[0, 0], [0, 200], [200, 200], [200, 0], [0, 0]]]

# A vertical wide street at x=-50 lies within 100 ft of the lot (x in [0, 200]).
WIDE_SEGMENT_PATHS = [[[-50.0, -1000.0], [-50.0, 1000.0]]]


# ---------------------------------------------------------------------------
# Fixture builders (offline; real typed objects via the accepted parse surfaces)
# ---------------------------------------------------------------------------


def _dcm_attributes(object_id: int, streetwidth: str) -> dict:
    return {
        "OBJECTID": object_id,
        "Borough": "Manhattan",
        "Feat_Type": "Mapped_St",
        "Feat_status": "City_St",
        "Street_NM": "Test Street",
        "HonoraryNM": "None",
        "Old_ST_NM": "None",
        "Streetwidth": streetwidth,
        "Route_Type": "Gen_use",
        "RoadwayType": "Surface_ST",
        "Build_Status": "Improved",
        "Record_ST": "N",
        "Paper_ST": "N",
        "Stair_ST": "N",
        "CCO_ST": "N",
        "Marg_Wharf": "N",
        "Edit_Date": None,
    }


def _dcm_page_body(features: list[dict]) -> str:
    return json.dumps(
        {
            "objectIdFieldName": "OBJECTID",
            "geometryType": "esriGeometryPolyline",
            "geometryProperties": {"units": "esriFeet"},
            "spatialReference": {
                "wkid": DCM_CRS_STAMP["wkid"],
                "latestWkid": DCM_CRS_STAMP["latest_wkid"],
            },
            "features": features,
        }
    )


def _transport(body: str) -> DcmTransport:
    return DcmTransport(
        url="https://example.invalid/dcm-page",
        status=200,
        body=body,
        retrieved_at="2026-09-17T00:00:00Z",
    )


def _lot_double(
    *, outcome: str = OUTCOME_SINGLE, review_required: bool = False, rings: list | None = None
) -> SimpleNamespace:
    assessment = analyze_lot_geometry(
        {"rings": rings if rings is not None else SQUARE_LOT_RINGS},
        crs=MAPPLUTO_CRS_STAMP,
        correlation_id=CID,
    )
    return SimpleNamespace(
        outcome=outcome,
        review_required=review_required,
        geometry=assessment,
        crs=dict(MAPPLUTO_CRS_STAMP),
        retrieved_at="2026-09-17T00:00:00Z",
        raw_digest="sha256:lotdigest",
    )


def _segments_double(
    features: list[dict], *, exceeded: bool = False
) -> SimpleNamespace:
    segments, _ = parse_segment_page(_transport(_dcm_page_body(features)), correlation_id=CID)
    return SimpleNamespace(
        segments=segments,
        exceeded_transfer_limit_on_last_page=exceeded,
        source_data_last_edited="2026-09-01T00:00:00Z",
        retrieved_at="2026-09-17T00:00:00Z",
    )


def _geometries_double(
    features: list[dict], *, exceeded: bool = False
) -> SimpleNamespace:
    page = parse_segment_geometry_page(_transport(_dcm_page_body(features)), correlation_id=CID)
    return SimpleNamespace(
        entries=page.entries,
        exceeded_transfer_limit_on_last_page=exceeded,
        crs=dict(DCM_CRS_STAMP),
        retrieved_at="2026-09-17T00:00:00Z",
    )


def _feature(object_id: int, streetwidth: str, paths: list) -> dict:
    return {"attributes": _dcm_attributes(object_id, streetwidth), "geometry": {"paths": paths}}


class _CountingFetchers:
    """Fetcher set that records how many times each seam is invoked (AS-1
    zero-connector-calls proof) and returns pre-built doubles."""

    def __init__(self, *, lot=None, segments=None, geometries=None):
        self.calls = {"lot": 0, "segments": 0, "geometries": 0}
        self._lot = lot
        self._segments = segments
        self._geometries = geometries

    def as_fetchers(self) -> LiveWideStreetFetchers:
        return LiveWideStreetFetchers(
            fetch_lot=self._fetch_lot,
            fetch_segments_by_envelope=self._fetch_segments,
            fetch_segment_geometries_by_ids=self._fetch_geometries,
        )

    def _fetch_lot(self, canonical_bbl, correlation_id):
        self.calls["lot"] += 1
        if isinstance(self._lot, Exception):
            raise self._lot
        return self._lot

    def _fetch_segments(self, envelope, correlation_id):
        self.calls["segments"] += 1
        assert len(envelope) == 4  # the provider always passes a 4-tuple envelope
        if isinstance(self._segments, Exception):
            raise self._segments
        return self._segments

    def _fetch_geometries(self, object_id_in, correlation_id):
        self.calls["geometries"] += 1
        if isinstance(self._geometries, Exception):
            raise self._geometries
        return self._geometries


# ---------------------------------------------------------------------------
# AS-1: flag reading (explicit true token only; absent/unknown -> disabled)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("token", ["1", "true", "TRUE", "yes", "on", " on "])
def test_enabled_only_for_explicit_true_token(token: str) -> None:
    enabled = live_wide_street_provider_enabled(
        {LIVE_WIDE_STREET_PROVIDER_ENABLED_ENV_VAR: token}
    )
    assert enabled is True


@pytest.mark.parametrize("token", ["", "0", "off", "no", "maybe", "2"])
def test_disabled_for_non_true_token(token: str) -> None:
    enabled = live_wide_street_provider_enabled(
        {LIVE_WIDE_STREET_PROVIDER_ENABLED_ENV_VAR: token}
    )
    assert enabled is False


def test_disabled_when_absent() -> None:
    assert live_wide_street_provider_enabled({}) is False


def test_flag_off_returns_none_with_zero_connector_calls(monkeypatch) -> None:
    monkeypatch.delenv(LIVE_WIDE_STREET_PROVIDER_ENABLED_ENV_VAR, raising=False)
    counting = _CountingFetchers(
        lot=AssertionError("fetch_lot must not be called when the flag is off")
    )
    monkeypatch.setattr(provider, "_ACTIVE_FETCHERS", counting.as_fetchers())
    assert default_live_wide_street_determination(BBL_FIXTURE, CID) is None
    assert counting.calls == {"lot": 0, "segments": 0, "geometries": 0}


# ---------------------------------------------------------------------------
# AS-3: happy path composes a real typed determination end-to-end
# ---------------------------------------------------------------------------


def test_all_narrow_neighborhood_yields_confident_not_within() -> None:
    # Every candidate segment classifies narrow (40 ft) -> the accepted policy
    # returns narrow for each -> the wiring's confident standard row governs.
    fetchers = _CountingFetchers(
        lot=_lot_double(),
        segments=_segments_double([_feature(1, "40", WIDE_SEGMENT_PATHS)]),
        geometries=_geometries_double([]),
    ).as_fetchers()
    determination = build_live_wide_street_determination(BBL_FIXTURE, CID, fetchers=fetchers)
    assert isinstance(determination, WideStreetDetermination)
    assert determination.determination_state == DETERMINATION_NOT_WITHIN_WIDE
    assert determination.far_row == FAR_ROW_STANDARD
    assert determination.lot_identity == BBL_FIXTURE
    # Provenance quintuple is aggregated from the policy decision (D-052-R005).
    assert determination.policy_decision_states == ("narrow",)
    assert determination.original_labels == ("40",)


def test_wide_segment_yields_professional_review_never_fabricated_wide() -> None:
    # A wide (80 ft) mapped segment within 100 ft of the lot. The accepted stack
    # cannot attest the B4 EC-5 named-street / alternate-width preconditions, so
    # the composition resolves to professional review - never a fabricated wide.
    counting = _CountingFetchers(
        lot=_lot_double(),
        segments=_segments_double([_feature(7, "80", WIDE_SEGMENT_PATHS)]),
        geometries=_geometries_double([_feature(7, "80", WIDE_SEGMENT_PATHS)]),
    )
    determination = build_live_wide_street_determination(
        BBL_FIXTURE, CID, fetchers=counting.as_fetchers()
    )
    assert isinstance(determination, WideStreetDetermination)
    assert determination.determination_state == DETERMINATION_PROFESSIONAL_REVIEW
    assert determination.far_row == FAR_ROW_NONE
    # The wide-disposed segment's geometry WAS fetched (the composition reached
    # the buffer stage before the EC-5 gate refused).
    assert counting.calls["geometries"] == 1


# ---------------------------------------------------------------------------
# AS-4: every failure/insufficiency class -> None (honest fail-safe)
# ---------------------------------------------------------------------------


def test_zero_segments_in_envelope_returns_none_never_confident_not_within() -> None:
    # D-051 honest absence: no DCM segment intersected the envelope -> None,
    # NOT a confident not-within determination.
    fetchers = _CountingFetchers(
        lot=_lot_double(), segments=_segments_double([]),
    ).as_fetchers()
    assert build_live_wide_street_determination(BBL_FIXTURE, CID, fetchers=fetchers) is None


def test_partial_segment_page_returns_none() -> None:
    fetchers = _CountingFetchers(
        lot=_lot_double(),
        segments=_segments_double([_feature(1, "40", WIDE_SEGMENT_PATHS)], exceeded=True),
    ).as_fetchers()
    assert build_live_wide_street_determination(BBL_FIXTURE, CID, fetchers=fetchers) is None


def test_partial_wide_geometry_page_returns_none() -> None:
    fetchers = _CountingFetchers(
        lot=_lot_double(),
        segments=_segments_double([_feature(9, "80", WIDE_SEGMENT_PATHS)]),
        geometries=_geometries_double([_feature(9, "80", WIDE_SEGMENT_PATHS)], exceeded=True),
    ).as_fetchers()
    assert build_live_wide_street_determination(BBL_FIXTURE, CID, fetchers=fetchers) is None


def test_lot_connector_error_returns_none() -> None:
    fetchers = _CountingFetchers(
        lot=MapPlutoUpstreamError("boom", correlation_id=CID),
    ).as_fetchers()
    assert build_live_wide_street_determination(BBL_FIXTURE, CID, fetchers=fetchers) is None


def test_segment_connector_error_returns_none() -> None:
    fetchers = _CountingFetchers(
        lot=_lot_double(),
        segments=UpstreamError("boom", correlation_id=CID),
    ).as_fetchers()
    assert build_live_wide_street_determination(BBL_FIXTURE, CID, fetchers=fetchers) is None


def test_unexpected_lot_error_returns_none() -> None:
    fetchers = _CountingFetchers(lot=RuntimeError("unexpected")).as_fetchers()
    assert build_live_wide_street_determination(BBL_FIXTURE, CID, fetchers=fetchers) is None


def test_unexpected_segment_error_returns_none() -> None:
    # A non-DCM (unexpected) failure from the segment fetch is still fail-safed to
    # None by the provider's typed-boundary except - never a fabricated result.
    fetchers = _CountingFetchers(
        lot=_lot_double(),
        segments=RuntimeError("unexpected segment failure"),
    ).as_fetchers()
    assert build_live_wide_street_determination(BBL_FIXTURE, CID, fetchers=fetchers) is None


def test_wide_geometry_connector_error_returns_none() -> None:
    # A typed DCM connector error while fetching the wide segment's geometry ->
    # None (the buffer inputs would be incomplete; never buffered on absent data).
    fetchers = _CountingFetchers(
        lot=_lot_double(),
        segments=_segments_double([_feature(9, "80", WIDE_SEGMENT_PATHS)]),
        geometries=UpstreamError("geometry boom", correlation_id=CID),
    ).as_fetchers()
    assert build_live_wide_street_determination(BBL_FIXTURE, CID, fetchers=fetchers) is None


def test_multiple_feature_lot_returns_none() -> None:
    fetchers = _CountingFetchers(
        lot=_lot_double(outcome=OUTCOME_MULTIPLE, review_required=True),
    ).as_fetchers()
    assert build_live_wide_street_determination(BBL_FIXTURE, CID, fetchers=fetchers) is None


# ---------------------------------------------------------------------------
# AS-4: payload-only fail-safe logging (typed error CLASS + correlation id,
# never str(exc)). These assert the log LINE the provider emits, complementing
# the None-return assertions above.
# ---------------------------------------------------------------------------


def test_typed_connector_error_logs_payload_only_never_str_exc(caplog) -> None:
    # A typed DCM connector failure returns None AND emits exactly one fail-safe
    # log line carrying the event, the error CLASS, and the correlation id - never
    # str(exc). The exception message is a CANARY that must not reach the log line
    # (the upstream chain may embed untrusted strings; M1-T002 G5 F5 policy).
    fetchers = _CountingFetchers(
        lot=_lot_double(),
        segments=UpstreamError("canary-wide-street-detail", correlation_id=CID),
    ).as_fetchers()
    with caplog.at_level(
        logging.WARNING, logger="app.spatial.wide_street_live_provider"
    ):
        determination = build_live_wide_street_determination(
            BBL_FIXTURE, CID, fetchers=fetchers
        )
    assert determination is None
    lines = [
        record.getMessage()
        for record in caplog.records
        if record.name == "app.spatial.wide_street_live_provider"
        and "fail_safe" in record.getMessage()
    ]
    assert len(lines) == 1
    assert "event=segment_connector_error" in lines[0]
    assert "error_type=UpstreamError" in lines[0]
    assert f"correlation_id={CID}" in lines[0]
    assert "canary-wide-street-detail" not in lines[0]


def test_zero_segment_fail_safe_logs_payload_only_with_correlation_id(caplog) -> None:
    # The honest-absence branch (no exception object) still logs payload-only: the
    # event and the correlation id, with error_type=none (D-051 honest absence).
    fetchers = _CountingFetchers(
        lot=_lot_double(),
        segments=_segments_double([]),
    ).as_fetchers()
    with caplog.at_level(
        logging.WARNING, logger="app.spatial.wide_street_live_provider"
    ):
        determination = build_live_wide_street_determination(
            BBL_FIXTURE, CID, fetchers=fetchers
        )
    assert determination is None
    lines = [
        record.getMessage()
        for record in caplog.records
        if record.name == "app.spatial.wide_street_live_provider"
        and "fail_safe" in record.getMessage()
    ]
    assert len(lines) == 1
    assert "event=no_segments_in_envelope" in lines[0]
    assert "error_type=none" in lines[0]
    assert f"correlation_id={CID}" in lines[0]
