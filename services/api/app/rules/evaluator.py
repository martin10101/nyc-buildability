"""Deterministic rule evaluator (M4-T001).

Given a validated ``RuleDefinition``, a plain inputs dict, the snapshot store,
and (optionally) an M2-T013 spatial context, produce a full ``EvaluationTrace``
wrapped in a ``RuleResult``. The evaluation is pure and reproducible: same rule
version + same inputs + same snapshots -> byte-identical trace.

Load-bearing guarantees:

* No guessed values. A missing REQUIRED input yields typed missing-data
  behaviour (``missing_critical`` / ``professional_review_required``) with NO
  computed output - never a fabricated number (PRD section 12; RE-S4).
* Uncertainty is propagated, never collapsed. An uncertain M2-T013 geometric
  context downgrades coverage to ``professional_review_required`` (or
  ``data_conflict``) and records WHY; the rule never turns uncertain geometry
  into a definitive single-district conclusion (owner directive item 8; RE-S4).
* ``verified`` is unreachable for a draft rule. A draft rule tops out at
  ``conditional``; ``verified`` requires a ``published`` rule evaluated with a
  matching G6 approval attached (owner directive item 5; RE-S2).
"""

from __future__ import annotations

import math
import re
from typing import Any

from . import coverage as cov
from . import lifecycle
from .models import (
    ComputationStep,
    EvaluationTrace,
    PredicateTrace,
    RuleDefinition,
    RuleResult,
)
from .operations import COMPUTE_OPS, PREDICATE_OPS, OperationError
from .snapshots import SnapshotStore

# M2-T013 lot-overall classes that are NOT a single confident assignment. A
# single-district-confident lot is the only class that does not, by itself,
# force professional review of a district-scoped rule.
_GEOM_CONFIDENT = "single_district_confident"
_GEOM_DATA_CONFLICT = "data_conflict"
_PRR = cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED  # short alias for line width


class EvaluationError(RuntimeError):
    pass


# --------------------------------------------------------------------------
# Applicability / predicate evaluation
# --------------------------------------------------------------------------

def _eval_predicate(node: dict, inputs: dict) -> tuple[bool, dict]:
    if "all" in node:
        results = [_eval_predicate(child, inputs) for child in node["all"]]
        outcome = all(r[0] for r in results)
        return outcome, {"all": [r[1] for r in results], "outcome": outcome}
    if "any" in node:
        results = [_eval_predicate(child, inputs) for child in node["any"]]
        outcome = any(r[0] for r in results)
        return outcome, {"any": [r[1] for r in results], "outcome": outcome}
    if "not" in node:
        inner_outcome, inner_trace = _eval_predicate(node["not"], inputs)
        return (not inner_outcome), {"not": inner_trace, "outcome": not inner_outcome}
    op = node["op"]
    input_name = node.get("input")
    value = inputs.get(input_name) if input_name is not None else None
    outcome = PREDICATE_OPS[op](value, node)
    detail = {k: node[k] for k in ("value", "values", "compare") if k in node}
    detail["value_seen"] = value
    return outcome, PredicateTrace(op, input_name, detail, outcome).as_dict()


def _predicate_input_names(node: dict) -> set[str]:
    names: set[str] = set()
    for combinator in ("all", "any"):
        for child in node.get(combinator, []):
            names |= _predicate_input_names(child)
    if "not" in node:
        names |= _predicate_input_names(node["not"])
    if node.get("input") is not None:
        names.add(node["input"])
    return names


# --------------------------------------------------------------------------
# Computation
# --------------------------------------------------------------------------

def _resolve_ref(ref: dict, inputs: dict, params: dict, step_values: dict) -> Any:
    if "const" in ref:
        return ref["const"]
    if "input" in ref:
        return inputs.get(ref["input"])
    if "param" in ref:
        return params[ref["param"]]
    if "param_select" in ref:
        sel = ref["param_select"]
        key = inputs.get(sel["key_input"])
        table = params[sel["map"]]
        if key not in table:
            raise EvaluationError(
                f"param_select: key {key!r} (from input {sel['key_input']!r}) "
                f"not in parameter map {sel['map']!r}"
            )
        return table[key]
    if "step" in ref:
        return step_values[ref["step"]]
    raise EvaluationError(f"malformed ref {ref!r}")


def _run_computation(rule: RuleDefinition, inputs: dict) -> tuple[list, dict]:
    step_values: dict[str, float] = {}
    step_traces: list = []
    for step in rule.computation["steps"]:
        resolved = [
            _resolve_ref(arg, inputs, rule.parameters, step_values) for arg in step["args"]
        ]
        try:
            result = COMPUTE_OPS[step["op"]](resolved)
        except OperationError as exc:
            raise EvaluationError(f"step {step['id']!r}: {exc}") from exc
        step_values[step["id"]] = result
        step_traces.append(
            ComputationStep(
                step["id"], step["op"], resolved, result, step.get("note", "")
            ).as_dict()
        )
    outputs = {
        name: step_values[target["step"]]
        for name, target in rule.computation["outputs"].items()
    }
    return step_traces, outputs


# --------------------------------------------------------------------------
# Uncertainty (M2-T013) + exceptions
# --------------------------------------------------------------------------

def _uncertainty_effect(
    rule: RuleDefinition, spatial_context: dict | None
) -> tuple[str | None, dict]:
    """Return (coverage_downgrade_or_None, uncertainty_trace)."""
    if not spatial_context:
        return None, {"propagated": False}
    cls = spatial_context.get("lot_overall_class")
    prr = bool(spatial_context.get("professional_review_required"))
    note = spatial_context.get("coverage_note")
    policy = rule.uncertainty_policy or {}
    trace = {
        "propagated": True,
        "lot_overall_class": cls,
        "professional_review_required": prr,
        "coverage_note": note,
        "collapsed_into_definitive_district": False,
    }
    if cls == _GEOM_DATA_CONFLICT:
        trace["effect"] = cov.COVERAGE_DATA_CONFLICT
        return policy.get("data_conflict_coverage", cov.COVERAGE_DATA_CONFLICT), trace
    if cls is not None and cls != _GEOM_CONFIDENT:
        effect = policy.get("geometry_uncertain_coverage", _PRR)
        trace["effect"] = effect
        return effect, trace
    if prr:
        effect = policy.get("geometry_uncertain_coverage", _PRR)
        trace["effect"] = effect
        return effect, trace
    trace["effect"] = None
    return None, trace


def _apply_exceptions(rule: RuleDefinition, inputs: dict) -> tuple[str | None, list, list]:
    """Return (coverage_downgrade_or_None, exceptions_applied, notes)."""
    downgrade: str | None = None
    applied: list = []
    notes: list = []
    for exc in rule.exceptions:
        condition = exc.get("condition")
        holds = True if condition is None else _eval_predicate(condition, inputs)[0]
        if not holds:
            continue
        effect = exc["effect"]
        applied.append({"id": exc["id"], "effect": effect, "description": exc["description"]})
        notes.append(f"exception {exc['id']}: {exc['description']}")
        if effect == "professional_review_required":
            downgrade = cov.most_severe(downgrade or cov.COVERAGE_VERIFIED, _PRR)
        elif effect == "conditional_alternative":
            downgrade = cov.most_severe(
                downgrade or cov.COVERAGE_VERIFIED, cov.COVERAGE_CONDITIONAL
            )
        # documented_limitation: recorded as a note only; no coverage change.
    return downgrade, applied, notes


# --------------------------------------------------------------------------
# Citations with provenance
# --------------------------------------------------------------------------

def _citations_with_provenance(rule: RuleDefinition, snapshots: SnapshotStore) -> list:
    out = []
    for c in rule.citations:
        snap = snapshots.get(c.snapshot_id)
        out.append(
            {
                "snapshot_id": c.snapshot_id,
                "section": c.section,
                "quote": c.quote,
                "last_amended": c.last_amended,
                "provenance": snap.provenance(),
            }
        )
    return out


# --------------------------------------------------------------------------
# M4-T003: fail-closed input validation (fix 1)
# --------------------------------------------------------------------------

def _is_finite_number(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:  # int too big to convert to float (e.g. 10**400)
        return False


def _json_safe(value: Any) -> Any:
    """Non-finite floats are not valid strict JSON; represent them as strings so
    a fail-closed trace (which records the offending input) stays serializable.
    Recurse into lists/tuples/dicts so a non-finite value nested in a container
    (e.g. ``[float('inf')]``) is stringified too, keeping the whole trace
    ``json.dumps(..., allow_nan=False)``-safe."""
    if isinstance(value, float) and not math.isfinite(value):
        return repr(value)
    if isinstance(value, list | tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    return value


def _json_safe_inputs(inputs: dict) -> dict:
    return {name: _json_safe(value) for name, value in inputs.items()}


def _invalid_reason(spec, value: Any) -> str | None:
    """Return why a SUPPLIED (non-None) input value is invalid, or None if valid.
    Fail-closed: a value that is the wrong type, non-finite, out of the declared
    numeric domain, or not in the declared enum is rejected before computation so
    the engine never turns a bad input into a fabricated (e.g. negative) result."""
    kind = spec.type
    if kind in ("number", "integer"):
        if isinstance(value, bool) or not isinstance(value, int | float):
            return f"expected numeric {kind}, got {type(value).__name__}"
        try:
            number = float(value)
        except OverflowError:
            return "numeric value is out of representable range (too large to use)"
        if not math.isfinite(number):
            return "non-finite number (NaN or infinity) is not a usable value"
        if kind == "integer" and not number.is_integer():
            return "expected an integer value"
        if spec.minimum is not None and number < spec.minimum:
            return f"below inclusive minimum {spec.minimum}"
        if spec.maximum is not None and number > spec.maximum:
            return f"above inclusive maximum {spec.maximum}"
        if spec.exclusive_minimum is not None and number <= spec.exclusive_minimum:
            return f"not greater than exclusive_minimum {spec.exclusive_minimum}"
        if spec.exclusive_maximum is not None and number >= spec.exclusive_maximum:
            return f"not less than exclusive_maximum {spec.exclusive_maximum}"
    elif kind == "boolean":
        if not isinstance(value, bool):
            return f"expected boolean, got {type(value).__name__}"
    elif kind == "string":
        if not isinstance(value, str):
            return f"expected string, got {type(value).__name__}"
    if spec.enum is not None and value not in spec.enum:
        return f"value {value!r} is not in the declared enum {list(spec.enum)}"
    return None


def _validate_inputs(rule: RuleDefinition, inputs: dict) -> tuple[list[str], list[dict]]:
    """Return (missing_required, invalid_inputs). A required input that is None is
    missing; any supplied input that fails :func:`_invalid_reason` is invalid."""
    missing_required: list[str] = []
    invalid_inputs: list[dict] = []
    for spec in rule.inputs:
        value = inputs.get(spec.name)
        if value is None:
            if spec.required:
                missing_required.append(spec.name)
            continue
        reason = _invalid_reason(spec, value)
        if reason is not None:
            invalid_inputs.append(
                {"name": spec.name, "reason": reason, "value_seen": _json_safe(value)}
            )
    return missing_required, invalid_inputs


# --------------------------------------------------------------------------
# M4-T003: release status (fix 3) + temporal effectiveness (fix 4)
# --------------------------------------------------------------------------

def _rule_release(rule: RuleDefinition, *, verified_eligible: bool) -> dict:
    release = rule.release or {}
    return {
        "lifecycle_status": rule.status,
        "deterministic_tests": release.get("deterministic_tests", "none"),
        "independent_review": release.get("independent_review", "pending"),
        "qualified_human_approval": release.get("qualified_human_approval", "pending"),
        "verified_eligible": bool(verified_eligible),
    }


_ISO_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")


def _valid_iso_date(value: Any) -> bool:
    """True only for a syntactically valid ISO ``YYYY-MM-DD`` calendar date. A
    non-string or a malformed/out-of-range value is rejected so temporal gating
    fails closed instead of doing a misleading lexical string comparison."""
    if not isinstance(value, str):
        return False
    match = _ISO_DATE_RE.match(value)
    if not match:
        return False
    _, month, day = (int(part) for part in match.groups())
    return 1 <= month <= 12 and 1 <= day <= 31


def _effective_window(rule: RuleDefinition, as_of_date: str | None) -> dict:
    return {
        "effective_from": rule.effective_from,
        "effective_to": rule.effective_to,
        "evaluated_as_of": as_of_date,
        "in_effect": rule.is_in_effect(as_of_date),
    }


# --------------------------------------------------------------------------
# M4-T003: compliance determination (fix 5)
# --------------------------------------------------------------------------

_COMPARATORS = {
    "lt": lambda a, b: a < b,
    "le": lambda a, b: a <= b,
    "gt": lambda a, b: a > b,
    "ge": lambda a, b: a >= b,
    "eq": lambda a, b: a == b,
    "ne": lambda a, b: a != b,
}


def _resolve_determination_ref(ref: dict, inputs: dict, outputs: dict) -> Any:
    if "const" in ref:
        return ref["const"]
    if "input" in ref:
        return inputs.get(ref["input"])
    if "output" in ref:
        return outputs.get(ref["output"])
    return None


def _evaluate_determination(rule: RuleDefinition, inputs: dict, outputs: dict) -> dict | None:
    """Evaluate a compliance determination (proposal vs computed limit) into a
    genuine pass/fail, WITHOUT changing coverage. Returns None when the rule has
    no determination or an operand is not a finite number (indeterminate)."""
    spec = rule.determination
    if not spec:
        return None
    left = _resolve_determination_ref(spec["left"], inputs, outputs)
    right = _resolve_determination_ref(spec["right"], inputs, outputs)
    if not _is_finite_number(left) or not _is_finite_number(right):
        return None
    passed = _COMPARATORS[spec["compare"]](float(left), float(right))
    return {
        "id": spec["id"],
        "description": spec.get("description", ""),
        "compare": spec["compare"],
        "left_value": float(left),
        "right_value": float(right),
        "outcome": "pass" if passed else "fail",
        "label": spec["pass_label"] if passed else spec["fail_label"],
    }


# --------------------------------------------------------------------------
# Top-level evaluate
# --------------------------------------------------------------------------

def evaluate(
    rule: RuleDefinition,
    inputs: dict,
    snapshots: SnapshotStore,
    *,
    spatial_context: dict | None = None,
    g6_approval: lifecycle.G6Approval | None = None,
    as_of_date: str | None = None,
) -> RuleResult:
    citations = _citations_with_provenance(rule, snapshots)
    verified_eligible = rule.status == lifecycle.STATUS_PUBLISHED and _approval_matches(
        rule, g6_approval
    )
    rule_release = _rule_release(rule, verified_eligible=verified_eligible)
    as_of_invalid = as_of_date is not None and not _valid_iso_date(as_of_date)
    if as_of_invalid:
        effective_window = {
            "effective_from": rule.effective_from,
            "effective_to": rule.effective_to,
            "evaluated_as_of": _json_safe(as_of_date),
            "in_effect": False,
        }
    else:
        effective_window = _effective_window(rule, as_of_date)
    evaluated_inputs = _json_safe_inputs(inputs)
    base_notes: list = []

    def _make_trace(**overrides) -> EvaluationTrace:
        fields = {
            "rule_id": rule.rule_id,
            "rule_version": rule.rule_version,
            "rule_status": rule.status,
            "family": rule.family,
            "evaluated_inputs": evaluated_inputs,
            "citations": citations,
            "uncertainty": {"propagated": False},
            "exceptions_applied": [],
            "computation_steps": [],
            "outputs": {},
            "applicability_trace": [],
            "input_validation": {"valid": True, "invalid_inputs": []},
            "rule_release": rule_release,
            "effective_window": effective_window,
            "determination": None,
        }
        fields.update(overrides)
        return EvaluationTrace(**fields)

    # 0a. Invalid as_of_date fails closed (M4-T003 rework): a non-string or a
    #     non-ISO/out-of-range date cannot be temporally reasoned about; do NOT
    #     do a misleading lexical compare (fail OPEN). No computation, no value.
    if as_of_invalid:
        appl_trace = {"invalid_as_of_date": True, "value_seen": _json_safe(as_of_date)}
        return RuleResult(_make_trace(
            applicability_outcome=False,
            applicability_trace=[appl_trace],
            coverage_status=cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
            data_completeness=cov.COMPLETENESS_COMPLETE,
            notes=base_notes + ["as_of_date is not a valid ISO (YYYY-MM-DD) calendar date; "
                                "temporal effectiveness cannot be determined (fail-closed)"],
        ))

    # 0. Temporal gating (fix 4): a rule not in effect as of the supplied date does
    #    not apply - no computation, no value, a visible reason (never silent).
    if not effective_window["in_effect"]:
        return RuleResult(
            _make_trace(
                applicability_outcome=False,
                applicability_trace=[
                    {"not_effective": True, "evaluated_as_of": as_of_date}
                ],
                coverage_status=cov.COVERAGE_NOT_APPLICABLE,
                data_completeness=cov.COMPLETENESS_COMPLETE,
                notes=base_notes
                + [
                    f"rule {rule.rule_id} is not effective as of {as_of_date} "
                    f"(effective {rule.effective_from}..{rule.effective_to})"
                ],
            )
        )

    # 1. Fail-closed input validation (fix 1): a missing required input, or ANY
    #    supplied input that is the wrong type / non-finite / out of declared
    #    domain / not in the declared enum, stops the evaluation before any
    #    computation. No fabricated value (never a negative/NaN/inf result).
    missing_required, invalid_inputs = _validate_inputs(rule, inputs)
    optional_missing = [
        spec.name for spec in rule.inputs if not spec.required and inputs.get(spec.name) is None
    ]

    if missing_required or invalid_inputs:
        blocking = set(missing_required) | {iv["name"] for iv in invalid_inputs}
        appl_inputs = _predicate_input_names(rule.applicability)
        if appl_inputs & blocking:
            appl_outcome = False
            appl_trace = {
                "indeterminate": True,
                "reason": "applicability input missing or invalid",
            }
            base_notes.append("applicability indeterminate: applicability input(s) missing/invalid")
        else:
            appl_outcome, appl_trace = _eval_predicate(rule.applicability, inputs)
        required_broken = blocking & set(rule.required_inputs())
        completeness = (
            cov.COMPLETENESS_MISSING_CRITICAL
            if required_broken
            else cov.COMPLETENESS_MISSING_NONCRITICAL
        )
        note_bits = []
        if missing_required:
            note_bits.append(f"missing required input(s): {sorted(missing_required)}")
        if invalid_inputs:
            note_bits.append(
                "invalid input(s): "
                + ", ".join(f"{iv['name']} ({iv['reason']})" for iv in invalid_inputs)
            )
        return RuleResult(
            _make_trace(
                applicability_outcome=appl_outcome,
                applicability_trace=[appl_trace],
                coverage_status=cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
                data_completeness=completeness,
                input_validation={"valid": not invalid_inputs, "invalid_inputs": invalid_inputs},
                notes=base_notes + [f"{'; '.join(note_bits)}; no value computed (fail-closed)"],
            )
        )

    # 2. Applicability.
    appl_outcome, appl_trace = _eval_predicate(rule.applicability, inputs)
    if not appl_outcome:
        completeness = (
            cov.COMPLETENESS_MISSING_NONCRITICAL if optional_missing else cov.COMPLETENESS_COMPLETE
        )
        return RuleResult(
            _make_trace(
                applicability_outcome=False,
                applicability_trace=[appl_trace],
                coverage_status=cov.COVERAGE_NOT_APPLICABLE,
                data_completeness=completeness,
                notes=base_notes + ["rule not applicable to the supplied inputs"],
            )
        )

    # 3. Deterministic computation.
    step_traces, outputs = _run_computation(rule, inputs)

    # 3a. Output finiteness guard (M4-T003 rework, D1): even with in-domain inputs
    #     a computation can overflow to a non-finite result (e.g. a huge finite
    #     lot_area multiplied by a FAR). Never emit a fabricated inf/NaN output;
    #     fail closed to professional review with a visible reason.
    nonfinite_steps = [s["step_id"] for s in step_traces if not _is_finite_number(s["result"])]
    if nonfinite_steps:
        return RuleResult(_make_trace(
            applicability_outcome=True,
            applicability_trace=[appl_trace],
            coverage_status=cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
            data_completeness=cov.COMPLETENESS_COMPLETE,
            notes=base_notes + [
                f"computation produced a non-finite result in step(s) {nonfinite_steps} "
                "(numeric overflow); no value emitted (fail-closed)"
            ],
        ))

    # 4. Base coverage for a draft rule is conditional; verified is only for a
    #    published rule with a matching G6 approval attached.
    base_coverage = cov.COVERAGE_VERIFIED if verified_eligible else cov.COVERAGE_CONDITIONAL

    # 5. Exceptions + geometric uncertainty downgrade coverage (never upgrade).
    exc_downgrade, exceptions_applied, exc_notes = _apply_exceptions(rule, inputs)
    geom_downgrade, uncertainty_trace = _uncertainty_effect(rule, spatial_context)
    coverage_status = cov.most_severe(base_coverage, exc_downgrade, geom_downgrade)

    completeness = (
        cov.COMPLETENESS_MISSING_NONCRITICAL if optional_missing else cov.COMPLETENESS_COMPLETE
    )
    notes = list(base_notes) + exc_notes
    if optional_missing:
        notes.append(f"optional input(s) not supplied: {sorted(optional_missing)}")
    for limitation in rule.limitations:
        notes.append(f"limitation: {limitation}")

    # 6. Compliance determination (fix 5): a genuine pass/fail against a computed
    #    limit, recorded in the trace WITHOUT changing coverage.
    determination = _evaluate_determination(rule, inputs, outputs)

    return RuleResult(
        _make_trace(
            applicability_outcome=True,
            applicability_trace=[appl_trace],
            computation_steps=step_traces,
            outputs=outputs,
            coverage_status=coverage_status,
            data_completeness=completeness,
            uncertainty=uncertainty_trace,
            exceptions_applied=exceptions_applied,
            notes=notes,
            determination=determination,
        )
    )


def _approval_matches(rule: RuleDefinition, approval: lifecycle.G6Approval | None) -> bool:
    return (
        approval is not None
        and approval.rule_id == rule.rule_id
        and approval.rule_version == rule.rule_version
    )
