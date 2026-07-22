/**
 * HARDENED typed client + presentation classifier + feature-flag helpers for
 * the INTERNAL draft rule-evaluation surface (task M4-T005 phase 3).
 *
 * Contract: services/api/app/api/v1/rule_evaluation.py (read-only dependency),
 * the flag-gated internal GET /api/v1/properties/{bbl}/rule-evaluation.
 *
 * This module transports, verifies shape, and CLASSIFIES a server-computed
 * result into a presentation template; it never computes a legal value, never
 * derives a district, coverage status, conflict, or share range, and never
 * decides which rule governs (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md — legal
 * logic is the deterministic backend's; the frontend only displays it). Every
 * discriminator the classifier reads (coverage_status, fail_safe,
 * fail_safe_reason, rule_conflict.conflict) is produced by the backend.
 *
 * Guarantees mirrored from src/lib/api.ts:
 *   1. EXACT (HTTP status, body state) pair enforcement. A response whose pair
 *      is outside the documented rule-eval matrix renders as a distinct
 *      `unexpected_response`; a body is never routed by its `state` alone.
 *   2. Every 200 body is runtime-validated against the GENERATED canonical
 *      types (src/lib/rule-evaluation-contract.ts) BEFORE any rendering;
 *      failure is a distinct `validation_failure` carrying only a bounded
 *      problem list.
 *   3. All reflected server text is length-capped and control-stripped; the
 *      correlation id is token-allowlisted.
 *   4. Requests are cancellable (AbortController) and time-bounded; a
 *      superseded request resolves to `aborted`, a timeout to the recoverable
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
import {
  validateRuleEvaluationDocument,
  type RuleEvaluation,
} from "./rule-evaluation-contract";

/** Default request budget; kept below the Playwright test timeout so the
 * timeout journey is provable in CI without configuration. */
export const DEFAULT_TIMEOUT_MS = 12_000;

// ---------------------------------------------------------------------------
// Frontend feature flag (defense in depth; the server is independently gated).
//
// The surface is OFF by default and is gated by TWO independent conditions,
// both of which must hold:
//
//  1. ENVIRONMENT: the runtime, server-read variable INTERNAL_RULE_EVAL_UI
//     holds an explicit true token. The name is intentionally NOT prefixed
//     NEXT_PUBLIC_, so Next never inlines it into the browser bundle at build
//     time and never leaks the flag or the endpoint to the client: the Server
//     Component reads it once per request and passes a plain boolean into the
//     client tree. Absent / empty / unknown -> disabled (fail safe), so a
//     production deploy that never sets it keeps the surface unreachable.
//
//  2. PER-REQUEST OPT-IN: the request explicitly asks for the surface via
//     `?ruleeval=on`. Absent (or `off`) -> disabled. This second factor keeps
//     the experimental surface silent unless deliberately requested even where
//     the environment allows it, and lets the shared single-server e2e harness
//     enable the surface for the rule-evaluation journeys WITHOUT rendering it
//     (or issuing its fetch) on any other journey. In production, where the
//     environment gate is closed, the opt-in has no effect at all.
//
// When the resulting boolean is false the surface is never rendered and the
// rule-evaluation fetch is never issued.
// ---------------------------------------------------------------------------

const TRUE_TOKENS: ReadonlySet<string> = new Set(["1", "true", "yes", "on"]);
export const INTERNAL_RULE_EVAL_UI_ENV_VAR = "INTERNAL_RULE_EVAL_UI";

/** The env-level flag: an explicit true token enables it; absent / empty /
 * unknown -> disabled (fail safe). Read server-side only. */
export function ruleEvaluationFlagEnabled(
  rawValue: string | undefined = process.env[INTERNAL_RULE_EVAL_UI_ENV_VAR],
): boolean {
  return typeof rawValue === "string" && TRUE_TOKENS.has(rawValue.trim().toLowerCase());
}

/** Whether to render the rule-evaluation surface for THIS request: the env
 * flag must be on AND the request must explicitly opt in with `?ruleeval=on`.
 * Default (no env, no params, or `?ruleeval=off`) is OFF. */
export function ruleEvaluationSurfaceEnabled(params?: {
  ruleeval?: string | string[] | undefined;
}): boolean {
  if (!ruleEvaluationFlagEnabled()) return false;
  const raw = params?.ruleeval;
  const value = Array.isArray(raw) ? raw[0] : raw;
  return typeof value === "string" && TRUE_TOKENS.has(value.trim().toLowerCase());
}

// ---------------------------------------------------------------------------
// Outcome union (each documented envelope from rule_evaluation.py + the
// browser-level failure modes).
// ---------------------------------------------------------------------------

export interface RuleEvaluationOutcomeDoc {
  kind: "evaluation";
  document: RuleEvaluation;
  correlationId: string | null;
}

/** Endpoint flag-gated off (or unmounted): generic 404 {"detail":"Not Found"},
 * no `state`, no correlation id. Benign — never blocks the profile. */
export interface FeatureUnavailableOutcome {
  kind: "feature_unavailable";
}

export interface RuleNoMatchOutcome {
  kind: "no_match";
  bbl: string | null;
  message: string;
  correlationId: string | null;
}

export interface RuleValidationErrorOutcome {
  kind: "validation_error";
  code: string;
  message: string;
  correlationId: string | null;
}

export const RULE_UPSTREAM_FAILURE_STATES = [
  "rate_limited",
  "source_unavailable",
  "timeout",
  "schema_drift",
] as const;
export type RuleUpstreamFailureState = (typeof RULE_UPSTREAM_FAILURE_STATES)[number];

export interface RuleUpstreamFailureOutcome {
  kind: "upstream_failure";
  state: RuleUpstreamFailureState;
  httpStatus: number;
  message: string;
  correlationId: string | null;
}

export interface RuleInternalErrorOutcome {
  kind: "internal_error";
  message: string;
  correlationId: string | null;
}

/** Documented 500 where the SERVER refused to ship an invalid document
 * (state=internal_contract_error). */
export interface RuleServerContractErrorOutcome {
  kind: "server_contract_error";
  message: string;
  correlationId: string | null;
}

/** A 200 whose body failed CLIENT-side canonical validation. */
export interface RuleValidationFailureOutcome {
  kind: "validation_failure";
  problems: string[];
  correlationId: string | null;
}

export interface RuleNetworkErrorOutcome {
  kind: "network_error";
  message: string;
}

export interface RuleClientTimeoutOutcome {
  kind: "client_timeout";
  timeoutMs: number;
}

export interface RuleAbortedOutcome {
  kind: "aborted";
}

export interface RuleUnexpectedResponseOutcome {
  kind: "unexpected_response";
  httpStatus: number;
  receivedState: string | null;
  correlationId: string | null;
}

export type RuleEvaluationOutcome =
  | RuleEvaluationOutcomeDoc
  | FeatureUnavailableOutcome
  | RuleNoMatchOutcome
  | RuleValidationErrorOutcome
  | RuleUpstreamFailureOutcome
  | RuleInternalErrorOutcome
  | RuleServerContractErrorOutcome
  | RuleValidationFailureOutcome
  | RuleNetworkErrorOutcome
  | RuleClientTimeoutOutcome
  | RuleAbortedOutcome
  | RuleUnexpectedResponseOutcome;

/** Outcomes on which a Retry is meaningful (recoverable server/network faults;
 * the profile stays usable regardless). */
export function ruleOutcomeIsRecoverable(outcome: RuleEvaluationOutcome): boolean {
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
// Exact (HTTP status, state) pair matrix — mirrors rule_evaluation.py verbatim.
// Distinct from the property matrix: (404, no_match) is a RESULT, and the extra
// (404, null) pair is the flag-gated / unmounted generic Not Found.
// ---------------------------------------------------------------------------

type DocumentedRulePair = readonly [number, string | null];

const DOCUMENTED_RULE_PAIRS: readonly DocumentedRulePair[] = [
  [200, null], // rule_evaluation document (validated client-side before render)
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

const RULE_PAIR_KEYS: ReadonlySet<string> = new Set(
  DOCUMENTED_RULE_PAIRS.map(([status, state]) => `${status}:${state ?? ""}`),
);

export function isDocumentedRulePair(status: number, state: string | null): boolean {
  return RULE_PAIR_KEYS.has(`${status}:${state ?? ""}`);
}

export interface RuleEvaluationLookupOptions {
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
 * Fetch and classify the internal draft rule-evaluation result for a BBL. The
 * caller must already have decided the surface is enabled (this function is
 * never invoked when the flag is off — the surface is not rendered at all).
 */
export async function fetchRuleEvaluation(
  bbl: string,
  options: RuleEvaluationLookupOptions = {},
): Promise<RuleEvaluationOutcome> {
  const fetchImpl = options.fetchImpl ?? fetch;
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const url = `${apiBaseUrl()}/api/v1/properties/${encodeURIComponent(bbl)}/rule-evaluation`;

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
          "The draft rule-evaluation service could not be reached. Nothing was " +
          "evaluated. The property profile above is unaffected, and this is safe to retry.",
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
    // RAW state for contract checks — sanitizing before comparison could
    // launder a malformed state into a documented one. Bounded form is display-only.
    const state = record && typeof record.state === "string" ? record.state : null;

    if (!isDocumentedRulePair(response.status, state)) {
      return {
        kind: "unexpected_response",
        httpStatus: response.status,
        receivedState: state === null ? null : boundedToken(state, 48),
        correlationId,
      };
    }

    if (response.status === 200) {
      const validation = validateRuleEvaluationDocument(body);
      if (!validation.ok) {
        return {
          kind: "validation_failure",
          problems: validation.problems.map((problem) =>
            boundedText(problem, "problem detail unavailable"),
          ),
          correlationId,
        };
      }
      return { kind: "evaluation", document: validation.document, correlationId };
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

    if ((RULE_UPSTREAM_FAILURE_STATES as readonly string[]).includes(state ?? "")) {
      return {
        kind: "upstream_failure",
        state: state as RuleUpstreamFailureState,
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
          "The server refused to deliver a draft evaluation that failed its contract checks.",
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
// Presentation classifier — maps a server-computed document onto exactly one
// of the five result-derived UI states. It reads ONLY backend discriminators
// and performs NO legal reasoning; the priority order simply picks the most
// specific honest framing.
// ---------------------------------------------------------------------------

export type RuleEvalPresentation =
  | "applicable_draft" // 1. a draft determination with computed outputs
  | "unsupported" // 2. coverage_status unsupported / not_applicable
  | "spatial_uncertainty" // 5. split-lot / data-conflict: share ranges preserved
  | "rule_conflict" // 4. typed same-family rule conflict
  | "missing_evidence"; // 3. fail-safe professional-review (absent substrate / lot area)

export function classifyRuleEvaluation(document: RuleEvaluation): RuleEvalPresentation {
  if (document.rule_conflict?.conflict === true) return "rule_conflict";
  const coverage = document.coverage_status;
  if (coverage === "unsupported" || coverage === "not_applicable") return "unsupported";
  const reason = document.fail_safe_reason;
  if (
    reason === "geometry_uncertain" ||
    reason === "data_conflict" ||
    reason === "inconsistent_confident_geometry"
  ) {
    return "spatial_uncertainty";
  }
  if (
    document.fail_safe ||
    document.professional_review_required ||
    coverage === "professional_review_required"
  ) {
    return "missing_evidence";
  }
  return "applicable_draft";
}

// ---------------------------------------------------------------------------
// Assistive-technology announcement copy for rule-eval outcome arrivals. Mirror
// of src/lib/announce.ts: derived deterministically from the already-classified
// outcome; no legal semantics, no "verified"/"best"/"guaranteed" wording, no
// invented values. `aborted` announces nothing (a superseded request).
// ---------------------------------------------------------------------------

const RULE_UPSTREAM_ANNOUNCEMENTS: Record<RuleUpstreamFailureState, string> = {
  rate_limited: "Draft evaluation unavailable: the official data source is throttling requests.",
  source_unavailable: "Draft evaluation unavailable: the official data source is unavailable.",
  timeout: "Draft evaluation unavailable: the official data source timed out.",
  schema_drift: "Draft evaluation unavailable: the official dataset changed shape.",
};

const PRESENTATION_ANNOUNCEMENTS: Record<RuleEvalPresentation, string> = {
  applicable_draft:
    "Draft rule evaluation loaded: an unreviewed draft determination that requires professional review.",
  unsupported:
    "Draft rule evaluation loaded: no draft rule applies to this property.",
  spatial_uncertainty:
    "Draft rule evaluation loaded: spatial uncertainty — the lot spans districts, shown as ranges; professional review required.",
  rule_conflict:
    "Draft rule evaluation loaded: conflicting draft rules; professional review required and no value produced.",
  missing_evidence:
    "Draft rule evaluation loaded: professional review required; the evidence needed for a draft determination is missing.",
};

export function announcementForRuleEvaluation(outcome: RuleEvaluationOutcome): string {
  switch (outcome.kind) {
    case "evaluation":
      return PRESENTATION_ANNOUNCEMENTS[classifyRuleEvaluation(outcome.document)];
    case "feature_unavailable":
      return "Draft rule evaluation is not available in this environment.";
    case "no_match":
      return "Draft evaluation: no property record found in the official dataset.";
    case "validation_error":
      return "Draft evaluation rejected: the API rejected this BBL.";
    case "upstream_failure":
      return RULE_UPSTREAM_ANNOUNCEMENTS[outcome.state];
    case "internal_error":
      return "Draft evaluation failed: something went wrong on our side.";
    case "server_contract_error":
      return "Draft evaluation failed: the server refused to deliver an invalid draft document.";
    case "validation_failure":
      return "Draft evaluation failed: the response did not match the published data contract.";
    case "network_error":
      return "Draft evaluation failed: the service could not be reached. The property profile is unaffected.";
    case "client_timeout":
      return "Draft evaluation failed: the request took too long and was cancelled.";
    case "unexpected_response":
      return "Draft evaluation failed: unexpected response from the platform API.";
    case "aborted":
      return "";
  }
}
