"""Test-only site_fact v1 contract validation (queue item B-02).

Validates against the canonical ``packages/contracts/schemas/v1/site_fact.schema.json``
with jsonschema (Draft 2020-12, ``common.schema.json`` resolved), strict JSON (no
NaN/Infinity), and no fixture-only ``_expected_failure`` key. When the Lane C runtime
validator ``app.contracts.study_contracts.validate_site_fact_document`` (task C-03) is
on the branch, every document is ALSO checked by it, so these tests keep proving the
production path once it lands.
"""

from __future__ import annotations

import json
from functools import cache, lru_cache
from pathlib import Path

import jsonschema
from referencing import Registry, Resource

REPO_ROOT = Path(__file__).resolve().parents[4]
SCHEMA_DIR = REPO_ROOT / "packages" / "contracts" / "schemas" / "v1"
SITE_FACT_ID = (
    "https://github.com/martin10101/nyc-buildability/packages/contracts/schemas/v1/"
    "site_fact.schema.json"
)


def load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _registry() -> Registry:
    docs = [load_schema(name) for name in ("site_fact.schema.json", "common.schema.json")]
    return Registry().with_resources(
        [(doc["$id"], Resource.from_contents(doc)) for doc in docs]
    )


@cache
def validator_for(ref: str) -> jsonschema.Draft202012Validator:
    """Validator for the site_fact schema (``ref=""``) or one of its ``$defs``
    (``ref="#/$defs/measurement_known"``)."""
    return jsonschema.Draft202012Validator({"$ref": SITE_FACT_ID + ref}, registry=_registry())


def schema_errors(document: object, ref: str = "") -> list[str]:
    return [error.message for error in validator_for(ref).iter_errors(document)]


def assert_valid_site_fact(document: dict) -> None:
    json.dumps(document, allow_nan=False)
    assert "_expected_failure" not in document
    errors = schema_errors(document)
    assert not errors, (document.get("fact_id"), errors)
    try:
        from app.contracts.study_contracts import validate_site_fact_document
    except ImportError:  # C-03 not merged into this branch yet
        return
    validate_site_fact_document(document)
