"""The §8a hidden-issue flag layer: one flag per item, grouped (queue item B-09; plan L-11).

Plan ``docs/PRODUCT_PLAN_CURRENT_2026-09-28.md`` section 8a: hidden issues and
opportunities are "checked on every property" and each is "shown as a flag, an
opportunity, or 'Check needed' when the data is not available". A missing source produces
"Check needed", never a guess (lane prompt B, shared rules).

This module is the data-side flag layer the §8a groups share. It carries no legal meaning
and computes nothing about the law: a flag only ever reports what the sourced data already
shows, or says the source is not available. Legal determinations (what the rules permit, a
use's conformance) belong to the engine (Lane A).

Statuses:

- ``flag`` - the sourced data shows an issue worth surfacing.
- ``opportunity`` - the sourced data shows a gain worth surfacing.
- ``check_needed`` - the source is missing or not connected, so the item cannot be
  answered from the data; a reviewer must check it. This is never a negative claim.
- ``not_flagged`` - the source IS available and shows no issue (a real "checked and clear"
  determination, never the absence of data).

The plan names the first three. ``not_flagged`` is a conservative fourth state recorded so
an available-but-clear check is never confused with a missing source (B-09 report); it is a
design default, not plan text. There is no site_fact or results schema slot for the flag
layer yet, so a flag is a plain record here; wiring it into the study and a contract is a
Lane C request (as B-06 did with ``docs/lanes/requests/B-1.md``).

Pure, deterministic code: no I/O, no clock, no legal logic.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

__all__ = [
    "LABELS",
    "STATUS_CHECK_NEEDED",
    "STATUS_FLAG",
    "STATUS_NOT_FLAGGED",
    "STATUS_OPPORTUNITY",
    "STATUSES",
    "FlagGroup",
    "HiddenIssueFlag",
]

STATUS_FLAG = "flag"
STATUS_OPPORTUNITY = "opportunity"
STATUS_CHECK_NEEDED = "check_needed"
STATUS_NOT_FLAGGED = "not_flagged"
STATUSES: tuple[str, ...] = (
    STATUS_FLAG,
    STATUS_OPPORTUNITY,
    STATUS_CHECK_NEEDED,
    STATUS_NOT_FLAGGED,
)
# "Check needed" is the plan section 8a wording, copied exactly.
LABELS: Mapping[str, str] = MappingProxyType({
    STATUS_FLAG: "Flag",
    STATUS_OPPORTUNITY: "Opportunity",
    STATUS_CHECK_NEEDED: "Check needed",
    STATUS_NOT_FLAGGED: "No flag",
})


@dataclass(frozen=True)
class HiddenIssueFlag:
    """One §8a item as a flag, opportunity, check_needed or not_flagged.

    Attributes:
        item_id: a stable id, ``<group>.<item>`` (for example
            ``existing_building.larger_than_today``).
        group: the §8a group id (for example ``existing_building``).
        title: the item's plain title.
        status: one of :data:`STATUSES`.
        detail: the one line shown beside the affected results (plan section 5a: never a
            wall of warnings). For ``check_needed`` it names the missing source plainly.
        typical_source: the §8a "Typical source" for this item (what would answer it).
        evidence: the inputs this flag was drawn from, each ``{"label", "source"}`` where
            ``source`` is the provenance object (or None for an input with no dataset).
        fact_refs: the ``fact_id`` of each site fact this flag draws on, so a consumer can
            tie the flag to the facts (and to their "Out of date" status).
        exception_label: a results exception label beside the number, such as "Out of date"
            (data-version staleness from B-06), or None.
        phase: the §8a phase for this item ("1" for the existing-building group).
    """

    item_id: str
    group: str
    title: str
    status: str
    detail: str
    typical_source: str
    evidence: tuple[Mapping, ...] = ()
    fact_refs: tuple[str, ...] = ()
    exception_label: str | None = None
    phase: str = "1"

    def __post_init__(self) -> None:
        if self.status not in LABELS:
            raise ValueError(
                f"unknown flag status {self.status!r}; expected one of {list(STATUSES)}"
            )

    @property
    def status_label(self) -> str:
        return LABELS[self.status]

    @property
    def needs_check(self) -> bool:
        return self.status == STATUS_CHECK_NEEDED

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "group": self.group,
            "title": self.title,
            "status": self.status,
            "status_label": self.status_label,
            "detail": self.detail,
            "typical_source": self.typical_source,
            "evidence": [dict(item) for item in self.evidence],
            "fact_refs": list(self.fact_refs),
            "exception_label": self.exception_label,
            "phase": self.phase,
        }


@dataclass(frozen=True)
class FlagGroup:
    """One §8a group (for example the existing-building group) as its flags.

    Attributes:
        group_id: the group id (for example ``existing_building``).
        title: the group's plain title.
        lot_bbl: the tax lot (10-digit BBL) the flags are for.
        flags: the item flags, in plan order.
    """

    group_id: str
    title: str
    lot_bbl: str
    flags: tuple[HiddenIssueFlag, ...] = field(default=())

    def of_status(self, status: str) -> tuple[HiddenIssueFlag, ...]:
        return tuple(flag for flag in self.flags if flag.status == status)

    @property
    def raised(self) -> tuple[HiddenIssueFlag, ...]:
        """Items shown as a flag or an opportunity (something to surface)."""
        return tuple(
            flag for flag in self.flags
            if flag.status in (STATUS_FLAG, STATUS_OPPORTUNITY)
        )

    @property
    def checks_needed(self) -> tuple[HiddenIssueFlag, ...]:
        return self.of_status(STATUS_CHECK_NEEDED)

    def to_dict(self) -> dict:
        return {
            "group_id": self.group_id,
            "title": self.title,
            "lot_bbl": self.lot_bbl,
            "flags": [flag.to_dict() for flag in self.flags],
        }
