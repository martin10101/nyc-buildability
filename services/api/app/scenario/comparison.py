"""Deterministic OFFLINE scenario COMPARISON / delta engine (M5-T010).

Fourth optimization-side brick under M5 (after ``derive`` M5-T005/M5-T006, ``ranking``
M5-T007, and ``sensitivity`` M5-T008): backs the Compare (Step 3) UI's side-by-side view. It
consumes ONE ``scenario`` document plus TWO OR MORE explicitly-declared, NAMED assumption-sets,
runs each set through the accepted :func:`app.scenario.derive_practical_usable_range` READ-ONLY,
and returns a NEW, ordered comparison object. It is contract-free: it is NOT the canonical
scenario contract and must never be stored or presented as Verified.

Hard boundaries (AI-boundary + honesty; also enforced by
``tests/scenario/test_scenario_comparison.py``):

* Consumes ``derive`` READ-ONLY and NEVER recalculates a legal value: each set's illustrative
  range is exactly the ``derive`` echo, and the canonical draft cap is transported VERBATIM from
  ``derive`` (byte-equal to derive's cap echo). The only arithmetic this module performs is the
  BASELINE-RELATIVE delta of already-surfaced numbers (a difference / ratio), never a fresh legal
  calculation.
* Baseline-relative deltas: for each numeric metric (the derived practical-usable-range min /
  point / max and the canonical draft cap) each set carries the ABSOLUTE difference and the
  PERCENT difference versus the baseline set, plus a transparent per-field breakdown naming which
  metric moved and by how much. A delta may legitimately be NEGATIVE (a more-reducing set has a
  smaller usable area than the baseline), so delta values are computed as guaranteed-FINITE floats
  and are deliberately NOT passed through :func:`_json_safe` (which would rewrite a negative into a
  typed marker); ``json.dumps(result, allow_nan=False)`` still never raises because every delta is
  finite by construction (computed from two finite metric values, with a finiteness re-check).
* TOTAL, STABLE order (documented content key, baseline first): all sets are ordered ASCENDING by a
  stable CONTENT key - the EXACT (insertion-order-preserving) strict-JSON serialization of the
  sanitized ``{name, assumption_set}`` echo - so the ordered output is a pure function of the SET
  of named sets, INDEPENDENT of the order they are supplied in. The BASELINE is the first set in
  that order (the smallest content key); every delta is therefore relative to a content-determined
  baseline, never to the caller's transient input position. Ties (byte-identical rows) are
  interchangeable, so ``sorted``'s stability keeps the order total without relying on dict
  insertion order or float equality.
* Never invents: no set / metric / value is fabricated. A NON-baseline set whose derivation is
  not-derivable yields a TYPED not-comparable marker in that set's row (kept in order, never
  dropped, never raised). A percent delta against a zero / ``None`` / absent baseline metric yields
  a typed not-computable marker (no ``ZeroDivisionError``, no NaN / Inf).
* Fail closed / typed degenerate handling: fewer than two sets, a malformed (non-list) container,
  or a not-derivable BASELINE -> a typed ``invalid`` result with a machine-readable reason; a
  scenario document that surfaces no positive draft cap -> a typed ``empty`` result with a visible
  reason. Never an unhandled raise.
* Strict-JSON-safe via the SHARED sanitizer: every echoed set (name + assumptions) and every
  transported ``derived`` breakdown is passed through the shared
  ``services/api/app/scenario/_json_safety._json_safe`` (imported, never re-duplicated - that is the
  duplication M5-T009 removed), so a malformed assumption value is a TYPED, bounded, address-free
  marker and never echoed raw. ``json.dumps(result, allow_nan=False)`` never raises; no NaN / Inf;
  no negative number appears anywhere except a delta field; no object address leaks.
* Never Verified: ``coverage_status`` can never be ``verified`` on ANY outcome (an incoming
  ``verified`` is capped to ``conditional``); ``needs_review`` is always True and the canonical
  ``not_verified_disclaimer`` (:data:`NOT_VERIFIED_DISCLAIMER`) is stamped on EVERY outcome
  regardless of the input document's disclaimer (an empty / whitespace / missing / non-string /
  arbitrary incoming disclaimer can never suppress or replace the honesty warning); every value is
  ILLUSTRATIVE (from the draft cap), never Verified.
* Read-only: the scenario document and each assumption-set are consumed without mutation and
  without aliasing (echoes are freshly-built sanitized structures), so the caller's inputs are
  byte-unchanged after the comparison.
"""

from __future__ import annotations

import json
import math
from typing import Any

from ._json_safety import _json_safe
from .constants import NOT_VERIFIED_DISCLAIMER
from .derive import (
    DerivedRangeKind,
    _cap_section_reference,
    derive_practical_usable_range,
)

__all__ = [
    "COMPARISON_LABEL",
    "COMPARISON_METRIC_KEYS",
    "ComparisonKind",
    "compare_scenario_assumption_sets",
]


# --- Typed vocabulary + honest labels (all CONSTANTS; nothing computed at runtime). ---


class ComparisonKind:
    """Typed outcome of a comparison (string values serialize straight into the object)."""

    #: Two or more sets were compared; sets are ordered by the content key, baseline first.
    COMPARED = "scenario_assumption_set_comparison"
    #: The scenario document surfaces no positive draft cap -> nothing to compare (visible reason).
    EMPTY = "empty_no_comparable_cap"
    #: Fail-closed: fewer than two sets, a malformed container, or a not-derivable baseline.
    INVALID = "invalid_comparison_request"


# Never-Verified ceiling: an incoming ``verified`` is capped to this on EVERY outcome.
NEVER_VERIFIED_COVERAGE_CEILING = "conditional"

#: The numeric metrics compared, in the fixed emission order. usable-range endpoints move with the
#: declared factors; the canonical cap is transported verbatim and is invariant across the sets, so
#: its delta transparently reads zero unless the underlying scenario cap itself differs.
COMPARISON_METRIC_KEYS = (
    "usable_range_min",
    "usable_range_point",
    "usable_range_max",
    "canonical_cap_sq_ft",
)

# The three usable-range metric labels never name a Zoning Resolution section, so they stay
# fixed text; only ``canonical_cap_sq_ft`` (below) names one, derived per-call from the rule
# ACTUALLY evaluated (D-059-R003).
_STATIC_METRIC_LABELS: dict[str, str] = {
    "usable_range_min": (
        "Illustrative practical-usable-area range MINIMUM (sq ft): the derived point-estimate min "
        "= draft cap x applied factors, transported from derive_practical_usable_range."
    ),
    "usable_range_point": (
        "Illustrative practical-usable-area range POINT (sq ft): the derived point = draft cap x "
        "applied factors, transported from derive_practical_usable_range."
    ),
    "usable_range_max": (
        "Illustrative practical-usable-area range MAXIMUM (sq ft): the derived point-estimate max "
        "= draft cap x applied factors, transported from derive_practical_usable_range."
    ),
}


def _canonical_cap_metric_label(section_reference: str | None) -> str:
    """D-059-R003: the ``canonical_cap_sq_ft`` metric label's Zoning Resolution section clause,
    built from the ACTUAL evaluated rule's own citation (never hardcoded). Falls back to a
    section-agnostic clause (never invents a section) when no citation is available."""
    section_clause = (
        f"(ZR {section_reference}, sq ft)"
        if isinstance(section_reference, str) and section_reference
        else "(sq ft; see cap_provenance.citations for the exact Zoning Resolution section)"
    )
    return (
        f"Canonical DRAFT residential zoning-floor-area cap {section_clause}: transported VERBATIM "
        "from derive_practical_usable_range; NEVER independently recalculated by the comparison."
    )


def _metric_labels(section_reference: str | None) -> dict[str, str]:
    """The four compared metrics' labels (D-059-R003): the three usable-range labels are fixed
    text; ``canonical_cap_sq_ft`` is derived per-call from the actually-evaluated rule."""
    return {
        **_STATIC_METRIC_LABELS,
        "canonical_cap_sq_ft": _canonical_cap_metric_label(section_reference),
    }


# Backward-compatible module constant (D-059-R003) for the small set of consumers OUTSIDE this
# task's allowed_paths (none currently import it directly, but it is kept for the same reason
# the other four label constants are: a stable, literally-correct R5 rendering). Byte-identical
# to ``_metric_labels("23-21")``.
_METRIC_LABELS: dict[str, str] = _metric_labels("23-21")


# Mandatory honest label on a comparison (illustrative / from the draft cap, never Verified).
#
# D-059-R003 (M5-T028): the Zoning Resolution section named MUST be derived from the rule
# ACTUALLY evaluated for the subject property (the R6-R12 family cites ZR 23-22, not the R1-R5
# families' 23-21), never hardcoded. ``_comparison_label`` builds the label from whatever
# section the scenario document's own ``cap_provenance`` citation names.
def _comparison_label(section_reference: str | None) -> str:
    """The mandatory comparison label, with the Zoning Resolution section clause built from the
    ACTUAL evaluated rule's citation (``section_reference``) rather than a hardcoded section
    number. Falls back to a section-agnostic clause (never invents a section) when no citation is
    available."""
    section_clause = (
        f"(ZR {section_reference})"
        if isinstance(section_reference, str) and section_reference
        else "(see cap_provenance.citations for the exact Zoning Resolution section)"
    )
    return (
        "ILLUSTRATIVE scenario comparison: two or more explicitly-declared NAMED assumption-sets "
        "compared side-by-side for ONE scenario. Each set's derived illustrative "
        "practical-usable-area "
        "range is echoed from derive_practical_usable_range and its numeric metrics are "
        "delta'd against "
        f"the baseline set (absolute + percent). The canonical draft cap {section_clause} is "
        "transported "
        "VERBATIM; NO independent legal calculation is performed. NOT gross, net, sellable, "
        "or feasible "
        "floor area; NOT a buildable envelope; NOT an optimization over invented sets. Draft "
        "(needs_review); requires professional review; NOT Verified."
    )


# Backward-compatible module constant (D-059-R003) for the small set of consumers OUTSIDE this
# task's allowed_paths that import ``COMPARISON_LABEL`` directly (scenario/__init__.py's
# re-export, and test_scenario_comparison.py's honest-label assertions against the R5 canonical
# fixture). Byte-identical to ``_comparison_label("23-21")`` - the R5 canonical rule_evaluation
# fixture's own citation - so this stays a harmless, literally-correct legacy alias, NOT a
# universal label: the live path below calls ``_comparison_label`` with the real per-request
# citation for every district family.
COMPARISON_LABEL = _comparison_label("23-21")

# Mandatory honest label on every comparison row.
SET_LABEL = (
    "ILLUSTRATIVE comparison row: one explicitly-declared named assumption-set, its derived "
    "illustrative usable-area range and baseline-relative deltas computed from already-surfaced "
    "numbers only. NOT Verified; requires professional review."
)


# --- Numeric guards (fail-closed): reject bool / non-numeric / NaN / +-inf / overflow. ---


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
    """Top-level honesty lineage stamped on EVERY outcome (COMPARED / EMPTY / INVALID): the bounded
    (never-Verified) coverage status, ``needs_review`` True, and the canonical
    ``not_verified_disclaimer``.

    The comparison ALWAYS emits its OWN :data:`NOT_VERIFIED_DISCLAIMER` and never trusts the input
    document's disclaimer field. An empty (``""``), whitespace-only, missing, non-string, or
    otherwise arbitrary incoming disclaimer could otherwise SUPPRESS or REPLACE the honesty warning
    on a contract-free object that must never be presented as Verified; emitting the canonical
    constant unconditionally guarantees every public outcome carries the full not-verified
    disclaimer verbatim."""
    return {
        "coverage_status": _bounded_coverage_status(scenario_document),
        "needs_review": True,
        "not_verified_disclaimer": NOT_VERIFIED_DISCLAIMER,
    }


def _base_lineage_identity(scenario_document: Any) -> dict:
    """Scenario identity + bounded coverage status surfaced on the comparison (AS-1 base
    lineage). Every field is read straight from the scenario document (scalars only, no mutable
    substructure is aliased into the output); a never-Verified coverage ceiling is enforced."""
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


def _compared_metrics_doc(metric_labels: dict[str, str]) -> list[dict]:
    """A fresh, documented list of the numeric metrics this comparison delta's, in emission
    order (so a consumer can render the columns without hard-coding the metric vocabulary).
    ``metric_labels`` (D-059-R003) is the per-call label set from :func:`_metric_labels`, so
    ``canonical_cap_sq_ft`` names the ACTUAL evaluated rule's section."""
    return [{"metric": key, "metric_label": metric_labels[key]} for key in COMPARISON_METRIC_KEYS]


# --- Per-set parsing / derivation (explicit-only, read-only, sanitized) ---


def _parse_entry(entry: Any) -> tuple[str | None, Any, str | None]:
    """Parse one supplied assumption-set entry into ``(name, assumptions, structural_reason)``.

    * A named-set dict ``{"name": <str>, "assumptions": <list>}`` -> ``(name, assumptions, None)``;
      a missing / non-string name is surfaced as ``None`` (never fabricated). The ``assumptions``
      list MUST be EXPLICITLY SUPPLIED as a list: a MISSING or NULL ``assumptions`` is NOT silently
      coerced into a raw empty set (that would fabricate the RAW-scenario outcome the caller never
      declared) - it is a TYPED structural not-comparable failure carrying a reason; likewise an
      ``assumptions`` that is present but NOT a list is a TYPED structural failure (never passed on
      to ``derive`` as a malformed container). An EXPLICIT empty list ``[]`` stays valid - it is the
      RAW scenario, no factor applied.
    * A bare list -> an unnamed set of those assumptions ``(None, entry, None)``.
    * Anything else -> a STRUCTURAL not-comparable row with a reason and no derivation."""
    if isinstance(entry, dict):
        name = _str_or_none(entry.get("name"))
        if "assumptions" not in entry or entry.get("assumptions") is None:
            return (
                name,
                None,
                (
                    "NOT COMPARABLE: the named assumption-set does not EXPLICITLY supply an "
                    "'assumptions' list (it is missing or null). An explicitly-declared set "
                    "requires an explicit list; a missing / null assumptions is NOT silently "
                    "treated as an empty (raw) set. Supply an explicit [] for the raw scenario. "
                    "No delta is fabricated."
                ),
            )
        raw_assumptions = entry["assumptions"]
        if not isinstance(raw_assumptions, list):
            return (
                name,
                None,
                (
                    "NOT COMPARABLE: the named assumption-set's 'assumptions' is malformed - it "
                    f"must be a list, got {type(raw_assumptions).__name__}. An explicit "
                    "assumptions LIST is required; no delta is fabricated."
                ),
            )
        return name, raw_assumptions, None
    if isinstance(entry, list):
        return None, entry, None
    return (
        None,
        None,
        (
            "NOT COMPARABLE: the assumption-set entry is not a named set (an object with 'name' "
            "and 'assumptions') or a bare assumptions list "
            f"(got {type(entry).__name__}); no delta is fabricated."
        ),
    )


def _build_set_core(scenario_document: dict, entry: Any) -> dict:
    """Build ONE comparison-row CORE from a single supplied entry (ordering / baseline / deltas
    are attached later once the baseline is known).

    The entry's assumptions are FIRST made strict-JSON-safe via the shared :func:`_json_safe`
    (identical to a JSON-safe input, a typed address-free marker for a malformed one), then fed
    through ``derive_practical_usable_range`` on a shallow scenario-document copy - so ``derive``
    scores exactly this set with its own fail-closed guards and can never crash on (or leak the
    address of) a malformed value. The SAME sanitized structures are what the row EMITS, so nothing
    malformed is echoed raw and the caller's input is never aliased. A derive outcome that is not a
    DERIVED range (or whose metrics are not all finite) yields a not-comparable core flagged with a
    reason, never a fabricated metric."""
    name, assumptions, structural_reason = _parse_entry(entry)
    if structural_reason is not None:
        return {
            "name": name,
            "assumption_set": _json_safe(entry),
            "comparable": False,
            "derived": None,
            "derived_kind": None,
            "metrics": None,
            "not_comparable_reason": structural_reason,
            "label": SET_LABEL,
        }

    safe_assumptions = _json_safe(assumptions)
    candidate_document = {**scenario_document, "assumptions": safe_assumptions}
    derived = derive_practical_usable_range(candidate_document)
    metrics = _extract_metrics(derived)
    comparable = metrics is not None
    not_comparable_reason: str | None = None
    if not comparable:
        not_comparable_reason = derived.get("not_derivable_reason") or (
            "NOT COMPARABLE: this assumption-set did not produce a derived illustrative range with "
            f"finite metrics (derived_kind={derived.get('derived_kind')!r}); flagged "
            "not-comparable, no delta is fabricated."
        )
    return {
        "name": name,
        "assumption_set": safe_assumptions,
        "comparable": comparable,
        "derived": _json_safe(derived),
        "derived_kind": derived.get("derived_kind"),
        "metrics": metrics,
        "not_comparable_reason": not_comparable_reason,
        "label": SET_LABEL,
    }


def _extract_metrics(derived: dict) -> dict | None:
    """The four compared numeric metrics from a DERIVED outcome, or ``None`` when the outcome is
    not a derived range or any metric is not a finite number (fail-closed: never a partial or
    fabricated metric set). Values are transported VERBATIM (original type) from ``derive``."""
    if derived.get("derived_kind") != DerivedRangeKind.DERIVED:
        return None
    usable_range = derived.get("practical_usable_range")
    if not isinstance(usable_range, dict):
        return None
    metrics = {
        "usable_range_min": usable_range.get("min"),
        "usable_range_point": usable_range.get("point"),
        "usable_range_max": usable_range.get("max"),
        "canonical_cap_sq_ft": derived.get("canonical_cap_sq_ft"),
    }
    if any(_finite_float(value) is None for value in metrics.values()):
        return None
    return metrics


# --- Baseline-relative delta (finite by construction; may be negative) ---


def _metric_delta(
    metric_key: str,
    baseline_value: Any,
    set_value: Any,
    metric_labels: dict[str, str] | None = None,
) -> dict:
    """Baseline-relative delta for ONE metric: the ABSOLUTE difference and the PERCENT difference
    of this set's metric versus the baseline set's metric, plus a transparent breakdown.

    ``metric_labels`` (D-059-R003) is the per-call label set from :func:`_metric_labels`, so
    ``canonical_cap_sq_ft``'s label names the ACTUAL evaluated rule's section; it defaults to the
    R5 (``23-21``) backward-compatible rendering when omitted (a caller that is not the live
    comparison flow, e.g. a targeted unit test of this helper in isolation).

    Both differences are computed from finite floats and are re-checked finite, so the emitted
    delta is ALWAYS a finite number (it may be NEGATIVE - a legitimate reduction) and never NaN /
    Inf; a delta is therefore emitted directly, not through the non-negative-only
    :func:`_json_safe`.
    A missing / non-finite baseline OR set value -> a typed not-computable marker (no delta
    fabricated). A percent delta against a ZERO baseline metric -> a typed not-computable percent
    marker (no ``ZeroDivisionError``, no Inf) while the absolute delta is still reported."""
    labels = metric_labels if metric_labels is not None else _METRIC_LABELS
    baseline_float = _finite_float(baseline_value)
    set_float = _finite_float(set_value)
    entry: dict[str, Any] = {
        "metric": metric_key,
        "metric_label": labels[metric_key],
        "baseline_value": baseline_value if baseline_float is not None else None,
        "set_value": set_value if set_float is not None else None,
        "absolute_delta": None,
        "percent_delta": None,
        "computable": False,
        "moved": None,
        "not_computable_reason": None,
    }
    if baseline_float is None or set_float is None:
        entry["not_computable_reason"] = (
            "NOT COMPUTABLE: the baseline or this set's value for this metric is absent or not a "
            "finite number; no delta is fabricated."
        )
        return entry

    absolute = set_float - baseline_float
    if not math.isfinite(absolute):
        entry["not_computable_reason"] = (
            "NOT COMPUTABLE: the absolute delta was non-finite; no delta is fabricated."
        )
        return entry
    entry["absolute_delta"] = absolute
    entry["computable"] = True
    entry["moved"] = absolute != 0.0

    if baseline_float == 0.0:
        entry["not_computable_reason"] = (
            "PERCENT NOT COMPUTABLE: the baseline value for this metric is zero; a percent delta "
            "against a zero baseline is undefined (no ZeroDivisionError, no Inf/NaN fabricated). "
            "The absolute delta is still reported."
        )
        return entry
    percent = absolute / baseline_float * 100.0
    if not math.isfinite(percent):
        entry["not_computable_reason"] = (
            "PERCENT NOT COMPUTABLE: the percent delta was non-finite; only the absolute delta is "
            "reported."
        )
        return entry
    entry["percent_delta"] = percent
    return entry


# --- Ordering (total, deterministic, input-order-independent) ---


def _content_key(name: str | None, assumption_set_echo: Any) -> str:
    """Deterministic stable content key: the EXACT (insertion-order-preserving) strict-JSON
    serialization of the sanitized ``{name, assumption_set}`` echo - the very bytes this row
    contributes to the output. Ordering by this key makes the ordered comparison a pure function of
    the SET of named sets, INDEPENDENT of the transient input position, and picks a
    content-determined baseline (the smallest key). ``sort_keys`` is deliberately NOT used (it would
    collapse dicts differing only in key insertion order). Never raises: the echo is already
    strict-JSON-safe, with a deterministic ``repr`` fallback."""
    try:
        return json.dumps(
            {"name": name, "assumption_set": assumption_set_echo},
            ensure_ascii=True,
            default=repr,
        )
    except TypeError:
        return "repr:" + repr((name, assumption_set_echo))


# --- Typed-outcome assemblers ---


def _degenerate_result(scenario_document: Any, kind: str, reason: str) -> dict:
    """A typed ``invalid`` / ``empty`` outcome: no comparison performed, a machine-readable reason,
    never a fabricated set or metric."""
    section_reference = _cap_section_reference(scenario_document)
    result = {
        "comparison_kind": kind,
        "base_lineage": _base_lineage_identity(scenario_document),
        "baseline_set_name": None,
        "baseline_metrics": None,
        "compared_metrics": _compared_metrics_doc(_metric_labels(section_reference)),
        "set_count": 0,
        "comparable_count": 0,
        "sets": [],
        "label": _comparison_label(section_reference),
        "reasons": [reason],
        "invalid_reason": reason if kind == ComparisonKind.INVALID else None,
        "empty_reason": reason if kind == ComparisonKind.EMPTY else None,
    }
    result.update(_base_lineage(scenario_document))
    return result


def compare_scenario_assumption_sets(
    scenario_document: Any,
    assumption_sets: Any,
) -> dict:
    """Compare TWO OR MORE explicitly-declared NAMED assumption-sets for ONE scenario document.

    The scenario document and every assumption-set are consumed READ-ONLY (never mutated, never
    aliased into the output). Returns a NEW, separate comparison object (contract-free); it is NOT
    the canonical scenario contract and must never be stored or presented as Verified.

    * ``assumption_sets`` is a list of named sets, each a dict
      ``{"name": <str>, "assumptions": <list of assumption dicts>}`` (a bare list is accepted as an
      unnamed set). Fewer than two sets, or a non-list container -> typed ``invalid`` outcome. A
      named set MUST explicitly supply an ``assumptions`` LIST: a missing / null / non-list
      ``assumptions`` is a TYPED not-comparable row (never silently coerced into a raw empty set),
      while an explicit ``[]`` remains valid (the raw scenario). A structural not-comparable row is
      kept in stable order; if it is the baseline (smallest content key) the outcome is ``invalid``.
    * A scenario document that surfaces no positive ``draft_zoning_floor_area_cap_sq_ft`` -> typed
      ``empty`` outcome with a visible reason.
    * Each set is run through ``derive_practical_usable_range`` READ-ONLY; its illustrative range
      and canonical cap are transported verbatim. Sets are ordered ASCENDING by a stable content
      key and the FIRST (smallest key) is the BASELINE. If the baseline is not derivable -> typed
      ``invalid`` outcome. A NON-baseline set that is not derivable is kept in order as a typed
      not-comparable row, never dropped.
    * For every set and every numeric metric (usable-range min / point / max + canonical cap) the
      row carries the absolute and percent delta versus the baseline, with a per-field breakdown.

    The result is deterministic and strict-JSON-safe: identical inputs (in any set order) yield
    byte-identical output, and ``json.dumps(result, allow_nan=False)`` never raises (every number
    is finite; only delta fields may be negative).
    """
    scenario_doc = scenario_document if isinstance(scenario_document, dict) else {}

    if _positive_finite_float(scenario_doc.get("draft_zoning_floor_area_cap_sq_ft")) is None:
        return _degenerate_result(
            scenario_document,
            ComparisonKind.EMPTY,
            (
                "EMPTY: the scenario document surfaces no positive canonical "
                "draft_zoning_floor_area_cap_sq_ft (no_scenario / unsupported / malformed); there "
                "is no illustrative usable area to compare and no set is fabricated."
            ),
        )

    if not isinstance(assumption_sets, list):
        return _degenerate_result(
            scenario_document,
            ComparisonKind.INVALID,
            (
                "FAIL-CLOSED: the assumption_sets container is malformed (expected a list of "
                f"named assumption-sets, got {type(assumption_sets).__name__}); no comparison is "
                "performed and no set is fabricated."
            ),
        )

    if len(assumption_sets) < 2:
        return _degenerate_result(
            scenario_document,
            ComparisonKind.INVALID,
            (
                "FAIL-CLOSED: a comparison needs at least two named assumption-sets; got "
                f"{len(assumption_sets)}. No comparison is performed and no set is fabricated."
            ),
        )

    cores = [_build_set_core(scenario_doc, entry) for entry in assumption_sets]
    ordered = sorted(cores, key=lambda core: _content_key(core["name"], core["assumption_set"]))
    baseline = ordered[0]

    if not baseline["comparable"]:
        return _degenerate_result(
            scenario_document,
            ComparisonKind.INVALID,
            (
                "FAIL-CLOSED: the baseline assumption-set (the set with the smallest stable "
                "content key, ordered first) is not derivable, so no baseline-relative delta can "
                "be computed. Baseline reason: "
                + str(baseline["not_comparable_reason"])
            ),
        )

    baseline_metrics = baseline["metrics"]
    section_reference = _cap_section_reference(scenario_document)
    metric_labels = _metric_labels(section_reference)
    sets_out: list[dict] = []
    for index, core in enumerate(ordered):
        set_metrics = core["metrics"]
        metric_deltas = [
            _metric_delta(
                metric_key,
                baseline_metrics.get(metric_key),
                set_metrics.get(metric_key) if isinstance(set_metrics, dict) else None,
                metric_labels,
            )
            for metric_key in COMPARISON_METRIC_KEYS
        ]
        changed = any(delta["moved"] for delta in metric_deltas if delta["moved"] is not None)
        sets_out.append(
            {
                "position": index + 1,
                "is_baseline": index == 0,
                **core,
                "metric_deltas": metric_deltas,
                "changed_from_baseline": bool(changed),
            }
        )

    comparable_count = sum(1 for core in ordered if core["comparable"])
    reasons = [
        (
            "COMPARED (illustrative): the explicitly-declared named assumption-sets ordered by a "
            "stable content key (baseline first), each set's derived illustrative usable-area "
            "range "
            "echoed from derive_practical_usable_range and its numeric metrics delta'd against the "
            "baseline. The canonical draft cap is transported verbatim; no legal value is "
            "recomputed and no set is invented."
        )
    ]
    if comparable_count < len(ordered):
        reasons.append(
            "One or more NON-baseline assumption-sets did not produce a derived illustrative "
            "range; "
            "those rows are flagged not-comparable and KEPT IN ORDER, never dropped and never "
            "given "
            "a fabricated delta."
        )

    result = {
        "comparison_kind": ComparisonKind.COMPARED,
        "base_lineage": _base_lineage_identity(scenario_document),
        "baseline_set_name": baseline["name"],
        "baseline_metrics": baseline_metrics,
        "compared_metrics": _compared_metrics_doc(metric_labels),
        "set_count": len(ordered),
        "comparable_count": comparable_count,
        "sets": sets_out,
        "label": _comparison_label(section_reference),
        "reasons": reasons,
        "invalid_reason": None,
        "empty_reason": None,
    }
    result.update(_base_lineage(scenario_document))
    return result
