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

from app.scenario.contract import ScenarioContractError, validate_scenario_document

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
# [ORCH-CORRECTED per contracts-CI] Fixtures whose defect the JSON Schema provably
# CANNOT express (ring closure, non-self-intersection) live in a THIRD directory:
# the contracts CI job's convention is that everything under fixtures/invalid/
# must fail SCHEMA validation, and these are schema-valid by construction (the CI
# validator walks only valid/ and invalid/, so this class is asserted here, at the
# validator layer where the defect is actually caught).
SEMANTICALLY_INVALID_FIXTURES = sorted(
    (FIXTURE_ROOT / "semantically_invalid" / "scenario").glob("*.json")
)


def test_there_are_the_required_fixtures():
    assert len(VALID_FIXTURES) >= 4, (
        "need >=4 valid fixtures (preliminary, unsupported, conflict, professional review)"
    )
    assert len(INVALID_FIXTURES) >= 3, (
        "need >=3 invalid fixtures (verified, embedded profile, missing field)"
    )
    assert len(SEMANTICALLY_INVALID_FIXTURES) == 2, (
        "need exactly the two schema-valid geometry fixtures (open ring, "
        "self-intersecting) in semantically_invalid/scenario/"
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


@pytest.mark.parametrize(
    "fixture", INVALID_FIXTURES + SEMANTICALLY_INVALID_FIXTURES, ids=lambda p: p.name
)
def test_invalid_fixture_rejected(fixture: Path):
    """Every invalid fixture is refused by the production contract gate.

    Invalid fixtures split by WHERE the defect is caught, and live in the
    directory matching that layer:

    * STRUCTURAL (fixtures/invalid/scenario/) - a defect the JSON Schema
      expresses and rejects directly: a 'verified' coverage_status, an embedded
      profile key, a missing required field, and (M5-T048) a non-positive
      floor_to_floor_ft, which the schema now rejects via ``exclusiveMinimum: 0``
      on proposed_level.floor_to_floor_ft. The contracts CI job independently
      requires every fixture in this directory to FAIL schema validation.
    * SEMANTIC (fixtures/semantically_invalid/scenario/) - a geometry invariant
      a JSON Schema provably cannot state: an unclosed or self-intersecting
      proposed_massing outline. These fixtures are STRUCTURALLY schema-valid and
      are refused only by app.scenario.proposal through
      validate_scenario_document (the CI schema job deliberately does not walk
      this directory).

    Asserting the whole contract gate (schema + strict-JSON guard +
    proposed_massing semantics) covers both classes; the per-fixture tests below
    pin each defect at its exact layer.
    """
    instance = _load(fixture)
    assert "_expected_failure" in instance, "invalid fixture must document its defect"
    with pytest.raises(ScenarioContractError):
        validate_scenario_document(instance)


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


# The proposed_massing GEOMETRY invalid fixtures (M5-T048) carry a SEMANTIC
# defect the JSON Schema provably cannot express (ring closure, non-self-
# intersection): each is structurally schema-valid yet refused by
# validate_scenario_document at the exact proposed_massing field it documents.
# They live under fixtures/semantically_invalid/scenario/ (NOT invalid/), because
# the contracts CI job requires everything under invalid/ to fail SCHEMA
# validation - which these deliberately do not.
# The negative-height fixture is NOT in this set: JSON Schema CAN express strict
# positivity (exclusiveMinimum: 0), so it fails schema validation directly - see
# test_proposed_massing_negative_height_fixture_fails_schema_validation below.
PROPOSED_MASSING_GEOMETRY_INVALID_FIXTURES = {
    "proposed_massing_open_ring.json": "proposed_massing.outline",
    "proposed_massing_self_intersecting.json": "proposed_massing.outline",
}


@pytest.mark.parametrize(
    ("fixture_name", "location"),
    sorted(PROPOSED_MASSING_GEOMETRY_INVALID_FIXTURES.items()),
    ids=lambda item: item if isinstance(item, str) else "",
)
def test_proposed_massing_geometry_fixture_is_schema_valid_but_semantically_refused(
    fixture_name: str, location: str
):
    instance = _load(FIXTURE_ROOT / "semantically_invalid" / "scenario" / fixture_name)
    # STRUCTURAL: the JSON Schema accepts the document (the defect is a geometry
    # invariant a JSON Schema cannot state).
    assert not list(_validator().iter_errors(instance)), (
        f"{fixture_name} should be structurally schema-valid; its defect is a "
        "geometry invariant the schema cannot express"
    )
    # SEMANTIC: the contract gate refuses it, naming the exact field.
    with pytest.raises(ScenarioContractError) as exc:
        validate_scenario_document(instance)
    assert exc.value.location == location


def test_proposed_massing_negative_height_fixture_fails_schema_validation():
    """The negative floor-to-floor height fixture is refused at the SCHEMA layer.

    JSON Schema CAN express strict positivity - proposed_level.floor_to_floor_ft
    carries ``exclusiveMinimum: 0`` - so this fixture (floor_to_floor_ft = -10.0)
    fails JSON Schema validation directly, independent of the semantic module.
    This is the schema-level rejection coverage AS-3 asks for on the height case;
    ring closure and non-self-intersection remain inexpressible in JSON Schema
    and are covered through the semantic gate above. The whole contract gate
    (which runs schema validation) refuses it too.
    """
    instance = _load(
        FIXTURE_ROOT / "invalid" / "scenario" / "proposed_massing_negative_height.json"
    )
    messages = " | ".join(e.message for e in _validator().iter_errors(instance))
    assert messages, "negative-height fixture must fail schema validation"
    assert "minimum" in messages.lower()
    with pytest.raises(ScenarioContractError):
        validate_scenario_document(instance)


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


# ---------------------------------------------------------------------------
# C1 shape update (M5-T017, D-041): the new required, fully-specified, closed
# unused_draft_zoning_floor_area key (mirrored byte-identically into the runtime
# bundle by test_runtime_bundle_copy_is_byte_identical_to_canonical above).
# ---------------------------------------------------------------------------


def test_unused_floor_area_is_required_fully_specified_and_closed():
    schema = _load(SCENARIO_SCHEMA)
    assert "unused_draft_zoning_floor_area" in schema["required"]
    assert schema["properties"]["unused_draft_zoning_floor_area"] == {
        "$ref": "#/$defs/unused_draft_zoning_floor_area"
    }
    section_def = schema["$defs"]["unused_draft_zoning_floor_area"]
    assert section_def["type"] == "object"
    assert section_def["additionalProperties"] is False
    # State + not-computable reason enums are fully specified.
    assert set(section_def["properties"]["state"]["enum"]) == {
        "computed",
        "over_built",
        "not_computable",
    }
    reason = section_def["properties"]["not_computable_reason"]["anyOf"][0]["enum"]
    assert set(reason) == {
        "missing_existing_building_area",
        "existing_building_area_unusable",
        "no_draft_far_cap",
    }
    # The inputs sub-object is closed too.
    assert schema["$defs"]["unused_floor_area_inputs"]["additionalProperties"] is False


@pytest.mark.parametrize("fixture", VALID_FIXTURES, ids=lambda p: p.name)
def test_valid_fixture_carries_unused_floor_area_section(fixture: Path):
    instance = _load(fixture)
    section = instance["unused_draft_zoning_floor_area"]
    assert section["label"]
    assert section["state"] in {"computed", "over_built", "not_computable"}


def test_property_profile_and_rule_evaluation_contracts_untouched():
    profile = _load(SCHEMA_DIR / "property_profile.schema.json")
    assert profile["properties"]["profile_version"]["properties"]["contract_version"][
        "enum"
    ] == ["1.0.0", "1.1.0", "1.2.0", "1.3.0", "1.4.0"]
    rule_eval = _load(SCHEMA_DIR / "rule_evaluation.schema.json")
    # [ORCH-CORRECTED per api CI on f954aa59] M5-T037 is the accepted contract
    # task that appends 1.1.0 (optional wide_street block); this guard admits
    # exactly the sanctioned enum, as it did for each property_profile bump.
    # [ORCH-CORRECTED at the M5-T058 harvest] M5-T058 is the sanctioning
    # contract task that appends 1.2.0 (substitution stamp); guard updated by
    # the orchestrator as the routed out-of-scope consumer fix (M5-T037
    # precedent above) — the sweep caught this file pinning the pre-1.2.0 enum.
    assert rule_eval["properties"]["contract_version"]["enum"] == [
        "1.0.0",
        "1.1.0",
        "1.2.0",
    ]


# ---------------------------------------------------------------------------
# Scenario contract 1.1.0 (task M5-T048, phase B0, D-076): the OPTIONAL
# proposed_massing INPUT CLASS - version selection, unchanged-legacy behavior,
# and the STRUCTURAL vs SEMANTIC validation split.
#
# STRUCTURAL vs SEMANTIC (documented distinction). JSON Schema fixes the shape -
# key presence, types, the srid=[2263] and kind=['proposed'] enums,
# additionalProperties:false, AND strict positivity of floor_to_floor_ft
# (exclusiveMinimum: 0). The remaining invariants split two ways:
#
#   (A) Expressible in JSON Schema but enforced in app.scenario.proposal BY
#       DESIGN, not by necessity: NYC EPSG:2263 per-coordinate bounds
#       (prefixItems + minimum/maximum), the sane floor-to-floor upper bound
#       (maximum), and the DB-013 count ceilings (maxItems on vertices/levels/
#       walls; maximum/minimum on floor_count). The module owns them so every
#       refusal is a TYPED ProposedMassingError naming the exact field and the
#       numeric bounds live once as MAX_*/NYC_2263_* constants (no schema/code
#       duplication across the two byte-identical copies). It re-checks
#       positivity as defense in depth.
#   (B) NOT expressible in JSON Schema - genuine cross-value/geometry invariants:
#       ring closure (first==last, cross-element equality), non-self-intersection
#       (a predicate over all edges), distinct non-closing vertices (partial-
#       array uniqueness), level-index contiguity {0..N-1} (a set tied to the
#       array length), and wall start/end indices in range of the outline vertex
#       count and distinct (a cross-field reference). These REQUIRE the module.
#       (Height finiteness is a third case: no real JSON document can carry
#       NaN/Infinity, so the schema never sees it; the module's finiteness check
#       guards in-memory floats as defense in depth.)
#
# validate_scenario_document surfaces each (A)/(B) defect as a
# ScenarioContractError naming the exact field. A document carrying a (B) defect
# is STRUCTURALLY schema-valid but SEMANTICALLY refused.
# ---------------------------------------------------------------------------

BASE_1_0_0_DOC = FIXTURE_ROOT / "valid" / "scenario" / "preliminary_r5_cap.json"

# A base X/Y comfortably inside the generous NYC EPSG:2263 unit-sanity bounds.
_PX, _PY = 986000.0, 200000.0


def _valid_proposed_block() -> dict:
    """A minimal, fully-valid proposed_massing block (fresh copy each call)."""
    return {
        "outline": {
            "srid": 2263,
            "vertices": [
                [_PX, _PY],
                [_PX + 100.0, _PY],
                [_PX + 100.0, _PY + 80.0],
                [_PX, _PY + 80.0],
                [_PX, _PY],
            ],
        },
        "levels": [
            {"level_index": 0, "floor_count": 1, "floor_to_floor_ft": 12.0},
            {"level_index": 1, "floor_count": 4, "floor_to_floor_ft": 10.0},
        ],
        "exterior_walls": [
            {"id": "south", "start_vertex_index": 0, "end_vertex_index": 1},
            {"id": "east", "start_vertex_index": 1, "end_vertex_index": 2},
        ],
        "provenance": {
            "author": "architect@example.com",
            "kind": "proposed",
            "editor_version": "proposal-editor/0.1.0",
            "parent_scenario_id": None,
        },
    }


def _doc_with_block(*, contract_version: str, block: dict) -> dict:
    """The known-good 1.0.0 fixture reparsed fresh, restamped, plus a block."""
    doc = _load(BASE_1_0_0_DOC)
    doc["contract_version"] = contract_version
    doc["proposed_massing"] = block
    return doc


# --- schema shape ----------------------------------------------------------


def test_contract_version_enum_admits_exactly_1_0_0_and_1_1_0():
    for schema_path in (SCENARIO_SCHEMA, BUNDLE_DIR / "scenario.schema.json"):
        enum = _load(schema_path)["properties"]["contract_version"]["enum"]
        assert enum == ["1.0.0", "1.1.0"]


def test_proposed_massing_is_optional_not_required():
    schema = _load(SCENARIO_SCHEMA)
    assert "proposed_massing" in schema["properties"]
    assert "proposed_massing" not in schema["required"]


def test_proposed_massing_def_structural_shape():
    defs = _load(SCENARIO_SCHEMA)["$defs"]
    block = defs["proposed_massing"]
    assert block["additionalProperties"] is False
    assert set(block["required"]) == {"outline", "levels", "exterior_walls", "provenance"}
    assert defs["proposed_outline"]["properties"]["srid"]["enum"] == [2263]
    assert defs["proposed_provenance"]["properties"]["kind"]["enum"] == ["proposed"]


# --- version selection + threading -----------------------------------------


def test_legacy_1_0_0_document_without_block_validates_unchanged():
    doc = _load(BASE_1_0_0_DOC)
    assert "proposed_massing" not in doc
    assert doc["contract_version"] == "1.0.0"
    validate_scenario_document(doc)  # no raise: the block path is inert on 1.0.0


def test_valid_block_on_1_1_0_document_validates():
    doc = _doc_with_block(contract_version="1.1.0", block=_valid_proposed_block())
    validate_scenario_document(doc)  # no raise


def test_block_present_but_1_0_0_version_is_refused():
    doc = _doc_with_block(contract_version="1.0.0", block=_valid_proposed_block())
    with pytest.raises(ScenarioContractError) as exc:
        validate_scenario_document(doc)
    assert exc.value.location == "contract_version"


# --- structural (schema) vs semantic (module) split ------------------------


def test_open_ring_block_is_structurally_valid_but_semantically_refused():
    block = _valid_proposed_block()
    block["outline"]["vertices"] = block["outline"]["vertices"][:-1]  # drop closing vertex
    doc = _doc_with_block(contract_version="1.1.0", block=block)
    # JSON Schema CANNOT express ring closure: the document is structurally valid.
    assert not list(_validator().iter_errors(doc))
    with pytest.raises(ScenarioContractError) as exc:
        validate_scenario_document(doc)
    assert exc.value.location == "proposed_massing.outline"


def test_self_intersecting_block_semantically_refused():
    block = _valid_proposed_block()
    block["outline"]["vertices"] = [
        [_PX, _PY],
        [_PX + 10.0, _PY + 10.0],
        [_PX + 10.0, _PY],
        [_PX, _PY + 10.0],
        [_PX, _PY],
    ]
    doc = _doc_with_block(contract_version="1.1.0", block=block)
    assert not list(_validator().iter_errors(doc))
    with pytest.raises(ScenarioContractError) as exc:
        validate_scenario_document(doc)
    assert exc.value.location == "proposed_massing.outline"


def test_level_count_mismatch_block_semantically_refused():
    block = _valid_proposed_block()
    block["levels"][1]["level_index"] = 5  # {0, 5} with 2 records -> not {0, 1}
    doc = _doc_with_block(contract_version="1.1.0", block=block)
    assert not list(_validator().iter_errors(doc))
    with pytest.raises(ScenarioContractError) as exc:
        validate_scenario_document(doc)
    assert exc.value.location == "proposed_massing.levels"


def test_non_finite_height_block_refused_by_json_safety_guard():
    block = _valid_proposed_block()
    block["levels"][0]["floor_to_floor_ft"] = float("inf")
    doc = _doc_with_block(contract_version="1.1.0", block=block)
    # A non-finite value can never be strict-JSON serialized; the NaN/Infinity
    # guard fires first, refusing the document at the root.
    with pytest.raises(ScenarioContractError) as exc:
        validate_scenario_document(doc)
    assert exc.value.location == "<root>"


# --- schema-layer structural refusals (srid + kind) ------------------------


def test_schema_rejects_outline_srid_not_2263():
    block = _valid_proposed_block()
    block["outline"]["srid"] = 4326
    doc = _doc_with_block(contract_version="1.1.0", block=block)
    messages = " ".join(e.message for e in _validator().iter_errors(doc))
    assert "2263" in messages


def test_schema_rejects_provenance_kind_not_proposed():
    block = _valid_proposed_block()
    block["provenance"]["kind"] = "record"
    doc = _doc_with_block(contract_version="1.1.0", block=block)
    messages = " ".join(e.message for e in _validator().iter_errors(doc))
    assert "proposed" in messages


# --- additive preservation: legacy docs unaffected by the bump -------------


@pytest.mark.parametrize("fixture", VALID_FIXTURES, ids=lambda p: p.name)
def test_existing_valid_fixtures_pass_server_validation(fixture: Path):
    validate_scenario_document(_load(fixture))
