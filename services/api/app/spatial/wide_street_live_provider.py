"""Settings-gated LIVE wide-street-determination provider (task M5-T035,
DB-015; M5-T034 G3 INFO-C).

Composes the ACCEPTED wide-street stack into the default
``get_wide_street_determination_provider()`` seam of the internal
rule-evaluation route, mirroring ``app.spatial.live_provider`` exactly. No new
spatial engine and NO new policy decisions live here; this module is
ORCHESTRATION ONLY (fetch -> assemble accepted inputs -> call the accepted
wiring):

    MapPLUTO lot geometry (mappluto_geometry_arcgis.fetch_lot_geometry)
      -> lot-bbox-plus-buffer EPSG:2263 envelope
      -> DCM centerline segments via the NEW envelope-intersects predicate
         (dcm_street_centerline_arcgis.fetch_street_segments)
      -> D-052 width policy per candidate segment
         (dcm_street_width_policy.classify_street_width_policy)
      -> typed polylines for the wide-disposed segments
         (dcm_street_centerline_geometry.fetch_street_segment_geometries)
      -> the B7 wiring's typed determination
         (wide_street_wiring.determine_wide_street_far), which itself invokes
         the B4 buffer engine.

Enablement is fail-safe and mirrors ``app.config`` / ``app.spatial.live_provider``:
the live path runs ONLY when ``LIVE_WIDE_STREET_PROVIDER_ENABLED`` is an explicit
true token. Absent / empty / unknown -> DISABLED, and the provider returns
``None`` with ZERO connector calls (the endpoint behaves byte-identically to the
pre-M5-T035 default: the conservative conditional-FAR row governs and no
wide-street bonus is granted).

Fail-safe contract (never a fabricated determination):

* Flag off -> ``None`` with zero connector calls.
* Any typed connector error, malformed/unexpected failure, transfer-limited
  (partial) page, wrong CRS, unusable lot geometry, or insufficient data ->
  ``None`` + a payload-only log line (typed error CLASS + correlation id; never
  ``str(exc)`` - M1-T002 G5 F5 policy).
* ZERO DCM segments intersecting the envelope -> ``None`` (D-051 honest absence:
  "no DCM segment intersected the queried envelope", NEVER a confident
  not-within-100ft claim; a pipeline gap is never converted into wide OR narrow).
* Otherwise the wiring's typed determination is returned UNMODIFIED - including
  its ``professional_review_required`` class. Uncertainty is never collapsed.

WHY LIVE DETERMINATIONS NEVER FABRICATE A CONFIDENT ``within_100ft`` (honest
fail-safe, D-051): the accepted stack implements neither frontage-coverage
geometry-matching's named-street/alternate-width leg nor the ZR 12-10
named-street override table (Broadway W94-97 CD7; Allen St Rivington-Delancey
CD3; the C5-3/C6-4/C6-6 alternate-width clause). This provider therefore leaves
the B4 engine's EC-5 preconditions UNATTESTED (``named_street_override_checked``
= ``alternate_width_clause_checked`` = ``False``), so any lot with a
wide-disposed segment resolves through the wiring to
``professional_review_required`` - the honest "a qualified human must decide the
wide-street question" outcome - rather than a guessed higher FAR. An all-narrow
neighborhood resolves to a confident ``not_within_100ft_of_wide_street`` (the
conservative standard FAR row, D-051 direction). ``within_100ft_of_wide_street``
is thus produced ONLY through a caller (e.g. a test dependency override) that
supplies a fully-attested determination, never by this live composition until
the named-override table lands (DB-010, out of scope here).
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from app.connectors.dcm_street_centerline_arcgis import (
    MAX_OBJECT_ID_LIST,
    DCMConnectorError,
    StreetSegmentQueryResult,
    fetch_street_segments,
)
from app.connectors.dcm_street_centerline_geometry import (
    GEOMETRY_OK,
    SegmentGeometryQueryResult,
    fetch_street_segment_geometries,
)
from app.connectors.dcm_street_width_classifier import DISPOSITION_WIDE
from app.connectors.dcm_street_width_policy import (
    FRONTAGE_MATCH_COVERAGE_ESTABLISHED,
    AttestedPreconditions,
    PolicyDecision,
    classify_street_width_policy,
)
from app.connectors.mappluto_geometry_arcgis import (
    GEOMETRY_REPAIRED,
    GEOMETRY_VALID,
    OUTCOME_SINGLE,
    LotGeometryResult,
    MapPlutoGeometryConnectorError,
    canonical_to_shapely,
    fetch_lot_geometry,
)
from app.connectors.wide_street_buffer_engine import (
    BUFFER_FT,
    AttestedLotPolygon,
    AttestedWideSegment,
    Ec5AttestedPreconditions,
)
from app.rules.wide_street_wiring import (
    NamedStreetOverrideStatus,
    WideStreetDetermination,
    determine_wide_street_far,
)

__all__ = [
    "ENVELOPE_MARGIN_FT",
    "LIVE_WIDE_STREET_PROVIDER_ENABLED_ENV_VAR",
    "LiveWideStreetFetchers",
    "build_live_wide_street_determination",
    "default_live_wide_street_determination",
    "live_wide_street_provider_enabled",
]

logger = logging.getLogger("app.spatial.wide_street_live_provider")

# Env var gating the live wide-street path. Declared once here. The CODE default,
# when the variable is absent/empty/unknown, is DISABLED (fail-safe) - see
# live_wide_street_provider_enabled. Mirrors LIVE_SPATIAL_PROVIDER_ENABLED.
LIVE_WIDE_STREET_PROVIDER_ENABLED_ENV_VAR = "LIVE_WIDE_STREET_PROVIDER_ENABLED"

# Same closed token set as app.config / app.spatial.live_provider: anything else
# - unset, "", "0", "off", a typo - is DISABLED (fail safe).
_TRUE_TOKENS = frozenset({"1", "true", "yes", "on"})

# Margin added to the 100-ft buffer distance when deriving the DCM query
# envelope from the lot bounding box. A segment within 100 ft of the lot must
# intersect the lot bbox expanded by BUFFER_FT; the extra margin covers the
# buffer's rounded end caps and the sources' stated +/-20-ft positional accuracy
# so the candidate gather is a safe SUPERSET (the exact geometric proximity is
# decided downstream by the accepted B4 engine, never by this envelope).
ENVELOPE_MARGIN_FT = 50.0

# EC-5 preconditions the accepted stack cannot yet satisfy (see the module
# docstring): left UNATTESTED so the B4 engine refuses to compute a proximity
# result and the wiring fails safe to professional review - a WITHIN_WIDE is
# never fabricated. This is the load-bearing fail-safe of the live path.
_UNATTESTED_EC5 = Ec5AttestedPreconditions(
    named_street_override_checked=False,
    alternate_width_clause_checked=False,
    attestation_note=(
        "M5-T035 live provider: the ZR 12-10 named-street override table and "
        "the C5-3/C6-4/C6-6 alternate-width clause are not implemented in the "
        "accepted stack (DB-010, out of scope); left unattested so no confident "
        "wide-street proximity is ever computed (honest fail-safe, D-051)."
    ),
)

# The wiring's separate named-street-override attestation. The override table is
# not implemented; the provider does not itself screen for the two named streets
# (that is DB-010), so segment_may_touch is left False and the B4 EC-5 gate above
# is the fail-safe that blocks a fabricated wide determination.
_NAMED_OVERRIDE_STATUS = NamedStreetOverrideStatus(
    override_table_implemented=False,
    segment_may_touch_named_override=False,
    note=(
        "M5-T035 live provider: named-street override table not implemented "
        "(DB-010); the B4 EC-5 preconditions are left unattested so a wide "
        "determination is never fabricated."
    ),
)


def live_wide_street_provider_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Whether the live wide-street path is enabled. Read from ``env`` (default
    ``os.environ``) on EVERY call so tests flip it with monkeypatch; True only
    for an explicit true token, absent/unknown -> False."""
    source = os.environ if env is None else env
    raw = source.get(LIVE_WIDE_STREET_PROVIDER_ENABLED_ENV_VAR)
    if raw is None:
        return False
    return raw.strip().lower() in _TRUE_TOKENS


# ---------------------------------------------------------------------------
# Connector seams (injection points; tests swap the module default with doubles
# so the DEFAULT provider path is exercised without the network).
# ---------------------------------------------------------------------------

# (canonical_bbl, correlation_id) -> MapPLUTO LotGeometryResult
LotFetcher = Callable[[str, str], LotGeometryResult]
# (envelope, correlation_id) -> DCM StreetSegmentQueryResult (attributes)
EnvelopeSegmentFetcher = Callable[
    [tuple[float, float, float, float], str], StreetSegmentQueryResult
]
# (object_id_in, correlation_id) -> DCM SegmentGeometryQueryResult (typed paths)
SegmentGeometryFetcher = Callable[[list[int], str], SegmentGeometryQueryResult]


@dataclass(frozen=True)
class LiveWideStreetFetchers:
    """The three connector calls the live path composes, as injectable seams."""

    fetch_lot: LotFetcher
    fetch_segments_by_envelope: EnvelopeSegmentFetcher
    fetch_segment_geometries_by_ids: SegmentGeometryFetcher


def _live_fetch_lot(canonical_bbl: str, correlation_id: str) -> LotGeometryResult:
    return fetch_lot_geometry(canonical_bbl, correlation_id=correlation_id)


def _live_fetch_segments_by_envelope(
    envelope: tuple[float, float, float, float], correlation_id: str
) -> StreetSegmentQueryResult:
    return fetch_street_segments(envelope=envelope, correlation_id=correlation_id)


def _live_fetch_segment_geometries_by_ids(
    object_id_in: list[int], correlation_id: str
) -> SegmentGeometryQueryResult:
    return fetch_street_segment_geometries(
        object_id_in=object_id_in, correlation_id=correlation_id
    )


# Module default; tests monkeypatch this attribute to inject doubles while the
# route keeps using the DEFAULT provider (no FastAPI dependency override).
_ACTIVE_FETCHERS = LiveWideStreetFetchers(
    fetch_lot=_live_fetch_lot,
    fetch_segments_by_envelope=_live_fetch_segments_by_envelope,
    fetch_segment_geometries_by_ids=_live_fetch_segment_geometries_by_ids,
)


# ---------------------------------------------------------------------------
# Payload-only fail-safe logging (never str(exc))
# ---------------------------------------------------------------------------


def _fail_safe(event: str, correlation_id: str, exc: Exception | None = None) -> None:
    """Payload-only fail-safe log: event + typed error CLASS + correlation id.
    Never str(exc) (the chain may embed untrusted upstream strings)."""
    logger.warning(
        "live_wide_street fail_safe event=%s error_type=%s correlation_id=%s",
        event,
        type(exc).__name__ if exc is not None else "none",
        correlation_id,
    )


# ---------------------------------------------------------------------------
# Accepted-input assembly (orchestration only - no policy decisions here)
# ---------------------------------------------------------------------------


def _attested_lot(
    lot_result: LotGeometryResult, canonical_bbl: str
) -> AttestedLotPolygon | None:
    """Wrap a usable single-feature lot geometry as the B4 engine's
    ``AttestedLotPolygon``, or ``None`` when the lot is not a usable
    single-feature valid/repaired geometry (honest absence, never guessed)."""
    if getattr(lot_result, "outcome", None) != OUTCOME_SINGLE:
        return None
    if getattr(lot_result, "review_required", True):
        return None
    assessment = getattr(lot_result, "geometry", None)
    if assessment is None or assessment.status not in (GEOMETRY_VALID, GEOMETRY_REPAIRED):
        return None
    if assessment.canonical_geometry is None:
        return None
    crs = getattr(lot_result, "crs", None) or {}
    return AttestedLotPolygon(
        assessment=assessment,
        wkid=crs.get("wkid"),
        latest_wkid=crs.get("latest_wkid", crs.get("latestWkid")),
        lot_identity=canonical_bbl,
        source_retrieved_at=getattr(lot_result, "retrieved_at", None),
        source_raw_digest=getattr(lot_result, "raw_digest", None),
    )


def _lot_envelope(
    lot: AttestedLotPolygon,
) -> tuple[float, float, float, float] | None:
    """Derive the EPSG:2263 (xmin, ymin, xmax, ymax) query envelope from the lot
    bounds expanded by BUFFER_FT + ENVELOPE_MARGIN_FT. Returns ``None`` when the
    lot geometry has no usable canonical form."""
    canonical = lot.assessment.canonical_geometry
    if canonical is None:
        return None
    geom = canonical_to_shapely(canonical)
    minx, miny, maxx, maxy = geom.bounds
    pad = BUFFER_FT + ENVELOPE_MARGIN_FT
    return (minx - pad, miny - pad, maxx + pad, maxy + pad)


def _policy_decisions(seg_result: StreetSegmentQueryResult) -> list[PolicyDecision]:
    """One D-052 policy decision per candidate segment, produced by the ACCEPTED
    ``classify_street_width_policy`` (no policy logic is decided here). The
    attestations reflect what the accepted DCM connector established: the source
    is documented and versioned, the segment's mapped/paper/record street status
    was checked by the connector, and the envelope-intersects gather collected
    every candidate segment in the lot neighborhood (frontage coverage). The
    ZR 12-10 named-street / alternate-width exceptions are carried to (and
    fail-safed at) the wiring's NamedStreetOverrideStatus and the B4 EC-5 gate,
    never silently resolved here. The classifier's raw width read is used (never
    a more-permissive value); the connector's mapped-street override only ever
    narrows, so feeding the raw read stays fail-safe."""
    source_version = seg_result.source_data_last_edited or seg_result.retrieved_at
    decisions: list[PolicyDecision] = []
    for segment in seg_result.segments:
        preconditions = AttestedPreconditions(
            source_documented=True,
            source_version=source_version,
            street_status_checked=True,
            frontage_match_method=FRONTAGE_MATCH_COVERAGE_ESTABLISHED,
            matched_geometry_ref=(
                f"OBJECTID={segment.object_id}"
                if segment.object_id is not None
                else None
            ),
            exceptions_checked=True,
        )
        decisions.append(
            classify_street_width_policy(segment.width_classification, preconditions)
        )
    return decisions


def _chunks(values: list[int], size: int) -> list[list[int]]:
    return [values[i : i + size] for i in range(0, len(values), size)]


def _attested_wide_segments(
    wide_object_ids: list[int],
    fetchers: LiveWideStreetFetchers,
    correlation_id: str,
) -> list[AttestedWideSegment] | None:
    """Fetch typed geometry for the wide-disposed segments (bounded OBJECTID IN
    chunks) and wrap each usable polyline as an ``AttestedWideSegment``. Returns
    ``None`` on any transfer-limited (partial) geometry page - the buffer inputs
    would be incomplete. A segment whose geometry is not usable
    (status != GEOMETRY_OK) is excluded (never buffered on absent geometry)."""
    if not wide_object_ids:
        return []
    attested: list[AttestedWideSegment] = []
    for chunk in _chunks(wide_object_ids, MAX_OBJECT_ID_LIST):
        geom_result = fetchers.fetch_segment_geometries_by_ids(chunk, correlation_id)
        if geom_result.exceeded_transfer_limit_on_last_page:
            return None
        crs = geom_result.crs or {}
        for entry in geom_result.entries:
            if entry.status != GEOMETRY_OK:
                continue
            attested.append(
                AttestedWideSegment(
                    polyline=entry,
                    wkid=crs.get("wkid"),
                    latest_wkid=crs.get("latest_wkid", crs.get("latestWkid")),
                    classification_basis=(
                        "DCM effective_disposition=wide; ambiguity_class="
                        f"{entry.segment.width_classification.ambiguity_class}"
                    ),
                    source_retrieved_at=geom_result.retrieved_at,
                    source_raw_digest=entry.segment.streetwidth_raw,
                )
            )
    return attested


# ---------------------------------------------------------------------------
# Live composition
# ---------------------------------------------------------------------------


def build_live_wide_street_determination(
    canonical_bbl: str,
    correlation_id: str,
    *,
    fetchers: LiveWideStreetFetchers,
) -> WideStreetDetermination | None:
    """Compose the live wide-street determination for one BBL, or ``None`` on
    ANY failure/partial/insufficient input (see the module fail-safe contract).
    When it does return, it returns the accepted wiring's typed determination
    UNMODIFIED - never a fabricated one."""
    try:
        lot_result = fetchers.fetch_lot(canonical_bbl, correlation_id)
    except MapPlutoGeometryConnectorError as exc:
        _fail_safe("lot_connector_error", correlation_id, exc)
        return None
    except Exception as exc:  # noqa: BLE001 - fail-safe boundary, typed log only
        _fail_safe("lot_unexpected_error", correlation_id, exc)
        return None

    lot = _attested_lot(lot_result, canonical_bbl)
    if lot is None:
        _fail_safe("lot_not_usable", correlation_id)
        return None

    envelope = _lot_envelope(lot)
    if envelope is None:
        _fail_safe("lot_envelope_unavailable", correlation_id)
        return None

    try:
        seg_result = fetchers.fetch_segments_by_envelope(envelope, correlation_id)
    except DCMConnectorError as exc:
        _fail_safe("segment_connector_error", correlation_id, exc)
        return None
    except Exception as exc:  # noqa: BLE001 - fail-safe boundary, typed log only
        _fail_safe("segment_unexpected_error", correlation_id, exc)
        return None

    if seg_result.exceeded_transfer_limit_on_last_page:
        _fail_safe("segment_page_partial", correlation_id)
        return None
    if not seg_result.segments:
        # D-051 honest absence: no DCM segment intersected the queried envelope.
        # This is NEVER a confident not-within-100ft claim - the pipeline was
        # given nothing to test against, so the provider yields None.
        _fail_safe("no_segments_in_envelope", correlation_id)
        return None

    policy_decisions = _policy_decisions(seg_result)

    wide_object_ids = [
        segment.object_id
        for segment in seg_result.segments
        if segment.effective_disposition == DISPOSITION_WIDE
        and segment.object_id is not None
    ]
    try:
        wide_segments = _attested_wide_segments(
            wide_object_ids, fetchers, correlation_id
        )
    except DCMConnectorError as exc:
        _fail_safe("segment_geometry_connector_error", correlation_id, exc)
        return None
    except Exception as exc:  # noqa: BLE001 - fail-safe boundary, typed log only
        _fail_safe("segment_geometry_unexpected_error", correlation_id, exc)
        return None
    if wide_segments is None:
        _fail_safe("segment_geometry_partial", correlation_id)
        return None

    # The wiring never raises: it maps every typed B4 engine failure and the
    # unattested EC-5 preconditions to professional review. The returned
    # determination is passed back UNMODIFIED (uncertainty never collapsed).
    return determine_wide_street_far(
        policy_decisions,
        lot=lot,
        wide_segments=wide_segments,
        ec5_preconditions=_UNATTESTED_EC5,
        named_street_override=_NAMED_OVERRIDE_STATUS,
        correlation_id=correlation_id,
    )


def default_live_wide_street_determination(
    canonical_bbl: str, correlation_id: str
) -> WideStreetDetermination | None:
    """The gated DEFAULT behavior behind the route's
    ``get_wide_street_determination_provider()`` seam: flag off (the default) ->
    ``None`` with zero connector calls (byte-identical to the pre-M5-T035
    default); flag on -> the live composition above."""
    if not live_wide_street_provider_enabled():
        return None
    return build_live_wide_street_determination(
        canonical_bbl, correlation_id, fetchers=_ACTIVE_FETCHERS
    )
