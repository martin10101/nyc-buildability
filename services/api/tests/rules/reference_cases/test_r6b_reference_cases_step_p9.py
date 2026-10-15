"""Step-P9 acceptance tests for the R6B reference cases (M5-T184).

The step-P9 case (``benchmark-options-2-3-6-7``) is the agreed worked values of
options 2 (qualifying affordable housing), 3 (qualifying senior housing), 6
(residences with a community facility) and 7 (a community facility alone) for the
benchmark lot (215-16 Northern Boulevard, lot 70 of block 7334; R6B with a C2-2
overlay; corner), read independently twice per option (option 2: provenance -19 and
-20; option 3: -21 and -22; options 6 and 7: -23 and -24) and confirmed by an
independent comparer (-25). These tests prove, one per input state:

* S1 - the seven reading files -19..-25 are present unchanged (digest pinned), each
  carries its marker and END-OF-REPORT, says it was made from the sealed folder, does
  NOT claim "no outside access"; a changed byte is caught.
* S2 - every option row names BOTH its readings and a shared row names the comparer;
  a row naming only one reading (or the wrong pair) is refused; a changed law quote is
  caught (the case is deliberately NOT in check.py CASE_READINGS).
* S3 - every citation cites a captured section whose snapshot exists; the uncaptured
  sections are never a value basis or a formal citation.
* S4 - the rows the two readings do not jointly settle stay not known with a kind of
  gap; a value where they differ is refused.
* S5 - the qualifying-housing and community-facility use-permission rows carry the
  eligibility caveat; no forbidden present-tense "not captured" wording appears.
* S6 - every quantity carries exactly one of the nine bases (equal to the
  authoritative set); the recorded 10,075 and the GIS 10,387.99 are never combined.
* S7 - the arithmetic recomputes exactly (24,180; 4,030; 35; 20,150; 8,060; 6,045);
  the 24-11 rows carry table_assertion null; a changed operand is caught.
* S8 - no unconditional "no rear yard"; the corner waiver names its condition.
* S9 - the case is wired in (CASE_IDS, REQUIRED_BASE_IDS, README, the page
  byte-identical, program_result_errors empty, other cases byte-stable, support .py
  files under 600 lines).

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
import r6b_reference_cases_step_p9 as step_p9  # noqa: E402

CASES = lib.load_all()
CID = "benchmark-options-2-3-6-7"

# Every case except the new one, pinned at the claim head: this task adds a case and
# must not touch any existing one. The digest proves byte-stability without git.
PRIOR_CASES_DIGEST = "f5e61b1a99a0bf6d0da5fb918090635318802ed5c8675afcaefd3b4ac3fed15a"

# The sections the readers did not have among the captures: they must never be a value
# basis or a formal citation (they are named in prose only).
UNCAPTURED_SECTIONS = ("23-154", "23-63", "74-902", "74-903",
                       "22-131", "22-132", "22-133", "22-134", "22-135")


def _row(rid):
    return next(r for r in CASES[CID]["rows"] if r["row_id"] == rid)


def _step_result(rid, label):
    stp = next(s for s in _row(rid)["arithmetic"] if s["label"].startswith(label))
    return Decimal(stp["result"])


# --------------------------------------------------------------------------
# S1 - the seven reading files are present unchanged, and a changed one is caught
# --------------------------------------------------------------------------
def test_the_seven_step_p9_readings_are_present_unchanged():
    assert check.step_p9 is step_p9  # the checker wires the step-P9 guards
    assert step_p9.reading_digest_errors() == []
    assert len(step_p9.STEP_P9_READINGS) == 7
    for name, spec in step_p9.STEP_P9_READINGS.items():
        raw = (lib.PROVENANCE_DIR / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == spec["digest"], name
        text = raw.decode("utf-8")
        assert "sealed folder" in text, name
        assert spec["marker"] in text, name
        assert "no outside access" not in text, name
        assert text.rstrip().endswith("END-OF-REPORT"), name


def test_a_changed_step_p9_reading_is_caught(monkeypatch):
    bad = dict(step_p9.STEP_P9_READINGS)
    bad["return-independent-hand-calculation-19.md"] = {
        "marker": "M5-T184 PROVENANCE -19 (OPTION 2, READING A)", "digest": "0" * 64}
    monkeypatch.setattr(step_p9, "STEP_P9_READINGS", bad)
    errs = step_p9.reading_digest_errors()
    assert errs and any("digest changed" in m for m in errs), errs


# --------------------------------------------------------------------------
# the whole case validates clean
# --------------------------------------------------------------------------
def test_step_p9_case_validates_clean():
    assert check.validate_case(CID, CASES[CID]) == []


# --------------------------------------------------------------------------
# S2 - every option row names both readings; a shared row names the comparer
# --------------------------------------------------------------------------
def test_step_p9_rows_name_their_readings():
    assert step_p9.reading_pair_errors(CID, CASES[CID]) == []
    for row in CASES[CID]["rows"]:
        rid = row["row_id"]
        ref = row["source_reference"]
        if rid.startswith("opt2-"):
            assert "return-independent-hand-calculation-19" in ref, rid
            assert "return-independent-hand-calculation-20" in ref, rid
        elif rid.startswith("opt3-"):
            assert "return-independent-hand-calculation-21" in ref, rid
            assert "return-independent-hand-calculation-22" in ref, rid
        elif rid.startswith(("opt6-", "opt7-", "opt67-")):
            assert "return-independent-hand-calculation-23" in ref, rid
            assert "return-independent-hand-calculation-24" in ref, rid
        else:
            assert "return-independent-hand-calculation-25" in ref, rid


def test_an_option_row_naming_only_one_reading_is_refused():
    data = copy.deepcopy(CASES[CID])
    target = next(r for r in data["rows"] if r["row_id"] == "opt2-max-residential-fa")
    target["source_reference"] = "return-independent-hand-calculation-19.md only (one reading)."
    errs = step_p9.reading_pair_errors(CID, data)
    assert errs and any("opt2-max-residential-fa" in m and "both" in m.lower() for m in errs), errs


def test_an_option_row_naming_the_wrong_pair_is_refused():
    data = copy.deepcopy(CASES[CID])
    target = next(r for r in data["rows"] if r["row_id"] == "opt2-heights")
    # names the option-3 pair instead of the option-2 pair
    target["source_reference"] = ("return-independent-hand-calculation-21.md and "
                                  "return-independent-hand-calculation-22.md.")
    errs = step_p9.reading_pair_errors(CID, data)
    assert errs and any("opt2-heights" in m for m in errs), errs


def test_a_shared_row_without_the_comparer_is_refused():
    data = copy.deepcopy(CASES[CID])
    target = next(r for r in data["rows"] if r["row_id"] == "options-out-of-scope")
    target["source_reference"] = "no reading named here."
    errs = step_p9.reading_pair_errors(CID, data)
    assert errs and any("options-out-of-scope" in m and "comparer" in m for m in errs), errs


# --------------------------------------------------------------------------
# S3 - every citation is a captured section; uncaptured sections never cited
# --------------------------------------------------------------------------
def test_every_step_p9_citation_matches_the_capture():
    cited = 0
    for row in CASES[CID]["rows"]:
        assert check.citation_errors(CID, row) == [], row["row_id"]
        for cite in row["citations"]:
            cited += 1
            assert cite["kind"] == "captured", (row["row_id"], cite["section"])
            assert (lib.REPO_ROOT / cite["snapshot_file"]).is_file(), cite["snapshot_id"]
    assert cited >= 20, "the value-bearing rows quote captured ZR text"


def test_uncaptured_sections_are_never_a_formal_citation():
    for row in CASES[CID]["rows"]:
        for cite in row["citations"]:
            section = str(cite["section"])
            for bad in UNCAPTURED_SECTIONS:
                assert bad not in section, (row["row_id"], section, bad)


def test_a_changed_law_quote_in_a_step_p9_row_is_caught():
    data = copy.deepcopy(CASES[CID])
    target = next(r for r in data["rows"] if r["row_id"] == "opt6-cf-max-fa")
    target["citations"][0]["quote"] = "this phrase is not in the capture at all"
    errs = check.citation_errors(CID, target)
    assert errs and any("quoted words" in m and "opt6-cf-max-fa" in m for m in errs), errs


# --------------------------------------------------------------------------
# S4 - the rows the two readings do not jointly settle stay not known
# --------------------------------------------------------------------------
def test_step_p9_not_settled_rows_stay_not_known_with_a_kind_of_gap():
    for rid in step_p9.MUST_STAY_NOT_KNOWN[CID]:
        r = lib.load_row(CID, rid)
        assert r["kind"] == "not_known", rid
        assert r["value"] is None, rid
        reason = r["reason"].lower()
        assert "kind of gap" in reason, rid
        assert ("missing fact about the property" in reason
                or "unresolved law" in reason), rid


def test_a_step_p9_value_where_the_readings_differ_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "opt3-max-dwelling-units":
            row["expected"]["kind"] = "value"
            row["expected"]["value"] = "35"
            row["expected"]["reason"] = ""
    errs = step_p9.must_stay_not_known_errors(CID, data)
    assert errs and any("opt3-max-dwelling-units" in m for m in errs), errs


# --------------------------------------------------------------------------
# S5 - eligibility caveat and forbidden present-tense wording
# --------------------------------------------------------------------------
def test_eligibility_rows_carry_the_caveat():
    assert step_p9.eligibility_errors(CID, CASES[CID]) == []
    for row in CASES[CID]["rows"]:
        rid = row["row_id"]
        if rid.startswith(("opt2-", "opt3-")) or rid in (
                "opt67-use-group-iii", "opt67-which-uses-not-known"):
            assert "decides no eligibility" in row["does_not_establish"].lower(), rid


def test_a_qualifying_housing_row_without_the_eligibility_caveat_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "opt3-senior-definitions":
            row["does_not_establish"] = "no caveat here."
    errs = step_p9.eligibility_errors(CID, data)
    assert errs and any("opt3-senior-definitions" in m for m in errs), errs


def test_no_forbidden_present_tense_wording_in_the_step_p9_case():
    assert step_p9.forbidden_wording_errors(CID, CASES[CID]) == []


def test_a_forbidden_not_captured_phrase_is_caught():
    data = copy.deepcopy(CASES[CID])
    data["rows"][0]["why_applies"] = "this section is not captured in the snapshot folder"
    errs = step_p9.forbidden_wording_errors(CID, data)
    assert errs and any("not captured" in m for m in errs), errs


# --------------------------------------------------------------------------
# S6 - every quantity carries exactly one of the nine bases
# --------------------------------------------------------------------------
def test_module_nine_bases_equal_the_authoritative_set():
    sys.path.insert(0, str(lib.REPO_ROOT / "tools"))
    import research_record_check as rrc  # noqa: E402
    assert set(step_p9.QUANTITY_BASES) == set(rrc.QUANTITY_BASES)


def test_every_quantity_carries_one_of_the_nine_bases():
    assert step_p9.quantity_basis_errors(CID, CASES[CID]) == []
    seen = 0
    bases = set()
    for row in CASES[CID]["rows"]:
        for q in row.get("quantities", []):
            seen += 1
            bases.add(q["basis"])
            assert q["basis"] in step_p9.QUANTITY_BASES, (row["row_id"], q)
    assert seen >= 15, "the measured rows carry quantities with their basis"
    assert "administrative_record" in bases  # the recorded lot area
    assert "derived" in bases
    assert "law" in bases


def test_a_quantity_without_a_basis_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "opt2-max-residential-fa":
            row["quantities"][0]["basis"] = ""
    errs = step_p9.quantity_basis_errors(CID, data)
    assert errs and any("no measurement basis" in m for m in errs), errs


def test_a_quantity_with_a_basis_outside_the_nine_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "opt6-cf-far":
            row["quantities"][0]["basis"] = "eyeball"
    errs = step_p9.quantity_basis_errors(CID, data)
    assert errs and any("is not one of the nine bases" in m for m in errs), errs


def test_recorded_and_gis_areas_are_never_combined():
    assert step_p9.no_mixed_basis_errors(CID, CASES[CID]) == []
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "opt2-max-residential-fa":
            row["arithmetic"][0]["operands"].append(
                {"name": "gis outline area", "value": "10387.99"})
    errs = step_p9.no_mixed_basis_errors(CID, data)
    assert errs and any("mixes the recorded area" in m for m in errs), errs


# --------------------------------------------------------------------------
# S7 - the arithmetic recomputes exactly; the 24-11 rows carry table_assertion null
# --------------------------------------------------------------------------
def test_step_p9_arithmetic_recomputes():
    for rid in ("opt2-max-residential-fa", "opt2-uap-affordable-fa", "opt2-max-dwelling-units",
                "opt6-cf-max-fa", "opt6-combined-max-fa", "opt67-cf-max-footprint",
                "opt2-vs-option-1", "opt3-vs-option-1"):
        assert lib.recompute_row_errors(CID, _row(rid)) == [], rid
    checks = [
        ("opt2-max-residential-fa", "Maximum residential floor area", "24180"),
        ("opt2-uap-affordable-fa", "Affordable floor area", "4030"),
        ("opt2-max-dwelling-units", "Maximum dwelling units", "35"),
        ("opt6-cf-max-fa", "Community-facility maximum floor area", "20150"),
        ("opt67-cf-max-footprint", "Corner-portion maximum footprint", "8060"),
        ("opt67-cf-max-footprint", "Interior-portion maximum footprint", "6045"),
    ]
    for rid, label, want in checks:
        assert _step_result(rid, label) == Decimal(want), (rid, label)


def test_the_24_11_rows_carry_table_assertion_null():
    seen = 0
    for row in CASES[CID]["rows"]:
        for cite in row["citations"]:
            if cite["snapshot_id"] == "zr-24-11":
                seen += 1
                assert cite["table_assertion"] is None, row["row_id"]
    assert seen >= 3, "the 24-11 FAR/coverage rows cite the plural-tables section"


def test_the_23_22_and_23_432_rows_use_the_table_assertion():
    seen = 0
    for row in CASES[CID]["rows"]:
        for cite in row["citations"]:
            if cite["snapshot_id"] in ("zr-23-22", "zr-23-432"):
                seen += 1
                assert cite["table_assertion"] is not None, row["row_id"]
                assert cite["table_assertion"]["district"] == "R6B", row["row_id"]
    assert seen >= 4, "options 2 and 3 pin the R6B table rows via table_assertion"


def test_a_changed_operand_is_caught_and_names_its_row():
    row = copy.deepcopy(_row("opt6-cf-max-fa"))
    row["arithmetic"][0]["operands"][0]["value"] = "2.50"  # was 2.00
    errs = lib.recompute_row_errors(CID, row)
    assert errs and any("opt6-cf-max-fa" in m for m in errs), errs


# --------------------------------------------------------------------------
# S8 - no unconditional "no rear yard"; the corner waiver names its condition
# --------------------------------------------------------------------------
def test_rear_yard_rows_name_condition_and_scope():
    assert step_p9.rear_yard_errors(CID, CASES[CID]) == []


def test_a_rear_yard_row_that_drops_its_condition_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "opt67-corner-rear-yard-waiver":
            row["expected"]["value"] = "no rear yard for the zoning lot under Z1"
            row["expected"]["reason"] = ""
            row["quantity"] = "the corner rear-yard waiver"
            row["why_applies"] = "the corner waiver applies"
            row["does_not_establish"] = "an illustration only"
    errs = step_p9.rear_yard_errors(CID, data)
    assert errs and any("opt67-corner-rear-yard-waiver" in m for m in errs), errs


# --------------------------------------------------------------------------
# S4 - nothing from a program run
# --------------------------------------------------------------------------
def test_step_p9_program_result_errors_is_empty():
    assert check.program_result_errors(CID, CASES[CID]) == []


# --------------------------------------------------------------------------
# S9 - the new case is wired in and the other cases stay byte-stable
# --------------------------------------------------------------------------
def test_step_p9_case_is_wired_in():
    assert CID in lib.CASE_IDS
    assert CID in lib.REQUIRED_BASE_IDS
    assert check.coverage_errors(CID, CASES[CID]) == []
    assert lib.case_path(CID).is_file()
    assert lib.page_path(CID).is_file()
    assert CID in (lib.DOCS_DIR / "README.md").read_text()


def test_step_p9_page_is_byte_identical_to_the_renderer():
    assert render.render_page(CASES[CID]) == lib.page_path(CID).read_text()


def test_prior_cases_rows_are_byte_stable():
    other = [c for c in lib.CASE_IDS if c != CID]
    blob = json.dumps({cid: lib.load_case(cid)["rows"] for cid in other},
                      sort_keys=True, ensure_ascii=False)
    assert hashlib.sha256(blob.encode()).hexdigest() == PRIOR_CASES_DIGEST


def test_support_files_stay_under_600_lines():
    for path in _HERE.glob("*.py"):
        lines = len(path.read_text().splitlines())
        assert lines < 600, f"{path.name} has {lines} lines (keep each file focused)"
