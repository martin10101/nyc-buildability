"""Build a :class:`~.inputs.SiteLot` from the accepted connectors' results (B-07).

No I/O. The outline goes through B-03's MapPLUTO adapter (EPSG:2263 only, fail closed), the
city records and zoning districts through the B-03 / B-04 PLUTO adapters. The B-05 result is
passed through as given. A result for a different lot than the one named is refused.
"""

from __future__ import annotations

from app.connectors import pluto_soda
from app.connectors.mappluto_geometry_arcgis import LotGeometryResult
from app.profile.existing_floor_area import ExistingFloorAreaResult
from app.spatial.frontage_street_width import zoning_context_from_pluto
from app.spatial.site_geometry import city_records_from_pluto, lot_outline_from_mappluto

from .inputs import SiteLot

__all__ = ["NO_MAPPLUTO_RESULT", "site_lot_from_sources"]

NO_MAPPLUTO_RESULT = "No MapPLUTO outline was fetched for this lot."


def site_lot_from_sources(
    bbl: str,
    lot_result: LotGeometryResult | None,
    pluto_result: pluto_soda.PlutoFetchResult | None = None,
    *,
    existing_floor_area: ExistingFloorAreaResult | None = None,
) -> SiteLot:
    """One tax lot's inputs from its MapPLUTO geometry, PLUTO row and B-05 result."""
    for name, result_bbl in (("MapPLUTO", lot_result.requested_bbl if lot_result else bbl),
                             ("PLUTO", pluto_result.bbl if pluto_result else bbl)):
        if result_bbl != bbl:
            raise ValueError(f"the {name} result is for {result_bbl}, not tax lot {bbl}")
    outline, refusal = (None, NO_MAPPLUTO_RESULT) if lot_result is None else (
        lot_outline_from_mappluto(lot_result))
    records = city_records_from_pluto(pluto_result) if pluto_result is not None else None
    zoning = zoning_context_from_pluto(pluto_result) if pluto_result is not None else None
    provenance = {
        "outline": dict(outline.provenance) if outline else None,
        "city_records": dict(records.provenance) if records else None,
    }
    return SiteLot(bbl, outline, refusal, records, zoning, existing_floor_area, provenance)
