/**
 * HARDENED typed client for GET /api/v1/address-resolution (task M5-T015).
 *
 * Contract: services/api/app/api/v1/address_resolution.py (read-only
 * dependency). Same discipline as src/lib/api.ts, adapted to the address
 * endpoint's two document kinds:
 *
 *   1. The (HTTP status, state) pair matrix below mirrors the endpoint's
 *      STATUS_STATE_MATRIX verbatim; any pair outside it renders as the
 *      distinct `unexpected_response` outcome. A body is never routed by
 *      its `state` alone.
 *   2. A 200 body must carry document_kind "address_resolution"; its
 *      material fields are mapped into a BOUNDED view (every reflected
 *      string through boundedText/boundedToken) BEFORE any rendering.
 *      Branching stays on the RAW `status` string (the endpoint contract:
 *      consumers branch on status, never on field presence); only the
 *      DISPLAY copy of an unrecognized status is bounded.
 *   3. Requests are cancellable and time-bounded exactly like the property
 *      client (aborted / client_timeout outcomes).
 *
 * No legal or address logic lives here: this module transports, verifies
 * the pair matrix, and bounds reflection. It never picks a suggestion,
 * never normalizes an address, never fabricates a field
 * (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md).
 */

import { boundedText, boundedToken } from "./bounded";

export const DEFAULT_ADDRESS_TIMEOUT_MS = 12_000;

/**
 * The endpoint's documented TYPED pairs, verbatim from STATUS_STATE_MATRIX
 * (address_resolution.py). request_budget_exceeded is documented there as
 * unreachable-by-construction (the endpoint passes no budget); it is kept
 * here so that, were it ever to arrive, it renders as its own honest typed
 * state instead of an undocumented surprise.
 */
export const ADDRESS_ERROR_STATES = [
  "invalid_input",
  "key_missing",
  "auth_failed",
  "rate_limited",
  "source_unavailable",
  "timeout",
  "malformed_response",
  "request_budget_exceeded",
  "internal_error",
] as const;
export type AddressErrorState = (typeof ADDRESS_ERROR_STATES)[number];

const DOCUMENTED_PAIRS: ReadonlySet<string> = new Set([
  "200|", // success family; the body's own status field discriminates
  "422|invalid_input",
  "503|key_missing",
  "502|auth_failed",
  "503|rate_limited",
  "503|source_unavailable",
  "504|timeout",
  "502|malformed_response",
  "503|request_budget_exceeded",
  "500|internal_error",
]);

/** One EE suggestion, slot order preserved. `streetName` is BOUNDED and is
 * the only member that may reach the DOM. `rawStreetName` is the source
 * string VERBATIM and exists solely so a user pick can re-resolve with the
 * exact street the source suggested (the connector's re-query contract);
 * it goes only to the fetch seam (URL-encoded), NEVER into a render. */
export interface SuggestionView {
  streetName: string;
  rawStreetName: string;
  streetCode: string | null;
}

/** Bounded display view of a 200 address_resolution document. */
export interface AddressDocumentView {
  /** RAW status string for branching (contract rule); bound for display
   * only via `statusToken` when it is not a recognized value. */
  status: string;
  statusToken: string;
  inputEcho: {
    houseNumber: string | null;
    street: string | null;
    borough: string | null;
    zip: string | null;
  };
  canonical: {
    bbl: string | null;
    bin: string | null;
    streetNameNormalized: string | null;
    boroughName: string | null;
    zipCode: string | null;
  };
  grc: string | null;
  grcMessage: string | null;
  grc2: string | null;
  grc2Message: string | null;
  suggestions: SuggestionView[];
  sourceFactsCount: number;
  sourceFactsNotEmittedReason: string | null;
  provenance: {
    sourceId: string | null;
    retrievedAt: string | null;
    connectorCorrelationId: string | null;
    responseDigest: string | null;
  };
}

export interface AddressDocumentOutcome {
  kind: "document";
  view: AddressDocumentView;
  correlationId: string | null;
}

export interface AddressErrorOutcome {
  kind: "error";
  state: AddressErrorState;
  httpStatus: number;
  message: string;
  /** Already server-bounded (the endpoint's local Retry-After guard);
   * re-tokenized here anyway — belt and suspenders. */
  retryAfter: string | null;
  correlationId: string | null;
}

export interface AddressNetworkErrorOutcome {
  kind: "network_error";
  message: string;
}

export interface AddressClientTimeoutOutcome {
  kind: "client_timeout";
  timeoutMs: number;
}

export interface AddressAbortedOutcome {
  kind: "aborted";
}

export interface AddressUnexpectedResponseOutcome {
  kind: "unexpected_response";
  httpStatus: number;
  receivedState: string | null;
  correlationId: string | null;
}

export type AddressOutcome =
  | AddressDocumentOutcome
  | AddressErrorOutcome
  | AddressNetworkErrorOutcome
  | AddressClientTimeoutOutcome
  | AddressAbortedOutcome
  | AddressUnexpectedResponseOutcome;

export interface AddressQuery {
  houseNumber: string;
  street: string;
  /** Exactly one of borough / zip is normally provided; both pass through
   * verbatim — the CONNECTOR is the validation authority. */
  borough: string | null;
  zip: string | null;
}

export interface AddressLookupOptions {
  fetchImpl?: typeof fetch;
  signal?: AbortSignal;
  timeoutMs?: number;
}

function apiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

/** Bounded-or-null: an absent/blank source string stays an explicit null
 * (rendered as honest absence), never a coerced fallback sentence. */
function textOrNull(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const bounded = boundedText(value, "");
  return bounded === "" ? null : bounded;
}

function documentView(record: Record<string, unknown>): AddressDocumentView {
  const status = typeof record.status === "string" ? record.status : "";
  const echo = asRecord(record.input_echo) ?? {};
  const canonical = asRecord(record.canonical) ?? {};
  const provenance = asRecord(record.provenance) ?? {};
  const suggestions: SuggestionView[] = [];
  if (Array.isArray(record.suggestions)) {
    for (const entry of record.suggestions) {
      const suggestion = asRecord(entry);
      const raw = suggestion?.street_name;
      // The connector guarantees every emitted slot has a nonempty
      // street_name (empty slots are skipped connector-side); this guard is
      // defense-in-depth against a drifted body, not slot filtering.
      if (typeof raw !== "string" || raw === "") continue;
      suggestions.push({
        streetName: boundedText(raw, "(unprintable street name)"),
        rawStreetName: raw,
        streetCode: boundedToken(suggestion?.street_code, 32),
      });
    }
  }
  return {
    status,
    statusToken: boundedToken(status, 48) ?? "absent",
    inputEcho: {
      houseNumber: textOrNull(echo.house_number),
      street: textOrNull(echo.street),
      borough: textOrNull(echo.borough),
      zip: textOrNull(echo.zip),
    },
    canonical: {
      bbl: boundedToken(canonical.bbl, 32),
      bin: boundedToken(canonical.bin, 32),
      streetNameNormalized: textOrNull(canonical.street_name_normalized),
      boroughName: textOrNull(canonical.borough_name),
      zipCode: boundedToken(canonical.zip_code, 16),
    },
    grc: boundedToken(record.grc, 8),
    grcMessage: textOrNull(record.grc_message),
    grc2: boundedToken(record.grc2, 8),
    grc2Message: textOrNull(record.grc2_message),
    suggestions,
    sourceFactsCount: Array.isArray(record.source_facts)
      ? record.source_facts.length
      : 0,
    sourceFactsNotEmittedReason: textOrNull(record.source_facts_not_emitted_reason),
    provenance: {
      sourceId: boundedToken(provenance.source_id, 64),
      retrievedAt: boundedToken(provenance.retrieved_at, 40),
      connectorCorrelationId: boundedToken(provenance.correlation_id, 64),
      responseDigest: textOrNull(provenance.response_digest),
    },
  };
}

export async function resolveAddress(
  query: AddressQuery,
  options: AddressLookupOptions = {},
): Promise<AddressOutcome> {
  const fetchImpl = options.fetchImpl ?? fetch;
  const timeoutMs = options.timeoutMs ?? DEFAULT_ADDRESS_TIMEOUT_MS;
  const params = new URLSearchParams();
  params.set("house_number", query.houseNumber);
  params.set("street", query.street);
  if (query.borough) params.set("borough", query.borough);
  if (query.zip) params.set("zip", query.zip);
  const url = `${apiBaseUrl()}/api/v1/address-resolution?${params.toString()}`;

  const controller = new AbortController();
  let timedOut = false;
  const externalSignal = options.signal;
  if (externalSignal?.aborted) {
    return { kind: "aborted" };
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
        method: "GET",
        headers: { Accept: "application/json" },
        cache: "no-store",
        signal: controller.signal,
      });
    } catch {
      if (timedOut) {
        return { kind: "client_timeout", timeoutMs };
      }
      if (controller.signal.aborted || externalSignal?.aborted) {
        return { kind: "aborted" };
      }
      return {
        kind: "network_error",
        message:
          "The platform API could not be reached. Nothing was resolved. " +
          "This lookup is safe to retry.",
      };
    }

    const correlationId = boundedToken(response.headers.get("X-Correlation-ID"));

    let body: unknown = null;
    try {
      body = await response.json();
    } catch {
      if (timedOut) {
        return { kind: "client_timeout", timeoutMs };
      }
      if (controller.signal.aborted || externalSignal?.aborted) {
        return { kind: "aborted" };
      }
      return {
        kind: "unexpected_response",
        httpStatus: response.status,
        receivedState: null,
        correlationId,
      };
    }

    const record = asRecord(body);
    // RAW state for the pair check; bounded form is DISPLAY-only.
    const state = record && typeof record.state === "string" ? record.state : null;
    const pairKey = `${response.status}|${state ?? ""}`;

    if (response.status === 200) {
      if (
        record === null ||
        record.document_kind !== "address_resolution" ||
        typeof record.status !== "string"
      ) {
        return {
          kind: "unexpected_response",
          httpStatus: 200,
          receivedState: state === null ? null : boundedToken(state, 48),
          correlationId,
        };
      }
      return { kind: "document", view: documentView(record), correlationId };
    }

    if (!DOCUMENTED_PAIRS.has(pairKey)) {
      return {
        kind: "unexpected_response",
        httpStatus: response.status,
        receivedState: state === null ? null : boundedToken(state, 48),
        correlationId,
      };
    }

    const error = asRecord(record?.error);
    return {
      kind: "error",
      state: state as AddressErrorState,
      httpStatus: response.status,
      message: boundedText(
        error?.message,
        "The address service reported a failure without further detail.",
      ),
      retryAfter: boundedToken(error?.retry_after, 32),
      correlationId,
    };
  } finally {
    clearTimeout(timer);
    externalSignal?.removeEventListener("abort", onExternalAbort);
  }
}
