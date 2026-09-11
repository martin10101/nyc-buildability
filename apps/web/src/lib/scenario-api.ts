/**
 * HARDENED typed client + presentation classifier for the INTERNAL
 * deterministic scenario surface (task M5-T004).
 *
 * Contract: services/api/app/api/v1/scenario.py (read-only dependency), the
 * flag-gated internal GET /api/v1/properties/{bbl}/scenario returning a
 * scenario @ 1.0.0 document.
 *
 * This module transports, verifies shape, and CLASSIFIES a server-computed
 * scenario into a presentation template; it never computes a legal value,
 * never derives a cap, coverage status, district, or share range, and never
 * decides which rule governs (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md — legal
 * logic is the deterministic backend's; the frontend only displays it). The
 * only material number a scenario surfaces — the draft zoning-floor-area cap —
 * is transported VERBATIM from the endpoint body and never recomputed here.
 *
 * Guarantees mirrored from src/lib/api.ts and src/lib/rule-evaluation.ts:
 *   1. EXACT (HTTP status, body state) pair enforcement. A response whose pair
 *      is outside the documented scenario matrix renders as a distinct
 *      `unexpected_response`; a body is never routed by its `state` alone.
 *   2. Every 200 body is runtime-validated against the GENERATED canonical
 *      types (src/lib/scenario-contract.ts) BEFORE any rendering; failure is a
 *      distinct `validation_failure` carrying only a bounded problem list —
 *      nothing partially rendered.
 *   3. All reflected server text is length-capped and control-stripped; the
 *      correlation id is token-allowlisted. This holds on BOTH paths: the
 *      failure path bounds its reflected strings inline below, and the SUCCESS
 *      path is bounded by boundScenarioDocument (src/lib/scenario-bounds.ts)
 *      before the document leaves this module — see that file for the two
 *      rules (arrays reject, strings truncate explicitly) and for the material
 *      values that are deliberately never transformed.
 *   5. The raw body is size-bounded BEFORE it is parsed: a response declaring
 *      more than MAX_RESPONSE_BYTES is rejected into `unexpected_response`
 *      rather than parsed and walked.
 *   4. Requests are cancellable (AbortController) and time-bounded; a
 *      superseded request resolves to `aborted`, a timeout to the recoverable
 *      `client_timeout`.
 *
 * The DISABLED-server case is first-class: when the endpoint is flag-gated off
 * (INTERNAL_SCENARIO_ENABLED absent) or unmounted it returns a generic
 * `404 {"detail":"Not Found"}` with no `state` and no correlation id. That
 * documented (404, null) pair maps to the benign `feature_unavailable`
 * outcome, which the UI shows as an honest "not available in this environment"
 * note rather than an error.
 */

import { apiBaseUrl } from "./api";
import { boundedText, boundedToken } from "./bounded";
import { MAX_RESPONSE_BYTES, boundScenarioDocument } from "./scenario-bounds";
import { type Scenario, validateScenarioDocument } from "./scenario-contract";

/** Default request budget; kept below the Playwright test timeout so the
 * timeout journey is provable in CI without configuration. */
export const DEFAULT_TIMEOUT_MS = 12_000;

// ---------------------------------------------------------------------------
// Outcome union (each documented envelope from scenario.py + the browser-level
// failure modes). Mirrors the rule-evaluation outcome union: the scenario
// matrix equals the rule-evaluation matrix, plus the flag-off (404, null).
// ---------------------------------------------------------------------------

export interface ScenarioOutcomeDoc {
  kind: "scenario";
  document: Scenario;
  correlationId: string | null;
}

/** Endpoint flag-gated off (or unmounted): generic 404 {"detail":"Not Found"},
 * no `state`, no correlation id. Benign — an honest environment note. */
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
export type ScenarioUpstreamFailureState =
  (typeof SCENARIO_UPSTREAM_FAILURE_STATES)[number];

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

/** Documented 500 where the SERVER refused to ship a document that failed its
 * own canonical-contract checks (state=internal_contract_error). */
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

/** Outcomes on which a Retry is meaningful (recoverable server/network
 * faults). `no_match`, `validation_error`, and `feature_unavailable` are
 * results, not recoverable faults, so they carry no Retry. */
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
// Exact (HTTP status, state) pair matrix — mirrors scenario.py
// STATUS_STATE_MATRIX verbatim, plus the flag-off / unmounted generic
// (404, null). The scenario matrix equals the rule-evaluation route's matrix.
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
 * Fetch and classify the internal deterministic scenario for a BBL. Offline by
 * construction: the caller injects `fetchImpl` in tests (committed fixtures);
 * no network, Supabase, or Geoclient dependency lives here.
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
          "The scenario service could not be reached. Nothing was compared, " +
          "and this is safe to retry.",
      };
    }

    const correlationId = boundedToken(response.headers.get("X-Correlation-ID"));

    // SIZE BOUND BEFORE PARSE (G5 finding 1). A response that DECLARES more
    // than the budget is refused without reading it, so `.json()` never parses
    // megabytes and the validator never walks the result. A body arriving with
    // no Content-Length (chunked) cannot be pre-measured without a streaming
    // reader, which would be a new dependency; the array bounds in
    // scenario-contract.ts and the string bounds in scenario-bounds.ts are the
    // backstop for that case.
    const declaredLength = Number(response.headers.get("Content-Length"));
    if (Number.isFinite(declaredLength) && declaredLength > MAX_RESPONSE_BYTES) {
      return {
        kind: "unexpected_response",
        httpStatus: response.status,
        receivedState: null,
        correlationId,
      };
    }

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
    // RAW state for contract checks — sanitizing before comparison could
    // launder a malformed state into a documented one. Bounded form is
    // DISPLAY-only.
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
      // Full runtime validation against the generated canonical types BEFORE
      // anything can render.
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
      // Bound the reflected SUCCESS-path strings before the document can
      // reach a renderer, so the module-header guarantee holds on this path
      // too. Material values are never transformed — see scenario-bounds.ts.
      return {
        kind: "scenario",
        document: boundScenarioDocument(validation.document),
        correlationId,
      };
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
          "The server refused to deliver a scenario that failed its contract checks.",
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
// Presentation classifier — maps a server-computed scenario onto exactly one of
// the three document-derived UI templates from its own `scenario_kind`
// discriminator. NO legal reasoning; the finer framing (professional-review vs
// data-conflict) is read from coverage_status/reasons by the renderer.
// ---------------------------------------------------------------------------

export type ScenarioPresentation = "preliminary" | "no_scenario" | "unsupported";

export function classifyScenario(document: Scenario): ScenarioPresentation {
  return document.scenario_kind;
}

// ---------------------------------------------------------------------------
// Assistive-technology announcement copy for scenario outcome arrivals. Mirror
// of src/lib/announce.ts: derived deterministically from the already-classified
// outcome; no legal semantics, no "verified"/"best"/"guaranteed" wording, no
// invented values. `aborted` announces nothing (a superseded request).
// ---------------------------------------------------------------------------

const SCENARIO_UPSTREAM_ANNOUNCEMENTS: Record<ScenarioUpstreamFailureState, string> = {
  rate_limited: "Scenario unavailable: the official data source is throttling requests.",
  source_unavailable: "Scenario unavailable: the official data source is unavailable.",
  timeout: "Scenario unavailable: the official data source timed out.",
  schema_drift: "Scenario unavailable: the official dataset changed shape.",
};

const SCENARIO_PRESENTATION_ANNOUNCEMENTS: Record<ScenarioPresentation, string> = {
  preliminary:
    "Compare loaded: a preliminary draft scenario that requires professional review.",
  no_scenario:
    "Compare loaded: no preliminary scenario could be stated; the reasons and any preserved ranges are shown.",
  unsupported:
    "Compare loaded: this property is not supported by an implemented rule family yet.",
};

export function announcementForScenario(outcome: ScenarioOutcome): string {
  switch (outcome.kind) {
    case "scenario":
      return SCENARIO_PRESENTATION_ANNOUNCEMENTS[classifyScenario(outcome.document)];
    case "feature_unavailable":
      return "Scenario comparison is not available in this environment.";
    case "no_match":
      return "Compare: no property record found in the official dataset.";
    case "validation_error":
      return "Compare rejected: the API rejected this BBL.";
    case "upstream_failure":
      return SCENARIO_UPSTREAM_ANNOUNCEMENTS[outcome.state];
    case "internal_error":
      return "Compare failed: something went wrong on our side.";
    case "server_contract_error":
      return "Compare failed: the server refused to deliver an invalid scenario document.";
    case "validation_failure":
      return "Compare failed: the response did not match the published data contract.";
    case "network_error":
      return "Compare failed: the scenario service could not be reached.";
    case "client_timeout":
      return "Compare failed: the request took too long and was cancelled.";
    case "unexpected_response":
      return "Compare failed: unexpected response from the platform API.";
    case "aborted":
      return "";
  }
}
