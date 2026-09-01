#!/usr/bin/env python3
"""MRL WorkerResult contract + controller-authoritative ClaudeCheckpoint builder
(M0-T134 / D-024 Amendment 39 R501/R503; C8).

Trust boundary (owner correction E): the Claude worker returns ONLY a minimal,
UNTRUSTED ``WorkerResult`` - an outcome enum, a bounded human summary, and a
bounded requested-next-action, and nothing else. It carries no run/task/session
ids, no SHAs, no branch/origin, no model or executable identity, no gate/test
results and no evidence digests. The controller alone constructs the authoritative
``ClaudeCheckpoint`` from its OWN observed run/task/session/Git facts; the worker's
two text fields are the only model-supplied content, and even the outcome is a
CLAIM, never itself an advancement decision.

The provider payload is validated against ``schemas/worker_result.schema.json``
(``additionalProperties:false``) by a small dependency-free enforcer that reads
the schema file - so a forged factual field, an unknown key, a wrong type, a bad
enum, or an out-of-range length all fail closed. This module adds no third-party
dependency; ``jsonschema`` is deliberately not used (undeclared in the lockfiles;
adding it would need a G5 provenance review).

Import direction: this module imports ``.checkpoint_extraction`` (RunnerError base)
and ``.models`` only; nothing here imports it back, so no cycle can form. Sibling
contract modules reuse ``load_schema``/``validate_instance`` from here.
"""
from __future__ import annotations

import dataclasses
import json
import pathlib
from typing import Any, Mapping

from .checkpoint_extraction import RunnerError
from .models import ClaudeCheckpoint

_SCHEMA_DIR = pathlib.Path(__file__).resolve().parent / "schemas"


class ContractError(RunnerError):
    """A fail-closed MRL data-contract violation.

    Subclasses ``RunnerError`` so a contract breach that reaches the loop is caught
    by cli.py's existing ``except RunnerError`` and is never mistaken for success.
    """


def load_schema(name: str) -> dict[str, Any]:
    """Load one JSON Schema file from the package ``schemas/`` directory.

    utf-8-sig so a BOM-prefixed file (the convention cli.py already reads) loads.
    """
    return json.loads((_SCHEMA_DIR / name).read_text(encoding="utf-8-sig"))


def _fail(where: str, message: str) -> None:
    raise ContractError("contract_violation", f"{where}: {message}")


def validate_instance(instance: Any, schema: Mapping[str, Any], where: str = "instance") -> None:
    """Validate ``instance`` against the supported subset of JSON Schema, fail-closed.

    Supported keywords (exactly what the MRL contract schemas use): object type with
    ``required``/``properties``/``additionalProperties:false``; string type with
    ``enum``/``minLength``/``maxLength``; array type with ``minItems``/``maxItems``/
    ``uniqueItems``/``items``. Any unsupported ``type`` raises rather than silently
    passing, so the enforcer can never quietly ignore a constraint.
    """
    schema_type = schema.get("type")
    if schema_type == "object":
        if not isinstance(instance, dict):
            _fail(where, f"expected object, got {type(instance).__name__}")
        props: Mapping[str, Any] = schema.get("properties", {})
        if schema.get("additionalProperties", True) is False:
            extra = sorted(set(instance) - set(props))
            if extra:
                _fail(where, f"unknown field(s) {extra} not permitted (additionalProperties=false)")
        for required in schema.get("required", []):
            if required not in instance:
                _fail(where, f"missing required field {required!r}")
        for key, subschema in props.items():
            if key in instance:
                validate_instance(instance[key], subschema, f"{where}.{key}")
    elif schema_type == "string":
        # bool is not str, so a JSON true/false or number fails here as intended.
        if not isinstance(instance, str):
            _fail(where, f"expected string, got {type(instance).__name__}")
        if "enum" in schema and instance not in schema["enum"]:
            _fail(where, f"{instance!r} is not one of {schema['enum']}")
        if "minLength" in schema and len(instance) < schema["minLength"]:
            _fail(where, f"length {len(instance)} below minLength {schema['minLength']}")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            _fail(where, f"length {len(instance)} above maxLength {schema['maxLength']}")
    elif schema_type == "array":
        if not isinstance(instance, list):
            _fail(where, f"expected array, got {type(instance).__name__}")
        if "minItems" in schema and len(instance) < schema["minItems"]:
            _fail(where, f"{len(instance)} items below minItems {schema['minItems']}")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            _fail(where, f"{len(instance)} items above maxItems {schema['maxItems']}")
        if schema.get("uniqueItems"):
            seen: list[Any] = []
            for i, element in enumerate(instance):
                if element in seen:
                    _fail(f"{where}[{i}]", "duplicate item not permitted (uniqueItems)")
                seen.append(element)
        item_schema = schema.get("items")
        if item_schema is not None:
            for i, element in enumerate(instance):
                validate_instance(element, item_schema, f"{where}[{i}]")
    else:  # pragma: no cover - guarded by the fixed contract schemas
        _fail(where, f"unsupported schema type {schema_type!r} (enforcer would ignore it)")


@dataclasses.dataclass(frozen=True)
class WorkerResult:
    """The untrusted MRL worker return. Exactly three fields; nothing factual."""

    outcome: str
    summary: str
    requested_next_action: str

    @classmethod
    def from_provider(cls, raw: Any) -> "WorkerResult":
        """Validate a raw provider payload against the schema and build the record.

        Any forged factual field (run_id, sha, branch, model, gate result, ...) is
        an unknown key under additionalProperties=false and is rejected here, so the
        worker can never supply a trusted fact (R503).
        """
        if not isinstance(raw, Mapping):
            _fail("worker_result", f"must be a JSON object, got {type(raw).__name__}")
        validate_instance(dict(raw), load_schema("worker_result.schema.json"), "worker_result")
        return cls(
            outcome=raw["outcome"],
            summary=raw["summary"],
            requested_next_action=raw["requested_next_action"],
        )


#: The worker's self-reported outcome maps to a checkpoint status. It is the
#: worker's CLAIM about its own unit; the actual advancement decision is the
#: controller's (and Codex's) job, never this status. NEEDS_OWNER maps to BLOCKED
#: (owner attention is carried in the summary / next action); a richer owner-
#: decision field is deferred to the tranche that wires the live loop.
_OUTCOME_TO_STATUS = {
    "COMPLETED": "UNIT_COMPLETE",
    "BLOCKED": "BLOCKED",
    "NEEDS_OWNER": "BLOCKED",
}


@dataclasses.dataclass(frozen=True)
class ControllerObservedFacts:
    """The checkpoint's factual/provenance fields, observed by the CONTROLLER.

    Every value here comes from the controller's own view of the run, the task
    packet, the session, and live Git - never from the worker's output.
    """

    run_id: str
    checkpoint_id: str
    task_id: str
    claude_session_id: str
    starting_sha: str
    current_sha: str
    branch: str
    worktree: str
    schema_version: str = "1.0.0"


def build_claude_checkpoint(
    worker_result: WorkerResult, facts: ControllerObservedFacts
) -> ClaudeCheckpoint:
    """Construct the authoritative ClaudeCheckpoint from controller-observed facts.

    Only ``summary`` and ``proposed_next_action`` (both untrusted text) come from the
    worker; ``status`` is a fixed map of the worker's outcome claim; every id, SHA,
    branch and worktree comes from ``facts``. The result is ``.validate()``-checked
    before return, so a malformed controller-side value also fails closed.
    """
    payload = {
        "schema_version": facts.schema_version,
        "run_id": facts.run_id,
        "checkpoint_id": facts.checkpoint_id,
        "task_id": facts.task_id,
        "claude_session_id": facts.claude_session_id,
        "status": _OUTCOME_TO_STATUS[worker_result.outcome],
        "summary": worker_result.summary,
        "starting_sha": facts.starting_sha,
        "current_sha": facts.current_sha,
        "branch": facts.branch,
        "worktree": facts.worktree,
        "proposed_next_action": worker_result.requested_next_action or "(worker proposed none)",
    }
    # Controller-side guard that the factual envelope was actually populated with
    # well-formed values (in addition to ClaudeCheckpoint.validate()).
    validate_instance(payload, load_schema("mrl_claude_checkpoint.schema.json"), "claude_checkpoint")
    checkpoint = ClaudeCheckpoint.from_dict(payload)
    checkpoint.validate()
    return checkpoint
