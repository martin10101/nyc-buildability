"""Deterministic maximum-buildable-envelope derivation (task M5-T064, D-082-R002).

The owner's post-B3 checkpoint directive (D-082): the smartest calculation comes FIRST -
the architect should see the rules-derived maximum BEFORE designing anything. Given the
analyzed lot's context and the applicable ruleset, this module derives the maximum buildable
envelope for the RECTANGLE-PRISM massing class the accepted checker
(:func:`app.rules.proposal_checks.check_proposal`) already prices, and PROVES the result is
self-consistent by running that same checker on the candidate it emits.

What it produces, per dimension (a MAXIMUM ceiling or a MINIMUM floor):

* the BINDING value - the tightest applicable rule's declared allowance for this lot,
  REGISTRY-DERIVED (evaluated through the EXISTING evaluator, never a hand-copied constant);
* per-dimension provenance - the BINDING rule id/version + the rule ids it OUT-BOUND;
* HONEST GAPS - a dimension whose governing rules cannot be computed for this lot is a typed
  gap in the :class:`EnvelopeGapReason` vocabulary naming WHY, never a guessed number and
  never silently dropped;
* a candidate ``proposed_massing`` draft (the accepted B0 shape, EPSG:2263) that SATURATES the
  computable binding values on a rectangle footprint FITTED TO THE LOT'S ACTUAL 2263 GEOMETRY -
  scaled to the lot's own proportions, anchored at the lot's real corner, and PROVEN contained
  within it; a lot whose supplied geometry is not a supported axis-aligned rectangle (or whose
  rules-derived footprint the lot cannot hold) is an EXPLICIT, typed candidate gap
  (:class:`CandidatePlacementStatus`) - never a fixed-anchor schematic presented as lot-fitted;
* GENERATOR-CHECKER CONSISTENCY - the candidate is run back through ``check_proposal``; the
  saturating dimensions must not FAIL (an emitted maximum the checker refuses is the defining
  failure of this slice and fails closed here).

The every-declaring-rule conservatism (mirroring
:func:`app.api.v1._proposal_fact_domains.derive_input_domains`). The maximum buildable envelope
must satisfy EVERY applicable rule simultaneously, so a MAXIMUM ceiling is the *tightest*
(smallest) allowance across the applicable-and-usable rules and a MINIMUM floor is the
*largest* requirement; the looser rules are automatically satisfied and are recorded as
out-competed. This is a conservative INTERSECTION, not a determination of which rule governs:
where more than one rule bounds a dimension the registry's own fail-closed conflict detector
(:meth:`RuleRegistry.detect_conflicts`, FH-2) is surfaced as an advisory for professional
review, and the whole envelope is disclosed as a rules-derived ESTIMATE, never an approval
(D-076-R002).

Commensurability (D-076-R002; identical stance to the accepted checker). Two dimensions are
STRUCTURALLY non-commensurable with the rectangle-prism massing class and are ALWAYS honest
gaps, whatever the registry says: the residential-FAR allowance governs a zoning floor area
that the prism's geometric gross is not, and the rear-yard depth governs a rear yard the prism
does not designate. Turning either into a saturating geometric dimension needs a legal
interpretation this module never makes.

Purity and determinism. Same ``lot_context`` + same ``registry`` = byte-stable output. The
module is pure computation on its parameters plus the existing evaluator/registry and the
accepted B0 validator; it performs NO network / connector / file I/O, builds NO scenario
document, and emits NO contract version (that stays with the scenario-workspace save path).
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum

from app.rules import coverage as cov
from app.rules.proposal_checks import (
    CALLER_RULE_INPUT_NAMES,
    RULE_INPUT_LOT_AREA_SOURCE,
    CheckOutcome,
    check_proposal,
)
from app.scenario.derivation import LotContext
from app.scenario.proposal import (
    MAX_FLOOR_TO_FLOOR_FT,
    NYC_2263_X_MAX,
    NYC_2263_X_MIN,
    NYC_2263_Y_MAX,
    NYC_2263_Y_MIN,
    ProposedMassingError,
    validate_proposed_massing,
)

__all__ = [
    "MASSING_CLASS",
    "ENVELOPE_DISCLOSURE",
    "ENVELOPE_DIMENSIONS",
    "EnvelopeDirection",
    "EnvelopeGapReason",
    "CandidatePlacementStatus",
    "CandidatePlacement",
    "MaxEnvelopeError",
    "EnvelopeDimensionSpec",
    "EnvelopeDimensionResult",
    "MaxEnvelope",
    "derive_max_envelope",
]


#: The single massing class this slice prices - a rectangular prism (a rectangle footprint
#: extruded to a height). Named on every result so a later class is additive, never a silent
#: reinterpretation of this one.
MASSING_CLASS = "rectangle_prism"

#: Fixed D-076-R002 honesty disclosure carried on every envelope. It is a rules-derived
#: ESTIMATE, never a record, permit, approval, or legal determination.
ENVELOPE_DISCLOSURE = (
    "This maximum-buildable envelope is a DETERMINISTIC, rules-derived ESTIMATE for the "
    "rectangle-prism massing class - NOT a city record, a permit, an approval, or a legal "
    "determination. Each dimension is the tightest applicable draft rule's allowance for this "
    "lot (the looser rules are automatically satisfied and recorded as out-competed); where "
    "more than one rule bounds a dimension, which rule governs is a legal determination "
    "requiring professional review, surfaced here as an advisory rather than resolved. "
    "Non-commensurable dimensions (residential FAR, rear yard) are disclosed as honest gaps. "
    "Qualified professional review is required before any reliance."
)

#: The evaluator input name for the lot area (mirrors the accepted checker's binding; the lot
#: area is sourced ONLY from ``LotContext.area_sq_ft``, never a caller fact).
_LOT_AREA_INPUT = "lot_area_sq_ft"

#: Coverage statuses under which a rule OUTPUT is a usable allowance - IDENTICAL to the accepted
#: checker's ``_USABLE_COVERAGE`` (a drift-guard test binds the two together so this can never
#: diverge from what ``check_proposal`` treats as usable).
_USABLE_COVERAGE = frozenset({cov.COVERAGE_CONDITIONAL, cov.COVERAGE_VERIFIED})


class EnvelopeDirection(str, Enum):
    """Whether a rule OUTPUT is a ceiling the envelope maximizes UP TO or a floor it must
    clear. The direction is the consuming rule's own; never guessed."""

    #: A MAXIMUM allowance: the envelope value is the TIGHTEST (smallest) across applicable
    #: rules (a value at it satisfies every applicable rule).
    MAXIMUM = "maximum"
    #: A MINIMUM requirement: the envelope value is the LARGEST across applicable rules.
    MINIMUM = "minimum"


class EnvelopeGapReason(str, Enum):
    """The typed reason a dimension is an honest gap rather than a binding value."""

    #: No rule in the family is applicable to the supplied lot facts (a visible
    #: not-applicable, never an invented ceiling - the "unbounded direction" case).
    NO_APPLICABLE_RULE = "no_applicable_rule"
    #: A rule applies but its coverage is professional_review_required / data_conflict, or a
    #: required input (e.g. an attested street width) is missing: no reliable allowance.
    ALLOWANCE_UNRESOLVED = "allowance_unresolved"
    #: The family has no implemented rule in the registry (RE-S7 unsupported).
    FAMILY_UNSUPPORTED = "family_unsupported"
    #: The dimension is structurally non-commensurable with the rectangle-prism massing class:
    #: the rule governs a quantity (a zoning floor area, a rear yard) this class does not
    #: parameterize, so the allowance cannot be saturated without a legal interpretation.
    NON_COMMENSURABLE_WITH_MASSING = "non_commensurable_with_massing"


class CandidatePlacementStatus(str, Enum):
    """Why a candidate footprint was (or was not) fitted to the lot. A candidate is emitted
    ONLY when the lot's supplied 2263 geometry is a supported axis-aligned rectangle the
    rules-derived footprint fits inside; every other outcome is an EXPLICIT typed gap so a
    schematic placement is never presented as lot-fitted."""

    #: The footprint was scaled to the lot's own proportions, anchored at the lot's real
    #: corner, and PROVEN contained within the lot rectangle.
    FITTED = "fitted"
    #: The maximum lot coverage ratio or the maximum height is an honest dimension gap, so no
    #: rules-derived footprint / prism can be sized at all (nothing to place).
    NO_SATURATING_BINDING = "no_saturating_binding"
    #: The lot's supplied geometry is not a supported axis-aligned rectangle (absent, non-
    #: axis-aligned, non-simple, degenerate, inconsistent with the recorded area, or outside
    #: the accepted NYC 2263 bounds); ``detail`` names which. NEVER a fixed-anchor schematic.
    LOT_GEOMETRY_UNSUPPORTED = "lot_geometry_unsupported"
    #: The rules-derived footprint area exceeds what the lot's own geometry can hold (the
    #: rules allow more coverage than the lot rectangle contains); the binding values stand
    #: but no contained candidate is emitted.
    FOOTPRINT_EXCEEDS_LOT = "footprint_exceeds_lot"
    #: Defense in depth: the constructed block failed B0 validation or the containment proof
    #: (construction guarantees neither happens); fail-closed with no candidate.
    CONSTRUCTION_INVALID = "construction_invalid"


class MaxEnvelopeError(ValueError):
    """A precondition failed, or the generator emitted a candidate its own checker refused
    (a generator-checker inconsistency - the defining failure of this slice). Carries the
    exact ``field``; always typed."""

    def __init__(self, message: str, *, field: str) -> None:
        super().__init__(message)
        self.field = field


# ---------------------------------------------------------------------------
# The declared, auditable dimension table.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EnvelopeDimensionSpec:
    """One declared envelope dimension: a family's rule OUTPUT interpreted as a ceiling or a
    floor. ``saturating`` marks a dimension that geometrically bounds the rectangle-prism
    candidate (footprint or height). ``semantic_gap`` marks a dimension that is ALWAYS an
    honest gap (non-commensurable), whatever the registry produces."""

    dimension_id: str
    family: str
    required_output: str
    direction: EnvelopeDirection
    unit: str
    label: str
    saturating: bool
    semantic_gap: str | None = None


_REAR_YARD_GAP = (
    "the rectangle-prism massing class designates no rear lot line, so a rear-yard-depth "
    "allowance cannot be turned into a saturating footprint constraint - determining which "
    "lot line is the rear is a legal interpretation this engine does not make"
)

_RESIDENTIAL_FAR_GAP = (
    "the rectangle-prism's geometric gross floor area is not a residential zoning floor area "
    "(no zoning deductions, exemptions, or bonuses), so the residential-FAR allowance cannot "
    "be saturated as a geometric dimension without a legal interpretation this engine does "
    "not make"
)


#: The declared dimensions. ``max_lot_coverage_ratio`` and ``max_building_height`` are
#: commensurable and SATURATING (they size the footprint and the height). The FAR and rear-yard
#: dimensions carry a ``semantic_gap`` and are always honest gaps. The families / output names
#: MIRROR the accepted checker's ``PROPOSAL_CHECKS`` so a candidate that saturates the binding
#: values is checkable by ``check_proposal`` at those exact outputs (generator-checker
#: consistency).
ENVELOPE_DIMENSIONS: tuple[EnvelopeDimensionSpec, ...] = (
    EnvelopeDimensionSpec(
        dimension_id="max_lot_coverage_ratio",
        family="lot_coverage",
        required_output="max_lot_coverage_ratio",
        direction=EnvelopeDirection.MAXIMUM,
        unit="ratio",
        label="maximum lot coverage ratio",
        saturating=True,
    ),
    EnvelopeDimensionSpec(
        dimension_id="max_building_height",
        family="residential_height_setback",
        required_output="max_building_height",
        direction=EnvelopeDirection.MAXIMUM,
        unit="feet",
        label="maximum building height",
        saturating=True,
    ),
    EnvelopeDimensionSpec(
        dimension_id="max_residential_floor_area_sq_ft",
        family="residential_far",
        required_output="max_residential_floor_area_sq_ft",
        direction=EnvelopeDirection.MAXIMUM,
        unit="square_feet",
        label="maximum residential zoning floor area",
        saturating=False,
        semantic_gap=_RESIDENTIAL_FAR_GAP,
    ),
    EnvelopeDimensionSpec(
        dimension_id="min_rear_yard_depth_ft",
        family="rear_yard",
        required_output="min_rear_yard_depth_ft",
        direction=EnvelopeDirection.MINIMUM,
        unit="feet",
        label="minimum rear yard depth",
        saturating=False,
        semantic_gap=_REAR_YARD_GAP,
    ),
)

#: The checker ``check_id`` that verifies each SATURATING dimension's candidate value (used by
#: the generator-checker consistency proof).
_SATURATING_CHECK_IDS = {
    "max_lot_coverage_ratio": "lot_coverage_ratio",
    "max_building_height": "building_height",
}


# ---------------------------------------------------------------------------
# Result models.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EnvelopeDimensionResult:
    """One resolved (or gapped) envelope dimension. Exactly one of ``binding_value`` and
    ``gap_reason`` is set."""

    dimension_id: str
    family: str
    required_output: str
    direction: EnvelopeDirection
    unit: str
    label: str
    saturating: bool
    binding_value: float | None
    binding_rule_id: str | None
    binding_rule_version: str | None
    coverage_status: str | None
    out_competed_rule_ids: tuple[str, ...]
    rule_citations: tuple[dict, ...]
    gap_reason: EnvelopeGapReason | None
    conflict_advisory: Mapping[str, object] | None
    detail: str

    def as_dict(self) -> dict:
        reason = self.gap_reason
        adv = self.conflict_advisory
        return {
            "dimension_id": self.dimension_id,
            "family": self.family,
            "required_output": self.required_output,
            "direction": self.direction.value,
            "unit": self.unit,
            "label": self.label,
            "saturating": self.saturating,
            "binding_value": self.binding_value,
            "binding_rule_id": self.binding_rule_id,
            "binding_rule_version": self.binding_rule_version,
            "coverage_status": self.coverage_status,
            "out_competed_rule_ids": list(self.out_competed_rule_ids),
            "rule_citations": list(self.rule_citations),
            "gap_reason": reason.value if reason is not None else None,
            "conflict_advisory": dict(adv) if adv is not None else None,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class CandidatePlacement:
    """How the candidate footprint relates to the lot's actual 2263 geometry. Present on every
    envelope (even when no candidate is emitted), so the placement outcome is always explicit
    and machine-readable rather than only a free-text note."""

    status: CandidatePlacementStatus
    detail: str
    #: The lot's supported axis-aligned bounding rectangle (only when geometry is supported).
    lot_rectangle: dict | None = None
    #: The emitted footprint's anchor + dimensions (only on a FITTED candidate).
    footprint: dict | None = None
    #: Whether the emitted footprint was PROVEN contained within the lot rectangle (FITTED only).
    contained: bool | None = None

    def as_dict(self) -> dict:
        return {
            "status": self.status.value,
            "detail": self.detail,
            "lot_rectangle": self.lot_rectangle,
            "footprint": self.footprint,
            "contained": self.contained,
        }


@dataclass(frozen=True)
class MaxEnvelope:
    """The full maximum-buildable envelope for the rectangle-prism massing class."""

    massing_class: str
    label: str | None
    disclosure: str
    dimensions: tuple[EnvelopeDimensionResult, ...]
    candidate: dict | None
    candidate_notes: tuple[str, ...]
    candidate_placement: CandidatePlacement
    candidate_consistency: dict | None
    binding_count: int
    gap_count: int
    saturating_binding_count: int
    rule_input_bindings: Mapping[str, str]
    unmapped_lot_facts: tuple[str, ...]

    def as_dict(self) -> dict:
        return {
            "massing_class": self.massing_class,
            "label": self.label,
            "disclosure": self.disclosure,
            "dimensions": [d.as_dict() for d in self.dimensions],
            "candidate": self.candidate,
            "candidate_notes": list(self.candidate_notes),
            "candidate_placement": self.candidate_placement.as_dict(),
            "candidate_consistency": self.candidate_consistency,
            "summary": {
                "binding": self.binding_count,
                "gap": self.gap_count,
                "saturating_binding": self.saturating_binding_count,
                "total": len(self.dimensions),
            },
            "rule_input_bindings": dict(self.rule_input_bindings),
            "unmapped_lot_facts": list(self.unmapped_lot_facts),
        }


# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------


def _is_finite_number(value: object) -> bool:
    """True for a finite int/float that is not a bool (JSON booleans are ints in Python and
    must never pass a numeric check). An int too large to convert to float is not finite."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _build_rule_inputs(
    lot: LotContext, lot_rule_facts: Mapping[str, object]
) -> tuple[dict, dict[str, str], tuple[str, ...]]:
    """Assemble the evaluator input dict from DECLARED sources only, MIRRORING the accepted
    checker: ``lot_area_sq_ft`` comes from ``LotContext.area_sq_ft`` (single source of truth);
    every other input comes from a caller fact whose key is in
    :data:`~app.rules.proposal_checks.CALLER_RULE_INPUT_NAMES`. A caller fact whose key is not
    permitted is recorded as unmapped and NEVER fed."""
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


def _family_traces(registry, family: str, inputs: dict) -> tuple[list[dict], bool]:
    """Evaluate every rule in ``family`` and return ``(exported_traces, supported)``.
    ``supported`` is False when the family has no implemented rule (RE-S7). Traces are taken
    through ``RuleResult.export()`` so a material value never leaves without resolvable
    provenance (PRD s19). Mirrors the accepted checker's own family evaluation."""
    family_coverage = registry.family_coverage(family)
    rule_ids = family_coverage.get("rule_ids")
    if not rule_ids:
        return [], False
    traces = [registry.evaluate(rule_id, inputs).export() for rule_id in rule_ids]
    return traces, True


@dataclass(frozen=True)
class _Binding:
    value: float
    rule_id: str
    rule_version: str | None
    coverage_status: str | None
    citations: tuple[dict, ...]
    out_competed: tuple[str, ...]


def _select_binding(
    traces: list[dict], required_output: str, direction: EnvelopeDirection
) -> tuple[_Binding | None, EnvelopeGapReason | None, str]:
    """Pick the BINDING allowance across the family's traces, or the typed gap reason.

    The binding value is the TIGHTEST usable allowance (smallest for a MAXIMUM ceiling, largest
    for a MINIMUM floor); ties are broken by the lowest rule id, deterministically. Every other
    usable rule produced a looser bound the envelope automatically satisfies and is recorded as
    out-competed. Fail-closed: 0 usable with >=1 applicable -> ALLOWANCE_UNRESOLVED; 0 applicable
    -> NO_APPLICABLE_RULE (the honest "unbounded direction" case, never an invented ceiling)."""
    usable: list[dict] = []
    applicable = False
    for trace in traces:
        if not trace.get("applicability_outcome"):
            continue
        applicable = True
        value = trace.get("outputs", {}).get(required_output)
        if trace.get("coverage_status") in _USABLE_COVERAGE and _is_finite_number(value):
            usable.append(trace)
    if not usable:
        if applicable:
            return (
                None,
                EnvelopeGapReason.ALLOWANCE_UNRESOLVED,
                "an applicable rule produced no usable allowance (coverage is "
                "professional_review_required / data_conflict, or a required input is "
                "missing); the bound is unresolved, never guessed",
            )
        return (
            None,
            EnvelopeGapReason.NO_APPLICABLE_RULE,
            "no rule in the family is applicable to the supplied lot facts; this direction "
            "is unbounded by the registry - an honest gap, never an invented ceiling",
        )

    def value_of(trace: dict) -> float:
        return float(trace["outputs"][required_output])

    if direction is EnvelopeDirection.MAXIMUM:
        binding = min(usable, key=lambda t: (value_of(t), str(t.get("rule_id"))))
    else:  # MINIMUM: largest value, tie -> lowest rule id
        binding = min(usable, key=lambda t: (-value_of(t), str(t.get("rule_id"))))

    binding_id = str(binding.get("rule_id"))
    out_competed = tuple(
        sorted(str(t.get("rule_id")) for t in usable if str(t.get("rule_id")) != binding_id)
    )
    detail = (
        f"binding {direction.value} allowance {value_of(binding)} from rule {binding_id!r}"
        + (f"; out-competed {list(out_competed)}" if out_competed else "; sole applicable rule")
    )
    return (
        _Binding(
            value=value_of(binding),
            rule_id=binding_id,
            rule_version=binding.get("rule_version"),
            coverage_status=binding.get("coverage_status"),
            citations=tuple(binding.get("citations", ())),
            out_competed=out_competed,
        ),
        None,
        detail,
    )


def _conflict_advisory(registry, family: str, required_output: str, inputs: dict) -> dict | None:
    """Surface the registry's OWN fail-closed FH-2 conflict detector (if the registry provides
    one) as an advisory when more than one rule competes for this output - for professional
    review, never resolved here. Guarded by ``getattr`` so a test double without the method is
    fine."""
    detect = getattr(registry, "detect_conflicts", None)
    if not callable(detect):
        return None
    conflict = detect(family, inputs)
    if not isinstance(conflict, Mapping):
        return None
    if required_output not in conflict.get("competing_output_names", ()):
        return None
    return {
        "competing_rule_ids": [r["rule_id"] for r in conflict.get("competing_rules", ())],
        "note": conflict.get("note"),
    }


def _resolve_dimension(
    spec: EnvelopeDimensionSpec, registry, inputs: dict
) -> EnvelopeDimensionResult:
    """Resolve one declared dimension to a binding value + provenance or a typed honest gap."""

    def gap(reason: EnvelopeGapReason, detail: str) -> EnvelopeDimensionResult:
        return EnvelopeDimensionResult(
            dimension_id=spec.dimension_id, family=spec.family,
            required_output=spec.required_output, direction=spec.direction, unit=spec.unit,
            label=spec.label, saturating=spec.saturating, binding_value=None,
            binding_rule_id=None, binding_rule_version=None, coverage_status=None,
            out_competed_rule_ids=(), rule_citations=(), gap_reason=reason,
            conflict_advisory=None, detail=detail,
        )

    # Semantic gate FIRST: a non-commensurable dimension is always an honest gap, whatever the
    # registry produces (identical stance to the accepted checker's semantic gate).
    if spec.semantic_gap is not None:
        return gap(EnvelopeGapReason.NON_COMMENSURABLE_WITH_MASSING, spec.semantic_gap)

    traces, supported = _family_traces(registry, spec.family, inputs)
    if not supported:
        return gap(
            EnvelopeGapReason.FAMILY_UNSUPPORTED,
            f"no rule implemented for family {spec.family!r} in the active registry "
            "(RE-S7 unsupported); an honest gap, never a fabricated ceiling",
        )

    binding, reason, detail = _select_binding(traces, spec.required_output, spec.direction)
    if binding is None:
        assert reason is not None  # narrow for typing
        return gap(reason, detail)

    advisory = _conflict_advisory(registry, spec.family, spec.required_output, inputs)
    return EnvelopeDimensionResult(
        dimension_id=spec.dimension_id, family=spec.family,
        required_output=spec.required_output, direction=spec.direction, unit=spec.unit,
        label=spec.label, saturating=spec.saturating, binding_value=binding.value,
        binding_rule_id=binding.rule_id, binding_rule_version=binding.rule_version,
        coverage_status=binding.coverage_status, out_competed_rule_ids=binding.out_competed,
        rule_citations=binding.citations, gap_reason=None, conflict_advisory=advisory,
        detail=detail,
    )


# ---------------------------------------------------------------------------
# Candidate construction (deterministic, FITTED to the lot's actual 2263 geometry).
# ---------------------------------------------------------------------------

#: Relative tolerance binding the lot-line bounding rectangle's area to the RECORDED lot area.
#: The candidate's coverage denominator is the AUTHORITATIVE ``LotContext.area_sq_ft`` (what the
#: checker divides the footprint by); a lot is a supported placement target only when its supplied
#: geometry is consistent with that area, so a "lot-fitted" candidate is never placed on geometry
#: that disagrees with the number the coverage is measured against.
_LOT_AREA_CONSISTENCY_REL_TOL = 1e-9

#: Bounded deterministic step budget for shrinking the footprint under the coverage cap at the
#: lot's real (large-magnitude) anchor, where the shoelace the checker computes is not byte-exact
#: and a single ULP step cannot overcome the rounding.
_FIT_GUARD_STEPS = 128


@dataclass(frozen=True)
class _LotRect:
    """The lot's supported axis-aligned bounding rectangle in EPSG:2263, anchored at its SW
    corner. Emitted only when :func:`_lot_rectangle` proves the supplied lot-line geometry is a
    simple axis-aligned rectangle consistent with the recorded lot area."""

    min_x: float
    min_y: float
    width: float
    depth: float

    @property
    def max_x(self) -> float:
        return self.min_x + self.width

    @property
    def max_y(self) -> float:
        return self.min_y + self.depth

    @property
    def area(self) -> float:
        return self.width * self.depth

    def as_dict(self) -> dict:
        return {
            "anchor_x": self.min_x, "anchor_y": self.min_y,
            "width_ft": self.width, "depth_ft": self.depth, "area_sq_ft": self.area,
        }


def _lot_rectangle(lot: LotContext) -> tuple[_LotRect | None, str]:
    """Derive the lot's supported axis-aligned bounding rectangle from its supplied lot-line
    segments, or return ``(None, reason)`` naming why the geometry is unsupported for candidate
    placement. Supported = every segment is a non-degenerate axis-aligned segment whose endpoints
    lie on the bounding box, each of the four bounding sides is present, and the bounding-box area
    is consistent with the recorded lot area. Anything else (absent geometry, a diagonal or
    interior vertex, a missing side, an area mismatch) is an honest, typed gap - NEVER coerced
    into a fixed-anchor schematic."""
    segments = lot.lot_line_segments
    if not segments:
        return None, (
            "no lot-line geometry was supplied, so the footprint cannot be fitted to the lot; "
            "no candidate is emitted (never a fixed-anchor schematic)"
        )
    xs: list[float] = []
    ys: list[float] = []
    for seg in segments:
        for px, py in (seg.start, seg.end):
            if not _is_finite_number(px) or not _is_finite_number(py):
                return None, (
                    "a lot-line coordinate is non-finite; the lot geometry is unusable for "
                    "candidate placement"
                )
            xs.append(float(px))
            ys.append(float(py))
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width, depth = max_x - min_x, max_y - min_y
    if not (width > 0.0 and depth > 0.0):
        return None, (
            "the lot-line geometry has zero width or depth (a degenerate bounding box); "
            "unsupported for candidate placement"
        )
    left = right = bottom = top = False
    for seg in segments:
        sx, sy = float(seg.start[0]), float(seg.start[1])
        ex, ey = float(seg.end[0]), float(seg.end[1])
        horizontal, vertical = (sy == ey), (sx == ex)
        if horizontal == vertical:  # neither (a diagonal) or both (a zero-length segment)
            return None, (
                "the lot-line geometry is not an axis-aligned rectangle (a diagonal or "
                "zero-length segment); unsupported for candidate placement in slice 1"
            )
        for px, py in ((sx, sy), (ex, ey)):
            if not (px == min_x or px == max_x or py == min_y or py == max_y):
                return None, (
                    "the lot-line geometry is not a simple axis-aligned rectangle (a vertex "
                    "lies inside its bounding box); unsupported for candidate placement"
                )
        left = left or (sx == min_x and ex == min_x)
        right = right or (sx == max_x and ex == max_x)
        bottom = bottom or (sy == min_y and ey == min_y)
        top = top or (sy == max_y and ey == max_y)
    if not (left and right and bottom and top):
        return None, (
            "the lot-line geometry does not enclose an axis-aligned rectangle (a bounding side "
            "is missing); unsupported for candidate placement in slice 1"
        )
    lot_area = float(lot.area_sq_ft)
    if not math.isclose(width * depth, lot_area, rel_tol=_LOT_AREA_CONSISTENCY_REL_TOL):
        return None, (
            f"the lot-line bounding rectangle area ({width * depth}) is not consistent with the "
            f"recorded lot area ({lot_area}); the supplied geometry and the coverage denominator "
            "disagree, so no lot-fitted candidate is emitted"
        )
    return _LotRect(min_x=min_x, min_y=min_y, width=width, depth=depth), (
        "supported axis-aligned rectangular lot"
    )


def _footprint_area(coverage_ratio: float, lot_area: float) -> float:
    """The footprint area that saturates the coverage ratio, GUARANTEED not to exceed it the
    way the checker computes coverage (``area / lot_area <= coverage_ratio``). If float rounding
    of ``coverage_ratio * lot_area`` lands a hair over, step down by ULPs (bounded) so the
    calibrated target can never be the maximum the checker refuses."""
    area = coverage_ratio * lot_area
    guard = 0
    while area > 0.0 and (area / lot_area) > coverage_ratio and guard < 8:
        area = math.nextafter(area, 0.0)
        guard += 1
    return area


def _rect_ring(min_x: float, min_y: float, width: float, depth: float) -> list[list[float]]:
    """The closed EPSG:2263 ring of the axis-aligned rectangle anchored at the lot's SW corner
    ``(min_x, min_y)``, counter-clockwise, with the closing vertex repeated (the accepted B0
    outline shape)."""
    x1, y1 = min_x + width, min_y + depth
    return [[min_x, min_y], [x1, min_y], [x1, y1], [min_x, y1], [min_x, min_y]]


def _shoelace_area(closed_ring: list[list[float]]) -> float:
    """Unsigned polygon area of a CLOSED ring by the shoelace formula - the IDENTICAL operation
    (and float order) :func:`app.scenario.derivation._shoelace_area` performs, so the coverage
    this module computes to size the footprint is byte-equal to the coverage the accepted checker
    will compute on the SAME outline (the generator-checker-consistency invariant at the lot's
    real anchor)."""
    total = 0.0
    for i in range(len(closed_ring) - 1):
        x1, y1 = closed_ring[i]
        x2, y2 = closed_ring[i + 1]
        total += x1 * y2 - x2 * y1
    return abs(total) / 2.0


def _rect_coverage(
    min_x: float, min_y: float, width: float, depth: float, lot_area: float
) -> float:
    """The coverage ratio the checker will compute for the rectangle footprint at the lot's real
    anchor: its shoelace area over the AUTHORITATIVE lot area."""
    return _shoelace_area(_rect_ring(min_x, min_y, width, depth)) / lot_area


def _shrink_depth_to_cap(
    min_x: float, min_y: float, width: float, depth: float,
    coverage_value: float, lot_area: float,
) -> float | None:
    """Shrink ONLY the depth (never the width, so lot containment is preserved) until the coverage
    the checker will compute on the footprint at the lot's real anchor is at or under the cap. At
    the lot's large-magnitude coordinates the shoelace is not byte-exact, so a proportional
    correction is applied per bounded step (a 1-ULP nudge guarantees strict progress). Returns the
    fitted depth, or ``None`` if it cannot be brought under the cap within the step budget."""
    guard = 0
    while guard < _FIT_GUARD_STEPS:
        cov = _rect_coverage(min_x, min_y, width, depth, lot_area)
        if cov <= coverage_value:
            return depth
        new_depth = depth * (coverage_value / cov)  # coverage_value / cov is strictly < 1 here
        if not (0.0 < new_depth < depth):
            new_depth = math.nextafter(depth, 0.0)
        depth = new_depth
        guard += 1
    return None


def _height_levels(height: float) -> list[dict]:
    """Level records whose derived cumulative height (``floor_to_floor_ft * floor_count``)
    saturates ``height`` without exceeding it. One floor when the height fits a single
    floor-to-floor ceiling (exact); otherwise the fewest equal floors that keep each
    floor-to-floor within the accepted bound, stepped down by ULPs if rounding lands over."""
    if height <= MAX_FLOOR_TO_FLOOR_FT:
        return [{"level_index": 0, "floor_count": 1, "floor_to_floor_ft": height}]
    n = math.ceil(height / MAX_FLOOR_TO_FLOOR_FT)
    ftf = height / n
    guard = 0
    while ftf * n > height and guard < 8:
        ftf = math.nextafter(ftf, 0.0)
        guard += 1
    return [{"level_index": 0, "floor_count": n, "floor_to_floor_ft": ftf}]


def _build_candidate(
    coverage_value: float | None, height_value: float | None, lot: LotContext
) -> tuple[dict | None, CandidatePlacement]:
    """Build a rectangle-prism candidate FITTED to the lot's actual 2263 geometry - scaled to the
    lot's own proportions, anchored at the lot's real SW corner, and PROVEN contained within it -
    or return ``(None, placement)`` with a typed :class:`CandidatePlacement` naming exactly why
    none was emitted. The emitted block is re-validated with the accepted B0 validator, and
    containment is re-proven, as defense in depth."""
    if (coverage_value is None or coverage_value <= 0.0
            or height_value is None or height_value <= 0.0):
        return None, CandidatePlacement(
            status=CandidatePlacementStatus.NO_SATURATING_BINDING,
            detail=(
                "no candidate: the maximum lot coverage ratio and/or the maximum building "
                "height is an honest gap (or non-positive), so no rules-derived footprint / "
                "prism can be sized to place"
            ),
        )
    lot_area = float(lot.area_sq_ft)  # validated finite-positive by derive_max_envelope

    rect, geo_detail = _lot_rectangle(lot)
    if rect is None:
        return None, CandidatePlacement(
            status=CandidatePlacementStatus.LOT_GEOMETRY_UNSUPPORTED, detail=geo_detail
        )
    if not (NYC_2263_X_MIN <= rect.min_x and rect.max_x <= NYC_2263_X_MAX
            and NYC_2263_Y_MIN <= rect.min_y and rect.max_y <= NYC_2263_Y_MAX):
        return None, CandidatePlacement(
            status=CandidatePlacementStatus.LOT_GEOMETRY_UNSUPPORTED,
            detail=(
                "the lot bounding rectangle is outside the accepted EPSG:2263 NYC bounds (a "
                "wrong-unit / wrong-CRS lot); no candidate is emitted"
            ),
            lot_rectangle=rect.as_dict(),
        )

    cap_area = _footprint_area(coverage_value, lot_area)
    if cap_area <= 0.0:  # pragma: no cover - coverage_value > 0 guaranteed above
        return None, CandidatePlacement(
            status=CandidatePlacementStatus.NO_SATURATING_BINDING,
            detail="no candidate: the calibrated footprint area is not positive",
            lot_rectangle=rect.as_dict(),
        )
    if cap_area > rect.area:
        return None, CandidatePlacement(
            status=CandidatePlacementStatus.FOOTPRINT_EXCEEDS_LOT,
            detail=(
                f"the rules-derived footprint area ({cap_area} sq ft, from the binding coverage "
                f"ratio) exceeds what the lot's own geometry can hold ({rect.area} sq ft); the "
                "binding values stand but no contained candidate is emitted"
            ),
            lot_rectangle=rect.as_dict(),
        )

    # Scale the lot rectangle to the calibrated footprint area, PRESERVING the lot's proportions
    # (so a translated or differently-proportioned lot yields a footprint fitted to IT), then
    # shrink only the depth so the checker-computed coverage never exceeds the cap at the real
    # anchor. scale <= 1 (cap_area <= rect.area), so the width never exceeds the lot's width.
    scale = math.sqrt(cap_area / rect.area)
    width = rect.width * scale
    depth = _shrink_depth_to_cap(
        rect.min_x, rect.min_y, width, rect.depth * scale, coverage_value, lot_area
    )
    if depth is None or not (width > 0.0 and depth > 0.0):
        return None, CandidatePlacement(
            status=CandidatePlacementStatus.CONSTRUCTION_INVALID,
            detail=(
                "no candidate: the footprint could not be fitted under the coverage cap at the "
                "lot's anchor within the deterministic step budget"
            ),
            lot_rectangle=rect.as_dict(),
        )

    ring = _rect_ring(rect.min_x, rect.min_y, width, depth)
    block = {
        "outline": {"srid": 2263, "vertices": ring},
        "levels": _height_levels(height_value),
        "exterior_walls": [
            {"id": "W-S", "start_vertex_index": 0, "end_vertex_index": 1},
            {"id": "W-E", "start_vertex_index": 1, "end_vertex_index": 2},
            {"id": "W-N", "start_vertex_index": 2, "end_vertex_index": 3},
            {"id": "W-W", "start_vertex_index": 3, "end_vertex_index": 0},
        ],
        "provenance": {
            "author": "max-envelope-generator",
            "editor_version": "m5-t064-slice1",
            "kind": "proposed",
        },
    }
    try:  # defense in depth: an emitted candidate is always a valid B0 block
        validate_proposed_massing(block)
    except ProposedMassingError as exc:  # pragma: no cover - construction guarantees validity
        return None, CandidatePlacement(
            status=CandidatePlacementStatus.CONSTRUCTION_INVALID,
            detail=f"no candidate: the constructed block failed B0 validation ({exc})",
            lot_rectangle=rect.as_dict(),
        )
    # Containment proof (belt-and-suspenders; the SW corner IS the lot's, and width/depth never
    # exceed the lot's, so this holds by construction).
    fx1, fy1 = rect.min_x + width, rect.min_y + depth
    contained = fx1 <= rect.max_x and fy1 <= rect.max_y
    if not contained:  # pragma: no cover - construction guarantees containment
        return None, CandidatePlacement(
            status=CandidatePlacementStatus.CONSTRUCTION_INVALID,
            detail="no candidate: the constructed footprint is not contained within the lot",
            lot_rectangle=rect.as_dict(),
        )
    placement = CandidatePlacement(
        status=CandidatePlacementStatus.FITTED,
        detail=(
            f"rectangle-prism footprint {width} x {depth} ft anchored at the lot's SW corner "
            f"({rect.min_x}, {rect.min_y}), scaled to the lot's proportions, saturating the "
            "coverage ratio and PROVEN contained within the lot; the height is saturated by the "
            "level records. A rules-derived estimate placement, not a surveyed siting."
        ),
        lot_rectangle=rect.as_dict(),
        footprint={
            "anchor_x": rect.min_x, "anchor_y": rect.min_y,
            "width_ft": width, "depth_ft": depth, "area_sq_ft": width * depth,
        },
        contained=True,
    )
    return block, placement


def _verify_consistency(
    candidate: dict, lot: LotContext, lot_rule_facts: Mapping[str, object],
    registry, *, label: str,
) -> dict:
    """Run the accepted checker on the candidate and confirm no SATURATING dimension FAILs.
    A FAIL is a generator-checker inconsistency - the defining failure of this slice - and fails
    closed with a typed :class:`MaxEnvelopeError`. A COULD_NOT_CHECK (e.g. the checker refuses to
    pick among competing rules) is tolerated: the candidate still satisfies the tightest rule.
    Returns a compact consistency record for the response."""
    report = check_proposal(
        candidate, lot, lot_rule_facts, scenario_label=label, registry=registry
    )
    by_id = {r.check_id: r for r in report.results}
    saturating: dict[str, str] = {}
    for dimension_id, check_id in _SATURATING_CHECK_IDS.items():
        result = by_id.get(check_id)
        if result is None:
            continue
        saturating[check_id] = result.outcome.value
        if result.outcome is CheckOutcome.FAIL:
            raise MaxEnvelopeError(
                f"generator-checker inconsistency: the candidate FAILs the {check_id!r} check "
                f"for dimension {dimension_id!r} (provided {result.provided_value} vs allowance "
                f"{result.required_value}); a maximum the checker refuses is never emitted",
                field=f"candidate.{dimension_id}",
            )
    return {
        "scenario_label": label,
        "summary": report.as_dict()["summary"],
        "saturating_checks": saturating,
    }


# ---------------------------------------------------------------------------
# Public entry point.
# ---------------------------------------------------------------------------


def derive_max_envelope(
    lot: LotContext,
    lot_rule_facts: Mapping[str, object] | None = None,
    *,
    registry,
    label: str | None = None,
) -> MaxEnvelope:
    """Derive the deterministic maximum-buildable envelope for the rectangle-prism massing class.

    ``lot`` the caller-supplied :class:`LotContext` (only ``area_sq_ft`` is consumed here; the
    coverage denominator); ``lot_rule_facts`` the caller-supplied lot rule inputs
    (``street_width_class`` is the wide-street OUTPUT shape consumed read-only). ``registry`` the
    rule registry to evaluate against (injected; tests supply a fixture registry). ``label`` an
    optional label echoed on the envelope and used as the candidate's ``scenario_label`` during
    the consistency proof.

    Returns a :class:`MaxEnvelope` enumerating EVERY declared dimension (each a binding value +
    provenance or a typed honest gap), a candidate ``proposed_massing`` draft saturating the
    computable binding values and FITTED to the lot's actual 2263 geometry (or ``None`` with a
    typed :class:`CandidatePlacement` naming why none was placed), and the generator-checker
    consistency record. Raises :class:`MaxEnvelopeError` on a precondition failure or a
    generator-checker inconsistency."""
    if not isinstance(lot, LotContext):
        raise MaxEnvelopeError("lot must be a LotContext instance", field="lot")
    if not _is_finite_number(lot.area_sq_ft) or float(lot.area_sq_ft) <= 0.0:
        raise MaxEnvelopeError(
            f"lot.area_sq_ft must be a finite positive number; got {lot.area_sq_ft!r}",
            field="lot.area_sq_ft",
        )
    facts: Mapping[str, object] = lot_rule_facts if lot_rule_facts is not None else {}

    inputs, bindings, unmapped = _build_rule_inputs(lot, facts)
    dimensions = tuple(
        _resolve_dimension(spec, registry, inputs) for spec in ENVELOPE_DIMENSIONS
    )

    by_dim = {d.dimension_id: d for d in dimensions}
    coverage = by_dim["max_lot_coverage_ratio"].binding_value
    height = by_dim["max_building_height"].binding_value
    candidate, placement = _build_candidate(coverage, height, lot)

    consistency: dict | None = None
    if candidate is not None:
        consistency = _verify_consistency(
            candidate, lot, facts, registry,
            label=label or "max-envelope-candidate",
        )

    binding_count = sum(d.binding_value is not None for d in dimensions)
    gap_count = sum(d.gap_reason is not None for d in dimensions)
    saturating_binding = sum(
        d.binding_value is not None and d.saturating for d in dimensions
    )
    return MaxEnvelope(
        massing_class=MASSING_CLASS, label=label, disclosure=ENVELOPE_DISCLOSURE,
        dimensions=dimensions, candidate=candidate, candidate_notes=(placement.detail,),
        candidate_placement=placement, candidate_consistency=consistency,
        binding_count=binding_count, gap_count=gap_count,
        saturating_binding_count=saturating_binding, rule_input_bindings=bindings,
        unmapped_lot_facts=unmapped,
    )
