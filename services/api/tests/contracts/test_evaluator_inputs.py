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
_TAXMAP = _source(
    "tax_map_computation",
    dataset="test-fixture-synthetic tax map",
    query_ref="test-fixture-synthetic://taxmap/4073340070",
)


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


def _benchmark_identity_address() -> str:
    """The lot's REAL confirmed address (benchmark pack identity.address), read from
    the fixture - the address the confirmed-address step supplies, not a test literal."""
    doc = json.loads(_BENCHMARK.read_text("utf-8"))
    return doc["identity"]["address"]


# 215-16 Northern as a CORNER lot: two per-street tax-map frontage facts (the live B-03
# read shape), everything else the benchmark city facts. R138 exercises the address-street
# front-lot-line selection on these.
def _two_frontage_corner_facts() -> list[dict]:
    facts = [f for f in _benchmark_city_facts() if f["key"] != "lot_frontage"]
    facts.append(
        _fact("lot_frontage", 103.88, "approximate_tax_map", "f-front-northern", _TAXMAP,
              street="Northern Boulevard")
    )
    facts.append(
        _fact("lot_frontage", 99.98, "approximate_tax_map", "f-front-215place", _TAXMAP,
              street="215 Place")
    )
    return facts


def _study_with_address(facts: list[dict], address) -> dict:
    study = _study(facts)
    study["property"]["address"] = address
    return study


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


def _existing_zfa_fact(
    *, value, rank: str, fact_id: str, source: dict | None, note: str, bbl="4073340070"
) -> dict:
    """An existing_zoning_floor_area site fact (B-05), for the INERT slot tests."""
    label = {
        "city_records": "City records",
        "assumed": "Assumed",
        "entered": "Entered",
        "unknown": "Unknown — enter",
    }[rank]
    known = rank != "unknown"
    return {
        "contract_version": "1.0.0",
        "fact_id": fact_id,
        "key": "existing_zoning_floor_area",
        "lot_bbl": bbl,
        "street": None,
        "value": value,
        "unit": "square_feet" if known else None,
        "measurement": {"rank": rank, "label": label},
        "source": source,
        "blocks": [] if known else ["remaining_floor_area", "existing_building_paths"],
        "editable": True,
        "note": note,
    }


# A realistic B-05 "no evidence supplied" unknown reason (resolve_existing_zoning_floor_area).
_EFA_UNKNOWN_NOTE = (
    "Needs existing zoning floor area: from a Buildings Department filing or certificate "
    "of occupancy, or entered as a stated assumption. City-recorded building area is never "
    "used for it. No DOB job-filing rows were supplied. No certificate of occupancy figure "
    "or stated assumption was entered."
)
# A B-05 known note carrying the tax-lot scope statement verbatim.
_EFA_KNOWN_NOTE = (
    "9,100 sq ft from DOB BIS job 421803891 (document 01). Scope: stated for tax lot "
    "4073340070; whether the figure covers only this tax lot or a zoning lot of several tax "
    "lots is not established. City-recorded building area is shown for reference only and is "
    "never used for it."
)


# --------------------------------------------------------------------------
# existing_building slot (contract 1.1.0, INERT): journey plan §2 step 4
# --------------------------------------------------------------------------

def test_default_has_no_existing_building_slot_and_stays_1_0_0() -> None:
    # No plan and no existing_zoning_floor_area fact: the slot is absent and the output is
    # byte-identical to the 1.0.0 shape (requirement d: identical to today).
    doc = build_evaluator_inputs(_study(_benchmark_city_facts()), _OPTION_ID)
    assert doc["contract_version"] == "1.0.0"
    assert "existing_building" not in doc


def test_plan_fills_the_slot_and_bumps_version_floor_area_unknown() -> None:
    # The benchmark pack has no sourced existing floor area; a "keep" plan still fills the
    # slot with an explicit-unknown floor area carrying B-05's reason verbatim.
    facts = _benchmark_city_facts()
    facts.append(
        _existing_zfa_fact(
            value=None, rank="unknown", fact_id="f-efa-unknown", source=None,
            note=_EFA_UNKNOWN_NOTE,
        )
    )
    doc = build_evaluator_inputs(_study(facts), _OPTION_ID, existing_building_plan="keep")
    assert doc["contract_version"] == "1.1.0"
    slot = doc["existing_building"]
    assert slot["plan"] == {
        "value": "keep", "basis": "entered", "label": "Entered",
        "statement": "Keep the existing building",
    }
    fa = slot["floor_area"]
    assert fa["key"] == "existing_zoning_floor_area"
    assert fa["rank"] == "unknown" and fa["label"] == "Unknown — enter"
    assert fa["value"] is None and fa["unit"] is None and fa["source_kind"] is None
    assert fa["governing"] is False
    assert fa["note"] == _EFA_UNKNOWN_NOTE  # B-05's reason, verbatim
    # The slot is INERT: the engine inputs are unchanged by it.
    assert [r["key"] for r in doc["inputs"]] == [
        "lot_area_sq_ft", "lot_front_ft", "lot_depth_ft", "lot_type", "zoning_district",
    ]


def test_known_existing_floor_area_fills_the_slot_without_a_plan() -> None:
    facts = _benchmark_city_facts()
    facts.append(
        _existing_zfa_fact(
            value=9100, rank="city_records", fact_id="f-efa-dob",
            source=_source(
                "city_filing", dataset="DOB Job Application Filings (ic3t-wcy2)",
                document_ref="DOB BIS job 421803891",
            ),
            note=_EFA_KNOWN_NOTE,
        )
    )
    doc = build_evaluator_inputs(_study(facts), _OPTION_ID)
    assert doc["contract_version"] == "1.1.0"
    slot = doc["existing_building"]
    assert slot["plan"] is None  # no plan supplied, but a known fact still fills the slot
    fa = slot["floor_area"]
    assert fa["value"] == 9100 and fa["unit"] == "square_feet"
    assert fa["rank"] == "city_records" and fa["label"] == "City records"
    assert fa["source_kind"] == "city_filing"
    assert fa["governing"] is True
    assert fa["note"] == _EFA_KNOWN_NOTE  # tax-lot scope statement, verbatim


def test_assumption_governs_existing_floor_area_only_without_a_city_source() -> None:
    # A lone stated assumption governs the existing floor area (no city source present).
    facts = _benchmark_city_facts()
    facts.append(
        _existing_zfa_fact(
            value=8000, rank="assumed", fact_id="f-efa-assumed",
            source=_source("assumption", statement="Architect-stated existing floor area."),
            note="8,000 sq ft entered as a stated assumption.",
        )
    )
    doc = build_evaluator_inputs(_study(facts), _OPTION_ID, existing_building_plan="keep")
    fa = doc["existing_building"]["floor_area"]
    assert fa["rank"] == "assumed" and fa["governing"] is True and fa["value"] == 8000


def test_assumption_beside_a_city_existing_floor_area_raises() -> None:
    # An assumption recorded BESIDE a city existing-floor-area value is a visible conflict.
    facts = _benchmark_city_facts()
    facts.append(
        _existing_zfa_fact(
            value=9100, rank="city_records", fact_id="f-efa-dob",
            source=_source(
                "city_filing", dataset="DOB Job Application Filings (ic3t-wcy2)",
                document_ref="DOB BIS job 421803891",
            ),
            note=_EFA_KNOWN_NOTE,
        )
    )
    facts.append(
        _existing_zfa_fact(
            value=8000, rank="assumed", fact_id="f-efa-assumed",
            source=_source("assumption", statement="Architect-stated existing floor area."),
            note="8,000 sq ft entered as a stated assumption.",
        )
    )
    with pytest.raises(
        EvaluatorInputsError, match="a stated assumption conflicts with a recorded value"
    ):
        build_evaluator_inputs(_study(facts), _OPTION_ID, existing_building_plan="keep")


def test_slot_is_inert_for_the_three_answer_evaluator() -> None:
    # Filling the slot does not change the engine output: the golden allowance still holds.
    facts = _benchmark_city_facts()
    facts.append(
        _existing_zfa_fact(
            value=None, rank="unknown", fact_id="f-efa-unknown", source=None,
            note=_EFA_UNKNOWN_NOTE,
        )
    )
    doc = build_evaluator_inputs(_study(facts), _OPTION_ID, existing_building_plan="keep")
    inputs = _three_answer_inputs(doc)
    result = generate_results(inputs, env=_LANE_ON)
    allowance = result.document["answers"]["floor_area_allowance"]
    area = next(v for v in allowance["values"] if v["key"] == "max_residential_floor_area")
    assert area["value"] == _benchmark_value("max_residential_floor_area")  # 20150, golden


def test_unknown_floor_area_fact_without_a_plan_leaves_the_slot_absent() -> None:
    # A lone UNKNOWN existing-floor-area fact and no plan does NOT fill the slot: the
    # 1.0.0 output is unchanged (requirement d).
    facts = _benchmark_city_facts()
    facts.append(
        _existing_zfa_fact(
            value=None, rank="unknown", fact_id="f-efa-unknown", source=None,
            note=_EFA_UNKNOWN_NOTE,
        )
    )
    doc = build_evaluator_inputs(_study(facts), _OPTION_ID)
    assert doc["contract_version"] == "1.0.0"
    assert "existing_building" not in doc


def test_unknown_plan_value_is_rejected() -> None:
    with pytest.raises(EvaluatorInputsError, match="is not one of"):
        build_evaluator_inputs(
            _study(_benchmark_city_facts()), _OPTION_ID, existing_building_plan="demolish"
        )


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


def test_assumption_governs_only_when_no_sourced_fact_exists() -> None:
    # lot_depth has ONLY a stated assumption (no city/sourced/entered depth): the
    # assumption governs and displaces nothing (plan section 9; section 3 step 4).
    facts = [f for f in _benchmark_city_facts() if f["key"] != "lot_depth"]
    facts.append(_fact("lot_depth", 98, "assumed", "f-depth-assumed", _ASSUMPTION))
    doc = build_evaluator_inputs(_study(facts), _OPTION_ID)

    depth = _record(doc, "lot_depth_ft")
    assert depth["fact_id"] == "f-depth-assumed"
    assert depth["rank"] == "assumed"
    assert depth["label"] == "Assumed"
    assert depth["source_kind"] == "assumption"
    assert depth["displaced"] == []  # an assumption never overrides a value
    # Assumed is weakest of all, so it wins the weakest-input label.
    assert doc["site_measurement_rank"] == "assumed"


def test_assumption_beside_a_sourced_fact_raises() -> None:
    # An assumption recorded BESIDE a city value for the same input is a visible conflict:
    # never silently governing, never silently discarded (CLAUDE.md principles 3 and 4).
    facts = _benchmark_city_facts()  # already carries a city lot_depth
    facts.append(_fact("lot_depth", 98, "assumed", "f-depth-assumed", _ASSUMPTION))
    with pytest.raises(
        EvaluatorInputsError, match="a stated assumption conflicts with a recorded value"
    ):
        build_evaluator_inputs(_study(facts), _OPTION_ID)


def test_conflicting_same_rank_values_raise() -> None:
    # Two city_records lot areas disagreeing on the value for one lot is a visible
    # conflict, named by both fact ids - never silently resolved by fact id (review F2).
    facts = _benchmark_city_facts()
    facts.append(_fact("lot_area", 5200, "city_records", "f-area-city-2", _CITY))
    with pytest.raises(EvaluatorInputsError) as excinfo:
        build_evaluator_inputs(_study(facts), _OPTION_ID)
    message = str(excinfo.value)
    assert "conflicting city_records values for lot_area_sq_ft" in message
    assert "f-area-city" in message and "f-area-city-2" in message


def test_same_rank_same_value_collapses() -> None:
    # Two city_records lot areas with the SAME value collapse to one governing record.
    facts = _benchmark_city_facts()
    facts.append(
        _fact("lot_area", _benchmark_value("lot_area"), "city_records", "f-area-city-2", _CITY)
    )
    doc = build_evaluator_inputs(_study(facts), _OPTION_ID)
    area = _record(doc, "lot_area_sq_ft")
    assert area["rank"] == "city_records"
    assert area["fact_id"] in {"f-area-city", "f-area-city-2"}
    assert area["displaced"] == []  # the duplicate collapses, it is not an override


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
    # one scalar is out of scope, so the adapter raises instead of guessing. The fixture's
    # address ("1 Synthetic Test Street") names NEITHER frontage street, so the R138
    # address-street exception does not fire and the fail-closed error stands.
    corner = json.loads(_CORNER_STUDY.read_text("utf-8"))
    with pytest.raises(EvaluatorInputsError, match="resolves to 2 distinct site facts"):
        build_evaluator_inputs(corner, "opt-a")


# --------------------------------------------------------------------------
# R138: corner-lot front lot line as a disclosed assumption (address street)
# --------------------------------------------------------------------------

def test_corner_front_lot_line_selected_from_the_address_street() -> None:
    # Two frontages (Northern Boulevard, 215 Place); the property address names Northern
    # Boulevard, so it is selected as the governing lot_front_ft - read from its own fact,
    # at its own tax-map rank, not guessed.
    study = _study_with_address(_two_frontage_corner_facts(), _benchmark_identity_address())
    doc = build_evaluator_inputs(study, _OPTION_ID)
    front = _record(doc, "lot_front_ft")
    assert front["value"] == 103.88
    assert front["fact_id"] == "f-front-northern"
    assert front["rank"] == "approximate_tax_map"
    assert front["source_kind"] == "tax_map_computation"
    # The other street's frontage is not a governing input and not in depends_on_fact_ids.
    assert "f-front-northern" in doc["depends_on_fact_ids"]
    assert "f-front-215place" not in doc["depends_on_fact_ids"]


def test_corner_front_lot_line_fails_closed_when_address_names_no_frontage() -> None:
    # An address that names neither frontage street is not a match: keep the fail-closed
    # multi-street error (requirement a).
    study = _study_with_address(_two_frontage_corner_facts(), "1 Nowhere Avenue")
    with pytest.raises(EvaluatorInputsError, match="resolves to 2 distinct site facts"):
        build_evaluator_inputs(study, _OPTION_ID)


def test_corner_front_lot_line_fails_closed_when_address_absent() -> None:
    # No confirmed address (the BBL-only read): nothing to match, so the fail-closed error
    # stands (requirement a).
    study = _study_with_address(_two_frontage_corner_facts(), None)
    with pytest.raises(EvaluatorInputsError, match="resolves to 2 distinct site facts"):
        build_evaluator_inputs(study, _OPTION_ID)


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


def test_three_answer_inputs_carry_the_scenario_objects_inert() -> None:
    # M5-T134: build_three_answer_inputs carries the property profile, the prepared tax-map outline
    # and the site geometry onto ThreeAnswerInputs VERBATIM as additive, INERT carriers; omitting
    # them leaves each None (not produced; no default stands for a fact). The engine reads none of
    # them - the byte-identity proof lives in test_wiring_emits_nothing.py.
    doc = build_evaluator_inputs(_study(_benchmark_city_facts()), _OPTION_ID)
    sentinel_profile = {"identity": {"bbl": "4073340070"}}
    sentinel_outline = object()
    sentinel_geometry = object()
    carried = build_three_answer_inputs(
        doc, results_id="res-evi-carry", computed_at="2026-10-03T00:00:00Z",
        housing_program="standard_residence", overlay_present=True,
        special_district_present=False, within_100_ft_of_street_line_intersection=True,
        street_line_intersection_angle_degrees=90.0, special_density_area=False,
        property_profile=sentinel_profile, prepared_outline=sentinel_outline,
        site_geometry=sentinel_geometry,
    )
    assert carried.property_profile is sentinel_profile
    assert carried.prepared_outline is sentinel_outline
    assert carried.site_geometry is sentinel_geometry
    # omitted (every existing caller) -> each carrier is None
    default = _three_answer_inputs(doc)
    assert default.property_profile is None
    assert default.prepared_outline is None
    assert default.site_geometry is None


# --------------------------------------------------------------------------
# contract: the documented invalid shapes fail validation
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "name",
    [
        "entered_labelled_city_records.json",
        "governing_record_without_fact_id.json",
        "unknown_rank.json",
        "assumed_record_displaces_a_fact.json",
        "existing_building_plan_city_source_basis.json",
        "existing_building_non_null_with_1_0_0_version.json",
    ],
)
def test_invalid_fixtures_fail_validation(name: str) -> None:
    from app.contracts.study_contracts import validate_evaluator_inputs_document

    path = _FIXTURE_ROOT / "invalid" / "evaluator_inputs" / name
    document = json.loads(path.read_text("utf-8"))
    assert isinstance(document.pop(FIXTURE_ONLY_KEY, None), str), "annotation missing"
    with pytest.raises(StudyContractError, match="failed canonical schema validation"):
        validate_evaluator_inputs_document(document)
