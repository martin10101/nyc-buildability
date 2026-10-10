"""The block close-up (M5-T155, ruling Y3).

A zoomed view of the whole context window (the lot's bounding box plus 400 ft):
the subject lot marked in coral among its neighbouring tax lots (each named
"Lot <n>" and its address), the existing buildings in grey, and the surrounding
street NETWORK drawn as centre lines with their names in CAPITALS along them. It
shares the site plan's look and its rotation to the lot's street frontage, and
computes no law (ruling Y6/Y8). Street names are read from the data; the caption
names every source and its date.

Needs the context window, the tax lots and the streets; any one unavailable
returns :class:`Unavailable` (S6), never a partial picture.
"""

from __future__ import annotations

from app.drawings.kit.sheet import Sheet
from app.drawings.kit.styles import TYPOGRAPHY

from .layout import PLAN, PLAN_MARGIN, REPORT_PLAN, REPORT_PLAN_MARGIN
from .model import BuildingLayer, Drawing, MapContext, StreetLayer, TaxLotLayer, Unavailable
from .site_context_plan import (
    TITLE_BAND_PT,
    caption_notes,
    compose_context,
    draw_buildings,
    draw_lot_addresses,
    draw_lot_numbers,
    draw_neighbour_lots,
    draw_street_centrelines,
    draw_subject_outline,
    draw_title,
    fit_view,
    frontage_rotation,
    label_street_lines,
    unavailable_layer,
)
from .subject import draw_subject_area

__all__ = ["draw_block_map"]


def draw_block_map(context: MapContext, *, frame: str = "sheet") -> Drawing | Unavailable:
    """The block close-up over the whole context window."""
    drawing = "block_map"
    if context.context_window is None:
        return Unavailable(drawing, "the context window is not in this document",
                           "source_unavailable", "/map_context/context_window")
    for name, layer, source in (
        ("tax_lots", context.tax_lots, "/map_context/tax_lots"),
        ("streets", context.streets, "/map_context/streets"),
    ):
        unavailable = unavailable_layer(name, layer, source)
        if unavailable is not None:
            return Unavailable(drawing, unavailable.reason, unavailable.reason_kind,
                               unavailable.source)
    assert isinstance(context.tax_lots, TaxLotLayer)
    assert isinstance(context.streets, StreetLayer)

    window = context.context_window.box
    alpha, frontage_name, frontage_source = frontage_rotation(context.subject_lot, context.streets)
    report = frame == "report"
    region, margin = (REPORT_PLAN, REPORT_PLAN_MARGIN) if report else (PLAN, PLAN_MARGIN)
    fr = fit_view(window, region, margin, alpha=alpha, top_band=TITLE_BAND_PT)

    buildings = context.buildings if isinstance(context.buildings, BuildingLayer) else None
    layers = {"tax_lots", "streets"}

    sheet = Sheet()
    draw_street_centrelines(sheet, context.streets, fr, window)
    draw_subject_area(sheet, context.subject_lot, fr)
    draw_neighbour_lots(sheet, context.tax_lots, fr, window)
    if buildings is not None:
        draw_buildings(sheet, buildings, fr, window)
        layers.add("buildings")
    draw_subject_outline(sheet, context.subject_lot, fr)
    # Lot numbers first (fixed at the lot centroids); the street names route clear
    # of them; the addresses go last and skip if they would overlap.
    draw_lot_numbers(sheet, context, fr, window)
    label_street_lines(sheet, context.streets, fr, TYPOGRAPHY.label_pt + 1.0, window,
                       with_width=False)
    draw_lot_addresses(sheet, context, fr, window)
    draw_title(sheet, "Block close-up", context.subject_lot, region)

    notes = caption_notes(context, layers=layers, gaps_note=False, frontage=frontage_name,
                          frontage_source=frontage_source)
    return compose_context(drawing, "Block close-up", sheet, fr, notes, report=report)
