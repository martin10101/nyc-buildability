"""Executable acceptance pack AS-1..AS-12 for the deterministic scenario
foundation (task M5-T001, proposal section 6).

Offline and deterministic. Each test maps to exactly one acceptance scenario and
asserts the honest-labelling and fail-closed guarantees the packet requires. The
builder is exercised against the same rule_evaluation payload shape the rule
engine actually emits (the committed canonical fixture) plus targeted variants.
"""

from __future__ import annotations

import copy
import json
import math

import pytest

from app.scenario import (
    CAP_OUTPUT_NAME,
    DRAFT_CAP_LABEL,
    NOT_VERIFIED_DISCLAIMER,
    SCENARIO_CONTRACT_VERSION,
    ConstraintCompleteness,
    ScenarioKind,
    build_scenario,
    validate_scenario_document,
)

from . import _support as S


def _coverage_values(node):
    """Every value stored under a 'coverage_status' key anywhere in a payload."""
    out = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "coverage_status" and isinstance(value, str):
                out.append(value)
            out.extend(_coverage_values(value))
    elif isinstance(node, list):
        for item in node:
            out.extend(_coverage_values(item))
    return out


def _constraint(document, key):
    for constraint in document["constraints"]:
        if constraint["key"] == key:
            return constraint
    raise AssertionError(f"constraint {key!r} not found")


# ---------------------------------------------------------------------------
# AS-1 confident R5 cap: surface the CANONICAL value verbatim.
# ---------------------------------------------------------------------------


def test_as1_confident_r5_cap_surfaces_canonical_trace_value():
    rule_evaluation = S.canonical_rule_evaluation()
    document = build_scenario(S.profile(), rule_evaluation)
    validate_scenario_document(document)

    assert document["scenario_kind"] == ScenarioKind.PRELIMINARY.value
    assert document["coverage_status"] == "conditional"
    assert document["contract_version"] == SCENARIO_CONTRACT_VERSION

    # The surfaced value EQUALS the trace value (not a locally recomputed one).
    assert document["draft_zoning_floor_area_cap_sq_ft"] == S.trace_cap(rule_evaluation)

    cap_constraint = _constraint(document, "residential_far_cap")
    assert cap_constraint["state"] == ConstraintCompleteness.DRAFT.value
    assert cap_constraint["value"] == S.trace_cap(rule_evaluation)

    # Mandatory label + not-Verified lineage attached to the value.
    assert document["cap_label"] == DRAFT_CAP_LABEL
    assert document["needs_review"] is True
    assert document["not_verified_disclaimer"] == NOT_VERIFIED_DISCLAIMER
    assert "verified" not in _coverage_values(document)


def test_as1_value_comes_from_trace_not_recompute_even_without_far():
    """With max_residential_far ABSENT, no far*lot_area recompute is possible, yet
    the cap is still surfaced from the trace - proving the value is READ from the
    trace, never locally derived."""
    rule_evaluation = S.canonical_rule_evaluation()
    del rule_evaluation["evaluations"][0]["outputs"]["max_residential_far"]
    document = build_scenario(S.profile(), rule_evaluation)
    validate_scenario_document(document)

    assert document["scenario_kind"] == ScenarioKind.PRELIMINARY.value
    assert document["draft_zoning_floor_area_cap_sq_ft"] == S.trace_cap(rule_evaluation)
    assert document["integrity_check"]["performed"] is False


# ---------------------------------------------------------------------------
# AS-2 unsupported district -> typed unsupported stub, no cap, visible reason.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rule_evaluation_factory",
    [S.unsupported_rule_evaluation, S.not_applicable_rule_evaluation],
)
def test_as2_unsupported_family_is_visible_stub_no_cap(rule_evaluation_factory):
    document = build_scenario(S.profile(), rule_evaluation_factory())
    validate_scenario_document(document)

    assert document["scenario_kind"] == ScenarioKind.UNSUPPORTED.value
    assert document["coverage_status"] in {"unsupported", "not_applicable"}
    assert document["draft_zoning_floor_area_cap_sq_ft"] is None
    assert document["cap_label"] is None
    assert document["reasons"], "an unsupported outcome must carry a visible reason"
    assert (
        _constraint(document, "residential_far_cap")["state"]
        == ConstraintCompleteness.UNSUPPORTED.value
    )


# ---------------------------------------------------------------------------
# AS-3 missing constraint -> NO scenario naming the missing datum; nothing inferred.
# ---------------------------------------------------------------------------


def test_as3_missing_required_input_names_the_gap_and_infers_nothing():
    document = build_scenario(S.profile(), S.missing_lot_area_rule_evaluation())
    validate_scenario_document(document)

    assert document["scenario_kind"] == ScenarioKind.NO_SCENARIO.value
    assert document["draft_zoning_floor_area_cap_sq_ft"] is None
    joined_reasons = " ".join(document["reasons"]).lower()
    assert "lot_area" in joined_reasons or "controlling input" in joined_reasons

    # Nothing inferred: every envelope family is still MISSING with no value.
    for key in ("height_limit", "setbacks_yards", "lot_coverage_open_space"):
        constraint = _constraint(document, key)
        assert constraint["state"] == ConstraintCompleteness.MISSING.value
        assert constraint["value"] is None


# ---------------------------------------------------------------------------
# AS-4 spatial uncertainty -> NO scenario; ranges/flags surfaced, never collapsed.
# ---------------------------------------------------------------------------


def test_as4_spatial_uncertainty_blocks_and_preserves_ranges():
    document = build_scenario(S.profile(), S.professional_review_rule_evaluation())
    validate_scenario_document(document)

    assert document["scenario_kind"] == ScenarioKind.NO_SCENARIO.value
    assert document["coverage_status"] == "professional_review_required"
    assert document["professional_review_required"] is True
    assert document["draft_zoning_floor_area_cap_sq_ft"] is None

    district = _constraint(document, "zoning_district")
    assert district["state"] == ConstraintCompleteness.PROFESSIONAL_REVIEW_REQUIRED.value
    # Share RANGES are surfaced, never collapsed into a single definitive district.
    candidates = district["provenance"]["base_district_candidates"]
    assert len(candidates) == 2
    assert candidates[0]["share_min"] != candidates[0]["share_max"]


# ---------------------------------------------------------------------------
# AS-5 legal-rule conflict -> NO scenario; competing-rule provenance surfaced.
# ---------------------------------------------------------------------------


def test_as5_rule_conflict_blocks_and_surfaces_competing_rules():
    document = build_scenario(S.profile(), S.conflict_rule_evaluation())
    validate_scenario_document(document)

    assert document["scenario_kind"] == ScenarioKind.NO_SCENARIO.value
    assert document["coverage_status"] == "data_conflict"
    assert document["draft_zoning_floor_area_cap_sq_ft"] is None

    cap = _constraint(document, "residential_far_cap")
    assert cap["state"] == ConstraintCompleteness.CONFLICTING.value
    competing = cap["provenance"]["competing_rules"]
    assert {rule["rule_id"] for rule in competing} == {
        "r5-residential-far",
        "r5-residential-far-alt",
    }


# ---------------------------------------------------------------------------
# AS-6 malformed / non-finite inputs -> fail-closed, no crash, strict-JSON.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "field,value",
    [
        ("lot_area_sq_ft", float("nan")),
        ("lot_area_sq_ft", float("inf")),
        ("lot_area_sq_ft", 10**400),  # huge int: overflows float -> inf
        ("lot_area_sq_ft", "10000"),  # wrong type
        ("lot_area_sq_ft", -5.0),  # non-positive
        ("max_residential_floor_area_sq_ft", float("nan")),
        ("max_residential_floor_area_sq_ft", float("-inf")),
        ("max_residential_floor_area_sq_ft", 0),  # non-positive cap
    ],
)
def test_as6_malformed_inputs_fail_closed_no_crash(field, value):
    document = build_scenario(S.profile(), S.malformed_rule_evaluation(field, value))

    assert document["scenario_kind"] == ScenarioKind.NO_SCENARIO.value
    assert document["professional_review_required"] is True
    assert document["draft_zoning_floor_area_cap_sq_ft"] is None

    # No negative / NaN / inf value survives anywhere; output stays strict-JSON.
    serialized = json.dumps(document, allow_nan=False)  # raises on NaN/inf
    reparsed = json.loads(serialized)
    for surfaced in _all_numbers(reparsed):
        assert math.isfinite(surfaced)
    # The document validates against the canonical schema (never returns invalid).
    validate_scenario_document(document)


def _all_numbers(node):
    out = []
    if isinstance(node, dict):
        for value in node.values():
            out.extend(_all_numbers(value))
    elif isinstance(node, list):
        for item in node:
            out.extend(_all_numbers(item))
    elif isinstance(node, int | float) and not isinstance(node, bool):
        out.append(node)
    return out


# ---------------------------------------------------------------------------
# AS-7 integrity disagreement fails closed; canonical value never replaced.
# ---------------------------------------------------------------------------


def test_as7_integrity_disagreement_fails_closed_and_surfaces_no_number():
    rule_evaluation = S.integrity_disagreement_rule_evaluation()
    canonical_cap = S.trace_cap(rule_evaluation)  # 15000
    recompute = 1.5 * rule_evaluation["lot_area_sq_ft"]  # 30000
    assert canonical_cap != recompute

    document = build_scenario(S.profile(), rule_evaluation)
    validate_scenario_document(document)

    assert document["scenario_kind"] == ScenarioKind.NO_SCENARIO.value
    assert document["coverage_status"] == "data_conflict"
    assert document["integrity_check"]["performed"] is True
    assert document["integrity_check"]["agreed"] is False

    # Neither the canonical value NOR the recompute is surfaced as a result.
    assert document["draft_zoning_floor_area_cap_sq_ft"] is None
    surfaced_numbers = _all_numbers(document)
    assert canonical_cap not in surfaced_numbers
    assert recompute not in surfaced_numbers


# ---------------------------------------------------------------------------
# AS-8 deterministic ordering -> byte-identical output for identical input.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rule_evaluation_factory",
    [
        S.canonical_rule_evaluation,
        S.unsupported_rule_evaluation,
        S.conflict_rule_evaluation,
        S.professional_review_rule_evaluation,
    ],
)
def test_as8_identical_input_yields_byte_identical_output(rule_evaluation_factory):
    first = build_scenario(S.profile(), rule_evaluation_factory())
    second = build_scenario(S.profile(), rule_evaluation_factory())
    # Insertion-order-preserving dump: proves stable key AND value ordering.
    assert json.dumps(first) == json.dumps(second)


# ---------------------------------------------------------------------------
# AS-9 never-Verified: exhaustive check; disclaimer + needs_review lineage.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rule_evaluation_factory",
    [
        S.canonical_rule_evaluation,
        S.unsupported_rule_evaluation,
        S.not_applicable_rule_evaluation,
        S.conflict_rule_evaluation,
        S.professional_review_rule_evaluation,
        S.missing_lot_area_rule_evaluation,
        S.integrity_disagreement_rule_evaluation,
    ],
)
def test_as9_no_scenario_is_ever_verified(rule_evaluation_factory):
    document = build_scenario(S.profile(), rule_evaluation_factory())
    validate_scenario_document(document)  # also asserts no verified coverage_status
    assert "verified" not in _coverage_values(document)
    assert document["needs_review"] is True
    assert document["not_verified_disclaimer"] == NOT_VERIFIED_DISCLAIMER


# ---------------------------------------------------------------------------
# AS-10 provenance & completeness preserved on every constraint and output.
# ---------------------------------------------------------------------------


def test_as10_provenance_and_completeness_preserved():
    rule_evaluation = S.canonical_rule_evaluation()
    document = build_scenario(S.profile(), rule_evaluation)

    # Every constraint carries a completeness state and a ConstraintCompleteness.
    valid_completeness = {"complete", "missing_noncritical", "missing_critical"}
    valid_states = {state.value for state in ConstraintCompleteness}
    for constraint in document["constraints"]:
        assert constraint["data_completeness"] in valid_completeness
        assert constraint["state"] in valid_states

    # Cap provenance: rule citation(s) + rule_id/version/status, propagated verbatim.
    cap_prov = document["cap_provenance"]
    trace = rule_evaluation["evaluations"][0]
    assert cap_prov["rule_id"] == trace["rule_id"]
    assert cap_prov["rule_version"] == trace["rule_version"]
    assert cap_prov["rule_status"] == trace["rule_status"]
    assert cap_prov["output_name"] == CAP_OUTPUT_NAME
    assert cap_prov["citations"][0]["snapshot_id"] == trace["citations"][0]["snapshot_id"]
    assert cap_prov["citations"][0]["provenance"] == trace["citations"][0]["provenance"]

    # Lot-area provenance: profile field + dataset resolved from the profile.
    lot_prov = _constraint(document, "lot_area")["provenance"]
    assert lot_prov["profile_field"] == rule_evaluation["lot_area_source"]
    assert lot_prov["resolved"][0]["source_id"] == "nyc-dcp-lot-geometry"
    assert lot_prov["resolved"][0]["dataset_version"] == "26v1"


# ---------------------------------------------------------------------------
# AS-11 explicit-assumption-only variation; no hidden factor ever applied.
# ---------------------------------------------------------------------------


def test_as11_variation_only_via_explicit_assumption_no_hidden_factor():
    rule_evaluation = S.canonical_rule_evaluation()
    baseline = build_scenario(S.profile(), rule_evaluation)

    explicit_assumption = {
        "key": "utilization_factor",
        "assumption_type": "utilization_factor",
        "value": 0.8,
        "unit": "ratio",
        "rationale": "illustrative explicit assumption",
    }
    variant = build_scenario(
        S.profile(), rule_evaluation, assumptions=[explicit_assumption]
    )

    # The surfaced cap is the RAW draft cap in BOTH - no hidden 0.8 factor applied.
    assert baseline["draft_zoning_floor_area_cap_sq_ft"] == S.trace_cap(rule_evaluation)
    assert variant["draft_zoning_floor_area_cap_sq_ft"] == S.trace_cap(rule_evaluation)
    assert (
        variant["draft_zoning_floor_area_cap_sq_ft"]
        == baseline["draft_zoning_floor_area_cap_sq_ft"]
    )

    # The ONLY difference between the two documents is the assumptions array.
    assert baseline["assumptions"] == []
    assert variant["assumptions"] == [explicit_assumption]
    baseline_no_assumptions = copy.deepcopy(baseline)
    variant_no_assumptions = copy.deepcopy(variant)
    baseline_no_assumptions["assumptions"] = None
    variant_no_assumptions["assumptions"] = None
    assert json.dumps(baseline_no_assumptions) == json.dumps(variant_no_assumptions)


# ---------------------------------------------------------------------------
# AS-12 regression: builder is read-only (never mutates inputs); no crash on
# an empty/degenerate input. The full-suite / no-canonical-modification proof is
# carried by CI + the producer report (git diff scope).
# ---------------------------------------------------------------------------


def test_as12_builder_never_mutates_its_inputs():
    rule_evaluation = S.canonical_rule_evaluation()
    profile = S.profile()
    rule_evaluation_snapshot = copy.deepcopy(rule_evaluation)
    profile_snapshot = copy.deepcopy(profile)

    build_scenario(profile, rule_evaluation)

    assert rule_evaluation == rule_evaluation_snapshot, "rule_evaluation was mutated"
    assert profile == profile_snapshot, "property_profile was mutated"


def test_as12_degenerate_empty_inputs_fail_closed_not_crash():
    document = build_scenario({}, {})
    validate_scenario_document(document)
    assert document["scenario_kind"] == ScenarioKind.NO_SCENARIO.value
    assert document["draft_zoning_floor_area_cap_sq_ft"] is None
