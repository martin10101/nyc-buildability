"""The report-side zoning-lot condition (DB-232; the G-6 report isolation, M5-T165).

Moved out of :mod:`.readers` so the document reader stays general. This module
holds:

* the marker phrase that identifies the ACRIS zoning-lot-index condition (kept in
  step with ``app.scenario.three_answers.result_way_conditions.ZONING_LOT_INDEX_MARKER``
  by a test, so the two cannot drift apart);
* :func:`zoning_lot_basis` - the ``(assumption, settled_by)`` of the shown figure's
  zoning-lot condition (re-exported by :mod:`.readers` as a compatibility facade);
* :func:`zoning_lot_open_item` - the "Zoning lot" open item built from that basis;
* :func:`page_one_zoning_lot_sentence` - the page-1 named-furniture sentence that
  names the register's INDEX ENTRY (never the instrument, D-094 R030), with every
  value read from the document's own condition.

``readers`` is imported inside the functions that use it so there is no import
cycle (``readers`` imports this module at load; this module reaches back only at
call time, when both modules are fully loaded).
"""

from __future__ import annotations

import re
from collections.abc import Mapping

from . import labels

__all__ = [
    "ZONING_LOT_EFFECT",
    "page_one_zoning_lot_sentence",
    "zoning_lot_basis",
    "zoning_lot_open_item",
]

# A phrase that appears ONLY in the ACRIS zoning-lot-index condition (other_lots_named /
# not_read wordings), matching the scenario conditions module's ZONING_LOT_INDEX_MARKER, so the
# condition is never confused with the generic zoning-lot condition on the unit limit or any other
# condition. A test holds the two in step.
_ZONING_LOT_CONDITION_MARKER = "register of recorded documents"

# The short structural effect of the zoning-lot condition (unchanged 1.4.0 output).
ZONING_LOT_EFFECT = (
    "The floor area, the apartment limit and the building option are worked for this tax lot "
    "alone; recorded documents may name it with another lot."
)

_MONTHS = {
    "january": "01", "february": "02", "march": "03", "april": "04",
    "may": "05", "june": "06", "july": "07", "august": "08",
    "september": "09", "october": "10", "november": "11", "december": "12",
}


def zoning_lot_basis(results: Mapping) -> tuple[str, str] | None:
    """The ACRIS zoning-lot condition (backlog DB-232) carried on a shown figure, as (assumption,
    settled_by), or None when no shown figure carries it. Detected by the marker phrase so it is
    never confused with the generic zoning-lot condition on the unit limit or any other condition.
    The figures carry it only in other_lots_named / not_read, so None means the figures are not
    conditional on the recorded-document index (no open item)."""
    from . import readers

    def _match(conditions) -> tuple[str, str] | None:
        for condition in conditions or []:
            if not isinstance(condition, Mapping):
                continue
            assumption = condition.get("assumption")
            if (
                condition.get("kind") == "unchecked_condition"
                and isinstance(assumption, str)
                and _ZONING_LOT_CONDITION_MARKER in assumption
            ):
                return assumption, str(condition.get("settled_by") or "")
        return None

    for name in readers.ANSWER_NAMES:
        for row in readers.present_values(readers.answer_block(results, name)):
            hit = _match(row.get("conditions"))
            if hit is not None:
                return hit
    for building in results.get("building_alternatives", []) or []:
        if not isinstance(building, Mapping):
            continue
        way = building.get("way")
        hit = _match(way.get("conditions") if isinstance(way, Mapping) else [])
        if hit is not None:
            return hit
    return None


def zoning_lot_open_item(results: Mapping) -> dict | None:
    """The "Zoning lot" open item (ordered FIRST, D-094 R029/R030) built from the
    document's condition, or ``None`` when no shown figure carries it. The reason is
    the document's own condition sentence and the resolver is its ``settled_by``."""
    basis = zoning_lot_basis(results)
    if basis is None:
        return None
    return {
        "category": "zoning_lot",
        "title": "Zoning lot",
        "effect": ZONING_LOT_EFFECT,
        "reason": basis[0],
        "resolves": basis[1],
        "status_label": labels.CONDITIONAL,
    }


def _subject_lot(results: Mapping) -> str | None:
    scope = results.get("scope")
    lot = scope.get("lot") if isinstance(scope, Mapping) else None
    value = lot.get("lot") if isinstance(lot, Mapping) else None
    return str(value) if value not in (None, "") else None


def page_one_zoning_lot_sentence(results: Mapping) -> str | None:
    """The page-1 property-specific zoning-lot sentence, naming the register's index
    ENTRY (never the instrument, D-094 R030): e.g. "the city's register lists a
    zoning lot description recorded 2022-02-08 against lots 1 and 70". Every value is
    parsed from the document's own condition; ``None`` when no shown figure carries
    the condition (then the caller shows the generic line). ``None`` too when the
    condition text cannot be parsed, so no value is invented."""
    basis = zoning_lot_basis(results)
    if basis is None:
        return None
    assumption = basis[0]
    if "zoning lot description" not in assumption.lower():
        return None
    date_match = re.search(r"recorded on (\w+) (\d{1,2}), (\d{4})", assumption)
    if date_match is None:
        return None
    month = _MONTHS.get(date_match.group(1).lower())
    if month is None:
        return None
    iso_date = f"{date_match.group(3)}-{month}-{int(date_match.group(2)):02d}"
    other_lots = re.findall(r"\blot (\d+)\b", assumption)
    subject = _subject_lot(results)
    lots: list[str] = []
    for lot in [*other_lots, *( [subject] if subject else [] )]:
        if lot not in lots:
            lots.append(lot)
    if not lots:
        return None
    lots.sort(key=lambda value: int(value))
    if len(lots) == 1:
        lots_text = f"lot {lots[0]}"
    else:
        lots_text = "lots " + ", ".join(lots[:-1]) + f" and {lots[-1]}"
    return (
        "the city's register lists a zoning lot description recorded "
        f"{iso_date} against {lots_text}"
    )
