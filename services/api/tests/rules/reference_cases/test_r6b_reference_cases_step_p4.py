"""Step-P4 acceptance tests for the R6B reference cases (M4-T032, D-090 R226/R241/R259/R291/R318).

The step-P4 case reads the law text captured by task M4-T031 (ZR 34-22 and 34-23
and their sections, ZR 35-22 and ZR 35-62 to 35-643, ZR 23-44, and the lot-coverage,
yard, street-wall, large-site, qualifying-residential-site, dwelling-unit and
qualifying-housing definitions). These tests prove: the two readings are present
unchanged (digest pinned); a value is recorded only where both readings agree; the
rows the two readings do not jointly settle stay not known; and the three
overlay-reading rows held subject to ZR 34-21 through 34-23 are superseded by the
step-P4 rows (one current answer per question). Kept in its own file so the main
test module stays under the 600-line focus threshold. Engine-free.
"""
from __future__ import annotations

import copy
import hashlib
import pathlib
import sys

import pytest

_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import r6b_reference_cases_check as check  # noqa: E402
import r6b_reference_cases_lib as lib  # noqa: E402
import r6b_reference_cases_step_p4 as step_p4  # noqa: E402

CASES = lib.load_all()


def test_the_two_step_p4_readings_are_present_unchanged():
    assert check.step_p4_reading_errors() == []
    for name, spec in step_p4.STEP_P4_READINGS.items():
        raw = (lib.PROVENANCE_DIR / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == spec["digest"], name
        text = raw.decode("utf-8")
        assert "sealed folder" in text, name
        assert text.rstrip().endswith("END-OF-REPORT"), name
    nine = (lib.PROVENANCE_DIR / "return-independent-hand-calculation-9.md").read_text()
    ten = (lib.PROVENANCE_DIR / "return-independent-hand-calculation-10.md").read_text()
    assert nine != ten


def test_a_changed_step_p4_reading_is_caught(monkeypatch):
    bad = {
        "return-independent-hand-calculation-9.md": {
            "marker": "ONE HARD RULE", "digest": "0" * 64,
        },
        "return-independent-hand-calculation-10.md":
            step_p4.STEP_P4_READINGS["return-independent-hand-calculation-10.md"],
    }
    monkeypatch.setattr(step_p4, "STEP_P4_READINGS", bad)
    errs = check.step_p4_reading_errors()
    assert errs and any("digest changed" in m for m in errs), errs


def test_step_p4_case_rows_name_both_readings():
    data = CASES["step-p4-worked"]
    for row in data["rows"]:
        assert check.both_readings_errors("step-p4-worked", row) == [], row["row_id"]


def test_step_p4_settled_and_not_known_rows():
    # settled where both readings agree on the same basis
    assert lib.load_row("step-p4-worked", "floor-area-ratio")["kind"] == "value"
    assert "same as plain R6B" in lib.load_row("step-p4-worked", "floor-area-ratio")["value"]
    assert lib.load_row("step-p4-worked", "lot-coverage")["kind"] == "value"
    assert lib.load_row("step-p4-worked", "rear-yard")["kind"] == "value"
    assert lib.load_row("step-p4-worked", "large-site")["kind"] == "value"
    assert lib.load_row("step-p4-worked", "qualifying-residential-site")["kind"] == "value"
    # the made-up 100x100 unit count is a conditional value (29, held by both readings
    # subject to the floor-area-ratio definition the readers did not have)
    units = lib.load_row("step-p4-worked", "made-up-100x100-units")
    assert units["kind"] == "value"
    assert "29" in units["value"] and "floor area ratio" in units["value"]
    # the rear-yard row records reading 9's completeness caveat (one reading holds a
    # condition the other does not); the answer is still "same as plain R6B"
    rear = lib.load_row("step-p4-worked", "rear-yard")
    assert "same as plain R6B" in rear["value"]
    assert "return-independent-hand-calculation-9.md" in rear["value"]
    # neither reading jointly settles these -> not known
    for rid in ("real-lot-prevailing-frontage", "zr-23-443-reach"):
        assert lib.load_row("step-p4-worked", rid)["kind"] == "not_known", rid


def test_a_step_p4_unsettled_row_given_a_value_is_refused():
    data = copy.deepcopy(CASES["step-p4-worked"])
    for row in data["rows"]:
        if row["row_id"] == "real-lot-prevailing-frontage":
            row["expected"]["kind"] = "value"
            row["expected"]["value"] = "yes, the lot has a prevailing street wall frontage"
            row["expected"]["reason"] = ""
    errs = step_p4.must_stay_not_known_errors("step-p4-worked", data)
    assert errs and any("real-lot-prevailing-frontage" in m for m in errs), errs


def test_a_step_p4_value_where_the_readings_differ_is_refused():
    data = copy.deepcopy(CASES["step-p4-worked"])
    for row in data["rows"]:
        if row["row_id"] == "zr-23-443-reach":
            row["expected"]["kind"] = "value"
            row["expected"]["value"] = "ZR 23-443(c) does not apply"
            row["expected"]["reason"] = ""
    errs = check.readings_differ_errors("step-p4-worked", data)
    assert errs and any("zr-23-443-reach" in m for m in errs), errs


def test_step_p4_supersedes_the_three_overlay_rows_held_subject_to_34_21_through_34_23():
    # the three overlay rows now carry superseded_by pointing to the step-P4 rows
    for rid in ("floor-area-ratio", "lot-coverage", "rear-yard"):
        with pytest.raises(lib.RowSuperseded) as exc:
            lib.load_row("overlay-reading", rid)
        assert f"step-p4-worked#{rid}" in str(exc.value), rid
        # the step-P4 target is current (not itself superseded)
        assert lib.load_row("step-p4-worked", rid)["superseded_by"] == []
