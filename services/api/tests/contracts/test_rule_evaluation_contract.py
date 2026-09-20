"""Contract-layer acceptance pack for rule_evaluation @ 1.0.0 (task M4-T005).

Offline and deterministic. Proves the new versioned contract:

- validates every canonical valid fixture (the exported evaluate_property shape);
- rejects every invalid fixture for its stated defect;
- references the canonical coverage_status vocabulary (never redefining it) and
  NEVER admits 'verified' - a draft-rule result may never be Verified;
- keeps the evaluated input identified BY REFERENCE (bbl + profile contract
  version + provenance + fingerprint), never an embedded profile copy;
- keeps the runtime-bundled copy byte-identical to the canonical source (the
  drift guard sync_contract_schemas.py cannot cover because its SCHEMA_FILES
  tuple is a forbidden edit target, so it lives here instead);
- leaves property_profile @ 1.4.0 byte-identical and still valid (AS-2).

Uses jsonschema (already a test dependency) with a referencing registry so the
cross-file $refs into coverage_status.schema.json / common.schema.json resolve.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

# services/api/tests/contracts/test_...py -> parents[4] is the repo root.
REPO_ROOT = Path(__file__).resolve().parents[4]
SCHEMA_DIR = REPO_ROOT / "packages" / "contracts" / "schemas" / "v1"
FIXTURE_ROOT = REPO_ROOT / "packages" / "contracts" / "fixtures"
BUNDLE_DIR = REPO_ROOT / "services" / "api" / "app" / "_contract_schemas" / "v1"

RULE_EVAL_SCHEMA = SCHEMA_DIR / "rule_evaluation.schema.json"
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
    """Registry of every v1 contract schema, keyed by $id, so any cross-file
    $ref resolves (mirrors how the API loads the four-schema $ref set)."""
    resources = []
    for schema_file in sorted(SCHEMA_DIR.glob("*.schema.json")):
        doc = _load(schema_file)
        resources.append(
            (doc["$id"], Resource.from_contents(doc, default_specification=DRAFT202012))
        )
    return Registry().with_resources(resources)


def _validator() -> jsonschema.Draft202012Validator:
    schema = _load(RULE_EVAL_SCHEMA)
    return jsonschema.Draft202012Validator(schema, registry=_registry())


def _iter_coverage_values(node):
    """Every value stored under a 'coverage_status' key anywhere in a payload."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "coverage_status" and isinstance(value, str):
                yield value
            yield from _iter_coverage_values(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_coverage_values(item)


VALID_FIXTURES = sorted((FIXTURE_ROOT / "valid" / "rule_evaluation").glob("*.json"))
INVALID_FIXTURES = sorted((FIXTURE_ROOT / "invalid" / "rule_evaluation").glob("*.json"))


def test_there_are_the_required_fixtures() -> None:
    assert len(VALID_FIXTURES) >= 4, (
        "need >=4 valid fixtures (draft, not_applicable, fail-safe, split-lot)"
    )
    assert len(INVALID_FIXTURES) >= 3, (
        "need >=3 invalid fixtures (verified, missing field, embedded profile)"
    )


@pytest.mark.parametrize("fixture", VALID_FIXTURES, ids=lambda p: p.name)
def test_valid_fixture_validates(fixture: Path) -> None:
    """AS-1: each realistic exported payload validates; coverage/provenance
    resolve via $ref."""
    instance = _load(fixture)
    _validator().validate(instance)  # raises on failure


@pytest.mark.parametrize("fixture", VALID_FIXTURES, ids=lambda p: p.name)
def test_valid_fixture_never_verified(fixture: Path) -> None:
    """No valid fixture carries 'verified' at any coverage_status site."""
    values = list(_iter_coverage_values(_load(fixture)))
    assert values, "fixture should carry at least one coverage_status"
    assert "verified" not in values


@pytest.mark.parametrize("fixture", VALID_FIXTURES, ids=lambda p: p.name)
def test_valid_fixture_identifies_input_by_reference(fixture: Path) -> None:
    """The document identifies the evaluated input by reference and never
    embeds a full property profile."""
    instance = _load(fixture)
    ev = instance["evaluated_input"]
    assert set(ev) == {"bbl", "profile_contract_version", "input_fingerprint", "input_provenance"}
    assert ev["input_fingerprint"].startswith("sha256:")
    # No embedded property-profile structure anywhere at the top level.
    for profile_key in (
        "property_profile", "lot_facts", "profile_version", "provenance", "identity",
    ):
        assert profile_key not in instance, f"unexpected embedded profile key {profile_key!r}"


@pytest.mark.parametrize("fixture", INVALID_FIXTURES, ids=lambda p: p.name)
def test_invalid_fixture_rejected(fixture: Path) -> None:
    """Each invalid fixture fails validation and carries an _expected_failure
    note documenting the intended defect."""
    instance = _load(fixture)
    assert "_expected_failure" in instance, "invalid fixture must document its defect"
    errors = list(_validator().iter_errors(instance))
    assert errors, f"invalid fixture {fixture.name} unexpectedly validated"


def test_invalid_verified_fixture_fails_on_coverage_enum() -> None:
    instance = _load(FIXTURE_ROOT / "invalid" / "rule_evaluation" / "coverage_status_verified.json")
    messages = " | ".join(e.message for e in _validator().iter_errors(instance))
    assert "verified" in messages


def test_invalid_missing_field_fixture_fails_on_required() -> None:
    instance = _load(FIXTURE_ROOT / "invalid" / "rule_evaluation" / "missing_coverage_status.json")
    messages = " ".join(e.message for e in _validator().iter_errors(instance))
    assert "coverage_status" in messages and "required" in messages.lower()


def test_invalid_embedded_profile_fixture_fails_on_additional_property() -> None:
    instance = _load(
        FIXTURE_ROOT / "invalid" / "rule_evaluation" / "embedded_property_profile.json"
    )
    messages = " ".join(e.message for e in _validator().iter_errors(instance))
    assert "property_profile" in messages and "dditional" in messages


# ---------------------------------------------------------------------------
# Canonical-coverage referencing invariants
# ---------------------------------------------------------------------------


def test_schema_refs_canonical_coverage_status_never_redefines_it() -> None:
    """The contract references coverage_status.schema.json for its vocabulary
    and never redefines the canonical 6-value enum inline."""
    schema = _load(RULE_EVAL_SCHEMA)
    draft = schema["$defs"]["coverage_status_draft"]
    refs = [branch.get("$ref") for branch in draft["allOf"] if "$ref" in branch]
    assert "coverage_status.schema.json" in refs, (
        "coverage_status_draft must $ref the canonical schema"
    )
    # Every coverage_status property points at the shared draft def, not an
    # inline enum.
    assert schema["properties"]["coverage_status"] == {"$ref": "#/$defs/coverage_status_draft"}
    assert schema["$defs"]["family_coverage"]["properties"]["coverage_status"] == {
        "$ref": "#/$defs/coverage_status_draft"
    }
    assert schema["$defs"]["evaluation_trace"]["properties"]["coverage_status"] == {
        "$ref": "#/$defs/coverage_status_draft"
    }
    # The full canonical 6-value enum is never re-listed anywhere in this file.
    assert sorted(CANONICAL_COVERAGE) not in _all_enums(schema)


def test_verified_is_not_an_allowed_coverage_status() -> None:
    """'verified' is excluded from the draft coverage vocabulary and rejected by
    validation at the coverage_status site."""
    schema = _load(RULE_EVAL_SCHEMA)
    subset = next(
        b["enum"] for b in schema["$defs"]["coverage_status_draft"]["allOf"] if "enum" in b
    )
    assert "verified" not in subset
    assert set(subset) == set(CANONICAL_COVERAGE) - {"verified"}

    valid = _load(FIXTURE_ROOT / "valid" / "rule_evaluation" / "supported_family_draft.json")
    tampered = dict(valid)
    tampered["coverage_status"] = "verified"
    assert list(_validator().iter_errors(tampered)), (
        "'verified' must be rejected at coverage_status"
    )


def _all_enums(node) -> list:
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


# ---------------------------------------------------------------------------
# Runtime bundle byte-identity (drift guard the forbidden sync script omits)
# ---------------------------------------------------------------------------


def test_runtime_bundle_copy_is_byte_identical_to_canonical() -> None:
    canonical = RULE_EVAL_SCHEMA.read_bytes()
    bundled = (BUNDLE_DIR / "rule_evaluation.schema.json").read_bytes()
    assert bundled == canonical, (
        "services/api/app/_contract_schemas/v1/rule_evaluation.schema.json is out of "
        "sync with the canonical packages/contracts source. sync_contract_schemas.py "
        "does not guard it (its SCHEMA_FILES tuple is a forbidden edit target for "
        "M4-T005 phase 1); recopy the canonical bytes."
    )


# ---------------------------------------------------------------------------
# AS-2: property_profile @ 1.4.0 untouched and still valid
# ---------------------------------------------------------------------------


def test_property_profile_contract_still_1_4_0_closed_enum() -> None:
    profile = _load(SCHEMA_DIR / "property_profile.schema.json")
    enum = profile["properties"]["profile_version"]["properties"]["contract_version"]["enum"]
    assert enum == ["1.0.0", "1.1.0", "1.2.0", "1.3.0", "1.4.0"]


@pytest.mark.parametrize(
    "fixture",
    sorted((FIXTURE_ROOT / "valid" / "property_profile").glob("*.json")),
    ids=lambda p: p.name,
)
def test_existing_property_profile_fixtures_still_validate(fixture: Path) -> None:
    schema = _load(SCHEMA_DIR / "property_profile.schema.json")
    jsonschema.Draft202012Validator(schema, registry=_registry()).validate(_load(fixture))


# ---------------------------------------------------------------------------
# M5-T058: additive contract 1.2.0 — the OPTIONAL substrate_substitution block
# (condo billing-BBL -> base-lot substitution stamp) + the condo_base_lot_
# unresolved honest-refusal vocabulary. Documents are built INLINE from the
# committed valid fixtures because packages/contracts/fixtures is a forbidden
# edit target for this packet, so no new fixture file is added; the block shape
# mirrors app.spatial.live_provider.build_substrate_substitution_stamp.
# ---------------------------------------------------------------------------

BASE_VALID = FIXTURE_ROOT / "valid" / "rule_evaluation" / "supported_family_draft.json"
BASE_FAIL_SAFE = FIXTURE_ROOT / "valid" / "rule_evaluation" / "professional_review_fail_safe.json"

SUBSTRATE_SUBSTITUTION_BLOCK = {
    "entered_bbl": "3022647515",
    "analyzed_bbl": "3022640032",
    "note": (
        "This analysis runs on the recorded base tax lot for the entered "
        "condominium billing lot; the entered billing lot and the analyzed base "
        "lot are recorded as entered versus analyzed, a record and not a "
        "computed allowance."
    ),
    "condo_key": "301313",
    "resolution_path": "dof_dtm_condo",
    "source_id": "nyc-dof-dtm-condo",
    "dataset_ids": ["dtm-condo-2026-07"],
    "retrieved_at": "2026-09-06T00:00:00Z",
    "mixed_substrate": {
        "lot_facts_substrate": "analyzed_base_lot",
        "identity_facts_substrate": "entered_billing_lot",
        "note": (
            "The lot area and geometry describe the analyzed base lot; the "
            "PLUTO identity facts describe the entered billing lot."
        ),
    },
}


def _stamped_1_2_0_document() -> dict:
    """The committed conditional-draft fixture promoted to a 1.2.0 document that
    CARRIES the optional substrate_substitution stamp. evaluated_input.bbl stays
    the ENTERED billing BBL — the stamp alone carries entered-vs-analyzed."""
    doc = _load(BASE_VALID)
    doc["contract_version"] = "1.2.0"
    doc["evaluated_input"]["bbl"] = SUBSTRATE_SUBSTITUTION_BLOCK["entered_bbl"]
    doc["substrate_substitution"] = json.loads(json.dumps(SUBSTRATE_SUBSTITUTION_BLOCK))
    return doc


def test_m5t058_contract_version_enum_admits_1_2_0_additively() -> None:
    """1.2.0 is appended, not substituted: the closed enum is exactly the three
    published rule_evaluation versions."""
    schema = _load(RULE_EVAL_SCHEMA)
    assert schema["properties"]["contract_version"]["enum"] == ["1.0.0", "1.1.0", "1.2.0"]
    # substrate_substitution is OPTIONAL — never added to the required list.
    assert "substrate_substitution" not in schema["required"]
    assert "substrate_substitution" in schema["properties"]


def test_m5t058_stamped_1_2_0_document_round_trips() -> None:
    """AS-1/AS-5: a 1.2.0 document carrying the substrate_substitution stamp
    validates, and the block survives a JSON round-trip byte-for-byte (every
    field preserved, entered_bbl == evaluated_input.bbl)."""
    doc = _stamped_1_2_0_document()
    _validator().validate(doc)  # raises on failure
    round_tripped = json.loads(json.dumps(doc))
    assert round_tripped["substrate_substitution"] == SUBSTRATE_SUBSTITUTION_BLOCK
    assert (
        round_tripped["substrate_substitution"]["entered_bbl"]
        == round_tripped["evaluated_input"]["bbl"]
    )
    # Both schema copies admit the identical document (byte-identity proven
    # separately; here the runtime bundle validates the same instance).
    bundle_schema = _load(BUNDLE_DIR / "rule_evaluation.schema.json")
    jsonschema.Draft202012Validator(bundle_schema, registry=_registry()).validate(doc)


def test_m5t058_optional_block_absent_still_validates_at_1_2_0() -> None:
    """Optional-block absence: a 1.2.0 document that OMITS the block validates
    (the serializer emits it only on the substituted path)."""
    doc = _load(BASE_VALID)
    doc["contract_version"] = "1.2.0"
    assert "substrate_substitution" not in doc
    _validator().validate(doc)


def test_m5t058_old_documents_stay_valid_without_the_block() -> None:
    """Old-document validity: 1.0.0 and 1.1.0 documents with no block remain
    valid — the additive block and enum member never became required."""
    for version in ("1.0.0", "1.1.0"):
        doc = _load(BASE_VALID)
        doc["contract_version"] = version
        assert "substrate_substitution" not in doc
        _validator().validate(doc)


def test_m5t058_substrate_substitution_is_a_closed_object() -> None:
    """Closed object shapes: an unexpected key anywhere in the block (top level
    OR the nested mixed_substrate) is rejected (additionalProperties:false)."""
    top = _stamped_1_2_0_document()
    top["substrate_substitution"]["unexpected_key"] = "x"
    top_messages = " ".join(e.message for e in _validator().iter_errors(top))
    assert "unexpected_key" in top_messages and "dditional" in top_messages

    nested = _stamped_1_2_0_document()
    nested["substrate_substitution"]["mixed_substrate"]["unexpected_key"] = "x"
    nested_messages = " ".join(e.message for e in _validator().iter_errors(nested))
    assert "unexpected_key" in nested_messages and "dditional" in nested_messages


def test_m5t058_substrate_substitution_required_fields_enforced() -> None:
    """Every documented stamp field is required; removing any one fails
    validation for its stated defect."""
    for field in (
        "entered_bbl",
        "analyzed_bbl",
        "note",
        "condo_key",
        "resolution_path",
        "source_id",
        "dataset_ids",
        "retrieved_at",
        "mixed_substrate",
    ):
        doc = _stamped_1_2_0_document()
        del doc["substrate_substitution"][field]
        errors = list(_validator().iter_errors(doc))
        assert errors, f"removing substrate_substitution.{field} should fail validation"
        assert any("required" in e.message and field in e.message for e in errors), field


def test_m5t058_fail_safe_reason_admits_condo_base_lot_unresolved() -> None:
    """New refusal reason: condo_base_lot_unresolved is admitted, and a fail-safe
    document naming it validates with NO substitution stamp (a multi-lot /
    unresolved outcome exposes no single analyzed lot to stamp)."""
    schema = _load(RULE_EVAL_SCHEMA)
    enum = next(
        branch["enum"]
        for branch in schema["properties"]["fail_safe_reason"]["anyOf"]
        if "enum" in branch
    )
    assert "condo_base_lot_unresolved" in enum

    doc = _load(BASE_FAIL_SAFE)
    doc["contract_version"] = "1.2.0"
    doc["fail_safe_reason"] = "condo_base_lot_unresolved"
    assert "substrate_substitution" not in doc
    _validator().validate(doc)


def test_m5t058_unknown_fail_safe_reason_rejected() -> None:
    doc = _load(BASE_FAIL_SAFE)
    doc["fail_safe_reason"] = "condo_substrate_missing"
    assert list(_validator().iter_errors(doc)), (
        "an undocumented fail_safe_reason must be rejected"
    )


def test_m5t058_contract_version_outside_enum_rejected() -> None:
    """The rule_evaluation contract_version enum is closed at 1.2.0: 1.3.0 (a
    property_profile version) is NOT a rule_evaluation contract version."""
    doc = _stamped_1_2_0_document()
    doc["contract_version"] = "1.3.0"
    assert list(_validator().iter_errors(doc))
