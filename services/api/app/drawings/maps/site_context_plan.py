"""The site plan among its surroundings (M5-T155, D-090 R936-R938).

The owner looked at the old site drawing - the lot's outline alone on a blank
page - and said it was "a rectangle on an angle" with "no reference to where he
is". This draws what the competitor's site/location pages draw, reading cleanly
on the REAL recorded tax map (hundreds of neighbouring lots):

* the subject lot clearly coloured, with its edge lengths;
* its immediate neighbours (the lots that share an edge with it) labelled
  "Lot <n>" + address; every OTHER lot a thin light outline, unlabelled;
* existing building footprints as light grey fills;
* the streets as the even open space between the tax lots across the whole frame,
  each named in CAPITALS with its mapped width, centred in the street;
* rotated so the lot's main street frontage runs horizontal with that street at
  the top; the north arrow then shows true grid north and the caption says so.

Everything is clipped to a clean rectangular viewport (an architect's drawing
frame): lots, buildings and streets are cut at the frame edge, nothing floats
outside it, and only the furniture (north arrow, scale bar, legend) sits below.
No law is computed or drawn (ruling Y6/Y8). The caption returned to the caller
names every source and its date.

This module also carries the shared scene helpers the block close-up and the
neighbourhood map reuse. Coordinates are EPSG:2263 US survey feet; nothing is
reprojected; the output is byte-deterministic (S8).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from shapely import make_valid
from shapely.geometry import LineString
from shapely.geometry import Polygon as ShapelyPolygon

from app.drawings.kit import geometry as geo
from app.drawings.kit.furniture import legend, legend_flow, notes_block, scale_bar
from app.drawings.kit.hatches import hatch_defs
from app.drawings.kit.labels import Box, format_feet, format_number, text_box
from app.drawings.kit.sheet import Sheet
from app.drawings.kit.site_plan import STANDARD_SCALES_FT_PER_IN
from app.drawings.kit.styles import TYPOGRAPHY
from app.drawings.kit.svg import (
    element,
    num,
    path_data,
    polyline_data,
    svg_document,
    text_element,
)

from .errors import MapInputError
from .layout import (
    CANVAS_H,
    CANVAS_W,
    PANEL_W,
    PANEL_X,
    PLAN,
    PLAN_MARGIN,
    REPORT_CANVAS_W,
    REPORT_FURN_TOP,
    REPORT_LEGEND_X,
    REPORT_MAX_H_PT,
    REPORT_NORTH_CX,
    REPORT_PLAN,
    REPORT_PLAN_MARGIN,
    REPORT_SCALE_X,
    map_notes,
)
from .model import (
    BuildingLayer,
    Drawing,
    Label,
    LayerUnavailable,
    MapContext,
    MapNote,
    NeighbourLot,
    Point,
    Polygon,
    StreetLayer,
    SubjectLot,
    TaxLotLayer,
    Unavailable,
)
from .street_areas import (
    MIN_STREET_AREA_SQFT,
    clip_polygon_to_rect,
    clip_polyline_to_rect,
    gaps_in_rect,
)

__all__ = [
    "SITE_PAD_FT",
    "SITE_STREET_REACH_FT",
    "ViewFrame",
    "caption_notes",
    "compose_context",
    "draw_block_scene",
    "draw_neighbourhood_scene",
    "draw_site_context_plan",
    "edge_sharing_lots",
    "fit_view",
    "frontage_rotation",
    "site_context_view",
    "subtitle_from_bbl",
    "unavailable_layer",
    "viewport",
]

POINTS_PER_INCH = 72.0

# The site plan shows the lot plus about 80 ft on each side, extended toward any
# adjoining street centre line within SITE_STREET_REACH_FT so every fronting
# street shows and can be named (capped at the reach).
SITE_PAD_FT = 80.0
SITE_STREET_REACH_FT = 140.0
FRONTAGE_STREET_MAX_FT = 90.0  # a street this far outward names a frontage edge
EDGE_MIN_LABEL_FT = 6.0        # shorter edges are left undimensioned
TITLE_BAND_PT = 30.0           # height reserved at the top of the region for the title
FRAME_INSET = 2.0              # the viewport is inset this far inside the plan region
STREET_LABEL_MIN_RUN_PT = 26.0  # a street piece shorter than this (on screen) is not labelled

# Compact SUMMARY frame (rework 3): for page 1 and a one-page location sheet - at
# most 88 mm (249.45 pt) by 72 mm (204.09 pt); no title, subtitle, legend or notes
# column inside (the report captions it); a compact north arrow and scale bar.
SUMMARY_MAX_W_PT = 249.4
SUMMARY_MAX_H_PT = 204.0
SUMMARY_CANVAS_W = 248.0
SUMMARY_PLAN = (3.0, 3.0, 245.0, 168.0)
SUMMARY_PLAN_MARGIN = 6.0
SUMMARY_FURN_TOP = 172.0
SUMMARY_NORTH_CX = 12.0
SUMMARY_SCALE_X = 34.0
SITE_SUMMARY_BORDER_FT = 90.0   # streets this close to the lot border it (site summary)
BLOCK_SUMMARY_BORDER_FT = 230.0  # streets this close border the subject's block (block summary)

_Box = tuple[float, float, float, float]
BOROUGHS = {"1": "Manhattan", "2": "Bronx", "3": "Brooklyn", "4": "Queens", "5": "Staten Island"}


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
) -> ViewFrame:
    """Fit ``window`` (its four corners, rotated by ``alpha``) into ``region`` at
    the largest STANDARD architectural/engineering scale that fits, so the scale
    bar states a real 1 in = S ft scale. ``top_band`` reserves title height."""
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
    k = next((POINTS_PER_INCH / s for s in STANDARD_SCALES_FT_PER_IN
              if POINTS_PER_INCH / s <= fit), None)
    if k is None:
        raise MapInputError("view_too_large", "the view does not fit the largest standard scale",
                            location="/map_context")
    ox = region[0] + ((region[2] - region[0]) - width * k) / 2.0
    oy = region[1] + top_band + ((region[3] - region[1] - top_band) - height * k) / 2.0
    return ViewFrame(k, cos, sin, minrx, maxry, ox, oy, math.degrees(-alpha))


def viewport(region: _Box, top_band: float = TITLE_BAND_PT) -> _Box:
    """The clean rectangular drawing frame inside ``region``: inset on every
    side, with ``top_band`` reserved at the top (the title band in the report
    frame; just the inset in the summary frame). Everything is clipped to it."""
    return (region[0] + FRAME_INSET, region[1] + top_band,
            region[2] - FRAME_INSET, region[3] - FRAME_INSET)


def bordering_street_names(outline: Polygon, streets: StreetLayer, max_dist: float) -> set[str]:
    """The names of the streets whose centre line comes within ``max_dist`` feet
    of ``outline`` - the streets that border the lot (or the block). Used to label
    only the main streets on the compact summary frame."""
    subj = make_valid(ShapelyPolygon(outline.exterior))
    names: set[str] = set()
    for street in streets.streets:
        for path in street.paths:
            if len(path) >= 2 and subj.distance(LineString([tuple(p) for p in path])) <= max_dist:
                names.add(street.name)
                break
    return names


def summary_notes(frontage: str | None) -> list[MapNote]:
    """SHORT plain sentences for the caller to caption the summary frame (no
    source names, dates or dataset ids - the report composes those from the
    provenance)."""
    notes = []
    if frontage is not None:
        notes.append(MapNote(f"Rotated to the {frontage} frontage.", "/map_context/subject_lot"))
    notes.append(MapNote("Map geometry only; tax boundaries do not establish the legal zoning "
                         "lot; nothing is surveyed.", "/map_context/subject_lot"))
    return notes


def _pad_box(box: _Box, pad: float) -> _Box:
    return box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad


def _inside(box: _Box, p: Point) -> bool:
    return box[0] <= p[0] <= box[2] and box[1] <= p[1] <= box[3]


def site_context_view(subject: SubjectLot, streets: StreetLayer) -> _Box:
    """The site-plan view: the subject bbox + 80 ft, pulled out toward any street
    centre-line point within SITE_STREET_REACH_FT of the lot (capped), so every
    adjoining street shows (deterministic)."""
    base_box = geo.bbox(subject.outline.exterior)
    base = _pad_box(base_box, SITE_PAD_FT)
    reach = _pad_box(base_box, SITE_STREET_REACH_FT)
    xs, ys = [base[0], base[2]], [base[1], base[3]]
    for street in streets.streets:
        for path in street.paths:
            for p in path:
                if _inside(reach, p):
                    xs.append(p[0])
                    ys.append(p[1])
    return (max(min(xs), reach[0]), max(min(ys), reach[1]),
            min(max(xs), reach[2]), min(max(ys), reach[3]))


# --------------------------------------------------------------------------- #
# Frontage detection + the immediate neighbours + the subtitle.
# --------------------------------------------------------------------------- #
def _seg_foot(p: Point, a: Point, b: Point) -> tuple[float, Point]:
    dx, dy = b[0] - a[0], b[1] - a[1]
    length_sq = dx * dx + dy * dy
    if length_sq == 0.0:
        return math.hypot(p[0] - a[0], p[1] - a[1]), a
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / length_sq))
    foot = (a[0] + t * dx, a[1] + t * dy)
    return math.hypot(p[0] - foot[0], p[1] - foot[1]), foot


def _nearest_outward_street(mid: Point, nout: Point, streets: Sequence):
    name = source = None
    best: float | None = None
    for street in streets:
        for path in street.paths:
            for a, b in zip(path, path[1:], strict=False):
                dist, foot = _seg_foot(mid, a, b)
                if (foot[0] - mid[0]) * nout[0] + (foot[1] - mid[1]) * nout[1] <= 0.0:
                    continue
                if best is None or dist < best:
                    best, name, source = dist, street.name, street.name_source
    return name, source, best


def frontage_rotation(subject: SubjectLot, streets: StreetLayer):
    """The rotation levelling the subject's longest street-bordering edge with
    that street at the top, plus the street's name/source. No qualifying edge ->
    (0.0, None, None) (north-up)."""
    ring = subject.outline.exterior
    area = geo.signed_area(ring)
    best = None
    for a, b in geo.edges(ring):
        if geo.edge_length(a, b) < EDGE_MIN_LABEL_FT:
            continue
        nx, ny = geo.outward_normal(a, b, area)
        mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        name, source, dist = _nearest_outward_street(mid, (nx, ny), streets.streets)
        if name is None or source is None or dist is None or dist > FRONTAGE_STREET_MAX_FT:
            continue
        length = geo.edge_length(a, b)
        if best is None or length > best[0]:
            best = (length, (nx, ny), name, source)
    if best is None:
        return 0.0, None, None
    _, nout, name, source = best
    alpha = math.pi / 2.0 - math.atan2(nout[1], nout[0])
    return alpha, name, source


def edge_sharing_lots(context: MapContext) -> list[NeighbourLot]:
    """The neighbouring tax lots that share a BOUNDARY EDGE with the subject (a
    shared segment longer than 1 ft - a mere corner touch does not count). These
    are the only neighbours the site plan labels."""
    if not isinstance(context.tax_lots, TaxLotLayer):
        return []
    subj = make_valid(ShapelyPolygon(context.subject_lot.outline.exterior))
    out = []
    for lot in context.tax_lots.lots:
        nb = make_valid(ShapelyPolygon(lot.outline.exterior))
        if subj.boundary.intersection(nb.boundary).length > 1.0:
            out.append(lot)
    return out


def subtitle_from_bbl(bbl: str | None) -> str | None:
    """"Queens, Block 7334, lot 70" style from a 10-digit BBL (never the raw
    BBL); ``None`` if the BBL is not a plain 10-digit string."""
    if bbl is None or len(bbl) != 10 or not bbl.isdigit():
        return None
    boro = BOROUGHS.get(bbl[0])
    prefix = f"{boro}, " if boro else ""
    return f"{prefix}Block {int(bbl[1:6])}, lot {int(bbl[6:])}"


# --------------------------------------------------------------------------- #
# Label placement (drop a label rather than overlap -> S4 has zero overlaps).
# --------------------------------------------------------------------------- #
def _place(sheet: Sheet, candidates, text, *, size, source, role, anchor="start", style=None,
           rect: _Box | None = None, pad: float = 1.0) -> bool:
    for x, y, rot in candidates:
        box = text_box(x, y, text, size, anchor, rot)
        if rect is not None and not _box_in_rect(box, rect):
            continue
        if any(box.overlaps(other, pad) for other in sheet.boxes):
            continue
        sheet.label([(x, y, rot)], text, size=size, source=source, role=role, anchor=anchor,
                    style=style)
        return True
    return False


def _box_in_rect(box, rect: _Box) -> bool:
    return box.x0 >= rect[0] and box.y0 >= rect[1] and box.x1 <= rect[2] and box.y1 <= rect[3]


def _readable(angle_deg: float) -> float:
    if angle_deg >= 90.0:
        return angle_deg - 180.0
    if angle_deg < -90.0:
        return angle_deg + 180.0
    return angle_deg


# --------------------------------------------------------------------------- #
# The scene: street areas, lots, buildings, labels - all clipped to the frame.
# --------------------------------------------------------------------------- #
def _proj(polygon: Polygon, fr: ViewFrame):
    return [[fr.px(p) for p in ring] for ring in polygon.rings]


def _draw_clipped_area(sheet: Sheet, rings, kind: str, source: str, rect: _Box) -> None:
    for poly in clip_polygon_to_rect([tuple(r) for r in rings], rect):
        sheet.area(path_data(poly), kind, [("data-source", source)])


def _draw_clipped_outline(sheet: Sheet, rings, kind: str, source: str, rect: _Box) -> None:
    for poly in clip_polygon_to_rect([tuple(r) for r in rings], rect):
        sheet.line(path_data(poly), kind, [("fill-rule", "evenodd"), ("data-source", source)])


def _lot_bbox_touches(polygon: Polygon, fr: ViewFrame, rect: _Box) -> bool:
    xs = [fr.px(p)[0] for p in polygon.exterior]
    ys = [fr.px(p)[1] for p in polygon.exterior]
    return not (max(xs) < rect[0] or min(xs) > rect[2] or max(ys) < rect[1] or min(ys) > rect[3])


def _draw_street_areas(sheet: Sheet, lots: Sequence[Polygon], fr: ViewFrame, rect: _Box,
                       data_region) -> None:
    proj = [[fr.px(p) for p in ring] for lot in lots for ring in [lot.exterior]]  # exteriors only
    lot_rings = [[tuple(ring)] for ring in proj]
    min_area = MIN_STREET_AREA_SQFT * fr.k * fr.k
    for i, piece in enumerate(gaps_in_rect(rect, lot_rings, min_area, data_region)):
        sheet.area(path_data(piece), "street_area",
                   [("data-source", f"/map_context/tax_lots#gap-{i}")])


def _data_region(context: MapContext, fr: ViewFrame):
    """The context window (the box the lots and buildings were fetched for),
    projected to screen rings, so no street is drawn outside it. ``None`` when
    the document carries no context window."""
    cw = context.context_window
    if cw is None:
        return None
    corners = [(cw.xmin, cw.ymin), (cw.xmax, cw.ymin), (cw.xmax, cw.ymax), (cw.xmin, cw.ymax)]
    return [tuple(fr.px(c) for c in corners)]


def _label_streets(sheet: Sheet, streets: StreetLayer, fr: ViewFrame, rect: _Box, size: float,
                   *, with_width: bool, data_region=None, only: set[str] | None = None) -> None:
    best: dict[str, tuple] = {}
    for street in streets.streets:
        if only is not None and street.name not in only:
            continue
        for path in street.paths:
            for piece in clip_polyline_to_rect([fr.px(p) for p in path], rect, data_region):
                length = _poly_len(piece)
                if length >= STREET_LABEL_MIN_RUN_PT and (
                        street.name not in best or length > best[street.name][0]):
                    best[street.name] = (length, piece, street)
    for name in sorted(best):
        _, piece, street = best[name]
        _place(sheet, _line_candidates(piece, size), street.name.upper(), size=size,
               source=street.name_source, role="street", anchor="middle", style="italic",
               rect=rect)
        if with_width and street.mapped_width_ft is not None:
            wtext = f"{format_number(street.mapped_width_ft)} ft mapped width"
            _place(sheet, _line_candidates(piece, size - 1.5), wtext, size=max(7.0, size - 1.5),
                   source=street.mapped_width_source, role="street_width", anchor="middle",
                   style="italic", rect=rect)


def _poly_len(coords: Sequence[Point]) -> float:
    return sum(geo.edge_length(a, b) for a, b in zip(coords, coords[1:], strict=False))


def _line_candidates(poly: Sequence[Point], size: float):
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
                ang = _readable(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])))
                for off, d in ((0.0, n), (size + 2.0, n), (size + 2.0, (-n[0], -n[1]))):
                    out.append((mid[0] + d[0] * off, mid[1] + d[1] * off, ang))
                break
            acc += seg_len
    return out


def _focus_lot_label(sheet: Sheet, outline: Polygon, fr: ViewFrame, number: str | None,
                     number_source, address, address_source, rect: _Box, *, size: float) -> None:
    cx, cy = fr.px(geo.centroid(outline.exterior))
    if number is not None and number_source is not None:
        steps = [0.0, 2.4 * size, -2.4 * size, 4.8 * size, -4.8 * size]
        _place(sheet, [(cx, cy + s, 0.0) for s in steps], f"Lot {number}", size=size,
               source=number_source, role="lot_number", anchor="middle", rect=rect)
    if address is not None and address_source is not None:
        asz = size - 1.0
        steps = [1.0, 3.2, -3.2, 5.4, -5.4]
        _place(sheet, [(cx, cy + size + s, 0.0) for s in steps], address, size=max(7.0, asz),
               source=address_source, role="lot_address", anchor="middle", rect=rect)


def _lot_number(bbl: str | None) -> str | None:
    return str(int(bbl[-4:])) if bbl and len(bbl) == 10 and bbl.isdigit() else None


def _draw_edge_lengths(sheet: Sheet, subject: SubjectLot, fr: ViewFrame, rect: _Box) -> None:
    ring = subject.outline.exterior
    area = geo.signed_area(ring)
    size = TYPOGRAPHY.dimension_pt
    for i, (a, b) in enumerate(geo.edges(ring)):
        if geo.edge_length(a, b) < EDGE_MIN_LABEL_FT:
            continue
        nx, ny = geo.outward_normal(a, b, area)
        pa, pb = fr.px(a), fr.px(b)
        n = _screen_dir((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0, (nx, ny), fr)
        ang = _readable(math.degrees(math.atan2(pb[1] - pa[1], pb[0] - pa[0])))
        mx, my = (pa[0] + pb[0]) / 2.0, (pa[1] + pb[1]) / 2.0
        cands = [(mx + n[0] * (4.0 + j * (size + 1.0)), my + n[1] * (4.0 + j * (size + 1.0)), ang)
                 for j in range(7)]
        _place(sheet, cands, format_feet(geo.edge_length(a, b)), size=size,
               source=f"edge:{subject.outline.source}/0#{i}", role="dimension", anchor="middle",
               rect=rect)


def _screen_dir(wx: float, wy: float, nout_world: Point, fr: ViewFrame) -> Point:
    pm = fr.px((wx, wy))
    pt = fr.px((wx + nout_world[0], wy + nout_world[1]))
    dx, dy = pt[0] - pm[0], pt[1] - pm[1]
    length = math.hypot(dx, dy) or 1.0
    return (dx / length, dy / length)


def _restroke_subject(sheet: Sheet, subject: SubjectLot, fr: ViewFrame, rect: _Box) -> None:
    _draw_clipped_outline(sheet, _proj(subject.outline, fr), "subject_lot",
                          subject.outline.source, rect)


def draw_frame(sheet: Sheet, rect: _Box) -> None:
    """A thin border around the drawing viewport."""
    sheet.parts.append(element("rect", [
        ("x", rect[0]), ("y", rect[1]), ("width", rect[2] - rect[0]), ("height", rect[3] - rect[1]),
        ("fill", "none"), ("stroke", "#C9CFD4"), ("stroke-width", 0.75),
        ("data-role", "frame")]))


def draw_title(sheet: Sheet, title: str, subtitle: str | None, subtitle_source: str | None,
               region: _Box) -> None:
    size = TYPOGRAPHY.title_pt
    x = region[0] + 6.0
    y = region[1] + size + 2.0
    sheet.parts.append(text_element(x, y, title, size=size, source=None, role="title",
                                    weight="bold"))
    sheet.labels.append(Label(title, None, "title"))
    if subtitle is not None:
        sheet.parts.append(text_element(x, y + size + 1.0, subtitle, size=TYPOGRAPHY.label_pt,
                                        source=subtitle_source, role="title"))
        sheet.labels.append(Label(subtitle, subtitle_source, "title"))


# --------------------------------------------------------------------------- #
# Shared scene used by the site plan and the block close-up.
# --------------------------------------------------------------------------- #
def _draw_lots_and_buildings(sheet: Sheet, context: MapContext, fr: ViewFrame, rect: _Box) -> None:
    lots = context.tax_lots.lots if isinstance(context.tax_lots, TaxLotLayer) else ()
    # street space first, confined to the data window (no street where no data)
    all_lots = [context.subject_lot.outline, *(lot.outline for lot in lots)]
    _draw_street_areas(sheet, all_lots, fr, rect, _data_region(context, fr))
    # the subject fill, then the neighbours as thin light outlines
    _draw_clipped_area(sheet, _proj(context.subject_lot.outline, fr), "subject_lot",
                       context.subject_lot.outline.source, rect)
    for lot in lots:
        if _lot_bbox_touches(lot.outline, fr, rect):
            _draw_clipped_outline(sheet, _proj(lot.outline, fr), "neighbour_lot",
                                  lot.outline.source, rect)
    if isinstance(context.buildings, BuildingLayer):
        for fp in context.buildings.footprints:
            if _lot_bbox_touches(fp.outline, fr, rect):
                _draw_clipped_area(sheet, _proj(fp.outline, fr), "building_footprint",
                                   fp.source, rect)
    _restroke_subject(sheet, context.subject_lot, fr, rect)


def draw_block_scene(
    context: MapContext, fr: ViewFrame, rect: _Box, region: _Box, *,
    title: str | None, with_edges: bool, with_widths: bool, label_focus: bool,
    street_filter: set[str] | None = None,
) -> Sheet:
    """The shared coloured scene for the site plan and the block close-up:
    even street areas, the subject coloured, the neighbours as thin outlines,
    buildings grey, street names centred in their street. Labels only the subject
    (and, when ``label_focus``, its edge-sharing neighbours). ``title=None`` and a
    ``street_filter`` give the compact summary (no title; only the main streets)."""
    assert isinstance(context.streets, StreetLayer)
    sheet = Sheet()
    data_region = _data_region(context, fr)
    _draw_lots_and_buildings(sheet, context, fr, rect)
    size = TYPOGRAPHY.label_pt + 1.0
    _label_streets(sheet, context.streets, fr, rect, size, with_width=with_widths,
                   data_region=data_region, only=street_filter)
    # the subject label first (most prominent), then the immediate neighbours
    subj = context.subject_lot
    _focus_lot_label(sheet, subj.outline, fr, _lot_number(subj.bbl), subj.bbl_source, None, None,
                     rect, size=TYPOGRAPHY.label_pt + 2.0)
    if label_focus:
        for lot in edge_sharing_lots(context):
            _focus_lot_label(sheet, lot.outline, fr, _lot_number(lot.bbl), lot.bbl_source,
                             lot.address, lot.address_source, rect, size=TYPOGRAPHY.label_pt)
    if with_edges:
        _draw_edge_lengths(sheet, subj, fr, rect)
    draw_frame(sheet, rect)
    if title is not None:
        draw_title(sheet, title, subtitle_from_bbl(subj.bbl), subj.bbl_source, region)
    return sheet


# --------------------------------------------------------------------------- #
# Neighbourhood scene (street network of centre lines; no tax lots at ~2,000 ft).
# --------------------------------------------------------------------------- #
def draw_neighbourhood_scene(context: MapContext, fr: ViewFrame, rect: _Box, region: _Box,
                             *, summary: bool = False) -> Sheet:
    assert isinstance(context.streets, StreetLayer)
    sheet = Sheet()
    # the street network, clipped to the viewport
    pieces_by_name: dict[str, list] = {}
    for street in context.streets.streets:
        for path in street.paths:
            for piece in clip_polyline_to_rect([fr.px(p) for p in path], rect):
                sheet.line(polyline_data(list(piece)), "street_centreline",
                           [("data-source", f"{street.source}/paths")])
                pieces_by_name.setdefault(street.name, []).append((street, piece))
    all_lines = [piece for runs in pieces_by_name.values() for _s, piece in runs]
    _mark_subject(sheet, context.subject_lot, fr, rect, TYPOGRAPHY.label_pt, all_lines,
                  with_label=not summary)
    priority = (bordering_street_names(context.subject_lot.outline, context.streets, 140.0)
                if summary else None)  # on the thumbnail, name the lot's own streets first
    _label_network(sheet, pieces_by_name, rect, TYPOGRAPHY.label_pt + (0.0 if summary else 1.0),
                   priority=priority, pad=5.0 if summary else 1.0)
    draw_frame(sheet, rect)
    if not summary:
        draw_title(sheet, "Neighbourhood", subtitle_from_bbl(context.subject_lot.bbl),
                   context.subject_lot.bbl_source, region)
    return sheet


def _label_network(sheet: Sheet, pieces_by_name: dict, rect: _Box, size: float,
                   priority: set[str] | None = None, pad: float = 1.0) -> None:
    """One label per street, on its longest clipped piece, placed AWAY from every
    other street's lines (so no name crosses another street); dropped if no clear
    spot exists. ``priority`` names are placed FIRST (so the lot's own streets win
    the space on the crowded summary thumbnail)."""
    all_lines = [piece for runs in pieces_by_name.values() for _s, piece in runs]
    order = sorted(pieces_by_name)
    if priority:
        pri = [n for n in pieces_by_name if n in priority]
        pri.sort(key=lambda n: (-round(max(_poly_len(p) for _s, p in pieces_by_name[n]), 2), n))
        order = pri + sorted(n for n in pieces_by_name if n not in priority)
    for name in order:
        runs = pieces_by_name[name]
        _street, piece = max(runs, key=lambda r: _poly_len(r[1]))
        if _poly_len(piece) < STREET_LABEL_MIN_RUN_PT:
            continue
        cands = _network_candidates(piece, all_lines, size)
        _place(sheet, cands, name.upper(), size=size, source=runs[0][0].name_source,
               role="street", anchor="middle", style="italic", rect=rect, pad=pad)


def _network_candidates(piece, all_lines, size):
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
                ang = _readable(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])))
                clear = _clearance(mid, piece, all_lines)
                scored.append((clear, mid, ang))
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


def _clearance(p: Point, own, all_lines) -> float:
    best = 1e9
    for line in all_lines:
        if line is own:
            continue
        for a, b in zip(line, line[1:], strict=False):
            d, _f = _seg_foot(p, a, b)
            best = min(best, d)
    return best


def _mark_subject(sheet: Sheet, subject: SubjectLot, fr: ViewFrame, rect: _Box,
                  size: float, avoid_lines, *, with_label: bool = True) -> None:
    _draw_clipped_area(sheet, _proj(subject.outline, fr), "subject_lot",
                       subject.outline.source, rect)
    _restroke_subject(sheet, subject, fr, rect)
    if not with_label:
        # the compact summary marks the lot with the coral marker only; reserve
        # its footprint so no street name is drawn across the marker.
        pts = [fr.px(p) for p in subject.outline.exterior]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        sheet.reserve(Box(min(xs) - 3.0, min(ys) - 3.0, max(xs) + 3.0, max(ys) + 3.0))
        return
    cx, cy = fr.px(geo.centroid(subject.outline.exterior))
    # candidates ringing the marker, ranked by clearance from the street lines, so
    # the 'Subject lot' label lands on open land - never on a street line.
    cands = []
    for ring in range(2, 10):
        radius = ring * (size + 2.0)
        for ang in range(0, 360, 30):
            rad = math.radians(ang)
            p = (cx + radius * math.cos(rad), cy + radius * math.sin(rad))
            cands.append((_clearance(p, None, avoid_lines), p))
    cands.sort(key=lambda c: (-round(c[0], 2), round(c[1][0], 2), round(c[1][1], 2)))
    for need_clear in (size * 0.8, size * 0.4, 0.0):
        for clear, (x, y) in cands:
            if clear < need_clear:
                continue
            box = text_box(x, y, "Subject lot", size, "middle", 0.0)
            if not _box_in_rect(box, rect) or any(box.overlaps(o) for o in sheet.boxes):
                continue
            sheet.label([(x, y, 0.0)], "Subject lot", size=size, source=None,
                        role="subject_mark", anchor="middle")
            sheet.parts.append(element("path", [
                ("d", polyline_data([(cx, cy), (x, y - size * 0.3)])), ("fill", "none"),
                ("stroke", "#C8500A"), ("stroke-width", 0.5), ("data-role", "leader")]))
            return


# --------------------------------------------------------------------------- #
# Caption + composition.
# --------------------------------------------------------------------------- #
def _attr_note(attribution: MapNote, edited: str | None) -> MapNote:
    """The layer's attribution, with the source's edit date appended when the
    document carries one in provenance (ruling Y7; the real recorded pack keeps
    the date in provenance, not in the attribution text)."""
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


def _north(cx: float, top: float, deg: float, *, caption: bool = True,
           half: float = 18.0) -> tuple[list[str], float]:
    """A grid-north arrow that rotates to point at grid north, with the 'Grid
    north' caption kept HORIZONTAL. ``caption=False`` and a smaller ``half`` give
    the compact summary arrow. Returns the parts and the bottom y."""
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
    ``mode`` is 'report', 'sheet' or 'summary'. The canvas height always clears
    the furniture. Summary: compact north arrow and scale bar, no legend or notes
    column; the short notes are returned to the caller."""
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


def unavailable_layer(name: str, layer: object, source: str) -> Unavailable | None:
    if layer is None:
        return Unavailable(name, f"the {name.replace('_', ' ')} layer is not in this document",
                           "source_unavailable", source)
    if isinstance(layer, LayerUnavailable):
        return Unavailable(name, layer.reason, layer.reason_kind, f"{layer.source}/reason")
    return None


# --------------------------------------------------------------------------- #
# The site context plan.
# --------------------------------------------------------------------------- #
def draw_site_context_plan(context: MapContext, *, frame: str = "sheet") -> Drawing | Unavailable:
    """The site plan among its surroundings. Needs the tax lots, the streets and
    the building footprints; any one unavailable returns Unavailable (S6)."""
    drawing = "site_context_plan"
    for name, layer, source in (
        ("tax_lots", context.tax_lots, "/map_context/tax_lots"),
        ("streets", context.streets, "/map_context/streets"),
        ("building_footprints", context.buildings, "/map_context/building_footprints"),
    ):
        unavailable = unavailable_layer(name, layer, source)
        if unavailable is not None:
            return Unavailable(drawing, unavailable.reason, unavailable.reason_kind,
                               unavailable.source)
    assert isinstance(context.streets, StreetLayer)
    view = site_context_view(context.subject_lot, context.streets)
    alpha, frontage_name, frontage_source = frontage_rotation(context.subject_lot, context.streets)
    title = "Site plan: the lot among its neighbours"
    if frame == "summary":
        fr = fit_view(view, SUMMARY_PLAN, SUMMARY_PLAN_MARGIN, alpha=alpha, top_band=0.0)
        rect = viewport(SUMMARY_PLAN, FRAME_INSET)
        border = bordering_street_names(context.subject_lot.outline, context.streets,
                                        SITE_SUMMARY_BORDER_FT)
        sheet = draw_block_scene(context, fr, rect, SUMMARY_PLAN, title=None, with_edges=False,
                                 with_widths=False, label_focus=False, street_filter=border)
        return compose_context(drawing, title, sheet, fr, summary_notes(frontage_name),
                               mode="summary")
    report = frame == "report"
    region, margin = (REPORT_PLAN, REPORT_PLAN_MARGIN) if report else (PLAN, PLAN_MARGIN)
    fr = fit_view(view, region, margin, alpha=alpha, top_band=TITLE_BAND_PT)
    rect = viewport(region)
    sheet = draw_block_scene(context, fr, rect, region, title=title, with_edges=True,
                             with_widths=True, label_focus=True)
    notes = caption_notes(context, layers={"tax_lots", "streets", "buildings"}, gaps_note=True,
                          frontage=frontage_name, frontage_source=frontage_source)
    return compose_context(drawing, title, sheet, fr, notes,
                           mode="report" if report else "sheet")
