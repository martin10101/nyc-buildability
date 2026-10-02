// GENERATED FILE - DO NOT EDIT BY HAND.
// Source of truth: packages/contracts/schemas/v1/study.schema.json
// (+ common, site_fact). Regenerate with:
//   python packages/contracts/scripts/generate_ts_types.py
// CI fails if this file diverges from a fresh generation (task C-03).
//
// One shared study per property: lots, site facts, options as add-on selections.
// Types only: cross-field rules (oneOf/allOf constraints such as rank vs
// source kind) are enforced by the JSON Schema on the server, not here.
export type Bbl = string;
export type DateTime = string;
export type NonEmptyString = string;
export interface Lot {
  bbl: Bbl;
  approximate_lot_area_sq_ft: number | null;
  size_measurement: Measurement;
  selected: boolean;
}
export interface Combination {
  status: "single_lot" | "offered" | "not_offered";
  reason: NonEmptyString | null;
}
export interface Option {
  option_id: NonEmptyString;
  name: NonEmptyString;
  addon_selection: AddonSwitch[];
  goal: Goal;
  program: ("market_rate_residential" | "affordable_residential" | "senior_residential" | "community_facility" | "commercial")[];
  floor_to_floor_heights: FloorToFloorHeights;
  assumptions: Assumption[];
  existing_building_plan: "no_existing_building" | "keep" | "remove";
}
export interface AddonSwitch {
  addon_id: NonEmptyString;
  on: boolean;
}
export interface Goal {
  kind: "most_residential_floor_area" | "most_total_floor_area" | "other";
  text: NonEmptyString | null;
}
export interface FloorToFloorHeights {
  ground_floor: HeightSetting;
  typical_floor: HeightSetting;
  per_floor_overrides: {
    floor: number;
    height_ft: number;
  }[];
}
export interface HeightSetting {
  height_ft: number;
  basis: "stated_default" | "entered";
  statement: NonEmptyString;
}
export interface Assumption {
  assumption_id: NonEmptyString;
  statement: NonEmptyString;
  value: number | string | boolean | null;
  unit: string | null;
}
export interface Revision {
  number: number;
  created_at: DateTime;
  parent: number | null;
}
export interface Origin {
  kind: "new" | "copied_from_export";
  export_id: NonEmptyString | null;
}
export interface SiteFact {
  contract_version: "1.0.0" | "1.1.0";
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
  version_check?: VersionCheck;
}
export interface VersionCheck {
  status: "current" | "out_of_date" | "version_unknown";
  label: "Current" | "Out of date" | "Version unknown";
  latest_known_version: NonEmptyString | null;
  latest_known_seen_at: DateTime | null;
  latest_known_query_ref: NonEmptyString | null;
  reason: NonEmptyString;
}
export type BlockedOutput = "floor_area_allowance" | "remaining_floor_area" | "permitted_envelope" | "building_option" | "existing_building_paths" | "unit_estimate" | "geometry";
export interface Study {
  contract_version: "1.0.0";
  study_id: NonEmptyString;
  property: {
    bbl: Bbl;
    address: NonEmptyString | null;
  };
  lots: Lot[];
  lot_selection: {
    mode: "all" | "subset";
    statement: "Based on the lots you selected \u2014 the app does not verify the zoning lot";
    combination: Combination;
  };
  site: {
    facts: SiteFact[];
  };
  options: Option[];
  selected_option_id: NonEmptyString;
  revision: Revision;
  origin: Origin;
  _expected_failure?: string;
}
