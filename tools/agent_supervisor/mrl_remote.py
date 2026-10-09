#!/usr/bin/env python3
"""MRL remote-freshness observation (M0-T134 / D-024 Amendment 39 R505; C11).

A read-only ``git ls-remote`` observation of ONE base ref's current SHA plus the
moment it was observed, so the controller binds a FRESH base SHA into the
CodexDecision instead of trusting a possibly-stale local tracking ref. Option-B
neutral: the base ref is always a parameter - never a hard-coded ``origin/main``.

The git command is injectable (``run=``) so tests never touch the network and no
live GitHub call is made in Tranche A. The default runner does a real
``ls-remote`` but is never invoked in this tranche.
"""
from __future__ import annotations

import dataclasses
import datetime
import re
import subprocess
from typing import Callable, Sequence

from .mrl_worker_result import ContractError

_SHA40 = re.compile(r"^[0-9a-f]{40}$")

RunGit = Callable[[Sequence[str]], str]


@dataclasses.dataclass(frozen=True)
class RemoteObservation:
    """A fresh, read-only observation of a base ref on the remote."""

    normalized_remote_url: str
    base_ref: str
    base_sha: str
    observed_at_utc: str


def normalize_remote_url(url: str) -> str:
    """Canonicalize a remote URL for binding (strip trailing slash and .git)."""
    u = url.strip()
    if u.endswith("/"):
        u = u[:-1]
    if u.endswith(".git"):
        u = u[:-4]
    return u


def _default_run(argv: Sequence[str]) -> str:  # pragma: no cover - never called in Tranche A
    """Real ls-remote. Never invoked by tests or in Tranche A (no live GitHub call)."""
    return subprocess.run(list(argv), capture_output=True, text=True, check=True).stdout


def observe_remote(
    remote_url: str,
    base_ref: str,
    *,
    run: RunGit | None = None,
    now: Callable[[], datetime.datetime] | None = None,
) -> RemoteObservation:
    """Observe ``base_ref``'s current SHA on ``remote_url`` via read-only ls-remote.

    Fail-closed: an empty url/ref, or output that does not yield a 40-hex sha for
    the ref, raises rather than returning a guessed or stale value.
    """
    if not isinstance(remote_url, str) or not remote_url.strip():
        raise ContractError("contract_violation", "remote_url is required")
    if not isinstance(base_ref, str) or not base_ref.strip():
        raise ContractError("contract_violation",
                            "base_ref is required (Option-B neutral; never a hard-coded origin/main)")
    run = run or _default_run
    now = now or (lambda: datetime.datetime.now(datetime.timezone.utc))
    output = run(["git", "ls-remote", remote_url, base_ref])
    sha = ""
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) >= 2:
            sha = parts[0].strip().lower()
            break
    if not _SHA40.match(sha):
        raise ContractError(
            "contract_violation",
            f"ls-remote for {base_ref!r} on {remote_url!r} did not yield a 40-hex "
            f"sha (got {sha!r}); the observation fails closed rather than binding a "
            f"stale or guessed base")
    return RemoteObservation(normalize_remote_url(remote_url), base_ref, sha, now().isoformat())
