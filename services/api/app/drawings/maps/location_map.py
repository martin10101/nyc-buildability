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
from .layout import (
    PLAN,
    PLAN_MARGIN,
    REPORT_PLAN,
    REPORT_PLAN_MARGIN,
    compose,
    compose_report,
)
from .model import Drawing, LayerUnavailable, MapContext, MapNote, Unavailable
from .subject import draw_subject_area, label_subject

__all__ = ["draw_location_map"]


def draw_location_map(context: MapContext, *, frame: str = "sheet") -> Drawing | Unavailable:
    """The location map. ``frame='sheet'`` (default) is byte-identical to the committed snapshots;
    ``frame='report'`` is the A4 report composition - no notes column, at most 182 mm by 150 mm,
    labels at least 7 pt - with the attribution still reachable by the caller (ruling X9 a/c)."""
    report = frame == "report"
    layer = context.buildings
    if isinstance(layer, LayerUnavailable):
        return Unavailable("location_map", layer.reason, layer.reason_kind,
                           f"{layer.source}/reason")
    region, margin = (REPORT_PLAN, REPORT_PLAN_MARGIN) if report else (PLAN, PLAN_MARGIN)
    frame_obj = fit(
        [context.subject_lot.outline, *(b.outline for b in layer.footprints)], region, margin
    )
    sheet = Sheet()
    for footprint in layer.footprints:
        rings = [[frame_obj.px(p) for p in ring] for ring in footprint.outline.rings]
        sheet.area(path_data(rings), "building_footprint", [("data-source", footprint.source)])
    draw_subject_area(sheet, context.subject_lot, frame_obj)
    label_subject(sheet, context.subject_lot, frame_obj)

    notes = [
        MapNote(context.measurement_label, context.measurement_source),
        layer.attribution,
    ]
    compose_fn = compose_report if report else compose
    return compose_fn("location_map", "Location map", sheet, frame_obj.k, notes)
