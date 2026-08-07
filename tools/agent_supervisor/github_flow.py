#!/usr/bin/env python3
"""Automatic ordinary GitHub flow, PROVEN in shadow/dry-run only (D-010 S5, S19.4).

Directed capability under the supervisor freeze's defect/directed-capability lane
(0A.8 item 8: "automatic ordinary commit, task-branch push, PR, CI, merge, and
ledger continuation"; AD-006/AD-007/AD-077). This module implements and lets the
harness PROVE the decision and orchestration logic for the ordinary GitHub flow
that D-010 Section 5 authorizes the supervisor to run WITHOUT an owner response:

* Tier A (S5.1): push to the exact non-default task branch, open/update a PR,
  merge an ordinary green PR, and delete the merged task branch;
* Tier B (S5.2): route workflow / dependency / supervisor-code changes to the
  named specialist reviews - and specifically NOT to an owner approval;
* Tier D (S5.4): force push, direct push to `main`, and a suspected secret
  leakage stay HARD-DENY - re-used from `push_policy`, never re-decided here;
* S5.5: the ten automatic-merge conditions, each an individually testable
  predicate with a machine-readable refusal reason;
* S19.4: the ten-item GitHub-automation proof list is the acceptance backbone.

**SHADOW-ONLY.** Nothing in this module performs a real push, PR, or merge. Every
external side effect goes through an INJECTED runner (`GitHubRunner`) and is
journaled through the S13.7 external-effect journal, so a crash mid-push or
mid-merge reconciles from durable evidence and is never blindly retried. The
tests supply fakes / fixture repos; no real remote is ever contacted, and this
module wires nothing into a live path (it does not lift the R595 activation gate).

Decision logic is deterministic and takes NO wall-clock input: every timestamp
that matters is journaled by the effect layer, not read inside a predicate.
"""
from __future__ import annotations

import dataclasses
import re
from typing import Any, Callable, Mapping, Protocol, Sequence

from .external_effects import (
    EffectSpec,
    ExternalEffectJournal,
    ReconciliationResult,
    stable_action_id,
)
from .models import EFFECT_CONFIRMED, EFFECT_PENDING, digest_of

#: SHADOW-SCOPED effect specs. `github_pr_merge` is DELIBERATELY not added to the
#: production `MODELED_EFFECTS` registry: that registry is the live-path authority
#: and D-007 invariant 9 keeps it free of any merge/deploy effect. The merge is
#: instead journaled and reconciled through an `ExternalEffectJournal` constructed
#: with these `extra_specs`, so the whole flow is PROVEN in shadow without wiring
#: a new automatic effect into the live path (0A.8 item 8; AD-077). A merge is
#: additive to `main` (a merge commit), never a delete/overwrite, so it is not
#: destructive; read-before-write records the base SHA so a crash mid-merge
#: reconciles against what `main` actually became.
SHADOW_EFFECT_SPECS: Mapping[str, EffectSpec] = {
    "github_pr_merge": EffectSpec(
        "github_pr_merge",
        "merge an ordinary green pull request into the protected default branch",
        read_before_write=True, destructive=False,
        compensating_action=("none automatic: a merged PR is not auto-reverted; a "
                             "revert is a new reviewed change, an owner-visible action")),
}


def shadow_effects_journal(journal: Any, **kwargs: Any) -> ExternalEffectJournal:
    """Build an effect journal that also knows the shadow merge spec.

    Convenience for the harness: the returned journal resolves `github_pr_merge`
    from `SHADOW_EFFECT_SPECS` while leaving the production registry untouched.
    """
    extra = dict(SHADOW_EFFECT_SPECS)
    extra.update(kwargs.pop("extra_specs", {}) or {})
    return ExternalEffectJournal(journal, extra_specs=extra, **kwargs)
from .policy import (
    CONTROLLER_PATHS,
    HARD_DENY,
    file_class,
    path_matches,
)
from .push_policy import PushEvaluation, PushPlan, evaluate_push

# --------------------------------------------------------------------------
# Tier B change-class routing (D-010 S5.2)
# --------------------------------------------------------------------------

#: The S5.2 table, keyed by the D-010 change-class label. The value is the tuple
#: of independent specialist reviews that must pass before the change may merge
#: automatically. Owner approval is deliberately absent from every row: S5.2 says
#: "these changes do not require an owner response merely because they are
#: important". `owner_approval_required` is therefore ALWAYS False here.
SPECIALIST_REVIEW_TABLE: Mapping[str, tuple[str, ...]] = {
    "dependencies_and_lockfiles": ("dependency-security", "ci"),
    "github_actions_and_ci": ("security", "control-plane"),
    "auth_session_code": ("security", "code", "integration"),
    "additive_database_migration": ("data-contract", "security", "rollback-test"),
    "contract_schema_addition": ("data-contract", "compatibility"),
    "official_source_connector": ("source-data-contract", "drift-fixture"),
    "legal_corpus_ingestion": ("security", "prompt-injection-data-contract"),
    "draft_rule_implementation": ("rules-code", "qa"),
    "scenario_calculation": ("data-contract", "qa"),
    "survey_pdf_parser": ("security", "deterministic-validation"),
    "supervisor_code": ("control-plane", "security", "crash-replay"),
}

#: Map a `policy.file_class` result to its D-010 S5.2 change-class label. Classes
#: that S5.2 does not enumerate (e.g. a bare `deploy_definition`, which is Tier D
#: territory handled by `push_policy`) are intentionally absent.
_FILE_CLASS_TO_CHANGE_CLASS: Mapping[str, str] = {
    "workflow": "github_actions_and_ci",
    "lockfile": "dependencies_and_lockfiles",
    "dependency_manifest": "dependencies_and_lockfiles",
}


class GitHubFlowError(Exception):
    """A github-flow input was malformed. Fail closed; never assume permissive."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def _is_supervisor_code(relative_posix: str) -> bool:
    """True when a path is part of the active controller (D-010 S5.2 supervisor code)."""
    text = relative_posix.replace("\\", "/")
    return any(path_matches(text, pattern) for pattern in CONTROLLER_PATHS)


def change_classes_for(paths: Sequence[str]) -> dict[str, tuple[str, ...]]:
    """The distinct D-010 S5.2 change classes a changed-path set falls into.

    Returns a mapping of change-class label -> the sorted paths that put it there.
    A supervisor-code path is recognized by controller-path match even though its
    `file_class` is ordinary; that is why this cannot be a pure `file_class` map.
    """
    found: dict[str, list[str]] = {}
    for raw in paths:
        rel = str(raw).replace("\\", "/")
        if _is_supervisor_code(rel):
            found.setdefault("supervisor_code", []).append(rel)
            continue
        label = _FILE_CLASS_TO_CHANGE_CLASS.get(file_class(rel))
        if label is not None:
            found.setdefault(label, []).append(rel)
    return {label: tuple(sorted(paths)) for label, paths in found.items()}


@dataclasses.dataclass(frozen=True)
class ReviewRouting:
    """The Tier decision for a changed-path set (D-010 S5.1/S5.2).

    `tier` is "A" when no change class needs a specialist review and "B" when at
    least one does. `owner_approval_required` is ALWAYS False: neither Tier A nor
    Tier B routes to the owner (S5.1 "the owner is not asked"; S5.2 "do not
    require an owner response merely because they are important").
    """

    tier: str
    change_classes: tuple[str, ...]
    required_reviews: tuple[str, ...]
    owner_approval_required: bool = False
    reason: str = ""

    def review_set(self) -> frozenset[str]:
        return frozenset(self.required_reviews)


def route_for_review(paths: Sequence[str]) -> ReviewRouting:
    """Route a changed-path set to its Tier and required specialist reviews.

    Never routes to owner approval. Workflow / dependency / supervisor-code
    classes each map to their S5.2 review tuple; a purely ordinary diff is Tier A
    with no required review.
    """
    classes = change_classes_for(paths)
    if not classes:
        return ReviewRouting(
            tier="A", change_classes=(), required_reviews=(),
            reason="all changed paths are ordinary product code/docs/tests (D-010 S5.1)")
    reviews: set[str] = set()
    for label in classes:
        reviews.update(SPECIALIST_REVIEW_TABLE.get(label, ()))
    return ReviewRouting(
        tier="B",
        change_classes=tuple(sorted(classes)),
        required_reviews=tuple(sorted(reviews)),
        owner_approval_required=False,
        reason=("change classes " + ", ".join(sorted(classes)) +
                " require independent specialist review (D-010 S5.2) but NOT owner "
                "approval"))


# --------------------------------------------------------------------------
# Push authorization (D-010 S5.1 Tier A allow / S5.4 Tier D hard-deny)
# --------------------------------------------------------------------------

PUSH_ALLOW = "ALLOW"
PUSH_HARD_DENY = "HARD_DENY"


@dataclasses.dataclass(frozen=True)
class PushAuthorization:
    """Whether the ordinary automatic flow may push (D-010 S5.1/S5.4).

    Derived from `push_policy.evaluate_push`, which stays the single authority for
    the deny logic. A push is ALLOWED under Tier A only when no S13.6 check
    HARD-DENIES it; force push, a direct push to a protected default branch, a
    remote-identity mismatch, and a suspected secret leakage are the HARD-DENY
    shapes and are surfaced verbatim.
    """

    decision: str
    reason_code: str
    reason: str
    evaluation: PushEvaluation

    @property
    def allowed(self) -> bool:
        return self.decision == PUSH_ALLOW


def authorize_push(plan: PushPlan) -> PushAuthorization:
    """Classify a proposed push as Tier A ALLOW or Tier D HARD-DENY.

    The Tier A posture of D-010 S5.1 makes an ordinary exact-task-branch push
    automatic (no owner grant needed), so the pre-limited-auto `authority` ASK in
    `push_policy` is not treated as a denial here. Any HARD-DENY check, however,
    is fatal and is reported with its own machine-readable reason code.
    """
    evaluation = evaluate_push(plan)
    hard = [c for c in evaluation.checks if c.tier == HARD_DENY]
    if hard:
        first = hard[0]
        return PushAuthorization(PUSH_HARD_DENY, first.reason_code, first.detail, evaluation)
    return PushAuthorization(
        PUSH_ALLOW, "task_branch_push_permitted",
        "the exact authorized non-default task branch may be pushed automatically "
        "(D-010 S5.1 Tier A)", evaluation)


# --------------------------------------------------------------------------
# Stale-remote-SHA detection and reconciliation (D-010 S19.4; no blind retry)
# --------------------------------------------------------------------------

REMOTE_CURRENT = "REMOTE_CURRENT"
REMOTE_RECONCILE = "REMOTE_RECONCILE"
REMOTE_BLOCK = "REMOTE_BLOCK"


@dataclasses.dataclass(frozen=True)
class RemoteReconciliation:
    """A stale-remote-SHA decision. Never a blind retry (D-010 S5.4 item 13/14)."""

    decision: str
    reason_code: str
    detail: str
    verified_head: str = ""

    @property
    def may_proceed(self) -> bool:
        return self.decision == REMOTE_CURRENT


def reconcile_remote_sha(
    *,
    expected_head: str,
    observed_head: str,
    remote_state_known: bool,
    refetch: Callable[[], tuple[bool, str]] | None = None,
) -> RemoteReconciliation:
    """Decide whether the remote base is current, must be re-fetched, or blocks.

    * heads agree and the remote is readable -> REMOTE_CURRENT (may proceed);
    * the remote head cannot be read -> REMOTE_BLOCK (proceeding would claim
      success from stale refs - refused, never guessed);
    * heads diverge -> re-fetch and re-verify through the injected `refetch`
      (which returns `(reconciled, verified_head)`); a divergence is NEVER retried
      blindly. Without a `refetch` the divergence blocks.
    """
    if not remote_state_known:
        return RemoteReconciliation(
            REMOTE_BLOCK, "remote_state_unknown",
            "the remote head could not be read; a merge may not claim currency from "
            "stale refs (D-010 S5.4 item 13)")
    if expected_head and observed_head and expected_head == observed_head:
        return RemoteReconciliation(
            REMOTE_CURRENT, "remote_head_current",
            "the expected and observed remote heads agree", observed_head)
    if refetch is None:
        return RemoteReconciliation(
            REMOTE_BLOCK, "stale_remote_sha",
            f"remote head {observed_head!r} != expected {expected_head!r}; re-fetch and "
            f"re-verify before any merge (no blind retry)")
    reconciled, verified = refetch()
    if reconciled:
        return RemoteReconciliation(
            REMOTE_CURRENT, "reconciled_after_refetch",
            f"re-fetched and re-verified against remote head {verified!r}", verified)
    return RemoteReconciliation(
        REMOTE_BLOCK, "stale_after_refetch",
        f"re-fetch did not reconcile the base (remote head {verified!r}); the merge is "
        f"blocked rather than retried blindly")


# --------------------------------------------------------------------------
# Automatic-merge eligibility - the ten S5.5 conditions
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class MergeRequest:
    """Everything the ten S5.5 predicates need. Facts come from the evidence
    collector / CI, never from a model's description of them."""

    task_id: str
    task_authorized: bool
    dependency_valid: bool
    changed_paths: tuple[str, ...]
    task_allowed_paths: tuple[str, ...]
    required_checks: Mapping[str, bool]
    secret_scan_findings: tuple[str, ...]
    completed_reviews: Mapping[str, bool]
    blocking_findings: tuple[str, ...]
    is_production_deploy: bool
    will_record_main_sha: bool
    task_state_transactional: bool
    expected_remote_head: str = ""
    observed_remote_head: str = ""
    remote_state_known: bool = True
    mergeable: bool = True


@dataclasses.dataclass(frozen=True)
class MergeCondition:
    """One named S5.5 predicate with its own machine-readable outcome."""

    name: str
    ok: bool
    reason_code: str
    detail: str


@dataclasses.dataclass(frozen=True)
class MergeEvaluation:
    """The combined S5.5 verdict. `eligible` is the AND of all ten conditions."""

    eligible: bool
    conditions: tuple[MergeCondition, ...]
    required_reviews: tuple[str, ...]

    def refusals(self) -> tuple[MergeCondition, ...]:
        return tuple(c for c in self.conditions if not c.ok)

    def refusal_codes(self) -> tuple[str, ...]:
        return tuple(c.reason_code for c in self.conditions if not c.ok)


def _cond(name: str, ok: bool, ok_code: str, ok_detail: str,
          fail_code: str, fail_detail: str) -> MergeCondition:
    return MergeCondition(name, ok,
                          ok_code if ok else fail_code,
                          ok_detail if ok else fail_detail)


def cond_authorized_and_dependency_valid(req: MergeRequest) -> MergeCondition:
    ok = bool(req.task_authorized) and bool(req.dependency_valid)
    return _cond("authorized_and_dependency_valid", ok,
                 "authorized_and_dependency_valid",
                 f"task {req.task_id!r} is authorized and dependency-valid",
                 "not_authorized_or_dependency_invalid",
                 f"task {req.task_id!r} is not authorized "
                 f"({req.task_authorized}) or not dependency-valid ({req.dependency_valid})")


def cond_changed_paths_fit_task(req: MergeRequest) -> MergeCondition:
    outside = [p for p in req.changed_paths
               if not any(path_matches(str(p).replace("\\", "/"), pat)
                          for pat in req.task_allowed_paths)]
    ok = not outside
    return _cond("changed_paths_fit_task", ok,
                 "changed_paths_fit_task",
                 "every changed path is within the task's allowed scope",
                 "changed_paths_outside_task",
                 f"changed paths outside the task scope: {sorted(outside)}")


def cond_branch_current(req: MergeRequest) -> MergeCondition:
    reconciliation = reconcile_remote_sha(
        expected_head=req.expected_remote_head,
        observed_head=req.observed_remote_head,
        remote_state_known=req.remote_state_known)
    ok = reconciliation.may_proceed and bool(req.mergeable)
    if not reconciliation.may_proceed:
        return MergeCondition("branch_current_enough", False,
                              reconciliation.reason_code, reconciliation.detail)
    return _cond("branch_current_enough", ok,
                 "branch_current_enough",
                 "the branch is current with its base and merges cleanly",
                 "branch_not_mergeable",
                 "the branch does not merge cleanly against its current base")


def cond_required_checks_pass(req: MergeRequest) -> MergeCondition:
    if not req.required_checks:
        return MergeCondition("required_checks_pass", False, "no_required_checks",
                              "no required check was reported; a merge may not proceed "
                              "without required tests and CI (D-010 S5.5)")
    failing = sorted(name for name, passed in req.required_checks.items() if not passed)
    ok = not failing
    return _cond("required_checks_pass", ok,
                 "required_checks_pass",
                 f"all {len(req.required_checks)} required checks passed",
                 "required_check_failing",
                 f"required checks not passing: {failing}")


def cond_secret_scan_clean(req: MergeRequest) -> MergeCondition:
    ok = not req.secret_scan_findings
    return _cond("secret_scan_clean", ok,
                 "secret_scan_clean", "the secret scan reported nothing",
                 "secret_finding", f"the secret scan reported {list(req.secret_scan_findings)}; "
                 f"a suspected secret leakage blocks the merge (D-010 S5.4 item 9)")


def cond_specialist_reviews_pass(req: MergeRequest) -> MergeCondition:
    routing = route_for_review(req.changed_paths)
    required = routing.required_reviews
    missing = sorted(name for name in required
                     if not bool(req.completed_reviews.get(name, False)))
    ok = not missing
    return _cond("specialist_reviews_pass", ok,
                 "specialist_reviews_pass",
                 f"required specialist reviews {list(required)} all passed"
                 if required else "no specialist review is required (Tier A)",
                 "specialist_review_missing",
                 f"required specialist reviews not passing: {missing}")


def cond_no_blocking_finding(req: MergeRequest) -> MergeCondition:
    ok = not req.blocking_findings
    return _cond("no_unresolved_blocking_finding", ok,
                 "no_unresolved_blocking_finding",
                 "no unresolved blocking finding exists",
                 "unresolved_blocking_finding",
                 f"unresolved blocking findings: {list(req.blocking_findings)}")


def cond_not_production_deploy(req: MergeRequest) -> MergeCondition:
    ok = not req.is_production_deploy
    return _cond("not_production_deploy", ok,
                 "not_production_deploy", "the merge is not a production deployment",
                 "production_deploy", "the merge is a production deployment; that is an "
                 "owner-gated Tier D action (D-010 S5.4 item 7)")


def cond_resulting_main_sha_recorded(req: MergeRequest) -> MergeCondition:
    ok = bool(req.will_record_main_sha)
    return _cond("resulting_main_sha_recorded", ok,
                 "resulting_main_sha_recorded",
                 "the flow records the resulting main SHA after the merge",
                 "resulting_main_sha_not_recorded",
                 "the resulting main SHA would not be recorded; the merge is refused")


def cond_task_state_transactional(req: MergeRequest) -> MergeCondition:
    ok = bool(req.task_state_transactional)
    return _cond("task_state_updated_transactionally", ok,
                 "task_state_updated_transactionally",
                 "the task state is updated transactionally with the merge record",
                 "task_state_not_transactional",
                 "the task-state update is not transactional; the merge is refused")


#: The ten S5.5 predicates, in the directive's order. Each is individually
#: testable and each has both an ok and a fail direction.
MERGE_CONDITIONS: tuple[Callable[[MergeRequest], MergeCondition], ...] = (
    cond_authorized_and_dependency_valid,
    cond_changed_paths_fit_task,
    cond_branch_current,
    cond_required_checks_pass,
    cond_secret_scan_clean,
    cond_specialist_reviews_pass,
    cond_no_blocking_finding,
    cond_not_production_deploy,
    cond_resulting_main_sha_recorded,
    cond_task_state_transactional,
)


def evaluate_merge(req: MergeRequest) -> MergeEvaluation:
    """Evaluate all ten S5.5 automatic-merge conditions.

    `eligible` is True only when EVERY condition holds. There is no owner-approval
    condition: an ordinary green PR merges without asking the owner (S5.1/S5.5).
    """
    conditions = tuple(predicate(req) for predicate in MERGE_CONDITIONS)
    routing = route_for_review(req.changed_paths)
    return MergeEvaluation(
        eligible=all(c.ok for c in conditions),
        conditions=conditions,
        required_reviews=routing.required_reviews)


# --------------------------------------------------------------------------
# Merged-branch cleanup safety (D-010 S5.4)
# --------------------------------------------------------------------------

#: Branch-name shapes that must NEVER be auto-deleted even if they look merged.
#: Evidence, audit-anchor, and control branches are retained unless their
#: identity and purpose are proven (D-010 S5.4 final paragraph).
_PROTECTED_DEFAULT_NAMES: frozenset[str] = frozenset({"main", "master", "head"})
_RETAINED_BRANCH_MARKERS: tuple[str, ...] = (
    "evidence", "audit", "anchor", "control", "release", "backup", "archive",
    "hotfix", "prod", "production",
)
_TASK_BRANCH_RE = re.compile(r"^task/[A-Za-z0-9][A-Za-z0-9._\-/]*$")

BRANCH_DELETE = "DELETE"
BRANCH_RETAIN = "RETAIN"


@dataclasses.dataclass(frozen=True)
class BranchCleanupDecision:
    """Whether a branch may be auto-deleted after merge (D-010 S5.4)."""

    decision: str
    reason_code: str
    detail: str

    @property
    def may_delete(self) -> bool:
        return self.decision == BRANCH_DELETE


def _classify_branch(name: str) -> str:
    text = name.strip().lower()
    if text in _PROTECTED_DEFAULT_NAMES:
        return "protected_default"
    # A retained marker wins over the `/main` suffix so `backup/main` is kept as
    # an unusual branch, not misread as a protected default.
    if any(marker in text for marker in _RETAINED_BRANCH_MARKERS):
        return "retained"
    if text.endswith("/main") or text.endswith("/master"):
        return "protected_default"
    if _TASK_BRANCH_RE.match(name.strip()):
        return "task"
    return "unknown"


def evaluate_branch_cleanup(
    *,
    branch: str,
    merged_into_main: bool,
    is_current_worktree_branch: bool = False,
) -> BranchCleanupDecision:
    """Decide whether a branch may be safely auto-deleted.

    Deletes ONLY a proven-merged `task/...` branch. A protected default branch, an
    evidence/audit/anchor/control/unusual branch, an unmerged branch, or the
    branch currently checked out in the worktree is RETAINED. "Proven merged" is
    supplied by the caller from real ancestry evidence (the harness's git fixture
    proves it); this function never assumes a branch is merged.
    """
    kind = _classify_branch(branch)
    if kind == "protected_default":
        return BranchCleanupDecision(BRANCH_RETAIN, "protected_default_branch",
                                     f"{branch!r} is a protected default branch; never deleted")
    if kind == "retained":
        return BranchCleanupDecision(
            BRANCH_RETAIN, "unusual_or_evidence_branch",
            f"{branch!r} is an evidence/audit/anchor/control/unusual branch; retained "
            f"unless its identity and purpose are proven (D-010 S5.4)")
    if kind == "unknown":
        return BranchCleanupDecision(
            BRANCH_RETAIN, "unrecognized_branch_shape",
            f"{branch!r} is not a recognized task branch; retained rather than deleted")
    if is_current_worktree_branch:
        return BranchCleanupDecision(BRANCH_RETAIN, "current_worktree_branch",
                                     f"{branch!r} is the checked-out worktree branch; retained")
    if not merged_into_main:
        return BranchCleanupDecision(
            BRANCH_RETAIN, "not_proven_merged",
            f"{branch!r} is not proven merged into main; an unmerged branch is never "
            f"auto-deleted (D-010 S5.4)")
    return BranchCleanupDecision(BRANCH_DELETE, "merged_task_branch",
                                 f"{branch!r} is a proven-merged task branch; safe to delete")


# --------------------------------------------------------------------------
# Injected runner boundary + orchestration (SHADOW-ONLY)
# --------------------------------------------------------------------------


class GitHubRunner(Protocol):
    """The injected boundary every real side effect crosses. Tests pass a fake.

    A production implementation would perform the git/gh call; the supervisor
    holds it behind this Protocol so no decision code in this module ever touches
    a network client, and so a dry-run harness proves the whole flow.
    """

    def push_task_branch(self, plan: PushPlan) -> str: ...

    def create_pull_request(self, *, task_id: str, head: str, base: str,
                            title: str) -> str: ...

    def merge_pull_request(self, *, pr_ref: str, base_sha: str) -> str: ...

    def delete_branch(self, branch: str) -> None: ...


def _request_digest(payload: Mapping[str, Any]) -> str:
    return digest_of(payload)


@dataclasses.dataclass(frozen=True)
class FlowResult:
    """The outcome of one orchestrated step (push / PR / merge)."""

    performed: bool
    action_id: str
    resulting_state: str
    reason_code: str
    detail: str


class GitHubFlow:
    """Orchestrate the ordinary flow through the effect journal + injected runner.

    Every external write is journaled BEFORE it is attempted (idempotency key from
    the effect content) and confirmed only AFTER the runner verifies it. A crash
    between the before-record and the confirm leaves a PENDING effect that
    `reconcile()` proves or refutes from read-only evidence - it is never blindly
    re-fired (D-010 S5.4 item 13; S19.4 crash-reconciliation proof).
    """

    def __init__(self, effects: ExternalEffectJournal, runner: GitHubRunner, *,
                 task_id: str) -> None:
        self.effects = effects
        self.runner = runner
        self.task_id = task_id

    # -- idempotency / no-blind-retry guard ---------------------------------

    def _guard(self, action_id: str) -> tuple[str, Any]:
        """Classify an effect key before re-firing it.

        Returns one of:

        * ``("proceed", None)`` - no journal record: first attempt, run it;
        * ``("confirmed", record)`` - already CONFIRMED: return the recorded
          result idempotently and DO NOT perform the effect again (no duplicate);
        * ``("pending", record)`` - a PENDING record survived a crash: the effect
          MAY have occurred, so it is reconciled, never blindly re-fired.
        """
        existing = self.effects.journal.get_effect(action_id)
        if existing is None:
            return "proceed", None
        if existing.status == EFFECT_CONFIRMED:
            return "confirmed", existing
        if existing.status == EFFECT_PENDING:
            return "pending", existing
        return "proceed", existing  # a proven-FAILED record is safe to retry

    # -- push ---------------------------------------------------------------

    def push(self, plan: PushPlan) -> FlowResult:
        """Authorize then journal-and-perform a task-branch push (Tier A / D)."""
        auth = authorize_push(plan)
        if not auth.allowed:
            return FlowResult(False, "", "", auth.reason_code, auth.reason)
        digest = _request_digest({"branch": plan.branch, "head": plan.local_head})
        action_id = stable_action_id(
            effect_type="git_push_task_branch",
            target=f"{plan.remote_name}/{plan.branch}", task_id=self.task_id,
            request_digest=digest)
        phase, existing = self._guard(action_id)
        if phase == "confirmed":
            return FlowResult(False, action_id, existing.resulting_state,
                              "already_pushed", "the push is already CONFIRMED; not repeated")
        if phase == "pending":
            return FlowResult(False, action_id, "", "pending_effect_reconcile_first",
                              "a PENDING push survived a crash; reconcile it before any retry")
        record = self.effects.begin(
            effect_type="git_push_task_branch",
            target=f"{plan.remote_name}/{plan.branch}", task_id=self.task_id,
            request_digest=digest,
            prior_state_reader=lambda: plan.observed_remote_head or plan.expected_remote_head)
        resulting = self.runner.push_task_branch(plan)
        self.effects.confirm(record.action_id, resulting_state=resulting)
        return FlowResult(True, record.action_id, resulting, "pushed",
                          "task-branch push journaled and confirmed")

    # -- pull request -------------------------------------------------------

    def create_pull_request(self, *, head: str, base: str, title: str) -> FlowResult:
        """Journal-and-create the task PR (never merges it here)."""
        digest = _request_digest({"head": head, "base": base, "title": title})
        action_id = stable_action_id(
            effect_type="github_pr_create", target=f"{base}<-{head}",
            task_id=self.task_id, request_digest=digest)
        phase, existing = self._guard(action_id)
        if phase == "confirmed":
            return FlowResult(False, action_id, existing.resulting_state,
                              "already_created", "the PR is already CONFIRMED; not repeated")
        if phase == "pending":
            return FlowResult(False, action_id, "", "pending_effect_reconcile_first",
                              "a PENDING PR-create survived a crash; reconcile before retry")
        record = self.effects.begin(
            effect_type="github_pr_create",
            target=f"{base}<-{head}", task_id=self.task_id, request_digest=digest,
            prior_state_reader=lambda: "no_pr")
        pr_ref = self.runner.create_pull_request(
            task_id=self.task_id, head=head, base=base, title=title)
        self.effects.confirm(record.action_id, resulting_state=pr_ref)
        return FlowResult(True, record.action_id, pr_ref, "pr_created",
                          "pull request journaled and created")

    # -- merge --------------------------------------------------------------

    def merge(self, req: MergeRequest, *, pr_ref: str, base_sha: str) -> FlowResult:
        """Evaluate S5.5 then journal-and-perform an ordinary green-PR merge.

        Refuses BEFORE any effect is journaled when the merge is not eligible, so
        an ineligible merge leaves no external trace at all. A crash-surviving
        PENDING merge is reconciled, never blindly re-fired; a CONFIRMED merge is
        reported idempotently without a second merge.
        """
        evaluation = evaluate_merge(req)
        if not evaluation.eligible:
            codes = ", ".join(evaluation.refusal_codes())
            return FlowResult(False, "", "", "merge_ineligible",
                              f"automatic merge refused: {codes}")
        action_id = self.merge_action_id(pr_ref=pr_ref, base_sha=base_sha)
        phase, existing = self._guard(action_id)
        if phase == "confirmed":
            return FlowResult(False, action_id, existing.resulting_state,
                              "already_merged", "the merge is already CONFIRMED; not repeated")
        if phase == "pending":
            return FlowResult(False, action_id, "", "pending_effect_reconcile_first",
                              "a PENDING merge survived a crash; reconcile it before any retry")
        digest = _request_digest({"pr_ref": pr_ref, "base_sha": base_sha,
                                  "task_id": self.task_id})
        record = self.effects.begin(
            effect_type="github_pr_merge",
            target=pr_ref, task_id=self.task_id, request_digest=digest,
            prior_state_reader=lambda: base_sha)
        resulting_sha = self.runner.merge_pull_request(pr_ref=pr_ref, base_sha=base_sha)
        self.effects.confirm(record.action_id, resulting_state=resulting_sha)
        return FlowResult(True, record.action_id, resulting_sha, "merged",
                          "ordinary green PR merged; resulting main SHA recorded")

    def merge_action_id(self, *, pr_ref: str, base_sha: str) -> str:
        """The idempotency key a merge WOULD use - for crash reconciliation."""
        digest = _request_digest({"pr_ref": pr_ref, "base_sha": base_sha,
                                  "task_id": self.task_id})
        return stable_action_id(effect_type="github_pr_merge", target=pr_ref,
                                task_id=self.task_id, request_digest=digest)

    # -- cleanup ------------------------------------------------------------

    def cleanup_branch(self, *, branch: str, merged_into_main: bool,
                       is_current_worktree_branch: bool = False) -> FlowResult:
        """Delete a branch ONLY when `evaluate_branch_cleanup` proves it safe."""
        decision = evaluate_branch_cleanup(
            branch=branch, merged_into_main=merged_into_main,
            is_current_worktree_branch=is_current_worktree_branch)
        if not decision.may_delete:
            return FlowResult(False, "", "", decision.reason_code, decision.detail)
        self.runner.delete_branch(branch)
        return FlowResult(True, "", "", decision.reason_code, decision.detail)

    # -- crash reconciliation ----------------------------------------------

    def reconcile(self, action_id: str,
                  prober: Callable[[Any], tuple[bool | None, str]]) -> ReconciliationResult:
        """Prove a pending effect's fate from read-only evidence (no blind retry)."""
        return self.effects.reconcile(action_id, prober)
