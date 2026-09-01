"""Controller-authoritative git-state checkpoint envelope (D-024 Amendment 37 / M0-T133).

The four checkpoint-envelope fields ``branch``, ``worktree``, ``starting_sha`` and
``current_sha`` are CONTROLLER-AUTHORITATIVE: the controller already knows the dispatch
context (expected branch, expected worktree, the pre-dispatch starting SHA) and can
measure the live git state deterministically, so it fills them into the worker's
checkpoint *before* final validation and requires an EXACT NORMALIZED MATCH for any the
worker supplied. Any anomaly - a supplied value that mismatches, an unreadable
repository, an unexpected branch, the wrong worktree, or an ambiguous SHA - FAILS CLOSED
(the checkpoint is rejected, never enriched-over). Enrichment touches ONLY these four
fields; it never reads or writes status, summary, claims, evidence, review, advancement,
or any other field, so it cannot manufacture a false completion.

This module is pure and injectable: the git measurement is a ``GitRunner`` callable, so
no test contacts a real repository unless it chooses to.
"""

from __future__ import annotations

import dataclasses
import os
import re
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # Import the GitRunner TYPE only for checkers: a runtime import would form the
    # cycle recovery_probes -> preflight -> claude_runner -> checkpoint_envelope. The
    # runner is duck-typed at runtime (called as `git(argv, cwd)`; result.ok/.text).
    from .recovery_probes import GitRunner

#: The four controller-authoritative envelope fields, in a stable order.
ENVELOPE_FIELDS: tuple[str, ...] = ("branch", "worktree", "starting_sha", "current_sha")

#: A full git object name for this repository (sha1). A shorter or non-hex value is
#: AMBIGUOUS and fails closed rather than being guessed at.
_FULL_SHA_RE = re.compile(r"\A[0-9a-f]{40}\Z")


class EnvelopeError(ValueError):
    """A controller-authoritative envelope could not be established or a worker-supplied
    field did not match. Carries a stable ``code`` so the caller can fail closed with an
    honest reason. NEVER raised to silently overwrite worker data."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def normalize_sha(value: Any) -> str:
    """A normalized full 40-hex git SHA (lower-cased), or raise ``EnvelopeError``.

    A short, empty, non-hex, or otherwise ambiguous value is a fail-closed condition:
    the controller never resolves an ambiguous object name on the worker's behalf.
    """
    text = "" if value is None else str(value).strip().lower()
    if not _FULL_SHA_RE.match(text):
        raise EnvelopeError("ambiguous_sha",
                            f"{value!r} is not an unambiguous full 40-hex git SHA")
    return text


def normalize_worktree(value: Any) -> str:
    """A canonical form of a worktree path for equivalence comparison.

    Handles the Windows realities the checkpoint must survive: mixed forward/back
    slashes, a trailing slash, duplicate separators, and case-insensitivity. Two paths
    that denote the same location normalize equal; genuinely different paths do not.
    Purely lexical (no filesystem access), so it is deterministic for a fake path.
    """
    text = "" if value is None else str(value).strip()
    if not text:
        raise EnvelopeError("empty_worktree", "a worktree path may not be empty")
    unified = text.replace("\\", "/")
    # Collapse duplicate separators without touching a leading UNC-style prefix.
    collapsed = re.sub(r"/{2,}", "/", unified)
    trimmed = collapsed.rstrip("/") or "/"
    # Windows path comparison is case-insensitive; os.path.normcase lower-cases on
    # Windows and is a no-op on POSIX, so the same fixture compares equal on both.
    return os.path.normcase(trimmed)


def normalize_branch(value: Any) -> str:
    """A stripped branch name, or raise on an empty / detached-HEAD sentinel.

    A detached HEAD reports ``HEAD`` for ``rev-parse --abbrev-ref``; an unattended
    commissioning unit runs on a named task branch, so ``HEAD`` (or empty) is an
    unexpected/ambiguous branch state and fails closed.
    """
    text = "" if value is None else str(value).strip()
    if not text or text == "HEAD":
        raise EnvelopeError("ambiguous_branch",
                            f"{value!r} is not an unambiguous named branch")
    return text


@dataclasses.dataclass(frozen=True)
class MeasuredGitState:
    """One read-only measurement of a worktree's live git identity."""

    branch: str
    toplevel: str
    head_sha: str


def measure_git_state(git: GitRunner, worktree: str) -> MeasuredGitState:
    """Measure the live branch, worktree top-level, and HEAD sha with read-only git.

    Every command is a fixed read-only ``rev-parse``; any failure to execute or a
    non-zero exit is an unreadable repository state and fails closed.
    """
    def _one(argv: tuple[str, ...], code: str) -> str:
        result = git(argv, worktree)
        if not result.ok:
            raise EnvelopeError(
                code, f"read-only `git {' '.join(argv)}` did not succeed in {worktree!r} "
                      f"(ran={getattr(result, 'ran', '?')}, rc={getattr(result, 'returncode', '?')})")
        return result.text

    branch = normalize_branch(_one(("rev-parse", "--abbrev-ref", "HEAD"), "git_unreadable"))
    toplevel = _one(("rev-parse", "--show-toplevel"), "git_unreadable")
    head_sha = normalize_sha(_one(("rev-parse", "HEAD"), "git_unreadable"))
    return MeasuredGitState(branch=branch, toplevel=toplevel, head_sha=head_sha)


@dataclasses.dataclass(frozen=True)
class CheckpointEnvelope:
    """The controller's dispatch context for one unit, resolvable to the four
    authoritative git-state values via a fresh read-only measurement.

    ``expected_branch``/``expected_worktree`` come from the dispatch authority and
    ``starting_sha`` was measured by the controller BEFORE the worker ran. ``resolve``
    measures the live state, cross-checks it against the expectations (fail-closed on any
    mismatch), and returns the canonical values to enrich the checkpoint with.
    """

    expected_branch: str
    expected_worktree: str
    starting_sha: str
    git: GitRunner
    worktree: str = ""

    def resolve(self) -> dict[str, str]:
        target = self.worktree or self.expected_worktree
        observed = measure_git_state(self.git, target)
        if normalize_branch(observed.branch) != normalize_branch(self.expected_branch):
            raise EnvelopeError(
                "unexpected_branch",
                f"the worktree is on branch {observed.branch!r} but this unit was "
                f"dispatched for {self.expected_branch!r}")
        if normalize_worktree(observed.toplevel) != normalize_worktree(self.expected_worktree):
            raise EnvelopeError(
                "wrong_worktree",
                f"the git top-level {observed.toplevel!r} is not the dispatched worktree "
                f"{self.expected_worktree!r}")
        return {
            "branch": self.expected_branch.strip(),
            "worktree": self.expected_worktree.strip(),
            "starting_sha": normalize_sha(self.starting_sha),
            "current_sha": observed.head_sha,
        }


def _matches(field: str, worker_value: Any, authoritative: str) -> bool:
    """Exact NORMALIZED equality for one supplied envelope field (fail-closed on any
    difference). SHA fields compare as full 40-hex; the worktree compares path-canonically;
    the branch compares by stripped name."""
    if field in ("starting_sha", "current_sha"):
        try:
            return normalize_sha(worker_value) == normalize_sha(authoritative)
        except EnvelopeError:
            return False
    if field == "worktree":
        try:
            return normalize_worktree(worker_value) == normalize_worktree(authoritative)
        except EnvelopeError:
            return False
    # branch
    return str(worker_value).strip() == str(authoritative).strip()


def _is_absent(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def enrich_checkpoint(chosen: Mapping[str, Any],
                      authoritative: Mapping[str, str]) -> tuple[dict[str, Any], list[str]]:
    """Return an ENRICHED COPY of the worker checkpoint plus the list of fields the
    controller filled. The input mapping is never mutated (the caller keeps the
    worker's original bytes as evidence).

    For each of the four envelope fields: if the worker omitted it (absent/blank) the
    controller fills the authoritative value and records it as added; if the worker
    supplied it, an exact normalized match is required and a mismatch raises
    ``EnvelopeError`` (fail closed - the worker value is NEVER silently overwritten).
    Every non-envelope field is copied through untouched.
    """
    enriched = dict(chosen)
    added: list[str] = []
    for field in ENVELOPE_FIELDS:
        auth_value = authoritative[field]
        worker_value = chosen.get(field, None)
        if _is_absent(worker_value):
            enriched[field] = auth_value
            added.append(field)
            continue
        if not _matches(field, worker_value, auth_value):
            raise EnvelopeError(
                "checkpoint_field_mismatch",
                f"worker-supplied {field}={worker_value!r} does not match the "
                f"controller-authoritative value {auth_value!r}; refusing to overwrite")
        # Supplied and matching: canonicalize to the authoritative form for a stable record.
        enriched[field] = auth_value
    return enriched, added
