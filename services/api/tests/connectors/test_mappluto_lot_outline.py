"""MapPLUTO lot-outline connector acceptance pack (task M5-T020, D-040-R001).

Fully OFFLINE and deterministic: every case drives the connector through the
injected transport seam against the RECORDED f=geojson&outSR=4326 fixtures
(services/api/tests/fixtures/mappluto_lot_outline). No test touches the network.

Coverage maps to the packet scenarios:
- S1/S2: each typed outcome from its recorded fixture (single_lot Polygon /
  MultiPolygon / condo-billing; no_outline condo-unit and no-feature;
  multiple_features review; invalid_geometry) - contract-valid, honest.
- URL-builder injection resistance (S3): the BBL is the only variable and comes
  only from normalize_bbl; a non-canonical value is refused.
- lng/lat plausibility asserted FIXTURE-DERIVED (S1).
- display_only + EPSG:4326 crs + +/-20 ft accuracy note + NYC DCP attribution
  present on EVERY outcome (S1/S2).
- display-only boundary (S4): the module computes NO area/dimension and does not
  import shapely (grep-provable static assertion).
- recorded-official fixtures (S5): each raw fixture's sha256 matches the MANIFEST;
  synthetic negatives declare derived_from.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from app.connectors import mappluto_lot_outline as mlo
from app.connectors.bbl import BBLValidationError, normalize_bbl
from app.connectors.mappluto_geometry_arcgis import DisallowedRequestError
from app.connectors.mappluto_lot_outline import (
    CRS_4326,
    LotOutlineError,
    LotOutlineResultMismatchError,
    LotOutlineTransport,
    MalformedOutlineResponseError,
    UnexpectedCRSError,
    build_lot_outline,
    build_outline_query_url,
    parse_lot_outline,
    validate_lot_geometry_document,
)

FX = Path(__file__).resolve().parents[1] / "fixtures" / "mappluto_lot_outline"
MANIFEST = json.loads((FX / "MANIFEST.json").read_text(encoding="utf-8"))

# NYC WGS84 bounding box (generous) for lng/lat plausibility.
NYC_LNG = (-74.30, -73.60)
NYC_LAT = (40.40, 41.00)

RETRIEVED_AT = "2026-09-12T13:45:07Z"


def _transport_for(bbl: str, fixture_file: str) -> LotOutlineTransport:
    body = (FX / fixture_file).read_text(encoding="utf-8")
    return LotOutlineTransport(
        url=build_outline_query_url(bbl), status=200, body=body, retrieved_at=RETRIEVED_AT
    )


def _build(bbl: str, fixture_file: str) -> dict:
    return build_lot_outline(bbl, fetch=lambda c, i: _transport_for(c, fixture_file))


# ---------------------------------------------------------------------------
# S1/S2 - every typed outcome from its recorded fixture
# ---------------------------------------------------------------------------

OUTCOME_CASES = [
    ("1008350041", "LOT01_single_1008350041.geojson", "single_lot", "Polygon"),
    ("4142600001", "LOT06_multipolygon_4142600001.geojson", "single_lot", "MultiPolygon"),
    ("1000010010", "LOT05_holes_1000010010.geojson", "single_lot", "Polygon"),
    ("1000157501", "LOT03_condo_billing_1000157501.geojson", "single_lot", "Polygon"),
    ("1000151001", "LOT04_condo_unit_1000151001.geojson", "no_outline", None),
    ("5999999999", "LOT02_nofeature_5999999999.geojson", "no_outline", None),
    ("1008350041", "LOT96_multiple_features_synthetic.geojson", "multiple_features", None),
    ("1008350041", "LOT80_invalid_geometry_null_synthetic.geojson", "invalid_geometry", None),
]
_OUTCOME_IDS = [c[1] for c in OUTCOME_CASES]


@pytest.mark.parametrize("bbl,fixture,outcome,geom_type", OUTCOME_CASES, ids=_OUTCOME_IDS)
def test_outcome_is_typed_and_contract_valid(bbl, fixture, outcome, geom_type):
    env = _build(bbl, fixture)
    validate_lot_geometry_document(env)  # must not raise
    assert env["outcome"] == outcome
    assert env["bbl"] == bbl
    if geom_type is None:
        assert env["geometry"] is None  # geometry withheld / absent, never fabricated
    else:
        assert env["geometry"]["type"] == geom_type
        assert env["geometry"]["coordinates"]


def test_single_lot_bbl_1008350041_details():
    env = _build("1008350041", "LOT01_single_1008350041.geojson")
    assert env["feature_count"] == 1
    assert env["condo_classification"]["classification"] == "standard_lot"
    assert env["source"]["dataset_version"] == "26v2"
    assert env["lot_identity"]["block"] == 835
    assert env["lot_identity"]["lot"] == 41


def test_condo_billing_lot_surfaces_merged_complex_caveat():
    env = _build("1000157501", "LOT03_condo_billing_1000157501.geojson")
    assert env["outcome"] == "single_lot"
    assert env["condo_classification"]["classification"] == "condo_billing_lot"
    assert env["condo_classification"]["condo_no"] == 1025
    assert any("complex" in n.lower() for n in env["notes"])


def test_condo_unit_lot_is_honest_no_outline_not_error():
    env = _build("1000151001", "LOT04_condo_unit_1000151001.geojson")
    assert env["outcome"] == "no_outline"
    assert env["no_outline_reason"] == "condo_unit_lot_no_polygon"
    assert env["condo_classification"]["classification"] == "condo_unit_lot_query"
    assert env["geometry"] is None


def test_no_feature_bbl_is_no_outline_no_feature_reason():
    env = _build("5999999999", "LOT02_nofeature_5999999999.geojson")
    assert env["outcome"] == "no_outline"
    assert env["no_outline_reason"] == "no_feature_for_bbl"


def test_multiple_features_is_review_never_first_pick():
    env = _build("1008350041", "LOT96_multiple_features_synthetic.geojson")
    assert env["outcome"] == "multiple_features"
    assert env["feature_count"] == 2
    assert env["review_required"] is True
    assert env["geometry"] is None  # never a silent first-pick


def test_invalid_geometry_is_typed_outcome_not_500():
    env = _build("1008350041", "LOT80_invalid_geometry_null_synthetic.geojson")
    assert env["outcome"] == "invalid_geometry"
    assert env["feature_count"] == 1
    assert env["geometry"] is None


# ---------------------------------------------------------------------------
# S1 - lng/lat plausibility, asserted FIXTURE-DERIVED (verbatim transport)
# ---------------------------------------------------------------------------


def _iter_positions(geom):
    coords = geom["coordinates"]
    rings = coords if geom["type"] == "Polygon" else [r for poly in coords for r in poly]
    for ring in rings:
        yield from ring


def test_single_lot_coordinates_are_plausible_nyc_lnglat():
    env = _build("1008350041", "LOT01_single_1008350041.geojson")
    positions = list(_iter_positions(env["geometry"]))
    assert positions
    for lng, lat in positions:
        assert NYC_LNG[0] < lng < NYC_LNG[1], f"lng {lng} out of NYC range"
        assert NYC_LAT[0] < lat < NYC_LAT[1], f"lat {lat} out of NYC range"


def test_geometry_is_verbatim_from_the_recorded_fixture():
    raw = json.loads((FX / "LOT06_multipolygon_4142600001.geojson").read_text(encoding="utf-8"))
    env = _build("4142600001", "LOT06_multipolygon_4142600001.geojson")
    assert env["geometry"] == raw["features"][0]["geometry"]  # byte-for-byte structural equality


# ---------------------------------------------------------------------------
# Every outcome carries the display-only markers, crs, accuracy, attribution
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bbl,fixture", [(c[0], c[1]) for c in OUTCOME_CASES], ids=_OUTCOME_IDS
)
def test_every_outcome_carries_display_markers(bbl, fixture):
    env = _build(bbl, fixture)
    assert env["display_only"] is True
    assert env["crs"] == CRS_4326 == "EPSG:4326"
    assert "20 ft" in env["accuracy_note"] and "DISPLAY-ONLY" in env["accuracy_note"]
    assert "DCP" in env["attribution"] and "City Planning" in env["attribution"]
    assert env["disclaimer"]
    assert env["source"]["source_id"] == "nyc-dcp-mappluto-arcgis"
    assert env["source"]["endpoint"].endswith("&f=geojson&outSR=4326")


# ---------------------------------------------------------------------------
# S3 - URL builder injection resistance
# ---------------------------------------------------------------------------


def test_url_builder_emits_geojson_4326_and_int_where_clause():
    url = build_outline_query_url("1008350041")
    assert "f=geojson&outSR=4326" in url
    assert "where=BBL%3D1008350041" in url  # int-interpolated canonical BBL only
    assert url.startswith(
        "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/MAPPLUTO/FeatureServer/0/query"
    )


@pytest.mark.parametrize(
    "bad",
    ["1008350041 OR 1=1", "1008350041&f=json", "10083500", "'; DROP", "1008350041\n"],
)
def test_url_builder_refuses_non_canonical_bbl(bad):
    # A non-canonical value is refused before it can reach the URL - either as a
    # BBL validation error or a DisallowedRequestError; never interpolated raw.
    with pytest.raises((BBLValidationError, DisallowedRequestError)):
        build_outline_query_url(bad)


def test_build_lot_outline_propagates_bbl_validation_error():
    with pytest.raises(BBLValidationError):
        build_lot_outline("not-a-bbl", fetch=lambda c, i: pytest.fail("fetch must not run"))


# ---------------------------------------------------------------------------
# Typed transport/parse FAULTS (never mistaken for a valid empty outline)
# ---------------------------------------------------------------------------


_NORM = normalize_bbl("1008350041")


def _raw_transport(body: str, status: int = 200) -> LotOutlineTransport:
    return LotOutlineTransport(
        url=build_outline_query_url("1008350041"),
        status=status,
        body=body,
        retrieved_at=RETRIEVED_AT,
    )


def _parse(body: str, *, status: int = 200) -> dict:
    return parse_lot_outline(
        _raw_transport(body, status=status), normalized=_NORM, correlation_id="c"
    )


def test_non_200_status_is_upstream_error():
    with pytest.raises(LotOutlineError) as exc:
        _parse("{}", status=503)
    assert exc.value.error_type == "upstream_error"


def test_non_json_body_is_malformed():
    with pytest.raises(MalformedOutlineResponseError):
        _parse("<html>not json")


def test_non_featurecollection_is_malformed():
    with pytest.raises(MalformedOutlineResponseError):
        _parse('{"type":"Feature"}')


def test_arcgis_error_object_with_200_is_upstream():
    with pytest.raises(LotOutlineError) as exc:
        _parse('{"error":{"code":400,"message":"Invalid query"}}')
    assert exc.value.error_type == "upstream_error"


def test_wrong_crs_is_rejected_before_transport():
    body = json.dumps(
        {
            "type": "FeatureCollection",
            "crs": {"type": "name", "properties": {"name": "EPSG:2263"}},
            "features": [],
        }
    )
    with pytest.raises(UnexpectedCRSError):
        _parse(body)


def test_result_mismatch_when_returned_bbl_differs():
    raw = json.loads((FX / "LOT01_single_1008350041.geojson").read_text(encoding="utf-8"))
    raw["features"][0]["properties"]["BBL"] = 1000000001
    with pytest.raises(LotOutlineResultMismatchError):
        _parse(json.dumps(raw))


def test_missing_crs_member_is_tolerated_as_4326():
    # A geojson response with no crs member implies the requested outSR; the
    # only unsafe case is a PRESENT-but-different CRS (covered above).
    env = _parse(json.dumps({"type": "FeatureCollection", "features": []}))
    assert env["outcome"] == "no_outline"
    assert env["crs"] == "EPSG:4326"


# ---------------------------------------------------------------------------
# S4 - DISPLAY-ONLY boundary: no measurement, no shapely (grep-provable)
# ---------------------------------------------------------------------------


def test_module_computes_no_area_and_does_not_import_shapely():
    source = Path(mlo.__file__).read_text(encoding="utf-8")
    lowered = source.lower()
    assert "import shapely" not in lowered
    assert "compute_area" not in lowered
    assert "area_sq_ft" not in lowered
    assert ".area" not in source  # no shapely/geometry area access


# ---------------------------------------------------------------------------
# S5 - recorded-official fixtures: verbatim bytes match the MANIFEST
# ---------------------------------------------------------------------------


_FX_ENTRIES = MANIFEST["fixtures"]
_FX_IDS = [e["fixture_id"] for e in _FX_ENTRIES]


@pytest.mark.parametrize("entry", _FX_ENTRIES, ids=_FX_IDS)
def test_fixture_bytes_match_manifest_sha256(entry):
    data = (FX / entry["file"]).read_bytes()
    digest = "sha256:" + hashlib.sha256(data).hexdigest()
    assert digest == entry["response_body_sha256"], f"{entry['file']} drifted from MANIFEST"


def test_synthetic_fixtures_declare_derivation_and_raw_do_not():
    for entry in MANIFEST["fixtures"]:
        if entry["classification"] == "synthetic":
            assert entry["derived_from"], f"{entry['file']} must declare derived_from"
        else:
            assert entry["classification"] == "raw"
            assert entry["derived_from"] is None
