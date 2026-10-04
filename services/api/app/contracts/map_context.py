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
    from app.connectors.mappluto_geometry_arcgis import LotGeometryResult
    from app.connectors.zoning_features_arcgis import LayerQueryResult

__all__ = [
    "MapContextUnavailable",
    "MapNotes",
    "build_map_context",
]

CONTRACT_VERSION = "1.0.0"
DOCUMENT_KIND = "map_context"
UNITS = "feet"
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
