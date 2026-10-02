"""Whether the selected lots can be combined: one block and touching (B-07; plan §3 step 2).

"Lots can be combined only if they are on one block and touching. Otherwise the combination
is not offered, and the reason is shown." Touching is the stated test in ``parameters.py``
on the lots' EPSG:2263 tax-map outlines (B-03 ``prepare_outline`` validates each one). A lot
without a usable outline cannot be checked, so the combination is not offered (fail closed).
This is a site-geometry check, not a zoning-lot determination.

Order-free: the lots are taken in BBL order and conformed to each other once
(``conform.py``) before any shared line is measured, so the answer, the shared lines and the
reason do not depend on the order the lots were listed or selected in.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import combinations

from shapely.geometry import Polygon

from app.spatial.site_geometry.outline import prepare_outline

from .conform import conform_outlines
from .inputs import SiteLot, block_of, lot_number
from .parameters import MIN_SHARED_LINE_FT, OVERLAP_TOLERANCE_SQ_FT, SHARED_LINE_TOLERANCE_FT
from .results import (
    COMBINATION_NOT_OFFERED,
    COMBINATION_OFFERED,
    COMBINATION_SINGLE_LOT,
    Combination,
    SharedLine,
)

__all__ = ["CombinationCheck", "Contact", "PreparedLot", "check_combination", "lots_text"]


@dataclass(frozen=True)
class PreparedLot:
    """``polygon`` is the lot's own outline; ``conformed`` is the same outline after
    ``conform.py`` matched its lines to the other selected lots within the tolerance."""

    bbl: str
    polygon: Polygon
    source: str
    conformed: Polygon


@dataclass(frozen=True)
class Contact:
    """How two selected outlines meet."""

    first: str
    second: str
    distance_ft: float
    shared_ft: float
    overlap_sq_ft: float

    @property
    def touching(self) -> bool:
        if self.distance_ft > SHARED_LINE_TOLERANCE_FT:
            return False
        return self.shared_ft >= MIN_SHARED_LINE_FT or self.overlap_sq_ft > OVERLAP_TOLERANCE_SQ_FT

    def describe(self) -> str:
        pair = lots_text([self.first, self.second])
        if self.distance_ft > SHARED_LINE_TOLERANCE_FT:
            # Under 1 ft, 3 decimals: a 0.011 ft gap must not read as the 0.01 ft tolerance.
            digits = 3 if self.distance_ft < 1.0 else 2
            return f"{pair} are {self.distance_ft:,.{digits}f} ft apart"
        return (f"{pair} meet only at a point (shared lot line {self.shared_ft:.2f} ft, under "
                f"the {MIN_SHARED_LINE_FT:.2f} ft minimum)")


@dataclass(frozen=True)
class CombinationCheck:
    combination: Combination
    prepared: tuple[PreparedLot, ...] = ()
    contacts: tuple[Contact, ...] = ()


def lots_text(bbls: Sequence[str]) -> str:
    """'lot 1' / 'lots 1 and 70' / 'lots 1, 11 and 70' (lot numbers on one block)."""
    numbers = [str(lot_number(bbl)) for bbl in bbls]
    if len(numbers) == 1:
        return f"lot {numbers[0]}"
    return "lots " + ", ".join(numbers[:-1]) + " and " + numbers[-1]


def _contact(a: PreparedLot, b: PreparedLot) -> Contact:
    """Shared line and overlap from the conformed outlines (symmetric: an intersection);
    the gap from the lots' own outlines, as recorded."""
    shared = a.conformed.boundary.intersection(b.conformed.boundary).length
    return Contact(a.bbl, b.bbl, a.polygon.distance(b.polygon), shared,
                   a.conformed.intersection(b.conformed).area)


def _blocks_reason(lots: Sequence[SiteLot]) -> str:
    groups: dict[tuple[int, int], list[str]] = {}
    for lot in lots:
        groups.setdefault(block_of(lot.bbl), []).append(lot.bbl)
    boroughs = {borough for borough, _ in groups}
    parts = []
    for (borough, block), bbls in sorted(groups.items()):
        where = f"block {block}" if len(boroughs) == 1 else f"borough {borough} block {block}"
        parts.append(f"{where} ({lots_text(bbls)})")
    return ("Lots can be combined only if they are on one block. The selection is on "
            + ", ".join(parts[:-1]) + " and " + parts[-1] + ".")


def _components(prepared: Sequence[PreparedLot], contacts: Sequence[Contact]) -> list[list[str]]:
    parent = {lot.bbl: lot.bbl for lot in prepared}

    def root(bbl: str) -> str:
        while parent[bbl] != bbl:
            bbl = parent[bbl]
        return bbl

    for contact in contacts:
        if contact.touching:
            parent[root(contact.second)] = root(contact.first)
    groups: dict[str, list[str]] = {}
    for lot in prepared:
        groups.setdefault(root(lot.bbl), []).append(lot.bbl)
    return list(groups.values())


def _touching_reason(groups: list[list[str]], contacts: Sequence[Contact]) -> str:
    main, details = groups[0], []
    for group in groups[1:]:
        between = [c for c in contacts
                   if (c.first in main and c.second in group)
                   or (c.first in group and c.second in main)]
        nearest = min(between, key=lambda c: (c.distance_ft, -c.shared_ft))
        group_text = lots_text(group)
        details.append(f"{group_text[0].upper()}{group_text[1:]} "
                       f"{'does' if len(group) == 1 else 'do'} not touch "
                       f"{lots_text(main)} ({nearest.describe()})")
    return "Lots can be combined only if they touch. " + "; ".join(details) + "."


def check_combination(lots: Sequence[SiteLot]) -> CombinationCheck:
    """The same-block and touching check for the selected lots, with the reason.

    The result is the same for every order of ``lots``; ``prepared`` and ``contacts`` are in
    BBL order."""
    lots = sorted(lots, key=lambda lot: lot.bbl)
    if len(lots) == 1:
        return CombinationCheck(Combination(COMBINATION_SINGLE_LOT, None, True, None))
    if len({block_of(lot.bbl) for lot in lots}) > 1:
        return CombinationCheck(Combination(COMBINATION_NOT_OFFERED, _blocks_reason(lots),
                                            False, None))
    outlines: list[tuple[SiteLot, Polygon]] = []
    problems: list[str] = []
    for lot in lots:
        polygon, refusal = (None, lot.outline_refusal) if lot.outline is None else (
            prepare_outline(lot.outline))
        if polygon is None:
            problems.append(f"{lots_text([lot.bbl])}: {refusal}")
        else:
            outlines.append((lot, polygon.polygon))
    if problems:
        reason = ("Whether the lots touch cannot be checked without a usable tax-map outline "
                  "for each lot. " + " ".join(problems))
        return CombinationCheck(Combination(COMBINATION_NOT_OFFERED, reason, True, None))
    conformed, refusal = conform_outlines([polygon for _, polygon in outlines],
                                          [lots_text([lot.bbl]) for lot, _ in outlines])
    if refusal:
        return CombinationCheck(Combination(COMBINATION_NOT_OFFERED, refusal, True, None))
    prepared = [PreparedLot(lot.bbl, polygon, lot.outline.source, shape)
                for (lot, polygon), shape in zip(outlines, conformed, strict=True)]
    contacts = tuple(_contact(a, b) for a, b in combinations(prepared, 2))
    groups = _components(prepared, contacts)
    if len(groups) > 1:
        return CombinationCheck(
            Combination(COMBINATION_NOT_OFFERED, _touching_reason(groups, contacts), True, False),
            tuple(prepared), contacts)
    shared = tuple(SharedLine(c.first, c.second, round(c.shared_ft, 2))
                   for c in contacts if c.touching)
    return CombinationCheck(Combination(COMBINATION_OFFERED, None, True, True, shared),
                            tuple(prepared), contacts)
