"""The study-read route's study-setup document is contract-valid (lane C, request
D-1 slice 1).

Independent of the route's own (bundled-schema) guard: this validates the emitted
document against the CANONICAL ``packages/contracts/schemas/v1`` files with
jsonschema, so a drift between the bundle and the canonical schemas could not hide
a defect. The document is produced from the recorded 215-16 Northern PLUTO body
through the real B-02/B-07 pipeline; no network is touched.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path

import jsonschema
from referencing import Registry, Resource

from app.api.v1.study_inputs import assemble_study_inputs
from app.api.v1.study_read import _build_document
from app.connectors.pluto_soda import TransportResponse, fetch_by_bbl

REPO_ROOT = Path(__file__).resolve().parents[4]
SCHEMA_DIR = REPO_ROOT / "packages" / "contracts" / "schemas" / "v1"
PLUTO_FIXTURE = (
    REPO_ROOT
    / "services" / "api" / "tests" / "fixtures" / "benchmark_215_16_northern"
    / "pluto_64uk-42ks_bbl_4073340070.json"
)
NORTHERN_BBL = "4073340070"
STUDY_ID = (
    "https://github.com/martin10101/nyc-buildability/packages/contracts/schemas/v1/"
    "study.schema.json"
)
SITE_FACT_ID = (
    "https://github.com/martin10101/nyc-buildability/packages/contracts/schemas/v1/"
    "site_fact.schema.json"
)
FIXED_CLOCK = lambda: datetime(2026, 9, 30, 12, 0, 0, tzinfo=UTC)  # noqa: E731


@lru_cache(maxsize=1)
def _registry() -> Registry:
    docs = [
        json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))
        for name in ("study.schema.json", "site_fact.schema.json", "common.schema.json")
    ]
    return Registry().with_resources([(doc["$id"], Resource.from_contents(doc)) for doc in docs])


def _validator(ref: str) -> jsonschema.Draft202012Validator:
    return jsonschema.Draft202012Validator({"$ref": STUDY_ID + ref}, registry=_registry())


def _setup_document() -> dict:
    body = PLUTO_FIXTURE.read_text(encoding="utf-8")
    result = fetch_by_bbl(
        NORTHERN_BBL,
        transport=lambda url, headers, timeout: TransportResponse(200, body),
        sleep=lambda seconds: None,
        clock=FIXED_CLOCK,
        correlation_id="contract-test",
    )
    inputs = assemble_study_inputs(result, clock=FIXED_CLOCK, env={"LANE_B_ENABLED": "1"})
    return _build_document(NORTHERN_BBL, inputs)


def test_every_emitted_site_fact_is_site_fact_contract_valid() -> None:
    document = _setup_document()
    facts = document["site"]["facts"]
    assert facts, "the recorded Northern lot yields at least one site fact"
    site_fact_validator = jsonschema.Draft202012Validator(
        {"$ref": SITE_FACT_ID}, registry=_registry()
    )
    for fact in facts:
        json.dumps(fact, allow_nan=False)  # strict JSON, the schema cannot see NaN
        assert "_expected_failure" not in fact
        errors = [error.message for error in site_fact_validator.iter_errors(fact)]
        assert not errors, (fact.get("fact_id"), errors)


def test_version_check_facts_validate_against_the_canonical_site_fact_schema() -> None:
    """B-3: the emitted facts now carry ``source.version_check`` at contract 1.1.0.
    Prove the versioned facts validate against the CANONICAL packages/contracts
    site_fact schema (not only the route's bundled copy), and that the recorded
    Northern pack yields at least one such fact."""
    document = _setup_document()
    facts = document["site"]["facts"]
    site_fact_validator = jsonschema.Draft202012Validator(
        {"$ref": SITE_FACT_ID}, registry=_registry()
    )
    versioned = [fact for fact in facts if (fact.get("source") or {}).get("version_check")]
    assert versioned, "the recorded Northern pack carries at least one version_check fact"
    for fact in versioned:
        assert fact["contract_version"] == "1.1.0", fact.get("fact_id")
        errors = [error.message for error in site_fact_validator.iter_errors(fact)]
        assert not errors, (fact.get("fact_id"), errors)


def test_lots_and_lot_selection_match_the_study_defs() -> None:
    document = _setup_document()
    for lot in document["lots"]:
        errors = [error.message for error in _validator("#/$defs/lot").iter_errors(lot)]
        assert not errors, (lot.get("bbl"), errors)
    sel_errors = [
        error.message
        for error in _validator("#/properties/lot_selection").iter_errors(
            document["lot_selection"]
        )
    ]
    assert not sel_errors, sel_errors


def test_setup_composes_into_a_valid_study() -> None:
    document = _setup_document()
    # A TEST-ONLY option (never emitted by the route) completes the Study so the
    # real parts can be validated in place against study.schema.json.
    option = {
        "option_id": "opt-test",
        "name": "Option test (test-fixture-synthetic)",
        "addon_selection": [],
        "goal": {"kind": "most_residential_floor_area", "text": None},
        "program": ["market_rate_residential"],
        "floor_to_floor_heights": {
            "ground_floor": {"height_ft": 12, "basis": "stated_default", "statement": "t 12 ft"},
            "typical_floor": {"height_ft": 10, "basis": "stated_default", "statement": "t 10 ft"},
            "per_floor_overrides": [],
        },
        "assumptions": [],
        "existing_building_plan": "no_existing_building",
    }
    study = {
        "contract_version": "1.0.0",
        "study_id": "test-fixture-synthetic-study",
        "property": document["property"],
        "lots": document["lots"],
        "lot_selection": document["lot_selection"],
        "site": document["site"],
        "options": [option],
        "selected_option_id": "opt-test",
        "revision": {"number": 1, "created_at": "2026-09-30T12:00:00Z", "parent": None},
        "origin": {"kind": "new", "export_id": None},
    }
    errors = sorted(
        _validator("").iter_errors(study), key=lambda err: list(err.path)
    )
    assert not errors, [error.message for error in errors]
