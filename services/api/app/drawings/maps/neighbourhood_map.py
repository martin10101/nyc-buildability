"""The neighbourhood map (M5-T155, ruling Y3).

The street NETWORK of the streets window (the lot's bounding box plus 1,000 ft)
drawn as centre lines with their names in CAPITALS along them, with the subject
lot marked in coral and labelled. It stays NORTH-UP (the orchestrator's cue: the
neighbourhood map is not rotated), so the reader can orient the whole area to
grid north. It computes no law (ruling Y6/Y8); street names are read from the
data, and the caption names the sources and their dates.

Needs the streets layer; unavailable returns :class:`Unavailable` (S6).
"""

from __future__ import annotations

from app.drawings.kit.sheet import Sheet
from app.drawings.kit.styles import TYPOGRAPHY

from .layout import PLAN, PLAN_MARGIN, REPORT_PLAN, REPORT_PLAN_MARGIN
from .model import Drawing, MapContext, StreetLayer, Unavailable
from .site_context_plan import (
    TITLE_BAND_PT,
    caption_notes,
    compose_context,
    draw_street_centrelines,
    draw_title,
    fit_view,
    label_street_lines,
    mark_subject,
    unavailable_layer,
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
    report = frame == "report"
    region, margin = (REPORT_PLAN, REPORT_PLAN_MARGIN) if report else (PLAN, PLAN_MARGIN)
    fr = fit_view(window, region, margin, alpha=0.0, top_band=TITLE_BAND_PT)  # north-up

    sheet = Sheet()
    draw_street_centrelines(sheet, context.streets, fr, window)
    # Mark the subject first (its label is reserved), then the street names route
    # clear of it. The neighbourhood map omits the width labels (too dense at the
    # ~2,000 ft scale) - the block close-up carries the widths.
    mark_subject(sheet, context.subject_lot, fr, TYPOGRAPHY.label_pt)
    label_street_lines(sheet, context.streets, fr, TYPOGRAPHY.label_pt + 1.0, window,
                       with_width=False)
    draw_title(sheet, "Neighbourhood", context.subject_lot, region)

    notes = caption_notes(context, layers={"streets"})
    return compose_context(drawing, "Neighbourhood", sheet, fr, notes, report=report)
