"""GET /api/v1/properties/{bbl}/study - internal read of a study SETUP (lane C,
request D-1 slice 1).

Transports the lot-choice + site-facts SETUP half of a study for one confirmed
BBL, shaped to ``packages/contracts/schemas/v1/study.schema.json``:

- ``property`` (bbl + confirmed address, null when reached by BBL only);
- ``lots`` and ``lot_selection`` - VERBATIM from B-07's study adapters
  (``app.spatial.multi_lot_site.study_lots`` / ``study_lot_selection``) for the
  default "use all" selection, so the combination status and its plain-English
  reason, and the exact statement "Based on the lots you selected - the app does
  not verify the zoning lot", are B-07's words, never re-derived here;
- ``site.facts`` - B-02/B-03 ``site_fact`` v1 documents with their measurement
  rank, label and source, carried verbatim.

It is NOT a full study.schema.json Study: a study also requires options (program,
floor-to-floor heights, goal), and the plan forbids the backend inventing those
(``docs/PRODUCT_PLAN_CURRENT_2026-09-28.md`` M1-06 "no example data in real
work"; the study store "never invents option inputs ... they come from the
caller"). Options are chosen later in the flow; the web adapter composes the full
Study by adding the architect's option to this setup (request D-1 slice 1 item 2).
``document_kind`` is ``study_setup`` so the shape is explicit.

Route posture mirrors the accepted flag-gated internal reads
(``app.api.v1.condo_records`` / ``app.api.v1.rule_evaluation``):

- A NEW default-off flag ``INTERNAL_STUDY_READ_ENABLED`` (``app.config``). The
  route is ALWAYS registered but, when the flag is absent/empty/unknown, returns
  a generic ``404 Not Found`` byte-indistinguishable from an unmounted path.
  ``include_in_schema=False`` so it never appears in OpenAPI. The flag gates
  REACHABILITY; the lot choice itself is Lane B behaviour and is produced only
  when LANE_B_ENABLED is also on (``app.api.v1.study_inputs``), so production
  (neither flag set) keeps the route a 404.
- No authentication yet (service is internal/dev only). Because the default
  provider now reaches LIVE PLUTO, a per-caller rate limit (NB1) runs right
  after the flag check, BEFORE any validation or upstream work, returning a
  typed ``429`` so one unauthenticated GET cannot drive unbounded live SODA
  calls. The real per-caller isolation is the authenticated principal (B-001),
  which is why this route family stays effectively dev-only until auth lands.
- The BBL flows through ``normalize_bbl`` BEFORE any provider call, so a
  malformed BBL is a typed ``422`` with zero I/O. An optional ``selected`` lot
  re-pick (a repeatable query of canonical BBLs) is validated for SHAPE the same
  way (typed ``422`` before any I/O) and passed VERBATIM to B-07's derive; a
  re-pick B-07 rejects (a BBL not in this property's lot choice) is a typed
  ``422`` too. The route never computes geometry or adjacency itself.
- The study inputs come through an INJECTED provider (``get_study_inputs_provider``)
  so the tests run fully offline on recorded fixtures (the 215-16 Northern pack).
  The DEFAULT provider binds the resilient PLUTO fetcher the properties route
  uses (``app.resilience.fetcher.build_default_resilient_fetcher``); live city
  data is reached ONLY through that existing connector behind the seam. Every
  upstream failure (and a no-match, including a condo unit-lot) maps to the typed
  ``503``; nothing is ever fabricated.

ZONING MATH STAYS OFF (plan / lane rule). This route carries NO allowance,
capacity, FAR or rule output: a study setup holds the user's lot selection plus
B-07's combination check and the sourced site facts, nothing computed.

CONTRACT-GUARDED BEFORE SEND. Every emitted site fact is validated against
``site_fact.schema.json`` and every lot / the lot_selection against the
``study.schema.json`` ``$defs`` before the 200 is returned; a built document that
fails is a ``500 internal_contract_error`` (an invalid 200 is impossible, the
properties-route posture). ``STUDY_READ_STATUS_STATE_MATRIX`` is the single
source of truth for every emitted (HTTP status, state) pair.
"""

from __future__ import annotations

import json
import logging
import uuid
from functools import lru_cache
from importlib import resources

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from app.config import internal_study_read_enabled
from app.connectors.bbl import BBLValidationError, normalize_bbl
from app.contracts.study_contracts import StudyContractError, validate_site_fact_document
from app.resilience.rate_limit import SlidingWindowRateLimiter, caller_key
from app.spatial.multi_lot_site import LotSelectionError
from app.spatial.multi_lot_site.parameters import MAX_SELECTED_LOTS

from .study_inputs import (
    StudyInputsProvider,
    StudyInputsUnavailableError,
    default_study_inputs_provider,
)
from .study_setup_document import build_study_setup_document

# Compatibility facade (M5-T138): the study-setup builder moved to study_setup_document so the
# results route can reuse it (no fork; modularity law). study_read's behaviour is unchanged - it
# calls the shared builder - and this alias preserves the former private import path that an
# existing contract test uses, so that test stays green with no edit to its expectations.
_build_document = build_study_setup_document

__all__ = [
    "RATE_LIMIT_MAX_KEYS",
    "RATE_LIMIT_MAX_REQUESTS",
    "RATE_LIMIT_WINDOW_SECONDS",
    "STUDY_READ_STATUS_STATE_MATRIX",
    "get_rate_limiter",
    "get_study_inputs_provider",
    "router",
]

logger = logging.getLogger("app.api.v1.study_read")

router = APIRouter(prefix="/api/v1", tags=["study_read"])

# Defense-in-depth length cap for the reflected raw_value repr in a 422 detail
# (the condo-records / proposal bounded-repr class). The repr is already
# repr()-sanitized in app.connectors.bbl; this only bounds its LENGTH.
MAX_RAW_VALUE_REPR_CHARS = 256
_RAW_VALUE_TRUNCATION_MARKER = "...[truncated]"

# Server-side length cap on every 422 ``message`` (security review NB3). The
# sibling routes only capped detail.raw_value; this caps the message too so no
# 422 body can grow unbounded with reflected (even if already sanitized) text.
MAX_MESSAGE_CHARS = 256

# Per-caller sliding-window rate limit for THIS route (NB1): one unauthenticated
# GET on the LIVE default provider now drives a live SODA call, so the route
# needs a bound BEFORE any upstream work. The SAME reviewed primitive the D-087
# routes use (app.resilience.rate_limit.SlidingWindowRateLimiter), keyed by
# caller_key (authenticated principal when present, else client host; see that
# module for the proxy-collapse limit that keeps this route UNMOUNTED until
# B-001 auth lands). State is per-route and process-wide; tests reset/tighten it
# through get_rate_limiter(). Values mirror the export sibling (30 / 60 s).
RATE_LIMIT_MAX_REQUESTS = 30
RATE_LIMIT_WINDOW_SECONDS = 60.0
RATE_LIMIT_MAX_KEYS = 8192
_RATE_LIMITER = SlidingWindowRateLimiter(
    max_requests=RATE_LIMIT_MAX_REQUESTS,
    window_seconds=RATE_LIMIT_WINDOW_SECONDS,
    max_keys=RATE_LIMIT_MAX_KEYS,
)


def get_rate_limiter() -> SlidingWindowRateLimiter:
    """The shared, bounded per-caller limiter for this route. Tests reset/tighten
    it via this getter; it is NOT a client-controlled input."""
    return _RATE_LIMITER

# Bundled canonical schemas (byte-identical to packages/contracts/schemas/v1,
# kept so by services/api/scripts/sync_contract_schemas.py). Loaded read-only via
# importlib.resources, the same package-data path app.contracts.study_contracts
# uses, so it works from a non-editable install with no packages/ sibling.
_SCHEMA_PACKAGE = "app._contract_schemas.v1"
_STUDY_SCHEMA_ID = (
    "https://github.com/martin10101/nyc-buildability/packages/contracts/schemas/v1/"
    "study.schema.json"
)

# ---------------------------------------------------------------------------
# EXACT (HTTP status, state) pair matrix. Every success is a 200 with NO
# ``state`` field (the document speaks for itself); the disabled sentinel is a
# 404 with NO state (byte-identical to an unmounted path). A malformed BBL is a
# typed 422; a per-caller rate-limit refusal is a typed 429; inputs that cannot
# be produced (upstream unavailable/no-match, the Lane B gate off) are a bounded
# 503; an unexpected defect is a generic 500; a built document that fails its
# contract before send is a typed 500 (an invalid 200 is impossible).
# ---------------------------------------------------------------------------
STUDY_READ_STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # study-setup document
        (404, None),  # flag off / unmounted-path sentinel (generic Not Found)
        (422, "validation_error"),  # malformed BBL OR an invalid lot re-pick
        (429, "rate_limited"),  # per-caller rate limit exceeded (NB1)
        (503, "inputs_unavailable"),  # inputs could not be produced (fail safe)
        (500, "internal_error"),  # unexpected internal defect (generic)
        (500, "internal_contract_error"),  # built document failed its contract
    }
)


def get_study_inputs_provider() -> StudyInputsProvider:
    """Dependency returning the study-inputs provider (test override point).

    The default is the LIVE PLUTO path through the resilient fetcher the
    properties route uses (NB1); tests inject a fixture-backed provider so the
    whole suite runs offline."""
    return default_study_inputs_provider


@lru_cache(maxsize=1)
def _study_defs_registry():
    """A referencing registry over the bundled study + site_fact + common schemas,
    so a study.schema.json ``$defs`` subschema resolves its $refs."""
    from referencing import Registry, Resource

    names = ("study.schema.json", "site_fact.schema.json", "common.schema.json")
    docs = [
        json.loads(resources.files(_SCHEMA_PACKAGE).joinpath(name).read_text(encoding="utf-8"))
        for name in names
    ]
    return Registry().with_resources(
        [(doc["$id"], Resource.from_contents(doc)) for doc in docs]
    )


@lru_cache(maxsize=4)
def _study_defs_validator(ref: str):
    """A Draft 2020-12 validator for one study.schema.json ``$defs`` entry
    (e.g. ``"#/$defs/lot"``), built once from the bundle."""
    import jsonschema

    return jsonschema.Draft202012Validator(
        {"$ref": _STUDY_SCHEMA_ID + ref}, registry=_study_defs_registry()
    )


def _json(status_code: int, body: dict, correlation_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=body,
        headers={"X-Correlation-ID": correlation_id},
    )


def _not_found() -> JSONResponse:
    """Generic 404 identical to FastAPI's default for an unmounted path. No
    correlation id and no body hint, so a disabled feature is indistinguishable
    from a route that does not exist (fail-safe disable)."""
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


def _capped_raw_value(raw_value_repr: str) -> str:
    if len(raw_value_repr) <= MAX_RAW_VALUE_REPR_CHARS:
        return raw_value_repr
    return raw_value_repr[:MAX_RAW_VALUE_REPR_CHARS] + _RAW_VALUE_TRUNCATION_MARKER


def _capped_message(message: str) -> str:
    """Length-cap a 422 ``message`` server-side (security review NB3)."""
    if len(message) <= MAX_MESSAGE_CHARS:
        return message
    return message[:MAX_MESSAGE_CHARS] + _RAW_VALUE_TRUNCATION_MARKER


class _SelectedInvalid(Exception):
    """A ``selected`` re-pick is malformed in SHAPE (empty, duplicated or over the
    lot cap). Carries a bounded ``code`` + ``message`` for a typed 422; raised
    BEFORE any I/O. A selected BBL that is syntactically invalid surfaces as the
    connector's :class:`BBLValidationError` instead (reusing the path-BBL shape)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _validate_selected(selected: list[str] | None) -> list[str] | None:
    """Validate the optional ``selected`` re-pick query to CANONICAL BBLs, BEFORE
    any I/O (the typed-422 contract). None is the default "use all". Checks the
    SHAPE only - syntactic BBLs (reusing ``normalize_bbl``), no duplicates, and at
    most ``MAX_SELECTED_LOTS`` lots; whether each BBL is actually in THIS
    property's lot choice is B-07's call and is checked downstream (post-fetch),
    surfaced verbatim as a typed 422. No geometry or adjacency is computed here.

    Raises:
        BBLValidationError: a selected entry is not a syntactically valid BBL.
        _SelectedInvalid: the selection is empty, duplicated, or over the cap.
    """
    if selected is None:
        return None
    if not selected:
        raise _SelectedInvalid("empty_selection", "select at least one lot")
    canonical = [normalize_bbl(entry).canonical for entry in selected]
    if len(set(canonical)) != len(canonical):
        raise _SelectedInvalid("duplicate_selection", "a lot is selected more than once")
    if len(canonical) > MAX_SELECTED_LOTS:
        raise _SelectedInvalid(
            "too_many_lots", f"at most {MAX_SELECTED_LOTS} lots may be selected"
        )
    return canonical


def _validation_error_422(
    correlation_id: str, *, code: str, message: str, raw_value: str | None = None
) -> JSONResponse:
    """A typed ``(422, validation_error)`` with a bounded message (NB3). ``detail``
    always carries the bounded ``code``; ``raw_value`` is included (capped) only
    when the source error reflected one (a malformed BBL)."""
    detail: dict[str, object] = {"code": code}
    if raw_value is not None:
        detail["raw_value"] = _capped_raw_value(raw_value)
    return _json(
        422,
        {
            "state": "validation_error",
            "message": _capped_message(message),
            "correlation_id": correlation_id,
            "detail": detail,
        },
        correlation_id,
    )


def _rate_limited_429(correlation_id: str) -> JSONResponse:
    """A typed ``(429, rate_limited)`` consistent with the sibling routes: a
    server-minted correlation id, a bounded message, no caller text."""
    return _json(
        429,
        {
            "state": "rate_limited",
            "message": "per-caller rate limit exceeded; retry later",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _internal_error_500(correlation_id: str) -> JSONResponse:
    """Documented generic 500 for ANY unexpected exception. Logs the type +
    correlation id only (no str(exc)/traceback: the chain may embed untrusted
    upstream strings)."""
    return _json(
        500,
        {
            "state": "internal_error",
            "message": "unexpected internal error; see server logs by correlation id",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _internal_contract_error_500(correlation_id: str) -> JSONResponse:
    """A built study-setup document failed its contract before send. An invalid
    200 is impossible; the defect is internal, so the body is generic."""
    return _json(
        500,
        {
            "state": "internal_contract_error",
            "message": (
                "the study setup failed its contract checks before send and was not "
                "delivered; see server logs by correlation id"
            ),
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _inputs_unavailable_503(correlation_id: str) -> JSONResponse:
    """The study inputs could not be produced (upstream unavailable, the Lane B
    gate off, or the live fetch shell not wired yet). Fail safe: no study is
    fabricated. The ``reason`` is a bounded platform token, never upstream text."""
    return _json(
        503,
        {
            "state": "inputs_unavailable",
            "message": (
                "the study setup is not available for this property right now; nothing "
                "was fabricated and this is safe to retry"
            ),
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _assert_json_safe(document: dict) -> None:
    """Both JSON renderings the stack could use MUST succeed before send:
    ``allow_nan=False`` rejects NaN/Infinity, and the ``ensure_ascii=False``
    utf-8 form is what Starlette renders and raises on an unpaired surrogate."""
    json.dumps(document, allow_nan=False)
    json.dumps(document, ensure_ascii=False, allow_nan=False).encode("utf-8")


def _contract_guard(document: dict) -> None:
    """Validate the study-setup document against the contract before send. Every
    site fact against site_fact.schema.json; every lot and the lot_selection
    against the study.schema.json $defs. Raises StudyContractError on any defect
    so an invalid 200 is impossible."""
    for fact in document["site"]["facts"]:
        validate_site_fact_document(fact)
    for index, lot in enumerate(document["lots"]):
        errors = sorted(
            _study_defs_validator("#/$defs/lot").iter_errors(lot),
            key=lambda err: list(err.path),
        )
        if errors:
            raise StudyContractError(
                f"lot {index} failed the study contract: {errors[0].message}",
                contract="study",
                location=f"lots/{index}",
            )
    # lot_selection is defined INLINE under properties (study.schema.json has no
    # $defs/lot_selection), so the ref points at the property subschema; its own
    # $ref to $defs/combination still resolves in the registry.
    sel_errors = sorted(
        _study_defs_validator("#/properties/lot_selection").iter_errors(
            document["lot_selection"]
        ),
        key=lambda err: list(err.path),
    )
    if sel_errors:
        raise StudyContractError(
            f"lot_selection failed the study contract: {sel_errors[0].message}",
            contract="study",
            location="lot_selection",
        )


@router.get("/properties/{bbl}/study", include_in_schema=False)
def get_study(
    request: Request,
    bbl: str,
    selected: list[str] | None = Query(default=None),  # noqa: B008
    provide_inputs: StudyInputsProvider = Depends(get_study_inputs_provider),  # noqa: B008
) -> JSONResponse:
    """Read the study setup (lot choice + site facts) for one BBL. Feature-flag
    gated OFF by default (INTERNAL_STUDY_READ_ENABLED), mirroring the sibling
    internal reads. ``selected`` is an optional lot re-pick (repeatable query of
    canonical BBLs) passed VERBATIM to B-07's derive; omitted means "use all"."""
    # Guard 1 (fail-safe disable): absent/unknown flag -> 404 with no hint the
    # feature exists. Checked FIRST, before a correlation id is minted (the
    # flag-off 404 is byte-identical to an unmounted path and is unchanged by
    # the rate limit / re-pick below).
    if not internal_study_read_enabled():
        return _not_found()

    correlation_id = uuid.uuid4().hex

    # Guard 2 (NB1): per-caller rate limit BEFORE any validation or upstream
    # work, so one unauthenticated GET that would now drive a LIVE SODA call is
    # bounded. Keyed by caller_key (principal when present, else host). A typed
    # 429, consistent with the sibling routes.
    if not get_rate_limiter().allow(caller_key(request)):
        logger.info("study_read_v1 rate_limited correlation_id=%s", correlation_id)
        return _rate_limited_429(correlation_id)

    # 1. Validate the BBL BEFORE any provider call (typed 422; zero I/O).
    try:
        normalized = normalize_bbl(bbl)
    except BBLValidationError as exc:
        payload = exc.to_payload()  # raw_value is repr()-sanitized there
        logger.info(
            "study_read_v1 validation_error code=%s correlation_id=%s",
            payload["code"], correlation_id,
        )
        return _validation_error_422(
            correlation_id,
            code=payload["code"],
            message=payload["message"],
            raw_value=payload["raw_value"],
        )

    canonical = normalized.canonical

    # 1b. Validate the optional re-pick BEFORE any provider call (typed 422; zero
    #     I/O). Shape only: whether each BBL is in THIS property's lot choice is
    #     B-07's call, checked post-fetch (step 2).
    try:
        selected_bbls = _validate_selected(selected)
    except BBLValidationError as exc:
        payload = exc.to_payload()
        logger.info(
            "study_read_v1 validation_error stage=selected code=%s correlation_id=%s",
            payload["code"], correlation_id,
        )
        return _validation_error_422(
            correlation_id,
            code=payload["code"],
            message=payload["message"],
            raw_value=payload["raw_value"],
        )
    except _SelectedInvalid as exc:
        logger.info(
            "study_read_v1 validation_error stage=selected code=%s correlation_id=%s",
            exc.code, correlation_id,
        )
        return _validation_error_422(correlation_id, code=exc.code, message=exc.message)

    # 2. Produce the inputs through the injected provider. A typed unavailability
    #    is a bounded 503 (fail safe, nothing fabricated); a lot re-pick B-07
    #    rejects (a BBL not in this property's lot choice) is a typed 422; any
    #    other exception is a generic 500. ``selected`` is passed ONLY on a
    #    re-pick, so a default "use all" provider keeps its two-argument shape.
    try:
        if selected_bbls is None:
            inputs = provide_inputs(canonical, correlation_id)
        else:
            inputs = provide_inputs(canonical, correlation_id, selected=selected_bbls)
    except StudyInputsUnavailableError as exc:
        logger.info(
            "study_read_v1 inputs_unavailable reason=%s correlation_id=%s",
            exc.reason, correlation_id,
        )
        return _inputs_unavailable_503(correlation_id)
    except LotSelectionError:
        # B-07 rejected the selection (e.g. a BBL not in this property's lot
        # choice). A client re-pick error, not a 503/500. Fixed, bounded message:
        # the caller's BBLs are not echoed (they are logged only by classifier).
        logger.info(
            "study_read_v1 validation_error stage=re_pick correlation_id=%s",
            correlation_id,
        )
        return _validation_error_422(
            correlation_id,
            code="invalid_lot_selection",
            message="the selected lots are not a valid selection for this property",
        )
    except Exception:
        logger.error(
            "study_read_v1 unexpected_error stage=provide correlation_id=%s",
            correlation_id,
        )
        return _internal_error_500(correlation_id)

    # 3. Shape the document, contract-guard it, and guard its serialisation
    #    before send. A built document that fails the contract is a typed 500.
    try:
        document = build_study_setup_document(canonical, inputs)
        _contract_guard(document)
        _assert_json_safe(document)
    except StudyContractError:
        logger.error(
            "study_read_v1 contract_invalid correlation_id=%s", correlation_id
        )
        return _internal_contract_error_500(correlation_id)
    except Exception:
        logger.error(
            "study_read_v1 serialization_unsafe correlation_id=%s", correlation_id
        )
        return _internal_error_500(correlation_id)

    return _json(200, document, correlation_id)
