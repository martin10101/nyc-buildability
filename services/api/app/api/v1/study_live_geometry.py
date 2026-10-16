"""Live B-03 site-geometry provider for the study read (lane C, D-090-R124).

This is the LIVE binding for the study read's injected geometry seam
(``app.api.v1.study_inputs.GeometryProvider``, PR #390). It composes ALREADY
ACCEPTED pieces and introduces NO new connector:

- the existing live MapPLUTO lot-geometry fetch
  (:func:`app.connectors.mappluto_geometry_arcgis.fetch_lot_geometry`), adapted
  to the ``(canonical_bbl, correlation_id)`` geometry-seam convention;
- the accepted MapPLUTO outline adapter
  (:func:`app.spatial.site_geometry.lot_outline_from_mappluto`), which turns a
  single-part EPSG:2263 lot into a :class:`~app.spatial.site_geometry.LotOutline`;
- Lane B's accepted envelope-intersects street composition
  (:func:`app.spatial.site_geometry.street_data_for_lot`, PR #403), which closes
  the "no live binding produces the envelope-intersects DCM geometry pages" gap
  that formerly kept this seam unbound (it queries the City Map street centre
  lines for the lot's ENVELOPE and reuses the accepted paging/CRS/coverage gates);
- the pure B-03 derivation
  (:func:`app.spatial.site_geometry.derive_site_geometry`).

City records are NOT threaded here (``city_records=None``). The geometry seam is
called ``(canonical_bbl, correlation_id)`` and carries NO ``PlutoFetchResult``
(the PLUTO fetch is the study-inputs provider's own I/O), and the accepted
``city_records_from_pluto`` adapter needs one. Passing ``None`` is faithful:
``derive_site_geometry`` still yields the lot type, per-street frontages and
depth; only the area CROSS-CHECK against the city-recorded area is skipped (it
only annotates, it never changes a value), and the study read keeps the PLUTO
``lot_area`` fact it already carries.

Fail safe (D-051 honest absence; uncertainty never collapsed): any typed
connector or outline error -- a MapPLUTO/DCM connector failure, the live-streets
outline gate (:class:`~app.spatial.site_geometry.UnusableLotOutlineError`), a
non-EPSG:2263 geometry page, or a malformed BBL -- yields ``None`` (geometry
unavailable, so the facts stay unknown exactly as before). Nothing is ever
fabricated and the study read is never a 500 on an unavailable geometry. An
outline the adapter refuses (multi-part / holed / repaired beyond shape) is also
``None``. The failure CLASS is logged, never the payload.
"""

from __future__ import annotations

import logging
import threading
from collections import OrderedDict
from collections.abc import Callable

from app.api.v1.study_inputs import GeometryProvider, OutlineProvider
from app.connectors.bbl import BBLValidationError
from app.connectors.dcm_street_centerline_arcgis import (
    DCMConnectorError,
    DcmTransport,
    default_fetch,
)
from app.connectors.mappluto_geometry_arcgis import (
    LotGeometryResult,
    MapPlutoGeometryConnectorError,
    fetch_lot_geometry,
)
from app.spatial.site_geometry import (
    SiteGeometry,
    UnusableLotOutlineError,
    derive_site_geometry,
    lot_outline_from_mappluto,
    street_data_for_lot,
)
from app.spatial.site_geometry.outline import PreparedOutline, prepare_outline

__all__ = [
    "live_geometry_provider",
    "live_outline_provider",
    "shared_street_window_fetch",
]

logger = logging.getLogger("app.api.v1.study_live_geometry")

# Bound on the shared street-window memo (DB-273). Each request contributes at most a handful of
# entries (one metadata URL + the envelope page URLs) and never reuses another request's, so this
# only caps memory under a burst; it is intentionally far larger than any single window.
_SHARED_STREET_WINDOW_CACHE_MAX = 256


def shared_street_window_fetch(
    fetch: Callable[[str, str], DcmTransport] = default_fetch,
) -> Callable[[str, str], DcmTransport]:
    """Wrap a DCM street ``fetch`` so one request's street window is transported ONCE even when
    both the geometry provider and the street-data provider fetch it (DB-273).

    :func:`live_geometry_provider` and :func:`app.api.v1.study_inputs.live_street_data_provider`
    build the SAME envelope for the same lot in one request, so each asks the accepted paged fetch
    for the SAME metadata/page URLs. Behind ``LIVE_SPATIAL_PROVIDER_ENABLED`` (default off),
    :func:`app.api.v1.study_inputs._live_study_inputs_provider` hands this ONE wrapper to BOTH
    providers, so the window's HTTP transport runs once per request instead of twice. The flag is
    off by default, so no live behaviour changes; with it on the merged result is byte-identical to
    the two-fetch behaviour (the second provider reuses the first provider's transports).

    It is a thin pass-through: a SUCCESSFUL transport is memoised keyed by
    ``(url, correlation_id)`` -- the URL identifies the street window (the envelope is baked into
    it) and the correlation id scopes the memo to one request, so a fresh id never reuses another
    request's (or another lot's) entry and nothing is cached across requests. A fetch that RAISES is
    NOT memoised, so an unavailable window surfaces in BOTH providers exactly as the unwrapped fetch
    would (each still sees the failure and fails closed independently). The cache is bounded (LRU)
    and lock-guarded, so a burst of concurrent requests never grows it without limit and never
    returns a stale window; under contention the only effect is a missed reuse (a re-fetch).

    ``fetch`` defaults to the production
    :func:`~app.connectors.dcm_street_centerline_arcgis.default_fetch`; tests inject a counting
    double. The lot-geometry fetch is each provider's own and is not shared here (DB-273 is the
    street window only).
    """
    cache: OrderedDict[tuple[str, str], DcmTransport] = OrderedDict()
    lock = threading.Lock()

    def memoised_fetch(url: str, correlation_id: str) -> DcmTransport:
        key = (url, correlation_id)
        with lock:
            hit = cache.get(key)
            if hit is not None:
                cache.move_to_end(key)
                return hit
        # The fetch runs OUTSIDE the lock (it is I/O), so concurrent requests never serialise and a
        # raised failure never reaches the cache. A rare same-key race just fetches twice and stores
        # identical bytes -- in practice one request's two providers run sequentially on one thread.
        transport = fetch(url, correlation_id)
        with lock:
            cache[key] = transport
            cache.move_to_end(key)
            while len(cache) > _SHARED_STREET_WINDOW_CACHE_MAX:
                cache.popitem(last=False)
        return transport

    return memoised_fetch

# (canonical_bbl, correlation_id) -> MapPLUTO LotGeometryResult. The existing live
# MapPLUTO lot-geometry fetch wrapped to the geometry-seam call convention (the
# connector takes correlation_id keyword-only), mirroring
# ``app.spatial.live_provider._live_fetch_lot``.
LotGeometryFetch = Callable[[str, str], LotGeometryResult]

# Typed connector / outline errors that mean "no usable geometry for this lot":
# the facts stay unknown (the pre-geometry behaviour), never a fabricated geometry
# and never a 500. One base class each for the MapPLUTO and DCM connector stacks
# (every typed error subclasses one), Lane B's live-streets outline gate, and the
# BBL validator ``fetch_lot_geometry`` runs before any I/O. An unexpected defect is
# NOT caught here (it stays a 500, never masked as "facts unknown").
_GEOMETRY_UNAVAILABLE_ERRORS = (
    MapPlutoGeometryConnectorError,
    DCMConnectorError,
    UnusableLotOutlineError,
    BBLValidationError,
)


def _default_fetch_lot(canonical_bbl: str, correlation_id: str) -> LotGeometryResult:
    """The existing live MapPLUTO lot-geometry fetch, adapted to the
    ``(canonical_bbl, correlation_id)`` seam. No new connector: the metadata /
    drift / CRS / retry gates are the accepted connector's."""
    return fetch_lot_geometry(canonical_bbl, correlation_id=correlation_id)


def live_geometry_provider(
    *,
    fetch_lot: LotGeometryFetch = _default_fetch_lot,
    fetch_streets: Callable[[str, str], DcmTransport] = default_fetch,
) -> GeometryProvider:
    """A live B-03 :data:`~app.api.v1.study_inputs.GeometryProvider`.

    Returns a ``(canonical_bbl, correlation_id) -> SiteGeometry | None`` callable
    that, for one lot: fetches the MapPLUTO lot geometry through ``fetch_lot``,
    converts it to a :class:`~app.spatial.site_geometry.LotOutline` via the
    accepted adapter, composes the envelope-intersecting City Map streets through
    Lane B's :func:`~app.spatial.site_geometry.street_data_for_lot` (``fetch_streets``),
    and returns :func:`~app.spatial.site_geometry.derive_site_geometry`
    (``city_records=None``; see the module docstring). Any typed connector / outline
    error, or an outline the adapter refuses, yields ``None`` (geometry unavailable,
    facts stay unknown) -- never a fabricated geometry and never a 500. The failure
    CLASS is logged, never the payload.

    ``fetch_lot`` / ``fetch_streets`` are injection seams: the production defaults
    are the live connector fetches; tests and the e2e harness inject fixture-backed
    doubles so the whole seam runs offline on the recorded 215-16 Northern pack.
    """

    def provide(canonical_bbl: str, correlation_id: str) -> SiteGeometry | None:
        try:
            lot_result = fetch_lot(canonical_bbl, correlation_id)
            lot, refusal = lot_outline_from_mappluto(lot_result)
            if lot is None:
                logger.info(
                    "study_live_geometry unavailable reason=lot_outline_refused "
                    "correlation_id=%s",
                    correlation_id,
                )
                return None
            streets = street_data_for_lot(
                lot, correlation_id=correlation_id, fetch=fetch_streets
            )
            return derive_site_geometry(lot, streets, None)
        except _GEOMETRY_UNAVAILABLE_ERRORS as exc:
            logger.info(
                "study_live_geometry unavailable error_type=%s correlation_id=%s",
                type(exc).__name__,
                correlation_id,
            )
            return None

    return provide


def live_outline_provider(
    *,
    fetch_lot: LotGeometryFetch = _default_fetch_lot,
) -> OutlineProvider:
    """A live :data:`~app.api.v1.study_inputs.OutlineProvider` (M5-T134, reading O21).

    Returns a ``(canonical_bbl, correlation_id) -> PreparedOutline | None`` callable that, for one
    lot, fetches the MapPLUTO lot geometry through ``fetch_lot``, converts it to a
    :class:`~app.spatial.site_geometry.LotOutline` via the accepted
    :func:`~app.spatial.site_geometry.lot_outline_from_mappluto` adapter, and prepares it with
    :func:`~app.spatial.site_geometry.outline.prepare_outline` (the EPSG:2263 CRS gate and validity
    checks). No street data is fetched - the prepared outline needs none. Any typed connector /
    outline error, an outline the adapter refuses, or an outline ``prepare_outline`` refuses yields
    ``None`` (no usable outline, so the reach stays unknown) - never a fabricated outline and never
    a 500. The failure CLASS is logged, never the payload.

    This seam is SEPARATE from and additive to :func:`live_geometry_provider`, so every existing
    geometry provider and test double is unchanged. ``fetch_lot`` is an injection seam: the
    production default is the live connector fetch; tests and the e2e harness inject a
    fixture-backed double so the whole seam runs offline on the recorded 215-16 Northern pack.
    """

    def provide(canonical_bbl: str, correlation_id: str) -> PreparedOutline | None:
        try:
            lot_result = fetch_lot(canonical_bbl, correlation_id)
            lot, refusal = lot_outline_from_mappluto(lot_result)
            if lot is None:
                logger.info(
                    "study_live_outline unavailable reason=lot_outline_refused "
                    "correlation_id=%s",
                    correlation_id,
                )
                return None
            prepared, reason = prepare_outline(lot)
            if prepared is None:
                logger.info(
                    "study_live_outline unavailable reason=outline_not_measurable "
                    "correlation_id=%s",
                    correlation_id,
                )
                return None
            return prepared
        except _GEOMETRY_UNAVAILABLE_ERRORS as exc:
            logger.info(
                "study_live_outline unavailable error_type=%s correlation_id=%s",
                type(exc).__name__,
                correlation_id,
            )
            return None

    return provide
