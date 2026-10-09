"""Test-only validation against the study v1 contract (queue item B-07).

Validates a document against a JSON pointer inside the canonical
``packages/contracts/schemas/v1/study.schema.json`` (Draft 2020-12; ``site_fact`` and
``common`` resolved), for example ``#/$defs/lot`` or ``#/properties/lot_selection``.
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path

import jsonschema
from referencing import Registry, Resource

SCHEMAS = Path(__file__).resolve().parents[4] / "packages" / "contracts" / "schemas" / "v1"
STUDY_ID = ("https://github.com/martin10101/nyc-buildability/packages/contracts/schemas/v1/"
            "study.schema.json")


@cache
def _validator(pointer: str) -> jsonschema.Draft202012Validator:
    docs = [json.loads((SCHEMAS / name).read_text("utf-8"))
            for name in ("study.schema.json", "site_fact.schema.json", "common.schema.json")]
    registry = Registry().with_resources([(d["$id"], Resource.from_contents(d)) for d in docs])
    return jsonschema.Draft202012Validator({"$ref": STUDY_ID + pointer}, registry=registry)


def assert_valid_study_part(document: dict, pointer: str) -> None:
    json.dumps(document, allow_nan=False)
    errors = [error.message for error in _validator(pointer).iter_errors(document)]
    assert not errors, (document, errors)
