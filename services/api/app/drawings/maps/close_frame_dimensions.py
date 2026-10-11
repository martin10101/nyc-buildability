"""Dimension lines for the constraints close frame (M5-T166, D-094 R014/R015).

Each dimension is anchored to ONE edge of the subject lot's outline: two witness
lines rise from the edge's own endpoints to an offset dimension line, and the
label names the length and its basis in plain words, e.g.
``"99.98 ft, map outline, not surveyed"``.

The outline the close frame draws is the MapPLUTO (``gis``) outline, so the only
basis the 1.4.0 document carries is the city map outline (short form on drawings
"map outline"; D-094 contract change 2026-10-11). No tax-map figure is drawn -
none is in the 1.4.0 document, and a tax-map value is never merged with a GIS
outline (NB-04). An edge too short to carry a legible dimension is left
undimensioned (never a bare half-number). If a label cannot be placed at the
minimum size without a collision the frame FAILS rather than shrinking the label
or dropping the dimension silently (presentation contract section 6).

Witness-line endpoints lie on the edge's own projected vertices (``fr.px`` of the
ring vertex), so a dimension always measures the edge it is drawn against.
Coordinates are screen points.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from app.drawings.kit import geometry as geo
from app.drawings.kit.labels import Box, format_feet
from app.drawings.kit.sheet import Sheet
from app.drawings.kit.styles import style_for
from app.drawings.kit.svg import element, num

from .context_scene import ViewFrame, place, readable_angle, screen_dir
from .model import Point, Polygon

__all__ = [
    "DIMENSION_MIN_PT",
    "GIS_BASIS",
    "MIN_LABELLED_EDGE_FT",
    "DimensionPlacementError",
    "DrawnDimension",
    "draw_edge_dimensions",
]

_Box = tuple[float, float, float, float]

# The plain-words basis for the city-map outline the close frame draws (the gis
# short form "map outline" from the design contract, plus the standing honesty
# qualifier). Every dimension names it; nothing is merged across bases.
GIS_BASIS = "map outline, not surveyed"

MIN_LABELLED_EDGE_FT = 6.0     # a shorter edge is left undimensioned (never a bare number)
DIMENSION_MIN_PT = 8.5         # dimension labels print at least 8.5 pt (contract section 6)
_WITNESS_OFFSET_PT = 12.0      # the dimension line sits this far outside the edge
_LABEL_STEP_PT = 2.0           # extra outward clearance tried per candidate
_LANE_STEPS = 10               # candidate positions outward (a wider lane clears a near line)
_ALONG_STEPS = 6               # candidate shifts along the edge, each way, when the lane is blocked


class DimensionPlacementError(RuntimeError):
    """A dimension label could not be placed at the minimum size without a
    collision. The close frame FAILS rather than shrinking the label below the
    minimum or dropping a dimension silently (presentation contract section 6)."""


@dataclass(frozen=True)
class DrawnDimension:
    """One drawn edge dimension. ``a_px``/``b_px`` are the edge's two projected
    vertices - the witness lines are anchored there, so the dimension measures the
    edge it is drawn against (S1). ``label_box`` is the placed label's bounds, so a
    caller can prove the label crosses no drawn line but its own (rework 2)."""

    edge_index: int
    length_ft: float
    text: str
    basis: str
    a_px: Point
    b_px: Point
    label_box: Box


def _dimension_line(a: Point, b: Point, edge_index: int, kind: str) -> str:
    style = style_for("dimension")  # the annotation look (never added to the legend)
    return element("path", [
        ("d", f"M{num(a[0])} {num(a[1])} L{num(b[0])} {num(b[1])}"),
        ("fill", "none"), ("stroke", style.outline),
        ("stroke-width", style.line_weight_pt),
        ("data-role", "dimension-line"), ("data-kind", kind), ("data-edge", edge_index)])


def draw_edge_dimensions(
    sheet: Sheet, outline: Polygon, fr: ViewFrame, rect: _Box, *,
    basis: str = GIS_BASIS, size: float = DIMENSION_MIN_PT,
    min_edge_ft: float = MIN_LABELLED_EDGE_FT, avoid_lines=None,
) -> list[DrawnDimension]:
    """Draw a dimension against every edge of ``outline`` at least ``min_edge_ft``
    long: two witness lines from the edge's own projected vertices to an offset
    dimension line, and a label ``"<length> ft, <basis>"`` placed just outside the
    edge. Returns the drawn dimensions. Raises :class:`DimensionPlacementError`
    when a label cannot be placed at ``size`` without a collision (S2)."""
    if size < DIMENSION_MIN_PT:
        raise DimensionPlacementError(
            f"dimension label size {size} pt is below the {DIMENSION_MIN_PT} pt minimum")
    ring = outline.exterior
    area = geo.signed_area(ring)
    drawn: list[DrawnDimension] = []
    for i, (a, b) in enumerate(geo.edges(ring)):
        length = geo.edge_length(a, b)
        if length < min_edge_ft:
            continue
        pa, pb = fr.px(a), fr.px(b)
        nx, ny = geo.outward_normal(a, b, area)
        mid_world = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        n = screen_dir(mid_world[0], mid_world[1], (nx, ny), fr)
        dim_a = (pa[0] + n[0] * _WITNESS_OFFSET_PT, pa[1] + n[1] * _WITNESS_OFFSET_PT)
        dim_b = (pb[0] + n[0] * _WITNESS_OFFSET_PT, pb[1] + n[1] * _WITNESS_OFFSET_PT)
        text = f"{format_feet(length)}, {basis}"
        ang = readable_angle(math.degrees(math.atan2(pb[1] - pa[1], pb[0] - pa[0])))
        mx, my = (dim_a[0] + dim_b[0]) / 2.0, (dim_a[1] + dim_b[1]) / 2.0
        # Candidates move the label OUTWARD (a wider lane) and, when needed, ALONG the
        # edge, so it can dodge a neighbour boundary that brackets the lane while still
        # naming the edge it measures; ordered by least total displacement so the label
        # stays as centred and close to its edge as a clear spot allows (rework 2).
        elen = math.hypot(pb[0] - pa[0], pb[1] - pa[1]) or 1.0
        ux, uy = (pb[0] - pa[0]) / elen, (pb[1] - pa[1]) / elen
        step = size + _LABEL_STEP_PT
        grid = [(3.0 + j * step, al * step)
                for j in range(_LANE_STEPS) for al in range(-_ALONG_STEPS, _ALONG_STEPS + 1)]
        grid.sort(key=lambda oa: (oa[0] - 3.0) + abs(oa[1]))
        cands = [(mx + n[0] * out + ux * al, my + n[1] * out + uy * al, ang)
                 for out, al in grid]
        # cross_max_len=0.0 rejects a candidate whose box is touched by ANY line in
        # avoid_lines (the drawn lot boundaries and streets, NOT the dimension's own
        # witness/dimension lines, which are drawn below): a label may never cross a
        # drawn line other than its own (presentation contract section 6; rework 2).
        box = place(sheet, cands, text, size=size, source=f"edge:{outline.source}/0#{i}",
                    role="dimension", anchor="middle", rect=rect, pad=2.0,
                    avoid_lines=avoid_lines, own=None, cross_max_len=0.0)
        if box is None:
            raise DimensionPlacementError(
                f"edge {i} dimension {text!r} does not fit at {size} pt without a collision")
        # the witness lines are anchored ON the edge's own vertices (S1).
        sheet.parts.append(_dimension_line(pa, dim_a, i, "witness"))
        sheet.parts.append(_dimension_line(pb, dim_b, i, "witness"))
        sheet.parts.append(_dimension_line(dim_a, dim_b, i, "dimension"))
        drawn.append(DrawnDimension(i, length, text, basis, pa, pb, box))
    return drawn
