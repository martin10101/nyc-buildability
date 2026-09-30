"""Workload-sized working-turn allowances under a documented hard ceiling.

D-024 Amendment 22 property 5 (R380) + defect D3 correction (M0-T125 register):
the live 12-turn counted stop was a FIXED bound (``claude_runner.RunnerConfig.
max_turns = 12``) that reserved no final checkpoint turn, required no early
checkpoint, and was never sized from the work. The owner directive is explicit:

    "Sizes working-turn allowances from the bounded task/workload class under a
     documented hard safety ceiling; do not solve this merely by raising the
     fixed max_turns."

This module is that sizing. It consumes the EXISTING structural workload
classifier (``workload_classifier.WorkloadClassification`` — the four owner
classes, previously unwired into the launch/loop path per D3) and produces a
``TurnBudget`` that carries, for one bounded unit:

- ``working_turns`` — the class-sized allowance for productive tool use;
- ``reserved_final_turn`` — always 1, the turn reserved EXCLUSIVELY for
  mandatory checkpoint emission before exhaustion (property 3);
- ``early_checkpoint_by`` — the turn index by which the FIRST structured
  progress checkpoint must appear (property 2);
- ``incremental_checkpoint_every`` — the cadence for incremental checkpoints
  during the unit (property 2);
- ``total_turns`` — ``working_turns + reserved_final_turn``, the value that
  replaces the fixed ``max_turns`` for this unit, ALWAYS clamped to
  ``HARD_TURN_CEILING``.

Design discipline mirrors ``rotation.RotationThresholds`` and
``workload_classifier.WorkloadThresholds``: a frozen dataclass of owner-policy
numbers, ``from_controller_config`` that fails closed on unknown keys or
non-positive values, closed vocabularies, and a conservative landing for
unrecognizable shapes (never an optimistic large allowance).

Supervisor-freeze qualifying evidence: D-024-R372 (the Amendment-22 window),
D-024-R380 (property 5), M0-T125 defect D3 (VERIFIED live: 12/12 counted stop,
``workload_sizing`` zero production consumers).
"""
from __future__ import annotations

import dataclasses
import math
from collections.abc import Mapping
from typing import Any

from tools.agent_supervisor.workload_classifier import (
    COHESIVE_SUBAGENT,
    MAIN_SESSION,
    OVERSIZED_SPLIT,
    UNKNOWN_RECON,
    WORK_CLASSES,
    WorkloadClassification,
)

#: The absolute maximum turns (working + reserved) any single bounded unit may
#: receive, regardless of workload class or config. RATIONALE (documented per
#: R380): a bounded unit is bounded; work that genuinely needs more turns than
#: this is oversized and must be SPLIT before dispatch (the same principle
#: ``workload_classifier`` applies to ``oversized-split-at-seams``), never
#: handed a larger single unit. The ceiling is set well above the largest class
#: allowance so the workload class — not the ceiling — is the normal governor;
#: the ceiling only ever catches a config override or a future class table that
#: would otherwise mint an unbounded unit. It also caps worst-case provider
#: spend for one unit. It is a SAFETY ceiling, not a target: nothing sizes UP to
#: it. 40 = the largest sensible cohesive allowance (32) plus generous headroom,
#: and comfortably above the failed fixed 12 without ever being unbounded.
HARD_TURN_CEILING = 40

#: A bounded unit always reserves exactly ONE final turn for mandatory
#: checkpoint emission before exhaustion (property 3). It is never zero: a unit
#: that consumes its last working turn must still have a turn in which the
#: reserved-final-turn injection can demand the checkpoint.
RESERVED_FINAL_TURNS = 1


class TurnBudgetError(ValueError):
    """Typed error for turn-budget sizing (code + message)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclasses.dataclass(frozen=True)
class TurnAllowances:
    """Owner-policy working-turn allowances per workload class.

    These are NOT token predictions and NOT capacity claims — they are bounded
    working-turn budgets for the structural class of the unit (D-024 s5.5
    stance, shared with ``workload_classifier``). Every value is validated
    positive and within ``HARD_TURN_CEILING - RESERVED_FINAL_TURNS`` so the
    reserved final turn always fits under the hard ceiling.

    Defaults:

    - ``main-session`` (8): quick targeted work / frequent parent decisions —
      the smallest productive allowance;
    - ``cohesive-subagent`` (32): the preferred self-contained unit that owns a
      path from investigation through implementation/test — the class the live
      12-turn bound starved;
    - ``unknown-recon-first`` (6): the cheapest bounded reconnaissance step,
      taken BEFORE committing a larger allowance;
    - ``oversized-split-at-seams`` is deliberately ABSENT: such work is not
      dispatchable as one unit and ``size_turn_budget`` refuses it rather than
      sizing it (it must be split first).
    """

    main_session: int = 8
    cohesive_subagent: int = 32
    unknown_recon: int = 6

    def __post_init__(self) -> None:
        ceiling = HARD_TURN_CEILING - RESERVED_FINAL_TURNS
        for name in ("main_session", "cohesive_subagent", "unknown_recon"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise TurnBudgetError(
                    "bad_allowance",
                    f"{name} working-turn allowance must be a positive integer, "
                    f"got {value!r}")
            if value > ceiling:
                raise TurnBudgetError(
                    "allowance_over_ceiling",
                    f"{name} working-turn allowance {value} + {RESERVED_FINAL_TURNS} "
                    f"reserved turn exceeds HARD_TURN_CEILING {HARD_TURN_CEILING}; a "
                    f"unit that needs more turns must be split, never enlarged")

    def working_turns_for(self, work_class: str) -> int:
        """The working-turn allowance for a workload class (fails closed)."""
        table = {
            MAIN_SESSION: self.main_session,
            COHESIVE_SUBAGENT: self.cohesive_subagent,
            UNKNOWN_RECON: self.unknown_recon,
        }
        if work_class not in table:
            raise TurnBudgetError(
                "unsizable_class",
                f"workload class {work_class!r} has no dispatchable turn "
                f"allowance (only {sorted(table)} are sized here; "
                f"{OVERSIZED_SPLIT!r} must be split before dispatch)")
        return table[work_class]

    @classmethod
    def from_controller_config(cls, config: Any) -> "TurnAllowances":
        """Read ``[turn_budget]`` from the controller config, failing closed on
        unknown keys or non-positive values (the ``rotation.py`` pattern)."""
        raw = getattr(config, "raw", {}) or {}
        section = raw.get("turn_budget", {}) or {}
        if not isinstance(section, Mapping):
            raise TurnBudgetError("bad_section", "[turn_budget] must be a table")
        known = {f.name for f in dataclasses.fields(cls)}
        unknown = sorted(set(section) - known)
        if unknown:
            raise TurnBudgetError(
                "unknown_turn_budget_key",
                f"unrecognized [turn_budget] keys: {unknown}")
        values: dict[str, Any] = {}
        for name, value in section.items():
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise TurnBudgetError(
                    "bad_turn_budget_value",
                    f"{name} must be a positive integer, got {value!r}")
            values[name] = value
        return cls(**values)


@dataclasses.dataclass(frozen=True)
class TurnBudget:
    """One bounded unit's sized turn budget.

    ``total_turns`` is the value that replaces the fixed ``max_turns`` for the
    unit. ``dispatchable`` is False only when the workload class is oversized and
    must be split before it can be a unit at all (``stop_reason`` says why).
    """

    work_class: str
    working_turns: int
    reserved_final_turn: int
    total_turns: int
    early_checkpoint_by: int
    incremental_checkpoint_every: int
    hard_ceiling: int
    ceiling_clamped: bool
    dispatchable: bool
    reason: str
    stop_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def size_turn_budget(
    classification: WorkloadClassification,
    allowances: TurnAllowances | None = None,
) -> TurnBudget:
    """Size one bounded unit's turns from its structural workload class.

    - ``oversized-split-at-seams`` is NOT dispatchable as a single unit: the
      budget records ``dispatchable=False`` with a stop reason (split first),
      never a larger unit.
    - every other class gets ``working_turns`` from ``allowances`` plus exactly
      ``RESERVED_FINAL_TURNS`` reserved for mandatory checkpoint emission,
      clamped to ``HARD_TURN_CEILING``.
    - ``early_checkpoint_by`` = ceil(working_turns / 3), floored at 1 — the
      first structured progress checkpoint is demanded within the first third
      of the working turns (property 2);
    - ``incremental_checkpoint_every`` = ceil(working_turns / 3), floored at 1 —
      an incremental checkpoint cadence across the unit (property 2).

    Fails closed on an unknown class (the classifier's vocabulary is closed).
    """
    if not isinstance(classification, WorkloadClassification):
        raise TurnBudgetError(
            "bad_classification",
            "size_turn_budget requires a WorkloadClassification")
    work_class = classification.work_class
    if work_class not in WORK_CLASSES:
        raise TurnBudgetError(
            "unknown_class",
            f"classification carries unknown work class {work_class!r}")
    table = allowances or TurnAllowances()

    if work_class == OVERSIZED_SPLIT:
        return TurnBudget(
            work_class=work_class,
            working_turns=0,
            reserved_final_turn=RESERVED_FINAL_TURNS,
            total_turns=0,
            early_checkpoint_by=0,
            incremental_checkpoint_every=0,
            hard_ceiling=HARD_TURN_CEILING,
            ceiling_clamped=False,
            dispatchable=False,
            reason=classification.reason,
            stop_reason=(
                "work classified oversized-split-at-seams is not a single "
                "bounded unit; split it at natural seams before dispatch rather "
                "than sizing a larger unit (workload_classifier / R380)"),
        )

    working = table.working_turns_for(work_class)
    total_uncapped = working + RESERVED_FINAL_TURNS
    total = min(total_uncapped, HARD_TURN_CEILING)
    clamped = total_uncapped > HARD_TURN_CEILING
    if clamped:
        # The reserved final turn is never surrendered to the clamp; the working
        # allowance absorbs it, keeping property 3 intact under the ceiling.
        working = total - RESERVED_FINAL_TURNS
    early_by = max(1, math.ceil(working / 3))
    incremental_every = max(1, math.ceil(working / 3))
    return TurnBudget(
        work_class=work_class,
        working_turns=working,
        reserved_final_turn=RESERVED_FINAL_TURNS,
        total_turns=total,
        early_checkpoint_by=early_by,
        incremental_checkpoint_every=incremental_every,
        hard_ceiling=HARD_TURN_CEILING,
        ceiling_clamped=clamped,
        dispatchable=True,
        reason=(
            f"sized from workload class {work_class!r} "
            f"({classification.reason_code}): {working} working turns + "
            f"{RESERVED_FINAL_TURNS} reserved final checkpoint turn = "
            f"{total} total (hard ceiling {HARD_TURN_CEILING})"),
    )


def budget_for_packet(
    packet: Mapping[str, Any],
    allowances: TurnAllowances | None = None,
) -> tuple[WorkloadClassification, TurnBudget]:
    """Classify a task packet's workload and size its turn budget (M0-T126).

    A bounded task packet dispatched to a supervised worker is the
    cohesive-subagent size by construction; a packet may override with an
    explicit ``workload_class``. Returns ``(classification, budget)``. Raises
    ``TurnBudgetError`` on an unknown declared class — the caller renders it as a
    typed refusal. Keeps the derivation OUT of the CLI wiring (modularity).
    """
    declared = str(packet.get("workload_class", "") or "")
    if declared and declared not in WORK_CLASSES:
        raise TurnBudgetError(
            "bad_workload_class",
            f"packet workload_class {declared!r} is not one of {list(WORK_CLASSES)}")
    classification = WorkloadClassification(
        declared or COHESIVE_SUBAGENT,
        "declared_class" if declared else "default_cohesive",
        f"packet declared {declared!r}" if declared else
        "a bounded task packet dispatched to a supervised worker is the "
        "cohesive-subagent size by construction")
    return classification, size_turn_budget(classification, allowances)
