"""Deterministic OFFLINE single-variable sensitivity / what-if analysis (M5-T008).

Third optimization-side brick under M5 (after ``derive`` M5-T005/M5-T006 and ``ranking``
M5-T007): fills the Compare/Evidence UX's "what if we change ONE assumption" response. It
varies ONE explicitly-named assumption across an EXPLICIT caller-provided list of values, runs
each value through the accepted :func:`app.scenario.derive_practical_usable_range` READ-ONLY,
and returns a NEW, ordered response object. It is contract-free: it is NOT the canonical
scenario contract and must never be stored or presented as Verified.

Hard boundaries (AI-boundary + honesty; also enforced by
``tests/scenario/test_scenario_sensitivity.py``):

* Explicit-only: it varies ONLY the caller-provided explicit values for the named variable -
  each built into a single-assumption set and fed through ``derive`` - and NEVER invents,
  fabricates, or adds a value / scenario / assumption / alternative. Empty / ``None`` values ->
  a single BASELINE point of the RAW scenario (no value applied), never a fabricated value.
* Named variable + named metric: the response NAMES the varied variable AND the response
  metric; every point NAMES the varied variable. No point is emitted without naming what
  varied. The variable is restricted to a factor ``derive`` actually applies
  (``RECOGNIZED_FACTOR_TYPES``), so a what-if is never a flat no-op over an ignored assumption.
* Surfaced numbers only: each point's response uses ONLY already-surfaced numbers (the derived
  illustrative usable-area point / canonical draft cap transported verbatim by ``derive``) -
  never a recomputed legal / cap value, never a hidden weight. Each point carries the tried
  value, its derived point, and the transparent COMPONENTS (a documented function of the
  surfaced numbers only).
* TOTAL, STABLE order: points are ordered by the tried value ASCENDING (finite-valued points
  by magnitude first; a non-finite / non-numeric value bucketed after), ties / equal values
  broken by the EXACT insertion-order-preserving serialization of the point's emitted
  assumption-set echo (a deterministic CONTENT key, never the transient input position). So
  identical input -> byte-identical output INDEPENDENT of the order/duplication the values are
  supplied in.
* Fail closed: an unknown / malformed / non-finite variable, or a malformed ``values``
  container (present but not a list) -> a typed ``invalid`` outcome; a scenario document that
  surfaces no positive draft cap (no_scenario / unsupported / malformed) -> a typed ``empty``
  outcome with a visible reason. A value whose ``derive`` fails closed -> that point is flagged
  not-derivable and KEPT IN PLACE (value order), never given a fabricated point. Every emitted
  value is passed through a strict-JSON-safety sanitizer: a malformed value (NaN / +-Inf /
  negative / float-overflowing / non-serializable) is replaced by a TYPED, bounded placeholder
  marker, never echoed raw. No crash; strict-JSON-safe (``json.dumps(out, allow_nan=False)``
  never raises; no NaN / Inf / negative number is ever emitted).
* Never Verified: ``coverage_status`` can never be ``verified`` on ANY outcome (an incoming
  ``verified`` is capped to ``conditional``); a caller ``variable`` equal to the Verified token
  (any case) is never echoed on the ``invalid`` outcome, so the never-Verified token can never
  enter the output through ANY field; ``needs_review`` + the ``not_verified_disclaimer`` are
  preserved end-to-end; every point is ILLUSTRATIVE (from the draft cap), never Verified.
* Read-only: the scenario document and each value are consumed without mutation and without
  aliasing - the response echoes DEEP COPIES, so the caller's inputs are byte-unchanged after
  analysis.

NOTE ON THE JSON-SAFETY SANITIZER: the strict-JSON-safety helpers below intentionally mirror
those in the sibling ``ranking`` module. This task's allowed paths are ``sensitivity.py`` + its
export + its test only, so a shared ``scenario/_json_safety.py`` cannot be introduced here; a
future decomposition task should extract the common sanitizer. Keeping a self-contained copy is
preferred to importing another module's private helpers.
"""

from __future__ import annotations

import copy
import json
import math
from enum import Enum
from typing import Any

from .constants import NOT_VERIFIED_DISCLAIMER
from .derive import (
    RECOGNIZED_FACTOR_TYPES,
    DerivedRangeKind,
    derive_practical_usable_range,
)

__all__ = [
    "SENSITIVITY_LABEL",
    "SENSITIVITY_RESPONSE_METRIC",
    "SensitivityKind",
    "SensitivityVariable",
    "analyze_scenario_sensitivity",
]


# --- Typed vocabulary + honest labels (all CONSTANTS; nothing computed at runtime). ---


class SensitivityVariable(str, Enum):
    """The EXPLICIT, caller-named variable to vary (string-valued so it serializes straight into
    the response). A point is never emitted without naming this.

    The offerable variables are exactly the multiplicative usable-area reduction factors
    ``derive`` recognizes and applies (``RECOGNIZED_FACTOR_TYPES``): varying anything ``derive``
    ignores would produce a flat, meaningless what-if, so it fails closed instead. Additional
    variables register here only if ``derive`` also recognizes them (asserted by the test suite).
    """

    #: Multiplicative usable-area utilization ratio in (0, 1] applied to the draft cap.
    UTILIZATION_FACTOR = "utilization_factor"
    #: Multiplicative usable-area efficiency ratio in (0, 1] applied to the draft cap.
    EFFICIENCY_RATIO = "efficiency_ratio"


class SensitivityKind:
    """Typed outcome of a sensitivity analysis (string values serialize straight into the object)."""

    #: At least one response point was produced; points are ordered by tried value.
    ANALYZED = "sensitivity_response"
    #: The scenario document surfaces no positive draft cap -> nothing to analyze (visible reason).
    EMPTY = "empty_no_analyzable_cap"
    #: Fail-closed on an unknown/malformed variable or a malformed values container.
    INVALID = "invalid_sensitivity_request"


# Never-Verified ceiling: an incoming ``verified`` is capped to this on EVERY outcome.
NEVER_VERIFIED_COVERAGE_CEILING = "conditional"

#: The single response metric this analysis reports (NAMED on every outcome and point).
SENSITIVITY_RESPONSE_METRIC = "illustrative_usable_area_sq_ft"
SENSITIVITY_RESPONSE_METRIC_LABEL = (
    "Illustrative practical-usable-area point (square feet): the derived point = draft cap x "
    "product(applied factors), transported from derive_practical_usable_range verbatim."
)

# Mandatory honest label on a sensitivity response (illustrative / from the draft cap, never Verified).
SENSITIVITY_LABEL = (
    "ILLUSTRATIVE single-variable sensitivity / what-if response: ONE explicitly-named "
    "assumption varied across the caller's EXPLICIT list of values, each point computed ONLY "
    "from already-surfaced numbers (the DRAFT residential zoning-floor-area cap under ZR 23-21 "
    "x explicitly-declared typed factors). NOT gross, net, sellable, or feasible floor area; "
    "NOT a buildable envelope; NOT an optimization over invented values. Draft (needs_review); "
    "requires professional review; NOT Verified."
)

# Mandatory honest label on every response point.
POINT_LABEL = (
    "ILLUSTRATIVE response point: ONE explicit tried value for the named variable, its derived "
    "illustrative usable-area point computed from already-surfaced numbers only. NOT Verified; "
    "requires professional review."
)

# Human label naming each variable (so a point can never travel without naming what varied).
_VARIABLE_LABELS: dict[SensitivityVariable, str] = {
    SensitivityVariable.UTILIZATION_FACTOR: (
        "Utilization factor: the multiplicative usable-area utilization ratio in (0, 1] applied "
        "to the draft cap."
    ),
    SensitivityVariable.EFFICIENCY_RATIO: (
        "Efficiency ratio: the multiplicative usable-area efficiency ratio in (0, 1] applied to "
        "the draft cap."
    ),
}

#: Fixed, transparent provenance fields on each generated single-assumption set. Only the
#: ``value`` is the caller's explicit input; unit/rationale are documentation, never invented
#: numerics.
_SENSITIVITY_UNIT = "ratio"
_SENSITIVITY_POINT_RATIONALE = (
    "Sensitivity what-if: the named variable set to one explicit caller-provided value; no "
    "value is invented."
)

#: Sentinel meaning "no value supplied" -> a single BASELINE point of the raw scenario. It is
#: never emitted (its point carries value=None, is_baseline=True) and never a fabricated value.
_BASELINE = object()


# --- Numeric guards (fail-closed): reject bool / non-numeric / NaN / +-inf / negative. ---


def _is_number(value: Any) -> bool:
    """True only for a real numeric (int/float), never a bool."""
    return isinstance(value, int | float) and not isinstance(value, bool)


def _finite_float(value: Any) -> float | None:
    """``value`` as a finite float, or ``None`` when not usable (bool / non-numeric / NaN /
    +-inf / int too large for a finite float). Never raises."""
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
    """Finite float greater than or equal to zero, else ``None`` (a response is never negative)."""
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


# --- Strict-JSON-safety sanitizer for emitted echoes (fail-closed on malformed values). ---
# Mirrors ranking.py's sanitizer (see the module note); scope forbids a shared module here.


#: Max characters of a malformed value's repr surfaced in its typed placeholder marker.
_UNSAFE_REPR_LIMIT = 120

#: Max bit length of an integer whose EXACT decimal repr is small and safe to surface. A larger
#: integer is described by magnitude, because a full decimal expansion is unbounded work and,
#: past CPython's int->str ceiling (4300 digits), raises ``ValueError`` - which would crash an
#: unguarded ``repr``. 256 bits is ~77 decimal digits: under ``_UNSAFE_REPR_LIMIT`` and far
#: under the interpreter's ceiling.
_INT_DECIMAL_SAFE_BITS = 256

#: Reserved prefix for the deterministic replacement of a dict key that is not strict-JSON-safe.
_UNSAFE_KEY_TOKEN_PREFIX = "__unsafe_key__"


def _bounded_repr(rendered: str) -> str:
    """An already-rendered repr truncated to a bounded length with an explicit marker."""
    if len(rendered) <= _UNSAFE_REPR_LIMIT:
        return rendered
    return rendered[:_UNSAFE_REPR_LIMIT] + "...(truncated)"


def _safe_scalar_repr(value: Any) -> str:
    """A deterministic, bounded textual rendering of ``value`` that NEVER triggers CPython's
    integer string-conversion limit and NEVER embeds a non-deterministic object address:
    ``bool``/``float`` -> ``repr``; ``int`` -> exact decimal ``repr`` when small, else a magnitude
    descriptor; anything else -> ``<TypeName>`` (its type only, never an address-bearing repr)."""
    if isinstance(value, bool):
        return repr(value)
    if isinstance(value, int):
        if value.bit_length() <= _INT_DECIMAL_SAFE_BITS:
            return repr(value)
        return f"int(sign={'-' if value < 0 else '+'}, bit_length={value.bit_length()})"
    if isinstance(value, float):
        return repr(value)
    return f"<{type(value).__name__}>"


def _unsafe_marker(kind: str, value: Any) -> dict:
    """A TYPED, strict-JSON-safe placeholder standing in for a malformed emitted value, so a
    caller's malformed value is surfaced HONESTLY (typed) yet never echoed RAW. Numeric kinds
    carry a deterministic, bounded, decimal-repr-SAFE rendering; an ``unsupported`` object carries
    only its (deterministic) type name - never its address-bearing ``repr``."""
    marker = {
        "unsafe_value_removed": True,
        "unsafe_kind": kind,
        "unsafe_value_type": type(value).__name__,
    }
    if kind != "unsupported":
        marker["unsafe_value_repr"] = _bounded_repr(_safe_scalar_repr(value))
    return marker


def _unsafe_key_token(key: Any) -> str:
    """Deterministic, strict-JSON-safe replacement string for a dict key that cannot be a JSON
    object key. Built from :func:`_safe_scalar_repr`, so an arbitrary object surfaces its TYPE
    only and a huge integer surfaces its MAGNITUDE - the token neither raises nor varies
    run-to-run."""
    return f"{_UNSAFE_KEY_TOKEN_PREFIX}:{_bounded_repr(_safe_scalar_repr(key))}"


def _safe_key(key: Any) -> Any:
    """A dict key guaranteed safe for ``json.dumps(..., allow_nan=False)``: a ``str``/``None``/
    ``bool`` verbatim; a FINITE ``int``/``float`` verbatim; a non-finite/float-overflowing numeric
    key or ANY other type -> a deterministic typed :func:`_unsafe_key_token`."""
    if isinstance(key, str) or key is None or isinstance(key, bool):
        return key
    if isinstance(key, int | float):
        try:
            as_float = float(key)
        except (OverflowError, ValueError):
            return _unsafe_key_token(key)
        return key if math.isfinite(as_float) else _unsafe_key_token(key)
    return _unsafe_key_token(key)


def _json_safe(value: Any) -> Any:
    """A recursive, strict-JSON-safe rendering of ``value`` (insertion order preserved): a
    NaN/+-Inf/negative/float-overflowing number or a non-JSON-serializable object becomes a typed
    :func:`_unsafe_marker`; ``dict``/``list``/``tuple`` are walked (tuples emit as lists); a finite
    non-negative number, ``bool``, ``None`` and ``str`` pass through. The result contains no
    NaN/Inf/negative number and no non-serializable value, so ``json.dumps(result,
    allow_nan=False)`` never raises. Never mutates ``value`` (it builds fresh containers)."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int | float):
        try:
            as_float = float(value)
        except (OverflowError, ValueError):
            return _unsafe_marker("overflow", value)
        if math.isnan(as_float):
            return _unsafe_marker("nan", value)
        if math.isinf(as_float):
            return _unsafe_marker("infinity", value)
        if as_float < 0.0:
            return _unsafe_marker("negative", value)
        return value
    if value is None or isinstance(value, str):
        return value
    if isinstance(value, dict):
        return _json_safe_mapping(value)
    if isinstance(value, list | tuple):
        return [_json_safe(item) for item in value]
    return _unsafe_marker("unsupported", value)


def _json_safe_mapping(value: dict) -> dict:
    """Strict-JSON-safe rendering of a mapping (insertion order preserved): each key is made
    JSON-safe by :func:`_safe_key` and each value recursively by :func:`_json_safe`. Two DISTINCT
    source keys that collapse to the SAME safe key are de-collided with a deterministic ``#N``
    positional suffix, so a rejected key never SILENTLY overwrites another."""
    out: dict = {}
    for key, item in value.items():
        safe_key = _safe_key(key)
        if safe_key in out:
            base = safe_key if isinstance(safe_key, str) else _unsafe_key_token(key)
            suffix = 1
            while f"{base}#{suffix}" in out:
                suffix += 1
            safe_key = f"{base}#{suffix}"
        out[safe_key] = _json_safe(item)
    return out


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


def _base_lineage(scenario_document: Any) -> dict:
    """Lineage every outcome carries: bounded (never-Verified) coverage_status, needs_review, and
    the preserved not_verified_disclaimer."""
    disclaimer = (
        scenario_document.get("not_verified_disclaimer")
        if isinstance(scenario_document, dict)
        else None
    )
    return {
        "coverage_status": _bounded_coverage_status(scenario_document),
        "needs_review": True,
        "not_verified_disclaimer": (
            disclaimer if isinstance(disclaimer, str) else NOT_VERIFIED_DISCLAIMER
        ),
    }


# --- Variable normalization (fail-closed) ---


def _normalize_variable(variable: Any) -> SensitivityVariable | None:
    """The caller-supplied variable as a :class:`SensitivityVariable`, or ``None`` when it is
    unknown / malformed / non-finite. Accepts the enum member itself or its string value; any
    other type is rejected fail-closed. Belt-and-suspenders: only a variable ``derive`` actually
    applies as a factor is offerable, so a member outside ``RECOGNIZED_FACTOR_TYPES`` fails
    closed (never a flat what-if)."""
    if isinstance(variable, SensitivityVariable):
        member = variable
    elif isinstance(variable, str):
        try:
            member = SensitivityVariable(variable)
        except ValueError:
            return None
    else:
        return None
    if member.value not in RECOGNIZED_FACTOR_TYPES:
        return None
    return member


def _safe_variable_echo(variable: Any) -> str | None:
    """The caller variable echoed on an ``invalid`` outcome, kept strict-JSON-safe AND
    never-Verified: a non-string variable is never echoed (``None``), and a string equal to the
    Verified token (any case) is never echoed either (``None``), so a caller can neither make the
    output non-JSON-safe nor inject the never-Verified token into the output through this field."""
    if not isinstance(variable, str):
        return None
    if variable.strip().lower() == "verified":
        return None
    return variable


# --- Point construction ---


def _build_point(
    scenario_document: dict, variable: SensitivityVariable, tried: Any
) -> tuple[Any, dict]:
    """Build ONE response point (position assigned later) for a single tried value.

    ``tried`` is either the :data:`_BASELINE` sentinel (empty values -> a single point of the RAW
    scenario, no factor applied) or one explicit caller value. The value is FIRST made
    strict-JSON-safe (:func:`_json_safe`), then built into a single
    ``{key, assumption_type, value, unit, rationale}`` assumption fed through ``derive`` on a
    shallow scenario-document copy - so ``derive`` scores exactly the caller's explicit value with
    its own fail-closed guards. A derive outcome that is not a DERIVED range yields a not-derivable
    point flagged with derive's own reason, never a fabricated point.

    Sanitizing the value BEFORE it reaches ``derive`` (not only in the echo) is required for
    fail-closed no-crash + determinism: ``derive`` renders an out-of-domain factor value via
    ``repr`` in its reason string, so a raw huge integer would raise CPython's int->str limit
    (a crash) and a raw arbitrary object would leak a non-deterministic address. The sanitized
    value is a bounded, address-free typed marker for any malformed value and the value itself for
    a JSON-safe one, so ``derive`` always sees something it can repr safely and deterministically.
    The same sanitized value is what the point EMITS (tried value, echoed assumption-set,
    components), so nothing malformed is ever echoed raw. Returns ``(raw_value_for_sort,
    strict-JSON-safe point core)``; the RAW value is used ONLY for ordering and never emitted."""
    is_baseline = tried is _BASELINE
    if is_baseline:
        raw_for_sort: Any = _BASELINE
        safe_value: Any = None
        generated: list = []
    else:
        raw_for_sort = tried
        safe_value = _json_safe(tried)
        generated = [
            {
                "key": variable.value,
                "assumption_type": variable.value,
                "value": safe_value,
                "unit": _SENSITIVITY_UNIT,
                "rationale": _SENSITIVITY_POINT_RATIONALE,
            }
        ]

    echo = copy.deepcopy(generated)
    candidate_document = {**scenario_document, "assumptions": echo}
    derived = derive_practical_usable_range(candidate_document)

    derivable = False
    response_point: Any = None
    components: dict | None = None
    not_derivable_reason: str | None = None
    if derived.get("derived_kind") == DerivedRangeKind.DERIVED:
        usable = derived.get("practical_usable_range")
        point_value = usable.get("point") if isinstance(usable, dict) else None
        if _non_negative_finite_float(point_value) is None:
            not_derivable_reason = (
                "The derived range carried no non-negative finite usable-area point; flagged "
                "not-derivable (fail-closed, no fabricated response point)."
            )
        else:
            derivable = True
            response_point = point_value
            components = {
                "variable": variable.value,
                "tried_value": None if is_baseline else copy.deepcopy(tried),
                "is_baseline": is_baseline,
                "illustrative_usable_area_sq_ft": point_value,
                "canonical_cap_sq_ft": derived.get("canonical_cap_sq_ft"),
                "factor_product": derived.get("factor_product"),
                "formula": (
                    "response_point = illustrative_usable_area_sq_ft = canonical draft "
                    "zoning-floor-area cap x product(applied factors). No hidden weight; the "
                    "response is exactly the already-surfaced derived point for this value."
                ),
            }
    else:
        not_derivable_reason = derived.get("not_derivable_reason") or (
            "This tried value did not produce a derived illustrative range "
            f"(derived_kind={derived.get('derived_kind')!r}); flagged not-derivable, no "
            "fabricated response point."
        )

    core = _json_safe(
        {
            "variable": variable.value,
            "variable_label": _VARIABLE_LABELS[variable],
            "value": None if is_baseline else copy.deepcopy(tried),
            "is_baseline": is_baseline,
            "assumption_set": echo,
            "derivable": derivable,
            "response_metric": SENSITIVITY_RESPONSE_METRIC,
            "response_point": response_point,
            "components": components,
            "derived_kind": derived.get("derived_kind"),
            "not_derivable_reason": not_derivable_reason,
            "label": POINT_LABEL,
            "derived": derived,
        }
    )
    return raw_for_sort, core


# --- Ordering (total, deterministic, input-order-independent) ---


def _content_key(assumption_set_echo: Any) -> str:
    """Deterministic tie-break secondary key: the EXACT (insertion-order-preserving) JSON
    serialization of the already-sanitized assumption-set echo - the very bytes this point
    contributes to the output. Ordering equal-value points by these bytes makes the output a pure
    function of the SET of points, INDEPENDENT of the transient input position. ``sort_keys`` is
    deliberately NOT used (it would collapse dicts that differ only in key insertion order).
    Never raises: the echo is already strict-JSON-safe, with a deterministic ``repr`` fallback."""
    try:
        return json.dumps(assumption_set_echo, ensure_ascii=True, default=repr)
    except TypeError:
        return "repr:" + repr(assumption_set_echo)


def _sort_key(raw_for_sort: Any, content_key: str) -> tuple:
    """Total, deterministic sort key: points with a FINITE numeric value first (ordered by that
    value ASCENDING = 'explicit value order'), then non-finite/non-numeric values (the baseline
    sentinel, NaN/+-Inf, non-numeric) bucketed after, all finally tie-broken by the content key
    ASCENDING. Equal keys occur only for byte-identical points, which are interchangeable."""
    finite = _finite_float(raw_for_sort)
    return (
        0 if finite is not None else 1,
        finite if finite is not None else 0.0,
        content_key,
    )


def _order_points(built: list[tuple[Any, dict]]) -> list[dict]:
    """Order built ``(raw_value, point_core)`` pairs by the total deterministic key and assign a
    1-based ``position``."""
    keyed = [
        (_sort_key(raw, _content_key(core["assumption_set"])), core) for raw, core in built
    ]
    keyed.sort(key=lambda pair: pair[0])
    return [{"position": index + 1, **core} for index, (_, core) in enumerate(keyed)]


# --- Typed-outcome assemblers ---


def _invalid_result(scenario_document: Any, variable: Any, reason: str) -> dict:
    """Fail-closed ``invalid`` outcome (unknown/malformed variable or malformed values container).
    The variable is echoed only when it is a plain string that is NOT the Verified token."""
    result = {
        "sensitivity_kind": SensitivityKind.INVALID,
        "variable": _safe_variable_echo(variable),
        "variable_label": None,
        "response_metric": SENSITIVITY_RESPONSE_METRIC,
        "response_metric_label": SENSITIVITY_RESPONSE_METRIC_LABEL,
        "analyzed": False,
        "point_count": 0,
        "derivable_count": 0,
        "points": [],
        "label": SENSITIVITY_LABEL,
        "reasons": [reason],
        "invalid_reason": reason,
        "empty_reason": None,
    }
    result.update(_base_lineage(scenario_document))
    return result


def _empty_result(scenario_document: Any, variable: SensitivityVariable, reason: str) -> dict:
    """Typed ``empty`` outcome: the scenario document surfaces no positive draft cap, so there is
    nothing to analyze. Empty response + a visible reason, never a fabricated point."""
    result = {
        "sensitivity_kind": SensitivityKind.EMPTY,
        "variable": variable.value,
        "variable_label": _VARIABLE_LABELS[variable],
        "response_metric": SENSITIVITY_RESPONSE_METRIC,
        "response_metric_label": SENSITIVITY_RESPONSE_METRIC_LABEL,
        "analyzed": False,
        "point_count": 0,
        "derivable_count": 0,
        "points": [],
        "label": SENSITIVITY_LABEL,
        "reasons": [reason],
        "invalid_reason": None,
        "empty_reason": reason,
    }
    result.update(_base_lineage(scenario_document))
    return result


def analyze_scenario_sensitivity(
    scenario_document: Any,
    variable: Any,
    values: Any = None,
) -> dict:
    """Vary ONE explicitly-named assumption across an EXPLICIT list of values for ONE scenario.

    The scenario document and every value are consumed READ-ONLY (never mutated, never aliased
    into the output). Returns a NEW, separate sensitivity object (contract-free); it is NOT the
    canonical scenario contract and must never be stored or presented as Verified.

    * ``variable`` is the EXPLICIT caller variable (:class:`SensitivityVariable` or its string
      value, restricted to a factor ``derive`` applies). An unknown / malformed / non-finite
      variable -> typed ``invalid`` outcome.
    * ``values`` is a list of explicit values to try for that variable. ``None`` / empty -> a
      single BASELINE point of the RAW scenario (no value applied), never a fabricated value. A
      non-list (and non-None) container -> typed ``invalid`` outcome.
    * A scenario document that surfaces no positive ``draft_zoning_floor_area_cap_sq_ft``
      (no_scenario / unsupported / malformed) -> typed ``empty`` outcome with a visible reason.
    * Each value is run through ``derive_practical_usable_range`` and its response point is the
      already-surfaced derived usable-area point. A value whose derivation fails closed is flagged
      not-derivable and KEPT IN PLACE (value order), never given a fabricated point.

    The result is deterministic and strict-JSON-safe: identical inputs (in any value order or
    duplication) yield byte-identical output, and ``json.dumps(result, allow_nan=False)`` never
    raises (no NaN / Inf / negative number is emitted).
    """
    normalized = _normalize_variable(variable)
    if normalized is None:
        return _invalid_result(
            scenario_document,
            variable,
            (
                "FAIL-CLOSED: the sensitivity variable is unknown, malformed, or non-finite "
                f"(recognized variables: {sorted(v.value for v in SensitivityVariable)}). No "
                "point is analyzed and no value is fabricated."
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
        return _empty_result(
            scenario_document,
            normalized,
            (
                "EMPTY: the scenario document surfaces no positive canonical "
                "draft_zoning_floor_area_cap_sq_ft (no_scenario / unsupported / malformed); "
                "there is no illustrative usable area to analyze and no point is fabricated."
            ),
        )

    # Absent/None or empty list = "baseline" (rank the raw scenario, no value applied);
    # present-but-non-list = malformed -> fail closed.
    if values is None:
        values_to_try: list = [_BASELINE]
        baseline_mode = True
    elif isinstance(values, list):
        if values:
            values_to_try = list(values)
            baseline_mode = False
        else:
            values_to_try = [_BASELINE]
            baseline_mode = True
    else:
        return _invalid_result(
            scenario_document,
            variable,
            (
                "FAIL-CLOSED: the values container is malformed (expected a list of explicit "
                f"values, got {type(values).__name__}); no point is analyzed and no value is "
                "fabricated."
            ),
        )

    built = [_build_point(scenario_document, normalized, value) for value in values_to_try]
    points = _order_points(built)
    derivable_count = sum(1 for point in points if point["derivable"])

    reasons = [
        (
            "RESPONSE (illustrative): the caller's EXPLICIT values for the named variable, each "
            "point's response a documented function of already-surfaced numbers (the derived "
            "illustrative usable-area point = draft cap x declared factor); no value is invented "
            "and no legal value is recomputed."
        )
    ]
    if baseline_mode:
        reasons.append(
            "No explicit values were supplied; a single BASELINE point of the RAW scenario (no "
            "value applied) is returned - never a fabricated value."
        )
    if derivable_count < len(points):
        reasons.append(
            "One or more tried values did not produce a derived illustrative range; those points "
            "are flagged not-derivable and KEPT IN PLACE (value order), never given a fabricated "
            "response point."
        )

    result = {
        "sensitivity_kind": SensitivityKind.ANALYZED,
        "variable": normalized.value,
        "variable_label": _VARIABLE_LABELS[normalized],
        "response_metric": SENSITIVITY_RESPONSE_METRIC,
        "response_metric_label": SENSITIVITY_RESPONSE_METRIC_LABEL,
        "analyzed": True,
        "point_count": len(points),
        "derivable_count": derivable_count,
        "points": points,
        "label": SENSITIVITY_LABEL,
        "reasons": reasons,
        "invalid_reason": None,
        "empty_reason": None,
    }
    result.update(_base_lineage(scenario_document))
    return result
