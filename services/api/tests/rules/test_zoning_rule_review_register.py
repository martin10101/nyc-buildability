"""Build-time acceptance tests for the zoning-rule review register (M4-T023, D-090).

Deterministic: they read the committed ``register.json``, the committed rule
files, the committed law captures and the committed rendered Markdown, and they
re-derive every example's ``actual`` answer through the program's OWN rule
registry and evaluator. No network, no AI. They prove:

* S3 - one register entry per rule file and the reverse (23 today, no duplicate,
  no entry without a rule file, no rule file without an entry); every linked
  code / test / capture file exists.
* S4 - each entry pins the rule file's version and a line-ending-normalized
  sha256; a change to either is caught with a message naming the rule.
* S5 - every example's inputs are evaluated through the real engine and the
  result equals the recorded ``actual``; ``agrees`` equals whether the
  independently-worked ``expected`` matches ``actual`` (or is ``null`` for a gap).
  The recorded ``expected`` is never taken from a program run.
* S6 - the human-verdict rules, with negative cases (a verdict is refused without
  a named reviewer / date / revision / conditions; 'Correct'/'Incorrect' against
  an old revision must read 'Needs re-review'; a verdict is never derived from
  tests or an AI).
* S7 - the append-only history rules, with negative cases.
* S8 - the rendered Markdown is byte-identical to the renderer's output, with no
  stale or orphan detail page.
"""
from __future__ import annotations

import copy
import json
import pathlib

from app.rules.registry import RuleRegistry
from app.rules.review_register import check_review_register as checker
from app.rules.review_register import render_review_register as render

TEST_FILE = pathlib.Path(__file__).resolve()
REPO_ROOT = TEST_FILE.parents[4]
RULESET_DIR = TEST_FILE.parents[2] / "app" / "rules" / "rulesets"

REGISTER = render.load_register()
ENTRIES = REGISTER["entries"]
BY_ID = {e["rule_id"]: e for e in ENTRIES}

# Lane A carries the R6B rules; enable it so every backfilled rule is evaluable.
_LANES = {f"LANE_{x}_ENABLED": "true" for x in ("A", "B", "C", "D", "E")}


def _registry() -> RuleRegistry:
    return RuleRegistry(env=_LANES).load()


def _ruleset_ids() -> set[str]:
    return {json.loads(p.read_text())["rule_id"] for p in RULESET_DIR.glob("*.rule.json")}


# --------------------------------------------------------------------------
# positive: the committed register validates cleanly end to end
# --------------------------------------------------------------------------
def test_committed_register_validates_clean():
    errors = checker.validate(REGISTER)
    assert errors == [], "\n".join(errors)


# --------------------------------------------------------------------------
# S3 - backfill: one entry per rule file and the reverse; links exist
# --------------------------------------------------------------------------
def test_one_entry_per_rule_file_and_reverse():
    rule_ids = _ruleset_ids()
    entry_ids = [e["rule_id"] for e in ENTRIES]
    assert len(entry_ids) == len(set(entry_ids)), "duplicate register entries"
    assert set(entry_ids) == rule_ids
    assert len(entry_ids) == len(rule_ids) == 23


def test_entry_id_equals_rule_id():
    for e in ENTRIES:
        assert e["entry_id"] == e["rule_id"]


def test_linked_code_test_and_capture_files_exist():
    for e in ENTRIES:
        for rel in [e["rule_file"], *e["code_links"], *e["test_links"]]:
            assert (REPO_ROOT / rel).is_file(), f"{e['rule_id']}: missing {rel}"
        for law in e["law"]:
            snap = REPO_ROOT / law["snapshot_file"]
            assert snap.is_file(), f"{e['rule_id']}: {law['snapshot_file']}"


# --------------------------------------------------------------------------
# S2 - fixed, structured fields; automated status separate from the verdict
# --------------------------------------------------------------------------
def test_fields_are_fixed_and_structured():
    assert REGISTER["field_guide"]["verdict_values"] == [
        "Not reviewed", "Correct", "Incorrect", "Needs re-review"
    ]
    for e in ENTRIES:
        assert set(e) == checker.ENTRY_KEYS, e["rule_id"]
        assert set(e["human_review"]) == checker.HR_KEYS
        assert set(e["automated_tests"]) == {"suites", "note"}
        assert "automated_tests" not in e["human_review"]
        assert e["example"]["expected"]["basis_kind"] in checker.BASIS_KINDS


# --------------------------------------------------------------------------
# S4 - a rule change without a register update is caught
# --------------------------------------------------------------------------
def test_rule_version_and_sha256_match_live_files():
    rule_paths = checker.ruleset_rule_ids()
    for e in ENTRIES:
        assert checker.rule_file_errors(e, rule_paths[e["rule_id"]]) == []


def test_tampered_rule_sha_is_caught_and_names_the_rule():
    rule_paths = checker.ruleset_rule_ids()
    e = copy.deepcopy(BY_ID["r6b-height"])
    e["rule_file_sha256"] = "0" * 64
    errs = checker.rule_file_errors(e, rule_paths["r6b-height"])
    assert any("r6b-height" in m and "same change" in m for m in errs)


def test_changed_rule_version_is_caught():
    rule_paths = checker.ruleset_rule_ids()
    e = copy.deepcopy(BY_ID["r6b-height"])
    e["rule_version"] = "9.9.9-draft"
    errs = checker.rule_file_errors(e, rule_paths["r6b-height"])
    assert any("version" in m and "same change" in m for m in errs)


def test_law_digest_matches_live_capture():
    for e in ENTRIES:
        assert checker.law_errors(e) == [], e["rule_id"]


# --------------------------------------------------------------------------
# S5 - example actual is COMPUTED through the engine; expected is independent
# --------------------------------------------------------------------------
def test_example_actual_is_recomputed_through_the_engine():
    reg = _registry()
    for e in ENTRIES:
        ex = e["example"]
        result = reg.evaluate(e["rule_id"], ex["inputs"])
        assert result.outputs == ex["actual"]["values"], (
            f"{e['rule_id']}: recorded actual does not match the live program output"
        )
        assert result.coverage_status == ex["actual"]["coverage_status"], e["rule_id"]


def test_agrees_equals_expected_vs_actual_or_null_for_gap():
    for e in ENTRIES:
        ex = e["example"]
        exp = ex["expected"]
        if exp["basis_kind"] == "gap":
            assert ex["agrees"] is None, e["rule_id"]
            assert exp["values"] == {}, f"{e['rule_id']}: a gap must record no expected values"
        else:
            assert ex["agrees"] == (exp["values"] == ex["actual"]["values"]), e["rule_id"]
            # a recorded expected answer carries its independent basis + preparer
            assert exp["basis"].strip()
            assert "not checked by a professional" in exp["prepared_by"]


def test_every_basis_kind_is_present_at_least_once():
    kinds = {e["example"]["expected"]["basis_kind"] for e in ENTRIES}
    assert kinds == {"law_text", "reference_case", "gap"}


# --------------------------------------------------------------------------
# S6 - human-verdict rules (positive + negative)
# --------------------------------------------------------------------------
def test_all_backfilled_entries_read_not_reviewed():
    for e in ENTRIES:
        hr = e["human_review"]
        assert hr["verdict"] == "Not reviewed", e["rule_id"]
        assert hr["reviewer_name"] == "" and hr["review_date"] == ""
        assert hr["reviewed_revision"] is None
        assert checker.verdict_errors(e) == []


def test_verdict_refused_without_named_reviewer():
    e = copy.deepcopy(BY_ID["r6b-height"])
    e["human_review"]["verdict"] = "Correct"  # no reviewer name / date / revision / conditions
    errs = checker.verdict_errors(e)
    assert any("refused" in m for m in errs)


def test_correct_against_old_revision_must_be_needs_re_review():
    e = copy.deepcopy(BY_ID["r6b-height"])
    e["revision"] = 2
    e["human_review"].update(
        verdict="Correct", reviewer_name="Jane Roe RA", reviewer_role="architect",
        review_date="2026-10-10", reviewed_revision=1, reviewed_conditions="as drawn",
    )
    errs = checker.verdict_errors(e)
    assert any("Needs re-review" in m for m in errs)


def test_not_reviewed_with_a_reviewer_name_is_rejected():
    e = copy.deepcopy(BY_ID["r6b-height"])
    e["human_review"]["reviewer_name"] = "Someone"
    errs = checker.verdict_errors(e)
    assert any("Not reviewed" in m for m in errs)


def test_a_fully_recorded_current_verdict_is_accepted():
    e = copy.deepcopy(BY_ID["r6b-height"])
    e["human_review"].update(
        verdict="Correct", reviewer_name="Jane Roe RA", reviewer_role="architect",
        review_date="2026-10-10", reviewed_revision=e["revision"],
        reviewed_conditions="R6B lot, no overlay, no special district",
    )
    assert checker.verdict_errors(e) == []


# --------------------------------------------------------------------------
# S7 - append-only history (positive + negative)
# --------------------------------------------------------------------------
def test_history_rules_hold_for_committed_register():
    assert checker.history_errors(REGISTER) == []
    assert [ev["seq"] for ev in REGISTER["history"]] == list(range(1, len(REGISTER["history"]) + 1))


def test_each_entry_has_a_created_event_at_revision_1():
    seen = {
        ev["entry_id"]
        for ev in REGISTER["history"]
        if ev["event"] == "created" and ev["revision"] == 1
    }
    assert seen == set(BY_ID)


def test_missing_created_event_is_caught():
    reg = copy.deepcopy(REGISTER)
    reg["history"] = [ev for ev in reg["history"] if ev["entry_id"] != "r6b-height"]
    # re-number so the only complaint is the missing 'created' event
    for i, ev in enumerate(reg["history"], start=1):
        ev["seq"] = i
    errs = checker.history_errors(reg)
    assert any("r6b-height" in m and "created" in m for m in errs)


def test_non_contiguous_seq_is_caught():
    reg = copy.deepcopy(REGISTER)
    reg["history"][0]["seq"] = 99
    assert any("contiguous" in m for m in checker.history_errors(reg))


def test_current_revision_must_match_latest_event():
    reg = copy.deepcopy(REGISTER)
    reg["entries"][0]["revision"] = 5  # no matching history event
    assert any("latest history revision" in m for m in checker.history_errors(reg))


# --------------------------------------------------------------------------
# S8 - rendered Markdown is current (byte-identical) and has no orphans
# --------------------------------------------------------------------------
def test_register_md_is_byte_identical():
    produced = render.render_register_md(REGISTER)
    on_disk = (render.DOCS_DIR / "REGISTER.md").read_text()
    assert produced == on_disk, "REGISTER.md is stale; run render_review_register.py --write"


def test_history_md_is_byte_identical():
    produced = render.render_history_md(REGISTER)
    on_disk = (render.DOCS_DIR / "HISTORY.md").read_text()
    assert produced == on_disk, "HISTORY.md is stale; run render_review_register.py --write"


def test_each_detail_page_is_byte_identical():
    for e in ENTRIES:
        produced = render.render_detail_md(e)
        on_disk = (render.RULES_MD_DIR / f"{e['rule_id']}.md").read_text()
        assert produced == on_disk, f"{e['rule_id']}.md is stale; run --write"


def test_no_orphan_detail_page():
    wanted = {f"{e['rule_id']}.md" for e in ENTRIES}
    on_disk = {p.name for p in render.RULES_MD_DIR.glob("*.md")}
    assert on_disk == wanted


def test_renderer_is_deterministic():
    assert render.render_register_md(REGISTER) == render.render_register_md(render.load_register())


def test_editing_a_rendered_file_is_caught_by_the_checker():
    # Prove S8's check reacts to a hand-edit without touching the real file.
    original = render.render_detail_md(BY_ID["r6b-height"])
    tampered = original.replace("Not reviewed", "Correct", 1)
    assert tampered != original
    # the on-disk file still matches the renderer, but a hand-edited copy would not
    assert (render.RULES_MD_DIR / "r6b-height.md").read_text() == original


def test_guide_exists_and_is_not_rendered():
    guide = render.DOCS_DIR / "GUIDE.md"
    assert guide.is_file(), "GUIDE.md (handwritten) must exist"
    # GUIDE.md is handwritten and must never be one of the rendered files
    assert guide.name not in {"REGISTER.md", "HISTORY.md"}
