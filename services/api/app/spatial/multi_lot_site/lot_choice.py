"""The lot choice: the property's tax lots, condo base lots included (B-07; plan §3 step 2).

"This property has N lots: use all (default), or pick. Each lot is listed with its
approximate size. Lots are tax lots, not condo apartments." (plan §3 step 2)

- A plain tax lot is listed as entered.
- A condo BILLING lot (7501-7599) is not land: it is replaced by its recorded base lots,
  read from the accepted resolution seam (``app.connectors.condo_base_lot``). If it was not
  resolved, it is not listed and the reason says so ("Check needed"); no base lot is guessed.
- A condo UNIT lot (1001-6999) is an apartment, not a tax lot of land: not listed.

Size: the recorded lot area (City records) when there is one, else the tax-map outline area
(Approximate — tax map; plan §4: condo base lots have no PLUTO record), else Unknown.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from app.connectors.bbl import BBLValidationError
from app.connectors.condo_base_lot import (
    OUTCOME_MULTI_LOT,
    OUTCOME_RESOLVED_SINGLE,
    CondoResolution,
)
from app.connectors.dtm_condo_soda import LOT_CLASS_BILLING, LOT_CLASS_UNIT, classify_lot
from app.spatial.site_geometry import SourcedValue
from app.spatial.site_geometry.area import city_record_values, outline_area
from app.spatial.site_geometry.labels import RANK_CITY_RECORDS, unknown_value
from app.spatial.site_geometry.outline import prepare_outline

from .inputs import CondoOrigin, SiteLot
from .results import (
    ORIGIN_CONDO_BASE_LOT,
    ORIGIN_TAX_LOT,
    LotChoice,
    LotChoiceEntry,
    NotListed,
)

__all__ = ["NO_OUTLINE_SUPPLIED", "build_lot_choice", "lot_size"]

NO_OUTLINE_SUPPLIED = "No tax-map outline was supplied for this lot."
_CONDO_SIZE_NOTE = (
    "Condo base lots have no PLUTO record, so their size is approximate (tax map) unless "
    "Department of Finance dimensions are supplied."
)


def lot_size(lot: SiteLot) -> SourcedValue:
    """The lot's approximate size for the lot choice, with its §4 label."""
    recorded = city_record_values(lot.city_records).lot_area
    if recorded.known:
        return recorded
    if lot.outline is None:
        reason = lot.outline_refusal
    else:
        prepared, reason = prepare_outline(lot.outline)
        if prepared is not None:
            return outline_area(prepared.polygon.area, lot.outline.source)
    return unknown_value("sq ft", f"No recorded lot area and no usable tax-map outline: {reason}")


def _condo_origin(resolution: CondoResolution) -> CondoOrigin:
    return CondoOrigin(resolution.input_bbl, resolution.condo_key, resolution.condo_number,
                       resolution.source_id, tuple(resolution.dataset_ids),
                       resolution.retrieved_at)


def _unresolved(bbl: str, resolution: CondoResolution | None) -> NotListed:
    if resolution is None:
        why = "its base lots were not looked up"
    else:
        detail = f", {resolution.error_type}" if resolution.error_type else ""
        why = f"it was not resolved to its base lots ({resolution.outcome}{detail})"
    return NotListed(bbl, f"Condo billing lot {bbl}: {why}, so its land lots cannot be "
                          "listed. Check needed.")


def build_lot_choice(
    entered: Sequence[str],
    lots: Mapping[str, SiteLot],
    *,
    condo_resolutions: Mapping[str, CondoResolution] | None = None,
) -> LotChoice:
    """The lot choice for the BBLs entered for one property, in entered order.

    ``lots`` holds the data for each tax lot (base lots included), keyed by BBL; a lot with
    no data is still listed, with no outline and an unknown size. ``condo_resolutions`` are
    the seam's outcomes for the condo billing BBLs among ``entered``.
    """
    for key, lot in lots.items():
        if key != lot.bbl:
            raise ValueError(f"lots[{key!r}] holds tax lot {lot.bbl}")
    resolutions = condo_resolutions or {}
    entries: list[LotChoiceEntry] = []
    not_listed: list[NotListed] = []
    notes: list[str] = []
    seen: set[str] = set()

    def add(bbl: str, origin: str, condo: CondoOrigin | None) -> None:
        if bbl in seen:
            return
        seen.add(bbl)
        lot = lots.get(bbl) or SiteLot(bbl, None, NO_OUTLINE_SUPPLIED)
        entries.append(LotChoiceEntry(lot, lot_size(lot), origin, condo))

    for bbl in entered:
        try:
            kind = classify_lot(bbl)
        except BBLValidationError:
            not_listed.append(NotListed(str(bbl), "Not a valid 10-digit BBL."))
            continue
        if kind == LOT_CLASS_UNIT:
            not_listed.append(NotListed(bbl, (
                f"Lot {bbl} is a condo unit (an apartment), not a tax lot of land. Enter "
                "the condo's billing lot to list its base lots.")))
            continue
        if kind != LOT_CLASS_BILLING:
            add(bbl, ORIGIN_TAX_LOT, None)
            continue
        resolution = resolutions.get(bbl)
        if resolution is not None and resolution.input_bbl != bbl:
            raise ValueError(f"condo resolution for {resolution.input_bbl} given for {bbl}")
        if (resolution is None or not resolution.base_bbls
                or resolution.outcome not in (OUTCOME_RESOLVED_SINGLE, OUTCOME_MULTI_LOT)):
            not_listed.append(_unresolved(bbl, resolution))
            continue
        condo = _condo_origin(resolution)
        for base in resolution.base_bbls:
            add(base, ORIGIN_CONDO_BASE_LOT, condo)
        notes.append(
            f"Condo billing lot {bbl} stands for its recorded base lot(s) "
            f"{', '.join(resolution.base_bbls)} ({resolution.source_id}, read "
            f"{resolution.retrieved_at}); the base lots are listed, not the apartments.")
    if any(e.origin == ORIGIN_CONDO_BASE_LOT and e.size.rank != RANK_CITY_RECORDS
           for e in entries):
        notes.append(_CONDO_SIZE_NOTE)
    return LotChoice(tuple(entries), tuple(not_listed), tuple(notes))
