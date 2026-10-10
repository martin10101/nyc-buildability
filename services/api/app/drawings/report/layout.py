"""Layout and print CSS for the report (ruling X2, X3; page-types.md "Sheet",
"Type", "Tables").

The one stylesheet the report document carries. It reads colour and type sizes
from the shared presentation tokens (``app.drawings.kit.presentation_tokens``),
so the report, the drawing kit and the website stay one system. It sets A4
portrait with 14 mm margins and no other sheet size, the running identity and
"Page X of Y" in reserved page-margin boxes (``counter(page)``,
``counter(pages)``, ``string(...)``), a page break before each page type,
repeating table headers, rows that do not split, and the minimum type sizes.
"""

from __future__ import annotations

from app.drawings.kit.presentation_tokens import COLOR

__all__ = ["report_css"]


def _css_string(text: str) -> str:
    """Escape a value for use inside a CSS ``content: "..."`` string: backslash,
    double quote and newlines."""
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", " ")
        .replace("\r", " ")
    )


def report_css(header_left: str, footer_left: str) -> str:
    """The complete print stylesheet as one string. The running identity and
    footer are written LITERALLY into the ``@page`` margin boxes (Chromium does
    not support ``string-set``/``string()``), so both a browser and a server
    converter print them (F1)."""
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
  @top-left {{ content: "{header}"; font-size: 8pt; color: {supporting}; }}
  @top-right {{ content: "Preliminary zoning results"; font-size: 8pt; color: {supporting}; }}
  @bottom-left {{ content: "{footer}"; font-size: 8pt; color: {supporting}; }}
  @bottom-right {{
    content: "Page " counter(page) " of " counter(pages);
    font-size: 8pt; color: {supporting};
  }}
}}
html {{ font-family: Arial, Helvetica, sans-serif; color: {ink}; }}
body {{ margin: 0; font-size: 9.5pt; line-height: 1.4; background: {surface}; }}
.report-page {{ break-before: page; }}
.report-page:first-of-type {{ break-before: auto; }}
h1 {{ font-size: 22pt; line-height: 1.2; margin: 0 0 4mm; }}
h2 {{ font-size: 13pt; line-height: 1.3; margin: 0 0 2mm; break-after: avoid; }}
h3 {{ font-size: 11pt; line-height: 1.3; margin: 4mm 0 1.5mm; break-after: avoid; }}
p {{ margin: 0 0 2mm; }}
.reader-question {{ color: {supporting}; font-size: 10pt; margin: 0 0 4mm; }}
.type-name {{ color: {supporting}; font-size: 8.5pt; letter-spacing: 0.3pt; margin: 0 0 0.5mm; }}
.identity-line {{ color: {supporting}; font-size: 9pt; margin: 0 0 1mm; }}
.standing-label {{
  font-size: 8.5pt; color: {caution_ink}; background: {caution_surface};
  border-left: 2pt solid {caution_ink}; padding: 2mm 3mm; margin: 0 0 4mm;
}}
.answer {{ margin: 0 0 3mm; padding: 0 0 2mm; border-bottom: 0.4pt solid {divider}; }}
.answer-value {{ font-size: 14pt; font-weight: 700; }}
.label-chip {{
  font-size: 8pt; color: {supporting}; border: 0.4pt solid {divider};
  border-radius: 2pt; padding: 0.3mm 1.6mm; margin-left: 2mm; white-space: nowrap;
}}
.limitation {{ color: {caution_ink}; font-size: 9pt; }}
table {{ border-collapse: collapse; width: 100%; margin: 2mm 0 3mm; font-size: 8.5pt; }}
thead {{ display: table-header-group; background: {caution_surface}; }}
th, td {{
  border-bottom: 0.3pt solid {divider}; padding: 1.3mm 2mm; text-align: left;
  vertical-align: top;
}}
th {{ font-size: 8pt; color: {ink}; }}
td.num, th.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
tr {{ break-inside: avoid; }}
caption {{ text-align: left; font-weight: 600; font-size: 8.5pt; break-after: avoid; }}
/* Figures carry space above (D7) and keep together; drawings are embedded at
   their designed point size and are NEVER scaled by this stylesheet (D1): this
   stylesheet sets no size on an svg at all. */
figure {{ margin: 4mm 0 3mm; break-inside: avoid; }}
figcaption {{ font-size: 8pt; color: {supporting}; margin-top: 1.2mm; }}
.figure-note {{ font-size: 8pt; color: {supporting}; margin: 1mm 0 0; }}
.short-line {{ font-size: 9pt; color: {supporting}; font-style: italic; margin: 2mm 0 3mm; }}
a {{ color: {action}; }}
.key-table td, .key-table th {{ font-size: 8pt; }}
.nowrap {{ white-space: nowrap; }}
.summary {{ display: flex; gap: 6mm; align-items: flex-start; }}
.summary-answers {{ flex: 1 1 auto; }}
.summary-figure {{ flex: 0 0 auto; }}
.answers-table td {{ vertical-align: top; }}
.answers-table .answer-figure {{ font-weight: 700; font-size: 11pt; white-space: nowrap; }}
.reason-row td {{
  font-size: 8pt; color: {supporting}; border-bottom: 0.3pt solid {divider};
  padding-top: 0; padding-bottom: 1.6mm;
}}
.open-number {{ white-space: nowrap; }}
.estimate-line {{ margin: 2mm 0 3mm; }}
.coverage {{ margin-top: 4mm; }}
.coverage-line {{ font-size: 9pt; margin: 0 0 1mm; }}
/* Page type 2 opens with the one-page 'Where is the lot?' sheet; the 'What
   constrains the design?' sheet follows on its own printed page (ruling Y10). The
   two location thumbnails sit side by side; the grid can take a third later. */
.constraints-sheet {{ break-before: page; }}
.location-figures {{ display: flex; flex-wrap: wrap; gap: 6mm; align-items: flex-start; }}
.location-figure {{ flex: 0 1 auto; max-width: 88mm; break-inside: avoid; margin: 3mm 0; }}
.location-figure figure {{ margin: 0; }}
.location-figure figcaption {{ max-width: 88mm; }}
.figure-title {{ font-size: 9pt; font-weight: 700; margin: 0 0 1mm; }}
/* The scenario sheet's schedule, unchecked items and estimate stay together, so
   the estimate never lands alone on a page (rework 1 fix 5). */
.sheet-tail {{ break-inside: avoid; }}
""".strip()
