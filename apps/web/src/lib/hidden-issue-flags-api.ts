/**
 * Typed client for the internal §8a hidden-issue-flags read route (lane C packet
 * W2).
 *
 * Contract: services/api/app/api/v1/hidden_issue_flags_read.py (read-only
 * dependency). The route returns the four §8a flag groups wrapped in the W0
 * `hidden_issue_flags.schema.json` envelope ({contract_version, groups}) for one
 * confirmed BBL, behind the default-off INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED
 * flag (and Lane B's LANE_B_ENABLED gate).
 *
 * `fetchHiddenIssueFlags(bbl)` transports and verifies the document. Every 200
 * body is runtime-validated against the contract shape BEFORE anything can use it
 * (`validateHiddenIssueFlagsDocument`, in hidden-issue-flags-contract-checks.ts);
 * a bad body is a distinct `validation_failure` outcome, never partially trusted.
 * The documented non-200s map to typed outcomes: 404 -> `not_available` (the flag
 * is off / the route is unmounted, the "not connected yet" state), 422 ->
 * `validation_error`, 429 -> `rate_limited`, 503 -> `inputs_unavailable`, 500 ->
 * `server_contract_error` / `internal_error`. Browser-level failures are
 * `network_error` / `client_timeout` / `aborted`; anything else is
 * `unexpected_response`. All reflected server text is length-capped.
 *
 * NO legal logic and NO zoning math live here: this module transports and
 * verifies shape only. The §8a layer carries no legal meaning (it reports what
 * the sourced data shows, or 'Check needed'); what any rule requires is the rule
 * engine's and a reviewer's, never the web's.
 */

import { boundedText, boundedToken } from "./bounded";
import { isRecord } from "./scenario-contract-checks";
import { apiBaseUrl } from "./api";
import {
  validateHiddenIssueFlagsDocument,
  type HiddenIssueFlagsDocument,
} from "./hidden-issue-flags-contract-checks";

/** Default request budget, below the Playwright timeout so a slow route is
 * provable in CI without configuration (mirrors study-setup-api.ts). */
export const DEFAULT_TIMEOUT_MS = 12_000;

export interface HiddenIssueFlagsOutcome {
  kind: "flags";
  document: HiddenIssueFlagsDocument;
  correlationId: string | null;
}
/** 404: the route is off (flag unset) or unmounted - the "not connected yet" state. */
export interface NotAvailableOutcome {
  kind: "not_available";
}
export interface ValidationErrorOutcome {
  kind: "validation_error";
  code: string;
  message: string;
  correlationId: string | null;
}
/** 429: the per-caller rate limit was exceeded. Retryable. */
export interface RateLimitedOutcome {
  kind: "rate_limited";
  message: string;
  correlationId: string | null;
}
/** 503: the server could not produce the inputs (upstream/gate). Retryable. */
export interface InputsUnavailableOutcome {
  kind: "inputs_unavailable";
  message: string;
  correlationId: string | null;
}
/** 500 internal_contract_error: the server refused to ship a document that failed its contract. */
export interface ServerContractErrorOutcome {
  kind: "server_contract_error";
  message: string;
  correlationId: string | null;
}
export interface InternalErrorOutcome {
  kind: "internal_error";
  message: string;
  correlationId: string | null;
}
/** A 200 whose body failed CLIENT-side contract validation. */
export interface ValidationFailureOutcome {
  kind: "validation_failure";
  problems: string[];
  correlationId: string | null;
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
  receivedState: string | null;
  correlationId: string | null;
}

export type HiddenIssueFlagsFetchOutcome =
  | HiddenIssueFlagsOutcome
  | NotAvailableOutcome
  | ValidationErrorOutcome
  | RateLimitedOutcome
  | InputsUnavailableOutcome
  | ServerContractErrorOutcome
  | InternalErrorOutcome
  | ValidationFailureOutcome
  | NetworkErrorOutcome
  | ClientTimeoutOutcome
  | AbortedOutcome
  | UnexpectedResponseOutcome;

export interface FetchHiddenIssueFlagsOptions {
  /** Injection point for tests; defaults to the global fetch. */
  fetchImpl?: typeof fetch;
  signal?: AbortSignal;
  timeoutMs?: number;
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return isRecord(value) ? value : null;
}

/** Fetch and verify the §8a hidden-issue flags for one BBL. */
export async function fetchHiddenIssueFlags(
  bbl: string,
  options: FetchHiddenIssueFlagsOptions = {},
): Promise<HiddenIssueFlagsFetchOutcome> {
  const fetchImpl = options.fetchImpl ?? fetch;
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const url = `${apiBaseUrl()}/api/v1/properties/${encodeURIComponent(bbl)}/hidden-issue-flags`;

  const controller = new AbortController();
  let timedOut = false;
  const externalSignal = options.signal;
  if (externalSignal?.aborted) return { kind: "aborted" };
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
      if (timedOut) return { kind: "client_timeout", timeoutMs };
      if (controller.signal.aborted || externalSignal?.aborted) return { kind: "aborted" };
      return {
        kind: "network_error",
        message:
          "The platform API could not be reached. Nothing was retrieved. This is safe to retry.",
      };
    }

    const correlationId = boundedToken(response.headers.get("X-Correlation-ID"));

    // A 404 is the disabled / unmounted sentinel: it carries no JSON state, so
    // classify it by status alone (the "not connected yet" state).
    if (response.status === 404) return { kind: "not_available" };

    let body: unknown = null;
    try {
      body = await response.json();
    } catch {
      if (timedOut) return { kind: "client_timeout", timeoutMs };
      if (controller.signal.aborted || externalSignal?.aborted) return { kind: "aborted" };
      return { kind: "unexpected_response", httpStatus: response.status, receivedState: null, correlationId };
    }
    const record = asRecord(body);
    const state = record && typeof record.state === "string" ? record.state : null;

    if (response.status === 200 && state === null) {
      const validation = validateHiddenIssueFlagsDocument(body);
      if (!validation.ok) {
        return {
          kind: "validation_failure",
          problems: validation.problems.map((problem) =>
            boundedText(problem, "problem detail unavailable"),
          ),
          correlationId,
        };
      }
      return { kind: "flags", document: validation.document, correlationId };
    }

    if (response.status === 422 && state === "validation_error") {
      const detail = asRecord(record?.detail);
      return {
        kind: "validation_error",
        code: boundedToken(detail?.code, 48) ?? "unknown",
        message: boundedText(record?.message, "The BBL was rejected by the API."),
        correlationId,
      };
    }
    if (response.status === 429 && state === "rate_limited") {
      return {
        kind: "rate_limited",
        message: boundedText(record?.message, "Too many requests; please retry later."),
        correlationId,
      };
    }
    if (response.status === 503 && state === "inputs_unavailable") {
      return {
        kind: "inputs_unavailable",
        message: boundedText(record?.message, "The hidden-issue flags are not available right now."),
        correlationId,
      };
    }
    if (response.status === 500 && state === "internal_contract_error") {
      return {
        kind: "server_contract_error",
        message: boundedText(record?.message, "The server refused to deliver a document that failed its contract."),
        correlationId,
      };
    }
    if (response.status === 500 && state === "internal_error") {
      return {
        kind: "internal_error",
        message: boundedText(record?.message, "Unexpected internal error."),
        correlationId,
      };
    }

    // Any other (status, state) pair is outside the documented matrix.
    return {
      kind: "unexpected_response",
      httpStatus: response.status,
      receivedState: state === null ? null : boundedToken(state, 48),
      correlationId,
    };
  } finally {
    clearTimeout(timer);
    externalSignal?.removeEventListener("abort", onExternalAbort);
  }
}
