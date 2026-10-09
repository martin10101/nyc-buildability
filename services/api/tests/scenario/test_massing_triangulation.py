"""M5-T112 (DB-082 a): the public reusable ear-clipping triangulator.

Covers :func:`app.scenario.massing_triangulation.triangulate_polygon` - the ONE
documented public API the later GLB cap-export fix reuses instead of a naive vertex-0
fan: convex and concave (L / U) rings triangulate to ``n-2`` CCW triangles whose area
sum equals the polygon area and each of which stays inside the ring (no notch spanning);
exactly-collinear vertices collapse; and the work budget and a non-simple ring each fail
closed as a typed :class:`MassingModelError`. The returned triangle indices reference the
PREPARED ring, so a consumer builds a correct cap without re-deriving vertex order.

Each test has a named in-process mutation (of the CONSUMING triangulation namespace) that
reddens it; those mutations are demonstrated in the producer report and NOT committed here.
"""

from __future__ import annotations

import math

import pytest
from shapely.geometry import Polygon

from app.scenario.massing_guards import MassingModelError
from app.scenario.massing_triangulation import (
    MAX_TRIANGULATION_WORK,
    Triangulation,
    _min_ear_clip_work,
    _WorkBudget,
    triangulate_polygon,
)

# Simple test rings (no NYC range check applies to the public triangulator).
SQUARE = [[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]]  # area 100
LSHAPE = [[0.0, 0.0], [60.0, 0.0], [60.0, 30.0], [30.0, 30.0], [30.0, 80.0], [0.0, 80.0]]
USHAPE = [[0.0, 0.0], [80.0, 0.0], [80.0, 90.0], [60.0, 90.0], [60.0, 30.0],
          [20.0, 30.0], [20.0, 90.0], [0.0, 90.0]]
# A square with an exactly-collinear midpoint on the bottom edge (should collapse away).
SQUARE_WITH_COLLINEAR = [[0.0, 0.0], [5.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]]
# A self-touching ring that revisits an interior vertex (a single ring cannot carry a
# hole): _prepare_ring refuses it as a duplicate-vertex self-intersection.
SELF_TOUCHING = [[0.0, 0.0], [10.0, 0.0], [5.0, 5.0], [10.0, 10.0], [0.0, 10.0], [5.0, 5.0]]


def _tri_signed_area(a, b, c) -> float:
    """CCW-positive signed area, independent of the module under test."""
    return ((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])) / 2.0


def _tri_area_sum(result: Triangulation) -> float:
    return sum(abs(_tri_signed_area(result.ring[a], result.ring[b], result.ring[c]))
               for a, b, c in result.triangles)


def _regular(n: int, radius: float = 40.0):
    return [[round(radius * math.cos(2 * math.pi * k / n), 6),
             round(radius * math.sin(2 * math.pi * k / n), 6)] for k in range(n)]


def test_returns_triangulation_of_prepared_ring():
    result = triangulate_polygon(SQUARE, "square")
    assert isinstance(result, Triangulation)
    assert len(result.ring) == 4
    assert result.triangles  # non-empty CCW index triples into result.ring
    for tri in result.triangles:
        assert all(0 <= i < len(result.ring) for i in tri)


@pytest.mark.parametrize(
    "points,expected_area",
    [(SQUARE, 100.0),
     (_regular(8), None),
     (LSHAPE, 3300.0),
     (USHAPE, 80 * 90 - 40 * 60)],
    ids=["convex_square", "convex_octagon", "concave_l", "concave_u"],
)
def test_area_sum_equals_polygon_area_and_all_ccw(points, expected_area):
    """MUTATION (concave params): monkeypatch massing_triangulation._point_in_triangle ->
    always False drops the containment guard, so an L/U ear spans the notch and the area
    sum exceeds the polygon area -> RED. (Documented in the producer report.)"""
    result = triangulate_polygon(points, "poly")
    poly = Polygon([(x, y) for x, y in result.ring])
    if expected_area is not None:
        assert abs(poly.area - expected_area) < 1e-6
    # n-2 triangles for a simple polygon.
    assert len(result.triangles) == len(result.ring) - 2
    # Each triangle CCW and covered by the polygon (a fan on U spans the notch).
    for a, b, c in result.triangles:
        assert _tri_signed_area(result.ring[a], result.ring[b], result.ring[c]) > 0.0
        assert poly.covers(Polygon([result.ring[a], result.ring[b], result.ring[c]]))
    # Triangle area sum equals the polygon area within tolerance.
    assert abs(_tri_area_sum(result) - poly.area) <= 1e-9 * poly.area


def test_exactly_collinear_vertices_collapse():
    """MUTATION: monkeypatch massing_triangulation._cross3 -> a nonzero constant so the
    collinear-collapse test in _prepare_ring never fires; the midpoint is kept and the
    prepared ring has 5 vertices -> RED. (Documented in the producer report.)"""
    result = triangulate_polygon(SQUARE_WITH_COLLINEAR, "square_mid")
    assert len(result.ring) == 4  # the exactly-collinear midpoint is gone
    assert (5.0, 0.0) not in result.ring
    assert len(result.triangles) == 2
    poly = Polygon([(x, y) for x, y in result.ring])
    assert abs(_tri_area_sum(result) - poly.area) <= 1e-9 * poly.area


def test_work_budget_overspend_is_refused():
    """MUTATION: monkeypatch massing_triangulation._WorkBudget.charge -> a no-op so nothing
    is metered; no refusal is raised and pytest.raises is unsatisfied -> RED. (Documented in
    the producer report.)"""
    with pytest.raises(MassingModelError) as exc:
        triangulate_polygon(SQUARE, "square", budget=_WorkBudget(1))
    assert exc.value.reason == "triangulation_budget_exceeded"
    assert exc.value.field == "square"


def test_budget_admits_a_realistic_ring_by_default():
    result = triangulate_polygon(_regular(50), "n50")
    assert len(result.triangles) == 48
    # The default budget comfortably covers a convex ring's exact least work.
    assert _min_ear_clip_work(50) <= MAX_TRIANGULATION_WORK


def test_self_touching_ring_fails_closed():
    """A self-touching ring is caught by the duplicate-vertex check during preparation,
    BEFORE the ear scan (so the message names the duplicate, not a triangulation stall).

    MUTATION: monkeypatch massing_triangulation._prepare_ring -> a variant without the
    duplicate-vertex ``set`` check; the ring then reaches the ear scan and refuses with the
    'could not be triangulated' message instead, so the message assertion reddens. (Both
    layers refuse, so the message pins WHICH layer catches it; documented in the report.)"""
    with pytest.raises(MassingModelError) as exc:
        triangulate_polygon(SELF_TOUCHING, "self_touch")
    assert exc.value.reason == "self_intersection"
    assert "duplicate vertex" in str(exc.value)


def test_too_few_distinct_vertices_is_degenerate_refusal():
    """MUTATION: monkeypatch massing_triangulation._prepare_ring -> a variant without the
    ``len(parsed) < 3`` guard; the two-point ring reaches the collinear collapse and refuses
    with the 'collapses to fewer than 3' message instead, so this message assertion reddens.
    (Documented in the producer report.)"""
    with pytest.raises(MassingModelError) as exc:
        triangulate_polygon([[0.0, 0.0], [1.0, 1.0]], "twopt")
    assert exc.value.reason == "invalid_source"
    assert "at least 3 distinct vertices" in str(exc.value)


def test_indices_reference_prepared_ring_not_raw_input():
    """The closing duplicate is dropped, so indices point into the prepared ring - a
    consumer that indexed the raw (closed) input would misplace a cap face."""
    closed_square = [*SQUARE, SQUARE[0]]  # explicitly closed (5 positions)
    result = triangulate_polygon(closed_square, "closed")
    assert len(result.ring) == 4  # the closing duplicate is not a ring vertex
    for tri in result.triangles:
        assert all(0 <= i < 4 for i in tri)
