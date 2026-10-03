"""Thin, read-only access to Lane A rules for the three-answer generator (task A-04).

Every value the three answers use is REGISTRY-DERIVED - evaluated through the existing
rule evaluator, never a hand-copied constant (mirrors app.scenario.max_envelope). This
helper runs one rule, confirms its coverage is usable, and returns the requested output
with its Zoning Resolution sections, value sources and rule-version record, or a typed
gap naming why no value is available.

A rule held back by the Lane A flag (not indexed in the registry) is a gap with
``reason_kind='rule_not_implemented'``; an applicable rule whose coverage is not usable
(professional_review_required / data_conflict) is ``eligibility_unresolved``.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.rules import coverage as cov
from app.rules.registry import RuleRegistry

# Coverage statuses under which a rule OUTPUT is a usable allowance - the same set the
# accepted max-envelope engine treats as usable (conditional draft rules + verified).
USABLE_COVERAGE = frozenset({cov.COVERAGE_CONDITIONAL, cov.COVERAGE_VERIFIED})


@dataclass(frozen=True)
class RuleValue:
    """One usable rule output with its provenance."""

    rule_id: str
    rule_version: str
    rule_status: str
    output_name: str
    value: float
    coverage_status: str
    zr_sections: tuple[str, ...]


@dataclass(frozen=True)
class RuleGap:
    """A typed reason a rule produced no usable value (never a guessed number)."""

    rule_id: str
    reason: str
    reason_kind: str  # results.schema.json not_available reason_kind


class RuleParameterError(RuntimeError):
    """A declared rule-table parameter a caller depends on is absent or non-numeric. Raised
    fail-closed so a value (e.g. the dwelling-unit factor) can never silently drift from the
    rule table into a hand-copied literal."""


def rule_parameter(registry: RuleRegistry, rule_id: str, param_name: str) -> float:
    """Read a declared NUMERIC parameter from ``rule_id``'s rule table through the registry.

    Fails closed with :class:`RuleParameterError` when the rule is not indexed, the parameter
    is absent, or its declared value is not a finite number (booleans rejected). The value is
    the rule's own (e.g. ``dwelling_unit_factor = 680``), never a literal in calling code."""
    if rule_id not in registry.rule_ids():
        raise RuleParameterError(
            f"rule {rule_id!r} is not indexed; cannot read parameter {param_name!r}"
        )
    parameters = registry.rule(rule_id).parameters
    if param_name not in parameters:
        raise RuleParameterError(
            f"rule {rule_id!r} declares no parameter {param_name!r}"
        )
    value = parameters[param_name]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RuleParameterError(
            f"rule {rule_id!r} parameter {param_name!r} is not numeric: {value!r}"
        )
    return float(value)


def _zr_sections(citations: list[dict]) -> tuple[str, ...]:
    """Prefix each citation's section with 'ZR ' and de-duplicate, order-preserving."""
    out: list[str] = []
    for citation in citations:
        section = citation.get("section")
        if not section:
            continue
        label = f"ZR {section}"
        if label not in out:
            out.append(label)
    return tuple(out)


def evaluate_output(
    registry: RuleRegistry,
    rule_id: str,
    inputs: dict,
    output_name: str,
) -> RuleValue | RuleGap:
    """Evaluate ``rule_id`` and return its ``output_name`` as a :class:`RuleValue`, or a
    typed :class:`RuleGap`. Fails closed: a missing rule, an inapplicable rule, an
    unusable coverage, or an absent output all map to a gap, never to a number."""
    if rule_id not in registry.rule_ids():
        return RuleGap(
            rule_id=rule_id,
            reason=(
                f"Rule {rule_id} is not built for this district yet, or the Lane A "
                "engine is not enabled."
            ),
            reason_kind="rule_not_implemented",
        )
    result = registry.evaluate(rule_id, inputs)
    rule = registry.rule(rule_id)
    if result.coverage_status not in USABLE_COVERAGE:
        if result.coverage_status == cov.COVERAGE_NOT_APPLICABLE:
            reason = f"Rule {rule_id} does not apply to this lot's facts."
        else:
            reason = (
                f"Rule {rule_id} did not resolve for this lot (coverage "
                f"{result.coverage_status}); a required input may be missing or the "
                "site needs professional review."
            )
        return RuleGap(rule_id=rule_id, reason=reason, reason_kind="eligibility_unresolved")
    outputs = result.outputs
    if output_name not in outputs or outputs[output_name] is None:
        return RuleGap(
            rule_id=rule_id,
            reason=f"Rule {rule_id} produced no value for {output_name}.",
            reason_kind="missing_input",
        )
    return RuleValue(
        rule_id=rule_id,
        rule_version=rule.rule_version,
        rule_status=rule.status,
        output_name=output_name,
        value=float(outputs[output_name]),
        coverage_status=result.coverage_status,
        zr_sections=_zr_sections(result.trace.citations),
    )


def rule_version_record(registry: RuleRegistry, rule_id: str) -> dict | None:
    """The results-v1 rule_version record for ``rule_id``, or None when not indexed."""
    if rule_id not in registry.rule_ids():
        return None
    rule = registry.rule(rule_id)
    return {"rule_id": rule.rule_id, "version": rule.rule_version, "status": rule.status}
