"""Build site-geometry inputs from the accepted connectors' results (queue item B-03).

No I/O: these read results the connectors already produced (MapPLUTO lot geometry in
EPSG:2263, DCM street center-line geometry pages, the PLUTO record). Each adapter fails
closed with a plain reason rather than passing on something it cannot vouch for.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from urllib.parse import parse_qs, urlsplit

from app.connectors import pluto_soda
from app.connectors.dcm_street_centerline_arcgis import FEAT_TYPE_MAPPED, StreetSegment
from app.connectors.dcm_street_centerline_arcgis import SOURCE_ID as DCM_SOURCE_ID
from app.connectors.dcm_street_centerline_geometry import SegmentGeometryPage
from app.connectors.mappluto_geometry_arcgis import (
    GEOMETRY_REPAIRED,
    GEOMETRY_VALID,
    OUTCOME_SINGLE,
    LotGeometryResult,
)
from app.connectors.mappluto_geometry_arcgis import SOURCE_ID as MAPPLUTO_SOURCE_ID

from .derive import derive_site_geometry, refused_site_geometry
from .inputs import CityRecordLot, LotOutline, StreetCenterline, StreetData
from .outline import crs_is_measurement_grade
from .results import SiteGeometry

__all__ = [
    "SHAPE_PRESERVING_REPAIRS",
    "city_records_from_pluto",
    "derive_site_geometry_from_sources",
    "lot_outline_from_mappluto",
    "street_data_from_pages",
]

# MapPLUTO connector repairs that do not move the outline (ring closure, dropping a repeated
# vertex). Any other repair (e.g. make_valid) changes the shape, so it is not measured.
SHAPE_PRESERVING_REPAIRS = frozenset({"ring_closure", "drop_consecutive_duplicate_vertices"})

# DCM flags that make a segment something other than a plain mapped street (the connector's
# documented Y/N fields). Their meaning for frontage is not decided here: review.
_SPECIAL_FLAGS = ("paper_street", "record_street", "stair_street", "marginal_wharf")


def lot_outline_from_mappluto(result: LotGeometryResult) -> tuple[LotOutline | None, str | None]:
    """The EPSG:2263 MapPLUTO outline as a :class:`LotOutline`, or ``(None, reason)``."""
    if result.outcome != OUTCOME_SINGLE or result.review_required:
        return None, (f"MapPLUTO returned '{result.outcome}' for this lot and flags it for "
                      "review; one outline is needed to measure it.")
    geometry = result.geometry
    if geometry is None or geometry.canonical_geometry is None:
        return None, "MapPLUTO has no usable outline for this lot."
    if geometry.status == GEOMETRY_REPAIRED:
        methods = {str(repair.get("method")) for repair in geometry.repairs}
        if not methods <= SHAPE_PRESERVING_REPAIRS:
            return None, ("The MapPLUTO outline needed a repair that changes its shape ("
                          + ", ".join(sorted(methods)) + "); it is not measured.")
    elif geometry.status != GEOMETRY_VALID:
        return None, f"The MapPLUTO outline is not usable ({geometry.status})."
    if len(geometry.canonical_geometry) != 1:
        return None, ("The MapPLUTO outline has several separate parts; only single-part "
                      "lots are measured here.")
    if len(geometry.canonical_geometry[0]) != 1:
        return None, "The MapPLUTO outline has a hole; such lots are not measured here."
    # Measure the verbatim source ring (the connector's own area uses it too); the
    # canonical form is rounded to 0.01 ft for digests only.
    raw = result.features[0].get("geometry") if len(result.features) == 1 else None
    raw_rings = raw.get("rings") if isinstance(raw, dict) else None
    if not isinstance(raw_rings, list) or len(raw_rings) != 1:
        return None, "The MapPLUTO outline is not one simple ring; it is not measured here."
    version = (result.attributes or {}).get("Version")
    source = f"MapPLUTO {version} tax-lot" if isinstance(version, str) else "MapPLUTO tax-lot"
    provenance = {
        "source_id": MAPPLUTO_SOURCE_ID,
        "bbl": result.requested_bbl,
        "dataset_version": version,
        "request_url": result.request_url,
        "retrieved_at": result.retrieved_at,
        "raw_digest": result.raw_digest,
        "normalized_digest": result.normalized_digest,
        "geometry_status": geometry.status,
        "source_data_last_edited": result.source_data_last_edited,
    }
    ring = raw_rings[0]
    if not isinstance(ring, list) or not all(isinstance(v, list | tuple) for v in ring):
        return None, "The MapPLUTO outline ring is malformed; it is not measured here."
    exterior = tuple(tuple(vertex) for vertex in ring)  # values checked in prepare_outline
    return LotOutline(exterior, dict(result.crs), source, provenance), None


def _street_key(segment: StreetSegment) -> str:
    name = " ".join((segment.street_name or "").split())
    return name or f"Unnamed segment {segment.object_id}"


def _street_status(segment: StreetSegment) -> tuple[bool, str | None]:
    if segment.feat_type != FEAT_TYPE_MAPPED:
        return False, (f"the City Map feature type is {segment.feat_type!r}, not a mapped "
                       "street; needs review")
    odd = [f"{flag}={getattr(segment, flag)!r}" for flag in _SPECIAL_FLAGS
           if getattr(segment, flag) != "N"]
    if odd:
        return False, "the City Map flags it (" + ", ".join(odd) + "); needs review"
    return True, None


def _queried_envelope(request_url: str) -> str | None:
    """The EPSG:2263 intersects-envelope a DCM query page was fetched with, as the connector
    wrote it (``build_segment_query_url``), else None."""
    query = parse_qs(urlsplit(request_url).query)
    shape = (query.get("geometryType"), query.get("inSR"), query.get("spatialRel"))
    if shape != (["esriGeometryEnvelope"], ["2263"], ["esriSpatialRelIntersects"]):
        return None
    geometry = query.get("geometry")
    return geometry[0] if geometry and len(geometry) == 1 else None


def street_data_from_pages(
    pages: Sequence[SegmentGeometryPage], *, envelope: tuple[float, float, float, float]
) -> StreetData:
    """Every segment on the given query pages. ``envelope`` (EPSG:2263) must be the one the
    pages were queried with; each page's request URL is checked against it, so a query by
    street name can never pass for full coverage."""
    incomplete: list[str] = []
    centerlines: list[StreetCenterline] = []
    crs: dict = dict(pages[0].crs) if pages else {}
    if not pages:
        incomplete.append("No street query result was provided.")
    stated = ",".join(f"{float(v):.4f}" for v in envelope)
    for page in pages:
        if not crs_is_measurement_grade(page.crs):
            crs = {}
        if _queried_envelope(page.request_url) != stated:
            incomplete.append("A street query page was not fetched for the stated area.")
        if page.exceeded_transfer_limit:
            incomplete.append("The street query hit its transfer limit; streets may be missing.")
        for entry in page.entries:
            segment = entry.segment
            if not entry.has_usable_geometry or entry.paths is None:
                incomplete.append(f"Street segment {segment.object_id} "
                                  f"({segment.street_name}) has no usable geometry.")
                continue
            ok, note = _street_status(segment)
            centerlines.append(StreetCenterline(
                _street_key(segment), segment.street_name, segment.object_id,
                tuple(tuple(path) for path in entry.paths), segment.streetwidth_raw, ok, note))
    provenance = {
        "source_id": DCM_SOURCE_ID,
        "request_urls": [page.request_url for page in pages],
        "retrieved_at": [page.retrieved_at for page in pages],
        "raw_digests": [page.raw_digest for page in pages],
        "envelope": list(envelope),
    }
    return StreetData(tuple(centerlines), tuple(envelope), crs,
                      "DCP Digital City Map street center lines",
                      tuple(dict.fromkeys(incomplete)), provenance)


def _positive(fact: dict | None, unit: str) -> float | None:
    if fact is None or fact.get("units") != unit:
        return None
    value = fact.get("normalized_value")
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    if not math.isfinite(value) or value <= 0:
        return None  # PLUTO 0 / blank is "not recorded", never a 0 measurement
    return float(value)


def city_records_from_pluto(result: pluto_soda.PlutoFetchResult) -> CityRecordLot:
    """PLUTO ``lotarea`` / ``lotfront`` / ``lotdepth`` (units per the connector's
    FIELD_UNITS, data dictionary p.21-22 and p.29); anything else is not recorded."""
    version = result.dataset_version
    source = f"PLUTO {version} ({pluto_soda.DATASET_ID})" if version else "PLUTO"
    provenance = {
        "source_id": pluto_soda.SOURCE_ID,
        "dataset_version": result.dataset_version,
        "request_url": result.request_url,
        "retrieved_at": result.retrieved_at,
        "response_digest": result.response_digest,
    }
    facts = {fact.get("original_field_name"): fact for fact in result.facts}
    if result.status != "ok":
        return CityRecordLot(None, None, None, source, provenance)
    return CityRecordLot(
        _positive(facts.get("lotarea"), "square feet"),
        _positive(facts.get("lotfront"), "feet"),
        _positive(facts.get("lotdepth"), "feet"),
        source,
        provenance,
    )


def derive_site_geometry_from_sources(
    lot_result: LotGeometryResult,
    street_pages: Sequence[SegmentGeometryPage] | None,
    *,
    envelope: tuple[float, float, float, float] | None,
    pluto_result: pluto_soda.PlutoFetchResult | None = None,
) -> SiteGeometry:
    """Adapt the connector results and derive; an unusable outline gives a refusal."""
    records = city_records_from_pluto(pluto_result) if pluto_result is not None else None
    lot, refusal = lot_outline_from_mappluto(lot_result)
    streets = None
    if street_pages is not None and envelope is not None:
        streets = street_data_from_pages(street_pages, envelope=envelope)
    if lot is None:
        return refused_site_geometry(refusal or "No outline.", records, streets=streets)
    return derive_site_geometry(lot, streets, records)
