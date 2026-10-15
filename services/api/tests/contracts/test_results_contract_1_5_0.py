"""Results contract 1.5.0 (task M5-T164): additive rear-yard, envelope, illustrative
placement, input-facts and area-allocation blocks, plus the version sets.

1.5.0 is a strict superset of 1.4.0. The new blocks are OPTIONAL and additive, so every
valid 1.0.0-1.4.0 document stays valid; a document carrying any 1.5.0 block must declare
1.5.0 (the schema's reverse version binding). Two cross-key rules the schema cannot express
run in app.contracts.results_way_rules for 1.5.0 as the value-state way rule does for
1.3.0/1.4.0:

  * area_allocation.fitted may be true ONLY when the building's placement is placed;
  * area_allocation apartment + other = total within the two-decimal display rounding.

These tests run the new valid and invalid fixtures through BOTH results validators and the
bare schema, prove the two schema copies are byte-identical, prove the quantity-basis enum
equals QUANTITY_BASES, prove each new valid fixture is the journey fixture plus only the new
blocks, and prove the new way rules fire on 1.5.0 while 1.3.0/1.4.0 behaviour is unchanged.
Documents are built from committed fixtures loaded read-only; no fixture file is changed.
"""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

from app.contracts.results_way_rules import (
    CONTRACT_VERSIONS_WITH_WAY_LAYER,
    WayRuleViolation,
    results_way_violations,
)
from app.contracts.study_contracts import (
    FIXTURE_ONLY_KEY,
    StudyContractError,
    validate_study_contract_document,
)
from app.contracts.study_contracts import (
    validate_results_document as study_validate_results_document,
)
from app.scenario.three_answers.contract import ResultsContractError
from app.scenario.three_answers.contract import (
    validate_results_document as engine_validate_results_document,
)

# services/api/tests/contracts/test_*.py -> parents[4] is the repo root.
REPO_ROOT = Path(__file__).resolve().parents[4]
RESULTS_VALID = REPO_ROOT / "packages" / "contracts" / "fixtures" / "valid" / "results"
RESULTS_INVALID = REPO_ROOT / "packages" / "contracts" / "fixtures" / "invalid" / "results"
PRIMARY_SCHEMA = REPO_ROOT / "packages" / "contracts" / "schemas" / "v1" / "results.schema.json"
API_SCHEMA = (
    REPO_ROOT / "services" / "api" / "app" / "_contract_schemas" / "v1" / "results.schema.json"
)

JOURNEY = RESULTS_VALID / "recorded_215_16_northern_journey.json"
REAR_YARD = RESULTS_VALID / "synthetic_rear_yard_constraints_contract_1_5_0.json"
PLACED = RESULTS_VALID / "synthetic_placed_building_contract_1_5_0.json"
NEW_VALID = (REAR_YARD, PLACED)

INVALID_1_5_0 = sorted(RESULTS_INVALID.glob("*_contract_1_5_0.json"))

# (validator, its error type) - the two validators results documents pass through.
VALIDATORS = (
    pytest.param(study_validate_results_document, StudyContractError, id="study_contracts"),
    pytest.param(engine_validate_results_document, ResultsContractError, id="three_answers"),
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _quantity_bases_from_tool() -> set[str]:
    """The authoritative nine bases, read from tools/research_record_check.py (stdlib-only,
    __main__-guarded, so importing it has no side effects)."""
    path = REPO_ROOT / "tools" / "research_record_check.py"
    spec = importlib.util.spec_from_file_location("research_record_check_m5t164", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return set(module.QUANTITY_BASES)


# ---------------------------------------------------------------------------
# S6: version sets, schema-copy identity, and the version string.
# ---------------------------------------------------------------------------


def test_both_schema_copies_are_byte_identical() -> None:
    assert PRIMARY_SCHEMA.read_bytes() == API_SCHEMA.read_bytes()


def test_contract_version_enum_has_1_5_0() -> None:
    schema = _load(PRIMARY_SCHEMA)
    assert "1.5.0" in schema["properties"]["contract_version"]["enum"]


def test_way_layer_version_set_has_1_5_0() -> None:
    assert "1.5.0" in CONTRACT_VERSIONS_WITH_WAY_LAYER
    assert {"1.3.0", "1.4.0"} <= CONTRACT_VERSIONS_WITH_WAY_LAYER  # unchanged


def test_new_valid_fixtures_declare_1_5_0() -> None:
    for path in NEW_VALID:
        assert _load(path)["contract_version"] == "1.5.0"


# ---------------------------------------------------------------------------
# S5: the quantity-basis enum is exactly the nine QUANTITY_BASES.
# ---------------------------------------------------------------------------


def test_quantity_basis_enum_equals_QUANTITY_BASES() -> None:
    schema = _load(PRIMARY_SCHEMA)
    enum = schema["$defs"]["quantity_basis"]["enum"]
    assert len(enum) == len(set(enum))  # no duplicates
    assert set(enum) == _quantity_bases_from_tool()
    # The 1.5.0 fact/measure blocks all read the single quantity_basis def.
    ref = "#/$defs/quantity_basis"
    assert schema["$defs"]["input_fact"]["properties"]["basis"]["$ref"] == ref
    assert schema["$defs"]["rear_yard_input"]["properties"]["basis"]["$ref"] == ref


# ---------------------------------------------------------------------------
# S1 / S2: every valid fixture (existing and the two new) is accepted by both.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("validate, _error", VALIDATORS)
@pytest.mark.parametrize("fixture", sorted(RESULTS_VALID.glob("*.json")), ids=lambda p: p.name)
def test_every_valid_fixture_is_accepted_by_both(validate, _error, fixture: Path) -> None:
    validate(_load(fixture))


# ---------------------------------------------------------------------------
# S3 / S4 / S5 / S13: every new invalid 1.5.0 fixture is refused by the bare
# schema AND by both validators, for its documented defect.
# ---------------------------------------------------------------------------


def test_there_are_eight_new_invalid_fixtures() -> None:
    assert len(INVALID_1_5_0) == 8


@pytest.mark.parametrize("fixture", INVALID_1_5_0, ids=lambda p: p.name)
def test_invalid_fixture_documents_its_defect(fixture: Path) -> None:
    assert FIXTURE_ONLY_KEY in _load(fixture), "invalid fixture must document its defect"


@pytest.mark.parametrize("validate, error", VALIDATORS)
@pytest.mark.parametrize("fixture", INVALID_1_5_0, ids=lambda p: p.name)
def test_every_new_invalid_fixture_is_refused_by_both(validate, error, fixture: Path) -> None:
    instance = _load(fixture)
    instance.pop(FIXTURE_ONLY_KEY)  # refuse on the real schema defect, not the annotation
    with pytest.raises(error):
        validate(instance)


# ---------------------------------------------------------------------------
# S9: each new valid fixture is the journey fixture plus only the new blocks.
# ---------------------------------------------------------------------------

_V1_5_0_TOP_BLOCKS = ("rear_yard", "envelope_rows", "input_facts")


def _strip_1_5_0_blocks(doc: dict) -> dict:
    """Return the document with every 1.5.0 block removed."""
    d = copy.deepcopy(doc)
    for key in _V1_5_0_TOP_BLOCKS:
        d.pop(key, None)
    # M5-T172: the placement emission populates the floor-by-floor table with the drawn plates (it
    # is empty on a 1.4.0 / unplaced document), so strip it for the shared-1.4.0-core comparison.
    d["floor_by_floor"] = []
    if isinstance(d.get("geometry"), dict):
        d["geometry"].pop("constraint_lines", None)
        # M5-T172: the placement emission draws the floor_plates layer (not_available before); the
        # drawn layer is a 1.5.0 effect, so drop the whole layer for the 1.4.0-core comparison.
        d["geometry"].pop("floor_plates", None)
    for alt in d.get("building_alternatives", []) or []:
        if isinstance(alt, dict):
            alt.pop("placement", None)
            alt.pop("area_allocation", None)
            # M5-T170: the 1.5.0 envelope emission gates the "The street wall" not-checked line out
            # (page 6 then agrees with the applied street-wall reading on pages 3 and 8); M5-T172:
            # the placement emission drops "Where the plan sits on the lot" (the footprint now
            # sits on the lot). Both are 1.5.0 effects - normalize for the 1.4.0-core compare.
            if isinstance(alt.get("not_checked"), list):
                alt["not_checked"] = [
                    x for x in alt["not_checked"]
                    if x not in ("The street wall", "Where the plan sits on the lot")
                ]
            # M5-T172: the placement emission drops the fit note's "where the building sits on
            # the lot" clause (the footprint now sits on the lot); normalize for the 1.4.0 compare.
            if isinstance(alt.get("fit_note"), str):
                alt["fit_note"] = alt["fit_note"].replace(
                    "where the building sits on the lot and the other items",
                    "the other items",
                )
    # M5-T170: the 1.5.0 envelope emission reconciles the setback value state to the applied
    # envelope reading (the two setback emitters must agree); strip it for the 1.4.0-core compare.
    states = (d.get("answers", {}).get("permitted_envelope", {}) or {}).get("value_states")
    if isinstance(states, dict):
        states.pop("setback_above_base", None)
    return d


@pytest.mark.parametrize("fixture", NEW_VALID, ids=lambda p: p.name)
def test_new_valid_fixture_is_journey_plus_only_the_new_blocks(fixture: Path) -> None:
    journey = _load(JOURNEY)
    doc = _load(fixture)
    assert doc["contract_version"] == "1.5.0"
    # M5-T167: the journey now declares 1.5.0 too - its own ZR 23-344 rear_yard block and
    # input_facts were emitted from the corrected engine, so it is no longer a 1.4.0 baseline.
    assert journey["contract_version"] == "1.5.0"
    assert any(
        key in doc for key in (*_V1_5_0_TOP_BLOCKS, "building_alternatives")
    ), "the fixture must carry at least one 1.5.0 block"
    # Strip the 1.5.0 blocks from BOTH and compare the shared 1.4.0 core: the synthetic is the
    # journey plus only the new blocks, so once both are stripped their 1.4.0 cores are equal.
    stripped = _strip_1_5_0_blocks(doc)
    journey_core = _strip_1_5_0_blocks(journey)
    for identity in ("results_id", "study_id", "option_id", "computed_at"):
        stripped[identity] = journey_core[identity]
    assert stripped == journey_core


# ---------------------------------------------------------------------------
# S6: a document carrying a 1.5.0 block must declare 1.5.0 (the version binding).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("validate, error", VALIDATORS)
@pytest.mark.parametrize("fixture", NEW_VALID, ids=lambda p: p.name)
def test_a_1_5_0_block_declared_as_1_4_0_is_refused(validate, error, fixture: Path) -> None:
    doc = _load(fixture)
    doc["contract_version"] = "1.4.0"
    with pytest.raises(error):
        validate(doc)


# ---------------------------------------------------------------------------
# S12: the two area-allocation way rules fire on a 1.5.0 document (both
# validators refuse; the pure rule reports the breach). These are the
# mutation-sensitive tests: removing "1.5.0" from CONTRACT_VERSIONS_WITH_WAY_LAYER
# makes the pure rule silent, so the validators accept and these fail.
# ---------------------------------------------------------------------------


def _fitted_without_placed_doc() -> dict:
    """The placed fixture, re-pointed to a WITHHELD placement while the allocation stays
    fitted: schema-valid, but the fitted-only-when-placed way rule is broken."""
    doc = _load(PLACED)
    alt = doc["building_alternatives"][0]
    assert alt["area_allocation"]["fitted"] is True
    alt["placement"] = {
        "status": "withheld",
        "label": "Illustrative",
        "method": alt["placement"]["method"],
        "basis": alt["placement"]["basis"],
        "measure": alt["placement"]["measure"],
        "conversion_statement": alt["placement"]["conversion_statement"],
    }
    return doc


def _total_mismatch_doc() -> dict:
    """The placed fixture with apartment + other no longer equal to total: schema-valid, but
    the sum way rule is broken. ``other`` is moved (not ``apartment`` or ``total``) so the
    apartment still equals the share applied to the total - only the sum rule breaks, never the
    share rule (DB-248), so this isolates ``allocation_total_mismatch``."""
    doc = _load(PLACED)
    doc["building_alternatives"][0]["area_allocation"]["other_area_sqft"] += 1000.0
    return doc


def test_bare_schema_accepts_the_two_way_broken_documents() -> None:
    # The schema cannot express the cross-key rules, so it accepts both; the way rule refuses.
    for doc in (_fitted_without_placed_doc(), _total_mismatch_doc()):
        validate_study_contract_document("results", doc)
        assert results_way_violations(doc)


@pytest.mark.parametrize("validate, error", VALIDATORS)
def test_S12_fitted_without_placement_is_refused_by_both(validate, error) -> None:
    with pytest.raises(error):
        validate(_fitted_without_placed_doc())


@pytest.mark.parametrize("validate, error", VALIDATORS)
def test_S12_area_total_mismatch_is_refused_by_both(validate, error) -> None:
    with pytest.raises(error):
        validate(_total_mismatch_doc())


def test_pure_rule_flags_fitted_without_placement() -> None:
    breaches = results_way_violations(_fitted_without_placed_doc())
    assert [(b.answer, b.key, b.rule) for b in breaches] == [
        ("building_alternatives", "B", "allocation_fitted_without_placement")
    ]
    assert isinstance(breaches[0], WayRuleViolation)


def test_pure_rule_flags_area_total_mismatch() -> None:
    rules = {b.rule for b in results_way_violations(_total_mismatch_doc())}
    assert rules == {"allocation_total_mismatch"}


def test_pure_rule_accepts_the_two_well_formed_new_fixtures() -> None:
    for path in NEW_VALID:
        assert results_way_violations(_load(path)) == []


# ---------------------------------------------------------------------------
# S12: 1.3.0 / 1.4.0 behaviour is unchanged. A real 1.4.0 document carries no
# area_allocation, so the new rule is a no-op; below the way-layer set the rule
# does nothing even for a document that would break it.
# ---------------------------------------------------------------------------


def test_the_1_4_0_building_alternatives_fixture_has_no_way_breach() -> None:
    fixture = RESULTS_VALID / "synthetic_building_alternatives_contract_1_4_0.json"
    doc = _load(fixture)
    assert doc["contract_version"] == "1.4.0"
    assert results_way_violations(doc) == []


def test_area_rule_is_version_gated_below_the_way_layer_set() -> None:
    # A document that WOULD break the area rule, declared at 1.2.0, yields no breach: the rule
    # is version-gated (the version binding is the schema's job, not this rule's).
    doc = _fitted_without_placed_doc()
    doc["contract_version"] = "1.2.0"
    assert results_way_violations(doc) == []


def test_pure_rule_returns_empty_for_a_non_mapping() -> None:
    assert results_way_violations("not a document") == []
    assert results_way_violations({"contract_version": "1.5.0"}) == []
