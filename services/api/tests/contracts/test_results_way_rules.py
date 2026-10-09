"""The two results validators refuse the 1.3.0 documents the schema cannot (M5-T131).

Backlog row DB-171: the schema of results contract 1.3.0 cannot compare the keys of an
answer's shown values with the keys of its ``value_states`` map, so the schema alone
accepts a 1.3.0 document in which (i) a shown value has no way entry (an empty map is the
extreme case), (ii) a key is both shown and withheld, or (iii) a settled/conditional way
entry has no shown value. One shared pure rule
(:func:`app.contracts.results_way_rules.results_way_violations`) computes those breaches
after the schema, and BOTH results validators call it and refuse, each raising its own
error type:

- ``app.contracts.study_contracts.validate_results_document`` -> ``StudyContractError``
- ``app.scenario.three_answers.contract.validate_results_document`` -> ``ResultsContractError``

These tests run scenarios S1-S7 through BOTH validators, run every valid and invalid
results fixture of the repository through both unchanged, and prove the rule does nothing
below contract 1.3.0. Documents are built from an existing valid fixture loaded read-only;
no fixture file is added, changed or removed.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from app.contracts.results_way_rules import (
    CONTRACT_VERSION_1_3_0,
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
from app.scenario.three_answers.contract import (
    ResultsContractError,
)
from app.scenario.three_answers.contract import (
    validate_results_document as engine_validate_results_document,
)

# services/api/tests/contracts/test_*.py -> parents[4] is the repo root.
REPO_ROOT = Path(__file__).resolve().parents[4]
RESULTS_VALID = REPO_ROOT / "packages" / "contracts" / "fixtures" / "valid" / "results"
RESULTS_INVALID = REPO_ROOT / "packages" / "contracts" / "fixtures" / "invalid" / "results"
BASE_FIXTURE = RESULTS_VALID / "synthetic_all_answers_available.json"

PUBLISHED_PRE_1_3_0 = ("1.0.0", "1.1.0", "1.2.0")

# The permitted-envelope keys withheld in the well-formed 1.3.0 example (no number).
_WITHHELD_ENV_KEYS = {"max_lot_coverage", "setback_depth_above_base"}

# (validator, its error type) - the two validators results documents pass through.
VALIDATORS = (
    pytest.param(study_validate_results_document, StudyContractError, id="study_contracts"),
    pytest.param(engine_validate_results_document, ResultsContractError, id="three_answers"),
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _base_1_3_0() -> dict:
    """A well-formed 1.3.0 document built from the all-available fixture: two answers with
    a correct way-layer (settled / conditional values, two withheld values that are absent
    from values[]) and a whole answer that is not available."""
    doc = _load(BASE_FIXTURE)
    doc["contract_version"] = CONTRACT_VERSION_1_3_0

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
        "setback_depth_above_base": _withheld_entry(
            "Setback above the base",
            "ZR 23-433 is captured but not built.",
            "work_owed",
        ),
        "max_lot_coverage": _withheld_entry(
            "Maximum lot coverage",
            "The ZR 12-10 corner definition is not captured.",
            "missing_information",
        ),
    }

    doc["answers"]["building_option"] = {
        "status": "not_available",
        "reason": "No building option is shown in this milestone.",
        "reason_kind": "rule_not_implemented",
        "resolved_by": "Building the building-option generator and a reference case.",
        "gap_kind": "work_owed",
    }
    return doc


def _withheld_entry(label: str, reason: str, gap_kind: str) -> dict:
    return {
        "way": "withheld",
        "label": label,
        "reason": reason,
        "gap_kind": gap_kind,
        "resolved_by": "Capturing and reading the governing law text.",
    }


# floor_area_allowance shows two values; this one-entry map leaves the second
# (max_residential_floor_area) with no way entry - the S1 "settled by silence" defect.
_ONE_FAR_STATE = {"max_residential_far": {"way": "settled"}}


def _leave_second_far_value_unstated(doc: dict) -> dict:
    doc["answers"]["floor_area_allowance"]["value_states"] = dict(_ONE_FAR_STATE)
    return doc


# ---------------------------------------------------------------------------
# Sanity: both validators accept the well-formed 1.3.0 document (and the base
# fixture is really 1.0.0, so nothing emits 1.3.0).
# ---------------------------------------------------------------------------


def test_base_fixture_is_pre_1_3_0() -> None:
    assert _load(BASE_FIXTURE)["contract_version"] in PUBLISHED_PRE_1_3_0


@pytest.mark.parametrize("validate, _error", VALIDATORS)
def test_well_formed_1_3_0_document_is_accepted(validate, _error) -> None:
    validate(_base_1_3_0())


# ---------------------------------------------------------------------------
# S1: a shown value with no way entry is refused (an empty map included).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("validate, error", VALIDATORS)
def test_S1_shown_value_with_no_way_entry_is_refused(validate, error) -> None:
    doc = _leave_second_far_value_unstated(_base_1_3_0())
    assert len(doc["answers"]["floor_area_allowance"]["values"]) == 2
    with pytest.raises(error) as exc:
        validate(doc)
    message = str(exc.value)
    assert "floor_area_allowance" in message and "max_residential_floor_area" in message


@pytest.mark.parametrize("validate, error", VALIDATORS)
def test_S1_empty_way_map_is_refused(validate, error) -> None:
    doc = _base_1_3_0()
    doc["answers"]["floor_area_allowance"]["value_states"] = {}
    assert doc["answers"]["floor_area_allowance"]["status"] == "available"
    with pytest.raises(error):
        validate(doc)


# ---------------------------------------------------------------------------
# S2: a key both shown and withheld is refused.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("validate, error", VALIDATORS)
def test_S2_key_both_shown_and_withheld_is_refused(validate, error) -> None:
    doc = _base_1_3_0()
    shown = {v["key"] for v in doc["answers"]["floor_area_allowance"]["values"]}
    assert "max_residential_far" in shown  # it stays a shown value with a number
    doc["answers"]["floor_area_allowance"]["value_states"]["max_residential_far"] = (
        _withheld_entry("Maximum residential FAR", "not known", "missing_information")
    )
    with pytest.raises(error) as exc:
        validate(doc)
    assert "max_residential_far" in str(exc.value)


# ---------------------------------------------------------------------------
# S3: a settled/conditional way entry for no shown value is refused; a withheld
# entry for a key not in values[] is accepted (that is what withheld means).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("validate, error", VALIDATORS)
def test_S3_way_entry_for_no_value_is_refused(validate, error) -> None:
    doc = _base_1_3_0()
    doc["answers"]["floor_area_allowance"]["value_states"]["phantom_key"] = {"way": "settled"}
    with pytest.raises(error) as exc:
        validate(doc)
    assert "phantom_key" in str(exc.value)


@pytest.mark.parametrize("validate, _error", VALIDATORS)
def test_S3_withheld_entry_for_a_non_shown_key_is_accepted(validate, _error) -> None:
    doc = _base_1_3_0()
    shown = {v["key"] for v in doc["answers"]["floor_area_allowance"]["values"]}
    assert "a_future_withheld_value" not in shown
    doc["answers"]["floor_area_allowance"]["value_states"]["a_future_withheld_value"] = (
        _withheld_entry("A future value", "not known yet", "work_owed")
    )
    validate(doc)  # a withheld key that is not shown is allowed


# ---------------------------------------------------------------------------
# S4: an available answer with every value withheld is refused BY THE SCHEMA
# (values[] carries minItems:1), not by this rule. The shared rule reports no
# breach for it; the schema refuses it before the rule runs.
# ---------------------------------------------------------------------------


def _all_withheld_available_answer(measurement: dict) -> dict:
    return {
        "status": "available",
        "values": [],  # refused by the schema: answer_available.values minItems:1
        "measurement": measurement,
        "value_states": {
            "max_residential_far": _withheld_entry("FAR", "not known", "missing_information"),
        },
    }


def test_S4_all_withheld_available_answer_is_a_schema_breach_not_a_way_breach() -> None:
    doc = _base_1_3_0()
    measurement = copy.deepcopy(doc["answers"]["floor_area_allowance"]["measurement"])
    doc["answers"]["floor_area_allowance"] = _all_withheld_available_answer(measurement)
    # The shared way-rule sees no shown value and only a withheld entry: no breach.
    assert results_way_violations(doc) == []


@pytest.mark.parametrize("validate, error", VALIDATORS)
def test_S4_all_withheld_available_answer_is_refused_by_both(validate, error) -> None:
    doc = _base_1_3_0()
    measurement = copy.deepcopy(doc["answers"]["floor_area_allowance"]["measurement"])
    doc["answers"]["floor_area_allowance"] = _all_withheld_available_answer(measurement)
    with pytest.raises(error):  # the schema refuses the empty values[] list
        validate(doc)


# ---------------------------------------------------------------------------
# S5: a correct 1.3.0 document (settled, conditional and withheld values in one
# answer, a whole answer not available) is accepted by both.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("validate, _error", VALIDATORS)
def test_S5_correct_document_with_all_three_ways_is_accepted(validate, _error) -> None:
    doc = _base_1_3_0()
    env_states = doc["answers"]["permitted_envelope"]["value_states"]
    ways = {entry["way"] for entry in env_states.values()}
    assert {"settled", "conditional", "withheld"} <= ways
    assert doc["answers"]["building_option"]["status"] == "not_available"
    validate(doc)


# ---------------------------------------------------------------------------
# S6: nothing valid today changes. Every valid fixture is accepted and every
# invalid one refused by both validators; the rule is not applied below 1.3.0.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("validate, _error", VALIDATORS)
@pytest.mark.parametrize("fixture", sorted(RESULTS_VALID.glob("*.json")), ids=lambda p: p.name)
def test_S6_every_valid_fixture_is_accepted_by_both(validate, _error, fixture: Path) -> None:
    validate(_load(fixture))


@pytest.mark.parametrize("validate, error", VALIDATORS)
@pytest.mark.parametrize("fixture", sorted(RESULTS_INVALID.glob("*.json")), ids=lambda p: p.name)
def test_S6_every_invalid_fixture_is_refused_by_both(validate, error, fixture: Path) -> None:
    instance = _load(fixture)
    assert FIXTURE_ONLY_KEY in instance, "invalid fixture must document its defect"
    instance.pop(FIXTURE_ONLY_KEY)  # refuse on the real schema defect, not the annotation
    with pytest.raises(error):
        validate(instance)


@pytest.mark.parametrize("validate, _error", VALIDATORS)
@pytest.mark.parametrize("version", PUBLISHED_PRE_1_3_0)
def test_S6_prior_version_document_is_untouched_by_the_rule(validate, _error, version: str) -> None:
    doc = _load(BASE_FIXTURE)  # no value_states; the rule must not fire below 1.3.0
    doc["contract_version"] = version
    validate(doc)


@pytest.mark.parametrize("version", PUBLISHED_PRE_1_3_0)
def test_S6_shared_rule_does_nothing_below_1_3_0_even_with_a_broken_layer(version: str) -> None:
    # A document that WOULD break the rule at 1.3.0, declared at a lower version, yields
    # no breach from the shared rule (the version binding is the schema's job, not this
    # rule's): the rule is version-gated and does nothing below 1.3.0.
    doc = _leave_second_far_value_unstated(_base_1_3_0())
    doc["contract_version"] = version
    assert results_way_violations(doc) == []


# ---------------------------------------------------------------------------
# S7: one rule, two callers. Both validators refuse the same document (they call
# the one shared rule), and the shared rule is a pure function with no I/O.
# ---------------------------------------------------------------------------


def test_S7_one_shared_rule_two_callers() -> None:
    doc = _leave_second_far_value_unstated(_base_1_3_0())
    with pytest.raises(StudyContractError):
        study_validate_results_document(doc)
    with pytest.raises(ResultsContractError):
        engine_validate_results_document(copy.deepcopy(doc))


# ---------------------------------------------------------------------------
# The bare schema still accepts all three documents the rule refuses. The schema
# alone is validate_study_contract_document("results", doc): it runs the bundled
# canonical schema (plus strict-JSON and the fixture-annotation guard) and NOT
# the way-rule, so it must ACCEPT each document while the shared rule reports a
# breach for it. The schema's own descriptions say it cannot compare the values[]
# keys with the map keys, and those descriptions do not change.
# ---------------------------------------------------------------------------


def _key_both_shown_and_withheld_doc() -> dict:
    doc = _base_1_3_0()
    doc["answers"]["floor_area_allowance"]["value_states"]["max_residential_far"] = _withheld_entry(
        "Maximum residential FAR", "not known", "missing_information"
    )
    return doc


def _empty_way_map_doc() -> dict:
    doc = _base_1_3_0()
    doc["answers"]["floor_area_allowance"]["value_states"] = {}
    return doc


def test_bare_schema_accepts_the_three_documents_the_rule_refuses() -> None:
    docs = {
        "shown_value_with_no_way_entry": _leave_second_far_value_unstated(_base_1_3_0()),
        "key_both_shown_and_withheld": _key_both_shown_and_withheld_doc(),
        "empty_way_map": _empty_way_map_doc(),
    }
    for name, doc in docs.items():
        # The bare schema accepts it (no raise)...
        validate_study_contract_document("results", doc)
        # ...while the shared rule reports a breach, which is why both validators refuse.
        assert results_way_violations(doc), name


# ---------------------------------------------------------------------------
# The shared pure rule directly: each breach carries the answer, the key and a
# stable rule code; the correct document yields none.
# ---------------------------------------------------------------------------


def test_pure_rule_accepts_the_well_formed_document() -> None:
    assert results_way_violations(_base_1_3_0()) == []


def test_pure_rule_flags_a_shown_value_with_no_entry() -> None:
    doc = _leave_second_far_value_unstated(_base_1_3_0())
    breaches = results_way_violations(doc)
    assert [(b.answer, b.key, b.rule) for b in breaches] == [
        ("floor_area_allowance", "max_residential_floor_area", "shown_value_has_no_way_entry")
    ]
    assert isinstance(breaches[0], WayRuleViolation)


def test_pure_rule_flags_a_shown_key_marked_withheld() -> None:
    doc = _base_1_3_0()
    doc["answers"]["floor_area_allowance"]["value_states"]["max_residential_far"] = _withheld_entry(
        "FAR", "not known", "missing_information"
    )
    rules = {b.rule for b in results_way_violations(doc)}
    assert rules == {"shown_value_marked_withheld"}


def test_pure_rule_flags_a_way_entry_for_no_shown_value() -> None:
    doc = _base_1_3_0()
    doc["answers"]["permitted_envelope"]["value_states"]["phantom"] = {
        "way": "conditional",
        "conditions": [{"kind": "user_statement", "assumption": "if x", "settled_by": "a survey"}],
    }
    breaches = results_way_violations(doc)
    assert [(b.answer, b.key, b.rule) for b in breaches] == [
        ("permitted_envelope", "phantom", "way_entry_for_no_shown_value")
    ]


def test_pure_rule_returns_empty_for_a_non_mapping_or_missing_answers() -> None:
    assert results_way_violations("not a document") == []
    assert results_way_violations({"contract_version": CONTRACT_VERSION_1_3_0}) == []
