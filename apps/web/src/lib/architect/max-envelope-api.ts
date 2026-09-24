/**
 * HARDENED typed POST client for the INTERNAL, UNMOUNTED max-envelope route
 * (task M5-T070, D-082-R003 + D-083).
 *
 * Contract: services/api/app/api/v1/max_envelope_api.py (read-only dependency) —
 * the flag-gated, UNMOUNTED POST /api/v1/max-envelope that derives the maximum
 * buildable envelope for the rectangle-prism massing class from a caller lot
 * context. The 200 body is `MaxEnvelope.as_dict()` plus a top-level
 * `correlation_id`; the fixed server disclosure renders VERBATIM. This module
 * TRANSPORTS, size-bounds, shape-verifies, and BOUNDS every reflected string; it
 * computes NO coordinate and derives NO limit (the server engine is the single
 * truth surface — the no-client-math doctrine).
 *
 * Discipline copied EXACTLY from src/lib/outline-bridge-api.ts (the accepted
 * internal-client precedent): the documented (HTTP status, state) pair matrix
 * mirrored verbatim, the raw body size-bounded BEFORE parse (fail-closed), every
 * reflected string boundedText/boundedToken-capped, cancellable + time-bounded
 * requests, and an injectable `fetchImpl` so tests run offline.
 */

import { apiBaseUrl } from "@/lib/api";
import { boundedText, boundedToken, boundedZoningDistrict } from "@/lib/bounded";
import type { PropertyProfile } from "@/lib/contract";

/** The UNMOUNTED route path this client targets (mounting is a later release seam). */
export const MAX_ENVELOPE_ROUTE = "/api/v1/max-envelope";

/** Default request budget; kept below the Playwright timeout so the timeout
 * journey is provable in CI without configuration. */
export const DEFAULT_TIMEOUT_MS = 12_000;

/** Response-body ceiling before parse (fail-closed). The envelope is a small
 * document; a response declaring more is rejected rather than parsed and walked. */
export const MAX_RESPONSE_BYTES = 512_000;

// ---------------------------------------------------------------------------
// Request contract — mirrors max_envelope_api.py exactly (never guessed):
//   { lot: { area_sq_ft, area_provenance, lot_line_segments[], street_lines[] },
//     lot_rule_facts: { <caller lot facts> }, label? }
// lot_line_segments/street_lines carry EPSG:2263 coordinates; this surface sends
// none (the profile's display geometry is 4326 and NEVER measured), so the engine
// returns the binding limits with an explicit placement gap and no candidate.
// ---------------------------------------------------------------------------
export interface MaxEnvelopeLotLine {
  id: string;
  start: [number, number];
  end: [number, number];
}
export interface MaxEnvelopeRequestLot {
  area_sq_ft: number;
  area_provenance: { source_id: string };
  lot_line_segments: MaxEnvelopeLotLine[];
  street_lines: unknown[];
}
export interface MaxEnvelopeRequest {
  lot: MaxEnvelopeRequestLot;
  lot_rule_facts: Record<string, string>;
  label?: string;
}

// ---------------------------------------------------------------------------
// Gap-reason vocabulary — the EXACT machine tokens the server's EnvelopeGapReason
// enum emits (services/api/app/scenario/max_envelope.py :132-146, read-only). Kept
// here as a CLOSED union so the panel's analyst-copy map is exhaustive AT COMPILE
// TIME (a `Record<EnvelopeGapReason, string>` fails to compile if a token is added
// and left uncopied). A server token OUTSIDE this set is never invented copy: the
// panel renders it verbatim (fail-honest). This is a contract mirror — never
// guessed; if the server enum grows, this tuple and the copy map move together.
// ---------------------------------------------------------------------------
export const ENVELOPE_GAP_REASONS = [
  "no_applicable_rule",
  "allowance_unresolved",
  "family_unsupported",
  "non_commensurable_with_massing",
] as const;
export type EnvelopeGapReason = (typeof ENVELOPE_GAP_REASONS)[number];

// ---------------------------------------------------------------------------
// Bounded view models — what the panel reads. Every string is already bounded;
// numbers are verbatim server values (the binding allowance is load-bearing and
// must NOT be rounded/laundered here).
// ---------------------------------------------------------------------------
export interface EnvelopeConflictAdvisoryView {
  competingRuleIds: string[];
  note: string | null;
}
/** One binding-rule citation the SERVER emitted for a dimension (a section-level
 * ZR reference). The analyst reads the actual reference, not merely a count — the
 * section is load-bearing provenance and must survive to the panel. Mirrors the
 * evaluator citation shape (`_citations_with_provenance`: snapshot_id + section);
 * every string is bounded before render. */
export interface EnvelopeCitationView {
  section: string | null;
  snapshotId: string | null;
}
export interface EnvelopeDimensionView {
  dimensionId: string;
  family: string;
  label: string;
  unit: string;
  direction: string;
  saturating: boolean;
  bindingValue: number | null;
  bindingRuleId: string | null;
  bindingRuleVersion: string | null;
  coverageStatus: string | null;
  outCompetedRuleIds: string[];
  /** The ACTUAL server-provided binding-rule citations (section references), not
   * only their count. Empty for a gap dimension (the engine resolved no rule). */
  citations: EnvelopeCitationView[];
  citationCount: number;
  gapReason: string | null;
  conflictAdvisory: EnvelopeConflictAdvisoryView | null;
  detail: string;
}
/** The shape the adoption path seeds from (structurally a `CandidateSeed`). Only
 * present when the server emitted a candidate whose block shape verified here. */
export interface EnvelopeCandidateView {
  outline: { srid: number; vertices: Array<[number, number]> };
  levels: Array<{ level_index: number; floor_count: number; floor_to_floor_ft: number }>;
  exterior_walls: Array<{ id: string; start_vertex_index: number; end_vertex_index: number }>;
}
export interface EnvelopePlacementView {
  status: string;
  detail: string;
  contained: boolean | null;
}
export interface EnvelopeView {
  massingClass: string;
  label: string | null;
  disclosure: string;
  dimensions: EnvelopeDimensionView[];
  candidate: EnvelopeCandidateView | null;
  candidateNotes: string[];
  placement: EnvelopePlacementView;
  summary: { binding: number; gap: number; saturatingBinding: number; total: number };
  correlationId: string | null;
}

// ---------------------------------------------------------------------------
// Outcome union — the documented route envelopes plus the browser-level modes.
// ---------------------------------------------------------------------------
export interface EnvelopeOutcome {
  kind: "envelope";
  envelope: EnvelopeView;
  correlationId: string | null;
}
/** Flag off / unmounted: generic 404 {"detail":"Not Found"} — benign here. */
export interface EnvelopeFeatureUnavailableOutcome {
  kind: "feature_unavailable";
}
export interface EnvelopePayloadTooLargeOutcome {
  kind: "payload_too_large";
  message: string;
  correlationId: string | null;
}
/** (422, validation_error) — malformed body or a typed precondition refusal. */
export interface EnvelopeInvalidRequestOutcome {
  kind: "invalid_request";
  field: string | null;
  message: string;
  correlationId: string | null;
}
export interface EnvelopeInternalErrorOutcome {
  kind: "internal_error";
  message: string;
  correlationId: string | null;
}
/** A 200 whose body did not match the envelope contract. */
export interface EnvelopeValidationFailureOutcome {
  kind: "validation_failure";
  problems: string[];
  correlationId: string | null;
}
export interface EnvelopeNetworkErrorOutcome {
  kind: "network_error";
  message: string;
}
export interface EnvelopeClientTimeoutOutcome {
  kind: "client_timeout";
  timeoutMs: number;
}
export interface EnvelopeAbortedOutcome {
  kind: "aborted";
}
export interface EnvelopeUnexpectedResponseOutcome {
  kind: "unexpected_response";
  httpStatus: number;
  receivedState: string | null;
  correlationId: string | null;
}

export type MaxEnvelopeOutcome =
  | EnvelopeOutcome
  | EnvelopeFeatureUnavailableOutcome
  | EnvelopePayloadTooLargeOutcome
  | EnvelopeInvalidRequestOutcome
  | EnvelopeInternalErrorOutcome
  | EnvelopeValidationFailureOutcome
  | EnvelopeNetworkErrorOutcome
  | EnvelopeClientTimeoutOutcome
  | EnvelopeAbortedOutcome
  | EnvelopeUnexpectedResponseOutcome;

/** Outcomes on which a Retry is meaningful (recoverable server/network faults).
 * A typed refusal / feature-off is a RESULT, not a fault, so it carries no Retry. */
export function maxEnvelopeOutcomeIsRecoverable(outcome: MaxEnvelopeOutcome): boolean {
  return (
    outcome.kind === "internal_error" ||
    outcome.kind === "validation_failure" ||
    outcome.kind === "network_error" ||
    outcome.kind === "client_timeout" ||
    outcome.kind === "unexpected_response"
  );
}

// ---------------------------------------------------------------------------
// Exact (HTTP status, state) pair matrix — mirrors MAX_ENVELOPE_STATUS_STATE_MATRIX
// (max_envelope_api.py) verbatim.
// ---------------------------------------------------------------------------
type DocumentedPair = readonly [number, string | null];

const DOCUMENTED_PAIRS: readonly DocumentedPair[] = [
  [200, null], // the maximum-buildable envelope (NO state)
  [404, null], // flag off / unmounted-path sentinel
  [413, "payload_too_large"],
  [422, "validation_error"],
  [500, "internal_error"],
] as const;

const PAIR_KEYS: ReadonlySet<string> = new Set(
  DOCUMENTED_PAIRS.map(([status, state]) => `${status}:${state ?? ""}`),
);

export function isDocumentedMaxEnvelopePair(status: number, state: string | null): boolean {
  return PAIR_KEYS.has(`${status}:${state ?? ""}`);
}

export interface MaxEnvelopeOptions {
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
function stringOrNull(value: unknown, max = 96): string | null {
  return typeof value === "string" ? boundedText(value, "", max) || null : null;
}

// ---------------------------------------------------------------------------
// Candidate shape verification. A candidate is offered for adoption ONLY when its
// block shape verifies here (finite 2263 outline vertices, finite levels, integer
// wall references). A malformed candidate is dropped (the binding limits still
// stand) rather than laundered into an adoptable draft.
// ---------------------------------------------------------------------------
function boundCandidate(value: unknown): EnvelopeCandidateView | null {
  const record = asRecord(value);
  if (!record) return null;
  const outline = asRecord(record.outline);
  const rawVertices = outline?.vertices;
  if (!Array.isArray(rawVertices) || rawVertices.length === 0) return null;
  const vertices: Array<[number, number]> = [];
  for (const raw of rawVertices) {
    if (!Array.isArray(raw) || raw.length < 2) return null;
    const x = finiteOrNull(raw[0]);
    const y = finiteOrNull(raw[1]);
    if (x === null || y === null) return null;
    vertices.push([x, y]);
  }
  const srid = finiteOrNull(outline?.srid);
  if (srid !== 2263) return null;
  const rawLevels = record.levels;
  if (!Array.isArray(rawLevels)) return null;
  const levels: EnvelopeCandidateView["levels"] = [];
  for (const raw of rawLevels) {
    const l = asRecord(raw);
    const levelIndex = finiteOrNull(l?.level_index);
    const floorCount = finiteOrNull(l?.floor_count);
    const ftf = finiteOrNull(l?.floor_to_floor_ft);
    if (levelIndex === null || floorCount === null || ftf === null) return null;
    levels.push({ level_index: levelIndex, floor_count: floorCount, floor_to_floor_ft: ftf });
  }
  const rawWalls = record.exterior_walls;
  if (!Array.isArray(rawWalls)) return null;
  const walls: EnvelopeCandidateView["exterior_walls"] = [];
  for (const raw of rawWalls) {
    const w = asRecord(raw);
    const start = finiteOrNull(w?.start_vertex_index);
    const end = finiteOrNull(w?.end_vertex_index);
    if (typeof w?.id !== "string" || start === null || end === null) return null;
    walls.push({ id: boundedText(w.id, "W", 32), start_vertex_index: start, end_vertex_index: end });
  }
  return { outline: { srid: 2263, vertices }, levels, exterior_walls: walls };
}

function boundDimension(value: unknown): EnvelopeDimensionView | null {
  const record = asRecord(value);
  if (!record) return null;
  if (typeof record.dimension_id !== "string" || typeof record.label !== "string") return null;
  const advisoryRecord = asRecord(record.conflict_advisory);
  let conflictAdvisory: EnvelopeConflictAdvisoryView | null = null;
  if (advisoryRecord) {
    const competing = Array.isArray(advisoryRecord.competing_rule_ids)
      ? advisoryRecord.competing_rule_ids
          .filter((r): r is string => typeof r === "string")
          .map((r) => boundedText(r, "rule", 64))
      : [];
    conflictAdvisory = { competingRuleIds: competing, note: stringOrNull(advisoryRecord.note, 300) };
  }
  const outCompeted = Array.isArray(record.out_competed_rule_ids)
    ? record.out_competed_rule_ids
        .filter((r): r is string => typeof r === "string")
        .map((r) => boundedText(r, "rule", 64))
    : [];
  // Expose the ACTUAL binding-rule citations the server emitted (section-level
  // references), each string bounded before render — not merely their count.
  const citations: EnvelopeCitationView[] = Array.isArray(record.rule_citations)
    ? record.rule_citations
        .map((raw) => asRecord(raw))
        .filter((c): c is Record<string, unknown> => c !== null)
        .map((c) => ({ section: stringOrNull(c.section, 48), snapshotId: stringOrNull(c.snapshot_id, 64) }))
    : [];
  return {
    dimensionId: boundedText(record.dimension_id, "dimension", 64),
    family: boundedText(record.family, "unknown", 64),
    label: boundedText(record.label, "development limit", 120),
    unit: boundedText(record.unit, "", 32),
    direction: boundedText(record.direction, "", 16),
    saturating: record.saturating === true,
    bindingValue: finiteOrNull(record.binding_value),
    bindingRuleId: stringOrNull(record.binding_rule_id, 64),
    bindingRuleVersion: stringOrNull(record.binding_rule_version, 64),
    coverageStatus: stringOrNull(record.coverage_status, 48),
    outCompetedRuleIds: outCompeted,
    citations,
    citationCount: Array.isArray(record.rule_citations) ? record.rule_citations.length : 0,
    gapReason: stringOrNull(record.gap_reason, 64),
    conflictAdvisory,
    detail: boundedText(record.detail, "", 600),
  };
}

// ---------------------------------------------------------------------------
// 200-body bounding: shape-verify the envelope and bound every reflected string
// BEFORE it can render. A malformed core (no dimensions / no summary / no
// disclosure) is a distinct `validation_failure`, never a partial render.
// ---------------------------------------------------------------------------
function boundEnvelope(
  body: unknown,
  correlationId: string | null,
): { ok: true; envelope: EnvelopeView } | { ok: false; problems: string[] } {
  const record = asRecord(body);
  if (!record) return { ok: false, problems: ["envelope body was not a JSON object"] };
  const rawDimensions = record.dimensions;
  if (!Array.isArray(rawDimensions) || rawDimensions.length === 0) {
    return { ok: false, problems: ["envelope is missing a non-empty dimensions array"] };
  }
  const dimensions: EnvelopeDimensionView[] = [];
  for (const raw of rawDimensions) {
    const dim = boundDimension(raw);
    if (dim === null) return { ok: false, problems: ["an envelope dimension had an unusable shape"] };
    dimensions.push(dim);
  }
  const summaryRecord = asRecord(record.summary);
  const binding = finiteOrNull(summaryRecord?.binding);
  const gap = finiteOrNull(summaryRecord?.gap);
  const saturatingBinding = finiteOrNull(summaryRecord?.saturating_binding);
  const total = finiteOrNull(summaryRecord?.total);
  if (binding === null || gap === null || saturatingBinding === null || total === null) {
    return { ok: false, problems: ["envelope summary is missing its binding/gap/total counts"] };
  }
  const disclosure = typeof record.disclosure === "string" ? boundedText(record.disclosure, "", 2000) : "";
  if (disclosure === "") {
    return { ok: false, problems: ["envelope is missing the required server disclosure"] };
  }
  const placementRecord = asRecord(record.candidate_placement);
  const placement: EnvelopePlacementView = {
    status: boundedText(placementRecord?.status, "unknown", 48),
    detail: boundedText(placementRecord?.detail, "", 600),
    contained: typeof placementRecord?.contained === "boolean" ? placementRecord.contained : null,
  };
  const candidateNotes = Array.isArray(record.candidate_notes)
    ? record.candidate_notes
        .filter((n): n is string => typeof n === "string")
        .map((n) => boundedText(n, "", 300))
    : [];
  return {
    ok: true,
    envelope: {
      massingClass: boundedText(record.massing_class, "unknown", 48),
      label: stringOrNull(record.label, 200),
      disclosure,
      dimensions,
      candidate: boundCandidate(record.candidate),
      candidateNotes,
      placement,
      summary: { binding, gap, saturatingBinding, total },
      correlationId,
    },
  };
}

/**
 * POST a lot context to the internal max-envelope route and classify the
 * response. Offline by construction: the caller injects `fetchImpl` in tests.
 */
export async function fetchMaxEnvelope(
  request: MaxEnvelopeRequest,
  options: MaxEnvelopeOptions = {},
): Promise<MaxEnvelopeOutcome> {
  const fetchImpl = options.fetchImpl ?? fetch;
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const url = `${apiBaseUrl()}${MAX_ENVELOPE_ROUTE}`;

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
          "The development-limits service could not be reached. Nothing was computed, " +
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

    if (!isDocumentedMaxEnvelopePair(response.status, state)) {
      return {
        kind: "unexpected_response",
        httpStatus: response.status,
        receivedState: state === null ? null : boundedToken(state, 48),
        correlationId,
      };
    }

    if (response.status === 200) {
      const bounded = boundEnvelope(body, correlationId);
      if (!bounded.ok) {
        return { kind: "validation_failure", problems: bounded.problems, correlationId };
      }
      return { kind: "envelope", envelope: bounded.envelope, correlationId };
    }

    // (404, null): generic Not Found — the feature is disabled or unmounted.
    if (response.status === 404 && state === null) {
      return { kind: "feature_unavailable" };
    }

    if (state === "payload_too_large") {
      return {
        kind: "payload_too_large",
        message: boundedText(record?.message, "The request was too large to send."),
        correlationId,
      };
    }

    if (state === "validation_error") {
      return {
        kind: "invalid_request",
        field: stringOrNull(record?.field, 200),
        message: boundedText(record?.message, "The lot context was refused by the service."),
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
// Request assembly from the architect surface's existing lot context. The
// answer-first panel (D-083-R003) renders BEFORE any designer input, so the
// request is built from the profile alone: the recorded lot AREA (the coverage
// denominator) and a single recorded zoning district. NO lot geometry is sent —
// the profile's geometry is display 4326 and never measured — so the engine
// returns the binding limits with an explicit placement gap and no candidate.
// A profile without a usable finite lot area yields NULL: the panel degrades to a
// typed "cannot compute" card, never a fabricated limit.
// ---------------------------------------------------------------------------
export function maxEnvelopeRequestForProfile(profile: PropertyProfile): MaxEnvelopeRequest | null {
  const area = profile.lot_facts?.lotarea?.value;
  if (typeof area !== "number" || !Number.isFinite(area) || area <= 0) {
    return null;
  }
  const districts = Array.isArray(profile.zoning?.districts) ? profile.zoning.districts : [];
  const lot_rule_facts: Record<string, string> = {};
  if (districts.length === 1) {
    const district = boundedZoningDistrict(districts[0]);
    if (district) lot_rule_facts.zoning_district = district;
  }
  return {
    lot: {
      area_sq_ft: area,
      area_provenance: { source_id: "architect_surface_lot_context" },
      lot_line_segments: [],
      street_lines: [],
    },
    lot_rule_facts,
    label: `BBL ${profile.identity.bbl} preliminary development limits`,
  };
}

// ---------------------------------------------------------------------------
// Aggregate state (D-083-R004): while ANY dimension is an honest gap OR ANY
// conflict advisory is present, the aggregate presentation stays visibly
// INCOMPLETE — there is no unrestricted "complete"/green aggregate state. This is
// the mutation-sensitive predicate the panel and its tests key on.
// ---------------------------------------------------------------------------
export function envelopeHasConflictAdvisory(envelope: EnvelopeView): boolean {
  return envelope.dimensions.some((d) => d.conflictAdvisory !== null);
}

/** The three mutually-exclusive presentation states of one dimension row. */
export type DimensionRowKind = "value" | "gap" | "contract_violation";

/**
 * Classify a dimension row under the D-083-R004 BINDING-OR-GAP XOR invariant. The
 * server contract (max_envelope.py EnvelopeDimensionResult: "Exactly one of
 * binding_value and gap_reason is set") guarantees exactly one of `bindingValue`
 * and `gapReason` is present. A row that carries BOTH or NEITHER breaks that
 * invariant — it MUST NEVER render as a limit value (a NEITHER row would otherwise
 * render `null` as a number; a BOTH row would launder an untrustworthy value). It
 * surfaces instead as a typed `contract_violation` that keeps the aggregate visibly
 * incomplete. This is the mutation-sensitive predicate the panel and its tests key
 * on: removing the XOR check reddens the both/neither specs.
 */
export function dimensionRowKind(d: EnvelopeDimensionView): DimensionRowKind {
  const hasValue = d.bindingValue !== null;
  const hasGap = d.gapReason !== null;
  if (hasValue === hasGap) return "contract_violation"; // both set, or neither set
  return hasValue ? "value" : "gap";
}

/** True when ANY dimension breaks the binding-or-gap XOR invariant (D-083-R004).
 * A contract violation forces the aggregate to stay visibly INCOMPLETE, exactly
 * like an honest gap or a conflict advisory — no unrestricted "complete" state. */
export function envelopeHasContractViolation(envelope: EnvelopeView): boolean {
  return envelope.dimensions.some((d) => dimensionRowKind(d) === "contract_violation");
}

export function envelopeAggregateIsComplete(envelope: EnvelopeView): boolean {
  return (
    envelope.summary.gap === 0 &&
    !envelopeHasConflictAdvisory(envelope) &&
    !envelopeHasContractViolation(envelope)
  );
}

/** Adoption (D-083-R002/AS-4) is offered ONLY for a server-emitted candidate that
 * the engine FITTED to the lot and PROVED contained; every other placement leaves
 * no adoptable building. */
export function candidateIsAdoptable(envelope: EnvelopeView): boolean {
  return (
    envelope.candidate !== null &&
    envelope.placement.status === "fitted" &&
    envelope.placement.contained === true
  );
}

// ---------------------------------------------------------------------------
// Assistive-technology announcement — derived deterministically from the
// already-classified outcome. No legal semantics; never "maximum allowed
// building" / "best". `aborted` announces nothing (a superseded request).
// ---------------------------------------------------------------------------
export function announcementForMaxEnvelope(outcome: MaxEnvelopeOutcome): string {
  switch (outcome.kind) {
    case "envelope": {
      const { summary } = outcome.envelope;
      const incomplete = !envelopeAggregateIsComplete(outcome.envelope);
      const lead = incomplete
        ? `Preliminary development limits loaded, but ${summary.gap} of ${summary.total} could not be checked`
        : `Preliminary development limits loaded for ${summary.total} dimensions`;
      return `${lead}. A rules-derived estimate requiring professional review, not a maximum permitted building.`;
    }
    case "feature_unavailable":
      return "Preliminary development limits are not available in this environment.";
    case "payload_too_large":
      return "Preliminary development limits not loaded: the request was too large to send.";
    case "invalid_request":
      return "Preliminary development limits not loaded: the lot context was refused.";
    case "internal_error":
      return "Preliminary development limits not loaded: something went wrong on our side. This is safe to retry.";
    case "validation_failure":
      return "Preliminary development limits not loaded: the response did not match the published data contract.";
    case "network_error":
      return "Preliminary development limits not loaded: the service could not be reached.";
    case "client_timeout":
      return "Preliminary development limits not loaded: the request took too long and was cancelled.";
    case "unexpected_response":
      return "Preliminary development limits not loaded: unexpected response from the platform API.";
    case "aborted":
      return "";
  }
}
