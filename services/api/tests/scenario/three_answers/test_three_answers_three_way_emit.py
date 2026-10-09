"""Acceptance pack for the three-way emit (task M5-T136, scenarios S1-S21).

The transform :func:`app.scenario.three_answers.three_way_document.emit_three_way_document` turns
the engine's assembled results document plus the decision ways into the contract-1.3.0 three-way
document. These tests run the emit path - the adapter on the recorded benchmark lot, and the
transform directly on made-up lots - and check EACH input state against the reference cases
(docs/reference-cases/R6B/cases), never against the engine's saved output (work order rule 3; owner
rule 5). Every expected figure here is loaded from a reference case; a wiring/unchanged equality is
never counted as evidence a value is correct (that lives in test_wiring_emits_nothing.py, S12).

One test per input state, each with its own id; the producer report holds the table 'state,
outcome, test id'. The red proofs (the engine's own block still carries the withheld number) sit
beside the green assertions here; the mutation proofs (one per pinned branch) are run in a copy
OUTSIDE the repository and recorded in the producer report.
"""

from __future__ import annotations

import http.client
import json
import math
import re
import socket
from pathlib import Path

import pytest

from app.contracts.evaluator_inputs import build_evaluator_inputs, build_three_answer_inputs
from app.contracts.study_setup_bridge import study_from_study_setup
from app.profile.builder import build_property_profile
from app.scenario.three_answers import (
    BuildingDefaults,
    ResultsContractError,
    generate_results,
    validate_results_document,
)
from app.scenario.three_answers.engine_conditions import (
    DensityStatement,
    Derived,
    Presence,
    Source,
    derive_conditions,
)
from app.scenario.three_answers.result_way_engine_bridge import (
    run_engine_and_result_ways,
    run_engine_and_result_ways_from_evidence,
)
from app.scenario.three_answers.result_way_inputs import (
    AreaAgreement,
    DensityKnowledge,
    LotAreaFigures,
    LotType,
    Recorded,
)
from app.scenario.three_answers.result_ways import decide_result_ways
from app.scenario.three_answers.three_way_document import (
    ADDON_GAIN_FOLLOWS_WITHHELD_BUILDING_OPTION,
    BEST_COMBINATION_FOLLOWS_WITHHELD_BUILDING_OPTION,
    BUILDING_OPTION_POINTS_TO_ALTERNATIVES,
    FLOOR_PLATES_FOLLOW_FIRST_OPTION,
    FLOOR_STACK_FOLLOWS_WITHHELD_BUILDING_OPTION,
    FLOOR_STACK_GIVEN_IN_ALTERNATIVES,
    FLOOR_TO_FLOOR_KEY,
    HOUSING_PROGRAM_KEY,
    RESERVED_UNIT_ESTIMATE_REASON,
    SHORTFALL_FOLLOWS_WITHHELD_BUILDING_OPTION,
    STANDARD_UNIT_LIMIT_NOT_AVAILABLE_REASON,
    STANDARD_UNIT_LIMIT_NOT_AVAILABLE_RESOLVED_BY,
    UNIT_ESTIMATE_GIVEN_IN_ALTERNATIVES,
    emit_three_way_document,
)
from app.scenario.three_answers.three_way_scope_lines import (
    _scope_statement,
    _user_choice_statement,
)
from app.spatial.corner_reach_area import (
    STATE_MEASURED,
    STATE_ONE_CONFIRMED_STREET,
    STATE_OUTLINE_REFUSED,
    CornerPortionAreas,
)
from app.spatial.site_geometry import (
    derive_site_geometry,
    lot_outline_from_mappluto,
    street_data_from_pages,
)
from app.spatial.site_geometry.labels import tax_map_value, unknown_value
from app.spatial.site_geometry.outline import prepare_outline
from tests.api.test_study_read_api import _TEST_ONLY_OPTION
from tests.contracts.test_evaluator_inputs import _benchmark_identity_address
from tests.contracts.test_study_setup_bridge import _LANE_ON, _OPTION_ID, _REVISION, _northern_setup
from tests.spatial._northern_replay import (
    DCM_ENVELOPE,
    replay_dcm_page,
    replay_lot_geometry,
    replay_pluto,
)

from .test_result_ways_lib import (
    base_inputs,
    benchmark_reach,
    c2_reach,
    c3_reach,
    k20,
    plain_inputs,
    support_all,
)
from .test_three_answers_benchmark import _ON, _benchmark_inputs

_REPO_ROOT = Path(__file__).resolve().parents[5]
_CASES = _REPO_ROOT / "docs" / "reference-cases" / "R6B" / "cases"
_JOURNEY_FIXTURE = (
    _REPO_ROOT / "packages" / "contracts" / "fixtures" / "valid" / "results"
    / "recorded_215_16_northern_journey.json"
)

_STUDY_ID = "study-215-16-northern-journey"
_RESULTS_ID = "res-215-16-northern-journey"
_COMPUTED_AT = "2026-10-03T00:00:00Z"


# --------------------------------------------------------------------------- reference cases
def _ref_rows(case: str) -> dict:
    data = json.loads((_CASES / f"{case}.json").read_text("utf-8"))
    return {row["row_id"]: row for row in data["rows"]}


def _ref_value(case: str, row_id: str):
    return _ref_rows(case)[row_id]["expected"]["value"]


# --------------------------------------------------------------------------- the benchmark emit
def _carriers():
    lot, _unused = lot_outline_from_mappluto(replay_lot_geometry())
    streets = street_data_from_pages([replay_dcm_page()], envelope=DCM_ENVELOPE)
    geometry = derive_site_geometry(lot, streets)
    prepared, _reason = prepare_outline(lot)
    profile = build_property_profile(replay_pluto())
    return profile, prepared, geometry


def _benchmark_adapter(mp, *, special_density_statement=None, profile_on=True, geometry_on=True,
                       env=None):
    def _blocked(*_a, **_k):
        raise AssertionError("network I/O attempted in a recorded-data test")

    mp.setattr(http.client.HTTPConnection, "connect", _blocked)
    mp.setattr(http.client.HTTPSConnection, "connect", _blocked)
    mp.setattr(socket, "create_connection", _blocked)

    profile, prepared, geometry = _carriers()
    setup = _northern_setup(mp, geometry=True)
    setup["property"]["address"] = _benchmark_identity_address()
    study = study_from_study_setup(setup, _TEST_ONLY_OPTION, study_id=_STUDY_ID, revision=_REVISION)
    doc = build_evaluator_inputs(study, _OPTION_ID)
    inputs = build_three_answer_inputs(
        doc, results_id=_RESULTS_ID, computed_at=_COMPUTED_AT,
        housing_program="standard_residence", overlay_present=True,
        special_district_present=False, within_100_ft_of_street_line_intersection=True,
        street_line_intersection_angle_degrees=90.0, special_density_area=False, study=study,
        property_profile=profile if profile_on else None,
        prepared_outline=prepared if geometry_on else None,
        site_geometry=geometry if geometry_on else None,
    )
    return run_engine_and_result_ways(
        inputs, evaluator_inputs=doc, special_density_statement=special_density_statement,
        env=_LANE_ON if env is None else env,
    )


@pytest.fixture(scope="module")
def benchmark():
    """The benchmark lot emitted once through the adapter (the recorded pack, offline)."""
    with pytest.MonkeyPatch.context() as mp:
        res = _benchmark_adapter(mp)
    return res


# --------------------------------------------------------------------------- made-up emit path
def _emit_made_up(*, lot_area, lot_type, way_inputs, overlay_present=False):
    """Run the engine on a made-up lot and the transform over its document and the given ways."""
    engine_inputs = _benchmark_inputs(
        lot_area_sq_ft=float(lot_area), lot_type=lot_type, overlay_present=overlay_present,
        lot_area_fact_id="pluto:made-up:lotarea", scope_inputs=None,
    )
    engine_doc = generate_results(engine_inputs, env=_ON).document
    emitted = emit_three_way_document(engine_doc, decide_result_ways(way_inputs))
    return engine_doc, emitted


def _value(answer: dict, key: str):
    return next((v for v in answer["values"] if v["key"] == key), None)


def _states(answer: dict) -> dict:
    return answer.get("value_states", {})


def _all_result_numbers(node) -> list[float]:
    """Every number carried on a VALUE object, the unit_estimate, floor_by_floor, floor_stack,
    shortfall, best_combination or an add-on gain - i.e. numbers that are RESULTS, not prose."""
    out: list[float] = []

    def walk(n):
        if isinstance(n, bool):
            return
        if isinstance(n, (int, float)):
            out.append(float(n))
        elif isinstance(n, dict):
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)

    doc = node
    for ans in doc["answers"].values():
        if ans.get("status") == "available":
            walk(ans["values"])  # numbers on shown value objects only (not value_states prose)
    for key in ("floor_by_floor", "floor_stack", "shortfall", "best_combination", "addon_gains"):
        walk(doc.get(key))
    ue = doc.get("unit_estimate", {})
    if isinstance(ue, dict) and ue.get("status") == "available":
        walk(ue)
    return out


# =========================================================================== S1
def test_s1_benchmark_emits_contract_1_4_0(benchmark):
    """S1: the emitted document validates and declares 1.4.0 (the first-building-option additive
    blocks are attached for the conflicting-area benchmark, M5-T146); floor_area_allowance and
    permitted_envelope are available and each carries a value_states map; remaining_floor_area is
    still 'Not confirmed'; the shown floor-area and height numbers equal docs/reference-cases/R6B/
    cases/real-lot.json, never the engine's saved output."""
    doc = benchmark.document
    validate_results_document(doc)
    assert doc["contract_version"] == "1.4.0"
    fa = doc["answers"]["floor_area_allowance"]
    env = doc["answers"]["permitted_envelope"]
    assert fa["status"] == "available" and "value_states" in fa
    assert env["status"] == "available" and "value_states" in env
    assert doc["remaining_floor_area"] == {
        "status": "not_available",
        "reason": "Needs verified zoning-lot boundaries and existing zoning floor area.",
        "reason_kind": "missing_input",
    }
    # real-lot.json L1 (20,150) and L2 (24,180); heights L3 (30/45/55) and L4 (65).
    assert _ref_value("real-lot", "L1") == 20150
    assert _value(fa, "max_residential_floor_area")["value"] == _ref_value("real-lot", "L1")
    assert _value(
        fa, "max_residential_floor_area_qualifying_affordable_or_senior"
    )["value"] == _ref_value("real-lot", "L2") == 24180
    heights_text = str(_ref_value("real-lot", "L3")) + str(_ref_value("real-lot", "L4"))
    for key, ft in (
        ("min_base_height", 30.0), ("max_base_height", 45.0), ("max_building_height", 55.0),
        ("max_building_height_qualifying_affordable_or_senior", 65.0),
    ):
        assert _value(env, key)["value"] == ft
        assert f"{int(ft)} ft" in heights_text, key


# =========================================================================== S2
def test_s2_five_results_placed_per_owner_decision(benchmark):
    """S2 / owner R567: rear_yard and setback_above_base appear ONLY as value_states of
    permitted_envelope; the three legal unit limits ONLY as value_states of floor_area_allowance;
    none of the five appears in any answer's values[] (all withheld on the benchmark)."""
    doc = benchmark.document
    fa, env = doc["answers"]["floor_area_allowance"], doc["answers"]["permitted_envelope"]
    for key in ("rear_yard", "setback_above_base"):
        assert key in _states(env)
        assert key not in _states(fa)
    for key in (
        "legal_unit_limit_standard", "legal_unit_limit_qualifying_affordable",
        "legal_unit_limit_qualifying_senior",
    ):
        assert key in _states(fa)
        assert key not in _states(env)
    placed = {
        "rear_yard", "setback_above_base", "legal_unit_limit_standard",
        "legal_unit_limit_qualifying_affordable", "legal_unit_limit_qualifying_senior",
    }
    for answer in doc["answers"].values():
        if answer.get("status") == "available":
            assert not ({v["key"] for v in answer["values"]} & placed)


# =========================================================================== S3
def test_s3_coverage_withdrawn_agrees_with_the_by_portion_block(benchmark):
    """S3 / W11 (a): max_lot_coverage is absent from permitted_envelope.values[] and present as a
    withheld value_states entry that AGREES with the coverage_by_portion block - same reason, kind
    (a missing fact) and resolver, because the two lot areas disagree. No coverage percentage or
    footprint appears as a result number."""
    doc = benchmark.document
    env = doc["answers"]["permitted_envelope"]
    assert _value(env, "max_lot_coverage") is None
    state = _states(env)["max_lot_coverage"]
    block = doc["coverage_by_portion"]
    assert state["way"] == "withheld"
    assert block["status"] == "withheld"
    assert state["reason"] == block["reason"]
    assert state["gap_kind"] == block["gap_kind"] == "missing_information"
    assert state["resolved_by"] == block["resolved_by"]
    # the coverage percentage (100) never appears as a result number
    assert 100.0 not in _all_result_numbers(benchmark.document)


# =========================================================================== S4
def test_s4_rear_yard_withheld_not_not_required(benchmark):
    """S4 / DB-189, M5-T144: the rear yard is a withheld value_states entry; geometry.yards is
    not_available with that same withheld reason, NEVER the older whole-lot 'not required'. On the
    benchmark the C2-2 overlay no longer blocks the rear yard (M5-T144): it is withheld by the
    corner/reach logic (the far corner 144.60 ft is beyond the waiver area), for a missing property
    fact, and the reason no longer mentions the overlay."""
    doc = benchmark.document
    env = doc["answers"]["permitted_envelope"]
    rear = _states(env)["rear_yard"]
    assert rear["way"] == "withheld"
    assert rear["gap_kind"] == "missing_information"
    assert rear["reason"].startswith("The corner rear-yard waiver does not cover the whole lot: ")
    assert "144.60 ft" in rear["reason"]
    assert "overlay" not in rear["reason"].lower()
    yards = doc["geometry"]["yards"]
    assert yards["status"] == "not_available"
    assert yards["reason"] == rear["reason"]  # geometry follows the withheld result's reason
    assert yards["reason_kind"] == "missing_input"
    assert "not_required" not in json.dumps(yards)
    assert "not required" not in yards["reason"].lower()


def test_s4_rear_yard_reach_reason_carried_on_a_non_overlay_corner_lot():
    """DB-189 / O29 on the independent reading: a corner lot with the real lot's reach and NO
    overlay surfaces the module's reach reason (the far corner 144.60 ft from the corner point); the
    transform carries it verbatim into geometry.yards - never 'not required'. Expected reach from
    corner-reach.json real-lot-reach."""
    _engine, emitted = _emit_made_up(
        lot_area=10075, lot_type="corner",
        way_inputs=plain_inputs(
            lot_type=LotType.CORNER, reach=benchmark_reach(),
            area=LotAreaFigures(10075.0, AreaAgreement.DISAGREES, 10388.0),
            large_lot_threshold_met=False, **k20(False),
        ),
    )
    rear = _states(emitted["answers"]["permitted_envelope"])["rear_yard"]
    assert rear["way"] == "withheld"
    assert "144.60 ft" in rear["reason"]
    assert "144.60" in _ref_value("corner-reach", "real-lot-reach")
    assert emitted["geometry"]["yards"]["reason"] == rear["reason"]
    assert "not required" not in emitted["geometry"]["yards"]["reason"].lower()


# =========================================================================== S5
def test_s5_no_withheld_result_carries_a_number_anywhere(benchmark):
    """S5 / O31: no withheld result (coverage, rear yard, setback, building option, the three unit
    limits) carries a number anywhere. floor_by_floor is empty; floor_stack, shortfall and
    best_combination are not available, each naming the withheld result; every add-on gain is not
    available; the numbers 10,075 (a floor's area), 29 (the unit figure) and 100 (the coverage
    percent) appear nowhere as a result. RED PROOF: the engine's own blocks still carry them."""
    doc = benchmark.document
    engine = benchmark.engine_result.document

    assert doc["floor_by_floor"] == []
    assert doc["floor_stack"]["status"] == "not_available"
    # W11 (b): on the benchmark the list carries each building's floor schedule, so floor_stack says
    # where the schedule is given (building_alternatives); shortfall and best_combination are not
    # carried by the list, so they keep their follows-withheld reasons.
    assert doc["floor_stack"]["reason"] == FLOOR_STACK_GIVEN_IN_ALTERNATIVES
    assert doc["shortfall"]["status"] == "not_available"
    assert doc["shortfall"]["reason"] == SHORTFALL_FOLLOWS_WITHHELD_BUILDING_OPTION
    assert doc["best_combination"]["status"] == "not_available"
    assert doc["best_combination"]["reason"] == BEST_COMBINATION_FOLLOWS_WITHHELD_BUILDING_OPTION
    assert all(g["gain"]["status"] == "not_available" for g in doc["addon_gains"])
    for g in doc["addon_gains"]:
        if g["gain"]["reason"] == ADDON_GAIN_FOLLOWS_WITHHELD_BUILDING_OPTION:
            break
    else:
        raise AssertionError("no add-on gain carries the follows-withheld reason")

    result_numbers = _all_result_numbers(doc)
    assert 10075.0 not in result_numbers  # a floor plate / floor area of the withheld option
    assert 29.0 not in result_numbers  # the withheld unit figure
    assert 100.0 not in result_numbers  # the withheld coverage percent

    # RED PROOF (one per block): the engine's own blocks DO carry those numbers, so leaving any one
    # as the engine made it makes its number reappear and this test would fail.
    engine_numbers = _all_result_numbers(engine)
    assert 10075.0 in engine_numbers  # engine floor_by_floor / floor_stack / plate
    assert 29.0 in engine_numbers  # engine unit_estimate
    assert 100.0 in engine_numbers  # engine coverage
    assert engine["floor_by_floor"] != []
    assert engine["floor_stack"]["status"] == "available"
    assert engine["best_combination"]["status"] == "available"
    assert any(g["gain"]["status"] == "available" for g in engine["addon_gains"])


# =========================================================================== S6
def test_s6_unit_estimate_holds_no_legal_figure(benchmark):
    """S6 / O28: the emitted unit_estimate carries no legal number, no formula, no factor; it is the
    shared not-available shape whose reason begins 'Not known', names the Preliminary capacity
    estimate and says it is not built yet, never 'unsupported'; reason_kind is rule_not_implemented
    and the block has no gap_kind field. RED PROOF: the engine's inner block still holds 29 and the
    formula, and passing it through unchanged fails this test."""
    doc = benchmark.document
    ue = doc["unit_estimate"]
    # W11 (b): on the benchmark the list carries each building's estimate, so unit_estimate says
    # where the estimate is given (building_alternatives) and claims nothing else - no 'not built
    # yet' beside the list; still no legal figure, formula or factor.
    assert ue == {
        "status": "not_available",
        "reason": UNIT_ESTIMATE_GIVEN_IN_ALTERNATIVES,
        "reason_kind": "rule_not_implemented",
    }
    assert "building_alternatives" in ue["reason"]
    assert "not built yet" not in ue["reason"]
    assert "unsupported" not in ue["reason"].lower()
    assert "gap_kind" not in ue  # the shared not_available shape has no gap_kind here
    for banned in ("value", "formula", "factor"):
        assert banned not in ue
    # RED PROOF: the engine's inner block (which nothing but the adapter reads) still holds it.
    inner = benchmark.engine_result.document["unit_estimate"]
    assert inner["status"] == "available"
    assert inner["value"] == 29
    assert inner["formula"] == "20,150 ÷ 680 = 29.63"


# =========================================================================== S7
def test_s7_conditional_values_name_their_assumptions(benchmark):
    """S7: each shown value carries a conditional value_states entry naming its assumption(s) (the
    unchecked K20 conditions, and for floor area the recorded-area condition); the height limits are
    the district's limits and nowhere 'the maximum for this property'; no reason or label contains
    'professional review'."""
    doc = benchmark.document
    fa, env = doc["answers"]["floor_area_allowance"], doc["answers"]["permitted_envelope"]
    far = _states(fa)["max_residential_floor_area"]
    assert far["way"] == "conditional"
    assumptions = " ".join(c["assumption"] for c in far["conditions"])
    assert "recorded lot area of 10,075 sq ft" in assumptions  # the recorded-area condition (K5)
    for name in ("waterfront", "airport height", "transit easement", "a lot close to a district"):
        assert name in assumptions  # the four unchecked K20 conditions
    for key in ("min_base_height", "max_building_height"):
        assert _states(env)[key]["way"] == "conditional"
    blob = json.dumps(doc).lower()
    assert "professional review" not in blob
    assert "the maximum for this property" not in blob


# =========================================================================== S8
def test_s8_user_density_statement_is_conditional_only():
    """S8 / R255: with the user's statement that the lot is not in a special density area the
    legal_unit_limit_standard is a conditional value_states entry naming that statement, never
    settled; without it, withheld; a statement that contradicts the record (it IS in one) is held
    back, so the limit stays withheld. Run through the adapter on the benchmark lot."""
    with pytest.MonkeyPatch.context() as mp:
        with_stmt = _benchmark_adapter(mp, special_density_statement=True)
    with pytest.MonkeyPatch.context() as mp:
        without = _benchmark_adapter(mp, special_density_statement=None)
    with pytest.MonkeyPatch.context() as mp:
        contradicts = _benchmark_adapter(mp, special_density_statement=False)

    fa_with = with_stmt.document["answers"]["floor_area_allowance"]
    std = _states(fa_with)["legal_unit_limit_standard"]
    assert std["way"] == "conditional"
    assert any(c["kind"] == "user_statement" for c in std["conditions"])
    # the statement is not stored as a sourced fact anywhere in the document
    assert "as the user states" in json.dumps(std)
    without_fa = without.document["answers"]["floor_area_allowance"]
    assert _states(without_fa)["legal_unit_limit_standard"]["way"] == "withheld"
    contra_fa = contradicts.document["answers"]["floor_area_allowance"]
    assert _states(contra_fa)["legal_unit_limit_standard"]["way"] == "withheld"
    assert contradicts.gathered.held_back  # the contradicting statement is held back (R255)


# =========================================================================== S9
def test_s9_made_up_interior_lot_shown_floor_area():
    """S9: a made-up interior R6B lot of 5,355 sq ft; the floor-area value is 10,710 (settled when
    the K20 conditions are supplied checked-and-absent); the legal unit limit is withheld without
    density evidence and conditional (16) with the user's statement. Expected values from
    docs/reference-cases/R6B/cases/interior-lots.json (P5)."""
    base_ways = dict(
        lot_type=LotType.INTERIOR, area=LotAreaFigures(5355.0, AreaAgreement.AGREES, 5355.0),
    )
    # without density evidence: floor area settled (K20 absent), unit limit withheld
    _engine, settled = _emit_made_up(
        lot_area=5355, lot_type="interior",
        way_inputs=plain_inputs(**base_ways, **k20(True)),
    )
    fa = settled["answers"]["floor_area_allowance"]
    assert _value(fa, "max_residential_floor_area")["value"] == _ref_value(
        "interior-lots", "P5-floor-area"
    ) == 10710
    assert _states(fa)["max_residential_floor_area"]["way"] == "settled"
    assert _states(fa)["legal_unit_limit_standard"]["way"] == "withheld"
    assert _value(fa, "legal_unit_limit_standard") is None

    # conditional when the K20 conditions are not checked
    _e2, conditional = _emit_made_up(
        lot_area=5355, lot_type="interior",
        way_inputs=plain_inputs(**base_ways, **k20(False)),
    )
    assert _states(conditional["answers"]["floor_area_allowance"])[
        "max_residential_floor_area"
    ]["way"] == "conditional"


# =========================================================================== S10
def test_s10_made_up_corner_lot_coverage_from_reach():
    """S10: made-up corner lots C2 (60x80) and C3 (150x100) with the K20 conditions checked-and-
    absent. C2: coverage 100 percent settled and no rear yard required anywhere (shown in geometry,
    not a withheld entry). C3: coverage withheld (no single figure) and the rear yard withheld. With
    the K20 conditions not checked the same coverage figure is conditional. corner-reach.json."""
    # C2
    _e, c2 = _emit_made_up(
        lot_area=4800, lot_type="corner",
        way_inputs=plain_inputs(
            lot_type=LotType.CORNER, reach=c2_reach(),
            area=LotAreaFigures(4800.0, AreaAgreement.AGREES, 4800.0),
            large_lot_threshold_met=False, **k20(True),
        ),
    )
    env2 = c2["answers"]["permitted_envelope"]
    assert _value(env2, "max_lot_coverage")["value"] == 100.0
    assert _states(env2)["max_lot_coverage"]["way"] == "settled"
    # a settled rear yard carries no number, so it is not a value_states entry; it shows in geometry
    assert "rear_yard" not in _states(env2)
    assert c2["geometry"]["yards"]["status"] == "available"
    assert c2["geometry"]["yards"]["entries"][0]["status"] == "not_required"
    assert _ref_value("corner-reach", "C2-coverage") == "100 percent"
    assert "no rear yard required anywhere" in _ref_value("corner-reach", "C2-rear-yard")

    # C2 with the K20 conditions not checked -> coverage conditional
    _e2b, c2n = _emit_made_up(
        lot_area=4800, lot_type="corner",
        way_inputs=plain_inputs(
            lot_type=LotType.CORNER, reach=c2_reach(),
            area=LotAreaFigures(4800.0, AreaAgreement.AGREES, 4800.0),
            large_lot_threshold_met=False, **k20(False),
        ),
    )
    assert _states(c2n["answers"]["permitted_envelope"])["max_lot_coverage"]["way"] == "conditional"

    # C3
    _e3, c3 = _emit_made_up(
        lot_area=15000, lot_type="corner",
        way_inputs=plain_inputs(
            lot_type=LotType.CORNER, reach=c3_reach(),
            area=LotAreaFigures(15000.0, AreaAgreement.AGREES, 15000.0),
            large_lot_threshold_met=False, **k20(True),
        ),
    )
    env3 = c3["answers"]["permitted_envelope"]
    assert _value(env3, "max_lot_coverage") is None
    assert _states(env3)["max_lot_coverage"]["way"] == "withheld"
    assert _states(env3)["rear_yard"]["way"] == "withheld"
    assert _ref_rows("corner-reach")["C3-coverage"]["expected"]["kind"] == "not_known"
    assert _ref_rows("corner-reach")["C3-rear-yard"]["expected"]["kind"] == "not_known"


# =========================================================================== S11
def test_s11_a_fact_not_given_withholds_only_its_dependents():
    """S11 / R229, R240: with no site geometry (reach unknown) only the reach-dependent results are
    withheld and the others are unchanged; with no property profile every recorded column is not
    read and every result is withheld. A column not read is never taken as 'none'; never a zero."""
    with pytest.MonkeyPatch.context() as mp:
        no_geom = _benchmark_adapter(mp, geometry_on=False)
    with pytest.MonkeyPatch.context() as mp:
        no_profile = _benchmark_adapter(mp, profile_on=False)

    # no geometry: coverage (needs the reach) withheld; the floor area unchanged (still conditional)
    env = no_geom.document["answers"]["permitted_envelope"]
    assert _states(env)["max_lot_coverage"]["way"] == "withheld"
    fa = no_geom.document["answers"]["floor_area_allowance"]
    assert _states(fa)["max_residential_floor_area"]["way"] == "conditional"

    # no profile: every recorded column is not read, so every answer is withheld
    for name in ("floor_area_allowance", "permitted_envelope", "building_option"):
        assert no_profile.document["answers"][name]["status"] == "not_available"
    # never a zero anywhere among result numbers
    assert 0.0 not in _all_result_numbers(no_profile.document)


# =========================================================================== S15
def test_s15_validator_refuses_a_number_in_a_withheld_result(benchmark):
    """S15: the already-merged way-rule and the schema refuse a shown value marked withheld and a
    withheld entry carrying a number; NO new validator rule is added. The emitted document itself
    satisfies the invariant (it validated in S1)."""
    doc = benchmark.document
    # a shown value marked withheld in value_states is refused
    broken = json.loads(json.dumps(doc))
    env = broken["answers"]["permitted_envelope"]
    env["value_states"]["max_building_height"] = {
        "way": "withheld", "label": "x", "reason": "x", "gap_kind": "work_owed", "resolved_by": "x",
    }
    with pytest.raises(ResultsContractError):
        validate_results_document(broken)
    # a withheld entry carrying a number is refused by the schema (closed branch)
    broken2 = json.loads(json.dumps(doc))
    broken2["answers"]["permitted_envelope"]["value_states"]["max_lot_coverage"]["value"] = 100
    with pytest.raises(ResultsContractError):
        validate_results_document(broken2)


# =========================================================================== S16
def test_s16_nothing_is_activated(benchmark):
    """S16 / R584: engine.py is byte-identical and never names the decision module; the engine's
    inner document still declares 1.2.0; and no file under services/api/app calls generate_results
    except the one adapter."""
    app_root = Path(__file__).resolve().parents[3] / "app"
    engine_src = (app_root / "scenario" / "three_answers" / "engine.py").read_text("utf-8")
    assert "result_way" not in engine_src
    assert benchmark.engine_result.document["contract_version"] == "1.2.0"
    callers = [
        str(p.relative_to(app_root)) for p in app_root.rglob("*.py")
        if p.name != "engine.py" and re.search(r"generate_results\s*\(", p.read_text("utf-8"))
    ]
    assert callers == ["scenario/three_answers/result_way_engine_bridge.py"], callers


# =========================================================================== S19
def test_s19_standard_unit_limit_shown_with_its_formula():
    """S19 / O32: the made-up interior lot of 5,355 sq ft with the user's density statement puts ONE
    value object in floor_area_allowance.values[] with key legal_unit_limit_standard, value 16, unit
    dwelling_units, the dwelling-unit law section, the rule table among its sources, and a label
    that prints the formula, the factor and the rounding rule; its way is conditional and names the
    statement; unit_estimate stays reserved. Without the statement no such value exists and 16
    appears nowhere. Expected value from interior-lots.json (P5-units)."""
    ways = dict(
        lot_type=LotType.INTERIOR, area=LotAreaFigures(5355.0, AreaAgreement.AGREES, 5355.0),
    )
    _engine, shown = _emit_made_up(
        lot_area=5355, lot_type="interior",
        way_inputs=plain_inputs(**ways, special_density=DensityKnowledge.USER_STATEMENT_NOT_IN_ONE,
                                **k20(True)),
    )
    fa = shown["answers"]["floor_area_allowance"]
    obj = _value(fa, "legal_unit_limit_standard")
    assert obj is not None
    assert obj["value"] == _ref_value("interior-lots", "P5-units") == 16
    assert obj["unit"] == "dwelling_units"
    assert "ZR 23-52" in obj["zr_sections"]
    assert any(
        s["kind"] == "rule_table" and "r6b-dwelling-units" in s["ref"] for s in obj["sources"]
    )
    # the label prints the formula, the factor and the rounding rule in words (work order H10)
    assert "10,710 ÷ 680 = 15.75" in obj["label"]
    assert "680" in obj["label"] and "rounds up only at .75 or more" in obj["label"]
    assert _states(fa)["legal_unit_limit_standard"]["way"] == "conditional"
    assert shown["unit_estimate"]["status"] == "not_available"  # still reserved

    # without the statement: no value object, and 16 appears nowhere as a result
    _e2, hidden = _emit_made_up(
        lot_area=5355, lot_type="interior",
        way_inputs=plain_inputs(**ways, **k20(True)),
    )
    fa2 = hidden["answers"]["floor_area_allowance"]
    assert _value(fa2, "legal_unit_limit_standard") is None
    assert 16.0 not in _all_result_numbers(hidden)


# =========================================================================== S20
def test_s20_engine_switched_off_emits_no_number():
    """S20: with the engine's lane switch off the emitted document validates, carries no number of
    any result, and invents no way entry for a value that is not shown; unit_estimate is the
    reserved block (never a figure)."""
    with pytest.MonkeyPatch.context() as mp:
        off = _benchmark_adapter(mp, env={})  # lane A off
    doc = off.document
    validate_results_document(doc)
    assert doc["contract_version"] == "1.3.0"
    for name in ("floor_area_allowance", "permitted_envelope", "building_option"):
        ans = doc["answers"][name]
        assert ans["status"] == "not_available"
        assert "value_states" not in ans  # no invented way entry on a not-available answer
    assert doc["unit_estimate"]["status"] == "not_available"
    assert "value" not in doc["unit_estimate"]
    assert _all_result_numbers(doc) == []


# =========================================================================== S21
def test_s21_overlay_support_tied_to_the_reference_rows_at_the_adapter(benchmark):
    """S21 / DB-190(c), M5-T144: the benchmark lot has a recorded C2-2 overlay. The floor area,
    heights and coverage families read 'same as plain R6B' and are not blocked by the overlay; the
    rear yard is NO LONGER blocked by the overlay either (the step-P5 row zr-34-23-page resolved
    the step-P4 caveat), so it is decided by the corner/reach logic - here still withheld, now for
    a missing property fact (the far corner is beyond the waiver area), its reason no longer naming
    the overlay. The test reads the reference rows and runs the ADAPTER, not only the overlay
    table."""
    doc = benchmark.document
    # the overlay-reading reference rows: these families read 'same as plain R6B'
    overlay = _ref_rows("overlay-reading")
    for row_id in (
        "floor-area-ratio", "lot-coverage", "base-and-building-height", "dwelling-units",
    ):
        assert "same as plain R6B" in overlay[row_id]["expected"]["value"]
    # the overlay is recorded present on this lot.
    assert benchmark.gathered.recorded.commercial_overlay.code == "C2-2"
    env = doc["answers"]["permitted_envelope"]
    rear = _states(env)["rear_yard"]
    assert rear["way"] == "withheld"
    assert rear["gap_kind"] == "missing_information"  # the plain corner/reach rule, not the overlay
    assert "overlay" not in rear["reason"].lower()
    # the floor-area and height families are shown (the overlay reading supports them)
    fa = doc["answers"]["floor_area_allowance"]
    assert _states(fa)["max_residential_floor_area"]["way"] == "conditional"
    assert _states(env)["max_building_height"]["way"] == "conditional"


# =========================================================================== text guard
def test_every_text_the_transform_writes_is_plain_and_true(benchmark):
    """Rule L3: every text the transform WRITES carries no internal name (no gap/reading number, no
    task id, no 'the caller', 'reference case', 'module'), never 'professional review', never
    'unsupported', and no claim about which law text is captured. The transform's authored texts are
    its module constants."""
    authored = [
        RESERVED_UNIT_ESTIMATE_REASON,
        FLOOR_STACK_FOLLOWS_WITHHELD_BUILDING_OPTION,
        SHORTFALL_FOLLOWS_WITHHELD_BUILDING_OPTION,
        BEST_COMBINATION_FOLLOWS_WITHHELD_BUILDING_OPTION,
        ADDON_GAIN_FOLLOWS_WITHHELD_BUILDING_OPTION,
        STANDARD_UNIT_LIMIT_NOT_AVAILABLE_REASON,
        STANDARD_UNIT_LIMIT_NOT_AVAILABLE_RESOLVED_BY,
        # M5-T146: the first-building-option texts the transform writes when the list is present.
        BUILDING_OPTION_POINTS_TO_ALTERNATIVES,
        UNIT_ESTIMATE_GIVEN_IN_ALTERNATIVES,
        FLOOR_STACK_GIVEN_IN_ALTERNATIVES,
        FLOOR_PLATES_FOLLOW_FIRST_OPTION,  # W14 c second round: the true floor-plates reason
    ]
    # the one text the transform builds at run time: the shown unit-limit value object label
    with pytest.MonkeyPatch.context() as mp:
        emit = _benchmark_adapter(mp, special_density_statement=True)
    # the benchmark unit limit is withheld (overlay), so build a shown one on a made-up lot
    _e, shown = _emit_made_up(
        lot_area=5355, lot_type="interior",
        way_inputs=plain_inputs(
            lot_type=LotType.INTERIOR, area=LotAreaFigures(5355.0, AreaAgreement.AGREES, 5355.0),
            special_density=DensityKnowledge.USER_STATEMENT_NOT_IN_ONE, **k20(True),
        ),
    )
    label = _value(shown["answers"]["floor_area_allowance"], "legal_unit_limit_standard")["label"]
    authored.append(label)

    # the two design-choice sentences the transform writes when the user made the choice (M5-T139):
    # the floor-to-floor height entered, and each of the three housing programs selected
    authored.append(_user_choice_statement(FLOOR_TO_FLOOR_KEY, 14.0))
    for program in (
        "standard_residence", "qualifying_affordable_housing", "qualifying_senior_housing",
    ):
        authored.append(_user_choice_statement(HOUSING_PROGRAM_KEY, program))

    id_re = re.compile(r"\b[KO]\d+\b|\bM\d+-T\d+\b")
    forbidden = (
        "professional review", "unsupported", "the caller", "reference case", "work order",
        "orchestrator", "not captured", "is captured", "captured text", "gap k", "gap-",
    )
    for text in authored:
        low = text.lower()
        for token in forbidden:
            assert token not in low, (token, text)
        assert not id_re.search(text), text
        assert emit.document is not None  # the adapter path is exercised (non-vacuous)


# =========================================================================== M5-T137
# The engine's five conditions come from evidence (not a typed-in value). The committed journey
# result is regenerated THROUGH the new entry below; these tests pin its honesty.
def _scope_rows(doc: dict) -> dict:
    return {a["key"]: a for a in doc["scope"]["assumptions"]}


def test_s137_red_committed_within_100_scope_line_agrees_with_the_measured_reach():
    """S3 RED PROOF: the committed journey result's within-100 scope line must not say the lot is
    (assumed) within 100 feet while the SAME document's coverage reason says the lot reaches BEYOND
    the 100-ft corner-lot portion. Before the fix the scope says 'assumed to lie within 100 feet'
    (value True, basis assumed) - the contradiction this task removes; after it the line is the
    measured corner reach (144.60 ft, more than 100 feet)."""
    doc = json.loads(_JOURNEY_FIXTURE.read_text("utf-8"))
    # W11 (a): the coverage is withheld by portion (the two lot areas disagree); the single
    # whole-lot figure carries no number. It no longer repeats the reach wording - that lives on
    # the scope line below - so the two never contradict.
    coverage_state = doc["answers"]["permitted_envelope"]["value_states"]["max_lot_coverage"]
    assert coverage_state["way"] == "withheld"
    assert coverage_state["reason"] == doc["coverage_by_portion"]["reason"]
    within = _scope_rows(doc)["within_100_ft_of_street_line_intersection"]
    assert within["value"] is False, within  # not (assumed) within 100 feet
    assert "assumed to lie within 100 feet" not in within["statement"]
    assert within["basis"] != "assumed"  # a measured basis, not a bare assumption
    assert "144.60 feet" in within["statement"]  # the measured corner reach


# The dependency map (research Q1a): which shown results each engine condition can affect. A
# stand-in on any of them forbids a shown dependent (owner R229/R240; scenario S11). None means the
# condition feeds the engine's whole-document gate (special district -> review; overlay not-read ->
# every residential result withheld by the decision step), so NOTHING may be shown.
_CONDITION_DEPENDENTS: dict[str, set[str] | None] = {
    "special_district_present": None,
    "overlay_present": None,
    "within_100_ft_of_street_line_intersection": {"rear_yard"},
    "street_line_intersection_angle_degrees": {"rear_yard"},
    "special_density_area": {"legal_unit_limit_standard"},
}


def _shown_result_keys(doc: dict) -> set[str]:
    """Every result the emitted document SHOWS (settled or conditional): the value_states entries
    whose way is settled/conditional, plus the rear yard when it is shown in geometry.yards (a
    settled rear yard carries no number, so it is not a value_states entry)."""
    shown: set[str] = set()
    for name in ("floor_area_allowance", "permitted_envelope", "building_option"):
        answer = doc["answers"].get(name, {})
        if answer.get("status") != "available":
            continue
        for key, state in answer.get("value_states", {}).items():
            if state.get("way") in ("settled", "conditional"):
                shown.add(key)
    geometry = doc.get("geometry")
    yards = geometry.get("yards") if isinstance(geometry, dict) else None
    if isinstance(yards, dict) and yards.get("status") == "available":
        shown.add("rear_yard")
    return shown


def _assert_no_shown_result_rests_on_a_stand_in(doc: dict) -> None:
    """S11 / reading O35: no shown result (settled or conditional) rests on a stand-in. A condition
    is a stand-in exactly when its scope row's basis is 'assumed' (recorded -> city_records,
    measured -> approximate_tax_map, the user's statement -> entered; only not known / not
    applicable carry the stand-in with basis 'assumed'). Wherever a condition is a stand-in, every
    result that depends on it must be withheld."""
    rows = {a["key"]: a for a in doc["scope"]["assumptions"]}
    shown = _shown_result_keys(doc)
    for key, dependents in _CONDITION_DEPENDENTS.items():
        if rows[key]["basis"] != "assumed":
            continue  # a real source (recorded / measured / the user's statement): no stand-in
        if dependents is None:
            assert not shown, (key, shown)  # a stand-in on an all-affecting condition shows nothing
        else:
            assert not (dependents & shown), (key, dependents & shown)


@pytest.fixture(scope="module")
def evidence_benchmark():
    """The benchmark lot emitted once through the EVIDENCE entry (the five conditions derived from
    the recorded pack, offline), with no statement about the special density area."""
    with pytest.MonkeyPatch.context() as mp:
        res = _evidence(mp)
    return res


def _evidence(mp, *, special_density_statement=None, geometry_on=True, env=None,
              user_choices=None):
    def _blocked(*_a, **_k):
        raise AssertionError("network I/O attempted in a recorded-data test")

    mp.setattr(http.client.HTTPConnection, "connect", _blocked)
    mp.setattr(http.client.HTTPSConnection, "connect", _blocked)
    mp.setattr(socket, "create_connection", _blocked)

    profile, prepared, geometry = _carriers()
    setup = _northern_setup(mp, geometry=True)
    setup["property"]["address"] = _benchmark_identity_address()
    study = study_from_study_setup(setup, _TEST_ONLY_OPTION, study_id=_STUDY_ID, revision=_REVISION)
    doc = build_evaluator_inputs(study, _OPTION_ID)
    return run_engine_and_result_ways_from_evidence(
        evaluator_inputs=doc, study=study, results_id=_RESULTS_ID, computed_at=_COMPUTED_AT,
        housing_program="standard_residence", property_profile=profile,
        prepared_outline=prepared if geometry_on else None,
        site_geometry=geometry if geometry_on else None,
        special_density_statement=special_density_statement,
        user_choices=user_choices,
        env=_LANE_ON if env is None else env,
    )


def test_s137_shown_values_and_withheld_set_unchanged_through_evidence(evidence_benchmark):
    """S1/S2: through the evidence entry the shown floor-area figures and heights equal the
    reference cases exactly as before, and the coverage, rear yard, building option and unit limits
    are withheld exactly as before - nothing that is shown changed, only where each condition comes
    from. Expected figures from docs/reference-cases/R6B/cases/real-lot.json, never the saved
    output."""
    doc = evidence_benchmark.document
    validate_results_document(doc)
    assert doc["contract_version"] == "1.4.0"  # the first-building-option blocks are attached
    fa = doc["answers"]["floor_area_allowance"]
    env = doc["answers"]["permitted_envelope"]
    assert _ref_value("real-lot", "L1") == 20150
    assert _value(fa, "max_residential_floor_area")["value"] == 20150
    assert _value(
        fa, "max_residential_floor_area_qualifying_affordable_or_senior"
    )["value"] == _ref_value("real-lot", "L2") == 24180
    for key, ft in (("min_base_height", 30.0), ("max_base_height", 45.0),
                    ("max_building_height", 55.0),
                    ("max_building_height_qualifying_affordable_or_senior", 65.0)):
        assert _value(env, key)["value"] == ft
        assert _states(env)[key]["way"] == "conditional"
    # the withheld set is unchanged
    assert _states(env)["max_lot_coverage"]["way"] == "withheld"
    assert _states(env)["rear_yard"]["way"] == "withheld"
    assert _states(fa)["legal_unit_limit_standard"]["way"] == "withheld"
    assert doc["answers"]["building_option"]["status"] == "not_available"
    assert doc["unit_estimate"]["status"] == "not_available"


def test_s137_scope_lines_say_where_each_condition_comes_from(evidence_benchmark):
    """S3 (green): the five scope lines of the emitted benchmark document say where each condition
    comes from - overlay recorded, no special purpose district recorded, the lot not wholly within
    100 feet with the measured reach, the measured angle, the density not known. No line says 'this
    run does not read', and the within-100 line agrees with the coverage reason (no contradiction).
    """
    doc = evidence_benchmark.document
    rows = _scope_rows(doc)
    overlay_row = rows["overlay_present"]
    assert overlay_row["value"] is True and overlay_row["basis"] == "city_records"
    assert "recorded" in overlay_row["statement"].lower() and "C2-2" in overlay_row["statement"]
    district = rows["special_district_present"]
    assert district["value"] is False and district["basis"] == "city_records"
    assert "no special purpose district" in district["statement"].lower()
    within = rows["within_100_ft_of_street_line_intersection"]
    assert within["value"] is False and within["basis"] == "approximate_tax_map"
    assert "144.60 feet" in within["statement"] and "more than 100 feet" in within["statement"]
    angle = rows["street_line_intersection_angle_degrees"]
    assert angle["value"] == 89.7 and angle["basis"] == "approximate_tax_map"
    assert "89.7 degrees" in angle["statement"]
    density = rows["special_density_area"]
    assert density["statement"].lower().startswith("whether the lot is in a special density area")
    # a not-known condition shows the WORDS, never the stand-in the engine received (no "Yes")
    assert density["value"] == "Not known" and density["unit"] is None
    assert not isinstance(density["value"], bool)
    # no scope line claims the program does not read something it reads
    for row in doc["scope"]["assumptions"]:
        assert "does not read" not in row["statement"]
    # no contradiction (W11 a): the within-100 line is measured (the lot reaches beyond 100) and the
    # coverage value state agrees with the by-portion block (withheld; the two lot areas disagree).
    coverage_state = doc["answers"]["permitted_envelope"]["value_states"]["max_lot_coverage"]
    assert coverage_state["way"] == "withheld"
    assert coverage_state["reason"] == doc["coverage_by_portion"]["reason"]
    _assert_no_shown_result_rests_on_a_stand_in(doc)


def test_s137_invariant_over_the_benchmark_states(evidence_benchmark):
    """S11: no shown result rests on a stand-in, over the benchmark states the evidence entry
    produces - the benchmark (density not known), the benchmark with the user's density statement,
    and the benchmark with no site geometry (the corner reach not known)."""
    _assert_no_shown_result_rests_on_a_stand_in(evidence_benchmark.document)
    with pytest.MonkeyPatch.context() as mp:
        with_stmt = _evidence(mp, special_density_statement=True)
    _assert_no_shown_result_rests_on_a_stand_in(with_stmt.document)
    # the density is now the user's statement, so the unit limit may be shown (conditional)
    fa = with_stmt.document["answers"]["floor_area_allowance"]
    assert _states(fa)["legal_unit_limit_standard"]["way"] == "conditional"
    assert _scope_rows(with_stmt.document)["special_density_area"]["basis"] == "entered"
    with pytest.MonkeyPatch.context() as mp:
        no_geom = _evidence(mp, geometry_on=False)
    _assert_no_shown_result_rests_on_a_stand_in(no_geom.document)
    rows = _scope_rows(no_geom.document)
    # the reach is not known, so within-100 and the angle SHOW the words 'Not known' (never the
    # stand-in the engine received), and the rear yard is withheld
    within = rows["within_100_ft_of_street_line_intersection"]
    angle = rows["street_line_intersection_angle_degrees"]
    assert within["basis"] == "assumed" and within["value"] == "Not known"
    assert within["unit"] is None
    assert angle["value"] == "Not known" and angle["unit"] is None
    assert not isinstance(within["value"], bool) and not isinstance(angle["value"], (int, float))
    assert "not known" in within["statement"].lower()
    assert _states(no_geom.document["answers"]["permitted_envelope"])["rear_yard"]["way"] == (
        "withheld"
    )


def test_s137_invariant_special_district_not_read_withholds_everything():
    """S5/S11: when the special-district column was not read, the engine is given the present
    stand-in and the decision step withholds EVERY result, so the emitted document shows nothing
    that rests on the stand-in; the scope lines say the overlay and the special district are not
    known."""
    engine_doc = generate_results(
        _benchmark_inputs(special_district_present=True, overlay_present=False), env=_ON
    ).document
    ways = decide_result_ways(plain_inputs(special_purpose_district=Recorded.NOT_READ))
    conditions = derive_conditions(
        overlay_presence=Presence.NOT_READ, overlay_code=None,
        special_district_presence=Presence.NOT_READ,
        is_corner=True, reach_ft=None, angle_deg=None,
        density_statement=DensityStatement.NONE,
    )
    emitted = emit_three_way_document(engine_doc, ways, condition_sources=conditions)
    assert _shown_result_keys(emitted) == set()
    _assert_no_shown_result_rests_on_a_stand_in(emitted)
    rows = _scope_rows(emitted)
    district = rows["special_district_present"]
    overlay = rows["overlay_present"]
    assert district["basis"] == "assumed" and district["value"] == "Not known"
    assert "not known" in district["statement"].lower()
    assert overlay["basis"] == "assumed" and overlay["value"] == "Not known"
    assert "not known" in overlay["statement"].lower()
    # the words, never the stand-in the engine received (no 'Yes'/'No')
    assert not isinstance(district["value"], bool) and not isinstance(overlay["value"], bool)


def test_s137_interior_lot_scope_says_not_applicable():
    """S9: a made-up interior lot has no corner, so the within-100 and angle scope lines say they do
    not apply (no corner); nothing invented for a corner, and the rear yard is withheld."""
    engine_doc = generate_results(
        _benchmark_inputs(lot_type="interior", overlay_present=False), env=_ON
    ).document
    ways = decide_result_ways(plain_inputs(
        lot_type=LotType.INTERIOR, reach=None,
        area=LotAreaFigures(5355.0, AreaAgreement.AGREES, 5355.0), **k20(True),
    ))
    conditions = derive_conditions(
        overlay_presence=Presence.ABSENT, overlay_code=None,
        special_district_presence=Presence.ABSENT,
        is_corner=False, reach_ft=None, angle_deg=None,
        density_statement=DensityStatement.NONE,
    )
    emitted = emit_three_way_document(engine_doc, ways, condition_sources=conditions)
    rows = _scope_rows(emitted)
    within = rows["within_100_ft_of_street_line_intersection"]
    angle = rows["street_line_intersection_angle_degrees"]
    assert "not a corner lot" in within["statement"] and "does not apply" in within["statement"]
    assert "not a corner lot" in angle["statement"] and "does not apply" in angle["statement"]
    # a not-applicable corner condition SHOWS the words, never the made-up value (no 136 degrees)
    assert within["value"] == "Not applicable" and within["unit"] is None
    assert angle["value"] == "Not applicable" and angle["unit"] is None
    _assert_no_shown_result_rests_on_a_stand_in(emitted)


def test_s137_not_known_lines_show_words_never_a_boolean_or_number(evidence_benchmark):
    """A scope line of a condition that is not known (or does not apply) SHOWS the words 'Not known'
    / 'Not applicable', never the stand-in the engine received. Over every such line of the
    benchmark (density not known) and the no-geometry benchmark (reach not known), the value is one
    of those two strings and is never a boolean or a number - a reader never sees a substitute (e.g.
    'Yes') for something not known. This test FAILS if the transform shows the stand-in value."""
    docs = [evidence_benchmark.document]
    with pytest.MonkeyPatch.context() as mp:
        docs.append(_evidence(mp, geometry_on=False).document)
    seen_not_known = False
    for doc in docs:
        for row in doc["scope"]["assumptions"]:
            if row["key"] in _CONDITION_DEPENDENTS and row["basis"] == "assumed":
                seen_not_known = True
                assert row["value"] in ("Not known", "Not applicable"), row
                assert not isinstance(row["value"], bool), row
                assert not isinstance(row["value"], (int, float)), row
                assert row["unit"] is None, row
    assert seen_not_known  # the states above do carry a not-known condition (non-vacuous)


def test_s137_older_entry_leaves_the_scope_lines_as_the_engine_made_them(benchmark):
    """S12: the older entry (run_engine_and_result_ways), called with engine inputs the caller
    already holds and no condition sources, leaves the scope lines as the engine made them - the
    'assumed' flag disclosures, unchanged. Only the evidence entry rewrites them."""
    within = _scope_rows(benchmark.document)["within_100_ft_of_street_line_intersection"]
    assert within["basis"] == "assumed"
    assert within["statement"] == (
        "The lot is assumed to lie within 100 feet of a street-line intersection."
    )


def test_s137_scope_texts_are_plain_and_true():
    """S15 / rule L3: every scope line the transform writes for the five conditions is plain and
    true - no internal name (no gap or reading number, no task id, no 'module', 'reference case',
    'stand-in'), never 'professional review', and no machine code (snake_case). Every branch of the
    composer is covered."""
    battery: dict[str, list[Derived]] = {
        "overlay_present": [
            Derived(True, Source.RECORDED, code="C2-2"),
            Derived(False, Source.RECORDED),
            Derived(False, Source.NOT_KNOWN),
        ],
        "special_district_present": [
            Derived(True, Source.RECORDED),
            Derived(False, Source.RECORDED),
            Derived(True, Source.NOT_KNOWN),
        ],
        "within_100_ft_of_street_line_intersection": [
            Derived(False, Source.MEASURED, figure=144.60),
            Derived(True, Source.MEASURED, figure=100.00),
            Derived(False, Source.NOT_APPLICABLE),
            Derived(False, Source.NOT_KNOWN),
        ],
        "street_line_intersection_angle_degrees": [
            Derived(89.7, Source.MEASURED, figure=89.7),
            Derived(90.0, Source.MEASURED, figure=90.0),
            Derived(136.0, Source.NOT_APPLICABLE),
            Derived(136.0, Source.NOT_KNOWN),
        ],
        "special_density_area": [
            Derived(False, Source.USER_STATEMENT),
            Derived(True, Source.NOT_KNOWN),
        ],
    }
    texts = [_scope_statement(key, d) for key, variants in battery.items() for d in variants]
    id_re = re.compile(r"\b[KO]\d+\b|\bM\d+-T\d+\b")
    snake = re.compile(r"\b[a-z0-9]+(?:_[a-z0-9]+)+\b")
    forbidden = (
        "professional review", "unsupported", "the caller", "reference case", "work order",
        "orchestrator", "not captured", "is captured", "captured text", "gap k", "gap-",
        "stand-in", "module",
    )
    assert len(texts) == 16
    for text in texts:
        low = text.lower()
        for token in forbidden:
            assert token not in low, (token, text)
        assert not id_re.search(text), text
        assert not snake.search(text), text


# =========================================================================== M5-T139
# A choice the user made is said to be the user's choice (DB-204 a). The evidence entry learns which
# of the two design-choice scope rows the caller's request carried, and the transform rewrites those
# rows to say so (basis 'entered'); the value is never touched. When no choice is named, both rows
# stay exactly as the engine made them (the committed journey result is unchanged).
def test_t139_entry_without_user_choices_leaves_the_two_lines_as_the_engine_made_them(
    evidence_benchmark, benchmark
):
    """S4: the evidence entry called with NO user choice named, and the older entry
    (run_engine_and_result_ways), both leave the housing-program and floor-to-floor scope lines
    exactly as the engine's disclosure builder made them - basis 'default' and the engine's own
    'the default' sentences. Only a named choice rewrites them."""
    for doc in (evidence_benchmark.document, benchmark.document):
        rows = _scope_rows(doc)
        hp = rows[HOUSING_PROGRAM_KEY]
        f2f = rows[FLOOR_TO_FLOOR_KEY]
        assert hp["basis"] == "default"
        assert hp["statement"] == "Standard residence is used as the default housing program."
        assert f2f["basis"] == "default"
        assert f2f["statement"] == "A 10-foot floor-to-floor height is used as the default."


def test_t139_transform_rewrites_only_the_named_design_choice(evidence_benchmark):
    """O38: the transform rewrites a design-choice row ONLY when its key is named in user_choices.
    Naming the floor-to-floor height rewrites that row (basis 'entered', the entered sentence) and
    leaves the housing-program row at 'default'; naming the housing program does the reverse. The
    row's VALUE is never touched in either case."""
    engine_doc = evidence_benchmark.engine_result.document
    ways = evidence_benchmark.gathered.ways

    only_f2f = emit_three_way_document(
        engine_doc, ways, user_choices=frozenset({FLOOR_TO_FLOOR_KEY})
    )
    rows = _scope_rows(only_f2f)
    assert rows[FLOOR_TO_FLOOR_KEY]["basis"] == "entered"
    assert rows[FLOOR_TO_FLOOR_KEY]["value"] == 10.0  # value untouched
    assert rows[FLOOR_TO_FLOOR_KEY]["statement"] == (
        "A 10-foot floor-to-floor height was entered for this run."
    )
    assert rows[HOUSING_PROGRAM_KEY]["basis"] == "default"  # not named -> unchanged

    only_hp = emit_three_way_document(
        engine_doc, ways, user_choices=frozenset({HOUSING_PROGRAM_KEY})
    )
    rows2 = _scope_rows(only_hp)
    assert rows2[HOUSING_PROGRAM_KEY]["basis"] == "entered"
    assert rows2[HOUSING_PROGRAM_KEY]["value"] == "standard_residence"  # value untouched
    assert rows2[HOUSING_PROGRAM_KEY]["statement"] == (
        "Standard residence was selected for this run as the housing program."
    )
    assert rows2[FLOOR_TO_FLOOR_KEY]["basis"] == "default"  # not named -> unchanged


def test_t139_only_the_two_choice_lines_differ_with_user_choices(evidence_benchmark):
    """S5: the SAME lot and values through the evidence entry, with and without the user's choices.
    Only the basis and the statement of the housing-program and floor-to-floor rows differ; every
    value, unit, other scope line and other block of the document stay the same."""
    with pytest.MonkeyPatch.context() as mp:
        chosen = _evidence(mp, user_choices=frozenset({HOUSING_PROGRAM_KEY, FLOOR_TO_FLOOR_KEY}))
    d0 = evidence_benchmark.document
    d1 = chosen.document
    rows0 = _scope_rows(d0)
    rows1 = _scope_rows(d1)
    for key in (HOUSING_PROGRAM_KEY, FLOOR_TO_FLOOR_KEY):
        assert rows1[key]["value"] == rows0[key]["value"]  # value unchanged
        assert rows1[key]["unit"] == rows0[key]["unit"]  # unit unchanged
        assert rows0[key]["basis"] == "default"
        assert rows1[key]["basis"] == "entered"
        assert rows1[key]["statement"] != rows0[key]["statement"]

    def _blanked(doc: dict) -> dict:
        copy = json.loads(json.dumps(doc))
        for row in copy["scope"]["assumptions"]:
            if row["key"] in (HOUSING_PROGRAM_KEY, FLOOR_TO_FLOOR_KEY):
                row["basis"] = "<blanked>"
                row["statement"] = "<blanked>"
        return copy

    assert _blanked(d1) == _blanked(d0)  # nothing else moved


# =========================================================================== DB-199 gaps (M5-T143)
# Three states the three-way emitter lacked a test for (backlog DB-199 a, b, c). No app wording
# changes: the scope-line code moved behind the old import path and the two fallback texts were
# hoisted BYTE-IDENTICAL so the text guard above already covers them. NO behaviour of the emitter
# changes in this task.
# --- DB-199 (a): a completeness guard over the blocks of the emitted document (corrected) ---
# _all_result_numbers stays exactly as it is. The gap DB-199 (a) names is that a NEW block carrying
# a withheld result's number could pass every existing guard unseen, because _all_result_numbers
# walks only some blocks (a plain whole-document walk is not the answer: the document rightly
# carries numbers - coordinates, measurements, inputs, counts - outside the result blocks). This
# guard closes the hole by forcing EVERY block to be classified. The two result sets were read FROM
# _all_result_numbers above (not guessed): at the TOP LEVEL it walks each of these blocks whole, so
# every number inside them is a result number -
_RESULT_NUMBER_BLOCKS = frozenset({
    "addon_gains", "best_combination", "floor_by_floor", "floor_stack", "shortfall",
    "unit_estimate",
})
# - and INSIDE each answer it walks ONLY values[] (the shown value objects); it enters no other key.
_ANSWER_RESULT_KEYS = frozenset({"values"})

# Every OTHER top-level block carries no result number (one line each, saying what its numbers are):
_NO_RESULT_NUMBER_BLOCKS = {
    "answers": "entered in part: result numbers live inside each answer's values[]; keys below",
    "contract_version": "a contract-version identifier string",
    "results_id": "an identifier string",
    "study_id": "an identifier string",
    "option_id": "an identifier string",
    "revision": "a document revision counter (metadata), not a zoning result",
    "computed_at": "a timestamp string",
    "draft": "a draft flag (boolean)",
    "out_of_date": "an out-of-date flag (boolean)",
    "out_of_date_reason": "prose or null",
    "notices_count": "a count of notices (document metadata), not a zoning result",
    "depends_on_fact_ids": "fact identifier strings",
    "rule_versions": "rule id and version identifier strings",
    "completeness_line": "a prose status line",
    "status_strip": "a prose status strip",
    "lot_selection_statement": "a prose statement",
    "with_approvals_label": "a prose label",
    "street_width_case": "a street-width case label or identifier",
    "existing_building": "a fact block about the existing building (an input, not a result)",
    "remaining_floor_area": "a not_available status/reason block (carries no number)",
    "scope": (
        "scope assumptions: each condition's recorded/measured/entered value, a measurement (the "
        "corner reach, the angle) or a design-choice input (floor-to-floor) - inputs and "
        "measurements, not results"
    ),
    "geometry": (
        "not walked: polygon coordinates and the dimensions that draw the results. KNOWN DEFECT, "
        "pinned by the xfail test below and NOT covered by this guard: a withheld height's figure "
        "can remain here: for a corner lot in a recorded flood zone the withheld height limit (55) "
        "stays at geometry.envelope.tiers[0].top_ft, because _apply_geometry clears the envelope "
        "layer only when the coverage is withheld, never when a height is; the emitter's repair "
        "(the geometry must follow every withheld result) removes the xfail mark"
    ),
}

# The first-building-option blocks (contract 1.4.0, M5-T146 PART B). They carry result numbers, but
# worked by the step-P6 modules (first_building_options, preliminary_apartment_estimate), NOT by the
# engine, so they are NOT walked by _all_result_numbers (which checks the emitted numbers come from
# the engine). No WITHHELD result's number can hide here, so the DB-199 (a) hole cannot open in
# them: a withheld coverage carries NO number (its withheld branch has no numeric field) and a
# building that cannot be worked is ABSENT from the list, never a numeric placeholder.
_FIRST_OPTION_BLOCKS = {
    "building_alternatives": "worked (shown) alternatives; an unworkable building is absent, no 0",
    "coverage_by_portion": "available carries the footprint (shown); withheld carries NO number",
    "buildings_not_worked": "not-worked buildings; each entry is reason prose only, NO number",
}

# Every key INSIDE an answer other than values[] carries no result number:
_ANSWER_NO_RESULT_KEYS = {
    "status": "an availability flag string",
    "measurement": "the answer's measurement label and figure - a measurement, not a result",
    "value_states": "per-value way/reason/condition prose; a withheld entry carries no number",
    "reason": "prose (a not_available answer)",
    "reason_kind": "a reason-kind identifier string",
    "resolved_by": "prose (what would resolve the gap)",
    "gap_kind": "a gap-kind identifier string",
}


def _unclassified_blocks(doc: dict) -> list[str]:
    """Every top-level block, and every key inside each answer, must be classified above as a
    result-number block (walked by _all_result_numbers) or a no-result-number block (named, with a
    reason). Return the keys classified as NEITHER - the DB-199 (a) hole, where a new block could
    hide a withheld result's number unseen."""
    bad: list[str] = []
    classified_top = (
        _RESULT_NUMBER_BLOCKS | set(_NO_RESULT_NUMBER_BLOCKS) | set(_FIRST_OPTION_BLOCKS)
    )
    for key in doc:
        if key not in classified_top:
            bad.append(key)
    classified_answer = _ANSWER_RESULT_KEYS | set(_ANSWER_NO_RESULT_KEYS)
    for name, ans in doc.get("answers", {}).items():
        if not isinstance(ans, dict):
            continue
        for key in ans:
            if key not in classified_answer:
                bad.append(f"answers.{name}.{key}")
    return bad


def test_db199a_every_block_of_the_emitted_document_is_classified(benchmark, evidence_benchmark):
    """DB-199 (a): over the REAL emitted documents the existing guards use - the benchmark, the
    evidence benchmark, the made-up interior and corner lots, the lane-off and the no-profile
    documents - every top-level block and every key inside each answer is classified as a
    result-number block (walked by _all_result_numbers) or a no-result-number block (named, with a
    reason). A block in NEITHER set fails here, naming it. This is the guard the first version of
    this gap test lacked (it only showed a second helper could see an injected number; no guard of
    the real document used it)."""
    docs = [benchmark.document, evidence_benchmark.document]
    _e1, interior = _emit_made_up(
        lot_area=5355, lot_type="interior",
        way_inputs=plain_inputs(
            lot_type=LotType.INTERIOR, area=LotAreaFigures(5355.0, AreaAgreement.AGREES, 5355.0),
            **k20(True),
        ),
    )
    _e2, corner = _emit_made_up(
        lot_area=4800, lot_type="corner",
        way_inputs=plain_inputs(
            lot_type=LotType.CORNER, reach=c2_reach(),
            area=LotAreaFigures(4800.0, AreaAgreement.AGREES, 4800.0),
            large_lot_threshold_met=False, **k20(True),
        ),
    )
    docs += [interior, corner]
    with pytest.MonkeyPatch.context() as mp:
        docs.append(_benchmark_adapter(mp, env={}).document)  # lane A off (S20)
    with pytest.MonkeyPatch.context() as mp:
        docs.append(_benchmark_adapter(mp, profile_on=False).document)  # no property profile (S11)
    for doc in docs:
        assert _unclassified_blocks(doc) == [], _unclassified_blocks(doc)


def test_db199a_completeness_guard_catches_a_new_numeric_block(benchmark):
    """DB-199 (a) state: a NEW block carrying a number - at the top level, and inside an answer - is
    caught by the completeness guard (it is in neither set), so a withheld result's number can never
    be added in a new block unseen. MUTATION PROOFS (producer report): removing a name from either
    set makes the guard fail on the real document; skipping the inside-an-answer keys leaves the
    inside-an-answer case below unseen."""
    top_injected = json.loads(json.dumps(benchmark.document))
    top_injected["unreviewed_block"] = {"value": 100.0}
    assert "unreviewed_block" in _unclassified_blocks(top_injected)

    inside = json.loads(json.dumps(benchmark.document))
    name = next(n for n, a in inside["answers"].items() if a.get("status") == "available")
    inside["answers"][name]["unreviewed_value"] = 100.0
    assert f"answers.{name}.unreviewed_value" in _unclassified_blocks(inside)


def test_db199a_withheld_height_figure_leaks_into_geometry_known_defect():
    """S11 / DB-199 (a), REPAIRED in M5-T144 (owner row D-090-R661). A corner lot in a recorded
    flood zone, through the real engine and decide_result_ways: every height limit is withheld, so
    no height figure may remain anywhere in geometry. Before the repair the withheld
    max_building_height (55) sat at geometry.envelope.tiers[0].top_ft; now _apply_geometry clears
    geometry.envelope when the maximum building height is withheld (ruling C5), so no height figure
    remains. The strict-xfail mark was removed here: this is now an ordinary test that passes."""
    engine_doc = generate_results(
        _benchmark_inputs(
            lot_area_sq_ft=4800.0, lot_type="corner", overlay_present=False,
            lot_area_fact_id="pluto:made-up:lotarea", scope_inputs=None,
        ), env=_ON,
    ).document
    base = dict(
        lot_type=LotType.CORNER, reach=c2_reach(),
        area=LotAreaFigures(4800.0, AreaAgreement.AGREES, 4800.0),
        large_lot_threshold_met=False, **k20(True),
    )
    shown = emit_three_way_document(
        json.loads(json.dumps(engine_doc)), decide_result_ways(plain_inputs(**base)),
    )
    withheld = emit_three_way_document(
        json.loads(json.dumps(engine_doc)),
        decide_result_ways(plain_inputs(flood_zone=Recorded.PRESENT, **base)),
    )
    height_keys = {
        "min_base_height", "max_base_height", "max_building_height",
        "min_base_height_qualifying_affordable_or_senior",
        "max_base_height_qualifying_affordable_or_senior",
        "max_building_height_qualifying_affordable_or_senior",
    }
    states = _states(withheld["answers"]["permitted_envelope"])
    assert all(states[k]["way"] == "withheld" for k in height_keys)  # every height withheld here

    # the figures those heights WOULD have, from the shown emit of the same lot
    would_have = {
        v["key"]: float(v["value"])
        for v in shown["answers"]["permitted_envelope"]["values"] if v["key"] in height_keys
    }

    def _numbers(node, out):
        if isinstance(node, bool):
            return
        if isinstance(node, (int, float)):
            out.append(float(node))
        elif isinstance(node, dict):
            for v in node.values():
                _numbers(v, out)
        elif isinstance(node, list):
            for v in node:
                _numbers(v, out)

    geom_numbers: list[float] = []
    _numbers(withheld["geometry"], geom_numbers)
    leaked = sorted({f for f in would_have.values() if f in geom_numbers})
    assert leaked == [], f"withheld height figures still in geometry: {leaked}"


# ---------------------------------------------------------- S11-S14 the envelope follows the ways
def _corner_envelope_engine_doc():
    """A made-up R6B corner lot whose engine envelope geometry is AVAILABLE (top_ft set and a
    coverage footprint), so a withheld way has something to clear - the same engine doc the S11
    leak test uses."""
    return generate_results(
        _benchmark_inputs(
            lot_area_sq_ft=4800.0, lot_type="corner", overlay_present=False,
            lot_area_fact_id="pluto:made-up:lotarea", scope_inputs=None,
        ), env=_ON,
    ).document


def _emit_corner(**decide_overrides):
    engine_doc = _corner_envelope_engine_doc()
    base = dict(
        lot_type=LotType.CORNER, reach=c2_reach(),
        area=LotAreaFigures(4800.0, AreaAgreement.AGREES, 4800.0), **k20(True),
    )
    base.update(decide_overrides)
    return emit_three_way_document(
        json.loads(json.dumps(engine_doc)), decide_result_ways(plain_inputs(**base)),
    )


def test_s11_flood_zone_corner_height_withheld_envelope_cleared():
    """S11 / ruling C5: a flood-zone corner lot (every height withheld, coverage shown). The engine
    envelope is available (top_ft 55), but geometry.envelope becomes not_available carrying the
    withheld maximum-building-height reason; coverage is shown so it is the height reason alone."""
    withheld = _emit_corner(flood_zone=Recorded.PRESENT, large_lot_threshold_met=False)
    env = withheld["geometry"]["envelope"]
    assert env["status"] == "not_available"
    states = _states(withheld["answers"]["permitted_envelope"])
    assert states["max_building_height"]["way"] == "withheld"
    assert states["max_lot_coverage"]["way"] != "withheld"  # coverage shown here
    assert env["reason"] == states["max_building_height"]["reason"]  # the height reason alone
    assert env["reason_kind"] == "rule_not_implemented"  # flood height is work owed
    assert "55" not in env["reason"]  # no figure in the reason


def _envelope_way_reason(ways, key):
    """The reason of one permitted_envelope value's withheld way (read from the ways, because when
    every envelope value is withheld the emitted answer is a whole not-available with no
    value_states)."""
    return next(r for r in ways.permitted_envelope.values if r.key == key).way.reason


def test_s12_envelope_both_height_and_coverage_withheld_combined_reason():
    """S12 / ruling C5: a state where BOTH the maximum building height (flood) and the lot coverage
    (large lot) are withheld while the engine envelope was available. geometry.envelope is
    not_available with a reason naming the maximum building height FIRST then the lot coverage
    (fixed order), joined by one space; reason_kind is rule_not_implemented (both are work owed)."""
    base = dict(
        lot_type=LotType.CORNER, reach=c2_reach(),
        area=LotAreaFigures(4800.0, AreaAgreement.AGREES, 4800.0), **k20(True),
    )
    ways = decide_result_ways(plain_inputs(
        flood_zone=Recorded.PRESENT, large_lot_threshold_met=True, **base))
    emitted = emit_three_way_document(
        json.loads(json.dumps(_corner_envelope_engine_doc())), ways)
    env = emitted["geometry"]["envelope"]
    height_reason = _envelope_way_reason(ways, "max_building_height")
    coverage_reason = _envelope_way_reason(ways, "max_lot_coverage")
    assert env["status"] == "not_available"
    assert env["reason"] == f"{height_reason} {coverage_reason}"  # height first, then coverage
    assert env["reason"].index(height_reason) < env["reason"].index(coverage_reason)
    assert env["reason_kind"] == "rule_not_implemented"  # both contributors are work owed


def test_s12b_envelope_reason_kind_missing_input_when_no_contributor_is_work_owed():
    """S12 (precedence): when both withheld contributors are MISSING information (flood column not
    read; the large-lot question not stated) the envelope reason_kind is missing_input, not
    rule_not_implemented - the work_owed-wins precedence only lifts it when some contributor is
    work owed. The reason still names the height first then the coverage."""
    base = dict(
        lot_type=LotType.CORNER, reach=c2_reach(),
        area=LotAreaFigures(4800.0, AreaAgreement.AGREES, 4800.0), **k20(True),
    )
    ways = decide_result_ways(plain_inputs(
        flood_zone=Recorded.NOT_READ, large_lot_threshold_met=None, **base))
    emitted = emit_three_way_document(
        json.loads(json.dumps(_corner_envelope_engine_doc())), ways)
    env = emitted["geometry"]["envelope"]
    height_reason = _envelope_way_reason(ways, "max_building_height")
    coverage_reason = _envelope_way_reason(ways, "max_lot_coverage")
    assert env["status"] == "not_available"
    assert env["reason"] == f"{height_reason} {coverage_reason}"
    assert env["reason_kind"] == "missing_input"


def test_s13_envelope_height_shown_coverage_withheld_unchanged():
    """S13: height shown, coverage withheld (large lot). geometry.envelope is not_available with the
    coverage reason ALONE and its reason_kind - today's behaviour, preserved (exactly one withheld
    contributor)."""
    withheld = _emit_corner(large_lot_threshold_met=True)
    env = withheld["geometry"]["envelope"]
    states = _states(withheld["answers"]["permitted_envelope"])
    assert all(states[k]["way"] != "withheld" for k in (
        "min_base_height", "max_base_height", "max_building_height"))
    assert states["max_lot_coverage"]["way"] == "withheld"
    assert env["status"] == "not_available"
    assert env["reason"] == states["max_lot_coverage"]["reason"]  # coverage reason alone
    assert env["reason_kind"] == "rule_not_implemented"


def test_s14_envelope_height_and_coverage_shown_available():
    """S14: height shown and coverage shown. geometry.envelope stays AVAILABLE, exactly as the
    engine made it (a tier with a top_ft) - neither contributor is withheld, so nothing follows."""
    shown = _emit_corner(large_lot_threshold_met=False)
    env = shown["geometry"]["envelope"]
    states = _states(shown["answers"]["permitted_envelope"])
    assert states["max_building_height"]["way"] != "withheld"
    assert states["max_lot_coverage"]["way"] != "withheld"
    assert env["status"] == "available"
    assert env["tiers"][0]["top_ft"] is not None


def _interior_shown_limit_engine_and_ways():
    """A made-up interior R6B lot whose ways SHOW the standard unit limit (the user states the lot
    is not in a special density area, as in S19): the engine document and the ways."""
    engine_doc = generate_results(
        _benchmark_inputs(
            lot_area_sq_ft=5355.0, lot_type="interior", overlay_present=False,
            lot_area_fact_id="pluto:made-up:lotarea", scope_inputs=None,
        ), env=_ON,
    ).document
    ways = decide_result_ways(plain_inputs(
        lot_type=LotType.INTERIOR, area=LotAreaFigures(5355.0, AreaAgreement.AGREES, 5355.0),
        special_density=DensityKnowledge.USER_STATEMENT_NOT_IN_ONE, **k20(True),
    ))
    return engine_doc, ways


def test_db199b_shown_standard_limit_with_no_inner_block_is_withheld_with_no_number():
    """DB-199 (b): when the module SHOWS the standard unit limit but the engine's inner
    unit_estimate block is not available, the transform carries the limit as a WITHHELD value_state
    with its two exact texts and NO number - it never invents a figure (ruling B5 b; the fallback
    in _apply_answer reached by no test before this one). State: the interior lot whose ways show
    the limit, with the engine document's inner unit_estimate forced not-available before the
    transform runs. MUTATION PROOFS (producer report): changing the fallback's gap_kind, and
    reverting the fallback to append a value object with the figure, each turn this test red."""
    engine_doc, ways = _interior_shown_limit_engine_and_ways()
    # the figure this limit WOULD have for this lot, read from the UNFORCED engine document (16 for
    # this made-up lot); the forced document's result numbers are 2, 2.4, 30, 45, 55, 65, 10710,
    # 12852 - 16 is not among them, so the 'no number' assertion below genuinely bites.
    unforced = emit_three_way_document(json.loads(json.dumps(engine_doc)), ways)
    would_have = _value(unforced["answers"]["floor_area_allowance"], "legal_unit_limit_standard")
    would_have_value = float(would_have["value"])
    # now the engine's inner unit_estimate is not available for this lot
    engine_doc["unit_estimate"] = {
        "status": "not_available", "reason": "x", "reason_kind": "missing_input",
    }
    emitted = emit_three_way_document(engine_doc, ways)
    fa = emitted["answers"]["floor_area_allowance"]
    state = _states(fa)["legal_unit_limit_standard"]
    assert state["way"] == "withheld"
    assert state["reason"] == STANDARD_UNIT_LIMIT_NOT_AVAILABLE_REASON
    assert state["reason"] == (
        "The legal dwelling-unit limit is not known: the figure it would be read "
        "from is not available for this lot."
    )
    assert state["resolved_by"] == STANDARD_UNIT_LIMIT_NOT_AVAILABLE_RESOLVED_BY
    assert state["resolved_by"] == "A recorded lot area, or a survey or deed dimensions."
    assert state["gap_kind"] == "missing_information"  # the kind of gap the fallback writes
    # no value object for the limit, and the figure it would have (16) is not a result number
    assert _value(fa, "legal_unit_limit_standard") is None
    assert would_have_value not in _all_result_numbers(emitted)
    assert emitted["unit_estimate"]["status"] == "not_available"  # still the reserved block


def test_db199c_shown_standard_limit_carries_rule_table_source_with_the_list():
    """DB-199 (c), the REQUIREMENT: a shown standard unit limit carries its rule-table source when
    the engine document holds the rule-versions list. State: the interior lot whose ways show the
    limit, emitted with rule_versions present. MUTATION PROOF (producer report): forcing
    _rule_version to return None drops the rule-table source and this assertion fails."""
    engine_doc, ways = _interior_shown_limit_engine_and_ways()
    assert any(
        isinstance(r, dict) and r.get("rule_id") == "r6b-dwelling-units"
        for r in engine_doc["rule_versions"]
    )
    emitted = emit_three_way_document(json.loads(json.dumps(engine_doc)), ways)
    obj = _value(emitted["answers"]["floor_area_allowance"], "legal_unit_limit_standard")
    assert obj is not None
    kinds = {s["kind"] for s in obj["sources"]}
    assert "rule_table" in kinds and "zoning_resolution" in kinds
    assert any(
        s["kind"] == "rule_table" and "r6b-dwelling-units" in s["ref"] for s in obj["sources"]
    )


def test_db199c_missing_list_drops_rule_table_source_todays_behaviour_not_required():
    """DB-199 (c), TODAY'S BEHAVIOUR (NOT a requirement of this task): with the engine document's
    rule-versions list absent/empty the rule-table source of a shown standard unit limit is dropped
    silently and only the zoning-resolution source remains. Whether such a limit should instead be
    withheld is an OPEN question (backlog DB-199 c); this test pins only what the emitter does today
    and no behaviour of the emitter changes in this task."""
    engine_doc, ways = _interior_shown_limit_engine_and_ways()
    engine_doc["rule_versions"] = []
    emitted = emit_three_way_document(engine_doc, ways)
    obj = _value(emitted["answers"]["floor_area_allowance"], "legal_unit_limit_standard")
    assert obj is not None
    kinds = {s["kind"] for s in obj["sources"]}
    assert kinds == {"zoning_resolution"}  # the rule_table source is dropped; only ZR remains


# ========================================================================== W13 (M5-T146 part B)
# The first-building-option case where the two lot areas AGREE, and the case where the outline is
# NOT available, driven THROUGH the emitter: the measured corner-reach areas and the area
# comparison now reach emit_three_way_document from result_way_engine_bridge (ruling W13 b).
# Every expected figure is PARSED from the independent hand-worked example, never retyped.
_TOL_W13 = 0.01  # the reference records figures to two decimals; the module keeps them unrounded


def _p6_numbers_block(row_id: str) -> dict:
    data = json.loads((_CASES / "step-p6-worked.json").read_text("utf-8"))
    for row in data["rows"]:
        if row["row_id"] == row_id:
            return row["numbers_block"]
    raise AssertionError(f"row {row_id} not found in step-p6-worked.json")


def _made_up_interior_engine_doc():
    """A made-up interior R6B lot of 10,000 sq ft. It carries the scope block (so the emitter reads
    the lot type and the floor-to-floor assumption): FAR 2.00 -> allowance 20,000, min/max base
    30/45 ft - the made-up lot of step-P6 (made-up-footprint-a, made-up-building-a)."""
    return generate_results(
        _benchmark_inputs(
            lot_area_sq_ft=10000.0, lot_type="interior", overlay_present=False,
            lot_area_fact_id="pluto:made-up:lotarea",
        ), env=_ON,
    ).document


def _interior_one_street_corner_areas() -> CornerPortionAreas:
    """A one-confirmed-street measurement for an interior lot: its outline area is a known number
    but there is no corner to split, so the whole outline is the interior-lot portion (DB-212 b).
    The same shape the first_option_results S13 test builds."""
    return CornerPortionAreas(
        unknown_value("sq ft", "one street"), unknown_value("sq ft", "one street"),
        STATE_ONE_CONFIRMED_STREET, (),
    )


def test_w13_areas_agree_through_emitter_shows_footprint_and_building_a():
    """W13 (b) / S13 THROUGH THE EMITTER: an interior made-up lot of 10,000 sq ft whose recorded and
    outline areas AGREE, with the corner split measured. coverage_by_portion is AVAILABLE with the
    footprint (the interior ratio on the whole lot, 0.80 x 10,000 = 8,000, DB-212 b) and building A
    is listed beside building B. Expected building-A figures from step-p6-worked#made-up-building-a;
    nothing is called feasible."""
    engine_doc = _made_up_interior_engine_doc()
    ways = decide_result_ways(plain_inputs(
        lot_type=LotType.INTERIOR, area=LotAreaFigures(10000.0, AreaAgreement.AGREES, 10000.0),
        **k20(False),
    ))
    emitted = emit_three_way_document(
        engine_doc, ways,
        corner_areas=_interior_one_street_corner_areas(),
        lot_area=LotAreaFigures(10000.0, AreaAgreement.AGREES, 10000.0),
    )
    assert emitted["contract_version"] == "1.4.0"
    cov = emitted["coverage_by_portion"]
    assert cov["status"] == "available"
    assert math.isclose(cov["corner_portion_area_sqft"], 0.0, abs_tol=_TOL_W13)
    assert math.isclose(cov["interior_portion_area_sqft"], 10000.0, abs_tol=_TOL_W13)
    assert math.isclose(cov["interior_ratio"], 0.80, abs_tol=_TOL_W13)
    assert math.isclose(cov["corner_ratio"], 1.0, abs_tol=_TOL_W13)
    block_a = _p6_numbers_block("made-up-building-a")
    assert math.isclose(
        cov["footprint_sqft"], float(block_a["footprint_area_sqft"]), abs_tol=_TOL_W13
    )  # 8,000
    buildings = {a["building"] for a in emitted["building_alternatives"]}
    assert buildings == {"A", "B"}  # building A is now listed through the emitter
    a = next(x for x in emitted["building_alternatives"] if x["building"] == "A")
    assert a["storey_count"] == int(block_a["storey_count"]) == 2
    assert math.isclose(a["height_ft"], float(block_a["height_ft"]), abs_tol=_TOL_W13)  # 20
    assert math.isclose(
        a["total_floor_area_sqft"], float(block_a["total_floor_area_sqft"]), abs_tol=_TOL_W13
    )  # 16,000
    assert math.isclose(
        a["unused_floor_area_sqft"], float(block_a["unused_floor_area_sqft"]), abs_tol=_TOL_W13
    )  # 4,000
    assert a["below_min_base"] is True  # 20 ft < 30 ft
    assert "fit_note" not in a  # building A's footprint is the coverage footprint; no bound
    assert "feasible" not in json.dumps(emitted).lower()
    validate_results_document(emitted)


def test_w13_outline_not_available_through_emitter_withholds_coverage_and_lists_building_b():
    """W13 (b) THROUGH THE EMITTER: where the lot's outline is NOT available (the two areas could
    not be compared) coverage_by_portion is WITHHELD naming that - a missing fact about the property
    - and never computed from the recorded area; building B is listed as today and building A is
    absent."""
    engine_doc = _made_up_interior_engine_doc()
    ways = decide_result_ways(plain_inputs(
        lot_type=LotType.INTERIOR,
        area=LotAreaFigures(10000.0, AreaAgreement.COULD_NOT_COMPARE, None), **k20(False),
    ))
    emitted = emit_three_way_document(
        engine_doc, ways,
        corner_areas=CornerPortionAreas(
            unknown_value("sq ft", "no outline"), unknown_value("sq ft", "no outline"),
            STATE_OUTLINE_REFUSED, (),
        ),
        lot_area=LotAreaFigures(10000.0, AreaAgreement.COULD_NOT_COMPARE, None),
    )
    assert emitted["contract_version"] == "1.4.0"
    cov = emitted["coverage_by_portion"]
    assert cov["status"] == "withheld"
    assert cov["gap_kind"] == "missing_information"  # a missing fact about the property
    assert "outline is not available" in cov["reason"]
    assert "footprint_sqft" not in cov and "corner_portion_area_sqft" not in cov  # no number
    assert "recorded lot area is never used in its place" in cov["reason"]
    assert [a["building"] for a in emitted["building_alternatives"]] == ["B"]  # B lists, A absent
    validate_results_document(emitted)


def test_w13_areas_disagree_benchmark_blocks_unchanged_through_the_threaded_emitter(benchmark):
    """W13 (b) / requirement 3: where the two areas DISAGREE (the benchmark) nothing changes. The
    benchmark fixture now flows through the threaded bridge (run_engine_and_result_ways passes the
    measured corner-reach areas and the comparison), and its coverage_by_portion and
    building_alternatives are byte-equal to the committed journey document - proven here beside the
    journey test's whole-document byte comparison."""
    doc = benchmark.document
    committed = json.loads(_JOURNEY_FIXTURE.read_text("utf-8"))
    assert doc["coverage_by_portion"] == committed["coverage_by_portion"]
    assert doc["building_alternatives"] == committed["building_alternatives"]
    assert doc["coverage_by_portion"]["status"] == "withheld"
    assert "footprint_sqft" not in doc["coverage_by_portion"]  # no number on a withheld result


# ====================================================================== W14 (walkthrough F1)
# The document says WHY each building of the step-P6 method was not worked (buildings_not_worked),
# and the single building_option never states a false reason. Driven THROUGH the emitter here on
# the benchmark lot (areas disagree, overlay supported) at several floor-to-floor heights; the live
# route is driven in tests/api/test_results_read_api.py the way the 14 ft test drives it.
_BANNED_W14 = ("feasible", "complies", "preferred", "optimal")
_BENCH_RECORDED = 10075.0
_BENCH_ALLOWANCE = 20150.0
_LOWEST_RATIO = 0.80  # the lowest coverage ratio that can apply to the benchmark lot (W2)


def _benchmark_emit_at(f2f: float) -> dict:
    """The benchmark lot emitted through the transform at a given floor-to-floor height: the engine
    doc built with that height (so the scope carries it) and the benchmark decision ways (corner,
    areas DISAGREE, overlay supported so the floor area is shown). The measured corner-reach areas
    and the comparison are threaded exactly as result_way_engine_bridge threads them."""
    engine_doc = generate_results(
        _benchmark_inputs(building_defaults=BuildingDefaults(floor_to_floor_ft=float(f2f))),
        env=_ON,
    ).document
    ways = decide_result_ways(base_inputs(overlay_support=support_all(True)))
    corner = CornerPortionAreas(
        tax_map_value(100.0, "sq ft", "corner"), tax_map_value(9975.0, "sq ft", "interior"),
        STATE_MEASURED, (),
    )
    return emit_three_way_document(
        engine_doc, ways, corner_areas=corner,
        lot_area=LotAreaFigures(_BENCH_RECORDED, AreaAgreement.DISAGREES, 10388.0),
    )


def _not_worked(doc: dict, building: str) -> dict:
    return next(e for e in doc.get("buildings_not_worked", []) if e["building"] == building)


def test_w14_s25_sixteen_ft_no_building_worked_both_reasons_given():
    """S25 (the walkthrough's F1): at a floor-to-floor height of 16 ft NO building is listed.
    buildings_not_worked names building A (footprint withheld, the two areas disagree, missing
    information) and building B (ceil(30/16)=2 storeys, each a plan of allowance/2, above the bound
    = 80 percent of the recorded lot area, work owed). The single building_option points to both
    lists and no longer says the building is below the minimum base height."""
    doc = _benchmark_emit_at(16)
    assert doc["contract_version"] == "1.4.0"
    assert doc.get("building_alternatives") in (None, [])
    assert {e["building"] for e in doc["buildings_not_worked"]} == {"A", "B"}
    a = _not_worked(doc, "A")
    assert a["gap_kind"] == "missing_information" and a["reason"] == doc["coverage_by_portion"][
        "reason"
    ]
    b = _not_worked(doc, "B")
    assert b["gap_kind"] == "work_owed"
    storeys = math.ceil(30.0 / 16.0)  # 2
    plan = _BENCH_ALLOWANCE / storeys  # 10,075.00
    bound = _LOWEST_RATIO * _BENCH_RECORDED  # 8,060
    assert f"{storeys} storeys" in b["reason"]
    assert f"{plan:,.2f} sq ft" in b["reason"]  # 10,075.00
    assert f"{bound:,.0f} sq ft" in b["reason"]  # 8,060
    assert "80 percent of the recorded lot area" in b["reason"]
    assert "footprint" not in b["reason"]  # the bound is named truly, never "the footprint"
    bo = doc["answers"]["building_option"]
    assert bo["status"] == "not_available"
    assert "buildings_not_worked" in bo["reason"] and "building_alternatives" in bo["reason"]
    assert "below the minimum base height" not in bo["reason"]  # the false reason is gone


def test_w14_s26_twenty_five_ft_building_b_base_passes_maximum():
    """S26: at a floor-to-floor height of 25 ft building B is not worked because the fewest storeys
    reaching the minimum base height (ceil(30/25)=2 storeys, 50 ft) stand above the 45 ft maximum
    base height; building A is not worked (footprint withheld). Nothing feasible."""
    doc = _benchmark_emit_at(25)
    assert doc["contract_version"] == "1.4.0"
    assert doc.get("building_alternatives") in (None, [])
    b = _not_worked(doc, "B")
    assert b["gap_kind"] == "work_owed"
    storeys = math.ceil(30.0 / 25.0)  # 2
    height = storeys * 25.0  # 50
    assert f"{storeys} storeys standing {height:g} ft" in b["reason"]
    assert "maximum base height" in b["reason"]
    assert _not_worked(doc, "A")["gap_kind"] == "missing_information"


def test_w14_s27_building_b_listed_building_a_not_worked_at_10_and_14_ft():
    """S27: at 10 ft (the committed height) and 14 ft building B is LISTED and building A is in
    buildings_not_worked only (its footprint is the withheld coverage); each building is in exactly
    one list, and the regenerated benchmark changes only by building A's not-worked entry."""
    for f2f in (10, 14):
        doc = _benchmark_emit_at(f2f)
        assert [a["building"] for a in doc["building_alternatives"]] == ["B"]
        assert [e["building"] for e in doc["buildings_not_worked"]] == ["A"]
        worked = {a["building"] for a in doc["building_alternatives"]}
        not_worked = {e["building"] for e in doc["buildings_not_worked"]}
        assert not (worked & not_worked)  # exactly one list
        a = _not_worked(doc, "A")
        assert a["gap_kind"] == "missing_information"
        assert "disagree" in a["reason"] and "footprint" not in a["reason"].split(".")[0]
    committed = json.loads(_JOURNEY_FIXTURE.read_text("utf-8"))  # 10 ft is the committed height
    assert [e["building"] for e in committed["buildings_not_worked"]] == ["A"]


def test_w14_no_not_worked_reason_claims_feasible_or_preferred():
    """W14 / requirement 4: no reason in either building list claims the result is feasible,
    complies, preferred or optimal, at any of the walkthrough heights."""
    for f2f in (10, 14, 16, 25):
        doc = _benchmark_emit_at(f2f)
        for entry in (doc.get("building_alternatives") or []) + (
            doc.get("buildings_not_worked") or []
        ):
            blob = json.dumps(entry).lower()
            for banned in _BANNED_W14:
                assert banned not in blob, (f2f, banned, entry["building"])


# ==================================== W14 (c) second round: no false building-option text
_FALSE_BUILDING_OPTION_PHRASE = "below the minimum base height"


def _all_strings(node) -> list[str]:
    """Every string anywhere in the document (keys and values), so a false reason cannot hide in
    any block."""
    out: list[str] = []

    def walk(n):
        if isinstance(n, str):
            out.append(n)
        elif isinstance(n, dict):
            for key, value in n.items():
                out.append(key)
                walk(value)
        elif isinstance(n, list):
            for value in n:
                walk(value)

    walk(node)
    return out


def test_w14c_floor_plates_reason_is_the_true_placement_reason_on_the_benchmark():
    """W14 (c) second round: on the benchmark (first option applied) geometry.floor_plates no longer
    carries the decision module's older building-option text; it states the true reason - no
    placement is worked, so no floor plate is drawn - and points to the two building lists, with no
    base-height or rear-yard claim."""
    doc = _benchmark_emit_at(10)
    fp = doc["geometry"]["floor_plates"]
    assert fp["status"] == "not_available"
    assert fp["reason"].startswith("No floor plate is drawn: no placement on the lot is worked")
    assert "building_alternatives" in fp["reason"] and "buildings_not_worked" in fp["reason"]
    assert "minimum base height" not in fp["reason"]
    assert "rear yard" not in fp["reason"]
    assert fp["reason_kind"] == "rule_not_implemented"  # unchanged


def test_w14c_false_building_option_text_appears_in_no_emitted_string():
    """W14 (c) second round / requirement 3: the phrase 'below the minimum base height' appears in
    NO string of the emitted document - at 10, 14, 16 and 25 ft (the first option applied) and on a
    path where the floor-area allowance is NOT shown (the engine lane off). Through the emitter."""
    docs = [_benchmark_emit_at(f2f) for f2f in (10, 14, 16, 25)]
    with pytest.MonkeyPatch.context() as mp:
        docs.append(_benchmark_adapter(mp, env={}).document)  # lane A off: no floor-area allowance
    for doc in docs:
        for text in _all_strings(doc):
            assert _FALSE_BUILDING_OPTION_PHRASE not in text, text


def test_w14c_allowance_not_shown_building_option_states_only_what_is_true():
    """W14 (c) second round / requirement 2: on a path where the floor-area allowance is NOT shown
    (a blanket withhold - a recorded overlay with no supporting reading) the decision module's
    building-option text reaches the document, and it says ONLY that the program does not work a
    single building option - no base-height claim, no rear-yard claim, nothing about a building that
    was never worked. The geometry floor-plates layer carries the same true text (the first option
    is not applied, so it is not reconciled)."""
    _engine, doc = _emit_made_up(
        lot_area=10075, lot_type="corner", way_inputs=base_inputs(),  # overlay, no support -> blanket
    )
    assert doc["answers"]["floor_area_allowance"]["status"] != "available"  # allowance not shown
    reason = doc["answers"]["building_option"]["reason"]
    assert "this program does not work a single building option" in reason
    assert "minimum base height" not in reason
    assert "has not been checked against an independently worked example" not in reason
    assert "rear yard" not in reason
    floor_plates = doc["geometry"]["floor_plates"]
    assert "this program does not work a single building option" in floor_plates["reason"]
    assert "minimum base height" not in floor_plates["reason"]
