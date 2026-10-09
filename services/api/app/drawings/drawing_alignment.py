"""D-087 PKT-L2 (phase C2) drawing-to-lot alignment service (pure; no route,
no persistence).

The alignment step the PDF sheet import (:mod:`app.drawings.sheet_import`, M5-T121)
and the local-frame DXF import (:mod:`app.drawings.dxf_import`, M5-T108) both need but
do NOT do. A correctly scaled import draft is an outline in a LOCAL frame (small,
near-origin feet), so :func:`app.scenario.proposal.validate_proposed_massing` refuses
it as outside the NYC EPSG:2263 bounds (DB-092, the key limit this closes). Phase C2:
"alignment to the mapped lot with any discrepancy shown, never auto-reconciled."

Given a ``proposed_massing`` draft block + its import provenance dict (as returned by
``sheet_import.build_draft`` / ``dxf_import.build_draft`` - duck-typed on the block's
documented shape; NEITHER import module is imported or edited here), the mapped lot ring
in EPSG:2263 US survey feet (the caller supplies it - this module fetches NOTHING), and
USER-CONFIRMED control-point pairs (local feet <-> 2263), :func:`align_draft_to_lot`:
(1) FITS a 2D RIGID transform (rotation + translation only; NO scale, NO reflection) and
moves the outline(s) into 2263; (2) SHOWS every discrepancy and reconciles NONE - the
per-pair residuals and the max against a declared tolerance, the pairs' IMPLIED scale vs
the confirmed 1.0, a better MIRROR fit (>= 3 pairs), and the outline area OUTSIDE the
lot; (3) RE-VALIDATES through the SAME contract (``provenance.kind`` stays
``"proposed"``); every failure is a typed :class:`AlignmentRefusal` VALUE; and (4)
returns the block plus an alignment provenance block.

MATH AUTHORITY (D-087; cited again next to the code): the rigid fit is the Kabsch /
orthogonal Procrustes solution restricted to PROPER rotations. For the centred pairs let
``dot = sum(ax*bx + ay*by)`` and ``cross = sum(ax*by - ay*bx)`` (``a`` centred source,
``b`` centred target); ``theta = atan2(cross, dot)``, with the rotation built directly
from ``cos = dot/hypot(dot,cross)`` / ``sin = cross/hypot(dot,cross)`` (no atan2 round
trip, so a right-angle fit stays exact) and ``translation = target_centroid - R @
source_centroid``. The IMPLIED scale (similarity fit, DISCLOSED only) is
``hypot(dot, cross) / sum(|a|^2)``.

Honesty and safety (D-076-R002 / D-083-R006): alignment is USER-CONFIRMED, never
automatic (no corner auto-matching); the input-precision label is kept EXACTLY
(``"imported drawing - not survey-confirmed"``) and NEVER upgraded; nothing is labelled
a record, a permit, ``"approved"``, or a ``"maximum allowed building"``; every
discrepancy is a DISCLOSED value, never a silent rescale / flip / clip; work is bounded
(declared caps), coordinates must be finite and source picks distinct, and every output
number is finite - a non-finite or out-of-bounds result is a typed refusal.
"""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass
from dataclasses import field as dc_field

from shapely.errors import GEOSException, ShapelyError
from shapely.geometry import Polygon

from app.scenario.proposal import ProposedMassingError, validate_proposed_massing

__all__ = [
    "ALIGNMENT_METHOD",
    "ALIGNMENT_PRECISION_NOTE",
    "CONFIRMED_SCALE",
    "DEFAULT_TOLERANCE_FT",
    "MAX_CONTROL_PAIRS",
    "MAX_LOT_RING_VERTICES",
    "MIN_CONTROL_PAIRS",
    "SCALE_DISCREPANCY_REL",
    "AlignmentRefusal",
    "AlignmentResult",
    "ControlPair",
    "PlaneTransform",
    "align_draft_to_lot",
]

# --- method + honesty vocabulary -----------------------------------------------------
ALIGNMENT_METHOD = "rigid-least-squares-2d/1"
ALIGNMENT_FORMULA = (
    "2D rigid least squares (Kabsch / orthogonal Procrustes, PROPER rotation only): "
    "theta = atan2(sum cross, sum dot) of the centred pairs; R built from "
    "cos = dot/hypot(dot,cross), sin = cross/hypot(dot,cross); "
    "translation = target_centroid - R @ source_centroid; NO scale, NO reflection"
)
# The confirmed scale the rigid fit assumes: the local frame is ALREADY in the user's
# confirmed feet (the import measured one edge), so alignment applies NO further scale.
CONFIRMED_SCALE = 1.0
ALIGNMENT_PRECISION_NOTE = (
    "alignment places the imported drawing on the mapped lot; it does not upgrade the "
    "input precision and does not claim survey accuracy"
)

# --- declared bounds / thresholds (fail-closed; NOT legal or survey values) ----------
# At least two pairs are needed to determine a rigid transform; with exactly two the
# fit is DETERMINED but UNCHECKED (no redundancy to detect a bad pick) - disclosed.
MIN_CONTROL_PAIRS = 2
# A paste / UI error far above any real control-point set fails closed.
MAX_CONTROL_PAIRS = 1000
# The mapped lot ring is the only caller-supplied unbounded input; cap it so the
# outside-lot shapely work cannot dominate wall time (a real lot ring is far smaller).
MAX_LOT_RING_VERTICES = 100_000
# Residual disclosure threshold (feet). A max residual above this is SHOWN as a
# discrepancy; it never changes the geometry. The caller may override it.
DEFAULT_TOLERANCE_FT = 2.0
# Relative gap from the confirmed scale (1.0) beyond which the pairs' IMPLIED scale is
# disclosed as a mismatch (the measured edge or a pick is likely wrong) - never applied.
SCALE_DISCREPANCY_REL = 0.01
# A mirror fit is disclosed only when it is strictly better than the rigid fit by more
# than this relative margin (guards against float noise); it is NEVER applied.
_MIRROR_IMPROVEMENT_REL = 1e-9
# Areas below this (sq ft) are treated as numerically zero for the outside-lot note.
_AREA_EPSILON_SQ_FT = 1e-6

# Discrepancy type tokens (closed vocabulary; each SHOWN, never reconciled).
DISC_TWO_PAIRS_UNCHECKED = "two_pairs_unchecked"
DISC_RESIDUAL_EXCEEDS_TOLERANCE = "residual_exceeds_tolerance"
DISC_SCALE_MISMATCH = "scale_mismatch"
DISC_BETTER_MIRROR_FIT = "better_mirror_fit"
DISC_OUTLINE_OUTSIDE_LOT = "outline_outside_lot"

_Point = tuple[float, float]


@dataclass(frozen=True)
class ControlPair:
    """A user-confirmed control-point pair: a point in the draft's LOCAL feet frame and
    the EPSG:2263 point the user placed it at. NEVER auto-matched from drawing content."""

    local: _Point
    target: _Point


@dataclass(frozen=True)
class PlaneTransform:
    """A 2D affine map ``[[m00, m01], [m10, m11]] @ p + (tx, ty)``. The APPLIED transform
    is always a PROPER rigid motion (``determinant`` = +1); the mirror fit (det = -1) is
    computed only to DISCLOSE a better mirror, never applied."""

    m00: float
    m01: float
    m10: float
    m11: float
    tx: float
    ty: float

    def apply(self, x: float, y: float) -> _Point:
        return (
            self.m00 * x + self.m01 * y + self.tx,
            self.m10 * x + self.m11 * y + self.ty,
        )

    @property
    def determinant(self) -> float:
        return self.m00 * self.m11 - self.m01 * self.m10


@dataclass(frozen=True)
class AlignmentResult:
    """A validated, lot-aligned draft (``ok = True``): ``proposed_massing`` has passed
    :func:`validate_proposed_massing` with the outline(s) in 2263; ``provenance`` is the
    input import-provenance kept EXACTLY (precision unchanged); ``alignment`` is the
    alignment provenance block; ``discrepancies`` are SHOWN, never reconciled."""

    ok: bool
    proposed_massing: dict
    provenance: dict
    alignment: dict
    discrepancies: tuple[dict, ...]


@dataclass(frozen=True)
class AlignmentRefusal:
    """Typed refusal VALUE (``ok = False``); never a raised exception. ``reason`` is a
    closed-vocabulary token, ``detail`` a bounded string, ``field`` the offending input;
    ``discrepancies`` carries conflicts detected before the refusal."""

    ok: bool
    reason: str
    detail: str
    field: str | None = None
    discrepancies: tuple[dict, ...] = dc_field(default_factory=tuple)


# --------------------------------------------------------------------------- helpers


def _is_real(value: object) -> bool:
    """A finite int/float that is not a bool (JSON ``true``/``false`` are ints)."""
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(value)
    )


def _coerce_point(pt: object) -> _Point | None | str:
    """Return ``(x, y)`` floats, ``None`` for a structurally-wrong point, or the string
    ``"nonfinite"`` when the shape is right but a component is non-finite/non-numeric."""
    if not isinstance(pt, (tuple, list)) or len(pt) != 2:
        return None
    x, y = pt[0], pt[1]
    if isinstance(x, bool) or isinstance(y, bool):
        return "nonfinite"
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
        return None
    if not math.isfinite(x) or not math.isfinite(y):
        return "nonfinite"
    return (float(x), float(y))


def _centroid(points: list[_Point]) -> _Point:
    n = len(points)
    return (sum(p[0] for p in points) / n, sum(p[1] for p in points) / n)


def _cross_dot_sumsq(
    source: list[_Point], target: list[_Point], cen_s: _Point, cen_t: _Point
) -> tuple[float, float, float]:
    """``(dot, cross, source_sum_of_squares)`` of the centred pairs (MATH AUTHORITY):
    ``dot = sum(ax*bx + ay*by)``, ``cross = sum(ax*by - ay*bx)`` (``a`` centred source,
    ``b`` centred target)."""
    dot = cross = saq = 0.0
    for (sx, sy), (tx_, ty_) in zip(source, target, strict=True):
        ax, ay = sx - cen_s[0], sy - cen_s[1]
        bx, by = tx_ - cen_t[0], ty_ - cen_t[1]
        dot += ax * bx + ay * by
        cross += ax * by - ay * bx
        saq += ax * ax + ay * ay
    return dot, cross, saq


def _applied_scale() -> float:
    """The scale the APPLIED transform uses. The rigid fit applies NONE (the confirmed
    scale is 1.0); the pairs' implied scale is DISCLOSED, never applied. A dedicated
    seam so a test can prove applying the implied scale would change the geometry."""
    return CONFIRMED_SCALE


def _compose(
    cos: float, sin: float, *, reflect: bool, cen_s: _Point, cen_t: _Point
) -> PlaneTransform:
    """Build the affine map from a rotation (proper ``[[c, -s], [s, c]]``) or reflection
    (improper ``[[c, s], [s, -c]]``, determinant -1) that sends the source centroid onto
    the target centroid, scaled by :func:`_applied_scale` (1.0 for the rigid fit)."""
    s = _applied_scale()
    if reflect:
        m00, m01, m10, m11 = s * cos, s * sin, s * sin, -s * cos
    else:
        m00, m01, m10, m11 = s * cos, -s * sin, s * sin, s * cos
    tx = cen_t[0] - (m00 * cen_s[0] + m01 * cen_s[1])
    ty = cen_t[1] - (m10 * cen_s[0] + m11 * cen_s[1])
    return PlaneTransform(m00, m01, m10, m11, tx, ty)


def _rigid_fit(source: list[_Point], target: list[_Point]) -> PlaneTransform:
    """The PROPER 2D rigid least-squares transform (MATH AUTHORITY). Callers guarantee
    the fit is non-degenerate (source not coincident, ``hypot(dot, cross) > 0``)."""
    cen_s, cen_t = _centroid(source), _centroid(target)
    dot, cross, _ = _cross_dot_sumsq(source, target, cen_s, cen_t)
    norm = math.hypot(dot, cross)
    return _compose(dot / norm, cross / norm, reflect=False, cen_s=cen_s, cen_t=cen_t)


def _mirror_fit(source: list[_Point], target: list[_Point]) -> PlaneTransform:
    """The best REFLECTION fit, computed ONLY to disclose a better mirror (never applied).
    For ``F(phi) = [[c2, s2], [s2, -c2]]`` the optimum is ``2*phi = atan2(q, p)`` with
    ``p = sum(bx*ax - by*ay)``, ``q = sum(bx*ay + by*ax)``."""
    cen_s, cen_t = _centroid(source), _centroid(target)
    p = q = 0.0
    for (sx, sy), (tx_, ty_) in zip(source, target, strict=True):
        ax, ay = sx - cen_s[0], sy - cen_s[1]
        bx, by = tx_ - cen_t[0], ty_ - cen_t[1]
        p += bx * ax - by * ay
        q += bx * ay + by * ax
    mnorm = math.hypot(p, q)
    if mnorm == 0.0:
        c2, s2 = 1.0, 0.0
    else:
        c2, s2 = p / mnorm, q / mnorm
    return _compose(c2, s2, reflect=True, cen_s=cen_s, cen_t=cen_t)


def _implied_scale(source: list[_Point], target: list[_Point]) -> float:
    """The scale the pairs IMPLY under a similarity fit: ``hypot(dot, cross) /
    sum(|a|^2)`` (MATH AUTHORITY). Disclosed against the confirmed 1.0, never applied."""
    cen_s, cen_t = _centroid(source), _centroid(target)
    dot, cross, saq = _cross_dot_sumsq(source, target, cen_s, cen_t)
    return math.hypot(dot, cross) / saq


def _residuals(
    transform: PlaneTransform, source: list[_Point], target: list[_Point]
) -> list[float]:
    """Per-pair fit residual in feet: ``|transform(source_i) - target_i|`` for EVERY
    pair (the discrepancy record shows them all)."""
    out: list[float] = []
    for (sx, sy), (tx_, ty_) in zip(source, target, strict=True):
        px, py = transform.apply(sx, sy)
        out.append(math.hypot(px - tx_, py - ty_))
    return out


def _rms(values: list[float]) -> float:
    return math.sqrt(sum(v * v for v in values) / len(values)) if values else 0.0


def _choose_transform(
    rigid: PlaneTransform,
    mirror: PlaneTransform,
    rigid_rms: float,
    mirror_rms: float,
) -> PlaneTransform:
    """The APPLIED transform: ALWAYS the proper rigid fit - a better mirror is disclosed,
    NEVER flipped to. A seam so a test can prove applying the mirror would change the
    placement (orientation)."""
    return rigid


def _final_outline_vertices(vertices: list[list[float]], lot_ring: list[_Point]):
    """The outline vertices the aligned draft carries: the FULL transformed ring, NEVER
    clipped to the lot (the outside-lot area is DISCLOSED, not removed). A seam so a test
    can prove clipping would change the geometry."""
    return vertices


def _is_unchecked_two_pair(pair_count: int) -> bool:
    """Whether the fit is DETERMINED but UNCHECKED - exactly the minimum pairs, so no
    redundancy detects a bad pick. A dedicated seam so a test can prove the two-pair
    disclosure is load-bearing."""
    return pair_count == MIN_CONTROL_PAIRS


class _BadBlock(Exception):
    """Internal: the input draft block is not the documented shape (mapped to a typed
    ``bad_draft_block`` refusal). Never escapes the module."""


def _transform_vertices(
    outline: object, transform: PlaneTransform, lot_ring: list[_Point], *, footprint: bool
) -> list[list[float]]:
    """Transform one outline's vertices into 2263 (reads only ``outline["vertices"]`` as
    finite ``[x, y]`` pairs - the OUTPUT contract is enforced by
    :func:`validate_proposed_massing`). The footprint routes through the never-clip seam
    :func:`_final_outline_vertices`."""
    if not isinstance(outline, dict):
        raise _BadBlock("outline must be an object")
    vertices = outline.get("vertices")
    if not isinstance(vertices, list) or len(vertices) < 1:
        raise _BadBlock("outline.vertices must be a non-empty array")
    moved: list[list[float]] = []
    for vertex in vertices:
        pt = _coerce_point(vertex)
        if not isinstance(pt, tuple):
            raise _BadBlock("outline.vertices must be finite [x, y] pairs")
        moved.append(list(transform.apply(pt[0], pt[1])))
    if footprint:
        moved = _final_outline_vertices(moved, lot_ring)
    return moved


def _transform_block(
    block: object, transform: PlaneTransform, lot_ring: list[_Point]
) -> dict:
    """Deep-copy the draft block and transform every outline (footprint + any per-level
    outline) into 2263, preserving levels, walls and provenance verbatim. Raises
    :class:`_BadBlock` when the block is not the documented shape."""
    if not isinstance(block, dict):
        raise _BadBlock("proposed_massing must be an object")
    out = copy.deepcopy(block)
    out_outline = out.get("outline")
    if not isinstance(out_outline, dict):
        raise _BadBlock("proposed_massing.outline must be an object")
    out_outline["vertices"] = _transform_vertices(
        out_outline, transform, lot_ring, footprint=True
    )
    levels = out.get("levels")
    if isinstance(levels, list):
        for level in levels:
            if isinstance(level, dict) and isinstance(level.get("outline"), dict):
                level["outline"]["vertices"] = _transform_vertices(
                    level["outline"], transform, lot_ring, footprint=False
                )
    return out


def _distinct_ring(vertices: list[list[float]]) -> list[_Point]:
    """The distinct ring points (drop a repeated closing vertex) as float tuples."""
    pts = [(float(x), float(y)) for x, y in vertices]
    if len(pts) >= 2 and pts[0] == pts[-1]:
        pts = pts[:-1]
    return pts


def _safe_polygon(ring: list[_Point]) -> Polygon | None:
    """A shapely polygon from a ring, repaired with ``buffer(0)`` when invalid; ``None``
    when it cannot be made a usable polygon (the outside-lot area is then disclosed as
    unavailable, never a silent guess)."""
    try:
        poly = Polygon(ring)
        if not poly.is_valid:
            poly = poly.buffer(0)
        if poly.is_empty or poly.area == 0.0:
            return None
        return poly
    except (GEOSException, ShapelyError, ValueError):
        return None


def _outside_lot_area(
    outline_ring: list[_Point], lot_ring: list[_Point]
) -> float | None:
    """Area (sq ft, 2263) of the aligned outline OUTSIDE the mapped lot,
    ``outline.area - (outline ∩ lot).area``; DISCLOSED, never clipped. ``None`` when a
    polygon is unusable (surfaced honestly, never a silent zero)."""
    outline_poly = _safe_polygon(outline_ring)
    lot_poly = _safe_polygon(lot_ring)
    if outline_poly is None or lot_poly is None:
        return None
    try:
        inside = float(outline_poly.intersection(lot_poly).area)
    except (GEOSException, ShapelyError, ValueError):
        return None
    outside = float(outline_poly.area) - inside
    return outside if outside > _AREA_EPSILON_SQ_FT else 0.0


def _input_precision(provenance: object) -> str | None:
    """The input-precision label carried into the alignment block from the import
    provenance UNCHANGED (alignment upgrades precision NOWHERE). A seam so a test can
    prove an upgrade here would be caught."""
    if isinstance(provenance, dict):
        value = provenance.get("precision")
        if isinstance(value, str):
            return value
    return None


def _validate_lot_ring(lot_ring: object) -> list[_Point] | AlignmentRefusal:
    if not isinstance(lot_ring, (list, tuple)):
        return AlignmentRefusal(
            ok=False, reason="bad_lot_ring", detail="lot_ring must be a list of [x, y]",
            field="lot_ring",
        )
    if len(lot_ring) > MAX_LOT_RING_VERTICES:
        return AlignmentRefusal(
            ok=False, reason="bad_lot_ring",
            detail=f"lot_ring exceeds MAX_LOT_RING_VERTICES ({MAX_LOT_RING_VERTICES})",
            field="lot_ring",
        )
    points: list[_Point] = []
    for vertex in lot_ring:
        pt = _coerce_point(vertex)
        if pt == "nonfinite":
            return AlignmentRefusal(
                ok=False, reason="non_finite_input",
                detail="lot_ring has a non-finite coordinate", field="lot_ring",
            )
        if not isinstance(pt, tuple):
            return AlignmentRefusal(
                ok=False, reason="bad_lot_ring",
                detail="lot_ring must be a list of finite [x, y] pairs", field="lot_ring",
            )
        points.append(pt)
    if len(_distinct_ring([list(p) for p in points])) < 3:
        return AlignmentRefusal(
            ok=False, reason="bad_lot_ring",
            detail="lot_ring needs at least 3 distinct vertices", field="lot_ring",
        )
    return points


def _validate_pairs(
    control_pairs: object,
) -> tuple[list[_Point], list[_Point]] | AlignmentRefusal:
    if not isinstance(control_pairs, (list, tuple)):
        return AlignmentRefusal(
            ok=False, reason="bad_control_pair",
            detail="control_pairs must be a list of ControlPair or (local, target)",
            field="control_pairs",
        )
    if len(control_pairs) < MIN_CONTROL_PAIRS:
        return AlignmentRefusal(
            ok=False, reason="too_few_pairs",
            detail=(
                f"a rigid fit needs at least {MIN_CONTROL_PAIRS} user-confirmed control "
                f"pairs; got {len(control_pairs)}"
            ),
            field="control_pairs",
        )
    if len(control_pairs) > MAX_CONTROL_PAIRS:
        return AlignmentRefusal(
            ok=False, reason="too_many_pairs",
            detail=f"control_pairs exceeds MAX_CONTROL_PAIRS ({MAX_CONTROL_PAIRS})",
            field="control_pairs",
        )
    source: list[_Point] = []
    target: list[_Point] = []
    for pair in control_pairs:
        if isinstance(pair, ControlPair):
            local_raw, target_raw = pair.local, pair.target
        elif isinstance(pair, (tuple, list)) and len(pair) == 2:
            local_raw, target_raw = pair[0], pair[1]
        else:
            return AlignmentRefusal(
                ok=False, reason="bad_control_pair",
                detail="each control pair must be a ControlPair or a (local, target) pair",
                field="control_pairs",
            )
        local, target_pt = _coerce_point(local_raw), _coerce_point(target_raw)
        if local == "nonfinite" or target_pt == "nonfinite":
            return AlignmentRefusal(
                ok=False, reason="non_finite_input",
                detail="a control-point coordinate is non-finite", field="control_pairs",
            )
        if not isinstance(local, tuple) or not isinstance(target_pt, tuple):
            return AlignmentRefusal(
                ok=False, reason="bad_control_pair",
                detail="each control point must be a finite [x, y] pair",
                field="control_pairs",
            )
        source.append(local)
        target.append(target_pt)
    return source, target


def _build_alignment_block(
    *,
    source: list[_Point],
    target: list[_Point],
    transform: PlaneTransform,
    residuals: list[float],
    tolerance_ft: float,
    implied_scale: float,
    mirror_rms: float | None,
    outline_ring: list[_Point],
    lot_ring: list[_Point],
    provenance: object,
) -> tuple[dict, list[dict]]:
    """Assemble the alignment provenance block and the discrepancy list (SHOWN, never
    reconciled). Returns ``(alignment_block, discrepancies)``."""
    rotation_rad = math.atan2(transform.m10, transform.m00)
    max_residual = max(residuals) if residuals else 0.0
    outside = _outside_lot_area(outline_ring, lot_ring)
    outline_poly = _safe_polygon(outline_ring)
    outline_area = float(outline_poly.area) if outline_poly is not None else None

    discrepancies: list[dict] = []
    if _is_unchecked_two_pair(len(source)):
        discrepancies.append({
            "type": DISC_TWO_PAIRS_UNCHECKED,
            "detail": "two pairs: the fit is determined but UNCHECKED; add a third to verify",
        })
    if max_residual > tolerance_ft:
        discrepancies.append({
            "type": DISC_RESIDUAL_EXCEEDS_TOLERANCE,
            "max_residual_ft": max_residual,
            "tolerance_ft": tolerance_ft,
            "detail": "largest residual exceeds tolerance; verify picks - geometry not adjusted",
        })
    if abs(implied_scale - CONFIRMED_SCALE) > SCALE_DISCREPANCY_REL * CONFIRMED_SCALE:
        discrepancies.append({
            "type": DISC_SCALE_MISMATCH,
            "implied_scale": implied_scale,
            "confirmed_scale": CONFIRMED_SCALE,
            "detail": "pairs imply a scale != the confirmed 1.0; SHOWN, never rescaled",
        })
    rigid_rms = _rms(residuals)
    if mirror_rms is not None and mirror_rms < rigid_rms * (1.0 - _MIRROR_IMPROVEMENT_REL):
        discrepancies.append({
            "type": DISC_BETTER_MIRROR_FIT,
            "rigid_rms_residual_ft": rigid_rms,
            "mirror_rms_residual_ft": mirror_rms,
            "detail": "a mirror fit matches better; drawing may be mirrored - SHOWN, never flipped",
        })
    if outside is not None and outside > _AREA_EPSILON_SQ_FT:
        discrepancies.append({
            "type": DISC_OUTLINE_OUTSIDE_LOT,
            "area_sq_ft": outside,
            "detail": "part of the aligned outline is outside the lot - SHOWN, never clipped",
        })

    alignment = {
        "method": ALIGNMENT_METHOD,
        "formula": ALIGNMENT_FORMULA,
        "pair_count": len(source),
        "rotation_rad": rotation_rad,
        "rotation_deg": math.degrees(rotation_rad),
        "translation_ft": [transform.tx, transform.ty],
        "residuals_ft": list(residuals),
        "max_residual_ft": max_residual,
        "rms_residual_ft": rigid_rms,
        "tolerance_ft": tolerance_ft,
        "confirmed_scale": CONFIRMED_SCALE,
        "implied_scale": implied_scale,
        "mirror_rms_residual_ft": mirror_rms,
        "outline_area_sq_ft": outline_area,
        "outline_area_outside_lot_sq_ft": outside,
        "input_precision": _input_precision(provenance),
        "precision_note": ALIGNMENT_PRECISION_NOTE,
        "discrepancies": discrepancies,
    }
    return alignment, discrepancies


def _finite_numbers(alignment: dict) -> bool:
    """Whether every numeric value the alignment block emits is finite (JSON-safe under
    ``allow_nan=False``); ``None`` (a disclosed-unavailable value) is allowed."""
    scalars = (
        alignment["rotation_rad"], alignment["rotation_deg"], alignment["max_residual_ft"],
        alignment["rms_residual_ft"], alignment["tolerance_ft"], alignment["confirmed_scale"],
        alignment["implied_scale"], *alignment["translation_ft"], *alignment["residuals_ft"],
    )
    optional = (
        alignment["mirror_rms_residual_ft"], alignment["outline_area_sq_ft"],
        alignment["outline_area_outside_lot_sq_ft"],
    )
    if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in scalars):
        return False
    return all(v is None or (isinstance(v, (int, float)) and math.isfinite(v)) for v in optional)


def align_draft_to_lot(
    draft_block: object,
    provenance: object,
    lot_ring: object,
    control_pairs: object,
    *,
    tolerance_ft: float = DEFAULT_TOLERANCE_FT,
) -> AlignmentResult | AlignmentRefusal:
    """Place an import draft's LOCAL-frame outline onto the mapped lot by a 2D RIGID fit
    through user-confirmed control-point pairs, disclose every discrepancy (never
    reconciled), and re-validate through :func:`validate_proposed_massing`. Fetches
    nothing and raises nothing - every failure is a typed :class:`AlignmentRefusal`
    VALUE; nothing is labelled a record, permit, approved or maximum-allowed building;
    the input-precision label is kept EXACTLY."""
    if not (_is_real(tolerance_ft) and tolerance_ft >= 0.0):
        return AlignmentRefusal(
            ok=False, reason="non_finite_input",
            detail="tolerance_ft must be a finite, non-negative number", field="tolerance_ft",
        )

    pairs = _validate_pairs(control_pairs)
    if isinstance(pairs, AlignmentRefusal):
        return pairs
    source, target = pairs

    lot = _validate_lot_ring(lot_ring)
    if isinstance(lot, AlignmentRefusal):
        return lot

    # Fit degeneracy: coincident source picks cannot determine a rotation, and a
    # zero-magnitude (dot, cross) cannot determine an angle. Both are typed refusals.
    cen_s, cen_t = _centroid(source), _centroid(target)
    dot, cross, saq = _cross_dot_sumsq(source, target, cen_s, cen_t)
    if saq == 0.0:
        return AlignmentRefusal(
            ok=False, reason="coincident_source",
            detail="all source control points coincide; a rotation cannot be determined",
            field="control_pairs",
        )
    if math.hypot(dot, cross) == 0.0:
        return AlignmentRefusal(
            ok=False, reason="indeterminate_rotation",
            detail="the control pairs do not determine a rotation angle",
            field="control_pairs",
        )

    rigid = _rigid_fit(source, target)
    mirror = _mirror_fit(source, target)
    rigid_residuals = _residuals(rigid, source, target)
    mirror_rms = (
        _rms(_residuals(mirror, source, target)) if len(source) >= 3 else None
    )
    applied = _choose_transform(rigid, mirror, _rms(rigid_residuals), mirror_rms or 0.0)

    try:
        aligned_block = _transform_block(draft_block, applied, lot)
    except _BadBlock as exc:
        return AlignmentRefusal(
            ok=False, reason="bad_draft_block", detail=str(exc), field="proposed_massing",
        )

    try:
        validate_proposed_massing(aligned_block)
    except ProposedMassingError as exc:
        return AlignmentRefusal(
            ok=False, reason="aligned_invalid", detail=str(exc), field=exc.field,
        )

    outline_ring = _distinct_ring(aligned_block["outline"]["vertices"])
    alignment, discrepancies = _build_alignment_block(
        source=source, target=target, transform=applied, residuals=rigid_residuals,
        tolerance_ft=tolerance_ft, implied_scale=_implied_scale(source, target),
        mirror_rms=mirror_rms, outline_ring=outline_ring, lot_ring=lot,
        provenance=provenance,
    )
    if not _finite_numbers(alignment):
        return AlignmentRefusal(
            ok=False, reason="non_finite_result",
            detail="an aligned output number is non-finite; the fit is refused",
            field="control_pairs", discrepancies=tuple(discrepancies),
        )

    return AlignmentResult(
        ok=True,
        proposed_massing=aligned_block,
        provenance=copy.deepcopy(provenance) if isinstance(provenance, dict) else {},
        alignment=alignment,
        discrepancies=tuple(discrepancies),
    )
