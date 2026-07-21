"""Load + validate a rules-DSL document into a RuleDefinition.

Validation layers, all fail-closed:

1. JSON Schema (services/api/app/rules/schemas/v1/rule_definition.schema.json)
   via jsonschema (a runtime dependency of services/api).
2. Lifecycle guard: an authored rule may not declare a status beyond
   ``needs_review`` (owner directive item 5 - no AI-published/Verified rule).
3. Referential integrity: every citation ``snapshot_id`` and every parameter
   ``citation_ref`` resolves in the snapshot store; every computation ``ref``
   points at a declared input / parameter / earlier step; every declared output
   maps to an existing step; parameter maps used by ``param_select`` are objects.

A rule that fails any layer never becomes a RuleDefinition - the engine cannot
evaluate an unvalidated rule.
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path

import jsonschema

from . import lifecycle
from .models import Citation, InputSpec, OutputSpec, RuleDefinition
from .snapshots import SnapshotStore

_SCHEMA_DIR = Path(__file__).resolve().parent / "schemas" / "v1"
RULE_DEFINITION_SCHEMA_PATH = _SCHEMA_DIR / "rule_definition.schema.json"
EVALUATION_TRACE_SCHEMA_PATH = _SCHEMA_DIR / "evaluation_trace.schema.json"


class DSLError(RuntimeError):
    """Raised when a rule document is invalid at any validation layer."""


@cache
def _load_schema(path_str: str) -> dict:
    return json.loads(Path(path_str).read_text(encoding="utf-8"))


def rule_definition_schema() -> dict:
    return _load_schema(str(RULE_DEFINITION_SCHEMA_PATH))


def evaluation_trace_schema() -> dict:
    return _load_schema(str(EVALUATION_TRACE_SCHEMA_PATH))


def _schema_validate(document: dict) -> None:
    validator = jsonschema.Draft202012Validator(rule_definition_schema())
    errors = sorted(validator.iter_errors(document), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        loc = "/".join(str(p) for p in first.path) or "<root>"
        raise DSLError(f"rule schema violation at {loc}: {first.message}")


def _check_refs(document: dict, snapshots: SnapshotStore) -> None:
    rule_id = document.get("rule_id", "<unknown>")

    # citation snapshots resolve
    for citation in document["citations"]:
        snapshots.get(citation["snapshot_id"])  # raises SnapshotError if missing

    # parameter citation_refs resolve; index parameters by name
    params = {}
    for param in document["parameters"]:
        snapshots.get(param["citation_ref"])
        params[param["name"]] = param["value"]

    inputs = {spec["name"] for spec in document["inputs"]}

    # computation refs point at declared inputs / params / earlier steps
    seen_steps: set[str] = set()
    for step in document["computation"]["steps"]:
        for arg in step["args"]:
            _check_ref(rule_id, arg, inputs, params, seen_steps)
        seen_steps.add(step["id"])

    for out_name, target in document["computation"]["outputs"].items():
        if target["step"] not in seen_steps:
            raise DSLError(
                f"rule {rule_id}: output {out_name!r} references unknown step "
                f"{target['step']!r}"
            )

    # exception / special-district citation_refs (when present) resolve
    for exc in document.get("exceptions", []):
        ref = exc.get("citation_ref")
        if ref:
            snapshots.get(ref)
    for sdi in document.get("special_district_interactions", []):
        ref = sdi.get("citation_ref")
        if ref:
            snapshots.get(ref)


def _check_ref(rule_id, arg, inputs, params, seen_steps) -> None:
    keys = set(arg)
    if keys == {"const"}:
        return
    if keys == {"input"}:
        if arg["input"] not in inputs:
            raise DSLError(f"rule {rule_id}: ref input {arg['input']!r} is not a declared input")
        return
    if keys == {"param"}:
        pval = params.get(arg["param"], KeyError)
        if pval is KeyError:
            raise DSLError(
                f"rule {rule_id}: ref param {arg['param']!r} is not a declared parameter"
            )
        if not isinstance(pval, int | float) or isinstance(pval, bool):
            raise DSLError(
                f"rule {rule_id}: param {arg['param']!r} used as scalar but is not numeric"
            )
        return
    if keys == {"param_select"}:
        sel = arg["param_select"]
        pname = sel["map"]
        if pname not in params:
            raise DSLError(
                f"rule {rule_id}: param_select map {pname!r} is not a declared parameter"
            )
        if not isinstance(params[pname], dict):
            raise DSLError(
                f"rule {rule_id}: param_select map {pname!r} must be an object parameter"
            )
        if sel["key_input"] not in inputs:
            raise DSLError(
                f"rule {rule_id}: param_select key_input {sel['key_input']!r} "
                "is not a declared input"
            )
        return
    if keys == {"step"}:
        if arg["step"] not in seen_steps:
            raise DSLError(
                f"rule {rule_id}: ref step {arg['step']!r} is not an EARLIER step "
                "(forward/self references are not allowed)"
            )
        return
    raise DSLError(f"rule {rule_id}: malformed ref {arg!r} (exactly one ref key required)")


def build_rule_definition(document: dict, snapshots: SnapshotStore) -> RuleDefinition:
    _schema_validate(document)
    lifecycle.assert_agent_authorable(document["status"])
    _check_refs(document, snapshots)

    citations = tuple(
        Citation(
            snapshot_id=c["snapshot_id"],
            section=c["section"],
            quote=c["quote"],
            last_amended=c.get("last_amended"),
        )
        for c in document["citations"]
    )
    inputs = tuple(
        InputSpec(
            name=i["name"],
            type=i["type"],
            required=i["required"],
            unit=i.get("unit"),
            enum=tuple(i["enum"]) if i.get("enum") else None,
            description=i.get("description", ""),
        )
        for i in document["inputs"]
    )
    outputs = tuple(
        OutputSpec(
            name=o["name"], type=o["type"], unit=o.get("unit"),
            description=o.get("description", ""),
        )
        for o in document["outputs"]
    )
    parameters = {p["name"]: p["value"] for p in document["parameters"]}
    parameter_citations = {p["name"]: p["citation_ref"] for p in document["parameters"]}

    return RuleDefinition(
        rule_id=document["rule_id"],
        rule_version=document["rule_version"],
        family=document["family"],
        title=document["title"],
        jurisdiction=document["jurisdiction"],
        status=document["status"],
        description=document["description"],
        citations=citations,
        inputs=inputs,
        outputs=outputs,
        parameters=parameters,
        parameter_citations=parameter_citations,
        applicability=document["applicability"],
        computation=document["computation"],
        exceptions=tuple(document.get("exceptions", [])),
        special_district_interactions=tuple(document.get("special_district_interactions", [])),
        uncertainty_policy=document.get("uncertainty_policy", {}),
        limitations=tuple(document.get("limitations", [])),
        raw=document,
    )


def load_rule_file(path: Path, snapshots: SnapshotStore) -> RuleDefinition:
    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DSLError(f"rule file {path} is unreadable: {exc}") from exc
    return build_rule_definition(document, snapshots)
