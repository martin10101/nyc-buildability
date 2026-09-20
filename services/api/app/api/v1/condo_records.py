"""GET /api/v1/properties/{bbl}/condo-records - per-BBL condo RECORDS view
(task M5-T052, DB-031).

Surfaces the HONEST records view of a condominium billing (or unit) BBL: the
recorded billing lot, the FULL set of recorded base tax lots, and the substrate
record of any billing->base substitution, all with provenance. It is the
"missing half" of the M5-T045 condo work: a professional reviewing a multi-lot
condo previously saw only the fail-safe withhold with no view of what the city
actually records; this channel transports those records for display.

Route posture mirrors the accepted lot-geometry / record-address sibling routes
EXACTLY (app.api.v1.lot_geometry):

- Feature-flag gated OFF by default (reuses the EXISTING
  ``INTERNAL_RULE_EVAL_ENABLED`` flag - the condo records view is part of the
  same internal property flow and app.config is out of this packet's scope, so
  it reuses that flag and adds NO new one). Absent/empty/unknown -> a generic
  ``404 Not Found`` byte-indistinguishable from an unmounted path.
  ``include_in_schema=False`` so it never appears in OpenAPI.
- No authentication yet (service is internal/dev only).
- BODY-LESS: only the ``bbl`` path parameter. The BBL flows through
  ``normalize_bbl`` BEFORE any I/O; the resolver is reached only with the
  canonical value.

RECORDS, NEVER ALLOWANCES (D-073-R006). This channel makes NO zoning
determination and NEVER collapses a multi-lot set. Every outcome is an honest
typed record:

- ``resolved_single_base_lot``: the billing BBL resolves to EXACTLY ONE base
  lot; the substitution is recorded (which BBL was entered, which the analysis
  runs on) so the consumer can proceed on the substituted base lot (the allow
  path). The substrate record is the G3-A4 rider.
- ``multi_lot_set``: TWO OR MORE base lots. FAIL-SAFE: every base lot is a
  RECORD only; no single lot is chosen and no allowance is computed.
- ``unresolved`` / ``error``: honest absence / typed transport failure; no
  fabricated base lot, no records section on the consuming surface.
- ``not_condo_billing``: the input is not a condo lot; empty records.

GUARD-COHERENCE / CROSS-BOUNDARY TOKEN PIN (the T045 G3-A2 answer). The
``outcome`` token this route emits is the resolver's OWN typed outcome
(:data:`app.connectors.condo_base_lot.OUTCOME_*`) - the SAME literal the web
guard (``condoWithholdsAllowances``) and the web records view branch on. api and
web share ONE outcome vocabulary, pinned by tests on both sides, so the
allowance-withhold guard and the records view can never classify the same
resolution differently. The web display derives ONE state from that token; this
route is the production transport of the same typed resolution.

UNIT-BBL INCREMENT (G3-A3). A condo UNIT BBL (1001-6999) is resolved through the
accepted resolver's unit path (``app.connectors.dtm_condo_soda.resolve``, which
expands by ``condo_key`` to the full base-lot set) and mapped onto the SAME
outcome tokens, so a unit input reaches its billing/base outcome (single ->
substitution recorded; multi -> records only). Billing BBLs go through the
accepted seam ``resolve_condo_billing``.

The resolver seams are INJECTED (the lot-geometry dependency-injection pattern)
so the whole suite runs fully OFFLINE against recorded resolution fixtures. The
resolver connectors are consumed READ-ONLY; this module owns no resolution
logic and adds no contract-schema change (the document is this route's own
report shape, exactly like the record-address document).

``CONDO_RECORDS_STATUS_STATE_MATRIX`` below is the single source of truth for
every emitted (HTTP status, state) pair.
"""

from __future__ import annotations

import json
import logging
import uuid
from collections.abc import Callable

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.config import internal_rule_eval_enabled
from app.connectors.bbl import BBLValidationError, normalize_bbl
from app.connectors.condo_base_lot import (
    OUTCOME_ERROR,
    OUTCOME_MULTI_LOT,
    OUTCOME_RESOLVED_SINGLE,
    OUTCOME_UNRESOLVED,
    CondoResolution,
    resolve_condo_billing,
)
from app.connectors.dtm_condo_soda import (
    CONDO_DATASET_ID,
    DIVERGENT_ZONING_NOTICE,
    LOT_CLASS_BILLING,
    LOT_CLASS_UNIT,
    SOURCE_ID,
    STATUS_RESOLVED,
    STATUS_UNRESOLVED,
    CondoBaseLotResult,
    DtmCondoConnectorError,
    classify_lot,
)
from app.connectors.dtm_condo_soda import (
    resolve as dtm_resolve,
)
from app.site_definition import (
    SiteDefinitionStore,
    build_site_definition_block,
    default_site_definition_store,
)

__all__ = [
    "CONDO_RECORDS_STATUS_STATE_MATRIX",
    "CondoBillingResolver",
    "CondoUnitResolver",
    "get_condo_billing_resolver",
    "get_condo_site_definition_store",
    "get_condo_unit_resolver",
    "router",
]

logger = logging.getLogger("app.api.v1.condo_records")

router = APIRouter(prefix="/api/v1", tags=["condo_records"])

DOCUMENT_KIND = "condo_records"

# Recorded-zoning availability status vocabulary. The DTM condo base-lot channel
# this route consumes read-only records lot IDENTITY only (no zoning column), so
# a base lot's recorded zoning is a genuine UNKNOWN today - LABELLED explicitly,
# never a silent null. When an upstream channel begins carrying per-base-lot
# zoning it flows through ``_recorded_zoning_for`` unchanged and the status
# becomes RECORDED with no shape change.
ZONING_STATUS_RECORDED = "recorded"
ZONING_STATUS_UNKNOWN = "unknown"

# Billing-lot availability status. A billing-class entry IS the billing lot
# (recorded); a UNIT-class entry resolves through the unit path, which returns
# the base-lot set but NOT the billing lot, so the billing lot is a genuine
# UNKNOWN (never the entered unit BBL relabelled as billing); a non-condo input
# has no billing lot (not applicable). The status is LABELLED so a genuinely
# missing billing record is explicit, never a bare null a reader must interpret.
BILLING_STATUS_RECORDED = "recorded"
BILLING_STATUS_UNKNOWN = "unknown"
BILLING_STATUS_NOT_APPLICABLE = "not_applicable"

# Defense-in-depth length cap for the reflected raw_value repr embedded in a 422
# validation detail (DB-036(h); the DB-023c / DB-034(b) bounded-repr class). The
# BBL arrives as a URL path segment, but a hostile or oversized entered value must
# never let the echoed repr flood the error body, the logs, or a client's
# accessibility tree. The BBLValidationError payload's raw_value is ALREADY
# repr()-sanitized in app.connectors.bbl; this caps its LENGTH only. A repr at or
# under the cap is returned byte-identically, so every ordinary 422 is unchanged.
MAX_RAW_VALUE_REPR_CHARS = 256
_RAW_VALUE_TRUNCATION_MARKER = "...[truncated]"

# The concrete dependency that must be resolved (by the orchestrator, OUTSIDE
# this packet's forbidden connector/spatial/profile paths) before a base lot can
# carry recorded zoning. Surfaced in the payload whenever any base lot's zoning
# is unknown, so the universally-unknown zoning is an explicit, attributable gap
# with a named dependency - never a silently-deferred contract requirement and
# never a fabricated district. Full write-up: the M5-T052 producer report.
RECORDED_ZONING_DEPENDENCY = (
    "Recorded zoning per base lot is not carried by the DOF DTM condo base-lot "
    "channel this route consumes read-only (it records lot identity only; no "
    "zoning column - verified in app.connectors.dtm_condo_soda CONDO_COLUMNS / "
    "UNIT_COLUMNS and app.connectors.condo_base_lot.CondoResolution). Supplying "
    "it requires the ZTLDB / spatial zoning-by-BBL lookup, which lives in this "
    "packet's forbidden connector/spatial/profile paths and would require network "
    "in tests; it is routed to the orchestrator as an out-of-scope dependency "
    "(M5-T052 producer report)."
)

# ---------------------------------------------------------------------------
# EXACT (HTTP status, state) pair matrix. Every honest condo-records outcome is
# a 200 with NO ``state`` field (the document's own ``outcome`` discriminates);
# the disabled / not-found sentinel is a 404 with NO ``state`` (byte-identical
# to an unmounted path). A malformed BBL is a typed 422; an unexpected internal
# defect is a generic typed 500. There is no 5xx transport branch here: a typed
# connector failure is a NORMAL 200 ``error`` records document (the fail-safe
# the consumer surfaces), never an HTTP error - the resolver's typed error is a
# recorded outcome, not a route fault.
# ---------------------------------------------------------------------------
CONDO_RECORDS_STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # condo-records document (its own ``outcome`` discriminates)
        (404, None),  # flag off / unmounted-path sentinel (generic Not Found)
        (422, "validation_error"),  # malformed BBL, no resolver call
        (500, "internal_error"),  # unexpected internal defect (generic)
    }
)


# Billing-resolution seam: (canonical_bbl, correlation_id) -> CondoResolution.
# The default is the accepted policy seam; tests inject recorded resolutions.
CondoBillingResolver = Callable[[str, str], CondoResolution]
# Unit-resolution seam: (canonical_bbl, correlation_id) -> CondoBaseLotResult.
# The default is the accepted resolver's unit path; tests inject recorded
# results. A billing consumer never calls this; a UNIT-class input does.
CondoUnitResolver = Callable[[str, str], CondoBaseLotResult]


def _default_billing_resolver(canonical_bbl: str, correlation_id: str) -> CondoResolution:
    """Production billing resolution: the accepted policy seam, read-only. It
    already classifies, resolves a billing BBL, and maps a typed transport
    failure onto :data:`OUTCOME_ERROR` (never raising for a routine miss)."""
    return resolve_condo_billing(canonical_bbl, correlation_id=correlation_id)


def _default_unit_resolver(canonical_bbl: str, correlation_id: str) -> CondoBaseLotResult:
    """Production unit resolution: the accepted resolver's unit path, read-only.
    It reverse-resolves the unit and expands by ``condo_key`` to the full
    base-lot set (never collapsed). Its typed :class:`DtmCondoConnectorError` is
    caught by the route and recorded as an ``error`` outcome."""
    return dtm_resolve(canonical_bbl, correlation_id=correlation_id)


def get_condo_billing_resolver() -> CondoBillingResolver:
    """Dependency returning the billing-resolution seam (test override point)."""
    return _default_billing_resolver


def get_condo_unit_resolver() -> CondoUnitResolver:
    """Dependency returning the unit-resolution seam (test override point)."""
    return _default_unit_resolver


# Site-definition confirmations (M5-T059, D-078). The multi-lot document surfaces
# any RECORDED human site-definition confirmation (or an explicit unconfirmed
# status) read-only; the assembly lives in the site_definition package. Reading a
# confirmation NEVER selects a site or changes any calculation (D-078-R002): this
# is additive surfacing only.
def get_condo_site_definition_store() -> SiteDefinitionStore:
    """Dependency returning the store the condo-records document reads recorded
    site-definition confirmations from (test override point).

    Binds to the ONE shared package default (``default_site_definition_store``) -
    the SAME object the (unmounted) write API writes to - so a confirmation
    created there surfaces on this read document through the same binding. In
    production the write route is unmounted, so the shared default is empty and
    this document honestly shows "unconfirmed"; tests override it with a fresh
    store."""
    return default_site_definition_store()


def _json(status_code: int, body: dict, correlation_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=body,
        headers={"X-Correlation-ID": correlation_id},
    )


def _not_found() -> JSONResponse:
    """Generic 404 identical to FastAPI's default for an unmounted path. Carries
    NO correlation id and NO body hint, so a disabled feature is
    indistinguishable from a route that does not exist (fail-safe disable)."""
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


def _capped_raw_value(raw_value_repr: str) -> str:
    """Length-cap the reflected raw_value repr embedded in a 422 detail (DB-036(h),
    defense-in-depth). The repr is already sanitized in app.connectors.bbl; this
    only bounds its LENGTH so an oversized entered value cannot flood the error
    body. A repr at or under the cap is returned unchanged (byte-identical 422)."""
    if len(raw_value_repr) <= MAX_RAW_VALUE_REPR_CHARS:
        return raw_value_repr
    return raw_value_repr[:MAX_RAW_VALUE_REPR_CHARS] + _RAW_VALUE_TRUNCATION_MARKER


def _internal_error_500(correlation_id: str) -> JSONResponse:
    """Documented generic 500 for ANY unexpected exception. Logs the type +
    correlation id only (no str(exc)/traceback: the chain may embed untrusted
    upstream strings - payload-only logging policy)."""
    return _json(
        500,
        {
            "state": "internal_error",
            "message": "unexpected internal error; see server logs by correlation id",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _assert_json_safe(document: dict) -> None:
    """Both JSON renderings the stack could use MUST succeed before send (the
    lot-geometry renderer-parity guard): ``allow_nan=False`` rejects
    NaN/Infinity, and the ``ensure_ascii=False`` + utf-8 form is what Starlette's
    ``JSONResponse.render`` uses and raises on an unpaired surrogate."""
    json.dumps(document, allow_nan=False)
    json.dumps(document, ensure_ascii=False, allow_nan=False).encode("utf-8")


# ---------------------------------------------------------------------------
# Unit-path adaptation. A UNIT-class BBL is resolved through the accepted
# resolver's unit path, which returns the richer :class:`CondoBaseLotResult`.
# It is mapped onto the SAME typed :class:`CondoResolution` outcome the billing
# seam produces, using the resolver's PUBLIC status constants, so a unit input
# and a billing input share one outcome vocabulary and one document builder
# (the token pin holds across both entry paths). This mirrors the billing
# seam's own status->outcome mapping (``condo_base_lot._from_result``).
# ---------------------------------------------------------------------------
def _resolution_from_unit_result(
    canonical_bbl: str, correlation_id: str, result: CondoBaseLotResult
) -> CondoResolution:
    dataset_ids = tuple(
        dict.fromkeys(
            entry.get("dataset_id")
            for entry in result.provenance
            if entry.get("dataset_id")
        )
    ) or (CONDO_DATASET_ID,)
    common = {
        "input_bbl": canonical_bbl,
        "correlation_id": correlation_id,
        "condo_key": result.condo_key,
        "condo_number": result.condo_number,
        "resolution_path": result.resolution_path,
        "source_id": SOURCE_ID,
        "dataset_ids": dataset_ids,
        "retrieved_at": result.retrieved_at,
        "provenance": tuple(result.provenance),
        "divergent_zoning_notice": DIVERGENT_ZONING_NOTICE,
        "notes": tuple(result.notes),
    }
    if result.status == STATUS_RESOLVED:
        base_bbls = tuple(result.base_bbls)
        if len(base_bbls) == 1:
            return CondoResolution(
                outcome=OUTCOME_RESOLVED_SINGLE,
                base_bbls=base_bbls,
                resolved_base_bbl=base_bbls[0],
                **common,
            )
        return CondoResolution(
            outcome=OUTCOME_MULTI_LOT,
            base_bbls=base_bbls,
            resolved_base_bbl=None,
            **common,
        )
    if result.status == STATUS_UNRESOLVED:
        return CondoResolution(outcome=OUTCOME_UNRESOLVED, **common)
    # A unit input never yields not-a-condo, but any unknown status is treated
    # as fail-safe unresolved, never as success (never a fabricated base lot).
    return CondoResolution(outcome=OUTCOME_UNRESOLVED, **common)


def _error_resolution(
    canonical_bbl: str, correlation_id: str, exc: DtmCondoConnectorError
) -> CondoResolution:
    """Map a typed unit-path transport failure onto :data:`OUTCOME_ERROR`,
    exactly as the billing seam does for the billing path."""
    return CondoResolution(
        outcome=OUTCOME_ERROR,
        input_bbl=canonical_bbl,
        correlation_id=correlation_id,
        source_id=SOURCE_ID,
        error_type=exc.error_type,
        notes=(
            "condo base-lot resolution failed with a typed transport error; the "
            "records view is withheld and the consumer fail-safes to "
            "professional review (never a fabricated base lot).",
        ),
    )


# ---------------------------------------------------------------------------
# Document assembly. The condo-records document is this route's OWN report shape
# (no contract-schema change), built VERBATIM from the typed resolution.
#
# RECORDED ZONING PER BASE LOT (M5-T052). Every base lot is a RECORD that carries
# its recorded zoning, an EXPLICIT status LABEL for that zoning, and that record's
# provenance, so a reviewer sees, per base lot, what zoning the city records (or
# that it is a genuine unknown) and where the record came from. The recorded
# zoning is read from whatever the resolution carries for the lot
# (``_recorded_zoning_for``); the accepted DTM condo base-lot channel this route
# consumes records lot IDENTITY, not zoning (established read-only against
# ``dtm_condo_soda.CONDO_COLUMNS`` / ``UNIT_COLUMNS`` and
# ``condo_base_lot.CondoResolution`` - neither carries a zoning column), so today
# every value is ``recorded_zoning = null`` with ``recorded_zoning_status =
# "unknown"`` - a LABELLED unknown, never a silent null and never a fabricated
# district. The genuinely-unavailable zoning is NOT silently deferred: the
# document carries :data:`RECORDED_ZONING_DEPENDENCY` naming the concrete
# downstream dependency (ZTLDB / spatial zoning-by-BBL), which lives in this
# packet's FORBIDDEN connector/spatial/profile paths and is routed to the
# orchestrator in the producer report. When an upstream channel begins carrying
# per-base-lot zoning it flows through the SAME ``_recorded_zoning_for`` seam and
# the status flips to RECORDED with no shape change. The record's provenance
# reaches every base lot regardless, so the unknown is an honest, attributable
# gap, not a bare blank.
# ---------------------------------------------------------------------------
def _dataset_version(resolution: CondoResolution) -> str | None:
    """The dataset version (SODA ``rows_updated_at``) the source stamped, taken
    from the first query that carries one; honest ``None`` when the source
    omitted it, never fabricated."""
    for entry in resolution.provenance:
        rows_updated_at = entry.get("rows_updated_at")
        if rows_updated_at:
            return rows_updated_at
    return None


def _record_provenance(resolution: CondoResolution) -> dict:
    """The provenance attached to EVERY recorded base lot: the official source
    id, the dataset ids, the retrieval timestamp, and the dataset version. It is
    the attribution for the city record of the base lot's IDENTITY, so a reviewer
    can trace each base-lot record to its source even when the base lot's
    recorded zoning is a genuine unknown."""
    return {
        "source_id": resolution.source_id or SOURCE_ID,
        "dataset_ids": list(resolution.dataset_ids),
        "retrieved_at": resolution.retrieved_at,
        "dataset_version": _dataset_version(resolution),
    }


def _recorded_zoning_for(base_bbl: str, resolution: CondoResolution) -> str | None:
    """Return the recorded zoning the resolution carries for ``base_bbl``, or
    ``None`` when it is genuinely absent. Data-driven, not a hardcoded blank: the
    accepted DTM condo base-lot resolver this route consumes carries lot identity
    only (its columns hold no zoning district), so the value is honestly unknown
    here. When an upstream channel begins carrying per-base-lot zoning, it flows
    through this one seam without a shape change - unknown is retained ONLY for a
    lot whose zoning is genuinely absent from the resolution."""
    del base_bbl, resolution  # the DTM condo resolution carries no zoning today
    return None


def _base_lot_records(resolution: CondoResolution) -> list[dict]:
    provenance = _record_provenance(resolution)
    records: list[dict] = []
    for base_bbl in resolution.base_bbls:
        zoning = _recorded_zoning_for(base_bbl, resolution)
        records.append(
            {
                "bbl": base_bbl,
                # Recorded zoning + an EXPLICIT status label, so a genuinely
                # missing zoning record is a LABELLED unknown, never a silent null.
                "recorded_zoning": zoning,
                "recorded_zoning_status": (
                    ZONING_STATUS_RECORDED if zoning is not None else ZONING_STATUS_UNKNOWN
                ),
                # Per-record provenance: the record's provenance reaches EVERY
                # base-lot record so an unknown zoning is still attributable.
                "provenance": dict(provenance),
            }
        )
    return records


def _any_zoning_unknown(base_lots: list[dict]) -> bool:
    """True when at least one base-lot record carries an UNKNOWN recorded zoning,
    so the document should name the concrete dependency for that gap."""
    return any(
        lot["recorded_zoning_status"] == ZONING_STATUS_UNKNOWN for lot in base_lots
    )


def _billing_status(*, is_condo: bool, entered_lot_class: str | None) -> str:
    """Label the billing lot's availability. A billing-class entry IS the billing
    lot (recorded); a condo UNIT-class (or unknown-class) entry resolves through a
    path that does not return the billing lot, so it is a genuine UNKNOWN; a
    non-condo input has no billing lot (not applicable). Never relabels an entered
    unit BBL as the billing lot."""
    if not is_condo:
        return BILLING_STATUS_NOT_APPLICABLE
    if entered_lot_class == LOT_CLASS_BILLING:
        return BILLING_STATUS_RECORDED
    return BILLING_STATUS_UNKNOWN


def _provenance(resolution: CondoResolution) -> dict:
    """Provenance of the transported records: the official source id, the
    dataset ids, the resolution retrieval timestamp, and one entry per SODA
    query the resolver actually performed (dataset id, request url, retrieved_at,
    record count, query kind, rows_updated_at) - the provenance-quintuple
    discipline, verbatim from the resolver. ``dataset_version`` surfaces the SODA
    ``rows_updated_at`` the source stamped (the dataset's own version) so the
    records display can name the version of city data it shows; it is honest
    ``None`` when the source omitted it, never fabricated."""
    queries = [dict(entry) for entry in resolution.provenance]
    return {
        "source_id": resolution.source_id or SOURCE_ID,
        "dataset_ids": list(resolution.dataset_ids),
        "retrieved_at": resolution.retrieved_at,
        "dataset_version": _dataset_version(resolution),
        "queries": queries,
    }


def _substitution_record(resolution: CondoResolution) -> dict | None:
    """The substrate record (G3-A4): only when the analysis SUBSTITUTED a single
    base lot for the entered billing/unit BBL. It names which BBL was entered and
    which the analysis runs on, so the substitution is an explicit record, never
    a silent swap. A multi-lot / unresolved / error outcome exposes NO single
    analyzed lot (None), so a consumer physically cannot present one as the
    answer."""
    if resolution.outcome != OUTCOME_RESOLVED_SINGLE or not resolution.resolved_base_bbl:
        return None
    return {
        "entered_bbl": resolution.input_bbl,
        "analyzed_bbl": resolution.resolved_base_bbl,
        "note": (
            "Analysis runs on the recorded base tax lot the city records for "
            "this condo. The entered billing lot and the analyzed base lot are "
            "recorded as entered versus analyzed; this substitution is a record, "
            "not a computed allowance."
        ),
    }


def _reason(resolution: CondoResolution) -> str | None:
    """A bounded human summary for the outcomes that carry no base-lot records,
    so the absence is honest and never blank. The success / multi-lot outcomes
    speak through their records and need no reason line."""
    if resolution.outcome == OUTCOME_UNRESOLVED:
        return (
            "This condo billing lot matched no recorded base tax lot and the "
            "resolver's fallbacks were exhausted. No base lot is fabricated."
        )
    if resolution.outcome == OUTCOME_ERROR:
        return (
            "The official condo records source reported a typed failure; the "
            "records view is withheld. This is safe to retry."
        )
    return None


def _build_document(
    canonical_bbl: str,
    resolution: CondoResolution,
    entered_lot_class: str | None,
) -> dict:
    """Build the condo-records document from a typed resolution. Every field is
    a RECORD; no value is computed and no allowance appears anywhere."""
    is_condo = resolution.outcome in (
        OUTCOME_RESOLVED_SINGLE,
        OUTCOME_MULTI_LOT,
        OUTCOME_UNRESOLVED,
        OUTCOME_ERROR,
    )
    # THREE distinct identifiers, never conflated (M5-T052):
    #   - ``entered_bbl``  : the canonical BBL the user entered (unit OR billing).
    #   - ``billing_bbl``  : the condo BILLING lot, with an EXPLICIT
    #     ``billing_bbl_status`` label. Known ONLY when the entered BBL is itself a
    #     billing-class BBL (7501-7599); a UNIT-class entry resolves through the
    #     unit path, which returns the base-lot set and the condo key but NOT the
    #     billing lot, so the billing lot is a LABELLED unknown for a unit input
    #     (status "unknown", value ``null``) - never the entered unit BBL
    #     relabelled as billing. A non-condo input has no billing lot (status
    #     "not_applicable").
    #   - each ``base_lots[].bbl`` : a recorded base tax lot (the analyzed lot on
    #     the allow path) - distinct from both of the above.
    base_lots = _base_lot_records(resolution)
    billing_status = _billing_status(is_condo=is_condo, entered_lot_class=entered_lot_class)
    billing_bbl = canonical_bbl if billing_status == BILLING_STATUS_RECORDED else None
    document: dict = {
        "document_kind": DOCUMENT_KIND,
        "bbl": canonical_bbl,
        # The BBL the user entered, verbatim, plus its lot class so the display
        # can never present a condo unit lot as the condo's billing lot.
        "entered_bbl": canonical_bbl,
        "entered_lot_class": entered_lot_class,
        "outcome": resolution.outcome,
        "billing_bbl": billing_bbl,
        "billing_bbl_status": billing_status,
        "base_lots": base_lots,
        "substitution": _substitution_record(resolution),
        "condo_key": resolution.condo_key,
        "condo_number": resolution.condo_number,
        "resolution_path": resolution.resolution_path,
        "provenance": _provenance(resolution),
        # The concrete dependency for the genuinely-unknown recorded zoning,
        # present only when at least one base lot carries an unknown zoning, so the
        # gap is explicit and attributable rather than silently deferred.
        "recorded_zoning_dependency": (
            RECORDED_ZONING_DEPENDENCY if _any_zoning_unknown(base_lots) else None
        ),
        # The permanent no-collapse boundary, carried on a multi-lot outcome so
        # the divergent-zoning legal question stays visible.
        "divergent_zoning_notice": (
            resolution.divergent_zoning_notice
            if resolution.outcome == OUTCOME_MULTI_LOT
            else None
        ),
        "notes": list(resolution.notes),
        "reason": _reason(resolution),
        "error_type": resolution.error_type,
    }
    return document


@router.get("/properties/{bbl}/condo-records", include_in_schema=False)
def get_condo_records(
    bbl: str,
    resolve_billing: CondoBillingResolver = Depends(get_condo_billing_resolver),  # noqa: B008
    resolve_unit: CondoUnitResolver = Depends(get_condo_unit_resolver),  # noqa: B008
    site_definition_store: SiteDefinitionStore = Depends(  # noqa: B008
        get_condo_site_definition_store
    ),
) -> JSONResponse:
    """Transport the condo records view for one BBL. Feature-flag gated OFF by
    default (reuses INTERNAL_RULE_EVAL_ENABLED), mirroring the sibling routes."""
    # Guard 1 (fail-safe disable): absent/unknown flag -> 404 with no hint the
    # feature exists. Checked FIRST, before a correlation id is minted.
    if not internal_rule_eval_enabled():
        return _not_found()

    correlation_id = uuid.uuid4().hex

    # 1. Validate the BBL BEFORE any resolver call (typed 422; zero network I/O).
    try:
        normalized = normalize_bbl(bbl)
    except BBLValidationError as exc:
        payload = exc.to_payload()  # raw_value is repr()-sanitized there
        logger.info(
            "condo_records_v1 validation_error code=%s correlation_id=%s",
            payload["code"], correlation_id,
        )
        return _json(
            422,
            {
                "state": "validation_error",
                "message": payload["message"],
                "correlation_id": correlation_id,
                "detail": {
                    "code": payload["code"],
                    "raw_value": _capped_raw_value(payload["raw_value"]),
                },
            },
            correlation_id,
        )

    canonical = normalized.canonical

    # 2. Resolve read-only through the injected seam. A UNIT-class BBL takes the
    #    resolver's unit path (G3-A3); everything else takes the accepted billing
    #    seam. A typed transport failure is a NORMAL ``error`` records document
    #    (the billing seam maps it; the unit path is mapped here), never a 5xx.
    try:
        lot_class = classify_lot(canonical)
    except BBLValidationError:
        # normalize_bbl already accepted the value; classify_lot is stricter only
        # on shape it cannot see here. Fall back to the billing seam, which
        # itself pass-throughs a non-condo input honestly.
        lot_class = None

    try:
        if lot_class == LOT_CLASS_UNIT:
            try:
                unit_result = resolve_unit(canonical, correlation_id)
            except DtmCondoConnectorError as exc:
                resolution = _error_resolution(canonical, correlation_id, exc)
            else:
                resolution = _resolution_from_unit_result(
                    canonical, correlation_id, unit_result
                )
        else:
            resolution = resolve_billing(canonical, correlation_id)
    except Exception:
        logger.error(
            "condo_records_v1 unexpected_error stage=resolve correlation_id=%s",
            correlation_id,
        )
        return _internal_error_500(correlation_id)

    # 3. Build the records document and guard its serialisation before send. The
    #    entered lot class (billing / unit / not-a-condo / None) is threaded in so
    #    the document keeps the entered BBL and the condo billing lot distinct.
    try:
        document = _build_document(canonical, resolution, lot_class)
        # M5-T059 (D-078): additive, READ-ONLY site-definition surfacing on the
        # multi-lot document only. Recorded confirmation(s) or an explicit
        # unconfirmed status; the assembly lives in the site_definition package.
        # Reading a confirmation never selects a site or changes any calculation.
        if resolution.outcome == OUTCOME_MULTI_LOT and resolution.condo_key is not None:
            document["site_definition"] = build_site_definition_block(
                condo_key=resolution.condo_key,
                views=site_definition_store.list_for_condo_key(resolution.condo_key),
                resolver_base_bbls=resolution.base_bbls,
            )
        _assert_json_safe(document)
    except Exception:
        logger.error(
            "condo_records_v1 serialization_unsafe correlation_id=%s", correlation_id
        )
        return _internal_error_500(correlation_id)

    return _json(200, document, correlation_id)
