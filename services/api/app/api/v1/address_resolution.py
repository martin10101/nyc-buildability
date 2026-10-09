"""GET /api/v1/address-resolution - internal address -> canonical address + BBL
(task M2-T022).

Serves the accepted M2-T021 Geoclient connector over the internal flag-gated
API: house number + street + (borough or zip) in, the connector's TYPED
resolution outcome out, plus the MVP_AGENDA C4 endpoint duties discharged in
the response itself. Posture mirrors the accepted internal routes exactly:

- Feature-flag gated OFF by default: reachable ONLY when the EXISTING
  ``INTERNAL_RULE_EVAL_ENABLED`` flag is an explicit true token. Address entry
  is the entry step of the same internal property flow that flag already
  gates, and ``app.config`` is out of this packet's scope, so NO new flag is
  added (the M5-T013 evidence-route precedent). Absent/empty/unknown -> a
  generic ``404 Not Found`` byte-indistinguishable from an unmounted path (no
  correlation header, no hint the feature exists). ``include_in_schema=False``
  so it never appears in OpenAPI.
- No authentication yet (service is internal/dev only, must not be public).

TRANSPORT, NEVER INTERPRET. The connector's typed outcome is transported
verbatim: a ``resolved`` outcome carries the canonical fields; ``ambiguous``
carries the source's suggestion list VERBATIM in source slot order and the
machine-readable ``selection_policy: "caller_selects"`` - this service NEVER
picks a suggestion (that is ultimately the user's decision); ``not_found`` /
``rejected`` / ``unrecognized_status`` are VISIBLE 200 outcomes carrying both
Geosupport return codes, reason codes and messages - never silence, never a
5xx for a legitimate geocoding result. Partial fields populated on a
non-resolved outcome transport exactly as the connector contract states
(consumers branch on ``status``, never on field presence).

SOURCE-FACT MAPPING (MVP_AGENDA C4 duty 1). A success-class outcome
(``resolved`` / ``resolved_with_warnings``) ADDITIONALLY emits its material
values as ``source_facts[]`` - records shaped exactly like
``packages/contracts/schemas/v1/source_fact.schema.json`` (consumed READ-ONLY;
the acceptance tests validate every emitted record against that schema, which
is the consumability proof the C4 carry-forward owes). Mapping rules:

- one fact per canonical field the source actually provided (``bbl``, ``bin``,
  normalized street, borough name, zip, latitude, longitude); an absent or
  type-drifted field emits NO fact - absence is never fabricated and a drifted
  value stays visible in ``raw_fields`` per the connector contract;
- ``original_value`` is the verbatim ``raw_fields`` value and
  ``normalized_value`` the connector's canonical field - equal by construction
  for this transport-never-interpret connector;
- ``confidence`` is 1.0 (deterministic official retrieval; never mapped to a
  coverage label), ``user_confirmed_or_overridden`` is ``"none"``,
  ``conflict_status`` is ``"none"`` (cross-source conflicts belong to the
  profile conflicts array), ``effective_date`` is ``null`` (Geoclient
  publishes none);
- ``dataset_version`` is ``"geoclient-v2; Geosupport release id not exposed by
  the /address response"`` - the honest, self-describing basis: the /address
  response carries no Geosupport/PAD release id (fixture G01 shows only
  geosupportFunctionCode/ReturnCode fields), so the interface version is
  recorded and the gap disclosed rather than a release id invented;
- facts are emitted ONLY when the resolved BBL passes the platform's canonical
  BBL validation (``app.connectors.bbl.normalize_bbl`` - validation only,
  never a rewrite); otherwise ``source_facts`` is empty and
  ``source_facts_not_emitted_reason`` says why (fail-safe: a malformed
  identifier is withheld, never shipped as a conformant-looking fact);
- lineage keys: ``fact_key`` (stable logical identity
  ``<source_id>:<bbl>:<field>``), ``observation_id`` (unique per retrieval
  event, ``<connector correlation id>:<field>``), ``value_digest``
  (canonical-json-1 digest of the verbatim original value) and
  ``response_digest`` (the connector's own whole-response digest, transported
  verbatim with its ``digest_canonicalization`` spec in ``provenance``).

UNSANITIZED REFLECTED INPUT (C4 duty 2). ``grc_message`` / ``grc2_message``,
``suggestions`` and the source-echoed canonical strings reflect caller-typed
text back (fixture G02's message quotes the typed street). The endpoint
transports them VERBATIM (JSON-encoded) and the response carries the
machine-readable ``unsanitized_reflected_input`` warning naming those fields;
consumers must escape on render. No reflected text reaches a log line or a
response header from this module.

NO REQUEST-DERIVED BUDGET (C4 duty 3). This endpoint passes NO
``AnalysisBudget`` to the connector at all, so no ``analysis_id`` can ever be
derived from untrusted request input, and ``request_budget_exceeded`` is
unreachable by construction; it is nonetheless a documented matrix pair
because the connector-error handler would emit it at the default 503 if a
budget were ever introduced (G1 LOW-1 correction).

RETRY-AFTER LOCAL GUARD (C4 known defect in the shared engine's
``sanitize_retry_after`` - still ``$``-anchored/uncapped there, fix scoped to
the wave-wide sanitizer packet): a ``rate_limited`` payload's ``retry_after``
is re-bounded HERE before it is surfaced - full-match against a conservative
charset with a hard length cap - and DROPPED (never echoed) when it fails.

KEY HYGIENE: the subscription key is read by the connector at call time from
the environment; this module never touches, stores, logs, or echoes it, and
the leak-absence pack drives every failure path with a sentinel key and
positive controls.

TWO CORRELATION IDS, both honest: the HTTP-level id minted here rides the
``X-Correlation-ID`` header and every log line of this module; the connector
mints its own id, which travels verbatim inside ``provenance`` (success) or
the error payload (failure). They are distinct by design - the connector owns
its provenance identity; this module owns the HTTP exchange's.

FAIL-CLOSED: the connector call, document assembly and final serialisation
each sit inside a guard, so no unhandled raise escapes as an untyped
text/plain 500; :func:`_assert_json_safe` runs both ``json.dumps`` forms
(they disagree about unpaired surrogates) before send.

``STATUS_STATE_MATRIX`` below is the single source of truth for every TYPED
(HTTP status, state) pair this endpoint can emit; the flag-off generic 404
deliberately sits outside the typed space. States equal the connector
taxonomy's ``error_type`` values verbatim.
"""

from __future__ import annotations

import json
import logging
import re
import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.config import internal_rule_eval_enabled
from app.connectors.bbl import BBLValidationError, normalize_bbl
from app.connectors.geoclient_address import (
    AddressResolution,
    GeoclientConnectorError,
    resolve_address,
)
from app.connectors.pluto_soda import canonical_json_digest

__all__ = [
    "ADDRESS_RESOLUTION_CONTRACT_VERSION",
    "STATUS_STATE_MATRIX",
    "AddressResolver",
    "get_address_resolver",
    "router",
]

logger = logging.getLogger("app.api.v1.address_resolution")

router = APIRouter(prefix="/api/v1", tags=["address-resolution"])

# Version of THIS endpoint's transport document. A route-local shape embedding
# connector-validated material verbatim, NOT a competing packages/contracts
# schema (the evidence-route precedent), so it is versioned here.
ADDRESS_RESOLUTION_CONTRACT_VERSION = "1.0.0"

# Honest dataset_version for every emitted source_fact (basis in the module
# docstring; asserted verbatim by the acceptance tests).
DATASET_VERSION = (
    "geoclient-v2; Geosupport release id not exposed by the /address response"
)

# ---------------------------------------------------------------------------
# EXACT (HTTP status, state) pair matrix - the single source of truth for every
# TYPED pair this endpoint can emit (the flag-off generic 404 deliberately sits
# OUTSIDE the typed space: it is byte-indistinguishable from an unmounted
# path). Every geocoding OUTCOME (resolved, resolved_with_warnings, ambiguous,
# not_found, rejected, unrecognized_status) is a 200 with the outcome in the
# body; non-200 states equal the connector taxonomy's error_type strings
# verbatim. request_budget_exceeded is UNREACHABLE BY CONSTRUCTION (this
# endpoint passes no budget - S8) but documented here because the
# connector-error handler WOULD emit it at the default 503 if a budget were
# ever introduced (G1 LOW-1: the prior comment wrongly claimed the generic
# internal_error guard would catch it).
# ---------------------------------------------------------------------------
STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # every typed geocoding outcome (visible in the body)
        (422, "invalid_input"),  # connector-typed input rejection, no network
        (503, "key_missing"),  # server-side key configuration gap, never the client
        (502, "auth_failed"),  # upstream rejected OUR key (payload key-free)
        (503, "rate_limited"),  # upstream throttling after the bounded retry budget
        (503, "source_unavailable"),  # upstream outage after the retry budget
        (504, "timeout"),  # upstream timeout after the retry budget
        (502, "malformed_response"),  # upstream 200 outside the documented shape
        (503, "request_budget_exceeded"),  # unreachable by construction (no budget)
        (500, "internal_error"),  # unexpected internal defect (fail-closed guard)
    }
)

_ERROR_STATUS: dict[str, int] = {
    "invalid_input": 422,
    "key_missing": 503,
    "auth_failed": 502,
    "rate_limited": 503,
    "source_unavailable": 503,
    "timeout": 504,
    "malformed_response": 502,
}
_DEFAULT_ERROR_STATUS = 503

# (canonical outcome attribute, Geoclient source field name) - the material
# fields a success-class outcome maps into source_facts. Source field names
# exactly as the source exposes them (source_fact.original_field_name rule).
_FACT_FIELDS: tuple[tuple[str, str], ...] = (
    ("bbl", "bbl"),
    ("bin", "buildingIdentificationNumber"),
    ("street_name_normalized", "firstStreetNameNormalized"),
    ("borough_name", "firstBoroughName"),
    ("zip_code", "zipCode"),
    ("latitude", "latitude"),
    ("longitude", "longitude"),
)

_FACT_STATUSES = frozenset({"resolved", "resolved_with_warnings"})

# C4 duty 2: the response names its own unsanitized surfaces — EVERY one of
# them (G3 rework: input_echo, the most direct caller-input reflection, and
# the street/borough source_fact values were missing from this contract; a
# consumer escaping exactly this list would have shipped input_echo raw).
_REFLECTED_INPUT_WARNING = {
    "fields": [
        "input_echo",
        "grc_message",
        "grc2_message",
        "suggestions",
        "canonical.street_name_normalized",
        "canonical.borough_name",
        "provenance.request_params",
        "source_facts[].original_value (street/borough facts)",
        "source_facts[].normalized_value (street/borough facts)",
    ],
    "warning": (
        "UNSANITIZED source text that reflects caller-typed input back "
        "(the source echoes the typed street in its messages and "
        "suggestions). Transported verbatim by design; every consumer must "
        "escape on render and must never log these values verbatim."
    ),
}

# Local Retry-After guard (module docstring): conservative charset, hard cap,
# fullmatch so a trailing newline can never ride through.
_RETRY_AFTER_MAX_CHARS = 32
_RETRY_AFTER_SAFE_RE = re.compile(r"[0-9A-Za-z ,:\-]{1,32}")

# Resolver contract: keyword-call onto app.connectors.geoclient_address.
# resolve_address. Injected through FastAPI dependency_overrides so tests run
# offline on an injected transport while production uses the connector's own
# call-time environment read unchanged.
AddressResolver = object  # documentation alias; the seam is duck-typed below


def _default_resolver(
    house_number: str,
    street: str,
    *,
    borough: str | None = None,
    zip_code: str | None = None,
) -> AddressResolution:
    """Production resolver: signature matches the ROUTE's call contract exactly
    (positional house_number/street + keyword borough/zip_code — the G1 HIGH-1
    rework; the prior **kwargs-only form rejected the route's positional call
    and 500'd every real request, masked by positional-accepting test fakes).
    NO budget kwarg, ever (C4 duty 3); NO transport override in production —
    the connector resolves its default transport and env key at call time."""
    return resolve_address(
        house_number, street, borough=borough, zip_code=zip_code
    )


def get_address_resolver():
    """Dependency returning the address resolver (override point for tests)."""
    return _default_resolver


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


def _assert_json_safe(document: dict) -> None:
    """Both serialisation forms must succeed before send (they disagree about
    unpaired surrogates and NaN; the renderer uses the second form)."""
    json.dumps(document, allow_nan=False)
    json.dumps(document, ensure_ascii=False, allow_nan=False).encode("utf-8")


def _bounded_retry_after(detail: object) -> str | None:
    """The ONLY detail value this endpoint re-bounds locally: retry_after is
    upstream header text whose shared sanitizer is a known C4 defect, so it is
    full-matched against a conservative charset with a hard cap and DROPPED
    (never echoed, never truncated-and-shipped) on any failure."""
    if not isinstance(detail, dict):
        return None
    value = detail.get("retry_after")
    if not isinstance(value, str) or len(value) > _RETRY_AFTER_MAX_CHARS:
        return None
    if _RETRY_AFTER_SAFE_RE.fullmatch(value) is None:
        return None
    return value


def _source_facts(outcome: AddressResolution) -> tuple[list[dict], str | None]:
    """Map a success-class outcome onto source_fact-shaped records.

    Returns ``(facts, not_emitted_reason)``. A non-success status returns
    ``([], None)`` - no material fact exists to record. A success outcome
    whose BBL is absent or fails canonical validation returns ``([], reason)``:
    withheld and SAID SO, never shipped malformed (fail-safe)."""
    if outcome.status not in _FACT_STATUSES:
        return [], None
    if outcome.bbl is None:
        return [], (
            "success-class outcome carried no bbl; source facts require a "
            "BBL applicability and are withheld rather than fabricated"
        )
    try:
        # Validation only, and the CANONICAL string (normalize_bbl returns a
        # NormalizedBBL record; the fact carries the plain canonical form).
        fact_bbl = normalize_bbl(outcome.bbl).canonical
    except BBLValidationError:
        return [], (
            "resolved bbl failed canonical BBL validation; source facts are "
            "withheld rather than shipped malformed (the verbatim value "
            "remains in raw_fields)"
        )

    connector_correlation = outcome.provenance.get("correlation_id")
    retrieved_at = outcome.provenance.get("retrieved_at")
    response_digest = outcome.provenance.get("response_digest")

    facts: list[dict] = []
    for attribute, source_field in _FACT_FIELDS:
        normalized = getattr(outcome, attribute)
        if normalized is None:
            # Absent or type-drifted at the source: no fact is fabricated; a
            # drifted value stays visible in raw_fields per the connector
            # contract ("omitted OR drifted" - consumers consult raw_fields).
            continue
        original = outcome.raw_fields.get(source_field)
        fact = {
            "provenance_id": f"geoclient-address:{connector_correlation}:{source_field}",
            "source_id": outcome.provenance.get("source_id"),
            "original_field_name": source_field,
            "original_value": original,
            "normalized_value": normalized,
            "retrieved_at": retrieved_at,
            "dataset_version": DATASET_VERSION,
            "effective_date": None,
            "bbl": fact_bbl,
            "confidence": 1.0,
            "user_confirmed_or_overridden": "none",
            "conflict_status": "none",
            "fact_key": f"{outcome.provenance.get('source_id')}:{fact_bbl}:{source_field}",
            "observation_id": f"{connector_correlation}:{source_field}",
            "value_digest": canonical_json_digest(original),
        }
        if isinstance(response_digest, str):
            fact["response_digest"] = response_digest
        facts.append(fact)
    return facts, None


def _success_document(outcome: AddressResolution, correlation_id: str) -> dict:
    facts, not_emitted_reason = _source_facts(outcome)
    document: dict = {
        "contract_version": ADDRESS_RESOLUTION_CONTRACT_VERSION,
        "document_kind": "address_resolution",
        "correlation_id": correlation_id,
        "status": outcome.status,
        "grc": outcome.grc,
        "grc_reason": outcome.grc_reason,
        "grc_message": outcome.grc_message,
        "grc2": outcome.grc2,
        "grc2_reason": outcome.grc2_reason,
        "grc2_message": outcome.grc2_message,
        "input_echo": {
            "house_number": outcome.house_number_in,
            "street": outcome.street_in,
            "borough": outcome.borough_in,
            "zip": outcome.zip_in,
        },
        "canonical": {
            "bbl": outcome.bbl,
            "bin": outcome.bin,
            "street_name_normalized": outcome.street_name_normalized,
            "borough_name": outcome.borough_name,
            "zip_code": outcome.zip_code,
            "latitude": outcome.latitude,
            "longitude": outcome.longitude,
        },
        # VERBATIM, source slot order; selection is ALWAYS the caller's
        # (ultimately the user's) decision - never made by this service.
        "suggestions": outcome.suggestions,
        "selection_policy": "caller_selects",
        "unsanitized_reflected_input": _REFLECTED_INPUT_WARNING,
        "source_facts": facts,
        # Connector provenance VERBATIM (key-free by the connector's own
        # gated contract): source id, endpoint, request params, retrieval
        # timestamp, both GRCs, response digest + canonicalization spec, and
        # the CONNECTOR's own correlation id (distinct from the HTTP one).
        "provenance": outcome.provenance,
    }
    if not_emitted_reason is not None:
        document["source_facts_not_emitted_reason"] = not_emitted_reason
    return document


@router.get("/address-resolution", include_in_schema=False)
def get_address_resolution(
    house_number: str = Query(default=""),
    street: str = Query(default=""),
    borough: str | None = Query(default=None),
    zip_code: str | None = Query(default=None, alias="zip"),
    resolver=Depends(get_address_resolver),  # noqa: B008 (house DI idiom)
) -> JSONResponse:
    """Resolve an address through the Geoclient connector, transporting the
    typed outcome honestly. Input validation is the CONNECTOR's (typed,
    value-free, pre-network) so there is exactly one validation authority;
    the params are accepted as plain strings deliberately."""
    # Flag check FIRST - before a correlation id is minted or input is touched.
    if not internal_rule_eval_enabled():
        return _not_found()

    correlation_id = uuid.uuid4().hex

    try:
        outcome = resolver(
            house_number,
            street,
            borough=borough if borough else None,
            zip_code=zip_code if zip_code else None,
        )
    except GeoclientConnectorError as exc:
        payload = exc.to_payload()  # typed, bounded, key-free per the connector's gates
        state: str = payload["error_type"]  # always present on the typed taxonomy
        status_code = _ERROR_STATUS.get(state, _DEFAULT_ERROR_STATUS)
        body = {
            "contract_version": ADDRESS_RESOLUTION_CONTRACT_VERSION,
            "document_kind": "address_resolution_error",
            "state": state,
            "correlation_id": correlation_id,
            "error": {
                "error_type": state,
                "message": payload.get("message"),
                "connector_correlation_id": payload.get("correlation_id"),
                "source_id": payload.get("source_id"),
                "endpoint": payload.get("endpoint"),
            },
        }
        retry_after = _bounded_retry_after(payload.get("detail"))
        if retry_after is not None:
            body["error"]["retry_after"] = retry_after
        logger.info(
            "address_resolution_v1 error state=%s correlation_id=%s "
            "connector_correlation_id=%s",
            state,
            correlation_id,
            payload.get("correlation_id"),
        )
        try:
            _assert_json_safe(body)
        except (TypeError, ValueError):
            return _internal_error(correlation_id)
        return _json(status_code, body, correlation_id)
    except Exception:
        # Fail-closed: never an untyped escape. Type name only - no exception
        # text (it could echo body or reflected content into a log line).
        logger.error(
            "address_resolution_v1 internal_error correlation_id=%s", correlation_id
        )
        return _internal_error(correlation_id)

    try:
        document = _success_document(outcome, correlation_id)
        _assert_json_safe(document)
    except Exception:
        logger.error(
            "address_resolution_v1 internal_error stage=assembly correlation_id=%s",
            correlation_id,
        )
        return _internal_error(correlation_id)

    logger.info(
        "address_resolution_v1 outcome status=%s correlation_id=%s "
        "connector_correlation_id=%s source_facts=%d",
        outcome.status,
        correlation_id,
        outcome.provenance.get("correlation_id"),
        len(document["source_facts"]),
    )
    return _json(200, document, correlation_id)


def _internal_error(correlation_id: str) -> JSONResponse:
    return _json(
        500,
        {
            "contract_version": ADDRESS_RESOLUTION_CONTRACT_VERSION,
            "document_kind": "address_resolution_error",
            "state": "internal_error",
            "correlation_id": correlation_id,
            "error": {
                "error_type": "internal_error",
                "message": "internal error assembling the address-resolution response",
            },
        },
        correlation_id,
    )
