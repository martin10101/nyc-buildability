"""Integrity of the recorded benchmark-lot pack (queue item B-01; plan M1-20, C-3, C-7, C-8, C-9).

services/api/tests/fixtures/benchmark_215_16_northern/ holds official responses for
215-16 Northern Blvd, Queens (BBL 4073340070), captured once on 2026-09-30 UTC. MANIFEST.json
pins each file by SHA-256 of its exact bytes. These tests are offline: they re-hash every
file and prove that each connector-backed request URL is the one the connector itself builds.
"""

import hashlib
import json
from pathlib import Path

import pytest

from app.connectors import (
    building_footprints_arcgis,
    dcm_street_centerline_arcgis,
    dtm_lot_outline,
    mappluto_geometry_arcgis,
    mappluto_lot_outline,
    pluto_soda,
    zoning_features_arcgis,
    ztldb_soda,
)

PACK = Path(__file__).resolve().parents[1] / "fixtures" / "benchmark_215_16_northern"
MANIFEST = json.loads((PACK / "MANIFEST.json").read_text(encoding="utf-8"))
ENTRIES = {entry["file"]: entry for entry in MANIFEST["files"]}
NOT_RECORDINGS = {"MANIFEST.json", "README.md", ".gitattributes"}
BBL = "4073340070"
# MapPLUTO lot bounds (EPSG:2263, 0.01 ft) padded by 100 ft (wide-street buffer) + 50 ft margin,
# as app.spatial.wide_street_live_provider derives its DCM query envelope.
DCM_ENVELOPE = (1048638.63, 216160.44, 1049061.58, 216581.1)


def _lot_ring() -> list[list[float]]:
    doc = json.loads((PACK / "mappluto_lot_4073340070_epsg2263.json").read_bytes())
    return doc["features"][0]["geometry"]["rings"][0]


def test_manifest_lists_exactly_the_recorded_files():
    on_disk = {path.name for path in PACK.iterdir()} - NOT_RECORDINGS
    assert on_disk == set(ENTRIES)
    assert len(MANIFEST["files"]) == len(ENTRIES)
    assert MANIFEST["bbl"] == BBL


@pytest.mark.parametrize("name", sorted(ENTRIES))
def test_file_bytes_match_manifest_sha256(name):
    entry = ENTRIES[name]
    body = (PACK / name).read_bytes()
    assert len(body) == entry["bytes"]
    assert hashlib.sha256(body).hexdigest() == entry["sha256"]
    assert entry["http_status"] == 200
    assert entry["url"].startswith("https://")
    assert entry["retrieved_at"].startswith("2026-09-30T")
    assert entry["connector"] or entry["documented_in"]


def test_dcm_envelope_is_the_padded_lot_bounds():
    ring = _lot_ring()
    xs = [round(x, 2) for x, _ in ring]
    ys = [round(y, 2) for _, y in ring]
    expected = (min(xs) - 150, min(ys) - 150, max(xs) + 150, max(ys) + 150)
    assert DCM_ENVELOPE == pytest.approx(expected, abs=1e-6)


def test_connector_backed_urls_are_the_connectors_own_requests():
    zf = zoning_features_arcgis
    r6b = zf.build_attribute_where("nyzd", "ZONEDIST", "R6B")
    c22 = zf.build_attribute_where("nyco", "OVERLAY", "C2-2")
    built = {
        "pluto_64uk-42ks_bbl_4073340070.json": f"{pluto_soda.BASE_URL}?bbl={BBL}",
        "ztldb_fdkv-4t4z_bbl_4073340070.json": ztldb_soda.build_record_url(BBL),
        "ztldb_fdkv-4t4z_api_views_metadata.json": ztldb_soda.API_VIEWS_URL,
        "mappluto_layer_metadata.json": mappluto_geometry_arcgis.build_metadata_url(),
        "mappluto_lot_4073340070_epsg2263.json": mappluto_geometry_arcgis.build_lot_query_url(BBL),
        "mappluto_lot_outline_4073340070_epsg4326.geojson":
            mappluto_lot_outline.build_outline_query_url(BBL),
        "dtm_layer_metadata.json": f"{dtm_lot_outline.SERVICE_ROOT}/0?f=json",
        "dtm_lot_outline_4073340070_epsg4326.geojson": dtm_lot_outline.build_outline_query_url(BBL),
        "zoning_nyzd_layer_metadata.json": zf.build_metadata_url("nyzd"),
        "zoning_nyco_layer_metadata.json": zf.build_metadata_url("nyco"),
        "zoning_nyzd_count_R6B.json": zf.build_count_url("nyzd", r6b),
        "zoning_nyco_count_C2-2.json": zf.build_count_url("nyco", c22),
        "zoning_nyzd_query_R6B.json": zf.build_query_url(
            "nyzd", r6b, result_record_count=zf.MAX_RESULT_RECORD_COUNT, result_offset=0),
        "zoning_nyco_query_C2-2.json": zf.build_query_url(
            "nyco", c22, result_record_count=zf.MAX_RESULT_RECORD_COUNT, result_offset=0),
        "dcm_layer_metadata.json": dcm_street_centerline_arcgis.build_metadata_url(),
        "dcm_street_centerline_lot_envelope_4073340070.json":
            dcm_street_centerline_arcgis.build_segment_query_url(envelope=DCM_ENVELOPE),
        "building_footprints_layer_metadata.json": building_footprints_arcgis.build_metadata_url(),
        "building_footprints_lot_polygon_4073340070.json":
            building_footprints_arcgis.build_query_url(polygon=_lot_ring(), page_size=2000),
    }
    connector_backed = {name for name, entry in ENTRIES.items() if entry["connector"]}
    assert connector_backed == set(built)
    for name, url in built.items():
        assert ENTRIES[name]["url"] == url, name
