"""Run the three-answer engine and gather the scenario decision ways beside its result (task
M5-T134, Part 0 of docs/plans/R6B_RESULTS_CONNECTION_WORK_ORDER_2026-10-06.md; the third engine
piece, after M5-T130 carried the facts and M5-T131 added the validators).

This is the ONE thin adapter that hands the carried property profile, the prepared tax-map outline
and the site geometry - surfaced on :class:`~app.scenario.three_answers.ThreeAnswerInputs` by the
wiring of this task - together with the evaluator-inputs document the builders already produce, to
:func:`~app.scenario.three_answers.result_way_bridge.gather_result_ways`, and returns the decision
ways BESIDE the engine's :class:`~app.scenario.three_answers.engine.ThreeAnswersResult` in one
wrapper of its own.

NOTHING IS EMITTED (reading O23). The engine still emits exactly the results document it does today
(contract 1.2.0, byte-for-byte); this adapter adds no field to that document, turns on no production
switch, and is called by no route. ``engine.py`` is NOT edited and gets no field typed by the
decision module (reading O22): the wrapper holds the engine's result beside the gathered ways, as an
EXTERNAL attach point.

IMPORTS (reading O22 / scenario S12). It imports ONLY
:func:`~app.scenario.three_answers.result_way_bridge.gather_result_ways` and the engine's
``generate_results`` / ``ThreeAnswersResult``. It imports nothing from the api layer and nothing
from the spatial lot-reach module (the reach is measured inside ``gather_result_ways``). It is
therefore the one new file under ``services/api/app`` that names the decision module, so it is the
one new caller the import guard permits.

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

if TYPE_CHECKING:  # pragma: no cover - typing only
    from app.rules.registry import RuleRegistry

__all__ = ["EngineResultWays", "run_engine_and_result_ways"]


@dataclass(frozen=True)
class EngineResultWays:
    """The engine's result beside the gathered decision ways (reading O22).

    An EXTERNAL wrapper: ``engine.py`` is not edited and its ``ThreeAnswersResult`` carries no
    decision-module field; this adapter is the only place the two objects sit together. ``gathered``
    holds the decision ways, the module input, the recorded facts and their provenance, the area
    statement, the large-lot answer and the held-back strings.
    """

    engine_result: ThreeAnswersResult
    gathered: GatheredResult


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

    Returns :class:`EngineResultWays`: the engine's ``ThreeAnswersResult`` beside the
    ``GatheredResult``. NOTHING IS EMITTED - the engine's document is unchanged and no caller of
    this adapter is wired to a route in this task."""
    engine_result = generate_results(inputs, registry=registry, env=env)
    gathered = gather_result_ways(
        evaluator_inputs=evaluator_inputs,
        profile=inputs.property_profile,
        outline=inputs.prepared_outline,
        geometry=inputs.site_geometry,
        housing_kind=inputs.housing_program,
        special_density_statement=special_density_statement,
    )
    return EngineResultWays(engine_result=engine_result, gathered=gathered)
