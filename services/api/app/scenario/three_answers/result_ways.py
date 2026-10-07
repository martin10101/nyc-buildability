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

It computes NO zoning number: floor area, coverage percentages, heights, the unit factor and
the K3 area threshold stay where the engine computes them (or are stated by the caller). The
ONLY legal numbers are the two of reading O9 (100 feet, 135 degrees), each defined in
:mod:`result_way_inputs` with the capture id of the text it comes from, used only to compare
the lot-reach measurements. It holds NO table of what any overlay reading supports (reading
O5): the caller states that per result family. The way records mirror the merged results
contract 1.3.0 (``value_state`` / ``answer_not_available``), so the second piece emits them
unchanged and a test validates every object against the bundled schema (S7). Points the work
order leaves open are the orchestrator's readings O1-O10 (named here and in the producer
report, to be confirmed by the reviewers); any combination neither the work order nor those
readings decide is WITHHELD as work owed and listed in the report (O10). Nothing is guessed.
"""

from __future__ import annotations

from dataclasses import dataclass

# The input records, the two legal measures, the result vocabulary and the way (output)
# records all live in result_way_inputs (one records module); this module holds the decision
# logic and re-exports the records so its public interface is unchanged (a facade).
from .result_way_inputs import (
    BUILDING_OPTION_KEYS,
    CORNER_PORTION_WITHIN_100_FT,
    COVERAGE_KEY,
    FAMILY_HUMAN,
    FLOOR_AREA_KEYS,
    HEIGHT_KEYS,
    KIND_CONTRADICTED_RECORD,
    KIND_UNCHECKED_CONDITION,
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
    AreaAgreement,
    Checked,
    Condition,
    Conditional,
    DensityKnowledge,
    LegalMeasure,
    LotType,
    ReachMeasurements,
    Recorded,
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


# ---------------------------------------------------------------------------
# Small, named helpers (so a mutation proof can show the tests catch a change).
# ---------------------------------------------------------------------------
def _is_unchecked(state: Checked) -> bool:
    """A K20 condition contributes an unchecked_condition only while it is not checked."""
    return state is Checked.NOT_CHECKED


def _within(reach_value: float, measure: LegalMeasure) -> bool:
    """A reach is within a legal measure when it does not exceed it (the captured 'parallel
    to and 100 feet from' boundary and the '135 degrees or less' angle are inclusive)."""
    return reach_value <= measure.value


def _building_option_withheld() -> bool:
    """The building option (and everything that needs a footprint) is withheld in this
    milestone (gaps K4, K6): no building option is shown and no reference case exists."""
    return True


def _format_sq_ft(value: float) -> str:
    whole = int(round(value))
    body = f"{whole:,}" if float(whole) == float(value) else f"{value:,.2f}"
    return f"{body} sq ft"


def _format_ft(value: float) -> str:
    whole = int(round(value))
    return f"{whole} ft" if float(whole) == float(value) else f"{value:.2f} ft"


# ---------------------------------------------------------------------------
# Conditions that add up on a shown value (reading O2: conditions add up).
# ---------------------------------------------------------------------------
def _k20_unchecked(inp: ResultWayInputs) -> list[tuple[str, Checked]]:
    return [
        ("waterfront rules", inp.waterfront),
        ("airport height limits", inp.airport_height),
        ("transit easements", inp.transit_easement),
        ("a lot close to a district line", inp.near_district_line),
    ]


def _k20_condition(inp: ResultWayInputs) -> Condition | None:
    """The single unchecked-condition assumption naming the K20 conditions not checked, or
    None when all four are checked and absent (then that part of the condition is removed)."""
    not_checked = [name for name, state in _k20_unchecked(inp) if _is_unchecked(state)]
    if not not_checked:
        return None
    return Condition(
        kind=KIND_UNCHECKED_CONDITION,
        assumption=(
            "If none of these conditions, which were not checked, applies to this lot: "
            + ", ".join(not_checked)
        ),
        settled_by=(
            "Capturing and reading the governing law text for each, then confirming each "
            "is absent for this lot"
        ),
    )


def _area_condition(inp: ResultWayInputs) -> Condition | None:
    """The area assumption for a value that needs the lot area (gap K5, section 6). None when
    the figures agree (the recorded area is used and the value stops being conditional on the
    area). The recorded figure is relied on but is never evidence here - never settled (O4)."""
    area = inp.area
    if area.recorded_sq_ft is None or area.agreement is AreaAgreement.AGREES:
        return None
    recorded = _format_sq_ft(area.recorded_sq_ft)
    if area.agreement is AreaAgreement.DISAGREES:
        outline = _format_sq_ft(area.outline_sq_ft) if area.outline_sq_ft is not None else "another"
        assumption = (
            f"If the recorded lot area of {recorded} is confirmed (the recorded figure and "
            f"the tax-map outline area of {outline} disagree; neither is chosen automatically)"
        )
    else:  # COULD_NOT_COMPARE
        assumption = (
            f"If the recorded lot area of {recorded} is confirmed (the tax-map outline area "
            "could not be computed to compare it)"
        )
    return Condition(
        kind=KIND_CONTRADICTED_RECORD,
        assumption=assumption,
        settled_by="A survey, or deed dimensions, naming the document",
    )


def _shown(conditions: list[Condition]) -> WayRecord:
    """Settled when there is nothing to assume, otherwise conditional on what remains."""
    if not conditions:
        return Settled()
    return Conditional(conditions=tuple(conditions))


# ---------------------------------------------------------------------------
# Withholds that cover every result (reading O2; gaps K10, K18, K20-present).
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _Blanket:
    reason: str
    gap_kind: str
    resolved_by: str
    zr_sections: tuple[str, ...] = ()


def _blanket_withhold(inp: ResultWayInputs) -> _Blanket | None:
    """A condition that withholds EVERY result (a user's statement included, reading O2):
    a recorded or not-read special purpose district (K10) or split lot (K18), or one of the
    four no-data-source conditions recorded as present (reading O6)."""
    if inp.special_purpose_district is Recorded.PRESENT:
        return _Blanket(
            "City records record a special purpose district for this lot; the program does "
            "not yet handle a special purpose district, so every result is withheld.",
            WORK_OWED,
            "Capturing and building the special purpose district's rules, then a reference case.",
        )
    if inp.special_purpose_district is Recorded.NOT_READ:
        return _Blanket(
            "The special-purpose-district column was not read; a column that was not read is "
            "never taken as 'none', so every result is withheld until it is read.",
            MISSING_INFORMATION,
            "Reading the special-purpose-district column of the city record for this lot.",
        )
    if inp.split_by_district_line is Recorded.PRESENT:
        return _Blanket(
            "City records record this lot as split by a district line; no averaging rule "
            "exists in the program, so every result is withheld.",
            WORK_OWED,
            "Building the split-lot averaging rules, then a reference case.",
        )
    if inp.split_by_district_line is Recorded.NOT_READ:
        return _Blanket(
            "The split-lot column was not read; a column that was not read is never taken as "
            "'not split', so every result is withheld until it is read.",
            MISSING_INFORMATION,
            "Reading the split-lot column of the city record for this lot.",
        )
    present = [name for name, state in _k20_unchecked(inp) if state is Checked.PRESENT]
    if present:
        return _Blanket(
            "One of the conditions with no data source is recorded as present ("
            + ", ".join(present)
            + "); which results it can change is not established, so every zoning result is "
            "withheld.",
            WORK_OWED,
            "Capturing and reading the law text for that condition, then building its rule.",
        )
    return None


def _overlay_block(inp: ResultWayInputs, family: ResultFamily) -> Withheld | None:
    """How a recorded commercial overlay affects one result family (gap K9, reading O5).
    None when the overlay is recorded absent (decide as without an overlay) or when an
    independent reading supports showing this family; a Withheld (reason) otherwise. A
    not-read overlay column is never taken as 'none' (K10 generalised; section 10)."""
    overlay = inp.commercial_overlay
    if overlay is Recorded.ABSENT:
        return None
    label = LABELS.get(family.value, FAMILY_HUMAN[family])
    if overlay is Recorded.NOT_READ:
        return Withheld(
            label=label,
            reason=(
                "The commercial-overlay column was not read; a column that was not read is "
                "never taken as 'no overlay', so every residential result is withheld."
            ),
            gap_kind=MISSING_INFORMATION,
            resolved_by="Reading the commercial-overlay column of the city record for this lot.",
        )
    # overlay is Recorded.PRESENT: the caller states per-family support (O5).
    support = (inp.overlay_support or {}).get(family)
    code = f" ({inp.commercial_overlay_code})" if inp.commercial_overlay_code else ""
    if support is None:
        return Withheld(
            label=label,
            reason=(
                f"This lot has a recorded commercial overlay{code}; no independent reading of "
                "the overlay text is yet stated for this result, so it is withheld."
            ),
            gap_kind=WORK_OWED,
            resolved_by=(
                "Capturing and reading the Article III sections that govern a residential "
                "building in a commercial overlay, then a reference case."
            ),
        )
    if support.supported:
        return None
    owed = support.reading_owed or (
        "the reading of the Article III sections that govern a residential building in a "
        "commercial overlay"
    )
    return Withheld(
        label=label,
        reason=(
            f"This lot has a recorded commercial overlay{code}; {owed} is owed before this "
            "result may be shown."
        ),
        gap_kind=WORK_OWED,
        resolved_by="Capturing and reading " + owed + ", then a reference case.",
        zr_sections=support.zr_sections,
    )


# ---------------------------------------------------------------------------
# Per-family decisions.
# ---------------------------------------------------------------------------
def _floor_area_way(inp: ResultWayInputs, blanket: _Blanket | None, key: str) -> WayRecord:
    label = LABELS[key]
    if blanket is not None:
        return _blanket_way(blanket, label, ("ZR 23-22",))
    block = _overlay_block(inp, ResultFamily.FLOOR_AREA)
    if block is not None:
        return _relabel(block, label)
    inclusionary = _condition_withhold(
        inp.inclusionary_housing_area, label,
        present_reason=(
            "City records record an inclusionary housing area for this lot; the program does "
            "not yet apply its floor-area bonus, so the floor-area results are withheld."
        ),
        present_resolved=(
            "Building the inclusionary-housing floor-area rules, then a reference case."
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
    conditions = [c for c in (_area_condition(inp), _k20_condition(inp)) if c is not None]
    return _shown(conditions)


def _height_way(inp: ResultWayInputs, blanket: _Blanket | None, key: str) -> WayRecord:
    label = LABELS[key]
    if blanket is not None:
        return _blanket_way(blanket, label, ("ZR 23-432",))
    block = _overlay_block(inp, ResultFamily.HEIGHTS)
    if block is not None:
        return _relabel(block, label)
    flood = _condition_withhold(
        inp.flood_zone, label,
        present_reason=(
            "City records record a flood zone for this lot; the program does not yet apply "
            "the flood-zone height rules, so the height limits are withheld."
        ),
        present_resolved="Building the flood-zone height rules, then a reference case.",
        not_read_reason=(
            "The flood-zone column was not read; a column that was not read is never taken as "
            "'none', so the height limits are withheld."
        ),
        not_read_resolved="Reading the flood-zone column of the city record for this lot.",
        zr_sections=("ZR 23-432",),
    )
    if flood is not None:
        return flood
    k20 = _k20_condition(inp)
    return _shown([k20] if k20 is not None else [])


def _coverage_way(inp: ResultWayInputs, blanket: _Blanket | None) -> WayRecord:
    label = LABELS[COVERAGE_KEY]
    zr = ("ZR 23-362", "ZR 12-10")
    if blanket is not None:
        return _blanket_way(blanket, label, zr)
    block = _overlay_block(inp, ResultFamily.COVERAGE)
    if block is not None:
        return _relabel(block, label)
    if inp.large_lot_threshold_met:
        return Withheld(
            label=label,
            reason=(
                "The caller states this lot meets the gap-K3 large-lot threshold, where a "
                "different maximum applies that the program does not yet compute, so coverage "
                "is withheld."
            ),
            gap_kind=WORK_OWED,
            resolved_by="Building the large-lot coverage rule, then a reference case.",
            zr_sections=zr,
        )
    if inp.lot_type is None:
        return _no_lot_type(label, "coverage", zr)
    if inp.lot_type in (LotType.INTERIOR, LotType.THROUGH):
        return Withheld(
            label=label,
            reason=(
                "ZR 23-363, which may change the 80 percent interior/through-lot coverage, is "
                "not yet read, so coverage is withheld."
            ),
            gap_kind=WORK_OWED,
            resolved_by="Reading the captured ZR 23-363 and confirming it against this lot.",
            zr_sections=zr,
        )
    within = _street_reaches_within(inp.reach)
    if within is None:
        return _no_outline(label, "coverage", zr)
    if within is False:
        beyond = _streets_beyond(inp.reach)
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
    k20 = _k20_condition(inp)
    return _shown([k20] if k20 is not None else [])


def _rear_yard_way(inp: ResultWayInputs, blanket: _Blanket | None) -> WayRecord:
    label = LABELS[REAR_YARD_KEY]
    zr = ("ZR 23-344", "ZR 23-342")
    if blanket is not None:
        return _blanket_way(blanket, label, zr)
    block = _overlay_block(inp, ResultFamily.REAR_YARD)
    if block is not None:
        return _relabel(block, label)
    if inp.lot_type is None:
        return _no_lot_type(label, "the rear yard", zr)
    if inp.lot_type in (LotType.INTERIOR, LotType.THROUGH):
        return Withheld(
            label=label,
            reason=(
                "The corner rear-yard waiver does not apply to an interior or through lot, and "
                "the ordinary rear-yard depth (ZR 23-342) needs the building type and lot "
                "width, which are not given, so the rear yard is withheld."
            ),
            gap_kind=WORK_OWED,
            resolved_by="Building the ordinary rear-yard rule, then a reference case.",
            zr_sections=zr,
        )
    corner = inp.reach.corner if inp.reach is not None else None
    if corner is None or not corner.reach.known or not corner.angle.known:
        return _no_outline(label, "the rear yard", zr)
    within_point = _within(corner.reach.value, REAR_YARD_WAIVER_WITHIN_100_FT)
    within_angle = _within(corner.angle.value, REAR_YARD_WAIVER_MAX_ANGLE_135_DEG)
    if not (within_point and within_angle):
        return Withheld(
            label=label,
            reason=(
                f"The far corner is {_format_ft(corner.reach.value)} from the corner point, "
                f"beyond the rear-yard waiver area ({REAR_YARD_WAIVER_WITHIN_100_FT.comparison}"
                "); what the ordinary rear yard requires beyond it is not settled."
            ),
            gap_kind=WORK_OWED,
            resolved_by=(
                "Building the ordinary rear-yard rule for the part beyond the corner area, "
                "then a reference case."
            ),
            zr_sections=zr,
        )
    k20 = _k20_condition(inp)
    return _shown([k20] if k20 is not None else [])


def _setback_way(inp: ResultWayInputs, blanket: _Blanket | None) -> WayRecord:
    label = LABELS[SETBACK_KEY]
    if blanket is not None:
        return _blanket_way(blanket, label, ("ZR 23-433",))
    return Withheld(
        label=label,
        reason=(
            "The setback above the base (ZR 23-433) is captured but not built, so it is not "
            "covered; the envelope drawing and any floor above the base height wait for it."
        ),
        gap_kind=WORK_OWED,
        resolved_by="Building the ZR 23-433 setback rule, then a reference case.",
        zr_sections=("ZR 23-433",),
    )


def _unit_standard_way(inp: ResultWayInputs, blanket: _Blanket | None) -> WayRecord:
    label = LABELS[UNIT_STANDARD_KEY]
    zr = ("ZR 23-52", "ZR 12-10")
    if blanket is not None:
        return _blanket_way(blanket, label, zr)
    block = _overlay_block(inp, ResultFamily.UNIT_LIMIT)
    if block is not None:
        return _relabel(block, label)
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
                "Evidence of the lot's special-density-area status, and capturing the ZR 12-10 "
                "special-density-area definition"
            ),
        )
        rest = [c for c in (_area_condition(inp), _k20_condition(inp)) if c is not None]
        return Conditional(conditions=(statement, *rest))
    if density is DensityKnowledge.EVIDENCE_IN_ONE:
        return Withheld(
            label=label,
            reason=(
                "Evidence records this lot in a special density area, where the dwelling-unit "
                "formula does not apply, so the legal unit limit is withheld."
            ),
            gap_kind=WORK_OWED,
            resolved_by=(
                "Building the special-density-area dwelling-unit rule, then a reference case."
            ),
            zr_sections=zr,
        )
    # NOT_GIVEN, and EVIDENCE_NOT_IN_ONE (not decided by the work order, reading O10): withheld.
    return Withheld(
        label=label,
        reason=(
            "There is no evidence of whether the lot is in a special density area, and the "
            "ZR 12-10 special-density-area definition is not captured, so the legal unit limit "
            "is withheld; a user's statement would show it only as a conditional result."
        ),
        gap_kind=WORK_OWED,
        resolved_by=(
            "Capturing the ZR 12-10 special-density-area definition and evidence of the lot's "
            "status."
        ),
        zr_sections=zr,
    )


def _unit_qualifying_affordable_way(blanket: _Blanket | None) -> WayRecord:
    label = LABELS[UNIT_QUALIFYING_AFFORDABLE_KEY]
    if blanket is not None:
        return _blanket_way(blanket, label, ("ZR 23-52",))
    return Withheld(
        label=label,
        reason=(
            "The legal dwelling-unit limit for qualifying affordable housing is not set by the "
            "program in this milestone; the qualifying-housing definitions are not captured."
        ),
        gap_kind=WORK_OWED,
        resolved_by=(
            "Capturing the qualifying-affordable-housing definitions, then a reference case."
        ),
        zr_sections=("ZR 23-52",),
    )


def _unit_qualifying_senior_way(blanket: _Blanket | None) -> WayRecord:
    label = LABELS[UNIT_QUALIFYING_SENIOR_KEY]
    if blanket is not None:
        return _blanket_way(blanket, label, ("ZR 23-52",))
    return Withheld(
        label=label,
        reason=(
            "For qualifying senior housing the dwelling-unit limit is not set by this formula "
            "(ZR 23-52(a)(2) sets no factor), so it is not known in this milestone."
        ),
        gap_kind=WORK_OWED,
        resolved_by="Capturing the qualifying-senior-housing rule, then a reference case.",
        zr_sections=("ZR 23-52",),
    )


# ---------------------------------------------------------------------------
# Withhold builders shared across families.
# ---------------------------------------------------------------------------
def _blanket_way(blanket: _Blanket, label: str, zr_sections: tuple[str, ...]) -> Withheld:
    return Withheld(
        label=label,
        reason=blanket.reason,
        gap_kind=blanket.gap_kind,
        resolved_by=blanket.resolved_by,
        zr_sections=zr_sections,
    )


def _relabel(withheld: Withheld, label: str) -> Withheld:
    return Withheld(
        label=label,
        reason=withheld.reason,
        gap_kind=withheld.gap_kind,
        resolved_by=withheld.resolved_by,
        zr_sections=withheld.zr_sections,
    )


def _condition_withhold(
    state: Recorded, label: str, *, present_reason: str, present_resolved: str,
    not_read_reason: str, not_read_resolved: str, zr_sections: tuple[str, ...],
) -> Withheld | None:
    """A recorded K19 condition (inclusionary, flood): present -> work owed; not read ->
    missing information (reading O7); absent -> None (no effect)."""
    if state is Recorded.PRESENT:
        return Withheld(label, present_reason, WORK_OWED, present_resolved, zr_sections)
    if state is Recorded.NOT_READ:
        return Withheld(label, not_read_reason, MISSING_INFORMATION, not_read_resolved, zr_sections)
    return None


def _no_lot_type(label: str, what: str, zr: tuple[str, ...]) -> Withheld:
    return Withheld(
        label=label,
        reason=f"The lot type is not given, so {what} is not known.",
        gap_kind=MISSING_INFORMATION,
        resolved_by="Reading the lot type from the city record or the tax-map outline.",
        zr_sections=zr,
    )


def _no_outline(label: str, what: str, zr: tuple[str, ...]) -> Withheld:
    return Withheld(
        label=label,
        reason=(
            f"The lot outline and street-line reach are not measured, so {what} cannot be "
            "decided and is not known."
        ),
        gap_kind=MISSING_INFORMATION,
        resolved_by="Measuring the lot's reach from the recorded outline and its street lines.",
        zr_sections=zr,
    )


def _street_reaches_within(reach: ReachMeasurements | None) -> bool | None:
    """True when every street-line reach is known and within 100 ft; False when some reach is
    beyond; None when there is nothing to measure (no outline)."""
    if reach is None or not reach.street_lines:
        return None
    if any(not line.reach.known for line in reach.street_lines):
        return None
    return all(
        _within(line.reach.value, CORNER_PORTION_WITHIN_100_FT) for line in reach.street_lines
    )


def _streets_beyond(reach: ReachMeasurements) -> str:
    beyond = [
        f"{_format_ft(line.reach.value)} from the {line.street_name} street line"
        for line in reach.street_lines
        if line.reach.known and not _within(line.reach.value, CORNER_PORTION_WITHIN_100_FT)
    ]
    return "The lot reaches " + "; ".join(beyond)


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
        return AnswerWays(
            answer=answer,
            values=tuple(rows),
            whole_answer_not_available=WholeAnswerNotAvailable(
                reason=f"Every value of this answer is withheld: {first.reason}",
                reason_kind=REASON_KIND_BY_GAP[gap],
                gap_kind=gap,
                resolved_by=first.resolved_by,
            ),
        )
    return AnswerWays(answer=answer, values=tuple(rows))


def decide_result_ways(inp: ResultWayInputs) -> ResultWays:
    """Decide the way of EVERY result the packet lists, from what is known about a lot.

    Pure and deterministic: no I/O, no clock, no randomness, no rule evaluation and no zoning
    number. The two legal measures of reading O9 (100 feet, 135 degrees) are the only legal
    numbers; everything else is a way, never a value.
    """
    blanket = _blanket_withhold(inp)

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

    option_withheld = Withheld(
        label="Building option",
        reason=(
            "No building option is shown in this milestone: the building option is below the "
            "minimum base height and has no reference case, and its footprint needs the rear "
            "yard, which is not settled."
        ),
        gap_kind=WORK_OWED,
        resolved_by="Building the building-option generator and a reference case.",
    )
    if _building_option_withheld():
        option_rows = [
            ResultWay(key, LABELS[key], _relabel(option_withheld, LABELS[key]))
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
