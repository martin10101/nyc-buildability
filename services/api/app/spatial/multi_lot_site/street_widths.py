"""Street widths for the combined site's outside frontages (B-07, through B-04).

The B-04 step (``app.spatial.frontage_street_width``) reads a SiteGeometry, so it runs on
the combined outline's frontages unchanged. Its ZR 12-10 exception check needs the site's
zoning districts: for several lots that is every district recorded for any selected lot (a
district that may trigger an exception on one lot is not dropped), and unknown as soon as
one lot's districts are unknown. The community district is kept only when all lots agree.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from app.spatial.frontage_street_width import (
    LotZoningContext,
    MappedStreetSegment,
    SiteStreetWidths,
    derive_frontage_street_widths,
)
from app.spatial.site_geometry import SiteGeometry

from .combination import lots_text
from .inputs import SiteLot

__all__ = ["combined_street_widths", "combined_zoning"]


def combined_zoning(lots: Sequence[SiteLot]) -> LotZoningContext | None:
    """The zoning context the B-04 exception check uses for the selected lots."""
    if len(lots) == 1:
        return lots[0].zoning
    provenance = {"lots": {lot.bbl: dict(lot.zoning.provenance) if lot.zoning else None
                           for lot in lots}}
    unknown = [lot.bbl for lot in lots if lot.zoning is None or not lot.zoning.zoning_districts]
    if unknown:
        return LotZoningContext((), None, f"zoning districts unknown for {lots_text(unknown)}",
                                provenance)
    contexts = [lot.zoning for lot in lots]
    districts = tuple(dict.fromkeys(d for c in contexts for d in c.zoning_districts))
    community = {c.community_district for c in contexts}
    sources = " + ".join(dict.fromkeys(c.source for c in contexts))
    return LotZoningContext(districts, community.pop() if len(community) == 1 else None,
                            f"{sources} for {lots_text([lot.bbl for lot in lots])}", provenance)


def combined_street_widths(
    geometry: SiteGeometry,
    lots: Sequence[SiteLot],
    segments: Iterable[MappedStreetSegment],
) -> SiteStreetWidths:
    return derive_frontage_street_widths(geometry, segments, combined_zoning(lots))
