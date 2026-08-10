/**
 * Survey-review API-client SEAM — HTTP implementation (task M2-T016, Packet C).
 *
 * The ONE place survey-review server communication lives. Components depend on
 * the `SurveyReviewClient` interface (./types.ts) through the React context in
 * ./context.tsx — never on fetch calls scattered through the tree. This keeps
 * the whole backend contract reconcilable in a single module: when the backend
 * review-action slice ships, only the endpoint map + decoders below are checked
 * against it.
 *
 * Discipline carried over from the hardened property client (src/lib/api.ts):
 *   - every response body is runtime-validated (./validate.ts) before any
 *     component renders it; a malformed body is a `validation_failure` outcome
 *     carrying only a bounded problem list — nothing partial is shown;
 *   - all reflected server text is length-capped + control-stripped
 *     (src/lib/bounded.ts); correlation ids are token-allowlisted;
 *   - requests are cancellable (AbortController) and time-bounded; a superseded
 *     request resolves to `aborted`, a timeout to the recoverable
 *     `client_timeout` outcome;
 *   - typed backend refusals (reject_code) map to plain-language UI copy at the
 *     component layer — this module never shows raw payloads.
 *
 * No legal logic lives here (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md): it
 * transports, verifies shape, and classifies. It never promotes evidence,
 * computes a promotion verdict, or confirms anything.
 */

import { boundedText, boundedToken } from "../bounded";
import { validateReviewDocument } from "./validate";
import type {
  AcceptFactRequest,
  ActionOutcome,
  ConfirmDocumentRequest,
  CorrectFactRequest,
  DocumentState,
  InboxEntry,
  InboxOutcome,
  ReadDocumentOutcome,
  RejectDocumentRequest,
  RejectFactRequest,
  RequestOptions,
  RequestReExtractionRequest,
  ReviewActionError,
  ReviewRejectCode,
  SurveyReviewClient,
} from "./types";

/** Default request budget; kept below the Playwright timeout so the timeout
 * journey is provable in CI without configuration. */
export const DEFAULT_TIMEOUT_MS = 12_000;

const REJECT_CODES: ReadonlySet<string> = new Set<ReviewRejectCode>([
  "unauthorized",
  "illegal_transition",
  "unauthorized_transition_actor",
  "transition_reason_required",
  "promotion_gate_unmet",
  "correction_tampered",
  "correction_chain_mismatch",
  "correction_no_op",
  "correction_reason_required",
  "stale_history",
  "not_found",
  "validation_error",
]);

/**
 * API base URL. NEXT_PUBLIC_API_BASE_URL is compiled into the browser bundle at
 * build time (publishable name only). Default matches local/CI where FastAPI
 * listens on 127.0.0.1:8000.
 */
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
  /** Present when the network round-trip succeeded and JSON decoded. */
  ok?: {
    status: number;
    body: unknown;
    correlationId: string | null;
  };
  /** Present when the round-trip failed at the transport level. */
  transport?:
    | { kind: "network_error"; message: string }
    | { kind: "client_timeout"; timeoutMs: number }
    | { kind: "aborted" };
}

/**
 * Perform one cancellable, time-bounded fetch and decode JSON. Returns a
 * discriminated raw result so each public method can classify by endpoint.
 */
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
  if (externalSignal?.aborted) {
    return { transport: { kind: "aborted" } };
  }
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
      if (controller.signal.aborted || externalSignal?.aborted) {
        return { transport: { kind: "aborted" } };
      }
      return {
        transport: {
          kind: "network_error",
          message:
            "The review service could not be reached. Nothing was changed. " +
            "This action is safe to retry.",
        },
      };
    }

    const correlationId = boundedToken(response.headers.get("X-Correlation-ID"));
    let body: unknown = null;
    try {
      body = await response.json();
    } catch {
      if (timedOut) return { transport: { kind: "client_timeout", timeoutMs } };
      if (controller.signal.aborted || externalSignal?.aborted) {
        return { transport: { kind: "aborted" } };
      }
      body = null;
    }
    return { ok: { status: response.status, body, correlationId } };
  } finally {
    clearTimeout(timer);
    externalSignal?.removeEventListener("abort", onExternalAbort);
  }
}

/** Map a decoded error body to the typed `ReviewActionError`. */
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
    // A stale-history refusal may carry the current document so the reviewer
    // can re-open live state without losing their input (workflow §6.3).
    if (rawCode === "stale_history" && record && record.current_document) {
      const validation = validateReviewDocument(record.current_document);
      if (validation.ok) error.currentDocument = validation.document;
    }
    return error;
  }
  // A 4xx/5xx without a documented reject_code — surface not_found distinctly,
  // otherwise it is an unexpected condition (handled by the caller).
  if (status === 404) {
    return {
      kind: "error",
      reject_code: "not_found",
      message: boundedText(record?.message, "The document was not found."),
      correlationId,
    };
  }
  return null;
}

/** Shared decode for endpoints that return a fresh `ReviewDocument`. */
function decodeActionResponse(result: RawFetchResult): ActionOutcome {
  if (result.transport) return result.transport;
  const { status, body, correlationId } = result.ok!;
  if (status >= 200 && status < 300) {
    const validation = validateReviewDocument(body);
    if (!validation.ok) {
      return {
        kind: "validation_failure",
        problems: validation.problems.map((p) => boundedText(p, "problem detail unavailable")),
        correlationId,
      };
    }
    return { kind: "updated", document: validation.document, correlationId };
  }
  const error = decodeError(status, body, correlationId);
  if (error) return error;
  return { kind: "unexpected_response", httpStatus: status, correlationId };
}

function postInit(payload: unknown): RequestInit {
  return {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  };
}

class HttpSurveyReviewClient implements SurveyReviewClient {
  async readDocument(
    documentId: string,
    options: RequestOptions = {},
  ): Promise<ReadDocumentOutcome> {
    const url = `${documentsBase()}/${encodeURIComponent(documentId)}/review`;
    const result = await rawFetch(url, { method: "GET" }, options);
    if (result.transport) return result.transport;
    const { status, body, correlationId } = result.ok!;
    if (status === 200) {
      const validation = validateReviewDocument(body);
      if (!validation.ok) {
        return {
          kind: "validation_failure",
          problems: validation.problems.map((p) => boundedText(p, "problem detail unavailable")),
          correlationId,
        };
      }
      return { kind: "document", document: validation.document, correlationId };
    }
    const record = asRecord(body);
    if (status === 404) {
      return {
        kind: "not_found",
        message: boundedText(record?.message, "No survey document was found for this id."),
        correlationId,
      };
    }
    if (status === 401 || status === 403) {
      return {
        kind: "unauthorized",
        message: boundedText(
          record?.message,
          "You are not authorized to view this survey document.",
        ),
        correlationId,
      };
    }
    return { kind: "unexpected_response", httpStatus: status, correlationId };
  }

  async listInbox(
    state?: DocumentState,
    options: RequestOptions = {},
  ): Promise<InboxOutcome> {
    const query = state ? `?state=${encodeURIComponent(state)}` : "";
    const url = `${documentsBase()}/review-inbox${query}`;
    const result = await rawFetch(url, { method: "GET" }, options);
    if (result.transport) return result.transport;
    const { status, body, correlationId } = result.ok!;
    if (status === 200) {
      const record = asRecord(body);
      const rawEntries = record && Array.isArray(record.entries) ? record.entries : null;
      if (!rawEntries) {
        return {
          kind: "validation_failure",
          problems: ["inbox response is missing the entries array"],
          correlationId,
        };
      }
      const entries: InboxEntry[] = rawEntries
        .map((entry): InboxEntry | null => {
          const row = asRecord(entry);
          if (!row || typeof row.document_id !== "string") return null;
          return {
            document_id: boundedToken(row.document_id, 128) ?? row.document_id,
            title: boundedText(row.title, "Untitled document"),
            target_bbl: boundedToken(row.target_bbl, 32) ?? "",
            state: row.state as DocumentState,
            open_item_count:
              typeof row.open_item_count === "number" ? row.open_item_count : 0,
            updated_at: typeof row.updated_at === "string" ? row.updated_at : "",
          };
        })
        .filter((entry): entry is InboxEntry => entry !== null);
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

  async acceptFact(req: AcceptFactRequest, options: RequestOptions = {}): Promise<ActionOutcome> {
    const url = `${documentsBase()}/${encodeURIComponent(req.documentId)}/facts/${encodeURIComponent(req.evidenceId)}/accept`;
    return decodeActionResponse(await rawFetch(url, postInit({}), options));
  }

  async correctFact(req: CorrectFactRequest, options: RequestOptions = {}): Promise<ActionOutcome> {
    const url = `${documentsBase()}/${encodeURIComponent(req.documentId)}/facts/${encodeURIComponent(req.evidenceId)}/correct`;
    return decodeActionResponse(
      await rawFetch(
        url,
        postInit({
          corrected_normalized_value: req.corrected_normalized_value,
          corrected_units: req.corrected_units,
          reason: req.reason,
          accepted_history_fingerprint: req.accepted_history_fingerprint,
        }),
        options,
      ),
    );
  }

  async rejectFact(req: RejectFactRequest, options: RequestOptions = {}): Promise<ActionOutcome> {
    const url = `${documentsBase()}/${encodeURIComponent(req.documentId)}/facts/${encodeURIComponent(req.evidenceId)}/reject`;
    return decodeActionResponse(await rawFetch(url, postInit({ reason: req.reason }), options));
  }

  async rejectDocument(req: RejectDocumentRequest, options: RequestOptions = {}): Promise<ActionOutcome> {
    const url = `${documentsBase()}/${encodeURIComponent(req.documentId)}/reject`;
    return decodeActionResponse(await rawFetch(url, postInit({ reason: req.reason }), options));
  }

  async confirmDocument(req: ConfirmDocumentRequest, options: RequestOptions = {}): Promise<ActionOutcome> {
    const url = `${documentsBase()}/${encodeURIComponent(req.documentId)}/confirm`;
    return decodeActionResponse(await rawFetch(url, postInit({}), options));
  }

  async requestReExtraction(
    req: RequestReExtractionRequest,
    options: RequestOptions = {},
  ): Promise<ActionOutcome> {
    const url = `${documentsBase()}/${encodeURIComponent(req.documentId)}/reextract`;
    return decodeActionResponse(await rawFetch(url, postInit({}), options));
  }
}

/** Construct the default HTTP-backed client. */
export function createHttpSurveyReviewClient(): SurveyReviewClient {
  return new HttpSurveyReviewClient();
}
