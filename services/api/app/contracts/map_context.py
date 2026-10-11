"""Build the ``map_context`` v1 document from the accepted connectors' typed
results (maps connection step 3, owner directive D-090-R124).

This is a PURE builder: no network, no new connector, no renderer change. It
turns three already-produced typed results -

* the MapPLUTO per-lot geometry
  (:class:`~app.connectors.mappluto_geometry_arcgis.LotGeometryResult`),
* the DCP NYC GIS Zoning Features ``nyzd`` attribute-query page
  (:class:`~app.connectors.zoning_features_arcgis.LayerQueryResult`),
* the OTI Building Footprints context result
  (:class:`~app.connectors.building_footprints_arcgis.ContextBuildingsResult`),

into the ONE document the E-07 location and zoning map renderers consume via
:func:`app.drawings.maps.adapter.load_map_context`. The adapter is the
acceptance oracle: after assembling the document the builder validates it with
:func:`app.contracts.study_contracts.validate_map_context_document` AND loads it
through ``load_map_context``; anything the adapter refuses in a surrounding
layer demotes THAT layer to ``not_available`` carrying the adapter's own
message, and a refusal in the subject lot raises
:class:`MapContextUnavailable` (there is no map without a lot).

Provenance comes verbatim from the typed results - never invented. The three
mandatory zoning notes (attribution, horizontal-accuracy, the official
use-limitation) and the footprint attribution are supplied by the caller in
:class:`MapNotes` (sourced from ``docs/samples/maps/README.md``); the builder
composes no legal text of its own. Every coordinate stays EPSG:2263 US survey
feet - a layer whose CRS stamp does not report ``latest_wkid`` 2263 becomes
``not_available`` rather than being reprojected.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.connectors.building_footprints_geometry import (
    GEOMETRY_VALID,
    parse_footprint_geometry,
)
from app.connectors.zoning_features_arcgis import SOURCE_ID as ZONING_SOURCE_ID
from app.contracts.study_contracts import validate_map_context_document
from app.drawings.kit.geometry import bbox
from app.drawings.maps.adapter import SUPPORTED_CRS, load_map_context
from app.drawings.maps.errors import MapInputError
from app.profile.measurement import RANK_APPROXIMATE_TAX_MAP, measurement
from app.spatial.site_geometry.adapters import lot_outline_from_mappluto

if TYPE_CHECKING:  # pragma: no cover - typing only, no runtime import cost
    from app.connectors.building_footprints_arcgis import ContextBuildingsResult
    from app.connectors.dcm_street_centerline_geometry import SegmentGeometryQueryResult
    from app.connectors.mappluto_geometry_arcgis import LotGeometryResult
    from app.connectors.mappluto_window_arcgis import MapPlutoWindowResult
    from app.connectors.zoning_features_arcgis import LayerQueryResult

__all__ = [
    "MapContextUnavailable",
    "MapNotes",
    "ReportMapNotes",
    "build_map_context",
    "build_report_map_context",
    "parse_mapped_width_ft",
]

CONTRACT_VERSION = "1.0.0"
# Contract 1.1.0 (task M5-T154, ruling Y2): the report's site-context document.
# Adds the OPTIONAL context_window / tax_lots / streets members on top of the
# 1.0.0 shape, so every 1.0.0 document stays valid unchanged.
CONTRACT_VERSION_1_1_0 = "1.1.0"
DOCUMENT_KIND = "map_context"
UNITS = "feet"

# A mapped-street width text is turned into a number ONLY when it is one plain
# non-negative number such as "60" or "100"; "60-75", "<=75", ">90", "Unknown"
# or an empty string give null (D-052; ruling Y2). This is NOT a wide/narrow
# classification - it is the literal mapped width when the source states one.
_PLAIN_NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")


def parse_mapped_width_ft(width_text: object) -> int | float | None:
    """The mapped street width in feet, or ``None``. A number ONLY when
    ``width_text`` is exactly one plain non-negative number (optionally
    surrounded by whitespace); any range, bound, word or empty text gives
    ``None`` (ruling Y2 / D-052). An integral value returns an ``int``."""
    if not isinstance(width_text, str):
        return None
    text = width_text.strip()
    if not _PLAIN_NUMBER_RE.fullmatch(text):
        return None
    value = float(text)
    return int(value) if value.is_integer() else value
# EPSG:2263 latest_wkid; a layer whose stamp does not report it is not drawn.
_LATEST_WKID_2263 = 2263
# The only machine reason-kind the E-07 renderers and the contract admit.
_REASON_KIND = "source_unavailable"


class MapContextUnavailable(Exception):
    """No map can be built: the subject lot outline is unavailable (a refused
    MapPLUTO outline, or a lot not in EPSG:2263). Surrounding layers degrade to
    ``not_available``; only the subject lot raises, because the study is about
    that lot and both maps draw it."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class MapNotes:
    """The printed notes the caller supplies from ``docs/samples/maps/README.md``.

    The builder places these verbatim; it composes no legal text of its own.
    ``zoning_coverage`` is the attribute-query coverage note (the ``nyzd`` page
    was fetched by a ``ZONEDIST`` attribute query, so neighbouring districts of
    OTHER codes were not retrieved); the builder appends it to the zoning
    attribution so it rides on every zoning map (the contract has no separate
    field for it)."""

    zoning_attribution: str
    zoning_accuracy: str
    zoning_use_limitation: str
    zoning_coverage: str
    buildings_attribution: str


@dataclass(frozen=True)
class ReportMapNotes:
    """The printed dataset attributions for the report's site-context maps.

    The builder places each verbatim as the layer's ``attribution``; the source
    EDIT DATE is NOT appended here - it rides on each layer's provenance
    (``source_data_last_edited``), so the caption composes 'source, date' from
    the attribution plus provenance (ruling Y7), never an invented date. The
    builder composes no legal text of its own."""

    tax_lots_attribution: str
    buildings_attribution: str
    streets_attribution: str


# Fixed, non-invented reason for the zoning layer on a report site-context map:
# the report context does not fetch zoning districts (the zoning map stays its
# own feature). An honest not_available layer, never a blank or invented one.
_ZONING_NOT_FETCHED_REASON = (
    "Zoning districts are not fetched for the report site-context map."
)


def build_map_context(
    lot: LotGeometryResult,
    nyzd: LayerQueryResult | None,
    footprints: ContextBuildingsResult | None,
    *,
    window_ft: float,
    notes: MapNotes,
) -> dict:
    """Assemble, validate, and adapter-load the map_context document.

    Raises:
        MapContextUnavailable: the subject lot outline is refused or not in
            EPSG:2263 (no map without a lot).
    """
    subject_lot = _subject_lot(lot)
    lot_bbox = bbox(subject_lot["outline"][0])
    document = {
        "contract_version": CONTRACT_VERSION,
        "document_kind": DOCUMENT_KIND,
        "map_context": {
            "crs": SUPPORTED_CRS,
            "units": UNITS,
            "measurement": measurement(RANK_APPROXIMATE_TAX_MAP),
            "subject_lot": subject_lot,
            "zoning_districts": _zoning_layer(nyzd, lot_bbox, window_ft, notes),
            "building_footprints": _buildings_layer(footprints, notes),
        },
    }
    document = _resolve_through_adapter(document)
    validate_map_context_document(document)
    return document


# ---------------------------------------------------------------------------
# Report site-context document (contract 1.1.0, ruling Y2)
# ---------------------------------------------------------------------------


def build_report_map_context(
    lot: LotGeometryResult,
    *,
    context_window: tuple[float, float, float, float],
    tax_lots: MapPlutoWindowResult | None,
    tax_lots_unavailable_reason: str | None = None,
    footprints: ContextBuildingsResult | None,
    streets: SegmentGeometryQueryResult | None,
    streets_unavailable_reason: str | None = None,
    streets_window: tuple[float, float, float, float],
    notes: ReportMapNotes,
) -> dict:
    """Assemble, adapter-load and validate the report's 1.1.0 site-context
    document: the subject lot drawn among its surroundings. ``zoning_districts``
    is always a ``not_available`` layer (the report context does not fetch
    zoning). Each surrounding layer is either drawable or a ``not_available``
    layer carrying its reason; a refusing connector NEVER raises here (the caller
    passes ``None`` plus a reason). Every outline and path is an input geometry
    unchanged.

    Raises:
        MapContextUnavailable: the subject lot outline is refused or not in
            EPSG:2263 (no map without a lot).
    """
    subject_lot = _subject_lot(lot)
    document = {
        "contract_version": CONTRACT_VERSION_1_1_0,
        "document_kind": DOCUMENT_KIND,
        "map_context": {
            "crs": SUPPORTED_CRS,
            "units": UNITS,
            "measurement": measurement(RANK_APPROXIMATE_TAX_MAP),
            "subject_lot": subject_lot,
            "zoning_districts": _unavailable(_ZONING_NOT_FETCHED_REASON),
            "building_footprints": _buildings_layer(footprints, notes),
            "context_window": _window_box(context_window),
            "tax_lots": _tax_lots_layer(tax_lots, tax_lots_unavailable_reason, notes),
            "streets": _streets_layer(
                streets, streets_unavailable_reason, streets_window, notes
            ),
        },
    }
    document = _resolve_through_adapter(document)
    validate_map_context_document(document)
    return document


def _window_box(envelope: tuple[float, float, float, float]) -> dict:
    xmin, ymin, xmax, ymax = (float(v) for v in envelope)
    return {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}


def _verbatim_polygon(rings: list) -> list[list[list[float]]]:
    """The source esri rings as a contract polygon, verbatim (floats preserve the
    parsed value): no quantization, repair or re-orientation (ruling Y2)."""
    return [[[float(x), float(y)] for x, y in ring] for ring in rings]


def _tax_lots_layer(
    result: MapPlutoWindowResult | None, reason: str | None, notes: ReportMapNotes
) -> dict:
    if result is None:
        return _unavailable(reason or "Neighbouring tax lots could not be retrieved for this lot.")
    provenance = _tax_lots_provenance(result)
    if provenance is None:
        return _unavailable(
            "The neighbouring-tax-lot source carries no edit-version provenance; it is not drawn."
        )
    entries: list[dict] = []
    for window_lot in result.lots:
        entry: dict = {"bbl": window_lot.bbl, "outline": _verbatim_polygon(window_lot.outline)}
        if window_lot.address:
            entry["address"] = window_lot.address
        entries.append(entry)
    return {
        "status": "available",
        "entries": entries,
        "attribution": notes.tax_lots_attribution,
        "provenance": provenance,
    }


def _streets_layer(
    result: SegmentGeometryQueryResult | None,
    reason: str | None,
    window: tuple[float, float, float, float],
    notes: ReportMapNotes,
) -> dict:
    if result is None:
        return _unavailable(reason or "Street centre lines could not be retrieved for this lot.")
    provenance = _streets_provenance(result)
    if provenance is None:
        return _unavailable(
            "The street-centre-line source carries no edit-version provenance; it is not drawn."
        )
    entries: list[dict] = []
    for polyline in result.entries:
        name = polyline.segment.street_name
        if not polyline.has_usable_geometry or polyline.paths is None:
            continue
        if not (isinstance(name, str) and name.strip()):
            continue
        width_text = polyline.segment.streetwidth_raw
        entries.append({
            "name": name,
            "width_text": width_text,
            "mapped_width_ft": parse_mapped_width_ft(width_text),
            "paths": [[[float(x), float(y)] for x, y in path] for path in polyline.paths],
        })
    return {
        "status": "available",
        "window": _window_box(window),
        "entries": entries,
        "attribution": notes.streets_attribution,
        "provenance": provenance,
    }


def _tax_lots_provenance(result: MapPlutoWindowResult) -> dict | None:
    urls = result.request_urls or []
    digests = result.raw_digests or []
    return _layer_provenance(
        source_id=result.source_id,
        dataset_id=result.dataset_id,
        request_url=urls[0] if urls else None,
        retrieved_at=result.retrieved_at,
        raw_digest=digests[0] if digests else None,
        source_data_last_edited=result.source_data_last_edited,
        source_data_last_edited_ms=result.source_data_last_edited_ms,
    )


def _streets_provenance(result: SegmentGeometryQueryResult) -> dict | None:
    urls = result.page_urls or []
    digests = result.raw_digests or []
    return _layer_provenance(
        source_id=result.source_id,
        dataset_id=result.layer,
        request_url=urls[0] if urls else None,
        retrieved_at=result.retrieved_at,
        raw_digest=digests[0] if digests else None,
        source_data_last_edited=result.source_data_last_edited,
        source_data_last_edited_ms=result.source_data_last_edited_ms,
    )


# ---------------------------------------------------------------------------
# Subject lot
# ---------------------------------------------------------------------------


def _subject_lot(lot: LotGeometryResult) -> dict:
    outline, reason = lot_outline_from_mappluto(lot)
    if outline is None:
        raise MapContextUnavailable(reason or "The subject lot has no usable outline.")
    if not _crs_ok(outline.crs):
        raise MapContextUnavailable(
            "The subject lot geometry is not in EPSG:2263 (US survey feet); it is not reprojected."
        )
    ring = [[float(x), float(y)] for x, y in outline.exterior]
    subject: dict = {"outline": [ring]}
    bbl = getattr(lot, "requested_bbl", None)
    if isinstance(bbl, str) and bbl:
        subject["bbl"] = bbl
    return subject


# ---------------------------------------------------------------------------
# Zoning-district layer
# ---------------------------------------------------------------------------


def _zoning_layer(
    nyzd: LayerQueryResult | None,
    lot_bbox: tuple[float, float, float, float],
    window_ft: float,
    notes: MapNotes,
) -> dict:
    if nyzd is None:
        return _unavailable("No zoning-district features were provided for this lot.")
    provenance = _zoning_provenance(nyzd)
    if provenance is None:
        return _unavailable(
            "The zoning-district source carries no edit-version provenance; it is not drawn.",
            provenance=None,
        )
    if not _crs_ok(getattr(nyzd, "crs", None)):
        return _unavailable(
            "The zoning-district features are not in EPSG:2263; they are not reprojected.",
            provenance=provenance,
        )
    window = (lot_bbox[0] - window_ft, lot_bbox[1] - window_ft,
              lot_bbox[2] + window_ft, lot_bbox[3] + window_ft)
    entries: list[dict] = []
    for feature in nyzd.features:
        geometry = feature.get("geometry")
        if not isinstance(geometry, dict) or not geometry.get("rings"):
            continue
        points = [point for ring in geometry["rings"] for point in ring]
        if not _bbox_overlaps(bbox(points), window):
            continue
        status, _findings, parts, _flags = parse_footprint_geometry(geometry)
        if status != GEOMETRY_VALID:
            continue
        zonedist = feature.get("attributes", {}).get("ZONEDIST")
        for part in parts:
            entries.append({
                "zonedist": zonedist,
                "outline": _polygon(part),
            })
    return {
        "status": "available",
        "entries": entries,
        "attribution": f"{notes.zoning_attribution} {notes.zoning_coverage}",
        "accuracy": notes.zoning_accuracy,
        "use_limitation": notes.zoning_use_limitation,
        "provenance": provenance,
    }


# ---------------------------------------------------------------------------
# Building-footprint layer
# ---------------------------------------------------------------------------


def _buildings_layer(footprints: ContextBuildingsResult | None, notes: MapNotes) -> dict:
    if footprints is None:
        return _unavailable("No building-footprint features were provided for this lot.")
    provenance = _footprints_provenance(footprints)
    if getattr(footprints, "status", None) != "ok":
        reason = "The building-footprint source returned no features for this lot."
        refusal = getattr(footprints, "refusal", None)
        if refusal is not None and getattr(refusal, "message", None):
            reason = refusal.message
        return _unavailable(reason, provenance=provenance)
    if provenance is None:
        return _unavailable(
            "The building-footprint source carries no edit-version provenance; it is not drawn.",
            provenance=None,
        )
    if not _crs_ok(getattr(footprints, "crs", None)):
        return _unavailable(
            "The building footprints are not in EPSG:2263; they are not reprojected.",
            provenance=provenance,
        )
    entries: list[dict] = []
    for building in footprints.buildings:
        for part in building.parts:
            entry: dict = {"outline": _polygon(part)}
            if building.bin is not None:
                entry["bin"] = str(building.bin)
            if building.doitt_id is not None:
                entry["doitt_id"] = str(building.doitt_id)
            entries.append(entry)
    return {
        "status": "available",
        "entries": entries,
        "attribution": notes.buildings_attribution,
        "provenance": provenance,
    }


# ---------------------------------------------------------------------------
# Provenance (verbatim from the typed results; never invented)
# ---------------------------------------------------------------------------


def _zoning_provenance(nyzd: LayerQueryResult) -> dict | None:
    """Per-layer provenance for the ``nyzd`` query result. ``source_id`` is the
    zoning connector's declared source id; ``dataset_id`` is the queried layer;
    ``dataset_version`` is the dataset's own last-edit epoch (ArcGIS
    ``editingInfo.lastEditDate`` ms - the only version these feature services
    publish), distinct from the date-only ``source_data_last_edited``."""
    return _layer_provenance(
        source_id=ZONING_SOURCE_ID,
        dataset_id=getattr(nyzd, "layer", None),
        request_url=getattr(nyzd, "request_url", None),
        retrieved_at=getattr(nyzd, "retrieved_at", None),
        raw_digest=getattr(nyzd, "raw_digest", None),
        source_data_last_edited=getattr(nyzd, "source_data_last_edited", None),
        source_data_last_edited_ms=getattr(nyzd, "source_data_last_edited_ms", None),
    )


def _footprints_provenance(footprints: ContextBuildingsResult) -> dict | None:
    """Per-layer provenance for the footprint result. ``source_id`` /
    ``dataset_id`` ride on the typed result; the query page's request URL and
    digest are the first retrieved page (this benchmark returns a single page)."""
    request_urls = getattr(footprints, "request_urls", None) or []
    raw_digests = getattr(footprints, "raw_digests", None) or []
    return _layer_provenance(
        source_id=getattr(footprints, "source_id", None),
        dataset_id=getattr(footprints, "open_data_id", None),
        request_url=request_urls[0] if request_urls else None,
        retrieved_at=getattr(footprints, "retrieved_at", None),
        raw_digest=raw_digests[0] if raw_digests else None,
        source_data_last_edited=getattr(footprints, "source_data_last_edited", None),
        source_data_last_edited_ms=getattr(footprints, "source_data_last_edited_ms", None),
    )


def _layer_provenance(
    *,
    source_id: str | None,
    dataset_id: str | None,
    request_url: str | None,
    retrieved_at: str | None,
    raw_digest: str | None,
    source_data_last_edited: str | None,
    source_data_last_edited_ms: int | None,
) -> dict | None:
    """The contract provenance block, or None when the typed result does not
    carry every required value (a layer with incomplete provenance is not drawn
    - a material value with no provenance is a defect)."""
    if source_data_last_edited is None or source_data_last_edited_ms is None:
        return None
    values = {
        "source_id": source_id,
        "dataset_id": dataset_id,
        "request_url": request_url,
        "retrieved_at": retrieved_at,
        "raw_digest_sha256": raw_digest,
        "source_data_last_edited": source_data_last_edited.split("T", 1)[0],
        "dataset_version": str(source_data_last_edited_ms),
    }
    if any(value is None for value in values.values()):
        return None
    return values


# ---------------------------------------------------------------------------
# Adapter-driven resolution: load, demote the refused surrounding layer, retry.
# ---------------------------------------------------------------------------


def _resolve_through_adapter(document: dict) -> dict:
    """Load through the E-07 adapter; a ``MapInputError`` in a surrounding layer
    demotes THAT layer to ``not_available`` carrying the adapter's message and
    the load is retried; one in the subject lot raises."""
    demotable = {"zoning_districts", "building_footprints"}
    while True:
        try:
            load_map_context(document)
            return document
        except MapInputError as error:
            layer = _layer_of(error.location)
            if layer not in demotable or document["map_context"][layer].get(
                "status"
            ) == "not_available":
                raise MapContextUnavailable(str(error)) from error
            document["map_context"][layer] = _unavailable(
                str(error), provenance=document["map_context"][layer].get("provenance")
            )


def _layer_of(location: str) -> str | None:
    parts = [part for part in (location or "").split("/") if part]
    if len(parts) >= 2 and parts[0] == "map_context":
        return parts[1]
    return None


# ---------------------------------------------------------------------------
# Small shared helpers
# ---------------------------------------------------------------------------


def _unavailable(reason: str, *, provenance: dict | None = None) -> dict:
    layer: dict = {"status": "not_available", "reason": reason, "reason_kind": _REASON_KIND}
    if provenance is not None:
        layer["provenance"] = provenance
    return layer


def _polygon(part: object) -> list[list[list[float]]]:
    """A contract polygon (exterior ring first, then holes) from a parsed
    FootprintPart, verbatim: every ring equals an input ring."""
    rings = [part.exterior, *part.holes]  # type: ignore[attr-defined]
    return [[[float(x), float(y)] for x, y in ring] for ring in rings]


def _crs_ok(crs: object) -> bool:
    return isinstance(crs, dict) and crs.get("latest_wkid") == _LATEST_WKID_2263


def _bbox_overlaps(
    a: tuple[float, float, float, float], b: tuple[float, float, float, float]
) -> bool:
    return a[0] <= b[2] and a[2] >= b[0] and a[1] <= b[3] and a[3] >= b[1]
