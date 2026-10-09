"""Pure planar geometry for the drawing kit (feet; stdlib only, no I/O).

Only what the kit needs to validate and draw outlines: closed-ring checks,
simplicity (no self-crossing), point/ring containment with a boundary
tolerance, edge lengths, bounding boxes and outward normals.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence

from .model import Point, Ring

__all__ = [
    "BOUNDARY_TOL_FT",
    "all_points",
    "bbox",
    "centroid",
    "edge_length",
    "edges",
    "interiors_overlap",
    "is_simple",
    "outward_normal",
    "point_location",
    "point_on_boundary",
    "ring_area",
    "ring_within",
    "rings_cross",
    "signed_area",
    "split_probes",
]

# Boundary tolerance for "on the line" (1e-6 ft; EPSG:2263 values near 1e6 ft
# still carry ~1e-10 ft of float64 precision).
BOUNDARY_TOL_FT = 1e-6


def edges(ring: Ring) -> list[tuple[Point, Point]]:
    """The ring's edges; the ring is closed, so edge i joins vertex i and i+1."""
    return [(ring[i], ring[i + 1]) for i in range(len(ring) - 1)]


def edge_length(a: Point, b: Point) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def signed_area(ring: Ring) -> float:
    """Shoelace area; positive for counter-clockwise rings (x east, y north)."""
    total = 0.0
    for (ax, ay), (bx, by) in edges(ring):
        total += ax * by - bx * ay
    return total / 2.0


def bbox(points: Iterable[Point]) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    for x, y in points:
        xs.append(x)
        ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def _cross(o: Point, a: Point, b: Point) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _sign(value: float, tol: float) -> int:
    if value > tol:
        return 1
    if value < -tol:
        return -1
    return 0


def _distance_to_segment(p: Point, a: Point, b: Point) -> float:
    dx, dy = b[0] - a[0], b[1] - a[1]
    length_sq = dx * dx + dy * dy
    if length_sq == 0.0:
        return math.hypot(p[0] - a[0], p[1] - a[1])
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / length_sq))
    return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy))


def point_on_boundary(p: Point, ring: Ring, tol: float = BOUNDARY_TOL_FT) -> bool:
    return any(_distance_to_segment(p, a, b) <= tol for a, b in edges(ring))


def point_location(p: Point, ring: Ring, tol: float = BOUNDARY_TOL_FT) -> str:
    """``inside``, ``boundary`` or ``outside`` (even-odd ray casting)."""
    if point_on_boundary(p, ring, tol):
        return "boundary"
    x, y = p
    inside = False
    for (ax, ay), (bx, by) in edges(ring):
        if (ay > y) != (by > y):
            x_cross = ax + (y - ay) * (bx - ax) / (by - ay)
            if x_cross > x:
                inside = not inside
    return "inside" if inside else "outside"


def _segments_touch(a: Point, b: Point, c: Point, d: Point, tol: float) -> bool:
    """Whether closed segments ab and cd share at least one point."""
    o1, o2 = _sign(_cross(a, b, c), tol), _sign(_cross(a, b, d), tol)
    o3, o4 = _sign(_cross(c, d, a), tol), _sign(_cross(c, d, b), tol)
    if o1 * o2 < 0 and o3 * o4 < 0:
        return True
    return (
        _distance_to_segment(c, a, b) <= tol
        or _distance_to_segment(d, a, b) <= tol
        or _distance_to_segment(a, c, d) <= tol
        or _distance_to_segment(b, c, d) <= tol
    )


def _segments_cross(a: Point, b: Point, c: Point, d: Point, tol: float) -> bool:
    """Whether ab and cd cross at a point interior to both (a proper crossing)."""
    o1, o2 = _sign(_cross(a, b, c), tol), _sign(_cross(a, b, d), tol)
    o3, o4 = _sign(_cross(c, d, a), tol), _sign(_cross(c, d, b), tol)
    return o1 * o2 < 0 and o3 * o4 < 0


def is_simple(ring: Ring, tol: float = BOUNDARY_TOL_FT) -> bool:
    """No zero-length edge, and no two edges meet except neighbours at their
    shared vertex (neighbours must not fold back over each other)."""
    segs = edges(ring)
    n = len(segs)
    if any(edge_length(a, b) <= tol for a, b in segs):
        return False
    for i in range(n):
        a, b = segs[i]
        for j in range(i + 1, n):
            c, d = segs[j]
            adjacent = j == i + 1 or (i == 0 and j == n - 1)
            if not adjacent:
                if _segments_touch(a, b, c, d, tol):
                    return False
                continue
            # Neighbours share one vertex; fail when they fold back collinearly.
            shared, far_a, far_c = (b, a, d) if j == i + 1 else (a, b, c)
            if _sign(_cross(shared, far_a, far_c), tol) == 0:
                ux, uy = far_a[0] - shared[0], far_a[1] - shared[1]
                vx, vy = far_c[0] - shared[0], far_c[1] - shared[1]
                if ux * vx + uy * vy > 0:
                    return False
    return True


def split_probes(ring: Ring, other: Ring, tol: float = BOUNDARY_TOL_FT) -> list[Point]:
    """``ring``'s vertices plus the midpoint of every piece of its edges once
    they are split at ``other``'s vertices lying on them. When the two
    boundaries never properly cross, each piece lies wholly inside, outside or
    on ``other``, so these probes classify the whole boundary exactly."""
    probes: list[Point] = list(ring[:-1])
    others = other[:-1]
    for a, b in edges(ring):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length_sq = dx * dx + dy * dy
        cuts = [0.0, 1.0]
        for p in others:
            if _distance_to_segment(p, a, b) <= tol:
                cuts.append(((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / length_sq)
        cuts = sorted(min(1.0, max(0.0, t)) for t in cuts)
        for t0, t1 in zip(cuts, cuts[1:], strict=False):
            if (t1 - t0) * math.sqrt(length_sq) > tol:
                tm = (t0 + t1) / 2.0
                probes.append((a[0] + tm * dx, a[1] + tm * dy))
    return probes


def rings_cross(first: Ring, second: Ring, tol: float = BOUNDARY_TOL_FT) -> bool:
    """Whether any edge of ``first`` properly crosses an edge of ``second``."""
    second_edges = edges(second)
    return any(
        _segments_cross(a, b, c, d, tol) for a, b in edges(first) for c, d in second_edges
    )


def ring_within(inner: Ring, outer: Ring, tol: float = BOUNDARY_TOL_FT) -> bool:
    """Whether ``inner`` lies inside ``outer`` (touching the boundary allowed).

    No edges properly cross; no piece of ``inner``'s boundary lies outside
    ``outer``; and no piece of ``outer``'s boundary lies strictly inside
    ``inner`` (which catches an outer notch whose sides pass through the
    inner boundary only at vertices or collinearly).
    """
    if rings_cross(inner, outer, tol):
        return False
    if any(point_location(p, outer, tol) == "outside" for p in split_probes(inner, outer, tol)):
        return False
    return not any(
        point_location(p, inner, tol) == "inside" for p in split_probes(outer, inner, tol)
    )


def interiors_overlap(first: Ring, second: Ring, tol: float = BOUNDARY_TOL_FT) -> bool:
    """Whether the areas enclosed by two simple rings share any interior."""
    if rings_cross(first, second, tol):
        return True
    places = [point_location(p, second, tol) for p in split_probes(first, second, tol)]
    if "inside" in places or all(place == "boundary" for place in places):
        return True  # part of ``first`` inside ``second``, or the same outline
    return any(
        point_location(p, first, tol) == "inside" for p in split_probes(second, first, tol)
    )


def ring_area(ring: Ring) -> float:
    return abs(signed_area(ring))


def outward_normal(a: Point, b: Point, ring_area: float) -> tuple[float, float]:
    """Unit normal of edge ab pointing away from the ring's interior."""
    length = edge_length(a, b)
    dx, dy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    # For a counter-clockwise ring the interior is on the left of each edge.
    return (dy, -dx) if ring_area > 0 else (-dy, dx)


def centroid(ring: Ring) -> Point:
    """Area centroid of a simple ring."""
    area = signed_area(ring)
    cx = cy = 0.0
    for (ax, ay), (bx, by) in edges(ring):
        f = ax * by - bx * ay
        cx += (ax + bx) * f
        cy += (ay + by) * f
    return cx / (6.0 * area), cy / (6.0 * area)


def all_points(rings: Sequence[Ring]) -> list[Point]:
    return [p for ring in rings for p in ring]
