#!/usr/bin/env python3
"""Counter-breaker and run-budget wiring for the loop (M0-T079; D-023 item 1).

`circuit_breakers.py` owns what a breaker IS - the tallies, the thresholds, the
OK/WARN/TRIP verdicts. This module owns how the LOOP feeds them: which counters
one production event ticks, how the per-day window gets its UTC day, when a
forward counts as progress, how the tallies reach durable storage, and when the
owner-set run budget says a run may not take another step.

It is separate from `loop.py` on purpose. The loop is the S7 wiring - the states,
the transitions, the prompt path - and these are bookkeeping decisions that
change for entirely different reasons (a new counter, a new budget dimension).
They are free functions taking exactly what they need, so each is testable
without building a loop, and `SupervisedLoop` keeps thin delegating methods so
every existing caller is unchanged.

Qualifying evidence (AD-093 Section 0A.10): a requirement explicitly listed in
owner directive D-023 (item 1), plus the reproduced defect
`circuit_breakers.py`'s own Phase-1 note recorded - the counters were complete
and tested, and nothing fed them.

THE EVENT MAP, one line per counter, and the loop site each is ticked from:

    supervisor_cycles_per_task    once per cycle, before any provider call
    model_calls_per_task/_day     each provider dispatch (worker AND reviewer)
    external_writes_per_task/_day each outbound send (the loop's own external
                                  write; modeled effects in github_flow.py are
                                  that task's to wire)
    restart_attempts              each seam relaunch
    consecutive_invalid_outputs   a unit with no valid checkpoint, or a reviewer
                                  answer that never validated
    consecutive_revision_loops    a REVISE decision (any other decision resets it)
    consecutive_no_progress       a cycle whose checkpoint id repeats the last
    claude_runs_per_task          already wired before this task (unchanged)
    codex_reviews_per_checkpoint  already wired before this task (unchanged)
    consecutive_hard_denies       wired in broker.py (unchanged)

A tick that TRIPS is always a synchronous pause BEFORE the counted thing
happens, never after it - the discipline the pre-existing `claude_runs_per_task`
tick already used at the top of a cycle.
"""
from __future__ import annotations

from typing import Any

from .circuit_breakers import PER_DAY_COUNTERS

#: The one decision label that is NOT forward progress. See `record_progress`.
REVISE = "REVISE"

#: The counters a REVISE forward may clear. Deliberately excludes
#: `consecutive_revision_loops`, which is the thing a revision forward measures.
_REVISE_SAFE_RESETS = ("consecutive_invalid_outputs", "consecutive_hard_denies",
                       "consecutive_no_progress")


def tick(breakers: Any, name: str) -> tuple[bool, str]:
    """Record one counter tick. Returns (tripped, message)."""
    if breakers is None:
        return False, ""
    verdict = breakers.record(name)
    if verdict.tripped:
        return True, verdict.message
    if verdict.warning:
        return False, verdict.message
    return False, ""


def tick_daily(breakers: Any, run_budget: Any, name: str) -> tuple[bool, str]:
    """Tick a PER-DAY counter with the day taken from the injected clock seam.

    `record_daily` refuses to accrue against an unknown day (fail closed), so
    with no run budget - and therefore no clock seam - the per-day counters are
    not ticked at all rather than ticked against a guessed date. Their per-TASK
    companions still bound the same event either way, so the loop is never left
    with an unbounded one.
    """
    if breakers is None or run_budget is None:
        return False, ""
    verdict = breakers.record_daily(name, run_budget.utc_day())
    if verdict.tripped:
        return True, verdict.message
    if verdict.warning:
        return False, verdict.message
    return False, ""


def tick_event(breakers: Any, run_budget: Any, *names: str) -> tuple[bool, str, str]:
    """Tick every counter ONE event moves. Returns (tripped, name, message).

    All of them are ticked, then the FIRST trip is reported: a second limit that
    also fired must not go unrecorded just because an earlier one reported first.
    """
    tripped_name, tripped_message, warning = "", "", ""
    for name in names:
        if name in PER_DAY_COUNTERS:
            tripped, message = tick_daily(breakers, run_budget, name)
        else:
            tripped, message = tick(breakers, name)
        if tripped and not tripped_name:
            tripped_name, tripped_message = name, message
        elif message and not warning:
            warning = message
    if tripped_name:
        return True, tripped_name, tripped_message
    return False, "", warning


def reset(breakers: Any, name: str) -> None:
    """Clear one counter's streak. A no-op when no breakers are wired."""
    if breakers is not None:
        breakers.reset(name)


def persist(breakers: Any, run_budget: Any) -> None:
    """Persist the counter tallies with the durable run budget.

    This is the crash-resume half of the wiring: without it a resumed run
    rebuilds `CircuitBreakers` from the immutable limits and silently earns back
    every model call, external write, restart, and livelock allowance it had
    already spent.
    """
    if breakers is None or run_budget is None:
        return
    run_budget.persist_counters(breakers.snapshot(), day=run_budget.utc_day())


def record_progress(breakers: Any, decision: Any) -> None:
    """A completed forward is progress - unless it is another REVISE.

    `CircuitBreakers.record_progress` clears every RESET_ON_PROGRESS counter,
    which is right for a CONTINUE: the reviewer accepted the unit and the run
    moved on. It is wrong for a REVISE, because a revision forward is exactly
    the step `consecutive_revision_loops` exists to count - clearing the counter
    on the very act it measures is why that breaker could never accumulate no
    matter how many revisions a run did. So a REVISE clears the counters that
    are genuinely unrelated to it and leaves its own alone.

    Accepts the decision object or just its label, because the cross-process
    resume path has only the label the parked record kept.
    """
    if breakers is None:
        return
    label = (decision if isinstance(decision, str)
             else str(getattr(decision, "decision", "") or ""))
    if label == REVISE:
        for name in _REVISE_SAFE_RESETS:
            breakers.reset(name)
        return
    breakers.record_progress()


def budget_stop(run_budget: Any, *, audit: Any = None, run_id: str = "") -> str:
    """`budget_exhausted` when the owner-set budget is spent, else "".

    Call this ONLY between cycles. S11.2 is absolute: an in-flight unit is never
    interrupted for pressure, and a budget is pressure. Detecting exhaustion at
    the seam leaves the finished unit's work intact and closes the durable record
    with the machine-readable exit reason.

    With no ledger - and with an owner budget of None, which is the default and
    means unlimited (D-023-R037) - this returns "" every time. An unlimited run
    has no timer that can stop it.
    """
    if run_budget is None:
        return ""
    run_budget.observe()
    verdict = run_budget.check()
    if not verdict.exhausted:
        return ""
    run_budget.finalize(exit_reason="budget_exhausted", detail=verdict.reason)
    if audit is not None:
        audit.append(
            "run_budget_exhausted", run_id=run_id, policy_result="budget_exhausted",
            detail={"dimension": verdict.dimension,
                    "elapsed_seconds": verdict.elapsed_seconds,
                    "wall_clock_seconds": verdict.wall_clock_seconds,
                    "exhausted_counters": list(verdict.exhausted_counters),
                    "note": "the owner-set budget is spent; the run stops between "
                            "cycles with no unit in flight and clears no durable "
                            "hold, flag, deadline, or approval"})
    return "budget_exhausted"
