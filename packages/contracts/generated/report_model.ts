// GENERATED FILE - DO NOT EDIT BY HAND.
// Source of truth: packages/contracts/schemas/v1/report_model.schema.json
// (+ common, results, site_fact, study). Regenerate with:
//   python packages/contracts/scripts/generate_ts_types.py
// CI fails if this file diverges from a fresh generation (task C-03).
//
// What every export renders, bound to one results document.
// Types only: cross-field rules (oneOf/allOf constraints such as rank vs
// source kind) are enforced by the JSON Schema on the server, not here.
export type Bbl = string;
export type DateTime = string;
export type DateOnly = string;
export type NonEmptyString = string;
export type DigestSha256 = string;
export interface PointerRef {
  document: "results" | "study" | "report_model";
  pointer: string;
}
export type DisplayValue = {
  status: "available";
  value: number;
  unit: Unit;
  reads: PointerRef;
} | {
  status: "not_available";
  reason: NonEmptyString;
};
export interface CoverSheet {
  page_order: number;
  title: NonEmptyString;
  address: NonEmptyString | null;
  zoning_districts: NonEmptyString[];
  lots: Bbl[];
  floor_area_allowance: DisplayValue;
  maximum_height: DisplayValue;
}
export type DrawingSheet = {
  page_order: number;
  title: NonEmptyString;
  status: "available";
  reads_from: PointerRef[];
  measurement_note: NonEmptyString | null;
} | {
  page_order: number;
  title: NonEmptyString;
  status: "not_available";
  reason: NonEmptyString;
};
export interface TableSheet {
  page_order: number;
  title: NonEmptyString;
  reads_from: PointerRef[];
}
export interface PreliminarySheet {
  page_order: number;
  title: NonEmptyString;
  marking: "Preliminary \u2014 not for filing";
  reads_from: PointerRef[];
}
export interface CalculationRowAvailable {
  row_id: NonEmptyString;
  label: NonEmptyString;
  status: "available";
  value: number | string;
  unit: Unit | null;
  zr_section: ZrSection | null;
  source: NonEmptyString;
  reads: PointerRef;
  exception_label: ExceptionLabel;
}
export interface CalculationRowNotAvailable {
  row_id: NonEmptyString;
  label: NonEmptyString;
  status: "not_available";
  reason: NonEmptyString;
  reads: PointerRef;
}
export type Unit = "square_feet" | "feet" | "ratio" | "percent" | "stories" | "dwelling_units" | "square_feet_per_dwelling_unit";
export type ZrSection = string;
export type ExceptionLabel = ("Needs street width" | "With approvals" | "Out of date" | "Split district" | "Unpermitted work on record") | null;
export interface ReportModel {
  contract_version: "1.0.0";
  report_id: NonEmptyString;
  generated_at: DateTime;
  results_ref: {
    results_id: NonEmptyString;
    study_id: NonEmptyString;
    option_id: NonEmptyString;
    revision: number;
    results_digest: DigestSha256;
  };
  identification_line: {
    option_name: NonEmptyString;
    revision: number;
    date: DateOnly;
    text: string;
  };
  sheets: {
    cover: CoverSheet;
    site_plan: DrawingSheet;
    section: DrawingSheet;
    massing_3d: DrawingSheet;
    calculation_table: TableSheet;
    floor_by_floor_table: TableSheet;
    addon_comparison: TableSheet;
    assumptions: TableSheet;
    dob_style_preliminary?: PreliminarySheet;
  };
  standing_notices: {
    shown_once: true;
    page_order: number;
    not_dob_approval: NonEmptyString;
    floor_area_reminder: "Make sure this floor area is available for use. Confirm with the owner or developer that none of it was sold or merged with another lot.";
    zoning_lot_not_verified: "Based on the lots you selected \u2014 the app does not verify the zoning lot";
    district_incomplete: NonEmptyString | null;
    additional: {
      notice_id: NonEmptyString;
      text: NonEmptyString;
    }[];
  };
  calculation_rows: (CalculationRowAvailable | CalculationRowNotAvailable)[];
  assumptions: {
    assumption_id: NonEmptyString;
    statement: NonEmptyString;
  }[];
  _expected_failure?: string;
}
