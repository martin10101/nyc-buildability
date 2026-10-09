"""Build-time acceptance tests for the zoning-rule review register (M4-T023, D-090).

Deterministic: they read the committed ``register.json``, the committed rule
files, the committed law captures and the committed rendered Markdown, and they
re-derive every example's ``actual`` answer through the program's OWN rule
registry and evaluator. No network, no AI. The negative cases mutate a copy of
the data IN MEMORY (or render it to a temp folder), never the committed rule
files. They prove:

* S3  - one register entry per rule file and the reverse (23 today, no duplicate);
  every linked code / test / capture file exists.
* S4  - each entry pins the rule file's version and a line-ending-normalized
  sha256; a change to either is caught with a message naming the rule.
* S5  - every example's inputs are evaluated through the real engine and the
  result equals the recorded ``actual``; the recorded ``expected`` is independent.
* S6/S12 - the human-review rules: the reviewer's ORIGINAL decision is kept and a
  DERIVED field says whether it still applies; an old "Correct" can never be kept
  on a changed rule file, law capture or revision.
* S13 - the build check passes for an updated entry with no decision AND for one
  whose decision no longer applies; nothing requires a human decision.
* S14 - planned / committed / tested behaviour is told apart, and every tested
  item names the test function(s) that exercise it.
* S15 - the automated-tests field is a RESULT bound to the identity of what was
  tested; the checker demands "Not run" when a rule or test file changes.
* S7  - the append-only history rules, with negative cases.
* S8  - the rendered Markdown is byte-identical to the renderer's output, with no
  stale or orphan detail page (the tamper case runs the checker on a temp copy).
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


def _point_render_at(tmp_path, monkeypatch):
    """Point the renderer/checker at a temp docs folder so a mutated register can
    be rendered and the build check run without touching the committed tree."""
    docs = tmp_path / "docs"
    rules = docs / "rules"
    rules.mkdir(parents=True)
    monkeypatch.setattr(render, "DOCS_DIR", docs)
    monkeypatch.setattr(render, "RULES_MD_DIR", rules)
    return docs, rules


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
    fg = REGISTER["field_guide"]
    assert fg["verdict_values"] == ["Not reviewed", "Correct", "Incorrect", "Needs re-review"]
    assert fg["automated_test_status_values"] == ["Passed", "Failed", "Not run"]
    for e in ENTRIES:
        assert set(e) == checker.ENTRY_KEYS, e["rule_id"]
        assert set(e["human_review"]) == checker.HR_KEYS
        assert set(e["automated_tests"]) == checker.AT_KEYS
        assert set(e["behaviour"]) == checker.BEHAVIOUR_KEYS
        # automated-test status is its own field, never inside the human-review block
        assert "automated_tests" not in e["human_review"]
        assert "decision" not in e["automated_tests"]
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
            assert exp["basis"].strip()
            assert "not checked by a professional" in exp["prepared_by"]


def test_every_basis_kind_is_present_at_least_once():
    kinds = {e["example"]["expected"]["basis_kind"] for e in ENTRIES}
    assert kinds == {"law_text", "reference_case", "gap"}


# --------------------------------------------------------------------------
# S6 - all backfilled entries read 'Not reviewed'; a decision needs a reviewer
# --------------------------------------------------------------------------
def test_all_backfilled_entries_read_not_reviewed():
    for e in ENTRIES:
        hr = e["human_review"]
        assert hr["decision"] is None, e["rule_id"]
        assert hr["verdict"] == "Not reviewed", e["rule_id"]
        assert hr["applies_to_current"] is None
        assert hr["reviewer_name"] == "" and hr["review_date"] == ""
        assert hr["reviewed_revision"] is None
        assert checker.human_review_errors(e) == []


def test_decision_refused_without_a_named_reviewer_and_identity():
    e = copy.deepcopy(BY_ID["r6b-height"])
    e["human_review"]["decision"] = "Correct"  # but no reviewer / date / identity
    errs = checker.human_review_errors(e)
    assert any("refused" in m for m in errs)


def test_not_reviewed_with_a_reviewer_name_is_rejected():
    e = copy.deepcopy(BY_ID["r6b-height"])
    e["human_review"]["reviewer_name"] = "Someone"  # decision still None
    errs = checker.human_review_errors(e)
    assert any("no human decision must leave every reviewer field empty" in m for m in errs)


def test_a_fully_recorded_current_decision_is_accepted():
    e = copy.deepcopy(BY_ID["r6b-height"])
    law = checker.current_law_digests(e)
    e["human_review"].update(
        decision="Correct",
        reviewer_name="Jane Roe RA",
        reviewer_role="licensed architect (sample, not a real review)",
        review_date="2026-10-10",
        comments="sample",
        reviewed_revision=e["revision"],
        reviewed_conditions="R6B lot, no overlay, no special district",
        reviewed_rule_file_sha256=e["rule_file_sha256"],
        reviewed_law_digests=law,
    )
    applies, verdict = checker.derive_human_review(e)
    assert applies is True and verdict == "Correct"
    e["human_review"]["applies_to_current"] = True
    e["human_review"]["verdict"] = "Correct"
    assert checker.human_review_errors(e) == []


# --------------------------------------------------------------------------
# S12 - the ORIGINAL decision is kept; applies-to-current is DERIVED
# --------------------------------------------------------------------------
def _record_correct_decision(e, *, reviewed_rule_sha, reviewed_law, reviewed_rev):
    e["human_review"].update(
        decision="Correct",
        reviewer_name="Jane Roe RA",
        reviewer_role="licensed architect (sample, not a real review)",
        review_date="2026-10-10",
        comments="sample decision",
        reviewed_revision=reviewed_rev,
        reviewed_conditions="R6B lot, no overlay, no special district",
        reviewed_rule_file_sha256=reviewed_rule_sha,
        reviewed_law_digests=reviewed_law,
    )


def test_s12a_rule_change_under_a_correct_decision_reads_needs_re_review():
    # (a) a rule file changes and the register records the new digest in the SAME
    # change -> the entry reads 'Needs re-review' and the original decision stays.
    e = copy.deepcopy(BY_ID["r6b-height"])
    old_sha = e["rule_file_sha256"]
    _record_correct_decision(
        e, reviewed_rule_sha=old_sha, reviewed_law=checker.current_law_digests(e), reviewed_rev=1
    )
    e["rule_file_sha256"] = "a" * 64  # the rule file changed; digest updated here
    e["revision"] = 2
    applies, verdict = checker.derive_human_review(e)
    assert applies is False and verdict == "Needs re-review"
    assert e["human_review"]["decision"] == "Correct"  # original decision kept
    e["human_review"]["applies_to_current"] = False
    e["human_review"]["verdict"] = "Needs re-review"
    assert checker.human_review_errors(e) == []


def test_s12b_touching_the_file_cannot_keep_an_old_correct():
    # (b) merely storing 'Correct' when a reviewed identity differs is refused.
    e = copy.deepcopy(BY_ID["r6b-height"])
    _record_correct_decision(
        e, reviewed_rule_sha="a" * 64, reviewed_law=checker.current_law_digests(e), reviewed_rev=1
    )
    e["human_review"]["applies_to_current"] = True
    e["human_review"]["verdict"] = "Correct"
    errs = checker.human_review_errors(e)
    assert any("Needs re-review" in m for m in errs)


def test_s12c_changed_law_capture_digest_flags_needs_re_review():
    # (c) the same for a changed law-capture digest.
    e = copy.deepcopy(BY_ID["r6b-height"])
    stale_law = {k: "f" * 64 for k in checker.current_law_digests(e)}
    _record_correct_decision(
        e, reviewed_rule_sha=e["rule_file_sha256"], reviewed_law=stale_law,
        reviewed_rev=e["revision"],
    )
    applies, verdict = checker.derive_human_review(e)
    assert applies is False and verdict == "Needs re-review"
    e["human_review"]["applies_to_current"] = False
    e["human_review"]["verdict"] = "Needs re-review"
    assert checker.human_review_errors(e) == []
    e["human_review"]["verdict"] = "Correct"
    e["human_review"]["applies_to_current"] = True
    assert any("Needs re-review" in m for m in checker.human_review_errors(e))


def test_s12d_history_records_the_decision_and_its_later_non_application():
    # (d) a history event records the decision and a later event records that it
    # no longer applies.
    reg = {
        "entries": [{"rule_id": "x", "revision": 2}],
        "history": [
            {"seq": 1, "date": "2026-10-06", "entry_id": "x", "revision": 1,
             "event": "created", "summary": "created", "by": "backfill"},
            {"seq": 2, "date": "2026-10-10", "entry_id": "x", "revision": 1,
             "event": "human_verdict_recorded",
             "summary": "architect recorded Correct for revision 1", "by": "Jane Roe RA"},
            {"seq": 3, "date": "2026-10-12", "entry_id": "x", "revision": 2,
             "event": "flagged_for_re_review",
             "summary": "rule revised; earlier decision no longer applies", "by": "session"},
        ],
    }
    assert checker.history_errors(reg) == []
    events = {ev["event"] for ev in reg["history"]}
    assert "human_verdict_recorded" in events and "flagged_for_re_review" in events


# --------------------------------------------------------------------------
# S13 - the build check enforces record-keeping only (never a human decision)
# --------------------------------------------------------------------------
def test_s13_updated_entry_without_a_decision_passes_the_check(tmp_path, monkeypatch):
    reg = copy.deepcopy(REGISTER)
    e = next(x for x in reg["entries"] if x["rule_id"] == "r6b-lot-coverage")
    e["revision"] = 2
    e["last_changed"] = "2026-10-20"
    reg["history"].append({
        "seq": len(reg["history"]) + 1, "date": "2026-10-20",
        "entry_id": "r6b-lot-coverage", "revision": 2, "event": "implementation_changed",
        "summary": "sample revision for the record-keeping-only test", "by": "session",
    })
    _point_render_at(tmp_path, monkeypatch)
    render.write_all(reg)
    assert checker.validate(reg) == []  # passes with no decision at all
    assert e["human_review"]["verdict"] == "Not reviewed"


def test_s13_entry_whose_decision_no_longer_applies_passes_the_check(tmp_path, monkeypatch):
    reg = copy.deepcopy(REGISTER)
    e = next(x for x in reg["entries"] if x["rule_id"] == "r6b-height")
    _record_correct_decision(
        e, reviewed_rule_sha=e["rule_file_sha256"],
        reviewed_law=checker.current_law_digests(e), reviewed_rev=1,
    )
    e["revision"] = 2  # the rule was revised; the decision (rev 1) no longer applies
    e["last_changed"] = "2026-10-20"
    e["human_review"]["applies_to_current"] = False
    e["human_review"]["verdict"] = "Needs re-review"
    reg["history"].extend([
        {"seq": len(reg["history"]) + 1, "date": "2026-10-12", "entry_id": "r6b-height",
         "revision": 1, "event": "human_verdict_recorded",
         "summary": "architect recorded Correct for revision 1 (sample)", "by": "Jane Roe RA"},
        {"seq": len(reg["history"]) + 2, "date": "2026-10-20", "entry_id": "r6b-height",
         "revision": 2, "event": "flagged_for_re_review",
         "summary": "rule revised; earlier decision no longer applies (sample)", "by": "session"},
    ])
    _point_render_at(tmp_path, monkeypatch)
    render.write_all(reg)
    assert checker.validate(reg) == []  # passes though the verdict reads Needs re-review
    assert e["human_review"]["verdict"] == "Needs re-review"
    assert e["human_review"]["decision"] == "Correct"  # original decision kept


# --------------------------------------------------------------------------
# S14 - planned / committed / tested behaviour, told apart
# --------------------------------------------------------------------------
def test_behaviour_is_structured_and_tested_items_name_a_test():
    for e in ENTRIES:
        assert checker.behaviour_errors(e) == [], e["rule_id"]
        for item in e["behaviour"]["tested"]:
            assert "test_" in item, f"{e['rule_id']}: tested item names no test: {item!r}"


def test_committed_untested_items_say_no_test_was_found():
    for e in ENTRIES:
        for item in e["behaviour"]["committed_untested"]:
            assert "no test" in item.lower(), f"{e['rule_id']}: {item!r}"


def test_behaviour_rejects_a_tested_item_without_a_test_name():
    e = copy.deepcopy(BY_ID["r6b-height"])
    e["behaviour"]["tested"] = ["reports five heights"]  # no test_ name
    assert any("name the test" in m for m in checker.behaviour_errors(e))


def test_tested_item_naming_a_function_not_in_a_linked_file_is_refused():
    # F1(d): a cited function that is not DEFINED in one of the entry's linked
    # test files is refused (a bare "test_" substring is no longer enough).
    e = copy.deepcopy(BY_ID["r6b-height"])
    e["behaviour"]["tested"] = ["does something (test: test_this_function_is_defined_nowhere_xyz)"]
    errs = checker.behaviour_errors(e)
    assert any(
        "test_this_function_is_defined_nowhere_xyz" in m and "not defined" in m for m in errs
    )


def test_every_committed_tested_citation_is_defined_in_a_linked_file():
    # The committed register must satisfy the stronger rule for all 23 entries.
    for e in ENTRIES:
        assert checker.behaviour_errors(e) == [], e["rule_id"]


# --------------------------------------------------------------------------
# S15 - the automated-tests field is a RESULT bound to what was tested
# --------------------------------------------------------------------------
def test_automated_tests_result_shape_and_status():
    for e in ENTRIES:
        assert checker.automated_tests_errors(e) == [], e["rule_id"]
        at = e["automated_tests"]
        assert at["status"] == "Passed"
        assert len(at["tested_commit"]) == 40
        assert (REPO_ROOT / at["evidence"]).is_file()
        assert at["tested_rule_file_sha256"] == checker.lf_sha256(REPO_ROOT / e["rule_file"])


def test_changed_test_file_demands_status_not_run():
    e = copy.deepcopy(BY_ID["r6b-height"])
    rel = e["test_links"][0]
    e["automated_tests"]["tested_test_file_sha256s"][rel] = "0" * 64  # test file "changed"
    errs = checker.automated_tests_errors(e)
    assert any("Not run" in m for m in errs)
    e["automated_tests"]["status"] = "Not run"
    assert checker.automated_tests_errors(e) == []


def test_changed_rule_file_demands_status_not_run():
    e = copy.deepcopy(BY_ID["r6b-height"])
    e["automated_tests"]["tested_rule_file_sha256"] = "0" * 64  # rule file "changed"
    errs = checker.automated_tests_errors(e)
    assert any("Not run" in m for m in errs)
    e["automated_tests"]["status"] = "Not run"
    assert checker.automated_tests_errors(e) == []


def test_changed_second_linked_test_file_digest_demands_not_run():
    # F1(d): an entry that binds TWO test files must flip to "Not run" when the
    # SECOND linked file's recorded digest no longer matches.
    e = copy.deepcopy(BY_ID["r5-residential-far"])
    assert len(e["test_links"]) == 2
    second = e["test_links"][1]
    e["automated_tests"]["tested_test_file_sha256s"][second] = "0" * 64
    assert any("Not run" in m for m in checker.automated_tests_errors(e))
    e["automated_tests"]["status"] = "Not run"
    assert checker.automated_tests_errors(e) == []


def test_a_linked_test_file_not_bound_by_a_digest_is_caught():
    # F1(a) reverse binding: every linked test file must be in the digest map.
    e = copy.deepcopy(BY_ID["r5-residential-far"])
    second = e["test_links"][1]
    del e["automated_tests"]["tested_test_file_sha256s"][second]
    assert any("tested_test_file_sha256s" in m for m in checker.automated_tests_errors(e))


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


def test_editing_a_rendered_file_is_caught_by_the_checker(tmp_path, monkeypatch):
    # F3: run the checker's rendered-file check against a TAMPERED on-disk copy.
    _point_render_at(tmp_path, monkeypatch)
    render.write_all(REGISTER)
    assert checker.rendered_errors(REGISTER) == []  # a clean, current temp tree
    target = render.RULES_MD_DIR / "r6b-height.md"
    target.write_text(target.read_text().replace("Not reviewed", "Correct", 1))
    errs = checker.rendered_errors(REGISTER)
    assert any("r6b-height.md" in e and "stale" in e for e in errs)


def test_guide_exists_and_is_not_rendered():
    guide = render.DOCS_DIR / "GUIDE.md"
    assert guide.is_file(), "GUIDE.md (handwritten) must exist"
    assert guide.name not in {"REGISTER.md", "HISTORY.md"}
