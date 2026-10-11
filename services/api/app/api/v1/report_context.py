"""The report's map-context provider (task M5-T154, ruling Y4; D-090-R936/R937).

Turns a BBL into the 1.1.0 ``map_context`` document the report's site-context
maps draw: the subject lot among its neighbouring tax lots, the surrounding
building footprints and the named street centre lines in a window around the
lot. DETERMINISTIC assembly only - no AI, no legal interpretation.

Gating (fail-safe, mirrors :mod:`app.spatial.live_provider`): the live binding
runs ONLY when ``LIVE_SPATIAL_PROVIDER_ENABLED`` is an explicit true token;
absent / empty / unknown -> the provider returns ``None`` with ZERO connector
calls, so production reports stay without surroundings until the flag is on and
CI stays offline by default. The provider NEVER raises: a connector refusal
makes THAT layer ``not_available`` (the rest of the map is still drawn), and a
missing subject-lot outline gives ``None`` (there is no context map without a
lot).

Windows (EPSG:2263, from the subject lot's own bounding box, ruling Y2):
neighbouring tax lots and building footprints for the lot bbox **+ 400 ft**;
named street centre lines for the lot bbox **+ 1,000 ft**.

The assembly takes INJECTABLE fetch functions. :func:`recorded_pack_provider`
binds them to a recorded window pack folder so the browser-test harness
(M5-T156) renders the maps from recorded bytes with only the ``app`` package on
the Python path - no network, no test module imported.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from random import Random

from app.connectors.building_footprints_arcgis import (
    ContextBuildingsResult,
    fetch_context_buildings,
)
from app.connectors.dcm_street_centerline_arcgis import DcmTransport
from app.connectors.dcm_street_centerline_geometry import (
    SegmentGeometryQueryResult,
    fetch_street_segment_geometries,
)
from app.connectors.mappluto_geometry_arcgis import (
    LotGeometryResult,
    fetch_lot_geometry,
)
from app.connectors.mappluto_window_arcgis import (
    MapPlutoWindowConnectorError,
    MapPlutoWindowResult,
    fetch_window_lots,
)
from app.contracts.map_context import (
    MapContextUnavailable,
    ReportMapNotes,
    build_report_map_context,
)
from app.resilience.transport import TransportResponse
from app.spatial.live_provider import live_spatial_provider_enabled
from app.spatial.site_geometry.adapters import lot_outline_from_mappluto

__all__ = [
    "DEFAULT_REPORT_MAP_NOTES",
    "TAX_LOTS_WINDOW_FT",
    "STREETS_WINDOW_FT",
    "MapContextProvider",
    "ReportMapFetchers",
    "default_report_map_context_provider",
    "get_report_map_context_provider",
    "recorded_pack_provider",
]

logger = logging.getLogger("app.api.v1.report_context")

# (bbl, correlation_id) -> a schema-valid 1.1.0 map_context document, or None.
MapContextProvider = Callable[[str, str], dict | None]

# Window paddings around the subject lot's bounding box (ruling Y2, EPSG:2263 ft).
TAX_LOTS_WINDOW_FT = 400.0
STREETS_WINDOW_FT = 1000.0
_COORD_DECIMALS = 2  # canonical EPSG:2263 precision; the recorded window URLs use it

# Fixed, honest, NON-leaking reasons shown on the map when a layer's connector
# refuses (never the upstream error text, which may embed untrusted strings).
_TAX_LOTS_REFUSED = (
    "Neighbouring tax lots could not be retrieved from the city tax map for this area."
)
_STREETS_REFUSED = (
    "Street centre lines could not be retrieved from the Digital City Map for this area."
)

# Dataset attributions (verbatim; the source EDIT DATE rides on each layer's
# provenance, ruling Y7 - the caption composes 'source, date' from both).
DEFAULT_REPORT_MAP_NOTES = ReportMapNotes(
    tax_lots_attribution=(
        "Neighbouring tax lots: NYC Department of City Planning, MapPLUTO, via NYC Open Data "
        "under the NYC Open Data Terms of Use."
    ),
    buildings_attribution=(
        "Building footprints: NYC Office of Technology and Innovation, Building Footprints "
        "(NYC Open Data 5zhs-2jue), via NYC Open Data under the NYC Open Data Terms of Use."
    ),
    streets_attribution=(
        "Street centre lines: NYC Department of City Planning, Digital City Map (DCM) Street "
        "Center Line, via NYC Open Data under the NYC Open Data Terms of Use."
    ),
)


# ---------------------------------------------------------------------------
# Injectable fetch seams
# ---------------------------------------------------------------------------

# (bbl, correlation_id) -> MapPLUTO per-BBL LotGeometryResult (the subject lot)
LotFetcher = Callable[[str, str], LotGeometryResult]
# (envelope, subject_bbl, correlation_id) -> neighbouring-lot window result
WindowFetcher = Callable[[tuple[float, float, float, float], str, str], MapPlutoWindowResult]
# (envelope, correlation_id) -> building-footprint window result
FootprintsFetcher = Callable[[tuple[float, float, float, float], str], ContextBuildingsResult]
# (envelope, correlation_id) -> street-centre-line window result
StreetsFetcher = Callable[[tuple[float, float, float, float], str], SegmentGeometryQueryResult]


@dataclass(frozen=True)
class ReportMapFetchers:
    """The four connector calls the report map-context assembly composes."""

    fetch_lot: LotFetcher
    fetch_window: WindowFetcher
    fetch_footprints: FootprintsFetcher
    fetch_streets: StreetsFetcher


def _live_fetch_lot(bbl: str, correlation_id: str) -> LotGeometryResult:
    return fetch_lot_geometry(bbl, correlation_id=correlation_id)


def _live_fetch_window(
    envelope: tuple[float, float, float, float], subject_bbl: str, correlation_id: str
) -> MapPlutoWindowResult:
    return fetch_window_lots(envelope=envelope, subject_bbl=subject_bbl, interactive=True,
                             correlation_id=correlation_id)


def _live_fetch_footprints(
    envelope: tuple[float, float, float, float], correlation_id: str
) -> ContextBuildingsResult:
    return fetch_context_buildings(envelope=envelope, interactive=True,
                                   correlation_id=correlation_id)


def _live_fetch_streets(
    envelope: tuple[float, float, float, float], correlation_id: str
) -> SegmentGeometryQueryResult:
    return fetch_street_segment_geometries(envelope=envelope, correlation_id=correlation_id)


_LIVE_FETCHERS = ReportMapFetchers(
    fetch_lot=_live_fetch_lot,
    fetch_window=_live_fetch_window,
    fetch_footprints=_live_fetch_footprints,
    fetch_streets=_live_fetch_streets,
)


# ---------------------------------------------------------------------------
# Windows
# ---------------------------------------------------------------------------


def _window(
    bbox: tuple[float, float, float, float], pad: float
) -> tuple[float, float, float, float]:
    xmin, ymin, xmax, ymax = bbox
    return (round(xmin - pad, _COORD_DECIMALS), round(ymin - pad, _COORD_DECIMALS),
            round(xmax + pad, _COORD_DECIMALS), round(ymax + pad, _COORD_DECIMALS))


def _subject_bbox(lot: LotGeometryResult) -> tuple[float, float, float, float] | None:
    """The subject lot's EPSG:2263 bounding box at canonical 0.01-ft precision,
    or ``None`` when the lot has no usable EPSG:2263 outline (no subject -> no
    map). Mirrors the precision the recorded window URLs were derived at."""
    outline, _reason = lot_outline_from_mappluto(lot)
    if outline is None:
        return None
    crs = getattr(outline, "crs", None)
    if not (isinstance(crs, dict) and crs.get("latest_wkid") == 2263):
        return None
    xs = [round(float(x), _COORD_DECIMALS) for x, _y in outline.exterior]
    ys = [round(float(y), _COORD_DECIMALS) for _x, y in outline.exterior]
    if not xs or not ys:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


# ---------------------------------------------------------------------------
# Assembly (never raises)
# ---------------------------------------------------------------------------


def _log_fail(event: str, correlation_id: str, exc: Exception | None = None) -> None:
    """Payload-only fail-safe log: event + typed error CLASS + correlation id.
    Never ``str(exc)`` (the chain may embed untrusted upstream strings)."""
    logger.warning("report_map_context fail event=%s error_type=%s correlation_id=%s",
                   event, type(exc).__name__ if exc is not None else "none", correlation_id)


def _assemble(bbl: str, correlation_id: str, fetchers: ReportMapFetchers,
              notes: ReportMapNotes) -> dict | None:
    try:
        lot = fetchers.fetch_lot(bbl, correlation_id)
    except Exception as exc:  # noqa: BLE001 - fail-safe boundary; no subject -> None
        _log_fail("subject_lot", correlation_id, exc)
        return None
    bbox = _subject_bbox(lot)
    if bbox is None:
        return None  # no usable EPSG:2263 subject outline -> no context map (ruling Y4)
    context_window = _window(bbox, TAX_LOTS_WINDOW_FT)
    streets_window = _window(bbox, STREETS_WINDOW_FT)

    window: MapPlutoWindowResult | None = None
    tax_reason: str | None = None
    try:
        window = fetchers.fetch_window(context_window, bbl, correlation_id)
    except MapPlutoWindowConnectorError as exc:
        tax_reason = _TAX_LOTS_REFUSED
        _log_fail("tax_lots", correlation_id, exc)
    except Exception as exc:  # noqa: BLE001 - any failure demotes the layer, never crashes
        tax_reason = _TAX_LOTS_REFUSED
        _log_fail("tax_lots", correlation_id, exc)

    footprints: ContextBuildingsResult | None = None
    try:
        footprints = fetchers.fetch_footprints(context_window, correlation_id)
    except Exception as exc:  # noqa: BLE001 - fetch_context_buildings never raises; guard anyway
        _log_fail("building_footprints", correlation_id, exc)

    streets: SegmentGeometryQueryResult | None = None
    streets_reason: str | None = None
    try:
        streets = fetchers.fetch_streets(streets_window, correlation_id)
    except Exception as exc:  # noqa: BLE001 - any failure demotes the layer, never crashes
        streets_reason = _STREETS_REFUSED
        _log_fail("streets", correlation_id, exc)

    try:
        return build_report_map_context(
            lot,
            context_window=context_window,
            tax_lots=window,
            tax_lots_unavailable_reason=tax_reason,
            footprints=footprints,
            streets=streets,
            streets_unavailable_reason=streets_reason,
            streets_window=streets_window,
            notes=notes,
        )
    except MapContextUnavailable:
        return None  # subject outline refused at build time -> None
    except Exception as exc:  # noqa: BLE001 - a built document that cannot validate -> None
        _log_fail("assembly", correlation_id, exc)
        return None


# ---------------------------------------------------------------------------
# Default (live-gated) provider + FastAPI dependency
# ---------------------------------------------------------------------------


def default_report_map_context_provider(bbl: str, correlation_id: str) -> dict | None:
    """The gated DEFAULT provider: flag off (default) -> ``None`` with zero
    connector calls; flag on -> the live assembly above (never raises)."""
    if not live_spatial_provider_enabled():
        return None
    return _assemble(bbl, correlation_id, _LIVE_FETCHERS, DEFAULT_REPORT_MAP_NOTES)


def get_report_map_context_provider() -> MapContextProvider:
    """FastAPI dependency returning the report map-context provider (the route's
    test-override point). The default is the live provider, gated OFF in
    production by ``LIVE_SPATIAL_PROVIDER_ENABLED``; the browser-test harness
    overrides it with :func:`recorded_pack_provider`."""
    return default_report_map_context_provider


# ---------------------------------------------------------------------------
# Recorded-pack harness entry point (ruling Y4): bind the provider to a pack
# folder so the browser test renders from recorded bytes, app-package-only.
# ---------------------------------------------------------------------------

_BASE_PACK_NAME = "benchmark_215_16_northern"
_REPLAY_CLOCK = datetime(2026, 10, 10, 19, 5, 57, tzinfo=UTC)


def _resolve_inside(folder: Path, name: object) -> Path:
    """Resolve a MANIFEST ``file`` entry against its pack ``folder`` and REFUSE
    any path that escapes the folder (``..`` traversal or an absolute path), so a
    hostile or broken MANIFEST can never make the loader read a file outside its
    own pack (G5 A1). The file must also be a plain name, not a nested path."""
    if not isinstance(name, str) or not name or "/" in name or "\\" in name:
        raise ValueError(f"MANIFEST file entry must be a plain file name, got {name!r}")
    resolved = (folder / name).resolve()
    if not resolved.is_relative_to(folder.resolve()):
        raise ValueError(f"MANIFEST file entry {name!r} escapes its pack folder {folder}")
    return resolved


def _pack_url_map(pack_dir: Path, base_pack_dir: Path | None) -> dict[str, tuple[Path, str]]:
    """URL -> (file path, retrieved_at) from the window pack PLUS the base pack it
    extends (per-BBL subject geometry + each layer's metadata). The window pack
    overrides the base on a URL collision. Every resolved file path is proven to
    stay inside its own pack folder (:func:`_resolve_inside`). Only the ``app``
    package and the pack folders (plain files) are needed - no test module is
    imported."""
    base = base_pack_dir if base_pack_dir is not None else pack_dir.parent / _BASE_PACK_NAME
    url_map: dict[str, tuple[Path, str]] = {}
    for folder in (base, pack_dir):
        manifest = folder / "MANIFEST.json"
        if not manifest.exists():
            continue
        for entry in json.loads(manifest.read_text("utf-8")).get("files", []):
            path = _resolve_inside(folder, entry.get("file"))
            url_map[entry["url"]] = (path, entry.get("retrieved_at", ""))
    return url_map


def recorded_pack_provider(
    pack_dir: str | Path,
    *,
    base_pack_dir: str | Path | None = None,
    notes: ReportMapNotes | None = None,
) -> MapContextProvider:
    """Bind the provider to a recorded window pack folder (M5-T154 pack), serving
    the recorded bytes through the real connectors' own fetch/parse code - NO
    network. Usable with only the ``app`` package importable. The subject lot's
    per-BBL geometry and the layers' metadata come from the base pack the window
    pack extends (``../benchmark_215_16_northern`` by default)."""
    pack = Path(pack_dir)
    base = Path(base_pack_dir) if base_pack_dir is not None else None
    url_map = _pack_url_map(pack, base)
    report_notes = notes if notes is not None else DEFAULT_REPORT_MAP_NOTES

    def _body(url: str) -> str:
        record = url_map.get(url)
        if record is None:
            raise FileNotFoundError(f"no recorded response for URL in the pack: {url}")
        return record[0].read_text("utf-8")

    def _transport(url: str, headers: Mapping[str, str], timeout: float) -> TransportResponse:
        return TransportResponse(200, _body(url))

    def _dcm_fetch(url: str, correlation_id: str) -> DcmTransport:
        record = url_map.get(url)
        if record is None:
            raise FileNotFoundError(f"no recorded response for URL in the pack: {url}")
        retrieved_at = record[1] or _REPLAY_CLOCK.strftime("%Y-%m-%dT%H:%M:%SZ")
        return DcmTransport(url=url, status=200, body=record[0].read_text("utf-8"),
                            retrieved_at=retrieved_at)

    def _no_sleep(_seconds: float) -> None:
        return None

    def fetch_lot(bbl: str, correlation_id: str) -> LotGeometryResult:
        return fetch_lot_geometry(bbl, transport=_transport, sleep=_no_sleep,
                                  clock=lambda: _REPLAY_CLOCK, rng=Random(0),
                                  correlation_id=correlation_id)

    def fetch_window(envelope, subject_bbl, correlation_id) -> MapPlutoWindowResult:
        return fetch_window_lots(envelope=envelope, subject_bbl=subject_bbl, transport=_transport,
                                 sleep=_no_sleep, clock=lambda: _REPLAY_CLOCK, rng=Random(0),
                                 correlation_id=correlation_id)

    def fetch_footprints(envelope, correlation_id) -> ContextBuildingsResult:
        return fetch_context_buildings(envelope=envelope, page_size=2000, transport=_transport,
                                       sleep=_no_sleep, clock=lambda: _REPLAY_CLOCK, rng=Random(0),
                                       correlation_id=correlation_id)

    def fetch_streets(envelope, correlation_id) -> SegmentGeometryQueryResult:
        return fetch_street_segment_geometries(envelope=envelope, fetch=_dcm_fetch,
                                               correlation_id=correlation_id)

    fetchers = ReportMapFetchers(fetch_lot=fetch_lot, fetch_window=fetch_window,
                                 fetch_footprints=fetch_footprints, fetch_streets=fetch_streets)

    def provider(bbl: str, correlation_id: str) -> dict | None:
        return _assemble(bbl, correlation_id, fetchers, report_notes)

    return provider
