"use client";

/**
 * The parity panel — "Comparable sales & floor area" (queue D-15, plan §11b,
 * queue item B-11). Presentation only, over the v1 parity contract fetched
 * through the lane C adapter `fetchParityData`. It shows two things, and no more
 * in this slice:
 *
 *  1. Comparable sales: each recorded DOF sale with its recorded price and date,
 *     plainly; the disclosed "similar type and size" selection filter in plain
 *     words VERBATIM (an OPEN owner question, B-11 — shown, never decided here);
 *     the excluded rows and their reasons behind a "details" disclosure; the
 *     pinned not-a-valuation notice; and the DOF provenance behind a "Source"
 *     disclosure. NO average, NO price-per-square-foot, NO estimate, NO computed
 *     number of any kind.
 *  2. Unused floor area: ONLY the owner-settled wording ("Remaining development
 *     capacity: Not confirmed" / "Needs verified zoning-lot boundaries and
 *     existing zoning floor area."), in place of a number (§5a item 3). Never a
 *     digit; nothing claims a verified zoning lot.
 *
 * It follows §5a: one status strip with at most three items (details on tap),
 * readable text (it inherits the floating window's 14 px floor), no internal
 * codes on the face, and a plain "not connected yet" card for a 404 plus the
 * shared §5a `FailureNoticeCard` for every other failure — never a number with a
 * caution label. A superseded (aborted) request owns no surface.
 *
 * NO legal logic and NO zoning math live here. The zoning-math switch is off, so
 * the floor-by-floor table and the unit estimate with its formula are NOT in this
 * slice; neither is scenario comparison nor the data-flags / transit-parking
 * panel (D-12 already carries the §8a flags). See docs/lanes/status/D.md.
 */

import { useCallback, useEffect, useState } from "react";
import {
  fetchParityData,
  type ParityData,
  type ParityOutcome,
} from "@/lib/parity-api";
import {
  PARITY_NOT_CONNECTED,
  STRIP_DETAIL_NOTE,
  comparableSalesView,
  parityStripSummary,
  unusedFloorAreaView,
  type ComparableSalesView,
  type ParityStripSummary,
  type SaleRowView,
  type UnusedFloorAreaView,
} from "@/lib/architect/parity-panel-view";
import { FailureNoticeCard } from "./workspace/DashboardFailureNotice";
import { referenceRow, type DashboardFailureNoticeModel } from "./workspace/dashboard-failure";

const NEEDS_PLATFORM =
  "This needs the platform team. Trying again will likely give the same result until it is fixed.";
const RETRY_SAFE = "The property you entered is fine. Trying again is safe.";

/**
 * The §5a failure notice for a non-success parity outcome, or null when the panel
 * handles the outcome another way (`parity` is success; `feature_unavailable` is
 * the "not connected yet" empty card; `aborted` is a superseded request that owns
 * no surface). Reuses the dashboard failure model so the same honest wording is
 * shared; no internal code appears on the face (§5a items 4-5).
 */
export function parityFailureNotice(
  outcome: ParityOutcome,
): DashboardFailureNoticeModel | null {
  switch (outcome.kind) {
    case "parity":
    case "feature_unavailable":
    case "aborted":
      return null;
    case "validation_error":
      return {
        title: "The app could not read this property identifier",
        body: outcome.message,
        recovery: "Check the identifier and try another lot.",
        retryable: false,
        technical: referenceRow(outcome.correlationId),
      };
    case "rate_limited":
      return {
        title: "The data source is busy right now",
        body: outcome.message,
        recovery: RETRY_SAFE,
        retryable: true,
        technical: referenceRow(outcome.correlationId),
      };
    case "inputs_unavailable":
      return {
        title: "Comparable sales and floor area are not available right now",
        body: outcome.message,
        recovery: "The official city source did not return the inputs yet. Trying again is safe.",
        retryable: true,
        technical: referenceRow(outcome.correlationId),
      };
    case "internal_error":
      return {
        title: "Something went wrong on our side",
        body: "The app hit an unexpected problem while loading the comparable sales and floor area.",
        recovery: RETRY_SAFE,
        retryable: true,
        technical: [
          ...(outcome.state ? [{ label: "Failure type", value: outcome.state }] : []),
          ...referenceRow(outcome.correlationId),
        ],
      };
    case "validation_failure":
      return {
        title: "The data did not match the published format",
        body: "The service returned data that failed this screen's format check. Nothing from that response is shown.",
        recovery: NEEDS_PLATFORM,
        retryable: true,
        technical: [
          ...outcome.problems.map((problem) => ({ label: "Format problem", value: problem })),
          ...referenceRow(outcome.correlationId),
        ],
      };
    case "network_error":
      return {
        title: "Could not reach the app's service",
        body: outcome.message,
        recovery: RETRY_SAFE,
        retryable: true,
        technical: [],
      };
    case "client_timeout":
      return {
        title: "Comparable sales took too long",
        body:
          `The service did not answer within ${Math.round(outcome.timeoutMs / 1000)} seconds, ` +
          "so the request was cancelled. No partial data is shown.",
        recovery: RETRY_SAFE,
        retryable: true,
        technical: [],
      };
    case "unexpected_response":
      return {
        title: "Unexpected response from the service",
        body: "The service answered in a way the app does not recognize, so the response was not trusted or shown.",
        recovery: RETRY_SAFE,
        retryable: true,
        technical: [
          { label: "HTTP status", value: String(outcome.httpStatus) },
          ...(outcome.receivedState ? [{ label: "Response state", value: outcome.receivedState }] : []),
          ...referenceRow(outcome.correlationId),
        ],
      };
  }
}

type PanelStatus = { kind: "empty" } | { kind: "error"; model: DashboardFailureNoticeModel };

export interface ParityPanelProps {
  bbl: string;
  /** Injection point for tests; defaults to the global fetch (the live path). */
  fetchImpl?: typeof fetch;
}

interface ParityPanelState {
  status: PanelStatus | null;
  data: ParityData | null;
  retry: () => void;
}

function useParityData({ bbl, fetchImpl }: ParityPanelProps): ParityPanelState {
  const [data, setData] = useState<ParityData | null>(null);
  const [status, setStatus] = useState<PanelStatus | null>(null);
  const [reload, setReload] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setStatus(null);
    setData(null);
    void (async () => {
      const outcome = await fetchParityData(bbl, { fetchImpl });
      if (cancelled) return;
      if (outcome.kind === "parity") {
        setData(outcome.data);
        return;
      }
      if (outcome.kind === "aborted") return; // superseded; the live request owns the surface
      if (outcome.kind === "feature_unavailable") {
        setStatus({ kind: "empty" });
        return;
      }
      const model = parityFailureNotice(outcome);
      setStatus(model ? { kind: "error", model } : { kind: "empty" });
    })();
    return () => {
      cancelled = true;
    };
  }, [bbl, fetchImpl, reload]);

  const retry = useCallback(() => setReload((value) => value + 1), []);
  return { status, data, retry };
}

function LoadingCard() {
  return (
    <section className="card architect-empty" role="status" aria-busy="true" data-testid="parity-loading">
      <p className="architect-eyebrow">Comparable sales &amp; floor area</p>
      <p>Loading recorded comparable sales and the floor-area status…</p>
    </section>
  );
}

function NotConnectedCard() {
  return (
    <section className="card architect-empty" data-testid="parity-unavailable">
      <p className="architect-eyebrow">Comparable sales &amp; floor area</p>
      <h2>Comparable sales are not connected yet</h2>
      <p>{PARITY_NOT_CONNECTED}</p>
    </section>
  );
}

/** The one §5a status strip: the up-to-three summary items, with a plain
 * explanation on tap (details on tap). */
function ParityStatusStrip({ summary }: { summary: ParityStripSummary }) {
  return (
    <details className="card parity-strip" data-testid="parity-strip">
      <summary>
        <span className="parity-strip__items" data-testid="parity-strip-items">
          {summary.items.join(" · ")}
        </span>
        <span className="parity-strip__toggle"> — details</span>
      </summary>
      <div className="parity-strip__detail" data-testid="parity-strip-detail">
        <p>{STRIP_DETAIL_NOTE}</p>
      </div>
    </details>
  );
}

function SaleRow({ sale }: { sale: SaleRowView }) {
  return (
    <li className="parity-sale" data-testid={`parity-${sale.key}`}>
      <span className="parity-sale__address">{sale.address}</span>
      <span className="parity-sale__price">
        Recorded sale price: {sale.recordedPrice ?? "not recorded"}
      </span>
      <span className="parity-sale__date">Sale date: {sale.saleDate}</span>
    </li>
  );
}

function ComparableSalesSection({ view }: { view: ComparableSalesView }) {
  return (
    <section className="card parity-comparable-sales" data-testid="parity-comparable-sales" aria-label="Comparable sales">
      <h2>Comparable sales</h2>
      <p className="parity-not-a-valuation" data-testid="parity-not-a-valuation">
        {view.notAValuation}
      </p>
      {view.criteriaText ? (
        <p className="parity-criteria" data-testid="parity-criteria">
          How these were selected: {view.criteriaText}
        </p>
      ) : null}
      {view.selected.length ? (
        <ul className="parity-sales-list">
          {view.selected.map((sale) => (
            <SaleRow key={sale.key} sale={sale} />
          ))}
        </ul>
      ) : (
        <p className="parity-sales-empty">No recorded sale matched the disclosed filter.</p>
      )}
      {view.excluded.length ? (
        <details className="parity-excluded" data-testid="parity-excluded">
          <summary>{view.excluded.length} not included — details</summary>
          <ul>
            {view.excluded.map((row) => (
              <li key={row.key} data-testid={`parity-${row.key}`}>
                <span>{row.address}</span> <span>{row.saleDate}</span> <span>{row.reasonText}</span>
              </li>
            ))}
          </ul>
        </details>
      ) : null}
      {view.source ? (
        <details className="parity-source" data-testid="parity-source">
          <summary>Source</summary>
          <dl>
            <dt>Dataset</dt>
            <dd>{view.source.dataset}</dd>
            {view.source.datasetId ? (
              <>
                <dt>Dataset id</dt>
                <dd>{view.source.datasetId}</dd>
              </>
            ) : null}
            {view.source.requestUrl ? (
              <>
                <dt>Request</dt>
                <dd>{view.source.requestUrl}</dd>
              </>
            ) : null}
            {view.source.retrievedAt ? (
              <>
                <dt>Retrieved</dt>
                <dd>{view.source.retrievedAt}</dd>
              </>
            ) : null}
            {view.source.vintage ? (
              <>
                <dt>Dataset vintage</dt>
                <dd>{view.source.vintage}</dd>
              </>
            ) : null}
          </dl>
        </details>
      ) : null}
    </section>
  );
}

function UnusedFloorAreaSection({ view }: { view: UnusedFloorAreaView }) {
  return (
    <section className="card parity-unused" data-testid="parity-unused" aria-label="Unused floor area">
      <h2>Unused floor area</h2>
      <p className="parity-unused__label" data-testid="parity-unused-label">
        {view.label}
      </p>
      <p className="parity-unused__reason" data-testid="parity-unused-reason">
        {view.reason}
      </p>
    </section>
  );
}

export function ParityPanel({ bbl, fetchImpl }: ParityPanelProps) {
  const { status, data, retry } = useParityData({ bbl, fetchImpl });

  if (status?.kind === "error") {
    return <FailureNoticeCard model={status.model} onRetry={retry} testId="parity-failure" focusTitle />;
  }
  if (status?.kind === "empty") return <NotConnectedCard />;
  if (!data) return <LoadingCard />;

  const sales = comparableSalesView(data);
  const unused = unusedFloorAreaView(data);
  const summary = parityStripSummary(data);

  return (
    <div className="parity-panel" data-testid="parity-panel">
      <ParityStatusStrip summary={summary} />
      <ComparableSalesSection view={sales} />
      <UnusedFloorAreaSection view={unused} />
    </div>
  );
}
