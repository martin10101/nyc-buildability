#!/usr/bin/env python3
"""Pending-prompt parking, approval binding, and covered-instruction
verification (S9/S13.5; M0-T045/M0-T046/M0-T048).

Moved VERBATIM out of `loop.py` (M0-T093 modularity split; supervisor-freeze
qualifying evidence D-024-R103): a grandfathered-oversized `loop.py` grew past
its reviewed baseline allowance when the unit-H1 guardrail-refusal seam was
wired, and the modularity policy's remedy is a facade-preserving split (the
M0-T080 / unit-G `operator_channel_cli` precedent), never an exception record.
This block is the loop's most self-contained responsibility - what an operator
approval actually BINDS to, and how a parked prompt is approved, verified, and
consumed across processes - with its own accepted test packs
(test_agent_supervisor_pending_prompt / _park_approve_binding / _audit_anchor /
_c2_binding). `loop.py` re-exports every public name, so every existing
`loop.<name>` import site keeps working unchanged (docs/CODE_MODULARITY_POLICY.md
section 6). No behavior change: the code below is byte-identical to what
`loop.py` held, save for these imports.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from .codex_reviewer import build_forwarded_prompt
from .errors import LoopError
from .models import digest_of, to_utc_iso
from .policy import DENY_AND_HALT

# --------------------------------------------------------------------------
# Prompt digests: what an approval actually binds to
# --------------------------------------------------------------------------
#
# Historically a rendered forwarded prompt was NOT stable across renders: it
# carried a `FORWARDED AT:` timestamp and a reference to the evidence packet,
# whose own digest moved with the clock and with live git state. Binding an
# approval to those bytes makes a digest-bound approval impossible to honour - the
# operator is shown one digest, and by the time they answer with it the prompt has
# re-rendered to a different one. (Found by running `start --mode supervised` end
# to end: the approval never matched, twice, for two different reasons.)
#
# So the approval digest is computed from the INSTRUCTION FIELDS directly - the
# exact five things S9 says every forwarded prompt carries, plus the task and stage
# that confer authority:
#
#   approval_digest   "is this the same INSTRUCTION?"   Binds the approval, the
#                     pending-prompt record, and the outbox message id, so a
#                     crash-and-re-render resumes rather than duplicating.
#   digest_of(prompt) "what exact bytes went out?"      Recorded in the envelope
#                     and the audit trail, for provenance.
#
# Change the task, the stage, a permitted path, the requested action, or a stop
# condition, and the approval digest changes - so the approval is invalidated,
# which is exactly S13.5's rule. Change only the clock, and it does not.
#
# M0-T048 (D-010 am.14, R136/R137) went one step further so the FORWARDED CONTENT
# itself - not just the approval - is bound to that operator-named digest.
# `build_forwarded_prompt` now emits a DETERMINISTIC, timestamp-free body that is a
# pure function of the same five canonical fields; the `FORWARDED AT:` clock is
# appended only at actual forward time (`stamp_forwarded_at`) and the volatile
# packet reference is gone. So the timestamp-free body is reconstructable from
# approval-covered material, and `verify_covered_instruction` (below) recomputes it
# at approve/resume and refuses fail-closed unless the persisted structured
# instruction reproduces the operator-named approval digest. An attacker who
# rewrites the parked prompt bytes AND their journal-resident `prompt_bytes_digest`,
# leaving the operator digest untouched, can no longer get altered content
# forwarded: the content is derived from the operator-covered instruction, never
# trusted from the mutable journal bytes.

APPROVAL_DIGEST_FIELDS: tuple[str, ...] = (
    "task_id", "stage", "allowed_paths", "requested_action", "stop_conditions")


def approval_digest(
    *,
    task_id: str,
    stage: str,
    allowed_paths: Sequence[str],
    requested_action: str,
    stop_conditions: Sequence[str],
) -> str:
    """The digest an approval binds to: the instruction, not the clock."""
    return digest_of({
        "task_id": task_id,
        "stage": stage,
        "allowed_paths": sorted(str(p) for p in allowed_paths),
        "requested_action": requested_action.strip(),
        "stop_conditions": sorted(str(s) for s in stop_conditions),
    })


#: Reason codes that ARE would-be synchronous stops (S4.5), used to count the
#: owner-touch budget. Derived, not restated: policy owns the condition list.
def is_synchronous_stop(decision: Any) -> bool:
    """True when a `PolicyDecision`-shaped object demands a synchronous stop."""
    return bool(getattr(decision, "synchronous_stop", False)) or \
        getattr(decision, "outcome", "") == DENY_AND_HALT


def pending_prompt_key(run_id: str) -> str:
    """The durable key the supervised WAIT parks its held prompt under.

    Kept here so the writer (`run_cycle`), the loop consumer, and the CLI
    `resume-pending-prompt` command cannot drift apart on the key shape.

    The record travels through three shapes, and every consumer keys off the
    field that is present (never a positional guess):

    * PARKED (written by `run_cycle` at the supervised WAIT) -
      ``{"cycle", "digest", "prompt", "reviewed_checkpoint_id", "decision",
      "created_at_utc"}``. ``digest`` is the approval binding the operator must
      name; ``prompt`` is the EXACT held prompt bytes, parked so a DIFFERENT
      process can forward them unchanged (M0-T045).
    * APPROVED (written by `approve_pending_prompt` on a successful
      `resume-pending-prompt`) - ``{"approved": True, "cycle", "prompt",
      "approved_digest", "decision", "prior_digest", "approved_at_utc"}``. The
      ``digest`` key is DROPPED so the re-approval guards (`not
      pending.get("digest")`) stay closed, while ``prompt`` + ``approved_digest``
      carry exactly what a fresh `start` needs to forward once.
    * CONSUMED (written by `consume_pending_prompt` after the forward is sent) -
      ``{"consumed": True, "consumed_at_utc", "prior_digest"}``. Nothing
      approvable and nothing forwardable remains.
    """
    return f"pending_prompt/{run_id}"


def consume_pending_prompt(journal: Any, run_id: str, *, prior_digest: str = "") -> None:
    """Clear the pending_prompt record after it is approved and forwarded (AS-4).

    G5 V1.2.3 LOW finding (project-control/reports/
    M0-T036-V1.2.3-G5-security-delta-review.md): "neither it nor the loop
    consumes/clears the record after use", so in an active supervised
    multi-cycle run a later WAIT for a DIFFERENT ask could still carry a prior
    cycle's pending_prompt, and an operator supplying that (genuine, system-
    recorded) digest would re-fire owner_approved_pending_prompt. Consuming the
    record on a SUCCESSFUL resume drops the digest, so the WAIT guards ("no
    pending-prompt record" / digest mismatch) fail closed on any re-approval:
    a stale record can never be approved twice.
    """
    journal.set_state(
        pending_prompt_key(run_id),
        {"consumed": True, "consumed_at_utc": to_utc_iso(),
         "prior_digest": prior_digest})


def verify_covered_instruction(
        instruction: Any, operator_digest: str, prompt: str, anchor: Any) -> str:
    """Reconstruct the forwarded body from OPERATOR-COVERED material, or fail closed.

    M0-T048 (D-010 am.14, R136): the forwarded content must be cryptographically
    bound to information the operator-named ``approval_digest`` covers, never trusted
    from the mutable journal ``prompt``/``prompt_bytes_digest`` fields alone. This
    recomputes the instruction body from the persisted structured instruction and
    returns it ONLY when:

      1. the persisted structured instruction is present and well-formed (an
         old-shape/missing record REFUSES - it is never treated as journal-resident-
         only verification, AS-6);
      2. ``approval_digest(instruction)`` reproduces the operator-named digest - so
         every field that determines the body is exactly what the operator approved;
      3. (defence in depth, preserving the M0-T046 sealed byte anchor) the park-time
         ``prompt_bytes_digest`` and the parked ``prompt`` bytes both still match the
         reconstruction.

    Because ``build_forwarded_prompt`` is a pure function of the same canonical fields
    ``approval_digest`` covers, step 2 alone already fixes every byte of the returned
    body; steps 1/3 give distinct fail-closed reason codes and keep the earlier
    guarantees intact. Raises ``LoopError`` (``pending_prompt_uncovered`` or
    ``pending_prompt_tampered``) with no side effect on any refusal.
    """
    if not isinstance(instruction, Mapping):
        raise LoopError(
            "pending_prompt_uncovered",
            "the parked record carries no structured approved instruction; refusing "
            "to forward bytes that are not bound to the operator-named approval digest "
            "(old-shape/missing binding material). Fail-closed: no fallback to "
            "journal-resident-only verification")
    try:
        fields = {
            "task_id": str(instruction["task_id"]),
            "stage": str(instruction["stage"]),
            "allowed_paths": list(instruction["allowed_paths"]),
            "requested_action": str(instruction["requested_action"]),
            "stop_conditions": list(instruction["stop_conditions"]),
        }
    except (KeyError, TypeError) as exc:
        raise LoopError(
            "pending_prompt_uncovered",
            f"the parked approved instruction is malformed ({exc!r}); refusing "
            f"fail-closed rather than forward uncovered content") from exc
    if approval_digest(**fields) != operator_digest:
        raise LoopError(
            "pending_prompt_uncovered",
            "the parked approved instruction does not reproduce the operator-named "
            "approval digest; the forwarded content would not be covered by the "
            "operator's approval. Fail-closed: no approval is written")
    expected_body = build_forwarded_prompt(**fields)
    if isinstance(anchor, str) and anchor and digest_of(expected_body) != anchor:
        raise LoopError(
            "pending_prompt_tampered",
            "the park-time byte anchor no longer matches the body reconstructed from "
            "the operator-covered instruction; the parked record was altered after "
            "park. Fail-closed: no approval is written")
    if digest_of(prompt) != digest_of(expected_body):
        raise LoopError(
            "pending_prompt_tampered",
            "the parked prompt bytes no longer match the byte anchor / reconstruction "
            "from the operator-covered instruction; the held prompt was altered after "
            "it was parked. Refusing fail-closed: no approval is written")
    return expected_body


#: The sealed, hash-chained audit event the `resume-pending-prompt` CLI writes on a
#: genuine operator approval. Its ``input_digest`` is the operator-named approval
#: digest; the event lives in the append-only local hash chain (audit_log.py, M0-T046),
#: so forging or rewriting it requires breaking the chain, which `verify_chain` detects.
OPERATOR_APPROVAL_EVENT = "operator_resume_pending_prompt"


def verify_approved_digest_against_audit(
        audit: Any, run_id: str, approved_digest: str) -> None:
    """Cross-check the journal ``approved_digest`` against the SEALED operator approval.

    M0-T048 REWORK (D-010 R145..R150; G3 MAJOR-1): the cross-process resume path must
    NOT trust the mutable journal ``approved_digest`` as the sole record of what the
    operator approved. An attacker with journal write who rewrites ``approved_instruction``
    AND ``approved_digest`` (AND ``prompt``/``prompt_bytes_digest``) self-consistently
    AFTER a genuine approval otherwise slips altered content through the reconstruction
    check (the forged instruction reproduces the forged digest). This anchors the resume
    to the ALREADY-SEALED, hash-chained operator-approval audit evidence instead: the
    ``resume-pending-prompt`` CLI seals an ``operator_resume_pending_prompt``
    (``decision="approve"``) event whose ``input_digest`` is the operator-named digest.
    Rewriting that event requires breaking the chain, which ``verify_chain`` detects.

    Fails closed with a DISTINCT reason code (never fails open, never warn-only) on:
      * no audit log to consult                    -> ``approved_digest_audit_unavailable``
      * an unreadable audit log                    -> ``approval_audit_unreadable``
      * a chain that does not verify (tamper/fork/
        truncate)                                  -> ``approval_audit_chain_invalid``
      * no sealed approval event for this run      -> ``approved_digest_audit_missing``
      * a sealed approval whose operator-named
        digest differs from the journal's          -> ``approved_digest_audit_mismatch``
      * conflicting/duplicated sealed approvals of
        the same digest                            -> ``approved_digest_audit_ambiguous``

    No side effects. The caller seals the refusal (owner requirement: the mismatch must
    be durably recorded) and re-raises fail-closed.
    """
    if audit is None:
        raise LoopError(
            "approved_digest_audit_unavailable",
            "no sealed operator-approval audit evidence is available to cross-check the "
            "journal approved_digest against; refusing fail-closed rather than treating "
            "the mutable journal as the sole record of what the operator approved")
    try:
        verification = audit.verify_chain()
    except Exception as exc:  # a damaged/unreadable log must never fail open
        raise LoopError(
            "approval_audit_unreadable",
            f"the operator-approval audit log is unreadable ({exc}); refusing to forward "
            f"without a verifiable sealed record of the approval") from exc
    if not getattr(verification, "ok", False):
        raise LoopError(
            "approval_audit_chain_invalid",
            f"the operator-approval audit chain does not verify "
            f"({getattr(verification, 'code', '')}: {getattr(verification, 'message', '')}); "
            f"a tampered, forked, or truncated chain can no longer anchor what the "
            f"operator approved, so the resume refuses fail-closed")
    try:
        records = audit.read_all()
    except Exception as exc:
        raise LoopError(
            "approval_audit_unreadable",
            f"the operator-approval audit log could not be read ({exc}); refusing to "
            f"forward without a verifiable sealed record of the approval") from exc
    approvals = [
        r for r in records
        if r.get("event_type") == OPERATOR_APPROVAL_EVENT
        and r.get("decision") == "approve"
        and (r.get("run_id") or "") == run_id]
    if not approvals:
        raise LoopError(
            "approved_digest_audit_missing",
            "no sealed operator-approval event records an approval for this run; the "
            "journal claims an approval that the hash-chained audit evidence does not "
            "hold. Refusing fail-closed - a missing durable approval is never trusted")
    matching = [r for r in approvals
                if (r.get("input_digest") or "") == approved_digest]
    if not matching:
        raise LoopError(
            "approved_digest_audit_mismatch",
            "the journal approved_digest does not match the operator-named digest sealed "
            "in the operator-approval audit evidence; the mutable journal was altered "
            "after a genuine approval. Refusing fail-closed - the sealed, hash-chained "
            "record, not the journal, is the authoritative record of the approval")
    if len(matching) > 1:
        raise LoopError(
            "approved_digest_audit_ambiguous",
            "multiple sealed operator-approval events name the same approved_digest for "
            "this run; the approval evidence is ambiguous or replayed. Refusing "
            "fail-closed rather than guessing which approval is authoritative")


def approve_pending_prompt(journal: Any, run_id: str, *, pending: Mapping[str, Any],
                           approval_binding: str) -> None:
    """Record a PARKED prompt as APPROVED without dropping what the forward needs.

    M0-T045: the approval and the forward can happen in DIFFERENT processes -
    `resume-pending-prompt` fires the owner_approved_pending_prompt transition,
    and a later, separate `start` completes the forward. The old code called
    `consume_pending_prompt` at approval time, which dropped the held prompt
    bytes and the digest, so the resuming process had nothing to forward and the
    loop refused. This keeps the exact held prompt text plus an `approved_digest`
    binding so the resuming loop can verify integrity and forward once - while
    STILL removing the `digest` key so every re-approval guard (`not
    pending.get("digest")`) stays fail-closed. An OLD-shape parked record with no
    held prompt leaves behind an approved record with no `prompt`/`approved_digest`,
    which the loop refuses to forward (it never fabricates a prompt).

    M0-T046 (D-010-R124), G5 LOW-1: a park-time byte anchor (`prompt_bytes_digest`)
    was frozen when the bytes were authentic and re-verified before any state change.

    M0-T048 (D-010 am.14, R136/R137): closes the G5 C2 residual. The parked record
    now carries the STRUCTURED approved instruction, and this function reconstructs
    the forwarded body from it and REFUSES fail-closed unless that instruction
    reproduces the OPERATOR-NAMED approval digest (`approval_binding`). `approved_digest`
    is bound to that operator-named digest - not a journal-resident byte anchor - so an
    attacker who rewrites BOTH the parked `prompt` and `prompt_bytes_digest`
    consistently, leaving the operator digest unchanged, still cannot get altered
    content forwarded: the body is derived from operator-covered material, and any
    edit to a covered field breaks the digest match. Old-shape records (no structured
    instruction) refuse (AS-6). The CLI performs the same check BEFORE it
    transitions/audits, so in the normal path this is defense in depth.
    """
    prompt = pending.get("prompt")
    record: dict[str, Any] = {
        "approved": True,
        "cycle": pending.get("cycle"),
        "decision": pending.get("decision"),
        "reviewed_checkpoint_id": pending.get("reviewed_checkpoint_id"),
        "approved_at_utc": to_utc_iso(),
        "prior_digest": approval_binding,
    }
    if isinstance(prompt, str) and prompt:
        # Reconstruct + verify against the OPERATOR-NAMED digest; raises fail-closed.
        expected_body = verify_covered_instruction(
            pending.get("approved_instruction"), approval_binding, prompt,
            pending.get("prompt_bytes_digest"))
        record["approved_instruction"] = dict(pending["approved_instruction"])
        # Persist the canonical reconstruction (== the verified parked bytes), never a
        # possibly-tampered journal value.
        record["prompt"] = expected_body
        # Bind to the OPERATOR-NAMED approval digest itself (R136), now that the body
        # is a verified pure function of the material that digest covers.
        record["approved_digest"] = approval_binding
    journal.set_state(pending_prompt_key(run_id), record)

