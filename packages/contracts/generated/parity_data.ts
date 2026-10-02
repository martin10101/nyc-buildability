// GENERATED FILE - DO NOT EDIT BY HAND.
// Source of truth: packages/contracts/schemas/v1/parity_data.schema.json
// (+ common, site_fact). Regenerate with:
//   python packages/contracts/scripts/generate_ts_types.py
// CI fails if this file diverges from a fresh generation (task C-03).
//
// Parity data: disclosed comparable sales (not a valuation) and unused floor area.
// Types only: cross-field rules (oneOf/allOf constraints such as rank vs
// source kind) are enforced by the JSON Schema on the server, not here.
export type Bbl = string;
export type DateTime = string;
export type NonEmptyString = string;
export interface ComparableSales {
  subject: SubjectSpec;
  criteria: SelectionCriteria;
  criteria_text: NonEmptyString;
  not_a_valuation: "These are recorded sales selected by a simple, disclosed filter, not a valuation or an appraisal. How \"similar type and size\" should be defined is a product choice to confirm with the owner.";
  selected: ComparableSale[];
  excluded: ExcludedCandidate[];
  source: Source | null;
}
export interface SubjectSpec {
  bbl: Bbl | null;
  building_class_category: NonEmptyString | null;
  gross_square_feet: number | null;
}
export interface SelectionCriteria {
  size_tolerance_fraction: number;
  exclude_zero_price: boolean;
  require_recorded_size: boolean;
}
export interface ComparableSale {
  bbl: Bbl | null;
  borough: string | null;
  neighborhood: string | null;
  block: string | null;
  lot: string | null;
  address: string | null;
  zip_code: string | null;
  building_class_category: string | null;
  building_class_at_time_of_sale: string | null;
  residential_units: number | null;
  commercial_units: number | null;
  total_units: number | null;
  year_built: number | null;
  land_square_feet: number | null;
  gross_square_feet: number | null;
  sale_price: number | null;
  sale_date: string | null;
  source: Source | null;
}
export interface ExcludedCandidate {
  bbl: Bbl | null;
  address: string | null;
  sale_date: string | null;
  reason: "subject_lot" | "zero_price_transfer" | "different_building_class_category" | "no_recorded_gross_floor_area" | "gross_floor_area_out_of_range";
}
export interface UnusedFloorArea {
  lot_bbl: Bbl;
  role: "subject" | "neighbor";
  status: "not_confirmed";
  label: "Remaining development capacity: Not confirmed";
  reason: "Needs verified zoning-lot boundaries and existing zoning floor area.";
  existing_floor_area_input: ExistingFloorAreaInput;
  detail: NonEmptyString;
}
export interface ExistingFloorAreaInput {
  known: boolean;
  value_sq_ft: number | null;
  unit: "square_feet" | null;
  measurement: Measurement;
  source: Source | null;
  basis: "certificate_of_occupancy" | "dob_job_filing" | "stated_assumption" | "unknown";
  basis_label: NonEmptyString;
  note: string | null;
}
export type Measurement = MeasurementSurveyEntered | MeasurementCityRecords | MeasurementApproximateTaxMap | MeasurementEntered | MeasurementAssumed | MeasurementUnknown;
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
export interface ParityData {
  contract_version: "1.0.0";
  comparable_sales: ComparableSales;
  unused_floor_area: UnusedFloorArea;
  _expected_failure?: string;
}
