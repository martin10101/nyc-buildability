/**
 * HARDENED typed client + presentation classifier + feature-flag helpers for
 * the INTERNAL draft scenario surface (task M5-T002).
 *
 * Contract: services/api/app/api/v1/scenario.py (read-only dependency), the
 * flag-gated internal GET /api/v1/properties/{bbl}/scenario.
 *
 * This module transports, verifies shape, and CLASSIFIES a server-computed
 * scenario into a presentation template; it never computes a legal value, never
 * recomputes or relabels the surfaced draft zoning-floor-area cap, never decides
 * coverage, and never fills a missing envelope constraint
 * (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md — legal logic is the deterministic
 * backend's and the scenario builder's; the frontend only displays it). Every
 * discriminator the classifier reads (scenario_kind, coverage_status,
 * professional_review_required) is produced by the backend.
 *
 * Guarantees mirrored from src/lib/rule-evaluation.ts, guarantee-for-guarantee:
 *   1. EXACT (HTTP status, body state) pair enforcement. A response whose pair
 *      is outside the documented scenario matrix renders as a distinct
 *      `unexpected_response`; a body is never routed by its `state` alone.
 *   2. Every 200 body is runtime-validated against the GENERATED canonical
 *      types (src/lib/scenario-contract.ts) BEFORE any rendering; failure is a
 *      distinct `validation_failure` carrying only a bounded problem list.
 *   3. All reflected server text is length-capped and control-stripped; the
 *      correlation id is token-allowlisted.
 *   4. Requests are cancellable (AbortController) and time-bounded; a superseded
 *      request resolves to `aborted`, a timeout to the recoverable
 *      `client_timeout`.
 *
 * The DISABLED-server case is first-class: when the endpoint is flag-gated off
 * (or unmounted) it returns a generic `404 {"detail":"Not Found"}` with no
 * `state` and no correlation id. That documented (404, null) pair maps to the
 * benign `feature_unavailable` outcome, which the UI shows as an honest "not
 * available in this environment" note that NEVER blocks the property profile.
 */

import { apiBaseUrl } from "./api";
import { boundedText, boundedToken } from "./bounded";
import { validateScenarioDocument, type Scenario } from "./scenario-contract";

/** Default request budget; kept below the Playwright test timeout so the
 * timeout journey is provable in CI without configuration. */
export const DEFAULT_TIMEOUT_MS = 12_000;

// ---------------------------------------------------------------------------
// Frontend feature flag (defense in depth; the server is independently gated).
//
// The surface is OFF by default and is gated by TWO independent conditions,
// both of which must hold:
//
//  1. ENVIRONMENT: the runtime, server-read variable INTERNAL_SCENARIO_UI holds
//     an explicit true token. The name is intentionally NOT prefixed
//     NEXT_PUBLIC_, so Next never inlines it into the browser bundle at build
//     time and never leaks the flag or the endpoint to the client: the Server
//     Component reads it once per request and passes a plain boolean into the
//     client tree. Absent / empty / unknown -> disabled (fail safe), so a
//     production deploy that never sets it keeps the surface unreachable. (This
//     mirrors rule-evaluation's INTERNAL_RULE_EVAL_UI guarantee-for-guarantee;
//     see the producer report for the deliberate non-public choice.)
//
//  2. PER-REQUEST OPT-IN: the request explicitly asks for the surface via
//     `?scenario=on`. Absent (or `off`) -> disabled. This second factor keeps
//     the experimental surface silent unless deliberately requested even where
//     the environment allows it, and lets the shared single-server e2e harness
//     enable the surface for the scenario journeys WITHOUT rendering it (or
//     issuing its fetch) on any other journey. In production, where the
//     environment gate is closed, the opt-in has no effect at all.
//
// When the resulting boolean is false the surface is never rendered and the
// scenario fetch is never issued.
// ---------------------------------------------------------------------------

const TRUE_TOKENS: ReadonlySet<string> = new Set(["1", "true", "yes", "on"]);
export const INTERNAL_SCENARIO_UI_ENV_VAR = "INTERNAL_SCENARIO_UI";

/** The env-level flag: an explicit true token enables it; absent / empty /
 * unknown -> disabled (fail safe). Read server-side only. */
export function scenarioFlagEnabled(
  rawValue: string | undefined = process.env[INTERNAL_SCENARIO_UI_ENV_VAR],
): boolean {
  return typeof rawValue === "string" && TRUE_TOKENS.has(rawValue.trim().toLowerCase());
}

/** Whether to render the scenario surface for THIS request: the env flag must
 * be on AND the request must explicitly opt in with `?scenario=on`. Default (no
 * env, no params, or `?scenario=off`) is OFF. */
export function scenarioSurfaceEnabled(params?: {
  scenario?: string | string[] | undefined;
}): boolean {
  if (!scenarioFlagEnabled()) return false;
  const raw = params?.scenario;
  const value = Array.isArray(raw) ? raw[0] : raw;
  return typeof value === "string" && TRUE_TOKENS.has(value.trim().toLowerCase());
}

// ---------------------------------------------------------------------------
// Outcome union (each documented envelope from scenario.py + the browser-level
// failure modes). Mirrors rule-evaluation's outcome union.
// ---------------------------------------------------------------------------

export interface ScenarioOutcomeDoc {
  kind: "scenario";
  document: Scenario;
  correlationId: string | null;
}

/** Endpoint flag-gated off (or unmounted): generic 404 {"detail":"Not Found"},
 * no `state`, no correlation id. Benign — never blocks the profile. */
export interface ScenarioFeatureUnavailableOutcome {
  kind: "feature_unavailable";
}

export interface ScenarioNoMatchOutcome {
  kind: "no_match";
  bbl: string | null;
  message: string;
  correlationId: string | null;
}

export interface ScenarioValidationErrorOutcome {
  kind: "validation_error";
  code: string;
  message: string;
  correlationId: string | null;
}

export const SCENARIO_UPSTREAM_FAILURE_STATES = [
  "rate_limited",
  "source_unavailable",
  "timeout",
  "schema_drift",
] as const;
export type ScenarioUpstreamFailureState = (typeof SCENARIO_UPSTREAM_FAILURE_STATES)[number];

export interface ScenarioUpstreamFailureOutcome {
  kind: "upstream_failure";
  state: ScenarioUpstreamFailureState;
  httpStatus: number;
  message: string;
  correlationId: string | null;
}

export interface ScenarioInternalErrorOutcome {
  kind: "internal_error";
  message: string;
  correlationId: string | null;
}

/** Documented 500 where the SERVER refused to ship an invalid document
 * (state=internal_contract_error). */
export interface ScenarioServerContractErrorOutcome {
  kind: "server_contract_error";
  message: string;
  correlationId: string | null;
}

/** A 200 whose body failed CLIENT-side canonical validation. */
export interface ScenarioValidationFailureOutcome {
  kind: "validation_failure";
  problems: string[];
  correlationId: string | null;
}

export interface ScenarioNetworkErrorOutcome {
  kind: "network_error";
  message: string;
}

export interface ScenarioClientTimeoutOutcome {
  kind: "client_timeout";
  timeoutMs: number;
}

export interface ScenarioAbortedOutcome {
  kind: "aborted";
}

export interface ScenarioUnexpectedResponseOutcome {
  kind: "unexpected_response";
  httpStatus: number;
  receivedState: string | null;
  correlationId: string | null;
}

export type ScenarioOutcome =
  | ScenarioOutcomeDoc
  | ScenarioFeatureUnavailableOutcome
  | ScenarioNoMatchOutcome
  | ScenarioValidationErrorOutcome
  | ScenarioUpstreamFailureOutcome
  | ScenarioInternalErrorOutcome
  | ScenarioServerContractErrorOutcome
  | ScenarioValidationFailureOutcome
  | ScenarioNetworkErrorOutcome
  | ScenarioClientTimeoutOutcome
  | ScenarioAbortedOutcome
  | ScenarioUnexpectedResponseOutcome;

/** Outcomes on which a Retry is meaningful (recoverable server/network faults;
 * the profile stays usable regardless). */
export function scenarioOutcomeIsRecoverable(outcome: ScenarioOutcome): boolean {
  return (
    outcome.kind === "upstream_failure" ||
    outcome.kind === "internal_error" ||
    outcome.kind === "server_contract_error" ||
    outcome.kind === "validation_failure" ||
    outcome.kind === "network_error" ||
    outcome.kind === "client_timeout" ||
    outcome.kind === "unexpected_response"
  );
}

// ---------------------------------------------------------------------------
// Exact (HTTP status, state) pair matrix — mirrors scenario.py verbatim (which
// mirrors the rule-evaluation route's error mapping). (404, no_match) is a
// RESULT, and the extra (404, null) pair is the flag-gated / unmounted generic
// Not Found.
// ---------------------------------------------------------------------------

type DocumentedScenarioPair = readonly [number, string | null];

const DOCUMENTED_SCENARIO_PAIRS: readonly DocumentedScenarioPair[] = [
  [200, null], // scenario document (validated client-side before render)
  [404, null], // generic Not Found: feature flag off / route unmounted
  [422, "validation_error"],
  [404, "no_match"],
  [502, "schema_drift"],
  [503, "rate_limited"],
  [503, "source_unavailable"],
  [504, "timeout"],
  [500, "internal_error"],
  [500, "internal_contract_error"],
] as const;

const SCENARIO_PAIR_KEYS: ReadonlySet<string> = new Set(
  DOCUMENTED_SCENARIO_PAIRS.map(([status, state]) => `${status}:${state ?? ""}`),
);

export function isDocumentedScenarioPair(status: number, state: string | null): boolean {
  return SCENARIO_PAIR_KEYS.has(`${status}:${state ?? ""}`);
}

export interface ScenarioLookupOptions {
  fetchImpl?: typeof fetch;
  signal?: AbortSignal;
  timeoutMs?: number;
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

/**
 * Fetch and classify the internal draft scenario result for a BBL. The caller
 * must already have decided the surface is enabled (this function is never
 * invoked when the flag is off — the surface is not rendered at all). Only the
 * bbl path parameter is ever sent; no request body, no query-supplied facts.
 */
export async function fetchScenario(
  bbl: string,
  options: ScenarioLookupOptions = {},
): Promise<ScenarioOutcome> {
  const fetchImpl = options.fetchImpl ?? fetch;
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const url = `${apiBaseUrl()}/api/v1/properties/${encodeURIComponent(bbl)}/scenario`;

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
      if (timedOut) return { kind: "client_timeout", timeoutMs };
      if (controller.signal.aborted || externalSignal?.aborted) return { kind: "aborted" };
      return {
        kind: "network_error",
        message:
          "The draft scenario service could not be reached. Nothing was assembled. " +
          "The property profile above is unaffected, and this is safe to retry.",
      };
    }

    const correlationId = boundedToken(response.headers.get("X-Correlation-ID"));

    let body: unknown = null;
    try {
      body = await response.json();
    } catch {
      if (timedOut) return { kind: "client_timeout", timeoutMs };
      if (controller.signal.aborted || externalSignal?.aborted) return { kind: "aborted" };
      return {
        kind: "unexpected_response",
        httpStatus: response.status,
        receivedState: null,
        correlationId,
      };
    }

    const record = asRecord(body);
    // RAW state for contract checks — sanitizing before comparison could launder
    // a malformed state into a documented one. Bounded form is display-only.
    const state = record && typeof record.state === "string" ? record.state : null;

    if (!isDocumentedScenarioPair(response.status, state)) {
      return {
        kind: "unexpected_response",
        httpStatus: response.status,
        receivedState: state === null ? null : boundedToken(state, 48),
        correlationId,
      };
    }

    if (response.status === 200) {
      const validation = validateScenarioDocument(body);
      if (!validation.ok) {
        return {
          kind: "validation_failure",
          problems: validation.problems.map((problem) =>
            boundedText(problem, "problem detail unavailable"),
          ),
          correlationId,
        };
      }
      return { kind: "scenario", document: validation.document, correlationId };
    }

    // (404, null): generic Not Found — the feature is disabled or unmounted.
    if (response.status === 404 && state === null) {
      return { kind: "feature_unavailable" };
    }

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

    if ((SCENARIO_UPSTREAM_FAILURE_STATES as readonly string[]).includes(state ?? "")) {
      return {
        kind: "upstream_failure",
        state: state as ScenarioUpstreamFailureState,
        httpStatus: response.status,
        message: boundedText(record?.message, "The official data source failed."),
        correlationId,
      };
    }

    if (state === "internal_contract_error") {
      return {
        kind: "server_contract_error",
        message: boundedText(
          record?.message,
          "The server refused to deliver a draft scenario that failed its contract checks.",
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

// ---------------------------------------------------------------------------
// Presentation classifier — maps a server-computed scenario document onto
// exactly one of the honest UI states. It reads ONLY backend discriminators
// (scenario_kind, coverage_status, professional_review_required) and performs
// NO legal reasoning; the priority order picks the most specific honest framing.
// ---------------------------------------------------------------------------

export type ScenarioPresentation =
  | "preliminary_cap" // preliminary scenario: the draft cap is surfaced verbatim
  | "unsupported" // no implemented rule family for this district
  | "conflict" // competing rules / conflicting data; no value
  | "professional_review" // spatial / professional-review uncertainty; no value
  | "missing"; // a required controlling input is absent; no value

export function classifyScenario(document: Scenario): ScenarioPresentation {
  if (document.scenario_kind === "preliminary") return "preliminary_cap";
  const coverage = document.coverage_status;
  if (
    document.scenario_kind === "unsupported" ||
    coverage === "unsupported" ||
    coverage === "not_applicable"
  ) {
    return "unsupported";
  }
  if (coverage === "data_conflict") return "conflict";
  if (document.professional_review_required || coverage === "professional_review_required") {
    return "professional_review";
  }
  return "missing";
}

// ---------------------------------------------------------------------------
// Assistive-technology announcement copy for scenario outcome arrivals. Derived
// deterministically from the already-classified outcome; no legal semantics, no
// "verified"/"best"/"guaranteed" wording, no invented values. `aborted`
// announces nothing (a superseded request).
// ---------------------------------------------------------------------------

const SCENARIO_UPSTREAM_ANNOUNCEMENTS: Record<ScenarioUpstreamFailureState, string> = {
  rate_limited: "Draft scenario unavailable: the official data source is throttling requests.",
  source_unavailable: "Draft scenario unavailable: the official data source is unavailable.",
  timeout: "Draft scenario unavailable: the official data source timed out.",
  schema_drift: "Draft scenario unavailable: the official dataset changed shape.",
};

const SCENARIO_PRESENTATION_ANNOUNCEMENTS: Record<ScenarioPresentation, string> = {
  preliminary_cap:
    "Draft scenario loaded: a preliminary draft zoning-floor-area cap that requires professional review; not a buildable envelope.",
  unsupported:
    "Draft scenario loaded: no draft rule applies to this property, so no scenario was produced.",
  conflict:
    "Draft scenario loaded: conflicting draft rules or data; professional review required and no value produced.",
  professional_review:
    "Draft scenario loaded: professional review required; spatial uncertainty blocks a draft scenario and no value was produced.",
  missing:
    "Draft scenario loaded: a required controlling input is missing, so no draft scenario value was produced.",
};

export function announcementForScenario(outcome: ScenarioOutcome): string {
  switch (outcome.kind) {
    case "scenario":
      return SCENARIO_PRESENTATION_ANNOUNCEMENTS[classifyScenario(outcome.document)];
    case "feature_unavailable":
      return "Draft scenario is not available in this environment.";
    case "no_match":
      return "Draft scenario: no property record found in the official dataset.";
    case "validation_error":
      return "Draft scenario rejected: the API rejected this BBL.";
    case "upstream_failure":
      return SCENARIO_UPSTREAM_ANNOUNCEMENTS[outcome.state];
    case "internal_error":
      return "Draft scenario failed: something went wrong on our side.";
    case "server_contract_error":
      return "Draft scenario failed: the server refused to deliver an invalid draft document.";
    case "validation_failure":
      return "Draft scenario failed: the response did not match the published data contract.";
    case "network_error":
      return "Draft scenario failed: the service could not be reached. The property profile is unaffected.";
    case "client_timeout":
      return "Draft scenario failed: the request took too long and was cancelled.";
    case "unexpected_response":
      return "Draft scenario failed: unexpected response from the platform API.";
    case "aborted":
      return "";
  }
}
