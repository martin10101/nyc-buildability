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


def report_css() -> str:
    """The complete print stylesheet as one string."""
    ink = COLOR["ink"]
    supporting = COLOR["supporting"]
    divider = COLOR["divider"]
    surface = COLOR["surface"]
    action = COLOR["action"]
    caution_ink = COLOR["caution-ink"]
    caution_surface = COLOR["caution-surface"]
    return f"""
@page {{
  size: A4 portrait;
  margin: 14mm;
  @top-left {{ content: string(running-identity); font-size: 8pt; color: {supporting}; }}
  @top-right {{ content: "Preliminary zoning results"; font-size: 8pt; color: {supporting}; }}
  @bottom-left {{ content: string(running-footer); font-size: 8pt; color: {supporting}; }}
  @bottom-right {{
    content: "Page " counter(page) " of " counter(pages);
    font-size: 8pt; color: {supporting};
  }}
}}
html {{ font-family: Arial, Helvetica, sans-serif; color: {ink}; }}
body {{ margin: 0; font-size: 9.5pt; line-height: 1.4; background: {surface}; }}
.page-string-identity {{ string-set: running-identity content(); }}
.page-string-footer {{ string-set: running-footer content(); }}
.page-string-identity, .page-string-footer {{
  position: absolute; left: -10000px; top: 0; height: 0; overflow: hidden;
}}
.report-page {{ break-before: page; }}
.report-page:first-of-type {{ break-before: auto; }}
h1 {{ font-size: 22pt; line-height: 1.2; margin: 0 0 4mm; }}
h2 {{ font-size: 13pt; line-height: 1.3; margin: 0 0 2mm; break-after: avoid; }}
h3 {{ font-size: 11pt; line-height: 1.3; margin: 4mm 0 1.5mm; break-after: avoid; }}
p {{ margin: 0 0 2mm; }}
.reader-question {{ color: {supporting}; font-size: 10pt; margin: 0 0 4mm; }}
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
figure {{ margin: 0 0 3mm; break-inside: avoid; }}
figure svg {{ max-width: 182mm; max-height: 150mm; height: auto; }}
figcaption {{ font-size: 8pt; color: {supporting}; margin-top: 1.2mm; }}
.figure-note {{ font-size: 8pt; color: {supporting}; margin: 1mm 0 0; }}
.short-line {{ font-size: 9pt; color: {supporting}; font-style: italic; margin: 2mm 0 3mm; }}
a {{ color: {action}; }}
.bar-chart text {{ font-size: 7pt; }}
.key-table td, .key-table th {{ font-size: 8pt; }}
""".strip()
