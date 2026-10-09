"""Typed, validated view of the city-open-data context the maps draw from.

Built only by :func:`app.drawings.maps.adapter.load_map_context`. Every printed
value keeps ``source`` - the JSON pointer (RFC 6901) of where it came from in
the map-context document - so each label and note traces back to the data
(the same check-C-4 discipline as the drawing kit). All coordinates are in
EPSG:2263 US survey feet (the authoritative measurement CRS); the maps never
reproject and never accept a display CRS.

The geometry primitives (:class:`Polygon`, :class:`Point`, :class:`Ring`), the
finished :class:`Drawing`, each printed :class:`Label`, the :class:`Unavailable`
outcome, and the :class:`LayerUnavailable` layer outcome are reused from the
drawing kit so screen, PDF and DXF share one vocabulary.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.drawings.kit.model import (
    Drawing,
    Label,
    LayerUnavailable,
    Point,
    Polygon,
    Ring,
    Unavailable,
)

__all__ = [
    "BuildingFootprint",
    "BuildingLayer",
    "Drawing",
    "Label",
    "LayerUnavailable",
    "MapContext",
    "MapNote",
    "Point",
    "Polygon",
    "Ring",
    "SubjectLot",
    "Unavailable",
    "ZoningDistrict",
    "ZoningLayer",
]


@dataclass(frozen=True)
class MapNote:
    """One note read from the map-context data, with where its value came from.

    A note is never literal typed text: every note names a ``source`` pointer so
    the provenance (dataset attribution, accuracy statement, official use
    limitation, measurement rank) is always traceable to the data.
    """

    text: str
    source: str


@dataclass(frozen=True)
class SubjectLot:
    """The lot the study is about - the focus of both maps, emphasised on top of
    the city-data context. ``bbl`` is the borough-block-lot label read from the
    data (optional: the data may carry no BBL)."""

    bbl: str | None
    bbl_source: str | None
    outline: Polygon
    source: str


@dataclass(frozen=True)
class ZoningDistrict:
    """One zoning-district polygon from the DCP NYC GIS Zoning Features (nyzd),
    labelled by its ``symbol`` - the verbatim ``ZONEDIST`` designation."""

    symbol: str
    symbol_source: str
    outline: Polygon
    source: str


@dataclass(frozen=True)
class BuildingFootprint:
    """One building-footprint polygon from the OTI Building Footprints dataset,
    drawn as neighbourhood context (not labelled individually)."""

    outline: Polygon
    source: str


@dataclass(frozen=True)
class ZoningLayer:
    """Zoning districts around the lot plus the three notes every zoning map must
    carry: the dataset attribution, the horizontal-accuracy statement, and the
    official use limitation (districts are NOT for lot-level determination)."""

    districts: tuple[ZoningDistrict, ...]
    attribution: MapNote
    accuracy: MapNote
    use_limitation: MapNote
    source: str


@dataclass(frozen=True)
class BuildingLayer:
    """Building footprints around the lot plus the dataset attribution note."""

    footprints: tuple[BuildingFootprint, ...]
    attribution: MapNote
    source: str


@dataclass(frozen=True)
class MapContext:
    """Everything the location and zoning maps need, validated and fail-closed.

    ``zoning`` / ``buildings`` are the drawable layer, or a
    :class:`LayerUnavailable` carrying the data's own reason when the layer
    could not be retrieved (the corresponding map then returns
    :class:`Unavailable`, never a blank or invented map).
    """

    crs: str
    measurement_label: str
    measurement_source: str
    subject_lot: SubjectLot
    zoning: ZoningLayer | LayerUnavailable
    buildings: BuildingLayer | LayerUnavailable
