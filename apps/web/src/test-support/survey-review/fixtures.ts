/**
 * Backend-shaped survey-review fixtures for tests ONLY (task M2-T016 rework).
 *
 * These build `DocumentReviewView`-shaped documents (the shipped backend read
 * model) keyed by `document_digest` = `sha256:<64hex>`. Three material facts:
 * one clean (→ accept), one in conflict (→ correct), one unresolved advisory-AI
 * detection (→ reject or correct). Derived fields (`promotable`,
 * `downstream_impact`, `blocking_fact_ids`, `confirm_precondition_met`,
 * `is_unconfirmed_evidence`) are (re)computed by the mock reducer to match the
 * backend, so fixtures only set the raw check counts + confirmation state.
 *
 * Uses only type imports from the app (erased at transpile) so it is e2e-safe.
 * Not shipped: application code never imports this module.
 */

import type {
  ConfirmationState,
  CorrectionEntry,
  DocumentState,
  DownstreamImpact,
  EvidenceLocation,
  ExtractionMethod,
  PrincipalCapabilities,
  TransitionRecord,
} from "@/lib/surveyReview/types";

export const DIGEST_PRO = `sha256:${"a".repeat(64)}`;
export const DIGEST_USER = `sha256:${"b".repeat(64)}`;
export const DIGEST_UPLOADED = `sha256:${"d".repeat(64)}`;

export type PrincipalProfile = "professional" | "preparer";

export interface MockFact {
  evidence_id: string;
  fact_type: string;
  original_value: unknown;
  baseline_normalized_value: unknown;
  baseline_units: string | null;
  normalized_value: unknown;
  units: string | null;
  confirmation_state: ConfirmationState;
  confirmation_note: string | null;
  correction_history: CorrectionEntry[];
  correction_count: number;
  check_pass: number;
  check_fail: number;
  check_unresolved: number;
  location: EvidenceLocation | null;
  page_number: number | null;
  extraction_method: ExtractionMethod | null;
  is_unconfirmed_evidence: boolean;
  promotable: boolean;
  downstream_impact: DownstreamImpact | null;
  /** Mock-only marker (never serialised in the read). */
  _material: boolean;
}

export interface MockPrincipal {
  principal_id: string | null;
  role: "user" | "qualified_professional";
  display_name: string;
  capabilities: PrincipalCapabilities;
}

export interface MockDoc {
  document_digest: string;
  target_bbl: string;
  title: string;
  state: DocumentState;
  state_history: TransitionRecord[];
  facts: MockFact[];
  confirm_precondition_met: boolean;
  blocking_fact_ids: string[];
  original_available: boolean;
  principal: MockPrincipal;
}

const CAPABILITIES: Record<PrincipalProfile, PrincipalCapabilities> = {
  professional: {
    can_view: true,
    can_accept_fact: true,
    can_correct_fact: true,
    can_reject_fact: true,
    can_confirm_document: true,
    can_reject_document: true,
    can_reopen_document: true,
  },
  // reject_fact is professional-only in the shipped slice; a preparer (human_user)
  // may accept/correct but not reject a fact or take any document decision.
  preparer: {
    can_view: true,
    can_accept_fact: true,
    can_correct_fact: true,
    can_reject_fact: false,
    can_confirm_document: false,
    can_reject_document: false,
    can_reopen_document: false,
  },
};

function principalFor(profile: PrincipalProfile): MockPrincipal {
  if (profile === "professional") {
    return {
      principal_id: "reviewer-001",
      role: "qualified_professional",
      display_name: "Designated professional (fixture)",
      capabilities: CAPABILITIES.professional,
    };
  }
  return {
    principal_id: "user-001",
    role: "user",
    display_name: "Preparer (fixture)",
    capabilities: CAPABILITIES.preparer,
  };
}

function facts(): MockFact[] {
  const shared = {
    correction_history: [] as CorrectionEntry[],
    correction_count: 0,
    confirmation_note: null,
    is_unconfirmed_evidence: true,
    promotable: false,
    downstream_impact: null as DownstreamImpact | null,
    _material: true,
  };
  return [
    {
      ...shared,
      evidence_id: "sev:doc:p1:1",
      fact_type: "boundary_segment_distance",
      original_value: "120.00'",
      baseline_normalized_value: 120,
      baseline_units: "feet",
      normalized_value: 120,
      units: "feet",
      confirmation_state: "unconfirmed",
      check_pass: 1,
      check_fail: 0,
      check_unresolved: 0,
      location: {
        kind: "bounding_box",
        bounding_box: { x_min: 60, y_min: 640, x_max: 300, y_max: 680, coordinate_space: "raster_pixels" },
      },
      page_number: 1,
      extraction_method: "vector_object_extraction",
    },
    {
      ...shared,
      correction_history: [],
      evidence_id: "sev:doc:p1:2",
      fact_type: "stated_lot_area",
      original_value: "5,000 SF",
      baseline_normalized_value: 5000,
      baseline_units: "square_feet",
      normalized_value: 5000,
      units: "square_feet",
      confirmation_state: "unconfirmed",
      check_pass: 0,
      check_fail: 1,
      check_unresolved: 0,
      location: {
        kind: "bounding_box",
        bounding_box: { x_min: 340, y_min: 300, x_max: 560, y_max: 345, coordinate_space: "raster_pixels" },
      },
      page_number: 1,
      extraction_method: "ocr_text",
    },
    {
      ...shared,
      correction_history: [],
      evidence_id: "sev:doc:p1:3",
      fact_type: "north_arrow_orientation",
      original_value: { bearing_deg: 12.5 },
      baseline_normalized_value: 12.5,
      baseline_units: "degrees",
      normalized_value: 12.5,
      units: "degrees",
      confirmation_state: "unconfirmed",
      check_pass: 0,
      check_fail: 0,
      check_unresolved: 1,
      location: {
        kind: "bounding_box",
        bounding_box: { x_min: 500, y_min: 60, x_max: 560, y_max: 130, coordinate_space: "raster_pixels" },
      },
      page_number: 1,
      extraction_method: "ai_assisted_classification",
    },
  ];
}

function stateHistory(): TransitionRecord[] {
  return [
    { from_state: null, to_state: "uploaded", actor_kind: "deterministic_pipeline", actor_id: null, occurred_at: "2026-07-20T11:59:00Z", reason: null },
    { from_state: "uploaded", to_state: "processing", actor_kind: "deterministic_pipeline", actor_id: null, occurred_at: "2026-07-20T11:59:30Z", reason: null },
    { from_state: "processing", to_state: "needs_review", actor_kind: "deterministic_pipeline", actor_id: null, occurred_at: "2026-07-20T12:00:05Z", reason: null },
  ];
}

export function reviewDoc(profile: PrincipalProfile, digest: string): MockDoc {
  return {
    document_digest: digest,
    target_bbl: "1000010010",
    title: "Survey — 140 Carder Road (fixture)",
    state: "needs_review",
    state_history: stateHistory(),
    facts: facts(),
    confirm_precondition_met: false,
    blocking_fact_ids: [],
    original_available: true,
    principal: principalFor(profile),
  };
}

export function uploadedDoc(): MockDoc {
  return {
    document_digest: DIGEST_UPLOADED,
    target_bbl: "1000010010",
    title: "Survey — pending extraction (fixture)",
    state: "uploaded",
    state_history: [stateHistory()[0]],
    facts: [],
    confirm_precondition_met: false,
    blocking_fact_ids: [],
    original_available: true,
    principal: principalFor("professional"),
  };
}
