"""Shared connector transport + bounded-retry engine (task M2-T011).

Consolidates the M1-T002 transport primitives (previously homed in
``app.connectors.pluto_soda``) and the transport retry loop previously
duplicated across the four accepted connectors (``pluto_soda``,
``zoning_features_arcgis``, ``ztldb_soda``, ``mappluto_geometry_arcgis``).
NULL HYPOTHESIS = behavior unchanged: every retry count, budget check,
Retry-After rule, jitter bound, typed-error classification, sanitization
rule, and log line is preserved exactly as accepted. Connector-specific
semantics (error classes, messages, SODA 400 classification, layer
tagging) stay in the connectors and reach this engine only through
:class:`RetryHooks` / :func:`standard_retry_hooks`.

Transport hardening carried over verbatim from M1-T002 G5: bounded body
read (F1, :data:`MAX_RESPONSE_BYTES`) and refused redirects (F3,
:class:`NoRedirectHandler` - urllib's default handler would re-send
X-App-Token to a redirect target). Retry-policy grounding is unchanged
from M1-T009 (Socrata documents only the 429 status; Retry-After is
optional input honored per RFC 9110, over-cap honored by NOT retrying;
full-jitter backoff from an injected seeded RNG). The legacy M1-T002
pluto policy (plain exponential, no jitter) is retained as
:func:`fixed_exponential_delay`; PLUTO production retry authority stays
in :class:`app.resilience.fetcher.ResilientPlutoFetcher`.

Deterministic code only: no AI, no legal logic (PRD sections 2, 32.5).
"""

from __future__ import annotations

import logging
import re
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import NoReturn

from app.resilience.budget import AnalysisBudget

__all__ = [
    "DEFAULT_OPENER",
    "MAX_RESPONSE_BYTES",
    "DelayPolicy",
    "NoRedirectHandler",
    "RetryHooks",
    "Transport",
    "TransportFailure",
    "TransportResponse",
    "TransportTimeout",
    "fixed_exponential_delay",
    "get_retry_after",
    "jittered_retry_after_delay",
    "request_with_retry",
    "sanitize_retry_after",
    "standard_retry_hooks",
    "urllib_transport",
]

# G5 F1 (M1-T002): bounded response read. Expected per-record bodies are
# small; anything beyond this cap indicates a compromised/misbehaving
# endpoint and is refused instead of exhausting worker memory.
MAX_RESPONSE_BYTES = 10 * 1024 * 1024

# Task M1-T009: Retry-After is untrusted response data. Both RFC 9110 forms
# (delay-seconds and HTTP-date, e.g. "Fri, 17 Jul 2026 08:00:00 GMT") match
# this allowlist and pass through verbatim; anything else is repr()-sanitized
# before entering the typed-error detail. The delay policy parses the value;
# unparseable -> jittered backoff.
_RETRY_AFTER_SAFE_RE = re.compile(r"^[A-Za-z0-9,: +\-]{1,64}$")


# ---------------------------------------------------------------------------
# Transport abstraction (injectable so all tests run offline) - moved
# verbatim from app.connectors.pluto_soda (M1-T002); pluto_soda re-exports
# these names so every existing import site keeps working unchanged.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TransportResponse:
    """Transport-level response.

    ``headers`` (task M1-T009, ADDITIVE with a default so every existing
    fixture transport keeps constructing ``TransportResponse(status, body)``
    unchanged): response headers with LOWERCASE keys - transports normalize
    on capture. Used only to surface the RFC 9110 ``Retry-After`` value of a
    429 into the typed error detail for the resilience layer; header values
    are never logged and never appear in payloads unsanitized.
    """

    status: int
    body: str
    headers: Mapping[str, str] = field(default_factory=dict)


class TransportTimeout(Exception):
    """Raised by a transport on connect/read timeout."""


class TransportFailure(Exception):
    """Raised by a transport when the network/DNS/TLS layer fails.
    The message must already be free of secrets."""


Transport = Callable[[str, dict[str, str], float], TransportResponse]


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """G5 F3 (M1-T002): refuse ALL HTTP redirects. urllib's default redirect
    handler re-sends request headers - including X-App-Token - to the
    redirect target, so an open redirect on the pinned official host could
    exfiltrate the token cross-host. Returning None makes urlopen raise
    HTTPError(3xx), which the transport converts into a plain
    TransportResponse; the caller then classifies the 3xx as a typed error.
    The token never follows any redirect, same-host or cross-host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ARG002
        return None


# Module-level opener WITHOUT redirect following (G5 F3). build_opener
# replaces the default HTTPRedirectHandler with our subclass.
DEFAULT_OPENER = urllib.request.build_opener(NoRedirectHandler)


def _lowercase_headers(message: object) -> dict[str, str]:
    """Task M1-T009: capture RESPONSE headers with lowercase keys for the
    TransportResponse headers contract. Response headers are server data
    (never the request's X-App-Token); they stay out of logs and payloads
    except the sanitized Retry-After detail."""
    if message is None:
        return {}
    try:
        items = message.items()  # type: ignore[attr-defined]
    except AttributeError:
        return {}
    return {str(name).lower(): str(value) for name, value in items}


def _bounded_read(stream: object) -> str:
    """G5 F1: read at most MAX_RESPONSE_BYTES; refuse oversize bodies with a
    typed transport failure instead of an unbounded read + json.loads."""
    data = stream.read(MAX_RESPONSE_BYTES + 1)  # type: ignore[attr-defined]
    if len(data) > MAX_RESPONSE_BYTES:
        raise TransportFailure(
            f"response body exceeded {MAX_RESPONSE_BYTES} bytes; refusing unbounded read"
        )
    return data.decode("utf-8", errors="replace")


def urllib_transport(
    url: str,
    headers: dict[str, str],
    timeout: float,
    *,
    opener: object | None = None,
) -> TransportResponse:
    """Default stdlib transport (no third-party HTTP dependency; low-storage
    policy). Translates urllib failures into transport-level signals.
    Hardened per M1-T002 G5: bounded body read (F1) and no redirect
    following (F3).

    ``opener`` (task M2-T011, additive): the no-redirect opener to use;
    defaults to the module-level :data:`DEFAULT_OPENER`. The
    ``pluto_soda.urllib_transport`` compatibility wrapper passes its own
    module-level ``_OPENER`` so the accepted monkeypatch seam
    (``pluto_soda._OPENER``) keeps working unchanged."""
    active_opener = opener if opener is not None else DEFAULT_OPENER
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with active_opener.open(request, timeout=timeout) as response:  # type: ignore[attr-defined]  # noqa: S310
            return TransportResponse(
                status=response.status,
                body=_bounded_read(response),
                # getattr: headers stay optional so response doubles without
                # a headers attribute (tests) keep working - headers are an
                # additive capture, never a required transport capability.
                headers=_lowercase_headers(getattr(response, "headers", None)),
            )
    except urllib.error.HTTPError as exc:
        # Includes refused 3xx redirects (F3): status passes through and the
        # caller maps it to a typed error; no request is ever re-issued.
        body = _bounded_read(exc)
        return TransportResponse(
            status=exc.code,
            body=body,
            headers=_lowercase_headers(getattr(exc, "headers", None)),
        )
    except TimeoutError as exc:  # socket.timeout is an alias since Python 3.10
        raise TransportTimeout(f"timeout after {timeout}s") from exc
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, TimeoutError):
            raise TransportTimeout(f"timeout after {timeout}s") from exc
        raise TransportFailure(f"network failure: {type(exc.reason).__name__}") from exc


# ---------------------------------------------------------------------------
# Retry-After capture (single definition; previously duplicated per module)
# ---------------------------------------------------------------------------


def get_retry_after(headers: object) -> str | None:
    """Case-insensitive Retry-After lookup (transports normalize to
    lowercase keys; this stays defensive for injected test transports whose
    header objects may not be mappings)."""
    try:
        items = headers.items()  # type: ignore[attr-defined]
    except AttributeError:
        return None
    for name, value in items:
        if str(name).lower() == "retry-after" and isinstance(value, str):
            return value
    return None


def sanitize_retry_after(raw: str) -> str:
    """Task M1-T009: pass through RFC 9110-shaped Retry-After values
    verbatim; repr()-sanitize anything else (untrusted header data)."""
    if _RETRY_AFTER_SAFE_RE.match(raw):
        return raw
    return repr(raw)


# ---------------------------------------------------------------------------
# Delay policies (the ONLY point where the four accepted loops differed in
# retry arithmetic; both accepted behaviors preserved verbatim)
# ---------------------------------------------------------------------------

# (attempt, last_kind, last_detail) -> seconds to sleep before the next
# attempt, or None to STOP retrying immediately (Retry-After beyond the
# bounded-wait cap: honored by NOT retrying - M1-T009 policy).
DelayPolicy = Callable[[int, "str | None", Mapping[str, object]], "float | None"]


def fixed_exponential_delay(backoff_base: float) -> DelayPolicy:
    """Legacy M1-T002 ``pluto_soda`` policy, preserved exactly: plain
    exponential ``backoff_base * 2**(attempt-1)`` with no jitter and no
    Retry-After wait (the sanitized Retry-After value still lands in the
    typed-error detail for the resilience layer to honor). Production
    jitter/Retry-After authority for the PLUTO path lives in
    :class:`app.resilience.fetcher.ResilientPlutoFetcher`, which calls the
    connector with ``max_attempts=1``."""

    def policy(
        attempt: int, last_kind: str | None, last_detail: Mapping[str, object]
    ) -> float | None:
        return backoff_base * (2 ** (attempt - 1))

    return policy


def jittered_retry_after_delay(
    *,
    backoff_base: float,
    backoff_cap: float,
    retry_after_cap: float,
    rng,
    wall_clock,
) -> DelayPolicy:
    """M1-T009 policy used by the M2-T007/T008/T009 connectors, preserved
    exactly: a parseable Retry-After on a 429 is honored verbatim unless it
    exceeds ``retry_after_cap`` (then retrying STOPS - typed failure now,
    never a blocked worker thread); otherwise AWS-style full-jitter bounded
    exponential backoff from the injected seeded RNG."""
    # Deferred import keeps module import order identical to the accepted
    # connectors (retry.py has no dependency back on this module either way).
    from app.resilience.retry import backoff_delay, parse_retry_after

    def policy(
        attempt: int, last_kind: str | None, last_detail: Mapping[str, object]
    ) -> float | None:
        if last_kind == "rate_limited" and "retry_after" in last_detail:
            parsed = parse_retry_after(
                last_detail["retry_after"], wall_now=wall_clock
            )
            if parsed is not None:
                if parsed > retry_after_cap:
                    # Honored by NOT retrying: typed failure now rather
                    # than a blocked worker thread (M1-T009 policy).
                    return None
                return parsed
        return backoff_delay(
            attempt,
            base_seconds=backoff_base,
            cap_seconds=backoff_cap,
            rng=rng,
        )

    return policy


# ---------------------------------------------------------------------------
# Shared bounded retry engine
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RetryHooks:
    """Connector-specific seam of the shared loop. Every hook that raises
    MUST raise (``NoReturn``); the engine never fabricates connector errors
    itself, so typed taxonomies, messages, detail dicts, and layer tags stay
    in the owning connector exactly as accepted."""

    logger: logging.Logger  # the CONNECTOR's logger (logger names unchanged)
    log_label: str  # accepted per-connector log prefix, e.g. "pluto_soda"
    correlation_id: str
    # Sanitizer applied to str(TransportFailure) before it enters the retry
    # detail: identity for pluto_soda (M1-T002 accepted behavior), each
    # connector's _safe_text for the M2-wave connectors.
    sanitize_network_reason: Callable[[str], str]
    # Terminal raisers (retry budget exhausted). detail already carries
    # {**last_detail, "url": url, "max_attempts": max_attempts}.
    raise_rate_limited: Callable[[dict], NoReturn]
    raise_timeout: Callable[[dict], NoReturn]
    raise_unavailable: Callable[[dict, str | None], NoReturn]
    # Non-retryable statuses (anything not 200/429/5xx, e.g. the SODA 400
    # schema-drift signature, refused 3xx redirects): classify and raise.
    raise_for_unexpected_status: Callable[[TransportResponse], NoReturn]
    # Budget exhaustion (only for connectors that thread a budget through).
    raise_budget_exceeded: Callable[[AnalysisBudget], NoReturn] | None = None


# Accepted budget-exhaustion message, identical across the M2-wave
# connectors (M2-T007/T008/T009) and preserved verbatim.
_BUDGET_EXHAUSTED_MESSAGE = (
    "per-analysis upstream request budget is exhausted; no "
    "further upstream calls are made for this analysis"
)


def standard_retry_hooks(
    *,
    logger: logging.Logger,
    log_label: str,
    correlation_id: str,
    url: str,
    sanitize_network_reason: Callable[[str], str],
    rate_limited_error: type[Exception],
    rate_limited_message: str,
    timeout_error: type[Exception],
    timeout_message: str,
    unavailable_error: type[Exception],
    unavailable_message: str,
    include_reason_kind: bool,
    raise_for_unexpected_status: Callable[[TransportResponse], NoReturn] | None = None,
    unexpected_status_message: str | None = None,
    budget_error: type[Exception] | None = None,
    error_kwargs: Mapping[str, object] | None = None,
) -> RetryHooks:
    """Build the standard terminal raisers so each connector declares ONLY
    its accepted error classes, messages, and extra kwargs (e.g. the
    zoning-features ``layer`` tag) instead of re-implementing the raise
    scaffolding. Every error class must accept the shared connector-error
    signature ``(message, *, correlation_id, detail, **error_kwargs)``.

    ``include_reason_kind`` preserves the accepted detail-shape split: the
    M2-wave connectors add ``reason_kind`` to the terminal unavailable
    detail; the M1-T002 pluto_soda detail has no such key.

    Exactly one of ``raise_for_unexpected_status`` (custom classification,
    e.g. the SODA 400 schema-drift signature) or
    ``unexpected_status_message`` (a ``{status}`` template raised as
    ``unavailable_error`` with ``{"http_status": status, "url": url}``,
    the accepted ArcGIS-connector shape) must be provided."""
    extra = dict(error_kwargs or {})
    if (raise_for_unexpected_status is None) == (unexpected_status_message is None):
        raise ValueError(
            "provide exactly one of raise_for_unexpected_status or "
            "unexpected_status_message"
        )

    def _raise_unexpected_from_template(response: TransportResponse) -> NoReturn:
        assert unexpected_status_message is not None  # noqa: S101 - checked above
        raise unavailable_error(
            unexpected_status_message.format(status=response.status),
            correlation_id=correlation_id,
            detail={"http_status": response.status, "url": url},
            **extra,
        )

    def _raise_rate_limited(detail: dict) -> NoReturn:
        raise rate_limited_error(
            rate_limited_message, correlation_id=correlation_id, detail=detail, **extra
        )

    def _raise_timeout(detail: dict) -> NoReturn:
        raise timeout_error(
            timeout_message, correlation_id=correlation_id, detail=detail, **extra
        )

    def _raise_unavailable(detail: dict, last_kind: str | None) -> NoReturn:
        if include_reason_kind:
            detail = {**detail, "reason_kind": last_kind}
        raise unavailable_error(
            unavailable_message, correlation_id=correlation_id, detail=detail, **extra
        )

    raise_budget_exceeded: Callable[[AnalysisBudget], NoReturn] | None = None
    if budget_error is not None:

        def raise_budget_exceeded(exhausted: AnalysisBudget) -> NoReturn:
            raise budget_error(
                _BUDGET_EXHAUSTED_MESSAGE,
                correlation_id=correlation_id,
                detail={
                    "max_upstream_requests": exhausted.max_upstream_requests,
                    "consumed": exhausted.consumed,
                    "analysis_id": exhausted.analysis_id,
                },
                **extra,
            )

    return RetryHooks(
        logger=logger,
        log_label=log_label,
        correlation_id=correlation_id,
        sanitize_network_reason=sanitize_network_reason,
        raise_rate_limited=_raise_rate_limited,
        raise_timeout=_raise_timeout,
        raise_unavailable=_raise_unavailable,
        raise_for_unexpected_status=(
            raise_for_unexpected_status
            if raise_for_unexpected_status is not None
            else _raise_unexpected_from_template
        ),
        raise_budget_exceeded=raise_budget_exceeded,
    )


def request_with_retry(
    url: str,
    *,
    transport: Transport,
    headers: dict[str, str],
    timeout: float,
    max_attempts: int,
    hooks: RetryHooks,
    compute_delay: DelayPolicy,
    sleep: Callable[[float], None],
    budget: AnalysisBudget | None = None,
) -> TransportResponse:
    """Bounded retry on 429/5xx/timeout/network failure ONLY. Every other
    status and every parse or drift condition is classified by the owning
    connector via ``hooks.raise_for_unexpected_status`` and never retried.
    One budget unit per upstream ATTEMPT (every network call costs quota),
    consumed BEFORE the I/O. Control flow is byte-for-byte the accepted
    M1-T002/M2-T007/T008/T009 loop; only the connector-specific raises and
    log labels arrive through ``hooks``."""
    last_kind: str | None = None
    last_detail: dict = {}
    for attempt in range(1, max_attempts + 1):
        if budget is not None and not budget.try_consume():
            assert hooks.raise_budget_exceeded is not None  # noqa: S101 - wiring error, not runtime input
            hooks.raise_budget_exceeded(budget)
        try:
            response = transport(url, headers, timeout)
        except TransportTimeout:
            last_kind, last_detail = "timeout", {"attempts": attempt}
            hooks.logger.warning(
                "%s timeout url=%s attempt=%d correlation_id=%s",
                hooks.log_label, url, attempt, hooks.correlation_id,
            )
        except TransportFailure as exc:
            last_kind = "network"
            last_detail = {
                "attempts": attempt,
                "reason": hooks.sanitize_network_reason(str(exc)),
            }
            hooks.logger.warning(
                "%s network failure url=%s attempt=%d correlation_id=%s",
                hooks.log_label, url, attempt, hooks.correlation_id,
            )
        else:
            if response.status == 200:
                return response
            if response.status == 429:
                last_kind, last_detail = "rate_limited", {"attempts": attempt}
                # Surface the (sanitized) Retry-After value in the typed
                # detail so downstream layers can honor it exactly (RFC 9110
                # section 10.2.3). The header is OPTIONAL input, never a
                # guessed guarantee (M1-T009).
                retry_after_raw = get_retry_after(response.headers)
                if retry_after_raw is not None:
                    last_detail["retry_after"] = sanitize_retry_after(retry_after_raw)
                hooks.logger.warning(
                    "%s throttled (429) url=%s attempt=%d correlation_id=%s",
                    hooks.log_label, url, attempt, hooks.correlation_id,
                )
            elif 500 <= response.status < 600:
                last_kind = "server_error"
                last_detail = {"attempts": attempt, "http_status": response.status}
                hooks.logger.warning(
                    "%s server error %d url=%s attempt=%d correlation_id=%s",
                    hooks.log_label, response.status, url, attempt,
                    hooks.correlation_id,
                )
            else:
                hooks.raise_for_unexpected_status(response)
        if attempt < max_attempts:
            delay = compute_delay(attempt, last_kind, last_detail)
            if delay is None:
                # Retry-After beyond the bounded wait: honored by NOT
                # retrying (typed failure now, never a blocked thread).
                break
            sleep(delay)

    detail = {**last_detail, "url": url, "max_attempts": max_attempts}
    if last_kind == "rate_limited":
        hooks.raise_rate_limited(detail)
    if last_kind == "timeout":
        hooks.raise_timeout(detail)
    hooks.raise_unavailable(detail, last_kind)
    raise AssertionError("unreachable: a terminal hook must raise")  # pragma: no cover
