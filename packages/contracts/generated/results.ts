// GENERATED FILE - DO NOT EDIT BY HAND.
// Source of truth: packages/contracts/schemas/v1/results.schema.json
// (+ common, site_fact, study). Regenerate with:
//   python packages/contracts/scripts/generate_ts_types.py
// CI fails if this file diverges from a fresh generation (task C-03).
//
// The answers computed for one option of one study revision.
// Types only: cross-field rules (oneOf/allOf constraints such as rank vs
// source kind) are enforced by the JSON Schema on the server, not here.
export type DateTime = string;
export type NonEmptyString = string;
export interface StreetWidthCase {
  marker: "Needs street width";
  assumptions: {
    street: NonEmptyString;
    assumed: "wide" | "narrow";
    street_width_fact_id: NonEmptyString;
  }[];
  side_by_side_with: NonEmptyString[];
}
export type Unit = "square_feet" | "feet" | "ratio" | "percent" | "stories" | "dwelling_units" | "square_feet_per_dwelling_unit";
export type ZrSection = string;
export interface ValueSource {
  kind: "site_fact" | "rule_table" | "zoning_resolution";
  ref: NonEmptyString;
}
export type ExceptionLabel = ("Needs street width" | "With approvals" | "Out of date" | "Split district" | "Unpermitted work on record") | null;
export interface NotAvailable {
  status: "not_available";
  reason: NonEmptyString;
  reason_kind: "missing_input" | "rule_not_implemented" | "rule_not_reviewed" | "eligibility_unresolved" | "geometry_unsupported";
}
export interface NotApplicable {
  status: "not_applicable";
  reason: NonEmptyString;
}
export type Answer = AnswerAvailable | NotAvailable;
export interface AnswerAvailable {
  status: "available";
  values: AnswerValue[];
  measurement: MeasurementKnown;
}
export interface AnswerValue {
  key: string;
  label: NonEmptyString;
  value: number;
  unit: Unit;
  zr_sections: ZrSection[];
  sources: ValueSource[];
  exception_label: ExceptionLabel;
}
export interface RemainingAvailable {
  status: "available";
  value_sf: number;
  existing_zoning_floor_area_fact_id: NonEmptyString;
}
export interface ShortfallNone {
  status: "none";
}
export interface ShortfallPresent {
  status: "shortfall";
  sq_ft: number;
  reasons: ShortfallReason[];
}
export interface ShortfallReason {
  text: NonEmptyString;
  computed_from: NonEmptyString[];
  values: {
    name: NonEmptyString;
    value: number;
    unit: Unit;
  }[];
}
export interface AddonGain {
  addon_id: NonEmptyString;
  name: NonEmptyString;
  group: "A" | "B" | "C" | "D1";
  on: boolean;
  relative_to: "current_selection";
  requires: NonEmptyString[];
  gain: GainAvailable | NotAvailable;
}
export interface GainAvailable {
  status: "available";
  floor_area_sf: number;
  height_ft: number | null;
  floors: number | null;
}
export interface BestCombinationAvailable {
  status: "available";
  goal: Goal;
  selected_addon_ids: NonEmptyString[];
  excluded: {
    addon_id: NonEmptyString;
    reason: NonEmptyString;
  }[];
  goal_value_sf: number;
}
export type FloorUse = "residential" | "commercial" | "community_facility" | "cellar" | "bulkhead_or_mechanical";
export interface FloorRow {
  floor: number;
  floor_label: NonEmptyString;
  gross_sf: number;
  deductions_sf: number;
  zoning_floor_area_sf: number;
  height_ft: number;
  use: FloorUse;
}
export interface FloorStackAvailable {
  status: "available";
  floors_fit: number;
  height_limit_ft: number;
  levels: {
    floor: number;
    floor_to_floor_ft: number;
    top_of_floor_ft: number;
    allowable_area_sf: number;
  }[];
  zr_sections: ZrSection[];
}
export interface ExistingBuildingNone {
  status: "no_existing_building";
}
export interface ExistingBuildingPresent {
  status: "present";
  paths: {
    keep: PathWithoutBudget;
    partial_rebuild: PathAvailable & {
      rebuild_budget?: {
      };
    } | NotAvailable;
    full_rebuild: PathWithoutBudget;
  };
  partial_rebuild_traps: ("walls_new_development" | "unsafe_condition_75_percent")[];
  exceptions: ("one_or_two_family_house" | "severe_disaster_recovery")[];
  flags: ("rent_regulated_apartments" | "recorded_zoning_lot_documents" | "recorded_vs_zoning_floor_area_gap")[];
  headline: string | null;
  larger_than_allowed_flag: "The existing building is larger than today's zoning allows; demolition would reduce floor area." | null;
}
export type PathWithoutBudget = PathAvailable & {
  rebuild_budget?: null;
} | NotAvailable;
export interface PathAvailable {
  status: "available";
  floor_area_sf: number;
  height_ft: number | null;
  rule: NonEmptyString;
  zr_sections: ZrSection[];
  rebuild_budget: {
    floor_area_sf: number;
    perimeter_wall_ft: number;
  } | null;
}
export interface UnitEstimateAvailable {
  status: "available";
  value: number;
  formula: NonEmptyString;
  factor: {
    value: number;
    unit: "square_feet_per_dwelling_unit";
  };
  rounding_rule: NonEmptyString;
  zr_sections: ZrSection[];
}
export type Point = number[];
export type Ring = Point[];
export type Polygon = Ring[];
export type Line = Point[];
export interface YardRequired {
  kind: "front" | "side" | "rear";
  status: "required";
  depth_ft: number;
  outline: Polygon;
  zr_sections: ZrSection[];
}
export interface YardNotRequired {
  kind: "front" | "side" | "rear";
  status: "not_required";
  reason: NonEmptyString;
  zr_sections: ZrSection[];
}
export interface GeometryAvailable {
  status: "available";
  crs: "local_feet" | "EPSG:2263";
  units: "feet";
  measurement: MeasurementKnown;
  lot_outline: Polygon;
  streets: {
    street: NonEmptyString;
    frontage_line: Line;
    street_width_fact_id: NonEmptyString | null;
  }[];
  yards: {
    status: "available";
    entries: (YardRequired | YardNotRequired)[];
  } | NotAvailable;
  setback_lines_per_level: {
    status: "available";
    entries: {
      floor: number;
      lines: Line[];
      zr_sections: ZrSection[];
    }[];
  } | NotAvailable;
  envelope: {
    status: "available";
    tiers: {
      bottom_ft: number;
      top_ft: number;
      outline: Polygon;
    }[];
  } | NotAvailable;
  floor_plates: {
    status: "available";
    entries: {
      floor: number;
      outline: Polygon;
      gross_sf: number;
      use: FloorUse;
    }[];
  } | NotAvailable;
}
export interface RuleVersion {
  rule_id: NonEmptyString;
  version: NonEmptyString;
  status: "discovered" | "extracted_draft" | "needs_review" | "published";
}
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
export interface Goal {
  kind: "most_residential_floor_area" | "most_total_floor_area" | "other";
  text: NonEmptyString | null;
}
export interface Results {
  contract_version: "1.0.0";
  results_id: NonEmptyString;
  study_id: NonEmptyString;
  option_id: NonEmptyString;
  revision: number;
  computed_at: DateTime;
  out_of_date: boolean;
  out_of_date_reason: NonEmptyString | null;
  depends_on_fact_ids: NonEmptyString[];
  lot_selection_statement: "Based on the lots you selected \u2014 the app does not verify the zoning lot";
  with_approvals_label: "With approvals \u2014 not guaranteed" | null;
  answers: {
    floor_area_allowance: Answer;
    permitted_envelope: Answer;
    building_option: Answer;
  };
  remaining_floor_area: RemainingAvailable | NotAvailable | NotApplicable;
  shortfall: ShortfallNone | ShortfallPresent | NotAvailable;
  addon_gains: AddonGain[];
  best_combination: BestCombinationAvailable | NotAvailable;
  completeness_line: {
    text: NonEmptyString;
    not_yet_covered: NonEmptyString[];
  };
  status_strip: {
    text: NonEmptyString;
  }[];
  notices_count: number;
  floor_by_floor: FloorRow[];
  floor_stack: FloorStackAvailable | NotAvailable;
  existing_building: ExistingBuildingNone | ExistingBuildingPresent | NotAvailable;
  unit_estimate: UnitEstimateAvailable | NotAvailable;
  geometry: GeometryAvailable | NotAvailable;
  rule_versions: RuleVersion[];
  draft: boolean;
  street_width_case: StreetWidthCase | null;
  _expected_failure?: string;
}
