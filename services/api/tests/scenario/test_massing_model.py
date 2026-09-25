"""M5-T082 (D-087 3D-1) tests for the deterministic massing truth object.

Covers AS-1 (declared frame + deterministic golden), AS-2 (closed, outward,
non-degenerate meshes; cap area == polygon area; reversed-winding mutation),
AS-3 (plates + metrics; swapped-floor-height mutation), AS-4 (typed fail-closed
refusals; nothing clipped) and AS-5 (honest labels + generated-option path).

M5-T088 (DB-054 a-j) hardening, the ``test_t088_*`` tests plus the U / comb
parametrizations: a non-star concave fixture that a naive fan cannot pass,
clockwise and collinear rings, the containment tolerance boundary, the coordinate
magnitude / floor / output-vertex / triangulation-work bounds (each refused before
the heavy work it guards), non-integer volume conditioning, a five-floor golden.
"""

from __future__ import annotations

import math
import pathlib
from collections import Counter
from fractions import Fraction

import numpy as np
import pytest
from shapely.geometry import Polygon

from app.scenario import massing_model as mm
from app.scenario import massing_triangulation as mt
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

# Non-star-shaped concave U (area 80*90 - 40*60 = 4800): the notch walls x=..030
# (interior to their left, x < 30) and x=..070 (x > 70) leave an empty kernel, so a
# fan from ANY vertex over-covers it. The L-shape above is star-shaped (DB-054 a).
USHAPE = [
    [1000010.0, 200010.0],
    [1000090.0, 200010.0],
    [1000090.0, 200100.0],
    [1000070.0, 200100.0],
    [1000070.0, 200040.0],
    [1000030.0, 200040.0],
    [1000030.0, 200100.0],
    [1000010.0, 200100.0],
]

# Non-star-shaped three-tooth comb (area 80*20 + 70*(15+16+15) = 4820).
COMB = [
    [1000010.0, 200010.0],
    [1000090.0, 200010.0],
    [1000090.0, 200100.0],
    [1000075.0, 200100.0],
    [1000075.0, 200030.0],
    [1000058.0, 200030.0],
    [1000058.0, 200100.0],
    [1000042.0, 200100.0],
    [1000042.0, 200030.0],
    [1000025.0, 200030.0],
    [1000025.0, 200100.0],
    [1000010.0, 200100.0],
]

# Non-integer 2263 coordinates (DB-054 e): a concave footprint inside a lot whose
# centroid (the local origin) is itself non-integer, so world != local arithmetic.
NONINT_LOT = [
    [999999.5, 199999.25],
    [1000100.75, 199999.25],
    [1000100.75, 200120.125],
    [999999.5, 200120.125],
]
NONINT = [
    [1000012.345678, 200013.579135],
    [1000071.234567, 200011.111111],
    [1000068.987654, 200047.654321],
    [1000041.414213, 200049.999999],
    [1000039.271828, 200088.161803],
    [1000014.142135, 200086.60254],
]

FIVE_FLOOR_HEIGHTS = [12.0, 11.0, 13.0, 10.0, 14.0]


def _regular(n: int, radius: float = 40.0) -> list[list[float]]:
    """A CCW regular n-gon centred in the lot (convex, B0-valid)."""
    cx, cy = 1000050.0, 200060.0
    return [
        [round(cx + radius * math.cos(2 * math.pi * k / n), 6),
         round(cy + radius * math.sin(2 * math.pi * k / n), 6)]
        for k in range(n)
    ]


def _spiral(turns: int, per_turn: int) -> list[list[float]]:
    """A thin CCW spiral strip (simple, B0-valid): the ear-clipping worst-case
    family - most convex candidates are not ears, so the scan does far more than
    its least work."""
    cx, cy = 1000050.0, 200060.0
    outer, inner = [], []
    for k in range(turns * per_turn + 1):
        th = 2 * math.pi * k / per_turn
        r_in = 2.0 + 3.0 * th / (2 * math.pi)
        outer.append([round(cx + (r_in + 1.0) * math.cos(th), 6),
                      round(cy + (r_in + 1.0) * math.sin(th), 6)])
        inner.append([round(cx + r_in * math.cos(th), 6),
                      round(cy + r_in * math.sin(th), 6)])
    return outer + inner[::-1]


def _block(vertices: list[list[float]], levels: list[dict] | None = None) -> dict:
    return {
        "outline": _outline(vertices),
        "levels": levels if levels is not None else [
            {"level_index": 0, "floor_count": 1, "floor_to_floor_ft": 12.0}],
        "exterior_walls": _walls(len(vertices)),
        "provenance": _provenance(),
    }


def _stack(level_count: int, floor_count: int, height: float = 10.0) -> list[dict]:
    return [
        {"level_index": i, "floor_count": floor_count, "floor_to_floor_ft": height}
        for i in range(level_count)
    ]


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


def _tri_signed_area_2d(a, b, c) -> float:
    """Independent of the module: > 0 when ``a b c`` winds CCW."""
    return ((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])) / 2.0


def _shoelace(ring) -> float:
    """Signed area of an open ring (> 0 CCW), independent of the module."""
    n = len(ring)
    return sum(
        ring[i][0] * ring[(i + 1) % n][1] - ring[(i + 1) % n][0] * ring[i][1]
        for i in range(n)
    ) / 2.0


def _exact_area(ring) -> Fraction:
    """Exact rational shoelace area of float vertices (no rounding at all)."""
    pts = [(Fraction(x), Fraction(y)) for x, y in ring]
    n = len(pts)
    twice = sum(
        pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1]
        for i in range(n)
    )
    return twice / 2


def _cap_faces_face_outward(md: dict) -> bool:
    """Every top-cap face normal points +z and every bottom-cap face -z (a naive fan
    on a non-star ring leaves a CW cap triangle whose normal flips)."""
    verts = md["vertices"]
    for a, b, c in md["triangles"]:
        zs = {verts[a][2], verts[b][2], verts[c][2]}
        if len(zs) != 1:
            continue  # a side-wall face
        signed = _tri_signed_area_2d(verts[a], verts[b], verts[c])
        z = zs.pop()
        if z == md["z_top_ft"] and not signed > 0:
            return False
        if z == md["z_bottom_ft"] and not signed < 0:
            return False
    return True


@pytest.fixture
def heavy_work(monkeypatch):
    """Counts triangulations and prism builds reached through the builder, to prove a
    bound refuses BEFORE the heavy work it guards (the builder resolves both names
    from the module namespace at call time)."""
    calls: Counter = Counter()
    real_triangulate, real_prism = mm._triangulate, mm._build_prism

    def triangulate(*args, **kwargs):
        calls["triangulate"] += 1
        return real_triangulate(*args, **kwargs)

    def prism(*args, **kwargs):
        calls["prism"] += 1
        return real_prism(*args, **kwargs)

    monkeypatch.setattr(mm, "_triangulate", triangulate)
    monkeypatch.setattr(mm, "_build_prism", prism)
    return calls


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


@pytest.mark.parametrize(
    "block",
    [_rect_block(), _lshape_block(), _five_floor_block(), _block(USHAPE), _block(COMB)],
    ids=["rect", "lshape", "five_floor", "ushape", "comb"],
)
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
        # Every cap face individually outward (M5-T088: concave-specific).
        assert _cap_faces_face_outward(md)
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
    [(RECT, 2400.0), (LSHAPE, 3000.0), (USHAPE, 4800.0), (COMB, 4820.0)],
    ids=["rect", "lshape", "ushape", "comb"],
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


@pytest.mark.parametrize(
    "ring_pts", [LSHAPE, USHAPE, COMB], ids=["lshape", "ushape", "comb"]
)
def test_as2_concave_ring_triangulates_without_spanning_the_notch(ring_pts):
    ring = mm._prepare_ring([list(p) for p in ring_pts], "t")
    cap = mm._triangulate(ring, "t")
    assert len(cap) == len(ring) - 2  # a simple polygon -> n-2 triangles
    poly = Polygon(ring)
    for a, b, c in cap:
        # Each triangle CCW and inside the ring (a fan on U / comb breaks both).
        assert _tri_signed_area_2d(ring[a], ring[b], ring[c]) > 0.0
        assert poly.covers(Polygon([ring[a], ring[b], ring[c]]))


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


def test_as4_lot_ring_with_too_few_vertices_is_refused():
    # M5-T088 (DB-054 f): renamed from the misnamed "lot_with_hole" test - a
    # one-vertex ring is a degenerate lot, refused invalid_source (pinned exactly).
    with pytest.raises(MassingModelError) as exc:
        build_massing_model(
            lot_ring=[[1000000.0, 200000.0]],  # too few vertices
            proposed_massing=_rect_block(),
        )
    assert exc.value.reason == "invalid_source"


def test_t088_as5_keyhole_lot_ring_pinching_a_hole_is_refused():
    """DB-054 f repaired honestly: one ring cannot carry an interior ring, so a lot
    "with a hole" can only arrive as a keyhole ring that revisits the slit vertices
    - refused self_intersection (the Polygon ``interiors`` branch is unreachable)."""
    base_x, base_y = 1000000.0, 200000.0
    keyhole = [
        (0, 0), (100, 0), (100, 120), (0, 120), (0, 60),  # shell, down to the slit
        (40, 60), (40, 80), (60, 80), (60, 40), (40, 40),  # the hole, clockwise
        (40, 60), (0, 60),  # back out along the slit (revisited vertices)
    ]
    ring = [[base_x + x, base_y + y] for x, y in keyhole]
    with pytest.raises(MassingModelError) as exc:
        build_massing_model(lot_ring=ring, proposed_massing=_rect_block())
    assert exc.value.reason == "self_intersection"
    assert exc.value.field == "lot_ring"


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


# ---------------------------------------------------------------------------
# M5-T088 AS-1 - the non-star concave fixtures really discriminate a naive fan.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("ring_pts", [USHAPE, COMB], ids=["ushape", "comb"])
def test_t088_as1_fixture_is_not_star_shaped_so_every_fan_over_covers(ring_pts):
    """Fixture validity: a fan from EVERY start vertex covers more than the ring's
    area, so the U / comb parametrizations redden any naive fan (the star-shaped
    L-shape cannot: a fan from its vertex 0 is exact)."""
    ring = [tuple(p) for p in ring_pts]
    area = Polygon(ring).area
    n = len(ring)
    for start in range(n):
        fan = sum(
            abs(_tri_signed_area_2d(ring[start], ring[(start + i) % n],
                                    ring[(start + i + 1) % n]))
            for i in range(1, n - 1)
        )
        assert fan > area + 1.0, f"a fan from vertex {start} is exact"


# ---------------------------------------------------------------------------
# M5-T088 AS-2 - clockwise rings normalize; an exact collinear vertex collapses.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "cw_lot,cw_footprint",
    [(True, False), (False, True), (True, True)],
    ids=["cw_lot", "cw_footprint", "cw_both"],
)
def test_t088_as2_clockwise_rings_normalize_to_ccw(cw_lot, cw_footprint):
    lot = [list(p) for p in reversed(LOT_RING)] if cw_lot else LOT_RING
    footprint = [list(p) for p in reversed(LSHAPE)] if cw_footprint else LSHAPE
    assert (_shoelace(lot) < 0) is cw_lot  # the fixtures really are clockwise
    assert (_shoelace(footprint) < 0) is cw_footprint
    doc = build_massing_model(lot_ring=lot, proposed_massing=_block(footprint)).as_dict()
    assert _shoelace(doc["parcel"]["ring"]) > 0  # emitted lot ring is CCW
    assert doc["parcel"]["area_sq_ft"] == 12000.0
    md = doc["meshes"][0]
    n = len(md["vertices"]) // 2
    assert _shoelace([v[:2] for v in md["vertices"][:n]]) > 0  # footprint CCW
    assert {tuple(v[:2]) for v in md["vertices"]} == {tuple(p) for p in LSHAPE}
    assert _is_closed_manifold([tuple(t) for t in md["triangles"]])
    assert _cap_faces_face_outward(md)
    assert md["signed_volume_cu_ft"] == pytest.approx(3000.0 * 12.0, rel=1e-12)
    assert md["plate_area_sq_ft"] == 3000.0


def test_t088_as2_exact_collinear_vertex_collapses():
    rect_mid = [RECT[0], [1000030.0, 200010.0], RECT[1], RECT[2], RECT[3]]
    lot_mid = [LOT_RING[0], [1000050.0, 200000.0], *LOT_RING[1:]]
    model = build_massing_model(lot_ring=lot_mid, proposed_massing=_block(rect_mid))
    base = _build(_rect_block())
    assert len(model.meshes[0].vertices) == 8  # the straight vertex is gone
    assert model.meshes[0].as_dict() == base.meshes[0].as_dict()
    assert model.as_dict()["parcel"]["ring"] == base.as_dict()["parcel"]["ring"]


def test_t088_as2_near_collinear_vertex_is_kept_not_repaired():
    """The collapse is EXACT-only: a vertex 0.001 ft off the edge is a real corner,
    kept, and the mesh stays valid (no tolerance-based repair)."""
    dent = [RECT[0], [1000030.0, 200010.001], RECT[1], RECT[2], RECT[3]]
    md = _build(_block(dent)).meshes[0].as_dict()
    assert len(md["vertices"]) == 10
    assert _is_closed_manifold([tuple(t) for t in md["triangles"]])
    assert _cap_faces_face_outward(md)
    verts = md["vertices"]
    for a, b, c in md["triangles"]:
        assert _tri_area_3d(verts[a], verts[b], verts[c]) > 1e-9


# ---------------------------------------------------------------------------
# M5-T088 AS-3 - the containment tolerance boundary is pinned.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("overhang_ft", [0.5, 0.001], ids=["half_foot", "thousandth"])
def test_t088_as3_footprint_just_outside_the_lot_is_refused(overhang_ft):
    east = 1000100.0 + overhang_ft  # the lot's east line is x = 1000100
    over = [[1000060.0, 200010.0], [east, 200010.0], [east, 200070.0],
            [1000060.0, 200070.0]]
    with pytest.raises(MassingModelError) as exc:
        _build(_block(over))
    assert exc.value.reason == "footprint_outside_lot"


def test_t088_as3_footprint_on_the_lot_line_is_accepted():
    # Zero-lot-line corner footprint: two edges lie ON the lot lines.
    corner = [[1000000.0, 200000.0], [1000040.0, 200000.0], [1000040.0, 200060.0],
              [1000000.0, 200060.0]]
    assert _build(_block(corner)).plates[0]["area_sq_ft"] == 2400.0
    # A footprint identical to the lot is within it (not clipped, not refused).
    full = _build(_block([list(p) for p in LOT_RING])).as_dict()
    assert full["plates"][0]["area_sq_ft"] == full["parcel"]["area_sq_ft"] == 12000.0


# ---------------------------------------------------------------------------
# M5-T088 AS-4 - resource bounds, each typed and BEFORE the heavy work.
# ---------------------------------------------------------------------------


def test_t088_as4_near_overflow_lot_ring_is_a_typed_refusal(heavy_work):
    """DB-054 h / G5-F1: a finite ~1e154 lot ring overflows shapely's area and
    centroid, and the accepted M5-T082 module crashed UNTYPED (a GEOSException from
    the empty centroid on this fixture; G5-F1 saw a to_json ValueError). It is now
    a typed refusal before any geometry work."""
    big = 1e154
    lot = [[-big, -big], [big, -big], [big, big], [-big, big]]
    with pytest.raises(MassingModelError) as exc:
        build_massing_model(lot_ring=lot, proposed_massing=_rect_block())
    assert exc.value.reason == "coordinate_out_of_range"
    assert exc.value.field == "lot_ring[0]"
    assert heavy_work == Counter()


def test_t088_as4_coordinate_magnitude_bound_is_inclusive():
    edge = mm.MAX_COORD_ABS
    assert edge == 1e8
    lot = [[-edge, -edge], [edge, -edge], [edge, edge], [-edge, edge]]
    # M5-T098 (DB-061 c): the lot build path now NYC-range-gates the ring, so a ±1e8
    # lot no longer builds (it is a wrong-CRS/out-of-range lot). The magnitude bound
    # is CRS-agnostic and lives in _prepare_ring; its inclusivity (a coordinate exactly
    # AT 1e8 is accepted) is proven THERE directly, preserving this test's coverage.
    at_bound = mm._prepare_ring([[edge, edge], [edge - 1.0, edge], [edge, edge - 1.0]], "f")
    assert len(at_bound) == 3  # exactly 1e8 accepted (inclusive)
    lot[1] = [edge + 0.5, -edge]
    with pytest.raises(MassingModelError) as exc:
        build_massing_model(lot_ring=lot, proposed_massing=_rect_block())
    assert (exc.value.reason, exc.value.field) == ("coordinate_out_of_range", "lot_ring[1]")
    # The same bound guards footprint / per-level rings (B0 bounds them first).
    with pytest.raises(MassingModelError) as exc:
        mm._prepare_ring([[1e9, 0.0], [1e9 + 1.0, 0.0], [1e9, 1.0]], "f")
    assert (exc.value.reason, exc.value.field) == ("coordinate_out_of_range", "f[0]")


def test_t088_as4_floor_cap_refusal_names_floors(heavy_work):
    block = _block(RECT, levels=_stack(level_count=5, floor_count=500))  # 2500 floors
    with pytest.raises(MassingModelError) as exc:
        _build(block)
    assert exc.value.reason == "over_cap_floors"
    assert exc.value.field == "proposed_massing.levels"
    assert "2500 floors" in str(exc.value)
    assert heavy_work == Counter()


def test_t088_as4_floor_cap_boundary(monkeypatch):
    monkeypatch.setattr(mm, "MAX_TOTAL_FLOORS", 5)
    assert _build(_five_floor_block()).metrics["floor_count"] == 5  # at the cap: ok
    monkeypatch.setattr(mm, "MAX_TOTAL_FLOORS", 4)
    with pytest.raises(MassingModelError) as exc:
        _build(_five_floor_block())
    assert exc.value.reason == "over_cap_floors"


def test_t088_as4_output_vertex_ceiling_refuses_before_meshing(heavy_work):
    # 2000 floors (the floor cap) x a 26-gon = 104,000 vertices > 100,000.
    block = _block(_regular(26), levels=_stack(level_count=4, floor_count=500))
    with pytest.raises(MassingModelError) as exc:
        _build(block)
    assert exc.value.reason == "over_cap_output_vertices"
    assert "104000" in str(exc.value)
    assert heavy_work == Counter()


def test_t088_as4_output_vertex_ceiling_boundary(monkeypatch):
    monkeypatch.setattr(mm, "MAX_TOTAL_MESH_VERTICES", 8)  # one rect prism = 8
    assert len(_build(_rect_block()).meshes[0].vertices) == 8
    monkeypatch.setattr(mm, "MAX_TOTAL_MESH_VERTICES", 7)
    with pytest.raises(MassingModelError) as exc:
        _build(_rect_block())
    assert exc.value.reason == "over_cap_output_vertices"


SPIRAL = _spiral(turns=2, per_turn=20)


def test_t088_as4_triangulation_budget_meters_the_ear_scan():
    ring = mm._prepare_ring(SPIRAL, "t")
    least = mm._min_ear_clip_work(len(ring))
    # The default budget triangulates the spiral exactly.
    cap = mm._triangulate(ring, "t")
    assert len(cap) == len(ring) - 2
    tri_area = sum(_tri_signed_area_2d(ring[a], ring[b], ring[c]) for a, b, c in cap)
    assert all(_tri_signed_area_2d(ring[a], ring[b], ring[c]) > 0 for a, b, c in cap)
    assert tri_area == pytest.approx(Polygon(ring).area, rel=1e-9)
    # A budget above the least possible work but below this ring's real cost is
    # refused mid-scan (the worst case never runs to completion).
    with pytest.raises(MassingModelError) as exc:
        mm._triangulate(ring, "t", mm._WorkBudget(2 * least))
    assert (exc.value.reason, exc.value.field) == ("triangulation_budget_exceeded", "t")


def test_t088_as4_triangulation_budget_through_the_builder(monkeypatch, heavy_work):
    block = _block(SPIRAL)
    least = mm._min_ear_clip_work(len(mm._prepare_ring(SPIRAL, "t")))
    # Up front: the least possible work already exceeds the budget -> no scan at all.
    monkeypatch.setattr(mm, "MAX_TRIANGULATION_WORK", least - 1)
    with pytest.raises(MassingModelError) as exc:
        _build(block)
    assert exc.value.reason == "triangulation_budget_exceeded"
    assert heavy_work == Counter()
    # Metered: the scan starts, overspends, and is refused before any prism.
    monkeypatch.setattr(mm, "MAX_TRIANGULATION_WORK", 2 * least)
    with pytest.raises(MassingModelError) as exc:
        _build(block)
    assert exc.value.reason == "triangulation_budget_exceeded"
    assert exc.value.field == "proposed_massing.outline"
    assert heavy_work == Counter({"triangulate": 1})


def test_t088_as4_budget_admits_realistic_outlines(heavy_work):
    # A convex ring's exact cost is its least work (vertex 0 is always an ear);
    # the budget holds four max-size (999 distinct vertex) convex outlines.
    assert 4 * mm._min_ear_clip_work(mm.MAX_OUTLINE_VERTICES - 1) <= mm.MAX_TRIANGULATION_WORK
    assert _build(_block(_regular(200))).metrics["floor_count"] == 1
    # Identical per-level outlines are triangulated ONCE (content dedupe).
    levels = [
        {"level_index": i, "floor_count": 2, "floor_to_floor_ft": 10.0,
         "outline": _outline(LSHAPE)}
        for i in range(3)
    ]
    heavy_work.clear()
    model = _build(_block(RECT, levels=levels))
    assert heavy_work["triangulate"] == 1 and heavy_work["prism"] == 6
    assert all(m.plate_area_sq_ft == 3000.0 for m in model.meshes)


# ---------------------------------------------------------------------------
# M5-T088 AS-5 - non-integer conditioning; multi-floor golden.
# ---------------------------------------------------------------------------


def _world_volume(md: dict) -> float:
    """The un-conditioned reduction (world coordinates, no origin subtraction)."""
    v = np.array(md["vertices"], dtype=np.float64)
    t = np.array(md["triangles"], dtype=np.int64)
    return float(np.sum(np.einsum("ij,ij->i", v[t[:, 0]],
                                  np.cross(v[t[:, 1]], v[t[:, 2]]))) / 6.0)


def test_t088_as5_non_integer_volume_is_reduced_about_the_local_origin():
    levels = [
        {"level_index": 0, "floor_count": 1, "floor_to_floor_ft": 12.345678},
        {"level_index": 1, "floor_count": 90, "floor_to_floor_ft": 13.579246},
    ]
    model = build_massing_model(lot_ring=NONINT_LOT, proposed_massing=_block(NONINT, levels))
    ox, oy, _ = model.as_dict()["coordinate_reference_system"]["local_origin"]
    assert ox != math.floor(ox) and oy != math.floor(oy)  # world != local
    grid = Fraction(1, 10**6)
    world_misses = 0
    for mesh in model.meshes:
        md = mesh.as_dict()
        n = len(md["vertices"]) // 2
        area = _exact_area([(v[0], v[1]) for v in md["vertices"][:n]])
        exact = area * (Fraction(md["z_top_ft"]) - Fraction(md["z_bottom_ft"]))
        assert abs(Fraction(md["signed_volume_cu_ft"]) - exact) <= grid
        assert abs(Fraction(md["plate_area_sq_ft"]) - area) <= grid
        world_misses += abs(Fraction(round(_world_volume(md), 6)) - exact) > grid
    # Fixture validity: the world-coordinate reduction misses the exact volume.
    assert world_misses > 0


def test_t088_as5_five_floor_stack_golden():
    """DB-054 g: a multi-floor golden (the 1-floor RECT golden cannot see floor
    order). Integer coordinates + heights keep every value exact across runners.
    The accepted M5-T082 module emits these same bytes (M5-T088 changed no output)."""
    model = _build(_five_floor_block())
    assert model.content_hash() == _build(_five_floor_block()).content_hash()
    assert model.content_hash() == (
        "sha256:e23b5cbcca6ea7defee4b04c6bac51a94d4c26b5e643e2af923d29d1c248a6c5"
    )


# ---------------------------------------------------------------------------
# M5-T098 (DB-061 a-d) before-wiring hardening. Every test here is ADDED; the
# existing goldens above stay byte-identical.
# ---------------------------------------------------------------------------


# --- AS-1: the coordinate-magnitude bound checks x OR y (mutant MD) ---------


def test_t098_as1_y_only_magnitude_violation_is_refused():
    """DB-061 a / G4 ADVISORY-1 (strong): the magnitude bound checks x OR y. Every
    prior test violated it on X (or on both), so mutant MD - dropping the
    ``or abs(y) > MAX_COORD_ABS`` clause - survived, re-opening the DB-054(h) overflow
    via Y. A small-x / over-bound-y ring must be refused. Tested on _prepare_ring
    directly: the bound is CRS-agnostic and lives there (the lot/footprint build paths
    NYC-range-gate first, at a far tighter bound). With MD this ring parses cleanly and
    NO refusal is raised, so this reddens MD."""
    over = mm.MAX_COORD_ABS + 1.0  # 1e8 + 1, over the magnitude bound, on Y only
    with pytest.raises(MassingModelError) as exc:
        mm._prepare_ring([[0.0, over], [1.0, over], [0.0, over + 1.0]], "f")
    assert exc.value.reason == "coordinate_out_of_range"
    assert exc.value.field == "f[0]"


def test_t098_as1_y_only_magnitude_bound_is_inclusive():
    """The Y bound is inclusive at exactly 1e8 (mirrors the X-side inclusivity), so the
    y-only refusal above is a true > bound, not an off-by-one."""
    edge = mm.MAX_COORD_ABS
    at_bound = mm._prepare_ring([[0.0, edge], [1.0, edge], [0.0, edge - 1.0]], "f")
    assert len(at_bound) == 3  # y == 1e8 exactly is accepted


# --- AS-2: the lot ring gets the NYC EPSG:2263 range check (mutant: no check) -


def test_t098_as2_lot_ring_in_4326_degrees_is_refused_naming_lot_ring():
    """DB-061 c / G3-A2 / G5 F-LOW-2: the LOT ring - a separate argument B0 never sees
    - gets the same NYC EPSG:2263 range check as the proposal footprint. A 4326
    lon/lat lot (degrees) is refused, NAMING lot_ring; it is NOT reached by containment
    and mislabelled ``footprint_outside_lot``. Removing the check lets the tiny 4326
    lot reach containment, where the NYC-feet footprint reports footprint_outside_lot -
    a different reason - so this reddens that mutation."""
    lot_4326 = [[-73.99, 40.70], [-73.98, 40.70], [-73.98, 40.71], [-73.99, 40.71]]
    with pytest.raises(MassingModelError) as exc:
        build_massing_model(lot_ring=lot_4326, proposed_massing=_rect_block())
    assert exc.value.reason == "lot_ring_out_of_nyc_bounds"
    assert exc.value.field == "lot_ring"


def test_t098_as2_lot_ring_in_metres_is_refused_naming_lot_ring():
    """A UTM-metres lot (another common wrong-CRS mistake: x far below the NYC 2263
    easting range, y far above the northing range) is likewise refused by name."""
    lot_utm = [[583000.0, 4507000.0], [583100.0, 4507000.0],
               [583100.0, 4507120.0], [583000.0, 4507120.0]]
    with pytest.raises(MassingModelError) as exc:
        build_massing_model(lot_ring=lot_utm, proposed_massing=_rect_block())
    assert exc.value.reason == "lot_ring_out_of_nyc_bounds"
    assert exc.value.field == "lot_ring"


def test_t098_as2_lot_ring_reuses_the_b0_footprint_bounds():
    """The lot check reuses the SAME NYC_2263_* constants B0 range-checks the footprint
    with (single source of truth) - a lot one foot below the easting minimum is refused,
    exactly on the shared bound."""
    below = mm.NYC_2263_X_MIN - 1.0
    lot = [[below, 200000.0], [below + 100.0, 200000.0],
           [below + 100.0, 200120.0], [below, 200120.0]]
    with pytest.raises(MassingModelError) as exc:
        build_massing_model(lot_ring=lot, proposed_massing=_rect_block())
    assert exc.value.reason == "lot_ring_out_of_nyc_bounds"


def test_t098_as2_in_range_lot_is_unaffected_golden_unchanged():
    """An in-range NYC lot is untouched by the new check: the accepted M5-T082/T088
    golden bytes are unchanged (no behaviour change for valid input)."""
    model = _build(_rect_block())
    assert model.content_hash() == (
        "sha256:b7fa9862a0bb23885e7d7d71dae4a2d448a6ca4720f29a7b6bf68b4227c5133b"
    )


# --- AS-3: shapely GEOSException is wrapped at the module boundary -----------


def test_t098_as3_geos_exception_is_wrapped_as_massing_error(monkeypatch):
    """DB-061 d / G5 F-LOW-3: a shapely/GEOS engine error on a build path surfaces as a
    typed MassingModelError, never an untyped GEOSException. Proven by a SPY that makes
    the module's shapely Polygon construction raise GEOSException - not by hunting for a
    real GEOS crash (input is bounded/validity-checked before shapely today)."""
    from shapely.errors import GEOSException

    calls = {"n": 0}

    def exploding_polygon(*args, **kwargs):
        calls["n"] += 1
        raise GEOSException("simulated GEOS engine failure")

    monkeypatch.setattr(mm, "Polygon", exploding_polygon)
    with pytest.raises(MassingModelError) as exc:
        _build(_rect_block())
    assert exc.value.reason == "geometry_engine_error"
    assert calls["n"] >= 1  # the spied shapely construct really ran and raised


def test_t098_as3_generated_option_path_also_wraps_geos(monkeypatch):
    """The generated-option build path (build_from_generated_option -> build_massing_model)
    is covered by the same boundary wrap."""
    from shapely.errors import GEOSException

    def exploding_polygon(*args, **kwargs):
        raise GEOSException("simulated GEOS engine failure")

    candidate = _rect_block()
    envelope = {"candidate": candidate, "candidate_placement": {"status": "fitted"}}
    monkeypatch.setattr(mm, "Polygon", exploding_polygon)
    with pytest.raises(MassingModelError) as exc:
        build_from_generated_option(lot_ring=LOT_RING, max_envelope=envelope)
    assert exc.value.reason == "geometry_engine_error"


def test_t098_as3_typed_refusal_passes_through_the_geos_wrap_unchanged():
    """The wrap is SELECTIVE: a MassingModelError raised inside the wrapped body is a
    ValueError, not a GEOSException, so it is not swallowed or re-wrapped - its own
    reason survives (here footprint_outside_lot)."""
    block = _rect_block()
    block["outline"] = _outline([[x + 200.0, y] for x, y in RECT])  # outside the lot
    with pytest.raises(MassingModelError) as exc:
        _build(block)
    assert exc.value.reason == "footprint_outside_lot"


# --- AS-4: scan units are charged BEFORE the inner scan (mutant ME) ----------


def test_t098_as4_scan_units_charged_before_the_inner_scan(monkeypatch):
    """DB-061 b / G4 ADVISORY-2: in _triangulate the worst-case ``m-3`` scan units are
    charged BEFORE the inner point-in-triangle scan runs. A budget that overspends
    exactly at that charge refuses WITHOUT running the scan; mutant ME (charge the m-3
    units AFTER the scan) would run the whole scan first. Counting point-in-triangle
    calls discriminates the two: 0 (before) vs m-3 (after)."""
    ring = mm._prepare_ring(_regular(8), "t")
    n = len(ring)
    assert n == 8
    calls = {"n": 0}
    # [ORCH-CORRECTED per M5-T112 G3 B1 / G4 BLOCKING] after the M5-T112 split the inner scan
    # lives in massing_triangulation and resolves _point_in_triangle THERE, so the counter
    # patches that CONSUMING namespace (a facade patch no longer bites).
    real_pit = mt._point_in_triangle

    def counting_pit(*args, **kwargs):
        calls["n"] += 1
        return real_pit(*args, **kwargs)

    monkeypatch.setattr(mt, "_point_in_triangle", counting_pit)
    # units = n-3: the pos-0 candidate charge (1) leaves n-4; the convex candidate's
    # m-3 = n-3 charge then overspends. Charged BEFORE the scan -> zero pit calls.
    with pytest.raises(MassingModelError) as exc:
        mm._triangulate(ring, "t", mm._WorkBudget(n - 3))
    assert exc.value.reason == "triangulation_budget_exceeded"
    assert exc.value.field == "t"
    assert calls["n"] == 0  # the inner scan never ran (mutant ME makes this n-3 > 0)
    # Positive control: with ample budget the same patched scan DOES run, so the zero above
    # is a real observation and this guard cannot go vacuous silently again.
    mm._triangulate(ring, "t", mm._WorkBudget(mm.MAX_TRIANGULATION_WORK))
    assert calls["n"] > 0


# --- AS-5: scope / no new dependency / unwired ------------------------------


def test_t098_as5_module_imports_no_route_or_web_and_no_new_dependency():
    """Scope: the module stays a pure builder - no FastAPI/route/app/web import, and no
    third-party dependency beyond the already-admitted numpy + shapely."""
    source = pathlib.Path(mm.__file__).read_text(encoding="utf-8")
    for forbidden in ("fastapi", "app.main", "app.api", "starlette", "requests",
                      "httpx", "app.cad"):
        assert forbidden not in source, f"unexpected wiring/import: {forbidden!r}"
    # The only imports are stdlib + numpy + shapely + the read-only B0 proposal contract.
    import ast

    tree = ast.parse(source)
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".")[0])
    assert roots <= {"functools", "hashlib", "json", "math", "collections", "dataclasses",
                     "typing", "numpy", "shapely", "__future__"}


# ---------------------------------------------------------------------------
# M5-T106 (DB-069 a-d + DB-061 b) before-wiring hardening, ahead of the PKT-E
# scene seam. Every test here is ADDED; the goldens above stay byte-identical.
# ---------------------------------------------------------------------------


# --- AS-1: the LOT NYC range check runs on RAW vertices, before the collapse ---


def test_t106_as1_out_of_range_collinear_spike_in_lot_is_refused():
    """DB-069 a / M5-T098 G3 ADVISORY-1: the lot NYC range check must run on the RAW
    vertices, BEFORE the collinear collapse. A spike vertex at x=2e6 (out of the NYC
    X-range, under the 1e8 magnitude bound) lies ON the straight bottom edge, so the
    collinear collapse WOULD remove it - and the old post-collapse check never saw it.
    The raw-vertex check refuses it, naming lot_ring.

    Mutation (checking the COLLAPSED ring instead of the raw vertices): the spike is
    collapsed away, the remaining ring is the clean in-range rectangle, no refusal is
    raised and the model builds - so this test reddens that mutant."""
    lot = [
        [1000000.0, 200000.0],
        [2000000.0, 200000.0],   # collinear spike on y=200000; x=2e6 is out of NYC range
        [1000100.0, 200000.0],
        [1000100.0, 200120.0],
        [1000000.0, 200120.0],
    ]
    with pytest.raises(MassingModelError) as exc:
        build_massing_model(lot_ring=lot, proposed_massing=_rect_block())
    assert exc.value.reason == "lot_ring_out_of_nyc_bounds"
    assert exc.value.field == "lot_ring"


def test_t106_as1_near_overflow_lot_still_refuses_magnitude_first():
    """The raw NYC check is ordered AFTER the magnitude bound, so a ~1e154 overflow lot
    still refuses coordinate_out_of_range (not mislabelled lot_ring_out_of_nyc_bounds):
    the accepted M5-T088 precedence is preserved by the raw-vertex ordering."""
    big = 1e154
    lot = [[-big, -big], [big, -big], [big, big], [-big, big]]
    with pytest.raises(MassingModelError) as exc:
        build_massing_model(lot_ring=lot, proposed_massing=_rect_block())
    assert exc.value.reason == "coordinate_out_of_range"
    assert exc.value.field == "lot_ring[0]"


# --- AS-2: the geometry-engine wrap catches the whole ShapelyError family ----


def test_t106_as2_non_geos_shapely_error_is_wrapped(monkeypatch):
    """DB-069 b / M5-T098 G3 ADVISORY-2 / G5 F-LOW-1: the wrap catches the whole
    shapely ShapelyError family, not only GEOSException. A non-GEOS sibling
    (TopologicalError) raised on a build path is wrapped as a typed
    geometry_engine_error; the earlier `except GEOSException` would let it ESCAPE
    untyped. Proven with a spy on the module's Polygon construct. The fixture asserts
    the sibling is genuinely a ShapelyError but NOT a GEOSException, so the widening is
    real; the mutant (except GEOSException) reddens because a raw TopologicalError
    escapes instead of a MassingModelError."""
    from shapely.errors import GEOSException, ShapelyError, TopologicalError

    assert issubclass(TopologicalError, ShapelyError)
    assert not issubclass(TopologicalError, GEOSException)  # a genuine non-GEOS sibling

    def exploding_polygon(*args, **kwargs):
        raise TopologicalError("simulated non-GEOS shapely engine failure")

    monkeypatch.setattr(mm, "Polygon", exploding_polygon)
    with pytest.raises(MassingModelError) as exc:
        _build(_rect_block())
    assert exc.value.reason == "geometry_engine_error"


def test_t106_as2_typed_refusal_still_passes_through_the_widened_wrap():
    """The widened wrap stays SELECTIVE: MassingModelError is a ValueError, disjoint
    from ShapelyError, so a typed refusal raised inside the wrapped body is not swallowed
    or re-wrapped - its own reason survives (here footprint_outside_lot)."""
    block = _rect_block()
    block["outline"] = _outline([[x + 200.0, y] for x, y in RECT])  # outside the lot
    with pytest.raises(MassingModelError) as exc:
        _build(block)
    assert exc.value.reason == "footprint_outside_lot"


# --- AS-3: the lot NYC check probes the Y clause and later vertices ----------


def test_t106_as3_lot_in_x_range_out_of_y_range_is_refused():
    """DB-069 c / M5-T098 G4 ADVISORY-A: the Y clause was under-probed (every prior lot
    fixture violated X first). A lot whose vertices are IN the X range but OUT of the Y
    range is refused, naming lot_ring. Dropping the `and NYC_2263_Y_MIN <= y <= ...`
    clause reddens this (only X checked -> the lot builds far from the footprint and
    refuses footprint_outside_lot, a different reason)."""
    y_out = mm.NYC_2263_Y_MAX + 1000.0  # above the northing range; x stays in range
    lot = [[1000000.0, y_out], [1000100.0, y_out],
           [1000100.0, y_out + 120.0], [1000000.0, y_out + 120.0]]
    with pytest.raises(MassingModelError) as exc:
        build_massing_model(lot_ring=lot, proposed_massing=_rect_block())
    assert exc.value.reason == "lot_ring_out_of_nyc_bounds"
    assert exc.value.field == "lot_ring"


def test_t106_as3_lot_later_vertex_out_of_range_is_refused():
    """DB-069 c / M5-T098 G4 ADVISORY-A: the check must scan EVERY vertex, not only
    ring[0]. A lot whose first two vertices are in-range but a LATER vertex is out of the
    Y range is refused. Checking only ring[0] reddens this: the tall in-X lot otherwise
    contains the footprint and builds cleanly (no refusal at all)."""
    y_out = mm.NYC_2263_Y_MAX + 1000.0
    lot = [
        [1000000.0, 200000.0],   # vertex[0] fully in range
        [1000100.0, 200000.0],   # vertex[1] fully in range
        [1000100.0, y_out],      # a LATER vertex out of the Y range
        [1000000.0, y_out],
    ]
    with pytest.raises(MassingModelError) as exc:
        build_massing_model(lot_ring=lot, proposed_massing=_rect_block())
    assert exc.value.reason == "lot_ring_out_of_nyc_bounds"
    assert exc.value.field == "lot_ring"


# --- AS-4: refusal messages echo at most a bounded preview of caller input ---


def test_t106_as4_lot_vertex_refusal_echo_is_bounded():
    """DB-069 d / M5-T098 G5 F-LOW-2: a refusal echoing caller input is length-bounded.
    The lot path has no B0 total-positions gate, so a 200,000-character vertex value
    would otherwise produce a ~200,055-character message (log / response amplification).
    An unbounded `repr` reddens this (the full pasted value appears and the message is
    ~200,000 chars)."""
    huge = "9" * 200_000
    lot = [[huge, 200000.0], [1000100.0, 200000.0], [1000100.0, 200120.0],
           [1000000.0, 200120.0]]
    with pytest.raises(MassingModelError) as exc:
        build_massing_model(lot_ring=lot, proposed_massing=_rect_block())
    msg = str(exc.value)
    assert exc.value.reason == "non_finite"
    assert huge not in msg          # the full pasted value is truncated, not echoed
    assert len(msg) <= 300          # bounded (the preview limit + marker + prefix)
    assert "chars>" in msg          # the truncation marker is present (input was elided)


def test_t106_as4_invalid_source_refusal_echo_is_bounded():
    """The same bound applies to the `source` echo (a distinct caller-input echo site);
    an unbounded `repr` reddens it too."""
    huge = "x" * 200_000
    with pytest.raises(MassingModelError) as exc:
        build_massing_model(lot_ring=LOT_RING, proposed_massing=_rect_block(), source=huge)
    msg = str(exc.value)
    assert exc.value.reason == "invalid_source"
    assert huge not in msg
    assert len(msg) <= 300


def test_t106_as4_preview_is_transparent_for_small_values():
    """_preview does not alter a within-bound value (so valid-input error messages and
    the goldens are unchanged): a short repr is returned verbatim, and the bound is the
    declared MAX_ECHO_CHARS."""
    assert mm._preview([1000000.0, 200000.0]) == repr([1000000.0, 200000.0])
    assert mm.MAX_ECHO_CHARS == 120
    long = "z" * (mm.MAX_ECHO_CHARS + 50)
    out = mm._preview(long)
    assert len(out) < len(repr(long))
    assert out.startswith(repr(long)[: mm.MAX_ECHO_CHARS])


# --- AS-6: valid-input output is byte-identical (goldens unchanged) ----------


def test_t106_as6_valid_input_goldens_byte_identical():
    """AS-6 scope: the M5-T106 guards touch only refusal paths; a valid build is
    unchanged, so both accepted goldens (the 1-floor RECT and the 5-floor stack) stay
    byte-identical."""
    assert _build(_rect_block()).content_hash() == (
        "sha256:b7fa9862a0bb23885e7d7d71dae4a2d448a6ca4720f29a7b6bf68b4227c5133b"
    )
    assert _build(_five_floor_block()).content_hash() == (
        "sha256:e23b5cbcca6ea7defee4b04c6bac51a94d4c26b5e643e2af923d29d1c248a6c5"
    )


# ---------------------------------------------------------------------------
# M5-T106 round 2 (before-wiring preconditions for PKT-E / M5-T107): the typed
# boundary is completed for out-of-float-range integers, the residual echo sites
# are bounded, a second ShapelyError sibling pins the base-class catch, and
# _preview is proven never to raise. Every test here is ADDED (append-only).
# ---------------------------------------------------------------------------


# --- MED-1: a huge-integer coordinate fails closed as a typed non_finite -----


def test_t106r2_huge_int_lot_vertex_is_typed_non_finite():
    """G5 MED-1 (lot path): a JSON integer literal beyond the float range (10**400)
    makes math.isfinite overflow. It must fail closed as a typed non_finite refusal, NOT
    escape as an untyped OverflowError. _is_finite_number treats an out-of-float-range int
    as non-finite; the refusal message is bounded too.

    Mutation (revert _is_finite_number to call math.isfinite without the OverflowError
    guard): an untyped OverflowError escapes build_massing_model -> pytest.raises(
    MassingModelError) is not satisfied -> RED."""
    huge = 10 ** 400
    lot = [[huge, 200000.0], [1000100.0, 200000.0],
           [1000100.0, 200120.0], [1000000.0, 200120.0]]
    with pytest.raises(MassingModelError) as exc:
        build_massing_model(lot_ring=lot, proposed_massing=_rect_block())
    assert exc.value.reason == "non_finite"
    assert exc.value.field == "lot_ring[0]"
    assert len(str(exc.value)) <= 300  # the echo of the huge int is bounded


def test_t106r2_huge_int_footprint_vertex_is_typed_non_finite():
    """G5 MED-1 (footprint path): the same 10**400 in the proposal FOOTPRINT overflows B0's
    own finiteness check (proposal._is_real_number -> math.isfinite), which raises
    OverflowError, NOT a ProposedMassingError - so the existing `except ProposedMassingError`
    never sees it. The added `except OverflowError` types it as the same non_finite refusal.

    Mutation (drop the `except OverflowError` on the B0 validation try/except): the
    OverflowError escapes build_massing_model untyped -> RED."""
    block = _rect_block()
    block["outline"] = _outline(
        [[10 ** 400, 200010.0], [1000050.0, 200010.0],
         [1000050.0, 200070.0], [1000010.0, 200070.0]])
    with pytest.raises(MassingModelError) as exc:
        build_massing_model(lot_ring=LOT_RING, proposed_massing=block)
    assert exc.value.reason == "non_finite"
    assert exc.value.field == "proposed_massing.outline"


# --- LOW-1 / G3 ADVISORY-1(B): the re-echoed B0 error is length-bounded -------


def test_t106r2_b0_error_echo_is_bounded():
    """G5 LOW-1 = G3 ADVISORY-1(B): build_massing_model re-echoes the B0 ProposedMassingError
    text at the validation boundary. A 200,000-character FOOTPRINT vertex makes B0 produce a
    ~200,000-character message (proposal.py:250 `{vertex!r}`), which the re-echo would repeat
    unbounded. _preview(exc) bounds it.

    Mutation (revert the re-echo to `{exc}`): the message balloons to ~200,000 chars and the
    pasted value appears -> RED."""
    huge = "9" * 200_000
    block = _rect_block()
    block["outline"] = _outline(
        [[huge, 200010.0], [1000050.0, 200010.0],
         [1000050.0, 200070.0], [1000010.0, 200070.0]])
    with pytest.raises(MassingModelError) as exc:
        build_massing_model(lot_ring=LOT_RING, proposed_massing=block)
    msg = str(exc.value)
    assert exc.value.reason == "invalid_source"
    assert huge not in msg           # the pasted value is truncated, not echoed
    assert len(msg) <= 300           # bounded (prefix + preview + marker)
    assert "chars>" in msg           # the truncation marker is present


# --- G3 ADVISORY-1(A) = G4 ADVISORY-2: the no-candidate detail is bounded -----


def test_t106r2_no_candidate_detail_echo_is_bounded():
    """G3 ADVISORY-1(A) = G4 ADVISORY-2: build_from_generated_option's no-candidate path
    echoes the engine placement-gap `detail`. A 200,000-character detail would otherwise
    produce a ~200,000-character refusal. _preview(detail) bounds it.

    Mutation (revert to `{detail or ''}`): the full detail appears and the message is
    ~200,000 chars -> RED."""
    huge = "z" * 200_000
    envelope = {
        "candidate": None,
        "candidate_placement": {"status": "footprint_exceeds_lot", "detail": huge},
    }
    with pytest.raises(MassingModelError) as exc:
        build_from_generated_option(lot_ring=LOT_RING, max_envelope=envelope)
    msg = str(exc.value)
    assert exc.value.reason == "no_generated_candidate"
    assert huge not in msg
    assert len(msg) <= 300
    assert "chars>" in msg

    # A short, valid detail is still surfaced (the bound is transparent for small input).
    short = {
        "candidate": None,
        "candidate_placement": {"status": "footprint_exceeds_lot",
                                "detail": "the rules-derived footprint exceeds the lot"},
    }
    with pytest.raises(MassingModelError) as exc2:
        build_from_generated_option(lot_ring=LOT_RING, max_envelope=short)
    assert "footprint exceeds the lot" in str(exc2.value)


# --- G4 ADVISORY-1: a SECOND, distinct ShapelyError sibling pins the base catch


def test_t106r2_second_non_geos_shapely_sibling_is_also_wrapped(monkeypatch):
    """G4 ADVISORY-1: the AS-2 wrap must catch the ShapelyError BASE class, not an
    enumerated pair. test_t106_as2 exercises only TopologicalError; a maintainer narrowing
    the catch to `except (GEOSException, TopologicalError)` would ship green while other
    siblings escaped untyped. A SECOND, different sibling (GeometryTypeError - a genuine
    ShapelyError that is neither a GEOSException NOR a TopologicalError) raised on a build
    path is also wrapped as a typed geometry_engine_error.

    Mutation (`except (GEOSException, TopologicalError)`): GeometryTypeError escapes
    untyped -> RED (this test), while test_t106_as2 above stays green."""
    from shapely.errors import GeometryTypeError, GEOSException, ShapelyError, TopologicalError

    assert issubclass(GeometryTypeError, ShapelyError)
    assert not issubclass(GeometryTypeError, GEOSException)
    assert not issubclass(GeometryTypeError, TopologicalError)  # distinct from AS-2's sibling

    def exploding_polygon(*args, **kwargs):
        raise GeometryTypeError("simulated non-GEOS, non-Topological shapely failure")

    monkeypatch.setattr(mm, "Polygon", exploding_polygon)
    with pytest.raises(MassingModelError) as exc:
        _build(_rect_block())
    assert exc.value.reason == "geometry_engine_error"


# --- G5 INFO: _preview itself never raises -----------------------------------


def test_t106r2_preview_never_raises_when_repr_raises():
    """G5 INFO: _preview must never itself raise - a refusal message must always be
    buildable. A hostile __repr__ (RuntimeError) and a self-recursive __repr__
    (RecursionError) both yield the fixed `<unrepresentable value>` placeholder instead of
    propagating.

    Mutation (drop the try/except so repr(value) is called directly): the exception escapes
    _preview -> the call raises and the assertions are never reached -> RED."""
    class _Hostile:
        def __repr__(self):
            raise RuntimeError("hostile __repr__")

    class _Recursive:
        def __repr__(self):
            return repr(self)  # unbounded recursion -> RecursionError

    assert mm._preview(_Hostile()) == "<unrepresentable value>"
    assert mm._preview(_Recursive()) == "<unrepresentable value>"
    # a normal value is still previewed verbatim (the guard is transparent)
    assert mm._preview([1.0, 2.0]) == repr([1.0, 2.0])
