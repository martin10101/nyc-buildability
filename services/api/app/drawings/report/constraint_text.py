"""Short, structural effect texts for the report's open items (G-6 isolation).

These are the one-line "effect on the answer" phrases the open-items list shows for
a withheld or conditional constraint, moved out of :mod:`.readers` (task M5-T165)
so the document reader stays a general reader. Each text is keyed by the open-item
category and is authored here (it is NOT read from the document, which carries its
own long reason separately).

Every text keeps its 1.4.0 output UNCHANGED except two, corrected in M5-T165:

* ``lot_area`` names the GIS outline "city map outline" (never "tax-map outline";
  a GIS value is never called "tax map", D-094 R2/G-10).
* ``rear_yard`` is reworded as the design contract's OPEN CHECK (D-094 R037, R079;
  NB-03): it names the short-block provision ZR 23-344(b) and the adjoining-side-
  line provision ZR 23-344(c)(3) as not yet checked and draws NO conclusion. The
  earlier "not known beyond the corner area" wording is gone. The law link for
  23-344 is added by the page that shows the uncertainty, not spliced into the text.
"""

from __future__ import annotations

from collections.abc import Mapping

__all__ = [
    "PAGE3_DEFAULT_STATE",
    "PAGE3_FALLBACK_STATE",
    "REAR_YARD_LAW_SECTION",
    "REAR_YARD_OPEN_CHECK",
    "effect_for",
    "envelope_row",
    "envelope_rows",
    "has_results_rows",
    "rear_yard_checks",
    "rear_yard_combined",
]

# The constraint effect texts, by open-item category. Authored one-liners; the
# document's own long reason is carried separately by the open item.
_EFFECTS = {
    "lot_area": "The floor-area figures depend on it; the recorded area and the city map outline "
                "disagree.",
    "coverage": "The square-foot coverage figure is withheld.",
    "placement": "Where the building sits on the lot is not worked out.",
    "setback": "The setback above the base is not worked out.",
    "street_wall": "The street wall is not checked.",
    "parking": "Parking, loading and bicycle requirements are not checked.",
}

# The rear-yard open check (D-094 R037, R079; NB-03 revision 2). It states no
# conclusion and names the two provisions that have not been applied to this lot.
REAR_YARD_OPEN_CHECK = (
    "Whether a rear yard is required is not yet checked: the short-block rule ZR 23-344(b) and "
    "the adjoining-side-line rule ZR 23-344(c)(3) have not been applied to this lot."
)

# The single law section the rear-yard open check links to (its sub-paragraphs
# resolve to the same captured section page).
REAR_YARD_LAW_SECTION = "ZR 23-344"


def effect_for(category: str) -> str:
    """The short structural effect text for an open-item category. Returns the
    rear-yard OPEN CHECK for ``rear_yard`` and the fixed 1.4.0 text for every other
    constraint; an unknown category yields ``""`` (no invented text).

    This is the 1.4.0 open-item EFFECT text, read by :mod:`.readers` with the
    category alone (no document). It is UNCHANGED by the 1.5.0 reading below: the
    appendix open-item list and the page-1 uncertainty keep the open-check wording,
    which names both provisions and draws no conclusion (test_report_page_one
    pins ``effect_for("rear_yard") == REAR_YARD_OPEN_CHECK``)."""
    if category == "rear_yard":
        return REAR_YARD_OPEN_CHECK
    return _EFFECTS.get(category, "")


# --------------------------------------------------------------------------- #
# Reading the results contract 1.5.0 constraint rows (D-094 R037/R038/R079;
# task M5-T175). The report's page-3 "What constrains the design?" rows read the
# ENGINE's own rear-yard and envelope readings when the document carries them;
# a document with no 1.5.0 block falls back to the 1.4.0 output UNCHANGED.
# --------------------------------------------------------------------------- #

# The page-3 "State" column strings for a 1.4.0 document (moved here from
# page_site_context.py so the state text has one home). Each is the EXACT 1.4.0
# wording; when the document carries a 1.5.0 rear_yard / envelope block the row
# reads the engine's own text instead (``has_results_rows``). The fall-back must
# reproduce these byte-for-byte (S1).
PAGE3_FALLBACK_STATE = {"rear_yard": "Not known", "setback": "Not worked out yet"}
PAGE3_DEFAULT_STATE = "Not shown"


def rear_yard_combined(results: Mapping) -> Mapping | None:
    """The 1.5.0 combined rear-yard ROW (``state``, ``way``, ``conditions``,
    ``text``, ``zr_sections``), or ``None`` when the document carries no rear_yard
    block. It summarises the ZR 23-344 (a)/(b)/(c)(3) checks as one draft reading
    and carries NO number (a withheld or not_known row never carries one)."""
    block = results.get("rear_yard") if isinstance(results, Mapping) else None
    combined = block.get("combined") if isinstance(block, Mapping) else None
    return combined if isinstance(combined, Mapping) else None


def rear_yard_checks(results: Mapping) -> list[Mapping]:
    """The 1.5.0 rear-yard per-provision checks (each ``provision``, ``state``,
    ``text``, ``zr_sections`` and, for an applies/not_applicable check, its measured
    ``inputs``); empty when the document carries no rear_yard block."""
    block = results.get("rear_yard") if isinstance(results, Mapping) else None
    checks = block.get("checks") if isinstance(block, Mapping) else None
    return [c for c in checks if isinstance(c, Mapping)] if isinstance(checks, list) else []


def envelope_rows(results: Mapping) -> list[Mapping]:
    """The 1.5.0 envelope rows (setback, street wall, side yard), each with its
    ``kind``, ``state``, ``text``, ``zr_sections`` and (applies/not_applicable)
    ``values``; empty when the document carries no envelope_rows block."""
    rows = results.get("envelope_rows") if isinstance(results, Mapping) else None
    return [r for r in rows if isinstance(r, Mapping)] if isinstance(rows, list) else []


def envelope_row(results: Mapping, kind: str) -> Mapping | None:
    """The 1.5.0 envelope row of one ``kind`` (``setback`` / ``street_wall`` /
    ``side_yard``), or ``None`` when the document carries none of that kind."""
    for row in envelope_rows(results):
        if row.get("kind") == kind:
            return row
    return None


def has_results_rows(results: Mapping) -> bool:
    """True when the document carries a 1.5.0 rear_yard block or any envelope row,
    so the page-3 rows read the engine's own readings. False for every 1.4.0 (and
    earlier) document, so the page falls back to the 1.4.0 output UNCHANGED (S1)."""
    return rear_yard_combined(results) is not None or bool(envelope_rows(results))
