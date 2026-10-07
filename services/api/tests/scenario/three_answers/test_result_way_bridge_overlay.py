"""The overlay-support table rests on the merged reference rows (task M5-T130, scenario S4; O16).

The table lives in app code (``result_way_bridge_overlay``); this test reads the reference rows
it names THROUGH the test-only loader (which refuses a superseded row) and fails if a row is
superseded, is not a value row, or does not say "same as plain R6B". A family is supported only
where its current row gives the answer with no standing condition from either reading; the rear
yard is not supported because its row carries one reading's caveat. Expected outcomes come from
the reference rows and the orchestrator's reading O16, never from the module.
"""

from __future__ import annotations

import pathlib
import sys

from app.scenario.three_answers.result_way_bridge_overlay import (
    OVERLAY_DISTRICT,
    OVERLAY_SUPPORT_ROWS,
    SUPPORTED_OVERLAY_CODE,
    overlay_support_for,
)
from app.scenario.three_answers.result_way_inputs import ResultFamily

_REF_LIB_DIR = pathlib.Path(__file__).resolve().parents[2] / "rules" / "reference_cases"
if str(_REF_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_REF_LIB_DIR))

import r6b_reference_cases_lib as reference_cases  # noqa: E402


def _has_standing_condition(value: str) -> bool:
    """A reading's standing caveat in the row's prose means the answer is not unconditional.
    O16: the rear-yard row says 'same as plain R6B' but 'subject to one caveat' (the capture of
    ZR 34-23 holds only its title line)."""
    return "caveat" in value.lower()


def test_every_table_row_rests_on_a_current_same_as_plain_r6b_reference_row():
    """S4: each table entry names a CURRENT reference row (the loader raises on a superseded
    one), which is a value row that says 'same as plain R6B'."""
    for row in OVERLAY_SUPPORT_ROWS:
        loaded = reference_cases.load_row(row.case_id, row.row_id)  # raises if superseded
        assert loaded["kind"] == "value", f"{row.row_id}: not a value row"
        assert "same as plain r6b" in loaded["value"].lower(), row.row_id


def test_a_family_is_supported_only_with_no_standing_condition():
    """S4 / O16: a family is supported exactly when its current row carries no standing
    condition; the rear yard, whose row carries a caveat, is not supported."""
    for row in OVERLAY_SUPPORT_ROWS:
        loaded = reference_cases.load_row(row.case_id, row.row_id)
        standing = _has_standing_condition(loaded["value"])
        assert row.supported == (not standing), (
            f"{row.family.value}: table says supported={row.supported} but the row's standing "
            f"condition={standing}"
        )


def test_the_floor_area_coverage_heights_setback_units_are_supported_rear_yard_is_not():
    by_family = {row.family: row for row in OVERLAY_SUPPORT_ROWS}
    for family in (ResultFamily.FLOOR_AREA, ResultFamily.COVERAGE, ResultFamily.HEIGHTS,
                   ResultFamily.SETBACK, ResultFamily.UNIT_LIMIT):
        assert by_family[family].supported is True, family.value
    assert by_family[ResultFamily.REAR_YARD].supported is False
    # the rear-yard entry names the owed reading in plain words, so the decision module can show it
    assert by_family[ResultFamily.REAR_YARD].reading_owed


def test_the_statement_is_built_only_for_a_c2_2_overlay_within_r6b():
    """O16: any other overlay code, or an overlay within another district, supports nothing (the
    caller returns None, so the decision module withholds every residential result)."""
    assert overlay_support_for(SUPPORTED_OVERLAY_CODE, OVERLAY_DISTRICT) is not None
    assert overlay_support_for("C1-1", OVERLAY_DISTRICT) is None
    assert overlay_support_for(SUPPORTED_OVERLAY_CODE, "R5") is None
    assert overlay_support_for(None, OVERLAY_DISTRICT) is None


def test_the_built_statement_matches_the_table():
    support = overlay_support_for(SUPPORTED_OVERLAY_CODE, OVERLAY_DISTRICT)
    assert support is not None
    for row in OVERLAY_SUPPORT_ROWS:
        assert support[row.family].supported == row.supported
    assert support[ResultFamily.REAR_YARD].supported is False
    assert support[ResultFamily.FLOOR_AREA].supported is True
