"""The subject lot, drawn and labelled the same way on both maps.

The lot is filled in the emphasised ``subject_lot`` style so it stands out from
the city-data context, and its BBL label (when the data carries one) is read
from the data, never typed.
"""

from __future__ import annotations

from app.drawings.kit import geometry as geo
from app.drawings.kit.sheet import Sheet
from app.drawings.kit.styles import TYPOGRAPHY
from app.drawings.kit.svg import path_data

from .frame import MapFrame
from .model import SubjectLot

__all__ = ["draw_subject_area", "label_subject"]


def draw_subject_area(sheet: Sheet, lot: SubjectLot, frame: MapFrame) -> None:
    rings = [[frame.px(p) for p in ring] for ring in lot.outline.rings]
    sheet.area(path_data(rings), "subject_lot", [("data-source", lot.outline.source)])


def label_subject(sheet: Sheet, lot: SubjectLot, frame: MapFrame) -> None:
    if lot.bbl is None or lot.bbl_source is None:
        return
    cx, cy = frame.px(geo.centroid(lot.outline.exterior))
    size = TYPOGRAPHY.label_pt
    steps = [0.0, 2.2 * size, -2.2 * size, 4.4 * size, -4.4 * size]
    sheet.label([(cx, cy + s, 0.0) for s in steps], f"BBL {lot.bbl}", size=size,
                source=lot.bbl_source, role="subject_lot", anchor="middle")
