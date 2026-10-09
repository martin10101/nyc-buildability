"""Facts not given one at a time (S4, H5), the two area figures (S5, H6 and section 6) and the
overlay decided by what the caller states (S8). Expected ways come from the work order's
sentences, quoted beside each assertion; the module holds no table of what an overlay reading
supports (a test scans the source for the overlay chapters' section numbers).
"""

from __future__ import annotations

import pathlib

from app.scenario.three_answers import result_ways as rw
from app.scenario.three_answers.result_way_bridge_overlay import overlay_support_for
from app.scenario.three_answers.result_way_inputs import (
    AreaAgreement,
    LotAreaFigures,
    LotType,
    OverlayResultSupport,
    Recorded,
    ResultFamily,
)
from app.scenario.three_answers.result_ways import decide_result_ways

from .test_result_ways_lib import (
    base_inputs,
    benchmark_reach,
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


# --------------------------------------------------------------------------- S4 / H5
# H5: "Facts not given, one at a time ... Each time the results that depend on it are withheld
# and name it, and every other result is unchanged. A recorded special district, or a recorded
# split lot, withholds every result."


def test_h5_special_district_column_not_read_withholds_every_result():
    ways = decide_result_ways(plain_inputs(
        special_purpose_district=Recorded.NOT_READ, **k20(True)))
    for height in _heights(ways):
        assert is_withheld(height)
        assert "not read" in height.way.reason
        assert height.way.gap_kind == "missing_information"
    assert not ways.floor_area_allowance.is_available


def test_h5_no_outline_withholds_coverage_and_rear_yard_only():
    # "no outline ... the results that depend on it are withheld and name it, and every other
    # result is unchanged."
    ways = decide_result_ways(plain_inputs(reach=None, **k20(True)))
    assert is_withheld(_coverage(ways))
    assert is_withheld(ways.rear_yard)
    assert "not measured" in _coverage(ways).way.reason
    # every other result is unchanged: the heights and the floor area stay settled
    for height in _heights(ways):
        assert is_settled(height)
    for value in ways.floor_area_allowance.values:
        assert is_settled(value)


def test_h5_no_lot_area_withholds_floor_area_and_units_only():
    ways = decide_result_ways(plain_inputs(
        area=LotAreaFigures(None, None, None), **k20(True)))
    for value in ways.floor_area_allowance.values:
        assert is_withheld(value)
    assert is_withheld(ways.unit_limit_standard)
    # the heights do not need the area: they stay settled
    for height in _heights(ways):
        assert is_settled(height)


def test_h5_split_lot_record_not_read_withholds_every_result():
    ways = decide_result_ways(plain_inputs(
        split_by_district_line=Recorded.NOT_READ, **k20(True)))
    for height in _heights(ways):
        assert is_withheld(height)
    assert not ways.permitted_envelope.is_available


def test_h5_recorded_special_district_or_split_withholds_every_result():
    for field, value in (("special_purpose_district", Recorded.PRESENT),
                         ("split_by_district_line", Recorded.PRESENT)):
        ways = decide_result_ways(plain_inputs(**{field: value}, **k20(True)))
        assert not ways.floor_area_allowance.is_available
        assert not ways.permitted_envelope.is_available
        assert is_withheld(ways.rear_yard)
        assert is_withheld(ways.unit_limit_standard)


# --------------------------------------------------------------------------- S5 / H6 / section 6
# H6 and section 6: "agree: no area condition; disagree: conditional naming the recorded figure,
# both figures and what would settle it, no choice made; could not be compared: conditional on
# the recorded figure; none: withheld; the outline's area never stands in."


def test_s5_figures_that_agree_carry_no_area_condition():
    ways = decide_result_ways(plain_inputs(
        area=LotAreaFigures(5000.0, AreaAgreement.AGREES, 5000.0), **k20(False)))
    value = ways.floor_area_allowance.values[0]
    assert is_conditional(value)  # still conditional on the K20 conditions
    assert condition_kinds(value) == {"unchecked_condition"}  # but NOT on the area


def test_s5_figures_that_disagree_name_both_figures_and_make_no_choice():
    ways = decide_result_ways(plain_inputs(
        area=LotAreaFigures(10075.0, AreaAgreement.DISAGREES, 10388.0), **k20(True)))
    value = ways.floor_area_allowance.values[0]
    assert is_conditional(value)
    assert "contradicted_record" in condition_kinds(value)
    area_cond = next(c for c in value.way.conditions if c.kind == "contradicted_record")
    assert "10,075 sq ft" in area_cond.assumption  # the recorded figure, named
    assert "10,388 sq ft" in area_cond.assumption  # the other figure, named (no choice made)
    assert "survey" in area_cond.settled_by.lower()


def test_s5_figure_that_could_not_be_compared_is_an_unchecked_condition_o4():
    # Reading O4 (completed by the orchestrator, round 2): where the recorded lot area COULD
    # NOT be compared with the outline's area, the condition's kind is 'unchecked_condition'
    # (the comparison was not made), NOT 'contradicted_record' - which the contract describes
    # as "a recorded figure that another recorded figure contradicts" (results.schema.json
    # value_condition.kind), and here nothing contradicts the recorded figure. The assumption
    # says in plain words what was not checked.
    ways = decide_result_ways(plain_inputs(
        area=LotAreaFigures(10075.0, AreaAgreement.COULD_NOT_COMPARE, None), **k20(True)))
    value = ways.floor_area_allowance.values[0]
    assert is_conditional(value)
    assert condition_kinds(value) == {"unchecked_condition"}
    area_cond = next(c for c in value.way.conditions if c.kind == "unchecked_condition")
    assert "not compared with the tax-map outline's area" in area_cond.assumption
    assert area_cond.settled_by  # what would settle it


def test_s5_no_recorded_area_is_withheld_and_the_outline_never_stands_in():
    ways = decide_result_ways(plain_inputs(
        area=LotAreaFigures(None, None, 10388.0), **k20(True)))
    value = ways.floor_area_allowance.values[0]
    assert is_withheld(value)
    assert "never used" in value.way.reason  # the outline's area never stands in


# --------------------------------------------------------------------------- S8
# S8: "supported: decided as without an overlay; not supported: withheld as work owed, naming
# the reading owed; none stated: every residential result withheld; a dependent result withheld
# and naming what it depends on; the module holds no table of what any reading supports."


def test_s8_supported_result_is_decided_as_without_an_overlay():
    supported = decide_result_ways(base_overlay_support({ResultFamily.HEIGHTS: True}))
    for height in _heights(supported):
        assert is_conditional(height)  # conditional on K20, exactly as without an overlay


def test_s8_not_supported_result_is_withheld_naming_the_reading_owed():
    owed = "the reading of ZR 34-111 and ZR 35-632 under the overlay"
    ways = decide_result_ways(base_overlay_support(
        {ResultFamily.COVERAGE: OverlayResultSupport(False, owed, ("ZR 34-111", "ZR 35-632"))}))
    coverage = _coverage(ways)
    assert is_withheld(coverage)
    assert owed in coverage.way.reason  # the owed reading comes from the caller, not the module
    assert coverage.way.zr_sections == ("ZR 34-111", "ZR 35-632")
    assert coverage.way.gap_kind == "work_owed"


def test_s8_a_dependent_result_names_what_it_depends_on():
    # The building option depends on the withheld rear yard (its footprint); it is withheld and
    # names that dependency (gaps K4, K6).
    ways = decide_result_ways(plain_inputs(lot_type=LotType.CORNER, **k20(True)))
    assert not ways.building_option.is_available
    reason = ways.building_option.values[0].way.reason
    assert "rear yard" in reason


def test_s8_module_holds_no_table_of_what_a_reading_supports():
    # A test searches the source for section numbers of the overlay chapters: the module names
    # none of them; which results a reading supports is stated by the caller (reading O5).
    src = pathlib.Path(rw.__file__).read_text(encoding="utf-8")
    for section in ("34-111", "35-632", "35-631", "35-53", "34-24"):
        assert section not in src, f"the module names overlay section {section!r}"


def base_overlay_support(spec: dict):
    """A benchmark-overlay case where only the named families are supported (True), the rest
    carry an explicit not-supported statement (so the test controls each one)."""
    support = {}
    for family in ResultFamily:
        given = spec.get(family)
        if isinstance(given, OverlayResultSupport):
            support[family] = given
        else:
            support[family] = OverlayResultSupport(bool(given))
    return plain_inputs(
        commercial_overlay=Recorded.PRESENT, commercial_overlay_code="C2-2",
        overlay_support=support, **k20(False),
    )


# ===================================================================== M5-T144 S1-S7, S16
# The rear yard of an R6B corner lot beyond the waiver area, decided through the REAL overlay
# table (result_way_bridge_overlay.overlay_support_for), with and without the C2-2 overlay. The
# overlay no longer blocks the rear yard; the plain R6B corner/reach rules decide it, and beyond
# the waiver area it is withheld for a missing property fact. The exact texts are the ruled texts
# (M5-T144 ruling C1/C2); S1 and S3 assert the SAME text (one text for one situation of law).
_BEYOND_REASON = (
    "The corner rear-yard waiver does not cover the whole lot: the far corner is 144.60 ft from "
    "the point where the two street lines meet, beyond the rear-yard waiver area (the waiver "
    "covers the area within 100 ft of that point); the two street lines meet at 89.7 degrees, "
    "within the waiver's limit of 135 degrees. For the part beyond the waiver area, whether a "
    "rear yard is required depends on this lot's exact lot lines and on which lot lines of the "
    "adjoining lots meet them. The program does not have those facts, so the rear yard is not "
    "known."
)
_BEYOND_RESOLVER = (
    "A survey or deed that shows this lot's lot lines, and the adjoining lots' lot lines where "
    "they meet this lot."
)


def _c2_r6b_overlay(**overrides):
    """A recorded C2-2 overlay within R6B with the REAL overlay-support table wired in, exactly as
    the bridge wires it (result_way_bridge.overlay_support_for)."""
    return base_inputs(overlay_support=overlay_support_for("C2-2", "R6B"), **overrides)


def test_s1_c2_2_r6b_corner_beyond_100_angle_within_corrected_reason():
    """S1: a recorded C2-2 overlay in R6B, corner lot, far corner 144.60 ft (beyond 100) and the
    angle 89.7 degrees (within 135). The overlay no longer blocks the rear yard; it is withheld by
    the corner/reach logic with the corrected missing-information reason and resolver; no figure."""
    ways = decide_result_ways(_c2_r6b_overlay(reach=benchmark_reach(), **k20(True)))
    rear = ways.rear_yard.way
    assert is_withheld(ways.rear_yard)
    assert rear.reason == _BEYOND_REASON
    assert rear.gap_kind == "missing_information"
    assert rear.resolved_by == _BEYOND_RESOLVER
    assert "value" not in rear.to_value_state()  # no figure
    assert "overlay" not in rear.reason.lower()  # the overlay reading no longer appears


def test_s2_c2_2_r6b_corner_within_100_angle_within_rear_yard_shown():
    """S2: same overlay/district, corner lot, reach within 100 ft and angle within 135 (the C2
    made-up lot: corner 100.00 ft, right angle). The overlay no longer blocks it and the corner
    waiver applies: the rear yard is SHOWN (settled with the K20 conditions checked-and-absent)."""
    ways = decide_result_ways(_c2_r6b_overlay(
        reach=make_reach((("street A", 80.0), ("street B", 60.0)), 90.0, 100.0), **k20(True)))
    assert is_settled(ways.rear_yard)


def test_s3_no_overlay_r6b_corner_beyond_100_same_corrected_text():
    """S3 / ruling C1: a no-overlay R6B corner lot in the same position gets the SAME reason, kind
    and resolver as the C2-2 lot (S1) - one text for one situation of law; no figure."""
    ways = decide_result_ways(plain_inputs(
        lot_type=LotType.CORNER, reach=benchmark_reach(), **k20(True)))
    rear = ways.rear_yard.way
    assert is_withheld(ways.rear_yard)
    assert rear.reason == _BEYOND_REASON
    assert rear.gap_kind == "missing_information"
    assert rear.resolved_by == _BEYOND_RESOLVER


def test_s4_other_overlay_code_in_r6b_unchanged_generic_withheld():
    """S4: a recorded overlay whose code is not C2-2, in R6B - overlay_support_for returns None, so
    the rear yard is withheld with the GENERIC overlay-withheld text, naming the code, unchanged."""
    assert overlay_support_for("C1-1", "R6B") is None
    ways = decide_result_ways(base_inputs(
        commercial_overlay_code="C1-1", overlay_support=overlay_support_for("C1-1", "R6B"),
        reach=benchmark_reach(), **k20(True)))
    rear = ways.rear_yard.way
    assert is_withheld(ways.rear_yard)
    assert "no independent reading of the overlay text is yet stated" in rear.reason
    assert "(C1-1)" in rear.reason
    assert rear.gap_kind == "work_owed"


def test_s5_c2_2_other_district_table_is_none_and_lot_is_blanket_withheld():
    """S5: a recorded C2-2 overlay but district is not R6B - the table does not speak for it
    (overlay_support_for returns None), and the decision module blanket-withholds every result for
    a district out of the connected scope, so other districts are untouched by this change."""
    assert overlay_support_for("C2-2", "R5") is None
    ways = decide_result_ways(base_inputs(
        district="R5", overlay_support=overlay_support_for("C2-2", "R5"),
        reach=benchmark_reach(), **k20(True)))
    rear = ways.rear_yard.way
    assert is_withheld(ways.rear_yard)
    assert "R5" in rear.reason and "does not cover the whole lot" not in rear.reason


def test_s6_c2_2_r6b_corner_angle_over_135_keeps_waiver_text():
    """S6: C2-2 in R6B, corner lot, the two street lines meet at more than 135 degrees (far corner
    within 100). The overlay does not change it and it keeps the existing 'angle over the limit'
    waiver text (work owed), NOT the corrected missing-information text."""
    ways = decide_result_ways(_c2_r6b_overlay(
        reach=make_reach((("street A", 40.0), ("street B", 50.0)), 140.0, 90.0), **k20(True)))
    rear = ways.rear_yard.way
    assert is_withheld(ways.rear_yard)
    assert rear.gap_kind == "work_owed"
    assert "more than the rear-yard waiver's limit of 135 degrees" in rear.reason
    assert "does not cover the whole lot" not in rear.reason


def test_s7_c2_2_r6b_corner_unmeasured_keeps_unmeasured_text():
    """S7: C2-2 in R6B, corner present but the reach not measured. The overlay does not change it
    and it keeps the rear_yard_unmeasured text naming the missing measurement (missing
    information), NOT the corrected beyond-the-waiver text."""
    ways = decide_result_ways(_c2_r6b_overlay(
        reach=make_reach((("street A", 40.0), ("street B", 50.0)), 90.0, None), **k20(True)))
    rear = ways.rear_yard.way
    assert is_withheld(ways.rear_yard)
    assert rear.gap_kind == "missing_information"
    assert "not measured" in rear.reason
    assert "does not cover the whole lot" not in rear.reason


def test_s16_angle_over_and_both_branches_identical_with_and_without_overlay():
    """S16 / ruling C1/C2: the two branches M5-T144 did NOT change (angle over the limit; both
    fail) read character-for-character the same with the C2-2 overlay and without, their kind is
    work owed, and their resolver is the unchanged ordinary-rear-yard text. Proves only the
    distance-beyond/angle-within branch changed and the overlay changes none of them."""
    over = make_reach((("street A", 40.0), ("street B", 50.0)), 140.0, 90.0)   # angle over, within
    both = make_reach((("street A", 40.0), ("street B", 50.0)), 140.0, 144.60)  # both fail
    ordinary_resolver = (
        "Working out the ordinary rear-yard rule for the part the waiver does not cover and "
        "checking it against an independently worked example."
    )
    for reach in (over, both):
        with_overlay = decide_result_ways(_c2_r6b_overlay(reach=reach, **k20(True))).rear_yard.way
        no_overlay = decide_result_ways(plain_inputs(
            lot_type=LotType.CORNER, reach=reach, **k20(True))).rear_yard.way
        assert isinstance(with_overlay, rw.Withheld) and isinstance(no_overlay, rw.Withheld)
        assert with_overlay.reason == no_overlay.reason
        assert with_overlay.reason.startswith("The rear-yard waiver does not apply: ")
        assert with_overlay.gap_kind == no_overlay.gap_kind == "work_owed"
        assert with_overlay.resolved_by == no_overlay.resolved_by == ordinary_resolver
