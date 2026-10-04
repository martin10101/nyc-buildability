"""A-04 golden tests for the three-answer generator on the 215-16 Northern Blvd benchmark
(BBL 4073340070, lot 70), plan M1-14 / C-1 / C-2 / C-12; directive D-090.

Expected values are loaded from the benchmark contract fixture, never restated (the pattern
of ``tests/scenario/test_r6b_envelope_heights.py``). The generator must reproduce the
competitor-review section-A allowance (20,150 standard / 24,180 qualifying), the ONE ZR
23-432 height lookup (C-1), the dwelling-unit estimate with its formula (C-12), and emit a
document that validates against the results-v1 schema.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.scenario.constants import UNUSED_FLOOR_AREA_NOT_AVAILABLE_TEXT
from app.scenario.three_answers import (
    REMAINING_NOT_CONFIRMED_REASON,
    BuildingDefaults,
    ThreeAnswerInputs,
    generate_results,
)
from app.scenario.three_answers.scope import (
    ASSUMPTION_KEYS,
    DisclosedAssumption,
    ScopeInputs,
)

_REPO_ROOT = Path(__file__).resolve().parents[5]
_BENCHMARK = (
    _REPO_ROOT / "packages" / "contracts" / "fixtures" / "valid" / "benchmark_lot"
    / "northern_blvd_215_16_queens_4073340070.json"
)
# The #387 scope fixture (results 1.1.0): the benchmark document's scope must equal its
# scope object, so each disclosed assumption's basis/statement is read from here, never
# restated (the engine derives the lot identity and reads each value from the real inputs).
_SCOPE_FIXTURE = (
    _REPO_ROOT / "packages" / "contracts" / "fixtures" / "valid" / "results"
    / "synthetic_scope_tax_lot_only_northern.json"
)
_ON = {"LANE_A_ENABLED": "1"}
_OFF: dict[str, str] = {}


def _doc_fixture() -> dict:
    return json.loads(_BENCHMARK.read_text("utf-8"))


def _scope_fixture() -> dict:
    return json.loads(_SCOPE_FIXTURE.read_text("utf-8"))["scope"]


def _benchmark_scope_input_kwargs() -> dict:
    """The full ScopeInputs kwargs for 215-16 Northern (BBL 4073340070, Queens block 7334
    lot 70): the bbl plus one DisclosedAssumption per assumed input. The basis and
    statement of each disclosure are read from the scope fixture so they are never restated
    here, and the key set is the authoritative ASSUMPTION_KEYS, never a hand list - add an
    assumed input to the emitter and this helper covers it automatically."""
    assumptions = {a["key"]: a for a in _scope_fixture()["assumptions"]}

    def disclosure(key: str) -> DisclosedAssumption:
        row = assumptions[key]
        return DisclosedAssumption(basis=row["basis"], statement=row["statement"])

    kwargs: dict = {"bbl": "4073340070"}
    kwargs.update({key: disclosure(key) for key in ASSUMPTION_KEYS})
    return kwargs


def _benchmark_scope_inputs() -> ScopeInputs:
    """ScopeInputs for the 215-16 Northern benchmark, with every assumed input disclosed."""
    return ScopeInputs(**_benchmark_scope_input_kwargs())


def _expected(key: str):
    doc = _doc_fixture()
    return next(v["value"] for v in doc["expected_values"] if v["key"] == key)


def _benchmark_inputs(**overrides) -> ThreeAnswerInputs:
    base = dict(
        results_id="res-benchmark-1",
        study_id="study-1",
        option_id="opt-1",
        revision=1,
        computed_at="2026-10-03T00:00:00Z",
        zoning_district=_expected("zoning_district"),
        lot_area_sq_ft=float(_expected("lot_area")),
        lot_type=_expected("lot_type"),
        housing_program="standard_residence",
        overlay_present=True,  # C2-2 commercial overlay
        special_district_present=False,
        within_100_ft_of_street_line_intersection=True,
        street_line_intersection_angle_degrees=90.0,
        special_density_area=False,
        lot_front_ft=float(_expected("lot_dimension_1")),
        lot_depth_ft=float(_expected("lot_dimension_2")),
        depends_on_fact_ids=("pluto:4073340070:lotarea",),
        lot_area_fact_id="pluto:4073340070:lotarea",
        scope_inputs=_benchmark_scope_inputs(),
    )
    base.update(overrides)
    return ThreeAnswerInputs(**base)


def _value(answer: dict, key: str):
    return next(v for v in answer["values"] if v["key"] == key)


def _generate(**overrides):
    return generate_results(_benchmark_inputs(**overrides), env=_ON)


def test_document_validates_and_is_draft() -> None:
    # generate_results validates internally; reaching here means the document is schema-valid.
    result = _generate()
    doc = result.document
    # 1.1.0: the benchmark inputs carry scope_inputs, so the document emits the scope block
    # and declares 1.1.0 (D-090-R108 version binding).
    assert doc["contract_version"] == "1.1.0"
    assert doc["draft"] is True  # every rule is needs_review (D-090-R010)
    assert all(rv["status"] == "needs_review" for rv in doc["rule_versions"])
    assert result.lane_enabled is True


def test_allowance_equals_golden_standard_and_qualifying() -> None:
    # C-2: allowance = 20,150 sq ft (standard) and 24,180 sq ft (qualifying), FAR 2.00 / 2.40.
    allowance = _generate().document["answers"]["floor_area_allowance"]
    assert allowance["status"] == "available"
    assert _value(allowance, "max_residential_far")["value"] == _expected("max_residential_far")
    assert _value(allowance, "max_residential_floor_area")["value"] == _expected(
        "max_residential_floor_area"
    )
    assert _value(
        allowance, "max_residential_far_qualifying_affordable_or_senior"
    )["value"] == _expected("max_residential_far_qualifying_affordable_or_senior")
    assert _value(
        allowance, "max_residential_floor_area_qualifying_affordable_or_senior"
    )["value"] == _expected("max_residential_floor_area_qualifying_affordable_or_senior")
    # Every allowance value cites ZR 23-22.
    assert all("ZR 23-22" in v["zr_sections"] for v in allowance["values"])


def test_envelope_heights_come_from_one_zr_23_432_lookup() -> None:
    # C-1: every height shown anywhere comes from the same ZR 23-432 lookup.
    envelope = _generate().document["answers"]["permitted_envelope"]
    height_keys = {
        "min_base_height": _expected("min_base_height"),
        "max_base_height": _expected("max_base_height"),
        "max_building_height": _expected("max_building_height"),
        "max_base_height_qualifying_affordable_or_senior": _expected(
            "max_base_height_qualifying_affordable_or_senior"
        ),
        "max_building_height_qualifying_affordable_or_senior": _expected(
            "max_building_height_qualifying_affordable_or_senior"
        ),
    }
    for key, expected in height_keys.items():
        value = _value(envelope, key)
        assert value["value"] == expected, key
        assert value["unit"] == "feet"
        assert value["zr_sections"] == ["ZR 23-432"], key  # the ONE lookup


def test_coverage_and_rear_yard_from_corner_tables() -> None:
    doc = _generate().document
    envelope = doc["answers"]["permitted_envelope"]
    assert _value(envelope, "max_lot_coverage")["value"] == _expected("max_lot_coverage")
    # Rear yard waived within 100 ft of the corner: the drawing shows 'not required'.
    rear = doc["geometry"]["yards"]["entries"][0]
    assert rear["kind"] == "rear"
    assert rear["status"] == "not_required"
    assert rear["zr_sections"] == ["ZR 23-344(a)", "ZR 11-25"]


def test_building_option_reconciles_to_plate_times_floors() -> None:
    doc = _generate().document
    option = doc["answers"]["building_option"]
    assert option["status"] == "available"
    plate = _value(option, "floor_plate_area")["value"]
    floors = _value(option, "building_floors")["value"]
    achieved = _value(option, "achieved_zoning_floor_area")["value"]
    # Floor-by-floor table reconciles to the plate x floors and to the achieved total.
    rows = doc["floor_by_floor"]
    assert len(rows) == int(floors)
    assert sum(r["zoning_floor_area_sf"] for r in rows) == achieved
    assert achieved == plate * floors
    # Building height = floors x the stated floor-to-floor default, from ZR 23-432.
    assert _value(option, "building_height")["value"] == floors * 10.0
    # The building option rests on the floor-to-floor assumption -> 'Assumed' label.
    assert option["measurement"] == {"rank": "assumed", "label": "Assumed"}


def test_floor_stack_counts_floors_that_fit_under_the_height_limit() -> None:
    stack = _generate().document["floor_stack"]
    assert stack["status"] == "available"
    assert stack["height_limit_ft"] == _expected("max_building_height")  # 55
    # 5 floors fit under 55 ft at the 10 ft default; each level's allowable area is the plate.
    assert stack["floors_fit"] == 5
    assert len(stack["levels"]) == 5
    assert all(lvl["allowable_area_sf"] == 10075.0 for lvl in stack["levels"])
    assert stack["levels"][-1]["top_of_floor_ft"] == 50.0


def test_building_option_reaches_allowance_no_shortfall() -> None:
    # On this lot the envelope (5 floors x full plate) holds the whole FAR allowance, so the
    # honest answer is no shortfall (the competitor's '705 sq ft can't be captured' is wrong).
    doc = _generate().document
    assert doc["shortfall"] == {"status": "none"}


def test_unit_estimate_in_one_place_with_formula() -> None:
    # C-12: the unit estimate appears once, with its formula.
    estimate = _generate().document["unit_estimate"]
    assert estimate["status"] == "available"
    assert estimate["value"] == _expected("dwelling_units_standard")  # 29
    assert estimate["formula"] == "20,150 ÷ 680 = 29.63"
    assert estimate["factor"] == {"value": 680.0, "unit": "square_feet_per_dwelling_unit"}
    assert estimate["rounding_rule"] == "rounds up only at .75 or more"


def test_floor_to_floor_default_is_a_named_assumption_and_is_editable() -> None:
    result = _generate()
    # Declared, named assumption (never silent).
    ftf = next(a for a in result.assumptions if a.assumption_id == "floor_to_floor_ft")
    assert ftf.value == 10.0 and ftf.unit == "feet"
    # Editable: a different default changes the floor stack (fewer floors fit under 55 ft).
    taller = _generate(building_defaults=BuildingDefaults(floor_to_floor_ft=12.0))
    stack = taller.document["floor_stack"]
    assert stack["floors_fit"] == 4  # floor(55 / 12)
    assert all(lvl["floor_to_floor_ft"] == 12.0 for lvl in stack["levels"])


def test_remaining_capacity_is_never_a_number() -> None:
    # D-090-R038 owner wording: the slot never states a number.
    doc = _generate().document
    remaining = doc["remaining_floor_area"]
    assert remaining == {
        "status": "not_available",
        "reason": REMAINING_NOT_CONFIRMED_REASON,
        "reason_kind": "missing_input",
    }
    # Nothing claims the zoning lot is verified.
    assert doc["lot_selection_statement"] == (
        "Based on the lots you selected — the app does not verify the zoning lot"
    )
    # D-090-R108 puts the settled 'Remaining development capacity: Not confirmed' label in the
    # scope block, beside the numbers. The honest invariant stands: wherever that phrase
    # appears it is the settled not-confirmed label (no number), and nowhere else.
    rc = doc["scope"]["remaining_capacity"]
    assert rc["status"] == "not_confirmed"
    assert rc["label"] == UNUSED_FLOOR_AREA_NOT_AVAILABLE_TEXT  # byte-exact, no number
    assert json.dumps(doc).count("Remaining development capacity") == 1


def test_flag_off_gates_everything() -> None:
    result = generate_results(_benchmark_inputs(), env=_OFF)
    doc = result.document
    assert result.lane_enabled is False
    for name in ("floor_area_allowance", "permitted_envelope", "building_option"):
        assert doc["answers"][name]["status"] == "not_available"
    assert doc["geometry"]["status"] == "not_available"
    assert doc["unit_estimate"]["status"] == "not_available"
    assert doc["draft"] is True
    # Still a valid results-v1 document (generate_results validated it). The scope block is
    # gated on scope_inputs, not the lane flag, so the gated-off document still carries it and
    # declares 1.1.0 (D-090-R108).
    assert doc["contract_version"] == "1.1.0"
    assert doc["scope"]["label"] == "Tax-lot-only estimate"
