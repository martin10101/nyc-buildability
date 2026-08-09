"""Deterministic document-metadata consistency checks over already-validated survey
facts (M2-T015 SB-S3, part 3 — final checks part).

The final four checks of the survey-ingestion packet's DETERMINISTIC CHECKS clause:

- :func:`scale_consistency` — every scale statement across a document states the
  identical canonical ``1:N`` ratio.
- :func:`north_orientation_consistency` — every north-arrow orientation statement
  agrees within a stated angular tolerance, compared ON THE CIRCLE.
- :func:`elevation_consistency` — per-point-label elevation restatements agree within
  a stated tolerance; different labels are NEVER compared against each other.
- :func:`address_bbl_match` — the document's address/BBL text facts exactly equal the
  stated subject-property targets. Fuzzy or normalized address matching is a
  deliberate NON-goal of this module: any difference at all is a visible FAIL that
  routes to review.

Same ground rules as :mod:`app.documents.checks.boundary` and
:mod:`app.documents.checks.area`, whose tolerance refusal helper this module
deliberately reuses so the tolerance discipline stays single-sourced: checks consume
ONLY the resolved typed results of :mod:`app.documents.units` — never raw wire values,
never AI output — return the frozen typed results of :mod:`app.documents.checks`,
never raise for a check-domain outcome, and never default, convert, wrap, or guess a
stated value, unit, or tolerance.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from app.documents.checks import (
    CheckFailed,
    CheckPassed,
    CheckResult,
    CheckUnevaluable,
)
from app.documents.checks.boundary import _tolerance_reason
from app.documents.taxonomy import SurveyFactType
from app.documents.units import (
    AngleUnit,
    ElevationUnit,
    ValidatedBearing,
    ValidatedElevation,
    ValidatedScale,
    ValidatedUnitlessText,
)

__all__ = [
    "address_bbl_match",
    "elevation_consistency",
    "north_orientation_consistency",
    "scale_consistency",
]

_SCALE_CONSISTENCY = "scale_consistency"
_NORTH_ORIENTATION_CONSISTENCY = "north_orientation_consistency"
_ELEVATION_CONSISTENCY = "elevation_consistency"
_ADDRESS_BBL_MATCH = "address_bbl_match"


# ---------------------------------------------------------------------- helpers


def _scales_reason(scales: Sequence[object]) -> str | None:
    """The refusal reason for an unusable scale sequence, or ``None`` when usable.

    Usable means every element is the resolved :class:`ValidatedScale` type carrying
    the canonical dimensionless ``1:N`` ratio.
    """
    for index, candidate in enumerate(scales):
        if not isinstance(candidate, ValidatedScale):
            return (
                f"scales[{index}] must be a resolved ValidatedScale, got "
                f"{type(candidate).__name__} — raw wire values, unresolved results, "
                "and AI output are never consumed or coerced here"
            )
    return None


def _orientations_reason(orientations: Sequence[object]) -> str | None:
    """The refusal reason for an unusable orientation sequence, or ``None`` when usable.

    Usable means every element is the resolved :class:`ValidatedBearing` type stated in
    canonical decimal degrees — the only angle unit the circular comparison is grounded
    for; any other stated angle unit refuses closed and is never converted.
    """
    for index, candidate in enumerate(orientations):
        if not isinstance(candidate, ValidatedBearing):
            return (
                f"orientations[{index}] must be a resolved ValidatedBearing, got "
                f"{type(candidate).__name__} — raw wire values, unresolved results, "
                "and AI output are never consumed or coerced here"
            )
        if candidate.unit is not AngleUnit.DEGREES:
            return (
                "the circular comparison is grounded only for orientations stated in "
                f"'degrees'; orientations[{index}] states {candidate.unit!r} and is "
                "never converted"
            )
    return None


def _elevations_reason(entries: Sequence[object], name: str) -> str | None:
    """The refusal reason for an unusable elevation sequence, or ``None`` when usable.

    Usable means every element is the resolved :class:`ValidatedElevation` type and
    every element states the same elevation unit — a stated value is never converted.
    """
    first_unit: ElevationUnit | None = None
    for index, candidate in enumerate(entries):
        if not isinstance(candidate, ValidatedElevation):
            return (
                f"{name}[{index}] must be a resolved ValidatedElevation, got "
                f"{type(candidate).__name__} — raw wire values, unresolved results, "
                "and AI output are never consumed or coerced here"
            )
        if first_unit is None:
            first_unit = candidate.unit
        elif candidate.unit is not first_unit:
            return (
                f"{name} states mixed units ({first_unit!r} and {candidate.unit!r}); "
                "a stated value is never converted between units"
            )
    return None


def _angular_difference(a: int | float, b: int | float) -> float:
    """Angular difference between two orientations in degrees, ON THE CIRCLE.

    Both inputs are canonical decimal degrees in [0.0, 360.0); the difference is the
    shorter way around the circle, so 359.9 and 0.1 differ by 0.2, never 359.8.
    """
    raw = abs(float(a) - float(b))
    return min(raw, 360.0 - raw)


# ----------------------------------------------------------------------- checks


def scale_consistency(scales: Sequence[ValidatedScale]) -> CheckResult:
    """Deterministic document-wide scale-statement consistency check.

    Given every resolved ``ValidatedScale`` statement extracted across one document,
    PASSES iff all statements state the identical canonical ``1:N`` ratio. A drawing
    scale is a single document-level fact, so identity is the requirement: the check
    deliberately takes no tolerance parameter, and the recorded tolerance is the
    literal 0 of exact equality (``unit`` is ``None`` — the ratio is dimensionless).
    FAILS when more than one distinct ratio is stated, naming EVERY stated ratio
    verbatim as a ``"ratio[<ratio>]"`` occurrence-count entry of ``computed``; refuses
    as UNEVALUABLE — never coercing — on an empty sequence or any element that is not
    the required resolved type.
    """
    if len(scales) == 0:
        return CheckUnevaluable(
            check_name=_SCALE_CONSISTENCY,
            reason=(
                "scale_consistency needs at least one resolved scale statement, got "
                "an empty sequence — an empty submission is never reported as "
                "consistent"
            ),
        )
    scales_reason = _scales_reason(scales)
    if scales_reason is not None:
        return CheckUnevaluable(check_name=_SCALE_CONSISTENCY, reason=scales_reason)
    ratio_counts: dict[str, int] = {}
    for scale in scales:
        ratio_counts[scale.ratio] = ratio_counts.get(scale.ratio, 0) + 1
    computed: dict[str, int | float] = {
        "statement_count": len(scales),
        "distinct_ratio_count": len(ratio_counts),
    }
    for ratio, count in ratio_counts.items():
        computed[f"ratio[{ratio}]"] = count
    result_type = CheckPassed if len(ratio_counts) == 1 else CheckFailed
    return result_type(
        check_name=_SCALE_CONSISTENCY,
        unit=None,
        tolerance=0,
        computed=computed,
    )


def north_orientation_consistency(
    orientations: Sequence[ValidatedBearing],
    *,
    tolerance: int | float,
) -> CheckResult:
    """Deterministic north-arrow orientation consistency check, ON THE CIRCLE.

    Given every resolved ``ValidatedBearing`` north-arrow orientation statement
    extracted across one document (canonical decimal degrees in [0.0, 360.0)),
    compares every statement against the FIRST statement using the circular angular
    difference ``min(abs(a - b), 360 - abs(a - b))`` — the shorter way around the
    circle, so 359.9 and 0.1 differ by 0.2, never 359.8. PASSES iff every statement is
    within the caller-stated ``tolerance`` (degrees; REQUIRED — never defaulted) of
    the first, recording the first statement and the maximum angular difference
    verbatim; FAILS naming each conflicting statement verbatim as
    ``"statement[<index>]"`` and ``"statement[<index>].angular_difference"`` entries
    of ``computed``; refuses as UNEVALUABLE — never coercing — on an unusable
    tolerance, an empty sequence, or any element that is not the required resolved
    type stated in degrees.
    """
    tolerance_reason = _tolerance_reason(tolerance)
    if tolerance_reason is not None:
        return CheckUnevaluable(
            check_name=_NORTH_ORIENTATION_CONSISTENCY, reason=tolerance_reason
        )
    if len(orientations) == 0:
        return CheckUnevaluable(
            check_name=_NORTH_ORIENTATION_CONSISTENCY,
            reason=(
                "north_orientation_consistency needs at least one resolved "
                "orientation statement, got an empty sequence — an empty submission "
                "is never reported as consistent"
            ),
        )
    orientations_reason = _orientations_reason(orientations)
    if orientations_reason is not None:
        return CheckUnevaluable(
            check_name=_NORTH_ORIENTATION_CONSISTENCY, reason=orientations_reason
        )
    first = orientations[0].value
    max_angular_difference = 0.0
    conflicts: list[tuple[int, int | float, float]] = []
    for index, statement in enumerate(orientations):
        difference = _angular_difference(first, statement.value)
        max_angular_difference = max(max_angular_difference, difference)
        if difference > tolerance:
            conflicts.append((index, statement.value, difference))
    computed: dict[str, int | float] = {
        "statement_count": len(orientations),
        "stated_first": first,
        "max_angular_difference": max_angular_difference,
    }
    for index, value, difference in conflicts:
        computed[f"statement[{index}]"] = value
        computed[f"statement[{index}].angular_difference"] = difference
    result_type = CheckPassed if not conflicts else CheckFailed
    return result_type(
        check_name=_NORTH_ORIENTATION_CONSISTENCY,
        unit=AngleUnit.DEGREES.value,
        tolerance=tolerance,
        computed=computed,
    )


def elevation_consistency(
    statements: Mapping[str, Sequence[ValidatedElevation]],
    *,
    tolerance: int | float,
) -> CheckResult:
    """Deterministic per-point elevation restatement consistency check.

    Given a mapping of point label → the resolved ``ValidatedElevation`` restatements
    of that ONE surveyed point (e.g. a benchmark restated on multiple sheets),
    compares every restatement within each label against the label's FIRST statement.
    Different labels are NEVER compared against each other: two distinct points
    legitimately hold different elevations, so a cross-label comparison would be
    meaningless. PASSES iff, within every label, every restatement is exactly equal to
    or within the caller-stated ``tolerance`` of its first statement (same stated
    unit; REQUIRED — never defaulted); FAILS naming each conflicting label with the
    first statement and every conflicting restatement verbatim, as
    ``"<label>.stated_first"`` and ``"<label>.restatement[<index>]"`` entries of
    ``computed``; refuses as UNEVALUABLE — never coercing — on an unusable tolerance,
    an empty mapping, a non-string label, an empty restatement sequence for a label,
    any restatement that is not the required resolved type, mixed units within a
    label, or mixed units across labels (the single stated tolerance is in one stated
    unit, so one shared stated unit is required everywhere it is applied).
    """
    tolerance_reason = _tolerance_reason(tolerance)
    if tolerance_reason is not None:
        return CheckUnevaluable(
            check_name=_ELEVATION_CONSISTENCY, reason=tolerance_reason
        )
    if len(statements) == 0:
        return CheckUnevaluable(
            check_name=_ELEVATION_CONSISTENCY,
            reason=(
                "elevation_consistency needs at least one point label, got an empty "
                "mapping — an empty submission is never reported as consistent"
            ),
        )
    for label, entries in statements.items():
        if not isinstance(label, str):
            return CheckUnevaluable(
                check_name=_ELEVATION_CONSISTENCY,
                reason=(
                    "point labels must be strings, got "
                    f"{type(label).__name__} — labels are provenance and are never "
                    "coerced"
                ),
            )
        if len(entries) == 0:
            return CheckUnevaluable(
                check_name=_ELEVATION_CONSISTENCY,
                reason=(
                    f"statements[{label!r}] is empty; a label with no stated values "
                    "has nothing to compare and is never reported as consistent"
                ),
            )
        entries_reason = _elevations_reason(entries, f"statements[{label!r}]")
        if entries_reason is not None:
            return CheckUnevaluable(
                check_name=_ELEVATION_CONSISTENCY, reason=entries_reason
            )
    units = {entries[0].unit for entries in statements.values()}
    if len(units) > 1:
        stated_units = ", ".join(sorted(repr(unit) for unit in units))
        return CheckUnevaluable(
            check_name=_ELEVATION_CONSISTENCY,
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
        check_name=_ELEVATION_CONSISTENCY,
        unit=next(iter(units)).value,
        tolerance=tolerance,
        computed=computed,
    )


def address_bbl_match(
    address_fact: ValidatedUnitlessText | None,
    bbl_fact: ValidatedUnitlessText | None,
    *,
    subject_address: str,
    subject_bbl: str,
) -> CheckResult:
    """Deterministic exact-equality match of document identifiers to the subject property.

    Given the document's resolved ``ValidatedUnitlessText`` address fact and/or BBL
    fact (``None`` when the document states none), plus the STATED subject-property
    address string and BBL string the analysis targets, PASSES iff EVERY present fact
    exactly equals its stated counterpart: the BBL comparison is exact 10-digit string
    equality (the resolved fact is already the canonical 10-digit form), and the
    address comparison is exact string equality after NO transformation whatsoever —
    no trimming, case-folding, abbreviation expansion, punctuation stripping, or
    normalization of any kind. Fuzzy or normalized address matching is a deliberate
    NON-goal of this check: address text is provenance, and any difference at all —
    even ``"St"`` for ``"Street"`` — is a visible FAIL that routes to review, never a
    silent match. FAILS carrying both compared strings verbatim, as
    ``"<role>.document_fact[<text>]"`` and ``"<role>.subject_target[<text>]"`` entries
    of ``computed`` whose value is the 1/0 match flag of that role; refuses as
    UNEVALUABLE — never coercing — when NO address or BBL fact is present at all, when
    either stated subject target is missing or blank, when a present fact is not the
    required resolved type, or when a present fact carries the wrong ``fact_type`` for
    its role (facts are never re-labeled to fit a comparison).
    """
    if address_fact is None and bbl_fact is None:
        return CheckUnevaluable(
            check_name=_ADDRESS_BBL_MATCH,
            reason=(
                "address_bbl_match needs at least one resolved address or BBL text "
                "fact, got neither — a document stating no identifier is never "
                "reported as matching the subject property"
            ),
        )
    for target_name, target in (
        ("subject_address", subject_address),
        ("subject_bbl", subject_bbl),
    ):
        if not isinstance(target, str) or not target.strip():
            return CheckUnevaluable(
                check_name=_ADDRESS_BBL_MATCH,
                reason=(
                    f"the stated {target_name} target is missing or blank "
                    f"({target!r}); a match against an unstated target is never "
                    "assumed"
                ),
            )
    for role, fact, expected_fact_type in (
        ("address", address_fact, SurveyFactType.ADDRESS_TEXT),
        ("bbl", bbl_fact, SurveyFactType.BBL_TEXT),
    ):
        if fact is None:
            continue
        if not isinstance(fact, ValidatedUnitlessText):
            return CheckUnevaluable(
                check_name=_ADDRESS_BBL_MATCH,
                reason=(
                    f"the {role} fact must be a resolved ValidatedUnitlessText, got "
                    f"{type(fact).__name__} — raw wire values, unresolved results, "
                    "and AI output are never consumed or coerced here"
                ),
            )
        if fact.fact_type is not expected_fact_type:
            return CheckUnevaluable(
                check_name=_ADDRESS_BBL_MATCH,
                reason=(
                    f"the {role} fact must carry fact_type "
                    f"{expected_fact_type.value!r}, got {fact.fact_type.value!r} — "
                    "facts are never re-labeled to fit a comparison"
                ),
            )
    compared_fact_count = 0
    mismatched_fact_count = 0
    match_entries: dict[str, int | float] = {}
    for role, fact, target in (
        ("address", address_fact, subject_address),
        ("bbl", bbl_fact, subject_bbl),
    ):
        if fact is None:
            continue
        compared_fact_count += 1
        matched = 1 if fact.text == target else 0
        if matched == 0:
            mismatched_fact_count += 1
        match_entries[f"{role}.document_fact[{fact.text}]"] = matched
        match_entries[f"{role}.subject_target[{target}]"] = matched
    computed: dict[str, int | float] = {
        "compared_fact_count": compared_fact_count,
        "mismatched_fact_count": mismatched_fact_count,
    }
    computed.update(match_entries)
    result_type = CheckPassed if mismatched_fact_count == 0 else CheckFailed
    return result_type(
        check_name=_ADDRESS_BBL_MATCH,
        unit=None,
        tolerance=0,
        computed=computed,
    )
