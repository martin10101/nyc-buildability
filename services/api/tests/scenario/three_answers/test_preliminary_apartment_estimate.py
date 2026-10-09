"""Acceptance scenarios S22-S28 for the preliminary apartment estimate (PART D).

One test per scenario of this part. Every expected figure is PARSED from the
independent reference case docs/reference-cases/R6B/cases/step-p6-worked.json (the
``numbers_block`` of rows ``made-up-estimate-a/b`` and ``real-estimate-a/b``); no
expected value comes from a run of the module under test. The share range (0.60 to
0.75) and the apartment size (700 sq ft) are the owner's preliminary assumptions.
"""

from __future__ import annotations

import json
import pathlib
import re

import pytest

from app.scenario.three_answers.preliminary_apartment_estimate import (
    preliminary_apartment_estimate,
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


def _block(row_id: str) -> dict:
    return _rows()[row_id]["numbers_block"]


def _num(text: str) -> float:
    return float(str(text).replace(",", ""))


def _check_block(row_id: str, floor_area: float, block: dict) -> None:
    """Feed one floor area through the module and assert the block's own quotients and
    whole-number range (every figure parsed from the reading's numbers_block)."""
    result = preliminary_apartment_estimate(
        floor_area_sq_ft=floor_area,
        share_low=_num(block["share_low"]),
        share_high=_num(block["share_high"]),
        apartment_size_sq_ft=_num(block["apartment_size_sqft"]),
    )
    assert result.status == "available"
    assert result.quotient_low == pytest.approx(_num(block["quotient_low"]), abs=1e-9)
    assert result.quotient_high == pytest.approx(_num(block["quotient_high"]), abs=1e-9)
    assert result.whole_below_low == block["whole_below_low"]
    assert result.whole_above_low == block["whole_above_low"]
    assert result.whole_below_high == block["whole_below_high"]
    assert result.whole_above_high == block["whole_above_high"]


def test_s22_real_estimate_b() -> None:
    # Basis: step-p6-worked#real-estimate-b (20,150 sq ft -> 17.27 and 21.59).
    block = _block("real-estimate-b")
    _check_block("real-estimate-b", _num(block["floor_area_sqft"]), block)


def test_s23_made_up_estimate_a() -> None:
    # Basis: step-p6-worked#made-up-estimate-a (16,000 sq ft -> 13.71 and 17.14).
    block = _block("made-up-estimate-a")
    _check_block("made-up-estimate-a", _num(block["floor_area_sqft"]), block)


def test_s24_made_up_estimate_b() -> None:
    # Basis: step-p6-worked#made-up-estimate-b (20,000 sq ft -> 17.14 and 21.43).
    block = _block("made-up-estimate-b")
    _check_block("made-up-estimate-b", _num(block["floor_area_sqft"]), block)


def test_s25_real_estimate_a_two_readings_same_two_decimals() -> None:
    # Basis: step-p6-worked#real-estimate-a (10,309.91 and 10,309.88 both -> 8.84/11.05).
    block = _block("real-estimate-a")
    floors = block["floor_area_sqft"]  # {"reading1": "10309.91", "reading2": "10309.88"}
    for key in ("reading1", "reading2"):
        _check_block("real-estimate-a", _num(floors[key]), block)


def test_s26_missing_floor_area_not_known() -> None:
    result = preliminary_apartment_estimate(None)

    assert result.status == "not_known"
    assert result.quotient_low is None
    assert result.quotient_high is None
    assert result.gap_kind == "a missing fact about the property"
    reason = result.reason.lower()
    assert "floor area" in reason
    assert "preliminary assumption" in reason


def test_s27_zero_apartment_size_rejected() -> None:
    with pytest.raises(ValueError):
        preliminary_apartment_estimate(20_150.0, apartment_size_sq_ft=0.0)


def test_s28_labels_and_separation_from_the_legal_limit() -> None:
    # Basis: real-estimate-b does_not_establish; D-090 R545, R688, R700.
    block = _block("real-estimate-b")
    result = preliminary_apartment_estimate(
        floor_area_sq_ft=_num(block["floor_area_sqft"]),
        share_low=_num(block["share_low"]),
        share_high=_num(block["share_high"]),
        apartment_size_sq_ft=_num(block["apartment_size_sqft"]),
    )

    texts = (result.label, result.formula, result.reason)
    for text in texts:
        assert "preliminary assumption" in text.lower()

    joined = " ".join(texts).lower()
    assert not re.search(r"\blaw\b", joined)
    for forbidden in (
        "legal limit",
        "ceiling",
        "dwelling-unit limit",
        "measured",
        "typical",
        "validated",
        "approval",
        "captured",
        "complies",
        "feasible",
        "verified",
        "legally correct",
    ):
        assert forbidden not in joined, f"forbidden wording {forbidden!r} in a returned text"
