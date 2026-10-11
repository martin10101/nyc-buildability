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
    "ContextWindow",
    "Drawing",
    "Label",
    "LayerUnavailable",
    "Line",
    "MapContext",
    "MapNote",
    "NeighbourLot",
    "Point",
    "Polygon",
    "Ring",
    "StreetLine",
    "StreetLayer",
    "SubjectLot",
    "TaxLotLayer",
    "Unavailable",
    "ZoningDistrict",
    "ZoningLayer",
]

Line = tuple[Point, ...]


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
    """Building footprints around the lot plus the dataset attribution note.
    ``edited`` is the source's last-edited date read from provenance when the
    document carries it (for the caption; ruling Y7), else ``None``."""

    footprints: tuple[BuildingFootprint, ...]
    attribution: MapNote
    source: str
    edited: str | None = None


@dataclass(frozen=True)
class ContextWindow:
    """The rectangle (EPSG:2263 US survey feet) the neighbouring lots and the
    building footprints were fetched for - the lot's bounding box plus 400 ft
    (ruling Y2 a). ``xmax > xmin`` and ``ymax > ymin`` (the adapter checks)."""

    xmin: float
    ymin: float
    xmax: float
    ymax: float
    source: str

    @property
    def box(self) -> tuple[float, float, float, float]:
        return self.xmin, self.ymin, self.xmax, self.ymax


@dataclass(frozen=True)
class NeighbourLot:
    """One neighbouring tax lot (NOT the subject - the subject is never an
    entry, ruling Y2 b). ``bbl`` / ``address`` are optional labels read from the
    data; no owner name or personal field is ever carried."""

    bbl: str | None
    bbl_source: str | None
    address: str | None
    address_source: str | None
    outline: Polygon
    source: str


@dataclass(frozen=True)
class TaxLotLayer:
    """The neighbouring tax lots inside the context window plus the dataset
    attribution note (ruling Y2 b)."""

    lots: tuple[NeighbourLot, ...]
    attribution: MapNote
    source: str
    edited: str | None = None


@dataclass(frozen=True)
class StreetLine:
    """One mapped street centre line (ruling Y2 c). ``width_text`` is the source
    text unchanged (string or ``None``); ``mapped_width_ft`` is a number ONLY
    when ``width_text`` is one plain number such as '60' or '100' (D-052), else
    ``None``. ``paths`` are the centre-line polylines (each at least two points),
    EPSG:2263 US survey feet."""

    name: str
    name_source: str
    width_text: str | None
    width_source: str | None
    mapped_width_ft: float | None
    mapped_width_source: str | None
    paths: tuple[Line, ...]
    source: str


@dataclass(frozen=True)
class StreetLayer:
    """The mapped street centre lines inside the streets window (the lot's
    bounding box plus 1,000 ft, ruling Y2 c), plus the dataset attribution
    note. ``window`` is that larger box."""

    window: ContextWindow
    streets: tuple[StreetLine, ...]
    attribution: MapNote
    source: str
    edited: str | None = None


@dataclass(frozen=True)
class MapContext:
    """Everything the location and zoning maps need, validated and fail-closed.

    ``zoning`` / ``buildings`` are the drawable layer, or a
    :class:`LayerUnavailable` carrying the data's own reason when the layer
    could not be retrieved (the corresponding map then returns
    :class:`Unavailable`, never a blank or invented map).

    ``context_window`` / ``tax_lots`` / ``streets`` are the OPTIONAL 1.1.0
    members (ruling Y2) the site-context plan, block close-up and neighbourhood
    map draw from. A 1.0.0 document carries none of them (each stays ``None``),
    so the location and zoning maps are byte-identical and the new drawings are
    honestly :class:`Unavailable`. An optional layer that the data marks
    ``not_available`` is a :class:`LayerUnavailable`, never a partial picture.
    """

    crs: str
    measurement_label: str
    measurement_source: str
    subject_lot: SubjectLot
    zoning: ZoningLayer | LayerUnavailable
    buildings: BuildingLayer | LayerUnavailable
    context_window: ContextWindow | None = None
    tax_lots: TaxLotLayer | LayerUnavailable | None = None
    streets: StreetLayer | LayerUnavailable | None = None
