"""Resilient PLUTO fetcher: composition of cache, retry, breaker,
last-known-good, and budget around the accepted connector (task M1-T009).

Seam design (packet discipline "behind the existing transport seam"):

- The accepted ``fetch_by_bbl`` stays UNCHANGED as the single-attempt
  primitive: this wrapper always calls it with ``max_attempts=1`` and a
  no-op sleep so ALL retry authority lives in ONE place (no double retry
  loops, no double sleeps). Tests inject the same fixture ``transport``
  through ``fetch_kwargs`` that the connector suite already uses.
- The API route keeps its ``get_pluto_fetcher`` dependency seam; the
  resilient fetcher satisfies the same ``(bbl, correlation_id) ->
  PlutoFetchResult`` contract, so route tests and the web-e2e fixture
  harness keep overriding the seam unchanged.

Last-known-good staleness (item E, scenario S5) is surfaced through the
EXISTING provenance structures only - no contract change:

- ``retrieved_at`` on the result and every fact remains the ORIGINAL
  retrieval moment (provenance records actual retrieval, never serve time).
- A machine-readable connector note with the stable prefix
  ``served_from_last_known_good:`` is appended to ``result.notes``; the
  accepted builder carries notes verbatim into
  ``reproducibility.connector_notes`` (schema: array of non-empty strings),
  so staleness is visible in the served profile and in reports. The builder
  maps only its known note prefixes into ``missing_inputs``, so this note
  adds no phantom missing input.
- A stale serve is therefore NEVER silently fresh; a first-class
  contract-visible staleness field (e.g. ``reproducibility.staleness``)
  is recommended as an additive contract follow-up reviewed at G1.
"""

from __future__ import annotations

import copy
import os
import threading
import time
from collections import OrderedDict
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from random import Random

from app.connectors.bbl import normalize_bbl
from app.connectors.pluto_soda import (
    DATASET_ID,
    SOURCE_ID,
    PlutoConnectorError,
    PlutoFetchResult,
    RateLimitedError,
    SourceTimeoutError,
    SourceUnavailableError,
    fetch_by_bbl,
)
from app.resilience.breaker import CircuitBreaker
from app.resilience.budget import AnalysisBudget
from app.resilience.cache import TTLCache
from app.resilience.config import ResilienceConfig
from app.resilience.metrics import ResilienceMetrics
from app.resilience.retry import backoff_delay, parse_retry_after

__all__ = [
    "LKG_NOTE_PREFIX",
    "BudgetExceededError",
    "CircuitOpenError",
    "ResilientPlutoFetcher",
    "build_default_resilient_fetcher",
]


# Stable machine-readable prefix of the staleness note (scenario S5). Callers
# and the UI can detect a last-known-good serve by this prefix without a new
# contract field.
LKG_NOTE_PREFIX = "served_from_last_known_good:"


class BudgetExceededError(PlutoConnectorError):
    """Per-analysis upstream request budget exhausted (typed, scenario S6).

    Raised BEFORE any further upstream I/O; never masked by cache-expired
    refetches or last-known-good fallback."""

    error_type = "budget_exceeded"


class CircuitOpenError(SourceUnavailableError):
    """Fast rejection while the per-source circuit is open (scenario S4).

    Subclasses ``SourceUnavailableError`` ON PURPOSE: the outward meaning is
    "the official source is not being called because it is failing", so the
    documented route status/state matrix ((503, source_unavailable)) is
    unchanged; ``detail.circuit == "open"`` distinguishes the fast-reject
    path for operators."""


@dataclass
class _LkgEntry:
    stored_at: float
    result: PlutoFetchResult


def _noop_sleep(_seconds: float) -> None:
    return None


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _rfc3339(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def _is_retryable(exc: PlutoConnectorError) -> bool:
    """Retryable = transient upstream trouble (429 / timeout / 5xx / network).

    Never retried: schema drift (M1-T001 G1 finding - never blindly retried),
    non-drift 4xx and refused 3xx (the connector raises these as
    ``SourceUnavailableError`` WITH an ``http_status`` detail in 300..499),
    and every non-connector error. The same classification gates breaker
    counting and last-known-good eligibility: only transient-upstream
    failures mean "upstream is down".
    """
    if isinstance(exc, RateLimitedError | SourceTimeoutError):
        return True
    if isinstance(exc, SourceUnavailableError):
        status = exc.detail.get("http_status")
        if isinstance(status, int) and not isinstance(status, bool) \
                and not 500 <= status < 600:
            # Only 5xx are transient among status-bearing failures: refused
            # 3xx redirects, non-drift 4xx, and unexpected non-200 2xx would
            # all fail identically on retry.
            return False
        return True
    return False


class ResilientPlutoFetcher:
    """Callable ``(bbl, correlation_id, *, budget=None) -> PlutoFetchResult``.

    Per-call pipeline (each stage deterministic and injected for tests):

    1. BBL validation (typed ``BBLValidationError`` before any budget/cache/
       network work - unchanged connector discipline).
    2. Versioned-key TTL cache lookup (item A): a hit returns a deep copy
       with ZERO upstream I/O and no budget consumption.
    3. Per-source circuit breaker (item D): open -> fast reject with
       last-known-good fallback or typed ``CircuitOpenError``.
    4. Bounded retry engine (items B/C): one budget unit per upstream
       attempt (item F); 429 honors ``Retry-After`` EXACTLY when present,
       otherwise full-jitter bounded exponential backoff from the injected
       seeded RNG; ``retry_max_attempts`` caps total attempts.
    5. Success: cache + last-known-good stores updated, breaker success.
       Final transient failure: breaker failure, then last-known-good with
       VISIBLE staleness (item E) or the original typed error.
    """

    def __init__(
        self,
        *,
        fetch_fn: Callable[..., PlutoFetchResult] = fetch_by_bbl,
        config: ResilienceConfig | None = None,
        now: Callable[[], float] = time.monotonic,
        wall_clock: Callable[[], datetime] = _utc_now,
        sleep: Callable[[float], None] = time.sleep,
        rng: Random | None = None,
        metrics: ResilienceMetrics | None = None,
        fetch_kwargs: Mapping[str, object] | None = None,
    ) -> None:
        self._fetch_fn = fetch_fn
        self._config = config or ResilienceConfig()
        self._now = now
        self._wall_clock = wall_clock
        self._sleep = sleep
        self._rng = rng or Random()
        self.metrics = metrics or ResilienceMetrics()
        self._fetch_kwargs = dict(fetch_kwargs or {})
        self._cache = TTLCache(
            ttl_seconds=self._config.cache_ttl_seconds,
            max_entries=self._config.cache_max_entries,
            now=now,
            metrics=self.metrics,
        )
        self._breaker = CircuitBreaker(
            source_id=SOURCE_ID,
            failure_threshold=self._config.breaker_failure_threshold,
            cooldown_seconds=self._config.breaker_cooldown_seconds,
            now=now,
            metrics=self.metrics,
        )
        self._lkg_lock = threading.Lock()
        self._lkg: OrderedDict[str, _LkgEntry] = OrderedDict()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def __call__(
        self,
        bbl: object,
        correlation_id: str,
        *,
        budget: AnalysisBudget | None = None,
    ) -> PlutoFetchResult:
        canonical = normalize_bbl(bbl).canonical  # validation before anything
        key = self._cache_key(canonical)

        cached = self._cache.get(key)
        if cached is not None:
            self.metrics.emit(
                "cache_hit", key=key, correlation_id=correlation_id
            )
            return copy.deepcopy(cached)  # type: ignore[return-value]
        self.metrics.emit("cache_miss", key=key, correlation_id=correlation_id)

        if not self._breaker.allow():
            self.metrics.emit(
                "breaker_fast_reject",
                source_id=SOURCE_ID,
                cooldown_remaining_seconds=self._breaker.cooldown_remaining(),
                correlation_id=correlation_id,
            )
            rejection = CircuitOpenError(
                "circuit breaker is open for this source; the upstream call "
                "was rejected without network I/O",
                correlation_id=correlation_id,
                detail={
                    "circuit": "open",
                    "cooldown_remaining_seconds": self._breaker.cooldown_remaining(),
                },
            )
            return self._serve_lkg_or_raise(key, correlation_id, rejection)

        try:
            result = self._fetch_with_retry(canonical, correlation_id, budget)
        except BudgetExceededError:
            raise  # never masked by LKG (budget is a caller-side condition)
        except PlutoConnectorError as exc:
            if _is_retryable(exc):
                self._breaker.record_failure()
                self.metrics.emit(
                    "fetch_failure",
                    error_type=exc.error_type,
                    correlation_id=correlation_id,
                )
                return self._serve_lkg_or_raise(key, correlation_id, exc)
            self.metrics.emit(
                "fetch_failure",
                error_type=exc.error_type,
                correlation_id=correlation_id,
            )
            raise

        self._breaker.record_success()
        self._cache.put(key, copy.deepcopy(result))
        self.metrics.emit("cache_store", key=key, correlation_id=correlation_id)
        if result.status == "ok":
            self._store_lkg(key, result)
        self.metrics.emit(
            "fetch_success", status=result.status, correlation_id=correlation_id
        )
        return result

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _cache_key(self, canonical_bbl: str) -> str:
        # Versioned key (item A): bumping cache_key_version invalidates every
        # prior entry by construction.
        return (
            f"{self._config.cache_key_version}:{SOURCE_ID}:{DATASET_ID}:"
            f"bbl={canonical_bbl}"
        )

    def _fetch_with_retry(
        self,
        canonical_bbl: str,
        correlation_id: str,
        budget: AnalysisBudget | None,
    ) -> PlutoFetchResult:
        config = self._config
        for attempt in range(1, config.retry_max_attempts + 1):
            if budget is not None:
                if not budget.try_consume():
                    self.metrics.emit(
                        "budget_exceeded",
                        max_upstream_requests=budget.max_upstream_requests,
                        consumed=budget.consumed,
                        analysis_id=budget.analysis_id,
                        correlation_id=correlation_id,
                    )
                    raise BudgetExceededError(
                        "per-analysis upstream request budget is exhausted; "
                        "no further upstream calls are made for this analysis",
                        correlation_id=correlation_id,
                        detail={
                            "max_upstream_requests": budget.max_upstream_requests,
                            "consumed": budget.consumed,
                            "analysis_id": budget.analysis_id,
                        },
                    )
                self.metrics.emit(
                    "budget_consumed",
                    consumed=budget.consumed,
                    remaining=budget.remaining,
                    analysis_id=budget.analysis_id,
                    correlation_id=correlation_id,
                )
            try:
                # Single-attempt primitive: the accepted connector keeps its
                # validation/typing/provenance behavior; retry authority
                # lives ONLY here (no nested retry loops or sleeps).
                return self._fetch_fn(
                    canonical_bbl,
                    correlation_id=correlation_id,
                    **{**self._fetch_kwargs, "max_attempts": 1, "sleep": _noop_sleep},
                )
            except PlutoConnectorError as exc:
                if not _is_retryable(exc) or attempt >= config.retry_max_attempts:
                    raise
                delay = self._retry_delay(exc, attempt, correlation_id)
                if delay is None:
                    # Retry-After beyond the bounded wait: honored by NOT
                    # retrying (typed failure now, never a blocked thread).
                    raise
                self._sleep(delay)
        raise AssertionError("unreachable: loop returns or raises")  # pragma: no cover

    def _retry_delay(
        self, exc: PlutoConnectorError, attempt: int, correlation_id: str
    ) -> float | None:
        """Delay before the next attempt; ``None`` aborts retrying."""
        config = self._config
        if isinstance(exc, RateLimitedError):
            retry_after = parse_retry_after(
                exc.detail.get("retry_after"), wall_now=self._wall_clock
            )
            if retry_after is not None:
                if retry_after > config.retry_after_max_wait_seconds:
                    self.metrics.emit(
                        "retry_after_exceeds_cap",
                        retry_after_seconds=retry_after,
                        cap_seconds=config.retry_after_max_wait_seconds,
                        correlation_id=correlation_id,
                    )
                    return None
                # Item B: honored EXACTLY - no jitter, no scaling, no early
                # retry (scenario S2 asserts the sleep sequence verbatim).
                self.metrics.emit(
                    "retry_after_honored",
                    retry_after_seconds=retry_after,
                    attempt=attempt,
                    correlation_id=correlation_id,
                )
                return retry_after
        delay = backoff_delay(
            attempt,
            base_seconds=config.backoff_base_seconds,
            cap_seconds=config.backoff_cap_seconds,
            rng=self._rng,
        )
        self.metrics.emit(
            "retry_scheduled",
            attempt=attempt,
            delay_seconds=delay,
            reason=exc.error_type,
            correlation_id=correlation_id,
        )
        return delay

    def _store_lkg(self, key: str, result: PlutoFetchResult) -> None:
        with self._lkg_lock:
            self._lkg[key] = _LkgEntry(
                stored_at=self._now(), result=copy.deepcopy(result)
            )
            self._lkg.move_to_end(key)
            while len(self._lkg) > self._config.lkg_max_entries:
                self._lkg.popitem(last=False)

    def _serve_lkg_or_raise(
        self, key: str, correlation_id: str, exc: PlutoConnectorError
    ) -> PlutoFetchResult:
        """Item E (scenario S5): serve the last-known-good snapshot WITH
        visible staleness, or raise the original typed failure."""
        with self._lkg_lock:
            entry = self._lkg.get(key)
        if entry is None:
            self.metrics.emit(
                "lkg_unavailable", key=key, correlation_id=correlation_id
            )
            raise exc
        age_seconds = self._now() - entry.stored_at
        if age_seconds > self._config.lkg_max_age_seconds:
            self.metrics.emit(
                "lkg_too_old",
                key=key,
                age_seconds=age_seconds,
                max_age_seconds=self._config.lkg_max_age_seconds,
                correlation_id=correlation_id,
            )
            raise exc
        result = copy.deepcopy(entry.result)
        circuit_open = bool(exc.detail.get("circuit") == "open")
        # Staleness is VISIBLE through existing provenance structures:
        # retrieved_at stays the ORIGINAL retrieval moment, and this stable-
        # prefix note travels into reproducibility.connector_notes. Never
        # silently fresh (PRD principle 4).
        note = (
            f"{LKG_NOTE_PREFIX} upstream failure ({exc.error_type}"
            f"{', circuit open' if circuit_open else ''}) at "
            f"{_rfc3339(self._wall_clock())}; serving the last-known-good "
            f"official snapshot retrieved at {result.retrieved_at} "
            f"(age {age_seconds:.0f}s at serve time). This response is STALE "
            "cached data, not a fresh retrieval; retrieved_at reflects the "
            "actual original retrieval (task M1-T009)."
        )
        result.notes = [*result.notes, note]
        self.metrics.emit(
            "lkg_served",
            key=key,
            age_seconds=age_seconds,
            upstream_error_type=exc.error_type,
            correlation_id=correlation_id,
        )
        return result


def build_default_resilient_fetcher(
    environ: Mapping[str, str] = os.environ,
) -> ResilientPlutoFetcher:
    """Production composition: env-derived config, real monotonic clock,
    real sleep, OS-seeded RNG, structured-logging metrics."""
    return ResilientPlutoFetcher(config=ResilienceConfig.from_env(environ))
