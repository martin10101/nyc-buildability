#!/usr/bin/env python3
"""POSIX boundary inspection for the immutable controller config (D-091 T1).

The Linux analogue of `os_acl.py`. The owner directive D-091 moves the loop to a
Linux cloud server; the Windows OS-ACL boundary (`os_acl.py`, icacls + a UAC apply
script) does not exist there and already fails closed to UNKNOWN off-Windows. This
module asserts the SAME boundary on POSIX, with the SAME fail-closed verdict shape
(`os_acl.AclVerdict` / `os_acl.ControllerConfigAclVerdict`, states PROTECTED /
NOT_PROTECTED / UNKNOWN), so a single cross-platform entry point
(`os_acl.controller_config_acl_verdict`) and the doctor posture surface read one
shape on both platforms.

The POSIX boundary and why each clause is the right analogue of the Windows one:

  * **root-owned (st_uid == 0).** On POSIX the OWNER of a file may always `chmod`
    it, regardless of the mode bits - so a config at mode 0444 owned by an
    unprivileged user is still effectively writable by that user (they can add the
    write bit back). A non-root owner therefore defeats the boundary exactly the
    way a non-elevated Windows owner does by retaining implicit WRITE_DAC
    (`os_acl._confirm_owner_elevated`, G5 L-1). root-ownership is the POSIX
    requirement that corresponds to the elevated-owner requirement.
  * **not group- or world-writable.** The DACL analogue: no unprivileged principal
    may hold a write right on the object itself. Owner (root) write is expected and
    is the privileged/elevated action, like Administrators full control on Windows.
  * **protected parent directory.** A group/world-writable parent lets an
    unprivileged user rename or replace the config even when the file itself is
    read-only (the ADD_FILE / DELETE_CHILD analogue of `os_acl.evaluate_directory`).
  * **no symlinks.** A symlinked config or parent can be repointed at an
    attacker-controlled target - an active bypass - so it fails closed to
    NOT_PROTECTED (the safer, more-actionable direction, mirroring the os_acl rule
    that a writable probe beats a clean-looking ACL). Scope matches os_acl: the file
    and its immediate parent are checked, not every ancestor.

Fail-closed, like os_acl: a missing config, an unreadable owner/stat, or a
non-POSIX platform is UNKNOWN, and UNKNOWN is NEVER read as protected.

Stdlib only. No third-party dependency. The stat/owner lookup is injectable
(`lstat`) and the platform decision is injectable (`is_posix`) so every verdict is
testable on any host without root - the test supplies a fake stat result and forces
the platform branch.
"""
from __future__ import annotations

import os
import pathlib
import stat as stat_module
from typing import Any, Callable

from .os_acl import (
    NOT_PROTECTED,
    PROTECTED,
    UNKNOWN,
    AclVerdict,
    ControllerConfigAclVerdict,
)

#: Type of the injectable stat lookup. The production default is ``os.lstat``;
#: it does NOT follow a final symlink, so a symlinked target is detectable. Only
#: ``st_uid`` and ``st_mode`` are read, so a test fake needs only those two fields.
StatFunc = Callable[[str], Any]

#: The owner uid that counts as privileged on POSIX. root (0) is the elevated
#: owner; everyone else can chmod their own file and re-grant write.
ROOT_UID = 0


def _is_posix(is_posix: bool | None) -> bool:
    """Resolve the platform decision, injectable for tests on any host."""
    return os.name == "posix" if is_posix is None else is_posix


def _unknown(target: str, kind: str, reason: str,
             evidence: dict[str, Any] | None = None) -> AclVerdict:
    return AclVerdict(UNKNOWN, target, kind, (reason,), evidence or {})


def _evaluate_node(path: str | os.PathLike[str], *, kind: str,
                   lstat: StatFunc, is_posix: bool | None) -> AclVerdict:
    """Fail-closed verdict for one path (the config FILE or its PARENT directory).

    OK (PROTECTED) only when the node is root-owned, not group- or world-writable,
    and not a symlink. Anything else is NOT_PROTECTED with a named reason; a
    missing node, an unreadable stat, or a non-POSIX platform is UNKNOWN.
    """
    target = str(path)
    if not _is_posix(is_posix):
        return _unknown(target, kind,
                        "not a POSIX platform; the root-ownership boundary is "
                        "POSIX-specific and cannot be asserted here")
    try:
        st = lstat(target)
    except FileNotFoundError:
        return _unknown(target, kind,
                        f"the controller config {kind} does not exist; protection of a "
                        f"missing {kind} cannot be asserted")
    except OSError as exc:
        return _unknown(target, kind,
                        f"the {kind} could not be stat'd ({exc.__class__.__name__}); "
                        f"failing closed - an unresolvable owner/mode is not proof of "
                        f"protection")

    mode = st.st_mode
    uid = st.st_uid
    evidence: dict[str, Any] = {
        "uid": uid,
        "mode": format(stat_module.S_IMODE(mode), "04o"),
        "is_symlink": bool(stat_module.S_ISLNK(mode)),
    }

    if stat_module.S_ISLNK(mode):
        return AclVerdict(
            NOT_PROTECTED, target, kind,
            (f"the {kind} is a symlink; a symlinked target can be repointed at an "
             f"attacker-controlled path and is never trusted as the protected "
             f"{kind}",),
            evidence)

    if uid != ROOT_UID:
        return AclVerdict(
            NOT_PROTECTED, target, kind,
            (f"the {kind} is owned by uid {uid}, not root (0); a non-root owner can "
             f"chmod it and re-grant itself write (the POSIX analogue of WRITE_DAC), "
             f"so the boundary is defeated even at a read-only mode",),
            evidence)

    writable_bits = mode & (stat_module.S_IWGRP | stat_module.S_IWOTH)
    if writable_bits:
        offenders = []
        if mode & stat_module.S_IWGRP:
            offenders.append("group")
        if mode & stat_module.S_IWOTH:
            offenders.append("world")
        return AclVerdict(
            NOT_PROTECTED, target, kind,
            (f"the {kind} is {'- and '.join(offenders)}-writable (mode "
             f"{evidence['mode']}); an unprivileged process could modify it",),
            evidence)

    return AclVerdict(
        PROTECTED, target, kind,
        (f"the {kind} is root-owned (uid 0), not group- or world-writable (mode "
         f"{evidence['mode']}), and not a symlink; only root (the elevated owner) "
         f"may modify it",),
        evidence)


def evaluate_file(path: str | os.PathLike[str], *, lstat: StatFunc = os.lstat,
                  is_posix: bool | None = None) -> AclVerdict:
    """Fail-closed POSIX verdict for the config FILE."""
    return _evaluate_node(path, kind="file", lstat=lstat, is_posix=is_posix)


def evaluate_directory(path: str | os.PathLike[str], *, lstat: StatFunc = os.lstat,
                       is_posix: bool | None = None) -> AclVerdict:
    """Fail-closed POSIX verdict for the PARENT DIRECTORY."""
    return _evaluate_node(path, kind="directory", lstat=lstat, is_posix=is_posix)


def _combine(file_v: AclVerdict, parent_v: AclVerdict) -> str:
    """Combine the file and parent verdicts (the same rule as
    `os_acl.ControllerConfigAclVerdict`: PROTECTED requires BOTH; a single
    NOT_PROTECTED wins over UNKNOWN as the stronger, more-actionable fact; a
    missing/ambiguous pair stays UNKNOWN and never reads as protected)."""
    if file_v.state == PROTECTED and parent_v.state == PROTECTED:
        return PROTECTED
    if NOT_PROTECTED in (file_v.state, parent_v.state):
        return NOT_PROTECTED
    return UNKNOWN


def evaluate_controller_config_acl(
        config_path: str | os.PathLike[str], *, lstat: StatFunc = os.lstat,
        is_posix: bool | None = None) -> ControllerConfigAclVerdict:
    """The single POSIX entry point: fail-closed verdict for the config FILE and
    its PARENT directory, PROTECTED only when BOTH are protected. Returns the same
    `ControllerConfigAclVerdict` shape `os_acl` returns on Windows."""
    p = pathlib.Path(config_path)
    file_v = evaluate_file(p, lstat=lstat, is_posix=is_posix)
    parent_v = evaluate_directory(p.parent, lstat=lstat, is_posix=is_posix)
    return ControllerConfigAclVerdict(_combine(file_v, parent_v), file_v, parent_v)
