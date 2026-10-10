/**
 * Typed client for the program's report route (task M5-T153; ruling X9 d). The report route
 * M5-T151 serves `POST /api/v1/properties/{bbl}/report` with the SAME request body and the same
 * gating as the results route, answering `text/html; charset=utf-8` — the whole report as one
 * standalone document that carries no script. This module transports and classifies the response;
 * it holds no copy of a server value and decides no law (ruling X7).
 *
 * The real route arrives with M5-T151; until then this client is exercised with a stubbed
 * `fetchImpl` whose shape matches the real route (a 200 `text/html` body carrying the HTML string).
 *
 * The caller sends the SAME body the results form sends (`ResultsRequestBody`): the housing
 * program, an optional floor-to-floor height, an optional special-density statement.
 *
 * Outcomes, each mapped to ONE plain user state (no status code, no route, no field name reaches
 * the screen — ruling X6, scenario S4):
 *  - success:        a 200 `text/html` body → the report HTML.
 *  - not_available:  the route is not mounted/enabled yet (404) — "the report is not available yet".
 *  - refused:        the route declined to build the report for this lot/input (the gating), with
 *                    the server's own plain message.
 *  - error:          a transport failure, a timeout, or any response the client does not recognise.
 *  - aborted:        a newer request replaced this one.
 */

import { apiBaseUrl } from "./api";
import { boundedText } from "./bounded";
import { isRecord } from "./scenario-contract-checks";
import type { ResultsRequestBody } from "./results-api";

/** The report request body is the SAME shape the results form sends (ruling X9 d). */
export type ReportRequestBody = ResultsRequestBody;

/** Default request budget, below the Playwright timeout so a slow route is provable in CI without
 * configuration (mirrors results-api.ts). The report is larger than the results JSON, so this is a
 * touch more generous. */
export const DEFAULT_REPORT_TIMEOUT_MS = 20_000;

export interface ReportSuccessOutcome {
  kind: "success";
  html: string;
}
/** The route is off (flag unset) or not mounted yet — the report is not available. */
export interface ReportNotAvailableOutcome {
  kind: "not_available";
}
/** The route declined to build the report for this lot/input (the gating). Carries the server's
 * own plain message; never a status code or a field name. */
export interface ReportRefusedOutcome {
  kind: "refused";
  message: string;
}
/** A transport failure, a timeout, or any response the client does not recognise. */
export interface ReportErrorOutcome {
  kind: "error";
}
export interface ReportAbortedOutcome {
  kind: "aborted";
}

export type ReportFetchOutcome =
  | ReportSuccessOutcome
  | ReportNotAvailableOutcome
  | ReportRefusedOutcome
  | ReportErrorOutcome
  | ReportAbortedOutcome;

export interface FetchReportOptions {
  /** Injection point for tests; defaults to the global fetch (the live path). */
  fetchImpl?: typeof fetch;
  signal?: AbortSignal;
  timeoutMs?: number;
}

/** The plain message shown when the gating declines the report but sends no message of its own. */
const DEFAULT_REFUSED_MESSAGE = "The report could not be prepared for this property right now.";

function isHtml(response: Response): boolean {
  const type = response.headers.get("Content-Type") ?? "";
  return type.toLowerCase().includes("text/html");
}

/** POST the body for one BBL and classify the report response. */
export async function fetchReport(
  bbl: string,
  body: ReportRequestBody,
  options: FetchReportOptions = {},
): Promise<ReportFetchOutcome> {
  const fetchImpl = options.fetchImpl ?? fetch;
  const timeoutMs = options.timeoutMs ?? DEFAULT_REPORT_TIMEOUT_MS;
  const url = `${apiBaseUrl()}/api/v1/properties/${encodeURIComponent(bbl)}/report`;

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
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "text/html" },
        body: JSON.stringify(body),
        cache: "no-store",
        signal: controller.signal,
      });
    } catch {
      if (timedOut) return { kind: "error" };
      if (controller.signal.aborted || externalSignal?.aborted) return { kind: "aborted" };
      return { kind: "error" };
    }

    // A 404 is the disabled / unmounted sentinel: the report is not available yet.
    if (response.status === 404) return { kind: "not_available" };

    if (response.status === 200 && isHtml(response)) {
      let html: string;
      try {
        html = await response.text();
      } catch {
        return { kind: "error" };
      }
      if (html.trim() === "") return { kind: "error" };
      return { kind: "success", html };
    }

    // A documented gating refusal (the same gating as the results route): read the server's plain
    // message if it sent JSON; never surface a status code or a field name.
    if (response.status === 409 || response.status === 422 || response.status === 503) {
      let message = DEFAULT_REFUSED_MESSAGE;
      try {
        const payload: unknown = await response.json();
        if (isRecord(payload) && typeof payload.message === "string") {
          message = boundedText(payload.message, DEFAULT_REFUSED_MESSAGE);
        }
      } catch {
        // Keep the default plain message; the refusal state still holds.
      }
      return { kind: "refused", message };
    }

    // Anything else (an unexpected status, or a 200 that was not HTML) is a plain error.
    return { kind: "error" };
  } finally {
    clearTimeout(timer);
    externalSignal?.removeEventListener("abort", onExternalAbort);
  }
}
