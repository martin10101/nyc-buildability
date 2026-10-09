"""Zoning map SVG from city open data (plan section 5c item 2).

Draws the zoning-district polygons around the lot (DCP NYC GIS Zoning Features
``nyzd``), each labelled by its verbatim ``ZONEDIST`` symbol read from the data,
with the subject lot emphasised on top. The map is deliberately NOT a lot-level
zoning determination: the districts share one neutral wash (the symbol is the
only classification, and it is the label), and three sourced notes always
appear - the dataset attribution, the horizontal-accuracy statement, and the
official use limitation that these features are not for lot-level use.
"""

from __future__ import annotations

from app.drawings.kit import geometry as geo
from app.drawings.kit.sheet import Sheet
from app.drawings.kit.styles import TYPOGRAPHY
from app.drawings.kit.svg import path_data

from .frame import fit
from .layout import PLAN, PLAN_MARGIN, compose
from .model import Drawing, LayerUnavailable, MapContext, MapNote, Unavailable
from .subject import draw_subject_area, label_subject

__all__ = ["draw_zoning_map"]


def draw_zoning_map(context: MapContext) -> Drawing | Unavailable:
    layer = context.zoning
    if isinstance(layer, LayerUnavailable):
        return Unavailable("zoning_map", layer.reason, layer.reason_kind,
                           f"{layer.source}/reason")
    frame = fit(
        [context.subject_lot.outline, *(d.outline for d in layer.districts)], PLAN, PLAN_MARGIN
    )
    sheet = Sheet()
    for district in layer.districts:
        rings = [[frame.px(p) for p in ring] for ring in district.outline.rings]
        sheet.area(path_data(rings), "zoning_district", [("data-source", district.source)])
    draw_subject_area(sheet, context.subject_lot, frame)

    size = TYPOGRAPHY.label_pt
    for district in layer.districts:
        cx, cy = frame.px(geo.centroid(district.outline.exterior))
        steps = [0.0, 2.2 * size, -2.2 * size, 4.4 * size, -4.4 * size]
        sheet.label([(cx, cy + s, 0.0) for s in steps], district.symbol, size=size,
                    source=district.symbol_source, role="zoning_district", anchor="middle")
    label_subject(sheet, context.subject_lot, frame)

    notes = [
        MapNote(context.measurement_label, context.measurement_source),
        layer.use_limitation,
        layer.accuracy,
        layer.attribution,
    ]
    return compose("zoning_map", "Zoning map", sheet, frame.k, notes)
