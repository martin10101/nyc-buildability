"""The neighbourhood map (M5-T155, ruling Y3).

The street NETWORK of the streets window (the lot's bounding box plus 1,000 ft)
drawn as centre lines with their names in CAPITALS, each placed on an open
stretch of its street AWAY from intersections (a name is dropped rather than
allowed to cross another street), with the subject lot marked. It stays
NORTH-UP (the orchestrator's cue) so the reader can orient to grid north,
is clipped to a clean rectangular viewport, and computes no law (ruling Y6/Y8).

Needs the streets layer; unavailable returns :class:`Unavailable` (S6).
"""

from __future__ import annotations

from .layout import PLAN, PLAN_MARGIN, REPORT_PLAN, REPORT_PLAN_MARGIN
from .model import Drawing, MapContext, StreetLayer, Unavailable
from .site_context_plan import (
    FRAME_INSET,
    SUMMARY_PLAN,
    SUMMARY_PLAN_MARGIN,
    TITLE_BAND_PT,
    WIDE_PLAN,
    WIDE_PLAN_MARGIN,
    caption_notes,
    compose_context,
    draw_neighbourhood_scene,
    fit_view,
    summary_notes,
    unavailable_layer,
    viewport,
)

__all__ = ["draw_neighbourhood_map"]


def draw_neighbourhood_map(context: MapContext, *, frame: str = "sheet") -> Drawing | Unavailable:
    """The neighbourhood street network (north-up), the subject lot marked."""
    drawing = "neighbourhood_map"
    unavailable = unavailable_layer("streets", context.streets, "/map_context/streets")
    if unavailable is not None:
        return Unavailable(drawing, unavailable.reason, unavailable.reason_kind,
                           unavailable.source)
    assert isinstance(context.streets, StreetLayer)

    window = context.streets.window.box
    if frame == "summary":
        fr = fit_view(window, SUMMARY_PLAN, SUMMARY_PLAN_MARGIN, alpha=0.0, top_band=0.0)
        rect = viewport(SUMMARY_PLAN, FRAME_INSET)
        sheet = draw_neighbourhood_scene(context, fr, rect, SUMMARY_PLAN, summary=True)
        return compose_context(drawing, "Neighbourhood", sheet, fr, summary_notes(None),
                               mode="summary")
    if frame == "wide":
        fr = fit_view(window, WIDE_PLAN, WIDE_PLAN_MARGIN, alpha=0.0, top_band=0.0)
        rect = viewport(WIDE_PLAN, FRAME_INSET)
        sheet = draw_neighbourhood_scene(context, fr, rect, WIDE_PLAN, with_title=False)
        return compose_context(drawing, "Neighbourhood", sheet, fr, summary_notes(None),
                               mode="wide")
    report = frame == "report"
    region, margin = (REPORT_PLAN, REPORT_PLAN_MARGIN) if report else (PLAN, PLAN_MARGIN)
    fr = fit_view(window, region, margin, alpha=0.0, top_band=TITLE_BAND_PT)  # north-up
    rect = viewport(region)

    sheet = draw_neighbourhood_scene(context, fr, rect, region)
    notes = caption_notes(context, layers={"streets"})
    return compose_context(drawing, "Neighbourhood", sheet, fr, notes,
                           mode="report" if report else "sheet")
