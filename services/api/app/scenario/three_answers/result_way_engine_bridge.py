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

from .engine import ThreeAnswersResult, generate_results
from .inputs import ThreeAnswerInputs
from .result_way_bridge import GatheredResult, gather_result_ways
from .three_way_document import emit_three_way_document

if TYPE_CHECKING:  # pragma: no cover - typing only
    from app.rules.registry import RuleRegistry

__all__ = ["EngineResultWays", "run_engine_and_result_ways"]


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
