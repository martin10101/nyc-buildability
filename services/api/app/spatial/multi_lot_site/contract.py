"""Study-contract shapes for the lot choice and the selection (B-07).

Maps onto ``packages/contracts/schemas/v1/study.schema.json``: ``lots[]`` ($defs/lot: each
tax lot, its approximate size with the measurement rank and label, and whether it is
selected) and ``lot_selection`` (mode, the exact statement, and the combination status with
its reason). No new contract fields: the zoning-lot status, the per-lot existing buildings
and the geometry stay in the Python result until a contract task adds slots for them.
"""

from __future__ import annotations

from collections.abc import Iterable

from app.profile.measurement import measurement

from .results import LotChoice, MultiLotSite

__all__ = ["study_lot_selection", "study_lots"]


def study_lots(choice: LotChoice, selected_bbls: Iterable[str]) -> list[dict]:
    """Every listed tax lot as a study ``lots[]`` item."""
    selected = set(selected_bbls)
    return [{
        "bbl": entry.bbl,
        "approximate_lot_area_sq_ft": entry.size.value,
        "size_measurement": measurement(entry.size.rank),
        "selected": entry.bbl in selected,
    } for entry in choice.entries]


def study_lot_selection(site: MultiLotSite) -> dict:
    """The study ``lot_selection`` object for a derived selection."""
    return {
        "mode": site.selection_mode,
        "statement": site.statement,
        "combination": {"status": site.combination.status, "reason": site.combination.reason},
    }
