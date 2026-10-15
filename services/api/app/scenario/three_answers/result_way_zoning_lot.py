"""The ACRIS zoning-lot citation projection and its plain-words helpers (engine-side
isolation, task M5-T167 G-6; moved verbatim out of :mod:`result_way_bridge`).

Backlog DB-232. :func:`zoning_lot_citation` projects the connector/classifier's
:class:`~app.profile.zoning_lot_index.ZoningLotIndex` into the scenario-local
:class:`~app.scenario.three_answers.result_way_inputs.ZoningLotCitation` (plain lot labels and
dates), so the decision module and the emitter stay decoupled from the classifier.
:mod:`result_way_bridge` keeps importing :func:`zoning_lot_citation` from here (a compatibility
facade); its call site ``gather_result_ways`` is unchanged. The ``SourceFact`` / ``LargeLotAnswer``
/ ``GatheredResult`` dataclasses do NOT move - they stay in :mod:`result_way_bridge` (NB-01
revision 5)."""

from __future__ import annotations

from app.profile.zoning_lot_index import ZoningLotIndex, ZoningLotIndexState

from .result_way_inputs import (
    ZONING_LOT_NONE_FOUND,
    ZONING_LOT_NOT_CHECKED,
    ZONING_LOT_NOT_READ,
    ZONING_LOT_OTHER_LOTS_NAMED,
    ZONING_LOT_SINGLE_LOT_ONLY,
    ZoningLotCitation,
)

__all__ = ["zoning_lot_citation"]

# The scenario citation state for each classifier state (backlog DB-232).
_CITATION_STATE_BY_INDEX = {
    ZoningLotIndexState.NOT_CHECKED: ZONING_LOT_NOT_CHECKED,
    ZoningLotIndexState.NOT_READ: ZONING_LOT_NOT_READ,
    ZoningLotIndexState.NONE_FOUND: ZONING_LOT_NONE_FOUND,
    ZoningLotIndexState.SINGLE_LOT_ONLY: ZONING_LOT_SINGLE_LOT_ONLY,
    ZoningLotIndexState.OTHER_LOTS_NAMED: ZONING_LOT_OTHER_LOTS_NAMED,
}

_MONTHS = (
    "January", "February", "March", "April", "May", "June", "July", "August", "September",
    "October", "November", "December",
)


def _human_date(iso: str | None) -> str | None:
    """A plain-English date ("2022-02-08" -> "February 8, 2022"), or None. Windows-safe (no
    platform-specific strftime directive)."""
    if not iso:
        return None
    try:
        year, month, day = iso[:10].split("-")
        return f"{_MONTHS[int(month) - 1]} {int(day)}, {int(year)}"
    except (ValueError, IndexError):
        return None


def _lot_label(lot_number: str) -> str:
    try:
        return f"lot {int(lot_number)}"
    except (TypeError, ValueError):
        return f"lot {lot_number}"


def _join_lots(items: list[str]) -> str:
    """Join plain-word lot labels: "a", "a and b", "a, b, and c". Lives beside the bridge (not the
    decision module), so the decision module holds no list-index literal."""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def zoning_lot_citation(index: ZoningLotIndex | None) -> ZoningLotCitation:
    """Project the classifier's :class:`~app.profile.zoning_lot_index.ZoningLotIndex` into the
    scenario-local :class:`ZoningLotCitation` (plain lot labels and dates), so the decision module
    and the emitter stay decoupled from the connector / classifier. None (no provider bound) ->
    the not_checked default, which adds no condition and emits no scope row.

    When more than one ZONE document names other lots, the condition cites the FIRST (the module
    never picks a 'latest'); every named lot is still aggregated into the lot lists."""
    if index is None:
        return ZoningLotCitation()
    state = _CITATION_STATE_BY_INDEX.get(index.state, ZONING_LOT_NOT_CHECKED)
    subject_label = _lot_label(index.subject_bbl[6:10]) if index.subject_bbl else None
    other_same = [_lot_label(lot.lot) for lot in index.other_same_block_lots]
    other_block = [
        f"block {int(lot.block)}, {_lot_label(lot.lot)}" for lot in index.other_block_lots
    ]
    zone = index.zone_documents[0] if index.zone_documents else None
    zone_recorded = _human_date(zone.recorded_datetime) if zone is not None else None
    reminders = {doc.doc_type for doc in index.reminder_documents}
    return ZoningLotCitation(
        state=state,
        subject_lot_label=subject_label,
        other_same_block_phrase=_join_lots(other_same) if other_same else "",
        other_block_phrase=_join_lots(other_block) if other_block else "",
        zone_crfn=zone.crfn if zone is not None else None,
        zone_recorded_date=zone_recorded,
        single_lot_recorded_date=zone_recorded,
        as_of_date=_human_date(index.as_of_date),
        has_declaration="DECL" in reminders,
        has_certificate="CERT" in reminders,
    )
