"""Deterministic OFFLINE derivation of an ILLUSTRATIVE practical-usable-range (M5-T005).

First optimization-side brick under M5: fills the Compare UI's empty *practical usable
range* with an honest, explicit-assumption-only derived figure. Boundaries (also enforced
by ``tests/scenario/test_scenario_derive.py``):

* Contract-free: returns a NEW derived object; never edits builder/models/constants/
  contract or any canonical schema; consumes ``scenario`` READ-ONLY.
* The canonical cap is transported VERBATIM (original type/value) on every outcome and is
  never the derived range; a SEPARATE float view is used for arithmetic only, so the
  transported cap is never coerced and no silent int->float precision loss occurs.
* No hidden default: with no declared factor the endpoints are the cap verbatim
  (min==point==max==cap); no utilization/efficiency/optimization factor is ever silently
  applied. Only when a factor IS applied is the cap converted to float for the product.
* Underflow-safe: the cap is folded into the running product so a still-representable
  subnormal endpoint is not prematurely flushed to zero; a result that is genuinely
  unrepresentable (underflows to 0.0 even folded) is reported as a typed "not derivable",
  never a silently-successful zero.
* Fail closed on malformed/non-finite/negative/zero/out-of-domain/non-numeric factors, a
  malformed ``assumptions`` container (present but not a list), or a non-dict entry: a
  typed outcome with reasons, no crash, no NaN/negative/Inf, never a partial range, cap
  never mutated.
* Never Verified: ``coverage_status`` can never be ``verified`` on ANY outcome; an
  incoming ``verified`` (defended against, though a scenario must never carry it) is
  capped to ``conditional``.
* Determinism: identical input -> byte-identical output (endpoints, labels, reasons,
  provenance, and the factor list all emit in a fixed order).

The range is a POINT estimate (min==point==max) unless explicit low/high uncertainty is
declared; fabricating an uncertainty band would be a hidden assumption and is forbidden.
"""

from __future__ import annotations

import math
from typing import Any

from .constants import DRAFT_CAP_LABEL, NOT_VERIFIED_DISCLAIMER

__all__ = [
    "DERIVED_RANGE_LABEL",
    "RECOGNIZED_FACTOR_TYPES",
    "DerivedRangeKind",
    "derive_practical_usable_range",
]


# --- Typed vocabulary + honest labels (all CONSTANTS; nothing computed at runtime). ---


class DerivedRangeKind:
    """Typed outcome of a derivation (string values serialize straight into the object)."""

    #: Illustrative range derived from the canonical cap x declared factors.
    DERIVED = "derived_practical_usable_range"
    #: No canonical cap available -> typed "not derivable", never a fabricated number.
    NOT_DERIVABLE = "not_derivable"
    #: A declared factor / container / entry was malformed -> fail-closed, no range.
    INVALID_ASSUMPTION = "invalid_assumption"


# Closed set of recognized multiplicative usable-area reduction factors; each MUST be a
# finite float in (0, 1]. Recognition matches ``assumption_type`` first, then ``key``.
RECOGNIZED_FACTOR_TYPES = frozenset({"utilization_factor", "efficiency_ratio"})

# Never-Verified ceiling: an incoming ``verified`` is capped to this on EVERY outcome.
NEVER_VERIFIED_COVERAGE_CEILING = "conditional"

# Mandatory honest label on a derived range (illustrative/derived, never gross/net/
# sellable/feasible/buildable, never Verified).
DERIVED_RANGE_LABEL = (
    "ILLUSTRATIVE DERIVED practical-usable-area range: the DRAFT residential "
    "zoning-floor-area cap (ZR 23-21) multiplied by explicitly-declared typed "
    "assumption factors ONLY. NOT gross, net, sellable, or feasible floor area; "
    "NOT a buildable envelope; NOT an optimization result. Draft (needs_review); "
    "requires professional review; NOT Verified."
)


# --- Numeric guards (fail-closed): reject bool / non-numeric / NaN / +-inf. ---


def _finite_float(value: Any) -> float | None:
    """``value`` as a finite float, or ``None`` when not usable (bool / non-numeric /
    NaN / +-inf / int too large for a finite float). Never raises."""
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


def _as_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _factor_type(assumption: dict) -> str | None:
    """Recognized factor type of an assumption, else ``None`` (matches
    ``assumption_type`` first, then ``key``)."""
    for candidate in (assumption.get("assumption_type"), assumption.get("key")):
        if isinstance(candidate, str) and candidate in RECOGNIZED_FACTOR_TYPES:
            return candidate
    return None


def _copy_assumption(assumption: dict) -> dict:
    """Fresh fixed-shape copy of a declared assumption (never aliases the input, so the
    derived object can be mutated downstream without touching the scenario)."""
    return {
        "key": assumption.get("key"),
        "assumption_type": assumption.get("assumption_type"),
        "value": assumption.get("value"),
        "unit": assumption.get("unit"),
        "rationale": assumption.get("rationale"),
    }


# --- Outcome assembly ---


def _bounded_coverage_status(scenario_document: dict) -> str | None:
    """Coverage status carried onto an outcome, never-Verified enforced: an incoming
    ``verified`` (any case) -> ``conditional``; a non-string is not fabricated (``None``)."""
    coverage_status = scenario_document.get("coverage_status")
    if not isinstance(coverage_status, str):
        return None
    if coverage_status.strip().lower() == "verified":
        return NEVER_VERIFIED_COVERAGE_CEILING
    return coverage_status


def _base_document(scenario_document: dict) -> dict:
    """Lineage every outcome carries: bounded (never-Verified) coverage_status,
    needs_review, and the preserved not_verified_disclaimer."""
    disclaimer = scenario_document.get("not_verified_disclaimer")
    return {
        "coverage_status": _bounded_coverage_status(scenario_document),
        "needs_review": True,
        "not_verified_disclaimer": (
            disclaimer if isinstance(disclaimer, str) else NOT_VERIFIED_DISCLAIMER
        ),
    }


def _not_derivable(scenario_document: dict, reason: str, canonical_cap: Any) -> dict:
    """Typed 'no derived range' outcome (no cap, or a declared factor failed closed). No
    fabricated number; the canonical cap is transported VERBATIM (original value/type)."""
    document = {
        "derived_kind": DerivedRangeKind.NOT_DERIVABLE,
        "derivable": False,
        "practical_usable_range": None,
        "canonical_cap_sq_ft": canonical_cap,
        "cap_label": scenario_document.get("cap_label"),
        "applied_factors": [],
        "unapplied_assumptions": [],
        "factor_product": None,
        "label": DERIVED_RANGE_LABEL,
        "reasons": [reason],
        "not_derivable_reason": reason,
    }
    document.update(_base_document(scenario_document))
    return document


def _invalid_assumption(
    scenario_document: dict, reason: str, canonical_cap: Any
) -> dict:
    """Fail-closed on a malformed / out-of-domain factor, a malformed assumptions
    container, or a non-dict entry. No partial range; cap transported VERBATIM, never
    mutated."""
    document = _not_derivable(scenario_document, reason, canonical_cap)
    document["derived_kind"] = DerivedRangeKind.INVALID_ASSUMPTION
    return document


def derive_practical_usable_range(scenario_document: Any) -> dict:
    """Derive an ILLUSTRATIVE practical-usable-range (min/point/max) from a scenario
    document PLUS its explicitly-declared typed assumptions.

    The document is consumed READ-ONLY (never mutated). Returns a NEW, separate derived
    object (contract-free); it is NOT the canonical scenario contract and must never be
    stored or presented as Verified.

    * No positive canonical ``draft_zoning_floor_area_cap_sq_ft`` -> typed
      ``not_derivable`` outcome, no range.
    * A recognized factor (``utilization_factor`` / ``efficiency_ratio``) that is
      NaN/+-inf/negative/zero/>1/non-numeric, a malformed ``assumptions`` container
      (present but not a list), or a non-dict entry -> typed ``invalid_assumption``
      fail-closed outcome, no range.
    * Otherwise -> ``point = cap x product(factors)``; with no factor the endpoints are
      the cap VERBATIM (original type). ``min == point == max`` (a point estimate; no
      uncertainty spread is ever invented).
    * A positive product that underflows to an unrepresentable value (0.0 even with the
      cap folded into the running product) -> typed ``not_derivable``, never a zero range.
    """
    scenario_document = _as_dict(scenario_document)

    # Transport the cap VERBATIM. cap_raw is the ORIGINAL value/type (what every outcome
    # carries + what the no-factor endpoints use). cap_float is a SEPARATE finite-float
    # view used for the multiplicative arithmetic ONLY, so no coercion / precision loss.
    cap_raw = scenario_document.get("draft_zoning_floor_area_cap_sq_ft")
    cap_float = _positive_finite_float(cap_raw)
    if cap_float is None:
        kind = scenario_document.get("scenario_kind")
        return _not_derivable(
            scenario_document,
            (
                "NOT DERIVABLE: the scenario carries no positive canonical "
                "draft_zoning_floor_area_cap_sq_ft "
                f"(scenario_kind={kind!r}); no practical-usable-range is fabricated."
            ),
            cap_raw,
        )

    # Partition declared assumptions. Absent/None container = "no assumptions"
    # (legitimate); present-but-non-list = malformed -> fail closed (no range).
    raw_assumptions = scenario_document.get("assumptions")
    if raw_assumptions is None:
        assumptions: list = []
    elif isinstance(raw_assumptions, list):
        assumptions = raw_assumptions
    else:
        return _invalid_assumption(
            scenario_document,
            (
                "FAIL-CLOSED: the scenario 'assumptions' container is malformed "
                f"(expected a list, got {type(raw_assumptions).__name__}); no range "
                "is derived and the canonical cap is untouched."
            ),
            cap_raw,
        )

    applied_factors: list[dict] = []
    unapplied: list[dict] = []
    factor_values: list[float] = []
    for assumption in assumptions:
        if not isinstance(assumption, dict):
            # Non-dict entry -> fail closed, NO range (never silently skipped).
            return _invalid_assumption(
                scenario_document,
                (
                    "FAIL-CLOSED: a declared assumption entry is not an object "
                    f"(got {type(assumption).__name__}); no range is derived and "
                    "the canonical cap is untouched."
                ),
                cap_raw,
            )
        factor_type = _factor_type(assumption)
        if factor_type is None:
            unapplied.append(_copy_assumption(assumption))
            continue
        # A recognized factor MUST be a finite float in (0, 1].
        factor = _finite_float(assumption.get("value"))
        if factor is None or not (0.0 < factor <= 1.0):
            return _invalid_assumption(
                scenario_document,
                (
                    "FAIL-CLOSED: declared factor "
                    f"{factor_type!r} has an out-of-domain or non-finite value "
                    f"{assumption.get('value')!r} (must be a finite number in (0, 1]); "
                    "no range is derived and the canonical cap is untouched."
                ),
                cap_raw,
            )
        applied_factors.append(_copy_assumption(assumption))
        factor_values.append(factor)

    # Deterministic order: sort applied factors + values together by type/key.
    order = sorted(
        range(len(applied_factors)),
        key=lambda i: (
            str(applied_factors[i].get("assumption_type")),
            str(applied_factors[i].get("key")),
        ),
    )
    applied_factors = [applied_factors[i] for i in order]
    factor_values = [factor_values[i] for i in order]
    unapplied.sort(key=lambda a: (str(a.get("assumption_type")), str(a.get("key"))))

    # Endpoints: cap x product(factors); cap VERBATIM when no factor applied.
    if factor_values:
        # factor_product is the product of the declared factors, for provenance. For
        # extreme factors this standalone product can itself underflow to 0.0.
        product = 1.0
        for factor in factor_values:
            product *= factor
        factor_product = product

        # Arithmetic uses the SEPARATE float view; the transported cap (cap_raw) stays
        # exact. The naive `cap x product` can flush a STILL-REPRESENTABLE result to
        # zero when the standalone product underflowed first (e.g. cap x 1e-162 x
        # 1e-162 is a subnormal ~1.5e-320, but 1e-162 x 1e-162 already underflowed to
        # 0.0). Only when that happens, recompute by folding the cap into the running
        # product so no intermediate underflows prematurely; every non-underflow
        # outcome keeps its exact, already-verified arithmetic unchanged.
        endpoint = cap_float * product
        if endpoint == 0.0:
            endpoint = cap_float
            for factor in factor_values:
                endpoint *= factor
        if not math.isfinite(endpoint) or endpoint < 0.0:
            return _invalid_assumption(
                scenario_document,
                (
                    "FAIL-CLOSED: derived endpoint was non-finite or negative; "
                    "no range is derived."
                ),
                cap_raw,
            )
        if endpoint == 0.0:
            # cap and every factor are strictly positive, so the true result is a
            # positive value; if it still underflows to 0.0 folded, it is genuinely
            # unrepresentable -> report that explicitly, never a successful zero.
            return _not_derivable(
                scenario_document,
                (
                    "NOT DERIVABLE: the derived practical-usable-range is a positive "
                    "value too small to represent as a nonzero double (arithmetic "
                    "underflow); no zero range is fabricated and the canonical cap is "
                    "untouched."
                ),
                cap_raw,
            )
    else:
        # No factor -> the cap VERBATIM (original type), so no hidden default AND no
        # silent int->float precision loss can appear.
        endpoint = cap_raw
        factor_product = 1.0

    practical_usable_range = {
        "min": endpoint,
        "point": endpoint,
        "max": endpoint,
        "unit": "square_feet",
        "is_point_estimate": True,
        "note": (
            "Point estimate: min == point == max. No uncertainty spread is invented; "
            "the range widens only when explicit low/high uncertainty is declared."
        ),
    }

    reasons = [
        (
            "DERIVED (illustrative): practical-usable-range = canonical draft "
            "zoning-floor-area cap x the explicitly-declared typed factor(s). "
            "The canonical cap is transported verbatim and is never replaced by the "
            "derived range. NOT a buildable envelope; NOT Verified."
        )
    ]
    if not factor_values:
        reasons.append(
            "No usable-range factor was declared; the range equals the raw cap "
            "exactly (no utilization / efficiency / optimization default applied)."
        )
    if unapplied:
        reasons.append(
            "Declared assumption(s) not recognized as usable-range factors were "
            "surfaced but NOT applied: "
            + ", ".join(str(a.get("key")) for a in unapplied)
            + "."
        )

    document = {
        "derived_kind": DerivedRangeKind.DERIVED,
        "derivable": True,
        "practical_usable_range": practical_usable_range,
        "canonical_cap_sq_ft": cap_raw,
        "cap_label": (
            scenario_document.get("cap_label")
            if isinstance(scenario_document.get("cap_label"), str)
            else DRAFT_CAP_LABEL
        ),
        "applied_factors": applied_factors,
        "unapplied_assumptions": unapplied,
        "factor_product": factor_product,
        "label": DERIVED_RANGE_LABEL,
        "reasons": reasons,
        "not_derivable_reason": None,
    }
    document.update(_base_document(scenario_document))
    return document
