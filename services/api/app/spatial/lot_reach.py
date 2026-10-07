"""Lot reach: how far a lot reaches from its street lines and its corner point (M5-T127).

A pure, deterministic measurement on what single-lot site geometry already derives
(``app.spatial.site_geometry``): the prepared outline in EPSG:2263 feet, the confirmed
street frontages and the corner relation between two of them. It measures:

* for each confirmed, straight street frontage, the farthest perpendicular distance of any
  point of the outline from that frontage's street line;
* where exactly two confirmed, straight frontage streets meet at a lot corner, the point
  where the two street lines cross, the angle between them there, and the farthest
  straight-line distance of any point of the outline from that point.

MEASUREMENTS ONLY. The module holds no legal threshold and names no legal rule or
consequence: it reports distances and an angle, and a later caller compares them with
whatever the law requires -- that comparison is not this module's work. Every value is a
site_geometry :class:`~app.spatial.site_geometry.labels.SourcedValue`: a tax-map measurement
with its basis in plain words, or unknown (``value`` is None) with a plain reason -- never a
zero and never a default. It imports nothing from the rule or scenario engines, and nothing
calls it yet.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass

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

__all__ = ["CornerReach", "LotReach", "StreetLineReach", "measure_lot_reach"]

# Two street lines running more nearly parallel than this never give a single crossing point.
_PARALLEL_EPS = 1e-12
# Corner-point precision: the MapPLUTO connector's canonical coordinate precision, as labels.py.
_COORD_DECIMALS = 2


@dataclass(frozen=True)
class StreetLineReach:
    """How far the lot reaches, measured perpendicular to one street's frontage line.

    ``reach`` is the farthest perpendicular distance of any point of the outline from that
    street line (unknown when the frontage is not confirmed or not straight).
    """

    street_key: str
    street_name: str
    reach: SourcedValue


@dataclass(frozen=True)
class CornerReach:
    """Where exactly two confirmed, straight frontage streets meet at a lot corner.

    ``corner_point`` is the (x, y) in EPSG:2263 feet where the two street lines cross;
    ``angle`` is the angle between the two street lines there (carried from the site_geometry
    corner relation); ``reach`` is the farthest straight-line distance of any point of the
    outline from ``corner_point``. All three are unknown, ``corner_point`` is None and the two
    street names are None when there is no such corner (no confirmed straight pair, streets on
    opposite sides, more than two streets, or no usable outline).
    """

    first_street: str | None
    second_street: str | None
    angle: SourcedValue
    corner_point: Point2 | None
    reach: SourcedValue


@dataclass(frozen=True)
class LotReach:
    """The reach measurements for one lot: one per street frontage, plus the corner."""

    street_lines: tuple[StreetLineReach, ...]
    corner: CornerReach


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


def _street_line(edges: list[OutlineEdge]) -> tuple[Point2, Point2] | None:
    """A point on the frontage's street line and its unit direction (the length-weighted mean
    direction of the frontage edges), or None if the edges carry no length."""
    sx = sum(edge.direction[0] * edge.length_ft for edge in edges)
    sy = sum(edge.direction[1] * edge.length_ft for edge in edges)
    direction = unit((sx, sy))
    if direction is None or not edges:
        return None
    return edges[0].start, direction


def _farthest_perpendicular(vertices, point: Point2, direction: Point2) -> float:
    """Largest perpendicular distance of any vertex from the line through ``point`` along the
    unit vector ``direction``."""
    px, py = point
    dx, dy = direction
    return max(abs((vx - px) * dy - (vy - py) * dx) for vx, vy in vertices)


def _farthest_distance(vertices, point: Point2) -> float:
    return max(math.dist(vertex, point) for vertex in vertices)


def _line_crossing(p1: Point2, d1: Point2, p2: Point2, d2: Point2) -> Point2 | None:
    """The single point where line (``p1`` along ``d1``) meets line (``p2`` along ``d2``),
    or None when they are (near) parallel."""
    denom = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(denom) <= _PARALLEL_EPS:
        return None
    wx, wy = p2[0] - p1[0], p2[1] - p1[1]
    t = (wx * d2[1] - wy * d2[0]) / denom
    return p1[0] + d1[0] * t, p1[1] + d1[1] * t


def _rounded(point: Point2) -> Point2:
    return round(point[0], _COORD_DECIMALS), round(point[1], _COORD_DECIMALS)


def _no_corner(reason: str) -> CornerReach:
    return CornerReach(None, None, unknown_value("degrees", reason), None,
                       unknown_value("ft", reason))


def _street_line_reach(
    frontage: StreetFrontage, outline: PreparedOutline, source: str,
) -> StreetLineReach:
    """The reach from one street's frontage line (unknown when it is not a single straight
    line to measure from)."""
    name = frontage.street_name
    basis = (f"The farthest perpendicular distance of any point of the {source} outline from "
             f"the {name} street line")
    if frontage.status != FRONTAGE_CONFIRMED:
        return StreetLineReach(frontage.street_key, name, unknown_value(
            "ft", f"The frontage on {name} is not confirmed, so its street line is not "
            "settled.", basis))
    edges = _frontage_edges(frontage, outline)
    bend = frontage_bend_deg(edges)
    line = _street_line(edges)
    if bend > SINGLE_STREET_MAX_BEND_DEG or line is None:
        return StreetLineReach(frontage.street_key, name, unknown_value(
            "ft", f"The frontage on {name} is not straight (its lot lines turn by {bend:.0f} "
            "degrees), so it has no single street line to measure from.", basis))
    point, direction = line
    reach = _farthest_perpendicular(outline.vertices, point, direction)
    return StreetLineReach(frontage.street_key, name, tax_map_value(reach, "ft", basis))


def _corner_relation(
    streets: set[str], relations: tuple[StreetRelation, ...],
) -> StreetRelation | None:
    for relation in relations:
        if relation.relation == RELATION_CORNER and {relation.first, relation.second} == streets:
            return relation
    return None


def _corner_reach(
    street_lines: tuple[StreetLineReach, ...], outline: PreparedOutline,
    geometry: SiteGeometry, source: str,
) -> CornerReach:
    """The corner measurements, measured only where exactly two confirmed, straight frontage
    streets meet at a lot corner."""
    measured = [line for line in street_lines if line.reach.known]
    if len(measured) == 0:
        return _no_corner("No street has a confirmed, straight frontage, so there is no corner "
                          "point.")
    if len(measured) == 1:
        return _no_corner(f"Only {measured[0].street_name} has a confirmed, straight frontage, "
                          "so there is no corner point.")
    if len(measured) > 2:
        return _no_corner("More than two streets front the lot, so no single corner point is "
                          "measured.")
    first, second = measured
    relation = _corner_relation({first.street_key, second.street_key},
                                geometry.lot_type.relations)
    if relation is None:
        return _no_corner(f"{first.street_name} and {second.street_name} front the lot but do "
                          "not meet at a corner.")
    frontage_one = geometry.frontage(first.street_key)
    frontage_two = geometry.frontage(second.street_key)
    line_one = _street_line(_frontage_edges(frontage_one, outline)) if frontage_one else None
    line_two = _street_line(_frontage_edges(frontage_two, outline)) if frontage_two else None
    point = (_line_crossing(line_one[0], line_one[1], line_two[0], line_two[1])
             if line_one and line_two else None)
    if point is None:
        return _no_corner(f"The {first.street_name} and {second.street_name} street lines do "
                          "not cross at a single point.")
    names = f"{relation.first} and {relation.second}"
    angle_basis = (f"The angle between the {names} street lines where they meet, carried from "
                   "the site-geometry corner relation")
    reach_basis = (f"The farthest straight-line distance of any point of the {source} outline "
                   f"from the point where the {names} street lines meet")
    angle = (tax_map_value(relation.angle_deg, "degrees", angle_basis)
             if relation.angle_deg is not None
             else unknown_value("degrees", "The corner angle was not derived.", angle_basis))
    reach = tax_map_value(_farthest_distance(outline.vertices, point), "ft", reach_basis)
    return CornerReach(relation.first, relation.second, angle, _rounded(point), reach)


def measure_lot_reach(outline: PreparedOutline | None, geometry: SiteGeometry) -> LotReach:
    """Measure how far ``geometry``'s lot reaches from each confirmed, straight street
    frontage line and, where exactly two such frontages meet, from their corner point.

    ``outline`` is the prepared tax-map outline the geometry was derived from (both are built
    from the same lot). When the outline was refused there is nothing to measure: every value
    is unknown with the refusal reason, never a zero.
    """
    if outline is None or geometry.status == STATUS_REFUSED:
        reason = geometry.refusal_reason or "The lot outline could not be prepared."
        return LotReach((), _no_corner(reason))
    source = _outline_source(geometry)
    street_lines = tuple(_street_line_reach(frontage, outline, source)
                         for frontage in geometry.frontages)
    corner = _corner_reach(street_lines, outline, geometry, source)
    return LotReach(street_lines, corner)
