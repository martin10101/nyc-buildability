"""Labelled input channel from a study's site facts to the three-answer evaluator
(task C-07, plan docs/PRODUCT_PLAN_CURRENT_2026-09-28.md M1-08 'Labeled input channel
to the evaluator'; done-when 'Reviewed contract keeps entered values distinct from
facts'; directive D-090 R096).

Pure, offline, library-only (no route in this slice; C-08 wires engine -> API ->
dashboard). Two steps, each failing closed on a contract defect:

1. :func:`build_evaluator_inputs` reads a validated study document's site facts, picks
   ONE governing value per engine input, keeps the facts it overrode in ``displaced``,
   and returns a validated ``evaluator_inputs`` v1 document.
2. :func:`build_three_answer_inputs` turns that document (value, fact ids, weakest rank)
   plus the caller-supplied non-site inputs (program, overlay/special-district flags,
   geometry flags, document identity) into a
   :class:`app.scenario.three_answers.ThreeAnswerInputs`.

PRECEDENCE RULE (which value governs an engine input), grounded in the plan and the
already-accepted study operations - NOT invented here:

- An architect's EDIT (survey_entered or entered) overrides automatically-sourced data.
  Editing a value makes a new survey_entered/entered fact placed BESIDE the city value,
  which is never overwritten in place (plan section 3 step 3 'Each shows its source and
  can be edited'; section 4 'Entering survey numbers updates every dependent result';
  site_fact.schema.json ``editable`` ties the override path to entered/survey_entered;
  apps/web study-operations.ts enterSiteFactValue). The overridden city/computed fact
  travels in ``displaced``.
- Within the sourced/entered facts the plan's source order applies (plan section 4
  'Source order (highest available wins)'): survey (rank 1) > city records (rank 2) >
  approximate tax map (rank 3); an entered correction overrides the city value it was
  typed beside. This fixes the order survey_entered > entered > city_records >
  approximate_tax_map for the governing fact (:data:`_GOVERNING_PRIORITY`).
- A stated ASSUMPTION is NOT an override. The plan uses an assumption only where no
  sourced value exists (section 9 'Explicit assumptions'; section 3 step 4 takes an
  assumption for existing floor area only when no city source exists); section 4's source
  order omits it, and site_fact ``editable`` ties the override path to entered/
  survey_entered, not assumed. So an ``assumed`` fact governs an engine input ONLY when
  it is the sole value for it (no survey_entered/city_records/approximate_tax_map and no
  entered fact). An assumption recorded BESIDE a sourced or entered fact for the same
  input is a visible CONFLICT: :func:`build_evaluator_inputs` raises rather than silently
  picking either way (CLAUDE.md principle 3 fail-closed, principle 4 conflicts stay
  visible). An assumed governing record therefore never displaces anything (its
  ``displaced`` is empty - an invariant the evaluator_inputs contract also enforces).
- Two facts of the SAME rank for one input with DIFFERENT values are a visible conflict,
  raised (never resolved silently by fact id); two with the SAME value collapse to one.

WEAKEST-INPUT LABEL (``site_measurement_rank``). Each result carries the label of its
WEAKEST input (plan section 4 'Each result carries the label of its weakest input'). The
plan's source order ranks survey > city records > approximate (ranks 1-3); an entered or
assumed value is less authoritative than city data, the stated assumption weakest of all
(section 9), matching the order the site_fact contract lists its ranks in
(site_fact.schema.json #/$defs/measurement_known). So reliability runs survey_entered >
city_records > approximate_tax_map > entered > assumed (:data:`_RELIABILITY_ORDER`), and
``site_measurement_rank`` is the weakest among the governing records. This is distinct
from the governing order on purpose: governing answers 'whose value do we use', the label
answers 'how trustworthy is the weakest value we used' - so an entered value governs its
input yet honestly degrades the result's label to 'Entered'.

SCOPE / NOT INVENTED: the plan gives no rule for collapsing several street frontages or a
split district into the single scalar the current evaluator takes (that is the combined-
outline rule, plan section 4 'Multi-lot sites', and a later slice). So when an engine
input resolves to more than one distinct fact (different street or tax lot),
:func:`build_evaluator_inputs` raises rather than guessing which one to use.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from app.contracts.study_contracts import (
    validate_evaluator_inputs_document,
    validate_study_document,
)
from app.scenario.three_answers import BuildingDefaults, ThreeAnswerInputs

__all__ = [
    "CONTRACT_VERSION",
    "EvaluatorInputsError",
    "build_evaluator_inputs",
    "build_three_answer_inputs",
]

CONTRACT_VERSION = "1.0.0"

# site_fact key -> the ThreeAnswerInputs field the evaluator_inputs record fills. Only
# the measurable site values the evaluator consumes as scalars; commercial_overlay,
# street_width and existing_zoning_floor_area are not evaluator scalar inputs in this slice.
_SITE_KEY_TO_ENGINE_KEY = {
    "lot_area": "lot_area_sq_ft",
    "lot_frontage": "lot_front_ft",
    "lot_depth": "lot_depth_ft",
    "lot_type": "lot_type",
    "zoning_district": "zoning_district",
}

# Fixed emission / record order (deterministic output).
_ENGINE_KEY_ORDER = (
    "lot_area_sq_ft",
    "lot_front_ft",
    "lot_depth_ft",
    "lot_type",
    "zoning_district",
)

# Governing precedence AMONG SOURCED/ENTERED facts (lower governs): an architect edit
# (survey/entered) overrides automatically-sourced data; within each the plan's source
# order. 'assumed' is deliberately ABSENT - an assumption is not an override; it governs
# only as the sole value for an input, handled in _resolve_group. (Docstring: citations.)
_GOVERNING_PRIORITY = {
    "survey_entered": 0,
    "entered": 1,
    "city_records": 2,
    "approximate_tax_map": 3,
}

# Reliability order for the weakest-input label; later in the tuple = weaker.
_RELIABILITY_ORDER = (
    "survey_entered",
    "city_records",
    "approximate_tax_map",
    "entered",
    "assumed",
)

# Engine inputs ThreeAnswerInputs cannot default: a study missing one of these has no
# answer for it (that is 'Not available', handled by the caller/C-08, not guessed here).
_REQUIRED_ENGINE_KEYS = ("lot_area_sq_ft", "lot_type", "zoning_district")


class EvaluatorInputsError(Exception):
    """A study could not be turned into a valid evaluator-inputs channel. Raised
    server-side: an ambiguous or incomplete input set is surfaced, never guessed."""


def _is_known(fact: dict) -> bool:
    return fact["measurement"]["rank"] != "unknown"


def _single_value(engine_key: str, rank: str, facts: Sequence[dict]) -> dict:
    """One fact from a SAME-rank set. Two of the same rank with the SAME value collapse to
    one (deterministic by fact_id); DIFFERENT values are a visible conflict that is raised,
    never silently resolved by id (review F2)."""
    if len({f["value"] for f in facts}) > 1:
        ids = sorted(f["fact_id"] for f in facts)
        raise EvaluatorInputsError(
            f"conflicting {rank} values for {engine_key}: facts {ids[0]!r} and {ids[1]!r} "
            "record different values; resolve the conflict (keep one value)."
        )
    return sorted(facts, key=lambda f: f["fact_id"])[0]


def _resolve_group(engine_key: str, facts: Sequence[dict]) -> tuple[dict, list[dict]]:
    """The governing fact for one (engine input, street, lot) group and the facts it
    displaces. An assumption governs only when it is the sole value for the input; an
    assumption recorded beside a sourced/entered value is a visible conflict (raise, never
    a silent pick). Among sourced/entered facts the governing rank is the one that wins the
    source order, and only LOWER-ranked facts are displaced (same-rank duplicates collapse
    via _single_value)."""
    assumed = [f for f in facts if f["measurement"]["rank"] == "assumed"]
    sourced_or_entered = [f for f in facts if f["measurement"]["rank"] != "assumed"]

    if assumed and sourced_or_entered:
        raise EvaluatorInputsError(
            f"a stated assumption conflicts with a recorded value for {engine_key}; "
            "enter the value or remove the assumption"
        )
    if not sourced_or_entered:
        # Assumption is the sole value for the input, so it governs and displaces nothing.
        return _single_value(engine_key, "assumed", assumed), []

    governing_rank = min(
        (f["measurement"]["rank"] for f in sourced_or_entered),
        key=_GOVERNING_PRIORITY.__getitem__,
    )
    top = [f for f in sourced_or_entered if f["measurement"]["rank"] == governing_rank]
    governing = _single_value(engine_key, governing_rank, top)
    displaced = sorted(
        (f for f in sourced_or_entered if f["measurement"]["rank"] != governing_rank),
        key=lambda f: f["fact_id"],
    )
    return governing, list(displaced)


def _displaced_entry(fact: dict) -> dict:
    return {
        "fact_id": fact["fact_id"],
        "rank": fact["measurement"]["rank"],
        "label": fact["measurement"]["label"],
        "value": fact["value"],
    }


def _record(engine_key: str, governing: dict, displaced: Sequence[dict]) -> dict:
    """One governing_input record. The rank, label and source kind are copied verbatim
    from the site fact, so the evaluator_inputs vocabulary IS the site_fact contract's."""
    return {
        "key": engine_key,
        "value": governing["value"],
        "unit": governing["unit"],
        "fact_id": governing["fact_id"],
        "rank": governing["measurement"]["rank"],
        "label": governing["measurement"]["label"],
        "source_kind": governing["source"]["kind"],
        "governing": True,
        "displaced": [_displaced_entry(f) for f in displaced],
    }


def _weakest_rank(ranks: Sequence[str]) -> str:
    return max(ranks, key=_RELIABILITY_ORDER.index)


def build_evaluator_inputs(study: dict, option_id: str) -> dict:
    """Build and validate the evaluator_inputs v1 document for one option of ``study``.

    ``study`` is a (re-validated, fail-closed) study document; ``option_id`` names which
    option's evaluation these shared site facts feed. One governing record per engine
    input is chosen by the precedence rule in the module docstring. Raises
    :class:`EvaluatorInputsError` (fail closed, conflict visible) when the study has no
    known site value to evaluate; an engine input resolves to more than one distinct fact
    (multi-street / split-district, out of scope); a stated assumption sits beside a
    sourced or entered value for the same input; or two same-rank facts disagree on the
    value for one input."""
    validate_study_document(study)

    option_ids = [option["option_id"] for option in study["options"]]
    if option_id not in option_ids:
        raise EvaluatorInputsError(
            f"option {option_id!r} is not part of study {study['study_id']!r} "
            f"(options: {option_ids})"
        )

    # Group known facts by (engine input, street, tax lot): a city value and its
    # architect edit share all three, so they form one group; different streets or lots
    # are different inputs.
    groups: dict[tuple[str, Any, Any], list[dict]] = {}
    for fact in study["site"]["facts"]:
        engine_key = _SITE_KEY_TO_ENGINE_KEY.get(fact["key"])
        if engine_key is None or not _is_known(fact):
            continue
        groups.setdefault((engine_key, fact["street"], fact["lot_bbl"]), []).append(fact)

    by_engine: dict[str, list[list[dict]]] = {}
    for (engine_key, _street, _bbl), facts in groups.items():
        by_engine.setdefault(engine_key, []).append(facts)

    records: list[dict] = []
    for engine_key in _ENGINE_KEY_ORDER:
        resolved = by_engine.get(engine_key)
        if not resolved:
            continue
        if len(resolved) > 1:
            raise EvaluatorInputsError(
                f"engine input {engine_key!r} resolves to {len(resolved)} distinct site "
                "facts (different streets or tax lots); collapsing them is the combined-"
                "outline rule (plan section 4 'Multi-lot sites'), out of scope for C-07."
            )
        governing, displaced = _resolve_group(engine_key, resolved[0])
        records.append(_record(engine_key, governing, displaced))

    if not records:
        raise EvaluatorInputsError(
            f"study {study['study_id']!r} has no known site value for any engine input; "
            "nothing to evaluate."
        )

    document = {
        "contract_version": CONTRACT_VERSION,
        "study_id": study["study_id"],
        "option_id": option_id,
        "revision": study["revision"]["number"],
        "inputs": records,
        "site_measurement_rank": _weakest_rank([r["rank"] for r in records]),
        "depends_on_fact_ids": [r["fact_id"] for r in records],
    }
    validate_evaluator_inputs_document(document)
    return document


def build_three_answer_inputs(
    evaluator_inputs: dict,
    *,
    results_id: str,
    computed_at: str,
    housing_program: str,
    overlay_present: bool,
    special_district_present: bool,
    within_100_ft_of_street_line_intersection: bool,
    street_line_intersection_angle_degrees: float,
    special_density_area: bool,
    building_defaults: BuildingDefaults | None = None,
) -> ThreeAnswerInputs:
    """Build :class:`ThreeAnswerInputs` from a validated evaluator_inputs document.

    The site values, their fact ids and the weakest rank come from ``evaluator_inputs``;
    everything that is NOT a labelled site fact (the housing program, the overlay /
    special-district / geometry flags, and the results document identity) is supplied by
    the caller (the zoning determination and the option; C-08 wires them). Raises
    :class:`EvaluatorInputsError` when a required engine input (lot area, lot type, zoning
    district) is absent."""
    validate_evaluator_inputs_document(evaluator_inputs)

    by_key = {record["key"]: record for record in evaluator_inputs["inputs"]}
    missing = [key for key in _REQUIRED_ENGINE_KEYS if key not in by_key]
    if missing:
        raise EvaluatorInputsError(
            f"evaluator_inputs is missing required engine input(s) {missing}; the evaluator "
            "cannot compute an answer for them (surface 'Not available', never a guess)."
        )

    lot_area = by_key["lot_area_sq_ft"]
    front = by_key.get("lot_front_ft")
    depth = by_key.get("lot_depth_ft")

    return ThreeAnswerInputs(
        results_id=results_id,
        study_id=evaluator_inputs["study_id"],
        option_id=evaluator_inputs["option_id"],
        revision=evaluator_inputs["revision"],
        computed_at=computed_at,
        zoning_district=by_key["zoning_district"]["value"],
        lot_area_sq_ft=float(lot_area["value"]),
        lot_type=by_key["lot_type"]["value"],
        housing_program=housing_program,
        overlay_present=overlay_present,
        special_district_present=special_district_present,
        within_100_ft_of_street_line_intersection=within_100_ft_of_street_line_intersection,
        street_line_intersection_angle_degrees=street_line_intersection_angle_degrees,
        special_density_area=special_density_area,
        lot_front_ft=float(front["value"]) if front is not None else None,
        lot_depth_ft=float(depth["value"]) if depth is not None else None,
        building_defaults=building_defaults or BuildingDefaults(),
        depends_on_fact_ids=tuple(evaluator_inputs["depends_on_fact_ids"]),
        lot_area_fact_id=lot_area["fact_id"],
        site_measurement_rank=evaluator_inputs["site_measurement_rank"],
    )
