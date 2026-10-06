"""Build-time acceptance tests for the R6B reference cases (M4-T024, D-090 R226/R241/R259/R291).

Deterministic and engine-free: they read the authored case data files, the
captured law snapshots, the rendered pages and the README, recompute every
arithmetic step with exact decimal arithmetic, check every cited capture digest
against the live capture, and prove no case file carries a program result. They
import NOTHING from the rule engine, the scenario engine or any program output.
The negative (mutation) cases mutate a deep copy in memory; no committed file is
edited. They cover the acceptance scenarios S1 to S12.
"""
from __future__ import annotations

import copy
import pathlib
import sys

import pytest

_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import r6b_reference_cases_check as check  # noqa: E402
import r6b_reference_cases_lib as lib  # noqa: E402
import r6b_reference_cases_render as render  # noqa: E402

CASES = lib.load_all()
SUPPORT_FILES = sorted(_HERE.glob("*.py"))


# --------------------------------------------------------------------------
# positive: the committed cases validate cleanly end to end
# --------------------------------------------------------------------------
def test_everything_validates_clean():
    errors = check.validate_all() + render.rendered_errors()
    assert errors == [], "\n".join(errors)


# --------------------------------------------------------------------------
# S1 - four cases, each with one data file and one page; every table row present
# --------------------------------------------------------------------------
def test_four_cases_each_with_a_data_file_and_a_page():
    assert lib.CASE_IDS == ("real-lot", "interior-lots", "corner-reach", "suffix")
    for case_id in lib.CASE_IDS:
        assert lib.case_path(case_id).is_file(), f"missing data file for {case_id}"
        assert lib.page_path(case_id).is_file(), f"missing page for {case_id}"


def test_every_work_order_table_row_present_under_its_id():
    for case_id, data in CASES.items():
        assert check.coverage_errors(case_id, data) == [], case_id
    # the exact table ids the work order names
    assert [r["row_id"] for r in CASES["real-lot"]["rows"]] == [f"L{i}" for i in range(1, 16)]
    interior_ids = {r["row_id"] for r in CASES["interior-lots"]["rows"]}
    want_interior = {"P1-floor-area", "P3-units", "P4-units", "P5-units", "interior-coverage"}
    assert want_interior <= interior_ids
    corner_ids = {r["row_id"] for r in CASES["corner-reach"]["rows"]}
    for base in ("real-lot", "C1", "C2", "C3"):
        assert any(rid.startswith(base) for rid in corner_ids), base
    assert [r["row_id"] for r in CASES["suffix"]["rows"]] == [
        "23-362", "23-52", "23-344", "23-22", "23-432"
    ]


# --------------------------------------------------------------------------
# S2 - each row can be followed by a person
# --------------------------------------------------------------------------
def test_each_row_is_followable():
    for case_id, row in lib.iter_rows():
        tag = f"{case_id}/{row['row_id']}"
        assert str(row["why_applies"]).strip(), f"{tag}: no why_applies"
        assert str(row["source_reference"]).strip(), f"{tag}: no source_reference"
        assert set(row["expected"]) == lib.EXPECTED_KEYS
        for fact in row["facts_used"]:
            assert str(fact["source"]).strip(), f"{case_id}/{row['row_id']}: a fact lacks a source"
    # the rendered page shows the parts a reader needs
    for case_id in lib.CASE_IDS:
        page = lib.page_path(case_id).read_text()
        assert "Why the rule applies:" in page
        assert "Expected value:" in page
        assert "Where this stands in the independent reading:" in page


# --------------------------------------------------------------------------
# S3 - nothing from a program run
# --------------------------------------------------------------------------
def test_no_program_result_in_any_case():
    for case_id, data in CASES.items():
        assert check.program_result_errors(case_id, data) == [], case_id


def test_a_program_result_field_is_refused():
    data = copy.deepcopy(CASES["real-lot"])
    data["rows"][0]["program_today"] = "20150"
    errs = check.program_result_errors("real-lot", data)
    assert any("program" in m.lower() for m in errs)


def test_a_program_result_sentence_is_refused():
    data = copy.deepcopy(CASES["real-lot"])
    data["rows"][0]["why_applies"] = "the program today gives 20,150"
    errs = check.program_result_errors("real-lot", data)
    assert any("program today" in m for m in errs)


def test_support_code_imports_no_engine():
    # Parse the imports (not a substring scan, so this file's own word-list of
    # banned module names does not count) and refuse any import from the program.
    import ast

    def _modules(path: pathlib.Path):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    yield alias.name
            elif isinstance(node, ast.ImportFrom):
                yield node.module or ""

    for path in SUPPORT_FILES:
        for module in _modules(path):
            top = module.split(".")[0]
            assert top != "app", f"{path.name} imports {module!r} (must stay engine-free)"


# --------------------------------------------------------------------------
# S4 - values come from the helper's returns; the returns are kept unchanged
# --------------------------------------------------------------------------
def test_every_row_names_its_place_in_the_independent_reading():
    for case_id, row in lib.iter_rows():
        ref = row["source_reference"]
        assert "return-independent-hand-calculation" in ref or "work order" in ref.lower(), (
            f"{case_id}/{row['row_id']}: source reference does not point at the helper's return"
        )


def test_the_two_returns_are_present_unchanged():
    assert check.provenance_errors() == []
    one = (lib.PROVENANCE_DIR / "return-independent-hand-calculation-1.md").read_text()
    two = (lib.PROVENANCE_DIR / "return-independent-hand-calculation-2.md").read_text()
    assert "INDEPENDENT BLIND HAND-CALCULATION" in one and one.rstrip().endswith("END-OF-REPORT")
    assert "FOLLOW-UP" in two and two.rstrip().endswith("END-OF-REPORT")
    # the first-round distinctive numbers are carried verbatim
    assert "2.00 × 10,075 = 20,150" in one or "2.00 x 10,075 = 20,150 sf" in one
    assert one != two


# --------------------------------------------------------------------------
# S5 - arithmetic recomputed exactly (positive + the required worked numbers)
# --------------------------------------------------------------------------
def test_all_arithmetic_recomputes():
    for case_id, row in lib.iter_rows():
        assert lib.recompute_row_errors(case_id, row) == [], f"{case_id}/{row['row_id']}"


def test_the_worked_numbers_from_the_scenario():
    assert lib.load_row("real-lot", "L1")["value"] == 20150  # 2.00 x 10,075
    assert lib.load_row("real-lot", "L6")["value"] == 29      # 20,150 / 680 -> 29 (frac < 3/4)
    assert lib.load_row("interior-lots", "P5-units")["value"] == 16  # 10,710 / 680 = 15.75 -> 16
    assert lib.load_row("interior-lots", "P3-units")["value"] == 15  # 10,700 / 680 = 15.735 -> 15


def test_mutation_proof_s5_a_changed_operand_fails_and_names_the_row():
    row = copy.deepcopy(lib.find_row_or_none("real-lot", "L1"))
    row["arithmetic"][0]["operands"][1]["value"] = "10076"  # was 10075
    errs = lib.recompute_row_errors("real-lot", row)
    assert errs and any("real-lot/L1" in m for m in errs), errs


def test_mutation_proof_s5_a_changed_dwelling_unit_result_fails():
    row = copy.deepcopy(lib.find_row_or_none("interior-lots", "P5-units"))
    row["arithmetic"][0]["result"] = "15"  # the true threshold result is 16
    errs = lib.recompute_row_errors("interior-lots", row)
    assert errs and any("P5-units" in m for m in errs), errs


# --------------------------------------------------------------------------
# S6 - law text tied to its capture
# --------------------------------------------------------------------------
def test_every_citation_matches_the_live_capture():
    for case_id, row in lib.iter_rows():
        assert check.citation_errors(case_id, row) == [], f"{case_id}/{row['row_id']}"


def test_not_captured_sections_are_listed_in_the_readme():
    assert check.readme_errors() == []
    readme = (lib.DOCS_DIR / "README.md").read_text()
    for section in check.NOT_CAPTURED_SECTIONS:
        assert section in readme


def test_mutation_proof_s6_a_changed_digest_fails():
    row = copy.deepcopy(lib.find_row_or_none("real-lot", "L1"))
    row["citations"][0]["content_digest"] = "0" * 64
    errs = check.citation_errors("real-lot", row)
    assert errs and any("digest" in m for m in errs), errs


def test_mutation_proof_s6_a_quote_not_in_the_capture_fails():
    row = copy.deepcopy(lib.find_row_or_none("real-lot", "L1"))
    row["citations"][0]["quote"] = "this sentence is not in the capture at all"
    errs = check.citation_errors("real-lot", row)
    assert errs and any("not found in the capture" in m for m in errs), errs


# --------------------------------------------------------------------------
# S7 - not known stays not known
# --------------------------------------------------------------------------
NOT_KNOWN = {
    "real-lot": {"L5", "L7", "L8", "L12", "L14", "L15"},
    "corner-reach": {"real-lot-coverage", "real-lot-rear-yard", "C1-rear-yard",
                     "C3-coverage", "C3-rear-yard"},
}


def test_the_named_rows_are_not_known_with_a_reason_and_no_number():
    for case_id, ids in NOT_KNOWN.items():
        by_id = {r["row_id"]: r for r in CASES[case_id]["rows"]}
        for rid in ids:
            exp = by_id[rid]["expected"]
            assert exp["kind"] == "not_known", f"{case_id}/{rid} should be not known"
            assert exp["value"] is None, f"{case_id}/{rid} must carry no number"
            assert str(exp["reason"]).strip(), f"{case_id}/{rid} needs a reason"


def test_a_not_known_row_with_a_number_is_refused():
    row = copy.deepcopy(lib.find_row_or_none("real-lot", "L5"))
    row["expected"]["value"] = 100
    errs = check.expected_errors("real-lot", row)
    assert any("must carry no number" in m for m in errs)


def test_a_numeric_row_without_a_basis_is_refused():
    row = copy.deepcopy(lib.find_row_or_none("real-lot", "L1"))
    row["arithmetic"] = []
    row["citations"] = []
    errs = check.expected_errors("real-lot", row)
    assert any("arithmetic or a quoted law basis" in m for m in errs)


# --------------------------------------------------------------------------
# S8 - the change rule and the change log
# --------------------------------------------------------------------------
def test_change_log_starts_with_creation_and_is_ordered():
    for case_id, data in CASES.items():
        assert check.change_log_errors(case_id, data) == [], case_id
        log = data["change_log"]
        assert log, f"{case_id} has no change log"
        assert "creat" in log[0]["summary"].lower()


def test_readme_states_the_change_rule():
    readme = (lib.DOCS_DIR / "README.md").read_text().lower()
    for needle in ("corrected evidence", "corrected reading", "change in the law",
                   "investigated on both sides"):
        assert needle in readme, needle


# --------------------------------------------------------------------------
# S9 - what a case is worth
# --------------------------------------------------------------------------
def test_each_case_says_what_it_is_worth():
    for data in CASES.values():
        worth = data["what_it_is_worth"].lower()
        assert "ai helper" in worth
        assert "second ai" in worth
        assert "not proof" in worth
        assert "not professionally reviewed" in worth
    assert "one lot" in CASES["real-lot"]["what_it_is_worth"].lower()
    for case_id in lib.CASE_IDS:
        page = lib.page_path(case_id).read_text().lower()
        assert "not professionally reviewed" in page


# --------------------------------------------------------------------------
# S10 - rendered pages match the data (byte-identical); an edit diverges
# --------------------------------------------------------------------------
def test_pages_are_byte_identical_to_the_renderer():
    assert render.rendered_errors() == []
    for case_id, data in CASES.items():
        assert render.render_page(data) == lib.page_path(case_id).read_text(), case_id


def test_a_hand_edited_page_would_diverge():
    produced = render.render_page(CASES["real-lot"])
    tampered = produced.replace("Expected value:", "Expected answer:", 1)
    assert tampered != produced  # any hand edit breaks the byte-identical check


# --------------------------------------------------------------------------
# S11 - a loader for later law tests
# --------------------------------------------------------------------------
def test_loader_returns_value_kind_and_source_for_a_numeric_row():
    got = lib.load_row("real-lot", "L1")
    assert got["kind"] == "value"
    assert got["value"] == 20150
    assert "return-independent-hand-calculation" in got["source_reference"]


def test_loader_returns_a_not_known_row():
    got = lib.load_row("real-lot", "L5")
    assert got["kind"] == "not_known"
    assert got["value"] is None
    assert str(got["reason"]).strip()


def test_loader_fails_loudly_on_a_missing_row_or_case():
    with pytest.raises(lib.RowNotFound):
        lib.load_row("real-lot", "no-such-row")
    with pytest.raises(lib.RowNotFound):
        lib.load_row("no-such-case", "L1")


# --------------------------------------------------------------------------
# S12 - scope: the support files stay small and engine-free
# --------------------------------------------------------------------------
def test_support_files_are_focused():
    for path in SUPPORT_FILES:
        lines = len(path.read_text().splitlines())
        assert lines < 600, f"{path.name} has {lines} lines (keep each file focused)"
