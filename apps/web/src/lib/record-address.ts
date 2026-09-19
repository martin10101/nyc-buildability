"use client";

/**
 * HARDENED typed client + hook for GET /api/v1/properties/{bbl}/record-address
 * (task M5-T047, DB-032).
 *
 * Contract: services/api/app/api/v1/lot_geometry.py (the additive sibling
 * endpoint — read-only dependency). Same discipline as src/lib/lot-geometry-api.ts:
 *
 *   1. The (HTTP status, state) pair set below mirrors the route's
 *      RECORD_ADDRESS_STATUS_STATE_MATRIX; any pair outside it renders as the
 *      distinct `unexpected_response` outcome. A body is never routed by `state`
 *      alone.
 *   2. A 200 body must carry document_kind "record_address" and a recognized
 *      `outcome`; the reflected address is bounded (boundedText) BEFORE it may
 *      render. Branching stays on the RAW `outcome` string.
 *   3. The generic 404 {"detail":"Not Found"} (flag off / route unmounted) is a
 *      first-class `route_absent` outcome — never an error, never a crash.
 *   4. Requests are cancellable and time-bounded (aborted / client_timeout).
 *
 * RECORD, NOT MEASUREMENT: this module transports an official RECORD (the lot's
 * PLUTO address-of-record) for DISPLAY. It derives no value; the confirm card
 * shows the record only when it differs from the city-matched frontage
 * (recordAddressDiffersFromMatched), honestly nothing otherwise (D-073-R006).
 */

import { useEffect, useState } from "react";
import { apiBaseUrl } from "./api";
import { boundedText, boundedToken } from "./bounded";

export const DEFAULT_RECORD_ADDRESS_TIMEOUT_MS = 12_000;

/** The route's documented typed error states, verbatim from
 * RECORD_ADDRESS_STATUS_STATE_MATRIX. The three honest outcomes are 200
 * documents and are NOT error states. */
export const RECORD_ADDRESS_ERROR_STATES = [
  "validation_error",
  "rate_limited",
  "source_unavailable",
  "schema_drift",
  "timeout",
  "internal_error",
] as const;
export type RecordAddressErrorState =
  (typeof RECORD_ADDRESS_ERROR_STATES)[number];

/** The documented (HTTP status, state) pairs, mirrored from the route. "200|"
 * and "404|" carry NO `state` (the document discriminates on `outcome`; the 404
 * is the generic flag-off / unmounted sentinel). */
const DOCUMENTED_PAIRS: ReadonlySet<string> = new Set([
  "200|",
  "404|",
  "422|validation_error",
  "429|rate_limited",
  "502|source_unavailable",
  "502|schema_drift",
  "504|timeout",
  "500|internal_error",
]);

export const RECORD_ADDRESS_OUTCOMES = [
  "address_of_record",
  "no_address_of_record",
  "no_record",
] as const;
export type RecordAddressChannelOutcome =
  (typeof RECORD_ADDRESS_OUTCOMES)[number];

export interface RecordAddressSourceView {
  sourceId: string | null;
  datasetId: string | null;
  datasetVersion: string | null;
  retrievedAt: string | null;
}

/** Bounded display view of a 200 record_address document. */
export interface RecordAddressView {
  /** RAW outcome string for branching. */
  outcome: RecordAddressChannelOutcome;
  /** The verbatim PLUTO address-of-record, bounded for display; null on every
   * non-address_of_record outcome (and, defensively, on an address_of_record
   * whose value did not survive bounding). */
  address: string | null;
  source: RecordAddressSourceView;
}

export interface RecordAddressDocumentOutcome {
  kind: "document";
  view: RecordAddressView;
  correlationId: string | null;
}

/** Generic 404 {"detail":"Not Found"}: the feature is flag-gated off or the
 * route is unmounted. Benign — the confirm card simply shows no record line. */
export interface RecordAddressRouteAbsentOutcome {
  kind: "route_absent";
  httpStatus: number;
}

export interface RecordAddressErrorOutcome {
  kind: "error";
  state: RecordAddressErrorState;
  httpStatus: number;
  message: string;
  correlationId: string | null;
}

export interface RecordAddressNetworkErrorOutcome {
  kind: "network_error";
  message: string;
}

export interface RecordAddressClientTimeoutOutcome {
  kind: "client_timeout";
  timeoutMs: number;
}

export interface RecordAddressAbortedOutcome {
  kind: "aborted";
}

export interface RecordAddressUnexpectedResponseOutcome {
  kind: "unexpected_response";
  httpStatus: number;
  receivedState: string | null;
  correlationId: string | null;
}

export type RecordAddressOutcome =
  | RecordAddressDocumentOutcome
  | RecordAddressRouteAbsentOutcome
  | RecordAddressErrorOutcome
  | RecordAddressNetworkErrorOutcome
  | RecordAddressClientTimeoutOutcome
  | RecordAddressAbortedOutcome
  | RecordAddressUnexpectedResponseOutcome;

export interface RecordAddressLookupOptions {
  fetchImpl?: typeof fetch;
  signal?: AbortSignal;
  timeoutMs?: number;
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

function isKnownOutcome(value: unknown): value is RecordAddressChannelOutcome {
  return (
    typeof value === "string" &&
    (RECORD_ADDRESS_OUTCOMES as readonly string[]).includes(value)
  );
}

function documentView(record: Record<string, unknown>): RecordAddressView {
  const source = asRecord(record.source) ?? {};
  // The address is a reflected server string: bound it, and treat a
  // blank/dropped result as an explicit absence (never an empty line).
  const boundedAddress =
    typeof record.address === "string" ? boundedText(record.address, "") : "";
  return {
    outcome: record.outcome as RecordAddressChannelOutcome,
    address: boundedAddress === "" ? null : boundedAddress,
    source: {
      sourceId: boundedToken(source.source_id, 64),
      datasetId: boundedToken(source.dataset_id, 64),
      datasetVersion: boundedToken(source.dataset_version, 32),
      retrievedAt: boundedToken(source.retrieved_at, 40),
    },
  };
}

/**
 * Fetch the PLUTO address-of-record for one canonical BBL. The caller must
 * already have decided the surface is enabled (it is only rendered behind the
 * same server-read flag as the whole address confirm tree); this function
 * issues exactly ONE bounded fetch per invocation.
 */
export async function fetchRecordAddress(
  bbl: string,
  options: RecordAddressLookupOptions = {},
): Promise<RecordAddressOutcome> {
  const fetchImpl = options.fetchImpl ?? fetch;
  const timeoutMs = options.timeoutMs ?? DEFAULT_RECORD_ADDRESS_TIMEOUT_MS;
  const url = `${apiBaseUrl()}/api/v1/properties/${encodeURIComponent(bbl)}/record-address`;

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
        // DB-033 rider i: send NO credentials on every record-address fetch,
        // consistently with the address-search client (defense-in-depth: the API
        // has no auth cookies, and an explicit omit removes any ambient-credential
        // ambiguity across the address clients).
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
          "The city-record address could not be loaded. The address details " +
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
        record.document_kind !== "record_address" ||
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
      state: state as RecordAddressErrorState,
      httpStatus: response.status,
      message: boundedText(
        record?.message,
        "The city-record address service reported a failure without further detail.",
      ),
      correlationId,
    };
  } finally {
    clearTimeout(timer);
    externalSignal?.removeEventListener("abort", onExternalAbort);
  }
}

/** Normalize a full address string for the differ comparison: control chars and
 * runs of whitespace collapse to single spaces, trimmed, upper-cased. Deliberately
 * narrow (no abbreviation expansion or ordinal folding) — both the record address
 * and the matched frontage are already city-canonical strings. */
export function normalizeAddressForCompare(value: string): string {
  return value
    .replace(/[\r\n\t]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .toUpperCase();
}

/** True when a resolved record address is present AND differs from the
 * city-matched address (both normalized). The confirm card renders the labeled
 * city-record line ONLY when this is true; an equal record (same address) or an
 * absent one is an honest no-line. */
export function recordAddressDiffersFromMatched(
  recordAddress: string | null,
  matchedAddress: string,
): boolean {
  if (recordAddress === null) return false;
  const record = normalizeAddressForCompare(recordAddress);
  if (record === "") return false;
  return record !== normalizeAddressForCompare(matchedAddress);
}

/**
 * Fetch the record-address channel for a canonical BBL as a hook. Issues ONE
 * bounded fetch per BBL; a superseded/unmounted request is aborted (no retry
 * loop). Returns null while loading and when `bbl` is null (no fetch fires).
 */
export function useRecordAddress(
  bbl: string | null,
  options: RecordAddressLookupOptions = {},
): RecordAddressOutcome | null {
  const fetchImpl = options.fetchImpl;
  const [outcome, setOutcome] = useState<RecordAddressOutcome | null>(null);
  useEffect(() => {
    if (bbl === null) {
      setOutcome(null);
      return;
    }
    const controller = new AbortController();
    let active = true;
    setOutcome(null);
    void fetchRecordAddress(bbl, { fetchImpl, signal: controller.signal }).then(
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
