// GENERATED FILE - DO NOT EDIT BY HAND.
// Source of truth: packages/contracts/schemas/v1/transit_parking.schema.json
// (+ common, site_fact). Regenerate with:
//   python packages/contracts/scripts/generate_ts_types.py
// CI fails if this file diverges from a fresh generation (task C-03).
//
// One lot's transit/parking zone, applied to every option; no parking outcome.
// Types only: cross-field rules (oneOf/allOf constraints such as rank vs
// source kind) are enforced by the JSON Schema on the server, not here.
export type Bbl = string;
export type DateTime = string;
export type NonEmptyString = string;
export interface MissingSourceRef {
  dataset: NonEmptyString;
  dataset_id: NonEmptyString | null;
  publisher: NonEmptyString | null;
  dataset_version: NonEmptyString | null;
  url: string | null;
  components?: {
    dataset: NonEmptyString;
    dataset_id: NonEmptyString;
  }[];
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
export interface TransitParking {
  contract_version: "1.0.0" | "1.1.0";
  lot_bbl: Bbl;
  status: "recorded" | "check_needed";
  status_label: "Recorded" | "Check needed";
  transit_zone: NonEmptyString | null;
  source: Source | null;
  detail: NonEmptyString;
  missing_source: NonEmptyString | null;
  missing_source_ref?: MissingSourceRef | null;
  _expected_failure?: string;
}
