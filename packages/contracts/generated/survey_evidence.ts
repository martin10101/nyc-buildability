// GENERATED FILE - DO NOT EDIT BY HAND.
// Source of truth: packages/contracts/schemas/v1/survey_evidence.schema.json
// (+ common). Regenerate with:
//   python packages/contracts/scripts/generate_ts_types.py
// CI fails if this file diverges from a fresh generation (task M2-T015).
//
// One canonical per-fact survey-evidence contract shared by API, workers,
// and the evidence UI (PRD section 32.3). Document-extracted facts carry
// document/page/location identity (document_digest, page_number,
// location); original_value is immutable, correction_history is
// append-only, and nothing is born professionally confirmed -
// confidence never promotes a value (fail-closed principle).
export type Bbl = string;
export type NonEmptyString = string;
export type DateTime = string;
export type RawBytesDigestSha256 = string;
export interface SurveyEvidence {
  evidence_id: NonEmptyString;
  bbl: Bbl;
  document_digest: RawBytesDigestSha256;
  document_ref?: NonEmptyString;
  page_number: number;
  location: {
    kind: "bounding_box" | "vector_object";
    bounding_box?: {
      x_min: number;
      y_min: number;
      x_max: number;
      y_max: number;
      coordinate_space: "pdf_user_space_points" | "raster_pixels";
    };
    object_reference?: NonEmptyString;
  };
  fact_type: NonEmptyString;
  original_value: unknown;
  normalized_value: unknown;
  units: string | null;
  extraction_method: "vector_object_extraction" | "embedded_text_extraction" | "ocr_text" | "line_symbol_detection" | "ai_assisted_classification" | "deterministic_geometry_reconstruction";
  extraction_tool?: {
    name: NonEmptyString;
    version: NonEmptyString;
  };
  extraction_run_id?: NonEmptyString;
  extracted_at: DateTime;
  confidence: number;
  validation_results: {
    check_id: "address_bbl_match" | "units_consistency" | "scale_consistency" | "north_orientation" | "boundary_closure" | "area_vs_stated" | "segment_sum" | "contradictory_dimensions" | "geometry_validity" | "elevation_consistency" | "tax_lot_geometry_comparison";
    status: "pass" | "fail" | "unresolved";
    detail: string | null;
    expected_value?: unknown;
    observed_value?: unknown;
  }[];
  correction_history: {
    corrected_at: DateTime;
    corrected_by_role: "user" | "qualified_professional";
    corrected_by?: NonEmptyString;
    previous_normalized_value: unknown;
    corrected_normalized_value: unknown;
    previous_units: string | null;
    corrected_units: string | null;
    reason: NonEmptyString;
  }[];
  professional_confirmation: {
    state: "unconfirmed" | "confirmed" | "rejected";
    confirmed_by: string | null;
    confirmed_at: string | null;
    note?: string | null;
  };
}
