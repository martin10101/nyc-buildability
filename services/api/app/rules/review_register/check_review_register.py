#!/usr/bin/env python3
"""Deterministic validator for the zoning-rule review register (M4-T023).

Pure stdlib. No rule math, no network, no AI call. It reads the authored
``register.json``, the committed rule files, the captured law snapshots and the
rendered Markdown, and returns a list of plain-text problems (empty == clean).
It covers the acceptance scenarios: S2 (fixed, structured fields), S3 (one entry
per rule file and the reverse; links exist), S4 (a rule change without a register
update is caught), S6/S12 (the human-review rules: the reviewer's ORIGINAL
decision is kept, and a DERIVED field says whether it still applies; an old
"Correct" can never be kept on changed logic), S13 (the check enforces
record-keeping only - never a human decision), S14 (planned/committed/tested
behaviour is structured), S15 (the automated-tests field holds a RESULT bound to
the identity of what was tested), S7 (append-only history) and S8 (the rendered
Markdown is current). The example ``actual`` values are re-derived through the
real rule engine by the pytest suite, not here (this module stays engine-free so
it can run anywhere).

The small per-entry checkers (:func:`human_review_errors`, :func:`rule_file_errors`,
:func:`behaviour_errors`, etc.) are deliberately separate functions so the tests
can call them on mutated in-memory data for the negative cases.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re

from . import render_review_register as render

# A pytest function name as cited in a behaviour "tested" item.
TEST_FN_RE = re.compile(r"test_[A-Za-z0-9_]+")

REPO_ROOT = render.REPO_ROOT
RULESET_DIR = render.RULESET_DIR
SNAPSHOT_DIR = render.SNAPSHOT_DIR

VERDICTS = ("Not reviewed", "Correct", "Incorrect", "Needs re-review")
DECISIONS = (None, "Correct", "Incorrect")
BASIS_KINDS = ("law_text", "reference_case", "gap")
AT_STATUS = ("Passed", "Failed", "Not run")
EVENTS = (
    "created", "interpretation_changed", "applicability_changed",
    "implementation_changed", "evidence_changed", "human_verdict_recorded",
    "flagged_for_re_review",
)

ENTRY_KEYS = {
    "entry_id", "rule_id", "rule_file", "rule_version", "rule_file_sha256", "title",
    "family", "law", "applicable_from", "applicable_to", "applies_where", "exceptions",
    "interpretation", "example", "code_links", "test_links", "behaviour",
    "automated_tests", "revision", "last_changed", "human_review", "gaps", "draft_note",
}
HR_KEYS = {
    "decision", "reviewer_name", "reviewer_role", "review_date", "comments",
    "reviewed_revision", "reviewed_conditions", "reviewed_rule_file_sha256",
    "reviewed_law_digests", "applies_to_current", "verdict",
}
BEHAVIOUR_KEYS = {"tested", "committed_untested", "planned"}
AT_KEYS = {
    "status", "tested_commit", "tested_on", "command", "counts", "evidence",
    "tested_rule_file_sha256", "tested_test_file_sha256s", "note",
}
EXAMPLE_KEYS = {"description", "inputs", "expected", "actual", "agrees"}
EXPECTED_KEYS = {"values", "basis_kind", "basis", "prepared_by"}
LAW_KEYS = {
    "section", "official_url", "snapshot_id", "snapshot_file", "last_amended",
    "captured_on", "content_digest_sha256",
}
HISTORY_KEYS = {"seq", "date", "entry_id", "revision", "event", "summary", "by"}


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def lf_sha256(path: pathlib.Path) -> str:
    """sha256 over the file bytes with line endings normalized to LF (so a CRLF
    checkout and an LF checkout hash the same)."""
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def ruleset_rule_ids() -> dict[str, pathlib.Path]:
    out: dict[str, pathlib.Path] = {}
    for path in sorted(RULESET_DIR.glob("*.rule.json")):
        out[json.loads(path.read_text())["rule_id"]] = path
    return out


def current_law_digests(entry: dict) -> dict[str, str]:
    """The capture-id -> content-digest map for the entry's CURRENT law list."""
    return {law["snapshot_id"]: law["content_digest_sha256"] for law in entry["law"]}


# --------------------------------------------------------------------------
# S6 + S12: the human-review rules
# --------------------------------------------------------------------------
def derive_human_review(entry: dict) -> tuple:
    """Compute (applies_to_current, shown_verdict) from the STORED original
    decision and a comparison of the reviewed identities with the entry's current
    rule-file digest, law digests and revision. This is the ONLY place the shown
    verdict and the applies-to-current flag come from; the checker refuses any
    stored value that differs, so touching the register can never keep an old
    'Correct' on changed logic.

    - no decision            -> (None, 'Not reviewed')
    - decision, all identities match current -> (True, that decision)
    - decision, any identity differs         -> (False, 'Needs re-review')
    """
    hr = entry["human_review"]
    if hr.get("decision") is None:
        return (None, "Not reviewed")
    matches = (
        hr.get("reviewed_rule_file_sha256") == entry["rule_file_sha256"]
        and dict(hr.get("reviewed_law_digests") or {}) == current_law_digests(entry)
        and hr.get("reviewed_revision") == entry["revision"]
    )
    if matches:
        return (True, hr["decision"])
    return (False, "Needs re-review")


def human_review_errors(entry: dict) -> list[str]:
    rid = entry.get("rule_id", "?")
    hr = entry.get("human_review", {})
    errs: list[str] = []
    if set(hr) != HR_KEYS:
        errs.append(f"{rid}: human_review keys {sorted(hr)} != {sorted(HR_KEYS)}")
        return errs
    if hr["decision"] not in DECISIONS:
        errs.append(
            f"{rid}: human decision {hr['decision']!r} must be 'Correct', 'Incorrect' or null"
        )
        return errs
    if hr["verdict"] not in VERDICTS:
        errs.append(f"{rid}: shown verdict {hr['verdict']!r} is not one of {list(VERDICTS)}")
        return errs

    named = bool(str(hr["reviewer_name"]).strip())
    dated = bool(str(hr["review_date"]).strip())
    has_rev = hr["reviewed_revision"] is not None
    has_cond = bool(str(hr["reviewed_conditions"]).strip())
    has_rule_identity = bool(str(hr["reviewed_rule_file_sha256"] or "").strip())
    has_law_identity = bool(hr["reviewed_law_digests"])
    any_field = (
        named or dated or has_rev or has_cond or has_rule_identity or has_law_identity
        or bool(str(hr["comments"]).strip()) or bool(str(hr["reviewer_role"]).strip())
    )

    if hr["decision"] is None:
        if any_field:
            errs.append(
                f"{rid}: an entry with no human decision must leave every reviewer field empty "
                "(no name, role, date, comments, reviewed revision, conditions or reviewed "
                "identities); it reads 'Not reviewed'"
            )
    else:
        # A decision is recorded ONLY from a named human reviewer's own answer, with
        # the reviewed identity, never from tests or an agent.
        complete = all((named, dated, has_rev, has_cond, has_rule_identity, has_law_identity))
        if not complete:
            errs.append(
                f"{rid}: a human decision of {hr['decision']!r} is refused - it needs a reviewer "
                "name, a review date, the revision reviewed, the conditions reviewed and the "
                "identity of what was reviewed (the rule-file digest and the law-capture digests); "
                "a decision is never derived from tests or an agent review"
            )

    # The derived fields must equal the recomputed values; a stored value that
    # differs is refused (an old decision can never be shown as current after a change).
    applies, verdict = derive_human_review(entry)
    if hr["applies_to_current"] != applies:
        errs.append(
            f"{rid}: applies_to_current {hr['applies_to_current']!r} does not match the recomputed "
            f"value {applies!r}; it is derived from the reviewed identities versus the current ones"
        )
    if hr["verdict"] != verdict:
        errs.append(
            f"{rid}: shown verdict {hr['verdict']!r} does not match the recomputed verdict "
            f"{verdict!r}; a decision whose reviewed rule digest, law digests or revision differ "
            "from the current ones must read 'Needs re-review' (an old 'Correct' is never kept on "
            "changed logic)"
        )
    return errs


# --------------------------------------------------------------------------
# S14: planned / committed / tested behaviour, told apart
# --------------------------------------------------------------------------
def behaviour_errors(entry: dict) -> list[str]:
    rid = entry.get("rule_id", "?")
    b = entry.get("behaviour", {})
    errs: list[str] = []
    if set(b) != BEHAVIOUR_KEYS:
        errs.append(f"{rid}: behaviour keys {sorted(b)} != {sorted(BEHAVIOUR_KEYS)}")
        return errs
    for key in ("tested", "committed_untested", "planned"):
        items = b[key]
        if not isinstance(items, list) or not all(
            isinstance(s, str) and s.strip() for s in items
        ):
            errs.append(f"{rid}: behaviour.{key} must be a list of non-empty plain sentences")
    # Every 'tested' item names the test function(s) that exercise it, and each named
    # function must be DEFINED in one of the entry's OWN linked test files (a bare
    # "test_" substring is not enough - a cited test in a file the entry does not link
    # and bind would not flip the entry's result to "Not run" when that file changes).
    linked_text = ""
    for rel in entry.get("test_links", []):
        path = REPO_ROOT / rel
        if path.is_file():
            linked_text += path.read_text()
    for item in b.get("tested", []):
        if not isinstance(item, str):
            continue
        names = TEST_FN_RE.findall(item)
        if not names:
            errs.append(
                f"{rid}: a 'tested' behaviour must name the test function(s) that exercise it: "
                f"{item!r}"
            )
            continue
        for name in names:
            if f"def {name}(" not in linked_text:
                errs.append(
                    f"{rid}: tested item names {name}, which is not defined in any of the entry's "
                    f"linked test files {entry.get('test_links')}: {item!r}"
                )
    return errs


# --------------------------------------------------------------------------
# S15: the automated-tests field is a RESULT bound to what was tested
# --------------------------------------------------------------------------
def automated_tests_errors(entry: dict) -> list[str]:
    rid = entry.get("rule_id", "?")
    at = entry.get("automated_tests", {})
    errs: list[str] = []
    if set(at) != AT_KEYS:
        errs.append(f"{rid}: automated_tests keys {sorted(at)} != {sorted(AT_KEYS)}")
        return errs
    # Every linked test file is bound by a digest, and the reverse: the result is
    # bound to exactly the test files the entry links (F1).
    if set(at["tested_test_file_sha256s"]) != set(entry.get("test_links", [])):
        errs.append(
            f"{rid}: automated_tests.tested_test_file_sha256s keys "
            f"{sorted(at['tested_test_file_sha256s'])} must equal the entry's test_links "
            f"{sorted(entry.get('test_links', []))}"
        )
    if at["status"] not in AT_STATUS:
        errs.append(
            f"{rid}: automated_tests status {at['status']!r} is not one of {list(AT_STATUS)}"
        )
    ev = REPO_ROOT / at["evidence"]
    if not ev.is_file():
        errs.append(f"{rid}: automated_tests evidence file missing: {at['evidence']}")

    # The result is bound to the identity of what was tested: if the current rule
    # file or any current test file differs from the recorded digest, the status
    # MUST read 'Not run' so a result for an earlier version is never shown.
    stale = False
    rule_path = REPO_ROOT / entry["rule_file"]
    if not rule_path.is_file() or lf_sha256(rule_path) != at["tested_rule_file_sha256"]:
        stale = True
    for rel, digest in at["tested_test_file_sha256s"].items():
        p = REPO_ROOT / rel
        if not p.is_file() or lf_sha256(p) != digest:
            stale = True
    if stale and at["status"] != "Not run":
        errs.append(
            f"{rid}: the rule file or a test file changed since the recorded run, so "
            "automated_tests.status must read 'Not run' (a result for an earlier version is never "
            "shown as current)"
        )
    return errs


# --------------------------------------------------------------------------
# S4: a rule change without a register update is caught
# --------------------------------------------------------------------------
def rule_file_errors(entry: dict, rule_path: pathlib.Path) -> list[str]:
    rid = entry["rule_id"]
    errs: list[str] = []
    raw = json.loads(rule_path.read_text())
    if raw["rule_version"] != entry["rule_version"]:
        errs.append(
            f"{rid}: rule file version {raw['rule_version']!r} != register "
            f"{entry['rule_version']!r}; "
            "the register must be updated in the same change (new revision, history event)"
        )
    live = lf_sha256(rule_path)
    if live != entry["rule_file_sha256"]:
        errs.append(
            f"{rid}: rule file {entry['rule_file']} content changed (sha256 {live} != recorded "
            f"{entry['rule_file_sha256']}); the register must be updated in the same change "
            "(new revision, history event)"
        )
    return errs


def law_errors(entry: dict) -> list[str]:
    rid = entry["rule_id"]
    errs: list[str] = []
    for law in entry["law"]:
        if set(law) != LAW_KEYS:
            errs.append(f"{rid}: law entry keys {sorted(law)} != {sorted(LAW_KEYS)}")
            continue
        snap_path = REPO_ROOT / law["snapshot_file"]
        if not snap_path.is_file():
            errs.append(f"{rid}: law capture file missing: {law['snapshot_file']}")
            continue
        snap = json.loads(snap_path.read_text())
        if snap["content_digest_sha256"] != law["content_digest_sha256"]:
            errs.append(
                f"{rid}: law digest for {law['section']} does not match the capture "
                f"{law['snapshot_id']} (register {law['content_digest_sha256']} != capture "
                f"{snap['content_digest_sha256']}); re-sync the register with the capture"
            )
        if snap["source"]["request_url"] != law["official_url"]:
            errs.append(
                f"{rid}: law official_url for {law['section']} does not match the capture "
                f"{law['snapshot_id']}"
            )
    return errs


# --------------------------------------------------------------------------
# S2 + S3: structure, fixed fields, one-entry-per-rule, links exist
# --------------------------------------------------------------------------
def structure_errors(register: dict) -> list[str]:
    errs: list[str] = []
    top = {"schema", "schema_version", "generated_note", "field_guide", "entries", "history"}
    if set(register) != top:
        errs.append(f"top-level keys {sorted(register)} != {sorted(top)}")
        return errs
    fg = register["field_guide"]
    if list(fg.get("verdict_values", [])) != list(VERDICTS):
        errs.append("field_guide.verdict_values must be exactly the four allowed verdicts")
    if list(fg.get("decision_values", [])) != ["Correct", "Incorrect", "no decision"]:
        errs.append("field_guide.decision_values must be Correct, Incorrect, no decision")
    if list(fg.get("applies_to_current_values", [])) != ["true", "false", "null"]:
        errs.append("field_guide.applies_to_current_values must be true, false, null")
    if list(fg.get("automated_test_status_values", [])) != list(AT_STATUS):
        errs.append("field_guide.automated_test_status_values must be Passed, Failed, Not run")
    if list(fg.get("basis_kind_values", [])) != list(BASIS_KINDS):
        errs.append("field_guide.basis_kind_values must be law_text, reference_case, gap")
    if list(fg.get("event_values", [])) != list(EVENTS):
        errs.append("field_guide.event_values must be the seven history events")
    for entry in register["entries"]:
        rid = entry.get("rule_id", "?")
        if set(entry) != ENTRY_KEYS:
            diff = sorted(set(entry) ^ ENTRY_KEYS)
            errs.append(f"{rid}: entry keys {diff} differ from the fixed set")
            continue
        if entry["entry_id"] != entry["rule_id"]:
            errs.append(f"{rid}: entry_id {entry['entry_id']!r} must equal rule_id")
        ex = entry["example"]
        if set(ex) != EXAMPLE_KEYS:
            errs.append(f"{rid}: example keys differ from the fixed set")
        elif set(ex["expected"]) != EXPECTED_KEYS:
            errs.append(f"{rid}: example.expected keys differ from the fixed set")
        elif ex["expected"]["basis_kind"] not in BASIS_KINDS:
            errs.append(f"{rid}: example basis_kind {ex['expected']['basis_kind']!r} invalid")
        elif set(ex["actual"]) != {"values", "coverage_status"}:
            errs.append(f"{rid}: example.actual keys differ from the fixed set")
    return errs


def link_errors(register: dict) -> list[str]:
    errs: list[str] = []
    for entry in register["entries"]:
        rid = entry["rule_id"]
        for rel in [entry["rule_file"], *entry["code_links"], *entry["test_links"]]:
            if not (REPO_ROOT / rel).is_file():
                errs.append(f"{rid}: linked file does not exist: {rel}")
    return errs


def backfill_errors(register: dict) -> list[str]:
    errs: list[str] = []
    rule_ids = ruleset_rule_ids()
    entry_ids = [e["rule_id"] for e in register["entries"]]
    if len(entry_ids) != len(set(entry_ids)):
        dupes = sorted({r for r in entry_ids if entry_ids.count(r) > 1})
        errs.append(f"duplicate register entries for rule id(s): {dupes}")
    missing = sorted(set(rule_ids) - set(entry_ids))
    extra = sorted(set(entry_ids) - set(rule_ids))
    for rid in missing:
        errs.append(f"rule file {rid} has no register entry (backfill incomplete)")
    for rid in extra:
        errs.append(f"register entry {rid} has no matching rule file")
    return errs


# --------------------------------------------------------------------------
# S7: append-only history
# --------------------------------------------------------------------------
def history_errors(register: dict) -> list[str]:
    errs: list[str] = []
    history = register["history"]
    entry_ids = {e["rule_id"] for e in register["entries"]}
    current_rev = {e["rule_id"]: e["revision"] for e in register["entries"]}
    for i, ev in enumerate(history, start=1):
        if set(ev) != HISTORY_KEYS:
            errs.append(f"history event seq {ev.get('seq')} keys differ from the fixed set")
            continue
        if ev["seq"] != i:
            errs.append(f"history seq not contiguous from 1: expected {i}, got {ev['seq']}")
        if ev["event"] not in EVENTS:
            errs.append(f"history event {ev['event']!r} (seq {ev['seq']}) is not an allowed event")
        if ev["entry_id"] not in entry_ids:
            errs.append(f"history event seq {ev['seq']} names unknown rule {ev['entry_id']!r}")
    # dates non-decreasing with seq
    for prev, cur in zip(history, history[1:], strict=False):
        if cur["date"] < prev["date"]:
            errs.append(
                f"history not in date order at seq {cur['seq']} "
                f"({cur['date']} < {prev['date']})"
            )
    # per-entry: a created@rev1 event, current revision == latest event's revision,
    # no two consecutive identical events.
    by_entry: dict[str, list[dict]] = {}
    for ev in history:
        by_entry.setdefault(ev["entry_id"], []).append(ev)
    # iterate over EVERY entry (not only those with events) so an entry with no
    # history at all is still caught as missing its 'created' event.
    for rid in current_rev:
        events = by_entry.get(rid, [])
        if not any(e["event"] == "created" and e["revision"] == 1 for e in events):
            errs.append(f"{rid}: history has no 'created' event at revision 1")
        if not events:
            continue
        latest = max(events, key=lambda e: e["seq"])
        if latest["revision"] != current_rev.get(rid):
            errs.append(
                f"{rid}: current revision {current_rev.get(rid)} != latest history revision "
                f"{latest['revision']}"
            )
        for prev, cur in zip(events, events[1:], strict=False):
            if (prev["event"], prev["revision"], prev["summary"]) == (
                cur["event"], cur["revision"], cur["summary"]
            ):
                errs.append(f"{rid}: two consecutive identical history events (no change recorded)")
    return errs


# --------------------------------------------------------------------------
# S8: the rendered Markdown is current
# --------------------------------------------------------------------------
def rendered_errors(register: dict) -> list[str]:
    # Read the render module's paths at call time so a test can point them at a
    # temp folder (F3: run the byte-identical check on a tampered copy).
    docs_dir = render.DOCS_DIR
    rules_md_dir = render.RULES_MD_DIR
    errs: list[str] = []
    checks = {
        docs_dir / "REGISTER.md": render.render_register_md(register),
        docs_dir / "HISTORY.md": render.render_history_md(register),
    }
    for entry in register["entries"]:
        checks[rules_md_dir / f"{entry['rule_id']}.md"] = render.render_detail_md(entry)
    for path, produced in checks.items():
        if not path.is_file():
            errs.append(f"rendered file missing: {path.name} (run --write)")
        elif path.read_text() != produced:
            errs.append(f"rendered file is stale: {path.name} (run --write)")
    # orphan detail pages (a rules/*.md with no entry)
    wanted = {f"{e['rule_id']}.md" for e in register["entries"]}
    if rules_md_dir.is_dir():
        for existing in sorted(rules_md_dir.glob("*.md")):
            if existing.name not in wanted:
                errs.append(f"orphan detail page with no register entry: {existing.name}")
    return errs


# --------------------------------------------------------------------------
# top-level validate
# --------------------------------------------------------------------------
def validate(register: dict) -> list[str]:
    errs: list[str] = []
    errs += structure_errors(register)
    # Stop early if the shape is broken: the deeper checks assume fixed keys.
    if errs:
        return errs
    errs += backfill_errors(register)
    errs += link_errors(register)
    rule_ids = ruleset_rule_ids()
    for entry in register["entries"]:
        rule_path = rule_ids.get(entry["rule_id"])
        if rule_path is not None:
            errs += rule_file_errors(entry, rule_path)
        errs += law_errors(entry)
        errs += human_review_errors(entry)
        errs += behaviour_errors(entry)
        errs += automated_tests_errors(entry)
    errs += history_errors(register)
    errs += rendered_errors(register)
    return errs
