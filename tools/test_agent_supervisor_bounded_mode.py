#!/usr/bin/env python3
"""The bounded unattended mode: budgets, breakers, refusals (M0-T079, D-023 item 1).

Qualifying evidence (AD-093 Section 0A.10): a requirement explicitly listed in
owner directive D-023 (item 1, amended by D-023-R037), plus two reproduced
defects - the `limited-auto` traceback refusal and the circuit breakers whose own
module note said the wiring was not done.

Every "Claude" and every "Codex" here is an in-process fake, every clock is a
list-driven fake, and no provider, network, or real repository is involved.

What is proven:

* **an unlimited run has no timer at all.** No constant in this build caps a run
  length (D-023-R037), the CLI's wall-clock input has no default, and a run whose
  fake clock jumps ten years is never stopped by the budget.
* **a budgeted run stops deterministically**, at a seam, with a machine-readable
  exit reason, and clears no durable hold on the way out.
* **a crash-resume can never reset, extend, or shrink the run's own bounds**:
  the persisted start instant and budget win, elapsed seconds are clamped to a
  durable high-water mark so a backwards clock buys nothing, a relaunch naming
  different bounds is refused, and restored counters only ever rise.
* **every circuit breaker ticks from its real production event site**, proven by
  driving the REAL loop against fakes and watching each counter move.
* **refusals are machine meaningful**: one documented outcome and one stable
  nonzero exit code each, an unknown outcome raises rather than passing, and the
  bounded mode is OFF unless the owner enables it for that exact launch.
"""
from __future__ import annotations

import contextlib
import dataclasses
import io
import json
import pathlib
import re
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import loop as lp  # noqa: E402
from tools.agent_supervisor import policy as pol  # noqa: E402
from tools.agent_supervisor import refusals  # noqa: E402
from tools.agent_supervisor import run_budget as rb  # noqa: E402
from tools.agent_supervisor import state_machine as sm  # noqa: E402
from tools.agent_supervisor.audit_log import AuditLog  # noqa: E402
from tools.agent_supervisor.circuit_breakers import (  # noqa: E402
    COUNTER_LIMITS,
    BreakerError,
    CircuitBreakers,
)
from tools.agent_supervisor.claude_runner import RunnerConfig, RunResult  # noqa: E402
from tools.agent_supervisor.codex_reviewer import (  # noqa: E402
    ReviewOutcome,
    map_decision_to_tier,
)
from tools.agent_supervisor.config import Limits  # noqa: E402
from tools.agent_supervisor.durable_state import DurableJournal  # noqa: E402
from tools.agent_supervisor.models import (  # noqa: E402
    ClaudeCheckpoint,
    CodexDecision,
    digest_of,
)
from tools.agent_supervisor.state_machine import StateMachine  # noqa: E402

PACKAGE = REPO / "tools" / "agent_supervisor"

# --------------------------------------------------------------------------
# Fakes (same shape as tools/test_agent_supervisor_loop.py)
# --------------------------------------------------------------------------

_FAKE_LAUNCH_CONFIG = RunnerConfig(executable="fake-claude")


class FakeClock:
    """The ONE injected clock seam, driven by the test instead of by the OS."""

    def __init__(self, start: float = 1_770_000_000.0) -> None:
        self.now = float(start)
        self.reads = 0

    def __call__(self) -> float:
        self.reads += 1
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += float(seconds)


def checkpoint(**overrides) -> ClaudeCheckpoint:
    data = dict(
        schema_version="1.0.0", run_id="run-bounded", checkpoint_id="cp-1",
        task_id="M0-T079", claude_session_id="sess-1", status="UNIT_COMPLETE",
        summary="unit complete", starting_sha="a" * 40, current_sha="b" * 40,
        branch="task/M0-T079-bounded-mode", worktree="/repo/wt",
        proposed_next_action="continue", usage="unknown", context_pressure="unknown")
    data.update(overrides)
    return ClaudeCheckpoint(**data)


def decision(**overrides) -> CodexDecision:
    data = dict(
        schema_version="1.0.0", decision="CONTINUE", reviewed_task_id="M0-T079",
        reviewed_checkpoint_id="cp-1", verified_repo_head="b" * 40,
        verified_origin_main="a" * 40, model_used="fake-review-model",
        next_claude_prompt="Do the next bounded unit.")
    data.update(overrides)
    return CodexDecision(**data)


def run_result(cp: ClaudeCheckpoint | None = None, **overrides) -> RunResult:
    data = dict(argv=("fake",), returncode=0, duration_seconds=0.1,
                session_id="sess-1", checkpoint=cp if cp is not None else checkpoint(),
                containment="job_object")
    data.update(overrides)
    return RunResult(**data)


def outcome(dec: CodexDecision | None = None, **overrides) -> ReviewOutcome:
    actual = dec if dec is not None else decision()
    data = dict(decision=actual, model_used="fake-review-model",
                selection_digest="sel", attempts=1,
                decision_digest=digest_of(actual.to_dict()),
                tier=map_decision_to_tier(actual))
    data.update(overrides)
    return ReviewOutcome(**data)


class FakeRunner:
    """Returns scripted `RunResult`s and can advance the injected clock."""

    def __init__(self, *results: RunResult, model: str = "",
                 clock: FakeClock | None = None, seconds_per_unit: float = 0.0) -> None:
        self.results = list(results) or [run_result()]
        self.prompts: list[str] = []
        self.models: list[str] = []
        self.clock = clock
        self.seconds_per_unit = seconds_per_unit
        self.config = dataclasses.replace(_FAKE_LAUNCH_CONFIG, model=model,
                                          expected_model=model)

    def with_model(self, model: str) -> "FakeRunner":
        clone = FakeRunner(*self.results, model=model, clock=self.clock,
                           seconds_per_unit=self.seconds_per_unit)
        clone.prompts = self.prompts
        clone.models = self.models
        return clone

    def run_unit(self, prompt: str, **_kwargs) -> RunResult:
        self.prompts.append(prompt)
        self.models.append(self.config.model)
        if self.clock is not None and self.seconds_per_unit:
            self.clock.advance(self.seconds_per_unit)
        return self.results[min(len(self.prompts) - 1, len(self.results) - 1)]


class FakeReviewer:
    def __init__(self, *outcomes: ReviewOutcome) -> None:
        self.outcomes = list(outcomes) or [outcome()]
        self.packets: list[dict] = []

    def review(self, packet, **_kwargs) -> ReviewOutcome:
        self.packets.append(dict(packet))
        return self.outcomes[min(len(self.packets) - 1, len(self.outcomes) - 1)]


# --------------------------------------------------------------------------
# Base
# --------------------------------------------------------------------------


class BoundedTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.repo = self.tmp / "repo"
        (self.repo / "tools").mkdir(parents=True)
        self.db = self.tmp / "journal.sqlite3"
        self.journal = DurableJournal(self.db).open()
        self.addCleanup(self.journal.close)
        self.audit = AuditLog(self.tmp / "audit.jsonl", fsync=False)
        self.run_id = "run-bounded"
        self.machine = StateMachine(self.journal, self.audit, self.run_id)
        self.clock = FakeClock()
        self.authority = pol.TaskAuthority.from_packet(
            {"task_id": "M0-T079",
             "allowed_paths": ["tools/agent_supervisor/**",
                               "tools/test_agent_supervisor_*.py"],
             "forbidden_paths": [".github/**", ".claude/**"],
             "status": "in_progress"},
            repo_root=str(self.repo), worktree=str(self.repo),
            branch="task/M0-T079-bounded-mode", stage="phase4")

    def at_preflight(self) -> None:
        self.machine.transition(sm.PREFLIGHT, "start_command")

    def ledger(self, *, wall_clock_seconds: float | None = None,
               limits: Limits | None = None,
               journal=None, run_id: str = "") -> rb.RunBudgetLedger:
        budget = rb.RunBudget.from_limits(limits or Limits(),
                                          wall_clock_seconds=wall_clock_seconds)
        led = rb.RunBudgetLedger(journal or self.journal, run_id=run_id or self.run_id,
                                 budget=budget, clock=self.clock, audit=self.audit)
        led.start()
        return led

    def build(self, *, mode: str = "supervised", runner=None, reviewer=None,
              breakers=None, run_budget=None, max_cycles: int = 4,
              approval_gate=None, owner_enabled: bool = False,
              **config_overrides) -> lp.SupervisedLoop:
        config = lp.LoopConfig(
            mode=mode, task_id="M0-T079", stage="phase4",
            allowed_paths=self.authority.allowed_paths,
            stop_conditions=("no bypass flags",),
            max_cycles=max_cycles, owner_touch_budget=8,
            owner_enabled_bounded_auto=owner_enabled, **config_overrides)
        return lp.SupervisedLoop(
            config=config, journal=self.journal, audit=self.audit,
            machine=self.machine, authority=self.authority,
            runner=runner or FakeRunner(run_result()),
            reviewer=reviewer or FakeReviewer(outcome()),
            run_id=self.run_id, breakers=breakers, run_budget=run_budget,
            approval_gate=approval_gate or (lambda _d, _p: mode == "supervised"))


# --------------------------------------------------------------------------
# 1. Unlimited runs have NO timer (owner amendment D-023-R037)
# --------------------------------------------------------------------------


class UnlimitedRunTests(BoundedTestBase):
    def test_the_default_budget_is_unlimited(self) -> None:
        budget = rb.RunBudget.from_limits(Limits())
        self.assertIsNone(budget.wall_clock_seconds)
        self.assertTrue(budget.unlimited)
        self.assertIs(rb.UNLIMITED, None)

    def test_an_unlimited_run_is_never_exhausted_however_long_it_runs(self) -> None:
        led = self.ledger(wall_clock_seconds=None)
        for jump in (1.0, 3_600.0, 86_400.0, 315_360_000.0):  # up to ten years
            self.clock.advance(jump)
            verdict = led.check()
            self.assertFalse(verdict.exhausted,
                             f"an unlimited run was stopped after {verdict.elapsed_seconds}s")
            self.assertTrue(verdict.unlimited)
            self.assertIsNone(verdict.remaining_seconds)

    def test_an_unlimited_loop_run_is_never_stopped_by_the_budget(self) -> None:
        self.at_preflight()
        runner = FakeRunner(run_result(), clock=self.clock,
                            seconds_per_unit=90 * 24 * 3600.0)
        led = self.ledger(wall_clock_seconds=None)
        loop = self.build(runner=runner, run_budget=led, max_cycles=3)
        run = loop.run("first unit")
        self.assertNotEqual(run.stopped, "budget_exhausted")
        self.assertEqual(run.stopped, "max_cycles_reached")
        self.assertTrue(run.run_budget["unlimited"])
        self.assertGreater(run.run_budget["elapsed_seconds"], 86_400.0)

    #: C12 (G3 M-2): the name says "anywhere", so the scan covers every module
    #: that could hold a ceiling, and the pattern catches the shapes the original
    #: regex missed - a leading underscore, `DEFAULT_*`, and `*_CAP`.
    CEILING_PATTERN = (
        r"^_?(?:MAX|MAXIMUM|DEFAULT|ABSOLUTE|HARD)_[A-Z_]*"
        r"(?:RUN|WALL|DURATION|SECONDS|CLOCK|STOP)[A-Z_]*"
        r"|^_?[A-Z_]*(?:RUN|WALL|DURATION|CLOCK)[A-Z_]*"
        r"(?:MAX|MAXIMUM|CEILING|CAP|LIMIT)")

    def test_no_hardcoded_maximum_run_length_exists_anywhere(self) -> None:
        """D-023-R037 at the source level: no ceiling constant, no default.

        A comment promising "no maximum" is worth nothing if a constant somewhere
        quietly caps the run, so this reads the source - all four modules that
        could hold one, not just `run_budget.py` (C12) - and the CLI's wall-clock
        argument must default to None.
        """
        for name in ("run_budget.py", "loop.py", "cli.py", "loop_breakers.py"):
            source = (PACKAGE / name).read_text(encoding="utf-8")
            found = re.findall(self.CEILING_PATTERN + r"\s*[:=]", source,
                               flags=re.MULTILINE)
            self.assertEqual(found, [],
                             f"a hardcoded run-length ceiling appeared in {name}: {found}")

    def test_the_ceiling_scan_actually_catches_a_ceiling(self) -> None:
        """A guard nobody probed is a guard nobody can trust (C12 / G3 M-2)."""
        for name in ("MAX_RUN_SECONDS", "_MAX_RUN_SECONDS", "RUN_CEILING",
                     "ABSOLUTE_RUN_CAP", "DEFAULT_WALL_CLOCK_SECONDS",
                     "HARD_STOP_SECONDS", "MAX_WALL_CLOCK", "RUN_LENGTH_MAX",
                     "_RUN_DURATION_LIMIT"):
            with self.subTest(name=name):
                self.assertTrue(
                    re.findall(self.CEILING_PATTERN + r"\s*[:=]",
                               f"{name} = 36000\n", flags=re.MULTILINE),
                    f"the scan would not have caught {name}")

    def test_the_ceiling_scan_does_not_flag_ordinary_names(self) -> None:
        for name in ("RUN_BUDGET_KEY", "MAX_CYCLES", "COUNTER_LIMITS",
                     "BUDGET_RECORD_SCHEMA_VERSION", "DEFAULT_OWNER_TOUCH_BUDGET"):
            with self.subTest(name=name):
                self.assertEqual(
                    re.findall(self.CEILING_PATTERN + r"\s*[:=]",
                               f"{name} = 1\n", flags=re.MULTILINE), [])

        from tools.agent_supervisor import cli

        parser = cli.build_parser()
        actions = {a.dest: a for a in parser._actions}
        start = [a for a in parser._subparsers._group_actions[0].choices.items()
                 if a[0] == "start"][0][1]
        wall = {a.dest: a for a in start._actions}["run_wall_clock_seconds"]
        self.assertIsNone(wall.default,
                          "the owner wall-clock budget must have NO default; omitting it "
                          "means unlimited")
        self.assertIn("UNLIMITED", wall.help)

    def test_a_zero_budget_is_refused_rather_than_read_as_unlimited(self) -> None:
        for bad in (0, -1, -0.5):
            with self.subTest(value=bad):
                with self.assertRaises(rb.BudgetError) as ctx:
                    rb.RunBudget(wall_clock_seconds=bad)
                self.assertEqual(ctx.exception.code, "bad_wall_clock")

    def test_a_non_numeric_or_infinite_budget_is_refused(self) -> None:
        for bad in ("600", True, float("inf"), float("nan")):
            with self.subTest(value=bad):
                with self.assertRaises(rb.BudgetError):
                    rb.RunBudget(wall_clock_seconds=bad)

    def test_an_enormous_owner_budget_is_accepted_without_clamping(self) -> None:
        huge = 10.0 ** 9  # ~31 years; the owner may set whatever they want
        budget = rb.RunBudget(wall_clock_seconds=huge)
        self.assertEqual(budget.wall_clock_seconds, huge)


# --------------------------------------------------------------------------
# 2. Budgeted runs stop deterministically
# --------------------------------------------------------------------------


class BudgetExhaustionTests(BoundedTestBase):
    def test_exhaustion_is_exact_and_repeatable(self) -> None:
        led = self.ledger(wall_clock_seconds=100.0)
        self.clock.advance(99.999)
        self.assertFalse(led.check().exhausted)
        self.clock.advance(0.001)
        verdict = led.check()
        self.assertTrue(verdict.exhausted)
        self.assertEqual(verdict.dimension, "wall_clock")
        self.assertEqual(verdict.reason_code, "budget_exhausted")
        # Deterministic: asking again gives the same answer, not a drifting one.
        self.assertEqual(led.check().to_dict(), verdict.to_dict())

    def test_a_budgeted_loop_run_stops_between_cycles_with_an_exit_reason(self) -> None:
        self.at_preflight()
        runner = FakeRunner(run_result(), clock=self.clock, seconds_per_unit=40.0)
        led = self.ledger(wall_clock_seconds=100.0)
        loop = self.build(runner=runner, run_budget=led, max_cycles=10)
        run = loop.run("first unit")
        self.assertEqual(run.stopped, "budget_exhausted")
        # Three units would have crossed 100s; the run stopped at the seam AFTER
        # the unit that crossed it, never mid-unit.
        self.assertEqual(len(runner.prompts), 3)
        self.assertEqual(run.run_budget["exit_reason"], "budget_exhausted")
        self.assertTrue(run.run_budget["exhausted"])
        record = rb.load_record(self.journal, self.run_id)
        self.assertEqual(record["exit_reason"], "budget_exhausted")
        self.assertTrue(record["stopped_at_utc"])

    def test_the_operator_facing_refusal_names_run_id_for_both_dimensions(self) -> None:
        """D1 (G3 R-2): the remedy has to be where the operator actually reads.

        `check()` wrote `--run-id` into `BudgetVerdict.reason` and thence into the
        durable `exit_detail`, but `report()` dropped `exit_detail` and
        `dispatched_run_refusal`'s message was static - so the escape hatch
        existed everywhere except the refusal.
        """
        from tools.agent_supervisor.start_gate import dispatched_run_refusal

        for dimension, limits, wall in (("wall_clock", Limits(), 100.0),
                                        ("counter", Limits(max_model_calls_per_task=2),
                                         None)):
            with self.subTest(dimension=dimension):
                self.setUp()
                led = self.ledger(wall_clock_seconds=wall, limits=limits)
                if dimension == "wall_clock":
                    self.clock.advance(200.0)
                else:
                    led.persist_counters({"model_calls_per_task": 2},
                                         day=rb.utc_day_for(self.clock.now))
                verdict = led.check()
                self.assertTrue(verdict.exhausted)
                self.assertEqual(verdict.dimension, dimension)
                led.finalize(exit_reason="budget_exhausted", detail=verdict.reason)

                report = led.report()
                self.assertEqual(report["exhausted_dimension"], dimension)
                self.assertIn("--run-id", report["exit_detail"])

                item = dispatched_run_refusal(
                    "shadow", {"stopped": "budget_exhausted", "run_budget": report,
                               "cycles": []})
                self.assertEqual(item.outcome, refusals.BUDGET_EXHAUSTED)
                self.assertIn("--run-id", item.message)
                self.assertEqual(item.detail["remedy"], "--run-id <fresh-id>")
                self.assertIn("--run-id", "\n".join(item.lines()))

    def test_a_zero_cycle_budget_stop_is_not_reported_as_dispatched(self) -> None:
        """D1: a run refused at the seam before its first cycle ran nothing."""
        self.at_preflight()
        led = self.ledger(wall_clock_seconds=10.0)
        self.clock.advance(11.0)
        runner = FakeRunner(run_result())
        loop = self.build(runner=runner, run_budget=led, max_cycles=4)
        run = loop.run("first unit")
        self.assertEqual(run.stopped, "budget_exhausted")
        self.assertEqual(run.cycles, ())
        self.assertEqual(runner.prompts, [], "no unit was dispatched")
        self.assertEqual(run.provider_calls, 0)

    def test_exhaustion_is_recorded_in_the_audit_chain(self) -> None:
        self.at_preflight()
        runner = FakeRunner(run_result(), clock=self.clock, seconds_per_unit=40.0)
        led = self.ledger(wall_clock_seconds=30.0)
        loop = self.build(runner=runner, run_budget=led, max_cycles=4)
        loop.run("first unit")
        events = [record["event_type"] for record in self.audit.read_all()]
        self.assertIn("run_budget_exhausted", events)

    def test_exhaustion_clears_no_durable_flag_hold_or_approval(self) -> None:
        """Safe cleanup means closing the record - not releasing a safety flag."""
        from tools.agent_supervisor.resume_scheduler import (
            EMERGENCY_STOP_KEY,
            MANUAL_PAUSE_KEY,
            RESUME_NOT_BEFORE_KEY,
        )

        self.journal.set_state(MANUAL_PAUSE_KEY, True)
        self.journal.set_state(RESUME_NOT_BEFORE_KEY, "2099-01-01T00:00:00.000Z")
        led = self.ledger(wall_clock_seconds=1.0)
        self.clock.advance(5.0)
        led.finalize(exit_reason="budget_exhausted")
        self.assertIs(self.journal.get_state(MANUAL_PAUSE_KEY), True)
        self.assertEqual(self.journal.get_state(RESUME_NOT_BEFORE_KEY),
                         "2099-01-01T00:00:00.000Z")
        self.assertFalse(bool(self.journal.get_state(EMERGENCY_STOP_KEY, False)))

    def test_an_exhausted_counter_exhausts_the_budget_too(self) -> None:
        led = self.ledger(wall_clock_seconds=None,
                          limits=Limits(max_model_calls_per_task=2))
        led.persist_counters({"model_calls_per_task": 2}, day="2026-08-21")
        verdict = led.check()
        self.assertTrue(verdict.exhausted)
        self.assertEqual(verdict.dimension, "counter")
        self.assertIn("model_calls_per_task", verdict.exhausted_counters)

    def test_a_resumed_run_whose_budget_is_already_spent_makes_no_provider_call(self) -> None:
        self.at_preflight()
        led = self.ledger(wall_clock_seconds=10.0)
        self.clock.advance(11.0)
        runner = FakeRunner(run_result())
        loop = self.build(runner=runner, run_budget=led, max_cycles=4)
        run = loop.run("first unit")
        self.assertEqual(run.stopped, "budget_exhausted")
        self.assertEqual(run.provider_calls, 0)
        self.assertEqual(runner.prompts, [])


# --------------------------------------------------------------------------
# 3. A crash-resume cannot reset, extend, or shrink anything
# --------------------------------------------------------------------------


class CrashResumeBudgetTests(BoundedTestBase):
    def reopen(self, *, wall_clock_seconds: float | None = 100.0,
               limits: Limits | None = None) -> rb.RunBudgetLedger:
        """Simulate a crash by building a FRESH ledger over the same journal."""
        budget = rb.RunBudget.from_limits(limits or Limits(),
                                          wall_clock_seconds=wall_clock_seconds)
        led = rb.RunBudgetLedger(self.journal, run_id=self.run_id, budget=budget,
                                 clock=self.clock)
        led.start()
        return led

    def test_a_resume_reloads_the_original_start_instant(self) -> None:
        first = self.ledger(wall_clock_seconds=100.0)
        started = first.record()["started_at_epoch"]
        self.clock.advance(60.0)
        first.observe()

        resumed = self.reopen()
        self.assertTrue(resumed.resumed)
        self.assertEqual(resumed.record()["started_at_epoch"], started)
        # Elapsed CONTINUES from the original start; it does not restart at zero.
        self.assertAlmostEqual(resumed.elapsed(), 60.0, places=3)
        self.assertEqual(resumed.record()["resumes"], 1)

    def test_a_resume_cannot_reset_elapsed_time(self) -> None:
        led = self.ledger(wall_clock_seconds=100.0)
        self.clock.advance(90.0)
        led.observe()
        for _ in range(3):
            led = self.reopen()
            self.assertGreaterEqual(led.elapsed(), 90.0)
        self.clock.advance(10.0)
        self.assertTrue(self.reopen().check().exhausted)

    def test_a_backwards_clock_cannot_shrink_elapsed_and_is_recorded(self) -> None:
        """The high-water clamp: an NTP correction never gives time back.

        The honest limit is asserted too - a backwards clock PAUSES accrual
        until the clock catches up, and each such observation is counted in the
        durable record so the anomaly is visible rather than silent.
        """
        led = self.ledger(wall_clock_seconds=100.0)
        self.clock.advance(95.0)
        self.assertAlmostEqual(led.observe(), 95.0, places=3)

        self.clock.advance(-90.0)  # the wall clock jumps backwards
        self.assertAlmostEqual(led.elapsed(), 95.0, places=3, msg="elapsed shrank")
        self.assertAlmostEqual(led.observe(), 95.0, places=3)
        self.assertEqual(led.record()["backwards_clock_observations"], 1)

        resumed = self.reopen()
        self.assertAlmostEqual(resumed.elapsed(), 95.0, places=3)
        self.assertFalse(resumed.check().exhausted)
        self.clock.advance(95.0)  # the clock catches up and passes the budget
        self.assertTrue(resumed.check().exhausted)

    def test_a_relaunch_naming_a_different_budget_is_refused(self) -> None:
        self.ledger(wall_clock_seconds=100.0)
        for attempt in (1_000_000.0, 1.0, None):
            with self.subTest(budget=attempt):
                with self.assertRaises(rb.BudgetError) as ctx:
                    self.reopen(wall_clock_seconds=attempt)
                self.assertEqual(ctx.exception.code, "budget_conflict")

    def test_a_relaunch_cannot_widen_a_counter_bound_either(self) -> None:
        self.ledger(wall_clock_seconds=None, limits=Limits(max_model_calls_per_task=5))
        with self.assertRaises(rb.BudgetError) as ctx:
            self.reopen(wall_clock_seconds=None,
                        limits=Limits(max_model_calls_per_task=5000))
        self.assertEqual(ctx.exception.code, "budget_conflict")

    def test_persisted_counters_never_go_down(self) -> None:
        led = self.ledger(wall_clock_seconds=None)
        led.persist_counters({"model_calls_per_task": 7}, day="2026-08-21")
        led.persist_counters({"model_calls_per_task": 2}, day="2026-08-21")
        self.assertEqual(led.record()["counters"]["model_calls_per_task"], 7)

    def test_restore_reconciles_a_fresh_breaker_set_upward_only(self) -> None:
        led = self.ledger(wall_clock_seconds=None)
        today = rb.utc_day_for(self.clock.now)
        led.persist_counters({"model_calls_per_task": 7, "restart_attempts": 2},
                             day=today)
        breakers = CircuitBreakers(Limits())
        breakers.record("restart_attempts", 3)  # already higher than the record
        led.restore_counters(breakers)
        snapshot = breakers.snapshot()
        self.assertEqual(snapshot["model_calls_per_task"], 7)
        self.assertEqual(snapshot["restart_attempts"], 3, "restore must never lower")
        self.assertEqual(breakers.day, today)

    def test_a_same_day_resume_restores_the_per_day_tally(self) -> None:
        led = self.ledger(wall_clock_seconds=None)
        today = rb.utc_day_for(self.clock.now)
        led.persist_counters({"model_calls_per_day": 1500}, day=today)
        breakers = CircuitBreakers(Limits())
        led.restore_counters(breakers)
        self.assertEqual(breakers.value("model_calls_per_day"), 1500,
                         "the day has not rolled, so the tally is still today's")

    def test_a_per_day_tally_from_an_earlier_day_is_not_restored(self) -> None:
        """C4: a daily cap is daily. Yesterday's peak is not today's spend."""
        led = self.ledger(wall_clock_seconds=None)
        led.persist_counters({"model_calls_per_day": 1500, "model_calls_per_task": 9},
                             day="2026-02-01")
        self.clock.advance(48 * 3600.0)  # the UTC day rolls
        self.assertTrue(led.stale_day())
        breakers = CircuitBreakers(Limits())
        led.restore_counters(breakers)
        self.assertEqual(breakers.value("model_calls_per_day"), 0)
        self.assertEqual(breakers.value("model_calls_per_task"), 9,
                         "per-RUN tallies bound the run, not the day, and still restore")

    def test_an_exhausted_per_day_counter_stops_exhausting_when_the_day_rolls(self) -> None:
        """C4 (G5 I2): a daily cap silently became a permanent cap on that run id."""
        led = self.ledger(wall_clock_seconds=None,
                          limits=Limits(max_model_calls_per_day=2000))
        led.persist_counters({"model_calls_per_day": 2000},
                             day=rb.utc_day_for(self.clock.now))
        self.assertTrue(led.check().exhausted)
        self.assertIn("model_calls_per_day", led.check().exhausted_counters)

        self.clock.advance(24 * 3600.0)  # a new UTC day
        verdict = led.check()
        self.assertFalse(verdict.exhausted,
                         "the daily window rolled; the peak is history, not spend")
        self.assertEqual(verdict.exhausted_counters, ())

    def test_a_rolled_day_replaces_the_persisted_per_day_peak(self) -> None:
        led = self.ledger(wall_clock_seconds=None)
        led.persist_counters({"model_calls_per_day": 2000}, day="2026-02-01")
        self.clock.advance(24 * 3600.0)
        led.persist_counters({"model_calls_per_day": 1},
                             day=rb.utc_day_for(self.clock.now))
        self.assertEqual(led.record()["counters"]["model_calls_per_day"], 1,
                         "max() against yesterday's peak is what made a daily cap "
                         "permanent")

    def test_a_per_run_tally_is_never_rolled_by_a_new_day(self) -> None:
        led = self.ledger(wall_clock_seconds=None)
        led.persist_counters({"model_calls_per_task": 40}, day="2026-02-01")
        self.clock.advance(72 * 3600.0)
        led.persist_counters({"model_calls_per_task": 2},
                             day=rb.utc_day_for(self.clock.now))
        self.assertEqual(led.record()["counters"]["model_calls_per_task"], 40)

    def test_restore_refuses_an_unknown_counter_name(self) -> None:
        breakers = CircuitBreakers(Limits())
        with self.assertRaises(BreakerError):
            breakers.restore({"model_calls_per_taks": 1})
        with self.assertRaises(BreakerError):
            breakers.restore({"model_calls_per_task": -1})

    def test_a_resumed_loop_re_enters_with_the_tallies_it_left(self) -> None:
        """The end-to-end crash-resume proof, through the REAL loop.

        A first run spends model calls; the process "dies"; a second run over the
        same journal rebuilds `CircuitBreakers` from the immutable limits, and the
        restore puts the spent tallies back rather than handing out a fresh
        allowance.
        """
        limits = Limits(max_model_calls_per_task=4)
        self.at_preflight()
        first_breakers = CircuitBreakers(limits)
        first = self.build(runner=FakeRunner(run_result()),
                           breakers=first_breakers, max_cycles=1,
                           run_budget=self.ledger(limits=limits))
        first.run("first unit")
        spent = first_breakers.snapshot()["model_calls_per_task"]
        self.assertEqual(spent, 2, "one cycle dispatches the worker and the reviewer")

        second_breakers = CircuitBreakers(limits)
        self.assertEqual(second_breakers.snapshot()["model_calls_per_task"], 0)
        resumed_ledger = rb.RunBudgetLedger(
            self.journal, run_id=self.run_id,
            budget=rb.RunBudget.from_limits(limits), clock=self.clock)
        resumed_ledger.start()
        resumed_ledger.restore_counters(second_breakers)
        self.assertEqual(second_breakers.snapshot()["model_calls_per_task"], spent)

    def test_the_budget_record_survives_reopening_the_database_file(self) -> None:
        """Durability, not just in-memory state: the journal file is reopened."""
        led = self.ledger(wall_clock_seconds=250.0)
        started = led.record()["started_at_epoch"]
        led.persist_counters({"external_writes_per_task": 3}, day="2026-08-21")
        self.journal.close()

        reopened = DurableJournal(self.db).open()
        try:
            record = rb.load_record(reopened, self.run_id)
        finally:
            reopened.close()
        self.assertEqual(record["started_at_epoch"], started)
        self.assertEqual(record["budget"]["wall_clock_seconds"], 250.0)
        self.assertEqual(record["counters"]["external_writes_per_task"], 3)


# --------------------------------------------------------------------------
# 4. Every breaker ticks from its real production event site
# --------------------------------------------------------------------------


class BreakerWiringTests(BoundedTestBase):
    """The Phase-1 note in circuit_breakers.py said the wiring was not done.

    These drive the REAL loop against fakes and watch each counter move at the
    place the counted thing actually happens.
    """

    def loop_with(self, limits: Limits, **kwargs) -> tuple[lp.SupervisedLoop,
                                                           CircuitBreakers]:
        breakers = CircuitBreakers(limits)
        led = self.ledger(limits=limits)
        return self.build(breakers=breakers, run_budget=led, **kwargs), breakers

    def test_supervisor_cycles_per_task_ticks_once_per_cycle(self) -> None:
        self.at_preflight()
        loop, breakers = self.loop_with(Limits(max_supervisor_cycles_per_task=2),
                                        max_cycles=5)
        run = loop.run("first unit")
        self.assertEqual(breakers.value("supervisor_cycles_per_task"), 2)
        self.assertEqual(run.stopped, "circuit_breaker_hard_threshold")
        self.assertIn("supervisor_cycles_per_task", run.cycles[-1].reason)

    def test_model_calls_tick_at_the_worker_dispatch_before_the_call(self) -> None:
        self.at_preflight()
        runner = FakeRunner(run_result())
        loop, breakers = self.loop_with(Limits(max_model_calls_per_task=1),
                                        runner=runner, max_cycles=2)
        run = loop.run("first unit")
        self.assertEqual(breakers.value("model_calls_per_task"), 1)
        self.assertEqual(run.stopped, "circuit_breaker_hard_threshold")
        self.assertEqual(runner.prompts, [],
                         "the breaker must trip BEFORE the provider call it counts")
        self.assertEqual(run.provider_calls, 0)

    def test_model_calls_tick_at_the_reviewer_dispatch_too(self) -> None:
        self.at_preflight()
        reviewer = FakeReviewer(outcome())
        runner = FakeRunner(run_result())
        loop, breakers = self.loop_with(Limits(max_model_calls_per_task=2),
                                        runner=runner, reviewer=reviewer, max_cycles=2)
        run = loop.run("first unit")
        self.assertEqual(breakers.value("model_calls_per_task"), 2)
        self.assertEqual(len(runner.prompts), 1, "the worker call DID happen")
        self.assertEqual(reviewer.packets, [], "the review call did NOT")
        self.assertEqual(run.stopped, "circuit_breaker_hard_threshold")

    def test_the_per_day_model_call_counter_ticks_with_the_injected_day(self) -> None:
        self.at_preflight()
        loop, breakers = self.loop_with(Limits(max_model_calls_per_day=2), max_cycles=1)
        loop.run("first unit")
        self.assertEqual(breakers.value("model_calls_per_day"), 2)
        self.assertEqual(breakers.day, rb.utc_day_for(self.clock.now))

    def test_external_writes_tick_at_the_outbound_send(self) -> None:
        self.at_preflight()
        loop, breakers = self.loop_with(Limits(max_external_writes_per_task=2),
                                        max_cycles=4)
        run = loop.run("first unit")
        self.assertEqual(breakers.value("external_writes_per_task"), 2)
        self.assertEqual(breakers.value("external_writes_per_day"), 2)
        # The FIRST forward went out; the second was refused before the send.
        self.assertEqual(len(run.forwarded_message_ids), 1)
        self.assertEqual(run.stopped, "circuit_breaker_hard_threshold")
        self.assertEqual(self.journal.get_state("pending_prompt/" + self.run_id, {})
                         .get("consumed"), True)

    def test_restart_attempts_tick_at_a_seam_relaunch(self) -> None:
        self.at_preflight()
        runner = FakeRunner(run_result(model_mismatch=True,
                                       mismatch_detail="reported another model"),
                            run_result())
        loop, breakers = self.loop_with(Limits(max_restart_attempts=1),
                                        runner=runner, max_cycles=3)
        run = loop.run("first unit")
        self.assertEqual(len(run.rotations), 1, "the seam really did relaunch")
        self.assertEqual(breakers.value("restart_attempts"), 1)
        self.assertEqual(run.stopped, "circuit_breaker_hard_threshold")

    def test_consecutive_invalid_outputs_ticks_on_a_unit_with_no_checkpoint(self) -> None:
        self.at_preflight()
        runner = FakeRunner(run_result(checkpoint=None, returncode=1,
                                       checkpoint_error="no final checkpoint object"))
        loop, breakers = self.loop_with(Limits(max_consecutive_invalid_outputs=1),
                                        runner=runner, max_cycles=2)
        run = loop.run("first unit")
        self.assertEqual(breakers.value("consecutive_invalid_outputs"), 1)
        self.assertEqual(run.stopped, "no_valid_checkpoint")
        self.assertIn("consecutive_invalid_outputs_tripped", run.cycles[-1].notes)

    def test_a_valid_checkpoint_clears_the_invalid_output_streak(self) -> None:
        self.at_preflight()
        runner = FakeRunner(
            run_result(checkpoint=None, returncode=1, checkpoint_error="bad"),
            run_result())
        breakers = CircuitBreakers(Limits(max_consecutive_invalid_outputs=5))
        loop = self.build(runner=runner, breakers=breakers, max_cycles=1,
                          run_budget=self.ledger())
        loop.run("first unit")
        self.assertEqual(breakers.value("consecutive_invalid_outputs"), 1)
        # A second, healthy cycle from a fresh loop over the same breakers.
        self.machine.transition(sm.PREFLIGHT, "owner_cleared_pause")
        healthy = self.build(runner=FakeRunner(run_result()), breakers=breakers,
                             max_cycles=1)
        healthy.run_cycle("second unit", cycle=1)
        self.assertEqual(breakers.value("consecutive_invalid_outputs"), 0)

    def test_consecutive_revision_loops_tick_on_revise_and_reset_on_continue(self) -> None:
        self.at_preflight()
        revise = outcome(decision(decision="REVISE",
                                  next_claude_prompt="Fix the finding and re-report."))
        loop, breakers = self.loop_with(Limits(max_consecutive_revision_loops=2),
                                        reviewer=FakeReviewer(revise), max_cycles=5)
        run = loop.run("first unit")
        self.assertEqual(breakers.value("consecutive_revision_loops"), 2)
        self.assertEqual(run.stopped, "circuit_breaker_hard_threshold")
        self.assertEqual(len(run.forwarded_message_ids), 1,
                         "the trip refuses the SECOND revision forward")

        # A CONTINUE ends the streak rather than extending it.
        breakers.reset("consecutive_revision_loops")
        breakers.record("consecutive_revision_loops")
        self.machine.transition(sm.PREFLIGHT, "cycle_closed")
        continuing = self.build(runner=FakeRunner(run_result()), breakers=breakers,
                                max_cycles=1)
        continuing.run_cycle("next unit", cycle=1)
        self.assertEqual(breakers.value("consecutive_revision_loops"), 0)

    def test_consecutive_no_progress_ticks_when_the_checkpoint_id_repeats(self) -> None:
        self.at_preflight()
        runner = FakeRunner(run_result())  # the same checkpoint id every unit
        loop, breakers = self.loop_with(Limits(max_consecutive_no_progress=1),
                                        runner=runner, max_cycles=4)
        run = loop.run("first unit")
        self.assertEqual(breakers.value("consecutive_no_progress"), 1)
        self.assertEqual(run.stopped, "circuit_breaker_hard_threshold")
        self.assertEqual(self.machine.current_state, sm.PAUSED_RECOVERY)

    def test_a_new_checkpoint_id_is_progress(self) -> None:
        self.at_preflight()
        runner = FakeRunner(run_result(checkpoint(checkpoint_id="cp-1")),
                            run_result(checkpoint(checkpoint_id="cp-2")),
                            run_result(checkpoint(checkpoint_id="cp-3")))
        loop, breakers = self.loop_with(Limits(max_consecutive_no_progress=1),
                                        runner=runner, max_cycles=3)
        run = loop.run("first unit")
        self.assertEqual(breakers.value("consecutive_no_progress"), 0)
        self.assertEqual(run.stopped, "max_cycles_reached")

    def test_every_counter_in_the_registry_has_a_wired_event_site(self) -> None:
        """No counter is left as a tested tally that nothing feeds.

        `claude_runs_per_task` and `codex_reviews_per_checkpoint` were wired
        before this task; `consecutive_hard_denies` is wired in broker.py. The
        rest are wired in loop.py by M0-T079. This asserts that EVERY name in the
        registry is referenced by a production wiring site, so adding a counter
        without wiring it fails here rather than in production.
        """
        wiring = ((PACKAGE / "loop.py").read_text(encoding="utf-8")
                  + (PACKAGE / "broker.py").read_text(encoding="utf-8"))
        unwired = [name for name in COUNTER_LIMITS if f'"{name}"' not in wiring]
        self.assertEqual(unwired, [], f"counters with no production event site: {unwired}")

    def test_breaker_tallies_are_persisted_with_the_run_budget(self) -> None:
        self.at_preflight()
        led = self.ledger()
        breakers = CircuitBreakers(Limits())
        loop = self.build(breakers=breakers, run_budget=led, max_cycles=1)
        loop.run("first unit")
        persisted = rb.load_record(self.journal, self.run_id)["counters"]
        self.assertEqual(persisted["model_calls_per_task"], 2)
        self.assertEqual(persisted["supervisor_cycles_per_task"], 1)
        self.assertEqual(persisted["external_writes_per_task"], 1)


# --------------------------------------------------------------------------
# 5. Machine-meaningful refusals
# --------------------------------------------------------------------------


class RefusalContractTests(unittest.TestCase):
    def test_every_documented_outcome_has_a_distinct_nonzero_exit_code(self) -> None:
        codes = [refusals.EXIT_CODES[name] for name in refusals.OUTCOMES]
        self.assertEqual(len(set(codes)), len(codes), "exit codes must be distinct")
        for code in codes:
            self.assertGreater(code, 1,
                               "a refusal code must not collide with 0/1 or the "
                               "interpreter's own 2")

    def test_the_seven_required_outcomes_are_all_defined(self) -> None:
        self.assertEqual(
            set(refusals.OUTCOMES),
            {"halted", "unsafe", "unsupported_platform", "stale_state",
             "approval_required", "budget_exhausted", "refused_mode"})

    def test_an_unknown_outcome_raises_rather_than_becoming_success(self) -> None:
        with self.assertRaises(refusals.RefusalError):
            refusals.exit_code_for("probably_fine")
        with self.assertRaises(refusals.RefusalError):
            refusals.refusal("probably_fine", reason_code="x", message="y")

    def test_a_refusal_without_a_reason_code_is_refused(self) -> None:
        with self.assertRaises(refusals.RefusalError):
            refusals.refusal(refusals.UNSAFE, reason_code="", message="something")

    def test_the_payload_is_a_complete_machine_readable_document(self) -> None:
        item = refusals.refusal(refusals.BUDGET_EXHAUSTED,
                                reason_code="budget_exhausted",
                                message="the owner-set budget is spent",
                                detail={"elapsed_seconds": 36_000})
        payload = item.to_dict()
        for key in ("schema_version", "refused", "outcome", "exit_code",
                    "reason_code", "message", "detail", "at_utc"):
            self.assertIn(key, payload)
        self.assertEqual(payload["exit_code"], 15)
        self.assertTrue(payload["refused"])
        json.dumps(payload)  # must be serializable as-is

    def test_emit_writes_the_document_and_returns_the_exit_code(self) -> None:
        item = refusals.refusal(refusals.HALTED, reason_code="halt_unsafe",
                                message="the reviewer halted the run")
        stream = io.StringIO()
        code = refusals.emit(item, as_json=True, stream=stream)
        self.assertEqual(code, 10)
        self.assertEqual(json.loads(stream.getvalue())["outcome"], refusals.HALTED)
        text = io.StringIO()
        refusals.emit(item, as_json=False, stream=text)
        self.assertIn("REFUSED (halted, exit 10)", text.getvalue())
        self.assertNotIn("Traceback", text.getvalue())

    def test_an_unrecognized_recovery_verdict_fails_closed_to_unsafe(self) -> None:
        self.assertEqual(refusals.outcome_for_recovery("SOMETHING_NEW"), refusals.UNSAFE)
        self.assertEqual(refusals.outcome_for_recovery("UNSAFE_OR_DRIFTED"),
                         refusals.UNSAFE)
        self.assertEqual(refusals.outcome_for_recovery("AMBIGUOUS_EFFECT"),
                         refusals.STALE_STATE)
        self.assertEqual(
            refusals.outcome_for_recovery("SAFE_CHECKPOINT", "safe_but_forbidden"),
            refusals.APPROVAL_REQUIRED)

    def test_an_unattended_park_is_a_refusal_but_a_clean_finish_is_not(self) -> None:
        self.assertEqual(refusals.outcome_for_unattended_stop("ask_blocking"),
                         refusals.APPROVAL_REQUIRED)
        self.assertEqual(refusals.outcome_for_unattended_stop("halt_unsafe"),
                         refusals.HALTED)
        self.assertEqual(refusals.outcome_for_unattended_stop("budget_exhausted"),
                         refusals.BUDGET_EXHAUSTED)
        for clean in ("max_cycles_reached", "stage_complete", ""):
            self.assertIsNone(refusals.outcome_for_unattended_stop(clean))


# --------------------------------------------------------------------------
# 6. The bounded mode is OFF unless the owner enables THIS launch
# --------------------------------------------------------------------------


class OwnerGateTests(BoundedTestBase):
    def test_limited_auto_is_still_refused_by_name_without_the_owner_enable(self) -> None:
        with self.assertRaises(lp.LimitedAutoRefused) as ctx:
            lp.LoopConfig(mode="limited-auto", task_id="M0-T079", stage="phase4")
        self.assertEqual(ctx.exception.code, "limited_auto_refused")
        self.assertIn("separate explicit owner activation", ctx.exception.message)

    def test_the_runnable_mode_list_still_excludes_the_bounded_mode(self) -> None:
        self.assertEqual(lp.RUNNABLE_MODES, (lp.MODE_SHADOW, lp.MODE_SUPERVISED))
        self.assertNotIn(lp.MODE_LIMITED_AUTO, lp.RUNNABLE_MODES)
        self.assertEqual(lp.OWNER_GATED_MODES, (lp.MODE_LIMITED_AUTO,))

    def test_the_owner_enable_cannot_be_attached_to_another_mode(self) -> None:
        for mode in lp.RUNNABLE_MODES:
            with self.subTest(mode=mode):
                with self.assertRaises(lp.LoopError) as ctx:
                    lp.LoopConfig(mode=mode, task_id="t", stage="s",
                                  owner_enabled_bounded_auto=True)
                self.assertEqual(ctx.exception.code, "owner_enable_without_gated_mode")

    def test_no_config_default_reaches_the_bounded_mode(self) -> None:
        """The enable is a LAUNCH input; the immutable config cannot carry it."""
        from tools.agent_supervisor import config as cfg

        fields = {f.name for f in dataclasses.fields(cfg.ControllerConfig)}
        self.assertNotIn("owner_enabled_bounded_auto", fields)
        source = (PACKAGE / "config.py").read_text(encoding="utf-8")
        self.assertNotIn("owner_enabled_bounded_auto", source)

    def test_an_owner_enabled_bounded_run_forwards_without_an_approval(self) -> None:
        """With the enable, the mode really works - it is implemented, not a stub."""
        self.at_preflight()
        led = self.ledger(wall_clock_seconds=None)
        breakers = CircuitBreakers(Limits())
        loop = self.build(mode="limited-auto", owner_enabled=True, run_budget=led,
                          breakers=breakers, max_cycles=1,
                          runner=FakeRunner(run_result()),
                          approval_gate=lambda _d, _p: False)
        run = loop.run("first unit")
        self.assertEqual(run.stopped, "max_cycles_reached")
        self.assertEqual(len(run.forwarded_message_ids), 1)
        self.assertTrue(run.to_dict()["limited_auto_enabled"])
        # It took the S7 table's own AUTO edge and never parked for an owner.
        path = run.cycles[0].path
        self.assertIn(sm.FORWARD_PROMPT, path)
        self.assertNotIn(sm.WAIT_FOR_OWNER, path)
        triggers = [t.trigger for t in self.journal.transitions()]
        self.assertIn("tier_auto", triggers)

    def test_a_bounded_run_still_stops_for_every_non_auto_outcome(self) -> None:
        """The unattended mode may do LESS than supervised, never more."""
        self.at_preflight()
        halting = outcome(decision(decision="HALT_UNSAFE",
                                   blocking_findings=["a secret in the diff"],
                                   next_claude_prompt=""))
        loop = self.build(mode="limited-auto", owner_enabled=True,
                          run_budget=self.ledger(), breakers=CircuitBreakers(Limits()),
                          reviewer=FakeReviewer(halting), max_cycles=2)
        run = loop.run("first unit")
        self.assertEqual(run.stopped, "halt_unsafe")
        self.assertEqual(run.final_state, sm.HALTED)
        self.assertEqual(run.forwarded_message_ids, ())


# --------------------------------------------------------------------------
# 7. The CLI surface
# --------------------------------------------------------------------------


class CliBoundedModeTests(BoundedTestBase):
    def run_cli(self, *argv: str) -> tuple[int, str, str]:
        from tools.agent_supervisor import cli

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main([*argv, "--checkout", str(self.repo),
                             "--runtime-base", str(self.tmp / "runtime")])
        return code, out.getvalue(), err.getvalue()

    def test_limited_auto_without_the_enable_is_a_structured_refusal(self) -> None:
        code, out, err = self.run_cli("start", "--mode", "limited-auto", "--json")
        self.assertEqual(code, refusals.EXIT_CODES[refusals.REFUSED_MODE])
        payload = json.loads(out)
        self.assertEqual(payload["outcome"], refusals.REFUSED_MODE)
        self.assertEqual(payload["reason_code"], "limited_auto_not_enabled")
        self.assertNotIn("Traceback", out + err)

    def test_the_refusal_reaches_stderr_without_json(self) -> None:
        code, out, err = self.run_cli("start", "--mode", "limited-auto")
        self.assertEqual(code, refusals.EXIT_CODES[refusals.REFUSED_MODE])
        self.assertIn("REFUSED (refused_mode, exit 16)", err)
        self.assertEqual(out, "")

    def test_the_bounded_refusal_happens_before_any_input_check(self) -> None:
        """Nothing is opened, probed, or contacted: it is refused by name first."""
        code, out, _ = self.run_cli("start", "--mode", "limited-auto", "--json")
        payload = json.loads(out)
        self.assertEqual(code, 16)
        self.assertNotIn("missing_inputs", payload)
        self.assertNotIn("recovery", payload)

    def test_a_refused_bounded_launch_is_sealed_in_the_audit_chain(self) -> None:
        """C6 (G5 I5): an attempted activation under the R033 hold leaves a trace.

        The gate deliberately runs before the lock and the journal, which also
        meant the attempt was recorded nowhere at all - the one event a security
        reviewer would most want in a tamper-evident log.
        """
        from tools.agent_supervisor.durable_state import runtime_dir_for

        self.run_cli("start", "--mode", "limited-auto", "--json")
        path = (runtime_dir_for(self.repo, base=str(self.tmp / "runtime"))
                / "audit.jsonl")
        self.assertTrue(path.exists(), "the refusal must reach the audit log")
        records = [json.loads(line) for line in
                   path.read_text(encoding="utf-8").splitlines() if line.strip()]
        refused = [r for r in records
                   if r["event_type"] == "bounded_mode_launch_refused"]
        self.assertEqual(len(refused), 1)
        self.assertEqual(refused[0]["policy_result"], "limited_auto_not_enabled")
        self.assertEqual(refused[0]["decision"], "refuse")


# --------------------------------------------------------------------------
# 8. Corrections C1-C12 (consolidated review round)
# --------------------------------------------------------------------------


class BudgetSelfResetTests(BoundedTestBase):
    """C1 (G5 M1): a run could reset its own budget by nulling one JSON field.

    `start()` took the resume branch only on `isinstance(existing, Mapping) and
    existing.get("started_at_epoch") is not None`; every other shape fell through
    to a FRESH start that minted a new start instant, zeroed the elapsed
    high-water mark, emptied the tallies, and never reached the budget_conflict
    check. The supervised worker runs as the same OS user and can write the
    journal, so one field edit bought an unlimited run.
    """

    def spend(self, *, wall_clock_seconds: float = 3600.0) -> rb.RunBudgetLedger:
        """A run 3000s into a 3600s budget, with tallies spent."""
        led = self.ledger(wall_clock_seconds=wall_clock_seconds)
        self.clock.advance(3000.0)
        led.observe()
        led.persist_counters({"model_calls_per_task": 40},
                             day=rb.utc_day_for(self.clock.now))
        return led

    def reopen(self, *, wall_clock_seconds: float | None = 3600.0) -> rb.RunBudgetLedger:
        led = rb.RunBudgetLedger(
            self.journal, run_id=self.run_id, clock=self.clock, audit=self.audit,
            budget=rb.RunBudget.from_limits(Limits(),
                                            wall_clock_seconds=wall_clock_seconds))
        led.start()
        return led

    def tamper(self, mutate) -> None:
        record = self.journal.get_state(f"run_budget/{self.run_id}")
        self.journal.set_state(f"run_budget/{self.run_id}", mutate(dict(record)))

    def test_control_an_honest_relaunch_with_new_bounds_is_refused(self) -> None:
        self.spend()
        with self.assertRaises(rb.BudgetError) as ctx:
            self.reopen(wall_clock_seconds=36_000.0)
        self.assertEqual(ctx.exception.code, "budget_conflict")

    def test_a_nulled_start_instant_refuses_instead_of_minting_a_fresh_budget(self) -> None:
        """The exact proven attack: one field to null, and the clock reset."""
        self.spend()
        self.tamper(lambda r: {**r, "started_at_epoch": None})
        with self.assertRaises(rb.BudgetError) as ctx:
            self.reopen(wall_clock_seconds=36_000.0)
        self.assertEqual(ctx.exception.code, "budget_record_malformed")
        # And the record it refused is untouched: no fresh start was minted.
        record = rb.load_record(self.journal, self.run_id)
        self.assertEqual(record["budget"]["wall_clock_seconds"], 3600.0)
        self.assertGreaterEqual(record["elapsed_high_water_seconds"], 3000.0)
        self.assertEqual(record["counters"]["model_calls_per_task"], 40)

    def test_a_deleted_record_refuses_rather_than_starting_over(self) -> None:
        self.spend()
        self.journal.set_state(f"run_budget/{self.run_id}", None)
        with self.assertRaises(rb.BudgetError) as ctx:
            self.reopen(wall_clock_seconds=36_000.0)
        self.assertEqual(ctx.exception.code, "budget_record_unreadable")

    def test_a_non_record_payload_refuses(self) -> None:
        for payload in ("wiped", 0, [], 12.5, True):
            with self.subTest(payload=payload):
                self.setUp()
                self.spend()
                self.journal.set_state(f"run_budget/{self.run_id}", payload)
                with self.assertRaises(rb.BudgetError) as ctx:
                    self.reopen(wall_clock_seconds=36_000.0)
                self.assertIn(ctx.exception.code,
                              ("budget_record_unreadable", "budget_record_malformed"))

    def test_a_non_numeric_or_impossible_start_instant_refuses(self) -> None:
        for value in ("2026-01-01", 0, -5.0, [], {}, True):
            with self.subTest(value=value):
                self.setUp()
                self.spend()
                self.tamper(lambda r, v=value: {**r, "started_at_epoch": v})
                with self.assertRaises(rb.BudgetError) as ctx:
                    self.reopen()
                self.assertEqual(ctx.exception.code, "budget_record_malformed")

    def test_a_rewritten_budget_block_is_caught_by_its_own_recorded_digest(self) -> None:
        """Rewriting the budget under the record does not become 'the persisted budget'."""
        self.spend()
        self.tamper(lambda r: {**r, "budget": {**r["budget"],
                                               "wall_clock_seconds": 36_000.0}})
        with self.assertRaises(rb.BudgetError) as ctx:
            self.reopen(wall_clock_seconds=36_000.0)
        self.assertEqual(ctx.exception.code, "budget_record_tampered")

    def test_a_record_whose_budget_digest_was_DELETED_refuses(self) -> None:
        """D3 (G5 free hardening): the cheapest raw-DB rewrite of the lot.

        The tamper check used to read `if recorded_digest and recorded_digest !=
        ...`, so dropping the field skipped it entirely and the rewritten budget
        block sailed into the conflict comparison as "the persisted budget".
        `_first_launch` always writes the digest, so a legitimate record can never
        lack one.
        """
        self.spend()
        self.tamper(lambda r: {k: v for k, v in r.items() if k != "budget_digest"})
        with self.assertRaises(rb.BudgetError) as ctx:
            self.reopen()
        self.assertEqual(ctx.exception.code, "budget_record_malformed")

    def test_deleting_the_digest_does_not_smuggle_a_rewritten_budget(self) -> None:
        """The attack the missing-field skip actually enabled, end to end."""
        self.spend()
        self.tamper(lambda r: {**{k: v for k, v in r.items() if k != "budget_digest"},
                               "budget": {**r["budget"], "wall_clock_seconds": 36_000.0}})
        with self.assertRaises(rb.BudgetError) as ctx:
            self.reopen(wall_clock_seconds=36_000.0)
        self.assertEqual(ctx.exception.code, "budget_record_malformed")
        record = rb.load_record(self.journal, self.run_id)
        self.assertGreaterEqual(record["elapsed_high_water_seconds"], 3000.0)

    def test_an_empty_budget_digest_is_refused_like_a_missing_one(self) -> None:
        self.spend()
        self.tamper(lambda r: {**r, "budget_digest": ""})
        with self.assertRaises(rb.BudgetError) as ctx:
            self.reopen()
        self.assertEqual(ctx.exception.code, "budget_record_malformed")

    def test_an_unreadable_budget_block_refuses(self) -> None:
        self.spend()
        self.tamper(lambda r: {**r, "budget": {"wall_clock_seconds": "forever"},
                               "budget_digest": ""})
        with self.assertRaises(rb.BudgetError) as ctx:
            self.reopen()
        self.assertEqual(ctx.exception.code, "budget_record_malformed")

    def test_an_absent_record_is_still_a_legitimate_first_launch(self) -> None:
        """The one shape that MAY start fresh - and the only one."""
        led = self.reopen(wall_clock_seconds=600.0)
        self.assertFalse(led.resumed)
        self.assertEqual(led.record()["elapsed_high_water_seconds"], 0.0)

    def test_every_refusal_and_launch_is_sealed_in_the_audit_chain(self) -> None:
        """C6: budget_conflict is the canonical budget-tamper signal."""
        self.spend()
        with self.assertRaises(rb.BudgetError):
            self.reopen(wall_clock_seconds=36_000.0)
        events = [(r["event_type"], r["policy_result"]) for r in self.audit.read_all()]
        self.assertIn(("run_budget_started", "run_budget_started"), events)
        self.assertIn(("run_budget_refused", "budget_conflict"), events)

    def test_a_resume_is_sealed_too(self) -> None:
        self.spend()
        self.reopen()
        events = [r["event_type"] for r in self.audit.read_all()]
        self.assertIn("run_budget_resumed", events)


class CorruptStateTypedRefusalTests(BoundedTestBase):
    """C5 (G5 I3+I4): corrupt persisted state is TYPED, never a traceback."""

    def test_a_corrupt_persisted_wall_clock_raises_a_typed_error(self) -> None:
        for bad in ("forever", [], {}, "12x"):
            with self.subTest(value=bad):
                with self.assertRaises(rb.BudgetError) as ctx:
                    rb.RunBudget.from_dict({"wall_clock_seconds": bad})
                self.assertEqual(ctx.exception.code, "unreadable_budget")

    def test_corrupt_persisted_counter_limits_raise_a_typed_error(self) -> None:
        with self.assertRaises(rb.BudgetError):
            rb.RunBudget.from_dict({"counter_limits": "all of them"})
        with self.assertRaises(rb.BudgetError):
            rb.RunBudget.from_dict({"counter_limits": {"model_calls_per_task": "many"}})

    def test_an_unknown_tally_name_in_the_record_is_a_typed_refusal(self) -> None:
        """`persist_counters` validated names on WRITE; nothing validated on READ."""
        led = self.ledger()
        record = dict(self.journal.get_state(f"run_budget/{self.run_id}"))
        record["counters"] = {"model_calls_per_taks": 3}
        self.journal.set_state(f"run_budget/{self.run_id}", record)
        reopened = rb.RunBudgetLedger(
            self.journal, run_id=self.run_id, clock=self.clock,
            budget=rb.RunBudget.from_limits(Limits()))
        reopened.start()
        with self.assertRaises(rb.BudgetError) as ctx:
            reopened.restore_counters(CircuitBreakers(Limits()))
        self.assertEqual(ctx.exception.code, "unknown_counter_limit")
        del led


class ArgvReplayTests(unittest.TestCase):
    """C3 (G5 I1): a synthesized argv can never carry the owner enable."""

    def test_the_enable_is_denied_in_any_synthesized_argv(self) -> None:
        from tools.agent_supervisor import process as proc

        for token in ("--owner-enable-bounded-auto", "--OWNER-ENABLE-BOUNDED-AUTO",
                      "--owner-enable-bounded-auto=true"):
            with self.subTest(token=token):
                with self.assertRaises(proc.HardDenyError):
                    proc.assert_argv_safe(["python", "-m", "tools.agent_supervisor",
                                           "start", token])

    def test_the_pre_existing_deny_sets_are_unchanged(self) -> None:
        from tools.agent_supervisor import process as proc

        self.assertIn("--dangerously-skip-permissions", proc.HARD_DENY_ARGUMENTS)
        self.assertEqual(proc.EFFORT_ARGUMENT_PREFIXES,
                         ("--effort", "--reasoning-effort"))
        self.assertEqual(proc.assert_argv_safe(["git", "status", "--porcelain"]),
                         ["git", "status", "--porcelain"])


class RedactedOutputTests(BoundedTestBase):
    """C2 (G5 M2): stdout is a transmission, and it is redacted like every other."""

    PAT_REMOTE = "https://x-access-token:ghp_0123456789abcdefghijklmnop@github.com/o/r.git"

    def emit(self, *, as_json: bool) -> str:
        import argparse

        from tools.agent_supervisor import cli

        payload = {"probes": {"probes": [{"step": "git_and_remote_state",
                                          "detail": f"remote is {self.PAT_REMOTE}",
                                          "evidence": {"remote_url": self.PAT_REMOTE}}]}}
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            cli._emit(argparse.Namespace(json=as_json), payload,
                      [f"remote: {self.PAT_REMOTE}"])
        return buffer.getvalue()

    def test_a_pat_bearing_remote_never_reaches_stdout_as_json(self) -> None:
        text = self.emit(as_json=True)
        self.assertNotIn("ghp_0123456789abcdefghijklmnop", text)
        self.assertIn("REDACTED", text)

    def test_a_pat_bearing_remote_never_reaches_stdout_in_human_mode(self) -> None:
        text = self.emit(as_json=False)
        self.assertNotIn("ghp_0123456789abcdefghijklmnop", text)
        self.assertIn("REDACTED", text)

    def test_a_refusal_is_redacted_on_both_channels(self) -> None:
        item = refusals.refusal(
            refusals.UNSAFE, reason_code="remote_unreachable",
            message=f"the remote {self.PAT_REMOTE} did not answer",
            detail={"url": self.PAT_REMOTE})
        for as_json in (True, False):
            with self.subTest(as_json=as_json):
                stream = io.StringIO()
                refusals.emit(item, as_json=as_json, stream=stream)
                self.assertNotIn("ghp_0123456789abcdefghijklmnop", stream.getvalue())

    def test_ordinary_payloads_are_unchanged_by_redaction(self) -> None:
        """Over-eager, but not destructive: a clean payload survives verbatim."""
        import argparse

        from tools.agent_supervisor import cli

        payload = {"command": "start", "dispatched": True, "provider_calls_made": 2,
                   "missing_inputs": [], "recovery": {"classification": "SAFE_CHECKPOINT"}}
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            cli._emit(argparse.Namespace(json=True), payload, [])
        self.assertEqual(json.loads(buffer.getvalue()), payload)


class RevisionResetDerivationTests(unittest.TestCase):
    """C12 (G4 F2): the REVISE reset set is derived, so it cannot drift."""

    def test_it_is_exactly_reset_on_progress_minus_the_revision_counter(self) -> None:
        from tools.agent_supervisor import loop_breakers as lb
        from tools.agent_supervisor.circuit_breakers import RESET_ON_PROGRESS

        self.assertEqual(set(lb._REVISE_SAFE_RESETS),
                         set(RESET_ON_PROGRESS) - {"consecutive_revision_loops"})
        self.assertTrue(set(lb._REVISE_SAFE_RESETS).issubset(RESET_ON_PROGRESS))
        self.assertNotIn("consecutive_revision_loops", lb._REVISE_SAFE_RESETS)


# --------------------------------------------------------------------------
# D-024 Amendment 14 (M0-T120, R295): the shell-routing drift tooth at the
# START-GATE level - the fold SEMANTICS proven deterministically.
# --------------------------------------------------------------------------
#
# The one-line gating fold in `start_gate.live_revalidation` ANDs the routing
# tooth into `cli_capability_manifest` (the pinned-identity step), exactly the way
# `config_identity` is ANDed into `controller_manifest`. These tests prove that
# semantics without driving `cli.main`: (1) the tooth's three states at the pinned
# DIGEST identity, and (2) that a failing tooth, folded into the capability step,
# makes `recovery.classify` return UNSAFE_OR_DRIFTED (refuse) while a passing tooth
# leaves the dispatch-shaped map SAFE. See the M0-T120 producer report (L1) for why
# the LIVE fold line is staged (it would refuse every fake-executable start harness,
# including the out-of-scope golden pack, until each seeds routing evidence).
class ShellRoutingGateFoldTests(unittest.TestCase):
    def setUp(self) -> None:
        from tools.agent_supervisor import recovery as rec
        from tools.agent_supervisor import recovery_probes as rp
        self.rec = rec
        self.rp = rp
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = pathlib.Path(self._tmp.name)
        self.identity = "d6f6c29a" * 8  # a stand-in pinned executable digest
        (self.dir / "shell_routing_pinned.json").write_text(json.dumps({
            "schema": "shell_routing/v1", "measured": True,
            "claude_version": "2.1.251", "cli_identity": self.identity,
            "routing_summary": {"verdict": "native_preferred"}}), encoding="utf-8")

    def _routing(self, installed_identity: str):
        return self.rp.probe_shell_routing_evidence(
            evidence_dir=str(self.dir), installed_identity=installed_identity)

    def _dispatch_shaped_map(self, *, shell_routing_ok: bool) -> dict:
        """The revalidation map a dispatch-ready start produces, with the R295
        fold applied (cli_capability_manifest ANDed with the routing tooth)."""
        base = {step: True for step in self.rec.REVALIDATION_STEPS}
        base["cli_capability_manifest"] = bool(
            base["cli_capability_manifest"] and shell_routing_ok)
        return base

    def test_current_evidence_for_the_pinned_identity_passes_the_tooth(self) -> None:
        self.assertTrue(self._routing(self.identity).passes)

    def test_no_evidence_refuses_the_dispatch(self) -> None:
        routing = self.rp.probe_shell_routing_evidence(
            evidence_dir=str(self.dir / "empty"), installed_identity=self.identity)
        self.assertFalse(routing.passes)
        outcome = self.rec.classify(self.rec.RecoveryContext(
            revalidation=self._dispatch_shaped_map(shell_routing_ok=routing.passes)))
        self.assertEqual(outcome.classification, self.rec.UNSAFE_OR_DRIFTED)
        self.assertIn("cli_capability_manifest", outcome.failed_steps)

    def test_stale_identity_evidence_refuses_the_dispatch(self) -> None:
        routing = self._routing("b" * 64)  # a DIFFERENT pinned identity
        self.assertFalse(routing.passes)
        self.assertEqual(routing.reason_code, "routing_evidence_stale")
        outcome = self.rec.classify(self.rec.RecoveryContext(
            revalidation=self._dispatch_shaped_map(shell_routing_ok=routing.passes)))
        self.assertEqual(outcome.classification, self.rec.UNSAFE_OR_DRIFTED)

    def test_current_evidence_leaves_the_dispatch_map_safe(self) -> None:
        routing = self._routing(self.identity)
        self.assertTrue(routing.passes)
        outcome = self.rec.classify(self.rec.RecoveryContext(
            revalidation=self._dispatch_shaped_map(shell_routing_ok=routing.passes)))
        # The routing tooth no longer forces UNSAFE; cli_capability_manifest holds.
        self.assertNotIn("cli_capability_manifest", outcome.failed_steps)

    def test_the_gate_helper_sources_identity_by_file_hash_not_a_spawn(self) -> None:
        """`_claude_identity_digest` is a file hash (no `claude --version` spawn)."""
        from tools.agent_supervisor.start_gate import _claude_identity_digest
        from tools.agent_supervisor.process import executable_identity
        # A real file (this test module) hashes to the same digest both ways;
        # nothing is executed, so any readable file yields a stable identity.
        expected = executable_identity(__file__, name="claude").digest
        self.assertEqual(_claude_identity_digest(__file__), expected)
        self.assertEqual(_claude_identity_digest(""), "")


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2)
