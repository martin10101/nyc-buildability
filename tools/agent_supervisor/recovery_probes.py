#!/usr/bin/env python3
"""Live pre-dispatch revalidation probes (D-007 S11.5 step 5; D-023 item 1).

Qualifying evidence (AD-093 Section 0A.10): a reproduced defect. `cmd_start`
answered six of S11.5's twelve revalidation questions with the SAME synthetic
boolean - "did the operator name every CLI input?" - and answered three more with
a bare `True`:

    "task_authority": dispatchable,     "pending_requests": True,
    "branch":         dispatchable,     "scheduled_deadlines": True,
    "worktree":       dispatchable,     "last_external_effect": True,
    "git_and_remote_state": dispatchable,
    "auth":           dispatchable,
    "cli_capability_manifest": dispatchable,

A complete command line therefore CERTIFIED that the branch existed, that the
worktree was clean, that Git and the remote were in a known state, that auth was
present, that no approval was pending, that no deadline was outstanding, and that
the last external effect was accounted for - none of which it had looked at. The
supervisor could pass its own recovery gate while resting on nine facts nobody
had checked.

This module replaces those nine answers with real probes, plus two more the
directive names (config identity, surviving children) that are folded into
existing steps rather than widening `recovery.REVALIDATION_STEPS` - the step
vocabulary is frozen behaviour and does not need to change for the ANSWERS to
become honest.

FAIL-CLOSED IS THE WHOLE POINT. Every probe returns `ok` AND `known`, and only
``ok and known`` passes. "I could not determine this" is a failure, never a
shrug: `ProbeResult.passes` is the single place that rule lives, and
`recovery.classify` already treats a False step as UNSAFE_OR_DRIFTED, so an
unknown fact stops the run BEFORE any provider or GitHub contact.

INJECTION, NOT NETWORK. Every external reader is a parameter: the Git runner, the
remote-reachability check, the auth check, and the clock. Production wires
subprocess Git and the real filesystem; the tests wire fakes and never touch a
network, a provider, or a real repository. The remote probe in particular is
STRUCTURED but not automatically executed: a local task-branch run does not need
`origin` to be reachable, so the expectation is explicit
(`remote_reachability_required`) and, when it IS required, an unproven result
fails closed.
"""
from __future__ import annotations

import dataclasses
import json
import os
import pathlib
import re
import subprocess
from typing import Any, Callable, Mapping, Sequence

from .durable_state import JournalError
from .preflight import CAPABILITY_KEY
from .process import ProcessError, executable_identity
from .recovery import CHILD_PROCESSES_KEY, account_for_children
from .resume_scheduler import RESUME_NOT_BEFORE_KEY
from .run_budget import Clock, system_clock, utc_iso_for

#: The durable key the resolved provider-executable identities are pinned under.
#: First start records them; every later start must MATCH or the run refuses -
#: a provider CLI that changed under an unattended controller is drift, not a
#: detail (AD-093 "provider CLI/API drift").
EXECUTABLE_IDENTITY_KEY = "cli_executable_identity"

#: Task statuses in which a packet actually confers working authority. Same set
#: `policy.TaskAuthority.from_packet` uses for `active`, referenced rather than
#: restated so the two can never drift apart.
WORKING_STATUSES: frozenset[str] = frozenset({"in_progress", "claimed", "awaiting_gate"})

#: Files in the git directory that mean an operation is half-finished. A worktree
#: mid-merge/rebase/cherry-pick/bisect is not a base a supervised run may build on.
IN_PROGRESS_MARKERS: tuple[str, ...] = (
    "MERGE_HEAD", "REBASE_HEAD", "rebase-merge", "rebase-apply",
    "CHERRY_PICK_HEAD", "REVERT_HEAD", "BISECT_LOG",
)

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


# --------------------------------------------------------------------------
# Results
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ProbeResult:
    """One revalidation answer, and whether it was actually established.

    `known=False` means the probe could not determine the fact. That is NOT a
    pass, and `passes` is the only place that judgement is made.
    """

    step: str
    ok: bool
    known: bool = True
    reason_code: str = ""
    detail: str = ""
    evidence: Mapping[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "evidence", dict(self.evidence or {}))

    @property
    def passes(self) -> bool:
        """A probe passes only when it is BOTH established and satisfied."""
        return bool(self.ok and self.known)

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        data["passes"] = self.passes
        return data


def _ok(step: str, detail: str, **evidence: Any) -> ProbeResult:
    return ProbeResult(step, True, True, "", detail, evidence)


def _fail(step: str, reason_code: str, detail: str, **evidence: Any) -> ProbeResult:
    return ProbeResult(step, False, True, reason_code, detail, evidence)


def _unknown(step: str, reason_code: str, detail: str, **evidence: Any) -> ProbeResult:
    """An UNDETERMINED fact. Fails closed exactly like a failed one."""
    return ProbeResult(step, False, False, reason_code, detail, evidence)


@dataclasses.dataclass(frozen=True)
class ProbeReport:
    """Every probe this start ran, and the revalidation map recovery consumes."""

    results: tuple[ProbeResult, ...]

    def by_step(self) -> dict[str, ProbeResult]:
        return {result.step: result for result in self.results}

    def revalidation(self, steps: Sequence[str]) -> dict[str, bool]:
        """The `{step: bool}` map for `recover_boot`, restricted to `steps`.

        A step this report has no result for is simply ABSENT, and
        `recovery.classify` already treats a missing result as a failed check -
        so an unrun probe can never be mistaken for a passed one.
        """
        answers = self.by_step()
        return {step: answers[step].passes for step in steps if step in answers}

    def failures(self) -> tuple[ProbeResult, ...]:
        return tuple(r for r in self.results if not r.passes)

    def to_dict(self) -> dict[str, Any]:
        return {"probes": [r.to_dict() for r in self.results],
                "failed": [r.step for r in self.failures()]}


# --------------------------------------------------------------------------
# The Git seam
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class GitResult:
    """One Git invocation. `ran=False` means the command could not be executed."""

    returncode: int = 0
    stdout: str = ""
    stderr: str = ""
    ran: bool = True

    @property
    def ok(self) -> bool:
        return self.ran and self.returncode == 0

    @property
    def text(self) -> str:
        return self.stdout.strip()


#: A Git runner takes (argv-after-`git`, cwd) and returns a `GitResult`.
GitRunner = Callable[[Sequence[str], str], GitResult]


def subprocess_git(executable: str = "git", *, timeout_seconds: float = 30.0) -> GitRunner:
    """The production Git runner. Never used by the tests, which inject fakes."""

    def run(argv: Sequence[str], cwd: str) -> GitResult:
        try:
            completed = subprocess.run(  # noqa: S603 - fixed argv head, no shell
                [executable, *argv], cwd=cwd, capture_output=True, text=True,
                timeout=timeout_seconds, check=False)
        except (OSError, subprocess.SubprocessError) as exc:
            return GitResult(ran=False, stderr=f"{type(exc).__name__}: {exc}")
        return GitResult(returncode=completed.returncode,
                         stdout=completed.stdout or "", stderr=completed.stderr or "")

    return run


# --------------------------------------------------------------------------
# Probes
# --------------------------------------------------------------------------


def probe_task_authority(*, packet: Mapping[str, Any], repo_root: str,
                         packet_path: str = "") -> ProbeResult:
    """The packet confers live authority AND the ledger agrees it does.

    The packet on disk is the supervisor's authority source (never a model's
    description of the task), but a packet copy can be stale. The LEDGER entry
    under `project-control/tasks/<task_id>.json` is the control plane's record,
    so this requires both to exist and to agree on the task id and status, and
    requires that status to be one that actually confers work.
    """
    step = "task_authority"
    task_id = str(packet.get("task_id", "") or "")
    if not task_id:
        return _fail(step, "packet_without_task_id",
                     f"the task packet at {packet_path or '<unnamed>'} names no task_id; a "
                     f"packet that does not say which task it is confers no authority")
    status = str(packet.get("status", "") or "")
    if status not in WORKING_STATUSES:
        return _fail(step, "task_not_active",
                     f"task {task_id} is {status!r}; a supervised run needs a status that "
                     f"confers work ({sorted(WORKING_STATUSES)})",
                     task_id=task_id, status=status)
    ledger_path = pathlib.Path(repo_root) / "project-control" / "tasks" / f"{task_id}.json"
    if not ledger_path.is_file():
        return _unknown(step, "ledger_record_missing",
                        f"no ledger record at {ledger_path}; the packet's claim to authority "
                        f"cannot be corroborated against the control plane, and an "
                        f"uncorroborated authority claim is never assumed true",
                        task_id=task_id, ledger_path=str(ledger_path))
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        return _unknown(step, "ledger_record_unreadable",
                        f"the ledger record {ledger_path} could not be read ({exc}); an "
                        f"unreadable authority record fails closed",
                        task_id=task_id)
    if str(ledger.get("task_id", "")) != task_id:
        return _fail(step, "ledger_task_id_mismatch",
                     f"the ledger record at {ledger_path} names task "
                     f"{ledger.get('task_id')!r}, not {task_id!r}",
                     task_id=task_id)
    ledger_status = str(ledger.get("status", "") or "")
    if ledger_status != status:
        return _fail(step, "ledger_status_mismatch",
                     f"the packet says task {task_id} is {status!r} and the ledger says "
                     f"{ledger_status!r}; the supervisor never picks the more permissive of "
                     f"two disagreeing authority records",
                     task_id=task_id, packet_status=status, ledger_status=ledger_status)
    blockers = ledger.get("blockers") or []
    if blockers:
        return _fail(step, "task_blocked",
                     f"task {task_id} has {len(blockers)} unresolved blocker(s) in the "
                     f"ledger; a blocked task confers no authority to continue",
                     task_id=task_id)
    return _ok(step, f"task {task_id} is {status!r} in both the packet and the ledger, with "
                     f"no unresolved blockers", task_id=task_id, status=status)


def probe_branch(*, git: GitRunner, worktree: str, expected_branch: str = "") -> ProbeResult:
    """A named, checked-out branch exists - and matches `--branch` when given."""
    step = "branch"
    result = git(("rev-parse", "--abbrev-ref", "HEAD"), worktree)
    if not result.ran:
        return _unknown(step, "git_unavailable",
                        f"git could not be run in {worktree} ({result.stderr.strip()}); the "
                        f"checked-out branch is undetermined, which fails closed")
    if not result.ok:
        return _fail(step, "no_checked_out_branch",
                     f"git could not name the checked-out branch in {worktree}: "
                     f"{result.stderr.strip() or result.stdout.strip()}")
    branch = result.text
    if not branch or branch == "HEAD":
        return _fail(step, "detached_head",
                     f"{worktree} is on a detached HEAD; a supervised run needs a real "
                     f"branch to attribute its work to", branch=branch)
    if expected_branch and branch != expected_branch:
        return _fail(step, "branch_mismatch",
                     f"the run was authorized for branch {expected_branch!r} but "
                     f"{worktree} has {branch!r} checked out",
                     branch=branch, expected=expected_branch)
    return _ok(step, f"{worktree} is on branch {branch!r}", branch=branch)


def probe_worktree(*, git: GitRunner, worktree: str, repo_root: str = "") -> ProbeResult:
    """The worktree exists, is the Git work tree it claims to be, and is settled."""
    step = "worktree"
    path = pathlib.Path(worktree)
    if not path.is_dir():
        return _fail(step, "worktree_missing",
                     f"the authorized worktree {worktree} does not exist or is not a "
                     f"directory")
    inside = git(("rev-parse", "--is-inside-work-tree"), worktree)
    if not inside.ran:
        return _unknown(step, "git_unavailable",
                        f"git could not be run in {worktree} ({inside.stderr.strip()}); "
                        f"whether it is a work tree is undetermined")
    if not inside.ok or inside.text != "true":
        return _fail(step, "not_a_work_tree",
                     f"{worktree} is not inside a Git work tree; the supervisor refuses to "
                     f"run against a directory whose history it cannot read")
    git_dir = git(("rev-parse", "--absolute-git-dir"), worktree)
    if not git_dir.ok:
        return _unknown(step, "git_dir_undetermined",
                        f"the git directory for {worktree} could not be resolved "
                        f"({git_dir.stderr.strip()})")
    marker_root = pathlib.Path(git_dir.text)
    in_progress = [name for name in IN_PROGRESS_MARKERS if (marker_root / name).exists()]
    if in_progress:
        return _fail(step, "operation_in_progress",
                     f"{worktree} has an unfinished Git operation ({in_progress}); a "
                     f"half-completed merge, rebase, cherry-pick, revert, or bisect is not a "
                     f"base a supervised run may build on",
                     markers=in_progress)
    unmerged = git(("diff", "--name-only", "--diff-filter=U"), worktree)
    if not unmerged.ran:
        return _unknown(step, "git_unavailable",
                        f"unmerged paths in {worktree} could not be listed "
                        f"({unmerged.stderr.strip()})")
    if unmerged.ok and unmerged.text:
        paths = [line for line in unmerged.text.splitlines() if line.strip()]
        return _fail(step, "unmerged_paths",
                     f"{worktree} has {len(paths)} unresolved conflicted path(s); the "
                     f"worktree is not clean enough to run in", paths=paths[:20])
    detail = f"{worktree} is a settled Git work tree with no unresolved conflicts"
    if repo_root:
        detail += f" (repository root {repo_root})"
    return _ok(step, detail, git_dir=str(marker_root))


def probe_git_and_remote_state(
    *, git: GitRunner, worktree: str, remote: str = "origin",
    remote_reachability_required: bool = False,
    reachability: Callable[[str], ProbeResult] | None = None,
) -> ProbeResult:
    """HEAD resolves, the repository answers, and the remote EXPECTATION holds.

    Reachability is an expectation, not an assumption. A local task-branch run
    does not need `origin` to answer, so by default this records the configured
    remote and passes. When the caller states that the run WILL need the remote
    (`remote_reachability_required`), an unproven or unreachable remote fails
    closed - and the check itself is injected, so no test contacts a network.
    """
    step = "git_and_remote_state"
    head = git(("rev-parse", "HEAD"), worktree)
    if not head.ran:
        return _unknown(step, "git_unavailable",
                        f"git could not be run in {worktree} ({head.stderr.strip()}); the "
                        f"repository state is undetermined")
    if not head.ok or not _SHA_RE.match(head.text):
        return _fail(step, "head_unresolved",
                     f"HEAD in {worktree} does not resolve to a commit "
                     f"({head.text or head.stderr.strip()!r}); an empty or broken history is "
                     f"not a state a supervised run may start from")
    status = git(("status", "--porcelain"), worktree)
    if not status.ran or not status.ok:
        return _unknown(step, "status_undetermined",
                        f"git status did not answer in {worktree} "
                        f"({status.stderr.strip()}); the working state is undetermined")
    remote_url = git(("remote", "get-url", remote), worktree)
    configured = remote_url.text if remote_url.ok else ""
    if remote_reachability_required:
        if reachability is None:
            return _unknown(
                step, "remote_reachability_unprovable",
                f"this run requires {remote!r} to be reachable but no reachability check "
                f"was supplied; an unproven remote expectation fails closed")
        if not configured:
            return _fail(step, "remote_not_configured",
                         f"this run requires {remote!r} to be reachable but no such remote "
                         f"is configured in {worktree}")
        verdict = reachability(configured)
        if not verdict.passes:
            return ProbeResult(step, verdict.ok, verdict.known,
                               verdict.reason_code or "remote_unreachable",
                               f"the required remote {remote!r} ({configured}) did not "
                               f"answer: {verdict.detail}",
                               {"remote": remote, "url": configured})
        return _ok(step,
                   f"HEAD is {head.text}, the repository answers, and the required remote "
                   f"{remote!r} is reachable", head=head.text, remote=remote,
                   remote_url=configured, remote_reachable=True)
    return _ok(step,
               f"HEAD is {head.text} and the repository answers; remote {remote!r} is "
               f"{configured or 'not configured'} and this run does not require it to be "
               f"reachable (no push is authorized here)",
               head=head.text, remote=remote, remote_url=configured,
               remote_reachable=None)


def probe_auth(*, executables: Mapping[str, str],
               auth_check: Callable[[], ProbeResult] | None = None) -> ProbeResult:
    """The named provider executables are present, and any auth check passes.

    Presence is checked at the EXACT path the operator named - never a PATH
    search (S13.4). A live credential round trip is an injected check: when one
    is supplied its verdict is authoritative and an undetermined result fails
    closed; when none is supplied this reports exactly what it proved and no more.
    """
    step = "auth"
    missing = sorted(name for name, path in executables.items()
                     if not path or not pathlib.Path(path).is_file())
    if missing:
        return _fail(step, "executable_missing",
                     f"the executables named for {missing} do not exist at the paths given; "
                     f"nothing is discovered from PATH, so a missing binary is a refusal",
                     missing=missing)
    if auth_check is not None:
        verdict = auth_check()
        if not verdict.passes:
            return ProbeResult(step, verdict.ok, verdict.known,
                               verdict.reason_code or "auth_unproven",
                               f"the provider auth check did not pass: {verdict.detail}")
        return _ok(step, f"every named executable exists and the provider auth check "
                         f"passed: {verdict.detail}", checked=sorted(executables))
    return _ok(step,
               f"every named provider executable exists at the exact path given "
               f"({sorted(executables)}); no live credential round trip was performed, so "
               f"this asserts presence only",
               checked=sorted(executables), live_credential_check=False)


def probe_cli_capability_manifest(
    *, journal: Any, executables: Mapping[str, str], record: bool = True,
) -> ProbeResult:
    """No recorded capability probe FAILED, and the provider CLIs have not drifted.

    Two facts, both live. First, `preflight.record_probe` persists every
    capability probe the controller has run; a recorded FAILED probe means the
    installed CLI does not do something this build depends on, and a run must not
    start over it. Second, the resolved identity of each provider executable is
    pinned on first start and compared on every later one, so a CLI that was
    replaced or upgraded under an unattended controller is detected as drift
    instead of being discovered mid-run.
    """
    step = "cli_capability_manifest"
    probes = journal.get_state(CAPABILITY_KEY, {}) or {}
    if isinstance(probes, Mapping):
        failed = sorted(name for name, value in probes.items()
                        if isinstance(value, Mapping) and str(value.get("status", ""))
                        .upper() == "FAILED")
        if failed:
            return _fail(step, "capability_probe_failed",
                         f"recorded capability probes {failed} FAILED against the installed "
                         f"CLI; a run never starts on a capability the controller has "
                         f"already measured as absent", failed=failed)
    else:
        return _unknown(step, "capability_record_unreadable",
                        "the recorded capability probes are not a readable record; an "
                        "unreadable capability manifest fails closed")

    observed: dict[str, dict[str, Any]] = {}
    for name in sorted(executables):
        path = executables[name]
        try:
            identity = executable_identity(path, name=name)
        except (ProcessError, OSError) as exc:
            return _unknown(step, "executable_identity_unprovable",
                            f"the identity of the {name} executable at {path} could not be "
                            f"established ({exc}); an unidentifiable toolchain binary fails "
                            f"closed")
        observed[name] = {"path": identity.path, "size_bytes": identity.size_bytes,
                          "digest": identity.digest, "digest_kind": identity.digest_kind}

    pinned = journal.get_state(EXECUTABLE_IDENTITY_KEY, None)
    if isinstance(pinned, Mapping) and pinned:
        drifted = sorted(
            name for name, value in observed.items()
            if name in pinned and isinstance(pinned[name], Mapping)
            and (pinned[name].get("digest") != value["digest"]
                 or pinned[name].get("path") != value["path"]))
        if drifted:
            return _fail(step, "provider_cli_drift",
                         f"the provider executables {drifted} are not the ones this run was "
                         f"pinned to; a CLI that changed under an unattended controller is "
                         f"drift and must be re-established explicitly, not discovered "
                         f"mid-run", drifted=drifted)
        merged = {**{k: dict(v) for k, v in pinned.items() if isinstance(v, Mapping)},
                  **observed}
    else:
        merged = observed
    if record:
        try:
            journal.set_state(EXECUTABLE_IDENTITY_KEY, merged)
        except JournalError as exc:  # pragma: no cover - defensive
            return _unknown(step, "identity_pin_unwritable",
                            f"the provider-executable identity pin could not be written "
                            f"({exc}); an unrecorded pin cannot detect later drift")
    return _ok(step,
               f"no recorded capability probe failed and every provider executable matches "
               f"its pinned identity ({sorted(observed)})",
               pinned=sorted(merged))


def probe_pending_requests(*, journal: Any) -> ProbeResult:
    """No approval request is still waiting for a human.

    Read from durable state, not assumed. An open ASK is precisely the condition
    an unattended start must not run past: the previous run stopped to ask
    something, and starting again would abandon the question.
    """
    step = "pending_requests"
    try:
        open_asks = journal.open_asks()
    except Exception as exc:  # a journal that cannot answer is not an empty queue
        return _unknown(step, "pending_requests_unreadable",
                        f"the queued approval requests could not be read ({exc}); an "
                        f"unreadable request queue is never treated as an empty one")
    if open_asks:
        ids = [getattr(ask, "ask_id", "") for ask in open_asks]
        return _fail(step, "approval_pending",
                     f"{len(ids)} approval request(s) are still unanswered ({ids[:5]}); a "
                     f"run does not start past a question the owner has not answered",
                     ask_ids=ids[:20])
    return _ok(step, "no queued approval request is unanswered")


def probe_scheduled_deadlines(*, journal: Any,
                              clock: Clock = system_clock) -> ProbeResult:
    """The persisted usage-limit deadline is READABLE and its position is known.

    S11.5 gives an outstanding deadline its own dedicated outcome: `recover_boot`
    restores the timer (`deadline_restored`) and contacts no provider before it.
    So an outstanding deadline is NOT a failed revalidation here - failing the
    step would replace that specific, actionable verdict with a generic drift
    one. What this step answers is the question S11.5 actually asks: was the
    deadline state revalidated, or merely assumed? An unparseable deadline is
    undetermined, and an undetermined deadline is honoured rather than ignored.
    """
    step = "scheduled_deadlines"
    raw = str(journal.get_state(RESUME_NOT_BEFORE_KEY, "") or "")
    if not raw:
        return _ok(step, "no usage-limit deadline is persisted")
    now = utc_iso_for(clock())
    if not re.match(r"^\d{4}-\d{2}-\d{2}T", raw):
        return _unknown(step, "deadline_unparseable",
                        f"the persisted resume deadline {raw!r} is not a UTC timestamp this "
                        f"build can compare; an unreadable deadline is honoured, never "
                        f"ignored", deadline=raw)
    if raw > now:
        return _ok(step, f"a usage-limit deadline is persisted and holds until {raw} (now "
                         f"{now}); recovery restores the timer and contacts no provider "
                         f"before it", deadline=raw, now=now, outstanding=True)
    return _ok(step, f"the persisted deadline {raw} has passed (now {now})",
               deadline=raw, now=now, outstanding=False)


def probe_last_external_effect(*, journal: Any) -> ProbeResult:
    """The external-effect journal is READABLE and its pending set is known.

    A PENDING effect means "this may have happened", and S11.5 gives that its own
    outcome: `recover_boot` classifies AMBIGUOUS_EFFECT and sends the run to
    RECONCILE_EXTERNAL_EFFECT to prove what occurred from read-only evidence.
    Failing this step on a pending effect would let UNSAFE_OR_DRIFTED dominate
    and throw that guidance away, so a pending effect PASSES this step carrying
    the ids as evidence; only an effect journal that cannot be read at all is a
    failure, because "I could not look" is never "there is nothing there".
    """
    step = "last_external_effect"
    try:
        pending = list(journal.pending_effects())
    except Exception as exc:
        return _unknown(step, "effects_unreadable",
                        f"the external-effect journal could not be read ({exc}); an "
                        f"unreadable effect log is never treated as an empty one")
    if pending:
        ids = [effect.action_id for effect in pending]
        return _ok(step,
                   f"{len(ids)} journaled external effect(s) have no verified after-record "
                   f"({ids[:5]}); recovery classifies this AMBIGUOUS_EFFECT and proves each "
                   f"from read-only evidence rather than rerunning it",
                   action_ids=ids[:20], unreconciled=len(ids))
    return _ok(step, "every journaled external effect has a verified after-record")


def probe_config_identity(*, manifest_ok: bool, manifest_reason: str = "",
                          config_path: str = "") -> ProbeResult:
    """The immutable controller config is the one the manifest binds.

    Folded into the `controller_manifest` step rather than given a step of its
    own: `manifest.verify_manifest_with_config` already verifies the external
    config under its stable logical name, so this names the fact explicitly for
    the refusal detail without widening the frozen step vocabulary.
    """
    step = "config_identity"
    if not config_path:
        return _fail(step, "config_not_named",
                     "no immutable controller config was named; the limits, model chain, "
                     "and policy bounds a run is held to must come from a named file")
    if not pathlib.Path(config_path).is_file():
        return _fail(step, "config_missing",
                     f"the named controller config {config_path} does not exist")
    if not manifest_ok:
        return _fail(step, "config_binding_unverified",
                     f"the controller manifest did not verify the config binding "
                     f"({manifest_reason or 'not established'}); the config this run would "
                     f"read is not provably the one the manifest covers",
                     config_path=config_path)
    return _ok(step, f"the controller manifest verifies {config_path} under its stable "
                     f"logical name", config_path=config_path)


def probe_surviving_children(*, journal: Any) -> ProbeResult:
    """No recorded child process survived the discontinuity, and none is unknown.

    `recover_boot` already consumes this through `account_for_children`, which is
    what actually gates the classification. Running it here too surfaces WHICH
    child is the problem in the refusal payload, and costs one read.
    """
    step = "surviving_children"
    try:
        accounts = account_for_children(journal)
    except Exception as exc:
        return _unknown(step, "children_unreadable",
                        f"the recorded child processes could not be accounted for ({exc}); "
                        f"an unreadable child record is never read as 'nothing is running'",
                        key=CHILD_PROCESSES_KEY)
    surviving = [a.pid for a in accounts if a.surviving]
    undetermined = [a.pid for a in accounts if not a.determined]
    if surviving or undetermined:
        return _fail(step, "child_unaccounted",
                     f"recorded child processes survived or could not be determined "
                     f"(surviving={surviving}, undetermined={undetermined}); starting over a "
                     f"live worker is how one task gets two",
                     surviving=surviving, undetermined=undetermined)
    return _ok(step, f"all {len(accounts)} recorded child process(es) are accounted for")


# --------------------------------------------------------------------------
# The suite
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ProbeInputs:
    """Everything the live suite reads, injected so nothing is discovered."""

    journal: Any
    packet: Mapping[str, Any]
    repo_root: str
    worktree: str
    packet_path: str = ""
    expected_branch: str = ""
    executables: Mapping[str, str] = dataclasses.field(default_factory=dict)
    config_path: str = ""
    manifest_ok: bool = False
    manifest_reason: str = ""
    remote: str = "origin"
    remote_reachability_required: bool = False
    git: GitRunner | None = None
    reachability: Callable[[str], ProbeResult] | None = None
    auth_check: Callable[[], ProbeResult] | None = None
    clock: Clock = system_clock
    record_identity: bool = True


def run_live_probes(inputs: ProbeInputs) -> ProbeReport:
    """Run every live probe in one pass. Never contacts a provider or GitHub.

    The order is S11.5's, and no probe short-circuits another: the report always
    carries every answer, so the refusal names EVERY fact that is missing rather
    than only the first one found.
    """
    git = inputs.git if inputs.git is not None else subprocess_git()
    return ProbeReport(results=(
        probe_task_authority(packet=inputs.packet, repo_root=inputs.repo_root,
                             packet_path=inputs.packet_path),
        probe_branch(git=git, worktree=inputs.worktree,
                     expected_branch=inputs.expected_branch),
        probe_worktree(git=git, worktree=inputs.worktree, repo_root=inputs.repo_root),
        probe_git_and_remote_state(
            git=git, worktree=inputs.worktree, remote=inputs.remote,
            remote_reachability_required=inputs.remote_reachability_required,
            reachability=inputs.reachability),
        probe_auth(executables=inputs.executables, auth_check=inputs.auth_check),
        probe_cli_capability_manifest(journal=inputs.journal,
                                      executables=inputs.executables,
                                      record=inputs.record_identity),
        probe_pending_requests(journal=inputs.journal),
        probe_scheduled_deadlines(journal=inputs.journal, clock=inputs.clock),
        probe_last_external_effect(journal=inputs.journal),
        probe_config_identity(manifest_ok=inputs.manifest_ok,
                              manifest_reason=inputs.manifest_reason,
                              config_path=inputs.config_path),
        probe_surviving_children(journal=inputs.journal),
    ))


#: Probes that ANSWER a `recovery.REVALIDATION_STEPS` entry directly.
STEP_PROBES: tuple[str, ...] = (
    "task_authority", "branch", "worktree", "git_and_remote_state", "auth",
    "cli_capability_manifest", "pending_requests", "scheduled_deadlines",
    "last_external_effect",
)

#: Probes the directive names that are FOLDED into an existing step rather than
#: widening the frozen step vocabulary. `config_identity` strengthens
#: `controller_manifest`; `surviving_children` reports what `recover_boot`'s own
#: child accounting already gates on.
FOLDED_PROBES: tuple[str, ...] = ("config_identity", "surviving_children")


def default_worktree(repo_root: str, worktree: str = "") -> str:
    """The worktree a probe runs in: the named one, else the repository root."""
    return str(pathlib.Path(worktree or repo_root).resolve())


def named_executables(**paths: str | None) -> dict[str, str]:
    """Drop the executables the operator did not name; keep the rest verbatim."""
    return {name: os.fspath(path) for name, path in paths.items() if path}
