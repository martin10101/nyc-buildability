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

import { useCallback, useEffect, useRef, useState } from "react";
import { fetchResults, type ResultsFetchOutcome, type ResultsRequestBody } from "@/lib/results-api";
import { resultIdentity } from "@/lib/architect/result-identity";
import type { Results } from "@/lib/architect/three-answers";
import { OutcomeAnnouncer } from "@/components/property/OutcomeAnnouncer";
import { ThreeAnswersPanel } from "./answers/ThreeAnswersPanel";
import {
  ResultsForm,
  HEIGHT_REFUSED_MESSAGE,
  type ResultsFormValues,
} from "./ResultsForm";
import { FailureNoticeCard } from "./workspace/DashboardFailureNotice";
import { referenceRow, type DashboardFailureNoticeModel } from "./workspace/dashboard-failure";
import { ReportPreview } from "./report/ReportPreview";
import "./results-panel.css";

const RETRY_SAFE = "The property you entered is fine. Trying again is safe.";
const NEEDS_PLATFORM =
  "This needs the platform team. Trying again will likely give the same result until it is fixed.";

/** R3: shown when an input changed since the shown result was asked for. */
export const STALE_INPUTS_LINE =
  "You changed an input. These results are for the earlier inputs. Press Show results to update.";

/** The ONE title of the 404 "not connected yet" card, reused by the card and by the
 * screen-reader announcement so the two can never drift (walkthrough F2). */
export const NOT_CONNECTED_TITLE = "Results are not connected yet";

/** The screen-reader announcement when a result arrives (walkthrough F2; the only new AT-only text
 * the website adds, besides the 'Conditional' marker). Set when an outcome arrives and cleared to
 * '' while a request runs, so the SAME outcome on a retry is announced again (OutcomeAnnouncer). */
export const RESULTS_READY_ANNOUNCEMENT = "Development results are ready.";

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
        recovery: "Trying again is safe.",
        retryable: true,
        technical: referenceRow(outcome.correlationId),
      };
    case "lot_conditions_unconfirmed":
      // The same request would not succeed on a retry: show the server's plain reason and do NOT
      // label it safe to retry (ruling / matrix note).
      return {
        title: "The results are not available for this lot",
        body: outcome.message,
        recovery: "Trying again will give the same answer until that record can be read.",
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
      <h2>{NOT_CONNECTED_TITLE}</h2>
      <p>The results service is not available on this server. No results were shown.</p>
    </section>
  );
}

/** The heading of the "results are for another property" card, reused so it cannot drift. */
export const ANOTHER_LOT_TITLE = "These results are for another property";

/** Ruling V11 (10): a results document whose identity (the identity adapter) names a different lot
 * than the one requested is NOT shown; the panel says so and offers to ask again for this property. */
function AnotherLotCard({ onAskAgain }: { onAskAgain: () => void }) {
  return (
    <section className="card architect-empty" data-testid="results-another-lot">
      <p className="architect-eyebrow">Development results</p>
      <h2>{ANOTHER_LOT_TITLE}</h2>
      <p>The results that came back are for a different property, so they are not shown.</p>
      <button type="button" className="primary-button" data-testid="results-ask-again" onClick={onAskAgain}>
        Ask again for this property
      </button>
    </section>
  );
}

/**
 * The screen-reader announcement for the current state (walkthrough F2). '' while a request runs
 * or before any outcome, so a result is announced only on arrival and the SAME outcome on a retry
 * re-announces (the region's text genuinely changes). A success reads the fixed ready sentence; a
 * 404 reads the SAME title the not-connected card shows; every other failure reads the SAME title
 * its failure notice shows — so the announcement can never drift from the visible title.
 */
export function resultsAnnouncement(
  busy: boolean,
  outcome: ResultsFetchOutcome | null,
): string {
  if (busy || outcome === null) return "";
  if (outcome.kind === "success") return RESULTS_READY_ANNOUNCEMENT;
  if (outcome.kind === "not_available") return NOT_CONNECTED_TITLE;
  return resultsFailureNotice(outcome)?.title ?? "";
}

export interface ResultsPanelProps {
  bbl: string;
  /** The property's street address, as the dashboard already shows it. Passed to the report action
   * so the report carries it (scenario S9); absent when no confirmed address is known. */
  address?: string;
  /** Injection point for tests; defaults to the global fetch (the live path). */
  fetchImpl?: typeof fetch;
}

export function ResultsPanel({ bbl, address, fetchImpl }: ResultsPanelProps) {
  const [values, setValues] = useState<ResultsFormValues>(INITIAL_VALUES);
  const [heightError, setHeightError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [outcome, setOutcome] = useState<ResultsFetchOutcome | null>(null);
  const [askedWith, setAskedWith] = useState<ResultsFormValues | null>(null);
  // Ruling V11 (1): once a result is shown the form folds to a one-line summary; "Change inputs"
  // reopens it. `editing` is true while the form is open over a shown result.
  const [editing, setEditing] = useState(false);
  const requestId = useRef(0);
  const controllerRef = useRef<AbortController | null>(null);
  const rootRef = useRef<HTMLElement>(null);
  const pendingHeadingFocus = useRef(false);
  const pendingFormFocus = useRef(false);

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
      if (result.kind === "success") {
        // Fold the form and move focus to the results heading on a fresh result (ruling V11 (1)).
        // The focus effect only acts when an own-lot document actually renders.
        setEditing(false);
        pendingHeadingFocus.current = true;
      }
    })();
  }, [bbl, fetchImpl, values]);

  const onChange = useCallback((next: ResultsFormValues) => {
    setValues(next);
    // Clear a stale field message as soon as the field changes; the request is not re-sent.
    setHeightError(previous => (previous === null ? previous : null));
  }, []);

  // Restore the inputs to their starting choices (M5-T149 part C). It never asks the server and
  // never clears an already-shown result; if a result is shown, the normal stale line appears
  // because the inputs no longer match the inputs that result was asked for.
  const reset = useCallback(() => {
    setValues(INITIAL_VALUES);
    setHeightError(null);
  }, []);

  // Reopen the folded form with the inputs kept, and move focus into it (ruling V11 (1)).
  const changeInputs = useCallback(() => {
    setEditing(true);
    pendingFormFocus.current = true;
  }, []);

  // The report action sends the SAME inputs the results form sends (scenario S4). Built from the
  // current form values; a refused height yields no body, so the report cannot be created until the
  // field is fixed. When these inputs change after a report has loaded, ReportPreview marks the
  // shown report out of date and disables printing until it is reloaded.
  const currentRequest = buildRequest(values);
  const reportBody = currentRequest.ok ? currentRequest.body : null;

  const showingDocument = !busy && outcome?.kind === "success";
  // Ruling V11 (10): a document whose identity names a different lot than the one requested is not
  // shown. The lot is READ from the document's scope (identity adapter); an unidentified document is
  // not treated as "another lot" (it is simply shown as-is, never guessed to belong elsewhere).
  // The verified success document is a full results document at runtime; the panel's working view
  // type (ThreeAnswersResults) narrows it, so widen it back to read the identity fields the adapter
  // needs. The adapter reads the lot from scope and decides no law (ruling V2).
  const identity =
    showingDocument && outcome.kind === "success" ? resultIdentity(outcome.document as Results) : null;
  const forAnotherLot = identity?.kind === "known" && identity.lotBbl !== bbl;
  const showingOwnDocument = showingDocument && !forAnotherLot;
  const formFolded = showingOwnDocument && !editing;
  const stale = showingOwnDocument && askedWith !== null && !sameInputs(values, askedWith);
  const failure = !busy && outcome !== null ? resultsFailureNotice(outcome) : null;
  // The one polite live region (walkthrough F2): announce a result and each failure to a
  // screen-reader user. Cleared to '' while busy so a repeated outcome re-announces.
  const announcement = resultsAnnouncement(busy, outcome);

  // Focus management (ruling V11 (1)): when a fresh own-lot result renders, move focus to the
  // results heading (focus only; the live region owns announcements). When the form is reopened,
  // move focus into it so keyboard focus is never stranded on the vanished "Change inputs" button.
  useEffect(() => {
    if (pendingHeadingFocus.current && showingOwnDocument && !editing) {
      pendingHeadingFocus.current = false;
      const heading = rootRef.current?.querySelector<HTMLElement>(".ta-panel-title");
      if (heading) {
        heading.setAttribute("tabindex", "-1");
        heading.focus({ preventScroll: false });
      }
    } else if (pendingFormFocus.current && editing) {
      pendingFormFocus.current = false;
      rootRef.current?.querySelector<HTMLElement>("#results-housing-program")?.focus();
    }
  }, [showingOwnDocument, editing]);

  return (
    <section ref={rootRef} className="results-panel" aria-label="Development results" data-testid="results-panel">
      <OutcomeAnnouncer message={announcement} testId="results-announcer" />
      <ResultsForm
        values={values}
        onChange={onChange}
        onSubmit={submit}
        onReset={reset}
        busy={busy}
        heightError={heightError}
        folded={formFolded}
        onChangeInputs={changeInputs}
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
        forAnotherLot ? (
          <AnotherLotCard onAskAgain={submit} />
        ) : (
          <div className="results-document" data-testid="results-document">
            <ThreeAnswersPanel results={outcome.document} showDraftValues address={address} />
          </div>
        )
      ) : null}

      <ReportPreview bbl={bbl} request={reportBody} address={address} fetchImpl={fetchImpl} />
    </section>
  );
}
