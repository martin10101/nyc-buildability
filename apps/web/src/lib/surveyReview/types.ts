/**
 * Survey-review API-client SEAM — types (task M2-T016, Packet C).
 *
 * This module is the SINGLE typed contract every survey-review component
 * depends on. No component issues a raw fetch; they all speak `SurveyReviewClient`
 * (see ./api.ts). The types below mirror, verbatim where they overlap:
 *
 *   - the six document lifecycle states (`DocumentState`) 1:1 with the shipped
 *     `services/api/app/documents/state.py` `DocumentState` wire strings;
 *   - the per-fact `survey_evidence` contract
 *     (packages/contracts/schemas/v1/survey_evidence.schema.json 1.0.0);
 *   - the two state layers, the professional-confirmation MECHANISM, the
 *     append-only correction model, the H5 promotion gate, and the downstream
 *     honesty surface described in docs/SURVEY_REVIEW_WORKFLOW.md.
 *
 * HONESTY BOUNDARIES ENCODED IN THE TYPES:
 *   - There is NO "verified" confirmation state and NO automatic path to
 *     `professionally_confirmed`. A fact is born `unconfirmed`; only the
 *     capability-gated professional action (never a confidence score, never a
 *     passing check) can change that — and even the capability is server-derived.
 *   - `original_value` is read-only forever; corrections are additive
 *     `CorrectionEntry` rows, never a mutation.
 *   - The H5 promotion verdict (`PromotionVerdict`) is CONSUMED from the
 *     backend, never computed in React (CLAUDE.md principle 1: deterministic
 *     code calculates; the UI mirrors).
 *
 * The concrete license/designation that qualifies as the confirming
 * professional is a pending owner / qualified-human decision (workflow §5.5).
 * The UI therefore gates the confirm action on the server-supplied
 * `capabilities.can_confirm_document` flag and NEVER on a hardcoded role string.
 */

/** Any JSON value — `original_value`/`normalized_value` are open by contract. */
export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue };

// ---------------------------------------------------------------------------
// Two state layers (workflow §2)
// ---------------------------------------------------------------------------

/** Layer A — document lifecycle. 1:1 wire strings with backend `DocumentState`. */
export type DocumentState =
  | "uploaded"
  | "processing"
  | "auto_extracted"
  | "needs_review"
  | "rejected"
  | "professionally_confirmed";

/** Layer B — per-fact confirmation (`ProfessionalConfirmationState`). */
export type ConfirmationState = "unconfirmed" | "confirmed" | "rejected";

// ---------------------------------------------------------------------------
// Per-fact evidence — mirrors survey_evidence.schema.json 1.0.0
// ---------------------------------------------------------------------------

export type CorrectingRole = "user" | "qualified_professional";

export type ExtractionMethod =
  | "vector_object_extraction"
  | "embedded_text_extraction"
  | "ocr_text"
  | "line_symbol_detection"
  | "ai_assisted_classification"
  | "deterministic_geometry_reconstruction";

export type CheckId =
  | "address_bbl_match"
  | "units_consistency"
  | "scale_consistency"
  | "north_orientation"
  | "boundary_closure"
  | "area_vs_stated"
  | "segment_sum"
  | "contradictory_dimensions"
  | "geometry_validity"
  | "elevation_consistency"
  | "tax_lot_geometry_comparison";

export type CheckStatus = "pass" | "fail" | "unresolved";

export type CoordinateSpace = "pdf_user_space_points" | "raster_pixels";

export interface BoundingBox {
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
  coordinate_space: CoordinateSpace;
}

export interface EvidenceLocation {
  kind: "bounding_box" | "vector_object";
  bounding_box?: BoundingBox;
  object_reference?: string;
}

export interface ValidationResult {
  check_id: CheckId;
  status: CheckStatus;
  /** null ONLY on `pass`; every fail/unresolved states why (contract). */
  detail: string | null;
  /** Comparison basis (e.g. stated area) so a conflict is reproducible. */
  expected_value?: JsonValue;
  /** Computed/observed value (e.g. calculated polygon area, closure gap). */
  observed_value?: JsonValue;
}

/** One append-only correction row (workflow §6.2). Never edited or deleted. */
export interface CorrectionEntry {
  corrected_at: string;
  corrected_by_role: CorrectingRole;
  /** Required when role is `qualified_professional`; optional otherwise. */
  corrected_by?: string;
  previous_normalized_value: JsonValue;
  corrected_normalized_value: JsonValue;
  previous_units: string | null;
  corrected_units: string | null;
  reason: string;
}

export interface ProfessionalConfirmation {
  state: ConfirmationState;
  /** null exactly while `unconfirmed`. */
  confirmed_by: string | null;
  /** null exactly while `unconfirmed`. */
  confirmed_at: string | null;
  note?: string | null;
}

export interface SurveyEvidenceFact {
  evidence_id: string;
  bbl: string;
  document_digest: string;
  document_ref?: string;
  page_number: number;
  location: EvidenceLocation;
  fact_type: string;
  /** IMMUTABLE verbatim detection. Never touched by a correction (SC-S2). */
  original_value: JsonValue;
  /** Current (post-correction) normalized value. */
  normalized_value: JsonValue;
  /** REQUIRED; explicitly null when unitless. */
  units: string | null;
  extraction_method: ExtractionMethod;
  extraction_run_id?: string;
  extracted_at: string;
  /** 0..1. Confidence NEVER promotes a value (fail-closed). */
  confidence: number;
  validation_results: ValidationResult[];
  correction_history: CorrectionEntry[];
  professional_confirmation: ProfessionalConfirmation;
}

// ---------------------------------------------------------------------------
// Review read-model additions (produced by the review read endpoint;
// NOT part of the per-fact evidence contract)
// ---------------------------------------------------------------------------

/**
 * Deterministic H5 promotion verdict for one material fact (workflow §4.3).
 * CONSUMED from the backend — the UI only reads `allowed` to decide whether to
 * OFFER the confirm action; it never derives the verdict itself, and the
 * backend re-enforces the gate regardless of what the UI offered.
 */
export interface PromotionVerdict {
  evidence_id: string;
  allowed: boolean;
  /** When refused: plain-language reasons (unresolved/failed checks). */
  refusal_reasons: string[];
}

/** A material fact plus its review-derived annotations. */
export interface ReviewFact {
  fact: SurveyEvidenceFact;
  /** Whether this fact gates promotion / conditions a downstream conclusion. */
  material: boolean;
  promotion: PromotionVerdict;
  /** Human-facing label for `fact_type`. */
  display_label: string;
  /** True when `display_label` is an AI-suggested label (marked in the UI). */
  ai_drafted_label: boolean;
  /**
   * Optimistic-concurrency fingerprint of this fact's ACCEPTED correction
   * history (workflow §6.3). Echoed on correct/reject; a stale value is
   * refused with `stale_history` so no concurrent edit is silently lost.
   */
  accepted_history_fingerprint: string;
}

export type TransitionActorKind = "deterministic_pipeline" | "qualified_human";

/** One append-only document lifecycle transition (workflow §8.1). */
export interface TransitionRecord {
  from_state: DocumentState | null;
  to_state: DocumentState;
  actor_kind: TransitionActorKind;
  /** Required for `qualified_human` edges; null for pipeline. */
  actor_id: string | null;
  occurred_at: string;
  /** Non-null for the reason-required edges (2,3,6,11,12). */
  reason: string | null;
}

/** Downstream buildability-conclusion honesty status (workflow §7, §9.2). */
export type DownstreamStatus =
  | "blocked"
  | "provisional"
  | "recalculating"
  | "cleared";

export interface DownstreamConclusion {
  conclusion_id: string;
  /** Plain-language name of the buildability conclusion. */
  label: string;
  status: DownstreamStatus;
  /** Evidence facts (by `evidence_id`) that block/condition this conclusion. */
  blocking_evidence_ids: string[];
  /** Plain-language explanation; provisional states its assumption. */
  explanation: string;
  /** Provisional value, clearly labeled as not final; null when blocked. */
  provisional_value?: string | null;
  /** Honest coverage status — NEVER `verified` while survey evidence is open. */
  coverage_status: "professional_review_required" | "data_conflict";
}

export type PrincipalRole = "user" | "qualified_professional";

/**
 * Server-derived per-action authority (workflow §5.2). The UI MIRRORS these to
 * disable unavailable actions with a plain-language reason; the server is the
 * enforcement point. `can_confirm_document` encodes the pending owner-decided
 * qualified-professional binding (§5.5) — the UI never hardcodes a role.
 */
export interface PrincipalCapabilities {
  can_view: boolean;
  can_accept_fact: boolean;
  can_correct_fact: boolean;
  can_reject_fact: boolean;
  can_confirm_document: boolean;
  can_reject_document: boolean;
  can_request_reextraction: boolean;
}

export interface ReviewPrincipal {
  /** null while the B-001 identity/licensure directory is unprovisioned. */
  principal_id: string | null;
  role: PrincipalRole;
  display_name: string;
  capabilities: PrincipalCapabilities;
}

export interface ReviewPage {
  page_number: number;
  /** Rendered original-page image ref; null when extraction is unavailable. */
  image_ref: string | null;
  width: number | null;
  height: number | null;
  coordinate_space: CoordinateSpace | null;
}

/** The full review read-model for one document. */
export interface ReviewDocument {
  document_id: string;
  document_digest: string;
  target_bbl: string;
  title: string;
  state: DocumentState;
  state_history: TransitionRecord[];
  facts: ReviewFact[];
  downstream: DownstreamConclusion[];
  principal: ReviewPrincipal;
  pages: ReviewPage[];
  /** §11 parser-isolation honesty: false ⇒ rests in `uploaded`, no overlay. */
  extraction_available: boolean;
  /** Document-level optimistic-concurrency token. */
  concurrency_token: string;
}

/** One inbox row (workflow §3.1 Review inbox). */
export interface InboxEntry {
  document_id: string;
  title: string;
  target_bbl: string;
  state: DocumentState;
  /** Count of material facts still needing a decision. */
  open_item_count: number;
  updated_at: string;
}

// ---------------------------------------------------------------------------
// Request payloads
// ---------------------------------------------------------------------------

export interface AcceptFactRequest {
  documentId: string;
  evidenceId: string;
}

export interface CorrectFactRequest {
  documentId: string;
  evidenceId: string;
  corrected_normalized_value: JsonValue;
  corrected_units: string | null;
  /** Non-empty required reason (§6.2). */
  reason: string;
  /** Echo of `ReviewFact.accepted_history_fingerprint` (§6.3). */
  accepted_history_fingerprint: string;
}

export interface RejectFactRequest {
  documentId: string;
  evidenceId: string;
  /** Non-empty required reason. */
  reason: string;
}

export interface RejectDocumentRequest {
  documentId: string;
  /** Non-empty required reason (edge 11). */
  reason: string;
}

export interface ConfirmDocumentRequest {
  documentId: string;
}

export interface RequestReExtractionRequest {
  documentId: string;
}

// ---------------------------------------------------------------------------
// Typed error + outcome unions (mirrors src/lib/api.ts discipline)
// ---------------------------------------------------------------------------

/** Machine-readable refusal codes — the shipped typed backend errors. */
export type ReviewRejectCode =
  | "unauthorized"
  | "illegal_transition"
  | "unauthorized_transition_actor"
  | "transition_reason_required"
  | "promotion_gate_unmet"
  | "correction_tampered"
  | "correction_chain_mismatch"
  | "correction_no_op"
  | "correction_reason_required"
  | "stale_history"
  | "not_found"
  | "validation_error";

export interface ReviewActionError {
  kind: "error";
  reject_code: ReviewRejectCode;
  /** Bounded server text; the UI maps the code to plain-language copy. */
  message: string;
  correlationId: string | null;
  /**
   * For `stale_history`: the CURRENT document so the reviewer can re-open the
   * live state without losing their unsaved input (workflow §6.3, §10.8).
   */
  currentDocument?: ReviewDocument;
}

/** Browser-level failure: server unreachable, DNS, connection refused. */
export interface NetworkErrorOutcome {
  kind: "network_error";
  message: string;
}

/** The client-side request budget elapsed; recoverable via retry. */
export interface ClientTimeoutOutcome {
  kind: "client_timeout";
  timeoutMs: number;
}

/** The request was cancelled because a newer request superseded it. */
export interface AbortedOutcome {
  kind: "aborted";
}

/** A response outside the documented shape/status matrix. */
export interface UnexpectedResponseOutcome {
  kind: "unexpected_response";
  httpStatus: number;
  correlationId: string | null;
}

/** A 2xx body that failed CLIENT-side structural validation. */
export interface ValidationFailureOutcome {
  kind: "validation_failure";
  problems: string[];
  correlationId: string | null;
}

export interface ReadDocumentSuccess {
  kind: "document";
  document: ReviewDocument;
  correlationId: string | null;
}

export interface NotFoundOutcome {
  kind: "not_found";
  message: string;
  correlationId: string | null;
}

export interface UnauthorizedOutcome {
  kind: "unauthorized";
  message: string;
  correlationId: string | null;
}

export type ReadDocumentOutcome =
  | ReadDocumentSuccess
  | NotFoundOutcome
  | UnauthorizedOutcome
  | NetworkErrorOutcome
  | ClientTimeoutOutcome
  | AbortedOutcome
  | UnexpectedResponseOutcome
  | ValidationFailureOutcome;

export interface InboxSuccess {
  kind: "inbox";
  entries: InboxEntry[];
  correlationId: string | null;
}

export type InboxOutcome =
  | InboxSuccess
  | UnauthorizedOutcome
  | NetworkErrorOutcome
  | ClientTimeoutOutcome
  | AbortedOutcome
  | UnexpectedResponseOutcome
  | ValidationFailureOutcome;

export interface ActionSuccess {
  kind: "updated";
  /** Fresh read-model after the action (state, facts, downstream all settled). */
  document: ReviewDocument;
  correlationId: string | null;
}

export type ActionOutcome =
  | ActionSuccess
  | ReviewActionError
  | NetworkErrorOutcome
  | ClientTimeoutOutcome
  | AbortedOutcome
  | UnexpectedResponseOutcome
  | ValidationFailureOutcome;

export interface RequestOptions {
  /** Injection point for tests; defaults to the global fetch. */
  fetchImpl?: typeof fetch;
  /** External cancellation (supersession, unmount). */
  signal?: AbortSignal;
  timeoutMs?: number;
}

// ---------------------------------------------------------------------------
// The client interface — the ONE seam the orchestrator reconciles
// ---------------------------------------------------------------------------

export interface SurveyReviewClient {
  readDocument(
    documentId: string,
    options?: RequestOptions,
  ): Promise<ReadDocumentOutcome>;
  listInbox(
    state?: DocumentState,
    options?: RequestOptions,
  ): Promise<InboxOutcome>;
  acceptFact(req: AcceptFactRequest, options?: RequestOptions): Promise<ActionOutcome>;
  correctFact(req: CorrectFactRequest, options?: RequestOptions): Promise<ActionOutcome>;
  rejectFact(req: RejectFactRequest, options?: RequestOptions): Promise<ActionOutcome>;
  rejectDocument(
    req: RejectDocumentRequest,
    options?: RequestOptions,
  ): Promise<ActionOutcome>;
  confirmDocument(
    req: ConfirmDocumentRequest,
    options?: RequestOptions,
  ): Promise<ActionOutcome>;
  requestReExtraction(
    req: RequestReExtractionRequest,
    options?: RequestOptions,
  ): Promise<ActionOutcome>;
}
