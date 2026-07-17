"""Structured metrics/log hooks for the resilience layer (task M1-T009 item H).

Observability-ready and secret-free BY CONTRACT: event fields carry only
identifiers, counters, durations, states, and request URLs (tokens travel in
headers, never in URLs - accepted M1-T002 policy). Callers must never pass
header values, the app token, or response bodies as fields; the default
logging hook JSON-encodes fields so hostile strings cannot inject log lines
(same policy as the connector's payload-only logging, M1-T002 G5 F5).

Event vocabulary emitted by the layer (closed, documented set):

- ``cache_hit`` / ``cache_miss`` / ``cache_expired`` / ``cache_evicted`` /
  ``cache_store``
- ``retry_scheduled`` (jittered backoff) / ``retry_after_honored`` (exact) /
  ``retry_after_exceeds_cap``
- ``breaker_transition`` / ``breaker_fast_reject``
- ``lkg_served`` / ``lkg_unavailable`` / ``lkg_too_old``
- ``budget_consumed`` / ``budget_exceeded``
- ``fetch_success`` / ``fetch_failure``
"""

from __future__ import annotations

import json
import logging
import threading
from collections import Counter
from collections.abc import Callable

__all__ = ["MetricsHook", "ResilienceMetrics", "logging_metrics_hook"]

logger = logging.getLogger("app.resilience.metrics")

# Hook contract: (event_name, fields) -> None. Fields are JSON-serializable
# scalars/lists only; never secrets (see module docstring).
MetricsHook = Callable[[str, dict], None]


def logging_metrics_hook(event: str, fields: dict) -> None:
    """Default hook: one structured log line per event.

    ``json.dumps`` escapes control characters, so untrusted-derived strings
    (e.g. sanitized error codes) can never break the log line format.
    """
    logger.info(
        "resilience_metric event=%s fields=%s",
        event,
        json.dumps(fields, sort_keys=True, default=str),
    )


class ResilienceMetrics:
    """Thread-safe event counter + hook dispatcher.

    Counters make cache hit ratio, breaker transitions, and budget
    consumption assertable in deterministic tests and exposable to a future
    connector-health endpoint (PRD section 25) without a metrics backend.
    """

    def __init__(self, hook: MetricsHook = logging_metrics_hook) -> None:
        self._hook = hook
        self._lock = threading.Lock()
        self._counters: Counter[str] = Counter()

    def emit(self, event: str, **fields: object) -> None:
        with self._lock:
            self._counters[event] += 1
        self._hook(event, dict(fields))

    def count(self, event: str) -> int:
        with self._lock:
            return self._counters[event]

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            return dict(self._counters)

    def cache_hit_ratio(self) -> float | None:
        """Hits / (hits + misses); ``None`` before any cache lookup."""
        with self._lock:
            hits = self._counters["cache_hit"]
            misses = self._counters["cache_miss"]
        total = hits + misses
        if total == 0:
            return None
        return hits / total
