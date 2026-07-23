"""Contract-layer acceptance for scenario @ 1.0.0 (task M5-T001).

Offline and deterministic. Proves the new versioned contract:

- validates every canonical valid fixture (real builder output);
- rejects every invalid fixture for its stated defect;
- references the canonical coverage_status vocabulary (never redefining it) and
  NEVER admits 'verified' - a scenario is never Verified;
- keeps the evaluated input identified BY REFERENCE, never an embedded profile;
- keeps the runtime-bundled copy byte-identical to the canonical source (the
  drift guard sync_contract_schemas.py does not cover, because its SCHEMA_FILES
  tuple is a forbidden edit target, so it lives here - exactly as the
  rule_evaluation contract test does);
- leaves property_profile @ 1.4.0 and rule_evaluation @ 1.0.0 byte-identical.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

REPO_ROOT = Path(__file__).resolve().parents[4]
SCHEMA_DIR = REPO_ROOT / "packages" / "contracts" / "schemas" / "v1"
FIXTURE_ROOT = REPO_ROOT / "packages" / "contracts" / "fixtures"
BUNDLE_DIR = REPO_ROOT / "services" / "api" / "app" / "_contract_schemas" / "v1"

SCENARIO_SCHEMA = SCHEMA_DIR / "scenario.schema.json"
CANONICAL_COVERAGE = [
    "verified",
    "conditional",
    "professional_review_required",
    "data_conflict",
    "unsupported",
    "not_applicable",
]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _registry() -> Registry:
    resources = []
    for schema_file in sorted(SCHEMA_DIR.glob("*.schema.json")):
        doc = _load(schema_file)
        resources.append(
            (doc["$id"], Resource.from_contents(doc, default_specification=DRAFT202012))
        )
    return Registry().with_resources(resources)


def _validator() -> jsonschema.Draft202012Validator:
    return jsonschema.Draft202012Validator(_load(SCENARIO_SCHEMA), registry=_registry())


def _iter_coverage_values(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "coverage_status" and isinstance(value, str):
                yield value
            yield from _iter_coverage_values(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_coverage_values(item)


VALID_FIXTURES = sorted((FIXTURE_ROOT / "valid" / "scenario").glob("*.json"))
INVALID_FIXTURES = sorted((FIXTURE_ROOT / "invalid" / "scenario").glob("*.json"))


def test_there_are_the_required_fixtures():
    assert len(VALID_FIXTURES) >= 4, (
        "need >=4 valid fixtures (preliminary, unsupported, conflict, professional review)"
    )
    assert len(INVALID_FIXTURES) >= 3, (
        "need >=3 invalid fixtures (verified, embedded profile, missing field)"
    )


@pytest.mark.parametrize("fixture", VALID_FIXTURES, ids=lambda p: p.name)
def test_valid_fixture_validates(fixture: Path):
    _validator().validate(_load(fixture))


@pytest.mark.parametrize("fixture", VALID_FIXTURES, ids=lambda p: p.name)
def test_valid_fixture_never_verified(fixture: Path):
    values = list(_iter_coverage_values(_load(fixture)))
    assert values, "fixture should carry at least one coverage_status"
    assert "verified" not in values


@pytest.mark.parametrize("fixture", VALID_FIXTURES, ids=lambda p: p.name)
def test_valid_fixture_identifies_input_by_reference(fixture: Path):
    instance = _load(fixture)
    ev = instance["evaluated_input"]
    assert set(ev) == {
        "bbl",
        "profile_contract_version",
        "rule_evaluation_contract_version",
        "input_fingerprint",
    }
    # No embedded property-profile structure anywhere at the top level.
    for profile_key in (
        "property_profile",
        "lot_facts",
        "profile_version",
        "provenance",
        "identity",
    ):
        assert profile_key not in instance, f"unexpected embedded profile key {profile_key!r}"


@pytest.mark.parametrize("fixture", INVALID_FIXTURES, ids=lambda p: p.name)
def test_invalid_fixture_rejected(fixture: Path):
    instance = _load(fixture)
    assert "_expected_failure" in instance, "invalid fixture must document its defect"
    assert list(_validator().iter_errors(instance)), (
        f"invalid fixture {fixture.name} unexpectedly validated"
    )


def test_invalid_verified_fixture_fails_on_coverage_enum():
    instance = _load(FIXTURE_ROOT / "invalid" / "scenario" / "coverage_status_verified.json")
    messages = " | ".join(e.message for e in _validator().iter_errors(instance))
    assert "verified" in messages


def test_invalid_embedded_profile_fixture_fails_on_additional_property():
    instance = _load(FIXTURE_ROOT / "invalid" / "scenario" / "embedded_property_profile.json")
    messages = " ".join(e.message for e in _validator().iter_errors(instance))
    assert "property_profile" in messages and "dditional" in messages


def test_invalid_missing_field_fixture_fails_on_required():
    instance = _load(FIXTURE_ROOT / "invalid" / "scenario" / "missing_scenario_kind.json")
    messages = " ".join(e.message for e in _validator().iter_errors(instance))
    assert "scenario_kind" in messages and "required" in messages.lower()


# ---------------------------------------------------------------------------
# Canonical-coverage referencing invariants
# ---------------------------------------------------------------------------


def _all_enums(node):
    out = []
    if isinstance(node, dict):
        if "enum" in node and isinstance(node["enum"], list):
            out.append(sorted(node["enum"]))
        for value in node.values():
            out.extend(_all_enums(value))
    elif isinstance(node, list):
        for item in node:
            out.extend(_all_enums(item))
    return out


def test_schema_refs_canonical_coverage_status_never_redefines_it():
    schema = _load(SCENARIO_SCHEMA)
    draft = schema["$defs"]["coverage_status_draft"]
    refs = [branch.get("$ref") for branch in draft["allOf"] if "$ref" in branch]
    assert "coverage_status.schema.json" in refs
    assert schema["properties"]["coverage_status"] == {"$ref": "#/$defs/coverage_status_draft"}
    # The full canonical 6-value enum is never re-listed anywhere in this file.
    assert sorted(CANONICAL_COVERAGE) not in _all_enums(schema)


def test_verified_is_not_an_allowed_coverage_status():
    schema = _load(SCENARIO_SCHEMA)
    subset = next(
        b["enum"] for b in schema["$defs"]["coverage_status_draft"]["allOf"] if "enum" in b
    )
    assert "verified" not in subset
    assert set(subset) == set(CANONICAL_COVERAGE) - {"verified"}

    valid = _load(FIXTURE_ROOT / "valid" / "scenario" / "preliminary_r5_cap.json")
    tampered = dict(valid)
    tampered["coverage_status"] = "verified"
    assert list(_validator().iter_errors(tampered))


# ---------------------------------------------------------------------------
# Runtime bundle byte-identity (drift guard the forbidden sync script omits)
# ---------------------------------------------------------------------------


def test_runtime_bundle_copy_is_byte_identical_to_canonical():
    canonical = SCENARIO_SCHEMA.read_bytes()
    bundled = (BUNDLE_DIR / "scenario.schema.json").read_bytes()
    assert bundled == canonical, (
        "services/api/app/_contract_schemas/v1/scenario.schema.json is out of sync "
        "with the canonical packages/contracts source. sync_contract_schemas.py does "
        "not guard it (its SCHEMA_FILES tuple is a forbidden edit target for M5-T001); "
        "recopy the canonical bytes."
    )


# ---------------------------------------------------------------------------
# Neighbouring contracts untouched
# ---------------------------------------------------------------------------


def test_property_profile_and_rule_evaluation_contracts_untouched():
    profile = _load(SCHEMA_DIR / "property_profile.schema.json")
    assert profile["properties"]["profile_version"]["properties"]["contract_version"][
        "enum"
    ] == ["1.0.0", "1.1.0", "1.2.0", "1.3.0", "1.4.0"]
    rule_eval = _load(SCHEMA_DIR / "rule_evaluation.schema.json")
    assert rule_eval["properties"]["contract_version"]["enum"] == ["1.0.0"]
