/**
 * Typed client + store adapter for the internal study-read route (lane C,
 * request D-1 slice 1).
 *
 * Contract: services/api/app/api/v1/study_read.py (read-only dependency). The
 * route returns the lot-choice + site-facts SETUP half of a study
 * (study.schema.json property/lots/lot_selection/site) for one confirmed BBL,
 * behind the default-off INTERNAL_STUDY_READ_ENABLED flag.
 *
 * Two pieces:
 *
 * - `fetchStudySetup(bbl)`: transports and verifies the setup. Every 200 body is
 *   runtime-validated against the generated contract types BEFORE anything can
 *   use it (`validateStudySetupDocument`); a bad body is a distinct
 *   `validation_failure` outcome, never partially trusted. The documented
 *   non-200s map to typed outcomes: 404 -> `not_available` (the flag is off /
 *   the route is unmounted, the "not connected yet" state), 422 ->
 *   `validation_error`, 503 -> `inputs_unavailable`, 500 ->
 *   `server_contract_error` / `internal_error`. Browser-level failures are
 *   `network_error` / `client_timeout` / `aborted`; anything else is
 *   `unexpected_response`. All reflected server text is length-capped.
 *
 * - `ensureStudyFromSetup(store, setup, options)`: `ensure`s the C-05 study
 *   store (one shared study per property) from the fetched setup PLUS the
 *   architect's confirmed option inputs, which the CALLER supplies. It NEVER
 *   invents a study and NEVER guesses numbers: the facts and lot choice are the
 *   server's, and the option inputs are the caller's (the plan forbids inventing
 *   option inputs - study-operations.ts). The full study is validated by the
 *   store's `createStudyEntry` before it is committed; an invalid composition
 *   changes nothing and surfaces as a `StudyFailure`.
 *
 * No legal logic and no zoning math live here: this module transports, verifies
 * shape, and hands the verified pieces to the store.
 */

import { boundedText, boundedToken } from "../bounded";
import { Problems, checkBoolean, checkEnum, isRecord } from "../scenario-contract-checks";
import { apiBaseUrl } from "../api";
import {
  checkArray,
  checkBbl,
  checkNoFixtureAnnotation,
  checkNullableNonEmptyString,
  checkObject,
  isJsonNumber,
} from "./study-checks";
import { checkMeasurement, checkSiteFact } from "./site-fact-validator";
import { createStudyEntry, type NewOption } from "./study-operations";
import type { StudyResult } from "./study-entry";
import type { StudyStore } from "./study-store";
import {
  COMBINATION_STATUSES,
  LOT_SELECTION_MODES,
  LOT_SELECTION_STATEMENT,
  type Lot,
  type LotSelection,
  type SiteFact,
  type StudyProperty,
} from "./study-vocabulary";

/** Default request budget, below the Playwright timeout so a slow route is
 * provable in CI without configuration (mirrors src/lib/api.ts). */
export const DEFAULT_TIMEOUT_MS = 12_000;

/** The verified study setup: the real, server-produced half of a study. */
export interface StudySetup {
  readonly property: StudyProperty;
  readonly lots: Lot[];
  /** mode + combination; the exact statement is re-applied by the store. */
  readonly lotSelection: Pick<LotSelection, "mode" | "combination">;
  readonly siteFacts: SiteFact[];
}

export interface StudySetupOutcome {
  kind: "setup";
  setup: StudySetup;
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
/** 503: the server could not produce the inputs (upstream/gate/deferred). Retryable. */
export interface InputsUnavailableOutcome {
  kind: "inputs_unavailable";
  message: string;
  correlationId: string | null;
}
/** 500 internal_contract_error: the server refused to ship a setup that failed its contract. */
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

export type StudySetupFetchOutcome =
  | StudySetupOutcome
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

export interface FetchStudySetupOptions {
  /** Injection point for tests; defaults to the global fetch. */
  fetchImpl?: typeof fetch;
  signal?: AbortSignal;
  timeoutMs?: number;
}

export type StudySetupValidation =
  | { ok: true; setup: StudySetup }
  | { ok: false; problems: string[] };

/**
 * Validate a study-setup document against the contract shape. The option half of
 * a study is NOT part of this document (study_read.py), so only
 * property/lots/lot_selection/site.facts are checked here; the store validates
 * the full study when the option is composed in.
 */
export function validateStudySetupDocument(body: unknown): StudySetupValidation {
  const problems = new Problems();
  const doc = checkObject(problems, "study_setup", body);
  if (!doc) return { ok: false, problems: problems.list };
  checkNoFixtureAnnotation(problems, "study_setup", doc);

  // property
  const property = checkObject(problems, "property", doc.property);
  if (property) {
    checkBbl(problems, "property.bbl", property.bbl);
    checkNullableNonEmptyString(problems, "property.address", property.address);
  }

  // lots (>= 1), each a contract lot (the oneOf: positive size + known rank, or null + unknown).
  const lots = checkArray(problems, "lots", doc.lots, 1);
  lots?.forEach((item, index) => {
    const path = `lots[${index}]`;
    const lot = checkObject(problems, path, item);
    if (!lot) return;
    checkBbl(problems, `${path}.bbl`, lot.bbl);
    checkBoolean(problems, `${path}.selected`, lot.selected);
    const rank = checkMeasurement(problems, `${path}.size_measurement`, lot.size_measurement);
    const area = lot.approximate_lot_area_sq_ft;
    if (area === null) {
      if (rank !== null && rank !== "unknown") {
        problems.add(`${path}.size_measurement`, "an unknown lot size must carry rank 'unknown'");
      }
    } else if (!(isJsonNumber(area) && area > 0)) {
      problems.add(`${path}.approximate_lot_area_sq_ft`, "must be a number > 0, or null (never 0)");
    } else if (rank === "unknown") {
      problems.add(`${path}.size_measurement`, "a known lot size needs a known rank");
    }
  });

  // lot_selection (mode + exact statement + combination oneOf).
  const selection = checkObject(problems, "lot_selection", doc.lot_selection);
  if (selection) {
    checkEnum(problems, "lot_selection.mode", selection.mode, LOT_SELECTION_MODES);
    if (selection.statement !== LOT_SELECTION_STATEMENT) {
      problems.add("lot_selection.statement", "must be the exact lot-selection statement");
    }
    const combination = checkObject(problems, "lot_selection.combination", selection.combination);
    if (combination) {
      checkEnum(problems, "lot_selection.combination.status", combination.status, COMBINATION_STATUSES);
      checkNullableNonEmptyString(problems, "lot_selection.combination.reason", combination.reason);
      if (combination.status === "not_offered" && combination.reason === null) {
        problems.add("lot_selection.combination.reason", "a not-offered combination must state the reason");
      }
      if ((combination.status === "single_lot" || combination.status === "offered") && combination.reason !== null) {
        problems.add("lot_selection.combination.reason", "must be null unless the combination is not offered");
      }
    }
  }

  // site.facts (each a full site_fact document).
  const site = checkObject(problems, "site", doc.site);
  if (site) {
    const facts = checkArray(problems, "site.facts", site.facts);
    facts?.forEach((fact, index) => checkSiteFact(problems, `site.facts[${index}]`, fact));
  }

  if (problems.list.length > 0) return { ok: false, problems: problems.list };
  const typed = doc as unknown as {
    property: StudyProperty;
    lots: Lot[];
    lot_selection: StudySetup["lotSelection"];
    site: { facts: SiteFact[] };
  };
  return {
    ok: true,
    setup: {
      property: typed.property,
      lots: typed.lots,
      lotSelection: typed.lot_selection,
      siteFacts: typed.site.facts,
    },
  };
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return isRecord(value) ? value : null;
}

/** Fetch and verify the study setup for one BBL. */
export async function fetchStudySetup(
  bbl: string,
  options: FetchStudySetupOptions = {},
): Promise<StudySetupFetchOutcome> {
  const fetchImpl = options.fetchImpl ?? fetch;
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const url = `${apiBaseUrl()}/api/v1/properties/${encodeURIComponent(bbl)}/study`;

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
      const validation = validateStudySetupDocument(body);
      if (!validation.ok) {
        return {
          kind: "validation_failure",
          problems: validation.problems.map((problem) => boundedText(problem, "problem detail unavailable")),
          correlationId,
        };
      }
      return { kind: "setup", setup: validation.setup, correlationId };
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
        message: boundedText(record?.message, "The study setup is not available right now."),
        correlationId,
      };
    }
    if (response.status === 500 && state === "internal_contract_error") {
      return {
        kind: "server_contract_error",
        message: boundedText(record?.message, "The server refused to deliver a setup that failed its contract."),
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

export interface EnsureStudyOptions {
  /** Stable study id for the new study (one per property). */
  studyId: string;
  /** The architect's confirmed option inputs - NEVER invented here. */
  initialOption: NewOption;
  /** RFC 3339 time of the change (the new revision's created_at). */
  at: string;
  /** Overrides the setup's address (the confirmed address), when supplied. */
  address?: string | null;
}

/**
 * `ensure` the shared study store from a fetched setup plus the caller's
 * confirmed option. `ensure` creates the study only when the property has none
 * yet, so a second surface reads the first one's study. The store validates the
 * composed study against the contract before committing; an invalid composition
 * returns a `StudyFailure` and changes nothing.
 */
export function ensureStudyFromSetup(
  store: StudyStore,
  setup: StudySetup,
  options: EnsureStudyOptions,
): StudyResult {
  const bbl = setup.property.bbl;
  return store.ensure(bbl, () =>
    createStudyEntry({
      studyId: options.studyId,
      property: {
        bbl,
        address: options.address !== undefined ? options.address : setup.property.address,
      },
      lots: setup.lots,
      lotSelection: setup.lotSelection,
      siteFacts: setup.siteFacts,
      initialOption: options.initialOption,
      at: options.at,
    }),
  );
}
