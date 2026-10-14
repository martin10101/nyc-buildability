"""Constraint-line overlay for the site frame (M5-T175, D-094 R017/R044/R053).

The report's constraints close frame - and the page-1 thumbnail that embeds the
same SVG - may carry the results contract 1.5.0 ``geometry.constraint_lines``: the
rear-yard 100 ft line, the corner area, the 8 ft street-wall band and the setback
line. A line or area is drawn ONLY when its state is ``established`` (R017): a
``not_established`` or ``not_known`` item carries NO geometry and draws NOTHING, so
the legend lists only what is drawn (R044). Each drawn item is hatched (an area) or
a distinctive dashed stroke (a line) and labelled with its state and its ZR
section at >= 8.5 pt; a label that cannot be placed without a collision FAILS
rather than shrinks or is dropped (presentation contract section 6; S6). Nothing
here is a DOB determination.

The ``constraint_lines`` are in the RESULTS document's local-feet CRS (origin at
the lot's own minimum); the map frame is EPSG:2263 US survey feet. The two describe
ONE lot (the one-outline check, :func:`page_location.outlines_match`, matches them
vertex-for-vertex after each is shifted to its own minimum), so the transform from
the results frame to the map frame is the PURE TRANSLATION ``offset`` - the subject
outline's minimum (x, y) - never a reprojection. A drawn endpoint therefore lies on
the document's own vertex (within rounding) once the offset is removed (S5).

Each constraint kind has its OWN entry in the style table
(``app.drawings.kit.styles``) - the rear-yard 100 ft line, the corner area and the
street-wall band, beside the setback line - so the legend (generated from the drawn
kinds) names what is drawn and never lists "Setback line" when no setback line is
drawn (visual G3 finding 2; S13). The drawing LABEL still carries the exact
constraint name, its state and its law. Coordinates passed to the frame are the map
CRS; screen points come from ``fr.px``.

An established LINE is drawn only WITHIN the lot outline (S5/S14): each segment is
clipped to the subject lot polygon (``clip_polygon``), so a line that runs past the
lot is drawn only inside it (the clipped ends lie on the outline) and a line wholly
outside the lot draws nothing. The clip never moves or invents a point: an interior
vertex inside the lot stays on the document's own vertex (within rounding). The
label and the legend follow the drawn part.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from shapely import make_valid
from shapely.geometry import LineString
from shapely.geometry import Polygon as ShapelyPolygon

from app.drawings.kit.sheet import Sheet
from app.drawings.kit.svg import path_data, polyline_data

from .close_frame_dimensions import DIMENSION_MIN_PT, draw_other_basis_dimensions
from .context_scene import ViewFrame, place
from .model import Point, Polygon

__all__ = [
    "CONSTRAINT_LABELS",
    "ESTABLISHED",
    "ConstraintOverlayError",
    "DrawnConstraint",
    "draw_constraint_overlay",
    "draw_site_constraints",
    "expand_frame_for_overlay",
    "overlay_offset",
]

_Box = tuple[float, float, float, float]

# Only an established constraint carries geometry and is drawn (R017/R044).
ESTABLISHED = "established"

# The plain-word name each drawn constraint carries on its label (the contract's
# four constraint kinds). The legend shows the reused style kind's label; the
# drawing label shows this name with the state and the law, so a reader can tell
# the rear-yard line from the street-wall band.
CONSTRAINT_LABELS = {
    "rear_yard_100ft_line": "Rear-yard 100 ft line",
    "corner_area": "Corner area",
    "street_wall_band": "Street-wall band",
    "setback_line": "Setback line",
}

# Each constraint kind draws in its OWN style (same name in the style table), so the
# legend names the drawn kind - the rear-yard line as such, never a reused "Setback
# line" (S13; visual G3 finding 2). An unknown kind falls back to a generic hatched
# area / dashed line so it still draws something rather than failing loudly here.
_CONSTRAINT_STYLE = {
    "rear_yard_100ft_line": "rear_yard_100ft_line",
    "corner_area": "corner_area",
    "street_wall_band": "street_wall_band",
    "setback_line": "setback_line",
}
_AREA_FALLBACK = "yard"
_LINE_FALLBACK = "setback_line"


class ConstraintOverlayError(RuntimeError):
    """A constraint label could not be placed at the minimum size without a
    collision. The overlay FAILS rather than shrinking the label below 8.5 pt or
    dropping it silently (presentation contract section 6; S6)."""


@dataclass(frozen=True)
class DrawnConstraint:
    """One drawn constraint line or area. ``source_points`` are the document's own
    vertices (results-local feet, before the map offset), so a caller can prove the
    drawn geometry lies on the document's vertices within tolerance (S5).
    ``screen_points`` are the projected vertices; for a polygon both hold the
    exterior ring. ``style_kind`` is the reused style; ``label_box`` is the placed
    label's bounds (every label >= 8.5 pt, no collision)."""

    kind: str
    state: str
    style_kind: str
    is_polygon: bool
    source_points: tuple[Point, ...]
    screen_points: tuple[Point, ...]
    label_text: str
    label_box: object


def _is_polygon(geometry: Sequence) -> bool:
    """A polygon is a list of rings (each ring a list of points); a line is a list
    of points. Distinguish by the first element: a point is ``[x, y]`` (its first
    item is a number), a ring is ``[[x, y], ...]`` (its first item is a point)."""
    if not geometry:
        return False
    first = geometry[0]
    return (isinstance(first, (list, tuple)) and bool(first)
            and isinstance(first[0], (list, tuple)))


def _translate(points: Sequence, offset: Point) -> tuple[Point, ...]:
    ox, oy = offset
    return tuple((float(p[0]), float(p[1])) for p in points), \
        tuple((float(p[0]) + ox, float(p[1]) + oy) for p in points)


def _clip_line_to_polygon(mapped: Sequence[Point], clip_polygon: Polygon) -> list[list[Point]]:
    """Clip a line (mapped-frame points) to the lot outline polygon (S5/S14).

    Returns the inside pieces, each a list of >= 2 mapped points, in shapely's
    deterministic order; an empty list when the line is wholly outside the lot.
    The clip lies on the line and on the polygon boundary (shapely intersection),
    so a clipped end rests on the outline and an interior vertex inside the lot is
    preserved - no point is moved or invented beyond the clip."""
    poly = make_valid(ShapelyPolygon([tuple(p) for p in clip_polygon.exterior]))
    inter = LineString([tuple(p) for p in mapped]).intersection(poly)
    if inter.is_empty:
        return []
    geoms = list(getattr(inter, "geoms", [inter]))
    pieces: list[list[Point]] = []
    for geom in geoms:
        if geom.geom_type == "LineString" and len(geom.coords) >= 2:
            pieces.append([(float(x), float(y)) for x, y in geom.coords])
    return pieces


def _piece_len(points: Sequence[Point]) -> float:
    return sum(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
               for a, b in zip(points, points[1:], strict=False))


def _label_text(kind: str, state: str, zr_sections: Sequence) -> str:
    name = CONSTRAINT_LABELS.get(kind, kind)
    law = ", ".join(str(s) for s in (zr_sections or []))
    return f"{name}, {state}, {law}" if law else f"{name}, {state}"


def _label_candidates(anchor: Point, size: float):
    """Candidate label positions around the anchor, nearest first, so a long
    constraint label finds a clear spot without being shrunk (S6)."""
    ax, ay = anchor
    step = size + 3.0
    grid = [(0.0, 0.0)]
    for ring in range(1, 7):
        for dx in (0, -1, 1):
            for dy in (-1, 1, 0):
                if dx == 0 and dy == 0:
                    continue
                grid.append((dx * ring, dy * ring))
    grid.sort(key=lambda d: abs(d[0]) + abs(d[1]))
    return [(ax + dx * step, ay + dy * step, 0.0) for dx, dy in grid]


def draw_constraint_overlay(
    sheet: Sheet, constraint_lines: Sequence, fr: ViewFrame, rect: _Box, *,
    offset: Point = (0.0, 0.0), clip_polygon: Polygon | None = None,
    size: float = DIMENSION_MIN_PT, avoid_lines=None, with_labels: bool = True,
) -> list[DrawnConstraint]:
    """Draw the ESTABLISHED constraint lines/areas on the site frame and return the
    drawn constraints (R017/R044/R053). A not_established or not_known item draws
    nothing. Each drawn item is hatched (area) or dashed (line) in its OWN style, so
    the legend names the drawn kind (S13); on the large close frame (``with_labels``)
    it is labelled with its name, state and ZR section at >= ``size`` pt (default 8.5)
    and a label that cannot be placed without a collision raises
    :class:`ConstraintOverlayError` (never shrunk or dropped). The compact page-1
    thumbnail is too narrow for a label at 8.5 pt, so there the geometry is drawn and
    the LEGEND names it (``with_labels=False``). ``offset`` translates the
    results-local geometry into the map frame (the subject outline's minimum).

    When ``clip_polygon`` is given (the subject lot outline, in the map frame), an
    established LINE is drawn only WITHIN it: each segment is clipped to the polygon,
    so a line running past the lot is drawn only inside it and a line wholly outside
    draws nothing (S5/S14). The label and the legend follow the drawn part. A polygon
    constraint is drawn as given (areas are not clipped)."""
    drawn: list[DrawnConstraint] = []
    for item in constraint_lines or []:
        if not isinstance(item, Mapping) or item.get("state") != ESTABLISHED:
            continue  # R017/R044: only an established item carries geometry and is drawn
        geometry = item.get("geometry")
        if not geometry:
            continue
        kind = str(item.get("kind"))
        is_polygon = _is_polygon(geometry)
        if is_polygon:
            source_rings = [_translate(ring, offset) for ring in geometry]
            source_points = source_rings[0][0]
            screen_rings = [[fr.px(p) for p in mapped] for _raw, mapped in source_rings]
            screen_points = tuple(screen_rings[0])
            style_kind = _CONSTRAINT_STYLE.get(kind, _AREA_FALLBACK)
            sheet.area(path_data(screen_rings), style_kind,
                       [("data-role", "constraint-overlay"), ("data-kind", kind)])
            ax = sum(p[0] for p in screen_points) / len(screen_points)
            ay = sum(p[1] for p in screen_points) / len(screen_points)
        else:
            _raw, mapped = _translate(geometry, offset)
            pieces = ([list(mapped)] if clip_polygon is None
                      else _clip_line_to_polygon(mapped, clip_polygon))
            if not pieces:
                continue  # a line wholly outside the lot draws nothing (S5/S14)
            ox, oy = offset
            style_kind = _CONSTRAINT_STYLE.get(kind, _LINE_FALLBACK)
            for piece in pieces:
                sheet.line(polyline_data(piece), style_kind,
                           [("data-role", "constraint-overlay"), ("data-kind", kind)])
            # the LONGEST drawn piece carries the single label and is the recorded part.
            longest = max(pieces, key=_piece_len)
            source_points = tuple((p[0] - ox, p[1] - oy) for p in longest)
            screen_points = tuple(fr.px(p) for p in longest)
            mid = len(screen_points) // 2
            ax, ay = screen_points[mid]
        text = _label_text(kind, str(item.get("state")), item.get("zr_sections"))
        box = None
        if with_labels:
            # The label avoids every placed label (no collisions, S6) via sheet.boxes;
            # it may sit over its own constraint line, so the street/dimension lines are
            # avoided only as a running-along check (cross_max_len = 2 * size), never a
            # bare touch. The white halo keeps it legible over any line.
            box = place(sheet, _label_candidates((ax, ay), size), text, size=size,
                        source=f"constraint_line:{kind}", role="constraint-overlay-label",
                        anchor="middle", rect=rect, pad=1.5, avoid_lines=avoid_lines, own=None,
                        cross_max_len=2.0 * size, halo=True)
            if box is None:
                raise ConstraintOverlayError(
                    f"constraint label {text!r} does not fit at {size} pt without a collision")
        drawn.append(DrawnConstraint(kind, str(item.get("state")), style_kind, is_polygon,
                                     source_points, screen_points, text, box))
    return drawn


def overlay_offset(subject_outline: Polygon) -> Point:
    """The translation from the results-local frame to the map frame: the subject
    outline's minimum (x, y). The results outline is min-anchored and matches the
    map subject outline shifted to its own minimum (``outlines_match``), so adding
    the subject minimum places the results geometry on the map lot (never a
    reprojection)."""
    ring = subject_outline.exterior
    return (min(p[0] for p in ring), min(p[1] for p in ring))


def draw_site_constraints(
    sheet: Sheet, context, fr: ViewFrame, rect: _Box, *, constraint_lines=None,
    input_facts=None, size: float = DIMENSION_MIN_PT, avoid_lines=None,
    with_labels: bool = True,
) -> dict:
    """The thin entry the site frame's hook calls: draw the established
    ``constraint_lines`` (translated onto the map lot by ``overlay_offset``) and,
    on the large close frame (``with_labels``), the ``input_facts``' other-basis lot
    dimensions. Draws nothing when both are absent, so the site frame is
    byte-identical without them (S1). The compact page-1 thumbnail draws the
    constraint geometry only (named by the legend) and no other-basis labels, as it
    already drops its dimension labels. Returns the drawn constraints and facts."""
    out: dict = {}
    if constraint_lines:
        out["constraints"] = draw_constraint_overlay(
            sheet, constraint_lines, fr, rect,
            offset=overlay_offset(context.subject_lot.outline),
            clip_polygon=context.subject_lot.outline, size=size,
            avoid_lines=avoid_lines, with_labels=with_labels)
    if input_facts and with_labels:
        out["facts"] = draw_other_basis_dimensions(
            sheet, input_facts, rect, size=size, avoid_lines=avoid_lines)
    return out


_VIEWBOX_RE = re.compile(r'viewBox="0 0 ([\d.]+) ([\d.]+)"')
_RECT_RE = re.compile(r'<rect\b[^>]*?\sy="([\d.]+)"[^>]*?\sheight="([\d.]+)"')
_TEXT_Y_RE = re.compile(r'<text\b[^>]*?\sy="([\d.]+)"')
# The furniture strip (legend, scale bar, basis note) begins well below the drawing
# viewport; only content past this line can be a legend row that needs more height.
_FURNITURE_TOP_PT = 400.0


def expand_frame_for_overlay(svg: str) -> str:
    """Give the close frame the height its legend needs when the overlay adds a row
    (S13 legend fits). The overlay adds its own constraint entry to the legend, which
    can push the 'No building placed' row past the fixed close-frame height, clipping
    it over the sources caption (visual G3 finding 1). This expands the SVG height and
    viewBox to contain the furniture content with a small margin; it ONLY GROWS the
    frame (never shrinks it), so a frame whose legend already fits - every frame
    without the overlay - is returned byte-identical. No label is moved."""
    box = _VIEWBOX_RE.search(svg)
    if box is None:
        return svg
    width, height_text = box.group(1), box.group(2)
    height = float(height_text)
    bottom = 0.0
    for match in _RECT_RE.finditer(svg):
        top = float(match.group(1))
        if top > _FURNITURE_TOP_PT:
            bottom = max(bottom, top + float(match.group(2)))
    for match in _TEXT_Y_RE.finditer(svg):
        top = float(match.group(1))
        if top > _FURNITURE_TOP_PT:
            bottom = max(bottom, top + 2.0)
    needed = bottom + 8.0
    if needed <= height:
        return svg
    needed_text = f"{needed:.2f}"
    svg = svg.replace(f'viewBox="0 0 {width} {height_text}"',
                      f'viewBox="0 0 {width} {needed_text}"', 1)
    # the <svg> height attribute and the white background rect both carry the height.
    return svg.replace(f'height="{height_text}"', f'height="{needed_text}"', 2)
