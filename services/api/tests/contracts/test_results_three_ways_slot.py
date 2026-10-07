"""Results contract 1.3.0 three-ways slot (M5-T128, work order section 0 / D5).

Version 1.3.0 lets ONE value inside an answer carry which of the three ways of
the work order it appears in (docs/plans/R6B_RESULTS_CONNECTION_WORK_ORDER_2026-10-06.md
section 0 'How a result may appear'; D-090-R229/R255/R258/R268): settled,
conditional or withheld. It is STRICTLY ADDITIVE - nothing emits it yet. The slot is:

- an OPTIONAL ``value_states`` map on each AVAILABLE answer (floor_area_allowance,
  permitted_envelope, building_option), keyed by the answer value's key, each entry
  one of three closed ways (value_state): ``settled`` (no condition), ``conditional``
  (one or more named conditions, each with its kind, the assumption and what would
  settle it) or ``withheld`` (NO number; its label, reason, gap kind, what would
  resolve it and, where one applies, the law section);
- OPTIONAL ``resolved_by`` / ``gap_kind`` fields on a whole-answer not-available
  object (answer_not_available), without changing its present required fields.

These tests run the RUNTIME validator the engine uses (``validate_results_document``,
the byte-identical bundled schema), so a passing suite also proves the runtime copy
is in step (S8). They build every example document in the test from an existing valid
fixture loaded read-only; no fixture file is added, changed or removed.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from app.contracts.study_contracts import (
    FIXTURE_ONLY_KEY,
    StudyContractError,
    validate_results_document,
)

# services/api/tests/contracts/test_*.py -> parents[4] is the repo root.
REPO_ROOT = Path(__file__).resolve().parents[4]
RESULTS_VALID = REPO_ROOT / "packages" / "contracts" / "fixtures" / "valid" / "results"
RESULTS_INVALID = REPO_ROOT / "packages" / "contracts" / "fixtures" / "invalid" / "results"
BASE_FIXTURE = RESULTS_VALID / "synthetic_all_answers_available.json"
GENERATED_RESULTS_TS = REPO_ROOT / "packages" / "contracts" / "generated" / "results.ts"

PUBLISHED_PRE_1_3_0 = ("1.0.0", "1.1.0", "1.2.0")

# Keys of the permitted-envelope answer withheld in the 1.3.0 example (no number).
_WITHHELD_ENV_KEYS = {"max_lot_coverage", "setback_depth_above_base"}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _base_1_3_0() -> dict:
    """A well-formed 1.3.0 document built from the all-available fixture:

    - floor_area_allowance: one settled value, one conditional value (a recorded
      figure that another figure contradicts);
    - permitted_envelope: the three heights shown (settled / settled / conditional
      on the unchecked K20 conditions) beside two WITHHELD values (coverage =
      missing information; the setback above the base = work owed), each with no
      number in ``values``;
    - building_option: the whole answer withheld, carrying the 1.3.0 resolution
      fields (what would resolve it and that it is work owed).
    """
    doc = _load(BASE_FIXTURE)
    doc["contract_version"] = "1.3.0"

    doc["answers"]["floor_area_allowance"]["value_states"] = {
        "max_residential_far": {"way": "settled"},
        "max_residential_floor_area": {
            "way": "conditional",
            "conditions": [
                {
                    "kind": "contradicted_record",
                    "assumption": "If the recorded lot area of 10,075 sq ft is confirmed",
                    "settled_by": "A survey or deed dimensions",
                }
            ],
        },
    }

    env = doc["answers"]["permitted_envelope"]
    env["values"] = [v for v in env["values"] if v["key"] not in _WITHHELD_ENV_KEYS]
    env["value_states"] = {
        "min_base_height": {"way": "settled"},
        "max_base_height": {"way": "settled"},
        "max_building_height": {
            "way": "conditional",
            "conditions": [
                {
                    "kind": "unchecked_condition",
                    "assumption": (
                        "If none of the unchecked conditions (waterfront, airport "
                        "height, transit easement, near a district line) applies"
                    ),
                    "settled_by": "Capturing the governing law text and confirming each is absent",
                }
            ],
        },
        "setback_depth_above_base": {
            "way": "withheld",
            "label": "Setback above the base",
            "reason": "ZR 23-433 is captured but not built.",
            "gap_kind": "work_owed",
            "resolved_by": "Building the setback rule and a reference case.",
            "zr_sections": ["ZR 23-433"],
        },
        "max_lot_coverage": {
            "way": "withheld",
            "label": "Maximum lot coverage",
            "reason": (
                "The lot reaches 103.93 ft from the 215 Place street line, beyond the "
                "100 ft corner-coverage area; the ZR 12-10 corner definition is not captured."
            ),
            "gap_kind": "missing_information",
            "resolved_by": "Capturing the ZR 12-10 corner definition and reading the outline.",
            "zr_sections": ["ZR 23-362"],
        },
    }

    doc["answers"]["building_option"] = {
        "status": "not_available",
        "reason": "No building option is shown in this milestone.",
        "reason_kind": "rule_not_implemented",
        "resolved_by": "Building the building-option generator and a reference case.",
        "gap_kind": "work_owed",
    }
    return doc


# ---------------------------------------------------------------------------
# S1 / S2: strict additivity - every present fixture keeps its verdict.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture",
    sorted(RESULTS_VALID.glob("*.json")),
    ids=lambda p: p.name,
)
def test_every_valid_results_fixture_still_validates(fixture: Path) -> None:
    """S1: the 1.3.0 addition is strictly additive - no valid fixture had to change."""
    validate_results_document(_load(fixture))


@pytest.mark.parametrize(
    "fixture",
    sorted(RESULTS_INVALID.glob("*.json")),
    ids=lambda p: p.name,
)
def test_every_invalid_results_fixture_still_rejected(fixture: Path) -> None:
    """S2: every present invalid fixture stays invalid for its one stated defect."""
    instance = _load(fixture)
    assert FIXTURE_ONLY_KEY in instance, "invalid fixture must document its defect"
    instance.pop(FIXTURE_ONLY_KEY)
    with pytest.raises(StudyContractError):
        validate_results_document(instance)


# ---------------------------------------------------------------------------
# S3 (property e): a value can be withheld beside the shown values of an answer.
# ---------------------------------------------------------------------------


def test_withheld_value_sits_beside_shown_values() -> None:
    doc = _base_1_3_0()
    validate_results_document(doc)
    states = doc["answers"]["permitted_envelope"]["value_states"]
    shown_keys = {v["key"] for v in doc["answers"]["permitted_envelope"]["values"]}
    for key in _WITHHELD_ENV_KEYS:
        entry = states[key]
        assert entry["way"] == "withheld"
        assert "value" not in entry, "a withheld value carries no number"
        assert entry["label"] and entry["reason"] and entry["resolved_by"]
        assert entry["gap_kind"] in ("missing_information", "work_owed")
        assert key not in shown_keys, "a withheld key is not among the shown values"


def test_withheld_value_may_carry_its_law_section_or_omit_it() -> None:
    doc = _base_1_3_0()
    # zr_sections is optional on a withheld value.
    doc["answers"]["permitted_envelope"]["value_states"]["max_lot_coverage"].pop("zr_sections")
    validate_results_document(doc)


# ---------------------------------------------------------------------------
# S4 (property d): a conditional value names its assumptions; a settled one has none.
# ---------------------------------------------------------------------------


def test_conditional_value_names_its_assumptions() -> None:
    doc = _base_1_3_0()
    validate_results_document(doc)
    cond = doc["answers"]["floor_area_allowance"]["value_states"]["max_residential_floor_area"]
    assert cond["way"] == "conditional"
    assert len(cond["conditions"]) >= 1
    only = cond["conditions"][0]
    assert only["kind"] in ("user_statement", "contradicted_record", "unchecked_condition")
    assert only["assumption"] and only["settled_by"]


def test_conditional_without_a_condition_is_rejected() -> None:
    doc = _base_1_3_0()
    states = doc["answers"]["floor_area_allowance"]["value_states"]
    states["max_residential_floor_area"] = {"way": "conditional"}  # no conditions key
    with pytest.raises(StudyContractError):
        validate_results_document(doc)


def test_conditional_with_an_empty_condition_list_is_rejected() -> None:
    doc = _base_1_3_0()
    states = doc["answers"]["floor_area_allowance"]["value_states"]
    states["max_residential_floor_area"] = {"way": "conditional", "conditions": []}
    with pytest.raises(StudyContractError):
        validate_results_document(doc)


def test_settled_value_with_a_condition_is_rejected() -> None:
    doc = _base_1_3_0()
    states = doc["answers"]["floor_area_allowance"]["value_states"]
    good = states["max_residential_floor_area"]["conditions"]
    states["max_residential_far"] = {"way": "settled", "conditions": good}
    with pytest.raises(StudyContractError):
        validate_results_document(doc)
    # Reverting ONLY the stray condition makes the whole document valid again:
    # the condition on a settled value was the one and only defect.
    states["max_residential_far"] = {"way": "settled"}
    validate_results_document(doc)


# ---------------------------------------------------------------------------
# S5 (property c): in a 1.3.0 document no value is settled by silence.
# ---------------------------------------------------------------------------


def test_value_state_that_states_no_way_is_rejected() -> None:
    doc = _base_1_3_0()
    doc["answers"]["floor_area_allowance"]["value_states"]["max_residential_far"] = {}
    with pytest.raises(StudyContractError):
        validate_results_document(doc)


def test_available_answer_without_a_way_layer_is_rejected_at_1_3_0() -> None:
    doc = _base_1_3_0()
    del doc["answers"]["floor_area_allowance"]["value_states"]
    with pytest.raises(StudyContractError):
        validate_results_document(doc)
    # Restoring the way-layer makes the document valid -> its absence was the defect.
    doc["answers"]["floor_area_allowance"]["value_states"] = {
        "max_residential_far": {"way": "settled"},
        "max_residential_floor_area": {"way": "settled"},
    }
    validate_results_document(doc)


# ---------------------------------------------------------------------------
# S6 (property b): version binding both directions.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("stale", PUBLISHED_PRE_1_3_0)
def test_value_states_under_a_lower_version_is_rejected(stale: str) -> None:
    doc = _base_1_3_0()
    doc["contract_version"] = stale
    with pytest.raises(StudyContractError):
        validate_results_document(doc)


@pytest.mark.parametrize("version", PUBLISHED_PRE_1_3_0)
def test_a_document_without_the_new_fields_may_declare_any_prior_version(version: str) -> None:
    doc = _load(BASE_FIXTURE)  # no value_states, no resolution fields
    doc["contract_version"] = version
    validate_results_document(doc)


# ---------------------------------------------------------------------------
# Property e (partial): a withheld value never carries a number; a SINGLE
# value_state entry that mixes the fields of two ways is rejected. Two rules the
# schema CANNOT express (a key shown in values[] AND withheld in the map; a shown
# value with no entry) are pinned as known limits in the xfail tests below.
# ---------------------------------------------------------------------------


def test_withheld_value_carrying_a_number_is_rejected() -> None:
    doc = _base_1_3_0()
    states = doc["answers"]["permitted_envelope"]["value_states"]
    states["max_lot_coverage"]["value"] = 100  # a withheld value must carry no number
    with pytest.raises(StudyContractError):
        validate_results_document(doc)
    # Removing ONLY the number makes the document valid -> the number was the defect.
    del states["max_lot_coverage"]["value"]
    validate_results_document(doc)


def test_one_entry_mixing_two_ways_is_rejected() -> None:
    doc = _base_1_3_0()
    states = doc["answers"]["floor_area_allowance"]["value_states"]
    # One value_state entry that carries BOTH a shown way (way: settled) and the
    # fields of a withheld way (label/reason/gap_kind/resolved_by) matches none of
    # the three closed value_state branches and is rejected. NOTE: this is NOT the
    # "same key shown in values[] and withheld in the map" case - the schema does
    # NOT refuse that (see the KNOWN_LIMIT xfail tests below).
    states["max_residential_far"] = {
        "way": "settled",
        "label": "Maximum residential FAR",
        "reason": "not known",
        "gap_kind": "missing_information",
        "resolved_by": "a survey",
    }
    with pytest.raises(StudyContractError):
        validate_results_document(doc)


# ---------------------------------------------------------------------------
# KNOWN LIMITS. The schema is expressed with only the keywords the repository's
# contract validator accepts (.github/scripts/validate_contracts.py), so it does
# NOT refuse three wrong documents: a shown value with no way entry (C7b), a key
# both shown and withheld (C6), and an EMPTY value_states map on an available
# answer (round 4 - the empty map is the same gap as a shown value with no entry).
# Refusing them is owed to the validator of the engine that first emits 1.3.0
# (backlog row DB-171). strict=True makes each test FAIL the day the gap is
# closed, forcing whoever closes it to remove the mark.
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    strict=True,
    reason="KNOWN LIMIT (DB-171): JSON Schema 2020-12 cannot quantify that every value key "
    "shown in an answer's values[] array also carries a value_state, so a shown value with no "
    "way entry (settled by silence) is NOT refused by the schema. Refusing it is owed to the "
    "validator of the engine that first emits 1.3.0; strict xfail fails when that lands.",
)
def test_KNOWN_LIMIT_a_shown_value_with_no_way_entry_is_not_refused_by_the_schema() -> None:
    doc = _base_1_3_0()
    # Two values are shown in floor_area_allowance; leave only ONE value_state entry,
    # so the second shown value states no way (C7b). The desired rule is that the
    # contract refuses this; it does not today, so this assertion fails -> xfail.
    doc["answers"]["floor_area_allowance"]["value_states"] = {
        "max_residential_far": {"way": "settled"}
    }
    assert len(doc["answers"]["floor_area_allowance"]["values"]) == 2
    with pytest.raises(StudyContractError):
        validate_results_document(doc)


@pytest.mark.xfail(
    strict=True,
    reason="KNOWN LIMIT (DB-171): JSON Schema 2020-12 cannot express cross-container key "
    "disjointness for dynamic keys, so a key shown in an answer's values[] array AND carrying "
    "a withheld value_state (both shown and withheld) is NOT refused by the schema. Refusing it "
    "is owed to the validator of the engine that first emits 1.3.0; strict xfail fails on close.",
)
def test_KNOWN_LIMIT_a_key_both_shown_and_withheld_is_not_refused_by_the_schema() -> None:
    doc = _base_1_3_0()
    # max_residential_far stays a shown item of values[] (value 2.0) AND is given a
    # withheld value_state (C6). The desired rule is that the contract refuses this;
    # it does not today, so this assertion fails -> xfail.
    shown = {v["key"] for v in doc["answers"]["floor_area_allowance"]["values"]}
    assert "max_residential_far" in shown
    doc["answers"]["floor_area_allowance"]["value_states"]["max_residential_far"] = {
        "way": "withheld",
        "label": "Maximum residential FAR",
        "reason": "not known",
        "gap_kind": "missing_information",
        "resolved_by": "a survey",
    }
    with pytest.raises(StudyContractError):
        validate_results_document(doc)


@pytest.mark.xfail(
    strict=True,
    reason="KNOWN LIMIT (DB-171): the schema uses only the keywords the repository's contract "
    "validator accepts, which cannot require a non-empty object (no minProperties), so an EMPTY "
    "value_states map on an available answer of a 1.3.0 document is NOT refused. An available "
    "answer always has a shown value, so this is the same gap as a shown value with no entry. "
    "Refusing it is owed to the validator of the engine that first emits 1.3.0; strict xfail "
    "fails when that lands.",
)
def test_KNOWN_LIMIT_an_empty_way_map_is_not_refused_by_the_schema() -> None:
    doc = _base_1_3_0()
    # An available answer carries an EMPTY value_states map (present, satisfying the
    # forward binding's 'required', but with no ways at all). The desired rule is
    # that the contract refuses this; it does not today, so this assertion fails -> xfail.
    doc["answers"]["floor_area_allowance"]["value_states"] = {}
    assert doc["answers"]["floor_area_allowance"]["status"] == "available"
    with pytest.raises(StudyContractError):
        validate_results_document(doc)


# ---------------------------------------------------------------------------
# Property f: a withheld WHOLE answer may say what resolves it and which gap kind.
# ---------------------------------------------------------------------------


def test_whole_answer_not_available_carries_resolution_fields_at_1_3_0() -> None:
    doc = _base_1_3_0()
    bo = doc["answers"]["building_option"]
    assert bo["status"] == "not_available"
    assert bo["resolved_by"] and bo["gap_kind"] == "work_owed"
    validate_results_document(doc)


def test_not_available_resolution_fields_bind_1_3_0() -> None:
    doc = _load(BASE_FIXTURE)
    doc["answers"]["building_option"] = {
        "status": "not_available",
        "reason": "No building option is shown in this milestone.",
        "reason_kind": "rule_not_implemented",
        "resolved_by": "Building the generator and a reference case.",
        "gap_kind": "work_owed",
    }
    # The resolution fields are a 1.3.0 field: declaring a lower version is rejected.
    for stale in PUBLISHED_PRE_1_3_0:
        doc["contract_version"] = stale
        with pytest.raises(StudyContractError):
            validate_results_document(doc)
    doc["contract_version"] = "1.3.0"
    # building_option is the only available answer removed, so no way-layer is owed.
    doc["answers"]["floor_area_allowance"]["value_states"] = {
        "max_residential_far": {"way": "settled"},
        "max_residential_floor_area": {"way": "settled"},
    }
    doc["answers"]["permitted_envelope"]["value_states"] = {
        v["key"]: {"way": "settled"}
        for v in doc["answers"]["permitted_envelope"]["values"]
    }
    validate_results_document(doc)


def test_not_available_answer_still_requires_a_reason() -> None:
    doc = _base_1_3_0()
    del doc["answers"]["building_option"]["reason"]  # reason stays required
    with pytest.raises(StudyContractError):
        validate_results_document(doc)


# ---------------------------------------------------------------------------
# Property g: the remaining-floor-area line is untouched (shared not_available).
# ---------------------------------------------------------------------------


def test_remaining_floor_area_not_available_gained_no_1_3_0_fields() -> None:
    doc = _base_1_3_0()
    doc["remaining_floor_area"] = {
        "status": "not_available",
        "reason": "Needs verified zoning-lot boundaries and existing zoning floor area.",
        "reason_kind": "missing_input",
    }
    validate_results_document(doc)
    # The shared not_available is closed: remaining_floor_area never grew the
    # answer-level 1.3.0 resolution fields, so adding one is rejected.
    doc["remaining_floor_area"]["resolved_by"] = "a survey"
    with pytest.raises(StudyContractError):
        validate_results_document(doc)


# ---------------------------------------------------------------------------
# Property h / S8: the shown value's number stays a number in the generated types;
# the runtime copy accepts a 1.3.0 document (copies in step).
# ---------------------------------------------------------------------------


def test_shown_value_number_stays_a_number_in_generated_types() -> None:
    ts = GENERATED_RESULTS_TS.read_text(encoding="utf-8")
    start = ts.index("export interface AnswerValue {")
    body = ts[start : ts.index("}", start)]
    assert "value: number;" in body
    assert "way" not in body, "the shown value object is unchanged (no way marker on it)"


def test_runtime_copy_accepts_a_1_3_0_document() -> None:
    validate_results_document(_base_1_3_0())


# ---------------------------------------------------------------------------
# Round 4 guard: the repository's contract validator (.github/scripts/
# validate_contracts.py, CI job "contracts") accepts only a fixed keyword subset.
# Run its structural check over results.schema.json so a keyword outside that
# subset (the round-4 CI failure: minProperties / propertyNames) can never reach
# CI unseen from the api test suite. Loaded by path - it is a standalone stdlib
# script whose module-level code defines functions and does not run main() unless
# invoked as __main__ - so importing it here is sound; skip only if the repo tree
# (and thus the CI script) is absent from this checkout.
# ---------------------------------------------------------------------------


def test_repository_contract_validator_accepts_results_schema() -> None:
    validator_path = REPO_ROOT / ".github" / "scripts" / "validate_contracts.py"
    if not validator_path.exists():
        pytest.skip("repository contract validator not present in this checkout")
    spec = importlib.util.spec_from_file_location("results_slot_vc_guard", validator_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    schema = _load(REPO_ROOT / "packages" / "contracts" / "schemas" / "v1" / "results.schema.json")
    errors: list[str] = []
    module.structural_check(schema, schema["$id"], "#", errors, [])
    assert errors == [], errors
