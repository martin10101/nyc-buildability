// GENERATED FILE - DO NOT EDIT BY HAND.
// Source of truth: packages/contracts/schemas/v1/property_profile.schema.json
// (+ common, source_fact, coverage_status). Regenerate with:
//   python packages/contracts/scripts/generate_ts_types.py
// CI fails if this file diverges from a fresh generation (task M2-T003, S5).
//
// These types replace any hand-written client property-profile
// representation; all modules exchange this one canonical contract
// (PRD section 32.3). Every schema key is covered.
export type Bbl = string;
export type Bin = string;
export type BoroughCode = 1 | 2 | 3 | 4 | 5;
export type BoroughName = "Manhattan" | "Bronx" | "Brooklyn" | "Queens" | "Staten Island";
export type ZipCode = string;
export type DateTime = string;
export type DateOnly = string;
export type NonEmptyString = string;
export type DigestSha256 = string;
export type CoverageStatus = "verified" | "conditional" | "professional_review_required" | "data_conflict" | "unsupported" | "not_applicable";
export type DataCompleteness = "complete" | "missing_noncritical" | "missing_critical";
export interface SourceFact {
  provenance_id: NonEmptyString;
  source_id: NonEmptyString;
  original_field_name: NonEmptyString;
  original_value: unknown;
  normalized_value: unknown;
  units?: string | null;
  retrieved_at: DateTime;
  dataset_version: NonEmptyString;
  effective_date: string | null;
  bbl: Bbl;
  confidence: number;
  user_confirmed_or_overridden: "none" | "confirmed" | "overridden";
  conflict_status: "none" | "conflicting" | "resolved";
  fact_key?: NonEmptyString;
  observation_id?: NonEmptyString;
  value_digest?: DigestSha256;
  response_digest?: DigestSha256;
}
export interface FactValue {
  value: unknown;
  units?: string;
  provenance_ref: NonEmptyString;
  coverage_status?: CoverageStatus;
}
export type ProvenanceRefList = NonEmptyString[];
export interface DistrictProvenanceMap {
  [key: string]: ProvenanceRefList;
}
export interface PropertyProfile {
  profile_version: {
    contract_version: "1.0.0" | "1.1.0" | "1.2.0" | "1.3.0" | "1.4.0";
    profile_revision: number;
    generated_at: DateTime;
  };
  identity: {
    bbl: Bbl;
    bins?: Bin[];
    address?: {
      house_number?: string;
      street_name?: string;
      borough?: BoroughName;
      borough_code?: BoroughCode;
      zip_code?: ZipCode;
      normalized_address?: string;
    };
    geometry?: {
      type?: string;
      coordinates?: unknown;
    };
  };
  lot_facts: {
    [key: string]: FactValue;
  };
  existing_building_facts: {
    [key: string]: FactValue;
  };
  zoning: {
    districts?: string[];
    commercial_overlays?: string[];
    special_districts?: string[];
    mapped_features?: {
    }[];
    district_provenance?: DistrictProvenanceMap;
    commercial_overlay_provenance?: DistrictProvenanceMap;
    special_district_provenance?: DistrictProvenanceMap;
  };
  project_intent: {
    objectives?: string[];
    notes?: string;
  };
  provenance: SourceFact[];
  missing_inputs: {
    field: string;
    criticality: "critical" | "noncritical";
    reason?: string;
    feasibility_relevant?: boolean;
  }[];
  conflicts: {
    field: string;
    values: {
      source_id: string;
      value: unknown;
    }[];
    resolution: "unresolved" | "user_confirmed" | "user_overridden" | "source_priority";
  }[];
  user_confirmations: {
    field: string;
    action: "confirmed" | "overridden";
    override_value?: unknown;
    confirmed_at?: DateTime;
    confirmed_by?: string;
  }[];
  data_completeness?: DataCompleteness;
  reproducibility?: {
    correlation_id: NonEmptyString;
    source_id: NonEmptyString;
    dataset_id: NonEmptyString;
    dataset_version: string | null;
    request_url: NonEmptyString;
    retrieved_at: DateTime;
    record_count: number;
    drift_signals: NonEmptyString[];
    connector_notes: NonEmptyString[];
    coverage_policy: NonEmptyString;
    response_digest?: DigestSha256;
    digest_canonicalization?: NonEmptyString;
    staleness?: {
      served_from_cache: boolean;
      stale: boolean;
      upstream_error_type?: NonEmptyString;
      original_retrieved_at?: DateTime;
      age_seconds?: number;
    };
  };
  status_dimensions?: {
    source_record_completeness: "complete" | "partial" | "not_computed";
    analysis_readiness: "ready" | "blocked_missing_critical" | "blocked_data_conflict" | "not_computed";
    rule_coverage: "not_computed";
    geometry_validity: "missing" | "not_computed";
    financial_readiness: "not_computed";
    policy: NonEmptyString;
  };
  zoning_features?: {
    layers?: {
      layer: NonEmptyString;
      provenance_ref: NonEmptyString;
      coverage_status?: CoverageStatus;
    }[];
  };
  lot_geometry?: {
    outcome: NonEmptyString;
    review_required?: boolean;
    geometry_status?: string | null;
    area_sq_ft?: number | null;
    provenance_ref: NonEmptyString;
    coverage_status?: CoverageStatus;
    crs?: {
    };
  };
  spatial_intersection?: {
    bbl: Bbl;
    lot_overall_class: NonEmptyString;
    professional_review_required: boolean;
    coverage_note: NonEmptyString;
    provenance_refs: ProvenanceRefList;
    pairs?: {
    }[];
    crosscheck?: unknown | null;
    review_reasons?: string[];
    unassigned_area?: {
    }[];
    overlap_area?: {
    }[];
    accuracy_records?: {
    }[];
    policy?: {
    };
    notes?: string[];
  };
}
