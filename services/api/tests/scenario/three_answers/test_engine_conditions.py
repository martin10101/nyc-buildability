"""Unit tests for engine_conditions: the engine's five lot conditions derived from plain evidence
states (task M5-T137). ONE test per input state (the table in the producer report); the measured
reach and angle figures come from docs/reference-cases/R6B/cases/corner-reach.json through the
loader, never from a program run; the recorded and statement states are logic branches with no
number.

Each derivation branch and each withholding stand-in is PINNED here, so a mutation - flipping a
branch, or a stand-in direction - fails a test. The producer report flips each in a copy OUTSIDE
the repository and records the matching failing test (the mutation proofs).
"""

from __future__ import annotations

import pathlib
import sys

from app.scenario.three_answers.engine_conditions import (
    WITHIN_100_FT,
    DensityStatement,
    Presence,
    Source,
    angle_when_not_measured_degrees,
    derive_conditions,
    overlay,
    special_density,
    special_district,
    within_100_and_angle,
)

# The reference loader (test support, not program code). Same sys.path shim the lot-reach and
# result-way tests use; this folder has no __init__.py so it is imported by name.
_REF_LIB_DIR = pathlib.Path(__file__).resolve().parents[2] / "rules" / "reference_cases"
if str(_REF_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_REF_LIB_DIR))

import r6b_reference_cases_lib as reference_cases  # noqa: E402


def _reach_figure(row_id: str, figure: str) -> str:
    """Confirm a reach figure the test uses is the one the reference row records (never copied
    blind), and return the row prose."""
    row = reference_cases.load_row("corner-reach", row_id)
    assert figure in row["value"], (row_id, figure)
    return row["value"]


# --------------------------------------------------------------------------- overlay
def test_overlay_recorded_present_is_yes_with_the_code():
    derived = overlay(Presence.PRESENT, "C2-2")
    assert derived.engine_value is True
    assert derived.source is Source.RECORDED
    assert derived.code == "C2-2"


def test_overlay_recorded_absent_is_no():
    derived = overlay(Presence.ABSENT)
    assert derived.engine_value is False
    assert derived.source is Source.RECORDED


def test_overlay_not_read_is_no_overlay_not_known():
    # The stand-in direction: "no overlay" adds no commercial-overlay note, so nothing unsupported
    # is asserted. Flipping it to True (the mutation) would add an unsupported note.
    derived = overlay(Presence.NOT_READ)
    assert derived.engine_value is False
    assert derived.source is Source.NOT_KNOWN


# --------------------------------------------------------------------------- special district
def test_special_district_recorded_present_is_yes():
    derived = special_district(Presence.PRESENT)
    assert derived.engine_value is True
    assert derived.source is Source.RECORDED


def test_special_district_recorded_absent_is_no():
    derived = special_district(Presence.ABSENT)
    assert derived.engine_value is False
    assert derived.source is Source.RECORDED


def test_special_district_not_read_uses_the_present_stand_in():
    # The stand-in direction: "present" makes every rule ask for review, so every dependent result
    # is withheld (r6b_*.rule.json exception special_district_modification). Flipping it to False
    # (the mutation) would let the engine emit heights, coverage and the rest.
    derived = special_district(Presence.NOT_READ)
    assert derived.engine_value is True
    assert derived.source is Source.NOT_KNOWN


# --------------------------------------------------------------------------- within 100 ft + angle
def test_benchmark_corner_is_not_within_100_ft_measured():
    """The real benchmark lot reaches 144.60 ft from the corner point (corner-reach.json
    real-lot-reach), more than 100 feet, so within-100 is No; the angle 89.7 degrees is the measured
    value. Reach and angle come from the SAME measurement the decision step uses."""
    prose = _reach_figure("real-lot-reach", "144.60")
    within, angle = within_100_and_angle(is_corner=True, reach_ft=144.60, angle_deg=89.7)
    assert within.engine_value is False
    assert within.source is Source.MEASURED
    assert within.figure == 144.60
    assert angle.engine_value == 89.7
    assert angle.source is Source.MEASURED
    assert angle.figure == 89.7
    assert "144.60" in prose


def test_c2_corner_is_within_100_ft_measured():
    """The made-up corner lot C2 reaches 100.00 ft from the corner point (corner-reach.json
    C2-reach); the within-100 boundary is inclusive, so within-100 is Yes."""
    _reach_figure("C2-reach", "100.00")
    within, angle = within_100_and_angle(is_corner=True, reach_ft=100.00, angle_deg=90.0)
    assert within.engine_value is True
    assert within.source is Source.MEASURED
    assert angle.engine_value == 90.0
    assert angle.source is Source.MEASURED


def test_c3_corner_is_not_within_100_ft_measured():
    """The made-up corner lot C3 reaches 180.28 ft from the corner point (corner-reach.json
    C3-reach), more than 100 feet, so within-100 is No."""
    _reach_figure("C3-reach", "180.28")
    within, _angle = within_100_and_angle(is_corner=True, reach_ft=180.28, angle_deg=90.0)
    assert within.engine_value is False
    assert within.source is Source.MEASURED


def test_interior_lot_has_no_corner_conditions():
    within, angle = within_100_and_angle(is_corner=False, reach_ft=None, angle_deg=None)
    assert within.engine_value is False
    assert within.source is Source.NOT_APPLICABLE
    assert angle.engine_value == angle_when_not_measured_degrees()
    assert angle.source is Source.NOT_APPLICABLE


def test_corner_without_a_measurement_is_not_known():
    within, angle = within_100_and_angle(is_corner=True, reach_ft=None, angle_deg=None)
    assert within.engine_value is False  # the withholding stand-in (not within 100 feet)
    assert within.source is Source.NOT_KNOWN
    assert angle.engine_value == angle_when_not_measured_degrees()
    assert angle.source is Source.NOT_KNOWN


def test_unknown_lot_type_without_a_measurement_is_not_known():
    within, angle = within_100_and_angle(is_corner=None, reach_ft=None, angle_deg=None)
    assert within.source is Source.NOT_KNOWN
    assert angle.source is Source.NOT_KNOWN


def test_the_within_100_boundary_is_inclusive_at_100_ft():
    # ZR 23-344(a) "... within 100 feet ...", inclusive - the SAME comparison the decision step
    # uses, so the engine value never disagrees with the decision step for a shown rear yard.
    assert WITHIN_100_FT == 100.0
    at_limit, _a = within_100_and_angle(is_corner=True, reach_ft=100.0, angle_deg=90.0)
    assert at_limit.engine_value is True
    over_limit, _b = within_100_and_angle(is_corner=True, reach_ft=100.01, angle_deg=90.0)
    assert over_limit.engine_value is False


def test_angle_stand_in_is_past_the_waiver_limit():
    # The angle the engine is given when not measured is past the waiver's "135 degrees or less"
    # limit (ZR 23-344(a)), so the waiver never applies on it (within-100 "no" already withholds).
    assert angle_when_not_measured_degrees() > 135.0


# --------------------------------------------------------------------------- special density area
def test_density_user_statement_not_in_one_is_no_as_a_statement():
    derived = special_density(DensityStatement.NOT_IN_ONE)
    assert derived.engine_value is False
    assert derived.source is Source.USER_STATEMENT


def test_density_no_statement_uses_the_inside_one_stand_in():
    # The stand-in direction: "inside one" makes the dwelling-unit rule not applicable
    # (r6b_dwelling_units.rule.json applicability), so the limit is withheld. Flipping it to False
    # (the mutation) would let the engine emit a dwelling-unit figure.
    derived = special_density(DensityStatement.NONE)
    assert derived.engine_value is True
    assert derived.source is Source.NOT_KNOWN


# --------------------------------------------------------------------------- the five together
def test_derive_conditions_keys_and_benchmark_values():
    conds = derive_conditions(
        overlay_presence=Presence.PRESENT,
        overlay_code="C2-2",
        special_district_presence=Presence.ABSENT,
        is_corner=True,
        reach_ft=144.60,
        angle_deg=89.7,
        density_statement=DensityStatement.NONE,
    )
    assert set(conds) == {
        "overlay_present",
        "special_district_present",
        "within_100_ft_of_street_line_intersection",
        "street_line_intersection_angle_degrees",
        "special_density_area",
    }
    assert conds["overlay_present"].engine_value is True
    assert conds["special_district_present"].engine_value is False
    assert conds["within_100_ft_of_street_line_intersection"].engine_value is False
    assert conds["street_line_intersection_angle_degrees"].engine_value == 89.7
    # the density is not known (no statement), so the engine gets the inside-one stand-in
    assert conds["special_density_area"].engine_value is True
    assert conds["special_density_area"].source is Source.NOT_KNOWN
