// GENERATED FILE - DO NOT EDIT BY HAND.
// Source of truth: packages/contracts/schemas/v1/site_fact.schema.json
// (+ common). Regenerate with:
//   python packages/contracts/scripts/generate_ts_types.py
// CI fails if this file diverges from a fresh generation (task C-03).
//
// One site value of a study: known (rank + source) or unknown (never 0).
// Types only: cross-field rules (oneOf/allOf constraints such as rank vs
// source kind) are enforced by the JSON Schema on the server, not here.
export type Bbl = string;
export type DateTime = string;
export type NonEmptyString = string;
export type Measurement = MeasurementSurveyEntered | MeasurementCityRecords | MeasurementApproximateTaxMap | MeasurementEntered | MeasurementAssumed | MeasurementUnknown;
export type MeasurementKnown = MeasurementSurveyEntered | MeasurementCityRecords | MeasurementApproximateTaxMap | MeasurementEntered | MeasurementAssumed;
export interface MeasurementSurveyEntered {
  rank: "survey_entered";
  label: "Survey (entered)";
}
export interface MeasurementCityRecords {
  rank: "city_records";
  label: "City records";
}
export interface MeasurementApproximateTaxMap {
  rank: "approximate_tax_map";
  label: "Approximate \u2014 tax map";
}
export interface MeasurementEntered {
  rank: "entered";
  label: "Entered";
}
export interface MeasurementAssumed {
  rank: "assumed";
  label: "Assumed";
}
export interface MeasurementUnknown {
  rank: "unknown";
  label: "Unknown \u2014 enter";
}
export interface Source {
  kind: "survey" | "city_dataset" | "city_filing" | "tax_map_computation" | "architect_entry" | "assumption";
  dataset: NonEmptyString | null;
  dataset_version: NonEmptyString | null;
  retrieved_at: DateTime;
  query_ref: NonEmptyString | null;
  document_ref: NonEmptyString | null;
  statement: NonEmptyString | null;
  provenance_refs?: NonEmptyString[];
}
export type BlockedOutput = "floor_area_allowance" | "remaining_floor_area" | "permitted_envelope" | "building_option" | "existing_building_paths" | "unit_estimate" | "geometry";
export interface SiteFact {
  contract_version: "1.0.0";
  fact_id: NonEmptyString;
  key: "lot_area" | "lot_frontage" | "lot_depth" | "lot_type" | "zoning_district" | "commercial_overlay" | "street_width" | "existing_zoning_floor_area";
  lot_bbl: Bbl | null;
  street: NonEmptyString | null;
  value: number | string | null;
  unit: ("square_feet" | "feet") | null;
  measurement: Measurement;
  source: Source | null;
  blocks: BlockedOutput[];
  editable: boolean;
  note?: string | null;
  _expected_failure?: string;
}
