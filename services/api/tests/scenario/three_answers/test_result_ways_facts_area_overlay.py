"""Facts not given one at a time (S4, H5), the two area figures (S5, H6 and section 6) and the
overlay decided by what the caller states (S8). Expected ways come from the work order's
sentences, quoted beside each assertion; the module holds no table of what an overlay reading
supports (a test scans the source for the overlay chapters' section numbers).
"""

from __future__ import annotations

import pathlib

from app.scenario.three_answers import result_ways as rw
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
    condition_kinds,
    is_conditional,
    is_settled,
    is_withheld,
    k20,
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


def test_s5_figure_that_could_not_be_compared_is_conditional_on_the_recorded_figure():
    ways = decide_result_ways(plain_inputs(
        area=LotAreaFigures(10075.0, AreaAgreement.COULD_NOT_COMPARE, None), **k20(True)))
    value = ways.floor_area_allowance.values[0]
    assert is_conditional(value)
    area_cond = next(c for c in value.way.conditions if c.kind == "contradicted_record")
    assert "could not be computed to compare" in area_cond.assumption


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
