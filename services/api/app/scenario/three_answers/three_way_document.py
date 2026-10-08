"""Emit the results document in its three-way form (task M5-T136, Part 0 of
docs/plans/R6B_RESULTS_CONNECTION_WORK_ORDER_2026-10-06.md; the fourth and last engine piece,
after M5-T130 carried the facts, M5-T131 added the validators and M5-T134 built the adapter).

ONE pure function, :func:`emit_three_way_document`, from the engine's assembled results document
PLUS the decision-module ways (:class:`~app.scenario.three_answers.result_way_inputs.ResultWays`)
to the contract-1.3.0 three-way document. It is the SECOND new app file that names the decision
module (it imports the way records from ``result_way_inputs``), so it is added to the permitted
set in the one import-guard test, exactly as M5-T134 added the adapter.

WHAT IT DOES (readings O26-O32).
- It is a PURE document -> document transform given the ways: it computes NO zoning number. Every
  shown figure is the engine's own; the standard legal unit limit's figure, formula, factor and
  rounding rule, when shown, are taken from the engine's INNER ``unit_estimate`` block (reading
  O32), never recomputed here.
- For each of the three answers it attaches a ``value_states`` map with one entry for every value
  key the module decided: a settled/conditional value keeps its value object in ``values[]`` and
  records its way; a withheld value is REMOVED from ``values[]`` and recorded as a withheld entry
  (label, reason, gap kind, what would resolve it, and the law section where one applies - carrying
  no number). When every value of an answer is withheld the whole answer becomes ``not_available``
  with the additive 1.3.0 ``resolved_by`` / ``gap_kind`` fields.
- The five standalone results are placed per owner row R567: the rear yard and the setback above
  the base as ``value_states`` entries of ``permitted_envelope``; the three legal unit limits as
  ``value_states`` entries of ``floor_area_allowance``.
- The apartment-estimate block is RESERVED (reading O28, owner R568/R543): ``unit_estimate`` becomes
  the shared not-available shape whose reason begins 'Not known', names the Preliminary capacity
  estimate and says it is not built yet - no legal figure, no formula, no factor.
- Every block worked out from a withheld result FOLLOWS it (reading O31, scenario S5): when the
  building option is withheld ``floor_by_floor`` is empty and ``floor_stack``, ``shortfall``,
  ``best_combination`` and each available add-on gain become not available; when coverage or the
  building option is withheld the matching geometry layer becomes not available; the rear yard
  withheld makes ``geometry.yards`` not available with that withheld result's own reason, never the
  older whole-lot 'not required' (reading O29, DB-189). NO block carries a number worked out from a
  withheld result.
- The finished document is validated with the existing results validator (the way-layer rule runs
  after the schema), so an invalid document is never returned.

The engine, ``dwelling_units.py``, ``geometry.py``, ``answers.py``, the decision modules except the
adapter and every schema stay read-only; this module is the only new logic.
"""

from __future__ import annotations

import copy

from .contract import validate_results_document
from .engine_conditions import Derived, Source
from .result_way_inputs import (
    COVERAGE_KEY,
    LABELS,
    REASON_KIND_BY_GAP,
    UNIT_QUALIFYING_AFFORDABLE_KEY,
    UNIT_QUALIFYING_SENIOR_KEY,
    UNIT_STANDARD_KEY,
    AnswerWays,
    ResultWay,
    ResultWays,
    Withheld,
)

__all__ = [
    "ADDON_GAIN_FOLLOWS_WITHHELD_BUILDING_OPTION",
    "BEST_COMBINATION_FOLLOWS_WITHHELD_BUILDING_OPTION",
    "CONTRACT_VERSION_THREE_WAY",
    "FLOOR_STACK_FOLLOWS_WITHHELD_BUILDING_OPTION",
    "FLOOR_TO_FLOOR_KEY",
    "HOUSING_PROGRAM_KEY",
    "RESERVED_UNIT_ESTIMATE_REASON",
    "SHORTFALL_FOLLOWS_WITHHELD_BUILDING_OPTION",
    "USER_CHOICE_KEYS",
    "USER_ENTERED_FLOOR_TO_FLOOR_STATEMENT",
    "USER_SELECTED_HOUSING_PROGRAM_STATEMENT",
    "emit_three_way_document",
]

CONTRACT_VERSION_THREE_WAY = "1.3.0"

_DWELLING_UNITS_RULE = "r6b-dwelling-units"

# ---------------------------------------------------------------------------
# Texts the transform WRITES (every one plain and true: no internal name, no gap
# or reading number, no task id, never 'professional review', never 'unsupported',
# no claim about which law text is captured). The guard test over the transform's
# texts reads these constants; they are pasted into the producer report.
# ---------------------------------------------------------------------------
RESERVED_UNIT_ESTIMATE_REASON = (
    "Not known. The Preliminary capacity estimate (a practical estimate of how many apartments "
    "might fit) is not built yet."
)

FLOOR_STACK_FOLLOWS_WITHHELD_BUILDING_OPTION = (
    "The floor stack is not known: it is worked out from the building option and the lot coverage, "
    "and neither is known for this lot."
)
SHORTFALL_FOLLOWS_WITHHELD_BUILDING_OPTION = (
    "The gap to the allowance is not known: it is worked out from the building option, which is "
    "not known for this lot."
)
BEST_COMBINATION_FOLLOWS_WITHHELD_BUILDING_OPTION = (
    "The best combination is not known: it is worked out from building options, which are not "
    "known for this lot."
)
ADDON_GAIN_FOLLOWS_WITHHELD_BUILDING_OPTION = (
    "This gain is not known: it is worked out from building options, which are not known for this "
    "lot."
)

# reason_kind of the reserved estimate and the follow-on blocks: the estimator and the building
# option are calculations the program has not built yet (work owed), not a missing fact.
_WORK_OWED_REASON_KIND = "rule_not_implemented"


# ---------------------------------------------------------------------------
# The scope lines of the five conditions the engine takes (M5-T137, reading O36). When the evidence
# entry hands the per-condition sources, the transform rewrites each of the five scope rows to say,
# in plain words, where the condition comes from: recorded, measured from the tax-map outline, the
# user's statement, or not known / not applicable. The engine's own scope block
# (``build_scope_inputs``) and the schema stay read-only; the transform only rewrites the row's
# value, basis and statement from the source the entry derived. When the entry hands no sources
# (the older ``run_engine_and_result_ways`` entry) the scope lines stay as the engine made them.
#
# Every statement here is one of the transform's texts (plain and true: no internal name, no gap or
# reading number, no task id, never 'professional review'). The guard test over the transform's
# texts covers them; they are pasted into the producer report.
# ---------------------------------------------------------------------------

# The results scope_assumption basis each source maps to. There is NO "not known" basis in the
# schema, so a not-known / not-applicable value carries the stand-in it was given with basis
# 'assumed', because the schema has no other way and the schema is read-only here; the STATEMENT
# says it is not known / not applicable (reading O36; DB-196 holds the contract question).
_SCOPE_BASIS_BY_SOURCE = {
    Source.RECORDED: "city_records",
    Source.MEASURED: "approximate_tax_map",
    Source.USER_STATEMENT: "entered",
    Source.NOT_KNOWN: "assumed",
    Source.NOT_APPLICABLE: "assumed",
}

# The WORDS a scope line SHOWS for a condition that is not known or does not apply. The value the
# engine was given (the stand-in) is never shown as the scope row's value - a reader must not see a
# substitute figure for something not known (orchestrator correction of reading O36). The schema's
# scope_assumption value may be a string, and the unit is null for these words (the stand-in the
# engine received does not reach the emitted document). The statement still says it is not known /
# does not apply, what was taken for the calculation, and what is withheld.
_NOT_KNOWN_VALUE = "Not known"
_NOT_APPLICABLE_VALUE = "Not applicable"
_WORDS_VALUE_BY_SOURCE = {
    Source.NOT_KNOWN: _NOT_KNOWN_VALUE,
    Source.NOT_APPLICABLE: _NOT_APPLICABLE_VALUE,
}


# ---------------------------------------------------------------------------
# The two scope rows that carry a DESIGN CHOICE the user may make (M5-T139, DB-204 a). The engine's
# disclosure builder (read-only here) writes BOTH as "the default" (basis 'default'). When the
# caller's request CARRIED the choice, the transform rewrites only the row's basis (to 'entered')
# and its statement; the VALUE and UNIT are never touched. The keys match each scope row's `key`.
# ---------------------------------------------------------------------------
HOUSING_PROGRAM_KEY = "housing_program"
FLOOR_TO_FLOOR_KEY = "floor_to_floor_ft"
#: The two design-choice scope keys the user may make; the transform rewrites only these.
USER_CHOICE_KEYS = frozenset({HOUSING_PROGRAM_KEY, FLOOR_TO_FLOOR_KEY})

# Plain-words housing-program labels (study.schema.json vocabulary, closed): the document's own
# presentation labels. An unknown key falls back to itself so the sentence is never empty.
_HOUSING_PROGRAM_DISPLAY = {
    "standard_residence": "Standard residence",
    "qualifying_affordable_housing": "Qualifying affordable housing",
    "qualifying_senior_housing": "Qualifying senior housing",
}

# The two sentences the transform WRITES when the user made the choice (plain and true: no internal
# name, no task id, never 'professional review', never 'the default'). The guard test renders both.
USER_ENTERED_FLOOR_TO_FLOOR_STATEMENT = (
    "A {height}-foot floor-to-floor height was entered for this run."
)
USER_SELECTED_HOUSING_PROGRAM_STATEMENT = (
    "{program} was selected for this run as the housing program."
)


def _fmt_feet(value: float) -> str:
    return f"{value:.2f} feet"


def _fmt_degrees(value: float) -> str:
    whole = int(round(value))
    return f"{whole} degrees" if float(whole) == float(value) else f"{value:.1f} degrees"


def _scope_statement(key: str, derived: Derived) -> str:
    """The plain-words scope line for one of the five conditions, saying where it comes from."""
    source = derived.source
    if key == "overlay_present":
        if source is Source.RECORDED:
            if derived.engine_value:
                code = f" ({derived.code})" if derived.code else ""
                return f"A commercial overlay{code} is recorded for this lot in the city's records."
            return "The city's records list no commercial overlay for this lot."
        return (
            "Whether a commercial overlay applies to this lot is not known; every result that "
            "depends on it is withheld."
        )
    if key == "special_district_present":
        if source is Source.RECORDED:
            if derived.engine_value:
                return "A special purpose district is recorded for this lot in the city's records."
            return "The city's records list no special purpose district for this lot."
        return (
            "Whether a special purpose district applies to this lot is not known; a special "
            "purpose district is taken for the calculation, so every result that depends on it is "
            "withheld."
        )
    if key == "within_100_ft_of_street_line_intersection":
        if source is Source.MEASURED:
            reach = _fmt_feet(derived.figure)
            if derived.engine_value:
                return (
                    f"Measured from the tax-map outline, the lot's farthest point is {reach} from "
                    "the corner where its two street lines meet, within 100 feet of it."
                )
            return (
                f"Measured from the tax-map outline, the lot's farthest point is {reach} from the "
                "corner where its two street lines meet, more than 100 feet from it."
            )
        if source is Source.NOT_APPLICABLE:
            return (
                "This lot is not a corner lot, so whether it lies within 100 feet of a street-line "
                "corner does not apply."
            )
        return (
            "Whether the lot lies within 100 feet of the corner where two street lines meet is not "
            "known; it is taken as not within 100 feet for the calculation, so the rear yard that "
            "depends on it is withheld."
        )
    if key == "street_line_intersection_angle_degrees":
        if source is Source.MEASURED:
            return (
                "Measured from the tax-map outline, the lot's two street lines meet at about "
                f"{_fmt_degrees(derived.figure)}."
            )
        if source is Source.NOT_APPLICABLE:
            return (
                "This lot is not a corner lot, so the angle at which two street lines meet does "
                "not apply."
            )
        return (
            "The angle at which the lot's two street lines meet is not known; the rear yard that "
            "depends on it is withheld."
        )
    # special_density_area
    if source is Source.USER_STATEMENT:
        return (
            "The lot is taken to be outside a special density area because that was stated for "
            "this run; it is a statement, not a recorded fact."
        )
    return (
        "Whether the lot is in a special density area is not known; it is taken to be in one for "
        "the calculation, so the legal dwelling-unit limit that depends on it is withheld."
    )


def _user_choice_statement(key: str, value: object) -> str:
    """The plain-words scope line for a design choice the user made (M5-T139): the floor-to-floor
    height entered, or the housing program selected. ``value`` is read for the sentence only."""
    if key == FLOOR_TO_FLOOR_KEY:
        return USER_ENTERED_FLOOR_TO_FLOOR_STATEMENT.format(height=f"{float(value):g}")
    display = _HOUSING_PROGRAM_DISPLAY.get(value, value)
    return USER_SELECTED_HOUSING_PROGRAM_STATEMENT.format(program=display)


def _rewrite_scope_lines(
    doc: dict,
    condition_sources: dict[str, Derived] | None,
    user_choices: frozenset[str] | None,
) -> None:
    """Rewrite the scope rows the evidence entry can say more about: the five engine conditions from
    ``condition_sources`` (M5-T137), and the two design-choice rows (housing program, floor-to-floor
    height) named in ``user_choices`` when the user chose them (M5-T139). Every other row, and a
    design choice the user did NOT make, stays as the engine made it. Does nothing with no scope."""
    scope = doc.get("scope")
    if not isinstance(scope, dict):
        return
    assumptions = scope.get("assumptions")
    if not isinstance(assumptions, list):
        return
    sources = condition_sources if condition_sources is not None else {}
    choices = user_choices if user_choices is not None else frozenset()
    for row in assumptions:
        if not isinstance(row, dict):
            continue
        key = row.get("key")
        derived = sources.get(key)
        if derived is not None:
            row["basis"] = _SCOPE_BASIS_BY_SOURCE[derived.source]
            row["statement"] = _scope_statement(key, derived)
            words = _WORDS_VALUE_BY_SOURCE.get(derived.source)
            if words is not None:
                # Not known / not applicable: show the words, never the stand-in the engine
                # received; the unit is null (the stand-in does not reach the document).
                row["value"] = words
                row["unit"] = None
            else:
                # Recorded, measured or the user's statement: the real value (and its unit, as the
                # engine set it - degrees for the angle, null for the flags).
                row["value"] = derived.engine_value
            continue
        if key in choices and key in USER_CHOICE_KEYS:
            # A design choice the user made: basis 'entered' and a sentence that says so. The value
            # and the unit are NOT touched - only the basis and the statement move.
            row["basis"] = "entered"
            row["statement"] = _user_choice_statement(key, row["value"])


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------
def _not_available(reason: str, reason_kind: str) -> dict:
    """The shared not-available shape (status, reason, reason_kind) - no gap_kind/resolved_by
    (those additive 1.3.0 fields live only on a whole-answer not-available object)."""
    return {"status": "not_available", "reason": reason, "reason_kind": reason_kind}


def _withheld_not_available(way: Withheld) -> dict:
    """A geometry layer (or other shared not-available block) that FOLLOWS a withheld result,
    carrying that result's own reason and the matching reason_kind (reading O29/O31)."""
    return _not_available(way.reason, REASON_KIND_BY_GAP[way.gap_kind])


def _row(rows: tuple[ResultWay, ...], key: str) -> ResultWay | None:
    return next((row for row in rows if row.key == key), None)


def _rule_version(rule_versions: list, rule_id: str) -> str | None:
    for record in rule_versions:
        if isinstance(record, dict) and record.get("rule_id") == rule_id:
            return record.get("version")
    return None


def _fmt_number(value: float) -> str:
    whole = int(round(value))
    return f"{whole:,}" if float(whole) == float(value) else f"{value:,}"


def _unit_limit_value_object(inner_unit_estimate, rule_versions: list) -> dict | None:
    """The ONE value object for ``legal_unit_limit_standard`` when its way is shown (reading O32).

    The figure, formula, factor and rounding rule come from the engine's INNER ``unit_estimate``
    block (never recomputed here); the label prints the formula, the factor and the rounding rule
    in words (work order test H10: no value used in a calculation goes unprinted). Returns None when
    the engine's inner block is not available - then the caller adds no value object and the figure
    appears nowhere.
    """
    inner = inner_unit_estimate
    if not isinstance(inner, dict) or inner.get("status") != "available":
        return None
    factor = inner["factor"]["value"]
    label = (
        f"{LABELS[UNIT_STANDARD_KEY]}: {inner['formula']} "
        f"(dwelling-unit factor {_fmt_number(factor)} square feet per dwelling unit; "
        f"{inner['rounding_rule']})"
    )
    zr_sections = list(inner["zr_sections"])
    sources: list[dict] = []
    version = _rule_version(rule_versions, _DWELLING_UNITS_RULE)
    if version is not None:
        sources.append({"kind": "rule_table", "ref": f"{_DWELLING_UNITS_RULE}@{version}"})
    sources.append({"kind": "zoning_resolution", "ref": zr_sections[0]})
    return {
        "key": UNIT_STANDARD_KEY,
        "label": label,
        "value": float(inner["value"]),
        "unit": "dwelling_units",
        "zr_sections": zr_sections,
        "sources": sources,
        "exception_label": None,
    }


def _reserved_unit_estimate() -> dict:
    """The reserved apartment-estimate block (reading O28): the shared not-available shape, no legal
    figure, no formula, no factor; reason begins 'Not known' and names the Preliminary capacity
    estimate."""
    return _not_available(RESERVED_UNIT_ESTIMATE_REASON, _WORK_OWED_REASON_KIND)


# ---------------------------------------------------------------------------
# one answer: attach the value_states layer, withdraw withheld values, place the
# standalone results, add the standard unit-limit value object when it is shown
# ---------------------------------------------------------------------------
def _apply_answer(
    document: dict,
    doc: dict,
    name: str,
    *,
    answer_ways: AnswerWays,
    standalone_withheld: list[ResultWay],
    unit_standard_row: ResultWay | None = None,
    inner_unit_estimate=None,
) -> None:
    engine_answer = document["answers"][name]
    if engine_answer.get("status") != "available":
        # The engine already withheld the whole answer (e.g. the lane is off): leave it unchanged;
        # a not-available answer carries no value_states (the schema's forward binding allows it).
        return

    if answer_ways.whole_answer_not_available is not None:
        # Every value of the answer's OWN keys is withheld -> the whole answer is not available,
        # with the additive 1.3.0 resolution fields (the contract cannot keep an answer 'available'
        # with no shown value). The standalone results placed here are then all withheld too, so no
        # shown value is lost.
        doc["answers"][name] = answer_ways.whole_answer_not_available.to_dict()
        return

    # The answer's OWN value keys: each has an engine value object. A shown value keeps it and
    # records its way; a withheld value is withdrawn from values[] and recorded as a withheld entry.
    value_states: dict = {row.key: row.way.to_value_state() for row in answer_ways.values}
    shown_own = {row.key for row in answer_ways.values if not isinstance(row.way, Withheld)}
    new_values = [v for v in engine_answer["values"] if v["key"] in shown_own]

    # (O32) the standard legal unit limit: a value object with the engine's inner figure and its
    # formula/factor/rounding printed when SHOWN, a withheld entry otherwise. It is the only
    # standalone that can carry a number of its own.
    if unit_standard_row is not None:
        if isinstance(unit_standard_row.way, Withheld):
            value_states[unit_standard_row.key] = unit_standard_row.way.to_value_state()
        else:
            value_object = _unit_limit_value_object(
                inner_unit_estimate, document.get("rule_versions", [])
            )
            if value_object is not None:
                new_values.append(value_object)
                value_states[unit_standard_row.key] = unit_standard_row.way.to_value_state()
            else:
                # The module shows the limit but the engine's inner block is not available: rather
                # than invent a figure, carry the limit as withheld (no number appears anywhere).
                value_states[unit_standard_row.key] = Withheld(
                    label=LABELS[UNIT_STANDARD_KEY],
                    reason=(
                        "The legal dwelling-unit limit is not known: the figure it would be read "
                        "from is not available for this lot."
                    ),
                    gap_kind="missing_information",
                    resolved_by="A recorded lot area, or a survey or deed dimensions.",
                ).to_value_state()

    # The standalone results with NO number of their own (the rear yard, the setback above the base,
    # the qualifying unit limits): placed as a value_states entry ONLY when withheld - a withheld
    # entry belongs to no shown value, which the way rule allows. When one of them is settled or
    # conditional it carries no number and no value object, so it is NOT a value_states entry here;
    # it is shown elsewhere (e.g. the rear-yard waiver shows in geometry.yards).
    for row in standalone_withheld:
        if isinstance(row.way, Withheld):
            value_states[row.key] = row.way.to_value_state()

    doc["answers"][name] = {
        "status": "available",
        "values": new_values,
        "measurement": engine_answer["measurement"],
        "value_states": value_states,
    }


# ---------------------------------------------------------------------------
# blocks worked out from a withheld result follow it (reading O31)
# ---------------------------------------------------------------------------
def _apply_building_option_dependents(doc: dict) -> None:
    """When the building option is withheld, no block worked out from it may carry a number: the
    floor table is empty and the floor stack, the shortfall, the best combination and every add-on
    gain the engine showed as available become not available, each naming the withheld result."""
    doc["floor_by_floor"] = []
    doc["floor_stack"] = _not_available(
        FLOOR_STACK_FOLLOWS_WITHHELD_BUILDING_OPTION, _WORK_OWED_REASON_KIND
    )
    doc["shortfall"] = _not_available(
        SHORTFALL_FOLLOWS_WITHHELD_BUILDING_OPTION, _WORK_OWED_REASON_KIND
    )
    doc["best_combination"] = _not_available(
        BEST_COMBINATION_FOLLOWS_WITHHELD_BUILDING_OPTION, _WORK_OWED_REASON_KIND
    )
    for gain in doc.get("addon_gains", []):
        if isinstance(gain, dict) and isinstance(gain.get("gain"), dict) and (
            gain["gain"].get("status") == "available"
        ):
            gain["gain"] = _not_available(
                ADDON_GAIN_FOLLOWS_WITHHELD_BUILDING_OPTION, _WORK_OWED_REASON_KIND
            )


def _apply_geometry(doc: dict, ways: ResultWays, *, building_option_withheld: bool) -> None:
    """The geometry layers follow the ways (reading O29): the rear yard, the envelope tier (it needs
    the coverage) and the floor plates (they need the building option) become not available with the
    withheld result's own reason; the lot outline stays. The engine's geometry is rewritten here;
    geometry.py stays read-only."""
    geometry = doc.get("geometry")
    if not isinstance(geometry, dict) or geometry.get("status") != "available":
        return  # not even the lot outline is available (e.g. the lane is off): nothing to follow

    rear = ways.rear_yard.way
    if isinstance(rear, Withheld):
        geometry["yards"] = _withheld_not_available(rear)

    coverage_row = _row(ways.permitted_envelope.values, COVERAGE_KEY)
    if coverage_row is not None and isinstance(coverage_row.way, Withheld):
        geometry["envelope"] = _withheld_not_available(coverage_row.way)

    if building_option_withheld:
        bo_reason = ways.building_option.values[0].way
        if isinstance(bo_reason, Withheld):
            geometry["floor_plates"] = _withheld_not_available(bo_reason)


# ---------------------------------------------------------------------------
# the one public transform
# ---------------------------------------------------------------------------
def emit_three_way_document(
    document: dict, ways: ResultWays, *,
    condition_sources: dict[str, Derived] | None = None,
    user_choices: frozenset[str] | None = None,
) -> dict:
    """Transform the engine's assembled results ``document`` into the contract-1.3.0 three-way
    document, given the decision-module ``ways``. Pure: it mutates a deep copy, computes no zoning
    number, and returns a strictly schema-valid document (the way-layer rule runs after the schema).

    ``condition_sources`` (M5-T137, reading O36), when the evidence entry hands it, says for each of
    the engine's five lot conditions where it comes from; the transform then rewrites those five
    scope lines (value, basis, statement) so the scope block says, in plain words, recorded /
    measured / the user's statement / not known / not applicable. When None (the older
    ``run_engine_and_result_ways`` entry, which holds engine inputs already) the scope lines stay as
    the engine made them.

    ``user_choices`` (M5-T139, DB-204 a), when given, names which of the two design-choice scope
    rows the caller's request carried (:data:`USER_CHOICE_KEYS`); the transform rewrites those rows
    to basis 'entered' and a sentence saying the value is the user's choice, touching no value. When
    None or empty, both stay as the engine made them. The engine, disclosure builder and schema stay
    read-only."""
    doc = copy.deepcopy(document)
    doc["contract_version"] = CONTRACT_VERSION_THREE_WAY

    # The engine's INNER unit_estimate block, read BEFORE it is replaced by the reserved block, so
    # the standard legal unit limit (when shown) reads its figure from the engine, never recomputed.
    inner_unit_estimate = document.get("unit_estimate")

    # R567: the three legal unit limits are placed in floor_area_allowance; the rear yard and the
    # setback above the base in permitted_envelope.
    _apply_answer(
        document, doc, "floor_area_allowance",
        answer_ways=ways.floor_area_allowance,
        standalone_withheld=[
            ways.unit_limit_qualifying_affordable,
            ways.unit_limit_qualifying_senior,
        ],
        unit_standard_row=ways.unit_limit_standard,
        inner_unit_estimate=inner_unit_estimate,
    )
    _apply_answer(
        document, doc, "permitted_envelope",
        answer_ways=ways.permitted_envelope,
        standalone_withheld=[ways.rear_yard, ways.setback_above_base],
    )
    _apply_answer(
        document, doc, "building_option",
        answer_ways=ways.building_option,
        standalone_withheld=[],
    )

    # The apartment-estimate block is reserved in EVERY emitted document (reading O28).
    doc["unit_estimate"] = _reserved_unit_estimate()

    # Blocks worked out from a withheld result follow it - only where the engine actually produced
    # them (the lane is on and the building option was available to the engine).
    building_option_was_available = (
        document["answers"]["building_option"].get("status") == "available"
    )
    building_option_withheld = ways.building_option.whole_answer_not_available is not None
    if building_option_was_available and building_option_withheld:
        _apply_building_option_dependents(doc)
    _apply_geometry(doc, ways, building_option_withheld=building_option_withheld)

    # (O36) rewrite the five scope lines from the per-condition sources the evidence entry derived;
    # (M5-T139) rewrite the two design-choice lines the user made. Both read the scope block.
    if condition_sources is not None or user_choices is not None:
        _rewrite_scope_lines(doc, condition_sources, user_choices)

    _assert_no_qualifying_unit_value(doc)
    validate_results_document(doc)
    return doc


def _assert_no_qualifying_unit_value(doc: dict) -> None:
    """The qualifying-affordable and qualifying-senior unit limits are ALWAYS withheld by the module
    (it works out no figure for them): they are way entries only and never carry a value object."""
    allowance = doc["answers"].get("floor_area_allowance")
    if not isinstance(allowance, dict) or allowance.get("status") != "available":
        return
    shown = {v["key"] for v in allowance.get("values", [])}
    for key in (UNIT_QUALIFYING_AFFORDABLE_KEY, UNIT_QUALIFYING_SENIOR_KEY):
        assert key not in shown, f"{key} must never carry a value object (always withheld)"
