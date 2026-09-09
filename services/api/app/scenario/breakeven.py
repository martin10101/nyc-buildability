"""Deterministic OFFLINE scenario break-even / threshold FINDER (M5-T011).

Fifth and final optimization-side brick under M5 (derive -> sensitivity -> ranking -> comparison ->
THRESHOLD). It answers ONE honest analyst question - "over an EXPLICIT, bounded domain of candidate
values for one named assumption VARIABLE, at which candidate does a named derived RESPONSE METRIC (a
practical-usable-range field: min / point / max sq ft) FIRST meet-or-cross a caller-supplied numeric
TARGET?" - by a DETERMINISTIC bounded SCAN: for each candidate it builds a single-assumption set,
calls the accepted :func:`app.scenario.derive_practical_usable_range` READ-ONLY, reads the named
metric, and detects the FIRST adjacent grid interval where the metric crosses the target.

Guarantees (all also enforced by ``tests/scenario/test_scenario_breakeven.py``):

* Never invents / never Verified: the crossing is the HONEST grid BRACKET (two adjacent
  derivable candidates + transported metric values + direction); no interpolated sub-grid value
  is presented as derived, and any convenience midpoint is explicitly ``verified: False``. The
  canonical draft cap is transported VERBATIM from ``derive`` (no independent legal calculation);
  every outcome carries :data:`NOT_VERIFIED_DISCLAIMER` and can never be Verified.
* Deterministic + total order: identical inputs (in any domain order / duplication) produce
  byte-identical output - candidates are ordered ASCENDING by value (non-finite / non-numeric
  bucketed after), ties broken by a deterministic content key, never input position.
* Monotonicity-honest: it reports the FIRST crossing, counts ALL crossings, and sets
  ``non_monotonic`` when more than one exists. Already-met / no-crossing are typed markers,
  never a raise.
* Typed + fail-closed: a bad variable / metric / target / domain or a cap-less scenario yields
  a typed ``invalid`` / ``empty`` result with a reason; a candidate whose ``derive`` fails closed
  is flagged not-derivable and KEPT IN PLACE (value order), never dropped or fabricated.
* Strict-JSON-safe: every emitted value passes through the SHARED ``._json_safety._json_safe``
  (never re-duplicated), so ``json.dumps(result, allow_nan=False)`` never raises and no NaN / Inf
  / negative number or object address is emitted (below-target is ``meets_target: false``, never
  a negative margin).
* Contract-free + offline + read-only: imports only stdlib + ``.derive`` + ``.constants`` +
  ``._json_safety``; no network / persistence / file / subprocess I/O; the scenario document and
  domain are never mutated or aliased (echoes are freshly-built sanitized deep copies).
"""

from __future__ import annotations

import copy
import json
import math
from enum import Enum
from typing import Any

from ._json_safety import _json_safe
from .constants import NOT_VERIFIED_DISCLAIMER
from .derive import (
    RECOGNIZED_FACTOR_TYPES,
    DerivedRangeKind,
    derive_practical_usable_range,
)

__all__ = [
    "THRESHOLD_LABEL",
    "ThresholdKind",
    "ThresholdResponseMetric",
    "ThresholdVariable",
    "find_scenario_threshold",
]


# --- Typed vocabulary + honest labels (all CONSTANTS; nothing computed at runtime). ---


class ThresholdVariable(str, Enum):
    """The EXPLICIT, caller-named assumption to scan (string-valued so it serializes straight into
    the result). The offerable variables are exactly the usable-area reduction factors ``derive``
    applies (``RECOGNIZED_FACTOR_TYPES``); scanning anything ``derive`` ignores would produce a flat
    response with no honest crossing, so it fails closed instead."""

    #: Multiplicative usable-area utilization ratio in (0, 1] applied to the draft cap.
    UTILIZATION_FACTOR = "utilization_factor"
    #: Multiplicative usable-area efficiency ratio in (0, 1] applied to the draft cap.
    EFFICIENCY_RATIO = "efficiency_ratio"


class ThresholdResponseMetric(str, Enum):
    """The named derived response metric a crossing is measured against - a practical-usable-range
    endpoint transported VERBATIM from ``derive`` (min / point / max). String-valued so it
    serializes straight into the result; NAMED on every outcome and candidate."""

    #: Derived illustrative usable-area range MINIMUM (sq ft).
    USABLE_RANGE_MIN = "usable_range_min"
    #: Derived illustrative usable-area range POINT (sq ft) - the default response metric.
    USABLE_RANGE_POINT = "usable_range_point"
    #: Derived illustrative usable-area range MAXIMUM (sq ft).
    USABLE_RANGE_MAX = "usable_range_max"


class ThresholdKind:
    """Typed outcome of a threshold scan (string values serialize straight into the object)."""

    #: A first crossing bracket was found: the metric meets-or-crosses the target between two
    #: adjacent derivable candidates.
    FOUND = "scenario_threshold_crossing"
    #: The target is already met at the first derivable candidate (no rising threshold to find).
    ALREADY_MET = "target_already_met"
    #: No derivable candidate in the explicit domain ever meets the target.
    NO_CROSSING = "no_crossing_in_domain"
    #: The scenario document surfaces no positive draft cap -> nothing to scan (visible reason).
    EMPTY = "empty_no_analyzable_cap"
    #: Fail-closed: unknown / malformed variable, bad target, or an empty / malformed domain.
    INVALID = "invalid_threshold_request"


class _CrossingDirection:
    """The direction of a detected crossing across a bracket (string values serialize directly)."""

    #: The metric rises from BELOW the target to at-or-above it going lower -> upper.
    ASCENDING_MEETS = "meets_target_ascending"
    #: The metric falls from at-or-above the target to BELOW it going lower -> upper.
    DESCENDING_LEAVES = "leaves_target_descending"


# Never-Verified ceiling: an incoming ``verified`` is capped to this on EVERY outcome.
NEVER_VERIFIED_COVERAGE_CEILING = "conditional"

#: The derived ``practical_usable_range`` field each response metric reads (transported verbatim).
_METRIC_FIELD: dict[ThresholdResponseMetric, str] = {
    ThresholdResponseMetric.USABLE_RANGE_MIN: "min",
    ThresholdResponseMetric.USABLE_RANGE_POINT: "point",
    ThresholdResponseMetric.USABLE_RANGE_MAX: "max",
}

_METRIC_LABELS: dict[ThresholdResponseMetric, str] = {
    ThresholdResponseMetric.USABLE_RANGE_MIN: (
        "Derived illustrative practical-usable-area range MINIMUM (sq ft): draft cap x "
        "product(applied factors), transported verbatim from derive_practical_usable_range."
    ),
    ThresholdResponseMetric.USABLE_RANGE_POINT: (
        "Derived illustrative practical-usable-area range POINT (sq ft): draft cap x "
        "product(applied factors), transported verbatim from derive_practical_usable_range."
    ),
    ThresholdResponseMetric.USABLE_RANGE_MAX: (
        "Derived illustrative practical-usable-area range MAXIMUM (sq ft): draft cap x "
        "product(applied factors), transported verbatim from derive_practical_usable_range."
    ),
}

# Human label naming each variable (so a candidate can never travel without naming what varied).
_VARIABLE_LABELS: dict[ThresholdVariable, str] = {
    ThresholdVariable.UTILIZATION_FACTOR: (
        "Utilization factor: the multiplicative usable-area utilization ratio in (0, 1] applied "
        "to the draft cap."
    ),
    ThresholdVariable.EFFICIENCY_RATIO: (
        "Efficiency ratio: the multiplicative usable-area efficiency ratio in (0, 1] applied to "
        "the draft cap."
    ),
}

# Mandatory honest label on a threshold result (illustrative / from the draft cap, never Verified).
THRESHOLD_LABEL = (
    "ILLUSTRATIVE break-even / threshold response: ONE explicitly-named assumption scanned across "
    "the caller's EXPLICIT bounded domain of candidate values to find the FIRST candidate at which "
    "a named derived usable-area metric meets-or-crosses a numeric target. Each candidate's metric "
    "is the derived point = the DRAFT residential zoning-floor-area cap (ZR 23-21) x "
    "explicitly-declared typed factors, transported VERBATIM from derive_practical_usable_range. "
    "The crossing is reported as an HONEST grid BRACKET, never an interpolated sub-grid value. NOT "
    "gross, net, sellable, or feasible floor area; NOT a buildable envelope; NOT an optimization "
    "over invented values. Draft (needs_review); requires professional review; NOT Verified."
)

# Mandatory honest label on every candidate row.
CANDIDATE_LABEL = (
    "ILLUSTRATIVE candidate: ONE explicit value for the named variable, its derived illustrative "
    "usable-area metric transported verbatim from derive, and whether that metric meets the "
    "target. NOT Verified; requires professional review."
)

#: Fixed, transparent provenance fields on each generated single-assumption set. Only the ``value``
#: is the caller's explicit input; unit / rationale are documentation, never invented numerics.
_CANDIDATE_UNIT = "ratio"
_CANDIDATE_RATIONALE = (
    "Threshold scan: the named variable set to one explicit caller-provided candidate value; no "
    "value is invented."
)


# --- Numeric guards (fail-closed): reject bool / non-numeric / NaN / +-inf / negative. ---


def _is_number(value: Any) -> bool:
    """True only for a real numeric (int/float), never a bool."""
    return isinstance(value, int | float) and not isinstance(value, bool)


def _finite_float(value: Any) -> float | None:
    """``value`` as a finite float, or ``None`` when not usable (bool / non-numeric / NaN / +-inf /
    int too large for a finite float). Never raises."""
    if not _is_number(value):
        return None
    try:
        as_float = float(value)
    except (OverflowError, ValueError):
        return None
    if not math.isfinite(as_float):
        return None
    return as_float


def _non_negative_finite_float(value: Any) -> float | None:
    """Finite float greater than or equal to zero, else ``None`` (a metric / target is never
    negative)."""
    result = _finite_float(value)
    if result is None or result < 0.0:
        return None
    return result


def _positive_finite_float(value: Any) -> float | None:
    """Finite float strictly greater than zero, else ``None``."""
    result = _finite_float(value)
    if result is None or result <= 0.0:
        return None
    return result


# --- Never-Verified lineage carried onto every outcome ---


def _bounded_coverage_status(scenario_document: Any) -> str | None:
    """Coverage status carried onto an outcome, never-Verified enforced: an incoming ``verified``
    (any case) -> ``conditional``; a non-string is not fabricated (``None``)."""
    coverage_status = (
        scenario_document.get("coverage_status") if isinstance(scenario_document, dict) else None
    )
    if not isinstance(coverage_status, str):
        return None
    if coverage_status.strip().lower() == "verified":
        return NEVER_VERIFIED_COVERAGE_CEILING
    return coverage_status


def _str_or_none(value: Any) -> str | None:
    """``value`` when it is a plain string, else ``None`` (identity is never fabricated)."""
    return value if isinstance(value, str) else None


def _base_lineage(scenario_document: Any) -> dict:
    """Top-level honesty lineage stamped on EVERY outcome: the bounded (never-Verified) coverage
    status, ``needs_review`` True, and the finder's OWN canonical :data:`NOT_VERIFIED_DISCLAIMER`
    (never the input document's field, which could otherwise suppress or replace the honesty
    warning on a contract-free object that must never be presented as Verified)."""
    return {
        "coverage_status": _bounded_coverage_status(scenario_document),
        "needs_review": True,
        "not_verified_disclaimer": NOT_VERIFIED_DISCLAIMER,
    }


def _base_lineage_identity(scenario_document: Any) -> dict:
    """Scenario identity + bounded coverage status surfaced on the result (AS-1 base lineage). Every
    field is read straight from the scenario document (scalars only, nothing mutable is aliased); a
    never-Verified coverage ceiling is enforced."""
    evaluated = (
        scenario_document.get("evaluated_input") if isinstance(scenario_document, dict) else None
    )
    evaluated = evaluated if isinstance(evaluated, dict) else {}
    document = scenario_document if isinstance(scenario_document, dict) else {}
    return {
        "bbl": _str_or_none(evaluated.get("bbl")),
        "scenario_kind": _str_or_none(document.get("scenario_kind")),
        "contract_version": _str_or_none(document.get("contract_version")),
        "coverage_status": _bounded_coverage_status(scenario_document),
        "data_completeness": _str_or_none(document.get("data_completeness")),
    }


# --- Variable / metric normalization (fail-closed) ---


def _normalize_variable(variable: Any) -> ThresholdVariable | None:
    """The caller-supplied variable as a :class:`ThresholdVariable`, or ``None`` when unknown /
    malformed. Accepts the enum member or its string value; any other type fails closed. A member
    outside ``RECOGNIZED_FACTOR_TYPES`` (one ``derive`` would not apply) also fails closed."""
    if isinstance(variable, ThresholdVariable):
        member = variable
    elif isinstance(variable, str):
        try:
            member = ThresholdVariable(variable)
        except ValueError:
            return None
    else:
        return None
    if member.value not in RECOGNIZED_FACTOR_TYPES:
        return None
    return member


def _normalize_metric(response_metric: Any) -> ThresholdResponseMetric | None:
    """The caller-supplied response metric as a :class:`ThresholdResponseMetric`, or ``None`` when
    it is unknown / malformed. Accepts the enum member itself or its string value."""
    if isinstance(response_metric, ThresholdResponseMetric):
        return response_metric
    if isinstance(response_metric, str):
        try:
            return ThresholdResponseMetric(response_metric)
        except ValueError:
            return None
    return None


def _safe_variable_echo(variable: Any) -> str | None:
    """The caller variable echoed on an ``invalid`` outcome, kept strict-JSON-safe AND
    never-Verified: a non-string variable, or a string equal to the Verified token (any case), is
    never echoed (``None``), so a caller can neither make the output non-JSON-safe nor inject the
    never-Verified token through this field."""
    if not isinstance(variable, str):
        return None
    if variable.strip().lower() == "verified":
        return None
    return variable


# --- Candidate construction (explicit-only, read-only, sanitized) ---


def _build_candidate(
    scenario_document: dict,
    variable: ThresholdVariable,
    metric: ThresholdResponseMetric,
    field: str,
    target_float: float,
    target_echo: Any,
    candidate: Any,
) -> tuple[Any, dict]:
    """Build ONE candidate row for a single explicit candidate value. The value is sanitized
    (:func:`_json_safe`), built into a ``{key, assumption_type, value, unit, rationale}``
    assumption, and fed through ``derive`` on a shallow scenario-document copy; the SAME sanitized
    structures are what the row EMITS, so nothing malformed is echoed raw and the caller's input is
    never aliased. A ``derive`` outcome that is not a DERIVED range (or whose metric is not a
    non-negative finite number) yields a not-derivable row with a reason, never a fabricated metric.
    Returns ``(raw_candidate, row core)``; the raw value is used ONLY for ordering / midpoint."""
    safe_value = _json_safe(candidate)
    generated = [
        {
            "key": variable.value,
            "assumption_type": variable.value,
            "value": safe_value,
            "unit": _CANDIDATE_UNIT,
            "rationale": _CANDIDATE_RATIONALE,
        }
    ]
    echo = copy.deepcopy(generated)
    candidate_document = {**scenario_document, "assumptions": echo}
    derived = derive_practical_usable_range(candidate_document)

    derivable = False
    metric_value: Any = None
    meets_target: bool | None = None
    components: dict | None = None
    not_derivable_reason: str | None = None
    if derived.get("derived_kind") == DerivedRangeKind.DERIVED:
        usable = derived.get("practical_usable_range")
        raw_metric = usable.get(field) if isinstance(usable, dict) else None
        metric_float = _non_negative_finite_float(raw_metric)
        if metric_float is None:
            not_derivable_reason = (
                "The derived range carried no non-negative finite usable-area "
                f"{field}; flagged not-derivable (fail-closed, no fabricated metric)."
            )
        else:
            derivable = True
            metric_value = raw_metric
            meets_target = metric_float >= target_float
            components = {
                "variable": variable.value,
                "candidate_value": safe_value,
                "response_metric": metric.value,
                "metric_value": metric_value,
                "canonical_cap_sq_ft": derived.get("canonical_cap_sq_ft"),
                "factor_product": derived.get("factor_product"),
                "target": target_echo,
                "meets_target": meets_target,
                "formula": (
                    "meets_target = (metric_value >= target). metric_value is the derived "
                    "illustrative usable-area " + field + " = canonical draft zoning-floor-area "
                    "cap x product(applied factors), transported verbatim from "
                    "derive_practical_usable_range. No legal value is recomputed."
                ),
            }
    else:
        not_derivable_reason = derived.get("not_derivable_reason") or (
            "This candidate value did not produce a derived illustrative range "
            f"(derived_kind={derived.get('derived_kind')!r}); flagged not-derivable, no "
            "fabricated metric."
        )

    core = _json_safe(
        {
            "candidate_value": safe_value,
            "variable": variable.value,
            "variable_label": _VARIABLE_LABELS[variable],
            "response_metric": metric.value,
            "response_metric_label": _METRIC_LABELS[metric],
            "assumption_set": echo,
            "derivable": derivable,
            "metric_value": metric_value,
            "target": target_echo,
            "meets_target": meets_target,
            "components": components,
            "derived_kind": derived.get("derived_kind"),
            "not_derivable_reason": not_derivable_reason,
            "label": CANDIDATE_LABEL,
            "derived": derived,
        }
    )
    return candidate, core


# --- Ordering (total, deterministic, input-order-independent) ---


def _content_key(assumption_set_echo: Any) -> str:
    """Deterministic tie-break secondary key: the EXACT (insertion-order-preserving) JSON
    serialization of the already-sanitized assumption-set echo - the very bytes this row
    contributes to the output. Ordering equal-value candidates by these bytes makes the output a
    pure function of the SET of candidates, independent of input position. ``sort_keys`` is
    deliberately NOT used (it would collapse dicts differing only in key order). Never raises
    (deterministic ``repr`` fallback)."""
    try:
        return json.dumps(assumption_set_echo, ensure_ascii=True, default=repr)
    except TypeError:
        return "repr:" + repr(assumption_set_echo)


def _sort_key(raw_candidate: Any, content_key: str) -> tuple:
    """Total, deterministic sort key: candidates with a FINITE numeric value first (ordered by that
    value ASCENDING = the numeric grid), then non-finite / non-numeric values bucketed after, all
    finally tie-broken by the content key ASCENDING. Equal keys occur only for byte-identical rows,
    which are interchangeable."""
    finite = _finite_float(raw_candidate)
    return (
        0 if finite is not None else 1,
        finite if finite is not None else 0.0,
        content_key,
    )


def _order_candidates(built: list[tuple[Any, dict]]) -> list[tuple[Any, dict]]:
    """Order built ``(raw_candidate, row core)`` pairs by the total deterministic key and assign a
    1-based ``position``. The raw candidate is preserved for the crossing walk / midpoint but is
    never emitted."""
    keyed = [
        (_sort_key(raw, _content_key(core["assumption_set"])), raw, core) for raw, core in built
    ]
    keyed.sort(key=lambda triple: triple[0])
    return [(raw, {"position": index + 1, **core}) for index, (_, raw, core) in enumerate(keyed)]


# --- Crossing detection (honest grid bracket; no interpolation presented as derived) ---


def _bracket_midpoint(raw_lower: Any, raw_upper: Any) -> dict | None:
    """The plain arithmetic midpoint of two bracketing candidate values, EXPLICITLY labelled an
    illustrative estimate and ``verified: False`` - never a derived, interpolated, or Verified
    crossing. Returns ``None`` when a finite non-negative endpoint is unavailable (never a
    fabricated number)."""
    lower = _non_negative_finite_float(raw_lower)
    upper = _non_negative_finite_float(raw_upper)
    if lower is None or upper is None:
        return None
    midpoint = (lower + upper) / 2.0
    if not math.isfinite(midpoint) or midpoint < 0.0:
        return None
    return {
        "value": midpoint,
        "is_estimate": True,
        "verified": False,
        "note": (
            "ILLUSTRATIVE arithmetic midpoint of the bracketing candidate values ONLY. It is NOT a "
            "derived, interpolated, or Verified crossing value - the honest crossing is the grid "
            "BRACKET (lower / upper candidates). Provided for convenience; requires professional "
            "review."
        ),
    }


def _crossing_object(
    lower: dict,
    upper: dict,
    raw_lower: Any,
    raw_upper: Any,
    target_echo: Any,
    metric_name: str,
) -> dict:
    """The HONEST crossing bracket for two adjacent derivable candidates whose ``meets_target``
    differs: the two candidate values + their transported metric values + direction + grid
    positions. No interpolated sub-grid value is presented as derived; a clearly-labelled
    convenience midpoint is attached separately."""
    ascending = (not lower["meets_target"]) and upper["meets_target"]
    direction = (
        _CrossingDirection.ASCENDING_MEETS
        if ascending
        else _CrossingDirection.DESCENDING_LEAVES
    )
    return {
        "lower_candidate": lower["candidate_value"],
        "lower_metric_value": lower["metric_value"],
        "lower_meets_target": lower["meets_target"],
        "lower_position": lower["position"],
        "upper_candidate": upper["candidate_value"],
        "upper_metric_value": upper["metric_value"],
        "upper_meets_target": upper["meets_target"],
        "upper_position": upper["position"],
        "response_metric": metric_name,
        "target": target_echo,
        "direction": direction,
        "grid_adjacent": (upper["position"] - lower["position"]) == 1,
        "illustrative_bracket_midpoint": _bracket_midpoint(raw_lower, raw_upper),
        "note": (
            "HONEST grid bracket: the target is crossed strictly BETWEEN these two adjacent "
            "derivable candidates. The reported crossing is the explicit grid bracket, never an "
            "interpolated sub-grid value presented as derived. NOT Verified."
        ),
    }


def _scan_crossings(
    ordered: list[tuple[Any, dict]],
    target_echo: Any,
    metric_name: str,
) -> tuple[list[dict], list[tuple[Any, dict]]]:
    """Walk the ordered candidates and collect every crossing between consecutive DERIVABLE
    candidates (a change in ``meets_target``). Returns ``(crossings, derivable_rows)``: honest
    bracket objects in scan order, and the ``(raw_candidate, row)`` pairs that derived a metric."""
    derivable_rows = [(raw, row) for raw, row in ordered if row["derivable"]]
    crossings: list[dict] = []
    for (raw_lower, lower), (raw_upper, upper) in zip(derivable_rows, derivable_rows[1:]):
        if lower["meets_target"] != upper["meets_target"]:
            crossings.append(
                _crossing_object(lower, upper, raw_lower, raw_upper, target_echo, metric_name)
            )
    return crossings, derivable_rows


# --- Typed-outcome assemblers ---


def _degenerate_result(
    scenario_document: Any,
    variable: Any,
    metric: ThresholdResponseMetric | None,
    target_echo: Any,
    kind: str,
    reason: str,
) -> dict:
    """A typed ``invalid`` / ``empty`` outcome: no scan performed, a machine-readable reason, never
    a fabricated candidate, crossing, or metric. The variable is echoed only when it is a plain,
    non-Verified string; the metric only when it normalized."""
    result = {
        "threshold_kind": kind,
        "variable": _safe_variable_echo(variable),
        "variable_label": None,
        "response_metric": metric.value if metric is not None else None,
        "response_metric_label": _METRIC_LABELS[metric] if metric is not None else None,
        "target": target_echo,
        "base_lineage": _base_lineage_identity(scenario_document),
        "scanned": False,
        "candidate_count": 0,
        "derivable_count": 0,
        "candidates": [],
        "crossing": None,
        "crossings_count": 0,
        "non_monotonic": False,
        "first_meeting_candidate": None,
        "label": THRESHOLD_LABEL,
        "reasons": [reason],
        "invalid_reason": reason if kind == ThresholdKind.INVALID else None,
        "empty_reason": reason if kind == ThresholdKind.EMPTY else None,
    }
    result.update(_base_lineage(scenario_document))
    return result


def _result_reasons(
    kind: str, derivable_count: int, candidate_count: int, non_monotonic: bool
) -> list[str]:
    """The transparent, deterministic reason list for a scanned outcome."""
    headline = {
        ThresholdKind.FOUND: (
            "FOUND (illustrative): the metric first meets-or-crosses the target between two "
            "adjacent derivable candidates. The crossing is the HONEST grid bracket; the canonical "
            "draft cap is transported verbatim and no legal value is recomputed."
        ),
        ThresholdKind.ALREADY_MET: (
            "ALREADY MET (illustrative): the target is already met at the first derivable "
            "candidate, so there is no rising threshold to find. No candidate or crossing is "
            "fabricated."
        ),
        ThresholdKind.NO_CROSSING: (
            "NO CROSSING (illustrative): no derivable candidate in the explicit domain meets the "
            "target. No candidate or crossing is fabricated."
        ),
    }[kind]
    reasons = [headline]
    if derivable_count < candidate_count:
        reasons.append(
            "One or more candidates did not produce a derived illustrative range; those rows are "
            "flagged not-derivable and KEPT IN PLACE (value order), never dropped and never given "
            "a fabricated metric."
        )
    if non_monotonic:
        reasons.append(
            "NON-MONOTONIC: the metric crosses the target more than once across the domain; the "
            "FIRST crossing is reported and the non_monotonic flag is set so the caller is not "
            "misled."
        )
    return reasons


def find_scenario_threshold(
    scenario_document: Any,
    variable: Any,
    target: Any,
    domain: Any,
    response_metric: Any = ThresholdResponseMetric.USABLE_RANGE_POINT,
) -> dict:
    """Find the FIRST candidate at which a named derived usable-area metric meets-or-crosses a
    numeric ``target``, over the EXPLICIT bounded ``domain`` of candidate values for ONE named
    ``variable`` (a factor ``derive`` applies; ``response_metric`` selects the min / point / max
    endpoint, default point).

    The scenario document and domain are consumed READ-ONLY (never mutated or aliased); the
    return is a NEW contract-free object that must never be stored or presented as Verified. It
    fails closed to a typed ``invalid`` outcome on an unknown variable / metric, a non-finite /
    negative / absent target, or a ``None`` / non-list / empty domain; to a typed ``empty``
    outcome when the scenario surfaces no positive ``draft_zoning_floor_area_cap_sq_ft``.
    Candidates are scanned ASCENDING by value; one whose ``derive`` fails closed is flagged
    not-derivable and KEPT IN PLACE.

    Outcome kind is ``FOUND`` / ``ALREADY_MET`` / ``NO_CROSSING``. Monotonicity is NOT assumed:
    every crossing is counted, ``non_monotonic`` is set when more than one exists, and the FIRST
    crossing (an HONEST grid bracket, never an interpolated value) is the reported one. Output
    is deterministic and strict-JSON-safe: ``json.dumps(result, allow_nan=False)`` never raises.
    """
    normalized = _normalize_variable(variable)
    metric = _normalize_metric(response_metric)
    # Sanitize the target echo up front so an out-of-range / malformed target can never make the
    # invalid outcome non-JSON-safe; the numeric guard below decides validity independently.
    target_echo = _json_safe(target)

    if normalized is None:
        return _degenerate_result(
            scenario_document,
            variable,
            metric,
            target_echo,
            ThresholdKind.INVALID,
            (
                "FAIL-CLOSED: the threshold variable is unknown or malformed (recognized "
                f"variables: {sorted(v.value for v in ThresholdVariable)}). No candidate is "
                "scanned and no value is fabricated."
            ),
        )

    if metric is None:
        return _degenerate_result(
            scenario_document,
            variable,
            None,
            target_echo,
            ThresholdKind.INVALID,
            (
                "FAIL-CLOSED: the response metric is unknown or malformed (recognized metrics: "
                f"{sorted(m.value for m in ThresholdResponseMetric)}). No candidate is scanned and "
                "no value is fabricated."
            ),
        )

    target_float = _non_negative_finite_float(target)
    if target_float is None:
        return _degenerate_result(
            scenario_document,
            variable,
            metric,
            target_echo,
            ThresholdKind.INVALID,
            (
                "FAIL-CLOSED: the target is not a finite non-negative number (a square-foot "
                "threshold); it is absent, non-numeric, boolean, NaN / +-Inf, negative, or "
                "float-overflowing. No candidate is scanned and no value is fabricated."
            ),
        )

    if (
        _positive_finite_float(
            scenario_document.get("draft_zoning_floor_area_cap_sq_ft")
            if isinstance(scenario_document, dict)
            else None
        )
        is None
    ):
        return _degenerate_result(
            scenario_document,
            variable,
            metric,
            target_echo,
            ThresholdKind.EMPTY,
            (
                "EMPTY: the scenario document surfaces no positive canonical "
                "draft_zoning_floor_area_cap_sq_ft (no_scenario / unsupported / malformed); there "
                "is no illustrative usable area to scan and no candidate is fabricated."
            ),
        )

    if not isinstance(domain, list) or not domain:
        return _degenerate_result(
            scenario_document,
            variable,
            metric,
            target_echo,
            ThresholdKind.INVALID,
            (
                "FAIL-CLOSED: the candidate domain is empty or malformed (expected a non-empty "
                f"list of explicit candidate values, got {type(domain).__name__}). No candidate is "
                "scanned and no value is fabricated."
            ),
        )

    field = _METRIC_FIELD[metric]
    built = [
        _build_candidate(
            scenario_document, normalized, metric, field, target_float, target_echo, c
        )
        for c in domain
    ]
    ordered = _order_candidates(built)
    candidates = [row for _, row in ordered]
    derivable_count = sum(1 for row in candidates if row["derivable"])

    crossings, derivable_rows = _scan_crossings(ordered, target_echo, metric.value)
    crossings_count = len(crossings)
    non_monotonic = crossings_count >= 2
    first_crossing = crossings[0] if crossings else None

    if not derivable_rows:
        kind = ThresholdKind.NO_CROSSING
        first_meeting_candidate: Any = None
    elif derivable_rows[0][1]["meets_target"]:
        kind = ThresholdKind.ALREADY_MET
        first_meeting_candidate = derivable_rows[0][1]["candidate_value"]
    elif first_crossing is not None:
        kind = ThresholdKind.FOUND
        # The first derivable candidate is below the target and the first crossing is therefore the
        # upward bracket; the smallest candidate that MEETS the target is its upper endpoint.
        first_meeting_candidate = first_crossing["upper_candidate"]
    else:
        kind = ThresholdKind.NO_CROSSING
        first_meeting_candidate = None

    reasons = _result_reasons(kind, derivable_count, len(candidates), non_monotonic)

    result = {
        "threshold_kind": kind,
        "variable": normalized.value,
        "variable_label": _VARIABLE_LABELS[normalized],
        "response_metric": metric.value,
        "response_metric_label": _METRIC_LABELS[metric],
        "target": target_echo,
        "base_lineage": _base_lineage_identity(scenario_document),
        "scanned": True,
        "candidate_count": len(candidates),
        "derivable_count": derivable_count,
        "candidates": candidates,
        "crossing": first_crossing,
        "crossings_count": crossings_count,
        "non_monotonic": non_monotonic,
        "first_meeting_candidate": first_meeting_candidate,
        "label": THRESHOLD_LABEL,
        "reasons": reasons,
        "invalid_reason": None,
        "empty_reason": None,
    }
    result.update(_base_lineage(scenario_document))
    return result
