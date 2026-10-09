"""The overlay-support table rests on the merged reference rows (task M5-T130, scenario S4; O16;
M5-T144 ruling C1/C2).

The table lives in app code (``result_way_bridge_overlay``); this test reads the reference rows
it names THROUGH the test-only loader (which refuses a superseded row) and fails if a row is
superseded or is not a value row. Five families rest on a row that says "same as plain R6B"; the
rear yard now rests on the step-P5 row ``zr-34-23-page``, which reads the ZR 34-23 page as the
complete three-subsection list (none speaking of the rear yard) and resolves the step-P4
completeness caveat, so the overlay adds no rear-yard rule and every family is supported. "Being
supported" means the overlay no longer blocks the family; the plain R6B rules then decide it (and
may still withhold the rear yard for a missing property fact in the decision module). Expected
outcomes come from the reference rows and the orchestrator's reading O16, never from the module.
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

# The rear-yard family now rests on this step-P5 row (M5-T144); the other five rest on a row that
# says "same as plain R6B".
_REAR_YARD_ROW = ("step-p5-worked", "zr-34-23-page")


def test_every_table_row_rests_on_a_current_value_reference_row():
    """S4: each table entry names a CURRENT reference row (the loader raises on a superseded one)
    that is a value row. The five 'same as plain R6B' families say so; the rear-yard family rests
    on the step-P5 row that resolves the overlay caveat (checked in its own test below)."""
    for row in OVERLAY_SUPPORT_ROWS:
        loaded = reference_cases.load_row(row.case_id, row.row_id)  # raises if superseded
        assert loaded["kind"] == "value", f"{row.row_id}: not a value row"
        if row.family is not ResultFamily.REAR_YARD:
            assert "same as plain r6b" in loaded["value"].lower(), row.row_id


def test_the_rear_yard_rests_on_the_step_p5_row_that_resolves_the_overlay_caveat():
    """S4 / M5-T144 ruling C1: the rear-yard family rests on step-P5 row zr-34-23-page, a value
    row that reads the ZR 34-23 page as the complete three-subsection list (none speaking of the
    rear yard) and resolves the step-P4 completeness caveat, so the overlay adds no rear-yard rule
    and the rear yard follows the plain R6B rules."""
    by_family = {row.family: row for row in OVERLAY_SUPPORT_ROWS}
    rear = by_family[ResultFamily.REAR_YARD]
    assert (rear.case_id, rear.row_id) == _REAR_YARD_ROW
    loaded = reference_cases.load_row(rear.case_id, rear.row_id)
    value = loaded["value"].lower()
    assert loaded["kind"] == "value"
    assert "none of the three speaks of the rear yard" in value
    assert "resolving the completeness caveat" in value


def test_every_family_including_the_rear_yard_is_supported():
    """S4 / O16, M5-T144: with the step-P4 completeness caveat resolved in step P5, every family
    (including the rear yard) is supported - the overlay blocks none of them."""
    by_family = {row.family: row for row in OVERLAY_SUPPORT_ROWS}
    for family in (ResultFamily.FLOOR_AREA, ResultFamily.COVERAGE, ResultFamily.HEIGHTS,
                   ResultFamily.SETBACK, ResultFamily.UNIT_LIMIT, ResultFamily.REAR_YARD):
        assert by_family[family].supported is True, family.value
    # a supported row carries no 'reading owed' prose (nothing is owed any more)
    assert by_family[ResultFamily.REAR_YARD].reading_owed == ""


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
    assert support[ResultFamily.REAR_YARD].supported is True
    assert support[ResultFamily.FLOOR_AREA].supported is True
