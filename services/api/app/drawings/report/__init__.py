"""The program's report generator (task M5-T151).

Turns one results document (and, where available, a map document) into the
complete current-scope feasibility report in six reusable page types - decision
summary, site and context, option comparison, scenario sheet, assumptions and
open items, calculations and evidence - as one standalone HTML document for
printing (A4 portrait, 14 mm margins, running identity and page numbers in
reserved margin boxes). Built on the server from the results contract; the
drawings come from the drawing kit at the report frame (ruling X9).

The package is split into focused modules: one per page type, plus wording and
labels (:mod:`.labels`, :mod:`.sources`), the eleven-option list
(:mod:`.options`), figure formatting (:mod:`.formatting`), the document readers
(:mod:`.readers`), the drawing interface (:mod:`.drawings_embed`), the layout and
print CSS (:mod:`.layout`) and HTML assembly (:mod:`.html`). The one public entry
is :func:`build_report_html`.
"""

from __future__ import annotations

from .builder import build_report_html

__all__ = ["build_report_html"]
