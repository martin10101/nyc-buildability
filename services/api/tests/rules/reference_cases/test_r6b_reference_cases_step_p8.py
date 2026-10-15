"""Step-P8 acceptance tests for the R6B reference cases (M5-T177).

The step-P8 case (``placement-building-b``) is the two independent readings of where
the three-storey Building B (20,150 sq ft zoning floor area, 10-ft floor-to-floor)
sits on lot 70 of block 7334 (215-16 Northern Boulevard, Queens) under Z1 (lot 70
alone) and how its floor area divides. These tests prove, one per input state:

* S1 - the two readings are present unchanged (digest pinned), and a changed one is
  caught; each header says it was given eighteen settled answers and that the earlier
  footprint answer real-building-b was left out.
* S2 - every row names both readings (-17 and -18); a law-citing row quotes captured
  words found in the cited capture; a changed law quote is caught.
* S3 - the rows the two readings do not jointly settle stay not known with a kind of
  gap, and a value where they differ is refused.
* S4 - the plate (6,716.67) and the footprint figure (6,716.66) are each pinned to
  their own exact recompute, each carries the stated-measure label, the physical floor
  plate is not checked, and every quantity carries exactly one of the nine bases.
* S5 - the area allocation at the stated 60% share sums (apartment + other = total)
  and every arithmetic step recomputes exactly; a changed apartment figure is caught.
* S6 - a placement or coverage row that omits its basis or the Z1 condition is refused.
* S7 - placement-building-b is wired in (CASE_IDS, REQUIRED_BASE_IDS, README, the
  rendered page byte-identical, program_result_errors empty, the other cases byte-
  stable, every support .py under 600 SLOC).

Kept in its own file; engine-free (imports nothing from app).
"""
from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import sys
from decimal import Decimal

_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import r6b_reference_cases_check as check  # noqa: E402
import r6b_reference_cases_lib as lib  # noqa: E402
import r6b_reference_cases_render as render  # noqa: E402
import r6b_reference_cases_step_p8 as step_p8  # noqa: E402

CASES = lib.load_all()
CID = "placement-building-b"

# The other cases' rows, pinned at the claim head: this task adds a case and must not
# touch any existing one. The digest proves byte-stability of all cases except the new
# one, without git.
# Moved by M5-T184: adding the step-P9 case benchmark-options-2-3-6-7 puts it into this
# "other" set (CASE_IDS minus placement-building-b), so the blob grew by that case's rows
# and the digest changed; no existing case's rows changed.
# Moved again by M5-T184 round 2: the round-2 correction changed two rows of that same
# benchmark case (opt67-cf-lot-coverage records only the agreed corner 80 percent; the
# whole-lot opt67-cf-max-footprint becomes not known), so this "other" blob - which includes
# the benchmark case - changed again; no existing case's rows changed.
OTHER_CASES_DIGEST = "964a5adccda38e0a39f0573cec340ebb65e1a1a7f3c501a4e5dfdf042ae4b314"


def _row(rid):
    return next(r for r in CASES[CID]["rows"] if r["row_id"] == rid)


def _step(rid, label):
    return next(s for s in _row(rid)["arithmetic"] if s["label"].startswith(label))


# --------------------------------------------------------------------------
# S1 - the two readings are present unchanged, and a changed one is caught
# --------------------------------------------------------------------------
def test_the_two_step_p8_readings_are_present_unchanged():
    assert check.step_p8_reading_errors() == []
    for name, spec in step_p8.STEP_P8_READINGS.items():
        raw = (lib.PROVENANCE_DIR / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == spec["digest"], name
        text = raw.decode("utf-8")
        assert "sealed folder" in text, name
        assert spec["marker"] in text, name
        assert text.rstrip().endswith("END-OF-REPORT"), name
    seventeen = (lib.PROVENANCE_DIR / "return-independent-hand-calculation-17.md").read_text()
    eighteen = (lib.PROVENANCE_DIR / "return-independent-hand-calculation-18.md").read_text()
    assert seventeen != eighteen
    # each header says the readers were given eighteen settled answers and that the
    # earlier footprint answer real-building-b was left out on purpose
    for text in (seventeen, eighteen):
        assert "EIGHTEEN answers settled by earlier readings" in text
        assert "real-building-b was left out on purpose" in text


def test_a_changed_step_p8_reading_is_caught(monkeypatch):
    bad = {
        "return-independent-hand-calculation-17.md":
            {"marker": "ONE-HARD-RULE STATEMENT", "digest": "0" * 64},
        "return-independent-hand-calculation-18.md":
            step_p8.STEP_P8_READINGS["return-independent-hand-calculation-18.md"],
    }
    monkeypatch.setattr(step_p8, "STEP_P8_READINGS", bad)
    errs = check.step_p8_reading_errors()
    assert errs and any("digest changed" in m for m in errs), errs


# --------------------------------------------------------------------------
# the whole case validates clean
# --------------------------------------------------------------------------
def test_step_p8_case_validates_clean():
    assert check.validate_case(CID, CASES[CID]) == []


# --------------------------------------------------------------------------
# S2 - every row names both readings and law-citing rows quote captured words
# --------------------------------------------------------------------------
def test_step_p8_rows_name_both_readings():
    for row in CASES[CID]["rows"]:
        assert check.both_readings_errors(CID, row) == [], row["row_id"]
        ref = row["source_reference"]
        assert "return-independent-hand-calculation-17" in ref, row["row_id"]
        assert "return-independent-hand-calculation-18" in ref, row["row_id"]


def test_every_step_p8_citation_matches_the_capture():
    cited = 0
    for row in CASES[CID]["rows"]:
        assert check.citation_errors(CID, row) == [], row["row_id"]
        cited += len(row["citations"])
    assert cited >= 6, "the law-bearing rows quote captured ZR text"


def test_a_changed_law_quote_in_a_step_p8_row_is_caught():
    data = copy.deepcopy(CASES[CID])
    target = next(r for r in data["rows"] if r["row_id"] == "lot-coverage-max")
    target["citations"][0]["quote"] = "this phrase is not in the capture at all"
    errs = check.citation_errors(CID, target)
    assert errs and any("quoted words" in m and "lot-coverage-max" in m for m in errs), errs


# --------------------------------------------------------------------------
# S3 - the rows the two readings do not jointly settle stay not known
# --------------------------------------------------------------------------
def test_step_p8_not_settled_rows_stay_not_known_with_a_kind_of_gap():
    for rid in step_p8.MUST_STAY_NOT_KNOWN[CID]:
        r = lib.load_row(CID, rid)
        assert r["kind"] == "not_known", rid
        assert r["value"] is None, rid
        reason = r["reason"].lower()
        assert "kind of gap" in reason, rid
        assert ("missing fact about the property" in reason
                or "unresolved law" in reason), rid


def test_a_step_p8_value_where_the_readings_differ_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "gis-conflict-check":
            row["expected"]["kind"] = "value"
            row["expected"]["value"] = "the GIS outline is the correct basis"
            row["expected"]["reason"] = ""
    errs = step_p8.must_stay_not_known_errors(CID, data)
    assert errs and any("gis-conflict-check" in m for m in errs), errs


# --------------------------------------------------------------------------
# S4 - the plate and the footprint figure, each pinned; the label; the physical plate
# --------------------------------------------------------------------------
def test_the_plate_and_the_footprint_are_each_pinned_to_their_recompute():
    plate = _row("plate")
    assert plate["expected"]["value"] == "6716.67"
    assert lib.recompute_row_errors(CID, plate) == []
    foot = _row("footprint-tax-map")
    assert foot["expected"]["value"] == "6716.66"
    assert lib.recompute_row_errors(CID, foot) == []
    # 20,150 / 3 = 6,716.67 and 66.66 x 100.76 = 6,716.66 (0.01 sq ft apart, within +/-0.5)
    assert abs(Decimal("6716.67") - Decimal("6716.66")) <= Decimal("0.5")


def test_the_plate_and_footprint_carry_the_stated_measure_label():
    assert check.step_p8 is step_p8  # the checker wires the step-P8 guards
    assert step_p8.plate_label_errors(CID, CASES[CID]) == []


def test_a_figure_that_drops_the_stated_measure_label_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "footprint-tax-map":
            row["does_not_establish"] = "no label here"
            row["expected"]["value"] = "6716.66"
    errs = step_p8.plate_label_errors(CID, data)
    assert errs, errs
    assert any("footprint-tax-map" in m and "stated-measure label" in m for m in errs), errs


def test_the_physical_floor_plate_is_not_checked():
    r = lib.load_row(CID, "physical-plate-not-checked")
    assert r["kind"] == "not_known"
    assert r["value"] is None
    assert "physical floor plate" in r["reason"].lower()


# --------------------------------------------------------------------------
# S4 - every quantity carries exactly one of the nine bases
# --------------------------------------------------------------------------
def test_module_nine_bases_equal_the_authoritative_set():
    sys.path.insert(0, str(lib.REPO_ROOT / "tools"))
    import research_record_check as rrc  # noqa: E402
    assert set(step_p8.QUANTITY_BASES) == set(rrc.QUANTITY_BASES)


def test_every_quantity_carries_one_of_the_nine_bases():
    seen = 0
    for row in CASES[CID]["rows"]:
        assert step_p8.quantity_basis_errors(CID, row) == [], row["row_id"]
        for q in row.get("quantities", []):
            seen += 1
            assert q["basis"] in step_p8.QUANTITY_BASES, (row["row_id"], q)
    assert seen >= 8, "the measured rows carry quantities with their basis"


def test_a_quantity_without_a_basis_is_refused():
    data = copy.deepcopy(CASES[CID])
    row = next(r for r in data["rows"] if r["row_id"] == "footprint-tax-map")
    row["quantities"][0]["basis"] = ""
    errs = step_p8.quantity_basis_errors(CID, row)
    assert errs and any("no measurement basis" in m for m in errs), errs


def test_a_quantity_with_a_basis_outside_the_nine_is_refused():
    data = copy.deepcopy(CASES[CID])
    row = next(r for r in data["rows"] if r["row_id"] == "gis-conflict-check")
    row["quantities"][0]["basis"] = "eyeball"
    errs = step_p8.quantity_basis_errors(CID, row)
    assert errs and any("is not one of the nine bases" in m for m in errs), errs


# --------------------------------------------------------------------------
# S5 - the area allocation sums and recomputes exactly
# --------------------------------------------------------------------------
def test_the_area_allocation_sums_and_recomputes():
    row = _row("area-allocation")
    assert lib.recompute_row_errors(CID, row) == []
    apt_total = Decimal(_step("area-allocation", "Apartment area, total")["result"])
    other_total = Decimal(_step("area-allocation", "Other building area, total")["result"])
    apt_storey = Decimal(_step("area-allocation", "Apartment area, per storey")["result"])
    other_storey = Decimal(_step("area-allocation", "Other building area, per storey")["result"])
    assert apt_total == Decimal("12090.00")
    assert other_total == Decimal("8060.00")
    assert apt_total + other_total == Decimal("20150.00")        # apartment + other = total
    assert apt_storey + other_storey == Decimal("6716.67")       # per-storey = the plate


def test_a_changed_allocation_apartment_figure_is_caught():
    row = copy.deepcopy(_row("area-allocation"))
    # the apartment total result moved by 1 (12,090.00 -> 12,091.00)
    for step in row["arithmetic"]:
        if step["label"].startswith("Apartment area, total"):
            step["result"] = "12091.00"
    errs = lib.recompute_row_errors(CID, row)
    assert errs and any("area-allocation" in m for m in errs), errs


# --------------------------------------------------------------------------
# S6 - no placement or coverage conclusion without its basis and the Z1 condition
# --------------------------------------------------------------------------
def test_placement_and_coverage_rows_name_basis_and_z1():
    assert step_p8.placement_basis_errors(CID, CASES[CID]) == []


def test_a_placement_row_without_its_basis_or_z1_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "placement-tax-map":
            row["expected"]["value"] = "the building touches three lot lines and clears the back"
            row["expected"]["reason"] = ""
            row["quantity"] = "the placement"
            row["does_not_establish"] = "an illustration only"
    errs = step_p8.placement_basis_errors(CID, data)
    assert errs and any("placement-tax-map" in m and "basis" in m for m in errs), errs
    assert any("placement-tax-map" in m and "Z1" in m for m in errs), errs


# --------------------------------------------------------------------------
# S4 - nothing from a program run
# --------------------------------------------------------------------------
def test_step_p8_program_result_errors_is_empty():
    assert check.program_result_errors(CID, CASES[CID]) == []


# --------------------------------------------------------------------------
# S7 - the new case is wired in and the other cases stay byte-stable
# --------------------------------------------------------------------------
def test_step_p8_case_is_wired_in():
    assert CID in lib.CASE_IDS
    assert CID in lib.REQUIRED_BASE_IDS
    assert check.coverage_errors(CID, CASES[CID]) == []
    assert lib.case_path(CID).is_file()
    assert lib.page_path(CID).is_file()
    assert CID in (lib.DOCS_DIR / "README.md").read_text()


def test_step_p8_page_is_byte_identical_to_the_renderer():
    assert render.render_page(CASES[CID]) == lib.page_path(CID).read_text()


def test_other_cases_rows_are_byte_stable():
    other = [c for c in lib.CASE_IDS if c != CID]
    blob = json.dumps({cid: lib.load_case(cid)["rows"] for cid in other},
                      sort_keys=True, ensure_ascii=False)
    assert hashlib.sha256(blob.encode()).hexdigest() == OTHER_CASES_DIGEST


def test_support_files_stay_under_600_lines():
    for path in _HERE.glob("*.py"):
        lines = len(path.read_text().splitlines())
        assert lines < 600, f"{path.name} has {lines} lines (keep each file focused)"


# --------------------------------------------------------------------------
# wording: no forbidden present-tense "not captured" phrasing in the new case
# --------------------------------------------------------------------------
def test_no_forbidden_present_tense_wording_in_the_step_p8_case():
    forbidden = ("does not hold", "is not captured", "are not captured",
                 "not captured", "uncaptured")
    data = CASES[CID]

    def walk(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "change_log":
                    continue
                walk(v, path + [str(k)])
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, path + [str(i)])
        elif isinstance(node, str):
            low = node.lower()
            for p in forbidden:
                assert p not in low, (p, "/".join(path), node[:80])

    walk(data, [])
