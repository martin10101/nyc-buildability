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
    page_option_comparison,
    page_scenario_sheet,
    page_site_context,
    readers,
)
from .drawings_embed import Embedded
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
        bits.append(f"Revision {ident['revision']}")
    if ident.get("computed_at"):
        bits.append(f"computed {str(ident['computed_at']).split('T', 1)[0]}")
    return ", ".join(bits) if bits else "Preliminary zoning results"


def _map(fn_name: str, map_context: Mapping | None, env) -> Embedded:
    if not isinstance(map_context, Mapping):
        return Embedded(short_line="Context maps are not included in this report.")
    return drawings_embed.embed_map(fn_name, map_context, env=env)


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

    site_plan = drawings_embed.embed_kit_drawing("render_site_plan", results, env=env)
    location_map = _map("render_location_map", map_context, env)
    zoning_map = _map("render_zoning_map", map_context, env)
    maps_present = location_map.is_drawing or zoning_map.is_drawing

    pages = [
        page_decision_summary.render(results, ident, map_context=map_context, env=env),
        page_site_context.render(
            results, ident, site_plan=site_plan,
            location_map=location_map, zoning_map=zoning_map, env=env,
        ),
        page_option_comparison.render(results, ident, env=env),
        page_scenario_sheet.render(results, ident, env=env),
        page_assumptions.render(results, ident, maps_present=maps_present, env=env),
        page_evidence.render(results, ident, map_context=map_context, env=env),
    ]

    title = ident.get("display") or ident.get("address") or "Preliminary zoning results"
    body = (
        f'<div class="page-string-identity">{escape(header_line)}</div>'
        f'<div class="page-string-footer">{escape(footer_line)}</div>'
        + "".join(pages)
    )
    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{escape(title)}</title>\n"
        f"<style>{layout.report_css()}</style>\n"
        "</head>\n"
        f"<body>\n{body}\n</body>\n</html>\n"
    )
