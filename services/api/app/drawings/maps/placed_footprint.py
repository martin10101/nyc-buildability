"""The illustrative building footprint on the site close frame (M5-T173 part B1).

The report's constraints close frame may carry the engine's floor-1 plate (results
contract ``geometry.floor_plates``, part W threads it). This module translates that
results-local plate ring onto the MAP lot by :func:`constraint_overlay.overlay_offset`
(the pure translation that places the min-anchored results outline on the map subject
outline - never a reprojection) and draws it as an ILLUSTRATIVE footprint: a quiet
neutral fill in the ``illustrative_footprint`` style, NOT a use colour and not a
surveyed plan (legend "Illustrative building footprint").

Two edges are dimensioned - the back edge (the plate's width) and one depth edge -
each a FIGURE-ONLY label (the edge's own length, e.g. ``"103.88 ft"``, reusing the
close frame's :data:`DIMENSION_MIN_PT` and figure-only convention) at >= 8.5 pt on a
white background. Both dimension lines fall on the LOT-INTERIOR side (toward the
footprint centroid), so they never meet the lot-edge dimensions the scene draws
outside the lot. The dimensions share the city-map (gis) outline basis the close frame
states once in its note under the drawing, so no basis words sit on the figure and no
tax-map or clearance figure is ever drawn (NB-04; a clearance is not an edge length).

The footprint is drawn ONLY when the input is valid and every dimension label can be
placed: an invalid ring (non-finite, out of range, a point not a pair, under 3 or over
1,000 vertices, zero area, or a vertex more than 0.05 ft outside the subject outline)
or an unplaceable label draws NOTHING of the footprint - no exception, never a shrunk
or partial footprint (S4/S5). Coordinates passed to the frame are the map CRS
(EPSG:2263 US survey feet); screen points come from ``fr.px``.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from shapely import make_valid
from shapely.geometry import Point as ShapelyPoint
from shapely.geometry import Polygon as ShapelyPolygon

from app.drawings.kit.labels import Box, format_feet
from app.drawings.kit.sheet import Sheet
from app.drawings.kit.styles import style_for
from app.drawings.kit.svg import element, num, path_data

from .close_frame_dimensions import DIMENSION_MIN_PT
from .constraint_overlay import overlay_offset
from .context_scene import ViewFrame, place, readable_angle
from .model import Point, Polygon

__all__ = [
    "FOOTPRINT_KIND",
    "FOOTPRINT_SOURCE",
    "DrawnFootprint",
    "draw_placed_footprint",
]

_Box = tuple[float, float, float, float]

# The style kind (the contract literal with part B4's manifest - never renamed) and the
# results pointer the floor-1 plate ring lives at (part W threads the plate; the labels
# name this ring as their source so each figure traces to the document, check C-4).
FOOTPRINT_KIND = "illustrative_footprint"
FOOTPRINT_SOURCE = "/geometry/floor_plates/entries/0/outline/0"

_MAX_MAGNITUDE = 1e9
_MIN_VERTICES = 3
_MAX_VERTICES = 1000
_INSIDE_TOL_FT = 0.05       # a vertex at most this far outside the subject outline is "on" it
_EDGE_TOL_FT = 0.5          # edges within this of the longest/shortest are "width"/"depth" edges
_WITNESS_OFFSET_PT = 10.0   # the dimension line sits this far inside the edge
_LABEL_STEP_PT = 2.0
_LANE_STEPS = 9             # candidate lanes further inward (a wider lane clears a near label)
_ALONG_STEPS = 5            # candidate shifts along the edge, each way


@dataclass(frozen=True)
class DrawnFootprint:
    """One drawn illustrative footprint. ``source_points`` are the results-local ring
    vertices (closed); ``map_points`` are those translated onto the map lot (each the
    document vertex + overlay_offset, S2). ``width_ft`` / ``depth_ft`` are the two drawn
    dimensions' own edge lengths; ``label_boxes`` are the two placed labels (each
    >= 8.5 pt, no collision). Returned only when the WHOLE footprint is drawn."""

    source_points: tuple[Point, ...]
    map_points: tuple[Point, ...]
    width_ft: float
    depth_ft: float
    label_boxes: tuple[Box, Box]


def _finite_pair(value: object) -> Point | None:
    if not (isinstance(value, Sequence) and not isinstance(value, (str, bytes))
            and len(value) == 2):
        return None
    try:
        x, y = float(value[0]), float(value[1])
    except (TypeError, ValueError):
        return None
    if not (math.isfinite(x) and math.isfinite(y)):
        return None
    if abs(x) > _MAX_MAGNITUDE or abs(y) > _MAX_MAGNITUDE:
        return None
    return (x, y)


def _ring_vertices(footprint: object) -> list[Point] | None:
    """The ring as a clean list of finite coordinate pairs, or None if the shape is
    invalid: not a sequence, a point not a pair, a non-finite or out-of-range value, or
    under 3 / over 1,000 vertices (S4)."""
    if not (isinstance(footprint, Sequence) and not isinstance(footprint, (str, bytes))):
        return None
    pts: list[Point] = []
    for value in footprint:
        pair = _finite_pair(value)
        if pair is None:
            return None
        pts.append(pair)
    if not (_MIN_VERTICES <= len(pts) <= _MAX_VERTICES):
        return None
    return pts


def _signed_area(verts: list[Point]) -> float:
    ring = verts if verts[0] == verts[-1] else [*verts, verts[0]]
    return 0.5 * sum(a[0] * b[1] - b[0] * a[1]
                     for a, b in zip(ring, ring[1:], strict=False))


def _edge_len(pts: list[Point], i: int, n: int) -> float:
    a, b = pts[i], pts[(i + 1) % n]
    return math.hypot(b[0] - a[0], b[1] - a[1])


def _adjacent(i: int, j: int, n: int) -> bool:
    return i in ((j + 1) % n, (j - 1) % n)


def _boundary_dist(pts: list[Point], i: int, n: int, poly) -> float:
    a, b = pts[i], pts[(i + 1) % n]
    mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
    return poly.boundary.distance(ShapelyPoint(mid))


def _dimension_edges(map_pts: list[Point], poly) -> tuple[int, int]:
    """The width (back) edge and one depth edge. The width edge is a longest edge, the
    BACK one preferred - the longest edge whose midpoint is farthest from the subject
    boundary (the frontage long edge sits on it). The depth edge is a shortest edge
    adjacent to it, also farthest from the boundary; so both dimension lines fall on the
    lot-interior side and neither meets the lot-edge dimensions."""
    n = len(map_pts)
    lengths = [_edge_len(map_pts, i, n) for i in range(n)]
    lmax, lmin = max(lengths), min(lengths)
    wide = [i for i in range(n) if lengths[i] >= lmax - _EDGE_TOL_FT]
    back = max(wide, key=lambda i: (_boundary_dist(map_pts, i, n, poly), -i))
    deep = [i for i in range(n) if lengths[i] <= lmin + _EDGE_TOL_FT and i != back]
    adj = [i for i in deep if _adjacent(i, back, n)]
    pool = adj or deep or [i for i in range(n) if i != back]
    depth = max(pool, key=lambda i: (_boundary_dist(map_pts, i, n, poly), -i))
    return back, depth


def _dim_line(a: Point, b: Point, kind: str) -> str:
    style = style_for("dimension")  # the shared annotation look (never in the legend)
    return element("path", [
        ("d", f"M{num(a[0])} {num(a[1])} L{num(b[0])} {num(b[1])}"),
        ("fill", "none"), ("stroke", style.outline), ("stroke-width", style.line_weight_pt),
        ("data-role", "dimension-line"), ("data-kind", f"footprint-{kind}")])


def _draw_edge_dimension(
    sheet: Sheet, map_pts: list[Point], i: int, n: int, centroid: Point, fr: ViewFrame,
    rect: _Box, source: str, text: str, size: float, avoid_lines,
) -> Box | None:
    """Draw one edge's witness + dimension lines on the lot-interior side (toward
    ``centroid``) and place its FIGURE-ONLY label beside the dimension line on a white
    background. Returns the placed label box, or None (the whole footprint is then
    withheld - never shrunk or dropped silently; S5)."""
    pa, pb = fr.px(map_pts[i]), fr.px(map_pts[(i + 1) % n])
    elen = math.hypot(pb[0] - pa[0], pb[1] - pa[1]) or 1.0
    ux, uy = (pb[0] - pa[0]) / elen, (pb[1] - pa[1]) / elen
    nx, ny = -uy, ux  # an edge normal; flip it to point toward the footprint interior
    mx, my = (pa[0] + pb[0]) / 2.0, (pa[1] + pb[1]) / 2.0
    if nx * (centroid[0] - mx) + ny * (centroid[1] - my) < 0.0:
        nx, ny = -nx, -ny
    dim_a = (pa[0] + nx * _WITNESS_OFFSET_PT, pa[1] + ny * _WITNESS_OFFSET_PT)
    dim_b = (pb[0] + nx * _WITNESS_OFFSET_PT, pb[1] + ny * _WITNESS_OFFSET_PT)
    sheet.parts.append(_dim_line(pa, dim_a, "witness"))
    sheet.parts.append(_dim_line(pb, dim_b, "witness"))
    sheet.parts.append(_dim_line(dim_a, dim_b, "dimension"))
    dim_lines = [("dimension", [pa, dim_a]), ("dimension", [pb, dim_b]),
                 ("dimension", [dim_a, dim_b])]
    ang = readable_angle(math.degrees(math.atan2(pb[1] - pa[1], pb[0] - pa[0])))
    bmx, bmy = (dim_a[0] + dim_b[0]) / 2.0, (dim_a[1] + dim_b[1]) / 2.0
    step = size + _LABEL_STEP_PT
    grid = [(3.0 + j * step, al * step)
            for j in range(_LANE_STEPS) for al in range(-_ALONG_STEPS, _ALONG_STEPS + 1)]
    grid.sort(key=lambda oa: (oa[0] - 3.0) + abs(oa[1]))
    cands = [(bmx + nx * out + ux * al, bmy + ny * out + uy * al, ang) for out, al in grid]
    return place(sheet, cands, text, size=size, source=source, role="dimension",
                 anchor="middle", rect=rect, pad=2.0,
                 avoid_lines=list(avoid_lines or []) + dim_lines, own=None,
                 cross_max_len=0.0, halo=True)


def draw_placed_footprint(
    sheet: Sheet, footprint: object, subject_outline: Polygon, fr: ViewFrame, rect: _Box, *,
    source: str = FOOTPRINT_SOURCE, size: float = DIMENSION_MIN_PT, avoid_lines=None,
) -> DrawnFootprint | None:
    """Draw the engine's floor-1 plate as an illustrative footprint on the map lot and
    return the :class:`DrawnFootprint`, or None when nothing is drawn.

    ``footprint`` is the results-local floor-1 plate ring (a sequence of ``[x, y]``
    pairs). It is translated onto the map lot by :func:`overlay_offset` and validated;
    an invalid ring or an unplaceable dimension label draws NOTHING (no exception, never
    shrunk or partial; S4/S5). Drawn only on the close frame by its caller."""
    verts = _ring_vertices(footprint)
    if verts is None or abs(_signed_area(verts)) <= 1e-9:
        return None
    local = verts[:-1] if verts[0] == verts[-1] else list(verts)
    n = len(local)
    if n < _MIN_VERTICES:
        return None
    ox, oy = overlay_offset(subject_outline)
    map_pts = [(x + ox, y + oy) for x, y in local]
    poly = make_valid(ShapelyPolygon([(p[0], p[1]) for p in subject_outline.exterior]))
    for mp in map_pts:
        point = ShapelyPoint(mp)
        if not (poly.covers(point) or poly.distance(point) <= _INSIDE_TOL_FT):
            return None
    back, depth = _dimension_edges(map_pts, poly)
    # Plan-then-commit: draw into a temp sheet seeded with the live label boxes; if a
    # label cannot be placed the whole footprint is withheld (nothing is merged).
    tmp = Sheet()
    tmp.boxes = list(sheet.boxes)
    base = len(tmp.boxes)
    screen_ring = [fr.px(p) for p in map_pts]
    screen_ring.append(screen_ring[0])
    tmp.area(path_data([screen_ring]), FOOTPRINT_KIND,
             [("data-source", source), ("data-role", "illustrative-footprint")])
    cx = sum(p[0] for p in screen_ring[:-1]) / n
    cy = sum(p[1] for p in screen_ring[:-1]) / n
    boxes: list[Box] = []
    for i in (back, depth):
        box = _draw_edge_dimension(tmp, map_pts, i, n, (cx, cy), fr, rect,
                                   f"edge:{source}#{i}", format_feet(_edge_len(local, i, n)),
                                   size, avoid_lines)
        if box is None:
            return None  # a dimension could not be placed: withhold the whole footprint
        boxes.append(box)
    sheet.parts.extend(tmp.parts)
    sheet.labels.extend(tmp.labels)
    for kind in tmp.kinds:
        sheet.use_kind(kind)
    sheet.boxes.extend(tmp.boxes[base:])
    closed_map = tuple(map_pts) + (map_pts[0],)
    closed_src = tuple((float(x), float(y)) for x, y in local) + ((float(local[0][0]),
                                                                   float(local[0][1])),)
    return DrawnFootprint(closed_src, closed_map, _edge_len(local, back, n),
                          _edge_len(local, depth, n), (boxes[0], boxes[1]))
