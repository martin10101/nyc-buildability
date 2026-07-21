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
# Top-level evaluate
# --------------------------------------------------------------------------

def evaluate(
    rule: RuleDefinition,
    inputs: dict,
    snapshots: SnapshotStore,
    *,
    spatial_context: dict | None = None,
    g6_approval: lifecycle.G6Approval | None = None,
) -> RuleResult:
    citations = _citations_with_provenance(rule, snapshots)
    base_notes: list = []

    # 1. Missing required inputs -> typed missing-data behaviour, no computation.
    missing_required = [name for name in rule.required_inputs() if inputs.get(name) is None]
    optional_missing = [
        spec.name
        for spec in rule.inputs
        if not spec.required and inputs.get(spec.name) is None
    ]

    if missing_required:
        # Applicability is only shown if all of ITS inputs are present; otherwise
        # it is indeterminate (never silently 'not applicable').
        appl_inputs = _predicate_input_names(rule.applicability)
        if appl_inputs & set(missing_required):
            appl_outcome = False
            appl_trace = {"indeterminate": True, "reason": "required applicability input missing"}
            base_notes.append("applicability indeterminate: required input(s) missing")
        else:
            appl_outcome, appl_trace = _eval_predicate(rule.applicability, inputs)
        trace = EvaluationTrace(
            rule_id=rule.rule_id,
            rule_version=rule.rule_version,
            rule_status=rule.status,
            family=rule.family,
            evaluated_inputs=dict(inputs),
            applicability_outcome=appl_outcome,
            applicability_trace=[appl_trace],
            computation_steps=[],
            outputs={},
            coverage_status=cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
            data_completeness=cov.COMPLETENESS_MISSING_CRITICAL,
            citations=citations,
            uncertainty={"propagated": False},
            exceptions_applied=[],
            notes=base_notes
            + [f"missing required input(s): {sorted(missing_required)}; no value computed"],
        )
        return RuleResult(trace)

    # 2. Applicability.
    appl_outcome, appl_trace = _eval_predicate(rule.applicability, inputs)
    if not appl_outcome:
        completeness = (
            cov.COMPLETENESS_MISSING_NONCRITICAL if optional_missing else cov.COMPLETENESS_COMPLETE
        )
        trace = EvaluationTrace(
            rule_id=rule.rule_id,
            rule_version=rule.rule_version,
            rule_status=rule.status,
            family=rule.family,
            evaluated_inputs=dict(inputs),
            applicability_outcome=False,
            applicability_trace=[appl_trace],
            computation_steps=[],
            outputs={},
            coverage_status=cov.COVERAGE_NOT_APPLICABLE,
            data_completeness=completeness,
            citations=citations,
            uncertainty={"propagated": False},
            exceptions_applied=[],
            notes=base_notes + ["rule not applicable to the supplied inputs"],
        )
        return RuleResult(trace)

    # 3. Deterministic computation.
    step_traces, outputs = _run_computation(rule, inputs)

    # 4. Base coverage for a draft rule is conditional; verified is only for a
    #    published rule with a matching G6 approval attached.
    base_coverage = cov.COVERAGE_CONDITIONAL
    if rule.status == lifecycle.STATUS_PUBLISHED and _approval_matches(rule, g6_approval):
        base_coverage = cov.COVERAGE_VERIFIED

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

    trace = EvaluationTrace(
        rule_id=rule.rule_id,
        rule_version=rule.rule_version,
        rule_status=rule.status,
        family=rule.family,
        evaluated_inputs=dict(inputs),
        applicability_outcome=True,
        applicability_trace=[appl_trace],
        computation_steps=step_traces,
        outputs=outputs,
        coverage_status=coverage_status,
        data_completeness=completeness,
        citations=citations,
        uncertainty=uncertainty_trace,
        exceptions_applied=exceptions_applied,
        notes=notes,
    )
    return RuleResult(trace)


def _approval_matches(rule: RuleDefinition, approval: lifecycle.G6Approval | None) -> bool:
    return (
        approval is not None
        and approval.rule_id == rule.rule_id
        and approval.rule_version == rule.rule_version
    )
