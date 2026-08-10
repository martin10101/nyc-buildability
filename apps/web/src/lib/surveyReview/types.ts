/**
 * Survey-review API-client SEAM — types (task M2-T016, Packet C; reconciled to
 * the shipped backend slice `services/api/app/documents/review_actions.py`,
 * contract in `project-control/reports/M2-T016-backend-return.md`).
 *
 * The SINGLE typed contract every survey-review component depends on. No
 * component issues a raw fetch; they all speak `SurveyReviewClient` (./api.ts).
 * The read model mirrors the backend `DocumentReviewView`/`FactView` field names
 * 1:1; a few fields the backend read does NOT yet return are CLIENT-DERIVED or
 * AWAITING-BACKEND and are marked as such below (never fabricated as if
 * authoritative).
 *
 * Honesty boundaries encoded here (validated by the review, preserved):
 *   - No "verified" confirmation state; no automatic path to
 *     `professionally_confirmed`. A fact is born `unconfirmed`.
 *   - The confirm precondition is CONSUMED from the backend
 *     (`confirm_precondition_met` + `blocking_fact_ids`), never computed in React.
 *   - `original_value`/`baseline_*` are read-only; corrections are additive
 *     `CorrectionEntry` rows.
 *
 * Keying: every action is keyed on the `document_digest` = `sha256:<64hex>`
 * (URL-encode the colon). Re-extraction-as-new-upload is a separate pipeline
 * concern; the post-confirmation contradiction path is `reopen` (edge 12).
 */

export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue };

// ---------------------------------------------------------------------------
// Enums (1:1 wire strings with the backend)
// ---------------------------------------------------------------------------

export type DocumentState =
  | "uploaded"
  | "processing"
  | "auto_extracted"
  | "needs_review"
  | "rejected"
  | "professionally_confirmed";

export type ConfirmationState = "unconfirmed" | "confirmed" | "rejected";

export type CorrectingRole = "user" | "qualified_professional";

export type ExtractionMethod =
  | "vector_object_extraction"
  | "embedded_text_extraction"
  | "ocr_text"
  | "line_symbol_detection"
  | "ai_assisted_classification"
  | "deterministic_geometry_reconstruction";

export type CoordinateSpace = "pdf_user_space_points" | "raster_pixels";

export type DownstreamImpactKind = "blocked" | "provisional";

export type SurveyCoverageStatus = "professional_review_required" | "data_conflict";

// ---------------------------------------------------------------------------
// Shared shapes
// ---------------------------------------------------------------------------

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

/** One append-only correction row (backend `correction_history` entry). */
export interface CorrectionEntry {
  corrected_at: string;
  corrected_by_role: CorrectingRole;
  corrected_by?: string;
  previous_normalized_value: JsonValue;
  corrected_normalized_value: JsonValue;
  previous_units: string | null;
  corrected_units: string | null;
  reason: string;
}

/** Per-fact honest downstream consequence (backend `DownstreamImpact`). */
export interface DownstreamImpact {
  impact_kind: DownstreamImpactKind;
  coverage_status: SurveyCoverageStatus;
  reason: string;
  provenance_digest: string;
  provenance_evidence_ids: string[];
  /** Criticality — left null by the backend (decided by the profile consumer). */
  analysis_readiness: string | null;
}

export type TransitionActorKind = "deterministic_pipeline" | "qualified_human";

export interface TransitionRecord {
  from_state: DocumentState | null;
  to_state: DocumentState;
  actor_kind: TransitionActorKind;
  actor_id: string | null;
  occurred_at: string;
  reason: string | null;
}

// ---------------------------------------------------------------------------
// FactView — mirrors backend FactView (flat), plus client-derived fields
// ---------------------------------------------------------------------------

export interface FactView {
  // ---- from backend FactView ----
  evidence_id: string;
  fact_type: string;
  original_value: JsonValue;
  baseline_normalized_value: JsonValue;
  baseline_units: string | null;
  normalized_value: JsonValue;
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

  // ---- CLIENT-DERIVED / AWAITING-BACKEND (documented; never authoritative) ----
  /** AWAITING-BACKEND: `FactView` has no label; the client humanises `fact_type`. */
  display_label: string;
  /** AWAITING-BACKEND: no AI-drafted-label signal yet; defaults false. */
  ai_drafted_label: boolean;
  /**
   * CLIENT-DERIVED optimistic-concurrency token = `history_fingerprint` of
   * `correction_history` at read time (see ./fingerprint.ts). Echoed on correct;
   * a stale value is safely refused with `concurrent_review_modification`.
   */
  accepted_history_fingerprint: string;
}

// ---------------------------------------------------------------------------
// Principal / capabilities (AWAITING-BACKEND capability surface)
// ---------------------------------------------------------------------------

export type PrincipalRole = "user" | "qualified_professional";

export interface PrincipalCapabilities {
  can_view: boolean;
  can_accept_fact: boolean;
  can_correct_fact: boolean;
  can_reject_fact: boolean;
  can_confirm_document: boolean;
  can_reject_document: boolean;
  can_reopen_document: boolean;
}

export interface ReviewPrincipal {
  principal_id: string | null;
  role: PrincipalRole;
  display_name: string;
  capabilities: PrincipalCapabilities;
  /**
   * AWAITING-BACKEND: the review read does not yet return the principal's
   * capabilities. When false, the UI shows actions enabled and relies on the
   * server's typed `unauthorized_review_action` refusal (mirrored to plain
   * language) instead of pre-disabling — degrade honestly, never fabricate.
   */
  capabilities_known: boolean;
}

export interface ReviewPage {
  page_number: number;
  image_ref: string | null;
  width: number | null;
  height: number | null;
  coordinate_space: CoordinateSpace | null;
}

// ---------------------------------------------------------------------------
// ReviewDocument — backend DocumentReviewView + client-derived fields
// ---------------------------------------------------------------------------

export interface ReviewDocument {
  // ---- from backend DocumentReviewView ----
  document_digest: string;
  target_bbl: string;
  state: DocumentState;
  state_history: TransitionRecord[];
  facts: FactView[];
  /** H5 precondition — CONSUMED, never computed in React. */
  confirm_precondition_met: boolean;
  blocking_fact_ids: string[];
  original_available: boolean;
  correlation_id: string | null;

  // ---- CLIENT-DERIVED / AWAITING-BACKEND ----
  /** AWAITING-BACKEND: no document title in the read; derived from BBL. */
  title: string;
  /** CLIENT-DERIVED from each fact's `page_number`/`location` (no image bytes: B-001). */
  pages: ReviewPage[];
  /** AWAITING-BACKEND capability surface (see ReviewPrincipal.capabilities_known). */
  principal: ReviewPrincipal;
  /** CLIENT-DERIVED §11 honesty: false ⇒ rests in `uploaded`, no overlay/facts. */
  extraction_available: boolean;
}

/** One inbox row. AWAITING-BACKEND: there is no review-inbox endpoint yet. */
export interface InboxEntry {
  document_digest: string;
  title: string;
  target_bbl: string;
  state: DocumentState;
  open_item_count: number;
  updated_at: string;
}

// ---------------------------------------------------------------------------
// Request payloads (keyed on document_digest)
// ---------------------------------------------------------------------------

export interface AcceptFactRequest {
  documentDigest: string;
  evidenceId: string;
}

export interface CorrectFactRequest {
  documentDigest: string;
  evidenceId: string;
  corrected_normalized_value: JsonValue;
  corrected_units: string | null;
  reason: string;
  accepted_history_fingerprint: string;
}

export interface RejectFactRequest {
  documentDigest: string;
  evidenceId: string;
  reason: string;
}

export interface RejectDocumentRequest {
  documentDigest: string;
  reason: string;
}

export interface ConfirmDocumentRequest {
  documentDigest: string;
}

/** Edge 12: professionally_confirmed → needs_review (reason required). */
export interface ReopenDocumentRequest {
  documentDigest: string;
  reason: string;
}

// ---------------------------------------------------------------------------
// Typed errors + outcomes (reject codes 1:1 with the backend)
// ---------------------------------------------------------------------------

export type ReviewRejectCode =
  | "unauthorized_review_action"
  | "document_record_not_found"
  | "fact_not_found"
  | "concurrent_review_modification"
  | "correction_rejected"
  | "confirmation_rejected"
  | "illegal_transition"
  | "unauthorized_transition_actor"
  | "transition_reason_required"
  | "post_confirmation_edit_refused";

export interface ReviewActionError {
  kind: "error";
  reject_code: ReviewRejectCode;
  message: string;
  correlationId: string | null;
  /** From `confirmation_rejected` `detail.rejected_fact_ids`. */
  rejectedFactIds?: string[];
  /**
   * On `concurrent_review_modification` the client re-reads and attaches the
   * fresh document so the reviewer can re-apply their preserved draft (SC-S7).
   */
  currentDocument?: ReviewDocument;
}

export interface NetworkErrorOutcome {
  kind: "network_error";
  message: string;
}
export interface ClientTimeoutOutcome {
  kind: "client_timeout";
  timeoutMs: number;
}
export interface AbortedOutcome {
  kind: "aborted";
}
export interface UnexpectedResponseOutcome {
  kind: "unexpected_response";
  httpStatus: number;
  correlationId: string | null;
}
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
  /** The FRESH read-model after the mutation (client re-reads; see api.ts). */
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
  fetchImpl?: typeof fetch;
  signal?: AbortSignal;
  timeoutMs?: number;
}

// ---------------------------------------------------------------------------
// The client interface — the ONE seam the orchestrator reconciles
// ---------------------------------------------------------------------------

export interface SurveyReviewClient {
  readDocument(
    documentDigest: string,
    options?: RequestOptions,
  ): Promise<ReadDocumentOutcome>;
  /** AWAITING-BACKEND endpoint; the UI degrades to an honest empty/failure. */
  listInbox(state?: DocumentState, options?: RequestOptions): Promise<InboxOutcome>;
  acceptFact(req: AcceptFactRequest, options?: RequestOptions): Promise<ActionOutcome>;
  correctFact(req: CorrectFactRequest, options?: RequestOptions): Promise<ActionOutcome>;
  rejectFact(req: RejectFactRequest, options?: RequestOptions): Promise<ActionOutcome>;
  rejectDocument(req: RejectDocumentRequest, options?: RequestOptions): Promise<ActionOutcome>;
  confirmDocument(req: ConfirmDocumentRequest, options?: RequestOptions): Promise<ActionOutcome>;
  reopenDocument(req: ReopenDocumentRequest, options?: RequestOptions): Promise<ActionOutcome>;
}
