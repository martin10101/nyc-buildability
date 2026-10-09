"""Deterministic Bootstrap Gate 0 evaluation for a new or successor session
(D-024 Phase D, M0-T092; R125–R128).

R125: before any repository write, the session's PRIMARY current working
directory must BE the intended repository/worktree root — access through an
added working directory, an absolute path, or a later-created worktree is not
equivalent. R126: the MCP servers actually attached to the live session must
be proven empty or exactly an approved allowlist; a policy file's existence is
not proof. R127: a failed or UNKNOWN check permits bounded read-only diagnosis
only, and the diagnosis must name the actual launch directory, the intended
root, and any dirty paths. R128: a fresh session must independently pass this
gate before adopting uncommitted work from a failed-start session — and never
rewrites history or discards that work merely to obtain a clean status.

What already existed (R018 prove-first): Gate 0 was enforced PROCEDURALLY —
the campaign record's standing restriction line, the handoff-profile text, and
each orchestrator session's manual check. ``native_runtime.DispatchSpec``
passes ``--strict-mcp-config`` to CHILD sessions and ``capability_probe``
classifies the flag's support, but no deterministic, testable evaluation of
the gate itself existed for the SUCCESSOR-BOOT path (the section-16.3 matrix
names "Gate-0 recovery cases" — R109). This module is that evaluation: pure
input -> verdict, no discovery, no I/O.

Path identity reuses ``durable_state.canonical_checkout_path`` (resolve +
normcase) so "the same directory" means the same thing here as it does for the
runtime-state key.

Supervisor-freeze qualifying evidence: D-024-R102.
"""
from __future__ import annotations

import dataclasses
from typing import Any

from .durable_state import canonical_checkout_path

READ_ONLY_POSTURE = ("read-only diagnosis only; produce a terminal-visible "
                     "handoff; a fresh session is required (R127)")


class Gate0Error(Exception):
    """A write was attempted behind a failed or unknown Gate 0. Fails closed."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclasses.dataclass(frozen=True)
class Gate0Inputs:
    """The facts the gate is evaluated against. The CALLER establishes them
    (the process's own cwd, the live ``/mcp`` enumeration); this module never
    discovers anything, so an un-established fact must be passed as unknown —
    which fails, by design (R127)."""

    primary_cwd: str
    intended_root: str
    #: The MCP servers ACTUALLY attached to the live session. Meaningful only
    #: when ``mcp_enumeration_known`` is True.
    attached_mcp_servers: tuple[str, ...] = ()
    #: False when the live enumeration was not performed or did not conclude.
    #: Unknown is a failure, never a pass (R127).
    mcp_enumeration_known: bool = False
    approved_mcp_allowlist: tuple[str, ...] = ()
    #: True when the intended root is reachable ONLY through /add-dir or an
    #: additional working directory — R125 says that never satisfies the gate.
    reached_via_added_dir: bool = False
    dirty_paths: tuple[str, ...] = ()


@dataclasses.dataclass(frozen=True)
class Gate0Verdict:
    """The gate's answer plus the R127 diagnosis payload."""

    passed: bool
    failures: tuple[str, ...]
    diagnosis: dict[str, Any]


def evaluate_gate0(inputs: Gate0Inputs) -> Gate0Verdict:
    """Evaluate Bootstrap Gate 0. Every check that cannot PASS fails closed."""
    failures: list[str] = []

    if not inputs.primary_cwd or not inputs.intended_root:
        failures.append(
            "launch-root unknown: the primary cwd or the intended worktree "
            "root was not established; an unknown check is a failed check "
            "(R127)")
    else:
        try:
            same = (canonical_checkout_path(inputs.primary_cwd)
                    == canonical_checkout_path(inputs.intended_root))
        except OSError:
            same = False
        if not same:
            failures.append(
                f"the process's primary cwd ({inputs.primary_cwd}) is not the "
                f"intended worktree root ({inputs.intended_root}); reaching "
                f"the repository through an added directory or an absolute "
                f"path is not equivalent (R125)")
    if inputs.reached_via_added_dir:
        failures.append(
            "the intended root is reachable only through /add-dir / an "
            "additional working directory; R125 requires the LAUNCH root "
            "itself")

    if not inputs.mcp_enumeration_known:
        failures.append(
            "the live MCP attachment set was not enumerated or did not "
            "conclude; the presence of a policy file is not proof, and an "
            "unknown MCP state never passes (R126/R127)")
    else:
        allowlist = set(inputs.approved_mcp_allowlist)
        unapproved = tuple(s for s in inputs.attached_mcp_servers
                           if s not in allowlist)
        if unapproved:
            failures.append(
                f"MCP servers attached outside the approved allowlist: "
                f"{sorted(unapproved)}; the session must prove empty or "
                f"exactly-allowlisted attachments (R126)")

    diagnosis = {
        "actual_launch_directory": inputs.primary_cwd,
        "intended_worktree_root": inputs.intended_root,
        "dirty_uncommitted_paths": list(inputs.dirty_paths),
        "attached_mcp_servers": (list(inputs.attached_mcp_servers)
                                 if inputs.mcp_enumeration_known
                                 else "UNKNOWN (enumeration not performed)"),
        "approved_mcp_allowlist": list(inputs.approved_mcp_allowlist),
        "failures": list(failures),
        "posture_on_failure": READ_ONLY_POSTURE,
    }
    return Gate0Verdict(passed=not failures, failures=tuple(failures),
                        diagnosis=diagnosis)


def may_write(verdict: Gate0Verdict) -> bool:
    """Repository writes, task claims, commits, and pushes need a PASS."""
    return verdict.passed


def assert_may_write(verdict: Gate0Verdict) -> None:
    if verdict.passed:
        return
    raise Gate0Error(
        "gate0_failed",
        "Bootstrap Gate 0 did not pass: " + "; ".join(verdict.failures)
        + f". {READ_ONLY_POSTURE}")


@dataclasses.dataclass(frozen=True)
class AdoptionDecision:
    """R128: whether a fresh session may adopt a failed start's uncommitted
    work, and the one legal way to do it."""

    permitted: bool
    reason: str
    instruction: str = ""


def adoption_of_uncommitted(fresh_verdict: Gate0Verdict,
                            *, dirty_paths: tuple[str, ...]) -> AdoptionDecision:
    """A FRESH session adopts a failed-start session's uncommitted work only
    after independently passing Gate 0 itself; the work is adopted in place —
    history is never rewritten and the work is never discarded merely to
    obtain a clean status (R128)."""
    if not fresh_verdict.passed:
        return AdoptionDecision(
            False,
            "the fresh session has not independently passed Bootstrap Gate 0; "
            "adoption of uncommitted work is refused until it does (R128)")
    return AdoptionDecision(
        True,
        "the fresh session independently passed Bootstrap Gate 0",
        instruction=(
            f"adopt the uncommitted paths {sorted(dirty_paths)} IN PLACE: "
            f"review, then commit or explicitly quarantine them; never "
            f"rewrite history and never discard them merely to obtain a "
            f"clean status (R128)"))
