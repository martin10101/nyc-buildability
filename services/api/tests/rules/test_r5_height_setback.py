"""Acceptance + negative-control pack for the M4-T006 R5-series height & setback
DRAFT rule family (family ``residential_height_setback``).

The family is encoded PER-DISTRICT (R5 / R5A / R5B / R5D as separate rule files),
with base height, building height, perimeter-wall height, and setback modeled as
SEPARATE typed constraints, all ``needs_review`` and verified-INELIGIBLE. Every
constraint whose applicability turns on an input the canonical property_profile
cannot supply (street-width class, building type, qualifying-residential-site
geography) FAILS CLOSED to ``professional_review_required`` with no value.

No AI call anywhere - this is pure deterministic evaluation over the committed
rule DSL + captured ZR snapshots.

Coverage map:
  AS-1 per-variant confident (min/max preserved; conditional never verified)
  AS-2 provenance fidelity + tampered/absent snapshot fails closed
  AS-3 effective-date boundary (before/after 2024-12-05)
  AS-4 determinism (byte-identical export)
  AS-5 never-Verified / draft lifecycle
  AS-6 installed-wheel deployability (packaged snapshots + rulesets)
  NC-1 district-variant non-inheritance
  NC-2 wide / narrow / UNKNOWN street-width class
  NC-3 special-district / commercial-overlay context
  NC-4 building-type (and ground-floor) unavailable
  NC-5 missing required input
  NC-6 contradictory input (conflicting district signals)
  NC-7 mutually-exclusive rules -> rule_conflict, no selected value
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.rules import coverage as cov
from app.rules.dsl import load_rule_file
from app.rules.registry import RuleRegistry, detect_rule_conflicts
from app.rules.snapshots import SnapshotError, SnapshotStore

_ENGINE_DIR = Path(__file__).resolve().parents[3] / "services" / "api" / "app" / "rules"
# Robust to run location: resolve the ruleset dir via the installed package too.
_RULESET_DIR = Path(RuleRegistry().ruleset_dir)
_FAMILY = "residential_height_setback"

# The six rule ids that make up the family (per-district + the 23-424 alternative).
_FAMILY_RULE_IDS = [
    "r5-height",
    "r5-setback",
    "r5a-height",
    "r5b-height",
    "r5d-height",
    "r5-qrs-height",
]


@pytest.fixture
def registry() -> RuleRegistry:
    """The REAL registry (packaged snapshots + committed rulesets)."""
    return RuleRegistry().load()


# --------------------------------------------------------------------------
# AS-1 - per-variant confident; separate typed constraints; min/max preserved
# --------------------------------------------------------------------------

def test_as1_r5_height_confident_base_and_building_separate(registry):
    res = registry.evaluate("r5-height", {"zoning_district": "R5"})
    assert res.coverage_status == cov.COVERAGE_CONDITIONAL
    # Two SEPARATE typed constraints, not one collapsed number.
    assert res.outputs == {"max_base_height": 35.0, "max_building_height": 45.0}
    assert res.trace.rule_status == "needs_review"
    # The MAX is encoded; the absence of a MINIMUM base height is a documented
    # limitation (never a fabricated zero minimum).
    applied = {e["id"] for e in res.trace.exceptions_applied}
    assert "no_minimum_base_height" in applied


@pytest.mark.parametrize(
    "street_class,expected_depth", [("wide", 10.0), ("narrow", 15.0)]
)
def test_as1_r5_setback_confident_min_depth_by_street(registry, street_class, expected_depth):
    res = registry.evaluate(
        "r5-setback", {"zoning_district": "R5", "street_width_class": street_class}
    )
    assert res.coverage_status == cov.COVERAGE_CONDITIONAL
    assert res.outputs == {"required_setback_depth": expected_depth}


def test_as1_r5a_pitched_confident_wall_and_ridge_separate(registry):
    res = registry.evaluate(
        "r5a-height", {"zoning_district": "R5A", "building_type": "detached"}
    )
    assert res.coverage_status == cov.COVERAGE_CONDITIONAL
    assert res.outputs == {"max_perimeter_wall_height": 25.0, "max_building_height": 35.0}


def test_as1_r5b_confident_building_height_only(registry):
    res = registry.evaluate("r5b-height", {"zoning_district": "R5B"})
    assert res.coverage_status == cov.COVERAGE_CONDITIONAL
    assert res.outputs == {"max_building_height": 35.0}


def test_as1_r5d_confident_building_height_no_setback(registry):
    res = registry.evaluate("r5d-height", {"zoning_district": "R5D"})
    assert res.coverage_status == cov.COVERAGE_CONDITIONAL
    assert res.outputs == {"max_building_height": 45.0}
    # R5D carries no setback rule; its output set is building height only.
    assert "max_base_height" not in res.outputs


def test_as1_conditional_never_verified_for_every_variant(registry):
    cases = [
        ("r5-height", {"zoning_district": "R5"}),
        ("r5-setback", {"zoning_district": "R5", "street_width_class": "wide"}),
        ("r5a-height", {"zoning_district": "R5A", "building_type": "detached"}),
        ("r5b-height", {"zoning_district": "R5B"}),
        ("r5d-height", {"zoning_district": "R5D"}),
    ]
    for rid, inputs in cases:
        res = registry.evaluate(rid, inputs)
        assert res.coverage_status != cov.COVERAGE_VERIFIED
        assert res.trace.rule_release["verified_eligible"] is False


# --------------------------------------------------------------------------
# AS-2 - provenance fidelity; tampered / absent snapshot fails closed
# --------------------------------------------------------------------------

def test_as2_every_emitted_dimension_traces_to_snapshot_provenance(registry):
    res = registry.evaluate("r5-height", {"zoning_district": "R5"})
    exported = res.export()  # export() fails closed if any citation lacks provenance
    assert exported["citations"], "no citations on an emitted-value result"
    for cit in exported["citations"]:
        assert cit["section"]
        assert cit["quote"]
        assert cit["last_amended"] == "2024-12-05"
        prov = cit["provenance"]
        assert prov["content_digest_sha256"]
        assert prov["snapshot_id"] == cit["snapshot_id"]


def test_as2_setback_carries_all_three_citations(registry):
    res = registry.evaluate(
        "r5-setback", {"zoning_district": "R5", "street_width_class": "narrow"}
    )
    ids = sorted(c["snapshot_id"] for c in res.trace.citations)
    assert ids == ["zr-12-10", "zr-23-422", "zr-23-423"]


def test_as2_tampered_snapshot_fails_closed(tmp_path):
    """A snapshot whose stored digest no longer matches its excerpt bytes must
    raise on load - the rule engine can never cite a tampered source."""
    store = SnapshotStore().load()
    original = store.get("zr-23-422").raw
    tampered = dict(original)
    tampered["verbatim_excerpt"] = original["verbatim_excerpt"] + " TAMPERED"
    # keep the OLD content_digest_sha256 -> now stale
    (tmp_path / "zr-23-422.snapshot.json").write_text(
        json.dumps(tampered), encoding="utf-8"
    )
    with pytest.raises(SnapshotError, match="content_digest_sha256 mismatch"):
        SnapshotStore(tmp_path).load()


def test_as2_absent_snapshot_fails_closed():
    """Requesting a snapshot id that does not exist raises rather than
    silently returning nothing."""
    store = SnapshotStore().load()
    with pytest.raises(SnapshotError, match="unknown snapshot_id"):
        store.get("zr-does-not-exist")


# --------------------------------------------------------------------------
# AS-3 - effective-date boundary around 2024-12-05 (City of Yes)
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "rid,inputs",
    [
        ("r5-height", {"zoning_district": "R5"}),
        ("r5-setback", {"zoning_district": "R5", "street_width_class": "wide"}),
        ("r5a-height", {"zoning_district": "R5A", "building_type": "detached"}),
        ("r5b-height", {"zoning_district": "R5B"}),
        ("r5d-height", {"zoning_district": "R5D"}),
    ],
)
def test_as3_before_amendment_not_effective(registry, rid, inputs):
    res = registry.evaluate(rid, inputs, as_of_date="2024-12-04")
    assert res.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert res.outputs == {}
    assert res.trace.effective_window["in_effect"] is False


@pytest.mark.parametrize(
    "rid,inputs",
    [
        ("r5-height", {"zoning_district": "R5"}),
        ("r5-setback", {"zoning_district": "R5", "street_width_class": "wide"}),
        ("r5b-height", {"zoning_district": "R5B"}),
        ("r5d-height", {"zoning_district": "R5D"}),
    ],
)
def test_as3_on_amendment_date_effective(registry, rid, inputs):
    res = registry.evaluate(rid, inputs, as_of_date="2024-12-05")
    assert res.coverage_status == cov.COVERAGE_CONDITIONAL
    assert res.outputs
    assert res.trace.effective_window["in_effect"] is True


# --------------------------------------------------------------------------
# AS-4 - determinism (byte-identical export)
# --------------------------------------------------------------------------

def test_as4_determinism_byte_identical(registry):
    inputs = {"zoning_district": "R5"}
    a = json.dumps(registry.evaluate("r5-height", inputs).export(), sort_keys=True)
    b = json.dumps(registry.evaluate("r5-height", inputs).export(), sort_keys=True)
    assert a == b


# --------------------------------------------------------------------------
# AS-5 - never-Verified / draft lifecycle for the whole family
# --------------------------------------------------------------------------

def test_as5_every_family_rule_is_needs_review_and_verified_ineligible(registry):
    for rid in _FAMILY_RULE_IDS:
        rule = registry.rule(rid)
        assert rule.status == "needs_review"
        assert rule.family == _FAMILY
        assert rule.effective_from == "2024-12-05"
        assert rule.release.get("qualified_human_approval") == "pending"


def test_as5_family_coverage_is_conditional_never_verified(registry):
    fc = registry.family_coverage(_FAMILY)
    assert fc["coverage_status"] == cov.COVERAGE_CONDITIONAL
    assert sorted(fc["rule_ids"]) == sorted(_FAMILY_RULE_IDS)


# --------------------------------------------------------------------------
# AS-6 - installed-wheel deployability (packaged snapshots + rulesets)
# --------------------------------------------------------------------------

def test_as6_family_loads_from_default_packaged_registry():
    """A default RuleRegistry (packaged snapshot store + packaged rulesets, the
    exact resolution an installed wheel uses) loads every family rule and can
    evaluate one to a conditional value. The byte-identity / package-data globs
    are guarded by test_zr_snapshot_bundle + test_installed_deployability."""
    reg = RuleRegistry().load()
    for rid in _FAMILY_RULE_IDS:
        assert rid in reg.rule_ids()
    res = reg.evaluate("r5-height", {"zoning_district": "R5"})
    assert res.outputs == {"max_base_height": 35.0, "max_building_height": 45.0}


def test_as6_every_family_rule_file_validates_via_dsl_loader():
    store = SnapshotStore().load()
    for path in sorted(_RULESET_DIR.glob("*.rule.json")):
        rule = load_rule_file(path, store)  # raises DSLError if invalid
        assert rule.rule_id


# --------------------------------------------------------------------------
# NC-1 - district-variant non-inheritance
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "rid,foreign_district",
    [
        ("r5-height", "R5B"),
        ("r5-height", "R5A"),
        ("r5-height", "R5D"),
        ("r5b-height", "R5"),
        ("r5d-height", "R5"),
        ("r5a-height", "R5"),
    ],
)
def test_nc1_variant_value_not_applied_to_another(registry, rid, foreign_district):
    inputs = {"zoning_district": foreign_district}
    if rid == "r5a-height":
        inputs["building_type"] = "detached"
    res = registry.evaluate(rid, inputs)
    assert res.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert res.outputs == {}


def test_nc1_unknown_r5_variant_is_unsupported_not_nearest(registry):
    # A district that is not exactly an encoded variant is never mapped to the
    # 'nearest' one: no rule applies -> visible not_applicable, no value.
    for rid in ("r5-height", "r5a-height", "r5b-height", "r5d-height"):
        inputs = {"zoning_district": "R5X"}
        if rid == "r5a-height":
            inputs["building_type"] = "detached"
        assert registry.evaluate(rid, inputs).coverage_status == cov.COVERAGE_NOT_APPLICABLE


# --------------------------------------------------------------------------
# NC-2 - wide / narrow / UNKNOWN street-width class
# --------------------------------------------------------------------------

def test_nc2_missing_street_width_fails_closed(registry):
    res = registry.evaluate("r5-setback", {"zoning_district": "R5"})
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert res.outputs == {}
    assert res.trace.data_completeness == cov.COMPLETENESS_MISSING_CRITICAL


def test_nc2_invalid_street_class_fails_closed(registry):
    # An out-of-enum street class (e.g. an un-mapped/guessed value) is rejected
    # fail-closed, never coerced into a depth.
    res = registry.evaluate(
        "r5-setback", {"zoning_district": "R5", "street_width_class": "unknown"}
    )
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert res.outputs == {}
    assert res.trace.input_validation["valid"] is False


# --------------------------------------------------------------------------
# NC-3 - special-district / commercial-overlay context
# --------------------------------------------------------------------------

@pytest.mark.parametrize("flag", ["overlay_present", "special_district_present"])
def test_nc3_overlay_or_special_district_downgrades_never_silent_base(registry, flag):
    res = registry.evaluate("r5-height", {"zoning_district": "R5", flag: True})
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    applied = {e["id"] for e in res.trace.exceptions_applied}
    assert applied & {"commercial_overlay_modification", "special_district_modification"}


def test_nc3_historic_district_downgrades(registry):
    res = registry.evaluate("r5-height", {"zoning_district": "R5", "historic_district": True})
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED


# --------------------------------------------------------------------------
# NC-4 - building-type (and ground-floor) unavailable
# --------------------------------------------------------------------------

def test_nc4_building_type_unavailable_fails_closed(registry):
    res = registry.evaluate("r5a-height", {"zoning_district": "R5A"})
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert res.outputs == {}
    assert res.trace.data_completeness == cov.COMPLETENESS_MISSING_CRITICAL


def test_nc4_qualifying_site_geography_unavailable_fails_closed(registry):
    # The 23-424 alternative envelope's qualifying-residential-site geography is
    # not derivable from the canonical profile -> fail closed, no value.
    res = registry.evaluate("r5-qrs-height", {"zoning_district": "R5"})
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert res.outputs == {}


# --------------------------------------------------------------------------
# NC-5 - missing required input
# --------------------------------------------------------------------------

def test_nc5_missing_district_fails_closed(registry):
    res = registry.evaluate("r5-height", {})
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert res.outputs == {}
    assert res.trace.data_completeness == cov.COMPLETENESS_MISSING_CRITICAL


# --------------------------------------------------------------------------
# NC-6 - contradictory input (conflicting district signals)
# --------------------------------------------------------------------------

def test_nc6_conflicting_district_signals_data_conflict(registry):
    res = registry.evaluate(
        "r5-height",
        {"zoning_district": "R5"},
        spatial_context={
            "lot_overall_class": "data_conflict",
            "professional_review_required": True,
            "coverage_note": "conflicting district assignments for this lot",
        },
    )
    assert res.coverage_status == cov.COVERAGE_DATA_CONFLICT
    assert res.trace.uncertainty["lot_overall_class"] == "data_conflict"


def test_nc6_uncertain_geometry_professional_review(registry):
    res = registry.evaluate(
        "r5-height",
        {"zoning_district": "R5"},
        spatial_context={
            "lot_overall_class": "multi_district_split",
            "professional_review_required": True,
            "coverage_note": "lot spans multiple districts",
        },
    )
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED


# --------------------------------------------------------------------------
# NC-7 - mutually-exclusive rules -> rule_conflict, no selected value
# --------------------------------------------------------------------------

def test_nc7_base_and_qrs_rules_conflict_no_value(registry):
    inputs = {"zoning_district": "R5", "qualifying_residential_site": True}
    conflict = registry.detect_conflicts(_FAMILY, inputs)
    assert conflict is not None
    ids = [r["rule_id"] for r in conflict["competing_rules"]]
    assert ids == ["r5-height", "r5-qrs-height"]  # sorted, deterministic
    assert conflict["competing_output_names"] == ["max_base_height", "max_building_height"]
    # No value is produced from the competing rules.
    assert "value" not in conflict


def test_nc7_conflict_is_order_independent(registry):
    inputs = {"zoning_district": "R5", "qualifying_residential_site": True}
    rules = registry._by_family[_FAMILY]
    a = detect_rule_conflicts(rules, inputs)
    b = detect_rule_conflicts(list(reversed(rules)), inputs)
    assert a == b


def test_nc7_no_conflict_for_ordinary_r5(registry):
    # Without the qualifying-site flag, the alternative rule is not applicable;
    # the base R5 rule governs alone -> no spurious conflict.
    assert registry.detect_conflicts(_FAMILY, {"zoning_district": "R5"}) is None
