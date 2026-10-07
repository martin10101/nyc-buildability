"""A test for every input state the module acts on that the round-2 suite did not pin (gate
G4 findings F1-F8), plus the district readings O11 and the K14 label O12 and the explicit
None-agreement branch (G3 note F5). Every expected outcome is the work order sentence or the
orchestrator's reading quoted beside the test, never the module.
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
from app.scenario.three_answers.result_ways import decide_result_ways

from .test_result_ways_lib import (
    base_inputs,
    c2_reach,
    condition_kinds,
    is_conditional,
    is_settled,
    is_withheld,
    k20,
    make_reach,
    plain_inputs,
)


def _coverage(ways):
    return ways.permitted_envelope.values[-1]


def _heights(ways):
    return ways.permitted_envelope.values[:6]


# --------------------------------------------------------------------------- G4-F1 inclusionary
# Gap K19: "the results it can change are withheld (floor area for inclusionary housing)";
# reading O7: a column not read -> withheld as missing information.
def test_f1_inclusionary_present_withholds_floor_area_work_owed():
    ways = decide_result_ways(plain_inputs(
        inclusionary_housing_area=Recorded.PRESENT, **k20(True)))
    assert not ways.floor_area_allowance.is_available
    for value in ways.floor_area_allowance.values:
        assert is_withheld(value) and value.way.gap_kind == "work_owed"
    # the heights do not depend on it: still shown
    assert all(is_settled(h) for h in _heights(ways))


def test_f1_inclusionary_not_read_withholds_floor_area_missing_information():
    ways = decide_result_ways(plain_inputs(
        inclusionary_housing_area=Recorded.NOT_READ, **k20(True)))
    for value in ways.floor_area_allowance.values:
        assert is_withheld(value) and value.way.gap_kind == "missing_information"
        assert "not read" in value.way.reason


# --------------------------------------------------------------------------- G4-F2 flood zone
# Gap K19: "heights for flood"; reading O7: not read -> missing information.
def test_f2_flood_present_withholds_heights_work_owed():
    ways = decide_result_ways(plain_inputs(flood_zone=Recorded.PRESENT, **k20(True)))
    for height in _heights(ways):
        assert is_withheld(height) and height.way.gap_kind == "work_owed"
    # the floor area does not depend on it: still shown
    assert all(is_settled(v) for v in ways.floor_area_allowance.values)


def test_f2_flood_not_read_withholds_heights_missing_information():
    ways = decide_result_ways(plain_inputs(flood_zone=Recorded.NOT_READ, **k20(True)))
    for height in _heights(ways):
        assert is_withheld(height) and height.way.gap_kind == "missing_information"
        assert "not read" in height.way.reason


# --------------------------------------------------------------------------- G4-F3 density in one
# Gap K11: "In such an area the unit formula does not apply."
def test_f3_density_evidence_in_one_withholds_the_unit_limit():
    ways = decide_result_ways(plain_inputs(
        special_density=DensityKnowledge.EVIDENCE_IN_ONE, **k20(True)))
    assert is_withheld(ways.unit_limit_standard)
    assert ways.unit_limit_standard.way.gap_kind == "work_owed"
    assert "special density area" in ways.unit_limit_standard.way.reason


# EVIDENCE_NOT_IN_ONE (builder open combination 1; the G3 reviewer CONFIRMED it): gap K11 gives
# no settled or conditional path for recorded evidence of absence, so it is withheld as work
# owed (reading O10: anything neither the work order nor the readings decide is withheld).
def test_density_evidence_not_in_one_is_withheld_as_work_owed_o10():
    ways = decide_result_ways(plain_inputs(
        special_density=DensityKnowledge.EVIDENCE_NOT_IN_ONE, **k20(True)))
    assert is_withheld(ways.unit_limit_standard)
    assert ways.unit_limit_standard.way.gap_kind == "work_owed"


# --------------------------------------------------------------------------- G4-F4 overlay not read
# Work order section 10 / gap K10 generalised: "a column that was not read is never taken as
# 'none'", so a not-read overlay column withholds every residential result (the G3 reviewer
# CONFIRMED this behaviour).
def test_f4_overlay_not_read_withholds_every_residential_result_missing_information():
    ways = decide_result_ways(base_inputs(
        commercial_overlay=Recorded.NOT_READ, overlay_support=None))
    affected = [
        *ways.floor_area_allowance.values, *_heights(ways), _coverage(ways),
        ways.rear_yard, ways.unit_limit_standard,
    ]
    for row in affected:
        assert is_withheld(row) and row.way.gap_kind == "missing_information"
        assert "not read" in row.way.reason
    assert not ways.floor_area_allowance.is_available
    assert not ways.permitted_envelope.is_available


# --------------------------------------------------------------------------- G4-F5 large lot (K3)
# Gap K3 / reading O8: a lot that meets the large-lot threshold has coverage withheld.
def test_f5_large_lot_threshold_withholds_coverage_work_owed():
    ways = decide_result_ways(plain_inputs(
        lot_type=LotType.CORNER, large_lot_threshold_met=True, **k20(True)))
    coverage = _coverage(ways)
    assert is_withheld(coverage) and coverage.way.gap_kind == "work_owed"
    assert "large-lot" in coverage.way.reason


# --------------------------------------------------------------------------- G4-F7
# K19: "A landmark or historic district changes no zoning number; it is shown as a fact beside
# the results." So any state of the landmark flag changes no result's way.
def test_f7a_landmark_changes_no_result():
    absent = decide_result_ways(plain_inputs(
        landmark_or_historic=Recorded.ABSENT, **k20(True)))
    for state in (Recorded.PRESENT, Recorded.NOT_READ):
        other = decide_result_ways(plain_inputs(landmark_or_historic=state, **k20(True)))
        assert other == absent  # frozen dataclasses: identical ways throughout


# A through lot: coverage withheld until ZR 23-363 is read (K2), the rear yard withheld (the
# corner waiver does not apply, K4) - the same as an interior lot.
def test_f7b_through_lot_withholds_coverage_and_rear_yard():
    ways = decide_result_ways(plain_inputs(lot_type=LotType.THROUGH, **k20(True)))
    coverage = _coverage(ways)
    assert is_withheld(coverage) and "ZR 23-363" in coverage.way.reason
    assert is_withheld(ways.rear_yard) and ways.rear_yard.way.gap_kind == "work_owed"


# K8: the setback above the base is "not covered".
def test_f7c_setback_reason_says_not_covered():
    ways = decide_result_ways(plain_inputs(**k20(True)))
    assert is_withheld(ways.setback_above_base)
    assert "not covered" in ways.setback_above_base.way.reason


# --------------------------------------------------------------------------- G3-F5 agreement None
# G3 note F5: a recorded area whose agreement with the outline was not recorded (agreement is
# None) is handled by an explicit branch with the same cautious outcome as could-not-compare -
# conditional, never settled, kind unchecked_condition - never a silent fall-through.
def test_g3f5_agreement_none_with_a_recorded_area_is_conditional_unchecked_never_settled():
    ways = decide_result_ways(plain_inputs(
        area=LotAreaFigures(5000.0, None, None), **k20(True)))
    value = ways.floor_area_allowance.values[0]
    assert is_conditional(value) and not is_settled(value)
    assert condition_kinds(value) == {"unchecked_condition"}
    cond = value.way.conditions[0]
    assert "was not recorded" in cond.assumption and cond.settled_by


# --------------------------------------------------------------------------- O11 the district
# Reading O11: district not given -> every zoning result withheld as missing information (the
# owner's rule that a missing input leaves its dependent results "not known"); a district other
# than the work order's scope -> every result withheld as work owed (the rules connected so far
# are R6B's; this district's are owed). "Every result" means every key.
def _every_key_withheld(ways) -> bool:
    return all(is_withheld(row) for row in ways.result_ways())


def test_o11_district_not_given_withholds_every_result_missing_information():
    ways = decide_result_ways(plain_inputs(district=None))
    assert _every_key_withheld(ways)
    assert not ways.floor_area_allowance.is_available
    assert not ways.permitted_envelope.is_available
    for row in (ways.floor_area_allowance.values[0], _heights(ways)[0], _coverage(ways),
                ways.rear_yard, ways.setback_above_base, ways.unit_limit_standard):
        assert row.way.gap_kind == "missing_information"
    reason = ways.floor_area_allowance.values[0].way.reason
    assert "zoning district was not given" in reason and "zoning record" in reason


def test_o11_district_not_r6b_withholds_every_result_work_owed():
    ways = decide_result_ways(plain_inputs(district="R5"))
    assert _every_key_withheld(ways)
    for row in (ways.floor_area_allowance.values[0], _heights(ways)[0], _coverage(ways),
                ways.rear_yard, ways.setback_above_base, ways.unit_limit_standard):
        assert row.way.gap_kind == "work_owed"
    reason = _heights(ways)[0].way.reason
    assert "R6B" in reason and "R5" in reason


# --------------------------------------------------------------------------- O12 the K14 label
# Reading O12 (gap K14): 'The limit is labelled "new all-residential building". Other cases are
# withheld.' The standard unit limit's label carries those words (and keeps "standard
# residences"). The module has no input for a conversion or a mixed building.
def test_o12_standard_unit_label_carries_the_k14_words():
    ways = decide_result_ways(plain_inputs(**k20(True)))
    label = ways.unit_limit_standard.label
    assert "new all-residential building" in label
    assert "standard residences" in label


# ======================= ROUND 4: the remaining input states =======================
# Work order test H5 / section 4 item 3: a fact not given leaves the results that depend on it
# withheld and names it, and every other result is unchanged; owner's rule: a missing input
# leaves its dependent results "not known". The packet's objective: the housing kind is a
# design choice carried for the wording.


def _env_heights(ways):
    return tuple(ways.permitted_envelope.values[:6])


def test_f9_lot_type_not_given_withholds_coverage_and_rear_yard_only():
    """G4-F9: lot_type=None reaches no_lot_type -> coverage and rear yard withheld, missing
    information, 'lot type is not given'; every other result unchanged."""
    given = decide_result_ways(plain_inputs(lot_type=LotType.CORNER, reach=c2_reach(), **k20(True)))
    none = decide_result_ways(plain_inputs(lot_type=None, reach=c2_reach(), **k20(True)))
    # with the lot type given (C2 is within the reaches) coverage and rear yard are shown:
    assert is_settled(_coverage(given)) and is_settled(given.rear_yard)
    # with it not given, both are withheld, missing information, naming the lot type:
    for row in (_coverage(none), none.rear_yard):
        assert is_withheld(row) and row.way.gap_kind == "missing_information"
        assert "lot type is not given" in row.way.reason
    # every other result is unchanged (identical ways to the lot-type-given case):
    assert none.floor_area_allowance == given.floor_area_allowance
    assert _env_heights(none) == _env_heights(given)
    assert none.building_option == given.building_option
    assert none.setback_above_base == given.setback_above_base
    assert none.unit_limit_standard == given.unit_limit_standard
    assert none.unit_limit_qualifying_affordable == given.unit_limit_qualifying_affordable
    assert none.unit_limit_qualifying_senior == given.unit_limit_qualifying_senior


def test_housing_kind_not_given_changes_no_result():
    """The housing kind is a design choice carried for the wording (packet objective); any
    value, or None, gives the identical ResultWays."""
    given = decide_result_ways(plain_inputs(housing_kind="standard_residence", **k20(True)))
    none = decide_result_ways(plain_inputs(housing_kind=None, **k20(True)))
    assert none == given


def test_large_lot_threshold_met_none_is_not_a_large_lot():
    """large_lot_threshold_met=None is falsy: the gap-K3 branch does not fire (the same path as
    False); the caller states the comparison, so an unstated flag is not a large lot. With the
    K20 conditions absent and a corner lot within the reaches, coverage is shown."""
    ways = decide_result_ways(plain_inputs(
        lot_type=LotType.CORNER, reach=c2_reach(), large_lot_threshold_met=None, **k20(True)))
    assert is_settled(_coverage(ways))


# ---- the reach records (ReachMeasurements / StreetReach / CornerReach / ReachValue) ----
# K12 / section 4 item 5: the reach is measured from the recorded outline; an unknown reach is
# "no outline" and the results that need it are withheld as missing information. O9: the waiver
# needs the two street lines to meet at 135 degrees or less.
def _reach(a_known=True, b_known=True, corner_known=True, angle=90.0, angle_known=True,
           corner_ft=50.0):
    a = ReachValue(40.0 if a_known else None)
    b = ReachValue(50.0 if b_known else None)
    corner = CornerReach(
        ReachValue(corner_ft if corner_known else None),
        ReachValue(angle if angle_known else None),
    )
    return ReachMeasurements((StreetReach("street A", a), StreetReach("street B", b)), corner)


def test_street_line_reach_unknown_withholds_coverage_missing_information():
    ways = decide_result_ways(plain_inputs(
        lot_type=LotType.CORNER, reach=_reach(a_known=False), **k20(True)))
    coverage = _coverage(ways)
    assert is_withheld(coverage) and coverage.way.gap_kind == "missing_information"
    assert "not measured" in coverage.way.reason


def test_corner_reach_unknown_withholds_rear_yard_missing_information():
    ways = decide_result_ways(plain_inputs(
        lot_type=LotType.CORNER, reach=_reach(corner_known=False), **k20(True)))
    assert is_withheld(ways.rear_yard) and ways.rear_yard.way.gap_kind == "missing_information"


def test_corner_angle_unknown_withholds_rear_yard_missing_information():
    ways = decide_result_ways(plain_inputs(
        lot_type=LotType.CORNER, reach=_reach(angle_known=False), **k20(True)))
    assert is_withheld(ways.rear_yard) and ways.rear_yard.way.gap_kind == "missing_information"


def test_corner_angle_above_135_withholds_rear_yard_work_owed():
    """O9 (ZR 23-344): the waiver holds only where the two street lines meet at 135 degrees or
    less; above that the rear yard is withheld even when the corner reach is within 100 ft."""
    ways = decide_result_ways(plain_inputs(
        lot_type=LotType.CORNER, reach=make_reach(
            (("street A", 40.0), ("street B", 50.0)), 140.0, 50.0), **k20(True)))
    assert is_withheld(ways.rear_yard) and ways.rear_yard.way.gap_kind == "work_owed"


# ---- the area outline figure with a DISAGREES state (LotAreaFigures.outline_sq_ft) ----
def test_disagree_with_no_outline_figure_uses_the_fallback_wording():
    """Section 6: when the figures disagree the condition names the other figure; with no
    outline figure recorded the module still names it (as 'another'), conditional, never
    settled, kind contradicted_record."""
    ways = decide_result_ways(plain_inputs(
        area=LotAreaFigures(10075.0, AreaAgreement.DISAGREES, None), **k20(True)))
    value = ways.floor_area_allowance.values[0]
    assert is_conditional(value)
    cond = next(c for c in value.way.conditions if c.kind == "contradicted_record")
    assert "another" in cond.assumption


# ---- the commercial overlay code (commercial_overlay_code) with the overlay recorded present ----
def test_overlay_code_present_appears_in_the_reason():
    ways = decide_result_ways(base_inputs(
        commercial_overlay=Recorded.PRESENT, commercial_overlay_code="C2-2", overlay_support=None))
    assert "(C2-2)" in _coverage(ways).way.reason


def test_overlay_code_none_with_overlay_present_still_withholds_without_a_code():
    ways = decide_result_ways(base_inputs(
        commercial_overlay=Recorded.PRESENT, commercial_overlay_code=None, overlay_support=None))
    reason = _coverage(ways).way.reason
    assert is_withheld(_coverage(ways))
    assert "recorded commercial overlay;" in reason  # no " (code)" before the semicolon


# ---- overlay_support: a family marked not supported WITHOUT the reading owed ----
def test_overlay_not_supported_without_reading_owed_uses_the_fallback_reading():
    support = {f: OverlayResultSupport(True) for f in ResultFamily}
    # supported=False with no reading_owed given:
    support[ResultFamily.COVERAGE] = OverlayResultSupport(False)
    ways = decide_result_ways(base_inputs(
        commercial_overlay=Recorded.PRESENT, commercial_overlay_code="C2-2",
        overlay_support=support))
    coverage = _coverage(ways)
    assert is_withheld(coverage) and coverage.way.gap_kind == "work_owed"
    assert "Article III sections" in coverage.way.reason  # the fallback owed-reading text


# ---- the four K20 conditions, each recorded PRESENT -> blanket (reading O6) ----
@pytest.mark.parametrize(
    "field",
    ["waterfront", "airport_height", "transit_easement", "near_district_line"],
)
def test_each_k20_condition_present_withholds_every_result(field: str):
    """Reading O6 / H11: with one no-data-source condition recorded present, every zoning
    result is withheld (each of the four conditions, not only the two the earlier tests used)."""
    ways = decide_result_ways(plain_inputs(**{field: Checked.PRESENT}))
    assert not ways.floor_area_allowance.is_available
    assert not ways.permitted_envelope.is_available
    assert is_withheld(ways.rear_yard)
    assert "recorded as present" in _heights(ways)[0].way.reason
