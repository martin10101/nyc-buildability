"""The site plan among its surroundings (M5-T155, D-090 R936-R938).

The owner looked at the old site drawing - the lot's outline alone on a blank
page - and said it was "a rectangle on an angle" with "no reference to where he
is". This draws what the competitor's location and site pages draw, and follows
the owner's reference diagram of this lot:

* the subject lot clearly coloured, with its edge lengths;
* the neighbouring tax lots as thin lines, each named "Lot <n>" and its address;
* the existing building footprints as light grey fills;
* the streets as the pale open space between the tax lots, each named in CAPITALS
  along the street with its mapped width where the data gives a plain number;
* the drawing ROTATED so the lot's main street frontage runs horizontally with
  that street at the top (the north arrow then shows true grid north at that
  rotation, and the caption says which frontage it is rotated to).

No law is computed or drawn (ruling Y6/Y8): no yard, corner area, setback,
coverage portion, PROPOSED building footprint or building position, no lot area
and no adjoining-edge length. The "existing buildings" are the factual OTI
Building Footprints layer (the same context the accepted location map draws); the
subject's coral is drawn ON TOP of them, so nothing reads as a placed design. The
caption returned to the caller names every source and its date and states plainly
that the street areas come from the gaps between tax lots and nothing is surveyed.

This module also carries the shared scene helpers the block close-up and the
neighbourhood map reuse. Coordinates are EPSG:2263 US survey feet; nothing is
reprojected; the output is byte-deterministic (S8).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from app.drawings.kit import geometry as geo
from app.drawings.kit.furniture import (
    legend,
    legend_flow,
    notes_block,
    scale_bar,
)
from app.drawings.kit.hatches import hatch_defs
from app.drawings.kit.labels import format_feet, format_number, text_box
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
    Point,
    Polygon,
    StreetLayer,
    SubjectLot,
    TaxLotLayer,
    Unavailable,
)
from .street_areas import StreetArea, clip_street, street_areas
from .subject import draw_subject_area

__all__ = [
    "SITE_PAD_FT",
    "SITE_STREET_REACH_FT",
    "ViewFrame",
    "caption_notes",
    "compose_context",
    "draw_buildings",
    "draw_edge_lengths",
    "draw_lot_addresses",
    "draw_lot_numbers",
    "draw_neighbour_lots",
    "draw_site_context_plan",
    "draw_street_areas",
    "draw_street_centrelines",
    "draw_subject_outline",
    "draw_title",
    "fit_view",
    "frontage_rotation",
    "label_street_lines",
    "label_streets",
    "mark_subject",
    "site_context_view",
    "unavailable_layer",
]

POINTS_PER_INCH = 72.0

# The site plan shows the lot plus about 80 ft of context on each side, extended
# toward any mapped street centre line within SITE_STREET_REACH_FT so the lot's
# adjoining streets are always in view ("adjoining context needed for
# interpretation"), capped at the reach so the view never runs away.
SITE_PAD_FT = 80.0
SITE_STREET_REACH_FT = 150.0

FRONTAGE_STREET_MAX_FT = 90.0  # a street centre line this far outward names a frontage edge
EDGE_MIN_LABEL_FT = 6.0        # an edge shorter than this is not dimensioned (avoids a cramped tag)
STREET_LABEL_MIN_RUN_FT = 24.0  # a street run shorter than this is not labelled on the plan
TITLE_BAND_PT = 28.0           # height reserved at the top of the plan region for the title


# --------------------------------------------------------------------------- #
# A view frame that can be ROTATED (so a street frontage runs horizontal).
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ViewFrame:
    """World (EPSG:2263) -> screen, scaled uniformly, y flipped (grid north up
    before rotation), and rotated by ``alpha`` so a chosen frontage runs
    horizontal. ``north_deg`` is the SVG rotation that turns an up-arrow to point
    at grid north under this rotation."""

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
    window: tuple[float, float, float, float],
    region: tuple[float, float, float, float],
    margin: float,
    *,
    alpha: float = 0.0,
    top_band: float = 0.0,
) -> ViewFrame:
    """Fit ``window`` (the four corners, rotated by ``alpha``) into ``region`` at
    the largest STANDARD architectural/engineering scale that fits, so the scale
    bar states a real 1 in = S ft scale. ``top_band`` reserves height for the
    title."""
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


_Box = tuple[float, float, float, float]


def _pad_box(box: _Box, pad: float) -> _Box:
    return box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad


def _inside(box: tuple[float, float, float, float], p: Point) -> bool:
    return box[0] <= p[0] <= box[2] and box[1] <= p[1] <= box[3]


def site_context_view(
    subject: SubjectLot, streets: StreetLayer
) -> tuple[float, float, float, float]:
    """The site-plan view: the subject bbox + 80 ft, pulled out toward any street
    centre-line point within SITE_STREET_REACH_FT of the lot (capped at the
    reach), so every adjoining street shows and can be named (deterministic)."""
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
# Frontage detection (which edge to level, and the street that names it).
# --------------------------------------------------------------------------- #
def _seg_foot(p: Point, a: Point, b: Point) -> tuple[float, Point]:
    dx, dy = b[0] - a[0], b[1] - a[1]
    length_sq = dx * dx + dy * dy
    if length_sq == 0.0:
        return math.hypot(p[0] - a[0], p[1] - a[1]), a
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / length_sq))
    foot = (a[0] + t * dx, a[1] + t * dy)
    return math.hypot(p[0] - foot[0], p[1] - foot[1]), foot


def _nearest_outward_street(
    mid: Point, nout: Point, streets: Sequence
) -> tuple[str | None, str | None, float | None]:
    name = source = None
    best: float | None = None
    for street in streets:
        for path in street.paths:
            for a, b in zip(path, path[1:], strict=False):
                dist, foot = _seg_foot(mid, a, b)
                if (foot[0] - mid[0]) * nout[0] + (foot[1] - mid[1]) * nout[1] <= 0.0:
                    continue  # the street is not on the outward side of this edge
                if best is None or dist < best:
                    best, name, source = dist, street.name, street.name_source
    return name, source, best


def frontage_rotation(
    subject: SubjectLot, streets: StreetLayer
) -> tuple[float, str | None, str | None]:
    """The rotation that levels the subject's longest street-bordering edge with
    that street at the top, plus the street's name/source. No qualifying edge ->
    (0.0, None, None) (stay north-up)."""
    ring = subject.outline.exterior
    area = geo.signed_area(ring)
    best: tuple[float, Point, str, str] | None = None
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


# --------------------------------------------------------------------------- #
# Scene helpers (shared with the block close-up).
# --------------------------------------------------------------------------- #
def _polygon_touches(polygon: Polygon, window: tuple[float, float, float, float]) -> bool:
    minx, miny, maxx, maxy = geo.bbox(polygon.exterior)
    return not (maxx < window[0] or minx > window[2] or maxy < window[1] or miny > window[3])


def draw_street_areas(sheet: Sheet, areas: Sequence[StreetArea], frame: ViewFrame) -> None:
    for area in areas:
        rings = [[frame.px(p) for p in ring] for ring in area.outline.rings]
        sheet.area(path_data(rings), "street_area", [("data-source", area.outline.source)])


def draw_buildings(
    sheet: Sheet, buildings: BuildingLayer, frame: ViewFrame,
    window: tuple[float, float, float, float],
) -> None:
    for footprint in buildings.footprints:
        if not _polygon_touches(footprint.outline, window):
            continue
        rings = [[frame.px(p) for p in ring] for ring in footprint.outline.rings]
        sheet.area(path_data(rings), "building_footprint", [("data-source", footprint.source)])


def draw_neighbour_lots(
    sheet: Sheet, lots: TaxLotLayer, frame: ViewFrame,
    window: tuple[float, float, float, float],
) -> None:
    for lot in lots.lots:
        if not _polygon_touches(lot.outline, window):
            continue
        rings = [[frame.px(p) for p in ring] for ring in lot.outline.rings]
        sheet.line(path_data(rings), "neighbour_lot",
                   [("fill-rule", "evenodd"), ("data-source", lot.outline.source)])


def draw_subject_outline(sheet: Sheet, subject: SubjectLot, frame: ViewFrame) -> None:
    """Re-stroke the subject's boundary in the emphasised coral on top of the
    existing-building fills, so the lot boundary stays crisp (the fill + hatch is
    drawn earlier by draw_subject_area)."""
    rings = [[frame.px(p) for p in ring] for ring in subject.outline.rings]
    sheet.line(path_data(rings), "subject_lot",
               [("fill-rule", "evenodd"), ("data-source", subject.outline.source)])


def lot_number(bbl: str | None) -> str | None:
    """"<n>" from a 10-digit BBL (1 boro + 5 block + 4 lot); else ``None``."""
    if bbl is not None and len(bbl) == 10 and bbl.isdigit():
        return str(int(bbl[-4:]))
    return None


def _place_if_free(
    sheet: Sheet, candidates: Sequence[tuple[float, float, float]], text: str, *, size: float,
    source: str | None, role: str, anchor: str, style: str | None = None,
) -> bool:
    """Place ``text`` at the first candidate whose box is clear of every reserved
    box; if none is clear, skip it (return False) rather than overlap."""
    for x, y, rot in candidates:
        box = text_box(x, y, text, size, anchor, rot)
        if not any(box.overlaps(other) for other in sheet.boxes):
            sheet.label([(x, y, rot)], text, size=size, source=source, role=role, anchor=anchor,
                        style=style)
            return True
    return False


def draw_lot_numbers(
    sheet: Sheet, context: MapContext, frame: ViewFrame,
    window: tuple[float, float, float, float],
) -> None:
    """"Lot <n>" for the subject (most prominent) and every neighbouring tax lot
    drawn (owner reference, cue 2), at the lot centroid. Read from the BBL."""
    for outline, bbl, bbl_source, size in _lots_for_labels(context, window):
        number = lot_number(bbl)
        if number is None or bbl_source is None:
            continue
        cx, cy = frame.px(geo.centroid(outline.exterior))
        steps = [0.0, 2.4 * size, -2.4 * size, 4.8 * size, -4.8 * size]
        sheet.label([(cx, cy + s, 0.0) for s in steps], f"Lot {number}", size=size,
                    source=bbl_source, role="lot_number", anchor="middle")


def draw_lot_addresses(
    sheet: Sheet, context: MapContext, frame: ViewFrame,
    window: tuple[float, float, float, float],
) -> None:
    """The address under each neighbouring lot's number, where the data has one -
    placed LAST and skipped if it would overlap (so the essential labels win)."""
    if not isinstance(context.tax_lots, TaxLotLayer):
        return
    size = TYPOGRAPHY.label_pt - 1.0
    for lot in context.tax_lots.lots:
        if lot.address is None or lot.address_source is None:
            continue
        if not _polygon_touches(lot.outline, window):
            continue
        cx, cy = frame.px(geo.centroid(lot.outline.exterior))
        steps = [1.0, 3.4, -3.4, 5.8, -5.8, 8.2, -8.2]
        candidates = [(cx, cy + size + s * size / 2.0, 0.0) for s in steps]
        _place_if_free(sheet, candidates, lot.address, size=size, source=lot.address_source,
                       role="lot_address", anchor="middle")


def _lots_for_labels(context: MapContext, window: tuple[float, float, float, float]):
    subject = context.subject_lot
    rows = [(subject.outline, subject.bbl, subject.bbl_source, TYPOGRAPHY.label_pt + 2.0)]
    if isinstance(context.tax_lots, TaxLotLayer):
        for lot in context.tax_lots.lots:
            rows.append((lot.outline, lot.bbl, lot.bbl_source, TYPOGRAPHY.label_pt))
    return [r for r in rows if _polygon_touches(r[0], window)]


def _readable(angle_deg: float) -> float:
    if angle_deg >= 90.0:
        return angle_deg - 180.0
    if angle_deg < -90.0:
        return angle_deg + 180.0
    return angle_deg


def _along(pa: Point, pb: Point, normal: Point, offset: float, size: float, steps: int = 5):
    angle = _readable(math.degrees(math.atan2(pb[1] - pa[1], pb[0] - pa[0])))
    mx, my = (pa[0] + pb[0]) / 2.0, (pa[1] + pb[1]) / 2.0
    return [(mx + normal[0] * (offset + i * (size + 2.0)),
             my + normal[1] * (offset + i * (size + 2.0)), angle) for i in range(steps)]


@dataclass(frozen=True)
class _StreetLabel:
    name: str
    name_source: str
    mapped_width_ft: float | None
    mapped_width_source: str | None
    path: Sequence[Point]
    length: float


def label_streets(
    sheet: Sheet, areas: Sequence[StreetArea], frame: ViewFrame, size: float,
    *, min_run_ft: float = STREET_LABEL_MIN_RUN_FT, with_width: bool = True,
) -> None:
    """Each street's name in CAPITALS (and '<n> ft mapped width' where the data
    gives a number) once, along its longest run through any area (deduplicated by
    name, deterministic)."""
    best: dict[str, _StreetLabel] = {}
    for area in areas:
        for run in area.runs:
            if run.length_ft < min_run_ft:
                continue
            if run.name not in best or run.length_ft > best[run.name].length:
                best[run.name] = _StreetLabel(run.name, run.name_source, run.mapped_width_ft,
                                              run.mapped_width_source, run.path, run.length_ft)
    _emit_street_labels(sheet, best, frame, size, with_width=with_width)


def label_street_lines(
    sheet: Sheet, streets: StreetLayer, frame: ViewFrame, size: float,
    window: tuple[float, float, float, float], *, min_run_ft: float = STREET_LABEL_MIN_RUN_FT,
    with_width: bool = True,
) -> None:
    """Place each street's name in CAPITALS (and its mapped width where the data
    gives a number and ``with_width``) once, along the longest clipped piece in
    the window."""
    best: dict[str, _StreetLabel] = {}
    for street in streets.streets:
        pieces = clip_street(street, window)
        if not pieces:
            continue
        longest = max(pieces, key=_polyline_length)
        length = _polyline_length(longest)
        if length < min_run_ft:
            continue
        if street.name not in best or length > best[street.name].length:
            best[street.name] = _StreetLabel(street.name, street.name_source,
                                             street.mapped_width_ft, street.mapped_width_source,
                                             longest, length)
    _emit_street_labels(sheet, best, frame, size, with_width=with_width)


def _emit_street_labels(
    sheet: Sheet, best: dict[str, _StreetLabel], frame: ViewFrame, size: float, *, with_width: bool,
) -> None:
    for name in sorted(best):
        label = best[name]
        poly = [frame.px(p) for p in label.path]
        name_box = sheet.label(_line_candidates(poly, size), label.name.upper(), size=size,
                               source=label.name_source, role="street", anchor="middle",
                               style="italic")
        sheet.reserve(name_box)
        if (with_width and label.mapped_width_ft is not None
                and label.mapped_width_source is not None):
            width_text = f"{format_number(label.mapped_width_ft)} ft mapped width"
            wsize = max(7.0, size - 1.5)
            box = sheet.label(_line_candidates(poly, wsize), width_text, size=wsize,
                              source=label.mapped_width_source, role="street_width",
                              anchor="middle", style="italic")
            sheet.reserve(box)


def _line_candidates(poly: Sequence[Point], size: float):
    """Candidate label spots sampled along the whole projected polyline (several
    points, each on the line and to either side), so a street name routes clear
    of the lot labels reserved before it."""
    segs = [(a, b) for a, b in zip(poly, poly[1:], strict=False) if geo.edge_length(a, b) > 1e-6]
    if not segs:
        return [(poly[0][0], poly[0][1], 0.0)]
    lengths = [geo.edge_length(a, b) for a, b in segs]
    total = sum(lengths) or 1.0
    out = []
    for frac in (0.5, 0.35, 0.65, 0.22, 0.78, 0.12, 0.88):
        target = frac * total
        acc = 0.0
        for (a, b), seg_len in zip(segs, lengths, strict=False):
            if acc + seg_len >= target or (a, b) == segs[-1]:
                t = (target - acc) / seg_len if seg_len else 0.0
                mid = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                ux, uy = (b[0] - a[0]) / seg_len, (b[1] - a[1]) / seg_len
                n = (-uy, ux)
                angle = _readable(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])))
                for off, direction in ((0.0, n), (size + 2.0, n), (size + 2.0, (-n[0], -n[1]))):
                    out.append((mid[0] + direction[0] * off, mid[1] + direction[1] * off, angle))
                break
            acc += seg_len
    return out


def draw_street_centrelines(
    sheet: Sheet, streets: StreetLayer, frame: ViewFrame,
    window: tuple[float, float, float, float],
) -> None:
    """Draw the street NETWORK as centre lines clipped to the window (the block
    and neighbourhood maps)."""
    for street in streets.streets:
        for piece in clip_street(street, window):
            sheet.line(polyline_data([frame.px(p) for p in piece]), "street_centreline",
                       [("data-source", f"{street.source}/paths")])


def _polyline_length(coords: Sequence[Point]) -> float:
    return sum(geo.edge_length(a, b) for a, b in zip(coords, coords[1:], strict=False))


def mark_subject(sheet: Sheet, subject: SubjectLot, frame: ViewFrame, size: float) -> None:
    """Mark the subject lot on a small-scale map: the coral fill/outline plus a
    'Subject lot' label beside it (the lot itself is tiny at the neighbourhood
    scale)."""
    draw_subject_area(sheet, subject, frame)
    draw_subject_outline(sheet, subject, frame)
    cx, cy = frame.px(geo.centroid(subject.outline.exterior))
    candidates = []
    for ring in range(1, 7):
        radius = ring * (size + 4.0)
        for ang in range(0, 360, 45):
            rad = math.radians(ang)
            candidates.append((cx + radius * math.cos(rad), cy + radius * math.sin(rad), 0.0))
    sheet.label(candidates, "Subject lot", size=size, source=None, role="subject_mark",
                anchor="middle")


def draw_edge_lengths(sheet: Sheet, subject: SubjectLot, frame: ViewFrame) -> None:
    """Each subject edge's drawing length (a measure of the outline, ruling Y6),
    just outside the lot, read along the edge. Edges under EDGE_MIN_LABEL_FT are
    left undimensioned."""
    ring = subject.outline.exterior
    area = geo.signed_area(ring)
    size = TYPOGRAPHY.dimension_pt
    for i, (a, b) in enumerate(geo.edges(ring)):
        if geo.edge_length(a, b) < EDGE_MIN_LABEL_FT:
            continue
        nx, ny = geo.outward_normal(a, b, area)
        pa, pb = frame.px(a), frame.px(b)
        # outward in screen space (the frame may be rotated AND y-flipped).
        n_screen = _screen_outward(a, b, (nx, ny), frame)
        sheet.label(_along(pa, pb, n_screen, 4.0, size, 6), format_feet(geo.edge_length(a, b)),
                    size=size, source=f"edge:{subject.outline.source}/0#{i}", role="dimension",
                    anchor="middle")


def _screen_outward(a: Point, b: Point, nout_world: Point, frame: ViewFrame) -> Point:
    """The world outward normal expressed as a unit screen vector (so the label
    sits OUTSIDE the lot whatever the rotation)."""
    mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
    tip = (mid[0] + nout_world[0], mid[1] + nout_world[1])
    pm, pt = frame.px(mid), frame.px(tip)
    dx, dy = pt[0] - pm[0], pt[1] - pm[1]
    length = math.hypot(dx, dy) or 1.0
    return (dx / length, dy / length)


def draw_title(
    sheet: Sheet, title: str, subject: SubjectLot,
    region: tuple[float, float, float, float],
) -> None:
    size = TYPOGRAPHY.title_pt
    x = region[0] + 6.0
    y = region[1] + size + 2.0
    sheet.parts.append(text_element(x, y, title, size=size, source=None, role="title",
                                    weight="bold"))
    sheet.labels.append(Label(title, None, "title"))
    if subject.bbl is not None and subject.bbl_source is not None:
        lot_text = f"BBL {subject.bbl}"
        sheet.parts.append(text_element(x, y + size + 1.0, lot_text, size=TYPOGRAPHY.label_pt,
                                        source=subject.bbl_source, role="title"))
        sheet.labels.append(Label(lot_text, subject.bbl_source, "title"))


def caption_notes(
    context: MapContext, *, layers: set[str], gaps_note: bool = False,
    frontage: str | None = None, frontage_source: str | None = None,
) -> list[MapNote]:
    """The sources-and-dates caption returned to the caller (ruling Y7; S5): the
    outline basis, the attribution (with its edit date, in plain words) of each
    layer the drawing actually shows, the rotation note, and the honesty notes -
    for the site plan, that the street areas come from the gaps between tax lots -
    and always that it is map geometry only, nothing is surveyed, and tax
    boundaries do not establish the legal zoning lot. No URL, field name or code
    word appears in any of this text."""
    notes = [MapNote(context.measurement_label, context.measurement_source)]
    if "tax_lots" in layers and isinstance(context.tax_lots, TaxLotLayer):
        notes.append(context.tax_lots.attribution)
    if "streets" in layers and isinstance(context.streets, StreetLayer):
        notes.append(context.streets.attribution)
    if "buildings" in layers and isinstance(context.buildings, BuildingLayer):
        notes.append(context.buildings.attribution)
    if frontage is not None and frontage_source is not None:
        notes.append(MapNote(f"Rotated to the {frontage} frontage.", frontage_source))
    if gaps_note:
        notes.append(MapNote(
            "Street areas are drawn from the gaps between the tax lots.",
            "/map_context/tax_lots"))
    notes.append(MapNote(
        "Map geometry only; tax boundaries do not establish the legal zoning lot; "
        "nothing is surveyed.",
        "/map_context/subject_lot"))
    return notes


# --------------------------------------------------------------------------- #
# Composition (manual, so the north arrow can be rotated to grid north).
# --------------------------------------------------------------------------- #
def _north(cx: float, top: float, deg: float) -> list[str]:
    """A grid-north arrow that rotates to point at grid north under the drawing's
    rotation, with the 'Grid north' caption kept HORIZONTAL (so it never tilts or
    clips, even at a large frontage rotation). The glyph matches the kit arrow."""
    cy = top + 28.0
    size = TYPOGRAPHY.label_pt
    arrow = element("path", [
        ("d", f"M{num(cx)} {num(cy - 18.0)} L{num(cx + 7.0)} {num(cy + 18.0)} "
              f"L{num(cx)} {num(cy + 9.0)} L{num(cx - 7.0)} {num(cy + 18.0)} Z"),
        ("fill", "#000000"), ("stroke", "#000000"), ("stroke-width", 0.5),
    ])
    transform = f'rotate({num(deg)} {num(cx)} {num(cy)})' if abs(deg) >= 1e-9 else None
    glyph_open = f'<g data-role="north-arrow"{f" transform=\"{transform}\"" if transform else ""}>'
    return [
        glyph_open,
        arrow,
        text_element(cx, cy - 22.0, "N", size=size + 2, source=None, role="furniture",
                     anchor="middle", weight="bold"),
        "</g>",
        text_element(cx - 2.0, cy + 30.0, "Grid north", size=size, source=None, role="furniture"),
    ]


def compose_context(
    drawing: str, title: str, sheet: Sheet, frame: ViewFrame, notes: Sequence[MapNote],
    *, report: bool,
) -> Drawing:
    """Assemble the scene plus the furniture. ``report`` gives the wave-21 report
    frame (no notes column, at most 182 mm by 150 mm, notes returned as Labels);
    otherwise the full sheet with the right-hand panel. The north arrow is rotated
    to point at grid north under the drawing's rotation."""
    if report:
        panel = _north(REPORT_NORTH_CX, REPORT_FURN_TOP, frame.north_deg)
        bar_parts, bar_labels = scale_bar(REPORT_SCALE_X, REPORT_FURN_TOP + 16.0, frame.k, 150.0)
        legend_parts, legend_bottom = legend_flow(
            sheet.kinds, REPORT_LEGEND_X, REPORT_FURN_TOP, REPORT_CANVAS_W - REPORT_LEGEND_X - 8.0)
        height = min(REPORT_MAX_H_PT, max(REPORT_FURN_TOP + 46.0, legend_bottom) + 10.0)
        body = sheet.parts + panel + bar_parts + legend_parts
        svg = svg_document(width=REPORT_CANVAS_W, height=height, drawing=drawing, title=title,
                           defs=hatch_defs(sheet.kinds), body=body)
        note_labels = [Label(note.text, note.source, "note") for note in notes]
        return Drawing(drawing, svg, tuple(sheet.labels + bar_labels + note_labels),
                       tuple(sheet.kinds))
    panel = _north(PANEL_X + 20.0, 16.0, frame.north_deg)
    bar_parts, bar_labels = scale_bar(PANEL_X, 88.0, frame.k, 160.0)
    legend_parts, legend_bottom = legend(sheet.kinds, PANEL_X, 118.0)
    note_parts, note_labels, notes_bottom = notes_block(
        map_notes(notes), PANEL_X, legend_bottom + 10.0, PANEL_W)
    height = max(CANVAS_H, notes_bottom + 12.0)
    body = sheet.parts + panel + bar_parts + legend_parts + note_parts
    svg = svg_document(width=CANVAS_W, height=height, drawing=drawing, title=title,
                       defs=hatch_defs(sheet.kinds), body=body)
    return Drawing(drawing, svg, tuple(sheet.labels + bar_labels + note_labels),
                   tuple(sheet.kinds))


def unavailable_layer(name: str, layer: object, source: str) -> Unavailable | None:
    """Return an Unavailable for a layer that is absent (``None``) or
    ``not_available`` - the drawing never draws a partial picture (S6)."""
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
    the building footprints; any one unavailable returns Unavailable with its
    reason, never a partial picture (S6)."""
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
    assert isinstance(context.tax_lots, TaxLotLayer)
    assert isinstance(context.streets, StreetLayer)
    assert isinstance(context.buildings, BuildingLayer)

    view = site_context_view(context.subject_lot, context.streets)
    alpha, frontage_name, frontage_source = frontage_rotation(context.subject_lot, context.streets)
    report = frame == "report"
    region, margin = (REPORT_PLAN, REPORT_PLAN_MARGIN) if report else (PLAN, PLAN_MARGIN)
    fr = fit_view(view, region, margin, alpha=alpha, top_band=TITLE_BAND_PT)

    lots_for_gaps = [context.subject_lot.outline, *(lot.outline for lot in context.tax_lots.lots)]
    areas = street_areas(view, lots_for_gaps, context.streets.streets)

    sheet = Sheet()
    draw_street_areas(sheet, areas, fr)
    draw_subject_area(sheet, context.subject_lot, fr)
    draw_neighbour_lots(sheet, context.tax_lots, fr, view)
    draw_buildings(sheet, context.buildings, fr, view)
    draw_subject_outline(sheet, context.subject_lot, fr)
    # Place the essential labels first (lot numbers, edge dimensions, street names
    # and widths); the addresses go LAST and are skipped if they would overlap, so
    # the essential labels always win (S4: no overlaps on the report frame).
    draw_lot_numbers(sheet, context, fr, view)
    draw_edge_lengths(sheet, context.subject_lot, fr)
    label_streets(sheet, areas, fr, TYPOGRAPHY.label_pt + 1.0)
    draw_lot_addresses(sheet, context, fr, view)
    draw_title(sheet, "Site plan: the lot among its neighbours", context.subject_lot, region)

    notes = caption_notes(context, layers={"tax_lots", "streets", "buildings"}, gaps_note=True,
                          frontage=frontage_name, frontage_source=frontage_source)
    return compose_context(drawing, "Site plan: the lot among its neighbours", sheet, fr, notes,
                           report=report)
