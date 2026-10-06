#!/usr/bin/env python3
"""Deterministic validator for the zoning-rule review register (M4-T023).

Pure stdlib. No rule math, no network, no AI call. It reads the authored
``register.json``, the committed rule files, the captured law snapshots and the
rendered Markdown, and returns a list of plain-text problems (empty == clean).
It covers acceptance scenarios S2 (fixed, structured fields), S3 (one entry per
rule file and the reverse; links exist), S4 (a rule change without a register
update is caught), S6 (human-verdict rules), S7 (append-only history), and S8
(the rendered Markdown is current). The example `actual` values are re-derived
through the real rule engine by the pytest suite, not here (this module stays
engine-free so it can run anywhere).

The small per-entry checkers (:func:`verdict_errors`, :func:`rule_file_errors`,
etc.) are deliberately separate functions so the tests can call them on mutated
in-memory data for the negative cases.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

from . import render_review_register as render

REPO_ROOT = render.REPO_ROOT
RULESET_DIR = render.RULESET_DIR
SNAPSHOT_DIR = render.SNAPSHOT_DIR
DOCS_DIR = render.DOCS_DIR
RULES_MD_DIR = render.RULES_MD_DIR

VERDICTS = ("Not reviewed", "Correct", "Incorrect", "Needs re-review")
BASIS_KINDS = ("law_text", "reference_case", "gap")
EVENTS = (
    "created", "interpretation_changed", "applicability_changed",
    "implementation_changed", "evidence_changed", "human_verdict_recorded",
    "flagged_for_re_review",
)

ENTRY_KEYS = {
    "entry_id", "rule_id", "rule_file", "rule_version", "rule_file_sha256", "title",
    "family", "law", "applicable_from", "applicable_to", "applies_where", "exceptions",
    "interpretation", "example", "code_links", "test_links", "automated_tests",
    "revision", "last_changed", "human_review", "gaps", "draft_note",
}
HR_KEYS = {
    "verdict", "reviewer_name", "reviewer_role", "review_date", "comments",
    "reviewed_revision", "reviewed_conditions",
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


# --------------------------------------------------------------------------
# S6: human-verdict rules (callable on one entry, for negative tests)
# --------------------------------------------------------------------------
def verdict_errors(entry: dict) -> list[str]:
    rid = entry.get("rule_id", "?")
    hr = entry.get("human_review", {})
    errs: list[str] = []
    if set(hr) != HR_KEYS:
        errs.append(f"{rid}: human_review keys {sorted(hr)} != {sorted(HR_KEYS)}")
        return errs
    verdict = hr["verdict"]
    if verdict not in VERDICTS:
        errs.append(f"{rid}: human verdict {verdict!r} is not one of {list(VERDICTS)}")
        return errs
    named = bool(str(hr["reviewer_name"]).strip())
    dated = bool(str(hr["review_date"]).strip())
    has_rev = hr["reviewed_revision"] is not None
    has_cond = bool(str(hr["reviewed_conditions"]).strip())
    if verdict == "Not reviewed":
        if named or dated or has_rev or has_cond:
            errs.append(
                f"{rid}: a 'Not reviewed' verdict must leave reviewer name, date, reviewed "
                "revision and conditions empty"
            )
    else:
        # A real verdict is refused unless a named human reviewer, a date, the
        # revision reviewed and the conditions reviewed are all recorded.
        if not (named and dated and has_rev and has_cond):
            errs.append(
                f"{rid}: verdict {verdict!r} is refused - it needs a reviewer name, a review "
                "date, the revision reviewed and the conditions reviewed (a verdict may be "
                "recorded only from a named human reviewer's own answer, never from tests or an AI)"
            )
        stale_rev = has_rev and hr["reviewed_revision"] != entry["revision"]
        if verdict in ("Correct", "Incorrect") and stale_rev:
            errs.append(
                f"{rid}: verdict {verdict!r} was recorded against revision "
                f"{hr['reviewed_revision']} but the rule is now at revision {entry['revision']}; "
                "it must read 'Needs re-review' until a reviewer checks the current revision"
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
        at = entry["automated_tests"]
        if set(at) != {"suites", "note"}:
            errs.append(f"{rid}: automated_tests keys differ from the fixed set")
        # automated-test status is a field of its own, apart from the human verdict.
        if "human_review" in entry and "automated_tests" in entry["human_review"]:
            errs.append(f"{rid}: automated-test status must stay out of the human_review block")
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
    errs: list[str] = []
    checks = {
        DOCS_DIR / "REGISTER.md": render.render_register_md(register),
        DOCS_DIR / "HISTORY.md": render.render_history_md(register),
    }
    for entry in register["entries"]:
        checks[RULES_MD_DIR / f"{entry['rule_id']}.md"] = render.render_detail_md(entry)
    for path, produced in checks.items():
        if not path.is_file():
            errs.append(f"rendered file missing: {path.relative_to(REPO_ROOT)} (run --write)")
        elif path.read_text() != produced:
            errs.append(f"rendered file is stale: {path.relative_to(REPO_ROOT)} (run --write)")
    # orphan detail pages (a rules/*.md with no entry)
    wanted = {f"{e['rule_id']}.md" for e in register["entries"]}
    if RULES_MD_DIR.is_dir():
        for existing in sorted(RULES_MD_DIR.glob("*.md")):
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
        errs += verdict_errors(entry)
    errs += history_errors(register)
    errs += rendered_errors(register)
    return errs
