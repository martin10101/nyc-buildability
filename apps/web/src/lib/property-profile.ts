/**
 * TypeScript view of the canonical property-profile contract v1.1
 * (packages/contracts/schemas/v1/property_profile.schema.json, contract
 * versions 1.0.0 and 1.1.0).
 *
 * RULES (task M2-T001):
 * - This file models ONLY keys documented in the v1.1 contract
 *   (property_profile + source_fact + coverage_status + common schemas and
 *   packages/contracts/README.md). No competing schema, no invented keys.
 * - The accepted M1-T005 builder emits provenance records with EXTRA keys
 *   (e.g. dataset_id, request_url, input_vintages) that are NOT documented
 *   in source_fact.schema.json. Per the "documented keys only" rule the UI
 *   does NOT read them; dataset id / request URL metadata is read from the
 *   documented top-level `reproducibility` object instead.
 * - Every optional key here is optional in the contract; the UI must
 *   tolerate its absence (M1-T005 G3 carry-forward section 5: absent
 *   identity.address / identity.geometry / mapped_features, absent borough
 *   under conflict, partial district-provenance maps per M1-T006 D5).
 */

/** PRD section 12 coverage statuses — exactly the 6 canonical values. */
export const COVERAGE_STATUSES = [
  "verified",
  "conditional",
  "professional_review_required",
  "data_conflict",
  "unsupported",
  "not_applicable",
] as const;
export type CoverageStatus = (typeof COVERAGE_STATUSES)[number];

/** PRD section 12 data-completeness — exactly the 3 canonical values. */
export const DATA_COMPLETENESS_VALUES = [
  "complete",
  "missing_noncritical",
  "missing_critical",
] as const;
export type DataCompleteness = (typeof DATA_COMPLETENESS_VALUES)[number];

/** property_profile.schema.json $defs/fact_value. */
export interface FactValue {
  value: unknown;
  units?: string;
  provenance_ref: string;
  coverage_status?: CoverageStatus;
}

/**
 * source_fact.schema.json — documented keys only. The schema is open
 * (additionalProperties permitted) but undocumented keys are off-limits to
 * this frontend by task rule.
 */
export interface ProvenanceRecord {
  provenance_id: string;
  source_id: string;
  original_field_name: string;
  original_value: unknown;
  normalized_value: unknown;
  units?: string | null;
  retrieved_at: string;
  dataset_version: string;
  effective_date: string | null;
  bbl: string;
  confidence: number;
  user_confirmed_or_overridden: "none" | "confirmed" | "overridden";
  conflict_status: "none" | "conflicting" | "resolved";
}

export interface ProfileVersion {
  contract_version: "1.0.0" | "1.1.0";
  profile_revision: number;
  generated_at: string;
}

export interface IdentityAddress {
  house_number?: string;
  street_name?: string;
  borough?: string;
  borough_code?: number;
  zip_code?: string;
  normalized_address?: string;
}

export interface Identity {
  bbl: string;
  bins?: string[];
  /** May be absent (e.g. under borocode conflict — never derived). */
  address?: IdentityAddress;
  /** May be absent; full geometry contract is deferred to M2 tasks. */
  geometry?: { type?: string; coordinates?: unknown };
}

/** Entries of zoning.mapped_features (open objects; builder emits these). */
export interface MappedFeature {
  feature?: string;
  value?: unknown;
  provenance_ref?: string;
  coverage_status?: CoverageStatus;
  [key: string]: unknown;
}

/** Contract 1.1.0 district-provenance map (value -> non-empty ref list). */
export type DistrictProvenanceMap = Record<string, string[]>;

export interface Zoning {
  districts?: string[];
  commercial_overlays?: string[];
  special_districts?: string[];
  mapped_features?: MappedFeature[];
  /** OPTIONAL and possibly PARTIAL (M1-T006 G3 D5): never assume coverage. */
  district_provenance?: DistrictProvenanceMap;
  commercial_overlay_provenance?: DistrictProvenanceMap;
  special_district_provenance?: DistrictProvenanceMap;
}

export interface MissingInput {
  field: string;
  criticality: "critical" | "noncritical";
  reason?: string;
}

export interface ConflictValue {
  source_id: string;
  value: unknown;
  /** Not documented as required; builder emits it — treat as optional. */
  derivation?: string;
}

export interface Conflict {
  field: string;
  values: ConflictValue[];
  resolution: "unresolved" | "user_confirmed" | "user_overridden" | "source_priority";
  reason?: string | null;
}

export interface UserConfirmation {
  field: string;
  action: "confirmed" | "overridden";
  override_value?: unknown;
  confirmed_at?: string;
  confirmed_by?: string;
}

/** Contract 1.1.0 reproducibility block — all 10 subfields required when present. */
export interface Reproducibility {
  correlation_id: string;
  source_id: string;
  dataset_id: string;
  dataset_version: string | null;
  request_url: string;
  retrieved_at: string;
  record_count: number;
  drift_signals: string[];
  connector_notes: string[];
  coverage_policy: string;
}

export interface PropertyProfile {
  profile_version: ProfileVersion;
  identity: Identity;
  lot_facts: Record<string, FactValue>;
  existing_building_facts: Record<string, FactValue>;
  zoning: Zoning;
  project_intent: { objectives?: string[]; notes?: string };
  provenance: ProvenanceRecord[];
  missing_inputs: MissingInput[];
  conflicts: Conflict[];
  user_confirmations: UserConfirmation[];
  data_completeness?: DataCompleteness;
  reproducibility?: Reproducibility;
}
