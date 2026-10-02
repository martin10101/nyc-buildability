#!/usr/bin/env python3
"""D-091 T7 (M0-T170): resource fit for 5 loop lanes on a 4-CPU/8-GiB Linux box.

Acceptance scenarios (packet M0-T170.json), one test class each:

* PRIMARY - on a host reporting ~8 GiB total memory the pause ceiling resolves
  to no more than 70% of it, and at or above it the loop pauses (fail closed).
* BOUNDARY - a third concurrent review-or-combine request waits while two run;
  the per-lane cap holds.
* MISSING/AMBIGUOUS - unreadable memory or CPU gauges fail closed (pause), never
  run unbounded.
* REGRESSION - the Windows/PC defaults and the existing resource sampler
  behaviour are unchanged.

No real load is generated: the /proc/meminfo reader and the active process
counts are injected, and the loop is driven with the project's existing fake
runner/reviewer/sampler harness so the REAL consumer (`loop._check_resources`,
`circuit_breakers.CircuitBreakers`) enforces the readings unchanged.
"""
from __future__ import annotations

import pathlib
import sys
import unittest
from typing import Callable

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import loop as lp  # noqa: E402
from tools.agent_supervisor import state_machine as sm  # noqa: E402
from tools.agent_supervisor.circuit_breakers import OK, TRIP, CircuitBreakers  # noqa: E402
from tools.agent_supervisor.config import Limits, load_controller_config  # noqa: E402
from tools.agent_supervisor.resource_sampling import (  # noqa: E402
    GAUGE_CPU_PERCENT,
    GAUGE_FREE_DISK,
    GAUGE_MEMORY_BYTES,
    GAUGE_RETAINED_LOG,
    MEMORY_PAUSE_FRACTION,
    STRUCTURAL_UNKNOWN_GAUGES,
    GaugeSample,
    MemoryPauseVerdict,
    ResourceSampler,
    evaluate_linux_memory,
    linux_memory_gauge_sample,
    read_proc_meminfo,
    resolve_memory_ceiling_bytes,
)
from tools.agent_supervisor.run_budget import (  # noqa: E402
    GLOBAL_REVIEW_OR_COMBINE_DEFAULT,
    AdmissionVerdict,
    admit_review_or_combine,
)
from tools.test_agent_supervisor_loop import (  # noqa: E402
    FakeReviewer,
    FakeRunner,
    LoopTestBase,
    outcome,
    run_result,
)

GIB = 1024 ** 3
PACKAGE_ROOT = REPO / "tools" / "agent_supervisor"


def meminfo_text(*, total_kb: int, available_kb: int, extra: str = "") -> str:
    """A realistic /proc/meminfo body with injectable MemTotal / MemAvailable."""
    return (
        f"MemTotal:       {total_kb} kB\n"
        f"MemFree:          700424 kB\n"
        f"MemAvailable:    {available_kb} kB\n"
        f"Buffers:          437920 kB\n"
        f"Cached:          5448352 kB\n"
        f"{extra}"
    )


def reader_for(total_bytes: int, used_bytes: int) -> Callable[[], str]:
    """A /proc/meminfo reader for a host of `total_bytes` with `used_bytes` in use."""
    total_kb = total_bytes // 1024
    available_kb = (total_bytes - used_bytes) // 1024
    return lambda: meminfo_text(total_kb=total_kb, available_kb=available_kb)


class FakeSampler:
    """Returns a scripted list of GaugeSamples, once per `sample()` call."""

    def __init__(self, *samples: GaugeSample) -> None:
        self._samples = tuple(samples)

    def sample(self) -> tuple[GaugeSample, ...]:
        return self._samples


# --------------------------------------------------------------------------
# PRIMARY: the memory pause ceiling is <= 70% of MEASURED physical memory
# --------------------------------------------------------------------------


class MemoryCeilingDerivationTests(unittest.TestCase):
    def test_ceiling_is_at_most_70pct_of_an_8gib_host(self) -> None:
        total = 8 * GIB
        ceiling = resolve_memory_ceiling_bytes(total)
        self.assertEqual(MEMORY_PAUSE_FRACTION, 0.70)
        self.assertEqual(ceiling, int(0.70 * total))
        self.assertLessEqual(ceiling, int(0.70 * total))
        self.assertLess(ceiling, total)
        # ~5.6 GiB, not the whole box.
        self.assertAlmostEqual(ceiling / GIB, 5.6, places=1)

    def test_ceiling_is_derived_from_measured_total_not_hardcoded_8gib(self) -> None:
        """A 16-GiB box earns a ceiling ABOVE the 8-GiB constant and a 4-GiB box
        one well below it, proving the ceiling tracks /proc/meminfo, not a fixed
        8-GiB number (packet: 'do not hard-code 8 GiB')."""
        big = resolve_memory_ceiling_bytes(16 * GIB)
        small = resolve_memory_ceiling_bytes(4 * GIB)
        self.assertGreater(big, 8 * GIB)
        self.assertLess(small, 8 * GIB)
        self.assertEqual(big, int(0.70 * 16 * GIB))
        self.assertEqual(small, int(0.70 * 4 * GIB))
        self.assertNotEqual(big, Limits().max_memory_bytes)

    def test_configured_ceiling_can_only_tighten_never_exceed_70pct(self) -> None:
        total = 8 * GIB
        seventy = int(0.70 * total)
        # A tighter owner config wins.
        self.assertEqual(
            resolve_memory_ceiling_bytes(total, configured_ceiling_bytes=3 * GIB),
            3 * GIB)
        # Leaving the 8-GiB PC default still caps at 70% of the measured box.
        self.assertEqual(
            resolve_memory_ceiling_bytes(total, configured_ceiling_bytes=8 * GIB),
            seventy)

    def test_at_or_above_ceiling_pauses_below_does_not(self) -> None:
        total = 8 * GIB
        ceiling = resolve_memory_ceiling_bytes(total)
        at = evaluate_linux_memory(meminfo_reader=reader_for(total, ceiling))
        above = evaluate_linux_memory(meminfo_reader=reader_for(total, ceiling + GIB))
        below = evaluate_linux_memory(meminfo_reader=reader_for(total, ceiling - GIB))
        self.assertTrue(at.known and at.pause)
        self.assertTrue(above.known and above.pause)
        self.assertTrue(below.known and not below.pause)
        self.assertEqual(at.ceiling_bytes, ceiling)
        self.assertEqual(at.total_bytes, total)

    def test_meminfo_parses_kb_rows_to_bytes(self) -> None:
        info = read_proc_meminfo(lambda: meminfo_text(total_kb=8388608, available_kb=4194304))
        self.assertEqual(info["MemTotal"], 8388608 * 1024)
        self.assertEqual(info["MemAvailable"], 4194304 * 1024)


class MemoryCeilingThroughRealBreakerTests(LoopTestBase):
    """The Linux memory reading enforces the 70% ceiling through the UNCHANGED
    breaker and loop gate (no edit to loop.py / circuit_breakers.py)."""

    def _build(self, sampler, *, max_memory_bytes: int) -> lp.SupervisedLoop:
        return lp.SupervisedLoop(
            config=lp.LoopConfig(mode="shadow", task_id="M0-T170", stage="phase4",
                                 allowed_paths=self.authority.allowed_paths,
                                 stop_conditions=("no bypass flags",),
                                 max_cycles=2, owner_touch_budget=4),
            journal=self.journal, audit=self.audit, machine=self.machine,
            authority=self.authority,
            runner=FakeRunner(run_result()), reviewer=FakeReviewer(outcome()),
            run_id=self.run_id,
            breakers=CircuitBreakers(Limits(max_memory_bytes=max_memory_bytes)),
            resource_sampler=sampler)

    def test_gauge_sample_trips_the_breaker_at_the_derived_ceiling(self) -> None:
        total = 8 * GIB
        ceiling = resolve_memory_ceiling_bytes(total)
        sample = linux_memory_gauge_sample(reader_for(total, ceiling))
        breakers = CircuitBreakers(Limits(max_memory_bytes=ceiling))
        self.assertTrue(sample.known)
        self.assertEqual(breakers.gauge(GAUGE_MEMORY_BYTES, sample.value).verdict, TRIP)
        # A reading well below the warn band (0.75 * ceiling) is OK, not a pause.
        ok_sample = linux_memory_gauge_sample(reader_for(total, GIB))
        self.assertEqual(breakers.gauge(GAUGE_MEMORY_BYTES, ok_sample.value).verdict, OK)

    def test_memory_over_ceiling_pauses_the_loop_before_dispatch(self) -> None:
        total = 8 * GIB
        ceiling = resolve_memory_ceiling_bytes(total)
        self.at_preflight()
        sampler = FakeSampler(
            linux_memory_gauge_sample(reader_for(total, ceiling + GIB)),
            GaugeSample(GAUGE_FREE_DISK, known=True, value=500 * GIB),
            GaugeSample(GAUGE_RETAINED_LOG, known=True, value=1024))
        loop = self._build(sampler, max_memory_bytes=ceiling)
        result = loop.run_cycle("first unit", cycle=1)
        self.assertEqual(result.stopped, "resource_gauge_hard_threshold")
        self.assertEqual(self.machine.current_state, sm.PREFLIGHT)
        self.assertEqual(loop.runner.prompts, [])

    def test_memory_under_ceiling_dispatches(self) -> None:
        total = 8 * GIB
        ceiling = resolve_memory_ceiling_bytes(total)
        self.at_preflight()
        sampler = FakeSampler(
            linux_memory_gauge_sample(reader_for(total, ceiling - GIB)),
            GaugeSample(GAUGE_FREE_DISK, known=True, value=500 * GIB),
            GaugeSample(GAUGE_RETAINED_LOG, known=True, value=1024))
        loop = self._build(sampler, max_memory_bytes=ceiling)
        result = loop.run_cycle("first unit", cycle=1)
        self.assertNotEqual(result.stopped, "resource_gauge_hard_threshold")
        self.assertEqual(loop.runner.prompts, ["first unit"])


# --------------------------------------------------------------------------
# BOUNDARY: <=2 concurrent review-or-combine across lanes; per-lane cap holds
# --------------------------------------------------------------------------


class ConcurrencyAdmissionTests(unittest.TestCase):
    def admit(self, *, g=0, lane=0, gl=2, ll=1, lane_id="A") -> AdmissionVerdict:
        return admit_review_or_combine(global_active=g, lane_active=lane,
                                       global_limit=gl, lane_limit=ll, lane=lane_id)

    def test_default_global_ceiling_is_two(self) -> None:
        self.assertEqual(GLOBAL_REVIEW_OR_COMBINE_DEFAULT, 2)
        self.assertEqual(Limits().max_concurrent_reviews_or_combines, 2)

    def test_third_request_waits_while_two_run(self) -> None:
        # Two already running globally (one per two different lanes) -> a third
        # from an empty third lane still WAITS on the global cap of 2.
        self.assertTrue(self.admit(g=0, lane=0).admitted)
        self.assertTrue(self.admit(g=1, lane=0).admitted)
        third = self.admit(g=2, lane=0)
        self.assertFalse(third.admitted)
        self.assertEqual(third.reason_code, "concurrency_limit_reached")
        self.assertEqual(third.scope, "global")
        self.assertIn("waits", third.reason)

    def test_per_lane_cap_holds_even_when_global_has_room(self) -> None:
        # Global limit 3 has room, but the lane is already at its per-lane cap 1.
        held = self.admit(g=1, lane=1, gl=3, ll=1)
        self.assertFalse(held.admitted)
        self.assertEqual(held.reason_code, "concurrency_limit_reached")
        self.assertTrue(held.scope.startswith("lane"))

    def test_both_dimensions_must_be_clear_to_admit(self) -> None:
        self.assertTrue(self.admit(g=1, lane=0, gl=2, ll=1).admitted)
        self.assertFalse(self.admit(g=2, lane=0, gl=2, ll=1).admitted)  # global full
        self.assertFalse(self.admit(g=0, lane=1, gl=2, ll=1).admitted)  # lane full


# --------------------------------------------------------------------------
# MISSING/AMBIGUOUS: unreadable memory or CPU gauges fail closed (pause)
# --------------------------------------------------------------------------


class UnreadableGaugeFailClosedTests(unittest.TestCase):
    def test_unreadable_meminfo_pauses(self) -> None:
        def boom() -> str:
            raise OSError("permission denied")

        verdict = evaluate_linux_memory(meminfo_reader=boom)
        self.assertIsInstance(verdict, MemoryPauseVerdict)
        self.assertFalse(verdict.known)
        self.assertTrue(verdict.pause)
        self.assertIn("fail closed", verdict.reason)

    def test_meminfo_missing_memavailable_pauses(self) -> None:
        # An older kernel without MemAvailable must not be read as "all free".
        def reader() -> str:
            return "MemTotal:       8388608 kB\nMemFree:  700424 kB\n"

        verdict = evaluate_linux_memory(meminfo_reader=reader)
        self.assertFalse(verdict.known)
        self.assertTrue(verdict.pause)

    def test_implausible_meminfo_pauses(self) -> None:
        # MemAvailable above MemTotal is corrupt; never a flattering low reading.
        reader = reader_for(4 * GIB, used_bytes=-(1 * GIB))  # available > total
        verdict = evaluate_linux_memory(meminfo_reader=reader)
        self.assertFalse(verdict.known)
        self.assertTrue(verdict.pause)

    def test_unreadable_memory_gauge_sample_is_a_conservative_outage(self) -> None:
        def boom() -> str:
            raise OSError("device not ready")

        sample = linux_memory_gauge_sample(boom)
        self.assertFalse(sample.known)
        self.assertFalse(sample.structural)  # outage -> the loop pauses
        self.assertIn("outage", sample.reason)

    def test_unreadable_count_or_bad_limit_admits_nothing(self) -> None:
        self.assertFalse(admit_review_or_combine(
            global_active=-1, lane_active=0, global_limit=2, lane_limit=1).admitted)
        self.assertFalse(admit_review_or_combine(
            global_active=0, lane_active=0, global_limit=0, lane_limit=1).admitted)
        self.assertEqual(admit_review_or_combine(
            global_active=0, lane_active=0, global_limit=2,
            lane_limit=0).reason_code, "no_admission_limit")


class UnreadableGaugePausesLoopTests(LoopTestBase):
    def _build(self, sampler) -> lp.SupervisedLoop:
        return lp.SupervisedLoop(
            config=lp.LoopConfig(mode="shadow", task_id="M0-T170", stage="phase4",
                                 allowed_paths=self.authority.allowed_paths,
                                 stop_conditions=("no bypass flags",),
                                 max_cycles=2, owner_touch_budget=4),
            journal=self.journal, audit=self.audit, machine=self.machine,
            authority=self.authority,
            runner=FakeRunner(run_result()), reviewer=FakeReviewer(outcome()),
            run_id=self.run_id, breakers=CircuitBreakers(Limits()),
            resource_sampler=sampler)

    def test_cpu_sampling_outage_pauses_the_loop(self) -> None:
        self.at_preflight()
        sampler = FakeSampler(
            GaugeSample(GAUGE_CPU_PERCENT, known=False, structural=False,
                        reason="sampling outage: OSError: /proc/stat unreadable"))
        loop = self._build(sampler)
        result = loop.run_cycle("first unit", cycle=1)
        self.assertEqual(result.stopped, "resource_gauge_hard_threshold")
        self.assertIn("could not be sampled", result.reason)
        self.assertEqual(loop.runner.prompts, [])

    def test_meminfo_read_failure_pauses_the_loop(self) -> None:
        def boom() -> str:
            raise OSError("permission denied")

        self.at_preflight()
        sampler = FakeSampler(linux_memory_gauge_sample(boom))
        loop = self._build(sampler)
        result = loop.run_cycle("first unit", cycle=1)
        self.assertEqual(result.stopped, "resource_gauge_hard_threshold")
        self.assertEqual(loop.runner.prompts, [])


# --------------------------------------------------------------------------
# REGRESSION: PC/Windows defaults and the existing sampler are unchanged
# --------------------------------------------------------------------------


class RegressionTests(unittest.TestCase):
    def test_pc_resource_defaults_unchanged(self) -> None:
        limits = Limits()
        self.assertEqual(limits.max_memory_bytes, 8_589_934_592)  # 8 GiB
        self.assertEqual(limits.max_cpu_percent, 90)
        self.assertEqual(limits.max_processes, 24)
        self.assertEqual(limits.min_free_disk_bytes, 1_073_741_824)

    def test_new_concurrency_limits_default_and_parse(self) -> None:
        limits = Limits()
        self.assertEqual(limits.max_concurrent_reviews_or_combines, 2)
        self.assertEqual(limits.max_concurrent_reviews_or_combines_per_lane, 1)
        parsed = Limits.from_mapping(
            {"max_concurrent_reviews_or_combines": 2,
             "max_concurrent_reviews_or_combines_per_lane": 1}, "unit")
        self.assertEqual(parsed.max_concurrent_reviews_or_combines, 2)
        self.assertEqual(parsed.max_concurrent_reviews_or_combines_per_lane, 1)

    def test_example_config_still_loads_with_documented_values(self) -> None:
        config = load_controller_config(PACKAGE_ROOT / "config.example.toml")
        self.assertEqual(config.limits.max_memory_bytes, 8_589_934_592)
        self.assertEqual(config.limits.max_cpu_percent, 90)
        self.assertEqual(config.limits.max_processes, 24)
        self.assertEqual(config.limits.max_concurrent_reviews_or_combines, 2)
        self.assertEqual(
            config.limits.max_concurrent_reviews_or_combines_per_lane, 1)

    def test_windows_memory_gauge_stays_structural_unknown(self) -> None:
        # The stdlib Windows sampler is unchanged: memory_bytes is still an
        # honest structural unknown, never a fabricated OK or a new value.
        sampler = ResourceSampler(disk_path=str(HERE))
        by_gauge = {s.gauge: s for s in sampler.sample()}
        self.assertFalse(by_gauge[GAUGE_MEMORY_BYTES].known)
        self.assertTrue(by_gauge[GAUGE_MEMORY_BYTES].structural)
        self.assertIsNone(by_gauge[GAUGE_MEMORY_BYTES].value)
        self.assertIn(GAUGE_MEMORY_BYTES, STRUCTURAL_UNKNOWN_GAUGES)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
