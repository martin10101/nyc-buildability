"""Lot coverage by portion for a corner lot (ZR 23-362), from two measured areas.

Pure arithmetic: no file or network access, no clock, no AI. From the two portion
areas a corner-reach measurement produces - the corner-lot portion and the rest
(the interior-lot portion) - it works the footprint the ZR 23-362 coverage ratios
allow: the corner-lot portion at its ratio plus the interior-lot portion at its ratio.

The two ratios are the legal figures of ZR 23-362 (capture ``zr-23-362`` under
docs/research/zr-snapshots/v1/: "the maximum #residential# #lot coverage# for
#interior lots# or #through lots# shall be 80 percent and the maximum #residential#
#lot coverage# for #corner lots# shall be 100 percent"). The corner-lot portion is
the part within 100 feet of each intersecting street line (ZR 12-10, capture
``zr-12-10-lot-corner``); that 100-foot distance is documented here as the value a
later wiring step passes to the corner-reach measurement, and is not used in this
arithmetic. A later wiring step sources the 80 percent from the ``r6b-lot-coverage``
rule and hands this module the two measured areas; the defaults below mirror the
captured figures.

This module imports no other part of this task and is imported by no existing engine
file; nothing it returns is reachable from a reported result yet.
"""

from __future__ import annotations

from dataclasses import dataclass

# ZR 12-10 (capture zr-12-10-lot-corner): the corner-lot portion is bounded by lines
# parallel to and 100 feet from each intersecting street line. The wiring step passes
# this distance to the corner-reach measurement (PART A); it is not used in this file.
CORNER_LOT_DISTANCE_FT = 100.0

# ZR 23-362 (capture zr-23-362): corner lots 100 percent, interior or through lots 80
# percent. The wiring step sources these from the r6b-lot-coverage rule.
_CORNER_RATIO = 1.00
_INTERIOR_RATIO = 0.80

_ZR_SECTIONS = ("ZR 23-362", "ZR 12-10")
_FORMULA = (
    "footprint = corner-lot portion area x corner ratio "
    "+ interior-lot portion area x interior ratio"
)
_MEASUREMENT_BASIS = (
    "The two portion areas are square feet measured from the lot outline in EPSG:2263 "
    "US survey feet; see docs/measurement-basis/MEASUREMENT_BASIS.md (linked, not copied)."
)


@dataclass(frozen=True)
class CoverageByPortion:
    """The footprint the two portions allow by the ZR 23-362 ratios, or a not-known
    state. ``status`` is 'available' or 'not_known'. Areas are square feet; no value is
    rounded. ``missing_inputs`` names the inputs not known for a missing-input state
    (empty otherwise); ``gap_kind`` is None for a missing-input state (a module that
    takes plain numbers cannot know why an input is missing)."""

    status: str
    corner_allowed: float | None
    interior_allowed: float | None
    footprint: float | None
    corner_ratio: float | None
    interior_ratio: float | None
    formula: str
    zr_sections: tuple[str, ...]
    measurement_basis: str
    reason: str
    missing_inputs: tuple[str, ...]
    gap_kind: str | None


def permitted_footprint_by_portion(
    corner_portion_area: float | None,
    interior_portion_area: float | None,
    corner_ratio: float = _CORNER_RATIO,
    interior_ratio: float = _INTERIOR_RATIO,
) -> CoverageByPortion:
    """Apply the two ZR 23-362 coverage ratios to the two measured portion areas.

    ``corner_portion_area`` and ``interior_portion_area`` are the corner-lot and
    interior-lot portion areas (square feet) a corner-reach measurement produces. A
    missing area (``None``) gives a not-known result that names the missing inputs,
    never a zero and never a default, and names no kind of gap. A negative area, or a
    ratio outside 0 to 1, is refused with ``ValueError``; no footprint is ever worked
    from a negative area or an out-of-range ratio.
    """
    if not 0 <= corner_ratio <= 1 or not 0 <= interior_ratio <= 1:
        raise ValueError(
            "a coverage ratio must be between 0 and 1: "
            f"corner_ratio={corner_ratio}, interior_ratio={interior_ratio}"
        )
    missing = _missing_area_names(corner_portion_area, interior_portion_area)
    if missing:
        return CoverageByPortion(
            status="not_known",
            corner_allowed=None,
            interior_allowed=None,
            footprint=None,
            corner_ratio=None,
            interior_ratio=None,
            formula=_FORMULA,
            zr_sections=_ZR_SECTIONS,
            measurement_basis=_MEASUREMENT_BASIS,
            reason=(
                "The corner-lot portion area and the interior-lot portion area are not "
                "known for this lot; the corner-reach measurement supplies them. No "
                "footprint is given."
            ),
            missing_inputs=missing,
            gap_kind=None,
        )
    if corner_portion_area < 0 or interior_portion_area < 0:
        raise ValueError(
            "a portion area cannot be negative: "
            f"corner={corner_portion_area}, interior={interior_portion_area}"
        )
    corner_allowed = corner_portion_area * corner_ratio
    interior_allowed = interior_portion_area * interior_ratio
    footprint = corner_allowed + interior_allowed
    return CoverageByPortion(
        status="available",
        corner_allowed=corner_allowed,
        interior_allowed=interior_allowed,
        footprint=footprint,
        corner_ratio=corner_ratio,
        interior_ratio=interior_ratio,
        formula=_FORMULA,
        zr_sections=_ZR_SECTIONS,
        measurement_basis=_MEASUREMENT_BASIS,
        reason=(
            "The footprint the two portions allow is the corner-lot portion at "
            f"{corner_ratio * 100:g} percent of its area plus the interior-lot portion "
            f"at {interior_ratio * 100:g} percent of its area (ZR 23-362). The "
            "corner-lot portion is the part within 100 feet of each intersecting street "
            "line (ZR 12-10)."
        ),
        missing_inputs=(),
        gap_kind=None,
    )


def _missing_area_names(
    corner_portion_area: float | None, interior_portion_area: float | None
) -> tuple[str, ...]:
    """The names of the portion-area inputs that are not known (``None``)."""
    names: list[str] = []
    if corner_portion_area is None:
        names.append("corner_portion_area")
    if interior_portion_area is None:
        names.append("interior_portion_area")
    return tuple(names)
