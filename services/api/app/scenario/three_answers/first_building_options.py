"""PART C of task M5-T145: the two step-P6 buildings as pure functions with their floor
schedules.

These are the two buildings of the hand-worked example in
``docs/reference-cases/R6B/cases/step-p6-worked.json`` (rows made-up-building-a /-b and
real-building-a /-b), written as pure arithmetic over plain numbers:

- :func:`building_a` - the WIDEST footprint stacked to the floor-area maximum (fill rule
  ``widest``): as many full-footprint storeys as the floor-area allowance holds.
- :func:`building_b` - the FEWEST storeys that reach the minimum base height (fill rule
  ``to_min_base``): the whole allowance spread evenly over those storeys, every storey the
  same plan.

Both are a PLAIN STACK (every storey the same plan) at an assumed floor-to-floor height:
this shape and that height are design assumptions (the method of the step-P6 example and a
starting value chosen by the owner), not rules of law. Both worked buildings stay at or
below the maximum base height, so no storey above the base is counted and no setback is
worked.

This module decides NOTHING about which building a first option should show (that is the
owner's open decision, backlog row DB-210 (b)). It takes plain numbers, imports no other
part of the packet and no engine file (it does not import or change
``building_option.py``, the engine's own stacker, which is a different method), and nothing
reads it: no reported result is reachable from it. A later wiring step connects the parts.

No file, network or clock access. A missing input gives a plain not-known state naming its
kind of gap, never a zero and never a guessed value. No returned text says a building
complies or is feasible; ``below_min_base`` is a plain fact about the building's height, and
no text draws a legal conclusion from it (orchestrator ruling C3).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

# Status values for a floor schedule.
STATUS_AVAILABLE = "available"
STATUS_NOT_KNOWN = "not_known"

# The three kinds of gap a not-known state may name (orchestrator ruling C7).
GAP_MISSING_PROPERTY_FACT = "a missing fact about the property"
GAP_UNRESOLVED_LAW = "unresolved law"
GAP_CODE_NOT_BUILT = "code not built"

# Fill rules (the two methods of the step-P6 example).
FILL_WIDEST = "widest"
FILL_TO_MIN_BASE = "to_min_base"


@dataclass(frozen=True)
class StoreyRow:
    """One storey of a floor schedule. Areas are square feet; heights are feet above the
    base plane."""

    storey: int
    floor_to_floor_ft: float
    top_ft: float
    plan_area_sqft: float
    floor_area_sqft: float
    running_total_sqft: float


@dataclass(frozen=True)
class FloorSchedule:
    """The result of :func:`building_a` or :func:`building_b`: a floor schedule and its
    totals, or a plain not-known state. For a not-known state every figure is ``None``, the
    ``storeys`` tuple is empty, and ``gap_kind`` names which kind the gap is."""

    building: str  # "A" or "B"
    fill_rule: str  # FILL_WIDEST or FILL_TO_MIN_BASE
    status: str  # STATUS_AVAILABLE or STATUS_NOT_KNOWN
    reason: str  # a plain user text
    footprint_area_sqft: float | None = None
    floor_area_allowance_sqft: float | None = None
    storeys: tuple[StoreyRow, ...] = field(default_factory=tuple)
    storey_count: int | None = None
    height_ft: float | None = None
    total_floor_area_sqft: float | None = None
    unused_floor_area_sqft: float | None = None
    below_min_base: bool | None = None
    gap_kind: str | None = None


def _require_positive(name: str, value: float) -> None:
    """Reject an impossible (zero or negative) numeric input with a clear error. A ``None``
    input is a missing fact, handled before this is reached, not an impossible value."""
    if value <= 0:
        raise ValueError(
            f"{name} must be a positive number; a floor schedule cannot be worked from "
            f"{value}."
        )


def _not_known(building: str, fill_rule: str, reason: str, gap_kind: str) -> FloorSchedule:
    return FloorSchedule(
        building=building,
        fill_rule=fill_rule,
        status=STATUS_NOT_KNOWN,
        reason=reason,
        gap_kind=gap_kind,
    )


def building_a(
    footprint_area: float | None,
    floor_area_allowance: float | None,
    floor_to_floor_ft: float | None,
    min_base_ft: float | None,
    max_base_ft: float | None,
    max_building_ft: float | None,
) -> FloorSchedule:
    """Building A - the widest footprint stacked to the floor-area maximum.

    As many full-footprint storeys as the floor-area allowance holds
    (``floor(allowance / footprint)``), every storey the same footprint plan. A stack whose
    height would pass the maximum base height is not worked (ruling C2): storeys above the
    base and their setback are outside this method.
    """
    if footprint_area is None:
        return _not_known(
            "A",
            FILL_WIDEST,
            "Building A is not known: it needs the footprint it stacks on every storey, "
            "which comes from the measured lot outline and the two street lines. That "
            "footprint is not known for this lot.",
            GAP_MISSING_PROPERTY_FACT,
        )
    if floor_area_allowance is None:
        return _not_known(
            "A",
            FILL_WIDEST,
            "Building A is not known: it needs the building's floor-area allowance (its "
            "maximum residential floor area), which is not available for this lot.",
            GAP_MISSING_PROPERTY_FACT,
        )
    if (
        floor_to_floor_ft is None
        or min_base_ft is None
        or max_base_ft is None
        or max_building_ft is None
    ):
        return _not_known(
            "A",
            FILL_WIDEST,
            "Building A is not known: it needs the floor-to-floor height and the base and "
            "building heights, at least one of which is not available for this lot.",
            GAP_MISSING_PROPERTY_FACT,
        )

    _require_positive("footprint_area", footprint_area)
    _require_positive("floor_area_allowance", floor_area_allowance)
    _require_positive("floor_to_floor_ft", floor_to_floor_ft)
    _require_positive("min_base_ft", min_base_ft)
    _require_positive("max_base_ft", max_base_ft)
    _require_positive("max_building_ft", max_building_ft)

    storey_count = math.floor(floor_area_allowance / footprint_area)
    if storey_count < 1:
        return _not_known(
            "A",
            FILL_WIDEST,
            f"Building A is not known: one full-footprint storey of "
            f"{footprint_area:,.2f} sq ft already passes the floor-area allowance of "
            f"{floor_area_allowance:,.2f} sq ft, so no full-footprint storey is worked by "
            f"this method.",
            GAP_CODE_NOT_BUILT,
        )

    height_ft = storey_count * floor_to_floor_ft
    if height_ft > max_base_ft:
        return _not_known(
            "A",
            FILL_WIDEST,
            f"Building A is not known: stacking the footprint to the floor-area maximum "
            f"would stand {storey_count} storeys and {height_ft:g} ft high, above the "
            f"maximum base height of {max_base_ft:g} ft; storeys above the base and their "
            f"setback are not worked by this method.",
            GAP_CODE_NOT_BUILT,
        )

    storeys = tuple(
        StoreyRow(
            storey=i,
            floor_to_floor_ft=floor_to_floor_ft,
            top_ft=i * floor_to_floor_ft,
            plan_area_sqft=footprint_area,
            floor_area_sqft=footprint_area,
            running_total_sqft=i * footprint_area,
        )
        for i in range(1, storey_count + 1)
    )
    total = storey_count * footprint_area
    unused = floor_area_allowance - total
    below_min_base = height_ft < min_base_ft

    reason = (
        f"Building A (the widest footprint, a plain stack with every storey the same plan) "
        f"is {storey_count} storey{'s' if storey_count != 1 else ''} of "
        f"{footprint_area:,.2f} sq ft, {total:,.2f} sq ft in all, standing {height_ft:g} "
        f"ft, with {unused:,.2f} sq ft of the floor-area allowance unused. Its height of "
        f"{height_ft:g} ft is "
        f"{'below' if below_min_base else 'at or above'} the {min_base_ft:g} ft minimum "
        f"base height. The same-plan stack and the {floor_to_floor_ft:g} ft floor-to-floor "
        f"height are design assumptions, not rules of law."
    )
    return FloorSchedule(
        building="A",
        fill_rule=FILL_WIDEST,
        status=STATUS_AVAILABLE,
        reason=reason,
        footprint_area_sqft=footprint_area,
        floor_area_allowance_sqft=floor_area_allowance,
        storeys=storeys,
        storey_count=storey_count,
        height_ft=height_ft,
        total_floor_area_sqft=total,
        unused_floor_area_sqft=unused,
        below_min_base=below_min_base,
    )


def building_b(
    footprint_area: float | None,
    floor_area_allowance: float | None,
    floor_to_floor_ft: float | None,
    min_base_ft: float | None,
    max_base_ft: float | None,
    max_building_ft: float | None,
) -> FloorSchedule:
    """Building B - the fewest storeys that reach the minimum base height.

    The fewest storeys whose top reaches at least the minimum base height
    (``ceil(min_base / floor_to_floor)``), with the whole floor-area allowance spread evenly
    over them, every storey the same plan (``allowance / storeys``). The plan must fit within
    the footprint (ruling C1); a plan that would not fit is not worked (code not built). The
    footprint is a required input of building B too (ruling C1).
    """
    if floor_area_allowance is None:
        return _not_known(
            "B",
            FILL_TO_MIN_BASE,
            "Building B is not known: it needs the building's floor-area allowance (its "
            "maximum residential floor area) to spread over its storeys, which is not "
            "available for this lot.",
            GAP_MISSING_PROPERTY_FACT,
        )
    if footprint_area is None:
        return _not_known(
            "B",
            FILL_TO_MIN_BASE,
            "Building B is not known: its plan is the floor-area allowance divided by its "
            "storeys, and that plan cannot be shown to fit within a footprint that is not "
            "known for this lot.",
            GAP_MISSING_PROPERTY_FACT,
        )
    if (
        floor_to_floor_ft is None
        or min_base_ft is None
        or max_base_ft is None
        or max_building_ft is None
    ):
        return _not_known(
            "B",
            FILL_TO_MIN_BASE,
            "Building B is not known: it needs the floor-to-floor height and the base and "
            "building heights, at least one of which is not available for this lot.",
            GAP_MISSING_PROPERTY_FACT,
        )

    _require_positive("footprint_area", footprint_area)
    _require_positive("floor_area_allowance", floor_area_allowance)
    _require_positive("floor_to_floor_ft", floor_to_floor_ft)
    _require_positive("min_base_ft", min_base_ft)
    _require_positive("max_base_ft", max_base_ft)
    _require_positive("max_building_ft", max_building_ft)

    storey_count = math.ceil(min_base_ft / floor_to_floor_ft)
    height_ft = storey_count * floor_to_floor_ft
    if height_ft > max_base_ft:
        return _not_known(
            "B",
            FILL_TO_MIN_BASE,
            f"Building B is not known: reaching the minimum base height of "
            f"{min_base_ft:g} ft would need {storey_count} storeys standing "
            f"{height_ft:g} ft, above the maximum base height of {max_base_ft:g} ft; "
            f"storeys above the base and their setback are not worked by this method.",
            GAP_CODE_NOT_BUILT,
        )

    plan_area = floor_area_allowance / storey_count
    if plan_area > footprint_area:
        return _not_known(
            "B",
            FILL_TO_MIN_BASE,
            f"Building B is not known: {storey_count} storeys would need a plan of "
            f"{plan_area:,.2f} sq ft, which is more than the footprint of "
            f"{footprint_area:,.2f} sq ft; the worked method covers only a plan that fits "
            f"the footprint and works no taller building.",
            GAP_CODE_NOT_BUILT,
        )

    storeys = tuple(
        StoreyRow(
            storey=i,
            floor_to_floor_ft=floor_to_floor_ft,
            top_ft=i * floor_to_floor_ft,
            plan_area_sqft=plan_area,
            floor_area_sqft=plan_area,
            running_total_sqft=floor_area_allowance * i / storey_count,
        )
        for i in range(1, storey_count + 1)
    )
    total = floor_area_allowance  # building B spreads the whole allowance
    unused = 0.0
    below_min_base = height_ft < min_base_ft

    reason = (
        f"Building B (the fewest storeys reaching the minimum base height, a plain stack "
        f"with every storey the same plan) is {storey_count} storeys of {plan_area:,.2f} "
        f"sq ft, {total:,.2f} sq ft in all, standing {height_ft:g} ft, with none of the "
        f"floor-area allowance unused. The plan fits within the footprint of "
        f"{footprint_area:,.2f} sq ft. Its height of {height_ft:g} ft is "
        f"{'below' if below_min_base else 'at or above'} the {min_base_ft:g} ft minimum "
        f"base height. The same-plan stack and the {floor_to_floor_ft:g} ft floor-to-floor "
        f"height are design assumptions, not rules of law."
    )
    return FloorSchedule(
        building="B",
        fill_rule=FILL_TO_MIN_BASE,
        status=STATUS_AVAILABLE,
        reason=reason,
        footprint_area_sqft=footprint_area,
        floor_area_allowance_sqft=floor_area_allowance,
        storeys=storeys,
        storey_count=storey_count,
        height_ft=height_ft,
        total_floor_area_sqft=total,
        unused_floor_area_sqft=unused,
        below_min_base=below_min_base,
    )
