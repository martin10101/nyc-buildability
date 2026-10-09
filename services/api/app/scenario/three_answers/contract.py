"""Strict, offline validation of a results document against the bundled ``results`` schema
(task A-04).

Mirrors :mod:`app.scenario.contract`: the finished document is validated against the
runtime-bundled canonical schema (loaded read-only from ``app._contract_schemas.v1`` via
``importlib.resources``), so it works from a non-editable install with no ``packages/``
sibling. Lane C owns the schema; this module only READS it. An invalid document is never
returned by the generator.
"""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources

from app.contracts.results_way_rules import results_way_violations

__all__ = ["ResultsContractError", "validate_results_document"]

_SCHEMA_PACKAGE = "app._contract_schemas.v1"

# results.schema.json's external $refs reach these sibling contracts (transitively). All are
# loaded into the registry so every $ref resolves regardless of traversal order.
_REGISTRY_SCHEMA_FILES = (
    "results.schema.json",
    "common.schema.json",
    "site_fact.schema.json",
    "study.schema.json",
    "lot_geometry.schema.json",
    "source_fact.schema.json",
    "export_record.schema.json",
    "rule_evaluation.schema.json",
    "coverage_status.schema.json",
)


class ResultsContractError(Exception):
    """A results document failed strict validation against the bundled canonical schema.
    Raised SERVER-side: a document that does not honor the contract is an internal defect."""

    def __init__(self, message: str, *, location: str) -> None:
        super().__init__(message)
        self.location = location


def _load_bundled_schema(name: str) -> dict:
    text = resources.files(_SCHEMA_PACKAGE).joinpath(name).read_text(encoding="utf-8")
    return json.loads(text)


@lru_cache(maxsize=1)
def _validator():
    """Strict Draft 2020-12 validator for results.schema.json with its sibling $refs
    resolved, built once from the bundled package data."""
    import jsonschema

    docs = [_load_bundled_schema(name) for name in _REGISTRY_SCHEMA_FILES]
    schema = docs[0]
    try:
        from referencing import Registry, Resource

        registry = Registry().with_resources(
            [(doc["$id"], Resource.from_contents(doc)) for doc in docs]
        )
        return jsonschema.Draft202012Validator(schema, registry=registry)
    except ImportError:  # pragma: no cover - exercised only on legacy runners
        resolver = jsonschema.RefResolver(
            base_uri=schema["$id"],
            referrer=schema,
            store={doc["$id"]: doc for doc in docs},
        )
        return jsonschema.Draft202012Validator(schema, resolver=resolver)


def validate_results_document(document: dict) -> None:
    """Validate a results document against the bundled results schema strictly, before use.
    Raises :class:`ResultsContractError` on any defect so an invalid document is impossible
    to emit. Also fails closed on any non-JSON-safe (NaN/Infinity) numeric."""
    try:
        json.dumps(document, allow_nan=False)
    except (ValueError, TypeError) as exc:
        raise ResultsContractError(
            f"results document is not strict-JSON serializable: {exc}", location="<root>"
        ) from exc

    validator = _validator()
    errors = sorted(validator.iter_errors(document), key=lambda err: list(err.path))
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.path) or "<root>"
        raise ResultsContractError(
            f"results document failed canonical schema validation at {location}: "
            f"{first.message}",
            location=location,
        )

    # After the schema: a 1.3.0 document must also honor the way-layer rule the schema
    # cannot express (one shared rule; no copy here - see app.contracts.results_way_rules).
    violations = results_way_violations(document)
    if violations:
        first_way = violations[0]
        detail = "; ".join(violation.detail for violation in violations)
        raise ResultsContractError(
            "results document declares contract 1.3.0 but breaks the value-state way "
            f"rule: {detail}",
            location=f"answers/{first_way.answer}/value_states/{first_way.key}",
        )
