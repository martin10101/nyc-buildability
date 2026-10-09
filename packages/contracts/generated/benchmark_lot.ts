// GENERATED FILE - DO NOT EDIT BY HAND.
// Source of truth: packages/contracts/schemas/v1/benchmark_lot.schema.json
// (+ common, results, site_fact, study). Regenerate with:
//   python packages/contracts/scripts/generate_ts_types.py
// CI fails if this file diverges from a fresh generation (task C-03).
//
// A benchmark, pilot or golden lot with sourced expected values.
// Types only: cross-field rules (oneOf/allOf constraints such as rank vs
// source kind) are enforced by the JSON Schema on the server, not here.
export type Bbl = string;
export type BoroughName = "Manhattan" | "Bronx" | "Brooklyn" | "Queens" | "Staten Island";
export type DateTime = string;
export type DateOnly = string;
export type NonEmptyString = string;
export interface Identity {
  bbls: Bbl[];
  billing_bbl: Bbl | null;
  address: NonEmptyString;
  borough: BoroughName;
  identity_source: NonEmptyString;
}
export type FileSha256 = string;
export type RepoPath = string;
export interface ExpectedValue {
  key: string;
  label: NonEmptyString;
  value: number | string | null;
  unit: Unit | null;
  source: Source;
  verification_state: "expected_unverified" | "recorded" | "reviewed" | "pending" | "pending_owner";
  review: Review | null;
  note: string | null;
}
export interface Source {
  kind: "competitor_review" | "zoning_resolution" | "public_record" | "recorded_fixture" | "pending";
  ref: NonEmptyString;
  sha256: FileSha256 | null;
  pointer: NonEmptyString | null;
  cited_in: NonEmptyString | null;
  quote: NonEmptyString | null;
}
export interface Review {
  reviewer: NonEmptyString;
  reviewed_at: DateTime;
  record_ref: NonEmptyString;
}
export interface Check {
  check_id: "C-1" | "C-2" | "C-3" | "C-4" | "C-5" | "C-6" | "C-7" | "C-8" | "C-9" | "C-10" | "C-11" | "C-12";
  title: NonEmptyString;
  applicability: "applies" | "not_applicable" | "pending";
  reason: NonEmptyString | null;
  pass_when: NonEmptyString | null;
}
export interface RecordedFixture {
  path: RepoPath;
  sha256: FileSha256;
  dataset: NonEmptyString;
  retrieved_at: DateTime | DateOnly | null;
  note: string | null;
}
export interface ReferenceDocument {
  path: RepoPath;
  sha256: FileSha256;
  role: NonEmptyString;
}
export type Unit = "square_feet" | "feet" | "ratio" | "percent" | "stories" | "dwelling_units" | "square_feet_per_dwelling_unit";
export interface BenchmarkLot {
  contract_version: "1.0.0";
  benchmark_id: string;
  purpose: "benchmark" | "pilot" | "multi_lot_pilot";
  basis: NonEmptyString;
  identity: Identity | null;
  expected_values: ExpectedValue[];
  checks: Check[];
  recorded_fixtures: RecordedFixture[];
  reference_documents: ReferenceDocument[];
  open_items: NonEmptyString[];
  _expected_failure?: string;
}
