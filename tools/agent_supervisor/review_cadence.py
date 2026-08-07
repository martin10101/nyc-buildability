#!/usr/bin/env python3
"""Codex review-cadence policy (D-010 0A.3; R084).

0A.3 is explicit: Codex reviews MEANINGFUL checkpoints, not every keystroke,
command, or ordinary commit. This module is the single deterministic authority
that decides whether a fresh ephemeral Codex review is warranted at a given
checkpoint, and it answers in BOTH directions:

* a meaningful checkpoint (any of the 0A.3 default review points) -> review;
* a checkpoint whose only signal is a passing formatter/linter/unit-test result
  that deterministic code already proves -> DO NOT spend a review (0A.3 final
  rule; the controller prefers deterministic tools over model calls, 0A.7).

The policy takes no free text and reads no untrusted material: it consumes a
small set of objective boolean signals the supervisor derives itself from the
checkpoint and the deterministic evidence it collected. Nothing here invokes a
model, launches a process, or mutates state - it only classifies.
"""
from __future__ import annotations

import dataclasses
from typing import Any, Mapping

#: The 0A.3 default review points, in the directive's listed order. Each maps to
#: one objective signal on `CheckpointSignals`.
REVIEW_TRIGGERS: tuple[str, ...] = (
    "unit_complete",
    "before_merge",
    "material_correction",
    "security_sensitive_change",
    "architectural_interface_change",
    "deterministic_evidence_conflict",
    "unclassified_next_action",
)

#: trigger id -> the `CheckpointSignals` attribute that raises it.
_TRIGGER_FIELD: Mapping[str, str] = {
    "unit_complete": "unit_complete",
    "before_merge": "before_merge",
    "material_correction": "material_correction",
    "security_sensitive_change": "security_sensitive_change",
    "architectural_interface_change": "architectural_interface_change",
    "deterministic_evidence_conflict": "deterministic_evidence_conflict",
    "unclassified_next_action": "cannot_classify_next_action",
}


class CadenceError(ValueError):
    """A cadence input was malformed. Fail closed rather than guess intent."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclasses.dataclass(frozen=True)
class CheckpointSignals:
    """Objective, supervisor-derived signals for one checkpoint (0A.3).

    Every field is a fact the supervisor establishes deterministically (from the
    lifecycle, the diff, or the evidence it collected), never a worker claim.
    `only_deterministic_pass` is the guard case: True when the ONLY thing that
    happened is a passing formatter/linter/unit-test that deterministic code
    already proves - the exact situation 0A.3 says must NOT trigger a review.
    """

    unit_complete: bool = False
    before_merge: bool = False
    material_correction: bool = False
    security_sensitive_change: bool = False
    architectural_interface_change: bool = False
    deterministic_evidence_conflict: bool = False
    cannot_classify_next_action: bool = False
    only_deterministic_pass: bool = False

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "CheckpointSignals":
        allowed = {f.name for f in dataclasses.fields(cls)}
        unknown = sorted(set(data) - allowed)
        if unknown:
            raise CadenceError("unknown_signal",
                               f"unrecognized cadence signal(s): {unknown}")
        for name, value in data.items():
            if not isinstance(value, bool):
                raise CadenceError(
                    "non_boolean_signal",
                    f"signal {name!r} must be a bool, got {type(value).__name__}")
        return cls(**data)


@dataclasses.dataclass(frozen=True)
class CadenceDecision:
    """Whether to review, which 0A.3 triggers fired, and why."""

    review: bool
    triggers: tuple[str, ...]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {"review": self.review, "triggers": list(self.triggers),
                "reason": self.reason}


DETERMINISTIC_PASS_REASON = (
    "the only signal is a passing formatter/linter/unit-test that deterministic "
    "code already proves; 0A.3 forbids spending a Codex review merely to restate it")

NO_TRIGGER_REASON = (
    "no 0A.3 review trigger fired at this checkpoint; an ordinary keystroke, "
    "command, or commit does not warrant a review")


def decide_review(signals: CheckpointSignals) -> CadenceDecision:
    """Decide whether a fresh ephemeral Codex review is warranted (0A.3).

    A meaningful checkpoint always wins: if any 0A.3 trigger fired, the review
    happens even when a deterministic check also passed. Only when NO trigger
    fired does the deterministic-pass guard apply, and then the answer is a
    reasoned refusal - never a silent skip.
    """
    fired = tuple(t for t in REVIEW_TRIGGERS if getattr(signals, _TRIGGER_FIELD[t]))
    if fired:
        return CadenceDecision(review=True, triggers=fired,
                               reason="meaningful checkpoint (0A.3): " + ", ".join(fired))
    if signals.only_deterministic_pass:
        return CadenceDecision(review=False, triggers=(), reason=DETERMINISTIC_PASS_REASON)
    return CadenceDecision(review=False, triggers=(), reason=NO_TRIGGER_REASON)
