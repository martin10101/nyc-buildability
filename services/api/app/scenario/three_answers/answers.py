"""Answers 1 and 2 of the three answers (task A-04): the floor-area allowance and the
permitted envelope, each a results-v1 ``answer`` (available with values, or not_available
with a reason).

Both read ONLY from the Lane A rules through :mod:`rule_access`; no value is hand-copied.
The allowance surfaces the standard ZR 23-22 maximum AND the qualifying affordable/senior
alternative beside it (competitor-review check C-2), the alternative always labelled as a
separate legal determination this engine never makes. The envelope surfaces the ZR 23-432
heights (the ONE height lookup, check C-1), the ZR 23-362 lot coverage and the ZR 23-344(a)
rear-yard waiver.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .inputs import ThreeAnswerInputs
from .rule_access import RuleGap, RuleValue, evaluate_output

_FAR_RULE = "r6-r12-residential-far"
_QUALIFYING_FAR_RULE = "r6b-qualifying-housing-far"
_HEIGHT_RULE = "r6b-height"
_COVERAGE_RULE = "r6b-lot-coverage"
_REAR_YARD_RULE = "r6b-rear-yard-corner-waiver"


def rule_source(value: RuleValue) -> dict:
    return {"kind": "rule_table", "ref": f"{value.rule_id}@{value.rule_version}"}


def fact_source(fact_id: str) -> dict:
    return {"kind": "site_fact", "ref": fact_id}


def answer_value(
    *,
    key: str,
    label: str,
    value: float,
    unit: str,
    zr_sections: tuple[str, ...],
    sources: list[dict],
    exception_label: str | None = None,
) -> dict:
    """One results-v1 answer_value with its unit, ZR sections and sources."""
    return {
        "key": key,
        "label": label,
        "value": value,
        "unit": unit,
        "zr_sections": list(zr_sections),
        "sources": sources,
        "exception_label": exception_label,
    }


def not_available(reason: str, reason_kind: str) -> dict:
    return {"status": "not_available", "reason": reason, "reason_kind": reason_kind}


@dataclass(frozen=True)
class AllowanceResult:
    """The allowance answer plus the floor-area figures the rest of the engine reuses."""

    answer: dict
    standard_floor_area_sq_ft: float | None
    standard_far: float | None
    qualifying_floor_area_sq_ft: float | None
    rule_versions: tuple[dict, ...]


def build_allowance(
    inputs: ThreeAnswerInputs, registry, measurement: Mapping[str, str]
) -> AllowanceResult:
    """Floor-area allowance (plan section 5 answer 1): the most zoning floor area the rules
    allow (FAR x lot area), standard and qualifying alternative. Existing-building
    subtraction is reported separately (remaining_floor_area)."""
    rule_versions: list[dict] = []
    values: list[dict] = []

    far = evaluate_output(registry, _FAR_RULE, inputs.far_inputs(), "max_residential_far")
    area = evaluate_output(
        registry, _FAR_RULE, inputs.far_inputs(), "max_residential_floor_area_sq_ft"
    )
    if isinstance(far, RuleGap) or isinstance(area, RuleGap):
        gap = far if isinstance(far, RuleGap) else area
        return AllowanceResult(
            answer=not_available(gap.reason, gap.reason_kind),
            standard_floor_area_sq_ft=None,
            standard_far=None,
            qualifying_floor_area_sq_ft=None,
            rule_versions=tuple(rule_versions),
        )
    rule_versions.append(
        {"rule_id": far.rule_id, "version": far.rule_version, "status": far.rule_status}
    )
    far_sources = [rule_source(far)]
    area_sources = [rule_source(area)]
    if inputs.lot_area_fact_id:
        area_sources.append(fact_source(inputs.lot_area_fact_id))
    values.append(
        answer_value(
            key="max_residential_far",
            label="Maximum residential FAR (standard)",
            value=far.value,
            unit="ratio",
            zr_sections=far.zr_sections,
            sources=far_sources,
        )
    )
    values.append(
        answer_value(
            key="max_residential_floor_area",
            label="Maximum residential floor area (standard)",
            value=area.value,
            unit="square_feet",
            zr_sections=area.zr_sections,
            sources=area_sources,
        )
    )

    # The qualifying affordable / senior alternative (ZR 23-22 second column), surfaced
    # beside the standard allowance (C-2). Evaluated with a qualifying program so the
    # alternative value is computed; whether a development qualifies is never decided here.
    q_inputs = dict(inputs.qualifying_far_inputs())
    q_inputs["housing_program"] = "qualifying_affordable_housing"
    q_far = evaluate_output(
        registry, _QUALIFYING_FAR_RULE, q_inputs, "qualifying_max_residential_far"
    )
    q_area = evaluate_output(
        registry, _QUALIFYING_FAR_RULE, q_inputs, "qualifying_max_residential_floor_area_sq_ft"
    )
    qualifying_floor_area: float | None = None
    if isinstance(q_far, RuleValue) and isinstance(q_area, RuleValue):
        qualifying_floor_area = q_area.value
        rule_versions.append(
            {"rule_id": q_far.rule_id, "version": q_far.rule_version, "status": q_far.rule_status}
        )
        q_area_sources = [rule_source(q_area)]
        if inputs.lot_area_fact_id:
            q_area_sources.append(fact_source(inputs.lot_area_fact_id))
        values.append(
            answer_value(
                key="max_residential_far_qualifying_affordable_or_senior",
                label="Maximum residential FAR with qualifying affordable or senior housing",
                value=q_far.value,
                unit="ratio",
                zr_sections=q_far.zr_sections,
                sources=[rule_source(q_far)],
            )
        )
        values.append(
            answer_value(
                key="max_residential_floor_area_qualifying_affordable_or_senior",
                label=(
                    "Maximum residential floor area with qualifying affordable or senior housing"
                ),
                value=q_area.value,
                unit="square_feet",
                zr_sections=q_area.zr_sections,
                sources=q_area_sources,
            )
        )

    return AllowanceResult(
        answer={"status": "available", "values": values, "measurement": dict(measurement)},
        standard_floor_area_sq_ft=area.value,
        standard_far=far.value,
        qualifying_floor_area_sq_ft=qualifying_floor_area,
        rule_versions=tuple(rule_versions),
    )


@dataclass(frozen=True)
class EnvelopeResult:
    """The permitted-envelope answer plus the height/coverage/yard figures reused by the
    building option and geometry."""

    answer: dict
    max_building_height_ft: float | None
    max_base_height_ft: float | None
    min_base_height_ft: float | None
    max_lot_coverage_ratio: float | None
    rear_yard_required: bool | None  # False = waived (not required); None = unresolved
    height_zr_sections: tuple[str, ...]
    coverage_zr_sections: tuple[str, ...]
    rear_yard_zr_sections: tuple[str, ...]
    rule_versions: tuple[dict, ...]


# Each row is (rule_output_name, answer_value key, label, unit). The standard triple
# (min base / max base / max building) is surfaced first, then the qualifying-housing triple.
# The R6B ZR 23-432 table carries a SINGLE minimum-base-height column that spans the row (it is
# not repeated under the qualifying heading), so the qualifying minimum base height reads from
# the SAME ``min_base_height`` rule output (same 30 ft, same ZR 23-432) under its own key: a
# reader then sees min base / max base / max building for BOTH the standard (30 / 45 / 55) and
# the qualifying (30 / 45 / 65) cases, and the shared 30 ft is explicit rather than implied
# (D-090-R107 step 2; finding note docs/research/zr-snapshots/notes/
# 2026-10-04-r6b-minimum-base-height-20ft-sample.md section (d)).
_HEIGHT_OUTPUTS = (
    ("min_base_height", "min_base_height", "Minimum base height", "feet"),
    ("max_base_height", "max_base_height", "Maximum base height", "feet"),
    ("max_building_height", "max_building_height", "Maximum building height", "feet"),
    (
        "min_base_height",
        "min_base_height_qualifying_affordable_or_senior",
        "Minimum base height with qualifying affordable or senior housing",
        "feet",
    ),
    (
        "qualifying_max_base_height",
        "max_base_height_qualifying_affordable_or_senior",
        "Maximum base height with qualifying affordable or senior housing",
        "feet",
    ),
    (
        "qualifying_max_building_height",
        "max_building_height_qualifying_affordable_or_senior",
        "Maximum building height with qualifying affordable or senior housing",
        "feet",
    ),
)


def build_envelope(
    inputs: ThreeAnswerInputs, registry, measurement: Mapping[str, str]
) -> EnvelopeResult:
    """Permitted envelope (plan section 5 answer 2): base/maximum heights (ZR 23-432, the
    ONE height lookup - C-1), lot coverage (ZR 23-362) and the rear-yard waiver
    (ZR 23-344(a)). A corner lot's coverage and waiver come straight from the tables."""
    rule_versions: list[dict] = []
    values: list[dict] = []
    height_zr: tuple[str, ...] = ()
    coverage_zr: tuple[str, ...] = ()
    rear_yard_zr: tuple[str, ...] = ()
    heights: dict[str, float] = {}

    height_inputs = inputs.height_inputs()
    height_gap: RuleGap | None = None
    for output_name, key, label, unit in _HEIGHT_OUTPUTS:
        res = evaluate_output(registry, _HEIGHT_RULE, height_inputs, output_name)
        if isinstance(res, RuleGap):
            height_gap = res
            break
        heights[output_name] = res.value
        height_zr = res.zr_sections
        values.append(
            answer_value(
                key=key,
                label=label,
                value=res.value,
                unit=unit,
                zr_sections=res.zr_sections,
                sources=[rule_source(res)],
            )
        )
    if height_gap is not None:
        return EnvelopeResult(
            answer=not_available(height_gap.reason, height_gap.reason_kind),
            max_building_height_ft=None,
            max_base_height_ft=None,
            min_base_height_ft=None,
            max_lot_coverage_ratio=None,
            rear_yard_required=None,
            height_zr_sections=(),
            coverage_zr_sections=(),
            rear_yard_zr_sections=(),
            rule_versions=tuple(rule_versions),
        )
    height_rule_version = evaluate_output(
        registry, _HEIGHT_RULE, height_inputs, "max_building_height"
    )
    assert isinstance(height_rule_version, RuleValue)  # heights resolved above
    rule_versions.append(
        {
            "rule_id": height_rule_version.rule_id,
            "version": height_rule_version.rule_version,
            "status": height_rule_version.rule_status,
        }
    )

    coverage = evaluate_output(
        registry, _COVERAGE_RULE, inputs.coverage_inputs(), "max_residential_lot_coverage_percent"
    )
    coverage_ratio: float | None = None
    if isinstance(coverage, RuleValue):
        coverage_ratio = coverage.value / 100.0
        coverage_zr = coverage.zr_sections
        rule_versions.append(
            {
                "rule_id": coverage.rule_id,
                "version": coverage.rule_version,
                "status": coverage.rule_status,
            }
        )
        values.append(
            answer_value(
                key="max_lot_coverage",
                label="Maximum lot coverage",
                value=coverage.value,
                unit="percent",
                zr_sections=coverage.zr_sections,
                sources=[rule_source(coverage)],
            )
        )

    # Rear-yard waiver: output 0 = no rear yard required within 100 ft of the corner.
    rear = evaluate_output(
        registry,
        _REAR_YARD_RULE,
        inputs.rear_yard_inputs(),
        "rear_yard_required_within_100_ft_of_corner",
    )
    rear_yard_required: bool | None = None
    if isinstance(rear, RuleValue):
        rear_yard_required = bool(rear.value)  # 0 -> False (waived)
        rear_yard_zr = rear.zr_sections
        rule_versions.append(
            {"rule_id": rear.rule_id, "version": rear.rule_version, "status": rear.rule_status}
        )

    return EnvelopeResult(
        answer={"status": "available", "values": values, "measurement": dict(measurement)},
        max_building_height_ft=heights.get("max_building_height"),
        max_base_height_ft=heights.get("max_base_height"),
        min_base_height_ft=heights.get("min_base_height"),
        max_lot_coverage_ratio=coverage_ratio,
        rear_yard_required=rear_yard_required,
        height_zr_sections=height_zr,
        coverage_zr_sections=coverage_zr,
        rear_yard_zr_sections=rear_yard_zr,
        rule_versions=tuple(rule_versions),
    )
