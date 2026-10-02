// GENERATED FILE - DO NOT EDIT BY HAND.
// Source of truth: packages/contracts/schemas/v1/hidden_issue_flags.schema.json
// (+ common, site_fact). Regenerate with:
//   python packages/contracts/scripts/generate_ts_types.py
// CI fails if this file diverges from a fresh generation (task C-03).
//
// The §8a hidden-issue flag groups: flag, opportunity or 'Check needed'.
// Types only: cross-field rules (oneOf/allOf constraints such as rank vs
// source kind) are enforced by the JSON Schema on the server, not here.
export type Bbl = string;
export type DateTime = string;
export type NonEmptyString = string;
export interface FlagGroup {
  group_id: "existing_building" | "zoning_lot_history" | "map_based_rules" | "site_shape_and_street";
  title: NonEmptyString;
  lot_bbl: Bbl;
  flags: Flag[];
}
export interface Flag {
  item_id: NonEmptyString;
  group: "existing_building" | "zoning_lot_history" | "map_based_rules" | "site_shape_and_street";
  title: NonEmptyString;
  status: "flag" | "opportunity" | "check_needed" | "not_flagged";
  status_label: "Flag" | "Opportunity" | "Check needed" | "No flag";
  detail: NonEmptyString;
  typical_source: NonEmptyString;
  evidence: EvidenceItem[];
  fact_refs: NonEmptyString[];
  exception_label: NonEmptyString | null;
  phase: NonEmptyString;
}
export interface EvidenceItem {
  label: NonEmptyString;
  source: Source | EngineProvenance | null;
}
export interface EngineProvenance {
  kind?: NonEmptyString;
  statement?: NonEmptyString;
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
export interface HiddenIssueFlags {
  contract_version: "1.0.0";
  groups: FlagGroup[];
  _expected_failure?: string;
}
