#!/usr/bin/env python3
"""Owner-touch accounting: the S16.7 budget, which authorizes nothing (D-007).

`OwnerTouchLedger` counts the moments the owner WOULD have had to act - would-be
synchronous stops and blocking asks - and nothing else. It is a MEASUREMENT, and
the whole point of keeping it in its own module is that the measurement and the
thing being measured stay separable: this file imports no policy engine, no
grant constructor, and no tier table, so reading or writing the budget can never
widen authority, mint a grant, or move a tier. A source-level test asserts that
of `loop.py` AND of this file.

Split out of `loop.py` by M0-T079 under the modularity rule
(`docs/CODE_MODULARITY_POLICY.md`): the loop owns the S7 wiring, and owner-touch
accounting changes for entirely different reasons. `loop.py` re-exports every
name here, so every existing caller and test is unchanged.
"""
from __future__ import annotations

import dataclasses
from typing import Any

from .errors import LoopError
from .models import to_utc_iso

TOUCH_SYNCHRONOUS_STOP = "synchronous_stop"
TOUCH_BLOCKING_ASK = "blocking_ask"
TOUCH_SUPERVISED_APPROVAL = "supervised_mode_approval"
TOUCH_NOTIFY = "notify"

#: Kinds that count against the S16.7 budget. Supervised-mode approvals are a
#: property of the DEBUGGING mode, not of the target operating mode, so they are
#: recorded and reported but never counted - counting them would make the budget
#: measure the wrong thing. NOTIFY never blocks and never counts.
COUNTED_TOUCH_KINDS: frozenset[str] = frozenset({
    TOUCH_SYNCHRONOUS_STOP, TOUCH_BLOCKING_ASK,
})

OWNER_TOUCH_KEY = "owner_touch_ledger"


@dataclasses.dataclass(frozen=True)
class OwnerTouch:
    """One moment the owner would have had to act."""

    kind: str
    reason_code: str
    reason: str
    cycle: int
    counted: bool
    basis: str = ""
    at_utc: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class BudgetReport:
    """What the counter measured. It authorizes nothing (S16.7)."""

    budget: int
    counted: int
    within_budget: bool
    excess: int
    touches: tuple[OwnerTouch, ...]
    authorizes_nothing: bool = True
    note: str = (
        "The budget is a MEASUREMENT. Every excess stop must be dispositioned either as an "
        "accepted permanent gate or as a PROPOSED deterministic policy change that has "
        "passed security and control-plane review, replay testing, and explicit owner "
        "approval. The budget itself authorizes nothing (D-007 S16.7).")

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        data["touches"] = [t.to_dict() for t in self.touches]
        return data


class OwnerTouchLedger:
    """Durable count of would-be synchronous stops.

    Persisted in the journal's state table keyed by run, so a restart neither
    loses a touch nor counts one twice. It exposes no mutator of policy, of
    authority, or of any grant: reading this ledger can never widen anything.
    """

    def __init__(self, journal: Any, *, run_id: str, budget: int) -> None:
        self.journal = journal
        self.run_id = run_id
        self.budget = int(budget)

    def _key(self) -> str:
        return f"{OWNER_TOUCH_KEY}/{self.run_id}"

    def all_touches(self) -> tuple[OwnerTouch, ...]:
        raw = self.journal.get_state(self._key(), [])
        if not isinstance(raw, list):
            return ()
        known = {f.name for f in dataclasses.fields(OwnerTouch)}
        return tuple(OwnerTouch(**{k: v for k, v in item.items() if k in known})
                     for item in raw if isinstance(item, dict))

    def record(self, kind: str, *, reason_code: str, reason: str, cycle: int,
               basis: str = "") -> OwnerTouch:
        if kind not in (TOUCH_SYNCHRONOUS_STOP, TOUCH_BLOCKING_ASK,
                        TOUCH_SUPERVISED_APPROVAL, TOUCH_NOTIFY):
            raise LoopError("unknown_touch_kind", f"{kind!r} is not an owner-touch kind")
        touch = OwnerTouch(
            kind=kind, reason_code=reason_code, reason=reason, cycle=cycle,
            counted=kind in COUNTED_TOUCH_KINDS, basis=basis, at_utc=to_utc_iso())
        existing = [t.to_dict() for t in self.all_touches()]
        existing.append(touch.to_dict())
        self.journal.set_state(self._key(), existing)
        return touch

    def counted(self) -> int:
        return sum(1 for t in self.all_touches() if t.counted)

    def report(self) -> BudgetReport:
        touches = self.all_touches()
        counted = sum(1 for t in touches if t.counted)
        return BudgetReport(
            budget=self.budget,
            counted=counted,
            within_budget=counted <= self.budget,
            excess=max(0, counted - self.budget),
            touches=touches)
