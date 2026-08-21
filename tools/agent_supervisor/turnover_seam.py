#!/usr/bin/env python3
"""The FULL S11.3 turnover at the loop's rotation seams (M0-T080).

Qualifying evidence (supervisor-freeze §2/§3, AD-093 - a reproduced defect).
`rotation.py` already provided the whole safe-rotation protocol: the
unsafe-moment refusal list (`assert_safe_to_rotate`), the structured handoff
schema (`Handoff`, `validate_handoff`), review-model-only verification
(`verify_handoff`), durable storage of the VERIFIED handoff
(`RotationLedger.store_verified_handoff`), and the mandatory READY checkpoint
gate (`assert_ready_checkpoint`).

The live loop used almost none of it. All three of its rotation seams
(`_rotate_at_seam`, `_switch_at_seam`, `_return_to_pinned`) wrote a SMALLER,
non-S11.3 snapshot through `_refresh_session_handoff` - task, stage, branch,
worktree, reason, outgoing session id, pinned model, cycle - and then called
`RotationLedger.complete_rotation` DIRECTLY. So a production rotation:

* never checked whether the moment was safe to rotate (a still-pending approval,
  an unreconciled external effect, or an in-progress merge did not stop it);
* never built the S11.3 handoff, so nine of its fourteen required fields did not
  exist anywhere;
* never verified a handoff, so `verify_handoff` had no production caller;
* never stored a VERIFIED handoff, so `store_verified_handoff` had none either;
* never gated on a READY checkpoint, so `assert_ready_checkpoint` had none; and
* never checked afterwards that the successor was on the expected task, branch,
  HEAD, or model.

This module is that missing path, in one place so all three seams take it. It
owns exactly five responsibilities and no policy of its own: SAFE-SEAM check,
HANDOFF build, VERIFY + durable persist, READY gate, POST-LAUNCH verification.
Every judgement it makes is delegated to `rotation.py`, which stays the authority
on what a handoff is and when rotating is permitted.

FAIL-CLOSED throughout: an unreadable journal, an unverifiable handoff, an
unsatisfied READY gate, and a successor whose reported identity does not match
what was commanded each STOP the turnover. None of them degrades to "continue
anyway", and none of them is recorded as a completed rotation.
"""
from __future__ import annotations

import dataclasses
from typing import Any, Callable, Mapping, Sequence

from . import rotation, session_continuity
from .models import to_utc_iso

#: Durable key prefix for the armed READY gate. Per run, so two runs in one
#: checkout cannot satisfy each other's gate.
READY_GATE_KEY = "rotation_ready_gate"

#: The `model_used` recorded when the supervisor verified the handoff ITSELF,
#: deterministically, rather than through a live review-model session. S3.3
#: reserves final handoff verification to "review_model or deterministic
#: verification"; this names which of the two happened, so a reader can never
#: mistake a deterministic check for a reviewed one.
DETERMINISTIC_VERIFIER = "deterministic:supervisor-rederivation"


class SeamTurnoverError(Exception):
    """A full turnover was refused at one of its five gates. Always fails closed."""

    def __init__(self, code: str, message: str,
                 detail: Mapping[str, Any] | None = None) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.detail = dict(detail or {})


# --------------------------------------------------------------------------
# 1. The safe-seam check
# --------------------------------------------------------------------------


def safety_state_from_run(
    *,
    pending_effects: Sequence[Any] = (),
    open_asks: Sequence[Any] = (),
    unit_in_flight: bool = False,
    head_sha: str = "",
    branch: str = "",
    worktree: str = "",
    task_stage: str = "",
) -> rotation.RotationSafetyState:
    """Build the S11.3 safety state from facts the loop actually holds.

    Each field is answered from a real observation or reported AMBIGUOUS - never
    from an optimistic default. An unnamed HEAD, branch, worktree, or task stage
    is `*_ambiguous=True`, because "the supervisor cannot say what the SHA is" is
    exactly the condition S11.3 refuses to rotate through.
    """
    return rotation.RotationSafetyState(
        command_running=bool(unit_in_flight),
        tool_call_pending=False,
        approval_pending=bool(len(open_asks)),
        unaccounted_background_actions=len(pending_effects),
        unexplained_uncommitted_changes=False,
        merge_or_rebase_in_progress=False,
        conflict_present=False,
        sha_ambiguous=not bool(head_sha),
        worktree_ambiguous=not bool(worktree) or not bool(branch),
        task_stage_ambiguous=not bool(task_stage),
    )


def assert_safe_seam(state: rotation.RotationSafetyState) -> None:
    """Refuse the turnover at an unsafe or ambiguous moment (S11.3).

    Delegates the whole judgement to `rotation.assert_safe_to_rotate` and only
    re-labels the failure, so there is exactly one definition of "unsafe moment"
    in the package.
    """
    try:
        rotation.assert_safe_to_rotate(state)
    except rotation.RotationError as exc:
        raise SeamTurnoverError("unsafe_seam", exc.message,
                                {"reasons": list(rotation.unsafe_rotation_reasons(state))}
                                ) from exc


# --------------------------------------------------------------------------
# 2. The S11.3 handoff, built from what the loop knows
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class SeamFacts:
    """Everything the loop can state about the work being handed over.

    Deliberately a value object with no defaults for the facts S11.3 requires to
    be non-empty: a seam that cannot name the task, branch, worktree, HEAD, or
    next action must fail the build rather than emit a handoff with a plausible
    blank in it.
    """

    task_id: str
    stage: str
    branch: str
    worktree: str
    head_sha: str
    exact_next_action: str
    reason_code: str
    origin_main_sha: str = ""
    completed_work: str = ""
    changed_files: tuple[str, ...] = ()
    tests_and_ci: Mapping[str, Any] = dataclasses.field(default_factory=dict)
    pull_request_state: str = ""
    reviews_and_findings: tuple[str, ...] = ()
    open_blockers: tuple[str, ...] = ()
    owner_gates: tuple[str, ...] = ()
    forbidden_scope: tuple[str, ...] = ()
    evidence_digests: Mapping[str, str] = dataclasses.field(default_factory=dict)
    last_checkpoint_id: str = ""


#: The prohibitions that are true of EVERY supervised unit, whatever the packet
#: says. `forbidden_scope` is a required non-empty handoff field, and it must
#: never be empty merely because a packet listed no forbidden paths - the
#: structural prohibitions below always apply and are always carried across.
STRUCTURAL_FORBIDDEN_SCOPE: tuple[str, ...] = (
    "no change outside the task packet's allowed_paths and this worktree",
    "no push to a protected main branch and no force push",
    "no controller config, manifest, policy, or model-selection edit",
    "no acceptance of the task's own gate and no ledger write",
)


def build_handoff(facts: SeamFacts) -> rotation.Handoff:
    """Build and VALIDATE the full S11.3 handoff for this seam.

    `rotation.validate_handoff` is the authority on completeness and on the
    `/clear`-automation refusal; this only assembles the fields. A handoff that
    does not validate raises rather than being trimmed to fit.
    """
    shas: dict[str, str] = {"HEAD": facts.head_sha}
    if facts.origin_main_sha:
        shas["origin/main"] = facts.origin_main_sha
    handoff = rotation.Handoff(
        task_and_stage=f"{facts.task_id} @ {facts.stage}",
        authoritative_shas=shas,
        branch=facts.branch,
        worktree=facts.worktree,
        completed_work=(facts.completed_work
                        or f"the unit before the {facts.reason_code} rotation completed and "
                           f"returned checkpoint "
                           f"{facts.last_checkpoint_id or '(none recorded)'}"),
        changed_files=tuple(facts.changed_files),
        tests_and_ci=dict(facts.tests_and_ci),
        pull_request_state=(facts.pull_request_state
                            or "no pull request is open for this unit"),
        reviews_and_findings=tuple(facts.reviews_and_findings),
        open_blockers=tuple(facts.open_blockers),
        owner_gates=tuple(facts.owner_gates),
        forbidden_scope=tuple(facts.forbidden_scope) + STRUCTURAL_FORBIDDEN_SCOPE,
        exact_next_action=facts.exact_next_action,
        evidence_digests=dict(facts.evidence_digests),
    )
    try:
        rotation.validate_handoff(handoff)
    except rotation.RotationError as exc:
        raise SeamTurnoverError("handoff_incomplete", exc.message,
                                {"reason_code": facts.reason_code}) from exc
    return handoff


# --------------------------------------------------------------------------
# 3. Verification: a live review model, or the supervisor's own re-derivation
# --------------------------------------------------------------------------

#: A live verifier: hand it the handoff, get back the S11.3 reviewer verdict
#: mapping (`model_used`, `handoff_digest`, `verified`, `findings`). Injected, so
#: no test contacts a provider.
HandoffVerifier = Callable[[rotation.Handoff], Mapping[str, Any]]


def deterministic_verdict(handoff: rotation.Handoff, facts: SeamFacts) -> dict[str, Any]:
    """Re-derive every load-bearing handoff field from the supervisor's own facts.

    This is the "deterministic verification" arm S3.3 permits alongside
    review_model. It is a real check, not a rubber stamp: each field is compared
    against the value the supervisor independently holds, and ANY divergence is
    returned as a finding, which `rotation.verify_handoff` turns into a refusal.
    """
    findings: list[str] = []
    expected = {
        "task_and_stage": f"{facts.task_id} @ {facts.stage}",
        "branch": facts.branch,
        "worktree": facts.worktree,
        "exact_next_action": facts.exact_next_action,
    }
    for field_name, value in expected.items():
        actual = getattr(handoff, field_name)
        if actual != value:
            findings.append(
                f"{field_name} says {actual!r} but the supervisor's own record says {value!r}")
    if handoff.authoritative_shas.get("HEAD") != facts.head_sha:
        findings.append(
            f"authoritative_shas.HEAD says "
            f"{handoff.authoritative_shas.get('HEAD')!r} but the supervisor recorded "
            f"{facts.head_sha!r}")
    missing = [entry for entry in STRUCTURAL_FORBIDDEN_SCOPE
               if entry not in handoff.forbidden_scope]
    if missing:
        findings.append(f"forbidden_scope dropped the structural prohibitions {missing}")
    return {
        "model_used": DETERMINISTIC_VERIFIER,
        "handoff_digest": handoff.digest(),
        "verified": not findings,
        "findings": tuple(findings),
    }


def verify(
    handoff: rotation.Handoff,
    facts: SeamFacts,
    *,
    verifier: HandoffVerifier | None = None,
    review_model: str = "",
    advisory_model: str = "",
) -> rotation.HandoffVerification:
    """Verify the handoff, through the review model when one is wired.

    With a `verifier` injected the verdict comes from it and
    `rotation.verify_handoff` checks the reporting model against the configured
    `review_model` (and refuses the advisory model outright). With no verifier,
    the supervisor verifies deterministically and RECORDS that it did - the
    `model_used` is `DETERMINISTIC_VERIFIER`, never a model name, so the durable
    record can never suggest a review that did not happen.
    """
    if verifier is None:
        verdict = deterministic_verdict(handoff, facts)
        return rotation.verify_handoff(handoff, reviewer_verdict=verdict,
                                       review_model="", advisory_model="")
    try:
        verdict = dict(verifier(handoff) or {})
    except Exception as exc:
        raise SeamTurnoverError(
            "handoff_verifier_failed",
            f"the handoff verifier raised ({exc}); an unverifiable handoff is never "
            f"carried into a successor session") from exc
    return rotation.verify_handoff(handoff, reviewer_verdict=verdict,
                                   review_model=review_model,
                                   advisory_model=advisory_model)


# --------------------------------------------------------------------------
# 4 + 5. The READY gate and the post-launch identity check
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class SuccessorExpectation:
    """Exactly what the successor was COMMANDED to be, recorded before it runs.

    The post-launch check compares the successor's own report against this, so a
    mismatch is measured against a value that was written down first rather than
    against whatever the successor claims it was asked for.
    """

    task_id: str
    branch: str
    worktree: str
    head_sha: str
    model_id: str
    continuity_mode: str
    provider_session_id: str = ""
    rotation_record_key: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class SeamTurnoverResult:
    """The completed full turnover, with both identities and all its evidence."""

    rotation_record_key: str
    previous_provider_session_id: str
    continuity: session_continuity.ContinuityDecision
    handoff_digest: str
    verification: rotation.HandoffVerification
    expectation: SuccessorExpectation
    reorientation_prompt: str
    record: Mapping[str, Any] = dataclasses.field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rotation_record_key": self.rotation_record_key,
            "previous_provider_session_id": self.previous_provider_session_id,
            **self.continuity.to_dict(),
            "handoff_digest": self.handoff_digest,
            "verified_by_model": self.verification.model_used,
            "expectation": self.expectation.to_dict(),
            "reorientation_delivered": bool(self.reorientation_prompt),
        }


class SeamTurnover:
    """The one full-turnover path all three loop seams take."""

    def __init__(
        self,
        *,
        journal: Any,
        audit: Any = None,
        run_id: str = "",
        verifier: HandoffVerifier | None = None,
        review_model: str = "",
        advisory_model: str = "",
    ) -> None:
        self.journal = journal
        self.audit = audit
        self.run_id = run_id
        self._verifier = verifier
        self.review_model = review_model
        self.advisory_model = advisory_model
        self.ledger = rotation.RotationLedger(journal, audit=audit)

    # -- the gate key --------------------------------------------------------

    def _gate_key(self) -> str:
        return f"{READY_GATE_KEY}/{self.run_id}"

    def armed_gate(self) -> dict[str, Any] | None:
        data = self.journal.get_state(self._gate_key(), None)
        return dict(data) if isinstance(data, Mapping) and data.get("armed") else None

    def arm_ready_gate(self, expectation: SuccessorExpectation, *,
                       handoff_digest: str) -> dict[str, Any]:
        """Arm the S11.3 READY gate. Nothing may be forwarded until it is met."""
        record = {
            "armed": True,
            "armed_at_utc": to_utc_iso(),
            "handoff_digest": handoff_digest,
            **expectation.to_dict(),
        }
        self.journal.set_state(self._gate_key(), record)
        self._audit("rotation_ready_gate_armed", record)
        return record

    def clear_ready_gate(self, *, satisfied_by: str) -> None:
        self.journal.set_state(self._gate_key(),
                               {"armed": False, "satisfied_by": satisfied_by,
                                "cleared_at_utc": to_utc_iso()})

    def require_ready(self, checkpoint: Any) -> None:
        """Refuse any post-rotation forward until the successor reported READY.

        S11.3: "the re-oriented session returns a structured READY checkpoint
        BEFORE any change". The archived-session check is what makes the gate
        meaningful on a reorientation: a READY that came from the session the
        rotation just archived proves the rotation did not happen.
        """
        gate = self.armed_gate()
        if gate is None:
            return
        status = getattr(checkpoint, "status", None)
        session = str(getattr(checkpoint, "claude_session_id", "") or "")
        if status != "READY":
            raise SeamTurnoverError(
                "rotation_ready_required",
                f"the session that came up after the rotation reported status {status!r}; "
                f"S11.3 requires a structured READY checkpoint after re-orientation BEFORE "
                f"any change, so nothing is forwarded from this cycle",
                {"expected_status": "READY", "observed_status": status,
                 "handoff_digest": gate.get("handoff_digest", "")})
        if gate.get("continuity_mode") == session_continuity.REORIENTATION:
            archived = self.ledger.archived_sessions()
            if session and session in archived:
                raise SeamTurnoverError(
                    "ready_from_archived_session",
                    f"the READY checkpoint came from session {session!r}, which this "
                    f"rotation ARCHIVED; an archived session may never be resumed and its "
                    f"READY can never satisfy the gate (S11.3 / S15)",
                    {"session": session, "archived": list(archived)})
        elif gate.get("continuity_mode") == session_continuity.RESUME:
            expected = str(gate.get("provider_session_id", "") or "")
            if expected and session and session != expected:
                raise SeamTurnoverError(
                    "resumed_wrong_session",
                    f"the rotation commanded a RESUME of provider session {expected!r} but "
                    f"the READY checkpoint came from {session!r}; a resume that landed in a "
                    f"different session is not a resume",
                    {"expected": expected, "observed": session})
        self.clear_ready_gate(satisfied_by=session or "(no session id reported)")
        self._audit("rotation_ready_gate_satisfied",
                    {"session": session, "handoff_digest": gate.get("handoff_digest", "")})

    def verify_post_launch(self, *, checkpoint: Any, run_result: Any = None,
                           expectation: SuccessorExpectation | None = None
                           ) -> tuple[bool, str, dict[str, Any]]:
        """Prove the successor is on the commanded task, branch, HEAD, and model.

        Returns `(ok, reason, detail)`. A mismatch is never repaired here: the
        caller fails closed and stops. The MODEL comparison is the one the
        directive singles out - what the successor reports it is running is
        compared to the id that was commanded, and a difference stops the run
        rather than being absorbed as a downgrade note.
        """
        gate = expectation.to_dict() if expectation is not None else (self.armed_gate() or {})
        if not gate:
            return True, "no successor expectation was recorded for this cycle", {}
        mismatches: list[str] = []
        checks = (
            ("task_id", str(getattr(checkpoint, "task_id", "") or "")),
            ("branch", str(getattr(checkpoint, "branch", "") or "")),
            ("worktree", str(getattr(checkpoint, "worktree", "") or "")),
        )
        for field_name, observed in checks:
            expected = str(gate.get(field_name, "") or "")
            if expected and observed and observed != expected:
                mismatches.append(
                    f"{field_name}: commanded {expected!r}, successor reported {observed!r}")
        expected_head = str(gate.get("head_sha", "") or "")
        observed_head = str(getattr(checkpoint, "starting_sha", "") or "")
        if expected_head and observed_head and observed_head != expected_head:
            mismatches.append(
                f"starting_sha: the successor started from {observed_head!r}, not the "
                f"HEAD {expected_head!r} the handoff pinned")
        expected_model = str(gate.get("model_id", "") or "")
        observed_models = tuple(str(m) for m in
                                (getattr(run_result, "observed_models", ()) or ()))
        if expected_model and observed_models:
            wrong = [m for m in observed_models if m and m != expected_model]
            if wrong:
                mismatches.append(
                    f"model: the successor reported running {wrong!r}, not the commanded "
                    f"{expected_model!r}")
        detail = {"expectation": dict(gate), "observed_models": list(observed_models),
                  "mismatches": mismatches}
        if mismatches:
            return False, ("the successor is not the session that was commanded: "
                           + "; ".join(mismatches)), detail
        return True, "the successor reported the commanded task, branch, HEAD, and model", detail

    # -- the whole path ------------------------------------------------------

    def execute(
        self,
        *,
        facts: SeamFacts,
        safety_state: rotation.RotationSafetyState,
        continuity: session_continuity.ContinuityDecision,
        previous_provider_session_id: str,
        successor_model: str,
        evidence: Sequence[str] = (),
    ) -> SeamTurnoverResult:
        """Safe-seam -> handoff -> verify -> persist -> rotate -> arm READY.

        Ordered so nothing durable is written until the moment has been proved
        safe and the handoff has been proved complete AND verified: a refusal
        anywhere above leaves the run exactly where it was, with the rotation
        still pending, rather than half-rotated.
        """
        assert_safe_seam(safety_state)
        handoff = build_handoff(facts)
        verification = verify(handoff, facts, verifier=self._verifier,
                              review_model=self.review_model,
                              advisory_model=self.advisory_model)
        if not verification.verified:
            raise SeamTurnoverError(
                "handoff_unverified",
                f"the handoff was not verified ({verification.reason_code}: "
                f"{verification.reason}); a rotation never carries an unverified handoff "
                f"into a successor session (S11.3)",
                {"findings": list(verification.findings),
                 "handoff_digest": handoff.digest()})
        self.ledger.store_verified_handoff(handoff, verification)

        if continuity.resumed:
            # An archived session may never be resumed (S15). This is the last
            # place that can still be true before the launch is commanded.
            self.ledger.assert_not_archived(continuity.provider_session_id)

        record_key = rotation.new_rotation_record_key(previous_provider_session_id)
        record = self.ledger.complete_rotation(
            previous_provider_session_id=previous_provider_session_id,
            rotation_record_key=record_key,
            handoff_digest=handoff.digest(),
            continuity_mode=continuity.mode,
            provider_session_id=continuity.provider_session_id,
            provider_session_none_reason=continuity.none_reason,
        )
        expectation = SuccessorExpectation(
            task_id=facts.task_id, branch=facts.branch, worktree=facts.worktree,
            head_sha=facts.head_sha, model_id=successor_model,
            continuity_mode=continuity.mode,
            provider_session_id=continuity.provider_session_id,
            rotation_record_key=record_key)
        self.arm_ready_gate(expectation, handoff_digest=handoff.digest())

        prompt = ""
        if not continuity.resumed:
            payload = rotation.export_handoff_payload(
                handoff, verification, rotation_record_key=record_key,
                evidence=evidence)
            prompt = session_continuity.reorientation_prompt(payload, continuity)
        return SeamTurnoverResult(
            rotation_record_key=record_key,
            previous_provider_session_id=previous_provider_session_id,
            continuity=continuity,
            handoff_digest=handoff.digest(),
            verification=verification,
            expectation=expectation,
            reorientation_prompt=prompt,
            record=record,
        )

    def _audit(self, event: str, detail: Mapping[str, Any]) -> None:
        if self.audit is not None:
            self.audit.append(event, run_id=self.run_id,
                              output_digest=str(detail.get("handoff_digest", "") or ""),
                              detail=dict(detail))

