"""Site plan SVG from the results geometry (plan section 5c item 2).

Draws the lot lines with dimension labels computed from the lot outline
(never typed), the ground-floor footprint colored by use, required yards
hatched, setback lines, street names (only those present in the results -
street widths are printed only once the results carry them), a north arrow,
a scale bar, a legend generated from what is drawn, and notes read from the
results (measurement label, yards not required, layers not available).

The plan scale is a standard architectural/engineering scale (1 in = S ft at
72 points per inch), the largest that fits, so a later PDF can print it to
scale; the scale bar states it graphically.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from . import geometry as geo
from .errors import DrawingInputError
from .furniture import Note, case_notes, legend, north_arrow, notes_block, scale_bar, scope_notes
from .hatches import hatch_defs
from .labels import YARD_KIND_NAMES, format_feet, format_number
from .model import Drawing, DrawingInput, LayerUnavailable, Point, Polygon
from .sheet import Sheet
from .styles import TYPOGRAPHY, style_for
from .svg import element, path_data, polyline_data, svg_document

__all__ = ["STANDARD_SCALES_FT_PER_IN", "draw_site_plan"]

CANVAS_W, CANVAS_H = 720.0, 504.0
PLAN = (16.0, 16.0, 500.0, 488.0)  # x0, y0, x1, y1 of the plan region
PLAN_MARGIN = 62.0  # room around the lot for dimension and street labels
PANEL_X, PANEL_W = 520.0, 184.0
POINTS_PER_INCH = 72.0
STANDARD_SCALES_FT_PER_IN = (
    1, 2, 4, 5, 8, 10, 16, 20, 30, 32, 40, 50, 60, 64, 80, 100, 120, 128, 150, 200,
    250, 300, 400, 500, 600, 800, 1000, 2000, 5000,
)
DIM_OFFSET = 12.0


@dataclass(frozen=True)
class _Frame:
    k: float  # drawing points per foot
    ox: float
    oy: float
    minx: float
    maxy: float

    def px(self, p: Point) -> Point:
        return self.ox + (p[0] - self.minx) * self.k, self.oy + (self.maxy - p[1]) * self.k


def _frame(lot: Polygon) -> _Frame:
    minx, miny, maxx, maxy = geo.bbox(lot.exterior)
    width, height = maxx - minx, maxy - miny
    avail_w = (PLAN[2] - PLAN[0]) - 2 * PLAN_MARGIN
    avail_h = (PLAN[3] - PLAN[1]) - 2 * PLAN_MARGIN
    fit = min(avail_w / width, avail_h / height)
    k = next((POINTS_PER_INCH / s for s in STANDARD_SCALES_FT_PER_IN
              if POINTS_PER_INCH / s <= fit), None)
    if k is None:
        raise DrawingInputError("lot_too_large", "lot does not fit the largest plan scale",
                                location=lot.source)
    ox = PLAN[0] + ((PLAN[2] - PLAN[0]) - width * k) / 2.0
    oy = PLAN[1] + ((PLAN[3] - PLAN[1]) - height * k) / 2.0
    return _Frame(k, ox, oy, minx, maxy)


def _px_rings(polygon: Polygon, frame: _Frame) -> list[list[Point]]:
    return [[frame.px(p) for p in ring] for ring in polygon.rings]


def _readable(angle_deg: float) -> float:
    """Rotate text along a line but never upside down: into [-90, 90), so
    vertical text reads bottom to top."""
    if angle_deg >= 90.0:
        angle_deg -= 180.0
    elif angle_deg < -90.0:
        angle_deg += 180.0
    return angle_deg


def _along(pa: Point, pb: Point, normal: Point, offset: float, size: float, steps: int = 5):
    """Label candidates beside segment pa-pb on the ``normal`` side, stepping outward."""
    angle = _readable(math.degrees(math.atan2(pb[1] - pa[1], pb[0] - pa[0])))
    up = (math.sin(math.radians(angle)), -math.cos(math.radians(angle)))
    lift = 2.0 if up[0] * normal[0] + up[1] * normal[1] >= 0 else 2.0 + 0.8 * size
    mx, my = (pa[0] + pb[0]) / 2.0, (pa[1] + pb[1]) / 2.0
    return [
        (mx + normal[0] * (offset + lift + i * (size + 2.0)),
         my + normal[1] * (offset + lift + i * (size + 2.0)), angle)
        for i in range(steps)
    ]


def _dimensions(sheet: Sheet, data: DrawingInput, frame: _Frame) -> None:
    ring = data.lot.exterior
    area = geo.signed_area(ring)
    dim = style_for("dimension")
    sheet.use_kind("dimension")
    size = TYPOGRAPHY.dimension_pt
    for i, (a, b) in enumerate(geo.edges(ring)):
        nx, ny = geo.outward_normal(a, b, area)
        n = (nx, -ny)  # drawing y points down
        pa, pb = frame.px(a), frame.px(b)
        length = math.hypot(pb[0] - pa[0], pb[1] - pa[1])
        u = ((pb[0] - pa[0]) / length, (pb[1] - pa[1]) / length)
        tick = ((u[0] + n[0]) * 2.2, (u[1] + n[1]) * 2.2)
        segs = []
        for p in (pa, pb):
            base = (p[0] + n[0] * 2.0, p[1] + n[1] * 2.0)
            end = (p[0] + n[0] * (DIM_OFFSET + 3.0), p[1] + n[1] * (DIM_OFFSET + 3.0))
            on = (p[0] + n[0] * DIM_OFFSET, p[1] + n[1] * DIM_OFFSET)
            segs.append(polyline_data([base, end]))
            segs.append(polyline_data([(on[0] - tick[0], on[1] - tick[1]),
                                       (on[0] + tick[0], on[1] + tick[1])]))
        da = (pa[0] + n[0] * DIM_OFFSET, pa[1] + n[1] * DIM_OFFSET)
        db = (pb[0] + n[0] * DIM_OFFSET, pb[1] + n[1] * DIM_OFFSET)
        segs.append(polyline_data([da, db]))
        sheet.parts.append(element("path", [("d", " ".join(segs)), ("fill", "none"),
                                            ("stroke", dim.outline),
                                            ("stroke-width", float(dim.line_weight_pt))]))
        text = format_feet(geo.edge_length(a, b))
        sheet.label(_along(pa, pb, n, DIM_OFFSET, size), text, size=size,
                    source=f"edge:{data.lot.source}/0#{i}", role="dimension", anchor="middle")


def _streets(sheet: Sheet, data: DrawingInput, frame: _Frame) -> None:
    size = TYPOGRAPHY.label_pt + 1.0
    for street in data.streets:
        segs = list(zip(street.frontage, street.frontage[1:], strict=False))
        a, b = max(segs, key=lambda s: geo.edge_length(*s))  # first longest on ties
        length = geo.edge_length(a, b)
        n_ft = ((b[1] - a[1]) / length, -(b[0] - a[0]) / length)
        eps = min(0.5, length * 0.01)
        probe = ((a[0] + b[0]) / 2 + n_ft[0] * eps, (a[1] + b[1]) / 2 + n_ft[1] * eps)
        if geo.point_location(probe, data.lot.exterior) == "inside":
            n_ft = (-n_ft[0], -n_ft[1])
        n = (n_ft[0], -n_ft[1])
        offset = DIM_OFFSET + TYPOGRAPHY.dimension_pt + 14.0
        sheet.label(_along(frame.px(a), frame.px(b), n, offset, size), street.name,
                    size=size, source=f"{street.source}/street", role="street",
                    anchor="middle", style="italic")


def _yards(sheet: Sheet, data: DrawingInput, frame: _Frame) -> None:
    if isinstance(data.yards, LayerUnavailable):
        return
    size = TYPOGRAPHY.label_pt
    for yard in data.yards:
        sheet.area(path_data(_px_rings(yard.outline, frame)), "yard",
                   [("data-source", yard.source)])
    for yard in data.yards:
        cx, cy = frame.px(geo.centroid(yard.outline.exterior))
        steps = [0.0, 2.2 * size, -2.2 * size, 4.4 * size]
        name = YARD_KIND_NAMES[yard.kind]
        sheet.label([(cx, cy - 1.0 + s, 0.0) for s in steps], name, size=size,
                    source=f"{yard.source}/kind", role="yard_kind", anchor="middle")
        sheet.label([(cx, cy + size + 1.0 + s, 0.0) for s in steps], format_feet(yard.depth_ft),
                    size=size, source=f"{yard.source}/depth_ft", role="yard_depth",
                    anchor="middle")


def _setbacks(sheet: Sheet, data: DrawingInput, frame: _Frame) -> None:
    if isinstance(data.setback_lines, LayerUnavailable):
        return
    size = TYPOGRAPHY.note_pt
    for entry in data.setback_lines:
        for line in entry.lines:
            sheet.line(polyline_data([frame.px(p) for p in line]), "setback_line",
                       [("data-source", entry.source)])
        first = entry.lines[0]  # has length (checked by the adapter)
        a, b = max(zip(first, first[1:], strict=False), key=lambda s: geo.edge_length(*s))
        pa, pb = frame.px(a), frame.px(b)
        length = math.hypot(pb[0] - pa[0], pb[1] - pa[1])
        n = (-(pb[1] - pa[1]) / length, (pb[0] - pa[0]) / length)
        candidates = _along(pa, pb, n, 1.0, size, 3) + _along(pa, pb, (-n[0], -n[1]), 1.0, size, 3)
        sheet.label(candidates, f"Setback, floor {format_number(entry.floor)}", size=size,
                    source=f"{entry.source}/floor", role="setback_floor", anchor="middle")


def _footprint(sheet: Sheet, data: DrawingInput, frame: _Frame) -> None:
    if isinstance(data.floor_plates, LayerUnavailable):
        return
    for plate in data.floor_plates:
        if plate.floor == 1:
            sheet.area(path_data(_px_rings(plate.outline, frame)), plate.use,
                       [("data-source", plate.source), ("data-floor", plate.floor)])


def _notes(data: DrawingInput) -> list[Note]:
    notes = scope_notes(data.scope) + case_notes(data.street_width_case)
    notes.append(Note((("Lot outline:", None),
                       (data.measurement_label, "/geometry/measurement/label"))))
    for yard in data.yards_not_required:
        notes.append(Note(((f"{YARD_KIND_NAMES[yard.kind]} not required:", None),
                           (yard.reason, f"{yard.source}/reason"))))
    for layer in (data.yards, data.setback_lines, data.floor_plates):
        if isinstance(layer, LayerUnavailable):
            notes.append(Note(((layer.reason, f"{layer.source}/reason"),)))
    return notes


def draw_site_plan(data: DrawingInput) -> Drawing:
    """The site plan drawing (SVG text, sourced labels, kinds drawn)."""
    frame = _frame(data.lot)
    sheet = Sheet()
    _footprint(sheet, data, frame)
    _yards(sheet, data, frame)
    _setbacks(sheet, data, frame)
    sheet.line(path_data(_px_rings(data.lot, frame)), "lot_line",
               [("fill-rule", "evenodd"), ("data-source", data.lot.source)])
    _dimensions(sheet, data, frame)
    _streets(sheet, data, frame)

    panel = north_arrow(PANEL_X + 20.0, 16.0)
    bar_parts, bar_labels = scale_bar(PANEL_X, 88.0, frame.k, 160.0)
    legend_parts, legend_bottom = legend(sheet.kinds, PANEL_X, 118.0)
    note_parts, note_labels, notes_bottom = notes_block(_notes(data), PANEL_X,
                                                        legend_bottom + 10.0, PANEL_W)
    height = max(CANVAS_H, notes_bottom + 12.0)
    body = sheet.parts + panel + bar_parts + legend_parts + note_parts
    svg = svg_document(width=CANVAS_W, height=height, drawing="site_plan", title="Site plan",
                       defs=hatch_defs(sheet.kinds), body=body)
    labels = tuple(sheet.labels + bar_labels + note_labels)
    return Drawing("site_plan", svg, labels, tuple(sheet.kinds))
