"""Typed models for rule definitions, evaluation traces, and rule results.

A ``RuleDefinition`` is a thin, validated view over the JSON DSL document (parsed
and schema-checked in ``dsl.py``); the evaluator reads it structurally. An
``EvaluationTrace`` is the full, exportable record of one evaluation: resolved
inputs, the applicability decision with per-predicate reasoning, every
computation step with its resolved arguments and result, the citations with
their source-snapshot provenance, the coverage/completeness labels, and any
propagated geometric uncertainty. ``RuleResult`` wraps the trace and enforces
the export invariant: no material value leaves without resolvable provenance
(PRD section 19).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class InputSpec:
    name: str
    type: str
    required: bool
    unit: str | None = None
    enum: tuple[str, ...] | None = None
    description: str = ""
    # M4-T003 fail-closed domain constraints (all optional; numeric inputs only).
    minimum: float | None = None
    maximum: float | None = None
    exclusive_minimum: float | None = None
    exclusive_maximum: float | None = None


@dataclass(frozen=True)
class OutputSpec:
    name: str
    type: str
    unit: str | None = None
    description: str = ""


@dataclass(frozen=True)
class Citation:
    snapshot_id: str
    section: str
    quote: str
    last_amended: str | None = None


@dataclass(frozen=True)
class RuleDefinition:
    """Validated view over one rules-DSL document. Field-level meaning lives in
    services/api/app/rules/schemas/v1/rule_definition.schema.json."""

    rule_id: str
    rule_version: str
    family: str
    title: str
    jurisdiction: str
    status: str
    description: str
    citations: tuple[Citation, ...]
    inputs: tuple[InputSpec, ...]
    outputs: tuple[OutputSpec, ...]
    parameters: dict[str, Any]
    parameter_citations: dict[str, str]
    applicability: dict
    computation: dict
    exceptions: tuple[dict, ...]
    special_district_interactions: tuple[dict, ...]
    uncertainty_policy: dict
    limitations: tuple[str, ...]
    raw: dict
    # M4-T003 additive fields (temporal versioning, release status, compliance).
    effective_from: str | None = None
    effective_to: str | None = None
    release: dict = field(default_factory=dict)
    determination: dict | None = None

    def input_map(self) -> dict[str, InputSpec]:
        return {spec.name: spec for spec in self.inputs}

    def required_inputs(self) -> tuple[str, ...]:
        return tuple(spec.name for spec in self.inputs if spec.required)

    def output_names(self) -> tuple[str, ...]:
        return tuple(self.computation.get("outputs", {}).keys())

    def is_in_effect(self, as_of_date: str | None) -> bool:
        """True when no ``as_of_date`` is supplied (no temporal gating) or the ISO
        date falls in the half-open window ``[effective_from, effective_to)``."""
        if as_of_date is None:
            return True
        if self.effective_from is not None and as_of_date < self.effective_from:
            return False
        if self.effective_to is not None and as_of_date >= self.effective_to:
            return False
        return True


@dataclass
class ComputationStep:
    step_id: str
    op: str
    resolved_args: list[Any]
    result: float
    note: str = ""

    def as_dict(self) -> dict:
        return {
            "step_id": self.step_id,
            "op": self.op,
            "resolved_args": list(self.resolved_args),
            "result": self.result,
            "note": self.note,
        }


@dataclass
class PredicateTrace:
    op: str
    input_name: str | None
    detail: dict
    outcome: bool

    def as_dict(self) -> dict:
        return {
            "op": self.op,
            "input_name": self.input_name,
            "detail": dict(self.detail),
            "outcome": self.outcome,
        }


@dataclass
class EvaluationTrace:
    rule_id: str
    rule_version: str
    rule_status: str
    family: str
    evaluated_inputs: dict
    applicability_outcome: bool
    applicability_trace: list  # list[PredicateTrace-as-dict]
    computation_steps: list  # list[ComputationStep-as-dict]
    outputs: dict
    coverage_status: str
    data_completeness: str
    citations: list  # list[dict] with embedded snapshot provenance
    uncertainty: dict
    exceptions_applied: list
    notes: list = field(default_factory=list)
    # M4-T003 additive trace sections (always emitted).
    input_validation: dict = field(default_factory=lambda: {"valid": True, "invalid_inputs": []})
    rule_release: dict = field(default_factory=dict)
    effective_window: dict = field(default_factory=dict)
    determination: dict | None = None

    def as_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "rule_version": self.rule_version,
            "rule_status": self.rule_status,
            "family": self.family,
            "evaluated_inputs": dict(self.evaluated_inputs),
            "applicability_outcome": self.applicability_outcome,
            "applicability_trace": list(self.applicability_trace),
            "computation_steps": list(self.computation_steps),
            "outputs": dict(self.outputs),
            "coverage_status": self.coverage_status,
            "data_completeness": self.data_completeness,
            "citations": list(self.citations),
            "uncertainty": dict(self.uncertainty),
            "exceptions_applied": list(self.exceptions_applied),
            "notes": list(self.notes),
            "input_validation": dict(self.input_validation),
            "rule_release": dict(self.rule_release),
            "effective_window": dict(self.effective_window),
            "determination": dict(self.determination) if self.determination is not None else None,
        }


class ProvenanceError(RuntimeError):
    """Raised when a result would export a value without resolvable provenance."""


@dataclass
class RuleResult:
    """Wraps an evaluation trace. ``export()`` is the ONLY sanctioned way to get
    the machine result, and it fails closed if any citation lacks a resolvable
    source-snapshot provenance block (PRD section 19)."""

    trace: EvaluationTrace

    @property
    def coverage_status(self) -> str:
        return self.trace.coverage_status

    @property
    def outputs(self) -> dict:
        return dict(self.trace.outputs)

    def export(self) -> dict:
        for citation in self.trace.citations:
            prov = citation.get("provenance")
            if not prov or not prov.get("content_digest_sha256"):
                raise ProvenanceError(
                    f"rule {self.trace.rule_id}: citation for snapshot "
                    f"{citation.get('snapshot_id')!r} has no resolvable provenance; "
                    "a material rule value may not be exported without it (PRD s19)."
                )
        return self.trace.as_dict()
