"""Add-on recalculation, gains and 'Best combination' (task A-06, plan section 5 / M1-25;
directive D-090:D-090-R001).

Everything is RECALCULATED TOGETHER, never added up (plan section 5). For a selection (a set
of optional add-on ids) the effective allowance and height come from the accepted Lane A
rules - the standard ZR 23-22 / ZR 23-432 columns, or the qualifying-housing columns when a
qualifying-housing add-on is on - and the building outcome is computed with the SAME pure
floor-stack math the three-answer generator uses (``compute_building_option``). A gain is the
difference between two recalculated outcomes, so overlapping or conflicting switches can never
be double-counted.

'Best combination' is an EXHAUSTIVE, deterministic search over the admissible combinations of
the available optional Group A and B add-ons (respecting the computed exclusions), maximizing
the stated goal; the tie-break is stated (fewest add-ons, then the lexicographically smallest
id set). Every excluded add-on carries a COMPUTED reason (not implemented, a named conflict, or
no gain). No sentence is emitted unless it is computed true (plan check C-11 / A-05 discipline).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from itertools import combinations

from app.scenario.three_answers.answers import (
    AllowanceResult,
    EnvelopeResult,
    build_allowance,
    build_envelope,
    not_available,
)
from app.scenario.three_answers.building_option import compute_building_option
from app.scenario.three_answers.inputs import (
    MEASUREMENT_ASSUMED,
    AddonGoal,
    ThreeAnswerInputs,
)

from .catalogue import (
    QUALIFYING_PROGRAMS,
    AddOn,
    build_catalogue,
    conflicting_input_keys,
    conflicts,
    is_available,
    optional_group_a_b,
    unavailable_reason,
)

_QUALIFYING_HEIGHT_KEY = "max_building_height_qualifying_affordable_or_senior"
_RELATIVE_TO = "current_selection"

# A function that recalculates one selection's outcome. The default is the rule-driven
# :func:`outcome_for_selection`; tests inject a synthetic one to exercise the search and the
# computed exclusions in isolation.
OutcomeFn = Callable[[ThreeAnswerInputs, "BaseValues", Sequence[AddOn]], "SelectionOutcome | None"]


@dataclass(frozen=True)
class BaseValues:
    """The rule-derived figures every selection recomputes from (read once). The standard and
    qualifying columns both come from the accepted ZR 23-22 / ZR 23-432 rules; neither is a
    literal in this module."""

    standard_floor_area_sf: float | None
    qualifying_floor_area_sf: float | None
    standard_max_building_height_ft: float | None
    qualifying_max_building_height_ft: float | None
    coverage_ratio: float | None
    floor_to_floor_ft: float


@dataclass(frozen=True)
class SelectionOutcome:
    """What a selection builds, recalculated together: the achieved residential/total zoning
    floor area, the building height and the floors - all from the pure floor-stack math."""

    residential_floor_area_sf: float
    total_floor_area_sf: float
    building_height_ft: float
    floors: int
    program: str


def _qualifying_height(envelope: EnvelopeResult) -> float | None:
    """The qualifying-housing maximum building height (ZR 23-432), read from the envelope
    answer values the accepted height rule emitted - never restated here."""
    answer = envelope.answer
    if answer.get("status") != "available":
        return None
    for value in answer["values"]:
        if value["key"] == _QUALIFYING_HEIGHT_KEY:
            return float(value["value"])
    return None


def base_values(inputs: ThreeAnswerInputs, registry) -> BaseValues:
    """Compute, once, the rule-derived standard and qualifying columns the selections reuse."""
    allowance: AllowanceResult = build_allowance(inputs, registry, MEASUREMENT_ASSUMED)
    envelope: EnvelopeResult = build_envelope(inputs, registry, MEASUREMENT_ASSUMED)
    return BaseValues(
        standard_floor_area_sf=allowance.standard_floor_area_sq_ft,
        qualifying_floor_area_sf=allowance.qualifying_floor_area_sq_ft,
        standard_max_building_height_ft=envelope.max_building_height_ft,
        qualifying_max_building_height_ft=_qualifying_height(envelope),
        coverage_ratio=envelope.max_lot_coverage_ratio,
        floor_to_floor_ft=inputs.building_defaults.floor_to_floor_ft,
    )


def effective_program(inputs: ThreeAnswerInputs, selection: Sequence[AddOn]) -> str:
    """The housing program after the selected add-ons' input changes are applied over the
    base inputs (an admissible selection sets it at most once)."""
    changes: dict[str, object] = {}
    for addon in selection:
        changes.update(addon.input_change_map())
    program = changes.get("housing_program", inputs.housing_program)
    return str(program)


def outcome_for_selection(
    inputs: ThreeAnswerInputs, base: BaseValues, selection: Sequence[AddOn]
) -> SelectionOutcome | None:
    """Recalculate the whole building outcome for a selection. Returns ``None`` only when a
    required rule-derived figure is missing (the caller then reports not_available)."""
    program = effective_program(inputs, selection)
    qualifying = program in QUALIFYING_PROGRAMS
    area = base.qualifying_floor_area_sf if qualifying else base.standard_floor_area_sf
    height = (
        base.qualifying_max_building_height_ft
        if qualifying
        else base.standard_max_building_height_ft
    )
    if area is None or height is None or base.coverage_ratio is None:
        return None
    plate_sf = inputs.lot_area_sq_ft * base.coverage_ratio
    comp = compute_building_option(
        allowance_sf=area,
        plate_sf=plate_sf,
        max_building_height_ft=height,
        floor_to_floor_ft=base.floor_to_floor_ft,
    )
    if comp is None:
        return None
    return SelectionOutcome(
        residential_floor_area_sf=comp.achieved_sf,
        total_floor_area_sf=comp.achieved_sf,
        building_height_ft=comp.building_height_ft,
        floors=comp.floors_built,
        program=program,
    )


def goal_value_sf(outcome: SelectionOutcome, goal: AddonGoal) -> float:
    """The goal's floor area for an outcome (plan section 5 'stated goal'). In this slice no
    add-on separates total from residential floor area, so both kinds read the achieved area."""
    if goal.kind == "most_total_floor_area":
        return outcome.total_floor_area_sf
    return outcome.residential_floor_area_sf


def _admissible(selection: Sequence[AddOn]) -> bool:
    """A selection is admissible when no two of its add-ons conflict (computed exclusions)."""
    items = list(selection)
    for first, second in combinations(items, 2):
        if conflicts(first, second):
            return False
    return True


def addon_gain_entry(
    inputs: ThreeAnswerInputs,
    base: BaseValues,
    addon: AddOn,
    rule_ids: frozenset[str],
    current: Sequence[AddOn],
    outcome_fn: OutcomeFn = outcome_for_selection,
) -> dict:
    """One results-v1 ``addon_gain`` for an optional add-on: its delta against the CURRENT
    selection, recalculated together. not_available (rule_not_implemented) when the add-on has
    no reviewed rule - never a guessed number."""
    on = any(a.addon_id == addon.addon_id for a in current)
    base_entry = {
        "addon_id": addon.addon_id,
        "name": addon.label,
        "group": addon.group,
        "on": on,
        "relative_to": _RELATIVE_TO,
        "requires": list(addon.requires),
    }
    if not is_available(addon, rule_ids):
        base_entry["gain"] = not_available(unavailable_reason(addon), "rule_not_implemented")
        return base_entry

    current_outcome = outcome_fn(inputs, base, current)
    candidate = [a for a in current if a.addon_id != addon.addon_id] + [addon]
    candidate_outcome = (
        outcome_fn(inputs, base, candidate) if _admissible(candidate) else None
    )
    if current_outcome is None or candidate_outcome is None:
        base_entry["gain"] = not_available(
            f"Rule {', '.join(addon.rule_ids)} did not resolve for this lot.",
            "eligibility_unresolved",
        )
        return base_entry

    base_entry["gain"] = {
        "status": "available",
        "floor_area_sf": candidate_outcome.residential_floor_area_sf
        - current_outcome.residential_floor_area_sf,
        "height_ft": candidate_outcome.building_height_ft - current_outcome.building_height_ft,
        "floors": candidate_outcome.floors - current_outcome.floors,
    }
    return base_entry


def addon_gains(
    inputs: ThreeAnswerInputs,
    base: BaseValues,
    catalogue: tuple[AddOn, ...],
    rule_ids: frozenset[str],
    current: Sequence[AddOn] = (),
    outcome_fn: OutcomeFn = outcome_for_selection,
) -> list[dict]:
    """The ``addon_gains`` array: every optional Group A and B add-on, each with its gain
    relative to the current selection (zero gain is reported as zero, never hidden)."""
    return [
        addon_gain_entry(inputs, base, addon, rule_ids, current, outcome_fn)
        for addon in optional_group_a_b(catalogue)
    ]


def _tie_break_key(selection: tuple[AddOn, ...]) -> tuple[int, tuple[str, ...]]:
    """Deterministic tie-break among combinations with the SAME goal value: fewer add-ons
    first, then the lexicographically smallest sorted id set."""
    ids = tuple(sorted(a.addon_id for a in selection))
    return (len(ids), ids)


def best_combination(
    inputs: ThreeAnswerInputs,
    base: BaseValues,
    catalogue: tuple[AddOn, ...],
    rule_ids: frozenset[str],
    goal: AddonGoal,
    outcome_fn: OutcomeFn = outcome_for_selection,
) -> dict:
    """'Best combination' for the stated goal: an exhaustive, deterministic search over the
    admissible combinations of the AVAILABLE optional Group A and B add-ons (plan section 5;
    M1-25). Every left-out add-on carries a computed reason."""
    optional_ab = optional_group_a_b(catalogue)
    available = [a for a in optional_ab if is_available(a, rule_ids)]

    scored: list[tuple[float, tuple[int, tuple[str, ...]], tuple[AddOn, ...]]] = []
    for size in range(len(available) + 1):
        for combo in combinations(available, size):
            if not _admissible(combo):
                continue
            outcome = outcome_fn(inputs, base, combo)
            if outcome is None:
                continue
            scored.append((goal_value_sf(outcome, goal), _tie_break_key(combo), combo))

    if not scored:
        return not_available(
            "No supported Group A or B add-on is available for this district yet.",
            "rule_not_implemented",
        )

    best_value = max(value for value, _key, _combo in scored)
    best_tier = [entry for entry in scored if entry[0] == best_value]
    best_tier.sort(key=lambda entry: entry[1])
    _value, _key, best_combo = best_tier[0]
    selected_ids = sorted(a.addon_id for a in best_combo)

    excluded = _excluded_reasons(optional_ab, best_combo, rule_ids)
    return {
        "status": "available",
        "goal": goal.as_contract(),
        "selected_addon_ids": selected_ids,
        "excluded": excluded,
        "goal_value_sf": best_value,
    }


def _excluded_reasons(
    optional_ab: tuple[AddOn, ...],
    best_combo: tuple[AddOn, ...],
    rule_ids: frozenset[str],
) -> list[dict]:
    """A computed reason for every optional Group A/B add-on left out of the best combination:
    not implemented, a named conflict with a chosen add-on, or no gain toward the goal."""
    chosen = {a.addon_id for a in best_combo}
    reasons: list[dict] = []
    for addon in optional_ab:
        if addon.addon_id in chosen:
            continue
        if not is_available(addon, rule_ids):
            reason = unavailable_reason(addon)
        else:
            clash = next((c for c in best_combo if conflicts(addon, c)), None)
            if clash is not None:
                keys = ", ".join(conflicting_input_keys(addon, clash))
                reason = (
                    f"Conflicts with '{clash.label}' (both set {keys}); only one applies."
                )
            else:
                reason = "Adds no floor area toward the goal beyond the selected combination."
        reasons.append({"addon_id": addon.addon_id, "reason": reason})
    return reasons


def completeness_line(
    catalogue: tuple[AddOn, ...], rule_ids: frozenset[str]
) -> dict:
    """The completeness line (plan section 5 'Also shown'): computed true. 'all N' only when
    every optional Group A/B add-on is covered AND nothing is still queued; otherwise
    'Not yet covered: ...' naming the uncovered add-ons (A/B not implemented, plus the C/D1
    switches still out of scope)."""
    optional_ab = optional_group_a_b(catalogue)
    covered = [a for a in optional_ab if is_available(a, rule_ids)]
    uncovered_ab = [a for a in optional_ab if not is_available(a, rule_ids)]
    pending_cd = [
        a
        for a in catalogue
        if a.optional and a.group in ("C", "D1") and not is_available(a, rule_ids)
    ]
    not_yet_covered = [a.label for a in uncovered_ab] + [a.label for a in pending_cd]

    if not not_yet_covered:
        text = f"Add-ons checked for this district: all {len(covered)}."
    else:
        text = "Not yet covered: " + ", ".join(not_yet_covered) + "."
    return {"text": text, "not_yet_covered": not_yet_covered}


def build_addon_results(
    inputs: ThreeAnswerInputs,
    registry,
    *,
    catalogue: tuple[AddOn, ...] | None = None,
    current: Sequence[AddOn] = (),
) -> dict:
    """Assemble the three add-on slots for the results document: ``addon_gains``,
    ``best_combination`` and ``completeness_line``. The goal is read from the option's stated,
    editable ``inputs.addon_goal`` and saved into best_combination."""
    cat = catalogue if catalogue is not None else build_catalogue()
    rule_ids = frozenset(registry.rule_ids())
    base = base_values(inputs, registry)
    return {
        "addon_gains": addon_gains(inputs, base, cat, rule_ids, current),
        "best_combination": best_combination(inputs, base, cat, rule_ids, inputs.addon_goal),
        "completeness_line": completeness_line(cat, rule_ids),
    }
