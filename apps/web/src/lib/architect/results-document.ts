// Narrow local mirror of the v1 `results` contract
// (packages/contracts/schemas/v1/results.schema.json, contract_version 1.0.0), covering ONLY the
// fields the three-answers panel reads (queue D-05; plan §5 and §5a).
//
// SWITCH TO THE GENERATED TYPE LATER: task C-03 (#258) adds
// packages/contracts/generated/results.ts. It is not on this branch yet, so these declarations
// stand in for it. The names mirror the generated ones (Unit, ExceptionLabel, NotAvailable,
// NotApplicable, AnswerValue, AnswerAvailable, Answer, ShortfallPresent, …) and every field here
// is a structural SUBSET of the generated `Results`, so a generated `Results` value is already
// assignable to `ThreeAnswersResults`; the switch is an import change. Never widen a field here
// beyond the schema.

/** Schema `$defs/unit`. */
export type Unit =
  | "square_feet"
  | "feet"
  | "ratio"
  | "percent"
  | "stories"
  | "dwelling_units"
  | "square_feet_per_dwelling_unit";

/** Schema `$defs/exception_label`: at most ONE exception beside a number (plan §5a item 3). */
export type ExceptionLabel =
  | "Needs street width"
  | "With approvals"
  | "Out of date"
  | "Split district"
  | "Unpermitted work on record"
  | null;

/** Schema `$defs/not_available`: "Not available" with the reason, in place of a number. */
export interface NotAvailable {
  status: "not_available";
  reason: string;
  reason_kind:
    | "missing_input"
    | "rule_not_implemented"
    | "rule_not_reviewed"
    | "eligibility_unresolved"
    | "geometry_unsupported";
}

/** Schema `$defs/not_applicable`. */
export interface NotApplicable {
  status: "not_applicable";
  reason: string;
}

/** Schema `$defs/answer_value` (the `sources` field is not read by the panel). */
export interface AnswerValue {
  key: string;
  label: string;
  value: number;
  unit: Unit;
  zr_sections: readonly string[];
  exception_label: ExceptionLabel;
}

/** Schema `$defs/answer_available`; `measurement` is the weakest input's label (plan §4). */
export interface AnswerAvailable {
  status: "available";
  values: readonly AnswerValue[];
  measurement: { label: string };
}

/** Schema `$defs/answer`. */
export type Answer = AnswerAvailable | NotAvailable;

/** Schema `$defs/remaining_available`. */
export interface RemainingAvailable {
  status: "available";
  value_sf: number;
}

/** Schema `$defs/shortfall_none`. */
export interface ShortfallNone {
  status: "none";
}

/** Schema `$defs/shortfall_present` (only each reason's plain-English text is read). */
export interface ShortfallPresent {
  status: "shortfall";
  sq_ft: number;
  reasons: readonly { text: string }[];
}

/** Schema `$defs/street_width_case` (plan §4 "Needs street width"). */
export interface StreetWidthCase {
  assumptions: readonly { street: string; assumed: "wide" | "narrow" }[];
}

/** The subset of a `results` document the three-answers panel renders. */
export interface ThreeAnswersResults {
  out_of_date: boolean;
  out_of_date_reason: string | null;
  lot_selection_statement: string;
  with_approvals_label: string | null;
  answers: {
    floor_area_allowance: Answer;
    permitted_envelope: Answer;
    building_option: Answer;
  };
  remaining_floor_area: RemainingAvailable | NotAvailable | NotApplicable;
  shortfall: ShortfallNone | ShortfallPresent | NotAvailable;
  completeness_line: { text: string; not_yet_covered: readonly string[] };
  status_strip: readonly { text: string }[];
  notices_count: number;
  draft: boolean;
  street_width_case: StreetWidthCase | null;
}
