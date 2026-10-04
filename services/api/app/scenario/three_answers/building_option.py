"""Answer 3 of the three answers (task A-04): the building option - a floor stack with a
stated, editable floor-to-floor height, a floor-by-floor table, and a COMPUTED shortfall
reason when the option cannot reach the allowance.

The core is a pure, exact (``fractions.Fraction``) computation over four numbers: the
allowance, the floor plate (lot area x lot coverage), the maximum building height, and the
floor-to-floor height. Geometry is feet throughout. The shortfall reason is emitted ONLY
when the option's total is strictly below the allowance, and it names the real constraints
it was computed from with the actual numbers compared (competitor-review checks C-2, C-11:
no template sentences). When the envelope holds the whole allowance, the shortfall is
``none`` - the honest answer for an R6B lot, where the generous height limit is never the
binding constraint.

Minimum-base-height note (D-090-R107 step 2). The FAR-limited R6B sample building is 20 ft
tall while the R6B table minimum base height is 30 ft. The 20 ft sample is KEPT, not raised:
on a reading of the captured Zoning Resolution text no provision requires a building to rise
to the minimum base height, so raising the sample to a 30 ft street wall would read a
requirement into the text that it does not state. Finding:
docs/research/zr-snapshots/notes/2026-10-04-r6b-minimum-base-height-20ft-sample.md.
- ZR 23-431 (a) "line-up rules", the presumptive governing paragraph for R6B, state no
  minimum building height; the "extend to the minimum base height ... or the height of the
  #building#, whichever is less" language lives in paragraphs (b)/(c), not in (a).
- ZR 23-432 positions a setback only for street-wall portions that exceed the maximum base
  height (45 ft here); a 20 ft building never reaches it.
- ZR 23-433 only positions that (never-triggered) setback.
Instead of changing the sample, :func:`compliance_notes` emits a COMPUTED, plain-English
note (C-11 discipline) when, and only when, the built height is below the minimum base
height, citing ZR 23-431 / ZR 23-432 / ZR 23-433 and snapshots zr-23-431/432/433. It is a
DRAFT reading of the captured text: which paragraph of ZR 23-431 governs a given lot and the
legal effect wait for G6 qualified review. The v1 results contract's answer shape is closed
(status / values / measurement, additionalProperties false) and this producer adds no
contract field, so the note travels on the engine's :class:`BuildingOptionResult`
(compliance_notes), not inside the schema-validated document; surfacing it to the architect
needs a Lane C contract slot.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from fractions import Fraction

from .answers import AllowanceResult, EnvelopeResult, answer_value, not_available
from .inputs import ThreeAnswerInputs

_RESIDENTIAL = "residential"

# Minimum-base-height compliance note (D-090-R107 step 2). The three governing sections and
# the pinned snapshots that back the draft reading (see the module docstring and the finding
# note). Kept as module constants so the note cites exactly one, stable set.
_MIN_BASE_HEIGHT_ZR_SECTIONS = ("ZR 23-431", "ZR 23-432", "ZR 23-433")
_MIN_BASE_HEIGHT_SNAPSHOT_IDS = ("zr-23-431", "zr-23-432", "zr-23-433")


def _frac(value: float) -> Fraction:
    return Fraction(str(value))


@dataclass(frozen=True)
class FloorRow:
    floor: int
    floor_label: str
    gross_sf: float
    zoning_floor_area_sf: float
    height_ft: float

    def as_results_row(self) -> dict:
        return {
            "floor": self.floor,
            "floor_label": self.floor_label,
            "gross_sf": self.gross_sf,
            "deductions_sf": 0.0,
            "zoning_floor_area_sf": self.zoning_floor_area_sf,
            "height_ft": self.height_ft,
            "use": _RESIDENTIAL,
        }


@dataclass(frozen=True)
class StackLevel:
    floor: int
    floor_to_floor_ft: float
    top_of_floor_ft: float
    allowable_area_sf: float


@dataclass(frozen=True)
class BuildingOptionComputation:
    """The pure result: what fits under the envelope and how much of the allowance the
    option reaches."""

    plate_sf: float
    floor_to_floor_ft: float
    height_limit_ft: float
    floors_fit_under_height: int
    envelope_capacity_sf: float
    allowance_sf: float
    floors_built: int
    achieved_sf: float
    building_height_ft: float
    floor_rows: tuple[FloorRow, ...]
    stack_levels: tuple[StackLevel, ...]
    shortfall_sf: float  # 0.0 when the option reaches the allowance


def compute_building_option(
    *,
    allowance_sf: float,
    plate_sf: float,
    max_building_height_ft: float,
    floor_to_floor_ft: float,
) -> BuildingOptionComputation | None:
    """Compute the largest rectangle-prism building that fits under the envelope (height
    limit x floor plate) without exceeding the allowance. Returns ``None`` when no building
    is possible (non-positive input, or no floor fits under the height limit)."""
    if not (
        allowance_sf > 0 and plate_sf > 0 and max_building_height_ft > 0 and floor_to_floor_ft > 0
    ):
        return None

    allowance = _frac(allowance_sf)
    plate = _frac(plate_sf)
    height = _frac(max_building_height_ft)
    ftf = _frac(floor_to_floor_ft)

    floors_fit = int(height // ftf)  # exact floor of the height / floor-to-floor division
    if floors_fit < 1:
        return None
    capacity = plate * floors_fit

    # Floors needed to reach the allowance at a full plate (top floor may be partial).
    floors_to_reach = int(-(-allowance // plate))  # ceil(allowance / plate), exact

    if floors_to_reach <= floors_fit:
        floors_built = floors_to_reach
        achieved = allowance
        shortfall = Fraction(0)
    else:
        floors_built = floors_fit
        achieved = capacity
        shortfall = allowance - capacity

    # Floor-by-floor table for the built option (top floor partial if not an exact multiple).
    rows: list[FloorRow] = []
    remaining = achieved
    for floor_num in range(1, floors_built + 1):
        this_plate = plate if remaining >= plate else remaining
        rows.append(
            FloorRow(
                floor=floor_num,
                floor_label=("Ground floor" if floor_num == 1 else f"Floor {floor_num}"),
                gross_sf=float(this_plate),
                zoning_floor_area_sf=float(this_plate),
                height_ft=float(ftf),
            )
        )
        remaining -= this_plate

    # Floor stack: every floor that fits under the height limit (envelope capacity).
    levels: list[StackLevel] = []
    for floor_num in range(1, floors_fit + 1):
        levels.append(
            StackLevel(
                floor=floor_num,
                floor_to_floor_ft=float(ftf),
                top_of_floor_ft=float(ftf * floor_num),
                allowable_area_sf=float(plate),
            )
        )

    return BuildingOptionComputation(
        plate_sf=float(plate),
        floor_to_floor_ft=float(ftf),
        height_limit_ft=float(height),
        floors_fit_under_height=floors_fit,
        envelope_capacity_sf=float(capacity),
        allowance_sf=float(allowance),
        floors_built=floors_built,
        achieved_sf=float(achieved),
        building_height_ft=float(ftf * floors_built),
        floor_rows=tuple(rows),
        stack_levels=tuple(levels),
        shortfall_sf=float(shortfall),
    )


def shortfall_reason(
    comp: BuildingOptionComputation, coverage_ratio: float | None
) -> dict:
    """ONE shortfall reason, computed from the real constraints and true (C-11). Names the
    height limit and the floor plate, with the numbers compared. Call only when
    ``comp.shortfall_sf > 0``."""
    coverage_pct = (coverage_ratio * 100.0) if coverage_ratio is not None else None
    coverage_phrase = (
        f" ({coverage_pct:g}% lot coverage)" if coverage_pct is not None else ""
    )
    text = (
        f"A building filling the permitted envelope reaches {comp.envelope_capacity_sf:,.0f} "
        f"sq ft - a {comp.plate_sf:,.0f} sq ft floor plate{coverage_phrase} stacked "
        f"{comp.floors_fit_under_height} floors to the {comp.height_limit_ft:g} ft height "
        f"limit at {comp.floor_to_floor_ft:g} ft per floor - which is "
        f"{comp.shortfall_sf:,.0f} sq ft below the {comp.allowance_sf:,.0f} sq ft allowance."
    )
    return {
        "text": text,
        "computed_from": [
            "max_building_height",
            "max_lot_coverage",
            "max_residential_floor_area",
        ],
        "values": [
            {
                "name": "envelope_capacity",
                "value": comp.envelope_capacity_sf,
                "unit": "square_feet",
            },
            {"name": "allowance", "value": comp.allowance_sf, "unit": "square_feet"},
            {"name": "shortfall", "value": comp.shortfall_sf, "unit": "square_feet"},
            {"name": "height_limit", "value": comp.height_limit_ft, "unit": "feet"},
            {"name": "floors_that_fit", "value": comp.floors_fit_under_height, "unit": "stories"},
            {"name": "floor_plate", "value": comp.plate_sf, "unit": "square_feet"},
        ],
    }


def compliance_notes(
    comp: BuildingOptionComputation,
    min_base_height_ft: float | None,
    max_base_height_ft: float | None,
) -> tuple[dict, ...]:
    """The building option's minimum-base-height note, COMPUTED from the numbers (C-11: never a
    template). A single note is emitted ONLY when the built height is strictly below the minimum
    base height; when the building reaches or exceeds it - so the street wall already meets the
    base - no note appears and the tuple is empty.

    The note reads the captured Zoning Resolution text: no captured provision requires the
    building to rise to the minimum base height - the setback rule (ZR 23-432, ZR 23-433) applies
    only above the maximum base height, the extend-to-the-minimum-base-height language (ZR 23-431
    (b)/(c)) is itself capped at the building height ("whichever is less"), and the R6B line-up
    rule (ZR 23-431 (a)) states no minimum height. It is a DRAFT reading; which paragraph of ZR
    23-431 governs a given lot and the legal effect wait for G6 (see the module docstring and the
    finding note)."""
    if min_base_height_ft is None or max_base_height_ft is None:
        return ()
    if comp.building_height_ft >= min_base_height_ft:
        return ()
    snapshots = ", ".join(_MIN_BASE_HEIGHT_SNAPSHOT_IDS)
    text = (
        f"Built height {comp.building_height_ft:g} ft is below the {min_base_height_ft:g} ft "
        f"minimum base height. No captured provision requires the building to rise to it: the "
        f"setback rule (ZR 23-432, ZR 23-433) applies only to street-wall portions above the "
        f"{max_base_height_ft:g} ft maximum base height; where a street wall must extend to the "
        f"minimum base height (ZR 23-431 (b)/(c)) it extends to the building height when that is "
        f'lower ("whichever is less"); the R6B line-up rule (ZR 23-431 (a)) states no minimum '
        f"height. Draft reading of the captured text (snapshots {snapshots}); which paragraph of "
        f"ZR 23-431 governs this lot and the legal effect wait for qualified review."
    )
    note = {
        "text": text,
        "computed_from": ["building_height", "min_base_height", "max_base_height"],
        "values": [
            {"name": "building_height", "value": comp.building_height_ft, "unit": "feet"},
            {"name": "min_base_height", "value": float(min_base_height_ft), "unit": "feet"},
            {"name": "max_base_height", "value": float(max_base_height_ft), "unit": "feet"},
        ],
        "zr_sections": list(_MIN_BASE_HEIGHT_ZR_SECTIONS),
        "snapshot_ids": list(_MIN_BASE_HEIGHT_SNAPSHOT_IDS),
        "draft": True,
    }
    return (note,)


@dataclass(frozen=True)
class BuildingOptionResult:
    answer: dict
    shortfall: dict
    floor_by_floor: list[dict]
    floor_stack: dict
    computation: BuildingOptionComputation | None
    compliance_notes: tuple[dict, ...] = ()


def build_building_option(
    inputs: ThreeAnswerInputs,
    allowance: AllowanceResult,
    envelope: EnvelopeResult,
    measurement: Mapping[str, str],
) -> BuildingOptionResult:
    """Assemble the building-option answer, the shortfall block, the floor-by-floor table and
    the floor stack from the allowance and the envelope. ``measurement`` is 'Assumed' because
    the option rests on the stated floor-to-floor assumption."""
    if (
        allowance.standard_floor_area_sq_ft is None
        or envelope.max_building_height_ft is None
        or envelope.max_lot_coverage_ratio is None
    ):
        gap = not_available(
            "The building option needs the floor-area allowance, the height limit and the "
            "lot coverage; at least one is not available for this lot.",
            "missing_input",
        )
        return BuildingOptionResult(
            answer=gap,
            shortfall=gap,
            floor_by_floor=[],
            floor_stack=gap,
            computation=None,
        )

    plate_sf = inputs.lot_area_sq_ft * envelope.max_lot_coverage_ratio
    comp = compute_building_option(
        allowance_sf=allowance.standard_floor_area_sq_ft,
        plate_sf=plate_sf,
        max_building_height_ft=envelope.max_building_height_ft,
        floor_to_floor_ft=inputs.building_defaults.floor_to_floor_ft,
    )
    if comp is None:
        gap = not_available(
            f"No floor fits under the {envelope.max_building_height_ft:g} ft height limit at "
            f"{inputs.building_defaults.floor_to_floor_ft:g} ft per floor.",
            "missing_input",
        )
        return BuildingOptionResult(
            answer=gap, shortfall=gap, floor_by_floor=[], floor_stack=gap, computation=None
        )

    far_zr = _first_zr(allowance, ("ZR 23-22",))
    height_zr = envelope.height_zr_sections or ("ZR 23-432",)
    coverage_zr = envelope.coverage_zr_sections or ("ZR 23-362",)

    def _zr_source(sections: tuple[str, ...]) -> list[dict]:
        return [{"kind": "zoning_resolution", "ref": sections[0]}]

    values = [
        answer_value(
            key="achieved_zoning_floor_area",
            label="Achieved zoning floor area (building option)",
            value=comp.achieved_sf,
            unit="square_feet",
            zr_sections=far_zr,
            sources=_zr_source(far_zr),
        ),
        answer_value(
            key="building_floors",
            label="Floors (building option)",
            value=float(comp.floors_built),
            unit="stories",
            zr_sections=tuple(dict.fromkeys((*height_zr, *far_zr))),
            sources=_zr_source(height_zr),
        ),
        answer_value(
            key="building_height",
            label="Building height (building option)",
            value=comp.building_height_ft,
            unit="feet",
            zr_sections=height_zr,
            sources=_zr_source(height_zr),
        ),
        answer_value(
            key="floor_plate_area",
            label="Floor plate (building option)",
            value=comp.plate_sf,
            unit="square_feet",
            zr_sections=coverage_zr,
            sources=_zr_source(coverage_zr),
        ),
    ]
    answer = {"status": "available", "values": values, "measurement": dict(measurement)}

    if comp.shortfall_sf > 0:
        shortfall = {
            "status": "shortfall",
            "sq_ft": comp.shortfall_sf,
            "reasons": [shortfall_reason(comp, envelope.max_lot_coverage_ratio)],
        }
    else:
        shortfall = {"status": "none"}

    floor_stack = {
        "status": "available",
        "floors_fit": comp.floors_fit_under_height,
        "height_limit_ft": comp.height_limit_ft,
        "levels": [
            {
                "floor": lvl.floor,
                "floor_to_floor_ft": lvl.floor_to_floor_ft,
                "top_of_floor_ft": lvl.top_of_floor_ft,
                "allowable_area_sf": lvl.allowable_area_sf,
            }
            for lvl in comp.stack_levels
        ],
        "zr_sections": list(height_zr),
    }
    floor_by_floor = [row.as_results_row() for row in comp.floor_rows]
    return BuildingOptionResult(
        answer=answer,
        shortfall=shortfall,
        floor_by_floor=floor_by_floor,
        floor_stack=floor_stack,
        computation=comp,
        compliance_notes=compliance_notes(
            comp, envelope.min_base_height_ft, envelope.max_base_height_ft
        ),
    )


def _first_zr(allowance: AllowanceResult, default: tuple[str, ...]) -> tuple[str, ...]:
    """The ZR sections of the standard floor-area allowance value (for the option's FAR
    binding), defaulting when the allowance carries none."""
    answer = allowance.answer
    if answer.get("status") == "available":
        for value in answer["values"]:
            if value["key"] == "max_residential_floor_area":
                return tuple(value["zr_sections"])
    return default
