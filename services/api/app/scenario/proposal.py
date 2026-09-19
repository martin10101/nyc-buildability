"""Proposed-massing validation (task M5-T048, phase B0).

THIRD INPUT CLASS honesty (D-076-R002): an architect-proposed building is
NEITHER a city record NOR a rule. This module validates the parsed
``proposed_massing`` block of a scenario document with TYPED refusals only. It
computes NO allowance, derives NO area / lot-coverage / FAR / height, and runs
NO rule comparison - those are phases B1/B2. Records, rules, and proposals stay
three distinct things; nothing here implies a permitted or achievable value.

What is validated (each failure a :class:`ProposedMassingError` naming the exact
``field``):

* **closed ring** - the outline is an EXPLICITLY closed EPSG:2263 ring
  (``vertices[0] == vertices[-1]``);
* **simple ring** - no zero-length edge, no 180-degree spike (a collinear
  reversal at a shared vertex), and no two NON-adjacent edges share any point; a
  deterministic, dependency-free segment-intersection test (predicate documented
  on :func:`_ring_is_simple`);
* **unit sanity** - every coordinate is a finite number inside generous NYC
  EPSG:2263 (US survey feet) bounds; a value outside is a wrong-unit / wrong-CRS
  mistake and fails closed;
* **level consistency** - the ``level_index`` values are exactly ``{0..N-1}``
  (contiguous, unique), every ``floor_count`` is an integer >= 1, and every
  ``floor_to_floor_ft`` is a finite, strictly-positive number within a sane
  building bound; a differing per-level outline is validated as an outline;
* **wall integrity** - each wall ``id`` is a non-empty unique string and both
  vertex indices are in range and distinct;
* **bounded ceilings** - the DB-013 fail-closed pattern:
  :data:`MAX_OUTLINE_VERTICES`, :data:`MAX_LEVELS`, :data:`MAX_FLOOR_COUNT`,
  :data:`MAX_EXTERIOR_WALLS`.

The schema (``scenario.schema.json`` ``proposed_massing`` $def) fixes the
structural shape. This module owns the semantic invariants, of two kinds. Some a
JSON Schema CANNOT express and that require cross-value / geometry validation:
ring closure, non-self-intersection, distinct non-closing vertices, level-index
contiguity, and wall indices referencing the outline vertex count. Others a JSON
Schema COULD express (per-coordinate NYC bounds, the sane floor-to-floor upper
bound, the DB-013 count ceilings) but are enforced here BY DESIGN so each refusal
is a typed field-named error and the numeric bounds live once as constants;
strict positivity is expressed in the schema (``exclusiveMinimum: 0``) and
re-checked here as defense in depth. It is deterministic and offline: no network,
no dependency beyond the standard library.
"""

from __future__ import annotations

import math

__all__ = [
    "ProposedMassingError",
    "validate_proposed_massing",
    "MAX_OUTLINE_VERTICES",
    "MAX_LEVELS",
    "MAX_FLOOR_COUNT",
    "MAX_EXTERIOR_WALLS",
    "MAX_FLOOR_TO_FLOOR_FT",
]

# --- DB-013 bounded ceilings (fail-closed) ---------------------------------
# A proposed building far above any of these is a paste / generation error, not
# a real editor input; the validator refuses it rather than walking it.
MAX_OUTLINE_VERTICES = 1000  # positions, INCLUDING the repeated closing vertex
MAX_LEVELS = 500
MAX_FLOOR_COUNT = 500  # identical floors a single level record may represent
MAX_EXTERIOR_WALLS = 4000

# --- unit-sanity bounds ----------------------------------------------------
# Generous EPSG:2263 (NAD83 / New York Long Island, US survey feet) bounds that
# comfortably contain all five boroughs. These are FAIL-CLOSED guards against a
# wrong-unit / wrong-CRS coordinate (e.g. a 4326 lon/lat pair, or meters), NOT a
# precise city boundary; a coordinate outside is rejected as a unit mistake.
NYC_2263_X_MIN = 900000.0
NYC_2263_X_MAX = 1100000.0
NYC_2263_Y_MIN = 100000.0
NYC_2263_Y_MAX = 300000.0

# A sane per-level floor-to-floor height ceiling in feet (unit sanity, not a
# zoning rule). Anything above is treated as a unit error and fails closed.
MAX_FLOOR_TO_FLOOR_FT = 100.0

_REQUIRED_SRID = 2263
_PROPOSED_KIND = "proposed"

_Point = tuple[float, float]


class ProposedMassingError(ValueError):
    """A ``proposed_massing`` block failed validation.

    Carries the exact ``field`` (a dotted path into the block) so a caller can
    name it verbatim. A subclass of :class:`ValueError` so a caller may catch it
    broadly, but the type is precise and the failure is always typed.
    """

    def __init__(self, message: str, *, field: str) -> None:
        super().__init__(message)
        self.field = field


# ---------------------------------------------------------------------------
# Geometry primitives (deterministic, dependency-free)
# ---------------------------------------------------------------------------


def _orientation(a: _Point, b: _Point, c: _Point) -> float:
    """Signed area term ``(b-a) x (c-a)``: >0 left turn, <0 right turn, 0
    collinear."""
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _on_segment(a: _Point, b: _Point, p: _Point) -> bool:
    """True when a point ``p`` known to be collinear with ``a``-``b`` lies within
    that segment's closed bounding box (i.e. on the segment)."""
    return min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= p[1] <= max(
        a[1], b[1]
    )


def _segments_intersect(p1: _Point, p2: _Point, p3: _Point, p4: _Point) -> bool:
    """True when segment ``p1``-``p2`` and segment ``p3``-``p4`` share ANY point
    (a proper crossing, a T-touch, or a collinear overlap), by the standard
    four-orientation test. Touching at an endpoint counts as sharing a point;
    callers exclude legitimately-adjacent polygon edges before calling."""
    d1 = _orientation(p3, p4, p1)
    d2 = _orientation(p3, p4, p2)
    d3 = _orientation(p1, p2, p3)
    d4 = _orientation(p1, p2, p4)
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and (
        (d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)
    ):
        return True
    if d1 == 0 and _on_segment(p3, p4, p1):
        return True
    if d2 == 0 and _on_segment(p3, p4, p2):
        return True
    if d3 == 0 and _on_segment(p1, p2, p3):
        return True
    if d4 == 0 and _on_segment(p1, p2, p4):
        return True
    return False


def _ring_is_simple(ring: list[_Point]) -> bool:
    """True when ``ring`` (the DISTINCT vertices, closing duplicate already
    removed) is a simple polygon.

    Predicate: the ring is simple iff (1) no edge is zero-length, (2) no vertex
    is a 180-degree reversal spike (its two incident edges are collinear and
    point in opposing directions, so they overlap beyond the shared vertex), and
    (3) no two NON-adjacent edges share any point. Adjacent edges legitimately
    meet at their single shared vertex and are excluded from (3); condition (2)
    is what still forbids them from overlapping. O(n^2) in the vertex count,
    which is bounded by :data:`MAX_OUTLINE_VERTICES`.
    """
    n = len(ring)
    if n < 3:
        return False

    # (1) + (2): edge lengths and reversal spikes at each vertex.
    for k in range(n):
        prev_pt = ring[(k - 1) % n]
        cur = ring[k]
        nxt = ring[(k + 1) % n]
        if cur == nxt:  # zero-length edge
            return False
        v1 = (cur[0] - prev_pt[0], cur[1] - prev_pt[1])
        v2 = (nxt[0] - cur[0], nxt[1] - cur[1])
        cross = v1[0] * v2[1] - v1[1] * v2[0]
        dot = v1[0] * v2[0] + v1[1] * v2[1]
        if cross == 0 and dot < 0:  # collinear reversal -> spike / overlap
            return False

    # (3): non-adjacent edge intersections.
    for i in range(n):
        a, b = ring[i], ring[(i + 1) % n]
        for j in range(i + 1, n):
            # edges i and j are adjacent when they share a vertex.
            if j == i + 1 or (i == 0 and j == n - 1):
                continue
            c, d = ring[j], ring[(j + 1) % n]
            if _segments_intersect(a, b, c, d):
                return False
    return True


# ---------------------------------------------------------------------------
# Field validators
# ---------------------------------------------------------------------------


def _is_real_number(value: object) -> bool:
    """True for a finite int/float that is not a bool (JSON ``true``/``false``
    are ints in Python and must never pass a numeric check)."""
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(value)
    )


def _validate_outline(outline: object, field: str) -> list[_Point]:
    """Validate a closed EPSG:2263 outline and return its parsed vertex list
    (including the closing duplicate). Raises :class:`ProposedMassingError` with
    the exact field on any defect."""
    if not isinstance(outline, dict):
        raise ProposedMassingError(f"{field} must be an object", field=field)

    srid = outline.get("srid")
    if srid != _REQUIRED_SRID:
        raise ProposedMassingError(
            f"{field}.srid must be EPSG:{_REQUIRED_SRID} (US survey feet); got {srid!r}",
            field=f"{field}.srid",
        )

    vertices = outline.get("vertices")
    if not isinstance(vertices, list):
        raise ProposedMassingError(
            f"{field}.vertices must be an array", field=f"{field}.vertices"
        )
    if len(vertices) > MAX_OUTLINE_VERTICES:
        raise ProposedMassingError(
            f"{field}.vertices exceeds MAX_OUTLINE_VERTICES ({MAX_OUTLINE_VERTICES}); "
            f"got {len(vertices)}",
            field=f"{field}.vertices",
        )
    if len(vertices) < 4:
        raise ProposedMassingError(
            f"{field}.vertices must have at least 4 positions for a closed ring "
            f"(>=3 distinct vertices plus the repeated closing vertex); got {len(vertices)}",
            field=f"{field}.vertices",
        )

    parsed: list[_Point] = []
    for idx, vertex in enumerate(vertices):
        vfield = f"{field}.vertices[{idx}]"
        if not isinstance(vertex, (list, tuple)) or len(vertex) != 2:
            raise ProposedMassingError(
                f"{vfield} must be an [x, y] pair", field=vfield
            )
        x, y = vertex[0], vertex[1]
        if not _is_real_number(x) or not _is_real_number(y):
            raise ProposedMassingError(
                f"{vfield} must be a finite [x, y] pair of numbers; got {vertex!r}",
                field=vfield,
            )
        fx, fy = float(x), float(y)
        if not (
            NYC_2263_X_MIN <= fx <= NYC_2263_X_MAX
            and NYC_2263_Y_MIN <= fy <= NYC_2263_Y_MAX
        ):
            raise ProposedMassingError(
                f"{vfield} ({fx}, {fy}) is outside the plausible NYC EPSG:2263 bounds "
                f"([{NYC_2263_X_MIN}, {NYC_2263_X_MAX}] x [{NYC_2263_Y_MIN}, "
                f"{NYC_2263_Y_MAX}] US survey feet) - likely a wrong-unit or wrong-CRS "
                "coordinate",
                field=vfield,
            )
        parsed.append((fx, fy))

    if parsed[0] != parsed[-1]:
        raise ProposedMassingError(
            f"{field} ring is not closed: the first and last vertex must be identical "
            f"(got {parsed[0]} and {parsed[-1]})",
            field=field,
        )

    ring = parsed[:-1]  # the distinct ring vertices (drop the closing duplicate)
    if len(set(ring)) != len(ring):
        raise ProposedMassingError(
            f"{field} has duplicate vertices other than the closing vertex; a valid ring "
            "visits each vertex once",
            field=field,
        )
    if len(ring) < 3:
        raise ProposedMassingError(
            f"{field} needs at least 3 distinct vertices to bound an area; got {len(ring)}",
            field=field,
        )
    if not _ring_is_simple(ring):
        raise ProposedMassingError(
            f"{field} is self-intersecting; the outline must be a simple "
            "(non-self-intersecting) polygon",
            field=field,
        )
    return parsed


def _validate_levels(levels: object, field: str) -> None:
    if not isinstance(levels, list):
        raise ProposedMassingError(f"{field} must be an array", field=field)
    if len(levels) < 1:
        raise ProposedMassingError(
            f"{field} must contain at least one level record", field=field
        )
    if len(levels) > MAX_LEVELS:
        raise ProposedMassingError(
            f"{field} exceeds MAX_LEVELS ({MAX_LEVELS}); got {len(levels)}", field=field
        )

    indices: list[int] = []
    for pos, level in enumerate(levels):
        lf = f"{field}[{pos}]"
        if not isinstance(level, dict):
            raise ProposedMassingError(f"{lf} must be an object", field=lf)

        level_index = level.get("level_index")
        if isinstance(level_index, bool) or not isinstance(level_index, int):
            raise ProposedMassingError(
                f"{lf}.level_index must be an integer", field=f"{lf}.level_index"
            )
        indices.append(level_index)

        floor_count = level.get("floor_count")
        if isinstance(floor_count, bool) or not isinstance(floor_count, int):
            raise ProposedMassingError(
                f"{lf}.floor_count must be an integer", field=f"{lf}.floor_count"
            )
        if floor_count < 1:
            raise ProposedMassingError(
                f"{lf}.floor_count must be >= 1; got {floor_count}",
                field=f"{lf}.floor_count",
            )
        if floor_count > MAX_FLOOR_COUNT:
            raise ProposedMassingError(
                f"{lf}.floor_count exceeds MAX_FLOOR_COUNT ({MAX_FLOOR_COUNT}); "
                f"got {floor_count}",
                field=f"{lf}.floor_count",
            )

        ftf = level.get("floor_to_floor_ft")
        if (
            isinstance(ftf, bool)
            or not isinstance(ftf, (int, float))
            or not math.isfinite(ftf)
        ):
            raise ProposedMassingError(
                f"{lf}.floor_to_floor_ft must be a finite number; got {ftf!r}",
                field=f"{lf}.floor_to_floor_ft",
            )
        if ftf <= 0:
            raise ProposedMassingError(
                f"{lf}.floor_to_floor_ft must be strictly positive; got {ftf}",
                field=f"{lf}.floor_to_floor_ft",
            )
        if ftf > MAX_FLOOR_TO_FLOOR_FT:
            raise ProposedMassingError(
                f"{lf}.floor_to_floor_ft exceeds the plausible bound "
                f"({MAX_FLOOR_TO_FLOOR_FT} ft); got {ftf} - likely a unit error",
                field=f"{lf}.floor_to_floor_ft",
            )

        per_level_outline = level.get("outline")
        if per_level_outline is not None:
            _validate_outline(per_level_outline, f"{lf}.outline")

    if sorted(indices) != list(range(len(levels))):
        raise ProposedMassingError(
            f"{field} level_index values must be contiguous from 0 with no gaps or "
            f"duplicates (expected {{0..{len(levels) - 1}}}, got {sorted(indices)})",
            field=field,
        )


def _validate_walls(walls: object, vertex_count: int, field: str) -> None:
    if not isinstance(walls, list):
        raise ProposedMassingError(f"{field} must be an array", field=field)
    if len(walls) > MAX_EXTERIOR_WALLS:
        raise ProposedMassingError(
            f"{field} exceeds MAX_EXTERIOR_WALLS ({MAX_EXTERIOR_WALLS}); got {len(walls)}",
            field=field,
        )

    seen_ids: set[str] = set()
    for pos, wall in enumerate(walls):
        wf = f"{field}[{pos}]"
        if not isinstance(wall, dict):
            raise ProposedMassingError(f"{wf} must be an object", field=wf)

        wall_id = wall.get("id")
        if not isinstance(wall_id, str) or not wall_id.strip():
            raise ProposedMassingError(
                f"{wf}.id must be a non-empty string", field=f"{wf}.id"
            )
        if wall_id in seen_ids:
            raise ProposedMassingError(
                f"{wf}.id is not unique: {wall_id!r}", field=f"{wf}.id"
            )
        seen_ids.add(wall_id)

        for key in ("start_vertex_index", "end_vertex_index"):
            iv = wall.get(key)
            if isinstance(iv, bool) or not isinstance(iv, int):
                raise ProposedMassingError(
                    f"{wf}.{key} must be an integer", field=f"{wf}.{key}"
                )
            if not (0 <= iv < vertex_count):
                raise ProposedMassingError(
                    f"{wf}.{key} ({iv}) is out of range for an outline with "
                    f"{vertex_count} vertices",
                    field=f"{wf}.{key}",
                )
        if wall["start_vertex_index"] == wall["end_vertex_index"]:
            raise ProposedMassingError(
                f"{wf} start_vertex_index and end_vertex_index must differ "
                f"(got {wall['start_vertex_index']})",
                field=wf,
            )


def _validate_provenance(provenance: object, field: str) -> None:
    if not isinstance(provenance, dict):
        raise ProposedMassingError(f"{field} must be an object", field=field)

    for key in ("author", "editor_version"):
        value = provenance.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ProposedMassingError(
                f"{field}.{key} must be a non-empty string", field=f"{field}.{key}"
            )

    kind = provenance.get("kind")
    if kind != _PROPOSED_KIND:
        raise ProposedMassingError(
            f"{field}.kind must be the literal '{_PROPOSED_KIND}' - a proposed building "
            "is a THIRD input class, never a record or a rule (D-076-R002); "
            f"got {kind!r}",
            field=f"{field}.kind",
        )

    parent = provenance.get("parent_scenario_id")
    if parent is not None and (not isinstance(parent, str) or not parent.strip()):
        raise ProposedMassingError(
            f"{field}.parent_scenario_id, when present, must be a non-empty string or null",
            field=f"{field}.parent_scenario_id",
        )


def validate_proposed_massing(block: object) -> None:
    """Validate a parsed ``proposed_massing`` block. Returns ``None`` when the
    block is valid; raises :class:`ProposedMassingError` naming the exact field
    otherwise. Performs NO derivation and computes NO allowance (D-076-R002)."""
    if not isinstance(block, dict):
        raise ProposedMassingError(
            "proposed_massing must be an object", field="proposed_massing"
        )

    outline_vertices = _validate_outline(
        block.get("outline"), "proposed_massing.outline"
    )
    _validate_levels(block.get("levels"), "proposed_massing.levels")
    _validate_walls(
        block.get("exterior_walls"),
        len(outline_vertices),
        "proposed_massing.exterior_walls",
    )
    _validate_provenance(block.get("provenance"), "proposed_massing.provenance")
