"""Reusable scene toolkit for the context drawings (M5-T155, scope correction 1).

The view-frame + projection math, the label-placement/collision helpers, the
clipped-geometry drawing, and the furniture/caption composition the three
context drawings share. `site_context_plan.py` holds the drawing-specific scene
logic and imports this toolkit; `block_map.py` and `neighbourhood_map.py` reuse
it through `site_context_plan`'s facade. Pure presentation (no shapely needed
here); coordinates are screen points unless noted.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from app.drawings.kit import geometry as geo
from app.drawings.kit.furniture import legend, legend_flow, notes_block, scale_bar
from app.drawings.kit.hatches import hatch_defs
from app.drawings.kit.labels import Box, text_box
from app.drawings.kit.sheet import Sheet
from app.drawings.kit.site_plan import STANDARD_SCALES_FT_PER_IN
from app.drawings.kit.styles import TYPOGRAPHY
from app.drawings.kit.svg import element, num, path_data, svg_document, text_element

from .errors import MapInputError
from .layout import (
    CANVAS_H,
    CANVAS_W,
    PANEL_W,
    PANEL_X,
    REPORT_CANVAS_W,
    REPORT_FURN_TOP,
    REPORT_LEGEND_X,
    REPORT_MAX_H_PT,
    REPORT_NORTH_CX,
    REPORT_SCALE_X,
    map_notes,
)
from .model import (
    BuildingLayer,
    Drawing,
    Label,
    MapContext,
    MapNote,
    Point,
    Polygon,
    StreetLayer,
    TaxLotLayer,
)
from .street_areas import clip_polygon_to_rect

__all__ = [
    "FRAME_INSET",
    "SUMMARY_CANVAS_W",
    "SUMMARY_FURN_TOP",
    "SUMMARY_MAX_H_PT",
    "SUMMARY_MAX_W_PT",
    "SUMMARY_NORTH_CX",
    "SUMMARY_PLAN",
    "SUMMARY_PLAN_MARGIN",
    "SUMMARY_SCALE_X",
    "TITLE_BAND_PT",
    "WIDE_CANVAS_W",
    "WIDE_FURN_TOP",
    "WIDE_MAX_H_PT",
    "WIDE_PLAN",
    "WIDE_PLAN_MARGIN",
    "Box",
    "ViewFrame",
    "box_crosses_lines",
    "box_in_rect",
    "caption_notes",
    "clearance",
    "compose_context",
    "draw_clipped_area",
    "draw_clipped_outline",
    "draw_frame",
    "fit_view",
    "line_candidates",
    "lot_bbox_touches",
    "network_candidates",
    "pad_box",
    "place",
    "point_inside",
    "project_polygon",
    "readable_angle",
    "screen_dir",
    "seg_foot",
    "segment_crosses_lines",
    "summary_notes",
    "viewport",
    "polyline_len",
]

POINTS_PER_INCH = 72.0
TITLE_BAND_PT = 30.0            # height reserved at the top of the region for the title
FRAME_INSET = 2.0              # the viewport is inset this far inside the plan region

# Compact SUMMARY frame: at most 88 mm (249.45 pt) by 72 mm (204.09 pt).
SUMMARY_MAX_W_PT = 249.4
SUMMARY_MAX_H_PT = 204.0
SUMMARY_CANVAS_W = 248.0
SUMMARY_PLAN = (3.0, 3.0, 245.0, 168.0)
SUMMARY_PLAN_MARGIN = 6.0
SUMMARY_FURN_TOP = 172.0
SUMMARY_NORTH_CX = 12.0
SUMMARY_SCALE_X = 34.0

# WIDE frame: a landscape strip, at most 182 mm (515.9 pt) by 105 mm (297.6 pt).
WIDE_MAX_H_PT = 297.6
WIDE_CANVAS_W = REPORT_CANVAS_W
WIDE_PLAN = (8.0, 8.0, 504.0, 246.0)
WIDE_PLAN_MARGIN = 30.0
WIDE_FURN_TOP = 250.0

_Box = tuple[float, float, float, float]


# --------------------------------------------------------------------------- #
# A view frame that can be ROTATED (so a street frontage runs horizontal).
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ViewFrame:
    """World (EPSG:2263) -> screen, scaled uniformly, y flipped, rotated by
    ``alpha`` so a chosen frontage runs horizontal. ``north_deg`` is the SVG
    rotation that turns an up-arrow to point at grid north under this rotation."""

    k: float
    cos: float
    sin: float
    minrx: float
    maxry: float
    ox: float
    oy: float
    north_deg: float

    def px(self, p: Point) -> Point:
        rx = p[0] * self.cos - p[1] * self.sin
        ry = p[0] * self.sin + p[1] * self.cos
        return self.ox + (rx - self.minrx) * self.k, self.oy + (self.maxry - ry) * self.k


def fit_view(
    window: _Box, region: _Box, margin: float, *, alpha: float = 0.0, top_band: float = 0.0,
    fill: bool = False,
) -> ViewFrame:
    """Fit ``window`` (its four corners, rotated by ``alpha``) into ``region`` at
    a STANDARD architectural/engineering scale, so the scale bar states a real
    1 in = S ft scale. Normally the LARGEST standard scale that fits; with
    ``fill`` the standard scale that FILLS the binding dimension (the window
    reaches the frame edge, the viewport clipping the slight overflow and the
    empty rotation corners). ``top_band`` reserves title height."""
    cos, sin = math.cos(alpha), math.sin(alpha)
    corners = [(window[0], window[1]), (window[2], window[1]),
               (window[2], window[3]), (window[0], window[3])]
    rot = [(x * cos - y * sin, x * sin + y * cos) for x, y in corners]
    rxs = [p[0] for p in rot]
    rys = [p[1] for p in rot]
    minrx, maxrx, minry, maxry = min(rxs), max(rxs), min(rys), max(rys)
    width, height = maxrx - minrx, maxry - minry
    if width <= 0.0 or height <= 0.0:
        raise MapInputError("empty_extent", "view window has no extent", location="/map_context")
    avail_w = (region[2] - region[0]) - 2 * margin
    avail_h = (region[3] - region[1]) - 2 * margin - top_band
    fit = min(avail_w / width, avail_h / height)
    candidates = [POINTS_PER_INCH / s for s in STANDARD_SCALES_FT_PER_IN]
    if fill:  # smallest standard scale that still reaches the frame (fills it)
        bigger = [c for c in candidates if c >= fit]
        k = min(bigger) if bigger else max(candidates)
    else:
        k = next((c for c in candidates if c <= fit), None)
    if k is None:
        raise MapInputError("view_too_large", "the view does not fit the largest standard scale",
                            location="/map_context")
    ox = region[0] + ((region[2] - region[0]) - width * k) / 2.0
    oy = region[1] + top_band + ((region[3] - region[1] - top_band) - height * k) / 2.0
    return ViewFrame(k, cos, sin, minrx, maxry, ox, oy, math.degrees(-alpha))


def viewport(region: _Box, top_band: float = TITLE_BAND_PT) -> _Box:
    """The clean rectangular drawing frame inside ``region``: inset on every
    side, with ``top_band`` reserved at the top. Everything is clipped to it."""
    return (region[0] + FRAME_INSET, region[1] + top_band,
            region[2] - FRAME_INSET, region[3] - FRAME_INSET)


def pad_box(box: _Box, pad: float) -> _Box:
    return box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad


def point_inside(box: _Box, p: Point) -> bool:
    return box[0] <= p[0] <= box[2] and box[1] <= p[1] <= box[3]


# --------------------------------------------------------------------------- #
# Small geometry helpers (screen space).
# --------------------------------------------------------------------------- #
def seg_foot(p: Point, a: Point, b: Point) -> tuple[float, Point]:
    dx, dy = b[0] - a[0], b[1] - a[1]
    length_sq = dx * dx + dy * dy
    if length_sq == 0.0:
        return math.hypot(p[0] - a[0], p[1] - a[1]), a
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / length_sq))
    foot = (a[0] + t * dx, a[1] + t * dy)
    return math.hypot(p[0] - foot[0], p[1] - foot[1]), foot


def screen_dir(wx: float, wy: float, nout_world: Point, fr: ViewFrame) -> Point:
    pm = fr.px((wx, wy))
    pt = fr.px((wx + nout_world[0], wy + nout_world[1]))
    dx, dy = pt[0] - pm[0], pt[1] - pm[1]
    length = math.hypot(dx, dy) or 1.0
    return (dx / length, dy / length)


def polyline_len(coords: Sequence[Point]) -> float:
    return sum(geo.edge_length(a, b) for a, b in zip(coords, coords[1:], strict=False))


def readable_angle(angle_deg: float) -> float:
    if angle_deg >= 90.0:
        return angle_deg - 180.0
    if angle_deg < -90.0:
        return angle_deg + 180.0
    return angle_deg


def box_in_rect(box: Box, rect: _Box) -> bool:
    return box.x0 >= rect[0] and box.y0 >= rect[1] and box.x1 <= rect[2] and box.y1 <= rect[3]


def clearance(p: Point, own, all_lines) -> float:
    best = 1e9
    for line in all_lines:
        if line is own:
            continue
        for a, b in zip(line, line[1:], strict=False):
            d, _f = seg_foot(p, a, b)
            best = min(best, d)
    return best


def _seg_len_in_rect(a: Point, b: Point, x0, y0, x1, y1) -> float:
    """Length of segment ab inside the axis-aligned rect (Liang-Barsky clip)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, a[0] - x0), (dx, x1 - a[0]), (-dy, a[1] - y0), (dy, y1 - a[1])):
        if p == 0.0:
            if q < 0.0:
                return 0.0
        else:
            r = q / p
            if p < 0.0:
                if r > t1:
                    return 0.0
                t0 = max(t0, r)
            else:
                if r < t0:
                    return 0.0
                t1 = min(t1, r)
    return math.hypot(dx, dy) * (t1 - t0) if t1 > t0 else 0.0


def _seg_cross(a: Point, b: Point, c: Point, d: Point) -> bool:
    """A proper crossing of segments ab and cd (interiors meet)."""
    def ccw(p, q, r):
        return (r[1] - p[1]) * (q[0] - p[0]) - (q[1] - p[1]) * (r[0] - p[0])
    return (ccw(c, d, a) > 0) != (ccw(c, d, b) > 0) and (ccw(a, b, c) > 0) != (ccw(a, b, d) > 0)


def segment_crosses_lines(a: Point, b: Point, named_lines) -> bool:
    """Whether the leader segment ab crosses ANY street centre line (used so the
    'Subject lot' leader never crosses a street)."""
    for _name, line in named_lines:
        for c, d in zip(line, line[1:], strict=False):
            if _seg_cross(a, b, c, d):
                return True
    return False


def box_crosses_lines(box: Box, named_lines, own: str | None, pad: float = 0.0,
                      max_len: float = 0.0) -> bool:
    """Whether the label ``box`` is OVERLAPPED by a street (name != ``own``) for
    more than ``max_len`` points - i.e. that street RUNS ALONG the label, not just
    crosses it perpendicularly at an intersection. A lot/mark label passes
    ``own=None`` and ``max_len`` small (it may not touch any street); a street
    name allows a perpendicular crossing of a DIFFERENT street but not running
    along it."""
    x0, y0, x1, y1 = box.x0 - pad, box.y0 - pad, box.x1 + pad, box.y1 + pad
    for name, line in named_lines:
        if own is not None and name == own:
            continue
        inside = 0.0
        for a, b in zip(line, line[1:], strict=False):
            inside += _seg_len_in_rect(a, b, x0, y0, x1, y1)
            if inside > max_len:
                return True
    return False


# --------------------------------------------------------------------------- #
# Label placement (drop a label rather than overlap/cross -> clean frames).
# --------------------------------------------------------------------------- #
def place(sheet: Sheet, candidates, text, *, size, source, role, anchor="start", style=None,
          rect: _Box | None = None, pad: float = 1.0, avoid_lines=None, own: str | None = None,
          avoid_boxes=(), cross_max_len: float = 1.0) -> Box | None:
    """Place ``text`` at the first candidate whose box (a) is inside ``rect``,
    (b) does not overlap a placed label or any box in ``avoid_boxes``, and (c) is
    not run along by a street in ``avoid_lines`` other than ``own`` for more than
    ``cross_max_len`` points. Returns the placed Box, or ``None`` (dropped)."""
    for x, y, rot in candidates:
        box = text_box(x, y, text, size, anchor, rot)
        if rect is not None and not box_in_rect(box, rect):
            continue
        if any(box.overlaps(other, pad) for other in sheet.boxes):
            continue
        if any(box.overlaps(other, pad) for other in avoid_boxes):
            continue
        if avoid_lines is not None and box_crosses_lines(box, avoid_lines, own, pad=0.5,
                                                         max_len=cross_max_len):
            continue
        sheet.label([(x, y, rot)], text, size=size, source=source, role=role, anchor=anchor,
                    style=style)
        return box
    return None


def line_candidates(poly: Sequence[Point], size: float):
    """Candidate label spots sampled along the whole projected polyline (several
    points, each on the line and to either side)."""
    segs = [(a, b) for a, b in zip(poly, poly[1:], strict=False) if geo.edge_length(a, b) > 1e-6]
    if not segs:
        return [(poly[0][0], poly[0][1], 0.0)]
    lengths = [geo.edge_length(a, b) for a, b in segs]
    total = sum(lengths) or 1.0
    out = []
    for frac in (0.5, 0.4, 0.6, 0.3, 0.7, 0.2, 0.8):
        target, acc = frac * total, 0.0
        for (a, b), seg_len in zip(segs, lengths, strict=False):
            if acc + seg_len >= target or (a, b) == segs[-1]:
                t = (target - acc) / seg_len if seg_len else 0.0
                mid = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                ux, uy = (b[0] - a[0]) / seg_len, (b[1] - a[1]) / seg_len
                n = (-uy, ux)
                ang = readable_angle(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])))
                for off, d in ((0.0, n), (size + 2.0, n), (size + 2.0, (-n[0], -n[1]))):
                    out.append((mid[0] + d[0] * off, mid[1] + d[1] * off, ang))
                break
            acc += seg_len
    return out


def network_candidates(piece, all_lines, size):
    """Candidates along ``piece`` ordered by clearance from OTHER streets, so the
    name lands on an open stretch, not at an intersection."""
    segs = [(a, b) for a, b in zip(piece, piece[1:], strict=False) if geo.edge_length(a, b) > 1e-6]
    if not segs:
        return []
    lengths = [geo.edge_length(a, b) for a, b in segs]
    total = sum(lengths) or 1.0
    scored = []
    for frac in [i / 20.0 for i in range(2, 19)]:
        target, acc = frac * total, 0.0
        for (a, b), seg_len in zip(segs, lengths, strict=False):
            if acc + seg_len >= target or (a, b) == segs[-1]:
                t = (target - acc) / seg_len if seg_len else 0.0
                mid = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                ang = readable_angle(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])))
                scored.append((clearance(mid, piece, all_lines), mid, ang))
                break
            acc += seg_len
    scored.sort(key=lambda s: -s[0])
    out = []
    for _clear, mid, ang in scored:
        ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        n = (-uy, ux)
        for off in (size + 1.0, -(size + 1.0)):
            out.append((mid[0] + n[0] * off, mid[1] + n[1] * off, ang))
    return out


# --------------------------------------------------------------------------- #
# Projection + clipped drawing.
# --------------------------------------------------------------------------- #
def project_polygon(polygon: Polygon, fr: ViewFrame):
    return [[fr.px(p) for p in ring] for ring in polygon.rings]


def draw_clipped_area(sheet: Sheet, rings, kind: str, source: str, rect: _Box) -> None:
    for poly in clip_polygon_to_rect([tuple(r) for r in rings], rect):
        sheet.area(path_data(poly), kind, [("data-source", source)])


def draw_clipped_outline(sheet: Sheet, rings, kind: str, source: str, rect: _Box) -> None:
    for poly in clip_polygon_to_rect([tuple(r) for r in rings], rect):
        sheet.line(path_data(poly), kind, [("fill-rule", "evenodd"), ("data-source", source)])


def lot_bbox_touches(polygon: Polygon, fr: ViewFrame, rect: _Box) -> bool:
    xs = [fr.px(p)[0] for p in polygon.exterior]
    ys = [fr.px(p)[1] for p in polygon.exterior]
    return not (max(xs) < rect[0] or min(xs) > rect[2] or max(ys) < rect[1] or min(ys) > rect[3])


def draw_frame(sheet: Sheet, rect: _Box) -> None:
    """A thin border around the drawing viewport."""
    sheet.parts.append(element("rect", [
        ("x", rect[0]), ("y", rect[1]), ("width", rect[2] - rect[0]), ("height", rect[3] - rect[1]),
        ("fill", "none"), ("stroke", "#C9CFD4"), ("stroke-width", 0.75),
        ("data-role", "frame")]))


# --------------------------------------------------------------------------- #
# Caption + composition.
# --------------------------------------------------------------------------- #
def _attr_note(attribution: MapNote, edited: str | None) -> MapNote:
    if edited and edited not in attribution.text:
        return MapNote(f"{attribution.text} Source edit date {edited}.", attribution.source)
    return attribution


def caption_notes(context: MapContext, *, layers: set[str], gaps_note: bool = False,
                  frontage: str | None = None, frontage_source: str | None = None):
    """The sources-and-dates caption returned to the caller (ruling Y7; S5)."""
    notes = [MapNote(context.measurement_label, context.measurement_source)]
    if "tax_lots" in layers and isinstance(context.tax_lots, TaxLotLayer):
        notes.append(_attr_note(context.tax_lots.attribution, context.tax_lots.edited))
    if "streets" in layers and isinstance(context.streets, StreetLayer):
        notes.append(_attr_note(context.streets.attribution, context.streets.edited))
    if "buildings" in layers and isinstance(context.buildings, BuildingLayer):
        notes.append(_attr_note(context.buildings.attribution, context.buildings.edited))
    if frontage is not None and frontage_source is not None:
        notes.append(MapNote(f"Rotated to the {frontage} frontage.", frontage_source))
    if gaps_note:
        notes.append(MapNote("Street areas are drawn from the gaps between the tax lots.",
                             "/map_context/tax_lots"))
    notes.append(MapNote(
        "Map geometry only; tax boundaries do not establish the legal zoning lot; "
        "nothing is surveyed.", "/map_context/subject_lot"))
    return notes


def summary_notes(frontage: str | None) -> list[MapNote]:
    """SHORT plain sentences for the caller to caption the summary/wide frame (no
    source names, dates or dataset ids - the report composes those)."""
    notes = []
    if frontage is not None:
        notes.append(MapNote(f"Rotated to the {frontage} frontage.", "/map_context/subject_lot"))
    notes.append(MapNote("Map geometry only; tax boundaries do not establish the legal zoning "
                         "lot; nothing is surveyed.", "/map_context/subject_lot"))
    return notes


def _north(cx: float, top: float, deg: float, *, caption: bool = True,
           half: float = 18.0) -> tuple[list[str], float]:
    """A grid-north arrow that rotates to point at grid north, with the 'Grid
    north' caption kept HORIZONTAL. ``caption=False`` and a smaller ``half`` give
    the compact arrow. Returns the parts and the bottom y."""
    cy = top + half + 10.0
    size = TYPOGRAPHY.label_pt
    arrow = element("path", [
        ("d", f"M{num(cx)} {num(cy - half)} L{num(cx + 7.0)} {num(cy + half)} "
              f"L{num(cx)} {num(cy + half / 2.0)} L{num(cx - 7.0)} {num(cy + half)} Z"),
        ("fill", "#000000"), ("stroke", "#000000"), ("stroke-width", 0.5)])
    transform = f' transform="rotate({num(deg)} {num(cx)} {num(cy)})"' if abs(deg) >= 1e-9 else ""
    parts = [
        f'<g data-role="north-arrow"{transform}>', arrow,
        text_element(cx, cy - half - 4.0, "N", size=size + 2, source=None, role="furniture",
                     anchor="middle", weight="bold"), "</g>"]
    bottom = cy + half + 2.0
    if caption:
        caption_y = cy + 28.0
        parts.append(text_element(cx - 2.0, caption_y, "Grid north", size=size, source=None,
                                  role="furniture"))
        bottom = caption_y + 2.0
    return parts, bottom


def compose_context(drawing: str, title: str, sheet: Sheet, frame: ViewFrame,
                    notes: Sequence[MapNote], *, mode: str = "sheet") -> Drawing:
    """Assemble the scene plus the furniture (north arrow rotated to grid north).
    ``mode`` is 'report', 'sheet', 'summary' or 'wide'."""
    if mode == "summary":
        panel, north_bottom = _north(SUMMARY_NORTH_CX, SUMMARY_FURN_TOP, frame.north_deg,
                                     caption=False, half=9.0)
        bar_parts, bar_labels = scale_bar(SUMMARY_SCALE_X, SUMMARY_FURN_TOP + 10.0, frame.k, 80.0)
        height = min(SUMMARY_MAX_H_PT, max(north_bottom, SUMMARY_FURN_TOP + 26.0) + 4.0)
        body = sheet.parts + panel + bar_parts
        svg = svg_document(width=SUMMARY_CANVAS_W, height=height, drawing=drawing, title=title,
                           defs=hatch_defs(sheet.kinds), body=body)
        note_labels = [Label(n.text, n.source, "note") for n in notes]
        return Drawing(drawing, svg, tuple(sheet.labels + bar_labels + note_labels),
                       tuple(sheet.kinds))
    if mode == "wide":
        panel, north_bottom = _north(REPORT_NORTH_CX, WIDE_FURN_TOP, frame.north_deg,
                                     caption=False, half=10.0)
        bar_parts, bar_labels = scale_bar(REPORT_SCALE_X, WIDE_FURN_TOP + 14.0, frame.k, 100.0)
        legend_parts, legend_bottom = legend_flow(
            sheet.kinds, REPORT_LEGEND_X, WIDE_FURN_TOP, WIDE_CANVAS_W - REPORT_LEGEND_X - 8.0)
        height = min(WIDE_MAX_H_PT, max(north_bottom, legend_bottom, WIDE_FURN_TOP + 28.0) + 6.0)
        body = sheet.parts + panel + bar_parts + legend_parts
        svg = svg_document(width=WIDE_CANVAS_W, height=height, drawing=drawing, title=title,
                           defs=hatch_defs(sheet.kinds), body=body)
        note_labels = [Label(n.text, n.source, "note") for n in notes]
        return Drawing(drawing, svg, tuple(sheet.labels + bar_labels + note_labels),
                       tuple(sheet.kinds))
    if mode == "report":
        panel, north_bottom = _north(REPORT_NORTH_CX, REPORT_FURN_TOP, frame.north_deg)
        bar_parts, bar_labels = scale_bar(REPORT_SCALE_X, REPORT_FURN_TOP + 16.0, frame.k, 150.0)
        legend_parts, legend_bottom = legend_flow(
            sheet.kinds, REPORT_LEGEND_X, REPORT_FURN_TOP, REPORT_CANVAS_W - REPORT_LEGEND_X - 8.0)
        furn_bottom = max(north_bottom, legend_bottom, REPORT_FURN_TOP + 46.0)
        height = min(REPORT_MAX_H_PT, furn_bottom + 8.0)
        body = sheet.parts + panel + bar_parts + legend_parts
        svg = svg_document(width=REPORT_CANVAS_W, height=height, drawing=drawing, title=title,
                           defs=hatch_defs(sheet.kinds), body=body)
        note_labels = [Label(n.text, n.source, "note") for n in notes]
        return Drawing(drawing, svg, tuple(sheet.labels + bar_labels + note_labels),
                       tuple(sheet.kinds))
    panel, north_bottom = _north(PANEL_X + 20.0, 16.0, frame.north_deg)
    bar_parts, bar_labels = scale_bar(PANEL_X, 88.0, frame.k, 160.0)
    legend_parts, legend_bottom = legend(sheet.kinds, PANEL_X, 118.0)
    note_parts, note_labels, notes_bottom = notes_block(
        map_notes(notes), PANEL_X, legend_bottom + 10.0, PANEL_W)
    height = max(CANVAS_H, notes_bottom + 12.0, north_bottom + 12.0)
    body = sheet.parts + panel + bar_parts + legend_parts + note_parts
    svg = svg_document(width=CANVAS_W, height=height, drawing=drawing, title=title,
                       defs=hatch_defs(sheet.kinds), body=body)
    return Drawing(drawing, svg, tuple(sheet.labels + bar_labels + note_labels),
                   tuple(sheet.kinds))
