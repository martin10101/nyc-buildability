#!/usr/bin/env python3
"""Machine-meaningful refusal outcomes: exit codes + structured JSON (D-023).

Qualifying evidence (AD-093 Section 0A.10): a reproduced defect. `start --mode
limited-auto` raised a bare `NotImplementedError`, so the operator - and, worse,
any wrapper script or OS scheduled task driving the controller unattended - got a
Python traceback on stderr and an interpreter exit code that says nothing about
WHY the controller refused. Several other refusals were reported honestly in the
payload text but exited 0, which is indistinguishable from success to anything
that reads exit codes. An unattended controller whose refusals are not machine
readable cannot be supervised by a machine.

THE CONTRACT. Every refusal names exactly one outcome, and each outcome has one
stable nonzero exit code and one structured JSON payload:

    outcome               exit  meaning
    --------------------  ----  ------------------------------------------------
    halted                  10  a terminal HALT: the run is over and only an
                                explicit owner act reopens it
    unsafe                  11  integrity, authority, identity, repository,
                                toolchain, auth, or policy no longer matches
    unsupported_platform    12  this host cannot provide a precondition the run
                                requires (e.g. kill-on-close containment)
    stale_state             13  the durable state and the world disagree, or a
                                fact the run needs is missing or AMBIGUOUS
    approval_required       14  a human decision is required before anything else
                                may happen
    budget_exhausted        15  the owner-set run budget is spent (`run_budget`)
    refused_mode            16  the named mode is not enabled for this launch

Codes start at 10 so they can never collide with the interpreter's own 1/2 or
with the pre-existing generic `1` that `verify-controller` and the manifest
security halt return. `exit_code_for` raises on an unknown outcome: an
unrecognized refusal must never quietly become a success.

THE PAYLOAD. `Refusal.to_dict()` is the whole machine-readable answer -
`outcome`, `exit_code`, `reason_code`, `message`, `detail`, and the UTC instant.
It is emitted as JSON under `--json` and as plain lines otherwise, on stderr,
with NO traceback: a refusal is a decision the controller made, not a crash.
"""
from __future__ import annotations

import dataclasses
import json
import sys
from typing import Any, Mapping, Sequence, TextIO

from .models import to_utc_iso

REFUSAL_SCHEMA_VERSION = "1.0.0"

HALTED = "halted"
UNSAFE = "unsafe"
UNSUPPORTED_PLATFORM = "unsupported_platform"
STALE_STATE = "stale_state"
APPROVAL_REQUIRED = "approval_required"
BUDGET_EXHAUSTED = "budget_exhausted"
REFUSED_MODE = "refused_mode"

#: outcome -> its stable process exit code. Owner-facing contract: these numbers
#: are read by wrapper scripts and OS scheduled tasks, so they change only with a
#: documented migration, never as a side effect of an edit.
EXIT_CODES: Mapping[str, int] = {
    HALTED: 10,
    UNSAFE: 11,
    UNSUPPORTED_PLATFORM: 12,
    STALE_STATE: 13,
    APPROVAL_REQUIRED: 14,
    BUDGET_EXHAUSTED: 15,
    REFUSED_MODE: 16,
}

OUTCOMES: tuple[str, ...] = tuple(EXIT_CODES)

#: The exit code of a command that did what it was asked.
EXIT_OK = 0


class RefusalError(Exception):
    """An unknown refusal outcome was named. Never silently mapped to success."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def exit_code_for(outcome: str) -> int:
    """The exit code for an outcome. An unknown outcome RAISES (fail closed)."""
    if outcome not in EXIT_CODES:
        raise RefusalError(
            "unknown_refusal_outcome",
            f"{outcome!r} is not a documented refusal outcome; known outcomes: "
            f"{sorted(EXIT_CODES)}. An unrecognized refusal must never be reported as a "
            f"success exit code")
    return EXIT_CODES[outcome]


@dataclasses.dataclass(frozen=True)
class Refusal:
    """One refusal, in the shape a machine reads it."""

    outcome: str
    reason_code: str
    message: str
    detail: Mapping[str, Any] = dataclasses.field(default_factory=dict)
    at_utc: str = ""

    def __post_init__(self) -> None:
        exit_code_for(self.outcome)  # fail closed on an unknown outcome
        if not self.reason_code:
            raise RefusalError(
                "refusal_without_reason_code",
                "every refusal names the specific condition that caused it; a refusal "
                "with no reason code is not machine readable")
        if not self.at_utc:
            object.__setattr__(self, "at_utc", to_utc_iso())
        object.__setattr__(self, "detail", dict(self.detail or {}))

    @property
    def exit_code(self) -> int:
        return exit_code_for(self.outcome)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": REFUSAL_SCHEMA_VERSION,
            "refused": True,
            "outcome": self.outcome,
            "exit_code": self.exit_code,
            "reason_code": self.reason_code,
            "message": self.message,
            "detail": dict(self.detail),
            "at_utc": self.at_utc,
        }

    def lines(self) -> tuple[str, ...]:
        """The human view. Same facts, no traceback."""
        head = (f"REFUSED ({self.outcome}, exit {self.exit_code}): "
                f"{self.reason_code}")
        body = [head, self.message]
        for key in sorted(self.detail):
            body.append(f"  {key}: {self.detail[key]}")
        return tuple(body)


def refusal(outcome: str, *, reason_code: str, message: str,
            detail: Mapping[str, Any] | None = None) -> Refusal:
    """Build a refusal. Raises on an unknown outcome or a missing reason code."""
    return Refusal(outcome=outcome, reason_code=reason_code, message=message,
                   detail=dict(detail or {}))


def emit(item: Refusal, *, as_json: bool, stream: TextIO | None = None) -> int:
    """Print the refusal and return its exit code. Never raises on output."""
    target = stream if stream is not None else sys.stderr
    if as_json:
        print(json.dumps(item.to_dict(), indent=2, default=str), file=target)
    else:
        for line in item.lines():
            print(line, file=target)
    return item.exit_code


# --------------------------------------------------------------------------
# Classifying the controller's existing stop conditions
# --------------------------------------------------------------------------

#: Recovery classification -> refusal outcome. `recovery.classify` already names
#: the condition precisely; this only says which machine-readable bucket it lands
#: in, so the mapping stays derived rather than restated.
_RECOVERY_OUTCOMES: Mapping[str, str] = {
    "UNSAFE_OR_DRIFTED": UNSAFE,
    "AMBIGUOUS_EFFECT": STALE_STATE,
}

#: Recovery reason codes that classify SAFE_CHECKPOINT but still forbid a start.
_SAFE_BUT_BLOCKED_OUTCOMES: Mapping[str, str] = {
    "safe_but_forbidden": APPROVAL_REQUIRED,
    "deadline_restored": STALE_STATE,
}


def outcome_for_recovery(classification: str, reason_code: str = "") -> str:
    """The refusal outcome for a recovery result that forbids dispatch.

    An unrecognized classification is treated as UNSAFE rather than as a pass:
    the fail-closed direction for a verdict this table does not know is "do not
    start", never "start anyway".
    """
    if classification in _RECOVERY_OUTCOMES:
        return _RECOVERY_OUTCOMES[classification]
    if reason_code in _SAFE_BUT_BLOCKED_OUTCOMES:
        return _SAFE_BUT_BLOCKED_OUTCOMES[reason_code]
    return UNSAFE


#: Loop/state-machine refusal codes whose meaning is "the durable state and the
#: caller's idea of the world disagree". Everything else a loop refuses with is
#: an unsafe condition.
_STALE_LOOP_CODES: frozenset[str] = frozenset({
    "bad_cycle_entry_state",
    "illegal_transition",
    "forwarded_prompt_unavailable",
    "pending_prompt_uncovered",
    "pending_prompt_tampered",
    "rotate_without_pending",
})

#: Loop refusal codes that mean a human has to decide before anything continues.
_APPROVAL_LOOP_CODES: frozenset[str] = frozenset({
    "operator_declined",
    "ask_blocking",
    "stop_for_owner",
    "evidence_incomplete",
    "review_unavailable",
    "supervised_mode_operator_approval",
})


def outcome_for_loop_refusal(code: str) -> str:
    """The refusal outcome for a `LoopError` / illegal-transition code."""
    if code in _STALE_LOOP_CODES:
        return STALE_STATE
    if code in _APPROVAL_LOOP_CODES:
        return APPROVAL_REQUIRED
    if code == "budget_exhausted":
        return BUDGET_EXHAUSTED
    if code in ("halt_unsafe", "deny_and_halt"):
        return HALTED
    return UNSAFE


#: Run stop codes an UNATTENDED run cannot resolve by itself. In an attended mode
#: (shadow/supervised) parking for the owner is the expected shape of the run and
#: is reported, not refused; in the bounded unattended mode nobody is watching, so
#: the same park is a terminal refusal the caller must be able to detect.
_UNATTENDED_APPROVAL_STOPS: frozenset[str] = frozenset({
    "ask_blocking", "stop_for_owner", "evidence_incomplete", "review_unavailable",
    "operator_declined", "rotation_paused_model_unavailable",
})


def outcome_for_unattended_stop(stopped: str) -> str | None:
    """The refusal outcome for how a bounded unattended run STOPPED, or None.

    None means "this stop is not a refusal" - the run reached its cycle bound,
    completed the authorized stage, or closed a cycle normally.
    """
    if not stopped:
        return None
    if stopped == "budget_exhausted":
        return BUDGET_EXHAUSTED
    if stopped in ("halt_unsafe", "deny_and_halt"):
        return HALTED
    if stopped in _UNATTENDED_APPROVAL_STOPS:
        return APPROVAL_REQUIRED
    if stopped in ("max_cycles_reached", "stage_complete", "cycle_did_not_continue",
                   "shadow_observation_complete", "deny_and_continue",
                   "forward_suppressed"):
        return None
    return UNSAFE


def merge_into_payload(payload: dict[str, Any], item: Refusal) -> dict[str, Any]:
    """Attach a refusal to an existing command payload without hiding it."""
    payload["refusal"] = item.to_dict()
    payload["refused"] = True
    if not payload.get("stopped_because"):
        payload["stopped_because"] = f"{item.reason_code}: {item.message}"
    return payload


def document() -> Sequence[dict[str, Any]]:
    """The contract, as data - `doctor` prints it so operators can script it."""
    descriptions = {
        HALTED: "a terminal HALT; only an explicit owner act reopens the run",
        UNSAFE: "integrity, authority, identity, repository, toolchain, auth, or "
                "policy no longer matches",
        UNSUPPORTED_PLATFORM: "this host cannot provide a precondition the run requires",
        STALE_STATE: "durable state and the world disagree, or a required fact is "
                     "missing or ambiguous",
        APPROVAL_REQUIRED: "a human decision is required before anything else happens",
        BUDGET_EXHAUSTED: "the owner-set run budget is spent",
        REFUSED_MODE: "the named mode is not enabled for this launch",
    }
    return tuple({"outcome": name, "exit_code": EXIT_CODES[name],
                  "meaning": descriptions[name]} for name in OUTCOMES)
