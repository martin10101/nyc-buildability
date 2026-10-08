/**
 * Typed client for the internal results route (task M5-T140, Part B of the R6B results
 * connection; ruling R9).
 *
 * Contract: services/api/app/api/v1/results_read.py (read-only dependency). The route
 * POSTs one lot's OPTION — the housing program, an optional floor-to-floor height and an
 * optional statement about the special density area (results_request.py:47-55) — and
 * returns the emitted contract-1.3.0 three-way results document behind the default-off
 * INTERNAL_RESULTS_ENABLED flag. The website sends the option; every lot FACT comes from
 * the server's evidence, never the caller.
 *
 * `fetchResults(bbl, body, options)` transports and verifies. Every 200 body is
 * runtime-validated against the contract shape BEFORE anything can use it
 * (`validateResultsDocument`); a bad body is a distinct `validation_failure` outcome,
 * never partially trusted. Each documented (HTTP status, state) pair of the route's
 * RESULTS_READ_STATUS_STATE_MATRIX maps to one typed outcome; browser-level failures are
 * `network_error` / `client_timeout` / `aborted`; anything else is `unexpected_response`.
 * All reflected server text is length-capped (bounded.ts).
 *
 * NO legal logic and NO zoning math live here: this module transports, verifies shape and
 * hands the verified document to the panel. It holds NO copy of a server value.
 */

import { apiBaseUrl } from "./api";
import { boundedText, boundedToken } from "./bounded";
import { isRecord } from "./scenario-contract-checks";
import { validateResultsDocument } from "./results-contract-checks";
import type { ThreeAnswersResults } from "./architect/three-answers";

/** Default request budget, below the Playwright timeout so a slow route is provable in CI
 * without configuration (mirrors study-setup-api.ts and src/lib/api.ts). */
export const DEFAULT_TIMEOUT_MS = 12_000;

/** The caller's option body. The height and the statement are OMITTED when not made; an
 * absent height means "use the program's starting height" and an absent statement means
 * "no statement" (never a sent false/zero). */
export interface ResultsRequestBody {
  housing_program: "standard_residence" | "qualifying_affordable_housing" | "qualifying_senior_housing";
  floor_to_floor_ft?: number;
  special_density_statement?: boolean;
}

export interface SuccessOutcome {
  kind: "success";
  document: ThreeAnswersResults;
  correlationId: string | null;
}
/** 404: the route is off (flag unset) or unmounted — the "not connected yet" state. */
export interface NotAvailableOutcome {
  kind: "not_available";
}
export interface ValidationErrorOutcome {
  kind: "validation_error";
  code: string;
  field: string | null;
  message: string;
  correlationId: string | null;
}
export interface RateLimitedOutcome {
  kind: "rate_limited";
  message: string;
  correlationId: string | null;
}
/** 503 inputs_unavailable: the provider could not produce the lot's inputs. Safe to retry. */
export interface InputsUnavailableOutcome {
  kind: "inputs_unavailable";
  message: string;
  correlationId: string | null;
}
/** 503 lot_conditions_unconfirmed: a recorded fact needed for this lot could not be read. The
 * same request would not succeed on a retry, so this is NOT labelled safe to retry. */
export interface LotConditionsUnconfirmedOutcome {
  kind: "lot_conditions_unconfirmed";
  message: string;
  correlationId: string | null;
}
export interface InternalErrorOutcome {
  kind: "internal_error";
  message: string;
  correlationId: string | null;
}
/** 500 internal_contract_error: the server refused to ship a document that failed its contract. */
export interface InternalContractErrorOutcome {
  kind: "internal_contract_error";
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

export type ResultsFetchOutcome =
  | SuccessOutcome
  | NotAvailableOutcome
  | ValidationErrorOutcome
  | RateLimitedOutcome
  | InputsUnavailableOutcome
  | LotConditionsUnconfirmedOutcome
  | InternalErrorOutcome
  | InternalContractErrorOutcome
  | ValidationFailureOutcome
  | NetworkErrorOutcome
  | ClientTimeoutOutcome
  | AbortedOutcome
  | UnexpectedResponseOutcome;

export interface FetchResultsOptions {
  /** Injection point for tests; defaults to the global fetch. */
  fetchImpl?: typeof fetch;
  signal?: AbortSignal;
  timeoutMs?: number;
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return isRecord(value) ? value : null;
}

/** POST the option for one BBL and verify the returned results document. */
export async function fetchResults(
  bbl: string,
  body: ResultsRequestBody,
  options: FetchResultsOptions = {},
): Promise<ResultsFetchOutcome> {
  const fetchImpl = options.fetchImpl ?? fetch;
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const url = `${apiBaseUrl()}/api/v1/properties/${encodeURIComponent(bbl)}/results`;

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
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(body),
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

    // A 404 is the disabled / unmounted sentinel: it carries no JSON state, so classify it by
    // status alone (the "not connected yet" state).
    if (response.status === 404) return { kind: "not_available" };

    let payload: unknown = null;
    try {
      payload = await response.json();
    } catch {
      if (timedOut) return { kind: "client_timeout", timeoutMs };
      if (controller.signal.aborted || externalSignal?.aborted) return { kind: "aborted" };
      return { kind: "unexpected_response", httpStatus: response.status, receivedState: null, correlationId };
    }
    const record = asRecord(payload);
    const state = record && typeof record.state === "string" ? record.state : null;

    if (response.status === 200 && state === null) {
      const validation = validateResultsDocument(payload);
      if (!validation.ok) {
        return {
          kind: "validation_failure",
          problems: validation.problems.map(problem => boundedText(problem, "problem detail unavailable")),
          correlationId,
        };
      }
      return { kind: "success", document: validation.document, correlationId };
    }

    if (response.status === 422 && state === "validation_error") {
      const detail = asRecord(record?.detail);
      return {
        kind: "validation_error",
        code: boundedToken(detail?.code, 48) ?? "unknown",
        field: boundedToken(detail?.field, 48),
        message: boundedText(record?.message, "The request could not be understood."),
        correlationId,
      };
    }
    if (response.status === 429 && state === "rate_limited") {
      return {
        kind: "rate_limited",
        message: boundedText(record?.message, "Too many requests. Try again shortly."),
        correlationId,
      };
    }
    if (response.status === 503 && state === "inputs_unavailable") {
      return {
        kind: "inputs_unavailable",
        message: boundedText(record?.message, "The results could not be loaded right now."),
        correlationId,
      };
    }
    if (response.status === 503 && state === "lot_conditions_unconfirmed") {
      return {
        kind: "lot_conditions_unconfirmed",
        message: boundedText(
          record?.message,
          "A recorded fact needed to work out this lot's results could not be read.",
        ),
        correlationId,
      };
    }
    if (response.status === 500 && state === "internal_contract_error") {
      return {
        kind: "internal_contract_error",
        message: boundedText(record?.message, "The server held back a result that failed its own checks."),
        correlationId,
      };
    }
    if (response.status === 500 && state === "internal_error") {
      return {
        kind: "internal_error",
        message: boundedText(record?.message, "Something went wrong on the server."),
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
