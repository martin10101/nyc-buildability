/**
 * HARDENED typed GET client + contract checks for the INTERNAL parity-read route
 * (lane C packet W4).
 *
 * Contract: services/api/app/api/v1/parity_read.py (read-only dependency) - the
 * flag-gated internal GET /api/v1/properties/{bbl}/parity that returns the parity
 * DATA a property carries: the disclosed selection of recorded DOF comparable
 * sales (NOT a valuation) and the unused-floor-area line (ALWAYS "Not confirmed",
 * no number). The server is itself contract-guarded against
 * packages/contracts/schemas/v1/parity_data.schema.json before it ships a 200;
 * this client RE-ASSERTS the honesty invariants so a malformed/dishonest 200 can
 * never render.
 *
 * Discipline copied from src/lib/proposal-checks-api.ts (the accepted internal
 * client precedent):
 *   1. EXACT (HTTP status, state) pair enforcement mirroring the route's
 *      PARITY_READ_STATUS_STATE_MATRIX verbatim, plus the flag-off / unmounted
 *      generic (404, null) -> feature_unavailable. A body is never routed by its
 *      `state` alone, and the RAW state string is compared (sanitizing before the
 *      comparison could launder a malformed state into a documented one).
 *   2. The raw body is size-bounded BEFORE it is parsed: Content-Length must be a
 *      plain digit string within MAX_RESPONSE_BYTES; absent / blank / non-numeric
 *      / over-budget all FAIL CLOSED to unexpected_response.
 *   3. Every reflected server string that this module surfaces for display is
 *      length-capped / control-stripped (boundedText) or token-allowlisted
 *      (boundedToken) BEFORE it leaves the module; numbers pass through verbatim.
 *   4. Requests are cancellable (AbortController) and time-bounded; a superseded
 *      request resolves to `aborted`, a timeout to the recoverable
 *      `client_timeout`. `fetchImpl` is injectable for offline tests.
 *
 * The pinned owner-facing disclosure constants are LOCKED to the generated
 * contract literals with `satisfies`, so a schema wording change fails `tsc` here
 * rather than letting the client drift from the contract. This module TRANSPORTS
 * and CHECKS; it computes no valuation, average, price-per-square-foot or
 * remaining capacity, and introduces no 485-x / tax-incentive field.
 */

import { apiBaseUrl } from "./api";
import { boundedText, boundedToken } from "./bounded";
import type {
  ComparableSales,
  ParityData,
  UnusedFloorArea,
} from "../../../../packages/contracts/generated/parity_data";

export type { ParityData, ComparableSales, UnusedFloorArea };

/** Default request budget; kept below the Playwright test timeout so the timeout
 * journey is provable in CI without configuration. */
export const DEFAULT_TIMEOUT_MS = 12_000;

/** Response-body ceiling before parse (fail-closed). The parity document is a
 * small bounded page of recorded sale rows + one unused-floor-area line. */
export const MAX_RESPONSE_BYTES = 512_000;

// ---------------------------------------------------------------------------
// Pinned owner-facing disclosure constants, LOCKED to the generated contract
// literals. `satisfies` proves each equals the schema const exactly; a wording
// change in the schema (regenerated TS) fails tsc HERE.
// ---------------------------------------------------------------------------
export const NOT_A_VALUATION_NOTICE =
  'These are recorded sales selected by a simple, disclosed filter, not a valuation or an appraisal. How "similar type and size" should be defined is a product choice to confirm with the owner.' satisfies ComparableSales["not_a_valuation"];

export const NOT_CONFIRMED_STATUS = "not_confirmed" satisfies UnusedFloorArea["status"];
export const NOT_CONFIRMED_LABEL =
  "Remaining development capacity: Not confirmed" satisfies UnusedFloorArea["label"];
export const NOT_CONFIRMED_REASON =
  "Needs verified zoning-lot boundaries and existing zoning floor area." satisfies UnusedFloorArea["reason"];

export const PARITY_CONTRACT_VERSION = "1.0.0" satisfies ParityData["contract_version"];

// ---------------------------------------------------------------------------
// Bounded disclosure view - the owner-facing narrative strings, bounded for
// display BEFORE they leave the module. The structured `data` carries the
// validated, typed contract document; per-cell DOF values are bounded at render
// by src/lib/bounded.ts (the property-profile precedent), never invented here.
// ---------------------------------------------------------------------------
export interface ParityDisclosureView {
  notAValuation: string;
  criteriaText: string;
  unusedLabel: string;
  unusedReason: string;
  unusedDetail: string;
}

// ---------------------------------------------------------------------------
// Outcome union - the documented route envelopes plus the browser-level modes.
// ---------------------------------------------------------------------------
export interface ParityDataOutcome {
  kind: "parity";
  data: ParityData;
  disclosure: ParityDisclosureView;
  correlationId: string | null;
}
/** Flag-gated off / unmounted: generic 404 {"detail":"Not Found"} - benign. */
export interface ParityFeatureUnavailableOutcome {
  kind: "feature_unavailable";
}
/** (422, validation_error) - a typed boundary refusal (a malformed BBL). */
export interface ParityValidationErrorOutcome {
  kind: "validation_error";
  message: string;
  correlationId: string | null;
}
/** (429, rate_limited) - the per-caller budget is exhausted; safe to retry. */
export interface ParityRateLimitedOutcome {
  kind: "rate_limited";
  message: string;
  correlationId: string | null;
}
/** (503, inputs_unavailable) - the parity data could not be produced (Lane B gate
 * off, an upstream DOF failure, or no usable subject sale); nothing fabricated. */
export interface ParityInputsUnavailableOutcome {
  kind: "inputs_unavailable";
  message: string;
  correlationId: string | null;
}
/** (500, internal_error) OR (500, internal_contract_error) - an internal server
 * fault; the distinguishing state token is carried (bounded) for diagnostics. */
export interface ParityInternalErrorOutcome {
  kind: "internal_error";
  state: string | null;
  message: string;
  correlationId: string | null;
}
/** A 200 whose body did not satisfy the parity contract / honesty invariants. */
export interface ParityValidationFailureOutcome {
  kind: "validation_failure";
  problems: string[];
  correlationId: string | null;
}
export interface ParityNetworkErrorOutcome {
  kind: "network_error";
  message: string;
}
export interface ParityClientTimeoutOutcome {
  kind: "client_timeout";
  timeoutMs: number;
}
export interface ParityAbortedOutcome {
  kind: "aborted";
}
export interface ParityUnexpectedResponseOutcome {
  kind: "unexpected_response";
  httpStatus: number;
  receivedState: string | null;
  correlationId: string | null;
}

export type ParityOutcome =
  | ParityDataOutcome
  | ParityFeatureUnavailableOutcome
  | ParityValidationErrorOutcome
  | ParityRateLimitedOutcome
  | ParityInputsUnavailableOutcome
  | ParityInternalErrorOutcome
  | ParityValidationFailureOutcome
  | ParityNetworkErrorOutcome
  | ParityClientTimeoutOutcome
  | ParityAbortedOutcome
  | ParityUnexpectedResponseOutcome;

/** Outcomes on which a Retry is meaningful (recoverable server/network faults).
 * `feature_unavailable`, `validation_error` and `inputs_unavailable` are results,
 * not recoverable faults in the caller's gift, so they carry no Retry here. */
export function parityOutcomeIsRecoverable(outcome: ParityOutcome): boolean {
  return (
    outcome.kind === "rate_limited" ||
    outcome.kind === "internal_error" ||
    outcome.kind === "validation_failure" ||
    outcome.kind === "network_error" ||
    outcome.kind === "client_timeout" ||
    outcome.kind === "unexpected_response"
  );
}

// ---------------------------------------------------------------------------
// Exact (HTTP status, state) pair matrix - mirrors PARITY_READ_STATUS_STATE_MATRIX
// (parity_read.py) verbatim, plus the flag-off / unmounted generic (404, null).
// ---------------------------------------------------------------------------
type DocumentedPair = readonly [number, string | null];

const DOCUMENTED_PAIRS: readonly DocumentedPair[] = [
  [200, null], // parity document (validated client-side before use)
  [404, null], // generic Not Found: feature flag off / route unmounted
  [422, "validation_error"],
  [429, "rate_limited"],
  [503, "inputs_unavailable"],
  [500, "internal_error"],
  [500, "internal_contract_error"],
] as const;

const PAIR_KEYS: ReadonlySet<string> = new Set(
  DOCUMENTED_PAIRS.map(([status, state]) => `${status}:${state ?? ""}`),
);

export function isDocumentedParityPair(status: number, state: string | null): boolean {
  return PAIR_KEYS.has(`${status}:${state ?? ""}`);
}

export interface ParityFetchOptions {
  fetchImpl?: typeof fetch;
  signal?: AbortSignal;
  timeoutMs?: number;
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.length > 0;
}

// ---------------------------------------------------------------------------
// Banned derived-valuation / remaining-capacity / tax-incentive KEY names. The
// server's additionalProperties:false already forbids them; this is client-side
// defense-in-depth so a dishonest 200 can never render (485-x is out of scope).
//
// Valuation / capacity names are matched EXACTLY (mirroring the server honesty
// test), because the legitimate key `not_a_valuation` legitimately CONTAINS the
// word "valuation" and `existing_floor_area_input` the word "floor_area" - a
// substring rule would false-positive on them. Incentive markers are matched as
// substrings because no legitimate contract key carries one.
// ---------------------------------------------------------------------------
const BANNED_EXACT_KEYS: ReadonlySet<string> = new Set([
  "average",
  "avg",
  "mean",
  "price_per_square_foot",
  "price_per_sq_ft",
  "ppsf",
  "dollars_per_square_foot",
  "estimate",
  "estimated_value",
  "valuation",
  "capacity",
  "remaining",
  "remaining_floor_area",
  "remaining_development_capacity",
  "allowance",
  "floor_area_allowance",
  "far",
  "unused_floor_area_sq_ft",
  "air_rights",
]);
const BANNED_KEY_SUBSTRINGS: readonly string[] = [
  "485",
  "exemption",
  "incentive",
  "abatement",
];

function* iterKeys(node: unknown): Generator<string> {
  if (Array.isArray(node)) {
    for (const item of node) yield* iterKeys(item);
  } else if (typeof node === "object" && node !== null) {
    for (const [key, value] of Object.entries(node)) {
      yield key;
      yield* iterKeys(value);
    }
  }
}

/**
 * Runtime contract + honesty check on a 200 body. Returns the TYPED document on
 * success, or a bounded, body-independent problem list on failure. Every problem
 * message is a static literal (no byte of the rejected body reaches the list).
 */
export function checkParityData(
  body: unknown,
): { ok: true; data: ParityData } | { ok: false; problems: string[] } {
  const problems: string[] = [];
  const root = asRecord(body);
  if (!root) return { ok: false, problems: ["parity body was not a JSON object"] };

  if (root.contract_version !== PARITY_CONTRACT_VERSION) {
    problems.push("contract_version is not the published 1.0.0");
  }

  const comps = asRecord(root.comparable_sales);
  if (!comps) {
    problems.push("comparable_sales is missing or not an object");
  } else {
    if (comps.not_a_valuation !== NOT_A_VALUATION_NOTICE) {
      problems.push("comparable_sales.not_a_valuation is not the pinned disclosure");
    }
    if (!isNonEmptyString(comps.criteria_text)) {
      problems.push("comparable_sales.criteria_text must be a non-empty string");
    }
    if (!Array.isArray(comps.selected)) problems.push("comparable_sales.selected must be an array");
    if (!Array.isArray(comps.excluded)) problems.push("comparable_sales.excluded must be an array");
  }

  const unused = asRecord(root.unused_floor_area);
  if (!unused) {
    problems.push("unused_floor_area is missing or not an object");
  } else {
    if (unused.status !== NOT_CONFIRMED_STATUS) {
      problems.push("unused_floor_area.status must be 'not_confirmed'");
    }
    if (unused.label !== NOT_CONFIRMED_LABEL) {
      problems.push("unused_floor_area.label is not the owner-settled 'Not confirmed' line");
    }
    if (unused.reason !== NOT_CONFIRMED_REASON) {
      problems.push("unused_floor_area.reason is not the owner-settled reason line");
    }
    if (!asRecord(unused.existing_floor_area_input)) {
      problems.push("unused_floor_area.existing_floor_area_input is missing or not an object");
    }
    if (!isNonEmptyString(unused.detail)) {
      problems.push("unused_floor_area.detail must be a non-empty string");
    }
  }

  for (const key of iterKeys(body)) {
    const lowered = key.toLowerCase();
    const bannedExact = BANNED_EXACT_KEYS.has(lowered);
    const bannedSubstring = BANNED_KEY_SUBSTRINGS.some((marker) => lowered.includes(marker));
    if (bannedExact || bannedSubstring) {
      problems.push("a banned valuation / remaining-capacity / incentive field is present");
      break;
    }
  }

  if (problems.length > 0) return { ok: false, problems };
  return { ok: true, data: body as ParityData };
}

function boundDisclosure(data: ParityData): ParityDisclosureView {
  return {
    notAValuation: boundedText(data.comparable_sales.not_a_valuation, NOT_A_VALUATION_NOTICE),
    criteriaText: boundedText(data.comparable_sales.criteria_text, ""),
    unusedLabel: boundedText(data.unused_floor_area.label, NOT_CONFIRMED_LABEL),
    unusedReason: boundedText(data.unused_floor_area.reason, NOT_CONFIRMED_REASON),
    unusedDetail: boundedText(data.unused_floor_area.detail, ""),
  };
}

/**
 * GET the parity data for one BBL and classify the response. Offline by
 * construction: the caller injects `fetchImpl` in tests (committed fixtures); no
 * network dependency lives here.
 */
export async function fetchParityData(
  bbl: string,
  options: ParityFetchOptions = {},
): Promise<ParityOutcome> {
  const fetchImpl = options.fetchImpl ?? fetch;
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const url = `${apiBaseUrl()}/api/v1/properties/${encodeURIComponent(bbl)}/parity`;

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
          "The parity service could not be reached. Nothing was retrieved, and this " +
          "is safe to retry.",
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
    // RAW state for the contract check - sanitizing before comparison could
    // launder a malformed state into a documented one.
    const state = record && typeof record.state === "string" ? record.state : null;

    if (!isDocumentedParityPair(response.status, state)) {
      return {
        kind: "unexpected_response",
        httpStatus: response.status,
        receivedState: state === null ? null : boundedToken(state, 48),
        correlationId,
      };
    }

    if (response.status === 200) {
      const checked = checkParityData(body);
      if (!checked.ok) {
        return { kind: "validation_failure", problems: checked.problems, correlationId };
      }
      return {
        kind: "parity",
        data: checked.data,
        disclosure: boundDisclosure(checked.data),
        correlationId,
      };
    }

    // (404, null): generic Not Found - the feature is disabled or unmounted.
    if (response.status === 404 && state === null) {
      return { kind: "feature_unavailable" };
    }

    if (state === "validation_error") {
      return {
        kind: "validation_error",
        message: boundedText(record?.message, "The property reference was refused."),
        correlationId,
      };
    }

    if (state === "rate_limited") {
      return {
        kind: "rate_limited",
        message: boundedText(record?.message, "Too many requests; this is safe to retry shortly."),
        correlationId,
      };
    }

    if (state === "inputs_unavailable") {
      return {
        kind: "inputs_unavailable",
        message: boundedText(
          record?.message,
          "The parity data is not available for this property right now; nothing was fabricated.",
        ),
        correlationId,
      };
    }

    // Only (500, internal_error) and (500, internal_contract_error) remain.
    return {
      kind: "internal_error",
      state: state === null ? null : boundedToken(state, 48),
      message: boundedText(record?.message, "Unexpected internal error."),
      correlationId,
    };
  } finally {
    clearTimeout(timer);
    externalSignal?.removeEventListener("abort", onExternalAbort);
  }
}

// ---------------------------------------------------------------------------
// Assistive-technology announcement copy - derived deterministically from the
// already-classified outcome. No legal semantics; never "verified"/"valued"; the
// parity announcement leads with the not-a-valuation framing so recorded comps
// are never heard as an appraisal, and remaining capacity is always "Not
// confirmed". `aborted` announces nothing (a superseded request).
// ---------------------------------------------------------------------------
export function announcementForParity(outcome: ParityOutcome): string {
  switch (outcome.kind) {
    case "parity": {
      const count = outcome.data.comparable_sales.selected.length;
      return (
        `Parity data loaded: ${count} recorded comparable sale${count === 1 ? "" : "s"} ` +
        "selected by a disclosed filter - these are recorded sales, not a valuation. " +
        "Remaining development capacity: Not confirmed."
      );
    }
    case "feature_unavailable":
      return "Parity data is not available in this environment.";
    case "validation_error":
      return "Parity data rejected: the property reference was refused.";
    case "rate_limited":
      return "Parity data paused: too many requests. This is safe to retry shortly.";
    case "inputs_unavailable":
      return "Parity data is not available for this property right now. Nothing was fabricated.";
    case "internal_error":
      return "Parity data failed: something went wrong on our side.";
    case "validation_failure":
      return "Parity data failed: the response did not match the published data contract.";
    case "network_error":
      return "Parity data failed: the service could not be reached.";
    case "client_timeout":
      return "Parity data failed: the request took too long and was cancelled.";
    case "unexpected_response":
      return "Parity data failed: unexpected response from the platform API.";
    case "aborted":
      return "";
  }
}
