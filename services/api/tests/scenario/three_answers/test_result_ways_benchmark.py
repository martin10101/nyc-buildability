"""The benchmark lot (S1) and 'not checked is not confirmed' (S6). Every expected way is the
one the work order's sentences state (quoted beside each assertion), read from section 5 and
tests H1, H2 and H11; the reach measurements come from the corner-reach reference rows.
"""

from __future__ import annotations

from app.scenario.three_answers.result_way_inputs import (
    Checked,
    OverlayResultSupport,
    Recorded,
    ResultFamily,
)
from app.scenario.three_answers.result_ways import decide_result_ways

from .test_result_ways_lib import (
    base_inputs,
    condition_kinds,
    is_conditional,
    is_settled,
    is_withheld,
    k20,
    plain_inputs,
    support_all,
)


def _heights(ways):
    return ways.permitted_envelope.values[:6]


def _coverage(ways):
    return ways.permitted_envelope.values[-1]


# --------------------------------------------------------------------------- S1 / H1 / H2
# Work order S1 (packet) and H1/H2: on the benchmark lot "the height limits conditional on the
# four unchecked conditions and never settled". With "heights supported; floor area ratio,
# coverage and rear yard not yet supported": "the floor area ratio, floor area, coverage and
# rear yard withheld (a reading is owed)". In both "the setback, the building option and the
# unit limits withheld; never a zero".


def test_s1a_overlay_supports_heights_only():
    support = {
        ResultFamily.HEIGHTS: OverlayResultSupport(True),
        ResultFamily.FLOOR_AREA: OverlayResultSupport(
            False, "the floor-area reading under the overlay", ("ZR 34-111",)),
        ResultFamily.COVERAGE: OverlayResultSupport(
            False, "the coverage reading under the overlay", ("ZR 35-632",)),
        ResultFamily.REAR_YARD: OverlayResultSupport(
            False, "the rear-yard reading under the overlay", ("ZR 35-631",)),
        ResultFamily.UNIT_LIMIT: OverlayResultSupport(
            False, "the dwelling-unit reading under the overlay", ("ZR 23-52",)),
        ResultFamily.SETBACK: OverlayResultSupport(False, "the setback reading", ("ZR 23-433",)),
        ResultFamily.BUILDING_OPTION: OverlayResultSupport(False, "the option reading", ()),
    }
    ways = decide_result_ways(base_inputs(overlay_support=support))
    # "the height limits conditional on the four unchecked conditions and never settled"
    for height in _heights(ways):
        assert is_conditional(height)
        assert condition_kinds(height) == {"unchecked_condition"}
    # "the floor area ratio, floor area ... withheld (a reading is owed)"
    assert not ways.floor_area_allowance.is_available
    for value in ways.floor_area_allowance.values:
        assert is_withheld(value)
        assert "reading" in value.way.reason and value.way.gap_kind == "work_owed"
    # coverage and rear yard withheld (a reading is owed)
    assert is_withheld(_coverage(ways))
    assert is_withheld(ways.rear_yard)
    # "the setback, the building option and the unit limits withheld; never a zero"
    assert is_withheld(ways.setback_above_base)
    assert not ways.building_option.is_available
    assert is_withheld(ways.unit_limit_standard)
    assert is_withheld(ways.unit_limit_qualifying_affordable)
    assert is_withheld(ways.unit_limit_qualifying_senior)


def test_s1b_overlay_supports_everything():
    ways = decide_result_ways(base_inputs(overlay_support=support_all(True)))
    # "the floor-area figures conditional (on the recorded area and on the four conditions)"
    for value in ways.floor_area_allowance.values:
        assert is_conditional(value)
        assert condition_kinds(value) == {"contradicted_record", "unchecked_condition"}
    for height in _heights(ways):
        assert is_conditional(height)
    # "coverage still withheld (the lot reaches 103.93 ft from a street line)"
    coverage = _coverage(ways)
    assert is_withheld(coverage)
    assert "103.93 ft" in coverage.way.reason
    # "and the rear yard still withheld (144.60 ft from the corner point)"
    assert is_withheld(ways.rear_yard)
    assert "144.60 ft" in ways.rear_yard.way.reason
    # the setback, the building option and the unit limits withheld
    assert is_withheld(ways.setback_above_base)
    assert not ways.building_option.is_available
    assert is_withheld(ways.unit_limit_standard)


def test_s1_qualifying_unit_limits_read_not_known_h2():
    # H2: "the legal unit limits for qualifying affordable and qualifying senior housing read
    # 'not known'".
    ways = decide_result_ways(base_inputs(overlay_support=support_all(True)))
    assert is_withheld(ways.unit_limit_qualifying_affordable)
    assert is_withheld(ways.unit_limit_qualifying_senior)
    assert "not set by this formula" in ways.unit_limit_qualifying_senior.way.reason


def test_s1_recorded_overlay_with_no_support_withholds_every_residential_result():
    # Reading O5 / gap K9: "A recorded overlay with no statement of support at all: every
    # residential result withheld."
    ways = decide_result_ways(base_inputs(overlay_support=None))
    for value in ways.floor_area_allowance.values:
        assert is_withheld(value)
    for height in _heights(ways):
        assert is_withheld(height)
    assert is_withheld(_coverage(ways))
    assert is_withheld(ways.rear_yard)
    assert is_withheld(ways.unit_limit_standard)


def test_no_text_calls_a_height_the_property_maximum_h11():
    # H11 / R269: the height limit is the district's limit, "nowhere 'the maximum for this
    # property'". At the way level it is conditional (never settled) while a condition is open.
    ways = decide_result_ways(base_inputs(overlay_support=support_all(True)))
    for height in _heights(ways):
        assert not is_settled(height)
        for cond in height.way.conditions:
            assert "maximum for this property" not in cond.assumption.lower()


# --------------------------------------------------------------------------- S6 / H11
# H11: "With the K20 conditions not checked: no zoning result is settled; each is conditional
# and names the conditions ... With one of them recorded as present: the results it can change
# are withheld ... With all of them supplied as checked and absent: the height limits become
# settled."


def test_s6_not_checked_makes_every_zoning_result_conditional_not_settled():
    ways = decide_result_ways(plain_inputs(**k20(False)))
    for height in _heights(ways):
        assert is_conditional(height)
        assert condition_kinds(height) == {"unchecked_condition"}
    # the floor-area figures (area agrees) are conditional on the K20 conditions, not settled
    for value in ways.floor_area_allowance.values:
        assert is_conditional(value)


def test_s6_one_condition_present_withholds_every_zoning_result():
    ways = decide_result_ways(plain_inputs(airport_height=Checked.PRESENT))
    for height in _heights(ways):
        assert is_withheld(height)
    for value in ways.floor_area_allowance.values:
        assert is_withheld(value)
    assert is_withheld(_coverage(ways))
    assert is_withheld(ways.rear_yard)
    assert is_withheld(ways.unit_limit_standard)
    assert "recorded as present" in _heights(ways)[0].way.reason


def test_s6_all_conditions_checked_and_absent_settles_the_height_limits():
    ways = decide_result_ways(plain_inputs(**k20(True)))
    for height in _heights(ways):
        assert is_settled(height)
    # the floor-area figures (area agrees) are then settled too
    for value in ways.floor_area_allowance.values:
        assert is_settled(value)


def test_s6_recorded_special_district_is_not_a_k20_condition_but_still_withholds_all():
    # Gap K10: "One recorded: every result is withheld (owed)."
    ways = decide_result_ways(plain_inputs(
        special_purpose_district=Recorded.PRESENT, **k20(True)))
    for height in _heights(ways):
        assert is_withheld(height)
    assert ways.floor_area_allowance.whole_answer_not_available.gap_kind == "work_owed"
