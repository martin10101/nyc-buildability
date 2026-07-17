/**
 * Client-side mirror of the backend's exact (HTTP status, body state) pair
 * contract (task M2-T002 output A; scenario S2).
 *
 * SOURCE OF TRUTH: STATUS_STATE_MATRIX in
 * services/api/app/api/v1/properties.py (task M2-T003 item D) — a frozenset
 * the backend enumerates with a parametrized test so no undocumented pair
 * can ship. This module mirrors that set VERBATIM as the client contract:
 * a response whose (status, state) pair is not in this set is treated as a
 * hard `unexpected_response`, never routed by its body alone.
 *
 * OWNER-DIRECTED BLOCKING REGRESSION (S2): HTTP 500 with body
 * state=no_match — the recorded adversarial fixture
 * packages/contracts/fixtures/client_regression/http500_state_no_match.json
 * — must NEVER render as a no-match result. (500, "no_match") is absent
 * from this set, so the pair check rejects it structurally, not as a
 * special case.
 *
 * The 200 success pair carries NO `state` key; it is recorded with the
 * sentinel `null` exactly like the backend records it with `None`.
 */

/** Documented body states for non-200 responses (backend vocabulary). */
export type DocumentedState =
  | "validation_error"
  | "no_match"
  | "schema_drift"
  | "rate_limited"
  | "source_unavailable"
  | "timeout"
  | "internal_error"
  | "internal_contract_error"
  | "unsupported_contract_version";

export type StatusStatePair = readonly [number, DocumentedState | null];

/** Verbatim mirror of the backend STATUS_STATE_MATRIX (10 pairs). */
export const DOCUMENTED_STATUS_STATE_PAIRS: readonly StatusStatePair[] = [
  [200, null], // canonical profile (validated client-side before render)
  [422, "validation_error"],
  [404, "no_match"],
  [502, "schema_drift"],
  [503, "rate_limited"],
  [503, "source_unavailable"],
  [504, "timeout"],
  [500, "internal_error"],
  [500, "internal_contract_error"],
  [500, "unsupported_contract_version"],
] as const;

const PAIR_KEYS: ReadonlySet<string> = new Set(
  DOCUMENTED_STATUS_STATE_PAIRS.map(([status, state]) => `${status}:${state ?? ""}`),
);

/**
 * Exact pair membership. ANY mismatch — documented state on the wrong
 * status, unknown state, state present on a 200, state absent on a non-200
 * — returns false and must render as `unexpected_response`.
 */
export function isDocumentedPair(status: number, state: string | null): boolean {
  return PAIR_KEYS.has(`${status}:${state ?? ""}`);
}

export const UPSTREAM_FAILURE_STATES = [
  "rate_limited",
  "source_unavailable",
  "timeout",
  "schema_drift",
] as const;
export type UpstreamFailureState = (typeof UPSTREAM_FAILURE_STATES)[number];

export const SERVER_CONTRACT_ERROR_STATES = [
  "internal_contract_error",
  "unsupported_contract_version",
] as const;
export type ServerContractErrorState = (typeof SERVER_CONTRACT_ERROR_STATES)[number];
