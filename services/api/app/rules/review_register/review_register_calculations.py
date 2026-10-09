#!/usr/bin/env python3
"""Calculation-entry renderer and checker for the zoning-rule review register (M4-T038, D-090).

The register (M4-T023) carries one entry per rule-definition file. This focused module adds a
SECOND kind of entry - a CALCULATION entry - for the combined-rule and arithmetic calculations
that turn the rules into the reported floor area, footprint, building option, legal dwelling-unit
limit and preliminary apartment estimate, and which have no rule file of their own. It holds the
calculation renderer and the calculation checker helpers so ``render_review_register.py`` and
``check_review_register.py`` stay inside their module boundaries (they import this and keep their
old public import paths). Pure stdlib: no rule math, no network, no AI call.

A calculation entry has no rule file, so it is fingerprinted by the LF-normalized sha256 of its
implementing code module(s) and a combined ``code_identity_sha256``; a drift in any module fails
the check exactly as a changed rule file is caught for a rule entry. The EXPECTED side of every
worked example is an independent reference case (``case#row``); the ACTUAL side is the program's
own answer (read from the committed results document, or recomputed through the engine's functions
for a figure the engine computes and the document withholds). Expected is never taken from a
program run. No human verdict is ever entered; the human-review block is the same as a rule
entry's, with the recorded identity being the code identity, the law digests and the revision.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

from . import render_review_register as render

# --------------------------------------------------------------------------
# vocabularies
# --------------------------------------------------------------------------
ENTRY_KIND_VALUES = ("calculation", "calculation_comparison")
LEGAL_VS_DESIGN_KINDS = ("LEGAL_REQUIREMENT", "DESIGN_ASSUMPTION")
BASIS_KINDS = ("law_text", "reference_case", "gap")
ACTUAL_STATES = (
    "available", "available_conditional", "conditional", "withheld",
    "not_available", "not_built",
)
STEP_VERDICTS = ("agree", "differ", "side_missing")
DISAGREEMENT_KINDS = (
    "a missing fact about the property", "unresolved law", "code not built",
    "a design assumption that differs",
)
AT_STATUS = ("Passed", "Failed", "Not run")
VERDICTS = ("Not reviewed", "Correct", "Incorrect", "Needs re-review")
DECISIONS = (None, "Correct", "Incorrect")
# The literal words the owner requires on the apartment size and efficiency share (R700).
PRELIM_WORDS = "preliminary assumption"
PRELIM_TOKENS = ("700", "0.60", "0.75")

# --------------------------------------------------------------------------
# field key sets
# --------------------------------------------------------------------------
LAW_KEYS = {
    "section", "official_url", "snapshot_id", "snapshot_file", "last_amended",
    "captured_on", "content_digest_sha256",
}
CODE_MODULE_KEYS = {"path", "sha256"}
BEHAVIOUR_KEYS = {"tested", "committed_untested", "planned"}
LEGAL_VS_DESIGN_KEYS = {
    "figure", "kind", "quoted_text", "capture_snapshot_id", "capture_digest",
}
EXPECTED_KEYS = {"values", "basis_kind", "basis", "cited_rows", "prepared_by"}
ACTUAL_KEYS = {"values", "state", "engine_values", "engine_note"}
EXAMPLE_KEYS = {"description", "inputs", "expected", "actual", "agrees"}
CITED_ROW_KEYS = {"case_file", "row_id"}
AT_KEYS = {
    "status", "tested_commit", "tested_on", "command", "counts", "evidence",
    "tested_code_identity_sha256", "tested_test_file_sha256s", "note",
}
HR_KEYS = {
    "decision", "reviewer_name", "reviewer_role", "review_date", "comments",
    "reviewed_revision", "reviewed_conditions", "reviewed_code_identity_sha256",
    "reviewed_law_digests", "applies_to_current", "verdict",
}
STEP_KEYS = {"step", "name", "component_ref", "expected", "actual", "verdict", "note"}
STEP_EXPECTED_KEYS = {"value", "basis_kind", "cited_rows", "prepared_by"}
STEP_ACTUAL_KEYS = {"value", "state", "source"}
CLOSING_KEYS = {"disagreements", "missing_facts"}
DISAGREEMENT_KEYS = {"kind", "what", "would_settle"}

_COMMON_KEYS = {
    "entry_id", "entry_kind", "title", "family", "law", "combines_rule_ids",
    "code_modules", "code_identity_sha256", "applicable_from", "applicable_to",
    "applies_where", "exceptions", "interpretation", "units", "measurement_basis",
    "behaviour", "legal_vs_design", "linked_records", "test_links", "automated_tests",
    "revision", "last_changed", "human_review", "gaps", "coverage_gap", "draft_note",
}
CALC_ENTRY_KEYS = _COMMON_KEYS | {"inputs", "formula", "rounding", "example"}
CALC_COMPARISON_KEYS = _COMMON_KEYS | {"steps", "closing"}

CALC_HISTORY_KEYS = {"seq", "date", "entry_id", "revision", "event", "summary", "by"}
HISTORY_EVENTS = (
    "created", "interpretation_changed", "applicability_changed",
    "implementation_changed", "evidence_changed", "human_verdict_recorded",
    "flagged_for_re_review",
)


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------
def lf_sha256(path: pathlib.Path) -> str:
    """sha256 over the file bytes with line endings normalized to LF (so a CRLF checkout and an
    LF checkout hash the same)."""
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def code_identity(code_modules: list[dict]) -> str:
    """The combined fingerprint of an entry's implementing code modules: sha256 over the sorted
    ``path:sha256`` lines. This is how an entry with no rule file is identified."""
    lines = sorted(f"{m['path']}:{m['sha256']}" for m in code_modules)
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def _calc_md_dir() -> pathlib.Path:
    """The calculation detail-page folder, read from the render module at call time so a test can
    point the renderer at a temp docs folder."""
    return render.DOCS_DIR / "calculations"


def current_law_digests(law: list[dict]) -> dict[str, str]:
    return {law_item["snapshot_id"]: law_item["content_digest_sha256"] for law_item in law}


# --------------------------------------------------------------------------
# human review (same discipline as a rule entry; identity is the CODE identity)
# --------------------------------------------------------------------------
def derive_human_review(entry: dict) -> tuple:
    """(applies_to_current, shown_verdict) from the STORED decision versus the entry's current
    code identity, law digests and revision. A decision never survives a code change."""
    hr = entry["human_review"]
    if hr.get("decision") is None:
        return (None, "Not reviewed")
    matches = (
        hr.get("reviewed_code_identity_sha256") == entry["code_identity_sha256"]
        and dict(hr.get("reviewed_law_digests") or {}) == current_law_digests(entry["law"])
        and hr.get("reviewed_revision") == entry["revision"]
    )
    return (True, hr["decision"]) if matches else (False, "Needs re-review")


def human_review_errors(entry: dict) -> list[str]:
    eid = entry.get("entry_id", "?")
    hr = entry.get("human_review", {})
    errs: list[str] = []
    if set(hr) != HR_KEYS:
        errs.append(f"{eid}: human_review keys {sorted(hr)} != {sorted(HR_KEYS)}")
        return errs
    if hr["decision"] not in DECISIONS:
        errs.append(f"{eid}: human decision {hr['decision']!r} must be Correct, Incorrect or null")
        return errs
    if hr["verdict"] not in VERDICTS:
        errs.append(f"{eid}: shown verdict {hr['verdict']!r} is not one of {list(VERDICTS)}")
        return errs
    named = bool(str(hr["reviewer_name"]).strip())
    dated = bool(str(hr["review_date"]).strip())
    has_rev = hr["reviewed_revision"] is not None
    has_cond = bool(str(hr["reviewed_conditions"]).strip())
    has_code_identity = bool(str(hr["reviewed_code_identity_sha256"] or "").strip())
    has_law_identity = bool(hr["reviewed_law_digests"])
    any_field = (
        named or dated or has_rev or has_cond or has_code_identity or has_law_identity
        or bool(str(hr["comments"]).strip()) or bool(str(hr["reviewer_role"]).strip())
    )
    if hr["decision"] is None:
        if any_field:
            errs.append(
                f"{eid}: an entry with no human decision must leave every reviewer field empty; "
                "it reads 'Not reviewed'"
            )
    else:
        complete = all((named, dated, has_rev, has_cond, has_code_identity, has_law_identity))
        if not complete:
            errs.append(
                f"{eid}: a human decision of {hr['decision']!r} is refused - it needs a reviewer "
                "name, a review date, the revision reviewed, the conditions reviewed and the "
                "identity of what was reviewed (the code identity and the law-capture digests); a "
                "decision is never derived from tests or an agent review"
            )
    applies, verdict = derive_human_review(entry)
    if hr["applies_to_current"] != applies:
        errs.append(
            f"{eid}: applies_to_current {hr['applies_to_current']!r} does not match the "
            f"recomputed value {applies!r}"
        )
    if hr["verdict"] != verdict:
        errs.append(
            f"{eid}: shown verdict {hr['verdict']!r} does not match the recomputed verdict "
            f"{verdict!r}; a decision whose reviewed code identity, law digests or revision differ "
            "from the current ones must read 'Needs re-review'"
        )
    return errs


# --------------------------------------------------------------------------
# code-module identity (a drift fails the check like a changed rule file)
# --------------------------------------------------------------------------
def code_module_errors(entry: dict) -> list[str]:
    eid = entry.get("entry_id", "?")
    errs: list[str] = []
    mods = entry.get("code_modules", [])
    if not mods:
        errs.append(f"{eid}: a calculation entry must list at least one implementing code module")
        return errs
    for m in mods:
        if set(m) != CODE_MODULE_KEYS:
            errs.append(f"{eid}: code_module keys {sorted(m)} != {sorted(CODE_MODULE_KEYS)}")
            return errs
    recomputed_identity = code_identity(mods)
    if entry.get("code_identity_sha256") != recomputed_identity:
        errs.append(
            f"{eid}: code_identity_sha256 {entry.get('code_identity_sha256')} != the sha256 over "
            f"the sorted module lines {recomputed_identity}"
        )
    for m in mods:
        path = render.REPO_ROOT / m["path"]
        if not path.is_file():
            errs.append(f"{eid}: code module missing: {m['path']}")
        elif lf_sha256(path) != m["sha256"]:
            errs.append(
                f"{eid}: code module {m['path']} content changed (sha256 {lf_sha256(path)} != "
                f"recorded {m['sha256']}); the register must be updated in the same change "
                "(new revision, history event)"
            )
    return errs


# --------------------------------------------------------------------------
# automated tests (a RESULT bound to the code identity + the test-file digests)
# --------------------------------------------------------------------------
def automated_tests_errors(entry: dict) -> list[str]:
    eid = entry.get("entry_id", "?")
    at = entry.get("automated_tests", {})
    errs: list[str] = []
    if set(at) != AT_KEYS:
        errs.append(f"{eid}: automated_tests keys {sorted(at)} != {sorted(AT_KEYS)}")
        return errs
    if set(at["tested_test_file_sha256s"]) != set(entry.get("test_links", [])):
        errs.append(
            f"{eid}: automated_tests.tested_test_file_sha256s keys "
            f"{sorted(at['tested_test_file_sha256s'])} must equal the entry's test_links "
            f"{sorted(entry.get('test_links', []))}"
        )
    if at["status"] not in AT_STATUS:
        errs.append(
            f"{eid}: automated_tests status {at['status']!r} is not one of {list(AT_STATUS)}")
    if not (render.REPO_ROOT / at["evidence"]).is_file():
        errs.append(f"{eid}: automated_tests evidence file missing: {at['evidence']}")
    stale = at["tested_code_identity_sha256"] != entry.get("code_identity_sha256")
    for rel, digest in at["tested_test_file_sha256s"].items():
        p = render.REPO_ROOT / rel
        if not p.is_file() or lf_sha256(p) != digest:
            stale = True
    if stale and at["status"] != "Not run":
        errs.append(
            f"{eid}: a code module or a test file changed since the recorded run, so "
            "automated_tests.status must read 'Not run'"
        )
    return errs


# --------------------------------------------------------------------------
# law (reuse the rule-entry digest/url verification)
# --------------------------------------------------------------------------
def law_errors(entry: dict) -> list[str]:
    from . import check_review_register as checker

    return checker.law_errors({"rule_id": entry.get("entry_id", "?"), "law": entry.get("law", [])})


# --------------------------------------------------------------------------
# legal vs design: every figure marked; preliminary-assumption wording kept
# --------------------------------------------------------------------------
def legal_vs_design_errors(entry: dict) -> list[str]:
    eid = entry.get("entry_id", "?")
    errs: list[str] = []
    rows = entry.get("legal_vs_design", [])
    if not rows:
        errs.append(f"{eid}: legal_vs_design must mark every figure/step (it is empty)")
        return errs
    for row in rows:
        if set(row) != LEGAL_VS_DESIGN_KEYS:
            errs.append(f"{eid}: legal_vs_design row keys {sorted(row)} != "
                        f"{sorted(LEGAL_VS_DESIGN_KEYS)}")
            continue
        if row["kind"] not in LEGAL_VS_DESIGN_KINDS:
            errs.append(
                f"{eid}: legal_vs_design figure {row['figure']!r} is unmarked - kind "
                f"{row['kind']!r} must be LEGAL_REQUIREMENT or DESIGN_ASSUMPTION"
            )
            continue
        if row["kind"] == "LEGAL_REQUIREMENT":
            if not str(row["quoted_text"]).strip():
                errs.append(
                    f"{eid}: LEGAL_REQUIREMENT {row['figure']!r} must quote the captured text")
            snap_id = row["capture_snapshot_id"]
            snap_path = render.SNAPSHOT_DIR / f"{snap_id}.snapshot.json"
            if not snap_path.is_file():
                errs.append(f"{eid}: legal capture missing for {row['figure']!r}: {snap_id}")
            else:
                snap = json.loads(snap_path.read_text())
                if snap["content_digest_sha256"] != row["capture_digest"]:
                    errs.append(
                        f"{eid}: legal capture digest for {row['figure']!r} does not match "
                        f"{snap_id} (row {row['capture_digest']} != capture "
                        f"{snap['content_digest_sha256']})"
                    )
                quote = str(row["quoted_text"]).strip()
                excerpt = str(snap.get("verbatim_excerpt", "")).replace("\n", " ")
                if quote and quote not in excerpt:
                    errs.append(
                        f"{eid}: quoted_text for {row['figure']!r} is not a verbatim fragment of "
                        f"capture {snap_id}"
                    )
        # The apartment size (700) and the efficiency share (0.60-0.75) must read
        # 'preliminary assumption' wherever they appear, and be a design assumption (R700).
        figure = str(row["figure"])
        if any(tok in figure for tok in PRELIM_TOKENS):
            if row["kind"] != "DESIGN_ASSUMPTION":
                errs.append(
                    f"{eid}: the apartment size / efficiency share {figure!r} is a chosen design "
                    "assumption, not a legal requirement"
                )
            if PRELIM_WORDS not in figure:
                errs.append(
                    f"{eid}: the apartment size / efficiency share {figure!r} must carry the words "
                    f"'{PRELIM_WORDS}'"
                )
    return errs


# --------------------------------------------------------------------------
# cited reference-case rows exist and are not superseded (ruling C3)
# --------------------------------------------------------------------------
def _case_rows(case_file: str) -> dict | None:
    path = render.REPO_ROOT / case_file
    if not path.is_file():
        return None
    data = json.loads(path.read_text())
    return {r["row_id"]: r for r in data.get("rows", [])}


def cited_rows_errors(eid: str, cited_rows: list[dict]) -> list[str]:
    errs: list[str] = []
    for ref in cited_rows:
        if set(ref) != CITED_ROW_KEYS:
            errs.append(f"{eid}: cited_row keys {sorted(ref)} != {sorted(CITED_ROW_KEYS)}")
            continue
        rows = _case_rows(ref["case_file"])
        if rows is None:
            errs.append(f"{eid}: cited reference case file does not exist: {ref['case_file']}")
            continue
        row = rows.get(ref["row_id"])
        if row is None:
            errs.append(
                f"{eid}: cited case row does not exist: {ref['case_file']}#{ref['row_id']}"
            )
            continue
        if row.get("superseded_by") or row.get("superseded"):
            errs.append(
                f"{eid}: cited case row is superseded: {ref['case_file']}#{ref['row_id']}"
            )
    return errs


def _cited_row(ref: dict) -> dict | None:
    rows = _case_rows(ref.get("case_file", ""))
    return None if rows is None else rows.get(ref.get("row_id"))


# --------------------------------------------------------------------------
# example (component calculation entries)
# --------------------------------------------------------------------------
def example_errors(entry: dict) -> list[str]:
    eid = entry.get("entry_id", "?")
    errs: list[str] = []
    ex = entry.get("example", {})
    if set(ex) != EXAMPLE_KEYS:
        errs.append(f"{eid}: example keys {sorted(ex)} != {sorted(EXAMPLE_KEYS)}")
        return errs
    exp = ex["expected"]
    if set(exp) != EXPECTED_KEYS:
        errs.append(f"{eid}: example.expected keys {sorted(exp)} != {sorted(EXPECTED_KEYS)}")
        return errs
    if exp["basis_kind"] not in BASIS_KINDS:
        errs.append(f"{eid}: example basis_kind {exp['basis_kind']!r} invalid")
    act = ex["actual"]
    if set(act) != ACTUAL_KEYS:
        errs.append(f"{eid}: example.actual keys {sorted(act)} != {sorted(ACTUAL_KEYS)}")
        return errs
    if act["state"] not in ACTUAL_STATES:
        errs.append(
            f"{eid}: example.actual state {act['state']!r} is not one of {list(ACTUAL_STATES)}")
    errs += cited_rows_errors(eid, exp["cited_rows"])
    if exp["basis_kind"] == "reference_case" and not exp["cited_rows"]:
        errs.append(f"{eid}: a reference_case expected answer must cite at least one case#row")
    if ex["agrees"] not in (True, False, None):
        errs.append(f"{eid}: example.agrees {ex['agrees']!r} must be true, false or null")
    # Agreement rule carried from the reference cases: a single figure is recorded only when the
    # readings agree. Where the two readings differ, the expected side holds both figures (or reads
    # 'not known') and agrees is null; a forced single figure with agrees true is refused.
    if ex["agrees"] is True and exp["basis_kind"] == "gap":
        errs.append(f"{eid}: agrees cannot be true when the expected answer is a gap")
    # A withheld / not-built actual side is never a forced match: agrees must be null.
    if act["state"] in ("withheld", "not_available", "not_built") and ex["agrees"] is True:
        errs.append(
            f"{eid}: the program side is {act['state']}, so agrees must be null with a "
            "'program side withheld/not built' note - never a forced match"
        )
    # A cited reading that is 'not known' (the two step-P6 readings differ, so no single figure)
    # can never be a forced match: agrees must be null (the reference case's agreement rule).
    for ref in exp["cited_rows"]:
        row = _cited_row(ref)
        if row and row.get("expected", {}).get("kind") == "not_known" and ex["agrees"] is True:
            errs.append(
                f"{eid}: cited reading {ref['case_file']}#{ref['row_id']} is 'not known' (the "
                "readings differ); the expected side holds both figures or 'not known' and agrees "
                "is null - never a single forced figure"
            )
    return errs


# --------------------------------------------------------------------------
# steps + closing (the six-step comparison entry, ruling C1 / C4)
# --------------------------------------------------------------------------
def comparison_errors(entry: dict) -> list[str]:
    eid = entry.get("entry_id", "?")
    errs: list[str] = []
    steps = entry.get("steps", [])
    if [s.get("step") for s in steps] != [1, 2, 3, 4, 5, 6]:
        errs.append(f"{eid}: the comparison must show six steps in order 1..6")
    for s in steps:
        if set(s) != STEP_KEYS:
            errs.append(f"{eid}: step keys {sorted(s)} != {sorted(STEP_KEYS)}")
            continue
        if set(s["expected"]) != STEP_EXPECTED_KEYS:
            errs.append(f"{eid}: step {s['step']} expected keys differ from the fixed set")
        else:
            if s["expected"]["basis_kind"] not in BASIS_KINDS:
                errs.append(f"{eid}: step {s['step']} expected basis_kind invalid")
            errs += cited_rows_errors(eid, s["expected"]["cited_rows"])
        if set(s["actual"]) != STEP_ACTUAL_KEYS:
            errs.append(f"{eid}: step {s['step']} actual keys differ from the fixed set")
        if s["verdict"] not in STEP_VERDICTS:
            errs.append(f"{eid}: step {s['step']} verdict {s['verdict']!r} is not one of "
                        f"{list(STEP_VERDICTS)}")
    closing = entry.get("closing", {})
    if set(closing) != CLOSING_KEYS:
        errs.append(f"{eid}: closing keys {sorted(closing)} != {sorted(CLOSING_KEYS)}")
        return errs
    rows = list(closing["disagreements"]) + list(closing["missing_facts"])
    if not rows:
        errs.append(f"{eid}: the comparison must end in the disagreements and missing facts")
    for row in rows:
        if set(row) != DISAGREEMENT_KEYS:
            errs.append(f"{eid}: closing row keys {sorted(row)} != {sorted(DISAGREEMENT_KEYS)}")
            continue
        if row["kind"] not in DISAGREEMENT_KINDS:
            errs.append(f"{eid}: closing row kind {row['kind']!r} is not one of "
                        f"{list(DISAGREEMENT_KINDS)}")
    # The difference of method is recorded as a disagreement that names backlog row DB-210 (C4).
    text = json.dumps(closing)
    if "DB-210" not in text:
        errs.append(f"{eid}: the method difference must name backlog row DB-210 (ruling C4)")
    if "a design assumption that differs" not in [r.get("kind") for r in closing["disagreements"]]:
        errs.append(
            f"{eid}: the engine's sample stack against the independent two buildings must be "
            "recorded as a disagreement of kind 'a design assumption that differs' (C4)"
        )
    return errs


# --------------------------------------------------------------------------
# one calculation entry
# --------------------------------------------------------------------------
def _common_errors(entry: dict, entry_ids: set[str]) -> list[str]:
    eid = entry.get("entry_id", "?")
    errs: list[str] = []
    if entry["entry_kind"] not in ENTRY_KIND_VALUES:
        errs.append(f"{eid}: entry_kind {entry['entry_kind']!r} invalid")
    for rid in entry.get("combines_rule_ids", []):
        if rid not in entry_ids:
            errs.append(f"{eid}: combines_rule_ids names a rule entry that does not exist: {rid}")
    if set(entry.get("behaviour", {})) != BEHAVIOUR_KEYS:
        errs.append(f"{eid}: behaviour keys differ from the fixed set")
    for rel in entry.get("test_links", []):
        if not (render.REPO_ROOT / rel).is_file():
            errs.append(f"{eid}: linked test file does not exist: {rel}")
    if not str(entry.get("coverage_gap", "")).strip():
        errs.append(f"{eid}: coverage_gap must be one plain sentence (R703)")
    errs += code_module_errors(entry)
    errs += law_errors(entry)
    errs += human_review_errors(entry)
    errs += automated_tests_errors(entry)
    errs += legal_vs_design_errors(entry)
    return errs


def calc_entry_errors(entry: dict, entry_ids: set[str]) -> list[str]:
    eid = entry.get("entry_id", "?")
    kind = entry.get("entry_kind")
    wanted = CALC_ENTRY_KEYS if kind == "calculation" else CALC_COMPARISON_KEYS
    if set(entry) != wanted:
        errs = [f"{eid}: entry keys {sorted(set(entry) ^ wanted)} differ from the {kind} set"]
        return errs
    errs = _common_errors(entry, entry_ids)
    if kind == "calculation":
        errs += example_errors(entry)
    else:
        errs += comparison_errors(entry)
    return errs


# --------------------------------------------------------------------------
# coverage gaps (data; at least the nine of the inventory; ruling C6)
# --------------------------------------------------------------------------
def coverage_gaps_errors(register: dict) -> list[str]:
    gaps = register.get("coverage_gaps", [])
    errs: list[str] = []
    if not isinstance(gaps, list) or not all(isinstance(g, str) and g.strip() for g in gaps):
        errs.append("coverage_gaps must be a list of plain sentences")
        return errs
    if len(gaps) < 9:
        errs.append(f"coverage_gaps holds {len(gaps)} gaps; the inventory lists at least nine")
    if not any("M5-T144" in g for g in gaps):
        errs.append(
            "coverage_gaps must state that M5-T144 changed the engine and moved no entry (R703)")
    if not any("three-answers" in g or "three answers" in g for g in gaps):
        errs.append("coverage_gaps must state that the scenario three-answers engine has no entry")
    return errs


# --------------------------------------------------------------------------
# calculations history (a SEPARATE list from the rule-entry history)
# --------------------------------------------------------------------------
def calculations_history_errors(register: dict) -> list[str]:
    history = register.get("calculations_history", [])
    calc_ids = {c["entry_id"] for c in register.get("calculations", [])}
    current_rev = {c["entry_id"]: c["revision"] for c in register.get("calculations", [])}
    errs: list[str] = []
    for i, ev in enumerate(history, start=1):
        if set(ev) != CALC_HISTORY_KEYS:
            errs.append(f"calculations_history seq {ev.get('seq')} keys differ from the fixed set")
            continue
        if ev["seq"] != i:
            errs.append(
                f"calculations_history seq not contiguous from 1: expected {i}, got {ev['seq']}")
        if ev["event"] not in HISTORY_EVENTS:
            errs.append(f"calculations_history event {ev['event']!r} (seq {ev['seq']}) not allowed")
        if ev["entry_id"] not in calc_ids:
            errs.append(f"calculations_history seq {ev['seq']} names unknown calculation "
                        f"{ev['entry_id']!r}")
    for prev, cur in zip(history, history[1:], strict=False):
        if cur["date"] < prev["date"]:
            errs.append(f"calculations_history not in date order at seq {cur['seq']}")
    by_entry: dict[str, list[dict]] = {}
    for ev in history:
        by_entry.setdefault(ev["entry_id"], []).append(ev)
    for cid in current_rev:
        events = by_entry.get(cid, [])
        if not any(e["event"] == "created" and e["revision"] == 1 for e in events):
            errs.append(f"{cid}: calculations_history has no 'created' event at revision 1")
        if events and max(events, key=lambda e: e["seq"])["revision"] != current_rev[cid]:
            errs.append(f"{cid}: current revision != latest calculations_history revision")
    return errs


# --------------------------------------------------------------------------
# rendered Markdown is current (REGISTER.md calc section + calculations/<id>.md)
# --------------------------------------------------------------------------
def calc_rendered_errors(register: dict) -> list[str]:
    calc_dir = _calc_md_dir()
    errs: list[str] = []
    for calc in register.get("calculations", []):
        path = calc_dir / f"{calc['entry_id']}.md"
        produced = render_calc_detail_md(calc, register)
        if not path.is_file():
            errs.append(f"rendered calculation page missing: {calc['entry_id']}.md (run --write)")
        elif path.read_text() != produced:
            errs.append(f"rendered calculation page is stale: {calc['entry_id']}.md (run --write)")
    wanted = {f"{c['entry_id']}.md" for c in register.get("calculations", [])}
    if calc_dir.is_dir():
        for existing in sorted(calc_dir.glob("*.md")):
            if existing.name == "README.md":
                continue
            if existing.name not in wanted:
                errs.append(f"orphan calculation page with no entry: {existing.name}")
    return errs


# --------------------------------------------------------------------------
# top-level: validate every calculation addition
# --------------------------------------------------------------------------
def validate_calculations(register: dict) -> list[str]:
    errs: list[str] = []
    fg = register.get("field_guide", {})
    if list(fg.get("entry_kind_values", [])) != list(ENTRY_KIND_VALUES):
        errs.append("field_guide.entry_kind_values must be calculation, calculation_comparison")
    entry_ids = {e["rule_id"] for e in register.get("entries", [])}
    calcs = register.get("calculations", [])
    seen: list[str] = []
    for calc in calcs:
        cid = calc.get("entry_id", "?")
        if cid in entry_ids:
            errs.append(f"{cid}: a calculation entry id must not collide with a rule entry id")
        seen.append(cid)
        errs += calc_entry_errors(calc, entry_ids)
    dupes = sorted({c for c in seen if seen.count(c) > 1})
    if dupes:
        errs.append(f"duplicate calculation entry id(s): {dupes}")
    errs += coverage_gaps_errors(register)
    errs += calculations_history_errors(register)
    errs += calc_rendered_errors(register)
    return errs


# --------------------------------------------------------------------------
# rendering (compact; the calculation detail pages, table, gaps and history)
# --------------------------------------------------------------------------
def _b(items: list, empty: str = "(none recorded)") -> list[str]:
    """Bullet lines for a list, or a single empty-note bullet."""
    return [f"- {x}" for x in items] or [f"- {empty}"]


def _cites(cited_rows: list[dict]) -> str:
    return ", ".join(
        f"{pathlib.Path(r['case_file']).stem}#{r['row_id']}" for r in cited_rows
    ) or "-"


def _law_lines(law: list[dict]) -> list[str]:
    if not law:
        return ["(no legal rule; a design-only calculation)"]
    lines = [
        "| Section | Official link | Last amended | Captured on | Capture id | Digest (sha256) |",
        "|---|---|---|---|---|---|",
    ]
    for x in law:
        lines.append(
            f"| {render._esc(x['section'])} "
            f"| [{render._esc(x['section'])}]({x['official_url']}) "
            f"| {x['last_amended']} | {x['captured_on']} "
            f"| `{x['snapshot_id']}` | `{x['content_digest_sha256']}` |"
        )
    return lines


def _legal_vs_design_lines(rows: list[dict]) -> list[str]:
    out = ["| Figure or step | Kind | Quoted captured text (legal) | Capture |",
           "|---|---|---|---|"]
    for r in rows:
        quote = render._esc(r["quoted_text"]) if r["quoted_text"] else "-"
        cap = f"`{r['capture_snapshot_id']}`" if r["capture_snapshot_id"] else "-"
        out.append(f"| {render._esc(r['figure'])} | {r['kind']} | {quote} | {cap} |")
    return out


def _example_lines(entry: dict) -> list[str]:
    ex = entry["example"]
    exp, act = ex["expected"], ex["actual"]
    agrees = {True: "yes - the program's answer matches the independent expected answer",
              False: "NO - the program's answer differs from the independent expected answer",
              None: "not determined - a side is withheld/not built, or the two readings differ"}
    exp_val = ("a gap - see the basis" if exp["basis_kind"] == "gap"
               else render._values_sentence(exp["values"]) or "not known (see the basis)")
    act_val = render._values_sentence(act["values"]) or "withheld/not built"
    out = ["## Worked example: independent expected versus the program's actual", "",
           ex["description"], "",
           f"- Inputs: {render._values_sentence(ex['inputs'])}",
           f"- Expected answer (independent): {exp_val}",
           f"- Basis of the expected answer ({exp['basis_kind']}): {exp['basis']}",
           f"- Independent record(s) cited: {_cites(exp['cited_rows'])}",
           f"- Who prepared the expected answer: {exp['prepared_by']}",
           f"- Program's actual answer: {act_val}",
           f"- Standing of the program's answer: {act['state']}"]
    if act["engine_values"] or act["engine_note"]:
        out.append("- What the engine computes (the document withholds it): "
                   f"{render._values_sentence(act['engine_values']) or 'see the note'}")
        if act["engine_note"]:
            out.append(f"  - {act['engine_note']}")
    out += [f"- Do they agree? {agrees[ex['agrees']]}", ""]
    return out


def _steps_lines(entry: dict) -> list[str]:
    verd = {"agree": "agree", "differ": "differ", "side_missing": "a side is missing"}
    out = ["## The complete calculation, step by step", "",
           "| Step | What | Independent expected | Program actual (standing) | Verdict |",
           "|---|---|---|---|---|"]
    for s in entry["steps"]:
        exp = f"{render._esc(s['expected']['value'])} ({_cites(s['expected']['cited_rows'])})"
        act = f"{render._esc(s['actual']['value'])} [{s['actual']['state']}]"
        out.append(
            f"| {s['step']} | {render._esc(s['name'])} | {exp} | {act} | {verd[s['verdict']]} |")
    out.append("")
    for s in entry["steps"]:
        out += [f"### Step {s['step']}: {s['name']}", "",
                f"- Component: `{s['component_ref']}`",
                f"- Independent expected answer: {s['expected']['value']}",
                f"- Program's actual answer and standing: {s['actual']['value']} "
                f"({s['actual']['state']}; source: {s['actual']['source']})",
                f"- Verdict: {s['verdict']}", f"- {s['note']}", ""]
    cl = entry["closing"]
    settle = "- [{kind}] {what} - would be settled by: {would_settle}"
    out += ["## Every disagreement and missing fact (and what would settle it)", "",
            "Disagreements:"]
    out += [settle.format(**r) for r in cl["disagreements"]] or ["- (none recorded)"]
    out += ["", "Missing facts:"]
    out += [settle.format(**r) for r in cl["missing_facts"]] or ["- (none recorded)"]
    out.append("")
    return out


def render_calc_detail_md(entry: dict, register: dict | None = None) -> str:
    at, hr = entry["automated_tests"], entry["human_review"]
    appl_to = entry["applicable_to"] or "no end date"
    ev_tail = at["evidence"].split("docs/zoning-rule-review/", 1)[-1]
    rev = hr["reviewed_revision"] if hr["reviewed_revision"] is not None else "-"
    L = [f"# {entry['title']}", "", render.GENERATED_BANNER, "", f"> {entry['draft_note']}", "",
         f"- Calculation id: `{entry['entry_id']}`",
         f"- Entry kind: {entry['entry_kind']} (a combined/arithmetic calculation; no rule file)",
         f"- Family: {entry['family']}",
         f"- Applies from: {entry['applicable_from']} (to: {appl_to})",
         f"- Revision: {entry['revision']} (last changed {entry['last_changed']})",
         "- Combines rule entries: "
         + (", ".join(f"`{r}`" for r in entry["combines_rule_ids"]) or "none"), "",
         "## Code identity", "",
         "An entry with no rule file is fingerprinted by the LF-normalized sha256 of its code "
         "module(s). If a module changes and the entry is not revised, the check fails - as a "
         "changed rule file is caught for a rule entry.", "",
         f"- Combined code identity: `{entry['code_identity_sha256']}`", "- Modules:"]
    L += [f"  - `{m['path']}` (`{m['sha256']}`)" for m in entry["code_modules"]]
    L += ["", "## Law", ""] + _law_lines(entry["law"])
    L += ["", "## Where it applies", "", entry["applies_where"],
          "", "## Exceptions and limits", ""] + _b(entry["exceptions"])
    L += ["", "## How the program reads it", "", entry["interpretation"], "",
          "## Inputs, units, measurement basis, formula and rounding", ""]
    if "inputs" in entry:
        L += ["- Inputs:"] + [f"  - {x}" for x in entry["inputs"]]
    L += [f"- Units: {entry['units']}", f"- Measurement basis: {entry['measurement_basis']}"]
    if "formula" in entry:
        L += [f"- Formula: {entry['formula']}", f"- Rounding: {entry['rounding']}"]
    L.append("")
    L += _example_lines(entry) if entry["entry_kind"] == "calculation" else _steps_lines(entry)
    beh = entry["behaviour"]
    L += ["## What the program does today versus what is planned", "", "Implemented and tested:"]
    L += _b(beh["tested"])
    L += ["", "In the program but no test checks it:"] + _b(beh["committed_untested"])
    L += ["", "Planned, not built:"] + _b(beh["planned"], "Nothing recorded as planned.")
    L += ["", "## Automated test result", "", f"- Status: {at['status']}",
          f"- Code identity tested: `{at['tested_code_identity_sha256']}`",
          f"- Commit tested: `{at['tested_commit']}`", f"- Date tested: {at['tested_on']}",
          f"- Command: `{at['command']}`", f"- Counts: {at['counts']}",
          f"- Evidence: [run log](../{ev_tail})", "- Test files tested:"]
    L += [f"  - `{rel}` (`{dig}`)" for rel, dig in at["tested_test_file_sha256s"].items()]
    L += [f"- {at['note']}", "", "## Linked records (linked, not copied)", ""]
    L += _b(entry["linked_records"], "(none)")
    L += ["", "## Code and tests", ""]
    L += [f"- `{m['path']}`" for m in entry["code_modules"]]
    L += [f"- `{rel}`" for rel in entry["test_links"]]
    L += ["", "## Legal requirements and chosen design assumptions", ""]
    L += _legal_vs_design_lines(entry["legal_vs_design"])
    L += ["", "## Gaps and unresolved questions", ""] + _b(entry["gaps"])
    L += ["", f"- Coverage gap: {entry['coverage_gap']}", "",
          "## Human review", "", f"- Current verdict: {hr['verdict']}",
          f"- Reviewer name: {hr['reviewer_name'] or '-'}",
          f"- Reviewer role: {hr['reviewer_role'] or '-'}",
          f"- Review date: {hr['review_date'] or '-'}", f"- Revision reviewed: {rev}",
          f"- Conditions reviewed: {hr['reviewed_conditions'] or '-'}",
          f"- Comments: {hr['comments'] or '-'}",
          "- The verdict is derived from the reviewer's recorded decision and whether it still "
          "matches the current code identity, law captures and revision. A verdict is a named "
          "human reviewer's own answer; agent reviews are never recorded here."]
    if hr["decision"] is not None and hr["applies_to_current"] is False:
        L += ["", f"Earlier decision: {hr['decision']}, given by {hr['reviewer_name']} on "
              f"{hr['review_date']} for revision {hr['reviewed_revision']}; it does not apply to "
              "the current version."]
    L.append("")
    return "\n".join(L) + "\n"


def render_calculations_table_section(register: dict) -> list[str]:
    L = ["## Calculations (combined-rule/arithmetic calculations with no rule file of their own)",
         "",
         "These entries trace the calculations that turn the rules into the reported floor area, "
         "footprint, building option, legal dwelling-unit limit and preliminary apartment "
         "estimate. Each is fingerprinted by the sha256 of its code module(s); its worked example "
         "sets an independent reference case (expected) beside the program's own answer (actual). "
         "See `GUIDE.md` for the calculation fields.", "",
         "| Calculation | Kind | Combines | Code identity | Tests | Human verdict | Details |",
         "|---|---|---|---|---|---|---|"]
    for c in register.get("calculations", []):
        at = c["automated_tests"]
        tail = at["evidence"].split("docs/zoning-rule-review/", 1)[-1]
        combines = ", ".join(f"`{r}`" for r in c["combines_rule_ids"]) or "-"
        test_cell = f"{render._esc(at['status'])} ({at['tested_commit'][:8]}) [log]({tail})"
        L.append(
            f"| {render._esc(c['title'])} (`{c['entry_id']}`) | {c['entry_kind']} | {combines} "
            f"| `{c['code_identity_sha256'][:12]}...` | {test_cell} "
            f"| {render._esc(c['human_review']['verdict'])} "
            f"| [open](calculations/{c['entry_id']}.md) |")
    L.append("")
    return L


def render_coverage_gaps_section(register: dict) -> list[str]:
    L = ["## Coverage gaps (what the register does not yet cover)", "",
         "Each gap is a plain sentence. Stating a gap is not covering it; turning a gap into "
         "follow-up work is an orchestrator decision.", ""]
    L += [f"{i}. {g}" for i, g in enumerate(register.get("coverage_gaps", []), start=1)]
    L.append("")
    return L


def render_calculations_history_section(register: dict) -> list[str]:
    L = ["## Calculations history (append-only, oldest first)", "",
         "| Seq | Date | Calculation | Revision | Event | Summary | By |",
         "|---|---|---|---|---|---|---|"]
    esc = render._esc
    for ev in register.get("calculations_history", []):
        L.append(
            f"| {ev['seq']} | {ev['date']} | `{ev['entry_id']}` | {ev['revision']} "
            f"| {esc(ev['event'])} | {esc(ev['summary'])} | {esc(ev['by'])} |")
    L.append("")
    return L


def write_calc_pages(register: dict) -> list[pathlib.Path]:
    """Write the calculation detail pages; sweep any orphan page (never README.md)."""
    calc_dir = _calc_md_dir()
    calc_dir.mkdir(parents=True, exist_ok=True)
    written, wanted = [], set()
    for calc in register.get("calculations", []):
        path = calc_dir / f"{calc['entry_id']}.md"
        path.write_text(render_calc_detail_md(calc, register))
        written.append(path)
        wanted.add(path.name)
    for existing in calc_dir.glob("*.md"):
        if existing.name != "README.md" and existing.name not in wanted:
            existing.unlink()
    return written
