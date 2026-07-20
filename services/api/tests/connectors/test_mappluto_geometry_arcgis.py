"""MapPLUTO per-BBL geometry connector tests (task M2-T009, scenarios
GEO-S1..GEO-S12).

Offline, fixture-driven, deterministic: every HTTP interaction is replayed
from the fixture pack in services/api/tests/fixtures/mappluto_geometry/
(captured live from the official DCP_GIS MAPPLUTO ArcGIS service on
2026-07-20 UTC, plus clearly-labeled synthetic derivations) through an
injected fake transport. No test touches the network.

The invalid-geometry taxonomy fixtures (self-intersection, unclosed ring,
inverted orientation, duplicate vertices, degenerate ring, empty/null
geometry, geometry-collection surprise) are SYNTHETIC BY NECESSITY - the
live official service cannot politely produce them on demand - and each is
labeled synthetic in its file and in MANIFEST.json.

Spatial scenarios (GEO-S9) run against the REAL M2-T007 zoning-district
fixture (ZF03: the live-captured R3-2 polygon) and the REAL captured holed
lot (MPG06, Governors Island), proving the normalized lot geometry is
intersection-ready. They are TEST-level checks; no production intersection
engine exists in this task.
"""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from random import Random

import pytest
import shapely
from shapely.geometry import box

from app.connectors.bbl import BBLValidationError
from app.connectors.mappluto_geometry_arcgis import (
    BOUNDARY_TOLERANCE_FT,
    CRS_STAMP,
    MAX_FEATURES_PER_LOT,
    MPG_CANONICALIZATION_SPEC,
    OUT_FIELDS,
    PINNED_GEOS_VERSION_STRING,
    PINNED_SHAPELY_VERSION,
    REQUIRED_FIELDS,
    SERVICE_ROOT,
    SOURCE_ID,
    CircuitOpenError,
    DisallowedRequestError,
    MalformedResponseError,
    MapPlutoGeometryConnectorError,
    RateLimitedError,
    RequestBudgetExceededError,
    ResilientMapPlutoGeometryClient,
    ResultMismatchError,
    SchemaDriftError,
    SourceTimeoutError,
    UpstreamError,
    WrongCRSError,
    analyze_lot_geometry,
    build_lot_query_url,
    build_metadata_url,
    canonical_to_shapely,
    classify_spatial_relation,
    compute_area_sq_ft,
    fetch_layer_metadata,
    fetch_lot_geometry,
    normalized_geometry_digest,
    raw_body_digest,
)
from app.connectors.pluto_soda import (
    TransportFailure,
    TransportResponse,
    TransportTimeout,
)
from app.resilience import AnalysisBudget, ResilienceConfig

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "mappluto_geometry"
ZF_FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "zoning_features"

FIXED_CLOCK = lambda: datetime(2026, 7, 20, 12, 0, 0, tzinfo=UTC)  # noqa: E731

# Live-captured expectations (2026-07-20 UTC capture, fixture MPG01):
# dataLastEditDate 2026-05-27T14:36:18Z - consistent with the 26v1 release.
EXPECTED_DATA_LAST_EDITED_MS = 1779892578102
EXPECTED_MAX_RECORD_COUNT = 2000

# ---------------------------------------------------------------------------
# Cross-platform determinism anchors (GEO-S7): CI on a different OS must
# reproduce these exact digests from the committed fixtures (and from the
# fixture-independent hardcoded square), or the canonicalization pipeline is
# not deterministic. Computed with shapely 2.0.7 / GEOS 3.11.4.
# ---------------------------------------------------------------------------
SQUARE_ESRI = {"rings": [[[0, 0], [0, 100], [100, 100], [100, 0], [0, 0]]]}
SQUARE_NORMALIZED_DIGEST = (
    "sha256:6fc369acf997319e294ad1d45ab09e1fbbb9102e24a15bb5f86def2273d7279d"
)
SQUARE_ORIGINAL_DIGEST = (
    "sha256:97e9035618514d2b8a0f9d3ac8d76efe7612136aa319acbc76cd01cd2b80a734"
)
ESB_NORMALIZED_DIGEST = (
    "sha256:ed47213e6d9faa9bf53964a546e8d98f568775a60923d88dd0d392528e314db7"
)
HOLES_NORMALIZED_DIGEST = (
    "sha256:cdb238855dea0f235c44a3ac84b525d12ca9fed73bb50ffdbece1300ced4482b"
)
MULTI_NORMALIZED_DIGEST = (
    "sha256:054e72c468810961055ec9e902cef524ace784fd9bdddc533db148dd467b1de1"
)
BOWTIE_REPAIRED_NORMALIZED_DIGEST = (
    "sha256:d80588f53d1960f3cd8e5137ea4d4da86ea7eb91e0c5b37e834541be3af2e937"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def fixture_body(name: str):
    return json.loads(load_fixture(name)["response_body_raw"])


def fixture_response(name: str, headers: dict | None = None) -> TransportResponse:
    fixture = load_fixture(name)
    return TransportResponse(
        status=fixture["http_status"],
        body=fixture["response_body_raw"],
        headers=headers or {},
    )


def body_response(doc: dict, status: int = 200) -> TransportResponse:
    """Inline SYNTHETIC response built in the test body (labeled here)."""
    return TransportResponse(
        status=status, body=json.dumps(doc, ensure_ascii=False), headers={}
    )


class FakeTransport:
    """Replays a scripted sequence of responses/exceptions and records calls."""

    def __init__(self, script: list):
        self.script = list(script)
        self.calls: list[dict] = []

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        self.calls.append({"url": url, "headers": dict(headers), "timeout": timeout})
        if not self.script:
            raise AssertionError("FakeTransport script exhausted - unexpected extra request")
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


class SleepRecorder:
    def __init__(self):
        self.delays: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.delays.append(seconds)


class FakeMonotonic:
    def __init__(self):
        self.value = 1000.0

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def run_kwargs(transport: FakeTransport, **overrides):
    kwargs = dict(
        transport=transport,
        sleep=SleepRecorder(),
        clock=FIXED_CLOCK,
        rng=Random(42),
        correlation_id="test-corr",
    )
    kwargs.update(overrides)
    return kwargs


def single_lot_script() -> list[TransportResponse]:
    return [
        fixture_response("MPG01_meta.json"),
        fixture_response("MPG02_lot_single_1008350041.json"),
    ]


def make_client(script: list, config: ResilienceConfig, clock: FakeMonotonic):
    transport = FakeTransport(script)
    client = ResilientMapPlutoGeometryClient(
        config=config,
        transport=transport,
        now=clock,
        wall_clock=FIXED_CLOCK,
        sleep=SleepRecorder(),
        rng=Random(7),
    )
    return client, transport


CLIENT_CONFIG = ResilienceConfig(
    cache_ttl_seconds=100.0,
    retry_max_attempts=2,
    backoff_base_seconds=0.01,
    backoff_cap_seconds=0.02,
    breaker_failure_threshold=1,
    breaker_cooldown_seconds=60.0,
    lkg_max_age_seconds=86_400.0,
)


def district_canonical() -> list:
    """Canonical form of the REAL R3-2 zoning-district polygon from the
    accepted M2-T007 fixture pack (ZF03, captured live 2026-07-20)."""
    doc = json.loads(
        (ZF_FIXTURE_DIR / "ZF03_query_nyzd_single_R3-2.json").read_text(
            encoding="utf-8"
        )
    )
    feature = json.loads(doc["response_body_raw"])["features"][0]
    assessment = analyze_lot_geometry(feature["geometry"], crs=dict(CRS_STAMP))
    assert assessment.status == "valid"
    return assessment.canonical_geometry


def box_canonical(minx: float, miny: float, maxx: float, maxy: float) -> list:
    """Synthetic axis-aligned test rectangle in EPSG:2263 feet, expressed
    through the connector's own canonical pipeline (esri CW exterior)."""
    ring = [
        [minx, miny], [minx, maxy], [maxx, maxy], [maxx, miny], [minx, miny]
    ]
    assessment = analyze_lot_geometry({"rings": [ring]}, crs=dict(CRS_STAMP))
    assert assessment.status == "valid"
    return assessment.canonical_geometry


# ---------------------------------------------------------------------------
# GEO-S1 - single-lot polygon: metadata validation, identifier/result
# validation, provenance
# ---------------------------------------------------------------------------


def test_s1_metadata_snapshot_validates_and_stamps_provenance() -> None:
    transport = FakeTransport([fixture_response("MPG01_meta.json")])
    metadata = fetch_layer_metadata(**run_kwargs(transport))
    assert metadata.object_id_field == "OBJECTID"
    assert metadata.max_record_count == EXPECTED_MAX_RECORD_COUNT
    assert metadata.wkid == 102718 and metadata.latest_wkid == 2263
    assert metadata.geometry_type == "esriGeometryPolygon"
    assert metadata.supports_pagination and metadata.supports_order_by
    assert metadata.source_data_last_edited_ms == EXPECTED_DATA_LAST_EDITED_MS
    assert metadata.source_data_last_edited == "2026-05-27T14:36:18Z"
    assert metadata.request_url == build_metadata_url()
    assert metadata.raw_digest.startswith("sha256:")
    assert metadata.drift_signals == []


def test_s1_required_fields_constant_matches_captured_layer_schema() -> None:
    """Transcription guard: the connector's REQUIRED_FIELDS constants must
    match the live-captured MAPPLUTO layer schema (fixture MPG01)."""
    doc = fixture_body("MPG01_meta.json")
    live = {f["name"]: f["type"] for f in doc["fields"]}
    assert len(live) == 103  # research section 2.5: 103 PascalCase fields
    for name, expected_type in REQUIRED_FIELDS.items():
        assert live.get(name) == expected_type, name
    assert set(OUT_FIELDS) == set(REQUIRED_FIELDS)


def test_s1_single_lot_result_validated_against_request() -> None:
    transport = FakeTransport(single_lot_script())
    result = fetch_lot_geometry("1008350041", **run_kwargs(transport))
    assert result.outcome == "single_feature"
    assert result.review_required is False
    assert result.requested_bbl == "1008350041"
    assert (result.borough, result.block, result.lot) == (1, 835, 41)
    assert result.attributes["BBL"] == 1008350041
    assert result.attributes["Version"] == "26v1"
    assert result.identifier_conflicts == []
    assert result.geometry.status == "valid"
    assert result.geometry.geometry_kind == "polygon"
    # Provenance stamps (endpoint, layer metadata, retrieval + source edit
    # timestamps, CRS, separate digests).
    assert result.request_url == build_lot_query_url("1008350041")
    assert result.request_url == load_fixture(
        "MPG02_lot_single_1008350041.json"
    )["request_url"]
    assert result.metadata_request_url == build_metadata_url()
    assert result.retrieved_at == "2026-07-20T12:00:00Z"
    assert result.source_data_last_edited == "2026-05-27T14:36:18Z"
    assert result.crs == CRS_STAMP
    assert result.raw_digest != result.metadata_raw_digest
    assert result.digest_canonicalization == MPG_CANONICALIZATION_SPEC
    assert result.staleness is None


def test_s1_socrata_style_bbl_input_is_normalized_before_query() -> None:
    transport = FakeTransport(single_lot_script())
    result = fetch_lot_geometry("1008350041.00000000", **run_kwargs(transport))
    assert result.requested_bbl == "1008350041"
    assert "BBL%3D1008350041" in transport.calls[1]["url"]


@pytest.mark.parametrize(
    ("fixture", "expected_fragment"),
    [
        ("MPG91_meta_missing_bbl_field_synthetic.json", "missing"),
        ("MPG92_meta_retyped_block_synthetic.json", "type"),
        ("MPG93_meta_missing_objectid_synthetic.json", "objectIdField"),
        ("MPG94_meta_missing_maxrecordcount_synthetic.json", "maxRecordCount"),
    ],
)
def test_s1_metadata_negatives_fail_typed(fixture, expected_fragment) -> None:
    transport = FakeTransport([fixture_response(fixture)])
    with pytest.raises(SchemaDriftError) as excinfo:
        fetch_layer_metadata(**run_kwargs(transport))
    assert excinfo.value.error_type == "schema_drift"
    assert expected_fragment.lower() in str(excinfo.value).lower()


def test_s1_wrong_lot_returned_is_typed_result_mismatch() -> None:
    transport = FakeTransport(
        [
            fixture_response("MPG01_meta.json"),
            fixture_response("MPG97_wrong_lot_returned_synthetic.json"),
        ]
    )
    with pytest.raises(ResultMismatchError) as excinfo:
        fetch_lot_geometry("1008350041", **run_kwargs(transport))
    assert excinfo.value.error_type == "result_mismatch"
    assert excinfo.value.detail["requested_bbl"] == "1008350041"


def test_s1_component_conflict_is_visible_and_review_required() -> None:
    transport = FakeTransport(
        [
            fixture_response("MPG01_meta.json"),
            fixture_response("MPG98_component_conflict_synthetic.json"),
        ]
    )
    result = fetch_lot_geometry("1008350041", **run_kwargs(transport))
    assert result.review_required is True
    assert len(result.identifier_conflicts) == 1
    conflict = result.identifier_conflicts[0]
    assert conflict["field"] == "block"
    assert conflict["bbl_derived_value"] == 835
    assert conflict["component_value_parsed"] == 999
    assert any("identifier_conflict" in note for note in result.notes)


# ---------------------------------------------------------------------------
# GEO-S2 - multipolygon + holes normalize with canonical ordering
# ---------------------------------------------------------------------------


def test_s2_holed_polygon_normalizes_with_stable_digest() -> None:
    doc = fixture_body("MPG06_lot_holes_1000010010.json")
    assessment = analyze_lot_geometry(
        doc["features"][0]["geometry"], crs=dict(CRS_STAMP)
    )
    assert assessment.status == "valid"
    assert assessment.geometry_kind == "polygon"
    assert assessment.exterior_ring_count == 1
    assert assessment.hole_count == 2
    assert assessment.normalized_digest == HOLES_NORMALIZED_DIGEST
    # Canonical form: exterior first, holes after, holes sorted by their
    # serialized form; every ring an OPEN cycle of two-decimal strings.
    polygon = assessment.canonical_geometry[0]
    assert len(polygon) == 3
    hole_keys = [json.dumps(ring, separators=(",", ":")) for ring in polygon[1:]]
    assert hole_keys == sorted(hole_keys)
    for ring in polygon:
        assert ring[0] != ring[-1]
        assert ring[0] == min(ring)
        for x, _y in ring:
            assert "." in x and len(x.split(".")[1]) == 2


def test_s2_multipolygon_normalizes_with_stable_digest() -> None:
    doc = fixture_body("MPG07_lot_multipolygon_4142600001.json")
    assessment = analyze_lot_geometry(
        doc["features"][0]["geometry"], crs=dict(CRS_STAMP)
    )
    assert assessment.status == "valid"
    assert assessment.geometry_kind == "multipolygon"
    assert assessment.exterior_ring_count == 2
    assert assessment.normalized_digest == MULTI_NORMALIZED_DIGEST
    exterior_keys = [
        json.dumps(polygon[0], separators=(",", ":"))
        for polygon in assessment.canonical_geometry
    ]
    assert exterior_keys == sorted(exterior_keys)


def test_s2_ring_rotation_and_member_order_do_not_change_normalized_digest() -> None:
    doc = fixture_body("MPG07_lot_multipolygon_4142600001.json")
    geometry = doc["features"][0]["geometry"]
    swapped = {"rings": [geometry["rings"][1], geometry["rings"][0]]}
    original = analyze_lot_geometry(geometry, crs=dict(CRS_STAMP))
    reordered = analyze_lot_geometry(swapped, crs=dict(CRS_STAMP))
    assert original.normalized_digest == reordered.normalized_digest
    # ...while the ORIGINAL digests differ: the verbatim source geometry is
    # pinned separately, exactly as transported.
    assert original.original_geometry_digest != reordered.original_geometry_digest


# ---------------------------------------------------------------------------
# GEO-S3 - zero/one/multiple features are explicit typed outcomes
# ---------------------------------------------------------------------------


def test_s3_no_feature_is_explicit_typed_outcome_not_error() -> None:
    transport = FakeTransport(
        [
            fixture_response("MPG01_meta.json"),
            fixture_response("MPG03_lot_nofeature_5999999999.json"),
        ]
    )
    result = fetch_lot_geometry("5999999999", **run_kwargs(transport))
    assert result.outcome == "no_feature"
    assert result.geometry is None
    assert result.attributes is None
    assert result.features == []
    assert result.review_required is False
    assert any("no_feature" in note for note in result.notes)


def test_s3_multiple_features_is_review_required_never_first_pick() -> None:
    transport = FakeTransport(
        [
            fixture_response("MPG01_meta.json"),
            fixture_response("MPG96_multiple_features_synthetic.json"),
        ]
    )
    result = fetch_lot_geometry("1008350041", **run_kwargs(transport))
    assert result.outcome == "multiple_features"
    assert result.review_required is True
    # No single feature is picked: no attributes, no geometry assessment,
    # ALL features preserved verbatim for review.
    assert result.attributes is None
    assert result.geometry is None
    assert len(result.features) == 2
    assert any("never silently picks" in note for note in result.notes)


def test_s3_exceeded_transfer_limit_forces_multiple_outcome() -> None:
    # Inline SYNTHETIC: a full bounded page with exceededTransferLimit true
    # means even more features exist upstream - typed multiple_features.
    doc = fixture_body("MPG96_multiple_features_synthetic.json")
    import copy as _copy

    while len(doc["features"]) < MAX_FEATURES_PER_LOT:
        twin = _copy.deepcopy(doc["features"][0])
        twin["attributes"]["OBJECTID"] = (
            max(f["attributes"]["OBJECTID"] for f in doc["features"]) + 1
        )
        doc["features"].append(twin)
    doc["exceededTransferLimit"] = True
    transport = FakeTransport(
        [fixture_response("MPG01_meta.json"), body_response(doc)]
    )
    result = fetch_lot_geometry("1008350041", **run_kwargs(transport))
    assert result.outcome == "multiple_features"
    assert result.exceeded_transfer_limit is True
    assert any("more exist beyond" in note for note in result.notes)


# ---------------------------------------------------------------------------
# GEO-S4 - condominium billing-lot semantics (research section 2.5)
# ---------------------------------------------------------------------------


def test_s4_condo_billing_lot_resolves_with_complex_semantics() -> None:
    transport = FakeTransport(
        [
            fixture_response("MPG01_meta.json"),
            fixture_response("MPG04_lot_condo_billing_1000157501.json"),
        ]
    )
    result = fetch_lot_geometry("1000157501", **run_kwargs(transport))
    assert result.outcome == "single_feature"
    assert result.condo["classification"] == "condo_billing_lot"
    assert result.condo["condo_no"] == 1025
    assert "entire condominium complex" in result.condo["note"]
    # The connector NEVER claims per-unit polygons exist.
    assert "per-unit tax-lot polygons do not exist" in result.condo["note"]
    assert result.geometry.status == "valid"


def test_s4_condo_unit_lot_query_is_empty_with_billing_redirect_note() -> None:
    """Live-captured evidence for research section 2.5: the unit lot
    (1000151001) on the SAME block as billing lot 1000157501 has no
    MapPLUTO record; the typed outcome explains billing-BBL resolution."""
    transport = FakeTransport(
        [
            fixture_response("MPG01_meta.json"),
            fixture_response("MPG05_lot_condo_unit_1000151001.json"),
        ]
    )
    result = fetch_lot_geometry("1000151001", **run_kwargs(transport))
    assert result.outcome == "no_feature"
    assert result.condo["classification"] == "condo_unit_lot_query"
    assert "billing" in result.condo["note"]
    assert any("resolve the billing BBL" in note for note in result.notes)


def test_s4_condo_unit_lot_with_polygon_is_flagged_for_review() -> None:
    # Inline SYNTHETIC: a unit-range lot that unexpectedly returns its own
    # polygon contradicts the documented semantics - flagged, not trusted.
    doc = fixture_body("MPG04_lot_condo_billing_1000157501.json")
    doc["features"][0]["attributes"]["BBL"] = 1000151001
    doc["features"][0]["attributes"]["Lot"] = 1001
    transport = FakeTransport(
        [fixture_response("MPG01_meta.json"), body_response(doc)]
    )
    result = fetch_lot_geometry("1000151001", **run_kwargs(transport))
    assert result.outcome == "single_feature"
    assert result.review_required is True
    assert "condo_unit_lot_with_polygon" in result.drift_signals


# ---------------------------------------------------------------------------
# GEO-S5 - invalid-geometry taxonomy: each shape maps to an explicit
# typed state (fixtures labeled synthetic by necessity)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("fixture", "expected_status", "expected_finding"),
    [
        ("MPG80_geom_self_intersection_synthetic.json", "repaired", "self_intersection"),
        ("MPG81_geom_unclosed_ring_synthetic.json", "repaired", "unclosed_ring"),
        ("MPG82_geom_duplicate_vertices_synthetic.json", "repaired", "duplicate_vertices"),
        ("MPG83_geom_degenerate_ring_synthetic.json", "repaired", "degenerate_ring"),
        ("MPG84_geom_empty_rings_synthetic.json", "invalid_geometry", "empty_geometry"),
        ("MPG85_geom_null_synthetic.json", "invalid_geometry", "null_geometry"),
        (
            "MPG86_geom_orientation_all_ccw_synthetic.json",
            "review_required",
            "invalid_orientation",
        ),
        (
            "MPG87_geom_collection_paths_synthetic.json",
            "invalid_geometry",
            "geometry_collection",
        ),
        (
            "MPG88_geom_hole_outside_shell_synthetic.json",
            "review_required",
            "invalid_orientation",
        ),
    ],
)
def test_s5_taxonomy_shape_maps_to_explicit_typed_state(
    fixture, expected_status, expected_finding
) -> None:
    doc = fixture_body(fixture)
    geometry = doc["features"][0].get("geometry")
    assessment = analyze_lot_geometry(geometry, crs=dict(CRS_STAMP))
    assert assessment.status == expected_status
    assert expected_finding in assessment.findings
    # The verbatim original digest is ALWAYS preserved, whatever the state.
    assert assessment.original_geometry_digest.startswith("sha256:")
    if expected_status in ("invalid_geometry", "review_required"):
        assert assessment.normalized_digest is None
        assert assessment.canonical_geometry is None


def test_s5_missing_geometry_key_is_null_geometry() -> None:
    assessment = analyze_lot_geometry(None, crs=dict(CRS_STAMP))
    assert assessment.status == "invalid_geometry"
    assert assessment.findings == ["null_geometry"]


def test_s5_nonfinite_coordinate_is_typed_invalid() -> None:
    geometry = {
        "rings": [[[0, 0], [0, float("nan")], [100, 100], [100, 0], [0, 0]]]
    }
    assessment = analyze_lot_geometry(geometry, crs=dict(CRS_STAMP))
    assert assessment.status == "invalid_geometry"
    assert "nonfinite_coordinate" in assessment.findings


def test_s5_taxonomy_states_reach_lot_result_and_review_flag() -> None:
    transport = FakeTransport(
        [
            fixture_response("MPG01_meta.json"),
            fixture_response("MPG86_geom_orientation_all_ccw_synthetic.json"),
        ]
    )
    result = fetch_lot_geometry("1008350041", **run_kwargs(transport))
    assert result.outcome == "single_feature"
    assert result.geometry.status == "review_required"
    assert result.review_required is True
    assert result.area_sq_ft is None
    assert any("geometry_status=review_required" in note for note in result.notes)


def test_s5_all_synthetic_fixtures_are_labeled_synthetic() -> None:
    manifest = json.loads(
        (FIXTURE_DIR / "MANIFEST.json").read_text(encoding="utf-8")
    )
    for entry in manifest["fixtures"]:
        if "synthetic" in entry["file"]:
            assert entry["classification"] == "synthetic", entry["file"]
            assert entry["derived_from"], entry["file"]
        else:
            assert entry["classification"] == "raw", entry["file"]


# ---------------------------------------------------------------------------
# GEO-S6 - no-silent-repair policy
# ---------------------------------------------------------------------------


def test_s6_repair_records_method_versions_and_separate_digests() -> None:
    doc = fixture_body("MPG80_geom_self_intersection_synthetic.json")
    assessment = analyze_lot_geometry(
        doc["features"][0]["geometry"], crs=dict(CRS_STAMP)
    )
    assert assessment.status == "repaired"
    assert assessment.repaired is True
    methods = [repair["method"] for repair in assessment.repairs]
    assert "shapely_make_valid" in methods
    make_valid_repair = next(
        repair for repair in assessment.repairs
        if repair["method"] == "shapely_make_valid"
    )
    assert make_valid_repair["shapely_version"] == PINNED_SHAPELY_VERSION
    assert make_valid_repair["geos_version"] == PINNED_GEOS_VERSION_STRING
    assert "area_before_sq_ft" in make_valid_repair["detail"]
    # Original AND repaired digests kept separately - and different.
    assert assessment.original_geometry_digest.startswith("sha256:")
    assert assessment.normalized_digest == BOWTIE_REPAIRED_NORMALIZED_DIGEST
    assert assessment.original_geometry_digest != assessment.normalized_digest


def test_s6_structural_repairs_preserve_original_digest_separately() -> None:
    for fixture in (
        "MPG81_geom_unclosed_ring_synthetic.json",
        "MPG82_geom_duplicate_vertices_synthetic.json",
        "MPG83_geom_degenerate_ring_synthetic.json",
    ):
        doc = fixture_body(fixture)
        assessment = analyze_lot_geometry(
            doc["features"][0]["geometry"], crs=dict(CRS_STAMP)
        )
        assert assessment.status == "repaired", fixture
        assert assessment.repairs, fixture
        assert assessment.original_geometry_digest != assessment.normalized_digest


def test_s6_uncharacterizable_topology_is_review_required_not_repaired() -> None:
    for fixture in (
        "MPG86_geom_orientation_all_ccw_synthetic.json",
        "MPG88_geom_hole_outside_shell_synthetic.json",
    ):
        doc = fixture_body(fixture)
        assessment = analyze_lot_geometry(
            doc["features"][0]["geometry"], crs=dict(CRS_STAMP)
        )
        assert assessment.status == "review_required", fixture
        assert "shapely_make_valid" not in [
            repair["method"] for repair in assessment.repairs
        ]
        assert assessment.normalized_digest is None


def test_s6_repaired_geometry_never_presented_as_untouched_source() -> None:
    transport = FakeTransport(
        [
            fixture_response("MPG01_meta.json"),
            fixture_response("MPG81_geom_unclosed_ring_synthetic.json"),
        ]
    )
    result = fetch_lot_geometry("1008350041", **run_kwargs(transport))
    assert result.geometry.status == "repaired"
    assert any(
        "NOT the untouched official source" in note for note in result.notes
    )
    # The verbatim transported bytes and original geometry digest survive.
    assert result.raw_digest == raw_body_digest(
        load_fixture("MPG81_geom_unclosed_ring_synthetic.json")["response_body_raw"]
    )
    assert result.geometry.original_geometry_digest.startswith("sha256:")


def test_s6_valid_geometry_records_no_repairs() -> None:
    doc = fixture_body("MPG02_lot_single_1008350041.json")
    assessment = analyze_lot_geometry(
        doc["features"][0]["geometry"], crs=dict(CRS_STAMP)
    )
    assert assessment.status == "valid"
    assert assessment.repairs == []
    assert assessment.repaired is False


# ---------------------------------------------------------------------------
# GEO-S7 - deterministic geometry digests with pinned Shapely/GEOS
# ---------------------------------------------------------------------------


def test_s7_shapely_and_geos_versions_match_the_exact_pins() -> None:
    """The digest pipeline is proven against EXACTLY these library
    versions (packet safeguard 5). A mismatch means the environment does
    not match the pinned dependency set - fix the environment or re-pin
    deliberately (dedicated commit + re-anchored digests), never silently."""
    assert shapely.__version__ == PINNED_SHAPELY_VERSION
    assert shapely.geos_version_string == PINNED_GEOS_VERSION_STRING


def test_s7_hardcoded_cross_platform_anchor_reproduces_exactly() -> None:
    """Fixture-independent anchor: any platform/CI must reproduce this
    digest byte-identically from a hardcoded esri square, or the
    canonicalization pipeline is not deterministic."""
    assessment = analyze_lot_geometry(SQUARE_ESRI, crs=dict(CRS_STAMP))
    assert assessment.normalized_digest == SQUARE_NORMALIZED_DIGEST
    assert assessment.original_geometry_digest == SQUARE_ORIGINAL_DIGEST
    assert assessment.area_sq_ft == 10000.0


def test_s7_real_fixture_digests_reproduce_across_two_runs() -> None:
    digests = []
    for _ in range(2):
        doc = fixture_body("MPG02_lot_single_1008350041.json")
        assessment = analyze_lot_geometry(
            doc["features"][0]["geometry"], crs=dict(CRS_STAMP)
        )
        digests.append(
            (assessment.original_geometry_digest, assessment.normalized_digest)
        )
    assert digests[0] == digests[1]
    assert digests[0][1] == ESB_NORMALIZED_DIGEST


def test_s7_raw_original_and_normalized_digests_are_distinct_records() -> None:
    transport = FakeTransport(single_lot_script())
    result = fetch_lot_geometry("1008350041", **run_kwargs(transport))
    raw = result.raw_digest
    original = result.geometry.original_geometry_digest
    normalized = result.geometry.normalized_digest
    assert len({raw, original, normalized}) == 3
    assert raw == raw_body_digest(
        load_fixture("MPG02_lot_single_1008350041.json")["response_body_raw"]
    )
    assert normalized == ESB_NORMALIZED_DIGEST


def test_s7_digest_spec_is_self_describing_and_not_wkb() -> None:
    assert "mappluto-geom-canonical-1" in MPG_CANONICALIZATION_SPEC
    assert "0.01 ft" in MPG_CANONICALIZATION_SPEC
    assert "NOT" in MPG_CANONICALIZATION_SPEC and "WKB" in MPG_CANONICALIZATION_SPEC
    assert PINNED_SHAPELY_VERSION in MPG_CANONICALIZATION_SPEC
    assert PINNED_GEOS_VERSION_STRING in MPG_CANONICALIZATION_SPEC
    # And the digest is recomputable from the spec's canonical form.
    doc = fixture_body("MPG06_lot_holes_1000010010.json")
    assessment = analyze_lot_geometry(
        doc["features"][0]["geometry"], crs=dict(CRS_STAMP)
    )
    recomputed = normalized_geometry_digest(assessment.canonical_geometry)
    assert recomputed == assessment.normalized_digest == HOLES_NORMALIZED_DIGEST


# ---------------------------------------------------------------------------
# GEO-S8 - CRS safety: validation before interpretation; projected feet
# only; no degrees-based area path
# ---------------------------------------------------------------------------


def test_s8_wrong_metadata_crs_is_typed_before_any_coordinate_use() -> None:
    transport = FakeTransport([fixture_response("MPG90_meta_wrong_crs_synthetic.json")])
    with pytest.raises(WrongCRSError) as excinfo:
        fetch_layer_metadata(**run_kwargs(transport))
    assert excinfo.value.error_type == "wrong_crs"


def test_s8_wrong_query_crs_is_typed_before_geometry_interpretation() -> None:
    transport = FakeTransport(
        [
            fixture_response("MPG01_meta.json"),
            fixture_response("MPG99_query_wrong_crs_synthetic.json"),
        ]
    )
    with pytest.raises(WrongCRSError) as excinfo:
        fetch_lot_geometry("1008350041", **run_kwargs(transport))
    assert excinfo.value.error_type == "wrong_crs"


def test_s8_analysis_refuses_non_authoritative_crs() -> None:
    with pytest.raises(WrongCRSError):
        analyze_lot_geometry(SQUARE_ESRI, crs={"wkid": 4326, "latest_wkid": 4326})
    with pytest.raises(WrongCRSError):
        analyze_lot_geometry(SQUARE_ESRI, crs=None)


def test_s8_degrees_based_area_path_does_not_exist() -> None:
    """Negative proof: the ONLY area function refuses every CRS except the
    validated EPSG:2263 projected-feet CRS - passing geographic degrees
    (4326) or anything else is the typed wrong_crs failure."""
    geographic_like = box(-74.01, 40.70, -73.99, 40.72)
    for bad_crs in (
        {"wkid": 4326, "latest_wkid": 4326},
        {"wkid": 3857, "latest_wkid": 3857},
        {},
        None,
    ):
        with pytest.raises(WrongCRSError):
            compute_area_sq_ft(geographic_like, crs=bad_crs)


def test_s8_area_is_projected_feet_and_cross_checked_with_official_value() -> None:
    """Documented deterministic transformation test: the esri-rings ->
    shapely -> planar-area path in EPSG:2263 reproduces the official
    Shape__Area attribute (same CRS, same units) within float tolerance."""
    transport = FakeTransport(single_lot_script())
    result = fetch_lot_geometry("1008350041", **run_kwargs(transport))
    assert result.shape_area_attribute_sq_ft == 97113.6875  # verbatim official
    assert result.area_sq_ft == pytest.approx(97113.6875, rel=1e-6)
    assert result.geometry.area_crs["authority"].startswith("EPSG:2263")
    assert not any("shape_area_divergence" in note for note in result.notes)


def test_s8_area_divergence_is_surfaced_never_reconciled() -> None:
    # Inline SYNTHETIC: official attribute disagrees with computed area.
    doc = fixture_body("MPG02_lot_single_1008350041.json")
    doc["features"][0]["attributes"]["Shape__Area"] = 50000.0
    transport = FakeTransport(
        [fixture_response("MPG01_meta.json"), body_response(doc)]
    )
    result = fetch_lot_geometry("1008350041", **run_kwargs(transport))
    assert result.shape_area_attribute_sq_ft == 50000.0
    assert result.area_sq_ft == pytest.approx(97113.6875, rel=1e-6)
    assert any("shape_area_divergence" in note for note in result.notes)


# ---------------------------------------------------------------------------
# GEO-S9 - spatial scenarios against the M2-T007 district fixtures
# (TEST-level intersection-readiness; tolerance behavior explicitly named)
# ---------------------------------------------------------------------------

# Anchors probed from the REAL R3-2 polygon (ZF03): interior representative
# point of the district eroded by 100 ft, and the polygon bounds.
R32_DEEP_POINT = (997482.04, 163293.94)
R32_BOUNDS = (997012.99, 162583.65, 997933.57, 163807.58)


def test_s9_tolerance_is_named_and_matches_the_official_accuracy() -> None:
    assert BOUNDARY_TOLERANCE_FT == 20.0
    relation = classify_spatial_relation(
        box_canonical(0, 0, 10, 10), box_canonical(0, 0, 10, 10)
    )
    assert "plus-or-minus 20 ft" in relation["tolerance_basis"]


def test_s9_lot_fully_inside_district() -> None:
    x, y = R32_DEEP_POINT
    lot = box_canonical(x - 25, y - 25, x + 25, y + 25)
    relation = classify_spatial_relation(lot, district_canonical())
    assert relation["relation"] == "inside"
    assert relation["intersection_area_sq_ft"] == pytest.approx(2500.0, rel=1e-6)


def test_s9_lot_fully_outside_district() -> None:
    max_x = R32_BOUNDS[2]
    y = R32_DEEP_POINT[1]
    lot = box_canonical(max_x + 500, y - 25, max_x + 550, y + 25)
    relation = classify_spatial_relation(lot, district_canonical())
    assert relation["relation"] == "outside"
    assert relation["distance_ft"] > BOUNDARY_TOLERANCE_FT
    assert relation["intersection_area_sq_ft"] == 0.0


def test_s9_boundary_touch_is_uncertain_never_silently_classified() -> None:
    """A 20x20 ft lot centered ON the district boundary lies entirely
    within the plus-or-minus 20 ft tolerance band (corner distance 14.1 ft
    from center): typed boundary_uncertain, never inside/outside."""
    district = district_canonical()
    shape = canonical_to_shapely(district)
    boundary_point = shape.exterior.interpolate(0.5, normalized=True)
    x, y = boundary_point.x, boundary_point.y
    lot = box_canonical(x - 10, y - 10, x + 10, y + 10)
    relation = classify_spatial_relation(lot, district)
    assert relation["relation"] == "boundary_uncertain"


def test_s9_touching_lot_from_outside_is_uncertain() -> None:
    district = district_canonical()
    shape = canonical_to_shapely(district)
    boundary_point = shape.exterior.interpolate(0.25, normalized=True)
    x, y = boundary_point.x, boundary_point.y
    # A lot placed just outside, within the tolerance band (distance < 20).
    lot = box_canonical(x + 5, y + 5, x + 15, y + 15)
    relation = classify_spatial_relation(lot, district)
    assert relation["relation"] in ("boundary_uncertain", "outside")
    if relation["distance_ft"] <= BOUNDARY_TOLERANCE_FT:
        assert relation["relation"] == "boundary_uncertain"


def test_s9_split_intersection_detected_beyond_tolerance() -> None:
    """A long lot from deep inside the district to far beyond it has parts
    firmly inside AND firmly outside (both beyond the 20 ft band)."""
    x, y = R32_DEEP_POINT
    max_x = R32_BOUNDS[2]
    lot = box_canonical(x - 25, y - 25, max_x + 200, y + 25)
    relation = classify_spatial_relation(lot, district_canonical())
    assert relation["relation"] == "split_intersection"
    assert relation["intersection_area_sq_ft"] > 0.0


def test_s9_hole_interaction_uses_the_real_holed_lot() -> None:
    """Hole semantics against the REAL captured Governors Island polygon
    (MPG06): a lot deep inside a hole is OUTSIDE the polygon; a lot
    covering the hole and its surroundings is a split; a lot on the hole
    boundary is uncertain."""
    doc = fixture_body("MPG06_lot_holes_1000010010.json")
    assessment = analyze_lot_geometry(
        doc["features"][0]["geometry"], crs=dict(CRS_STAMP)
    )
    reference = assessment.canonical_geometry
    # Hole 0 (probed): bounds (979139.94, 191618.64, 979539.16, 191832.41),
    # deep-in-hole point (979331.85, 191738.05).
    deep = box_canonical(979331.85 - 20, 191738.05 - 20, 979331.85 + 20, 191738.05 + 20)
    assert classify_spatial_relation(deep, reference)["relation"] == "outside"
    covering = box_canonical(979039.94, 191518.64, 979639.16, 191932.41)
    assert (
        classify_spatial_relation(covering, reference)["relation"]
        == "split_intersection"
    )
    shape = canonical_to_shapely(reference)
    hole_boundary = shape.interiors[0].interpolate(0.5, normalized=True)
    on_boundary = box_canonical(
        hole_boundary.x - 10, hole_boundary.y - 10,
        hole_boundary.x + 10, hole_boundary.y + 10,
    )
    assert (
        classify_spatial_relation(on_boundary, reference)["relation"]
        == "boundary_uncertain"
    )


def test_s9_invalid_geometry_yields_no_canonical_form_to_classify() -> None:
    doc = fixture_body("MPG86_geom_orientation_all_ccw_synthetic.json")
    assessment = analyze_lot_geometry(
        doc["features"][0]["geometry"], crs=dict(CRS_STAMP)
    )
    assert assessment.canonical_geometry is None  # nothing enters intersection


def test_s9_repaired_geometry_classifies_deterministically() -> None:
    doc = fixture_body("MPG80_geom_self_intersection_synthetic.json")
    assessment = analyze_lot_geometry(
        doc["features"][0]["geometry"], crs=dict(CRS_STAMP)
    )
    assert assessment.status == "repaired"
    reference = box_canonical(987600.0, 211400.0, 987900.0, 211700.0)
    first = classify_spatial_relation(assessment.canonical_geometry, reference)
    second = classify_spatial_relation(assessment.canonical_geometry, reference)
    assert first == second
    assert first["relation"] == "inside"


def test_s9_repeated_runs_reproduce_identical_classifications() -> None:
    district = district_canonical()
    x, y = R32_DEEP_POINT
    lot = box_canonical(x - 25, y - 25, x + 25, y + 25)
    results = [classify_spatial_relation(lot, district) for _ in range(3)]
    assert results[0] == results[1] == results[2]


# ---------------------------------------------------------------------------
# GEO-S10 - allowlist, bounded parameters, resilience, malformed-never-empty
# ---------------------------------------------------------------------------


def test_s10_every_built_url_targets_the_pinned_official_root() -> None:
    assert build_metadata_url().startswith(SERVICE_ROOT + "/MAPPLUTO/")
    url = build_lot_query_url("1008350041")
    assert url.startswith(SERVICE_ROOT + "/MAPPLUTO/FeatureServer/0/query?")
    assert f"resultRecordCount={MAX_FEATURES_PER_LOT}" in url
    assert "outFields=" + "%2C".join(OUT_FIELDS) in url


def test_s10_url_builder_reproduces_captured_fixture_urls() -> None:
    assert build_metadata_url() == load_fixture("MPG01_meta.json")["request_url"]
    assert (
        build_lot_query_url("1000157501")
        == load_fixture("MPG04_lot_condo_billing_1000157501.json")["request_url"]
    )


def test_s10_invalid_bbl_is_refused_before_any_network_io() -> None:
    transport = FakeTransport([])
    for bad in ("", "12345", "6000010001", "10083500zz", None, -1):
        with pytest.raises(BBLValidationError):
            fetch_lot_geometry(bad, **run_kwargs(transport))
    assert transport.calls == []


def test_s10_url_builder_requires_canonical_form() -> None:
    with pytest.raises(DisallowedRequestError):
        build_lot_query_url("1008350041.00000000")
    with pytest.raises(BBLValidationError):
        build_lot_query_url("not-a-bbl")


def test_s10_timeout_persists_to_typed_timeout_with_bounded_retries() -> None:
    transport = FakeTransport([TransportTimeout()] * 3)
    with pytest.raises(SourceTimeoutError) as excinfo:
        fetch_layer_metadata(**run_kwargs(transport, max_attempts=3))
    assert excinfo.value.error_type == "timeout"
    assert len(transport.calls) == 3


def test_s10_429_persisted_is_typed_rate_limited() -> None:
    transport = FakeTransport(
        [fixture_response("MPG103_rate_limited_429_synthetic.json")] * 2
    )
    with pytest.raises(RateLimitedError) as excinfo:
        fetch_layer_metadata(**run_kwargs(transport, max_attempts=2))
    assert excinfo.value.error_type == "rate_limited"


def test_s10_retry_after_honored_exactly_then_success() -> None:
    sleeper = SleepRecorder()
    transport = FakeTransport(
        [
            fixture_response(
                "MPG103_rate_limited_429_synthetic.json", headers={"Retry-After": "7"}
            ),
            fixture_response("MPG01_meta.json"),
        ]
    )
    metadata = fetch_layer_metadata(
        **run_kwargs(transport, sleep=sleeper, max_attempts=2)
    )
    assert metadata.max_record_count == EXPECTED_MAX_RECORD_COUNT
    assert sleeper.delays == [7.0]


def test_s10_network_failure_persists_to_typed_upstream_error() -> None:
    transport = FakeTransport([TransportFailure("connection refused")] * 2)
    with pytest.raises(UpstreamError):
        fetch_layer_metadata(**run_kwargs(transport, max_attempts=2))


def test_s10_arcgis_error_object_with_http_200_is_upstream_error() -> None:
    transport = FakeTransport(
        [
            fixture_response("MPG01_meta.json"),
            fixture_response("MPG102_arcgis_error_http200_synthetic.json"),
        ]
    )
    with pytest.raises(UpstreamError) as excinfo:
        fetch_lot_geometry("1008350041", **run_kwargs(transport))
    assert excinfo.value.detail["arcgis_error_code"] == 400


@pytest.mark.parametrize(
    "fixture",
    [
        "MPG100_malformed_missing_features_synthetic.json",
        "MPG101_malformed_truncated_synthetic.json",
    ],
)
def test_s10_malformed_response_is_typed_never_an_empty_result(fixture) -> None:
    transport = FakeTransport(
        [fixture_response("MPG01_meta.json"), fixture_response(fixture)]
    )
    with pytest.raises(MalformedResponseError) as excinfo:
        fetch_lot_geometry("1008350041", **run_kwargs(transport))
    assert excinfo.value.error_type == "malformed_response"


def test_s10_request_budget_exhaustion_is_typed_and_pre_io() -> None:
    budget = AnalysisBudget(analysis_id="a1", max_upstream_requests=1)
    transport = FakeTransport(single_lot_script())
    with pytest.raises(RequestBudgetExceededError) as excinfo:
        fetch_lot_geometry("1008350041", **run_kwargs(transport, budget=budget))
    assert excinfo.value.error_type == "budget_exhausted"
    assert len(transport.calls) == 1  # metadata consumed the only unit


def test_s10_circuit_open_is_typed_and_makes_no_upstream_call() -> None:
    clock = FakeMonotonic()
    client, transport = make_client(
        [TransportTimeout()] * 2, CLIENT_CONFIG, clock
    )
    with pytest.raises(SourceTimeoutError):
        client.fetch_lot_geometry("1008350041", correlation_id="c1")
    calls_after_failure = len(transport.calls)
    with pytest.raises(CircuitOpenError) as excinfo:
        client.fetch_lot_geometry("1000010100", correlation_id="c2")
    assert excinfo.value.error_type == "circuit_open"
    assert len(transport.calls) == calls_after_failure  # no new upstream I/O


def test_s10_resilient_client_validates_bbl_before_cache_and_network() -> None:
    clock = FakeMonotonic()
    client, transport = make_client([], CLIENT_CONFIG, clock)
    with pytest.raises(BBLValidationError):
        client.fetch_lot_geometry("bogus", correlation_id="c1")
    assert transport.calls == []


def test_s10_error_taxonomy_states_are_distinguishable() -> None:
    error_types = {
        UpstreamError: "upstream_error",
        MalformedResponseError: "malformed_response",
        SchemaDriftError: "schema_drift",
        WrongCRSError: "wrong_crs",
        ResultMismatchError: "result_mismatch",
        SourceTimeoutError: "timeout",
        RateLimitedError: "rate_limited",
        DisallowedRequestError: "disallowed_request",
        RequestBudgetExceededError: "budget_exhausted",
        CircuitOpenError: "circuit_open",
    }
    assert len(set(error_types.values())) == len(error_types)
    for cls, expected in error_types.items():
        exc = cls("message", correlation_id="c")
        assert isinstance(exc, MapPlutoGeometryConnectorError)
        payload = exc.to_payload()
        assert payload["error_type"] == expected
        assert payload["source_id"] == SOURCE_ID
        assert "stack" not in json.dumps(payload).lower()


def test_s10_no_tokens_or_secrets_in_requests_fixtures_or_manifest() -> None:
    # M2-T007 G5 O4 carry-forward: WIDER secret-scan needle set. The
    # official service is keyless; nothing credential-shaped may exist.
    needles = (
        "token", "apikey", "api_key", "authorization", "bearer",
        "password", "secret",
    )
    for path in sorted(FIXTURE_DIR.glob("*.json")):
        text = path.read_text(encoding="utf-8").lower()
        for needle in needles:
            assert needle not in text, f"{needle!r} found in {path.name}"
    transport = FakeTransport(single_lot_script())
    fetch_lot_geometry("1008350041", **run_kwargs(transport))
    for call in transport.calls:
        assert call["headers"] == {"Accept": "application/json"}
        for needle in needles:
            assert needle not in call["url"].lower()


def test_s10_manifest_digests_match_committed_fixture_bytes() -> None:
    manifest = json.loads(
        (FIXTURE_DIR / "MANIFEST.json").read_text(encoding="utf-8")
    )
    assert manifest["task"] == "M2-T009"
    assert manifest["source_id"] == SOURCE_ID
    assert len(manifest["fixtures"]) == 30
    for entry in manifest["fixtures"]:
        body = load_fixture(entry["file"])["response_body_raw"]
        digest = "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()
        assert digest == entry["response_body_sha256"], entry["file"]
        assert entry["official_endpoint"].startswith(SERVICE_ROOT)


# ---------------------------------------------------------------------------
# GEO-S11 - two-staleness separation (owner rule; quartet pattern per
# M2-T008 precedent)
# ---------------------------------------------------------------------------


def old_source_script() -> list[TransportResponse]:
    return [
        fixture_response("MPG95_meta_old_edit_date_synthetic.json"),
        fixture_response("MPG02_lot_single_1008350041.json"),
    ]


def test_s11_the_two_staleness_dimensions_vary_independently() -> None:
    """Owner-required quartet: all four (source-age x transport-serve)
    combinations are observable and neither dimension ever writes the
    other's fields."""
    # 1. OLD source + FRESH transport: dataLastEditDate 2020-01-01 is
    #    provenance; a fresh retrieval is NOT stale.
    transport = FakeTransport(old_source_script())
    old_fresh = fetch_lot_geometry("1008350041", **run_kwargs(transport))
    assert old_fresh.source_data_last_edited == "2020-01-01T00:00:00Z"
    assert old_fresh.staleness is None

    # 2. CURRENT source + FRESH transport.
    transport = FakeTransport(single_lot_script())
    fresh_fresh = fetch_lot_geometry("1008350041", **run_kwargs(transport))
    assert fresh_fresh.source_data_last_edited == "2026-05-27T14:36:18Z"
    assert fresh_fresh.staleness is None

    # 3. OLD source + CACHED transport serve (upstream fine: not stale).
    clock = FakeMonotonic()
    client, _ = make_client(old_source_script(), CLIENT_CONFIG, clock)
    client.fetch_lot_geometry("1008350041", correlation_id="c1")
    clock.advance(10.0)
    cached = client.fetch_lot_geometry("1008350041", correlation_id="c2")
    assert cached.source_data_last_edited == "2020-01-01T00:00:00Z"
    assert cached.staleness["served_from_cache"] is True
    assert cached.staleness["stale"] is False

    # 4. OLD source + STALE transport serve (upstream failed; LKG).
    clock = FakeMonotonic()
    script = old_source_script() + [TransportTimeout()] * 2
    client, _ = make_client(script, CLIENT_CONFIG, clock)
    client.fetch_lot_geometry("1008350041", correlation_id="c1")
    clock.advance(150.0)  # beyond cache TTL, within LKG age
    lkg = client.fetch_lot_geometry("1008350041", correlation_id="c2")
    assert lkg.source_data_last_edited == "2020-01-01T00:00:00Z"
    assert lkg.staleness["stale"] is True
    assert lkg.staleness["upstream_error_type"] == "timeout"
    assert any("two-staleness rule" in note for note in lkg.notes)


def test_s11_cache_hit_serve_does_not_alter_source_timestamps() -> None:
    clock = FakeMonotonic()
    client, transport = make_client(single_lot_script(), CLIENT_CONFIG, clock)
    first = client.fetch_lot_geometry("1008350041", correlation_id="c1")
    assert first.staleness is None
    clock.advance(5.0)
    second = client.fetch_lot_geometry("1008350041", correlation_id="c2")
    assert len(transport.calls) == 2  # no new upstream I/O for the cache hit
    assert second.staleness["served_from_cache"] is True
    assert second.staleness["stale"] is False
    assert second.source_data_last_edited == first.source_data_last_edited
    assert second.retrieved_at == first.retrieved_at


# ---------------------------------------------------------------------------
# GEO-S12 - regression guards
# ---------------------------------------------------------------------------


def test_s12_no_pluto_module_state_is_modified() -> None:
    """Read-only reuse guard: importing/using this connector must not
    monkeypatch or replace anything in the reused pluto_soda module."""
    import app.connectors.pluto_soda as pluto_soda

    assert pluto_soda.urllib_transport.__module__ == "app.connectors.pluto_soda"
    assert pluto_soda.canonical_json_digest.__module__ == "app.connectors.pluto_soda"


def test_s12_correlation_id_minted_when_absent() -> None:
    transport = FakeTransport(single_lot_script())
    result = fetch_lot_geometry(
        "1008350041",
        transport=transport,
        sleep=SleepRecorder(),
        clock=FIXED_CLOCK,
        rng=Random(1),
    )
    assert isinstance(result.correlation_id, str) and len(result.correlation_id) == 32


def test_s12_metadata_injection_avoids_refetch() -> None:
    meta_transport = FakeTransport([fixture_response("MPG01_meta.json")])
    metadata = fetch_layer_metadata(**run_kwargs(meta_transport))
    transport = FakeTransport(
        [fixture_response("MPG02_lot_single_1008350041.json")]
    )
    result = fetch_lot_geometry(
        "1008350041", metadata=metadata, **run_kwargs(transport)
    )
    assert result.outcome == "single_feature"
    assert len(transport.calls) == 1
