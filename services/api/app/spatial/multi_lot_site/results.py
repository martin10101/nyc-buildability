"""Result records for multi-lot site math (queue item B-07, plan M2-05, §3 step 2, §4).

Coordinates (``CombinedOutline.exterior``) are internal, in EPSG:2263 feet, for diagrams and
the DXF; they are never shown to the architect (plan §4 "Coordinates").
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from app.profile.existing_floor_area import ExistingFloorAreaResult
from app.spatial.frontage_street_width import SiteStreetWidths
from app.spatial.site_geometry import SiteGeometry, SourcedValue
from app.spatial.site_geometry.inputs import Point2

from .inputs import CondoOrigin, SiteLot

__all__ = [
    "COMBINATION_NOT_OFFERED",
    "COMBINATION_OFFERED",
    "COMBINATION_SINGLE_LOT",
    "EXISTING_ATTACHED",
    "EXISTING_NOT_SUPPLIED",
    "ORIGIN_CONDO_BASE_LOT",
    "ORIGIN_TAX_LOT",
    "SELECTION_ALL",
    "SELECTION_STATEMENT",
    "SELECTION_SUBSET",
    "ZONING_LOT_CHECK_NEEDED",
    "ZONING_LOT_CHECK_NEEDED_LABEL",
    "Combination",
    "CombinedOutline",
    "LotChoice",
    "LotChoiceEntry",
    "LotExistingBuilding",
    "MultiLotSite",
    "NotListed",
    "SharedLine",
    "ZoningLotStatus",
]

# Study contract vocabulary (packages/contracts/schemas/v1/study.schema.json lot_selection).
SELECTION_ALL = "all"
SELECTION_SUBSET = "subset"
SELECTION_STATEMENT = "Based on the lots you selected — the app does not verify the zoning lot"
COMBINATION_SINGLE_LOT = "single_lot"
COMBINATION_OFFERED = "offered"
COMBINATION_NOT_OFFERED = "not_offered"

ORIGIN_TAX_LOT = "tax_lot"
ORIGIN_CONDO_BASE_LOT = "condo_base_lot"

EXISTING_ATTACHED = "attached"
EXISTING_NOT_SUPPLIED = "not_supplied"

# The only zoning-lot status this step can give: nothing here verifies a zoning lot.
ZONING_LOT_CHECK_NEEDED = "check_needed"
ZONING_LOT_CHECK_NEEDED_LABEL = "Check needed"


@dataclass(frozen=True)
class LotChoiceEntry:
    """One tax lot offered in the lot choice, with its approximate size (plan §3 step 2)."""

    lot: SiteLot
    size: SourcedValue
    origin: str = ORIGIN_TAX_LOT
    condo: CondoOrigin | None = None

    @property
    def bbl(self) -> str:
        return self.lot.bbl


@dataclass(frozen=True)
class NotListed:
    """An entered BBL that is not offered as a tax lot of land, and why."""

    bbl: str
    reason: str


@dataclass(frozen=True)
class LotChoice:
    """"This property has N lots: use all (default), or pick" (plan §3 step 2)."""

    entries: tuple[LotChoiceEntry, ...]
    not_listed: tuple[NotListed, ...] = ()
    notes: tuple[str, ...] = ()

    @property
    def bbls(self) -> tuple[str, ...]:
        return tuple(entry.bbl for entry in self.entries)


@dataclass(frozen=True)
class SharedLine:
    """A lot line two selected lots share; it is removed from the combined outline."""

    first_bbl: str
    second_bbl: str
    length_ft: float


@dataclass(frozen=True)
class Combination:
    """Whether the selected lots can be combined: one block and touching (plan §3 step 2).

    ``reason`` is plain English and set exactly when ``status`` is not offered.
    """

    status: str
    reason: str | None
    same_block: bool
    touching: bool | None
    shared_lines: tuple[SharedLine, ...] = ()


@dataclass(frozen=True)
class CombinedOutline:
    """The selected lots' outlines joined, with the lines between them removed."""

    lot_bbls: tuple[str, ...]
    exterior: tuple[Point2, ...]
    source: str
    shared_lines: tuple[SharedLine, ...]
    lots_outline_area_sq_ft: float
    statement: str


@dataclass(frozen=True)
class LotExistingBuilding:
    """One selected lot's existing-building fact (B-05), carried as it is.

    ``result`` is the B-05 result object itself, never copied, added to another lot's or
    subtracted from anything. ``status`` is ``not_supplied`` when no evidence was given.
    """

    bbl: str
    status: str
    result: ExistingFloorAreaResult | None
    note: str | None


@dataclass(frozen=True)
class ZoningLotStatus:
    """The zoning-lot status of the selection: always "Check needed" here.

    ``recorded_mentions`` are records that mention a zoning lot (flag only, plan P-2), each
    ``{document_ref, tax_lots, text, query_ref, retrieved_at}``. ``named_lots_not_selected``
    are tax lots those records name that the architect did not select.
    """

    status: str
    label: str
    statement: str
    reason: str
    recorded_mentions: tuple[Mapping[str, object], ...]
    named_lots_not_selected: tuple[str, ...]
    verified: bool = False


@dataclass(frozen=True)
class MultiLotSite:
    """Site facts for the lots the architect selected (plan §3 step 2, §4 "Multi-lot sites").

    ``geometry`` is the B-03 site geometry of the combined outline (frontage along its
    outside streets, lot type, depth, area against the recorded areas); None when the
    combination is not offered. ``lot_area_sum`` is the sum of the recorded lot areas
    (City records) or unknown. ``existing_buildings`` has one entry per selected lot.
    """

    selection_mode: str
    selected_bbls: tuple[str, ...]
    statement: str
    lots: tuple[LotChoiceEntry, ...]
    combination: Combination
    outline: CombinedOutline | None
    geometry: SiteGeometry | None
    lot_area_sum: SourcedValue
    street_widths: SiteStreetWidths | None
    existing_buildings: tuple[LotExistingBuilding, ...]
    zoning_lot: ZoningLotStatus
    notes: tuple[str, ...]
    parameters: Mapping[str, object] = field(default_factory=dict)
    provenance: Mapping[str, object] = field(default_factory=dict)
