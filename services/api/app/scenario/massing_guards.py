"""Massing input guards (M5-T112 split of :mod:`app.scenario.massing_model`).

One responsibility: the fail-closed INPUT boundary of the massing builder - the typed
refusal class, bounded caller-input echoes, finiteness/magnitude predicates, the NYC
EPSG:2263 range guard, the shapely geometry-engine wrap, and the DB-079 (b) overflow
field locator. Nothing here builds geometry or draws a rule; every gate is a TYPED
:class:`MassingModelError` and no input is silently clipped or repaired.

Imported by :mod:`app.scenario.massing_triangulation`, :mod:`app.scenario.massing_mesh`
and the :mod:`app.scenario.massing_model` facade; it imports only the read-only B0
proposal contract (the shared NYC bound constants) plus the standard library and the
already-admitted ``shapely``. No route, no web, no new dependency (D-087-R009).
"""

from __future__ import annotations

import functools
import math
from collections.abc import Mapping, Sequence

from shapely.errors import ShapelyError

from .proposal import (
    NYC_2263_X_MAX,
    NYC_2263_X_MIN,
    NYC_2263_Y_MAX,
    NYC_2263_Y_MIN,
)

__all__ = [
    "MassingModelError",
    "MAX_COORD_ABS",
    "MAX_ECHO_CHARS",
    "NYC_2263_X_MIN",
    "NYC_2263_X_MAX",
    "NYC_2263_Y_MIN",
    "NYC_2263_Y_MAX",
]

_Point = tuple[float, float]

#: Coordinate-magnitude bound (absolute value, US survey feet) on EVERY ring - the lot
#: ring is not B0-bounded, and a finite ~1e154 value overflows shapely's area / centroid
#: to inf/NaN. Mirrors the DXF / PDF writers' 1e8 (far outside NYC 2263).
MAX_COORD_ABS = 1e8

#: A refusal message echoes at most this many characters of the offending caller input
#: (DB-069 d / M5-T098 G5 F-LOW-2). The lot ring has no B0 total-positions gate, so a
#: 200,000-character pasted vertex would otherwise produce a 200,000-character message
#: (log / response amplification). :func:`_preview` truncates the ``repr`` to this bound.
MAX_ECHO_CHARS = 120


class MassingModelError(ValueError):
    """A massing input failed a section-10 quality gate. Carries a machine-readable
    ``reason`` and, where a specific field is implicated, the dotted ``field`` path.
    A subclass of :class:`ValueError` so a caller may catch broadly, but every
    refusal is typed and nothing is silently clipped or repaired."""

    def __init__(self, message: str, *, reason: str, field: str | None = None) -> None:
        super().__init__(message)
        self.reason = reason
        self.field = field


def _preview(value: object, limit: int = MAX_ECHO_CHARS) -> str:
    """A length-bounded ``repr`` of caller input for a refusal message (DB-069 d).

    Returns ``repr(value)`` unchanged when it is within ``limit`` characters; otherwise
    the first ``limit`` characters followed by a compact ``...<+N chars>`` marker (``N``
    a small integer, so the whole preview stays bounded). A refusal that echoes a huge
    pasted vertex, source or height thus cannot amplify the message. Resolved from the
    module namespace at call time so a mutation to it reddens the bounded-echo tests.

    ``repr`` itself never escapes this helper (DB-069 h / G5 INFO): a value whose
    ``repr`` raises - a ``RecursionError`` on deeply-nested data, or a hostile
    ``__repr__`` - yields the fixed ``<unrepresentable value>`` placeholder rather than
    propagating, so a refusal message can always be built."""
    try:
        text = repr(value)
    except Exception:  # noqa: BLE001 - a refusal preview must never itself raise
        return "<unrepresentable value>"
    if len(text) <= limit:
        return text
    return f"{text[:limit]}...<+{len(text) - limit} chars>"


def _is_finite_number(value: object) -> bool:
    """True for a finite int/float that is not a bool (JSON booleans are ints in
    Python and must never pass a numeric check).

    An int too large to convert to float (a JSON integer literal beyond the float
    range, e.g. ``10**400``) is treated as NON-finite (DB-069 g / G5 MED-1) instead of
    being allowed to raise ``OverflowError`` out of ``math.isfinite``: the caller then
    fails closed with the typed ``non_finite`` refusal rather than an untyped
    ``OverflowError`` escaping the builder. A finite float such as ``1e300`` is
    unaffected - it stays finite and hits the magnitude bound as before."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


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


def _require_raw_vertices_in_nyc_bounds(
    vertices: Sequence[_Point], field: str
) -> None:
    """Refuse when any RAW ring vertex is outside plausible NYC EPSG:2263 bounds (DB-069
    a / DB-061 c). Called from :func:`app.scenario.massing_triangulation._prepare_ring` on
    the lot ring BEFORE the collinear collapse, reusing the very :data:`NYC_2263_X_MIN` ..
    constants B0 applies to the proposal footprint (single source of truth) and naming
    ``field`` so the refusal points at the real culprit. EVERY vertex is checked (not only
    the first), on BOTH the easting and northing axes. Generous fail-closed unit guards,
    never a precise city boundary."""
    for x, y in vertices:
        if not (NYC_2263_X_MIN <= x <= NYC_2263_X_MAX
                and NYC_2263_Y_MIN <= y <= NYC_2263_Y_MAX):
            raise MassingModelError(
                f"lot_ring vertex ({x}, {y}) is outside plausible NYC EPSG:2263 bounds "
                f"([{NYC_2263_X_MIN}, {NYC_2263_X_MAX}] x [{NYC_2263_Y_MIN}, "
                f"{NYC_2263_Y_MAX}] US survey feet) - likely a wrong-unit or wrong-CRS "
                "lot; it is refused, never mislabelled",
                reason="lot_ring_out_of_nyc_bounds", field=field)


def _is_out_of_float_range_int(value: object) -> bool:
    """True for an ``int`` outside the finite float range - the value that makes B0's own
    ``math.isfinite`` raise ``OverflowError`` (a JSON integer literal such as ``10**400``).
    A bool, a float (even ``inf``), or a non-number is False: only an out-of-float-range
    int trips B0's ``OverflowError`` arm."""
    if isinstance(value, bool) or not isinstance(value, int):
        return False
    try:
        math.isfinite(value)
    except OverflowError:
        return True
    return False


def _outline_holds_overflow(outline: object) -> bool:
    """True when an outline's ``vertices`` contain an out-of-float-range int coordinate -
    the exact value B0 raises ``OverflowError`` on inside ``_validate_outline``."""
    if not isinstance(outline, Mapping):
        return False
    vertices = outline.get("vertices")
    if not isinstance(vertices, Sequence) or isinstance(vertices, (str, bytes)):
        return False
    for vertex in vertices:
        if (isinstance(vertex, Sequence) and not isinstance(vertex, (str, bytes))
                and len(vertex) == 2
                and (_is_out_of_float_range_int(vertex[0])
                     or _is_out_of_float_range_int(vertex[1]))):
            return True
    return False


def _locate_overflow_field(block: object) -> str:
    """Name the dotted field of the first out-of-float-range OUTLINE coordinate in a
    ``proposed_massing`` block, in B0's validation order (DB-079 b).

    B0 validates the footprint outline before the level outlines and raises a bare
    ``OverflowError`` (from ``math.isfinite`` on the huge int) that carries no field, so
    the builder's ``except OverflowError`` arm has to reconstruct WHERE the overflow sat.
    This mirrors that order - the footprint outline, then each level outline in list
    position order - and names the OUTLINE (matching B0's per-outline site), so a level
    outline overflow is labelled ``proposed_massing.levels[<pos>].outline`` instead of the
    former blanket ``proposed_massing.outline``. Fail-safe: an unwalkable block, or an
    overflow that sits in a non-outline field (e.g. a huge-int ``floor_to_floor_ft``, whose
    behaviour is unchanged), yields the ``proposed_massing.outline`` default this replaced,
    so no valid or previously-footprint-labelled refusal changes."""
    default = "proposed_massing.outline"
    if not isinstance(block, Mapping):
        return default
    if _outline_holds_overflow(block.get("outline")):
        return default  # == "proposed_massing.outline"
    levels = block.get("levels")
    if isinstance(levels, Sequence) and not isinstance(levels, (str, bytes)):
        for pos, level in enumerate(levels):
            if isinstance(level, Mapping) and _outline_holds_overflow(level.get("outline")):
                return f"proposed_massing.levels[{pos}].outline"
    return default
