"""Step-P5 acceptance tests for the R6B reference cases (M4-T035, D-090 R291/R513/R516/R526/R548).

The step-P5 case reads the 46 Zoning Resolution texts captured by tasks M4-T033
and M4-T034 (the mixed-building floor-area sections ZR 35-30 to 35-33 and the
floor-area-ratio definition; ZR 23-24 and the ZR 34-23 page; the ZR 12-10 energy,
building and story definitions; the fourteen parking, loading and bicycle
sections and a line per development option; and the benchmark lot's rear yard
from ZR 23-342 and 23-344). These tests prove: the two readings are present
unchanged (digest pinned); a value is recorded only where both readings agree;
the rows the two readings do not jointly settle stay not known; a value where the
readings differ is refused; a changed law quote is caught; and the step-P4 row
zr-34-23-sections is superseded by the step-P5 row zr-34-23-page (one current
answer per question). Kept in its own file so the main test module stays under
the 600-line focus threshold. Engine-free.
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
import r6b_reference_cases_step_p5 as step_p5  # noqa: E402

CASES = lib.load_all()


def test_the_two_step_p5_readings_are_present_unchanged():
    assert check.step_p5_reading_errors() == []
    for name, spec in step_p5.STEP_P5_READINGS.items():
        raw = (lib.PROVENANCE_DIR / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == spec["digest"], name
        text = raw.decode("utf-8")
        assert "sealed folder" in text, name
        assert text.rstrip().endswith("END-OF-REPORT"), name
    eleven = (lib.PROVENANCE_DIR / "return-independent-hand-calculation-11.md").read_text()
    twelve = (lib.PROVENANCE_DIR / "return-independent-hand-calculation-12.md").read_text()
    assert eleven != twelve


def test_a_changed_step_p5_reading_is_caught(monkeypatch):
    bad = {
        "return-independent-hand-calculation-11.md": {
            "marker": "one hard rule", "digest": "0" * 64,
        },
        "return-independent-hand-calculation-12.md":
            step_p5.STEP_P5_READINGS["return-independent-hand-calculation-12.md"],
    }
    monkeypatch.setattr(step_p5, "STEP_P5_READINGS", bad)
    errs = check.step_p5_reading_errors()
    assert errs and any("digest changed" in m for m in errs), errs


def test_step_p5_case_rows_name_both_readings():
    data = CASES["step-p5-worked"]
    for row in data["rows"]:
        assert check.both_readings_errors("step-p5-worked", row) == [], row["row_id"]


def test_step_p5_settled_rows():
    # settled where both readings agree on the same basis
    sections = lib.load_row("step-p5-worked", "mixed-use-sections")
    assert sections["kind"] == "value"
    assert "35-31" in sections["value"]
    combo = lib.load_row("step-p5-worked", "mixed-use-floor-area-combination")
    assert combo["kind"] == "value" and "combined cap" in combo["value"]
    shared = lib.load_row("step-p5-worked", "shared-floor-area-rule")
    assert shared["kind"] == "value" and "less" in shared["value"]
    # the made-up mixed building worked by hand
    attr = lib.load_row("step-p5-worked", "made-up-mixed-shared-attribution")
    assert attr["kind"] == "value"
    assert "83.58" in attr["value"] and "316.42" in attr["value"]
    res_far = lib.load_row("step-p5-worked", "made-up-mixed-residential-far")
    assert res_far["kind"] == "value" and "20,000" in res_far["value"]
    # the floor-area-ratio definition settles floor area = ratio x lot area for 100x100
    far100 = lib.load_row("step-p5-worked", "floor-area-ratio-made-up-100x100")
    assert far100["kind"] == "value" and "20,000" in far100["value"]
    assert "ratio x lot area" in far100["value"]
    # it settles the floor area, not the unit count: it names the standing step-P4 units row
    assert "made-up-100x100-units" in far100["value"]
    # the energy definitions
    for rid in ("fully-electrified-building-definition", "ultra-low-energy-building-definition",
                "energy-floor-area-exclusion", "proposed-building-energy-eligibility",
                "building-and-story-definitions"):
        assert lib.load_row("step-p5-worked", rid)["kind"] == "value", rid
    # the served transit-zone value is a recorded value, not a rule
    tz = lib.load_row("step-p5-worked", "transit-zone-value")
    assert tz["kind"] == "value" and "Outer Transit Zone" in tz["value"]
    # a development option line: rooming-unit parking is not required
    rooming = lib.load_row("step-p5-worked", "option-rooming-units")
    assert rooming["kind"] == "value" and "NOT required" in rooming["value"]


def test_step_p5_not_known_rows():
    # neither reading jointly settles these -> not known
    for rid in ("made-up-mixed-commercial-far", "made-up-mixed-whole-building-max",
                "zr-23-24-reach", "benchmark-rear-yard-23-342-23-344"):
        assert lib.load_row("step-p5-worked", rid)["kind"] == "not_known", rid
    # the rear-yard row names what would settle the part beyond the corner and the
    # standing step-P3 row it does not re-answer
    rear = lib.load_row("step-p5-worked", "benchmark-rear-yard-23-342-23-344")
    assert "real-lot-rear-yard-beyond-corner" in rear["reason"]
    assert "about 89.7 degrees" in rear["reason"] or "89.7" in rear["reason"]


def test_a_step_p5_unsettled_row_given_a_value_is_refused():
    data = copy.deepcopy(CASES["step-p5-worked"])
    for row in data["rows"]:
        if row["row_id"] == "made-up-mixed-commercial-far":
            row["expected"]["kind"] = "value"
            row["expected"]["value"] = "the commercial floor area ratio is 2.0"
            row["expected"]["reason"] = ""
    errs = step_p5.must_stay_not_known_errors("step-p5-worked", data)
    assert errs and any("made-up-mixed-commercial-far" in m for m in errs), errs


def test_a_step_p5_value_where_the_readings_differ_is_refused():
    data = copy.deepcopy(CASES["step-p5-worked"])
    for row in data["rows"]:
        if row["row_id"] == "benchmark-rear-yard-23-342-23-344":
            row["expected"]["kind"] = "value"
            row["expected"]["value"] = "no rear yard is required anywhere on the lot"
            row["expected"]["reason"] = ""
    errs = check.readings_differ_errors("step-p5-worked", data)
    assert errs and any("benchmark-rear-yard-23-342-23-344" in m for m in errs), errs


def test_a_changed_law_quote_in_a_step_p5_row_is_caught():
    data = copy.deepcopy(CASES["step-p5-worked"])
    target = next(r for r in data["rows"] if r["row_id"] == "mixed-use-sections")
    target["citations"][1]["quote"] = "this phrase is not in the capture at all"
    errs = check.citation_errors("step-p5-worked", target)
    assert errs and any("quoted words" in m and "mixed-use-sections" in m for m in errs), errs


def test_step_p5_supersedes_the_zr_34_23_sections_overlay_row():
    with pytest.raises(lib.RowSuperseded) as exc:
        lib.load_row("step-p4-worked", "zr-34-23-sections")
    assert "step-p5-worked#zr-34-23-page" in str(exc.value)
    # the step-P5 target is current (not itself superseded)
    assert lib.load_row("step-p5-worked", "zr-34-23-page")["superseded_by"] == []
    # the historical row is still readable on purpose and still carries its conclusion
    historical = lib.load_row("step-p4-worked", "zr-34-23-sections", allow_superseded=True)
    assert historical["superseded_by"] == ["step-p5-worked#zr-34-23-page"]
    assert historical["kind"] == "value"
