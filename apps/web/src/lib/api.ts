/**
 * HARDENED typed client for GET /api/v1/properties/{bbl} (task M2-T002).
 *
 * Contract: services/api/app/api/v1/properties.py (read-only dependency).
 * The client enforces the EXACT (HTTP status, body state) pair matrix
 * mirrored in src/lib/contract-matrix.ts:
 *
 *   1. Any pair outside the documented matrix — including the recorded
 *      owner-directed regression HTTP 500 + state=no_match — renders as a
 *      distinct `unexpected_response` outcome with the correlation id.
 *      A body is NEVER routed by its `state` alone (scenario S2).
 *   2. Every 200 body is runtime-validated against the GENERATED canonical
 *      types (src/lib/validate-profile.ts) BEFORE any rendering; failure is
 *      a distinct `validation_failure` outcome carrying only the bounded
 *      problem list — nothing partially rendered (scenario S3).
 *   3. All reflected server text is length-capped and control-stripped
 *      (src/lib/bounded.ts); correlation ids are token-allowlisted.
 *   4. Requests are cancellable (AbortController) and time-bounded; a
 *      superseded request resolves to the `aborted` outcome (ignored by the
 *      caller), a timeout to the recoverable `client_timeout` outcome
 *      (scenario S4).
 *
 * No legal logic lives here (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md): this
 * module transports, verifies shape, and classifies; it never computes
 * zoning values, fills in facts, or rewrites coverage labels.
 */

import { boundedText, boundedToken } from "./bounded";
import {
  isDocumentedPair,
  SERVER_CONTRACT_ERROR_STATES,
  UPSTREAM_FAILURE_STATES,
  type ServerContractErrorState,
  type UpstreamFailureState,
} from "./contract-matrix";
import type { PropertyProfile } from "./contract";
import { validateProfileDocument } from "./validate-profile";

export type { ServerContractErrorState, UpstreamFailureState };
export { UPSTREAM_FAILURE_STATES };

/** Default request budget. Kept below the Playwright test timeout so the
 * timeout journey is provable in CI without configuration. */
export const DEFAULT_TIMEOUT_MS = 12_000;

export interface ProfileOutcome {
  kind: "profile";
  profile: PropertyProfile;
  correlationId: string | null;
}

export interface NoMatchOutcome {
  kind: "no_match";
  bbl: string | null;
  /** Actionable explanation from the API (e.g. condo billing-lot guidance). */
  message: string;
  correlationId: string | null;
}

export interface ValidationErrorOutcome {
  kind: "validation_error";
  /** Typed code from detail.code (e.g. invalid_block). */
  code: string;
  message: string;
  correlationId: string | null;
}

export interface UpstreamFailureOutcome {
  kind: "upstream_failure";
  state: UpstreamFailureState;
  httpStatus: number;
  message: string;
  correlationId: string | null;
}

export interface InternalErrorOutcome {
  kind: "internal_error";
  message: string;
  correlationId: string | null;
}

/** Documented 500s where the SERVER refused to ship an invalid profile
 * (internal_contract_error / unsupported_contract_version, task M2-T003). */
export interface ServerContractErrorOutcome {
  kind: "server_contract_error";
  state: ServerContractErrorState;
  message: string;
  correlationId: string | null;
}

/** A 200 whose body failed CLIENT-side canonical validation (scenario S3). */
export interface ValidationFailureOutcome {
  kind: "validation_failure";
  problems: string[];
  correlationId: string | null;
}

/** Browser-level failure: server unreachable, DNS, connection refused… */
export interface NetworkErrorOutcome {
  kind: "network_error";
  message: string;
}

/** The client-side request budget elapsed; recoverable via retry. */
export interface ClientTimeoutOutcome {
  kind: "client_timeout";
  timeoutMs: number;
}

/** The request was cancelled because a newer lookup superseded it. */
export interface AbortedOutcome {
  kind: "aborted";
}

/** Anything outside the documented (status, state) pair matrix. */
export interface UnexpectedResponseOutcome {
  kind: "unexpected_response";
  httpStatus: number;
  /** Bounded body state token, when one was present (e.g. the recorded
   * 500+no_match regression pair) — shown so the mismatch is inspectable. */
  receivedState: string | null;
  correlationId: string | null;
}

export type LookupOutcome =
  | ProfileOutcome
  | NoMatchOutcome
  | ValidationErrorOutcome
  | UpstreamFailureOutcome
  | InternalErrorOutcome
  | ServerContractErrorOutcome
  | ValidationFailureOutcome
  | NetworkErrorOutcome
  | ClientTimeoutOutcome
  | AbortedOutcome
  | UnexpectedResponseOutcome;

export interface LookupOptions {
  /** Injection point for tests; defaults to the global fetch. */
  fetchImpl?: typeof fetch;
  /** External cancellation (superseding lookup, unmount). */
  signal?: AbortSignal;
  timeoutMs?: number;
}

/**
 * API base URL. NEXT_PUBLIC_API_BASE_URL is compiled into the browser bundle
 * at build time (publishable name only — see apps/web/.env.example). The
 * default matches local/CI development where the FastAPI service listens on
 * 127.0.0.1:8000.
 */
export function apiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

export async function fetchPropertyProfile(
  bbl: string,
  options: LookupOptions = {},
): Promise<LookupOutcome> {
  const fetchImpl = options.fetchImpl ?? fetch;
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const url = `${apiBaseUrl()}/api/v1/properties/${encodeURIComponent(bbl)}`;

  // One internal controller merges the two cancellation sources: the
  // caller's signal (supersession/unmount) and the timeout budget.
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
          "The platform API could not be reached. Nothing was retrieved. " +
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
    // RAW state for contract checks — sanitizing before comparison could
    // launder a malformed state (e.g. embedded control characters) into a
    // documented one. Bounded form is used for DISPLAY only.
    const state = record && typeof record.state === "string" ? record.state : null;

    // ------------------------------------------------------------------
    // EXACT pair enforcement (scenario S2). The body's `state` is only
    // trusted when the (HTTP status, state) pair is in the documented
    // matrix. HTTP 500 + state=no_match — the recorded regression fixture
    // — fails this check and can NEVER reach the no-match rendering path.
    // ------------------------------------------------------------------
    if (!isDocumentedPair(response.status, state)) {
      return {
        kind: "unexpected_response",
        httpStatus: response.status,
        receivedState: state === null ? null : boundedToken(state, 48),
        correlationId,
      };
    }

    if (response.status === 200) {
      // Full runtime validation against the generated canonical types
      // BEFORE anything can render (scenario S3).
      const validation = validateProfileDocument(body);
      if (!validation.ok) {
        return {
          kind: "validation_failure",
          problems: validation.problems.map((problem) =>
            boundedText(problem, "problem detail unavailable"),
          ),
          correlationId,
        };
      }
      return { kind: "profile", profile: validation.profile, correlationId };
    }

    // Documented non-200 pairs. `state` is non-null for all of them.
    if (state === "no_match") {
      return {
        kind: "no_match",
        bbl: typeof record?.bbl === "string" ? boundedToken(record.bbl, 32) : null,
        message: boundedText(
          record?.message,
          "No record was found for this BBL in the current official dataset.",
        ),
        correlationId,
      };
    }

    if (state === "validation_error") {
      const detail = asRecord(record?.detail);
      return {
        kind: "validation_error",
        code: boundedToken(detail?.code, 48) ?? "unknown",
        message: boundedText(record?.message, "The BBL was rejected by the API."),
        correlationId,
      };
    }

    if ((UPSTREAM_FAILURE_STATES as readonly string[]).includes(state ?? "")) {
      return {
        kind: "upstream_failure",
        state: state as UpstreamFailureState,
        httpStatus: response.status,
        message: boundedText(record?.message, "The official data source failed."),
        correlationId,
      };
    }

    if ((SERVER_CONTRACT_ERROR_STATES as readonly string[]).includes(state ?? "")) {
      return {
        kind: "server_contract_error",
        state: state as ServerContractErrorState,
        message: boundedText(
          record?.message,
          "The server refused to deliver a profile that failed its contract checks.",
        ),
        correlationId,
      };
    }

    // Only (500, internal_error) remains in the documented matrix.
    return {
      kind: "internal_error",
      message: boundedText(record?.message, "Unexpected internal error."),
      correlationId,
    };
  } finally {
    clearTimeout(timer);
    externalSignal?.removeEventListener("abort", onExternalAbort);
  }
}
