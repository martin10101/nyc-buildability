"""Acceptance scenarios S9-S14 for the by-portion lot-coverage arithmetic (PART B),
plus the orchestrator's corrections C12 and C16.

One test per scenario of this part. Every expected figure is PARSED from the
independent reference case docs/reference-cases/R6B/cases/step-p6-worked.json (rows
``made-up-footprint-a`` and ``real-lot-coverage-by-portion``) or is the plain hand
arithmetic written out in the scenario (S12); no expected value comes from a run of
the module under test.
"""

from __future__ import annotations

import json
import pathlib
import re

import pytest

from app.scenario.three_answers.lot_coverage_by_portion import (
    permitted_footprint_by_portion,
)

_CASE = (
    pathlib.Path(__file__).resolve().parents[5]
    / "docs"
    / "reference-cases"
    / "R6B"
    / "cases"
    / "step-p6-worked.json"
)


def _rows() -> dict:
    data = json.loads(_CASE.read_text())
    return {row["row_id"]: row for row in data["rows"]}


def _num(text: str) -> float:
    """A reading's figure such as '9,997.60' or '8,000' as a float (commas stripped)."""
    return float(text.replace(",", ""))


def _coverage_reading(row: dict, reading: str) -> dict:
    """Parse one reading's corner area, interior strip area, interior allowed and total
    allowed from the row's source_reference ('13' or '14')."""
    match = re.search(
        rf"calculation-{reading}\.md Q4b \(corner ([\d,.]+) at 100%; "
        rf"strip ([\d,.]+) at 80% = ([\d,.]+); total allowed ([\d,.]+)\)",
        row["source_reference"],
    )
    assert match, f"could not parse reading {reading} from {row['source_reference']!r}"
    return {
        "corner": _num(match.group(1)),
        "strip": _num(match.group(2)),
        "interior_allowed": _num(match.group(3)),
        "total": _num(match.group(4)),
    }


def test_s9_made_up_footprint_a_interior_lot_all_eighty_percent() -> None:
    # Basis: step-p6-worked#made-up-footprint-a (0.80 x 10,000 = 8,000).
    row = _rows()["made-up-footprint-a"]
    match = re.search(r"0\.80 x 10,000 = ([\d,]+)", row["expected"]["value"])
    assert match
    expected_footprint = _num(match.group(1))  # 8,000

    result = permitted_footprint_by_portion(
        corner_portion_area=0.0,
        interior_portion_area=10_000.0,
        corner_ratio=1.00,
        interior_ratio=0.80,
    )

    assert result.status == "available"
    assert result.corner_allowed == 0.0
    assert round(result.interior_allowed, 2) == expected_footprint  # 8,000.00
    assert round(result.footprint, 2) == expected_footprint  # 8,000.00


def test_s10_real_lot_coverage_by_portion_reading_13() -> None:
    # Basis: step-p6-worked#real-lot-coverage-by-portion, reading 13 (never a run).
    reading = _coverage_reading(_rows()["real-lot-coverage-by-portion"], "13")

    result = permitted_footprint_by_portion(
        corner_portion_area=reading["corner"],
        interior_portion_area=reading["strip"],
        corner_ratio=1.00,
        interior_ratio=0.80,
    )

    assert result.status == "available"
    assert round(result.corner_allowed, 2) == reading["corner"]  # 9,997.60
    assert round(result.interior_allowed, 2) == reading["interior_allowed"]  # 312.31
    assert round(result.footprint, 2) == reading["total"]  # 10,309.91


def test_s11_real_lot_coverage_by_portion_reading_14() -> None:
    # Basis: step-p6-worked#real-lot-coverage-by-portion, reading 14 (its own areas).
    reading = _coverage_reading(_rows()["real-lot-coverage-by-portion"], "14")

    result = permitted_footprint_by_portion(
        corner_portion_area=reading["corner"],
        interior_portion_area=reading["strip"],
        corner_ratio=1.00,
        interior_ratio=0.80,
    )

    assert result.status == "available"
    assert round(result.corner_allowed, 2) == reading["corner"]  # 9,997.46
    assert round(result.interior_allowed, 2) == reading["interior_allowed"]  # 312.42
    assert round(result.footprint, 2) == reading["total"]  # 10,309.88


def test_s12_corner_rule_whole_lot_within_corner_portion() -> None:
    # ZR 23-362 (capture zr-23-362): a lot wholly within the corner-lot portion takes
    # 100 percent. Scenario hand arithmetic: 5,000 x 1.00 = 5,000.00.
    result = permitted_footprint_by_portion(
        corner_portion_area=5_000.0,
        interior_portion_area=0.0,
        corner_ratio=1.00,
        interior_ratio=0.80,
    )

    assert result.status == "available"
    assert round(result.corner_allowed, 2) == 5_000.00
    assert result.interior_allowed == 0.0
    assert round(result.footprint, 2) == 5_000.00


def test_s13_missing_portion_areas_not_known() -> None:
    # Correction C12: a missing input names NO kind of gap; it names the missing inputs.
    result = permitted_footprint_by_portion(None, None)

    assert result.status == "not_known"
    assert result.footprint is None
    assert result.corner_allowed is None
    assert result.interior_allowed is None
    assert result.gap_kind is None
    assert result.missing_inputs == ("corner_portion_area", "interior_portion_area")
    assert "not known" in result.reason.lower()


def test_s14_negative_area_rejected() -> None:
    with pytest.raises(ValueError):
        permitted_footprint_by_portion(-1.0, 390.39)


def test_c16a_available_text_follows_actual_ratios() -> None:
    # Correction C16(a): the text of an available result is written from the ratios
    # actually used, not a hardcoded 80 percent.
    result = permitted_footprint_by_portion(
        corner_portion_area=1_000.0,
        interior_portion_area=1_000.0,
        corner_ratio=1.00,
        interior_ratio=0.50,
    )
    assert "50 percent" in result.reason
    assert "80 percent" not in result.reason


def test_c16b_ratio_out_of_range_rejected() -> None:
    # Correction C16(b): a ratio outside 0 to 1 is refused.
    with pytest.raises(ValueError):
        permitted_footprint_by_portion(1_000.0, 1_000.0, corner_ratio=1.5)
    with pytest.raises(ValueError):
        permitted_footprint_by_portion(1_000.0, 1_000.0, interior_ratio=-0.1)


def test_c16c_footprint_never_exceeds_sum_of_areas() -> None:
    # Correction C16(c) / D-090 R147: with ratios in 0..1 the footprint can never exceed
    # the sum of the two portion areas, over the scenarios' inputs.
    reading13 = _coverage_reading(_rows()["real-lot-coverage-by-portion"], "13")
    reading14 = _coverage_reading(_rows()["real-lot-coverage-by-portion"], "14")
    cases = [
        (0.0, 10_000.0),
        (reading13["corner"], reading13["strip"]),
        (reading14["corner"], reading14["strip"]),
        (5_000.0, 0.0),
    ]
    for corner, interior in cases:
        result = permitted_footprint_by_portion(corner, interior, 1.00, 0.80)
        assert result.footprint <= corner + interior + 1e-9
