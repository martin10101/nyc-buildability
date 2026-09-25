"""M5-T082 (D-087 3D-1): the deterministic massing truth object.

The canonical scenario-geometry object of ``docs/3D_MASSING_ENGINE_ARCHITECTURE.md``
(sections 2-4 and 10, subset). It is the SERVER-SIDE truth every 3D view and the
CAD export consume; a renderer draws it and never invents it (section 2). Nothing
here is a rule and nothing is a city record.

Honesty (D-076-R002 / D-083 vocabulary): a building derived from an architect
proposal is ``proposed`` ("Proposed - not a city record"); a building derived from
the max-envelope generator is a ``generated_option`` ("Generated building option").
No output is ever labelled a city record, a rule, or an achievable / legal value,
and no legal conclusion is drawn. The two source labels are the ONLY building
labels this module emits.

What it builds, from (a) the canonical EPSG:2263 lot ring, (b) a proposal footprint
ring + floor stack read through the accepted B0 proposal contract
(:mod:`app.scenario.proposal`, read-only), and optionally (c) a generated building
option in the max-envelope engine's ``as_dict`` shape:

* a declared coordinate frame - CRS, horizontal + vertical unit, axis order, a
  stable local origin near the parcel centroid and its exact world->local transform,
  and a precision grid (section 3);
* layers ``parcel`` and one of ``proposed_massing`` / ``generated_option`` (section 5
  subset);
* closed, outward-oriented triangulated prisms per floor band - a bottom cap, a top
  cap (ear-clipping triangulation that handles concave rings) and side walls, with
  consistent winding so the signed volume is positive and every directed edge
  appears exactly once (section 4 "Mesh construction" + section 10 mesh gate);
* per-floor plates with areas from the authoritative 2263 ring (shapely), gross floor
  area and total height metrics (section 10 reconciliation);
* provenance - the input digests, the passed-through proposal provenance and the
  ``generator_version`` ``massing-1.0.0`` (section 2).

Every section-10 quality gate that this slice can enforce is a TYPED refusal
(:class:`MassingModelError` with a machine-readable ``reason``): a footprint not
within the lot is ``footprint_outside_lot`` and is NEVER clipped or repaired; a
self-intersecting or self-touching ring (a single ring cannot carry a hole - one
that pinches a hole off by revisiting a vertex is ``self_intersection``), a
non-finite value, an over-cap vertex count, a non-positive floor height, or an
empty floor stack each fail closed.

M5-T088 (DB-054 a-j) resource bounds, each a typed refusal raised BEFORE the heavy
work it guards: a coordinate beyond :data:`MAX_COORD_ABS` (``coordinate_out_of_range``,
so no lot area / centroid can overflow into a non-JSON value), more than
:data:`MAX_TOTAL_FLOORS` floors (``over_cap_floors``, before any ring is prepared),
more than :data:`MAX_TOTAL_MESH_VERTICES` output vertices (``over_cap_output_vertices``,
before any triangulation or mesh), and ear-clipping work beyond
:data:`MAX_TRIANGULATION_WORK` (``triangulation_budget_exceeded`` - refused up front
when the least possible work already exceeds it, else metered so the worst-case
O(n^3) scan cannot run away). Identical outlines are triangulated once.

M5-T098 (DB-061 a-d) before-wiring guards: the LOT ring - a separate argument B0
never sees - gets the same NYC EPSG:2263 range check as the proposal footprint
(``lot_ring_out_of_nyc_bounds``), so a wrong-unit / wrong-CRS lot (a 4326 lon/lat
or metric ring) is refused BY NAME and never mislabelled ``footprint_outside_lot``;
and any ``shapely`` geometry-engine error on a build path is wrapped into a typed
:class:`MassingModelError` (``geometry_engine_error``) at the module boundary, so no
untyped ``shapely`` error can escape. Valid inputs are unchanged.

M5-T106 (DB-069 a-d) before-wiring hardening, ahead of the PKT-E scene seam that
feeds user geometry in: the LOT NYC range check runs on the RAW vertices (before the
collinear collapse), so an out-of-range collinear spike (e.g. x=2e6) is refused, not
silently collapsed away; the geometry-engine wrap catches the whole
:class:`shapely.errors.ShapelyError` family (``GEOSException`` and its siblings -
``TopologicalError``, ``GeometryTypeError``, ``DimensionError``...), so no ``shapely``
error escapes untyped; and every refusal echo of caller input is length-bounded
(:data:`MAX_ECHO_CHARS` via :func:`_preview`), so a huge pasted vertex cannot amplify
a message. Valid inputs are unchanged (both goldens byte-identical).

Deterministic and offline: standard library + the admitted ``shapely`` (validity,
area, containment) and ``numpy`` (mesh volume / area reductions). No network, no new
dependency, no route, no web. ``content_hash`` pins a golden sha256.
"""

from __future__ import annotations

import functools
import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
from shapely.errors import ShapelyError
from shapely.geometry import Polygon

from .proposal import (
    MAX_OUTLINE_VERTICES,
    NYC_2263_X_MAX,
    NYC_2263_X_MIN,
    NYC_2263_Y_MAX,
    NYC_2263_Y_MIN,
    ProposedMassingError,
    validate_proposed_massing,
)

__all__ = [
    "MassingModelError",
    "MassingModel",
    "build_massing_model",
    "build_from_generated_option",
    "GENERATOR_VERSION",
    "GEOMETRY_VERSION",
    "SOURCE_PROPOSED",
    "SOURCE_GENERATED_OPTION",
]

# --- versioning -----------------------------------------------------------
GENERATOR_VERSION = "massing-1.0.0"
GEOMETRY_VERSION = 1

# --- declared coordinate frame (section 3) --------------------------------
CRS_CODE = "EPSG:2263"
CRS_AUTHORITY = "EPSG:2263 (NAD83 / New York Long Island, US survey feet)"
HORIZONTAL_UNIT = "us_survey_foot"
VERTICAL_UNIT = "us_survey_foot"
AXIS_ORDER = "easting_northing"  # x = easting, y = northing
#: The grid a renderer should snap to; emitted coordinates are quantised to it so
#: the golden serialization is stable. Metadata, never a legal precision claim.
PRECISION_GRID_FT = 1e-6
_QUANT_DECIMALS = 6  # round(ft, 6) == PRECISION_GRID_FT

# --- source labels (the ONLY building labels; honesty vocabulary) ---------
SOURCE_PROPOSED = "proposed"
SOURCE_GENERATED_OPTION = "generated_option"
LAYER_PARCEL = "parcel"
_LAYER_FOR_SOURCE = {
    SOURCE_PROPOSED: "proposed_massing",
    SOURCE_GENERATED_OPTION: "generated_option",
}
_DISCLOSURE_FOR_SOURCE = {
    SOURCE_PROPOSED: "Proposed - not a city record",
    SOURCE_GENERATED_OPTION: "Generated building option",
}

# --- fail-closed ceilings (resource bounds, never legal values) ------------
#: Total expanded floors across the stack (a paste / generation error above this).
MAX_TOTAL_FLOORS = 2000
#: A footprint may sit at most this far outside the lot line (survey noise) before
#: it is refused ``footprint_outside_lot``. It is NEVER clipped to fit.
FOOTPRINT_OUTSIDE_LOT_TOL_FT = 1e-6
#: Coordinate-magnitude bound (absolute value, US survey feet) on EVERY ring - the
#: lot ring is not B0-bounded, and a finite ~1e154 value overflows shapely's area /
#: centroid to inf/NaN. Mirrors the DXF / PDF writers' 1e8 (far outside NYC 2263).
MAX_COORD_ABS = 1e8
#: Total emitted mesh vertices (2 x ring size per floor band) - bounds the payload a
#: viewer / exporter receives (~6.5 MB of JSON at the ceiling).
MAX_TOTAL_MESH_VERTICES = 100_000
#: Per-request ear-clipping work, in units that upper-bound point-in-triangle tests
#: (a convex 999-vertex ring costs 497,502). Shared by every distinct ring.
MAX_TRIANGULATION_WORK = 2_000_000
#: A refusal message echoes at most this many characters of the offending caller input
#: (DB-069 d / M5-T098 G5 F-LOW-2). The lot ring has no B0 total-positions gate, so a
#: 200,000-character pasted vertex would otherwise produce a 200,000-character message
#: (log / response amplification). :func:`_preview` truncates the ``repr`` to this bound.
MAX_ECHO_CHARS = 120

_Point = tuple[float, float]


class MassingModelError(ValueError):
    """A massing input failed a section-10 quality gate. Carries a machine-readable
    ``reason`` and, where a specific field is implicated, the dotted ``field`` path.
    A subclass of :class:`ValueError` so a caller may catch broadly, but every
    refusal is typed and nothing is silently clipped or repaired."""

    def __init__(self, message: str, *, reason: str, field: str | None = None) -> None:
        super().__init__(message)
        self.reason = reason
        self.field = field


def _wrap_geos_errors(func):
    """Wrap the shapely geometry-engine boundary (DB-061 d / DB-069 b): any
    :class:`shapely.errors.ShapelyError` escaping the engine on a build path becomes a
    typed :class:`MassingModelError` (``geometry_engine_error``), so no untyped
    ``shapely`` error reaches a caller and every wiring route can map one exception
    family to a client response. ``ShapelyError`` is the shapely base class, so this
    covers ``GEOSException`` AND its siblings (``TopologicalError``,
    ``GeometryTypeError``, ``DimensionError``, ``EmptyPartError``, ...) - the earlier
    ``except GEOSException`` let the non-GEOS siblings escape untyped (M5-T098 G3/G5
    advisory), which this closes before the PKT-E scene seam feeds user geometry in.

    Inputs are magnitude- and NYC-range-bounded, finiteness-checked and validity-checked
    before any shapely construct runs, so this is a defensive backstop, not a routine
    path - valid inputs never trigger it and their output is unchanged. A
    :class:`MassingModelError` is a :class:`ValueError`, NOT a
    :class:`shapely.errors.ShapelyError` (their class hierarchies are disjoint below
    :class:`Exception`), so a typed refusal raised inside the body passes through
    unwrapped with its own reason."""

    @functools.wraps(func)
    def _guarded(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ShapelyError as exc:
            raise MassingModelError(
                f"the geometry engine (shapely) failed on this input: {_preview(exc)}",
                reason="geometry_engine_error", field=None) from exc

    return _guarded


# ---------------------------------------------------------------------------
# Numeric helpers (deterministic).
# ---------------------------------------------------------------------------


def _preview(value: object, limit: int = MAX_ECHO_CHARS) -> str:
    """A length-bounded ``repr`` of caller input for a refusal message (DB-069 d).

    Returns ``repr(value)`` unchanged when it is within ``limit`` characters; otherwise
    the first ``limit`` characters followed by a compact ``...<+N chars>`` marker (``N``
    a small integer, so the whole preview stays bounded). A refusal that echoes a huge
    pasted vertex, source or height thus cannot amplify the message. Resolved from the
    module namespace at call time so a mutation to it reddens the bounded-echo tests."""
    text = repr(value)
    if len(text) <= limit:
        return text
    return f"{text[:limit]}...<+{len(text) - limit} chars>"


def _q(value: float) -> float:
    """Quantise a coordinate to the declared precision grid (deterministic)."""
    return round(float(value), _QUANT_DECIMALS)


def _is_finite_number(value: object) -> bool:
    """True for a finite int/float that is not a bool (JSON booleans are ints in
    Python and must never pass a numeric check)."""
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(value)
    )


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


# ---------------------------------------------------------------------------
# Ring preparation + ear-clipping triangulation.
# ---------------------------------------------------------------------------


def _require_raw_vertices_in_nyc_bounds(
    vertices: Sequence[_Point], field: str
) -> None:
    """Refuse when any RAW ring vertex is outside plausible NYC EPSG:2263 bounds (DB-069
    a / DB-061 c). Called from :func:`_prepare_ring` on the lot ring BEFORE the collinear
    collapse, reusing the very :data:`NYC_2263_X_MIN` .. constants B0 applies to the
    proposal footprint (single source of truth) and naming ``field`` so the refusal
    points at the real culprit. EVERY vertex is checked (not only the first), on BOTH the
    easting and northing axes. Generous fail-closed unit guards, never a precise city
    boundary."""
    for x, y in vertices:
        if not (NYC_2263_X_MIN <= x <= NYC_2263_X_MAX
                and NYC_2263_Y_MIN <= y <= NYC_2263_Y_MAX):
            raise MassingModelError(
                f"lot_ring vertex ({x}, {y}) is outside plausible NYC EPSG:2263 bounds "
                f"([{NYC_2263_X_MIN}, {NYC_2263_X_MAX}] x [{NYC_2263_Y_MIN}, "
                f"{NYC_2263_Y_MAX}] US survey feet) - likely a wrong-unit or wrong-CRS "
                "lot; it is refused, never mislabelled",
                reason="lot_ring_out_of_nyc_bounds", field=field)


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


# ---------------------------------------------------------------------------
# Prism mesh construction.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _PrismMesh:
    floor_index: int
    level_index: int
    z_bottom_ft: float
    z_top_ft: float
    vertices: tuple[tuple[float, float, float], ...]
    triangles: tuple[tuple[int, int, int], ...]
    plate_area_sq_ft: float
    signed_volume_cu_ft: float

    def as_dict(self) -> dict:
        return {
            "floor_index": self.floor_index,
            "level_index": self.level_index,
            "z_bottom_ft": self.z_bottom_ft,
            "z_top_ft": self.z_top_ft,
            "vertices": [list(v) for v in self.vertices],
            "triangles": [list(t) for t in self.triangles],
            "plate_area_sq_ft": self.plate_area_sq_ft,
            "signed_volume_cu_ft": self.signed_volume_cu_ft,
        }


def _build_prism(
    ring: Sequence[_Point],
    cap: Sequence[tuple[int, int, int]],
    z_bottom: float,
    z_top: float,
    floor_index: int,
    level_index: int,
    local_origin: _Point,
) -> _PrismMesh:
    """A single closed, outward-oriented prism over ``ring`` between two elevations.

    Bottom + top caps (top from the CCW ``cap`` triangulation, bottom reversed) and
    one outward-wound side quad per ring edge. Vertices are stored in authoritative
    world 2263 coordinates; the signed volume is reduced in LOCAL coordinates (origin
    subtracted) so the closed-mesh volume is well conditioned at NYC magnitudes."""
    n = len(ring)
    zb, zt = _q(z_bottom), _q(z_top)
    verts: list[tuple[float, float, float]] = [(x, y, zb) for x, y in ring]  # 0..n-1
    verts += [(x, y, zt) for x, y in ring]  # n..2n-1
    tris: list[tuple[int, int, int]] = []
    # Top cap: CCW from above -> +z outward normal.
    for a, b, c in cap:
        tris.append((a + n, b + n, c + n))
    # Bottom cap: reversed -> -z outward normal.
    for a, b, c in cap:
        tris.append((a, c, b))
    # Side walls: for CCW ring edge i->j, outward-wound quad (bi,bj,tj)+(bi,tj,ti).
    for i in range(n):
        j = (i + 1) % n
        bi, bj = i, j
        ti, tj = i + n, j + n
        tris.append((bi, bj, tj))
        tris.append((bi, tj, ti))

    ox, oy = local_origin
    local = np.array(
        [[vx - ox, vy - oy, vz] for vx, vy, vz in verts], dtype=np.float64
    )
    idx = np.array(tris, dtype=np.int64)
    v0 = local[idx[:, 0]]
    v1 = local[idx[:, 1]]
    v2 = local[idx[:, 2]]
    signed_volume = float(np.sum(np.einsum("ij,ij->i", v0, np.cross(v1, v2))) / 6.0)

    plate_area = float(Polygon([(x, y) for x, y in ring]).area)
    return _PrismMesh(
        floor_index=floor_index,
        level_index=level_index,
        z_bottom_ft=zb,
        z_top_ft=zt,
        vertices=tuple(verts),
        triangles=tuple(tris),
        plate_area_sq_ft=round(plate_area, _QUANT_DECIMALS),
        signed_volume_cu_ft=round(signed_volume, _QUANT_DECIMALS),
    )


# ---------------------------------------------------------------------------
# Provenance digests.
# ---------------------------------------------------------------------------


def _digest(payload: Any) -> str:
    """A deterministic sha256 over a canonical JSON encoding of ``payload``."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# The truth object.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MassingModel:
    """The versioned scenario-geometry truth object (section 2). Renderer-agnostic
    JSON; a viewer draws it and never becomes its source."""

    source: str
    disclosure: str
    coordinate_reference_system: dict
    parcel: dict
    building_layer: dict
    meshes: tuple[_PrismMesh, ...]
    plates: tuple[dict, ...]
    metrics: dict
    provenance: dict

    def as_dict(self) -> dict:
        return {
            "generator_version": GENERATOR_VERSION,
            "geometry_version": GEOMETRY_VERSION,
            "source": self.source,
            "disclosure": self.disclosure,
            "coverage_status": "conditional",
            "coordinate_reference_system": self.coordinate_reference_system,
            "layers": [LAYER_PARCEL, self.building_layer["layer"]],
            "parcel": self.parcel,
            "building_layer": self.building_layer,
            "meshes": [m.as_dict() for m in self.meshes],
            "plates": [dict(p) for p in self.plates],
            "metrics": self.metrics,
            "provenance": self.provenance,
        }

    def to_json(self) -> str:
        """Deterministic, strict (no NaN/Infinity) JSON encoding."""
        return json.dumps(
            self.as_dict(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )

    def content_hash(self) -> str:
        """A golden sha256 over :meth:`to_json` - stable for identical inputs."""
        return "sha256:" + hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Floor-stack adapter (B0 levels -> expanded per-floor bands).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _Floor:
    floor_index: int
    level_index: int
    height_ft: float
    z_bottom: float
    z_top: float
    ring: tuple[_Point, ...]  # the prepared ring; also its content-dedupe key
    ring_field: str


def _check_floor_cap(levels: Sequence[Any]) -> None:
    """Refuse an over-tall stack from the B0 level counts alone, BEFORE any ring is
    prepared, triangulated or meshed (``over_cap_floors``)."""
    total = sum(
        lvl.get("floor_count", 0) for lvl in levels
        if isinstance(lvl, Mapping) and isinstance(lvl.get("floor_count"), int)
    )
    if total > MAX_TOTAL_FLOORS:
        raise MassingModelError(
            f"the floor stack has {total} floors, over the cap of {MAX_TOTAL_FLOORS} "
            "floors", reason="over_cap_floors", field="proposed_massing.levels")


def _expand_floor_stack(
    block: Mapping[str, Any], default_ring: tuple[_Point, ...]
) -> list[_Floor]:
    """Adapter: expand the B0 ``levels`` (each ``floor_count`` identical floors of
    ``floor_to_floor_ft``) into an explicit per-floor band stack, stacking z from 0.

    The B0 contract DOES carry per-floor heights this way, so no separate floor-stack
    input is needed. A level may carry its own ``outline`` (a setback / tower band);
    that footprint is prepared for its floors (identical content shares one ring),
    else the top-level footprint is reused. No triangulation happens here. Fails
    closed on a non-positive height or an empty stack."""
    levels = block.get("levels")
    if not isinstance(levels, list) or not levels:
        raise MassingModelError("proposed_massing.levels must be a non-empty array",
                                reason="invalid_source", field="proposed_massing.levels")

    field_by_ring: dict[tuple[_Point, ...], str] = {
        default_ring: "proposed_massing.outline"}
    floors: list[_Floor] = []
    z = 0.0
    floor_index = 0
    for lvl in sorted(levels, key=lambda item: item.get("level_index", 0)):
        level_index = lvl.get("level_index", 0)
        height = lvl.get("floor_to_floor_ft")
        count = lvl.get("floor_count")
        if not _is_finite_number(height) or height <= 0:
            raise MassingModelError(
                f"level {level_index} floor_to_floor_ft must be finite and > 0; "
                f"got {_preview(height)}",
                reason="non_positive_height",
                field=f"proposed_massing.levels[{level_index}].floor_to_floor_ft")
        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            raise MassingModelError(
                f"level {level_index} floor_count must be an integer >= 1; "
                f"got {_preview(count)}",
                reason="invalid_source",
                field=f"proposed_massing.levels[{level_index}].floor_count")

        ring = default_ring
        if lvl.get("outline") is not None:
            ring = tuple(_prepare_ring(
                lvl["outline"].get("vertices", []),
                f"proposed_massing.levels[{level_index}].outline.vertices"))
            field_by_ring.setdefault(
                ring, f"proposed_massing.levels[{level_index}].outline")
        ring_field = field_by_ring[ring]

        for _ in range(count):
            floors.append(_Floor(
                floor_index=floor_index, level_index=level_index,
                height_ft=_q(height), z_bottom=_q(z), z_top=_q(z + height),
                ring=ring, ring_field=ring_field))
            z += height
            floor_index += 1
    return floors


def _check_output_size(floors: Sequence[_Floor]) -> None:
    """Refuse an over-large mesh from ring sizes alone, BEFORE any triangulation or
    prism is built (``over_cap_output_vertices``).

    This total INTENTIONALLY does not content-dedupe (DB-061 f / G3-A3): every floor
    emits its OWN prism, so two floors sharing an identical outline still produce two
    prisms and thus ``2 * (2 * ring)`` output vertices. :func:`_triangulate_distinct`
    dedupes the triangulation WORK (a distinct ring is triangulated once), but the
    emitted vertex COUNT is per floor. Never 'optimize' this sum into a
    per-distinct-ring figure: it would under-count the real payload a viewer/exporter
    receives and let the ceiling be bypassed."""
    total = sum(2 * len(floor.ring) for floor in floors)
    if total > MAX_TOTAL_MESH_VERTICES:
        raise MassingModelError(
            f"the massing would emit {total} mesh vertices, over the cap of "
            f"{MAX_TOTAL_MESH_VERTICES}", reason="over_cap_output_vertices",
            field="proposed_massing.levels")


def _triangulate_distinct(
    floors: Sequence[_Floor],
) -> dict[tuple[_Point, ...], list[tuple[int, int, int]]]:
    """Triangulate each DISTINCT ring once under ONE shared per-request budget.
    Refuses up front when the least possible work (:func:`_min_ear_clip_work`) of the
    distinct rings already exceeds :data:`MAX_TRIANGULATION_WORK`."""
    distinct: dict[tuple[_Point, ...], str] = {}
    for floor in floors:
        distinct.setdefault(floor.ring, floor.ring_field)
    least = sum(_min_ear_clip_work(len(ring)) for ring in distinct)
    if least > MAX_TRIANGULATION_WORK:
        raise MassingModelError(
            f"triangulating {len(distinct)} distinct outline(s) needs at least {least} "
            f"work units, over the budget of {MAX_TRIANGULATION_WORK}",
            reason="triangulation_budget_exceeded", field="proposed_massing.levels")
    budget = _WorkBudget(MAX_TRIANGULATION_WORK)
    return {ring: _triangulate(ring, field, budget) for ring, field in distinct.items()}


# ---------------------------------------------------------------------------
# Builders.
# ---------------------------------------------------------------------------


def _lot_polygon(lot_ring: Sequence[Sequence[float]]) -> tuple[Polygon, list[_Point]]:
    """Validate the canonical lot ring and return its shapely polygon + prepared ring.
    Refuses a self-intersecting or self-touching lot, and a lot outside the NYC
    EPSG:2263 range (a wrong-unit / wrong-CRS mistake, ``lot_ring_out_of_nyc_bounds``).

    The lot is the ONE ring B0 never validates, so :func:`_prepare_ring` is called with
    ``nyc_range_check=True``: it range-checks the RAW vertices in its parse loop, BEFORE
    the collinear collapse (DB-069 a), reusing the very :data:`NYC_2263_X_MIN` ..
    constants B0 applies to the proposal footprint (single source of truth) and naming
    ``lot_ring`` so the refusal points at the real culprit. These are generous
    fail-closed unit guards, never a precise city boundary. One ring cannot carry a
    hole: a keyhole ring that pinches one off by revisiting a vertex is refused
    ``self_intersection`` in :func:`_prepare_ring`."""
    ring = _prepare_ring(lot_ring, "lot_ring", nyc_range_check=True)
    poly = Polygon([(x, y) for x, y in ring])
    if poly.interiors:  # defensive: unreachable from one ring (DB-054 f)
        raise MassingModelError("lot_ring encloses a hole; a massing lot must be a "
                                "single simple ring", reason="lot_has_holes",
                                field="lot_ring")
    if not poly.is_valid:
        raise MassingModelError("lot_ring is not a valid simple polygon",
                                reason="self_intersection", field="lot_ring")
    return poly, ring


def _local_origin(lot_ring: Sequence[_Point]) -> _Point:
    """A stable local origin near the parcel centroid (section 3, step 1)."""
    centroid = Polygon([(x, y) for x, y in lot_ring]).centroid
    return (_q(centroid.x), _q(centroid.y))


def _crs_frame(origin: _Point) -> dict:
    """The declared coordinate frame with the exact world->local transform (section 3)."""
    ox, oy = origin
    return {
        "crs": CRS_CODE,
        "authority": CRS_AUTHORITY,
        "horizontal_unit": HORIZONTAL_UNIT,
        "vertical_unit": VERTICAL_UNIT,
        "axis_order": AXIS_ORDER,
        "storage": "authoritative_world_2263",
        "local_origin": [ox, oy, 0.0],
        "world_to_local": {
            "operation": "subtract_local_origin",
            "offset": [-ox, -oy, 0.0],
        },
        "precision_grid_ft": PRECISION_GRID_FT,
    }


@_wrap_geos_errors
def build_massing_model(
    *,
    lot_ring: Sequence[Sequence[float]],
    proposed_massing: Mapping[str, Any],
    source: str = SOURCE_PROPOSED,
    scenario_id: str | None = None,
    property_geometry_version_id: str | None = None,
    rule_release_id: str | None = None,
) -> MassingModel:
    """Build the massing truth object from a canonical 2263 lot ring and a B0
    ``proposed_massing`` block (validated read-only through :mod:`app.scenario.proposal`).

    ``source`` selects the honest building label (``proposed`` or ``generated_option``);
    the optional ids are carried through provenance verbatim. Every failure is a typed
    :class:`MassingModelError`; nothing is clipped or repaired."""
    if source not in _LAYER_FOR_SOURCE:
        raise MassingModelError(
            f"source must be one of {sorted(_LAYER_FOR_SOURCE)}; got {_preview(source)}",
            reason="invalid_source", field="source")

    # Fail-closed B0 validation of the proposed building (translated to a typed refusal).
    try:
        validate_proposed_massing(proposed_massing)
    except ProposedMassingError as exc:
        raise MassingModelError(
            f"proposed_massing failed B0 contract validation: {exc}",
            reason="invalid_source", field=exc.field) from exc

    # Cheap bounds first: nothing below runs for an over-tall stack.
    _check_floor_cap(proposed_massing["levels"])
    lot_poly, lot_prepared = _lot_polygon(lot_ring)
    origin = _local_origin(lot_prepared)

    footprint_ring = tuple(_prepare_ring(
        proposed_massing["outline"].get("vertices", []),
        "proposed_massing.outline.vertices"))
    floors = _expand_floor_stack(proposed_massing, footprint_ring)
    _check_output_size(floors)

    # Fail-closed containment: every floor footprint within the lot (never clipped).
    lot_guard = lot_poly.buffer(FOOTPRINT_OUTSIDE_LOT_TOL_FT)
    checked: set[tuple[_Point, ...]] = set()
    for floor in floors:
        if floor.ring in checked:
            continue
        checked.add(floor.ring)
        floor_poly = Polygon([(x, y) for x, y in floor.ring])
        if not lot_guard.contains(floor_poly):
            raise MassingModelError(
                f"level {floor.level_index} footprint lies outside the lot beyond "
                f"{FOOTPRINT_OUTSIDE_LOT_TOL_FT} ft; it is refused, never clipped",
                reason="footprint_outside_lot",
                field=f"proposed_massing.levels[{floor.level_index}].outline")

    caps = _triangulate_distinct(floors)
    meshes = tuple(
        _build_prism(floor.ring, caps[floor.ring], floor.z_bottom, floor.z_top,
                     floor.floor_index, floor.level_index, origin)
        for floor in floors
    )

    plates = tuple({
        "floor_index": m.floor_index,
        "level_index": m.level_index,
        "elevation_ft": m.z_bottom_ft,
        "height_ft": round(m.z_top_ft - m.z_bottom_ft, _QUANT_DECIMALS),
        "area_sq_ft": m.plate_area_sq_ft,
    } for m in meshes)

    gross_floor_area = round(sum(p["area_sq_ft"] for p in plates), _QUANT_DECIMALS)
    total_height = round(sum(p["height_ft"] for p in plates), _QUANT_DECIMALS)

    parcel = {
        "layer": LAYER_PARCEL,
        "ring": [[x, y] for x, y in lot_prepared],
        "area_sq_ft": round(float(lot_poly.area), _QUANT_DECIMALS),
        "elevation_ft": 0.0,
    }
    building_layer = {
        "layer": _LAYER_FOR_SOURCE[source],
        "disclosure": _DISCLOSURE_FOR_SOURCE[source],
        "floor_count": len(floors),
    }

    provenance = {
        "generator_version": GENERATOR_VERSION,
        "source": source,
        "scenario_id": scenario_id,
        "property_geometry_version_id": property_geometry_version_id,
        "rule_release_id": rule_release_id,
        "input_digests": {
            "lot_ring": _digest([[x, y] for x, y in lot_prepared]),
            "proposed_massing": _digest(_canonical_block(proposed_massing)),
            "local_origin": _digest(list(origin)),
        },
        "proposal_provenance": _passthrough_provenance(proposed_massing),
    }

    return MassingModel(
        source=source,
        disclosure=_DISCLOSURE_FOR_SOURCE[source],
        coordinate_reference_system=_crs_frame(origin),
        parcel=parcel,
        building_layer=building_layer,
        meshes=meshes,
        plates=plates,
        metrics={
            "gross_floor_area_sq_ft": gross_floor_area,
            "total_height_ft": total_height,
            "floor_count": len(floors),
            "lot_area_sq_ft": parcel["area_sq_ft"],
        },
        provenance=provenance,
    )


def build_from_generated_option(
    *,
    lot_ring: Sequence[Sequence[float]],
    max_envelope: Mapping[str, Any],
    scenario_id: str | None = None,
    property_geometry_version_id: str | None = None,
    rule_release_id: str | None = None,
) -> MassingModel:
    """Build the truth object from a generated building option in the max-envelope
    engine's exact ``as_dict`` shape. The candidate is the engine's ``candidate`` field
    (a B0 ``proposed_massing`` draft); when it is ``None`` the engine emitted an explicit
    typed placement gap and no massing can be built - a typed refusal, never a fabricated
    building. The result is labelled ``generated_option`` ("Generated building option")."""
    if not isinstance(max_envelope, Mapping) or "candidate" not in max_envelope:
        raise MassingModelError(
            "max_envelope must be the engine's as_dict shape carrying a 'candidate' key",
            reason="invalid_source", field="max_envelope")
    candidate = max_envelope.get("candidate")
    if candidate is None:
        placement = max_envelope.get("candidate_placement") or {}
        detail = placement.get("detail") if isinstance(placement, Mapping) else None
        raise MassingModelError(
            "max_envelope emitted no candidate footprint (an explicit typed placement "
            f"gap); no generated option can be built. {detail or ''}".strip(),
            reason="no_generated_candidate", field="max_envelope.candidate")
    return build_massing_model(
        lot_ring=lot_ring,
        proposed_massing=candidate,
        source=SOURCE_GENERATED_OPTION,
        scenario_id=scenario_id,
        property_geometry_version_id=property_geometry_version_id,
        rule_release_id=rule_release_id,
    )


def _canonical_block(block: Mapping[str, Any]) -> dict:
    """The digest-relevant subset of a proposed_massing block (outline + levels)."""
    return {
        "outline": block.get("outline"),
        "levels": block.get("levels"),
        "exterior_walls": block.get("exterior_walls"),
    }


def _passthrough_provenance(block: Mapping[str, Any]) -> dict:
    """Carry the proposal's own provenance through verbatim (author / editor_version /
    kind), so the truth object records where its footprint came from."""
    prov = block.get("provenance")
    if not isinstance(prov, Mapping):
        return {}
    return {
        "author": prov.get("author"),
        "editor_version": prov.get("editor_version"),
        "kind": prov.get("kind"),
        "parent_scenario_id": prov.get("parent_scenario_id"),
    }
