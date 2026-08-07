#!/usr/bin/env python3
"""The approval broker (D-007 S8.4, S13.5, S13.10).

The broker is the four-tier policy applied to a concrete request, plus the
bookkeeping that makes an approval safe:

    1. HARD-DENY (S4.4)        final; no model can override
    2. AUTO (S4.1, + grants)   approve THIS EXACT CALL once
    3. Codex advisory          only for pre-marked advisory-eligible categories,
                               never security-sensitive, never an external write
    4. ASK (S4.3)              everything else queues for the owner

Properties this module exists to guarantee:

* **Every approval is digest-bound** to the full S13.5 binding: tool name and
  complete input, executable identity, argv, the approved environment subset,
  canonical cwd, canonical target paths AND their file identities, task/stage,
  branch/worktree, HEAD and origin/main, policy and controller version,
  permission mode, and the request id. `verify_before_execute()` recomputes the
  binding immediately before execution; ANY difference invalidates it.
* **Nothing hangs.** `handle_unhandled()` denies. A request that cannot reach the
  broker is denied by construction (the CLI fails closed at EOF - verified in
  the Phase 1 probes).
* **A deferred request preserves the exact pending call and session id**, and
  resumption revalidates both the request and the repository state.
* **"Always allow" is never selected and no settings file is ever written.**
  `permission_suggestions` arriving from the CLI (the Phase 1 probe recorded
  `{"type":"setMode","mode":"acceptEdits"}`) are recorded as REJECTED, never
  applied. This module contains no file-write path for settings at all.

Claude's stated reason travels with the request for the audit record and is
deliberately EXCLUDED from the binding digest: it is untrusted text, and neither
rewording it nor changing it may affect an approval either way.
"""
from __future__ import annotations

import dataclasses
import uuid
from typing import Any, Callable, Mapping, Sequence

from . import CONTROLLER_VERSION
from .models import QueuedAsk, digest_of, to_utc_iso
from .policy import (
    ASK,
    AUTO,
    DEFAULT_POLICY_CONFIG,
    DENY_AND_HALT,
    HARD_DENY,
    POLICY_VERSION,
    PolicyConfig,
    PolicyDecision,
    ProposedAction,
    TaskAuthority,
    evaluate,
    file_identity,
    neutralize_untrusted,
    resolve_target,
)

APPROVE_ONCE = "APPROVE_ONCE"
DENY = "DENY"
DEFER_TO_OWNER = "DEFER_TO_OWNER"
ROUTE_TO_ASK = "ROUTE_TO_ASK"

BEHAVIORS: tuple[str, ...] = (APPROVE_ONCE, DENY, DEFER_TO_OWNER)

#: Journal key prefix for approval records.
APPROVAL_PREFIX = "approval/"

STATUS_PENDING = "PENDING_OWNER"
STATUS_APPROVED = "APPROVED_ONCE"
STATUS_DENIED = "DENIED"
STATUS_CONSUMED = "CONSUMED"
STATUS_REVOKED = "REVOKED"
STATUS_INVALIDATED = "INVALIDATED"


class BrokerError(Exception):
    """A broker input was malformed. Fail closed."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


# --------------------------------------------------------------------------
# The request and its S13.5 binding
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ApprovalRequest:
    """One tool request, carrying everything S8.4 says it must carry."""

    request_id: str
    tool_name: str
    tool_input: Mapping[str, Any] = dataclasses.field(default_factory=dict)
    argv: tuple[str, ...] = ()
    executable_identity: Mapping[str, Any] = dataclasses.field(default_factory=dict)
    env_names: tuple[str, ...] = ()
    env_values_digest: str = ""
    cwd: str = ""
    target_paths: tuple[str, ...] = ()
    file_identities: Mapping[str, str] = dataclasses.field(default_factory=dict)
    task_id: str = ""
    stage: str = ""
    branch: str = ""
    worktree: str = ""
    head_sha: str = ""
    origin_main_sha: str = ""
    permission_mode: str = "manual"
    session_id: str = ""
    tool_use_id: str = ""
    permission_suggestions: tuple[Mapping[str, Any], ...] = ()
    stated_reason: str = ""
    created_at_utc: str = ""
    policy_version: str = POLICY_VERSION
    controller_version: str = CONTROLLER_VERSION

    def binding(self) -> dict[str, Any]:
        """The exact S13.5 binding. `stated_reason` is deliberately absent."""
        return {
            "request_id": self.request_id,
            "tool_name": self.tool_name,
            "tool_input": dict(self.tool_input),
            "argv": list(self.argv),
            "executable_identity": dict(self.executable_identity),
            "env_subset": {"names": sorted(self.env_names),
                           "values_digest": self.env_values_digest},
            "cwd": self.cwd,
            "target_paths": list(self.target_paths),
            "file_identities": dict(self.file_identities),
            "task_id": self.task_id,
            "stage": self.stage,
            "branch": self.branch,
            "worktree": self.worktree,
            "head_sha": self.head_sha,
            "origin_main_sha": self.origin_main_sha,
            "policy_version": self.policy_version,
            "controller_version": self.controller_version,
            "permission_mode": self.permission_mode,
        }

    def digest(self) -> str:
        return digest_of(self.binding())

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        data["argv"] = list(self.argv)
        data["target_paths"] = list(self.target_paths)
        data["permission_suggestions"] = [dict(s) for s in self.permission_suggestions]
        return data

    def refreshed(self, *, head_sha: str | None = None,
                  origin_main_sha: str | None = None) -> "ApprovalRequest":
        """Re-stat every target path and optionally update the repository facts.

        Used immediately before execution: a file replaced, hard-linked, or
        re-created between approval and execution changes its identity, and the
        recomputed digest therefore stops matching (S13.5).
        """
        identities = {path: file_identity(self._absolute(path))
                      for path in self.target_paths}
        return dataclasses.replace(
            self,
            file_identities=identities,
            head_sha=self.head_sha if head_sha is None else head_sha,
            origin_main_sha=(self.origin_main_sha if origin_main_sha is None
                             else origin_main_sha))

    def _absolute(self, path: str) -> str:
        root = self.worktree or self.cwd or "."
        resolved = resolve_target(path, root)
        return resolved.canonical or path


def build_request(
    *,
    tool_name: str,
    tool_input: Mapping[str, Any] | None = None,
    authority: TaskAuthority,
    argv: Sequence[str] = (),
    executable_identity: Mapping[str, Any] | None = None,
    env: Mapping[str, str] | None = None,
    cwd: str = "",
    target_paths: Sequence[str] = (),
    head_sha: str = "",
    origin_main_sha: str = "",
    session_id: str = "",
    tool_use_id: str = "",
    permission_suggestions: Sequence[Mapping[str, Any]] = (),
    stated_reason: str = "",
    permission_mode: str = "manual",
    request_id: str = "",
) -> ApprovalRequest:
    """Assemble a fully bound request. Environment VALUES are never stored."""
    environment = dict(env or {})
    canonical_targets: list[str] = []
    identities: dict[str, str] = {}
    root = authority.worktree or authority.repo_root
    for path in target_paths:
        resolved = resolve_target(path, root)
        canonical = resolved.canonical or path
        canonical_targets.append(canonical)
        identities[canonical] = resolved.file_identity or file_identity(canonical)
    return ApprovalRequest(
        request_id=request_id or f"req_{uuid.uuid4().hex}",
        tool_name=tool_name,
        tool_input=dict(tool_input or {}),
        argv=tuple(str(a) for a in argv),
        executable_identity=dict(executable_identity or {}),
        env_names=tuple(sorted(environment)),
        env_values_digest=digest_of({k: environment[k] for k in sorted(environment)}),
        cwd=cwd or root,
        target_paths=tuple(canonical_targets),
        file_identities=identities,
        task_id=authority.task_id,
        stage=authority.stage,
        branch=authority.branch,
        worktree=authority.worktree,
        head_sha=head_sha,
        origin_main_sha=origin_main_sha,
        permission_mode=permission_mode,
        session_id=session_id,
        tool_use_id=tool_use_id,
        permission_suggestions=tuple(dict(s) for s in permission_suggestions),
        stated_reason=stated_reason,
        created_at_utc=to_utc_iso(),
    )


# --------------------------------------------------------------------------
# Outcomes
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class BrokerOutcome:
    """A schema-valid outcome bound to the exact request digest (S8.4)."""

    behavior: str
    request_id: str
    request_digest: str
    tier: str
    reason_code: str
    reason: str
    ask_id: str = ""
    outcome: str = ""
    synchronous_stop: bool = False
    advisory_used: str = ""
    matched_grant: str = ""
    rejected_suggestions: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @property
    def allowed(self) -> bool:
        return self.behavior == APPROVE_ONCE


@dataclasses.dataclass(frozen=True)
class AdvisoryRecommendation:
    """A fresh read-only Codex advisory. Valid only inside its marked category."""

    recommendation: str
    category: str
    model_used: str
    reason: str = ""


AdvisoryCallback = Callable[[ApprovalRequest, str], AdvisoryRecommendation]


# --------------------------------------------------------------------------
# The broker
# --------------------------------------------------------------------------

#: Categories that may EVER be resolved by a Codex advisory. Security-sensitive
#: requests and anything touching an external write are excluded by S8.4.
ADVISORY_CATEGORY_FOR_KIND: Mapping[str, str] = {
    "read": "read_only_inspection",
    "command": "documented_test_command",
    "git_command": "read_only_inspection",
    "file_write": "in_scope_file_edit",
}

NEVER_ADVISORY_KINDS: frozenset[str] = frozenset({
    "external_write", "push", "pr_mutation", "file_delete", "file_rename",
    "subagent", "network",
})

#: Suggestion types the CLI may offer that amount to "always allow". Recorded and
#: refused; never applied (S8.4).
FORBIDDEN_SUGGESTION_TYPES: frozenset[str] = frozenset({
    "setMode", "addRules", "alwaysAllow", "always_allow", "acceptEdits",
    "updatePermissions", "bypassPermissions",
})


class ApprovalBroker:
    """Evaluates, records, and revalidates approvals. Never executes anything."""

    def __init__(
        self,
        journal: Any,
        audit: Any,
        *,
        authority: TaskAuthority,
        mode: str = "shadow",
        config: PolicyConfig = DEFAULT_POLICY_CONFIG,
        advisory: AdvisoryCallback | None = None,
        breakers: Any = None,
        run_id: str = "",
    ) -> None:
        self.journal = journal
        self.audit = audit
        self.authority = authority
        self.mode = mode
        self.config = config
        self.advisory = advisory
        self.breakers = breakers
        self.run_id = run_id

    # -- persistence --------------------------------------------------------

    def _key(self, request_id: str) -> str:
        return APPROVAL_PREFIX + request_id

    def _store(self, request: ApprovalRequest, status: str, outcome: BrokerOutcome,
               decision: PolicyDecision | None = None) -> None:
        untrusted = neutralize_untrusted(request.stated_reason)
        self.journal.set_state(self._key(request.request_id), {
            "status": status,
            "request": request.to_dict(),
            "request_digest": outcome.request_digest,
            "outcome": outcome.to_dict(),
            "policy": decision.to_dict() if decision is not None else {},
            "session_id": request.session_id,
            "untrusted_reason_labels": list(untrusted.labels),
            "updated_at_utc": to_utc_iso(),
        })

    def record(self, request_id: str) -> dict[str, Any] | None:
        return self.journal.get_state(self._key(request_id))

    def pending(self) -> list[dict[str, Any]]:
        """Every request still awaiting the owner, oldest first."""
        out = [record for key, record in self.journal.all_state().items()
               if key.startswith(APPROVAL_PREFIX)
               and isinstance(record, dict)
               and record.get("status") == STATUS_PENDING]
        return sorted(out, key=lambda r: r.get("updated_at_utc", ""))

    # -- audit --------------------------------------------------------------

    def _audit(self, event: str, request: ApprovalRequest, outcome: BrokerOutcome,
               decision: PolicyDecision | None = None) -> None:
        if self.audit is None:
            return
        self.audit.append(
            event,
            run_id=self.run_id,
            decision=outcome.behavior,
            policy_result=f"{outcome.tier}:{outcome.reason_code}",
            input_digest=outcome.request_digest,
            detail={
                "request_id": request.request_id,
                "tool_name": request.tool_name,
                "task_id": request.task_id,
                "branch": request.branch,
                "target_paths": list(request.target_paths),
                "tier": outcome.tier,
                "outcome": outcome.outcome,
                "reason": outcome.reason,
                "rejected_suggestions": list(outcome.rejected_suggestions),
                "advisory_used": outcome.advisory_used,
                "matched_grant": outcome.matched_grant,
                "policy_rule": decision.rule_id if decision else "",
            })

    # -- suggestion handling ------------------------------------------------

    def reject_permission_suggestions(
            self, request: ApprovalRequest) -> tuple[str, ...]:
        """Record every offered suggestion as REFUSED. None is ever applied.

        The Phase 1 probe observed the CLI offering
        `{"type":"setMode","mode":"acceptEdits","destination":"session"}`. That is
        exactly the "always allow" S8.4 forbids. The broker names it and moves on.
        """
        rejected: list[str] = []
        for suggestion in request.permission_suggestions:
            label = str(suggestion.get("type", "unknown"))
            mode = suggestion.get("mode")
            rejected.append(f"{label}:{mode}" if mode else label)
        return tuple(rejected)

    # -- evaluation ---------------------------------------------------------

    def evaluate_request(
        self,
        request: ApprovalRequest,
        action: ProposedAction,
        *,
        review_passed: bool = False,
    ) -> BrokerOutcome:
        """Apply the S8.4 order and persist the result. Never returns None."""
        digest = request.digest()
        rejected = self.reject_permission_suggestions(request)

        decision = evaluate(action, authority=self.authority, mode=self.mode,
                            config=self.config, review_passed=review_passed)

        # 1. HARD-DENY is final.
        if decision.tier == HARD_DENY:
            outcome = BrokerOutcome(
                DENY, request.request_id, digest, HARD_DENY, decision.reason_code,
                decision.reason, outcome=decision.outcome,
                synchronous_stop=decision.outcome == DENY_AND_HALT,
                rejected_suggestions=rejected)
            self._store(request, STATUS_DENIED, outcome, decision)
            self._audit("approval_hard_denied", request, outcome, decision)
            if self.breakers is not None:
                self.breakers.record("consecutive_hard_denies")
            return outcome

        # 2. AUTO, including owner standing grants.
        if decision.tier == AUTO:
            outcome = BrokerOutcome(
                APPROVE_ONCE, request.request_id, digest, AUTO, decision.reason_code,
                decision.reason, matched_grant=decision.matched_grant,
                rejected_suggestions=rejected)
            self._store(request, STATUS_APPROVED, outcome, decision)
            self._audit("approval_auto", request, outcome, decision)
            return outcome

        # 3. Codex advisory - only inside a pre-marked, non-security category.
        category = self._advisory_category(action, decision)
        if category and self.advisory is not None:
            advised = self._consult_advisory(request, category)
            if advised is not None:
                if advised.recommendation == APPROVE_ONCE:
                    outcome = BrokerOutcome(
                        APPROVE_ONCE, request.request_id, digest, AUTO,
                        "codex_advisory_approve_once",
                        f"advisory {advised.model_used} approved this exact call inside the "
                        f"pre-marked category {category!r}; advisory approval can never "
                        f"reach outside that category",
                        advisory_used=advised.model_used,
                        rejected_suggestions=rejected)
                    self._store(request, STATUS_APPROVED, outcome, decision)
                    self._audit("approval_advisory", request, outcome, decision)
                    return outcome
                if advised.recommendation == DENY:
                    outcome = BrokerOutcome(
                        DENY, request.request_id, digest, ASK, "codex_advisory_deny",
                        f"advisory {advised.model_used} denied: {advised.reason}",
                        advisory_used=advised.model_used,
                        rejected_suggestions=rejected)
                    self._store(request, STATUS_DENIED, outcome, decision)
                    self._audit("approval_advisory_deny", request, outcome, decision)
                    return outcome

        # 4. ASK - queue for the owner; never hang, never guess.
        return self.defer(request, decision, rejected=rejected)

    def _advisory_category(self, action: ProposedAction,
                           decision: PolicyDecision) -> str:
        """The pre-marked advisory category, or '' when advisory is not allowed."""
        if decision.tier != ASK:
            return ""
        if action.kind in NEVER_ADVISORY_KINDS:
            return ""
        if decision.classification != "unclassified":
            # Security, scope, dependency, architecture, owner-gate, destructive and
            # legal ASKs are never advisory-eligible.
            return ""
        category = action.category or ADVISORY_CATEGORY_FOR_KIND.get(action.kind, "")
        if category not in self.config.advisory_eligible_categories:
            return ""
        return category

    def _consult_advisory(self, request: ApprovalRequest,
                          category: str) -> AdvisoryRecommendation | None:
        assert self.advisory is not None
        try:
            advised = self.advisory(request, category)
        except Exception as exc:  # pragma: no cover - defensive
            if self.audit is not None:
                self.audit.append("advisory_failed", run_id=self.run_id,
                                  error_category="advisory_error",
                                  detail={"request_id": request.request_id,
                                          "error": str(exc)})
            return None
        if not isinstance(advised, AdvisoryRecommendation):
            return None
        if advised.recommendation not in (APPROVE_ONCE, DENY, ROUTE_TO_ASK):
            return None
        if advised.category != category:
            # An advisory approval outside the pre-marked category is void.
            if self.audit is not None:
                self.audit.append(
                    "advisory_out_of_category", run_id=self.run_id,
                    error_category="advisory_scope",
                    detail={"request_id": request.request_id,
                            "marked_category": category,
                            "returned_category": advised.category})
            return None
        return advised

    def defer(self, request: ApprovalRequest, decision: PolicyDecision,
              *, rejected: Sequence[str] = ()) -> BrokerOutcome:
        """Queue an ASK, preserving the exact pending call and session id."""
        digest = request.digest()
        ask_id = f"ask_{request.request_id}"
        outcome = BrokerOutcome(
            DEFER_TO_OWNER, request.request_id, digest, decision.tier,
            decision.reason_code, decision.reason, ask_id=ask_id,
            synchronous_stop=decision.synchronous_stop,
            rejected_suggestions=tuple(rejected),
            notes=decision.notes)
        self._store(request, STATUS_PENDING, outcome, decision)
        try:
            self.journal.queue_ask(QueuedAsk(
                ask_id=ask_id, run_id=self.run_id, task_id=request.task_id,
                question=(f"Approve {request.tool_name} for task {request.task_id}? "
                          f"{decision.reason}"),
                request_digest=digest, created_at_utc=to_utc_iso(),
                classification=decision.classification or "unclassified"))
        except Exception:
            # A duplicate ask id means the same request is already queued; the
            # queue is idempotent, and losing the second insert is correct.
            pass
        self._audit("approval_deferred", request, outcome, decision)
        return outcome

    # -- non-interactive safety --------------------------------------------

    def handle_unhandled(self, request: ApprovalRequest,
                         reason: str = "") -> BrokerOutcome:
        """A request that reached no decision path. DENY - never hang (S8.4)."""
        digest = request.digest()
        outcome = BrokerOutcome(
            DENY, request.request_id, digest, HARD_DENY, "unhandled_request",
            reason or ("an unhandled request in non-interactive operation is denied; it "
                       "never hangs and is never silently allowed"),
            outcome="DENY_AND_CONTINUE")
        self._store(request, STATUS_DENIED, outcome)
        self._audit("approval_unhandled_denied", request, outcome)
        return outcome

    # -- TOCTOU revalidation ------------------------------------------------

    def verify_before_execute(self, request: ApprovalRequest) -> BrokerOutcome:
        """Recompute the binding immediately before execution (S13.5).

        Any difference in the command, arguments, paths, file identities, task,
        branch, worktree, repository state, policy version, or permission mode
        invalidates the approval.
        """
        record = self.record(request.request_id)
        if record is None:
            return self.handle_unhandled(
                request, "no approval record exists for this request id")
        status = record.get("status")
        if status == STATUS_CONSUMED:
            return BrokerOutcome(
                DENY, request.request_id, request.digest(), HARD_DENY,
                "approval_already_consumed",
                "an approve-once decision is consumed by its single execution",
                outcome="DENY_AND_CONTINUE")
        if status == STATUS_REVOKED:
            return BrokerOutcome(
                DENY, request.request_id, request.digest(), HARD_DENY,
                "approval_revoked", "this approval was revoked",
                outcome="DENY_AND_CONTINUE")
        if status != STATUS_APPROVED:
            return BrokerOutcome(
                DENY, request.request_id, request.digest(), ASK,
                "approval_not_granted",
                f"the request is {status}, not {STATUS_APPROVED}")

        current = request.refreshed()
        recomputed = current.digest()
        stored = str(record.get("request_digest", ""))
        if recomputed != stored:
            outcome = BrokerOutcome(
                DENY, request.request_id, recomputed, HARD_DENY,
                "digest_changed_before_execution",
                "the request or the repository state changed after approval; no approval "
                "survives a changed request or changed repository/policy state (inv. 6)",
                outcome="DENY_AND_CONTINUE")
            self._store(current, STATUS_INVALIDATED, outcome)
            self._audit("approval_invalidated", current, outcome)
            return outcome

        outcome = BrokerOutcome(
            APPROVE_ONCE, request.request_id, recomputed, AUTO,
            "revalidated", "the binding still matches exactly; approved for this one "
                           "execution")
        self._store(current, STATUS_CONSUMED, outcome)
        self._audit("approval_consumed", current, outcome)
        return outcome

    # -- owner answers ------------------------------------------------------

    def approve_once(self, request_id: str, displayed_digest: str) -> BrokerOutcome:
        """The owner's local `approve-once <request-id> <displayed-digest>`.

        The digest the owner saw must match the stored digest EXACTLY. A partial
        or stale digest is refused rather than guessed at.
        """
        record = self.record(request_id)
        if record is None:
            raise BrokerError("unknown_request", f"no pending request {request_id!r}")
        stored = str(record.get("request_digest", ""))
        if displayed_digest != stored:
            outcome = BrokerOutcome(
                DENY, request_id, stored, HARD_DENY, "digest_mismatch",
                "the displayed digest does not match the stored request binding; the "
                "answer is refused rather than guessed at")
            self._audit_record_only("approval_digest_mismatch", request_id, outcome)
            return outcome
        if record.get("status") != STATUS_PENDING:
            return BrokerOutcome(
                DENY, request_id, stored, ASK, "not_pending",
                f"request {request_id} is {record.get('status')}, not pending")
        outcome = BrokerOutcome(
            APPROVE_ONCE, request_id, stored, AUTO, "owner_approved_once",
            "the owner approved this exact call once; it is bound to the digest above "
            "and is revalidated immediately before execution")
        record["status"] = STATUS_APPROVED
        record["outcome"] = outcome.to_dict()
        record["answered_at_utc"] = to_utc_iso()
        self.journal.set_state(self._key(request_id), record)
        self._audit_record_only("approval_owner_approved", request_id, outcome)
        return outcome

    def deny_request(self, request_id: str, displayed_digest: str,
                     reason: str = "") -> BrokerOutcome:
        """The owner's local `deny <request-id> <displayed-digest>`."""
        record = self.record(request_id)
        if record is None:
            raise BrokerError("unknown_request", f"no pending request {request_id!r}")
        stored = str(record.get("request_digest", ""))
        if displayed_digest != stored:
            outcome = BrokerOutcome(
                DENY, request_id, stored, HARD_DENY, "digest_mismatch",
                "the displayed digest does not match the stored request binding")
            self._audit_record_only("approval_digest_mismatch", request_id, outcome)
            return outcome
        outcome = BrokerOutcome(
            DENY, request_id, stored, ASK, "owner_denied",
            reason or "the owner denied this request")
        record["status"] = STATUS_DENIED
        record["outcome"] = outcome.to_dict()
        record["answered_at_utc"] = to_utc_iso()
        self.journal.set_state(self._key(request_id), record)
        self._audit_record_only("approval_owner_denied", request_id, outcome)
        return outcome

    def revoke_all(self, reason: str = "operator revoke-all") -> int:
        """Revoke every pending and unconsumed approval, immediately (S13.10).

        Also reasserts that limited-auto is disabled. Nothing in this package can
        enable it; this makes the disabled state explicit in the durable record.
        """
        revoked = 0
        for key, record in self.journal.all_state().items():
            if not key.startswith(APPROVAL_PREFIX) or not isinstance(record, dict):
                continue
            if record.get("status") in (STATUS_PENDING, STATUS_APPROVED):
                record["status"] = STATUS_REVOKED
                record["revoked_reason"] = reason
                record["updated_at_utc"] = to_utc_iso()
                self.journal.set_state(key, record)
                revoked += 1
        self.journal.set_state("limited_auto_enabled", False)
        self.journal.set_state("revoke_all", {"at_utc": to_utc_iso(), "reason": reason,
                                              "revoked": revoked})
        if self.audit is not None:
            self.audit.append("approvals_revoked", run_id=self.run_id,
                              decision="REVOKE_ALL", policy_result="S13.10",
                              detail={"revoked": revoked, "reason": reason,
                                      "limited_auto_enabled": False})
        return revoked

    def _audit_record_only(self, event: str, request_id: str,
                           outcome: BrokerOutcome) -> None:
        if self.audit is None:
            return
        self.audit.append(event, run_id=self.run_id, decision=outcome.behavior,
                          policy_result=f"{outcome.tier}:{outcome.reason_code}",
                          input_digest=outcome.request_digest,
                          detail={"request_id": request_id, "reason": outcome.reason})


# --------------------------------------------------------------------------
# Tool-request translation (S8.4 structured data)
# --------------------------------------------------------------------------

#: Claude tool names mapped to the policy's action kinds. An unknown tool maps to
#: "unknown", which the policy queues rather than allows.
TOOL_KIND: Mapping[str, str] = {
    "Read": "read", "Glob": "read", "Grep": "read", "LS": "read",
    "NotebookRead": "read",
    "Write": "file_write", "Edit": "file_write", "MultiEdit": "file_write",
    "NotebookEdit": "file_write",
    "Bash": "command", "BashOutput": "read", "KillShell": "command",
    "Task": "subagent", "Agent": "subagent",
    "WebFetch": "network", "WebSearch": "network",
}

_PATH_INPUT_KEYS = ("file_path", "path", "notebook_path", "filePath")


def action_from_tool_request(
    tool_name: str,
    tool_input: Mapping[str, Any],
    *,
    request_id: str = "",
    stated_reason: str = "",
) -> ProposedAction:
    """Translate a `can_use_tool` control request into a `ProposedAction`.

    The mapping is deliberately conservative: an unrecognized tool becomes
    `unknown`, and the policy's fallthrough queues it.
    """
    kind = TOOL_KIND.get(tool_name, "unknown")
    paths: list[str] = []
    for key in _PATH_INPUT_KEYS:
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            paths.append(value)
    edits = tool_input.get("edits")
    change_bytes = 0
    for key in ("content", "new_string", "new_source"):
        value = tool_input.get(key)
        if isinstance(value, str):
            change_bytes += len(value.encode("utf-8"))
    if isinstance(edits, list):
        for edit in edits:
            if isinstance(edit, Mapping) and isinstance(edit.get("new_string"), str):
                change_bytes += len(edit["new_string"].encode("utf-8"))

    command_text = ""
    if kind == "command":
        raw = tool_input.get("command")
        command_text = raw if isinstance(raw, str) else ""

    return ProposedAction(
        kind=kind,
        tool_name=tool_name,
        tool_input=dict(tool_input),
        command_text=command_text,
        target_paths=tuple(paths),
        change_bytes=change_bytes,
        change_file_count=max(len(paths), 1),
        request_id=request_id,
        stated_reason=stated_reason,
    )
