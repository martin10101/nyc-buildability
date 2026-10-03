"""Strict, offline validation for the study contract set (task C-03, plan M1-09).

The six v1 contracts added by M5-T125 - site_fact, study, results,
report_model, export_record and benchmark_lot - are validated against the
runtime-bundled canonical schemas (``app._contract_schemas.v1``, loaded
read-only via ``importlib.resources`` - the same package-data path
``app.scenario.contract`` and ``app.rules.response`` use, so it works from a
non-editable install with no ``packages/`` sibling). The bundle copies are kept
byte-identical to ``packages/contracts/schemas/v1`` by
``services/api/scripts/sync_contract_schemas.py --check``.

A producer calls ``validate_<stem>_document(doc)`` before it hands a document
on; any defect raises :class:`StudyContractError`, so an invalid document is
never emitted. On top of the schema this layer fails closed on:

- non-strict JSON (NaN/Infinity), which the schemas cannot see;
- the fixture-only ``_expected_failure`` annotation anywhere in the document:
  the schemas admit it so invalid FIXTURES fail only for their stated defect,
  but producers never emit it.

Library only: nothing in the request path calls it yet (no behavior change).
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from functools import lru_cache
from importlib import resources
from typing import Any

__all__ = [
    "STUDY_CONTRACT_STEMS",
    "StudyContractError",
    "validate_benchmark_lot_document",
    "validate_export_record_document",
    "validate_hidden_issue_flags_document",
    "validate_parity_data_document",
    "validate_report_model_document",
    "validate_results_document",
    "validate_site_fact_document",
    "validate_evaluator_inputs_document",
    "validate_study_contract_document",
    "validate_study_document",
    "validate_transit_parking_document",
]

_SCHEMA_PACKAGE = "app._contract_schemas.v1"

STUDY_CONTRACT_STEMS = (
    "site_fact",
    "study",
    "results",
    "report_model",
    "export_record",
    "benchmark_lot",
    # Lane C packet W0 wiring contracts (plan section 8a / check C-8 / section 11b).
    "hidden_issue_flags",
    "transit_parking",
    "parity_data",
    # Lane C evaluator channel (task C-07, plan M1-08). $refs site_fact + common.
    "evaluator_inputs",
)

# Every $ref in the schemas resolves within the set plus common.schema.json
# (checked against the schemas: site_fact -> common; study -> site_fact;
# results -> site_fact, study; report_model, benchmark_lot -> results;
# export_record -> study, site_fact, results; the W0 wiring contracts
# hidden_issue_flags, transit_parking and parity_data -> common + site_fact
# (site_fact.schema.json#/$defs/source, and parity_data also #/$defs/measurement);
# evaluator_inputs -> common + site_fact (it mirrors site_fact's measurement
# and source vocabulary in its own $defs). One registry serves all of them.
_REGISTRY_SCHEMA_FILES = tuple(f"{stem}.schema.json" for stem in STUDY_CONTRACT_STEMS) + (
    "common.schema.json",
)

FIXTURE_ONLY_KEY = "_expected_failure"

# A schema error message can repr the whole failing instance (a root-level
# oneOf failure prints the entire document); keep raised messages bounded.
_MAX_DETAIL_CHARS = 300


class StudyContractError(Exception):
    """A study-set document failed strict validation. Raised server-side: a
    document that does not honor its contract is an internal defect."""

    def __init__(self, message: str, *, contract: str, location: str) -> None:
        super().__init__(message)
        self.contract = contract
        self.location = location


def _load_bundled_schema(name: str) -> dict:
    text = resources.files(_SCHEMA_PACKAGE).joinpath(name).read_text(encoding="utf-8")
    return json.loads(text)


@lru_cache(maxsize=1)
def _registry():
    from referencing import Registry, Resource

    docs = [_load_bundled_schema(name) for name in _REGISTRY_SCHEMA_FILES]
    return Registry().with_resources(
        [(doc["$id"], Resource.from_contents(doc)) for doc in docs]
    )


@lru_cache(maxsize=len(STUDY_CONTRACT_STEMS))
def _validator(stem: str):
    """Strict Draft 2020-12 validator for one stem, built once from the bundle."""
    import jsonschema

    schema = _load_bundled_schema(f"{stem}.schema.json")
    return jsonschema.Draft202012Validator(schema, registry=_registry())


def _fixture_annotation_paths(node: Any, path: str = "") -> Iterator[str]:
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}/{key}" if path else str(key)
            if key == FIXTURE_ONLY_KEY:
                yield here
            yield from _fixture_annotation_paths(value, here)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            yield from _fixture_annotation_paths(item, f"{path}/{index}" if path else str(index))


def validate_study_contract_document(stem: str, document: Any) -> None:
    """Validate ``document`` against the bundled ``<stem>`` schema strictly.

    Raises :class:`StudyContractError` on any defect; returns None when valid.
    An unknown stem is a programming error (ValueError), never a silent pass."""
    if stem not in STUDY_CONTRACT_STEMS:
        raise ValueError(f"unknown study contract {stem!r}; expected one of {STUDY_CONTRACT_STEMS}")
    if not isinstance(document, dict):
        raise StudyContractError(
            f"{stem} document must be a JSON object, got {type(document).__name__}",
            contract=stem,
            location="<root>",
        )
    try:
        json.dumps(document, allow_nan=False)
    except (ValueError, TypeError) as exc:
        raise StudyContractError(
            f"{stem} document is not strict-JSON serializable: {exc}",
            contract=stem,
            location="<root>",
        ) from exc
    annotation = next(_fixture_annotation_paths(document), None)
    if annotation is not None:
        raise StudyContractError(
            f"{stem} document carries the fixture-only key {FIXTURE_ONLY_KEY!r} at "
            f"{annotation}; producers never emit it",
            contract=stem,
            location=annotation,
        )

    errors = sorted(
        _validator(stem).iter_errors(document),
        key=lambda err: [str(part) for part in err.absolute_path],
    )
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.absolute_path) or "<root>"
        detail = first.message
        if len(detail) > _MAX_DETAIL_CHARS:
            detail = detail[:_MAX_DETAIL_CHARS] + "..."
        raise StudyContractError(
            f"{stem} document failed canonical schema validation at {location}: {detail}",
            contract=stem,
            location=location,
        )


def validate_site_fact_document(document: Any) -> None:
    validate_study_contract_document("site_fact", document)


def validate_study_document(document: Any) -> None:
    validate_study_contract_document("study", document)


def validate_results_document(document: Any) -> None:
    validate_study_contract_document("results", document)


def validate_report_model_document(document: Any) -> None:
    validate_study_contract_document("report_model", document)


def validate_export_record_document(document: Any) -> None:
    validate_study_contract_document("export_record", document)


def validate_benchmark_lot_document(document: Any) -> None:
    validate_study_contract_document("benchmark_lot", document)


def validate_hidden_issue_flags_document(document: Any) -> None:
    validate_study_contract_document("hidden_issue_flags", document)


def validate_transit_parking_document(document: Any) -> None:
    validate_study_contract_document("transit_parking", document)


def validate_parity_data_document(document: Any) -> None:
    validate_study_contract_document("parity_data", document)


def validate_evaluator_inputs_document(document: Any) -> None:
    validate_study_contract_document("evaluator_inputs", document)
