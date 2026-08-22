#!/usr/bin/env python3
"""Real session continuity across a rotation: provider identity, resume, reorientation.

Qualifying evidence (supervisor-freeze §2/§3, AD-093 - a reproduced defect).
Before M0-T080 the supervisor rotated a session like this:

    old_session = self._current_session_id            # loop.py
    new_session = rotation.new_session_id(old_session) # -> "sup-<uuid4 hex>"
    ledger.complete_rotation(old_session_id=old_session,
                             new_session_id_value=new_session, ...)

`rotation.new_session_id` minted `sup-{uuid.uuid4().hex}` - an identity the
SUPERVISOR invented - and the loop then stored it where a PROVIDER session
identity belongs. Three consequences, all reproduced:

1. `RunnerConfig.resume_session_id` exists and `claude_runner.build_argv` knows
   how to emit `--resume <session-id>`, but NO production code ever assigned it
   (a repository-wide search found exactly one writer: the `doctor` capability
   probe). A "completed rotation" therefore launched a FRESH, UNRESUMED session
   while recording rotation success.
2. `RotationLedger.assert_ready_checkpoint` compares the READY checkpoint's
   `claude_session_id` - a PROVIDER id the worker reports - against the invented
   `sup-...` id, so the READY gate could never match on a real session.
3. Nothing durable carried the real provider session id past the unit that
   produced it, so no later act could resume or even name the session that did
   the work.

This module supplies the missing half. It records the ACTUAL provider session
identity the Claude CLI reports (`RunResult.session_id`, parsed off the stream by
`claude_runner`), and it decides - explicitly, with a recorded reason - whether
the successor RESUMES that exact session or performs a NEW-SESSION
REORIENTATION carrying the full persisted handoff.

The one rule: the supervisor NEVER pretends. A rotation is recorded as `resume`
only when the successor really launches with `--resume <the provider id>`;
otherwise it is recorded as `reorientation` together with the closed, named
reason resume was impossible. There is no third state and no silent middle.
"""
from __future__ import annotations

import dataclasses
from typing import Any, Mapping

from .models import to_utc_iso

#: Durable key holding the LAST provider session identity a completed unit
#: reported, plus what it ran on. Distinct from `claude_runner.SESSION_KEY`
#: (the S8.2 full session identity record) because this one answers exactly one
#: question - "which provider session may the next launch resume?" - and must be
#: readable without reconstructing the whole identity record.
PROVIDER_SESSION_KEY = "provider_session_continuity"

#: The two continuity modes. There is no third value: a rotation either really
#: resumed the recorded provider session or it explicitly re-oriented a new one.
RESUME = "resume"
REORIENTATION = "reorientation"
CONTINUITY_MODES: tuple[str, ...] = (RESUME, REORIENTATION)

#: The CLOSED list of reasons a resume is impossible. A reorientation record must
#: name one of these; "we did not try" is not on the list and cannot be recorded.
NO_RECORDED_SESSION = "no_provider_session_recorded"
CROSS_MODEL = "cross_model"
RESUME_CAPABILITY_UNVERIFIED = "resume_capability_unverified"
PROVIDER_SESSION_EXPIRED = "provider_session_expired"
CONTEXT_SHEDDING_ROTATION = "context_shedding_rotation"

NONE_REASONS: tuple[str, ...] = (
    NO_RECORDED_SESSION, CROSS_MODEL, RESUME_CAPABILITY_UNVERIFIED,
    PROVIDER_SESSION_EXPIRED, CONTEXT_SHEDDING_ROTATION,
)

#: Rotation reason codes whose WHOLE PURPOSE is to shed the accumulated context.
#: Resuming the same provider session would carry that context straight back into
#: the successor and defeat the rotation, so resume is impossible BY POLICY here -
#: and S11.3 says so directly ("a brand-new explicitly identified session is the
#: required behaviour"). Listed explicitly rather than inferred, so adding a new
#: rotation reason is a deliberate decision about continuity, not an accident.
CONTEXT_SHEDDING_REASONS: frozenset[str] = frozenset({
    "context_threshold",
    "checkpoint_count",
    "compaction_event",
    "oversized_checkpoint",
    "instruction_adherence_loss",
    "owner_request",
    "mandatory_threshold",
    "large_job_threshold",
    "unknown_usage_conservative",
})


class ContinuityError(Exception):
    """A continuity record was malformed. Always fails closed."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclasses.dataclass(frozen=True)
class ProviderSession:
    """The provider's OWN session identity, as reported by the provider.

    `session_id` is the id the Claude CLI emitted on its stream (the
    `system`/`init` event's `session_id`, which `claude_runner` parses into
    `RunResult.session_id`). It is never minted, derived, or defaulted here: an
    absent id stays absent, which makes a later resume impossible and SAYS so.
    """

    session_id: str
    model_id: str = ""
    run_id: str = ""
    cycle: int = 0
    recorded_at_utc: str = ""
    #: Monotonic-independent ordering aid: the epoch seconds the record was
    #: taken, when the caller supplied a clock. 0.0 means "not measured".
    recorded_at_epoch: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> "ProviderSession | None":
        if not isinstance(data, Mapping):
            return None
        session_id = str(data.get("session_id", "") or "")
        if not session_id:
            return None
        try:
            cycle = int(data.get("cycle", 0) or 0)
        except (TypeError, ValueError):
            cycle = 0
        try:
            epoch = float(data.get("recorded_at_epoch", 0.0) or 0.0)
        except (TypeError, ValueError):
            epoch = 0.0
        return cls(
            session_id=session_id,
            model_id=str(data.get("model_id", "") or ""),
            run_id=str(data.get("run_id", "") or ""),
            cycle=cycle,
            recorded_at_utc=str(data.get("recorded_at_utc", "") or ""),
            recorded_at_epoch=epoch,
        )


def record_provider_session(
    journal: Any, *, session_id: str, model_id: str = "", run_id: str = "",
    cycle: int = 0, at_epoch: float = 0.0,
) -> ProviderSession | None:
    """Persist the provider session identity a completed unit reported.

    An EMPTY id is not recorded and does not overwrite a previous record: the
    honest meaning of "the stream carried no session id" is "we learned nothing
    new", never "the session identity is now blank".
    """
    if not session_id:
        return None
    record = ProviderSession(
        session_id=session_id, model_id=model_id, run_id=run_id, cycle=cycle,
        recorded_at_utc=to_utc_iso(), recorded_at_epoch=float(at_epoch or 0.0))
    journal.set_state(PROVIDER_SESSION_KEY, record.to_dict())
    return record


def recorded_provider_session(journal: Any, *, run_id: str = "") -> ProviderSession | None:
    """The last recorded provider session, or None. Unreadable state reads None.

    M0-T080 correction U14 (G4 F6): the record is keyed per CHECKOUT, not per run,
    so run B could read run A's leftover session - and then ARCHIVE it on B's
    first rotation, or offer it to a `--resume`. Passing `run_id` scopes the read:
    a record from a different run reads as absent, which is the honest answer
    (this run has not recorded a session yet) and is fail-closed for continuity.
    Callers that legitimately want the last session whoever owned it - the
    standalone watchdog, which runs after the orchestrator process is gone -
    omit `run_id` and get the previous behaviour.
    """
    try:
        recorded = ProviderSession.from_dict(journal.get_state(PROVIDER_SESSION_KEY, None))
    except Exception:  # pragma: no cover - a journal that cannot be read
        return None
    if recorded is None or not run_id:
        return recorded
    return recorded if recorded.run_id == run_id else None


def clear_provider_session(journal: Any) -> None:
    """Forget the recorded provider session (an explicit act, never implicit)."""
    journal.set_state(PROVIDER_SESSION_KEY, None)


@dataclasses.dataclass(frozen=True)
class ContinuityDecision:
    """How the successor will actually continue, and the evidence for it.

    `mode` is `resume` ONLY when `provider_session_id` is a real recorded
    provider id that the successor launch will pass to `--resume`. Every other
    case is `reorientation` and carries at least one `none_reasons` entry.
    """

    mode: str
    provider_session_id: str = ""
    none_reason: str = ""
    none_reasons: tuple[str, ...] = ()
    successor_model: str = ""
    session_model: str = ""
    reason: str = ""

    def __post_init__(self) -> None:
        if self.mode not in CONTINUITY_MODES:
            raise ContinuityError(
                "unknown_continuity_mode",
                f"{self.mode!r} is not one of {list(CONTINUITY_MODES)}; a rotation either "
                f"really resumed the provider session or explicitly re-oriented a new one")
        if self.mode == RESUME and not self.provider_session_id:
            raise ContinuityError(
                "resume_without_session_id",
                "a resume decision must name the exact provider session id the successor "
                "launch will pass to --resume; a resume with no id is a fresh session "
                "wearing a resume label")
        if self.mode == REORIENTATION and not self.none_reason:
            raise ContinuityError(
                "reorientation_without_reason",
                "a reorientation must name WHY resume was impossible; an unexplained "
                "reorientation is indistinguishable from silently starting over")
        # M0-T080 correction U14 (G3 M-2): the PRIMARY reason is validated too.
        # Only the tuple was checked, so a decision could carry a made-up
        # `none_reason` as long as `none_reasons` was empty or well-formed - and
        # the primary is the one every record and message quotes.
        unknown = [r for r in (*self.none_reasons, self.none_reason)
                   if r and r not in NONE_REASONS]
        if unknown:
            raise ContinuityError(
                "unknown_none_reason",
                f"{sorted(set(unknown))} are not among the closed impossibility reasons "
                f"{list(NONE_REASONS)}")

    @property
    def resumed(self) -> bool:
        return self.mode == RESUME

    def to_dict(self) -> dict[str, Any]:
        return {
            "continuity_mode": self.mode,
            "provider_session_id": self.provider_session_id,
            "provider_session_none_reason": self.none_reason,
            "provider_session_none_reasons": list(self.none_reasons),
            "successor_model": self.successor_model,
            "session_model": self.session_model,
            "reason": self.reason,
        }


def decide_continuity(
    *,
    recorded: ProviderSession | None,
    successor_model: str,
    rotation_reason: str = "",
    resume_capability_verified: bool = False,
    max_age_seconds: float | None = None,
    now_epoch: float = 0.0,
) -> ContinuityDecision:
    """Resume the recorded provider session, or explicitly re-orient a new one.

    Every impossibility is collected, not short-circuited, so the record names
    ALL of them rather than only the first one hit; the primary `none_reason` is
    the first in the closed order above.

    `max_age_seconds=None` means NO age bound is applied. That is deliberate:
    nothing on this build knows the provider's real session lifetime, and
    `CLAUDE.md` principle 3 forbids guessing it. An age bound is applied only
    when a caller supplies one from a source that actually knows.
    """
    reasons: list[str] = []
    session_model = recorded.model_id if recorded is not None else ""

    if recorded is None or not recorded.session_id:
        reasons.append(NO_RECORDED_SESSION)
    else:
        # M0-T080 correction U2. This used to require BOTH ids to be non-empty
        # before it would call a rotation cross-model, so a recorded session whose
        # `model_id` was unknown ("") plus a KNOWN different successor produced a
        # clean `resume` with no reasons at all - the loudest possible case read as
        # "no objection". A resume needs POSITIVE proof that the successor runs the
        # same model the recorded session ran; an empty value on either side is not
        # that proof, and CLAUDE.md principle 3 forbids guessing it.
        if not successor_model or not session_model or successor_model != session_model:
            reasons.append(CROSS_MODEL)
        if rotation_reason in CONTEXT_SHEDDING_REASONS:
            reasons.append(CONTEXT_SHEDDING_ROTATION)
        if not resume_capability_verified:
            reasons.append(RESUME_CAPABILITY_UNVERIFIED)
        if (max_age_seconds is not None and recorded.recorded_at_epoch
                and now_epoch and now_epoch - recorded.recorded_at_epoch > max_age_seconds):
            reasons.append(PROVIDER_SESSION_EXPIRED)

    if not reasons and recorded is not None:
        return ContinuityDecision(
            mode=RESUME,
            provider_session_id=recorded.session_id,
            successor_model=successor_model,
            session_model=session_model,
            reason=(f"the successor RESUMES provider session {recorded.session_id!r} on "
                    f"{successor_model or 'the current model'}: the id is recorded, the "
                    f"model is unchanged, exact-session resume is verified on this binary, "
                    f"and the rotation is not one that exists to shed context"))

    ordered = tuple(r for r in NONE_REASONS if r in reasons)
    return ContinuityDecision(
        mode=REORIENTATION,
        provider_session_id="",
        none_reason=ordered[0],
        none_reasons=ordered,
        successor_model=successor_model,
        session_model=session_model,
        reason=(f"the successor CANNOT resume the recorded provider session "
                f"({', '.join(ordered)}), so it starts a NEW session and is re-oriented "
                f"from the full persisted handoff. This is recorded as a reorientation, "
                f"never as a resume that did not happen"))


#: The sentinel a reorientation prompt opens with. Kept out of the handoff body
#: so a test can prove the successor was handed a reorientation, and so the text
#: is one string rather than something assembled differently at each seam.
REORIENTATION_HEADER = "SESSION REORIENTATION (D-007 S11.3)"


def reorientation_prompt(payload: Mapping[str, Any], decision: ContinuityDecision) -> str:
    """The FULL persisted handoff, delivered as the successor's first prompt.

    The successor is a brand-new session that knows nothing, so the prompt is the
    whole exported handoff bundle - not a digest, not a pointer, not a summary -
    plus the one thing S11.3 requires back before any change: a structured READY
    checkpoint. `rotation.export_handoff_payload` has already refused any handoff
    that automates an interactive `/clear`, so this only formats what it returns.
    """
    import json

    handoff = dict(payload.get("handoff", {}) or {})
    next_action = str(payload.get("exact_next_authorized_action", "") or "")
    lines = [
        REORIENTATION_HEADER,
        "",
        f"The previous session could not be resumed ({decision.none_reason}: "
        f"{', '.join(decision.none_reasons)}). You are a NEW session. Everything you are "
        f"authorized to know about this work is below; nothing is carried over implicitly.",
        "",
        "HANDOFF (verified, digest "
        f"{str(payload.get('handoff_digest', '') or '')[:16]}..., verified by "
        f"{str(payload.get('verified_by_model', '') or 'the review model')}):",
        json.dumps(handoff, indent=2, ensure_ascii=False, sort_keys=True, default=str),
        "",
        f"EVIDENCE REFERENCES: {list(payload.get('evidence_refs', []) or [])}",
        "",
        f"EXACT NEXT AUTHORIZED ACTION: {next_action}",
        "",
        "REQUIRED FIRST RESPONSE: a structured checkpoint with status READY, carrying this "
        "session's own claude_session_id. Make NO change of any kind before that checkpoint "
        "has been returned and accepted.",
    ]
    return "\n".join(lines)
