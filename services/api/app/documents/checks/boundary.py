"""Deterministic boundary checks over already-validated survey facts (M2-T015 SB-S3).

The first two checks of the survey-ingestion packet's DETERMINISTIC CHECKS clause:

- :func:`boundary_closure` — closure error of an ordered boundary traverse.
- :func:`segment_sum_consistency` — sum of stated part distances against a stated whole.

Both consume ONLY the resolved typed results of :mod:`app.documents.units`
(:class:`~app.documents.units.ValidatedDistance`,
:class:`~app.documents.units.ValidatedBearing`) — never raw wire values, never AI
output — and return the frozen typed results of :mod:`app.documents.checks`, never
raising for a check-domain outcome. Every tolerance is a REQUIRED caller statement in
the same stated unit as the distances, recorded verbatim in the result; nothing is
defaulted, converted, wrapped, or guessed. Bearings are canonical decimal degrees
measured clockwise from north — ``AngleUnit.DEGREES`` is the only angle unit this
arithmetic is grounded for, so any other stated angle unit refuses closed.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from app.documents.checks import (
    CheckFailed,
    CheckPassed,
    CheckResult,
    CheckUnevaluable,
)
from app.documents.units import AngleUnit, ValidatedBearing, ValidatedDistance

__all__ = ["boundary_closure", "segment_sum_consistency"]

_BOUNDARY_CLOSURE = "boundary_closure"
_SEGMENT_SUM_CONSISTENCY = "segment_sum_consistency"


# ---------------------------------------------------------------------- helpers


def _tolerance_reason(tolerance: object) -> str | None:
    """The refusal reason for an unusable stated tolerance, or ``None`` when usable.

    The tolerance is a REQUIRED caller statement — never defaulted or guessed — and
    must be a finite non-negative number: comparing against a non-number, non-finite,
    or negative tolerance would silently disguise a malformed statement as a
    substantive PASS or FAIL, so it refuses instead.
    """
    if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)):
        return (
            "tolerance must be a stated finite non-negative number, got "
            f"{type(tolerance).__name__} — it is never defaulted, parsed, or coerced"
        )
    if not math.isfinite(tolerance):
        return f"tolerance must be a finite number, got {tolerance!r}"
    if tolerance < 0:
        return (
            f"tolerance must be non-negative, got {tolerance!r}; no computed magnitude "
            "could ever satisfy it, so the statement is refused as ambiguous rather "
            "than reported as a substantive failure"
        )
    return None


def _distances_reason(distances: Sequence[object], role: str) -> str | None:
    """The refusal reason for an unusable distance sequence, or ``None`` when usable.

    Usable means every element is the resolved :class:`ValidatedDistance` type and all
    elements state one single unit member — a stated value is never converted, so a
    mixed-unit sequence (possible once ``DistanceUnit`` extends additively) has no
    single deterministic sum or magnitude and refuses closed.
    """
    for index, candidate in enumerate(distances):
        if not isinstance(candidate, ValidatedDistance):
            return (
                f"{role}[{index}] must be a resolved ValidatedDistance, got "
                f"{type(candidate).__name__} — raw wire values, unresolved results, "
                "and AI output are never consumed or coerced here"
            )
    units = {distance.unit for distance in distances}
    if len(units) > 1:
        stated = ", ".join(sorted(repr(unit) for unit in units))
        return (
            f"{role} state mixed units ({stated}); a stated value is never converted "
            "between units, so one shared stated unit is required"
        )
    return None


# ----------------------------------------------------------------------- checks


def boundary_closure(
    distances: Sequence[ValidatedDistance],
    bearings: Sequence[ValidatedBearing],
    *,
    tolerance: int | float,
) -> CheckResult:
    """Deterministic closure check for an ordered boundary traverse.

    Given one resolved ``ValidatedDistance`` segment length per resolved
    ``ValidatedBearing`` direction — lengths all in one shared stated unit, bearings in
    canonical decimal degrees measured clockwise from north — computes the closure
    error vector

        dx = sum(d * sin(radians(bearing)))   (east component)
        dy = sum(d * cos(radians(bearing)))   (north component)

    and its magnitude ``hypot(dx, dy)``, all recorded verbatim in the result. PASSES
    iff the magnitude is <= the caller-stated ``tolerance`` (same unit as the
    distances; REQUIRED — never defaulted); FAILS carrying the computed misclosure
    otherwise; refuses as UNEVALUABLE — never coercing — when the tolerance is
    unusable, the distance/bearing counts mismatch, the traverse has fewer than 3
    segments, any input is not the required resolved type, distance units are mixed,
    or any bearing states an angle unit other than degrees.
    """
    tolerance_reason = _tolerance_reason(tolerance)
    if tolerance_reason is not None:
        return CheckUnevaluable(check_name=_BOUNDARY_CLOSURE, reason=tolerance_reason)
    if len(distances) != len(bearings):
        return CheckUnevaluable(
            check_name=_BOUNDARY_CLOSURE,
            reason=(
                "boundary_closure needs exactly one bearing per distance segment, got "
                f"{len(distances)} distances and {len(bearings)} bearings — inputs are "
                "never truncated or padded to fit"
            ),
        )
    if len(distances) < 3:
        return CheckUnevaluable(
            check_name=_BOUNDARY_CLOSURE,
            reason=(
                f"a closed boundary traverse needs at least 3 segments, got "
                f"{len(distances)}"
            ),
        )
    distances_reason = _distances_reason(distances, "distances")
    if distances_reason is not None:
        return CheckUnevaluable(check_name=_BOUNDARY_CLOSURE, reason=distances_reason)
    for index, candidate in enumerate(bearings):
        if not isinstance(candidate, ValidatedBearing):
            return CheckUnevaluable(
                check_name=_BOUNDARY_CLOSURE,
                reason=(
                    f"bearings[{index}] must be a resolved ValidatedBearing, got "
                    f"{type(candidate).__name__} — raw wire values, unresolved "
                    "results, and AI output are never consumed or coerced here"
                ),
            )
        if candidate.unit is not AngleUnit.DEGREES:
            return CheckUnevaluable(
                check_name=_BOUNDARY_CLOSURE,
                reason=(
                    "the closure arithmetic is grounded only for bearings stated in "
                    f"'degrees'; bearings[{index}] states {candidate.unit!r} and is "
                    "never converted"
                ),
            )
    dx = math.fsum(
        distance.value * math.sin(math.radians(bearing.value))
        for distance, bearing in zip(distances, bearings, strict=True)
    )
    dy = math.fsum(
        distance.value * math.cos(math.radians(bearing.value))
        for distance, bearing in zip(distances, bearings, strict=True)
    )
    magnitude = math.hypot(dx, dy)
    computed = {
        "segment_count": len(distances),
        "closure_dx": dx,
        "closure_dy": dy,
        "closure_magnitude": magnitude,
    }
    result_type = CheckPassed if magnitude <= tolerance else CheckFailed
    return result_type(
        check_name=_BOUNDARY_CLOSURE,
        unit=distances[0].unit.value,
        tolerance=tolerance,
        computed=computed,
    )


def segment_sum_consistency(
    parts: Sequence[ValidatedDistance],
    whole: ValidatedDistance,
    *,
    tolerance: int | float,
) -> CheckResult:
    """Deterministic parts-vs-whole distance consistency check.

    Given resolved ``ValidatedDistance`` parts and a stated resolved
    ``ValidatedDistance`` whole, all in one shared stated unit, computes
    ``parts_sum = fsum(part values)`` and the signed
    ``difference = parts_sum - whole``, both recorded verbatim in the result. PASSES
    iff ``abs(difference)`` is <= the caller-stated ``tolerance`` (same unit;
    REQUIRED — never defaulted); FAILS carrying the computed difference otherwise;
    refuses as UNEVALUABLE — never coercing — on an unusable tolerance, empty parts,
    any input that is not the required resolved type, or mixed units (among the parts
    or between the parts and the whole).
    """
    tolerance_reason = _tolerance_reason(tolerance)
    if tolerance_reason is not None:
        return CheckUnevaluable(
            check_name=_SEGMENT_SUM_CONSISTENCY, reason=tolerance_reason
        )
    if not isinstance(whole, ValidatedDistance):
        return CheckUnevaluable(
            check_name=_SEGMENT_SUM_CONSISTENCY,
            reason=(
                "the stated whole must be a resolved ValidatedDistance, got "
                f"{type(whole).__name__} — raw wire values, unresolved results, and "
                "AI output are never consumed or coerced here"
            ),
        )
    if len(parts) == 0:
        return CheckUnevaluable(
            check_name=_SEGMENT_SUM_CONSISTENCY,
            reason=(
                "segment_sum_consistency needs at least one part distance, got an "
                "empty sequence — an empty sum is never compared against the stated "
                "whole"
            ),
        )
    parts_reason = _distances_reason(parts, "parts")
    if parts_reason is not None:
        return CheckUnevaluable(check_name=_SEGMENT_SUM_CONSISTENCY, reason=parts_reason)
    if whole.unit is not parts[0].unit:
        return CheckUnevaluable(
            check_name=_SEGMENT_SUM_CONSISTENCY,
            reason=(
                f"parts are stated in {parts[0].unit!r} but the whole is stated in "
                f"{whole.unit!r}; a stated value is never converted between units"
            ),
        )
    parts_sum = math.fsum(part.value for part in parts)
    difference = parts_sum - whole.value
    computed = {
        "part_count": len(parts),
        "parts_sum": parts_sum,
        "stated_whole": whole.value,
        "difference": difference,
    }
    result_type = CheckPassed if abs(difference) <= tolerance else CheckFailed
    return result_type(
        check_name=_SEGMENT_SUM_CONSISTENCY,
        unit=whole.unit.value,
        tolerance=tolerance,
        computed=computed,
    )
