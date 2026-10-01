"""A-02b (D-090): the additive ``round_threshold`` DSL op.

``round_threshold(value, threshold)`` keeps the whole number of ``value`` and adds one only when the
fractional part is AT LEAST ``threshold`` (ZR 23-52(b): "Fractions equal to or greater than
three-quarters ... shall be considered to be one dwelling unit"). It is decided on the exact
rational, fails closed outside its domain, and leaves the existing ``round`` op (half away from
zero) unchanged.
"""

from __future__ import annotations

import json
from fractions import Fraction

import pytest

from app.rules import dsl
from app.rules.evaluator import EvaluationError, evaluate
from app.rules.operations import COMPUTE_OPS, OperationError
from app.rules.snapshots import SnapshotStore

_op = COMPUTE_OPS["round_threshold"]
_round = COMPUTE_OPS["round"]
_THREE_QUARTERS = Fraction(3, 4)


# --------------------------------------------------------------------------
# Boundaries at .75 (exact).
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Fraction(2015, 68), 29),          # 20,150 / 680 = 29.632... -> 29 (the benchmark)
        (Fraction(119, 4), 30),            # 29.75 exactly -> 30 (equal counts)
        (Fraction(20229, 680), 29),        # 29.7485... -> 29
        (Fraction(20230, 680), 30),        # 29.75 as a floor-area quotient -> 30
        (Fraction(2974999, 100000), 29),   # 29.74999 -> 29
        (Fraction(2975001, 100000), 30),   # 29.75001 -> 30
        (29, 29),                          # a whole number stays
        (Fraction(2999, 100), 30),         # 29.99 -> 30
        (0, 0),
        (Fraction(3, 4), 1),               # 0.75 -> 1
        (Fraction(74, 100), 0),            # 0.74 -> 0
    ],
)
def test_threshold_three_quarters_boundaries(value, expected) -> None:
    result = _op([value, _THREE_QUARTERS])
    assert isinstance(result, Fraction)
    assert result == expected


@pytest.mark.parametrize(("value", "expected"), [(29.75, 30), (29.63, 29), ("29.75", 30),
                                                 ("29.7499", 29), (29, 29)])
def test_json_and_string_numbers_are_read_exactly(value, expected) -> None:
    # 29.75 and 0.75 enter through the canonical-decimal boundary, never as binary floats.
    assert _op([value, 0.75]) == expected


def test_boundary_is_exact_where_float_arithmetic_is_not() -> None:
    # 0.06 + 0.57 + 0.12 is 0.7499999999999999 in binary floats (a float rule would drop the
    # fraction); exactly it is 0.75, which counts as one.
    assert 0.06 + 0.57 + 0.12 < 0.75
    value = COMPUTE_OPS["add"]([0.06, 0.57, 0.12])
    assert value == _THREE_QUARTERS
    assert _op([value, 0.75]) == 1


@pytest.mark.parametrize(
    ("threshold", "value", "expected"),
    [(1, Fraction(2999, 100), 29),        # threshold 1: every fraction is dropped
     (Fraction(1, 2), Fraction(5, 2), 3),  # threshold 0.5: 2.5 -> 3
     (Fraction(1, 2), Fraction(249, 100), 2)],
)
def test_other_thresholds(threshold, value, expected) -> None:
    assert _op([value, threshold]) == expected


# --------------------------------------------------------------------------
# Fail-closed domain.
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "args",
    [
        [-1, 0.75],               # a count is never negative: no sign convention invented
        [Fraction(-1, 4), 0.75],
        [29.5, 0],                # threshold 0 would count a whole number as one more
        [29.5, -0.25],
        [29.5, 1.5],
        [29.5],                   # arity
        [29.5, 0.75, 1],
        [None, 0.75],             # non-numeric
        [True, 0.75],
        ["abc", 0.75],
        [float("nan"), 0.75],
        [float("inf"), 0.75],
    ],
)
def test_out_of_domain_fails_closed(args) -> None:
    with pytest.raises(OperationError):
        _op(args)


# --------------------------------------------------------------------------
# Existing rounding is unchanged.
# --------------------------------------------------------------------------

def test_round_keeps_half_away_from_zero() -> None:
    assert _round([2.5, 0]) == 3
    assert _round([-2.5, 0]) == -3
    assert _round([2.675, 2]) == Fraction(268, 100)
    # The same quotient rounds differently under the two ops, by design.
    assert _round([Fraction(2015, 68), 0]) == 30
    assert _op([Fraction(2015, 68), 0.75]) == 29


def test_op_vocabulary_is_additive_and_matches_the_schema() -> None:
    assert set(COMPUTE_OPS) == {"identity", "add", "subtract", "multiply", "divide", "min",
                                "max", "round", "round_threshold", "clamp"}
    schema = json.loads(dsl.RULE_DEFINITION_SCHEMA_PATH.read_text("utf-8"))
    step_ops = schema["properties"]["computation"]["properties"]["steps"]["items"][
        "properties"]["op"]["enum"]
    assert set(step_ops) == set(COMPUTE_OPS)


# --------------------------------------------------------------------------
# Through the evaluator (a synthetic draft rule; no production rule involved).
# --------------------------------------------------------------------------

def _syn_rule(steps: list[dict], outputs: dict) -> dict:
    return {
        "rule_id": "syn-round-threshold",
        "rule_version": "0.0.1-draft",
        "family": "syn_family",
        "title": "synthetic",
        "jurisdiction": "nyc",
        "status": "needs_review",
        "description": "synthetic rule exercising round_threshold",
        "citations": [{"snapshot_id": "zr-23-52", "section": "23-52", "quote": "680"}],
        "inputs": [
            {"name": "zoning_district", "type": "string", "required": True},
            {"name": "value", "type": "number", "required": True},
        ],
        "outputs": [{"name": name, "type": "number"} for name in outputs],
        "parameters": [],
        "applicability": {"op": "in_set", "input": "zoning_district", "values": ["DEMO"]},
        "computation": {"steps": steps, "outputs": outputs},
    }


def _eval(doc: dict, inputs: dict):
    store = SnapshotStore().load()
    return evaluate(dsl.build_rule_definition(doc, store), inputs, store)


@pytest.mark.parametrize(("value", "expected"), [(20150, 29.0), (20230, 30.0), (20229, 29.0)])
def test_evaluator_runs_divide_then_round_threshold(value, expected) -> None:
    doc = _syn_rule(
        steps=[
            {"id": "q", "op": "divide", "args": [{"input": "value"}, {"const": 680}]},
            {"id": "n", "op": "round_threshold", "args": [{"step": "q"}, {"const": 0.75}]},
        ],
        outputs={"n": {"step": "n"}},
    )
    trace = _eval(doc, {"zoning_district": "DEMO", "value": value}).export()
    assert trace["outputs"]["n"] == expected
    assert [s["op"] for s in trace["computation_steps"]] == ["divide", "round_threshold"]


def test_evaluator_fails_closed_on_a_negative_value() -> None:
    doc = _syn_rule(
        steps=[{"id": "n", "op": "round_threshold", "args": [{"input": "value"},
                                                             {"const": 0.75}]}],
        outputs={"n": {"step": "n"}},
    )
    with pytest.raises(EvaluationError, match="round_threshold"):
        _eval(doc, {"zoning_district": "DEMO", "value": -3})


def test_schema_rejects_an_unknown_op() -> None:
    doc = _syn_rule(
        steps=[{"id": "n", "op": "round_up_somehow", "args": [{"input": "value"}]}],
        outputs={"n": {"step": "n"}},
    )
    with pytest.raises(dsl.DSLError):
        dsl.build_rule_definition(doc, SnapshotStore().load())
