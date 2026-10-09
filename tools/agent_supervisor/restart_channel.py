#!/usr/bin/env python3
"""Explicit, audited, fail-closed operator recovery surfaces (F-2 class closure).

D-024 Amendment 16 (rows R303-R313). The S7 state machine has always DEFINED the
owner recovery edges out of its blocking and terminal states, but three of them
had NO code path that could fire them - the exact "the edge the state machine
always defined but no command could reach" defect the pilot named F-2, twice
fixed before (``clear-recovery`` for ``PAUSED_RECOVERY``, ``resume-pending-prompt``
for the held-prompt ``WAIT_FOR_OWNER`` exit). This module owns the remaining ones:

* ``HALTED -> IDLE`` on ``owner_explicit_restart`` - the reproduced M0-T107 defect
  (an owner-typed certified start refused pre-dispatch, exit 13, because the
  trigger had zero call sites: ``project-control/reports/M0-T107-cycle2-start-refusal.md``);
* ``EMERGENCY_STOPPED -> IDLE`` on ``owner_explicit_restart`` - the latent sibling
  named in that same report, deliberately given a STRONGER acknowledgment so an
  emergency stop is never left by habit or a script default;
* ``WAIT_FOR_OWNER -> PREFLIGHT`` on ``owner_answer_validated`` - a THIRD latent
  instance this task's own removal-sensitive reachability sweep uncovered (the
  owner-answered resume that ``resume-pending-prompt`` documents it deliberately
  does NOT cover), closed here so the complete F-2 class is reachable (R303).

Every surface here is the ``clear-recovery`` discipline, made explicit:

* it refuses while the durable emergency-stop FLAG is set (the flag is cleared
  only by ``stop --clear``; a recovery surface never overrides it);
* it refuses from any state other than the exact edge source;
* it refuses while a fail-closed precondition holds - an open owner ask, a
  pending external effect, a recorded surviving/undetermined child, provider
  identity drift, or a recovery classification that is not ``SAFE_CHECKPOINT``
  (R311);
* it clears NO durable flag, resets NO budget, and dispatches NOTHING;
* it holds the single-instance lock across the read-checks and the transition,
  so exactly one controller can fire the edge and a racing second invocation
  fails closed (``lock_held``);
* it transitions state EXACTLY ONCE and leaves a durable audited owner-recovery
  record - the ``state_transition`` event the machine writes plus a first-class
  operator-recovery event (R313).

Nothing here re-runs the live revalidation set: the surfaces move a parked run to
a re-validation entry point (``IDLE``/``PREFLIGHT``) and the subsequent ``start``
re-runs the full S11.5/preflight gate (including the live provider-CLI drift probe
``recovery_probes.probe_cli_capability_manifest``) before any provider is
contacted. See ``_recovery_classification_precondition`` for why the drift check
is the recorded recovery classification here, plus the live re-gate at ``start``.
"""
from __future__ import annotations

import dataclasses
import pathlib
import sys
from typing import Any, Callable

from . import CONTROLLER_VERSION
from .durable_state import checkout_key
from .locking import SingleInstanceLock
from .models import digest_of
from .operator_channel_cli import emit_payload, open_runtime
from .recovery import (
    SAFE_CHECKPOINT,
    DurableFlags,
    account_for_children,
    last_outcome as last_recovery_outcome,
)
from .state_machine import (
    EMERGENCY_STOPPED,
    HALTED,
    IDLE,
    INITIAL_STATE,
    PREFLIGHT,
    STATE_KEY,
    WAIT_FOR_OWNER,
    IllegalTransitionError,
    StateMachine,
)

#: The single trigger that fires both `HALTED -> IDLE` and
#: `EMERGENCY_STOPPED -> IDLE`. Named once so the CLI, the tests, and the
#: reachability sweep all reference the same literal.
OWNER_EXPLICIT_RESTART = "owner_explicit_restart"
OWNER_ANSWER_VALIDATED = "owner_answer_validated"

#: The audit event each operator surface appends alongside the state-machine's
#: own `state_transition` event. First-class so an operator restart is queryable
#: as an event, not only inferable from a transition row.
EVENT_OWNER_RESTART = "operator_owner_restart"
EVENT_EMERGENCY_ACK_RESTART = "operator_emergency_stop_ack_restart"
EVENT_OWNER_ANSWER_RESUME = "operator_owner_answer_resume"

#: Recovery-classification revalidation steps whose failure means the provider
#: toolchain/identity or its authentication drifted (see
#: `recovery.REVALIDATION_STEPS`). A recorded recovery outcome that failed one of
#: these is surfaced as `provider_identity_drift` specifically (R311), distinct
#: from a generic unsafe classification.
_IDENTITY_REVALIDATION_STEPS: frozenset[str] = frozenset({
    "cli_capability_manifest", "auth",
})


@dataclasses.dataclass(frozen=True)
class RestartResult:
    """The outcome of one operator-recovery attempt.

    ``ok`` False carries a stable ``code`` and a typed ``message`` and means
    NOTHING was written (no transition, no flag change, no audit decision event).
    ``ok`` True carries the applied edge and the durable record's identifiers.
    """

    ok: bool
    code: str
    message: str
    command: str = ""
    state_from: str = ""
    state_to: str = ""
    trigger: str = ""
    run_id: str = ""
    sequence: int = -1

    def as_payload(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def _refuse(command: str, code: str, message: str) -> RestartResult:
    return RestartResult(ok=False, code=code, message=message, command=command)


def _current_state(journal: Any) -> str:
    return str(journal.get_state(STATE_KEY, INITIAL_STATE))


def _open_owner_asks(journal: Any) -> list[Any]:
    """Unanswered owner asks, reconciled at read time (M0-T070/M0-T115).

    Imported lazily so this module never participates in an import cycle with the
    broker (the ``recovery_probes`` precedent). A read error propagates and the
    caller fails closed - it is never treated as an empty queue.
    """
    from .broker import owner_unanswered_asks
    return list(owner_unanswered_asks(journal))


def _surviving_children(journal: Any) -> list[Any]:
    """Recorded children that survived the discontinuity or could not be
    determined - either is drift, never "probably gone" (S11.5 step 3)."""
    return [child for child in account_for_children(journal)
            if child.surviving or not child.determined]


def _recovery_classification_precondition(
    journal: Any, command: str,
) -> RestartResult | None:
    """Refuse unless the RECORDED recovery classification is SAFE_CHECKPOINT.

    The last ``recover_boot`` (run inside the preceding ``start``; it is what
    stamped the journal ``LAST_RECOVERY_KEY``) classified the at-rest journal.
    SAFE_CHECKPOINT means every S11.5 revalidation step passed - which includes
    ``cli_capability_manifest`` (the pinned provider-CLI identity compared against
    the installed executables) and ``auth`` - and no surviving child, pending
    effect, competing writer, or blocking flag was present AT THAT RECOVERY.

    A full LIVE provider-CLI drift probe (hashing the installed executables) needs
    the named executables and a live process; this operator command has neither,
    so it does NOT re-run that probe. It is not silently skipped: the recorded
    SAFE_CHECKPOINT is the evidence the pinned-identity revalidation passed, and
    the subsequent ``start`` re-runs ``recovery_probes.probe_cli_capability_manifest``
    LIVE against the installed executables and refuses on ``provider_cli_drift``
    before any provider is contacted (this surface only moves the journal to a
    re-validation entry point and dispatches nothing).

    An absent record, or one classified anything other than SAFE_CHECKPOINT, fails
    closed. A failure attributable to the provider toolchain/identity or its auth
    is surfaced as ``provider_identity_drift`` specifically (R311).
    """
    outcome = last_recovery_outcome(journal)
    if not isinstance(outcome, dict) or not outcome:
        return _refuse(
            command, "recovery_unclassified",
            "no recovery classification is recorded for this journal; a blocked "
            "run is restarted only after recovery has proven the checkpoint safe. "
            "Run the preceding `start` (which performs the S11.5 recover-boot "
            "classification) first; this surface never assumes safety.")
    classification = str(outcome.get("classification", ""))
    if classification == SAFE_CHECKPOINT:
        return None
    failed = set(outcome.get("failed_steps") or []) | set(outcome.get("missing_steps") or [])
    reason = str(outcome.get("reason", ""))
    reason_code = str(outcome.get("reason_code", ""))
    if failed & _IDENTITY_REVALIDATION_STEPS:
        return _refuse(
            command, "provider_identity_drift",
            "the recorded recovery classification failed the provider "
            f"toolchain/identity revalidation ({sorted(failed & _IDENTITY_REVALIDATION_STEPS)}): "
            f"{reason or reason_code}. A drifted or unauthenticated provider CLI is "
            "re-established explicitly through the standard start/preflight path, "
            "not restarted over.")
    return _refuse(
        command, "unsafe_recovery_classification",
        f"the recorded recovery classification is {classification!r} "
        f"({reason_code}), not {SAFE_CHECKPOINT}: {reason}. A blocked run is never "
        "restarted over an unresolved recovery condition.")


def evaluate_preconditions(
    journal: Any, *, expected_from_state: str, command: str,
) -> RestartResult | None:
    """The shared, read-only, fail-closed guard for every operator-recovery edge.

    Returns the FIRST failing precondition as a typed :class:`RestartResult`
    refusal, or ``None`` when every precondition passes. It writes nothing. The
    order is: durable emergency-stop flag, exact source state, open owner asks,
    pending external effects, surviving/undetermined children, then the recorded
    recovery classification (which subsumes the provider-identity revalidation).
    """
    flags = DurableFlags.read(journal)
    if flags.emergency_stop:
        return _refuse(
            command, "emergency_stop_flag_set",
            "a durable emergency stop is set. Clear it with an explicit "
            "`stop --clear` first (after the cause is addressed); an operator "
            "recovery surface never overrides the durable emergency-stop flag.")

    state = _current_state(journal)
    if state != expected_from_state:
        return _refuse(
            command, "wrong_state",
            f"nothing to do: the journal is in {state}, not {expected_from_state}. "
            f"`{command}` fires only the {expected_from_state} recovery edge, and "
            f"never a different state's.")

    try:
        open_asks = _open_owner_asks(journal)
    except Exception as exc:  # a queue that cannot be read is the caller's refusal
        return _refuse(
            command, "asks_unreadable",
            f"the owner-ask queue could not be read ({type(exc).__name__}); an "
            "unreadable queue fails closed rather than being treated as empty.")
    if open_asks:
        return _refuse(
            command, "open_asks",
            f"{len(open_asks)} owner ask(s) are still unanswered; a blocked run is "
            "not restarted while a question the owner must answer is open. Answer "
            "them (`approve-once`/`deny`) first.")

    pending = list(journal.pending_effects())
    if pending:
        return _refuse(
            command, "pending_effects",
            f"{len(pending)} external effect(s) are journaled with no verified "
            f"after-effect ({[e.action_id for e in pending]}); a restart never runs "
            "over an unreconciled external effect.")

    survivors = _surviving_children(journal)
    if survivors:
        return _refuse(
            command, "surviving_children",
            f"{len(survivors)} recorded child process(es) survived the "
            f"discontinuity or could not be determined ({[c.pid for c in survivors]}); "
            "a restart never proceeds while a child is unaccounted for.")

    classification_refusal = _recovery_classification_precondition(journal, command)
    if classification_refusal is not None:
        return classification_refusal
    return None


def _run_id_for(journal: Any) -> str:
    last = journal.last_transition()
    return last.run_id if last is not None and last.run_id else "operator"


def _fire_edge(
    journal: Any,
    audit: Any,
    *,
    state_to: str,
    trigger: str,
    command: str,
    audit_event: str,
    extra_detail: dict[str, Any] | None = None,
) -> RestartResult:
    """Apply exactly one transition and append the durable owner-recovery record.

    The state-machine transition writes its own ``state_transition`` audit event
    and commits the journal FIRST; only THEN is the first-class operator-recovery
    event appended, so no operator-recovery event is ever recorded without the
    transition it attests to. Idempotency inside :meth:`StateMachine.transition`
    is a backstop; the ``wrong_state`` precondition already refuses a repeat.
    """
    run_id = _run_id_for(journal)
    state_from = _current_state(journal)
    machine = StateMachine(journal, audit, run_id)
    detail = {"operator_initiated": True, "command": command}
    if extra_detail:
        detail.update(extra_detail)
    try:
        result = machine.transition(state_to, trigger, detail=dict(detail))
    except IllegalTransitionError as exc:
        # Defensive: the preconditions already gate the source state, so this is
        # unreachable in normal use; it stays a typed refusal, never a traceback.
        return _refuse(command, "illegal_transition", str(exc))
    audit.append(
        audit_event, run_id=run_id, decision="owner_recovery",
        state_from=state_from, state_to=state_to, policy_result=trigger,
        detail={**detail, "sequence": result.sequence, "applied": result.applied})
    return RestartResult(
        ok=True, code="restarted", message=f"{state_from} -> {state_to} on {trigger}",
        command=command, state_from=state_from, state_to=state_to, trigger=trigger,
        run_id=run_id, sequence=result.sequence)


def owner_restart(
    journal: Any, audit: Any, lock: Any, *, command: str = "owner-restart",
) -> RestartResult:
    """Fire ``HALTED -> IDLE`` on ``owner_explicit_restart`` - the M0-T107 edge.

    Refuses on ``EMERGENCY_STOPPED`` (that exit needs the STRONGER
    :func:`acknowledge_emergency_stop`), and on every fail-closed precondition.
    Holds the single-instance lock across the check and the transition.
    """
    return _locked(
        journal, audit, lock, command=command,
        expected_from_state=HALTED, state_to=IDLE, trigger=OWNER_EXPLICIT_RESTART,
        audit_event=EVENT_OWNER_RESTART)


def owner_answer_resume(
    journal: Any, audit: Any, lock: Any, *, command: str = "resume-after-answer",
) -> RestartResult:
    """Fire ``WAIT_FOR_OWNER -> PREFLIGHT`` on ``owner_answer_validated``.

    The third latent F-2 instance: a run parked at ``WAIT_FOR_OWNER`` for an owner
    QUESTION (not a held prompt - that is ``resume-pending-prompt``) had no surface
    to resume it once the owner had answered. Permitted only when the owner ask
    queue is empty (the ``open_asks`` precondition proves the question was
    answered through the authenticated ``approve-once``/``deny`` path) and every
    other precondition holds; it moves the run to ``PREFLIGHT``, where the next
    ``start`` re-validates before any provider contact.
    """
    return _locked(
        journal, audit, lock, command=command,
        expected_from_state=WAIT_FOR_OWNER, state_to=PREFLIGHT,
        trigger=OWNER_ANSWER_VALIDATED, audit_event=EVENT_OWNER_ANSWER_RESUME)


def emergency_stop_provenance(journal: Any) -> dict[str, Any] | None:
    """The last recorded transition INTO ``EMERGENCY_STOPPED``, or ``None``.

    The confirmation token binds to this so the acknowledgment names the exact
    emergency-stop incident and cannot be produced by a habitual or default
    argument.
    """
    for record in reversed(journal.transitions()):
        if record.state_to == EMERGENCY_STOPPED:
            return {"sequence": record.sequence, "state_from": record.state_from,
                    "trigger": record.trigger, "run_id": record.run_id,
                    "committed_at_utc": record.committed_at_utc}
    return None


def emergency_ack_token(journal: Any) -> str:
    """A short journal-derived confirmation token for the emergency-stop exit.

    Derived from the provenance of the last transition into ``EMERGENCY_STOPPED``
    (its sequence, source state, trigger, and run id). Empty when the journal
    records no such transition - in which case the acknowledgment cannot be
    formed and :func:`acknowledge_emergency_stop` fails closed. Not a secret: it
    is a digest of already-audited transition metadata, printed so the operator
    must deliberately read and re-supply it.
    """
    provenance = emergency_stop_provenance(journal)
    if provenance is None:
        return ""
    return digest_of(provenance)[:16]


def acknowledge_emergency_stop(
    journal: Any,
    audit: Any,
    lock: Any,
    *,
    acknowledged: bool,
    confirm_token: str,
    command: str = "acknowledge-emergency-stop",
) -> RestartResult:
    """Fire ``EMERGENCY_STOPPED -> IDLE`` on ``owner_explicit_restart`` - STRONGER.

    Materially stronger than :func:`owner_restart`, and impossible to trigger by
    habit or a script default: it requires BOTH an explicit ``acknowledged`` flag
    AND a ``confirm_token`` that matches :func:`emergency_ack_token` - a digest
    derived from THIS journal's emergency-stop provenance. A missing or wrong
    token is refused (and the required token is disclosed so the operator must
    deliberately re-supply it), and the standard preconditions apply, including
    that the durable emergency-stop FLAG has already been cleared with
    ``stop --clear``.
    """
    if not acknowledged:
        return _refuse(
            command, "acknowledgment_required",
            "leaving an EMERGENCY_STOPPED run requires the explicit "
            "`--acknowledge-emergency-stop` flag AND the journal's confirmation "
            "token; an emergency stop is never exited by an ordinary restart, a "
            "default, or a script.")
    expected = emergency_ack_token(journal)
    if not expected:
        return _refuse(
            command, "no_emergency_provenance",
            "no transition into EMERGENCY_STOPPED is recorded, so no confirmation "
            "token can be formed; the emergency-stop acknowledgment fails closed "
            "rather than guessing.")
    supplied = str(confirm_token or "").strip()
    if supplied != expected:
        return _refuse(
            command, "confirm_token_mismatch",
            "the supplied --confirm-emergency-token does not match this journal's "
            f"emergency-stop confirmation token. Re-run with "
            f"--confirm-emergency-token {expected} to acknowledge THIS emergency "
            "stop; the token binds to the recorded emergency-stop incident and is "
            "never wildcarded.")
    return _locked(
        journal, audit, lock, command=command,
        expected_from_state=EMERGENCY_STOPPED, state_to=IDLE,
        trigger=OWNER_EXPLICIT_RESTART, audit_event=EVENT_EMERGENCY_ACK_RESTART,
        extra_detail={"acknowledged": True, "confirm_token": expected})


def _locked(
    journal: Any,
    audit: Any,
    lock: Any,
    *,
    command: str,
    expected_from_state: str,
    state_to: str,
    trigger: str,
    audit_event: str,
    extra_detail: dict[str, Any] | None = None,
) -> RestartResult:
    """Acquire the single-instance lock, re-check preconditions UNDER the lock,
    fire the edge exactly once, then release. A live foreign holder fails closed
    (``lock_held``); the under-lock re-check closes the check-then-act window so
    two racing invocations can never both transition."""
    from .locking import LockError
    try:
        lock.acquire()
    except LockError as exc:
        return _refuse(command, getattr(exc, "code", "lock_error"),
                       f"refusing to run: {getattr(exc, 'message', str(exc))}. "
                       "Exactly one controller may drive a checkout.")
    try:
        refusal = evaluate_preconditions(
            journal, expected_from_state=expected_from_state, command=command)
        if refusal is not None:
            return refusal
        return _fire_edge(
            journal, audit, state_to=state_to, trigger=trigger, command=command,
            audit_event=audit_event, extra_detail=extra_detail)
    finally:
        try:
            lock.release()
        except Exception:  # pragma: no cover - release is best-effort cleanup
            pass


#: The operator-recovery triggers this module is responsible for making
#: reachable, derived MECHANICALLY from the state machine by the reachability
#: test (see `tools/test_agent_supervisor_restart_channel.py`). Listed here only
#: as documentation of intent; the test derives its own set from `TRANSITIONS`
#: and never reads this tuple, so this can never mask a regression.
OWNER_RECOVERY_TRIGGERS: tuple[str, ...] = (
    OWNER_EXPLICIT_RESTART, OWNER_ANSWER_VALIDATED,
)


# --------------------------------------------------------------------------
# CLI surface (D-024 R034: one command surface, no parallel CLI). Registered
# on the existing parser by `register_restart_verbs`, exactly like
# `operator_channel_cli.register_operator_verbs`; `cli.py` stays a thin wire.
# --------------------------------------------------------------------------


def _emit_restart_result(args: Any, result: RestartResult) -> int:
    """Render a :class:`RestartResult`: emit on success, a typed stderr refusal
    (exit 1) on any fail-closed precondition."""
    if result.ok:
        emit_payload(
            args, {**result.as_payload(), "restarted": True},
            [f"{result.state_from} -> {result.state_to} on {result.trigger} by an "
             "explicit operator command; no flag was cleared, no budget was reset, "
             "and nothing was dispatched. `start` may now resume this run."])
        return 0
    print(f"refusing to {result.command} ({result.code}): {result.message}",
          file=sys.stderr)
    return 1


def _restart_cli(args: Any, op_call: Callable[[Any, Any, Any], RestartResult]) -> int:
    """Open the runtime, build the single-instance lock, delegate, and render."""
    runtime, journal, audit = open_runtime(args)
    checkout = pathlib.Path(args.checkout).resolve()
    lock = SingleInstanceLock(runtime, checkout_key=checkout_key(checkout),
                              controller_version=CONTROLLER_VERSION)
    try:
        result = op_call(journal, audit, lock)
    finally:
        journal.close()
    return _emit_restart_result(args, result)


def cmd_owner_restart(args: Any) -> int:
    """`owner-restart`: audited HALTED -> IDLE owner_explicit_restart (M0-T107)."""
    return _restart_cli(args, owner_restart)


def cmd_resume_after_answer(args: Any) -> int:
    """`resume-after-answer`: audited WAIT_FOR_OWNER -> PREFLIGHT
    owner_answer_validated (the held-prompt case stays `resume-pending-prompt`)."""
    return _restart_cli(args, owner_answer_resume)


def cmd_acknowledge_emergency_stop(args: Any) -> int:
    """`acknowledge-emergency-stop`: STRONGER audited EMERGENCY_STOPPED -> IDLE
    owner_explicit_restart, gated on the explicit flag AND the journal token."""
    def _ack(journal: Any, audit: Any, lock: Any) -> RestartResult:
        return acknowledge_emergency_stop(
            journal, audit, lock,
            acknowledged=bool(getattr(args, "acknowledge_emergency_stop", False)),
            confirm_token=getattr(args, "confirm_emergency_token", "") or "")
    return _restart_cli(args, _ack)


def register_restart_verbs(sub: Any, add_common: Callable[[Any], None]) -> None:
    """Register the three operator-recovery verbs on the existing command surface
    (R034: no parallel CLI). `cli.py` calls this alongside the other
    `register_*_verbs`."""
    for name, handler, help_text in (
        ("owner-restart", cmd_owner_restart,
         "explicit operator exit from HALTED: fires the audited "
         "owner_explicit_restart transition to IDLE, fail-closed (live)"),
        ("resume-after-answer", cmd_resume_after_answer,
         "explicit operator resume of a WAIT_FOR_OWNER owner-question parking: "
         "fires the audited owner_answer_validated transition to PREFLIGHT (live)"),
    ):
        parser = sub.add_parser(name, help=help_text)
        add_common(parser)
        parser.set_defaults(func=handler)

    ack = sub.add_parser(
        "acknowledge-emergency-stop",
        help="explicit STRONGER operator exit from EMERGENCY_STOPPED: fires the "
             "audited owner_explicit_restart transition to IDLE. Requires the "
             "--acknowledge-emergency-stop flag AND the journal's "
             "--confirm-emergency-token; never automatic or an ordinary restart "
             "(live)")
    add_common(ack)
    ack.add_argument(
        "--acknowledge-emergency-stop", action="store_true",
        help="explicit acknowledgment that an EMERGENCY_STOPPED run is being left; "
             "required, and never a default")
    ack.add_argument(
        "--confirm-emergency-token", default="",
        help="this journal's emergency-stop confirmation token (printed on a "
             "mismatch); binds the acknowledgment to the recorded emergency-stop "
             "incident so it cannot be triggered by habit or a script default")
    ack.set_defaults(func=cmd_acknowledge_emergency_stop)
