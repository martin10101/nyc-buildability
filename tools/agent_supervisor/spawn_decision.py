"""Goldilocks spawn decision: main-session / spawn / resume / fork / split /
recon (D-024 Phase C item 3, M0-T090).

Encodes the owner's sizing rule (D-024 s5.5, s6): no micro-spawn churn (do
not spawn when startup/context rereading likely costs more than doing the
work in the main session), no mega-assignments (oversized work splits at
seams BEFORE dispatch), resume a healthy resumable subagent for follow-up
work in the same coherent assignment instead of paying a second startup
cost, NEVER resume an overloaded/confused context merely to save startup
cost, and fork only when inheriting the parent's context and prompt cache is
genuinely beneficial AND the parent context is clean — a bloated parent is
not forked by default.

Model routing follows s6: a lower-tier model is selected only when its
context size and demonstrated capability fit the cohesive assignment; model
cost alone never justifies a model whose window will not hold the work
coherently. Unknown windows/capability fail conservative.

Decisions are records with reasons — the shadow-mode controller records
them; nothing here spawns, resumes, stops, or messages any agent (R595
unchanged).

Supervisor-freeze qualifying evidence: D-024-R101.
"""
from __future__ import annotations

import dataclasses

from .startup_overhead import OverheadCalibration
from .workload_classifier import (
    COHESIVE_SUBAGENT,
    MAIN_SESSION,
    OVERSIZED_SPLIT,
    UNKNOWN_RECON,
    WorkloadClassification,
)

DECIDE_STAY_MAIN = "stay-main"
DECIDE_SPAWN_NEW = "spawn-new"
DECIDE_RESUME_EXISTING = "resume-existing"
DECIDE_FORK_PARENT = "fork-parent"
DECIDE_SPLIT_FIRST = "split-first"
DECIDE_RECON_FIRST = "recon-first"

#: Closed decision vocabulary.
SPAWN_DECISIONS: tuple[str, ...] = (
    DECIDE_STAY_MAIN, DECIDE_SPAWN_NEW, DECIDE_RESUME_EXISTING,
    DECIDE_FORK_PARENT, DECIDE_SPLIT_FIRST, DECIDE_RECON_FIRST)


class SpawnDecisionError(ValueError):
    """Typed error for spawn decisions (code + message)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclasses.dataclass(frozen=True)
class ExistingSubagentHealth:
    """External-evidence view of a resumable subagent (D-024 s6). The
    controller judges health from telemetry/evidence; the worker is never
    asked to self-assess a quota."""

    assignment_id: str
    same_coherent_assignment: bool = False
    healthy: bool = False
    overloaded_or_confused: bool = False


@dataclasses.dataclass(frozen=True)
class ParentContextState:
    """What forking would inherit (D-024 s6): fork only when inheritance and
    prompt-cache reuse are genuinely beneficial AND the parent is clean."""

    context_clean: bool = False
    inheritance_beneficial: bool = False


@dataclasses.dataclass(frozen=True)
class SpawnDecision:
    decision: str
    reason_code: str
    reason: str
    classification: WorkloadClassification | None = None

    def to_dict(self) -> dict[str, object]:
        data: dict[str, object] = {
            "decision": self.decision,
            "reason_code": self.reason_code,
            "reason": self.reason,
        }
        if self.classification is not None:
            data["classification"] = dataclasses.asdict(self.classification)
        return data


def decide_spawn(
    classification: WorkloadClassification,
    *,
    calibration: OverheadCalibration | None = None,
    existing: ExistingSubagentHealth | None = None,
    parent: ParentContextState | None = None,
) -> SpawnDecision:
    """Deterministic Goldilocks decision from the structural classification
    plus controller-held evidence. Precedence:

    1. oversized -> split-first (never dispatched whole);
    2. unknown -> recon-first (cheapest bounded sizing step);
    3. main-session -> stay-main (micro-spawn churn costs more than it
       saves; the calibration medians document that startup cost);
    4. cohesive + healthy same-assignment resumable subagent ->
       resume-existing (retains its history instead of starting over);
       an overloaded/confused subagent is NEVER resumed merely to save
       startup cost — it lands and a fresh bounded unit takes over;
    5. cohesive + clean parent whose inheritance genuinely helps ->
       fork-parent; a bloated parent is not forked by default;
    6. otherwise -> spawn-new.
    """
    if classification.work_class == OVERSIZED_SPLIT:
        return SpawnDecision(
            DECIDE_SPLIT_FIRST, "oversized",
            "oversized/cross-boundary work is split at natural graph/"
            "ownership/test seams before dispatch (D-024 s5.5): "
            + classification.reason, classification)
    if classification.work_class == UNKNOWN_RECON:
        return SpawnDecision(
            DECIDE_RECON_FIRST, "unknown",
            "unknown work receives the cheapest bounded sizing/"
            "reconnaissance step before a writer is assigned (D-024 s5.5): "
            + classification.reason, classification)
    if classification.work_class == MAIN_SESSION:
        note = ""
        if calibration and calibration.observations:
            note = (f" (calibrated startup overhead across "
                    f"{calibration.observations} observation(s) documents the "
                    f"repeated read-in cost a fresh spawn would pay)")
        return SpawnDecision(
            DECIDE_STAY_MAIN, "micro_spawn_churn",
            "work stays in the main session; a fresh subagent would pay "
            "startup/read-in cost exceeding the work itself" + note,
            classification)
    if classification.work_class != COHESIVE_SUBAGENT:
        raise SpawnDecisionError(
            "bad_classification",
            f"unrecognized work class {classification.work_class!r}")

    if existing is not None and existing.same_coherent_assignment:
        if existing.overloaded_or_confused:
            return SpawnDecision(
                DECIDE_SPAWN_NEW, "unhealthy_not_resumed",
                f"subagent {existing.assignment_id!r} is the same coherent "
                f"assignment but external evidence shows an overloaded/"
                f"confused context; it is not resumed merely to save startup "
                f"cost (D-024 s6)", classification)
        if existing.healthy:
            return SpawnDecision(
                DECIDE_RESUME_EXISTING, "resume_healthy",
                f"follow-up work in the same coherent assignment resumes the "
                f"healthy subagent {existing.assignment_id!r} so it retains "
                f"its history instead of paying a second startup/read-in "
                f"cost (D-024 s6)", classification)

    if parent is not None and parent.inheritance_beneficial:
        if parent.context_clean:
            return SpawnDecision(
                DECIDE_FORK_PARENT, "fork_beneficial",
                "parent-context inheritance and prompt-cache reuse are "
                "genuinely beneficial and the parent context is clean "
                "(D-024 s6)", classification)
        return SpawnDecision(
            DECIDE_SPAWN_NEW, "bloated_parent_not_forked",
            "inheritance would help but the parent context is not clean; a "
            "bloated parent is not forked by default (D-024 s6)",
            classification)

    return SpawnDecision(
        DECIDE_SPAWN_NEW, "cohesive_new_unit",
        "one cohesive ownership unit gets one fresh bounded subagent from "
        "investigation through its natural proof (D-024 s5.5)",
        classification)


@dataclasses.dataclass(frozen=True)
class ModelFit:
    ok: bool
    reason_code: str
    reason: str


def model_fit(
    *,
    resolved_model: str,
    model_context_window: int | None,
    packet_target_tokens: int,
    demonstrated_capable: bool,
    headroom_factor: int = 4,
) -> ModelFit:
    """A lower-tier model is selected only when its context size and
    demonstrated capability fit the cohesive assignment (D-024 s6).

    Conservative on unknowns: an unknown window or undemonstrated capability
    refuses the routing rather than guessing. ``headroom_factor`` demands the
    window hold several packets' worth of working context, since the packet
    is only the STARTING context of real work — a policy knob, not a capacity
    claim.
    """
    if packet_target_tokens <= 0:
        raise SpawnDecisionError("bad_packet",
                                 "packet_target_tokens must be positive")
    if headroom_factor < 1:
        raise SpawnDecisionError("bad_headroom",
                                 "headroom_factor must be >= 1")
    if not demonstrated_capable:
        return ModelFit(
            False, "capability_undemonstrated",
            f"{resolved_model or 'the candidate model'} has not demonstrated "
            f"it can satisfy this assignment class; route to a model that "
            f"has (D-024 s6)")
    if model_context_window is None:
        return ModelFit(
            False, "window_unknown",
            "the candidate model's context window is unknown; unknown is "
            "never treated as large enough (D-024 s5.4 discipline)")
    needed = packet_target_tokens * headroom_factor
    if model_context_window < needed:
        return ModelFit(
            False, "window_too_small",
            f"context window {model_context_window} cannot coherently hold "
            f"the assignment (packet target {packet_target_tokens} with "
            f"headroom factor {headroom_factor} needs >= {needed}); model "
            f"cost alone does not justify a model that will not fit "
            f"(D-024 s6)")
    return ModelFit(
        True, "fits",
        f"window {model_context_window} holds the packet target "
        f"{packet_target_tokens} with headroom and capability is "
        f"demonstrated")
