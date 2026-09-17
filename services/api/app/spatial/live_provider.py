"""Settings-gated LIVE spatial-substrate provider (task M2-T020, D-032 finding A).

Composes the ACCEPTED spatial pipeline - MapPLUTO lot geometry, zoning-features
district polygons, the ZTLDB official assignment, and the M2-T013 engine via
``app.spatial.adapter.compose_from_connectors`` - into the default
``get_spatial_substrate_provider()`` seam of the internal rule-evaluation route.
No new spatial engine; this module is ORCHESTRATION ONLY (fetch -> compose).

Enablement is fail-safe and mirrors ``app.config``: the live path runs ONLY when
``LIVE_SPATIAL_PROVIDER_ENABLED`` is an explicit true token. Absent / empty /
unknown -> DISABLED, and the provider returns ``None`` exactly like the previous
default (CI stays deterministic and offline by default).

Fail-safe contract (never a fabricated substrate):

* Flag off -> ``None`` (absent substrate; evaluator fail-safes to professional
  review) with ZERO connector calls.
* Any typed connector error, malformed/unexpected failure, or transfer-limited
  (partial) district page -> ``None`` + a payload-only log line (typed error
  class + correlation id; never ``str(exc)`` - M1-T002 G5 F5 policy).
* No usable candidate districts (ZTLDB ``no_record`` / empty assignment) ->
  ``None``: composing against an empty district set would launder a missing
  input into a "no district covers this lot" geometric claim.
* Otherwise the engine's own record is returned UNMODIFIED - including its
  review / conflict / uncertain classes, which are documented fail-safe
  outcomes downstream. Uncertainty is never collapsed here.

Candidate districts come from the lot's OFFICIAL ZTLDB assignment (the MapPLUTO
geometry query returns no zoning attributes); each candidate label is fetched
from the matching zoning-features layer by the connector's bounded attribute
query, and the ENGINE - not this module - decides geometrically what actually
covers the lot, cross-checked against that same ZTLDB assignment.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from app.connectors.mappluto_geometry_arcgis import fetch_lot_geometry
from app.connectors.zoning_features_arcgis import (
    MAX_RESULT_RECORD_COUNT,
    query_features,
)
from app.connectors.ztldb_soda import fetch_by_bbl

from .adapter import compose_from_connectors

__all__ = [
    "LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR",
    "LiveSpatialFetchers",
    "build_live_substrate",
    "default_live_substrate",
    "live_spatial_provider_enabled",
]

logger = logging.getLogger("app.spatial.live_provider")

# Env var gating the live spatial path. Name declared once here. The value is
# environment-scoped and owner-visible only; this module never asserts what a
# deployed service currently carries. The CODE default, when the variable is
# absent/empty/unknown, is DISABLED (fail-safe) - see live_spatial_provider_enabled.
LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR = "LIVE_SPATIAL_PROVIDER_ENABLED"

# Same closed token set as app.config: anything else - unset, "", "0", "off",
# a typo - is DISABLED (fail safe).
_TRUE_TOKENS = frozenset({"1", "true", "yes", "on"})


def live_spatial_provider_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Whether the live spatial-substrate path is enabled. Read from ``env``
    (default ``os.environ``) on EVERY call so tests flip it with monkeypatch;
    True only for an explicit true token, absent/unknown -> False."""
    source = os.environ if env is None else env
    raw = source.get(LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR)
    if raw is None:
        return False
    return raw.strip().lower() in _TRUE_TOKENS


# ---------------------------------------------------------------------------
# Connector seams (injection points; tests swap the module default with
# doubles so the DEFAULT provider path is exercised without the network).
# ---------------------------------------------------------------------------

# (canonical_bbl, correlation_id) -> MapPLUTO LotGeometryResult
LotFetcher = Callable[[str, str], object]
# (canonical_bbl, correlation_id) -> ZtldbFetchResult
ZtldbFetcher = Callable[[str, str], object]
# (layer, field_name, value, correlation_id) -> zoning-features LayerQueryResult
DistrictLayerFetcher = Callable[[str, str, str, str], object]


@dataclass(frozen=True)
class LiveSpatialFetchers:
    """The three connector calls the live path composes, as injectable seams."""

    fetch_lot: LotFetcher
    fetch_ztldb: ZtldbFetcher
    fetch_district_layer: DistrictLayerFetcher


def _live_fetch_lot(canonical_bbl: str, correlation_id: str) -> object:
    return fetch_lot_geometry(canonical_bbl, correlation_id=correlation_id)


def _live_fetch_ztldb(canonical_bbl: str, correlation_id: str) -> object:
    return fetch_by_bbl(canonical_bbl, correlation_id=correlation_id)


def _live_fetch_district_layer(
    layer: str, field_name: str, value: str, correlation_id: str
) -> object:
    # Full bounded page: every polygon carrying the candidate label, so the
    # engine sees the containing polygon, not an arbitrary first match. A
    # result that still exceeds the transfer limit is treated as PARTIAL by
    # build_live_substrate and fail-safes to None.
    return query_features(
        layer,
        field_name,
        value,
        result_record_count=MAX_RESULT_RECORD_COUNT,
        correlation_id=correlation_id,
    )


# Module default; tests monkeypatch this attribute to inject doubles while the
# route keeps using the DEFAULT provider (no FastAPI dependency override).
_ACTIVE_FETCHERS = LiveSpatialFetchers(
    fetch_lot=_live_fetch_lot,
    fetch_ztldb=_live_fetch_ztldb,
    fetch_district_layer=_live_fetch_district_layer,
)


# ---------------------------------------------------------------------------
# Candidate-district derivation (official assignment -> bounded layer queries)
# ---------------------------------------------------------------------------


def _candidate_layer_queries(zoning_assignment: object) -> list[tuple[str, str, str]]:
    """Map the ZTLDB ``zoning_assignment`` onto deduplicated, order-preserving
    ``(layer, field_name, value)`` attribute queries. Official ordering is kept;
    slash-tie special districts contribute each component."""
    if not isinstance(zoning_assignment, dict):
        return []
    queries: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str]] = set()

    def _add(layer: str, field_name: str, value: object) -> None:
        if not (isinstance(value, str) and value.strip()):
            return
        key = (layer, value)
        if key in seen:
            return
        seen.add(key)
        queries.append((layer, field_name, value))

    for entry in zoning_assignment.get("zoning_districts", []) or []:
        if isinstance(entry, dict):
            _add("nyzd", "ZONEDIST", entry.get("value"))
    for entry in zoning_assignment.get("commercial_overlays", []) or []:
        if isinstance(entry, dict):
            _add("nyco", "OVERLAY", entry.get("value"))
    for entry in zoning_assignment.get("special_districts", []) or []:
        if not isinstance(entry, dict):
            continue
        components = entry.get("components")
        for component in components if isinstance(components, list) else []:
            _add("nysp", "SDLBL", component)
    _add("nylh", "LHLBL", zoning_assignment.get("limited_height_district"))
    return queries


# ---------------------------------------------------------------------------
# Live composition
# ---------------------------------------------------------------------------


def _fail_safe(event: str, correlation_id: str, exc: Exception | None = None) -> None:
    """Payload-only fail-safe log: event + typed error CLASS + correlation id.
    Never str(exc) (the chain may embed untrusted upstream strings)."""
    logger.warning(
        "live_spatial_substrate fail_safe event=%s error_type=%s correlation_id=%s",
        event,
        type(exc).__name__ if exc is not None else "none",
        correlation_id,
    )


def build_live_substrate(
    canonical_bbl: str,
    correlation_id: str,
    *,
    fetchers: LiveSpatialFetchers,
) -> object | None:
    """Compose the live spatial substrate for one BBL, or ``None`` (absent ->
    downstream professional-review fail-safe) on ANY failure or partial input.

    Returns the engine's ``LotIntersectionRecord`` unmodified - its review /
    conflict / uncertain classes are the documented fail-safe outcomes and are
    never collapsed or upgraded here.
    """
    try:
        ztldb_result = fetchers.fetch_ztldb(canonical_bbl, correlation_id)
        queries = _candidate_layer_queries(
            getattr(ztldb_result, "zoning_assignment", None)
        )
        if not queries:
            # no_record / empty assignment: no candidate set to verify against;
            # an empty-district composition would fabricate a geometric claim.
            _fail_safe("no_candidate_districts", correlation_id)
            return None

        lot_result = fetchers.fetch_lot(canonical_bbl, correlation_id)

        layer_results: list[object] = []
        for layer, field_name, value in queries:
            layer_result = fetchers.fetch_district_layer(
                layer, field_name, value, correlation_id
            )
            if bool(getattr(layer_result, "exceeded_transfer_limit", False)):
                # Partial district page: the containing polygon may be missing,
                # so any composition would rest on incomplete official data.
                _fail_safe("district_page_partial", correlation_id)
                return None
            layer_results.append(layer_result)

        return compose_from_connectors(lot_result, layer_results, ztldb_result)
    except Exception as exc:  # noqa: BLE001 - fail-safe boundary, typed log only
        # Typed connector errors (upstream, timeout, rate-limit, drift, CRS,
        # disallowed value, budget, circuit) and any unexpected defect all land
        # here: absent substrate, never a fabricated one and never a 500.
        _fail_safe("connector_error", correlation_id, exc)
        return None


def default_live_substrate(canonical_bbl: str, correlation_id: str) -> object | None:
    """The gated DEFAULT provider behavior behind the route's
    ``get_spatial_substrate_provider()`` seam: flag off (default) -> ``None``
    with zero connector calls (byte-identical to the pre-M2-T020 default);
    flag on -> the live composition above."""
    if not live_spatial_provider_enabled():
        return None
    return build_live_substrate(
        canonical_bbl, correlation_id, fetchers=_ACTIVE_FETCHERS
    )
