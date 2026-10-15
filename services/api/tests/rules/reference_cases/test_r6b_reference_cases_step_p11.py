"""Step-P11 acceptance tests for the R6B reference cases (M5-T186).

The step-P11 case (``benchmark-options-4-11``) is the agreed worked values of option 4
(more, smaller apartments) and option 11 (all programs combined) for the benchmark lot
(215-16 Northern Boulevard, lot 70 of block 7334; R6B with a C2-2 overlay; corner), read
independently twice per option (option 4: provenance -32 and -33; option 11: -35 and -36)
and confirmed by an independent comparer per option (option 4: -34; option 11: -37). With
options 4 and 11 recorded the eleven-option set is complete across the reference cases.
These tests prove, one per input state:

* S1 - the six new reading files -32..-37 are present unchanged (digest pinned), each
  carries its marker and END-OF-REPORT, says it was made from the sealed folder, does NOT
  claim "no outside access"; a changed byte is caught.
* S2 - every option row names BOTH its readings AND its comparer, and a shared row names
  both comparers; a row naming only one reading, the wrong pair, or the wrong comparer is
  refused (the case is deliberately NOT in check.py CASE_READINGS: two reading pairs AND
  two comparers).
* S3 - every citation cites a captured section whose snapshot exists; the uncaptured
  sections (76-131, 23-154, 77-00, 35-34) are never a value basis or a formal citation.
* S4 - the rows the two readings do not jointly settle stay not known; a value where they
  differ is refused; the street-wall row stays not known and records no 8-foot quantity
  (the comparer's correction is an adjudicator's note, never a recorded value).
* S5 - the eligibility rows carry the "decides no eligibility" caveat and the owner-question
  rows the "decides neither owner question" caveat; no forbidden present-tense "not
  captured" wording appears.
* S6 - every quantity carries exactly one of the nine bases (equal to the authoritative
  set); the recorded 10,075 and the GIS 10,387.99 are never combined.
* S7 - the arithmetic recomputes exactly (20,150; 24,180; 4,030; 29; 35) with the dwelling
  rounding boundaries; the plural-'tables' rows carry table_assertion null while
  23-22/23-432 use the assertion; a changed operand is caught.
* S8 - the mixed-building street-wall/height derivation path is recorded as an NB-06 draft
  reading; the carve-out row names the checked sections; option 11's duplicate figures
  cross-cite the prior cases and open no new floor-area pool.
* S9 - the case is wired in (CASE_IDS, REQUIRED_BASE_IDS, README, the page byte-identical,
  program_result_errors empty, other cases byte-stable, support .py files under 600 lines).

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
import r6b_reference_cases_step_p11 as step_p11  # noqa: E402

CASES = lib.load_all()
CID = "benchmark-options-4-11"

# Every case except the new one, pinned at the claim head: this task adds a case and must
# not touch any existing one. The digest proves byte-stability without git.
OTHER_CASES_DIGEST = "2bfd30e3f3122f7507af463adb382a36b924a0b6a3311bb2a898cd1d5accce5e"

# The sections the readers did not have among the captures: they must never be a value
# basis or a formal citation (they are named in prose only).
UNCAPTURED_SECTIONS = ("76-131", "23-154", "77-00", "35-34")

PLURAL_TABLES_SNAPSHOTS = ("zr-33-121", "zr-24-11")


def _row(rid):
    return next(r for r in CASES[CID]["rows"] if r["row_id"] == rid)


def _step_result(rid, label):
    stp = next(s for s in _row(rid)["arithmetic"] if s["label"].startswith(label))
    return Decimal(stp["result"])


# --------------------------------------------------------------------------
# S1 - the six reading files are present unchanged, and a changed one is caught
# --------------------------------------------------------------------------
def test_the_six_step_p11_readings_are_present_unchanged():
    assert check.step_p11 is step_p11  # the checker wires the step-P11 guards
    assert step_p11.reading_digest_errors() == []
    assert len(step_p11.STEP_P11_READINGS) == 6
    for name, spec in step_p11.STEP_P11_READINGS.items():
        raw = (lib.PROVENANCE_DIR / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == spec["digest"], name
        text = raw.decode("utf-8")
        assert "sealed folder" in text, name
        assert spec["marker"] in text, name
        assert "no outside access" not in text, name
        assert text.rstrip().endswith("END-OF-REPORT"), name
    # the method is stated truthfully per file (truthful headers, S1)
    o4b = (lib.PROVENANCE_DIR / "return-independent-hand-calculation-33.md").read_text()
    assert "no ZR website fetch required" in o4b
    o11a = (lib.PROVENANCE_DIR / "return-independent-hand-calculation-35.md").read_text()
    assert "No program run was read" in o11a


def test_a_changed_step_p11_reading_is_caught(monkeypatch):
    bad = dict(step_p11.STEP_P11_READINGS)
    bad["return-independent-hand-calculation-32.md"] = {
        "marker": "M5-T186 PROVENANCE -32 (OPTION 4, READING A)", "digest": "0" * 64}
    monkeypatch.setattr(step_p11, "STEP_P11_READINGS", bad)
    errs = step_p11.reading_digest_errors()
    assert errs and any("digest changed" in m for m in errs), errs


# --------------------------------------------------------------------------
# the whole case validates clean
# --------------------------------------------------------------------------
def test_step_p11_case_validates_clean():
    assert check.validate_case(CID, CASES[CID]) == []


# --------------------------------------------------------------------------
# S2 - every option row names both readings and its comparer; shared rows name both
# --------------------------------------------------------------------------
def test_step_p11_rows_name_their_readings_and_comparer():
    assert step_p11.reading_pair_errors(CID, CASES[CID]) == []
    for row in CASES[CID]["rows"]:
        rid = row["row_id"]
        ref = row["source_reference"]
        if rid.startswith("opt4-"):
            assert "return-independent-hand-calculation-32" in ref, rid
            assert "return-independent-hand-calculation-33" in ref, rid
            assert "return-independent-hand-calculation-34" in ref, rid
        elif rid.startswith("opt11-"):
            assert "return-independent-hand-calculation-35" in ref, rid
            assert "return-independent-hand-calculation-36" in ref, rid
            assert "return-independent-hand-calculation-37" in ref, rid
        else:
            assert "return-independent-hand-calculation-34" in ref, rid
            assert "return-independent-hand-calculation-37" in ref, rid


def test_an_option_row_naming_only_one_reading_is_refused():
    data = copy.deepcopy(CASES[CID])
    target = next(r for r in data["rows"] if r["row_id"] == "opt4-residential-far-standard")
    target["source_reference"] = ("return-independent-hand-calculation-32.md only, confirmed by "
                                  "return-independent-hand-calculation-34.md.")
    errs = step_p11.reading_pair_errors(CID, data)
    assert errs and any(
        "opt4-residential-far-standard" in m and "both" in m.lower() for m in errs), errs


def test_an_option_row_naming_the_wrong_pair_is_refused():
    data = copy.deepcopy(CASES[CID])
    target = next(r for r in data["rows"] if r["row_id"] == "opt4-max-residential-fa")
    # names the option-11 pair and comparer instead of the option-4 ones
    target["source_reference"] = ("return-independent-hand-calculation-35.md and "
                                  "return-independent-hand-calculation-36.md, confirmed by "
                                  "return-independent-hand-calculation-37.md.")
    errs = step_p11.reading_pair_errors(CID, data)
    assert errs and any("opt4-max-residential-fa" in m for m in errs), errs


def test_an_option_row_naming_the_wrong_comparer_is_refused():
    data = copy.deepcopy(CASES[CID])
    target = next(r for r in data["rows"] if r["row_id"] == "opt4-du-factor")
    # correct pair -32/-33 but the wrong comparer (-37 belongs to option 11)
    target["source_reference"] = ("return-independent-hand-calculation-32.md and "
                                  "return-independent-hand-calculation-33.md, confirmed by "
                                  "return-independent-hand-calculation-37.md.")
    errs = step_p11.reading_pair_errors(CID, data)
    assert errs and any("opt4-du-factor" in m and "comparer" in m for m in errs), errs


def test_a_shared_row_without_both_comparers_is_refused():
    data = copy.deepcopy(CASES[CID])
    target = next(r for r in data["rows"] if r["row_id"] == "options-out-of-scope")
    target["source_reference"] = "no reading or comparer named here."
    errs = step_p11.reading_pair_errors(CID, data)
    assert errs and any("options-out-of-scope" in m and "comparer" in m for m in errs), errs


# --------------------------------------------------------------------------
# S3 - every citation is a captured section; uncaptured sections never cited
# --------------------------------------------------------------------------
def test_every_step_p11_citation_matches_the_capture():
    cited = 0
    for row in CASES[CID]["rows"]:
        assert check.citation_errors(CID, row) == [], row["row_id"]
        for cite in row["citations"]:
            cited += 1
            assert cite["kind"] == "captured", (row["row_id"], cite["section"])
            assert (lib.REPO_ROOT / cite["snapshot_file"]).is_file(), cite["snapshot_id"]
    assert cited >= 25, "the value-bearing rows quote captured ZR text"


def test_uncaptured_sections_are_never_a_formal_citation():
    for row in CASES[CID]["rows"]:
        for cite in row["citations"]:
            section = str(cite["section"])
            for bad in UNCAPTURED_SECTIONS:
                assert bad not in section, (row["row_id"], section, bad)


def test_a_changed_law_quote_in_a_step_p11_row_is_caught():
    data = copy.deepcopy(CASES[CID])
    target = next(r for r in data["rows"] if r["row_id"] == "opt11-single-use-far-res")
    target["citations"][0]["quote"] = "this phrase is not in the capture at all"
    errs = check.citation_errors(CID, target)
    assert errs and any("quoted words" in m and "opt11-single-use-far-res" in m for m in errs), errs


# --------------------------------------------------------------------------
# S4 - the rows the two readings do not jointly settle stay not known
# --------------------------------------------------------------------------
def test_step_p11_not_settled_rows_stay_not_known_with_a_kind_of_gap():
    for rid in step_p11.MUST_STAY_NOT_KNOWN[CID]:
        r = lib.load_row(CID, rid)
        assert r["kind"] == "not_known", rid
        assert r["value"] is None, rid
        reason = r["reason"].lower()
        assert "kind of gap" in reason, rid
        assert ("missing fact about the property" in reason
                or "unresolved law" in reason
                or "unresolved reading" in reason
                or "agency determination" in reason
                or "open owner question" in reason
                or "pending legislation" in reason), rid


def test_a_step_p11_value_where_the_readings_differ_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "opt4-nofactor-conversions":
            row["expected"]["kind"] = "value"
            row["expected"]["value"] = "not applicable"
            row["expected"]["reason"] = ""
    errs = step_p11.must_stay_not_known_errors(CID, data)
    assert errs and any("opt4-nofactor-conversions" in m for m in errs), errs


def test_the_street_wall_row_records_no_8_foot_comparer_value():
    # it is not known and carries no measured quantity in the authored case
    assert step_p11.street_wall_not_recorded_errors(CID, CASES[CID]) == []
    r = lib.load_row(CID, "opt11-street-wall-line")
    assert r["kind"] == "not_known"
    # recording the comparer's 8-foot figure as a quantity is refused
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "opt11-street-wall-line":
            row["quantities"] = [{"name": "street-wall placement distance", "value": "8",
                                  "unit": "ft", "basis": "law"}]
    errs = step_p11.street_wall_not_recorded_errors(CID, data)
    assert errs and any("opt11-street-wall-line" in m and "8-foot" in m for m in errs), errs


# --------------------------------------------------------------------------
# S5 - eligibility / owner-question caveats and forbidden present-tense wording
# --------------------------------------------------------------------------
def test_eligibility_and_meaning_rows_carry_their_caveats():
    assert step_p11.eligibility_errors(CID, CASES[CID]) == []
    for row in CASES[CID]["rows"]:
        rid = row["row_id"]
        dne = row["does_not_establish"].lower()
        if rid in step_p11._ELIGIBILITY_ROW_IDS:
            assert "decides no eligibility" in dne, rid
        if rid in step_p11._MEANING_ROW_IDS:
            assert "decides neither owner question" in dne, rid


def test_a_use_permission_row_without_the_eligibility_caveat_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "opt11-combine-shops":
            row["does_not_establish"] = "no caveat here."
    errs = step_p11.eligibility_errors(CID, data)
    assert errs and any("opt11-combine-shops" in m for m in errs), errs


def test_an_owner_question_row_without_its_caveat_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "opt11-split-lot-meaning":
            row["does_not_establish"] = "no caveat here."
    errs = step_p11.eligibility_errors(CID, data)
    assert errs and any("opt11-split-lot-meaning" in m for m in errs), errs


def test_no_forbidden_present_tense_wording_in_the_step_p11_case():
    assert step_p11.forbidden_wording_errors(CID, CASES[CID]) == []


def test_a_forbidden_not_captured_phrase_is_caught():
    data = copy.deepcopy(CASES[CID])
    data["rows"][0]["why_applies"] = "this section is not captured in the snapshot folder"
    errs = step_p11.forbidden_wording_errors(CID, data)
    assert errs and any("not captured" in m for m in errs), errs


# --------------------------------------------------------------------------
# S6 - every quantity carries exactly one of the nine bases
# --------------------------------------------------------------------------
def test_module_nine_bases_equal_the_authoritative_set():
    sys.path.insert(0, str(lib.REPO_ROOT / "tools"))
    import research_record_check as rrc  # noqa: E402
    assert set(step_p11.QUANTITY_BASES) == set(rrc.QUANTITY_BASES)


def test_every_quantity_carries_one_of_the_nine_bases():
    assert step_p11.quantity_basis_errors(CID, CASES[CID]) == []
    seen = 0
    bases = set()
    for row in CASES[CID]["rows"]:
        for q in row.get("quantities", []):
            seen += 1
            bases.add(q["basis"])
            assert q["basis"] in step_p11.QUANTITY_BASES, (row["row_id"], q)
    assert seen >= 15, "the measured rows carry quantities with their basis"
    assert "administrative_record" in bases  # the recorded lot area
    assert "derived" in bases
    assert "law" in bases


def test_a_quantity_without_a_basis_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "opt4-max-residential-fa":
            row["quantities"][0]["basis"] = ""
    errs = step_p11.quantity_basis_errors(CID, data)
    assert errs and any("no measurement basis" in m for m in errs), errs


def test_a_quantity_with_a_basis_outside_the_nine_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "opt4-residential-far-standard":
            row["quantities"][0]["basis"] = "eyeball"
    errs = step_p11.quantity_basis_errors(CID, data)
    assert errs and any("is not one of the nine bases" in m for m in errs), errs


def test_recorded_and_gis_areas_are_never_combined():
    assert step_p11.no_mixed_basis_errors(CID, CASES[CID]) == []
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "opt11-max-total-fa-standard":
            row["arithmetic"][0]["operands"].append(
                {"name": "gis outline area", "value": "10387.99"})
    errs = step_p11.no_mixed_basis_errors(CID, data)
    assert errs and any("mixes the recorded area" in m for m in errs), errs


# --------------------------------------------------------------------------
# S7 - the arithmetic recomputes exactly; plural-tables rows carry null assertions
# --------------------------------------------------------------------------
def test_step_p11_arithmetic_recomputes():
    for rid in ("opt4-max-residential-fa", "opt4-max-dwelling-units",
                "opt11-max-total-fa-standard", "opt11-max-total-fa-qualifying",
                "opt11-du-standard", "opt11-du-qualifying-affordable"):
        assert lib.recompute_row_errors(CID, _row(rid)) == [], rid
    checks = [
        ("opt4-max-residential-fa", "Maximum residential floor area", "20150"),
        ("opt4-max-dwelling-units", "Maximum dwelling units", "29"),
        ("opt11-max-total-fa-standard", "Maximum total floor area", "20150"),
        ("opt11-max-total-fa-qualifying", "Maximum total floor area", "24180"),
        ("opt11-max-total-fa-qualifying", "Qualifying-housing bonus", "4030"),
        ("opt11-du-standard", "Maximum dwelling units", "29"),
        ("opt11-du-qualifying-affordable", "Maximum dwelling units", "35"),
    ]
    for rid, label, want in checks:
        assert _step_result(rid, label) == Decimal(want), (rid, label)


def test_dwelling_unit_rounding_boundaries():
    # the three-quarters rule: 29.63 -> 29, 35.56 -> 35, and the exact boundaries
    assert lib.dwelling_units(Decimal("20150"), Decimal("680")) == 29
    assert lib.dwelling_units(Decimal("24180"), Decimal("680")) == 35
    assert lib.dwelling_units(Decimal("20230"), Decimal("680")) == 30  # 29.75 -> 30
    assert lib.dwelling_units(Decimal("20229"), Decimal("680")) == 29  # 29.7485 -> 29


def test_the_plural_tables_rows_carry_table_assertion_null():
    seen = 0
    for row in CASES[CID]["rows"]:
        for cite in row["citations"]:
            if cite["snapshot_id"] in PLURAL_TABLES_SNAPSHOTS:
                seen += 1
                assert cite["table_assertion"] is None, (row["row_id"], cite["snapshot_id"])
    assert seen >= 2, "the plural-'tables' sections (33-121, 24-11) carry a null table_assertion"


def test_the_23_22_and_23_432_rows_use_the_table_assertion():
    seen = 0
    for row in CASES[CID]["rows"]:
        for cite in row["citations"]:
            if cite["snapshot_id"] in ("zr-23-22", "zr-23-432"):
                seen += 1
                assert cite["table_assertion"] is not None, row["row_id"]
                assert cite["table_assertion"]["district"] == "R6B", row["row_id"]
    assert seen >= 6, "options 4/11 pin the R6B table rows via table_assertion"


def test_a_changed_operand_is_caught_and_names_its_row():
    row = copy.deepcopy(_row("opt11-du-standard"))
    row["arithmetic"][0]["operands"][0]["value"] = "21000"  # was 20150
    errs = lib.recompute_row_errors(CID, row)
    assert errs and any("opt11-du-standard" in m for m in errs), errs


# --------------------------------------------------------------------------
# S8 - NB-06 draft height condition, carve-out row, cross-cite reproduction
# --------------------------------------------------------------------------
def test_height_rows_carry_the_nb06_draft_condition_and_values():
    for rid, mbldg in (("opt11-height-standard", "55"), ("opt11-height-qualifying", "65")):
        row = _row(rid)
        text = (row["why_applies"] + " " + row["expected"]["value"] + " "
                + row["source_reference"]).lower()
        assert "nb-06" in text and "draft" in text, rid
        cite = next(c for c in row["citations"] if c["snapshot_id"] == "zr-23-432")
        assert cite["table_assertion"]["district"] == "R6B", rid
        assert mbldg in str(cite["table_assertion"]["fields"].values()), rid


def test_carveout_row_names_the_checked_sections():
    row = _row("opt11-carveouts-dont-tighten-R6B")
    sections = {c["section"] for c in row["citations"]}
    assert {"35-31", "35-32", "35-33", "24-162"} <= sections


def test_option_11_duplicate_figures_reproduce_the_prior_cases_and_open_no_new_pool():
    # 20,150 / 29 reproduce option 1 (real-lot L1/L6); 24,180 / 35 reproduce option 2
    assert _step_result("opt11-max-total-fa-standard", "Maximum total floor area") == \
        Decimal(lib.load_row("real-lot", "L1")["value"])
    assert _step_result("opt11-du-standard", "Maximum dwelling units") == \
        Decimal(lib.load_row("real-lot", "L6")["value"])
    assert _step_result("opt11-max-total-fa-qualifying", "Maximum total floor area") == \
        Decimal(lib.load_row("benchmark-options-2-3-6-7", "opt2-max-residential-fa")["value"])
    assert _step_result("opt11-du-qualifying-affordable", "Maximum dwelling units") == \
        Decimal(lib.load_row("benchmark-options-2-3-6-7", "opt2-max-dwelling-units")["value"])
    # the cross-citing rows name the prior case+row in prose
    std = _row("opt11-max-total-fa-standard")["source_reference"]
    assert "real-lot.json row L1" in std
    qual = _row("opt11-max-total-fa-qualifying")["source_reference"]
    assert "benchmark-options-2-3-6-7.json#opt2-max-residential-fa" in qual


# --------------------------------------------------------------------------
# S4 - nothing from a program run
# --------------------------------------------------------------------------
def test_step_p11_program_result_errors_is_empty():
    assert check.program_result_errors(CID, CASES[CID]) == []


# --------------------------------------------------------------------------
# S9 - the new case is wired in and the other cases stay byte-stable
# --------------------------------------------------------------------------
def test_step_p11_case_is_wired_in():
    assert CID in lib.CASE_IDS
    assert lib.CASE_IDS[-1] == CID  # appended as the 15th and last case
    assert CID in lib.REQUIRED_BASE_IDS
    assert check.coverage_errors(CID, CASES[CID]) == []
    assert lib.case_path(CID).is_file()
    assert lib.page_path(CID).is_file()
    assert CID in (lib.DOCS_DIR / "README.md").read_text()


def test_step_p11_page_is_byte_identical_to_the_renderer():
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
