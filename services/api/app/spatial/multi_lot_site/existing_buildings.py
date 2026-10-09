"""Existing buildings in a multi-lot site: carried per tax lot, never combined (B-07; M2-07).

Each selected lot keeps its own B-05 existing zoning floor area result
(``app.profile.existing_floor_area``) exactly as given: the same object, with its value or
its "Unknown" and reason, its set-aside figures and its zoning-lot citations. Nothing here
adds the lots' figures together, picks one, or subtracts anything; a combined existing floor
area would need the zoning-lot scope that B-05 records as not established. A lot without
evidence is listed as "not supplied", never dropped.
"""

from __future__ import annotations

from collections.abc import Sequence

from .combination import lots_text
from .inputs import SiteLot
from .results import EXISTING_ATTACHED, EXISTING_NOT_SUPPLIED, LotExistingBuilding

__all__ = ["PER_LOT_NOTE", "attach_existing_buildings"]

PER_LOT_NOTE = (
    "Existing buildings are kept for each tax lot. Their floor areas are not added up across "
    "lots, and nothing is subtracted here."
)


def attach_existing_buildings(lots: Sequence[SiteLot]) -> tuple[LotExistingBuilding, ...]:
    """One entry per selected lot, in selection order."""
    entries = []
    for lot in lots:
        if lot.existing_floor_area is None:
            entries.append(LotExistingBuilding(
                lot.bbl, EXISTING_NOT_SUPPLIED, None,
                f"No existing-building evidence was supplied for {lots_text([lot.bbl])}; its "
                "existing zoning floor area is unknown. Check needed."))
        else:
            entries.append(LotExistingBuilding(lot.bbl, EXISTING_ATTACHED,
                                               lot.existing_floor_area, None))
    return tuple(entries)
