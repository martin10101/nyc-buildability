"""Location and zoning maps (task E-07, plan section 5c item 2): server-made
vector SVG maps from NYC city open data, built on the E-01 drawing kit.

Public entry points (behind the same Lane E flag ``LANE_E_ENABLED``, default
off):

* :func:`render_location_map` - the subject lot among the surrounding building
  footprints (OTI Building Footprints), the lot labelled by its BBL;
* :func:`render_zoning_map` - the subject lot against the zoning-district
  boundaries (DCP NYC GIS Zoning Features ``nyzd``), each district labelled by
  its verbatim ``ZONEDIST`` symbol, with the official use-limitation,
  horizontal-accuracy and attribution notes.

Both validate the map context first (:mod:`.adapter`, fail closed) and are pure
and deterministic: the same context gives byte-identical SVG. Each returns a
:class:`Drawing` (SVG text, every printed label with its source, kinds drawn)
or :class:`Unavailable` carrying the data's own reason when a layer could not be
retrieved. Coordinates are EPSG:2263 US survey feet; nothing is reprojected and
no raster base-map imagery is drawn. The shared look lives in the drawing kit's
style table (``app.drawings.kit.styles``). Live services are never called here;
tests use recorded fixtures.
"""

from __future__ import annotations

from collections.abc import Mapping

from app.drawings.kit.flag import DrawingKitDisabled, drawing_kit_enabled

from .adapter import load_map_context
from .block_map import draw_block_map
from .errors import MapInputError
from .location_map import draw_location_map
from .model import (
    BuildingFootprint,
    BuildingLayer,
    ContextWindow,
    Drawing,
    Label,
    LayerUnavailable,
    MapContext,
    MapNote,
    NeighbourLot,
    StreetLayer,
    StreetLine,
    SubjectLot,
    TaxLotLayer,
    Unavailable,
    ZoningDistrict,
    ZoningLayer,
)
from .neighbourhood_map import draw_neighbourhood_map
from .site_context_plan import draw_site_context_plan
from .zoning_map import draw_zoning_map

__all__ = [
    "BuildingFootprint",
    "BuildingLayer",
    "ContextWindow",
    "Drawing",
    "DrawingKitDisabled",
    "Label",
    "LayerUnavailable",
    "MapContext",
    "MapInputError",
    "MapNote",
    "NeighbourLot",
    "StreetLayer",
    "StreetLine",
    "SubjectLot",
    "TaxLotLayer",
    "Unavailable",
    "ZoningDistrict",
    "ZoningLayer",
    "load_map_context",
    "render_block_map",
    "render_location_map",
    "render_neighbourhood_map",
    "render_site_context_plan",
    "render_zoning_map",
]


def _context(doc: Mapping, env: Mapping[str, str] | None) -> MapContext:
    if not drawing_kit_enabled(env):
        raise DrawingKitDisabled("the drawing kit is off (LANE_E_ENABLED is not set)")
    return load_map_context(doc)


def render_location_map(
    doc: Mapping, *, frame: str = "sheet", env: Mapping[str, str] | None = None
) -> Drawing | Unavailable:
    """The location map. ``frame='sheet'`` (default) is byte-identical; ``frame='report'`` is the
    A4 report composition (no notes column, at most 182 mm x 150 mm, labels at least 7 pt, the
    attribution kept reachable as a label) - ruling X9 a/c."""
    return draw_location_map(_context(doc, env), frame=frame)


def render_zoning_map(
    doc: Mapping, *, frame: str = "sheet", env: Mapping[str, str] | None = None
) -> Drawing | Unavailable:
    """The zoning map. ``frame='sheet'`` (default) is byte-identical; ``frame='report'`` is the A4
    report composition (no notes column, at most 182 mm x 150 mm, labels at least 7 pt, the
    attribution/accuracy/use-limitation notes kept reachable as labels) - ruling X9 a/c."""
    return draw_zoning_map(_context(doc, env), frame=frame)


def render_site_context_plan(
    doc: Mapping, *, frame: str = "sheet", env: Mapping[str, str] | None = None
) -> Drawing | Unavailable:
    """The site plan among its surroundings (M5-T155, ruling Y3): the subject lot coloured with its
    edge lengths, the neighbouring tax lots and existing buildings in greys, and the streets as the
    pale space between the tax lots named along the street, rotated to the lot's frontage.
    ``frame='report'`` gives the wave-21 report frame (no notes column, at most 182 mm by 150 mm,
    every label at least 7 pt, the caption returned to the caller). Unavailable if the tax lots, the
    streets or the building footprints are not available."""
    return draw_site_context_plan(_context(doc, env), frame=frame)


def render_block_map(
    doc: Mapping, *, frame: str = "sheet", env: Mapping[str, str] | None = None
) -> Drawing | Unavailable:
    """The block close-up (M5-T155, ruling Y3): the whole context window - the subject lot marked
    among its neighbouring tax lots and the surrounding street network, rotated to the lot's
    frontage. ``frame='report'`` gives the wave-21 report frame. Unavailable if the context window,
    the tax lots or the streets are not available."""
    return draw_block_map(_context(doc, env), frame=frame)


def render_neighbourhood_map(
    doc: Mapping, *, frame: str = "sheet", env: Mapping[str, str] | None = None
) -> Drawing | Unavailable:
    """The neighbourhood map (M5-T155, ruling Y3): the street network of the streets window, the
    subject lot marked, north-up. ``frame='report'`` gives the wave-21 report frame. Unavailable if
    the streets are not available."""
    return draw_neighbourhood_map(_context(doc, env), frame=frame)
