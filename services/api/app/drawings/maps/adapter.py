"""Map-context document -> :class:`MapContext` (validated, fail-closed).

The map context is reshaped city open data (lot outline from MapPLUTO / DOF
Digital Tax Map, zoning districts from DCP NYC GIS Zoning Features ``nyzd``,
building footprints from the OTI Building Footprints dataset). Live services
are never called here; the renderers draw only what this adapter has validated.

What a schema alone cannot state is checked here: a single supported CRS
(EPSG:2263 US survey feet - citywide absolute coordinates, never a local or
display CRS); closed, finite, in-range, simple, non-degenerate rings; holes
inside their exterior; bounded feature counts; and every printed string
well-formed for XML. Any failure raises :class:`MapInputError`; nothing partial
is drawn. A layer the data marks ``not_available`` is not an error - it becomes
:class:`LayerUnavailable` carrying the data's own reason.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

from app.drawings.kit import geometry as geo
from app.drawings.kit.svg import xml_illegal

from .errors import MapInputError
from .model import (
    BuildingFootprint,
    BuildingLayer,
    LayerUnavailable,
    MapContext,
    MapNote,
    Point,
    Polygon,
    Ring,
    SubjectLot,
    ZoningDistrict,
    ZoningLayer,
)

__all__ = [
    "MAX_ABS_COORD_FT",
    "MAX_MAP_FEATURES",
    "MAX_RING_POINTS",
    "SUPPORTED_CRS",
    "load_map_context",
]

# EPSG:2263 is the authoritative measurement CRS; the maps overlay citywide
# absolute coordinates (lot, districts, footprints), so a local-origin or
# display CRS is refused rather than silently misplaced.
SUPPORTED_CRS = "EPSG:2263"
MAX_RING_POINTS = 2048  # bounds the O(n^2) simplicity check
MAX_MAP_FEATURES = 2000  # bounds districts / footprints drawn per map
MAX_ABS_COORD_FT = 1.0e8  # EPSG:2263 NYC values are ~1e6 ft; far beyond is corrupt


def load_map_context(doc: Mapping) -> MapContext:
    """Validate ``doc`` and return the drawable map context (fail-closed)."""
    context = _require_mapping(doc, "map_context", "/map_context")
    crs = context.get("crs")
    if crs != SUPPORTED_CRS:
        raise MapInputError(
            "unsupported_crs",
            f"maps require {SUPPORTED_CRS} (US survey feet); got {crs!r}",
            location="/map_context/crs",
        )
    measurement = _require_mapping(context, "measurement", "/map_context/measurement")
    return MapContext(
        crs=crs,
        measurement_label=_text(measurement["label"], "/map_context/measurement/label"),
        measurement_source="/map_context/measurement/label",
        subject_lot=_subject_lot(context["subject_lot"]),
        zoning=_zoning(context["zoning_districts"]),
        buildings=_buildings(context["building_footprints"]),
    )


def _subject_lot(raw: Mapping) -> SubjectLot:
    base = "/map_context/subject_lot"
    bbl = raw.get("bbl")
    return SubjectLot(
        bbl=_text(bbl, f"{base}/bbl") if bbl is not None else None,
        bbl_source=f"{base}/bbl" if bbl is not None else None,
        outline=_polygon(raw["outline"], f"{base}/outline"),
        source=base,
    )


def _zoning(raw: Mapping) -> ZoningLayer | LayerUnavailable:
    base = "/map_context/zoning_districts"
    if raw["status"] == "not_available":
        return _unavailable("zoning_districts", raw, base)
    entries = _entries(raw["entries"], base)
    districts = []
    for i, entry in enumerate(entries):
        location = f"{base}/entries/{i}"
        districts.append(
            ZoningDistrict(
                symbol=_text(entry["zonedist"], f"{location}/zonedist"),
                symbol_source=f"{location}/zonedist",
                outline=_polygon(entry["outline"], f"{location}/outline"),
                source=location,
            )
        )
    return ZoningLayer(
        districts=tuple(districts),
        attribution=_note(raw["attribution"], f"{base}/attribution"),
        accuracy=_note(raw["accuracy"], f"{base}/accuracy"),
        use_limitation=_note(raw["use_limitation"], f"{base}/use_limitation"),
        source=base,
    )


def _buildings(raw: Mapping) -> BuildingLayer | LayerUnavailable:
    base = "/map_context/building_footprints"
    if raw["status"] == "not_available":
        return _unavailable("building_footprints", raw, base)
    entries = _entries(raw["entries"], base)
    footprints = tuple(
        BuildingFootprint(_polygon(entry["outline"], f"{base}/entries/{i}/outline"),
                          f"{base}/entries/{i}")
        for i, entry in enumerate(entries)
    )
    return BuildingLayer(
        footprints=footprints,
        attribution=_note(raw["attribution"], f"{base}/attribution"),
        source=base,
    )


def _entries(raw: Sequence, base: str) -> Sequence:
    if len(raw) > MAX_MAP_FEATURES:
        raise MapInputError("too_many_features", f"more than {MAX_MAP_FEATURES}",
                            location=f"{base}/entries")
    return raw


def _unavailable(layer: str, raw: Mapping, base: str) -> LayerUnavailable:
    return LayerUnavailable(layer, _text(raw["reason"], f"{base}/reason"), raw["reason_kind"],
                            base)


def _require_mapping(raw: Mapping, key: str, location: str) -> Mapping:
    value = raw.get(key) if isinstance(raw, Mapping) else None
    if not isinstance(value, Mapping):
        raise MapInputError("missing_block", f"expected an object at {key!r}", location=location)
    return value


def _note(value: str, location: str) -> MapNote:
    return MapNote(_text(value, location), location)


def _text(value: object, location: str) -> str:
    """A string a map prints: must be a string with no character XML 1.0 forbids
    (which would make the SVG malformed)."""
    if not isinstance(value, str):
        raise MapInputError("invalid_text", "expected a string", location=location)
    if xml_illegal(value):
        raise MapInputError("invalid_text", "text carries a character XML forbids",
                            location=location)
    return value


def _finite(value: object, location: str) -> float:
    number = float(value)  # type: ignore[arg-type]
    if not math.isfinite(number):
        raise MapInputError("non_finite_number", "value is not finite", location=location)
    return number


def _point(raw: Sequence, location: str) -> Point:
    x, y = _finite(raw[0], location), _finite(raw[1], location)
    if abs(x) > MAX_ABS_COORD_FT or abs(y) > MAX_ABS_COORD_FT:
        raise MapInputError("coordinate_out_of_range", "coordinate beyond the supported extent",
                            location=location)
    return (x, y)


def _ring(raw: Sequence, location: str) -> Ring:
    if len(raw) > MAX_RING_POINTS:
        raise MapInputError("ring_too_large", f"more than {MAX_RING_POINTS} points",
                            location=location)
    ring = tuple(_point(p, f"{location}/{i}") for i, p in enumerate(raw))
    if len(ring) < 2 or ring[0] != ring[-1]:
        raise MapInputError("ring_not_closed", "first and last point differ", location=location)
    if len(set(ring[:-1])) < 3:
        raise MapInputError("ring_degenerate", "fewer than 3 distinct points", location=location)
    if not geo.is_simple(ring):
        raise MapInputError("ring_not_simple", "outline crosses or touches itself",
                            location=location)
    if abs(geo.signed_area(ring)) <= geo.BOUNDARY_TOL_FT:
        raise MapInputError("ring_zero_area", "outline encloses no area", location=location)
    return ring


def _polygon(raw: Sequence, location: str) -> Polygon:
    rings = tuple(_ring(r, f"{location}/{i}") for i, r in enumerate(raw))
    if not rings:
        raise MapInputError("polygon_empty", "no rings", location=location)
    for i, hole in enumerate(rings[1:], start=1):
        if not geo.ring_within(hole, rings[0]):
            raise MapInputError("hole_outside_exterior", "hole is not inside its exterior ring",
                                location=f"{location}/{i}")
    return Polygon(rings=rings, source=location)
