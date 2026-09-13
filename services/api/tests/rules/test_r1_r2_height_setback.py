"""Acceptance + negative-control pack for the M4-T012 R1/R2-series height/setback
DRAFT rule family (family ``residential_height_setback_r1_r2``), encoded per the
D-049 definitive rescope (owner decision, 2026-09-13: "encode the 11-25
reading").

The family clones the accepted M4-T006/M4-T014 pilot discipline for four rules:

  r1-r2-bare-pitched-height             23-421  bare R1/R2 (express citation)
                                         -> 25 ft perimeter wall + 35 ft ridge
                                         (both above base plane), gated on a
                                         pitched building type.
  r1-r2-suffix-variants-pitched-height  11-25 + 23-421  R1-1 R1-2 R1-2A R2A R2X
                                         (OWNER-DECISION suffix inheritance,
                                         D-049) -> the SAME 25/35 envelope.
  r1-r2-reference-plane-23421g          23-421(g)  R1-1 R1-2 R2 (no letter
                                         suffix) -> conditional 5 ft reference-
                                         plane elevation allowance, triggered by
                                         (area>=9500 AND width>=100) OR slope>=5.
  r1-r2-qrs-height                      23-424  R1-1 R1-2 R1-2A R2 R2A R2X on a
                                         qualifying residential site -> 35/35 ft
                                         alternative envelope, competing with the
                                         base envelope rules for max_building_height.

Every value carries its ZR section/clause, amendment date (2024-12-05, or
1994-06-29 for 11-25), and the snapshot id + content digest. Every rule is
needs_review (DRAFT). No AI call anywhere - pure deterministic evaluation over
the committed rule DSL + captured ZR snapshots (captured via the official
print/PDF channel per the M4-T012 binding capture-completeness requirement).

Coverage map:
  AS-1 per-variant confident; separate typed constraints; express vs owner-decision provenance
  AS-2 provenance fidelity + citation content-digest binding + tampered snapshot fails closed
  AS-3 effective-date boundary (2024-12-05 for 23-421/23-424; 1994-06-29 for 11-25 is NOT the
       gating date - the citing rules' own effective_from governs, per M4-T003 temporal design)
  AS-4 determinism (byte-identical export)
  AS-5 never-Verified / draft lifecycle for the whole family + no compliance language
  AS-6 installed-wheel deployability + DSL validation
  NC-1 cross-variant isolation (no district borrows another variant's rule)
  NC-2 letter-suffix exclusion from section 23-421(g) (R1-2A/R2A/R2X never get the allowance)
  NC-3 special-district / commercial-overlay / historic-district / large-site /
       transportation context -> PRR
  NC-4 building-type unavailable -> fail closed (PRR)
  NC-5 missing required input -> fail closed (PRR), including the (g) rule's 3 geometry inputs
  NC-6 uncertain / conflicting geometry -> PRR / data_conflict
  NC-7 same-family conflict: QRS alternative vs base envelope for max_building_height
  NC-8 (g) trigger boundary: area+width path, slope path, neither path,
       conservative all-required design
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

_REPO_ROOT = Path(__file__).resolve().parents[4]
_RULESET_DIR = Path(RuleRegistry().ruleset_dir)
_DOCS_SNAPSHOT_DIR = _REPO_ROOT / "docs" / "research" / "zr-snapshots" / "v1"
_FAMILY = "residential_height_setback_r1_r2"

_FAMILY_RULE_IDS = [
    "r1-r2-bare-pitched-height",
    "r1-r2-suffix-variants-pitched-height",
    "r1-r2-reference-plane-23421g",
    "r1-r2-qrs-height",
]

_RULE_FILES = [
    "r1_r2_bare_pitched_height.rule.json",
    "r1_r2_suffix_variants_pitched_height.rule.json",
    "r1_r2_reference_plane_23421g.rule.json",
    "r1_r2_qrs_height.rule.json",
]

_PITCHED_FORMS = ["detached", "semi_detached", "zero_lot_line"]
_NONPITCHED_FORMS = ["attached", "other"]

_ENVELOPE_NO_MODIFIERS = {
    "overlay_present": False,
    "special_district_present": False,
    "historic_district": False,
    "large_site": False,
    "transportation_infrastructure_adjacent": False,
}

_QRS_NO_MODIFIERS = {
    "overlay_present": False,
    "special_district_present": False,
}


def _known_unmodified(rule, base: dict, **inputs) -> dict:
    """``inputs`` plus an explicit 'no modifier applies' value for every OPTIONAL
    modifier flag THIS rule declares (DF-6: an omitted flag is UNKNOWN, not False)."""
    declared = {spec.name for spec in rule.inputs}
    return {**{k: v for k, v in base.items() if k in declared}, **inputs}


def _envelope_inputs(rule, **inputs) -> dict:
    return _known_unmodified(rule, _ENVELOPE_NO_MODIFIERS, **inputs)


def _qrs_inputs(rule, **inputs) -> dict:
    return _known_unmodified(rule, _QRS_NO_MODIFIERS, **inputs)


@pytest.fixture
def registry() -> RuleRegistry:
    return RuleRegistry().load()


@pytest.fixture(scope="module")
def store() -> SnapshotStore:
    return SnapshotStore(_DOCS_SNAPSHOT_DIR).load()


# --------------------------------------------------------------------------
# AS-1 - per-variant confident; separate typed constraints; express vs owner-decision
# --------------------------------------------------------------------------

@pytest.mark.parametrize("district", ["R1", "R2"])
@pytest.mark.parametrize("form", _PITCHED_FORMS)
def test_as1_bare_confident_wall_and_ridge_separate(registry, district, form):
    rule = registry.rule("r1-r2-bare-pitched-height")
    res = registry.evaluate(
        "r1-r2-bare-pitched-height",
        _envelope_inputs(rule, zoning_district=district, building_type=form),
    )
    assert res.coverage_status == cov.COVERAGE_CONDITIONAL
    assert res.outputs == {"max_perimeter_wall_height": 25.0, "max_building_height": 35.0}
    assert res.trace.rule_status == "needs_review"


@pytest.mark.parametrize("district", ["R1-1", "R1-2", "R1-2A", "R2A", "R2X"])
@pytest.mark.parametrize("form", _PITCHED_FORMS)
def test_as1_suffix_variant_confident_wall_and_ridge_separate(registry, district, form):
    rule = registry.rule("r1-r2-suffix-variants-pitched-height")
    res = registry.evaluate(
        "r1-r2-suffix-variants-pitched-height",
        _envelope_inputs(rule, zoning_district=district, building_type=form),
    )
    assert res.coverage_status == cov.COVERAGE_CONDITIONAL
    # SAME envelope as the bare-label rule, obtained via 11-25 suffix inheritance.
    assert res.outputs == {"max_perimeter_wall_height": 25.0, "max_building_height": 35.0}


def test_as1_bare_and_suffix_rules_cite_distinct_provenance(registry):
    """The bare rule's citation is EXPRESS ONLY (23-421); the suffix rule ALSO
    cites 11-25 (owner-decision provenance), never presenting the extension as
    an express per-variant citation."""
    bare = registry.rule("r1-r2-bare-pitched-height")
    suffix = registry.rule("r1-r2-suffix-variants-pitched-height")
    bare_ids = {c.snapshot_id for c in bare.citations}
    suffix_ids = {c.snapshot_id for c in suffix.citations}
    assert "zr-11-25" not in bare_ids
    assert "zr-11-25" in suffix_ids
    assert "zr-23-421-r1-r2" in bare_ids
    assert "zr-23-421-r1-r2" in suffix_ids


def test_as1_r2x_far_row_documented_as_floor_area_only(registry):
    """D-049-R002: R2X's distinct 23-21 FAR row is a floor-area-only exception
    and does NOT modify the height envelope; the height value is IDENTICAL to
    R2A/R1-2A, and the FAR distinction is surfaced as a documented limitation."""
    rule = registry.rule("r1-r2-suffix-variants-pitched-height")
    res = registry.evaluate(
        "r1-r2-suffix-variants-pitched-height",
        _envelope_inputs(rule, zoning_district="R2X", building_type="detached"),
    )
    assert res.outputs == {"max_perimeter_wall_height": 25.0, "max_building_height": 35.0}
    applied = {e["id"]: e for e in res.trace.exceptions_applied}
    assert "r2x_far_row_is_floor_area_only" in applied
    assert applied["r2x_far_row_is_floor_area_only"]["effect"] == "documented_limitation"
    # A non-R2X variant does NOT carry the R2X-specific note.
    other = registry.evaluate(
        "r1-r2-suffix-variants-pitched-height",
        _envelope_inputs(rule, zoning_district="R2A", building_type="detached"),
    )
    assert "r2x_far_row_is_floor_area_only" not in {
        e["id"] for e in other.trace.exceptions_applied
    }


def test_as1_reference_plane_g_confident_when_area_and_width_satisfy(registry):
    res = registry.evaluate(
        "r1-r2-reference-plane-23421g",
        {
            "zoning_district": "R1-1", "building_type": "detached",
            "lot_area_sqft": 10000, "lot_width_ft": 120, "rear_wall_slope_percent": 0,
        },
    )
    assert res.coverage_status == cov.COVERAGE_CONDITIONAL
    assert res.outputs == {"reference_plane_elevation_max_ft": 5.0}


def test_as1_reference_plane_g_confident_when_slope_satisfies(registry):
    res = registry.evaluate(
        "r1-r2-reference-plane-23421g",
        {
            "zoning_district": "R2", "building_type": "zero_lot_line",
            "lot_area_sqft": 1000, "lot_width_ft": 20, "rear_wall_slope_percent": 5,
        },
    )
    assert res.coverage_status == cov.COVERAGE_CONDITIONAL
    assert res.outputs == {"reference_plane_elevation_max_ft": 5.0}


def test_as1_qrs_confident_base_and_building_height(registry):
    rule = registry.rule("r1-r2-qrs-height")
    res = registry.evaluate(
        "r1-r2-qrs-height",
        _qrs_inputs(rule, zoning_district="R2", qualifying_residential_site=True),
    )
    assert res.coverage_status == cov.COVERAGE_CONDITIONAL
    assert res.outputs == {"max_base_height": 35.0, "max_building_height": 35.0}


def test_as1_conditional_never_verified_for_every_rule(registry):
    cases = [
        ("r1-r2-bare-pitched-height", {"zoning_district": "R1", "building_type": "detached"}),
        (
            "r1-r2-suffix-variants-pitched-height",
            {"zoning_district": "R1-2A", "building_type": "detached"},
        ),
        (
            "r1-r2-reference-plane-23421g",
            {
                "zoning_district": "R1-1", "building_type": "detached",
                "lot_area_sqft": 10000, "lot_width_ft": 120, "rear_wall_slope_percent": 0,
            },
        ),
        ("r1-r2-qrs-height", {"zoning_district": "R2", "qualifying_residential_site": True}),
    ]
    for rid, inputs in cases:
        rule = registry.rule(rid)
        full = (
            _envelope_inputs(rule, **inputs)
            if rid != "r1-r2-qrs-height"
            else _qrs_inputs(rule, **inputs)
        )
        if rid == "r1-r2-reference-plane-23421g":
            full = inputs
        res = registry.evaluate(rid, full)
        assert res.coverage_status != cov.COVERAGE_VERIFIED
        assert res.trace.rule_release["verified_eligible"] is False


# --------------------------------------------------------------------------
# AS-2 - provenance fidelity; citation digest binding; tampered snapshot fails closed
# --------------------------------------------------------------------------

def test_as2_every_recorded_citation_digest_matches_snapshot(store):
    for name in _RULE_FILES:
        doc = json.loads((_RULESET_DIR / name).read_text("utf-8"))
        for cit in doc["citations"]:
            recorded = cit.get("content_digest_sha256")
            if recorded is None:
                continue  # optional field; zr-23-423 citation in the QRS rule omits it
            snap = store.get(cit["snapshot_id"])
            recomputed = hashlib.sha256(snap.verbatim_excerpt.encode("utf-8")).hexdigest()
            assert snap.content_digest_sha256 == recomputed
            assert recorded == snap.content_digest_sha256


def test_as2_tampered_reference_plane_snapshot_fails_closed(tmp_path):
    store = SnapshotStore().load()
    original = store.get("zr-23-421-g").raw
    tampered = dict(original)
    tampered["verbatim_excerpt"] = original["verbatim_excerpt"] + " TAMPERED"
    (tmp_path / "zr-23-421-g.snapshot.json").write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(SnapshotError, match="content_digest_sha256 mismatch"):
        SnapshotStore(tmp_path).load()


def test_as2_mismatched_recorded_citation_digest_fails_closed_at_load(store):
    doc = json.loads((_RULESET_DIR / "r1_r2_reference_plane_23421g.rule.json").read_text("utf-8"))
    good = store.get("zr-23-421-g").content_digest_sha256
    flipped = ("0" if good[0] != "0" else "1") + good[1:]
    doc["citations"][0]["content_digest_sha256"] = flipped
    with pytest.raises(
        DSLError, match=r"records content_digest_sha256 .* but the snapshot on disk stores"
    ):
        build_rule_definition(doc, store)


def test_as2_11_25_snapshot_last_amended_predates_city_of_yes(store):
    """ZR 11-25 is a general Resolution-interpretation rule last amended
    1994-06-29 (long before City of Yes, 2024-12-05); the citing rule's OWN
    effective_from (2024-12-05, matching 23-421) governs temporal gating -
    11-25's much older amendment date does not make the rule effective earlier."""
    snap = store.get("zr-11-25")
    assert snap.section_last_amended == "1994-06-29"
    rule = RuleRegistry().load().rule("r1-r2-suffix-variants-pitched-height")
    assert rule.effective_from == "2024-12-05"


# --------------------------------------------------------------------------
# AS-3 - effective-date boundary around 2024-12-05 (City of Yes)
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "rid,inputs",
    [
        ("r1-r2-bare-pitched-height", {"zoning_district": "R1", "building_type": "detached"}),
        (
            "r1-r2-suffix-variants-pitched-height",
            {"zoning_district": "R2X", "building_type": "detached"},
        ),
        ("r1-r2-qrs-height", {"zoning_district": "R2", "qualifying_residential_site": True}),
        (
            "r1-r2-reference-plane-23421g",
            {
                "zoning_district": "R1-1", "building_type": "detached",
                "lot_area_sqft": 50000, "lot_width_ft": 500, "rear_wall_slope_percent": 50,
            },
        ),
    ],
)
def test_as3_before_amendment_not_effective(registry, rid, inputs):
    rule = registry.rule(rid)
    full = (
        _qrs_inputs(rule, **inputs)
        if rid == "r1-r2-qrs-height"
        else _envelope_inputs(rule, **inputs)
    )
    res = registry.evaluate(rid, full, as_of_date="2024-12-04")
    assert res.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert res.outputs == {}
    assert res.trace.effective_window["in_effect"] is False


@pytest.mark.parametrize(
    "rid,inputs",
    [
        ("r1-r2-bare-pitched-height", {"zoning_district": "R1", "building_type": "detached"}),
        (
            "r1-r2-suffix-variants-pitched-height",
            {"zoning_district": "R2X", "building_type": "detached"},
        ),
        ("r1-r2-qrs-height", {"zoning_district": "R2", "qualifying_residential_site": True}),
        (
            "r1-r2-reference-plane-23421g",
            {
                "zoning_district": "R1-1", "building_type": "detached",
                "lot_area_sqft": 50000, "lot_width_ft": 500, "rear_wall_slope_percent": 50,
            },
        ),
    ],
)
def test_as3_on_amendment_date_effective(registry, rid, inputs):
    rule = registry.rule(rid)
    full = (
        _qrs_inputs(rule, **inputs)
        if rid == "r1-r2-qrs-height"
        else _envelope_inputs(rule, **inputs)
    )
    res = registry.evaluate(rid, full, as_of_date="2024-12-05")
    assert res.coverage_status == cov.COVERAGE_CONDITIONAL
    assert res.outputs
    assert res.trace.effective_window["in_effect"] is True


# --------------------------------------------------------------------------
# AS-4 - determinism (byte-identical export)
# --------------------------------------------------------------------------

def test_as4_determinism_byte_identical(registry):
    rule = registry.rule("r1-r2-suffix-variants-pitched-height")
    inputs = _envelope_inputs(rule, zoning_district="R2X", building_type="detached")
    a = json.dumps(
        registry.evaluate("r1-r2-suffix-variants-pitched-height", inputs).export(), sort_keys=True
    )
    b = json.dumps(
        registry.evaluate("r1-r2-suffix-variants-pitched-height", inputs).export(), sort_keys=True
    )
    assert a == b


# --------------------------------------------------------------------------
# AS-5 - never-Verified / draft lifecycle for the whole family + language guard
# --------------------------------------------------------------------------

def test_as5_every_family_rule_is_needs_review(registry):
    for rid in _FAMILY_RULE_IDS:
        rule = registry.rule(rid)
        assert rule.status == "needs_review"
        assert rule.family == _FAMILY
        assert rule.release.get("qualified_human_approval") == "pending"


def test_as5_family_coverage_is_conditional_never_verified(registry):
    fc = registry.family_coverage(_FAMILY)
    assert fc["coverage_status"] == cov.COVERAGE_CONDITIONAL
    assert sorted(fc["rule_ids"]) == sorted(_FAMILY_RULE_IDS)


def test_as5_no_buildable_or_compliance_language_in_rulesets():
    banned = ["buildable envelope", "feasible", "massing", "compliant", "compliance determination"]
    for name in _RULE_FILES:
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
        "r1-r2-bare-pitched-height",
        _envelope_inputs(
            reg.rule("r1-r2-bare-pitched-height"), zoning_district="R2", building_type="detached"
        ),
    )
    assert res.outputs == {"max_perimeter_wall_height": 25.0, "max_building_height": 35.0}


def test_as6_every_new_rule_file_validates_via_dsl_loader():
    store = SnapshotStore().load()
    for name in _RULE_FILES:
        rule = load_rule_file(_RULESET_DIR / name, store)
        assert rule.rule_id


# --------------------------------------------------------------------------
# NC-1 - cross-variant isolation (no district borrows another variant's rule)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("foreign", ["R1-1", "R1-2", "R1-2A", "R2A", "R2X", "R3A", "R5"])
def test_nc1_bare_rule_scoped_to_bare_labels_only(registry, foreign):
    rule = registry.rule("r1-r2-bare-pitched-height")
    res = registry.evaluate(
        "r1-r2-bare-pitched-height",
        _envelope_inputs(rule, zoning_district=foreign, building_type="detached"),
    )
    assert res.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert res.outputs == {}


@pytest.mark.parametrize("foreign", ["R1", "R2", "R3A", "R3X", "R4", "R5"])
def test_nc1_suffix_variant_rule_never_matches_bare_or_foreign(registry, foreign):
    rule = registry.rule("r1-r2-suffix-variants-pitched-height")
    res = registry.evaluate(
        "r1-r2-suffix-variants-pitched-height",
        _envelope_inputs(rule, zoning_district=foreign, building_type="detached"),
    )
    assert res.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert res.outputs == {}


def test_nc1_unknown_variant_is_unsupported_not_nearest(registry):
    for rid in ("r1-r2-bare-pitched-height", "r1-r2-suffix-variants-pitched-height"):
        rule = registry.rule(rid)
        res = registry.evaluate(
            rid, _envelope_inputs(rule, zoning_district="R2Z", building_type="detached")
        )
        assert res.coverage_status == cov.COVERAGE_NOT_APPLICABLE


@pytest.mark.parametrize("foreign", ["R3A", "R3X", "R4", "R5"])
def test_nc1_qrs_rule_never_matches_foreign_districts(registry, foreign):
    """G4 rework advisory: pin the QRS rule's in_set so a future broadening of its
    district scope is a visible, test-caught change."""
    rule = registry.rule("r1-r2-qrs-height")
    res = registry.evaluate(
        "r1-r2-qrs-height",
        _qrs_inputs(rule, zoning_district=foreign, qualifying_residential_site=True),
    )
    assert res.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert res.outputs == {}


@pytest.mark.parametrize("foreign", ["R3A", "R3X", "R4", "R5"])
def test_nc1_reference_plane_rule_never_matches_foreign_districts(registry, foreign):
    """G4 rework advisory: pin the (g) rule's in_set against foreign districts even
    with fully-satisfying geometry (NC-2 covers the excluded R1/R2-family members)."""
    res = registry.evaluate(
        "r1-r2-reference-plane-23421g",
        {
            "zoning_district": foreign, "building_type": "detached",
            "lot_area_sqft": 50000, "lot_width_ft": 500, "rear_wall_slope_percent": 50,
        },
    )
    assert res.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert res.outputs == {}


# --------------------------------------------------------------------------
# NC-2 - letter-suffix exclusion from section 23-421(g)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("excluded", ["R1-2A", "R2A", "R2X", "R1"])
def test_nc2_letter_suffix_and_bare_r1_excluded_from_reference_plane(registry, excluded):
    """R1-2A, R2A, R2X (letter suffixes) and bare 'R1' are NOT eligible for the
    section 23-421(g) allowance, even with a fully-satisfying geometry trigger."""
    res = registry.evaluate(
        "r1-r2-reference-plane-23421g",
        {
            "zoning_district": excluded, "building_type": "detached",
            "lot_area_sqft": 50000, "lot_width_ft": 500, "rear_wall_slope_percent": 50,
        },
    )
    assert res.coverage_status == cov.COVERAGE_NOT_APPLICABLE
    assert res.outputs == {}


@pytest.mark.parametrize("eligible", ["R1-1", "R1-2", "R2"])
def test_nc2_no_letter_suffix_members_eligible(registry, eligible):
    res = registry.evaluate(
        "r1-r2-reference-plane-23421g",
        {
            "zoning_district": eligible, "building_type": "detached",
            "lot_area_sqft": 50000, "lot_width_ft": 500, "rear_wall_slope_percent": 50,
        },
    )
    assert res.coverage_status == cov.COVERAGE_CONDITIONAL
    assert res.outputs == {"reference_plane_elevation_max_ft": 5.0}


# --------------------------------------------------------------------------
# NC-3 - special-district / commercial-overlay / historic / large-site / transportation -> PRR
# --------------------------------------------------------------------------

_ENVELOPE_MODIFIER_FLAGS = [
    "overlay_present", "special_district_present", "historic_district",
    "large_site", "transportation_infrastructure_adjacent",
]


@pytest.mark.parametrize("flag", _ENVELOPE_MODIFIER_FLAGS)
def test_nc3_bare_rule_modifier_downgrades(registry, flag):
    rule = registry.rule("r1-r2-bare-pitched-height")
    inputs = _envelope_inputs(rule, zoning_district="R2", building_type="detached")
    inputs[flag] = True
    res = registry.evaluate("r1-r2-bare-pitched-height", inputs)
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED


@pytest.mark.parametrize("flag", _ENVELOPE_MODIFIER_FLAGS)
def test_nc3_suffix_variant_rule_modifier_downgrades(registry, flag):
    rule = registry.rule("r1-r2-suffix-variants-pitched-height")
    inputs = _envelope_inputs(rule, zoning_district="R2A", building_type="detached")
    inputs[flag] = True
    res = registry.evaluate("r1-r2-suffix-variants-pitched-height", inputs)
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED


def test_nc3_omitted_modifier_flag_is_indeterminate_not_confident(registry):
    """DF-6: an OMITTED optional modifier flag is UNKNOWN, not False."""
    res = registry.evaluate(
        "r1-r2-bare-pitched-height", {"zoning_district": "R1", "building_type": "detached"}
    )
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED


@pytest.mark.parametrize("flag", ["overlay_present", "special_district_present"])
def test_nc3_qrs_modifier_downgrades(registry, flag):
    rule = registry.rule("r1-r2-qrs-height")
    inputs = _qrs_inputs(rule, zoning_district="R2", qualifying_residential_site=True)
    inputs[flag] = True
    res = registry.evaluate("r1-r2-qrs-height", inputs)
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED


# --------------------------------------------------------------------------
# NC-4 - building-type unavailable -> fail closed
# --------------------------------------------------------------------------

def test_nc4_bare_building_type_unavailable_fails_closed(registry):
    res = registry.evaluate("r1-r2-bare-pitched-height", {"zoning_district": "R1"})
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert res.outputs == {}
    assert res.trace.data_completeness == cov.COMPLETENESS_MISSING_CRITICAL


def test_nc4_suffix_variant_building_type_unavailable_fails_closed(registry):
    res = registry.evaluate(
        "r1-r2-suffix-variants-pitched-height", {"zoning_district": "R2X"}
    )
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert res.outputs == {}


def test_nc4_reference_plane_building_type_unavailable_fails_closed(registry):
    res = registry.evaluate(
        "r1-r2-reference-plane-23421g",
        {
            "zoning_district": "R1-1", "lot_area_sqft": 10000,
            "lot_width_ft": 120, "rear_wall_slope_percent": 0,
        },
    )
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert res.outputs == {}


def test_nc4_invalid_building_type_fails_closed(registry):
    res = registry.evaluate(
        "r1-r2-bare-pitched-height",
        {
            "zoning_district": "R1", "building_type": "spaceship",
            **_ENVELOPE_NO_MODIFIERS,
        },
    )
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert res.outputs == {}
    assert res.trace.input_validation["valid"] is False


# --------------------------------------------------------------------------
# NC-5 - missing required input -> fail closed
# --------------------------------------------------------------------------

def test_nc5_missing_district_fails_closed(registry):
    for rid in _FAMILY_RULE_IDS:
        res = registry.evaluate(rid, {})
        assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
        assert res.outputs == {}
        assert res.trace.data_completeness == cov.COMPLETENESS_MISSING_CRITICAL


@pytest.mark.parametrize(
    "missing_field",
    ["lot_area_sqft", "lot_width_ft", "rear_wall_slope_percent"],
)
def test_nc5_reference_plane_missing_any_single_geometry_input_fails_closed(
    registry, missing_field
):
    """NC-8 conservative-by-design: even ONE missing geometry input fails closed,
    regardless of whether the OTHER two would already resolve the trigger."""
    full = {
        "zoning_district": "R1-1", "building_type": "detached",
        "lot_area_sqft": 50000, "lot_width_ft": 500, "rear_wall_slope_percent": 50,
    }
    del full[missing_field]
    res = registry.evaluate("r1-r2-reference-plane-23421g", full)
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert res.outputs == {}
    assert res.trace.data_completeness == cov.COMPLETENESS_MISSING_CRITICAL


def test_nc5_qrs_missing_qualifying_flag_fails_closed(registry):
    res = registry.evaluate(
        "r1-r2-qrs-height",
        {"zoning_district": "R2", "overlay_present": False, "special_district_present": False},
    )
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert res.outputs == {}


# --------------------------------------------------------------------------
# NC-6 - uncertain / conflicting geometry
# --------------------------------------------------------------------------

def test_nc6_conflicting_district_signals_data_conflict(registry):
    rule = registry.rule("r1-r2-bare-pitched-height")
    res = registry.evaluate(
        "r1-r2-bare-pitched-height",
        _envelope_inputs(rule, zoning_district="R1", building_type="detached"),
        spatial_context={
            "lot_overall_class": "data_conflict",
            "professional_review_required": True,
            "coverage_note": "conflicting district assignments for this lot",
        },
    )
    assert res.coverage_status == cov.COVERAGE_DATA_CONFLICT
    assert res.trace.uncertainty["lot_overall_class"] == "data_conflict"


def test_nc6_uncertain_geometry_professional_review(registry):
    rule = registry.rule("r1-r2-suffix-variants-pitched-height")
    res = registry.evaluate(
        "r1-r2-suffix-variants-pitched-height",
        _envelope_inputs(rule, zoning_district="R2X", building_type="detached"),
        spatial_context={
            "lot_overall_class": "multi_district_split",
            "professional_review_required": True,
            "coverage_note": "lot spans multiple districts",
        },
    )
    assert res.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED


# --------------------------------------------------------------------------
# NC-7 - same-family conflict: QRS alternative vs base envelope
# --------------------------------------------------------------------------

def test_nc7_qrs_and_suffix_variant_rules_conflict_no_value(registry):
    inputs = {
        "zoning_district": "R2X", "building_type": "detached",
        "qualifying_residential_site": True,
    }
    conflict = registry.detect_conflicts(_FAMILY, inputs)
    assert conflict is not None
    ids = [r["rule_id"] for r in conflict["competing_rules"]]
    assert ids == ["r1-r2-qrs-height", "r1-r2-suffix-variants-pitched-height"]
    assert conflict["competing_output_names"] == ["max_building_height"]
    assert "value" not in conflict


def test_nc7_qrs_and_bare_rule_conflict_no_value(registry):
    inputs = {
        "zoning_district": "R2", "building_type": "detached",
        "qualifying_residential_site": True,
    }
    conflict = registry.detect_conflicts(_FAMILY, inputs)
    assert conflict is not None
    ids = [r["rule_id"] for r in conflict["competing_rules"]]
    assert ids == ["r1-r2-bare-pitched-height", "r1-r2-qrs-height"]


def test_nc7_conflict_is_order_independent(registry):
    inputs = {
        "zoning_district": "R2X", "building_type": "detached",
        "qualifying_residential_site": True,
    }
    rules = registry._by_family[_FAMILY]
    a = detect_rule_conflicts(rules, inputs)
    b = detect_rule_conflicts(list(reversed(rules)), inputs)
    assert a == b


def test_nc7_no_conflict_for_ordinary_r2_without_qrs(registry):
    assert registry.detect_conflicts(
        _FAMILY, {"zoning_district": "R2", "building_type": "detached"}
    ) is None


def test_nc7_reference_plane_rule_never_conflicts_with_envelope_rules(registry):
    """The (g) rule emits a DIFFERENT output name (reference_plane_elevation_max_ft)
    from the envelope rules; it is complementary, never a same-family conflict."""
    inputs = {
        "zoning_district": "R1-1", "building_type": "detached",
        "lot_area_sqft": 50000, "lot_width_ft": 500, "rear_wall_slope_percent": 50,
    }
    assert registry.detect_conflicts(_FAMILY, inputs) is None


# --------------------------------------------------------------------------
# NC-8 - (g) trigger boundary: area+width path, slope path, neither, conservative design
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "area,width,slope,expect_applicable",
    [
        (9500, 100, 0, True),      # exactly at the area/width boundary
        (9499, 100, 0, False),     # one sq ft short of the area boundary
        (9500, 99, 0, False),      # one ft short of the width boundary
        (100, 10, 5, True),        # exactly at the slope boundary, tiny lot
        (100, 10, 4.99, False),    # just under the slope boundary
        (100, 10, 0, False),       # neither path satisfied
    ],
)
def test_nc8_trigger_boundary_values(registry, area, width, slope, expect_applicable):
    res = registry.evaluate(
        "r1-r2-reference-plane-23421g",
        {
            "zoning_district": "R2", "building_type": "detached",
            "lot_area_sqft": area, "lot_width_ft": width, "rear_wall_slope_percent": slope,
        },
    )
    if expect_applicable:
        assert res.coverage_status == cov.COVERAGE_CONDITIONAL
        assert res.outputs == {"reference_plane_elevation_max_ft": 5.0}
    else:
        assert res.coverage_status == cov.COVERAGE_NOT_APPLICABLE
        assert res.outputs == {}


def test_nc8_setback_geometry_never_a_numeric_output(registry):
    """The full sloping-plane setback (23-421 paragraphs a-f) is a documented
    limitation on the envelope rules, never a numeric output anywhere in this
    family."""
    for rid in ("r1-r2-bare-pitched-height", "r1-r2-suffix-variants-pitched-height"):
        rule = registry.rule(rid)
        district = "R1" if rid == "r1-r2-bare-pitched-height" else "R1-2A"
        res = registry.evaluate(
            rid, _envelope_inputs(rule, zoning_district=district, building_type="detached")
        )
        assert "required_setback_depth" not in res.outputs
        assert "setback" not in json.dumps(res.outputs).lower()
        applied = {e["id"] for e in res.trace.exceptions_applied}
        assert "pitched_plane_setback_professional_review" in applied
