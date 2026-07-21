"""M4-T002 rules-engine <-> property-analysis integration acceptance pack
(RI-S1 .. RI-S8).

Everything is offline and deterministic. The integration under test
(``app.rules.integration``) maps a canonical property profile + the M2-T013
spatial substrate into the M4-T001 evaluator and evaluates the draft R5
residential-FAR family, preserving uncertainty and failing safe.

Spatial fixtures are built from the REAL ``app.spatial`` domain dataclasses and
serialized exactly the way the accepted M2-T012 profile builder serializes them
(``LotIntersectionRecord.as_dict()`` minus ``coverage_audits``, plus
``provenance_refs``) so no field name can silently drift from production. The
rule registry is the REAL one (real R5 rule + real ZR 23-21 source snapshot), so
citation provenance genuinely resolves.
"""

from __future__ import annotations

import json

import jsonschema
import pytest

from app.rules import RuleRegistry
from app.rules import coverage as cov
from app.rules import integration as ri
from app.rules.dsl import evaluation_trace_schema
from app.spatial import policy as spatial_policy
from app.spatial.models import (
    LOT_BOUNDARY_UNCERTAIN,
    LOT_DATA_CONFLICT,
    LOT_INVALID_GEOMETRY_REVIEW,
    LOT_SINGLE_DISTRICT_CONFIDENT,
    LOT_SLIVER_AMBIGUOUS,
    LOT_SPLIT_LOT_CONFIDENT,
    PAIR_INTERIOR_CONFIDENT,
    PAIR_NEAR_BOUNDARY_UNCERTAIN,
    PAIR_SLIVER_AMBIGUOUS,
    PAIR_SPLIT_CONFIDENT,
    CrossCheckOutcome,
    LotIntersectionRecord,
    PairIntersection,
)

_BBL = "1000010001"
_PRR = cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED


def _single_pair_profile(lot_class: str, pair_class: str, *, prr: bool = True) -> dict:
    """One-base-pair spatial profile at a given lot/pair class (used to sweep the
    fail-safe and canonical-coverage assertions across classes)."""
    record = _record(lot_class, [_pair("R5", pair_class)], professional_review_required=prr)
    return _profile(_spatial_section(record))


# --------------------------------------------------------------------------
# Faithful fixture builders (real dataclasses -> the builder's serialized form).
# --------------------------------------------------------------------------

def _pair(
    label: str,
    pair_class: str,
    *,
    layer: str = "nyzd",
    lot_area: float = 10000.0,
    share: tuple[float, float, float] = (1.0, 1.0, 1.0),
    minor_portion: bool = False,
) -> PairIntersection:
    share_min, share_point, share_max = share
    return PairIntersection(
        layer=layer,
        family=spatial_policy.family_for_layer(layer),
        district_label=label,
        pair_class=pair_class,
        raw_intersection_sq_ft=lot_area * share_point,
        firm_intersection_sq_ft=lot_area * share_point,
        dilated_intersection_sq_ft=lot_area * share_max,
        distance_ft=0.0,
        lot_area_sq_ft=lot_area,
        share_min=share_min,
        share_point=share_point,
        share_max=share_max,
        minor_portion=minor_portion,
        band_ft=40.0,
        combination_rule="linear_sum",
        lot_accuracy={"value_ft": 20.0, "basis": "assumed"},
        district_accuracy={"value_ft": 20.0, "basis": "documented"},
        accuracy_basis_assumed=True,
        band_exceeds_feature_width=False,
        sensitivity_flip=False,
        feature_ref={"layer": layer, "object_id": 1},
        notes=[],
    )


def _record(
    lot_overall_class: str,
    pairs: list,
    *,
    professional_review_required: bool,
    review_reasons: list | None = None,
    crosscheck: CrossCheckOutcome | None = None,
    notes: list | None = None,
    bbl: str = _BBL,
) -> LotIntersectionRecord:
    return LotIntersectionRecord(
        bbl=bbl,
        lot_overall_class=lot_overall_class,
        pairs=pairs,
        coverage_audits=[],
        crosscheck=crosscheck,
        professional_review_required=professional_review_required,
        review_reasons=review_reasons or [],
        unassigned_area=[],
        overlap_area=[],
        accuracy_records=[],
        policy=spatial_policy.policy_snapshot(),
        provenance={"source_id": "nyc-dcp-mappluto-arcgis", "requested_bbl": bbl},
        notes=notes or [],
    )


def _spatial_section(record: LotIntersectionRecord, *, provenance_refs=("prov-spatial",)) -> dict:
    """Serialize like app.profile.wave_integration._spatial_intersection_section:
    the record's as_dict() with coverage_audits EXCLUDED plus provenance_refs."""
    record_dict = record.as_dict()
    section = {key: value for key, value in record_dict.items() if key != "coverage_audits"}
    section["provenance_refs"] = list(provenance_refs)
    return section


def _profile(
    spatial_section: dict | None,
    *,
    area: float | None = 10000.0,
    bbl: str = _BBL,
    with_geometry: bool = True,
) -> dict:
    profile: dict = {"identity": {"bbl": bbl}}
    if spatial_section is not None:
        profile["spatial_intersection"] = spatial_section
    if with_geometry:
        profile["lot_geometry"] = {
            "outcome": "single_feature",
            "geometry_status": "valid",
            "review_required": False,
            "area_sq_ft": area,
            "provenance_ref": "prov-lotgeom",
        }
    return profile


def _confident_profile(district: str = "R5", *, area: float = 10000.0) -> dict:
    record = _record(
        LOT_SINGLE_DISTRICT_CONFIDENT,
        [_pair(district, PAIR_INTERIOR_CONFIDENT, lot_area=area)],
        professional_review_required=False,
    )
    return _profile(_spatial_section(record), area=area)


def _iter_coverage_values(payload) -> list:
    """Every value stored under a ``coverage_status`` key anywhere in the payload
    (used to prove no Verified label is present)."""
    found: list = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key == "coverage_status" and isinstance(value, str):
                found.append(value)
            else:
                found.extend(_iter_coverage_values(value))
    elif isinstance(payload, list):
        for item in payload:
            found.extend(_iter_coverage_values(item))
    return found


@pytest.fixture
def registry() -> RuleRegistry:
    return RuleRegistry().load()


# --------------------------------------------------------------------------
# RI-S1 - confident path carries the R5 FAR result, conditional, full trace.
# --------------------------------------------------------------------------

def test_ri_s1_confident_r5_carries_far_result_conditional_with_citations(registry):
    result = ri.evaluate_property(_confident_profile("R5", area=10000.0), registry=registry)

    assert result.coverage_status == cov.COVERAGE_CONDITIONAL
    assert result.coverage_status != cov.COVERAGE_VERIFIED
    assert result.zoning_district == "R5"
    assert result.lot_area_sq_ft == 10000.0
    assert result.lot_area_source == "lot_geometry.area_sq_ft"
    assert result.fail_safe is False
    assert result.coverage_source == "rule_evaluator"

    assert len(result.evaluations) == 1
    trace = result.evaluations[0]
    assert trace["outputs"] == {
        "max_residential_far": 1.5,
        "max_residential_floor_area_sq_ft": 15000.0,
    }
    assert trace["rule_version"] == "0.1.0-draft"
    # every citation resolves to source-snapshot provenance (fail-closed export)
    for citation in trace["citations"]:
        assert citation["provenance"]["content_digest_sha256"]
        assert citation["section"] == "23-21"
    # the deterministic trace validates against the canonical evaluation-trace contract
    jsonschema.Draft202012Validator(evaluation_trace_schema()).validate(trace)
    # input provenance points back into the profile's provenance graph
    assert result.input_provenance["lot_area_sq_ft"] == ["prov-lotgeom"]
    assert result.input_provenance["zoning_district"] == ["prov-spatial"]
    # export() succeeds (never Verified)
    assert result.export()["coverage_status"] == cov.COVERAGE_CONDITIONAL


def test_ri_s1_r5d_far_value(registry):
    result = ri.evaluate_property(_confident_profile("R5D", area=5000.0), registry=registry)
    assert result.zoning_district == "R5D"
    assert result.evaluations[0]["outputs"] == {
        "max_residential_far": 2.0,
        "max_residential_floor_area_sq_ft": 10000.0,
    }
    assert result.coverage_status == cov.COVERAGE_CONDITIONAL


def test_ri_s1_lot_area_falls_back_to_spatial_pair_when_geometry_absent(registry):
    # No lot_geometry section -> the confident base pair's lot area is used.
    record = _record(
        LOT_SINGLE_DISTRICT_CONFIDENT,
        [_pair("R5", PAIR_INTERIOR_CONFIDENT, lot_area=8000.0)],
        professional_review_required=False,
    )
    profile = _profile(_spatial_section(record), with_geometry=False)
    result = ri.evaluate_property(profile, registry=registry)
    assert result.lot_area_sq_ft == 8000.0
    assert result.lot_area_source == "spatial_intersection.pairs[].lot_area_sq_ft"
    assert result.evaluations[0]["outputs"]["max_residential_floor_area_sq_ft"] == 12000.0


# --------------------------------------------------------------------------
# RI-S2 - uncertainty preserved, never collapsed; no district, no value.
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "lot_class,pair_class,expected",
    [
        (LOT_BOUNDARY_UNCERTAIN, PAIR_NEAR_BOUNDARY_UNCERTAIN, _PRR),
        (LOT_SLIVER_AMBIGUOUS, PAIR_SLIVER_AMBIGUOUS, _PRR),
        (LOT_SPLIT_LOT_CONFIDENT, PAIR_SPLIT_CONFIDENT, _PRR),
    ],
)
def test_ri_s2_uncertain_geometry_fails_safe_no_value(registry, lot_class, pair_class, expected):
    record = _record(
        lot_class,
        [
            _pair("R5", pair_class, share=(0.55, 0.60, 0.65)),
            _pair("R6", pair_class, share=(0.35, 0.40, 0.45)),
        ],
        professional_review_required=True,
        review_reasons=[f"lot_overall_class={lot_class}"],
    )
    result = ri.evaluate_property(_profile(_spatial_section(record)), registry=registry)

    assert result.coverage_status == expected
    assert result.zoning_district is None          # never collapsed to a definitive district
    assert result.evaluations == []                # no computed value
    assert result.fail_safe is True
    assert result.fail_safe_reason == ri.FAILSAFE_GEOMETRY_UNCERTAIN
    assert result.needs_review is True

    # share RANGES + review flags surfaced, never renormalized to a point
    candidates = {
        c["district_label"]: c
        for c in result.spatial_uncertainty["base_district_candidates"]
    }
    assert candidates["R5"]["share_min"] == 0.55 and candidates["R5"]["share_max"] == 0.65
    assert candidates["R6"]["share_min"] == 0.35 and candidates["R6"]["share_max"] == 0.45
    assert result.spatial_uncertainty["review_reasons"] == [f"lot_overall_class={lot_class}"]
    assert result.spatial_uncertainty["professional_review_required"] is True


def test_ri_s2_data_conflict_is_typed_and_preserved(registry):
    crosscheck = CrossCheckOutcome(
        outcome="set_conflict",
        ztldb_ordered_districts=[{"position": 1, "label": "R6"}],
        geometric_ordered_districts=[{"label": "R5", "share_point": 1.0}],
        possible_vintage_skew=False,
        ztldb_dataset_version="2026v1",
        display_upgrade="none",
        vintage_comparison="not_applicable",
        notes=["ztldb set-conflict"],
    )
    record = _record(
        LOT_DATA_CONFLICT,
        [_pair("R5", PAIR_INTERIOR_CONFIDENT)],
        professional_review_required=True,
        review_reasons=["ztldb set_conflict"],
        crosscheck=crosscheck,
    )
    result = ri.evaluate_property(_profile(_spatial_section(record)), registry=registry)

    assert result.coverage_status == cov.COVERAGE_DATA_CONFLICT
    assert result.fail_safe_reason == ri.FAILSAFE_DATA_CONFLICT
    assert result.zoning_district is None
    assert result.evaluations == []
    # the typed conflict itself flows through, never adjudicated away
    assert result.spatial_uncertainty["crosscheck"]["outcome"] == "set_conflict"


def test_ri_s2_invalid_geometry_review_fails_safe(registry):
    record = _record(
        LOT_INVALID_GEOMETRY_REVIEW,
        [],
        professional_review_required=True,
        review_reasons=["lot geometry not intersectable"],
    )
    profile = _profile(_spatial_section(record), with_geometry=False)
    result = ri.evaluate_property(profile, registry=registry)
    assert result.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert result.zoning_district is None
    assert result.evaluations == []


# --------------------------------------------------------------------------
# RI-S3 - fail-safe on missing evidence (absent section / missing context).
# --------------------------------------------------------------------------

def test_ri_s3_absent_spatial_intersection_fails_safe(registry):
    profile = _profile(None)  # no spatial_intersection at all
    result = ri.evaluate_property(profile, registry=registry)
    assert result.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert result.fail_safe_reason == ri.FAILSAFE_SPATIAL_ABSENT
    assert result.spatial_context is None
    assert result.zoning_district is None
    assert result.lot_area_sq_ft is None
    assert result.evaluations == []
    assert result.needs_review is True


def test_ri_s3_present_section_missing_class_fails_safe(registry):
    # spatial_intersection present but lot_overall_class missing -> incomplete context
    section = {
        "professional_review_required": False,
        "pairs": [],
        "provenance_refs": ["prov-spatial"],
    }
    result = ri.evaluate_property(_profile(section), registry=registry)
    assert result.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert result.fail_safe_reason == ri.FAILSAFE_SPATIAL_INCOMPLETE
    assert result.zoning_district is None
    assert result.evaluations == []


def test_ri_s3_confident_but_no_interior_pair_fails_safe(registry):
    # class says confident but the pairs contradict it -> never guess a district
    record = _record(
        LOT_SINGLE_DISTRICT_CONFIDENT,
        [_pair("R5", PAIR_SPLIT_CONFIDENT)],  # not interior_confident
        professional_review_required=False,
    )
    result = ri.evaluate_property(_profile(_spatial_section(record)), registry=registry)
    assert result.coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
    assert result.fail_safe_reason == ri.FAILSAFE_INCONSISTENT_CONFIDENT
    assert result.zoning_district is None
    assert result.evaluations == []


# --------------------------------------------------------------------------
# RI-S4 - honest draft status: coverage + needs_review + not-Verified disclaimer.
# --------------------------------------------------------------------------

def test_ri_s4_result_carries_coverage_needs_review_and_disclaimer(registry):
    result = ri.evaluate_property(_confident_profile("R5"), registry=registry)
    assert result.coverage_status in cov.COVERAGE_STATUSES
    assert result.needs_review is True
    assert result.rule_lifecycle_statuses == ["needs_review"]
    assert "not a Verified determination" in result.not_verified_disclaimer
    # no field anywhere equals verified
    assert cov.COVERAGE_VERIFIED not in _iter_coverage_values(result.as_dict())
    # the evaluated rule is a draft (agent-authorable), never published
    assert result.evaluations[0]["rule_status"] == "needs_review"


def test_ri_s4_fail_safe_result_also_honest(registry):
    result = ri.evaluate_property(_profile(None), registry=registry)
    assert result.needs_review is True
    assert result.not_verified_disclaimer
    assert cov.COVERAGE_VERIFIED not in _iter_coverage_values(result.as_dict())


# --------------------------------------------------------------------------
# RI-S5 - determinism: same profile -> byte-identical output.
# --------------------------------------------------------------------------

def test_ri_s5_same_profile_byte_identical(registry):
    profile_a = _confident_profile("R5")
    profile_b = _confident_profile("R5")
    out_a = ri.evaluate_property(profile_a, registry=registry).as_dict()
    # a fresh registry load must produce identical bytes
    out_b = ri.evaluate_property(profile_b, registry=RuleRegistry().load()).as_dict()
    assert json.dumps(out_a, sort_keys=True) == json.dumps(out_b, sort_keys=True)


def test_ri_s5_fail_safe_is_deterministic(registry):
    record = _record(
        LOT_SPLIT_LOT_CONFIDENT,
        [_pair("R5", PAIR_SPLIT_CONFIDENT, share=(0.5, 0.6, 0.7))],
        professional_review_required=True,
    )
    section = _spatial_section(record)
    out_a = ri.evaluate_property(_profile(section), registry=registry).as_dict()
    out_b = ri.evaluate_property(_profile(section), registry=registry).as_dict()
    assert json.dumps(out_a, sort_keys=True) == json.dumps(out_b, sort_keys=True)


# --------------------------------------------------------------------------
# RI-S6 - coverage honesty for a non-R5 district / unimplemented family.
# --------------------------------------------------------------------------

def test_ri_s6_confident_non_r5_district_is_visible_not_applicable(registry):
    result = ri.evaluate_property(_confident_profile("R7"), registry=registry)
    assert result.zoning_district == "R7"  # confidently known...
    assert result.coverage_status == cov.COVERAGE_NOT_APPLICABLE  # ...but no R5 rule applies
    assert result.evaluations  # the not_applicable trace is surfaced, not silence
    assert result.evaluations[0]["applicability_outcome"] is False
    assert any("not_applicable" in reason for reason in result.reasons)


def test_ri_s6_unimplemented_family_is_visible_unsupported(registry):
    # coverage honesty mirrors the engine's RE-S7: an absent family is unsupported
    assert (
        registry.family_coverage("commercial_far")["coverage_status"]
        == cov.COVERAGE_UNSUPPORTED
    )
    result = ri.evaluate_property(_confident_profile("R5"), registry=registry)
    assert result.family_coverage["coverage_status"] == cov.COVERAGE_CONDITIONAL
    assert result.family_coverage["family"] == ri.TARGET_FAMILY


# --------------------------------------------------------------------------
# RI-S7 - downstream safety: a draft can never be read as Verified.
# --------------------------------------------------------------------------

def test_ri_s7_no_verified_anywhere_in_any_outcome(registry):
    profiles = [
        _confident_profile("R5"),
        _confident_profile("R7"),
        _profile(None),
        _single_pair_profile(LOT_DATA_CONFLICT, PAIR_INTERIOR_CONFIDENT),
    ]
    for profile in profiles:
        payload = ri.evaluate_property(profile, registry=registry).export()
        assert cov.COVERAGE_VERIFIED not in _iter_coverage_values(payload)


def test_ri_s7_guard_rejects_a_verified_payload():
    # top-level verified is refused
    with pytest.raises(ri.DraftVerifiedError):
        ri.assert_not_verified({"coverage_status": cov.COVERAGE_VERIFIED, "evaluations": []})
    # a verified evaluator trace is refused
    with pytest.raises(ri.DraftVerifiedError):
        ri.assert_not_verified(
            {
                "coverage_status": cov.COVERAGE_CONDITIONAL,
                "evaluations": [{"rule_id": "x", "coverage_status": cov.COVERAGE_VERIFIED}],
            }
        )


def test_ri_s7_disclaimer_text_is_not_a_status(registry):
    # the disclaimer contains the word "Verified" but is never a coverage_status,
    # so the guard passes on a real (draft) result
    result = ri.evaluate_property(_confident_profile("R5"), registry=registry)
    ri.assert_not_verified(result)  # must not raise
    assert "Verified" in result.not_verified_disclaimer


# --------------------------------------------------------------------------
# RI-S8 - regression: spatial-vocab drift guard + canonical coverage only.
# --------------------------------------------------------------------------

def test_ri_s8_spatial_vocabulary_drift_guard():
    """The integration duplicates four spatial vocabulary values to avoid pulling
    the shapely-heavy app.spatial package into the service path. They MUST equal
    the real ones (mirrors the coverage.py <-> canonical-contract drift guard)."""
    assert ri._BASE_ZONING_FAMILY == spatial_policy.family_for_layer("nyzd")
    assert ri._LOT_SINGLE_DISTRICT_CONFIDENT == LOT_SINGLE_DISTRICT_CONFIDENT
    assert ri._LOT_DATA_CONFLICT == LOT_DATA_CONFLICT
    assert ri._PAIR_INTERIOR_CONFIDENT == PAIR_INTERIOR_CONFIDENT


def test_ri_s8_only_canonical_coverage_statuses(registry):
    profiles = [
        _confident_profile("R5"),
        _confident_profile("R7"),
        _profile(None),
        _single_pair_profile(LOT_BOUNDARY_UNCERTAIN, PAIR_NEAR_BOUNDARY_UNCERTAIN),
    ]
    for profile in profiles:
        payload = ri.evaluate_property(profile, registry=registry).as_dict()
        for value in _iter_coverage_values(payload):
            assert value in cov.COVERAGE_STATUSES
            assert value != cov.COVERAGE_VERIFIED


def test_ri_s8_target_family_matches_r5_rule_family(registry):
    # the family this slice targets is exactly the R5 rule's declared family
    rule = registry.rule("r5-residential-far")
    assert rule.family == ri.TARGET_FAMILY
