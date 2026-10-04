"""Replay the recorded 215-16 Northern pack's zoning-district and building-footprint map
layers through the REAL connectors, offline (maps connection step 1; D-090-R124).

``replay_nyzd_page()`` and ``replay_footprints_lot_polygon()`` serve the recorded pack bytes
to ``zoning_features_arcgis.query_features`` / ``building_footprints_arcgis`` 's
``fetch_context_buildings`` by URL, so the connectors' OWN typed results are reproduced with no
network. These tests pin
the recorded counts/ids, prove each request URL + raw digest is the one the MANIFEST recorded,
and confirm the authoritative EPSG:2263 CRS stamp. The two pack literals asserted are the
object id (3201) and feature count (185) of the recorded nyzd page; everything else (the bbox
containment, the footprint BINs) is computed or read from the pack, never restated.
"""

from __future__ import annotations

import json

from ._northern_replay import (
    MANIFEST,
    PACK,
    manifest_digest,
    replay_footprints_lot_polygon,
    replay_lot_geometry,
    replay_nyzd_page,
)

NYZD_PAGE_FILE = "zoning_nyzd_query_R6B.json"
FOOTPRINTS_PAGE_FILE = "building_footprints_lot_polygon_4073340070.json"
# Material-overlap relations (a boundary-touch-only footprint is NOT an intersection).
MATERIAL_OVERLAP = {"within", "partial_overlap"}


def _bbox(ring: list[list[float]]) -> tuple[float, float, float, float]:
    xs = [x for x, _ in ring]
    ys = [y for _, y in ring]
    return min(xs), min(ys), max(xs), max(ys)


def _recorded_footprint_bins() -> set[int]:
    """Read the expected BINs straight from the recorded footprint page (never restated)."""
    doc = json.loads((PACK / FOOTPRINTS_PAGE_FILE).read_bytes())
    return {feature["attributes"]["BIN"] for feature in doc["features"]}


def test_nyzd_page_is_the_connectors_own_r6b_result() -> None:
    result = replay_nyzd_page()
    assert result.status == "ok"
    assert result.layer == "nyzd"
    assert result.record_count == 185
    object_ids = [feature["object_id"] for feature in result.features]
    assert 3201 in object_ids
    feature = next(f for f in result.features if f["object_id"] == 3201)
    assert feature["attributes"]["ZONEDIST"] == "R6B"


def test_nyzd_object_3201_ring_bbox_contains_the_lot_ring() -> None:
    result = replay_nyzd_page()
    feature = next(f for f in result.features if f["object_id"] == 3201)
    zone_bbox = _bbox(feature["geometry"]["rings"][0])
    lot_ring = replay_lot_geometry().features[0]["geometry"]["rings"][0]
    lot_bbox = _bbox(lot_ring)
    # The R6B district polygon's bbox must enclose the benchmark lot's ring bbox.
    assert zone_bbox[0] <= lot_bbox[0]
    assert zone_bbox[1] <= lot_bbox[1]
    assert zone_bbox[2] >= lot_bbox[2]
    assert zone_bbox[3] >= lot_bbox[3]


def test_nyzd_provenance_and_crs_match_the_manifest() -> None:
    result = replay_nyzd_page()
    assert result.request_url == MANIFEST[NYZD_PAGE_FILE]["url"]
    assert result.raw_digest == manifest_digest(NYZD_PAGE_FILE)
    assert result.crs["latest_wkid"] == 2263


def test_footprints_hold_exactly_the_two_intersecting_buildings() -> None:
    result = replay_footprints_lot_polygon()
    assert result.status == "ok"
    assert result.refusal is None
    expected_bins = _recorded_footprint_bins()
    assert len(result.buildings) == len(expected_bins) == 2
    assert {building.bin for building in result.buildings} == expected_bins
    # Both footprints materially overlap the lot (a boundary touch is not an intersection).
    for building in result.buildings:
        assert building.query_relation in MATERIAL_OVERLAP
        assert building.query_overlap_area_sq_ft is not None
        assert building.query_overlap_area_sq_ft > 0.0


def test_footprints_provenance_and_crs_match_the_manifest() -> None:
    result = replay_footprints_lot_polygon()
    assert result.request_urls[0] == MANIFEST[FOOTPRINTS_PAGE_FILE]["url"]
    assert result.raw_digests[0] == manifest_digest(FOOTPRINTS_PAGE_FILE)
    assert result.crs["latest_wkid"] == 2263
