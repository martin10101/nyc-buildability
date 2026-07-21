"""M2-T013 spatial-intersection engine acceptance pack.

Covers the packet scenarios SI-S1..S12 and SI-CF1..CF7 plus the uncertainty /
coverage-honesty / reproducibility requirements. Synthetic axis-aligned boxes
(EPSG:2263 US survey feet) give precise control of the compound band; two tests
consume the REAL accepted connector fixtures (ZF03 nyzd R3-2 district, MPG06
holed lot) by reference to prove the engine operates on real connector geometry.

Invariants asserted throughout: no result is ever labelled ``Verified``; no
uncertain case collapses into a definitive assignment; shares are never
renormalized; exact geometric results are preserved regardless of class.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import shapely
from shapely import geos_version

from app.connectors.mappluto_geometry_arcgis import (
    CRS_STAMP,
    analyze_lot_geometry,
    canonical_to_shapely,
)
from app.spatial import (
    DistrictFeature,
    LotInput,
    classify_pair,
    compose_from_connectors,
    compose_lot_intersection,
    district_features_from_layer_result,
    lot_input_from_result,
    policy_snapshot,
)
from app.spatial.models import (
    AUDIT_COMPLETE_NONOVERLAPPING,
    AUDIT_GAPS_DETECTED,
    AUDIT_NOT_APPLICABLE,
    AUDIT_OVERLAPS_DETECTED,
    AUDIT_UNKNOWN,
    LOT_BOUNDARY_UNCERTAIN,
    LOT_DATA_CONFLICT,
    LOT_INVALID_GEOMETRY_REVIEW,
    LOT_SINGLE_DISTRICT_CONFIDENT,
    LOT_SLIVER_AMBIGUOUS,
    LOT_SPLIT_LOT_CONFIDENT,
    PAIR_EXTERIOR_CONFIDENT,
    PAIR_INTERIOR_CONFIDENT,
    PAIR_NEAR_BOUNDARY_UNCERTAIN,
    PAIR_SLIVER_AMBIGUOUS,
    PAIR_SPLIT_CONFIDENT,
    XCHK_AGREEMENT,
    XCHK_ORDERING_DISAGREEMENT,
    XCHK_SET_CONFLICT,
    XCHK_ZTLDB_ABSENT,
)
from app.spatial.policy import (
    MAPPLUTO_LOT_ACCURACY,
    SourceAccuracy,
    combined_band_ft,
    layer_accuracy,
)

FIX = Path(__file__).resolve().parents[1] / "fixtures"

# Every legal value the classification-bearing fields may take. "verified" is
# absent by construction (SI-CF5 / SI-S9).
_PAIR_CLASSES = {
    PAIR_INTERIOR_CONFIDENT,
    PAIR_EXTERIOR_CONFIDENT,
    PAIR_SPLIT_CONFIDENT,
    PAIR_NEAR_BOUNDARY_UNCERTAIN,
    PAIR_SLIVER_AMBIGUOUS,
}
_LOT_CLASSES = {
    LOT_SINGLE_DISTRICT_CONFIDENT,
    LOT_SPLIT_LOT_CONFIDENT,
    LOT_BOUNDARY_UNCERTAIN,
    LOT_SLIVER_AMBIGUOUS,
    LOT_DATA_CONFLICT,
    LOT_INVALID_GEOMETRY_REVIEW,
}
_AUDIT_STATUSES = {
    AUDIT_UNKNOWN,
    AUDIT_COMPLETE_NONOVERLAPPING,
    AUDIT_GAPS_DETECTED,
    AUDIT_OVERLAPS_DETECTED,
    AUDIT_NOT_APPLICABLE,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def box(minx: float, miny: float, maxx: float, maxy: float) -> list:
    """Canonical form of an axis-aligned rectangle (single polygon, open ring)."""
    return [[[[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy]]]]


def lot(canonical, *, bbl="1000010001", area=None, status="valid", review=False, accuracy=None):
    return LotInput(
        bbl=bbl,
        canonical_geometry=canonical,
        area_sq_ft=area,
        accuracy=accuracy or MAPPLUTO_LOT_ACCURACY,
        geometry_status=status,
        review_required=review,
        provenance={"source_id": "test"},
    )


def district(canonical, *, label="R5", layer="nyzd", family=None, accuracy=None, status="valid"):
    from app.spatial.policy import family_for_layer

    return DistrictFeature(
        layer=layer,
        family=family or family_for_layer(layer),
        label=label,
        canonical_geometry=canonical,
        accuracy=accuracy or layer_accuracy(layer),
        geometry_status=status,
        feature_ref={"layer": layer, "label": label},
    )


def ztldb(*district_values):
    return {
        "zoning_districts": [
            {"position": i + 1, "column": f"zoning_district_{i + 1}", "value": v}
            for i, v in enumerate(district_values)
        ]
    }


def assert_vocab(record) -> None:
    """No classification field is ever outside its known vocabulary (=> never
    'verified')."""
    assert record.lot_overall_class in _LOT_CLASSES
    for pair in record.pairs:
        assert pair.pair_class in _PAIR_CLASSES, pair.pair_class
    for audit in record.coverage_audits:
        assert audit.status in _AUDIT_STATUSES


# ---------------------------------------------------------------------------
# SI-S1 interior lot (primary)
# ---------------------------------------------------------------------------
def test_si_s1_interior_lot_single_district_confident() -> None:
    rec = compose_lot_intersection(
        lot(box(100, 100, 200, 200)),
        [district(box(0, 0, 400, 400), label="R5")],
        ztldb_assignment=ztldb("R5"),
        ztldb_status="ok",
    )
    assert rec.lot_overall_class == LOT_SINGLE_DISTRICT_CONFIDENT
    assert rec.pairs[0].pair_class == PAIR_INTERIOR_CONFIDENT
    assert rec.professional_review_required is False
    # Exact geometric result preserved (advisory 2.3): lot fully inside district.
    assert rec.pairs[0].raw_intersection_sq_ft == pytest.approx(10000.0, rel=1e-9)
    assert rec.pairs[0].share_point == pytest.approx(1.0, rel=1e-9)
    assert rec.crosscheck.outcome == XCHK_AGREEMENT
    assert rec.crosscheck.display_upgrade == "none"
    assert_vocab(rec)


# ---------------------------------------------------------------------------
# SI-S2 split lot: per-district ranges, shares NOT forced to 100%
# ---------------------------------------------------------------------------
def test_si_s2_split_lot_two_districts_with_ranges() -> None:
    a = district(box(0, 0, 200, 400), label="R5")
    b = district(box(200, 0, 400, 400), label="R6")
    rec = compose_lot_intersection(
        lot(box(50, 100, 350, 300)),  # firmly into both A and B
        [a, b],
        ztldb_assignment=ztldb("R5", "R6"),
        ztldb_status="ok",
    )
    assert rec.lot_overall_class == LOT_SPLIT_LOT_CONFIDENT
    classes = {p.district_label: p.pair_class for p in rec.pairs}
    assert classes == {"R5": PAIR_SPLIT_CONFIDENT, "R6": PAIR_SPLIT_CONFIDENT}
    for p in rec.pairs:
        assert p.share_min <= p.share_point <= p.share_max
    assert_vocab(rec)


# ---------------------------------------------------------------------------
# SI-S3 near-boundary: preserved exact result; ZTLDB upgrades DISPLAY to
# conditional at most; never a definitive single assignment.
# ---------------------------------------------------------------------------
def test_si_s3_near_boundary_conditional_at_most() -> None:
    d = district(box(0, 0, 400, 400), label="R5")
    rec = compose_lot_intersection(
        lot(box(380, 100, 420, 140)),  # straddles the x=400 edge, all within band
        [d],
        ztldb_assignment=ztldb("R5"),
        ztldb_status="ok",
    )
    assert rec.pairs[0].pair_class == PAIR_NEAR_BOUNDARY_UNCERTAIN
    # Exact geometric result preserved separately from the class.
    assert rec.pairs[0].raw_intersection_sq_ft == pytest.approx(800.0, rel=1e-9)
    # Uncertainty is NEVER collapsed; ZTLDB corroboration is display-only.
    assert rec.lot_overall_class == LOT_BOUNDARY_UNCERTAIN
    assert rec.crosscheck.outcome == XCHK_AGREEMENT
    assert rec.crosscheck.display_upgrade == "conditional"
    assert rec.professional_review_required is True
    assert_vocab(rec)


# ---------------------------------------------------------------------------
# SI-S4 sliver: sliver_ambiguous, exact sliver preserved, never suppressed;
# and the minor_portion flag on a small firm share (pair-level, precise).
# ---------------------------------------------------------------------------
def test_si_s4_sliver_ambiguous_preserved() -> None:
    big = district(box(0, 0, 400, 400), label="R5")  # lot firmly inside
    grazing = district(box(190, 0, 590, 400), label="R6")  # grazes lot within band
    rec = compose_lot_intersection(lot(box(100, 100, 200, 200)), [big, grazing], ztldb_status="ok")
    pair_b = next(p for p in rec.pairs if p.district_label == "R6")
    assert pair_b.pair_class == PAIR_SLIVER_AMBIGUOUS
    assert pair_b.raw_intersection_sq_ft > 0.0  # exact sliver preserved, not suppressed
    assert pair_b.firm_intersection_sq_ft == 0.0
    assert rec.lot_overall_class == LOT_SLIVER_AMBIGUOUS
    assert rec.professional_review_required is True
    assert_vocab(rec)


def test_si_s4_minor_portion_flag_not_suppressed() -> None:
    # Huge lot; a small fully-contained district gives a firm share < 2%.
    lot_shape = canonical_to_shapely(box(0, 0, 10000, 10000))
    small = canonical_to_shapely(box(0, 0, 1000, 1000))
    pair = classify_pair(
        lot_shape,
        lot_shape.area,
        layer="nyzd",
        family="base_zoning",
        district_label="R5",
        district_shape=small,
        lot_accuracy=MAPPLUTO_LOT_ACCURACY,
        district_accuracy=layer_accuracy("nyzd"),
    )
    assert pair.pair_class == PAIR_SPLIT_CONFIDENT
    assert 0.0 < (pair.firm_intersection_sq_ft / lot_shape.area) < 0.02
    assert pair.minor_portion is True
    assert pair.firm_intersection_sq_ft > 0.0  # never suppressed


# ---------------------------------------------------------------------------
# SI-S5 ZTLDB cross-check: agreement / ordering-disagreement / set-conflict
# ---------------------------------------------------------------------------
def test_si_s5_ordering_disagreement_conditional() -> None:
    a = district(box(0, 0, 200, 400), label="R5")
    b = district(box(200, 0, 400, 400), label="R6")
    rec = compose_lot_intersection(
        lot(box(50, 100, 300, 300)),  # A gets the larger share
        [a, b],
        ztldb_assignment=ztldb("R6", "R5"),  # ZTLDB order reversed
        ztldb_status="ok",
    )
    assert rec.lot_overall_class == LOT_SPLIT_LOT_CONFIDENT
    assert rec.crosscheck.outcome == XCHK_ORDERING_DISAGREEMENT
    assert rec.crosscheck.display_upgrade == "conditional"


def test_si_s5_set_conflict_is_data_conflict_with_vintage_skew() -> None:
    rec = compose_lot_intersection(
        lot(box(100, 100, 200, 200)),
        [district(box(0, 0, 400, 400), label="R5")],
        ztldb_assignment=ztldb("M1-1"),  # different district set
        ztldb_status="ok",
        ztldb_source_vintage="2026-04-05",
        district_source_vintage="2026-07-01",
    )
    assert rec.crosscheck.outcome == XCHK_SET_CONFLICT
    assert rec.lot_overall_class == LOT_DATA_CONFLICT
    assert rec.crosscheck.possible_vintage_skew is True
    assert rec.professional_review_required is True


# ---------------------------------------------------------------------------
# SI-S6 / SI-CF3 coverage honesty: same-family gap -> explicit unassigned_area
# ---------------------------------------------------------------------------
def test_si_s6_base_gap_emits_unassigned_area() -> None:
    # Lot extends well past its only base-zoning district -> real coverage gap.
    rec = compose_lot_intersection(
        lot(box(0, 0, 400, 200)),
        [district(box(0, 0, 200, 200), label="R5")],
        ztldb_status="ok",
    )
    families = {u["family"] for u in rec.unassigned_area}
    assert "base_zoning" in families
    base_audit = next(c for c in rec.coverage_audits if c.family == "base_zoning")
    assert base_audit.status == AUDIT_GAPS_DETECTED
    assert base_audit.unassigned_area_sq_ft == pytest.approx(40000.0, rel=1e-6)


# ---------------------------------------------------------------------------
# SI-CF1 cross-family stacking is NOT overlap_area
# ---------------------------------------------------------------------------
def test_si_cf1_cross_family_stacking_not_overlap() -> None:
    nyzd = district(box(0, 0, 400, 400), label="R5", layer="nyzd")
    nysp = district(box(0, 0, 400, 400), label="Special-1", layer="nysp")
    rec = compose_lot_intersection(lot(box(100, 100, 200, 200)), [nyzd, nysp], ztldb_status="ok")
    assert rec.overlap_area == []  # base + special covering the same area is legitimate
    fam_status = {c.family: c.status for c in rec.coverage_audits}
    assert fam_status["base_zoning"] == AUDIT_COMPLETE_NONOVERLAPPING
    assert fam_status["special_purpose_district"] == AUDIT_NOT_APPLICABLE


# ---------------------------------------------------------------------------
# SI-CF2 overlay absence is NOT unassigned
# ---------------------------------------------------------------------------
def test_si_cf2_overlay_partial_absence_not_unassigned() -> None:
    nyzd = district(box(0, 0, 400, 400), label="R5", layer="nyzd")
    nyco = district(box(0, 0, 150, 400), label="C1-4", layer="nyco")  # covers only part of the lot
    rec = compose_lot_intersection(lot(box(0, 0, 400, 200)), [nyzd, nyco], ztldb_status="ok")
    overlay_unassigned = [u for u in rec.unassigned_area if u["family"] == "commercial_overlay"]
    assert overlay_unassigned == []  # overlay absence over part of the lot is expected
    overlay_audit = next(c for c in rec.coverage_audits if c.family == "commercial_overlay")
    assert overlay_audit.status == AUDIT_NOT_APPLICABLE


# ---------------------------------------------------------------------------
# SI-CF4 genuine same-family overlap -> explicit overlap_area
# ---------------------------------------------------------------------------
def test_si_cf4_same_family_overlap_emits_overlap_area() -> None:
    a = district(box(0, 0, 300, 400), label="R5", layer="nyzd")
    b = district(box(200, 0, 400, 400), label="R6", layer="nyzd")  # overlaps A on x[200,300]
    rec = compose_lot_intersection(lot(box(0, 0, 400, 400)), [a, b], ztldb_status="ok")
    base_overlap = [o for o in rec.overlap_area if o["family"] == "base_zoning"]
    assert base_overlap, "same-family base overlap must be explicit"
    base_audit = next(c for c in rec.coverage_audits if c.family == "base_zoning")
    assert base_audit.status == AUDIT_OVERLAPS_DETECTED


# ---------------------------------------------------------------------------
# Fail-safe hardening from independent review (G4 F1 + G3 obs 1/2)
# ---------------------------------------------------------------------------
def test_f1_non_base_overlay_uncertainty_triggers_review() -> None:
    """G4 F1: a real positional uncertainty on a NON-base family (here a
    commercial overlay grazing the lot within the band) must route to review
    even when the base assignment is confident - without collapsing the pair."""
    base = district(box(0, 0, 400, 400), label="R5", layer="nyzd")
    overlay = district(box(190, 0, 590, 400), label="C1-4", layer="nyco")  # grazes lot in-band
    rec = compose_lot_intersection(
        lot(box(100, 100, 200, 200)),
        [base, overlay],
        ztldb_assignment=ztldb("R5"),
        ztldb_status="ok",
    )
    overlay_pair = next(p for p in rec.pairs if p.district_label == "C1-4")
    assert overlay_pair.pair_class == PAIR_NEAR_BOUNDARY_UNCERTAIN
    assert overlay_pair.raw_intersection_sq_ft > 0.0  # preserved, not collapsed
    assert rec.lot_overall_class == LOT_SINGLE_DISTRICT_CONFIDENT  # base still confident
    assert rec.professional_review_required is True  # but the overlay uncertainty is flagged
    assert any("non-base positional uncertainty" in r for r in rec.review_reasons)
    assert_vocab(rec)


def test_coverage_anomaly_triggers_review_in_isolation() -> None:
    """G3 obs 2: a same-family coverage anomaly must force review even when the
    lot class is otherwise confident and ZTLDB agrees (no other trigger)."""
    a = district(box(0, 0, 300, 400), label="R5", layer="nyzd")
    b = district(box(200, 0, 400, 400), label="R6", layer="nyzd")  # overlaps A on x[200,300]
    rec = compose_lot_intersection(
        lot(box(0, 0, 400, 400)), [a, b], ztldb_assignment=ztldb("R5", "R6"), ztldb_status="ok"
    )
    assert rec.lot_overall_class == LOT_SPLIT_LOT_CONFIDENT  # not uncertain
    assert rec.crosscheck.outcome != XCHK_ZTLDB_ABSENT  # ZTLDB agrees; not the trigger
    assert rec.professional_review_required is True
    assert any("coverage anomaly" in r for r in rec.review_reasons)


def test_g3_obs1_simultaneous_overlap_and_gap_both_explicit() -> None:
    """G3 obs 1: when a base family has BOTH a same-family overlap AND a coverage
    gap, both quantities stay explicit; neither suppresses the other."""
    a = district(box(0, 0, 300, 400), label="R5", layer="nyzd")
    b = district(box(200, 0, 400, 400), label="R6", layer="nyzd")  # overlap x[200,300]
    rec = compose_lot_intersection(  # lot extends to x=600 -> x[400,600] uncovered gap
        lot(box(0, 0, 600, 400)), [a, b], ztldb_assignment=ztldb("R5", "R6"), ztldb_status="ok"
    )
    base_unassigned = [u for u in rec.unassigned_area if u["family"] == "base_zoning"]
    base_overlap = [o for o in rec.overlap_area if o["family"] == "base_zoning"]
    assert base_unassigned, "coverage gap must remain explicit"
    assert base_overlap, "same-family overlap must remain explicit"
    assert base_unassigned[0]["unassigned_area_sq_ft"] == pytest.approx(80000.0, rel=1e-6)
    assert base_overlap[0]["overlap_area_sq_ft"] == pytest.approx(40000.0, rel=1e-6)


# ---------------------------------------------------------------------------
# SI-CF5 / SI-S9 no Verified label anywhere (grep/test-provable)
# ---------------------------------------------------------------------------
def test_si_cf5_no_verified_label_in_any_field() -> None:
    scenarios = [
        compose_lot_intersection(
            lot(box(100, 100, 200, 200)),
            [district(box(0, 0, 400, 400))],
            ztldb_assignment=ztldb("R5"),
            ztldb_status="ok",
        ),
        compose_lot_intersection(
            lot(box(380, 100, 420, 140)),
            [district(box(0, 0, 400, 400))],
            ztldb_assignment=ztldb("R5"),
            ztldb_status="ok",
        ),
        compose_lot_intersection(
            lot(box(0, 0, 400, 200)), [district(box(0, 0, 200, 200))], ztldb_status="ok"
        ),
    ]
    for rec in scenarios:
        assert_vocab(rec)
        assert rec.crosscheck.outcome != "verified"
        # No field value anywhere equals a verified/confirmed label.
        blob = json.dumps(rec.as_dict()).lower()
        for banned in ('"verified"', "confirmed_assignment", "confirmed_split"):
            assert banned not in blob


def test_si_cf5_source_has_no_verified_status_literal() -> None:
    # No module may emit a bare ``"verified"`` string literal as a status/class
    # value. The word appears only inside longer disclaimer strings ("not a
    # Verified determination") and prose, never as a standalone quoted literal.
    import re

    standalone_verified = re.compile(r"""["']verified["']""", re.IGNORECASE)
    spatial_dir = Path(__file__).resolve().parents[2] / "app" / "spatial"
    for py in spatial_dir.glob("*.py"):
        text = py.read_text(encoding="utf-8")
        assert not standalone_verified.search(text), f"bare 'verified' literal in {py.name}"


# ---------------------------------------------------------------------------
# SI-CF6 shares never renormalized; point shares not forced to 100%
# ---------------------------------------------------------------------------
def test_si_cf6_shares_not_renormalized() -> None:
    rec = compose_lot_intersection(
        lot(box(0, 0, 400, 200)),
        [district(box(0, 0, 200, 200), label="R5")],  # covers half the lot
        ztldb_status="ok",
    )
    base_pairs = [p for p in rec.pairs if p.family == "base_zoning"]
    total_point = sum(p.share_point for p in base_pairs)
    assert total_point == pytest.approx(0.5, rel=1e-6)  # NOT forced up to 1.0
    for p in base_pairs:
        # share_point is exactly raw/lot_area, never rescaled.
        assert p.share_point == pytest.approx(p.raw_intersection_sq_ft / p.lot_area_sq_ft, rel=1e-9)


# ---------------------------------------------------------------------------
# SI-CF7 coverage-audit status is internal (present per family, not a contract)
# ---------------------------------------------------------------------------
def test_si_cf7_audit_status_internal_no_contract_import() -> None:
    rec = compose_lot_intersection(
        lot(box(100, 100, 200, 200)), [district(box(0, 0, 400, 400))], ztldb_status="ok"
    )
    assert all(c.status in _AUDIT_STATUSES for c in rec.coverage_audits)
    # The engine never imports a published contract schema (M2-T012 integrates).
    spatial_dir = Path(__file__).resolve().parents[2] / "app" / "spatial"
    for py in spatial_dir.glob("*.py"):
        text = py.read_text(encoding="utf-8")
        assert "packages/contracts" not in text
        assert "_contract_schemas" not in text
        assert "app.profile" not in text


# ---------------------------------------------------------------------------
# SI-S7 invalid / degenerate geometry
# ---------------------------------------------------------------------------
def test_si_s7_degenerate_narrow_district_band_exceeds_feature_width() -> None:
    narrow = district(box(0, 0, 400, 50), label="R5")  # 50 ft tall < 2*band(80)
    rec = compose_lot_intersection(lot(box(50, 10, 150, 40)), [narrow], ztldb_status="ok")
    pair = rec.pairs[0]
    assert pair.band_exceeds_feature_width is True
    assert pair.pair_class != PAIR_INTERIOR_CONFIDENT  # confidence impossible by construction
    assert rec.professional_review_required is True


def test_si_s7_invalid_lot_geometry_review_no_fabricated_assignment() -> None:
    rec = compose_lot_intersection(
        lot(None, status="invalid_geometry", review=True),
        [district(box(0, 0, 400, 400))],
        ztldb_assignment=ztldb("R5"),
        ztldb_status="ok",
    )
    assert rec.lot_overall_class == LOT_INVALID_GEOMETRY_REVIEW
    assert rec.pairs == []  # nothing fabricated
    assert rec.professional_review_required is True


# ---------------------------------------------------------------------------
# SI-S8 assumed-accuracy fail-safe: 2x-band sensitivity flip -> review
# ---------------------------------------------------------------------------
def test_si_s8_sensitivity_flip_triggers_review() -> None:
    d = district(box(0, 0, 400, 400), label="R5")
    # Lot inside erode(40) but not inside erode(80): interior at band, flips at 2x.
    rec = compose_lot_intersection(
        lot(box(50, 50, 350, 350)), [d], ztldb_assignment=ztldb("R5"), ztldb_status="ok"
    )
    pair = rec.pairs[0]
    assert pair.accuracy_basis_assumed is True  # MapPLUTO lot accuracy is assumed (V1)
    assert pair.sensitivity_flip is True
    assert rec.professional_review_required is True


def test_si_s8_accuracy_provenance_documented_vs_assumed() -> None:
    rec = compose_lot_intersection(
        lot(box(100, 100, 200, 200)), [district(box(0, 0, 400, 400))], ztldb_status="ok"
    )
    bases = {r["applies_to"]: r["basis"] for r in rec.accuracy_records}
    assert bases["nyc-dcp-zoning-features:nyzd"] == "documented"
    assert bases["nyc-dcp-mappluto-arcgis:MAPPLUTO"] == "assumed"


# ---------------------------------------------------------------------------
# SI-S10 reproducibility + pins + policy version
# ---------------------------------------------------------------------------
def test_si_s10_reproducible_and_pinned() -> None:
    args = (
        lot(box(50, 100, 350, 300)),
        [district(box(0, 0, 200, 400), label="R5"), district(box(200, 0, 400, 400), label="R6")],
    )
    kwargs = {"ztldb_assignment": ztldb("R5", "R6"), "ztldb_status": "ok"}
    first = compose_lot_intersection(*args, **kwargs).as_dict()
    second = compose_lot_intersection(*args, **kwargs).as_dict()
    assert first == second
    assert first["policy"]["policy_version"] == policy_snapshot()["policy_version"]
    assert shapely.__version__ == "2.0.7"
    assert ".".join(str(p) for p in geos_version) == "3.11.4"
    assert first["policy"]["combination_rule"] == "linear_sum"


# ---------------------------------------------------------------------------
# SI-S11 missing input fails typed and visible
# ---------------------------------------------------------------------------
def test_si_s11_missing_district_layer_no_fabricated_assignment() -> None:
    rec = compose_lot_intersection(lot(box(100, 100, 200, 200)), [], ztldb_status="no_record")
    assert rec.lot_overall_class == LOT_BOUNDARY_UNCERTAIN
    assert rec.pairs == []
    assert rec.crosscheck.outcome == XCHK_ZTLDB_ABSENT
    assert rec.professional_review_required is True


def test_band_is_linear_sum_of_two_accuracies() -> None:
    assert combined_band_ft(MAPPLUTO_LOT_ACCURACY, layer_accuracy("nyzd")) == pytest.approx(40.0)
    doubled = SourceAccuracy(value_ft=30.0, basis="assumed", citation="t", applies_to="t")
    assert combined_band_ft(doubled, layer_accuracy("nyzd")) == pytest.approx(50.0)


# ---------------------------------------------------------------------------
# Real committed connector fixtures (by reference): prove real-data consumption
# ---------------------------------------------------------------------------
def _fixture_features(relpath: str) -> list:
    """Parse the committed connector fixture and return its inner esri features
    (the fixtures wrap the response in ``response_body_raw``)."""
    doc = json.loads((FIX / relpath).read_text(encoding="utf-8"))
    return json.loads(doc["response_body_raw"])["features"]


def _real_r32_district_canonical() -> list:
    feature = _fixture_features("zoning_features/ZF03_query_nyzd_single_R3-2.json")[0]
    return analyze_lot_geometry(feature["geometry"], crs=dict(CRS_STAMP)).canonical_geometry


def test_real_nyzd_r32_fixture_interior_lot() -> None:
    district_canonical = _real_r32_district_canonical()
    # Deep interior point probed from the real R3-2 polygon (connector test).
    x, y = 997482.04, 163293.94
    rec = compose_lot_intersection(
        lot(box(x - 25, y - 25, x + 25, y + 25)),
        [district(district_canonical, label="R3-2")],
        ztldb_assignment=ztldb("R3-2"),
        ztldb_status="ok",
    )
    assert rec.lot_overall_class == LOT_SINGLE_DISTRICT_CONFIDENT
    assert rec.pairs[0].district_label == "R3-2"
    assert rec.crosscheck.outcome == XCHK_AGREEMENT
    assert_vocab(rec)


def test_real_holed_lot_fixture_consumed_deterministically() -> None:
    feature = _fixture_features("mappluto_geometry/MPG06_lot_holes_1000010010.json")[0]
    assessment = analyze_lot_geometry(feature["geometry"], crs=dict(CRS_STAMP))
    lot_in = lot(assessment.canonical_geometry, bbl="1000010010", status=assessment.status)
    d = _real_r32_district_canonical()
    r1 = compose_lot_intersection(lot_in, [district(d, label="R3-2")], ztldb_status="ok").as_dict()
    r2 = compose_lot_intersection(lot_in, [district(d, label="R3-2")], ztldb_status="ok").as_dict()
    assert r1 == r2  # deterministic on the real holed polygon
    assert r1["lot_overall_class"] in _LOT_CLASSES


# ---------------------------------------------------------------------------
# Adapter: operates directly on accepted connector domain-model shapes
# ---------------------------------------------------------------------------
def test_adapter_consumes_connector_shaped_objects() -> None:
    raw_feature = _fixture_features("zoning_features/ZF03_query_nyzd_single_R3-2.json")[0]
    layer_result = SimpleNamespace(
        layer="nyzd",
        features=[raw_feature],
        object_id_field="OBJECTID",
        normalized_digest="digest-zf03",
        retrieved_at="2026-07-20T00:00:00Z",
        source_data_last_edited="2026-07-01T00:00:00Z",
    )
    features = district_features_from_layer_result(layer_result)
    assert len(features) == 1
    assert features[0].layer == "nyzd"
    assert features[0].family == "base_zoning"
    assert features[0].label == "R3-2"
    assert features[0].canonical_geometry is not None

    # Lot side: a LotGeometryResult-shaped object with a real assessed geometry.
    mpg_feature = _fixture_features("mappluto_geometry/MPG06_lot_holes_1000010010.json")[0]
    assessment = analyze_lot_geometry(mpg_feature["geometry"], crs=dict(CRS_STAMP))
    lot_result = SimpleNamespace(
        outcome="single_feature",
        geometry=assessment,
        review_required=False,
        requested_bbl="1000010010",
        area_sq_ft=assessment.area_sq_ft,
        retrieved_at="2026-07-20T00:00:00Z",
        normalized_digest="digest-mpg06",
        source_data_last_edited="2026-07-01T00:00:00Z",
        crs=dict(CRS_STAMP),
    )
    lot_in = lot_input_from_result(lot_result)
    assert lot_in.bbl == "1000010010"
    assert lot_in.canonical_geometry is not None
    assert lot_in.review_required is False

    rec = compose_from_connectors(lot_result, [layer_result], None)
    assert rec.bbl == "1000010010"
    assert_vocab(rec)


def test_adapter_lot_no_feature_maps_to_review() -> None:
    lot_result = SimpleNamespace(
        outcome="no_feature",
        geometry=None,
        review_required=False,
        requested_bbl="1000019999",
        area_sq_ft=None,
        retrieved_at="2026-07-20T00:00:00Z",
        normalized_digest=None,
        source_data_last_edited=None,
        crs=dict(CRS_STAMP),
    )
    lot_in = lot_input_from_result(lot_result)
    assert lot_in.geometry_status == "no_feature"
    assert lot_in.review_required is True
    rec = compose_lot_intersection(lot_in, [district(box(0, 0, 400, 400))], ztldb_status="ok")
    assert rec.lot_overall_class == LOT_INVALID_GEOMETRY_REVIEW
