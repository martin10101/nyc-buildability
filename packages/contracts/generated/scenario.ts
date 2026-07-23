// GENERATED FILE - DO NOT EDIT BY HAND.
// Source of truth: packages/contracts/schemas/v1/scenario.schema.json
// (+ common, coverage_status). Regenerate with:
//   python packages/contracts/scripts/generate_ts_types.py
// CI fails if this file diverges from a fresh generation (task M5-T001).
//
// One canonical scenario contract shared by API, workers, and reports
// (PRD section 32.3). coverage_status is the canonical vocabulary
// narrowed to exclude 'verified' - a scenario is never Verified. The
// draft zoning-floor-area cap is surfaced VERBATIM from a rule_evaluation
// trace, never recomputed; envelope constraints are MISSING, never
// inferred. The evaluated input is identified by reference, never by an
// embedded profile copy.
export type Bbl = string;
export type NonEmptyString = string;
export type DigestSha256 = string;
export type CoverageStatus = "verified" | "conditional" | "professional_review_required" | "data_conflict" | "unsupported" | "not_applicable";
export type DataCompleteness = "complete" | "missing_noncritical" | "missing_critical";
export type DraftCoverageStatus = CoverageStatus & ("conditional" | "professional_review_required" | "data_conflict" | "unsupported" | "not_applicable");
export interface ScenarioEvaluatedInput {
  bbl: Bbl | null;
  profile_contract_version: NonEmptyString;
  rule_evaluation_contract_version: NonEmptyString;
  input_fingerprint: DigestSha256 | null;
}
export interface ScenarioCitation {
  snapshot_id: string;
  section: string;
  quote: string;
  last_amended?: string | null;
  provenance: {
  };
}
export interface CapProvenance {
  rule_id: string;
  rule_version: string;
  rule_status: "discovered" | "extracted_draft" | "needs_review" | "published";
  output_name: string;
  citations: ScenarioCitation[];
  note: string;
}
export interface ScenarioConstraint {
  key: NonEmptyString;
  state: "known" | "draft" | "missing" | "conflicting" | "unsupported" | "professional_review_required";
  value: number | string | boolean | null;
  unit: string | null;
  data_completeness: DataCompleteness;
  provenance: unknown | null;
  note: string;
}
export interface ScenarioAssumption {
  key: NonEmptyString;
  assumption_type: string;
  value: number | string | boolean | null;
  unit: string | null;
  rationale: string;
}
export interface CoverageMatrixRow {
  constraint_family: string;
  governs: string;
  rule_status_today: "draft" | "missing" | "out_of_scope";
  blocks_buildable_envelope: boolean;
}
export interface IntegrityCheck {
  performed: boolean;
  agreed: boolean | null;
  tolerance: number;
  method: string;
  note: string;
}
export interface Scenario {
  contract_version: "1.0.0";
  scenario_kind: "preliminary" | "no_scenario" | "unsupported";
  coverage_status: DraftCoverageStatus;
  data_completeness: DataCompleteness;
  needs_review: boolean;
  professional_review_required: boolean;
  not_verified_disclaimer: NonEmptyString;
  evaluated_input: ScenarioEvaluatedInput;
  constraints: ScenarioConstraint[];
  draft_zoning_floor_area_cap_sq_ft: number | null;
  cap_label: NonEmptyString | null;
  cap_provenance: CapProvenance | null;
  assumptions: ScenarioAssumption[];
  reasons: string[];
  coverage_matrix: CoverageMatrixRow[];
  integrity_check: IntegrityCheck;
  _expected_failure?: string;
}
