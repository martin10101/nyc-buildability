#!/usr/bin/env python3
"""Deterministic checker for the review register's CALCULATION entries (M4-T038, D-090).

Split out of ``review_register_calculations.py`` (DB-211 c): the per-entry validators, the
code-identity fingerprint, the cited-reference-case checks, the six-step comparison checks and the
two DB-211 (a) guards, and the top-level :func:`validate_calculations` that ``--check`` runs
(``check_review_register.validate`` calls it). Pure stdlib: no rule math, no network, no AI call.
Public names are re-exported from the old path.

A calculation entry has no rule file, so it is fingerprinted by the LF-normalized sha256 of its
implementing code module(s) and a combined ``code_identity_sha256``; a drift in any module fails
the check exactly as a changed rule file is caught for a rule entry. The EXPECTED side of every
worked example is an independent reference case (``case#row``); the ACTUAL side is the program's
own answer. Expected is never taken from a program run. No human verdict is ever entered.

Two guards close the gap backlog row DB-211 (a) named - a wrong six-step verdict or a dropped
legal-or-design row that a FRESH RENDER would hide, because the rendered page would then match the
mutated data. Both guards read the register JSON directly, so they stay red after ``--write``:
:func:`step_verdict_errors` binds each step's verdict to the state of its actual side, and
:func:`figure_rows_errors` requires that every figure the six steps rest on has its legal-or-design
row.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

from . import calc_render
from . import render_review_register as render
from .calc_vocab import (
    ACTUAL_KEYS,
    ACTUAL_STATES,
    AT_KEYS,
    AT_STATUS,
    BASIS_KINDS,
    BEHAVIOUR_KEYS,
    CALC_COMPARISON_KEYS,
    CALC_ENTRY_KEYS,
    CALC_HISTORY_KEYS,
    CITED_ROW_KEYS,
    CLOSING_KEYS,
    CODE_MODULE_KEYS,
    DECISIONS,
    DISAGREEMENT_KEYS,
    DISAGREEMENT_KINDS,
    ENTRY_KIND_VALUES,
    EXAMPLE_KEYS,
    EXPECTED_KEYS,
    HISTORY_EVENTS,
    HR_KEYS,
    LEGAL_VS_DESIGN_KEYS,
    LEGAL_VS_DESIGN_KINDS,
    PRELIM_TOKENS,
    PRELIM_WORDS,
    STEP_ABSENT_STATES,
    STEP_ACTUAL_KEYS,
    STEP_EXPECTED_KEYS,
    STEP_KEYS,
    STEP_PRESENT_STATES,
    STEP_VERDICTS,
    VERDICTS,
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
        if not isinstance(row["program_results"], list) or not all(
            isinstance(x, str) for x in row["program_results"]
        ):
            errs.append(f"{eid}: closing row program_results must be a list of result keys")
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
# DB-211 (a) guard 1: a step's verdict follows the state of its actual side
# --------------------------------------------------------------------------
def step_verdict_errors(entry: dict) -> list[str]:
    """Bind each six-step verdict to the state of its actual (program) side, so a wrong verdict is
    caught by the data itself and not only by the page being stale (DB-211 a; the G4 mutation f that
    a fresh render hid).

    - A step whose program side is WITHHELD or NOT BUILT has nothing to compare, so its verdict can
      only be 'side_missing' - never 'agree' or 'differ'. (A 'not_available' side may still read
      'differ' when the difference is one of method, e.g. the withheld building option against the
      independent two buildings - step 3.)
    - A step that reads 'agree' needs both sides present: its actual side must be a PRESENT state
      and both the expected and the actual value must be non-empty.
    """
    eid = entry.get("entry_id", "?")
    errs: list[str] = []
    for s in entry.get("steps", []):
        step_no = s.get("step")
        actual = s.get("actual", {})
        state = actual.get("state")
        verdict = s.get("verdict")
        if state not in STEP_PRESENT_STATES + STEP_ABSENT_STATES:
            errs.append(
                f"{eid}: step {step_no} actual state {state!r} is not one of "
                f"{list(STEP_PRESENT_STATES + STEP_ABSENT_STATES)}"
            )
            continue
        if state in ("withheld", "not_built") and verdict != "side_missing":
            errs.append(
                f"{eid}: step {step_no} program side is {state}, so its verdict must be "
                f"'side_missing', never {verdict!r} (there is nothing to compare; DB-211 a)"
            )
        if verdict == "agree":
            if state not in STEP_PRESENT_STATES:
                errs.append(
                    f"{eid}: step {step_no} reads 'agree' but its program side is {state} (not a "
                    f"present state); 'agree' needs both sides present and equal (DB-211 a)"
                )
            if not str(s.get("expected", {}).get("value", "")).strip():
                errs.append(
                    f"{eid}: step {step_no} reads 'agree' but its independent expected value is "
                    "empty; 'agree' needs both sides present (DB-211 a)"
                )
            if not str(actual.get("value", "")).strip():
                errs.append(
                    f"{eid}: step {step_no} reads 'agree' but its program actual value is empty; "
                    "'agree' needs both sides present (DB-211 a)"
                )
    return errs


# --------------------------------------------------------------------------
# DB-211 (a) guard 2: every figure the six steps rest on has its legal-or-design row
# --------------------------------------------------------------------------
def figure_rows_errors(entry: dict) -> list[str]:
    """Require that every figure the six steps rest on has a legal-or-design row, so a dropped row
    is caught by the data itself and not only by the page being stale (DB-211 a; the G4 mutation h2
    that a fresh render hid).

    - Each legal rule the steps combine (every section in the entry's ``law``) must have its own
      LEGAL_REQUIREMENT row among the ``legal_vs_design`` figures.
    - Each preliminary-assumption figure the steps use (the apartment size 700 and the efficiency
      share 0.60-0.75, wherever they appear in a step's text) must have a DESIGN_ASSUMPTION row
      carrying that figure.
    """
    eid = entry.get("entry_id", "?")
    errs: list[str] = []
    rows = entry.get("legal_vs_design", [])
    legal_figs = [str(r.get("figure", "")) for r in rows if r.get("kind") == "LEGAL_REQUIREMENT"]
    design_figs = [str(r.get("figure", "")) for r in rows if r.get("kind") == "DESIGN_ASSUMPTION"]
    for law_item in entry.get("law", []):
        section = str(law_item.get("section", ""))
        if section and not any(section in fig for fig in legal_figs):
            errs.append(
                f"{eid}: the six-step figure for ZR {section} has no LEGAL_REQUIREMENT row in "
                f"legal_vs_design (every figure the steps rest on needs its legal-or-design row; "
                "DB-211 a)"
            )
    steps_text = json.dumps(entry.get("steps", []))
    for tok in PRELIM_TOKENS:
        if tok in steps_text and not any(tok in fig for fig in design_figs):
            errs.append(
                f"{eid}: the preliminary-assumption figure {tok!r} appears in the steps but has no "
                "DESIGN_ASSUMPTION row in legal_vs_design (DB-211 a)"
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
        # DB-211 (a) guards: a six-step verdict follows its actual side, and every figure the steps
        # rest on has its legal-or-design row. Caught by the data, so a fresh render cannot hide it.
        errs += step_verdict_errors(entry)
        errs += figure_rows_errors(entry)
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
    calc_dir = calc_render._calc_md_dir()
    errs: list[str] = []
    for calc in register.get("calculations", []):
        path = calc_dir / f"{calc['entry_id']}.md"
        produced = calc_render.render_calc_detail_md(calc, register)
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
