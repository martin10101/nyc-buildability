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

from app.connectors.condo_base_lot import resolve_condo_billing
from app.connectors.mappluto_geometry_arcgis import fetch_lot_geometry
from app.connectors.zoning_features_arcgis import (
    MAX_RESULT_RECORD_COUNT,
    query_features,
)
from app.connectors.ztldb_soda import fetch_by_bbl

from .adapter import compose_from_connectors

__all__ = [
    "CONDO_BASE_LOT_UNRESOLVED_CAUSE",
    "LIVE_SPATIAL_PROVIDER_ENABLED_ENV_VAR",
    "CondoResolverSeam",
    "LiveSpatialFetchers",
    "LiveSubstrateResult",
    "build_live_substrate",
    "build_live_substrate_resolved",
    "build_substrate_substitution_stamp",
    "default_live_substrate",
    "default_live_substrate_resolved",
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
# Condo billing-BBL -> base-lot pre-lookup step (M5-T045).
#
# A condo BILLING BBL (lot 7501-7599) has no zonable land parcel of its own; the
# zoning-lot lookup must run on the condo's BASE land lot. This seam runs BEFORE
# any zoning-lot fetch and is fail-safe: a resolved SINGLE base lot substitutes
# for the input; a MULTI-LOT / UNRESOLVED / typed-ERROR outcome fail-safes to
# None (absent substrate -> downstream professional review), never fabricating a
# substrate and never collapsing a condo's divergent-zoning base lots. A non
# condo-billing BBL is a pass-through (zero connector calls) so non-condo and
# flag-off behavior stays byte-identical.
# ---------------------------------------------------------------------------

# (canonical_bbl, correlation_id) -> CondoResolution
CondoResolverSeam = Callable[[str, str], object]


def _live_resolve_condo(canonical_bbl: str, correlation_id: str) -> object:
    return resolve_condo_billing(canonical_bbl, correlation_id=correlation_id)


# Tests monkeypatch this attribute to inject a condo double, exactly like
# _ACTIVE_FETCHERS. Classification is pure, so a non-condo BBL costs zero I/O.
_ACTIVE_CONDO_RESOLVER: CondoResolverSeam = _live_resolve_condo


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


def _record_condo_substitution(
    input_bbl: str, base_bbl: str, condo_key: str | None, correlation_id: str
) -> None:
    """Payload-only record of a condo billing-BBL -> base-lot substitution.
    Only digit-string BBLs / condo_key and our own correlation id are logged;
    never an untrusted upstream string."""
    logger.info(
        "live_spatial_substrate condo_resolution input_bbl=%s base_bbl=%s "
        "condo_key=%s correlation_id=%s",
        input_bbl,
        base_bbl,
        condo_key if condo_key is not None else "none",
        correlation_id,
    )


# ---------------------------------------------------------------------------
# Condo substrate-substitution stamp + resolved-substrate carry (M5-T058).
#
# build_live_substrate historically DISCARDED the CondoResolution at the seam
# boundary - the substitution survived only as a log line. build_live_substrate_
# resolved carries the resolution ACROSS the seam in a typed LiveSubstrateResult
# so the rule-evaluation route can stamp the additive rule_evaluation
# substrate_substitution block (contract 1.2.0) and name a condo-caused refusal
# honestly (condo_base_lot_unresolved) instead of the generic
# spatial_intersection_absent. build_live_substrate REMAINS the byte-identical
# ``object | None`` seam the three other route consumers (evidence / scenario /
# scenario_analysis) still call, now delegating here for its return.
# ---------------------------------------------------------------------------

# The honest fail-safe cause carried when the substrate is absent BECAUSE a condo
# billing BBL resolved to a multi-lot / unresolved / typed-error outcome (never an
# auto-picked base lot, D-078-R002). Equals the rule_evaluation contract 1.2.0
# fail_safe_reason token; app.rules.integration maps it onto its
# FAILSAFE_CONDO_BASE_LOT_UNRESOLVED. A genuinely-absent non-condo substrate
# carries None here and keeps the generic spatial_intersection_absent reason.
CONDO_BASE_LOT_UNRESOLVED_CAUSE = "condo_base_lot_unresolved"

# Fixed plain-language records for the substitution stamp (a RECORD of a
# documented resolution, never a computed allowance).
_SUBSTITUTION_STAMP_NOTE = (
    "This analysis runs on the recorded base tax lot for the entered "
    "condominium billing lot. The entered billing lot and the analyzed base lot "
    "are recorded as entered versus analyzed - a record of the city's documented "
    "resolution, not a computed allowance."
)
_MIXED_SUBSTRATE_LOT_FACTS = "analyzed_base_lot"
_MIXED_SUBSTRATE_IDENTITY_FACTS = "entered_billing_lot"
_MIXED_SUBSTRATE_NOTE = (
    "The lot area and geometry describe the analyzed base lot; the PLUTO identity "
    "facts describe the entered billing lot."
)


@dataclass(frozen=True)
class LiveSubstrateResult:
    """The composed live substrate PLUS the condo resolution that produced it.

    ``substrate`` is the composed M2-T013 record or ``None`` - byte-identical to
    the historical :func:`build_live_substrate` return. ``substitution_stamp`` is
    the additive rule_evaluation ``substrate_substitution`` block, present ONLY
    when a single resolved condo base lot was substituted AND a real substrate
    composed; ``None`` on every other path. ``fail_safe_cause`` is
    :data:`CONDO_BASE_LOT_UNRESOLVED_CAUSE` when the substrate is absent BECAUSE a
    condo outcome fail-safed (multi-lot / unresolved / typed error), else ``None``
    (a genuinely-absent non-condo substrate keeps the generic reason).
    ``resolution`` carries the raw CondoResolution when the condo pre-lookup ran,
    for provenance; ``None`` on a non-condo pass-through or flag-off.
    """

    substrate: object | None
    substitution_stamp: dict | None = None
    fail_safe_cause: str | None = None
    resolution: object | None = None
    # True when the live substrate path actually ran (flag on) - even if it
    # fail-safed to an absent substrate. False ONLY for the settings-gated
    # flag-off no-op default, which composes nothing and issues zero connector
    # calls; the rule-evaluation route treats that no-op as "no resolved opinion"
    # and defers to the legacy object|None substrate provider (so a test/consumer
    # that injects a substrate through the unwidened seam is still honored).
    evaluated: bool = True


def build_substrate_substitution_stamp(input_bbl: str, resolution: object) -> dict:
    """Build the additive ``substrate_substitution`` block from a resolved-single
    :class:`~app.connectors.condo_base_lot.CondoResolution`.

    Reuses the accepted ``{entered_bbl, analyzed_bbl, note}`` substitution triple
    (``app.api.v1.condo_records._substitution_record`` shape) EXTENDED with the
    resolution provenance carried verbatim (never fabricated) and the machine
    readable mixed-substrate visibility block. The caller guarantees
    ``resolution.substitutes_base_lot`` is True, so ``resolved_base_bbl`` is a
    single resolved base land lot (D-078-R002: never an auto-picked one)."""
    return {
        "entered_bbl": input_bbl,
        "analyzed_bbl": getattr(resolution, "resolved_base_bbl", None),
        "note": _SUBSTITUTION_STAMP_NOTE,
        "condo_key": getattr(resolution, "condo_key", None),
        "resolution_path": getattr(resolution, "resolution_path", None),
        "source_id": getattr(resolution, "source_id", None),
        "dataset_ids": list(getattr(resolution, "dataset_ids", ()) or ()),
        "retrieved_at": getattr(resolution, "retrieved_at", None),
        "mixed_substrate": {
            "lot_facts_substrate": _MIXED_SUBSTRATE_LOT_FACTS,
            "identity_facts_substrate": _MIXED_SUBSTRATE_IDENTITY_FACTS,
            "note": _MIXED_SUBSTRATE_NOTE,
        },
    }


def build_live_substrate_resolved(
    canonical_bbl: str,
    correlation_id: str,
    *,
    fetchers: LiveSpatialFetchers,
    condo_resolver: CondoResolverSeam | None = None,
) -> LiveSubstrateResult:
    """Compose the live substrate AND carry the condo resolution across the seam.

    Identical composition and fail-safe contract to :func:`build_live_substrate`
    (which now delegates here for its ``object | None`` return), extended to a
    typed :class:`LiveSubstrateResult`: a resolved-single substitution rides WITH
    the substrate as a ``substitution_stamp``; a condo multi-lot / unresolved /
    typed-error outcome fail-safes to an absent substrate carrying
    :data:`CONDO_BASE_LOT_UNRESOLVED_CAUSE` (never an auto-picked base lot,
    D-078-R002); a non-condo path (or a non-condo absent substrate) carries
    neither, so the generic spatial_intersection_absent reason survives. The condo
    resolver is called AT MOST ONCE per evaluation."""
    resolve_condo = condo_resolver or _ACTIVE_CONDO_RESOLVER
    try:
        # Condo pre-lookup step: resolve a billing BBL to its base land lot, or
        # fail safe. Runs before any zoning-lot fetch.
        condo = resolve_condo(canonical_bbl, correlation_id)
        if getattr(condo, "is_fail_safe", False):
            # multi-lot / unresolved / typed error -> absent substrate, named
            # honestly for the condo cause. Divergent zoning is never collapsed
            # and no base lot is ever auto-selected (D-078-R002).
            _fail_safe(f"condo_{getattr(condo, 'outcome', 'fail_safe')}", correlation_id)
            return LiveSubstrateResult(
                substrate=None,
                fail_safe_cause=CONDO_BASE_LOT_UNRESOLVED_CAUSE,
                resolution=condo,
            )
        if getattr(condo, "substitutes_base_lot", False):
            substrate_bbl = getattr(condo, "resolved_base_bbl", None) or canonical_bbl
            _record_condo_substitution(
                canonical_bbl,
                substrate_bbl,
                getattr(condo, "condo_key", None),
                correlation_id,
            )
            stamp = build_substrate_substitution_stamp(canonical_bbl, condo)
            resolution = condo
        else:
            # Not a condo-billing BBL: byte-identical prior behavior, no stamp.
            substrate_bbl = canonical_bbl
            stamp = None
            resolution = None

        ztldb_result = fetchers.fetch_ztldb(substrate_bbl, correlation_id)
        queries = _candidate_layer_queries(
            getattr(ztldb_result, "zoning_assignment", None)
        )
        if not queries:
            # no_record / empty assignment: no candidate set to verify against;
            # an empty-district composition would fabricate a geometric claim. The
            # condo resolved fine (if it substituted), so this is a genuine absent
            # substrate, NOT a condo-cause refusal.
            _fail_safe("no_candidate_districts", correlation_id)
            return LiveSubstrateResult(substrate=None, resolution=resolution)

        lot_result = fetchers.fetch_lot(substrate_bbl, correlation_id)

        layer_results: list[object] = []
        for layer, field_name, value in queries:
            layer_result = fetchers.fetch_district_layer(
                layer, field_name, value, correlation_id
            )
            if bool(getattr(layer_result, "exceeded_transfer_limit", False)):
                # Partial district page: the containing polygon may be missing,
                # so any composition would rest on incomplete official data.
                _fail_safe("district_page_partial", correlation_id)
                return LiveSubstrateResult(substrate=None, resolution=resolution)
            layer_results.append(layer_result)

        substrate = compose_from_connectors(lot_result, layer_results, ztldb_result)
        return LiveSubstrateResult(
            substrate=substrate, substitution_stamp=stamp, resolution=resolution
        )
    except Exception as exc:  # noqa: BLE001 - fail-safe boundary, typed log only
        # Typed connector errors (upstream, timeout, rate-limit, drift, CRS,
        # disallowed value, budget, circuit) and any unexpected defect all land
        # here: absent substrate, never a fabricated one and never a 500.
        _fail_safe("connector_error", correlation_id, exc)
        return LiveSubstrateResult(substrate=None)


def build_live_substrate(
    canonical_bbl: str,
    correlation_id: str,
    *,
    fetchers: LiveSpatialFetchers,
    condo_resolver: CondoResolverSeam | None = None,
) -> object | None:
    """Compose the live spatial substrate for one BBL, or ``None`` (absent ->
    downstream professional-review fail-safe) on ANY failure or partial input.

    A condo billing-BBL is resolved to its base land lot BEFORE the zoning-lot
    lookup (``condo_resolver``; defaults to the module seam): a resolved single
    base lot substitutes for the input and the substitution is recorded; a
    multi-lot / unresolved / typed-error condo outcome fail-safes to ``None``,
    never fabricating a substrate and never collapsing divergent zoning. A non
    condo-billing BBL passes through unchanged with zero condo I/O.

    Returns the engine's ``LotIntersectionRecord`` unmodified - its review /
    conflict / uncertain classes are the documented fail-safe outcomes and are
    never collapsed or upgraded here.

    Delegates to :func:`build_live_substrate_resolved` and returns ONLY the
    substrate, so the three route consumers that do not carry the substitution
    (evidence / scenario / scenario_analysis) observe the exact prior
    ``object | None`` contract (a single condo-resolver call, no double SODA).
    """
    return build_live_substrate_resolved(
        canonical_bbl,
        correlation_id,
        fetchers=fetchers,
        condo_resolver=condo_resolver,
    ).substrate


def default_live_substrate(canonical_bbl: str, correlation_id: str) -> object | None:
    """The gated DEFAULT provider behavior behind the route's
    ``get_spatial_substrate_provider()`` seam: flag off (default) -> ``None``
    with zero connector calls (byte-identical to the pre-M2-T020 default);
    flag on -> the live composition above."""
    if not live_spatial_provider_enabled():
        return None
    return build_live_substrate(
        canonical_bbl,
        correlation_id,
        fetchers=_ACTIVE_FETCHERS,
        condo_resolver=_ACTIVE_CONDO_RESOLVER,
    )


def default_live_substrate_resolved(
    canonical_bbl: str, correlation_id: str
) -> LiveSubstrateResult:
    """The gated DEFAULT provider behind the rule-evaluation route's RESOLVED
    seam (``get_resolved_spatial_substrate_provider()``): flag off (default) ->
    an empty :class:`LiveSubstrateResult` (absent substrate, no stamp, no condo
    cause) with zero connector calls; flag on -> the live composition carrying the
    condo resolution. Exactly one condo-resolver call per evaluation, and the
    three other route consumers keep calling :func:`default_live_substrate`
    unchanged (no widening of their seam)."""
    if not live_spatial_provider_enabled():
        return LiveSubstrateResult(substrate=None, evaluated=False)
    return build_live_substrate_resolved(
        canonical_bbl,
        correlation_id,
        fetchers=_ACTIVE_FETCHERS,
        condo_resolver=_ACTIVE_CONDO_RESOLVER,
    )
