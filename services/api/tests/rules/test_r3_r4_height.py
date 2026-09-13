"""Acceptance + negative-control pack for the M4-T014 R3/R4-series height
DRAFT rule family (family ``residential_height_setback_r3_r4``).

The family clones the accepted M4-T006 R5 pilot discipline for the districts whose
enumeration the official text settles EXPLICITLY (M4-T012 live verification /
blocker B-023): ZR 23-421 lists the pitched-roof envelope for R1 R2 R3A R3X R3-1
R3-2 R4 R4-1 R4A R5A; ZR 23-422 lists the flat-roof envelope for R3-2 R4 R4B R5
R5B R5D. This wave discharges the R3/R4-series members ONLY:

  r3-r4-pitched-height   23-421  R3A R3X R3-1 R3-2 R4 R4-1 R4A  -> 25 ft perimeter
                                 wall + 35 ft ridge/building (both above base plane),
                                 gated on a pitched building type; sloping-plane
                                 setback = documented-limitation A2 gap.
  r3-2-r4-flat-height    23-422  R3-2 R4 (residences NOT subject to 23-421)
                                 -> 35 ft max building height, gated on a non-pitched
                                 building type.
  r4b-height             23-422  R4B (flat-only, no 23-421 counterpart) -> 25 ft max
                                 building height.

Every value carries its ZR section/clause, amendment date (2024-12-05), and the
snapshot id + content digest. Every rule is needs_review (DRAFT). No AI call
anywhere - pure deterministic evaluation over the committed rule DSL + captured ZR
snapshots.

Cross-SECTION isolation is a first-class concern here (unlike the R5 pilot):
R3-2 and R4 appear in BOTH 23-421 (pitched 25/35) and 23-422 (flat 35), selected by
building type; the tests prove a 23-422 flat value never leaks into a 23-421 pitched
constraint or vice versa, and that R4B's 25 ft flat cap never merges with R3-2/R4's
35 ft flat cap. The R4B pitched-asymmetry (flat-only) is asserted, never symmetrized.

Coverage map:
  AS-1 per-variant confident; separate typed constraints; pitched 25/35 vs flat 35/25
  AS-2 provenance fidelity + citation content-digest binding + tampered snapshot fails closed
  AS-3 effective-date boundary around 2024-12-05 (City of Yes)
  AS-4 determinism (byte-identical export)
  AS-5 never-Verified / draft lifecycle for the whole family
  AS-6 installed-wheel deployability (packaged snapshots + rulesets) + DSL validation
  NC-1 cross-variant isolation (no district borrows another variant's rule)
  NC-2 cross-SECTION isolation (pitched<->flat never conflate; building-type selection)
  NC-3 special-district / commercial-overlay / historic-district context -> PRR
  NC-4 building-type unavailable -> fail closed (PRR)
  NC-5 missing required input -> fail closed (PRR)
  NC-6 uncertain / conflicting geometry -> PRR / data_conflict
  NC-7 no same-family conflict for a dual-section district with a resolved building type
  NC-8 variant/section asymmetry recorded (R4B flat-only; R3A/R3X/R3-1/R4-1/R4A pitched-only)
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from app.rules import coverage as cov
from app.rules.dsl import DSLError, build_rule_definition, load_rule_file
from app.rules.registry import RuleRegistry, detect_rule_conflicts
from app.rules.snapshots import SnapshotError, SnapshotStore

_ENGINE_DIR = Path(__file__).resolve().parents[2] / "app" / "rules"
_REPO_ROOT = Path(__file__).resolve().parents[4]
_RULESET_DIR = Path(RuleRegistry().ruleset_dir)
_DOCS_SNAPSHOT_DIR = _REPO_ROOT / "docs" / "research" / "zr-snapshots" / "v1"
_FAMILY = "residential_height_setback_r3_r4"

_FAMILY_RULE_IDS = ["r3-2-r4-flat-height", "r3-r4-pitched-height", "r4b-height"]

# The pitched envelope governs these R3/R4-series districts (23-421 enumeration,
# R3/R4 members only); each shares the identical 25/35 ft envelope.
_PITCHED_DISTRICTS = ["R3A", "R3X", "R3-1", "R3-2", "R4", "R4-1", "R4A"]
_PITCHED_FORMS = ["detached", "semi_detached", "zero_lot_line"]
_NONPITCHED_FORMS = ["attached", "other"]

_NO_MODIFIERS = {
    "overlay_present": False,
    "special_district_present": False,
    "historic_district": False,
}


def _known_unmodified(rule, **inputs) -> dict:
    """``inputs`` plus an explicit 'no modifier applies' value for every OPTIONAL
    modifier flag THIS rule declares (DF-6: an omitted flag is UNKNOWN, not False)."""
    declared = {spec.name for spec in rule.inputs}
    return {**{k: v for k, v in _NO_MODIFIERS.items() if k in declared}, **inputs}


@pytest.fixture
def registry() -> RuleRegistry:
    return RuleRegistry().load()


@pytest.fixture(scope="module")
def store() -> SnapshotStore:
    return SnapshotStore(_DOCS_SNAPSHOT_DIR).load()


# --------------------------------------------------------------------------
# AS-1 - per-variant confident; separate typed constraints; min/max preserved
# --------------------------------------------------------------------------

@pytest.mark.parametrize("district", _PITCHED_DISTRICTS)
@pytest.mark.parametrize("form", _PITCHED_FORMS)
def test_as1_pitched_confident_wall_and_ridge_separate(registry, district, form):
    res = registry.evaluate(
        "r3-r4-pitched-height",
        _known_unmodified(
            registry.rule("r3-r4-pitched-height"),
            zoning_district=district,
            building_type=form,
        ),
    )
    assert res.coverage_status == cov.COVERAGE_CONDITIONAL
    # Two SEPARATE typed constraints, not one collapsed number.
    assert res.outputs == {"max_perimeter_wall_height": 25.0, "max_building_height": 35.0}
    assert res.trace.rule_status == "needs_review"


def test_as1_flat_r3_2_r4_confident_building_height_only(registry):
    for district in ("R3-2", "R4"):
        res = registry.evaluate(
            "r3-2-r4-flat-height",
            _known_unmodified(
                registry.rule("r3-2-r4-flat-height"),
                zoning_district=district,
                building_type="attached",
            ),
        )
        assert res.coverage_status == cov.COVERAGE_CONDITIONAL
        # Single flat cap; NO base-height/perimeter-wall/setback split invented.
        assert res.outputs == {"max_building_height": 35.0}
        assert "max_base_height" not in res.outputs
        assert "max_perimeter_wall_height" not in res.outputs


def test_as1_r4b_confident_building_height_only(registry):
    res = registry.evaluate(
        "r4b-height",
        _known_unmodified(registry.rule("r4b-height"), zoning_district="R4B"),
    )
    assert res.coverage_status == cov.COVERAGE_CONDITIONAL
    assert res.outputs == {"max_building_height": 25.0}
    assert "max_base_height" not in res.outputs


def test_as1_conditional_never_verified_for_every_variant(registry):
    cases = [
        ("r3-r4-pitched-height", {"zoning_district": "R3A", "building_type": "detached"}),
        ("r3-2-r4-flat-height", {"zoning_district": "R3-2", "building_type": "attached"}),
        ("r4b-height", {"zoning_district": "R4B"}),
    ]
    for rid, inputs in cases:
        res = registry.evaluate(rid, _known_unmodified(registry.rule(rid), **inputs))
        assert res.coverage_status != cov.COVERAGE_VERIFIED
        assert res.trace.rule_release["verified_eligible"] is False


# --------------------------------------------------------------------------
# AS-2 - provenance fidelity; citation digest binding; tampered snapshot fails closed
# --------------------------------------------------------------------------

def test_as2_pitched_dimensions_trace_to_snapshot_provenance(registry):
    res = registry.evaluate(
        "r3-r4-pitched-height",
        _known_unmodified(
            registry.rule("r3-r4-pitched-height"),
            zoning_district="R4", building_type="detached",
        ),
    )
    exported = res.export()  # export() fails closed if any citation lacks provenance
    assert exported["citations"], "no citations on an emitted-value result"
    ids = sorted(c["snapshot_id"] for c in exported["citations"])
    assert ids == ["zr-23-42", "zr-23-421-r3-r4"]
    for cit in exported["citations"]:
        assert cit["section"]
        assert cit["quote"]
        assert cit["last_amended"] == "2024-12-05"
        prov = cit["provenance"]
        assert prov["content_digest_sha256"]
        assert prov["snapshot_id"] == cit["snapshot_id"]


def test_as2_flat_and_r4b_cite_correct_sections(registry):
    flat = registry.evaluate(
        "r3-2-r4-flat-height",
        _known_unmodified(
            registry.rule("r3-2-r4-flat-height"),
            zoning_district="R4", building_type="attached",
        ),
    )
    assert sorted(c["snapshot_id"] for c in flat.trace.citations) == [
        "zr-23-42", "zr-23-422-r3-r4"
    ]
    r4b = registry.evaluate(
        "r4b-height", _known_unmodified(registry.rule("r4b-height"), zoning_district="R4B")
    )
    assert [c["snapshot_id"] for c in r4b.trace.citations] == ["zr-23-422-r3-r4"]


def test_as2_every_recorded_citation_digest_matches_snapshot(store):
    """Each new rule's recorded citation content_digest_sha256 must equal the
    snapshot's stored digest, itself cross-checked as sha256(verbatim_excerpt)."""
    for name in (
        "r3_r4_pitched_height.rule.json",
        "r3_2_r4_flat_height.rule.json",
        "r4b_height.rule.json",
    ):
        doc = json.loads((_RULESET_DIR / name).read_text("utf-8"))
        for cit in doc["citations"]:
            recorded = cit.get("content_digest_sha256")
            assert recorded is not None, f"{name}: citation missing content_digest_sha256"
            snap = store.get(cit["snapshot_id"])
            recomputed = hashlib.sha256(snap.verbatim_excerpt.encode("utf-8")).hexdigest()
            assert snap.content_digest_sha256 == recomputed
            assert recorded == snap.content_digest_sha256


def test_as2_tampered_snapshot_fails_closed(tmp_path):
    store = SnapshotStore().load()
    original = store.get("zr-23-421-r3-r4").raw
    tampered = dict(original)
    tampered["verbatim_excerpt"] = original["verbatim_excerpt"] + " TAMPERED"
    (tmp_path / "zr-23-421-r3-r4.snapshot.json").write_text(
        json.dumps(tampered), encoding="utf-8"
    )
    with pytest.raises(SnapshotError, match="content_digest_sha256 mismatch"):
        SnapshotStore(tmp_path).load()


def test_as2_mismatched_recorded_citation_digest_fails_closed_at_load(store):
    """A rule whose recorded citation digest disagrees with the snapshot refuses
    to load (M4-T010 fail-closed transcription binding)."""
    doc = json.loads((_RULESET_DIR / "r4b_height.rule.json").read_text("utf-8"))
    good = store.get("zr-23-422-r3-r4").content_digest_sha256
    flipped = ("0" if good[0] != "0" else "1") + good[1:]
    doc["citations"][0]["content_digest_sha256"] = flipped
    with pytest.raises(
        DSLError, match=r"records content_digest_sha256 .* but the snapshot on disk stores"
    ):
        build_rule_definition(doc, store)


# --------------------------------------------------------------------------
# AS-3 - effective-date boundary around 2024-12-05 (City of Yes)
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "rid,inputs",
    [
        ("r3-r4-pitched-height", {"zoning_district": "R3A", "building_type": "detached"}),
        ("r3-2-r4-flat-height", {"zoning_district": "R4", "building_type": "attached"}),
        ("r4b-height", {"zoning_district": "R4B"}),
    ],
)
def test_as3_before_amendment_not_effective(registry, rid, inputs):
    res = registry.evaluate(
        rid, _known_unmodified(registry.rule(rid), **inputs), as_of_date="2024-12-04"
    )
    assert res.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert res.outputs == {}
    assert res.trace.effective_window["in_effect"] is False


@pytest.mark.parametrize(
    "rid,inputs",
    [
        ("r3-r4-pitched-height", {"zoning_district": "R3A", "building_type": "detached"}),
        ("r3-2-r4-flat-height", {"zoning_district": "R4", "building_type": "attached"}),
        ("r4b-height", {"zoning_district": "R4B"}),
    ],
)
def test_as3_on_amendment_date_effective(registry, rid, inputs):
    res = registry.evaluate(
        rid, _known_unmodified(registry.rule(rid), **inputs), as_of_date="2024-12-05"
    )
    assert res.coverage_status == cov.COVERAGE_CONDITIONAL
    assert res.outputs
    assert res.trace.effective_window["in_effect"] is True


# --------------------------------------------------------------------------
# AS-4 - determinism (byte-identical export)
# --------------------------------------------------------------------------

def test_as4_determinism_byte_identical(registry):
    inputs = _known_unmodified(
        registry.rule("r3-r4-pitched-height"),
        zoning_district="R4", building_type="detached",
    )
    a = json.dumps(registry.evaluate("r3-r4-pitched-height", inputs).export(), sort_keys=True)
    b = json.dumps(registry.evaluate("r3-r4-pitched-height", inputs).export(), sort_keys=True)
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


def test_as5_no_buildable_or_compliance_language_in_rulesets():
    """No new ruleset labels anything a buildable envelope / feasible building /
    massing / compliance determination (owner directive; D-045-R009)."""
    banned = ["buildable envelope", "feasible", "massing", "compliant", "compliance determination"]
    for name in (
        "r3_r4_pitched_height.rule.json",
        "r3_2_r4_flat_height.rule.json",
        "r4b_height.rule.json",
    ):
        text = (_RULESET_DIR / name).read_text("utf-8").lower()
        for phrase in banned:
            assert phrase not in text, f"{name} contains banned phrase {phrase!r}"


# --------------------------------------------------------------------------
# AS-6 - installed-wheel deployability + DSL validation
# --------------------------------------------------------------------------

def test_as6_family_loads_from_default_packaged_registry():
    reg = RuleRegistry().load()
    for rid in _FAMILY_RULE_IDS:
        assert rid in reg.rule_ids()
    res = reg.evaluate(
        "r4b-height", _known_unmodified(reg.rule("r4b-height"), zoning_district="R4B")
    )
    assert res.outputs == {"max_building_height": 25.0}


def test_as6_every_new_rule_file_validates_via_dsl_loader():
    store = SnapshotStore().load()
    for name in (
        "r3_r4_pitched_height.rule.json",
        "r3_2_r4_flat_height.rule.json",
        "r4b_height.rule.json",
    ):
        rule = load_rule_file(_RULESET_DIR / name, store)  # raises DSLError if invalid
        assert rule.rule_id


# --------------------------------------------------------------------------
# NC-1 - cross-variant isolation (no district borrows another variant's rule)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("foreign", ["R5A", "R4B", "R1", "R2", "R5", "R5B", "R5D", "R3"])
def test_nc1_pitched_rule_not_applicable_to_non_enumerated_districts(registry, foreign):
    res = registry.evaluate(
        "r3-r4-pitched-height",
        _known_unmodified(
            registry.rule("r3-r4-pitched-height"),
            zoning_district=foreign, building_type="detached",
        ),
    )
    assert res.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert res.outputs == {}


@pytest.mark.parametrize("foreign", ["R4B", "R3A", "R3X", "R3-1", "R4-1", "R4A", "R5"])
def test_nc1_flat_rule_scoped_to_r3_2_and_r4_only(registry, foreign):
    res = registry.evaluate(
        "r3-2-r4-flat-height",
        _known_unmodified(
            registry.rule("r3-2-r4-flat-height"),
            zoning_district=foreign, building_type="attached",
        ),
    )
    assert res.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert res.outputs == {}


@pytest.mark.parametrize("foreign", ["R4", "R3-2", "R4A", "R4-1", "R5B"])
def test_nc1_r4b_rule_scoped_to_r4b_only(registry, foreign):
    res = registry.evaluate(
        "r4b-height", _known_unmodified(registry.rule("r4b-height"), zoning_district=foreign)
    )
    assert res.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert res.outputs == {}


def test_nc1_unknown_variant_is_unsupported_not_nearest(registry):
    for rid in ("r3-r4-pitched-height", "r3-2-r4-flat-height", "r4b-height"):
        inputs = {"zoning_district": "R3Z"}
        if rid != "r4b-height":
            inputs["building_type"] = "detached" if rid == "r3-r4-pitched-height" else "attached"
        res = registry.evaluate(rid, _known_unmodified(registry.rule(rid), **inputs))
        assert res.coverage_status == cov.COVERAGE_NOT_APPLICABLE


# --------------------------------------------------------------------------
# NC-2 - cross-SECTION isolation (pitched <-> flat never conflate)
# --------------------------------------------------------------------------

def test_nc2_r4_flat_value_never_leaks_into_pitched_constraint(registry):
    """R4 with a NON-pitched building type gets the 23-422 flat 35 ft building
    height ONLY; it never acquires a 23-421 perimeter-wall / ridge constraint."""
    flat = registry.evaluate(
        "r3-2-r4-flat-height",
        _known_unmodified(
            registry.rule("r3-2-r4-flat-height"),
            zoning_district="R4", building_type="attached",
        ),
    )
    assert flat.outputs == {"max_building_height": 35.0}
    assert "max_perimeter_wall_height" not in flat.outputs
    # ... and the pitched rule does NOT fire for the same non-pitched form.
    pitched = registry.evaluate(
        "r3-r4-pitched-height",
        _known_unmodified(
            registry.rule("r3-r4-pitched-height"),
            zoning_district="R4", building_type="attached",
        ),
    )
    assert pitched.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert pitched.outputs == {}


def test_nc2_r4_pitched_value_never_emitted_by_flat_rule(registry):
    """R4 with a pitched building type gets the 23-421 25/35 ft envelope from the
    pitched rule; the flat rule is not_applicable and emits no 35 ft flat value."""
    pitched = registry.evaluate(
        "r3-r4-pitched-height",
        _known_unmodified(
            registry.rule("r3-r4-pitched-height"),
            zoning_district="R4", building_type="detached",
        ),
    )
    assert pitched.outputs == {"max_perimeter_wall_height": 25.0, "max_building_height": 35.0}
    flat = registry.evaluate(
        "r3-2-r4-flat-height",
        _known_unmodified(
            registry.rule("r3-2-r4-flat-height"),
            zoning_district="R4", building_type="detached",
        ),
    )
    assert flat.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert flat.outputs == {}


def test_nc2_r4b_25_never_merges_with_r3_2_r4_35(registry):
    """R4B's 25 ft flat cap and R3-2/R4's 35 ft flat cap are distinct constraints
    on distinct rules; neither borrows the other's number (mutation-style binding)."""
    r4b = registry.evaluate(
        "r4b-height", _known_unmodified(registry.rule("r4b-height"), zoning_district="R4B")
    )
    assert r4b.outputs == {"max_building_height": 25.0}
    # the R3-2/R4 flat rule does not fire for R4B ...
    flat_r4b = registry.evaluate(
        "r3-2-r4-flat-height",
        _known_unmodified(
            registry.rule("r3-2-r4-flat-height"),
            zoning_district="R4B", building_type="attached",
        ),
    )
    assert flat_r4b.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    # ... and the r4b rule does not fire for R4 (would wrongly cap R4 at 25).
    r4b_on_r4 = registry.evaluate(
        "r4b-height", _known_unmodified(registry.rule("r4b-height"), zoning_district="R4")
    )
    assert r4b_on_r4.coverage_status == cov.COVERAGE_NOT_APPLICABLE


# --------------------------------------------------------------------------
# NC-3 - special-district / commercial-overlay / historic-district context -> PRR
# --------------------------------------------------------------------------

_MODIFIER_FLAGS = ["overlay_present", "special_district_present", "historic_district"]


@pytest.mark.parametrize("flag", _MODIFIER_FLAGS)
def test_nc3_pitched_modifier_downgrades_to_professional_review(registry, flag):
    inputs = _known_unmodified(
        registry.rule("r3-r4-pitched-height"),
        zoning_district="R3A", building_type="detached",
    )
    inputs[flag] = True
    res = registry.evaluate("r3-r4-pitched-height", inputs)
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED


@pytest.mark.parametrize("flag", _MODIFIER_FLAGS)
def test_nc3_flat_modifier_downgrades_to_professional_review(registry, flag):
    inputs = _known_unmodified(
        registry.rule("r3-2-r4-flat-height"),
        zoning_district="R4", building_type="attached",
    )
    inputs[flag] = True
    res = registry.evaluate("r3-2-r4-flat-height", inputs)
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED


def test_nc3_omitted_modifier_flag_is_indeterminate_not_confident(registry):
    """DF-6: an OMITTED optional modifier flag is UNKNOWN, not False; a district
    where a modifier COULD downgrade coverage escalates to professional review
    rather than silently returning the confident envelope."""
    res = registry.evaluate(
        "r3-r4-pitched-height", {"zoning_district": "R3A", "building_type": "detached"}
    )
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED


# --------------------------------------------------------------------------
# NC-4 - building-type unavailable -> fail closed
# --------------------------------------------------------------------------

def test_nc4_pitched_building_type_unavailable_fails_closed(registry):
    res = registry.evaluate("r3-r4-pitched-height", {"zoning_district": "R3A"})
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert res.outputs == {}
    assert res.trace.data_completeness == cov.COMPLETENESS_MISSING_CRITICAL


def test_nc4_flat_building_type_unavailable_fails_closed(registry):
    res = registry.evaluate("r3-2-r4-flat-height", {"zoning_district": "R4"})
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert res.outputs == {}
    assert res.trace.data_completeness == cov.COMPLETENESS_MISSING_CRITICAL


def test_nc4_invalid_building_type_fails_closed(registry):
    res = registry.evaluate(
        "r3-r4-pitched-height",
        {"zoning_district": "R3A", "building_type": "spaceship",
         "overlay_present": False, "special_district_present": False, "historic_district": False},
    )
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert res.outputs == {}
    assert res.trace.input_validation["valid"] is False


# --------------------------------------------------------------------------
# NC-5 - missing required input (district) -> fail closed
# --------------------------------------------------------------------------

def test_nc5_missing_district_fails_closed(registry):
    for rid in _FAMILY_RULE_IDS:
        res = registry.evaluate(rid, {})
        assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
        assert res.outputs == {}
        assert res.trace.data_completeness == cov.COMPLETENESS_MISSING_CRITICAL


# --------------------------------------------------------------------------
# NC-6 - uncertain / conflicting geometry
# --------------------------------------------------------------------------

def test_nc6_conflicting_district_signals_data_conflict(registry):
    res = registry.evaluate(
        "r3-r4-pitched-height",
        _known_unmodified(
            registry.rule("r3-r4-pitched-height"),
            zoning_district="R3A", building_type="detached",
        ),
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
        "r3-2-r4-flat-height",
        _known_unmodified(
            registry.rule("r3-2-r4-flat-height"),
            zoning_district="R4", building_type="attached",
        ),
        spatial_context={
            "lot_overall_class": "multi_district_split",
            "professional_review_required": True,
            "coverage_note": "lot spans multiple districts",
        },
    )
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED


# --------------------------------------------------------------------------
# NC-7 - no same-family conflict for a dual-section district with resolved form
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "district,form",
    [("R4", "detached"), ("R4", "attached"), ("R3-2", "zero_lot_line"), ("R3-2", "other")],
)
def test_nc7_no_conflict_when_building_type_resolves_the_section(registry, district, form):
    inputs = {"zoning_district": district, "building_type": form}
    assert registry.detect_conflicts(_FAMILY, inputs) is None


def test_nc7_conflict_detection_is_order_independent(registry):
    inputs = {"zoning_district": "R4", "building_type": "detached"}
    rules = registry._by_family[_FAMILY]
    a = detect_rule_conflicts(rules, inputs)
    b = detect_rule_conflicts(list(reversed(rules)), inputs)
    assert a == b


# --------------------------------------------------------------------------
# NC-8 - variant/section asymmetry recorded, never symmetrized
# --------------------------------------------------------------------------

def test_nc8_r4b_is_flat_only_no_pitched_envelope(registry):
    """R4B appears ONLY in 23-422; the pitched rule must NOT cover it, and no
    pitched envelope is invented for R4B."""
    res = registry.evaluate(
        "r3-r4-pitched-height",
        _known_unmodified(
            registry.rule("r3-r4-pitched-height"),
            zoning_district="R4B", building_type="detached",
        ),
    )
    assert res.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert res.outputs == {}


@pytest.mark.parametrize("pitched_only", ["R3A", "R3X", "R3-1", "R4-1", "R4A"])
def test_nc8_pitched_only_variants_have_no_flat_envelope(registry, pitched_only):
    """R3A/R3X/R3-1/R4-1/R4A appear ONLY in 23-421; the flat rule must NOT cover
    them (no flat 35 ft cap is invented for a pitched-only district)."""
    res = registry.evaluate(
        "r3-2-r4-flat-height",
        _known_unmodified(
            registry.rule("r3-2-r4-flat-height"),
            zoning_district=pitched_only, building_type="attached",
        ),
    )
    assert res.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert res.outputs == {}


def test_nc8_pitched_setback_is_documented_limitation_not_numeric(registry):
    """The 23-421 sloping-plane setback is an A2 gap surfaced as a documented
    limitation - never a numeric setback output."""
    res = registry.evaluate(
        "r3-r4-pitched-height",
        _known_unmodified(
            registry.rule("r3-r4-pitched-height"),
            zoning_district="R4", building_type="detached",
        ),
    )
    assert "required_setback_depth" not in res.outputs
    assert "setback" not in json.dumps(res.outputs).lower()
    applied = {e["id"]: e for e in res.trace.exceptions_applied}
    assert "pitched_plane_setback_professional_review" in applied
    assert applied["pitched_plane_setback_professional_review"]["effect"] == "documented_limitation"
