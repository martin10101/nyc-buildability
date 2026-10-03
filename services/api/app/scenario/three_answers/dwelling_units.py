"""The dwelling-unit estimate in ONE place, with its formula (task A-04; plan section 11b;
competitor-review check C-12).

Reads the Lane A ``r6b-dwelling-units`` rule, whose dividend is the standard residential
floor-area allowance this generator already computed. The rule carries the division and the
ZR 23-52(b) three-quarter rounding; this module shapes the results-v1 ``unit_estimate`` block
(the single source every surface repeats).
"""

from __future__ import annotations

from .answers import not_available
from .inputs import ThreeAnswerInputs
from .rule_access import RuleGap, RuleValue, evaluate_output, rule_parameter

_UNITS_RULE = "r6b-dwelling-units"
# The dwelling-unit factor is NOT a literal here: it is read from the rule table's declared
# parameter (r6b-dwelling-units parameters.dwelling_unit_factor) so the formula and the factor
# field can never drift from the rule the estimate is computed by (review F1).
_FACTOR_PARAM = "dwelling_unit_factor"


def _format_thousands(value: float) -> str:
    return f"{value:,.0f}"


def build_unit_estimate(
    inputs: ThreeAnswerInputs, registry, standard_floor_area_sq_ft: float | None
) -> dict:
    """The ``unit_estimate`` block: value, formula, factor, rounding rule and ZR sections, or
    not_available when the allowance or the rule is unavailable."""
    if standard_floor_area_sq_ft is None:
        return not_available(
            "The dwelling-unit estimate needs the residential floor-area allowance.",
            "missing_input",
        )
    units_inputs = inputs.dwelling_unit_inputs(standard_floor_area_sq_ft)
    before = evaluate_output(registry, _UNITS_RULE, units_inputs, "dwelling_units_before_rounding")
    value = evaluate_output(registry, _UNITS_RULE, units_inputs, "max_dwelling_units")
    if isinstance(before, RuleGap) or isinstance(value, RuleGap):
        gap = before if isinstance(before, RuleGap) else value
        return not_available(gap.reason, gap.reason_kind)
    assert isinstance(before, RuleValue) and isinstance(value, RuleValue)

    factor = rule_parameter(registry, _UNITS_RULE, _FACTOR_PARAM)
    formula = (
        f"{_format_thousands(standard_floor_area_sq_ft)} ÷ {factor:,.0f} = "
        f"{before.value:.2f}"
    )
    zr_sections = list(value.zr_sections) or ["ZR 23-52"]
    return {
        "status": "available",
        "value": int(value.value),
        "formula": formula,
        "factor": {"value": factor, "unit": "square_feet_per_dwelling_unit"},
        "rounding_rule": "rounds up only at .75 or more",
        "zr_sections": zr_sections,
    }
