"""The three-answer generator entry point (task A-04, plan M1-14 / C-2 / C-11; directive
D-090).

``generate_results`` builds, from the benchmark-style inputs and the Lane A draft rule
tables, a results-v1 document carrying the three SEPARATE answers (floor-area allowance,
permitted envelope, building option with its floor stack, floor-by-floor table and computed
shortfall reason), the unit estimate in one place, and ONE geometry block in feet. It then
validates the document against the bundled results schema and returns it with the stated,
named assumptions.

Lane gate: the whole engine runs only when ``LANE_A_ENABLED`` is an explicit true token
(app.config.lane_enabled). With the flag off, nothing is computed - every answer, the
geometry and every rule-dependent block is ``not_available`` and the document is marked
draft. The engine is library-only; Lane C mounts any route later.

Honesty invariants held here:
- No answer is ever a number with a caution label; it is a value or 'not_available'.
- Every rule result is DRAFT (``needs_review``); ``draft`` is always true, so no surface
  presents these as reviewed (D-090-R010).
- The remaining-development-capacity slot never states a number: it is the owner-settled
  'Not confirmed' not_available (D-090-R038). Nothing claims the zoning lot is verified.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from app.config import lane_enabled
from app.rules.registry import RuleRegistry

from .answers import build_allowance, build_envelope, not_available
from .building_option import build_building_option
from .contract import validate_results_document
from .dwelling_units import build_unit_estimate
from .geometry import build_geometry
from .inputs import (
    MEASUREMENT_APPROXIMATE_TAX_MAP,
    MEASUREMENT_ASSUMED,
    Assumption,
    ThreeAnswerInputs,
)
from .rule_access import rule_version_record

CONTRACT_VERSION = "1.0.0"
LANE = "A"

LOT_SELECTION_STATEMENT = "Based on the lots you selected — the app does not verify the zoning lot"

# Owner-settled wording for the remaining-development-capacity slot (D-090-R038). The slot
# NEVER states a number; it is this not_available reason, shown as 'Remaining development
# capacity: Not confirmed'.
REMAINING_NOT_CONFIRMED_REASON = (
    "Needs verified zoning-lot boundaries and existing zoning floor area."
)

_DWELLING_UNITS_RULE = "r6b-dwelling-units"


@dataclass(frozen=True)
class ThreeAnswersResult:
    """The generator output: the validated results-v1 document plus the stated, named
    assumptions it rests on and the lane-enabled flag."""

    document: dict
    assumptions: tuple[Assumption, ...]
    lane_enabled: bool


def _resolve_registry(
    registry: RuleRegistry | None, env: Mapping[str, str] | None
) -> RuleRegistry:
    if registry is not None:
        return registry
    return RuleRegistry(env=env).load()


def _dedupe_rule_versions(*groups: tuple[dict, ...]) -> list[dict]:
    seen: dict[str, dict] = {}
    for group in groups:
        for record in group:
            seen.setdefault(record["rule_id"], record)
    return list(seen.values())


def _completeness_line() -> dict:
    """Fallback completeness line for the lane-off document only (nothing is computed). When
    the lane is enabled the add-on model computes the real line (app.scenario.addons)."""
    return {
        "text": (
            "Add-ons checked for this district: none (the zoning engine is not enabled)."
        ),
        "not_yet_covered": [
            "Add-on gains",
            "Best combination",
            "Existing-building keep / partial-rebuild / full-rebuild paths",
            "Setback lines",
        ],
    }


def _lane_off_document(inputs: ThreeAnswerInputs) -> dict:
    """The fully-gated document emitted when LANE_A_ENABLED is off: nothing is computed."""
    gap = not_available(
        "The zoning-math engine (Lane A) is not enabled; its draft rules are not reviewed.",
        "rule_not_reviewed",
    )
    geometry_gap = not_available(
        "The zoning-math engine (Lane A) is not enabled.", "rule_not_reviewed"
    )
    return _assemble_document(
        inputs=inputs,
        answers={
            "floor_area_allowance": dict(gap),
            "permitted_envelope": dict(gap),
            "building_option": dict(gap),
        },
        shortfall=dict(gap),
        floor_by_floor=[],
        floor_stack=dict(gap),
        unit_estimate=dict(gap),
        geometry=geometry_gap,
        rule_versions=[],
        status_strip=[{"text": "Zoning engine not enabled"}],
        notices_count=0,
    )


def _assemble_document(
    *,
    inputs: ThreeAnswerInputs,
    answers: dict,
    shortfall: dict,
    floor_by_floor: list[dict],
    floor_stack: dict,
    unit_estimate: dict,
    geometry: dict,
    rule_versions: list[dict],
    status_strip: list[dict],
    notices_count: int,
    addon_gains: list[dict] | None = None,
    best_combination: dict | None = None,
    completeness_line: dict | None = None,
) -> dict:
    return {
        "contract_version": CONTRACT_VERSION,
        "results_id": inputs.results_id,
        "study_id": inputs.study_id,
        "option_id": inputs.option_id,
        "revision": inputs.revision,
        "computed_at": inputs.computed_at,
        "out_of_date": False,
        "out_of_date_reason": None,
        "depends_on_fact_ids": list(inputs.depends_on_fact_ids),
        "lot_selection_statement": LOT_SELECTION_STATEMENT,
        "with_approvals_label": None,
        "answers": answers,
        "remaining_floor_area": not_available(
            REMAINING_NOT_CONFIRMED_REASON, "missing_input"
        ),
        "shortfall": shortfall,
        "addon_gains": addon_gains if addon_gains is not None else [],
        "best_combination": best_combination
        if best_combination is not None
        else not_available(
            "The add-on model is not built in this slice (task M1-25).", "rule_not_implemented"
        ),
        "completeness_line": completeness_line
        if completeness_line is not None
        else _completeness_line(),
        "status_strip": status_strip,
        "notices_count": notices_count,
        "floor_by_floor": floor_by_floor,
        "floor_stack": floor_stack,
        "existing_building": not_available(
            "Keep / partial-rebuild / full-rebuild paths need existing floor-by-floor zoning "
            "areas (task M2-08); not computed in this slice.",
            "missing_input",
        ),
        "unit_estimate": unit_estimate,
        "geometry": geometry,
        "rule_versions": rule_versions,
        "draft": True,
        "street_width_case": None,
    }


def generate_results(
    inputs: ThreeAnswerInputs,
    *,
    registry: RuleRegistry | None = None,
    env: Mapping[str, str] | None = None,
) -> ThreeAnswersResult:
    """Generate and validate the three-answer results-v1 document for one option.

    ``registry`` may be supplied (already loaded); otherwise one is built from ``env`` (the
    lane flag is read there). The returned document is strictly schema-valid."""
    resolved_env = env
    reg = _resolve_registry(registry, env)
    # Enablement: the default path reads LANE_A_ENABLED from ``env`` (app.config.lane_enabled);
    # a CALLER-SUPPLIED registry was already built with its own env, so we infer enablement from
    # the gated rule's presence in it (the lane-A rules are indexed only when the flag was on).
    enabled = lane_enabled(LANE, resolved_env) if registry is None else (
        _DWELLING_UNITS_RULE in reg.rule_ids()
    )

    assumptions = inputs.all_assumptions()

    if not enabled:
        document = _lane_off_document(inputs)
        validate_results_document(document)
        return ThreeAnswersResult(document=document, assumptions=assumptions, lane_enabled=False)

    site_measurement = inputs.site_measurement()
    allowance = build_allowance(inputs, reg, site_measurement)
    envelope = build_envelope(inputs, reg, site_measurement)
    option = build_building_option(inputs, allowance, envelope, MEASUREMENT_ASSUMED)
    unit_estimate = build_unit_estimate(inputs, reg, allowance.standard_floor_area_sq_ft)
    geometry = build_geometry(inputs, envelope, option.computation, MEASUREMENT_APPROXIMATE_TAX_MAP)

    rule_versions = _dedupe_rule_versions(allowance.rule_versions, envelope.rule_versions)
    if unit_estimate.get("status") == "available":
        units_version = rule_version_record(reg, _DWELLING_UNITS_RULE)
        if units_version is not None:
            rule_versions = _dedupe_rule_versions(tuple(rule_versions), (units_version,))

    # Add-on model (task A-06): automatic add-ons are already applied by the rules above;
    # the optional switches, their gains vs the current selection (empty by default) and the
    # 'Best combination' for the option's stated goal are computed from the SAME accepted rules.
    # Imported locally to keep the three_answers <-> addons package import acyclic.
    from app.scenario.addons import build_addon_results

    addons = build_addon_results(inputs, reg)

    document = _assemble_document(
        inputs=inputs,
        answers={
            "floor_area_allowance": allowance.answer,
            "permitted_envelope": envelope.answer,
            "building_option": option.answer,
        },
        shortfall=option.shortfall,
        floor_by_floor=option.floor_by_floor,
        floor_stack=option.floor_stack,
        unit_estimate=unit_estimate,
        geometry=geometry,
        rule_versions=rule_versions,
        status_strip=[
            {"text": "Zoning maximum"},
            {"text": "Approximate measurements"},
            {"text": "Lots you selected"},
        ],
        notices_count=len(assumptions),
        addon_gains=addons["addon_gains"],
        best_combination=addons["best_combination"],
        completeness_line=addons["completeness_line"],
    )
    validate_results_document(document)
    return ThreeAnswersResult(document=document, assumptions=assumptions, lane_enabled=True)
