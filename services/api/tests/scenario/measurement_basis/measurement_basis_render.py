#!/usr/bin/env python3
"""Deterministic renderer + checker CLI for the measurement-basis examples (M5-T126).

Reads each authored example data file under ``docs/measurement-basis/examples/`` and
renders one plain-English page per example that a person can follow with the law text
and a calculator. The output is a pure function of the JSON: running it twice over the
same data produces a byte-identical page. It performs no rule math beyond the
measurement-basis arithmetic engine, no network I/O and no AI call, and it imports
nothing from the rule or scenario engine. The hand-written ``MEASUREMENT_BASIS.md`` is
never rendered or overwritten.

Usage (stdlib only, run from anywhere)::

    python measurement_basis_render.py --write   # (re)render the example pages
    python measurement_basis_render.py --check    # validate; non-zero on any issue
"""
from __future__ import annotations

import argparse
import pathlib
import sys
from decimal import Decimal

_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import measurement_basis_lib as lib  # noqa: E402

GENERATED_BANNER = (
    "GENERATED FILE - do not edit by hand. Produced by "
    "`services/api/tests/scenario/measurement_basis/measurement_basis_render.py` from "
    "`<example>.json`; edit the data file and re-render. See `../MEASUREMENT_BASIS.md`."
)
ZONING_LABELS = {
    "count": "Counts in full",
    "exclude": "Excluded",
    "exclude_if_condition": "Excluded only if the stated condition is shown",
    "not_residential_portion": "Not part of the residential portion",
}
HPD_LABELS = {"count": "Counts (inside a dwelling unit)", "exclude": "Excluded"}


def _num(value) -> str:
    dec = Decimal(str(value))
    if dec == dec.to_integral_value():
        return f"{int(dec):,}"
    return f"{dec:,}"


def _esc(text) -> str:
    return str(text).replace("|", "\\|")


def _zoning_cell(comp: dict) -> str:
    z = comp["zoning"]
    label = ZONING_LABELS[z["treatment"]]
    bits = [f"{label} ({z['provision']})"]
    if str(z["condition"]).strip():
        shown = "shown" if z["condition_shown"] else "NOT shown -> the space counts"
        bits.append(f"condition: {z['condition']} [{shown}]")
    return "; ".join(bits)


def render_page(data: dict) -> str:
    lines: list[str] = []
    lines.append(f"# {data['title']}")
    lines.append("")
    lines.append(GENERATED_BANNER)
    lines.append("")
    lines.append(f"Mixed-use example: {'yes' if data['mixed_use'] else 'no'}.")
    lines.append("")
    lines.append(data["made_up_note"])
    lines.append("")
    lines.append(data["standing_label"])
    lines.append("")
    lines.append("## The building in this example")
    lines.append("")
    lines.append(data["building"])
    lines.append("")
    lines.append(data["assumptions_note"])
    lines.append("")
    lines.extend(_render_schedule(data))
    lines.extend(_render_law(data))
    lines.extend(_render_reconciliation(data))
    lines.extend(_render_legal_cap(data))
    lines.extend(_render_lists(data))
    return "\n".join(lines) + "\n"


def _render_schedule(data: dict) -> list[str]:
    lines = ["## One area schedule (measured from the layout)", ""]
    lines.append("| Component | Portion | Measured area (sq ft) | How measured | "
                 "Under zoning floor area | Under HPD dwelling-unit area |")
    lines.append("|---|---|---|---|---|---|")
    for comp in data["components"]:
        lines.append(
            f"| {_esc(comp['name'])} | {comp['portion']} | {_num(comp['measured_area'])} | "
            f"{_esc(comp['how_measured'])} | {_esc(_zoning_cell(comp))} | "
            f"{_esc(HPD_LABELS[comp['hpd']['treatment']] + ' - ' + comp['hpd']['reason'])} |"
        )
    lines.append("")
    lines.append("Each component appears once. The residential zoning floor area and the "
                 "HPD dwelling-unit area are summed from this one schedule, each on its own.")
    lines.append("")
    return lines


def _render_law(data: dict) -> list[str]:
    lines = ["## The law and guideline relied on", ""]
    seen: set[tuple] = set()
    for comp in data["components"]:
        for cite in comp["zoning"]["citations"] + comp["hpd"]["citations"]:
            key = (cite["kind"], cite.get("section", ""), cite["quote"][:40])
            if key in seen:
                continue
            seen.add(key)
            lines.extend(_render_citation(cite))
    lines.append("")
    return lines


def _render_citation(cite: dict) -> list[str]:
    lines: list[str] = []
    if cite["kind"] == "captured":
        lines.append(f"- ZR {cite['section']} ({cite['title']}) - captured law.")
        lines.append(f"  - Capture: snapshot `{cite['snapshot_id']}`, "
                     f"digest `{cite['content_digest']}`.")
        lines.append(f"  - Official page: {cite['official_url']} "
                     f"(last amended {cite['last_amended']}).")
        lines.append(f"  - Quoted: \"{cite['quote']}\"")
    else:
        lines.append(f"- {cite['title']} - guideline, not law. {cite['status_note']}")
        lines.append(f"  - Source: {cite['official_url']} (edition {cite['edition']}, "
                     f"read {cite['date_read']}).")
        lines.append(f"  - Quoted: \"{cite['quote']}\"")
    return lines


def _render_reconciliation(data: dict) -> list[str]:
    recon = data["reconciliation"]
    lines = ["## The two areas, worked out separately, then reconciled", ""]
    lines.append(f"- Residential zoning floor area (sum of what counts under zoning): "
                 f"{_num(recon['residential_zoning_floor_area'])} sq ft.")
    lines.append(f"- Total HPD dwelling-unit area (sum of what counts under HPD): "
                 f"{_num(recon['total_hpd_dwelling_unit_area'])} sq ft.")
    lines.append("")
    lines.append("Reconciliation - every square foot of the difference, by component "
                 "(nothing is deducted twice):")
    lines.append("")
    lines.append("| From | Component | Amount (sq ft) |")
    lines.append("|---|---|---|")
    lines.append(f"| Residential zoning floor area | (start) | "
                 f"{_num(recon['residential_zoning_floor_area'])} |")
    for step in recon["bridge"]:
        sign = "-" if step["direction"] == "subtract" else "+"
        lines.append(f"| {sign} counts for zoning but not HPD | {_esc(step['component_id'])} | "
                     f"{sign}{_num(step['area'])} |")
    lines.append(f"| = Total HPD dwelling-unit area | (end) | "
                 f"{_num(recon['total_hpd_dwelling_unit_area'])} |")
    lines.append("")
    ratio = recon["ratio"]
    lines.append(f"Ratio for this example = total HPD-measured dwelling-unit area "
                 f"({_num(ratio['numerator'])}) / residential zoning floor area "
                 f"({_num(ratio['denominator'])}) = {ratio['value']}.")
    lines.append("")
    lines.append("This ratio belongs to THIS made-up example only. Two or three examples "
                 "cannot establish a typical figure; no percentage is validated here.")
    lines.append("")
    return lines


def _render_legal_cap(data: dict) -> list[str]:
    cap = data["legal_unit_cap"]
    lines = ["## The legal unit cap (a separate figure)", ""]
    lines.append(f"- Maximum residential floor area allowed: "
                 f"{_num(cap['max_residential_floor_area'])} sq ft ({cap['provision']}).")
    lines.append(f"- Divided by the dwelling-unit factor {cap['factor']}: "
                 f"{cap['raw_quotient']} -> {cap['units_cap']} dwelling units (ZR 23-52 "
                 f"rounding).")
    lines.append(f"- {cap['note']}")
    lines.append("")
    return lines


def _render_lists(data: dict) -> list[str]:
    lines: list[str] = []
    lines.append("## What this example shows")
    lines.append("")
    for item in data["what_it_shows"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## What this example does not show")
    lines.append("")
    for item in data["what_it_does_not_show"]:
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
    return lines


def write_all() -> list[pathlib.Path]:
    written: list[pathlib.Path] = []
    for example_id in lib.EXAMPLE_IDS:
        page = lib.page_path(example_id)
        page.write_text(render_page(lib.load_example(example_id)))
        written.append(page)
    return written


def rendered_errors() -> list[str]:
    errs: list[str] = []
    for example_id in lib.EXAMPLE_IDS:
        page = lib.page_path(example_id)
        produced = render_page(lib.load_example(example_id))
        if not page.is_file():
            errs.append(f"rendered page missing: {example_id}.md (run --write)")
        elif page.read_text() != produced:
            errs.append(f"rendered page is stale: {example_id}.md (run --write)")
    return errs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render or check the measurement-basis examples")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="render the example pages")
    group.add_argument("--check", action="store_true", help="validate; non-zero on any issue")
    args = parser.parse_args(argv)

    if args.write:
        written = write_all()
        print(f"rendered {len(written)} example page(s) under {lib.EXAMPLES_DIR}")
        return 0

    import measurement_basis_check as checker  # noqa: E402

    errors = checker.validate_all() + rendered_errors()
    if errors:
        print(f"measurement-basis check FAILED with {len(errors)} issue(s):")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("measurement-basis check PASSED (no issues)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
