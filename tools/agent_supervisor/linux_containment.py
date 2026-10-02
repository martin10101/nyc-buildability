#!/usr/bin/env python3
"""Linux systemd control-group containment proof (M0-T177, B-027; D-091-R001/R007).

Qualifying evidence: B-027 (reproduced defect) — the Linux loop cannot start a
live worker because the ONLY accepted containment is the Windows Job Object, and
no POSIX mechanism proves the safety property the M0-T052 G5 C1 pin requires:

    when the supervisor dies by ANY external means (SIGKILL, OOM), the worker AND
    every descendant (including `setsid`/double-fork grandchildren) end WITHOUT
    relying on anything inside the supervisor running, and that reaping completes
    before any later `start` can dispatch.

On Linux that property is delivered by systemd: when the unit's main process
dies, systemd stops the service and tears down the service control group
(`KillMode=control-group`/`mixed`), SIGKILLing every remaining member after a
bounded `TimeoutStopSec`. A non-root process cannot leave its control group, and
any later `systemctl start` waits behind the stop job.

This module is the IN-PROCESS proof that the running process actually IS in that
situation. It PROVES, it never assumes: every input (the process cgroup, the
unit's `systemctl show` properties) is READ at runtime, and ANYTHING missing,
unreadable, garbled, timed out, or inconsistent is a REFUSAL with a precise
reason — never a default-to-safe guess.

Everything is injectable (the cgroup reader, the `systemctl show` runner, pid,
euid) so the whole proof is unit-tested with no real systemd and on any host.
"""
from __future__ import annotations

import dataclasses
import os
import re
from typing import Callable, Sequence

#: Properties read from `systemctl show <unit>` in one bounded, no-shell call.
SYSTEMCTL_PROPERTIES: tuple[str, ...] = (
    "KillMode", "ExitType", "MainPID", "ControlGroup",
    "SendSIGKILL", "TimeoutStopUSec", "ProtectControlGroups",
)

#: KillMode values under which systemd kills the WHOLE control group on stop.
#: `process`/`none`/`mixed`: `process` and `none` leave descendants alive, so
#: only `control-group` and `mixed` are accepted (`mixed` SIGTERMs the main
#: process but SIGKILLs the whole group, which still reaps every descendant).
ACCEPTED_KILL_MODES: frozenset[str] = frozenset({"control-group", "mixed"})

#: Bounded cap on the service stop timeout, in microseconds. systemd SIGKILLs the
#: remaining control-group members `TimeoutStopSec` AFTER a stop begins; an
#: unbounded (`infinity`) or long timeout would let an orphaned worker linger past
#: a later `start`, defeating the "reaping completes before any later start can
#: dispatch" half of the property. 60 s is chosen as the cap: comfortably above
#: the hardened template's 15 s (so the template passes with margin) and well
#: under systemd's 90 s default (so a unit left at the default is REFUSED, forcing
#: an explicit short bound). A value above the cap is refused as "not bounded".
MAX_TIMEOUT_STOP_USEC: int = 60 * 1_000_000

#: Short timeout for the `systemctl show` probe. The probe is a local, read-only
#: status query; anything slower than this is treated as unreadable (a refusal).
SHOW_TIMEOUT_SECONDS: float = 5.0

#: systemd timespan units -> microseconds (systemd.time(7)). Deliberately a SMALL
#: set: a value using any other unit is unparseable and therefore REFUSED
#: (fail-closed), never silently coerced.
_TIMESPAN_UNIT_USEC: dict[str, int] = {
    "us": 1, "usec": 1, "µs": 1,
    "ms": 1_000, "msec": 1_000,
    "s": 1_000_000, "sec": 1_000_000, "second": 1_000_000, "seconds": 1_000_000,
    "min": 60_000_000, "minute": 60_000_000, "minutes": 60_000_000,
    "h": 3_600_000_000, "hr": 3_600_000_000, "hour": 3_600_000_000, "hours": 3_600_000_000,
    "d": 86_400_000_000, "day": 86_400_000_000, "days": 86_400_000_000,
}
_TIMESPAN_TOKEN = re.compile(r"(\d+(?:\.\d+)?)\s*([a-zµ]+)")

#: Reader/runner seam types.
CgroupReader = Callable[[], str]
ShowRunner = Callable[[str, Sequence[str]], "tuple[int, str, str]"]


@dataclasses.dataclass(frozen=True)
class ContainmentProof:
    """A typed proof result. `ok` is True ONLY when every condition was PROVED.

    `kind` is the containment kind the host actually offers: ``systemd_cgroup``
    when proved, ``process_group`` on any refusal (the honest POSIX fallback).
    `reason` always explains the verdict. `cgroup_path`/`unit` are populated only
    on a proof, so a caller can verify a worker's membership against the SAME path.
    """

    ok: bool
    kind: str
    reason: str
    cgroup_path: str = ""
    unit: str = ""

    @classmethod
    def proved(cls, cgroup_path: str, unit: str) -> "ContainmentProof":
        return cls(
            ok=True, kind="systemd_cgroup",
            reason=(f"proved: this process is the main process of systemd unit {unit!r} "
                    f"(cgroup {cgroup_path!r}) whose control group the kernel tears down "
                    f"on stop"),
            cgroup_path=cgroup_path, unit=unit)

    @classmethod
    def refused(cls, reason: str) -> "ContainmentProof":
        return cls(ok=False, kind="process_group", reason=reason)


# --------------------------------------------------------------------------
# Default readers (the real /proc + systemctl seam; replaced wholesale in tests)
# --------------------------------------------------------------------------


def _read_self_cgroup() -> str:
    with open("/proc/self/cgroup", "r", encoding="utf-8") as handle:
        return handle.read()


def _read_pid_cgroup(pid: int) -> str:
    with open(f"/proc/{pid}/cgroup", "r", encoding="utf-8") as handle:
        return handle.read()


def _default_show_runner(unit: str, properties: Sequence[str],
                         *, timeout: float = SHOW_TIMEOUT_SECONDS) -> tuple[int, str, str]:
    """Run ``systemctl show <unit> -p <props>`` via the package's bounded,
    no-shell `process.run` (imported lazily to avoid an import cycle)."""
    from . import process as _process  # lazy: process.py imports this module

    argv = ["systemctl", "show", unit, "-p", ",".join(properties)]
    result = _process.run(argv, timeout=timeout, use_job_object=False)
    return result.returncode, result.stdout or "", result.stderr or ""


# --------------------------------------------------------------------------
# Pure parsers
# --------------------------------------------------------------------------


def parse_cgroup_v2_path(content: str) -> str | None:
    """Return the unified cgroup-v2 path from /proc/<x>/cgroup content, or None.

    A PURE cgroup-v2 hierarchy has EXACTLY ONE line, ``0::<absolute-path>``. A
    cgroup-v1 or hybrid host has several controller lines, so it returns None and
    is refused by the caller: this gate's kill semantics only hold under unified
    v2 (the kernel's single-hierarchy membership a non-root process cannot leave).
    """
    lines = [ln for ln in content.splitlines() if ln.strip()]
    if len(lines) != 1:
        return None
    line = lines[0]
    if not line.startswith("0::"):
        return None
    path = line[3:]
    if not path.startswith("/"):
        return None
    return path


def parse_show_output(text: str) -> dict[str, str]:
    """Parse ``KEY=VALUE`` lines from `systemctl show` output into a dict."""
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or "=" not in line:
            continue
        key, _, value = line.partition("=")
        out[key.strip()] = value.strip()
    return out


def parse_systemd_usec(value: str) -> int | None:
    """Parse a systemd ``*USec`` value to microseconds; None when unbounded or
    unparseable.

    `systemctl show` may report the value either as a raw microsecond integer or
    as a human timespan (``15s``, ``1min 30s``, ``500ms``). ``infinity`` (and a
    zero/empty value, which also means "no bound") returns None. Any token using
    an unrecognized unit, or trailing junk, returns None — fail-closed, so a
    value this function cannot fully account for is treated as unbounded and
    refused by the caller.
    """
    v = value.strip().lower()
    if not v or v == "infinity":
        return None
    if v.isdigit():
        iv = int(v)
        return iv if iv > 0 else None
    total = 0.0
    pos = 0
    matched = False
    for match in _TIMESPAN_TOKEN.finditer(v):
        if match.start() != pos:  # an unparsed gap before this token
            return None
        unit = match.group(2)
        if unit not in _TIMESPAN_UNIT_USEC:
            return None
        total += float(match.group(1)) * _TIMESPAN_UNIT_USEC[unit]
        pos = match.end()
        while pos < len(v) and v[pos] == " ":
            pos += 1
        matched = True
    if not matched or pos != len(v):
        return None
    iv = int(total)
    return iv if iv > 0 else None


def unit_from_cgroup_path(path: str) -> str:
    """The unit name is the last component of the service cgroup path."""
    return path.rsplit("/", 1)[-1]


# --------------------------------------------------------------------------
# The proof
# --------------------------------------------------------------------------


def prove_systemd_containment(
    *,
    pid: int | None = None,
    euid: int | None = None,
    cgroup_reader: CgroupReader | None = None,
    show_runner: ShowRunner | None = None,
    timeout: float = SHOW_TIMEOUT_SECONDS,
    max_timeout_stop_usec: int = MAX_TIMEOUT_STOP_USEC,
) -> ContainmentProof:
    """Prove this process is the main process of a hardened systemd .service whose
    control group the kernel reaps on stop. Returns a typed `ContainmentProof`;
    ANY unreadable/garbled/inconsistent input is a refusal, never an assumption.
    """
    if os.name == "nt":
        return ContainmentProof.refused("not a POSIX host; systemd containment does not apply")

    this_pid = os.getpid() if pid is None else pid
    this_euid = (os.geteuid() if euid is None else euid)  # geteuid: POSIX only, guarded above
    read_cgroup = cgroup_reader or _read_self_cgroup
    run_show = show_runner or (lambda unit, props: _default_show_runner(unit, props, timeout=timeout))

    # 1. Our own cgroup must be a pure cgroup-v2 .service path.
    try:
        content = read_cgroup()
    except Exception as exc:  # unreadable /proc/self/cgroup
        return ContainmentProof.refused(f"/proc/self/cgroup could not be read ({exc})")
    path = parse_cgroup_v2_path(content)
    if path is None:
        return ContainmentProof.refused(
            "not a pure cgroup-v2 hierarchy: exactly one '0::<path>' line is required "
            "(a cgroup-v1 or hybrid host, or an unreadable cgroup, is refused)")
    if not path.endswith(".service"):
        return ContainmentProof.refused(
            f"the control-group path {path!r} is not a systemd .service (a .scope or "
            f"user-session path does not give service-stop control-group kill semantics)")
    unit = unit_from_cgroup_path(path)

    # 2. Read the unit's live properties.
    try:
        code, out, err = run_show(unit, SYSTEMCTL_PROPERTIES)
    except Exception as exc:  # systemctl missing / did not launch / timed out
        return ContainmentProof.refused(
            f"`systemctl show {unit}` could not run ({exc}); an unreadable unit state is a refusal")
    if code != 0:
        return ContainmentProof.refused(
            f"`systemctl show {unit}` exited {code} (stderr {err.strip()[:200]!r}); "
            f"an unreadable unit state is a refusal")
    props = parse_show_output(out)
    missing = [key for key in SYSTEMCTL_PROPERTIES if key not in props]
    if missing:
        return ContainmentProof.refused(
            f"`systemctl show {unit}` did not report {missing}; a garbled or partial unit "
            f"state is a refusal")

    # 3. The control-group kill semantics.
    kill_mode = props["KillMode"]
    if kill_mode not in ACCEPTED_KILL_MODES:
        return ContainmentProof.refused(
            f"KillMode={kill_mode!r}; only {sorted(ACCEPTED_KILL_MODES)} tear down the whole "
            f"control group on stop (KillMode=process/none leave descendants alive)")

    exit_type = props["ExitType"]
    if exit_type != "main":
        return ContainmentProof.refused(
            f"ExitType={exit_type!r}; ExitType=main is required so systemd ties the unit's "
            f"lifetime to THIS process dying (ExitType=cgroup would wait for the group to empty)")

    try:
        main_pid = int(props["MainPID"])
    except (TypeError, ValueError):
        return ContainmentProof.refused(f"MainPID={props['MainPID']!r} is not an integer")
    if main_pid != this_pid:
        return ContainmentProof.refused(
            f"MainPID={main_pid} but this process is {this_pid}; the proof holds only for the "
            f"unit's MAIN process (a child cannot prove the service stops when IT dies)")

    control_group = props["ControlGroup"]
    if control_group != path:
        return ContainmentProof.refused(
            f"systemctl ControlGroup={control_group!r} does not match our cgroup {path!r}; "
            f"a mismatch means we are not the process systemd will reap")

    send_sigkill = props["SendSIGKILL"].lower()
    if send_sigkill != "yes":
        return ContainmentProof.refused(
            f"SendSIGKILL={props['SendSIGKILL']!r}; without SendSIGKILL=yes a member that "
            f"ignores SIGTERM survives the stop, so the kill is not guaranteed")

    usec = parse_systemd_usec(props["TimeoutStopUSec"])
    if usec is None:
        return ContainmentProof.refused(
            f"TimeoutStopUSec={props['TimeoutStopUSec']!r} is infinite, zero, or unparseable; a "
            f"finite bounded stop timeout is required so a lingering worker cannot outlast a "
            f"later start")
    if usec > max_timeout_stop_usec:
        return ContainmentProof.refused(
            f"TimeoutStopUSec={props['TimeoutStopUSec']!r} ({usec} us) exceeds the "
            f"{max_timeout_stop_usec} us ({max_timeout_stop_usec // 1_000_000} s) cap; the SIGKILL "
            f"that reaps the control group must arrive within a bounded, short window")

    # 4. Root hardening: a root worker could otherwise rewrite cgroup membership to
    #    escape the kill unless the service tree is made read-only to it.
    if this_euid == 0:
        protect = props["ProtectControlGroups"].lower()
        if protect != "yes":
            return ContainmentProof.refused(
                f"running as root (euid 0) requires ProtectControlGroups=yes so a compromised "
                f"root member cannot rewrite its cgroup to escape the kill; got "
                f"ProtectControlGroups={props['ProtectControlGroups']!r}")

    return ContainmentProof.proved(path, unit)


def pid_in_service_cgroup(pid: int, expected_cgroup: str,
                          *, reader: CgroupReader | None = None) -> bool:
    """True when /proc/<pid>/cgroup places <pid> in EXACTLY `expected_cgroup`.

    Fail-closed: an unreadable, garbled, v1/hybrid, or different cgroup is False.
    Used to VERIFY (not assume) that an adopted worker really is a member of the
    supervisor's own service control group, so the kernel-level kill covers it.
    """
    if not expected_cgroup:
        return False
    read = reader or (lambda: _read_pid_cgroup(pid))
    try:
        content = read()
    except Exception:
        return False
    path = parse_cgroup_v2_path(content)
    if path is None:
        return False
    return path == expected_cgroup
