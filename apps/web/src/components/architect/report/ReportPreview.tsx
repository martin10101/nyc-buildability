"use client";

/**
 * The report action (task M5-T153, scenario S4; directive D-090 rows R903/R928). It opens the
 * program's report — built on the server by M5-T151 and printed by the browser — for the current
 * property and the SAME inputs the results form sends, and shows it for printing.
 *
 * It appears in two places:
 *  - inside the Results window (controlled mode): the parent passes the current results inputs as
 *    `request`; when those inputs change after the report has loaded, the shown report is marked
 *    OUT OF DATE and printing is disabled until it is reloaded;
 *  - in the workspace report tool when results are switched on (`withInputs`): it renders the same
 *    results inputs form and builds the request itself.
 *
 * The returned report is shown in a sandboxed iframe that runs NO script (ruling X9 d: the report
 * is standalone static HTML). Printing is driven from the parent window. States: loading; a failed
 * fetch or a refusal in plain words (no status code, route or field name — ruling X6); out of date.
 * No legal logic and no zoning math live here; it transports and presents (ruling X7).
 */

import { useCallback, useEffect, useRef, useState } from "react";
import {
  fetchReport,
  type ReportFetchOutcome,
  type ReportRequestBody,
} from "@/lib/report-api";
import {
  HEIGHT_REFUSED_MESSAGE,
  ResultsForm,
  type ResultsFormValues,
} from "../ResultsForm";
import "./report-preview.css";

/** The starting inputs for the self-contained report tool — the same choices the results form
 * starts from (standard residence, no height, no statement). Mirrors ResultsPanel's INITIAL_VALUES;
 * kept local to avoid a client-component import cycle (ResultsPanel renders this component). */
const INITIAL_VALUES: ResultsFormValues = {
  program: "standard_residence",
  heightText: "",
  densityStatement: false,
};

/** Plain, developer-free lines for each state (ruling X6). */
const LOADING_LINE = "Preparing the report for this property…";
const NOT_AVAILABLE_LINE = "The report is not available yet for this property.";
const ERROR_LINE = "The report could not be loaded. Trying again is safe.";
const OUT_OF_DATE_LINE =
  "You changed an input. This report is for the earlier inputs. Reload it before printing.";
const INVALID_INPUTS_LINE = "Enter valid inputs above, then create the report.";

/**
 * Build the report body from the form, mirroring the results form's rule (ruling X9 d: the SAME
 * body): the height is sent only when present and greater than zero, the statement only when made.
 * A non-positive or non-numeric height is refused with the results form's own message.
 */
function buildReportBody(
  values: ResultsFormValues,
): { ok: true; body: ReportRequestBody } | { ok: false; heightError: string } {
  const trimmed = values.heightText.trim();
  const body: ReportRequestBody = { housing_program: values.program };
  if (trimmed !== "") {
    const height = Number(trimmed);
    if (!Number.isFinite(height) || height <= 0) {
      return { ok: false, heightError: HEIGHT_REFUSED_MESSAGE };
    }
    body.floor_to_floor_ft = height;
  }
  if (values.densityStatement === true) body.special_density_statement = true;
  return { ok: true, body };
}

function sameBody(a: ReportRequestBody | null, b: ReportRequestBody | null): boolean {
  if (a === null || b === null) return false;
  return (
    a.housing_program === b.housing_program &&
    a.floor_to_floor_ft === b.floor_to_floor_ft &&
    a.special_density_statement === b.special_density_statement
  );
}

export interface ReportPreviewProps {
  bbl: string;
  /** Controlled mode: the current inputs (the same body the results form sends), or null when the
   * inputs are not valid. Ignored when `withInputs` is set. */
  request?: ReportRequestBody | null;
  /** Self-contained mode (the workspace report tool): render the results inputs form and build the
   * request from it. */
  withInputs?: boolean;
  /** The property's street address, as the website already shows it (scenario S9). Sent to the
   * report route as the optional `?address=` parameter; trimmed and capped client-side. Absent when
   * the website has no confirmed address. */
  address?: string;
  /** Injection point for tests; defaults to the global fetch (the live path). */
  fetchImpl?: typeof fetch;
}

export function ReportPreview({ bbl, request = null, withInputs = false, address, fetchImpl }: ReportPreviewProps) {
  const [values, setValues] = useState<ResultsFormValues>(INITIAL_VALUES);
  const [heightError, setHeightError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [outcome, setOutcome] = useState<ReportFetchOutcome | null>(null);
  const [loadedRequest, setLoadedRequest] = useState<ReportRequestBody | null>(null);
  const requestId = useRef(0);
  const controllerRef = useRef<AbortController | null>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // The inputs this action will send: in the self-contained tool they come from its own form; in
  // the Results window they are the parent's current inputs. An invalid self-contained height
  // yields null so nothing is sent.
  let effectiveRequest: ReportRequestBody | null;
  if (withInputs) {
    const built = buildReportBody(values);
    effectiveRequest = built.ok ? built.body : null;
  } else {
    effectiveRequest = request;
  }
  const effectiveRef = useRef<ReportRequestBody | null>(effectiveRequest);
  effectiveRef.current = effectiveRequest;

  const load = useCallback(() => {
    const body = effectiveRef.current;
    if (!body) return;
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    requestId.current += 1;
    const id = requestId.current;
    const asked = body;
    setLoading(true);
    void (async () => {
      const result = await fetchReport(bbl, body, { fetchImpl, signal: controller.signal, address });
      if (id !== requestId.current) return; // a newer request has replaced this one
      setOutcome(result);
      setLoading(false);
      if (result.kind === "success") setLoadedRequest(asked);
    })();
  }, [bbl, fetchImpl, address]);

  // Abort any in-flight request when the component unmounts (the window is closed).
  useEffect(() => () => controllerRef.current?.abort(), []);

  const onFormChange = useCallback((next: ResultsFormValues) => {
    setValues(next);
    setHeightError(previous => (previous === null ? previous : null));
  }, []);

  const onFormSubmit = useCallback(() => {
    const built = buildReportBody(values);
    if (!built.ok) {
      setHeightError(built.heightError);
      return;
    }
    setHeightError(null);
    load();
  }, [values, load]);

  const onFormReset = useCallback(() => {
    setValues(INITIAL_VALUES);
    setHeightError(null);
  }, []);

  const print = useCallback(() => {
    iframeRef.current?.contentWindow?.print?.();
  }, []);

  const hasReport = !loading && outcome?.kind === "success";
  const outOfDate = hasReport && !sameBody(effectiveRequest, loadedRequest);
  const canPrint = hasReport && !outOfDate;
  const actionLabel = hasReport ? (outOfDate ? "Update report" : "Reload report") : "Create report";

  return (
    <section className="report-preview" aria-label="Report" data-testid="report-preview">
      <h3 className="report-preview-title">Report</h3>
      <p className="report-preview-lead">
        Open the program&apos;s report for this property and print it or save it as a PDF.
      </p>

      {withInputs ? (
        <ResultsForm
          values={values}
          onChange={onFormChange}
          onSubmit={onFormSubmit}
          onReset={onFormReset}
          busy={loading}
          heightError={heightError}
          folded={false}
          onChangeInputs={() => {}}
        />
      ) : null}

      <div className="report-preview-actions">
        <button
          type="button"
          className="primary-button"
          data-testid="report-create"
          aria-busy={loading}
          disabled={loading || effectiveRequest === null}
          onClick={load}
        >
          {actionLabel}
        </button>
        {hasReport ? (
          <button
            type="button"
            className="secondary-button"
            data-testid="report-print"
            disabled={!canPrint}
            onClick={print}
          >
            Print or save as PDF
          </button>
        ) : null}
      </div>

      {effectiveRequest === null && !hasReport ? (
        <p className="report-preview-note section-note" data-testid="report-invalid-inputs">
          {INVALID_INPUTS_LINE}
        </p>
      ) : null}

      {loading ? (
        <p className="report-preview-note" role="status" aria-busy="true" data-testid="report-loading">
          {LOADING_LINE}
        </p>
      ) : null}

      {!loading && outcome?.kind === "not_available" ? (
        <p className="report-preview-error" role="status" data-testid="report-not-available">
          {NOT_AVAILABLE_LINE}
        </p>
      ) : null}

      {!loading && outcome?.kind === "refused" ? (
        <p className="report-preview-error" role="status" data-testid="report-refused">
          {outcome.message}
        </p>
      ) : null}

      {!loading && outcome?.kind === "error" ? (
        <p className="report-preview-error" role="status" data-testid="report-error">
          {ERROR_LINE}
        </p>
      ) : null}

      {outOfDate ? (
        <p className="report-preview-stale" role="status" data-testid="report-stale">
          {OUT_OF_DATE_LINE}
        </p>
      ) : null}

      {hasReport && outcome.kind === "success" ? (
        <iframe
          ref={iframeRef}
          className="report-preview-frame"
          data-testid="report-frame"
          title="Report preview"
          /* No script runs in the frame: the report is standalone static HTML (ruling X9 d). The
             two tokens are only what printing from the parent needs:
               allow-same-origin — the parent must read the frame's contentWindow to print it; a
                 sandboxed frame without it is an opaque origin the parent cannot drive. With no
                 allow-scripts the frame still cannot execute anything.
               allow-modals — window.print() opens the browser print dialog, which the sandbox
                 treats as a modal; without this token the print call is silently blocked.
             allow-scripts, allow-forms, allow-popups, allow-top-navigation and allow-downloads are
             deliberately omitted: the report runs no script, submits no form, opens no window,
             navigates nothing and downloads nothing. */
          sandbox="allow-same-origin allow-modals"
          srcDoc={outcome.html}
        />
      ) : null}
    </section>
  );
}
