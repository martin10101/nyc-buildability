"""Tests for the labelled input channel to the evaluator (task C-07, plan M1-08).

Covers the adapter (app.contracts.evaluator_inputs) and the evaluator_inputs v1
contract: an entered/assumed/survey value governs its engine input and stays
distinct from the city fact it displaces, the weakest governing rank carries
through to the three-answer evaluator's emitted answers, and the documented
invalid shapes fail validation.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from app.contracts.evaluator_inputs import (
    EvaluatorInputsError,
    build_evaluator_inputs,
    build_three_answer_inputs,
)
from app.contracts.study_contracts import FIXTURE_ONLY_KEY, StudyContractError
from app.scenario.three_answers import generate_results

# services/api/tests/contracts/test_*.py -> parents[4] is the repo root.
_REPO_ROOT = Path(__file__).resolve().parents[4]
_FIXTURE_ROOT = _REPO_ROOT / "packages" / "contracts" / "fixtures"
_STUDY_BASE = (
    _FIXTURE_ROOT / "valid" / "study"
    / "synthetic_copied_from_export_existing_zfa_unknown.json"
)
_CORNER_STUDY = _FIXTURE_ROOT / "valid" / "study" / "synthetic_corner_lot_two_options.json"
_BENCHMARK = (
    _FIXTURE_ROOT / "valid" / "benchmark_lot"
    / "northern_blvd_215_16_queens_4073340070.json"
)
_OPTION_ID = "opt-1"
_LANE_ON = {"LANE_A_ENABLED": "1"}

_LABELS = {
    "survey_entered": "Survey (entered)",
    "city_records": "City records",
    "approximate_tax_map": "Approximate — tax map",
    "entered": "Entered",
    "assumed": "Assumed",
}
_UNIT = {
    "lot_area": "square_feet",
    "lot_frontage": "feet",
    "lot_depth": "feet",
    "lot_type": None,
    "zoning_district": None,
}


def _source(kind: str, **over) -> dict:
    base = {
        "kind": kind,
        "dataset": None,
        "dataset_version": None,
        "retrieved_at": "2026-10-03T00:00:00Z",
        "query_ref": None,
        "document_ref": None,
        "statement": None,
    }
    base.update(over)
    return base


_CITY = _source(
    "city_dataset",
    dataset="test-fixture-synthetic PLUTO",
    dataset_version="26v2",
    query_ref="test-fixture-synthetic://pluto/4073340070",
)
_ARCHITECT = _source("architect_entry")
_SURVEY = _source("survey", document_ref="test-fixture-synthetic survey-001")
_ASSUMPTION = _source("assumption", statement="Architect-stated value for a check.")


def _fact(key, value, rank, fact_id, source, *, street=None, bbl="4073340070") -> dict:
    return {
        "contract_version": "1.0.0",
        "fact_id": fact_id,
        "key": key,
        "lot_bbl": bbl,
        "street": street,
        "value": value,
        "unit": _UNIT[key],
        "measurement": {"rank": rank, "label": _LABELS[rank]},
        "source": source,
        "blocks": [],
        "editable": True,
    }


def _study(facts: list[dict], *, study_id: str = "study-evi") -> dict:
    base = copy.deepcopy(json.loads(_STUDY_BASE.read_text("utf-8")))
    base["study_id"] = study_id
    base["site"]["facts"] = facts
    base["revision"] = {"number": 1, "created_at": "2026-10-03T00:00:00Z", "parent": None}
    return base


# 215-16 Northern Blvd benchmark site values (copied, never edited, from the
# benchmark fixture that tests/scenario/three_answers/test_three_answers_benchmark.py
# also reads).
def _benchmark_value(key: str):
    doc = json.loads(_BENCHMARK.read_text("utf-8"))
    return next(v["value"] for v in doc["expected_values"] if v["key"] == key)


def _benchmark_city_facts() -> list[dict]:
    return [
        _fact("lot_area", _benchmark_value("lot_area"), "city_records", "f-area-city", _CITY),
        _fact(
            "lot_frontage", _benchmark_value("lot_dimension_1"), "city_records",
            "f-front-city", _CITY, street="Northern Boulevard",
        ),
        _fact(
            "lot_depth", _benchmark_value("lot_dimension_2"), "city_records",
            "f-depth-city", _CITY,
        ),
        _fact("lot_type", _benchmark_value("lot_type"), "city_records", "f-type-city", _CITY),
        _fact(
            "zoning_district", _benchmark_value("zoning_district"), "city_records",
            "f-zd-city", _CITY,
        ),
    ]


def _record(doc: dict, engine_key: str) -> dict:
    return next(r for r in doc["inputs"] if r["key"] == engine_key)


# --------------------------------------------------------------------------
# build_evaluator_inputs: governing selection and displacement
# --------------------------------------------------------------------------

def test_only_city_facts_are_city_records_with_empty_displaced() -> None:
    doc = build_evaluator_inputs(_study(_benchmark_city_facts()), _OPTION_ID)
    assert doc["contract_version"] == "1.0.0"
    assert doc["option_id"] == _OPTION_ID
    assert doc["site_measurement_rank"] == "city_records"
    for record in doc["inputs"]:
        assert record["rank"] == "city_records"
        assert record["label"] == "City records"
        assert record["governing"] is True
        assert record["displaced"] == []
    # depends_on_fact_ids lists exactly the governing fact ids.
    assert doc["depends_on_fact_ids"] == [r["fact_id"] for r in doc["inputs"]]


def test_entered_lot_area_governs_and_displaces_the_city_fact() -> None:
    facts = _benchmark_city_facts()
    facts.append(
        _fact("lot_area", 10080, "entered", "f-area-city-entered", _ARCHITECT)
    )
    doc = build_evaluator_inputs(_study(facts), _OPTION_ID)

    area = _record(doc, "lot_area_sq_ft")
    assert area["fact_id"] == "f-area-city-entered"
    assert area["rank"] == "entered"
    assert area["label"] == "Entered"
    assert area["value"] == 10080
    assert area["source_kind"] == "architect_entry"
    # The city fact it overrode travels in displaced, distinct and intact.
    assert area["displaced"] == [
        {"fact_id": "f-area-city", "rank": "city_records", "label": "City records", "value": 10075}
    ]
    # Entered is the weakest governing rank, so the whole channel carries it.
    assert doc["site_measurement_rank"] == "entered"
    assert "f-area-city-entered" in doc["depends_on_fact_ids"]
    assert "f-area-city" not in doc["depends_on_fact_ids"]


def test_assumed_value_governs_and_is_the_weakest_rank() -> None:
    facts = _benchmark_city_facts()
    facts.append(
        _fact("lot_depth", 98, "assumed", "f-depth-assumed", _ASSUMPTION)
    )
    doc = build_evaluator_inputs(_study(facts), _OPTION_ID)

    depth = _record(doc, "lot_depth_ft")
    assert depth["fact_id"] == "f-depth-assumed"
    assert depth["rank"] == "assumed"
    assert depth["label"] == "Assumed"
    assert depth["source_kind"] == "assumption"
    assert depth["displaced"][0]["fact_id"] == "f-depth-city"
    # Assumed is weakest of all, so it wins the weakest-input label.
    assert doc["site_measurement_rank"] == "assumed"


def test_survey_value_governs_but_does_not_weaken_the_label() -> None:
    facts = _benchmark_city_facts()
    facts.append(
        _fact(
            "lot_frontage", 101.0, "survey_entered", "f-front-survey", _SURVEY,
            street="Northern Boulevard",
        )
    )
    doc = build_evaluator_inputs(_study(facts), _OPTION_ID)

    front = _record(doc, "lot_front_ft")
    assert front["fact_id"] == "f-front-survey"
    assert front["rank"] == "survey_entered"
    assert front["label"] == "Survey (entered)"
    assert front["source_kind"] == "survey"
    assert front["displaced"][0]["fact_id"] == "f-front-city"
    # Survey is the STRONGEST rank: the weakest input is still the city_records
    # of the other facts, so the channel's label stays City records.
    assert doc["site_measurement_rank"] == "city_records"


def test_unknown_facts_do_not_govern() -> None:
    facts = _benchmark_city_facts()
    # An unknown depth never feeds the evaluator (it blocks); the city depth governs.
    facts.append(
        {
            "contract_version": "1.0.0",
            "fact_id": "f-depth-unknown",
            "key": "lot_depth",
            "lot_bbl": "4073340070",
            "street": None,
            "value": None,
            "unit": None,
            "measurement": {"rank": "unknown", "label": "Unknown — enter"},
            "source": None,
            "blocks": ["permitted_envelope"],
            "editable": True,
        }
    )
    doc = build_evaluator_inputs(_study(facts), _OPTION_ID)
    depth = _record(doc, "lot_depth_ft")
    assert depth["rank"] == "city_records"
    assert depth["fact_id"] == "f-depth-city"


def test_unknown_option_is_rejected() -> None:
    with pytest.raises(EvaluatorInputsError, match="is not part of study"):
        build_evaluator_inputs(_study(_benchmark_city_facts()), "opt-does-not-exist")


def test_multi_street_frontage_is_not_guessed() -> None:
    # The corner-lot fixture has two frontage facts (two streets); collapsing them to
    # one scalar is out of scope, so the adapter raises instead of guessing.
    corner = json.loads(_CORNER_STUDY.read_text("utf-8"))
    with pytest.raises(EvaluatorInputsError, match="resolves to 2 distinct site facts"):
        build_evaluator_inputs(corner, "opt-a")


# --------------------------------------------------------------------------
# build_three_answer_inputs + generate_results: the weakest rank carries through
# --------------------------------------------------------------------------

def _three_answer_inputs(doc: dict):
    return build_three_answer_inputs(
        doc,
        results_id="res-evi-1",
        computed_at="2026-10-03T00:00:00Z",
        housing_program="standard_residence",
        overlay_present=True,  # C2-2 commercial overlay (benchmark)
        special_district_present=False,
        within_100_ft_of_street_line_intersection=True,
        street_line_intersection_angle_degrees=90.0,
        special_density_area=False,
    )


def test_benchmark_city_inputs_reproduce_the_golden_allowance() -> None:
    doc = build_evaluator_inputs(_study(_benchmark_city_facts()), _OPTION_ID)
    inputs = _three_answer_inputs(doc)
    assert inputs.lot_area_sq_ft == float(_benchmark_value("lot_area"))
    assert inputs.lot_area_fact_id == "f-area-city"
    assert inputs.site_measurement_rank == "city_records"

    result = generate_results(inputs, env=_LANE_ON)
    allowance = result.document["answers"]["floor_area_allowance"]
    assert allowance["status"] == "available"
    # The weakest input is city_records, so the answer carries that label.
    assert allowance["measurement"] == {"rank": "city_records", "label": "City records"}
    area = next(v for v in allowance["values"] if v["key"] == "max_residential_floor_area")
    assert area["value"] == _benchmark_value("max_residential_floor_area")  # 20150, golden
    envelope = result.document["answers"]["permitted_envelope"]
    assert envelope["measurement"] == {"rank": "city_records", "label": "City records"}


def test_entered_lot_area_flows_into_the_evaluator_with_the_entered_label() -> None:
    facts = _benchmark_city_facts()
    facts.append(_fact("lot_area", 10080, "entered", "f-area-city-entered", _ARCHITECT))
    doc = build_evaluator_inputs(_study(facts), _OPTION_ID)
    inputs = _three_answer_inputs(doc)
    # The ENTERED value (not the city value) is what the evaluator computes from.
    assert inputs.lot_area_sq_ft == 10080.0
    assert inputs.lot_area_fact_id == "f-area-city-entered"
    assert inputs.site_measurement_rank == "entered"

    result = generate_results(inputs, env=_LANE_ON)
    allowance = result.document["answers"]["floor_area_allowance"]
    # The emitted answer carries the weakest input's label: Entered.
    assert allowance["measurement"] == {"rank": "entered", "label": "Entered"}
    far = next(v for v in allowance["values"] if v["key"] == "max_residential_far")["value"]
    area = next(v for v in allowance["values"] if v["key"] == "max_residential_floor_area")["value"]
    # The allowance is FAR x the entered lot area, not the city lot area.
    assert area == far * 10080.0


def test_missing_required_engine_input_is_rejected() -> None:
    # Drop lot_type: the evaluator cannot answer, so the adapter refuses (no guess).
    facts = [f for f in _benchmark_city_facts() if f["key"] != "lot_type"]
    doc = build_evaluator_inputs(_study(facts), _OPTION_ID)
    with pytest.raises(EvaluatorInputsError, match="missing required engine input"):
        _three_answer_inputs(doc)


# --------------------------------------------------------------------------
# contract: the documented invalid shapes fail validation
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "name",
    [
        "entered_labelled_city_records.json",
        "governing_record_without_fact_id.json",
        "unknown_rank.json",
    ],
)
def test_invalid_fixtures_fail_validation(name: str) -> None:
    from app.contracts.study_contracts import validate_evaluator_inputs_document

    path = _FIXTURE_ROOT / "invalid" / "evaluator_inputs" / name
    document = json.loads(path.read_text("utf-8"))
    assert isinstance(document.pop(FIXTURE_ONLY_KEY, None), str), "annotation missing"
    with pytest.raises(StudyContractError, match="failed canonical schema validation"):
        validate_evaluator_inputs_document(document)
