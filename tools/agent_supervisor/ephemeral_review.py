#!/usr/bin/env python3
"""The operational fresh-ephemeral Codex review loop (D-010 0A.1; AD-027/087/088).

`codex_reviewer.CodexReviewer` launches one fresh, read-only Codex process and
returns one validated decision. This module makes that an OPERATIONAL loop end to
end (0A.1): it admits the packet through the AD-083 content guard and the 0A.4
budget, runs the review, and leaves a DURABLE record holding the decision, the
evidence references, the model identity, the usage telemetry, and the digest
(0A.1 item 7). Nothing here activates autonomy or weakens the shadow-only posture:
it records and returns, like the rest of the supervisor.

Three directive mechanisms live here:

* AD-027 (no shared state): every review is a brand-new process; the record
  proves each review is independent of the last (distinct packet digest, no
  carried conversation).
* AD-087 (no duplicate investigation): the bounded packet lets Codex challenge
  the worker without inheriting its context; when Codex cites a source the packet
  did not supply, the record notes which and why (0A.6).
* AD-088 (role honesty): the record distinguishes the read-only `reviewer` from
  the writable `worker` fallback (0A.5). This loop only ever runs the reviewer;
  the worker role is a recorded EXCEPTION built by `record_worker_fallback`, never
  activated here.
"""
from __future__ import annotations

import dataclasses
import json
import os
import pathlib
from typing import Any, Callable, Mapping, Sequence

from .models import USAGE_UNKNOWN, digest_of, to_utc_iso
from .redaction import redact_structure
from .review_packet import ReviewBudget, assess_evidence_packet, guard_packet

RECORD_VERSION = "1.0.0"

#: P6 (M0-T061): reviewer `error_code`s that mean the DISPATCHED reviewer returned
#: NOTHING adjudicable - it timed out, produced no decision file, or the provider
#: rejected the turn (HTTP 400 -> `turn.failed`). These are the "gate dispatched,
#: no verdict returned" cases the P6 re-dispatch guard exists for: absent output
#: that must never be indistinguishable from a clean review.
#:
#: Deliberately EXCLUDED: `schema_retry_exhausted` (and per-decision validation
#: codes). Those mean the reviewer DELIVERED output that its OWN bounded schema
#: retry already adjudicated and fail-closed into a distinct, sealed, ok=False
#: record (the gate-reviewed G3 M-2 invariant in
#: `test_agent_supervisor_ephemeral_review`). That is not "absent evidence treated
#: as passing evidence", so it is not re-dispatched or relabeled here.
SILENT_NO_VERDICT_CODES: frozenset[str] = frozenset({
    "review_timeout", "missing_decision_file", "provider_rejected_request",
})

REVIEWER_ROLE = "reviewer"
#: AD-088 / 0A.5: the writable Codex worker fallback. A recorded EXCEPTION, never
#: activated by this loop - `conduct_ephemeral_review` refuses any non-reviewer
#: role, and worker records are built only by `record_worker_fallback`.
WORKER_ROLE = "worker"
ROLES = (REVIEWER_ROLE, WORKER_ROLE)


class EphemeralReviewError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclasses.dataclass
class ReviewRecord:
    """One durable record of a fresh ephemeral review (0A.1 item 7).

    Mutable only so `finalize()` can redact and digest-seal it in one place, the
    way `evidence.EvidencePacket` does. Once finalized the `record_digest` binds
    the stored bytes, so tampering is detectable via `verify_record`.
    """

    record_version: str
    run_id: str
    reviewed_task_id: str
    reviewed_checkpoint_id: str
    role: str
    created_at_utc: str
    ok: bool
    decision: dict[str, Any] | None
    decision_value: str
    decision_digest: str
    evidence_refs: list[dict[str, Any]]
    model_used: str
    model_selection_digest: str
    model_self_report_mismatch: str
    usage_telemetry: dict[str, Any] | str
    packet_digest: str
    budget: dict[str, Any]
    guard_findings: list[dict[str, Any]]
    reopened_sources: list[dict[str, Any]]
    independence: dict[str, Any]
    attempts: int
    returncode: int
    error_code: str
    error_message: str
    notify_events: list[str]
    redaction_count: int = 0
    redaction_labels: tuple[str, ...] = ()
    record_digest: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        data["redaction_labels"] = list(self.redaction_labels)
        return data

    def finalize(self) -> "ReviewRecord":
        """Redact untrusted content, then seal with a content digest."""
        body = self.to_dict()
        for key in ("record_digest", "redaction_count", "redaction_labels"):
            body.pop(key, None)
        redacted = redact_structure(body)
        stored = redacted.value
        stored["redaction_count"] = redacted.count
        stored["redaction_labels"] = list(redacted.labels)
        stored["record_digest"] = digest_of(stored)
        fields = {f.name for f in dataclasses.fields(ReviewRecord)}
        clean = {k: v for k, v in stored.items()
                 if k in fields and k != "redaction_labels"}
        record = ReviewRecord(**clean)
        record.redaction_labels = tuple(stored["redaction_labels"])
        return record


def verify_record(stored: Mapping[str, Any]) -> bool:
    """True iff the stored record's digest matches its content (tamper check)."""
    body = {k: v for k, v in stored.items() if k != "record_digest"}
    if isinstance(body.get("redaction_labels"), tuple):
        body["redaction_labels"] = list(body["redaction_labels"])
    return digest_of(body) == stored.get("record_digest")


def _packet_digest(packet: Mapping[str, Any]) -> str:
    recorded = packet.get("packet_digest")
    if isinstance(recorded, str) and recorded:
        return recorded
    return digest_of(packet)


def _independence_proof(packet_digest: str, *,
                        prior: "ReviewRecord | None") -> dict[str, Any]:
    proof: dict[str, Any] = {
        "fresh_process_per_review": True,
        "shares_conversation_state": False,
        "packet_digest": packet_digest,
        "note": "each review is a brand-new read-only process; no Codex "
                "conversation is carried between reviews (0A.1/AD-027)",
    }
    if prior is not None:
        proof["prior_packet_digest"] = prior.packet_digest
        proof["prior_record_digest"] = prior.record_digest
        proof["distinct_from_prior"] = prior.packet_digest != packet_digest
    return proof


def _reopened_sources(evidence_refs: Sequence[Mapping[str, Any]],
                      packet_source_paths: Sequence[str]) -> list[dict[str, Any]]:
    """Sources cited in the decision that the packet did NOT supply (AD-087/0A.6).

    Codex may reopen authoritative source to verify the worker; when it cites a
    path the bounded packet did not contain, the record notes it and why, so a
    reviewer can see Codex went beyond the packet rather than silently re-running
    the worker's whole investigation.
    """
    provided = {str(p) for p in packet_source_paths}
    out: list[dict[str, Any]] = []
    for ref in evidence_refs:
        if not isinstance(ref, Mapping):
            continue
        path = ref.get("path")
        if isinstance(path, str) and path and path not in provided:
            out.append({
                "path": path,
                "reason": "cited in the decision but not supplied in the review "
                          "packet; Codex reopened authoritative source to verify "
                          "the worker (0A.6/AD-087)"})
    return out


class ReviewJournal:
    """An append-only durable store of sealed review records (0A.1 item 7)."""

    def __init__(self, path: str | os.PathLike[str], *, fsync: bool = True) -> None:
        self.path = pathlib.Path(path)
        self._fsync = fsync

    def append(self, record: ReviewRecord) -> ReviewRecord:
        sealed = record if record.record_digest else record.finalize()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(sealed.to_dict(), sort_keys=True, ensure_ascii=False)
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            handle.flush()
            if self._fsync:
                os.fsync(handle.fileno())
        return sealed

    def load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        out: list[dict[str, Any]] = []
        for line in self.path.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if line:
                out.append(json.loads(line))
        return out

    def verify(self) -> bool:
        return all(verify_record(row) for row in self.load())


def _refusal_record(*, error_code: str, error_message: str, run_id: str,
                    task_id: str, checkpoint_id: str, packet_digest: str,
                    budget: dict[str, Any], guard_findings: list[dict[str, Any]],
                    prior: "ReviewRecord | None", now: Callable[[], str],
                    journal: "ReviewJournal | None") -> ReviewRecord:
    """A durable record for a review that was REFUSED before any process ran."""
    record = ReviewRecord(
        record_version=RECORD_VERSION, run_id=run_id,
        reviewed_task_id=task_id, reviewed_checkpoint_id=checkpoint_id,
        role=REVIEWER_ROLE, created_at_utc=now(), ok=False,
        decision=None, decision_value="", decision_digest="",
        evidence_refs=[], model_used="", model_selection_digest="",
        model_self_report_mismatch="", usage_telemetry=USAGE_UNKNOWN,
        packet_digest=packet_digest, budget=budget, guard_findings=guard_findings,
        reopened_sources=[],
        independence=_independence_proof(packet_digest, prior=prior),
        attempts=0, returncode=0, error_code=error_code,
        error_message=error_message, notify_events=[]).finalize()
    if journal is not None:
        journal.append(record)
    return record


def _silent_reviewer_record(
    *, run_id: str, task_id: str, checkpoint_id: str, packet_digest: str,
    budget: dict[str, Any], guard_findings: list[dict[str, Any]],
    first_outcome: Any, redispatch_outcome: Any, prior: "ReviewRecord | None",
    now: Callable[[], str], journal: "ReviewJournal | None") -> ReviewRecord:
    """A hard fail-closed PAUSE/STOP record for a reviewer that returned NO verdict.

    P6 (M0-T061): under unattended actuation a gate that was DISPATCHED but
    returned no decision - on both the first dispatch and the single controlled
    re-dispatch - must never be indistinguishable from a clean review ("absent
    evidence treated as passing evidence"). This seals a DISTINCT, VISIBLE
    fail-closed record (ok=False, decision=None, its own `error_code`, a notify
    event) rather than proceeding. It carries the underlying outcome's own failure
    code, message, and usage so the silence is diagnosable, and is sealed and
    journaled exactly like `_refusal_record` and every other durable review record.
    """
    underlying_code = (redispatch_outcome.error_code
                       or first_outcome.error_code or "no_decision")
    underlying_message = (redispatch_outcome.error_message
                          or first_outcome.error_message or "")
    message = (
        "the dispatched reviewer returned NO verdict (outcome.decision is None) on "
        "both the first dispatch AND the single controlled re-dispatch; fail-closed "
        "PAUSE/STOP rather than treating absent evidence as passing evidence (P6). "
        f"underlying reviewer failure [{underlying_code}]: {underlying_message}")
    record = ReviewRecord(
        record_version=RECORD_VERSION, run_id=run_id,
        reviewed_task_id=task_id, reviewed_checkpoint_id=checkpoint_id,
        role=REVIEWER_ROLE, created_at_utc=now(), ok=False,
        decision=None, decision_value="", decision_digest="",
        evidence_refs=[], model_used=redispatch_outcome.model_used,
        model_selection_digest=redispatch_outcome.selection_digest,
        model_self_report_mismatch="",
        usage_telemetry=getattr(redispatch_outcome, "usage_telemetry", USAGE_UNKNOWN),
        packet_digest=packet_digest, budget=budget, guard_findings=guard_findings,
        reopened_sources=[],
        independence=_independence_proof(packet_digest, prior=prior),
        attempts=first_outcome.attempts + redispatch_outcome.attempts,
        returncode=redispatch_outcome.returncode,
        error_code="reviewer_silent_no_verdict", error_message=message,
        notify_events=["reviewer_silent_redispatched",
                       "reviewer_silent_no_verdict",
                       "reviewer_paused_fail_closed"]).finalize()
    if journal is not None:
        journal.append(record)
    return record


def conduct_ephemeral_review(
    reviewer: Any,
    packet: Mapping[str, Any],
    *,
    reviewed_task_id: str,
    reviewed_checkpoint_id: str,
    budget: ReviewBudget,
    model_context_window: int | None,
    run_id: str = "",
    packet_source_paths: Sequence[str] = (),
    role: str = REVIEWER_ROLE,
    guard_strip: bool = False,
    prior_record: "ReviewRecord | None" = None,
    journal: "ReviewJournal | None" = None,
    now: Callable[[], str] = to_utc_iso,
) -> ReviewRecord:
    """Run one fresh ephemeral review end to end and return a durable record.

    Order is fail-closed: content guard first (never send prohibited material),
    then the 0A.4 budget (never send an oversized packet), then the fresh
    read-only process, then the sealed record. A guard rejection or a budget
    overflow returns a durable REFUSAL record and never launches a process.
    """
    if role != REVIEWER_ROLE:
        raise EphemeralReviewError(
            "role_not_activatable",
            f"the ephemeral-review loop runs only the read-only {REVIEWER_ROLE!r} "
            f"role; a Codex {role!r} (writable fallback) is a separate authorized "
            f"exception (0A.5) and is never activated here (AD-088)")

    packet_dict = dict(packet)

    # 1. AD-083 prohibited-content guard (fail closed).
    guard = guard_packet(packet_dict, current_task_id=reviewed_task_id,
                         strip=guard_strip)
    guard_findings = [f.to_dict() for f in guard.findings]
    if guard.rejected:
        return _refusal_record(
            error_code="prohibited_content",
            error_message="the packet carried prohibited whole-material a normal "
                          "review must never receive (0A.1/AD-083); refused",
            run_id=run_id, task_id=reviewed_task_id,
            checkpoint_id=reviewed_checkpoint_id,
            packet_digest=_packet_digest(packet_dict), budget={},
            guard_findings=guard_findings, prior=prior_record, now=now,
            journal=journal)
    packet_dict = guard.packet or packet_dict

    # 2. 0A.4 budget (fail closed; refuse over-ceiling with guidance).
    assessment = assess_evidence_packet(
        packet_dict, budget=budget, model_context_window=model_context_window)
    packet_digest = _packet_digest(packet_dict)
    if not assessment.within_ceiling:
        return _refusal_record(
            error_code="packet_over_budget",
            error_message="the review packet exceeds the 0A.4 effective ceiling; "
                          "refused with split/summarize guidance rather than sent "
                          "or silently trimmed (0A.4 rule 5)",
            run_id=run_id, task_id=reviewed_task_id,
            checkpoint_id=reviewed_checkpoint_id, packet_digest=packet_digest,
            budget=assessment.to_dict(), guard_findings=guard_findings,
            prior=prior_record, now=now, journal=journal)

    # 3. Fresh, read-only ephemeral process -> one validated decision.
    # P6 (M0-T061): under unattended actuation a reviewer that was DISPATCHED but
    # returned NOTHING adjudicable (timeout / no decision file / provider-rejected
    # turn -> decision is None AND a SILENT_NO_VERDICT_CODES error) must never be
    # indistinguishable from a clean review. Detect that silence, allow EXACTLY ONE
    # controlled re-dispatch of the same packet, then fail closed to a hard
    # PAUSE/STOP record. A DELIVERED verdict (`decision is not None`) - including a
    # FAIL/BLOCKED HALT_UNSAFE/STOP_FOR_OWNER - is never re-dispatched; neither is
    # an already-bounded-adjudicated failure (schema_retry_exhausted / validation
    # exhaustion), which is a distinct sealed ok=False record on its own.
    extra_notify: list[str] = []
    outcome = reviewer.review(
        packet_dict, expected_task_id=reviewed_task_id,
        expected_checkpoint_id=reviewed_checkpoint_id)
    if outcome.decision is None and outcome.error_code in SILENT_NO_VERDICT_CODES:
        # No verdict returned. Bounded detection -> EXACTLY ONE controlled
        # re-dispatch of the same packet (a fresh read-only process).
        redispatch = reviewer.review(
            packet_dict, expected_task_id=reviewed_task_id,
            expected_checkpoint_id=reviewed_checkpoint_id)
        if redispatch.decision is None:
            # Still silent after the one retry -> hard fail-closed PAUSE/STOP.
            # Never downgraded to "proceed"/ok=True.
            return _silent_reviewer_record(
                run_id=run_id, task_id=reviewed_task_id,
                checkpoint_id=reviewed_checkpoint_id, packet_digest=packet_digest,
                budget=assessment.to_dict(), guard_findings=guard_findings,
                first_outcome=outcome, redispatch_outcome=redispatch,
                prior=prior_record, now=now, journal=journal)
        # The single re-dispatch DELIVERED a verdict; proceed normally, but tag
        # the sealed record so the recovered-from-silence path stays visible.
        outcome = redispatch
        extra_notify.append("reviewer_redispatched_after_silence")

    # 4. Seal the durable record (0A.1 item 7).
    decision = outcome.decision
    evidence_refs = list(decision.evidence_refs) if decision is not None else []
    record = ReviewRecord(
        record_version=RECORD_VERSION, run_id=run_id,
        reviewed_task_id=reviewed_task_id,
        reviewed_checkpoint_id=reviewed_checkpoint_id, role=REVIEWER_ROLE,
        created_at_utc=now(), ok=outcome.ok,
        decision=decision.to_dict() if decision is not None else None,
        decision_value=decision.decision if decision is not None else "",
        decision_digest=outcome.decision_digest, evidence_refs=evidence_refs,
        model_used=outcome.model_used,
        model_selection_digest=outcome.selection_digest,
        model_self_report_mismatch=outcome.model_self_report_mismatch,
        usage_telemetry=getattr(outcome, "usage_telemetry", USAGE_UNKNOWN),
        packet_digest=packet_digest, budget=assessment.to_dict(),
        guard_findings=guard_findings,
        reopened_sources=_reopened_sources(evidence_refs, packet_source_paths),
        independence=_independence_proof(packet_digest, prior=prior_record),
        attempts=outcome.attempts, returncode=outcome.returncode,
        error_code=outcome.error_code, error_message=outcome.error_message,
        notify_events=list(outcome.notify_events) + extra_notify).finalize()
    if journal is not None:
        journal.append(record)
    return record


def record_worker_fallback(
    *, run_id: str, reviewed_task_id: str, reviewed_checkpoint_id: str,
    model_used: str = "", note: str = "", now: Callable[[], str] = to_utc_iso,
    journal: "ReviewJournal | None" = None,
) -> ReviewRecord:
    """Build (never activate) a durable record marking a Codex WORKER fallback.

    0A.5/AD-088: Codex may become a writable worker only under explicit authorized
    conditions, and the supervisor must RECORD that Codex acted as a worker rather
    than a reviewer. This builds that record so the role is auditable. It launches
    nothing and grants no write access - activation is a separate authorized act.
    """
    record = ReviewRecord(
        record_version=RECORD_VERSION, run_id=run_id,
        reviewed_task_id=reviewed_task_id,
        reviewed_checkpoint_id=reviewed_checkpoint_id, role=WORKER_ROLE,
        created_at_utc=now(), ok=False, decision=None, decision_value="",
        decision_digest="", evidence_refs=[], model_used=model_used,
        model_selection_digest="", model_self_report_mismatch="",
        usage_telemetry=USAGE_UNKNOWN, packet_digest="", budget={},
        guard_findings=[], reopened_sources=[],
        independence={"fresh_process_per_review": True,
                      "shares_conversation_state": False,
                      "note": note or "Codex acted as a writable worker under an "
                      "authorized 0A.5 exception; recorded, not activated here"},
        attempts=0, returncode=0, error_code="worker_fallback_recorded",
        error_message=note or "recorded worker-role exception (AD-088/0A.5)",
        notify_events=["codex_worker_fallback_recorded"]).finalize()
    if journal is not None:
        journal.append(record)
    return record
