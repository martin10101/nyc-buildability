"""Location map SVG from city open data (plan section 5c item 2).

Draws the surrounding building footprints (OTI Building Footprints dataset) as
neighbourhood context, with the subject lot emphasised on top and labelled by
its BBL read from the data, so the reader can see where the lot sits. No aerial
or street base-map imagery is drawn: a raster base map would need its own
publisher-confirmed licence, which this increment does not carry, so the map is
vector city data only (see docs/samples/maps/README.md).
"""

from __future__ import annotations

from app.drawings.kit.sheet import Sheet
from app.drawings.kit.svg import path_data

from .frame import fit
from .layout import PLAN, PLAN_MARGIN, compose
from .model import Drawing, LayerUnavailable, MapContext, MapNote, Unavailable
from .subject import draw_subject_area, label_subject

__all__ = ["draw_location_map"]


def draw_location_map(context: MapContext) -> Drawing | Unavailable:
    layer = context.buildings
    if isinstance(layer, LayerUnavailable):
        return Unavailable("location_map", layer.reason, layer.reason_kind,
                           f"{layer.source}/reason")
    frame = fit(
        [context.subject_lot.outline, *(b.outline for b in layer.footprints)], PLAN, PLAN_MARGIN
    )
    sheet = Sheet()
    for footprint in layer.footprints:
        rings = [[frame.px(p) for p in ring] for ring in footprint.outline.rings]
        sheet.area(path_data(rings), "building_footprint", [("data-source", footprint.source)])
    draw_subject_area(sheet, context.subject_lot, frame)
    label_subject(sheet, context.subject_lot, frame)

    notes = [
        MapNote(context.measurement_label, context.measurement_source),
        layer.attribution,
    ]
    return compose("location_map", "Location map", sheet, frame.k, notes)
