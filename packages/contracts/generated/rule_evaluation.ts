// GENERATED FILE - DO NOT EDIT BY HAND.
// Source of truth: packages/contracts/schemas/v1/rule_evaluation.schema.json
// (+ common, coverage_status). Regenerate with:
//   python packages/contracts/scripts/generate_ts_types.py
// CI fails if this file diverges from a fresh generation (task M4-T005).
//
// One canonical rule-evaluation result contract shared by API, workers,
// scenarios, and reports (PRD section 32.3). coverage_status is the
// canonical vocabulary narrowed to exclude 'verified' - a draft result
// is never Verified. The evaluated input is identified by reference
// (bbl + profile contract version + provenance + fingerprint), never by
// an embedded profile copy.
export type Bbl = string;
export type NonEmptyString = string;
export type DigestSha256 = string;
export type CoverageStatus = "verified" | "conditional" | "professional_review_required" | "data_conflict" | "unsupported" | "not_applicable";
export type DataCompleteness = "complete" | "missing_noncritical" | "missing_critical";
export type DraftCoverageStatus = CoverageStatus & ("conditional" | "professional_review_required" | "data_conflict" | "unsupported" | "not_applicable");
export interface InputProvenance {
  zoning_district: NonEmptyString[];
  lot_area_sq_ft: NonEmptyString[];
}
export interface EvaluatedInput {
  bbl: Bbl | null;
  profile_contract_version: NonEmptyString;
  input_fingerprint: DigestSha256;
  input_provenance: InputProvenance;
}
export interface SpatialContext {
  lot_overall_class: string | null;
  professional_review_required: boolean;
  coverage_note: string | null;
}
export interface BaseDistrictCandidate {
  district_label: string | null;
  pair_class: string | null;
  share_min: number | null;
  share_point: number | null;
  share_max: number | null;
  minor_portion: boolean | null;
}
export interface SpatialUncertainty {
  lot_overall_class: string | null;
  professional_review_required: boolean;
  coverage_note: string | null;
  review_reasons: string[];
  notes: string[];
  base_district_candidates: BaseDistrictCandidate[];
  crosscheck: unknown;
}
export interface FamilyCoverage {
  family: string;
  coverage_status: DraftCoverageStatus;
  note: string;
  rule_ids?: string[];
}
export interface CompetingRule {
  rule_id: string;
  rule_version: string;
  effective_from: string | null;
  effective_to: string | null;
  output_names: string[];
}
export interface RuleConflict {
  conflict: boolean;
  family: string;
  as_of_date: string | null;
  competing_output_names: string[];
  competing_rules: CompetingRule[];
  note: string;
}
export interface ComputationStep {
  step_id: string;
  op: string;
  resolved_args: unknown[];
  result: number;
  note: string;
}
export interface Citation {
  snapshot_id: string;
  section: string;
  quote: string;
  last_amended?: string | null;
  provenance: {
  };
}
export interface EvaluationTrace {
  rule_id: string;
  rule_version: string;
  rule_status: "discovered" | "extracted_draft" | "needs_review" | "published";
  family: string;
  evaluated_inputs: {
  };
  applicability_outcome: boolean;
  applicability_trace: {
  }[];
  computation_steps: ComputationStep[];
  outputs: {
  };
  coverage_status: DraftCoverageStatus;
  data_completeness: DataCompleteness;
  citations: Citation[];
  uncertainty: {
  };
  exceptions_applied: unknown[];
  notes: string[];
  input_validation: {
    valid: boolean;
    invalid_inputs: {
      name: string;
      reason: string;
      value_seen?: unknown;
    }[];
  };
  rule_release: {
    lifecycle_status: "discovered" | "extracted_draft" | "needs_review" | "published";
    deterministic_tests: "declared" | "none";
    independent_review: "pending" | "passed";
    qualified_human_approval: "pending" | "approved";
    verified_eligible: boolean;
  };
  effective_window: {
    effective_from: string | null;
    effective_to: string | null;
    evaluated_as_of: string | null;
    in_effect: boolean;
  };
  determination: unknown | null;
}
export interface RuleEvaluation {
  contract_version: "1.0.0";
  evaluated_input: EvaluatedInput;
  coverage_status: DraftCoverageStatus;
  coverage_source: "rule_evaluator" | "integration_fail_safe";
  data_completeness: DataCompleteness | null;
  needs_review: boolean;
  professional_review_required: boolean;
  fail_safe: boolean;
  fail_safe_reason: ("spatial_intersection_absent" | "spatial_context_incomplete" | "data_conflict" | "geometry_uncertain" | "inconsistent_confident_geometry" | "rule_conflict") | null;
  rule_lifecycle_statuses: ("discovered" | "extracted_draft" | "needs_review" | "published")[];
  not_verified_disclaimer: NonEmptyString;
  zoning_district: NonEmptyString | null;
  lot_area_sq_ft: number | null;
  lot_area_source: NonEmptyString | null;
  spatial_context: SpatialContext | null;
  spatial_uncertainty: SpatialUncertainty;
  evaluations: EvaluationTrace[];
  family_coverage: FamilyCoverage;
  reasons: string[];
  rule_conflict: RuleConflict | null;
  _expected_failure?: string;
}
