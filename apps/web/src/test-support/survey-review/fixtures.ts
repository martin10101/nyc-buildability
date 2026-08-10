/**
 * Spec-shaped survey-review fixtures for tests ONLY (task M2-T016).
 *
 * Nothing here is imported by application code — the app has no mocked success
 * path. These builders produce `ReviewDocument`s that satisfy the M2-T016
 * read-model (types.ts) and the SURVEY_REVIEW_WORKFLOW contract: two material
 * facts (one clean → accept, one in conflict → correct) and one non-material
 * advisory AI fact (→ reject), plus downstream conclusions that are blocked /
 * provisional on the conflict fact so the honesty surface has something to
 * clear. Values are synthetic and clearly non-official.
 */

import type {
  DocumentState,
  PrincipalCapabilities,
  ReviewDocument,
  ReviewFact,
} from "@/lib/surveyReview/types";

export const FIXTURE_DIGEST = `sha256:${"a".repeat(64)}`;

export type PrincipalProfile = "professional" | "preparer" | "consumer";

const CAPABILITIES: Record<PrincipalProfile, PrincipalCapabilities> = {
  professional: {
    can_view: true,
    can_accept_fact: true,
    can_correct_fact: true,
    can_reject_fact: true,
    can_confirm_document: true,
    can_reject_document: true,
    can_request_reextraction: true,
  },
  preparer: {
    can_view: true,
    can_accept_fact: true,
    can_correct_fact: true,
    can_reject_fact: true,
    can_confirm_document: false,
    can_reject_document: false,
    can_request_reextraction: true,
  },
  consumer: {
    can_view: true,
    can_accept_fact: false,
    can_correct_fact: false,
    can_reject_fact: false,
    can_confirm_document: false,
    can_reject_document: false,
    can_request_reextraction: false,
  },
};

function principalFor(profile: PrincipalProfile) {
  const capabilities = CAPABILITIES[profile];
  if (profile === "professional") {
    return {
      principal_id: "reviewer-001",
      role: "qualified_professional" as const,
      display_name: "Designated professional (fixture)",
      capabilities,
    };
  }
  if (profile === "preparer") {
    return {
      principal_id: "user-001",
      role: "user" as const,
      display_name: "Preparer (fixture)",
      capabilities,
    };
  }
  return {
    principal_id: null,
    role: "user" as const,
    display_name: "Client (read-only fixture)",
    capabilities,
  };
}

function facts(): ReviewFact[] {
  return [
    {
      fact: {
        evidence_id: "sev:doc:p1:1",
        bbl: "1000010010",
        document_digest: FIXTURE_DIGEST,
        page_number: 1,
        location: {
          kind: "bounding_box",
          bounding_box: {
            x_min: 60,
            y_min: 640,
            x_max: 300,
            y_max: 680,
            coordinate_space: "raster_pixels",
          },
        },
        fact_type: "boundary_segment_distance",
        original_value: "120.00'",
        normalized_value: 120,
        units: "feet",
        extraction_method: "vector_object_extraction",
        extracted_at: "2026-07-20T12:00:00Z",
        confidence: 1,
        validation_results: [
          { check_id: "boundary_closure", status: "pass", detail: null },
        ],
        correction_history: [],
        professional_confirmation: { state: "unconfirmed", confirmed_by: null, confirmed_at: null },
      },
      material: true,
      promotion: { evidence_id: "sev:doc:p1:1", allowed: true, refusal_reasons: [] },
      display_label: "Boundary segment distance (north line)",
      ai_drafted_label: false,
      accepted_history_fingerprint: "hist-0",
    },
    {
      fact: {
        evidence_id: "sev:doc:p1:2",
        bbl: "1000010010",
        document_digest: FIXTURE_DIGEST,
        page_number: 1,
        location: {
          kind: "bounding_box",
          bounding_box: {
            x_min: 340,
            y_min: 300,
            x_max: 560,
            y_max: 345,
            coordinate_space: "raster_pixels",
          },
        },
        fact_type: "stated_lot_area",
        original_value: "5,000 SF",
        normalized_value: 5000,
        units: "square_feet",
        extraction_method: "ocr_text",
        extracted_at: "2026-07-20T12:00:00Z",
        confidence: 0.62,
        validation_results: [
          {
            check_id: "area_vs_stated",
            status: "fail",
            detail:
              "The area calculated from the reconstructed boundary diverges from the stated lot area by 200 square feet.",
            expected_value: 5000,
            observed_value: 4800,
          },
        ],
        correction_history: [],
        professional_confirmation: { state: "unconfirmed", confirmed_by: null, confirmed_at: null },
      },
      material: true,
      promotion: {
        evidence_id: "sev:doc:p1:2",
        allowed: false,
        refusal_reasons: [
          "area_vs_stated failed: calculated 4,800 sq ft vs stated 5,000 sq ft.",
        ],
      },
      display_label: "Stated lot area",
      ai_drafted_label: false,
      accepted_history_fingerprint: "hist-0",
    },
    {
      fact: {
        evidence_id: "sev:doc:p1:3",
        bbl: "1000010010",
        document_digest: FIXTURE_DIGEST,
        page_number: 1,
        location: {
          kind: "bounding_box",
          bounding_box: {
            x_min: 500,
            y_min: 60,
            x_max: 560,
            y_max: 130,
            coordinate_space: "raster_pixels",
          },
        },
        fact_type: "north_arrow_orientation",
        original_value: { bearing_deg: 12.5 },
        normalized_value: 12.5,
        units: "degrees",
        extraction_method: "ai_assisted_classification",
        extracted_at: "2026-07-20T12:00:00Z",
        confidence: 0.55,
        validation_results: [
          {
            check_id: "north_orientation",
            status: "unresolved",
            detail: "Could not corroborate the detected north arrow against a second reference.",
          },
        ],
        correction_history: [],
        professional_confirmation: { state: "unconfirmed", confirmed_by: null, confirmed_at: null },
      },
      material: false,
      promotion: { evidence_id: "sev:doc:p1:3", allowed: true, refusal_reasons: [] },
      display_label: "North arrow orientation",
      ai_drafted_label: true,
      accepted_history_fingerprint: "hist-0",
    },
  ];
}

/** Build a fresh needs_review document for the given principal profile. */
export function reviewDocument(
  profile: PrincipalProfile = "professional",
  documentId = "doc-pro",
): ReviewDocument {
  return {
    document_id: documentId,
    document_digest: FIXTURE_DIGEST,
    target_bbl: "1000010010",
    title: "Survey — 140 Carder Road (fixture)",
    state: "needs_review",
    state_history: [
      {
        from_state: null,
        to_state: "uploaded",
        actor_kind: "deterministic_pipeline",
        actor_id: null,
        occurred_at: "2026-07-20T11:59:00Z",
        reason: null,
      },
      {
        from_state: "uploaded",
        to_state: "processing",
        actor_kind: "deterministic_pipeline",
        actor_id: null,
        occurred_at: "2026-07-20T11:59:30Z",
        reason: null,
      },
      {
        from_state: "processing",
        to_state: "needs_review",
        actor_kind: "deterministic_pipeline",
        actor_id: null,
        occurred_at: "2026-07-20T12:00:05Z",
        reason: null,
      },
    ],
    facts: facts(),
    downstream: [
      {
        conclusion_id: "far_max",
        label: "Maximum floor area (FAR basis)",
        status: "blocked",
        blocking_evidence_ids: ["sev:doc:p1:2"],
        explanation:
          "Blocked — needs survey resolution. Cannot be computed until the stated-vs-calculated lot area conflict is resolved. No value is shown.",
        provisional_value: null,
        coverage_status: "professional_review_required",
      },
      {
        conclusion_id: "lot_coverage",
        label: "Maximum lot coverage",
        status: "provisional",
        blocking_evidence_ids: ["sev:doc:p1:2"],
        explanation:
          "Provisional — computed on the assumption that the stated lot area is correct while the area conflict is unresolved. Not a final result.",
        provisional_value: "≤ 60% (assumes stated 5,000 sq ft)",
        coverage_status: "data_conflict",
      },
    ],
    principal: principalFor(profile),
    pages: [
      {
        page_number: 1,
        image_ref: null,
        width: 612,
        height: 792,
        coordinate_space: "raster_pixels",
      },
    ],
    extraction_available: true,
    concurrency_token: "doc-token-0",
  };
}

/** An extraction-unavailable document that honestly rests in `uploaded`. */
export function extractionUnavailableDocument(): ReviewDocument {
  const doc = reviewDocument("professional", "doc-uploaded");
  doc.state = "uploaded";
  doc.extraction_available = false;
  doc.facts = [];
  doc.downstream = [];
  doc.state_history = [doc.state_history[0]];
  return doc;
}

export function inboxEntries() {
  return [
    {
      document_id: "doc-pro",
      title: "Survey — 140 Carder Road (fixture)",
      target_bbl: "1000010010",
      state: "needs_review" as DocumentState,
      open_item_count: 2,
      updated_at: "2026-07-20T12:00:05Z",
    },
  ];
}
