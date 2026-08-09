"""Tax-lot (MapPLUTO) reference cross-checks over already-validated survey facts
(M2-T015 SB-S4).

Compares resolved survey facts against the ACCEPTED tax-lot reference for the subject
property — carried here as the frozen read-only :class:`TaxLotReference`:

- :func:`tax_lot_bbl_crosscheck` — the survey's resolved BBL text fact against the
  reference BBL, exact 10-digit string equality.
- :func:`tax_lot_area_crosscheck` — the survey's resolved stated or calculated
  lot-area fact against the reference lot area within a caller-stated tolerance, in
  ``square_feet`` ONLY — never a unit conversion.

DOCTRINE — the reference is context, never authority. The licensed survey remains the
authoritative boundary evidence for the subject property; MapPLUTO/tax-lot geometry
serves ONLY as a cross-check and must NEVER silently override a licensed survey. A
cross-check DISCREPANCY is a visible typed FAIL that routes to professional review —
it never mutates, corrects, replaces, or suppresses any survey fact. That is enforced
structurally, not by convention: this module deliberately has NO code path that writes
survey state — it imports no state, storage, session, repository, or database
machinery (typed values in, frozen typed results out), the reference model is frozen
and consumed read-only, and every returned result type is non-promotable.

Same ground rules as :mod:`app.documents.checks`, whose frozen typed results
(:class:`CheckPassed` / :class:`CheckFailed` / :class:`CheckUnevaluable`) this module
returns: the survey side consumes ONLY the resolved typed results of
:mod:`app.documents.units` — never raw wire values, never AI output — no check-domain
outcome ever raises, and no stated value, unit, or tolerance is ever defaulted,
converted, wrapped, or guessed. A missing/malformed reference field, a non-resolved
survey input, a non-``square_feet`` survey area unit, or an unusable tolerance refuses
closed as UNEVALUABLE.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from app.documents.checks import (
    CheckFailed,
    CheckPassed,
    CheckResult,
    CheckUnevaluable,
)
from app.documents.models import BBL_PATTERN
from app.documents.taxonomy import SurveyFactType
from app.documents.units import AreaUnit, ValidatedArea, ValidatedUnitlessText

__all__ = ["TaxLotReference", "tax_lot_area_crosscheck", "tax_lot_bbl_crosscheck"]

_TAX_LOT_BBL_CROSSCHECK = "tax_lot_bbl_crosscheck"
_TAX_LOT_AREA_CROSSCHECK = "tax_lot_area_crosscheck"

#: The only survey fact types a lot-area cross-check is grounded for — the survey's
#: stated lot area and its calculated lot area. Extended additively only; any other
#: fact type refuses closed rather than being re-labeled to fit the comparison.
_LOT_AREA_FACT_TYPES = frozenset(
    {SurveyFactType.STATED_LOT_AREA, SurveyFactType.CALCULATED_LOT_AREA}
)


# ------------------------------------------------------------------ reference model


@dataclass(frozen=True)
class TaxLotReference:
    """Frozen READ-ONLY record of the accepted tax-lot reference for the subject
    property (MapPLUTO / tax-lot geometry lineage), consumed by the cross-checks as
    context only.

    Every field is REQUIRED and carried verbatim — never defaulted: ``bbl`` is the
    canonical 10-digit NYC BBL string; ``lot_area_square_feet`` is the reference lot
    area as a finite positive number of square feet; ``source_dataset``,
    ``source_version``, and ``retrieved_at`` are the verbatim provenance strings of
    the accepted reference record. The model performs no validation or coercion of its
    own — a malformed field makes every cross-check consuming the record refuse as
    UNEVALUABLE, never yield a corrected value. The record is never authoritative for
    the boundary: ``promotable`` and ``overrides_survey`` are class-level ``False`` by
    doctrine, and there is no code path here (or anywhere in this module) that writes
    survey state.
    """

    bbl: str
    lot_area_square_feet: int | float
    source_dataset: str
    source_version: str
    retrieved_at: str

    promotable = False
    overrides_survey = False


# ---------------------------------------------------------------------- helpers


def _tolerance_reason(tolerance: object) -> str | None:
    """The refusal reason for an unusable stated tolerance, or ``None`` when usable.

    Usable means a finite non-negative number (zero means exact) — REQUIRED and never
    defaulted; a boolean, string, non-finite, or negative tolerance is never coerced.
    """
    if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)):
        return (
            "the stated tolerance must be a number, got "
            f"{type(tolerance).__name__} — a tolerance is never parsed, defaulted, or "
            "coerced"
        )
    if not math.isfinite(tolerance):
        return f"the stated tolerance must be a finite number, got {tolerance!r}"
    if tolerance < 0:
        return (
            f"the stated tolerance must be non-negative (zero means exact), got "
            f"{tolerance!r}"
        )
    return None


def _reference_reason(reference: object) -> str | None:
    """The refusal reason for an unusable tax-lot reference, or ``None`` when usable.

    Usable means a :class:`TaxLotReference` whose every field is well-formed: the
    canonical 10-digit BBL string, a finite positive lot area, and non-blank
    provenance strings. A malformed field is never reformatted, inferred, or defaulted
    — the cross-check refuses instead, and the reference is never modified.
    """
    if not isinstance(reference, TaxLotReference):
        return (
            "the tax-lot reference must be a TaxLotReference, got "
            f"{type(reference).__name__} — raw wire values and unaccepted records are "
            "never consumed or coerced here"
        )
    if not isinstance(reference.bbl, str) or not BBL_PATTERN.fullmatch(reference.bbl):
        return (
            "TaxLotReference.bbl must be the canonical 10-digit NYC BBL string, got "
            f"{reference.bbl!r} — a malformed reference identifier is never "
            "reformatted or inferred"
        )
    area = reference.lot_area_square_feet
    if (
        isinstance(area, bool)
        or not isinstance(area, (int, float))
        or not math.isfinite(area)
        or area <= 0
    ):
        return (
            "TaxLotReference.lot_area_square_feet must be a finite positive number, "
            f"got {area!r} — a malformed reference area is never coerced"
        )
    for field_name in ("source_dataset", "source_version", "retrieved_at"):
        value = getattr(reference, field_name)
        if not isinstance(value, str) or not value.strip():
            return (
                f"TaxLotReference.{field_name} must be a non-blank provenance string, "
                f"got {value!r} — reference provenance is REQUIRED verbatim and never "
                "defaulted"
            )
    return None


# ----------------------------------------------------------------------- checks


def tax_lot_bbl_crosscheck(
    survey_bbl: ValidatedUnitlessText, reference: TaxLotReference
) -> CheckResult:
    """Deterministic exact-equality cross-check of the survey's BBL against the
    accepted tax-lot reference BBL.

    Given the survey's resolved ``ValidatedUnitlessText`` BBL fact and the frozen
    :class:`TaxLotReference`, PASSES iff the two 10-digit BBL strings are exactly
    equal — no trimming, reformatting, or normalization of any kind. FAILS carrying
    BOTH compared strings verbatim, as ``"bbl.survey_fact[<text>]"`` and
    ``"bbl.tax_lot_reference[<bbl>]"`` entries of ``computed`` whose value is the 1/0
    match flag (the same shape as
    :func:`app.documents.checks.metadata.address_bbl_match`). A FAIL is a visible
    discrepancy that routes to professional review and NEVER overrides, mutates,
    corrects, replaces, or suppresses the survey fact — the licensed survey remains
    the authoritative boundary evidence; the reference is context only. Refuses as
    UNEVALUABLE — never coercing — when the reference is missing or malformed (wrong
    type, malformed BBL, non-finite/non-positive lot area, or missing/blank
    provenance), when the survey input is not the required resolved type, or when it
    carries a ``fact_type`` other than the BBL text fact type (facts are never
    re-labeled to fit a comparison).
    """
    reference_reason = _reference_reason(reference)
    if reference_reason is not None:
        return CheckUnevaluable(
            check_name=_TAX_LOT_BBL_CROSSCHECK, reason=reference_reason
        )
    if not isinstance(survey_bbl, ValidatedUnitlessText):
        return CheckUnevaluable(
            check_name=_TAX_LOT_BBL_CROSSCHECK,
            reason=(
                "the survey BBL fact must be a resolved ValidatedUnitlessText, got "
                f"{type(survey_bbl).__name__} — raw wire values, unresolved results, "
                "and AI output are never consumed or coerced here"
            ),
        )
    if survey_bbl.fact_type is not SurveyFactType.BBL_TEXT:
        return CheckUnevaluable(
            check_name=_TAX_LOT_BBL_CROSSCHECK,
            reason=(
                "the survey BBL fact must carry fact_type "
                f"{SurveyFactType.BBL_TEXT.value!r}, got {survey_bbl.fact_type!r} — "
                "facts are never re-labeled to fit a comparison"
            ),
        )
    flag = 1 if survey_bbl.text == reference.bbl else 0
    computed = {
        "compared_fact_count": 1,
        "mismatched_fact_count": 1 - flag,
        f"bbl.survey_fact[{survey_bbl.text}]": flag,
        f"bbl.tax_lot_reference[{reference.bbl}]": flag,
    }
    result_type = CheckPassed if flag == 1 else CheckFailed
    return result_type(
        check_name=_TAX_LOT_BBL_CROSSCHECK,
        unit=None,
        tolerance=0,
        computed=computed,
    )


def tax_lot_area_crosscheck(
    survey_area: ValidatedArea,
    reference: TaxLotReference,
    *,
    tolerance: int | float,
) -> CheckResult:
    """Deterministic tolerance cross-check of the survey's lot area against the
    accepted tax-lot reference lot area.

    Given the survey's resolved stated or calculated ``ValidatedArea`` lot-area fact
    and the frozen :class:`TaxLotReference`, compares the two areas in ``square_feet``
    ONLY: the reference lot area is stated in square feet, and a stated survey value
    is never converted between units, so a survey area stated in ``acres`` (or any
    other unit) refuses as UNEVALUABLE instead. PASSES iff
    ``abs(survey_area - reference_area)`` is <= the caller-stated ``tolerance``
    (REQUIRED — finite, non-negative, in square feet, never defaulted), both areas and
    their difference recorded verbatim in ``computed``; FAILS carrying the same
    verbatim numbers otherwise — a visible discrepancy that routes to professional
    review and NEVER overrides, mutates, corrects, replaces, or suppresses the survey
    fact; the licensed survey remains the authoritative boundary evidence and the
    reference is context only. Refuses as UNEVALUABLE — never coercing — on an
    unusable tolerance, a missing or malformed reference (wrong type, malformed BBL,
    non-finite/non-positive lot area, or missing/blank provenance), a survey input
    that is not the required resolved type, a survey ``fact_type`` other than the
    stated/calculated lot-area fact types, or a survey area unit other than
    ``square_feet``.
    """
    tolerance_reason = _tolerance_reason(tolerance)
    if tolerance_reason is not None:
        return CheckUnevaluable(
            check_name=_TAX_LOT_AREA_CROSSCHECK, reason=tolerance_reason
        )
    reference_reason = _reference_reason(reference)
    if reference_reason is not None:
        return CheckUnevaluable(
            check_name=_TAX_LOT_AREA_CROSSCHECK, reason=reference_reason
        )
    if not isinstance(survey_area, ValidatedArea):
        return CheckUnevaluable(
            check_name=_TAX_LOT_AREA_CROSSCHECK,
            reason=(
                "the survey area must be a resolved ValidatedArea, got "
                f"{type(survey_area).__name__} — raw wire values, unresolved results, "
                "and AI output are never consumed or coerced here"
            ),
        )
    if survey_area.fact_type not in _LOT_AREA_FACT_TYPES:
        return CheckUnevaluable(
            check_name=_TAX_LOT_AREA_CROSSCHECK,
            reason=(
                "the survey area fact must carry fact_type "
                f"{SurveyFactType.STATED_LOT_AREA.value!r} or "
                f"{SurveyFactType.CALCULATED_LOT_AREA.value!r}, got "
                f"{survey_area.fact_type!r} — facts are never re-labeled to fit a "
                "comparison"
            ),
        )
    if survey_area.unit is not AreaUnit.SQUARE_FEET:
        return CheckUnevaluable(
            check_name=_TAX_LOT_AREA_CROSSCHECK,
            reason=(
                "the tax-lot reference lot area is stated in "
                f"{AreaUnit.SQUARE_FEET.value!r}, but the survey area is stated in "
                f"{survey_area.unit!r}; a stated value is never converted between "
                "units, so only a square-feet survey area is comparable"
            ),
        )
    difference = survey_area.value - reference.lot_area_square_feet
    computed = {
        "survey_area": survey_area.value,
        "tax_lot_reference_area": reference.lot_area_square_feet,
        "difference": difference,
    }
    result_type = CheckPassed if abs(difference) <= tolerance else CheckFailed
    return result_type(
        check_name=_TAX_LOT_AREA_CROSSCHECK,
        unit=AreaUnit.SQUARE_FEET.value,
        tolerance=tolerance,
        computed=computed,
    )
