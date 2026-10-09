"""Acceptance tests for the CALCULATION entries of the zoning-rule review register (M4-T038, D-090).

Deterministic: they read the committed ``register.json``, the committed scenario-engine modules,
the committed law captures, the committed reference cases and the committed results document, and
they re-derive the program's ACTUAL side through the program's OWN rule engine and the engine's own
building-option function. No network, no AI. The EXPECTED side is always an independent reference
case (``case#row``); it is never taken from a program run. The negative cases mutate an in-memory
copy (or render to a temp folder); they never change a rule, a calculation, a result or a fixture.

Scenario coverage (packet S1-S14): S1 positive validates + renders clean; S2/C2 the actual side is
recomputed through the engine (floor area 20,150; the engine computes 29 while the document
withholds it; the engine's sample stack); S3 a code-module drift is caught; S4 a value where the two
step-P6 readings differ is refused; S5 the built step agrees, a withheld step's side is missing; S6
a cited case row that does not exist or is superseded is refused; S7 the special-density exception;
S8 the effective date; S9 legal-vs-design and the preliminary-assumption wording; S10 the human
verdict rules; S11 the coverage gaps; S13 the six-step page; S14 the method difference names DB-210.
"""
from __future__ import annotations

import copy
import json
import pathlib

from app.rules.registry import RuleRegistry
from app.rules.review_register import check_review_register as checker
from app.rules.review_register import render_review_register as render
from app.rules.review_register import review_register_calculations as calc
from app.scenario.three_answers.building_option import compute_building_option

TEST_FILE = pathlib.Path(__file__).resolve()
REPO_ROOT = TEST_FILE.parents[4]
FIXTURE = (
    REPO_ROOT / "packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json"
)

REGISTER = render.load_register()
CALCS = REGISTER["calculations"]
BY_ID = {c["entry_id"]: c for c in CALCS}

_LANES = {f"LANE_{x}_ENABLED": "true" for x in ("A", "B", "C", "D", "E")}


def _registry() -> RuleRegistry:
    return RuleRegistry(env=_LANES).load()


def _fixture() -> dict:
    return json.loads(FIXTURE.read_text())


# --------------------------------------------------------------------------
# S1 - the committed register (rule entries + the new calculation collection) validates clean
# --------------------------------------------------------------------------
def test_committed_register_validates_clean():
    assert checker.validate(REGISTER) == [], "\n".join(checker.validate(REGISTER))


def test_committed_calculations_validate_clean():
    assert calc.validate_calculations(REGISTER) == []


def test_the_six_calculation_entries_are_present():
    assert [c["entry_id"] for c in CALCS] == [
        "calc-floor-area-allowance",
        "calc-lot-coverage-by-portion",
        "calc-building-option-floor-stack",
        "calc-legal-dwelling-unit-limit",
        "calc-preliminary-apartment-estimate",
        "calc-first-building-option-complete",
    ]
    kinds = {c["entry_id"]: c["entry_kind"] for c in CALCS}
    assert kinds["calc-first-building-option-complete"] == "calculation_comparison"
    assert kinds["calc-floor-area-allowance"] == "calculation"


def test_schema_version_bumped_additively():
    assert REGISTER["schema_version"] == "1.1"
    assert REGISTER["field_guide"]["entry_kind_values"] == ["calculation", "calculation_comparison"]


def test_the_23_rule_entries_are_untouched():
    # The rule collection keeps exactly 23 entries, each with the rule-entry key set (no calc field
    # was back-filled onto a rule entry).
    assert len(REGISTER["entries"]) == 23
    for e in REGISTER["entries"]:
        assert set(e) == checker.ENTRY_KEYS
        assert "entry_kind" not in e
        assert "code_modules" not in e


# --------------------------------------------------------------------------
# S1 - the calculation pages and the regenerated tables are byte-identical to the renderer
# --------------------------------------------------------------------------
def test_each_calculation_page_is_byte_identical():
    calc_dir = render.DOCS_DIR / "calculations"
    for c in CALCS:
        produced = calc.render_calc_detail_md(c, REGISTER)
        on_disk = (calc_dir / f"{c['entry_id']}.md").read_text()
        assert produced == on_disk, f"{c['entry_id']}.md is stale; run --write"


def test_register_md_carries_the_calculations_and_gaps_sections():
    md = (render.DOCS_DIR / "REGISTER.md").read_text()
    assert md == render.render_register_md(REGISTER)
    assert "## Calculations" in md
    assert "## Coverage gaps" in md
    for c in CALCS:
        assert c["entry_id"] in md


def test_history_md_carries_the_calculations_history_section():
    md = (render.DOCS_DIR / "HISTORY.md").read_text()
    assert md == render.render_history_md(REGISTER)
    assert "## Calculations history" in md


def test_no_orphan_calculation_page():
    assert calc.calc_rendered_errors(REGISTER) == []


# --------------------------------------------------------------------------
# S2 / C2 - the ACTUAL side is recomputed through the engine; EXPECTED is independent
# --------------------------------------------------------------------------
def test_calc_floor_area_recomputed_matches_independent():
    # The program's floor area is recomputed through the rule the calculation combines; the
    # independent expected (real-lot#L1) is never taken from that run.
    reg = _registry()
    c = BY_ID["calc-floor-area-allowance"]
    result = reg.evaluate("r6-r12-residential-far", c["example"]["inputs"])
    assert result.outputs["max_residential_floor_area_sq_ft"] == 20150.0
    assert result.outputs == c["example"]["actual"]["values"]
    assert result.coverage_status == "conditional"
    assert c["example"]["expected"]["values"]["max_residential_floor_area_sq_ft"] == 20150
    assert c["example"]["agrees"] is True  # 20,150 (independent) == 20,150 (program)


def test_calc_unit_limit_engine_computes_29_document_withholds():
    # The engine computes 29 internally (the r6b-dwelling-units rule); the document withholds the
    # legal dwelling-unit limit. The page says BOTH.
    reg = _registry()
    c = BY_ID["calc-legal-dwelling-unit-limit"]
    result = reg.evaluate("r6b-dwelling-units", c["example"]["inputs"])
    assert result.outputs["max_dwelling_units"] == 29.0
    assert c["example"]["actual"]["engine_values"]["max_dwelling_units"] == 29
    assert c["example"]["actual"]["state"] == "withheld"
    assert c["example"]["expected"]["values"]["max_dwelling_units"] == 29  # real-lot#L6
    assert c["example"]["agrees"] is None  # the document withholds it; never a forced match
    # the document really withholds the standard legal unit limit
    vs = _fixture()["answers"]["floor_area_allowance"]["value_states"]["legal_unit_limit_standard"]
    assert vs["way"] == "withheld"
    assert "special density area" in vs["reason"]


def test_engine_sample_stack_differs_from_independent_two_buildings():
    # C2/C4/S14: the engine's sample floor stack is recomputed through compute_building_option from
    # the inputs stated in the entry (the made-up interior lot), and it differs from the independent
    # example's two buildings; the benchmark program side is withheld.
    c = BY_ID["calc-building-option-floor-stack"]
    comp = compute_building_option(
        allowance_sf=20000.0, plate_sf=8000.0, max_building_height_ft=55.0, floor_to_floor_ft=10.0
    )
    assert comp.floors_built == 3
    assert comp.achieved_sf == 20000.0
    assert comp.building_height_ft == 30.0
    assert [r.zoning_floor_area_sf for r in comp.floor_rows] == [8000.0, 8000.0, 4000.0]
    ev = c["example"]["actual"]["engine_values"]
    assert ev["engine_floors_built"] == comp.floors_built
    assert ev["engine_achieved_sf"] == comp.achieved_sf
    assert ev["engine_building_height_ft"] == comp.building_height_ft
    assert ev["engine_top_floor_sf"] == comp.floor_rows[-1].zoning_floor_area_sf
    assert c["example"]["actual"]["state"] == "not_available"
    assert "DB-210" in c["example"]["actual"]["engine_note"]
    assert "made-up demonstration" in " ".join(c["inputs"])


def test_document_actuals_match_the_recorded_fixture():
    # C2: the document-level actual answer is read from the committed results document (the journey
    # test proves it byte-equal to the program output).
    doc = _fixture()
    fa = doc["answers"]["floor_area_allowance"]
    vals = {v["key"]: v["value"] for v in fa["values"]}
    assert vals["max_residential_floor_area"] == 20150.0
    assert fa["value_states"]["max_residential_floor_area"]["way"] == "conditional"
    assert doc["answers"]["building_option"]["status"] == "not_available"
    cov = doc["answers"]["permitted_envelope"]["value_states"]["max_lot_coverage"]
    assert cov["way"] == "withheld"
    assert doc["unit_estimate"]["status"] == "not_available"
    # the regenerated 1.4.0 document gives each worked building's estimate in building_alternatives,
    # so the single unit_estimate block now points there (PART E / M5-T146)
    assert "building_alternatives" in doc["unit_estimate"]["reason"]
    est = doc["building_alternatives"][0]["capacity_estimate"]
    assert est["label"] == "Preliminary capacity estimate"
    assert (est["quotient_low"], est["quotient_high"]) == (17.27, 21.59)


# --------------------------------------------------------------------------
# S5 - the built step agrees; a withheld / not-built step records agrees=null
# --------------------------------------------------------------------------
def test_built_step_agrees_withheld_steps_side_missing():
    assert BY_ID["calc-floor-area-allowance"]["example"]["agrees"] is True
    for cid in ("calc-lot-coverage-by-portion", "calc-building-option-floor-stack",
                "calc-legal-dwelling-unit-limit", "calc-preliminary-apartment-estimate"):
        assert BY_ID[cid]["example"]["agrees"] is None, cid


def test_a_withheld_actual_cannot_be_forced_to_agree():
    c = copy.deepcopy(BY_ID["calc-lot-coverage-by-portion"])
    c["example"]["agrees"] = True  # a forced match on a withheld side
    errs = calc.example_errors(c)
    assert any("never a forced match" in m for m in errs)


# --------------------------------------------------------------------------
# S4 - a single figure where the two step-P6 readings differ is refused
# --------------------------------------------------------------------------
def test_a_not_known_reading_cannot_be_a_forced_single_figure():
    c = copy.deepcopy(BY_ID["calc-lot-coverage-by-portion"])
    # claim a single footprint figure and agreement, where the readings differ (real-lot-coverage
    # -by-portion is 'not known'): refused.
    c["example"]["actual"]["state"] = "available"
    c["example"]["agrees"] = True
    errs = calc.example_errors(c)
    assert any("not known" in m and "forced" in m for m in errs)


# --------------------------------------------------------------------------
# S6 / C3 - a cited case row that does not exist, or is superseded, is refused
# --------------------------------------------------------------------------
def test_cited_rows_of_every_entry_exist():
    for c in CALCS:
        if c["entry_kind"] == "calculation":
            exp = c["example"]["expected"]
            assert calc.cited_rows_errors(c["entry_id"], exp["cited_rows"]) == []
        else:
            for s in c["steps"]:
                assert calc.cited_rows_errors(c["entry_id"], s["expected"]["cited_rows"]) == []


def test_a_cited_row_that_does_not_exist_is_refused():
    errs = calc.cited_rows_errors("calc-x", [{
        "case_file": "docs/reference-cases/R6B/cases/real-lot.json", "row_id": "L999-not-real",
    }])
    assert any("does not exist" in m for m in errs)


def test_a_superseded_cited_row_is_refused(tmp_path, monkeypatch):
    # Render the reference-case lookup at a temp copy whose cited row is marked superseded.
    case = json.loads(
        (REPO_ROOT / "docs/reference-cases/R6B/cases/real-lot.json").read_text()
    )
    for row in case["rows"]:
        if row["row_id"] == "L6":
            row["superseded_by"] = "a later reading (sample)"
    temp_case = tmp_path / "real-lot.json"
    temp_case.write_text(json.dumps(case))
    monkeypatch.setattr(render, "REPO_ROOT", tmp_path.parent)
    rel = temp_case.relative_to(tmp_path.parent).as_posix()
    errs = calc.cited_rows_errors("calc-x", [{"case_file": rel, "row_id": "L6"}])
    assert any("superseded" in m for m in errs)


# --------------------------------------------------------------------------
# S3 - a code-module drift is caught (a value for an earlier code version is never shown as current)
# --------------------------------------------------------------------------
def test_code_module_drift_is_caught_and_names_the_module():
    c = copy.deepcopy(BY_ID["calc-floor-area-allowance"])
    c["code_modules"][0]["sha256"] = "0" * 64
    c["code_identity_sha256"] = calc.code_identity(c["code_modules"])
    errs = calc.code_module_errors(c)
    assert any("content changed" in m and "same change" in m for m in errs)


def test_code_identity_mismatch_is_caught():
    c = copy.deepcopy(BY_ID["calc-floor-area-allowance"])
    c["code_identity_sha256"] = "0" * 64
    assert any("code_identity_sha256" in m for m in calc.code_module_errors(c))


def test_changed_code_module_demands_automated_tests_not_run():
    c = copy.deepcopy(BY_ID["calc-floor-area-allowance"])
    c["code_identity_sha256"] = "0" * 64  # a module "changed" since the recorded run
    errs = calc.automated_tests_errors(c)
    assert any("Not run" in m for m in errs)
    c["automated_tests"]["status"] = "Not run"
    assert calc.automated_tests_errors(c) == []


# --------------------------------------------------------------------------
# S9 - legal requirements told apart from design assumptions; preliminary-assumption wording
# --------------------------------------------------------------------------
def test_every_figure_is_marked_legal_or_design():
    for c in CALCS:
        assert calc.legal_vs_design_errors(c) == [], c["entry_id"]


def test_an_unmarked_figure_is_refused():
    c = copy.deepcopy(BY_ID["calc-floor-area-allowance"])
    c["legal_vs_design"][0]["kind"] = "SOMETHING_ELSE"
    assert any("unmarked" in m for m in calc.legal_vs_design_errors(c))


def test_preliminary_assumption_words_are_required_on_size_and_share():
    c = copy.deepcopy(BY_ID["calc-preliminary-apartment-estimate"])
    for row in c["legal_vs_design"]:
        if "700" in row["figure"]:
            row["figure"] = row["figure"].replace("preliminary assumption", "a chosen size")
    assert any("preliminary assumption" in m for m in calc.legal_vs_design_errors(c))


def test_size_or_share_marked_legal_is_refused():
    c = copy.deepcopy(BY_ID["calc-preliminary-apartment-estimate"])
    for row in c["legal_vs_design"]:
        if "0.60" in row["figure"]:
            row["kind"] = "LEGAL_REQUIREMENT"
    assert any("chosen design assumption" in m for m in calc.legal_vs_design_errors(c))


def test_legal_rows_quote_a_verbatim_fragment_of_the_capture():
    c = copy.deepcopy(BY_ID["calc-floor-area-allowance"])
    for row in c["legal_vs_design"]:
        if row["kind"] == "LEGAL_REQUIREMENT":
            row["quoted_text"] = "a sentence that is not in the capture at all"
    assert any("not a verbatim fragment" in m for m in calc.legal_vs_design_errors(c))


# --------------------------------------------------------------------------
# S7 - the special-density exception (legal-unit-limit withheld; engine computes 29)
# --------------------------------------------------------------------------
def test_special_density_applicability_is_a_legal_requirement():
    c = BY_ID["calc-legal-dwelling-unit-limit"]
    legal_special = [
        r for r in c["legal_vs_design"]
        if r["kind"] == "LEGAL_REQUIREMENT" and "special density" in r["figure"].lower()
    ]
    assert legal_special, "the special-density applicability must be marked a LEGAL REQUIREMENT"
    assert any("special density" in x.lower() for x in c["exceptions"])


# --------------------------------------------------------------------------
# S8 - effective date: every entry carries applicable_from / applicable_to
# --------------------------------------------------------------------------
def test_every_calculation_entry_carries_an_effective_date():
    for c in CALCS:
        assert c["applicable_from"] == "2024-12-05"
        assert c["applicable_to"] is None


# --------------------------------------------------------------------------
# S10 - the human verdict rules (no verdict from tests or an agent; decisions survive no change)
# --------------------------------------------------------------------------
def test_every_calculation_reads_not_reviewed():
    for c in CALCS:
        assert c["human_review"]["decision"] is None
        assert c["human_review"]["verdict"] == "Not reviewed"
        assert calc.human_review_errors(c) == []


def test_a_decision_without_a_named_reviewer_is_refused():
    c = copy.deepcopy(BY_ID["calc-floor-area-allowance"])
    c["human_review"]["decision"] = "Correct"
    assert any("refused" in m for m in calc.human_review_errors(c))


def test_a_decision_whose_code_identity_changes_reads_needs_re_review():
    c = copy.deepcopy(BY_ID["calc-floor-area-allowance"])
    c["human_review"].update(
        decision="Correct", reviewer_name="Jane Roe RA",
        reviewer_role="licensed architect (sample, not a real review)", review_date="2026-10-10",
        comments="sample", reviewed_revision=1, reviewed_conditions="R6B benchmark lot",
        reviewed_code_identity_sha256=c["code_identity_sha256"],
        reviewed_law_digests=calc.current_law_digests(c["law"]),
    )
    c["code_identity_sha256"] = "a" * 64  # a module changed; identity updated here
    applies, verdict = calc.derive_human_review(c)
    assert applies is False and verdict == "Needs re-review"
    assert c["human_review"]["decision"] == "Correct"  # original decision kept


def test_a_decision_typed_into_the_block_without_identity_is_refused():
    c = copy.deepcopy(BY_ID["calc-floor-area-allowance"])
    c["human_review"]["decision"] = "Correct"
    c["human_review"]["verdict"] = "Correct"
    c["human_review"]["applies_to_current"] = True
    assert calc.human_review_errors(c) != []


# --------------------------------------------------------------------------
# S11 - the coverage gaps are data and are rendered (at least nine; R703)
# --------------------------------------------------------------------------
def test_coverage_gaps_are_data_and_hold_at_least_nine():
    assert calc.coverage_gaps_errors(REGISTER) == []
    assert len(REGISTER["coverage_gaps"]) >= 9
    assert any("M5-T144" in g for g in REGISTER["coverage_gaps"])
    assert any("three-answers" in g for g in REGISTER["coverage_gaps"])
    md = (render.DOCS_DIR / "REGISTER.md").read_text()
    assert REGISTER["coverage_gaps"][0] in md


def test_too_few_coverage_gaps_is_caught():
    reg = copy.deepcopy(REGISTER)
    reg["coverage_gaps"] = reg["coverage_gaps"][:3]
    assert any("at least nine" in m for m in calc.coverage_gaps_errors(reg))


# --------------------------------------------------------------------------
# S13 / C1 - the six-step page shows six steps in order and ends with the disagreements
# --------------------------------------------------------------------------
def test_six_step_page_has_six_steps_and_closing_names_db210():
    c = BY_ID["calc-first-building-option-complete"]
    assert [s["step"] for s in c["steps"]] == [1, 2, 3, 4, 5, 6]
    names = [s["name"] for s in c["steps"]]
    assert "Applicable legal unit limit" in names
    assert "Separate preliminary apartment estimate" in names  # a separate step (R688)
    assert calc.comparison_errors(c) == []
    closing = json.dumps(c["closing"])
    assert "DB-210" in closing
    kinds = [d["kind"] for d in c["closing"]["disagreements"]]
    assert "a design assumption that differs" in kinds  # S14


def test_s14_method_difference_missing_db210_is_caught():
    c = copy.deepcopy(BY_ID["calc-first-building-option-complete"])
    c["closing"] = json.loads(json.dumps(c["closing"]).replace("DB-210", "a backlog row"))
    assert any("DB-210" in m for m in calc.comparison_errors(c))


def test_a_step_with_an_invalid_verdict_is_caught():
    c = copy.deepcopy(BY_ID["calc-first-building-option-complete"])
    c["steps"][0]["verdict"] = "complies"
    assert any("verdict" in m for m in calc.comparison_errors(c))


# --------------------------------------------------------------------------
# each listed gap that names a withheld program result uses the program's own kind
# (work_owed -> code not built; missing_information -> a missing fact about the property)
# --------------------------------------------------------------------------
_GAP_KIND_TO_PAGE_KIND = {
    "work_owed": "code not built",
    "missing_information": "a missing fact about the property",
}
_REASON_KIND_TO_PAGE_KIND = {
    "rule_not_implemented": "code not built",
    "missing_input": "a missing fact about the property",
}


def _result_blocks(doc: dict) -> dict:
    blocks: dict = {}
    for ans in doc["answers"].values():
        if isinstance(ans, dict):
            for k, v in ans.get("value_states", {}).items():
                blocks[k] = v
    blocks["building_option"] = doc["answers"]["building_option"]
    for k in ("floor_stack", "unit_estimate"):
        blocks[k] = doc[k]
    return blocks


def _expected_page_kind(block: dict):
    gk = block.get("gap_kind")
    if gk:
        return _GAP_KIND_TO_PAGE_KIND.get(gk)
    return _REASON_KIND_TO_PAGE_KIND.get(block.get("reason_kind"))


def _gap_kind_mismatches(closing: dict, blocks: dict) -> list:
    bad = []
    for row in closing["disagreements"] + closing["missing_facts"]:
        for key in row["program_results"]:
            want = _expected_page_kind(blocks[key])
            if want is None or row["kind"] != want:
                bad.append((key, row["kind"], want))
    return bad


def test_every_listed_withheld_gap_kind_agrees_with_the_program():
    # Every closing gap that names a withheld program result uses the kind the program itself
    # records for that result in the committed results document.
    blocks = _result_blocks(_fixture())
    c = BY_ID["calc-first-building-option-complete"]
    assert _gap_kind_mismatches(c["closing"], blocks) == []
    named = {k for row in c["closing"]["disagreements"] + c["closing"]["missing_facts"]
             for k in row["program_results"]}
    want = {"legal_unit_limit_standard", "max_lot_coverage", "building_option", "rear_yard"}
    assert want <= named
    # the corrected row: the legal unit limit is code not built (gap_kind work_owed)
    lul = [r for r in c["closing"]["missing_facts"]
           if "legal_unit_limit_standard" in r["program_results"]]
    assert lul and lul[0]["kind"] == "code not built"


def test_a_mismatched_gap_kind_is_caught():
    # mutation proof (a deep copy, not the committed file): mislabel the withheld legal unit
    # limit as 'unresolved law' and the enforcement catches it against the program's work_owed kind.
    blocks = _result_blocks(_fixture())
    c = copy.deepcopy(BY_ID["calc-first-building-option-complete"])
    for r in c["closing"]["missing_facts"]:
        if "legal_unit_limit_standard" in r["program_results"]:
            r["kind"] = "unresolved law"
    assert _gap_kind_mismatches(c["closing"], blocks) != []


# --------------------------------------------------------------------------
# the calculation history is append-only and a separate list from the rule history
# --------------------------------------------------------------------------
def test_calculations_history_is_append_only_and_separate():
    assert calc.calculations_history_errors(REGISTER) == []
    # the rule-entry history is unchanged (its events never name a calculation id)
    rule_ids = {e["rule_id"] for e in REGISTER["entries"]}
    assert all(ev["entry_id"] in rule_ids for ev in REGISTER["history"])
    calc_ids = {c["entry_id"] for c in CALCS}
    assert all(ev["entry_id"] in calc_ids for ev in REGISTER["calculations_history"])
    # The history is append-only, so it grows past one 'created' event per calculation as entries
    # are revised (M5-T145 appended a revision-2 event for each entry that followed a new module);
    # the invariant the checker holds is that the seq is contiguous from 1, not that it equals the
    # number of calculations.
    hist = REGISTER["calculations_history"]
    assert [ev["seq"] for ev in hist] == list(range(1, len(hist) + 1))


def test_a_calculation_id_colliding_with_a_rule_id_is_refused():
    reg = copy.deepcopy(REGISTER)
    reg["calculations"][0]["entry_id"] = "r6b-height"
    assert any("collide" in m for m in calc.validate_calculations(reg))


COMPARISON_ID = "calc-first-building-option-complete"


# --------------------------------------------------------------------------
# S15 (M5-T146 part D) - the checker module is split behind a compatibility facade (DB-211 c): the
# public names stay importable from the old path and resolve to the focused modules.
# --------------------------------------------------------------------------
def test_calculation_module_is_a_compatibility_facade():
    from app.rules.review_register import calc_checks, calc_render, calc_vocab

    # the three focused modules exist and the facade re-exports their public names (same objects).
    assert calc.validate_calculations is calc_checks.validate_calculations
    assert calc.step_verdict_errors is calc_checks.step_verdict_errors
    assert calc.figure_rows_errors is calc_checks.figure_rows_errors
    assert calc.render_calc_detail_md is calc_render.render_calc_detail_md
    assert calc.ENTRY_KIND_VALUES is calc_vocab.ENTRY_KIND_VALUES
    # the facade exposes the full prior public surface (every re-exported name resolves).
    for name in ("code_identity", "current_law_digests", "comparison_errors",
                 "legal_vs_design_errors", "write_calc_pages", "render_calculations_table_section"):
        assert hasattr(calc, name), name


# --------------------------------------------------------------------------
# S17 (M5-T146 part D) - DB-211 (a) guard 1: a six-step verdict follows its actual side's state.
# The register as committed passes; a verdict that no longer follows its side goes red even after a
# fresh render (the G4 mutation f that the stale-page coupling alone could not catch).
# --------------------------------------------------------------------------
def test_six_step_verdicts_follow_their_actual_side_on_the_committed_register():
    assert calc.step_verdict_errors(BY_ID[COMPARISON_ID]) == []


def _render_again(reg: dict, tmp_path, monkeypatch) -> list[str]:
    """Write the (mutated) calculation pages to a temp docs folder and return the stale-page
    check result, so a test can prove a fresh render would NOT catch the mutation."""
    monkeypatch.setattr(render, "DOCS_DIR", tmp_path)
    calc.write_calc_pages(reg)
    return calc.calc_rendered_errors(reg)


def test_a_six_step_verdict_without_a_present_side_is_caught_after_render(tmp_path, monkeypatch):
    # Force the withheld footprint step (its program side is withheld) to read 'agree'. After
    # re-rendering, the pages match the mutated data so the stale-page check is clean - but the
    # verdict guard still goes red (the G4 mutation f that a fresh render alone hid).
    reg = copy.deepcopy(REGISTER)
    comp = next(c for c in reg["calculations"] if c["entry_id"] == COMPARISON_ID)
    step = next(s for s in comp["steps"] if s["actual"]["state"] == "withheld")
    assert step["verdict"] == "side_missing"
    step["verdict"] = "agree"
    assert _render_again(reg, tmp_path, monkeypatch) == []  # a fresh render hides it
    errs = calc.step_verdict_errors(comp)
    assert any("side_missing" in m or "present" in m for m in errs)  # the guard still catches it


def test_a_step_whose_side_changes_without_its_verdict_is_caught():
    # DB-211 (a): change a step's actual side to an absent state while the verdict stays 'agree'.
    comp = copy.deepcopy(BY_ID[COMPARISON_ID])
    assert comp["steps"][0]["verdict"] == "agree" and comp["steps"][0]["actual"]["state"] == \
        "settled"
    comp["steps"][0]["actual"]["state"] = "withheld"  # side now absent; verdict unchanged
    errs = calc.step_verdict_errors(comp)
    assert any("side_missing" in m for m in errs)  # withheld cannot keep 'agree'
    assert any("'agree' needs both sides present" in m for m in errs)


def test_a_withheld_step_cannot_read_differ():
    comp = copy.deepcopy(BY_ID[COMPARISON_ID])
    # step 5 is withheld/side_missing; forcing it to 'differ' is refused (nothing to compare).
    assert comp["steps"][4]["actual"]["state"] == "withheld"
    comp["steps"][4]["verdict"] = "differ"
    assert any("side_missing" in m for m in calc.step_verdict_errors(comp))


# --------------------------------------------------------------------------
# S18 (M5-T146 part D) - DB-211 (a) guard 2: every figure the six steps rest on has its
# legal-or-design row. A dropped row goes red even after a fresh render (the G4 mutation h2).
# --------------------------------------------------------------------------
def test_every_six_step_figure_has_its_legal_or_design_row_on_the_committed_register():
    assert calc.figure_rows_errors(BY_ID[COMPARISON_ID]) == []


def test_a_dropped_legal_row_is_caught_after_render(tmp_path, monkeypatch):
    # Remove the heights (ZR 23-432) legal row the six steps rest on. After re-rendering the pages
    # match the mutated data (stale-page check clean), but the figure-row guard still goes red.
    reg = copy.deepcopy(REGISTER)
    comp = next(c for c in reg["calculations"] if c["entry_id"] == COMPARISON_ID)
    comp["legal_vs_design"] = [
        r for r in comp["legal_vs_design"] if "23-432" not in r["figure"]
    ]
    assert _render_again(reg, tmp_path, monkeypatch) == []  # a fresh render hides it
    assert any("23-432" in m for m in calc.figure_rows_errors(comp))  # the guard still catches it


def test_a_dropped_design_assumption_row_is_caught():
    # Remove the apartment-size (700) design row that a six step uses; the guard catches it.
    comp = copy.deepcopy(BY_ID[COMPARISON_ID])
    comp["legal_vs_design"] = [r for r in comp["legal_vs_design"] if "700" not in r["figure"]]
    assert any("'700'" in m for m in calc.figure_rows_errors(comp))


# --------------------------------------------------------------------------
# S19 (M5-T146 part D) - DB-211 (b) scenario fixes.
# S7: feed a lot with a special density area PRESENT to the engine - the dwelling-unit formula does
# not apply there (ZR 23-52(a)(1)); the earlier test only checked the legal-requirement marking.
# --------------------------------------------------------------------------
def test_special_density_present_makes_the_unit_limit_not_applicable():
    reg = _registry()
    c = BY_ID["calc-legal-dwelling-unit-limit"]
    base = dict(c["example"]["inputs"])
    # the committed example feeds special_density_area=False; the engine then computes 29
    assert base["special_density_area"] is False
    present = reg.evaluate("r6b-dwelling-units", {**base, "special_density_area": True})
    assert present.coverage_status == "not_applicable"
    assert "max_dwelling_units" not in present.outputs  # no number; the formula does not apply
    # and the marking the earlier scenario checked still holds (the applicability is a legal rule)
    legal_special = [
        r for r in c["legal_vs_design"]
        if r["kind"] == "LEGAL_REQUIREMENT" and "special density" in r["figure"].lower()
    ]
    assert legal_special


# S8: derive each calculation's effective date from the LAST-AMENDED dates of the rules it combines,
# not from a hard-coded literal (the earlier test asserted a fixed 2024-12-05).
def test_effective_date_is_derived_from_the_combined_rules():
    rule_by_id = {e["rule_id"]: e for e in REGISTER["entries"]}
    for c in CALCS:
        combined_amended = [
            law["last_amended"]
            for rid in c["combines_rule_ids"]
            for law in rule_by_id[rid]["law"]
        ]
        assert combined_amended, c["entry_id"]
        # applies-from is the latest amendment among the combined rules' captured law
        assert c["applicable_from"] == max(combined_amended), c["entry_id"]
        # applies-to is open while every combined rule is still in force
        combined_ends = [rule_by_id[rid]["applicable_to"] for rid in c["combines_rule_ids"]]
        assert c["applicable_to"] is None and all(e is None for e in combined_ends), c["entry_id"]


# --------------------------------------------------------------------------
# S20 (M5-T146 part D) - the guards check code identity, captures and figures, never a human verdict
# (R374): their output is independent of the human-review block.
# --------------------------------------------------------------------------
def test_the_guards_never_read_a_human_verdict():
    comp = copy.deepcopy(BY_ID[COMPARISON_ID])
    before = (calc.step_verdict_errors(comp), calc.figure_rows_errors(comp))
    comp["human_review"].update(
        decision="Correct", reviewer_name="Jane Roe RA", review_date="2026-10-10",
        verdict="Correct", applies_to_current=True,
    )
    after = (calc.step_verdict_errors(comp), calc.figure_rows_errors(comp))
    assert before == after == ([], [])  # the guards ignore the human verdict entirely
