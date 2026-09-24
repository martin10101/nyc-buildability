"""Building-footprint connector tests (task M5-T089, scenarios AS-1..AS-5).

Offline and deterministic: every HTTP interaction replays a RECORDED body from
services/api/tests/fixtures/building_footprints/ (captured once with curl from the official
OTI BUILDING_view service on 2026-09-24 UTC; URL, retrieved_at and sha256 in MANIFEST.json
and README.md) through an injected transport. No test touches the network. Failure shapes
that the live service cannot produce on demand are clearly labelled SYNTHETIC derivations
of a recorded body, built in-memory here.
"""

import ast
import hashlib
import json
import re
import urllib.parse
from datetime import UTC, datetime
from pathlib import Path
from random import Random

import pytest
from shapely.geometry import box

import app.connectors.building_footprints_arcgis as bf
from app.connectors.building_footprints_arcgis import (
    FEATURE_CODE_LABELS,
    FOOTPRINT_GEOMETRY_POLICY,
    OUT_FIELDS,
    REQUIRED_FIELDS,
    SOURCE_ID,
    build_metadata_url,
    build_query_url,
    classify_query_relation,
    fetch_context_buildings,
    parse_footprint_geometry,
)
from app.resilience import AnalysisBudget
from app.resilience.transport import TransportFailure, TransportResponse, TransportTimeout

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "building_footprints"
MANIFEST = json.loads((FIXTURE_DIR / "MANIFEST.json").read_text(encoding="utf-8"))
API_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = API_ROOT / "app" / "connectors" / "building_footprints_arcgis.py"
FIXED_CLOCK = lambda: datetime(2026, 9, 24, 12, 0, 0, tzinfo=UTC)  # noqa: E731

SUBJECT_ENVELOPE = (1020160, 267240, 1020230, 267325)
# MapPLUTO 26v2 lot ring of BBL 2033800084 (EPSG:2263), read from the DCP_GIS MAPPLUTO
# service on 2026-09-24 (query where=BBL=2033800084); the connector rounds it to 0.0001 ft.
SUBJECT_LOT_RING = [
    [1020218.78468084, 267251.170263767],
    [1020179.18730211, 267245.499997139],
    [1020165.64894295, 267345.884310246],
    [1020184.16237974, 267348.517512798],
    [1020205.2515645, 267351.515867233],
    [1020218.78468084, 267251.170263767],
]
CONDO_ENVELOPE = (1036960, 202070, 1037030, 202130)
COURTYARD_ENVELOPE = (990980, 222312, 990990, 222322)
PLACEHOLDER_ENVELOPE = (992333, 215590, 992341, 215598)
ZERO_HEIGHT_ENVELOPE = (1009525, 266530, 1009540, 266545)
EMPTY_ENVELOPE = (990975, 222270, 990985, 222280)
SHORT_NAMES = ("HEIGHTROOF", "GROUNDELEV", "MPLUTO_BBL", "CNSTRCT_YR", "FEAT_CODE",
               "LSTMODDATE", "LSTSTATTYPE")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def body(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def doc(name: str) -> dict:
    return json.loads(body(name))


def manifest_entry(name: str) -> dict:
    return next(e for e in MANIFEST["files"] if e["file"] == name)


def ok(text: str) -> TransportResponse:
    return TransportResponse(200, text)


class Replay:
    """Injected transport: exact-URL routes; a list route is served in order (retries)."""

    def __init__(self, routes: dict):
        self.routes = {url: list(v) if isinstance(v, list) else [v] for url, v in routes.items()}
        self.calls: list[str] = []
        self.unexpected: list[str] = []

    def __call__(self, url, headers, timeout):
        self.calls.append(url)
        if url not in self.routes:
            self.unexpected.append(url)
            raise TransportFailure("unexpected URL in replay")
        queue = self.routes[url]
        item = queue.pop(0) if len(queue) > 1 else queue[0]
        if isinstance(item, Exception):
            raise item
        return item


def run(routes: dict, **kwargs):
    transport = Replay(routes)
    kwargs.setdefault("site_ground_elevation_ft", 197)
    result = fetch_context_buildings(
        transport=transport, clock=FIXED_CLOCK, sleep=lambda _s: None, rng=Random(0),
        correlation_id="t-cid", **kwargs)
    return result, transport


META = {build_metadata_url(): ok(body("layer_metadata.json"))}
P1_URL = build_query_url(envelope=SUBJECT_ENVELOPE, page_size=2, offset=0)
P2_URL = build_query_url(envelope=SUBJECT_ENVELOPE, page_size=2, offset=2)
SUBJECT_ROUTES = {**META, P1_URL: ok(body("subject_2033800084_envelope_p1.json")),
                  P2_URL: ok(body("subject_2033800084_envelope_p2.json"))}


def one_page(envelope, fixture: str, **kwargs):
    url = build_query_url(envelope=envelope, page_size=2000)
    return run({**META, url: ok(body(fixture))}, envelope=envelope, **kwargs)


def by_oid(result) -> dict:
    return {b.object_id: b for b in result.buildings}


def gap_codes(building) -> dict:
    return {(g["field"], g["code"]) for g in building.gaps}


def synthetic_page(mutate) -> str:
    """SYNTHETIC: a recorded page-1 body, mutated in-memory by ``mutate(doc)``."""
    page = doc("subject_2033800084_envelope_p1.json")
    mutate(page)
    return json.dumps(page)


# ---------------------------------------------------------------------------
# Fixture pack integrity (AS-5)
# ---------------------------------------------------------------------------


def test_fixture_pack_is_small_recorded_and_sha256_pinned():
    files = sorted(p.name for p in FIXTURE_DIR.glob("*.json") if p.name != "MANIFEST.json")
    assert files == sorted(e["file"] for e in MANIFEST["files"])
    for entry in MANIFEST["files"]:
        raw = (FIXTURE_DIR / entry["file"]).read_bytes().replace(b"\r\n", b"\n")
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"], entry["file"]
        assert len(raw) == entry["bytes"] <= 16 * 1024, entry["file"]
        assert entry["http_status"] == 200
        assert entry["request_url"].startswith(MANIFEST["layer_url"])
        assert re.fullmatch(r"2026-09-24T\d\d:\d\d:\d\dZ", entry["retrieved_at"])
    readme = (FIXTURE_DIR / "README.md").read_text(encoding="utf-8")
    for entry in MANIFEST["files"]:
        assert entry["file"] in readme and entry["sha256"] in readme


# ---------------------------------------------------------------------------
# AS-1 request contract
# ---------------------------------------------------------------------------


def test_as1_connector_urls_reproduce_the_recorded_requests_byte_for_byte():
    assert build_metadata_url() == manifest_entry("layer_metadata.json")["request_url"]
    expected = {
        "subject_2033800084_envelope_p1.json": P1_URL,
        "subject_2033800084_envelope_p2.json": P2_URL,
        "subject_2033800084_lot_polygon.json": build_query_url(polygon=SUBJECT_LOT_RING,
                                                               page_size=2000),
        "condo_4068157501_envelope.json": build_query_url(envelope=CONDO_ENVELOPE,
                                                          page_size=2000),
        "courtyard_hole_1011250025_envelope.json": build_query_url(envelope=COURTYARD_ENVELOPE,
                                                                   page_size=2000),
        "placeholder_zero_height_null_ground_envelope.json": build_query_url(
            envelope=PLACEHOLDER_ENVELOPE, page_size=2000),
        "zero_height_condo_2059447501_envelope.json": build_query_url(
            envelope=ZERO_HEIGHT_ENVELOPE, page_size=2000),
        "empty_result_envelope.json": build_query_url(envelope=EMPTY_ENVELOPE, page_size=2000),
    }
    for name, url in expected.items():
        assert url == manifest_entry(name)["request_url"], name


@pytest.mark.parametrize("kind", ["envelope", "polygon"])
def test_as1_query_uses_outsr_2263_long_names_intersects_and_ordered_paging(kind):
    geometry = {"envelope": SUBJECT_ENVELOPE} if kind == "envelope" else {
        "polygon": SUBJECT_LOT_RING}
    url = build_query_url(**geometry, page_size=2000, offset=0)
    params = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))
    assert params["outSR"] == "2263" and params["inSR"] == "2263"
    assert params["spatialRel"] == "esriSpatialRelIntersects"
    assert params["geometryType"] == ("esriGeometryEnvelope" if kind == "envelope"
                                      else "esriGeometryPolygon")
    assert params["outFields"].split(",") == list(OUT_FIELDS)
    for short in SHORT_NAMES:
        assert short not in params["outFields"].split(",")
    assert {"HEIGHT_ROOF", "GROUND_ELEVATION", "MAPPLUTO_BBL", "BASE_BBL", "BIN", "DOITT_ID",
            "CONSTRUCTION_YEAR", "FEATURE_CODE"} <= set(params["outFields"].split(","))
    assert params["orderByFields"] == "OBJECTID ASC"
    assert (params["resultRecordCount"], params["resultOffset"]) == ("2000", "0")
    assert params["returnGeometry"] == "true" and params["f"] == "json"
    assert "*" not in params["outFields"]


def test_as1_required_field_pins_match_the_recorded_layer_schema():
    layer = doc("layer_metadata.json")
    live = {f["name"]: f["type"] for f in layer["fields"]}
    for name, esri_type in REQUIRED_FIELDS.items():
        assert live[name] == esri_type
    assert layer["maxRecordCount"] == 2000 and layer["objectIdField"] == "OBJECTID"


def test_as1_pages_follow_exceeded_transfer_limit_with_deterministic_offsets():
    result, transport = run(SUBJECT_ROUTES, envelope=SUBJECT_ENVELOPE, page_size=2)
    assert result.status == "ok", result.refusal
    assert transport.calls == [build_metadata_url(), P1_URL, P2_URL]
    assert result.request_urls == [P1_URL, P2_URL] and result.pages_fetched == 2
    assert [b.object_id for b in result.buildings] == [29471, 229537, 794314]
    assert doc("subject_2033800084_envelope_p1.json")["exceededTransferLimit"] is True


def test_as1_page_size_never_exceeds_the_layer_max_record_count():
    """SYNTHETIC metadata: maxRecordCount lowered to 1 caps the requested page size."""
    meta = doc("layer_metadata.json")
    meta["maxRecordCount"] = 1
    url = build_query_url(envelope=EMPTY_ENVELOPE, page_size=1)
    result, transport = run({build_metadata_url(): ok(json.dumps(meta)),
                             url: ok(body("empty_result_envelope.json"))},
                            envelope=EMPTY_ENVELOPE)
    assert result.status == "ok" and transport.calls[1] == url


@pytest.mark.parametrize(
    "geometry",
    [
        {},
        {"envelope": SUBJECT_ENVELOPE, "polygon": SUBJECT_LOT_RING},
        {"envelope": (1, 2, 3)},
        {"envelope": (5, 5, 1, 9)},
        {"envelope": (0, 0, 0, 10)},
        {"envelope": (0, 0, float("nan"), 1)},
        {"envelope": (0, 0, 10**400, 1)},
        {"envelope": (True, 0, 1, 1)},
        {"envelope": (0, 0, 9000, 10)},
        {"polygon": SUBJECT_LOT_RING[:-1]},
        {"polygon": [[0, 0], [10, 10], [10, 0], [0, 10], [0, 0]]},
        {"polygon": [[0, 0], [1, 1]]},
        {"polygon": [[0, 0, 0], [0, 1, 0], [1, 1, 0], [0, 0, 0]]},
    ],
)
def test_as1_invalid_query_input_is_refused_before_any_io(geometry):
    result, transport = run(META, **geometry)
    assert result.status == "refused" and result.refusal.error_type == "disallowed_request"
    assert transport.calls == [] and result.refusal.request_url is None


@pytest.mark.parametrize(
    "kwargs",
    [{"site_ground_elevation_ft": float("inf")}, {"site_ground_elevation_ft": "197"},
     {"subject_bbl": "6000010001"}, {"page_size": 0}, {"page_size": 2001}],
)
def test_as1_invalid_caller_parameters_are_refused_before_any_io(kwargs):
    result, transport = run(META, envelope=SUBJECT_ENVELOPE, **kwargs)
    assert result.refusal.error_type == "disallowed_request" and transport.calls == []


# ---------------------------------------------------------------------------
# AS-2 parse + datum + geometry policy
# ---------------------------------------------------------------------------


def test_as2_recorded_pages_parse_into_typed_records_with_verbatim_2263_rings():
    result, _ = run(SUBJECT_ROUTES, envelope=SUBJECT_ENVELOPE, page_size=2,
                    subject_bbl="2033800084")
    buildings = by_oid(result)
    recorded = {f["attributes"]["OBJECTID"]: f for name in (
        "subject_2033800084_envelope_p1.json", "subject_2033800084_envelope_p2.json")
        for f in doc(name)["features"]}
    for oid, building in buildings.items():
        rings = recorded[oid]["geometry"]["rings"]
        assert building.geometry_status == "valid" and len(building.parts) == 1
        assert building.parts[0].exterior == [[float(x), float(y)] for x, y in rings[0]]
        assert building.original_geometry == recorded[oid]["geometry"]
        assert building.attributes == recorded[oid]["attributes"]
    subject = buildings[229537]
    assert (subject.bin, subject.doitt_id) == (2019299, 353927)
    assert subject.base_bbl == subject.mappluto_bbl == "2033800084"
    assert subject.joins_subject_lot is True
    assert buildings[29471].joins_subject_lot is False
    assert subject.height_roof_ft == 33.49 and subject.ground_elevation_ft == 197.0
    assert subject.construction_year == 1910 and subject.feature_code_label == "Building"
    assert subject.geom_source == "Photogrammetric"
    assert subject.last_edited == "2017-08-22T18:57:18Z"
    assert subject.gaps == [] and subject.flags == []
    assert result.crs == {"wkid": 102718, "latest_wkid": 2263,
                          "authority": "EPSG:2263 (NAD83 / New York Long Island, US survey feet)"}


def test_as2_relative_base_z_is_ground_minus_site_ground_exactly():
    result, _ = run(SUBJECT_ROUTES, envelope=SUBJECT_ENVELOPE, page_size=2,
                    site_ground_elevation_ft=197)
    buildings = by_oid(result)
    assert buildings[29471].relative_base_z_ft == 0.0
    assert buildings[229537].relative_base_z_ft == 0.0
    assert buildings[794314].ground_elevation_ft == 195.0
    assert buildings[794314].relative_base_z_ft == -2.0
    assert buildings[229537].relative_roof_z_ft == 33.49
    assert buildings[794314].relative_roof_z_ft == pytest.approx(19.28, abs=1e-9)
    shifted, _ = run(SUBJECT_ROUTES, envelope=SUBJECT_ENVELOPE, page_size=2,
                     site_ground_elevation_ft=195.5)
    assert by_oid(shifted)[794314].relative_base_z_ft == -0.5
    assert by_oid(shifted)[229537].relative_base_z_ft == 1.5


def test_as2_units_and_datum_labels_keep_the_rq1_inference_visible():
    result, _ = run(SUBJECT_ROUTES, envelope=SUBJECT_ENVELOPE, page_size=2)
    building = result.buildings[0]
    assert building.height_unit == "us_survey_foot"
    assert "INFERENCE" in building.height_unit_basis and "RQ-1" in building.height_unit_basis
    assert building.ground_datum == "NAVD88"
    assert "RQ-2" in building.ground_datum_basis and "centroid" in building.ground_datum_basis
    assert "not height above sea level" in building.height_reference


def test_as2_site_ground_not_supplied_is_a_typed_gap_never_a_default():
    result, _ = run(SUBJECT_ROUTES, envelope=SUBJECT_ENVELOPE, page_size=2,
                    site_ground_elevation_ft=None)
    for building in result.buildings:
        assert building.relative_base_z_ft is None and building.relative_roof_z_ft is None
        assert ("site_ground_elevation_ft", "site_ground_not_supplied") in gap_codes(building)


def test_as2_query_relation_distinguishes_within_from_partial_overlap():
    result, _ = run(SUBJECT_ROUTES, envelope=SUBJECT_ENVELOPE, page_size=2)
    buildings = by_oid(result)
    assert buildings[229537].query_relation == "within"
    assert buildings[29471].query_relation == "partial_overlap"
    assert buildings[794314].query_relation == "partial_overlap"
    assert 0.0 < buildings[29471].query_overlap_area_sq_ft < buildings[29471].footprint_area_sq_ft


def test_as2_lot_polygon_query_returns_the_subject_footprint_within_the_lot():
    url = build_query_url(polygon=SUBJECT_LOT_RING, page_size=2000)
    result, _ = run({**META, url: ok(body("subject_2033800084_lot_polygon.json"))},
                    polygon=SUBJECT_LOT_RING, subject_bbl="2033800084")
    assert [b.object_id for b in result.buildings] == [229537]
    assert result.buildings[0].query_relation == "within"
    assert result.buildings[0].joins_subject_lot is True
    assert result.query["kind"] == "polygon" and len(result.query["ring"]) == 6


def test_as2_courtyard_hole_is_kept_on_its_part_and_flagged():
    result, _ = one_page(COURTYARD_ENVELOPE, "courtyard_hole_1011250025_envelope.json")
    (building,) = result.buildings
    rings = doc("courtyard_hole_1011250025_envelope.json")["features"][0]["geometry"]["rings"]
    assert building.geometry_status == "valid" and len(building.parts) == 1
    assert building.parts[0].exterior == rings[0] and building.parts[0].holes == [rings[1]]
    assert "has_holes" in building.flags and "multipart" not in building.flags
    assert building.footprint_area_sq_ft == pytest.approx(40953.0004 - 5962.5794, abs=0.01)
    assert building.query_relation == "partial_overlap"


def square(x, y, size=10.0, clockwise=True):
    ring = [[x, y], [x, y + size], [x + size, y + size], [x + size, y], [x, y]]
    return ring if clockwise else list(reversed(ring))


def test_as2_multipart_policy_keeps_every_part_in_response_order():
    """SYNTHETIC geometry: two disjoint clockwise exteriors and one hole in the second."""
    hole = square(24, 4, 2, clockwise=False)
    status, findings, parts, flags = parse_footprint_geometry(
        {"rings": [square(0, 0), square(20, 0), hole]})
    assert status == "valid" and findings == []
    assert [p.exterior for p in parts] == [square(0, 0), square(20, 0)]
    assert parts[0].holes == [] and parts[1].holes == [hole]
    assert set(flags) == {"multipart", "has_holes"}
    assert [p.area_sq_ft for p in parts] == [100.0, 96.0]


@pytest.mark.parametrize(
    ("geometry", "status", "finding"),
    [
        (None, "invalid", "null_geometry"),
        ({"paths": [[[0, 0], [1, 1]]]}, "invalid", "not_a_polygon_geometry"),
        ({"rings": []}, "invalid", "empty_geometry"),
        ({"rings": [square(0, 0)[:-1]]}, "invalid", "unclosed_ring"),
        ({"rings": [[[0, 0], [0, 1], [float("inf"), 1], [0, 0]]]}, "invalid",
         "nonfinite_coordinate"),
        ({"rings": [[[0, 0], [0, 1], [0, 2], [0, 0]]]}, "invalid", "degenerate_ring"),
        ({"rings": [[[0, 0], ["a", 1], [1, 1], [0, 0]]]}, "invalid", "malformed_ring"),
        ({"rings": [[[0, 0], [10, 10], [10, 0], [0, 10], [0, 0]]]}, "invalid",
         "self_intersecting_ring"),
        ({"rings": [[[0, 0], [10, 20], [10, 0], [0, 10], [0, 0]]]}, "invalid",
         "invalid_part:0:"),
        ({"rings": [square(0, 0, clockwise=False)]}, "review_required",
         "no_clockwise_exterior_ring"),
        ({"rings": [square(0, 0), square(50, 50, 2, clockwise=False)]}, "review_required",
         "hole_outside_every_exterior"),
        ({"rings": [square(0, 0), square(5, 5)]}, "review_required", "parts_overlap:0:1"),
    ],
)
def test_as2_geometry_policy_types_every_unusable_case(geometry, status, finding):
    got_status, findings, parts, _ = parse_footprint_geometry(geometry)
    assert got_status == status and parts == []
    assert any(f.startswith(finding) for f in findings), findings


def test_as2_touching_parts_are_kept_and_flagged_not_treated_as_overlap():
    """SYNTHETIC geometry: two exteriors sharing one edge (a party wall)."""
    status, _, parts, flags = parse_footprint_geometry({"rings": [square(0, 0), square(10, 0)]})
    assert status == "valid" and len(parts) == 2
    assert "parts_touch" in flags and "multipart" in flags


def test_as2_unusable_geometry_record_is_still_returned_never_dropped():
    """SYNTHETIC page: the subject footprint's ring is unclosed; the record survives."""
    def mutate(page):
        page["features"][1]["geometry"]["rings"][0].pop()
    result, _ = run({**SUBJECT_ROUTES, P1_URL: ok(synthetic_page(mutate))},
                    envelope=SUBJECT_ENVELOPE, page_size=2)
    subject = by_oid(result)[229537]
    assert result.status == "ok" and len(result.buildings) == 3
    assert subject.geometry_status == "invalid" and subject.parts == []
    assert subject.geometry_findings == ["unclosed_ring"] and subject.query_relation is None
    assert subject.original_geometry is not None and subject.footprint_area_sq_ft is None


@pytest.mark.parametrize(
    ("ring", "relation", "overlap"),
    [
        (square(10, 10), "within", 100.0),
        (square(95, 10), "partial_overlap", 50.0),
        (square(100, 10), "boundary_touch", 0.0),
        (square(100, 100), "boundary_touch", 0.0),
        (square(150, 10), "disjoint_locally", 0.0),
    ],
)
def test_as2_query_relation_boundary_touch_is_not_overlap(ring, relation, overlap):
    """SYNTHETIC geometry against a 100 ft box: edge and corner touches are boundary
    touches (zero-area), distinct from positive-area overlap."""
    _, _, parts, _ = parse_footprint_geometry({"rings": [ring]})
    assert classify_query_relation(parts, box(0, 0, 100, 100)) == (relation, overlap)


def test_as2_server_local_disagreement_is_flagged_and_kept():
    """SYNTHETIC page: a footprint shifted 1000 ft away from the query envelope."""
    def mutate(page):
        rings = page["features"][0]["geometry"]["rings"]
        page["features"][0]["geometry"]["rings"] = [[[x + 1000.0, y] for x, y in r]
                                                    for r in rings]
    result, _ = run({**SUBJECT_ROUTES, P1_URL: ok(synthetic_page(mutate))},
                    envelope=SUBJECT_ENVELOPE, page_size=2)
    moved = by_oid(result)[29471]
    assert moved.query_relation == "disjoint_locally"
    assert "server_local_relation_disagreement" in moved.flags


def test_as2_provenance_quintuple_is_complete():
    result, _ = run(SUBJECT_ROUTES, envelope=SUBJECT_ENVELOPE, page_size=2)
    prov = result.provenance()
    assert prov["source"] == {"source_id": SOURCE_ID, "open_data_id": "5zhs-2jue",
                              "layer_url": MANIFEST["layer_url"]}
    assert prov["request"] == {"metadata": build_metadata_url(), "pages": [P1_URL, P2_URL]}
    assert prov["retrieved_at"] == "2026-09-24T12:00:00Z"
    assert prov["source_data_last_edited"] == "2026-09-20T02:16:01Z"
    assert prov["response_digests"] == {
        "metadata": "sha256:" + manifest_entry("layer_metadata.json")["sha256"],
        "pages": ["sha256:" + manifest_entry("subject_2033800084_envelope_p1.json")["sha256"],
                  "sha256:" + manifest_entry("subject_2033800084_envelope_p2.json")["sha256"]]}
    assert result.geometry_policy == FOOTPRINT_GEOMETRY_POLICY
    assert result.drift_signals == []


def test_as2_well_formed_empty_result_is_valid_and_empty():
    result, _ = one_page(EMPTY_ENVELOPE, "empty_result_envelope.json")
    assert result.status == "ok" and result.buildings == [] and result.pages_fetched == 1


# ---------------------------------------------------------------------------
# AS-3 honest gaps
# ---------------------------------------------------------------------------


def test_as3_zero_height_is_a_typed_gap_never_a_default():
    result, _ = one_page(ZERO_HEIGHT_ENVELOPE, "zero_height_condo_2059447501_envelope.json",
                         site_ground_elevation_ft=201)
    (building,) = result.buildings
    assert building.attributes["HEIGHT_ROOF"] == 0
    assert building.height_roof_ft is None and building.relative_roof_z_ft is None
    assert ("HEIGHT_ROOF", "height_roof_zero_not_available") in gap_codes(building)
    assert building.relative_base_z_ft == 0.0  # the ground is published; only the height gaps
    assert building.feature_code == 2100


@pytest.mark.parametrize(
    ("value", "code"),
    [(None, "height_roof_null_not_available"), (0.0, "height_roof_zero_not_available"),
     (-3.5, "height_roof_negative"), ("33", "height_roof_malformed"),
     (True, "height_roof_malformed"), (10**400, "height_roof_malformed")],
)
def test_as3_missing_or_invalid_heights_are_typed_gaps(value, code):
    """SYNTHETIC page: HEIGHT_ROOF of the subject footprint replaced."""
    def mutate(page):
        page["features"][1]["attributes"]["HEIGHT_ROOF"] = value
    result, _ = run({**SUBJECT_ROUTES, P1_URL: ok(synthetic_page(mutate))},
                    envelope=SUBJECT_ENVELOPE, page_size=2)
    subject = by_oid(result)[229537]
    assert subject.height_roof_ft is None and subject.relative_roof_z_ft is None
    assert ("HEIGHT_ROOF", code) in gap_codes(subject)


def test_as3_placeholder_and_null_ground_are_typed_gaps():
    result, _ = one_page(PLACEHOLDER_ENVELOPE,
                         "placeholder_zero_height_null_ground_envelope.json")
    (building,) = result.buildings
    codes = gap_codes(building)
    assert building.feature_code == 1003 and building.feature_code_label == "Placeholder"
    assert ("FEATURE_CODE", "placeholder_geometry_not_building_outline") in codes
    assert ("HEIGHT_ROOF", "height_roof_zero_not_available") in codes
    assert ("GROUND_ELEVATION", "missing") in codes
    assert ("CONSTRUCTION_YEAR", "missing") in codes
    assert ("GEOM_SOURCE", "missing") in codes and ("LAST_STATUS_TYPE", "missing") in codes
    assert building.ground_elevation_ft is None
    assert building.relative_base_z_ft is None  # never replaced by the site ground (197)
    assert building.base_bbl == building.mappluto_bbl == "1201359999"  # verbatim, no guess


def test_as3_condo_billing_lot_join_is_flagged():
    result, _ = one_page(CONDO_ENVELOPE, "condo_4068157501_envelope.json",
                         subject_bbl="4068157501")
    assert [b.object_id for b in result.buildings] == [51179, 56671, 1043581]
    for building in result.buildings:
        assert building.base_bbl == "4068150020" and building.mappluto_bbl == "4068157501"
        assert {"condo_billing_lot_join", "mappluto_bbl_differs_from_base_bbl"} <= set(
            building.flags)
        assert building.joins_subject_lot is True
    base_view, _ = one_page(CONDO_ENVELOPE, "condo_4068157501_envelope.json",
                            subject_bbl="4068150020")
    for building in base_view.buildings:
        assert building.joins_subject_lot is False
        assert "base_bbl_is_subject_but_mappluto_bbl_differs" in building.flags


def test_as3_zero_height_building_on_a_condo_billing_lot_carries_both():
    result, _ = one_page(ZERO_HEIGHT_ENVELOPE, "zero_height_condo_2059447501_envelope.json")
    (building,) = result.buildings
    assert (building.base_bbl, building.mappluto_bbl) == ("2059440110", "2059447501")
    assert "condo_billing_lot_join" in building.flags


@pytest.mark.parametrize(
    ("field", "value", "expect"),
    [
        ("BIN", 2000000, ("flag", "bin_unassigned_million_bin")),
        ("FEATURE_CODE", 4242, ("gap", ("FEATURE_CODE", "undocumented_feature_code"))),
        ("FEATURE_CODE", None, ("gap", ("FEATURE_CODE", "missing"))),
        ("MAPPLUTO_BBL", "20338000X4", ("gap", ("MAPPLUTO_BBL", "unparseable_bbl"))),
        ("BASE_BBL", 2033800084, ("gap", ("BASE_BBL", "unparseable_bbl"))),
        ("DOITT_ID", None, ("gap", ("DOITT_ID", "missing"))),
        ("CONSTRUCTION_YEAR", 0, ("gap", ("CONSTRUCTION_YEAR", "zero_not_available"))),
        ("GROUND_ELEVATION", 0, ("flag", "ground_elevation_zero_unverified")),
        ("GROUND_ELEVATION", "197", ("gap", ("GROUND_ELEVATION", "malformed"))),
        ("LAST_EDITED_DATE", None, ("gap", ("LAST_EDITED_DATE", "missing_or_malformed"))),
    ],
)
def test_as3_attribute_gaps_and_flags_are_typed(field, value, expect):
    """SYNTHETIC page: one attribute of the subject footprint replaced."""
    def mutate(page):
        page["features"][1]["attributes"][field] = value
    result, _ = run({**SUBJECT_ROUTES, P1_URL: ok(synthetic_page(mutate))},
                    envelope=SUBJECT_ENVELOPE, page_size=2)
    subject = by_oid(result)[229537]
    kind, item = expect
    assert item in (subject.flags if kind == "flag" else gap_codes(subject))


def test_as3_every_none_value_has_a_matching_gap():
    routes = {**META}
    records = []
    for envelope, name in [(PLACEHOLDER_ENVELOPE,
                            "placeholder_zero_height_null_ground_envelope.json"),
                           (ZERO_HEIGHT_ENVELOPE, "zero_height_condo_2059447501_envelope.json")]:
        url = build_query_url(envelope=envelope, page_size=2000)
        result, _ = run({**routes, url: ok(body(name))}, envelope=envelope,
                        site_ground_elevation_ft=None)
        records.extend(result.buildings)
    field_of = {"doitt_id": "DOITT_ID", "bin": "BIN", "base_bbl": "BASE_BBL",
                "mappluto_bbl": "MAPPLUTO_BBL", "feature_code": "FEATURE_CODE",
                "height_roof_ft": "HEIGHT_ROOF", "ground_elevation_ft": "GROUND_ELEVATION",
                "construction_year": "CONSTRUCTION_YEAR", "geom_source": "GEOM_SOURCE",
                "last_edited": "LAST_EDITED_DATE", "last_status_type": "LAST_STATUS_TYPE"}
    for building in records:
        gapped = {g["field"] for g in building.gaps}
        for attr, source_field in field_of.items():
            if getattr(building, attr) is None:
                assert source_field in gapped, (building.object_id, attr)
        assert "site_ground_elevation_ft" in gapped


def test_as3_feature_code_labels_are_the_documented_domain():
    assert FEATURE_CODE_LABELS[1003] == "Placeholder" and FEATURE_CODE_LABELS[2100] == "Building"
    assert sorted(FEATURE_CODE_LABELS) == [1000, 1001, 1002, 1003, 1004, 1005, 1006, 2100,
                                           2110, 5100, 5110]


# ---------------------------------------------------------------------------
# AS-4 fail-closed transport (typed refusal with the failed request's provenance)
# ---------------------------------------------------------------------------


def refused(result, error_type):
    assert result.status == "refused" and result.buildings == []
    assert result.refusal.error_type == error_type, result.refusal
    assert result.refusal.correlation_id == "t-cid"
    assert result.refusal.retrieved_at == "2026-09-24T12:00:00Z"
    return result.refusal


@pytest.mark.parametrize(
    ("responses", "error_type"),
    [
        ([TransportResponse(500, "busy")] * 3, "upstream_error"),
        ([TransportResponse(404, "nope")], "upstream_error"),
        ([TransportResponse(429, "slow")] * 3, "rate_limited"),
        ([TransportTimeout("t")] * 3, "timeout"),
        ([TransportFailure("dns")] * 3, "upstream_error"),
    ],
)
def test_as4_transport_failures_become_typed_refusals(responses, error_type):
    result, transport = run({**META, P1_URL: responses}, envelope=SUBJECT_ENVELOPE,
                            page_size=2)
    refusal = refused(result, error_type)
    assert refusal.request_url == P1_URL and refusal.raw_digest is None
    assert refusal.detail["url"] == P1_URL
    assert result.metadata_raw_digest is not None  # provenance gathered before the failure


def test_as4_recorded_arcgis_error_object_is_an_upstream_refusal():
    result, _ = run({**META, P1_URL: ok(body("short_field_names_error_object.json"))},
                    envelope=SUBJECT_ENVELOPE, page_size=2)
    refusal = refused(result, "upstream_error")
    assert refusal.detail["arcgis_error_code"] == "400"
    assert refusal.request_url == P1_URL
    assert refusal.raw_digest == "sha256:" + manifest_entry(
        "short_field_names_error_object.json")["sha256"]


def test_as4_malformed_json_is_refused_with_the_body_digest():
    truncated = body("subject_2033800084_envelope_p1.json")[:500]
    result, _ = run({**META, P1_URL: ok(truncated)}, envelope=SUBJECT_ENVELOPE, page_size=2)
    refusal = refused(result, "malformed_response")
    assert refusal.raw_digest == "sha256:" + hashlib.sha256(truncated.encode()).hexdigest()


@pytest.mark.parametrize(
    "payload",
    ["[]", '{"features": {}}', '{"spatialReference": {"wkid": 102718, "latestWkid": 2263}, '
     '"features": [{"x": 1}]}'],
)
def test_as4_wrong_shapes_are_malformed_never_empty(payload):
    result, _ = run({**META, P1_URL: ok(payload)}, envelope=SUBJECT_ENVELOPE, page_size=2)
    refused(result, "malformed_response")


def test_as4_recorded_web_mercator_page_is_refused_as_wrong_crs():
    result, _ = run({**META, P1_URL: ok(body("subject_2033800084_no_outsr_web_mercator.json"))},
                    envelope=SUBJECT_ENVELOPE, page_size=2)
    refusal = refused(result, "wrong_crs")
    assert "102100" in refusal.detail["spatial_reference"]
    assert refusal.request_url == P1_URL


def test_as4_nonempty_page_without_spatial_reference_is_refused():
    """SYNTHETIC page: spatialReference removed while features are present."""
    result, _ = run({**SUBJECT_ROUTES,
                     P1_URL: ok(synthetic_page(lambda p: p.pop("spatialReference")))},
                    envelope=SUBJECT_ENVELOPE, page_size=2)
    refused(result, "wrong_crs")


def test_as4_over_page_count_is_refused():
    """A recorded 2-feature page served for a request that asked for 1 feature."""
    url = build_query_url(envelope=SUBJECT_ENVELOPE, page_size=1)
    result, _ = run({**META, url: ok(body("subject_2033800084_envelope_p1.json"))},
                    envelope=SUBJECT_ENVELOPE, page_size=1)
    refusal = refused(result, "paging_pathology")
    assert refusal.detail["reason"] == "over_page_count" and refusal.request_url == url


def test_as4_repeated_object_ids_across_pages_are_refused():
    routes = {**SUBJECT_ROUTES, P2_URL: ok(body("subject_2033800084_envelope_p1.json"))}
    result, _ = run(routes, envelope=SUBJECT_ENVELOPE, page_size=2)
    assert refused(result, "paging_pathology").detail["reason"] == "repeated_object_ids"


def test_as4_empty_page_claiming_more_data_is_refused():
    """SYNTHETIC page 2: no features but exceededTransferLimit=true."""
    def mutate(page):
        page["features"] = []
    result, _ = run({**SUBJECT_ROUTES, P2_URL: ok(synthetic_page(mutate))},
                    envelope=SUBJECT_ENVELOPE, page_size=2)
    assert refused(result, "paging_pathology").detail["reason"] == "zero_progress"


def test_as4_page_ceiling_and_feature_cap_are_refusals_not_truncation(monkeypatch):
    monkeypatch.setattr(bf, "HARD_MAX_PAGES", 1)
    result, _ = run(SUBJECT_ROUTES, envelope=SUBJECT_ENVELOPE, page_size=2)
    assert refused(result, "paging_pathology").detail["reason"] == "page_ceiling"
    monkeypatch.setattr(bf, "HARD_MAX_PAGES", 50)
    monkeypatch.setattr(bf, "MAX_CONTEXT_BUILDINGS", 2)
    result, _ = run(SUBJECT_ROUTES, envelope=SUBJECT_ENVELOPE, page_size=2)
    assert refused(result, "paging_pathology").detail["reason"] == "over_feature_cap"


@pytest.mark.parametrize(
    "mutate",
    [
        lambda m: m.update(name="BUILDING_P"),
        lambda m: m.update(geometryType="esriGeometryPoint"),
        lambda m: m.update(objectIdField="FID"),
        lambda m: m.update(fields={}),
        lambda m: m.update(maxRecordCount=None),
        lambda m: m["advancedQueryCapabilities"].update(supportsPagination=False),
        lambda m: [f.update(name="HEIGHTROOF") for f in m["fields"] if f["name"] == "HEIGHT_ROOF"],
        lambda m: [f.update(type="esriFieldTypeString") for f in m["fields"]
                   if f["name"] == "GROUND_ELEVATION"],
    ],
)
def test_as4_layer_schema_drift_is_refused_before_any_page(mutate):
    """SYNTHETIC metadata: the recorded layer JSON with one contract element changed."""
    meta = doc("layer_metadata.json")
    mutate(meta)
    result, transport = run({build_metadata_url(): ok(json.dumps(meta)), **{
        P1_URL: ok(body("subject_2033800084_envelope_p1.json"))}},
        envelope=SUBJECT_ENVELOPE, page_size=2)
    refusal = refused(result, "schema_drift")
    assert refusal.request_url == build_metadata_url() and transport.calls == [
        build_metadata_url()]


def test_as4_publication_crs_change_and_missing_edit_date_are_visible_drift_signals():
    """SYNTHETIC metadata: publication CRS changed, editingInfo removed (non-fatal)."""
    meta = doc("layer_metadata.json")
    meta["extent"]["spatialReference"] = {"wkid": 102718, "latestWkid": 2263}
    meta.pop("editingInfo")
    result, _ = run({**SUBJECT_ROUTES, build_metadata_url(): ok(json.dumps(meta))},
                    envelope=SUBJECT_ENVELOPE, page_size=2)
    assert result.status == "ok"
    assert result.drift_signals == ["publication_crs_changed", "missing_editing_info"]
    assert result.source_data_last_edited is None


def test_as4_unknown_attribute_is_a_drift_signal():
    """SYNTHETIC page: an attribute outside the requested field set."""
    def mutate(page):
        page["features"][0]["attributes"]["NAME"] = "x"
    result, _ = run({**SUBJECT_ROUTES, P1_URL: ok(synthetic_page(mutate))},
                    envelope=SUBJECT_ENVELOPE, page_size=2)
    assert result.status == "ok" and result.drift_signals == ["unknown_attribute:'NAME'"]


def test_as4_budget_exhaustion_is_a_refusal():
    result, _ = run(SUBJECT_ROUTES, envelope=SUBJECT_ENVELOPE, page_size=2,
                    budget=AnalysisBudget(max_upstream_requests=2, analysis_id="a"))
    refusal = refused(result, "budget_exhausted")
    assert refusal.request_url == P2_URL


def test_as4_unexpected_internal_exception_never_escapes():
    def broken(url, headers, timeout):
        raise RuntimeError("boom")
    result = fetch_context_buildings(envelope=SUBJECT_ENVELOPE, transport=broken,
                                     clock=FIXED_CLOCK, correlation_id="t-cid")
    refusal = refused(result, "internal_error")
    assert refusal.detail == {"exception": "RuntimeError"}
    assert refusal.request_url == build_metadata_url()


# ---------------------------------------------------------------------------
# AS-5 scope: no dependencies beyond the admitted set, not wired, no network
# ---------------------------------------------------------------------------


def test_as5_module_imports_only_stdlib_shapely_and_app():
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    assert roots <= {"__future__", "hashlib", "json", "logging", "math", "time", "urllib",
                     "uuid", "collections", "dataclasses", "datetime", "random", "shapely",
                     "app"}


def test_as5_connector_is_not_wired_to_any_route_or_module():
    for path in (API_ROOT / "app").rglob("*.py"):
        if path == MODULE_PATH:
            continue
        assert "building_footprints_arcgis" not in path.read_text(encoding="utf-8"), path


def test_as5_fixture_pack_contains_no_credential_material():
    needles = ("token", "apikey", "api_key", "authorization", "bearer", "password", "secret")
    for path in sorted(FIXTURE_DIR.iterdir()):
        text = path.read_text(encoding="utf-8").lower()
        for needle in needles:
            assert needle not in text, (path.name, needle)


def test_as5_requests_are_keyless_and_carry_only_the_accept_header():
    seen: list[dict] = []
    replay = Replay(SUBJECT_ROUTES)

    def recording(url, headers, timeout):
        seen.append(dict(headers))
        return replay(url, headers, timeout)
    result = fetch_context_buildings(envelope=SUBJECT_ENVELOPE, page_size=2, transport=recording,
                                     clock=FIXED_CLOCK)
    assert result.status == "ok" and seen == [{"Accept": "application/json"}] * 3
    assert all("token" not in url.lower() for url in replay.calls)


def test_as5_recorded_replay_never_reaches_the_network(monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("network access attempted in an offline test")
    monkeypatch.setattr("app.resilience.transport.DEFAULT_OPENER.open", no_network)
    result, transport = run(SUBJECT_ROUTES, envelope=SUBJECT_ENVELOPE, page_size=2)
    assert result.status == "ok" and transport.unexpected == []
