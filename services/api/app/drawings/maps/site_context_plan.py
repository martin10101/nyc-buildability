"""The site plan among its surroundings (M5-T155, D-090 R936-R938).

The owner looked at the old site drawing - the lot's outline alone on a blank
page - and said it was "a rectangle on an angle" with "no reference to where he
is". This draws what the competitor's site/location pages draw, reading cleanly
on the REAL recorded tax map (hundreds of neighbouring lots): the subject lot
clearly coloured ABOVE the existing building (shown as a dashed outline so the
coral reads first), its immediate (edge-sharing) neighbours labelled "Lot <n>"
+ address, other lots as thin outlines, existing buildings grey, the streets as
the even open space between the tax lots named along the street, rotated so the
main frontage runs level. No law is computed or drawn (ruling Y6/Y8).

The reusable view-frame, projection, label-placement and composition helpers
live in :mod:`context_scene`; this module holds the drawing-specific scene logic
and re-exports the toolkit so the block close-up and neighbourhood map keep
importing it from here. Coordinates are EPSG:2263 US survey feet.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from shapely import make_valid
from shapely.geometry import LineString
from shapely.geometry import Polygon as ShapelyPolygon

from app.drawings.kit import geometry as geo
from app.drawings.kit.labels import Box, format_feet, format_number, text_box
from app.drawings.kit.sheet import Sheet
from app.drawings.kit.styles import TYPOGRAPHY
from app.drawings.kit.svg import element, path_data, polyline_data, text_element

from .context_scene import (
    FRAME_INSET,
    SUMMARY_PLAN,
    SUMMARY_PLAN_MARGIN,
    TITLE_BAND_PT,
    WIDE_PLAN,
    WIDE_PLAN_MARGIN,
    ViewFrame,
    box_crosses_lines,
    caption_notes,
    compose_context,
    draw_clipped_area,
    draw_clipped_outline,
    draw_frame,
    fit_view,
    line_candidates,
    lot_bbox_touches,
    network_candidates,
    pad_box,
    place,
    point_inside,
    polyline_len,
    project_polygon,
    readable_angle,
    screen_dir,
    seg_foot,
    segment_crosses_lines,
    summary_notes,
    viewport,
)
from .layout import PLAN, PLAN_MARGIN, REPORT_PLAN, REPORT_PLAN_MARGIN
from .model import (
    BuildingLayer,
    Drawing,
    Label,
    LayerUnavailable,
    MapContext,
    NeighbourLot,
    Point,
    Polygon,
    StreetLayer,
    SubjectLot,
    TaxLotLayer,
    Unavailable,
)
from .street_areas import MIN_STREET_AREA_SQFT, clip_polyline_to_rect, gaps_in_rect

# Re-export the shared toolkit so block_map / neighbourhood_map / the tests keep
# importing these names from site_context_plan (compatibility facade).
__all__ = [
    "SITE_PAD_FT",
    "SITE_STREET_REACH_FT",
    "SUMMARY_PLAN",
    "SUMMARY_PLAN_MARGIN",
    "TITLE_BAND_PT",
    "WIDE_PLAN",
    "WIDE_PLAN_MARGIN",
    "FRAME_INSET",
    "ViewFrame",
    "bordering_street_names",
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
    "summary_notes",
    "unavailable_layer",
    "viewport",
]

# The site plan shows the lot plus about 80 ft on each side, extended toward any
# adjoining street centre line within SITE_STREET_REACH_FT so every fronting
# street shows and can be named (capped at the reach).
SITE_PAD_FT = 80.0
SITE_STREET_REACH_FT = 140.0
FRONTAGE_STREET_MAX_FT = 90.0  # a street this far outward names a frontage edge
EDGE_MIN_LABEL_FT = 6.0        # shorter edges are left undimensioned
STREET_LABEL_MIN_RUN_PT = 26.0  # a street piece shorter than this (on screen) is not labelled
GAP_NAMED_MIN_PT = 14.0        # a gap is a street only if a centre line runs this far through it
MARKER_LEADER_MAX_PT = 42.0    # the 'Subject lot' leader is at most 15 mm long, crosses no street
SITE_SUMMARY_BORDER_FT = 90.0   # streets this close to the lot border it (site summary)
BLOCK_SUMMARY_BORDER_FT = 230.0  # streets this close border the subject's block (block summary)

_Box = tuple[float, float, float, float]
BOROUGHS = {"1": "Manhattan", "2": "Bronx", "3": "Brooklyn", "4": "Queens", "5": "Staten Island"}


def site_context_view(subject: SubjectLot, streets: StreetLayer) -> _Box:
    """The site-plan view: the subject bbox + 80 ft, pulled out toward any street
    centre-line point within SITE_STREET_REACH_FT of the lot (capped), so every
    adjoining street shows (deterministic)."""
    base_box = geo.bbox(subject.outline.exterior)
    base = pad_box(base_box, SITE_PAD_FT)
    reach = pad_box(base_box, SITE_STREET_REACH_FT)
    xs, ys = [base[0], base[2]], [base[1], base[3]]
    for street in streets.streets:
        for path in street.paths:
            for p in path:
                if point_inside(reach, p):
                    xs.append(p[0])
                    ys.append(p[1])
    return (max(min(xs), reach[0]), max(min(ys), reach[1]),
            min(max(xs), reach[2]), min(max(ys), reach[3]))


# --------------------------------------------------------------------------- #
# Frontage detection + the immediate neighbours + the subtitle.
# --------------------------------------------------------------------------- #
def _nearest_outward_street(mid: Point, nout: Point, streets: Sequence):
    name = source = None
    best: float | None = None
    for street in streets:
        for path in street.paths:
            for a, b in zip(path, path[1:], strict=False):
                dist, foot = seg_foot(mid, a, b)
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
    shared segment longer than 1 ft - a mere corner touch does not count)."""
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


def bordering_street_names(outline: Polygon, streets: StreetLayer, max_dist: float) -> set[str]:
    """Names of streets whose centre line comes within ``max_dist`` ft of
    ``outline`` - the streets bordering the lot (or block)."""
    subj = make_valid(ShapelyPolygon(outline.exterior))
    names: set[str] = set()
    for street in streets.streets:
        for path in street.paths:
            if len(path) >= 2 and subj.distance(LineString([tuple(p) for p in path])) <= max_dist:
                names.add(street.name)
                break
    return names


# --------------------------------------------------------------------------- #
# Scene geometry: street areas (only named gaps filled), lots, buildings.
# --------------------------------------------------------------------------- #
def _data_region(context: MapContext, fr: ViewFrame):
    cw = context.context_window
    if cw is None:
        return None
    corners = [(cw.xmin, cw.ymin), (cw.xmax, cw.ymin), (cw.xmax, cw.ymax), (cw.xmin, cw.ymax)]
    return [tuple(fr.px(c) for c in corners)]


def _street_lines_screen(streets: StreetLayer, fr: ViewFrame, rect: _Box, data_region):
    """Every street centre line clipped to the drawing window, as (name, polyline)
    - used both to decide which gaps are streets and to keep labels off OTHER
    streets' lines."""
    out = []
    for street in streets.streets:
        for path in street.paths:
            for piece in clip_polyline_to_rect([fr.px(p) for p in path], rect, data_region):
                out.append((street.name, piece))
    return out


def _draw_street_areas(sheet: Sheet, lots: Sequence[Polygon], street_lines, fr: ViewFrame,
                       rect: _Box, data_region) -> None:
    """Fill ONLY the gaps a named street centre line runs through; a gap no
    centre line crosses (an outer-corner pocket) is left NEUTRAL white, not given
    a second street style (T155 cosmetic fix 2)."""
    proj = [[fr.px(p) for p in ring] for lot in lots for ring in [lot.exterior]]
    lot_rings = [[tuple(ring)] for ring in proj]
    min_area = MIN_STREET_AREA_SQFT * fr.k * fr.k
    lines = [LineString(line) for _name, line in street_lines]
    for i, piece in enumerate(gaps_in_rect(rect, lot_rings, min_area, data_region)):
        gap = make_valid(ShapelyPolygon(piece[0], list(piece[1:])))
        if any(gap.intersection(ln).length >= GAP_NAMED_MIN_PT for ln in lines):
            sheet.area(path_data(piece), "street_area",
                       [("data-source", f"/map_context/tax_lots#gap-{i}")])


def _draw_lots_and_buildings(sheet: Sheet, context: MapContext, fr: ViewFrame, rect: _Box,
                             street_lines) -> None:
    lots = context.tax_lots.lots if isinstance(context.tax_lots, TaxLotLayer) else ()
    all_lots = [context.subject_lot.outline, *(lot.outline for lot in lots)]
    _draw_street_areas(sheet, all_lots, street_lines, fr, rect, _data_region(context, fr))
    for lot in lots:
        if lot_bbox_touches(lot.outline, fr, rect):
            draw_clipped_outline(sheet, project_polygon(lot.outline, fr), "neighbour_lot",
                                 lot.outline.source, rect)
    subj = context.subject_lot
    subj_sp = make_valid(ShapelyPolygon(subj.outline.exterior))
    on_subject = []  # existing buildings on the subject lot (drawn as a dashed outline on top)
    if isinstance(context.buildings, BuildingLayer):
        for fp in context.buildings.footprints:
            if not lot_bbox_touches(fp.outline, fr, rect):
                continue
            fp_sp = make_valid(ShapelyPolygon(fp.outline.exterior))
            if fp_sp.area > 0.0 and fp_sp.intersection(subj_sp).area > 0.5 * fp_sp.area:
                on_subject.append(fp)
            else:  # a neighbour's building: grey hatch
                draw_clipped_area(sheet, project_polygon(fp.outline, fr), "building_footprint",
                                  fp.source, rect)
    # the subject fill goes ABOVE the neighbour buildings (T155-C1), then the
    # subject's own existing building as a dashed outline, then the crisp border.
    draw_clipped_area(sheet, project_polygon(subj.outline, fr), "subject_lot",
                      subj.outline.source, rect)
    for fp in on_subject:
        draw_clipped_outline(sheet, project_polygon(fp.outline, fr), "existing_building",
                             fp.source, rect)
    draw_clipped_outline(sheet, project_polygon(subj.outline, fr), "subject_lot",
                         subj.outline.source, rect)


# --------------------------------------------------------------------------- #
# Scene labels.
# --------------------------------------------------------------------------- #
def _lot_number(bbl: str | None) -> str | None:
    return str(int(bbl[-4:])) if bbl and len(bbl) == 10 and bbl.isdigit() else None


def _subject_box(subject: SubjectLot, fr: ViewFrame) -> Box:
    pts = [fr.px(p) for p in subject.outline.exterior]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return Box(min(xs), min(ys), max(xs), max(ys))


def _label_streets(sheet: Sheet, streets: StreetLayer, fr: ViewFrame, rect: _Box, size: float,
                   *, with_width: bool, data_region=None, only: set[str] | None = None,
                   street_lines=None, avoid_boxes=()) -> None:
    best: dict[str, tuple] = {}
    for street in streets.streets:
        if only is not None and street.name not in only:
            continue
        for path in street.paths:
            for piece in clip_polyline_to_rect([fr.px(p) for p in path], rect, data_region):
                length = polyline_len(piece)
                if length >= STREET_LABEL_MIN_RUN_PT and (
                        street.name not in best or length > best[street.name][0]):
                    best[street.name] = (length, piece, street)
    for name in sorted(best):
        _, piece, street = best[name]
        place(sheet, line_candidates(piece, size), street.name.upper(), size=size,
              source=street.name_source, role="street", anchor="middle", style="italic",
              rect=rect, avoid_lines=street_lines, own=street.name, avoid_boxes=avoid_boxes,
              cross_max_len=2.6 * size)
        if with_width and street.mapped_width_ft is not None:
            wtext = f"{format_number(street.mapped_width_ft)} ft mapped width"
            place(sheet, line_candidates(piece, size - 1.5), wtext, size=max(7.0, size - 1.5),
                  source=street.mapped_width_source, role="street_width", anchor="middle",
                  style="italic", rect=rect, avoid_lines=street_lines, own=street.name,
                  avoid_boxes=avoid_boxes, cross_max_len=2.6 * size)


def _subject_label(sheet: Sheet, subject: SubjectLot, fr: ViewFrame, rect: _Box, size: float,
                   street_lines) -> None:
    """"Lot <n>" sitting ON or immediately beside the subject lot, never across a
    street (T156-C2 a). Dropped if it cannot fit without crossing a street - the
    coral marker then stands alone."""
    number = _lot_number(subject.bbl)
    if number is None or subject.bbl_source is None:
        return
    cx, cy = fr.px(geo.centroid(subject.outline.exterior))
    steps = [0.0, size + 1.0, -(size + 1.0), 2.0 * size, -2.0 * size]
    place(sheet, [(cx, cy + s, 0.0) for s in steps], f"Lot {number}", size=size,
          source=subject.bbl_source, role="lot_number", anchor="middle", rect=rect,
          avoid_lines=street_lines, own=None)


def _neighbour_label(sheet: Sheet, lot: NeighbourLot, fr: ViewFrame, rect: _Box, size: float,
                     street_lines, avoid_boxes) -> None:
    """"Lot <n>" (and the address) placed WELL INSIDE the neighbour, clear of the
    streets and of the subject marker (T155 cosmetic fix 3; T156-C2)."""
    number = _lot_number(lot.bbl)
    cx, cy = fr.px(geo.centroid(lot.outline.exterior))
    if number is not None and lot.bbl_source is not None:
        steps = [0.0, 2.6 * size, -2.6 * size, 5.2 * size]
        place(sheet, [(cx, cy + s, 0.0) for s in steps], f"Lot {number}", size=size,
              source=lot.bbl_source, role="lot_number", anchor="middle", rect=rect, pad=2.5,
              avoid_lines=street_lines, own=None, avoid_boxes=avoid_boxes)
    if lot.address is not None and lot.address_source is not None:
        asz = max(7.0, size - 1.0)
        steps = [size + 2.0, 3.6 * size, -(size + 2.0), 6.0 * size]
        place(sheet, [(cx, cy + s, 0.0) for s in steps], lot.address, size=asz,
              source=lot.address_source, role="lot_address", anchor="middle", rect=rect, pad=2.5,
              avoid_lines=street_lines, own=None, avoid_boxes=avoid_boxes)


def _draw_edge_lengths(sheet: Sheet, subject: SubjectLot, fr: ViewFrame, rect: _Box,
                       street_lines) -> None:
    ring = subject.outline.exterior
    area = geo.signed_area(ring)
    size = TYPOGRAPHY.dimension_pt
    for i, (a, b) in enumerate(geo.edges(ring)):
        if geo.edge_length(a, b) < EDGE_MIN_LABEL_FT:
            continue
        nx, ny = geo.outward_normal(a, b, area)
        pa, pb = fr.px(a), fr.px(b)
        n = screen_dir((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0, (nx, ny), fr)
        ang = readable_angle(math.degrees(math.atan2(pb[1] - pa[1], pb[0] - pa[0])))
        mx, my = (pa[0] + pb[0]) / 2.0, (pa[1] + pb[1]) / 2.0
        cands = [(mx + n[0] * (4.0 + j * (size + 1.5)), my + n[1] * (4.0 + j * (size + 1.5)), ang)
                 for j in range(7)]
        place(sheet, cands, format_feet(geo.edge_length(a, b)), size=size,
              source=f"edge:{subject.outline.source}/0#{i}", role="dimension", anchor="middle",
              rect=rect, pad=2.0, avoid_lines=street_lines, own=None)


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
def draw_block_scene(
    context: MapContext, fr: ViewFrame, rect: _Box, region: _Box, *,
    title: str | None, with_edges: bool, with_widths: bool, label_focus: bool,
    street_filter: set[str] | None = None,
) -> Sheet:
    """The shared coloured scene: even street areas (named gaps only), the subject
    coloured above the existing building, neighbours as thin outlines, buildings
    grey, street names in their street. Labels only the subject (and, when
    ``label_focus``, its edge-sharing neighbours), never across a street."""
    assert isinstance(context.streets, StreetLayer)
    sheet = Sheet()
    data_region = _data_region(context, fr)
    street_lines = _street_lines_screen(context.streets, fr, rect, data_region)
    _draw_lots_and_buildings(sheet, context, fr, rect, street_lines)
    marker_box = _subject_box(context.subject_lot, fr)
    size = TYPOGRAPHY.label_pt + 1.0
    _label_streets(sheet, context.streets, fr, rect, size, with_width=with_widths,
                   data_region=data_region, only=street_filter, street_lines=street_lines,
                   avoid_boxes=(marker_box,))
    subj = context.subject_lot
    _subject_label(sheet, subj, fr, rect, TYPOGRAPHY.label_pt + 2.0, street_lines)
    if label_focus:
        for lot in edge_sharing_lots(context):
            _neighbour_label(sheet, lot, fr, rect, TYPOGRAPHY.label_pt, street_lines, (marker_box,))
    if with_edges:
        _draw_edge_lengths(sheet, subj, fr, rect, street_lines)
    draw_frame(sheet, rect)
    if title is not None:
        draw_title(sheet, title, subtitle_from_bbl(subj.bbl), subj.bbl_source, region)
    return sheet


# --------------------------------------------------------------------------- #
# Neighbourhood scene (street network of centre lines; no tax lots at ~2,000 ft).
# --------------------------------------------------------------------------- #
def draw_neighbourhood_scene(context: MapContext, fr: ViewFrame, rect: _Box, region: _Box,
                             *, summary: bool = False, with_title: bool = True) -> Sheet:
    assert isinstance(context.streets, StreetLayer)
    sheet = Sheet()
    pieces_by_name: dict[str, list] = {}
    named_lines = []
    for street in context.streets.streets:
        for path in street.paths:
            for piece in clip_polyline_to_rect([fr.px(p) for p in path], rect):
                sheet.line(polyline_data(list(piece)), "street_centreline",
                           [("data-source", f"{street.source}/paths")])
                pieces_by_name.setdefault(street.name, []).append((street, piece))
                named_lines.append((street.name, piece))
    _mark_subject(sheet, context.subject_lot, fr, rect, TYPOGRAPHY.label_pt, named_lines,
                  with_label=not summary)
    priority = (bordering_street_names(context.subject_lot.outline, context.streets, 140.0)
                if summary else None)
    _label_network(sheet, pieces_by_name, named_lines, rect,
                   TYPOGRAPHY.label_pt + (0.0 if summary else 1.0),
                   priority=priority, pad=5.0 if summary else 1.0)
    draw_frame(sheet, rect)
    if with_title and not summary:
        draw_title(sheet, "Neighbourhood", subtitle_from_bbl(context.subject_lot.bbl),
                   context.subject_lot.bbl_source, region)
    return sheet


def _label_network(sheet: Sheet, pieces_by_name: dict, named_lines, rect: _Box, size: float,
                   priority: set[str] | None = None, pad: float = 1.0) -> None:
    """One name per street, on its longest clipped piece, placed so its box
    crosses NO other street's line and no placed label/marker; dropped otherwise.
    ``priority`` streets are placed first (the lot's own streets win the space)."""
    order = sorted(pieces_by_name)
    if priority:
        pri = [n for n in pieces_by_name if n in priority]
        pri.sort(key=lambda n: (-round(max(polyline_len(p) for _s, p in pieces_by_name[n]), 2), n))
        order = pri + sorted(n for n in pieces_by_name if n not in priority)
    all_lines = [piece for runs in pieces_by_name.values() for _s, piece in runs]
    for name in order:
        runs = pieces_by_name[name]
        _street, piece = max(runs, key=lambda r: polyline_len(r[1]))
        if polyline_len(piece) < STREET_LABEL_MIN_RUN_PT:
            continue
        place(sheet, network_candidates(piece, all_lines, size), name.upper(), size=size,
              source=runs[0][0].name_source, role="street", anchor="middle", style="italic",
              rect=rect, pad=pad, avoid_lines=named_lines, own=name, cross_max_len=2.6 * size)


def _grow(box: Box, pad: float) -> Box:
    return Box(box.x0 - pad, box.y0 - pad, box.x1 + pad, box.y1 + pad)


def _mark_subject(sheet: Sheet, subject: SubjectLot, fr: ViewFrame, rect: _Box,
                  size: float, named_lines, *, with_label: bool = True) -> None:
    """Mark the subject (coral), and - unless ``with_label`` is off - place a
    'Subject lot' label beside it with a leader. The marker, label and leader are
    reserved as one region so no street name crosses any of them (T156-C2 b)."""
    draw_clipped_area(sheet, project_polygon(subject.outline, fr), "subject_lot",
                      subject.outline.source, rect)
    draw_clipped_outline(sheet, project_polygon(subject.outline, fr), "subject_lot",
                         subject.outline.source, rect)
    marker_box = _subject_box(subject, fr)
    cx, cy = (marker_box.x0 + marker_box.x1) / 2.0, (marker_box.y0 + marker_box.y1) / 2.0
    if not with_label:
        sheet.reserve(_grow(marker_box, 3.0))
        return
    # Place the label in open space WITHIN 15 mm of the marker, closest first,
    # with a leader that crosses NO street line; if none exists, draw no label
    # (the legend already explains the coral marker).
    for ring in range(2, 13):
        radius = ring * (size * 0.8)
        if radius > MARKER_LEADER_MAX_PT:
            break
        for ang in range(0, 360, 15):
            rad = math.radians(ang)
            x, y = cx + radius * math.cos(rad), cy + radius * math.sin(rad)
            lx, ly = x, y - size * 0.3  # the leader's label end
            if math.hypot(lx - cx, ly - cy) > MARKER_LEADER_MAX_PT:
                continue
            box = text_box(x, y, "Subject lot", size, "middle", 0.0)
            if not (box.x0 >= rect[0] and box.y0 >= rect[1]
                    and box.x1 <= rect[2] and box.y1 <= rect[3]):
                continue
            if any(box.overlaps(o) for o in sheet.boxes):
                continue
            if box_crosses_lines(box, named_lines, None, 0.5, max_len=2.0):
                continue
            if segment_crosses_lines((cx, cy), (lx, ly), named_lines):
                continue
            sheet.label([(x, y, 0.0)], "Subject lot", size=size, source=None,
                        role="subject_mark", anchor="middle")
            sheet.parts.append(element("path", [
                ("d", polyline_data([(cx, cy), (lx, ly)])), ("fill", "none"),
                ("stroke", "#C8500A"), ("stroke-width", 0.5), ("data-role", "leader")]))
            sheet.reserve(Box(min(marker_box.x0, box.x0) - 1.0, min(marker_box.y0, box.y0) - 1.0,
                              max(marker_box.x1, box.x1) + 1.0, max(marker_box.y1, box.y1) + 1.0))
            return
    sheet.reserve(_grow(marker_box, 3.0))


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
    if frame == "wide":
        fr = fit_view(view, WIDE_PLAN, WIDE_PLAN_MARGIN, alpha=alpha, top_band=0.0)
        rect = viewport(WIDE_PLAN, FRAME_INSET)
        sheet = draw_block_scene(context, fr, rect, WIDE_PLAN, title=None, with_edges=True,
                                 with_widths=True, label_focus=True)
        return compose_context(drawing, title, sheet, fr, summary_notes(frontage_name),
                               mode="wide")
    report = frame == "report"
    region, margin = ((REPORT_PLAN, REPORT_PLAN_MARGIN) if report else (PLAN, PLAN_MARGIN))
    fr = fit_view(view, region, margin, alpha=alpha, top_band=TITLE_BAND_PT)
    rect = viewport(region)
    sheet = draw_block_scene(context, fr, rect, region, title=title, with_edges=True,
                             with_widths=True, label_focus=True)
    notes = caption_notes(context, layers={"tax_lots", "streets", "buildings"}, gaps_note=True,
                          frontage=frontage_name, frontage_source=frontage_source)
    return compose_context(drawing, title, sheet, fr, notes,
                           mode="report" if report else "sheet")
