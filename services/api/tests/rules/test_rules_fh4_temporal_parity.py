"""FH-4 temporal-parity acceptance pack (task M4-T005 phase 2, scenario AS-9).

Adversarial, deterministic, fully offline. Proves the FH-4 safeguard: an
IMPOSSIBLE calendar ``as_of_date`` (e.g. ``2024-02-30``) fails closed IDENTICALLY
on BOTH temporal paths through the rules engine -

* the conflict-detection path (``registry.detect_rule_conflicts`` /
  ``RuleRegistry.detect_conflicts``), and
* the single-rule evaluate path (``registry.evaluate`` -> ``evaluator.evaluate``),
  and its integration surface ``integration.evaluate_property`` -

using the SAME ``evaluator._valid_iso_date`` calendar validator. A genuine leap
day ``2024-02-29`` still evaluates on both paths (the safeguard is additive and
strictly fail-closed; it never changes legitimate behaviour).

Before FH-4, only the evaluate path validated the date; ``detect_rule_conflicts``
called ``RuleDefinition.is_in_effect`` directly, which does a LEXICAL string
comparison and would treat an impossible date as a real one - so a would-be
conflict could be spuriously reported (or suppressed) on a date that does not
exist. This pack pins the corrected parity.

All rule fixtures are the SYNTHETIC M4-T004 conflict fixtures (two always-in-effect
residential_far rules competing for the same output); the real corpus has a single
R5 rule and can never conflict, so a multi-rule conflict can only be exercised
synthetically. The real R5 family's unchanged behaviour is proven at the end.
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

_FIX = Path(__file__).resolve().parent / "fixtures"
_M4T004 = _FIX / "m4t004"
_R5 = "r5-residential-far"
_FAMILY = "residential_far"
_SYNTH_INPUTS = {"zoning_district": "SYNTH", "lot_area_sq_ft": 10000}
_PRR = cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED

# 2024-02-30 / 2024-04-31 do not exist; 2025-02-29 is Feb 29 in a NON-leap year.
_IMPOSSIBLE_DATES = ["2024-02-30", "2024-04-31", "2025-02-29"]
# Real calendar dates, including a genuine leap day.
_REAL_DATES = ["2024-02-29", "2024-06-15", "2023-01-01"]


@pytest.fixture
def synthetic_registry() -> RuleRegistry:
    """SYNTHETIC registry whose residential_far family holds two always-in-effect
    rules (res-far-synth-a / res-far-synth-b) competing for the same outputs."""
    snaps = SnapshotStore(_M4T004 / "snapshots")
    return RuleRegistry(_M4T004 / "rulesets", snapshots=snaps).load()


@pytest.fixture
def real_registry() -> RuleRegistry:
    """The REAL registry (single R5 residential_far rule)."""
    return RuleRegistry().load()


def _confident_synth_profile(district: str = "SYNTH", *, area: float = 10000.0) -> dict:
    """Minimal contract-shaped profile with one confident base-zoning district
    (the exact keys evaluate_property reads), hand-crafted so this pack stays
    independent of the shapely-heavy app.spatial package."""
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


# ==========================================================================
# The shared validator gates both paths identically.
# ==========================================================================

@pytest.mark.parametrize("impossible", _IMPOSSIBLE_DATES)
def test_as9_shared_validator_rejects_impossible(impossible):
    assert _valid_iso_date(impossible) is False


@pytest.mark.parametrize("real", _REAL_DATES)
def test_as9_shared_validator_accepts_real(real):
    assert _valid_iso_date(real) is True


# ==========================================================================
# AS-9 core parity: impossible date fails closed on BOTH paths identically.
# ==========================================================================

@pytest.mark.parametrize("impossible", _IMPOSSIBLE_DATES)
def test_as9_impossible_date_fails_closed_on_both_paths(synthetic_registry, impossible):
    rules = synthetic_registry._by_family[_FAMILY]

    # Path 1 - conflict detection: an impossible date puts NO rule in effect, so
    # the conflict that exists on a real date is not falsely reported. Both the
    # module function and the registry method fail closed identically.
    assert detect_rule_conflicts(rules, _SYNTH_INPUTS, impossible) is None
    assert synthetic_registry.detect_conflicts(_FAMILY, _SYNTH_INPUTS, impossible) is None

    # Path 2 - single-rule evaluate: the SAME impossible date routes through
    # _valid_iso_date to in_effect=False and a typed invalid_as_of_date, no value.
    for rule in rules:
        result = synthetic_registry.evaluate(rule.rule_id, _SYNTH_INPUTS, as_of_date=impossible)
        assert result.trace.effective_window["in_effect"] is False
        assert result.trace.applicability_outcome is False
        assert result.trace.applicability_trace[0].get("invalid_as_of_date") is True
        assert result.outputs == {}
        json.dumps(result.export(), allow_nan=False)


@pytest.mark.parametrize("real", _REAL_DATES)
def test_as9_real_date_evaluates_on_both_paths(synthetic_registry, real):
    rules = synthetic_registry._by_family[_FAMILY]

    # Path 1: on a real date both always-in-effect rules conflict (parity control:
    # proves it was the impossible date, not the FH-4 code, that suppressed it).
    conflict = detect_rule_conflicts(rules, _SYNTH_INPUTS, real)
    assert conflict is not None and conflict["conflict"] is True

    # Path 2: the same real date is genuinely in effect (no invalid_as_of_date).
    for rule in rules:
        result = synthetic_registry.evaluate(rule.rule_id, _SYNTH_INPUTS, as_of_date=real)
        assert result.trace.effective_window["in_effect"] is True
        assert "invalid_as_of_date" not in result.trace.applicability_trace[0]


# ==========================================================================
# AS-9 integration surface: evaluate_property threads the same fail-closed gate.
# ==========================================================================

@pytest.mark.parametrize("impossible", _IMPOSSIBLE_DATES)
def test_as9_integration_impossible_date_no_spurious_conflict(synthetic_registry, impossible):
    # The conflict that surfaces on a real date is NOT produced on an impossible
    # date: no rule is in effect, so evaluate_property yields a visible
    # not_applicable (no value, no guessed conflict), never a fail-safe conflict.
    result = ri.evaluate_property(
        _confident_synth_profile(), registry=synthetic_registry, as_of_date=impossible
    )
    assert result.rule_conflict is None
    assert result.fail_safe is False
    assert result.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    # Each competing rule was fail-closed on the invalid date.
    assert result.evaluations
    for trace in result.evaluations:
        assert trace["applicability_outcome"] is False
        assert trace["applicability_trace"][0].get("invalid_as_of_date") is True
    json.dumps(result.export(), allow_nan=False)


def test_as9_integration_real_date_surfaces_conflict(synthetic_registry):
    # Control: on a real leap day the conflict IS surfaced (typed, no value).
    result = ri.evaluate_property(
        _confident_synth_profile(), registry=synthetic_registry, as_of_date="2024-02-29"
    )
    assert result.coverage_status == _PRR
    assert result.fail_safe is True
    assert result.fail_safe_reason == ri.FAILSAFE_RULE_CONFLICT
    assert result.rule_conflict is not None
    assert result.evaluations == []


# ==========================================================================
# Determinism + real-family regression.
# ==========================================================================

def test_as9_impossible_date_result_is_deterministic(synthetic_registry):
    profile = _confident_synth_profile()
    a = ri.evaluate_property(
        profile, registry=synthetic_registry, as_of_date="2024-02-30"
    ).as_dict()
    fresh = RuleRegistry(
        _M4T004 / "rulesets", snapshots=SnapshotStore(_M4T004 / "snapshots")
    ).load()
    b = ri.evaluate_property(profile, registry=fresh, as_of_date="2024-02-30").as_dict()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


@pytest.mark.parametrize("impossible", _IMPOSSIBLE_DATES)
def test_as9_real_r5_family_impossible_date_still_fails_closed(real_registry, impossible):
    # The real single-rule R5 family can never conflict; an impossible date on the
    # detect path is a no-op (None) and the evaluate path fails closed with no value.
    inputs = {"zoning_district": "R5", "lot_area_sq_ft": 10000, "site_class": "standard_zoning_lot"}
    assert real_registry.detect_conflicts(_FAMILY, inputs, impossible) is None
    result = real_registry.evaluate(_R5, inputs, as_of_date=impossible)
    assert result.coverage_status == _PRR
    assert result.trace.effective_window["in_effect"] is False
    assert result.outputs == {}
