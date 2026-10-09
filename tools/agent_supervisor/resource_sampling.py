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
from functools import partial
from typing import Callable, Mapping, Sequence

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
        memory_gauge: Callable[[], "GaugeSample"] | None = None,
    ) -> None:
        self.disk_path = disk_path
        self.log_paths = tuple(log_paths)
        self._disk_free_fn = disk_free_fn or _default_disk_free
        self._log_size_fn = log_size_fn or _default_log_size
        #: Optional live resident-memory reader (Linux: `linux_memory_gauge_sample`
        #: against /proc/meminfo). None -> `memory_bytes` stays a structural unknown,
        #: the unchanged Windows/stdlib behaviour. Set only by `build_resource_sampler`
        #: on POSIX, so the default sampler is byte-identical to before.
        self._memory_gauge = memory_gauge

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
            if gauge == GAUGE_MEMORY_BYTES and self._memory_gauge is not None:
                # POSIX: a LIVE resident-memory reading (/proc/meminfo) feeds the
                # unchanged `memory_bytes` breaker; a read failure returns a
                # sampling outage the loop already treats as a conservative pause.
                samples.append(self._memory_gauge())
            else:
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


# --------------------------------------------------------------------------
# Linux working-memory pause ceiling (D-091 T7, cloud loop design §5)
# --------------------------------------------------------------------------
#
# On Windows the resident-memory gauge is structurally unmeasurable stdlib-only
# (above), so it is reported as unknown and never pauses a cycle. On the shared
# Linux cloud box memory IS measurable from `/proc/meminfo`, and owner rule
# D-090-R076 requires the loop stay under 70% of physical memory (dropping from
# 5 lanes to 4 as it approaches). This block supplies that measurement and the
# pause ceiling, stdlib-only and injectable, WITHOUT changing the Windows
# sampler (`ResourceSampler.sample`) or the breaker (`circuit_breakers.py`): the
# existing gauge path enforces it when a Linux launcher feeds it these readings.

#: Owner rule D-090-R076 / design §5: pause at 70% of the MEASURED physical
#: total. The fraction encodes the owner rule; the ceiling in BYTES is DERIVED
#: from /proc/meminfo at resolve time, never a hard-coded byte count.
MEMORY_PAUSE_FRACTION = 0.70

#: The /proc/meminfo rows this module reads. MemAvailable is the kernel's own
#: estimate of memory obtainable without swapping; its ABSENCE (older kernels)
#: is a fail-closed condition, never an assumption that all memory is free.
MEMINFO_TOTAL = "MemTotal"
MEMINFO_AVAILABLE = "MemAvailable"


@dataclasses.dataclass(frozen=True)
class MemoryPauseVerdict:
    """Linux working-memory checked against the 70%-of-physical pause ceiling.

    `pause` is the fail-closed decision the loop acts on: True at/above the
    ceiling AND True whenever the gauge could not be read. `known` is False only
    in that unreadable case, so an operator can tell a real over-ceiling pause
    from a measurement failure.
    """

    known: bool
    pause: bool
    used_bytes: int | None = None
    total_bytes: int | None = None
    ceiling_bytes: int | None = None
    reason: str = ""


def read_proc_meminfo(reader: Callable[[], str] | None = None) -> dict[str, int]:
    """`/proc/meminfo` as a ``{row name: BYTES}`` mapping. Raises on any failure.

    `reader` returns the raw file text; the default reads `/proc/meminfo`. The
    kernel reports these rows in kB, so a ``kB`` value is converted to bytes and
    a unit-less value is taken verbatim. Injectable so a test drives any host's
    numbers (or a read failure) without touching the real host. Fail closed: a
    malformed row is skipped and a read error propagates to the caller, which
    pauses rather than inventing a reading.
    """
    text = (reader or _default_meminfo_text)()
    out: dict[str, int] = {}
    for line in text.splitlines():
        name, sep, rest = line.partition(":")
        if not sep:
            continue
        fields = rest.split()
        if not fields:
            continue
        try:
            amount = int(fields[0])
        except ValueError:
            continue
        unit = fields[1].lower() if len(fields) > 1 else ""
        out[name.strip()] = amount * 1024 if unit == "kb" else amount
    return out


def _working_memory(info: Mapping[str, int]) -> tuple[int, int]:
    """(physical total, working memory used) in bytes, or raise (fail closed).

    Used = MemTotal - MemAvailable. A missing row, a non-positive total, or an
    implausible pair (available negative or above total) raises rather than
    yielding a flattering low reading.
    """
    total = info[MEMINFO_TOTAL]
    available = info[MEMINFO_AVAILABLE]
    if (not isinstance(total, int) or not isinstance(available, int)
            or total <= 0 or available < 0 or available > total):
        raise ValueError(
            f"implausible /proc/meminfo: {MEMINFO_TOTAL}={total!r} "
            f"{MEMINFO_AVAILABLE}={available!r}")
    return total, total - available


def resolve_memory_ceiling_bytes(
    physical_total_bytes: int,
    *,
    configured_ceiling_bytes: int | None = None,
    fraction: float = MEMORY_PAUSE_FRACTION,
) -> int:
    """The memory pause ceiling in BYTES: no more than `fraction` of the MEASURED
    physical total, and never above a tighter owner-configured ceiling.

    ``min(configured, floor(fraction * physical))`` guarantees the loop pauses at
    or below 70% of real RAM regardless of what the config names, so leaving the
    8-GiB PC default in config.toml still yields ~5.6 GiB on an 8-GiB Linux box —
    the ceiling is derived from the box, not hard-coded (design §5). Raises on an
    implausible physical total or fraction (fail closed: no ceiling is invented).
    """
    if not isinstance(physical_total_bytes, int) or physical_total_bytes <= 0:
        raise ValueError(
            f"physical memory total must be a positive int, got "
            f"{physical_total_bytes!r}")
    if not isinstance(fraction, (int, float)) or not 0 < float(fraction) <= 1:
        raise ValueError(
            f"memory pause fraction must be in (0, 1], got {fraction!r}")
    ceiling = int(physical_total_bytes * float(fraction))
    if configured_ceiling_bytes is not None:
        if not isinstance(configured_ceiling_bytes, int) or configured_ceiling_bytes <= 0:
            raise ValueError(
                f"configured memory ceiling must be a positive int, got "
                f"{configured_ceiling_bytes!r}")
        ceiling = min(ceiling, configured_ceiling_bytes)
    return ceiling


def evaluate_linux_memory(
    *,
    meminfo_reader: Callable[[], str] | None = None,
    configured_ceiling_bytes: int | None = None,
    fraction: float = MEMORY_PAUSE_FRACTION,
) -> MemoryPauseVerdict:
    """Decide whether the loop must pause on memory, from `/proc/meminfo` alone.

    PAUSE when working memory (MemTotal - MemAvailable) is at or above the
    `resolve_memory_ceiling_bytes` ceiling (≤ 70% of measured physical). FAIL
    CLOSED (pause, `known=False`) when `/proc/meminfo` cannot be read or is
    missing/implausible — a guard that cannot read memory never assumes memory
    is fine (AD-025).
    """
    try:
        total, used = _working_memory(read_proc_meminfo(meminfo_reader))
        ceiling = resolve_memory_ceiling_bytes(
            total, configured_ceiling_bytes=configured_ceiling_bytes,
            fraction=fraction)
    except Exception as exc:
        return MemoryPauseVerdict(
            known=False, pause=True,
            reason=(f"/proc/meminfo unreadable ({type(exc).__name__}: {exc}); "
                    f"pausing rather than assuming memory is within limits "
                    f"(fail closed)"))
    pause = used >= ceiling
    pct = f"{fraction:.0%}"
    reason = (
        f"working memory {used} bytes {'>= ' if pause else 'below '}pause "
        f"ceiling {ceiling} bytes ({pct} of {total} physical)")
    return MemoryPauseVerdict(True, pause, used, total, ceiling, reason)


def linux_memory_gauge_sample(
    meminfo_reader: Callable[[], str] | None = None,
) -> GaugeSample:
    """A ``memory_bytes`` GaugeSample for the EXISTING loop resource gate on Linux.

    Returns the working-memory reading (``known=True``) so `_check_resources`
    trips it against `max_memory_bytes` with no change to loop.py or
    circuit_breakers.py — set that ceiling to `resolve_memory_ceiling_bytes(...)`
    and the unchanged breaker enforces the 70% pause ceiling. A read failure
    returns a sampling OUTAGE (``known=False, structural=False``), which the loop
    already treats as a conservative pause.
    """
    try:
        _total, used = _working_memory(read_proc_meminfo(meminfo_reader))
    except Exception as exc:
        return GaugeSample(
            gauge=GAUGE_MEMORY_BYTES, known=False, structural=False,
            reason=f"sampling outage: {type(exc).__name__}: {exc}")
    return GaugeSample(gauge=GAUGE_MEMORY_BYTES, known=True, value=used)


def posix_memory_ceiling_bytes(
    configured_ceiling_bytes: int | None,
    *,
    meminfo_reader: Callable[[], str] | None = None,
    fraction: float = MEMORY_PAUSE_FRACTION,
) -> int | None:
    """The launch-time `max_memory_bytes` breaker ceiling for THIS host, in bytes.

    On a non-POSIX host (Windows) returns None: resident memory is structurally
    unmeasurable stdlib-only there, so the caller leaves the configured ceiling
    untouched and the gauge stays a structural unknown (Windows byte-identical).

    On POSIX returns ``resolve_memory_ceiling_bytes(MemTotal, ...)`` = no more than
    `fraction` (70%, owner rule D-090-R076) of the MEASURED physical total read
    from /proc/meminfo, never above a tighter owner-configured ceiling, and never a
    hard-coded byte count. Fail closed: an unreadable, missing, or implausible
    /proc/meminfo RAISES rather than inventing or loosening a ceiling, so the loop
    never launches under an unmeasured memory ceiling (AD-025).
    """
    if os.name != "posix":
        return None
    physical_total = read_proc_meminfo(meminfo_reader)[MEMINFO_TOTAL]
    return resolve_memory_ceiling_bytes(
        physical_total, configured_ceiling_bytes=configured_ceiling_bytes,
        fraction=fraction)


def build_resource_sampler(
    *,
    disk_path: str,
    log_paths: Sequence[str] = (),
    meminfo_reader: Callable[[], str] | None = None,
) -> ResourceSampler:
    """A `ResourceSampler` wired for THIS host's resident-memory capability.

    On POSIX the `memory_bytes` gauge is live from /proc/meminfo
    (`linux_memory_gauge_sample`), so the unchanged `loop._check_resources` /
    breaker path enforces the resolved 70% ceiling. Off POSIX (Windows) no memory
    gauge is attached, so `memory_bytes` stays a structural unknown exactly as the
    plain `ResourceSampler` reports it — Windows behaviour is byte-identical.
    """
    memory_gauge = (
        partial(linux_memory_gauge_sample, meminfo_reader)
        if os.name == "posix" else None)
    return ResourceSampler(
        disk_path=disk_path, log_paths=log_paths, memory_gauge=memory_gauge)


def _default_meminfo_text() -> str:  # pragma: no cover - reads the real host
    with open("/proc/meminfo", "r", encoding="utf-8") as handle:
        return handle.read()


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
