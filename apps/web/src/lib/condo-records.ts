"use client";

/**
 * HARDENED typed client + hook for GET /api/v1/properties/{bbl}/condo-records
 * (task M5-T052, DB-031).
 *
 * Contract: services/api/app/api/v1/condo_records.py (read-only dependency).
 * Same discipline as src/lib/record-address.ts:
 *
 *   1. The (HTTP status, state) pair set below mirrors the route's
 *      CONDO_RECORDS_STATUS_STATE_MATRIX; any pair outside it renders as the
 *      distinct `unexpected_response` outcome. A body is never routed by `state`
 *      alone.
 *   2. A 200 body must carry document_kind "condo_records" and a recognized
 *      `outcome`; every reflected string is bounded BEFORE it may render.
 *      Branching stays on the RAW `outcome` string.
 *   3. The generic 404 {"detail":"Not Found"} (flag off / route unmounted) is a
 *      first-class `route_absent` outcome — never an error, never a crash.
 *   4. Requests are cancellable and time-bounded (aborted / client_timeout).
 *
 * CROSS-BOUNDARY TOKEN PIN (the T045 G3-A2 answer). The outcome tokens below are
 * the SAME literals the api emits (app.connectors.condo_base_lot OUTCOME_*) and
 * the SAME literals the web allowance-withhold guard branches on
 * (PropertyOverview.condoWithholdsAllowances imports CONDO_OUTCOME_RESOLVED_SINGLE
 * from here). api and web share ONE outcome vocabulary, pinned by tests on both
 * sides, so the records view and the fail-safe guard can never classify the same
 * condo resolution differently.
 *
 * RECORDS, NEVER ALLOWANCES (D-073-R006). This module transports the recorded
 * base-lot(s) of a condo for DISPLAY as city records. It derives no value; the
 * resolver makes no zoning determination, so a base lot's recorded zoning is a
 * null record (honest UNKNOWN), never a fabricated district.
 */

import { useEffect, useState } from "react";
import { apiBaseUrl } from "./api";
import { validateBblInput } from "./bbl";
import { boundedText, boundedToken } from "./bounded";

export const DEFAULT_CONDO_RECORDS_TIMEOUT_MS = 12_000;

// --- Outcome-token vocabulary (the cross-boundary token pin) ----------------
// Each literal EQUALS the resolver's app.connectors.condo_base_lot OUTCOME_*.
export const CONDO_OUTCOME_NOT_CONDO_BILLING = "not_condo_billing";
export const CONDO_OUTCOME_RESOLVED_SINGLE = "resolved_single_base_lot";
export const CONDO_OUTCOME_MULTI_LOT = "multi_lot_set";
export const CONDO_OUTCOME_UNRESOLVED = "unresolved";
export const CONDO_OUTCOME_ERROR = "error";

export const CONDO_RECORDS_OUTCOMES = [
  CONDO_OUTCOME_NOT_CONDO_BILLING,
  CONDO_OUTCOME_RESOLVED_SINGLE,
  CONDO_OUTCOME_MULTI_LOT,
  CONDO_OUTCOME_UNRESOLVED,
  CONDO_OUTCOME_ERROR,
] as const;
export type CondoRecordsChannelOutcome = (typeof CONDO_RECORDS_OUTCOMES)[number];

/** The route's documented typed error states, verbatim from
 * CONDO_RECORDS_STATUS_STATE_MATRIX. The five honest outcomes are 200 documents
 * and are NOT error states (a typed resolver failure is the 200 `error`
 * outcome, not an HTTP error). */
export const CONDO_RECORDS_ERROR_STATES = [
  "validation_error",
  "internal_error",
] as const;
export type CondoRecordsErrorState =
  (typeof CONDO_RECORDS_ERROR_STATES)[number];

/** The documented (HTTP status, state) pairs, mirrored from the route. "200|"
 * and "404|" carry NO `state` (the document discriminates on `outcome`; the 404
 * is the generic flag-off / unmounted sentinel). */
const DOCUMENTED_PAIRS: ReadonlySet<string> = new Set([
  "200|",
  "404|",
  "422|validation_error",
  "500|internal_error",
]);

export interface CondoBaseLotRecord {
  /** The recorded base tax lot BBL. */
  bbl: string;
  /** The recorded zoning district for this base lot, or null when the resolver
   * carries none (it makes no zoning determination). Never fabricated. */
  recordedZoning: string | null;
  /** EXPLICIT availability label for the recorded zoning ("recorded" | "unknown"),
   * mirrored from the api's recorded_zoning_status so the client honestly gates the
   * divergent-zoning notice (only when zoning is actually recorded) and the
   * recorded-zoning gap note (only when at least one base lot's zoning is unknown).
   * Falls back to a value derived from recordedZoning when the source omits it. */
  recordedZoningStatus: string;
}

/** One recorded SODA query the resolver actually performed. Per-record
 * provenance for the transported records: which dataset, when it was retrieved,
 * the dataset version (SODA rowsUpdatedAt) the source stamped, and how many rows
 * it returned. Every field is honest-nullable — an absent value is `null`
 * (rendered as an explicit unknown), never invented. */
export interface CondoRecordsQueryProvenance {
  datasetId: string | null;
  queryKind: string | null;
  retrievedAt: string | null;
  rowsUpdatedAt: string | null;
  recordCount: number | null;
}

export interface CondoRecordsProvenance {
  sourceId: string | null;
  datasetIds: string[];
  retrievedAt: string | null;
  /** The dataset version (SODA rowsUpdatedAt) for the transported records, when
   * the source stamped one; null when the source omitted it (honest unknown,
   * never fabricated). Carried explicitly so the records display can name the
   * version of the city data it is showing. */
  datasetVersion: string | null;
  /** Per-record provenance: one entry per SODA query the resolver performed. */
  queries: CondoRecordsQueryProvenance[];
}

/** The substrate record (G3-A4): only present on a resolved-single outcome. */
export interface CondoSubstitutionRecord {
  enteredBbl: string | null;
  analyzedBbl: string | null;
  note: string | null;
}

// --- Site-definition confirmation surfacing (M5-T059, D-078) -----------------
// READ-ONLY view of the api's additive `site_definition` block on a multi-lot
// document. Slice 1 has NO mutation client: this parses the recorded human
// confirmation(s) for display; it never selects a site and never drives a
// calculation (D-078-R002).
export const SITE_DEFINITION_STATUS_CONFIRMED = "confirmed";
export const SITE_DEFINITION_STATUS_UNCONFIRMED = "unconfirmed";
/** The self-attested attestation-status literal, pinned to the api's
 * AttestationStatus.UNAUTHENTICATED_SELF_ATTESTED. A confirmation carrying it is
 * ALWAYS refused for any calculation use, regardless of what the payload's
 * refused_for_calculation flag claims — identity is not yet verified (B-001), so
 * the loud refusal can never be cleared by an untrusted body. */
export const SITE_DEFINITION_ATTESTATION_SELF_ATTESTED =
  "unauthenticated_self_attested";
/** The ACTIVE confirmation-status literal, pinned to the api's
 * ConfirmationStatus.ACTIVE. Only a confirmation whose OWN derived status is
 * active may surface as the recorded active confirmation. */
export const SITE_DEFINITION_CONFIRMATION_STATUS_ACTIVE = "active";

/** One recorded confirmation, bounded for display. */
export interface SiteDefinitionConfirmationView {
  recordId: string | null;
  status: string | null;
  confirmerName: string | null;
  confirmerRole: string | null;
  attestationStatus: string | null;
  /** True when the confirmation is refused for any calculation use (a
   * self-attested confirmation is, until authentication exists — B-001). Defaults
   * to TRUE (fail-safe) when the source omits or malforms it. */
  refusedForCalculation: boolean;
  confirmedAt: string | null;
  parcels: string[];
  reason: string | null;
  note: string | null;
}

/** The additive `site_definition` block: the recorded human confirmation of a
 * multi-lot site, or an explicit UNCONFIRMED status. Never a system selection. */
export interface SiteDefinitionView {
  /** "confirmed" | "unconfirmed" (bounded; defaults to "unconfirmed"). */
  status: string;
  condoKey: string | null;
  /** The single ACTIVE confirmation, or null when unconfirmed. */
  activeConfirmation: SiteDefinitionConfirmationView | null;
  /** Count of recorded confirmations in the chain (active + superseded + revoked). */
  confirmationCount: number;
  /** A surfaced factual discrepancy between the recorded parcels and the current
   * resolver output; never changes the confirmation's status (D-078-R002). */
  parcelDiscrepancy: {
    recordedParcels: string[];
    currentResolverParcels: string[];
  } | null;
}

/** Bounded display view of a 200 condo_records document. */
export interface CondoRecordsView {
  /** RAW outcome string for branching (one of CONDO_RECORDS_OUTCOMES). */
  outcome: CondoRecordsChannelOutcome;
  /** The BBL the user actually entered (unit OR billing), validated through the
   * shared client BBL parser (lib/bbl.ts, read-only). It is labelled separately
   * from the recorded billing lot so a real unit-BBL input renders under its own
   * "Condo lot you entered" label instead of the billing lot's unknown. Null only
   * when the source omitted or malformed it. */
  enteredBbl: string | null;
  /** The lot class of the entered BBL ("billing" | "unit" | ...), when the source
   * carries it; null otherwise. */
  enteredLotClass: string | null;
  /** The condo billing/unit lot the records are recorded FOR; null for a
   * non-condo input. */
  billingBbl: string | null;
  /** EXPLICIT availability label for the billing lot ("recorded" | "unknown" |
   * "not_applicable"), mirrored from the api's billing_bbl_status. A unit-class
   * input resolves through a path that returns the base lots but not the billing
   * lot, so its billing lot is a labelled unknown — never the entered unit BBL
   * relabelled as billing. Null only when the source omitted it. */
  billingBblStatus: string | null;
  /** Every recorded base tax lot as a RECORD (empty on non-condo / unresolved /
   * error). */
  baseLots: CondoBaseLotRecord[];
  /** The billing->base substitution record, present only on resolved-single. */
  substitution: CondoSubstitutionRecord | null;
  condoKey: string | null;
  condoNumber: string | null;
  /** The permanent no-collapse boundary notice, present only on multi-lot. */
  divergentZoningNotice: string | null;
  /** The api's recorded_zoning_dependency: present only when at least one base
   * lot's recorded zoning is a genuine unknown, so the surface can honestly
   * explain the gap (recorded zoning comes from a separate zoning-by-lot source
   * not yet connected) rather than showing a bare "unknown". Null when every base
   * lot carries recorded zoning. */
  recordedZoningDependency: string | null;
  /** A bounded human reason for an outcome that carries no records; null
   * otherwise. */
  reason: string | null;
  /** The typed resolver error class, present only on the `error` outcome. */
  errorType: string | null;
  provenance: CondoRecordsProvenance;
  /** The recorded site-definition confirmation surfacing (M5-T059), present only
   * on a multi-lot document that carries the additive `site_definition` block;
   * null otherwise. Read-only display of a human act, never a system selection. */
  siteDefinition: SiteDefinitionView | null;
}

export interface CondoRecordsDocumentOutcome {
  kind: "document";
  view: CondoRecordsView;
  correlationId: string | null;
}

/** Generic 404 {"detail":"Not Found"}: flag-gated off or route unmounted.
 * Benign — the surface simply shows no records section. */
export interface CondoRecordsRouteAbsentOutcome {
  kind: "route_absent";
  httpStatus: number;
}

export interface CondoRecordsErrorOutcome {
  kind: "error";
  state: CondoRecordsErrorState;
  httpStatus: number;
  message: string;
  correlationId: string | null;
}

export interface CondoRecordsNetworkErrorOutcome {
  kind: "network_error";
  message: string;
}

export interface CondoRecordsClientTimeoutOutcome {
  kind: "client_timeout";
  timeoutMs: number;
}

export interface CondoRecordsAbortedOutcome {
  kind: "aborted";
}

export interface CondoRecordsUnexpectedResponseOutcome {
  kind: "unexpected_response";
  httpStatus: number;
  receivedState: string | null;
  correlationId: string | null;
}

export type CondoRecordsOutcome =
  | CondoRecordsDocumentOutcome
  | CondoRecordsRouteAbsentOutcome
  | CondoRecordsErrorOutcome
  | CondoRecordsNetworkErrorOutcome
  | CondoRecordsClientTimeoutOutcome
  | CondoRecordsAbortedOutcome
  | CondoRecordsUnexpectedResponseOutcome;

export interface CondoRecordsLookupOptions {
  fetchImpl?: typeof fetch;
  signal?: AbortSignal;
  timeoutMs?: number;
}

/** Bound a reflected ISO-8601 timestamp: the token charset PLUS the colon and
 * plus-sign an ISO instant legitimately carries ([0-9A-Za-z.:+-]). boundedToken
 * would strip the colons and silently corrupt the value (the sanitizer-boundary
 * lesson: identifiers and timestamps are different vocabularies); anything
 * outside the ISO charset is dropped, the result is capped, and an empty result
 * is an explicit null - never an invented stamp. */
function boundedTimestamp(value: unknown, max = 40): string | null {
  if (typeof value !== "string") {
    return null;
  }
  const cleaned = value.replace(/[^0-9A-Za-z.:+-]/g, "").slice(0, max);
  return cleaned === "" ? null : cleaned;
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

function isKnownOutcome(value: unknown): value is CondoRecordsChannelOutcome {
  return (
    typeof value === "string" &&
    (CONDO_RECORDS_OUTCOMES as readonly string[]).includes(value)
  );
}

/** Bound a reflected BBL-shaped identifier to a plain token; null when absent or
 * unusable (never an invented or empty value). */
function boundedBbl(value: unknown): string | null {
  return boundedToken(value, 20);
}

/** Parse a reflected ENTERED BBL through the shared client BBL validator
 * (lib/bbl.ts, read-only): a well-formed 10-digit BBL is carried as the canonical
 * value so the surface can label it under its own "Condo lot you entered" heading,
 * distinct from the recorded billing lot; anything else is an explicit null (never
 * an invented value). This keeps the ENTERED identity (what the user typed)
 * separate from the recorded BILLING lot the resolver returns, so a real unit-BBL
 * input never renders "not recorded (unknown)" under the entered label. */
function enteredBblValue(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const result = validateBblInput(value);
  return result.ok ? result.canonical : null;
}

function baseLotRecords(value: unknown): CondoBaseLotRecord[] {
  if (!Array.isArray(value)) return [];
  const records: CondoBaseLotRecord[] = [];
  for (const entry of value) {
    const record = asRecord(entry);
    if (record === null) continue;
    const bbl = boundedBbl(record.bbl);
    if (bbl === null) continue; // never render a base lot without a recorded BBL
    const zoning = boundedToken(record.recorded_zoning, 32);
    // Mirror the api's explicit availability label; fall back to a value derived
    // from the recorded zoning so the status is always present and honest.
    const status =
      boundedToken(record.recorded_zoning_status, 16) ??
      (zoning !== null ? "recorded" : "unknown");
    records.push({ bbl, recordedZoning: zoning, recordedZoningStatus: status });
  }
  return records;
}

function substitutionRecord(value: unknown): CondoSubstitutionRecord | null {
  const record = asRecord(value);
  if (record === null) return null;
  return {
    // DB-038(f)-2 (G3-1): the ENTERED BBL is parsed through the strict
    // validateBblInput-backed parser (enteredBblValue), not the looser
    // boundedBbl token cleaner, so a non-canonical entered value is an explicit
    // null instead of a sanitized-but-invalid token — the same discipline the
    // top-level entered_bbl already uses.
    enteredBbl: enteredBblValue(record.entered_bbl),
    analyzedBbl: boundedBbl(record.analyzed_bbl),
    note: typeof record.note === "string" ? boundedText(record.note, "") || null : null,
  };
}

function queryProvenance(value: unknown): CondoRecordsQueryProvenance[] {
  if (!Array.isArray(value)) return [];
  const entries: CondoRecordsQueryProvenance[] = [];
  for (const raw of value) {
    const record = asRecord(raw);
    if (record === null) continue;
    entries.push({
      datasetId: boundedToken(record.dataset_id, 64),
      queryKind: boundedToken(record.query_kind, 48),
      retrievedAt: boundedTimestamp(record.retrieved_at),
      rowsUpdatedAt: boundedTimestamp(record.rows_updated_at),
      recordCount:
        typeof record.record_count === "number" && Number.isFinite(record.record_count)
          ? record.record_count
          : null,
    });
  }
  return entries;
}

function provenanceView(value: unknown): CondoRecordsProvenance {
  const record = asRecord(value) ?? {};
  const datasetIds = Array.isArray(record.dataset_ids)
    ? record.dataset_ids
        .map((entry) => boundedToken(entry, 64))
        .filter((entry): entry is string => entry !== null)
    : [];
  const queries = queryProvenance(record.queries);
  // The dataset version is the SODA rowsUpdatedAt the source stamped on the
  // records; take the first query that carries one, else an explicit unknown
  // (null) — never a fabricated version.
  const datasetVersion =
    queries.find((entry) => entry.rowsUpdatedAt !== null)?.rowsUpdatedAt ?? null;
  return {
    sourceId: boundedToken(record.source_id, 64),
    datasetIds,
    retrievedAt: boundedTimestamp(record.retrieved_at),
    datasetVersion,
    queries,
  };
}

/** Bound a parcel-set array (base-lot BBLs) to a de-duplication-free list of plain
 * tokens, dropping any entry that is absent or unusable — never an invented BBL. */
function boundedParcels(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value
    .map((entry) => boundedBbl(entry))
    .filter((entry): entry is string => entry !== null);
}

/** Parse ONE recorded confirmation (the api's ConfirmationView payload) into a
 * bounded display view. READ-ONLY: this never selects a site (D-078-R002).
 *
 * The refused-for-calculation flag is fail-safe. A SELF-ATTESTED confirmation is
 * ALWAYS refused for calculation (its identity is not yet verified — B-001), so
 * the flag is forced TRUE regardless of what the payload claims: an untrusted
 * body supplying `refused_for_calculation: false` can never clear the loud
 * refusal on a self-attested record. For any other attestation the flag still
 * defaults to TRUE and is cleared only by an explicit boolean `false`, so a
 * missing or malformed flag can never read as calculation-eligible (slice 1 has
 * no calculation path regardless). */
function siteDefinitionConfirmationView(
  value: unknown,
): SiteDefinitionConfirmationView | null {
  const record = asRecord(value);
  if (record === null) return null;
  const confirmer = asRecord(record.confirmer) ?? {};
  const attestationStatus = boundedToken(record.attestation_status, 48);
  const selfAttested =
    attestationStatus === SITE_DEFINITION_ATTESTATION_SELF_ATTESTED;
  const refusedForCalculation = selfAttested
    ? true
    : record.refused_for_calculation !== false;
  return {
    recordId: boundedToken(record.record_id, 64),
    status: boundedToken(record.status, 16),
    confirmerName:
      typeof confirmer.name === "string" ? boundedText(confirmer.name, "") || null : null,
    confirmerRole: boundedToken(confirmer.role, 32),
    attestationStatus,
    refusedForCalculation,
    confirmedAt: boundedTimestamp(record.confirmed_at),
    parcels: boundedParcels(record.parcels),
    reason:
      typeof record.reason === "string" ? boundedText(record.reason, "") || null : null,
    note: typeof record.note === "string" ? boundedText(record.note, "") || null : null,
  };
}

/** Parse the block's `active_confirmation`, returning it ONLY when it is a
 * well-formed ACTIVE confirmation — its OWN derived status is "active" AND it
 * carries a record id. An empty ({}), malformed, or non-active (superseded /
 * revoked) payload yields null, so it can never render as a recorded active
 * confirmation even if the block's top-level status wrongly claims "confirmed". */
function activeConfirmationView(
  value: unknown,
): SiteDefinitionConfirmationView | null {
  const confirmation = siteDefinitionConfirmationView(value);
  if (confirmation === null) return null;
  if (
    confirmation.status !== SITE_DEFINITION_CONFIRMATION_STATUS_ACTIVE ||
    confirmation.recordId === null
  ) {
    return null;
  }
  return confirmation;
}

/** Parse the api's additive `site_definition` block on a multi-lot document.
 * READ-ONLY surfacing of a recorded human confirmation (or an explicit
 * UNCONFIRMED status); never a system selection (D-078-R002). The block is
 * CONFIRMED only when BOTH the top-level status is the exact "confirmed" literal
 * AND a well-formed ACTIVE confirmation is present; otherwise it fails safe to
 * UNCONFIRMED, so an empty, malformed, or non-active confirmation can never read
 * as a confirmed site. Returns null when the block is absent (a non-multi-lot
 * document carries none). */
function siteDefinitionView(value: unknown): SiteDefinitionView | null {
  const record = asRecord(value);
  if (record === null) return null;
  const activeConfirmation = activeConfirmationView(record.active_confirmation);
  const status =
    activeConfirmation !== null &&
    boundedToken(record.status, 16) === SITE_DEFINITION_STATUS_CONFIRMED
      ? SITE_DEFINITION_STATUS_CONFIRMED
      : SITE_DEFINITION_STATUS_UNCONFIRMED;
  const confirmations = Array.isArray(record.confirmations)
    ? record.confirmations
    : [];
  const discrepancy = asRecord(record.parcel_discrepancy);
  return {
    status,
    condoKey: boundedToken(record.condo_key, 32),
    activeConfirmation,
    confirmationCount: confirmations.length,
    parcelDiscrepancy:
      discrepancy === null
        ? null
        : {
            recordedParcels: boundedParcels(discrepancy.recorded_parcels),
            currentResolverParcels: boundedParcels(discrepancy.current_resolver_parcels),
          },
  };
}

function documentView(record: Record<string, unknown>): CondoRecordsView {
  return {
    outcome: record.outcome as CondoRecordsChannelOutcome,
    enteredBbl: enteredBblValue(record.entered_bbl),
    enteredLotClass: boundedToken(record.entered_lot_class, 16),
    billingBbl: boundedBbl(record.billing_bbl),
    billingBblStatus: boundedToken(record.billing_bbl_status, 16),
    baseLots: baseLotRecords(record.base_lots),
    substitution: substitutionRecord(record.substitution),
    condoKey: boundedToken(record.condo_key, 32),
    condoNumber: boundedToken(record.condo_number, 32),
    divergentZoningNotice:
      typeof record.divergent_zoning_notice === "string"
        ? boundedText(record.divergent_zoning_notice, "") || null
        : null,
    recordedZoningDependency:
      typeof record.recorded_zoning_dependency === "string"
        ? boundedText(record.recorded_zoning_dependency, "") || null
        : null,
    reason:
      typeof record.reason === "string" ? boundedText(record.reason, "") || null : null,
    errorType: boundedToken(record.error_type, 48),
    provenance: provenanceView(record.provenance),
    siteDefinition: siteDefinitionView(record.site_definition),
  };
}

/**
 * Fetch the condo records view for one canonical BBL. The caller must already
 * have decided the surface is enabled (it is only rendered behind the same
 * server-read flag as the whole internal property flow); this function issues
 * exactly ONE bounded fetch per invocation.
 */
export async function fetchCondoRecords(
  bbl: string,
  options: CondoRecordsLookupOptions = {},
): Promise<CondoRecordsOutcome> {
  const fetchImpl = options.fetchImpl ?? fetch;
  const timeoutMs = options.timeoutMs ?? DEFAULT_CONDO_RECORDS_TIMEOUT_MS;
  const url = `${apiBaseUrl()}/api/v1/properties/${encodeURIComponent(bbl)}/condo-records`;

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
        // Send NO credentials on every condo-records fetch, consistently with
        // the address clients (defense-in-depth: the API has no auth cookies).
        credentials: "omit",
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
          "The city condo records could not be loaded. The property details " +
          "above are unaffected, and this is safe to retry.",
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
    const state = record && typeof record.state === "string" ? record.state : null;
    const pairKey = `${response.status}|${state ?? ""}`;

    if (response.status === 200) {
      if (
        record === null ||
        record.document_kind !== "condo_records" ||
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
      state: state as CondoRecordsErrorState,
      httpStatus: response.status,
      message: boundedText(
        record?.message,
        "The city condo records service reported a failure without further detail.",
      ),
      correlationId,
    };
  } finally {
    clearTimeout(timer);
    externalSignal?.removeEventListener("abort", onExternalAbort);
  }
}

/**
 * Fetch the condo-records channel for a canonical BBL as a hook. Issues ONE
 * bounded fetch per BBL; a superseded/unmounted request is aborted (no retry
 * loop). Returns null while loading and when `bbl` is null (no fetch fires).
 */
export function useCondoRecords(
  bbl: string | null,
  options: CondoRecordsLookupOptions = {},
): CondoRecordsOutcome | null {
  const fetchImpl = options.fetchImpl;
  const [outcome, setOutcome] = useState<CondoRecordsOutcome | null>(null);
  useEffect(() => {
    if (bbl === null) {
      setOutcome(null);
      return;
    }
    const controller = new AbortController();
    let active = true;
    setOutcome(null);
    void fetchCondoRecords(bbl, { fetchImpl, signal: controller.signal }).then(
      (result) => {
        if (active && result.kind !== "aborted") setOutcome(result);
      },
    );
    return () => {
      active = false;
      controller.abort();
    };
  }, [bbl, fetchImpl]);
  return outcome;
}

// --- Derived channel state (the web half of the guard-coherence decision) ----
//
// The architect surface must NOT branch on the raw CondoRecordsOutcome union in
// three places (notice, fail-safe guard, records section) — that is the exact
// incoherence the T045 G3-A2 question warned about. Instead, this ONE pure
// reducer collapses the transport outcome to a small surface vocabulary, and the
// surface (deriveCondoSurface in PropertyOverview) combines it with the accepted
// profile fail-safe guard. Only the resolver's OWN condo outcomes are treated as
// condo signals; a transport failure (network / timeout / HTTP error / route
// absent) is `unavailable`, which NEVER withholds on its own — the enrichment is
// simply missing and the accepted profile/backend fail-safes remain authoritative
// (a condo-records outage must not blank every property's allowances).
export type CondoChannelState =
  | { kind: "idle" } // no BBL yet (no fetch fired)
  | { kind: "loading" } // fetch in flight
  | { kind: "non_condo" } // not a condo lot, or the feature route is absent
  | { kind: "single"; view: CondoRecordsView } // resolved to ONE base lot (allow path)
  | { kind: "multi_lot"; view: CondoRecordsView } // TWO+ base lots (records + withhold)
  | { kind: "unresolved"; view: CondoRecordsView } // condo, no base lot found (withhold)
  | { kind: "resolver_error"; view: CondoRecordsView } // condo, typed resolver error (withhold)
  | { kind: "unavailable"; reason: string }; // transport/route unavailable (no signal)

/**
 * Reduce a raw condo-records channel outcome to the ONE surface state the
 * architect surface consumes. Pure and total; safe to call every render.
 */
export function deriveCondoChannelState(
  outcome: CondoRecordsOutcome | null,
): CondoChannelState {
  if (outcome === null) return { kind: "loading" };
  switch (outcome.kind) {
    case "document": {
      const view = outcome.view;
      switch (view.outcome) {
        case CONDO_OUTCOME_MULTI_LOT:
          return { kind: "multi_lot", view };
        case CONDO_OUTCOME_RESOLVED_SINGLE:
          return { kind: "single", view };
        case CONDO_OUTCOME_UNRESOLVED:
          return { kind: "unresolved", view };
        case CONDO_OUTCOME_ERROR:
          return { kind: "resolver_error", view };
        case CONDO_OUTCOME_NOT_CONDO_BILLING:
          return { kind: "non_condo" };
        default:
          // An unknown 200 outcome token this build does not recognise: fail
          // safe as unavailable (never as a positive success/allow signal).
          return { kind: "unavailable", reason: "unrecognized-outcome" };
      }
    }
    case "route_absent":
      // The feature flag is off / the route is unmounted: behave as non-condo,
      // never as an error — the surface simply shows no records section.
      return { kind: "non_condo" };
    case "error":
    case "network_error":
    case "client_timeout":
    case "unexpected_response":
      return { kind: "unavailable", reason: outcome.kind };
    case "aborted":
      // A superseded/unmounted request; treated as still loading (the hook has
      // already discarded it, so this branch is defensive only).
      return { kind: "loading" };
    default:
      return { kind: "unavailable", reason: "unknown" };
  }
}

/**
 * True when a channel state is a POSITIVELY-confirmed condo fail-safe outcome
 * for which computed development allowances must be withheld: two-or-more base
 * lots, an unresolved condo, or a typed resolver error. A `single` (allow path),
 * `non_condo`, `loading`, `idle`, or `unavailable` state does NOT withhold on
 * its own. This is monotonic with the accepted profile guard: the channel may
 * only ADD withholding, never remove it (records never unlock allowances).
 */
export function channelWithholdsAllowances(state: CondoChannelState): boolean {
  return (
    state.kind === "multi_lot" ||
    state.kind === "unresolved" ||
    state.kind === "resolver_error"
  );
}
