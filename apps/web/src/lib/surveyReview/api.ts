/**
 * Survey-review API-client SEAM — HTTP implementation (task M2-T016 rework;
 * reconciled to the shipped backend slice, contract in
 * `project-control/reports/M2-T016-backend-return.md`).
 *
 * The ONE place survey-review server communication lives. Components depend on
 * the `SurveyReviewClient` interface (./types.ts) through the React context
 * (./context.tsx) — never on scattered fetch calls.
 *
 * Endpoints (keyed on the `document_digest` = `sha256:<64hex>`; colon URL-encoded):
 *   GET  /api/v1/documents/{digest}/review                 -> DocumentReviewView
 *   POST /api/v1/documents/{digest}/facts/{eid}/accept     -> ReviewActionResult
 *   POST /api/v1/documents/{digest}/facts/{eid}/correct    -> ReviewActionResult
 *   POST /api/v1/documents/{digest}/facts/{eid}/reject     -> ReviewActionResult
 *   POST /api/v1/documents/{digest}/confirm                -> ReviewActionResult
 *   POST /api/v1/documents/{digest}/reject                 -> ReviewActionResult
 *   POST /api/v1/documents/{digest}/reopen                 -> ReviewActionResult
 *
 * The mutating handlers return a `ReviewActionResult`, NOT the settled document.
 * So after each successful mutation the client RE-READS the review view (single
 * place, below) and returns that fresh `ReviewDocument` for the UI to render.
 *
 * Discipline carried over from the hardened property client: runtime validation
 * before render, bounded reflection, cancellation/timeout, typed refusals mapped
 * to plain language at the component layer. No legal logic here.
 */

import { boundedText, boundedToken } from "../bounded";
import { historyFingerprint } from "./fingerprint";
import { factTypeLabel } from "./labels";
import { validateReviewView } from "./validate";
import type {
  AcceptFactRequest,
  ActionOutcome,
  ConfirmDocumentRequest,
  CorrectFactRequest,
  DocumentState,
  FactView,
  InboxEntry,
  InboxOutcome,
  JsonValue,
  ReadDocumentOutcome,
  RejectDocumentRequest,
  RejectFactRequest,
  ReopenDocumentRequest,
  RequestOptions,
  ReviewActionError,
  ReviewDocument,
  ReviewPage,
  ReviewPrincipal,
  ReviewRejectCode,
  SurveyReviewClient,
} from "./types";

export const DEFAULT_TIMEOUT_MS = 12_000;

const REJECT_CODES: ReadonlySet<string> = new Set<ReviewRejectCode>([
  "unauthorized_review_action",
  "document_record_not_found",
  "fact_not_found",
  "concurrent_review_modification",
  "correction_rejected",
  "confirmation_rejected",
  "illegal_transition",
  "unauthorized_transition_actor",
  "transition_reason_required",
  "post_confirmation_edit_refused",
]);

/**
 * Bounded sanitizer for an evidence id. Same defensive shape as `boundedToken`
 * (non-string rejected, hostile characters stripped, length bounded, empty ->
 * null) but the charset keeps `:` because evidence ids are colon-delimited
 * (`sev:doc:p1:3`). `boundedToken` would flatten that to `sevdocp13`, and a
 * rejected-fact id that no longer equals any `fact.evidence_id` cannot be
 * matched back to the fact that blocked confirmation.
 */
const MAX_EVIDENCE_ID_LENGTH = 128;

export function boundedEvidenceId(
  value: unknown,
  max: number = MAX_EVIDENCE_ID_LENGTH,
): string | null {
  if (typeof value !== "string") return null;
  const cleaned = value.replace(/[^A-Za-z0-9._:-]/g, "").slice(0, max);
  return cleaned === "" ? null : cleaned;
}

/**
 * AWAITING-BACKEND capability surface (workflow §5.2). Until the review read
 * returns the principal's capabilities, actions are shown enabled and the
 * server's typed `unauthorized_review_action` refusal is surfaced in plain
 * language — the UI never fabricates a capability it was not told.
 */
const SERVER_ENFORCED_PRINCIPAL: ReviewPrincipal = {
  principal_id: null,
  role: "user",
  display_name: "Reviewer",
  capabilities: {
    can_view: true,
    can_accept_fact: true,
    can_correct_fact: true,
    can_reject_fact: true,
    can_confirm_document: true,
    can_reject_document: true,
    can_reopen_document: true,
  },
  capabilities_known: false,
};

export function apiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";
}

function documentsBase(): string {
  return `${apiBaseUrl()}/api/v1/documents`;
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

interface RawFetchResult {
  ok?: { status: number; body: unknown; correlationId: string | null };
  transport?:
    | { kind: "network_error"; message: string }
    | { kind: "client_timeout"; timeoutMs: number }
    | { kind: "aborted" };
}

async function rawFetch(
  url: string,
  init: RequestInit,
  options: RequestOptions,
): Promise<RawFetchResult> {
  const fetchImpl = options.fetchImpl ?? fetch;
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const controller = new AbortController();
  let timedOut = false;
  const externalSignal = options.signal;
  if (externalSignal?.aborted) return { transport: { kind: "aborted" } };
  const onExternalAbort = () => controller.abort();
  externalSignal?.addEventListener("abort", onExternalAbort);
  const timer = setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, timeoutMs);

  try {
    let response: Response;
    try {
      response = await fetchImpl(url, {
        ...init,
        cache: "no-store",
        signal: controller.signal,
        headers: { Accept: "application/json", ...(init.headers ?? {}) },
      });
    } catch {
      if (timedOut) return { transport: { kind: "client_timeout", timeoutMs } };
      if (controller.signal.aborted || externalSignal?.aborted) return { transport: { kind: "aborted" } };
      return {
        transport: {
          kind: "network_error",
          message:
            "The review service could not be reached. Nothing was changed. This action is safe to retry.",
        },
      };
    }
    const correlationId = boundedToken(response.headers.get("X-Correlation-ID"));
    let body: unknown = null;
    try {
      body = await response.json();
    } catch {
      if (timedOut) return { transport: { kind: "client_timeout", timeoutMs } };
      if (controller.signal.aborted || externalSignal?.aborted) return { transport: { kind: "aborted" } };
      body = null;
    }
    return { ok: { status: response.status, body, correlationId } };
  } finally {
    clearTimeout(timer);
    externalSignal?.removeEventListener("abort", onExternalAbort);
  }
}

function postInit(payload: unknown): RequestInit {
  return {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  };
}

/** Map a decoded backend error body to the typed `ReviewActionError`. */
function decodeError(
  status: number,
  body: unknown,
  correlationId: string | null,
): ReviewActionError | null {
  const record = asRecord(body);
  const rawCode = record && typeof record.reject_code === "string" ? record.reject_code : null;
  if (rawCode && REJECT_CODES.has(rawCode)) {
    const error: ReviewActionError = {
      kind: "error",
      reject_code: rawCode as ReviewRejectCode,
      message: boundedText(record?.message, "The review service refused this action."),
      correlationId,
    };
    const detail = asRecord(record?.detail);
    const rejected = detail?.rejected_fact_ids;
    if (Array.isArray(rejected)) {
      // An entry that sanitizes to nothing is DROPPED, not passed through as
      // `String(id)` — falling back to the raw value would defeat the sanitizer
      // for exactly the hostile inputs it exists to bound.
      error.rejectedFactIds = rejected
        .map((id) => boundedEvidenceId(id))
        .filter((id): id is string => id !== null);
    }
    return error;
  }
  if (status === 404) {
    return {
      kind: "error",
      reject_code: "document_record_not_found",
      message: boundedText(record?.message, "The document was not found."),
      correlationId,
    };
  }
  return null;
}

// --------------------------------------------------------------------------
// Backend DocumentReviewView -> client ReviewDocument (derive missing fields)
// --------------------------------------------------------------------------

function mapFact(raw: Record<string, unknown>): FactView {
  const correctionHistory = Array.isArray(raw.correction_history)
    ? (raw.correction_history as FactView["correction_history"])
    : [];
  const rawLabel = raw.display_label;
  const factType = typeof raw.fact_type === "string" ? raw.fact_type : "unknown";
  return {
    evidence_id: String(raw.evidence_id),
    fact_type: factType,
    original_value: raw.original_value as FactView["original_value"],
    baseline_normalized_value: raw.baseline_normalized_value as FactView["baseline_normalized_value"],
    baseline_units: (raw.baseline_units as string | null) ?? null,
    normalized_value: raw.normalized_value as FactView["normalized_value"],
    units: (raw.units as string | null) ?? null,
    confirmation_state: raw.confirmation_state as FactView["confirmation_state"],
    confirmation_note: (raw.confirmation_note as string | null) ?? null,
    correction_history: correctionHistory,
    correction_count:
      typeof raw.correction_count === "number" ? raw.correction_count : correctionHistory.length,
    check_pass: typeof raw.check_pass === "number" ? raw.check_pass : 0,
    check_fail: typeof raw.check_fail === "number" ? raw.check_fail : 0,
    check_unresolved: typeof raw.check_unresolved === "number" ? raw.check_unresolved : 0,
    location: (raw.location as FactView["location"]) ?? null,
    page_number: typeof raw.page_number === "number" ? raw.page_number : null,
    extraction_method: (raw.extraction_method as FactView["extraction_method"]) ?? null,
    is_unconfirmed_evidence: raw.is_unconfirmed_evidence !== false,
    promotable: raw.promotable === true,
    downstream_impact: (raw.downstream_impact as FactView["downstream_impact"]) ?? null,
    // client-derived / awaiting-backend:
    display_label:
      typeof rawLabel === "string" && rawLabel !== "" ? rawLabel : factTypeLabel(factType),
    ai_drafted_label:
      raw.ai_drafted_label === true || raw.extraction_method === "ai_assisted_classification",
    accepted_history_fingerprint: historyFingerprint(correctionHistory as unknown as JsonValue[]),
  };
}

function derivePages(facts: FactView[]): ReviewPage[] {
  const byPage = new Map<number, ReviewPage>();
  for (const fact of facts) {
    const page = fact.page_number ?? 1;
    if (!byPage.has(page)) {
      byPage.set(page, {
        page_number: page,
        image_ref: null,
        width: null,
        height: null,
        coordinate_space: fact.location?.bounding_box?.coordinate_space ?? null,
      });
    }
  }
  return [...byPage.values()].sort((a, b) => a.page_number - b.page_number);
}

function mapPrincipal(raw: unknown): ReviewPrincipal {
  const record = asRecord(raw);
  const caps = record ? asRecord(record.capabilities) : null;
  if (!record || !caps) return SERVER_ENFORCED_PRINCIPAL;
  const bool = (key: string) => caps[key] === true;
  return {
    principal_id: typeof record.principal_id === "string" ? record.principal_id : null,
    role: record.role === "qualified_professional" ? "qualified_professional" : "user",
    display_name: boundedText(record.display_name, "Reviewer"),
    capabilities: {
      can_view: bool("can_view"),
      can_accept_fact: bool("can_accept_fact"),
      can_correct_fact: bool("can_correct_fact"),
      can_reject_fact: bool("can_reject_fact"),
      can_confirm_document: bool("can_confirm_document"),
      can_reject_document: bool("can_reject_document"),
      can_reopen_document: bool("can_reopen_document"),
    },
    capabilities_known: true,
  };
}

function mapReviewDocument(raw: Record<string, unknown>): ReviewDocument {
  const facts = Array.isArray(raw.facts)
    ? (raw.facts as unknown[]).map((f) => mapFact(f as Record<string, unknown>))
    : [];
  const state = raw.state as DocumentState;
  const targetBbl = typeof raw.target_bbl === "string" ? raw.target_bbl : "";
  return {
    document_digest: String(raw.document_digest),
    target_bbl: targetBbl,
    state,
    state_history: Array.isArray(raw.state_history)
      ? (raw.state_history as ReviewDocument["state_history"])
      : [],
    facts,
    confirm_precondition_met: raw.confirm_precondition_met === true,
    blocking_fact_ids: Array.isArray(raw.blocking_fact_ids) ? (raw.blocking_fact_ids as string[]) : [],
    original_available: raw.original_available === true,
    correlation_id: typeof raw.correlation_id === "string" ? raw.correlation_id : null,
    // client-derived / awaiting-backend:
    title:
      typeof raw.title === "string" && raw.title !== ""
        ? raw.title
        : `Survey document — BBL ${targetBbl || "unknown"}`,
    pages: derivePages(facts),
    principal: mapPrincipal(raw.principal),
    extraction_available: state !== "uploaded",
  };
}

class HttpSurveyReviewClient implements SurveyReviewClient {
  async readDocument(
    documentDigest: string,
    options: RequestOptions = {},
  ): Promise<ReadDocumentOutcome> {
    const url = `${documentsBase()}/${encodeURIComponent(documentDigest)}/review`;
    const result = await rawFetch(url, { method: "GET" }, options);
    if (result.transport) return result.transport;
    const { status, body, correlationId } = result.ok!;
    if (status === 200) {
      const validation = validateReviewView(body);
      if (!validation.ok) {
        return {
          kind: "validation_failure",
          problems: validation.problems.map((p) => boundedText(p, "problem detail unavailable")),
          correlationId,
        };
      }
      return {
        kind: "document",
        document: mapReviewDocument(body as Record<string, unknown>),
        correlationId,
      };
    }
    const record = asRecord(body);
    if (status === 404) {
      return {
        kind: "not_found",
        message: boundedText(record?.message, "No survey document was found for this digest."),
        correlationId,
      };
    }
    if (status === 401 || status === 403) {
      return {
        kind: "unauthorized",
        message: boundedText(record?.message, "You are not authorized to view this survey document."),
        correlationId,
      };
    }
    return { kind: "unexpected_response", httpStatus: status, correlationId };
  }

  async listInbox(state?: DocumentState, options: RequestOptions = {}): Promise<InboxOutcome> {
    // AWAITING-BACKEND: no review-inbox endpoint yet. The seam is preserved; if
    // the endpoint is absent the request returns a documented empty/failure and
    // the UI degrades honestly (never a fabricated queue).
    const query = state ? `?state=${encodeURIComponent(state)}` : "";
    const url = `${documentsBase()}/review-inbox${query}`;
    const result = await rawFetch(url, { method: "GET" }, options);
    if (result.transport) return result.transport;
    const { status, body, correlationId } = result.ok!;
    if (status === 200) {
      const record = asRecord(body);
      const rawEntries = record && Array.isArray(record.entries) ? record.entries : null;
      if (!rawEntries) {
        return { kind: "validation_failure", problems: ["inbox response missing entries"], correlationId };
      }
      const entries: InboxEntry[] = rawEntries
        .map((entry): InboxEntry | null => {
          const row = asRecord(entry);
          if (!row || typeof row.document_digest !== "string") return null;
          return {
            document_digest: row.document_digest,
            title: boundedText(row.title, "Untitled document"),
            target_bbl: boundedToken(row.target_bbl, 32) ?? "",
            state: row.state as DocumentState,
            open_item_count: typeof row.open_item_count === "number" ? row.open_item_count : 0,
            updated_at: typeof row.updated_at === "string" ? row.updated_at : "",
          };
        })
        .filter((e): e is InboxEntry => e !== null);
      return { kind: "inbox", entries, correlationId };
    }
    if (status === 401 || status === 403) {
      return {
        kind: "unauthorized",
        message: boundedText(asRecord(body)?.message, "You are not authorized to view the review inbox."),
        correlationId,
      };
    }
    return { kind: "unexpected_response", httpStatus: status, correlationId };
  }

  /** Re-read the settled view after a successful mutation. */
  private async reReadAsAction(
    documentDigest: string,
    options: RequestOptions,
  ): Promise<ActionOutcome> {
    const read = await this.readDocument(documentDigest, options);
    switch (read.kind) {
      case "document":
        return { kind: "updated", document: read.document, correlationId: read.correlationId };
      case "not_found":
        return {
          kind: "error",
          reject_code: "document_record_not_found",
          message: read.message,
          correlationId: read.correlationId,
        };
      case "unauthorized":
        return {
          kind: "error",
          reject_code: "unauthorized_review_action",
          message: read.message,
          correlationId: read.correlationId,
        };
      default:
        return read; // network_error | client_timeout | aborted | unexpected_response | validation_failure
    }
  }

  private async finishMutation(
    result: RawFetchResult,
    documentDigest: string,
    options: RequestOptions,
  ): Promise<ActionOutcome> {
    if (result.transport) return result.transport;
    const { status, body, correlationId } = result.ok!;
    if (status >= 200 && status < 300) {
      return this.reReadAsAction(documentDigest, options);
    }
    const error = decodeError(status, body, correlationId);
    if (!error) return { kind: "unexpected_response", httpStatus: status, correlationId };
    if (error.reject_code === "concurrent_review_modification") {
      // Re-read so the reviewer sees the fresh state and can re-apply their draft.
      const fresh = await this.readDocument(documentDigest, options);
      if (fresh.kind === "document") error.currentDocument = fresh.document;
    }
    return error;
  }

  async acceptFact(req: AcceptFactRequest, options: RequestOptions = {}): Promise<ActionOutcome> {
    const url = `${documentsBase()}/${encodeURIComponent(req.documentDigest)}/facts/${encodeURIComponent(req.evidenceId)}/accept`;
    return this.finishMutation(await rawFetch(url, postInit({}), options), req.documentDigest, options);
  }

  async correctFact(req: CorrectFactRequest, options: RequestOptions = {}): Promise<ActionOutcome> {
    const url = `${documentsBase()}/${encodeURIComponent(req.documentDigest)}/facts/${encodeURIComponent(req.evidenceId)}/correct`;
    const res = await rawFetch(
      url,
      postInit({
        corrected_normalized_value: req.corrected_normalized_value,
        corrected_units: req.corrected_units,
        reason: req.reason,
        accepted_history_fingerprint: req.accepted_history_fingerprint,
      }),
      options,
    );
    return this.finishMutation(res, req.documentDigest, options);
  }

  async rejectFact(req: RejectFactRequest, options: RequestOptions = {}): Promise<ActionOutcome> {
    const url = `${documentsBase()}/${encodeURIComponent(req.documentDigest)}/facts/${encodeURIComponent(req.evidenceId)}/reject`;
    return this.finishMutation(await rawFetch(url, postInit({ reason: req.reason }), options), req.documentDigest, options);
  }

  async rejectDocument(req: RejectDocumentRequest, options: RequestOptions = {}): Promise<ActionOutcome> {
    const url = `${documentsBase()}/${encodeURIComponent(req.documentDigest)}/reject`;
    return this.finishMutation(await rawFetch(url, postInit({ reason: req.reason }), options), req.documentDigest, options);
  }

  async confirmDocument(req: ConfirmDocumentRequest, options: RequestOptions = {}): Promise<ActionOutcome> {
    const url = `${documentsBase()}/${encodeURIComponent(req.documentDigest)}/confirm`;
    return this.finishMutation(await rawFetch(url, postInit({}), options), req.documentDigest, options);
  }

  async reopenDocument(req: ReopenDocumentRequest, options: RequestOptions = {}): Promise<ActionOutcome> {
    const url = `${documentsBase()}/${encodeURIComponent(req.documentDigest)}/reopen`;
    return this.finishMutation(await rawFetch(url, postInit({ reason: req.reason }), options), req.documentDigest, options);
  }
}

export function createHttpSurveyReviewClient(): SurveyReviewClient {
  return new HttpSurveyReviewClient();
}
