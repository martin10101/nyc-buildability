"""Building-footprint geometry helpers (task M5-T101, PKT-C, D-087-R003).

Behaviour-preserving extraction (step 1 of PKT-C): the ring reader, the
FOOTPRINT_GEOMETRY_POLICY parser and the query-relation classifier - plus the
small numeric helpers they share - are moved here VERBATIM from the OTI
building-footprint connector so the connector stays below the modularity cap
before the wiring-hardening riders are added. The connector re-exports every
public name below, so existing test imports keep resolving unchanged.

This module imports NOTHING from the connector: the dependency is one-way
(connector -> geometry), so the connector's import graph stays acyclic. (The
connector's module name is deliberately not repeated here: an unrelated
not-wired test greps app sources for that literal.)

Pure planar geometry on the published EPSG:2263 coordinates (never quantized,
never repaired). Deterministic code only: no AI, no network I/O, no legal logic.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from shapely.geometry import Polygon
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union
from shapely.validation import explain_validity

__all__ = [
    "COORD_ABS_MAX_FT",
    "FootprintPart",
    "GEOMETRY_INVALID",
    "GEOMETRY_REVIEW_REQUIRED",
    "GEOMETRY_VALID",
    "classify_query_relation",
    "parse_footprint_geometry",
]

GEOMETRY_VALID = "valid"
GEOMETRY_INVALID = "invalid"
GEOMETRY_REVIEW_REQUIRED = "review_required"

# Connector safety policy (engineering bound, not a source fact): the absolute
# coordinate domain a footprint ring may occupy. Mirrors the accepted DCM
# envelope bound; used here (the ring reader) and by the connector's query
# validation, which imports it back.
COORD_ABS_MAX_FT = 5_000_000.0


# ---------------------------------------------------------------------------
# Small numeric / repr helpers (shared with the connector via re-export)
# ---------------------------------------------------------------------------


def _safe_repr(value: object, limit: int = 200) -> str:
    try:
        text = repr(value)
    except (ValueError, RecursionError):
        return f"<unrepresentable {type(value).__name__}>"
    return text if len(text) <= limit else text[:limit] + "...(truncated)"


def _is_real(value: object) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _finite(value: object) -> float | None:
    """A finite float, or None for bools, non-numbers, overflowing ints, inf and NaN."""
    if not _is_real(value):
        return None
    try:
        number = float(value)  # type: ignore[arg-type]
    except OverflowError:
        return None
    return number if math.isfinite(number) else None


def _signed_area(ring: list[list[float]]) -> float:
    """Shoelace area of a CLOSED ring (positive = counterclockwise)."""
    return sum(
        ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1] for i in range(len(ring) - 1)
    ) / 2.0


# ---------------------------------------------------------------------------
# Result contract for one exterior ring and its holes
# ---------------------------------------------------------------------------


@dataclass
class FootprintPart:
    """One exterior ring and its holes, closed and verbatim (exterior clockwise, holes
    counterclockwise, as published). ``area_sq_ft`` is planar EPSG:2263 area net of holes:
    display grade, never a measurement of record."""

    exterior: list[list[float]]
    holes: list[list[list[float]]]
    area_sq_ft: float


# ---------------------------------------------------------------------------
# Geometry policy (FOOTPRINT_GEOMETRY_POLICY) + relation to the query geometry
# ---------------------------------------------------------------------------


def _ring(raw: object) -> list[list[float]] | str:
    """A verbatim closed ring, or the finding code that disqualifies it."""
    if not isinstance(raw, list) or len(raw) < 4:
        return "malformed_ring"
    ring: list[list[float]] = []
    for vertex in raw:
        if not (isinstance(vertex, list) and len(vertex) == 2 and all(map(_is_real, vertex))):
            return "malformed_ring"
        x, y = _finite(vertex[0]), _finite(vertex[1])
        if x is None or y is None:
            return "nonfinite_coordinate"
        if max(abs(x), abs(y)) > COORD_ABS_MAX_FT:
            return "coordinate_out_of_bounds"
        ring.append([x, y])
    if ring[0] != ring[-1]:
        return "unclosed_ring"
    if len({(x, y) for x, y in ring}) < 3:
        return "degenerate_ring"
    if _signed_area(ring) == 0.0:
        # Zero signed area: collinear (degenerate) or a self-crossing ring whose lobes cancel.
        extent = Polygon(ring).convex_hull.area
        return "self_intersecting_ring" if extent > 0.0 else "degenerate_ring"
    return ring


def parse_footprint_geometry(
    esri: object,
) -> tuple[str, list[str], list[FootprintPart], list[str]]:
    """Apply FOOTPRINT_GEOMETRY_POLICY: (status, findings, parts, flags)."""
    if esri is None:
        return GEOMETRY_INVALID, ["null_geometry"], [], []
    rings_raw = esri.get("rings") if isinstance(esri, dict) else None
    if not isinstance(rings_raw, list):
        return GEOMETRY_INVALID, ["not_a_polygon_geometry"], [], []
    if not rings_raw:
        return GEOMETRY_INVALID, ["empty_geometry"], [], []
    checked = [_ring(raw) for raw in rings_raw]
    bad = sorted({r for r in checked if isinstance(r, str)})
    if bad:
        return GEOMETRY_INVALID, bad, [], []
    rings = [r for r in checked if not isinstance(r, str)]
    exteriors = [r for r in rings if _signed_area(r) < 0.0]
    holes = [r for r in rings if _signed_area(r) > 0.0]
    if not exteriors:
        return GEOMETRY_REVIEW_REQUIRED, ["no_clockwise_exterior_ring"], [], []
    shells = [Polygon(r) for r in exteriors]
    owned: list[list[list[list[float]]]] = [[] for _ in exteriors]
    for hole in holes:
        point = Polygon(hole).representative_point()
        containing = [i for i, shell in enumerate(shells) if shell.contains(point)]
        if not containing:
            return GEOMETRY_REVIEW_REQUIRED, ["hole_outside_every_exterior"], [], []
        owned[min(containing, key=lambda i: shells[i].area)].append(hole)
    polygons = [Polygon(ext, owned[i]) for i, ext in enumerate(exteriors)]
    findings: list[str] = []
    for index, poly in enumerate(polygons):
        if not poly.is_valid:
            findings.append(f"invalid_part:{index}:{_safe_repr(explain_validity(poly), 120)}")
    if findings:
        return GEOMETRY_INVALID, findings, [], []
    flags: list[str] = []
    for i in range(len(polygons)):
        for j in range(i + 1, len(polygons)):
            if polygons[i].intersection(polygons[j]).area > 0.0:
                return GEOMETRY_REVIEW_REQUIRED, [f"parts_overlap:{i}:{j}"], [], []
            if polygons[i].intersects(polygons[j]) and "parts_touch" not in flags:
                flags.append("parts_touch")
    if len(polygons) > 1:
        flags.append("multipart")
    if holes:
        flags.append("has_holes")
    parts = [FootprintPart(exteriors[i], owned[i], float(p.area)) for i, p in enumerate(polygons)]
    return GEOMETRY_VALID, [], parts, flags


def classify_query_relation(
    parts: list[FootprintPart], query_shape: BaseGeometry
) -> tuple[str, float]:
    """Exact planar relation of a footprint to the query geometry (no tolerance):
    ``within`` | ``partial_overlap`` (positive-area intersection) | ``boundary_touch``
    (shares only boundary points - e.g. a party wall on the lot line) | ``disjoint_locally``
    (the service matched it, the local 2263 test does not; kept and flagged)."""
    footprint = unary_union([Polygon(p.exterior, p.holes) for p in parts])
    overlap = float(footprint.intersection(query_shape).area)
    if overlap > 0.0 and footprint.within(query_shape):
        return "within", overlap
    if overlap > 0.0:
        return "partial_overlap", overlap
    if footprint.intersects(query_shape):
        return "boundary_touch", 0.0
    return "disjoint_locally", 0.0
