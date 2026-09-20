"""Proposal-conditioned rule checks (task M5-T054, D-076 phase B2).

The FIRST production caller of :func:`app.scenario.derivation.derive_proposal`. Given a
VALIDATED ``proposed_massing`` block, a caller-supplied :class:`LotContext`, and
caller-supplied lot rule-input facts (all parameters; nothing is fetched), it turns the
proposal's geometric FACTS into CHECKS against the EXISTING rule engine, grouped
PASS / FAIL / COULD_NOT_CHECK.

Load-bearing boundaries (permanent principle 1; D-076-R002):

* FACTS vs ALLOWANCES - ``provided_value`` is the proposal-PROVIDED fact
  (:data:`SOURCE_CLASS`); ``required_value`` is a rule OUTPUT. Never conflated, and the
  summary always carries the COULD_NOT_CHECK count so a passing subset is never
  whole-building approval.
* No new rule logic / no ruleset edits - every allowance comes from the EXISTING
  evaluator via the registry; this module reads rule OUTPUTS and coverage only.
* COULD_NOT_CHECK is first-class and names WHY. A PROVIDED fact that does not establish
  the quantity a rule governs is PROVIDED_FACT_NOT_COMMENSURATE: matching units do NOT
  make a geometric gross floor area a residential zoning floor area, nor a generic
  minimum wall-to-lot-line setback a rear-yard depth - designating those is a legal
  interpretation this module never makes. Any fallback stays the consuming rule's own
  validated direction (D-051).

Wiring preconditions (T051-G5 + DB-034(b)) bind HERE, the first caller: list-size
ceilings and coordinate/area finiteness, refused BEFORE derivation so no EvidenceRecord
carries a non-finite value, offending values shown only via a length-capped repr.

DB-034(d): builds NO scenario document and emits NO contract version (imports only
derivation symbols); the emit-only-when-a-block-is-present invariant rides to the first
EMITTING packet (B3). Purity (AS-7): stdlib + the B1 derivation module and this
package's evaluator/registry; no network/connector/file I/O; iteration bounded by the
validated block and the ceilings below.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum

from app.scenario.derivation import (
    SOURCE_CLASS,
    LotContext,
    ProposalDerivation,
    derive_proposal,
)

from . import coverage as cov
from .registry import RuleRegistry

__all__ = [
    "MAX_LOT_LINE_SEGMENTS", "MAX_STREET_LINES", "MAX_REFUSAL_REPR_LEN",
    "CheckDirection", "CheckOutcome", "CouldNotCheckReason", "ProposalCheckError",
    "ProposalCheck", "PROPOSAL_CHECKS", "RULE_INPUT_LOT_AREA_SOURCE",
    "CALLER_RULE_INPUT_NAMES", "CheckResult", "ProposalCheckReport", "check_proposal",
]


# ---------------------------------------------------------------------------
# Wiring-precondition ceilings + bounded repr (T051-G5, DB-034(b)).
# ---------------------------------------------------------------------------

#: Maximum caller-supplied lot-line segments; a list above this is a paste /
#: generation error and is refused before any derivation runs (fail-closed).
MAX_LOT_LINE_SEGMENTS = 1000

#: Maximum caller-supplied attested street-frontage lines; refused above this.
MAX_STREET_LINES = 500

#: Length cap (chars) for any offending value embedded in a refusal (DB-034(b)).
MAX_REFUSAL_REPR_LEN = 120


def _capped_repr(value: object, limit: int = MAX_REFUSAL_REPR_LEN) -> str:
    """A length-capped ``repr`` (DB-034(b)) so an oversized value can never bloat a
    refusal message."""
    text = repr(value)
    if len(text) > limit:
        return f"{text[:limit]}...(repr truncated at {limit} chars)"
    return text


# ---------------------------------------------------------------------------
# Typed vocabulary.
# ---------------------------------------------------------------------------


class CheckDirection(str, Enum):
    """Whether a rule OUTPUT is a ceiling the proposal must stay under or a floor it
    must meet. The direction is the consuming rule's own (D-051); never guessed."""

    #: PASS iff provided <= required (the output is a MAXIMUM allowance).
    MAXIMUM = "maximum"
    #: PASS iff provided >= required (the output is a MINIMUM requirement).
    MINIMUM = "minimum"


class CheckOutcome(str, Enum):
    """The grouped outcome of one proposal-conditioned check."""

    PASS = "pass"
    FAIL = "fail"
    #: First-class typed outcome: the check could not be run. NEVER a silent pass.
    COULD_NOT_CHECK = "could_not_check"


class CouldNotCheckReason(str, Enum):
    """The typed reason a check is COULD_NOT_CHECK - every value names WHY."""

    #: The derived proposal fact needed is a typed honest absence (no lot line, etc.).
    PROVIDED_FACT_ABSENT = "provided_fact_absent"
    #: The derived fact does not establish the quantity the rule OUTPUT governs -
    #: matching units are not equivalence (geometric gross floor area is not a
    #: residential zoning floor area; a generic minimum lot-line setback is not a
    #: rear-yard depth). Closing the gap needs a new derived fact or a caller
    #: designation, never a legal interpretation made here.
    PROVIDED_FACT_NOT_COMMENSURATE = "provided_fact_not_commensurate"
    #: No rule in the family is applicable to the supplied lot facts (a visible
    #: not_applicable, never a silent pass).
    NO_APPLICABLE_RULE = "no_applicable_rule"
    #: A rule applies but its coverage is professional_review_required /
    #: data_conflict, or a required input (e.g. an attested street width) is missing:
    #: no reliable allowance is produced.
    ALLOWANCE_UNRESOLVED = "allowance_unresolved"
    #: The family has no implemented rule in the registry (RE-S7 unsupported).
    FAMILY_UNSUPPORTED = "family_unsupported"
    #: More than one applicable rule independently produced the same allowance
    #: output; which governs is a legal determination this module never picks.
    AMBIGUOUS_RULE = "ambiguous_rule"


class ProposalCheckError(ValueError):
    """A wiring precondition failed, so no derivation/check was attempted. Carries
    the exact ``field`` (a dotted path into the caller inputs). Always typed."""

    def __init__(self, message: str, *, field: str) -> None:
        super().__init__(message)
        self.field = field


# ---------------------------------------------------------------------------
# The EXPLICIT, declared fact-mapping table (auditable data; AS-5).
#
# Each derived fact is a PROVIDED value compared against a rule OUTPUT (the
# allowance). No proposal-derived EvidenceRecord is ever fed as a rule INPUT. A
# check carrying a ``semantic_gap`` is structurally non-commensurable and ALWAYS
# surfaces COULD_NOT_CHECK (PROVIDED_FACT_NOT_COMMENSURATE), never a comparison.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProposalCheck:
    """One declared check: a derived PROVIDED fact vs a rule OUTPUT allowance."""

    check_id: str
    #: The rule FAMILY whose applicable rule supplies the allowance.
    family: str
    #: The rule OUTPUT name that is the allowance (a ceiling or a floor).
    required_output: str
    #: The key into :data:`_PROVIDED_FACT_KEYS` selecting the derived PROVIDED value.
    provided_fact: str
    #: Whether ``required_output`` is a MAXIMUM (ceiling) or MINIMUM (floor).
    direction: CheckDirection
    #: The unit of BOTH the provided and required value (they must be commensurate).
    unit: str
    #: A plain human label for the provided quantity (for B3 rendering).
    label: str
    #: When set, the provided fact does NOT establish the quantity ``required_output``
    #: governs; the check is COULD_NOT_CHECK (PROVIDED_FACT_NOT_COMMENSURATE) with this
    #: text as the reason. No rule is evaluated and no allowance is presented.
    semantic_gap: str | None = None

    def as_dict(self) -> dict:
        return {
            "check_id": self.check_id,
            "family": self.family,
            "required_output": self.required_output,
            "provided_fact": self.provided_fact,
            "direction": self.direction.value,
            "unit": self.unit,
            "label": self.label,
            "semantic_gap": self.semantic_gap,
        }


#: The derived-fact keys this module reads off a :class:`ProposalDerivation`. Any
#: ``provided_fact`` in :data:`PROPOSAL_CHECKS` must be one of these (guarded at
#: import by :func:`_assert_checks_valid`).
_PROVIDED_FACT_KEYS = (
    "lot_coverage", "gross_floor_area", "cumulative_height", "min_lot_line_setback",
)


_REAR_YARD_GAP = (
    "the proposal's minimum wall-to-lot-line setback is not a rear-yard depth: no "
    "rear lot line is designated in the derivation, so the generic minimum setback "
    "across all walls cannot establish the rear yard the rule governs - determining "
    "which lot line is the rear is a legal interpretation this module does not make"
)

_RESIDENTIAL_FAR_GAP = (
    "the proposal's derived gross floor area is a pure geometric gross (no zoning "
    "deductions, exemptions, or bonuses - see the B1 gross-floor-area exclusions) and "
    "is not a residential zoning floor area; the matching square-foot unit is not "
    "equivalence, so it cannot be compared against the residential-FAR allowance "
    "without a legal interpretation this module does not make"
)


#: The declared checks. ``lot_coverage`` and ``building_height`` are commensurable
#: (the derived fact IS the quantity the rule governs). ``rear_yard_depth`` and
#: ``residential_far_floor_area`` carry a ``semantic_gap`` and always surface
#: COULD_NOT_CHECK (PROVIDED_FACT_NOT_COMMENSURATE) - the derived fact does not
#: establish the governed quantity even though the units match.
PROPOSAL_CHECKS: tuple[ProposalCheck, ...] = (
    ProposalCheck(
        check_id="lot_coverage_ratio",
        family="lot_coverage",
        required_output="max_lot_coverage_ratio",
        provided_fact="lot_coverage",
        direction=CheckDirection.MAXIMUM,
        unit="ratio",
        label="proposed lot coverage ratio",
    ),
    ProposalCheck(
        check_id="building_height",
        family="residential_height_setback",
        required_output="max_building_height",
        provided_fact="cumulative_height",
        direction=CheckDirection.MAXIMUM,
        unit="feet",
        label="proposed cumulative building height",
    ),
    ProposalCheck(
        check_id="rear_yard_depth",
        family="rear_yard",
        required_output="min_rear_yard_depth_ft",
        provided_fact="min_lot_line_setback",
        direction=CheckDirection.MINIMUM,
        unit="feet",
        label="proposed minimum wall-to-lot-line setback",
        semantic_gap=_REAR_YARD_GAP,
    ),
    ProposalCheck(
        check_id="residential_far_floor_area",
        family="residential_far",
        required_output="max_residential_floor_area_sq_ft",
        provided_fact="gross_floor_area",
        direction=CheckDirection.MAXIMUM,
        unit="square_feet",
        label="proposed gross floor area",
        semantic_gap=_RESIDENTIAL_FAR_GAP,
    ),
)


# ---------------------------------------------------------------------------
# Rule-input bindings (auditable; AS-5): the ONLY values that reach the evaluator.
# ---------------------------------------------------------------------------

#: The lot-area rule input is sourced from ``LotContext.area_sq_ft`` (the single
#: source of truth; a same-named caller fact is dropped as unmapped).
RULE_INPUT_LOT_AREA_SOURCE = "lot_context.area_sq_ft"

#: The caller lot-fact names permitted to feed rule inputs. A caller fact whose key
#: is not listed here is recorded as unmapped and NEVER fed to a rule (no silent
#: dict merge). ``street_width_class`` is the caller-attested wide-street OUTPUT
#: shape consumed read-only - never re-derived here.
CALLER_RULE_INPUT_NAMES = (
    "zoning_district",
    "street_width_class",
    "site_class",
    "overlay_present",
    "special_district_present",
    "historic_district",
    "large_site",
    "lot_depth_ft",
)

_LOT_AREA_INPUT = "lot_area_sq_ft"

#: Coverage statuses under which a rule OUTPUT is a usable allowance. Any other
#: status makes the check COULD_NOT_CHECK - fail-closed, never a guessed value.
_USABLE_COVERAGE = frozenset({cov.COVERAGE_CONDITIONAL, cov.COVERAGE_VERIFIED})


# ---------------------------------------------------------------------------
# Result models.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CheckResult:
    """One proposal-conditioned check result. ``provided_value`` is the PROVIDED
    quantity (:data:`SOURCE_CLASS`); ``required_value`` is the rule-computed
    ALLOWANCE. Distinct fields, distinct provenance, never merged. On a FAIL,
    ``shortfall`` is the positive magnitude by which the proposal misses the
    allowance in the check's direction."""

    check_id: str
    family: str
    label: str
    unit: str
    direction: CheckDirection
    outcome: CheckOutcome
    provided_value: float | None
    required_value: float | None
    shortfall: float | None
    could_not_check_reason: CouldNotCheckReason | None
    detail: str
    # provenance
    scenario_label: str
    proposal_id: str | None
    source_class: str
    provided_input_ids: tuple[str, ...]
    provided_provenance: Mapping[str, object] | None
    rule_id: str | None
    rule_version: str | None
    rule_status: str | None
    coverage_status: str | None
    rule_citations: tuple[dict, ...]

    def as_dict(self) -> dict:
        reason = self.could_not_check_reason
        prov = self.provided_provenance
        return {
            "check_id": self.check_id,
            "family": self.family,
            "label": self.label,
            "unit": self.unit,
            "direction": self.direction.value,
            "outcome": self.outcome.value,
            "provided_value": self.provided_value,
            "required_value": self.required_value,
            "shortfall": self.shortfall,
            "could_not_check_reason": reason.value if reason is not None else None,
            "detail": self.detail,
            "provenance": {
                "scenario_label": self.scenario_label,
                "proposal_id": self.proposal_id,
                "source_class": self.source_class,
                "provided_input_ids": list(self.provided_input_ids),
                "provided_provenance": dict(prov) if prov is not None else None,
                "rule_id": self.rule_id,
                "rule_version": self.rule_version,
                "rule_status": self.rule_status,
                "coverage_status": self.coverage_status,
                "rule_citations": list(self.rule_citations),
            },
        }


@dataclass(frozen=True)
class ProposalCheckReport:
    """The grouped result of evaluating a proposal against the declared checks. The
    counts always include ``could_not_check_count`` (AS-4) so a passing subset is never
    presentable as whole-building approval. ``fact_mapping`` and ``rule_input_bindings``
    echo the declared, auditable mapping; ``unmapped_lot_facts`` surfaces every caller
    fact that was NOT fed to a rule input."""

    scenario_label: str
    proposal_id: str | None
    source_class: str
    outline_digest: str
    results: tuple[CheckResult, ...]
    pass_count: int
    fail_count: int
    could_not_check_count: int
    fact_mapping: tuple[ProposalCheck, ...]
    rule_input_bindings: Mapping[str, str]
    unmapped_lot_facts: tuple[str, ...]

    def as_dict(self) -> dict:
        return {
            "scenario_label": self.scenario_label,
            "proposal_id": self.proposal_id,
            "source_class": self.source_class,
            "outline_digest": self.outline_digest,
            "results": [r.as_dict() for r in self.results],
            "summary": {
                "pass": self.pass_count,
                "fail": self.fail_count,
                "could_not_check": self.could_not_check_count,
                "total": len(self.results),
            },
            "fact_mapping": [c.as_dict() for c in self.fact_mapping],
            "rule_input_bindings": dict(self.rule_input_bindings),
            "unmapped_lot_facts": list(self.unmapped_lot_facts),
        }


# ---------------------------------------------------------------------------
# Wiring preconditions (T051-G5, DB-034(b)): enforced BEFORE any derivation.
# ---------------------------------------------------------------------------


def _is_finite_number(value: object) -> bool:
    """True for a finite int/float that is not a bool. An int too large to convert
    to float (e.g. ``10**400``) is NOT finite for our purposes and is rejected."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:  # int too large to represent as a float
        return False


def _require_finite_point(point: object, field_path: str) -> None:
    if not isinstance(point, (list, tuple)) or len(point) != 2:
        raise ProposalCheckError(
            f"{field_path} must be an [x, y] pair; got {_capped_repr(point)}",
            field=field_path,
        )
    x, y = point[0], point[1]
    if not _is_finite_number(x) or not _is_finite_number(y):
        raise ProposalCheckError(
            f"{field_path} must be finite EPSG:2263 coordinates; got "
            f"{_capped_repr(point)} - a NaN/inf coordinate is refused before "
            "derivation so no evidence record can carry a non-finite value",
            field=field_path,
        )


def _enforce_wiring_preconditions(lot: LotContext) -> None:
    """Refuse a LotContext that would drive an unbounded or non-finite derivation,
    BEFORE :func:`derive_proposal` (the T051-G5 precondition set at the first caller).
    Typed :class:`ProposalCheckError` naming the exact field (and offending count)."""
    if not isinstance(lot, LotContext):
        raise ProposalCheckError(
            f"lot must be a LotContext; got {_capped_repr(type(lot))}", field="lot"
        )

    n_lines = len(lot.lot_line_segments)
    if n_lines > MAX_LOT_LINE_SEGMENTS:
        raise ProposalCheckError(
            f"lot.lot_line_segments has {n_lines} segment(s), above the "
            f"MAX_LOT_LINE_SEGMENTS ceiling ({MAX_LOT_LINE_SEGMENTS}); refused before "
            "derivation (fail-closed bounded iteration)",
            field="lot.lot_line_segments",
        )
    n_streets = len(lot.street_lines)
    if n_streets > MAX_STREET_LINES:
        raise ProposalCheckError(
            f"lot.street_lines has {n_streets} line(s), above the MAX_STREET_LINES "
            f"ceiling ({MAX_STREET_LINES}); refused before derivation (fail-closed "
            "bounded iteration)",
            field="lot.street_lines",
        )

    if not _is_finite_number(lot.area_sq_ft):
        raise ProposalCheckError(
            f"lot.area_sq_ft must be a finite number; got {_capped_repr(lot.area_sq_ft)}",
            field="lot.area_sq_ft",
        )

    for seg in lot.lot_line_segments:
        _require_finite_point(seg.start, f"lot.lot_line_segments[{seg.id!r}].start")
        _require_finite_point(seg.end, f"lot.lot_line_segments[{seg.id!r}].end")
    for line in lot.street_lines:
        _require_finite_point(line.start, f"lot.street_lines[{line.wall_id!r}].start")
        _require_finite_point(line.end, f"lot.street_lines[{line.wall_id!r}].end")


# ---------------------------------------------------------------------------
# Provided-value extraction from the derivation (each a PROVIDED fact).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _Provided:
    value: float | None
    input_ids: tuple[str, ...]
    provenance: Mapping[str, object] | None
    detail: str


def _provided_value(derivation: ProposalDerivation, key: str) -> _Provided:
    """Read one declared PROVIDED fact off the derivation. A typed honest absence
    (``value is None``) is preserved, never defaulted."""
    if key == "min_lot_line_setback":
        return _min_lot_line_setback(derivation)
    if key == "lot_coverage":
        rec = derivation.lot_coverage
    elif key == "gross_floor_area":
        rec = derivation.gross_floor_area.evidence
    elif key == "cumulative_height":
        rec = derivation.cumulative_height
    else:  # pragma: no cover - guarded at import by _assert_checks_valid
        raise ProposalCheckError(f"unknown provided_fact key {key!r}", field="provided_fact")
    return _Provided(rec.value, rec.input_ids, rec.provenance, rec.detail)


def _min_lot_line_setback(derivation: ProposalDerivation) -> _Provided:
    """The minimum wall-to-lot-line setback across the exterior walls - a typed honest
    absence when no wall has a derivable lot-line setback. A PROVIDED geometric value
    only; NOT a rear-yard depth."""
    best: float | None = None
    best_ids: tuple[str, ...] = ()
    for wall in derivation.wall_setbacks:
        rec = wall.lot_line_setback
        if rec.value is None:
            continue
        if best is None or rec.value < best:
            best = rec.value
            best_ids = rec.input_ids
    if best is None:
        return _Provided(
            None, (), None,
            "no wall has a derivable lot-line setback (no lot-line segment supplied); "
            "a typed honest absence, never a default distance",
        )
    return _Provided(
        best, best_ids, None,
        "minimum wall-to-lot-line setback across the exterior walls; a PROVIDED "
        "geometric value, not an allowance and not a rear-yard depth",
    )


# ---------------------------------------------------------------------------
# Rule-input assembly (auditable mapping; AS-5).
# ---------------------------------------------------------------------------


def _build_rule_inputs(
    lot: LotContext, lot_rule_facts: Mapping[str, object]
) -> tuple[dict, dict[str, str], tuple[str, ...]]:
    """Assemble the evaluator input dict from DECLARED sources only. ``lot_area_sq_ft``
    comes from ``LotContext.area_sq_ft``; every other input comes from a caller fact
    whose key is in :data:`CALLER_RULE_INPUT_NAMES`. A caller fact whose key is not
    permitted is recorded as unmapped and NEVER fed. Returns ``(inputs, bindings,
    unmapped)``."""
    inputs: dict = {_LOT_AREA_INPUT: float(lot.area_sq_ft)}
    bindings: dict[str, str] = {_LOT_AREA_INPUT: RULE_INPUT_LOT_AREA_SOURCE}
    unmapped: list[str] = []
    for key, value in lot_rule_facts.items():
        if key in CALLER_RULE_INPUT_NAMES:
            inputs[key] = value
            bindings[key] = f"caller_lot_fact:{key}"
        else:
            unmapped.append(key)
    return inputs, bindings, tuple(sorted(unmapped))


# ---------------------------------------------------------------------------
# Evaluate one check against the family's rules.
# ---------------------------------------------------------------------------


def _family_traces(
    registry: RuleRegistry, family: str, inputs: dict
) -> tuple[list[dict], bool]:
    """Evaluate every rule in ``family`` and return ``(exported_traces, supported)``.
    ``supported`` is False when the family has no implemented rule (RE-S7). Traces are
    taken through ``RuleResult.export()`` so a material value never leaves without
    resolvable provenance (PRD s19)."""
    family_coverage = registry.family_coverage(family)
    rule_ids = family_coverage.get("rule_ids")
    if not rule_ids:
        return [], False
    traces = [registry.evaluate(rule_id, inputs).export() for rule_id in rule_ids]
    return traces, True


def _select_allowance(
    traces: list[dict], required_output: str
) -> tuple[dict | None, CouldNotCheckReason | None, str, dict | None]:
    """Pick the single applicable rule trace that produced ``required_output`` as a
    usable allowance, or return the typed COULD_NOT_CHECK reason. Fail-closed: 0 usable
    -> NO_APPLICABLE_RULE / ALLOWANCE_UNRESOLVED; >1 -> AMBIGUOUS_RULE (never picks a
    winner, mirroring the evaluator's FH-2 stance). Returns ``(usable_trace, reason,
    detail, evidence_trace)``; ``evidence_trace`` is a representative
    applicable-but-unusable trace so an unresolved result can carry that rule's id and
    coverage status (naming WHY)."""
    usable: list[dict] = []
    evidence: dict | None = None
    for trace in traces:
        if not trace.get("applicability_outcome"):
            continue
        value = trace.get("outputs", {}).get(required_output)
        if trace.get("coverage_status") in _USABLE_COVERAGE and _is_finite_number(value):
            usable.append(trace)
        elif evidence is None:  # first applicable-but-unusable trace, kept as evidence
            evidence = trace
    if len(usable) == 1:
        return usable[0], None, "single applicable rule produced a usable allowance", usable[0]
    if len(usable) > 1:
        ids = sorted(str(t.get("rule_id")) for t in usable)
        detail = (f"{len(usable)} rules ({ids}) independently produced {required_output!r}; "
                  "which governs is a legal determination not picked here")
        return None, CouldNotCheckReason.AMBIGUOUS_RULE, detail, None
    if evidence is not None:  # >=1 applicable trace, none usable
        detail = ("an applicable rule produced no usable allowance (coverage is "
                  "professional_review_required / data_conflict, or a required input - e.g. "
                  "an attested street width - is missing); the allowance is unresolved")
        return None, CouldNotCheckReason.ALLOWANCE_UNRESOLVED, detail, evidence
    detail = ("no rule in the family is applicable to the supplied lot facts "
              "(a visible not_applicable, never a silent pass)")
    return None, CouldNotCheckReason.NO_APPLICABLE_RULE, detail, None


def _compare(
    direction: CheckDirection, provided: float, required: float
) -> tuple[CheckOutcome, float | None]:
    """Compare a PROVIDED value against a required allowance in the check's own
    direction. ``shortfall`` is the positive miss magnitude on a FAIL, else ``None``."""
    if direction is CheckDirection.MAXIMUM:
        return (CheckOutcome.PASS, None) if provided <= required else (
            CheckOutcome.FAIL, provided - required)
    return (CheckOutcome.PASS, None) if provided >= required else (
        CheckOutcome.FAIL, required - provided)


def _result(
    check: ProposalCheck, outcome: CheckOutcome, provided: _Provided, *,
    detail: str, scenario_label: str, proposal_id: str | None,
    required_value: float | None = None, shortfall: float | None = None,
    reason: CouldNotCheckReason | None = None, trace: dict | None = None,
) -> CheckResult:
    """Build one :class:`CheckResult`, keeping the PROVIDED fact and the REQUIRED
    allowance (with its rule provenance) in distinct fields - the single construction
    site for both the resolved and the COULD_NOT_CHECK paths."""
    t = trace or {}
    value = float(provided.value) if provided.value is not None else None
    return CheckResult(
        check_id=check.check_id, family=check.family, label=check.label,
        unit=check.unit, direction=check.direction, outcome=outcome,
        provided_value=value, required_value=required_value, shortfall=shortfall,
        could_not_check_reason=reason, detail=detail, scenario_label=scenario_label,
        proposal_id=proposal_id, source_class=SOURCE_CLASS,
        provided_input_ids=provided.input_ids, provided_provenance=provided.provenance,
        rule_id=t.get("rule_id"), rule_version=t.get("rule_version"),
        rule_status=t.get("rule_status"), coverage_status=t.get("coverage_status"),
        rule_citations=tuple(t.get("citations", ())),
    )


def _run_check(
    check: ProposalCheck, derivation: ProposalDerivation, registry: RuleRegistry,
    inputs: dict, *, scenario_label: str, proposal_id: str | None,
) -> CheckResult:
    provided = _provided_value(derivation, check.provided_fact)

    def cnc(reason: CouldNotCheckReason, detail: str, trace: dict | None = None) -> CheckResult:
        return _result(check, CheckOutcome.COULD_NOT_CHECK, provided, detail=detail,
                       reason=reason, trace=trace, scenario_label=scenario_label,
                       proposal_id=proposal_id)

    # Semantic gate FIRST: a declared non-commensurable check never yields a
    # determination, whatever the registry says (the PROVIDED value is still recorded).
    if check.semantic_gap is not None:
        return cnc(CouldNotCheckReason.PROVIDED_FACT_NOT_COMMENSURATE, check.semantic_gap)
    if provided.value is None:
        return cnc(CouldNotCheckReason.PROVIDED_FACT_ABSENT,
                   f"the proposal provides no {check.label} ({provided.detail})")

    traces, supported = _family_traces(registry, check.family, inputs)
    if not supported:
        return cnc(CouldNotCheckReason.FAMILY_UNSUPPORTED,
                   f"no rule implemented for family {check.family!r} in the active "
                   "registry (RE-S7 unsupported); left unchecked, never a silent pass")

    trace, reason, detail, evidence = _select_allowance(traces, check.required_output)
    if trace is None:
        assert reason is not None  # narrow for typing
        return cnc(reason, detail, trace=evidence)

    required = float(trace["outputs"][check.required_output])
    outcome, shortfall = _compare(check.direction, float(provided.value), required)
    detail = (f"{check.label} {provided.value} {check.unit} vs {check.direction.value} "
              f"allowance {required} {check.unit} ({check.required_output})")
    return _result(check, outcome, provided, detail=detail, required_value=required,
                   shortfall=shortfall, trace=trace, scenario_label=scenario_label,
                   proposal_id=proposal_id)


# ---------------------------------------------------------------------------
# Public entry point.
# ---------------------------------------------------------------------------


def check_proposal(
    block: object, lot: LotContext, lot_rule_facts: Mapping[str, object] | None = None,
    *, scenario_label: str, proposal_id: str | None = None,
    registry: RuleRegistry | None = None,
) -> ProposalCheckReport:
    """Check a proposed building against the EXISTING rule engine.

    ``block`` a VALIDATED ``proposed_massing`` block (re-validated by
    :func:`derive_proposal` as defense in depth); ``lot`` the caller-supplied
    :class:`LotContext`; ``lot_rule_facts`` the caller-supplied lot rule inputs
    (``street_width_class`` is the wide-street OUTPUT shape consumed read-only, never
    re-derived). Enforces the wiring preconditions, calls :func:`derive_proposal`
    EXACTLY ONCE, then evaluates each declared check via the existing evaluator and
    groups the results into PASS / FAIL / COULD_NOT_CHECK (the summary always carries
    the COULD_NOT_CHECK count, AS-4). Raises :class:`ProposalCheckError` only for a
    precondition failure; a degenerate-block error from derivation propagates
    unchanged."""
    if not isinstance(scenario_label, str) or not scenario_label.strip():
        raise ProposalCheckError(
            "scenario_label must be a non-empty string so every result is labeled",
            field="scenario_label",
        )
    facts: Mapping[str, object] = lot_rule_facts if lot_rule_facts is not None else {}

    _enforce_wiring_preconditions(lot)  # (1) preconditions BEFORE any derivation
    derivation = derive_proposal(block, lot)  # (2) derive the proposal FACTS once
    inputs, bindings, unmapped = _build_rule_inputs(lot, facts)  # (3) declared inputs only
    registry = registry or _default_registry()

    # (4)/(5) Run each declared check; group and count (COULD_NOT_CHECK first-class).
    results = tuple(
        _run_check(check, derivation, registry, inputs,
                   scenario_label=scenario_label, proposal_id=proposal_id)
        for check in PROPOSAL_CHECKS
    )
    passes = sum(r.outcome is CheckOutcome.PASS for r in results)
    fails = sum(r.outcome is CheckOutcome.FAIL for r in results)
    cnc = sum(r.outcome is CheckOutcome.COULD_NOT_CHECK for r in results)
    return ProposalCheckReport(
        scenario_label=scenario_label, proposal_id=proposal_id, source_class=SOURCE_CLASS,
        outline_digest=derivation.outline_digest, results=results,
        pass_count=passes, fail_count=fails, could_not_check_count=cnc,
        fact_mapping=PROPOSAL_CHECKS, rule_input_bindings=bindings,
        unmapped_lot_facts=tuple(unmapped),
    )


_REGISTRY: RuleRegistry | None = None


def _default_registry() -> RuleRegistry:
    """The lazily-loaded production registry (callers inject their own for tests)."""
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = RuleRegistry().load()
    return _REGISTRY


def _assert_checks_valid() -> None:
    """Import-time guard: every declared check names a known provided-fact key, so a
    typo can never silently drop a check."""
    for check in PROPOSAL_CHECKS:
        if check.provided_fact not in _PROVIDED_FACT_KEYS:
            raise ValueError(
                f"check {check.check_id!r} names unknown provided_fact "
                f"{check.provided_fact!r}"
            )


_assert_checks_valid()
