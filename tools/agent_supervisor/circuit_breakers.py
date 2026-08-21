#!/usr/bin/env python3
"""Configurable, fail-closed circuit breakers (D-007 S13.8, S7).

Breakers are SUPERVISOR-enforced, never prompt-enforced: no model is asked to
respect a limit, and no model can raise one. Two shapes:

* **counters** - monotonically increasing tallies (Claude runs, Codex reviews,
  model calls and external writes per task AND per day, consecutive revision
  loops, consecutive hard denies, consecutive no-progress cycles). Some reset on
  evidence of progress; the per-day counters reset when the UTC day rolls
  (`record_daily`).
* **gauges** - observed resource readings compared to a ceiling or floor
  (process count, free disk, retained-log/review-packet size, CPU percent,
  resident memory).

Each evaluation returns one of three verdicts:

    OK    below the warning line
    WARN  at or above `warn_ratio` of the limit -> a NOTIFY event; never blocks
    TRIP  at or above the hard limit -> a synchronous pause (S4.5)

Unknown breaker names raise rather than passing silently: a typo must not
disable a safety limit. Limits come from the immutable, manifest-covered
`config.toml`, so a runtime model change can never move one (S3.1).

Wiring status (was the Phase 1 scope note; corrected by M0-T079, D-023 item 1).
The breakers and their bookkeeping have always been complete and tested. What was
missing was the wiring, and the note said so:

    "WIRING them to real resource sampling (CPU/memory readings, spend ceilings)
    and to the notification surface is Phase 2/3; the gauge API is ready for it."

M0-T041 (AS-3) wired the GAUGES to live resource sampling. M0-T079 wired every
remaining COUNTER to its real production event site in the loop -
`supervisor_cycles_per_task` per cycle, `model_calls_per_task`/`_per_day` on each
provider dispatch, `external_writes_per_task`/`_per_day` on each outbound send,
`restart_attempts` on each seam relaunch, and the three livelock counters at
their semantic sites - and made the tallies survive a crash through
`restore()` + the durable run-budget record (`run_budget.py`). Spend ceilings
remain out of scope: no priced-usage signal exists on this build to sample.
"""
from __future__ import annotations

import dataclasses
from typing import Mapping

from .config import Limits

OK = "OK"
WARN = "WARN"
TRIP = "TRIP"

#: counter name -> the `Limits` field holding its hard threshold.
#:
#: V1.1 note (G3 finding B-4, reviewed): the first mapping is imprecise on BOTH
#: sides and is DOCUMENTED here rather than renamed. What the counter actually
#: measures: Claude units dispatched by ONE supervisor invocation (a fresh
#: `CircuitBreakers` is built per `start`, and the counter never resets), i.e.
#: units-per-run - not per-task, and not CLI "turns" (turns are the intra-unit
#: `--max-turns` bound). Renaming `max_claude_turns_per_run` would invalidate
#: every owner-placed, manifest-covered config.toml (S3.1: limits are immutable
#: config), and renaming the counter would silently decouple historical audit
#: events from new ones; both renames are config/audit-schema changes for a
#: separately owner-approved version, so V1.1 records the semantics instead.
#: `codex_reviews_per_checkpoint` DOES measure what its name claims as of V1.1:
#: the loop resets it on every newly received checkpoint (correction B-4).
COUNTER_LIMITS: Mapping[str, str] = {
    "claude_runs_per_task": "max_claude_turns_per_run",
    "codex_reviews_per_checkpoint": "max_codex_reviews_per_checkpoint",
    "supervisor_cycles_per_task": "max_supervisor_cycles_per_task",
    "model_calls_per_task": "max_model_calls_per_task",
    "external_writes_per_task": "max_external_writes_per_task",
    "model_calls_per_day": "max_model_calls_per_day",
    "external_writes_per_day": "max_external_writes_per_day",
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
    "cpu_percent": ("max_cpu_percent", "max"),
    "memory_bytes": ("max_memory_bytes", "max"),
}

#: Counters whose bound is PER DAY, not per run. They live in COUNTER_LIMITS
#: like every other counter (so evaluate/tripped/snapshot include them), but are
#: ticked through `record_daily`, which rolls the day window first so the bound
#: is genuinely daily. The day is supplied by the caller (a UTC date string) so
#: the breaker never reads the clock itself and stays deterministic.
PER_DAY_COUNTERS: frozenset[str] = frozenset({
    "model_calls_per_day", "external_writes_per_day",
})


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
        #: The UTC calendar day the per-day counters are currently accruing
        #: against. `None` until the first per-day tick. Crossing to a new day
        #: resets every per-day counter before the tick (see `record_daily`).
        self._day: str | None = None

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

    def record_daily(self, name: str, day: str, amount: int = 1) -> BreakerVerdict:
        """Tick a PER-DAY counter, rolling the day window first, then evaluate.

        `day` is a caller-supplied UTC calendar date (e.g. "2026-08-05"). The
        supervisor injects it so the breaker never reads the clock and stays
        deterministic and replayable. Crossing to a new day resets every per-day
        counter to zero BEFORE this tick, so the bound is genuinely per-day and
        not a cumulative-per-run tally. Fail closed: a per-day tick without a
        real date, or against a counter that is not per-day, raises rather than
        silently passing - a typo or a missing date must never disable the cap.
        """
        if name not in PER_DAY_COUNTERS:
            raise BreakerError(
                f"{name!r} is not a per-day counter; per-day counters: "
                f"{sorted(PER_DAY_COUNTERS)}")
        self._roll_day(day)
        return self.record(name, amount)

    def _roll_day(self, day: str) -> None:
        """Reset the per-day counters when the supplied UTC day advances."""
        if not isinstance(day, str) or not day.strip():
            raise BreakerError(
                "a per-day counter tick requires a non-empty UTC date string; "
                "refusing to accrue against an unknown day (fail closed)")
        if self._day is None:
            self._day = day
        elif day != self._day:
            self._day = day
            for counter in PER_DAY_COUNTERS:
                self._counters[counter] = 0

    def restore(self, counters: Mapping[str, int], *, day: str = "") -> None:
        """Reconcile these breakers with tallies persisted before a discontinuity.

        M0-T079 (D-023 item 1): a crash-resume rebuilds `CircuitBreakers` from
        the immutable limits, which used to hand the resumed run a full fresh
        allowance of model calls, external writes, restarts, and livelock
        tolerance. The durable run-budget record carries the tallies forward and
        this puts them back.

        Monotonic on purpose: each counter is raised to the HIGHER of its current
        and persisted value, never lowered. A restore can therefore only ever
        tighten a breaker, so neither a crash, a partial write, nor a replayed
        older snapshot can give the run back an allowance it has already spent.
        `day` restores the per-day window the tallies were accrued against, so a
        resume on the SAME UTC day keeps them and the first tick on a NEW day
        rolls them exactly as `record_daily` always has. An unknown counter name
        raises, like every other addressed-by-name path here.
        """
        for name, value in counters.items():
            self._require_counter(name)
            amount = int(value)
            if amount < 0:
                raise BreakerError(
                    f"counter {name!r} cannot be restored to a negative tally {amount}")
            self._counters[name] = max(self._counters[name], amount)
        if day:
            self._roll_day(day)

    @property
    def day(self) -> str | None:
        """The UTC day the per-day counters are currently accruing against."""
        return self._day

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
