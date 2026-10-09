"""Axonometric massing SVG (plan section 5c items 2 and 5, "3D massing").

Each floor plate from the results is extruded by its floor-to-floor height
from the floor-by-floor table and drawn as a vector box, colored by use from
the style table, shaded by face direction, in painter's order (see
:mod:`.projection`). The lot outline is drawn at grade. A floor table beside
the massing prints each floor's name, gross area and floor-to-floor height,
read from the floor-by-floor rows, with a leader to its floor; rows never
overlap. The legend lists the kinds actually drawn.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import geometry as geo
from .color import mix
from .furniture import case_notes, legend, notes_block, scope_notes
from .hatches import hatch_defs
from .labels import format_area, format_feet, text_box
from .model import Drawing, DrawingInput, FloorPlate, FloorRow, LayerUnavailable, Unavailable
from .projection import SIDE, TOP_LIGHTENING, floor_faces, floor_levels, project
from .sheet import Sheet
from .styles import TYPOGRAPHY, style_for
from .svg import element, open_tag, path_data, polyline_data, svg_document, text_element

__all__ = ["draw_massing"]

CANVAS_W, CANVAS_H = 720.0, 504.0
DRAW = (16.0, 40.0, 480.0, 440.0)  # x0, y0, x1, y1 of the massing region
COL_NAME_X, COL_AREA_X, COL_HEIGHT_X = 516.0, 628.0, 704.0
HEADER_Y = 28.0
ROW_H = 12.0
SWATCH_W = 11.0


@dataclass(frozen=True)
class _Fit:
    k: float
    ox: float
    oy: float
    min_x: float
    max_y: float

    def px(self, x: float, y: float, z: float) -> tuple[float, float]:
        sx, sy = project(x, y, z)
        return self.ox + (sx - self.min_x) * self.k, self.oy + (self.max_y - sy) * self.k


def _fit(points3d: list[tuple[float, float, float]]) -> _Fit:
    projected = [project(*p) for p in points3d]
    min_x, min_y, max_x, max_y = geo.bbox(projected)
    width, height = max(max_x - min_x, 1e-9), max(max_y - min_y, 1e-9)
    avail_w, avail_h = DRAW[2] - DRAW[0], DRAW[3] - DRAW[1]
    k = min(avail_w / width, avail_h / height)
    ox = DRAW[0] + (avail_w - width * k) / 2.0
    oy = DRAW[1] + (avail_h - height * k) / 2.0
    return _Fit(k, ox, oy, min_x, max_y)


def _local(plate: FloorPlate, origin) -> list[tuple[float, float]]:
    return [(x - origin[0], y - origin[1]) for x, y in plate.outline.exterior]


def _draw_floor(sheet: Sheet, faces, fit: _Fit) -> None:
    for face in faces:
        style = style_for(face.plate.use)
        if face.face == SIDE:
            fill = mix(style.fill, "#000000", face.darkening)
        else:
            fill = mix(style.fill, "#FFFFFF", TOP_LIGHTENING)
        rings = [[fit.px(*p) for p in ring] + [fit.px(*ring[0])] for ring in face.rings]
        sheet.area(path_data(rings), face.plate.use,
                   [("data-plate", face.plate.source), ("data-face", face.face)], fill=fill)


def _floor_anchor(floor: int, plates, levels, origin, fit: _Fit) -> tuple[float, float]:
    """Right-most screen point of the floor's plates at mid-height (on a
    viewer-facing side, so the leader reaches a visible face)."""
    z0, z1 = levels[floor]
    return max(fit.px(x, y, (z0 + z1) / 2.0)
               for plate in plates if plate.floor == floor for x, y in _local(plate, origin))


def _row_values(sheet: Sheet, row: FloorRow, y: float, size: float) -> float:
    """One table row: use swatch, floor name, gross area, floor-to-floor height.
    Returns the baseline of the values line (a long name pushes it down)."""
    style = style_for(row.use)
    sheet.parts.append(element("rect", [
        ("x", COL_NAME_X), ("y", y - 6.5), ("width", 7.0), ("height", 7.0),
        ("fill", style.fill), ("stroke", style.outline), ("stroke-width", 0.5),
        ("data-use", row.use)]))
    area, height = format_area(row.gross_sf), format_feet(row.height_ft)
    name_x = COL_NAME_X + SWATCH_W
    two_lines = (text_box(name_x, 0.0, row.label, size).x1 + 4.0
                 > text_box(COL_AREA_X, 0.0, area, size, "end").x0)
    values_y = y + ROW_H if two_lines else y
    sheet.label([(name_x, y, 0.0)], row.label, size=size,
                source=f"{row.source}/floor_label", role="floor_name")
    sheet.label([(COL_AREA_X, values_y, 0.0)], area, size=size,
                source=f"{row.source}/gross_sf", role="floor_area", anchor="end")
    sheet.label([(COL_HEIGHT_X, values_y, 0.0)], height, size=size,
                source=f"{row.source}/height_ft", role="floor_height", anchor="end")
    return values_y


def _floor_table(sheet: Sheet, data: DrawingInput, levels, origin, fit: _Fit) -> float:
    """Rows read from floor_by_floor, grouped by floor (top floor first), one
    leader per floor; rows never overlap. Returns the last baseline."""
    size = TYPOGRAPHY.label_pt
    for x, text, anchor in ((COL_NAME_X, "Floor", "start"), (COL_AREA_X, "Gross area", "end"),
                            (COL_HEIGHT_X, "Floor-to-floor", "end")):
        sheet.parts.append(text_element(x, HEADER_Y, text, size=size, source=None,
                                        role="furniture", anchor=anchor, weight="bold"))
    y = HEADER_Y
    for floor in sorted({row.floor for row in data.floor_rows}, reverse=True):
        ax, ay = _floor_anchor(floor, data.floor_plates, levels, origin, fit)
        y = max(ay + size * 0.35, y + ROW_H)
        sheet.parts.append(element("path", [
            ("d", polyline_data([(ax + 3.0, ay), (COL_NAME_X - 4.0, y - size * 0.35)])),
            ("fill", "none"), ("stroke", "#666666"), ("stroke-width", 0.4),
            ("data-floor", floor)]))
        rows = [row for row in data.floor_rows if row.floor == floor]
        for j, row in enumerate(rows):
            y = _row_values(sheet, row, y + (ROW_H if j else 0.0), size)
    return y


def draw_massing(data: DrawingInput) -> Drawing | Unavailable:
    """The axonometric massing, or Unavailable when there are no floor plates."""
    plates = data.floor_plates
    if isinstance(plates, LayerUnavailable):
        return Unavailable("massing", plates.reason, plates.reason_kind, f"{plates.source}/reason")
    if not plates:
        return Unavailable("massing", "The results list no floor plates.", "missing_input",
                           "/geometry/floor_plates/entries")
    levels = floor_levels(data.floor_rows)
    minx, miny, _, _ = geo.bbox(data.lot.exterior)
    origin = (minx, miny)
    lot_local = [(x - minx, y - miny) for x, y in data.lot.exterior]
    extent = [(x, y, 0.0) for x, y in lot_local]
    for plate in plates:
        z0, z1 = levels[plate.floor]
        extent += [(x, y, z) for x, y in _local(plate, origin) for z in (z0, z1)]
    fit = _fit(extent)

    sheet = Sheet()
    indexed = list(enumerate(plates))
    for floor in sorted(levels):
        if floor == 1:
            lot_rings = [[fit.px(x - minx, y - miny, 0.0) for x, y in ring]
                         for ring in data.lot.rings]
            sheet.line(path_data(lot_rings), "lot_line",
                       [("fill-rule", "evenodd"), ("data-source", data.lot.source)])
        faces = floor_faces(floor, [(i, p) for i, p in indexed if p.floor == floor],
                            levels[floor], origin)
        sheet.parts.append(open_tag("g", [("data-floor", floor)]))
        _draw_floor(sheet, faces, fit)
        sheet.parts.append("</g>")
    if 1 not in levels:  # cellars only: the lot still shows at grade
        lot_rings = [[fit.px(x - minx, y - miny, 0.0) for x, y in ring] for ring in data.lot.rings]
        sheet.line(path_data(lot_rings), "lot_line",
                   [("fill-rule", "evenodd"), ("data-source", data.lot.source)])

    table_bottom = _floor_table(sheet, data, levels, origin, fit)
    legend_parts, legend_bottom = legend(sheet.kinds, COL_NAME_X, table_bottom + 14.0)
    note_parts, note_labels, notes_bottom = notes_block(
        scope_notes(data.scope) + case_notes(data.street_width_case), COL_NAME_X,
        legend_bottom + 10.0, CANVAS_W - COL_NAME_X - 16.0)
    height = max(CANVAS_H, legend_bottom + 12.0, notes_bottom + 12.0)
    svg = svg_document(width=CANVAS_W, height=height, drawing="massing",
                       title="Axonometric massing", defs=hatch_defs(sheet.kinds),
                       body=sheet.parts + legend_parts + note_parts)
    return Drawing("massing", svg, tuple(sheet.labels + note_labels), tuple(sheet.kinds))
