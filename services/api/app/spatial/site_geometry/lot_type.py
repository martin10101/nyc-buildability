"""Geometric lot type from the outline: corner / interior / through / unknown (B-03, §4).

THE TEST (stated; not a Zoning Resolution determination - the 12-10 snapshot in this
repository holds only the wide/narrow street text, not the corner / through / interior lot
definitions, so a qualified reviewer maps this to the legal terms). For one set of fronting
edges:

* interior - frontage on exactly one street, straight within ``SINGLE_STREET_MAX_BEND_DEG``;
* corner - frontage on two or more streets, and at least one pair meets at a lot corner (their
  frontage edges share a vertex) whose interior angle lies in the clear-corner range
  ``CORNER_ANGLE_MIN_DEG``..``CORNER_ANGLE_MAX_DEG``;
* through - frontage on exactly two streets on opposite sides (outward directions at least
  ``THROUGH_MIN_NORMAL_ANGLE_DEG`` apart) that do not meet at a lot corner;
* otherwise unknown.

UNCERTAIN EDGES. Each uncertain edge may front nothing or any street it may face. The type is
evaluated under every such reading (at most ``MAX_LOT_TYPE_READINGS``). It is stated only when
every reading gives the same known type - the classification then does not depend on any
margin - and the uncertain edges are listed as ``unconfirmed_lot_lines``. Otherwise it is
unknown with ``REASON_DEPENDS_ON_UNCERTAIN_LOT_LINES``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import combinations, product

from .depth import frontage_bend_deg, mean_outward_normal
from .labels import LABEL_TAX_MAP, LABEL_UNKNOWN
from .outline import OutlineEdge, PreparedOutline
from .parameters import (
    CORNER_ANGLE_MAX_DEG,
    CORNER_ANGLE_MIN_DEG,
    MAX_LOT_TYPE_READINGS,
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

__all__ = [
    "BASIS",
    "REASON_DEPENDS_ON_UNCERTAIN_LOT_LINES",
    "REASON_FRONTAGE_NOT_STRAIGHT",
    "REASON_NO_STREET_FRONTAGE",
    "REASON_OUTLINE_REFUSED",
    "REASON_STREET_CROSSES_LOT",
    "REASON_STREET_DATA_INCOMPLETE",
    "REASON_TOO_MANY_READINGS",
    "REASON_UNCLEAR_STREET_PAIR",
    "classify_lot_type",
    "interior_angle_deg",
]

BASIS = (
    "Geometric test on the tax-map outline and City Map street center lines "
    "(app.spatial.site_geometry.lot_type); not a Zoning Resolution determination"
)

# Machine-readable reasons for an unknown lot type (LotType.reason_code).
REASON_OUTLINE_REFUSED = "outline_refused"
REASON_STREET_DATA_INCOMPLETE = "street_data_incomplete"
REASON_STREET_CROSSES_LOT = "street_crosses_lot"
REASON_DEPENDS_ON_UNCERTAIN_LOT_LINES = "depends_on_uncertain_lot_lines"
REASON_TOO_MANY_READINGS = "too_many_uncertain_readings"
REASON_NO_STREET_FRONTAGE = "no_street_frontage"
REASON_FRONTAGE_NOT_STRAIGHT = "frontage_not_straight"
REASON_UNCLEAR_STREET_PAIR = "unclear_street_pair"


@dataclass(frozen=True)
class _Reading:
    kind: str
    reason: str | None
    reason_code: str | None
    streets: tuple[str, ...]
    relations: tuple[StreetRelation, ...] = ()


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


def _classify(fronting: dict[int, str], outline: PreparedOutline) -> _Reading:
    """Lot type for one reading: edge index -> street it fronts."""
    edges_by_street: dict[str, list[OutlineEdge]] = {}
    for index in sorted(fronting):
        edges_by_street.setdefault(fronting[index], []).append(outline.edges[index])
    streets = tuple(sorted(edges_by_street))
    if not streets:
        return _Reading(LOT_TYPE_UNKNOWN, (
            "No street frontage was found. The lot may have no street frontage, or a street "
            "may be missing from the city street data."), REASON_NO_STREET_FRONTAGE, ())
    for street, edges in edges_by_street.items():
        bend = frontage_bend_deg(edges)
        if bend > SINGLE_STREET_MAX_BEND_DEG:
            return _Reading(LOT_TYPE_UNKNOWN, (
                f"The frontage on {street} is not straight (its lot lines turn by "
                f"{bend:.0f} degrees)."), REASON_FRONTAGE_NOT_STRAIGHT, streets)
    if len(streets) == 1:
        return _Reading(LOT_TYPE_INTERIOR, None, None, streets)
    relations = tuple(_relation(a, b, edges_by_street, outline)
                      for a, b in combinations(streets, 2))
    unclear = [r.reason for r in relations if r.relation == RELATION_UNCLEAR]
    if unclear:
        return _Reading(LOT_TYPE_UNKNOWN, "; ".join(unclear) + ".", REASON_UNCLEAR_STREET_PAIR,
                        streets, relations)
    if any(r.relation == RELATION_CORNER for r in relations):
        return _Reading(LOT_TYPE_CORNER, None, None, streets, relations)
    if len(streets) == 2:
        return _Reading(LOT_TYPE_THROUGH, None, None, streets, relations)
    return _Reading(LOT_TYPE_UNKNOWN, "Three or more streets face the lot and none meet at a "
                    "corner.", REASON_UNCLEAR_STREET_PAIR, streets, relations)


def _unknown(reason: str, code: str, reading: _Reading | None = None, lines=()) -> LotType:
    streets = reading.streets if reading else ()
    relations = reading.relations if reading else ()
    return LotType(LOT_TYPE_UNKNOWN, LABEL_UNKNOWN, BASIS, reason, streets, relations, code,
                   tuple(lines))


def _describe(uncertain: list[EdgeFinding]) -> str:
    return " | ".join(f"lot line {f.index + 1} ({f.length_ft:.2f} ft): " + "; ".join(f.reasons)
                      for f in uncertain)


def classify_lot_type(
    findings: tuple[EdgeFinding, ...],
    outline: PreparedOutline,
    incomplete: tuple[str, ...] = (),
    crossings: tuple[str, ...] = (),
) -> LotType:
    """``incomplete`` (the street data may miss a street) and ``crossings`` (a mapped street
    runs through the lot) come from ``street_data``; any one leaves the type unknown."""
    if incomplete:
        return _unknown(" ".join(incomplete), REASON_STREET_DATA_INCOMPLETE)
    if crossings:
        return _unknown(" ".join(crossings), REASON_STREET_CROSSES_LOT)
    confirmed = {f.index: f.street_key for f in findings if f.street_key is not None}
    uncertain = [f for f in findings if f.verdict == EDGE_UNCERTAIN]
    options = [(None, *f.candidate_streets) for f in uncertain]
    if math.prod(len(o) for o in options) > MAX_LOT_TYPE_READINGS:
        return _unknown("Too many lot lines are uncertain to compare every reading. "
                        + _describe(uncertain), REASON_TOO_MANY_READINGS,
                        lines=[f.index for f in uncertain])
    base = _classify(confirmed, outline)
    kinds = {base.kind}
    for choice in product(*options):
        fronting = dict(confirmed)
        fronting.update({f.index: key for f, key in zip(uncertain, choice, strict=True) if key})
        kinds.add(_classify(fronting, outline).kind)
    lines = tuple(f.index for f in uncertain)
    if len(kinds) > 1:
        possible = ", ".join(sorted(kinds - {LOT_TYPE_UNKNOWN}))
        if LOT_TYPE_UNKNOWN in kinds:
            possible += " or undetermined"
        return _unknown(
            "The lot type depends on lot lines that could not be matched to a street "
            f"(possible types: {possible}). " + _describe(uncertain),
            REASON_DEPENDS_ON_UNCERTAIN_LOT_LINES, base, lines)
    if base.kind == LOT_TYPE_UNKNOWN:
        extra = (" Uncertain lot lines: " + _describe(uncertain)) if uncertain else ""
        return _unknown((base.reason or "") + extra,
                        base.reason_code or REASON_NO_STREET_FRONTAGE, base, lines)
    return LotType(base.kind, LABEL_TAX_MAP, BASIS, None, base.streets, base.relations, None,
                   lines)
