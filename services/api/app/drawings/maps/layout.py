"""Shared page layout for the maps: the plan region, the right-hand panel
(north arrow, scale bar, legend generated from what is drawn, sourced notes),
and assembly into a finished :class:`Drawing`.

Both maps compose the same way, so the panel is built once here. The legend,
scale bar and note machinery are reused verbatim from the drawing-kit furniture
so the look is identical to the site plan, section and massing.
"""

from __future__ import annotations

from collections.abc import Sequence

from app.drawings.kit.furniture import Note, legend, north_arrow, notes_block, scale_bar
from app.drawings.kit.hatches import hatch_defs
from app.drawings.kit.sheet import Sheet
from app.drawings.kit.svg import svg_document

from .model import Drawing, MapNote

__all__ = ["CANVAS_H", "CANVAS_W", "PLAN", "PLAN_MARGIN", "compose", "map_notes"]

CANVAS_W, CANVAS_H = 720.0, 504.0
PLAN = (16.0, 16.0, 500.0, 488.0)  # x0, y0, x1, y1 of the plan region
PLAN_MARGIN = 40.0  # room around the mapped features for labels
PANEL_X, PANEL_W = 520.0, 184.0


def map_notes(notes: Sequence[MapNote]) -> list[Note]:
    """Each :class:`MapNote` as a furniture note whose single run names its
    source (so every printed note traces back to the data)."""
    return [Note(((note.text, note.source),)) for note in notes]


def compose(
    drawing: str, title: str, sheet: Sheet, px_per_ft: float, notes: Sequence[MapNote]
) -> Drawing:
    """Assemble the plan ``sheet`` plus the panel into one SVG drawing."""
    panel = north_arrow(PANEL_X + 20.0, 16.0)
    bar_parts, bar_labels = scale_bar(PANEL_X, 88.0, px_per_ft, 160.0)
    legend_parts, legend_bottom = legend(sheet.kinds, PANEL_X, 118.0)
    note_parts, note_labels, notes_bottom = notes_block(
        map_notes(notes), PANEL_X, legend_bottom + 10.0, PANEL_W
    )
    height = max(CANVAS_H, notes_bottom + 12.0)
    body = sheet.parts + panel + bar_parts + legend_parts + note_parts
    svg = svg_document(width=CANVAS_W, height=height, drawing=drawing, title=title,
                       defs=hatch_defs(sheet.kinds), body=body)
    labels = tuple(sheet.labels + bar_labels + note_labels)
    return Drawing(drawing, svg, labels, tuple(sheet.kinds))
