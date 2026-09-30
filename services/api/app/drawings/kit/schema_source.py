"""Read-only loading of the canonical ``results`` contract for input validation.

Mirrors the bundled-schema pattern of :mod:`app.scenario.contract` (package data
under ``app._contract_schemas.v1`` read with ``importlib.resources``, a strict
Draft 2020-12 validator with a ``referencing`` registry). ``results.schema.json``
and the contracts it references (``common``, ``site_fact``, ``study``) are not in
that bundle yet (request E-1 to Lane C), so when the bundle lacks any of them
the canonical source ``packages/contracts/schemas/v1`` of a source checkout is
used instead. All four documents always come from ONE place. When neither
place has them all, validation fails CLOSED (``schema_unavailable``).
"""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from pathlib import Path

from .errors import DrawingInputError

__all__ = ["results_validator", "schema_documents"]

_BUNDLED_PACKAGE = "app._contract_schemas.v1"

# results.schema.json's external $refs resolve into exactly these contracts
# (study.schema.json in turn references common and site_fact only).
_SCHEMA_FILES = (
    "results.schema.json",
    "common.schema.json",
    "site_fact.schema.json",
    "study.schema.json",
)


def _bundled_texts() -> dict[str, str] | None:
    root = resources.files(_BUNDLED_PACKAGE)
    if not all(root.joinpath(name).is_file() for name in _SCHEMA_FILES):
        return None
    return {name: root.joinpath(name).read_text(encoding="utf-8") for name in _SCHEMA_FILES}


def _canonical_texts() -> dict[str, str] | None:
    for parent in Path(__file__).resolve().parents:
        directory = parent / "packages" / "contracts" / "schemas" / "v1"
        if directory.is_dir():
            if not all((directory / name).is_file() for name in _SCHEMA_FILES):
                return None
            return {
                name: (directory / name).read_text(encoding="utf-8") for name in _SCHEMA_FILES
            }
    return None


@lru_cache(maxsize=1)
def schema_documents() -> tuple[dict, ...]:
    """The four schema documents, results first, all from one source."""
    texts = _bundled_texts() or _canonical_texts()
    if texts is None:
        raise DrawingInputError(
            "schema_unavailable",
            "results.schema.json and its referenced contracts could not be loaded",
        )
    return tuple(json.loads(texts[name]) for name in _SCHEMA_FILES)


@lru_cache(maxsize=1)
def results_validator():
    """Strict Draft 2020-12 validator for results.schema.json (built once)."""
    import jsonschema
    from referencing import Registry, Resource

    docs = schema_documents()
    registry = Registry().with_resources(
        [(doc["$id"], Resource.from_contents(doc)) for doc in docs]
    )
    return jsonschema.Draft202012Validator(docs[0], registry=registry)
