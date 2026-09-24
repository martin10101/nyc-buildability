"""POST /api/v1/max-envelope - deterministic maximum-buildable-envelope route (M5-T064, D-082).

The internal, flag-gated HTTP seam onto the accepted max-envelope engine
(:func:`app.scenario.max_envelope.derive_max_envelope`). Given a caller-supplied lot context
and lot rule facts, it derives the maximum buildable envelope for the rectangle-prism massing
class - the binding value + provenance per dimension, honest gaps, and a candidate
``proposed_massing`` draft the engine has already proven consistent against the accepted checker
- and returns it. It stores nothing and emits NO scenario document and NO contract version.

THIS ROUTE SHIPS UNMOUNTED. ``app/main.py`` is held by the live M5-T062 lane; the ``include_router``
line rides a later orchestrator seam. Tests mount the router on a fresh ``FastAPI()`` via
``TestClient`` (the accepted M5-T059 pattern) and assert it is ABSENT from the app's OpenAPI.

Route discipline MIRRORS the accepted sibling ``/api/v1/proposal-checks`` route, reusing its
accepted boundary primitives rather than forking them:

* Posture - feature-flag gated OFF by default (REUSED ``INTERNAL_RULE_EVAL_ENABLED``, the same
  flag class the sibling internal routes use; ``include_in_schema=False``; absent/empty/unknown
  flag -> a generic 404 byte-indistinguishable from an unmounted path). A bounded request body
  (raw-byte ceiling by BOUNDED STREAMING, reusing the accepted T053 primitives). No auth change:
  authn / tenancy / per-user ownership of the supplied lot geometry arrive with the PUBLIC
  exposure packet, recorded here as a disposition, not implemented (the route is unreachable
  without the internal flag).
* Boundary - ``label`` is length-capped and charset-restricted (BP-2); the mapped
  ``lot_rule_facts`` are validated against the evaluator's OWN declared vocabulary (types, then
  registry-derived enum/numeric bounds) before anything is fed (BP-5); the lot object's ids and
  republished provenance objects are bounded by the accepted ``_build_lot_context``; the
  lot-line / street-line counts are route-capped (BP-4). Every error path length-caps any embedded
  value (BP-3) and every non-disabled response carries ``X-Correlation-ID``.
* The engine is the single entry, called once, off the event loop (``run_in_threadpool``); it runs
  the accepted checker on its own candidate, so a generator-checker inconsistency fails closed
  (500) rather than shipping a maximum the checker refuses.

The emitted (HTTP status, state) pairs are the single source of truth
:data:`MAX_ENVELOPE_STATUS_STATE_MATRIX`; the 200 envelope carries NO ``state`` (pair
``(200, None)``), mirroring the accepted sibling routes.
"""

from __future__ import annotations

import functools
import json
import logging
import uuid
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

# Reuse the accepted sibling route's caller-fact discipline + lot-shaping (read-only imports; this
# route is UNMOUNTED and never edits those modules). A single _FieldRefusal identity crosses the
# modules, and the security-sensitive lot bounding stays one accepted implementation, not a fork.
from app.api.v1._proposal_fact_domains import (
    _FieldRefusal,
    _require_label,
    _validate_lot_rule_fact_domains,
    _validate_lot_rule_fact_keys,
    _validate_lot_rule_fact_types,
)
from app.api.v1.proposal_checks_api import (
    ROUTE_MAX_LOT_LINE_SEGMENTS,
    ROUTE_MAX_STREET_LINES,
    _build_lot_context,
)
from app.api.v1.proposal_validation import (
    MAX_BODY_BYTES,
    _bounded_message,
    _declared_content_length,
    _read_body_within_ceiling,
)
from app.config import internal_rule_eval_enabled
from app.rules.proposal_checks import ProposalCheckError
from app.rules.registry import RuleRegistry
from app.scenario.derivation import ProposalDerivationError
from app.scenario.lot_geometry_derivation import (
    DerivedLotGeometry,
    derive_lot_line_segments,
    production_lot_geometry_provider,
)
from app.scenario.max_envelope import (
    CandidatePlacementStatus,
    MaxEnvelopeError,
    derive_max_envelope,
)
from app.scenario.proposal import ProposedMassingError

__all__ = [
    "MAX_BODY_BYTES",
    "MAX_FIELD_LEN",
    "MAX_ENVELOPE_STATUS_STATE_MATRIX",
    "get_lot_geometry_provider",
    "get_max_envelope_registry",
    "router",
]

logger = logging.getLogger("app.api.v1.max_envelope_api")

router = APIRouter(prefix="/api/v1", tags=["max_envelope"])

#: Hard cap on the refusal ``field`` value on EVERY response and log path (mirrors the sibling
#: route's BP-3 bound). A legitimate field is a short dotted path; anything longer is truncated
#: with a marker before it can reach a client or a log record.
MAX_FIELD_LEN = 200

#: The documented (HTTP status, state) pairs - the single source of truth. The 200 envelope
#: carries NO ``state`` (pair ``(200, None)``), mirroring the accepted sibling routes.
MAX_ENVELOPE_STATUS_STATE_MATRIX: frozenset[tuple[int, str | None]] = frozenset(
    {
        (200, None),  # the maximum-buildable envelope (NO state; NO derived scenario document)
        (404, None),  # flag off / unmounted-path sentinel (generic Not Found)
        (413, "payload_too_large"),  # raw body over MAX_BODY_BYTES, before parse
        (422, "validation_error"),  # malformed/non-finite/non-encodable body OR typed refusal
        (500, "internal_error"),  # unexpected internal defect (generic)
    }
)


def get_max_envelope_registry() -> RuleRegistry | None:
    """The rule registry the envelope evaluates against. Returns ``None`` so the route loads the
    production registry (via :func:`_effective_registry`); tests monkeypatch this module attribute
    to inject a synthetic fixture registry. NOT a client-controlled input."""
    return None


#: Lazily-loaded, cached production registry (mirrors the sibling route + engine lazy load).
_PRODUCTION_REGISTRY: RuleRegistry | None = None


def _effective_registry() -> RuleRegistry:
    """The registry the engine will evaluate against: the test-injected one when
    :func:`get_max_envelope_registry` supplies it, else the lazily-loaded, cached production
    registry. Resolved ON THE EVENT LOOP (never inside a ``run_in_threadpool`` hop) so a
    first-touch race cannot load the production registry twice."""
    global _PRODUCTION_REGISTRY
    injected = get_max_envelope_registry()
    if injected is not None:
        return injected
    if _PRODUCTION_REGISTRY is None:
        _PRODUCTION_REGISTRY = RuleRegistry().load()
    return _PRODUCTION_REGISTRY


def get_lot_geometry_provider():
    """The lot-geometry provider used for server-side derivation (DB-050(a)) when a request carries
    a BBL but NO lot-line geometry. Returns ``None`` so the route uses the production MapPLUTO
    provider (:func:`app.scenario.lot_geometry_derivation.production_lot_geometry_provider`); tests
    monkeypatch this module attribute to inject an OFFLINE fixture-backed provider. NOT a
    client-controlled input - it has no request binding."""
    return None


def _effective_lot_geometry_provider():
    """The provider server-side derivation uses: the test-injected one when
    :func:`get_lot_geometry_provider` supplies it, else the production MapPLUTO provider."""
    injected = get_lot_geometry_provider()
    if injected is not None:
        return injected
    return production_lot_geometry_provider()


def _should_derive_lot_geometry(lot: dict) -> bool:
    """DB-050(a): derive server-side ONLY when the caller supplied NO lot-line geometry AND a
    non-empty BBL. A request that carries any lot-line segment is served byte-identically to today
    (no derivation call).

    "No lot-line geometry" means the field is ABSENT, ``None``, or an EMPTY LIST - nothing else. A
    malformed ``lot_line_segments`` (a string, a number, an object) is NOT an invitation to
    substitute derived geometry: it stays on the typed-refusal path so ``_build_lot_context``'s
    ``lot.lot_line_segments must be an array`` 422 survives unchanged, with or without a BBL.
    Silently replacing a caller's malformed field would turn a documented refusal into a 200."""
    if "lot_line_segments" in lot:
        segments = lot["lot_line_segments"]
        supplied_none = segments is None or (isinstance(segments, list) and not segments)
        if not supplied_none:
            return False
    bbl = lot.get("bbl")
    if isinstance(bbl, str):
        return bbl.strip() != ""
    return isinstance(bbl, int | float) and not isinstance(bbl, bool)


def _json(status_code: int, body: dict, correlation_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code, content=body, headers={"X-Correlation-ID": correlation_id}
    )


def _not_found() -> JSONResponse:
    """Generic 404 identical to FastAPI's default for an unmounted path (fail-safe disable):
    no correlation id, no body hint that the feature exists."""
    return JSONResponse(status_code=404, content={"detail": "Not Found"})


def _bounded_field(field: str | None) -> str | None:
    """Hard-cap a refusal ``field`` before it reaches a client OR a log record (BP-3). The
    truncation marker names the original length only."""
    if field is None or len(field) <= MAX_FIELD_LEN:
        return field
    return field[:MAX_FIELD_LEN] + f"...<truncated; {len(field)} chars total>"


def _validation_error(
    message: str, correlation_id: str, *, field: str | None = None
) -> JSONResponse:
    """Typed (422, "validation_error") with a BOUNDED reason (BP-3), optionally naming the exact
    ``field`` (itself bounded). Never a traceback / path / secret / internal string."""
    body: dict[str, object] = {
        "state": "validation_error",
        "message": _bounded_message(message),
        "correlation_id": correlation_id,
    }
    if field is not None:
        body["field"] = _bounded_field(field)
    return _json(422, body, correlation_id)


def _payload_too_large(correlation_id: str) -> JSONResponse:
    return _json(
        413,
        {
            "state": "payload_too_large",
            "message": f"request body exceeds the maximum of {MAX_BODY_BYTES} bytes",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _internal_error_500(correlation_id: str) -> JSONResponse:
    """Documented generic 500 for ANY unexpected exception. Logs the correlation id only (never
    ``str(exc)`` / a traceback: the request may carry untrusted strings)."""
    return _json(
        500,
        {
            "state": "internal_error",
            "message": "unexpected internal error; see server logs by correlation id",
            "correlation_id": correlation_id,
        },
        correlation_id,
    )


def _enforce_route_caps(lot: dict) -> None:
    """BP-4: refuse a payload whose lot-line / street-line counts exceed the route caps (reusing
    the sibling route's caps), with a cheap O(1) ``len``, BEFORE any engine work. The engine only
    reads the lot AREA, but its generator-checker consistency proof runs the accepted checker on
    the candidate against this same lot, so the same list ceilings apply. A typed refusal names
    the exact cap; non-list fields are left for the shape refusals downstream."""
    lot_lines = lot.get("lot_line_segments")
    if isinstance(lot_lines, list) and len(lot_lines) > ROUTE_MAX_LOT_LINE_SEGMENTS:
        raise _FieldRefusal(
            f"lot.lot_line_segments has {len(lot_lines)} entries, above the route cap "
            f"ROUTE_MAX_LOT_LINE_SEGMENTS ({ROUTE_MAX_LOT_LINE_SEGMENTS})",
            field="lot.lot_line_segments",
        )
    streets = lot.get("street_lines")
    if isinstance(streets, list) and len(streets) > ROUTE_MAX_STREET_LINES:
        raise _FieldRefusal(
            f"lot.street_lines has {len(streets)} entries, above the route cap "
            f"ROUTE_MAX_STREET_LINES ({ROUTE_MAX_STREET_LINES})",
            field="lot.street_lines",
        )


@router.post("/max-envelope", include_in_schema=False)
async def post_max_envelope(request: Request) -> JSONResponse:
    """Derive the maximum-buildable envelope for a caller lot. Feature-flag gated OFF by default
    (reuses INTERNAL_RULE_EVAL_ENABLED), mirroring the sibling internal routes."""
    # Fail-safe disable: absent/unknown flag -> generic 404 with no hint the feature exists.
    if not internal_rule_eval_enabled():
        return _not_found()

    correlation_id = uuid.uuid4().hex

    # Bounded body - raw size ceiling BEFORE parsing, via the reused bounded-streaming accumulator.
    declared_length = _declared_content_length(request)
    if declared_length is not None and declared_length > MAX_BODY_BYTES:
        logger.info(
            "max_envelope_v1 payload_too_large declared_content_length=%d correlation_id=%s",
            declared_length, correlation_id,
        )
        return _payload_too_large(correlation_id)
    raw, too_large = await _read_body_within_ceiling(request.stream(), MAX_BODY_BYTES)
    if too_large:
        logger.info(
            "max_envelope_v1 payload_too_large streamed_over_ceiling max_bytes=%d "
            "correlation_id=%s",
            MAX_BODY_BYTES, correlation_id,
        )
        return _payload_too_large(correlation_id)

    if not raw or not raw.strip():
        return _validation_error("request body must be a JSON object", correlation_id)
    try:
        body = json.loads(raw)
    except Exception:
        return _validation_error(
            "request body is not valid JSON (or is too deeply nested to parse)", correlation_id
        )
    if not isinstance(body, dict):
        return _validation_error("request body must be a JSON object", correlation_id)

    # Strict-JSON + renderer-parity guard: NaN/Infinity or a non-encodable string is refused here
    # with the SAME encoder settings the response renderer uses, so no malformed value reaches the
    # engine or the response.
    try:
        json.dumps(body, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except Exception:
        return _validation_error(
            "request body is not strict-JSON serializable (NaN/Infinity) or contains "
            "non-encodable text (an unpaired surrogate)",
            correlation_id,
        )

    # Boundary extraction + BP-2 / BP-4 / BP-5-type refusals, each typed and field-named.
    try:
        lot = body.get("lot")
        if not isinstance(lot, dict):
            raise _FieldRefusal("lot must be an object", field="lot")
        lot_rule_facts = body.get("lot_rule_facts", {})
        if not isinstance(lot_rule_facts, dict):
            raise _FieldRefusal("lot_rule_facts must be an object", field="lot_rule_facts")
        label_raw = body.get("label")
        label = None if label_raw is None else _require_label(label_raw, "label")

        _enforce_route_caps(lot)  # BP-4 (cheap, before any heavy work)
        _validate_lot_rule_fact_keys(lot_rule_facts)  # BP-2 discipline on keys
        _validate_lot_rule_fact_types(lot_rule_facts)  # BP-5 (mapped value types)
    except _FieldRefusal as exc:
        logger.info("max_envelope_v1 refused field=%s correlation_id=%s",
                    _bounded_field(exc.field), correlation_id)
        return _validation_error(exc.message, correlation_id, field=exc.field)

    # Resolve the engine's effective registry ONCE, on the event loop, then run the cheap
    # registry-derived enum/numeric-bound check. Resolution can only fail on a genuine internal
    # defect (e.g. a missing ruleset dir) -> a generic 500.
    try:
        registry = _effective_registry()
    except Exception:
        logger.error("max_envelope_v1 registry_unavailable correlation_id=%s", correlation_id)
        return _internal_error_500(correlation_id)
    try:
        _validate_lot_rule_fact_domains(lot_rule_facts, registry)
    except _FieldRefusal as exc:
        logger.info("max_envelope_v1 domain_refused field=%s correlation_id=%s",
                    _bounded_field(exc.field), correlation_id)
        return _validation_error(exc.message, correlation_id, field=exc.field)

    # DB-050(a): when the caller supplies NO lot-line geometry but a BBL, derive authoritative
    # EPSG:2263 lot-line segments server-side from the official MapPLUTO connector so the fitted
    # candidate path is reachable. Fail-closed - any derivation failure leaves the segments empty,
    # so the engine keeps today's honest lot_geometry_unsupported gap (never a fabricated
    # rectangle) and the reason is surfaced below. Requests that DO carry segments skip derivation
    # entirely and are byte-identical to today. The provider does I/O + shapely work OFF the event
    # loop.
    # The derivation itself types every EXPECTED failure (unresolvable BBL, no/multiple features,
    # unusable geometry, over-cap ring, connector fault); an UNEXPECTED provider defect propagates
    # by contract, so it is caught here and mapped to the documented generic 500 - the same guard
    # the registry resolution and the engine call carry, so no path escapes the status/state matrix.
    derived: DerivedLotGeometry | None = None
    if _should_derive_lot_geometry(lot):
        try:
            # Resolved ON THE EVENT LOOP (never inside the threadpool hop) so the production
            # client's lazy global cannot be first-touch raced - see DB-039(i) in
            # production_lot_geometry_provider.
            provider = _effective_lot_geometry_provider()
            derived = await run_in_threadpool(
                functools.partial(
                    derive_lot_line_segments,
                    lot.get("bbl"),
                    provider=provider,
                    max_segments=ROUTE_MAX_LOT_LINE_SEGMENTS,
                    correlation_id=correlation_id,
                )
            )
        except Exception:
            logger.error(
                "max_envelope_v1 unexpected_error stage=derive_lot_geometry correlation_id=%s",
                correlation_id,
            )
            return _internal_error_500(correlation_id)
        if derived.ok and derived.segments is not None:
            lot = {**lot, "lot_line_segments": list(derived.segments)}

    try:
        lot_context = _build_lot_context(lot)
    except _FieldRefusal as exc:
        logger.info("max_envelope_v1 lot_refused field=%s correlation_id=%s",
                    _bounded_field(exc.field), correlation_id)
        return _validation_error(exc.message, correlation_id, field=exc.field)

    # The single engine entry, called once, OFF the event loop. BP-3: every propagated error
    # detail is length-capped; an unexpected defect is a generic 500 (no str(exc)/traceback leak).
    try:
        envelope = await run_in_threadpool(
            functools.partial(
                derive_max_envelope,
                lot_context,
                lot_rule_facts,
                registry=registry,
                label=label,
            )
        )
    except MaxEnvelopeError as exc:
        # A precondition failure (bad lot) is the caller's fault -> 422. A generator-checker
        # inconsistency (field 'candidate.*') is an internal invariant violation -> 500.
        if (exc.field or "").startswith("candidate"):
            logger.error("max_envelope_v1 generator_checker_inconsistency field=%s "
                         "correlation_id=%s", _bounded_field(exc.field), correlation_id)
            return _internal_error_500(correlation_id)
        logger.info("max_envelope_v1 precondition_refused field=%s correlation_id=%s",
                    _bounded_field(exc.field), correlation_id)
        return _validation_error(str(exc), correlation_id, field=exc.field)
    except (ProposalCheckError, ProposalDerivationError, ProposedMassingError) as exc:
        # From the consistency proof's checker run over this lot (e.g. a non-finite lot-line
        # coordinate); the caller's fault -> typed, bounded 422 naming the exact field.
        logger.info("max_envelope_v1 lot_check_refused field=%s correlation_id=%s",
                    _bounded_field(getattr(exc, "field", None)), correlation_id)
        return _validation_error(str(exc), correlation_id, field=getattr(exc, "field", None))
    except Exception:
        logger.error("max_envelope_v1 unexpected_error stage=derive correlation_id=%s",
                     correlation_id)
        return _internal_error_500(correlation_id)

    document: dict[str, Any] = envelope.as_dict()
    document["correlation_id"] = correlation_id
    # DB-050(a): when a derivation was attempted, surface its outcome + provenance machine-readably.
    # On a fail-closed outcome the engine has already returned the honest lot_geometry_unsupported
    # gap on empty segments; carry the derivation reason into that placement detail so the caller
    # sees WHY no geometry was available (never a fabricated placement).
    if derived is not None:
        document["derived_lot_geometry"] = derived.as_response_block()
        if not derived.ok:
            placement = document.get("candidate_placement")
            if (
                isinstance(placement, dict)
                and placement.get("status")
                == CandidatePlacementStatus.LOT_GEOMETRY_UNSUPPORTED.value
            ):
                placement["detail"] = (
                    f"{placement['detail']} | server-side lot-geometry derivation "
                    f"({derived.outcome.value}): {derived.detail}"
                )
    try:  # defense in depth: the body was already proven strict-JSON above
        json.dumps(document, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except Exception:
        logger.error("max_envelope_v1 serialization_unsafe correlation_id=%s", correlation_id)
        return _internal_error_500(correlation_id)
    return _json(200, document, correlation_id)
