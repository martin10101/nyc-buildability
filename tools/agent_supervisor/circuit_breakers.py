#!/usr/bin/env python3
"""Configurable, fail-closed circuit breakers (D-007 S13.8, S7).

Breakers are SUPERVISOR-enforced, never prompt-enforced: no model is asked to
respect a limit, and no model can raise one. Two shapes:

* **counters** - monotonically increasing tallies (Claude runs, Codex reviews,
  model calls, external writes, consecutive revision loops, consecutive hard
  denies, consecutive no-progress cycles). Some reset on evidence of progress.
* **gauges** - observed resource readings compared to a ceiling or floor
  (process count, free disk).

Each evaluation returns one of three verdicts:

    OK    below the warning line
    WARN  at or above `warn_ratio` of the limit -> a NOTIFY event; never blocks
    TRIP  at or above the hard limit -> a synchronous pause (S4.5)

Unknown breaker names raise rather than passing silently: a typo must not
disable a safety limit. Limits come from the immutable, manifest-covered
`config.toml`, so a runtime model change can never move one (S3.1).

Phase 1 scope note: the breakers and their bookkeeping are complete and tested.
WIRING them to real resource sampling (CPU/memory readings, spend ceilings) and
to the notification surface is Phase 2/3; the gauge API is ready for it.
"""
from __future__ import annotations

import dataclasses
from typing import Mapping

from .config import Limits

OK = "OK"
WARN = "WARN"
TRIP = "TRIP"

#: counter name -> the `Limits` field holding its hard threshold.
COUNTER_LIMITS: Mapping[str, str] = {
    "claude_runs_per_task": "max_claude_turns_per_run",
    "codex_reviews_per_checkpoint": "max_codex_reviews_per_checkpoint",
    "supervisor_cycles_per_task": "max_supervisor_cycles_per_task",
    "model_calls_per_task": "max_model_calls_per_task",
    "external_writes_per_task": "max_external_writes_per_task",
    "restart_attempts": "max_restart_attempts",
    "consecutive_invalid_outputs": "max_consecutive_invalid_outputs",
    "consecutive_revision_loops": "max_consecutive_revision_loops",
    "consecutive_hard_denies": "max_consecutive_hard_denies",
    "consecutive_no_progress": "max_consecutive_no_progress",
}

#: Counters that reset when the run demonstrates progress.
RESET_ON_PROGRESS: frozenset[str] = frozenset({
    "consecutive_invalid_outputs", "consecutive_revision_loops",
    "consecutive_hard_denies", "consecutive_no_progress",
})

#: gauge name -> (`Limits` field, comparison). "max" trips at/above, "min" at/below.
GAUGE_LIMITS: Mapping[str, tuple[str, str]] = {
    "process_count": ("max_processes", "max"),
    "free_disk_bytes": ("min_free_disk_bytes", "min"),
    "retained_log_bytes": ("max_retained_log_bytes", "max"),
    "review_packet_bytes": ("max_review_packet_bytes", "max"),
}


class BreakerError(Exception):
    """An unknown breaker was addressed. Never silently ignored."""


@dataclasses.dataclass(frozen=True)
class BreakerVerdict:
    name: str
    verdict: str
    value: int | float
    limit: int | float
    message: str = ""

    @property
    def tripped(self) -> bool:
        return self.verdict == TRIP

    @property
    def warning(self) -> bool:
        return self.verdict == WARN


class CircuitBreakers:
    """Counter and gauge breakers derived from the immutable controller limits."""

    def __init__(self, limits: Limits) -> None:
        self.limits = limits
        self._counters: dict[str, int] = {name: 0 for name in COUNTER_LIMITS}

    # -- counters ------------------------------------------------------------

    def value(self, name: str) -> int:
        self._require_counter(name)
        return self._counters[name]

    def record(self, name: str, amount: int = 1) -> BreakerVerdict:
        """Increment a counter and evaluate it."""
        self._require_counter(name)
        if amount < 0:
            raise BreakerError(f"counter {name!r} cannot be decremented")
        self._counters[name] += amount
        return self.evaluate(name)

    def reset(self, name: str) -> None:
        self._require_counter(name)
        self._counters[name] = 0

    def record_progress(self) -> None:
        """Evidence of real progress clears the livelock counters (S13.8)."""
        for name in RESET_ON_PROGRESS:
            self._counters[name] = 0

    def evaluate(self, name: str) -> BreakerVerdict:
        self._require_counter(name)
        limit = int(getattr(self.limits, COUNTER_LIMITS[name]))
        current = self._counters[name]
        if current >= limit:
            return BreakerVerdict(
                name, TRIP, current, limit,
                f"{name} reached its hard limit ({current} >= {limit}); this is a "
                f"synchronous pause, not a notification")
        if current >= max(1, int(limit * self.limits.warn_ratio)):
            return BreakerVerdict(
                name, WARN, current, limit,
                f"{name} is at {current} of {limit}; NOTIFY only, the loop continues")
        return BreakerVerdict(name, OK, current, limit)

    def _require_counter(self, name: str) -> None:
        if name not in self._counters:
            raise BreakerError(
                f"unknown counter {name!r}; known counters: {sorted(self._counters)}")

    # -- gauges --------------------------------------------------------------

    def gauge(self, name: str, observed: int | float) -> BreakerVerdict:
        """Evaluate an observed resource reading against its ceiling or floor."""
        if name not in GAUGE_LIMITS:
            raise BreakerError(
                f"unknown gauge {name!r}; known gauges: {sorted(GAUGE_LIMITS)}")
        field, direction = GAUGE_LIMITS[name]
        limit = getattr(self.limits, field)
        if direction == "max":
            if observed >= limit:
                return BreakerVerdict(name, TRIP, observed, limit,
                                      f"{name} {observed} reached the ceiling {limit}")
            if observed >= limit * self.limits.warn_ratio:
                return BreakerVerdict(name, WARN, observed, limit,
                                      f"{name} {observed} is approaching {limit}")
            return BreakerVerdict(name, OK, observed, limit)

        if observed <= limit:
            return BreakerVerdict(name, TRIP, observed, limit,
                                  f"{name} {observed} fell to or below the floor {limit}")
        if observed <= limit / max(self.limits.warn_ratio, 0.01):
            return BreakerVerdict(name, WARN, observed, limit,
                                  f"{name} {observed} is approaching the floor {limit}")
        return BreakerVerdict(name, OK, observed, limit)

    # -- reporting -----------------------------------------------------------

    def snapshot(self) -> dict[str, int]:
        return dict(self._counters)

    def tripped(self) -> tuple[BreakerVerdict, ...]:
        return tuple(v for v in (self.evaluate(n) for n in self._counters) if v.tripped)
