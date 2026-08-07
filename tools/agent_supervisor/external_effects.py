#!/usr/bin/env python3
"""External effects, exactly once (D-007 S13.7, S11.5).

Git can roll back a commit. It cannot roll back an email, a PR comment, an issue
mutation, a cloud call, a deployment, or a payment. Every allowed external write
therefore gets:

* a **stable action id / idempotency key** derived from the effect's own content,
  so the same logical effect always produces the same key and a crash can never
  turn one effect into two;
* a **recorded target and expected prior state**, with read-before-write where
  the provider supports it;
* a **before-record committed and durably flushed BEFORE the effect**, and an
  after-record written **only after the result is verified**;
* **reconciliation before any retry** after a timeout or network loss - a PENDING
  record at recovery time means "this may have happened", which S11.5 classifies
  as `AMBIGUOUS_EFFECT`: prove what occurred from read-only evidence, never
  blindly rerun;
* **no automatic delete or overwrite** of an external resource, and a documented
  compensating action only where one safely exists.

An external write that is not explicitly modeled here is ASK-gated by the policy
engine. That is deliberate: the model list is the whole authority.

This module journals and reconciles. It never performs an external write itself.
"""
from __future__ import annotations

import dataclasses
from typing import Any, Callable, Mapping

from .durable_state import DurableJournal
from .models import (
    EFFECT_CONFIRMED,
    EFFECT_FAILED,
    EFFECT_PENDING,
    EffectRecord,
    digest_of,
    to_utc_iso,
)

RECONCILED_OCCURRED = "RECONCILED_OCCURRED"
RECONCILED_NOT_OCCURRED = "RECONCILED_NOT_OCCURRED"
RECONCILIATION_IMPOSSIBLE = "RECONCILIATION_IMPOSSIBLE"


class ExternalEffectError(Exception):
    """An external-effect rule was violated. Fail closed; never retry blindly."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclasses.dataclass(frozen=True)
class EffectSpec:
    """The policy model for ONE kind of external write."""

    effect_type: str
    description: str
    read_before_write: bool
    destructive: bool
    compensating_action: str
    requires_owner_gate: bool = False


#: The complete set of modeled external writes. Anything absent is ASK-gated.
#: Nothing here deletes or overwrites an external resource.
MODELED_EFFECTS: Mapping[str, EffectSpec] = {
    "git_push_task_branch": EffectSpec(
        "git_push_task_branch",
        "push commits to the exact authorized non-main task branch",
        read_before_write=True, destructive=False,
        compensating_action=("none automatic: a pushed branch is not force-updated or "
                             "deleted by the supervisor; recovery is a new commit")),
    "github_pr_create": EffectSpec(
        "github_pr_create", "create the task pull request (never merge it)",
        read_before_write=True, destructive=False,
        compensating_action="close the PR - an owner action, never automatic"),
    "github_pr_update": EffectSpec(
        "github_pr_update", "update the task pull request body or title",
        read_before_write=True, destructive=False,
        compensating_action="restore the recorded prior body - owner action"),
    "audit_anchor_push": EffectSpec(
        "audit_anchor_push",
        "push the audit chain head to the controller-owned anchor branch (Option A)",
        read_before_write=True, destructive=False,
        compensating_action="none needed: the anchor branch is append-only"),
    "owner_notification": EffectSpec(
        "owner_notification", "send one view-only redacted notification",
        read_before_write=False, destructive=False,
        compensating_action="none: a sent notification cannot be unsent"),
}


#: Substrings that mark an effect name/type as destructive. A merge is additive
#: (a merge commit) and is deliberately NOT here, so the shadow `github_pr_merge`
#: spec is admissible; a delete/overwrite/deploy/force/reset shape is not.
DESTRUCTIVE_EFFECT_MARKERS: tuple[str, ...] = (
    "delete", "destroy", "overwrite", "wipe", "purge", "drop", "remove",
    "rmdir", "force_push", "deploy",
)


def _looks_destructive(name: str) -> bool:
    lowered = str(name).lower()
    return any(marker in lowered for marker in DESTRUCTIVE_EFFECT_MARKERS)


def guard_extra_specs(
    extra_specs: Mapping[str, EffectSpec] | None) -> dict[str, EffectSpec]:
    """Validate a per-instance `extra_specs` override channel (D-010 SEC-1).

    The override is consulted BEFORE `MODELED_EFFECTS`, so an unguarded live-path
    journal built with `extra_specs` could shadow a registry spec or make an
    unmodeled destructive effect performable without appearing in the registry
    the invariant-9 lock guards. This fails those shapes closed at construction:

    * a key that collides with a modeled live-path effect is REFUSED (an override
      may never shadow the production registry);
    * a spec marked `destructive`, or whose name/effect_type matches a destructive
      marker, is REFUSED (the supervisor never auto-deletes/overwrites/deploys).
    """
    specs = dict(extra_specs or {})
    for name, spec in specs.items():
        if name in MODELED_EFFECTS:
            raise ExternalEffectError(
                "extra_spec_collision",
                f"{name!r} collides with a modeled live-path effect; an extra spec may "
                f"never shadow or override the production registry (D-010 SEC-1)")
        if getattr(spec, "destructive", False) or _looks_destructive(name) or \
                _looks_destructive(getattr(spec, "effect_type", "")):
            raise ExternalEffectError(
                "destructive_extra_spec",
                f"{name!r} is a destructive extra spec; a destructive external effect is "
                f"never journaled-and-performed through this channel (D-010 SEC-1)")
    return specs


def is_modeled(effect_type: str) -> bool:
    return effect_type in MODELED_EFFECTS


def spec_for(effect_type: str) -> EffectSpec:
    try:
        return MODELED_EFFECTS[effect_type]
    except KeyError as exc:
        raise ExternalEffectError(
            "unmodeled_effect",
            f"{effect_type!r} is not a modeled external write; unmodeled external writes "
            f"are ASK-gated (S13.7) and never performed on a model's say-so") from exc


def stable_action_id(
    *,
    effect_type: str,
    target: str,
    task_id: str,
    request_digest: str,
    logical_sequence: str = "",
) -> str:
    """The idempotency key. Same logical effect in, same key out - always.

    A crash between the before-record and the effect produces the SAME key on the
    next attempt, so the journal recognizes the pending effect instead of
    creating a second one.
    """
    return "eff_" + digest_of({
        "effect_type": effect_type,
        "target": target,
        "task_id": task_id,
        "request_digest": request_digest,
        "logical_sequence": logical_sequence,
    })[:32]


@dataclasses.dataclass(frozen=True)
class ReconciliationResult:
    """What read-only evidence proved about a pending effect."""

    action_id: str
    status: str
    detail: str
    observed_state: str = ""

    @property
    def safe_to_retry(self) -> bool:
        return self.status == RECONCILED_NOT_OCCURRED

    @property
    def requires_pause(self) -> bool:
        return self.status == RECONCILIATION_IMPOSSIBLE


class ExternalEffectJournal:
    """The S13.7 journal, layered on the Phase 1 durable effects table."""

    def __init__(self, journal: DurableJournal, *, audit: Any = None,
                 run_id: str = "",
                 extra_specs: Mapping[str, EffectSpec] | None = None) -> None:
        self.journal = journal
        self.audit = audit
        self.run_id = run_id
        #: SHADOW-SCOPED specs, merged with `MODELED_EFFECTS` for lookups ONLY on
        #: this instance. The production registry (the live-path authority) is
        #: never mutated, so a directed/shadow capability can be journaled and
        #: reconciled through this machinery without wiring a new automatic effect
        #: into the live path (D-007 invariant 9 stays true of `MODELED_EFFECTS`).
        #: `guard_extra_specs` fails closed on a registry collision or a
        #: destructive override, so this channel can never shadow a modeled effect
        #: or smuggle a delete/overwrite/deploy past invariant 9 (D-010 SEC-1).
        self.extra_specs: Mapping[str, EffectSpec] = guard_extra_specs(extra_specs)

    def _spec_for(self, effect_type: str) -> EffectSpec:
        """Resolve a spec from the instance's shadow specs, then the registry."""
        if effect_type in self.extra_specs:
            return self.extra_specs[effect_type]
        return spec_for(effect_type)

    # -- before / after ------------------------------------------------------

    def begin(
        self,
        *,
        effect_type: str,
        target: str,
        task_id: str,
        request_digest: str,
        logical_sequence: str = "",
        prior_state_reader: Callable[[], str] | None = None,
    ) -> EffectRecord:
        """Journal the effect BEFORE performing it, with its expected prior state.

        Returns the EXISTING record when the action id is already present: a
        repeated `begin()` for the same logical effect is recognized, not
        duplicated.
        """
        spec = self._spec_for(effect_type)
        action_id = stable_action_id(effect_type=effect_type, target=target,
                                     task_id=task_id, request_digest=request_digest,
                                     logical_sequence=logical_sequence)
        existing = self.journal.get_effect(action_id)
        if existing is not None:
            self._audit("external_effect_duplicate_begin", action_id, effect_type,
                        {"status": existing.status,
                         "note": "same idempotency key: not a second effect"})
            return existing

        prior_state = ""
        if spec.read_before_write:
            if prior_state_reader is None:
                raise ExternalEffectError(
                    "read_before_write_required",
                    f"{effect_type!r} requires read-before-write; supply a reader that "
                    f"records the expected prior state")
            prior_state = str(prior_state_reader())

        record = self.journal.record_before_effect(
            action_id=action_id, effect_type=effect_type, target=target,
            expected_prior_state=prior_state, request_digest=request_digest)
        self._audit("external_effect_before", action_id, effect_type,
                    {"target": target, "expected_prior_state": prior_state,
                     "compensating_action": spec.compensating_action})
        return record

    def confirm(self, action_id: str, *, resulting_state: str,
                reconciliation: str = "") -> EffectRecord:
        """Journal the VERIFIED result. Only ever called after verification."""
        record = self.journal.record_after_effect(
            action_id, resulting_state=resulting_state, status=EFFECT_CONFIRMED,
            reconciliation=reconciliation)
        self._audit("external_effect_after", action_id, record.effect_type,
                    {"resulting_state": resulting_state,
                     "reconciliation": reconciliation})
        return record

    def fail(self, action_id: str, *, detail: str) -> EffectRecord:
        """Journal a PROVEN failure. An unproven failure stays pending instead."""
        record = self.journal.record_after_effect(
            action_id, resulting_state="", status=EFFECT_FAILED, reconciliation=detail)
        self._audit("external_effect_failed", action_id, record.effect_type,
                    {"detail": detail})
        return record

    # -- reconciliation ------------------------------------------------------

    def pending(self) -> list[EffectRecord]:
        return self.journal.pending_effects()

    def reconcile(
        self,
        action_id: str,
        prober: Callable[[EffectRecord], tuple[bool | None, str]],
    ) -> ReconciliationResult:
        """Prove from read-only evidence whether a pending effect occurred.

        `prober` returns `(occurred, observed_state)` where `occurred` is True,
        False, or None for "cannot be determined". None means the ambiguity stands
        and the run pauses (S11.5 `PAUSED_RECOVERY`) - it never means "assume it
        did not happen and retry".
        """
        record = self.journal.get_effect(action_id)
        if record is None:
            raise ExternalEffectError("unknown_action",
                                      f"no journaled effect with id {action_id!r}")
        if record.status != EFFECT_PENDING:
            return ReconciliationResult(
                action_id, RECONCILED_OCCURRED if record.status == EFFECT_CONFIRMED
                else RECONCILED_NOT_OCCURRED,
                f"already {record.status}", record.resulting_state)

        try:
            occurred, observed = prober(record)
        except Exception as exc:
            result = ReconciliationResult(
                action_id, RECONCILIATION_IMPOSSIBLE,
                f"the read-only probe failed ({exc}); the effect remains ambiguous")
            self._audit("external_effect_unreconciled", action_id, record.effect_type,
                        {"detail": result.detail})
            return result

        if occurred is True:
            self.confirm(action_id, resulting_state=observed,
                         reconciliation="reconciled from read-only provider/Git evidence")
            return ReconciliationResult(action_id, RECONCILED_OCCURRED,
                                        "proven to have occurred", observed)
        if occurred is False:
            self.journal.record_after_effect(
                action_id, resulting_state="", status=EFFECT_FAILED,
                reconciliation="proven NOT to have occurred; safe to retry with the same "
                               "idempotency key")
            self._audit("external_effect_reconciled_absent", action_id,
                        record.effect_type, {"observed": observed})
            return ReconciliationResult(action_id, RECONCILED_NOT_OCCURRED,
                                        "proven not to have occurred", observed)

        result = ReconciliationResult(
            action_id, RECONCILIATION_IMPOSSIBLE,
            "read-only evidence cannot establish whether the effect occurred; the run "
            "pauses rather than retrying an ambiguous external action (inv. 13)",
            observed)
        self._audit("external_effect_unreconciled", action_id, record.effect_type,
                    {"observed": observed})
        return result

    def assert_safe_to_retry(self, action_id: str) -> None:
        """Refuse a retry unless the effect is PROVEN not to have occurred."""
        record = self.journal.get_effect(action_id)
        if record is None:
            return
        if record.status == EFFECT_PENDING:
            raise ExternalEffectError(
                "ambiguous_retry_refused",
                f"effect {action_id!r} is still PENDING; reconcile it before any retry "
                f"(S13.7, invariant 13)")
        if record.status == EFFECT_CONFIRMED:
            raise ExternalEffectError(
                "already_performed",
                f"effect {action_id!r} is CONFIRMED; performing it again would be a "
                f"duplicate external action")

    def assert_not_destructive(self, effect_type: str) -> None:
        """No automatic delete or overwrite of an external resource (S13.7)."""
        spec = self._spec_for(effect_type)
        if spec.destructive:
            raise ExternalEffectError(
                "destructive_external_effect",
                f"{effect_type!r} would delete or overwrite an external resource; the "
                f"supervisor never does that automatically")

    # -- audit ---------------------------------------------------------------

    def _audit(self, event: str, action_id: str, effect_type: str,
               detail: Mapping[str, Any]) -> None:
        if self.audit is None:
            return
        self.audit.append(event, run_id=self.run_id,
                          detail={"action_id": action_id, "effect_type": effect_type,
                                  **dict(detail), "at_utc": to_utc_iso()})


def recovery_classification(pending: list[EffectRecord]) -> str:
    """The S11.5 label a set of pending effects implies at recovery time."""
    if not pending:
        return "SAFE_CHECKPOINT"
    return "AMBIGUOUS_EFFECT"
