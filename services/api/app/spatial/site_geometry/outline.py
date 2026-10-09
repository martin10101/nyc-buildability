"""Lot outline preparation: CRS gate, validity checks and outline edges (queue item B-03).

Fails closed: an outline that is not EPSG:2263, has non-numeric or non-finite coordinates,
fewer than three distinct corners, crosses itself, or has (near-)zero area is refused with
a plain reason, and nothing is measured from it.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass

from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
from shapely.validation import explain_validity

from app.connectors.mappluto_geometry_arcgis import EXPECTED_LATEST_WKID, EXPECTED_WKID

from .inputs import LotOutline, Point2
from .parameters import MAX_LOT_VERTICES, MIN_LOT_AREA_SQ_FT, MIN_VERTEX_SPACING_FT

__all__ = [
    "OutlineEdge",
    "PreparedOutline",
    "crs_is_measurement_grade",
    "finite_point",
    "prepare_outline",
]


@dataclass(frozen=True)
class OutlineEdge:
    """One straight side of the outline. The ring is counterclockwise, so the lot lies to
    the left of ``direction`` and ``outward_normal`` points away from the lot."""

    index: int
    start: Point2
    end: Point2
    length_ft: float
    direction: Point2
    outward_normal: Point2


@dataclass(frozen=True)
class PreparedOutline:
    polygon: Polygon
    vertices: tuple[Point2, ...]
    edges: tuple[OutlineEdge, ...]


def crs_is_measurement_grade(crs: object) -> bool:
    """True only for the EPSG:2263 stamp (wkid 102718 / latest wkid 2263)."""
    if not isinstance(crs, Mapping):
        return False
    latest = crs.get("latest_wkid", crs.get("latestWkid"))
    return crs.get("wkid") == EXPECTED_WKID and latest == EXPECTED_LATEST_WKID


def finite_point(value: object) -> Point2 | None:
    """An (x, y) pair of finite real numbers, else None (bools are not numbers here)."""
    if not isinstance(value, tuple | list) or len(value) != 2:
        return None
    x, y = value
    for part in (x, y):
        if isinstance(part, bool) or not isinstance(part, int | float):
            return None
        if not math.isfinite(part):
            return None
    return float(x), float(y)


def _distinct_cycle(points: list[Point2]) -> list[Point2]:
    """Drop the closing vertex and consecutive repeats (closer than MIN_VERTEX_SPACING_FT)."""
    cycle: list[Point2] = []
    for point in points:
        if cycle and math.dist(cycle[-1], point) < MIN_VERTEX_SPACING_FT:
            continue
        cycle.append(point)
    while len(cycle) > 1 and math.dist(cycle[0], cycle[-1]) < MIN_VERTEX_SPACING_FT:
        cycle.pop()
    return cycle


def _edges(vertices: tuple[Point2, ...]) -> tuple[OutlineEdge, ...]:
    edges: list[OutlineEdge] = []
    count = len(vertices)
    for index in range(count):
        start = vertices[index]
        end = vertices[(index + 1) % count]
        length = math.dist(start, end)
        ux, uy = (end[0] - start[0]) / length, (end[1] - start[1]) / length
        edges.append(OutlineEdge(index, start, end, length, (ux, uy), (uy, -ux)))
    return tuple(edges)


def prepare_outline(lot: LotOutline) -> tuple[PreparedOutline | None, str | None]:
    """Return ``(prepared, None)`` or ``(None, reason)``."""
    if not crs_is_measurement_grade(lot.crs):
        return None, (
            "The lot outline is not in EPSG:2263 feet, so nothing is measured from it "
            "(display outlines in degrees are never measured)."
        )
    raw = list(lot.exterior) if isinstance(lot.exterior, tuple | list) else []
    if len(raw) > MAX_LOT_VERTICES + 1:
        return None, f"The lot outline has more than {MAX_LOT_VERTICES} corners."
    points = [finite_point(value) for value in raw]
    if any(point is None for point in points):
        return None, "The lot outline has a coordinate that is not a finite number."
    cycle = _distinct_cycle([point for point in points if point is not None])
    if len(cycle) < 3:
        return None, "The lot outline has fewer than three distinct corners."
    polygon = Polygon(cycle)
    if not polygon.is_valid:
        # Keep the problem's name only; the coordinates GEOS appends are never surfaced.
        problem = explain_validity(polygon).split("[", 1)[0].strip() or "invalid shape"
        return None, f"The lot outline is not a valid shape ({problem})."
    if polygon.area < MIN_LOT_AREA_SQ_FT:
        return None, "The lot outline encloses no measurable area."
    polygon = orient(polygon, sign=1.0)
    vertices = tuple((float(x), float(y)) for x, y in polygon.exterior.coords[:-1])
    return PreparedOutline(polygon, vertices, _edges(vertices)), None
