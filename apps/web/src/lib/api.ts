/**
 * Typed client for GET /api/v1/properties/{bbl} (task M2-T001).
 *
 * The response contract is defined by services/api/app/api/v1/properties.py
 * (read-only dependency):
 *
 *   200  canonical property profile (no `state` key)
 *   404  state=no_match          — a RESULT, not an error (condo unit lots
 *                                  include the billing-lot explanation)
 *   422  state=validation_error  — detail.code + message
 *   502  state=schema_drift
 *   503  state=rate_limited | source_unavailable
 *   504  state=timeout
 *   500  state=internal_error    — generic; correlation id only
 *
 * `state` is THE discriminator on non-200 responses (M1-T005 G3 section 5):
 * a plain routing 404 (or any body without a recognized `state`) is mapped
 * to `unexpected_response`, never to `no_match`.
 *
 * No legal logic lives here (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md): this
 * module transports and classifies responses; it never computes zoning
 * values, never fills in missing facts, and never rewrites coverage labels.
 */

import type { PropertyProfile } from "./property-profile";

/** Documented upstream-failure states (5xx family with typed bodies). */
export const UPSTREAM_FAILURE_STATES = [
  "rate_limited",
  "source_unavailable",
  "timeout",
  "schema_drift",
] as const;
export type UpstreamFailureState = (typeof UPSTREAM_FAILURE_STATES)[number];

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

/** Browser-level failure: server unreachable, DNS, connection refused… */
export interface NetworkErrorOutcome {
  kind: "network_error";
  message: string;
}

/** Anything outside the documented contract (e.g. a routing 404 with no state). */
export interface UnexpectedResponseOutcome {
  kind: "unexpected_response";
  httpStatus: number;
  correlationId: string | null;
}

export type LookupOutcome =
  | ProfileOutcome
  | NoMatchOutcome
  | ValidationErrorOutcome
  | UpstreamFailureOutcome
  | InternalErrorOutcome
  | NetworkErrorOutcome
  | UnexpectedResponseOutcome;

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

function textOrFallback(value: unknown, fallback: string): string {
  return typeof value === "string" && value.trim() !== "" ? value : fallback;
}

export async function fetchPropertyProfile(
  bbl: string,
  fetchImpl: typeof fetch = fetch,
): Promise<LookupOutcome> {
  const url = `${apiBaseUrl()}/api/v1/properties/${encodeURIComponent(bbl)}`;
  let response: Response;
  try {
    response = await fetchImpl(url, {
      method: "GET",
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
  } catch {
    return {
      kind: "network_error",
      message:
        "The platform API could not be reached. Nothing was retrieved. " +
        "This lookup is safe to retry.",
    };
  }

  const correlationId = response.headers.get("X-Correlation-ID");

  let body: unknown = null;
  try {
    body = await response.json();
  } catch {
    return { kind: "unexpected_response", httpStatus: response.status, correlationId };
  }
  const record = asRecord(body);

  if (response.status === 200) {
    // 200 carries the canonical profile document and no `state` key.
    if (record && asRecord(record.profile_version) && asRecord(record.identity)) {
      return { kind: "profile", profile: body as PropertyProfile, correlationId };
    }
    return { kind: "unexpected_response", httpStatus: 200, correlationId };
  }

  const state = record && typeof record.state === "string" ? record.state : null;

  if (state === "no_match") {
    return {
      kind: "no_match",
      bbl: typeof record?.bbl === "string" ? record.bbl : null,
      message: textOrFallback(
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
      code: textOrFallback(detail?.code, "unknown"),
      message: textOrFallback(record?.message, "The BBL was rejected by the API."),
      correlationId,
    };
  }

  if ((UPSTREAM_FAILURE_STATES as readonly string[]).includes(state ?? "")) {
    return {
      kind: "upstream_failure",
      state: state as UpstreamFailureState,
      httpStatus: response.status,
      message: textOrFallback(record?.message, "The official data source failed."),
      correlationId,
    };
  }

  if (state === "internal_error") {
    return {
      kind: "internal_error",
      message: textOrFallback(record?.message, "Unexpected internal error."),
      correlationId,
    };
  }

  // No recognized `state` — e.g. a routing 404. NEVER treated as no_match.
  return { kind: "unexpected_response", httpStatus: response.status, correlationId };
}
