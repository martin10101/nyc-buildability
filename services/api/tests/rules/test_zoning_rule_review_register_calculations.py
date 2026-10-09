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
    assert "not built yet" in doc["unit_estimate"]["reason"]


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
# the calculation history is append-only and a separate list from the rule history
# --------------------------------------------------------------------------
def test_calculations_history_is_append_only_and_separate():
    assert calc.calculations_history_errors(REGISTER) == []
    # the rule-entry history is unchanged (its events never name a calculation id)
    rule_ids = {e["rule_id"] for e in REGISTER["entries"]}
    assert all(ev["entry_id"] in rule_ids for ev in REGISTER["history"])
    calc_ids = {c["entry_id"] for c in CALCS}
    assert all(ev["entry_id"] in calc_ids for ev in REGISTER["calculations_history"])
    assert [ev["seq"] for ev in REGISTER["calculations_history"]] == list(range(1, len(CALCS) + 1))


def test_a_calculation_id_colliding_with_a_rule_id_is_refused():
    reg = copy.deepcopy(REGISTER)
    reg["calculations"][0]["entry_id"] = "r6b-height"
    assert any("collide" in m for m in calc.validate_calculations(reg))
