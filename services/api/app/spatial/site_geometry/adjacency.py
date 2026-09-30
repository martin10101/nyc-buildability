"""Street-adjacency test for each outline edge (queue item B-03, plan §4 frontage).

THE TEST (stated, conservative). From evenly spaced points along an edge, look straight
out (along the edge's outward normal) up to ``SEARCH_RADIUS_FT`` and take the first street
center line crossed. A point MATCHES street S when all of these hold:

* the lot itself does not lie between the point and the center line;
* S has a plain numeric mapped width w, and the distance d to its center line is within
  ``STREET_LINE_MATCH_TOLERANCE_FT`` of w/2 (the lot line sits on the street line);
* S's center line runs within ``PARALLEL_MAX_ANGLE_DEG`` of the edge;
* S is a plain mapped street (``status_ok``).

A point is CLEAR when no center line is crossed within the radius, the lot itself is in
the way, the center line crosses at more than ``STREET_ACROSS_ANGLE_DEG`` (the street runs
across the view, not along the lot line), or d > w/2 + ``NOT_FRONTING_MARGIN_FT``. Every
other point is UNCERTAIN.

An edge FRONTS S only when every point matches S; it has NO STREET only when every point
is clear; otherwise it is uncertain and the reasons are kept. Unknown is never forced.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .inputs import Point2, StreetCenterline
from .outline import OutlineEdge, PreparedOutline
from .parameters import (
    NOT_FRONTING_MARGIN_FT,
    PARALLEL_MAX_ANGLE_DEG,
    SEARCH_RADIUS_FT,
    STREET_ACROSS_ANGLE_DEG,
    STREET_LINE_MATCH_TOLERANCE_FT,
)
from .rays import line_angle_deg, ray_segment_distance, sample_points, unit
from .results import EDGE_FRONTS, EDGE_NO_STREET, EDGE_UNCERTAIN, EdgeFinding

__all__ = ["classify_edges", "mapped_width_ft"]

_PLAIN_NUMBER_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*$")

_MATCH = "match"
_CLEAR = "clear"
_UNCERTAIN = "uncertain"


def mapped_width_ft(raw: str | None) -> float | None:
    """The DCM ``Streetwidth`` text as feet, only when it is one plain positive number.

    Ranges, inequalities and prose ("varies", "Unknown") give None: the street line cannot
    be placed, so a nearby street stays uncertain (never guessed).
    """
    if not isinstance(raw, str):
        return None
    match = _PLAIN_NUMBER_RE.match(raw)
    if match is None:
        return None
    value = float(match.group(1))
    return value if value > 0.0 else None


@dataclass(frozen=True)
class _Piece:
    street: StreetCenterline
    a: Point2
    b: Point2
    direction: Point2


@dataclass(frozen=True)
class _Sample:
    kind: str
    street: StreetCenterline | None = None
    gap_ft: float | None = None
    code: str | None = None
    worst: float = 0.0


def _pieces(streets: tuple[StreetCenterline, ...]) -> list[_Piece]:
    pieces = []
    for street in streets:
        for path in street.paths:
            for a, b in zip(path, path[1:], strict=False):
                direction = unit((b[0] - a[0], b[1] - a[1]))
                if direction is not None:
                    pieces.append(_Piece(street, a, b, direction))
    return pieces


def _nearest(origin, normal, pieces, radius):
    best_t, best_piece = None, None
    for piece in pieces:
        t = ray_segment_distance(origin, normal, piece.a, piece.b, radius)
        if t is not None and (best_t is None or t < best_t):
            best_t, best_piece = t, piece
    return best_t, best_piece


def _lot_in_the_way(origin, normal, edge: OutlineEdge, outline: PreparedOutline, reach):
    for other in outline.edges:
        if other.index != edge.index:
            if ray_segment_distance(origin, normal, other.start, other.end, reach) is not None:
                return True
    return False


def _judge_sample(origin, edge, outline, pieces) -> _Sample:
    distance, piece = _nearest(origin, edge.outward_normal, pieces, SEARCH_RADIUS_FT)
    if piece is None or _lot_in_the_way(origin, edge.outward_normal, edge, outline, distance):
        return _Sample(_CLEAR)
    street = piece.street
    angle = line_angle_deg(edge.direction, piece.direction)
    if angle > STREET_ACROSS_ANGLE_DEG:
        return _Sample(_CLEAR)
    width = mapped_width_ft(street.mapped_width_raw)
    if width is None:
        return _Sample(_UNCERTAIN, street, None, "width")
    gap = distance - width / 2.0
    if gap > NOT_FRONTING_MARGIN_FT:
        return _Sample(_CLEAR)
    if not street.status_ok:
        return _Sample(_UNCERTAIN, street, gap, "status")
    if gap < -STREET_LINE_MATCH_TOLERANCE_FT:
        return _Sample(_UNCERTAIN, street, gap, "inside", -gap)
    if gap > STREET_LINE_MATCH_TOLERANCE_FT:
        return _Sample(_UNCERTAIN, street, gap, "between", gap)
    if angle > PARALLEL_MAX_ANGLE_DEG:
        return _Sample(_UNCERTAIN, street, gap, "angle", angle)
    return _Sample(_MATCH, street, gap)


def _name(street: StreetCenterline) -> str:
    return street.street_name or street.street_key


def _reason(code: str, street: StreetCenterline, worst: float) -> str:
    name = _name(street)
    if code == "width":
        return (
            f"{name}: the mapped width {street.mapped_width_raw!r} is not a single number, "
            "so its street line cannot be placed"
        )
    if code == "status":
        return f"{name}: {street.status_note or 'not a plain mapped street'}"
    if code == "inside":
        return f"{name}: this lot line lies up to {worst:.1f} ft inside the mapped street"
    if code == "between":
        return (
            f"{name}: this lot line is up to {worst:.1f} ft from the street line - too far "
            "to be frontage, too close to rule it out"
        )
    return f"{name}: the street runs at up to {worst:.0f} degrees to this lot line"


def _uncertain_reasons(samples: list[_Sample], weights: list[float], length: float):
    worst: dict[tuple[str, str], tuple[float, StreetCenterline]] = {}
    for sample in samples:
        if sample.kind == _UNCERTAIN and sample.street is not None and sample.code:
            key = (sample.street.street_key, sample.code)
            if key not in worst or sample.worst > worst[key][0]:
                worst[key] = (sample.worst, sample.street)
    reasons = [_reason(code, street, value) for (_, code), (value, street) in worst.items()]
    matched = {s.street.street_key: s.street for s in samples if s.kind == _MATCH and s.street}
    if len(matched) > 1:
        reasons.append("this lot line faces more than one street")
    for key, street in matched.items():
        share = sum(w for s, w in zip(samples, weights, strict=True)
                    if s.kind == _MATCH and s.street and s.street.street_key == key) / length
        reasons.append(f"{_name(street)}: the street line runs along only {share:.0%} of it")
    return tuple(sorted(set(reasons)))


def _edge_finding(edge: OutlineEdge, outline: PreparedOutline, pieces) -> EdgeFinding:
    points = sample_points(edge)
    samples = [_judge_sample(point, edge, outline, pieces) for point, _ in points]
    weights = [weight for _, weight in points]
    matches = [s for s in samples if s.kind == _MATCH and s.street is not None]
    keys = {s.street.street_key for s in matches}
    share = round(len(matches) / len(samples), 4)
    gaps = [abs(s.gap_ft) for s in matches if s.gap_ft is not None]
    max_gap = round(max(gaps), 2) if gaps else None
    object_ids = tuple(sorted({s.street.object_id for s in matches
                               if s.street.object_id is not None}))
    length = round(edge.length_ft, 2)
    if len(matches) == len(samples) and len(keys) == 1:
        key = next(iter(keys))
        return EdgeFinding(edge.index, length, EDGE_FRONTS, key, (key,), (), share, max_gap,
                           object_ids)
    if all(s.kind == _CLEAR for s in samples):
        return EdgeFinding(edge.index, length, EDGE_NO_STREET, None, (), (), 0.0, None)
    candidates = tuple(sorted({s.street.street_key for s in samples if s.street is not None}))
    reasons = _uncertain_reasons(samples, weights, edge.length_ft)
    return EdgeFinding(edge.index, length, EDGE_UNCERTAIN, None, candidates, reasons, share,
                       max_gap, object_ids)


def classify_edges(
    outline: PreparedOutline, streets: tuple[StreetCenterline, ...]
) -> tuple[EdgeFinding, ...]:
    """One finding per outline edge, in ring order."""
    pieces = _pieces(streets)
    return tuple(_edge_finding(edge, outline, pieces) for edge in outline.edges)
