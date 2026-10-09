/**
 * HARDENED typed POST client for the INTERNAL outline-bridge route
 * (task M5-T065, D-082-R001).
 *
 * Contract: services/api/app/api/v1/outline_bridge.py (read-only dependency) —
 * the flag-gated, UNMOUNTED internal POST /api/v1/outline-bridge that converts a
 * map-drawn EPSG:4326 outline to authoritative EPSG:2263 by CORRESPONDENCE to the
 * SAME parcel's two accepted representations (never projection math, no new
 * dependency). The returned 2263 vertices carry the affine fit residual AND the
 * margin over the next-best alignment disclosed honestly; a low residual alone
 * never establishes correspondence, so an ambiguous/indistinguishable parcel is
 * REFUSED, never guessed. The bridged values are PROPOSED input, never a survey
 * and never a city record (D-076-R002).
 *
 * Discipline copied EXACTLY from src/lib/proposal-checks-api.ts (the accepted
 * internal-client precedent):
 *   1. EXACT (HTTP status, state) pair enforcement mirroring the route's
 *      OUTLINE_BRIDGE_STATUS_STATE_MATRIX verbatim, plus the flag-off /
 *      unmounted generic (404, null) -> feature_unavailable. A body is never
 *      routed by its `state` alone.
 *   2. The raw body is size-bounded BEFORE it is parsed: Content-Length must be
 *      a plain digit string within MAX_RESPONSE_BYTES; absent / blank /
 *      non-numeric / over-budget all FAIL CLOSED to unexpected_response.
 *   3. Every reflected server string is length-capped/control-stripped
 *      (boundedText) or token-allowlisted (boundedToken) BEFORE it leaves this
 *      module; numbers pass through verbatim (the server value is the truth).
 *      No raw-HTML injection sink is used anywhere in this packet.
 *   4. Requests are cancellable (AbortController) and time-bounded; a superseded
 *      request resolves to `aborted`, a timeout to the recoverable
 *      `client_timeout`. `fetchImpl` is injectable for offline tests.
 *
 * This module TRANSPORTS and BOUNDS; it computes no coordinate and never
 * re-derives a transform — the server correspondence remains the single truth
 * surface (the no-reprojection doctrine: no client-side 4326->2263 math here).
 */

import { apiBaseUrl } from "./api";
import { boundedText, boundedToken } from "./bounded";

/** Default request budget; kept below the Playwright test timeout so the
 * timeout journey is provable in CI without configuration. */
export const DEFAULT_TIMEOUT_MS = 12_000;

/** Response-body ceiling before parse (fail-closed). The bridge response is a
 * small document; a response declaring more than this is rejected rather than
 * parsed and walked. */
export const MAX_RESPONSE_BYTES = 512_000;

// ---------------------------------------------------------------------------
// Request shape — mirrors the route's documented request contract exactly:
//   { bbl, drawn_vertices: [[lng, lat], ...], srid? }.
// drawn_vertices are DISPLAY 4326 positions; the route converts them by
// correspondence (no transform lives on this side).
// ---------------------------------------------------------------------------
export interface OutlineBridgeRequest {
  bbl: string;
  drawn_vertices: Array<[number, number]>;
  /** Always 4326 (the display CRS); the route refuses any other value. */
  srid?: number;
}

// ---------------------------------------------------------------------------
// Bounded view models — what the UI reads. Every string field here has already
// been bounded; numbers are verbatim server values (the disclosed residual is
// load-bearing and must NOT be rounded/laundered here).
// ---------------------------------------------------------------------------
export interface BridgeVertex {
  x: number;
  y: number;
}

export interface BridgeRingIdentity {
  crs: string | null;
  sourceId: string | null;
  representation: string | null;
}

export interface BridgeCorrespondenceView {
  method: string;
  alignment: string;
  alignmentWinding: string;
  alignmentOffset: number | null;
  controlPointCount: number | null;
  candidatesEvaluated: number | null;
  rmsResidualFt: number | null;
  maxResidualFt: number | null;
  residualBoundFt: number | null;
  runnerUpRmsResidualFt: number | null;
  alignmentSeparationFt: number | null;
  alignmentSeparationMinFt: number | null;
  sourceDisplayRing: BridgeRingIdentity;
  sourceAuthoritativeRing: BridgeRingIdentity;
}

export interface OutlineBridgeReportView {
  bbl: string | null;
  srid: number;
  vertices: BridgeVertex[];
  correspondence: BridgeCorrespondenceView;
  disclosure: string;
  correlationId: string | null;
}

// ---------------------------------------------------------------------------
// Outcome union — the documented route envelopes plus the browser-level modes.
// The refusals are DISTINCT so the drawing UI can name what went wrong (an
// ambiguous/high-residual fit is a result, never a coordinate).
// ---------------------------------------------------------------------------
export interface BridgedOutcome {
  kind: "bridged";
  report: OutlineBridgeReportView;
  correlationId: string | null;
}
/** Flag-gated off / unmounted: generic 404 {"detail":"Not Found"} — benign. */
export interface BridgeFeatureUnavailableOutcome {
  kind: "feature_unavailable";
}
export interface BridgePayloadTooLargeOutcome {
  kind: "payload_too_large";
  message: string;
  correlationId: string | null;
}
/** (422, invalid_request) — malformed/degenerate/over-cap caller input, naming
 * the machine `reason` the route returned. */
export interface BridgeInvalidRequestOutcome {
  kind: "invalid_request";
  reason: string | null;
  message: string;
  correlationId: string | null;
}
/** (422, out_of_neighborhood) — a drawn vertex outside the bounded neighborhood
 * of the lot; DISTINCT from a residual refusal. */
export interface BridgeOutOfNeighborhoodOutcome {
  kind: "out_of_neighborhood";
  message: string;
  correlationId: string | null;
}
/** (422, correspondence_unavailable) — the two rings could not be corresponded
 * (too few/many, mismatch, degenerate, or AMBIGUOUS), naming the `reason`. */
export interface BridgeCorrespondenceUnavailableOutcome {
  kind: "correspondence_unavailable";
  reason: string | null;
  message: string;
  correlationId: string | null;
}
/** (422, residual_too_high) — the affine fit residual exceeded the conservative
 * bound; the disclosed residual and bound are carried for honesty. */
export interface BridgeResidualTooHighOutcome {
  kind: "residual_too_high";
  rmsResidualFt: number | null;
  residualBoundFt: number | null;
  message: string;
  correlationId: string | null;
}
/** (502, source_unavailable) — a connector fault fetching a source ring. */
export interface BridgeSourceUnavailableOutcome {
  kind: "source_unavailable";
  sourceId: string | null;
  message: string;
  correlationId: string | null;
}
export interface BridgeInternalErrorOutcome {
  kind: "internal_error";
  message: string;
  correlationId: string | null;
}
/** A 200 whose body did not match the bridge contract. */
export interface BridgeValidationFailureOutcome {
  kind: "validation_failure";
  problems: string[];
  correlationId: string | null;
}
export interface BridgeNetworkErrorOutcome {
  kind: "network_error";
  message: string;
}
export interface BridgeClientTimeoutOutcome {
  kind: "client_timeout";
  timeoutMs: number;
}
export interface BridgeAbortedOutcome {
  kind: "aborted";
}
export interface BridgeUnexpectedResponseOutcome {
  kind: "unexpected_response";
  httpStatus: number;
  receivedState: string | null;
  correlationId: string | null;
}

export type OutlineBridgeOutcome =
  | BridgedOutcome
  | BridgeFeatureUnavailableOutcome
  | BridgePayloadTooLargeOutcome
  | BridgeInvalidRequestOutcome
  | BridgeOutOfNeighborhoodOutcome
  | BridgeCorrespondenceUnavailableOutcome
  | BridgeResidualTooHighOutcome
  | BridgeSourceUnavailableOutcome
  | BridgeInternalErrorOutcome
  | BridgeValidationFailureOutcome
  | BridgeNetworkErrorOutcome
  | BridgeClientTimeoutOutcome
  | BridgeAbortedOutcome
  | BridgeUnexpectedResponseOutcome;

/** Outcomes on which a Retry is meaningful (recoverable server/network faults).
 * The typed refusals (invalid/out-of-neighborhood/correspondence/residual/
 * payload/feature) are RESULTS, not faults, so they carry no Retry. */
export function outlineBridgeOutcomeIsRecoverable(outcome: OutlineBridgeOutcome): boolean {
  return (
    outcome.kind === "source_unavailable" ||
    outcome.kind === "internal_error" ||
    outcome.kind === "validation_failure" ||
    outcome.kind === "network_error" ||
    outcome.kind === "client_timeout" ||
    outcome.kind === "unexpected_response"
  );
}

// ---------------------------------------------------------------------------
// Exact (HTTP status, state) pair matrix — mirrors
// OUTLINE_BRIDGE_STATUS_STATE_MATRIX (outline_bridge.py) verbatim, plus the
// flag-off / unmounted generic (404, null).
// ---------------------------------------------------------------------------
type DocumentedPair = readonly [number, string | null];

const DOCUMENTED_PAIRS: readonly DocumentedPair[] = [
  [200, null], // bridged 2263 vertices + correspondence provenance
  [404, null], // generic Not Found: feature flag off / route unmounted
  [413, "payload_too_large"],
  [422, "invalid_request"],
  [422, "out_of_neighborhood"],
  [422, "correspondence_unavailable"],
  [422, "residual_too_high"],
  [502, "source_unavailable"],
  [500, "internal_error"],
] as const;

const PAIR_KEYS: ReadonlySet<string> = new Set(
  DOCUMENTED_PAIRS.map(([status, state]) => `${status}:${state ?? ""}`),
);

export function isDocumentedBridgePair(status: number, state: string | null): boolean {
  return PAIR_KEYS.has(`${status}:${state ?? ""}`);
}

export interface OutlineBridgeOptions {
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

function boundRingIdentity(value: unknown): BridgeRingIdentity {
  const record = asRecord(value) ?? {};
  return {
    // crs carries a ':' (EPSG:2263) that the token charset would strip, so it is
    // bounded as text (control-stripped, length-capped) rather than tokenized.
    crs: typeof record.crs === "string" ? boundedText(record.crs, "", 32) : null,
    sourceId: typeof record.source_id === "string" ? boundedText(record.source_id, "", 96) : null,
    representation:
      typeof record.representation === "string" ? boundedText(record.representation, "", 96) : null,
  };
}

// ---------------------------------------------------------------------------
// 200-body bounding: shape-verify the bridge document and bound every reflected
// string BEFORE it can render. A malformed 200 is a distinct `validation_failure`,
// never a partial/undisclosed render — the residual disclosure is load-bearing,
// so a body missing the correspondence block is refused, never shown as bare
// coordinates.
// ---------------------------------------------------------------------------
function boundReport(
  body: unknown,
  correlationId: string | null,
): { ok: true; report: OutlineBridgeReportView } | { ok: false; problems: string[] } {
  const record = asRecord(body);
  if (!record) return { ok: false, problems: ["bridge body was not a JSON object"] };
  const rawVertices = record.vertices;
  const correspondence = asRecord(record.correspondence);
  if (!Array.isArray(rawVertices) || rawVertices.length === 0) {
    return { ok: false, problems: ["bridge is missing a non-empty vertices array"] };
  }
  if (!correspondence) {
    return { ok: false, problems: ["bridge is missing the correspondence provenance block"] };
  }
  const vertices: BridgeVertex[] = [];
  for (const raw of rawVertices) {
    const v = asRecord(raw);
    const x = finiteOrNull(v?.x);
    const y = finiteOrNull(v?.y);
    if (x === null || y === null) {
      return { ok: false, problems: ["a bridged vertex was not finite {x, y} 2263 coordinates"] };
    }
    vertices.push({ x, y });
  }
  const srid = finiteOrNull(record.srid);
  if (srid !== 2263) {
    return { ok: false, problems: ["bridge srid was not the authoritative 2263"] };
  }

  return {
    ok: true,
    report: {
      bbl: typeof record.bbl === "string" ? boundedToken(record.bbl, 32) : null,
      srid: 2263,
      vertices,
      correspondence: {
        method: boundedText(correspondence.method, "unknown"),
        alignment: boundedText(correspondence.alignment, "unknown"),
        alignmentWinding: boundedText(correspondence.alignment_winding, "unknown"),
        alignmentOffset: finiteOrNull(correspondence.alignment_offset),
        controlPointCount: finiteOrNull(correspondence.control_point_count),
        candidatesEvaluated: finiteOrNull(correspondence.candidates_evaluated),
        rmsResidualFt: finiteOrNull(correspondence.rms_residual_ft),
        maxResidualFt: finiteOrNull(correspondence.max_residual_ft),
        residualBoundFt: finiteOrNull(correspondence.residual_bound_ft),
        runnerUpRmsResidualFt: finiteOrNull(correspondence.runner_up_rms_residual_ft),
        alignmentSeparationFt: finiteOrNull(correspondence.alignment_separation_ft),
        alignmentSeparationMinFt: finiteOrNull(correspondence.alignment_separation_min_ft),
        sourceDisplayRing: boundRingIdentity(correspondence.source_display_ring),
        sourceAuthoritativeRing: boundRingIdentity(correspondence.source_authoritative_ring),
      },
      disclosure: boundedText(
        record.disclosure,
        "These EPSG:2263 vertices are bridged from your drawing; approximate proposed input, not a survey and not a city record.",
      ),
      correlationId,
    },
  };
}

/**
 * POST a map-drawn 4326 outline to the internal bridge route and classify the
 * response. Offline by construction: the caller injects `fetchImpl` in tests
 * (committed fixtures); no network dependency lives here.
 */
export async function fetchOutlineBridge(
  request: OutlineBridgeRequest,
  options: OutlineBridgeOptions = {},
): Promise<OutlineBridgeOutcome> {
  const fetchImpl = options.fetchImpl ?? fetch;
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const url = `${apiBaseUrl()}/api/v1/outline-bridge`;

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
        body: JSON.stringify({ srid: 4326, ...request }),
        cache: "no-store",
        signal: controller.signal,
      });
    } catch {
      if (timedOut) return { kind: "client_timeout", timeoutMs };
      if (controller.signal.aborted || externalSignal?.aborted) return { kind: "aborted" };
      return {
        kind: "network_error",
        message:
          "The outline-bridge service could not be reached. Nothing was converted, " +
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

    if (!isDocumentedBridgePair(response.status, state)) {
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
      return { kind: "bridged", report: bounded.report, correlationId };
    }

    // (404, null): generic Not Found — the feature is disabled or unmounted.
    if (response.status === 404 && state === null) {
      return { kind: "feature_unavailable" };
    }

    if (state === "payload_too_large") {
      return {
        kind: "payload_too_large",
        message: boundedText(record?.message, "The drawing was too large to send."),
        correlationId,
      };
    }

    if (state === "invalid_request") {
      return {
        kind: "invalid_request",
        reason: typeof record?.reason === "string" ? boundedToken(record.reason, 48) : null,
        message: boundedText(record?.message, "The drawn outline was refused by the bridge."),
        correlationId,
      };
    }

    if (state === "out_of_neighborhood") {
      return {
        kind: "out_of_neighborhood",
        message: boundedText(
          record?.message,
          "A drawn point fell outside the lot; draw the outline over the shown parcel.",
        ),
        correlationId,
      };
    }

    if (state === "correspondence_unavailable") {
      return {
        kind: "correspondence_unavailable",
        reason: typeof record?.reason === "string" ? boundedToken(record.reason, 48) : null,
        message: boundedText(
          record?.message,
          "The drawing could not be matched to the official parcel geometry.",
        ),
        correlationId,
      };
    }

    if (state === "residual_too_high") {
      return {
        kind: "residual_too_high",
        rmsResidualFt: finiteOrNull(record?.rms_residual_ft),
        residualBoundFt: finiteOrNull(record?.residual_bound_ft),
        message: boundedText(
          record?.message,
          "The drawing did not align closely enough with the official parcel geometry.",
        ),
        correlationId,
      };
    }

    if (state === "source_unavailable") {
      return {
        kind: "source_unavailable",
        sourceId: typeof record?.source_id === "string" ? boundedText(record.source_id, "", 96) : null,
        message: boundedText(record?.message, "An official parcel source could not be reached."),
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
// already-classified outcome. No legal semantics; never "verified"/"best". A
// bridged result announces the disclosed residual so the user hears that the
// converted shape is approximate proposed input, never a survey. `aborted`
// announces nothing (a superseded request).
// ---------------------------------------------------------------------------
export function announcementForOutlineBridge(outcome: OutlineBridgeOutcome): string {
  switch (outcome.kind) {
    case "bridged": {
      const rms = outcome.report.correspondence.rmsResidualFt;
      const residual = rms === null ? "a disclosed" : `a ${rms.toFixed(2)} ft`;
      return (
        `Outline converted: ${outcome.report.vertices.length} points placed in the numeric table ` +
        `with ${residual} fit residual disclosed. These are approximate proposed values, not a ` +
        `survey and not a city record; edit them in the table and run the check.`
      );
    }
    case "feature_unavailable":
      return "Map-drawing conversion is not available in this environment. Enter coordinates in the table instead.";
    case "payload_too_large":
      return "Outline not converted: the drawing was too large to send.";
    case "invalid_request":
      return "Outline not converted: the drawn shape was refused. Adjust the drawn points and try again.";
    case "out_of_neighborhood":
      return "Outline not converted: a drawn point fell outside the shown lot. Draw over the parcel and try again.";
    case "correspondence_unavailable":
      return "Outline not converted: the drawing could not be matched to the official parcel geometry, so no coordinates were produced.";
    case "residual_too_high":
      return "Outline not converted: the drawing did not align closely enough with the official parcel, so no coordinates were produced.";
    case "source_unavailable":
      return "Outline not converted: an official parcel source could not be reached. This is safe to retry.";
    case "internal_error":
      return "Outline not converted: something went wrong on our side. This is safe to retry.";
    case "validation_failure":
      return "Outline not converted: the response did not match the published data contract.";
    case "network_error":
      return "Outline not converted: the bridge service could not be reached.";
    case "client_timeout":
      return "Outline not converted: the request took too long and was cancelled.";
    case "unexpected_response":
      return "Outline not converted: unexpected response from the platform API.";
    case "aborted":
      return "";
  }
}
