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

from .close_frame_dimensions import (
    DIMENSION_MIN_PT,
    GIS_BASIS_NOTE,
    dimension_line_segments,
    draw_edge_dimensions,
)
from .constraint_overlay import draw_site_constraints, overlay_was_drawn
from .context_scene import (
    CLOSE_PLAN,
    CLOSE_PLAN_MARGIN,
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
from .placed_footprint import draw_placed_footprint
from .street_areas import (
    MIN_STREET_AREA_SQFT,
    clip_polygon_to_rect,
    clip_polyline_to_rect,
    gaps_in_rect,
)

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
    "dimension_avoid_lines",
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
# The large constraints close frame zooms in tighter so the subject and its
# edge-sharing neighbours DOMINATE and there is room for dimension lanes (M5-T166).
CLOSE_PAD_FT = 52.0
CLOSE_STREET_REACH_FT = 85.0
# Neighbouring buildings are drawn this much lighter on the close frames so the
# subject lot and its dimensions dominate (D-094 R115/R116; S15).
NEIGHBOUR_BUILDING_OPACITY = 0.45
FRONTAGE_STREET_MAX_FT = 90.0  # a street this far outward names a frontage edge
EDGE_MIN_LABEL_FT = 6.0        # shorter edges are left undimensioned
STREET_LABEL_MIN_RUN_PT = 26.0  # a street piece shorter than this (on screen) is not labelled
GAP_NAMED_MIN_PT = 14.0        # a gap is a street only if a centre line runs this far through it
MARKER_LEADER_MAX_PT = 42.0    # the 'Subject lot' leader is at most 15 mm long, crosses no street
SITE_SUMMARY_BORDER_FT = 90.0   # streets this close to the lot border it (site summary)
BLOCK_SUMMARY_BORDER_FT = 230.0  # streets this close border the subject's block (block summary)

_Box = tuple[float, float, float, float]
BOROUGHS = {"1": "Manhattan", "2": "Bronx", "3": "Brooklyn", "4": "Queens", "5": "Staten Island"}


def _view_toward_streets(subject: SubjectLot, streets: StreetLayer,
                         pad_ft: float, reach_ft: float) -> _Box:
    """The subject bbox + ``pad_ft``, pulled out toward any street centre-line point
    within ``reach_ft`` of the lot (capped), so every adjoining street shows
    (deterministic)."""
    base_box = geo.bbox(subject.outline.exterior)
    base = pad_box(base_box, pad_ft)
    reach = pad_box(base_box, reach_ft)
    xs, ys = [base[0], base[2]], [base[1], base[3]]
    for street in streets.streets:
        for path in street.paths:
            for p in path:
                if point_inside(reach, p):
                    xs.append(p[0])
                    ys.append(p[1])
    return (max(min(xs), reach[0]), max(min(ys), reach[1]),
            min(max(xs), reach[2]), min(max(ys), reach[3]))


def site_context_view(subject: SubjectLot, streets: StreetLayer) -> _Box:
    """The site-plan view: the subject bbox + 80 ft, reaching to adjoining streets."""
    return _view_toward_streets(subject, streets, SITE_PAD_FT, SITE_STREET_REACH_FT)


def close_frame_view(subject: SubjectLot, streets: StreetLayer) -> _Box:
    """The tighter large-close-frame view (M5-T166): the subject dominates, reaching
    just far enough to show its fronting streets' centre lines for naming."""
    return _view_toward_streets(subject, streets, CLOSE_PAD_FT, CLOSE_STREET_REACH_FT)


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


def dimension_avoid_lines(context: MapContext, fr: ViewFrame, rect: _Box):
    """The DRAWN lot-boundary polylines a dimension label must not cross on the close
    frame (rework 2): every neighbour lot whose bbox touches the view, projected and
    clipped to the viewport EXACTLY as ``draw_clipped_outline`` draws it, each as
    ('boundary', polyline). The subject lot is omitted: a dimension sits against the
    very edge it measures, and its own witness/dimension lines (drawn separately) are
    the only lines its label may cross (presentation contract section 6; visual G3
    finding 5). Shared with the close-frame test, so what is enforced is checked."""
    lots = context.tax_lots.lots if isinstance(context.tax_lots, TaxLotLayer) else ()
    out = []
    for lot in lots:
        if not lot_bbox_touches(lot.outline, fr, rect):
            continue
        rings = [tuple(r) for r in project_polygon(lot.outline, fr)]
        for poly in clip_polygon_to_rect(rings, rect):
            out.append(("boundary", list(poly)))
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
                             street_lines, *, light_neighbours: bool = False) -> None:
    lots = context.tax_lots.lots if isinstance(context.tax_lots, TaxLotLayer) else ()
    all_lots = [context.subject_lot.outline, *(lot.outline for lot in lots)]
    _draw_street_areas(sheet, all_lots, street_lines, fr, rect, _data_region(context, fr))
    for lot in lots:
        if lot_bbox_touches(lot.outline, fr, rect):
            draw_clipped_outline(sheet, project_polygon(lot.outline, fr), "neighbour_lot",
                                 lot.outline.source, rect)
    subj = context.subject_lot
    subj_sp = make_valid(ShapelyPolygon(subj.outline.exterior))
    # the close frames draw neighbours' buildings lighter so the subject dominates (S15).
    fp_opacity = NEIGHBOUR_BUILDING_OPACITY if light_neighbours else None
    on_subject = []  # existing buildings on the subject lot (drawn as a dashed outline on top)
    if isinstance(context.buildings, BuildingLayer):
        for fp in context.buildings.footprints:
            if not lot_bbox_touches(fp.outline, fr, rect):
                continue
            fp_sp = make_valid(ShapelyPolygon(fp.outline.exterior))
            if fp_sp.area > 0.0 and fp_sp.intersection(subj_sp).area > 0.5 * fp_sp.area:
                on_subject.append(fp)
            else:  # a neighbour's building: grey hatch (lighter on the close frames)
                draw_clipped_area(sheet, project_polygon(fp.outline, fr), "building_footprint",
                                  fp.source, rect, opacity=fp_opacity)
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
                   street_lines=None, avoid_boxes=(), min_pt: float = 0.0,
                   halo: bool = False) -> None:
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
    width_size = max(7.0, min_pt, size - 1.5)
    for name in sorted(best):
        _, piece, street = best[name]
        place(sheet, line_candidates(piece, size), street.name.upper(), size=size,
              source=street.name_source, role="street", anchor="middle", style="italic",
              rect=rect, avoid_lines=street_lines, own=street.name, avoid_boxes=avoid_boxes,
              cross_max_len=2.6 * size, halo=halo)
        if with_width and street.mapped_width_ft is not None:
            wtext = f"{format_number(street.mapped_width_ft)} ft mapped width"
            place(sheet, line_candidates(piece, width_size), wtext, size=width_size,
                  source=street.mapped_width_source, role="street_width", anchor="middle",
                  style="italic", rect=rect, avoid_lines=street_lines, own=street.name,
                  avoid_boxes=avoid_boxes, cross_max_len=2.6 * size, halo=halo)


def _subject_label(sheet: Sheet, subject: SubjectLot, fr: ViewFrame, rect: _Box, size: float,
                   street_lines, *, halo: bool = False) -> None:
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
          avoid_lines=street_lines, own=None, halo=halo)


def _neighbour_label(sheet: Sheet, lot: NeighbourLot, fr: ViewFrame, rect: _Box, size: float,
                     street_lines, avoid_boxes, *, min_pt: float = 0.0,
                     with_address: bool = True, halo: bool = False) -> None:
    """"Lot <n>" (and, unless ``with_address`` is off, the address) placed WELL
    INSIDE the neighbour, clear of the streets and of the subject marker (T155
    cosmetic fix 3; T156-C2). The close frames drop the neighbour address to cut
    clutter - only the lot number stays (S15)."""
    number = _lot_number(lot.bbl)
    cx, cy = fr.px(geo.centroid(lot.outline.exterior))
    if number is not None and lot.bbl_source is not None:
        steps = [0.0, 2.6 * size, -2.6 * size, 5.2 * size]
        place(sheet, [(cx, cy + s, 0.0) for s in steps], f"Lot {number}", size=size,
              source=lot.bbl_source, role="lot_number", anchor="middle", rect=rect, pad=2.5,
              avoid_lines=street_lines, own=None, avoid_boxes=avoid_boxes, halo=halo)
    if with_address and lot.address is not None and lot.address_source is not None:
        asz = max(7.0, min_pt, size - 1.0)
        steps = [size + 2.0, 3.6 * size, -(size + 2.0), 6.0 * size]
        place(sheet, [(cx, cy + s, 0.0) for s in steps], lot.address, size=asz,
              source=lot.address_source, role="lot_address", anchor="middle", rect=rect, pad=2.5,
              avoid_lines=street_lines, own=None, avoid_boxes=avoid_boxes, halo=halo)


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
    street_filter: set[str] | None = None, dimension_style: str = "simple",
    min_label_pt: float = 0.0, close_style: bool = False,
    constraint_lines=None, input_facts=None,
) -> Sheet:
    """The shared coloured scene: even street areas (named gaps only), the subject
    coloured above the existing building, neighbours as thin outlines, buildings
    grey, street names in their street. Labels only the subject (and, when
    ``label_focus``, its edge-sharing neighbours), never across a street.
    ``dimension_style='close'`` draws figure-only dimension lines (M5-T166);
    ``min_label_pt`` raises every scene label to at least that size (the close
    frame keeps all labels at >= 8.5 pt, failing rather than shrinking).
    ``close_style`` (the page-3 and page-1 close frames) puts every scene label on
    a white background, draws neighbouring buildings lighter, and drops neighbour
    addresses so the subject and its dimensions dominate (S14, S15)."""
    assert isinstance(context.streets, StreetLayer)
    sheet = Sheet()
    data_region = _data_region(context, fr)
    street_lines = _street_lines_screen(context.streets, fr, rect, data_region)
    _draw_lots_and_buildings(sheet, context, fr, rect, street_lines,
                             light_neighbours=close_style)
    marker_box = _subject_box(context.subject_lot, fr)
    subj = context.subject_lot
    # On the close frame the dimensions are the focus: place them FIRST so they win
    # the lanes outside the lot, then fit the street/neighbour labels around them.
    dim_lines: list = []
    if with_edges and dimension_style == "close":
        # A dimension is anchored to the edge it measures and sits in the lane just
        # outside it, so it may run parallel to that edge's own fronting street; it is
        # placed first and the street names then avoid its boxes. Its label is kept
        # clear of every drawn lot boundary and street line (rework 2, visual G3 F5),
        # and the lot/street/width labels then also avoid the dimension and witness
        # lines so no dimension line runs along a label (rework 3, defect 2).
        boundary_avoid = street_lines + dimension_avoid_lines(context, fr, rect)
        dims = draw_edge_dimensions(sheet, subj.outline, fr, rect,
                                    size=max(DIMENSION_MIN_PT, min_label_pt),
                                    avoid_lines=boundary_avoid)
        dim_lines = dimension_line_segments(dims)
    label_lines = street_lines + dim_lines
    size = max(TYPOGRAPHY.label_pt + 1.0, min_label_pt)
    _label_streets(sheet, context.streets, fr, rect, size, with_width=with_widths,
                   data_region=data_region, only=street_filter, street_lines=label_lines,
                   avoid_boxes=(marker_box,), min_pt=min_label_pt, halo=close_style)
    subj_label_pt = max(TYPOGRAPHY.label_pt + 2.0, min_label_pt)
    _subject_label(sheet, subj, fr, rect, subj_label_pt, label_lines, halo=close_style)
    if label_focus:
        for lot in edge_sharing_lots(context):
            _neighbour_label(sheet, lot, fr, rect, max(TYPOGRAPHY.label_pt, min_label_pt),
                             label_lines, (marker_box,), min_pt=min_label_pt,
                             with_address=not close_style, halo=close_style)
    if with_edges and dimension_style != "close":
        _draw_edge_lengths(sheet, subj, fr, rect, street_lines)
    # The constraint-line overlay + input_facts' other-basis dimensions (M5-T175):
    # drawn only where constraint_lines/input_facts are passed; the body lives in
    # constraint_overlay.py (near-zero SLOC here; DB-250). Without them the scene is
    # byte-identical (S1). Overlay labels avoid the street and dimension lines.
    if constraint_lines or input_facts:
        # The large close frame (dimension_style='close') carries the overlay labels
        # and the other-basis dimensions; the compact page-1 thumbnail draws the
        # constraint geometry only, named by the legend (it drops dimension labels).
        draw_site_constraints(sheet, context, fr, rect, constraint_lines=constraint_lines,
                              input_facts=input_facts,
                              size=max(DIMENSION_MIN_PT, min_label_pt), avoid_lines=label_lines,
                              with_labels=dimension_style == "close")
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
def draw_site_context_plan(context: MapContext, *, frame: str = "sheet",
                           constraint_lines=None, input_facts=None,
                           placed_footprint=None) -> Drawing | Unavailable:
    """The site plan among its surroundings. Needs the tax lots, the streets and
    the building footprints; any one unavailable returns Unavailable (S6).
    ``constraint_lines`` / ``input_facts`` (results contract 1.5.0) are drawn only on
    the close frames; both default to None, so existing callers are byte-identical
    (S1) and the overlay body lives in constraint_overlay.py (M5-T175).
    ``placed_footprint`` (the engine's results-local floor-1 plate ring, part W threads
    it) is drawn as an illustrative footprint on the CLOSE frame only (M5-T173 B1); None
    keeps every frame byte-identical (S1/S6)."""
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
    if frame == "summary_close":
        # The COMPACT close frame for page 1 (M5-T166 rework 1, G3/G4 F1): the same
        # close COMPOSITION as the page-3 frame - the subject and its edge-sharing
        # neighbours dominate the tight view - at the 88 mm page-1 column. The 88 mm
        # column is too narrow to carry a dimension label at >= 8.5 pt with its basis
        # words, so NO dimension lines are drawn here (the large close frame on page 3
        # carries them); never a bare number. Street widths and neighbour labels are
        # dropped too, keeping the page-1 word budget. No yard/setback area (R008/R017).
        close_view = close_frame_view(context.subject_lot, context.streets)
        fr = fit_view(close_view, SUMMARY_PLAN, SUMMARY_PLAN_MARGIN, alpha=alpha, top_band=0.0)
        rect = viewport(SUMMARY_PLAN, FRAME_INSET)
        border = bordering_street_names(context.subject_lot.outline, context.streets,
                                        SITE_SUMMARY_BORDER_FT)
        # close_style: the page-1 compact close frame gets the same white label
        # backgrounds and lighter neighbouring buildings as the large page-3 frame
        # (S14, S15); it carries no dimensions, so no basis note (K1).
        sheet = draw_block_scene(context, fr, rect, SUMMARY_PLAN, title=None, with_edges=False,
                                 with_widths=False, label_focus=False, street_filter=border,
                                 close_style=True, constraint_lines=constraint_lines,
                                 input_facts=input_facts)
        return compose_context(drawing, title, sheet, fr, summary_notes(frontage_name),
                               mode="summary")
    if frame == "wide":
        fr = fit_view(view, WIDE_PLAN, WIDE_PLAN_MARGIN, alpha=alpha, top_band=0.0)
        rect = viewport(WIDE_PLAN, FRAME_INSET)
        sheet = draw_block_scene(context, fr, rect, WIDE_PLAN, title=None, with_edges=True,
                                 with_widths=True, label_focus=True)
        return compose_context(drawing, title, sheet, fr, summary_notes(frontage_name),
                               mode="wide")
    if frame == "close":
        # The large page-3 constraints close frame (M5-T166, D-094 R014): the subject
        # and its edge-sharing neighbours dominate, dimension lines name the city-map
        # outline basis, every label is at least 8.5 pt, and the 'No building placed'
        # legend entry shows. No rear-yard or setback AREA is drawn (R008/R017).
        close_view = close_frame_view(context.subject_lot, context.streets)
        fr = fit_view(close_view, CLOSE_PLAN, CLOSE_PLAN_MARGIN, alpha=alpha,
                      top_band=TITLE_BAND_PT)
        rect = viewport(CLOSE_PLAN)
        sheet = draw_block_scene(context, fr, rect, CLOSE_PLAN, title=title, with_edges=True,
                                 with_widths=True, label_focus=True, dimension_style="close",
                                 min_label_pt=DIMENSION_MIN_PT, close_style=True,
                                 constraint_lines=constraint_lines, input_facts=input_facts)
        # The dimensions all share the gis basis, so it is stated ONCE in a note under
        # the drawing and each label shows only the figure (owner K1, D-094 R116).
        # When an established constraint is actually DRAWN it adds its own legend entry,
        # so compose_context gives the close frame the full height its furniture needs
        # (overlay_present), keeping the 'No building placed' row off the sources caption
        # (S3; DB-263 A2). overlay_present follows whether a constraint was truly drawn
        # (overlay_was_drawn reads the drawn kinds), NOT the mere presence of the
        # constraint_lines block: the benchmark CARRIES four not_established/not_known
        # items that draw nothing, so its frame stays clamped and byte-identical, as a
        # frame with no overlay at all does (S4; DB-263 F1, correcting round 1's
        # bool(constraint_lines) which grew the benchmark frame 470 -> 474).
        # The engine's floor-1 plate, drawn as an illustrative footprint on the map lot
        # (part B1): an invalid ring or an unplaceable label draws nothing. The
        # 'No building placed' row drops only when a footprint was PASSED (the engine
        # placed the building, even if a degenerate ring draws nothing; S4); a drawn
        # footprint's own legend entry needs the frame's full height, like a constraint
        # overlay's (overlay_present).
        footprint = (None if placed_footprint is None else
                     draw_placed_footprint(sheet, placed_footprint, context.subject_lot.outline,
                                           fr, rect))
        return compose_context(drawing, title, sheet, fr, summary_notes(frontage_name),
                               mode="close", not_placed_legend=placed_footprint is None,
                               basis_note=GIS_BASIS_NOTE,
                               overlay_present=overlay_was_drawn(sheet) or footprint is not None)
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
