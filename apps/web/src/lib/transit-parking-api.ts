/**
 * Typed client for the internal transit/parking read route (lane C packet W3,
 * plan check C-8 / queue item B-10).
 *
 * Contract: services/api/app/api/v1/transit_parking_read.py (read-only
 * dependency). The route returns ONE lot's transit/parking-ZONE status
 * (transit_parking.schema.json v1 - the serialized
 * resolve_transit_parking_status output in a contract-version envelope) for one
 * BBL, behind the default-off INTERNAL_TRANSIT_PARKING_READ_ENABLED flag. The
 * document carries the PLUTO transit-zone classification VERBATIM, or says the
 * source is "Check needed"; it states NO parking OUTCOME (a number of spaces, a
 * waiver, or an exemption is a rule-engine / legal determination made by Lane A
 * and a qualified reviewer at G6, never here, and the contract has no slot for
 * one).
 *
 * `fetchTransitParking(bbl)` transports and verifies the status. Every 200 body
 * is runtime-validated against the generated contract type BEFORE anything can
 * use it (`validateTransitParkingDocument`); a bad body is a distinct
 * `validation_failure` outcome, never partially trusted. The documented non-200s
 * map to typed outcomes: 404 -> `not_available` (the flag is off / the route is
 * unmounted, the "not connected yet" state), 422 -> `validation_error`, 503 ->
 * `inputs_unavailable`, 500 -> `server_contract_error` / `internal_error`.
 * Browser-level failures are `network_error` / `client_timeout` / `aborted`;
 * anything else is `unexpected_response`. All reflected server text is
 * length-capped.
 *
 * No legal logic and no zoning math live here: this module transports and
 * verifies shape only. It mirrors src/lib/study/study-setup-api.ts.
 */

import { boundedText, boundedToken } from "./bounded";
import {
  Problems,
  checkEnum,
  checkNonEmptyString,
  isNonEmptyString,
  isRecord,
} from "./scenario-contract-checks";
import { apiBaseUrl } from "./api";
import {
  checkArray,
  checkBbl,
  checkDateTime,
  checkKeys,
  checkNoFixtureAnnotation,
  checkNullableNonEmptyString,
  checkObject,
} from "./study/study-checks";
import { SOURCE_KINDS } from "./study/study-vocabulary";
import { checkVersionCheck } from "./study/site-fact-validator";
import type {
  Source,
  TransitParking,
} from "../../../../packages/contracts/generated/transit_parking";

/** Default request budget, below the Playwright timeout so a slow route is
 * provable in CI without configuration (mirrors src/lib/api.ts). */
export const DEFAULT_TIMEOUT_MS = 12_000;

/** The contract-version the client accepts (transit_parking.schema.json v1). */
export const TRANSIT_PARKING_CONTRACT_VERSION = "1.0.0";

const STATUS_VALUES = ["recorded", "check_needed"] as const;
const STATUS_LABELS = ["Recorded", "Check needed"] as const;

/** The closed transit_parking document key set (additionalProperties:false). A
 * body with any other key - a parking-outcome field, say - is refused. */
const DOCUMENT_KEYS = [
  "contract_version",
  "lot_bbl",
  "status",
  "status_label",
  "transit_zone",
  "source",
  "detail",
  "missing_source",
] as const;

const SOURCE_KEYS = [
  "kind",
  "dataset",
  "dataset_version",
  "retrieved_at",
  "query_ref",
  "document_ref",
  "statement",
] as const;

export interface TransitParkingStatusOutcome {
  kind: "status";
  status: TransitParking;
  correlationId: string | null;
}
/** 404: the route is off (flag unset) or unmounted - the "not connected yet" state. */
export interface NotAvailableOutcome {
  kind: "not_available";
}
export interface ValidationErrorOutcome {
  kind: "validation_error";
  code: string;
  message: string;
  correlationId: string | null;
}
/** 503: the server could not produce the status (upstream/no-match/gate off). Retryable. */
export interface InputsUnavailableOutcome {
  kind: "inputs_unavailable";
  message: string;
  correlationId: string | null;
}
/** 500 internal_contract_error: the server refused to ship a status that failed its contract. */
export interface ServerContractErrorOutcome {
  kind: "server_contract_error";
  message: string;
  correlationId: string | null;
}
export interface InternalErrorOutcome {
  kind: "internal_error";
  message: string;
  correlationId: string | null;
}
/** A 200 whose body failed CLIENT-side contract validation. */
export interface ValidationFailureOutcome {
  kind: "validation_failure";
  problems: string[];
  correlationId: string | null;
}
export interface NetworkErrorOutcome {
  kind: "network_error";
  message: string;
}
export interface ClientTimeoutOutcome {
  kind: "client_timeout";
  timeoutMs: number;
}
export interface AbortedOutcome {
  kind: "aborted";
}
export interface UnexpectedResponseOutcome {
  kind: "unexpected_response";
  httpStatus: number;
  receivedState: string | null;
  correlationId: string | null;
}

export type TransitParkingFetchOutcome =
  | TransitParkingStatusOutcome
  | NotAvailableOutcome
  | ValidationErrorOutcome
  | InputsUnavailableOutcome
  | ServerContractErrorOutcome
  | InternalErrorOutcome
  | ValidationFailureOutcome
  | NetworkErrorOutcome
  | ClientTimeoutOutcome
  | AbortedOutcome
  | UnexpectedResponseOutcome;

export interface FetchTransitParkingOptions {
  /** Injection point for tests; defaults to the global fetch. */
  fetchImpl?: typeof fetch;
  signal?: AbortSignal;
  timeoutMs?: number;
}

export type TransitParkingValidation =
  | { ok: true; status: TransitParking }
  | { ok: false; problems: string[] };

/**
 * Validate a source (site_fact.schema.json#/$defs/source) or null. The
 * kind-specific required-field rules (the schema oneOf) are enforced by the JSON
 * Schema on the SERVER, which contract-guards before send; the client checks the
 * shape it consumes (keys, kind, nullable text, retrieved_at).
 */
function checkTransitParkingSource(problems: Problems, path: string, value: unknown): void {
  if (value === null) return;
  const source = checkObject(problems, path, value);
  if (!source) return;
  checkKeys(problems, path, source, SOURCE_KEYS, ["provenance_refs", "version_check"]);
  checkEnum(problems, `${path}.kind`, source.kind, SOURCE_KINDS);
  for (const field of ["dataset", "dataset_version", "query_ref", "document_ref", "statement"]) {
    checkNullableNonEmptyString(problems, `${path}.${field}`, source[field]);
  }
  checkDateTime(problems, `${path}.retrieved_at`, source.retrieved_at);
  if (source.provenance_refs !== undefined) {
    const refs = checkArray(problems, `${path}.provenance_refs`, source.provenance_refs);
    refs?.forEach((ref, index) => {
      checkNonEmptyString(problems, `${path}.provenance_refs[${index}]`, ref);
    });
  }
  // source.version_check (site_fact contract 1.1.0): the same shared $def check.
  if (source.version_check !== undefined) {
    checkVersionCheck(problems, `${path}.version_check`, source.version_check, source.dataset_version);
  }
}

/**
 * Validate a transit/parking document against the contract shape. Mirrors the
 * server's transit_parking.schema.json: the closed key set, the status/label
 * enums, the nullable zone/source/missing_source, and the allOf coherence rule
 * (status, status_label, transit_zone and missing_source move together).
 */
export function validateTransitParkingDocument(body: unknown): TransitParkingValidation {
  const problems = new Problems();
  const doc = checkObject(problems, "transit_parking", body);
  if (!doc) return { ok: false, problems: problems.list };
  checkNoFixtureAnnotation(problems, "transit_parking", doc);
  // Closed shape: required keys present, NO extra key (a parking-outcome field,
  // say, is refused here - the zone only).
  checkKeys(problems, "transit_parking", doc, DOCUMENT_KEYS);

  if (doc.contract_version !== TRANSIT_PARKING_CONTRACT_VERSION) {
    problems.add("contract_version", `must be the string "${TRANSIT_PARKING_CONTRACT_VERSION}"`);
  }
  checkBbl(problems, "lot_bbl", doc.lot_bbl);
  checkEnum(problems, "status", doc.status, STATUS_VALUES);
  checkEnum(problems, "status_label", doc.status_label, STATUS_LABELS);
  checkNullableNonEmptyString(problems, "transit_zone", doc.transit_zone);
  checkNonEmptyString(problems, "detail", doc.detail);
  checkNullableNonEmptyString(problems, "missing_source", doc.missing_source);
  checkTransitParkingSource(problems, "source", doc.source);

  // allOf coherence (the schema oneOf): recorded carries a zone and no missing
  // source; check_needed carries no zone and names the source to check.
  if (doc.status === "recorded") {
    if (doc.status_label !== "Recorded") {
      problems.add("status_label", "a recorded status must be labelled 'Recorded'");
    }
    if (!isNonEmptyString(doc.transit_zone)) {
      problems.add("transit_zone", "a recorded status must carry a transit zone");
    }
    if (doc.missing_source !== null) {
      problems.add("missing_source", "a recorded status must carry no missing source");
    }
  } else if (doc.status === "check_needed") {
    if (doc.status_label !== "Check needed") {
      problems.add("status_label", "a check-needed status must be labelled 'Check needed'");
    }
    if (doc.transit_zone !== null) {
      problems.add("transit_zone", "a check-needed status must carry no transit zone");
    }
    if (!isNonEmptyString(doc.missing_source)) {
      problems.add("missing_source", "a check-needed status must name the source to check");
    }
  }

  if (problems.list.length > 0) return { ok: false, problems: problems.list };
  return { ok: true, status: doc as unknown as TransitParking };
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return isRecord(value) ? value : null;
}

/** Fetch and verify the transit/parking status for one BBL. */
export async function fetchTransitParking(
  bbl: string,
  options: FetchTransitParkingOptions = {},
): Promise<TransitParkingFetchOutcome> {
  const fetchImpl = options.fetchImpl ?? fetch;
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const url = `${apiBaseUrl()}/api/v1/properties/${encodeURIComponent(bbl)}/transit-parking`;

  const controller = new AbortController();
  let timedOut = false;
  const externalSignal = options.signal;
  if (externalSignal?.aborted) return { kind: "aborted" };
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
          "The platform API could not be reached. Nothing was retrieved. This is safe to retry.",
      };
    }

    const correlationId = boundedToken(response.headers.get("X-Correlation-ID"));

    // A 404 is the disabled / unmounted sentinel: it carries no JSON state, so
    // classify it by status alone (the "not connected yet" state).
    if (response.status === 404) return { kind: "not_available" };

    let body: unknown = null;
    try {
      body = await response.json();
    } catch {
      if (timedOut) return { kind: "client_timeout", timeoutMs };
      if (controller.signal.aborted || externalSignal?.aborted) return { kind: "aborted" };
      return { kind: "unexpected_response", httpStatus: response.status, receivedState: null, correlationId };
    }
    const record = asRecord(body);
    const state = record && typeof record.state === "string" ? record.state : null;

    if (response.status === 200 && state === null) {
      const validation = validateTransitParkingDocument(body);
      if (!validation.ok) {
        return {
          kind: "validation_failure",
          problems: validation.problems.map((problem) => boundedText(problem, "problem detail unavailable")),
          correlationId,
        };
      }
      return { kind: "status", status: validation.status, correlationId };
    }

    if (response.status === 422 && state === "validation_error") {
      const detail = asRecord(record?.detail);
      return {
        kind: "validation_error",
        code: boundedToken(detail?.code, 48) ?? "unknown",
        message: boundedText(record?.message, "The BBL was rejected by the API."),
        correlationId,
      };
    }
    if (response.status === 503 && state === "inputs_unavailable") {
      return {
        kind: "inputs_unavailable",
        message: boundedText(record?.message, "The transit/parking status is not available right now."),
        correlationId,
      };
    }
    if (response.status === 500 && state === "internal_contract_error") {
      return {
        kind: "server_contract_error",
        message: boundedText(record?.message, "The server refused to deliver a status that failed its contract."),
        correlationId,
      };
    }
    if (response.status === 500 && state === "internal_error") {
      return {
        kind: "internal_error",
        message: boundedText(record?.message, "Unexpected internal error."),
        correlationId,
      };
    }

    // Any other (status, state) pair is outside the documented matrix.
    return {
      kind: "unexpected_response",
      httpStatus: response.status,
      receivedState: state === null ? null : boundedToken(state, 48),
      correlationId,
    };
  } finally {
    clearTimeout(timer);
    externalSignal?.removeEventListener("abort", onExternalAbort);
  }
}

export type { Source as TransitParkingSource, TransitParking };
