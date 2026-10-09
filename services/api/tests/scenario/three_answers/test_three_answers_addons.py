"""A-06 tests for the add-on model on the 215-16 Northern Blvd benchmark (BBL 4073340070),
plan section 6 / section 5 'Best combination' / M1-25; directive D-090:D-090-R001.

Expected values are loaded from the benchmark contract fixture, never restated (the pattern of
``test_three_answers_benchmark.py``). The slice proves: automatic add-ons on / optional off by
default; the qualifying-housing switch moves the allowance to the rule's qualifying value;
gains equal the difference between two recalculated outcomes; 'Best combination' for the goal
picks the qualifying option and explains every exclusion; the completeness line flips with
coverage; a removed rule degrades to not_available; and the document validates against the
results contract (generate_results validates internally).
"""

from __future__ import annotations

import json
from pathlib import Path

from app.rules.registry import RuleRegistry
from app.scenario.addons import (
    AddOn,
    SelectionOutcome,
    base_values,
    best_combination,
    build_catalogue,
    completeness_line,
    conflicts,
    is_available,
    optional_group_a_b,
    outcome_for_selection,
)
from app.scenario.addons.recalculation import addon_gain_entry
from app.scenario.three_answers import ThreeAnswerInputs, generate_results
from app.scenario.three_answers.inputs import AddonGoal

_REPO_ROOT = Path(__file__).resolve().parents[5]
_BENCHMARK = (
    _REPO_ROOT / "packages" / "contracts" / "fixtures" / "valid" / "benchmark_lot"
    / "northern_blvd_215_16_queens_4073340070.json"
)
_ON = {"LANE_A_ENABLED": "1"}


def _doc_fixture() -> dict:
    return json.loads(_BENCHMARK.read_text("utf-8"))


def _expected(key: str):
    doc = _doc_fixture()
    return next(v["value"] for v in doc["expected_values"] if v["key"] == key)


def _benchmark_inputs(**overrides) -> ThreeAnswerInputs:
    base = dict(
        results_id="res-addon-1",
        study_id="study-1",
        option_id="opt-1",
        revision=1,
        computed_at="2026-10-03T00:00:00Z",
        zoning_district=_expected("zoning_district"),
        lot_area_sq_ft=float(_expected("lot_area")),
        lot_type=_expected("lot_type"),
        housing_program="standard_residence",
        overlay_present=True,
        special_district_present=False,
        within_100_ft_of_street_line_intersection=True,
        street_line_intersection_angle_degrees=90.0,
        special_density_area=False,
        lot_front_ft=float(_expected("lot_dimension_1")),
        lot_depth_ft=float(_expected("lot_dimension_2")),
        depends_on_fact_ids=("pluto:4073340070:lotarea",),
        lot_area_fact_id="pluto:4073340070:lotarea",
    )
    base.update(overrides)
    return ThreeAnswerInputs(**base)


def _registry() -> RuleRegistry:
    return RuleRegistry(env=_ON).load()


def _gain(doc: dict, addon_id: str) -> dict:
    return next(g for g in doc["addon_gains"] if g["addon_id"] == addon_id)


def _catalogue_entry(addon_id: str) -> AddOn:
    return next(a for a in build_catalogue() if a.addon_id == addon_id)


# --- Automatic on / optional off by default -------------------------------------------------


def test_automatic_add_ons_are_on_and_optional_switches_start_off() -> None:
    doc = generate_results(_benchmark_inputs(), env=_ON).document
    # Optional switches all start off (no add-on is selected by default).
    assert doc["addon_gains"], "optional add-ons should be listed as gains"
    assert all(g["on"] is False for g in doc["addon_gains"])
    assert all(g["relative_to"] == "current_selection" for g in doc["addon_gains"])
    # Automatic add-ons are applied by the rules and are NOT optional switches.
    catalogue = build_catalogue()
    automatic = [a for a in catalogue if a.automatic]
    assert any(a.addon_id == "corner_lot_coverage" for a in automatic)
    gain_ids = {g["addon_id"] for g in doc["addon_gains"]}
    assert not any(a.addon_id in gain_ids for a in automatic)  # automatics aren't gain switches


# --- The qualifying-housing switch moves the allowance to the rule's qualifying value -------


def test_qualifying_switch_moves_allowance_to_rule_qualifying_value() -> None:
    inputs = _benchmark_inputs()
    reg = _registry()
    base = base_values(inputs, reg)
    affordable = _catalogue_entry("qualifying_affordable_housing")

    baseline = outcome_for_selection(inputs, base, ())
    qualifying = outcome_for_selection(inputs, base, (affordable,))
    assert baseline is not None and qualifying is not None
    # Baseline reaches the standard allowance; the switch reaches the qualifying allowance -
    # both read from the accepted ZR 23-22 rule (golden fixture values, never restated here).
    assert baseline.residential_floor_area_sf == float(_expected("max_residential_floor_area"))
    assert qualifying.residential_floor_area_sf == float(
        _expected("max_residential_floor_area_qualifying_affordable_or_senior")
    )
    # The switch also lifts the height cap used (ZR 23-432), so one more floor fits.
    assert qualifying.floors == baseline.floors + 1


# --- Gains equal the difference between the two recalculated outcomes ------------------------


def test_gain_equals_difference_between_two_recalculated_outcomes() -> None:
    inputs = _benchmark_inputs()
    reg = _registry()
    base = base_values(inputs, reg)
    affordable = _catalogue_entry("qualifying_affordable_housing")

    baseline = outcome_for_selection(inputs, base, ())
    qualifying = outcome_for_selection(inputs, base, (affordable,))
    assert baseline is not None and qualifying is not None

    doc = generate_results(inputs, env=_ON).document
    gain = _gain(doc, "qualifying_affordable_housing")["gain"]
    assert gain["status"] == "available"
    assert gain["floor_area_sf"] == (
        qualifying.residential_floor_area_sf - baseline.residential_floor_area_sf
    )
    assert gain["height_ft"] == qualifying.building_height_ft - baseline.building_height_ft
    assert gain["floors"] == qualifying.floors - baseline.floors
    # And the gain equals the independently-sourced allowance delta (qualifying - standard).
    assert gain["floor_area_sf"] == float(
        _expected("max_residential_floor_area_qualifying_affordable_or_senior")
    ) - float(_expected("max_residential_floor_area"))


def test_zero_gain_is_reported_as_zero_never_hidden() -> None:
    # An available add-on that changes nothing about the outcome still reports its zero gain -
    # it is present as 0, never dropped. Proven with a flat synthetic outcome (same result for
    # any selection) and a real, available add-on.
    inputs = _benchmark_inputs()
    reg = _registry()
    base = base_values(inputs, reg)
    affordable = _catalogue_entry("qualifying_affordable_housing")
    flat = _flat_outcome(1000.0)
    entry = addon_gain_entry(
        inputs, base, affordable, frozenset(reg.rule_ids()), (), outcome_fn=flat
    )
    assert entry["gain"]["status"] == "available"
    assert entry["gain"] == {
        "status": "available",
        "floor_area_sf": 0.0,  # zero, explicitly present - never hidden
        "height_ft": 0.0,
        "floors": 0,
    }


def test_not_implemented_add_on_reports_not_available() -> None:
    doc = generate_results(_benchmark_inputs(), env=_ON).document
    gain = _gain(doc, "community_facility_floor_area")["gain"]
    assert gain["status"] == "not_available"
    assert gain["reason_kind"] == "rule_not_implemented"


# --- Best combination picks the qualifying option and explains every exclusion --------------


def test_best_combination_picks_qualifying_with_computed_exclusions() -> None:
    doc = generate_results(_benchmark_inputs(), env=_ON).document
    best = doc["best_combination"]
    assert best["status"] == "available"
    assert best["goal"]["kind"] == "most_residential_floor_area"  # the default goal
    # The qualifying option reaches the qualifying allowance (golden fixture value).
    assert best["goal_value_sf"] == float(
        _expected("max_residential_floor_area_qualifying_affordable_or_senior")
    )
    # Deterministic tie-break: affordable (id-first) over senior; senior excluded by conflict.
    assert best["selected_addon_ids"] == ["qualifying_affordable_housing"]
    senior_reason = next(
        e["reason"] for e in best["excluded"] if e["addon_id"] == "qualifying_senior_housing"
    )
    assert "housing_program" in senior_reason  # the exclusion is computed from the shared input
    # Every left-out optional A/B add-on is explained.
    excluded_ids = {e["addon_id"] for e in best["excluded"]}
    cat_ab = {a.addon_id for a in optional_group_a_b(build_catalogue())}
    assert excluded_ids == cat_ab - {"qualifying_affordable_housing"}


def test_goal_is_editable_and_saved_with_the_option() -> None:
    inputs = _benchmark_inputs(addon_goal=AddonGoal(kind="most_total_floor_area"))
    result = generate_results(inputs, env=_ON)
    best = result.document["best_combination"]
    assert best["goal"] == {"kind": "most_total_floor_area", "text": None}
    # The floor-to-floor assumption is also saved and surfaced beside the results.
    assert any(a.assumption_id == "floor_to_floor_ft" for a in result.assumptions)


# --- Completeness line flips with coverage --------------------------------------------------


def test_completeness_line_flips_with_coverage() -> None:
    # The real R6B catalogue: only the two qualifying add-ons are covered, so the line reads
    # "Not yet covered: ..." and names the uncovered switches.
    real = completeness_line(build_catalogue(), frozenset(_registry().rule_ids()))
    assert real["text"].startswith("Not yet covered:")
    assert real["not_yet_covered"]

    # A small synthetic catalogue of two optional Group A add-ons, both backed by a rule that
    # IS in the registry view -> full coverage -> "all 2". Drop that rule -> the line flips.
    synthetic = (
        _synthetic_addon("addon_one", "key_1", "on"),
        _synthetic_addon("addon_two", "key_2", "on"),
    )
    all_covered = completeness_line(synthetic, frozenset({"synthetic-rule"}))
    assert all_covered["not_yet_covered"] == []
    assert all_covered["text"] == "Add-ons checked for this district: all 2."

    none_covered = completeness_line(synthetic, frozenset())
    assert none_covered["not_yet_covered"] == ["addon_one", "addon_two"]
    assert none_covered["text"].startswith("Not yet covered:")


# --- Mutation tests: flip an exclusion -> the best set changes; remove a rule -> not_available


def _flat_outcome(value_sf: float):
    """An outcome identical for every selection - so any add-on's gain is exactly zero."""

    def fn(inputs, base, selection) -> SelectionOutcome:
        return SelectionOutcome(
            residential_floor_area_sf=value_sf,
            total_floor_area_sf=value_sf,
            building_height_ft=20.0,
            floors=2,
            program="standard_residence",
        )

    return fn


def _synthetic_outcome(base_sf: float, per_addon_sf: float):
    """A synthetic, additive outcome: each selected add-on adds ``per_addon_sf`` floor area,
    so two non-conflicting add-ons are strictly better together than either alone."""

    def fn(inputs, base, selection) -> SelectionOutcome:
        total = base_sf + per_addon_sf * len(list(selection))
        return SelectionOutcome(
            residential_floor_area_sf=total,
            total_floor_area_sf=total,
            building_height_ft=10.0 * (1 + len(list(selection))),
            floors=1 + len(list(selection)),
            program="standard_residence",
        )

    return fn


def _synthetic_addon(addon_id: str, key: str, value: str) -> AddOn:
    return AddOn(
        addon_id=addon_id,
        group="A",
        label=addon_id,
        automatic=False,
        rule_ids=("synthetic-rule",),
        input_changes=((key, value),),
        requires=(),
    )


def test_flipping_an_exclusion_changes_the_best_set() -> None:
    inputs = _benchmark_inputs()
    reg = _registry()
    base = base_values(inputs, reg)
    goal = AddonGoal()
    rule_ids = frozenset({"synthetic-rule"})
    outcome_fn = _synthetic_outcome(base_sf=1000.0, per_addon_sf=100.0)

    # No exclusion (different input keys): both add-ons combine -> best set is BOTH.
    x = _synthetic_addon("addon_x", "key_x", "on")
    y_free = _synthetic_addon("addon_y", "key_y", "on")
    free = best_combination(inputs, base, (x, y_free), rule_ids, goal, outcome_fn)
    assert free["selected_addon_ids"] == ["addon_x", "addon_y"]
    assert free["goal_value_sf"] == 1200.0

    # Flip an exclusion on (same input key, different values): they now conflict, so the best
    # set DROPS to one add-on, and the loser is excluded with the computed conflict reason.
    y_conflict = _synthetic_addon("addon_y", "key_x", "other")
    assert conflicts(x, y_conflict)
    excluded = best_combination(inputs, base, (x, y_conflict), rule_ids, goal, outcome_fn)
    assert excluded["selected_addon_ids"] == ["addon_x"]  # tie-break: id-first
    assert excluded["goal_value_sf"] == 1100.0
    reason = next(
        e["reason"] for e in excluded["excluded"] if e["addon_id"] == "addon_y"
    )
    assert "key_x" in reason and "Conflicts with" in reason


def test_removing_a_rule_degrades_the_gain_to_not_available() -> None:
    inputs = _benchmark_inputs()
    reg = _registry()
    base = base_values(inputs, reg)
    affordable = _catalogue_entry("qualifying_affordable_housing")
    # With the add-on's rules present, it is available.
    assert is_available(affordable, frozenset(reg.rule_ids()))
    # Remove the rules from the registry view -> the gain is not_available (rule_not_implemented),
    # never a guessed number.
    entry = addon_gain_entry(inputs, base, affordable, frozenset(), ())
    assert entry["gain"]["status"] == "not_available"
    assert entry["gain"]["reason_kind"] == "rule_not_implemented"


# --- Existing three-answer behavior is unchanged where the add-on slots are not involved -----


def test_document_still_validates_and_three_answers_unchanged() -> None:
    # generate_results validates the whole document against the results contract internally.
    doc = generate_results(_benchmark_inputs(), env=_ON).document
    assert doc["answers"]["floor_area_allowance"]["status"] == "available"
    assert doc["answers"]["permitted_envelope"]["status"] == "available"
    assert doc["answers"]["building_option"]["status"] == "available"
    assert doc["with_approvals_label"] is None  # no approval add-on is on
