"""M4-T007 exact-legal-arithmetic acceptance pack (DF-2 / blocker B-014).

Proves the rule-evaluation core computes and COMPARES legal thresholds in exact
rational arithmetic built from canonical decimal strings - not binary float - and
that geometry floats stay isolated behind an explicit typed conversion. Maps to
the packet's acceptance scenarios:

* AS-1 - no binary-float arithmetic remains on the legal value path.
* AS-2 - adversarial exact-threshold suite: equalities a naive float engine gets
  WRONG resolve deterministically here.
* AS-3 - differential (native evaluator vs an independent exact recompute) +
  property-based invariants over generated inputs.
* AS-4 - per-rule rounding mode/scale/order + unit enforcement are explicit and
  covered; malformed/non-finite/unknown-unit inputs fail closed.

Everything is offline, deterministic, stdlib-only. Synthetic rule fixtures reuse
the M4-T003 demo snapshot; they are illustrative and never a legal statement.
"""

from __future__ import annotations

import ast
import json
import random
from fractions import Fraction
from pathlib import Path

import pytest

from app.rules import RuleRegistry, units
from app.rules import coverage as cov
from app.rules.dsl import build_rule_definition
from app.rules.evaluator import EvaluationError, evaluate
from app.rules.operations import COMPUTE_OPS
from app.rules.snapshots import SnapshotStore

_ENGINE_DIR = Path(__file__).resolve().parents[2] / "app" / "rules"
_R5_PATH = _ENGINE_DIR / "rulesets" / "r5_residential_far.rule.json"
_M4T003 = Path(__file__).resolve().parent / "fixtures" / "m4t003"
_R5 = "r5-residential-far"
_PRR = cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED

_DEMO_CITE = {
    "snapshot_id": "zr-demo-m4t003",
    "section": "00-00-DEMO",
    "quote": "SYNTHETIC exact-arithmetic fixture; illustrative, never a legal statement.",
    "last_amended": None,
}


def _snaps() -> SnapshotStore:
    return SnapshotStore(_M4T003 / "snapshots").load()


def _build(doc: dict):
    return build_rule_definition(doc, _snaps())


def _eval(doc: dict, inputs: dict):
    return evaluate(_build(doc), inputs, _snaps())


def _syn_doc(
    *, steps: list, outputs: dict, out_specs: list, determination: dict | None = None,
    inputs: list | None = None, parameters: list | None = None,
) -> dict:
    """Assemble a schema-valid SYNTHETIC single-family rule doc for exact-math tests."""
    doc = {
        "rule_id": "syn-exact",
        "rule_version": "0.0.1-draft",
        "family": "syn_exact",
        "title": "SYNTHETIC exact-arithmetic fixture",
        "jurisdiction": "nyc",
        "status": "extracted_draft",
        "description": "SYNTHETIC M4-T007 exact-arithmetic fixture; illustrative, never legal.",
        "citations": [_DEMO_CITE],
        "inputs": inputs
        if inputs is not None
        else [{"name": "zoning_district", "type": "string", "required": True}],
        "outputs": out_specs,
        "parameters": parameters or [],
        "applicability": {"op": "in_set", "input": "zoning_district", "values": ["DEMO"]},
        "computation": {"steps": steps, "outputs": outputs},
    }
    if determination is not None:
        doc["determination"] = determination
    return doc


@pytest.fixture
def registry() -> RuleRegistry:
    return RuleRegistry().load()


# ==========================================================================
# AS-1 - no binary-float arithmetic on the legal value path.
# ==========================================================================

_OP_SAMPLE_ARGS = {
    "identity": [1.5],
    "add": [0.1, 0.2],
    "subtract": [0.3, 0.1],
    "multiply": [2, 3],
    "divide": [1, 3],
    "min": [3, 1, 2],
    "max": [3, 1, 2],
    "round": [2.5, 0],
    "clamp": [5, 0, 3],
}


def test_as1_every_compute_op_returns_an_exact_fraction():
    # A float on the value path would surface here as a non-Fraction result.
    assert set(COMPUTE_OPS) == set(_OP_SAMPLE_ARGS)
    for op, args in _OP_SAMPLE_ARGS.items():
        result = COMPUTE_OPS[op](args)
        assert isinstance(result, Fraction), f"op {op!r} returned {type(result).__name__}"


def test_as1_operations_module_has_no_float_calls_on_value_path():
    # operations.py is the pure value-path module: it must contain NO float()
    # coercion and NO legacy determinism-rounding hooks.
    source = (_ENGINE_DIR / "operations.py").read_text(encoding="utf-8")
    assert "float(" not in source
    assert "_QUANT" not in source and "def _q(" not in source
    # and it must route numbers through the exact-arithmetic foundation.
    assert "from . import units" in source


def test_as1_evaluator_determination_and_computation_use_exact_not_float():
    # The two legacy float comparison/round patterns are gone from the evaluator.
    source = (_ENGINE_DIR / "evaluator.py").read_text(encoding="utf-8")
    assert "float(left)" not in source and "float(right)" not in source
    assert "round(value, _QUANT)" not in source
    # _run_computation must hand back EXACT rational outputs for the determination.
    tree = ast.parse(source)
    run_comp = next(
        node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_run_computation"
    )
    assert "outputs_exact" in ast.unparse(run_comp)


def test_as1_run_computation_keeps_outputs_exact():
    from app.rules.evaluator import _run_computation

    rule = _build(_syn_doc(
        steps=[{"id": "s", "op": "multiply", "args": [{"const": 0.1}, {"const": 3}]}],
        outputs={"v": {"step": "s"}},
        out_specs=[{"name": "v", "type": "number"}],
    ))
    _traces, outputs_json, outputs_exact, nonrep = _run_computation(
        rule, {"zoning_district": "DEMO"}
    )
    assert nonrep == []
    assert outputs_exact["v"] == Fraction(3, 10)          # exact, not 0.30000000000000004
    assert isinstance(outputs_exact["v"], Fraction)
    assert outputs_json["v"] == 0.3


# ==========================================================================
# AS-2 - adversarial exact-threshold suite (float would be wrong here).
# ==========================================================================

def test_as2_addition_equality_at_float_trap_resolves_exactly():
    # 0.1 + 0.2 == 0.3 is FALSE in IEEE-754; the exact engine says pass.
    assert (0.1 + 0.2) != 0.3  # the trap, in plain float
    doc = _syn_doc(
        steps=[{"id": "total", "op": "add", "args": [{"const": 0.1}, {"const": 0.2}]}],
        outputs={"total": {"step": "total"}},
        out_specs=[{"name": "total", "type": "number"}],
        determination={
            "id": "eq_check", "left": {"output": "total"}, "compare": "eq",
            "right": {"const": 0.3}, "pass_label": "exact", "fail_label": "off",
        },
    )
    res = _eval(doc, {"zoning_district": "DEMO"})
    assert res.trace.determination["outcome"] == "pass"
    assert res.outputs["total"] == 0.3


def test_as2_le_boundary_a_naive_float_engine_would_flip():
    # left = 0.1 + 0.2 (exactly 0.3), right = 0.3 (a limit): proposal is within.
    assert (0.1 + 0.2) > 0.3  # a naive float engine would (wrongly) report "exceeds"
    doc = _syn_doc(
        steps=[
            {"id": "computed", "op": "add", "args": [{"const": 0.1}, {"const": 0.2}]},
            {"id": "limit", "op": "identity", "args": [{"const": 0.3}]},
        ],
        outputs={"computed": {"step": "computed"}, "limit": {"step": "limit"}},
        out_specs=[{"name": "computed", "type": "number"}, {"name": "limit", "type": "number"}],
        determination={
            "id": "le_check", "left": {"output": "computed"}, "compare": "le",
            "right": {"output": "limit"}, "pass_label": "within", "fail_label": "exceeds",
        },
    )
    res = _eval(doc, {"zoning_district": "DEMO"})
    assert res.trace.determination["outcome"] == "pass"


def test_as2_division_equality_at_float_trap_resolves_exactly():
    # 0.3 / 0.1 == 3 is FALSE in IEEE-754 (it is 2.9999999999999996).
    assert (0.3 / 0.1) != 3
    doc = _syn_doc(
        steps=[{"id": "q", "op": "divide", "args": [{"const": 0.3}, {"const": 0.1}]}],
        outputs={"q": {"step": "q"}},
        out_specs=[{"name": "q", "type": "number"}],
        determination={
            "id": "eq3", "left": {"output": "q"}, "compare": "eq",
            "right": {"const": 3}, "pass_label": "exact", "fail_label": "off",
        },
    )
    res = _eval(doc, {"zoning_district": "DEMO"})
    assert res.outputs["q"] == 3.0
    assert res.trace.determination["outcome"] == "pass"


def test_as2_subtraction_is_exact():
    # 0.3 - 0.1 == 0.2 is FALSE in IEEE-754 (0.19999999999999998).
    assert (0.3 - 0.1) != 0.2
    doc = _syn_doc(
        steps=[{"id": "d", "op": "subtract", "args": [{"const": 0.3}, {"const": 0.1}]}],
        outputs={"d": {"step": "d"}},
        out_specs=[{"name": "d", "type": "number"}],
    )
    res = _eval(doc, {"zoning_district": "DEMO"})
    assert res.outputs["d"] == 0.2


def test_as2_min_max_clamp_select_exactly_at_a_tie():
    doc = _syn_doc(
        steps=[
            {"id": "sum", "op": "add", "args": [{"const": 0.1}, {"const": 0.2}]},
            {"id": "picked", "op": "min", "args": [{"step": "sum"}, {"const": 0.3}]},
            {"id": "capped", "op": "clamp",
             "args": [{"step": "sum"}, {"const": 0}, {"const": 0.3}]},
        ],
        outputs={"picked": {"step": "picked"}, "capped": {"step": "capped"}},
        out_specs=[{"name": "picked", "type": "number"}, {"name": "capped", "type": "number"}],
    )
    res = _eval(doc, {"zoning_district": "DEMO"})
    # min(0.3, 0.3) and clamp(0.3, 0, 0.3) are both exactly 0.3 (no float tie error).
    assert res.outputs["picked"] == 0.3
    assert res.outputs["capped"] == 0.3


def test_as2_compliance_at_exact_computed_cap_is_inclusive_pass():
    # proposed floor area exactly equal to the computed cap must pass a `le` cap.
    doc = _syn_doc(
        inputs=[
            {"name": "zoning_district", "type": "string", "required": True},
            {"name": "lot_area_sq_ft", "type": "number", "required": True,
             "unit": "square_feet", "exclusive_minimum": 0},
            {"name": "proposed_sq_ft", "type": "number", "required": True,
             "unit": "square_feet", "exclusive_minimum": 0},
        ],
        parameters=[{"name": "far", "value": 2.5, "citation_ref": "zr-demo-m4t003"}],
        steps=[
            {"id": "far", "op": "identity", "args": [{"param": "far"}]},
            {"id": "max_fa", "op": "multiply",
             "args": [{"input": "lot_area_sq_ft"}, {"step": "far"}]},
        ],
        outputs={"max_fa": {"step": "max_fa"}},
        out_specs=[{"name": "max_fa", "type": "number", "unit": "square_feet"}],
        determination={
            "id": "cap", "left": {"input": "proposed_sq_ft"}, "compare": "le",
            "right": {"output": "max_fa"}, "pass_label": "within", "fail_label": "exceeds",
        },
    )
    # lot 1234.5 * FAR 2.5 = 3086.25 exactly.
    base = {"zoning_district": "DEMO", "lot_area_sq_ft": 1234.5}
    at_cap = _eval(doc, {**base, "proposed_sq_ft": 3086.25})
    assert at_cap.trace.determination["outcome"] == "pass"
    assert at_cap.trace.determination["right_value"] == 3086.25
    over = _eval(doc, {**base, "proposed_sq_ft": 3086.26})
    assert over.trace.determination["outcome"] == "fail"


def test_as2_exact_trace_is_json_safe():
    doc = _syn_doc(
        steps=[{"id": "q", "op": "divide", "args": [{"const": 1}, {"const": 3}]}],
        outputs={"q": {"step": "q"}},
        out_specs=[{"name": "q", "type": "number"}],
    )
    res = _eval(doc, {"zoning_district": "DEMO"})
    # a non-terminating quotient still renders to a finite JSON number.
    json.dumps(res.export(), allow_nan=False)
    assert abs(res.outputs["q"] - (1 / 3)) < 1e-9


# ==========================================================================
# AS-3 - differential (native vs independent exact recompute) + properties.
# ==========================================================================

def _r5_far_map() -> dict[str, Fraction]:
    doc = json.loads(_R5_PATH.read_text(encoding="utf-8"))
    raw = next(p["value"] for p in doc["parameters"] if p["name"] == "standard_far_by_district")
    return {district: units.to_exact(value) for district, value in raw.items()}


def _r5_inputs(district: str, area) -> dict:
    return {
        "zoning_district": district,
        "lot_area_sq_ft": area,
        "site_class": "standard_zoning_lot",
    }


def test_as3_differential_native_vs_independent_exact_recompute(registry):
    far_map = _r5_far_map()
    rng = random.Random(20260724)
    checked = 0
    for _ in range(400):
        district = rng.choice(["R5", "R5A", "R5B", "R5D"])
        # areas including non-float-representable decimals (2 fractional digits).
        area = rng.randint(1, 20_000_000) + rng.randint(0, 99) / 100
        far = far_map[district]
        exact_floor = units.to_exact(area) * far  # independent exact recompute
        res = registry.evaluate(_R5, _r5_inputs(district, area))
        assert res.outputs["max_residential_far"] == units.to_json_number(far)
        assert res.outputs["max_residential_floor_area_sq_ft"] == units.to_json_number(exact_floor)
        checked += 1
    assert checked == 400


def test_as3_property_floor_area_scales_linearly_with_lot_area(registry):
    # Integer areas + integer factors so the SCALED INPUT k*A is itself exact
    # (a float a*k would already have lost precision before the engine saw it);
    # non-representable decimals are covered by the differential test above.
    far_map = _r5_far_map()
    rng = random.Random(11)
    for _ in range(100):
        district = rng.choice(["R5", "R5A", "R5B", "R5D"])
        area = rng.randint(1, 1_000_000)
        factor = rng.randint(2, 9)
        far = far_map[district]
        base = registry.evaluate(_R5, _r5_inputs(district, area))
        scaled = registry.evaluate(_R5, _r5_inputs(district, area * factor))
        # FAR cap is invariant to lot area.
        assert scaled.outputs["max_residential_far"] == base.outputs["max_residential_far"]
        # floor area scales EXACTLY by the factor (no float drift): floor(k*A) equals
        # the exact k*A*FAR rendered the same way.
        expected = units.to_json_number(units.to_exact(area) * far * factor)
        assert scaled.outputs["max_residential_floor_area_sq_ft"] == expected
        # and it is exactly the factor times the base result (linearity).
        assert (
            units.to_exact(area * factor) * far
            == factor * (units.to_exact(area) * far)
        )
        # monotonic: a larger lot never yields a smaller floor area.
        assert (
            scaled.outputs["max_residential_floor_area_sq_ft"]
            >= base.outputs["max_residential_floor_area_sq_ft"]
        )


def test_as3_far_cap_constant_across_areas(registry):
    for district, far in _r5_far_map().items():
        seen = {
            registry.evaluate(_R5, _r5_inputs(district, area)).outputs["max_residential_far"]
            for area in (100, 2500.5, 999999.99, 12345678)
        }
        assert seen == {units.to_json_number(far)}


# ==========================================================================
# AS-4 - explicit per-rule rounding (mode/scale/order) + unit enforcement.
# ==========================================================================

def test_as4_round_op_uses_documented_half_up_mode():
    # round(2.5, 0) is 3 (half away from zero), NOT banker's 2; and round(2.675, 2)
    # is 2.68 exactly (float round(2.675, 2) == 2.67 is the trap).
    assert round(2.675, 2) == 2.67  # the float trap this engine avoids
    doc = _syn_doc(
        steps=[
            {"id": "tie", "op": "round", "args": [{"const": 2.5}, {"const": 0}]},
            {"id": "two_places", "op": "round", "args": [{"const": 2.675}, {"const": 2}]},
        ],
        outputs={"tie": {"step": "tie"}, "two_places": {"step": "two_places"}},
        out_specs=[{"name": "tie", "type": "number"}, {"name": "two_places", "type": "number"}],
    )
    res = _eval(doc, {"zoning_district": "DEMO"})
    assert res.outputs["tie"] == 3.0
    assert res.outputs["two_places"] == 2.68


def test_as4_rounding_order_intermediates_stay_exact_until_an_explicit_round():
    # A rule that divides then rounds: the intermediate 1/3 is kept exact and only
    # the explicit round step reduces scale. Without a round step the full-precision
    # value is emitted (rounding is per-rule and explicit, never implicit).
    rounded = _syn_doc(
        steps=[
            {"id": "third", "op": "divide", "args": [{"const": 1}, {"const": 3}]},
            {"id": "r", "op": "round", "args": [{"step": "third"}, {"const": 2}]},
        ],
        outputs={"r": {"step": "r"}},
        out_specs=[{"name": "r", "type": "number"}],
    )
    unrounded = _syn_doc(
        steps=[{"id": "third", "op": "divide", "args": [{"const": 1}, {"const": 3}]}],
        outputs={"third": {"step": "third"}},
        out_specs=[{"name": "third", "type": "number"}],
    )
    assert _eval(rounded, {"zoning_district": "DEMO"}).outputs["r"] == 0.33
    assert _eval(unrounded, {"zoning_district": "DEMO"}).outputs["third"] == pytest.approx(1 / 3)


def test_as4_round_rejects_non_integer_ndigits():
    doc = _syn_doc(
        steps=[{"id": "r", "op": "round", "args": [{"const": 2.5}, {"const": 1.5}]}],
        outputs={"r": {"step": "r"}},
        out_specs=[{"name": "r", "type": "number"}],
    )
    with pytest.raises(EvaluationError):
        _eval(doc, {"zoning_district": "DEMO"})


def test_as4_unknown_unit_fails_closed_no_value():
    doc = _syn_doc(
        inputs=[
            {"name": "zoning_district", "type": "string", "required": True},
            {"name": "measure", "type": "number", "required": True, "unit": "furlongs"},
        ],
        steps=[{"id": "s", "op": "identity", "args": [{"input": "measure"}]}],
        outputs={"s": {"step": "s"}},
        out_specs=[{"name": "s", "type": "number", "unit": "furlongs"}],
    )
    res = _eval(doc, {"zoning_district": "DEMO", "measure": 10})
    assert res.coverage_status == _PRR
    assert res.outputs == {}
    assert any("unknown" in note.lower() and "unit" in note.lower() for note in res.trace.notes)
    json.dumps(res.export(), allow_nan=False)


def test_as4_known_units_are_accepted(registry):
    # sanity: the real R5 rule (square_feet / far units) is NOT rejected.
    res = registry.evaluate(_R5, _r5_inputs("R5", 10000))
    assert res.coverage_status == cov.COVERAGE_CONDITIONAL
    assert res.outputs["max_residential_floor_area_sq_ft"] == 15000.0


def test_as4_division_by_zero_fails_closed_without_a_value():
    doc = _syn_doc(
        steps=[{"id": "q", "op": "divide", "args": [{"const": 1}, {"const": 0}]}],
        outputs={"q": {"step": "q"}},
        out_specs=[{"name": "q", "type": "number"}],
    )
    with pytest.raises(EvaluationError):
        _eval(doc, {"zoning_district": "DEMO"})


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_as4_non_finite_numeric_input_fails_closed(registry, bad):
    res = registry.evaluate(_R5, _r5_inputs("R5", bad))
    assert res.coverage_status == _PRR
    assert res.outputs == {}
    assert res.trace.input_validation["valid"] is False
    json.dumps(res.export(), allow_nan=False)


def test_as4_overflow_output_representability_fails_closed(registry):
    # 1.2e308 * FAR 1.5 = 1.8e308 overflows the finite JSON-number range even though
    # the exact rational is finite: fail closed rather than emit a value.
    res = registry.evaluate(_R5, _r5_inputs("R5", 1.2e308))
    assert res.coverage_status == _PRR
    assert res.outputs == {}
    assert any("non-finite result" in note for note in res.trace.notes)
    json.dumps(res.export(), allow_nan=False)


# ==========================================================================
# Geometry-float isolation: a geometry float crosses onto the legal path only
# through the explicit typed conversion (units.to_exact).
# ==========================================================================

def test_geometry_float_is_canonicalized_exactly(registry):
    # A shapely-style area float crosses onto the legal path through to_exact, which
    # builds the value from its canonical decimal string - so the float and that
    # string are the SAME exact rational, and the engine's floor area is the exact
    # product (no binary-noise drift from the geometry engine's float).
    geom_area = 5000.123456789  # as if produced by a geometry engine (float)
    far = _r5_far_map()["R5"]
    assert units.to_exact(geom_area) == units.to_exact(str(geom_area))
    res = registry.evaluate(_R5, _r5_inputs("R5", geom_area))
    expected = units.to_json_number(units.to_exact(geom_area) * far)
    assert res.outputs["max_residential_floor_area_sq_ft"] == expected


def test_geometry_float_never_reaches_arithmetic_as_a_float():
    # The boundary is units.to_exact: it turns a raw geometry float into an exact
    # rational before any legal arithmetic, so downstream ops see no float.
    geom_area = 3333.333333333
    exact = units.to_exact(geom_area)
    assert isinstance(exact, Fraction)
    # every op composed on that value stays exact.
    product = COMPUTE_OPS["multiply"]([geom_area, Fraction(3, 2)])
    assert isinstance(product, Fraction)
    assert product == exact * Fraction(3, 2)
