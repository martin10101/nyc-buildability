"""Single-lot site geometry (queue item B-03; plan M1-13 data side and §4 "Measurements").

From a tax-lot outline in EPSG:2263 feet and the City Map street center lines around it:
lot area (checked against the recorded area, never replacing it), frontage per street along
the outline's outside edges, geometric lot type (corner / interior / through / unknown) and
lot depth where definable. Every value carries its §4 source label; unknown stays unknown.

Modules: ``inputs`` (plain inputs) · ``outline`` (CRS gate, validity, edges) · ``rays``
(planar primitives) · ``adjacency`` (the street-line test per edge) · ``street_data``
(completeness checks) · ``frontage`` · ``depth`` · ``lot_type`` · ``area`` · ``derive``
(pure entry point) · ``adapters`` (from connector results) · ``labels`` · ``parameters`` ·
``results``. Nothing calls this package yet; a later Lane C task wires it.
"""

from __future__ import annotations

from .adapters import (
    city_records_from_pluto,
    derive_site_geometry_from_sources,
    lot_outline_from_mappluto,
    street_data_from_pages,
)
from .derive import derive_site_geometry, refused_site_geometry
from .inputs import CityRecordLot, LotOutline, StreetCenterline, StreetData
from .labels import (
    LABEL_CITY_RECORDS,
    LABEL_SURVEY,
    LABEL_TAX_MAP,
    LABEL_UNKNOWN,
    SourcedValue,
)
from .parameters import METHOD_VERSION, parameters_snapshot
from .results import (
    AreaCheck,
    CityRecordValues,
    DepthProfile,
    EdgeFinding,
    LotType,
    SiteGeometry,
    StreetFrontage,
    StreetRelation,
)

__all__ = [
    "LABEL_CITY_RECORDS",
    "LABEL_SURVEY",
    "LABEL_TAX_MAP",
    "LABEL_UNKNOWN",
    "METHOD_VERSION",
    "AreaCheck",
    "CityRecordLot",
    "CityRecordValues",
    "DepthProfile",
    "EdgeFinding",
    "LotOutline",
    "LotType",
    "SiteGeometry",
    "SourcedValue",
    "StreetCenterline",
    "StreetData",
    "StreetFrontage",
    "StreetRelation",
    "city_records_from_pluto",
    "derive_site_geometry",
    "derive_site_geometry_from_sources",
    "lot_outline_from_mappluto",
    "parameters_snapshot",
    "refused_site_geometry",
    "street_data_from_pages",
]
