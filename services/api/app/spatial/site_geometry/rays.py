"""Planar ray and angle primitives for site geometry (queue item B-03).

Pure arithmetic in EPSG:2263 feet; no I/O, no shapely. Used to look straight out from
(and straight into) a lot line.
"""

from __future__ import annotations

import math

from .inputs import Point2
from .outline import OutlineEdge
from .parameters import MAX_SAMPLES_PER_EDGE, MIN_SAMPLES_PER_EDGE, SAMPLE_SPACING_FT

__all__ = [
    "line_angle_deg",
    "ray_segment_distance",
    "sample_points",
    "unit",
    "vector_angle_deg",
]

_PARALLEL_EPS = 1e-12
_T_EPS = 1e-6
_S_EPS = 1e-9


def sample_points(edge: OutlineEdge) -> list[tuple[Point2, float]]:
    """Evenly spaced points strictly inside the edge, each with the length it stands for."""
    count = math.ceil(edge.length_ft / SAMPLE_SPACING_FT)
    count = max(MIN_SAMPLES_PER_EDGE, min(MAX_SAMPLES_PER_EDGE, count))
    (x0, y0), (x1, y1) = edge.start, edge.end
    weight = edge.length_ft / count
    points = []
    for i in range(count):
        f = (i + 0.5) / count
        points.append(((x0 + (x1 - x0) * f, y0 + (y1 - y0) * f), weight))
    return points


def ray_segment_distance(
    origin: Point2, direction: Point2, a: Point2, b: Point2, max_distance: float
) -> float | None:
    """Distance along the unit ray ``origin + t * direction`` to segment ``a``-``b``.

    Returns ``t`` for a crossing with ``0 < t <= max_distance``, else None. A segment
    running exactly along the ray never counts as a crossing.
    """
    ex, ey = b[0] - a[0], b[1] - a[1]
    dx, dy = direction
    denom = dx * ey - dy * ex
    if abs(denom) <= _PARALLEL_EPS * max(1.0, math.hypot(ex, ey)):
        return None
    wx, wy = a[0] - origin[0], a[1] - origin[1]
    t = (wx * ey - wy * ex) / denom
    s = (wx * dy - wy * dx) / denom
    if t <= _T_EPS or t > max_distance or s < -_S_EPS or s > 1.0 + _S_EPS:
        return None
    return t


def unit(vector: Point2) -> Point2 | None:
    length = math.hypot(vector[0], vector[1])
    if length == 0.0:
        return None
    return vector[0] / length, vector[1] / length


def vector_angle_deg(u: Point2, v: Point2) -> float:
    """Angle between two unit vectors, 0..180 degrees."""
    dot = max(-1.0, min(1.0, u[0] * v[0] + u[1] * v[1]))
    return math.degrees(math.acos(dot))


def line_angle_deg(u: Point2, v: Point2) -> float:
    """Angle between two undirected lines given by unit vectors, 0..90 degrees."""
    angle = vector_angle_deg(u, v)
    return min(angle, 180.0 - angle)
