#!/usr/bin/env python3
"""Markdown rendering for the review register's CALCULATION entries (M4-T038).

Split out of ``review_register_calculations.py`` (DB-211 c): the calculation detail pages, the
calculations table, the coverage-gaps section and the calculations-history section, plus the writer.
The output is a pure function of the register JSON (running it twice is byte-identical); it performs
no rule math, no network I/O and no AI call. Public names are re-exported from the old path.
"""
from __future__ import annotations

import pathlib

from . import render_review_register as render


def _calc_md_dir() -> pathlib.Path:
    """The calculation detail-page folder, read from the render module at call time so a test can
    point the renderer at a temp docs folder."""
    return render.DOCS_DIR / "calculations"


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

    def _row(r: dict) -> str:
        pr = (" (program result(s): " + ", ".join(r["program_results"]) + ")"
              if r["program_results"] else "")
        return f"- [{r['kind']}]{pr} {r['what']} - would be settled by: {r['would_settle']}"

    out += ["## Every disagreement and missing fact (and what would settle it)", "",
            "Disagreements:"]
    out += [_row(r) for r in cl["disagreements"]] or ["- (none recorded)"]
    out += ["", "Missing facts:"]
    out += [_row(r) for r in cl["missing_facts"]] or ["- (none recorded)"]
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
