"""The block close-up (M5-T155, ruling Y3).

The whole context window (the lot's bounding box plus 400 ft), drawn like the
competitor's page-4 "Property Close-Up": the subject lot coloured among its
neighbours (thin light outlines, UNLABELLED - only the subject is labelled),
the existing buildings light grey, and the surrounding streets as the even open
space between the tax lots with one name per street centred in the street. It
shares the site plan's look and its rotation to the lot's frontage, is clipped
to a clean rectangular viewport, and computes no law (ruling Y6/Y8).

Needs the context window, the tax lots and the streets; any one unavailable
returns :class:`Unavailable` (S6).
"""

from __future__ import annotations

from .layout import PLAN, PLAN_MARGIN, REPORT_PLAN, REPORT_PLAN_MARGIN
from .model import BuildingLayer, Drawing, MapContext, StreetLayer, TaxLotLayer, Unavailable
from .site_context_plan import (
    TITLE_BAND_PT,
    caption_notes,
    compose_context,
    draw_block_scene,
    fit_view,
    frontage_rotation,
    unavailable_layer,
    viewport,
)

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
    rect = viewport(region)

    layers = {"tax_lots", "streets"}
    if isinstance(context.buildings, BuildingLayer):
        layers.add("buildings")
    sheet = draw_block_scene(context, fr, rect, region, title="Block close-up",
                             with_edges=False, with_widths=False, label_focus=False)
    notes = caption_notes(context, layers=layers, gaps_note=True, frontage=frontage_name,
                          frontage_source=frontage_source)
    return compose_context(drawing, "Block close-up", sheet, fr, notes, report=report)
