"""Multi-lot site math (queue item B-07; plan M2-05, §3 step 2 and §4 "Multi-lot sites").

Done when (plan M2-05): "Selecting 1, 2 or all lots updates the outline, frontage, lot type
and area correctly on test fixtures."

For the tax lots the architect selects: the lot choice with condo base lots in it, the
same-block and touching check with its reason, the combined outline with the shared lot
lines removed, and the single-lot geometry of B-03 (frontage along the outside streets, lot
type, depth, area against the summed recorded areas) and street widths of B-04 run on that
combined outline. Each lot's existing building (B-05) stays with its lot. The zoning lot is
never verified here: its status is always "Check needed". No floor area, FAR or capacity is
computed.

Modules: ``inputs`` · ``lot_choice`` · ``combination`` (one block, touching) ·
``combined_outline`` · ``street_widths`` · ``existing_buildings`` · ``zoning_lot`` ·
``derive`` (pure entry point) · ``gate`` (Lane B flag; the only entry a caller uses) ·
``adapters`` · ``contract`` (study shapes) · ``parameters`` · ``results``. Nothing calls this
package yet; a later Lane C task wires it behind ``LANE_B_ENABLED`` (off).
"""

from __future__ import annotations

from .adapters import site_lot_from_sources
from .combination import check_combination
from .contract import study_lot_selection, study_lots
from .derive import LotSelectionError, derive_multi_lot_site
from .gate import derive_multi_lot_site_if_enabled, multi_lot_site_enabled
from .inputs import CondoOrigin, SiteLot
from .lot_choice import build_lot_choice, lot_size
from .parameters import METHOD_VERSION, parameters_snapshot
from .results import (
    COMBINATION_NOT_OFFERED,
    COMBINATION_OFFERED,
    COMBINATION_SINGLE_LOT,
    EXISTING_ATTACHED,
    EXISTING_NOT_SUPPLIED,
    ORIGIN_CONDO_BASE_LOT,
    ORIGIN_TAX_LOT,
    SELECTION_ALL,
    SELECTION_STATEMENT,
    SELECTION_SUBSET,
    ZONING_LOT_CHECK_NEEDED,
    ZONING_LOT_CHECK_NEEDED_LABEL,
    Combination,
    CombinedOutline,
    LotChoice,
    LotChoiceEntry,
    LotExistingBuilding,
    MultiLotSite,
    NotListed,
    SharedLine,
    ZoningLotStatus,
)

__all__ = [
    "COMBINATION_NOT_OFFERED",
    "COMBINATION_OFFERED",
    "COMBINATION_SINGLE_LOT",
    "EXISTING_ATTACHED",
    "EXISTING_NOT_SUPPLIED",
    "METHOD_VERSION",
    "ORIGIN_CONDO_BASE_LOT",
    "ORIGIN_TAX_LOT",
    "SELECTION_ALL",
    "SELECTION_STATEMENT",
    "SELECTION_SUBSET",
    "ZONING_LOT_CHECK_NEEDED",
    "ZONING_LOT_CHECK_NEEDED_LABEL",
    "Combination",
    "CombinedOutline",
    "CondoOrigin",
    "LotChoice",
    "LotChoiceEntry",
    "LotExistingBuilding",
    "LotSelectionError",
    "MultiLotSite",
    "NotListed",
    "SharedLine",
    "SiteLot",
    "ZoningLotStatus",
    "build_lot_choice",
    "check_combination",
    "derive_multi_lot_site",
    "derive_multi_lot_site_if_enabled",
    "lot_size",
    "multi_lot_site_enabled",
    "parameters_snapshot",
    "site_lot_from_sources",
    "study_lot_selection",
    "study_lots",
]
