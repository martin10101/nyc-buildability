"""Fully offline tests for the DCM centerline geometry sibling module
(task M4-T020, packet scenarios S1-S4; S5 is the scope/regression scenario
run via the documented commands). Wire bodies are either the recorded
M4-T015 fixtures in ``services/api/tests/fixtures/dcm_street_centerline/``
(READ-ONLY) or documented in-memory page bodies built here; no network
access occurs in this suite and no fixture file is modified."""

from __future__ import annotations

import ast
import json
import os

import pytest

import app.connectors.dcm_street_centerline_geometry as geometry_module
from app.connectors.dcm_street_centerline_arcgis import (
    ATTRIBUTION,
    CRS_STAMP,
    SOURCE_ID,
    DcmTransport,
    MalformedResponseError,
    SchemaDriftError,
    UpstreamError,
    WrongCRSError,
    build_metadata_url,
    default_fetch,
    raw_body_digest,
)
from app.connectors.dcm_street_centerline_geometry import (
    EXPECTED_PAGE_GEOMETRY_TYPE,
    GEOMETRY_DEGENERATE_PATH,
    GEOMETRY_EMPTY_PATHS,
    GEOMETRY_MALFORMED_COORDINATE,
    GEOMETRY_MALFORMED_OBJECT,
    GEOMETRY_NONFINITE_COORDINATE,
    GEOMETRY_NULL,
    GEOMETRY_OK,
    GEOMETRY_STATUSES,
    GEOMETRY_UNEXPECTED_KIND,
    SegmentGeometryPage,
    SegmentGeometryQueryResult,
    fetch_street_segment_geometries,
    parse_segment_geometry_page,
)

FIXTURE_DIR = os.path.join(
    os.path.dirname(__file__), "..", "fixtures", "dcm_street_centerline"
)

CORRELATION_ID = "m4t020-test"

AUTHORITATIVE_SR = {"wkid": 102718, "latestWkid": 2263}


def _fixture_body(name: str) -> str:
    with open(os.path.join(FIXTURE_DIR, name), encoding="utf-8") as f:
        return f.read()


def _attributes(object_id: int = 1, streetwidth: str = "60") -> dict:
    return {
        "OBJECTID": object_id,
        "Borough": "Manhattan",
        "Feat_Type": "Mapped_St",
        "Feat_status": "City_St",
        "Street_NM": "West 100 Street",
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


def _feature(
    object_id: int = 1,
    *,
    paths: list | None = None,
    geometry: object = "default",
    include_geometry: bool = True,
) -> dict:
    """One documented query-page feature. ``geometry='default'`` builds a
    paths geometry from ``paths``; pass ``geometry=...`` explicitly (or
    ``include_geometry=False``) to exercise the taxonomy."""
    feature: dict = {"attributes": _attributes(object_id)}
    if not include_geometry:
        return feature
    if geometry == "default":
        feature["geometry"] = {
            "paths": paths if paths is not None else [[[1.0, 2.0], [3.0, 4.0]]]
        }
    else:
        feature["geometry"] = geometry
    return feature


def _page_body(
    features: list[dict],
    *,
    spatial_reference: object = "authoritative",
    include_spatial_reference: bool = True,
    geometry_type: object = EXPECTED_PAGE_GEOMETRY_TYPE,
    include_geometry_type: bool = True,
    exceeded: bool | None = None,
) -> str:
    doc: dict = {
        "objectIdFieldName": "OBJECTID",
        "geometryProperties": {"shapeLengthFieldName": "Shape__Length", "units": "esriFeet"},
        "features": features,
    }
    if include_geometry_type:
        doc["geometryType"] = geometry_type
    if include_spatial_reference:
        doc["spatialReference"] = (
            dict(AUTHORITATIVE_SR)
            if spatial_reference == "authoritative"
            else spatial_reference
        )
    if exceeded is not None:
        doc["exceededTransferLimit"] = exceeded
    return json.dumps(doc)


def _transport(body: str, *, status: int = 200) -> DcmTransport:
    return DcmTransport(
        url="https://example.invalid/recorded-page",
        status=status,
        body=body,
        retrieved_at="2026-09-14T00:00:00Z",
    )


def _parse(body: str, *, status: int = 200) -> SegmentGeometryPage:
    return parse_segment_geometry_page(
        _transport(body, status=status), correlation_id=CORRELATION_ID
    )


def _counting_fetcher(bodies: list[str]):
    """Serve raw bodies in sequence and count calls (proves the paged flow
    performs exactly one transport per page and never a second fetch)."""
    calls: list[str] = []

    def _fetch(url: str, correlation_id: str) -> DcmTransport:
        index = len(calls)
        calls.append(url)
        return DcmTransport(
            url=url, status=200, body=bodies[index], retrieved_at="2026-09-14T00:00:00Z"
        )

    return _fetch, calls


# ---------------------------------------------------------------------------
# S1: wire-format parse and typing (real recorded fixture + multi-path)
# ---------------------------------------------------------------------------


def test_recorded_fixture_page_parses_typed_multipath_polylines() -> None:
    body = _fixture_body("west_100_st_two_segments.json")
    page = _parse(body)
    assert isinstance(page, SegmentGeometryPage)
    assert page.features_total == 2
    assert [entry.status for entry in page.entries] == [GEOMETRY_OK, GEOMETRY_OK]
    by_id = {entry.object_id: entry for entry in page.entries}

    # Multi-path segments preserved as distinct paths in wire order.
    assert by_id[7719].path_count == 3
    assert by_id[14471].path_count == 3
    assert by_id[7719].vertex_count == 6
    assert by_id[14471].vertex_count == 12

    # Typed polylines: tuples of finite (x, y) float pairs.
    assert by_id[7719].paths is not None
    first_vertex = by_id[7719].paths[0][0]
    assert isinstance(by_id[7719].paths, tuple)
    assert isinstance(by_id[7719].paths[0], tuple)
    assert isinstance(first_vertex, tuple)
    assert all(isinstance(component, float) for component in first_vertex)
    assert first_vertex == (992185.54514055, 229943.965358555)


def test_entries_pair_geometry_with_attributes_from_the_same_page_body() -> None:
    page = _parse(_fixture_body("west_100_st_two_segments.json"))
    by_id = {entry.object_id: entry for entry in page.entries}
    assert by_id[7719].segment.streetwidth_raw == "60"
    assert by_id[14471].segment.streetwidth_raw == "100"
    assert by_id[7719].segment.street_name == "West 100 Street"
    assert by_id[7719].feature_index == 0
    assert by_id[14471].feature_index == 1


def test_paths_match_the_wire_json_exactly_no_rounding() -> None:
    body = _fixture_body("west_100_st_two_segments.json")
    page = _parse(body)
    raw_features = json.loads(body)["features"]
    for entry, raw_feature in zip(page.entries, raw_features, strict=True):
        raw_paths = tuple(
            tuple((float(x), float(y)) for x, y, *_ in path)
            for path in raw_feature["geometry"]["paths"]
        )
        assert entry.paths == raw_paths


def test_exceeded_transfer_limit_flag_passes_through() -> None:
    page = _parse(_page_body([_feature(1)], exceeded=True))
    assert page.exceeded_transfer_limit is True
    page = _parse(_page_body([_feature(1)]))
    assert page.exceeded_transfer_limit is False


def test_empty_features_page_is_a_normal_empty_result() -> None:
    page = _parse(_page_body([]))
    assert page.entries == []
    assert page.features_total == 0
    assert page.usable_geometry_count == 0


# ---------------------------------------------------------------------------
# S1 (reuse fidelity): the accepted transport is reused by import; no
# duplicated HTTP/query building exists in the geometry module
# ---------------------------------------------------------------------------


def test_module_reuses_the_accepted_transport_surfaces_by_import() -> None:
    assert geometry_module.default_fetch is default_fetch
    assert geometry_module.SOURCE_ID == SOURCE_ID
    with open(geometry_module.__file__, encoding="utf-8") as f:
        source = f.read()
    # No transport re-implementation and no reprojection/conversion library:
    # the module's ONLY imports are the stdlib parse/typing helpers and the
    # accepted transport module (read-only reuse).
    imported_modules: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported_modules.add(node.module or "")
    assert imported_modules == {
        "__future__",
        "json",
        "collections.abc",
        "dataclasses",
        "math",
        "app.connectors.dcm_street_centerline_arcgis",
    }
    # No URL building against the service and no unit-conversion constant
    # (tokens that cannot occur as prose in the module's documentation).
    for forbidden in (
        "urllib",
        "FeatureServer",
        "outSR",
        "http://",
        "https://",
        "pyproj",
        "to_crs",
        "0.3048",
        "3.2808",
    ):
        assert forbidden not in source, forbidden


def test_reused_validation_surfaces_type_transport_failures() -> None:
    # Non-200 status: typed by the accepted parse_segment_page (reused).
    with pytest.raises(UpstreamError):
        _parse(_page_body([_feature(1)]), status=502)
    # ArcGIS error object with HTTP 200: upstream error, never data.
    with pytest.raises(UpstreamError):
        _parse(json.dumps({"error": {"code": 400, "message": "bad"}}))
    # Missing features array: malformed, never a valid empty result.
    with pytest.raises(MalformedResponseError):
        _parse(json.dumps({"spatialReference": AUTHORITATIVE_SR}))


# ---------------------------------------------------------------------------
# S2: CRS fail-closed (only wkid 102718 / latestWkid 2263 is accepted)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "spatial_reference,include",
    [
        pytest.param(None, False, id="spatialReference_key_absent"),
        pytest.param(None, True, id="spatialReference_json_null"),
        pytest.param({}, True, id="wkid_absent"),
        pytest.param({"wkid": 4326, "latestWkid": 4326}, True, id="wrong_wkid_wgs84"),
        pytest.param({"wkid": 2263, "latestWkid": 2263}, True, id="wkid_2263_not_102718"),
        pytest.param({"wkid": 102718}, True, id="latestWkid_absent"),
        pytest.param({"wkid": 102718, "latestWkid": 9999}, True, id="wrong_latestWkid"),
        pytest.param("EPSG:2263", True, id="spatialReference_not_an_object"),
    ],
)
def test_crs_fail_closed_rejects_everything_but_the_authoritative_pair(
    spatial_reference: object, include: bool
) -> None:
    body = _page_body(
        [_feature(1)],
        spatial_reference=spatial_reference,
        include_spatial_reference=include,
    )
    with pytest.raises(WrongCRSError) as excinfo:
        _parse(body)
    message = str(excinfo.value)
    # The typed error names expected vs received.
    assert "102718" in message
    assert "2263" in message
    assert excinfo.value.error_type == "wrong_crs"
    assert excinfo.value.detail["expected"] == {"wkid": 102718, "latestWkid": 2263}
    assert "received" in excinfo.value.detail


def test_crs_gate_runs_before_the_geometry_type_check() -> None:
    body = _page_body([_feature(1)], include_spatial_reference=False, include_geometry_type=False)
    with pytest.raises(WrongCRSError):
        _parse(body)


def test_non_polyline_page_geometry_type_is_typed_schema_drift() -> None:
    with pytest.raises(SchemaDriftError) as excinfo:
        _parse(_page_body([_feature(1)], geometry_type="esriGeometryPolygon"))
    assert "esriGeometryPolyline" in str(excinfo.value)
    with pytest.raises(SchemaDriftError):
        _parse(_page_body([_feature(1)], include_geometry_type=False))


# ---------------------------------------------------------------------------
# S3: malformed-geometry taxonomy (typed, visible, never a silent drop)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "feature,expected_status,expected_finding_fragment",
    [
        pytest.param(
            _feature(1, include_geometry=False),
            GEOMETRY_NULL,
            "geometry_key_missing",
            id="geometry_key_missing",
        ),
        pytest.param(
            _feature(1, geometry=None), GEOMETRY_NULL, "geometry_json_null", id="geometry_null"
        ),
        pytest.param(
            _feature(1, geometry=[[1.0, 2.0]]),
            GEOMETRY_MALFORMED_OBJECT,
            "geometry_not_an_object",
            id="geometry_not_a_dict",
        ),
        pytest.param(
            _feature(1, geometry={}),
            GEOMETRY_MALFORMED_OBJECT,
            "paths_key_missing",
            id="paths_key_missing",
        ),
        pytest.param(
            _feature(1, geometry={"rings": [[[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 0.0]]]}),
            GEOMETRY_UNEXPECTED_KIND,
            "non_polyline_geometry_keys:rings",
            id="polygon_payload_on_polyline_layer",
        ),
        pytest.param(
            _feature(1, geometry={"paths": "not-a-list"}),
            GEOMETRY_MALFORMED_OBJECT,
            "paths_not_a_list",
            id="paths_not_a_list",
        ),
        pytest.param(
            _feature(1, geometry={"paths": []}),
            GEOMETRY_EMPTY_PATHS,
            "paths_empty",
            id="empty_paths",
        ),
        pytest.param(
            _feature(1, paths=[[[1.0, 2.0]]]),
            GEOMETRY_DEGENERATE_PATH,
            "path_0_has_1_point",
            id="single_point_path",
        ),
        pytest.param(
            _feature(1, paths=[[["abc", 2.0], [3.0, 4.0]]]),
            GEOMETRY_MALFORMED_COORDINATE,
            "path_0_vertex_0_x_non_numeric:str",
            id="non_numeric_x",
        ),
        pytest.param(
            _feature(1, paths=[[[1.0, True], [3.0, 4.0]]]),
            GEOMETRY_MALFORMED_COORDINATE,
            "path_0_vertex_0_y_non_numeric:bool",
            id="boolean_y_is_not_numeric",
        ),
        pytest.param(
            _feature(1, paths=[[[1.0], [3.0, 4.0]]]),
            GEOMETRY_MALFORMED_COORDINATE,
            "path_0_vertex_0_is_not_an_xy_pair",
            id="vertex_missing_y",
        ),
        pytest.param(
            _feature(1, paths=[[[float("nan"), 2.0], [3.0, 4.0]]]),
            GEOMETRY_NONFINITE_COORDINATE,
            "path_0_vertex_0_nonfinite",
            id="nan_coordinate",
        ),
        pytest.param(
            _feature(1, paths=[[[1.0, 2.0], [float("inf"), 4.0]]]),
            GEOMETRY_NONFINITE_COORDINATE,
            "path_0_vertex_1_nonfinite",
            id="infinity_coordinate",
        ),
    ],
)
def test_each_malformed_geometry_condition_is_a_distinct_typed_state(
    feature: dict, expected_status: str, expected_finding_fragment: str
) -> None:
    page = _parse(_page_body([feature]))
    assert page.features_total == 1  # visible, never dropped
    entry = page.entries[0]
    assert entry.status == expected_status
    assert entry.status in GEOMETRY_STATUSES
    assert any(expected_finding_fragment in finding for finding in entry.findings)
    assert entry.paths is None
    assert entry.path_count == 0 and entry.vertex_count == 0
    assert entry.has_usable_geometry is False
    # Identity/attributes stay paired even when the geometry is refused.
    assert entry.object_id == 1
    assert entry.segment.streetwidth_raw == "60"
    assert page.usable_geometry_count == 0
    assert page.refused_geometry_count == 1


def test_a_bad_feature_never_hides_or_drops_its_page_neighbors() -> None:
    page = _parse(
        _page_body(
            [
                _feature(1, paths=[[[1.0, 2.0], [3.0, 4.0]]]),
                _feature(2, geometry=None),
                _feature(3, paths=[[[5.0, 6.0], [7.0, 8.0]]]),
            ]
        )
    )
    assert [entry.object_id for entry in page.entries] == [1, 2, 3]
    assert [entry.status for entry in page.entries] == [
        GEOMETRY_OK,
        GEOMETRY_NULL,
        GEOMETRY_OK,
    ]
    assert page.usable_geometry_count == 2
    assert page.refused_geometry_count == 1


def test_no_partial_polyline_repair_one_bad_path_refuses_the_whole_geometry() -> None:
    page = _parse(
        _page_body([_feature(1, paths=[[[1.0, 2.0], [3.0, 4.0]], [[5.0, 6.0]]])])
    )
    entry = page.entries[0]
    assert entry.status == GEOMETRY_DEGENERATE_PATH
    assert entry.paths is None  # the intact first path is NOT salvaged
    assert any("path_1_has_1_point" in finding for finding in entry.findings)


def test_extra_vertex_components_are_visible_not_silently_discarded() -> None:
    page = _parse(_page_body([_feature(1, paths=[[[1.0, 2.0, 99.5], [3.0, 4.0]]])]))
    entry = page.entries[0]
    assert entry.status == GEOMETRY_OK
    assert entry.paths == (((1.0, 2.0), (3.0, 4.0)),)
    assert any("path_0_vertex_0_extra_components:1" in f for f in entry.findings)


# ---------------------------------------------------------------------------
# S4: passthrough integrity and provenance schema
# ---------------------------------------------------------------------------


def test_high_precision_and_integer_wire_values_pass_through_untouched() -> None:
    page = _parse(
        _page_body(
            [
                _feature(
                    1,
                    paths=[[[992185.54514055, 229943.965358555], [1000, -0.000001]]],
                )
            ]
        )
    )
    paths = page.entries[0].paths
    assert paths is not None
    assert paths[0][0] == (992185.54514055, 229943.965358555)
    assert paths[0][1] == (1000.0, -0.000001)


def test_page_provenance_carries_retrieval_identity_and_digest() -> None:
    body = _fixture_body("west_100_st_two_segments.json")
    page = _parse(body)
    assert page.raw_digest == raw_body_digest(body)
    assert page.request_url == "https://example.invalid/recorded-page"
    assert page.retrieved_at == "2026-09-14T00:00:00Z"
    assert page.correlation_id == CORRELATION_ID
    assert page.source_id == SOURCE_ID
    assert page.layer == "DCM_Street_Center_Line"
    assert page.attribution == ATTRIBUTION
    assert page.crs == CRS_STAMP
    assert page.wkid == 102718 and page.latest_wkid == 2263
    assert page.geometry_type == EXPECTED_PAGE_GEOMETRY_TYPE
    assert page.units == "esriFeet"
    assert page.contract_version == "1.0.0"


# ---------------------------------------------------------------------------
# Paged entry point: single fetch per page, provenance passthrough
# ---------------------------------------------------------------------------


def test_paged_fetch_transports_each_page_exactly_once() -> None:
    metadata_body = _fixture_body("metadata.json")
    page_body = _fixture_body("west_100_st_two_segments.json")
    fetch, calls = _counting_fetcher([metadata_body, page_body])
    result = fetch_street_segment_geometries(
        borough="Manhattan", street_name="West 100 Street", fetch=fetch
    )
    assert isinstance(result, SegmentGeometryQueryResult)
    # Exactly one metadata call + one page call: no second fetch per page.
    assert len(calls) == 2
    assert calls[0] == build_metadata_url()
    assert result.pages_fetched == 1
    assert len(result.entries) == 2
    assert {entry.object_id for entry in result.entries} == {7719, 14471}
    assert all(entry.status == GEOMETRY_OK for entry in result.entries)


def test_paged_fetch_carries_transport_provenance_through() -> None:
    metadata_body = _fixture_body("metadata.json")
    page_body = _fixture_body("west_100_st_two_segments.json")
    fetch, calls = _counting_fetcher([metadata_body, page_body])
    result = fetch_street_segment_geometries(
        borough="Manhattan", street_name="West 100 Street", fetch=fetch
    )
    assert result.source_data_last_edited_ms == 1764617995374
    assert result.source_data_last_edited == "2025-12-01T19:39:55Z"
    assert result.metadata_request_url == build_metadata_url()
    assert result.raw_digests == [raw_body_digest(page_body)]
    assert result.page_urls == [calls[1]]
    assert result.drift_signals == []
    assert result.crs == CRS_STAMP
    assert result.source_id == SOURCE_ID
    assert len(result.pages) == 1
    assert result.pages[0].raw_digest == raw_body_digest(page_body)
    assert result.pages[0].correlation_id == result.correlation_id
    assert result.exceeded_transfer_limit_on_last_page is False


def test_paged_fetch_walks_multiple_pages_one_transport_each() -> None:
    metadata_body = _fixture_body("metadata.json")
    page_one = _page_body([_feature(1)], exceeded=True)
    page_two = _page_body([_feature(2)])
    fetch, calls = _counting_fetcher([metadata_body, page_one, page_two])
    result = fetch_street_segment_geometries(object_id_in=[1, 2], fetch=fetch)
    assert len(calls) == 3  # metadata + two pages, each transported once
    assert result.pages_fetched == 2
    assert [entry.object_id for entry in result.entries] == [1, 2]
    assert [page.exceeded_transfer_limit for page in result.pages] == [True, False]
    assert result.raw_digests == [raw_body_digest(page_one), raw_body_digest(page_two)]


def test_paged_fetch_fails_closed_when_a_page_carries_the_wrong_crs() -> None:
    metadata_body = _fixture_body("metadata.json")
    bad_page = _page_body([_feature(1)], spatial_reference={"wkid": 3857, "latestWkid": 3857})
    fetch, _ = _counting_fetcher([metadata_body, bad_page])
    with pytest.raises(WrongCRSError):
        fetch_street_segment_geometries(object_id=1, fetch=fetch)
