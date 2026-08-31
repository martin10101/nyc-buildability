#!/usr/bin/env python3
"""The single pre-provider-contact enforcement seam for every worker launch/resume.

D-024 Amendment 19 (rows R331-R344). Qualifying evidence: the reproduced cycle-2
live defect (`project-control/reports/M0-T107-cycle2-live-journey.md`), whose
durable journal shows BOTH failures at once:

* ``rotation_pending = true`` / ``rotation_pending_reason = "context_threshold"``
  set when a unit crossed the 400k ceiling at 604,772 tokens, then left
  UNCONSUMED across the next START, which dispatched a unit that grew to 640,224
  tokens and died ``returncode 1`` with no structured checkpoint - the ceiling
  was never evaluated before provider contact; and
* every record of the resumed worker's transcript stamped
  ``cwd = C:\\Users\\MLFLL\\Downloads\\nyc-zoning\\ctl24`` (the orchestrator's
  PRIMARY control checkout) instead of the isolated worktree ``wt-m0t107`` - the
  launch cwd was never bound to the packet's worktree.

This module is the ONE seam every path capable of launching or resuming a worker
passes through BEFORE the provider is contacted (ordinary start, recovery start,
controller restart, rotation, turnover, checkpoint continuation). It is modelled
on ``restart_channel`` (M0-T121): a focused, fail-closed enforcement module with
typed refusals and a deterministic, removal-sensitive reachability test
(``tools/test_agent_supervisor_launch_seam.py``).

It owns two guards and NOTHING else - no I/O, no journal writes, no provider
contact, no policy state:

1. **Context-rotation ceiling (R332/R333/R334).** A session AT OR ABOVE the 400k
   ceiling is NEVER resumed: the seam reports ``ROTATE`` (rotate to a fresh
   session at the safe seam) or the caller fails closed. MISSING or unknown token
   telemetry on a to-be-continued session is fail-closed (``REFUSE``), NEVER
   assumed below the ceiling. Exactly-at-400k is at-or-above.
2. **cwd binding (R335/R336).** A launch/resume/rotation whose cwd is not the
   packet's isolated worktree fails closed BEFORE provider contact - a
   primary-checkout cwd, an unexpected cwd, or an unbound (empty) worktree. The
   comparison is Windows-path aware: drive-letter case and slash direction do not
   let a primary-checkout launch masquerade as the worktree.

The ceiling constant is imported from ``rotation.RotationThresholds`` so this
module and the rotation policy can never disagree; it is owner-policy, not a
capacity claim (S11.1).
"""
from __future__ import annotations

import dataclasses
import os
from typing import Any

from .rotation import RotationThresholds

#: The 400k context-rotation ceiling, taken from the single owner-policy source
#: (`RotationThresholds.context_rotation_threshold`) so it can never drift from
#: the value the mid-unit observer and the seam rotation already use. NOT a
#: capacity claim; an owner-editable policy number (S11.1 / D-004-R743).
CONTEXT_ROTATION_CEILING: int = RotationThresholds().context_rotation_threshold

# -- actions ---------------------------------------------------------------

#: The launch may proceed to provider contact: both guards passed.
PROCEED = "proceed"
#: The session is at/above the ceiling: it must NOT be resumed. The caller
#: rotates to a fresh session at the safe seam (never contacts the provider on
#: the over-ceiling session).
ROTATE = "rotate"
#: A fail-closed refusal: no provider contact, a typed reason, nothing rotates.
REFUSE = "refuse"

# -- refusal / action codes ------------------------------------------------

#: cwd guard (R335/R336).
CWD_UNBOUND = "cwd_unbound"                # no expected worktree, or empty cwd
CWD_PRIMARY_CHECKOUT = "cwd_primary_checkout"  # cwd is the primary control checkout
CWD_MISMATCH = "cwd_mismatch"              # cwd is some other unexpected directory

#: repo/evidence-binding guard (M0-T125 defect D2): the evidence collector and
#: Codex reviewer bind to `repo`. When the packet declares an isolated worktree
#: but `repo` resolves to the PRIMARY control checkout, the git facts in the
#: evidence packet and the reviewer's `-C <repo>` tree are the orchestrator's
#: control checkout, not the worker's tree — the evidence/review half of the
#: cycle-2 leakage class.
REPO_PRIMARY_CHECKOUT = "repo_primary_checkout"

#: ceiling guard (R332/R333/R334).
CEILING_TELEMETRY_MISSING = "ceiling_telemetry_missing"  # unknown usage on a resume
OVER_CEILING_RESUME_FORBIDDEN = "over_ceiling_resume_forbidden"  # tokens >= ceiling

#: Every code this seam can emit, for the reachability/coverage test to key on.
REFUSAL_CODES: tuple[str, ...] = (
    CWD_UNBOUND, CWD_PRIMARY_CHECKOUT, CWD_MISMATCH, REPO_PRIMARY_CHECKOUT,
    CEILING_TELEMETRY_MISSING, OVER_CEILING_RESUME_FORBIDDEN,
)


class LaunchSeamError(Exception):
    """A launch was refused before provider contact. Always fails closed.

    Carries the stable refusal ``code`` and the ``action`` the seam decided
    (``REFUSE`` for a hard refusal, ``ROTATE`` for an over-ceiling session the
    caller must rotate rather than resume), so a caller that raises this instead
    of branching still preserves the distinction.
    """

    def __init__(self, code: str, message: str, action: str = REFUSE) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.action = action


@dataclasses.dataclass(frozen=True)
class LaunchDecision:
    """The seam's verdict about one launch/resume, and the evidence for it."""

    action: str
    code: str = ""
    message: str = ""

    @property
    def ok(self) -> bool:
        """True only when the launch may proceed to provider contact."""
        return self.action == PROCEED

    @property
    def rotate(self) -> bool:
        """True when the session is over-ceiling and must be rotated, not resumed."""
        return self.action == ROTATE

    def as_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class WorkerLaunchContext:
    """Everything the seam needs to decide, gathered by the calling path.

    Nothing here is fetched by the seam: the caller (the runner before Popen, the
    loop before a dispatch, the CLI before building the runner) collects the facts
    and hands them over, so the seam stays a pure decision with no I/O.
    """

    #: The directory the worker process will be launched in.
    cwd: str = ""
    #: The packet's isolated worktree the launch MUST be bound to. Empty means the
    #: caller did not bind a worktree at this layer; the cwd guard is then deferred
    #: to the layer that does (the CLI/loop seam), and only the ceiling is checked
    #: here. An empty worktree in a layer that IS responsible for binding is itself
    #: unbound and fails closed via `assert_worktree_isolated`.
    expected_worktree: str = ""
    #: The orchestrator's primary control checkout, when known, so a cwd that lands
    #: on it is named specifically (`cwd_primary_checkout`) rather than as a generic
    #: mismatch. Optional; a generic mismatch is still fail-closed.
    primary_checkout: str = ""
    #: True when this launch would CONTINUE/RESUME a recorded session (a `--resume`,
    #: or a start that carries a recorded provider session forward). A fresh session
    #: cannot be an over-ceiling resume, so the ceiling guard only applies when this
    #: is True.
    resuming: bool = False
    #: The cumulative context tokens the session-to-be-continued last reported.
    #: `None` = unknown telemetry (fail closed on a resume).
    session_context_tokens: int | None = None
    #: True only when the token telemetry above was actually observed.
    session_usage_known: bool = False
    #: The ceiling to apply; defaults to the owner-policy 400k.
    ceiling: int = CONTEXT_ROTATION_CEILING


# -- path normalization (Windows-aware) ------------------------------------


def normalize_path(path: str) -> str:
    """A comparison-safe path form: drive-letter case and slash direction folded.

    `os.path.normcase` lowercases the drive letter and flips `/` to `\\` on
    Windows; `os.path.normpath` collapses `.`/`..` and duplicate separators. Empty
    stays empty. No filesystem access, so a worktree that does not exist on the
    reviewer's box still compares correctly.
    """
    if not path:
        return ""
    return os.path.normcase(os.path.normpath(str(path)))


def same_path(a: str, b: str) -> bool:
    """True when two non-empty paths denote the same directory (Windows-aware)."""
    na, nb = normalize_path(a), normalize_path(b)
    return bool(na) and bool(nb) and na == nb


# -- guards ----------------------------------------------------------------


def worktree_matches_packet(cwd_worktree: str, packet_worktree: str) -> bool:
    """True when the bound worktree is the one the packet declares.

    The packet's ``worktree`` may be an ABSOLUTE path (matched exactly, Windows
    path forms folded) or a RELATIVE isolated-worktree NAME such as ``wt-m0t123``
    (matched against the basename of the bound worktree). Either form makes the
    reproduced defect - packet declares ``wt-m0t107`` while the launch is bound to
    ``...\\ctl24`` - a clean mismatch.
    """
    if not cwd_worktree or not packet_worktree:
        return False
    if os.path.isabs(packet_worktree):
        return same_path(cwd_worktree, packet_worktree)
    base = os.path.basename(os.path.normpath(str(cwd_worktree)))
    return normalize_path(base) == normalize_path(packet_worktree)


def evaluate_packet_worktree_binding(
    cwd_worktree: str, packet_worktree: str, primary_checkout: str = "",
) -> LaunchDecision | None:
    """The CLI-layer gate: the bound worktree must be the packet's isolated worktree.

    The reproduced dimension-(b) root cause is that `cli._run_loop` defaulted the
    worktree to the primary checkout when `--worktree` was absent, so the launch
    cwd landed on the orchestrator's control checkout `...\\ctl24` even though the
    packet declared the isolated worktree `wt-m0t107`. This refuses, BEFORE the
    runner is built, whenever the bound worktree is not the one the packet declares
    - naming the primary-checkout case specifically. A packet that declares no
    worktree (single-checkout runs and older harnesses) is not constrained here;
    the runner's own `cwd == expected_worktree` guard still holds.
    """
    if not packet_worktree:
        return None
    if worktree_matches_packet(cwd_worktree, packet_worktree):
        return None
    if primary_checkout and same_path(cwd_worktree, primary_checkout):
        return LaunchDecision(
            REFUSE, CWD_PRIMARY_CHECKOUT,
            f"the launch would be bound to the orchestrator's PRIMARY control checkout "
            f"{cwd_worktree!r}, but the task packet declares the isolated worktree "
            f"{packet_worktree!r}; a worker never runs in the control checkout "
            f"(D-024-R336, the reproduced cycle-2 defect). Pass --worktree pointing at "
            f"the packet's isolated worktree.")
    return LaunchDecision(
        REFUSE, CWD_MISMATCH,
        f"the launch would be bound to {cwd_worktree!r}, which is not the isolated "
        f"worktree {packet_worktree!r} the task packet declares; an unexpected worker "
        f"worktree fails closed before provider contact (D-024-R336).")


def evaluate_repo_binding(
    repo: str, packet_worktree: str, primary_checkout: str = "",
) -> LaunchDecision | None:
    """Evidence/review repo binding (M0-T125 defect D2). Refuse or `None`.

    When the packet declares an isolated worktree, the `repo` the evidence
    collector and Codex reviewer bind to must NOT be the PRIMARY control
    checkout — otherwise the evidence git facts and the reviewer's working tree
    describe the orchestrator's control checkout rather than the worker's tree.
    A packet that declares no worktree (single-checkout runs) is unconstrained
    here, the same stance as `evaluate_packet_worktree_binding`. A repo that IS
    the declared worktree (the degenerate single-checkout shape) is allowed.
    """
    if not packet_worktree:
        return None
    if not primary_checkout or not same_path(repo, primary_checkout):
        return None
    if same_path(repo, packet_worktree):
        return None
    return LaunchDecision(
        REFUSE, REPO_PRIMARY_CHECKOUT,
        f"evidence and Codex review would bind to the PRIMARY control checkout "
        f"{repo!r}, but the task packet declares the isolated worktree "
        f"{packet_worktree!r}; the evidence git facts and the reviewer's -C tree "
        f"would describe the control checkout, not the worker's tree "
        f"(D-024-R336, defect D2). Pass --repo pointing at the worker's "
        f"repository, not the control checkout.")


def enforce_launch_bindings(
    cwd_worktree: str, repo: str, packet_worktree: str, primary_checkout: str = "",
) -> LaunchDecision | None:
    """The CLI pre-runner bindings: worktree cwd (R336) AND evidence repo (D2).

    Returns the FIRST refusal (worktree binding, then repo binding), or `None`
    when both bind correctly. One entry point so `cli._run_loop` enforces both
    seam checks with a single call before the runner is built.
    """
    worktree = evaluate_packet_worktree_binding(
        cwd_worktree, packet_worktree, primary_checkout)
    if worktree is not None:
        return worktree
    return evaluate_repo_binding(repo, packet_worktree, primary_checkout)


def evaluate_cwd(
    cwd: str, expected_worktree: str, primary_checkout: str = "",
) -> LaunchDecision | None:
    """cwd binding (R335/R336). Returns a refusal or `None` when bound correctly.

    Fails closed on: an unbound expectation or empty cwd, a cwd that is the primary
    checkout (named specifically), and any other cwd that is not the expected
    worktree. Windows path forms (drive case, slashes) are folded so a
    primary-checkout launch can never masquerade as the worktree.
    """
    if not expected_worktree:
        return LaunchDecision(
            REFUSE, CWD_UNBOUND,
            "the launch cwd cannot be validated: no expected worktree was supplied. "
            "An unbound worker cwd fails closed rather than being assumed correct.")
    if not cwd:
        return LaunchDecision(
            REFUSE, CWD_UNBOUND,
            f"the launch cwd is empty but must be the isolated worktree "
            f"{expected_worktree!r}; an empty cwd fails closed (D-024-R336).")
    if same_path(cwd, expected_worktree):
        return None
    if primary_checkout and same_path(cwd, primary_checkout):
        return LaunchDecision(
            REFUSE, CWD_PRIMARY_CHECKOUT,
            f"the launch cwd {cwd!r} is the orchestrator's PRIMARY control checkout, "
            f"not the packet's isolated worktree {expected_worktree!r}; a worker never "
            f"runs in the control checkout (D-024-R336, the reproduced cycle-2 defect).")
    return LaunchDecision(
        REFUSE, CWD_MISMATCH,
        f"the launch cwd {cwd!r} is not the packet's isolated worktree "
        f"{expected_worktree!r}; an unexpected worker cwd fails closed before "
        f"provider contact (D-024-R336).")


def evaluate_ceiling(
    resuming: bool,
    session_context_tokens: int | None,
    session_usage_known: bool,
    ceiling: int = CONTEXT_ROTATION_CEILING,
) -> LaunchDecision | None:
    """Context-rotation ceiling (R332/R333/R334). Returns a decision or `None`.

    A fresh launch (`resuming=False`) has no session to be over-ceiling, so the
    ceiling never applies. When continuing/resuming a recorded session:

    * unknown telemetry (`None`, or `usage_known` False) is fail-closed
      (`REFUSE`/`ceiling_telemetry_missing`) - never assumed below the ceiling;
    * tokens AT OR ABOVE the ceiling means the session is NEVER resumed
      (`ROTATE`/`over_ceiling_resume_forbidden`): the caller rotates to a fresh
      session at the safe seam;
    * tokens strictly below the ceiling is `None` (resume permitted).
    """
    if not resuming:
        return None
    if session_context_tokens is None or not session_usage_known:
        return LaunchDecision(
            REFUSE, CEILING_TELEMETRY_MISSING,
            "the session to be continued reports no context-token telemetry, so the "
            "400k rotation ceiling cannot be evaluated; an unknown usage on a resume "
            "fails closed and is NEVER assumed below the ceiling (D-024-R333).")
    tokens = int(session_context_tokens)
    if tokens >= int(ceiling):
        return LaunchDecision(
            ROTATE, OVER_CEILING_RESUME_FORBIDDEN,
            f"the session to be continued last reported {tokens} context tokens, at or "
            f"above the {int(ceiling)} rotation ceiling; it is NEVER resumed - it rotates "
            f"to a fresh session at the safe seam (D-024-R333/R334).")
    return None


def enforce_launch(ctx: WorkerLaunchContext) -> LaunchDecision:
    """The single decision every launch/resume path routes through.

    cwd binding first (only when this layer bound a worktree), then the ceiling.
    Returns `PROCEED` only when both guards pass. Pure: it reads `ctx` and returns
    a decision; it never touches the journal, the runner, or the provider.
    """
    if ctx.expected_worktree:
        cwd_decision = evaluate_cwd(ctx.cwd, ctx.expected_worktree, ctx.primary_checkout)
        if cwd_decision is not None:
            return cwd_decision
    ceiling_decision = evaluate_ceiling(
        ctx.resuming, ctx.session_context_tokens, ctx.session_usage_known, ctx.ceiling)
    if ceiling_decision is not None:
        return ceiling_decision
    return LaunchDecision(
        PROCEED, "",
        "both launch guards passed: the cwd is the packet's isolated worktree and no "
        "over-ceiling session is being resumed")


def enforce_or_raise(ctx: WorkerLaunchContext) -> LaunchDecision:
    """Raise `LaunchSeamError` unless the launch may proceed to provider contact.

    Used at the ironclad runner chokepoint (`ClaudeRunner.run_unit`, immediately
    before `subprocess.Popen`), where an over-ceiling resume and a cwd mismatch
    are BOTH refusals: a runner cannot rotate, so a `--resume` of an over-ceiling
    session must never reach the process. Callers that CAN rotate (the loop seam)
    use `enforce_launch` and branch on `ROTATE`.
    """
    decision = enforce_launch(ctx)
    if decision.ok:
        return decision
    raise LaunchSeamError(decision.code, decision.message, decision.action)
