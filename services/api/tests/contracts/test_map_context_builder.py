"""Builder tests for map_context v1 (maps connection step 3, D-090-R124).

The builder :func:`app.contracts.map_context.build_map_context` turns the
recorded 215-16 Northern pack's THREE typed connector results - MapPLUTO lot
geometry, the ``nyzd`` zoning attribute-query page, the OTI building-footprint
context result - into the ONE document the E-07 renderers consume. These tests
replay the pack OFFLINE through the real connectors (no network) and prove:

* the built document is schema-valid AND loads through the E-07 adapter;
* the subject ring is the pack's own lot ring (read from the replayed result);
* exactly one zoning district (OBJECTID 3201, R6B) and the two intersecting
  footprints (BINs read from the replayed result) are drawn;
* every drawable layer's provenance is the MANIFEST's (request URL, digest);
* a non-2263 layer, a None layer and an adapter-refused ring all demote to
  ``not_available`` (the refused ring carrying the adapter's own message);
* a refused subject outline raises ``MapContextUnavailable``;
* NO geometry is fabricated - every output ring is an input ring (or a
  ``parse_footprint_geometry`` split of one), byte for byte.
"""

from __future__ import annotations

import pytest

from app.connectors.building_footprints_geometry import (
    FootprintPart,
    parse_footprint_geometry,
)
from app.contracts.map_context import (
    MapContextUnavailable,
    MapNotes,
    build_map_context,
)
from app.contracts.study_contracts import validate_map_context_document
from app.drawings.maps.adapter import load_map_context
from app.drawings.maps.model import BuildingLayer, LayerUnavailable, ZoningLayer
from tests.spatial._northern_replay import (
    MANIFEST,
    manifest_digest,
    replay_footprints_lot_polygon,
    replay_lot_geometry,
    replay_nyzd_page,
)

WINDOW_FT = 150.0
NYZD_PAGE_FILE = "zoning_nyzd_query_R6B.json"
FOOTPRINTS_PAGE_FILE = "building_footprints_lot_polygon_4073340070.json"
NYZD_LOCAL_OBJECT_ID = 3201  # the one R6B district whose ring bbox contains the lot


def _notes(nyzd: object, footprints: object) -> MapNotes:
    """The README notes the caller supplies; the source edit dates are read from
    the replayed results, never restated."""
    return MapNotes(
        zoning_attribution=(
            "Zoning districts: NYC Department of City Planning, NYC GIS Zoning Features "
            "(nyzd), via NYC Open Data under the NYC Open Data Terms of Use; source edit "
            f"date {nyzd.source_data_last_edited[:10]}."
        ),
        zoning_accuracy=(
            "Zoning-district boundaries are approximate: the DCP horizontal accuracy "
            "statement is approximately +/- 20 ft, so a boundary drawn near the lot is not "
            "a lot-level determination."
        ),
        zoning_use_limitation=(
            "These features are not intended for determining zoning at the individual tax "
            "lot level."
        ),
        zoning_coverage=(
            "This zoning layer was retrieved by an attribute query for ZONEDIST 'R6B'; "
            "neighbouring districts of other codes were not retrieved."
        ),
        buildings_attribution=(
            "Building footprints: NYC Office of Technology and Innovation, Building "
            "Footprints (NYC Open Data 5zhs-2jue), under the NYC Open Data Terms of Use; "
            f"source edit date {footprints.source_data_last_edited[:10]}."
        ),
    )


def _build_northern() -> dict:
    lot = replay_lot_geometry()
    nyzd = replay_nyzd_page()
    footprints = replay_footprints_lot_polygon()
    return build_map_context(lot, nyzd, footprints, window_ft=WINDOW_FT,
                             notes=_notes(nyzd, footprints))


def _feature_by_object_id(nyzd: object, object_id: int) -> dict:
    return next(f for f in nyzd.features if f["object_id"] == object_id)


def _as_float_rings(rings: list) -> list:
    return [[[float(x), float(y)] for x, y in ring] for ring in rings]


# ---------------------------------------------------------------------------
# Happy path: schema-valid, adapter-loadable, exactly the recorded content.
# ---------------------------------------------------------------------------


def test_northern_document_is_schema_valid_and_adapter_loadable() -> None:
    document = _build_northern()
    validate_map_context_document(document)  # raises on any defect
    context = load_map_context(document)
    assert context.crs == "EPSG:2263"
    assert context.measurement_label == "Approximate — tax map"
    assert isinstance(context.zoning, ZoningLayer)
    assert isinstance(context.buildings, BuildingLayer)


def test_subject_ring_is_the_packs_own_lot_ring() -> None:
    lot = replay_lot_geometry()
    document = build_map_context(lot, replay_nyzd_page(), replay_footprints_lot_polygon(),
                                 window_ft=WINDOW_FT, notes=_notes(replay_nyzd_page(),
                                 replay_footprints_lot_polygon()))
    raw_ring = lot.features[0]["geometry"]["rings"][0]
    outline = document["map_context"]["subject_lot"]["outline"]
    assert outline == [[[float(x), float(y)] for x, y in raw_ring]]
    assert len(raw_ring) == 6  # the pack's 6 vertices (5 distinct + closure)
    assert document["map_context"]["subject_lot"]["bbl"] == lot.requested_bbl


def test_exactly_one_zoning_entry_object_3201_r6b() -> None:
    nyzd = replay_nyzd_page()
    document = build_map_context(replay_lot_geometry(), nyzd, replay_footprints_lot_polygon(),
                                 window_ft=WINDOW_FT, notes=_notes(nyzd, nyzd))
    entries = document["map_context"]["zoning_districts"]["entries"]
    assert len(entries) == 1
    assert entries[0]["zonedist"] == "R6B"
    # the one drawn district is the parse split of recorded feature OBJECTID 3201
    feature = _feature_by_object_id(nyzd, NYZD_LOCAL_OBJECT_ID)
    assert feature["attributes"]["ZONEDIST"] == "R6B"
    _status, _f, parts, _flags = parse_footprint_geometry(feature["geometry"])
    assert entries[0]["outline"] == _as_float_rings([parts[0].exterior, *parts[0].holes])


def test_two_footprints_with_recorded_bins() -> None:
    footprints = replay_footprints_lot_polygon()
    document = build_map_context(replay_lot_geometry(), replay_nyzd_page(), footprints,
                                 window_ft=WINDOW_FT, notes=_notes(footprints, footprints))
    entries = document["map_context"]["building_footprints"]["entries"]
    expected_bins = {str(b.bin) for b in footprints.buildings}
    assert len(entries) == len(footprints.buildings) == 2
    assert {entry["bin"] for entry in entries} == expected_bins


def test_zoning_coverage_note_rides_on_the_attribution() -> None:
    document = _build_northern()
    attribution = document["map_context"]["zoning_districts"]["attribution"]
    assert "attribute query for ZONEDIST 'R6B'" in attribution
    assert "not retrieved" in attribution


# ---------------------------------------------------------------------------
# Provenance: verbatim from the typed result, tied to the recorded MANIFEST.
# ---------------------------------------------------------------------------


def test_zoning_provenance_is_the_manifest_record() -> None:
    nyzd = replay_nyzd_page()
    document = build_map_context(replay_lot_geometry(), nyzd, replay_footprints_lot_polygon(),
                                 window_ft=WINDOW_FT, notes=_notes(nyzd, nyzd))
    provenance = document["map_context"]["zoning_districts"]["provenance"]
    assert provenance["request_url"] == MANIFEST[NYZD_PAGE_FILE]["url"] == nyzd.request_url
    assert provenance["retrieved_at"] == nyzd.retrieved_at
    assert provenance["raw_digest_sha256"] == manifest_digest(NYZD_PAGE_FILE) == nyzd.raw_digest
    assert provenance["source_id"] == "nyc-dcp-zoning-features-arcgis"
    assert provenance["dataset_id"] == "nyzd"
    assert provenance["source_data_last_edited"] == nyzd.source_data_last_edited[:10]
    assert provenance["dataset_version"] == str(nyzd.source_data_last_edited_ms)


def test_footprint_provenance_is_the_manifest_record() -> None:
    footprints = replay_footprints_lot_polygon()
    document = build_map_context(replay_lot_geometry(), replay_nyzd_page(), footprints,
                                 window_ft=WINDOW_FT, notes=_notes(footprints, footprints))
    provenance = document["map_context"]["building_footprints"]["provenance"]
    assert provenance["request_url"] == MANIFEST[FOOTPRINTS_PAGE_FILE]["url"]
    assert provenance["request_url"] == footprints.request_urls[0]
    assert provenance["retrieved_at"] == footprints.retrieved_at
    assert provenance["raw_digest_sha256"] == manifest_digest(FOOTPRINTS_PAGE_FILE)
    assert provenance["source_id"] == "nyc-oti-building-footprints-arcgis"
    assert provenance["dataset_id"] == "5zhs-2jue"
    assert provenance["dataset_version"] == str(footprints.source_data_last_edited_ms)


# ---------------------------------------------------------------------------
# Degradation: unavailable / mismatched / refused inputs never invent a map.
# ---------------------------------------------------------------------------


def test_none_layers_degrade_to_not_available() -> None:
    document = build_map_context(replay_lot_geometry(), None, None, window_ft=WINDOW_FT,
                                 notes=_notes(replay_nyzd_page(), replay_footprints_lot_polygon()))
    context = load_map_context(document)
    assert isinstance(context.zoning, LayerUnavailable)
    assert isinstance(context.buildings, LayerUnavailable)
    assert document["map_context"]["zoning_districts"]["reason_kind"] == "source_unavailable"


def test_non_2263_zoning_layer_is_not_available_never_reprojected() -> None:
    nyzd = replay_nyzd_page()
    nyzd.crs = {"wkid": 102718, "latest_wkid": 4326}  # a display CRS, not the measurement CRS
    document = build_map_context(replay_lot_geometry(), nyzd, replay_footprints_lot_polygon(),
                                 window_ft=WINDOW_FT, notes=_notes(nyzd, nyzd))
    zoning = document["map_context"]["zoning_districts"]
    assert zoning["status"] == "not_available"
    assert "EPSG:2263" in zoning["reason"]
    assert isinstance(load_map_context(document).zoning, LayerUnavailable)


def test_broken_layer_ring_demotes_with_the_adapters_message() -> None:
    footprints = replay_footprints_lot_polygon()
    footprints.buildings = [footprints.buildings[0]]
    # A deliberately broken (unclosed) ring parse never produced: it reaches the
    # adapter, which refuses it; the layer must carry the adapter's own message.
    footprints.buildings[0].parts = [
        FootprintPart(exterior=[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0]], holes=[], area_sq_ft=0.0)
    ]
    document = build_map_context(replay_lot_geometry(), replay_nyzd_page(), footprints,
                                 window_ft=WINDOW_FT, notes=_notes(footprints, footprints))
    buildings = document["map_context"]["building_footprints"]
    assert buildings["status"] == "not_available"
    assert buildings["reason"].startswith("ring_not_closed")  # the adapter's MapInputError code
    assert isinstance(load_map_context(document).buildings, LayerUnavailable)


def test_refused_subject_outline_raises() -> None:
    lot = replay_lot_geometry()
    lot.review_required = True  # MapPLUTO flags the lot for review -> no usable outline
    with pytest.raises(MapContextUnavailable):
        build_map_context(lot, replay_nyzd_page(), replay_footprints_lot_polygon(),
                          window_ft=WINDOW_FT,
                          notes=_notes(replay_nyzd_page(), replay_footprints_lot_polygon()))


# ---------------------------------------------------------------------------
# No fabricated geometry: every drawn ring is an input ring (or a parse split).
# ---------------------------------------------------------------------------


def test_no_geometry_is_fabricated() -> None:
    lot = replay_lot_geometry()
    nyzd = replay_nyzd_page()
    footprints = replay_footprints_lot_polygon()
    document = build_map_context(lot, nyzd, footprints, window_ft=WINDOW_FT,
                                 notes=_notes(nyzd, footprints))
    context = document["map_context"]
    # Subject ring is the verbatim MapPLUTO ring.
    assert context["subject_lot"]["outline"] == [
        [[float(x), float(y)] for x, y in lot.features[0]["geometry"]["rings"][0]]
    ]
    # Each zoning outline is a parse_footprint_geometry split of recorded OBJECTID 3201.
    feature = _feature_by_object_id(nyzd, NYZD_LOCAL_OBJECT_ID)
    _s, _f, zoning_parts, _fl = parse_footprint_geometry(feature["geometry"])
    expected_zoning = [_as_float_rings([p.exterior, *p.holes]) for p in zoning_parts]
    assert [e["outline"] for e in context["zoning_districts"]["entries"]] == expected_zoning
    # Each footprint outline is a verbatim ContextBuilding.parts ring.
    expected_footprints = [
        _as_float_rings([part.exterior, *part.holes])
        for building in footprints.buildings
        for part in building.parts
    ]
    assert [e["outline"] for e in context["building_footprints"]["entries"]] == expected_footprints
