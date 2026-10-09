"""Assemble the first-building-option result blocks (task M5-T146 PART B, ruling W9).

A PURE assembly module: no file, network or clock access, no AI, no rule evaluation. It takes
plain numbers (the floor-area allowance, the recorded lot area, the min/max base heights and the
floor-to-floor height), the lot type, whether the recorded and tax-map-outline areas agree, and -
when it was measured - the corner-reach by-portion areas, and it returns the two ADDITIVE results
contract 1.4.0 blocks:

* ``coverage_by_portion`` - the maximum lot coverage read BY PORTION (ZR 23-362: 100 percent on the
  corner-lot portion within 100 ft of each intersecting street line per ZR 12-10, 80 percent on the
  rest). The footprint IN SQUARE FEET is shown ONLY where the recorded and outline areas AGREE
  (ruling W1); where they DISAGREE, or the by-portion split could not be measured, it is WITHHELD
  with NO number, naming its kind of gap (a missing fact, or a limit of the method).
* ``building_alternatives`` - a LIST of the worked first-building alternatives, NONE preferred
  (ruling W3). Building B (the fewest storeys reaching the minimum base height) is worked whenever
  its plan fits the lowest applicable coverage ratio times the RECORDED lot area (ruling W2);
  building A (the widest footprint) is worked only where the footprint figure is available (ruling
  W2). Each alternative carries its floor schedule, its way ('conditional', reusing the 1.3.0
  value-state conditions), what was NOT checked (ruling W5) and its own preliminary capacity
  estimate worked from that building's own floor area (ruling W4).

It calls the four accepted M5-T145 modules (:mod:`app.spatial.corner_reach_area`,
:mod:`lot_coverage_by_portion`, :mod:`first_building_options` and
:mod:`preliminary_apartment_estimate`) and nothing from the decision module. It computes NO zoning
number of its own: the two coverage ratios and the 100 ft distance come from the captured ZR text
held in :mod:`lot_coverage_by_portion`; the floor schedules and the estimate come from the step-P6
modules. Nothing it returns is called feasible, complies, confirmed, validated or legally correct,
and no human verdict is entered (ruling W5, D-090 R544/R556/R570).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.spatial.corner_reach_area import (
    STATE_MEASURED,
    STATE_ONE_CONFIRMED_STREET,
    CornerPortionAreas,
)

from .first_building_options import (
    STATUS_AVAILABLE,
    FloorSchedule,
    building_a,
    building_b,
)
from .lot_coverage_by_portion import CORNER_LOT_DISTANCE_FT, permitted_footprint_by_portion
from .preliminary_apartment_estimate import (
    PreliminaryApartmentEstimate,
    preliminary_apartment_estimate,
)

__all__ = [
    "COVERAGE_LABEL",
    "CornerPortionAreas",
    "FirstOptionBlocks",
    "FirstOptionInputs",
    "assemble_first_option",
    "max_lot_coverage_value_state",
    "portions_measurable",
]

COVERAGE_LABEL = "Maximum lot coverage"
_ZR_SECTIONS = ("ZR 23-362", "ZR 12-10")
_INTERIOR_LOT_TYPES = ("interior", "through")

# gap kinds (the results contract's two values), named here from each missing input (D-090 R650).
_MISSING_FACT = "missing_information"
_METHOD_LIMIT = "work_owed"

_LAW_BY_PORTION = (
    "By portion the law allows up to 100 percent coverage on the corner-lot portion (the part "
    "within 100 feet of each intersecting street line) and up to 80 percent on the rest "
    "(ZR 23-362, ZR 12-10)."
)
_DISAGREE_REASON = (
    "Not shown as a square-foot figure: the recorded lot area and the area measured from the "
    "tax-map outline disagree, and the outline's area is a drawing measure, never used in a "
    "zoning calculation in its place. " + _LAW_BY_PORTION
)
_CANNOT_COMPARE_REASON = (
    "Not shown as a square-foot figure: the lot's tax-map outline is not available, so the "
    "corner-lot and interior-lot portions cannot be measured and the footprint is not known; the "
    "recorded lot area is never used in its place. " + _LAW_BY_PORTION
)
_METHOD_LIMIT_REASON = (
    "Not shown: this lot is not a two-street corner the program can split into a corner-lot "
    "portion and an interior-lot portion (its frontages do not seed two straight street lines), "
    "so the by-portion footprint is not worked. " + _LAW_BY_PORTION
)
_SURVEY_RESOLVED = (
    "A survey or deed dimensions that reconcile the recorded lot area with the tax-map outline."
)
_OUTLINE_RESOLVED = (
    "The lot's tax-map outline (a prepared parcel geometry), or a survey or deed dimensions, so "
    "the corner-lot and interior-lot portions can be measured."
)
_METHOD_RESOLVED = (
    "Working out the by-portion coverage for this lot's frontages and checking it against an "
    "independently worked example."
)

# The max_lot_coverage value state when the by-portion block IS available (the areas agree): the
# single whole-lot figure is still not given, because the lot is partly a corner-lot portion and
# partly an interior-lot portion; coverage is read by portion in coverage_by_portion. (Not reached
# end to end today - the server only emits the block for the conflicting-area case - but kept
# correct so the value state can never contradict an available block.)
_SINGLE_FIGURE_NOT_GIVEN_REASON = (
    "Coverage is given by portion in coverage_by_portion (the corner-lot portion at 100 percent "
    "plus the interior-lot portion at 80 percent); a single whole-lot coverage figure is not given "
    "for a lot that is partly a corner-lot portion and partly an interior-lot portion."
)
_SINGLE_FIGURE_NOT_GIVEN_RESOLVED = "Reading coverage by portion in coverage_by_portion."

_NOT_CHECKED_BASE = (
    "Where the plan sits on the lot",
    "The street wall",
    "Parking, loading and bicycle requirements",
)
_NOT_CHECKED_REAR_YARD = "The rear yard beyond the corner"


@dataclass(frozen=True)
class FirstOptionInputs:
    """Everything the assembly decides from, as plain values. ``corner_areas`` is the measured
    by-portion areas when a two-street corner (or a one-street interior lot) was measured, else
    None - when None the caller has already established that the lot's geometry is workable (the
    server's conflicting-area benchmark path, where the footprint is withheld and needs no portion
    areas). ``areas_agree`` is True when the recorded and outline areas agree, False when they
    disagree, None when they could not be compared. ``way_conditions`` are the value-state
    conditions to reuse for each alternative's (and the available coverage's) way - the same
    conditions the floor-area answer already carries."""

    allowance_sqft: float | None
    recorded_lot_area_sqft: float | None
    min_base_ft: float | None
    max_base_ft: float | None
    floor_to_floor_ft: float | None
    lot_type: str | None
    areas_agree: bool | None
    corner_areas: CornerPortionAreas | None
    outline_area_sqft: float | None
    way_conditions: tuple[dict, ...] = ()


@dataclass(frozen=True)
class FirstOptionBlocks:
    """The two assembled blocks. Either may be None (the key is then omitted from the document):
    ``coverage_by_portion`` is None only when the lot has no coverage context at all;
    ``building_alternatives`` is None when no building can be worked."""

    coverage_by_portion: dict | None
    building_alternatives: tuple[dict, ...] | None


def assemble_first_option(inp: FirstOptionInputs) -> FirstOptionBlocks:
    """Assemble ``coverage_by_portion`` and ``building_alternatives`` from the inputs."""
    coverage, footprint = _coverage(inp)
    alternatives = _alternatives(inp, footprint)
    return FirstOptionBlocks(coverage, alternatives or None)


# --------------------------------------------------------------------------- coverage by portion
def _portion_areas(
    corner_areas: CornerPortionAreas | None, lot_type: str | None, outline_area_sqft: float | None,
) -> tuple[float, float] | None:
    """The (corner-lot-portion, interior-lot-portion) areas, or None when the by-portion split is
    not available: no measurement (the server benchmark path), a lot that is not a measured
    two-street corner, or an interior lot with no outline area (DB-212 b)."""
    corner = corner_areas
    if corner is None:
        return None
    if corner.state == STATE_MEASURED:
        near, rest = corner.corner_portion.value, corner.interior_portion.value
        if near is None or rest is None:
            return None
        return near, rest
    if (
        corner.state == STATE_ONE_CONFIRMED_STREET
        and lot_type in _INTERIOR_LOT_TYPES
        and outline_area_sqft is not None
    ):
        return 0.0, outline_area_sqft
    return None


def _portions(inp: FirstOptionInputs) -> tuple[float, float] | None:
    return _portion_areas(inp.corner_areas, inp.lot_type, inp.outline_area_sqft)


def portions_measurable(
    corner_areas: CornerPortionAreas | None, lot_type: str | None, outline_area_sqft: float | None,
) -> bool:
    """Whether the measured corner-reach areas would yield a by-portion footprint for this lot, so
    the emitter should pass them to the assembly (then the footprint shows and building A is
    worked). Mirrors :func:`_portion_areas` exactly; where it is False building B - which needs no
    outline - still lists (ruling W13)."""
    return _portion_areas(corner_areas, lot_type, outline_area_sqft) is not None


def _coverage(inp: FirstOptionInputs) -> tuple[dict, float | None]:
    """The coverage_by_portion block and, when the footprint can be shown, its figure."""
    portions = _portions(inp)
    if inp.areas_agree is True and portions is not None:
        corner_area, interior_area = portions
        cov = permitted_footprint_by_portion(corner_area, interior_area)
        block = {
            "status": "available",
            "corner_ratio": cov.corner_ratio,
            "interior_ratio": cov.interior_ratio,
            "corner_lot_distance_ft": CORNER_LOT_DISTANCE_FT,
            "corner_portion_area_sqft": corner_area,
            "interior_portion_area_sqft": interior_area,
            "footprint_sqft": cov.footprint,
            "zr_sections": list(_ZR_SECTIONS),
            "way": _way(inp.way_conditions),
        }
        return block, cov.footprint
    if inp.areas_agree is False:
        return _coverage_withheld(_DISAGREE_REASON, _MISSING_FACT, _SURVEY_RESOLVED), None
    if inp.areas_agree is None:
        return _coverage_withheld(_CANNOT_COMPARE_REASON, _MISSING_FACT, _OUTLINE_RESOLVED), None
    # areas agree but the by-portion split could not be measured: a limit of the method.
    return _coverage_withheld(_METHOD_LIMIT_REASON, _METHOD_LIMIT, _METHOD_RESOLVED), None


def _coverage_withheld(reason: str, gap_kind: str, resolved_by: str) -> dict:
    return {
        "status": "withheld",
        "label": COVERAGE_LABEL,
        "reason": reason,
        "gap_kind": gap_kind,
        "resolved_by": resolved_by,
        "zr_sections": list(_ZR_SECTIONS),
    }


def max_lot_coverage_value_state(block: dict) -> dict:
    """The ``max_lot_coverage`` value state that AGREES with the ``coverage_by_portion`` block
    (ruling W11 a): two results about one thing must never give different reasons, kinds or
    resolvers. Where the block is WITHHELD (the areas disagree), the value state carries the SAME
    reason, gap_kind and resolver as the block. Where the block is AVAILABLE (the areas agree),
    coverage is given by portion in ``coverage_by_portion`` and no single whole-lot figure is given;
    the kind is ``work_owed`` - the weaker of the two allowed kinds, claiming no missing property
    fact, only that a single whole-lot figure is not offered for a split lot."""
    if block.get("status") == "withheld":
        return {
            "way": "withheld",
            "label": COVERAGE_LABEL,
            "reason": block["reason"],
            "gap_kind": block["gap_kind"],
            "resolved_by": block["resolved_by"],
            "zr_sections": list(block.get("zr_sections", _ZR_SECTIONS)),
        }
    return {
        "way": "withheld",
        "label": COVERAGE_LABEL,
        "reason": _SINGLE_FIGURE_NOT_GIVEN_REASON,
        "gap_kind": _METHOD_LIMIT,
        "resolved_by": _SINGLE_FIGURE_NOT_GIVEN_RESOLVED,
        "zr_sections": list(_ZR_SECTIONS),
    }


# --------------------------------------------------------------------------- building alternatives
def _numbers_ok(inp: FirstOptionInputs) -> bool:
    values = (inp.allowance_sqft, inp.min_base_ft, inp.max_base_ft, inp.floor_to_floor_ft)
    return all(v is not None and v > 0 for v in values)


def _geometry_understood(inp: FirstOptionInputs) -> bool:
    """Whether the lot's geometry is understood well enough to work a first-building alternative.
    When no corner measurement was supplied the caller has already established this (the server's
    conflicting-area benchmark path). A supplied measurement that is neither a two-street corner
    nor a one-street interior lot (an outline that was refused, a bent frontage, more than two
    streets, or two streets that do not meet) is a limit of the method: no alternative is worked."""
    corner = inp.corner_areas
    if corner is None:
        return True
    if corner.state == STATE_MEASURED:
        return True
    return corner.state == STATE_ONE_CONFIRMED_STREET and inp.lot_type in _INTERIOR_LOT_TYPES


def _alternatives(inp: FirstOptionInputs, footprint: float | None) -> tuple[dict, ...]:
    if not _geometry_understood(inp) or not _numbers_ok(inp):
        return ()
    alts: list[dict] = []
    if footprint is not None:
        widest = building_a(
            footprint, inp.allowance_sqft, inp.floor_to_floor_ft, inp.min_base_ft, inp.max_base_ft
        )
        if widest.status == STATUS_AVAILABLE:
            alts.append(_alternative(widest, inp, footprint, fit=None))
    if inp.recorded_lot_area_sqft is not None:
        bound = permitted_footprint_by_portion(0.0, inp.recorded_lot_area_sqft).footprint
        fewest = building_b(
            bound, inp.allowance_sqft, inp.floor_to_floor_ft, inp.min_base_ft, inp.max_base_ft
        )
        if fewest.status == STATUS_AVAILABLE and fewest.storeys:
            plan = fewest.storeys[0].plan_area_sqft
            alts.append(_alternative(fewest, inp, plan, fit=(bound, plan)))
    return tuple(alts)


def _alternative(
    schedule: FloorSchedule,
    inp: FirstOptionInputs,
    footprint_area_sqft: float,
    *,
    fit: tuple[float, float] | None,
) -> dict:
    entry = {
        "building": schedule.building,
        "label": _label(schedule),
        "fill_rule": schedule.fill_rule,
        "floor_schedule": [_floor_row(storey) for storey in schedule.storeys],
        "storey_count": schedule.storey_count,
        "height_ft": schedule.height_ft,
        "footprint_area_sqft": footprint_area_sqft,
        "floor_area_allowance_sqft": schedule.floor_area_allowance_sqft,
        "total_floor_area_sqft": schedule.total_floor_area_sqft,
        "unused_floor_area_sqft": schedule.unused_floor_area_sqft,
        "below_min_base": schedule.below_min_base,
        "way": _way(inp.way_conditions),
        "not_checked": _not_checked(inp),
        "capacity_estimate": _estimate(
            preliminary_apartment_estimate(schedule.total_floor_area_sqft)
        ),
    }
    note = _fit_note(inp, fit)
    if note is not None:
        entry["fit_note"] = note  # the OPTIONAL fit_note field (ruling W11 c); label stays a name
    return entry


def _floor_row(storey) -> dict:
    return {
        "storey": storey.storey,
        "floor_to_floor_ft": storey.floor_to_floor_ft,
        "top_ft": storey.top_ft,
        "plan_area_sqft": storey.plan_area_sqft,
        "floor_area_sqft": storey.floor_area_sqft,
        "running_total_sqft": storey.running_total_sqft,
    }


def _label(schedule: FloorSchedule) -> str:
    """A short NAME for the alternative (ruling W11 c): the reasoning that the plan fits goes in
    the OPTIONAL fit_note field, not here."""
    if schedule.building == "A":
        return "Building A: the widest footprint"
    return "Building B: the fewest storeys reaching the minimum base height"


def _fit_note(inp: FirstOptionInputs, fit: tuple[float, float] | None) -> str | None:
    """The plain sentence saying WHY the building fits the lot coverage even at the lowest
    applicable ratio (ruling W11 c; ruling W2 for building B). The lowest-ratio bound appears ONLY
    in this text, never as a footprint figure. None when there is no bound to state (building A's
    footprint is itself the coverage footprint)."""
    if fit is None or inp.recorded_lot_area_sqft is None:
        return None
    bound, plan = fit
    return (
        f"The plan of {plan:,.2f} sq ft fits the lot coverage even at the lowest applicable ratio: "
        f"80 percent of the recorded lot area ({inp.recorded_lot_area_sqft:,.0f} sq ft) is "
        f"{bound:,.0f} sq ft, at least the plan. This checks the plan against coverage only; where "
        "the building sits on the lot and the other items listed as not checked are not worked."
    )


def _not_checked(inp: FirstOptionInputs) -> list[str]:
    rows: list[str] = []
    if inp.lot_type == "corner":
        rows.append(_NOT_CHECKED_REAR_YARD)
    rows.extend(_NOT_CHECKED_BASE)
    return rows


def _estimate(estimate: PreliminaryApartmentEstimate) -> dict:
    if estimate.status == "available":
        return {
            "label": estimate.label,
            "floor_area_sqft": estimate.floor_area_sq_ft,
            "share_low": estimate.share_low,
            "share_high": estimate.share_high,
            "apartment_size_sqft": estimate.apartment_size_sq_ft,
            "quotient_low": estimate.quotient_low,
            "quotient_high": estimate.quotient_high,
            "quotient_low_unrounded": estimate.quotient_low_unrounded,
            "quotient_high_unrounded": estimate.quotient_high_unrounded,
            "whole_below_low": estimate.whole_below_low,
            "whole_above_low": estimate.whole_above_low,
            "whole_below_high": estimate.whole_below_high,
            "whole_above_high": estimate.whole_above_high,
        }
    return {"label": estimate.label, "reason": estimate.reason}


def _way(conditions: tuple[dict, ...]) -> dict:
    return {"way": "conditional", "conditions": [dict(condition) for condition in conditions]}
