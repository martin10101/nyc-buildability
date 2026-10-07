#!/usr/bin/env python3
"""Deterministic renderer + checker CLI for the R6B reference cases (M4-T024).

Reads each authored case data file under ``docs/reference-cases/R6B/cases/`` and
renders one plain-English page per case under ``docs/reference-cases/R6B/`` that a
person can follow with the law text and a calculator. The output is a pure
function of the JSON: running it twice over the same data produces a
byte-identical page. It performs no rule math beyond the reference-case
arithmetic engine, no network I/O and no AI call, and it imports nothing from the
rule or scenario engine. The hand-written ``README.md`` and the ``provenance/``
returns are never rendered or overwritten.

Usage (stdlib only, run from anywhere)::

    python r6b_reference_cases_render.py --write   # (re)render the case pages
    python r6b_reference_cases_render.py --check    # validate; non-zero on any issue
"""
from __future__ import annotations

import argparse
import pathlib
import sys
from decimal import ROUND_DOWN, Decimal

_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import r6b_reference_cases_lib as lib  # noqa: E402

GENERATED_BANNER = (
    "GENERATED FILE - do not edit by hand. Produced by "
    "`services/api/tests/rules/reference_cases/r6b_reference_cases_render.py` from "
    "`cases/<case>.json`; edit the data file and re-render. See `README.md`."
)
OPERATION_SYMBOL = {
    "multiply": "x", "subtract": "-", "divide": "/", "hypotenuse": "hypotenuse",
}


# --------------------------------------------------------------------------
# small formatting helpers
# --------------------------------------------------------------------------
def _num(value) -> str:
    """A number with thousands separators; an integral value drops its decimals."""
    dec = Decimal(str(value))
    if dec == dec.to_integral_value():
        return f"{int(dec):,}"
    return f"{dec:,}"


def _fmt_num_str(text: str) -> str:
    """An authored numeric string, with thousands separators and its decimals kept
    as written (so a law ratio '2.00' and an exact '100.00' render unchanged)."""
    negative = text.startswith("-")
    body = text[1:] if negative else text
    if "." in body:
        whole, frac = body.split(".", 1)
        out = f"{int(whole):,}.{frac}"
    else:
        out = f"{int(body):,}"
    return ("-" + out) if negative else out


def _scalar(value) -> str:
    """Render a scalar value: an authored numeric string keeps its decimals, a JSON
    number uses :func:`_num`, prose is shown as written."""
    if lib.is_numeric_value(value):
        return _fmt_num_str(value) if isinstance(value, str) else _num(value)
    return str(value)


def _value_text(value, unit: str) -> str:
    if value is None:
        return "not known"
    return f"{_scalar(value)} {unit}".strip()


def _operand_text(operand: dict) -> str:
    return f"{_scalar(operand['value'])} ({operand['name']})"


def _step_text(step: dict) -> str:
    operands = step["operands"]
    result = step["result"]
    result_shown = _scalar(result)
    if step["operation"] == "hypotenuse":
        a, b = (_operand_text(o) for o in operands)
        return f"{step['label']}: the square root of {a} squared plus {b} squared = {result_shown}"
    if step["operation"] == "divide" and step["rounding"] == "dwelling_unit_three_quarters":
        a, b = operands
        quotient = lib.raw_quotient(step)
        truncated = quotient.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        ellipsis = "..." if quotient != truncated else ""
        whole = int(quotient)
        rounded_up = int(Decimal(str(result))) > whole
        rule = ("a fraction of three-quarters or more counts as one dwelling unit"
                if rounded_up else "a fraction below three-quarters is dropped")
        left, right = _operand_text(a), _operand_text(b)
        return (f"{step['label']}: {left} / {right} = {truncated}{ellipsis}; "
                f"{rule} -> {result_shown}")
    symbol = OPERATION_SYMBOL[step["operation"]]
    joined = f" {symbol} ".join(_operand_text(o) for o in operands)
    tail = ""
    if step["rounding"] == "round_half_up_2dp":
        tail = " (rounded to two decimal places)"
    return f"{step['label']}: {joined} = {result_shown}{tail}"


# --------------------------------------------------------------------------
# page rendering
# --------------------------------------------------------------------------
def render_page(data: dict) -> str:
    lines: list[str] = []
    lines.append(f"# {data['title']}")
    lines.append("")
    lines.append(GENERATED_BANNER)
    lines.append("")
    lines.append(f"Work order table: {data['work_order_table']}.")
    lines.append("")
    lines.append(data["summary"])
    lines.append("")
    lines.append("## What this case is worth")
    lines.append("")
    lines.append(data["what_it_is_worth"])
    lines.append("")
    lines.append(f"- Prepared by: {data['prepared_by']}")
    lines.append(f"- Checked by: {data['checked_by']}")
    lines.append("")

    lines.append("## The facts this case uses")
    lines.append("")
    lines.append("| Fact | Value | Where it comes from |")
    lines.append("|---|---|---|")
    for fact in data["facts"]:
        lines.append(f"| {_esc(fact['name'])} | {_esc(fact['value'])} | {_esc(fact['source'])} |")
    lines.append("")

    lines.append("## Rows")
    lines.append("")
    for row in data["rows"]:
        lines.extend(_render_row(row))

    lines.append("## What this case does not establish")
    lines.append("")
    for item in data["what_it_does_not_establish"]:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Sources")
    lines.append("")
    for item in data["sources"]:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Change log")
    lines.append("")
    lines.append("| Date | Change | By |")
    lines.append("|---|---|---|")
    for entry in data["change_log"]:
        lines.append(f"| {entry['date']} | {_esc(entry['summary'])} | {_esc(entry['by'])} |")
    lines.append("")
    return "\n".join(lines) + "\n"


def _render_row(row: dict) -> list[str]:
    lines: list[str] = []
    lines.append(f"### {row['row_id']} - {row['quantity']}")
    lines.append("")

    lines.append("Facts used:")
    lines.append("")
    if row["facts_used"]:
        for fact in row["facts_used"]:
            lines.append(f"- {fact['name']} = {fact['value']} (source: {fact['source']})")
    else:
        lines.append("- none (this row rests on the law text alone)")
    lines.append("")

    lines.append("Law relied on:")
    lines.append("")
    for cite in row["citations"]:
        lines.extend(_render_citation(cite))
    if not row["citations"]:
        lines.append("- none cited")
    lines.append("")

    lines.append(f"Why the rule applies: {row['why_applies']}")
    lines.append("")

    if row["arithmetic"]:
        lines.append("Working, step by step:")
        lines.append("")
        for step in row["arithmetic"]:
            lines.append(f"- {_step_text(step)}")
        lines.append("")

    exp = row["expected"]
    if exp["kind"] == "not_known":
        lines.append(f"Expected value: not known. {exp['reason']}")
    else:
        lines.append(f"Expected value: {_value_text(exp['value'], exp['unit'])}")
    lines.append("")
    lines.append(f"Where this stands in the independent reading: {row['source_reference']}")
    lines.append("")
    lines.append(f"What this row does not establish: {row['does_not_establish']}")
    lines.append("")
    superseded = row.get("superseded_by")
    if superseded:
        targets = ", ".join(superseded)
        lines.append(
            f"Superseded by: {targets} (kept as the record of what the earlier readers could "
            "settle; the current answer is in the named row(s))."
        )
        lines.append("")
    return lines


def _render_citation(cite: dict) -> list[str]:
    lines: list[str] = []
    quote = cite["quote"]
    if cite["kind"] == "captured":
        lines.append(f"- ZR {cite['section']} ({cite['title']}) - captured.")
        lines.append(
            f"  - Capture: snapshot `{cite['snapshot_id']}`, file `{cite['snapshot_file']}`."
        )
        lines.append(f"  - Content digest: `{cite['content_digest']}`.")
        lines.append(f"  - Official page: {cite['official_url']}.")
        lines.append(f"  - Quoted: \"{quote}\"")
        if cite["table_assertion"]:
            assertion = cite["table_assertion"]
            fields = "; ".join(f"{k} = {v}" for k, v in assertion["fields"].items())
            lines.append(
                f"  - From the captured table, district {assertion['district']}: {fields}."
            )
    else:
        lines.append(
            f"- ZR {cite['section']} ({cite['title']}) - NOT captured. {cite['status_note']} "
            f"Read on the official page {cite['official_url']} on {cite['date_read']}."
        )
        lines.append(f"  - Read there: \"{quote}\"")
    return lines


def _esc(text) -> str:
    return str(text).replace("|", "\\|")


# --------------------------------------------------------------------------
# write / check
# --------------------------------------------------------------------------
def write_all() -> list[pathlib.Path]:
    written: list[pathlib.Path] = []
    for case_id in lib.CASE_IDS:
        page = lib.page_path(case_id)
        page.write_text(render_page(lib.load_case(case_id)))
        written.append(page)
    return written


def rendered_errors() -> list[str]:
    errs: list[str] = []
    for case_id in lib.CASE_IDS:
        page = lib.page_path(case_id)
        produced = render_page(lib.load_case(case_id))
        if not page.is_file():
            errs.append(f"rendered page missing: {case_id}.md (run --write)")
        elif page.read_text() != produced:
            errs.append(f"rendered page is stale: {case_id}.md (run --write)")
    return errs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render or check the R6B reference cases")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="render the case pages from the JSON")
    group.add_argument("--check", action="store_true", help="validate; exit non-zero on any issue")
    args = parser.parse_args(argv)

    if args.write:
        written = write_all()
        print(f"rendered {len(written)} case page(s) under {lib.DOCS_DIR}")
        return 0

    import r6b_reference_cases_check as checker  # noqa: E402

    errors = checker.validate_all() + rendered_errors()
    if errors:
        print(f"reference-case check FAILED with {len(errors)} issue(s):")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("reference-case check PASSED (no issues)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
