"""The made-up corner lots (S2, test H3) and the interior lots with the unit limit (S3, tests
H4 and H9). Coverage and rear-yard reaches are read from the corner-reach reference rows; the
ways come from the work order's sentences, quoted beside each assertion.
"""

from __future__ import annotations

from app.scenario.three_answers.result_way_inputs import (
    AreaAgreement,
    DensityKnowledge,
    LotAreaFigures,
    LotType,
)
from app.scenario.three_answers.result_ways import decide_result_ways

from .test_result_ways_lib import (
    c1_reach,
    c2_reach,
    c3_reach,
    condition_kinds,
    is_conditional,
    is_settled,
    is_withheld,
    k20,
    plain_inputs,
)


def _coverage(ways):
    return ways.permitted_envelope.values[-1]


def _corner(reach, **overrides):
    return plain_inputs(lot_type=LotType.CORNER, reach=reach, **overrides)


# --------------------------------------------------------------------------- S2 / H3
# H3: "40 x 100 ft gives coverage 100 percent and rear yard withheld; 60 x 80 ft gives coverage
# 100 percent and no rear yard required anywhere; 150 x 100 ft gives coverage withheld and rear
# yard withheld ... each supplied with the K20 conditions as checked and absent [settled] ...
# With the K20 conditions not checked, the same values are conditional."


def test_h3_c1_coverage_shown_rear_yard_withheld():
    settled = decide_result_ways(_corner(c1_reach(), **k20(True)))
    # "40 x 100 ft gives coverage 100 percent" -> coverage shown; settled when K20 absent
    assert is_settled(_coverage(settled))
    # "and rear yard withheld" (the far corner is 107.70 ft, beyond the 100 ft waiver area)
    assert is_withheld(settled.rear_yard)
    assert "107.70 ft" in settled.rear_yard.way.reason
    # "With the K20 conditions not checked, the same values are conditional."
    not_checked = decide_result_ways(_corner(c1_reach(), **k20(False)))
    assert is_conditional(_coverage(not_checked))
    assert condition_kinds(_coverage(not_checked)) == {"unchecked_condition"}


def test_h3_c2_coverage_shown_and_no_rear_yard_required_anywhere():
    settled = decide_result_ways(_corner(c2_reach(), **k20(True)))
    # "60 x 80 ft gives coverage 100 percent and no rear yard required anywhere" -> both shown;
    # settled when the K20 conditions are checked and absent (the diagonal is exactly 100 ft).
    assert is_settled(_coverage(settled))
    assert is_settled(settled.rear_yard)
    not_checked = decide_result_ways(_corner(c2_reach(), **k20(False)))
    assert is_conditional(_coverage(not_checked))
    assert is_conditional(not_checked.rear_yard)


def test_h3_c3_coverage_withheld_and_rear_yard_withheld():
    ways = decide_result_ways(_corner(c3_reach(), **k20(True)))
    # "150 x 100 ft gives coverage withheld and rear yard withheld" even with K20 checked:
    # the reach (150 ft; corner 180.28 ft) is beyond the legal measures.
    assert is_withheld(_coverage(ways))
    assert "150 ft" in _coverage(ways).way.reason
    assert is_withheld(ways.rear_yard)
    assert "180.28 ft" in ways.rear_yard.way.reason


# --------------------------------------------------------------------------- S3 / H4 / H9
# H4: "floor area as in the table, settled when the K20 conditions are supplied as checked and
# absent, conditional when they are not checked; the legal unit limit withheld with no
# density-area evidence, and conditional, with the table's value, when the user states it;
# coverage withheld until step P1's reading of 23-363 is in". The interior lots carry one area
# figure.


def _interior(**overrides):
    return plain_inputs(
        lot_type=LotType.INTERIOR, reach=None,
        area=LotAreaFigures(5000.0, AreaAgreement.AGREES, 5000.0), **overrides,
    )


def test_h4_interior_floor_area_settled_when_k20_checked_conditional_when_not():
    settled = decide_result_ways(_interior(**k20(True)))
    for value in settled.floor_area_allowance.values:
        assert is_settled(value)
    not_checked = decide_result_ways(_interior(**k20(False)))
    for value in not_checked.floor_area_allowance.values:
        assert is_conditional(value)
        assert condition_kinds(value) == {"unchecked_condition"}


def test_h4_interior_coverage_withheld_until_the_23_363_reading():
    ways = decide_result_ways(_interior(**k20(True)))
    coverage = _coverage(ways)
    assert is_withheld(coverage)
    assert "ZR 23-363" in coverage.way.reason
    assert coverage.way.gap_kind == "work_owed"


def test_h4_h9_unit_limit_withheld_without_density_evidence():
    # "the legal unit limit withheld with no density-area evidence"
    ways = decide_result_ways(_interior(special_density=DensityKnowledge.NOT_GIVEN, **k20(True)))
    assert is_withheld(ways.unit_limit_standard)
    assert ways.unit_limit_standard.way.gap_kind == "work_owed"


def test_h9_user_statement_makes_the_unit_limit_a_conditional_result_only():
    # H9: "A user's statement about the lot (the density-area answer) produces only a
    # conditional result that names the statement; the statement is absent from the sourced
    # facts ... without it the result is withheld again."
    stated = decide_result_ways(
        _interior(special_density=DensityKnowledge.USER_STATEMENT_NOT_IN_ONE, **k20(True)))
    assert is_conditional(stated.unit_limit_standard)
    assert "user_statement" in condition_kinds(stated.unit_limit_standard)
    # the statement is confined to the unit limit; it makes no other result conditional
    assert is_settled(stated.floor_area_allowance.values[0])
    # without the statement the unit limit is withheld again
    without = decide_result_ways(_interior(special_density=DensityKnowledge.NOT_GIVEN, **k20(True)))
    assert is_withheld(without.unit_limit_standard)


def test_h9_statement_is_never_stored_as_a_fact_it_stays_a_condition():
    # R255: "a user's assumption supports only a labelled conditional result"; the module's
    # only use of the statement is a condition of kind user_statement - never a settled value.
    ways = decide_result_ways(
        _interior(special_density=DensityKnowledge.USER_STATEMENT_NOT_IN_ONE, **k20(False)))
    way = ways.unit_limit_standard.way
    assert is_conditional(ways.unit_limit_standard)
    kinds = {c.kind for c in way.conditions}
    assert "user_statement" in kinds and "unchecked_condition" in kinds
