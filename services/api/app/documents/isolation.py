"""Fail-closed parser-isolation capability gate (application-level; M2-T015, R275-R276).

Deterministic capability probe and gate for the parser isolation boundary of
``docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md`` section 5: parsing of untrusted
document bytes is permitted ONLY behind a kernel-enforced boundary with BOTH mandatory
properties — Landlock LSM filesystem isolation and seccomp-BPF network denial. A plain
child process is not that boundary; process separation never suffices to enable parsing.

This module probes the platform facts — host os name, kernel release string, Landlock
ABI availability, seccomp availability — via stdlib-only introspection. No child
process is ever spawned by a probe, and no ctypes syscall is ever attempted on a
non-Linux host: there, every Linux-only capability is UNAVAILABLE by construction.
The result is the frozen :class:`IsolationCapability` carrying those facts plus the
typed verdict, reusing the typed-result pattern of :mod:`app.documents.units`
(frozen value results, refusal-as-value, never an exception).

Fail-closed rule: absence of evidence is always DISABLED, never a warning. A probe
error, an unknown platform, an unreadable kernel interface, or partial detection each
yields :class:`ParsingDisabled` naming the capability that failed and why.
:class:`ParsingPermitted` is returned ONLY when every required capability is
affirmatively PROVEN available — Linux, plus Landlock, plus seccomp, all positively
detected. The verdict attests capability PRESENCE on the running kernel; actually
applying the boundary (the Landlock ruleset, the seccomp filter installed with
``no_new_privs``, and the canary self-verification before the first untrusted byte)
remains the isolated parser path's duty per section 5 — presence here never
substitutes for applied, self-verified enforcement there.

There is deliberately NO override parameter, NO environment-variable bypass, and NO
config flag anywhere in this module that could enable parsing without a proven
boundary. Production-substrate enablement is deployment-gated under B-001 (Render
Linux substrate verification per section 5's honest substrate statement); Linux CI is
where the real extraction path runs (R274). Windows/macOS hosts therefore always
receive :class:`ParsingDisabled`.
"""

from __future__ import annotations

import platform
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "CapabilityProbe",
    "IsolationCapability",
    "ParsingDisabled",
    "ParsingPermitted",
    "ParsingVerdict",
    "require_isolation",
]

_LINUX = "Linux"

#: Landlock syscall facts (``include/uapi/linux/landlock.h``): the
#: ``landlock_create_ruleset`` syscall number is architecture-uniform (post-unification
#: syscall table), and passing the version flag with a null ruleset attribute is the
#: kernel-documented read-only ABI query — it creates nothing and restricts nothing.
_SYS_LANDLOCK_CREATE_RULESET = 444
_LANDLOCK_CREATE_RULESET_VERSION = 1

_ACTIVE_LSM_PATH = "/sys/kernel/security/lsm"
_SECCOMP_STATUS_PATH = "/proc/self/status"
_SECCOMP_ACTIONS_PATH = "/proc/sys/kernel/seccomp/actions_avail"


# ------------------------------------------------------------------ typed results


@dataclass(frozen=True)
class CapabilityProbe:
    """One probed platform fact: whether a required capability is AFFIRMATIVELY
    available on this host, with the stated evidence or the stated failure reason."""

    capability: str
    available: bool
    detail: str


@dataclass(frozen=True)
class ParsingPermitted:
    """Typed PERMITTED verdict: every required capability (Linux kernel, Landlock,
    seccomp) was positively detected on this host.

    Presence only: the isolated parser path must still apply and self-verify the full
    boundary policy before reading any untrusted byte (architecture section 5).
    """

    permitted = True


@dataclass(frozen=True)
class ParsingDisabled:
    """Typed refusal of parsing — the ``isolation_unavailable`` outcome of
    architecture section 5, carrying which capability failed and why.

    Deliberately a value, never an exception: an unprovable boundary is a routine
    fail-closed outcome the caller must surface — documents rest in ``uploaded``,
    nothing silently degrades, and there is no fallback to unisolated parsing. The
    payload is metadata only and safe to serialize into an API response or audit
    record.
    """

    failed_capability: str
    reason: str

    permitted = False
    reject_code = "isolation_unavailable"

    def to_payload(self) -> dict:
        """Structured refusal payload (metadata only, JSON-serializable)."""
        return {
            "reject_code": self.reject_code,
            "failed_capability": self.failed_capability,
            "reason": self.reason,
        }


ParsingVerdict = ParsingPermitted | ParsingDisabled


@dataclass(frozen=True)
class IsolationCapability:
    """Frozen result of one capability probe run: the probed platform facts plus the
    derived fail-closed verdict."""

    os_name: str
    kernel_release: str
    landlock: CapabilityProbe
    seccomp: CapabilityProbe
    verdict: ParsingVerdict


# ------------------------------------------------------------------- probe seams


def _probe_os_name() -> str:
    """Host operating-system name (``'Linux'``, ``'Windows'``, ``'Darwin'``, …)."""
    return platform.system()


def _probe_kernel_release() -> str:
    """Host kernel release string (e.g. ``'6.8.0-1024-aws'``)."""
    return platform.release()


def _probe_landlock(os_name: str) -> CapabilityProbe:
    """Affirmative Landlock detection: active LSM listing plus a readable ABI version.

    Linux-only by construction; the ctypes ABI query is reached only inside the Linux
    branch and is the read-only version query, never a ruleset application.
    """
    if os_name != _LINUX:
        return CapabilityProbe(
            capability="landlock",
            available=False,
            detail=(
                f"Landlock is a Linux-only kernel LSM; on host os {os_name!r} it is "
                "UNAVAILABLE by construction"
            ),
        )
    try:
        active_lsms = Path(_ACTIVE_LSM_PATH).read_text(encoding="ascii").strip()
    except OSError as exc:
        return CapabilityProbe(
            capability="landlock",
            available=False,
            detail=(
                f"cannot read the active LSM list at {_ACTIVE_LSM_PATH} ({exc}); an "
                "unprovable boundary is unavailable"
            ),
        )
    if "landlock" not in active_lsms.split(","):
        return CapabilityProbe(
            capability="landlock",
            available=False,
            detail=(
                "'landlock' is not among the running kernel's active LSMs "
                f"({active_lsms!r})"
            ),
        )
    try:
        import ctypes  # Linux-only branch: never reached on a non-Linux host

        libc = ctypes.CDLL(None, use_errno=True)
        libc.syscall.restype = ctypes.c_long
        abi = libc.syscall(
            ctypes.c_long(_SYS_LANDLOCK_CREATE_RULESET),
            None,
            ctypes.c_size_t(0),
            ctypes.c_uint32(_LANDLOCK_CREATE_RULESET_VERSION),
        )
        if abi < 1:
            errno = ctypes.get_errno()
            return CapabilityProbe(
                capability="landlock",
                available=False,
                detail=(
                    f"landlock_create_ruleset ABI query returned {abi} (errno "
                    f"{errno}); the Landlock ABI is not affirmatively available"
                ),
            )
    except Exception as exc:  # noqa: BLE001 — ANY query failure is unavailability
        return CapabilityProbe(
            capability="landlock",
            available=False,
            detail=(
                f"Landlock ABI query failed: {exc}; a failed probe is never treated "
                "as available"
            ),
        )
    return CapabilityProbe(
        capability="landlock",
        available=True,
        detail=f"active LSM with Landlock ABI version {abi}",
    )


def _probe_seccomp(os_name: str) -> CapabilityProbe:
    """Affirmative seccomp detection: the kernel exposes the ``Seccomp`` process field
    AND filter-mode action support. Linux-only by construction."""
    if os_name != _LINUX:
        return CapabilityProbe(
            capability="seccomp",
            available=False,
            detail=(
                f"seccomp is a Linux-only kernel facility; on host os {os_name!r} it "
                "is UNAVAILABLE by construction"
            ),
        )
    try:
        status = Path(_SECCOMP_STATUS_PATH).read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return CapabilityProbe(
            capability="seccomp",
            available=False,
            detail=(
                f"cannot read {_SECCOMP_STATUS_PATH} ({exc}); seccomp support is "
                "unprovable and therefore unavailable"
            ),
        )
    if not any(line.startswith("Seccomp:") for line in status.splitlines()):
        return CapabilityProbe(
            capability="seccomp",
            available=False,
            detail=(
                f"no 'Seccomp' field in {_SECCOMP_STATUS_PATH}: the running kernel "
                "does not affirmatively report seccomp support"
            ),
        )
    try:
        actions = Path(_SECCOMP_ACTIONS_PATH).read_text(encoding="ascii").strip()
    except OSError as exc:
        return CapabilityProbe(
            capability="seccomp",
            available=False,
            detail=(
                f"cannot read {_SECCOMP_ACTIONS_PATH} ({exc}); seccomp-BPF filter "
                "support is not affirmatively available"
            ),
        )
    if not actions:
        return CapabilityProbe(
            capability="seccomp",
            available=False,
            detail=(
                f"{_SECCOMP_ACTIONS_PATH} is empty; seccomp filter actions are not "
                "affirmatively available"
            ),
        )
    return CapabilityProbe(
        capability="seccomp",
        available=True,
        detail=f"seccomp filter available (actions_avail: {actions})",
    )


# ---------------------------------------------------------------------- the gate


def _guarded_probe(
    capability: str, probe: Callable[[], CapabilityProbe]
) -> CapabilityProbe:
    """Run one capability probe; a raising probe IS unavailability, never a crash."""
    try:
        return probe()
    except Exception as exc:  # noqa: BLE001 — ANY probe failure disables parsing
        return CapabilityProbe(
            capability=capability,
            available=False,
            detail=(
                f"{capability} probe raised {type(exc).__name__}: {exc}; a failed "
                "probe is never treated as available"
            ),
        )


def _derive_verdict(
    os_name: str, landlock: CapabilityProbe, seccomp: CapabilityProbe
) -> ParsingVerdict:
    """Fail-closed verdict: permitted ONLY on full affirmative proof; first missing
    mandatory property named in section 5's order (Landlock, then seccomp)."""
    if os_name != _LINUX:
        return ParsingDisabled(
            failed_capability="os",
            reason=(
                f"parser isolation requires a Linux kernel; host platform {os_name!r} "
                "cannot provide Landlock or seccomp, so parsing is disabled by "
                "construction"
            ),
        )
    if not landlock.available:
        return ParsingDisabled(failed_capability="landlock", reason=landlock.detail)
    if not seccomp.available:
        return ParsingDisabled(failed_capability="seccomp", reason=seccomp.detail)
    return ParsingPermitted()


def require_isolation() -> IsolationCapability:
    """Fail-closed parser-isolation gate: the SINGLE entry extraction code calls
    before ANY untrusted-byte decode.

    Returns the frozen :class:`IsolationCapability` whose ``verdict`` is
    :class:`ParsingPermitted` ONLY when every required capability is affirmatively
    PROVEN available on this host — a Linux kernel with Landlock (active LSM and a
    queryable ABI) and seccomp (filter support) both positively detected — and
    otherwise :class:`ParsingDisabled` carrying which capability failed and why.
    Absence of evidence is always DISABLED, never a warning: probe errors, unknown
    platforms, and partial detection all disable parsing.

    This function deliberately takes NO arguments and consults NO ambient state:
    there is NO override parameter, NO environment-variable bypass, and NO config
    flag that can enable parsing without a proven kernel-enforced boundary.
    Production-substrate enablement is deployment-gated under B-001 (Render Linux
    substrate verification, architecture section 5's honest substrate statement);
    Linux CI is where the real extraction path runs (R274). Windows and macOS hosts
    therefore always receive :class:`ParsingDisabled`.
    """
    try:
        os_name = _probe_os_name()
        kernel_release = _probe_kernel_release()
    except Exception as exc:  # noqa: BLE001 — an unprobable platform disables parsing
        not_probed = "not probed: the platform probe itself failed"
        return IsolationCapability(
            os_name="<unprobed>",
            kernel_release="<unprobed>",
            landlock=CapabilityProbe(
                capability="landlock", available=False, detail=not_probed
            ),
            seccomp=CapabilityProbe(
                capability="seccomp", available=False, detail=not_probed
            ),
            verdict=ParsingDisabled(
                failed_capability="os",
                reason=(
                    f"platform probe raised {type(exc).__name__}: {exc}; an "
                    "unprobable platform is never parsed on"
                ),
            ),
        )
    landlock = _guarded_probe("landlock", lambda: _probe_landlock(os_name))
    seccomp = _guarded_probe("seccomp", lambda: _probe_seccomp(os_name))
    return IsolationCapability(
        os_name=os_name,
        kernel_release=kernel_release,
        landlock=landlock,
        seccomp=seccomp,
        verdict=_derive_verdict(os_name, landlock, seccomp),
    )
