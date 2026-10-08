"use client";

/**
 * The results panel (task M5-T140, Part B of the R6B results connection). The first screen that
 * shows the results. It offers the design choices and the optional statement (ResultsForm), asks
 * the server ONLY when the user presses the button (ruling R2), shows the state, then renders the
 * returned results document through the EXISTING three-answers cards (ThreeAnswersPanel) — each
 * result settled, conditional or withheld, every answer and every failure in its plain state.
 *
 * It holds NO copy of a server value (ruling R3): no starting height, no result, no reason text.
 * It prints what the returned document carries. It adds NO second standing-review label (ruling
 * R8): the dashboard renders the one copy. A newer request aborts an older one and an older answer
 * is never shown after a newer one (ruling R2; scenario S22).
 */

import { useCallback, useRef, useState } from "react";
import { fetchResults, type ResultsFetchOutcome, type ResultsRequestBody } from "@/lib/results-api";
import { ThreeAnswersPanel } from "./answers/ThreeAnswersPanel";
import {
  ResultsForm,
  HEIGHT_REFUSED_MESSAGE,
  type ResultsFormValues,
} from "./ResultsForm";
import { FailureNoticeCard } from "./workspace/DashboardFailureNotice";
import { referenceRow, type DashboardFailureNoticeModel } from "./workspace/dashboard-failure";
import "./results-panel.css";

const RETRY_SAFE = "The property you entered is fine. Trying again is safe.";
const NEEDS_PLATFORM =
  "This needs the platform team. Trying again will likely give the same result until it is fixed.";

/** R7 (D-090-R548, DB-180): shown whenever a result is shown. */
export const PARKING_LINE =
  "Parking, loading and bicycle requirements are not yet checked for this option. It is not shown as feasible.";

/** R3: shown when an input changed since the shown result was asked for. */
export const STALE_INPUTS_LINE =
  "You changed an input. These results are for the earlier inputs. Press Show results to update.";

const INITIAL_VALUES: ResultsFormValues = {
  program: "standard_residence",
  heightText: "",
  densityStatement: false,
};

type HeightParse =
  | { kind: "absent" }
  | { kind: "present"; value: number }
  | { kind: "invalid" };

/** Parse the raw height field. Presence is tested with `=== ""`, never a truthiness test, so a
 * height of 0 is a REFUSED value (invalid), not "no height" (ruling R4; DB-204(c): no upper
 * limit). */
function parseHeight(text: string): HeightParse {
  const trimmed = text.trim();
  if (trimmed === "") return { kind: "absent" };
  const value = Number(trimmed);
  if (!Number.isFinite(value) || value <= 0) return { kind: "invalid" };
  return { kind: "present", value };
}

/** Build the option body from the form, or report the field message for a refused height. The
 * height is sent only when present; the statement only when made (`=== true`). */
function buildRequest(
  values: ResultsFormValues,
): { ok: true; body: ResultsRequestBody } | { ok: false; heightError: string } {
  const height = parseHeight(values.heightText);
  if (height.kind === "invalid") return { ok: false, heightError: HEIGHT_REFUSED_MESSAGE };
  const body: ResultsRequestBody = { housing_program: values.program };
  if (height.kind === "present") body.floor_to_floor_ft = height.value;
  if (values.densityStatement === true) body.special_density_statement = true;
  return { ok: true, body };
}

function sameInputs(a: ResultsFormValues, b: ResultsFormValues): boolean {
  return (
    a.program === b.program &&
    a.heightText === b.heightText &&
    a.densityStatement === b.densityStatement
  );
}

/** The §5a failure notice for a non-success, non-404 outcome. 404 (not_available) is the plain
 * "not connected yet" card; `success` and `aborted` own no notice. No stack or path is shown; the
 * correlation id and HTTP status sit behind the card's Technical details disclosure. */
export function resultsFailureNotice(
  outcome: ResultsFetchOutcome,
): DashboardFailureNoticeModel | null {
  switch (outcome.kind) {
    case "success":
    case "not_available":
    case "aborted":
      return null;
    case "validation_error":
      return {
        title: "The request could not be understood",
        body: outcome.message,
        recovery: "Check the form and try again.",
        retryable: false,
        technical: [
          { label: "Rejection code", value: outcome.code },
          ...(outcome.field ? [{ label: "Field", value: outcome.field }] : []),
          ...referenceRow(outcome.correlationId),
        ],
      };
    case "rate_limited":
      return {
        title: "Too many requests",
        body: "The results were requested too many times in a short while, so this request was held back.",
        recovery: "Try again shortly.",
        retryable: true,
        technical: referenceRow(outcome.correlationId),
      };
    case "inputs_unavailable":
      return {
        title: "The results could not be loaded right now",
        body: outcome.message,
        recovery: "The official source did not return the inputs yet. Trying again is safe.",
        retryable: true,
        technical: referenceRow(outcome.correlationId),
      };
    case "lot_conditions_unconfirmed":
      // The same request would not succeed on a retry: show the server's plain reason and do NOT
      // label it safe to retry (ruling / matrix note).
      return {
        title: "The results are not available for this lot",
        body: outcome.message,
        recovery: "A recorded fact needed to work out this lot's results could not be read.",
        retryable: false,
        technical: referenceRow(outcome.correlationId),
      };
    case "internal_error":
    case "internal_contract_error":
      return {
        title: "Something went wrong",
        body: "The app hit an unexpected problem while loading the results. Nothing was shown.",
        recovery: outcome.kind === "internal_contract_error" ? NEEDS_PLATFORM : RETRY_SAFE,
        retryable: true,
        technical: referenceRow(outcome.correlationId),
      };
    case "validation_failure":
      return {
        title: "The results could not be loaded",
        body: "The service returned data that failed this screen's format check. Nothing from that response is shown.",
        recovery: NEEDS_PLATFORM,
        retryable: true,
        technical: outcome.problems.map(problem => ({ label: "Format problem", value: problem })).concat(
          referenceRow(outcome.correlationId),
        ),
      };
    case "network_error":
      return {
        title: "Could not reach the server",
        body: outcome.message,
        recovery: RETRY_SAFE,
        retryable: true,
        technical: [],
      };
    case "client_timeout":
      return {
        title: "The results took too long",
        body: `The server did not answer within ${Math.round(outcome.timeoutMs / 1000)} seconds, so the request was cancelled. No partial results are shown.`,
        recovery: RETRY_SAFE,
        retryable: true,
        technical: [],
      };
    case "unexpected_response":
      return {
        title: "Unexpected response from the server",
        body: "The server answered in a way the app does not recognize, so the response was not trusted or shown.",
        recovery: RETRY_SAFE,
        retryable: true,
        technical: [
          { label: "HTTP status", value: String(outcome.httpStatus) },
          ...referenceRow(outcome.correlationId),
        ],
      };
  }
}

function LoadingCard() {
  return (
    <section className="card architect-empty" role="status" aria-busy="true" data-testid="results-loading">
      <p className="architect-eyebrow">Development results</p>
      <p>Working out the results for this property…</p>
    </section>
  );
}

function NotConnectedCard() {
  return (
    <section className="card architect-empty" data-testid="results-unavailable">
      <p className="architect-eyebrow">Development results</p>
      <h2>Results are not connected yet</h2>
      <p>The results service is not switched on for this build. No results were requested or shown.</p>
    </section>
  );
}

export interface ResultsPanelProps {
  bbl: string;
  /** Injection point for tests; defaults to the global fetch (the live path). */
  fetchImpl?: typeof fetch;
}

export function ResultsPanel({ bbl, fetchImpl }: ResultsPanelProps) {
  const [values, setValues] = useState<ResultsFormValues>(INITIAL_VALUES);
  const [heightError, setHeightError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [outcome, setOutcome] = useState<ResultsFetchOutcome | null>(null);
  const [askedWith, setAskedWith] = useState<ResultsFormValues | null>(null);
  const requestId = useRef(0);
  const controllerRef = useRef<AbortController | null>(null);

  const submit = useCallback(() => {
    const request = buildRequest(values);
    if (!request.ok) {
      setHeightError(request.heightError);
      return;
    }
    setHeightError(null);
    // Newer wins (ruling R2, S22): abort any in-flight request and ignore any older answer.
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    requestId.current += 1;
    const id = requestId.current;
    const asked = values;
    setBusy(true);
    void (async () => {
      const result = await fetchResults(bbl, request.body, { fetchImpl, signal: controller.signal });
      if (id !== requestId.current) return; // a newer request has replaced this one
      setOutcome(result);
      setAskedWith(asked);
      setBusy(false);
    })();
  }, [bbl, fetchImpl, values]);

  const onChange = useCallback((next: ResultsFormValues) => {
    setValues(next);
    // Clear a stale field message as soon as the field changes; the request is not re-sent.
    setHeightError(previous => (previous === null ? previous : null));
  }, []);

  const showingDocument = !busy && outcome?.kind === "success";
  const stale = showingDocument && askedWith !== null && !sameInputs(values, askedWith);
  const failure = !busy && outcome !== null ? resultsFailureNotice(outcome) : null;

  return (
    <section className="results-panel" aria-label="Development results" data-testid="results-panel">
      <ResultsForm
        values={values}
        onChange={onChange}
        onSubmit={submit}
        busy={busy}
        heightError={heightError}
      />

      {stale ? (
        <p className="results-stale section-note" role="status" data-testid="results-stale">
          {STALE_INPUTS_LINE}
        </p>
      ) : null}

      {busy ? <LoadingCard /> : null}

      {!busy && outcome?.kind === "not_available" ? <NotConnectedCard /> : null}

      {failure ? (
        <FailureNoticeCard model={failure} onRetry={submit} testId="results-failure" focusTitle />
      ) : null}

      {showingDocument && outcome.kind === "success" ? (
        <div className="results-document" data-testid="results-document">
          <p className="results-parking section-note" data-testid="results-parking">
            {PARKING_LINE}
          </p>
          <ThreeAnswersPanel results={outcome.document} showDraftValues />
        </div>
      ) : null}
    </section>
  );
}
