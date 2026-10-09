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
from .errors import MapInputError
from .location_map import draw_location_map
from .model import (
    BuildingFootprint,
    BuildingLayer,
    Drawing,
    Label,
    LayerUnavailable,
    MapContext,
    MapNote,
    SubjectLot,
    Unavailable,
    ZoningDistrict,
    ZoningLayer,
)
from .zoning_map import draw_zoning_map

__all__ = [
    "BuildingFootprint",
    "BuildingLayer",
    "Drawing",
    "DrawingKitDisabled",
    "Label",
    "LayerUnavailable",
    "MapContext",
    "MapInputError",
    "MapNote",
    "SubjectLot",
    "Unavailable",
    "ZoningDistrict",
    "ZoningLayer",
    "load_map_context",
    "render_location_map",
    "render_zoning_map",
]


def _context(doc: Mapping, env: Mapping[str, str] | None) -> MapContext:
    if not drawing_kit_enabled(env):
        raise DrawingKitDisabled("the drawing kit is off (LANE_E_ENABLED is not set)")
    return load_map_context(doc)


def render_location_map(
    doc: Mapping, *, env: Mapping[str, str] | None = None
) -> Drawing | Unavailable:
    return draw_location_map(_context(doc, env))


def render_zoning_map(
    doc: Mapping, *, env: Mapping[str, str] | None = None
) -> Drawing | Unavailable:
    return draw_zoning_map(_context(doc, env))
