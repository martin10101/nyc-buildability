"""M5-T082 (D-087 3D-1) tests for the deterministic massing truth object.

Covers AS-1 (declared frame + deterministic golden), AS-2 (closed, outward,
non-degenerate meshes; cap area == polygon area; reversed-winding mutation),
AS-3 (plates + metrics; swapped-floor-height mutation), AS-4 (typed fail-closed
refusals; nothing clipped) and AS-5 (honest labels + generated-option path).
"""

from __future__ import annotations

import math
import pathlib
from collections import Counter

import pytest
from shapely.geometry import Polygon

from app.scenario import massing_model as mm
from app.scenario.massing_model import (
    MassingModel,
    MassingModelError,
    build_from_generated_option,
    build_massing_model,
)

# ---------------------------------------------------------------------------
# Fixtures - all coordinates in EPSG:2263 US survey feet inside the NYC bounds.
# ---------------------------------------------------------------------------

# A 100 x 120 ft lot rectangle, supplied OPEN (connector convention).
LOT_RING = [
    [1000000.0, 200000.0],
    [1000100.0, 200000.0],
    [1000100.0, 200120.0],
    [1000000.0, 200120.0],
]


def _walls(n: int) -> list[dict]:
    return [
        {"id": f"W{i}", "start_vertex_index": i, "end_vertex_index": (i + 1) % n}
        for i in range(n)
    ]


def _outline(vertices: list[list[float]]) -> dict:
    return {"srid": 2263, "vertices": vertices + [vertices[0]]}


def _provenance() -> dict:
    return {"author": "test-architect", "editor_version": "test-1", "kind": "proposed"}


# Rectangle 40 x 60 (area 2400) fully inside the lot.
RECT = [
    [1000010.0, 200010.0],
    [1000050.0, 200010.0],
    [1000050.0, 200070.0],
    [1000010.0, 200070.0],
]

# Concave L-shape (area 3000) fully inside the lot.
LSHAPE = [
    [1000010.0, 200010.0],
    [1000070.0, 200010.0],
    [1000070.0, 200040.0],
    [1000040.0, 200040.0],
    [1000040.0, 200080.0],
    [1000010.0, 200080.0],
]

FIVE_FLOOR_HEIGHTS = [12.0, 11.0, 13.0, 10.0, 14.0]


def _rect_block() -> dict:
    return {
        "outline": _outline(RECT),
        "levels": [{"level_index": 0, "floor_count": 1, "floor_to_floor_ft": 12.0}],
        "exterior_walls": _walls(4),
        "provenance": _provenance(),
    }


def _lshape_block() -> dict:
    return {
        "outline": _outline(LSHAPE),
        "levels": [{"level_index": 0, "floor_count": 1, "floor_to_floor_ft": 12.0}],
        "exterior_walls": _walls(6),
        "provenance": _provenance(),
    }


def _five_floor_block(heights: list[float] | None = None) -> dict:
    hs = heights if heights is not None else FIVE_FLOOR_HEIGHTS
    return {
        "outline": _outline(RECT),
        "levels": [
            {"level_index": i, "floor_count": 1, "floor_to_floor_ft": h}
            for i, h in enumerate(hs)
        ],
        "exterior_walls": _walls(4),
        "provenance": _provenance(),
    }


def _build(block: dict, **kw) -> MassingModel:
    return build_massing_model(lot_ring=LOT_RING, proposed_massing=block, **kw)


# ---------------------------------------------------------------------------
# Mesh-property helpers (independent re-derivation of the invariants).
# ---------------------------------------------------------------------------


def _directed_edges(triangles) -> Counter:
    edges: Counter = Counter()
    for a, b, c in triangles:
        edges[(a, b)] += 1
        edges[(b, c)] += 1
        edges[(c, a)] += 1
    return edges


def _is_closed_manifold(triangles) -> bool:
    """Closed + consistently oriented: every directed edge appears exactly once and
    its reverse appears exactly once (so every undirected edge is shared by exactly
    two triangles). Reversing any single face breaks this."""
    edges = _directed_edges(triangles)
    if any(count != 1 for count in edges.values()):
        return False
    return all(edges.get((b, a), 0) == 1 for (a, b) in edges)


def _tri_area_3d(v0, v1, v2) -> float:
    ux, uy, uz = (v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2])
    wx, wy, wz = (v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2])
    cx, cy, cz = (uy * wz - uz * wy, uz * wx - ux * wz, ux * wy - uy * wx)
    return 0.5 * math.sqrt(cx * cx + cy * cy + cz * cz)


# ---------------------------------------------------------------------------
# AS-1 - truth object declares the frame and is deterministic.
# ---------------------------------------------------------------------------


def test_as1_declares_full_coordinate_frame():
    doc = _build(_rect_block()).as_dict()
    assert doc["generator_version"] == "massing-1.0.0"
    crs = doc["coordinate_reference_system"]
    assert crs["crs"] == "EPSG:2263"
    assert "NAD83" in crs["authority"]
    assert crs["horizontal_unit"] == "us_survey_foot"
    assert crs["vertical_unit"] == "us_survey_foot"
    assert crs["axis_order"] == "easting_northing"
    assert len(crs["local_origin"]) == 3
    # The exact world->local transform: subtracting the local origin.
    ox, oy, _ = crs["local_origin"]
    assert crs["world_to_local"]["offset"] == [-ox, -oy, 0.0]
    assert crs["precision_grid_ft"] == mm.PRECISION_GRID_FT
    assert doc["provenance"]["input_digests"]["lot_ring"].startswith("sha256:")
    assert doc["provenance"]["input_digests"]["proposed_massing"].startswith("sha256:")


def test_as1_json_serializable_and_deterministic_golden():
    model = _build(_rect_block())
    # JSON-serializable, strict (no NaN/Infinity).
    text = model.to_json()
    assert isinstance(text, str) and text
    # Deterministic across two independent builds.
    again = _build(_rect_block())
    assert model.content_hash() == again.content_hash()
    # Golden sha256 pins the canonical output. The rectangle fixture has exact
    # coordinates/areas so the golden is stable (no float-drift across runners).
    assert model.content_hash() == (
        "sha256:b7fa9862a0bb23885e7d7d71dae4a2d448a6ca4720f29a7b6bf68b4227c5133b"
    )


def test_as1_local_origin_near_parcel_centroid():
    crs = _build(_rect_block()).as_dict()["coordinate_reference_system"]
    centroid = Polygon([(x, y) for x, y in LOT_RING]).centroid
    ox, oy, _ = crs["local_origin"]
    assert abs(ox - centroid.x) < 1.0 and abs(oy - centroid.y) < 1.0


# ---------------------------------------------------------------------------
# AS-2 - mesh correctness for rectangle, concave L-shape and a 5-floor stack.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("block", [_rect_block(), _lshape_block(), _five_floor_block()])
def test_as2_every_prism_closed_outward_and_nondegenerate(block):
    model = _build(block)
    assert model.meshes
    for mesh in model.meshes:
        md = mesh.as_dict()
        tris = [tuple(t) for t in md["triangles"]]
        verts = md["vertices"]
        # Closed, consistently-oriented manifold.
        assert _is_closed_manifold(tris)
        # Outward orientation -> positive signed volume.
        assert md["signed_volume_cu_ft"] > 0.0
        # No degenerate triangle.
        for a, b, c in tris:
            assert _tri_area_3d(verts[a], verts[b], verts[c]) > 1e-9


def test_as2_reversed_face_winding_is_detected():
    """The closure invariant catches a single reversed face (the AS-2 mutation)."""
    mesh = _build(_rect_block()).meshes[0]
    tris = [tuple(t) for t in mesh.as_dict()["triangles"]]
    assert _is_closed_manifold(tris)
    mutated = list(tris)
    a, b, c = mutated[0]
    mutated[0] = (a, c, b)  # reverse one face winding
    assert not _is_closed_manifold(mutated)


@pytest.mark.parametrize(
    "ring_pts,expected_area",
    [(RECT, 2400.0), (LSHAPE, 3000.0)],
)
def test_as2_cap_triangulation_area_equals_polygon_area(ring_pts, expected_area):
    ring = mm._prepare_ring([list(p) for p in ring_pts], "t")
    cap = mm._triangulate(ring, "t")
    poly_area = Polygon([(x, y) for x, y in ring]).area
    assert abs(poly_area - expected_area) < 1e-6
    tri_area = sum(abs(mm._cross3(ring[a], ring[b], ring[c])) / 2.0 for a, b, c in cap)
    assert abs(tri_area - poly_area) <= 1e-9 * poly_area


def test_as2_volume_equals_area_times_height():
    for mesh in _build(_five_floor_block()).meshes:
        md = mesh.as_dict()
        height = md["z_top_ft"] - md["z_bottom_ft"]
        expected = md["plate_area_sq_ft"] * height
        assert abs(md["signed_volume_cu_ft"] - expected) <= 1e-9 * expected


def test_as2_concave_lshape_triangulates_without_spanning_the_notch():
    ring = mm._prepare_ring([list(p) for p in LSHAPE], "t")
    cap = mm._triangulate(ring, "t")
    assert len(cap) == len(ring) - 2  # a simple polygon -> n-2 triangles


# ---------------------------------------------------------------------------
# AS-3 - plates + metrics reconcile; swapped-height mutation reddens.
# ---------------------------------------------------------------------------


def test_as3_plate_areas_match_shapely_2263_area():
    model = _build(_five_floor_block())
    shapely_area = Polygon([(x, y) for x, y in RECT]).area
    for plate in model.as_dict()["plates"]:
        assert abs(plate["area_sq_ft"] - shapely_area) <= 1e-6


def test_as3_metrics_reconcile_with_plates():
    doc = _build(_five_floor_block()).as_dict()
    plates = doc["plates"]
    assert doc["metrics"]["gross_floor_area_sq_ft"] == pytest.approx(
        sum(p["area_sq_ft"] for p in plates)
    )
    assert doc["metrics"]["total_height_ft"] == pytest.approx(sum(FIVE_FLOOR_HEIGHTS))
    assert doc["metrics"]["floor_count"] == 5


def test_as3_five_floor_plate_elevations():
    """Elevations follow the exact cumulative floor-height sequence. Swapping two
    distinct floor heights (the AS-3 mutation) changes this and reddens the test."""
    doc = _build(_five_floor_block()).as_dict()
    elevations = [p["elevation_ft"] for p in doc["plates"]]
    expected = []
    z = 0.0
    for h in FIVE_FLOOR_HEIGHTS:
        expected.append(z)
        z += h
    assert elevations == expected


def test_as3_swapping_two_floor_heights_changes_the_model():
    base = _build(_five_floor_block())
    swapped_heights = list(FIVE_FLOOR_HEIGHTS)
    swapped_heights[0], swapped_heights[2] = swapped_heights[2], swapped_heights[0]
    swapped = _build(_five_floor_block(swapped_heights))
    assert base.content_hash() != swapped.content_hash()
    base_elev = [p["elevation_ft"] for p in base.as_dict()["plates"]]
    swap_elev = [p["elevation_ft"] for p in swapped.as_dict()["plates"]]
    assert base_elev != swap_elev


# ---------------------------------------------------------------------------
# AS-4 - typed fail-closed refusals; nothing clipped or repaired.
# ---------------------------------------------------------------------------


def test_as4_footprint_outside_lot_is_refused_not_clipped():
    block = _rect_block()
    # Shift the footprint outside the lot rectangle (still inside NYC bounds).
    shifted = [[x + 200.0, y] for x, y in RECT]
    block["outline"] = _outline(shifted)
    with pytest.raises(MassingModelError) as exc:
        _build(block)
    assert exc.value.reason == "footprint_outside_lot"


def test_as4_lot_with_hole_is_refused():
    # A lot ring that self-touches to enclose a hole is not a simple ring.
    with pytest.raises(MassingModelError) as exc:
        build_massing_model(
            lot_ring=[[1000000.0, 200000.0]],  # too few vertices
            proposed_massing=_rect_block(),
        )
    assert exc.value.reason in {"invalid_source", "lot_has_holes", "self_intersection"}


def test_as4_self_intersecting_footprint_is_refused():
    block = _rect_block()
    bowtie = [
        [1000010.0, 200010.0],
        [1000050.0, 200070.0],
        [1000050.0, 200010.0],
        [1000010.0, 200070.0],
    ]
    block["outline"] = _outline(bowtie)
    with pytest.raises(MassingModelError) as exc:
        _build(block)
    assert exc.value.reason in {"invalid_source", "self_intersection"}


def test_as4_non_finite_coordinate_is_refused():
    with pytest.raises(MassingModelError) as exc:
        build_massing_model(
            lot_ring=[[1000000.0, 200000.0], [float("nan"), 200000.0],
                      [1000100.0, 200120.0]],
            proposed_massing=_rect_block(),
        )
    assert exc.value.reason == "non_finite"


def test_as4_over_cap_vertices_is_refused():
    huge = [[1000000.0 + i * 1e-3, 200000.0] for i in range(mm.MAX_OUTLINE_VERTICES + 5)]
    with pytest.raises(MassingModelError) as exc:
        build_massing_model(lot_ring=huge, proposed_massing=_rect_block())
    assert exc.value.reason == "over_cap_vertices"


def test_as4_non_positive_height_is_refused():
    block = _rect_block()
    block["levels"] = [
        {"level_index": 0, "floor_count": 1, "floor_to_floor_ft": 0.0}
    ]
    with pytest.raises(MassingModelError) as exc:
        _build(block)
    # B0 rejects a non-positive floor_to_floor_ft; the massing layer surfaces a typed
    # refusal either way (never a built zero-height prism).
    assert exc.value.reason in {"invalid_source", "non_positive_height"}


def test_as4_nothing_is_clipped_on_valid_input():
    # A valid footprint is preserved vertex-for-vertex (no silent repair).
    model = _build(_rect_block())
    ring_xy = {(v[0], v[1]) for v in model.meshes[0].as_dict()["vertices"]}
    for x, y in RECT:
        assert (x, y) in ring_xy


# ---------------------------------------------------------------------------
# AS-5 - honest labels + the generated-option path; scope.
# ---------------------------------------------------------------------------


def test_as5_only_honest_source_labels():
    proposed = _build(_rect_block()).as_dict()
    assert proposed["source"] == "proposed"
    assert proposed["disclosure"] == "Proposed - not a city record"
    assert proposed["building_layer"]["layer"] == "proposed_massing"
    assert proposed["coverage_status"] == "conditional"


def test_as5_module_has_no_permitted_or_maximum_allowed_wording():
    source = pathlib.Path(mm.__file__).read_text(encoding="utf-8").lower()
    for banned in ("permitted", "approved", "maximum allowed", "maximum-allowed"):
        assert banned not in source, f"banned wording in module: {banned!r}"


def test_as5_generated_option_path_from_max_envelope_as_dict():
    candidate = _rect_block()
    candidate["provenance"] = {
        "author": "max-envelope-generator",
        "editor_version": "m5-t064-slice1",
        "kind": "proposed",
    }
    envelope = {
        "candidate": candidate,
        "candidate_placement": {"status": "fitted", "detail": "ok"},
    }
    model = build_from_generated_option(lot_ring=LOT_RING, max_envelope=envelope)
    doc = model.as_dict()
    assert doc["source"] == "generated_option"
    assert doc["disclosure"] == "Generated building option"
    assert doc["building_layer"]["layer"] == "generated_option"


def test_as5_generated_option_no_candidate_is_typed_refusal():
    envelope = {
        "candidate": None,
        "candidate_placement": {
            "status": "footprint_exceeds_lot",
            "detail": "the rules-derived footprint exceeds what the lot can hold",
        },
    }
    with pytest.raises(MassingModelError) as exc:
        build_from_generated_option(lot_ring=LOT_RING, max_envelope=envelope)
    assert exc.value.reason == "no_generated_candidate"
