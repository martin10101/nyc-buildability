"""The truth table (task M5-T132): one case per input state of every result that
``decide_result_ways`` decides, pinning (a) the WAY of every state (S6: a way never changes),
(b) the gap KIND, and (c) the meaning-bearing parts of the reason - the condition that really
fails, the measured value, and the ABSENCE of the words of a condition that holds (never a whole
sentence, so a later wording polish does not weaken the check).

The repaired rows are the two the owner's outside reviewer named (S1 evidence-not-in-one,
S2 corner-angle-fails) plus the rest of the same fault surface found by the inventory: the
rear-yard interior/through reason, the corner reach/angle not-measured texts, the rear-yard
waiver's three failing states, the standard unit limit's not-given text, the qualifying-senior
reason, and the whole-answer reason when its values are withheld for more than one reason.

Expected outcomes are the orchestrator's readings O19/O20 and the work order's section 5, never
the module. The 'before' column of every row (the untouched module at the claim head) is in the
producer report; the red proof for S1 and S2 is recorded there too.
"""

from __future__ import annotations

import pytest

from app.scenario.three_answers.result_way_inputs import (
    AreaAgreement,
    Checked,
    CornerReach,
    DensityKnowledge,
    LotAreaFigures,
    LotType,
    OverlayResultSupport,
    ReachMeasurements,
    ReachValue,
    Recorded,
    ResultFamily,
    StreetReach,
)
from app.scenario.three_answers.result_ways import (
    Conditional,
    Settled,
    Withheld,
    decide_result_ways,
)

from .test_result_ways_lib import base_inputs, k20, make_reach, plain_inputs, support_all


# ---------------------------------------------------------------------------------- reach helpers
def _corner_reach(corner_ft, angle_deg, *, reach_known=True, angle_known=True):
    """A corner lot's reach with the corner point's reach and/or angle optionally unknown. The
    street-line reaches are two known frontages (so only the corner measurements vary)."""
    corner = CornerReach(
        ReachValue(corner_ft if reach_known else None),
        ReachValue(angle_deg if angle_known else None),
    )
    return ReachMeasurements(
        (StreetReach("street A", ReachValue(40.0)), StreetReach("street B", ReachValue(50.0))),
        corner,
    )


def _street_reach_unknown():
    """A corner lot whose site geometry exists but one street-line reach is unknown (no_outline
    for coverage; the corner measurements are present)."""
    return ReachMeasurements(
        (StreetReach("street A", ReachValue(None)), StreetReach("street B", ReachValue(50.0))),
        CornerReach(ReachValue(50.0), ReachValue(90.0)),
    )


def _overlay_family(family, support):
    """A benchmark overlay case where every family is supported except ``family``, which carries
    ``support`` (an OverlayResultSupport or None-for-missing)."""
    mapping = {f: OverlayResultSupport(True) for f in ResultFamily}
    if support is None:
        del mapping[family]
    else:
        mapping[family] = support
    return base_inputs(overlay_support=mapping, **k20(True))


# ---------------------------------------------------------------------------------- the table
# Each row: id, a thunk that builds the inputs, the focal result key, the expected WAY type, the
# expected gap_kind (None for a shown way), the substrings the reason MUST contain, and the
# substrings the reason MUST NOT contain (the words of a condition that holds).
WAY_W, WAY_C, WAY_S = Withheld, Conditional, Settled

_TABLE = [
    # --- blanket withholds (reading O2/O6/O11): focal a representative zoning result ---
    ("B1_district_none", lambda: plain_inputs(district=None), "min_base_height",
     WAY_W, "missing_information", ["zoning district was not given"], []),
    ("B2_district_not_r6b", lambda: plain_inputs(district="R5"), "min_base_height",
     WAY_W, "work_owed", ["R6B", "R5"], []),
    ("B3_special_purpose_present", lambda: plain_inputs(
        special_purpose_district=Recorded.PRESENT, **k20(True)), "min_base_height",
     WAY_W, "work_owed", ["special purpose district"], []),
    ("B4_special_purpose_not_read", lambda: plain_inputs(
        special_purpose_district=Recorded.NOT_READ, **k20(True)), "min_base_height",
     WAY_W, "missing_information", ["not read"], []),
    ("B5_split_present", lambda: plain_inputs(
        split_by_district_line=Recorded.PRESENT, **k20(True)), "min_base_height",
     WAY_W, "work_owed", ["split by a district line"], []),
    ("B6_split_not_read", lambda: plain_inputs(
        split_by_district_line=Recorded.NOT_READ, **k20(True)), "min_base_height",
     WAY_W, "missing_information", ["split-lot column", "not read"], []),
    ("B7_k20_present", lambda: plain_inputs(waterfront=Checked.PRESENT), "min_base_height",
     WAY_W, "work_owed", ["recorded as present"], []),
    # --- overlay block per family (reading O5) ---
    ("OB1_overlay_not_read", lambda: base_inputs(
        commercial_overlay=Recorded.NOT_READ, overlay_support=None, **k20(True)),
     "max_lot_coverage", WAY_W, "missing_information",
     ["commercial-overlay column", "not read"], []),
    ("OB2_overlay_present_no_map", lambda: base_inputs(overlay_support=None, **k20(True)),
     "max_lot_coverage", WAY_W, "work_owed",
     ["recorded commercial overlay", "no independent reading"], []),
    ("OB3_overlay_family_missing", lambda: _overlay_family(ResultFamily.COVERAGE, None),
     "max_lot_coverage", WAY_W, "work_owed", ["no independent reading"], []),
    ("OB5_overlay_not_supported_named", lambda: _overlay_family(
        ResultFamily.COVERAGE, OverlayResultSupport(
            False, "the coverage reading under the overlay", ("ZR 34-111",))),
     "max_lot_coverage", WAY_W, "work_owed", ["the coverage reading under the overlay"], []),
    ("OB6_overlay_not_supported_fallback", lambda: _overlay_family(
        ResultFamily.COVERAGE, OverlayResultSupport(False)),
     "max_lot_coverage", WAY_W, "work_owed", ["Article III sections"], []),
    ("OB4_overlay_supported", lambda: base_inputs(overlay_support=support_all(True), **k20(True)),
     "min_base_height", WAY_S, None, [], []),
    # --- floor area ---
    ("FA1_no_area", lambda: plain_inputs(area=LotAreaFigures(None, None, None), **k20(True)),
     "max_residential_far", WAY_W, "missing_information", ["No lot area is recorded"], []),
    ("FA2_inclusionary_present", lambda: plain_inputs(
        inclusionary_housing_area=Recorded.PRESENT, **k20(True)),
     "max_residential_far", WAY_W, "work_owed", ["inclusionary housing area"], []),
    ("FA3_inclusionary_not_read", lambda: plain_inputs(
        inclusionary_housing_area=Recorded.NOT_READ, **k20(True)),
     "max_residential_far", WAY_W, "missing_information", ["was not read"], []),
    ("FA4_settled", lambda: plain_inputs(**k20(True)), "max_residential_far", WAY_S, None, [], []),
    ("FA5_conditional_k20", lambda: plain_inputs(**k20(False)),
     "max_residential_far", WAY_C, None, [], []),
    ("FA6_area_disagrees", lambda: plain_inputs(
        area=LotAreaFigures(10075.0, AreaAgreement.DISAGREES, 10388.0), **k20(True)),
     "max_residential_far", WAY_C, None, [], []),
    ("FA7_area_could_not_compare", lambda: plain_inputs(
        area=LotAreaFigures(10075.0, AreaAgreement.COULD_NOT_COMPARE, None), **k20(True)),
     "max_residential_far", WAY_C, None, [], []),
    ("FA8_area_agreement_none", lambda: plain_inputs(
        area=LotAreaFigures(5000.0, None, None), **k20(True)),
     "max_residential_far", WAY_C, None, [], []),
    # --- heights ---
    ("H1_flood_present", lambda: plain_inputs(flood_zone=Recorded.PRESENT, **k20(True)),
     "min_base_height", WAY_W, "work_owed", ["flood zone"], []),
    ("H2_flood_not_read", lambda: plain_inputs(flood_zone=Recorded.NOT_READ, **k20(True)),
     "min_base_height", WAY_W, "missing_information", ["flood-zone column", "not read"], []),
    ("H3_settled", lambda: plain_inputs(**k20(True)), "min_base_height", WAY_S, None, [], []),
    ("H4_conditional", lambda: plain_inputs(**k20(False)), "min_base_height", WAY_C, None, [], []),
    # --- coverage ---
    ("C1_large_lot", lambda: plain_inputs(large_lot_threshold_met=True, **k20(True)),
     "max_lot_coverage", WAY_W, "work_owed", ["different maximum lot coverage", "ZR 23-362"], []),
    ("C2_lot_type_none", lambda: plain_inputs(
        lot_type=None, reach=make_reach((("a", 40.0), ("b", 50.0)), 90.0, 50.0), **k20(True)),
     "max_lot_coverage", WAY_W, "missing_information", ["lot type is not given"], []),
    ("C3_interior", lambda: plain_inputs(lot_type=LotType.INTERIOR, reach=None, **k20(True)),
     "max_lot_coverage", WAY_W, "work_owed", ["ZR 23-363"], []),
    ("C3b_through", lambda: plain_inputs(lot_type=LotType.THROUGH, reach=None, **k20(True)),
     "max_lot_coverage", WAY_W, "work_owed", ["ZR 23-363"], []),
    ("C4_no_outline", lambda: plain_inputs(reach=None, **k20(True)),
     "max_lot_coverage", WAY_W, "missing_information", ["not measured"], []),
    ("C4b_street_reach_unknown", lambda: plain_inputs(reach=_street_reach_unknown(), **k20(True)),
     "max_lot_coverage", WAY_W, "missing_information", ["not measured"], []),
    ("C5_reaches_beyond", lambda: plain_inputs(
        reach=make_reach((("a", 100.0), ("b", 150.0)), 90.0, 180.28), **k20(True)),
     "max_lot_coverage", WAY_W, "work_owed", ["150 ft", "beyond the corner-lot portion"], []),
    ("C6_large_lot_none", lambda: plain_inputs(
        reach=make_reach((("a", 80.0), ("b", 60.0)), 90.0, 100.0),
        large_lot_threshold_met=None, **k20(True)),
     "max_lot_coverage", WAY_W, "missing_information",
     ["was not compared", "recorded lot area"], []),
    ("C7_settled", lambda: plain_inputs(
        reach=make_reach((("a", 80.0), ("b", 60.0)), 90.0, 100.0), **k20(True)),
     "max_lot_coverage", WAY_S, None, [], []),
    ("C8_conditional", lambda: plain_inputs(
        reach=make_reach((("a", 80.0), ("b", 60.0)), 90.0, 100.0), **k20(False)),
     "max_lot_coverage", WAY_C, None, [], []),
    # --- rear yard (the repaired surface) ---
    ("RY1_lot_type_none", lambda: plain_inputs(
        lot_type=None, reach=make_reach((("a", 40.0), ("b", 50.0)), 90.0, 50.0), **k20(True)),
     "rear_yard", WAY_W, "missing_information", ["lot type is not given"], []),
    ("RY2_interior", lambda: plain_inputs(lot_type=LotType.INTERIOR, reach=None, **k20(True)),
     "rear_yard", WAY_W, "work_owed",
     ["corner rear-yard waiver does not apply", "does not yet work out", "ZR 23-342"],
     ["which are not given"]),
    ("RY3_corner_none", lambda: plain_inputs(reach=None, **k20(True)),
     "rear_yard", WAY_W, "missing_information", ["not measured"], []),
    ("RY4_reach_unknown", lambda: plain_inputs(
        reach=_corner_reach(50.0, 90.0, reach_known=False), **k20(True)),
     "rear_yard", WAY_W, "missing_information", ["far corner's reach", "not measured"], []),
    ("RY5_angle_unknown", lambda: plain_inputs(
        reach=_corner_reach(50.0, 90.0, angle_known=False), **k20(True)),
     "rear_yard", WAY_W, "missing_information", ["angle", "not measured"],
     ["reach from the point where the two street lines meet is not measured"]),
    ("RY6_both_unknown", lambda: plain_inputs(
        reach=_corner_reach(50.0, 90.0, reach_known=False, angle_known=False), **k20(True)),
     "rear_yard", WAY_W, "missing_information",
     ["far corner's reach", "angle", "not measured"], []),
    ("RY7_distance_fails", lambda: plain_inputs(
        reach=make_reach((("a", 40.0), ("b", 50.0)), 90.0, 107.70), **k20(True)),
     "rear_yard", WAY_W, "work_owed",
     ["107.70 ft", "beyond the rear-yard waiver area", "90 degrees", "within the waiver's limit"],
     ["more than the rear-yard waiver's limit"]),
    ("RY8_angle_fails", lambda: plain_inputs(
        reach=make_reach((("a", 40.0), ("b", 50.0)), 140.0, 90.0), **k20(True)),
     "rear_yard", WAY_W, "work_owed",
     ["140 degrees", "more than the rear-yard waiver's limit of 135 degrees",
      "within 100 ft of it"],
     ["beyond the rear-yard waiver area"]),
    ("RY9_both_fail", lambda: plain_inputs(
        reach=make_reach((("a", 40.0), ("b", 50.0)), 140.0, 144.60), **k20(True)),
     "rear_yard", WAY_W, "work_owed",
     ["144.60 ft", "beyond the rear-yard waiver area", "140 degrees",
      "more than the rear-yard waiver's limit"], []),
    ("RY10_settled", lambda: plain_inputs(
        reach=make_reach((("a", 80.0), ("b", 60.0)), 90.0, 100.0), **k20(True)),
     "rear_yard", WAY_S, None, [], []),
    ("RY11_conditional", lambda: plain_inputs(
        reach=make_reach((("a", 80.0), ("b", 60.0)), 90.0, 100.0), **k20(False)),
     "rear_yard", WAY_C, None, [], []),
    # --- setback ---
    ("SB1_setback", lambda: plain_inputs(**k20(True)),
     "setback_above_base", WAY_W, "work_owed", ["not covered", "ZR 23-433"], []),
    # --- unit limit standard (the repaired surface) ---
    ("US1_no_area", lambda: plain_inputs(area=LotAreaFigures(None, None, None), **k20(True)),
     "legal_unit_limit_standard", WAY_W, "missing_information", ["No lot area is recorded"], []),
    ("US2_user_statement", lambda: plain_inputs(
        special_density=DensityKnowledge.USER_STATEMENT_NOT_IN_ONE, **k20(True)),
     "legal_unit_limit_standard", WAY_C, None, [], []),
    ("US3_evidence_in_one", lambda: plain_inputs(
        special_density=DensityKnowledge.EVIDENCE_IN_ONE, **k20(True)),
     "legal_unit_limit_standard", WAY_W, "work_owed",
     ["Evidence records this lot in a special density area"], []),
    ("US4_not_given", lambda: plain_inputs(
        special_density=DensityKnowledge.NOT_GIVEN, **k20(True)),
     "legal_unit_limit_standard", WAY_W, "work_owed",
     ["There is no evidence", "has not been worked out", "conditional result"], []),
    ("US5_evidence_not_in_one", lambda: plain_inputs(
        special_density=DensityKnowledge.EVIDENCE_NOT_IN_ONE, **k20(True)),
     "legal_unit_limit_standard", WAY_W, "work_owed",
     ["Evidence records this lot outside a special density area", "has not been worked out"],
     ["There is no evidence", "no evidence"]),
    # --- unit limit qualifying ---
    ("UA1_affordable", lambda: plain_inputs(**k20(True)),
     "legal_unit_limit_qualifying_affordable", WAY_W, "work_owed",
     ["qualifying affordable housing"], []),
    ("USR1_senior", lambda: plain_inputs(**k20(True)),
     "legal_unit_limit_qualifying_senior", WAY_W, "work_owed",
     ["not set by this formula", "not worked out yet", "ZR 23-52(a)(2)"], []),
    # --- building option ---
    ("BO1_option", lambda: plain_inputs(**k20(True)),
     "achieved_zoning_floor_area", WAY_W, "work_owed", ["rear yard"], []),
]


def _focal(ways, key):
    return next(row.way for row in ways.result_ways() if row.key == key)


@pytest.mark.parametrize(
    "state_id,make_inputs,key,way_type,gap_kind,must_contain,must_not_contain",
    [pytest.param(*row, id=row[0]) for row in _TABLE],
)
def test_every_input_state_of_every_result(
    state_id, make_inputs, key, way_type, gap_kind, must_contain, must_not_contain
):
    """S5/S6: one case per row of the table. The WAY is pinned (so a way never changes), and for
    a withheld way the kind and the meaning-bearing parts of the reason are checked: the condition
    that really fails is named, and the words of a condition that holds are absent."""
    way = _focal(decide_result_ways(make_inputs()), key)
    assert isinstance(way, way_type), f"{state_id}: way is {type(way).__name__}"
    if isinstance(way, Withheld):
        assert way.gap_kind == gap_kind, f"{state_id}: kind {way.gap_kind}"
        for token in must_contain:
            assert token in way.reason, f"{state_id}: {token!r} missing from reason: {way.reason}"
        for token in must_not_contain:
            assert token not in way.reason, f"{state_id}: {token!r} should be absent: {way.reason}"


# ===== the two states the owner's reviewer named (S1, S2), plus the other two O20 states =====
def test_s1_evidence_not_in_one_names_the_evidence_not_the_absence_of_it():
    """S1 / reading O19. Evidence records the lot OUTSIDE a special density area. The standard
    unit limit stays withheld (owed work); the reason states that evidence and NEVER 'there is no
    evidence'; the 'resolved by' names the owed work and NEVER asks for a fact the state holds.
    This test FAILS on the module at the claim head (the reason there is the 'not given' text)."""
    way = _focal(
        decide_result_ways(plain_inputs(
            special_density=DensityKnowledge.EVIDENCE_NOT_IN_ONE, **k20(True))),
        "legal_unit_limit_standard",
    )
    assert isinstance(way, Withheld)
    assert way.gap_kind == "work_owed"
    assert "Evidence records this lot outside a special density area" in way.reason
    assert "no evidence" not in way.reason.lower()
    # the 'resolved by' names the owed work, not a bare fact the state already holds
    assert "sourced fact" not in way.resolved_by.lower()
    assert "worked example" in way.resolved_by


def test_s2_corner_angle_fails_distance_holds_names_the_angle_not_the_distance():
    """S2 / reading O20. The far corner is 90 ft from the corner point (within the 100-foot
    waiver area) and the angle is 140 degrees (over the 135-degree limit). The rear yard stays
    withheld (owed work); the reason names the angle against its limit and says the far corner is
    WITHIN 100 ft, and NEVER says it is beyond the waiver area. FAILS at the claim head (the text
    there blames the distance as beyond the waiver area and never names the angle)."""
    way = _focal(
        decide_result_ways(plain_inputs(
            reach=make_reach((("street A", 40.0), ("street B", 50.0)), 140.0, 90.0), **k20(True))),
        "rear_yard",
    )
    assert isinstance(way, Withheld)
    assert way.gap_kind == "work_owed"
    assert "140 degrees" in way.reason
    assert "135 degrees" in way.reason
    assert "within 100 ft of it" in way.reason
    assert "beyond the rear-yard waiver area" not in way.reason


def test_us4_not_given_resolved_by_names_owed_work_not_a_bare_fact():
    """US4 / R258. With no density evidence the kind is work owed, so the 'resolved by' names the
    owed work and does NOT ask for a bare 'sourced fact' (which, on its own, would not resolve it:
    evidence that the lot is not in such an area stays withheld as owed work, reading O19)."""
    way = _focal(
        decide_result_ways(plain_inputs(
            special_density=DensityKnowledge.NOT_GIVEN, **k20(True))),
        "legal_unit_limit_standard",
    )
    assert isinstance(way, Withheld) and way.gap_kind == "work_owed"
    assert "sourced fact" not in way.resolved_by.lower()
    assert "worked out" in way.resolved_by or "Working out" in way.resolved_by


def test_s3_corner_distance_fails_angle_holds_names_the_distance_not_the_angle():
    """S3 / reading O20. The far corner is 144.60 ft (beyond the 100-foot area) and the angle is
    90 degrees (within the limit). The reason names the distance beyond the area and says the
    angle is within the limit; it never blames the angle."""
    way = _focal(
        decide_result_ways(plain_inputs(
            reach=make_reach((("street A", 40.0), ("street B", 50.0)), 90.0, 144.60), **k20(True))),
        "rear_yard",
    )
    assert isinstance(way, Withheld) and way.gap_kind == "work_owed"
    assert "144.60 ft" in way.reason
    assert "beyond the rear-yard waiver area" in way.reason
    assert "within the waiver's limit" in way.reason
    assert "more than the rear-yard waiver's limit" not in way.reason


def test_s4_corner_both_fail_names_both_conditions():
    """S4 / reading O20. Both fail (far corner 144.60 ft; angle 140 degrees). The reason names
    both the distance beyond the area and the angle over the limit."""
    way = _focal(
        decide_result_ways(plain_inputs(
            reach=make_reach((("street A", 40.0), ("street B", 50.0)), 140.0, 144.60),
            **k20(True))),
        "rear_yard",
    )
    assert isinstance(way, Withheld) and way.gap_kind == "work_owed"
    assert "144.60 ft" in way.reason and "beyond the rear-yard waiver area" in way.reason
    assert "140 degrees" in way.reason
    assert "more than the rear-yard waiver's limit" in way.reason


# ===== the whole-answer reason (multi-reason) =====
def test_whole_answer_reason_names_every_distinct_reason_not_just_the_first():
    """An answer whose values are withheld for MORE THAN ONE reason must not present the first
    value's reason as if it were the only one. Here the envelope's height limits are withheld for
    a flood zone (work owed) and coverage is withheld for the interior-lot rule (ZR 23-363): the
    whole-answer reason names both."""
    ways = decide_result_ways(plain_inputs(
        lot_type=LotType.INTERIOR, reach=None, flood_zone=Recorded.PRESENT, **k20(True)))
    na = ways.permitted_envelope.whole_answer_not_available
    assert na is not None and na.gap_kind == "work_owed"
    assert "for more than one reason" in na.reason
    assert "flood zone" in na.reason
    assert "ZR 23-363" in na.reason


def test_whole_answer_single_reason_keeps_the_single_reason_wording():
    """When every value is withheld for the SAME reason the whole-answer reason gives that one
    reason (not the 'more than one reason' wording)."""
    ways = decide_result_ways(plain_inputs(district=None))
    na = ways.floor_area_allowance.whole_answer_not_available
    assert na is not None
    assert "for more than one reason" not in na.reason
    assert "zoning district was not given" in na.reason
