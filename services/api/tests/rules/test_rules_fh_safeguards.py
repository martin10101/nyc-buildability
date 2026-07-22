"""M4-T004 pre-endpoint fail-closed safeguards acceptance pack (FH-1 / FH-2 / FH-3).

Adversarial, deterministic, and fully offline. Exercises the three future-hardening
items recorded in project-control/reports/M4-RULES-FUTURE-HARDENING.md before the
rules engine is exposed to untrusted callers at a public endpoint:

* FH-1 - ``_valid_iso_date`` now does TRUE calendar validation (impossible days
  such as 2024-02-30 fail closed; a genuine leap day 2024-02-29 stays valid).
* FH-2 - a strictly fail-closed, deterministic, load-order-independent detector
  for a same-family rule CONFLICT (>=2 rules simultaneously in effect and
  independently applicable to the same inputs for an overlapping output). It
  surfaces a typed conflict for professional review and NEVER picks a winner.
* FH-3 - ``assert_not_verified`` tolerates a FOREIGN payload whose ``evaluations``
  (or ``family_coverage``) is a non-list/non-dict, failing safe instead of raising
  ``TypeError`` while still catching any genuine ``verified`` status.

All FH-2 rule fixtures are SYNTHETIC (clearly labelled, no real legal content)
under tests/rules/fixtures/m4t004/** and tests/rules/fixtures/m4t004_res_temporal/**.
The real corpus has a single R5 residential_far rule, so the multi-rule conflict
paths can only be exercised with synthetic fixtures. The real R5 family is proven
UNAFFECTED (no conflict, unchanged behaviour) at the end of the pack.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.rules import RuleRegistry
from app.rules import coverage as cov
from app.rules import integration as ri
from app.rules.evaluator import _valid_iso_date
from app.rules.registry import detect_rule_conflicts
from app.rules.snapshots import SnapshotStore

_R5 = "r5-residential-far"
_FIX = Path(__file__).resolve().parent / "fixtures"
_M4T004 = _FIX / "m4t004"
_M4T004_TEMPORAL = _FIX / "m4t004_res_temporal"
_PRR = cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
_SYNTH_INPUTS = {"zoning_district": "SYNTH", "lot_area_sq_ft": 10000}


# --------------------------------------------------------------------------
# Fixtures / builders.
# --------------------------------------------------------------------------

@pytest.fixture
def registry() -> RuleRegistry:
    """The REAL registry (single R5 residential_far rule)."""
    return RuleRegistry().load()


@pytest.fixture
def synthetic_registry() -> RuleRegistry:
    """SYNTHETIC M4-T004 registry: several families exercising every FH-2 path,
    including a residential_far family holding two always-in-effect conflict rules."""
    snaps = SnapshotStore(_M4T004 / "snapshots")
    return RuleRegistry(_M4T004 / "rulesets", snapshots=snaps).load()


@pytest.fixture
def temporal_registry() -> RuleRegistry:
    """SYNTHETIC registry whose residential_far family is an OVERLAPPING-window
    temporal pair (early up to 2024-06-01, late from 2024-01-01), reusing the
    m4t004 snapshot. Used to prove as_of_date threading through evaluate_property."""
    snaps = SnapshotStore(_M4T004 / "snapshots")
    return RuleRegistry(_M4T004_TEMPORAL / "rulesets", snapshots=snaps).load()


def _confident_synth_profile(district: str = "SYNTH", *, area: float = 10000.0) -> dict:
    """Minimal contract-shaped profile with a confident single base-zoning
    district (the keys evaluate_property actually reads), hand-crafted to keep the
    FH pack independent of the shapely-heavy app.spatial package."""
    return {
        "identity": {"bbl": "1000010001"},
        "spatial_intersection": {
            "lot_overall_class": "single_district_confident",
            "professional_review_required": False,
            "coverage_note": None,
            "pairs": [
                {
                    "family": "base_zoning",
                    "pair_class": "interior_confident",
                    "district_label": district,
                    "lot_area_sq_ft": area,
                    "share_min": 1.0,
                    "share_point": 1.0,
                    "share_max": 1.0,
                    "minor_portion": False,
                }
            ],
            "review_reasons": [],
            "notes": [],
            "provenance_refs": ["prov-spatial"],
            "crosscheck": None,
        },
        "lot_geometry": {
            "outcome": "single_feature",
            "geometry_status": "valid",
            "review_required": False,
            "area_sq_ft": area,
            "provenance_ref": "prov-lotgeom",
        },
    }


def _real_r5_confident_profile(*, area: float = 10000.0) -> dict:
    profile = _confident_synth_profile("R5", area=area)
    return profile


# ==========================================================================
# FH-1 - true calendar validation of as_of_date.
# ==========================================================================

@pytest.mark.parametrize(
    "impossible", ["2024-02-30", "2024-04-31", "2024-11-31", "2025-02-29", "2023-02-29"]
)
def test_fh1_impossible_calendar_date_is_invalid(impossible):
    assert _valid_iso_date(impossible) is False


@pytest.mark.parametrize(
    "real_date", ["2024-02-29", "2024-12-05", "2023-06-01", "2024-01-01", "2000-02-29"]
)
def test_fh1_real_calendar_date_is_valid(real_date):
    # a genuine leap day (2024-02-29, 2000-02-29) stays valid.
    assert _valid_iso_date(real_date) is True


def test_fh1_non_string_and_none_unchanged():
    # the existing non-string/None handling is preserved exactly.
    assert _valid_iso_date(None) is False
    assert _valid_iso_date(20240101) is False
    assert _valid_iso_date(["2024-01-01"]) is False


@pytest.mark.parametrize("impossible", ["2024-02-30", "2024-04-31", "2025-02-29"])
def test_fh1_impossible_date_fails_closed_via_evaluator(registry, impossible):
    # an impossible date routes through the existing as_of_invalid fail-closed path.
    result = registry.evaluate(
        _R5,
        {"zoning_district": "R5", "lot_area_sq_ft": 10000, "site_class": "standard_zoning_lot"},
        as_of_date=impossible,
    )
    assert result.coverage_status == _PRR
    assert result.outputs == {}
    assert result.trace.effective_window["in_effect"] is False
    assert result.trace.applicability_trace[0].get("invalid_as_of_date") is True
    json.dumps(result.export(), allow_nan=False)


def test_fh1_real_leap_date_is_not_the_invalid_path(registry):
    # 2024-02-29 is a REAL date: it must NOT hit the invalid_as_of_date path. It is
    # before the R5 effective_from (2024-12-05), so it is a visible not_effective
    # outcome - proving the date itself parsed as valid.
    result = registry.evaluate(
        _R5, {"zoning_district": "R5", "lot_area_sq_ft": 10000}, as_of_date="2024-02-29"
    )
    assert result.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert "invalid_as_of_date" not in result.trace.applicability_trace[0]
    assert result.trace.applicability_trace[0].get("not_effective") is True


# ==========================================================================
# FH-3 - assert_not_verified tolerates a hostile/foreign payload.
# ==========================================================================

@pytest.mark.parametrize("bad_evaluations", [5, {"a": 1}, "verified", 0, 3.14, ("x",)])
def test_fh3_non_list_evaluations_do_not_crash(bad_evaluations):
    # a non-list evaluations field must be treated as empty, never raise TypeError.
    ri.assert_not_verified(
        {"coverage_status": cov.COVERAGE_CONDITIONAL, "evaluations": bad_evaluations}
    )


@pytest.mark.parametrize("bad_family", [5, "verified", ["x"], 0])
def test_fh3_non_dict_family_coverage_does_not_crash(bad_family):
    ri.assert_not_verified(
        {"coverage_status": cov.COVERAGE_CONDITIONAL, "family_coverage": bad_family}
    )


def test_fh3_still_catches_verified_top_level():
    with pytest.raises(ri.DraftVerifiedError):
        ri.assert_not_verified({"coverage_status": cov.COVERAGE_VERIFIED, "evaluations": 5})


def test_fh3_still_catches_verified_trace_even_with_malformed_family():
    # a genuine verified trace is still caught even when other containers are junk.
    with pytest.raises(ri.DraftVerifiedError):
        ri.assert_not_verified(
            {
                "coverage_status": cov.COVERAGE_CONDITIONAL,
                "evaluations": [
                    {"rule_id": "a", "coverage_status": cov.COVERAGE_CONDITIONAL},
                    {"rule_id": "b", "coverage_status": cov.COVERAGE_VERIFIED},
                ],
                "family_coverage": 999,  # malformed, must be ignored not crash
            }
        )


def test_fh3_still_catches_verified_family_coverage():
    with pytest.raises(ri.DraftVerifiedError):
        ri.assert_not_verified(
            {
                "coverage_status": cov.COVERAGE_CONDITIONAL,
                "evaluations": "junk",  # non-list, ignored
                "family_coverage": {"coverage_status": cov.COVERAGE_VERIFIED},
            }
        )


# ==========================================================================
# FH-2 - same-family conflict detection (module-level detector).
# ==========================================================================

def test_fh2_positive_conflict_is_typed_and_complete(synthetic_registry):
    conflict = synthetic_registry.detect_conflicts("residential_far", _SYNTH_INPUTS)
    assert conflict is not None
    assert conflict["conflict"] is True
    assert conflict["family"] == "residential_far"
    ids = [r["rule_id"] for r in conflict["competing_rules"]]
    assert ids == ["res-far-synth-a", "res-far-synth-b"]  # sorted, deterministic
    # each competing rule carries its effective window (both null here).
    for entry in conflict["competing_rules"]:
        assert "effective_from" in entry and "effective_to" in entry
        assert "rule_version" in entry
        assert entry["output_names"] == ["max_synth_far", "max_synth_floor_area_sq_ft"]
    assert conflict["competing_output_names"] == ["max_synth_far", "max_synth_floor_area_sq_ft"]
    # NO output/determination value is produced from the competing rules.
    assert "outputs" not in conflict
    assert "determination" not in conflict
    # strict-JSON serializable (allow_nan=False).
    json.dumps(conflict, allow_nan=False)


def test_fh2_conflict_is_independent_of_load_order(synthetic_registry):
    rules = synthetic_registry._by_family["residential_far"]
    forward = detect_rule_conflicts(list(rules), _SYNTH_INPUTS)
    reverse = detect_rule_conflicts(list(reversed(rules)), _SYNTH_INPUTS)
    assert forward is not None
    # byte-identical typed conflict regardless of the order rules were supplied.
    assert json.dumps(forward, sort_keys=True) == json.dumps(reverse, sort_keys=True)


def test_fh2_overlapping_windows_conflict_only_inside_overlap(synthetic_registry):
    fam = "syn_window_overlap_far"
    # overlap window is [2024-01-01, 2024-06-01).
    assert synthetic_registry.detect_conflicts(fam, _SYNTH_INPUTS, "2024-03-01") is not None
    # outside the overlap only one rule is in effect -> no conflict.
    assert synthetic_registry.detect_conflicts(fam, _SYNTH_INPUTS, "2023-06-01") is None
    assert synthetic_registry.detect_conflicts(fam, _SYNTH_INPUTS, "2024-09-01") is None


def test_fh2_non_overlapping_windows_never_conflict(synthetic_registry):
    fam = "syn_temporal_far"
    for as_of in ("2023-06-01", "2024-06-01", "2100-01-01"):
        assert synthetic_registry.detect_conflicts(fam, _SYNTH_INPUTS, as_of) is None


def test_fh2_boundary_date_is_deterministic_half_open(synthetic_registry):
    # is_in_effect uses the half-open window [effective_from, effective_to):
    # effective_from INCLUSIVE, effective_to EXCLUSIVE. At the seam 2024-01-01 the
    # early rule (effective_to=2024-01-01, exclusive) is OUT and only the late rule
    # (effective_from=2024-01-01, inclusive) is in effect -> exactly one governs,
    # no conflict, deterministic.
    seam_early = synthetic_registry.rule("syn-temporal-early")
    seam_late = synthetic_registry.rule("syn-temporal-late")
    assert seam_early.is_in_effect("2024-01-01") is False  # effective_to exclusive
    assert seam_late.is_in_effect("2024-01-01") is True    # effective_from inclusive
    assert seam_early.is_in_effect("2023-12-31") is True
    seam = synthetic_registry.detect_conflicts("syn_temporal_far", _SYNTH_INPUTS, "2024-01-01")
    assert seam is None


def test_fh2_disjoint_applicability_never_conflicts(synthetic_registry):
    fam = "syn_disjoint_far"
    # only one of the pair matches any given district -> never a conflict. A
    # district neither rule applies to has no candidates -> also no conflict.
    for district in ("AAA", "BBB", "ZZZ"):
        inputs = {"zoning_district": district, "lot_area_sq_ft": 1}
        assert synthetic_registry.detect_conflicts(fam, inputs) is None


def test_fh2_complementary_different_outputs_never_conflict(synthetic_registry):
    # both apply, both in effect, but they emit DIFFERENT outputs -> not competitors.
    assert synthetic_registry.detect_conflicts("syn_complementary_far", _SYNTH_INPUTS) is None


def test_fh2_cross_family_never_conflicts(synthetic_registry):
    # same output name + same applicability but different families -> per-family
    # detection means each family has a single rule, so neither conflicts.
    assert synthetic_registry.detect_conflicts("syn_crossfam_x_far", _SYNTH_INPUTS) is None
    assert synthetic_registry.detect_conflicts("syn_crossfam_y_far", _SYNTH_INPUTS) is None


def test_fh2_unknown_family_returns_none(synthetic_registry):
    assert synthetic_registry.detect_conflicts("no_such_family", _SYNTH_INPUTS) is None


# ==========================================================================
# FH-2 - integration surfacing (evaluate_property).
# ==========================================================================

def _far_of(result) -> float:
    """The single computed max_synth_far across the evaluated traces (the
    not-in-effect sibling rule appears as a not_applicable trace with no output)."""
    values = [
        trace["outputs"]["max_synth_far"]
        for trace in result.evaluations
        if isinstance(trace, dict) and "max_synth_far" in trace.get("outputs", {})
    ]
    assert len(values) == 1
    return values[0]

def test_fh2_integration_conflict_is_prr_typed_no_value(synthetic_registry):
    result = ri.evaluate_property(_confident_synth_profile("SYNTH"), registry=synthetic_registry)
    assert result.coverage_status == _PRR
    assert result.fail_safe is True
    assert result.fail_safe_reason == ri.FAILSAFE_RULE_CONFLICT
    assert result.professional_review_required is True
    assert result.needs_review is True
    # NO value is produced from the competing rules.
    assert result.evaluations == []
    # typed conflict is surfaced with competing IDs + effective windows.
    conflict = result.rule_conflict
    assert conflict is not None
    assert [r["rule_id"] for r in conflict["competing_rules"]] == [
        "res-far-synth-a",
        "res-far-synth-b",
    ]
    assert all("effective_from" in r and "effective_to" in r for r in conflict["competing_rules"])
    # provenance is preserved (the confident district + its provenance survive).
    assert result.zoning_district == "SYNTH"
    assert result.input_provenance["zoning_district"] == ["prov-spatial"]
    # never Verified; strict-JSON export succeeds.
    payload = result.export()
    assert payload["coverage_status"] != cov.COVERAGE_VERIFIED
    json.dumps(payload, allow_nan=False)


def test_fh2_integration_conflict_is_deterministic(synthetic_registry):
    profile = _confident_synth_profile("SYNTH")
    a = ri.evaluate_property(profile, registry=synthetic_registry).as_dict()
    fresh = RuleRegistry(
        _M4T004 / "rulesets", snapshots=SnapshotStore(_M4T004 / "snapshots")
    ).load()
    b = ri.evaluate_property(profile, registry=fresh).as_dict()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_fh2_integration_as_of_inside_overlap_conflicts(temporal_registry):
    result = ri.evaluate_property(
        _confident_synth_profile("SYNTH"), registry=temporal_registry, as_of_date="2024-03-01"
    )
    assert result.coverage_status == _PRR
    assert result.fail_safe_reason == ri.FAILSAFE_RULE_CONFLICT
    assert result.rule_conflict is not None
    assert result.evaluations == []


@pytest.mark.parametrize("as_of,expected_far", [("2023-06-01", 1.0), ("2024-09-01", 2.0)])
def test_fh2_integration_as_of_outside_overlap_evaluates_normally(
    temporal_registry, as_of, expected_far
):
    # outside the overlap exactly ONE rule is in effect -> normal conditional value,
    # no conflict. Proves as_of_date is genuinely threaded through the integration.
    result = ri.evaluate_property(
        _confident_synth_profile("SYNTH"), registry=temporal_registry, as_of_date=as_of
    )
    assert result.rule_conflict is None
    assert result.fail_safe is False
    assert result.coverage_status == cov.COVERAGE_CONDITIONAL
    assert _far_of(result) == expected_far
    json.dumps(result.export(), allow_nan=False)


def test_fh2_integration_boundary_effective_to_exclusive(temporal_registry):
    # at 2024-06-01 the early rule (effective_to=2024-06-01) is OUT (exclusive) and
    # only the late rule governs -> single value, deterministic, no conflict.
    result = ri.evaluate_property(
        _confident_synth_profile("SYNTH"), registry=temporal_registry, as_of_date="2024-06-01"
    )
    assert result.rule_conflict is None
    assert result.coverage_status == cov.COVERAGE_CONDITIONAL
    assert _far_of(result) == 2.0


def test_fh2_integration_no_as_of_treats_both_in_effect_as_conflict(temporal_registry):
    # as_of_date=None applies no temporal gating: both null-inclusive windows are in
    # effect -> the conflict is surfaced (never a silent pick of one version).
    result = ri.evaluate_property(_confident_synth_profile("SYNTH"), registry=temporal_registry)
    assert result.coverage_status == _PRR
    assert result.fail_safe_reason == ri.FAILSAFE_RULE_CONFLICT


def test_fh2_integration_conflict_never_verified(temporal_registry, synthetic_registry):
    for reg in (temporal_registry, synthetic_registry):
        payload = ri.evaluate_property(_confident_synth_profile("SYNTH"), registry=reg).export()
        assert _no_verified(payload)
        json.dumps(payload, allow_nan=False)


def _no_verified(payload) -> bool:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key == "coverage_status" and value == cov.COVERAGE_VERIFIED:
                return False
            if not _no_verified(value):
                return False
    elif isinstance(payload, list):
        return all(_no_verified(item) for item in payload)
    return True


# ==========================================================================
# Regression - the REAL single-rule R5 family is UNAFFECTED by FH-2.
# ==========================================================================

def test_fh2_real_r5_family_has_no_conflict(registry):
    # the real registry has exactly one residential_far rule; no conflict is ever
    # possible, with or without an as_of_date.
    inputs = {"zoning_district": "R5", "lot_area_sq_ft": 10000}
    assert registry.detect_conflicts("residential_far", inputs) is None
    assert registry.detect_conflicts("residential_far", inputs, "2025-01-01") is None


def test_fh2_real_r5_integration_unchanged_no_conflict_field(registry):
    result = ri.evaluate_property(_real_r5_confident_profile(area=10000.0), registry=registry)
    assert result.rule_conflict is None
    assert result.fail_safe is False
    assert result.coverage_status == cov.COVERAGE_CONDITIONAL
    assert result.zoning_district == "R5"
    assert result.evaluations[0]["outputs"]["max_residential_floor_area_sq_ft"] == 15000.0
    # as_dict now carries the additive rule_conflict key (None on the happy path).
    assert result.as_dict()["rule_conflict"] is None
    json.dumps(result.export(), allow_nan=False)


def test_fh2_real_r5_integration_with_as_of_after_effective_from(registry):
    # threading a valid as_of_date after the R5 effective_from must not change the
    # single-rule outcome (still a conditional value, no conflict).
    result = ri.evaluate_property(
        _real_r5_confident_profile(area=10000.0), registry=registry, as_of_date="2025-06-01"
    )
    assert result.rule_conflict is None
    assert result.coverage_status == cov.COVERAGE_CONDITIONAL
    assert result.evaluations[0]["outputs"]["max_residential_far"] == 1.5
