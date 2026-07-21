"""M4-T003 rules-engine correctness-hardening acceptance pack (RH-S1 .. RH-S8).

Driven by the owner launch-readiness review (2026-07-21). Everything is offline
and deterministic. The production engine + R5 rule live under
services/api/app/rules/**; SYNTHETIC temporal + compliance fixtures under
tests/rules/fixtures/m4t003/** exercise the new capabilities with zero impact on
the accepted M4-T001 pack.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import jsonschema
import pytest

from app.rules import RuleRegistry
from app.rules import coverage as cov
from app.rules.dsl import DSLError, build_rule_definition, evaluation_trace_schema
from app.rules.snapshots import SnapshotStore

_R5 = "r5-residential-far"
_ENGINE_DIR = Path(__file__).resolve().parents[2] / "app" / "rules"
_R5_PATH = _ENGINE_DIR / "rulesets" / "r5_residential_far.rule.json"
_M4T003 = Path(__file__).resolve().parent / "fixtures" / "m4t003"

_PRR = cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED


def _r5_doc() -> dict:
    return json.loads(_R5_PATH.read_text("utf-8"))


def _std(district: str, area: float) -> dict:
    return {
        "zoning_district": district,
        "lot_area_sq_ft": area,
        "site_class": "standard_zoning_lot",
    }


def _eff_ids(reg: RuleRegistry, family: str, date: str) -> list[str]:
    return [r.rule_id for r in reg.effective_rules(family, date)]


@pytest.fixture
def registry() -> RuleRegistry:
    return RuleRegistry().load()


@pytest.fixture
def hardening_registry() -> RuleRegistry:
    """Registry over the SYNTHETIC M4-T003 temporal + compliance fixtures."""
    snaps = SnapshotStore(_M4T003 / "snapshots")
    return RuleRegistry(_M4T003 / "rulesets", snapshots=snaps).load()


# --------------------------------------------------------------------------
# RH-S1 - negative numeric input fails closed (the owner's exact defect).
# --------------------------------------------------------------------------

def test_rh_s1_negative_lot_area_fails_closed_no_value(registry):
    result = registry.evaluate(
        _R5, {"zoning_district": "R5", "lot_area_sq_ft": -5000, "site_class": "standard_zoning_lot"}
    )
    assert result.coverage_status == _PRR
    assert result.outputs == {}  # never a negative floor area
    validation = result.trace.input_validation
    assert validation["valid"] is False
    assert any(iv["name"] == "lot_area_sq_ft" for iv in validation["invalid_inputs"])
    assert result.trace.data_completeness == cov.COMPLETENESS_MISSING_CRITICAL


# --------------------------------------------------------------------------
# RH-S2 - non-finite numeric input fails closed; the trace stays strict JSON.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_rh_s2_non_finite_lot_area_fails_closed(registry, bad):
    result = registry.evaluate(_R5, {"zoning_district": "R5", "lot_area_sq_ft": bad})
    assert result.coverage_status == _PRR
    assert result.outputs == {}
    # the fail-closed trace records the offending input yet is STRICT JSON
    # (non-finite floats are represented as strings, so allow_nan=False is safe)
    json.dumps(result.export(), allow_nan=False)


# --------------------------------------------------------------------------
# RH-S3 - wrong type / invalid enum fail closed (no crash, no silent accept).
# --------------------------------------------------------------------------

def test_rh_s3_wrong_type_fails_closed_no_crash(registry):
    result = registry.evaluate(_R5, {"zoning_district": "R5", "lot_area_sq_ft": "not-a-number"})
    assert result.coverage_status == _PRR
    assert result.outputs == {}
    assert result.trace.input_validation["valid"] is False


def test_rh_s3_invalid_enum_fails_closed(registry):
    result = registry.evaluate(
        _R5, {"zoning_district": "R5", "lot_area_sq_ft": 5000, "site_class": "banana"}
    )
    assert result.coverage_status == _PRR
    assert any(
        iv["name"] == "site_class" for iv in result.trace.input_validation["invalid_inputs"]
    )


def test_rh_s3_non_r5_district_is_still_not_applicable_not_invalid(registry):
    # zoning_district scope is applicability, NOT a domain enum: R7 is a visible
    # not_applicable, never an invalid input (preserves M4-T001 + M4-T002 RI-S6).
    result = registry.evaluate(_R5, _std("R7", 5000))
    assert result.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert result.trace.input_validation["valid"] is True


# --------------------------------------------------------------------------
# RH-S4 - predicate / determination references validated fail-closed at LOAD.
# --------------------------------------------------------------------------

def test_rh_s4_misspelled_applicability_input_rejected_at_load(registry):
    doc = _r5_doc()
    doc["applicability"] = {"op": "in_set", "input": "zoning_distrct", "values": ["R5"]}
    with pytest.raises(DSLError):
        build_rule_definition(doc, registry.snapshots)


def test_rh_s4_misspelled_exception_condition_input_rejected_at_load(registry):
    doc = _r5_doc()
    doc["exceptions"][0]["condition"] = {
        "not": {"op": "equals", "input": "site_clas", "value": "standard_zoning_lot"}
    }
    with pytest.raises(DSLError):
        build_rule_definition(doc, registry.snapshots)


def test_rh_s4_determination_undeclared_output_rejected_at_load(hardening_registry):
    doc = json.loads((_M4T003 / "rulesets" / "demo-compliance-far.rule.json").read_text("utf-8"))
    doc["determination"]["right"] = {"output": "nonexistent_output"}
    with pytest.raises(DSLError):
        build_rule_definition(doc, hardening_registry.snapshots)


# --------------------------------------------------------------------------
# RH-S5 - rule test/lifecycle release status carried in every trace.
# --------------------------------------------------------------------------

def test_rh_s5_release_status_in_trace_draft_not_verified_eligible(registry):
    release = registry.evaluate(_R5, _std("R5", 5000)).trace.rule_release
    assert release["lifecycle_status"] == "needs_review"
    assert release["verified_eligible"] is False
    assert release["qualified_human_approval"] == "pending"
    assert release["independent_review"] == "pending"
    assert release["deterministic_tests"] == "declared"  # the R5 rule declares its suite


# --------------------------------------------------------------------------
# RH-S6 - effective-date temporal versioning (before/after transition).
# --------------------------------------------------------------------------

def test_rh_s6_effective_date_selects_version(hardening_registry):
    hr, fam = hardening_registry, "demo_temporal_far"
    inputs = {"zoning_district": "DEMO", "lot_area_sq_ft": 10000}

    # Before the 2024-01-01 amendment -> only version 1 governs.
    assert _eff_ids(hr, fam, "2023-06-01") == ["demo-temporal-far-v1"]
    before = hr.evaluate("demo-temporal-far-v1", inputs, as_of_date="2023-06-01")
    assert before.outputs["max_far"] == 1.0
    v2_before = hr.evaluate("demo-temporal-far-v2", inputs, as_of_date="2023-06-01")
    assert v2_before.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert v2_before.trace.effective_window["in_effect"] is False

    # On/after the amendment (half-open boundary) -> only version 2 governs.
    for on_after in ("2024-01-01", "2024-06-01"):
        assert _eff_ids(hr, fam, on_after) == ["demo-temporal-far-v2"]
    after = hr.evaluate("demo-temporal-far-v2", inputs, as_of_date="2024-06-01")
    assert after.outputs["max_far"] == 2.0
    v1_after = hardening_registry.evaluate("demo-temporal-far-v1", inputs, as_of_date="2024-06-01")
    assert v1_after.coverage_status == cov.COVERAGE_NOT_APPLICABLE


def test_rh_s6_no_as_of_means_no_temporal_gating(hardening_registry):
    inputs = {"zoning_district": "DEMO", "lot_area_sq_ft": 10000}
    result = hardening_registry.evaluate("demo-temporal-far-v1", inputs)  # as_of_date=None
    assert result.trace.effective_window["evaluated_as_of"] is None
    assert result.trace.effective_window["in_effect"] is True
    assert result.outputs["max_far"] == 1.0


# --------------------------------------------------------------------------
# RH-S7 - compliance determination: a genuine applies+passes / applies+fails.
# --------------------------------------------------------------------------

def test_rh_s7_compliance_pass_and_fail(hardening_registry):
    base = {"zoning_district": "DEMO", "lot_area_sq_ft": 10000}  # max floor area = 15000

    ok = hardening_registry.evaluate(
        "demo-compliance-far", {**base, "proposed_floor_area_sq_ft": 12000}
    )
    assert ok.coverage_status == cov.COVERAGE_CONDITIONAL
    assert ok.trace.determination["outcome"] == "pass"
    assert ok.trace.determination["label"] == "within_far_limit"
    assert ok.trace.determination["left_value"] == 12000.0
    assert ok.trace.determination["right_value"] == 15000.0

    over = hardening_registry.evaluate(
        "demo-compliance-far", {**base, "proposed_floor_area_sq_ft": 20000}
    )
    assert over.coverage_status == cov.COVERAGE_CONDITIONAL  # a fail does NOT change coverage
    assert over.trace.determination["outcome"] == "fail"
    assert over.trace.determination["label"] == "exceeds_far_limit"


def test_rh_s7_no_determination_when_rule_has_none(registry):
    # the R5 rule declares no determination -> the trace field is null
    assert registry.evaluate(_R5, _std("R5", 5000)).trace.determination is None


# --------------------------------------------------------------------------
# RH-S8 - regression: valid inputs still compute; trace validates; determinism;
# nothing verified; existing engine pack unaffected (run separately).
# --------------------------------------------------------------------------

def test_rh_s8_valid_r5_still_computes(registry):
    result = registry.evaluate(_R5, _std("R5", 10000))
    assert result.coverage_status == cov.COVERAGE_CONDITIONAL
    assert result.outputs["max_residential_floor_area_sq_ft"] == 15000.0
    assert result.trace.input_validation["valid"] is True


def test_rh_s8_hardened_trace_validates_against_schema(registry, hardening_registry):
    r5_trace = registry.evaluate(_R5, _std("R5", 10000)).export()
    jsonschema.Draft202012Validator(evaluation_trace_schema()).validate(r5_trace)
    comp = hardening_registry.evaluate(
        "demo-compliance-far",
        {"zoning_district": "DEMO", "lot_area_sq_ft": 10000, "proposed_floor_area_sq_ft": 12000},
    ).export()
    jsonschema.Draft202012Validator(evaluation_trace_schema()).validate(comp)


def test_rh_s8_determinism_same_inputs_identical_trace(registry):
    inputs = _std("R5", 10000)
    a = registry.evaluate(_R5, inputs).export()
    b = RuleRegistry().load().evaluate(_R5, inputs).export()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_rh_s8_nothing_verified(registry, hardening_registry):
    demo_far = {"zoning_district": "DEMO", "lot_area_sq_ft": 10000}
    compliance_inp = {**demo_far, "proposed_floor_area_sq_ft": 12000}
    for reg, rid, inp in [
        (registry, _R5, _std("R5", 10000)),
        (hardening_registry, "demo-temporal-far-v2", demo_far),
        (hardening_registry, "demo-compliance-far", compliance_inp),
    ]:
        result = reg.evaluate(rid, inp)
        assert result.coverage_status != cov.COVERAGE_VERIFIED
        assert result.trace.rule_release["verified_eligible"] is False


def test_rh_s8_finite_helpers_are_strict():
    # guardrail on the finiteness check the fail-closed path depends on
    assert math.isfinite(0.0) and not math.isfinite(float("inf"))
