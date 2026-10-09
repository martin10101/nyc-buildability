"""Shared builders for the result-way tests (task M5-T129). No test functions of its own.

Expected OUTCOMES come from the work order's sentences (quoted beside each test), never from
the module under test. The made-up lots' DIMENSIONS come from the work order's table C; the
reach MEASUREMENTS are read from the reach rows of the corner-reach reference case through the
loader (``real-lot-reach``, ``C1-reach``, ``C2-reach``, ``C3-reach``). To keep the two pieces
of this wave independent, the tests read NO other reference row (the other task may supersede
rows while this one is built), and this helper asserts every reach figure it uses against the
loaded row's prose, so no number is copied blind.
"""

from __future__ import annotations

import pathlib
import sys

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
    ResultWayInputs,
    StreetReach,
)
from app.scenario.three_answers.result_ways import Conditional, ResultWay, Settled, Withheld

# The reference loader (test support, not program code). Same sys.path shim the lot-reach
# test uses; this folder has no __init__.py so it is imported by name.
_REF_LIB_DIR = pathlib.Path(__file__).resolve().parents[2] / "rules" / "reference_cases"
if str(_REF_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_REF_LIB_DIR))

import r6b_reference_cases_lib as reference_cases  # noqa: E402


def reach_row(row_id: str) -> dict:
    """One reach row read through the loader (never a program run)."""
    return reference_cases.load_row("corner-reach", row_id)


def assert_figures_in_row(row_id: str, *figures: str) -> dict:
    """Confirm every reach figure the test uses is the one the reference row records, so a
    number is never copied blind. Returns the row for further assertions."""
    row = reach_row(row_id)
    assert row["kind"] == "value", f"{row_id}: not a value row"
    for figure in figures:
        assert figure in row["value"], f"{row_id}: {figure!r} not in the reach row prose"
    return row


def make_reach(
    street_lines: tuple[tuple[str, float], ...], angle_deg: float, corner_ft: float
) -> ReachMeasurements:
    """Build the reach records from named street-line reaches, the corner angle and the corner
    reach (mirroring the measurements M5-T127's lot_reach produces)."""
    lines = tuple(StreetReach(name, ReachValue(ft)) for name, ft in street_lines)
    corner = CornerReach(ReachValue(corner_ft), ReachValue(angle_deg))
    return ReachMeasurements(lines, corner)


def benchmark_reach() -> ReachMeasurements:
    """The real lot's reach: 99.97 ft (Northern Boulevard), 103.93 ft (215 Place), corner
    144.60 ft (work order table C, reach row real-lot-reach); angle 89.7 degrees (work order
    L9: 'two street frontages meeting at 89.7 degrees')."""
    assert_figures_in_row("real-lot-reach", "99.97", "103.93", "144.60")
    return make_reach((("Northern Boulevard", 99.97), ("215 Place", 103.93)), 89.7, 144.60)


def corner_reach(row_id: str, a_ft: float, b_ft: float, corner_ft: float) -> ReachMeasurements:
    """A made-up corner lot's reach (table C; the rectangles meet at a right angle)."""
    return make_reach((("street A", a_ft), ("street B", b_ft)), 90.0, corner_ft)


# The three made-up corner lots of table C, their dimensions from the work order text and
# every reach figure confirmed against the loaded reach row.
def c1_reach() -> ReachMeasurements:  # 40 x 100 ft
    assert_figures_in_row("C1-reach", "100.00", "40.00", "107.70")
    return corner_reach("C1-reach", 100.00, 40.00, 107.70)


def c2_reach() -> ReachMeasurements:  # 60 x 80 ft
    assert_figures_in_row("C2-reach", "80.00", "60.00", "100.00")
    return corner_reach("C2-reach", 80.00, 60.00, 100.00)


def c3_reach() -> ReachMeasurements:  # 150 x 100 ft
    assert_figures_in_row("C3-reach", "100.00", "150.00", "180.28")
    return corner_reach("C3-reach", 100.00, 150.00, 180.28)


_K20_NOT_CHECKED = dict(
    waterfront=Checked.NOT_CHECKED, airport_height=Checked.NOT_CHECKED,
    transit_easement=Checked.NOT_CHECKED, near_district_line=Checked.NOT_CHECKED,
)
_K20_ALL_ABSENT = dict(
    waterfront=Checked.ABSENT, airport_height=Checked.ABSENT,
    transit_easement=Checked.ABSENT, near_district_line=Checked.ABSENT,
)


def k20(checked: bool) -> dict:
    """The four K20 conditions, all checked-and-absent (True) or all not-checked (False)."""
    return dict(_K20_ALL_ABSENT) if checked else dict(_K20_NOT_CHECKED)


def base_inputs(**overrides) -> ResultWayInputs:
    """The benchmark lot as recorded (work order S1): R6B, a recorded C2-2 overlay, corner,
    the benchmark reach, the two area figures disagreeing (10,075 and 10,388 sq ft, K5), no
    special district, not split, the four K20 conditions not checked, no density evidence.
    Overrides replace any field for a focused case."""
    fields = dict(
        district="R6B", lot_type=LotType.CORNER, housing_kind="standard_residence",
        area=LotAreaFigures(10075.0, AreaAgreement.DISAGREES, 10388.0),
        reach=benchmark_reach(),
        special_purpose_district=Recorded.ABSENT, split_by_district_line=Recorded.ABSENT,
        commercial_overlay=Recorded.PRESENT, commercial_overlay_code="C2-2",
        inclusionary_housing_area=Recorded.ABSENT, flood_zone=Recorded.ABSENT,
        landmark_or_historic=Recorded.ABSENT,
        special_density=DensityKnowledge.NOT_GIVEN, large_lot_threshold_met=False,
        overlay_support=None,
    )
    fields.update(_K20_NOT_CHECKED)
    fields.update(overrides)
    return ResultWayInputs(**fields)


def plain_inputs(**overrides) -> ResultWayInputs:
    """A lot with NO commercial overlay (so the residential rules are decided as without an
    overlay) and one recorded area figure that agrees, for the made-up lots."""
    defaults = dict(
        commercial_overlay=Recorded.ABSENT, commercial_overlay_code=None,
        area=LotAreaFigures(10075.0, AreaAgreement.AGREES, 10075.0),
    )
    defaults.update(overrides)
    return base_inputs(**defaults)


def support_all(supported: bool) -> dict[ResultFamily, OverlayResultSupport]:
    return {family: OverlayResultSupport(supported) for family in ResultFamily}


def way_name(row: ResultWay) -> str:
    return type(row.way).__name__


def is_settled(row: ResultWay) -> bool:
    return isinstance(row.way, Settled)


def is_conditional(row: ResultWay) -> bool:
    return isinstance(row.way, Conditional)


def is_withheld(row: ResultWay) -> bool:
    return isinstance(row.way, Withheld)


def condition_kinds(row: ResultWay) -> set[str]:
    assert isinstance(row.way, Conditional)
    return {c.kind for c in row.way.conditions}
