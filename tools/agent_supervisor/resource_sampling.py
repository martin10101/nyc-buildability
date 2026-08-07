#!/usr/bin/env python3
"""Live resource sampling for the R207 gauge breakers (D-007 S13.8; M0-T041 AS-3).

Activation-checklist evidence (project-control/reports/
M0-T036-ACTIVATION-CHECKLIST.md): "Live resource **sampling** wired into the loop
for the R207 limit set (config/circuit-breaker knobs exist + are fail-closed
today; live sampling is the documented Phase-2/3 boundary)". The R207 limit SET
(the four knobs from commit c6a2c59 -- max_model_calls_per_day,
max_external_writes_per_day, max_cpu_percent, max_memory_bytes -- plus the earlier
process_count / free_disk_bytes / retained_log_bytes / review_packet_bytes gauges)
was already bounded, configurable, and fail-closed in `circuit_breakers.py`, but
NOTHING sampled real readings into the gauge breakers from the loop. This module
supplies those readings, stdlib-only and Windows-compatible, and honestly reports
what a standard-library process on Windows CANNOT measure.

Two honesty rules, both load-bearing (AD-025: unknown is never treated as
zero/success):

1. A metric that this host CANNOT measure with the standard library alone (CPU
   percent, resident memory, and a generic process count on Windows -- psutil is
   not an admitted dependency, D-007 Section 5.1 stdlib-only lane) is reported as
   `known=False, structural=True`. It is NEVER fed to the breaker as a fabricated
   low/OK value -- an absent reading must never masquerade as a safe reading.

2. A metric that IS normally measurable (free disk via `shutil.disk_usage`,
   retained-log bytes via `os.stat`) but whose measurement RAISES this time is a
   sampling OUTAGE: reported as `known=False, structural=False`. The loop's
   consumer treats that conservatively (fail closed -- pause), because a resource
   guard that cannot read the resource must not assume the resource is fine.
"""
from __future__ import annotations

import dataclasses
import os
import shutil
from typing import Callable, Sequence

#: Gauge names (must match circuit_breakers.GAUGE_LIMITS) this sampler produces.
GAUGE_FREE_DISK = "free_disk_bytes"
GAUGE_RETAINED_LOG = "retained_log_bytes"
GAUGE_CPU_PERCENT = "cpu_percent"
GAUGE_MEMORY_BYTES = "memory_bytes"
GAUGE_PROCESS_COUNT = "process_count"

#: Gauges this host measures with the standard library alone.
MEASURABLE_GAUGES: tuple[str, ...] = (GAUGE_FREE_DISK, GAUGE_RETAINED_LOG)

#: Gauges NOT measurable stdlib-only on Windows. Represented as unknown, never as
#: a fabricated OK reading. (`process_count` is here because the sampler has no
#: authoritative child-process registry to count from; the containment layer, not
#: this sampler, owns child lifetimes.)
STRUCTURAL_UNKNOWN_GAUGES: tuple[str, ...] = (
    GAUGE_CPU_PERCENT, GAUGE_MEMORY_BYTES, GAUGE_PROCESS_COUNT)

_STDLIB_ONLY_REASON = (
    "not measurable with the Python standard library alone on Windows (psutil is "
    "not an admitted dependency; D-007 stdlib-only lane) -- reported as unknown, "
    "never as a safe reading")


@dataclasses.dataclass(frozen=True)
class GaugeSample:
    """One resource reading, or an honest statement that it is unknown."""

    gauge: str
    known: bool
    value: float | int | None = None
    #: True when the metric is STRUCTURALLY unmeasurable on this host (a permanent
    #: capability gap, disclosed, never a per-cycle pause). False for a transient
    #: sampling OUTAGE of a normally-measurable metric (conservative -> pause).
    structural: bool = False
    reason: str = ""


class ResourceSampler:
    """Samples the live R207 resource gauges, stdlib-only.

    Measurement functions are injectable so a test can drive a real reading OR a
    sampling outage deterministically without touching the real host resources.
    """

    def __init__(
        self,
        *,
        disk_path: str,
        log_paths: Sequence[str] = (),
        disk_free_fn: Callable[[str], int] | None = None,
        log_size_fn: Callable[[Sequence[str]], int] | None = None,
    ) -> None:
        self.disk_path = disk_path
        self.log_paths = tuple(log_paths)
        self._disk_free_fn = disk_free_fn or _default_disk_free
        self._log_size_fn = log_size_fn or _default_log_size

    def _sample_measurable(self, gauge: str, fn: Callable[[], int]) -> GaugeSample:
        try:
            value = int(fn())
        except Exception as exc:  # a sampling OUTAGE: known=False, NOT structural
            return GaugeSample(
                gauge=gauge, known=False, structural=False,
                reason=f"sampling outage: {type(exc).__name__}: {exc}")
        return GaugeSample(gauge=gauge, known=True, value=value)

    def sample(self) -> tuple[GaugeSample, ...]:
        """Return one GaugeSample per live R207 resource gauge."""
        samples = [
            self._sample_measurable(
                GAUGE_FREE_DISK, lambda: self._disk_free_fn(self.disk_path)),
            self._sample_measurable(
                GAUGE_RETAINED_LOG, lambda: self._log_size_fn(self.log_paths)),
        ]
        for gauge in STRUCTURAL_UNKNOWN_GAUGES:
            samples.append(GaugeSample(
                gauge=gauge, known=False, structural=True,
                reason=_STDLIB_ONLY_REASON))
        return tuple(samples)

    def capability_report(self) -> dict[str, list[str]]:
        """Which gauges are live-sampled vs structurally unmonitored on this host.

        The disclosure surface for `doctor`: an operator sees exactly which R207
        resource limits are enforced by live sampling and which are unmonitored
        (and therefore never falsely reported safe).
        """
        return {
            "live_sampled": list(MEASURABLE_GAUGES),
            "structurally_unmonitored": list(STRUCTURAL_UNKNOWN_GAUGES),
        }


def _default_disk_free(path: str) -> int:
    return int(shutil.disk_usage(path).free)


def _default_log_size(paths: Sequence[str]) -> int:
    total = 0
    for path in paths:
        try:
            total += os.stat(path).st_size
        except FileNotFoundError:
            # An absent log file contributes zero bytes; that is a real, known
            # reading (no bytes retained), not a sampling outage.
            continue
    return total
