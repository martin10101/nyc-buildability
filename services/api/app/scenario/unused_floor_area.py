"""Deterministic derivation of the C1 unused-draft-zoning-floor-area section (M5-T017, D-041).

Gap-list item C1: the honest "unused DRAFT floor area" line for the first screen. This
module owns ALL of the C1 logic (the ``derive.py`` separate-module precedent); the scenario
``builder.py`` only wires the returned section into every document via a thin call in
``_assemble``.

The section is a pure, deterministic function of the ``property_profile`` (its
``existing_building_facts.bldgarea`` AND ``.numbldgs`` facts + root ``provenance[]`` array)
and the two draft-cap fields the builder already computed
(``draft_zoning_floor_area_cap_sq_ft`` + ``cap_provenance``). It performs NO independent legal
calculation: it consumes the canonical cap VERBATIM (never recomputed, never adjusted) and
subtracts the existing built floor area.

Hard guarantees (also enforced by ``tests/scenario/test_unused_floor_area.py``):

* States are typed (:class:`UnusedFloorAreaState`): ``computed`` (cap and a usable existing
  area present; value = cap - existing built area, an UNROUNDED float in square_feet; an
  exact zero is ``computed``, NOT over-built - ONLY when numbldgs establishes vacancy, see
  below), ``over_built`` (value strictly NEGATIVE, preserved EXACTLY - never
  clamped/nulled/abs'd - with an honest statement, a section-level professional-review flag,
  AND the document root professional_review_required forced true), and ``not_computable``
  with a typed reason (:class:`UnusedFloorAreaNotComputableReason`):
  ``missing_existing_building_area`` / ``existing_building_area_unusable`` (the fact's
  coverage_status is echoed verbatim) / ``no_draft_far_cap``. A not_computable value is
  ``null`` and NEVER estimated.
* D-059-R002/R011 (official PLUTO data dictionary): a recorded ``bldgarea`` of exactly 0 is
  NOT automatically a usable zero (a vacant lot). It is consumed as a usable zero ONLY when
  the SAME profile's ``numbldgs`` fact establishes vacancy (present, usable coverage_status,
  value exactly 0). When ``numbldgs`` is absent, unusable, or positive, a zero ``bldgarea``
  routes to ``existing_building_area_unusable`` (never guessed as vacant), with
  ``professional_review_required`` true at the section level (a recorded zero alongside a
  positive/uncertain building count is a data discrepancy, not a silent skip) and the original
  zero + the numbldgs basis carried as machine-readable ``assumptions`` records (the closed
  ``inputs`` shape has no numbldgs field).
* Precise-noun labeling (research 3.1): the label states what the engine computed
  (FAR-derived floor-area difference); it never says "maximum buildable area", "remaining
  development rights", or "remaining capacity". A scope note records that building geometry
  has NOT been assessed. No "verified"/"compliant" language is introduced.
* Machine-readable ZR 12-10 assumption (tax lot treated as the zoning lot) is carried as a
  document field on any computed/over_built section.
* Per-input provenance (research 3.2 "Calculated" row): the formula plus each input with its
  provenance - the cap provenance echoed verbatim, the existing-area provenance resolved from
  the fact's ``provenance_ref`` against the profile root ``provenance[]`` array.
* JSON-safe on every state: the value is always a finite float or ``null``, so both
  ``json.dumps(x, allow_nan=False)`` and ``.encode("utf-8")`` succeed.
* Determinism: identical input -> byte-identical output (fixed key order; no runtime
  randomness). The profile is consumed READ-ONLY.
"""

from __future__ import annotations

import math
from typing import Any

from . import constants as C
from .models import UnusedFloorAreaNotComputableReason as Reason
from .models import UnusedFloorAreaState as State

__all__ = ["build_unused_floor_area_section"]


# ---------------------------------------------------------------------------
# Numeric / shape guards (fail-closed), mirroring builder.py.
# ---------------------------------------------------------------------------


def _finite_float(value: Any) -> float | None:
    """``value`` as a finite float, else ``None`` (bool / non-numeric / NaN / +-inf /
    int too large for a finite float). Never raises."""
    if isinstance(value, bool):
        return None
    if not isinstance(value, int | float):
        return None
    try:
        as_float = float(value)
    except (OverflowError, ValueError):
        return None
    if not math.isfinite(as_float):
        return None
    return as_float


def _positive_finite_float(value: Any) -> float | None:
    """Finite float strictly greater than zero, else ``None``."""
    result = _finite_float(value)
    if result is None or result <= 0.0:
        return None
    return result


def _nonnegative_finite_float(value: Any) -> float | None:
    """Finite float greater than or equal to zero, else ``None`` (an existing built
    floor area of exactly 0 is a usable value - e.g. a vacant lot)."""
    result = _finite_float(value)
    if result is None or result < 0.0:
        return None
    return result


def _as_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


# ---------------------------------------------------------------------------
# Provenance resolution (reuses the profile-provenance-index pattern from
# builder._profile_provenance_index / _lot_area_provenance; kept local so this
# module stays self-contained and creates no import cycle with builder.py).
# ---------------------------------------------------------------------------


def _profile_provenance_index(property_profile: dict) -> dict[str, dict]:
    """Map provenance_id -> provenance record from the profile (read-only)."""
    index: dict[str, dict] = {}
    for record in _as_dict(property_profile).get("provenance", []) or []:
        if isinstance(record, dict) and isinstance(record.get("provenance_id"), str):
            index[record["provenance_id"]] = record
    return index


def _resolve_provenance(property_profile: dict, provenance_ref: Any) -> dict | None:
    """Resolve a fact ``provenance_ref`` against the profile root ``provenance[]``
    array into a source-naming record (same field subset as
    builder._lot_area_provenance.resolved), or ``None`` when it does not resolve."""
    if not isinstance(provenance_ref, str):
        return None
    record = _profile_provenance_index(property_profile).get(provenance_ref)
    if record is None:
        return None
    return {
        "provenance_id": record.get("provenance_id"),
        "source_id": record.get("source_id"),
        "dataset_version": record.get("dataset_version"),
        "original_field_name": record.get("original_field_name"),
        "effective_date": record.get("effective_date"),
    }


def _bldgarea_fact(property_profile: dict) -> dict | None:
    """The existing-building bldgarea fact_value ({value, provenance_ref,
    coverage_status, units}), or ``None`` when absent."""
    facts = _as_dict(_as_dict(property_profile).get("existing_building_facts"))
    fact = facts.get("bldgarea")
    return fact if isinstance(fact, dict) else None


def _numbldgs_fact(property_profile: dict) -> dict | None:
    """The existing-building numbldgs fact_value ({value, provenance_ref,
    coverage_status, units}), or ``None`` when absent (same profile.
    existing_building_facts sibling as bldgarea - app.profile.builder's
    BUILDING_FACT_COLUMNS)."""
    facts = _as_dict(_as_dict(property_profile).get("existing_building_facts"))
    fact = facts.get("numbldgs")
    return fact if isinstance(fact, dict) else None


def _vacancy_basis(property_profile: dict) -> tuple[bool, Any, Any]:
    """D-059-R002/R011: whether a recorded bldgarea of 0 is an established
    vacancy per the official PLUTO data dictionary rule (a zero building-area
    value with a POSITIVE building count means the area is UNAVAILABLE, not a
    real zero - never guessed). Vacancy is established ONLY when the profile's
    numbldgs fact is present, has a usable coverage_status, AND its value is a
    usable finite non-negative number equal to exactly 0 - numbldgs absent,
    unusable-coverage, non-numeric, or positive all fail closed (NOT
    established).

    Returns ``(vacancy_established, raw_numbldgs_value, usable_numbldgs_value)``
    - the raw value is echoed for traceability even when it does not establish
    vacancy (e.g. a positive count); the usable value is ``None`` whenever the
    fact could not be read as a finite non-negative number."""
    fact = _numbldgs_fact(property_profile)
    if fact is None:
        return False, None, None
    raw_value = fact.get("value")
    coverage = fact.get("coverage_status")
    usable_coverage = (
        isinstance(coverage, str) and coverage in C.USABLE_EXISTING_AREA_COVERAGE_STATUSES
    )
    usable_value = _nonnegative_finite_float(raw_value) if usable_coverage else None
    established = usable_value is not None and usable_value == 0.0
    return established, raw_value, usable_value


def _zero_with_buildings_assumptions(
    *, raw_bldgarea_value: Any, raw_numbldgs_value: Any, usable_numbldgs_value: float | None
) -> list[dict]:
    """D-059-R002: the machine-readable basis for the zero-with-buildings
    fail-closed outcome - the ORIGINAL recorded zero plus the numbldgs basis
    that failed to establish vacancy, both kept traceable (the closed
    unused_floor_area_inputs contract shape has no room for a third field, so
    this rides in ``assumptions``, the documented generic channel for
    machine-readable calculation basis records)."""
    if isinstance(raw_numbldgs_value, bool) or not isinstance(
        raw_numbldgs_value, int | float | str
    ):
        numbldgs_basis_clause = "numbldgs was not present in the property profile"
        numbldgs_assumption_value: Any = None
        numbldgs_unit = None
    elif usable_numbldgs_value is not None:
        numbldgs_basis_clause = (
            f"numbldgs was recorded as {usable_numbldgs_value:g}, a positive "
            "building count (not zero)"
        )
        numbldgs_assumption_value = usable_numbldgs_value
        numbldgs_unit = "buildings"
    else:
        numbldgs_basis_clause = (
            f"numbldgs was recorded as {raw_numbldgs_value!r} but is not usable "
            "(coverage_status or value)"
        )
        numbldgs_assumption_value = raw_numbldgs_value
        numbldgs_unit = None
    return [
        {
            "key": "existing_building_area_recorded_zero",
            "assumption_type": "not_computable_basis",
            "value": raw_bldgarea_value,
            "unit": "square_feet",
            "rationale": (
                "PLUTO recorded the existing-building bldgarea fact as exactly "
                "0; the recorded zero is preserved here even though it was NOT "
                "consumed as a usable existing area (see "
                "existing_building_area_unusable)."
            ),
        },
        {
            "key": "existing_building_area_numbldgs_basis",
            "assumption_type": "not_computable_basis",
            "value": numbldgs_assumption_value,
            "unit": numbldgs_unit,
            "rationale": (
                "Official PLUTO data dictionary (D-059-R011): a recorded "
                "bldgarea of 0 with a positive building count means the "
                "existing building area is UNAVAILABLE, not a real zero; "
                "vacancy is established only when numbldgs is present, usable, "
                f"and exactly 0. Here, {numbldgs_basis_clause}, so vacancy is "
                "NOT established and this fails closed rather than guessing."
            ),
        },
    ]


# ---------------------------------------------------------------------------
# Section assembly
# ---------------------------------------------------------------------------


def _inputs(
    *,
    cap_value: float | None,
    cap_provenance: dict | None,
    existing_value: float | None,
    existing_unit: Any,
    existing_coverage_status: Any,
    existing_provenance_ref: Any,
    existing_provenance: dict | None,
) -> dict:
    """The per-input provenance block (research 3.2 "Calculated" row). Present on
    every state so a consumer can always see what was, and was not, available."""
    return {
        "draft_zoning_floor_area_cap": {
            "value_sq_ft": cap_value,
            "unit": "square_feet" if cap_value is not None else None,
            "provenance": cap_provenance if isinstance(cap_provenance, dict) else None,
        },
        "existing_building_floor_area": {
            "value_sq_ft": existing_value,
            "unit": existing_unit if isinstance(existing_unit, str) else None,
            "coverage_status": (
                existing_coverage_status
                if isinstance(existing_coverage_status, str)
                else None
            ),
            "provenance_ref": (
                existing_provenance_ref
                if isinstance(existing_provenance_ref, str)
                else None
            ),
            "provenance": existing_provenance,
        },
    }


def _section(
    *,
    state: State,
    value: float | None,
    professional_review_required: bool,
    over_built_statement: str | None,
    not_computable_reason: Reason | None,
    formula: str | None,
    assumptions: list[dict],
    inputs: dict,
) -> dict:
    """Assemble the section in a fixed key order (determinism)."""
    return {
        "state": state.value,
        "unused_draft_zoning_floor_area_sq_ft": value,
        "unit": "square_feet" if value is not None else None,
        "label": C.UNUSED_FLOOR_AREA_LABEL,
        "scope_note": C.UNUSED_FLOOR_AREA_SCOPE_NOTE,
        "formula": formula,
        "professional_review_required": professional_review_required,
        "over_built_statement": over_built_statement,
        "not_computable_reason": (
            not_computable_reason.value if not_computable_reason is not None else None
        ),
        "inputs": inputs,
        "assumptions": assumptions,
    }


def build_unused_floor_area_section(
    *,
    property_profile: dict,
    cap_value: float | None,
    cap_provenance: dict | None,
) -> dict:
    """Derive the ``unused_draft_zoning_floor_area`` section deterministically.

    ``property_profile`` is consumed READ-ONLY. ``cap_value`` is the canonical draft
    residential zoning-floor-area cap the builder already surfaced (``None`` on every
    no-scenario / unsupported / fail-closed outcome); it is consumed VERBATIM, never
    recomputed or adjusted. ``cap_provenance`` is the builder's cap provenance dict
    (echoed verbatim), or ``None``.

    Returns the section dict. Its ``professional_review_required`` is the SECTION-level
    flag; the builder ORs it into the document root flag so an over-built remainder
    forces root professional_review_required true.
    """
    property_profile = _as_dict(property_profile)

    # Read the existing-building bldgarea fact once.
    fact = _bldgarea_fact(property_profile)
    fact_value = fact.get("value") if fact is not None else None
    fact_units = fact.get("units") if fact is not None else None
    fact_coverage = fact.get("coverage_status") if fact is not None else None
    fact_ref = fact.get("provenance_ref") if fact is not None else None
    resolved_prov = (
        _resolve_provenance(property_profile, fact_ref) if fact is not None else None
    )

    cap = _positive_finite_float(cap_value)

    # ------------------------------------------------------------------
    # No positive draft cap surfaced -> not_computable (no_draft_far_cap).
    # No subtraction is attempted and no number is invented. The existing-area
    # input is still recorded for transparency.
    # ------------------------------------------------------------------
    if cap is None:
        return _section(
            state=State.NOT_COMPUTABLE,
            value=None,
            professional_review_required=False,
            over_built_statement=None,
            not_computable_reason=Reason.NO_DRAFT_FAR_CAP,
            formula=None,
            assumptions=[],
            inputs=_inputs(
                cap_value=None,
                cap_provenance=None,
                existing_value=None,
                existing_unit=fact_units,
                existing_coverage_status=fact_coverage,
                existing_provenance_ref=fact_ref,
                existing_provenance=resolved_prov,
            ),
        )

    # ------------------------------------------------------------------
    # Cap present. Now the existing-built-area fact must be present and usable.
    # ------------------------------------------------------------------
    inputs_missing = _inputs(
        cap_value=cap,
        cap_provenance=cap_provenance,
        existing_value=None,
        existing_unit=fact_units,
        existing_coverage_status=fact_coverage,
        existing_provenance_ref=fact_ref,
        existing_provenance=resolved_prov,
    )

    # (a) No fact, or the fact value is null -> missing_existing_building_area.
    if fact is None or fact_value is None:
        return _section(
            state=State.NOT_COMPUTABLE,
            value=None,
            professional_review_required=False,
            over_built_statement=None,
            not_computable_reason=Reason.MISSING_EXISTING_BUILDING_AREA,
            formula=None,
            assumptions=[],
            inputs=inputs_missing,
        )

    # (b) Fact present but its coverage_status is not usable -> unusable
    # (coverage_status echoed verbatim via inputs_missing).
    usable_coverage = (
        isinstance(fact_coverage, str)
        and fact_coverage in C.USABLE_EXISTING_AREA_COVERAGE_STATUSES
    )
    existing_area = _nonnegative_finite_float(fact_value)
    if not usable_coverage or existing_area is None:
        return _section(
            state=State.NOT_COMPUTABLE,
            value=None,
            professional_review_required=False,
            over_built_statement=None,
            not_computable_reason=Reason.EXISTING_BUILDING_AREA_UNUSABLE,
            formula=None,
            assumptions=[],
            inputs=inputs_missing,
        )

    # (b2) D-059-R002/R011: a recorded bldgarea of exactly 0 is USABLE only when
    # this SAME profile establishes vacancy via numbldgs (present, usable
    # coverage_status, and == 0). The official PLUTO data dictionary states a
    # zero building-area value with a positive building count means the area is
    # UNAVAILABLE, not a real zero; when numbldgs is absent, unusable, or
    # positive, vacancy is NOT established and this fails closed to the SAME
    # typed reason as case (b) - never guessed as a vacant lot. Routes to
    # professional review (unlike case (a)/(b): a recorded zero alongside
    # buildings is a data discrepancy that needs a qualified human, not a
    # silent skip). The original zero and the numbldgs basis stay traceable in
    # assumptions (the closed inputs shape has no third field for numbldgs).
    if existing_area == 0.0:
        vacancy_established, raw_numbldgs_value, usable_numbldgs_value = _vacancy_basis(
            property_profile
        )
        if not vacancy_established:
            return _section(
                state=State.NOT_COMPUTABLE,
                value=None,
                professional_review_required=True,
                over_built_statement=None,
                not_computable_reason=Reason.EXISTING_BUILDING_AREA_UNUSABLE,
                formula=None,
                assumptions=_zero_with_buildings_assumptions(
                    raw_bldgarea_value=fact_value,
                    raw_numbldgs_value=raw_numbldgs_value,
                    usable_numbldgs_value=usable_numbldgs_value,
                ),
                inputs=inputs_missing,
            )

    # ------------------------------------------------------------------
    # COMPUTED / OVER_BUILT: cap - existing built area, UNROUNDED. The cap is
    # consumed verbatim; the difference is never clamped/abs'd/nulled.
    # ------------------------------------------------------------------
    value = cap - existing_area
    inputs = _inputs(
        cap_value=cap,
        cap_provenance=cap_provenance,
        existing_value=existing_area,
        existing_unit=fact_units,
        existing_coverage_status=fact_coverage,
        existing_provenance_ref=fact_ref,
        existing_provenance=resolved_prov,
    )
    assumptions = [C.zoning_lot_extent_assumption()]

    if value < 0.0:
        return _section(
            state=State.OVER_BUILT,
            value=value,
            professional_review_required=True,
            over_built_statement=C.UNUSED_FLOOR_AREA_OVER_BUILT_STATEMENT,
            not_computable_reason=None,
            formula=C.UNUSED_FLOOR_AREA_FORMULA,
            assumptions=assumptions,
            inputs=inputs,
        )

    # value >= 0.0 (an exact zero is a computed, honest zero remainder).
    return _section(
        state=State.COMPUTED,
        value=value,
        professional_review_required=False,
        over_built_statement=None,
        not_computable_reason=None,
        formula=C.UNUSED_FLOOR_AREA_FORMULA,
        assumptions=assumptions,
        inputs=inputs,
    )
