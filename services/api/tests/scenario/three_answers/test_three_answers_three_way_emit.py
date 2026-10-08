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
import re
import socket
from pathlib import Path

import pytest

from app.contracts.evaluator_inputs import build_evaluator_inputs, build_three_answer_inputs
from app.contracts.study_setup_bridge import study_from_study_setup
from app.profile.builder import build_property_profile
from app.scenario.three_answers import (
    ResultsContractError,
    generate_results,
    validate_results_document,
)
from app.scenario.three_answers.result_way_engine_bridge import run_engine_and_result_ways
from app.scenario.three_answers.result_way_inputs import (
    AreaAgreement,
    DensityKnowledge,
    LotAreaFigures,
    LotType,
)
from app.scenario.three_answers.result_ways import decide_result_ways
from app.scenario.three_answers.three_way_document import (
    ADDON_GAIN_FOLLOWS_WITHHELD_BUILDING_OPTION,
    BEST_COMBINATION_FOLLOWS_WITHHELD_BUILDING_OPTION,
    FLOOR_STACK_FOLLOWS_WITHHELD_BUILDING_OPTION,
    RESERVED_UNIT_ESTIMATE_REASON,
    SHORTFALL_FOLLOWS_WITHHELD_BUILDING_OPTION,
    emit_three_way_document,
)
from app.spatial.site_geometry import (
    derive_site_geometry,
    lot_outline_from_mappluto,
    street_data_from_pages,
)
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
    benchmark_reach,
    c2_reach,
    c3_reach,
    k20,
    plain_inputs,
)
from .test_three_answers_benchmark import _ON, _benchmark_inputs

_REPO_ROOT = Path(__file__).resolve().parents[5]
_CASES = _REPO_ROOT / "docs" / "reference-cases" / "R6B" / "cases"

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
def test_s1_benchmark_emits_contract_1_3_0(benchmark):
    """S1: the emitted document validates and declares 1.3.0; floor_area_allowance and
    permitted_envelope are available and each carries a value_states map; remaining_floor_area is
    still 'Not confirmed'; the shown floor-area and height numbers equal docs/reference-cases/R6B/
    cases/real-lot.json, never the engine's saved output."""
    doc = benchmark.document
    validate_results_document(doc)
    assert doc["contract_version"] == "1.3.0"
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
def test_s3_coverage_withdrawn_with_its_reach_reason(benchmark):
    """S3: max_lot_coverage is absent from permitted_envelope.values[] and present as a withheld
    value_states entry whose reason carries the measured reach (103.93 ft from the 215 Place street
    line, corner-reach.json real-lot-reach); no coverage percentage appears anywhere."""
    env = benchmark.document["answers"]["permitted_envelope"]
    assert _value(env, "max_lot_coverage") is None
    state = _states(env)["max_lot_coverage"]
    assert state["way"] == "withheld"
    assert "103.93 ft" in state["reason"] and "215 Place" in state["reason"]
    assert "103.93" in _ref_value("corner-reach", "real-lot-reach")
    # the coverage percentage (100) never appears as a result number
    assert 100.0 not in _all_result_numbers(benchmark.document)


# =========================================================================== S4
def test_s4_rear_yard_withheld_not_not_required(benchmark):
    """S4 / DB-189: the rear yard is a withheld value_states entry; geometry.yards is not_available
    with that same withheld reason, NEVER the older whole-lot 'not required'. On the benchmark the
    merged decision module blocks the rear yard on the recorded C2-2 overlay first, so the reason is
    the overlay reading owed (the module is read-only; see the producer report, question of law)."""
    doc = benchmark.document
    env = doc["answers"]["permitted_envelope"]
    rear = _states(env)["rear_yard"]
    assert rear["way"] == "withheld"
    yards = doc["geometry"]["yards"]
    assert yards["status"] == "not_available"
    assert yards["reason"] == rear["reason"]  # geometry follows the withheld result's reason
    assert "not_required" not in json.dumps(yards)
    assert "not required" not in yards["reason"].lower()
    # the module's benchmark reason is the overlay reading owed (the read-only module blocks first):
    assert "overlay" in rear["reason"].lower()


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
    assert doc["floor_stack"]["reason"] == FLOOR_STACK_FOLLOWS_WITHHELD_BUILDING_OPTION
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
    assert ue == {
        "status": "not_available",
        "reason": RESERVED_UNIT_ESTIMATE_REASON,
        "reason_kind": "rule_not_implemented",
    }
    assert ue["reason"].startswith("Not known")
    assert "Preliminary capacity estimate" in ue["reason"]
    assert "not built yet" in ue["reason"]
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
    """S21 / DB-190(c): the benchmark lot has a recorded C2-2 overlay; the rear yard is NOT
    supported by the overlay reading (overlay-reading.json / step-p4-worked), so it is withheld,
    while the floor area, heights and coverage families are not blocked by the overlay. The test
    reads the reference rows and runs the ADAPTER, not only the overlay table."""
    doc = benchmark.document
    # the overlay-reading reference rows: these families read 'same as plain R6B'
    overlay = _ref_rows("overlay-reading")
    for row_id in (
        "floor-area-ratio", "lot-coverage", "base-and-building-height", "dwelling-units",
    ):
        assert "same as plain R6B" in overlay[row_id]["expected"]["value"]
    # the merged reading (step-p4-worked) leaves the rear yard owed, so the adapter withholds it;
    # the overlay is recorded present on this lot.
    assert benchmark.gathered.recorded.commercial_overlay.code == "C2-2"
    env = doc["answers"]["permitted_envelope"]
    assert _states(env)["rear_yard"]["way"] == "withheld"
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
