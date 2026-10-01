"""Make the selected lots' tax-map lines meet exactly, independent of lot order (B-07).

Neighbouring tax lots do not always share vertices. A narrow rear lot's corners can sit in
the middle of a deeper lot's rear line (a T-junction), and outlines can be rounded
independently (the MapPLUTO adapter measures the verbatim ring). Before any shared line is
measured or any outline is joined, every selected lot is conformed against all the others,
in two order-free steps, both within ``SHARED_LINE_TOLERANCE_FT``:

1. Vertices of different lots that lie within the tolerance of each other form one group
   (transitively) and all move to the group's lowest (x, y) vertex.
2. Each lot's lines are noded at every other lot's vertex that lies within the tolerance of
   them (GEOS ``snap`` against the other lots' vertices, sorted): the vertex is inserted, so
   the shared stretch of the two lines has the same end points in both lots.

A lot narrower than twice the tolerance somewhere is refused first, with the reason: its
lines could be matched to its own opposite line instead of a neighbour's.

Nothing else moves: a gap or an overlap wider than the tolerance stays as it is. Because the
inputs are treated as a set (vertex groups by coordinates, references sorted), the result
for each lot does not depend on the order the lots were given in.
"""

from __future__ import annotations

from collections.abc import Sequence

import shapely
from shapely.geometry import MultiPoint, Point, Polygon

from .parameters import SHARED_LINE_TOLERANCE_FT

__all__ = ["conform_outlines"]

_Point = tuple[float, float]


def _ring(polygon: Polygon) -> list[_Point]:
    return [(float(x), float(y)) for x, y in polygon.exterior.coords[:-1]]


def _groups(rings: Sequence[list[_Point]]) -> dict[_Point, _Point]:
    """Each vertex -> the lowest vertex of its group (vertices of different lots within the
    tolerance, joined transitively)."""
    owners: dict[_Point, set[int]] = {}
    for index, ring in enumerate(rings):
        for point in ring:
            owners.setdefault(point, set()).add(index)
    points = sorted(owners)
    parent = list(range(len(points)))

    def root(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    tree = shapely.STRtree([Point(p) for p in points])
    left, right = tree.query([Point(p) for p in points], predicate="dwithin",
                             distance=SHARED_LINE_TOLERANCE_FT)
    for i, j in zip(left.tolist(), right.tolist(), strict=True):
        # Only vertices of different lots are grouped; a lot's own corners stay apart.
        if i != j and len(owners[points[i]] | owners[points[j]]) > 1:
            a, b = root(i), root(j)
            parent[max(a, b)] = min(a, b)
    return {point: points[root(i)] for i, point in enumerate(points)}


def _moved(ring: list[_Point], groups: dict[_Point, _Point]) -> list[_Point]:
    out: list[_Point] = []
    for point in ring:
        target = groups[point]
        if not out or out[-1] != target:
            out.append(target)
    while len(out) > 1 and out[0] == out[-1]:
        out.pop()
    return out


def conform_outlines(
    polygons: Sequence[Polygon], names: Sequence[str] | None = None
) -> tuple[tuple[Polygon, ...], str | None]:
    """``(conformed, None)`` with one polygon per input, in input order, or ``((), reason)``
    when a lot is narrower than twice the tolerance somewhere, or is no longer a valid shape
    after conforming.
    ``names`` label the lots in the reason."""
    labels = list(names) if names is not None else [f"lot {i + 1}" for i in range(len(polygons))]
    for label, polygon in zip(labels, polygons, strict=True):
        # A lot narrower than twice the tolerance somewhere has lines that could be matched
        # to its own opposite line instead of a neighbour's: shrinking it by the tolerance
        # then empties it or cuts it in two.
        shrunk = polygon.buffer(-SHARED_LINE_TOLERANCE_FT)
        if shrunk.is_empty or shrunk.geom_type != "Polygon":
            return (), (f"{label[0].upper()}{label[1:]} is narrower than "
                        f"{2 * SHARED_LINE_TOLERANCE_FT:.2f} ft in places, so its tax-map lines "
                        "cannot be matched to its neighbours'. The tax-map lines need review.")
    rings = [_ring(p) for p in polygons]
    groups = _groups(rings)
    moved = [_moved(ring, groups) for ring in rings]
    conformed: list[Polygon] = []
    for index, ring in enumerate(moved):
        others = sorted({point for j, other in enumerate(moved) if j != index for point in other})
        shape = Polygon(ring) if len(ring) >= 3 else None
        if shape is not None and others:
            shape = shapely.snap(shape, MultiPoint(others), SHARED_LINE_TOLERANCE_FT)
        if shape is None or shape.geom_type != "Polygon" or not shape.is_valid:
            return (), ("The selected lots' tax-map lines could not be matched within "
                        f"{SHARED_LINE_TOLERANCE_FT:.2f} ft without changing a lot's shape.")
        conformed.append(shape)
    return tuple(conformed), None
