#!/usr/bin/env python3
"""M0-T173 (D-091 TW3): wire the Linux memory gauge + the 70% ceiling into the loop.

Proves the acceptance scenarios of packet M0-T173.json, driving the REAL sampler
(`build_resource_sampler`), the REAL ceiling resolver (`posix_memory_ceiling_bytes`),
and the REAL loop gate + breaker (`loop._check_resources`, `CircuitBreakers.gauge`)
exactly as M0-T170's `MemoryCeilingThroughRealBreakerTests` did -- no edit to loop.py
or circuit_breakers.py, no live provider call.

- PRIMARY: on POSIX the sampler reports `memory_bytes` from /proc/meminfo and the loop
  pauses at or above the resolved 70% ceiling (owner rule D-090-R076), dispatches below.
- MISSING/AMBIGUOUS: an unreadable gauge pauses the loop (fail closed).
- REGRESSION: the plain `ResourceSampler` (and the off-POSIX `build_resource_sampler`)
  still report `memory_bytes` as a structural unknown -- Windows behaviour unchanged.

`os.name` is patched ONLY around construction (never around `run_cycle`, whose
containment detection is platform-sensitive) and a synthetic `/proc/meminfo` reader is
always injected, so every test is deterministic on both Linux and Windows CI.
"""
from __future__ import annotations

import dataclasses
import pathlib
import sys
import unittest
from typing import Callable
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import loop as lp  # noqa: E402
from tools.agent_supervisor import state_machine as sm  # noqa: E402
from tools.agent_supervisor.circuit_breakers import (  # noqa: E402
    OK,
    TRIP,
    CircuitBreakers,
)
from tools.agent_supervisor.config import Limits  # noqa: E402
from tools.agent_supervisor.resource_sampling import (  # noqa: E402
    GAUGE_FREE_DISK,
    GAUGE_MEMORY_BYTES,
    GAUGE_RETAINED_LOG,
    MEMORY_PAUSE_FRACTION,
    STRUCTURAL_UNKNOWN_GAUGES,
    GaugeSample,
    ResourceSampler,
    build_resource_sampler,
    posix_memory_ceiling_bytes,
    resolve_memory_ceiling_bytes,
)
from tools.test_agent_supervisor_loop import (  # noqa: E402
    FakeReviewer,
    FakeRunner,
    LoopTestBase,
    outcome,
    run_result,
)

GIB = 1024 ** 3
OS_NAME = "tools.agent_supervisor.resource_sampling.os.name"


def reader_for(total_bytes: int, used_bytes: int) -> Callable[[], str]:
    """A /proc/meminfo reader for a host of `total_bytes` with `used_bytes` in use."""
    total_kb = total_bytes // 1024
    available_kb = (total_bytes - used_bytes) // 1024
    return lambda: (
        f"MemTotal:       {total_kb} kB\n"
        f"MemFree:          700424 kB\n"
        f"MemAvailable:    {available_kb} kB\n"
        f"Cached:          5448352 kB\n"
    )


def boom() -> str:
    raise OSError("meminfo unreadable")


def posix_sampler(**kwargs) -> ResourceSampler:
    """Build a sampler with the POSIX memory gauge wired, regardless of host OS."""
    with mock.patch(OS_NAME, "posix"):
        return build_resource_sampler(**kwargs)


# --------------------------------------------------------------------------
# posix_memory_ceiling_bytes: launch-time ceiling, POSIX-only, fail closed
# --------------------------------------------------------------------------


class PosixMemoryCeilingTests(unittest.TestCase):
    def test_posix_ceiling_is_70pct_of_measured_total(self) -> None:
        total = 8 * GIB
        with mock.patch(OS_NAME, "posix"):
            ceiling = posix_memory_ceiling_bytes(
                Limits().max_memory_bytes, meminfo_reader=reader_for(total, GIB))
        self.assertEqual(MEMORY_PAUSE_FRACTION, 0.70)
        self.assertEqual(ceiling, int(0.70 * total))

    def test_configured_ceiling_can_only_tighten_the_posix_ceiling(self) -> None:
        total = 8 * GIB
        tighter = 3 * GIB  # below 70% of 8 GiB (~5.6 GiB)
        with mock.patch(OS_NAME, "posix"):
            ceiling = posix_memory_ceiling_bytes(
                tighter, meminfo_reader=reader_for(total, GIB))
        self.assertEqual(ceiling, tighter)

    def test_non_posix_returns_none_keeping_configured_ceiling(self) -> None:
        # Windows: no measured total, so the caller keeps the configured ceiling
        # byte-for-byte and the gauge stays a structural unknown.
        with mock.patch(OS_NAME, "nt"):
            self.assertIsNone(
                posix_memory_ceiling_bytes(
                    Limits().max_memory_bytes, meminfo_reader=reader_for(8 * GIB, GIB)))

    def test_unreadable_meminfo_raises_fail_closed(self) -> None:
        # No launch under an UNMEASURED ceiling: the resolver raises rather than
        # inventing or loosening one (AD-025).
        with mock.patch(OS_NAME, "posix"):
            with self.assertRaises(OSError):
                posix_memory_ceiling_bytes(
                    Limits().max_memory_bytes, meminfo_reader=boom)

    def test_missing_memtotal_raises_fail_closed(self) -> None:
        with mock.patch(OS_NAME, "posix"):
            with self.assertRaises(KeyError):
                posix_memory_ceiling_bytes(
                    Limits().max_memory_bytes,
                    meminfo_reader=lambda: "MemAvailable:   1000 kB\n")


# --------------------------------------------------------------------------
# build_resource_sampler: POSIX wires a live memory gauge; off-POSIX does not
# --------------------------------------------------------------------------


class BuildResourceSamplerTests(unittest.TestCase):
    def _memory_sample(self, sampler: ResourceSampler) -> GaugeSample:
        return {s.gauge: s for s in sampler.sample()}[GAUGE_MEMORY_BYTES]

    def test_posix_emits_a_live_known_memory_reading(self) -> None:
        total = 8 * GIB
        sampler = posix_sampler(disk_path=str(HERE),
                                meminfo_reader=reader_for(total, 2 * GIB))
        sample = self._memory_sample(sampler)
        self.assertTrue(sample.known)
        self.assertIsNotNone(sample.value)
        self.assertAlmostEqual(sample.value / GIB, 2.0, places=1)

    def test_posix_unreadable_gauge_is_a_conservative_outage(self) -> None:
        sampler = posix_sampler(disk_path=str(HERE), meminfo_reader=boom)
        sample = self._memory_sample(sampler)
        # known=False + structural=False is exactly what the loop treats as a pause.
        self.assertFalse(sample.known)
        self.assertFalse(sample.structural)
        self.assertIsNone(sample.value)
        self.assertIn("sampling outage", sample.reason)

    def test_non_posix_attaches_no_gauge_memory_stays_structural_unknown(self) -> None:
        with mock.patch(OS_NAME, "nt"):
            sampler = build_resource_sampler(disk_path=str(HERE),
                                             meminfo_reader=reader_for(8 * GIB, GIB))
        sample = self._memory_sample(sampler)
        self.assertFalse(sample.known)
        self.assertTrue(sample.structural)
        self.assertIsNone(sample.value)


# --------------------------------------------------------------------------
# PRIMARY + fail-closed through the REAL loop gate + breaker (unchanged)
# --------------------------------------------------------------------------


class LinuxGaugeThroughRealLoopTests(LoopTestBase):
    """The live Linux reading enforces the 70% ceiling through the UNCHANGED
    breaker and loop gate -- no edit to loop.py / circuit_breakers.py."""

    def _build(self, sampler, *, max_memory_bytes: int) -> lp.SupervisedLoop:
        return lp.SupervisedLoop(
            config=lp.LoopConfig(mode="shadow", task_id="M0-T173", stage="phase4",
                                 allowed_paths=self.authority.allowed_paths,
                                 stop_conditions=("no bypass flags",),
                                 max_cycles=2, owner_touch_budget=4),
            journal=self.journal, audit=self.audit, machine=self.machine,
            authority=self.authority,
            runner=FakeRunner(run_result()), reviewer=FakeReviewer(outcome()),
            run_id=self.run_id,
            breakers=CircuitBreakers(Limits(max_memory_bytes=max_memory_bytes)),
            resource_sampler=sampler)

    def _sampler(self, reader: Callable[[], str]) -> ResourceSampler:
        # log_paths=() -> retained_log is a known 0 (never trips); the real disk
        # gauge reads ample CI free space; only the injected memory reading differs
        # between the pause and dispatch cases below (the trip is memory, nothing else).
        return posix_sampler(disk_path=str(self.tmp), log_paths=(), meminfo_reader=reader)

    def test_memory_over_ceiling_pauses_the_loop_before_dispatch(self) -> None:
        total = 8 * GIB
        ceiling = resolve_memory_ceiling_bytes(total)
        self.at_preflight()
        loop = self._build(self._sampler(reader_for(total, ceiling + GIB)),
                           max_memory_bytes=ceiling)
        result = loop.run_cycle("first unit", cycle=1)
        self.assertEqual(result.stopped, "resource_gauge_hard_threshold")
        self.assertEqual(self.machine.current_state, sm.PREFLIGHT)
        self.assertEqual(loop.runner.prompts, [])

    def test_memory_under_ceiling_dispatches(self) -> None:
        total = 8 * GIB
        ceiling = resolve_memory_ceiling_bytes(total)
        self.at_preflight()
        loop = self._build(self._sampler(reader_for(total, ceiling - GIB)),
                           max_memory_bytes=ceiling)
        result = loop.run_cycle("first unit", cycle=1)
        self.assertNotEqual(result.stopped, "resource_gauge_hard_threshold")
        self.assertEqual(loop.runner.prompts, ["first unit"])

    def test_unreadable_gauge_pauses_the_loop(self) -> None:
        total = 8 * GIB
        ceiling = resolve_memory_ceiling_bytes(total)
        self.at_preflight()
        loop = self._build(self._sampler(boom), max_memory_bytes=ceiling)
        result = loop.run_cycle("first unit", cycle=1)
        self.assertEqual(result.stopped, "resource_gauge_hard_threshold")
        self.assertEqual(loop.runner.prompts, [])


# --------------------------------------------------------------------------
# The cli.py launch wiring: resolved ceiling -> the breaker trips at 70%
# --------------------------------------------------------------------------


class CliLaunchWiringTests(unittest.TestCase):
    """Reproduce cli.cmd_start's two-line composition (posix_memory_ceiling_bytes
    -> dataclasses.replace -> CircuitBreakers) and prove the breaker enforces the
    derived 70% ceiling. The full cmd_start path is exercised by the start-path
    suites in CI (model_chain, mrl_launch_path, start_reentry)."""

    def _breakers(self, reader: Callable[[], str], *, os_name: str) -> CircuitBreakers:
        with mock.patch(OS_NAME, os_name):
            ceiling = posix_memory_ceiling_bytes(
                Limits().max_memory_bytes, meminfo_reader=reader)
        limits = Limits() if ceiling is None else dataclasses.replace(
            Limits(), max_memory_bytes=ceiling)
        return CircuitBreakers(limits)

    def test_posix_breaker_ceiling_trips_at_70pct(self) -> None:
        total = 8 * GIB
        ceiling = resolve_memory_ceiling_bytes(total)
        breakers = self._breakers(reader_for(total, GIB), os_name="posix")
        self.assertEqual(breakers.limits.max_memory_bytes, ceiling)
        self.assertEqual(breakers.gauge(GAUGE_MEMORY_BYTES, ceiling).verdict, TRIP)
        self.assertEqual(breakers.gauge(GAUGE_MEMORY_BYTES, GIB).verdict, OK)

    def test_non_posix_keeps_the_configured_8gib_ceiling(self) -> None:
        breakers = self._breakers(reader_for(8 * GIB, GIB), os_name="nt")
        self.assertEqual(breakers.limits.max_memory_bytes, Limits().max_memory_bytes)
        self.assertEqual(breakers.limits.max_memory_bytes, 8_589_934_592)


# --------------------------------------------------------------------------
# REGRESSION: the plain ResourceSampler is byte-identical (Windows unchanged)
# --------------------------------------------------------------------------


class RegressionTests(unittest.TestCase):
    def test_plain_sampler_memory_gauge_stays_structural_unknown(self) -> None:
        # The default constructor (no memory_gauge) is what every non-launch path
        # builds; memory_bytes must remain an honest structural unknown everywhere.
        sampler = ResourceSampler(disk_path=str(HERE))
        by_gauge = {s.gauge: s for s in sampler.sample()}
        self.assertFalse(by_gauge[GAUGE_MEMORY_BYTES].known)
        self.assertTrue(by_gauge[GAUGE_MEMORY_BYTES].structural)
        self.assertIsNone(by_gauge[GAUGE_MEMORY_BYTES].value)
        self.assertIn(GAUGE_MEMORY_BYTES, STRUCTURAL_UNKNOWN_GAUGES)

    def test_measurable_gauges_still_present_and_known(self) -> None:
        sampler = ResourceSampler(disk_path=str(HERE), log_paths=())
        by_gauge = {s.gauge: s for s in sampler.sample()}
        self.assertTrue(by_gauge[GAUGE_FREE_DISK].known)
        self.assertTrue(by_gauge[GAUGE_RETAINED_LOG].known)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
