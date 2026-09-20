/**
 * HARDENED typed POST client for the INTERNAL proposal-checks route
 * (task M5-T060, D-076 phase B3 slice 2).
 *
 * Contract: services/api/app/api/v1/proposal_checks_api.py (read-only
 * dependency) — the flag-gated internal POST /api/v1/proposal-checks that runs
 * the accepted B2 check engine over an editor-authored proposal and returns the
 * grouped PASS / FAIL / COULD_NOT_CHECK report (services/api/app/rules/
 * proposal_checks.py `ProposalCheckReport.as_dict`).
 *
 * Discipline copied EXACTLY from src/lib/scenario-api.ts (the accepted internal
 * client precedent):
 *   1. EXACT (HTTP status, state) pair enforcement mirroring the route's
 *      PROPOSAL_CHECKS_STATUS_STATE_MATRIX verbatim, plus the flag-off /
 *      unmounted generic (404, null) -> feature_unavailable. A body is never
 *      routed by its `state` alone.
 *   2. The raw body is size-bounded BEFORE it is parsed: Content-Length must be
 *      a plain digit string within MAX_RESPONSE_BYTES; absent / blank /
 *      non-numeric / over-budget all FAIL CLOSED to unexpected_response.
 *   3. Every reflected server string is length-capped/control-stripped
 *      (boundedText) or token-allowlisted (boundedToken) BEFORE it leaves this
 *      module — the DB-039(k) render-escaping obligation. Numbers pass through
 *      verbatim (the server value is the truth), strings are bounded. No raw-HTML
 *      injection sink is used anywhere in this packet.
 *   4. Requests are cancellable (AbortController) and time-bounded; a superseded
 *      request resolves to `aborted`, a timeout to the recoverable
 *      `client_timeout`. `fetchImpl` is injectable for offline tests.
 *
 * This module TRANSPORTS and BOUNDS; it computes no legal value and never
 * re-derives an allowance, coverage status, or shortfall — the server refusal
 * remains the single truth surface.
 */

import { apiBaseUrl } from "./api";
import { boundedText, boundedToken } from "./bounded";

/** Default request budget; kept below the Playwright test timeout so the
 * timeout journey is provable in CI without configuration. */
export const DEFAULT_TIMEOUT_MS = 12_000;

/** Response-body ceiling before parse (fail-closed). The route's report is a
 * small grouped document; a response declaring more than this is rejected
 * rather than parsed and walked. */
export const MAX_RESPONSE_BYTES = 512_000;

// ---------------------------------------------------------------------------
// Request shape — mirrors the route's documented request contract exactly:
//   { proposed_massing, lot, lot_rule_facts, scenario_label, proposal_id }.
// The 2263 outline is the numeric authority; no display CRS or transform lives
// here (the 4326->2263 bridge is a deferred D-076-R003 owner-checkpoint
// question, deliberately absent).
// ---------------------------------------------------------------------------
export interface ProposalCheckRequest {
  proposed_massing: {
    outline: { srid: number; vertices: Array<[number, number]> };
    levels: Array<{ level_index: number; floor_count: number; floor_to_floor_ft: number }>;
    exterior_walls: Array<{ id: string; start_vertex_index: number; end_vertex_index: number }>;
    provenance: Record<string, unknown>;
  };
  lot: {
    area_sq_ft: number | null;
    area_provenance: Record<string, unknown>;
    lot_line_segments: Array<{ id: string; start: [number, number]; end: [number, number] }>;
    street_lines: Array<{
      wall_id: string;
      start: [number, number];
      end: [number, number];
      attestation: Record<string, unknown>;
    }>;
  };
  lot_rule_facts: Record<string, unknown>;
  scenario_label: string;
  proposal_id: string | null;
}

// ---------------------------------------------------------------------------
// Bounded report view model — what the UI renders. Every string field here has
// already been bounded; numbers are verbatim server values.
// ---------------------------------------------------------------------------
export interface CheckResultView {
  checkId: string;
  family: string;
  label: string;
  unit: string;
  direction: string;
  outcome: string; // "pass" | "fail" | "could_not_check"
  providedValue: number | null;
  requiredValue: number | null;
  shortfall: number | null;
  couldNotCheckReason: string | null;
  detail: string;
  semanticGap: string | null;
  ruleId: string | null;
  coverageStatus: string | null;
  providedInputIds: string[];
}

export interface ProposalCheckReportView {
  scenarioLabel: string;
  proposalId: string | null;
  sourceClass: string;
  outlineDigest: string;
  results: CheckResultView[];
  summary: { pass: number; fail: number; couldNotCheck: number; total: number };
  unmappedLotFacts: string[];
  correlationId: string | null;
}

// ---------------------------------------------------------------------------
// Outcome union — the documented route envelopes plus the browser-level modes.
// ---------------------------------------------------------------------------
export interface ProposalReportOutcome {
  kind: "report";
  report: ProposalCheckReportView;
  correlationId: string | null;
}
/** Flag-gated off / unmounted: generic 404 {"detail":"Not Found"} — benign. */
export interface ProposalFeatureUnavailableOutcome {
  kind: "feature_unavailable";
}
export interface ProposalPayloadTooLargeOutcome {
  kind: "payload_too_large";
  message: string;
  correlationId: string | null;
}
/** (422, validation_error) — a typed boundary refusal, optionally naming the
 * exact `field` the route rejected. */
export interface ProposalValidationErrorOutcome {
  kind: "validation_error";
  field: string | null;
  message: string;
  correlationId: string | null;
}
export interface ProposalInternalErrorOutcome {
  kind: "internal_error";
  message: string;
  correlationId: string | null;
}
/** A 200 whose body did not match the report contract. */
export interface ProposalValidationFailureOutcome {
  kind: "validation_failure";
  problems: string[];
  correlationId: string | null;
}
export interface ProposalNetworkErrorOutcome {
  kind: "network_error";
  message: string;
}
export interface ProposalClientTimeoutOutcome {
  kind: "client_timeout";
  timeoutMs: number;
}
export interface ProposalAbortedOutcome {
  kind: "aborted";
}
export interface ProposalUnexpectedResponseOutcome {
  kind: "unexpected_response";
  httpStatus: number;
  receivedState: string | null;
  correlationId: string | null;
}

export type ProposalCheckOutcome =
  | ProposalReportOutcome
  | ProposalFeatureUnavailableOutcome
  | ProposalPayloadTooLargeOutcome
  | ProposalValidationErrorOutcome
  | ProposalInternalErrorOutcome
  | ProposalValidationFailureOutcome
  | ProposalNetworkErrorOutcome
  | ProposalClientTimeoutOutcome
  | ProposalAbortedOutcome
  | ProposalUnexpectedResponseOutcome;

/** Outcomes on which a Retry is meaningful (recoverable server/network faults).
 * `payload_too_large`, `validation_error`, and `feature_unavailable` are
 * results, not recoverable faults, so they carry no Retry. */
export function proposalCheckOutcomeIsRecoverable(outcome: ProposalCheckOutcome): boolean {
  return (
    outcome.kind === "internal_error" ||
    outcome.kind === "validation_failure" ||
    outcome.kind === "network_error" ||
    outcome.kind === "client_timeout" ||
    outcome.kind === "unexpected_response"
  );
}

// ---------------------------------------------------------------------------
// Exact (HTTP status, state) pair matrix — mirrors
// PROPOSAL_CHECKS_STATUS_STATE_MATRIX (proposal_checks_api.py) verbatim, plus
// the flag-off / unmounted generic (404, null).
// ---------------------------------------------------------------------------
type DocumentedPair = readonly [number, string | null];

const DOCUMENTED_PAIRS: readonly DocumentedPair[] = [
  [200, null], // grouped report (validated client-side before render)
  [404, null], // generic Not Found: feature flag off / route unmounted
  [413, "payload_too_large"],
  [422, "validation_error"],
  [500, "internal_error"],
] as const;

const PAIR_KEYS: ReadonlySet<string> = new Set(
  DOCUMENTED_PAIRS.map(([status, state]) => `${status}:${state ?? ""}`),
);

export function isDocumentedProposalPair(status: number, state: string | null): boolean {
  return PAIR_KEYS.has(`${status}:${state ?? ""}`);
}

export interface ProposalCheckOptions {
  fetchImpl?: typeof fetch;
  signal?: AbortSignal;
  timeoutMs?: number;
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

function finiteOrNull(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

// ---------------------------------------------------------------------------
// 200-body bounding: shape-verify the grouped report and bound every reflected
// string BEFORE it can render (DB-039(k)). A malformed 200 is a distinct
// `validation_failure`, never a partial render.
// ---------------------------------------------------------------------------
function boundReport(
  body: unknown,
  correlationId: string | null,
): { ok: true; report: ProposalCheckReportView } | { ok: false; problems: string[] } {
  const record = asRecord(body);
  if (!record) return { ok: false, problems: ["report body was not a JSON object"] };
  const rawResults = record.results;
  const summary = asRecord(record.summary);
  if (!Array.isArray(rawResults)) return { ok: false, problems: ["report is missing a results array"] };
  if (!summary) return { ok: false, problems: ["report is missing a summary object"] };
  const pass = finiteOrNull(summary.pass);
  const fail = finiteOrNull(summary.fail);
  const couldNotCheck = finiteOrNull(summary.could_not_check);
  const total = finiteOrNull(summary.total);
  if (pass === null || fail === null || couldNotCheck === null || total === null) {
    return { ok: false, problems: ["report summary counts were not all numbers"] };
  }

  // semantic_gap prose lives on fact_mapping (by check_id); attach it to results
  // so the report can disclose the non-commensurability reason.
  const gapByCheckId = new Map<string, string | null>();
  if (Array.isArray(record.fact_mapping)) {
    for (const entry of record.fact_mapping) {
      const row = asRecord(entry);
      if (row && typeof row.check_id === "string") {
        gapByCheckId.set(
          row.check_id,
          typeof row.semantic_gap === "string" ? boundedText(row.semantic_gap, "") : null,
        );
      }
    }
  }

  const results: CheckResultView[] = rawResults.map((raw) => {
    const r = asRecord(raw) ?? {};
    const prov = asRecord(r.provenance) ?? {};
    const checkId = boundedText(r.check_id, "unknown");
    const providedIdsRaw = Array.isArray(prov.provided_input_ids) ? prov.provided_input_ids : [];
    return {
      checkId,
      family: boundedText(r.family, "unknown"),
      label: boundedText(r.label, "unlabeled check"),
      unit: boundedText(r.unit, ""),
      direction: boundedText(r.direction, ""),
      outcome: boundedText(r.outcome, "unknown"),
      providedValue: finiteOrNull(r.provided_value),
      requiredValue: finiteOrNull(r.required_value),
      shortfall: finiteOrNull(r.shortfall),
      couldNotCheckReason:
        typeof r.could_not_check_reason === "string"
          ? boundedText(r.could_not_check_reason, "unspecified")
          : null,
      detail: boundedText(r.detail, ""),
      semanticGap: gapByCheckId.get(checkId) ?? null,
      ruleId: typeof prov.rule_id === "string" ? boundedText(prov.rule_id, "") : null,
      coverageStatus:
        typeof prov.coverage_status === "string" ? boundedText(prov.coverage_status, "") : null,
      providedInputIds: providedIdsRaw
        .map((id) => boundedText(id, ""))
        .filter((id) => id !== ""),
    };
  });

  const unmappedLotFacts = Array.isArray(record.unmapped_lot_facts)
    ? record.unmapped_lot_facts.map((key) => boundedText(key, "")).filter((key) => key !== "")
    : [];

  return {
    ok: true,
    report: {
      scenarioLabel: boundedText(record.scenario_label, "Untitled proposal"),
      proposalId: typeof record.proposal_id === "string" ? boundedText(record.proposal_id, "") : null,
      sourceClass: boundedText(record.source_class, "proposed"),
      outlineDigest: boundedToken(record.outline_digest, 96) ?? "",
      results,
      summary: { pass, fail, couldNotCheck, total },
      unmappedLotFacts,
      correlationId,
    },
  };
}

/**
 * POST an editor-authored proposal to the internal checks route and classify the
 * response. Offline by construction: the caller injects `fetchImpl` in tests
 * (committed fixtures); no network dependency lives here.
 */
export async function fetchProposalCheck(
  request: ProposalCheckRequest,
  options: ProposalCheckOptions = {},
): Promise<ProposalCheckOutcome> {
  const fetchImpl = options.fetchImpl ?? fetch;
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const url = `${apiBaseUrl()}/api/v1/proposal-checks`;

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
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(request),
        cache: "no-store",
        signal: controller.signal,
      });
    } catch {
      if (timedOut) return { kind: "client_timeout", timeoutMs };
      if (controller.signal.aborted || externalSignal?.aborted) return { kind: "aborted" };
      return {
        kind: "network_error",
        message:
          "The proposal-check service could not be reached. Nothing was checked, " +
          "and this is safe to retry.",
      };
    }

    const correlationId = boundedToken(response.headers.get("X-Correlation-ID"));

    // SIZE BOUND BEFORE PARSE (fail-closed): a plain digit Content-Length within
    // MAX_RESPONSE_BYTES only; anything else rejects into unexpected_response.
    const declaredLengthHeader = response.headers.get("Content-Length");
    const declaredLength =
      declaredLengthHeader !== null && /^[0-9]+$/.test(declaredLengthHeader.trim())
        ? Number(declaredLengthHeader.trim())
        : Number.NaN;
    if (!Number.isFinite(declaredLength) || declaredLength > MAX_RESPONSE_BYTES) {
      return { kind: "unexpected_response", httpStatus: response.status, receivedState: null, correlationId };
    }

    let body: unknown = null;
    try {
      body = await response.json();
    } catch {
      if (timedOut) return { kind: "client_timeout", timeoutMs };
      if (controller.signal.aborted || externalSignal?.aborted) return { kind: "aborted" };
      return { kind: "unexpected_response", httpStatus: response.status, receivedState: null, correlationId };
    }

    const record = asRecord(body);
    // RAW state for the contract check — sanitizing before comparison could
    // launder a malformed state into a documented one.
    const state = record && typeof record.state === "string" ? record.state : null;

    if (!isDocumentedProposalPair(response.status, state)) {
      return {
        kind: "unexpected_response",
        httpStatus: response.status,
        receivedState: state === null ? null : boundedToken(state, 48),
        correlationId,
      };
    }

    if (response.status === 200) {
      const bounded = boundReport(body, correlationId);
      if (!bounded.ok) {
        return { kind: "validation_failure", problems: bounded.problems, correlationId };
      }
      return { kind: "report", report: bounded.report, correlationId };
    }

    // (404, null): generic Not Found — the feature is disabled or unmounted.
    if (response.status === 404 && state === null) {
      return { kind: "feature_unavailable" };
    }

    if (state === "payload_too_large") {
      return {
        kind: "payload_too_large",
        message: boundedText(record?.message, "The proposal was too large to send."),
        correlationId,
      };
    }

    if (state === "validation_error") {
      return {
        kind: "validation_error",
        field: typeof record?.field === "string" ? boundedText(record.field, "unknown field") : null,
        message: boundedText(record?.message, "The proposal was refused by the checking service."),
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
// Assistive-technology announcement copy — derived deterministically from the
// already-classified outcome. No legal semantics; never "verified"/"best"; the
// report announcement leads with the FAIL and COULD_NOT_CHECK counts so a
// passing subset is never heard as whole-building approval. `aborted` announces
// nothing (a superseded request).
// ---------------------------------------------------------------------------
export function announcementForProposalCheck(outcome: ProposalCheckOutcome): string {
  switch (outcome.kind) {
    case "report": {
      const s = outcome.report.summary;
      return (
        `Proposal check complete: ${s.fail} did not meet a rule allowance, ` +
        `${s.couldNotCheck} could not be checked, ${s.pass} met the allowance. ` +
        `These are proposed values you entered, not a city record; professional review required.`
      );
    }
    case "feature_unavailable":
      return "Proposal checks are not available in this environment.";
    case "payload_too_large":
      return "Proposal check failed: the draft was too large to send.";
    case "validation_error":
      return "Proposal check rejected: the draft was refused by the checking service.";
    case "internal_error":
      return "Proposal check failed: something went wrong on our side.";
    case "validation_failure":
      return "Proposal check failed: the response did not match the published data contract.";
    case "network_error":
      return "Proposal check failed: the checking service could not be reached.";
    case "client_timeout":
      return "Proposal check failed: the request took too long and was cancelled.";
    case "unexpected_response":
      return "Proposal check failed: unexpected response from the platform API.";
    case "aborted":
      return "";
  }
}
