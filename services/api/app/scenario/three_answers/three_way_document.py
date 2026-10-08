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
    "RESERVED_UNIT_ESTIMATE_REASON",
    "SHORTFALL_FOLLOWS_WITHHELD_BUILDING_OPTION",
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
def emit_three_way_document(document: dict, ways: ResultWays) -> dict:
    """Transform the engine's assembled results ``document`` into the contract-1.3.0 three-way
    document, given the decision-module ``ways``. Pure: it mutates a deep copy, computes no zoning
    number, and returns a strictly schema-valid document (the way-layer rule runs after the schema).
    """
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
