"""Geometric lot type from the outline: corner / interior / through / unknown (B-03, §4).

THE TEST (stated; not a Zoning Resolution determination - the ZR 12-10 definitions are
not snapshotted in this repository, so a qualified reviewer maps this to the legal terms):

* unknown - the street data is incomplete, a mapped street crosses the lot, any edge is
  uncertain, no street is fronted, a frontage bends, or any pair of fronted streets is
  neither a clear corner nor clearly opposite. The reason is always given.
* interior - frontage on exactly one street.
* corner - frontage on two or more streets, and at least one pair of them meets at a lot
  corner (their frontage edges share a vertex) whose interior angle lies in the
  clear-corner range ``CORNER_ANGLE_MIN_DEG``..``CORNER_ANGLE_MAX_DEG``.
* through - frontage on exactly two streets on opposite sides (outward directions at least
  ``THROUGH_MIN_NORMAL_ANGLE_DEG`` apart) that do not meet at a lot corner.
"""

from __future__ import annotations

import math
from itertools import combinations

from .depth import frontage_bend_deg, mean_outward_normal
from .labels import LABEL_TAX_MAP, LABEL_UNKNOWN
from .outline import OutlineEdge, PreparedOutline
from .parameters import (
    CORNER_ANGLE_MAX_DEG,
    CORNER_ANGLE_MIN_DEG,
    SINGLE_STREET_MAX_BEND_DEG,
    THROUGH_MIN_NORMAL_ANGLE_DEG,
)
from .rays import vector_angle_deg
from .results import (
    EDGE_UNCERTAIN,
    LOT_TYPE_CORNER,
    LOT_TYPE_INTERIOR,
    LOT_TYPE_THROUGH,
    LOT_TYPE_UNKNOWN,
    RELATION_CORNER,
    RELATION_THROUGH,
    RELATION_UNCLEAR,
    EdgeFinding,
    LotType,
    StreetRelation,
)

__all__ = ["classify_lot_type", "interior_angle_deg"]

BASIS = (
    "Geometric test on the tax-map outline and City Map street center lines "
    "(app.spatial.site_geometry.lot_type); not a Zoning Resolution determination"
)


def _unknown(reason: str, streets: tuple[str, ...] = (), relations=()) -> LotType:
    return LotType(LOT_TYPE_UNKNOWN, LABEL_UNKNOWN, BASIS, reason, streets, tuple(relations))


def interior_angle_deg(outline: PreparedOutline, vertex_index: int) -> float:
    """Interior angle of the counterclockwise outline at one vertex, 0..360 degrees."""
    count = len(outline.vertices)
    prev = outline.vertices[vertex_index - 1]
    here = outline.vertices[vertex_index]
    nxt = outline.vertices[(vertex_index + 1) % count]
    din = (here[0] - prev[0], here[1] - prev[1])
    dout = (nxt[0] - here[0], nxt[1] - here[1])
    turn = math.degrees(math.atan2(din[0] * dout[1] - din[1] * dout[0],
                                   din[0] * dout[0] + din[1] * dout[1]))
    return 180.0 - turn


def _shared_vertices(first: list[OutlineEdge], second: list[OutlineEdge], count: int):
    """Vertices where an edge of one street's frontage meets an edge of the other's."""
    shared = set()
    for a in first:
        for b in second:
            if (a.index + 1) % count == b.index:
                shared.add(b.index)
            if (b.index + 1) % count == a.index:
                shared.add(a.index)
    return sorted(shared)


def _relation(s1, s2, edges_by_street, outline: PreparedOutline) -> StreetRelation:
    first, second = edges_by_street[s1], edges_by_street[s2]
    shared = _shared_vertices(first, second, len(outline.edges))
    if shared:
        angles = [interior_angle_deg(outline, vertex) for vertex in shared]
        if all(CORNER_ANGLE_MIN_DEG <= angle <= CORNER_ANGLE_MAX_DEG for angle in angles):
            angle = round(angles[0], 1)
            return StreetRelation(s1, s2, RELATION_CORNER, angle,
                                  f"{s1} and {s2} meet at a lot corner of {angle} degrees")
        worst = max(angles, key=lambda a: abs(a - 90.0))
        return StreetRelation(
            s1, s2, RELATION_UNCLEAR, round(worst, 1),
            f"{s1} and {s2} meet at a lot corner of {worst:.0f} degrees, outside the "
            f"clear-corner range {CORNER_ANGLE_MIN_DEG:.0f}-{CORNER_ANGLE_MAX_DEG:.0f}",
        )
    n1, n2 = mean_outward_normal(first), mean_outward_normal(second)
    apart = vector_angle_deg(n1, n2) if n1 and n2 else 0.0
    if apart >= THROUGH_MIN_NORMAL_ANGLE_DEG:
        return StreetRelation(s1, s2, RELATION_THROUGH, round(apart, 1),
                              f"{s1} and {s2} are on opposite sides of the lot")
    return StreetRelation(
        s1, s2, RELATION_UNCLEAR, round(apart, 1),
        f"{s1} and {s2} frontages neither meet at a lot corner nor face opposite ways",
    )


def classify_lot_type(
    findings: tuple[EdgeFinding, ...],
    outline: PreparedOutline,
    blockers: list[str],
) -> LotType:
    """``blockers`` are reasons found upstream (incomplete street data, a street crossing
    the lot); any one of them leaves the type unknown."""
    if blockers:
        return _unknown(" ".join(blockers))
    uncertain = [f for f in findings if f.verdict == EDGE_UNCERTAIN]
    if uncertain:
        parts = [f"lot line {f.index + 1} ({f.length_ft:.2f} ft): " + "; ".join(f.reasons)
                 for f in uncertain]
        return _unknown("Some lot lines could not be matched to a street. " + " | ".join(parts))
    edges_by_street: dict[str, list[OutlineEdge]] = {}
    for finding in findings:
        if finding.street_key is not None:
            edges_by_street.setdefault(finding.street_key, []).append(
                outline.edges[finding.index])
    streets = tuple(sorted(edges_by_street))
    if not streets:
        return _unknown(
            "No street frontage was found. The lot may have no street frontage, or a street "
            "may be missing from the city street data."
        )
    for street, edges in edges_by_street.items():
        bend = frontage_bend_deg(edges)
        if bend > SINGLE_STREET_MAX_BEND_DEG:
            return _unknown(f"The frontage on {street} is not straight (its lot lines turn "
                            f"by {bend:.0f} degrees).", streets)
    if len(streets) == 1:
        return LotType(LOT_TYPE_INTERIOR, LABEL_TAX_MAP, BASIS, None, streets)
    relations = [_relation(a, b, edges_by_street, outline) for a, b in combinations(streets, 2)]
    unclear = [r.reason for r in relations if r.relation == RELATION_UNCLEAR]
    if unclear:
        return _unknown("; ".join(unclear) + ".", streets, relations)
    if any(r.relation == RELATION_CORNER for r in relations):
        return LotType(LOT_TYPE_CORNER, LABEL_TAX_MAP, BASIS, None, streets, tuple(relations))
    if len(streets) == 2:
        return LotType(LOT_TYPE_THROUGH, LABEL_TAX_MAP, BASIS, None, streets, tuple(relations))
    return _unknown("Three or more streets face the lot and none meet at a corner.",
                    streets, relations)
