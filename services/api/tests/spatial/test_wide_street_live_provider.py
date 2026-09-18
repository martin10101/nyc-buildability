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
import re
from types import SimpleNamespace

import pytest

from app.connectors.dcm_street_centerline_arcgis import (
    CRS_STAMP as DCM_CRS_STAMP,
)
from app.connectors.dcm_street_centerline_arcgis import (
    DcmTransport,
    UpstreamError,
    parse_segment_page,
    raw_body_digest,
)
from app.connectors.dcm_street_centerline_geometry import parse_segment_geometry_page
from app.connectors.mappluto_geometry_arcgis import (
    CRS_STAMP as MAPPLUTO_CRS_STAMP,
)
from app.connectors.mappluto_geometry_arcgis import (
    GEOMETRY_VALID,
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
    # DB-020: the provider walks geom_result.pages (never the flattened entries)
    # so each attested segment carries the SegmentGeometryPage's own retrieval
    # identity + raw-body digest. The real SegmentGeometryQueryResult exposes both
    # ``pages`` and the flattened ``entries``; the double mirrors that.
    return SimpleNamespace(
        entries=page.entries,
        pages=[page],
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
# DB-020 (M5-T035 G1 F1): the attested provenance digest is the geometry-PAGE
# raw-body sha256, NEVER the segment's free-text Streetwidth attribute.
# ---------------------------------------------------------------------------


def test_db020_attested_segment_carries_geometry_page_digest_not_width_text() -> None:
    # Before the fix, AttestedWideSegment.source_raw_digest carried the segment's
    # Streetwidth text (e.g. "80"). It must carry the SegmentGeometryPage raw-body
    # sha256 digest for the page the segment was parsed from.
    features = [_feature(7, "80", WIDE_SEGMENT_PATHS)]
    fetchers = _CountingFetchers(geometries=_geometries_double(features)).as_fetchers()
    attested = provider._attested_wide_segments([7], fetchers, CID)
    assert attested is not None
    assert len(attested) == 1
    digest = attested[0].source_raw_digest
    assert digest is not None
    # sha256-shaped, and exactly the page's own raw-body digest.
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", digest), digest
    assert digest == raw_body_digest(_dcm_page_body(features))
    # The pre-fix defect value (the Streetwidth text) is never used as the digest,
    # even though the source attribute itself is preserved untouched on the segment.
    assert digest != "80"
    assert attested[0].polyline.segment.streetwidth_raw == "80"
    assert digest != attested[0].polyline.segment.streetwidth_raw


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


# ---------------------------------------------------------------------------
# DB-021 (M5-T040) provider hardening: (a) provider-side MAX_LOT_VERTICES
# pre-check before the provider's own first canonical_to_shapely; (b) the
# wide_object_ids cap before the geometry-fetch loop; (e) direct coverage of the
# segment_geometry_unexpected_error branch and the _attested_lot sub-branches.
# ---------------------------------------------------------------------------


def _fail_safe_lines(caplog) -> list[str]:
    return [
        record.getMessage()
        for record in caplog.records
        if record.name == "app.spatial.wide_street_live_provider"
        and "fail_safe" in record.getMessage()
    ]


def test_db021a_lot_over_vertex_cap_returns_none_before_envelope(monkeypatch, caplog) -> None:
    # DB-021a: a lot whose canonical vertex count exceeds the provider-side
    # MAX_LOT_VERTICES bound is refused BEFORE _lot_envelope's canonical_to_shapely
    # (fail-safe None). Lower the cap below the 5-vertex square lot to exercise it.
    monkeypatch.setattr(provider, "MAX_LOT_VERTICES", 3)
    counting = _CountingFetchers(
        lot=_lot_double(),
        segments=AssertionError("segments must not be fetched past the vertex cap"),
    )
    with caplog.at_level(logging.WARNING, logger="app.spatial.wide_street_live_provider"):
        determination = build_live_wide_street_determination(
            BBL_FIXTURE, CID, fetchers=counting.as_fetchers()
        )
    assert determination is None
    # Refused before any segment fetch (the check runs before _lot_envelope).
    assert counting.calls["segments"] == 0
    lines = _fail_safe_lines(caplog)
    assert any("event=lot_vertices_over_cap" in line for line in lines)


def test_db021b_wide_segments_over_cap_returns_none_before_geometry_fetch(
    monkeypatch, caplog
) -> None:
    # DB-021b: more wide-disposed OBJECTIDs than MAX_WIDE_SEGMENTS are refused
    # BEFORE the geometry-fetch loop (the engine's own 512 ceiling would only fire
    # after every page was fetched). Lower the cap to 1 with two wide segments.
    monkeypatch.setattr(provider, "MAX_WIDE_SEGMENTS", 1)
    counting = _CountingFetchers(
        lot=_lot_double(),
        segments=_segments_double(
            [_feature(7, "80", WIDE_SEGMENT_PATHS), _feature(8, "80", WIDE_SEGMENT_PATHS)]
        ),
        geometries=AssertionError("geometry must not be fetched past the wide cap"),
    )
    with caplog.at_level(logging.WARNING, logger="app.spatial.wide_street_live_provider"):
        determination = build_live_wide_street_determination(
            BBL_FIXTURE, CID, fetchers=counting.as_fetchers()
        )
    assert determination is None
    assert counting.calls["geometries"] == 0
    lines = _fail_safe_lines(caplog)
    assert any("event=wide_segments_over_cap" in line for line in lines)


def test_db021e_unexpected_wide_geometry_error_returns_none(caplog) -> None:
    # DB-021e: an UNEXPECTED (non-DCM) failure from the geometry fetch is
    # fail-safed to None via the segment_geometry_unexpected_error branch (the
    # sibling of the typed DCMConnectorError branch already covered above).
    counting = _CountingFetchers(
        lot=_lot_double(),
        segments=_segments_double([_feature(9, "80", WIDE_SEGMENT_PATHS)]),
        geometries=RuntimeError("unexpected geometry failure"),
    )
    with caplog.at_level(logging.WARNING, logger="app.spatial.wide_street_live_provider"):
        determination = build_live_wide_street_determination(
            BBL_FIXTURE, CID, fetchers=counting.as_fetchers()
        )
    assert determination is None
    lines = _fail_safe_lines(caplog)
    assert any("event=segment_geometry_unexpected_error" in line for line in lines)
    assert any("error_type=RuntimeError" in line for line in lines)


def _assessment(*, status: str = GEOMETRY_VALID, canonical=None) -> SimpleNamespace:
    return SimpleNamespace(
        status=status,
        canonical_geometry=SQUARE_LOT_RINGS if canonical is None else canonical,
    )


@pytest.mark.parametrize(
    "lot,label",
    [
        (
            SimpleNamespace(
                outcome=OUTCOME_MULTIPLE, review_required=False, geometry=_assessment()
            ),
            "not-single-outcome",
        ),
        (
            SimpleNamespace(
                outcome=OUTCOME_SINGLE, review_required=True, geometry=_assessment()
            ),
            "review-required",
        ),
        (
            SimpleNamespace(outcome=OUTCOME_SINGLE, review_required=False, geometry=None),
            "geometry-none",
        ),
        (
            SimpleNamespace(
                outcome=OUTCOME_SINGLE,
                review_required=False,
                geometry=_assessment(status="invalid"),
            ),
            "status-not-valid",
        ),
        (
            SimpleNamespace(
                outcome=OUTCOME_SINGLE,
                review_required=False,
                geometry=SimpleNamespace(status=GEOMETRY_VALID, canonical_geometry=None),
            ),
            "canonical-none",
        ),
    ],
    ids=lambda v: v if isinstance(v, str) else "",
)
def test_db021e_attested_lot_rejects_every_unusable_subbranch(lot, label) -> None:
    # DB-021e: each _attested_lot None-return sub-branch (wrong outcome, review
    # required, missing geometry, non-valid/repaired status, missing canonical
    # geometry) is directly exercised and yields None (honest absence).
    assert provider._attested_lot(lot, BBL_FIXTURE) is None


def test_db021e_attested_lot_accepts_usable_single_valid_lot() -> None:
    # Positive companion: a usable single valid lot is wrapped (never None), so
    # the sub-branch tests above are proven to be rejecting, not vacuous.
    lot = _lot_double()
    attested = provider._attested_lot(lot, BBL_FIXTURE)
    assert attested is not None
    assert attested.lot_identity == BBL_FIXTURE
