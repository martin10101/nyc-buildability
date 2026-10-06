#!/usr/bin/env python3
"""Deterministic renderer + checker CLI for the zoning-rule review register (M4-T023).

Reads ``register.json`` (the authored, machine-readable register) and renders the
human-readable Markdown under ``docs/zoning-rule-review/``: the short current
table (``REGISTER.md``), one detail page per rule (``rules/<rule_id>.md``) and the
append-only history (``HISTORY.md``). The output is a pure function of the JSON:
running it twice over the same JSON produces byte-identical Markdown. It performs
no rule math, no network I/O and no AI call; it only re-presents the committed
data (the hand-written ``GUIDE.md`` is NOT rendered and is never overwritten).

Usage (stdlib only, run from anywhere)::

    python render_review_register.py --write   # (re)render the Markdown
    python render_review_register.py --check    # validate; non-zero on any issue

``--check`` delegates to :mod:`check_review_register`, which validates the data
and asserts the committed Markdown equals this renderer's output.
``tests/rules/test_zoning_rule_review_register.py`` additionally re-derives every
example through the program's own rule engine.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[4]
REGISTER_JSON = HERE / "register.json"
RULESET_DIR = HERE.parent / "rulesets"
SNAPSHOT_DIR = REPO_ROOT / "docs" / "research" / "zr-snapshots" / "v1"
DOCS_DIR = REPO_ROOT / "docs" / "zoning-rule-review"
RULES_MD_DIR = DOCS_DIR / "rules"

GENERATED_BANNER = (
    "GENERATED FILE - do not edit by hand. Produced by "
    "`services/api/app/rules/review_register/render_review_register.py` from "
    "`register.json`; edit the JSON and re-render. See `GUIDE.md`."
)


# --------------------------------------------------------------------------
# Loading + small helpers
# --------------------------------------------------------------------------
def load_register() -> dict:
    return json.loads(REGISTER_JSON.read_text())


def detail_rel_path(rule_id: str) -> str:
    return f"rules/{rule_id}.md"


def _esc(text: str) -> str:
    """Escape a table cell so a literal pipe does not break the Markdown row."""
    return str(text).replace("|", "\\|")


def _num(value) -> str:
    """Plain rendering of a JSON number: an integral float shows as an integer."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _val(value) -> str:
    """Plain rendering of any scalar in a values/inputs map."""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (int, float)):
        return _num(value)
    if value is None:
        return "not set"
    return str(value)


def _values_sentence(values: dict) -> str:
    if not values:
        return "none"
    return "; ".join(f"{k} = {_val(v)}" for k, v in values.items())


def _law_cell(entry: dict) -> str:
    law = entry["law"]
    first = law[0]
    link = f"[{_esc(first['section'])}]({first['official_url']})"
    txt = f"{link}, applies from {entry['applicable_from']}"
    if len(law) > 1:
        txt += f" (+{len(law) - 1} more section(s), see details)"
    return txt


def _reviewer_cell(entry: dict) -> str:
    hr = entry["human_review"]
    if hr["reviewer_name"] or hr["review_date"]:
        bits = [b for b in (hr["reviewer_name"], hr["review_date"]) if b]
        return _esc(", ".join(bits))
    return "-"


def _evidence_rel(at: dict, from_rules_dir: bool) -> str:
    """Link to the committed test-run log, relative to the Markdown that cites it.

    The register stores a repo-relative path under ``docs/zoning-rule-review/``;
    REGISTER.md links it as ``evidence/...`` and a detail page as ``../evidence/...``.
    """
    tail = at["evidence"].split("docs/zoning-rule-review/", 1)[-1]
    return ("../" + tail) if from_rules_dir else tail


# --------------------------------------------------------------------------
# REGISTER.md - the short current table
# --------------------------------------------------------------------------
def render_register_md(register: dict) -> str:
    lines: list[str] = []
    lines.append("# Zoning-rule review register")
    lines.append("")
    lines.append(GENERATED_BANNER)
    lines.append("")
    lines.append(
        f"This register covers the {len(register['entries'])} rule-definition files the program "
        "has today - one entry per rule. That is **not** complete coverage of the New York City "
        "Zoning Resolution; it is the set of zoning rules the program has implemented so far."
    )
    lines.append("")
    lines.append(
        "For each rule it shows the law it rests on, where it applies, how the program reads it in "
        "plain English, a worked example, what the program does today versus what is only planned, "
        "the result of the rule's automated tests, and a place for a New York City architect or "
        "zoning examiner to record whether the program's reading is correct."
    )
    lines.append("")
    lines.append(
        "Every rule here is the program's own **unreviewed draft** reading of the law, not legal "
        "advice. This is a review record: nothing in the program waits for a verdict (ADR-007)."
    )
    lines.append("")
    lines.append(
        "See `GUIDE.md` for what each field means, how the register is kept current, and how a "
        "human verdict is recorded. The detail pages are under `rules/`; the append-only history "
        "is in `HISTORY.md`."
    )
    lines.append("")
    lines.append(
        "- The **Tests** column shows the recorded result of the rule's own automated tests "
        "(Passed, Failed or Not run), the short commit they ran at, and a link to the run log. A "
        "passing result is a code check, not a human or professional review of the law."
    )
    lines.append(
        "- The **Human verdict** is one of: Not reviewed, Correct, Incorrect, Needs re-review. It "
        "is filled only from a named human reviewer's own answer - never because tests passed or "
        "an agent review agreed. Agent reviews of this register are agent reviews, not human or "
        "professional reviews. Every rule reads 'Not reviewed' today."
    )
    lines.append("")
    lines.append(
        "| Rule | Law | Revision (last changed) | Tests | Human verdict "
        "| Reviewer and date | Details |"
    )
    lines.append("|---|---|---|---|---|---|---|")
    for entry in register["entries"]:
        at = entry["automated_tests"]
        short = at["tested_commit"][:8]
        test_cell = f"{_esc(at['status'])} ({short}) [log]({_evidence_rel(at, False)})"
        lines.append(
            f"| {_esc(entry['title'])} (`{entry['rule_id']}`) "
            f"| {_law_cell(entry)} "
            f"| {entry['revision']} ({entry['last_changed']}) "
            f"| {test_cell} "
            f"| {_esc(entry['human_review']['verdict'])} "
            f"| {_reviewer_cell(entry)} "
            f"| [open]({detail_rel_path(entry['rule_id'])}) |"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# rules/<rule_id>.md - one detail page per rule
# --------------------------------------------------------------------------
def render_detail_md(entry: dict) -> str:
    lines: list[str] = []
    lines.append(f"# {entry['title']}")
    lines.append("")
    lines.append(GENERATED_BANNER)
    lines.append("")
    lines.append(f"> {entry['draft_note']}")
    lines.append("")
    lines.append(f"- Rule id: `{entry['rule_id']}`")
    lines.append(f"- Family: {entry['family']}")
    lines.append(f"- Rule version: {entry['rule_version']}")
    appl_to = entry["applicable_to"] if entry["applicable_to"] else "no end date"
    lines.append(f"- Applies from: {entry['applicable_from']} (to: {appl_to})")
    lines.append(f"- Revision: {entry['revision']} (last changed {entry['last_changed']})")
    lines.append("")

    lines.append("## Law")
    lines.append("")
    lines.append(
        "| Section | Official link | Last amended | Captured on | Capture id "
        "| Content digest (sha256) |"
    )
    lines.append("|---|---|---|---|---|---|")
    for law in entry["law"]:
        lines.append(
            f"| {_esc(law['section'])} | [{_esc(law['section'])}]({law['official_url']}) "
            f"| {law['last_amended']} | {law['captured_on']} | `{law['snapshot_id']}` "
            f"| `{law['content_digest_sha256']}` |"
        )
    lines.append("")

    lines.append("## Where it applies")
    lines.append("")
    lines.append(entry["applies_where"])
    lines.append("")

    lines.append("## Exceptions and limits")
    lines.append("")
    for item in entry["exceptions"]:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## How the program reads it")
    lines.append("")
    lines.append(entry["interpretation"])
    lines.append("")

    ex = entry["example"]
    lines.append("## Example")
    lines.append("")
    lines.append(ex["description"])
    lines.append("")
    lines.append(f"- Inputs: {_values_sentence(ex['inputs'])}")
    exp = ex["expected"]
    if exp["basis_kind"] == "gap":
        lines.append("- Expected answer: not determined from the captured text (a gap - see below)")
    else:
        lines.append(f"- Expected answer: {_values_sentence(exp['values'])}")
    lines.append(f"- Basis of the expected answer ({exp['basis_kind']}): {exp['basis']}")
    lines.append(f"- Who prepared the expected answer: {exp['prepared_by']}")
    act = ex["actual"]
    lines.append(f"- Answer the program gives: {_values_sentence(act['values'])}")
    lines.append(f"- Result label the program attaches: {act['coverage_status']}")
    if ex["agrees"] is None:
        agrees = "not determined (the expected answer is a gap)"
    elif ex["agrees"]:
        agrees = "yes - the program's answer matches the expected answer"
    else:
        agrees = "NO - the program's answer differs from the expected answer (see the gap note)"
    lines.append(f"- Do they agree? {agrees}")
    lines.append("")

    lines.append("## Code")
    lines.append("")
    for link in entry["code_links"]:
        lines.append(f"- `{link}`")
    lines.append("")

    lines.append("## Tests")
    lines.append("")
    for link in entry["test_links"]:
        lines.append(f"- `{link}`")
    lines.append("")

    beh = entry["behaviour"]
    lines.append("## What the program does today and a test checks")
    lines.append("")
    for item in beh["tested"] or ["(none recorded)"]:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## In the program but no test checks it")
    lines.append("")
    for item in beh["committed_untested"] or ["(none recorded)"]:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Planned, not built")
    lines.append("")
    for item in beh["planned"] or ["(none recorded)"]:
        lines.append(f"- {item}")
    lines.append("")

    at = entry["automated_tests"]
    lines.append("## Automated test result")
    lines.append("")
    lines.append(f"- Status: {at['status']}")
    lines.append(f"- Commit tested: `{at['tested_commit']}`")
    lines.append(f"- Date tested: {at['tested_on']}")
    lines.append(f"- Command: `{at['command']}`")
    lines.append(f"- Counts: {at['counts']}")
    lines.append(f"- Evidence: [run log]({_evidence_rel(at, True)})")
    lines.append(f"- Rule file digest tested: `{at['tested_rule_file_sha256']}`")
    lines.append("- Test files tested:")
    for rel, digest in at["tested_test_file_sha256s"].items():
        lines.append(f"  - `{rel}` (`{digest}`)")
    lines.append(f"- {at['note']}")
    lines.append("")

    lines.append("## Gaps")
    lines.append("")
    for item in entry["gaps"]:
        lines.append(f"- {item}")
    lines.append("")

    hr = entry["human_review"]
    lines.append("## Human review")
    lines.append("")
    lines.append(f"- Current verdict: {hr['verdict']}")
    lines.append(f"- Reviewer name: {hr['reviewer_name'] or '-'}")
    lines.append(f"- Reviewer role: {hr['reviewer_role'] or '-'}")
    lines.append(f"- Review date: {hr['review_date'] or '-'}")
    rev = hr["reviewed_revision"] if hr["reviewed_revision"] is not None else "-"
    lines.append(f"- Revision reviewed: {rev}")
    lines.append(f"- Conditions reviewed: {hr['reviewed_conditions'] or '-'}")
    lines.append(f"- Comments: {hr['comments'] or '-'}")
    lines.append(
        "- The verdict shown above is derived from the reviewer's recorded decision and whether "
        "that decision still matches the current rule file, law captures and revision. A verdict "
        "is a named human reviewer's own answer; agent reviews are never recorded here."
    )
    if hr["decision"] is not None and hr["applies_to_current"] is False:
        lines.append("")
        lines.append(
            f"Earlier decision: {hr['decision']}, given by {hr['reviewer_name']} on "
            f"{hr['review_date']} for revision {hr['reviewed_revision']}; it does not apply to the "
            "current version."
        )
    lines.append("")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# HISTORY.md - the append-only history, oldest first
# --------------------------------------------------------------------------
def render_history_md(register: dict) -> str:
    lines: list[str] = []
    lines.append("# Zoning-rule review register - history")
    lines.append("")
    lines.append(GENERATED_BANNER)
    lines.append("")
    lines.append(
        "Events are only ever added, oldest first. A change to a rule's interpretation, "
        "applicability or implementation adds a new revision, keeps the old detail here, and sets "
        "the affected human verdicts to 'Needs re-review'. Nothing is removed or rewritten."
    )
    lines.append("")
    lines.append("| Seq | Date | Rule | Revision | Event | Summary | By |")
    lines.append("|---|---|---|---|---|---|---|")
    for ev in register["history"]:
        lines.append(
            f"| {ev['seq']} | {ev['date']} | `{ev['entry_id']}` | {ev['revision']} "
            f"| {_esc(ev['event'])} | {_esc(ev['summary'])} | {_esc(ev['by'])} |"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# write all rendered files
# --------------------------------------------------------------------------
def write_all(register: dict | None = None) -> list[pathlib.Path]:
    register = register or load_register()
    written: list[pathlib.Path] = []
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    RULES_MD_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "REGISTER.md").write_text(render_register_md(register))
    written.append(DOCS_DIR / "REGISTER.md")
    (DOCS_DIR / "HISTORY.md").write_text(render_history_md(register))
    written.append(DOCS_DIR / "HISTORY.md")
    wanted = set()
    for entry in register["entries"]:
        path = RULES_MD_DIR / f"{entry['rule_id']}.md"
        path.write_text(render_detail_md(entry))
        written.append(path)
        wanted.add(path.name)
    # remove any orphan detail page so --write leaves a clean, current tree.
    for existing in RULES_MD_DIR.glob("*.md"):
        if existing.name not in wanted:
            existing.unlink()
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render or check the zoning-rule review register")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="render the Markdown from the JSON")
    group.add_argument("--check", action="store_true", help="validate; exit non-zero on any issue")
    args = parser.parse_args(argv)

    if args.write:
        written = write_all()
        print(f"rendered {len(written)} file(s) under {DOCS_DIR}")
        return 0

    # --check: delegate to the stdlib checker (imported lazily to avoid a cycle).
    from . import check_review_register as checker

    errors = checker.validate(load_register())
    if errors:
        print(f"register check FAILED with {len(errors)} issue(s):")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("register check PASSED (no issues)")
    return 0


if __name__ == "__main__":
    # Allow running as a script (python render_review_register.py --check) by
    # falling back to an absolute import when there is no package context.
    if __package__ in (None, ""):
        sys.path.insert(0, str(HERE.parent))
        import review_register.render_review_register as _m  # type: ignore

        raise SystemExit(_m.main())
    raise SystemExit(main())
