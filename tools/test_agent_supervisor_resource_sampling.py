#!/usr/bin/env python3
"""AS-3: live resource sampling wired into the loop for the R207 gauge set.

Activation-checklist evidence: project-control/reports/
M0-T036-ACTIVATION-CHECKLIST.md ("Live resource **sampling** wired into the loop
for the R207 limit set ... live sampling is the documented Phase-2/3 boundary").

Two levels are proven:

1. the sampler measures what the standard library CAN on Windows (free disk,
   retained-log bytes), reports a measurement OUTAGE distinctly from a
   STRUCTURALLY unmeasurable metric (CPU/memory/process-count), and never
   fabricates an OK reading (AD-025);
2. the loop consumes samples fail-closed: a measured limit crossing pauses, a
   sampling OUTAGE degrades to the conservative pause, and a structural unknown
   neither pauses nor is treated as safe (both directions tested).
"""
from __future__ import annotations

import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import loop as lp  # noqa: E402
from tools.agent_supervisor import state_machine as sm  # noqa: E402
from tools.agent_supervisor.circuit_breakers import CircuitBreakers  # noqa: E402
from tools.agent_supervisor.config import Limits  # noqa: E402
from tools.agent_supervisor.resource_sampling import (  # noqa: E402
    GAUGE_CPU_PERCENT,
    GAUGE_FREE_DISK,
    GAUGE_MEMORY_BYTES,
    GAUGE_PROCESS_COUNT,
    GAUGE_RETAINED_LOG,
    MEASURABLE_GAUGES,
    STRUCTURAL_UNKNOWN_GAUGES,
    GaugeSample,
    ResourceSampler,
)
from tools.test_agent_supervisor_loop import (  # noqa: E402
    FakeRunner,
    FakeReviewer,
    LoopTestBase,
    outcome,
    run_result,
)


class FakeSampler:
    """Returns a scripted list of GaugeSamples, once per `sample()` call."""

    def __init__(self, *samples: GaugeSample) -> None:
        self._samples = tuple(samples)

    def sample(self) -> tuple[GaugeSample, ...]:
        return self._samples


# --------------------------------------------------------------------------
# The sampler in isolation
# --------------------------------------------------------------------------


class SamplerUnitTests(unittest.TestCase):
    def test_measurable_gauges_report_real_readings(self) -> None:
        sampler = ResourceSampler(
            disk_path=str(HERE),
            disk_free_fn=lambda _p: 5_000_000_000,
            log_size_fn=lambda _paths: 4096)
        by_gauge = {s.gauge: s for s in sampler.sample()}
        self.assertTrue(by_gauge[GAUGE_FREE_DISK].known)
        self.assertEqual(by_gauge[GAUGE_FREE_DISK].value, 5_000_000_000)
        self.assertTrue(by_gauge[GAUGE_RETAINED_LOG].known)
        self.assertEqual(by_gauge[GAUGE_RETAINED_LOG].value, 4096)

    def test_measurement_outage_is_unknown_and_not_structural(self) -> None:
        def boom(_p):
            raise OSError("device not ready")

        sampler = ResourceSampler(disk_path="X:/nope", disk_free_fn=boom)
        disk = {s.gauge: s for s in sampler.sample()}[GAUGE_FREE_DISK]
        self.assertFalse(disk.known)
        self.assertFalse(disk.structural)
        self.assertIn("outage", disk.reason)

    def test_unmeasurable_gauges_are_structural_unknown_never_a_value(self) -> None:
        sampler = ResourceSampler(disk_path=str(HERE))
        by_gauge = {s.gauge: s for s in sampler.sample()}
        for gauge in (GAUGE_CPU_PERCENT, GAUGE_MEMORY_BYTES, GAUGE_PROCESS_COUNT):
            with self.subTest(gauge=gauge):
                self.assertFalse(by_gauge[gauge].known)
                self.assertTrue(by_gauge[gauge].structural)
                self.assertIsNone(by_gauge[gauge].value)

    def test_log_size_sums_files_and_tolerates_missing(self) -> None:
        real = HERE / "test_agent_supervisor_resource_sampling.py"
        sampler = ResourceSampler(
            disk_path=str(HERE),
            log_paths=(str(real), str(HERE / "does_not_exist.jsonl")))
        log = {s.gauge: s for s in sampler.sample()}[GAUGE_RETAINED_LOG]
        self.assertTrue(log.known)
        self.assertEqual(log.value, real.stat().st_size)

    def test_capability_report_lists_live_and_unmonitored(self) -> None:
        report = ResourceSampler(disk_path=str(HERE)).capability_report()
        self.assertEqual(tuple(report["live_sampled"]), MEASURABLE_GAUGES)
        self.assertEqual(
            tuple(report["structurally_unmonitored"]), STRUCTURAL_UNKNOWN_GAUGES)


# --------------------------------------------------------------------------
# The loop consuming samples (both directions)
# --------------------------------------------------------------------------


class LoopResourceGateTests(LoopTestBase):
    def _build(self, sampler) -> lp.SupervisedLoop:
        return lp.SupervisedLoop(
            config=lp.LoopConfig(mode="shadow", task_id="M0-T036", stage="phase4",
                                 allowed_paths=self.authority.allowed_paths,
                                 stop_conditions=("no bypass flags",),
                                 max_cycles=2, owner_touch_budget=4),
            journal=self.journal, audit=self.audit, machine=self.machine,
            authority=self.authority,
            runner=FakeRunner(run_result()), reviewer=FakeReviewer(outcome()),
            run_id=self.run_id, breakers=CircuitBreakers(Limits()),
            resource_sampler=sampler)

    def test_measured_limit_crossing_pauses_before_dispatch(self) -> None:
        """Direction 1: a REAL reading below the disk floor trips -> the cycle
        stops for the owner at its legal entry state, nothing was dispatched."""
        self.at_preflight()
        sampler = FakeSampler(
            GaugeSample(GAUGE_FREE_DISK, known=True, value=0))  # <= 1 GiB floor
        loop = self._build(sampler)
        result = loop.run_cycle("first unit", cycle=1)
        self.assertEqual(result.stopped, "resource_gauge_hard_threshold")
        self.assertEqual(self.machine.current_state, sm.PREFLIGHT)
        self.assertEqual(loop.runner.prompts, [],
                         "no provider call may be spent once a gauge tripped")

    def test_sampling_outage_degrades_to_conservative_pause(self) -> None:
        """Direction 2: a measurable gauge that could not be read this time
        pauses (fail closed) rather than assuming the resource is fine."""
        self.at_preflight()
        sampler = FakeSampler(
            GaugeSample(GAUGE_FREE_DISK, known=False, structural=False,
                        reason="sampling outage: OSError: device not ready"))
        loop = self._build(sampler)
        result = loop.run_cycle("first unit", cycle=1)
        self.assertEqual(result.stopped, "resource_gauge_hard_threshold")
        self.assertIn("could not be sampled", result.reason)
        self.assertEqual(loop.runner.prompts, [])

    def test_structural_unknown_neither_pauses_nor_is_treated_as_safe(self) -> None:
        """A structurally unmeasurable gauge does NOT pause the cycle (that would
        make the supervisor unusable on Windows) and is NEVER fed to the breaker
        as a fabricated OK reading -- the cycle dispatches normally."""
        self.at_preflight()
        sampler = FakeSampler(
            GaugeSample(GAUGE_CPU_PERCENT, known=False, structural=True,
                        reason="not measurable stdlib-only on Windows"),
            GaugeSample(GAUGE_MEMORY_BYTES, known=False, structural=True,
                        reason="not measurable stdlib-only on Windows"))
        loop = self._build(sampler)
        result = loop.run_cycle("first unit", cycle=1)
        self.assertNotEqual(result.stopped, "resource_gauge_hard_threshold")
        self.assertEqual(loop.runner.prompts, ["first unit"],
                         "a structural unknown must not block dispatch")

    def test_measured_within_limits_does_not_pause(self) -> None:
        """A healthy reading lets the cycle proceed to dispatch."""
        self.at_preflight()
        sampler = FakeSampler(
            GaugeSample(GAUGE_FREE_DISK, known=True, value=500_000_000_000),
            GaugeSample(GAUGE_RETAINED_LOG, known=True, value=1024))
        loop = self._build(sampler)
        result = loop.run_cycle("first unit", cycle=1)
        self.assertNotEqual(result.stopped, "resource_gauge_hard_threshold")
        self.assertEqual(loop.runner.prompts, ["first unit"])

    def test_no_sampler_is_a_noop_backward_compatible(self) -> None:
        """With no sampler injected (every pre-AS-3 caller) the resource gate is
        a no-op: behavior is unchanged."""
        self.at_preflight()
        loop = lp.SupervisedLoop(
            config=lp.LoopConfig(mode="shadow", task_id="M0-T036", stage="phase4",
                                 allowed_paths=self.authority.allowed_paths,
                                 stop_conditions=("no bypass flags",),
                                 max_cycles=2, owner_touch_budget=4),
            journal=self.journal, audit=self.audit, machine=self.machine,
            authority=self.authority,
            runner=FakeRunner(run_result()), reviewer=FakeReviewer(outcome()),
            run_id=self.run_id, breakers=CircuitBreakers(Limits()))
        result = loop.run_cycle("first unit", cycle=1)
        self.assertNotEqual(result.stopped, "resource_gauge_hard_threshold")
        self.assertEqual(loop.runner.prompts, ["first unit"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
