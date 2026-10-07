"""The conditions and blanket rules that apply across every result (task M5-T129, round 2).

Split out of :mod:`result_ways` along a responsibility seam so every file stays under the
modularity warning threshold: this module holds the cross-result logic - the K20 unchecked
condition, the area condition, the blanket withholding, the commercial-overlay block and the
small shared withhold builders and reach helpers. The per-result deciders and the assembly
stay in :mod:`result_ways`, which is the only module that imports this one (plus the records
in :mod:`result_way_inputs`); nothing under ``services/api/app`` imports either.

It computes NO zoning number: the only legal numbers it touches are the two legal measures of
reading O9 (defined in :mod:`result_way_inputs`), and it only compares reach measurements with
them. It holds NO table of what any overlay reading supports (reading O5): the caller states
that per result family, and this module only reads what the caller stated.
"""

from __future__ import annotations

from dataclasses import dataclass

from .result_way_inputs import (
    CORNER_PORTION_WITHIN_100_FT,
    FAMILY_HUMAN,
    KIND_CONTRADICTED_RECORD,
    KIND_UNCHECKED_CONDITION,
    LABELS,
    MISSING_INFORMATION,
    WORK_ORDER_DISTRICT,
    WORK_OWED,
    AreaAgreement,
    Checked,
    Condition,
    Conditional,
    LegalMeasure,
    ReachMeasurements,
    Recorded,
    ResultFamily,
    ResultWayInputs,
    Settled,
    WayRecord,
    Withheld,
)

__all__ = [
    "Blanket",
    "area_condition",
    "blanket_way",
    "blanket_withhold",
    "condition_withhold",
    "format_ft",
    "format_sq_ft",
    "k20_condition",
    "no_lot_type",
    "no_outline",
    "overlay_block",
    "relabel",
    "shown",
    "street_reaches_within",
    "streets_beyond",
    "within",
]


# ---------------------------------------------------------------------------
# Small, named helpers (so a mutation proof can show the tests catch a change).
# ---------------------------------------------------------------------------
def _is_unchecked(state: Checked) -> bool:
    """A K20 condition contributes an unchecked_condition only while it is not checked."""
    return state is Checked.NOT_CHECKED


def within(reach_value: float, measure: LegalMeasure) -> bool:
    """A reach is within a legal measure when it does not exceed it (the captured 'parallel
    to and 100 feet from' boundary and the '135 degrees or less' angle are inclusive)."""
    return reach_value <= measure.value


def format_sq_ft(value: float) -> str:
    whole = int(round(value))
    body = f"{whole:,}" if float(whole) == float(value) else f"{value:,.2f}"
    return f"{body} sq ft"


def format_ft(value: float) -> str:
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


def k20_condition(inp: ResultWayInputs) -> Condition | None:
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
            "Finding a source for each of these conditions and confirming each is absent for "
            "this lot"
        ),
    )


def area_condition(inp: ResultWayInputs) -> Condition | None:
    """The area assumption for a value that needs the lot area (gap K5, section 6). None when
    the figures agree (the recorded area is used and the value stops being conditional on the
    area). The recorded figure is relied on but is never evidence here - never settled (O4).

    Reading O4 (completed by the orchestrator in round 2): when the figures DISAGREE the kind
    is ``contradicted_record`` (another recorded figure contradicts the recorded area); when
    the area COULD NOT BE COMPARED the kind is ``unchecked_condition`` - the comparison was not
    made and nothing contradicts the figure, so the contract's ``contradicted_record`` ("a
    recorded figure that another recorded figure contradicts") does not fit."""
    area = inp.area
    if area.recorded_sq_ft is None or area.agreement is AreaAgreement.AGREES:
        return None
    recorded = format_sq_ft(area.recorded_sq_ft)
    if area.agreement is AreaAgreement.DISAGREES:
        outline = format_sq_ft(area.outline_sq_ft) if area.outline_sq_ft is not None else "another"
        return Condition(
            kind=KIND_CONTRADICTED_RECORD,
            assumption=(
                f"If the recorded lot area of {recorded} is confirmed (the recorded figure and "
                f"the tax-map outline area of {outline} disagree; neither is chosen "
                "automatically)"
            ),
            settled_by="A survey, or deed dimensions, naming the document",
        )
    if area.agreement is AreaAgreement.COULD_NOT_COMPARE:
        # Reading O4: the comparison was not made; nothing contradicts the recorded figure, so
        # the kind is unchecked_condition, not contradicted_record.
        return Condition(
            kind=KIND_UNCHECKED_CONDITION,
            assumption=(
                f"If the recorded lot area of {recorded} is correct - it was not compared with "
                "the tax-map outline's area, which could not be computed"
            ),
            settled_by=(
                "Computing the tax-map outline area to compare it, or a survey or deed dimensions"
            ),
        )
    # agreement is None with a recorded area (G3 note F5): whether the figures agree was not
    # recorded. Handled by an explicit branch, never a silent fall-through, with the same
    # cautious outcome as could-not-compare - conditional, never settled, unchecked_condition.
    return Condition(
        kind=KIND_UNCHECKED_CONDITION,
        assumption=(
            f"If the recorded lot area of {recorded} is correct - whether it agrees with the "
            "tax-map outline's area was not recorded"
        ),
        settled_by=(
            "Comparing the recorded area with the tax-map outline's area, or a survey or deed "
            "dimensions"
        ),
    )


def shown(conditions: list[Condition]) -> WayRecord:
    """Settled when there is nothing to assume, otherwise conditional on what remains."""
    if not conditions:
        return Settled()
    return Conditional(conditions=tuple(conditions))


# ---------------------------------------------------------------------------
# Withholds that cover every result (reading O2; gaps K10, K18, K20-present).
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Blanket:
    reason: str
    gap_kind: str
    resolved_by: str
    zr_sections: tuple[str, ...] = ()


def blanket_withhold(inp: ResultWayInputs) -> Blanket | None:
    """A condition that withholds EVERY result (a user's statement included, reading O2):
    the district not given or not the work order's scope (reading O11), a recorded or not-read
    special purpose district (K10) or split lot (K18), or one of the four no-data-source
    conditions recorded as present (reading O6). Checked in that order; the first match wins."""
    # (O11) the district. A missing district leaves every dependent result not known; a
    # district other than the work order's scope has rules that are owed. Every zoning result
    # depends on the district, so either withholds EVERY result.
    if inp.district is None:
        return Blanket(
            "The zoning district was not given; it comes from the city's zoning record, and "
            "every zoning result depends on it, so every result is withheld until it is given.",
            MISSING_INFORMATION,
            "Reading the zoning district from the city's zoning record for this lot.",
        )
    if inp.district != WORK_ORDER_DISTRICT:
        return Blanket(
            f"The rules connected so far are those of {WORK_ORDER_DISTRICT}; this lot's "
            f"district is {inp.district}, whose rules are owed, so every result is withheld.",
            WORK_OWED,
            f"Connecting the rules for the {inp.district} district and checking them against "
            "independently worked examples.",
        )
    if inp.special_purpose_district is Recorded.PRESENT:
        return Blanket(
            "City records record a special purpose district for this lot; the program does "
            "not yet handle a special purpose district, so every result is withheld.",
            WORK_OWED,
            "Working out the special purpose district's rules and checking them against an "
            "independently worked example.",
        )
    if inp.special_purpose_district is Recorded.NOT_READ:
        return Blanket(
            "The special-purpose-district column was not read; a column that was not read is "
            "never taken as 'none', so every result is withheld until it is read.",
            MISSING_INFORMATION,
            "Reading the special-purpose-district column of the city record for this lot.",
        )
    if inp.split_by_district_line is Recorded.PRESENT:
        return Blanket(
            "City records record this lot as split by a district line; no averaging rule "
            "exists in the program, so every result is withheld.",
            WORK_OWED,
            "Working out the split-lot averaging rules and checking them against an "
            "independently worked example.",
        )
    if inp.split_by_district_line is Recorded.NOT_READ:
        return Blanket(
            "The split-lot column was not read; a column that was not read is never taken as "
            "'not split', so every result is withheld until it is read.",
            MISSING_INFORMATION,
            "Reading the split-lot column of the city record for this lot.",
        )
    present = [name for name, state in _k20_unchecked(inp) if state is Checked.PRESENT]
    if present:
        return Blanket(
            "One of the conditions with no data source is recorded as present ("
            + ", ".join(present)
            + "); which results it can change is not established, so every zoning result is "
            "withheld.",
            WORK_OWED,
            "Finding a source for that condition and working out its rule, then checking it "
            "against an independently worked example.",
        )
    return None


def overlay_block(inp: ResultWayInputs, family: ResultFamily) -> Withheld | None:
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
                "An independent reading of the Article III sections that govern a residential "
                "building in a commercial overlay, checked against an independently worked "
                "example."
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
        resolved_by=(
            "An independent reading of the Article III sections that govern a residential "
            "building in a commercial overlay, checked against an independently worked example."
        ),
        zr_sections=support.zr_sections,
    )


# ---------------------------------------------------------------------------
# Withhold builders shared across families.
# ---------------------------------------------------------------------------
def blanket_way(blanket: Blanket, label: str, zr_sections: tuple[str, ...]) -> Withheld:
    return Withheld(
        label=label,
        reason=blanket.reason,
        gap_kind=blanket.gap_kind,
        resolved_by=blanket.resolved_by,
        zr_sections=zr_sections,
    )


def relabel(withheld: Withheld, label: str) -> Withheld:
    return Withheld(
        label=label,
        reason=withheld.reason,
        gap_kind=withheld.gap_kind,
        resolved_by=withheld.resolved_by,
        zr_sections=withheld.zr_sections,
    )


def condition_withhold(
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


def no_lot_type(label: str, what: str, zr: tuple[str, ...]) -> Withheld:
    return Withheld(
        label=label,
        reason=f"The lot type is not given, so {what} is not known.",
        gap_kind=MISSING_INFORMATION,
        resolved_by="Reading the lot type from the city record or the tax-map outline.",
        zr_sections=zr,
    )


def no_outline(label: str, what: str, zr: tuple[str, ...]) -> Withheld:
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


def street_reaches_within(reach: ReachMeasurements | None) -> bool | None:
    """True when every street-line reach is known and within 100 ft; False when some reach is
    beyond; None when there is nothing to measure (no outline)."""
    if reach is None or not reach.street_lines:
        return None
    if any(not line.reach.known for line in reach.street_lines):
        return None
    return all(
        within(line.reach.value, CORNER_PORTION_WITHIN_100_FT) for line in reach.street_lines
    )


def streets_beyond(reach: ReachMeasurements) -> str:
    beyond = [
        f"{format_ft(line.reach.value)} from the {line.street_name} street line"
        for line in reach.street_lines
        if line.reach.known and not within(line.reach.value, CORNER_PORTION_WITHIN_100_FT)
    ]
    return "The lot reaches " + "; ".join(beyond)
