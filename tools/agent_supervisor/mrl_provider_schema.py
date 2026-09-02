#!/usr/bin/env python3
"""Draft-7 provider-schema projection at the Claude CLI boundary (M0-T141;
D-024 Amendment 44 R666-R671).

Reproduced live defect (canary-b5-02, 2026-09-02, controller audit records 22-26):
Claude Code 2.1.252 validates ``--json-schema`` with a Draft-7 validator and the
child exits 1 BEFORE provider contact when the schema declares
``"$schema": "https://json-schema.org/draft/2020-12/schema"`` -
``Error: --json-schema is not a valid JSON Schema: no schema with key or ref
"https://json-schema.org/draft/2020-12/schema"``. Anthropic's structured-output
documentation requires Draft 7, and anthropics/claude-code issue #80402 reproduces
the same error (Draft 7, or removing the top-level declaration, is the documented
workaround). Evidence preserved in
``project-control/reports/M0-T141-canary-b502-schema-failure-evidence.md``.

The canonical contract schemas under ``schemas/`` stay Draft 2020-12 and keep
feeding the controller-side enforcer unchanged (R666). This module produces the
DEEP-COPIED provider-facing copy handed to the CLI (R667/R670): the top-level
declaration becomes the explicit Draft-7 one (R668), and every keyword is checked
against a same-meaning-in-both-drafts allowlist - any unknown, newer-draft-only,
or draft-divergent keyword raises ``ContractError`` instead of being silently
translated or dropped (R669). A projection failure surfaces through the runner's
existing typed-refusal path, still before any provider contact.

Import direction: this module imports ``.mrl_worker_result`` only (for
``ContractError``); nothing there imports it back, so no cycle can form.
"""
from __future__ import annotations

import copy
from typing import Any, Mapping

from .mrl_worker_result import ContractError

#: The dialect the canonical contract schemas declare (and the exact URI the
#: 2.1.252 CLI refused - the preserved stderr names this string verbatim).
CANONICAL_DECLARATION = "https://json-schema.org/draft/2020-12/schema"
#: The explicit Draft-7 declaration the provider copy carries (R668).
DRAFT7_DECLARATION = "http://json-schema.org/draft-07/schema#"

#: Keywords whose meaning is identical under Draft 2020-12 and Draft 7 for a
#: non-referencing schema (no $ref is admitted, so $id/$comment are inert
#: identity/annotation keywords in both drafts).
_SAME_MEANING = frozenset({
    "$id", "$comment", "title", "description", "default", "examples",
    "readOnly", "writeOnly", "type", "enum", "const",
    "multipleOf", "maximum", "exclusiveMaximum", "minimum", "exclusiveMinimum",
    "maxLength", "minLength", "pattern",
    "maxItems", "minItems", "uniqueItems",
    "maxProperties", "minProperties", "required",
    "format", "contentEncoding", "contentMediaType",
})
#: One subschema value; walked recursively. ``items`` is handled separately
#: because only its schema form means the same thing in both drafts.
_RECURSE_SINGLE = frozenset({
    "additionalProperties", "propertyNames", "contains", "not", "if", "then", "else",
})
#: name -> subschema maps; each value walked.
_RECURSE_MAP = frozenset({"properties", "patternProperties"})
#: lists of subschemas; each element walked.
_RECURSE_LIST = frozenset({"allOf", "anyOf", "oneOf"})
#: Refused outright, with the reason the projection cannot be trusted (R669).
_REFUSED = {
    "$ref": "resolves with different sibling-keyword semantics in Draft 7 vs Draft 2020-12",
    "$defs": "is Draft 2019-09+; a Draft-7 validator would silently ignore it",
    "definitions": "is a reserved bag only in Draft 7; under the canonical Draft 2020-12 it is an unknown keyword (drift signal)",
    "dependencies": "was removed in Draft 2019-09 (split into dependentRequired/dependentSchemas); the two drafts disagree",
    "$anchor": "is Draft 2019-09+",
    "$dynamicAnchor": "is Draft 2020-12 only",
    "$dynamicRef": "is Draft 2020-12 only",
    "$recursiveAnchor": "is Draft 2019-09 only",
    "$recursiveRef": "is Draft 2019-09 only",
    "$vocabulary": "is Draft 2019-09+",
    "unevaluatedItems": "is Draft 2019-09+; Draft 7 would silently ignore it",
    "unevaluatedProperties": "is Draft 2019-09+; Draft 7 would silently ignore it",
    "dependentRequired": "is Draft 2019-09+; Draft 7 would silently ignore it",
    "dependentSchemas": "is Draft 2019-09+; Draft 7 would silently ignore it",
    "minContains": "is Draft 2019-09+; Draft 7 would silently ignore it",
    "maxContains": "is Draft 2019-09+; Draft 7 would silently ignore it",
    "prefixItems": "is Draft 2020-12 only; Draft 7 would silently ignore it",
    "contentSchema": "is Draft 2019-09+; Draft 7 would silently ignore it",
    "deprecated": "is Draft 2019-09+; Draft 7 would silently ignore it",
}


def _refuse(where: str, key: str, why: str) -> None:
    raise ContractError(
        "draft7_schema_incompatible",
        f"{where}: keyword {key!r} {why}; the provider projection fails closed "
        f"instead of silently translating (R669)")


def _walk(node: Any, where: str) -> None:
    """Verify every keyword in a (sub)schema means the same thing under Draft 7."""
    if isinstance(node, bool):
        return  # boolean schemas are identical in both drafts
    if not isinstance(node, Mapping):
        _refuse(where, "<subschema>", f"is {type(node).__name__}, not a schema object")
    for key, value in node.items():
        if key == "$schema":
            _refuse(where, key, "declares a dialect below the top level")
        elif key in _REFUSED:
            _refuse(where, key, _REFUSED[key])
        elif key in _SAME_MEANING:
            continue  # enum/const/etc. values are data, never subschemas
        elif key == "items":
            if isinstance(value, list):
                _refuse(where, key, "is array-form (tuple) items - Draft 2020-12 "
                                    "and Draft 7 disagree on its meaning")
            _walk(value, f"{where}.items")
        elif key in _RECURSE_SINGLE:
            _walk(value, f"{where}.{key}")
        elif key in _RECURSE_MAP:
            if not isinstance(value, Mapping):
                _refuse(where, key, f"must map names to subschemas, got {type(value).__name__}")
            for name, sub in value.items():
                _walk(sub, f"{where}.{key}.{name}")
        elif key in _RECURSE_LIST:
            if not isinstance(value, list):
                _refuse(where, key, f"must be a list of subschemas, got {type(value).__name__}")
            for i, sub in enumerate(value):
                _walk(sub, f"{where}.{key}[{i}]")
        else:
            _refuse(where, key, "is not on the Draft-7 same-meaning allowlist")


def provider_schema_for_claude_cli(schema: Any) -> dict[str, Any]:
    """The deep-copied, explicitly Draft-7-declared copy for ``--json-schema``.

    The canonical in-memory schema is never mutated (R670): the projection deep
    copies first, verifies every keyword is Draft-7 compatible (R669, fail
    closed), and returns a NEW object whose only difference from the canonical
    content is the explicit Draft-7 top-level declaration (R667/R668). A
    canonical schema already declaring Draft 7, or declaring nothing, projects
    the same way; any other dialect refuses.
    """
    if not isinstance(schema, Mapping):
        raise ContractError("draft7_schema_incompatible",
                            f"provider schema must be a JSON object, got {type(schema).__name__}")
    projected = copy.deepcopy(dict(schema))
    declared = projected.pop("$schema", None)
    if declared is not None and declared not in (CANONICAL_DECLARATION, DRAFT7_DECLARATION):
        _refuse("schema", "$schema", f"declares unrecognized dialect {declared!r}")
    _walk(projected, "schema")
    return {"$schema": DRAFT7_DECLARATION, **projected}
