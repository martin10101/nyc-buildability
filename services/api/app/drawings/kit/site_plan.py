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
from .furniture import (
    Note,
    case_notes,
    legend,
    legend_flow,
    north_arrow,
    notes_block,
    scale_bar,
    scope_notes,
)
from .hatches import hatch_defs
from .labels import YARD_KIND_NAMES, Box, format_feet, format_number
from .model import Drawing, DrawingInput, Label, LayerUnavailable, Point, Polygon
from .sheet import Sheet
from .styles import TYPOGRAPHY, style_for
from .svg import element, path_data, polyline_data, svg_document, text_element

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

# Report frame (ruling X9 a): sized for A4 at 14 mm margins - at most 182 mm wide by 150 mm high;
# 1 user unit = 1 pt, so 182 mm = 515.91 pt and 150 mm = 425.20 pt. No notes column (the evidence
# page carries provenance); the plan fills the top, a compact furniture strip sits below.
REPORT_MAX_W_PT = 515.9
REPORT_MAX_H_PT = 425.2
REPORT_CANVAS_W = 512.0
REPORT_PLAN = (8.0, 8.0, 504.0, 346.0)  # the plan region in the report frame
REPORT_PLAN_MARGIN = 46.0
REPORT_FURN_TOP = 356.0
REPORT_NORTH_CX = 24.0
REPORT_SCALE_X = 58.0
REPORT_LEGEND_X = 180.0
REPORT_TOP_BIAS = 14.0  # shift the lot down so the top street label clears the viewBox top (K5)

# Summary frame (ruling K3): the decision summary's small visual - at most 85 mm by 85 mm
# (85 mm = 240.94 pt; 1 user unit = 1 pt). Only the lot outline, the street names beside their
# frontages, the frontage lengths (not every edge), a north arrow and a scale bar; no legend, no
# notes. Every label at least 7 pt.
SUMMARY_MAX_PT = 240.9
SUMMARY_CANVAS_W = 238.0
SUMMARY_PLAN = (6.0, 4.0, 232.0, 182.0)
SUMMARY_PLAN_MARGIN = 34.0
SUMMARY_TOP_BIAS = 10.0  # shift the lot down so the top street label clears the viewBox top (K5)
SUMMARY_NORTH_CX = 20.0
SUMMARY_SCALE_X = 56.0


@dataclass(frozen=True)
class _Frame:
    k: float  # drawing points per foot
    ox: float
    oy: float
    minx: float
    maxy: float

    def px(self, p: Point) -> Point:
        return self.ox + (p[0] - self.minx) * self.k, self.oy + (self.maxy - p[1]) * self.k


def _frame(
    lot: Polygon,
    region: tuple[float, float, float, float] = PLAN,
    margin: float = PLAN_MARGIN,
    top_bias: float = 0.0,
) -> _Frame:
    minx, miny, maxx, maxy = geo.bbox(lot.exterior)
    width, height = maxx - minx, maxy - miny
    avail_w = (region[2] - region[0]) - 2 * margin
    avail_h = (region[3] - region[1]) - 2 * margin
    fit = min(avail_w / width, avail_h / height)
    k = next((POINTS_PER_INCH / s for s in STANDARD_SCALES_FT_PER_IN
              if POINTS_PER_INCH / s <= fit), None)
    if k is None:
        raise DrawingInputError("lot_too_large", "lot does not fit the largest plan scale",
                                location=lot.source)
    ox = region[0] + ((region[2] - region[0]) - width * k) / 2.0
    # ``top_bias`` shifts the lot DOWN within the region (the small report/summary frames keep more
    # room above the lot for a long top-frontage street label, so no label is clipped - K5).
    oy = region[1] + ((region[3] - region[1]) - height * k) / 2.0 + top_bias
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


def _reserve_seg(sheet: Sheet, p: Point, q: Point) -> None:
    """Reserve the bounding box of one drawn segment (a dimension tick or line) so that no label is
    placed over it (the collision check now covers labels against dimension ticks and lines, K2)."""
    sheet.reserve(Box(min(p[0], q[0]), min(p[1], q[1]), max(p[0], q[0]), max(p[1], q[1])))


def _leader(sheet: Sheet, start: Point, box: Box) -> None:
    """A thin leader from a short edge's dimension line to its label, stopping just short of the
    label box so it points at the label without touching it (K2)."""
    cx, cy = (box.x0 + box.x1) / 2.0, (box.y0 + box.y1) / 2.0
    dx, dy = cx - start[0], cy - start[1]
    dist = math.hypot(dx, dy) or 1.0
    # stop 3 pt before the box edge along the line to the box centre
    reach = max(0.0, dist - max(box.x1 - box.x0, box.y1 - box.y0) / 2.0 - 3.0)
    end = (start[0] + dx / dist * reach, start[1] + dy / dist * reach)
    sheet.parts.append(element("path", [("d", polyline_data([start, end])), ("fill", "none"),
                                        ("stroke", style_for("dimension").outline),
                                        ("stroke-width", 0.4), ("data-role", "dimension-leader")]))


def _dimensions(sheet: Sheet, data: DrawingInput, frame: _Frame) -> None:
    ring = data.lot.exterior
    area = geo.signed_area(ring)
    dim = style_for("dimension")
    sheet.use_kind("dimension")
    size = TYPOGRAPHY.dimension_pt
    # Pass 1: draw every edge's dimension geometry (extension lines, ticks, dimension line) and
    # reserve each segment, so pass 2 can place labels clear of ALL ticks and lines (K2).
    placements: list[tuple] = []
    for i, (a, b) in enumerate(geo.edges(ring)):
        nx, ny = geo.outward_normal(a, b, area)
        n = (nx, -ny)  # drawing y points down
        pa, pb = frame.px(a), frame.px(b)
        length = math.hypot(pb[0] - pa[0], pb[1] - pa[1])
        u = ((pb[0] - pa[0]) / length, (pb[1] - pa[1]) / length)
        tick = ((u[0] + n[0]) * 2.2, (u[1] + n[1]) * 2.2)
        segs = []
        drawn: list[tuple[Point, Point]] = []
        for p in (pa, pb):
            base = (p[0] + n[0] * 2.0, p[1] + n[1] * 2.0)
            end = (p[0] + n[0] * (DIM_OFFSET + 3.0), p[1] + n[1] * (DIM_OFFSET + 3.0))
            on = (p[0] + n[0] * DIM_OFFSET, p[1] + n[1] * DIM_OFFSET)
            t0 = (on[0] - tick[0], on[1] - tick[1])
            t1 = (on[0] + tick[0], on[1] + tick[1])
            segs.append(polyline_data([base, end]))
            segs.append(polyline_data([t0, t1]))
            drawn += [(base, end), (t0, t1)]
        da = (pa[0] + n[0] * DIM_OFFSET, pa[1] + n[1] * DIM_OFFSET)
        db = (pb[0] + n[0] * DIM_OFFSET, pb[1] + n[1] * DIM_OFFSET)
        segs.append(polyline_data([da, db]))
        drawn.append((da, db))
        sheet.parts.append(element("path", [("d", " ".join(segs)), ("fill", "none"),
                                            ("stroke", dim.outline),
                                            ("stroke-width", float(dim.line_weight_pt)),
                                            ("data-role", "dimension-geometry")]))
        for p, q in drawn:
            _reserve_seg(sheet, p, q)
        placements.append((i, pa, pb, n, da, db, length))
    # Pass 2: place each label at the first candidate clear of every reserved tick, line and label.
    # A SHORT edge (shorter than its own label) steps further out and draws a leader to the label.
    for i, pa, pb, n, da, db, length in placements:
        text = format_feet(geo.edge_length(ring[i], ring[i + 1]))
        short = length < len(text) * size * TYPOGRAPHY.char_width_em
        candidates = _along(pa, pb, n, DIM_OFFSET, size, 12 if short else 6)
        box = sheet.label(candidates, text, size=size, source=f"edge:{data.lot.source}/0#{i}",
                          role="dimension", anchor="middle")
        if short:
            _leader(sheet, ((da[0] + db[0]) / 2.0, (da[1] + db[1]) / 2.0), box)


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


def draw_site_plan(data: DrawingInput, *, frame: str = "sheet") -> Drawing:
    """The site plan drawing (SVG text, sourced labels, kinds drawn).

    ``frame='sheet'`` (default) is today's full sheet, byte-identical to the committed snapshots.
    ``frame='report'`` is the A4 report composition (ruling X9 a): the same drawn lot, dimensions
    and street names, but no notes column, a compact legend, sized at most 182 mm by 150 mm with
    every label at least 7 pt at that size. ``frame='summary'`` (ruling K3) is the decision
    summary's small visual: the lot outline, the street names and frontage lengths only, north and
    scale bar, at most 85 mm by 85 mm."""
    if frame == "summary":
        return _draw_summary(data)
    report = frame == "report"
    fr = (_frame(data.lot, REPORT_PLAN, REPORT_PLAN_MARGIN, REPORT_TOP_BIAS) if report
          else _frame(data.lot))
    sheet = Sheet()
    _footprint(sheet, data, fr)
    _yards(sheet, data, fr)
    _setbacks(sheet, data, fr)
    sheet.line(path_data(_px_rings(data.lot, fr)), "lot_line",
               [("fill-rule", "evenodd"), ("data-source", data.lot.source)])
    _dimensions(sheet, data, fr)
    _streets(sheet, data, fr)

    if report:
        return _compose_report(sheet, fr, data)

    panel = north_arrow(PANEL_X + 20.0, 16.0)
    bar_parts, bar_labels = scale_bar(PANEL_X, 88.0, fr.k, 160.0)
    legend_parts, legend_bottom = legend(sheet.kinds, PANEL_X, 118.0)
    note_parts, note_labels, notes_bottom = notes_block(_notes(data), PANEL_X,
                                                        legend_bottom + 10.0, PANEL_W)
    height = max(CANVAS_H, notes_bottom + 12.0)
    body = sheet.parts + panel + bar_parts + legend_parts + note_parts
    svg = svg_document(width=CANVAS_W, height=height, drawing="site_plan", title="Site plan",
                       defs=hatch_defs(sheet.kinds), body=body)
    labels = tuple(sheet.labels + bar_labels + note_labels)
    return Drawing("site_plan", svg, labels, tuple(sheet.kinds))


def _compose_report(sheet: Sheet, fr: _Frame, data: DrawingInput) -> Drawing:
    """Assemble the report-frame site plan: the plan ``sheet`` plus a compact furniture strip
    (north arrow, scale bar, legend) below it - no notes column (ruling X9 a). A single caption
    line names the outline's basis in plain words (the results' measurement label; ruling K4).
    Sized at most 182 mm by 150 mm; every label at least 7 pt at that size."""
    panel = north_arrow(REPORT_NORTH_CX, REPORT_FURN_TOP)
    bar_parts, bar_labels = scale_bar(REPORT_SCALE_X, REPORT_FURN_TOP + 16.0, fr.k, 150.0)
    legend_parts, legend_bottom = legend_flow(
        sheet.kinds, REPORT_LEGEND_X, REPORT_FURN_TOP, REPORT_CANVAS_W - REPORT_LEGEND_X - 8.0)
    north_bottom = REPORT_FURN_TOP + 46.0
    caption_y = max(north_bottom, legend_bottom) + 12.0
    caption_text = f"Lot outline: {data.measurement_label}"
    caption = text_element(REPORT_NORTH_CX - 4.0, caption_y, caption_text,
                           size=TYPOGRAPHY.note_pt, source="/geometry/measurement/label",
                           role="caption")
    caption_label = Label(caption_text, "/geometry/measurement/label", "caption")
    height = min(REPORT_MAX_H_PT, caption_y + 8.0)
    body = sheet.parts + panel + bar_parts + legend_parts + [caption]
    svg = svg_document(width=REPORT_CANVAS_W, height=height, drawing="site_plan",
                       title="Site plan", defs=hatch_defs(sheet.kinds), body=body)
    return Drawing("site_plan", svg, tuple(sheet.labels + bar_labels + [caption_label]),
                   tuple(sheet.kinds))


def _close(a: Point, b: Point, tol: float = 0.05) -> bool:
    return abs(a[0] - b[0]) <= tol and abs(a[1] - b[1]) <= tol


def _frontage_edge_indices(data: DrawingInput) -> set[int]:
    """The lot-outline edge indices that carry a street frontage (so the summary dimensions only
    the frontage edges, not every edge). A frontage line's points are lot-outline vertices, so each
    frontage segment matches one ring edge."""
    ring = [tuple(p) for p in data.lot.exterior]
    found: set[int] = set()
    for street in data.streets:
        pts = [tuple(p) for p in street.frontage]
        for p, q in zip(pts, pts[1:], strict=False):
            for i in range(len(ring) - 1):
                a, b = ring[i], ring[i + 1]
                if (_close(a, p) and _close(b, q)) or (_close(a, q) and _close(b, p)):
                    found.add(i)
                    break
    return found


def _summary_frontages(sheet: Sheet, data: DrawingInput, fr: _Frame) -> None:
    """Draw the frontage lengths (frontage edges only) and the street names beside their
    frontages, for the summary frame."""
    ring = data.lot.exterior
    area = geo.signed_area(ring)
    size = TYPOGRAPHY.label_pt
    for i in sorted(_frontage_edge_indices(data)):
        a, b = ring[i], ring[i + 1]
        nx, ny = geo.outward_normal(a, b, area)
        n = (nx, -ny)
        sheet.label(_along(fr.px(a), fr.px(b), n, 6.0, size, 6), format_feet(geo.edge_length(a, b)),
                    size=size, source=f"edge:{data.lot.source}/0#{i}", role="dimension",
                    anchor="middle")
    for street in data.streets:
        pairs = list(zip(street.frontage, street.frontage[1:], strict=False))
        a, b = max(pairs, key=lambda s: geo.edge_length(*s))
        length = geo.edge_length(a, b)
        n_ft = ((b[1] - a[1]) / length, -(b[0] - a[0]) / length)
        eps = min(0.5, length * 0.01)
        probe = ((a[0] + b[0]) / 2 + n_ft[0] * eps, (a[1] + b[1]) / 2 + n_ft[1] * eps)
        if geo.point_location(probe, data.lot.exterior) == "inside":
            n_ft = (-n_ft[0], -n_ft[1])
        n = (n_ft[0], -n_ft[1])
        sheet.label(_along(fr.px(a), fr.px(b), n, 18.0, size, 6), street.name, size=size,
                    source=f"{street.source}/street", role="street", anchor="middle",
                    style="italic")


def _draw_summary(data: DrawingInput) -> Drawing:
    """The summary-frame site plan (ruling K3): the lot outline, the street names beside their
    frontages, the frontage lengths only, a north arrow and a scale bar - at most 85 mm by 85 mm,
    every label at least 7 pt. No legend, no notes."""
    fr = _frame(data.lot, SUMMARY_PLAN, SUMMARY_PLAN_MARGIN, SUMMARY_TOP_BIAS)
    sheet = Sheet()
    sheet.line(path_data(_px_rings(data.lot, fr)), "lot_line",
               [("fill-rule", "evenodd"), ("data-source", data.lot.source)])
    _summary_frontages(sheet, data, fr)
    # Compose tightly (K6): put the north arrow and scale bar immediately beneath the drawn content
    # (the lot and its labels), so there is no empty band between the plan and the furniture.
    lot_bottom = max(y for _, y in (fr.px(p) for p in data.lot.exterior))
    content_bottom = max([lot_bottom, *(box.y1 for box in sheet.boxes)])
    furn_top = content_bottom + 10.0
    panel = north_arrow(SUMMARY_NORTH_CX, furn_top)
    bar_parts, bar_labels = scale_bar(SUMMARY_SCALE_X, furn_top + 14.0, fr.k, 86.0)
    height = min(SUMMARY_MAX_PT, furn_top + 46.0 + 6.0)
    body = sheet.parts + panel + bar_parts
    svg = svg_document(width=SUMMARY_CANVAS_W, height=height, drawing="site_plan",
                       title="Site plan", defs=hatch_defs(sheet.kinds), body=body)
    return Drawing("site_plan", svg, tuple(sheet.labels + bar_labels), tuple(sheet.kinds))
