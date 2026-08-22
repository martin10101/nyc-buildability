#!/usr/bin/env python3
"""How the supervised loop drives the FULL S11.3 turnover seam (M0-T080).

Extracted from `loop.py` for the same reason `loop_breakers.py` was in M0-T079:
these functions change for entirely different reasons than the S7 state wiring
`loop.py` owns. WHAT a turnover is - safe-seam check, handoff build, verification,
durable persistence, READY gate, post-launch identity check - lives in
`turnover_seam.py`; WHICH FACTS this run can state about the work, and WHERE in
the cycle the gates are applied, live here; `loop.py` keeps thin delegating
methods so its public surface is unchanged.

Every function takes the loop as its first argument rather than being a method,
so the module has no state of its own and the loop stays the single owner of the
run's mutable identity (`_provider_session_id`, `_rotation_record_key`, the
runner binding).
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from . import session_continuity as sc
from . import turnover_seam as ts
from .errors import LoopError
from .models import digest_of, to_utc_iso


def seam_facts(loop: Any, *, reason_code: str, cycle: int) -> ts.SeamFacts:
    """Everything this run can truthfully state about the work being handed over.

    Each value comes from something the supervisor already holds - the task
    packet's authority, the run's recorded HEAD, and the last VALID checkpoint -
    so the handoff describes the real unit rather than a summary a model wrote.
    `head_sha` prefers the run's own recorded HEAD and falls back to the last
    checkpoint's `current_sha`, which is the SHA the worker actually finished on;
    when neither exists the seam refuses on `sha_ambiguous` rather than rotating
    with an unknown HEAD.
    """
    last = loop._last_checkpoint
    head = loop._head_sha or str(getattr(last, "current_sha", "") or "")
    changed = tuple(str(f) for f in (getattr(last, "changed_files", ()) or ()))
    blockers = tuple(str(b.get("id", b)) if isinstance(b, Mapping) else str(b)
                     for b in (getattr(last, "blockers", ()) or ()))
    gates = tuple(str(g.get("question", g)) if isinstance(g, Mapping) else str(g)
                  for g in (getattr(last, "owner_decisions_required", ()) or ()))
    return ts.SeamFacts(
        task_id=loop.config.task_id,
        stage=loop.config.stage,
        branch=loop.authority.branch,
        worktree=loop.authority.worktree,
        head_sha=head,
        origin_main_sha=loop._origin_main_sha,
        reason_code=reason_code,
        completed_work=str(getattr(last, "summary", "") or ""),
        changed_files=changed,
        tests_and_ci={"tests": list(getattr(last, "tests", ()) or ()),
                      "ci": getattr(last, "ci", None)},
        pull_request_state=str(getattr(last, "pull_request", None)
                               or "no pull request is open for this unit"),
        open_blockers=blockers,
        owner_gates=gates,
        forbidden_scope=tuple(loop.authority.forbidden_paths),
        evidence_digests={"last_checkpoint": digest_of(last.to_dict())} if last else {},
        last_checkpoint_id=loop._last_checkpoint_id,
        exact_next_action=(
            f"continue task {loop.config.task_id} at stage {loop.config.stage} on "
            f"branch {loop.authority.branch} in {loop.authority.worktree}: dispatch the "
            f"next bounded unit from checkpoint "
            f"{loop._last_checkpoint_id or 'the task packet'} under the same authority. "
            f"Rotation reason: {reason_code}"),
    )


def full_turnover(loop: Any, *, cycle: int, reason_code: str,
                  successor_model: str) -> ts.SeamTurnoverResult:
    """Safe-seam -> handoff -> verify -> persist -> rotate -> arm READY -> actuate.

    The single replacement for the three direct `complete_rotation` calls the
    seams used to make. Every gate `rotation.py` provides is applied, and the
    CONTINUITY decision - a real `--resume` of the recorded provider session, or
    an explicit new-session reorientation carrying the full handoff - is made and
    RECORDED rather than assumed.
    """
    facts = seam_facts(loop, reason_code=reason_code, cycle=cycle)
    safety = ts.safety_state_from_run(
        pending_effects=list(loop.journal.pending_effects()),
        open_asks=list(loop.journal.open_asks()),
        unit_in_flight=False,
        head_sha=facts.head_sha, branch=facts.branch,
        worktree=facts.worktree, task_stage=facts.stage)
    continuity = sc.decide_continuity(
        # U14/G4-F6: scoped to THIS run, so run B never resumes or archives
        # a session run A left behind in the same checkout.
        recorded=sc.recorded_provider_session(loop.journal, run_id=loop.run_id),
        successor_model=successor_model,
        rotation_reason=reason_code,
        resume_capability_verified=resume_capability_verified(loop),
        max_age_seconds=loop._resume_max_age_seconds)
    result = loop._seam.execute(
        facts=facts, safety_state=safety, continuity=continuity,
        previous_provider_session_id=loop._provider_session_id,
        successor_model=successor_model,
        evidence=(loop._last_checkpoint_id,) if loop._last_checkpoint_id else ())
    # ACTUATION: a resume that does not reach the launch is not a resume.
    if continuity.resumed:
        actuate_resume(loop, continuity.provider_session_id)
    else:
        # The outgoing provider session is archived and gone; forget it so
        # nothing downstream can offer it to a later `--resume`.
        loop._provider_session_id = ""
        sc.clear_provider_session(loop.journal)
    loop._rotation_record_key = result.rotation_record_key
    loop._successor_expectation = result.expectation
    return result


def resume_capability_verified(loop: Any) -> bool:
    """Whether `--resume <session-id>` was behaviourally probed on THIS binary.

    Read off the runner's own launch config, the same field
    `claude_runner.build_argv` consults before it will emit the flag at all.
    Absent reads False: an unprobed capability is never assumed present (S8.2 -
    never fall back to a "most recent session" lookup).
    """
    config = getattr(loop.runner, "config", None)
    return getattr(config, "resume_capability_verified", False) is True


def actuate_resume(loop: Any, provider_session_id: str) -> None:
    """Rebind the RUNNER so the next unit really launches with `--resume`.

    The mirror of `_actuate_model`, and for the same reason: recording a resume
    the launch never performed is the defect this task fixes. A runner that
    cannot be rebound is a REFUSAL, not a record.
    """
    rebind = getattr(loop.runner, "with_resume", None)
    if not callable(rebind):
        raise LoopError(
            "resume_actuation_unavailable",
            f"the runner cannot be rebound to resume provider session "
            f"{provider_session_id!r}, so the rotation would record a resume that never "
            f"reached the process; refusing rather than claiming a continuity the "
            f"successor does not have")
    loop.runner = rebind(provider_session_id)


def post_rotation_gates(loop: Any, checkpoint: Any, run_result: Any, *, cycle: int,
                        touches: list) -> tuple[str, str] | None:
    """The READY gate and the post-launch identity check. `None` means pass.

    Both are no-ops when no turnover armed them, so an ordinary cycle in a run
    that never rotated is untouched. After a turnover they are mandatory and fail
    CLOSED: the run stops, nothing is forwarded, and the owner is told which
    expectation the successor did not meet.
    """
    from .loop import TOUCH_SYNCHRONOUS_STOP  # local: loop imports this module

    # Read the DURABLE gate before `require_ready` clears it. `_successor_expectation`
    # is in-memory, so a crash between the rotation and the successor's first
    # checkpoint would otherwise lose it and skip the identity check on exactly the
    # cycle that needs it most. The armed gate carries the same expectation and
    # survives the restart, so it is the fallback.
    armed = loop._seam.armed_gate()

    try:
        loop._seam.require_ready(checkpoint)
    except ts.SeamTurnoverError as exc:
        touches.append(loop._touch(
            TOUCH_SYNCHRONOUS_STOP, reason_code=exc.code, reason=exc.message,
            cycle=cycle,
            basis="S11.3 READY checkpoint after re-orientation, before any change"))
        if loop.audit is not None:
            loop.audit.append("rotation_ready_gate_refused", run_id=loop.run_id,
                              decision="deny", policy_result=exc.code,
                              detail={"cycle": cycle, "message": exc.message,
                                      **exc.detail})
        return exc.code, exc.message

    expectation = loop._successor_expectation
    if expectation is None:
        if armed is None:
            return None
        expectation = ts.SuccessorExpectation(
            task_id=str(armed.get("task_id", "") or ""),
            branch=str(armed.get("branch", "") or ""),
            worktree=str(armed.get("worktree", "") or ""),
            head_sha=str(armed.get("head_sha", "") or ""),
            model_id=str(armed.get("model_id", "") or ""),
            continuity_mode=str(armed.get("continuity_mode", "") or ""),
            provider_session_id=str(armed.get("provider_session_id", "") or ""),
            rotation_record_key=str(armed.get("rotation_record_key", "") or ""))
    ok, reason, detail = loop._seam.verify_post_launch(
        checkpoint=checkpoint, run_result=run_result, expectation=expectation)
    # Checked once per turnover: the successor has now identified itself.
    loop._successor_expectation = None
    if ok:
        if loop.audit is not None:
            loop.audit.append("successor_identity_verified", run_id=loop.run_id,
                              policy_result="successor_matches_command",
                              detail={"cycle": cycle, **detail})
        return None
    touches.append(loop._touch(
        TOUCH_SYNCHRONOUS_STOP, reason_code="successor_identity_mismatch",
        reason=reason, cycle=cycle,
        basis="M0-T080 post-launch verification: a successor that is not the session "
              "that was commanded never continues the work"))
    if loop.audit is not None:
        loop.audit.append("successor_identity_mismatch", run_id=loop.run_id,
                          decision="deny", policy_result="successor_identity_mismatch",
                          detail={"cycle": cycle, "reason": reason, **detail})
    return "successor_identity_mismatch", reason


def turnover_refused(loop: Any, *, cycle: int, reason_code: str,
                     error: ts.SeamTurnoverError):
    """A gate in the full turnover refused: PAUSE + notify, never half-rotate.

    Reached when the moment was unsafe, the handoff could not be built, or the
    handoff did not verify. Nothing durable about the rotation has been written
    at that point, so the run stays exactly where it was with the rotation still
    pending - and the owner is told which gate refused.
    """
    from .loop import (  # local: loop imports this module
        PAUSED_RECOVERY, QueuedAsk, SeamRotation, TOUCH_SYNCHRONOUS_STOP,
    )

    loop.machine.transition(
        PAUSED_RECOVERY, "unsafe_condition",
        detail={"cycle": cycle, "reason": error.code,
                "rotation_reason": reason_code, **error.detail})
    touch = loop._touch(
        TOUCH_SYNCHRONOUS_STOP, reason_code=error.code, reason=error.message,
        cycle=cycle, basis="S11.3 safe rotation protocol (M0-T080 full turnover)")
    ask_id = f"turnover_refused/{loop.run_id}/{cycle}"
    try:
        loop.journal.queue_ask(QueuedAsk(
            ask_id=ask_id, run_id=loop.run_id, task_id=loop.config.task_id,
            question=(f"A session turnover was refused at the {error.code} gate: "
                      f"{error.message} How should the run proceed?"),
            request_digest=digest_of({"code": error.code, "cycle": cycle}),
            created_at_utc=to_utc_iso(), classification="security"))
    except Exception:
        pass  # a duplicate ask id means the same refusal is already queued
    if loop.audit is not None:
        loop.audit.append(
            "rotation_refused", run_id=loop.run_id, decision="deny",
            policy_result=error.code,
            detail={"cycle": cycle, "reason_code": reason_code,
                    "refusal_code": error.code, "message": error.message,
                    "ask_id": ask_id, **error.detail})
    return SeamRotation(relaunched=False, paused=True, stopped="rotation_refused",
                        reason=error.message, reason_code=error.code, touch=touch)


def stop_chain_exhausted(loop: Any, *, cycle: int, reason_code: str,
                         exhausted_model: str,
                         attempts: Sequence[Mapping[str, Any]]):
    """No chain entry launched: STOP, refresh the handoff, notify (D-004-R755).

    The end of the chain is a full stop, never a fallback. Nothing outside the
    chain is tried, no substitute is chosen, and the run does not continue: the
    handoff is refreshed under this reason code, the owner is notified through
    the existing pause/ask surface, and the seam reports the stop.
    """
    from .loop import (  # local: loop imports this module
        CHAIN_EXHAUSTED_STOP, PAUSED_RECOVERY, QueuedAsk, SeamRotation,
        TOUCH_SYNCHRONOUS_STOP,
    )

    handoff_digest = loop._refresh_session_handoff(cycle=cycle,
                                                   reason_code=CHAIN_EXHAUSTED_STOP)
    loop.machine.transition(
        PAUSED_RECOVERY, "unsafe_condition",
        detail={"cycle": cycle, "reason": CHAIN_EXHAUSTED_STOP,
                "pinned_model": loop.pinned_model,
                "exhausted_model": exhausted_model,
                "chain": list(loop.model_chain.entries),
                "rotation_reason": reason_code})
    touch = loop._touch(
        TOUCH_SYNCHRONOUS_STOP, reason_code=CHAIN_EXHAUSTED_STOP,
        reason=(f"no entry in the configured model chain "
                f"{list(loop.model_chain.entries)} actually launched after "
                f"{exhausted_model!r} was exhausted; the session stops rather than "
                f"continuing on an unlisted or substitute model (D-004-R755)"),
        cycle=cycle, basis="D-004 model chain / D-007 am.12")
    ask_id = f"model_chain_exhausted/{loop.run_id}/{cycle}"
    try:
        loop.journal.queue_ask(QueuedAsk(
            ask_id=ask_id, run_id=loop.run_id, task_id=loop.config.task_id,
            question=(f"No model in the configured chain "
                      f"{list(loop.model_chain.entries)} could be launched after "
                      f"{exhausted_model!r} was exhausted. The session has stopped and "
                      f"will not continue on any other model; how should it proceed?"),
            request_digest=handoff_digest, created_at_utc=to_utc_iso(),
            classification="security"))
    except Exception:
        # A duplicate ask id means the same stop is already queued.
        pass
    if loop.audit is not None:
        loop.audit.append(
            CHAIN_EXHAUSTED_STOP, run_id=loop.run_id,
            decision="deny", policy_result=CHAIN_EXHAUSTED_STOP,
            output_digest=handoff_digest,
            detail={"cycle": cycle, "pinned_model": loop.pinned_model,
                    "exhausted_model": exhausted_model,
                    "chain": list(loop.model_chain.entries),
                    "chain_attempts": [dict(a) for a in attempts],
                    "launched_model": loop.launched_model(),
                    "reason_code": reason_code, "ask_id": ask_id,
                    "handoff_digest": handoff_digest,
                    "note": "every chain entry was tried by an actual launch attempt and "
                            "none came up; the supervisor NEVER continues on an unlisted "
                            "or substitute model (D-004-R754/R755)"})
    return SeamRotation(
        relaunched=False, paused=True, stopped=CHAIN_EXHAUSTED_STOP,
        reason=(f"no entry in the configured model chain launched after "
                f"{exhausted_model!r} was exhausted; the session stopped and the owner "
                f"was notified"),
        reason_code=CHAIN_EXHAUSTED_STOP, touch=touch)


def with_reorientation(seam: Any, prompt: str) -> str:
    """Put the full persisted handoff ahead of the next prompt, when re-orienting.

    The successor of a REORIENTATION is a brand-new session that knows nothing
    about the work, so S11.3's handoff has to actually REACH it. Before M0-T080
    the loop handed the next unit the forwarded prompt alone and the handoff
    stayed in the journal, which is why "the successor was re-oriented" was a
    claim rather than an action. A resume returns the prompt unchanged.
    """
    if not seam.reorientation_prompt:
        return prompt
    return f"{seam.reorientation_prompt}\n\n---\n\nFORWARDED UNIT PROMPT:\n{prompt}"
