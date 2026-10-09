#!/usr/bin/env python3
"""Deterministic renderer for the A-01 rule-coverage matrix (plan M1-03).

Reads ``coverage_matrix.json`` (the authored, machine-readable matrix) and
writes ``COVERAGE_MATRIX.md`` (a human-readable rendering). The output is a pure
function of the JSON: running it twice over the same JSON produces byte-identical
Markdown. It performs no rule math, no network I/O and no AI call; it only
re-presents the committed data. ``tests/rules/test_coverage_matrix.py`` asserts
the committed Markdown is byte-identical to this renderer's output.

Run ``python render_coverage_matrix.py`` from anywhere; both files live next to
this module.
"""
from __future__ import annotations

import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
MATRIX_JSON = HERE / "coverage_matrix.json"
MATRIX_MD = HERE / "COVERAGE_MATRIX.md"

# Short grid codes (documented in the rendered legend).
STATUS_CODE = {
    "implemented_draft": "ID",
    "not_implemented": "—",
    "not_applicable": "NA",
    "needs_reviewer": "NR",
}
OUTPUT_CODE = {
    "far": "FAR",
    "heights": "HGT",
    "setbacks": "SBK",
    "yards": "YRD",
    "coverage": "COV",
    "units": "UNI",
}


def load_matrix() -> dict:
    return json.loads(MATRIX_JSON.read_text())


def _cell(matrix: dict, district: str, column: str) -> dict:
    for row in matrix["districts"]:
        if row["district"] == district:
            return row["columns"][column]
    raise KeyError(district)


def _column_labels(matrix: dict) -> list[tuple[str, str]]:
    """Return (column_key, short_code) in canonical column order."""
    labels: list[tuple[str, str]] = []
    for col in matrix["output_columns"]:
        labels.append((col, OUTPUT_CODE[col]))
    for i, addon in enumerate(matrix["add_on_columns"], start=1):
        labels.append((f"add_on:{addon['key']}", f"AO{i}"))
    return labels


def _md_escape(text: str) -> str:
    return text.replace("|", "\\|")


def render_markdown(matrix: dict) -> str:
    lines: list[str] = []
    out_cols = matrix["output_columns"]
    add_ons = matrix["add_on_columns"]
    labels = _column_labels(matrix)
    column_order = matrix["column_order"]

    lines.append(f"# {matrix['title']}")
    lines.append("")
    lines.append(
        "GENERATED FILE — do not edit by hand. Produced by "
        "`render_coverage_matrix.py` from `coverage_matrix.json`; edit the JSON "
        "and re-render."
    )
    lines.append("")
    lines.append(f"- Plan: {matrix['plan_ref']}")
    lines.append(f"- Queue: {matrix['queue_ref']}")
    lines.append(f"- Directives: {', '.join(matrix['directive_refs'])}")
    lines.append(f"- Lane: {matrix['lane']}")
    lines.append("")
    lines.append(f"> {matrix['review_state_note']}")
    lines.append("")

    # ---- district list source ----
    ls = matrix["list_source"]
    lines.append("## District list source")
    lines.append("")
    lines.append(ls["method"])
    lines.append("")
    lines.append("| ZR section | Section title | Table caption | Covers | Districts | Content digest (sha256) |")
    lines.append("|---|---|---|---|---:|---|")
    for s in ls["sources"]:
        lines.append(
            f"| {s['zr_section']} | {_md_escape(s['section_title'])} | "
            f"{_md_escape(s['table_caption'])} | {s['covers']} | "
            f"{s['district_count']} | `{s['content_digest_sha256']}` |"
        )
    lines.append(f"| | | | **total** | **{ls['total_district_count']}** | |")
    lines.append("")
    for note in ls["notes"]:
        lines.append(f"- {note}")
    lines.append("")

    # ---- legends ----
    lines.append("## Legend")
    lines.append("")
    lines.append("### Status")
    lines.append("")
    lines.append("| Code | Status | Meaning |")
    lines.append("|---|---|---|")
    for status, code in STATUS_CODE.items():
        lines.append(f"| `{code}` | {status} | {matrix['status_vocab'][status]} |")
    lines.append("")
    lines.append("### Output columns")
    lines.append("")
    lines.append("| Code | Output |")
    lines.append("|---|---|")
    for col in out_cols:
        lines.append(f"| `{OUTPUT_CODE[col]}` | {col} |")
    lines.append("")
    lines.append("### Add-on columns (plan §6)")
    lines.append("")
    lines.append("| Code | Add-on | Group | Type |")
    lines.append("|---|---|---|---|")
    for i, addon in enumerate(add_ons, start=1):
        lines.append(
            f"| `AO{i}` | {_md_escape(addon['name'])} | {addon['group']} | "
            f"{_md_escape(addon['type'])} |"
        )
    lines.append("")
    lines.append("### Street-width source")
    lines.append("")
    lines.append("| Value | Meaning |")
    lines.append("|---|---|")
    for value, meaning in matrix["street_width_source_vocab"].items():
        lines.append(f"| `{value}` | {meaning} |")
    lines.append("")

    # ---- per-status / per-column summary ----
    lines.append("## Summary")
    lines.append("")
    lines.append("| Column | ID | — | NA | NR |")
    lines.append("|---|---:|---:|---:|---:|")
    totals = {k: 0 for k in STATUS_CODE}
    for col_key, code in labels:
        per = {k: 0 for k in STATUS_CODE}
        for row in matrix["districts"]:
            per[row["columns"][col_key]["status"]] += 1
            totals[row["columns"][col_key]["status"]] += 1
        lines.append(
            f"| `{code}` | {per['implemented_draft']} | {per['not_implemented']} | "
            f"{per['not_applicable']} | {per['needs_reviewer']} |"
        )
    lines.append(
        f"| **total** | **{totals['implemented_draft']}** | "
        f"**{totals['not_implemented']}** | **{totals['not_applicable']}** | "
        f"**{totals['needs_reviewer']}** |"
    )
    lines.append("")

    # ---- the grid ----
    lines.append("## Coverage grid (district x column)")
    lines.append("")
    header = "| District | " + " | ".join(code for _, code in labels) + " |"
    sep = "|---|" + "|".join([":-:"] * len(labels)) + "|"
    lines.append(header)
    lines.append(sep)
    for row in matrix["districts"]:
        cells = [STATUS_CODE[row["columns"][k]["status"]] for k, _ in labels]
        lines.append(f"| {row['district']} | " + " | ".join(cells) + " |")
    lines.append("")

    # ---- detail: implemented_draft + needs_reviewer + not_applicable ----
    lines.append("## Implemented (draft) cells")
    lines.append("")
    lines.append(
        "Every rule below is status `needs_review`; `implemented_draft` is the "
        "ceiling (D-090-R010)."
    )
    lines.append("")
    lines.append("| District | Column | Rule ids | Tests | ZR sections | Street-width source |")
    lines.append("|---|---|---|---|---|---|")
    code_by_key = dict(labels)
    for row in matrix["districts"]:
        for col_key, _ in labels:
            cell = row["columns"][col_key]
            if cell["status"] != "implemented_draft":
                continue
            rids = ", ".join(f"`{r}`" for r in cell["rule_ids"])
            tests = "<br>".join(_md_escape(t) for t in cell["tests"])
            secs = ", ".join(cell["zr_sections"])
            sws = cell["street_width_source"] or ""
            lines.append(
                f"| {row['district']} | `{code_by_key[col_key]}` | {rids} | "
                f"{tests} | {secs} | `{sws}` |"
            )
    lines.append("")

    lines.append("## Needs-reviewer cells")
    lines.append("")
    lines.append("| District | Column | Reason |")
    lines.append("|---|---|---|")
    for row in matrix["districts"]:
        for col_key, _ in labels:
            cell = row["columns"][col_key]
            if cell["status"] != "needs_reviewer":
                continue
            lines.append(
                f"| {row['district']} | `{code_by_key[col_key]}` | "
                f"{_md_escape(cell['notes'])} |"
            )
    lines.append("")

    lines.append("## Not-applicable cells")
    lines.append("")
    na_cols = sorted(
        {
            code_by_key[col_key]
            for row in matrix["districts"]
            for col_key, _ in labels
            if row["columns"][col_key]["status"] == "not_applicable"
        }
    )
    na_count = sum(
        1
        for row in matrix["districts"]
        for col_key, _ in labels
        if row["columns"][col_key]["status"] == "not_applicable"
    )
    lines.append(
        f"{na_count} cell(s) across column(s) {', '.join(f'`{c}`' for c in na_cols)}. "
        "See each cell's `notes` in `coverage_matrix.json` for the cited basis."
    )
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> None:
    matrix = load_matrix()
    MATRIX_MD.write_text(render_markdown(matrix))


if __name__ == "__main__":
    main()
