"""Assemble the full report document (ruling X2).

One public entry, :func:`build_report_html`, turns one results document (and,
where available, a map document) into the complete current-scope report in the
six page types, as one standalone HTML string: A4 print CSS, the running
identity and page numbers in reserved margin boxes, and no script. It reuses the
focused page modules and reads every figure from the document.
"""

from __future__ import annotations

from collections.abc import Mapping

from . import (
    drawings_embed,
    layout,
    page_assumptions,
    page_decision_summary,
    page_evidence,
    page_location,
    page_option_comparison,
    page_scenario_sheet,
    page_site_context,
    readers,
)
from .html import escape

__all__ = ["build_report_html"]


def _identity(results: Mapping, identity: Mapping | None) -> dict:
    override = identity or {}
    ident = readers.identity(results, address=override.get("address"))
    for key, value in override.items():
        if value is not None:
            ident[key] = value
    return ident


def _footer_line(ident: Mapping) -> str:
    bits = []
    if ident.get("revision") is not None:
        bits.append(f"Results revision {ident['revision']}")
    if ident.get("computed_at"):
        bits.append(f"computed {str(ident['computed_at']).split('T', 1)[0]}")
    return " · ".join(bits) if bits else "Preliminary zoning results"


def build_report_html(
    results: Mapping,
    *,
    map_context: Mapping | None = None,
    identity: Mapping | None = None,
    env=None,
) -> str:
    """The complete report as one standalone HTML document."""
    ident = _identity(results, identity)
    header_line = readers.identity_header_line(ident)
    footer_line = _footer_line(ident)

    # The lot among its surroundings is shown ONLY when the map document's subject
    # outline equals the results lot outline (ruling Y5, the one-outline check);
    # otherwise today's lot-only plan is kept and one limitation line is printed.
    # Two outlines are never drawn together (S2).
    surroundings = page_location.resolve(map_context, results, env=env)
    if surroundings.available and surroundings.report_plan is not None:
        # The full-size site plan among its surroundings, shown once on the
        # constraints sheet (the same full-size drawing is never printed twice).
        site_plan = surroundings.report_plan
    else:
        site_plan = drawings_embed.embed_kit_drawing(
            "render_site_plan", results, env=env,
            not_available_line="The site plan is not available for this report.",
        )
    # 'Context maps' moves to what the report covers only when the maps are printed
    # (ruling Y10 / S5); otherwise the coverage block reports them as not yet.
    maps_present = surroundings.available
    # Page 1 carries the COMPACT summary-frame site plan beside the answers (not the
    # full-size one); ``None`` falls back to the wave-21 summary site plan.
    summary_plan = surroundings.summary_plan if surroundings.available else None
    pages = [
        page_decision_summary.render(results, ident, maps_present=maps_present,
                                     site_context_plan=summary_plan, env=env),
        page_site_context.render(results, ident, site_plan=site_plan,
                                 surroundings=surroundings, env=env),
        page_option_comparison.render(results, ident, env=env),
        page_scenario_sheet.render(results, ident, env=env),
        page_assumptions.render(results, ident, env=env),
        page_evidence.render(results, ident, map_context=map_context, env=env),
    ]

    title = ident.get("address") or ident.get("display") or "Preliminary zoning results"
    body = "".join(pages)
    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{escape(title)}</title>\n"
        f"<style>{layout.report_css(header_line, footer_line)}</style>\n"
        "</head>\n"
        f"<body>\n{body}\n</body>\n</html>\n"
    )
