"""Acceptance scenarios S22-S28 for the preliminary apartment estimate (PART D), plus
the orchestrator's corrections C12 and C15.

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


def _check_block(floor_area: float, block: dict) -> None:
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
    _check_block(_num(block["floor_area_sqft"]), block)


def test_s23_made_up_estimate_a() -> None:
    # Basis: step-p6-worked#made-up-estimate-a (16,000 sq ft -> 13.71 and 17.14).
    block = _block("made-up-estimate-a")
    _check_block(_num(block["floor_area_sqft"]), block)


def test_s24_made_up_estimate_b() -> None:
    # Basis: step-p6-worked#made-up-estimate-b (20,000 sq ft -> 17.14 and 21.43).
    block = _block("made-up-estimate-b")
    _check_block(_num(block["floor_area_sqft"]), block)


def test_s25_real_estimate_a_two_readings_same_two_decimals() -> None:
    # Basis: step-p6-worked#real-estimate-a (10,309.91 and 10,309.88 both -> 8.84/11.05).
    block = _block("real-estimate-a")
    floors = block["floor_area_sqft"]  # {"reading1": "10309.91", "reading2": "10309.88"}
    for key in ("reading1", "reading2"):
        _check_block(_num(floors[key]), block)


def test_s26_missing_floor_area_not_known() -> None:
    # Correction C12: a missing input names NO kind of gap; it names the missing input.
    result = preliminary_apartment_estimate(None)

    assert result.status == "not_known"
    assert result.quotient_low is None
    assert result.quotient_high is None
    assert result.gap_kind is None
    assert result.missing_inputs == ("floor_area_sq_ft",)
    assert result.label == "Not known"
    assert "floor area" in result.reason.lower()


def test_s27_zero_apartment_size_rejected() -> None:
    with pytest.raises(ValueError):
        preliminary_apartment_estimate(20_150.0, apartment_size_sq_ft=0.0)


def test_s28_labels_and_separation_from_the_legal_limit() -> None:
    # Corrections C15(a)/(b): label is the owner's own words; the texts that name the
    # apartment size or the share carry 'preliminary assumption' and the owner's
    # descriptions. Basis: real-estimate-b does_not_establish; D-090 R540/R541/R545/
    # R688/R700.
    block = _block("real-estimate-b")
    result = preliminary_apartment_estimate(
        floor_area_sq_ft=_num(block["floor_area_sqft"]),
        share_low=_num(block["share_low"]),
        share_high=_num(block["share_high"]),
        apartment_size_sq_ft=_num(block["apartment_size_sqft"]),
    )

    assert result.label == "Preliminary capacity estimate"
    assert "preliminary assumption" not in result.label.lower()

    for text in (result.formula, result.reason):
        lower = text.lower()
        assert "preliminary assumption" in lower
        assert "sensitivity range" in lower
        assert "the user can change" in lower
        assert "hpd measurement basis" in lower

    joined = " ".join((result.label, result.formula, result.reason)).lower()
    for word in ("measured", "typical", "validated", "realistic", "expected", "law"):
        assert not re.search(rf"\b{word}\b", joined), f"forbidden word {word!r}"
    for phrase in (
        "legal limit",
        "ceiling",
        "dwelling-unit limit",
        "approval",
        "captured",
        "complies",
        "feasible",
        "verified",
        "legally correct",
    ):
        assert phrase not in joined, f"forbidden wording {phrase!r} in a returned text"


def test_c15c_exact_whole_quotient_above_equals_below() -> None:
    # Correction C15(c): the whole above a quotient is its ceiling; an exact whole
    # quotient has the same number below and above. 14,000 x 0.50 / 700 = 10.00 and
    # 14,000 x 0.75 / 700 = 15.00 (both exact).
    result = preliminary_apartment_estimate(
        14_000.0, share_low=0.50, share_high=0.75, apartment_size_sq_ft=700.0
    )
    assert result.quotient_low == pytest.approx(10.0, abs=1e-9)
    assert result.quotient_high == pytest.approx(15.0, abs=1e-9)
    assert result.whole_below_low == 10
    assert result.whole_above_low == 10
    assert result.whole_below_high == 15
    assert result.whole_above_high == 15


def test_c15d_negative_floor_area_rejected() -> None:
    with pytest.raises(ValueError):
        preliminary_apartment_estimate(-1.0)


def test_c15d_share_outside_0_to_1_rejected() -> None:
    with pytest.raises(ValueError):
        preliminary_apartment_estimate(20_150.0, share_high=1.5)


def test_c15d_low_share_above_high_share_rejected() -> None:
    with pytest.raises(ValueError):
        preliminary_apartment_estimate(20_150.0, share_low=0.80, share_high=0.60)
