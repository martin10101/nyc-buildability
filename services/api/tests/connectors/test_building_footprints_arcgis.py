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
import logging
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


def _app_imports(path: Path) -> set[str]:
    """The ``app.*`` modules a source file imports (direct edges), by AST."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("app."):
            mods.add(node.module)
        elif isinstance(node, ast.Import):
            mods.update(a.name for a in node.names if a.name.startswith("app."))
    return mods


def _module_path(module: str) -> Path | None:
    """Resolve an ``app.*`` module name to its source file (a ``module.py`` or a package
    ``__init__.py``), or None when it is neither (a namespace / C-extension)."""
    parts = module.split(".")
    candidate = API_ROOT.joinpath(*parts).with_suffix(".py")
    if candidate.exists():
        return candidate
    pkg_init = API_ROOT.joinpath(*parts, "__init__.py")
    return pkg_init if pkg_init.exists() else None


def test_pkte_connector_is_unwired_from_the_mounted_app_and_wired_only_to_the_scene_assembler():
    """AS-5 (DB-073 e): the grep-for-the-literal not-wired test is REPLACED with an
    import-graph/AST check, because PKT-E now imports this connector by design and the old grep
    would trip on that. The load-bearing invariant is instead: the connector is NOT reachable
    from the mounted app (app.main), and neither is the UNMOUNTED scene route - so no route
    serving this connector is live. It IS wired to exactly the accepted consumer, the scene
    assembler. Mutation guard: mounting scene_api in main.py (or importing the connector from a
    reachable module) makes it reachable and reddens the unreachability assertion."""
    seen: set[str] = set()
    queue = ["app.main"]
    while queue:
        module = queue.pop()
        if module in seen:
            continue
        seen.add(module)
        path = _module_path(module)
        if path is None:
            continue
        queue.extend(_app_imports(path))
    assert "app.connectors.building_footprints_arcgis" not in seen
    assert "app.api.v1.scene_api" not in seen  # the scene route ships UNMOUNTED
    # The expected wiring: the scene assembler is the connector's one production consumer.
    assembler = API_ROOT / "app" / "scenario" / "scene_assembler.py"
    assert "app.connectors.building_footprints_arcgis" in _app_imports(assembler)


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


# ---------------------------------------------------------------------------
# M5-T100 riders (DB-058 e, h, l, m): findable-but-non-leaky internal errors, an
# end-to-end missing-geometry test, the one-half-wrong CRS pages, and the zero-year value.
# Every page below is SYNTHETIC (built in-memory here); no recorded fixture is added or
# changed, no new dependency is introduced, and nothing reaches the network.
# ---------------------------------------------------------------------------

LOGGER_NAME = "app.connectors.building_footprints_arcgis"


def _broken_transport(exc):
    """A transport that raises ``exc`` (an UNEXPECTED, non-transport error) on first call, so
    it propagates to the connector's catch-all internal_error branch."""
    def transport(url, headers, timeout):
        raise exc
    return transport


def _error_records(caplog):
    return [r for r in caplog.records
            if r.levelno == logging.ERROR and r.name == LOGGER_NAME]


def test_t100_internal_error_is_findable_and_logs_no_upstream_text(caplog):
    """AS-1 (DB-058 e): an UNEXPECTED exception whose MESSAGE echoes upstream body text is
    findable at error level (exception class + a sanitized bounded message + correlation id)
    while the returned refusal still carries ONLY the class name and the log leaks no
    upstream body text. Mutation guard: logging str(exc) (the raw message) reddens the
    absence assertions; downgrading/removing the log reddens the findability assertion."""
    upstream = 'UPSTREAM_BODY {"secret":"AdminSecret123"}\nFORGED: fake second log line'
    with caplog.at_level(logging.ERROR, logger=LOGGER_NAME):
        result = fetch_context_buildings(
            envelope=SUBJECT_ENVELOPE, transport=_broken_transport(RuntimeError(upstream)),
            clock=FIXED_CLOCK, correlation_id="t-cid")
    # The returned refusal is unchanged: class-name-only, never the exception message (G5-safe).
    refusal = refused(result, "internal_error")
    assert refusal.detail == {"exception": "RuntimeError"}
    records = _error_records(caplog)
    assert len(records) == 1, [r.getMessage() for r in records]
    line = records[0].getMessage()
    # Findable: the exception class, the sanitized message, and the correlation id are present.
    assert "class=RuntimeError" in line
    assert "unexpected internal failure - no data returned" in line
    assert "correlation_id=t-cid" in line
    # No upstream body text, embedded secret, or forged newline reaches the log.
    assert "AdminSecret123" not in line and "UPSTREAM_BODY" not in line
    assert "FORGED" not in line and "\n" not in line


def test_t100_internal_error_log_sanitizes_and_bounds_a_hostile_class_name(caplog):
    """AS-1 (DB-058 e): the exception CLASS is the only exception-derived field logged; a
    hostile class name (embedded control character, over-long) is neutralized by the shared
    transport sanitizer and length-bounded before it reaches the log, so it can neither forge
    a log line nor dump an unbounded value. Mutation guard: dropping the sanitizer leaves a
    raw newline; dropping the length bound drops the truncation marker."""
    hostile = type("Bad\nFORGED " + "Z" * 400, (Exception,), {})
    with caplog.at_level(logging.ERROR, logger=LOGGER_NAME):
        result = fetch_context_buildings(
            envelope=SUBJECT_ENVELOPE, transport=_broken_transport(hostile("boom")),
            clock=FIXED_CLOCK, correlation_id="t-cid")
    refused(result, "internal_error")
    records = _error_records(caplog)
    assert len(records) == 1
    line = records[0].getMessage()
    assert "\n" not in line  # the control character is repr-escaped, not a forged log line
    assert "...(truncated)" in line  # the over-long class name is length-bounded
    assert "ZZZZZZZZZZ" not in line[line.index("...(truncated)"):]  # bounded, not the full name


def test_t100_sanitized_bounded_neutralizes_control_chars_and_bounds_length():
    """AS-1 (DB-058 e): the shared-transport-sanitizer helper escapes control characters (no
    forged log line) and bounds length (no unbounded dump); an allowlist-safe short value
    passes through verbatim."""
    assert bf._sanitized_bounded("RuntimeError") == "RuntimeError"
    escaped = bf._sanitized_bounded("line1\nline2")
    assert "\n" not in escaped
    bounded = bf._sanitized_bounded("Z" * 500)
    assert bounded.endswith("...(truncated)")
    assert len(bounded) <= bf._LOG_FIELD_MAX + len("...(truncated)")


def test_t100_missing_geometry_key_is_typed_null_geometry_end_to_end():
    """AS-2 (DB-058 h): a feature that LACKS its 'geometry' key flows through the whole fetch
    to a typed invalid / null_geometry record - never an untyped error and never dropped.
    Mutation guard: removing the null_geometry guard in parse_footprint_geometry reddens the
    findings assertion (the finding becomes not_a_polygon_geometry)."""
    def mutate(page):
        del page["features"][1]["geometry"]
    result, _ = run({**SUBJECT_ROUTES, P1_URL: ok(synthetic_page(mutate))},
                    envelope=SUBJECT_ENVELOPE, page_size=2)
    assert result.status == "ok" and len(result.buildings) == 3
    subject = by_oid(result)[229537]
    assert subject.geometry_status == "invalid"
    assert subject.geometry_findings == ["null_geometry"]
    assert subject.parts == [] and subject.footprint_area_sq_ft is None
    assert subject.query_relation is None and subject.original_geometry is None


@pytest.mark.parametrize(
    "spatial_reference",
    [
        {"wkid": 102718, "latestWkid": 9999},  # kills MY1b (a gate that checks only wkid)
        {"wkid": 3857, "latestWkid": 2263},    # kills MY1a (a gate that checks only latestWkid)
    ],
)
def test_t100_crs_page_gate_requires_both_wkid_and_latest_wkid(spatial_reference):
    """AS-3 (DB-058 l): a page whose spatialReference has only ONE half of wkid 102718 /
    latestWkid 2263 is refused wrong_crs - the gate requires BOTH halves. Mutation guard:
    simplifying the gate to either half (G4 MY1a/MY1b) lets one of these pages through and
    reddens the wrong_crs refusal assertion."""
    def mutate(page):
        page["spatialReference"] = spatial_reference
    result, _ = run({**SUBJECT_ROUTES, P1_URL: ok(synthetic_page(mutate))},
                    envelope=SUBJECT_ENVELOPE, page_size=2)
    refusal = refused(result, "wrong_crs")
    assert refusal.request_url == P1_URL


def test_t100_zero_construction_year_nulls_the_value_not_only_the_gap():
    """AS-4 (DB-058 m): CONSTRUCTION_YEAR 0 yields construction_year None (the displaced
    value) AND the zero_not_available gap - never a false 'year 0'. Mutation guard: keeping
    year == 0 (G4 MY7, drop the `year = None`) reddens the None assertion."""
    def mutate(page):
        page["features"][1]["attributes"]["CONSTRUCTION_YEAR"] = 0
    result, _ = run({**SUBJECT_ROUTES, P1_URL: ok(synthetic_page(mutate))},
                    envelope=SUBJECT_ENVELOPE, page_size=2)
    subject = by_oid(result)[229537]
    assert subject.construction_year is None
    assert ("CONSTRUCTION_YEAR", "zero_not_available") in gap_codes(subject)


# ---------------------------------------------------------------------------
# M5-T101 PKT-C riders: the split (AS-1), memory + time bounds (AS-2), log
# safety (AS-3), datum + untrusted text (AS-4), the source_registry draft (AS-5).
# Every page/geometry below is SYNTHETIC or a monkeypatched config; no recorded
# fixture is added or changed and nothing reaches the network.
# ---------------------------------------------------------------------------


def test_pktc_geometry_split_is_reexported_and_acyclic():
    """AS-1: the ring/geometry helpers live in the geometry module; the connector re-exports
    the SAME objects, imports FROM it (one-way), and the geometry module imports nothing back -
    the import graph stays acyclic."""
    import app.connectors.building_footprints_geometry as geo
    assert bf.parse_footprint_geometry is geo.parse_footprint_geometry
    assert bf.classify_query_relation is geo.classify_query_relation
    assert bf.FootprintPart is geo.FootprintPart
    geo_src = Path(geo.__file__).read_text(encoding="utf-8")
    tree = ast.parse(geo_src)
    modules = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    modules |= {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    assert not any("building_footprints_arcgis" in m for m in modules)


def test_pktc_geometry_vertex_cap_refuses_before_retention(monkeypatch):
    """AS-2 (DB-058 b): one geometry above the vertex cap is refused resource_exhausted before
    it is retained. Mutation guard: raising MAX_GEOMETRY_VERTICES lets the query succeed."""
    monkeypatch.setattr(bf, "MAX_GEOMETRY_VERTICES", 4)  # real footprint rings carry more
    result, _ = run(SUBJECT_ROUTES, envelope=SUBJECT_ENVELOPE, page_size=2)
    refusal = refused(result, "resource_exhausted")
    assert refusal.detail["reason"] == "geometry_vertex_cap"
    assert refusal.detail["max_vertices"] == 4


def test_pktc_cumulative_bytes_ceiling_refuses_before_retention(monkeypatch):
    """AS-2 (DB-058 b): once cumulative decoded page bytes exceed the ceiling paging is refused
    resource_exhausted. Mutation guard: raising MAX_TOTAL_DECODED_BYTES lets the query run."""
    monkeypatch.setattr(bf, "MAX_TOTAL_DECODED_BYTES", 10)  # smaller than any real page body
    result, _ = run(SUBJECT_ROUTES, envelope=SUBJECT_ENVELOPE, page_size=2)
    refusal = refused(result, "resource_exhausted")
    assert refusal.detail["reason"] == "cumulative_bytes_ceiling"


def test_pktc_wall_clock_deadline_stops_paging_typed():
    """AS-2 (DB-058 c): a caller deadline already past stops paging with a typed
    deadline_exceeded refusal before any query page. A future deadline does not refuse.
    Mutation guard: a no-op _check_deadline lets paging complete."""
    past = datetime(2026, 9, 24, 11, 0, 0, tzinfo=UTC)  # before FIXED_CLOCK 12:00
    result, transport = run(SUBJECT_ROUTES, envelope=SUBJECT_ENVELOPE, page_size=2,
                            deadline=past)
    refusal = refused(result, "deadline_exceeded")
    assert refusal.detail["reason"] == "deadline_exceeded"
    # DB-073(c): the deadline is now checked BEFORE the metadata fetch too, so a past deadline
    # makes NO request at all (previously the metadata request was already in flight).
    assert transport.calls == []
    future = datetime(2026, 9, 24, 13, 0, 0, tzinfo=UTC)
    ok_result, _ = run(SUBJECT_ROUTES, envelope=SUBJECT_ENVELOPE, page_size=2, deadline=future)
    assert ok_result.status == "ok"


def test_pktc_interactive_caps_max_attempts_fail_fast():
    """AS-2 (DB-058 c): interactive=True caps attempts at INTERACTIVE_MAX_ATTEMPTS, so a
    transient 500 that a 3-attempt call retries past becomes an immediate refusal. Mutation
    guard: raising INTERACTIVE_MAX_ATTEMPTS restores the retry and the fetch succeeds."""
    p1 = ok(body("subject_2033800084_envelope_p1.json"))
    p2 = ok(body("subject_2033800084_envelope_p2.json"))
    routes = {**META, P1_URL: [TransportResponse(500, "busy"), p1], P2_URL: p2}
    ok_result, _ = run(routes, envelope=SUBJECT_ENVELOPE, page_size=2)
    assert ok_result.status == "ok", ok_result.refusal
    inter, _ = run(routes, envelope=SUBJECT_ENVELOPE, page_size=2, interactive=True)
    refused(inter, "upstream_error")


def test_pktc_safe_correlation_id_strips_control_and_falls_back():
    """AS-3 (DB-058 d / DB-066 b): the correlation-id sanitizer keeps a safe id verbatim,
    strips CR/LF and control characters, and falls back to a server-generated id when the
    input is missing, non-string, or emptied after stripping."""
    assert bf._safe_correlation_id("t-cid") == "t-cid"
    assert bf._safe_correlation_id("a\r\nb\x00c") == "abc"
    assert bf._safe_correlation_id(None) and bf._safe_correlation_id(None) != ""
    assert bf._safe_correlation_id("\r\n") != "" and "\n" not in bf._safe_correlation_id("x\ny")


def test_pktc_hostile_correlation_id_never_reaches_a_log_raw(caplog):
    """AS-3 (DB-058 d / DB-066 b): a caller correlation id carrying CR/LF/NUL is stripped at
    entry, so no raw control character reaches EITHER log site (this connector or the shared
    transport, which reads the same io.cid); the refusal carries the stripped id. Mutation
    guard: an identity _safe_correlation_id lets the raw newline forge a log line."""
    hostile = "abc\r\ndef\x00ghi\nFORGED"
    with caplog.at_level(logging.ERROR, logger=LOGGER_NAME):
        result = fetch_context_buildings(
            envelope=SUBJECT_ENVELOPE, transport=_broken_transport(RuntimeError("boom")),
            clock=FIXED_CLOCK, correlation_id=hostile)
    line = _error_records(caplog)[0].getMessage()
    assert "\n" not in line and "\r" not in line and "\x00" not in line
    assert "correlation_id=abcdefghiFORGED" in line
    assert result.correlation_id == "abcdefghiFORGED"
    assert result.refusal.correlation_id == "abcdefghiFORGED"


def test_pktc_trailing_newline_in_log_field_is_stripped_not_forged():
    """AS-3 (DB-066 a): the shared allowlist regex ends in `$`, which matches BEFORE a trailing
    newline - so 'Foo\\n' would pass through raw. PKT-C strips CR/LF outright first. Mutation
    guard: emptying _CONTROL_CHAR_DELETE lets the trailing newline survive."""
    assert bf._sanitized_bounded("Foo\n") == "Foo"
    assert "\n" not in bf._sanitized_bounded("Foo\r\n") and "\r" not in bf._sanitized_bounded("a\r")


def test_pktc_class_name_trailing_newline_is_stripped_end_to_end(caplog):
    """AS-3 (DB-066 a): a class __name__ that ENDS in a newline is logged without a raw newline
    (the real allowlist `$`-before-trailing-newline case). Mutation guard: emptying
    _CONTROL_CHAR_DELETE reddens the no-newline assertion."""
    hostile = type("EvilError\n", (Exception,), {})
    with caplog.at_level(logging.ERROR, logger=LOGGER_NAME):
        result = fetch_context_buildings(
            envelope=SUBJECT_ENVELOPE, transport=_broken_transport(hostile("x")),
            clock=FIXED_CLOCK, correlation_id="t-cid")
    refused(result, "internal_error")
    line = _error_records(caplog)[0].getMessage()
    assert "\n" not in line and "class=EvilError" in line


def test_pktc_short_alphanumeric_secret_in_message_never_logged(caplog):
    """AS-3 (DB-066 c): a BARE alphanumeric secret (which the shared allowlist would pass
    VERBATIM) in an exception message never reaches the log - the internal_error site logs a
    fixed message + the class name only, never str(exc). The paired passthrough assertion
    shows the sanitizer alone would NOT catch it, so message-omission is the guard. Mutation:
    logging str(exc) would leak the secret."""
    secret = "AdminSecret123"
    with caplog.at_level(logging.ERROR, logger=LOGGER_NAME):
        result = fetch_context_buildings(
            envelope=SUBJECT_ENVELOPE, transport=_broken_transport(RuntimeError(secret)),
            clock=FIXED_CLOCK, correlation_id="t-cid")
    refused(result, "internal_error")
    line = _error_records(caplog)[0].getMessage()
    assert secret not in line
    assert bf._sanitized_bounded(secret) == secret  # allowlist passthrough: omission is the guard


def test_pktc_typed_refusal_emits_no_error_record(caplog):
    """AS-3 (DB-066 d): a TYPED refusal (an upstream 500 and a disallowed_request) emits NO
    ERROR record - only the genuine internal_error branch logs at ERROR. Mutation guard: an
    ERROR log added to the typed refusal path would make this list non-empty (a double log)."""
    with caplog.at_level(logging.ERROR, logger=LOGGER_NAME):
        r1, _ = run({**META, P1_URL: [TransportResponse(500, "x")] * 3},
                    envelope=SUBJECT_ENVELOPE, page_size=2)
        r2, _ = run(META, envelope=(5, 5, 1, 9))
    refused(r1, "upstream_error")
    refused(r2, "disallowed_request")
    assert _error_records(caplog) == []


def test_pktc_datum_disclosure_and_untrusted_text_are_on_the_record():
    """AS-4 (DB-058 f, a): each record discloses BOTH ground-elevation definitions (none
    silently chosen), keeps NAVD88 as published, and lists the untrusted verbatim source-text
    fields consumers must escape on render."""
    result, _ = run(SUBJECT_ROUTES, envelope=SUBJECT_ENVELOPE, page_size=2)
    b = result.buildings[0]
    assert b.ground_datum == "NAVD88"
    assert "lowest elevation at building ground level" in b.ground_datum_basis
    assert "centroid" in b.ground_datum_basis
    assert "neither is chosen" in b.ground_datum_basis
    assert b.untrusted_text_fields == ("attributes", "geom_source", "last_status_type")
    assert "escape" in b.untrusted_text_notice.lower()


def test_pktc_zero_ground_elevation_is_a_typed_unverified_value_not_a_default():
    """AS-4 (DB-058 f): a zero GROUND_ELEVATION stays a real 0.0 flagged unverified - never
    None, never replaced by the site ground. Mutation guard: an _ground_attr that nulls a zero
    (mutate the consuming namespace) reddens the 0.0 assertion."""
    def mutate(page):
        page["features"][1]["attributes"]["GROUND_ELEVATION"] = 0
    result, _ = run({**SUBJECT_ROUTES, P1_URL: ok(synthetic_page(mutate))},
                    envelope=SUBJECT_ENVELOPE, page_size=2, site_ground_elevation_ft=197)
    subject = by_oid(result)[229537]
    assert subject.ground_elevation_ft == 0.0
    assert "ground_elevation_zero_unverified" in subject.flags


def test_pktc_source_registry_draft_matches_connector_identity():
    """AS-5 (DB-058 g): the source_registry draft mirrors the existing drafts, its primary
    source_id equals the connector SOURCE_ID, and the height-unit + datum inferences stay
    listed as open questions."""
    repo_root = API_ROOT.parents[1]
    draft = json.loads(
        (repo_root / "docs" / "research" / "source-registry-drafts"
         / "building-footprints.json").read_text(encoding="utf-8"))
    assert isinstance(draft, list) and draft
    primary = draft[0]
    assert primary["source_id"] == SOURCE_ID
    for key in ("agency", "official_url", "fields_available", "known_limitations",
                "open_questions"):
        assert key in primary
    blob = json.dumps(primary)
    assert "RQ-1" in blob and "RQ-2" in blob  # height-unit + datum inferences stay open


# ---------------------------------------------------------------------------
# M5-T107 PKT-E riders (DB-073 a-g): the wiring packet's pre-consumption fixes to the
# connector - the correlation-id sanitiser also strips U+2028/U+2029 and is length-bounded;
# the deadline is honoured before the metadata fetch and during retry sleeps; a tz-naive
# deadline is a typed disallowed_request; a multi-page advancing-clock deadline test and a
# cumulative-bytes ceiling test between the one-page and two-page sums. Every page/geometry
# below is SYNTHETIC or a monkeypatched config; nothing reaches the network.
# ---------------------------------------------------------------------------


def test_pkte_correlation_id_strips_line_and_paragraph_separators(caplog):
    """DB-073(a) / M5-T101 G5 L-1: the sanitizer strips U+2028 (line) and U+2029 (paragraph)
    separators too, so a cid carrying them cannot forge a log line at either log site and a
    consumer that renders result.correlation_id raw is safe. Mutation guard: removing
    0x2028/0x2029 from _CONTROL_CHAR_DELETE leaves the separators in and reddens both the unit
    and the end-to-end assertions."""
    assert bf._safe_correlation_id("A B C") == "ABC"
    assert len(bf._safe_correlation_id("A B C").splitlines()) == 1
    with caplog.at_level(logging.ERROR, logger=LOGGER_NAME):
        result = fetch_context_buildings(
            envelope=SUBJECT_ENVELOPE, transport=_broken_transport(RuntimeError("boom")),
            clock=FIXED_CLOCK, correlation_id="pre post FORGED")
    line = _error_records(caplog)[0].getMessage()
    assert " " not in line and " " not in line
    assert "correlation_id=prepostFORGED" in line
    assert result.correlation_id == "prepostFORGED"


def test_pkte_correlation_id_is_length_bounded_at_the_source():
    """DB-073(b) / M5-T101 G5 L-2: a very long printable cid is length-bounded to _LOG_FIELD_MAX
    at the source, so a hostile caller cannot dump an unbounded id at every log site (incl. once
    per retry attempt in the shared transport). Mutation guard: removing the length bound in
    _safe_correlation_id restores the 5000-char value and reddens this."""
    bounded = bf._safe_correlation_id("z" * 5000)
    assert bounded.endswith("...(truncated)")
    assert len(bounded) <= bf._LOG_FIELD_MAX + len("...(truncated)")
    assert bf._safe_correlation_id("t-cid") == "t-cid"  # a short cid is unchanged


def test_pkte_deadline_checked_before_the_metadata_fetch():
    """DB-073(c): a past deadline refuses deadline_exceeded BEFORE any request - not even the
    metadata fetch is made. Mutation guard: removing the pre-metadata _check_deadline lets the
    metadata request go out (transport.calls != [])."""
    past = datetime(2026, 9, 24, 11, 0, 0, tzinfo=UTC)
    result, transport = run(SUBJECT_ROUTES, envelope=SUBJECT_ENVELOPE, page_size=2,
                            deadline=past)
    assert refused(result, "deadline_exceeded")
    assert transport.calls == []


def test_pkte_deadline_refuses_during_a_retry_sleep():
    """DB-073(c): the deadline is honoured DURING retry backoff, not only at each page top. A
    transient 500 triggers a retry; the clock crosses the deadline before the sleep, so the
    connector refuses deadline_exceeded rather than overshooting by the retry budget. Mutation
    guard: passing the plain self.sleep (dropping the _check_deadline in _sleep_within_deadline)
    lets the retry proceed and the call refuses upstream_error after the budget instead."""
    before = datetime(2026, 9, 24, 11, 0, 0, tzinfo=UTC)
    after = datetime(2026, 9, 24, 13, 0, 0, tzinfo=UTC)
    deadline = datetime(2026, 9, 24, 12, 0, 0, tzinfo=UTC)
    state = {"attempt1": False}

    def clock():
        return after if state["attempt1"] else before

    def transport(url, headers, timeout):
        if url == build_metadata_url():
            return ok(body("layer_metadata.json"))
        state["attempt1"] = True  # a P1 attempt just happened -> clock now past the deadline
        return TransportResponse(500, "busy")

    result = fetch_context_buildings(
        envelope=SUBJECT_ENVELOPE, page_size=2, transport=transport, clock=clock,
        sleep=lambda _s: None, rng=Random(0), correlation_id="t-cid", max_attempts=3,
        deadline=deadline)
    assert result.status == "refused"
    assert result.refusal.error_type == "deadline_exceeded"


def test_pkte_tz_naive_deadline_is_a_typed_disallowed_request():
    """DB-073(d): a tz-naive deadline is refused as disallowed_request BEFORE any I/O, not a
    TypeError -> internal_error from the comparison. Mutation guard: removing _validate_deadline
    lets the naive datetime reach _check_deadline and become internal_error."""
    naive = datetime(2026, 9, 24, 13, 0, 0)  # no tzinfo
    result, transport = run(SUBJECT_ROUTES, envelope=SUBJECT_ENVELOPE, page_size=2,
                            deadline=naive)
    assert result.refusal.error_type == "disallowed_request"
    assert result.refusal.detail["reason"] == "tz_naive_deadline"
    assert transport.calls == []


def test_pkte_deadline_is_checked_at_every_page_not_once():
    """DB-073(f) / M5-T101 G4 A1: with an advancing clock the deadline trips on the SECOND page,
    proving each page top checks the deadline (not a hoisted once-only check). Mutation guard: a
    once-only check hoisted before the paging loop (using the pre-loop 'before' time) lets both
    pages through and the call succeeds - reddening this refusal assertion."""
    before = datetime(2026, 9, 24, 11, 0, 0, tzinfo=UTC)
    after = datetime(2026, 9, 24, 13, 0, 0, tzinfo=UTC)
    deadline = datetime(2026, 9, 24, 12, 0, 0, tzinfo=UTC)
    state = {"page1": False}

    def clock():
        return after if state["page1"] else before

    replay = Replay(SUBJECT_ROUTES)

    def transport(url, headers, timeout):
        resp = replay(url, headers, timeout)
        if url == P1_URL:
            state["page1"] = True  # page 1 fetched -> the page-2 top check is now past deadline
        return resp

    result = fetch_context_buildings(
        envelope=SUBJECT_ENVELOPE, page_size=2, transport=transport, clock=clock,
        sleep=lambda _s: None, rng=Random(0), correlation_id="t-cid", deadline=deadline)
    assert result.status == "refused"
    assert result.refusal.error_type == "deadline_exceeded"
    assert replay.calls == [build_metadata_url(), P1_URL]  # page 2 never fetched


def test_pkte_cumulative_bytes_ceiling_is_between_the_one_and_two_page_sums(monkeypatch):
    """DB-073(g) / M5-T101 G4 A2: with the ceiling set BETWEEN the one-page and two-page byte
    sums, the query refuses cumulative_bytes_ceiling on the second page - proving the byte total
    accumulates across pages. Mutation guard: a per-page reset (decoded_bytes = len(body) each
    page) leaves page 2 under the ceiling and lets the query succeed - reddening this."""
    b1 = len(body("subject_2033800084_envelope_p1.json").encode("utf-8"))
    b2 = len(body("subject_2033800084_envelope_p2.json").encode("utf-8"))
    monkeypatch.setattr(bf, "MAX_TOTAL_DECODED_BYTES", b1 + b2 - 1)
    result, transport = run(SUBJECT_ROUTES, envelope=SUBJECT_ENVELOPE, page_size=2)
    refusal = refused(result, "resource_exhausted")
    assert refusal.detail["reason"] == "cumulative_bytes_ceiling"
    assert transport.calls == [build_metadata_url(), P1_URL, P2_URL]
