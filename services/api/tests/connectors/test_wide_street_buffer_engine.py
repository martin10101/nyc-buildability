"""Fully offline tests for the B4 wide-street buffer/intersection engine
(task M4-T021, packet scenarios S1-S5). No network access occurs anywhere in
this suite; every fixture is built in-memory via the accepted connectors'
own PARSE surfaces (``parse_segment_geometry_page`` / ``analyze_lot_geometry``
- read-only reuse, never re-implemented) fed synthetic, hand-authored wire
bodies - never real API traffic and never a file this suite writes to.

Expected numeric values (areas, intersects booleans) are HAND-DERIVED from
the fixture coordinates (plain rectangle geometry - see the module-level
comments) and independently cross-checked with a standalone shapely probe
run OUTSIDE this module before these assertions were written (recorded in
the M4-T021 producer report); they are never produced by calling the module
under test."""

from __future__ import annotations

import ast
import dataclasses
import json

import pytest
from shapely.geometry import LineString

import app.connectors.wide_street_buffer_engine as engine
from app.connectors.dcm_street_centerline_arcgis import DcmTransport
from app.connectors.dcm_street_centerline_geometry import (
    EXPECTED_LATEST_WKID as DCM_WKID_LATEST,
)
from app.connectors.dcm_street_centerline_geometry import (
    EXPECTED_WKID as DCM_WKID,
)
from app.connectors.dcm_street_centerline_geometry import (
    GEOMETRY_OK,
    parse_segment_geometry_page,
)
from app.connectors.mappluto_geometry_arcgis import (
    CRS_STAMP as MAPPLUTO_CRS_STAMP,
)
from app.connectors.mappluto_geometry_arcgis import (
    EXPECTED_LATEST_WKID as MAPPLUTO_WKID_LATEST,
)
from app.connectors.mappluto_geometry_arcgis import (
    EXPECTED_WKID as MAPPLUTO_WKID,
)
from app.connectors.mappluto_geometry_arcgis import (
    GEOMETRY_INVALID,
    analyze_lot_geometry,
)
from app.connectors.wide_street_buffer_engine import (
    BUFFER_FT,
    EC2_UNDER_CLAIM_NOTICE,
    PINNED_GEOS_VERSION_STRING,
    PINNED_SHAPELY_VERSION,
    STATUS_COMPUTED,
    STATUS_NO_WIDE_SEGMENTS_PROVIDED,
    TANGENCY_NOTICE,
    AttestedLotPolygon,
    AttestedWideSegment,
    Ec5AttestedPreconditions,
    InvalidGeometryError,
    MalformedAttestationError,
    WideStreetBufferResult,
    WrongCRSError,
    compute_wide_street_buffer_intersection,
)

CORRELATION_ID = "m4t021-test"

# ---------------------------------------------------------------------------
# Fixture builders (fully offline; reuse the accepted connectors' own parse
# surfaces so fixtures are real typed objects, not hand-forged dataclasses)
# ---------------------------------------------------------------------------


def _dcm_attributes(object_id: int, streetwidth: str = "80") -> dict:
    return {
        "OBJECTID": object_id,
        "Borough": "Manhattan",
        "Feat_Type": "Mapped_St",
        "Feat_status": "City_St",
        "Street_NM": "Test Wide Street",
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


def _dcm_page_body(
    features: list[dict],
    *,
    wkid: object = DCM_WKID,
    latest_wkid: object = DCM_WKID_LATEST,
    include_sr: bool = True,
) -> str:
    doc: dict = {
        "objectIdFieldName": "OBJECTID",
        "geometryType": "esriGeometryPolyline",
        "geometryProperties": {"shapeLengthFieldName": "Shape__Length", "units": "esriFeet"},
        "features": features,
    }
    if include_sr:
        doc["spatialReference"] = {"wkid": wkid, "latestWkid": latest_wkid}
    return json.dumps(doc)


def _dcm_feature(object_id: int, paths: list, streetwidth: str = "80") -> dict:
    return {
        "attributes": _dcm_attributes(object_id, streetwidth),
        "geometry": {"paths": paths},
    }


def _make_segment(
    object_id: int,
    paths: list,
    *,
    wkid: int | None = DCM_WKID,
    latest_wkid: int | None = DCM_WKID_LATEST,
    streetwidth: str = "80",
) -> AttestedWideSegment:
    body = _dcm_page_body([_dcm_feature(object_id, paths, streetwidth)])
    transport = DcmTransport(
        url="https://example.invalid/dcm-page",
        status=200,
        body=body,
        retrieved_at="2026-09-14T00:00:00Z",
    )
    page = parse_segment_geometry_page(transport, correlation_id=CORRELATION_ID)
    entry = page.entries[0]
    basis = (
        f"effective_disposition={entry.segment.effective_disposition}; "
        f"basis={entry.segment.width_classification.basis}"
    )
    return AttestedWideSegment(
        polyline=entry,
        wkid=wkid,
        latest_wkid=latest_wkid,
        classification_basis=basis,
        source_retrieved_at=page.retrieved_at,
        source_raw_digest=page.raw_digest,
    )


def _make_lot(
    rings: list,
    *,
    wkid: int | None = MAPPLUTO_WKID,
    latest_wkid: int | None = MAPPLUTO_WKID_LATEST,
    lot_identity: str = "1-00100-0001",
) -> AttestedLotPolygon:
    assessment = analyze_lot_geometry(
        {"rings": rings}, crs=MAPPLUTO_CRS_STAMP, correlation_id=CORRELATION_ID
    )
    return AttestedLotPolygon(
        assessment=assessment,
        wkid=wkid,
        latest_wkid=latest_wkid,
        lot_identity=lot_identity,
        source_retrieved_at="2026-09-14T00:00:00Z",
        source_raw_digest="sha256:deadbeef",
    )


# Square lot 0..200 x 0..200 sq ft (esri clockwise exterior ring convention;
# verified via analyze_lot_geometry: status='valid', area_sq_ft=40000.0).
SQUARE_LOT_RINGS = [[[0, 0], [0, 200], [200, 200], [200, 0], [0, 0]]]

EC5_CHECKED = Ec5AttestedPreconditions(
    named_street_override_checked=True,
    alternate_width_clause_checked=True,
    attestation_note="both checks performed for this synthetic fixture",
)


# ---------------------------------------------------------------------------
# S1: wide_only_buffer_membership
# ---------------------------------------------------------------------------


def test_segment_within_100ft_intersects_true_with_nonempty_area() -> None:
    # Vertical segment at x=-50 (long y-range to avoid endpoint effects);
    # lot spans x in [0, 200]. Buffer reaches x in [-150, 50]: intersects
    # the lot in x in [0, 50], y in [0, 200] -> area = 50 * 200 = 10000.
    lot = _make_lot(SQUARE_LOT_RINGS)
    segment = _make_segment(1, [[[-50.0, -1000.0], [-50.0, 1000.0]]])
    result = compute_wide_street_buffer_intersection(
        lot, [segment], ec5_preconditions=EC5_CHECKED, correlation_id=CORRELATION_ID
    )
    assert result.status == STATUS_COMPUTED
    assert len(result.segment_contributions) == 1
    contribution = result.segment_contributions[0]
    assert contribution.intersects is True
    assert contribution.area_sq_ft == pytest.approx(10000.0)
    assert not contribution.sub_geometry.is_empty
    assert contribution.segment_object_id == 1
    assert "effective_disposition=wide" in contribution.classification_basis
    # Aggregate mirrors the single-segment result exactly.
    assert result.aggregate_intersects is True
    assert result.aggregate_area_sq_ft == pytest.approx(10000.0)
    assert result.lot_area_sq_ft == pytest.approx(40000.0)
    assert result.lot_identity == "1-00100-0001"


def test_segment_beyond_100ft_intersects_false_with_empty_portion() -> None:
    # Vertical segment at x=-300; buffer reaches only x in [-400, -200],
    # never touching the lot (x in [0, 200]).
    lot = _make_lot(SQUARE_LOT_RINGS)
    segment = _make_segment(2, [[[-300.0, -1000.0], [-300.0, 1000.0]]])
    result = compute_wide_street_buffer_intersection(
        lot, [segment], ec5_preconditions=EC5_CHECKED, correlation_id=CORRELATION_ID
    )
    contribution = result.segment_contributions[0]
    assert contribution.intersects is False
    assert contribution.sub_geometry.is_empty
    assert contribution.area_sq_ft == 0.0
    assert result.aggregate_intersects is False
    assert result.aggregate_area_sq_ft == 0.0


def test_only_caller_supplied_segments_participate_never_reclassified() -> None:
    # A segment whose raw Streetwidth is narrow (40 ft) is still buffered
    # exactly as supplied - the module never re-reads Streetwidth or
    # re-decides disposition; it trusts the caller's wide-only contract.
    lot = _make_lot(SQUARE_LOT_RINGS)
    segment = _make_segment(3, [[[-50.0, -1000.0], [-50.0, 1000.0]]], streetwidth="40")
    result = compute_wide_street_buffer_intersection(
        lot, [segment], ec5_preconditions=EC5_CHECKED, correlation_id=CORRELATION_ID
    )
    # Identical geometric result to the "wide" 80-ft-labelled fixture above -
    # proving disposition text never enters the buffer computation.
    assert result.segment_contributions[0].area_sq_ft == pytest.approx(10000.0)


def test_per_segment_identity_is_visible() -> None:
    lot = _make_lot(SQUARE_LOT_RINGS)
    seg_a = _make_segment(11, [[[-50.0, -1000.0], [-50.0, 1000.0]]])
    seg_b = _make_segment(12, [[[-300.0, -1000.0], [-300.0, 1000.0]]])
    result = compute_wide_street_buffer_intersection(
        lot, [seg_a, seg_b], ec5_preconditions=EC5_CHECKED, correlation_id=CORRELATION_ID
    )
    ids = {c.segment_object_id for c in result.segment_contributions}
    assert ids == {11, 12}


# ---------------------------------------------------------------------------
# S2: crs_and_input_fail_closed
# ---------------------------------------------------------------------------


def test_missing_lot_crs_is_typed_wrong_crs() -> None:
    lot = _make_lot(SQUARE_LOT_RINGS, wkid=None, latest_wkid=None)
    segment = _make_segment(1, [[[-50.0, -1000.0], [-50.0, 1000.0]]])
    with pytest.raises(WrongCRSError) as excinfo:
        compute_wide_street_buffer_intersection(
            lot, [segment], ec5_preconditions=EC5_CHECKED, correlation_id=CORRELATION_ID
        )
    assert excinfo.value.error_type == "wrong_crs"
    assert "lot polygon" in str(excinfo.value)


def test_mismatched_lot_crs_is_typed_wrong_crs() -> None:
    lot = _make_lot(SQUARE_LOT_RINGS, wkid=4326, latest_wkid=4326)
    segment = _make_segment(1, [[[-50.0, -1000.0], [-50.0, 1000.0]]])
    with pytest.raises(WrongCRSError):
        compute_wide_street_buffer_intersection(
            lot, [segment], ec5_preconditions=EC5_CHECKED, correlation_id=CORRELATION_ID
        )


def test_missing_segment_crs_is_typed_wrong_crs() -> None:
    lot = _make_lot(SQUARE_LOT_RINGS)
    segment = _make_segment(1, [[[-50.0, -1000.0], [-50.0, 1000.0]]], wkid=None, latest_wkid=None)
    with pytest.raises(WrongCRSError) as excinfo:
        compute_wide_street_buffer_intersection(
            lot, [segment], ec5_preconditions=EC5_CHECKED, correlation_id=CORRELATION_ID
        )
    assert "segment object_id=1" in str(excinfo.value)


def test_mismatched_segment_crs_is_typed_wrong_crs() -> None:
    lot = _make_lot(SQUARE_LOT_RINGS)
    segment = _make_segment(1, [[[-50.0, -1000.0], [-50.0, 1000.0]]], wkid=102100, latest_wkid=3857)
    with pytest.raises(WrongCRSError):
        compute_wide_street_buffer_intersection(
            lot, [segment], ec5_preconditions=EC5_CHECKED, correlation_id=CORRELATION_ID
        )


def test_crs_gate_runs_before_geometry_is_ever_interpreted() -> None:
    # Both the CRS AND the geometry are wrong; the CRS error must win (no
    # coordinate is interpreted before the CRS gate passes).
    lot = _make_lot([[[0, 0], [0, 0]]], wkid=None, latest_wkid=None)
    segment = _make_segment(1, [[[-50.0, -1000.0], [-50.0, 1000.0]]])
    with pytest.raises(WrongCRSError):
        compute_wide_street_buffer_intersection(
            lot, [segment], ec5_preconditions=EC5_CHECKED, correlation_id=CORRELATION_ID
        )


def test_invalid_lot_geometry_is_typed_invalid_geometry() -> None:
    # A degenerate lot ring (all points collinear/zero-extent) -> GEOMETRY_INVALID.
    bad_assessment = analyze_lot_geometry(
        {"rings": [[[0, 0], [0, 0], [0, 0]]]},
        crs=MAPPLUTO_CRS_STAMP,
        correlation_id=CORRELATION_ID,
    )
    assert bad_assessment.status == GEOMETRY_INVALID
    lot = AttestedLotPolygon(
        assessment=bad_assessment,
        wkid=MAPPLUTO_WKID,
        latest_wkid=MAPPLUTO_WKID_LATEST,
        lot_identity="1-00100-0002",
        source_retrieved_at=None,
        source_raw_digest=None,
    )
    segment = _make_segment(1, [[[-50.0, -1000.0], [-50.0, 1000.0]]])
    with pytest.raises(InvalidGeometryError) as excinfo:
        compute_wide_street_buffer_intersection(
            lot, [segment], ec5_preconditions=EC5_CHECKED, correlation_id=CORRELATION_ID
        )
    assert excinfo.value.error_type == "invalid_geometry"


def test_invalid_segment_geometry_is_typed_invalid_geometry() -> None:
    # A degenerate path (single vertex) never reaches GEOMETRY_OK status.
    lot = _make_lot(SQUARE_LOT_RINGS)
    body = _dcm_page_body([_dcm_feature(1, [[[1.0, 2.0]]])])
    transport = DcmTransport(
        url="https://example.invalid/dcm-page", status=200, body=body,
        retrieved_at="2026-09-14T00:00:00Z",
    )
    page = parse_segment_geometry_page(transport, correlation_id=CORRELATION_ID)
    entry = page.entries[0]
    assert entry.status != GEOMETRY_OK
    segment = AttestedWideSegment(
        polyline=entry, wkid=DCM_WKID, latest_wkid=DCM_WKID_LATEST,
        classification_basis="synthetic degenerate", source_retrieved_at=None,
        source_raw_digest=None,
    )
    with pytest.raises(InvalidGeometryError) as excinfo:
        compute_wide_street_buffer_intersection(
            lot, [segment], ec5_preconditions=EC5_CHECKED, correlation_id=CORRELATION_ID
        )
    assert excinfo.value.error_type == "invalid_geometry"


def test_ec5_preconditions_dataclass_has_no_defaults() -> None:
    with pytest.raises(TypeError):
        Ec5AttestedPreconditions()  # type: ignore[call-arg]


def test_attested_wide_segment_dataclass_has_no_defaults() -> None:
    with pytest.raises(TypeError):
        AttestedWideSegment()  # type: ignore[call-arg]


def test_attested_lot_polygon_dataclass_has_no_defaults() -> None:
    with pytest.raises(TypeError):
        AttestedLotPolygon()  # type: ignore[call-arg]


def test_missing_ec5_preconditions_is_a_construction_error() -> None:
    lot = _make_lot(SQUARE_LOT_RINGS)
    segment = _make_segment(1, [[[-50.0, -1000.0], [-50.0, 1000.0]]])
    with pytest.raises(TypeError):
        compute_wide_street_buffer_intersection(  # type: ignore[call-arg]
            lot, [segment], correlation_id=CORRELATION_ID
        )


def test_malformed_ec5_preconditions_type_is_typed_error() -> None:
    lot = _make_lot(SQUARE_LOT_RINGS)
    segment = _make_segment(1, [[[-50.0, -1000.0], [-50.0, 1000.0]]])
    with pytest.raises(MalformedAttestationError) as excinfo:
        compute_wide_street_buffer_intersection(
            lot, [segment], ec5_preconditions={"named_street_override_checked": True},  # type: ignore[arg-type]
            correlation_id=CORRELATION_ID,
        )
    assert excinfo.value.error_type == "malformed_attestation"


def test_malformed_ec5_preconditions_non_bool_field_is_typed_error() -> None:
    lot = _make_lot(SQUARE_LOT_RINGS)
    segment = _make_segment(1, [[[-50.0, -1000.0], [-50.0, 1000.0]]])
    bad = Ec5AttestedPreconditions(
        named_street_override_checked="yes",  # type: ignore[arg-type]
        alternate_width_clause_checked=True,
        attestation_note=None,
    )
    with pytest.raises(MalformedAttestationError) as excinfo:
        compute_wide_street_buffer_intersection(
            lot, [segment], ec5_preconditions=bad, correlation_id=CORRELATION_ID
        )
    assert "named_street_override_checked" in str(excinfo.value)


# ---------------------------------------------------------------------------
# S3: portions_split_corner_lot
# ---------------------------------------------------------------------------


def test_corner_lot_union_before_intersect_and_per_segment_visibility() -> None:
    # Two wide frontages: a vertical segment (west, in-range) and a
    # horizontal segment (south, in-range). Each alone yields 10000 sq ft;
    # their buffers overlap in the lot's SW 50x50 corner (2500 sq ft), so
    # the correct UNION-based aggregate is 10000 + 10000 - 2500 = 17500 -
    # strictly greater than either individual contribution and strictly
    # less than 20000 (which a naive sum would give), and strictly between
    # 0 and the full lot area (40000).
    lot = _make_lot(SQUARE_LOT_RINGS)
    vertical = _make_segment(21, [[[-50.0, -1000.0], [-50.0, 1000.0]]])
    horizontal = _make_segment(22, [[[-1000.0, -50.0], [1000.0, -50.0]]])
    result = compute_wide_street_buffer_intersection(
        lot, [vertical, horizontal], ec5_preconditions=EC5_CHECKED, correlation_id=CORRELATION_ID
    )
    by_id = {c.segment_object_id: c for c in result.segment_contributions}
    assert by_id[21].area_sq_ft == pytest.approx(10000.0)
    assert by_id[22].area_sq_ft == pytest.approx(10000.0)
    assert by_id[21].intersects is True
    assert by_id[22].intersects is True

    assert result.aggregate_area_sq_ft == pytest.approx(17500.0)
    assert result.aggregate_intersects is True
    # Genuine partial split (EC-1): strictly between 0 and the full lot area.
    assert 0.0 < result.aggregate_area_sq_ft < result.lot_area_sq_ft
    # Union correctness: aggregate < naive sum, and > either individual part.
    assert result.aggregate_area_sq_ft < by_id[21].area_sq_ft + by_id[22].area_sq_ft
    assert result.aggregate_area_sq_ft > by_id[21].area_sq_ft
    assert result.aggregate_area_sq_ft > by_id[22].area_sq_ft


def test_non_wide_frontage_never_included_by_construction() -> None:
    # The caller simply never builds an AttestedWideSegment for the
    # non-wide frontage - it structurally cannot participate.
    lot = _make_lot(SQUARE_LOT_RINGS)
    vertical = _make_segment(21, [[[-50.0, -1000.0], [-50.0, 1000.0]]])
    result = compute_wide_street_buffer_intersection(
        lot, [vertical], ec5_preconditions=EC5_CHECKED, correlation_id=CORRELATION_ID
    )
    assert len(result.segment_contributions) == 1
    assert result.aggregate_area_sq_ft == pytest.approx(10000.0)


# ---------------------------------------------------------------------------
# S4: tangency_and_empty_honesty
# ---------------------------------------------------------------------------


def test_exact_tangency_is_the_unmodified_geos_predicate_result() -> None:
    # Segment at x=-100 (long y-range): buffer reaches EXACTLY x=0, the
    # lot's own west boundary. GEOS reports intersects=True (boundary
    # contact is not disjoint) and the intersection is a zero-area
    # LineString (measure-zero touch) - verified via an independent
    # standalone shapely probe before writing this assertion (see producer
    # report); NOT a value this module invents a tolerance around.
    lot = _make_lot(SQUARE_LOT_RINGS)
    segment = _make_segment(31, [[[-100.0, -1000.0], [-100.0, 1000.0]]])
    result = compute_wide_street_buffer_intersection(
        lot, [segment], ec5_preconditions=EC5_CHECKED, correlation_id=CORRELATION_ID
    )
    contribution = result.segment_contributions[0]
    assert contribution.intersects is True
    assert contribution.area_sq_ft == 0.0
    assert contribution.sub_geometry.geom_type == "LineString"
    assert result.tangency_notice == TANGENCY_NOTICE
    # The notice NAMES BOUNDARY_TOLERANCE_FT to explain why it is NOT
    # reused (documentation, not reuse) - the structural proof that it is
    # never actually imported/used as a value lives in
    # test_module_never_reimplements_transport_or_reprojection below.
    assert "BOUNDARY_TOLERANCE_FT" in result.tangency_notice
    assert "BOUNDARY_TOLERANCE_FT" not in dir(engine)


def test_empty_wide_segment_set_is_typed_never_a_default() -> None:
    lot = _make_lot(SQUARE_LOT_RINGS)
    result = compute_wide_street_buffer_intersection(
        lot, [], ec5_preconditions=EC5_CHECKED, correlation_id=CORRELATION_ID
    )
    assert result.status == STATUS_NO_WIDE_SEGMENTS_PROVIDED
    assert result.segment_contributions == ()
    assert result.aggregate_intersects is None
    assert result.aggregate_sub_geometry is None
    assert result.aggregate_area_sq_ft is None
    assert result.aggregate_union_buffer is None
    assert result.empty_notice is not None
    assert "NOT a computed False" in result.empty_notice
    assert "NOT a computed True" in result.empty_notice
    # Explicitly never coerced to a boolean either way.
    assert result.aggregate_intersects is not True
    assert result.aggregate_intersects is not False


def test_ec2_under_claim_notice_always_present() -> None:
    lot = _make_lot(SQUARE_LOT_RINGS)
    empty_result = compute_wide_street_buffer_intersection(
        lot, [], ec5_preconditions=EC5_CHECKED, correlation_id=CORRELATION_ID
    )
    assert empty_result.ec2_under_claim_notice == EC2_UNDER_CLAIM_NOTICE
    segment = _make_segment(1, [[[-50.0, -1000.0], [-50.0, 1000.0]]])
    computed_result = compute_wide_street_buffer_intersection(
        lot, [segment], ec5_preconditions=EC5_CHECKED, correlation_id=CORRELATION_ID
    )
    assert computed_result.ec2_under_claim_notice == EC2_UNDER_CLAIM_NOTICE


def test_ec5_preconditions_pass_through_unmodified_regardless_of_value() -> None:
    # B4 does not gate computation on the attested EC-5 values (module
    # docstring design decision, producer report) - but they ARE always
    # carried through unmodified for audit, including when False.
    lot = _make_lot(SQUARE_LOT_RINGS)
    segment = _make_segment(1, [[[-50.0, -1000.0], [-50.0, 1000.0]]])
    unchecked = Ec5AttestedPreconditions(
        named_street_override_checked=False,
        alternate_width_clause_checked=False,
        attestation_note="not yet checked for this synthetic fixture",
    )
    result = compute_wide_street_buffer_intersection(
        lot, [segment], ec5_preconditions=unchecked, correlation_id=CORRELATION_ID
    )
    assert result.status == STATUS_COMPUTED
    assert result.ec5_preconditions is unchecked
    assert result.ec5_preconditions.named_street_override_checked is False


# ---------------------------------------------------------------------------
# S5: scope_regression_determinism
# ---------------------------------------------------------------------------


def test_shapely_and_geos_versions_are_pinned_for_determinism() -> None:
    import shapely

    assert shapely.__version__ == "2.0.7"
    assert shapely.geos_version_string == "3.11.4"
    assert PINNED_SHAPELY_VERSION == "2.0.7"
    assert PINNED_GEOS_VERSION_STRING == "3.11.4"
    lot = _make_lot(SQUARE_LOT_RINGS)
    segment = _make_segment(1, [[[-50.0, -1000.0], [-50.0, 1000.0]]])
    result = compute_wide_street_buffer_intersection(
        lot, [segment], ec5_preconditions=EC5_CHECKED, correlation_id=CORRELATION_ID
    )
    assert result.shapely_version == "2.0.7"
    assert result.geos_version == "3.11.4"


def test_buffer_ft_constant_is_exactly_100_with_citation() -> None:
    assert BUFFER_FT == 100.0
    lot = _make_lot(SQUARE_LOT_RINGS)
    segment = _make_segment(1, [[[-50.0, -1000.0], [-50.0, 1000.0]]])
    result = compute_wide_street_buffer_intersection(
        lot, [segment], ec5_preconditions=EC5_CHECKED, correlation_id=CORRELATION_ID
    )
    assert result.buffer_ft == 100.0
    assert "23-22" in result.buffer_ft_citation
    assert "footnote 1" in result.buffer_ft_citation


def test_crs_stamp_is_the_authoritative_epsg_2263_pair() -> None:
    lot = _make_lot(SQUARE_LOT_RINGS)
    segment = _make_segment(1, [[[-50.0, -1000.0], [-50.0, 1000.0]]])
    result = compute_wide_street_buffer_intersection(
        lot, [segment], ec5_preconditions=EC5_CHECKED, correlation_id=CORRELATION_ID
    )
    assert result.crs == {
        "wkid": 102718,
        "latest_wkid": 2263,
        "authority": "EPSG:2263 (NAD83 / New York Long Island, US survey feet)",
    }


def test_result_is_a_frozen_dataclass_instance() -> None:
    lot = _make_lot(SQUARE_LOT_RINGS)
    segment = _make_segment(1, [[[-50.0, -1000.0], [-50.0, 1000.0]]])
    result = compute_wide_street_buffer_intersection(
        lot, [segment], ec5_preconditions=EC5_CHECKED, correlation_id=CORRELATION_ID
    )
    assert isinstance(result, WideStreetBufferResult)
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.status = "mutated"  # type: ignore[misc]


def test_module_never_reimplements_transport_or_reprojection() -> None:
    """No transport re-implementation, no reprojection/conversion library,
    no rule-file edits, and no re-classification of street width anywhere
    in this module (mirrors the accepted M4-T020 AST/token-scan precedent)."""
    with open(engine.__file__, encoding="utf-8") as f:
        source = f.read()

    imported_modules: set[str] = set()
    imported_names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported_modules.add(node.module or "")
            imported_names.update(alias.name for alias in node.names)
    assert imported_modules == {
        "__future__",
        "collections.abc",
        "dataclasses",
        "shapely",
        "shapely.geometry",
        "shapely.geometry.base",
        "shapely.ops",
        "app.connectors.dcm_street_centerline_geometry",
        "app.connectors.mappluto_geometry_arcgis",
    }
    # The positional-accuracy constant must NEVER be imported as a value
    # (it may only ever appear as documentation prose explaining why it is
    # NOT reused - see TANGENCY_NOTICE / EC-4).
    assert "BOUNDARY_TOLERANCE_FT" not in imported_names
    # No re-classification surface is imported - B4 never re-decides width.
    assert not imported_modules & {
        "app.connectors.dcm_street_width_classifier",
        "app.connectors.dcm_street_width_policy",
        "app.connectors.dcm_street_centerline_arcgis",
    }

    # (http/https appear legitimately in this module's docstring as a
    # research-evidence citation - https://epsg.io/2263 - so URL-scheme
    # tokens are excluded from this scan; "reproject"/"reprojection" and
    # "pyproject" also appear legitimately in prose explaining that NO
    # reprojection occurs and citing the pyproject.toml determinism
    # discipline - the structural proof those describe truthfully is the
    # exhaustive imported_modules allowlist above, not string absence.
    # "urllib"/"to_crs"/the unit-conversion literals below are implementation
    # -only tokens that would never legitimately appear in this module's
    # prose, so their absence remains a meaningful signal.)
    for forbidden in (
        "urllib",
        "to_crs",
        "0.3048",
        "3.2808",
    ):
        assert forbidden not in source, forbidden


def test_line_probe_matches_the_hand_derived_expected_values() -> None:
    """Independent, direct-shapely cross-check of the exact geometric facts
    this suite's expected values rely on (NOT calling the module under
    test) - a regression guard on the fixture geometry itself."""
    from shapely.geometry import Polygon

    lot_geom = Polygon([(0, 0), (0, 200), (200, 200), (200, 0), (0, 0)])
    assert lot_geom.area == 40000.0
    within = LineString([(-50, -1000), (-50, 1000)]).buffer(100.0, quad_segs=8)
    assert lot_geom.intersection(within).area == 10000.0
    beyond = LineString([(-300, -1000), (-300, 1000)]).buffer(100.0, quad_segs=8)
    assert lot_geom.intersection(beyond).is_empty
    tangent = LineString([(-100, -1000), (-100, 1000)]).buffer(100.0, quad_segs=8)
    tangent_intersection = lot_geom.intersection(tangent)
    assert lot_geom.intersects(tangent) is True
    assert tangent_intersection.area == 0.0
