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

    def input_map(self) -> dict[str, InputSpec]:
        return {spec.name: spec for spec in self.inputs}

    def required_inputs(self) -> tuple[str, ...]:
        return tuple(spec.name for spec in self.inputs if spec.required)


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
