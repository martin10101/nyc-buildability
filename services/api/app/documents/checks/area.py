"""Deterministic area and dimension-consistency checks over already-validated survey
facts (M2-T015 SB-S3, part 2).

The second pair of checks of the survey-ingestion packet's DETERMINISTIC CHECKS clause:

- :func:`calculated_vs_stated_area` — shoelace polygon area of an ordered closed
  boundary traverse against a stated area.
- :func:`contradictory_dimensions` — restatements of the SAME physical dimension
  against that dimension's first statement.

Same ground rules as :mod:`app.documents.checks.boundary`, whose refusal helpers this
module deliberately reuses so the tolerance and resolved-input discipline stays
single-sourced: checks consume ONLY the resolved typed results of
:mod:`app.documents.units` — never raw wire values, never AI output — return the frozen
typed results of :mod:`app.documents.checks`, never raise for a check-domain outcome,
and never default, convert, wrap, or guess a stated value, unit, or tolerance. The one
grounded distance→area unit pairing is feet → square_feet; every other pairing refuses
closed rather than converting.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

from app.documents.checks import (
    CheckFailed,
    CheckPassed,
    CheckResult,
    CheckUnevaluable,
)
from app.documents.checks.boundary import _distances_reason, _tolerance_reason
from app.documents.units import (
    AngleUnit,
    AreaUnit,
    DistanceUnit,
    ValidatedArea,
    ValidatedBearing,
    ValidatedDistance,
)

__all__ = ["calculated_vs_stated_area", "contradictory_dimensions"]

_CALCULATED_VS_STATED_AREA = "calculated_vs_stated_area"
_CONTRADICTORY_DIMENSIONS = "contradictory_dimensions"

# The only grounded pairing between a stated distance unit and the unit of a polygon
# area computed from those distances. Extended additively only, together with the
# deterministic tests that ground each new pairing; a pairing absent here refuses
# closed — a stated area is never converted to fit.
_SQUARE_UNIT_OF: Mapping[DistanceUnit, AreaUnit] = {
    DistanceUnit.FEET: AreaUnit.SQUARE_FEET,
}


# ---------------------------------------------------------------------- helpers


def _bearings_reason(bearings: Sequence[object]) -> str | None:
    """The refusal reason for an unusable bearing sequence, or ``None`` when usable.

    Usable means every element is the resolved :class:`ValidatedBearing` type stated in
    canonical decimal degrees — the only angle unit the polygon-area arithmetic is
    grounded for; any other stated angle unit refuses closed and is never converted.
    """
    for index, candidate in enumerate(bearings):
        if not isinstance(candidate, ValidatedBearing):
            return (
                f"bearings[{index}] must be a resolved ValidatedBearing, got "
                f"{type(candidate).__name__} — raw wire values, unresolved results, "
                "and AI output are never consumed or coerced here"
            )
        if candidate.unit is not AngleUnit.DEGREES:
            return (
                "the polygon-area arithmetic is grounded only for bearings stated in "
                f"'degrees'; bearings[{index}] states {candidate.unit!r} and is never "
                "converted"
            )
    return None


# ----------------------------------------------------------------------- checks


def calculated_vs_stated_area(
    distances: Sequence[ValidatedDistance],
    bearings: Sequence[ValidatedBearing],
    stated: ValidatedArea,
    *,
    tolerance: int | float,
) -> CheckResult:
    """Deterministic calculated-vs-stated area check for an ordered closed traverse.

    Given one resolved ``ValidatedDistance`` segment length per resolved
    ``ValidatedBearing`` direction — the same traverse rules as
    :func:`app.documents.checks.boundary.boundary_closure`: at least 3 segments, one
    shared stated distance unit, bearings in canonical decimal degrees measured
    clockwise from north — accumulates the traverse vertices from the origin

        x_k = x_{k-1} + d_k * sin(radians(bearing_k))   (east component)
        y_k = y_{k-1} + d_k * cos(radians(bearing_k))   (north component)

    and computes the enclosed polygon area with the shoelace formula over the vertex
    ring (absolute value, so traversal direction never matters):

        area = abs(fsum(x_i * y_{i+1}  -  x_{i+1} * y_i)) / 2

    The stated area's unit MUST be the square of the shared distance unit
    (feet → square_feet, the only grounded pairing); any other pairing refuses as
    UNEVALUABLE, never converted. PASSES iff ``abs(computed_area - stated_area)`` is
    <= the caller-stated ``tolerance`` (stated in the same square unit; REQUIRED —
    never defaulted), both numbers recorded verbatim in the result; FAILS carrying the
    same verbatim numbers otherwise; refuses as UNEVALUABLE — never coercing — when
    the tolerance is unusable, the stated area is not the required resolved type, the
    distance/bearing counts mismatch, the traverse has fewer than 3 segments, any
    input is not the required resolved type, distance units are mixed, any bearing
    states an angle unit other than degrees, or the distance/area unit pairing is not
    grounded.
    """
    tolerance_reason = _tolerance_reason(tolerance)
    if tolerance_reason is not None:
        return CheckUnevaluable(
            check_name=_CALCULATED_VS_STATED_AREA, reason=tolerance_reason
        )
    if not isinstance(stated, ValidatedArea):
        return CheckUnevaluable(
            check_name=_CALCULATED_VS_STATED_AREA,
            reason=(
                "the stated area must be a resolved ValidatedArea, got "
                f"{type(stated).__name__} — raw wire values, unresolved results, and "
                "AI output are never consumed or coerced here"
            ),
        )
    if len(distances) != len(bearings):
        return CheckUnevaluable(
            check_name=_CALCULATED_VS_STATED_AREA,
            reason=(
                "calculated_vs_stated_area needs exactly one bearing per distance "
                f"segment, got {len(distances)} distances and {len(bearings)} "
                "bearings — inputs are never truncated or padded to fit"
            ),
        )
    if len(distances) < 3:
        return CheckUnevaluable(
            check_name=_CALCULATED_VS_STATED_AREA,
            reason=(
                f"a closed boundary traverse needs at least 3 segments, got "
                f"{len(distances)}"
            ),
        )
    distances_reason = _distances_reason(distances, "distances")
    if distances_reason is not None:
        return CheckUnevaluable(
            check_name=_CALCULATED_VS_STATED_AREA, reason=distances_reason
        )
    bearings_reason = _bearings_reason(bearings)
    if bearings_reason is not None:
        return CheckUnevaluable(
            check_name=_CALCULATED_VS_STATED_AREA, reason=bearings_reason
        )
    expected_area_unit = _SQUARE_UNIT_OF.get(distances[0].unit)
    if expected_area_unit is None:
        return CheckUnevaluable(
            check_name=_CALCULATED_VS_STATED_AREA,
            reason=(
                "no grounded square-area unit pairing exists for distances stated in "
                f"{distances[0].unit!r}; the computed polygon area would have no "
                "stated unit, and a stated area is never converted to fit"
            ),
        )
    if stated.unit is not expected_area_unit:
        return CheckUnevaluable(
            check_name=_CALCULATED_VS_STATED_AREA,
            reason=(
                f"distances are stated in {distances[0].unit!r}, so the computed "
                f"polygon area is in {expected_area_unit!r}, but the stated area is "
                f"in {stated.unit!r}; a stated value is never converted between units"
            ),
        )
    vertices: list[tuple[float, float]] = [(0.0, 0.0)]
    x = 0.0
    y = 0.0
    for distance, bearing in zip(distances, bearings, strict=True):
        x += distance.value * math.sin(math.radians(bearing.value))
        y += distance.value * math.cos(math.radians(bearing.value))
        vertices.append((x, y))
    cross_sum = math.fsum(
        vertices[index][0] * vertices[(index + 1) % len(vertices)][1]
        - vertices[(index + 1) % len(vertices)][0] * vertices[index][1]
        for index in range(len(vertices))
    )
    computed_area = abs(cross_sum) / 2.0
    difference = computed_area - stated.value
    computed = {
        "segment_count": len(distances),
        "computed_area": computed_area,
        "stated_area": stated.value,
        "difference": difference,
    }
    result_type = CheckPassed if abs(difference) <= tolerance else CheckFailed
    return result_type(
        check_name=_CALCULATED_VS_STATED_AREA,
        unit=stated.unit.value,
        tolerance=tolerance,
        computed=computed,
    )


def contradictory_dimensions(
    statements: Mapping[str, Sequence[ValidatedDistance]],
    *,
    tolerance: int | float,
) -> CheckResult:
    """Deterministic same-dimension restatement consistency check.

    Given a mapping of dimension label → the resolved ``ValidatedDistance`` statements
    of that ONE physical dimension (e.g. a boundary segment stated on multiple survey
    pages), compares every restatement within each label against the label's FIRST
    statement. PASSES iff every restatement is exactly equal to or within the
    caller-stated ``tolerance`` of its first statement (same stated unit; REQUIRED —
    never defaulted); FAILS naming each contradicting label with the first statement
    and every conflicting restatement verbatim, as ``"<label>.stated_first"`` and
    ``"<label>.restatement[<index>]"`` entries of ``computed``; refuses as
    UNEVALUABLE — never coercing — on an unusable tolerance, an empty mapping, a
    non-string label, an empty statement sequence for a label, any statement that is
    not the required resolved type, mixed units within a label, or mixed units across
    labels (the single stated tolerance is in one stated unit, so one shared stated
    unit is required everywhere it is applied).
    """
    tolerance_reason = _tolerance_reason(tolerance)
    if tolerance_reason is not None:
        return CheckUnevaluable(
            check_name=_CONTRADICTORY_DIMENSIONS, reason=tolerance_reason
        )
    if len(statements) == 0:
        return CheckUnevaluable(
            check_name=_CONTRADICTORY_DIMENSIONS,
            reason=(
                "contradictory_dimensions needs at least one dimension label, got an "
                "empty mapping — an empty submission is never reported as consistent"
            ),
        )
    for label, entries in statements.items():
        if not isinstance(label, str):
            return CheckUnevaluable(
                check_name=_CONTRADICTORY_DIMENSIONS,
                reason=(
                    "dimension labels must be strings, got "
                    f"{type(label).__name__} — labels are provenance and are never "
                    "coerced"
                ),
            )
        if len(entries) == 0:
            return CheckUnevaluable(
                check_name=_CONTRADICTORY_DIMENSIONS,
                reason=(
                    f"statements[{label!r}] is empty; a label with no stated values "
                    "has nothing to compare and is never reported as consistent"
                ),
            )
        entries_reason = _distances_reason(entries, f"statements[{label!r}]")
        if entries_reason is not None:
            return CheckUnevaluable(
                check_name=_CONTRADICTORY_DIMENSIONS, reason=entries_reason
            )
    units = {entries[0].unit for entries in statements.values()}
    if len(units) > 1:
        stated_units = ", ".join(sorted(repr(unit) for unit in units))
        return CheckUnevaluable(
            check_name=_CONTRADICTORY_DIMENSIONS,
            reason=(
                f"labels state mixed units ({stated_units}); the single stated "
                "tolerance is in one stated unit, so one shared stated unit across "
                "all labels is required and a stated value is never converted"
            ),
        )
    statement_count = sum(len(entries) for entries in statements.values())
    contradicting_label_count = 0
    contradiction_entries: dict[str, int | float] = {}
    for label, entries in statements.items():
        first = entries[0].value
        conflicts = [
            (index, entry.value)
            for index, entry in enumerate(entries)
            if abs(entry.value - first) > tolerance
        ]
        if conflicts:
            contradicting_label_count += 1
            contradiction_entries[f"{label}.stated_first"] = first
            for index, value in conflicts:
                contradiction_entries[f"{label}.restatement[{index}]"] = value
    computed: dict[str, int | float] = {
        "label_count": len(statements),
        "statement_count": statement_count,
        "contradicting_label_count": contradicting_label_count,
    }
    computed.update(contradiction_entries)
    result_type = CheckPassed if contradicting_label_count == 0 else CheckFailed
    return result_type(
        check_name=_CONTRADICTORY_DIMENSIONS,
        unit=next(iter(units)).value,
        tolerance=tolerance,
        computed=computed,
    )
