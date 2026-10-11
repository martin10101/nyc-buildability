"""Step-P7 acceptance tests for the R6B reference cases (M5-T176).

The step-P7 case (``short-block-rear-yard``) is the two independent readings of
ZR 23-344(b) (the short dimension of a block) and 23-344(c)(3), written into the R6B
reference cases as one case: the reading of what 23-344(b) measures and whether its
thresholds are strict; of 23-344(c)/(c)(3); of how 23-342/23-343/23-344 fit together;
the ten made-up boundary cases M1 to M10; and the real lot (215-16 Northern Boulevard,
lot 70 of block 7334) under Z1 and Z2 on each measurement basis. These tests prove,
one per input state:

* S1 - the two readings are present unchanged (digest pinned), and a changed one is caught.
* S2 - every row names both readings and quotes captured words found in the capture.
* S3 - M5-T167's scenarios S1 to S12 are each mapped, and the 'within 100 feet' and
  'less than 230 feet' readings are rows of their own.
* S4 - program_result_errors is empty (no value comes from a program run).
* S6 - the rows the two readings do not jointly settle stay not known with a kind of
  gap, and a value where they differ is refused.
* S7 - every quantity carries exactly one of the nine bases (and the module's set
  equals tools/research_record_check.py QUANTITY_BASES); a quantity with no basis, or
  with two, is refused.
* S8 - no real-lot row records an unconditional 'no rear yard'; every real-lot row
  quotes ZR 23-344; an unconditional 'no rear yard' is refused.
* the existing cases' rows are byte-identical to the claim head.

Kept in its own file; engine-free (imports nothing from app).
"""
from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import r6b_reference_cases_check as check  # noqa: E402
import r6b_reference_cases_lib as lib  # noqa: E402
import r6b_reference_cases_step_p7 as step_p7  # noqa: E402

CASES = lib.load_all()
CID = "short-block-rear-yard"

# The prior cases' rows, pinned at the claim head: this task adds a case and must not
# touch any existing one. The digest proves byte-stability without git.
PRIOR_ROWS_DIGEST = "4285ac72268598eb054fa0485b23a7bafa2b455c336a973ca75ecbf264b77583"


def _row(rid):
    return next(r for r in CASES[CID]["rows"] if r["row_id"] == rid)


# --------------------------------------------------------------------------
# S1 - the two readings are present unchanged, and a changed one is caught
# --------------------------------------------------------------------------
def test_the_two_step_p7_readings_are_present_unchanged():
    assert check.step_p7_reading_errors() == []
    for name, spec in step_p7.STEP_P7_READINGS.items():
        raw = (lib.PROVENANCE_DIR / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == spec["digest"], name
        text = raw.decode("utf-8")
        assert "sealed folder" in text, name
        assert spec["marker"] in text, name
        assert text.rstrip().endswith("END-OF-REPORT"), name
    fifteen = (lib.PROVENANCE_DIR / "return-independent-hand-calculation-15.md").read_text()
    sixteen = (lib.PROVENANCE_DIR / "return-independent-hand-calculation-16.md").read_text()
    assert fifteen != sixteen
    # each header says the readers were given four earlier answers as settled
    for text in (fifteen, sixteen):
        assert "FOUR answers settled by earlier readings" in text


def test_a_changed_step_p7_reading_is_caught(monkeypatch):
    bad = {
        "return-independent-hand-calculation-15.md":
            {"marker": "ONE HARD RULE", "digest": "0" * 64},
        "return-independent-hand-calculation-16.md":
            step_p7.STEP_P7_READINGS["return-independent-hand-calculation-16.md"],
    }
    monkeypatch.setattr(step_p7, "STEP_P7_READINGS", bad)
    errs = check.step_p7_reading_errors()
    assert errs and any("digest changed" in m for m in errs), errs


# --------------------------------------------------------------------------
# the whole case validates clean
# --------------------------------------------------------------------------
def test_step_p7_case_validates_clean():
    assert check.validate_case(CID, CASES[CID]) == []


# --------------------------------------------------------------------------
# S2 - every row names both readings and quotes captured words
# --------------------------------------------------------------------------
def test_step_p7_rows_name_both_readings():
    for row in CASES[CID]["rows"]:
        assert check.both_readings_errors(CID, row) == [], row["row_id"]
        ref = row["source_reference"]
        assert "return-independent-hand-calculation-15" in ref, row["row_id"]
        assert "return-independent-hand-calculation-16" in ref, row["row_id"]


def test_every_step_p7_row_quotes_captured_words():
    for row in CASES[CID]["rows"]:
        assert check.citation_errors(CID, row) == [], row["row_id"]
        assert row["citations"], f"{row['row_id']}: a row must cite at least one capture"


def test_a_changed_law_quote_in_a_step_p7_row_is_caught():
    data = copy.deepcopy(CASES[CID])
    target = next(r for r in data["rows"] if r["row_id"] == "b-less-than-230")
    target["citations"][0]["quote"] = "this phrase is not in the capture at all"
    errs = check.citation_errors(CID, target)
    assert errs and any("quoted words" in m and "b-less-than-230" in m for m in errs), errs


# --------------------------------------------------------------------------
# S3 - M5-T167's scenarios S1 to S12 are each mapped
# --------------------------------------------------------------------------
def test_m5_t167_scenarios_s1_to_s12_are_each_mapped():
    row = _row("m5-t167-scenario-map")
    value = row["expected"]["value"]
    for n in range(1, 13):
        assert f"S{n} (" in value, f"S{n} not mapped in the scenario map"
    # the readings of 'within 100 feet' and 'less than 230 feet' are rows of their own
    assert lib.load_row(CID, "b-within-100-feet")["kind"] == "not_known"
    assert lib.load_row(CID, "b-less-than-230")["kind"] == "value"


# --------------------------------------------------------------------------
# S4 - nothing in the case comes from a program run
# --------------------------------------------------------------------------
def test_program_result_errors_is_empty():
    assert check.program_result_errors(CID, CASES[CID]) == []


# --------------------------------------------------------------------------
# S6 - the rows the two readings do not jointly settle stay not known
# --------------------------------------------------------------------------
def test_step_p7_not_settled_rows_stay_not_known_with_a_kind_of_gap():
    for rid in step_p7.MUST_STAY_NOT_KNOWN[CID]:
        r = lib.load_row(CID, rid)
        assert r["kind"] == "not_known", rid
        assert r["value"] is None, rid
        reason = r["reason"].lower()
        assert "kind of gap" in reason, rid
        assert ("missing fact about the property" in reason
                or "unresolved law" in reason), rid


def test_a_step_p7_value_where_the_readings_differ_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "real-lot-short-dimension":
            row["expected"]["kind"] = "value"
            row["expected"]["value"] = "the Northern Boulevard frontage is a short dimension"
            row["expected"]["reason"] = ""
    errs = step_p7.must_stay_not_known_errors(CID, data)
    assert errs and any("real-lot-short-dimension" in m for m in errs), errs


# --------------------------------------------------------------------------
# S7 - every quantity carries exactly one of the nine bases
# --------------------------------------------------------------------------
def test_module_nine_bases_equal_the_authoritative_set():
    sys.path.insert(0, str(lib.REPO_ROOT / "tools"))
    import research_record_check as rrc  # noqa: E402
    assert set(step_p7.QUANTITY_BASES) == set(rrc.QUANTITY_BASES)


def test_every_quantity_carries_one_of_the_nine_bases():
    seen = 0
    for row in CASES[CID]["rows"]:
        assert step_p7.quantity_basis_errors(CID, row) == [], row["row_id"]
        for q in row.get("quantities", []):
            seen += 1
            assert q["basis"] in step_p7.QUANTITY_BASES, (row["row_id"], q)
    assert seen >= 8, "the real-lot rows carry measured quantities with their basis"


def test_a_quantity_without_a_basis_is_refused():
    data = copy.deepcopy(CASES[CID])
    row = next(r for r in data["rows"] if r["row_id"] == "real-lot-reach")
    row["quantities"][0]["basis"] = ""
    errs = step_p7.quantity_basis_errors(CID, row)
    assert errs and any("no measurement basis" in m for m in errs), errs


def test_a_quantity_with_a_basis_outside_the_nine_is_refused():
    data = copy.deepcopy(CASES[CID])
    row = next(r for r in data["rows"] if r["row_id"] == "real-lot-short-dimension")
    row["quantities"][0]["basis"] = "eyeball"
    errs = step_p7.quantity_basis_errors(CID, row)
    assert errs and any("is not one of the nine bases" in m for m in errs), errs


# --------------------------------------------------------------------------
# S8 - no unconditional 'no rear yard' on the real lot; every real-lot row quotes 23-344
# --------------------------------------------------------------------------
def test_every_real_lot_row_quotes_23_344_and_has_no_unconditional_no_rear_yard():
    assert step_p7.real_lot_rear_yard_errors(CID, CASES[CID]) == []


def test_an_unconditional_no_rear_yard_in_a_real_lot_row_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "real-lot-z1-rear-yard":
            row["expected"]["kind"] = "value"
            row["expected"]["value"] = "no rear yard is required on the lot"
            row["expected"]["reason"] = ""
    errs = step_p7.real_lot_rear_yard_errors(CID, data)
    assert errs and any("real-lot-z1-rear-yard" in m and "no rear yard" in m for m in errs), errs


def test_a_real_lot_row_that_drops_its_23_344_citation_is_refused():
    data = copy.deepcopy(CASES[CID])
    for row in data["rows"]:
        if row["row_id"] == "real-lot-front-lot-line":
            row["citations"] = [c for c in row["citations"] if "23-344" not in c["section"]]
    errs = step_p7.real_lot_rear_yard_errors(CID, data)
    assert errs and any("must quote ZR 23-344" in m for m in errs), errs


# --------------------------------------------------------------------------
# the existing cases' rows are byte-identical to the claim head
# --------------------------------------------------------------------------
def test_prior_cases_rows_are_byte_stable():
    prior = [c for c in lib.CASE_IDS if c != CID]
    blob = json.dumps({cid: lib.load_case(cid)["rows"] for cid in prior},
                      sort_keys=True, ensure_ascii=False)
    assert hashlib.sha256(blob.encode()).hexdigest() == PRIOR_ROWS_DIGEST


# --------------------------------------------------------------------------
# wording: no forbidden present-tense "not captured" phrasing in the new case
# --------------------------------------------------------------------------
def test_no_forbidden_present_tense_wording_in_the_step_p7_case():
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
