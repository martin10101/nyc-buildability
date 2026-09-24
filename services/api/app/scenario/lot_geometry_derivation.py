"""Server-side derivation of authoritative EPSG:2263 lot-line segments from the official MapPLUTO
connector by BBL (task M5-T076, DB-050(a)).

The T070 wave proved that one-action max-envelope adoption is production-UNREACHABLE: the client
rightly sends no lot geometry (its profile geometry is display 4326, never measured), and the
engine rightly refuses to fit a candidate without lot lines
(:func:`app.scenario.max_envelope._lot_rectangle` returns ``lot_geometry_unsupported`` on empty
segments). This module is the SERVER side of the cure: given a BBL, it derives the lot's
authoritative EPSG:2263 exterior-ring lot-line segments from
:mod:`app.connectors.mappluto_geometry_arcgis` (the measurement-grade 2263 canonical geometry,
NEVER the display-only 4326 outline connector), in exactly the shape
:func:`app.api.v1.proposal_checks_api._build_lot_context` validates and
:class:`app.scenario.derivation.LotContext` consumes.

The ROUTE decides eligibility, not this module: server-side derivation is invoked ONLY when the
caller supplied no lot-line geometry - an ABSENT ``lot_line_segments`` field or an EMPTY LIST
(DB-051(b) orchestrator ruling). A present-but-``null`` or otherwise malformed value is a typed 422
refusal upstream and never reaches this module - one rule, one refusal class; ``null`` is NOT
treated as absent.

Design commitments:

* AUTHORITATIVE SOURCE ONLY. The exterior ring comes from the connector's canonical EPSG:2263
  geometry (``GeometryAssessment.canonical_geometry``). The display-only 4326
  ``mappluto_lot_outline`` is NEVER read here - it is not measurement-grade.
* FAIL-CLOSED (D-051 discipline). Every failure class - the BBL is not resolvable, the service
  returns no feature, it returns multiple features (review required), the official geometry is
  unusable, the official geometry is VALID but exceeds OUR OWN segment cap, or the connector
  faults - yields a typed :class:`DerivedLotGeometry` with ``segments = None`` and a plain reason.
  The caller (the route) then keeps today's honest ``lot_geometry_unsupported`` gap. NEVER a
  fabricated or partial rectangle, NEVER a truncated ring, NEVER a silent fallback.
* PROVENANCE. A successful derivation carries the provenance quintuple (source id, BBL,
  retrieved-at, dataset version, geometry digest) so the derived facts retain their lineage.

This module performs NO network I/O itself: it takes a :data:`LotGeometryProvider` (canonical BBL
-> :class:`LotGeometryResult`) so tests inject an OFFLINE fixture-backed provider and production
injects the resilient MapPLUTO client. It is pure derivation + typed classification.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from app.connectors.bbl import BBLValidationError, normalize_bbl
from app.connectors.mappluto_geometry_arcgis import (
    GEOMETRY_REPAIRED,
    GEOMETRY_VALID,
    OUTCOME_MULTIPLE,
    OUTCOME_NONE,
    SOURCE_ID,
    GeometryAssessment,
    LotGeometryResult,
    MapPlutoGeometryConnectorError,
    ResilientMapPlutoGeometryClient,
)

__all__ = [
    "DEFAULT_MAX_DERIVED_SEGMENTS",
    "DerivedLotGeometry",
    "LotGeometryDerivationOutcome",
    "LotGeometryProvider",
    "derive_lot_line_segments",
    "production_lot_geometry_provider",
]

logger = logging.getLogger("app.scenario.lot_geometry_derivation")

#: A provider resolves a canonical 10-digit BBL to the official MapPLUTO lot-geometry result. It
#: raises :class:`MapPlutoGeometryConnectorError` on an upstream/transport fault (mapped to the
#: ``connector_fault`` class here). Production injects the resilient ArcGIS client; tests inject an
#: offline fixture-backed callable.
LotGeometryProvider = Callable[[str], LotGeometryResult]

#: Default ceiling on the number of derived lot-line segments. The route passes its own entry cap
#: (``ROUTE_MAX_LOT_LINE_SEGMENTS``); a ring above the cap is an honest fail-closed gap typed
#: ``GEOMETRY_OVER_CAP`` (OUR constraint, not bad official data), never a truncated geometry.
DEFAULT_MAX_DERIVED_SEGMENTS = 800


class LotGeometryDerivationOutcome(str, Enum):
    """Why a server-side lot-geometry derivation succeeded or (fail-closed) did not.

    ``DERIVED`` alone carries usable segments; every other outcome keeps today's honest
    ``lot_geometry_unsupported`` gap with the reason surfaced - never a fabricated rectangle."""

    #: Authoritative EPSG:2263 lot-line segments were derived from the official exterior ring.
    DERIVED = "derived"
    #: The supplied BBL is not a resolvable canonical BBL; no derivation was attempted.
    BBL_UNRESOLVABLE = "bbl_unresolvable"
    #: The official service returned a well-formed response with zero features for this BBL.
    NO_FEATURE = "no_feature"
    #: The official service returned multiple features for one BBL (review required); the
    #: connector never silently picks one, so no geometry is derived.
    MULTIPLE_FEATURES = "multiple_features"
    #: The official geometry is unusable (invalid/review-required assessment, or a degenerate
    #: exterior ring); no lot geometry is derived without review.
    INVALID_GEOMETRY = "invalid_geometry"
    #: The official geometry is VALID but its exterior ring(s) yield more segments than OUR cap
    #: allows. Deliberately distinct from ``INVALID_GEOMETRY``: the City's data is not at fault -
    #: the route's own ``ROUTE_MAX_LOT_LINE_SEGMENTS`` ceiling is the binding constraint (a real
    #: recorded lot, the MPG07 multipolygon, hits it). Never a truncated ring.
    GEOMETRY_OVER_CAP = "geometry_over_cap"
    #: The official source could not be reached or returned a typed connector error.
    CONNECTOR_FAULT = "connector_fault"


@dataclass(frozen=True)
class DerivedLotGeometry:
    """The typed result of a server-side lot-geometry derivation.

    ``segments`` is a tuple of ``{"id", "start", "end"}`` dicts (the exact shape
    :func:`app.api.v1.proposal_checks_api._build_lot_context` validates) ONLY on the ``DERIVED``
    outcome; it is ``None`` on every fail-closed outcome. ``provenance`` carries the quintuple on
    ``DERIVED`` and is ``None`` otherwise."""

    outcome: LotGeometryDerivationOutcome
    detail: str
    segments: tuple[dict, ...] | None = None
    provenance: dict | None = None

    @property
    def ok(self) -> bool:
        return self.outcome is LotGeometryDerivationOutcome.DERIVED and self.segments is not None

    def as_response_block(self) -> dict:
        """A small, strict-JSON-safe block for the route to attach to the envelope response so the
        derivation outcome + provenance stay machine-readable (never a fabricated value)."""
        return {
            "outcome": self.outcome.value,
            "detail": self.detail,
            "provenance": self.provenance,
        }


def _fail(outcome: LotGeometryDerivationOutcome, detail: str) -> DerivedLotGeometry:
    return DerivedLotGeometry(outcome=outcome, detail=detail)


#: Why no segments could be cut from an otherwise-present canonical geometry. The two causes are
#: kept APART because they say opposite things about the official source: ``_RING_DEGENERATE`` is a
#: problem with the City's geometry, ``_RING_OVER_CAP`` is a problem with OUR ceiling (the data is
#: valid). Conflating them would tell a caller the official data is bad when it is not.
_RING_DEGENERATE = "degenerate"
_RING_OVER_CAP = "over_cap"


def _exterior_ring_segments(
    canonical_geometry: list, *, max_segments: int
) -> tuple[tuple[dict, ...] | None, str | None]:
    """Turn the connector's canonical geometry (a list of polygons; each polygon's FIRST ring is
    its exterior, remaining rings are holes) into lot-line segments over the exterior ring(s) only.

    Each canonical ring is an OPEN cycle of ``[x, y]`` coordinate string pairs; consecutive
    vertices (wrapping the last back to the first) become one axis-agnostic segment. Holes are NOT
    lot lines and are excluded.

    Returns ``(segments, None)`` on success, else ``(None, reason)`` (fail-closed) where the reason
    is :data:`_RING_DEGENERATE` (an empty polygon or a ring with < 3 vertices - the official
    geometry is unusable) or :data:`_RING_OVER_CAP` (a well-formed ring whose segment count would
    exceed ``max_segments`` - OUR cap binds, never a truncated ring)."""
    segments: list[dict] = []
    for polygon in canonical_geometry:
        if not polygon:
            return None, _RING_DEGENERATE
        exterior = polygon[0]
        points = [(float(x), float(y)) for x, y in exterior]
        if len(points) < 3:
            return None, _RING_DEGENERATE
        count = len(points)
        for index in range(count):
            start_x, start_y = points[index]
            end_x, end_y = points[(index + 1) % count]
            segments.append(
                {
                    "id": f"derived-lot-line-{len(segments)}",
                    "start": [start_x, start_y],
                    "end": [end_x, end_y],
                }
            )
            if len(segments) > max_segments:
                return None, _RING_OVER_CAP
    if not segments:
        return None, _RING_DEGENERATE
    return tuple(segments), None


def _provenance_quintuple(result: LotGeometryResult, assessment: GeometryAssessment) -> dict:
    """The provenance quintuple carried on a successful derivation - source id, BBL, retrieved-at,
    dataset version, and the canonical geometry digest - plus the CRS and geometry status for
    completeness. Never guessed: a missing MapPLUTO ``Version`` attribute stays ``None``."""
    dataset_version: str | None = None
    if isinstance(result.attributes, dict):
        raw_version = result.attributes.get("Version")
        if isinstance(raw_version, str) and raw_version:
            dataset_version = raw_version
    return {
        "source_id": SOURCE_ID,
        "bbl": result.requested_bbl,
        "retrieved_at": result.retrieved_at,
        "dataset_version": dataset_version,
        "geometry_digest": assessment.normalized_digest,
        "crs": dict(result.crs) if isinstance(result.crs, dict) else result.crs,
        "geometry_status": assessment.status,
        "source_data_last_edited": result.source_data_last_edited,
    }


def derive_lot_line_segments(
    bbl: object,
    *,
    provider: LotGeometryProvider,
    max_segments: int = DEFAULT_MAX_DERIVED_SEGMENTS,
    correlation_id: str = "lot-geom-derive",
) -> DerivedLotGeometry:
    """Derive authoritative EPSG:2263 lot-line segments for ``bbl`` from the official MapPLUTO
    geometry, fail-closed. Returns a :class:`DerivedLotGeometry`: ``DERIVED`` with segments +
    provenance, or a typed honest failure with ``segments = None`` (the caller keeps today's
    ``lot_geometry_unsupported`` gap and surfaces the reason). Unexpected (non-connector)
    exceptions propagate so the caller maps them to a generic internal error."""
    try:
        normalized = normalize_bbl(bbl)
    except BBLValidationError as exc:
        return _fail(
            LotGeometryDerivationOutcome.BBL_UNRESOLVABLE,
            f"the supplied BBL is not a resolvable canonical BBL ({exc.code}); no server-side lot "
            "geometry was derived",
        )

    try:
        result = provider(normalized.canonical)
    except MapPlutoGeometryConnectorError as exc:
        logger.info(
            "lot_geometry_derivation connector_fault error_type=%s correlation_id=%s",
            exc.error_type, correlation_id,
        )
        return _fail(
            LotGeometryDerivationOutcome.CONNECTOR_FAULT,
            "the official MapPLUTO geometry source could not be reached or returned an error "
            f"({exc.error_type}); no server-side lot geometry was derived",
        )

    if result.outcome == OUTCOME_NONE:
        return _fail(
            LotGeometryDerivationOutcome.NO_FEATURE,
            "the official MapPLUTO service returned no feature for this BBL; there is no lot "
            "geometry to derive",
        )
    if result.outcome == OUTCOME_MULTIPLE:
        return _fail(
            LotGeometryDerivationOutcome.MULTIPLE_FEATURES,
            "the official MapPLUTO service returned multiple features for this BBL (review "
            "required); the connector never silently picks one, so no lot geometry is derived",
        )

    # Single feature. A review-required flag (identifier conflict, condo anomaly, or a geometry
    # pathology the connector already typed) is not silently consumed here.
    if result.review_required:
        return _fail(
            LotGeometryDerivationOutcome.INVALID_GEOMETRY,
            "the official MapPLUTO feature for this BBL is flagged review-required (identifier "
            "conflict or geometry pathology); no lot geometry is derived without human review",
        )
    assessment = result.geometry
    if (
        assessment is None
        or assessment.status not in (GEOMETRY_VALID, GEOMETRY_REPAIRED)
        or not assessment.canonical_geometry
    ):
        status = assessment.status if assessment is not None else "absent"
        return _fail(
            LotGeometryDerivationOutcome.INVALID_GEOMETRY,
            f"the official MapPLUTO geometry for this BBL is not usable (assessment status "
            f"{status!r}); no lot geometry is derived (never a fabricated rectangle)",
        )

    segments, ring_refusal = _exterior_ring_segments(
        assessment.canonical_geometry, max_segments=max_segments
    )
    if segments is None:
        if ring_refusal == _RING_OVER_CAP:
            # PROVENANCE HONESTY (permanent principle 4): the City's geometry is valid here; our
            # own ceiling is what blocks the derivation. Say so, and never truncate the ring.
            return _fail(
                LotGeometryDerivationOutcome.GEOMETRY_OVER_CAP,
                "the official MapPLUTO geometry for this BBL is valid, but its exterior ring(s) "
                f"yield more lot-line segments than this route's cap allows ({max_segments}); the "
                "official data is not at fault - our own cap is the binding constraint - so no lot "
                "geometry is derived (never a truncated ring)",
            )
        return _fail(
            LotGeometryDerivationOutcome.INVALID_GEOMETRY,
            "the official MapPLUTO exterior ring is degenerate (an empty polygon or fewer than 3 "
            "vertices); no lot geometry is derived",
        )

    return DerivedLotGeometry(
        outcome=LotGeometryDerivationOutcome.DERIVED,
        detail=(
            f"derived {len(segments)} authoritative EPSG:2263 lot-line segment(s) from the "
            "official MapPLUTO exterior ring"
        ),
        segments=segments,
        provenance=_provenance_quintuple(result, assessment),
    )


#: Lazily-constructed, cached production MapPLUTO client (cache + circuit breaker + last-known-good
#: + metrics). Constructing it is pure in-process state; the max-envelope route ships UNMOUNTED, so
#: network I/O happens only once the route is mounted at a later seam.
_PRODUCTION_CLIENT: ResilientMapPlutoGeometryClient | None = None


def production_lot_geometry_provider() -> LotGeometryProvider:
    """The production provider: resolves lot geometry from the official MapPLUTO ArcGIS connector
    via the resilient client. Injected by the route only when no test provider is set.

    DB-039(i) (mirrors :func:`app.api.v1.proposal_checks_api._effective_registry`'s doctrine): the
    lazy client global is resolved HERE, and the route calls this ON THE EVENT LOOP - it MUST NOT
    be called inside a :func:`run_in_threadpool` hop. The returned closure therefore constructs
    NOTHING: a first-touch race between concurrent worker threads could otherwise build two
    clients, splitting the response cache, circuit-breaker state, last-known-good store, and
    resilience metrics between them."""
    global _PRODUCTION_CLIENT
    if _PRODUCTION_CLIENT is None:
        _PRODUCTION_CLIENT = ResilientMapPlutoGeometryClient()
    client = _PRODUCTION_CLIENT

    def _provider(canonical_bbl: str) -> LotGeometryResult:
        return client.fetch_lot_geometry(canonical_bbl)

    return _provider
