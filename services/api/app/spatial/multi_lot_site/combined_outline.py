"""The combined outline: the selected lots' outlines with the lines between them removed.

Plan §4 "Multi-lot sites": "The combined outline is built from the selected lots' outlines,
with the lines between them removed." Built only after the touching check
(``combination.py``) passed, from the conformed outlines it measured (``conform.py``: the
shared lines already have the same end points in both lots). They are joined in one union
and the ring is put in GEOS normal form, so the outline does not depend on lot order. The
result must be one piece without holes, else nothing is measured and the reason says why:
B-03 measures single-ring outlines only.
"""

from __future__ import annotations

from collections.abc import Sequence

import shapely

from app.spatial.site_geometry import LotOutline
from app.spatial.site_geometry.parameters import MIN_LOT_AREA_SQ_FT

from .combination import CombinationCheck, lots_text
from .inputs import SiteLot
from .parameters import METHOD_VERSION, OVERLAP_TOLERANCE_SQ_FT, SHARED_LINE_TOLERANCE_FT
from .results import CombinedOutline

__all__ = ["build_combined_outline"]


def _overlap_reason(check: CombinationCheck) -> str | None:
    overlaps = [c for c in check.contacts if c.overlap_sq_ft > OVERLAP_TOLERANCE_SQ_FT]
    if not overlaps:
        return None
    listed = "; ".join(f"{lots_text([c.first, c.second])} by {c.overlap_sq_ft:,.2f} sq ft"
                       for c in overlaps)
    return ("The tax-map outlines of the selected lots overlap (" + listed + "), so the "
            "combined outline is not built. The tax-map conflict needs review.")


def _hole_reason(union: shapely.Polygon) -> str:
    enclosed = sum(shapely.Polygon(ring).area for ring in union.interiors)
    if enclosed < MIN_LOT_AREA_SQ_FT:
        return (f"The selected lots' tax-map lines leave a gap of {enclosed:,.2f} sq ft inside "
                "the combined outline that is wider than the "
                f"{SHARED_LINE_TOLERANCE_FT:.2f} ft tolerance, so the combined outline is not "
                "built. The tax-map lines need review.")
    return (f"The selected lots enclose {enclosed:,.2f} sq ft of land that is not selected. "
            "A combined outline with a hole is not measured here; select the enclosed lot "
            "too, or enter the measurements.")


def _source(lots: Sequence[SiteLot]) -> str:
    sources = list(dict.fromkeys(lot.outline.source for lot in lots if lot.outline))
    return f"combined {' + '.join(sources)} ({lots_text([lot.bbl for lot in lots])})"


def build_combined_outline(
    check: CombinationCheck, lots: Sequence[SiteLot]
) -> tuple[CombinedOutline | None, LotOutline | None, str | None]:
    """``(combined, outline_to_measure, None)`` or ``(None, None, reason)``."""
    refusal = _overlap_reason(check)
    if refusal:
        return None, None, refusal
    union = shapely.normalize(shapely.union_all([lot.conformed for lot in check.prepared]))
    if union.geom_type != "Polygon":
        return None, None, ("The selected lots do not form one piece of land, so the combined "
                            "outline is not built.")
    if union.interiors:
        return None, None, _hole_reason(union)
    shared = check.combination.shared_lines
    removed = sum(line.length_ft for line in shared)
    lots_area = sum(lot.polygon.area for lot in check.prepared)
    bbls = tuple(lot.bbl for lot in lots)
    statement = (
        f"The combined outline joins {lots_text(bbls)} and removes the lot line(s) they share "
        f"({removed:,.2f} ft). It encloses {union.area:,.2f} sq ft; the lots' own outlines add "
        f"up to {lots_area:,.2f} sq ft ({union.area - lots_area:+,.2f} sq ft).")
    exterior = tuple((float(x), float(y)) for x, y in union.exterior.coords)
    provenance = {
        "method_version": METHOD_VERSION,
        "lots": {lot.bbl: dict(lot.outline.provenance) for lot in lots if lot.outline},
        "shared_lines": [[s.first_bbl, s.second_bbl, s.length_ft] for s in shared],
    }
    outline = LotOutline(exterior, dict(lots[0].outline.crs), _source(lots), provenance)
    combined = CombinedOutline(bbls, exterior, outline.source, shared, round(lots_area, 2),
                               statement)
    return combined, outline, None
