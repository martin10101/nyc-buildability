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
import datetime as _dt
import json
import os
import pathlib
import re
import subprocess
from typing import Any, Callable, Mapping, Sequence

from .durable_state import JournalError
from .models import to_utc_iso
from .preflight import CAPABILITY_KEY
# M0-T079 correction round: the shared result vocabulary and the control-plane
# probes now live in their own modules. Re-exported here so every caller, test,
# and `from .recovery_probes import ...` site is unchanged.
from .probe_control_plane import (  # noqa: F401
    WORKING_STATUSES,
    open_blockers_for,
    probe_task_authority,
)
from .probe_result import (
    ProbeReport,
    ProbeResult,
    fail_probe as _fail,
    ok_probe as _ok,
    unknown_probe as _unknown,
)
from .process import ProcessError, executable_identity
from .recovery import CHILD_PROCESSES_KEY, account_for_children
from .resume_scheduler import RESUME_NOT_BEFORE_KEY
from .run_budget import Clock, system_clock, utc_iso_for

#: The durable key the resolved provider-executable identities are pinned under.
#: First start records them; every later start must MATCH or the run refuses -
#: a provider CLI that changed under an unattended controller is drift, not a
#: detail (AD-093 "provider CLI/API drift").
EXECUTABLE_IDENTITY_KEY = "cli_executable_identity"

#: Files in the git directory that mean an operation is half-finished. A worktree
#: mid-merge/rebase/cherry-pick/bisect is not a base a supervised run may build on.
IN_PROGRESS_MARKERS: tuple[str, ...] = (
    "MERGE_HEAD", "REBASE_HEAD", "rebase-merge", "rebase-apply",
    "CHERRY_PICK_HEAD", "REVERT_HEAD", "BISECT_LOG",
)

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


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
    repin: bool = False, audit: Any = None,
) -> ProbeResult:
    """No recorded capability probe FAILED, and the provider CLIs have not drifted.

    Two facts, both live. First, `preflight.record_probe` persists every
    capability probe the controller has run; a recorded FAILED probe means the
    installed CLI does not do something this build depends on, and a run must not
    start over it. Second, the resolved identity of each provider executable is
    pinned on first start and compared on every later one, so a CLI that was
    replaced or upgraded under an unattended controller is detected as drift
    instead of being discovered mid-run.

    C10 (G3 I-3) adds the way OUT. Detection is unchanged and still refuses by
    default; what was missing was any supported remedy, so a routine Claude Code
    or Codex auto-update bricked every subsequent `start` on that checkout with
    no option but deleting the journal - destroying the run's durable evidence,
    which is the thing the rest of this task exists to preserve. `repin=True`
    (the operator's explicit `--repin-cli-identity`) accepts the NEW identity,
    records it with provenance - what it replaced, when, and that an owner asked
    for it - and seals an audit event. A per-launch human act, never a default,
    and not reachable from a synthesized argv or a config value.
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
    repinned: list[str] = []
    if isinstance(pinned, Mapping) and pinned:
        drifted = sorted(
            name for name, value in observed.items()
            if name in pinned and isinstance(pinned[name], Mapping)
            and (pinned[name].get("digest") != value["digest"]
                 or pinned[name].get("path") != value["path"]))
        if drifted and not repin:
            return _fail(step, "provider_cli_drift",
                         f"the provider executables {drifted} are not the ones this run was "
                         f"pinned to; a CLI that changed under an unattended controller is "
                         f"drift and must be re-established explicitly, not discovered "
                         f"mid-run. If the change was a legitimate update, re-pin it "
                         f"deliberately with `--repin-cli-identity`, which records the new "
                         f"identity with provenance and seals an audit event",
                         drifted=drifted)
        merged = {**{k: dict(v) for k, v in pinned.items() if isinstance(v, Mapping)},
                  **observed}
        for name in drifted:
            previous = pinned[name] if isinstance(pinned.get(name), Mapping) else {}
            merged[name] = {**observed[name],
                            "repinned_at_utc": to_utc_iso(),
                            "repinned_by": "operator --repin-cli-identity",
                            "replaced_digest": str(previous.get("digest", "") or ""),
                            "replaced_path": str(previous.get("path", "") or "")}
            repinned.append(name)
        if repinned and audit is not None:
            try:
                audit.append(
                    "cli_identity_repinned", policy_result="owner_repin",
                    detail={"repinned": repinned,
                            "note": "an operator explicitly accepted a changed provider "
                                    "CLI identity; drift detection itself is unchanged"})
            except Exception:  # pragma: no cover - a damaged chain is its own evidence
                pass
    else:
        merged = observed
    if record:
        try:
            journal.set_state(EXECUTABLE_IDENTITY_KEY, merged)
        except JournalError as exc:  # pragma: no cover - defensive
            return _unknown(step, "identity_pin_unwritable",
                            f"the provider-executable identity pin could not be written "
                            f"({exc}); an unrecorded pin cannot detect later drift")
    if repinned:
        return _ok(step,
                   f"an operator re-pinned the provider executables {repinned} to their "
                   f"current identity with recorded provenance; drift detection resumes "
                   f"against the new pin", pinned=sorted(merged), repinned=repinned)
    return _ok(step,
               f"no recorded capability probe failed and every provider executable matches "
               f"its pinned identity ({sorted(observed)})",
               pinned=sorted(merged), repinned=[])


def probe_pending_requests(*, journal: Any) -> ProbeResult:
    """No approval request is still waiting for a human.

    Read from durable state, not assumed. An open ASK is precisely the condition
    an unattended start must not run past: the previous run stopped to ask
    something, and starting again would abandon the question.
    """
    step = "pending_requests"
    # M0-T115 (D-024-R274, the M0-T113 live-restart defect): read through the
    # shared broker reconciliation - a broker-origin ask the owner has already
    # answered is history, not an open question, so journals written BEFORE the
    # broker-side fix stay truthful without any journal write. Non-broker asks
    # and still-pending records block exactly as before.
    from .broker import owner_unanswered_asks
    try:
        open_asks = owner_unanswered_asks(journal)
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
    now_epoch = float(clock())
    now = utc_iso_for(now_epoch)
    if not raw:
        return _ok(step, "no usage-limit deadline is persisted", outstanding=False)
    # C9: parse the INSTANT rather than compare ISO strings lexicographically.
    # The old comparison was guarded by a regex anchoring only
    # `^\d{4}-\d{2}-\d{2}T`, so an offset form, a different sub-second precision,
    # or a missing `Z` compared as TEXT - harmless while nothing consumed
    # `outstanding`, and load-bearing now that the dispatch gate does.
    deadline_epoch = parse_utc_instant(raw)
    if deadline_epoch is None:
        return _unknown(step, "deadline_unparseable",
                        f"the persisted resume deadline {raw!r} is not a UTC timestamp this "
                        f"build can compare; an unreadable deadline is honoured, never "
                        f"ignored", deadline=raw)
    if deadline_epoch > now_epoch:
        return _ok(step, f"a usage-limit deadline is persisted and holds until {raw} (now "
                         f"{now}); recovery restores the timer and contacts no provider "
                         f"before it", deadline=raw, now=now, outstanding=True)
    return _ok(step, f"the persisted deadline {raw} has passed (now {now})",
               deadline=raw, now=now, outstanding=False)


def parse_utc_instant(value: str) -> float | None:
    """Epoch seconds for a UTC ISO-8601 instant, or None when it is unreadable.

    Accepts the package's own `to_utc_iso` shape (`...Z`) and any offset form
    `datetime.fromisoformat` understands. A naive timestamp is treated as UTC
    rather than local: S11.4 calls ambiguous time a defect, and the supervisor
    only ever writes UTC. None means UNDETERMINED, which every caller honours
    rather than ignores.
    """
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    try:
        moment = _dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=_dt.timezone.utc)
    return moment.timestamp()


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
# Shell-routing drift tooth (D-024 Amendment 14, R295)
# --------------------------------------------------------------------------
#
# Qualifying evidence: D-024-R291 (the first live run's shell-first ASK stops,
# `M0-T113-activation-evidence.md` item 4, that no ledger task addressed). The
# certified loop must never dispatch on a Claude CLI whose tool-routing behavior
# has not been MEASURED for that exact installed identity - a CLI that started
# steering routine discovery/editing to shell ("bashFirst", GitHub issue #88041)
# under an unattended controller is drift, not a detail. This probe refuses
# fail-closed unless current shell-routing evidence exists whose recorded
# `claude_version` equals the installed CLI's version. It is a FOLDED probe (it
# strengthens the pinned-identity story `cli_capability_manifest` already tells)
# and follows the same conventions as the others: ok/known/reason_code/detail,
# and anything undetermined fails closed.

#: The packaged directory the version-keyed routing fixtures live in.
ROUTING_EVIDENCE_DIR = str(pathlib.Path(__file__).resolve().parent / "fixtures")

#: The routing fixtures this tooth reads, and the schema they must declare.
ROUTING_FIXTURE_GLOB = "shell_routing_*.json"
ROUTING_EVIDENCE_SCHEMA = "shell_routing/v1"

#: Durable-journal key holding routing evidence recorded for a specific pinned CLI
#: identity (the M0-T072 bound-manifest precedent: the certified identity records
#: its measured routing evidence durably, and the gate reads it - the SAME way a
#: bound manifest is recorded and then verified at dispatch). The shipped package
#: fixture covers the REAL installed claude; a run against any OTHER pinned identity
#: (an operator who re-measured routing after a CLI change; a test harness with a
#: FAKE executable) records that identity's evidence here, never in the shipped
#: `fixtures/` dir. Value is a list of {cli_identity, claude_version, verdict}.
SHELL_ROUTING_EVIDENCE_KEY = "shell_routing_evidence"


def record_routing_evidence(journal: Any, *, cli_identity: str,
                            claude_version: str = "",
                            verdict: str = "native_preferred") -> None:
    """Record a durable routing-evidence record for one pinned CLI identity.

    The M0-T072 precedent for a fake-executable harness (or an operator who
    re-measured routing for a changed CLI): the evidence is recorded in the DURABLE
    JOURNAL keyed on the identity it was measured against, and the pre-dispatch
    tooth reads it there - never by writing into the shipped `fixtures/` directory
    and never by special-casing the identity in production policy.
    """
    identity = str(cli_identity or "").strip()
    if not identity:
        raise JournalError("routing evidence requires a non-empty cli_identity")
    records = journal.get_state(SHELL_ROUTING_EVIDENCE_KEY, []) or []
    if not isinstance(records, list):
        records = []
    records = [r for r in records
              if not (isinstance(r, Mapping) and str(r.get("cli_identity", "")) == identity)]
    records.append({"cli_identity": identity, "claude_version": str(claude_version or ""),
                    "verdict": str(verdict or "")})
    journal.set_state(SHELL_ROUTING_EVIDENCE_KEY, records)


def _journal_routing_records(journal: Any) -> list[dict[str, Any]]:
    """Durable routing-evidence records, or [] when none/unreadable (fail closed)."""
    if journal is None:
        return []
    try:
        raw = journal.get_state(SHELL_ROUTING_EVIDENCE_KEY, []) or []
    except Exception:  # an unreadable journal is not evidence; the dir may still match
        return []
    out: list[dict[str, Any]] = []
    if isinstance(raw, list):
        for r in raw:
            if isinstance(r, Mapping) and str(r.get("cli_identity", "")).strip():
                out.append({"cli_identity": str(r.get("cli_identity", "")).strip(),
                            "claude_version": str(r.get("claude_version", "")).strip(),
                            "verdict": str(r.get("verdict", "")).strip()})
    return out


def default_claude_version_runner(executable_path: str) -> str:
    """`claude --version` as a bare version token, or ``""`` when unreadable.

    A bounded, read-only local subprocess (no network) - the same shape the Git
    seam uses. Returns only the leading version token (``2.1.251``) so it can be
    compared against a fixture's recorded ``claude_version``.
    """
    try:
        completed = subprocess.run(  # noqa: S603 - fixed argv head, no shell
            [executable_path, "--version"], capture_output=True, text=True,
            timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):
        return ""
    first = (completed.stdout or completed.stderr or "").strip().splitlines()
    if not first:
        return ""
    parts = first[0].split()
    return parts[0].strip() if parts else ""


def _dir_routing_records(directory: str) -> tuple[list[dict[str, Any]], str]:
    """Measured routing records from the fixtures dir, and an unreadable reason.

    Returns ``(records, unreadable_reason)``; a non-empty reason means the store
    itself could not be read (fail closed). A malformed individual fixture is
    skipped, never trusted and never fatal.
    """
    dpath = pathlib.Path(directory)
    if not dpath.is_dir():
        return [], ""  # a missing dir is "no evidence here", not "unreadable"
    try:
        fixtures = sorted(dpath.glob(ROUTING_FIXTURE_GLOB))
    except OSError as exc:
        return [], f"the evidence directory {directory} could not be listed ({exc})"
    records: list[dict[str, Any]] = []
    for path in fixtures:
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        if data.get("schema") != ROUTING_EVIDENCE_SCHEMA or data.get("measured") is not True:
            continue
        fx_identity = str(data.get("cli_identity", "")).strip()
        fx_version = str(data.get("claude_version", "")).strip()
        if not fx_identity and not fx_version:
            continue
        verdict = ""
        summary = data.get("routing_summary")
        if isinstance(summary, Mapping):
            verdict = str(summary.get("verdict", ""))
        records.append({"cli_identity": fx_identity, "claude_version": fx_version,
                        "verdict": verdict, "source": path.name})
    return records, ""


def probe_shell_routing_evidence(
    *, evidence_dir: str = "", installed_version: str = "",
    installed_identity: str = "", executable_path: str = "",
    version_runner: Callable[[str], str] | None = None,
    journal: Any = None,
) -> ProbeResult:
    """Current shell-routing evidence exists for the PINNED CLI identity (R295).

    The pinned identity is the executable DIGEST (``installed_identity``) - the
    same identity `_claude_cli_identity` / the capability-manifest machinery uses,
    computed by hashing the binary (no spawn, no provider call). Evidence comes
    from two durable sources: the shipped ``evidence_dir`` fixtures (the REAL
    installed claude) AND journal records under ``SHELL_ROUTING_EVIDENCE_KEY`` (the
    M0-T072 bound-manifest precedent - an operator who re-measured routing for a
    changed CLI, or a fake-executable harness, records that identity's evidence
    durably). A version string (``installed_version``, read/injected) is an
    ALTERNATE match key kept for direct/version-keyed use. Fails closed unless a
    measured record matches:

    * neither identity nor version can be determined -> UNDETERMINED (fails closed);
    * no measured routing evidence is present at all -> ``routing_evidence_absent``;
    * evidence is present but none matches the pinned identity -> a changed CLI
      whose routing was never measured, ``routing_evidence_stale``;
    * a record matches -> the routing was measured for this identity, PASS.

    Injected inputs only, so no test contacts a provider; a malformed or unreadable
    fixture is never counted as evidence.
    """
    step = "shell_routing"
    directory = evidence_dir or ROUTING_EVIDENCE_DIR
    identity = installed_identity.strip() if isinstance(installed_identity, str) else ""
    version = installed_version.strip() if isinstance(installed_version, str) else ""
    if not identity and not version and executable_path:
        runner = version_runner or default_claude_version_runner
        try:
            version = str(runner(executable_path) or "").strip()
        except Exception:  # a version probe that raised did not establish a version
            version = ""
    #: The token the refusal detail names as the pinned identity.
    pinned = identity or version
    if not pinned:
        return _unknown(step, "cli_version_undetermined",
                        "the installed Claude CLI identity could not be determined (no "
                        "digest or version), so current shell-routing evidence cannot be "
                        "matched to the pinned identity; an unverifiable identity fails closed")
    dir_records, unreadable = _dir_routing_records(directory)
    if unreadable:
        return _unknown(step, "routing_evidence_unreadable",
                        f"{unreadable}; an unreadable evidence store fails closed")
    records = dir_records + _journal_routing_records(journal)
    evidence_identities: list[str] = []
    for rec in records:
        fx_identity = str(rec.get("cli_identity", "")).strip()
        fx_version = str(rec.get("claude_version", "")).strip()
        evidence_identities.append(fx_identity or fx_version)
        # Match on the DIGEST identity when the gate supplied one; otherwise fall
        # back to the version string (direct/version-keyed callers and tests).
        matched = ((identity and fx_identity and fx_identity == identity)
                   or (not identity and version and fx_version == version))
        if matched:
            return _ok(step,
                       f"measured shell-routing evidence exists for the pinned CLI "
                       f"identity {pinned!r} ({rec.get('source', 'journal')}; routing "
                       f"verdict {rec.get('verdict', '')!r})",
                       cli_identity=pinned, claude_version=fx_version,
                       fixture=str(rec.get("source", "journal")),
                       routing_verdict=str(rec.get("verdict", "")))
    if evidence_identities:
        return _fail(step, "routing_evidence_stale",
                     f"shell-routing evidence exists but only for "
                     f"{sorted(set(evidence_identities))}, not the pinned CLI identity "
                     f"{pinned!r}; changed shell-routing behavior must be re-measured "
                     f"before it enters a certified run",
                     pinned_identity=pinned,
                     evidence_identities=sorted(set(evidence_identities)))
    return _fail(step, "routing_evidence_absent",
                 f"no measured shell-routing evidence for the pinned CLI identity "
                 f"{pinned!r} was found (dir {directory} + journal)",
                 pinned_identity=pinned)


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
    #: C10: the owner's explicit acceptance of a legitimately changed provider
    #: CLI. Default False keeps drift DETECTION exactly as strict as it was.
    repin_cli_identity: bool = False
    #: The hash-chained audit log, so a re-pin leaves a durable owner-visible
    #: record. Default None keeps every existing caller unchanged.
    audit: Any = None
    #: R295 shell-routing drift tooth. `installed_cli_identity` is the executable
    #: DIGEST the gate holds (same identity `_claude_cli_identity` uses; computed by
    #: hashing the binary, no spawn) - the primary match key. `installed_cli_version`
    #: is the alternate version-string key; when both are empty the tooth reads a
    #: version once from the claude executable via `routing_version_runner`.
    #: `routing_evidence_dir` defaults to the packaged fixtures directory. Injected
    #: so no test contacts a provider.
    installed_cli_identity: str = ""
    installed_cli_version: str = ""
    routing_evidence_dir: str = ""
    routing_version_runner: Callable[[str], str] | None = None


def _isolated(step: str, probe: Callable[[], ProbeResult]) -> ProbeResult:
    """Run one probe so a raise becomes ITS failure, not everyone else's.

    C5 (G5 I3): the eleven probes used to be arguments to a single tuple literal,
    so the first one to raise killed the other ten and the exception escaped
    `run_live_probes` entirely - `cmd_start` catches only a few exception classes
    and `main()` catches none, so an unreadable journal produced a traceback and
    the generic exit 1 that `refusals.py` numbers its codes from 10 specifically
    to avoid. Every probe now runs, and a raising probe is an UNDETERMINED fact,
    which fails closed exactly like a determined failure.
    """
    try:
        return probe()
    except Exception as exc:  # a probe that cannot answer is not a probe that passed
        return _unknown(step, "probe_raised",
                        f"the {step} probe could not complete ({type(exc).__name__}: "
                        f"{exc}); an unfinished check is never a passed one")


def run_live_probes(inputs: ProbeInputs) -> ProbeReport:
    """Run every live probe in one pass. Never contacts a provider or GitHub.

    The order is S11.5's, and no probe short-circuits another - not by returning
    a failure, and (since C5) not by raising either. The report always carries
    every answer, so the refusal names EVERY fact that is missing rather than
    only the first one found.
    """
    git = inputs.git if inputs.git is not None else subprocess_git()
    probes: tuple[tuple[str, Callable[[], ProbeResult]], ...] = (
        ("task_authority", lambda: probe_task_authority(
            packet=inputs.packet, repo_root=inputs.repo_root,
            packet_path=inputs.packet_path)),
        ("branch", lambda: probe_branch(
            git=git, worktree=inputs.worktree,
            expected_branch=inputs.expected_branch)),
        ("worktree", lambda: probe_worktree(
            git=git, worktree=inputs.worktree, repo_root=inputs.repo_root)),
        ("git_and_remote_state", lambda: probe_git_and_remote_state(
            git=git, worktree=inputs.worktree, remote=inputs.remote,
            remote_reachability_required=inputs.remote_reachability_required,
            reachability=inputs.reachability)),
        ("auth", lambda: probe_auth(
            executables=inputs.executables, auth_check=inputs.auth_check)),
        ("cli_capability_manifest", lambda: probe_cli_capability_manifest(
            journal=inputs.journal, executables=inputs.executables,
            record=inputs.record_identity, repin=inputs.repin_cli_identity,
            audit=inputs.audit)),
        ("pending_requests", lambda: probe_pending_requests(journal=inputs.journal)),
        ("scheduled_deadlines", lambda: probe_scheduled_deadlines(
            journal=inputs.journal, clock=inputs.clock)),
        ("last_external_effect", lambda: probe_last_external_effect(
            journal=inputs.journal)),
        ("config_identity", lambda: probe_config_identity(
            manifest_ok=inputs.manifest_ok, manifest_reason=inputs.manifest_reason,
            config_path=inputs.config_path)),
        ("surviving_children", lambda: probe_surviving_children(journal=inputs.journal)),
        # R295: the routing tooth reads the installed CLI version from
        # `installed_cli_version` (injected). It deliberately does NOT auto-launch
        # the executable here: `run_live_probes` runs on every start, and spawning
        # `claude --version` in the sweep would both add a launch to the hot path
        # and, in the golden fakes, increment their launch counters. A caller that
        # WANTS the version read from the binary supplies `routing_version_runner`
        # explicitly (with the executable path); by default the version is injected
        # and an absent version fails closed (folded, so it never gates dispatch by
        # itself - see FOLDED_PROBES and the start_gate fold note).
        ("shell_routing", lambda: probe_shell_routing_evidence(
            evidence_dir=inputs.routing_evidence_dir,
            installed_identity=inputs.installed_cli_identity,
            installed_version=inputs.installed_cli_version,
            executable_path=(inputs.executables.get("claude", "")
                             if inputs.routing_version_runner else ""),
            version_runner=inputs.routing_version_runner,
            journal=inputs.journal)),
    )
    return ProbeReport(results=tuple(_isolated(step, probe) for step, probe in probes))


#: Probes that ANSWER a `recovery.REVALIDATION_STEPS` entry directly.
STEP_PROBES: tuple[str, ...] = (
    "task_authority", "branch", "worktree", "git_and_remote_state", "auth",
    "cli_capability_manifest", "pending_requests", "scheduled_deadlines",
    "last_external_effect",
)

#: Probes the directive names that are FOLDED into an existing step rather than
#: widening the frozen step vocabulary. `config_identity` strengthens
#: `controller_manifest`; `surviving_children` reports what `recover_boot`'s own
#: child accounting already gates on; `shell_routing` (D-024-R295) strengthens the
#: pinned-CLI-identity story `cli_capability_manifest` tells - it appears in the
#: report so the refusal payload names it, and gating it into the revalidation map
#: is the one-line fold `start_gate.live_revalidation` already applies to
#: `config_identity` (start_gate.py is outside this unit's allowed paths; see the
#: producer report's integration finding).
FOLDED_PROBES: tuple[str, ...] = (
    "config_identity", "surviving_children", "shell_routing")


def default_worktree(repo_root: str, worktree: str = "") -> str:
    """The worktree a probe runs in: the named one, else the repository root."""
    return str(pathlib.Path(worktree or repo_root).resolve())


def named_executables(**paths: str | None) -> dict[str, str]:
    """Drop the executables the operator did not name; keep the rest verbatim."""
    return {name: os.fspath(path) for name, path in paths.items() if path}
