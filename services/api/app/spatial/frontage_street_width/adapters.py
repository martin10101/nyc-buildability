"""Build street-width inputs from the accepted connectors' results (queue item B-04).

No I/O: these read results the connectors already produced - the DCM street center-line
geometry pages the B-03 site geometry was derived from, optionally the DCM layer metadata
(for the dataset's last-edit date) and the PLUTO record (for the lot's zoning districts).
"""

from __future__ import annotations

from collections.abc import Sequence

from app.connectors import pluto_soda
from app.connectors.dcm_street_centerline_arcgis import (
    ATTRIBUTION,
    FEAT_TYPE_MAPPED,
    LayerMetadata,
    StreetSegment,
)
from app.connectors.dcm_street_centerline_geometry import SegmentGeometryPage
from app.spatial.site_geometry.results import SiteGeometry

from .derive import derive_frontage_street_widths
from .exceptions import Zr1210Exceptions
from .inputs import LotZoningContext, MappedStreetSegment, SegmentSource
from .results import SiteStreetWidths

__all__ = [
    "mapped_segments_from_pages",
    "street_widths_from_sources",
    "zoning_context_from_pluto",
]

# The same street-status test the B-03 adapter applies before a segment can front a lot
# (app.spatial.site_geometry.adapters): the documented Feat_Type "Mapped_St" and the
# connector's Y/N special-street flags all "N". Anything else needs review.
_SPECIAL_FLAGS = ("paper_street", "record_street", "stair_street", "marginal_wharf")

# PLUTO zoning-district columns (connector PLUTO_COLUMN_TYPES; SODA omits null columns).
_DISTRICT_FIELDS = ("zonedist1", "zonedist2", "zonedist3", "zonedist4")
_OVERLAY_FIELDS = ("overlay1", "overlay2")


def _street_status(segment: StreetSegment) -> tuple[bool, str | None]:
    if segment.feat_type != FEAT_TYPE_MAPPED:
        return False, (f"the City Map feature type is {segment.feat_type!r}, not a mapped "
                       "street; needs review")
    odd = [f"{flag}={getattr(segment, flag)!r}" for flag in _SPECIAL_FLAGS
           if getattr(segment, flag) != "N"]
    if odd:
        return False, "the City Map flags it (" + ", ".join(odd) + "); needs review"
    return True, None


def mapped_segments_from_pages(
    pages: Sequence[SegmentGeometryPage], *, layer_metadata: LayerMetadata | None = None
) -> tuple[MappedStreetSegment, ...]:
    """Every segment on the pages, with the page it was read from as its source."""
    version = layer_metadata.source_data_last_edited if layer_metadata else None
    segments = []
    for page in pages:
        source = SegmentSource(
            source=ATTRIBUTION,
            source_id=page.source_id,
            dataset=f"{page.service_root}/{page.layer}",
            dataset_version=version,
            request_url=page.request_url,
            retrieved_at=page.retrieved_at,
            raw_digest=page.raw_digest,
        )
        for entry in page.entries:
            segment = entry.segment
            if segment.object_id is None:
                continue
            plain, note = _street_status(segment)
            segments.append(MappedStreetSegment(
                segment.object_id, segment.street_name, segment.borough,
                segment.streetwidth_raw, plain, note, source))
    return tuple(segments)


def _text(facts: dict, name: str) -> str | None:
    value = (facts.get(name) or {}).get("normalized_value")
    return value.strip() if isinstance(value, str) and value.strip() else None


def zoning_context_from_pluto(result: pluto_soda.PlutoFetchResult) -> LotZoningContext:
    """The lot's zoning districts and commercial overlays as PLUTO records them.

    Without ``zonedist1`` the districts are unknown (an overlay alone never stands in for
    them). The community district is left unknown: PLUTO ``cd`` is a coded number whose
    layout is not verified in this repository, so it is not decoded.
    """
    version = result.dataset_version
    source = f"PLUTO {version}" if version else "PLUTO"
    provenance = {
        "source_id": pluto_soda.SOURCE_ID,
        "dataset_version": version,
        "request_url": result.request_url,
        "retrieved_at": result.retrieved_at,
        "response_digest": result.response_digest,
        "fields": list(_DISTRICT_FIELDS + _OVERLAY_FIELDS),
    }
    facts = {fact.get("original_field_name"): fact for fact in result.facts}
    if result.status != "ok" or _text(facts, "zonedist1") is None:
        return LotZoningContext((), None, source, provenance)
    values = [_text(facts, name) for name in _DISTRICT_FIELDS + _OVERLAY_FIELDS]
    districts = tuple(dict.fromkeys(v for v in values if v is not None))
    return LotZoningContext(districts, None, source, provenance)


def street_widths_from_sources(
    site: SiteGeometry,
    street_pages: Sequence[SegmentGeometryPage],
    *,
    pluto_result: pluto_soda.PlutoFetchResult | None = None,
    layer_metadata: LayerMetadata | None = None,
    exceptions: Zr1210Exceptions | None = None,
) -> SiteStreetWidths:
    """Street widths for ``site`` from the same DCM pages it was derived from."""
    zoning = zoning_context_from_pluto(pluto_result) if pluto_result is not None else None
    return derive_frontage_street_widths(
        site, mapped_segments_from_pages(street_pages, layer_metadata=layer_metadata),
        zoning, exceptions=exceptions)
