"""Plain inputs for multi-lot site math (queue item B-07, plan M2-05).

One :class:`SiteLot` per tax lot: its EPSG:2263 outline (or why there is none), its city
records, its zoning districts (for the B-04 street-width exceptions) and its existing
building fact from B-05, which is carried per lot and never combined. ``adapters.py``
builds these from connector results; tests build them directly.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from app.connectors.bbl import BBLValidationError, normalize_bbl
from app.profile.existing_floor_area import ExistingFloorAreaResult
from app.spatial.frontage_street_width import LotZoningContext
from app.spatial.site_geometry import CityRecordLot, LotOutline

__all__ = ["CondoOrigin", "SiteLot", "block_of", "lot_number"]


def _canonical(bbl: object) -> str:
    try:
        normalized = normalize_bbl(bbl)
    except BBLValidationError as exc:
        raise ValueError(f"not a valid tax lot BBL: {bbl!r} ({exc})") from None
    if normalized.canonical != bbl:
        raise ValueError(f"BBL must be the canonical 10-digit string, got {bbl!r}")
    return normalized.canonical


def block_of(bbl: str) -> tuple[int, int]:
    """(borough, block) of a canonical BBL."""
    normalized = normalize_bbl(bbl)
    return normalized.borough, normalized.block


def lot_number(bbl: str) -> int:
    return normalize_bbl(bbl).lot


@dataclass(frozen=True)
class CondoOrigin:
    """Why a base lot is in the lot choice: it is a recorded base lot of a condo billing lot.

    Copied from the accepted resolution seam (``app.connectors.condo_base_lot``): the billing
    BBL, the condo key and number, the source and datasets and when they were read.
    """

    billing_bbl: str
    condo_key: str | None
    condo_number: str | None
    source_id: str | None
    dataset_ids: tuple[str, ...]
    retrieved_at: str | None


@dataclass(frozen=True)
class SiteLot:
    """One tax lot as the multi-lot step needs it.

    ``outline`` is the lot's EPSG:2263 tax-map outline, or None with ``outline_refusal``
    saying why there is none. ``city_records`` are its PLUTO (or DOF) dimensions; None when
    none were found (a condo base lot has no PLUTO row). ``existing_floor_area`` is the B-05
    result for this tax lot, passed through untouched; None when no evidence was supplied.
    """

    bbl: str
    outline: LotOutline | None
    outline_refusal: str | None = None
    city_records: CityRecordLot | None = None
    zoning: LotZoningContext | None = None
    existing_floor_area: ExistingFloorAreaResult | None = None
    provenance: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _canonical(self.bbl)
        if self.outline is None and not self.outline_refusal:
            raise ValueError(f"tax lot {self.bbl}: give an outline or the reason it has none")
        fact = self.existing_floor_area.fact if self.existing_floor_area else None
        if fact is not None and fact.get("lot_bbl") != self.bbl:
            raise ValueError(
                f"tax lot {self.bbl}: the existing floor area fact belongs to "
                f"{fact.get('lot_bbl')!r}; a lot's existing building is never moved to another lot"
            )
