"""Decide HOW each result appears: settled, conditional or withheld (task M5-T129, Part 0 of
docs/plans/R6B_RESULTS_CONNECTION_WORK_ORDER_2026-10-06.md).

A pure, deterministic decision module in NEW files that NOTHING calls yet; it changes no
present behaviour. Given what is known about a lot it returns, for each result, one of the
three ways of the work order's section 0: settled (every fact is evidence, a reference case
supports the reading, every condition that could change it was checked and is absent);
conditional (it rests on explicit, defensible assumptions that are not evidence - a user's
statement, a recorded figure another figure contradicts, or a condition not checked and
assumed not to apply - each named with its kind and what would settle it); or withheld (a
known gap affects it: "not known", the reason, the kind of gap and what would resolve it).

The module is three files in one package: :mod:`result_way_inputs` (the input records, the
two legal measures, the result vocabulary and the way/output records), :mod:`result_way_conditions`
(the cross-result rules: the K20 condition, the area condition, the blanket withholding, the
overlay block and the shared withhold builders), and this module (the per-result deciders and
the one public function :func:`decide_result_ways`, which also re-exports the records so its
public interface is unchanged - a facade). It computes NO zoning number: floor area, coverage
percentages, heights, the unit factor and the K3 area threshold stay where the engine computes
them (or are stated by the caller); the ONLY legal numbers are the two of reading O9 (100 feet,
135 degrees), used only to compare the lot-reach measurements. It holds NO table of what any
overlay reading supports (reading O5): the caller states that per result family. The way
records mirror the merged results contract 1.3.0, so the second piece emits them unchanged and
a test validates every object against the bundled schema (S7). Points the work order leaves
open are the orchestrator's readings O1-O10 (named here and in the producer report); any
combination neither the work order nor those readings decide is WITHHELD as work owed and
listed in the report (O10). Nothing is guessed.
"""

from __future__ import annotations

from .result_way_conditions import (
    Blanket,
    area_condition,
    blanket_way,
    blanket_withhold,
    condition_withhold,
    format_angle,
    format_ft,
    k20_condition,
    no_lot_type,
    no_outline,
    overlay_block,
    rear_yard_unmeasured,
    relabel,
    shown,
    street_reaches_within,
    streets_beyond,
    within,
)
from .result_way_inputs import (
    BUILDING_OPTION_KEYS,
    CORNER_PORTION_WITHIN_100_FT,
    COVERAGE_KEY,
    FLOOR_AREA_KEYS,
    HEIGHT_KEYS,
    KIND_USER_STATEMENT,
    LABELS,
    MISSING_INFORMATION,
    REAR_YARD_KEY,
    REAR_YARD_WAIVER_MAX_ANGLE_135_DEG,
    REAR_YARD_WAIVER_WITHIN_100_FT,
    REASON_KIND_BY_GAP,
    SETBACK_KEY,
    UNIT_QUALIFYING_AFFORDABLE_KEY,
    UNIT_QUALIFYING_SENIOR_KEY,
    UNIT_STANDARD_KEY,
    WORK_OWED,
    AnswerWays,
    Condition,
    Conditional,
    CornerReach,
    DensityKnowledge,
    LegalMeasure,
    LotType,
    ResultFamily,
    ResultWay,
    ResultWayInputs,
    ResultWays,
    Settled,
    WayRecord,
    WholeAnswerNotAvailable,
    Withheld,
)

__all__ = [
    "BUILDING_OPTION_KEYS",
    "CORNER_PORTION_WITHIN_100_FT",
    "COVERAGE_KEY",
    "FLOOR_AREA_KEYS",
    "HEIGHT_KEYS",
    "LABELS",
    "REAR_YARD_KEY",
    "REAR_YARD_WAIVER_MAX_ANGLE_135_DEG",
    "REAR_YARD_WAIVER_WITHIN_100_FT",
    "SETBACK_KEY",
    "UNIT_QUALIFYING_AFFORDABLE_KEY",
    "UNIT_QUALIFYING_SENIOR_KEY",
    "UNIT_STANDARD_KEY",
    "AnswerWays",
    "Condition",
    "Conditional",
    "LegalMeasure",
    "ResultWay",
    "ResultWays",
    "Settled",
    "WayRecord",
    "WholeAnswerNotAvailable",
    "Withheld",
    "decide_result_ways",
]


def _building_option_withheld() -> bool:
    """The building option (and everything that needs a footprint) is withheld in this
    milestone (gaps K4, K6): no building option is shown and no reference case exists."""
    return True


# ---------------------------------------------------------------------------
# Per-result deciders.
# ---------------------------------------------------------------------------
def _floor_area_way(inp: ResultWayInputs, blanket: Blanket | None, key: str) -> WayRecord:
    label = LABELS[key]
    if blanket is not None:
        return blanket_way(blanket, label, ("ZR 23-22",))
    block = overlay_block(inp, ResultFamily.FLOOR_AREA)
    if block is not None:
        return relabel(block, label)
    inclusionary = condition_withhold(
        inp.inclusionary_housing_area, label,
        present_reason=(
            "City records record an inclusionary housing area for this lot; the program does "
            "not yet apply its floor-area bonus, so the floor-area results are withheld."
        ),
        present_resolved=(
            "Working out the inclusionary-housing floor-area rule and checking it against an "
            "independently worked example."
        ),
        not_read_reason=(
            "The inclusionary-housing-area column was not read; a column that was not read is "
            "never taken as 'none', so the floor-area results are withheld."
        ),
        not_read_resolved="Reading the inclusionary-housing-area column of the city record.",
        zr_sections=("ZR 23-22",),
    )
    if inclusionary is not None:
        return inclusionary
    if inp.area.recorded_sq_ft is None:
        return Withheld(
            label=label,
            reason=(
                "No lot area is recorded, and the tax-map outline's area is never used in a "
                "zoning calculation in its place, so the floor area is not known."
            ),
            gap_kind=MISSING_INFORMATION,
            resolved_by="A recorded lot area, or a survey or deed dimensions.",
            zr_sections=("ZR 23-22",),
        )
    conditions = [c for c in (area_condition(inp), k20_condition(inp)) if c is not None]
    return shown(conditions)


def _height_way(inp: ResultWayInputs, blanket: Blanket | None, key: str) -> WayRecord:
    label = LABELS[key]
    if blanket is not None:
        return blanket_way(blanket, label, ("ZR 23-432",))
    block = overlay_block(inp, ResultFamily.HEIGHTS)
    if block is not None:
        return relabel(block, label)
    flood = condition_withhold(
        inp.flood_zone, label,
        present_reason=(
            "City records record a flood zone for this lot; the program does not yet apply "
            "the flood-zone height rules, so the height limits are withheld."
        ),
        present_resolved=(
            "Working out the flood-zone height rule and checking it against an independently "
            "worked example."
        ),
        not_read_reason=(
            "The flood-zone column was not read; a column that was not read is never taken as "
            "'none', so the height limits are withheld."
        ),
        not_read_resolved="Reading the flood-zone column of the city record for this lot.",
        zr_sections=("ZR 23-432",),
    )
    if flood is not None:
        return flood
    k20 = k20_condition(inp)
    return shown([k20] if k20 is not None else [])


def _coverage_way(inp: ResultWayInputs, blanket: Blanket | None) -> WayRecord:
    label = LABELS[COVERAGE_KEY]
    zr = ("ZR 23-362", "ZR 12-10")
    if blanket is not None:
        return blanket_way(blanket, label, zr)
    block = overlay_block(inp, ResultFamily.COVERAGE)
    if block is not None:
        return relabel(block, label)
    if inp.large_lot_threshold_met:  # (O8) K3 applied as written; the module holds no 30,000
        return Withheld(
            label=label,
            reason=(
                "This lot is at or above the lot size at which a different maximum lot "
                "coverage applies (ZR 23-362), and the program does not work out that maximum "
                "yet, so coverage is not known."
            ),
            gap_kind=WORK_OWED,
            resolved_by=(
                "Working out the larger-lot coverage rule and checking it against an "
                "independently worked example."
            ),
            zr_sections=zr,
        )
    if inp.lot_type is None:
        return no_lot_type(label, "coverage", zr)
    if inp.lot_type in (LotType.INTERIOR, LotType.THROUGH):
        return Withheld(
            label=label,
            reason=(
                "A further rule (ZR 23-363) may change the coverage for an interior or through "
                "lot, and the program does not work that out yet, so coverage is not known."
            ),
            gap_kind=WORK_OWED,
            resolved_by=(
                "Working out the ZR 23-363 rule for this lot and checking it against an "
                "independently worked example."
            ),
            zr_sections=zr,
        )
    reaches_within = street_reaches_within(inp.reach)
    if reaches_within is None:
        return no_outline(label, "coverage", zr)
    if reaches_within is False:
        beyond = streets_beyond(inp.reach)
        return Withheld(
            label=label,
            reason=(
                f"{beyond}, beyond the corner-lot portion "
                f"({CORNER_PORTION_WITHIN_100_FT.comparison}), so there is no single whole-lot "
                "coverage figure: the near part is a "
                "corner-lot portion and the strip beyond is an interior-lot portion."
            ),
            gap_kind=WORK_OWED,
            resolved_by=(
                "Computing coverage per portion (the corner-lot portion and the remaining "
                "interior-lot portion)."
            ),
            zr_sections=zr,
        )
    if inp.large_lot_threshold_met is None:
        # (O13) the large-lot question of gap K3 was NOT STATED. None is not "no": a missing
        # input leaves its dependent result not known, never filled by a default. Sits here,
        # after the blanket rules, the lot type, an interior/through lot and the reach, so those
        # more fundamental reasons still win; it fires only when coverage would otherwise show.
        return Withheld(
            label=label,
            reason=(
                "Whether this lot is at or above the lot size at which a different maximum lot "
                "coverage applies is not known, because the recorded lot area was not compared "
                "with that size (ZR 23-362), so coverage is not known."
            ),
            gap_kind=MISSING_INFORMATION,
            resolved_by=(
                "Comparing the recorded lot area with the lot size named in ZR 23-362."
            ),
            zr_sections=zr,
        )
    k20 = k20_condition(inp)
    return shown([k20] if k20 is not None else [])


def _rear_yard_way(inp: ResultWayInputs, blanket: Blanket | None) -> WayRecord:
    label = LABELS[REAR_YARD_KEY]
    zr = ("ZR 23-344", "ZR 23-342")
    if blanket is not None:
        return blanket_way(blanket, label, zr)
    block = overlay_block(inp, ResultFamily.REAR_YARD)
    if block is not None:
        return relabel(block, label)
    if inp.lot_type is None:
        return no_lot_type(label, "the rear yard", zr)
    if inp.lot_type in (LotType.INTERIOR, LotType.THROUGH):
        return Withheld(
            label=label,
            reason=(
                "The corner rear-yard waiver does not apply to an interior or through lot, and "
                "the program does not yet work out the ordinary rear-yard depth (ZR 23-342), so "
                "the rear yard is not known."
            ),
            gap_kind=WORK_OWED,
            resolved_by=(
                "Working out the ordinary rear-yard rule and checking it against an "
                "independently worked example."
            ),
            zr_sections=zr,
        )
    corner = inp.reach.corner if inp.reach is not None else None
    if corner is None:
        return no_outline(label, "the rear yard", zr)
    if not corner.reach.known or not corner.angle.known:
        # (O20) the corner is present but a measurement is missing; name exactly which, never a
        # measurement that is present. A known reach is never reported as unmeasured.
        return rear_yard_unmeasured(
            label, reach_known=corner.reach.known, angle_known=corner.angle.known, zr=zr,
        )
    within_point = within(corner.reach.value, REAR_YARD_WAIVER_WITHIN_100_FT)
    within_angle = within(corner.angle.value, REAR_YARD_WAIVER_MAX_ANGLE_135_DEG)
    if not within_point or not within_angle:
        return _rear_yard_outside_waiver(label, corner, within_point, within_angle, zr)
    k20 = k20_condition(inp)
    return shown([k20] if k20 is not None else [])


def _rear_yard_outside_waiver(
    label: str, corner: CornerReach, within_point: bool, within_angle: bool,
    zr: tuple[str, ...],
) -> Withheld:
    """(O20) The corner reach and angle are both measured and at least one of the rear-yard
    waiver's two conditions fails. Each of the three states names the condition(s) that really
    fail, with the measured value, and never the condition that holds: the distance alone (the
    far corner is beyond the waiver area; the angle is within the limit), the angle alone (the
    measured angle exceeds the limit; the far corner is within the area), or both."""
    far = format_ft(corner.reach.value)
    waiver_ft = format_ft(REAR_YARD_WAIVER_WITHIN_100_FT.value)
    angle = format_angle(corner.angle.value)
    limit = format_angle(REAR_YARD_WAIVER_MAX_ANGLE_135_DEG.value)
    beyond = (
        f"the far corner is {far} from the point where the two street lines meet, beyond the "
        f"rear-yard waiver area (the waiver covers the area within {waiver_ft} of that point)"
    )
    over = (
        f"the two street lines meet at {angle}, more than the rear-yard waiver's limit of {limit}"
    )
    within_dist = (
        f"the far corner is {far} from the point where the two street lines meet, within "
        f"{waiver_ft} of it"
    )
    within_ang = f"the two street lines meet at {angle}, within the waiver's limit of {limit}"
    if not within_point and not within_angle:
        clause = f"{beyond}, and {over}"
    elif not within_point:
        clause = f"{beyond}; {within_ang}"
    else:
        clause = f"{over}; {within_dist}"
    return Withheld(
        label=label,
        reason=(
            f"The rear-yard waiver does not apply: {clause}. What the ordinary rear yard requires "
            "where the waiver does not apply is not settled."
        ),
        gap_kind=WORK_OWED,
        resolved_by=(
            "Working out the ordinary rear-yard rule for the part the waiver does not cover and "
            "checking it against an independently worked example."
        ),
        zr_sections=zr,
    )


def _setback_way(inp: ResultWayInputs, blanket: Blanket | None) -> WayRecord:
    label = LABELS[SETBACK_KEY]
    if blanket is not None:
        return blanket_way(blanket, label, ("ZR 23-433",))
    return Withheld(
        label=label,
        reason=(
            "The program does not work out the setback above the base (ZR 23-433) yet, so it is "
            "not covered; the envelope drawing and any floor above the base height wait for it."
        ),
        gap_kind=WORK_OWED,
        resolved_by=(
            "Working out the ZR 23-433 setback rule and checking it against an independently "
            "worked example."
        ),
        zr_sections=("ZR 23-433",),
    )


def _unit_standard_way(inp: ResultWayInputs, blanket: Blanket | None) -> WayRecord:
    label = LABELS[UNIT_STANDARD_KEY]
    zr = ("ZR 23-52", "ZR 12-10")
    if blanket is not None:
        return blanket_way(blanket, label, zr)
    block = overlay_block(inp, ResultFamily.UNIT_LIMIT)
    if block is not None:
        return relabel(block, label)
    if inp.area.recorded_sq_ft is None:
        return Withheld(
            label=label,
            reason=(
                "No lot area is recorded, and the outline's area is never used in its place, "
                "so the legal dwelling-unit limit is not known."
            ),
            gap_kind=MISSING_INFORMATION,
            resolved_by="A recorded lot area, or a survey or deed dimensions.",
            zr_sections=zr,
        )
    density = inp.special_density
    if density is DensityKnowledge.USER_STATEMENT_NOT_IN_ONE:
        statement = Condition(
            kind=KIND_USER_STATEMENT,
            assumption="If the lot is not in a special density area, as the user states",
            settled_by=(
                "A sourced fact saying whether the lot is in a special density area"
            ),
        )
        rest = [c for c in (area_condition(inp), k20_condition(inp)) if c is not None]
        return Conditional(conditions=(statement, *rest))
    if density is DensityKnowledge.EVIDENCE_IN_ONE:
        return Withheld(
            label=label,
            reason=(
                "Evidence records this lot in a special density area, where the dwelling-unit "
                "formula does not apply, so the legal dwelling-unit limit is not known."
            ),
            gap_kind=WORK_OWED,
            resolved_by=(
                "Working out the special-density-area dwelling-unit rule and checking it "
                "against an independently worked example."
            ),
            zr_sections=zr,
        )
    if density is DensityKnowledge.EVIDENCE_NOT_IN_ONE:
        # (O19) evidence records the lot OUTSIDE a special density area. The work order decides
        # nothing for this state (reading O10), so it stays withheld as owed work. The reason
        # states the evidence the state already holds; the 'resolved by' names the owed work and
        # never asks for a fact the state has.
        return Withheld(
            label=label,
            reason=(
                "Evidence records this lot outside a special density area; how the legal "
                "dwelling-unit limit is shown on that evidence has not been worked out and "
                "checked against an independently worked example, so the legal dwelling-unit "
                "limit is not known."
            ),
            gap_kind=WORK_OWED,
            resolved_by=(
                "Working out how the legal dwelling-unit limit is shown for a lot recorded "
                "outside a special density area and checking it against an independently worked "
                "example."
            ),
            zr_sections=zr,
        )
    # NOT_GIVEN: no evidence either way. Withheld as owed work (its kind); a user's statement
    # that the lot is not in a special density area would show it only as a conditional result.
    # The reason does not claim the lot is in such an area, and the 'resolved by' names the owed
    # work, not a bare fact (R258 keeps missing information and owed work apart).
    return Withheld(
        label=label,
        reason=(
            "There is no evidence of whether this lot is in a special density area, where the "
            "dwelling-unit formula does not apply, and how the legal dwelling-unit limit is "
            "shown once that is known has not been worked out and checked against an "
            "independently worked example, so the legal dwelling-unit limit is not known; a "
            "user's statement that the lot is not in a special density area would show it only "
            "as a conditional result."
        ),
        gap_kind=WORK_OWED,
        resolved_by=(
            "Working out how the legal dwelling-unit limit is shown from sourced evidence of the "
            "special density area and checking it against an independently worked example; a "
            "user's statement that the lot is not in a special density area would show it as a "
            "conditional result."
        ),
        zr_sections=zr,
    )


def _unit_qualifying_affordable_way(blanket: Blanket | None) -> WayRecord:
    label = LABELS[UNIT_QUALIFYING_AFFORDABLE_KEY]
    if blanket is not None:
        return blanket_way(blanket, label, ("ZR 23-52",))
    return Withheld(
        label=label,
        reason=(
            "The program does not work out the legal dwelling-unit limit for qualifying "
            "affordable housing yet, so it is not known."
        ),
        gap_kind=WORK_OWED,
        resolved_by=(
            "Connecting the rule for qualifying affordable housing and checking it against an "
            "independently worked example."
        ),
        zr_sections=("ZR 23-52",),
    )


def _unit_qualifying_senior_way(blanket: Blanket | None) -> WayRecord:
    label = LABELS[UNIT_QUALIFYING_SENIOR_KEY]
    if blanket is not None:
        return blanket_way(blanket, label, ("ZR 23-52",))
    return Withheld(
        label=label,
        reason=(
            "The dwelling-unit formula sets no factor for qualifying senior housing (ZR "
            "23-52(a)(2)), so this formula gives no unit limit for it; whether any other "
            "provision limits the number of units has not been checked, so the legal "
            "dwelling-unit limit for it is not known: it is not set by this formula."
        ),
        gap_kind=WORK_OWED,
        resolved_by=(
            "Checking whether any other provision limits the number of units for qualifying "
            "senior housing and checking the result against an independently worked example."
        ),
        zr_sections=("ZR 23-52",),
    )


# ---------------------------------------------------------------------------
# Assembling the answers.
# ---------------------------------------------------------------------------
def _answer(answer: str, rows: list[ResultWay]) -> AnswerWays:
    """Fold the value ways into an answer. When every value is withheld the answer itself is
    not available (the contract cannot keep an answer 'available' with no shown value)."""
    if all(isinstance(row.way, Withheld) for row in rows):
        withheld = [row.way for row in rows if isinstance(row.way, Withheld)]
        gap = WORK_OWED if any(w.gap_kind == WORK_OWED for w in withheld) else MISSING_INFORMATION
        first = next(iter(withheld))
        # Name every distinct reason, not just the first: an answer whose values are withheld for
        # different reasons must not present the first value's reason as if it were the only one.
        # (round 2) the same for the 'resolved by': name every distinct 'resolved by', in value
        # order, when they differ; a single text when they are all the same.
        distinct_reasons: list[str] = []
        distinct_resolved: list[str] = []
        for w in withheld:
            if w.reason not in distinct_reasons:
                distinct_reasons.append(w.reason)
            if w.resolved_by not in distinct_resolved:
                distinct_resolved.append(w.resolved_by)
        if all(reason == first.reason for reason in distinct_reasons):
            whole_reason = f"Every value of this answer is withheld: {first.reason}"
        else:
            whole_reason = (
                "Every value of this answer is withheld, for more than one reason: "
                + " ".join(distinct_reasons)
            )
        if all(text == first.resolved_by for text in distinct_resolved):
            whole_resolved = first.resolved_by
        else:
            whole_resolved = " ".join(distinct_resolved)
        return AnswerWays(
            answer=answer,
            values=tuple(rows),
            whole_answer_not_available=WholeAnswerNotAvailable(
                reason=whole_reason,
                reason_kind=REASON_KIND_BY_GAP[gap],
                gap_kind=gap,
                resolved_by=whole_resolved,
            ),
        )
    return AnswerWays(answer=answer, values=tuple(rows))


def decide_result_ways(inp: ResultWayInputs) -> ResultWays:
    """Decide the way of EVERY result the packet lists, from what is known about a lot.

    Pure and deterministic: no I/O, no clock, no randomness, no rule evaluation and no zoning
    number. The two legal measures of reading O9 (100 feet, 135 degrees) are the only legal
    numbers; everything else is a way, never a value.
    """
    blanket = blanket_withhold(inp)

    floor_area = _answer(
        "floor_area_allowance",
        [
            ResultWay(key, LABELS[key], _floor_area_way(inp, blanket, key))
            for key in FLOOR_AREA_KEYS
        ],
    )
    envelope_rows = [
        ResultWay(key, LABELS[key], _height_way(inp, blanket, key)) for key in HEIGHT_KEYS
    ]
    envelope_rows.append(
        ResultWay(COVERAGE_KEY, LABELS[COVERAGE_KEY], _coverage_way(inp, blanket))
    )
    envelope = _answer("permitted_envelope", envelope_rows)

    # (O3) a result computed from a withheld result is withheld and names it: the building
    # option's footprint depends on the rear yard, which is not settled this milestone.
    option_withheld = Withheld(
        label="Building option",
        reason=(
            "No building option is shown yet: the building option is below the minimum base "
            "height and has not been checked against an independently worked example, and its "
            "footprint needs the rear yard, which is not settled."
        ),
        gap_kind=WORK_OWED,
        resolved_by=(
            "Working out the building-option generator and checking it against an "
            "independently worked example."
        ),
    )
    if _building_option_withheld():
        option_rows = [
            ResultWay(key, LABELS[key], relabel(option_withheld, LABELS[key]))
            for key in BUILDING_OPTION_KEYS
        ]
    else:  # pragma: no cover - only a mutation proof reaches this branch
        option_rows = [ResultWay(key, LABELS[key], Settled()) for key in BUILDING_OPTION_KEYS]
    building_option = _answer("building_option", option_rows)

    return ResultWays(
        floor_area_allowance=floor_area,
        permitted_envelope=envelope,
        building_option=building_option,
        rear_yard=ResultWay(REAR_YARD_KEY, LABELS[REAR_YARD_KEY], _rear_yard_way(inp, blanket)),
        setback_above_base=ResultWay(
            SETBACK_KEY, LABELS[SETBACK_KEY], _setback_way(inp, blanket)
        ),
        unit_limit_standard=ResultWay(
            UNIT_STANDARD_KEY, LABELS[UNIT_STANDARD_KEY], _unit_standard_way(inp, blanket)
        ),
        unit_limit_qualifying_affordable=ResultWay(
            UNIT_QUALIFYING_AFFORDABLE_KEY, LABELS[UNIT_QUALIFYING_AFFORDABLE_KEY],
            _unit_qualifying_affordable_way(blanket),
        ),
        unit_limit_qualifying_senior=ResultWay(
            UNIT_QUALIFYING_SENIOR_KEY, LABELS[UNIT_QUALIFYING_SENIOR_KEY],
            _unit_qualifying_senior_way(blanket),
        ),
    )
