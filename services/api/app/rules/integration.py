"""Property-analysis <-> rules-engine integration (M4-T002, service layer).

Bridges the accepted M2-T012 canonical property profile (contract 1.4.0) and the
M2-T013 spatial-intersection substrate into the M4-T001 deterministic rules
evaluator, and evaluates the draft R5 residential-FAR family. This module MAPS;
it does NOT calculate (the evaluator calculates) and it does NOT decide law.

It runs at the SERVICE layer only: no public endpoint, no UI, no contract change.
It consumes the property profile and spatial substrate as plain read-only data.

Load-bearing guarantees (owner directive 2026-07-20/21; task M4-T002 hard rules):

* READ-ONLY consumption. The property profile and spatial substrate arrive as a
  plain ``dict`` (the canonical profile the accepted builder emits). Nothing here
  mutates them, writes them back, or imports the profile builder / spatial engine
  / a canonical contract. The three spatial vocabulary constants below are
  duplicated (not imported) to avoid pulling the shapely-heavy ``app.spatial``
  package into this service path; a drift-guard test (RI-S8) asserts they stay
  identical to ``app.spatial``. This mirrors the coverage.py <-> canonical-contract
  duplication pattern already used in this engine.
* Uncertainty is preserved, never collapsed. The M2-T013 split-share RANGES,
  typed ZTLDB conflicts, and professional-review flags flow into the result
  untouched (``spatial_uncertainty``). An uncertain lot is NEVER turned into a
  definitive single district: a base-zoning district is derived ONLY from a lot
  the spatial engine already classified ``single_district_confident`` with a
  single ``interior_confident`` base pair.
* FAIL SAFE. When the spatial substrate is absent, its class is not
  ``single_district_confident``, or it routes to professional review, the result
  is ``professional_review_required`` (``data_conflict`` for a ZTLDB set-conflict)
  with NO guessed district and NO computed value.
* Provenance fail-closed. Evaluator traces are taken through
  ``RuleResult.export()``, which refuses to emit a material value whose citation
  lacks resolvable source provenance (PRD section 19).
* Draft is never Verified. Nothing here emits or up-labels a ``verified`` coverage
  status; a draft rule tops out at ``conditional``. Every result carries its
  coverage status, the evaluated rule's ``needs_review`` lifecycle state, and an
  explicit not-Verified disclaimer, and :func:`assert_not_verified` fail-closes if
  a ``verified`` status ever appears anywhere in the payload - so a downstream
  caller (scenario generator, UI, report) can never read a draft as final.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import coverage as cov
from . import lifecycle
from .registry import RuleRegistry

# ---------------------------------------------------------------------------
# Spatial vocabulary (DUPLICATED from app.spatial, guarded by a drift test).
#
# Importing app.spatial.models / app.spatial.policy would execute
# app.spatial.__init__, which eagerly imports the shapely-dependent engine and
# adapter - an unnecessary heavy dependency for this pure data mapping. The four
# values below are copied verbatim from their sources; RI-S8's drift guard
# imports the real constants and asserts equality so a rename can never diverge
# silently (the same technique coverage.py uses against the canonical contract).
# ---------------------------------------------------------------------------
_BASE_ZONING_FAMILY = "base_zoning"  # app.spatial.policy.LAYER_FAMILY["nyzd"]
_LOT_SINGLE_DISTRICT_CONFIDENT = "single_district_confident"  # models.LOT_SINGLE_DISTRICT_CONFIDENT
_LOT_DATA_CONFLICT = "data_conflict"  # models.LOT_DATA_CONFLICT
_PAIR_INTERIOR_CONFIDENT = "interior_confident"  # models.PAIR_INTERIOR_CONFIDENT

# The draft family this slice wires in (the R5 rule's ``family`` field). Adding
# another residential-FAR district rule to the registry needs no change here.
TARGET_FAMILY = "residential_far"

# The permanent honest disclaimer stamped on every integration result. Draft rule
# output is a candidate representation, never a Verified legal determination.
NOT_VERIFIED_DISCLAIMER = (
    "DRAFT - not a Verified determination. This result is produced by a "
    "needs_review draft rule pending raw-HTML source verification and G6 "
    "qualified-human legal approval (PRD sections 10-12). It must never be "
    "presented, stored, or consumed as Verified; coverage tops out at conditional."
)

# Typed fail-safe discriminators (machine-readable; finer than coverage_status).
FAILSAFE_SPATIAL_ABSENT = "spatial_intersection_absent"
FAILSAFE_SPATIAL_INCOMPLETE = "spatial_context_incomplete"
FAILSAFE_DATA_CONFLICT = "data_conflict"
FAILSAFE_GEOMETRY_UNCERTAIN = "geometry_uncertain"
FAILSAFE_INCONSISTENT_CONFIDENT = "inconsistent_confident_geometry"

_COVERAGE_SOURCE_EVALUATOR = "rule_evaluator"
_COVERAGE_SOURCE_FAIL_SAFE = "integration_fail_safe"


class DraftVerifiedError(RuntimeError):
    """Raised when an integration payload would carry a ``verified`` coverage
    status. A draft-rule integration can never be Verified; this fail-closes so
    the mistake surfaces here rather than downstream (RI-S7)."""


@dataclass(frozen=True)
class PropertyRuleEvaluation:
    """Result of mapping one property profile into the rules evaluator.

    ``coverage_status`` is one of the six canonical statuses and is NEVER
    ``verified``. ``evaluations`` holds the deterministic evaluator traces
    (already ``export()``-ed, so provenance is resolved) and is empty on a
    fail-safe short-circuit. ``spatial_uncertainty`` preserves the M2-T013 facts
    verbatim (share ranges, conflicts, review flags), never collapsed.
    """

    bbl: str | None
    coverage_status: str
    data_completeness: str | None
    needs_review: bool
    professional_review_required: bool
    fail_safe: bool
    fail_safe_reason: str | None
    rule_lifecycle_statuses: list
    not_verified_disclaimer: str
    zoning_district: str | None
    lot_area_sq_ft: float | None
    lot_area_source: str | None
    spatial_context: dict | None
    spatial_uncertainty: dict
    input_provenance: dict
    evaluations: list
    family_coverage: dict
    reasons: list
    coverage_source: str = _COVERAGE_SOURCE_EVALUATOR
    verified_status_present: bool = False

    def as_dict(self) -> dict:
        return {
            "bbl": self.bbl,
            "coverage_status": self.coverage_status,
            "data_completeness": self.data_completeness,
            "needs_review": self.needs_review,
            "professional_review_required": self.professional_review_required,
            "fail_safe": self.fail_safe,
            "fail_safe_reason": self.fail_safe_reason,
            "rule_lifecycle_statuses": list(self.rule_lifecycle_statuses),
            "not_verified_disclaimer": self.not_verified_disclaimer,
            "zoning_district": self.zoning_district,
            "lot_area_sq_ft": self.lot_area_sq_ft,
            "lot_area_source": self.lot_area_source,
            "spatial_context": (
                dict(self.spatial_context) if self.spatial_context is not None else None
            ),
            "spatial_uncertainty": dict(self.spatial_uncertainty),
            "input_provenance": dict(self.input_provenance),
            "evaluations": list(self.evaluations),
            "family_coverage": dict(self.family_coverage),
            "reasons": list(self.reasons),
            "coverage_source": self.coverage_source,
            "verified_status_present": self.verified_status_present,
        }

    def export(self) -> dict:
        """Serialize for a downstream consumer, fail-closed: raises
        :class:`DraftVerifiedError` if any ``verified`` status ever slipped in."""
        payload = self.as_dict()
        assert_not_verified(payload)
        return payload


# ---------------------------------------------------------------------------
# Downstream-safety guard (RI-S7): a draft integration is never Verified.
# ---------------------------------------------------------------------------

def assert_not_verified(payload: PropertyRuleEvaluation | dict) -> None:
    """Fail closed if a ``verified`` coverage status appears anywhere in the
    payload - the top-level status, any evaluator trace, or the family-coverage
    block. Downstream callers can call this on data they received to refuse a
    draft masquerading as Verified. Only ``coverage_status`` FIELDS are checked;
    the disclaimer TEXT (which contains the word "Verified") is never a status."""
    data = payload.as_dict() if isinstance(payload, PropertyRuleEvaluation) else payload
    verified = cov.COVERAGE_VERIFIED
    if data.get("coverage_status") == verified:
        raise DraftVerifiedError(
            "integration coverage_status is 'verified'; a draft-rule result may "
            "never be Verified (G6 qualified-human approval is required first)."
        )
    for trace in data.get("evaluations") or []:
        if isinstance(trace, dict) and trace.get("coverage_status") == verified:
            raise DraftVerifiedError(
                f"evaluator trace for rule {trace.get('rule_id')!r} carries "
                "'verified'; a draft rule may never be Verified."
            )
    family_coverage = data.get("family_coverage") or {}
    if isinstance(family_coverage, dict) and family_coverage.get("coverage_status") == verified:
        raise DraftVerifiedError("family_coverage is 'verified'; unreachable for a draft family.")


# ---------------------------------------------------------------------------
# Read-only extraction helpers.
# ---------------------------------------------------------------------------

def _positive_number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool) and value > 0


def _base_pairs(spatial: dict) -> list:
    return [
        pair
        for pair in (spatial.get("pairs") or [])
        if isinstance(pair, dict) and pair.get("family") == _BASE_ZONING_FAMILY
    ]


def _preserve_uncertainty(spatial: dict) -> dict:
    """Surface the M2-T013 facts-with-uncertainty verbatim - share RANGES, typed
    conflicts, and review flags - never collapsed into a single assignment."""
    candidates = [
        {
            "district_label": pair.get("district_label"),
            "pair_class": pair.get("pair_class"),
            "share_min": pair.get("share_min"),
            "share_point": pair.get("share_point"),
            "share_max": pair.get("share_max"),
            "minor_portion": pair.get("minor_portion"),
        }
        for pair in _base_pairs(spatial)
    ]
    return {
        "lot_overall_class": spatial.get("lot_overall_class"),
        "professional_review_required": bool(spatial.get("professional_review_required", False)),
        "coverage_note": spatial.get("coverage_note"),
        "review_reasons": list(spatial.get("review_reasons") or []),
        "notes": list(spatial.get("notes") or []),
        "base_district_candidates": candidates,
        "crosscheck": spatial.get("crosscheck"),
    }


def _empty_uncertainty() -> dict:
    return {
        "lot_overall_class": None,
        "professional_review_required": False,
        "coverage_note": None,
        "review_reasons": [],
        "notes": [],
        "base_district_candidates": [],
        "crosscheck": None,
    }


def _confident_base_district(spatial: dict) -> str | None:
    """The single confidently-assigned base-zoning district, or None.

    The spatial engine emits ``single_district_confident`` iff there is exactly
    one ``interior_confident`` base-zoning pair and no other firm/uncertain base
    pair (engine.py). We re-derive that single label WITHOUT collapsing anything:
    if the invariant does not hold we return None and the caller fails safe."""
    interior = [p for p in _base_pairs(spatial) if p.get("pair_class") == _PAIR_INTERIOR_CONFIDENT]
    if len(interior) != 1:
        return None
    label = interior[0].get("district_label")
    return label if isinstance(label, str) and label.strip() else None


def _lot_area(profile: dict, spatial: dict) -> tuple[float | None, str | None]:
    """Zoning-lot area input, preferring the validated MapPLUTO geometry area.

    Precedence: the canonical ``lot_geometry.area_sq_ft`` (M2-T009, computed only
    in the validated EPSG:2263 projected CRS); else the same MapPLUTO geometry
    area carried on the confident base pair. Absent/non-positive -> None, and the
    evaluator then yields a typed missing-critical result with no computed value.
    NOTE (documented limitation): a zoning lot may differ from the tax-lot
    geometry; this is a draft-rule input and never a Verified boundary."""
    geometry = profile.get("lot_geometry")
    if isinstance(geometry, dict) and _positive_number(geometry.get("area_sq_ft")):
        return float(geometry["area_sq_ft"]), "lot_geometry.area_sq_ft"
    for pair in _base_pairs(spatial):
        if pair.get("pair_class") == _PAIR_INTERIOR_CONFIDENT and _positive_number(
            pair.get("lot_area_sq_ft")
        ):
            return float(pair["lot_area_sq_ft"]), "spatial_intersection.pairs[].lot_area_sq_ft"
    return None, None


def _input_provenance(profile: dict, spatial: dict, area_source: str | None) -> dict:
    """Which profile provenance records back each derived evaluator input, so a
    downstream reader can trace inputs (the OUTPUT provenance is the rule's own
    citations, enforced fail-closed by RuleResult.export())."""
    spatial_refs = [ref for ref in (spatial.get("provenance_refs") or []) if isinstance(ref, str)]
    provenance = {"zoning_district": list(spatial_refs), "lot_area_sq_ft": []}
    geometry = profile.get("lot_geometry")
    if area_source == "lot_geometry.area_sq_ft" and isinstance(geometry, dict):
        ref = geometry.get("provenance_ref")
        provenance["lot_area_sq_ft"] = [ref] if isinstance(ref, str) and ref else []
    elif area_source and area_source.startswith("spatial_intersection"):
        provenance["lot_area_sq_ft"] = list(spatial_refs)
    return provenance


def _completeness_from(evaluations: list) -> str | None:
    """Most-severe data-completeness across the evaluated traces (or None)."""
    severity = {
        cov.COMPLETENESS_COMPLETE: 0,
        cov.COMPLETENESS_MISSING_NONCRITICAL: 1,
        cov.COMPLETENESS_MISSING_CRITICAL: 2,
    }
    seen = [
        trace.get("data_completeness")
        for trace in evaluations
        if isinstance(trace, dict) and trace.get("data_completeness") in severity
    ]
    if not seen:
        return None
    return max(seen, key=lambda status: severity[status])


# ---------------------------------------------------------------------------
# Registry (lazy, immutable) - callers may inject their own for tests.
# ---------------------------------------------------------------------------

_REGISTRY: RuleRegistry | None = None


def _default_registry() -> RuleRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = RuleRegistry().load()
    return _REGISTRY


def _fail_safe(
    *,
    bbl: str | None,
    coverage_status: str,
    fail_safe_reason: str,
    reason: str,
    spatial_context: dict | None,
    spatial_uncertainty: dict,
    family_coverage: dict,
) -> PropertyRuleEvaluation:
    """Build a fail-safe result: professional review (or data conflict) with NO
    guessed district and NO computed value; uncertainty preserved."""
    return PropertyRuleEvaluation(
        bbl=bbl,
        coverage_status=coverage_status,
        data_completeness=None,
        needs_review=True,
        professional_review_required=True,
        fail_safe=True,
        fail_safe_reason=fail_safe_reason,
        rule_lifecycle_statuses=[],
        not_verified_disclaimer=NOT_VERIFIED_DISCLAIMER,
        zoning_district=None,
        lot_area_sq_ft=None,
        lot_area_source=None,
        spatial_context=spatial_context,
        spatial_uncertainty=spatial_uncertainty,
        input_provenance={"zoning_district": [], "lot_area_sq_ft": []},
        evaluations=[],
        family_coverage=family_coverage,
        reasons=[reason],
        coverage_source=_COVERAGE_SOURCE_FAIL_SAFE,
    )


# ---------------------------------------------------------------------------
# Public entry point.
# ---------------------------------------------------------------------------

def evaluate_property(
    profile: dict,
    *,
    registry: RuleRegistry | None = None,
) -> PropertyRuleEvaluation:
    """Map a canonical property profile into the rules evaluator and evaluate the
    draft R5 residential-FAR family. Pure and deterministic: the same profile
    yields a byte-identical result. Consumes ``profile`` strictly read-only.

    The profile is the contract-1.4.0 dict the accepted M2-T012 builder emits; the
    keys read are ``identity.bbl``, ``spatial_intersection`` (the M2-T013
    substrate), and ``lot_geometry.area_sq_ft``. Nothing is written back.
    """
    registry = registry or _default_registry()
    family_coverage = registry.family_coverage(TARGET_FAMILY)
    identity = profile.get("identity")
    bbl = identity.get("bbl") if isinstance(identity, dict) else None

    spatial = profile.get("spatial_intersection")
    if not isinstance(spatial, dict):
        # RI-S3: no spatial substrate -> no lot-level district is known. Never
        # guess one from PLUTO zonedist; fail safe with no value.
        return _fail_safe(
            bbl=bbl,
            coverage_status=cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
            fail_safe_reason=FAILSAFE_SPATIAL_ABSENT,
            reason=(
                "property profile carries no spatial_intersection section; the "
                "lot-level zoning-district assignment is unknown and must not be "
                "guessed - professional review required"
            ),
            spatial_context=None,
            spatial_uncertainty=_empty_uncertainty(),
            family_coverage=family_coverage,
        )

    lot_overall_class = spatial.get("lot_overall_class")
    professional_review_required = bool(spatial.get("professional_review_required", False))
    spatial_context = {
        "lot_overall_class": lot_overall_class,
        "professional_review_required": professional_review_required,
        "coverage_note": spatial.get("coverage_note"),
    }
    spatial_uncertainty = _preserve_uncertainty(spatial)

    if not isinstance(lot_overall_class, str) or not lot_overall_class:
        # RI-S3: spatial section present but the required class is missing -> the
        # spatial_context is incomplete; fail safe.
        return _fail_safe(
            bbl=bbl,
            coverage_status=cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
            fail_safe_reason=FAILSAFE_SPATIAL_INCOMPLETE,
            reason=(
                "spatial_intersection is present but lot_overall_class is missing; "
                "the spatial context is incomplete - professional review required"
            ),
            spatial_context=spatial_context,
            spatial_uncertainty=spatial_uncertainty,
            family_coverage=family_coverage,
        )

    if lot_overall_class == _LOT_DATA_CONFLICT:
        # RI-S2: a ZTLDB set-conflict is a typed data conflict; surface it, never
        # pick a winner.
        return _fail_safe(
            bbl=bbl,
            coverage_status=cov.COVERAGE_DATA_CONFLICT,
            fail_safe_reason=FAILSAFE_DATA_CONFLICT,
            reason=(
                "spatial_intersection lot_overall_class=data_conflict (e.g. a ZTLDB "
                "set-conflict); the conflict is preserved and no definitive district "
                "or value is produced"
            ),
            spatial_context=spatial_context,
            spatial_uncertainty=spatial_uncertainty,
            family_coverage=family_coverage,
        )

    if lot_overall_class != _LOT_SINGLE_DISTRICT_CONFIDENT or professional_review_required:
        # RI-S2: any positional uncertainty (boundary_uncertain / split_lot /
        # sliver_ambiguous / invalid_geometry_review) or a professional-review
        # rollup -> fail safe. Share ranges and review flags are preserved and
        # never collapsed into a definitive district.
        return _fail_safe(
            bbl=bbl,
            coverage_status=cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
            fail_safe_reason=FAILSAFE_GEOMETRY_UNCERTAIN,
            reason=(
                f"spatial_intersection lot_overall_class={lot_overall_class!r}, "
                f"professional_review_required={professional_review_required}; the "
                "lot-level district is not confidently assignable - uncertainty "
                "preserved, never collapsed; professional review required"
            ),
            spatial_context=spatial_context,
            spatial_uncertainty=spatial_uncertainty,
            family_coverage=family_coverage,
        )

    # --- Confident path: exactly one interior_confident base-zoning district. ---
    district = _confident_base_district(spatial)
    if district is None:
        # Defensive: the engine's single_district_confident invariant did not
        # hold in the data we were handed. Never guess - fail safe.
        return _fail_safe(
            bbl=bbl,
            coverage_status=cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED,
            fail_safe_reason=FAILSAFE_INCONSISTENT_CONFIDENT,
            reason=(
                "lot_overall_class=single_district_confident but the base-zoning "
                "pairs do not contain exactly one interior_confident district; the "
                "record is internally inconsistent - professional review required"
            ),
            spatial_context=spatial_context,
            spatial_uncertainty=spatial_uncertainty,
            family_coverage=family_coverage,
        )

    lot_area_sq_ft, lot_area_source = _lot_area(profile, spatial)
    # site_class is deliberately NOT derived: whether a lot is a "qualifying
    # residential site" is a separate legal determination the rule defers. Leaving
    # it absent makes the rule surface the higher-FAR alternative as conditional.
    inputs = {"zoning_district": district, "lot_area_sq_ft": lot_area_sq_ft}

    evaluations: list = []
    applicable_coverages: list = []
    statuses: set = set()
    reasons: list = []
    for rule_id in family_coverage.get("rule_ids", []):
        result = registry.evaluate(rule_id, inputs, spatial_context=spatial_context)
        trace = result.export()  # provenance fail-closed (PRD section 19)
        evaluations.append(trace)
        statuses.add(trace["rule_status"])
        if trace["applicability_outcome"]:
            applicable_coverages.append(trace["coverage_status"])

    if applicable_coverages:
        coverage_status = cov.most_severe(*applicable_coverages)
    else:
        # RI-S6: a confident district that no implemented draft rule applies to is
        # a VISIBLE not_applicable, never silence.
        coverage_status = cov.COVERAGE_NOT_APPLICABLE
        reasons.append(
            f"no implemented {TARGET_FAMILY} rule applies to district {district!r}; "
            "result is not_applicable (visible, not silent)"
        )

    needs_review = coverage_status != cov.COVERAGE_VERIFIED and (
        professional_review_required
        or any(status != lifecycle.STATUS_PUBLISHED for status in statuses)
        or coverage_status
        in (cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED, cov.COVERAGE_DATA_CONFLICT)
    )

    result = PropertyRuleEvaluation(
        bbl=bbl,
        coverage_status=coverage_status,
        data_completeness=_completeness_from(evaluations),
        needs_review=needs_review,
        professional_review_required=(
            coverage_status == cov.COVERAGE_PROFESSIONAL_REVIEW_REQUIRED
        ),
        fail_safe=False,
        fail_safe_reason=None,
        rule_lifecycle_statuses=sorted(statuses),
        not_verified_disclaimer=NOT_VERIFIED_DISCLAIMER,
        zoning_district=district,
        lot_area_sq_ft=lot_area_sq_ft,
        lot_area_source=lot_area_source,
        spatial_context=spatial_context,
        spatial_uncertainty=spatial_uncertainty,
        input_provenance=_input_provenance(profile, spatial, lot_area_source),
        evaluations=evaluations,
        family_coverage=family_coverage,
        reasons=reasons,
        coverage_source=_COVERAGE_SOURCE_EVALUATOR,
    )
    # Defensive fail-close: this function can never return a Verified draft.
    assert_not_verified(result)
    return result


__all__ = [
    "PropertyRuleEvaluation",
    "DraftVerifiedError",
    "evaluate_property",
    "assert_not_verified",
    "NOT_VERIFIED_DISCLAIMER",
    "TARGET_FAMILY",
    "FAILSAFE_SPATIAL_ABSENT",
    "FAILSAFE_SPATIAL_INCOMPLETE",
    "FAILSAFE_DATA_CONFLICT",
    "FAILSAFE_GEOMETRY_UNCERTAIN",
    "FAILSAFE_INCONSISTENT_CONFIDENT",
]
