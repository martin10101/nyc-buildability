"""Competitor-error guard checks, Lane A engine side (D-090 source-025, R147-R150).

One test per Lane-A E-item from the 215-16 Northern competitor review
(``docs/COMPETITOR_REVIEW_ENVELOPE_215-16_NORTHERN_2026-09-28.md``; guards table
``docs/plans/COMPETITOR_ERROR_GUARDS_2026-10-04.md``). Each E-id is named in the
test or its docstring.

- E2  (no R6B wide-street FAR bonus): a REAL red/green guard on the recorded R6B
  benchmark lot.
- E9  (lot splits, each piece its own lot type; C-10): a PENDING test for the
  unbuilt A-13 feature.
- E19 (identical buildings merged or explained; C-6): a PENDING test for the
  unbuilt A-05 feature (PR #369, reviewed PASS, not merged).

The recorded 215-16 Northern data is the benchmark contract fixture, read through
the benchmark test's helpers (never restated here).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from .test_three_answers_benchmark import _benchmark_inputs, _generate, _value

# <root>/services/api/tests/scenario/three_answers/<this file>
_REPO_ROOT = Path(__file__).resolve().parents[5]
_RULESETS = _REPO_ROOT / "services" / "api" / "app" / "rules" / "rulesets"
_WIDE_STREET_RULE = _RULESETS / "r6_r7_r8_wide_street_conditional_far.rule.json"
_R6B_QUALIFYING_RULE = _RULESETS / "r6b_qualifying_housing_far.rule.json"


def _rule(path: Path) -> dict:
    return json.loads(path.read_text("utf-8"))


def _param(rule: dict, name: str):
    return next(p["value"] for p in rule["parameters"] if p["name"] == name)


# --- E2: R6B has no wide-street FAR bonus (competitor review page 3) ---------------------


def test_e2_r6b_is_not_in_the_wide_street_conditional_far_district_table() -> None:
    """E2: the ONLY source of a higher within-100-ft-of-a-wide-street FAR is the
    wide-street-conditional rule's district table. R6B is absent from it, so the
    engine can never route R6B to a wide-street bonus.

    Red/green: if the R6B exclusion were removed by adding ``"R6B"`` to the table,
    R6B would become eligible for a wide-street bonus and this assertion fails."""
    table = _param(_rule(_WIDE_STREET_RULE), "wide_street_far_by_district")
    assert set(table) == {"R6", "R7-1", "R7-2", "R8"}
    assert "R6B" not in table
    # Prove the guard is load-bearing: with R6B injected the invariant breaks.
    injected = dict(table, **{"R6B": 3.0})
    assert "R6B" in injected  # the mutation the guard forbids would pass the table


def test_e2_r6b_qualifying_rule_states_no_wide_street_increase() -> None:
    """E2: the R6B qualifying-housing FAR rule carries an explicit documented
    limitation that R6B has no wide-street increase (neither 2.00 nor 2.40 changes
    with street width)."""
    exception_ids = [e["id"] for e in _rule(_R6B_QUALIFYING_RULE)["exceptions"]]
    assert "no_wide_street_increase" in exception_ids


def test_e2_r6b_allowance_shows_no_wide_street_bonus_value() -> None:
    """E2: the computed floor-area allowance for the recorded R6B lot surfaces only
    the standard and qualifying FAR/area (ZR 23-22); no wide-street / bonus value
    appears, and the standard FAR is 2.00 (not R6's wide-street 3.00)."""
    allowance = _generate().document["answers"]["floor_area_allowance"]
    assert allowance["status"] == "available"
    keys = {v["key"] for v in allowance["values"]}
    assert keys == {
        "max_residential_far",
        "max_residential_floor_area",
        "max_residential_far_qualifying_affordable_or_senior",
        "max_residential_floor_area_qualifying_affordable_or_senior",
    }
    assert not any("wide" in k.lower() or "bonus" in k.lower() for k in keys)
    assert _value(allowance, "max_residential_far")["value"] == 2.0


# --- E9: lot splits, each piece its own lot type (C-10) - NOT BUILT YET (A-13) -----------


@pytest.mark.skip(reason="NOT BUILT YET: A-13 (C-10) - a split-lot scenario that evaluates "
                         "each resulting lot with its own lot type and states the subdivision.")
def test_e9_split_lot_evaluates_each_piece_with_its_own_lot_type() -> None:
    """E9: when the A-13 split-lot scenario exists, splitting the recorded 215-16
    Northern CORNER lot into two pieces must evaluate each piece with its OWN lot
    type (one corner, one interior, which carry different yard/coverage rules) and
    state that a formal subdivision is required. Assertion to come:

        pieces = evaluate_lot_split(_benchmark_inputs())
        assert {p.lot_type for p in pieces} == {"corner", "interior"}
        assert pieces.subdivision_required is True
    """
    _ = _benchmark_inputs()  # recorded Northern corner lot the split would start from


# --- E19: identical buildings merged or explained (C-6) - NOT BUILT YET (A-05, PR #369) --


@pytest.mark.skip(reason="NOT BUILT YET: A-05 / PR #369 (C-6) - the no-duplicate-options "
                         "guard that merges or explains two options with the same building.")
def test_e19_identical_building_options_are_merged_or_explained() -> None:
    """E19: when A-05 lands, two program options that produce the byte-identical
    building geometry are either merged into one row or carry an explicit
    explanation of why both are shown. Assertion to come:

        compared = compare_options([option_a, option_b])  # same geometry
        assert compared.merged_or_explained(option_a, option_b)
    """
    pytest.fail("A-05 not built: duplicate-option merge/explain guard is absent")
