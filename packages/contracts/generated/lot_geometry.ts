// GENERATED FILE - DO NOT EDIT BY HAND.
// Source of truth: packages/contracts/schemas/v1/lot_geometry.schema.json
// (+ common). Emitted by the repo generator's shared emission functions
// (packages/contracts/scripts/generate_ts_types.py) for task M5-T020. Wiring
// a generate_lot_geometry()/check_lot_geometry() entrypoint + CI drift check
// into that script is a documented follow-up (M5-T020 producer report).
//
// One canonical DISPLAY-ONLY lot-outline contract shared by the API and the
// web map (PRD section 32.3). The geometry is EPSG:4326 GeoJSON TRANSPORT FOR
// DISPLAY ONLY - no area/dimension is ever derived from it; the authoritative
// EPSG:2263 path owns all measurement. Coordinates are [longitude, latitude]
// verbatim from the official NYC DCP MapPLUTO feature service.
export type Bbl = string;
export type NonEmptyString = string;
export type DateTime = string;
export type LngLatPosition = number[];
export type LinearRing = LngLatPosition[];
export interface PolygonGeometry {
  type: "Polygon";
  coordinates: LinearRing[];
}
export interface MultiPolygonGeometry {
  type: "MultiPolygon";
  coordinates: LinearRing[][];
}
export type OutlineGeometry = PolygonGeometry | MultiPolygonGeometry | null;
export interface CondoClassification {
  classification: "standard_lot" | "condo_billing_lot" | "condo_unit_lot_query";
  condo_no: number | null;
  note: NonEmptyString | null;
}
export interface LotIdentity {
  boro_code: number | null;
  borough: string | null;
  block: number | null;
  lot: number | null;
  condo_no: number | null;
}
export interface LotOutlineSource {
  source_id: "nyc-dcp-mappluto-arcgis";
  service_root: NonEmptyString;
  layer: NonEmptyString;
  endpoint: NonEmptyString;
  dataset_version: NonEmptyString | null;
  retrieved_at: DateTime;
}
export interface LotGeometry {
  contract_version: "1.0.0";
  document_kind: "lot_outline";
  bbl: Bbl;
  outcome: "single_lot" | "no_outline" | "multiple_features" | "invalid_geometry";
  display_only: true;
  crs: "EPSG:4326";
  geometry: OutlineGeometry;
  feature_count: number;
  review_required: boolean;
  no_outline_reason: ("condo_unit_lot_no_polygon" | "no_feature_for_bbl") | null;
  condo_classification: CondoClassification;
  lot_identity: LotIdentity | null;
  source: LotOutlineSource;
  accuracy_note: NonEmptyString;
  attribution: NonEmptyString;
  disclaimer: NonEmptyString;
  notes: string[];
  _expected_failure?: string;
}
