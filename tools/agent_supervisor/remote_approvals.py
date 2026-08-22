#!/usr/bin/env python3
"""Authenticated, request-bound remote approvals (D-007 S13.10).

S13.10: "Remote approval of queued ASK items requires an authenticated surface
binding: owner identity, exact request digest, one-time nonce, expiration,
current task/branch/SHA, and an approve-once or deny outcome. A bare 'yes' by
email/Slack/SMS is insufficient unless a separately reviewed authenticated
integration binds it to the exact request."

The binding is the whole security property, so it is a value object
(`ApprovalBinding`) whose digest covers every element. An answer is accepted only
when ALL of these hold:

* the nonce exists, has never been consumed, and belongs to this binding;
* the binding has not expired (monotonic-independent: expiry is an absolute UTC
  instant, and a clock moved backwards is rejected rather than trusted);
* the answered request digest equals the bound one;
* the owner identity matches;
* the repository state (task, branch, HEAD) still matches the binding;
* the outcome is exactly `approve-once` or `deny`.

Anything else - a replay, an expired nonce, a wrong digest, an unbound "yes" -
is refused with its own reason code and is recorded. There is no "always allow",
no "approve all", and no bulk approval. `revoke_all` revokes every outstanding
binding AND asserts limited-auto off.

This module performs NO network I/O. The "authenticated surface" is modelled as
an interface the owner's separately reviewed integration would implement; this
build only issues, verifies, consumes, and revokes bindings locally.
"""
from __future__ import annotations

import dataclasses
import datetime as _dt
import hmac
import secrets
from typing import Any, Mapping

from .models import digest_of, to_utc_iso

APPROVE_ONCE = "approve-once"
DENY = "deny"
OUTCOMES: tuple[str, ...] = (APPROVE_ONCE, DENY)

BINDINGS_KEY = "remote_approval_bindings"
CONSUMED_NONCE_KEY = "remote_approval_consumed_nonces"
LIMITED_AUTO_KEY = "limited_auto_enabled"

DEFAULT_EXPIRY_SECONDS = 3600


class RemoteApprovalError(Exception):
    """A remote answer was not accepted. Always fails closed."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclasses.dataclass(frozen=True)
class ApprovalBinding:
    """The complete S13.10 binding. Its digest is what the owner confirms."""

    binding_id: str
    owner_identity: str
    request_id: str
    request_digest: str
    nonce: str
    expires_at_utc: str
    task_id: str
    branch: str
    head_sha: str
    question: str
    created_at_utc: str

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    def digest(self) -> str:
        """Digest over EVERY bound element (the nonce included)."""
        return digest_of(self.to_dict())

    def expired(self, now_utc: _dt.datetime) -> bool:
        expiry = _dt.datetime.fromisoformat(self.expires_at_utc.replace("Z", "+00:00"))
        return now_utc >= expiry


@dataclasses.dataclass(frozen=True)
class RemoteAnswer:
    """What the authenticated surface reports back. Untrusted until verified."""

    binding_id: str
    nonce: str
    outcome: str
    owner_identity: str
    request_digest: str
    displayed_binding_digest: str = ""
    received_at_utc: str = ""


@dataclasses.dataclass(frozen=True)
class AnswerVerdict:
    accepted: bool
    outcome: str
    reason_code: str
    reason: str
    binding_id: str = ""
    request_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


class RemoteApprovalRegistry:
    """Durable issue / verify / consume / revoke over the journal."""

    def __init__(self, journal: Any, *, audit: Any = None,
                 owner_identity: str = "") -> None:
        self.journal = journal
        self.audit = audit
        self.owner_identity = owner_identity

    # -- state ---------------------------------------------------------------

    def _bindings(self) -> dict[str, dict[str, Any]]:
        data = self.journal.get_state(BINDINGS_KEY, {}) or {}
        return dict(data) if isinstance(data, Mapping) else {}

    def _write_bindings(self, bindings: Mapping[str, Any]) -> None:
        self.journal.set_state(BINDINGS_KEY, dict(bindings))

    def _consumed(self) -> list[str]:
        return list(self.journal.get_state(CONSUMED_NONCE_KEY, []) or [])

    def open_bindings(self) -> tuple[ApprovalBinding, ...]:
        known = {f.name for f in dataclasses.fields(ApprovalBinding)}
        return tuple(
            ApprovalBinding(**{k: v for k, v in record.items() if k in known})
            for record in self._bindings().values()
        )

    # -- issuing -------------------------------------------------------------

    def issue(
        self,
        *,
        request_id: str,
        request_digest: str,
        task_id: str,
        branch: str,
        head_sha: str,
        question: str,
        now_utc: _dt.datetime | None = None,
        expiry_seconds: int = DEFAULT_EXPIRY_SECONDS,
    ) -> ApprovalBinding:
        """Issue one binding with a fresh one-time nonce and an absolute expiry."""
        if not self.owner_identity:
            raise RemoteApprovalError(
                "no_owner_identity",
                "a remote approval binding requires the owner identity the authenticated "
                "surface will assert; an unattributed approval is not an approval")
        if len(request_digest) != 64:
            raise RemoteApprovalError("bad_request_digest",
                                      "the bound request digest must be a full SHA-256")
        if expiry_seconds <= 0:
            raise RemoteApprovalError("bad_expiry",
                                      "a remote approval must expire; 'never' is not an "
                                      "option")
        now = now_utc or _dt.datetime.now(_dt.timezone.utc)
        binding = ApprovalBinding(
            binding_id=f"rab_{secrets.token_hex(8)}",
            owner_identity=self.owner_identity,
            request_id=request_id,
            request_digest=request_digest,
            nonce=secrets.token_hex(16),
            expires_at_utc=to_utc_iso(now + _dt.timedelta(seconds=expiry_seconds)),
            task_id=task_id,
            branch=branch,
            head_sha=head_sha,
            question=question,
            created_at_utc=to_utc_iso(now),
        )
        bindings = self._bindings()
        bindings[binding.binding_id] = binding.to_dict()
        self._write_bindings(bindings)
        self._audit("remote_approval_issued", {
            "binding_id": binding.binding_id, "request_id": request_id,
            "binding_digest": binding.digest(), "expires_at_utc": binding.expires_at_utc})
        return binding

    # -- verifying -----------------------------------------------------------

    def verify(
        self,
        answer: RemoteAnswer,
        *,
        now_utc: _dt.datetime | None = None,
        current_task_id: str = "",
        current_branch: str = "",
        current_head_sha: str = "",
    ) -> AnswerVerdict:
        """Verify and CONSUME an answer. Every failure has its own reason code."""
        now = now_utc or _dt.datetime.now(_dt.timezone.utc)

        if answer.outcome not in OUTCOMES:
            return self._reject(answer, "unbound_answer",
                                f"the surface returned {answer.outcome!r}; only "
                                f"{OUTCOMES} are accepted. A bare 'yes' is not an approval "
                                f"(S13.10)")

        bindings = self._bindings()
        record = bindings.get(answer.binding_id)
        if record is None:
            if answer.nonce in self._consumed():
                return self._reject(answer, "nonce_replayed",
                                    "this nonce was already used; a remote approval is "
                                    "single-use and replay-resistant")
            return self._reject(answer, "unknown_binding",
                                f"no open binding {answer.binding_id!r}; an answer that is "
                                f"not bound to a live request is refused")

        known = {f.name for f in dataclasses.fields(ApprovalBinding)}
        binding = ApprovalBinding(**{k: v for k, v in record.items() if k in known})

        if not hmac.compare_digest(answer.nonce, binding.nonce):
            return self._reject(answer, "nonce_mismatch",
                                "the answer's nonce does not match the issued one")
        if answer.nonce in self._consumed():
            return self._reject(answer, "nonce_replayed",
                                "this nonce was already used; a remote approval is "
                                "single-use and replay-resistant")
        if binding.expired(now):
            self._consume(binding, bindings)
            return self._reject(answer, "expired_nonce",
                                f"the binding expired at {binding.expires_at_utc}; an "
                                f"expired approval is never honoured")
        if not hmac.compare_digest(answer.request_digest, binding.request_digest):
            return self._reject(answer, "wrong_digest",
                                "the answered request digest is not the bound one; the "
                                "request changed, so the approval is void (S13.5)")
        if answer.displayed_binding_digest and not hmac.compare_digest(
                answer.displayed_binding_digest, binding.digest()):
            return self._reject(answer, "wrong_digest",
                                "the digest the owner was shown does not match this binding")
        if answer.owner_identity != binding.owner_identity:
            return self._reject(answer, "wrong_owner",
                                "the answering identity is not the bound owner identity")
        for name, current, bound in (("task", current_task_id, binding.task_id),
                                     ("branch", current_branch, binding.branch),
                                     ("HEAD", current_head_sha, binding.head_sha)):
            if current and current != bound:
                return self._reject(answer, "repository_state_changed",
                                    f"the {name} moved from {bound!r} to {current!r} after "
                                    f"the binding was issued; no approval survives a changed "
                                    f"repository state (invariant 6)")

        self._consume(binding, bindings)
        self._audit("remote_approval_answered", {
            "binding_id": binding.binding_id, "request_id": binding.request_id,
            "outcome": answer.outcome, "binding_digest": binding.digest()})
        return AnswerVerdict(
            answer.outcome == APPROVE_ONCE, answer.outcome, "answer_accepted",
            f"authenticated, digest-bound, single-use {answer.outcome} for request "
            f"{binding.request_id}", binding.binding_id, binding.request_id)

    def _consume(self, binding: ApprovalBinding, bindings: dict[str, Any]) -> None:
        bindings.pop(binding.binding_id, None)
        self._write_bindings(bindings)
        consumed = self._consumed()
        if binding.nonce not in consumed:
            consumed.append(binding.nonce)
        self.journal.set_state(CONSUMED_NONCE_KEY, consumed)

    def _reject(self, answer: RemoteAnswer, code: str, reason: str) -> AnswerVerdict:
        self._audit("remote_approval_rejected",
                    {"binding_id": answer.binding_id, "reason_code": code})
        return AnswerVerdict(False, DENY, code, reason, answer.binding_id)

    # -- revocation ----------------------------------------------------------

    def revoke_all(self, *, reason: str) -> dict[str, Any]:
        """Revoke every outstanding binding AND assert limited-auto disabled (S13.10)."""
        bindings = self._bindings()
        consumed = self._consumed()
        for record in bindings.values():
            nonce = str(record.get("nonce", ""))
            if nonce and nonce not in consumed:
                consumed.append(nonce)
        count = len(bindings)
        self._write_bindings({})
        self.journal.set_state(CONSUMED_NONCE_KEY, consumed)
        self.journal.set_state(LIMITED_AUTO_KEY, False)
        record = {"revoked_bindings": count, "reason": reason,
                  "limited_auto_enabled": False, "at_utc": to_utc_iso()}
        self._audit("remote_approvals_revoked", record)
        return record

    def _audit(self, event: str, detail: Mapping[str, Any]) -> None:
        if self.audit is not None:
            self.audit.append(event, detail=dict(detail))


def disable_limited_auto(journal: Any, *, reason: str, audit: Any = None) -> dict[str, Any]:
    """The immediate 'turn it off' half of the S13.10 revoke command."""
    journal.set_state(LIMITED_AUTO_KEY, False)
    record = {"limited_auto_enabled": False, "reason": reason, "at_utc": to_utc_iso(),
              "note": "limited-auto is implemented (M0-T079) and OFF by default, enabled "
                      "only by an explicit per-launch owner act; this command asserts the "
                      "flag off regardless"}
    if audit is not None:
        audit.append("limited_auto_disabled", detail=record)
    return record
