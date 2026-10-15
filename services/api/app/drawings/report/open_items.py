"""Evidence-appendix reading for the merged appendix (M5-T169).

This module holds the appendix-specific reading that would otherwise swell
:mod:`.readers` past its responsibility: the five-field issue records, the
``input_facts`` rows with the nine closed bases' plain words (G-10), the worked
arithmetic read from the document's own values, and each result's review-register
entry and review state (R025/R026/R027). :mod:`.readers` stays the general
document reader; this module turns its views into the appendix's records.

No figure is typed here (ruling X7): every number comes from the document and is
only formatted. No law is computed; the register is read, never written
(G-11/M5-T172 own it).
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path

from . import formatting, readers, sources

__all__ = [
    "appendix_issue_records",
    "basis_label",
    "input_fact_rows",
    "register_rule_rows",
    "worked_arithmetic",
]

# The nine closed measurement bases in plain words (design contract, change 2026-10-11;
# G-10). Keyed by the `quantity_basis` enum. A GIS fact is "city map (GIS measurement)"
# whether it is an outline or a street-centre-line width - the SOURCE TITLE tells them
# apart - so a street width is never labelled "city map outline" and no GIS outline is
# ever called a "tax map"/"tax-map outline" (S4/G-10).
_NINE_BASES = {
    "law": "zoning law",
    "deed": "deed",
    "survey": "survey",
    "printed_tax_map": "printed tax map",
    "approved_plan": "approved plan",
    "filing_attribute": "building filing",
    "administrative_record": "city record",
    "gis": "city map (GIS measurement)",
    "derived": "worked from other values",
}


def basis_label(basis: object) -> str:
    """The plain word for one of the nine closed bases; an unknown basis reads
    "recorded value" so no raw enum token reaches the reader (never "tax map")."""
    return _NINE_BASES.get(str(basis or ""), "recorded value")


# Readable names for the document's input-fact keys. A street-width key carries the
# street name after the colon; it reads "Mapped street width - <name>" (never
# "city map outline", S4). An unknown key is humanised from its words.
_INPUT_FACT_NAMES = {
    "recorded_lot_area": "Recorded lot area",
    "lot_outline_area": "Lot outline area (city map)",
}


def _input_fact_name(key: object) -> str:
    text = str(key or "")
    if text.startswith("mapped_street_width:"):
        return f"Mapped street width - {text.split(':', 1)[1]}"
    if text in _INPUT_FACT_NAMES:
        return _INPUT_FACT_NAMES[text]
    cleaned = text.replace("_", " ").strip()
    return cleaned[:1].upper() + cleaned[1:] if cleaned else "Recorded value"


def _source_line(fact: Mapping) -> str:
    """The fact's source title and date in plain words: "<title> (as of <date>)"."""
    title = str(fact.get("source_title") or "").strip()
    date = str(fact.get("source_date") or "").strip()
    if title and date:
        return f"{title} (as of {date})"
    return title or "Recorded city data"


def input_fact_rows(results: Mapping) -> list[dict]:
    """One row per 1.5.0 ``input_fact``: a readable name, the formatted value with its
    unit, the plain-word basis (G-10) and the source title and date. Empty on a 1.4.0
    document (no block), so the appendix shows no input-facts table there (S15)."""
    rows: list[dict] = []
    for fact in readers.input_facts(results):
        unit = {"sq_ft": "square_feet", "ft": "feet"}.get(str(fact.get("unit") or ""),
                                                          fact.get("unit"))
        rows.append(
            {
                "name": _input_fact_name(fact.get("key")),
                "value": formatting.format_measure(fact.get("value"), unit)
                or formatting.format_int_commas(fact.get("value")),
                "basis": basis_label(fact.get("basis")),
                "source": _source_line(fact),
            }
        )
    return rows


def _fact_value(results: Mapping, key: str):
    for fact in readers.input_facts(results):
        if fact.get("key") == key:
            return fact
    return None


# The arithmetic portion of the legal dwelling-unit-limit label (the document's own
# sentence) begins after the first colon: "20,150 / 680 = 29.63 (dwelling-unit factor
# 680 square feet per dwelling unit; ...)". We read the EQUATION (up to the parenthesis)
# and append the rounded whole value; the parenthetical factor explanation stays in the
# figures table only (R077: no explanation printed twice). We never retype the factor.
def _unit_limit_expression(results: Mapping) -> str | None:
    row = readers.named_value(readers.answer_block(results, "floor_area_allowance"),
                              "legal_unit_limit_standard")
    if row is None:
        return None
    label = str(row.get("label") or "")
    tail = label.split(":", 1)[1].strip() if ":" in label else ""
    equation = tail.split("(", 1)[0].strip() if tail else ""
    if not equation:
        return None
    whole = formatting.format_int_commas(row.get("value"))
    return f"{equation} → {whole}" if whole is not None else equation


def worked_arithmetic(results: Mapping) -> list[dict]:
    """The worked arithmetic, each figure READ from the document and each input NAMING
    ITS BASIS (R023/R026). Two derivations when the document carries them: the floor-area
    allowance (recorded lot area, city record x FAR, zoning law) and the legal
    dwelling-unit limit (floor area / the dwelling-unit factor, zoning law). No single
    figure mixes two bases (S5): the floor area uses the recorded lot area
    (administrative_record), never the city-map outline (gis)."""
    rows: list[dict] = []
    lot = _fact_value(results, "recorded_lot_area")
    fa = readers.answer_block(results, "floor_area_allowance")
    far = readers.named_value(fa, "max_residential_far")
    area = readers.named_value(fa, "max_residential_floor_area")
    if lot is not None and far is not None and area is not None:
        lot_text = formatting.format_measure(lot.get("value"), "square_feet")
        rows.append(
            {
                "name": "Maximum residential floor area",
                "expression": (
                    f"{lot_text} (recorded lot area, {basis_label(lot.get('basis'))}) "
                    f"× {formatting.format_ratio(far.get('value'))} (FAR, zoning law) "
                    f"= {area.get('display')}"
                ),
            }
        )
    unit_expr = _unit_limit_expression(results)
    if unit_expr is not None:
        rows.append(
            {
                "name": "Legal dwelling-unit limit (standard residences)",
                "expression": f"{unit_expr}, under zoning law",
            }
        )
    return rows


# ------------------------------------------------------------ five-field issue records
# Categories whose resolution needs recorded SITE documents the owner supplies, kept
# apart from the work the program must do (R025). Everything else is program work.
_SITE_DOCUMENT_CATEGORIES = {"zoning_lot", "lot_area"}
_ROLE_SITE = "Owner or surveyor"
_ROLE_PROGRAM = "This program"
_EVIDENCE_REFERENCE = {
    "zoning_lot": "City Register (page 1)",
    "lot_area": "Survey or deed",
}
_ZR_RE = re.compile(r"ZR \d{1,3}-\d{1,4}(?:\([a-z0-9]+\))*")
# A material document reason is kept beneath the row (R025) ONLY where it adds unique
# content not shown on the affected result or in the shared assumptions: the coverage
# by-portion law and the per-program legal-limit gaps. The zoning-lot, lot-area and
# rear-yard reasons already appear on page 1 / page 3 / the shared assumptions, so
# repeating them in the appendix is the repetition R077 removes.
_DETAIL_CATEGORIES = {"coverage", "legal_unit_limit"}
# R054: the honest "A check not yet made ..." next action is printed at most ONCE; a
# second not-checked item points back to it instead of repeating the sentence.
_CHECK_WORD = readers._CHECK_WORD
_CHECK_WORD_AGAIN = "A check of the same kind (see the item above)."


def _evidence_reference(item: Mapping) -> str:
    category = item.get("category")
    if category in _EVIDENCE_REFERENCE:
        return _EVIDENCE_REFERENCE[category]
    found = list(dict.fromkeys(_ZR_RE.findall(
        f"{item.get('effect') or ''} {item.get('reason') or ''}")))
    return "; ".join(found) if found else "This report's own calculations"


def appendix_issue_records(results: Mapping) -> list[dict]:
    """The open items as five-field issue records in the appendix (R025): issue,
    consequence, next action, responsible role, evidence reference. The number is the
    reader's open-item number (so ``id="issue-<n>"`` stays byte-stable and the page-1
    and page-3 "see item N" links resolve, R060). Missing site documents carry the
    owner/surveyor role; program work carries the program's; the honest "A check not
    yet made ..." next action prints at most once (R054)."""
    records: list[dict] = []
    check_word_used = False
    for item in readers.open_items(results):
        category = item.get("category")
        next_action = item.get("resolves") or "Not stated"
        if next_action == _CHECK_WORD:
            if check_word_used:
                next_action = _CHECK_WORD_AGAIN
            check_word_used = True
        # The material document reason is preserved beneath the row when it adds unique
        # information beyond the consequence/title AND is not shown elsewhere (R025 keeps
        # material limitations; R077 removes repeats) - see _DETAIL_CATEGORIES.
        reason = item.get("reason")
        detail = (reason if reason and category in _DETAIL_CATEGORIES
                  and reason not in (item["effect"], item["title"]) else None)
        records.append(
            {
                "number": item["number"],
                "issue": item["title"],
                "consequence": item["effect"],
                "next_action": next_action,
                "responsible_role": _ROLE_SITE if category in _SITE_DOCUMENT_CATEGORIES
                else _ROLE_PROGRAM,
                "evidence_reference": _evidence_reference(item),
                "detail": detail,
            }
        )
    return records


# ------------------------------------------------------------ review-register linkage
_REGISTER_PATH = (
    Path(__file__).resolve().parents[2] / "rules" / "review_register" / "register.json"
)


def _register_index() -> dict:
    """{rule_id: entry} from the review register, read defensively and cached. An
    unreadable or malformed register reads as empty, so the appendix still renders
    (the rule then shows no register state)."""
    cached = getattr(_register_index, "_cache", None)
    if cached is not None:
        return cached
    index: dict = {}
    try:
        raw = _REGISTER_PATH.read_bytes().replace(b"\r\n", b"\n")
        data = json.loads(raw.decode("utf-8"))
        for entry in data.get("entries", []) if isinstance(data, dict) else []:
            if isinstance(entry, Mapping) and entry.get("rule_id"):
                index[str(entry["rule_id"])] = entry
    except (OSError, ValueError, UnicodeError):
        index = {}
    _register_index._cache = index  # type: ignore[attr-defined]
    return index


def register_rule_rows(results: Mapping) -> list[dict]:
    """Each ``rule_versions`` entry mapped to its EXISTING review-register entry and
    review state (R027): the SHORT readable rule title (never the register's long
    title - the appendix stays within the word cap) and the register verdict (for
    example "Not reviewed"). The register is read, never written (G-11). A rule with no
    register entry shows "Not in the review register" so nothing is invented."""
    index = _register_index()
    rows: list[dict] = []
    for rule in readers.provenance(results).get("rule_versions", []):
        rule_id = str(rule.get("rule_id") or "")
        entry = index.get(rule_id)
        if isinstance(entry, Mapping):
            verdict = ((entry.get("human_review") or {}).get("verdict")
                       if isinstance(entry.get("human_review"), Mapping) else None)
            state = str(verdict or "Not reviewed")
        else:
            state = "Not in the review register"
        rows.append({"title": sources.readable_rule_title(rule_id), "review_state": state,
                     "status": sources.readable_rule_status(rule.get("status"))})
    return rows
