"""Step-P6 acceptance tests for the R6B reference cases (M4-T037).

D-090 R291/R519/R545/R650/R651/R664/R686-R690/R699/R700.

The step-P6 case is one independent hand-worked example of a first building option:
whether a building may be lower than the minimum base height; a footprint and floors
worked by hand for a made-up interior lot and the recorded corner lot (lot coverage
by portion; variants where a property fact is missing); what a floor schedule must
list; and the preliminary apartment estimate on the owner's starting values, kept
apart from the legal dwelling-unit ceiling. These tests prove, one per input state:
the two readings are present unchanged (digest pinned); a value is recorded only
where both readings agree; the rows the readings do not jointly settle stay not
known; a value where they differ is refused; a changed law quote is caught; every
building and estimate block recomputes from its own inputs (storey sums; total plus
unused equals the maximum; plan area times storeys equals the floor area; building
B's plan equals the maximum divided by its storeys; the estimate's four figures
follow from the floor area); every figure is marked a legal requirement or a chosen
design assumption; each building and estimate row says what the example is and is
not; and the superseded L15 row stays superseded with its targets current while the
reach rows are byte-stable. Kept in its own file; engine-free.
"""
from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import sys
from decimal import ROUND_HALF_UP, Decimal

import pytest

_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import r6b_reference_cases_check as check  # noqa: E402
import r6b_reference_cases_lib as lib  # noqa: E402
import r6b_reference_cases_step_p6 as step_p6  # noqa: E402

CASES = lib.load_all()
CID = "step-p6-worked"

# The four corner-reach reach rows are read by other tasks' tests and must not move.
# Their content digest, pinned at the claim head, proves byte-stability without git.
REACH_ROWS_DIGEST = "e708d886c42971c0beeaeb1d506421a1161bea748df80193e85a7dad309ef092"


def _D(x):
    return Decimal(str(x))


def _r2(x):
    return _D(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _block(rid):
    row = next(r for r in CASES[CID]["rows"] if r["row_id"] == rid)
    return row["numbers_block"]


# --------------------------------------------------------------------------
# provenance: the two readings present unchanged, and a changed one is caught
# --------------------------------------------------------------------------
def test_the_two_step_p6_readings_are_present_unchanged():
    assert check.step_p6_reading_errors() == []
    for name, spec in step_p6.STEP_P6_READINGS.items():
        raw = (lib.PROVENANCE_DIR / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == spec["digest"], name
        text = raw.decode("utf-8")
        assert "sealed folder" in text, name
        assert text.rstrip().endswith("END-OF-REPORT"), name
    thirteen = (lib.PROVENANCE_DIR / "return-independent-hand-calculation-13.md").read_text()
    fourteen = (lib.PROVENANCE_DIR / "return-independent-hand-calculation-14.md").read_text()
    assert thirteen != fourteen


def test_a_changed_step_p6_reading_is_caught(monkeypatch):
    bad = {
        "return-independent-hand-calculation-13.md":
            {"marker": "ONE HARD RULE", "digest": "0" * 64},
        "return-independent-hand-calculation-14.md":
            step_p6.STEP_P6_READINGS["return-independent-hand-calculation-14.md"],
    }
    monkeypatch.setattr(step_p6, "STEP_P6_READINGS", bad)
    errs = check.step_p6_reading_errors()
    assert errs and any("digest changed" in m for m in errs), errs


# --------------------------------------------------------------------------
# both readings named; the whole case validates clean
# --------------------------------------------------------------------------
def test_step_p6_case_validates_clean():
    assert check.validate_case(CID, CASES[CID]) == []


def test_step_p6_rows_name_both_readings():
    for row in CASES[CID]["rows"]:
        assert check.both_readings_errors(CID, row) == [], row["row_id"]


# --------------------------------------------------------------------------
# Q1 minimum base height: value only where both readings agree on the same words
# --------------------------------------------------------------------------
def test_minimum_base_height_rows_are_values_on_both_readings():
    plain = lib.load_row(CID, "min-base-height-plain-r6b")
    assert plain["kind"] == "value" and "permitted" in plain["value"].lower()
    overlay = lib.load_row(CID, "min-base-height-overlay")
    assert overlay["kind"] == "value" and "permitted" in overlay["value"].lower()
    least = lib.load_row(CID, "min-base-height-least-height-or-storeys")
    assert least["kind"] == "value" and "no captured provision" in least["value"].lower()
    wall = lib.load_row(CID, "min-base-height-street-wall")
    assert wall["kind"] == "value" and "whichever is less" in wall["value"]


# --------------------------------------------------------------------------
# the rows the two readings do not jointly settle stay not known
# --------------------------------------------------------------------------
def test_step_p6_not_known_rows_with_a_kind_of_gap():
    for rid in ("made-up-street-wall", "real-lot-coverage-by-portion",
                "real-lot-rear-yard-variants"):
        row = lib.load_row(CID, rid)
        assert row["kind"] == "not_known", rid
        assert row["value"] is None, rid
        reason = row["reason"].lower()
        assert "kind of gap" in reason, rid
        assert ("missing fact about the property" in reason
                or "measurement" in reason or "measured" in reason), rid


def test_a_step_p6_value_where_the_readings_differ_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "real-lot-coverage-by-portion":
            row["expected"]["kind"] = "value"
            row["expected"]["value"] = "the whole-lot coverage is 100 percent"
            row["expected"]["reason"] = ""
    errs = step_p6.must_stay_not_known_errors(CID, data)
    assert errs and any("real-lot-coverage-by-portion" in m for m in errs), errs


def test_a_changed_law_quote_in_a_step_p6_row_is_caught():
    data = copy.deepcopy(CASES[CID])
    target = next(r for r in data["rows"] if r["row_id"] == "min-base-height-plain-r6b")
    target["citations"][0]["quote"] = "this phrase is not in the capture at all"
    errs = check.citation_errors(CID, target)
    assert errs and any(
        "quoted words" in m and "min-base-height-plain-r6b" in m for m in errs), errs


# --------------------------------------------------------------------------
# the building blocks recompute from their own inputs (the six steps)
# --------------------------------------------------------------------------
def test_building_blocks_recompute_clean():
    assert step_p6.block_and_word_errors(CID, CASES[CID]) == []


def test_every_storey_table_sums_to_its_total_and_total_plus_unused_is_the_maximum():
    for rid in ("made-up-building-a", "made-up-building-b", "real-building-b"):
        b = _block(rid)
        total = _D(b["total_floor_area_sqft"])
        summed = sum(_D(s["floor_area_sqft"]) for s in b["storeys"]) if b["fill_rule"] == "widest" \
            else _D(b["storeys"][-1]["running_total_sqft"])
        assert summed == total, rid
        assert total + _D(b["unused_floor_area_sqft"]) == _D(b["maximum_floor_area_sqft"]), rid


def test_plan_area_times_storeys_equals_building_a_floor_area():
    b = _block("made-up-building-a")
    plan = _D(b["footprint_area_sqft"])
    assert plan * len(b["storeys"]) == _D(b["total_floor_area_sqft"])


def test_building_b_plan_area_is_the_maximum_divided_by_its_storeys():
    for rid in ("made-up-building-b", "real-building-b"):
        b = _block(rid)
        want = _r2(_D(b["maximum_floor_area_sqft"]) / len(b["storeys"]))
        for s in b["storeys"]:
            assert _D(s["plan_area_sqft"]) == want, rid


def test_real_building_a_holds_both_readers_footprints_and_both_give_one_storey():
    b = _block("real-building-a")
    fp = b["footprint_area_sqft"]
    assert set(fp) == {"reading1", "reading2"} and fp["reading1"] != fp["reading2"]
    assert b["storey_count"] == 1
    # each reader's footprint exceeds half the maximum, so a 2nd storey would pass it
    for area in (fp["reading1"], fp["reading2"]):
        assert 2 * _D(area) > _D(b["maximum_floor_area_sqft"])


def test_a_changed_storey_floor_area_makes_the_arithmetic_fail():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "made-up-building-a":
            row["numbers_block"]["storeys"][0]["floor_area_sqft"] = "9999"
    errs = step_p6.block_and_word_errors(CID, data)
    assert errs and any("made-up-building-a" in m for m in errs), errs


# --------------------------------------------------------------------------
# the estimate's four figures follow from the floor area the building holds
# --------------------------------------------------------------------------
def test_estimate_four_figures_follow_from_the_floor_area():
    for rid in ("made-up-estimate-a", "made-up-estimate-b", "real-estimate-b"):
        b = _block(rid)
        fa = _D(b["floor_area_sqft"])
        apt = _D(b["apartment_size_sqft"])
        for share, qk, wb, wa in (
            ("share_low", "quotient_low", "whole_below_low", "whole_above_low"),
            ("share_high", "quotient_high", "whole_below_high", "whole_above_high"),
        ):
            exact = fa * _D(b[share]) / apt
            assert _r2(exact) == _D(b[qk]), rid
            assert b[wb] == int(exact)  # floor for a positive quotient
            assert b[wa] == int(exact) + 1


def test_real_estimate_a_both_floor_areas_give_the_same_two_decimal_quotients():
    b = _block("real-estimate-a")
    fa = b["floor_area_sqft"]
    assert set(fa) == {"reading1", "reading2"}
    for area in (fa["reading1"], fa["reading2"]):
        assert _r2(_D(area) * _D("0.60") / _D("700")) == _D(b["quotient_low"])
        assert _r2(_D(area) * _D("0.75") / _D("700")) == _D(b["quotient_high"])


def test_a_changed_estimate_figure_makes_its_test_fail():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "made-up-estimate-a":
            row["numbers_block"]["quotient_low"] = "99.99"
    errs = step_p6.block_and_word_errors(CID, data)
    assert errs and any("made-up-estimate-a" in m and "quotient_low" in m for m in errs), errs


# --------------------------------------------------------------------------
# the legal dwelling-unit ceiling, apart from the estimate
# --------------------------------------------------------------------------
def test_the_legal_unit_ceiling_rows_are_29_and_recompute():
    for rid in ("made-up-unit-limit", "real-unit-limit"):
        row = next(r for r in CASES[CID]["rows"] if r["row_id"] == rid)
        assert row["expected"]["value"] == 29
        assert row["expected"]["unit"] == "dwelling units"
        assert lib.recompute_row_errors(CID, row) == [], rid
    # the real-lot ceiling restates the settled real-lot#L6 and does not supersede it
    real = next(r for r in CASES[CID]["rows"] if r["row_id"] == "real-unit-limit")
    assert "real-lot#L6" in real["source_reference"]
    assert "L6" in real["does_not_establish"]


# --------------------------------------------------------------------------
# what the example is and is not; the marks; the forbidden words (point 5, 13, 14)
# --------------------------------------------------------------------------
def test_a_building_row_without_the_point5_words_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "made-up-building-a":
            row["does_not_establish"] = row["does_not_establish"].replace(
                "method of the example", "approach")
    errs = step_p6.block_and_word_errors(CID, data)
    assert errs and any("method of the example" in m for m in errs), errs


def test_an_estimate_row_calling_its_figures_validated_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "made-up-estimate-a":
            row["expected"]["value"] += " These are validated apartment numbers."
    errs = step_p6.block_and_word_errors(CID, data)
    assert errs and any("validated" in m for m in errs), errs


def test_an_estimate_row_whose_share_lacks_preliminary_assumption_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "made-up-estimate-a":
            for mark in row["numbers_block"]["marks"]:
                if mark["role"] == "share_range":
                    mark["basis"] = "an unvalidated sensitivity range chosen by the owner"
    errs = step_p6.block_and_word_errors(CID, data)
    assert errs and any("preliminary assumption" in m for m in errs), errs


def test_a_building_figure_marked_as_neither_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "made-up-building-a":
            row["numbers_block"]["marks"][0]["mark"] = "best_guess"
    errs = step_p6.block_and_word_errors(CID, data)
    assert errs and any("neither a legal requirement nor a chosen design assumption" in m
                        for m in errs), errs


def test_an_assumption_marked_as_a_legal_requirement_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "made-up-building-a":
            for mark in row["numbers_block"]["marks"]:
                if mark["role"] == "floor_to_floor":
                    mark["mark"] = "legal_requirement"
    errs = step_p6.block_and_word_errors(CID, data)
    assert errs and any("chosen design assumption called a legal requirement" in m
                        for m in errs), errs


# --------------------------------------------------------------------------
# one current answer per question; the reach rows do not move
# --------------------------------------------------------------------------
def test_l15_is_superseded_by_the_step_p6_building_rows_and_targets_are_current():
    with pytest.raises(lib.RowSuperseded) as exc:
        lib.load_row("real-lot", "L15")
    assert "step-p6-worked#real-building-a" in str(exc.value)
    assert "step-p6-worked#real-building-b" in str(exc.value)
    historical = lib.load_row("real-lot", "L15", allow_superseded=True)
    assert historical["kind"] == "not_known" and historical["value"] is None
    assert lib.load_row(CID, "real-building-a")["superseded_by"] == []
    assert lib.load_row(CID, "real-building-b")["superseded_by"] == []


def test_the_reach_rows_are_byte_stable():
    cr = lib.load_case("corner-reach")
    reach = [r for r in cr["rows"] if r["row_id"] in
             ("real-lot-reach", "C1-reach", "C2-reach", "C3-reach")]
    assert [r["row_id"] for r in reach] == ["real-lot-reach", "C1-reach", "C2-reach", "C3-reach"]
    blob = json.dumps(reach, sort_keys=True, ensure_ascii=False)
    assert hashlib.sha256(blob.encode()).hexdigest() == REACH_ROWS_DIGEST
