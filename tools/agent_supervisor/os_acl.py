#!/usr/bin/env python3
"""Windows OS-ACL boundary inspection for the immutable controller config.

M0-T046 SCOPE 3 (D-010-R127/R128). Owner decision (source-012-amendment.md): the
current single-account writable ACL is NOT sufficient for supervised-auto
activation. The required boundary is:

  * the ordinary UNELEVATED supervisor process may READ the controller config;
  * it must NOT be able to modify, overwrite, delete, rename, replace, or change
    ACLs on it;
  * the PARENT DIRECTORY is protected against replacement/bypass too;
  * modification requires an elevated owner action (Windows UAC);
  * the existing fail-closed digest/identity verification (config.py) is retained.

This module INSPECTS and PROBES that boundary FROM an unelevated process and emits
a single fail-closed verdict (PROTECTED / NOT_PROTECTED / UNKNOWN) for the config
FILE and for its PARENT DIRECTORY. It:

  * NEVER attempts elevation and NEVER repairs anything;
  * uses only BOUNDED, NON-DESTRUCTIVE probes - it reads the ACL (icacls) and
    attempts a single open-for-write that WRITES NO BYTES, so it cannot damage a
    correctly-protected target and needs to restore nothing. It does NOT perform a
    live rename/delete/ACL-change against the real target (a successful such
    attempt on a not-yet-protected config would itself damage it); rename/delete/
    replace/ACL-change protection is assessed from the governing ACL RIGHTS, which
    is exactly what the OS enforces those operations from;
  * FAILS CLOSED on ANY ambiguity or probe error - an unresolvable state is
    UNKNOWN, and UNKNOWN is NEVER read as "protected".

The elevated apply/rollback is `harden_controller_config.ps1`, which the OWNER
runs via UAC. Applying the hardening is out of scope for this unelevated module.

Stdlib only. No third-party dependency. On a non-Windows platform the Windows ACL
boundary cannot be asserted, so the verdict is UNKNOWN (fail closed).
"""
from __future__ import annotations

import dataclasses
import os
import pathlib
import re
import subprocess
import sys
from typing import Any

# -- verdict states ---------------------------------------------------------

PROTECTED = "PROTECTED"
NOT_PROTECTED = "NOT_PROTECTED"
UNKNOWN = "UNKNOWN"  # fail-closed: never read as protected

#: Bound on any single ACL inspection subprocess. A probe that hangs is an
#: ambiguous state, not a pass: it times out and fails closed.
PROBE_TIMEOUT_SECONDS = 20.0

#: icacls permission codes that let a principal MODIFY / overwrite / delete /
#: rename-or-replace (via the parent) / change the ACL / take ownership. Presence
#: of ANY of these for a non-elevated principal means the boundary is not held.
DANGEROUS_RIGHTS: frozenset[str] = frozenset({
    "F",    # full control
    "M",    # modify
    "W",    # write
    "D",    # delete
    "DE",   # delete
    "WDAC",  # write DAC (change permissions)
    "WO",   # write owner (take ownership)
    "WD",   # write data / add file
    "AD",   # append data / add subdirectory
    "DC",   # delete child (rename/replace a file within a directory)
    "WEA",  # write extended attributes
    "WA",   # write attributes
    "GW",   # generic write
    "GA",   # generic all
})

#: Read/execute codes that are ALLOWED for the unelevated process (it may READ).
READ_ONLY_RIGHTS: frozenset[str] = frozenset({
    "R", "RX", "RC", "RD", "REA", "RA", "X", "S", "GR", "GE", "L", "Rc",
})

#: icacls inheritance/scope flags - NOT rights. `IO` (inherit-only) means the ACE
#: does not apply to the object itself and is ignored for effective permissions.
INHERITANCE_FLAGS: frozenset[str] = frozenset({"I", "OI", "CI", "IO", "NP", "N"})

#: Principals whose full control is EXPECTED and only usable when ELEVATED, so it
#: does not weaken the unelevated boundary. Everything else is treated as
#: unelevated-reachable (fail-closed direction).
ELEVATED_PRINCIPALS: frozenset[str] = frozenset({
    "BUILTIN\\ADMINISTRATORS",
    "ADMINISTRATORS",
    "NT AUTHORITY\\SYSTEM",
    "SYSTEM",
    "NT SERVICE\\TRUSTEDINSTALLER",
    "TRUSTEDINSTALLER",
})


@dataclasses.dataclass(frozen=True)
class AceEntry:
    """One parsed access-control entry: a principal and its rights tokens."""

    principal: str
    rights: frozenset[str]
    inherit_only: bool
    raw: str

    @property
    def is_elevated_principal(self) -> bool:
        return self.principal.upper() in ELEVATED_PRINCIPALS

    @property
    def dangerous_rights(self) -> frozenset[str]:
        return self.rights & DANGEROUS_RIGHTS


@dataclasses.dataclass(frozen=True)
class AclVerdict:
    """Fail-closed verdict for a single path (file OR directory)."""

    state: str
    target: str
    kind: str  # "file" | "directory"
    reasons: tuple[str, ...]
    evidence: dict[str, Any] = dataclasses.field(default_factory=dict)

    def is_protected(self) -> bool:
        return self.state == PROTECTED

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "target": self.target,
            "kind": self.kind,
            "protected": self.is_protected(),
            "reasons": list(self.reasons),
            "evidence": self.evidence,
        }


@dataclasses.dataclass(frozen=True)
class ControllerConfigAclVerdict:
    """Combined fail-closed verdict for the config FILE and its PARENT directory.

    `protected` (and PROTECTED state) require BOTH to be protected. If either is
    UNKNOWN the combined state is UNKNOWN unless the other is already
    NOT_PROTECTED (the stronger, more actionable fact). Missing/ambiguous NEVER
    reads as protected.
    """

    state: str
    file: AclVerdict
    parent: AclVerdict

    def is_protected(self) -> bool:
        return self.state == PROTECTED

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "protected": self.is_protected(),
            "file": self.file.to_dict(),
            "parent": self.parent.to_dict(),
        }


# -- parsing (pure; unit-tested over fixtures) ------------------------------

_ACE_RIGHTS_RE = re.compile(r":((?:\([^)]*\))+)\s*$")


def _split_tokens(rights_blob: str) -> list[str]:
    """`(I)(OI)(CI)(F)` -> ['I','OI','CI','F']; a granular group like `(M,DC)` is
    split on commas too, so each rights CODE is matched individually."""
    tokens: list[str] = []
    for group in re.findall(r"\(([^)]*)\)", rights_blob):
        for code in group.split(","):
            code = code.strip()
            if code:
                tokens.append(code)
    return tokens


def parse_icacls(output: str, *, target: str) -> tuple[list[AceEntry], str]:
    """Parse `icacls <target>` output into ACE entries. `(entries, error)`.

    Defensive: a line that does not match the `principal:(tokens)...` shape is
    ignored (the trailing "Successfully processed ..." summary, blank lines). If
    NO ACE line is found the caller treats it as ambiguous and fails closed.
    """
    entries: list[AceEntry] = []
    norm_target = str(target).strip().rstrip("\\/").upper()
    for line in output.splitlines():
        if not line.strip():
            continue
        m = _ACE_RIGHTS_RE.search(line)
        if not m:
            continue
        rights_blob = m.group(1)
        principal_part = line[: m.start()].strip()
        # On the FIRST ACE line icacls prefixes the target path; strip it.
        upper = principal_part.upper()
        if upper.startswith(norm_target):
            principal_part = principal_part[len(norm_target):].strip()
        if not principal_part:
            continue
        tokens = _split_tokens(rights_blob)
        rights = frozenset(t for t in tokens if t and t not in INHERITANCE_FLAGS)
        inherit_only = "IO" in tokens
        entries.append(AceEntry(principal=principal_part, rights=rights,
                                inherit_only=inherit_only, raw=line.strip()))
    if not entries:
        return [], "no ACE entries parsed from icacls output"
    return entries, ""


def evaluate_acl_entries(entries: list[AceEntry], *, target: str,
                         kind: str) -> AclVerdict:
    """Pure verdict over parsed ACE entries (the unit-test surface).

    NOT_PROTECTED if any NON-elevated principal holds a dangerous right on the
    object itself. PROTECTED if none do (an unelevated process may still READ).
    Ambiguity is the caller's UNKNOWN, not this function's job.
    """
    reasons: list[str] = []
    dangerous: list[dict[str, Any]] = []
    for ace in entries:
        if ace.inherit_only:
            continue  # does not apply to the object itself
        bad = ace.dangerous_rights
        if bad and not ace.is_elevated_principal:
            dangerous.append({"principal": ace.principal,
                              "rights": sorted(bad), "raw": ace.raw})
    evidence = {"aces": [{"principal": a.principal, "rights": sorted(a.rights),
                          "inherit_only": a.inherit_only} for a in entries],
                "dangerous": dangerous}
    if dangerous:
        for d in dangerous:
            reasons.append(
                f"unelevated principal {d['principal']!r} holds "
                f"{','.join(d['rights'])} on the {kind}")
        return AclVerdict(NOT_PROTECTED, str(target), kind, tuple(reasons), evidence)
    reasons.append(
        f"no unelevated principal holds a modify/delete/rename/change-ACL right on "
        f"the {kind}; only elevated principals (Administrators/SYSTEM) do")
    return AclVerdict(PROTECTED, str(target), kind, tuple(reasons), evidence)


# -- live inspection + bounded probe ----------------------------------------


def _run_icacls(path: pathlib.Path) -> tuple[str, str]:
    """Run `icacls <path>`; `(stdout, error)`. Any failure is a fail-closed error."""
    try:
        proc = subprocess.run(
            ["icacls", str(path)],
            capture_output=True, text=True, timeout=PROBE_TIMEOUT_SECONDS,
            check=False,
        )
    except FileNotFoundError:
        return "", "icacls not found (not a Windows platform, or PATH stripped)"
    except subprocess.TimeoutExpired:
        return "", "icacls timed out"
    except OSError as exc:  # pragma: no cover - defensive
        return "", f"icacls could not run: {exc}"
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip().splitlines()
        return "", f"icacls exit {proc.returncode}: {detail[0] if detail else 'no detail'}"
    return proc.stdout, ""


def probe_write_open(path: pathlib.Path) -> str:
    """Bounded, NON-DESTRUCTIVE open-for-write attempt: 'writable'|'denied'|error.

    Opens the file O_WRONLY without O_TRUNC and WRITES NOTHING, then closes it, so
    the content and mtime are unchanged whether or not the open succeeds. On a
    correctly-protected file this raises PermissionError ('denied'); on a writable
    file it succeeds ('writable') and nothing is written. Any other error is
    ambiguous and reported as such (the caller fails closed).
    """
    try:
        fd = os.open(str(path), os.O_WRONLY)
    except PermissionError:
        return "denied"
    except FileNotFoundError:
        return "error:missing"
    except OSError as exc:
        return f"error:{exc.__class__.__name__}"
    else:
        os.close(fd)
        return "writable"


def _unknown(target: str, kind: str, reason: str,
             evidence: dict[str, Any] | None = None) -> AclVerdict:
    return AclVerdict(UNKNOWN, target, kind, (reason,), evidence or {})


def evaluate_file(path: str | os.PathLike[str]) -> AclVerdict:
    """Fail-closed verdict for the config FILE: ACL inspection + a bounded
    non-destructive open-for-write corroboration."""
    p = pathlib.Path(path)
    target = str(p)
    if not p.exists():
        return _unknown(target, "file",
                        "the controller config file does not exist; protection of a "
                        "missing file cannot be asserted")
    if not sys.platform.startswith("win"):
        return _unknown(target, "file",
                        "not a Windows platform; the OS-ACL boundary is Windows-specific "
                        "and cannot be asserted here")
    output, err = _run_icacls(p)
    if err:
        return _unknown(target, "file", f"ACL inspection failed: {err}")
    entries, perr = parse_icacls(output, target=target)
    if perr:
        return _unknown(target, "file", f"ACL output ambiguous: {perr}",
                        {"raw": output})
    acl_verdict = evaluate_acl_entries(entries, target=target, kind="file")
    probe = probe_write_open(p)
    ev = dict(acl_verdict.evidence)
    ev["write_open_probe"] = probe
    if probe.startswith("error"):
        return _unknown(target, "file",
                        f"the open-for-write probe was ambiguous ({probe}); failing closed",
                        ev)
    if probe == "writable":
        # An active bypass beats a clean-looking ACL: writable wins (safer).
        return AclVerdict(
            NOT_PROTECTED, target, "file",
            acl_verdict.reasons + (
                "an unelevated open-for-write SUCCEEDED (the file is writable)",),
            ev)
    # probe == "denied": require the ACL to ALSO be clean for PROTECTED.
    if acl_verdict.state != PROTECTED:
        return dataclasses.replace(acl_verdict, evidence=ev)
    return AclVerdict(
        PROTECTED, target, "file",
        acl_verdict.reasons + (
            "an unelevated open-for-write was DENIED, corroborating the ACL",),
        ev)


def evaluate_directory(path: str | os.PathLike[str]) -> AclVerdict:
    """Fail-closed verdict for the PARENT DIRECTORY. Assessed by ACL inspection
    only: a live create/rename/delete probe in the real config directory would
    have to add or remove an entry (a mutation), which the non-destructive bound
    forbids; the governing ADD_FILE / DELETE_CHILD / WRITE / WDAC / WO rights are
    exactly what the OS enforces rename/replace/re-create from."""
    p = pathlib.Path(path)
    target = str(p)
    if not p.exists():
        return _unknown(target, "directory",
                        "the parent directory does not exist")
    if not sys.platform.startswith("win"):
        return _unknown(target, "directory",
                        "not a Windows platform; the OS-ACL boundary is Windows-specific")
    output, err = _run_icacls(p)
    if err:
        return _unknown(target, "directory", f"ACL inspection failed: {err}")
    entries, perr = parse_icacls(output, target=target)
    if perr:
        return _unknown(target, "directory", f"ACL output ambiguous: {perr}",
                        {"raw": output})
    return evaluate_acl_entries(entries, target=target, kind="directory")


def _combine(file_v: AclVerdict, parent_v: AclVerdict) -> str:
    if file_v.state == PROTECTED and parent_v.state == PROTECTED:
        return PROTECTED
    if NOT_PROTECTED in (file_v.state, parent_v.state):
        return NOT_PROTECTED
    return UNKNOWN


def evaluate_controller_config_acl(
        config_path: str | os.PathLike[str]) -> ControllerConfigAclVerdict:
    """The single entry point: fail-closed verdict for the config FILE and its
    PARENT directory. PROTECTED only when BOTH are protected."""
    p = pathlib.Path(config_path)
    file_v = evaluate_file(p)
    parent_v = evaluate_directory(p.parent)
    return ControllerConfigAclVerdict(_combine(file_v, parent_v), file_v, parent_v)
