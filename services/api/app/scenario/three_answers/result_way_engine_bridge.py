"""Run the three-answer engine and gather the scenario decision ways beside its result (task
M5-T134, Part 0 of docs/plans/R6B_RESULTS_CONNECTION_WORK_ORDER_2026-10-06.md; the third engine
piece, after M5-T130 carried the facts and M5-T131 added the validators).

This is the ONE thin adapter that hands the carried property profile, the prepared tax-map outline
and the site geometry - surfaced on :class:`~app.scenario.three_answers.ThreeAnswerInputs` by the
wiring of this task - together with the evaluator-inputs document the builders already produce, to
:func:`~app.scenario.three_answers.result_way_bridge.gather_result_ways`, and returns the decision
ways BESIDE the engine's :class:`~app.scenario.three_answers.engine.ThreeAnswersResult` in one
wrapper of its own.

IT EMITS THE THREE-WAY DOCUMENT (task M5-T136, reading O26). The engine still assembles exactly the
document it does today (contract 1.2.0), and this adapter then runs the pure transform
(:func:`~app.scenario.three_answers.three_way_document.emit_three_way_document`) over that document
and the gathered ways, and returns the contract-1.3.0 three-way document BESIDE the ways. It turns
on no production switch and is called by no route. ``engine.py`` is NOT edited and gets no field
typed by the decision module (reading O22): the emitting is done by the transform, outside the
engine; the engine's own ``ThreeAnswersResult`` still carries its unchanged document.

IMPORTS (reading O22 / O26). It imports
:func:`~app.scenario.three_answers.result_way_bridge.gather_result_ways`, the engine's
``generate_results`` / ``ThreeAnswersResult`` and the transform
:func:`~app.scenario.three_answers.three_way_document.emit_three_way_document`. It imports nothing
from the api layer and nothing from the spatial lot-reach module (the reach is measured inside
``gather_result_ways``). It names the decision module (through the transform and the bridge), so it
is one of the new app files the import guard permits.

NO DEFAULT STANDS FOR A FACT (rule L1, reading O21). When no prepared outline was produced the
outline is passed as absent and the reach stays unknown; when no profile was read every recorded
column is not read; nothing is invented here.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from app.contracts.evaluator_inputs import build_three_answer_inputs

from . import engine_conditions
from .engine import ThreeAnswersResult, generate_results
from .engine_conditions import DensityStatement, Presence
from .inputs import BuildingDefaults, ThreeAnswerInputs
from .result_way_bridge import GatheredResult, gather_result_ways
from .result_way_inputs import DensityKnowledge, LotType, Recorded
from .three_way_document import (
    FLOOR_TO_FLOOR_KEY,
    HOUSING_PROGRAM_KEY,
    USER_CHOICE_KEYS,
    emit_three_way_document,
)

if TYPE_CHECKING:  # pragma: no cover - typing only
    from app.rules.registry import RuleRegistry
    from app.spatial.site_geometry.outline import PreparedOutline
    from app.spatial.site_geometry.results import SiteGeometry

__all__ = [
    "FLOOR_TO_FLOOR_KEY",
    "HOUSING_PROGRAM_KEY",
    "USER_CHOICE_KEYS",
    "EngineResultWays",
    "run_engine_and_result_ways",
    "run_engine_and_result_ways_from_evidence",
]

# The recorded three-state (the decision step's own ``Recorded``) mapped to the plain presence the
# derivation module takes. Kept here, in a file the import guard already permits to name the
# decision module, so the derivation module (``engine_conditions``) stays free of that coupling.
_PRESENCE_BY_RECORDED = {
    Recorded.PRESENT: Presence.PRESENT,
    Recorded.ABSENT: Presence.ABSENT,
    Recorded.NOT_READ: Presence.NOT_READ,
}


def _is_corner(lot_type: LotType | None) -> bool | None:
    """True for a corner lot, False for an interior or through lot (no corner), None when the lot
    type was not read (then the corner conditions are not known, not 'no')."""
    if lot_type is None:
        return None
    return lot_type is LotType.CORNER


def _density_statement(knowledge: DensityKnowledge) -> DensityStatement:
    """The decision step's density knowledge mapped to the user's plain statement: the user's
    statement that the lot is not in a special density area, or no statement (every other state -
    none given, or a statement the program does not yet act on - carries no usable statement)."""
    if knowledge is DensityKnowledge.USER_STATEMENT_NOT_IN_ONE:
        return DensityStatement.NOT_IN_ONE
    return DensityStatement.NONE


@dataclass(frozen=True)
class EngineResultWays:
    """The engine's result, the gathered decision ways, and the emitted three-way document (reading
    O26). ``engine.py`` is not edited and its ``ThreeAnswersResult`` carries its own unchanged
    document; ``document`` here is the contract-1.3.0 three-way document the transform emits from
    that document and the ways. ``gathered`` holds the decision ways, the module input, the recorded
    facts and their provenance, the area statement, the large-lot answer and the held-back strings.
    """

    engine_result: ThreeAnswersResult
    gathered: GatheredResult
    document: dict


def run_engine_and_result_ways(
    inputs: ThreeAnswerInputs,
    *,
    evaluator_inputs: Mapping[str, Any] | None,
    special_density_statement: bool | None = None,
    registry: RuleRegistry | None = None,
    env: Mapping[str, str] | None = None,
) -> EngineResultWays:
    """Run the engine on ``inputs`` and gather the decision ways from the carried objects.

    The engine runs exactly as it does today (:func:`~app.scenario.three_answers.engine.
    generate_results`, with the caller's ``registry`` / ``env`` lane control) and emits an unchanged
    results document. The decision ways are then gathered from the objects CARRIED on ``inputs`` -
    the built property profile (``inputs.property_profile``), the prepared tax-map outline
    (``inputs.prepared_outline``) and the site geometry (``inputs.site_geometry``) - together with
    the ``evaluator_inputs`` document the builders already produce, the housing kind (the option,
    ``inputs.housing_program``) and an optional user statement about the special density area.

    When ``inputs.prepared_outline`` is None the outline is absent and the reach stays unknown
    (reading O21); when ``inputs.property_profile`` is None every recorded column is not read;
    nothing is invented and no default stands for a fact (rule L1). A user's statement is passed on
    as a statement and never enters a gathered fact record (owner rule R255).

    Returns :class:`EngineResultWays`: the engine's ``ThreeAnswersResult``, the ``GatheredResult``
    and the emitted contract-1.3.0 three-way ``document`` (reading O26). No caller of this adapter
    is wired to a route in this task; no production switch is turned on."""
    engine_result = generate_results(inputs, registry=registry, env=env)
    gathered = gather_result_ways(
        evaluator_inputs=evaluator_inputs,
        profile=inputs.property_profile,
        outline=inputs.prepared_outline,
        geometry=inputs.site_geometry,
        housing_kind=inputs.housing_program,
        special_density_statement=special_density_statement,
    )
    document = emit_three_way_document(engine_result.document, gathered.ways)
    return EngineResultWays(engine_result=engine_result, gathered=gathered, document=document)


def run_engine_and_result_ways_from_evidence(
    *,
    evaluator_inputs: Mapping[str, Any],
    study: Mapping[str, Any],
    results_id: str,
    computed_at: str,
    housing_program: str,
    property_profile: Mapping[str, Any] | None,
    prepared_outline: PreparedOutline | None,
    site_geometry: SiteGeometry | None,
    special_density_statement: bool | None = None,
    building_defaults: BuildingDefaults | None = None,
    user_choices: frozenset[str] | None = None,
    registry: RuleRegistry | None = None,
    env: Mapping[str, str] | None = None,
) -> EngineResultWays:
    """Run the engine and the three-way emit for a lot whose five engine conditions come from the
    SAME evidence the decision step gathers, never from a typed-in value (M5-T137, reading O33).

    This is the entry a server route uses: it takes what the server holds - the evaluator-inputs
    document, the study document, the option's housing program, the built property profile, the
    prepared tax-map outline, the site geometry, the user's optional statement about the special
    density area, and the result's id and time - and:

    (a) gathers the decision step's facts FIRST (:func:`gather_result_ways` over the same evidence);
    (b) derives the engine's five lot conditions from those SAME facts
        (:mod:`app.scenario.three_answers.engine_conditions`): the recorded commercial overlay and
        special purpose district, the corner reach and angle measured from the outline and geometry,
        and the user's density statement. Where a condition is not known the engine is given a
        value ONLY in the direction that withholds (``engine_conditions`` proves each from a rule);
    (c) builds the engine inputs with :func:`build_three_answer_inputs` using the DERIVED values,
        runs the engine, decides the ways and emits the three-way document - with the five scope
        lines rewritten to say where each condition comes from (reading O36).

    ``user_choices`` (M5-T139, DB-204 a) names which of the two design-choice scope rows the
    caller's request carried - the housing program and/or the floor-to-floor height
    (:data:`USER_CHOICE_KEYS`). It is NOT a fact about the lot: it records what the caller's own
    request contained. It is passed to the transform, which rewrites those rows to say the user's
    choice. When not given, nothing changes: the scope lines and the committed journey result are
    exactly as today.

    ``build_three_answer_inputs`` cross-checks ``overlay_present`` against the study's recorded
    commercial-overlay fact and fails closed if they disagree; the overlay value derived here comes
    from the SAME recorded data, so they agree. The engine, the decision modules, the disclosure
    builder and every schema stay read-only; no production switch is turned on and no route is
    wired here."""
    gathered = gather_result_ways(
        evaluator_inputs=evaluator_inputs,
        profile=property_profile,
        outline=prepared_outline,
        geometry=site_geometry,
        housing_kind=housing_program,
        special_density_statement=special_density_statement,
    )
    recorded = gathered.recorded
    reach = gathered.inputs.reach
    conditions = engine_conditions.derive_conditions(
        overlay_presence=_PRESENCE_BY_RECORDED[recorded.commercial_overlay.state],
        overlay_code=recorded.commercial_overlay.code,
        special_district_presence=_PRESENCE_BY_RECORDED[recorded.special_purpose_district.state],
        is_corner=_is_corner(gathered.inputs.lot_type),
        reach_ft=reach.corner.reach.value if reach is not None else None,
        angle_deg=reach.corner.angle.value if reach is not None else None,
        density_statement=_density_statement(gathered.inputs.special_density),
    )
    inputs = build_three_answer_inputs(
        dict(evaluator_inputs),
        results_id=results_id,
        computed_at=computed_at,
        housing_program=housing_program,
        overlay_present=conditions["overlay_present"].engine_value,
        special_district_present=conditions["special_district_present"].engine_value,
        within_100_ft_of_street_line_intersection=(
            conditions["within_100_ft_of_street_line_intersection"].engine_value
        ),
        street_line_intersection_angle_degrees=(
            conditions["street_line_intersection_angle_degrees"].engine_value
        ),
        special_density_area=conditions["special_density_area"].engine_value,
        building_defaults=building_defaults,
        study=dict(study),
        property_profile=property_profile,
        prepared_outline=prepared_outline,
        site_geometry=site_geometry,
    )
    engine_result = generate_results(inputs, registry=registry, env=env)
    document = emit_three_way_document(
        engine_result.document, gathered.ways,
        condition_sources=conditions, user_choices=user_choices,
    )
    return EngineResultWays(engine_result=engine_result, gathered=gathered, document=document)
