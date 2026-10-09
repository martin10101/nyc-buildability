"""Massing ring preparation + ear-clipping triangulation (M5-T112 split of
:mod:`app.scenario.massing_model`).

One responsibility: turn a raw EPSG:2263 ring into distinct, non-collinear, CCW vertices
and triangulate it with a concave-safe ear-clipping pass under a per-request work budget.
A simple polygon always has an ear (two-ears theorem); a stall means the ring is not
simple and fails closed as a typed :class:`~app.scenario.massing_guards.MassingModelError`.

Public API - :func:`triangulate_polygon` (ring in, prepared ring + CCW triangle indices
out, the same work budget and typed refusals) is the ONE documented reusable entry point
so the later GLB cap-export fix (DB-082 a) can replace its naive vertex-0 fan, which is
wrong for concave (e.g. L-shaped) footprints, with this robust triangulator.

Deterministic and offline: standard library plus the read-only guards module and the B0
outline-vertex cap. No shapely, no numpy, no route, no web, no new dependency.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .massing_guards import (
    MAX_COORD_ABS,
    MassingModelError,
    _is_finite_number,
    _Point,
    _preview,
    _require_raw_vertices_in_nyc_bounds,
)
from .proposal import MAX_OUTLINE_VERTICES

__all__ = [
    "Triangulation",
    "triangulate_polygon",
    "MAX_TRIANGULATION_WORK",
]

#: The grid a renderer should snap to; emitted coordinates are quantised to it so the
#: golden serialization is stable. Metadata, never a legal precision claim.
_QUANT_DECIMALS = 6  # round(ft, 6) == PRECISION_GRID_FT (the emitted frame metadata)

#: Per-request ear-clipping work, in units that upper-bound point-in-triangle tests (a
#: convex 999-vertex ring costs 497,502). Shared by every distinct ring.
MAX_TRIANGULATION_WORK = 2_000_000


def _q(value: float) -> float:
    """Quantise a coordinate to the declared precision grid (deterministic)."""
    return round(float(value), _QUANT_DECIMALS)


def _signed_area(ring: Sequence[_Point]) -> float:
    """Shoelace signed area of a distinct-vertex ring; > 0 for counter-clockwise."""
    total = 0.0
    n = len(ring)
    for i in range(n):
        x0, y0 = ring[i]
        x1, y1 = ring[(i + 1) % n]
        total += x0 * y1 - x1 * y0
    return total / 2.0


def _cross3(a: _Point, b: _Point, c: _Point) -> float:
    """Signed area term of triangle ``a b c``; > 0 for a left (CCW) turn at ``b``."""
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _point_in_triangle(p: _Point, a: _Point, b: _Point, c: _Point) -> bool:
    """True when ``p`` is inside or on the boundary of CCW triangle ``a b c``.
    Boundary-inclusive so a vertex touching an ear edge disqualifies the ear."""
    d1 = _cross3(a, b, p)
    d2 = _cross3(b, c, p)
    d3 = _cross3(c, a, p)
    has_neg = d1 < 0 or d2 < 0 or d3 < 0
    has_pos = d1 > 0 or d2 > 0 or d3 > 0
    return not (has_neg and has_pos)


def _prepare_ring(
    points: Sequence[Sequence[float]], field: str, *, nyc_range_check: bool = False
) -> list[_Point]:
    """Normalise a 2263 ring to distinct, non-collinear, CCW vertices.

    Accepts an open or explicitly-closed ring, drops the closing duplicate, and
    collapses collinear straight vertices (redundant corners on one edge) so ear
    clipping finds a strict-convex ear at every step and the caps and side walls
    share the SAME boundary. Fails closed on a non-finite or over-magnitude
    coordinate, an over-cap count, a duplicate vertex, or fewer than three distinct
    corners.

    When ``nyc_range_check`` is set (the lot path, which B0 never sees), each RAW vertex
    is range-checked against the NYC EPSG:2263 bounds in this parse loop - BEFORE the
    collinear collapse below (DB-069 a) - so an out-of-range collinear spike (e.g. a
    x=2e6 vertex on a straight edge) is refused ``lot_ring_out_of_nyc_bounds`` rather
    than silently collapsed away and never checked. The magnitude bound is checked first
    so a ~1e154 overflow still refuses ``coordinate_out_of_range`` (not mislabelled).
    Footprint / per-level rings are B0-range-checked upstream and pass ``False`` here."""
    if not isinstance(points, (list, tuple)):
        raise MassingModelError(f"{field} must be a list of [x, y] points",
                                reason="invalid_source", field=field)
    if len(points) > MAX_OUTLINE_VERTICES:
        raise MassingModelError(
            f"{field} has {len(points)} vertices, over the cap {MAX_OUTLINE_VERTICES}",
            reason="over_cap_vertices", field=field)

    parsed: list[_Point] = []
    raw: list[_Point] = []
    for idx, pt in enumerate(points):
        if not isinstance(pt, (list, tuple)) or len(pt) != 2:
            raise MassingModelError(f"{field}[{idx}] must be an [x, y] pair",
                                    reason="invalid_source", field=f"{field}[{idx}]")
        x, y = pt[0], pt[1]
        if not _is_finite_number(x) or not _is_finite_number(y):
            raise MassingModelError(
                f"{field}[{idx}] must be a finite [x, y] pair; got {_preview(pt)}",
                reason="non_finite", field=f"{field}[{idx}]")
        if abs(x) > MAX_COORD_ABS or abs(y) > MAX_COORD_ABS:
            raise MassingModelError(
                f"{field}[{idx}] exceeds the coordinate magnitude bound "
                f"{MAX_COORD_ABS:.0f} ft",
                reason="coordinate_out_of_range", field=f"{field}[{idx}]")
        raw.append((x, y))
        parsed.append((_q(x), _q(y)))

    # Lot-only NYC EPSG:2263 range check on the RAW vertices (DB-069 a), AFTER the whole
    # magnitude pass (so a ~1e154 overflow still refuses coordinate_out_of_range first -
    # the accepted M5-T088 precedence) and BEFORE the collinear collapse below (so an
    # out-of-range collinear spike, e.g. x=2e6 on a straight edge, is refused, not
    # silently collapsed away and never seen).
    if nyc_range_check:
        _require_raw_vertices_in_nyc_bounds(raw, field)

    if len(parsed) >= 2 and parsed[0] == parsed[-1]:
        parsed = parsed[:-1]  # drop the explicit closing duplicate
    if len(set(parsed)) != len(parsed):
        raise MassingModelError(
            f"{field} has a duplicate vertex other than the closing vertex",
            reason="self_intersection", field=field)
    if len(parsed) < 3:
        raise MassingModelError(
            f"{field} needs at least 3 distinct vertices; got {len(parsed)}",
            reason="invalid_source", field=field)

    # Orient CCW so triangulation winds toward +z.
    if _signed_area(parsed) < 0:
        parsed.reverse()

    # Collapse collinear straight vertices (redundant on a straight edge).
    ring: list[_Point] = []
    n = len(parsed)
    for i in range(n):
        prev_pt = parsed[(i - 1) % n]
        cur = parsed[i]
        nxt = parsed[(i + 1) % n]
        if _cross3(prev_pt, cur, nxt) == 0.0:
            continue
        ring.append(cur)
    if len(ring) < 3:
        raise MassingModelError(
            f"{field} collapses to fewer than 3 non-collinear corners",
            reason="invalid_source", field=field)
    return ring


class _WorkBudget:
    """A per-request ear-clipping work meter. Units upper-bound point-in-triangle
    tests; overspending is a typed ``triangulation_budget_exceeded`` refusal."""

    __slots__ = ("limit", "remaining")

    def __init__(self, units: int) -> None:
        self.limit = units
        self.remaining = units

    def charge(self, units: int, field: str) -> None:
        self.remaining -= units
        if self.remaining < 0:
            raise MassingModelError(
                f"{field} triangulation exceeds the work budget of {self.limit} units; "
                "refused before the ear scan runs away",
                reason="triangulation_budget_exceeded", field=field)


def _min_ear_clip_work(n: int) -> int:
    """The least :func:`_triangulate` can charge for an ``n``-vertex ring: each of the
    n-3 clips (m = n..4 remaining) examines at least one candidate (1 unit) and scans
    it fully (m-3 units), so sum(m-2) = (n-2)(n-1)/2 - 1. Exact, never an estimate."""
    return (n - 2) * (n - 1) // 2 - 1 if n > 3 else 0


def _triangulate(
    ring: Sequence[_Point], field: str, budget: _WorkBudget | None = None
) -> list[tuple[int, int, int]]:
    """Ear-clipping triangulation of a simple CCW ring (concave-safe).

    Returns index triples into ``ring``, each wound CCW (so a +z-facing cap normal).
    A simple polygon always has an ear (two-ears theorem); a stall means the ring is
    not simple and fails closed as ``self_intersection``. Work is metered by
    ``budget`` (a fresh :data:`MAX_TRIANGULATION_WORK` budget when omitted): one unit
    per candidate, and each convex candidate's worst-case containment scan (m-3
    units) is charged BEFORE that scan runs."""
    n = len(ring)
    if n < 3:
        raise MassingModelError(f"{field} needs at least 3 vertices to triangulate",
                                reason="invalid_source", field=field)
    if n == 3:
        return [(0, 1, 2)]
    if budget is None:
        budget = _WorkBudget(MAX_TRIANGULATION_WORK)

    remaining = list(range(n))
    triangles: list[tuple[int, int, int]] = []
    guard = 0
    guard_max = 2 * n * n + 8
    while len(remaining) > 3 and guard < guard_max:
        guard += 1
        m = len(remaining)
        clipped = False
        for pos in range(m):
            budget.charge(1, field)
            i_prev = remaining[(pos - 1) % m]
            i_cur = remaining[pos]
            i_next = remaining[(pos + 1) % m]
            a, b, c = ring[i_prev], ring[i_cur], ring[i_next]
            if _cross3(a, b, c) <= 0.0:  # reflex or collinear -> not an ear tip
                continue
            budget.charge(m - 3, field)
            if any(
                _point_in_triangle(ring[j], a, b, c)
                for j in remaining
                if j not in (i_prev, i_cur, i_next)
            ):
                continue
            triangles.append((i_prev, i_cur, i_next))
            del remaining[pos]
            clipped = True
            break
        if not clipped:
            break
    if len(remaining) != 3:
        raise MassingModelError(
            f"{field} could not be triangulated; the ring is not a simple polygon",
            reason="self_intersection", field=field)
    triangles.append((remaining[0], remaining[1], remaining[2]))
    return triangles


@dataclass(frozen=True)
class Triangulation:
    """The result of :func:`triangulate_polygon`. ``ring`` is the PREPARED CCW ring
    (distinct, non-collinear vertices); ``triangles`` are CCW index triples INTO ``ring``.

    The caller must use ``ring`` for vertex positions, not the raw input, because
    preparation drops the closing duplicate and collapses collinear vertices, so the
    triangle indices reference the prepared ring, not the original point list."""

    ring: tuple[_Point, ...]
    triangles: tuple[tuple[int, int, int], ...]


def triangulate_polygon(
    points: Sequence[Sequence[float]],
    field: str = "polygon",
    *,
    budget: _WorkBudget | None = None,
) -> Triangulation:
    """Concave-safe ear-clipping triangulation of a simple polygon - the ONE public,
    reusable massing triangulator (M5-T112 / DB-082 a).

    Ring in (an open or explicitly-closed EPSG:2263 point list), prepared ring + CCW
    triangle indices out. Preparation (:func:`_prepare_ring`) drops the closing
    duplicate, collapses exactly-collinear vertices, orients CCW, and fails closed on a
    non-finite / over-magnitude coordinate, a duplicate vertex, or fewer than three
    distinct corners; triangulation (:func:`_triangulate`) then ear-clips under the work
    budget (a fresh :data:`MAX_TRIANGULATION_WORK` budget when ``budget`` is omitted) and
    fails closed on a non-simple ring (``self_intersection``) or an over-budget scan
    (``triangulation_budget_exceeded``). Every refusal is a typed
    :class:`~app.scenario.massing_guards.MassingModelError`; nothing is clipped or
    repaired. The triangle-area sum equals the polygon area within floating tolerance.

    Intended so the GLB cap export (DB-082 a) reuses this instead of a naive vertex-0
    fan (wrong for concave, e.g. L-shaped, footprints). The lot-only NYC range check is
    deliberately NOT exposed here: a footprint reaching the exporter is already
    B0-range-checked, and the check belongs to the lot build path alone."""
    ring = _prepare_ring(points, field)
    if budget is None:
        budget = _WorkBudget(MAX_TRIANGULATION_WORK)
    triangles = _triangulate(ring, field, budget)
    return Triangulation(ring=tuple(ring), triangles=tuple(triangles))
