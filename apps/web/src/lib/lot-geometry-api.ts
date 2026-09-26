/**
 * HARDENED typed client for GET /api/v1/properties/{bbl}/lot-geometry
 * (task M5-T023, D-040-R001).
 *
 * Contract: services/api/app/api/v1/lot_geometry.py + the generated canonical
 * type packages/contracts/generated/lot_geometry.ts (read-only dependencies).
 * Same discipline as src/lib/address-api.ts / src/lib/api.ts:
 *
 *   1. The (HTTP status, state) pair matrix below mirrors the route's
 *      STATUS_STATE_MATRIX verbatim; any pair outside it renders as the
 *      distinct `unexpected_response` outcome. A body is never routed by its
 *      `state` alone.
 *   2. A 200 body must carry document_kind "lot_outline", display_only === true,
 *      crs === "EPSG:4326", and a recognized `outcome`; its material fields are
 *      mapped into a BOUNDED view (every reflected string through
 *      boundedText/boundedToken) BEFORE any rendering. Branching stays on the
 *      RAW `outcome` string.
 *   3. The generic 404 {"detail":"Not Found"} (flag off / route unmounted) is a
 *      first-class `route_absent` outcome — never an error, never a crash.
 *   4. Requests are cancellable and time-bounded (aborted / client_timeout).
 *
 * DISPLAY-ONLY: this module transports and verifies. It NEVER computes area,
 * dimension, or any measurement from the EPSG:4326 coordinates; it only
 * validates that coordinates are finite numbers before they may reach the map,
 * and passes the geometry through STRUCTURALLY UNCHANGED (every polygon, every
 * interior ring preserved exactly — no ring dropped, no first-polygon pick, no
 * hole filled). The authoritative EPSG:2263 path owns all measurement
 * (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md).
 */

import { boundedText, boundedToken } from "./bounded";

export const DEFAULT_LOT_GEOMETRY_TIMEOUT_MS = 12_000;

/** The route's documented typed error states, verbatim from STATUS_STATE_MATRIX
 * (lot_geometry.py). The four honest OUTLINE outcomes are 200 documents and are
 * NOT error states. */
export const LOT_GEOMETRY_ERROR_STATES = [
  "validation_error",
  "upstream_error",
  "malformed_response",
  "wrong_crs",
  "result_mismatch",
  "internal_contract_error",
  "internal_error",
] as const;
export type LotGeometryErrorState = (typeof LOT_GEOMETRY_ERROR_STATES)[number];

/** The documented (HTTP status, state) pairs, mirrored from the route.
 * "200|" and "404|" carry NO `state` (the outline document discriminates on
 * `outcome`; the 404 is the generic flag-off / unmounted sentinel). */
const DOCUMENTED_PAIRS: ReadonlySet<string> = new Set([
  "200|", // outline document family; the body's own `outcome` discriminates
  "404|", // flag off / unmounted-path sentinel (generic Not Found)
  "422|validation_error",
  "502|upstream_error",
  "502|malformed_response",
  "502|wrong_crs",
  "502|result_mismatch",
  "500|internal_contract_error",
  "500|internal_error",
]);

export const OUTLINE_OUTCOMES = [
  "single_lot",
  "no_outline",
  "multiple_features",
  "invalid_geometry",
] as const;
export type OutlineOutcome = (typeof OUTLINE_OUTCOMES)[number];

/** A geometry whose every coordinate has been validated as a finite number.
 * Structurally identical to the contract geometry (coordinates VERBATIM). */
export type ValidatedGeometry =
  | { type: "Polygon"; coordinates: number[][][] }
  | { type: "MultiPolygon"; coordinates: number[][][][] };

export interface LotOutlineSourceView {
  sourceId: string | null;
  datasetVersion: string | null;
  retrievedAt: string | null;
}

/** Bounded display view of a 200 lot_outline document. */
export interface LotOutlineView {
  /** RAW outcome string for branching; `outcomeToken` is the bounded display. */
  outcome: OutlineOutcome;
  outcomeToken: string;
  bbl: string | null;
  /** Validated, structurally-unchanged geometry — present ONLY when it parsed
   * as finite numbers; null on every non-single_lot outcome (and, defensively,
   * on a single_lot whose coordinates did not validate). */
  geometry: ValidatedGeometry | null;
  /** True when the document claims a single_lot outline but the coordinates
   * failed number validation (a contract violation surfaced honestly, never a
   * fabricated shape). */
  geometryUnusable: boolean;
  featureCount: number;
  reviewRequired: boolean;
  /** RAW reason string for branching; null on non-no_outline outcomes. */
  noOutlineReason: string | null;
  condoClassification: {
    classification: string;
    note: string | null;
  };
  accuracyNote: string;
  attribution: string;
  disclaimer: string;
  notes: string[];
  source: LotOutlineSourceView;
}

export interface LotOutlineDocumentOutcome {
  kind: "document";
  view: LotOutlineView;
  correlationId: string | null;
}

/** Generic 404 {"detail":"Not Found"}: the feature is flag-gated off or the
 * route is unmounted. Benign — the confirm card keeps its ZoLa link. */
export interface LotOutlineRouteAbsentOutcome {
  kind: "route_absent";
  httpStatus: number;
}

export interface LotOutlineErrorOutcome {
  kind: "error";
  state: LotGeometryErrorState;
  httpStatus: number;
  message: string;
  correlationId: string | null;
}

export interface LotOutlineNetworkErrorOutcome {
  kind: "network_error";
  message: string;
}

export interface LotOutlineClientTimeoutOutcome {
  kind: "client_timeout";
  timeoutMs: number;
}

export interface LotOutlineAbortedOutcome {
  kind: "aborted";
}

export interface LotOutlineUnexpectedResponseOutcome {
  kind: "unexpected_response";
  httpStatus: number;
  receivedState: string | null;
  correlationId: string | null;
}

export type LotOutlineOutcome =
  | LotOutlineDocumentOutcome
  | LotOutlineRouteAbsentOutcome
  | LotOutlineErrorOutcome
  | LotOutlineNetworkErrorOutcome
  | LotOutlineClientTimeoutOutcome
  | LotOutlineAbortedOutcome
  | LotOutlineUnexpectedResponseOutcome;

export interface LotGeometryLookupOptions {
  fetchImpl?: typeof fetch;
  signal?: AbortSignal;
  timeoutMs?: number;
  /** Explicit individual tax-map read; omitted preserves the MapPLUTO path. */
  source?: "tax-map";
}

function apiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

function textOrNull(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const bounded = boundedText(value, "");
  return bounded === "" ? null : bounded;
}

/** A finite JS number and not a boolean (which is a number subtype for typeof
 * purposes only in TS, but `typeof true === "boolean"`, so this is belt-and-
 * suspenders against a drifted body). NaN/Infinity are rejected. */
function isFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

/** A GeoJSON position: at least two finite-number ordinates. Extra ordinates
 * (z/m) are tolerated but the whole position must be finite numbers. */
function isValidPosition(value: unknown): value is number[] {
  return (
    Array.isArray(value) && value.length >= 2 && value.every(isFiniteNumber)
  );
}

function isValidRing(value: unknown): value is number[][] {
  return Array.isArray(value) && value.length >= 1 && value.every(isValidPosition);
}

function isValidPolygonCoords(value: unknown): value is number[][][] {
  return Array.isArray(value) && value.length >= 1 && value.every(isValidRing);
}

/**
 * Validate the contract geometry and return it STRUCTURALLY UNCHANGED, or null
 * if it is absent/unusable. Every polygon and every interior ring is preserved
 * exactly (no ring dropped, no first-polygon pick, no hole filled); this is a
 * transport check (are all coordinates finite numbers?), NEVER measurement.
 */
export function validateOutlineGeometry(value: unknown): ValidatedGeometry | null {
  const geom = asRecord(value);
  if (geom === null) return null;
  const coords = geom.coordinates;
  if (geom.type === "Polygon") {
    return isValidPolygonCoords(coords) ? { type: "Polygon", coordinates: coords } : null;
  }
  if (geom.type === "MultiPolygon") {
    if (
      Array.isArray(coords) &&
      coords.length >= 1 &&
      coords.every(isValidPolygonCoords)
    ) {
      return { type: "MultiPolygon", coordinates: coords as number[][][][] };
    }
    return null;
  }
  return null;
}

function stringArray(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  const out: string[] = [];
  for (const entry of value) {
    const bounded = textOrNull(entry);
    if (bounded !== null) out.push(bounded);
  }
  return out;
}

function documentView(record: Record<string, unknown>): LotOutlineView {
  const outcome = record.outcome as OutlineOutcome;
  const rawGeometry = validateOutlineGeometry(record.geometry);
  const isSingle = outcome === "single_lot";
  const condo = asRecord(record.condo_classification) ?? {};
  const source = asRecord(record.source) ?? {};
  const noOutlineReason =
    typeof record.no_outline_reason === "string" ? record.no_outline_reason : null;
  return {
    outcome,
    outcomeToken: boundedToken(outcome, 32) ?? "absent",
    bbl: boundedToken(record.bbl, 32),
    // Geometry travels ONLY on single_lot; on any other outcome we never draw a
    // shape even if the body carried coordinates (fail-safe: no first-pick).
    geometry: isSingle ? rawGeometry : null,
    geometryUnusable: isSingle && rawGeometry === null,
    featureCount:
      isFiniteNumber(record.feature_count) && record.feature_count >= 0
        ? record.feature_count
        : 0,
    reviewRequired: record.review_required === true,
    noOutlineReason,
    condoClassification: {
      classification: boundedToken(condo.classification, 48) ?? "unknown",
      note: textOrNull(condo.note),
    },
    accuracyNote: boundedText(
      record.accuracy_note,
      "This outline is a display-only approximation; no measurement is derived from it.",
    ),
    attribution: boundedText(
      record.attribution,
      "Source attribution not supplied; see source details.",
    ),
    disclaimer: boundedText(
      record.disclaimer,
      "Display only; not a legal boundary survey. The source disclaimer was not supplied.",
    ),
    notes: stringArray(record.notes),
    source: {
      sourceId: boundedToken(source.source_id, 64),
      datasetVersion: boundedToken(source.dataset_version, 32),
      retrievedAt: boundedToken(source.retrieved_at, 40),
    },
  };
}

function isKnownOutcome(value: unknown): value is OutlineOutcome {
  return (
    typeof value === "string" &&
    (OUTLINE_OUTCOMES as readonly string[]).includes(value)
  );
}

/**
 * Fetch the display-only 4326 lot outline for one canonical BBL. The caller
 * must already have decided the surface is enabled (it is only rendered behind
 * the same server-read flag as the whole address confirm tree); this function
 * issues exactly ONE bounded fetch per invocation.
 */
export async function fetchLotGeometry(
  bbl: string,
  options: LotGeometryLookupOptions = {},
): Promise<LotOutlineOutcome> {
  const fetchImpl = options.fetchImpl ?? fetch;
  const timeoutMs = options.timeoutMs ?? DEFAULT_LOT_GEOMETRY_TIMEOUT_MS;
  const query = options.source === "tax-map" ? "?source=tax-map" : "";
  const url = `${apiBaseUrl()}/api/v1/properties/${encodeURIComponent(bbl)}/lot-geometry${query}`;

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
      if (controller.signal.aborted || externalSignal?.aborted) {
        return { kind: "aborted" };
      }
      return {
        kind: "network_error",
        message:
          "The lot-outline service could not be reached. No outline was " +
          "loaded. The address details above are unaffected, and this is safe to retry.",
      };
    }

    // Defense against a stubbed/misbehaving fetch that resolves to a non-Response.
    if (!response || typeof response.status !== "number") {
      return {
        kind: "unexpected_response",
        httpStatus: 0,
        receivedState: null,
        correlationId: null,
      };
    }

    const correlationId = boundedToken(response.headers?.get?.("X-Correlation-ID"));

    let body: unknown = null;
    try {
      body = await response.json();
    } catch {
      if (timedOut) return { kind: "client_timeout", timeoutMs };
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
    // RAW state for the pair check; bounded form is DISPLAY-only.
    const state = record && typeof record.state === "string" ? record.state : null;
    const pairKey = `${response.status}|${state ?? ""}`;

    if (response.status === 200) {
      if (
        record === null ||
        record.document_kind !== "lot_outline" ||
        record.display_only !== true ||
        record.crs !== "EPSG:4326" ||
        !isKnownOutcome(record.outcome)
      ) {
        return {
          kind: "unexpected_response",
          httpStatus: 200,
          receivedState:
            record && typeof record.outcome === "string"
              ? boundedToken(record.outcome, 48)
              : null,
          correlationId,
        };
      }
      // An older API may ignore an unknown query parameter. Never let its
      // MapPLUTO billing/complex shape masquerade as the requested DOF lot.
      if (options.source === "tax-map" && (
        record.contract_version !== "1.1.0" ||
        asRecord(record.source)?.source_id !== "nyc-dof-digital-tax-map" ||
        record.bbl !== bbl
      )) {
        return {
          kind: "error", state: "result_mismatch", httpStatus: 200,
          message: "The returned outline does not identify the requested tax-map parcel and source.",
          correlationId,
        };
      }
      return { kind: "document", view: documentView(record), correlationId };
    }

    // Generic 404 (flag off / unmounted): the documented (404, null) sentinel.
    if (response.status === 404 && state === null) {
      return { kind: "route_absent", httpStatus: 404 };
    }

    if (!DOCUMENTED_PAIRS.has(pairKey)) {
      return {
        kind: "unexpected_response",
        httpStatus: response.status,
        receivedState: state === null ? null : boundedToken(state, 48),
        correlationId,
      };
    }

    return {
      kind: "error",
      state: state as LotGeometryErrorState,
      httpStatus: response.status,
      message: boundedText(
        record?.message,
        "The lot-outline service reported a failure without further detail.",
      ),
      correlationId,
    };
  } finally {
    clearTimeout(timer);
    externalSignal?.removeEventListener("abort", onExternalAbort);
  }
}
