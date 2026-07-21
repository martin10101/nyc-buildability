"""M4-T001 legal-rule acceptance-scenario pack (RE-S1 .. RE-S8) + the
ACCEPTANCE_SCENARIO_STANDARD legal-rule cases: applies+passes, applies+fails,
not-applicable, threshold boundary, missing input, general-modified-by-special,
exception applies/does-not, effective-date/citation + rule-version assertions.

Everything is offline and deterministic. The production engine + R5 rule live
under services/api/app/rules/**; a SYNTHETIC second-family fixture (rear yard)
under tests/rules/fixtures/** proves a structurally different family needs zero
engine changes.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import jsonschema
import pytest

from app.rules import RuleRegistry, lifecycle
from app.rules import coverage as cov
from app.rules.dsl import (
    DSLError,
    build_rule_definition,
    evaluation_trace_schema,
    rule_definition_schema,
)
from app.rules.models import ProvenanceError
from app.rules.operations import COMPUTE_OPS
from app.rules.snapshots import SnapshotError, SnapshotStore

_FIXTURES = Path(__file__).resolve().parent / "fixtures"
# test file: <root>/services/api/tests/rules/test_rules_engine.py
_ENGINE_DIR = Path(__file__).resolve().parents[2] / "app" / "rules"  # <root>/services/api/app/rules
_REPO_ROOT = _ENGINE_DIR.parents[3]  # <root>
R5_RULE_ID = "r5-residential-far"
_R5_RULE_PATH = _ENGINE_DIR / "rulesets" / "r5_residential_far.rule.json"


def _r5_doc() -> dict:
    return json.loads(_R5_RULE_PATH.read_text("utf-8"))


def _std(district: str, area: float) -> dict:
    """Standard-zoning-lot inputs for the R5 rule."""
    return {
        "zoning_district": district,
        "lot_area_sq_ft": area,
        "site_class": "standard_zoning_lot",
    }


@pytest.fixture
def registry() -> RuleRegistry:
    return RuleRegistry().load()


@pytest.fixture
def demo_registry() -> RuleRegistry:
    """Registry over the SYNTHETIC second-family fixtures (rear yard)."""
    snaps = SnapshotStore(_FIXTURES / "snapshots")
    return RuleRegistry(_FIXTURES / "rulesets", snapshots=snaps).load()


# --------------------------------------------------------------------------
# RE-S1 - DSL round-trip: parse, schema-validate, deterministic full trace.
# --------------------------------------------------------------------------

def test_re_s1_dsl_round_trip_and_full_trace(registry):
    result = registry.evaluate(
        R5_RULE_ID,
        {"zoning_district": "R5", "lot_area_sq_ft": 10000, "site_class": "standard_zoning_lot"},
    )
    trace = result.export()
    # deterministic computed outputs
    assert trace["outputs"] == {
        "max_residential_far": 1.5,
        "max_residential_floor_area_sq_ft": 15000.0,
    }
    # full trace carries inputs, formula steps, citation, versions
    assert trace["evaluated_inputs"]["zoning_district"] == "R5"
    assert [s["op"] for s in trace["computation_steps"]] == ["identity", "multiply"]
    assert trace["computation_steps"][1]["resolved_args"] == [10000, 1.5]
    assert trace["rule_version"] == "0.1.0-draft"
    assert trace["citations"][0]["section"] == "23-21"
    # the emitted trace validates against the evaluation-trace contract
    jsonschema.Draft202012Validator(evaluation_trace_schema()).validate(trace)


def test_re_s1_rule_file_validates_against_schema():
    document = _r5_doc()
    jsonschema.Draft202012Validator(rule_definition_schema()).validate(document)


def test_re_s8_determinism_same_inputs_identical_trace(registry):
    inputs = {"zoning_district": "R5D", "lot_area_sq_ft": 5000, "site_class": "standard_zoning_lot"}
    a = registry.evaluate(R5_RULE_ID, inputs).export()
    b = RuleRegistry().load().evaluate(R5_RULE_ID, inputs).export()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert a["outputs"] == {"max_residential_far": 2.0, "max_residential_floor_area_sq_ft": 10000.0}


# --------------------------------------------------------------------------
# RE-S2 - lifecycle: nothing verified without a recorded G6 approval.
# --------------------------------------------------------------------------

def test_re_s2_draft_rule_never_verified(registry):
    result = registry.evaluate(
        R5_RULE_ID,
        {"zoning_district": "R5", "lot_area_sq_ft": 8000, "site_class": "standard_zoning_lot"},
    )
    assert result.coverage_status == cov.COVERAGE_CONDITIONAL
    assert result.coverage_status != cov.COVERAGE_VERIFIED
    assert result.trace.rule_status in lifecycle.AGENT_AUTHORABLE_STATUSES


def test_re_s2_dsl_rejects_published_status(registry):
    document = _r5_doc()
    document["status"] = "published"
    with pytest.raises((DSLError, lifecycle.LifecycleError)):
        build_rule_definition(document, registry.snapshots)


def test_re_s2_publish_requires_g6_approval():
    with pytest.raises(lifecycle.LifecycleError):
        lifecycle.publish(lifecycle.STATUS_NEEDS_REVIEW, None)
    approval = lifecycle.G6Approval(
        rule_id=R5_RULE_ID, rule_version="0.1.0-draft",
        reviewer="licensed-zoning-professional", approved_at="2026-07-21T00:00:00Z",
        approval_ref="g6:demo",
    )
    assert lifecycle.publish(lifecycle.STATUS_NEEDS_REVIEW, approval) == lifecycle.STATUS_PUBLISHED


def test_re_s2_verified_only_for_published_with_matching_approval(registry):
    rule = registry.rule(R5_RULE_ID)
    published = dataclasses.replace(rule, status=lifecycle.STATUS_PUBLISHED)
    approval = lifecycle.G6Approval(
        rule_id=rule.rule_id, rule_version=rule.rule_version,
        reviewer="licensed-zoning-professional", approved_at="2026-07-21T00:00:00Z",
        approval_ref="g6:demo",
    )
    from app.rules import evaluator
    inputs = {"zoning_district": "R5", "lot_area_sq_ft": 8000, "site_class": "standard_zoning_lot"}
    # with matching approval -> verified is reachable ONLY here
    verified = evaluator.evaluate(published, inputs, registry.snapshots, g6_approval=approval)
    assert verified.coverage_status == cov.COVERAGE_VERIFIED
    # published but NO approval -> not verified
    unapproved = evaluator.evaluate(published, inputs, registry.snapshots, g6_approval=None)
    assert unapproved.coverage_status != cov.COVERAGE_VERIFIED
    # approval for a different version -> not verified
    stale = dataclasses.replace(approval, rule_version="9.9.9")
    mism = evaluator.evaluate(published, inputs, registry.snapshots, g6_approval=stale)
    assert mism.coverage_status != cov.COVERAGE_VERIFIED


# --------------------------------------------------------------------------
# RE-S3 - applicability (positive / negative / boundary) + special-district
# interaction point (general rule modified by a special-rule stub).
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "district,applies",
    [("R5", True), ("R5A", True), ("R5D", True), ("R7", False), ("C1-4", False)],
)
def test_re_s3_applicability(registry, district, applies):
    result = registry.evaluate(R5_RULE_ID, _std(district, 5000))
    if applies:
        assert result.trace.applicability_outcome is True
        assert result.coverage_status == cov.COVERAGE_CONDITIONAL
    else:
        assert result.trace.applicability_outcome is False
        assert result.coverage_status == cov.COVERAGE_NOT_APPLICABLE
        assert result.outputs == {}


def test_re_s3_special_district_interaction_point_present(registry):
    rule = registry.rule(R5_RULE_ID)
    sdi = {s["id"]: s for s in rule.special_district_interactions}
    assert "special_purpose_district_modifier" in sdi
    # a general rule that surfaces a special-district modifier stub
    assert sdi["special_purpose_district_modifier"]["special_rule_stub"]


# --------------------------------------------------------------------------
# RE-S4 - missing evidence (no guessed value) + uncertainty propagation.
# --------------------------------------------------------------------------

def test_re_s4_missing_required_input_yields_typed_missing_no_value(registry):
    result = registry.evaluate(R5_RULE_ID, {"zoning_district": "R5"})  # lot_area_sq_ft missing
    assert result.trace.data_completeness == cov.COMPLETENESS_MISSING_CRITICAL
    assert result.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert result.outputs == {}  # never a guessed value


@pytest.mark.parametrize(
    "cls,expected",
    [
        ("single_district_confident", cov.COVERAGE_CONDITIONAL),
        ("boundary_uncertain", cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED),
        ("sliver_ambiguous", cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED),
        ("split_lot_confident", cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED),
        ("invalid_geometry_review", cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED),
        ("data_conflict", cov.COVERAGE_DATA_CONFLICT),
    ],
)
def test_re_s4_uncertainty_propagates_never_collapses(registry, cls, expected):
    ctx = {
        "lot_overall_class": cls,
        "professional_review_required": cls != "single_district_confident",
        "coverage_note": "facts_with_uncertainty; not a Verified zoning determination",
    }
    result = registry.evaluate(
        R5_RULE_ID,
        {"zoning_district": "R5", "lot_area_sq_ft": 10000, "site_class": "standard_zoning_lot"},
        spatial_context=ctx,
    )
    assert result.coverage_status == expected
    # uncertain geometry is NEVER collapsed into a definitive single district
    assert result.trace.uncertainty["collapsed_into_definitive_district"] is False
    if expected != cov.COVERAGE_CONDITIONAL:
        assert result.trace.uncertainty["propagated"] is True


# --------------------------------------------------------------------------
# RE-S5 - second-family representability with ZERO engine changes.
# --------------------------------------------------------------------------

def test_re_s5_second_family_evaluates_with_same_engine(demo_registry):
    assert demo_registry.families() == ["rear_yard"]
    result = demo_registry.evaluate("r5-rear-yard-demo", {"zoning_district": "R5"})
    assert result.trace.applicability_outcome is True
    assert result.outputs == {"min_rear_yard_depth_ft": 30.0}
    assert result.coverage_status == cov.COVERAGE_CONDITIONAL  # draft, never verified


def test_re_s5_zero_engine_changes_families_are_pure_data():
    """Diff-provable: no engine source file mentions any family name; families
    are data, not code, so a structurally different family needs no engine edit."""
    engine_files = ["operations.py", "evaluator.py", "registry.py", "dsl.py", "models.py",
                    "coverage.py", "lifecycle.py", "snapshots.py"]
    for name in engine_files:
        text = (_ENGINE_DIR / name).read_text("utf-8")
        assert "residential_far" not in text, f"{name} hardcodes a family name"
        assert "rear_yard" not in text, f"{name} hardcodes a family name"
        assert "R5" not in text, f"{name} hardcodes a district"


def test_re_s5_second_family_uses_only_generic_ops(demo_registry):
    rule = demo_registry.rule("r5-rear-yard-demo")
    ops_used = {s["op"] for s in rule.computation["steps"]}
    assert ops_used <= set(COMPUTE_OPS)  # only the closed generic op set


# --------------------------------------------------------------------------
# RE-S6 - provenance: every value traces to a section snapshot; export without
# provenance is impossible.
# --------------------------------------------------------------------------

def test_re_s6_every_citation_resolves_to_snapshot_provenance(registry):
    result = registry.evaluate(R5_RULE_ID, {"zoning_district": "R5", "lot_area_sq_ft": 10000})
    for citation in result.trace.citations:
        prov = citation["provenance"]
        assert prov["content_digest_sha256"]
        assert prov["request_url"].startswith("https://zoningresolution.planning.nyc.gov")
        assert prov["section_number"] == "23-21"
        assert prov["section_last_amended"] == "2024-12-05"
        # draft provenance is honest about not being raw-verified
        assert prov["raw_html_verified"] is False


def test_re_s6_export_without_provenance_is_impossible(registry):
    result = registry.evaluate(R5_RULE_ID, {"zoning_district": "R5", "lot_area_sq_ft": 10000})
    # tamper: strip provenance from a citation -> export must fail closed
    result.trace.citations[0]["provenance"] = {}
    with pytest.raises(ProvenanceError):
        result.export()


def test_re_s6_snapshot_digest_tamper_evidence(tmp_path):
    snap_path = _REPO_ROOT / "docs" / "research" / "zr-snapshots" / "v1" / "zr-23-21.snapshot.json"
    src = json.loads(snap_path.read_text("utf-8"))
    src["verbatim_excerpt"] = src["verbatim_excerpt"] + " TAMPERED"
    p = tmp_path / "zr-23-21.snapshot.json"
    p.write_text(json.dumps(src), encoding="utf-8")
    with pytest.raises(SnapshotError):
        SnapshotStore(tmp_path).load()


# --------------------------------------------------------------------------
# RE-S7 - coverage honesty for an unimplemented family.
# --------------------------------------------------------------------------

def test_re_s7_unimplemented_family_is_visible_unsupported(registry):
    assert registry.family_coverage("commercial_far")["coverage_status"] == cov.COVERAGE_UNSUPPORTED
    impl = registry.family_coverage("residential_far")
    assert impl["coverage_status"] == cov.COVERAGE_CONDITIONAL


# --------------------------------------------------------------------------
# ACCEPTANCE_SCENARIO_STANDARD legal-rule cases (folded in).
# --------------------------------------------------------------------------

def test_applies_passes_clean_evaluation(registry):
    r = registry.evaluate(R5_RULE_ID, _std("R5A", 4000))
    assert r.trace.applicability_outcome is True
    assert r.coverage_status == cov.COVERAGE_CONDITIONAL
    assert r.outputs["max_residential_far"] == 1.5


def test_applies_fails_blocked_by_data_conflict(registry):
    r = registry.evaluate(
        R5_RULE_ID, _std("R5", 4000),
        spatial_context={
            "lot_overall_class": "data_conflict", "professional_review_required": True,
        },
    )
    assert r.coverage_status == cov.COVERAGE_DATA_CONFLICT


def test_threshold_boundary_lot_area(registry):
    # boundary at the 4,000 sq ft single-DU-cap threshold from the source footnote
    for area in (3999.99, 4000.0, 4000.01):
        r = registry.evaluate(R5_RULE_ID, _std("R5", area))
        assert r.outputs["max_residential_floor_area_sq_ft"] == round(area * 1.5, 10)


def test_exception_applies_and_does_not(registry):
    # site_class unknown -> qualifying-site alternative applies (conditional, surfaced)
    unknown = registry.evaluate(R5_RULE_ID, {"zoning_district": "R5", "lot_area_sq_ft": 5000})
    ids_unknown = {e["id"] for e in unknown.trace.exceptions_applied}
    assert "qualifying_residential_site" in ids_unknown
    # site_class standard -> the qualifying alternative does NOT apply
    standard = registry.evaluate(R5_RULE_ID, _std("R5", 5000))
    ids_standard = {e["id"] for e in standard.trace.exceptions_applied}
    assert "qualifying_residential_site" not in ids_standard
    # the documented single-DU-cap limitation is always recorded
    assert "single_dwelling_unit_equivalent_far_cap" in ids_standard


def test_citation_and_rule_version_and_effective_date_assertions(registry):
    r = registry.evaluate(R5_RULE_ID, {"zoning_district": "R5", "lot_area_sq_ft": 5000})
    trace = r.export()
    assert trace["rule_version"] == "0.1.0-draft"
    c = trace["citations"][0]
    assert c["section"] == "23-21"
    assert c["last_amended"] == "2024-12-05"  # effective/amendment date carried through
    assert c["provenance"]["section_last_amended"] == "2024-12-05"


def test_general_modified_by_special_stub_is_surfaced(registry):
    # the general rule declares the special-district interaction point (modifier stub)
    rule = registry.rule(R5_RULE_ID)
    stubs = [s for s in rule.special_district_interactions if s.get("special_rule_stub")]
    assert stubs, "general rule must surface a special-district modifier interaction point"


# --------------------------------------------------------------------------
# DSL integrity guards.
# --------------------------------------------------------------------------

def test_dsl_rejects_forward_step_reference(registry):
    document = _r5_doc()
    document["computation"]["steps"][0]["args"] = [{"step": "floor_area"}]  # forward ref
    with pytest.raises(DSLError):
        build_rule_definition(document, registry.snapshots)


def test_dsl_rejects_unresolvable_citation(registry):
    document = _r5_doc()
    document["citations"][0]["snapshot_id"] = "zr-does-not-exist"
    with pytest.raises(SnapshotError):
        build_rule_definition(document, registry.snapshots)


def test_coverage_and_completeness_match_canonical_contract():
    """Engine vocabulary must equal the canonical coverage_status contract."""
    canonical = json.loads(
        (_REPO_ROOT / "packages" / "contracts" / "schemas" / "v1"
         / "coverage_status.schema.json").read_text("utf-8")
    )
    assert set(cov.COVERAGE_STATUSES) == set(canonical["enum"])
    assert set(cov.COMPLETENESS_STATUSES) == set(canonical["$defs"]["data_completeness"]["enum"])
