"""Focused tests for the Draft-7 provider-schema projection (M0-T141; D-024-R666..R671).

Guarded live failure (preserved evidence:
project-control/reports/M0-T141-canary-b502-schema-failure-evidence.md): Claude Code
2.1.252 exited 1 BEFORE provider contact on the canonical WorkerResult schema because
its serialized --json-schema argument declared the Draft 2020-12 dialect. These tests
prove, offline:

* the canonical in-memory schema is never mutated and the schema file stays 2020-12
  internally (R666/R670);
* the provider copy declares Draft 7 explicitly and carries the canonical body
  otherwise unchanged (R667/R668);
* the serialized CLI argument contains no Draft 2020-12 declaration (R671);
* every unknown / newer-draft-only / draft-divergent keyword refuses instead of being
  silently translated (R669);
* serializing the schema the way the removed guard did reproduces the exact URI the
  CLI's recorded stderr refused - the same error would return with the guard removed
  (R671/R672).
"""
from __future__ import annotations

import copy
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.agent_supervisor.mrl_provider_schema import (  # noqa: E402
    CANONICAL_DECLARATION,
    DRAFT7_DECLARATION,
    provider_schema_for_claude_cli,
)
from tools.agent_supervisor.mrl_worker_result import ContractError, load_schema  # noqa: E402

#: Verbatim stderr of the failed live run (canary-b5-02 one_shot_unit.json,
#: checkpoint_error field; controller audit record 25).
RECORDED_STDERR = ('Error: --json-schema is not a valid JSON Schema: no schema with '
                   'key or ref "https://json-schema.org/draft/2020-12/schema"')


def canonical() -> dict:
    return load_schema("worker_result.schema.json")


# ---------------------------------------------------------------- R666/R670: canonical untouched

def test_canonical_schema_file_still_declares_2020_12_internally():
    # The internal contract deliberately stays on the canonical dialect; only the
    # CLI-boundary copy is projected (R666).
    assert canonical()["$schema"] == CANONICAL_DECLARATION


def test_canonical_in_memory_schema_is_never_mutated():
    loaded = canonical()
    snapshot = copy.deepcopy(loaded)
    projected = provider_schema_for_claude_cli(loaded)
    assert loaded == snapshot, "projection mutated the canonical in-memory schema (R670)"
    # deep-copy proof: writing into the projection cannot reach the canonical graph
    projected["properties"]["outcome"]["enum"].append("FORGED")
    projected["title"] = "tampered"
    projected["required"].append("forged_field")
    assert loaded == snapshot
    assert canonical() == snapshot


# ---------------------------------------------------------------- R667/R668: the provider copy

def test_provider_copy_declares_draft7_and_preserves_the_body():
    projected = provider_schema_for_claude_cli(canonical())
    assert projected["$schema"] == DRAFT7_DECLARATION
    body = {k: v for k, v in projected.items() if k != "$schema"}
    expected = {k: v for k, v in canonical().items() if k != "$schema"}
    assert body == expected, "the projection may change ONLY the top-level declaration"


def test_missing_declaration_projects_to_explicit_draft7():
    undeclared = {k: v for k, v in canonical().items() if k != "$schema"}
    assert provider_schema_for_claude_cli(undeclared)["$schema"] == DRAFT7_DECLARATION


def test_already_draft7_declaration_is_preserved():
    redeclared = dict(canonical())
    redeclared["$schema"] = DRAFT7_DECLARATION
    assert provider_schema_for_claude_cli(redeclared)["$schema"] == DRAFT7_DECLARATION


# ---------------------------------------------------------------- R671: the serialized argument

def test_serialized_cli_argument_contains_no_2020_12_declaration():
    # The exact expression the runner serializes into --json-schema.
    argument = json.dumps(provider_schema_for_claude_cli(
        load_schema("worker_result.schema.json")), sort_keys=True)
    assert "json-schema.org/draft/2020-12" not in argument
    assert DRAFT7_DECLARATION in argument
    assert json.loads(argument)["$schema"] == DRAFT7_DECLARATION


def test_guard_removed_would_reproduce_the_exact_recorded_failure():
    # The pre-fix expression, verbatim (mrl_one_shot.py before M0-T141): serializing
    # the canonical schema directly. The URI it emits is byte-equal to the one the
    # CLI's recorded stderr refused, so removing the projection returns the same
    # error (R671); the preserved run shows provider-contact count zero (R672).
    legacy_argument = json.dumps(load_schema("worker_result.schema.json"), sort_keys=True)
    refused_uri = RECORDED_STDERR.split('"')[1]
    assert refused_uri == CANONICAL_DECLARATION
    assert f'"{refused_uri}"' in legacy_argument
    fixed_argument = json.dumps(provider_schema_for_claude_cli(
        load_schema("worker_result.schema.json")), sort_keys=True)
    assert refused_uri not in fixed_argument


# ---------------------------------------------------------------- R669: fail-closed keyword walk

def _with_top_level(**extra):
    mutated = dict(canonical())
    mutated.update(extra)
    return mutated


@pytest.mark.parametrize("label, schema", [
    ("newer_defs", _with_top_level(**{"$defs": {"x": {"type": "string"}}})),
    ("newer_prefix_items", _with_top_level(prefixItems=[{"type": "string"}])),
    ("newer_unevaluated_properties", _with_top_level(unevaluatedProperties=False)),
    ("newer_dependent_required", _with_top_level(dependentRequired={"summary": ["outcome"]})),
    ("newer_min_contains", _with_top_level(minContains=1)),
    ("newer_deprecated", _with_top_level(deprecated=True)),
    ("divergent_ref", _with_top_level(**{"$ref": "#/definitions/x"})),
    ("divergent_definitions", _with_top_level(definitions={})),
    ("divergent_dependencies", _with_top_level(dependencies={})),
    ("unknown_vendor_keyword", _with_top_level(**{"x-vendor": True})),
    ("nested_unknown_keyword", {
        "$schema": CANONICAL_DECLARATION, "type": "object",
        "properties": {"outcome": {"type": "string", "unevaluatedItems": False}}}),
    ("nested_schema_declaration", {
        "$schema": CANONICAL_DECLARATION, "type": "object",
        "properties": {"outcome": {"$schema": CANONICAL_DECLARATION, "type": "string"}}}),
    ("array_form_items", {
        "$schema": CANONICAL_DECLARATION, "type": "array",
        "items": [{"type": "string"}, {"type": "integer"}]}),
    ("unrecognized_dialect", _with_top_level(**{"$schema": "http://json-schema.org/draft-04/schema#"})),
    ("non_object_schema", ["not", "a", "schema"]),
])
def test_incompatible_input_refuses_instead_of_translating(label, schema):
    with pytest.raises(ContractError) as exc:
        provider_schema_for_claude_cli(schema)
    assert exc.value.code == "draft7_schema_incompatible", label


def test_refusal_does_not_mutate_the_offending_input():
    mutated = _with_top_level(**{"$defs": {"x": {"type": "string"}}})
    snapshot = copy.deepcopy(mutated)
    with pytest.raises(ContractError):
        provider_schema_for_claude_cli(mutated)
    assert mutated == snapshot


# ---------------------------------------------------------------- the walk recurses everywhere

@pytest.mark.parametrize("where, schema", [
    ("allOf", {"$schema": CANONICAL_DECLARATION, "allOf": [{"prefixItems": []}]}),
    ("if", {"$schema": CANONICAL_DECLARATION, "if": {"$ref": "#/x"}, "then": {"type": "object"}}),
    ("additionalProperties", {"$schema": CANONICAL_DECLARATION, "type": "object",
                              "additionalProperties": {"$defs": {}}}),
    ("items", {"$schema": CANONICAL_DECLARATION, "type": "array",
               "items": {"dependentSchemas": {}}}),
    ("patternProperties", {"$schema": CANONICAL_DECLARATION, "type": "object",
                           "patternProperties": {"^x": {"minContains": 2}}}),
])
def test_nested_positions_are_walked(where, schema):
    with pytest.raises(ContractError) as exc:
        provider_schema_for_claude_cli(schema)
    assert exc.value.code == "draft7_schema_incompatible", where


def test_compatible_nested_constructs_project_cleanly():
    schema = {
        "$schema": CANONICAL_DECLARATION, "type": "object", "additionalProperties": False,
        "required": ["rows"], "properties": {
            "rows": {"type": "array", "minItems": 1, "uniqueItems": True,
                     "items": {"type": "string", "minLength": 1, "maxLength": 64}},
            "kind": {"type": "string", "enum": ["a", "b"]},
        },
    }
    projected = provider_schema_for_claude_cli(schema)
    assert projected["$schema"] == DRAFT7_DECLARATION
    assert projected["properties"] == schema["properties"]
    assert projected["properties"] is not schema["properties"]
