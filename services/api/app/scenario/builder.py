"""Deterministic, coverage-aware scenario builder (task M5-T001).

``build_scenario`` consumes a ``property_profile`` (1.4.0) and a
``rule_evaluation`` (1.0.0) document READ-ONLY and returns a strict-JSON
``scenario`` document. It performs NO independent legal calculation: the only
material number it can surface is the canonical
``max_residential_floor_area_sq_ft`` output already present in a
``rule_evaluation`` trace, and it surfaces that value VERBATIM.

Hard guarantees (enforced here and by the acceptance pack in
``tests/scenario``):

* The surfaced cap is the canonical trace value, never recomputed. Any
  ``far * lot_area`` recompute is VERIFICATION-ONLY and fails closed on
  disagreement (proposal section 5 step 5) - it never replaces the value.
* No envelope constraint (height, stories, setbacks, yards, parking, lot
  coverage, efficiency, unit count, gross-to-net, constructability) is ever
  inferred; each is emitted as ``missing``.
* The cap is never relabeled as gross/net/sellable/feasible area or a buildable
  envelope; it always carries the mandatory draft label.
* No hidden utilization/optimization default: a preliminary scenario equals the
  raw draft cap; any variation is an explicit typed assumption that never
  changes the surfaced value.
* No scenario is ever Verified; every scenario carries ``needs_review`` and the
  not-Verified disclaimer.
* Fail-closed: any conflict, professional-review/spatial uncertainty, malformed
  or non-finite input, or an absent controlling input yields a typed
  ``no_scenario`` outcome with reasons - never a crash and never a guessed
  value.

The function is pure and deterministic: identical input yields byte-identical
output (constraints, reasons, and matrix all emit in a fixed order).
"""

from __future__ import annotations

import math
from typing import Any

from . import constants as C
from .models import (
    ConstraintCompleteness,
    DataCompleteness,
    ScenarioKind,
    most_severe_completeness,
)

__all__ = ["build_scenario"]


# ---------------------------------------------------------------------------
# Numeric guards (fail-closed): reject NaN / +-inf / bool / non-numeric /
# not-finite-as-float (huge int overflow). A value is usable only when it maps
# to a finite Python float.
# ---------------------------------------------------------------------------


def _finite_float(value: Any) -> float | None:
    """Return ``value`` as a finite float, or ``None`` when it is not a usable
    finite number (bool, non-numeric, NaN, +-inf, or an integer too large to be
    represented as a finite float). Never raises."""
    if isinstance(value, bool):
        return None
    if not isinstance(value, int | float):
        return None
    try:
        as_float = float(value)
    except (OverflowError, ValueError):
        return None
    if not math.isfinite(as_float):
        return None
    return as_float


def _positive_finite_float(value: Any) -> float | None:
    """Finite float strictly greater than zero, else ``None``."""
    result = _finite_float(value)
    if result is None or result <= 0.0:
        return None
    return result


def _is_present_number(value: Any) -> bool:
    """True when a value is present (not None) and numeric-shaped (so a malformed
    numeric is distinguishable from an absent one)."""
    return value is not None


# ---------------------------------------------------------------------------
# Read-only extraction helpers
# ---------------------------------------------------------------------------


def _as_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _find_residential_far_trace(rule_evaluation: dict) -> dict | None:
    """Return the first applicable residential_far evaluation trace, or None.

    Deterministic: iterates ``evaluations`` in document order and returns the
    first trace whose family is residential_far and whose applicability outcome
    is true. Never reshapes the trace."""
    for trace in rule_evaluation.get("evaluations", []) or []:
        if not isinstance(trace, dict):
            continue
        if trace.get("family") != C.RESIDENTIAL_FAR_FAMILY:
            continue
        if trace.get("applicability_outcome") is True:
            return trace
    return None


def _profile_provenance_index(property_profile: dict) -> dict[str, dict]:
    """Map provenance_id -> provenance record from the profile (read-only)."""
    index: dict[str, dict] = {}
    for record in _as_dict(property_profile).get("provenance", []) or []:
        if isinstance(record, dict) and isinstance(record.get("provenance_id"), str):
            index[record["provenance_id"]] = record
    return index


def _lot_area_provenance(
    rule_evaluation: dict, property_profile: dict, lot_area_source: Any
) -> dict | None:
    """Build lot-area provenance from the profile field + dataset (proposal
    section 4/AS-10). Resolves rule_evaluation.input_provenance.lot_area_sq_ft
    refs into the profile's provenance array to name the source + dataset."""
    refs = (
        _as_dict(_as_dict(rule_evaluation.get("evaluated_input")).get("input_provenance"))
        .get("lot_area_sq_ft")
    )
    index = _profile_provenance_index(property_profile)
    resolved: list[dict] = []
    for ref in refs or []:
        record = index.get(ref)
        if record is not None:
            resolved.append(
                {
                    "provenance_id": record.get("provenance_id"),
                    "source_id": record.get("source_id"),
                    "dataset_version": record.get("dataset_version"),
                    "original_field_name": record.get("original_field_name"),
                    "effective_date": record.get("effective_date"),
                }
            )
    return {
        "profile_field": lot_area_source if isinstance(lot_area_source, str) else None,
        "provenance_refs": list(refs) if isinstance(refs, list) else [],
        "resolved": resolved,
    }


def _cap_provenance(trace: dict) -> dict:
    """Cap provenance propagated VERBATIM from the trace (rule id/version/status
    + citations with their source-snapshot provenance). Never invented."""
    citations = []
    for citation in trace.get("citations", []) or []:
        if not isinstance(citation, dict):
            continue
        entry = {
            "snapshot_id": citation.get("snapshot_id"),
            "section": citation.get("section"),
            "quote": citation.get("quote"),
            "provenance": _as_dict(citation.get("provenance")),
        }
        if "last_amended" in citation:
            entry["last_amended"] = citation.get("last_amended")
        citations.append(entry)
    return {
        "rule_id": trace.get("rule_id"),
        "rule_version": trace.get("rule_version"),
        "rule_status": trace.get("rule_status"),
        "output_name": C.CAP_OUTPUT_NAME,
        "citations": citations,
        "note": (
            "Draft residential zoning-floor-area cap consumed verbatim from the "
            "canonical rule_evaluation trace output; not recomputed by the "
            "scenario engine."
        ),
    }


# ---------------------------------------------------------------------------
# Assumption normalization (explicit-only; never applied to the cap)
# ---------------------------------------------------------------------------


def _normalize_assumptions(assumptions: list[dict] | None) -> list[dict]:
    """Return declared assumptions as contract records, in a deterministic order
    (by key). Recorded verbatim; NEVER applied to the surfaced cap. Malformed
    entries are dropped fail-closed (an assumption that is not a well-formed
    record cannot silently take effect)."""
    if not assumptions:
        return []
    records: list[dict] = []
    for assumption in assumptions:
        if not isinstance(assumption, dict):
            continue
        key = assumption.get("key")
        if not isinstance(key, str) or not key:
            continue
        value = assumption.get("value")
        # Reject a non-finite numeric assumption value fail-closed.
        if isinstance(value, int | float) and not isinstance(value, bool):
            if _finite_float(value) is None:
                continue
        records.append(
            {
                "key": key,
                "assumption_type": str(assumption.get("assumption_type", "unspecified")),
                "value": value,
                "unit": assumption.get("unit") if isinstance(assumption.get("unit"), str) else None,
                "rationale": str(assumption.get("rationale", "")),
            }
        )
    records.sort(key=lambda record: record["key"])
    return records


# ---------------------------------------------------------------------------
# Constraint builders
# ---------------------------------------------------------------------------


def _constraint(
    key: str,
    state: ConstraintCompleteness,
    value: Any,
    unit: str | None,
    completeness: DataCompleteness,
    provenance: dict | None,
    note: str,
) -> dict:
    return {
        "key": key,
        "state": state.value,
        "value": value,
        "unit": unit,
        "data_completeness": completeness.value,
        "provenance": provenance,
        "note": note,
    }


def _missing_envelope_constraints() -> list[dict]:
    """The envelope families that have no rule today - always MISSING, never
    inferred (proposal section 5a)."""
    out: list[dict] = []
    for key, governs, blocks in C.MISSING_ENVELOPE_CONSTRAINTS:
        out.append(
            _constraint(
                key=key,
                state=ConstraintCompleteness.MISSING,
                value=None,
                unit=None,
                completeness=C.completeness_for_blocking(blocks),
                provenance=None,
                note=(
                    f"No rule family provides {governs}; recorded as a gap. "
                    "MUST NOT be inferred, defaulted, or estimated."
                ),
            )
        )
    return out


# ---------------------------------------------------------------------------
# Outcome assembly
# ---------------------------------------------------------------------------


def _evaluated_input(rule_evaluation: dict, property_profile: dict) -> dict:
    ev = _as_dict(rule_evaluation.get("evaluated_input"))
    bbl = ev.get("bbl")
    if bbl is None:
        identity = _as_dict(_as_dict(property_profile).get("identity"))
        candidate = identity.get("bbl")
        bbl = candidate if isinstance(candidate, str) else None
    return {
        "bbl": bbl if isinstance(bbl, str) else None,
        "profile_contract_version": str(ev.get("profile_contract_version") or "unknown"),
        "rule_evaluation_contract_version": str(
            rule_evaluation.get("contract_version") or "unknown"
        ),
        "input_fingerprint": (
            ev.get("input_fingerprint")
            if isinstance(ev.get("input_fingerprint"), str)
            else None
        ),
    }


def _assemble(
    *,
    scenario_kind: ScenarioKind,
    coverage_status: str,
    professional_review_required: bool,
    rule_evaluation: dict,
    property_profile: dict,
    constraints: list[dict],
    reasons: list[str],
    cap_value: float | None,
    cap_provenance: dict | None,
    assumptions: list[dict],
    integrity_check: dict,
) -> dict:
    completeness = most_severe_completeness(
        [DataCompleteness(c["data_completeness"]) for c in constraints]
    )
    document = {
        "contract_version": C.SCENARIO_CONTRACT_VERSION,
        "scenario_kind": scenario_kind.value,
        "coverage_status": coverage_status,
        "data_completeness": completeness.value,
        "needs_review": True,
        "professional_review_required": professional_review_required,
        "not_verified_disclaimer": C.NOT_VERIFIED_DISCLAIMER,
        "evaluated_input": _evaluated_input(rule_evaluation, property_profile),
        "constraints": constraints,
        "draft_zoning_floor_area_cap_sq_ft": cap_value,
        "cap_label": C.DRAFT_CAP_LABEL if cap_value is not None else None,
        "cap_provenance": cap_provenance,
        "assumptions": assumptions,
        "reasons": reasons,
        "coverage_matrix": C.coverage_matrix_rows(),
        "integrity_check": integrity_check,
    }
    return document


def _integrity_not_performed(note: str) -> dict:
    return {
        "performed": False,
        "agreed": None,
        "tolerance": C.INTEGRITY_TOLERANCE,
        "method": C.INTEGRITY_METHOD,
        "note": note,
    }


def build_scenario(
    property_profile: dict,
    rule_evaluation: dict,
    *,
    assumptions: list[dict] | None = None,
) -> dict:
    """Build a deterministic scenario document from a profile + rule evaluation.

    ``property_profile`` and ``rule_evaluation`` are consumed READ-ONLY (never
    mutated). ``assumptions`` is an optional list of explicit typed assumptions;
    it defaults to none and NEVER changes the surfaced cap value.

    Returns a strict-JSON ``scenario`` document (validate it with
    :func:`app.scenario.contract.validate_scenario_document`).
    """
    property_profile = _as_dict(property_profile)
    rule_evaluation = _as_dict(rule_evaluation)
    assumption_records = _normalize_assumptions(assumptions)

    # --- read-only signal extraction -------------------------------------
    re_coverage = rule_evaluation.get("coverage_status")
    re_prr = bool(rule_evaluation.get("professional_review_required"))
    fail_safe_reason = rule_evaluation.get("fail_safe_reason")
    rule_conflict = _as_dict(rule_evaluation.get("rule_conflict"))
    spatial_uncertainty = _as_dict(rule_evaluation.get("spatial_uncertainty"))
    family_coverage = _as_dict(rule_evaluation.get("family_coverage"))
    family_cov_status = family_coverage.get("coverage_status")
    lot_area_source = rule_evaluation.get("lot_area_source")
    zoning_district = rule_evaluation.get("zoning_district")

    trace = _find_residential_far_trace(rule_evaluation)
    trace_outputs = _as_dict(trace.get("outputs")) if trace else {}
    trace_completeness = None
    if trace is not None and isinstance(trace.get("data_completeness"), str):
        try:
            trace_completeness = DataCompleteness(trace["data_completeness"])
        except ValueError:
            trace_completeness = None

    lot_area_raw = rule_evaluation.get("lot_area_sq_ft")
    cap_raw = trace_outputs.get(C.CAP_OUTPUT_NAME) if trace else None
    far_raw = trace_outputs.get(C.FAR_OUTPUT_NAME) if trace else None

    # --- malformed / non-finite detection (fail-closed) ------------------
    malformed_fields: list[str] = []
    lot_area = _positive_finite_float(lot_area_raw)
    if _is_present_number(lot_area_raw) and lot_area is None:
        malformed_fields.append("lot_area_sq_ft")
    cap_value = _positive_finite_float(cap_raw)
    if _is_present_number(cap_raw) and cap_value is None:
        malformed_fields.append(C.CAP_OUTPUT_NAME)
    far_value = _finite_float(far_raw)
    if _is_present_number(far_raw) and far_value is None:
        malformed_fields.append(C.FAR_OUTPUT_NAME)

    # --- bbl cross-check (profile vs rule_evaluation) --------------------
    ev_bbl = _as_dict(rule_evaluation.get("evaluated_input")).get("bbl")
    profile_bbl = _as_dict(property_profile.get("identity")).get("bbl")
    bbl_mismatch = (
        isinstance(ev_bbl, str)
        and isinstance(profile_bbl, str)
        and ev_bbl != profile_bbl
    )

    # --- gating booleans --------------------------------------------------
    has_conflict = (
        re_coverage == "data_conflict"
        or rule_conflict.get("conflict") is True
        or fail_safe_reason in C.CONFLICT_FAIL_SAFE_REASONS
        or bbl_mismatch
    )
    has_professional_review = (
        re_prr
        or re_coverage == "professional_review_required"
        or bool(spatial_uncertainty.get("professional_review_required"))
        or fail_safe_reason in C.PROFESSIONAL_REVIEW_FAIL_SAFE_REASONS
    )
    has_malformed = bool(malformed_fields)
    is_unsupported = (
        re_coverage in {"unsupported", "not_applicable"}
        or family_cov_status in {"unsupported", "not_applicable"}
    )

    # Provenance / lot-area constraint reused by several branches.
    lot_area_prov = _lot_area_provenance(rule_evaluation, property_profile, lot_area_source)

    # =====================================================================
    # Precedence: malformed > conflict > professional-review > unsupported >
    # preliminary. Each fail-closed branch surfaces NO cap.
    # =====================================================================

    if has_malformed:
        return _no_scenario_malformed(
            rule_evaluation, property_profile, malformed_fields, lot_area, lot_area_prov,
            zoning_district, assumption_records,
        )

    if has_conflict:
        return _no_scenario_conflict(
            rule_evaluation, property_profile, rule_conflict, fail_safe_reason,
            bbl_mismatch, lot_area, lot_area_prov, zoning_district, assumption_records,
        )

    if has_professional_review:
        return _no_scenario_professional_review(
            rule_evaluation, property_profile, spatial_uncertainty, fail_safe_reason,
            lot_area, lot_area_prov, zoning_district, assumption_records,
        )

    if is_unsupported:
        return _unsupported_stub(
            rule_evaluation, property_profile, re_coverage, family_coverage,
            lot_area, lot_area_prov, zoning_district, assumption_records,
        )

    # --- preliminary candidate: all controlling inputs must be present ---
    missing_inputs: list[str] = []
    family_conditional = family_cov_status == "conditional" and re_coverage == "conditional"
    if not family_conditional:
        missing_inputs.append("residential_far family coverage (conditional)")
    if trace is None:
        missing_inputs.append("applicable residential_far evaluation trace")
    if lot_area is None:
        missing_inputs.append("lot_area_sq_ft")
    if cap_value is None:
        missing_inputs.append(C.CAP_OUTPUT_NAME)

    if missing_inputs:
        return _no_scenario_missing(
            rule_evaluation, property_profile, re_coverage, missing_inputs,
            lot_area, lot_area_prov, zoning_district, trace_completeness, assumption_records,
        )

    # --- VERIFICATION-ONLY integrity check (never replaces the value) ----
    if far_value is not None:
        recomputed = far_value * lot_area
        canonical = cap_value
        tolerance = C.INTEGRITY_TOLERANCE * max(1.0, abs(canonical))
        agreed = math.isfinite(recomputed) and abs(recomputed - canonical) <= tolerance
        if not agreed:
            return _no_scenario_integrity(
                rule_evaluation, property_profile, lot_area, lot_area_prov,
                zoning_district, trace, assumption_records,
            )
        integrity_check = {
            "performed": True,
            "agreed": True,
            "tolerance": C.INTEGRITY_TOLERANCE,
            "method": C.INTEGRITY_METHOD,
            "note": (
                "Verification-only recompute (far * lot_area) agreed with the "
                "canonical trace value within tolerance; the surfaced value "
                "remains the canonical trace output, not the recompute."
            ),
        }
    else:
        integrity_check = _integrity_not_performed(
            "Verification recompute skipped: max_residential_far not available; "
            "the surfaced value is the canonical trace output."
        )

    # --- PRELIMINARY: surface the canonical cap VERBATIM -----------------
    cap_prov = _cap_provenance(trace)
    constraints = [
        _constraint(
            key="residential_far_cap",
            state=ConstraintCompleteness.DRAFT,
            value=cap_value,
            unit="square_feet",
            completeness=trace_completeness or DataCompleteness.MISSING_NONCRITICAL,
            provenance=cap_prov,
            note=C.DRAFT_CAP_LABEL,
        ),
        _constraint(
            key="lot_area",
            state=ConstraintCompleteness.KNOWN,
            value=lot_area,
            unit="square_feet",
            completeness=DataCompleteness.COMPLETE,
            provenance=lot_area_prov,
            note="Zoning-lot area consumed from the rule_evaluation input (profile-sourced).",
        ),
        _constraint(
            key="zoning_district",
            state=ConstraintCompleteness.KNOWN,
            value=zoning_district if isinstance(zoning_district, str) else None,
            unit=None,
            completeness=DataCompleteness.COMPLETE,
            provenance=None,
            note="Confidently-assigned base zoning district used by the evaluation.",
        ),
    ]
    constraints.extend(_missing_envelope_constraints())

    reasons = [
        (
            "Preliminary scenario: surfaced the canonical draft residential "
            "zoning-floor-area cap (ZR 23-21) from the rule_evaluation trace, "
            "verbatim. NOT a buildable envelope - see the coverage matrix for the "
            "rule families still MISSING."
        )
    ]

    return _assemble(
        scenario_kind=ScenarioKind.PRELIMINARY,
        coverage_status="conditional",
        professional_review_required=False,
        rule_evaluation=rule_evaluation,
        property_profile=property_profile,
        constraints=constraints,
        reasons=reasons,
        cap_value=cap_value,
        cap_provenance=cap_prov,
        assumptions=assumption_records,
        integrity_check=integrity_check,
    )


# ---------------------------------------------------------------------------
# Fail-closed / stub branches (each surfaces NO cap)
# ---------------------------------------------------------------------------


def _base_constraints_no_cap(
    cap_state: ConstraintCompleteness,
    cap_note: str,
    lot_area: float | None,
    lot_area_prov: dict | None,
    zoning_district: Any,
    district_state: ConstraintCompleteness,
    cap_provenance: dict | None = None,
    district_provenance: dict | None = None,
) -> list[dict]:
    """Constraint list for a no-cap outcome: the cap constraint in the given
    state, lot_area/zoning_district reflecting what is known, then the always-
    missing envelope families."""
    if lot_area is not None:
        lot_constraint = _constraint(
            key="lot_area",
            state=ConstraintCompleteness.KNOWN,
            value=lot_area,
            unit="square_feet",
            completeness=DataCompleteness.COMPLETE,
            provenance=lot_area_prov,
            note="Zoning-lot area consumed from the rule_evaluation input (profile-sourced).",
        )
    else:
        lot_constraint = _constraint(
            key="lot_area",
            state=ConstraintCompleteness.MISSING,
            value=None,
            unit="square_feet",
            completeness=DataCompleteness.MISSING_CRITICAL,
            provenance=lot_area_prov,
            note="No positive zoning-lot area available; not inferred.",
        )
    constraints = [
        _constraint(
            key="residential_far_cap",
            state=cap_state,
            value=None,
            unit="square_feet",
            completeness=DataCompleteness.MISSING_CRITICAL,
            provenance=cap_provenance,
            note=cap_note,
        ),
        lot_constraint,
        _constraint(
            key="zoning_district",
            state=district_state,
            value=zoning_district if isinstance(zoning_district, str) else None,
            unit=None,
            completeness=(
                DataCompleteness.COMPLETE
                if district_state == ConstraintCompleteness.KNOWN
                else DataCompleteness.MISSING_CRITICAL
            ),
            provenance=district_provenance,
            note="Base zoning district as seen by the evaluation (never collapsed when uncertain).",
        ),
    ]
    constraints.extend(_missing_envelope_constraints())
    return constraints


def _no_scenario_malformed(
    rule_evaluation, property_profile, malformed_fields, lot_area, lot_area_prov,
    zoning_district, assumptions,
):
    constraints = _base_constraints_no_cap(
        cap_state=ConstraintCompleteness.PROFESSIONAL_REVIEW_REQUIRED,
        cap_note=(
            "Malformed / non-finite numeric input detected; no cap surfaced "
            "(fail-closed). Fields: " + ", ".join(sorted(malformed_fields))
        ),
        lot_area=lot_area if "lot_area_sq_ft" not in malformed_fields else None,
        lot_area_prov=lot_area_prov,
        zoning_district=zoning_district,
        district_state=ConstraintCompleteness.KNOWN
        if isinstance(zoning_district, str)
        else ConstraintCompleteness.MISSING,
    )
    reasons = [
        (
            "NO SCENARIO (fail-closed): malformed or non-finite numeric input "
            "(" + ", ".join(sorted(malformed_fields)) + "). No value is guessed; "
            "escalated to professional review."
        )
    ]
    return _assemble(
        scenario_kind=ScenarioKind.NO_SCENARIO,
        coverage_status="professional_review_required",
        professional_review_required=True,
        rule_evaluation=rule_evaluation,
        property_profile=property_profile,
        constraints=constraints,
        reasons=reasons,
        cap_value=None,
        cap_provenance=None,
        assumptions=assumptions,
        integrity_check=_integrity_not_performed(
            "Not performed: malformed input stopped the build before any cap candidate."
        ),
    )


def _no_scenario_conflict(
    rule_evaluation, property_profile, rule_conflict, fail_safe_reason, bbl_mismatch,
    lot_area, lot_area_prov, zoning_district, assumptions,
):
    conflict_prov = None
    if rule_conflict.get("conflict") is True:
        conflict_prov = {
            "family": rule_conflict.get("family"),
            "as_of_date": rule_conflict.get("as_of_date"),
            "competing_output_names": rule_conflict.get("competing_output_names"),
            "competing_rules": rule_conflict.get("competing_rules"),
            "note": rule_conflict.get("note"),
        }
    reasons = [
        (
            "NO SCENARIO (fail-closed): a legal-rule or data conflict is present; "
            "the scenario engine never selects, ranks, or merges competing rules."
        )
    ]
    if bbl_mismatch:
        reasons.append(
            "Input mismatch: the property_profile identity.bbl and the "
            "rule_evaluation evaluated_input.bbl disagree; treated as a data conflict."
        )
    if fail_safe_reason in C.CONFLICT_FAIL_SAFE_REASONS:
        reasons.append(f"rule_evaluation fail_safe_reason: {fail_safe_reason}.")
    constraints = _base_constraints_no_cap(
        cap_state=ConstraintCompleteness.CONFLICTING,
        cap_note=(
            "Competing rules / conflicting data present; no cap surfaced. Conflict "
            "provenance retained in reasons/provenance."
        ),
        lot_area=lot_area,
        lot_area_prov=lot_area_prov,
        zoning_district=zoning_district,
        district_state=ConstraintCompleteness.CONFLICTING,
        cap_provenance=conflict_prov,
    )
    return _assemble(
        scenario_kind=ScenarioKind.NO_SCENARIO,
        coverage_status="data_conflict",
        professional_review_required=False,
        rule_evaluation=rule_evaluation,
        property_profile=property_profile,
        constraints=constraints,
        reasons=reasons,
        cap_value=None,
        cap_provenance=None,
        assumptions=assumptions,
        integrity_check=_integrity_not_performed(
            "Not performed: a conflict stopped the build before any cap candidate."
        ),
    )


def _no_scenario_professional_review(
    rule_evaluation, property_profile, spatial_uncertainty, fail_safe_reason,
    lot_area, lot_area_prov, zoning_district, assumptions,
):
    # Surface the share ranges / review flags, never collapsed.
    district_prov = None
    if spatial_uncertainty:
        district_prov = {
            "lot_overall_class": spatial_uncertainty.get("lot_overall_class"),
            "professional_review_required": spatial_uncertainty.get(
                "professional_review_required"
            ),
            "review_reasons": spatial_uncertainty.get("review_reasons"),
            "base_district_candidates": spatial_uncertainty.get("base_district_candidates"),
            "coverage_note": spatial_uncertainty.get("coverage_note"),
        }
    reasons = [
        (
            "NO SCENARIO (fail-closed): spatial/professional-review uncertainty is "
            "present; share ranges and review flags are surfaced, never collapsed "
            "into a definitive district."
        )
    ]
    if fail_safe_reason in C.PROFESSIONAL_REVIEW_FAIL_SAFE_REASONS:
        reasons.append(f"rule_evaluation fail_safe_reason: {fail_safe_reason}.")
    constraints = _base_constraints_no_cap(
        cap_state=ConstraintCompleteness.PROFESSIONAL_REVIEW_REQUIRED,
        cap_note="Spatial/professional-review uncertainty blocks any cap.",
        lot_area=lot_area,
        lot_area_prov=lot_area_prov,
        zoning_district=zoning_district,
        district_state=ConstraintCompleteness.PROFESSIONAL_REVIEW_REQUIRED,
        district_provenance=district_prov,
    )
    return _assemble(
        scenario_kind=ScenarioKind.NO_SCENARIO,
        coverage_status="professional_review_required",
        professional_review_required=True,
        rule_evaluation=rule_evaluation,
        property_profile=property_profile,
        constraints=constraints,
        reasons=reasons,
        cap_value=None,
        cap_provenance=None,
        assumptions=assumptions,
        integrity_check=_integrity_not_performed(
            "Not performed: professional-review/spatial uncertainty stopped the build."
        ),
    )


def _unsupported_stub(
    rule_evaluation, property_profile, re_coverage, family_coverage,
    lot_area, lot_area_prov, zoning_district, assumptions,
):
    coverage_status = (
        re_coverage
        if re_coverage in {"unsupported", "not_applicable"}
        else family_coverage.get("coverage_status")
    )
    if coverage_status not in {"unsupported", "not_applicable"}:
        coverage_status = "unsupported"
    family_prov = None
    if family_coverage:
        family_prov = {
            "family": family_coverage.get("family"),
            "coverage_status": family_coverage.get("coverage_status"),
            "note": family_coverage.get("note"),
        }
    reasons = [
        (
            "UNSUPPORTED: the district / rule family is not implemented. No cap is "
            "surfaced; this is a visible stub, not silence."
        )
    ]
    constraints = _base_constraints_no_cap(
        cap_state=ConstraintCompleteness.UNSUPPORTED,
        cap_note="No implemented rule family for this district; unsupported (visible).",
        lot_area=lot_area,
        lot_area_prov=lot_area_prov,
        zoning_district=zoning_district,
        district_state=ConstraintCompleteness.UNSUPPORTED,
        cap_provenance=family_prov,
    )
    return _assemble(
        scenario_kind=ScenarioKind.UNSUPPORTED,
        coverage_status=coverage_status,
        professional_review_required=False,
        rule_evaluation=rule_evaluation,
        property_profile=property_profile,
        constraints=constraints,
        reasons=reasons,
        cap_value=None,
        cap_provenance=None,
        assumptions=assumptions,
        integrity_check=_integrity_not_performed(
            "Not performed: unsupported family, no cap candidate."
        ),
    )


def _no_scenario_missing(
    rule_evaluation, property_profile, re_coverage, missing_inputs,
    lot_area, lot_area_prov, zoning_district, trace_completeness, assumptions,
):
    coverage_status = (
        re_coverage
        if re_coverage in C.DRAFT_COVERAGE_VALUES
        else "professional_review_required"
    )
    reasons = [
        (
            "NO SCENARIO: a required controlling input is absent - "
            + "; ".join(missing_inputs)
            + ". Nothing is inferred to fill the gap."
        )
    ]
    constraints = _base_constraints_no_cap(
        cap_state=ConstraintCompleteness.MISSING,
        cap_note=(
            "Required controlling input(s) absent: "
            + ", ".join(missing_inputs)
            + ". Not inferred."
        ),
        lot_area=lot_area,
        lot_area_prov=lot_area_prov,
        zoning_district=zoning_district,
        district_state=ConstraintCompleteness.KNOWN
        if isinstance(zoning_district, str)
        else ConstraintCompleteness.MISSING,
    )
    return _assemble(
        scenario_kind=ScenarioKind.NO_SCENARIO,
        coverage_status=coverage_status,
        professional_review_required=coverage_status == "professional_review_required",
        rule_evaluation=rule_evaluation,
        property_profile=property_profile,
        constraints=constraints,
        reasons=reasons,
        cap_value=None,
        cap_provenance=None,
        assumptions=assumptions,
        integrity_check=_integrity_not_performed(
            "Not performed: a required controlling input was absent."
        ),
    )


def _no_scenario_integrity(
    rule_evaluation, property_profile, lot_area, lot_area_prov, zoning_district,
    trace, assumptions,
):
    """Fail-closed on integrity disagreement (proposal section 5 step 5). Neither
    the canonical value nor the recompute is surfaced; the canonical value is
    never replaced."""
    reasons = [
        (
            "NO SCENARIO (fail-closed): the verification-only recompute "
            "(far * lot_area) disagreed with the canonical trace value beyond "
            "tolerance. Neither number is surfaced; the canonical trace value is "
            "never replaced by a locally derived one."
        )
    ]
    # Provenance of the disputed cap is retained (rule id/version/status) so the
    # conflict is auditable, but NO numeric value is surfaced.
    cap_prov = {
        "rule_id": trace.get("rule_id"),
        "rule_version": trace.get("rule_version"),
        "rule_status": trace.get("rule_status"),
        "output_name": C.CAP_OUTPUT_NAME,
        "citations": [],
        "note": (
            "Cap withheld: verification recompute disagreed with the canonical "
            "trace value; fail-closed to data_conflict."
        ),
    }
    constraints = _base_constraints_no_cap(
        cap_state=ConstraintCompleteness.CONFLICTING,
        cap_note=(
            "Integrity disagreement between the canonical trace value and the "
            "verification recompute; no cap surfaced (fail-closed)."
        ),
        lot_area=lot_area,
        lot_area_prov=lot_area_prov,
        zoning_district=zoning_district,
        district_state=ConstraintCompleteness.KNOWN
        if isinstance(zoning_district, str)
        else ConstraintCompleteness.MISSING,
        cap_provenance=cap_prov,
    )
    integrity_check = {
        "performed": True,
        "agreed": False,
        "tolerance": C.INTEGRITY_TOLERANCE,
        "method": C.INTEGRITY_METHOD,
        "note": (
            "Verification recompute disagreed with the canonical trace value "
            "beyond tolerance; failed closed. Raw numbers are not surfaced."
        ),
    }
    return _assemble(
        scenario_kind=ScenarioKind.NO_SCENARIO,
        coverage_status="data_conflict",
        professional_review_required=False,
        rule_evaluation=rule_evaluation,
        property_profile=property_profile,
        constraints=constraints,
        reasons=reasons,
        cap_value=None,
        cap_provenance=None,
        assumptions=assumptions,
        integrity_check=integrity_check,
    )
