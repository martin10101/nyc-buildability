"""Strict, offline validation of a scenario document against the bundled
``scenario`` schema (task M5-T001).

Mirrors :mod:`app.rules.response`: the finished document is validated against
the runtime-bundled canonical schema (loaded read-only from
``app._contract_schemas.v1`` via ``importlib.resources`` - the same package-data
path the profile and rule_evaluation layers use, so it works from a non-editable
install with no ``packages/`` sibling). An invalid document is never returned.

``assert_scenario_not_verified`` is a belt-and-suspenders boundary guard: even
if a future refactor introduced a ``verified`` status, it can never leave this
layer.
"""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources

__all__ = [
    "ScenarioContractError",
    "assert_scenario_not_verified",
    "validate_scenario_document",
]

# The runtime-bundled schema package (package DATA inside the installed app),
# the same source app.profile.contract and app.rules.response load from.
_SCHEMA_PACKAGE = "app._contract_schemas.v1"

# scenario.schema.json's external $refs resolve into exactly these two sibling
# contracts: the canonical coverage vocabulary and the shared common shapes.
_REGISTRY_SCHEMA_FILES = (
    "scenario.schema.json",
    "common.schema.json",
    "coverage_status.schema.json",
)


class ScenarioContractError(Exception):
    """A scenario document failed strict validation against the bundled
    canonical schema. Raised SERVER-side: a document that does not honor the
    contract is an internal defect, mirroring the property-profile and
    rule_evaluation error paths."""

    def __init__(self, message: str, *, location: str) -> None:
        super().__init__(message)
        self.location = location


def _load_bundled_schema(name: str) -> dict:
    text = resources.files(_SCHEMA_PACKAGE).joinpath(name).read_text(encoding="utf-8")
    return json.loads(text)


@lru_cache(maxsize=1)
def _validator():
    """Strict Draft 2020-12 validator for scenario.schema.json with its common +
    coverage_status $refs resolved. Built once from the bundled package data
    (works from a non-editable install)."""
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


def _iter_coverage_values(node):
    """Yield every value stored under a ``coverage_status`` key anywhere."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "coverage_status" and isinstance(value, str):
                yield value
            yield from _iter_coverage_values(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_coverage_values(item)


def assert_scenario_not_verified(document: dict) -> None:
    """Fail closed if any ``coverage_status`` in the document equals
    ``verified``. A scenario is never Verified."""
    for value in _iter_coverage_values(document):
        if value == "verified":
            raise ScenarioContractError(
                "scenario document carries a 'verified' coverage_status; a scenario "
                "is never Verified",
                location="coverage_status",
            )


def validate_scenario_document(document: dict) -> None:
    """Validate a scenario document against the bundled scenario schema strictly,
    before use. Raises :class:`ScenarioContractError` on any defect so an invalid
    document is impossible to emit (mirrors validate_rule_evaluation_document).

    Also fails closed on any ``verified`` coverage_status and on any non-JSON-safe
    (NaN/Infinity) numeric, which strict JSON must never carry."""
    # Strict-JSON guard: reject NaN/Infinity before schema validation.
    try:
        json.dumps(document, allow_nan=False)
    except (ValueError, TypeError) as exc:
        raise ScenarioContractError(
            f"scenario document is not strict-JSON serializable: {exc}",
            location="<root>",
        ) from exc

    assert_scenario_not_verified(document)

    validator = _validator()
    errors = sorted(validator.iter_errors(document), key=lambda err: list(err.path))
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.path) or "<root>"
        raise ScenarioContractError(
            f"scenario document failed canonical schema validation at {location}: "
            f"{first.message}",
            location=location,
        )
