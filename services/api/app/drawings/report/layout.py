"""Layout and print CSS for the report (ruling X2, X3; page-types.md "Sheet",
"Type", "Tables").

The one stylesheet the report document carries. It reads colour AND the print type
scale from the shared presentation tokens (``app.drawings.kit.presentation_tokens``),
so the report, the drawing kit and the website stay one system. Every FONT SIZE is
read from a ``TYPE`` token (D-094 R047, R048); the remaining literal ``pt`` values are
borders, line weights and letter spacing (contract section 6), not type sizes. It sets
A4 portrait with 14 mm margins and no other sheet size, the running
identity and "Page X of Y" in reserved page-margin boxes, a page break before each
page type, repeating table headers, rows that do not split, and the type scale.
"""

from __future__ import annotations

from app.drawings.kit.presentation_tokens import COLOR, TYPE

__all__ = ["report_css"]

# The print type scale, read from the TYPE tokens (no hard-coded pt below).
_TITLE_PT = TYPE["property-title"]["print_pt"]      # 22 pt
_HEADLINE_PT = TYPE["headline-value"]["print_pt"]   # 28-32 pt (the page-1 results)
_SECTION_PT = TYPE["section-title"]["print_pt"]      # 14 pt
_BODY_PT = TYPE["body"]["print_pt"]                  # 10.5 pt
_COMPACT_PT = TYPE["compact"]["print_pt"]            # 9.5 pt (tables, supporting text)
_NOTE_PT = TYPE["source-note"]["print_pt"]           # 8.5 pt (footer, captions, chips)


def _css_string(text: str) -> str:
    """Escape a value for use inside a CSS ``content: "..."`` string: backslash,
    double quote and newlines, and neutralize ``<``/``>`` as CSS hex escapes so a
    value containing ``</style>`` cannot terminate the ``<style>`` element the
    ``@page`` margin boxes live in (DB-277). ``\\3C `` and ``\\3E `` render as
    ``<`` and ``>`` in the content string, so any value without angle brackets
    (every run-identity value: address, "Results revision N", "computed
    YYYY-MM-DD") produces byte-identical CSS. The angle-bracket replaces come
    AFTER the backslash doubling so their own backslash is not doubled."""
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", " ")
        .replace("\r", " ")
        .replace("<", "\\3C ")
        .replace(">", "\\3E ")
    )


def report_css(header_left: str, footer_left: str) -> str:
    """The complete print stylesheet as one string. The running identity and
    footer are written LITERALLY into the ``@page`` margin boxes (Chromium does
    not support ``string-set``/``string()``), so both a browser and a server
    converter print them (F1). Every print size comes from the TYPE tokens."""
    ink = COLOR["ink"]
    supporting = COLOR["supporting"]
    divider = COLOR["divider"]
    surface = COLOR["surface"]
    action = COLOR["action"]
    caution_ink = COLOR["caution-ink"]
    caution_surface = COLOR["caution-surface"]
    header = _css_string(header_left)
    footer = _css_string(footer_left)
    return f"""
@page {{
  size: A4 portrait;
  margin: 14mm;
  @top-left {{ content: "{header}"; font-size: {_NOTE_PT}pt; color: {supporting}; }}
  @top-right {{
    content: "Preliminary zoning results"; font-size: {_NOTE_PT}pt; color: {supporting};
  }}
  @bottom-left {{ content: "{footer}"; font-size: {_NOTE_PT}pt; color: {supporting}; }}
  @bottom-right {{
    content: "Page " counter(page) " of " counter(pages);
    font-size: {_NOTE_PT}pt; color: {supporting};
  }}
}}
html {{ font-family: Arial, Helvetica, sans-serif; color: {ink}; }}
body {{ margin: 0; font-size: {_BODY_PT}pt; line-height: 1.4; background: {surface}; }}
.report-page {{ break-before: page; }}
.report-page:first-of-type {{ break-before: auto; }}
h1 {{ font-size: {_TITLE_PT}pt; line-height: 1.2; margin: 0 0 3mm; }}
h2 {{ font-size: {_SECTION_PT}pt; line-height: 1.3; margin: 0 0 2mm; break-after: avoid; }}
h3 {{ font-size: {_SECTION_PT}pt; line-height: 1.3; margin: 4mm 0 1.5mm; break-after: avoid; }}
p {{ margin: 0 0 2mm; }}
.reader-question {{ color: {supporting}; font-size: {_COMPACT_PT}pt; margin: 0 0 4mm; }}
.type-name {{
  color: {supporting}; font-size: {_NOTE_PT}pt; letter-spacing: 0.3pt; margin: 0 0 0.5mm;
}}
.identity-line {{ color: {supporting}; font-size: {_COMPACT_PT}pt; margin: 0 0 1mm; }}
.standing-label {{
  font-size: {_NOTE_PT}pt; color: {caution_ink}; background: {caution_surface};
  border-left: 2pt solid {caution_ink}; padding: 1.6mm 3mm; margin: 0 0 2.5mm;
}}
.answer {{ margin: 0 0 3mm; padding: 0 0 2mm; border-bottom: 0.4pt solid {divider}; }}
.answer-value {{ font-size: {_SECTION_PT}pt; font-weight: 700; }}
.label-chip {{
  font-size: {_NOTE_PT}pt; color: {supporting}; border: 0.4pt solid {divider};
  border-radius: 2pt; padding: 0.3mm 1.6mm; margin-left: 2mm; white-space: nowrap;
}}
.limitation {{ color: {caution_ink}; font-size: {_COMPACT_PT}pt; }}
table {{ border-collapse: collapse; width: 100%; margin: 2mm 0 3mm; font-size: {_COMPACT_PT}pt; }}
thead {{ display: table-header-group; background: {caution_surface}; }}
th, td {{
  border-bottom: 0.3pt solid {divider}; padding: 1.3mm 2mm; text-align: left;
  vertical-align: top;
}}
th {{ font-size: {_COMPACT_PT}pt; color: {ink}; }}
td.num, th.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
tr {{ break-inside: avoid; }}
/* A short table (the html builder marks it) moves whole across a page break, never
   splitting into a lone fragment; its heading stays with it (h3 break-after: avoid). */
.no-split {{ break-inside: avoid; }}
caption {{ text-align: left; font-weight: 600; font-size: {_NOTE_PT}pt; break-after: avoid; }}
/* Figures carry space above (D7) and keep together; drawings are embedded at
   their designed point size and are NEVER scaled by this stylesheet (D1): this
   stylesheet sets no size on an svg at all. */
figure {{ margin: 4mm 0 3mm; break-inside: avoid; }}
figcaption {{ font-size: {_NOTE_PT}pt; color: {supporting}; margin-top: 1.2mm; }}
.figure-note {{ font-size: {_NOTE_PT}pt; color: {supporting}; margin: 1mm 0 0; }}
.short-line {{
  font-size: {_COMPACT_PT}pt; color: {supporting}; font-style: italic; margin: 2mm 0 3mm;
}}
a {{ color: {action}; }}
.key-table td, .key-table th {{ font-size: {_NOTE_PT}pt; }}
.nowrap {{ white-space: nowrap; }}
/* The decision-summary row must fit the printable width: the answers table takes
   the remaining space and its cells wrap, the figure stays 88 mm, so nothing
   overflows and the whole body prints at its true size (correction 2). */
.summary {{ display: flex; gap: 4mm; align-items: flex-start; }}
.summary-answers {{ flex: 1 1 auto; min-width: 0; }}
.summary-figure {{ flex: 0 0 88mm; }}
.summary-figure figcaption {{ white-space: normal; }}
/* Two columns: the Answer name (with its status label below it) takes a fixed narrow
   column and the Result column takes the rest, so a key figure keeps its number and unit
   on one line in the space beside the 88 mm figure (visual G3 rework 2). */
.answers-table {{ table-layout: fixed; }}
.answers-table th:first-child, .answers-table td:first-child {{ width: 24mm; }}
.answer-name {{ margin: 0 0 1mm; }}
.answers-table td, .answers-table th {{ vertical-align: top; overflow-wrap: break-word;
  padding-top: 1mm; padding-bottom: 1mm; }}
.answers-table .identity-line, .answers-table .answer-detail {{ line-height: 1.3; }}
/* The page-1 results print in large type (the headline value scale); fonts are never
   shrunk to fit a page count (D-094 R047, R048) - a larger scale may add a page. */
.answers-table .answer-figure {{ font-weight: 700; font-size: {_HEADLINE_PT}pt; line-height: 1.1; }}
/* The rest of each result (the body detail) sits below the key figure at the body size,
   so a long result never prints at the headline size (visual G3 rework 1). */
.answer-detail {{ font-size: {_BODY_PT}pt; margin: 0.5mm 0 0; }}
.allowance-phrase {{ font-size: {_COMPACT_PT}pt; color: {supporting}; margin: 1mm 0 0; }}
/* The legal ceiling sits BESIDE the apartment estimate, side by side and distinct,
   with the distinction line below (D-094 R071, R078). */
.ceiling-estimate {{ margin: 3mm 0 2mm; }}
.ceiling-estimate-pair {{ display: flex; gap: 8mm; align-items: flex-start; }}
.ceiling, .estimate {{ flex: 1 1 0; min-width: 0; }}
.distinction {{ font-size: {_COMPACT_PT}pt; color: {supporting}; margin: 1.5mm 0 0; }}
/* The uncertainties list stays together (heading + its items) so it never splits
   across a page break into a lone item (visual G3 rework 1). */
.uncertainties {{ margin-top: 2mm; break-inside: avoid; }}
.uncertainties h3 {{ margin-top: 0; }}
.uncertainties ul {{ margin: 1mm 0 0; padding-left: 6mm; }}
.scope-line {{ font-size: {_COMPACT_PT}pt; color: {supporting}; margin: 2mm 0 0; }}
.scope-note {{ font-size: {_COMPACT_PT}pt; margin: 0 0 3mm; }}
.reason-row td {{
  font-size: {_NOTE_PT}pt; color: {supporting}; border-bottom: 0.3pt solid {divider};
  padding-top: 0; padding-bottom: 1.6mm;
}}
.open-number {{ white-space: nowrap; }}
/* Page type 2 opens with one neighbourhood locator; the 'What constrains the design?'
   sheet follows on its own printed page with the dimensioned constraints close-up
   (D-094 R014/R074, the one-locator composition). The .location-stack and
   .location-wide-figure rules below stay valid for one figure or two. */
.constraints-sheet {{ break-before: page; }}
.location-stack {{ margin-top: 2mm; }}
.location-wide-figure {{ break-inside: avoid; margin: 0 0 5mm; }}
.location-wide-figure figure {{ margin: 1mm 0; }}
.figure-title {{ font-size: {_COMPACT_PT}pt; font-weight: 700; margin: 0 0 1mm; }}
/* The scenario sheet's floor schedule and estimate stay together, so the estimate
   never lands alone on a page (rework 1 fix 5). */
.sheet-tail {{ break-inside: avoid; }}
/* The tall floor-stack figure sits beside the 'Why' and 'What was not checked' text
   so the sheet fits one page where it can (correction 3). */
.scenario-row {{ display: flex; gap: 6mm; align-items: flex-start; break-inside: avoid; }}
.scenario-figure {{ flex: 0 0 auto; }}
.scenario-figure figure {{ margin: 0; }}
.scenario-side {{ flex: 1 1 0; min-width: 0; }}
.scenario-side h3 {{ margin-top: 0; }}
/* The rules/review, drawing notes and run identity share a row in columns so the
   appendix stays compact (corrections T156-C1; M5-T169 DB-270). The row may break across
   a page so the status-label key is not pushed onto a near-empty last page. */
.evidence-columns {{ display: flex; gap: 8mm; align-items: flex-start; }}
.evidence-column {{ flex: 1 1 0; min-width: 0; }}
.evidence-column h3 {{ margin-top: 0; }}
.evidence-column ul {{ margin: 0; }}
/* A long unbroken run-identity value - the 40-character deployed commit printed in
   the run-identity column - breaks WITHIN its list item so it cannot overflow the
   narrow flex column and make Chromium shrink the whole document to fit (8 pages
   instead of 10; DB-277/S10). overflow-wrap:anywhere breaks only a token that would
   otherwise overflow, so every value that already fits is laid out byte-identically. */
.evidence-column li {{ overflow-wrap: anywhere; }}
/* The open-items table is TALL (a note under most rows), so it breaks between rows
   with its header repeated, and the assumptions plus the start of the open items
   share a page (correction 3). An item's note never separates from the item (the
   note row never starts a page), and at least three rows stay on each side. */
.reason-row {{ break-before: avoid; }}
.open-items-block table {{ orphans: 3; widows: 3; }}
.open-items-block table td {{ padding-top: 1mm; padding-bottom: 1mm; }}
""".strip()
