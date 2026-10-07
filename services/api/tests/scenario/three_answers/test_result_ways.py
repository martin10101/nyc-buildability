"""Result-way module invariants (task M5-T129): new-files-only, no zoning number, nothing
imports it, every way object fits the bundled contract, no reason names 'professional review'.

The expected OUTCOMES come from the work order's sentences, quoted beside each test, never from
the module. This file holds the invariants that hold across every case (S7, S9, H7); the
lot-by-lot scenarios (S1-S6, S8) are in the sibling test_result_ways_*.py files.
"""

from __future__ import annotations

import ast
import pathlib

import jsonschema
import pytest

from app.contracts import study_contracts
from app.scenario.three_answers import result_ways as rw
from app.scenario.three_answers.result_way_inputs import (
    Checked,
    DensityKnowledge,
    LotAreaFigures,
    LotType,
    Recorded,
)
from app.scenario.three_answers.result_ways import (
    AnswerWays,
    Conditional,
    ResultWays,
    Settled,
    Withheld,
    decide_result_ways,
)

from .test_result_ways_lib import base_inputs, k20, plain_inputs, support_all

_APP_ROOT = pathlib.Path(rw.__file__).resolve().parents[2]  # services/api/app
# The module is three files in one package (result_ways re-exports the records):
_MODULE_FILES = ("result_ways.py", "result_way_inputs.py", "result_way_conditions.py")


# --------------------------------------------------------------------------- a battery of cases
def _battery() -> list[ResultWays]:
    """One ResultWays per shape the module can produce, so the invariants see every way."""
    return [
        decide_result_ways(base_inputs()),
        decide_result_ways(base_inputs(overlay_support=support_all(True))),
        decide_result_ways(base_inputs(overlay_support=support_all(False))),
        decide_result_ways(plain_inputs(**k20(True))),
        decide_result_ways(plain_inputs(**k20(False))),
        decide_result_ways(plain_inputs(special_purpose_district=Recorded.PRESENT)),
        decide_result_ways(plain_inputs(split_by_district_line=Recorded.NOT_READ)),
        decide_result_ways(plain_inputs(waterfront=Checked.PRESENT)),
        decide_result_ways(plain_inputs(
            lot_type=LotType.INTERIOR, reach=None,
            special_density=DensityKnowledge.USER_STATEMENT_NOT_IN_ONE,
        )),
        decide_result_ways(plain_inputs(
            area=LotAreaFigures(None, None, None),
            inclusionary_housing_area=Recorded.PRESENT, flood_zone=Recorded.NOT_READ,
        )),
    ]


# --------------------------------------------------------------------------- S9: new files only
def test_nothing_under_app_imports_the_module_yet():
    """S9: a test proves that nothing under services/api/app imports the module. The three
    module files may reference each other (result_ways imports the other two); no OTHER app
    file names any of them."""
    offenders = [
        str(path) for path in _APP_ROOT.rglob("*.py")
        if path.name not in _MODULE_FILES
        and "result_way" in path.read_text(encoding="utf-8")
    ]
    assert offenders == [], f"these modules already reference the result-way module: {offenders}"


def test_module_holds_no_zoning_number_only_the_two_legal_measures():
    """S9 / rule: no FAR, percentage, height or factor constant; the ONLY numeric literals are
    the two legal measures of reading O9 (100 feet, 135 degrees)."""
    literals: set[float] = set()
    for name in _MODULE_FILES:
        src = (_APP_ROOT / "scenario" / "three_answers" / name).read_text(encoding="utf-8")
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if not isinstance(node.value, bool):
                    literals.add(float(node.value))
    assert literals == {100.0, 135.0}, f"unexpected numeric literal(s) in the module: {literals}"
    assert rw.CORNER_PORTION_WITHIN_100_FT.value == 100.0
    assert rw.REAR_YARD_WAIVER_WITHIN_100_FT.value == 100.0
    assert rw.REAR_YARD_WAIVER_MAX_ANGLE_135_DEG.value == 135.0


def test_the_two_legal_measures_cite_their_captures():
    """Reading O9: each legal measure carries the capture id of the ZR text it comes from."""
    assert rw.CORNER_PORTION_WITHIN_100_FT.capture_snapshot_id == "zr-12-10-lot-corner"
    assert rw.REAR_YARD_WAIVER_WITHIN_100_FT.capture_snapshot_id == "zr-23-344"
    assert rw.REAR_YARD_WAIVER_MAX_ANGLE_135_DEG.capture_snapshot_id == "zr-23-344"
    assert "100 feet" in rw.CORNER_PORTION_WITHIN_100_FT.captured_words
    assert "135 degrees or less" in rw.REAR_YARD_WAIVER_MAX_ANGLE_135_DEG.captured_words


# --------------------------------------------------------------------------- the public interface
def test_decides_every_result_the_packet_lists():
    ways = decide_result_ways(base_inputs())
    answer_keys = {
        row.key for answer in (ways.floor_area_allowance, ways.permitted_envelope,
                               ways.building_option) for row in answer.values
    }
    assert rw.FLOOR_AREA_KEYS[0] in answer_keys
    assert set(rw.FLOOR_AREA_KEYS) <= answer_keys
    assert set(rw.HEIGHT_KEYS) | {rw.COVERAGE_KEY} <= answer_keys
    assert set(rw.BUILDING_OPTION_KEYS) <= answer_keys
    standalone = {
        ways.rear_yard.key, ways.setback_above_base.key, ways.unit_limit_standard.key,
        ways.unit_limit_qualifying_affordable.key, ways.unit_limit_qualifying_senior.key,
    }
    assert standalone == {
        rw.REAR_YARD_KEY, rw.SETBACK_KEY, rw.UNIT_STANDARD_KEY,
        rw.UNIT_QUALIFYING_AFFORDABLE_KEY, rw.UNIT_QUALIFYING_SENIOR_KEY,
    }


# --------------------------------------------------------------------------- S7: fits the contract
def _value_state_validator() -> jsonschema.Draft202012Validator:
    results_id = study_contracts._load_bundled_schema("results.schema.json")["$id"]
    return jsonschema.Draft202012Validator(
        {"$ref": f"{results_id}#/$defs/value_state"}, registry=study_contracts._registry()
    )


def _not_available_validator() -> jsonschema.Draft202012Validator:
    results_id = study_contracts._load_bundled_schema("results.schema.json")["$id"]
    return jsonschema.Draft202012Validator(
        {"$ref": f"{results_id}#/$defs/answer_not_available"}, registry=study_contracts._registry()
    )


def test_every_way_object_validates_against_the_bundled_contract():
    """S7 (work order H7): each way validates as a value_state (or as the not-available form
    of an answer) of the bundled schema; a withheld way never carries a number."""
    vs = _value_state_validator()
    na = _not_available_validator()
    seen_ways: set[str] = set()
    for ways in _battery():
        for row in ways.result_ways():
            state = row.way.to_value_state()
            vs.validate(state)
            seen_ways.add(state["way"])
            if isinstance(row.way, Withheld):
                assert "value" not in state, "a withheld value carries no number"
        for answer in (ways.floor_area_allowance, ways.permitted_envelope, ways.building_option):
            if answer.whole_answer_not_available is not None:
                na.validate(answer.whole_answer_not_available.to_dict())
    assert seen_ways == {"settled", "conditional", "withheld"}, seen_ways


def test_every_withheld_way_has_a_reason_a_kind_and_what_would_resolve_it():
    """H7: every withheld result has a reason, a kind, and what would resolve it."""
    for ways in _battery():
        for row in ways.result_ways():
            if isinstance(row.way, Withheld):
                assert row.way.label and row.way.reason and row.way.resolved_by
                assert row.way.gap_kind in ("missing_information", "work_owed")


def test_every_conditional_names_at_least_one_assumption():
    for ways in _battery():
        for row in ways.result_ways():
            if isinstance(row.way, Conditional):
                assert len(row.way.conditions) >= 1
                for cond in row.way.conditions:
                    assert cond.kind in (
                        "user_statement", "contradicted_record", "unchecked_condition"
                    )
                    assert cond.assumption and cond.settled_by


def test_a_settled_way_carries_no_condition():
    for ways in _battery():
        for row in ways.result_ways():
            if isinstance(row.way, Settled):
                assert row.way.to_value_state() == {"way": "settled"}


# --------------------------------------------------------------------------- H7 / K7: the phrase
def test_no_reason_contains_the_phrase_of_gap_k7():
    """H7: no reason text contains 'professional review' (gap K7 corrected)."""
    for ways in _battery():
        for text in _all_text(ways):
            assert "professional review" not in text.lower(), text


def test_module_source_never_names_the_k7_phrase():
    for name in _MODULE_FILES:
        src = (_APP_ROOT / "scenario" / "three_answers" / name).read_text(encoding="utf-8")
        assert "professional review" not in src.lower()


def _all_text(ways: ResultWays) -> list[str]:
    texts: list[str] = []
    for row in ways.result_ways():
        way = row.way
        if isinstance(way, Withheld):
            texts.extend([way.label, way.reason, way.resolved_by])
        elif isinstance(way, Conditional):
            for cond in way.conditions:
                texts.extend([cond.assumption, cond.settled_by])
    for answer in (ways.floor_area_allowance, ways.permitted_envelope, ways.building_option):
        na = answer.whole_answer_not_available
        if na is not None:
            texts.extend([na.reason, na.resolved_by])
    return texts


@pytest.mark.parametrize("answer_name", ["floor_area_allowance", "permitted_envelope"])
def test_an_answer_is_not_available_only_when_every_value_is_withheld(answer_name: str):
    """The contract cannot keep an answer 'available' with no shown value: the whole answer is
    not available exactly when every one of its values is withheld."""
    # One K20 condition recorded present withholds every zoning result (reading O6).
    withheld_all = decide_result_ways(plain_inputs(waterfront=Checked.PRESENT))
    answer: AnswerWays = getattr(withheld_all, answer_name)
    assert not answer.is_available
    assert all(isinstance(row.way, Withheld) for row in answer.values)
    # All K20 absent: the answer is available again (its values are shown).
    shown = decide_result_ways(plain_inputs(**k20(True)))
    assert getattr(shown, answer_name).is_available
