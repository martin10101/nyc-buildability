"""Corner-reach area (M5-T145 PART A): the lot area within a caller-given distance of both
street lines, and of the rest.

A pure, deterministic measurement that stands beside the sibling lot-reach module (M5-T127)
and follows its conventions. It reads only what single-lot site geometry already derives
(``app.spatial.site_geometry``): the prepared tax-map outline in EPSG:2263 feet and the
confirmed street frontages. On a lot whose two confirmed, straight street frontages meet at a
corner it measures:

* the AREA of the part of the outline within the caller's distance of BOTH street lines (the
  corner-lot portion), and
* the AREA of the rest (the interior-lot portion).

MEASUREMENTS ONLY. The module holds no legal threshold and names no legal rule, section or
consequence: the distance is passed in by the caller, and a later caller compares the areas
with whatever the law requires -- that comparison is not this module's work. Like the sibling
lot-reach module, it measures and names no kind of gap. Every value is a site_geometry
:class:`~app.spatial.site_geometry.labels.SourcedValue`: a tax-map area with its basis in plain
words, or unknown (``value`` is None) with a plain reason -- never a zero and never a default. A
genuinely measured rest of 0.0 (the whole lot lies within the distance of both lines) is a known
value, distinct from unknown. Each outcome also carries a fixed, machine-readable ``state`` code,
so a caller need not read the text to branch. It imports nothing from the rule or scenario
engines, nothing from the sibling lot-reach module, and nothing calls it yet.

The corner portion is found by a pure-Python half-plane clip (Sutherland-Hodgman): the outline
is clipped to the points within the caller's distance of street line one, and that result to the
points within the distance of street line two. Each half-plane is convex, so the clip is exact
even for a non-convex outline; the interior portion is the outline's own area minus the corner
portion.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from app.spatial.site_geometry.depth import frontage_bend_deg
from app.spatial.site_geometry.inputs import Point2
from app.spatial.site_geometry.labels import SourcedValue, tax_map_value, unknown_value
from app.spatial.site_geometry.outline import OutlineEdge, PreparedOutline
from app.spatial.site_geometry.parameters import SINGLE_STREET_MAX_BEND_DEG
from app.spatial.site_geometry.rays import unit
from app.spatial.site_geometry.results import (
    FRONTAGE_CONFIRMED,
    RELATION_CORNER,
    STATUS_REFUSED,
    SiteGeometry,
    StreetFrontage,
    StreetRelation,
)

__all__ = [
    "CAUSE_NOT_CONFIRMED",
    "CAUSE_NOT_STRAIGHT",
    "STATE_MEASURED",
    "STATE_MORE_THAN_TWO_STREETS",
    "STATE_NOT_A_CORNER",
    "STATE_NO_CONFIRMED_STREET",
    "STATE_ONE_CONFIRMED_STREET",
    "STATE_OUTLINE_REFUSED",
    "CornerPortionAreas",
    "area_within_distance_of_both",
    "measure_corner_reach_area",
]

# A line is (a point on it, its unit direction) -- the same shape the sibling module measures from.
Line = tuple[Point2, Point2]

# One fixed code for the measured outcome and one distinct code for each unknown state.
STATE_MEASURED = "measured"
STATE_OUTLINE_REFUSED = "outline_refused_or_missing"
STATE_NO_CONFIRMED_STREET = "no_confirmed_straight_frontage"
STATE_ONE_CONFIRMED_STREET = "one_confirmed_straight_frontage"
STATE_MORE_THAN_TWO_STREETS = "more_than_two_confirmed_frontages"
STATE_NOT_A_CORNER = "frontages_do_not_meet_at_a_corner"

# Why a frontage could not seed a street line, so a caller can tell the two causes apart.
CAUSE_NOT_CONFIRMED = "frontage_not_confirmed"
CAUSE_NOT_STRAIGHT = "frontage_not_straight"

# A rest area below zero by more than this share of the outline area is a defect, not rounding.
_REST_NEGATIVE_TOLERANCE_SHARE = 1e-6


@dataclass(frozen=True)
class CornerPortionAreas:
    """The two by-portion areas of a corner lot, measured only.

    ``corner_portion`` is the area within the caller's distance of both street lines;
    ``interior_portion`` is the area of the rest. Each is a
    :class:`~app.spatial.site_geometry.labels.SourcedValue`: a tax-map area, or unknown
    (``value`` is None) with a plain reason. A measured 0.0 (the whole lot lies within the
    distance of both lines) is a known value, distinct from unknown.

    ``state`` is one of the module's ``STATE_*`` codes: the measured outcome, or a distinct code
    for each unknown state. ``frontage_causes`` is a tuple of ``(street name, CAUSE_* code)``
    pairs for every frontage that could not seed a street line, so a caller can tell a frontage
    that is not confirmed from one that is not straight without reading any text.
    """

    corner_portion: SourcedValue
    interior_portion: SourcedValue
    state: str
    frontage_causes: tuple[tuple[str, str], ...] = field(default_factory=tuple)


# --------------------------------------------------------------------------- pure geometry


def _signed_perp(point: Point2, line_point: Point2, line_dir: Point2) -> float:
    """Signed perpendicular offset of ``point`` from the line (point + t * dir), by the 2D
    cross product. Positive on one side of the line, negative on the other."""
    dx, dy = line_dir
    wx, wy = point[0] - line_point[0], point[1] - line_point[1]
    return dx * wy - dy * wx


def _polygon_area(ring: list[Point2]) -> float:
    """Shoelace area of a ring (absolute, so it does not depend on the ring's orientation)."""
    count = len(ring)
    if count < 3:
        return 0.0
    total = 0.0
    for index in range(count):
        x0, y0 = ring[index]
        x1, y1 = ring[(index + 1) % count]
        total += x0 * y1 - x1 * y0
    return abs(total) / 2.0


def _clip_within_distance(ring: list[Point2], line: Line, distance: float) -> list[Point2]:
    """Keep the part of ``ring`` within perpendicular ``distance`` of ``line``, on the side the
    lot lies on (Sutherland-Hodgman clip by one convex half-plane)."""
    point, direction = line
    # The lot lies on one side of its frontage line; the vertex of largest offset names that
    # side, so the clip boundary (distance into the lot) is placed correctly.
    inward = 1.0
    peak = 0.0
    for vertex in ring:
        offset = _signed_perp(vertex, point, direction)
        if abs(offset) > abs(peak):
            peak = offset
    if peak < 0.0:
        inward = -1.0

    def depth(vertex: Point2) -> float:
        # Perpendicular distance into the lot, minus the clip distance: keep where it is <= 0.
        return inward * _signed_perp(vertex, point, direction) - distance

    kept: list[Point2] = []
    count = len(ring)
    for index in range(count):
        start = ring[index]
        end = ring[(index + 1) % count]
        d_start = depth(start)
        d_end = depth(end)
        start_in = d_start <= 0.0
        end_in = d_end <= 0.0
        if start_in and end_in:
            kept.append(end)
        elif start_in and not end_in:
            kept.append(_crossing(start, end, d_start, d_end))
        elif not start_in and end_in:
            kept.append(_crossing(start, end, d_start, d_end))
            kept.append(end)
    return kept


def _crossing(start: Point2, end: Point2, d_start: float, d_end: float) -> Point2:
    """Where the edge start->end crosses the clip boundary (depth == 0)."""
    t = d_start / (d_start - d_end)
    return start[0] + t * (end[0] - start[0]), start[1] + t * (end[1] - start[1])


def _resolve_rest(full: float, corner: float) -> float:
    """The interior-portion area (``full - corner``). The corner is a clipped subset of the
    outline, so the rest is mathematically non-negative: a negative within rounding noise (a tiny
    share of the outline area) is a measured zero, and a larger negative is a defect that raises
    rather than being hidden."""
    rest = full - corner
    if rest < 0.0:
        if -rest <= _REST_NEGATIVE_TOLERANCE_SHARE * full:
            return 0.0
        raise ValueError(
            "the interior portion is negative by more than rounding noise "
            f"({rest:.6f} sq ft of a {full:.2f} sq ft outline): the corner portion cannot "
            "exceed the outline")
    return rest


def area_within_distance_of_both(
    outline_vertices: list[Point2], line1: Line, line2: Line, distance_ft: float,
) -> tuple[float, float]:
    """Return ``(corner_area, rest_area)`` in square feet: the area of ``outline_vertices``
    within ``distance_ft`` of BOTH lines, and the area of the rest. Pure arithmetic on the
    EPSG:2263 outline; no clock, no I/O. A distance of zero or less raises ``ValueError``."""
    if distance_ft <= 0.0:
        raise ValueError("the distance must be greater than zero")
    ring = list(outline_vertices)
    full = _polygon_area(ring)
    clipped = _clip_within_distance(ring, line1, distance_ft)
    clipped = _clip_within_distance(clipped, line2, distance_ft)
    corner = _polygon_area(clipped)
    rest = _resolve_rest(full, corner)
    return corner, rest


# --------------------------------------------------------------------------- site geometry


def _outline_source(geometry: SiteGeometry) -> str:
    """The lot-outline source name recorded on the geometry, for the basis text."""
    provenance = geometry.provenance
    outline_prov = provenance.get("lot_outline") if isinstance(provenance, Mapping) else None
    if isinstance(outline_prov, Mapping):
        name = outline_prov.get("source")
        if isinstance(name, str) and name:
            return name
    return "tax-map"


def _frontage_edges(frontage: StreetFrontage, outline: PreparedOutline) -> list[OutlineEdge]:
    return [outline.edges[index] for index in frontage.edge_indices]


def _street_line(edges: list[OutlineEdge]) -> Line | None:
    """A point on the frontage's street line and its unit direction (the length-weighted mean
    direction of the frontage edges), or None if the edges carry no length."""
    sx = sum(edge.direction[0] * edge.length_ft for edge in edges)
    sy = sum(edge.direction[1] * edge.length_ft for edge in edges)
    direction = unit((sx, sy))
    if direction is None or not edges:
        return None
    return edges[0].start, direction


def _confirmed_straight_line(
    frontage: StreetFrontage, outline: PreparedOutline,
) -> tuple[Line | None, str | None, str | None]:
    """``(line, None, None)`` for a confirmed, straight frontage; else
    ``(None, cause_code, reason)`` -- the same states the sibling lot-reach module refuses a
    street line for, with the cause code so a caller can branch without reading the text."""
    name = frontage.street_name
    if frontage.status != FRONTAGE_CONFIRMED:
        return None, CAUSE_NOT_CONFIRMED, f"the frontage on {name} is not confirmed"
    edges = _frontage_edges(frontage, outline)
    bend = frontage_bend_deg(edges)
    line = _street_line(edges)
    if bend > SINGLE_STREET_MAX_BEND_DEG or line is None:
        return None, CAUSE_NOT_STRAIGHT, (
            f"the frontage on {name} is not straight (its lot lines turn by {bend:.0f} degrees)")
    return line, None, None


def _corner_relation(
    street_keys: set[str], relations: tuple[StreetRelation, ...],
) -> StreetRelation | None:
    for relation in relations:
        pair = {relation.first, relation.second}
        if relation.relation == RELATION_CORNER and pair == street_keys:
            return relation
    return None


def _both_unknown(
    reason: str, state: str, causes: tuple[tuple[str, str], ...] = (),
) -> CornerPortionAreas:
    missing = unknown_value("sq ft", reason)
    return CornerPortionAreas(missing, missing, state, causes)


def measure_corner_reach_area(
    outline: PreparedOutline | None, geometry: SiteGeometry, distance_ft: float,
) -> CornerPortionAreas:
    """Measure the corner-lot and interior-lot portion areas of ``geometry``'s lot: the part of
    the prepared outline within ``distance_ft`` of both confirmed, straight street lines, and
    the rest.

    Both portions are unknown (never a zero) on every state the sibling lot-reach module finds no
    corner for: the outline was refused or missing, no street or only one street has a confirmed
    straight frontage, more than two do, or the two streets do not meet at a corner. Each outcome
    carries a distinct ``STATE_*`` code and, for every frontage that could not seed a street line,
    a ``(street name, CAUSE_*)`` pair. A genuinely measured rest of 0.0 (the whole lot lies within
    ``distance_ft`` of both lines) is a known value. A distance of zero or less raises
    ``ValueError``.
    """
    if distance_ft <= 0.0:
        raise ValueError("the distance must be greater than zero")
    if outline is None or geometry.status == STATUS_REFUSED:
        reason = geometry.refusal_reason or "The lot outline could not be prepared."
        return _both_unknown(reason, STATE_OUTLINE_REFUSED)

    straight: list[tuple[StreetFrontage, Line]] = []
    causes: list[tuple[str, str]] = []
    reasons: list[str] = []
    for frontage in geometry.frontages:
        line, cause, reason = _confirmed_straight_line(frontage, outline)
        if line is not None:
            straight.append((frontage, line))
        elif cause is not None and reason is not None:
            causes.append((frontage.street_name, cause))
            reasons.append(reason)
    cause_pairs = tuple(causes)

    if len(straight) == 0:
        if reasons:
            reason = (f"There is no corner to measure within {distance_ft:.0f} ft of both "
                      "street lines: " + "; ".join(reasons) + ".")
        else:
            reason = ("No street has a confirmed, straight frontage, so there is no corner to "
                      f"measure within {distance_ft:.0f} ft of both street lines.")
        return _both_unknown(reason, STATE_NO_CONFIRMED_STREET, cause_pairs)

    if len(straight) == 1:
        reason = (f"Only {straight[0][0].street_name} has a confirmed, straight frontage, so "
                  f"there is no corner to measure within {distance_ft:.0f} ft of both street "
                  "lines; the outline area is a known number but the corner/interior split is "
                  "not.")
        return _both_unknown(reason, STATE_ONE_CONFIRMED_STREET, cause_pairs)

    if len(straight) > 2:
        reason = ("More than two streets front the lot, so no single corner is measured within "
                  f"{distance_ft:.0f} ft of both street lines.")
        return _both_unknown(reason, STATE_MORE_THAN_TWO_STREETS, cause_pairs)

    (frontage_one, line_one), (frontage_two, line_two) = straight
    relation = _corner_relation({frontage_one.street_key, frontage_two.street_key},
                                geometry.lot_type.relations)
    if relation is None:
        reason = (f"{frontage_one.street_name} and {frontage_two.street_name} front the lot but "
                  f"do not meet at a corner, so there is no corner to measure within "
                  f"{distance_ft:.0f} ft of both street lines.")
        return _both_unknown(reason, STATE_NOT_A_CORNER, cause_pairs)

    corner_area, rest_area = area_within_distance_of_both(
        list(outline.vertices), line_one, line_two, distance_ft)
    source = _outline_source(geometry)
    names = f"{frontage_one.street_name} and {frontage_two.street_name}"
    corner_basis = (f"The area of the part of the {source} outline within {distance_ft:.0f} ft "
                    f"of both the {names} street lines")
    interior_basis = (f"The area of the rest of the {source} outline, beyond {distance_ft:.0f} "
                      f"ft of one of the {names} street lines")
    return CornerPortionAreas(
        tax_map_value(corner_area, "sq ft", corner_basis),
        tax_map_value(rest_area, "sq ft", interior_basis),
        STATE_MEASURED,
        cause_pairs,
    )
