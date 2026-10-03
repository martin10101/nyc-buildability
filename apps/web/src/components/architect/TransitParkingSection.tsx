"use client";

/**
 * The "Transit and parking zone" section of the parity window — "Comparable sales &
 * floor area" (queue D-15 slice 2, plan §5a / §11b, queue item B-10, check C-8).
 *
 * Presentation only, over the v1 transit_parking contract fetched through the lane C
 * adapter `fetchTransitParking`. It reads ONE lot's transit/parking-ZONE status and
 * shows, in plain words: the contract's `status_label` as the headline, the recorded
 * `transit_zone`, the server's verbatim `detail` line, and — when the zone is not
 * recorded — `missing_source` as "Not available — <reason>". The dataset / version /
 * retrieved provenance sits ONLY behind a "Source" disclosure (§5a item 4). It shows
 * NO computed number, NO parking-requirement math, and never decides a rule or claims
 * a verified zoning lot (the contract has no parking-outcome slot; that is Lane A /
 * G6 work, never this layer's).
 *
 * States (each its own surface, independent of the sibling comparable-sales section):
 * loading; `not_available` / 404 → the same plain "not connected yet" card the window
 * uses; every error outcome → the shared §5a `FailureNoticeCard`; a superseded
 * (`aborted`) request owns no surface and renders nothing.
 */

import { useCallback, useEffect, useState } from "react";
import {
  fetchTransitParking,
  type TransitParking,
  type TransitParkingFetchOutcome,
} from "@/lib/transit-parking-api";
import {
  TRANSIT_NOT_CONNECTED,
  TRANSIT_SECTION_TITLE,
  transitParkingView,
} from "@/lib/architect/transit-parking-view";
import { FailureNoticeCard } from "./workspace/DashboardFailureNotice";
import { referenceRow, type DashboardFailureNoticeModel } from "./workspace/dashboard-failure";

const NEEDS_PLATFORM =
  "This needs the platform team. Trying again will likely give the same result until it is fixed.";
const RETRY_SAFE = "The property you entered is fine. Trying again is safe.";

/**
 * The §5a failure notice for a non-success transit/parking outcome, or null when the
 * section handles the outcome another way (`status` renders data; `not_available` is
 * the "not connected yet" empty card; `aborted` is a superseded request that owns no
 * surface). Reuses the dashboard failure model so the same honest wording is shared;
 * no internal code appears on the face (§5a items 4-5).
 */
export function transitParkingFailureNotice(
  outcome: TransitParkingFetchOutcome,
): DashboardFailureNoticeModel | null {
  switch (outcome.kind) {
    case "status":
    case "not_available":
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
    case "inputs_unavailable":
      return {
        title: "The transit and parking zone is not available right now",
        body: outcome.message,
        recovery: "The official city source did not return the zone yet. Trying again is safe.",
        retryable: true,
        technical: referenceRow(outcome.correlationId),
      };
    case "server_contract_error":
      return {
        title: "The app would not show an unreliable transit and parking zone",
        body:
          "The service built a transit/parking status that failed its own quality checks and " +
          "held it back rather than show data it could not trust.",
        recovery: NEEDS_PLATFORM,
        retryable: true,
        technical: referenceRow(outcome.correlationId),
      };
    case "internal_error":
      return {
        title: "Something went wrong on our side",
        body: "The app hit an unexpected problem while loading the transit and parking zone.",
        recovery: RETRY_SAFE,
        retryable: true,
        technical: referenceRow(outcome.correlationId),
      };
    case "validation_failure":
      return {
        title: "The transit and parking data did not match the published format",
        body:
          "The service returned a transit/parking status that failed this screen's format check. " +
          "Nothing from that response is shown.",
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
        title: "The transit and parking zone took too long",
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

type SectionStatus =
  | { kind: "empty" }
  | { kind: "aborted" }
  | { kind: "error"; model: DashboardFailureNoticeModel };

export interface TransitParkingSectionProps {
  bbl: string;
  /** Injection point for tests; defaults to the global fetch (the live path). */
  fetchImpl?: typeof fetch;
}

function useTransitParking({ bbl, fetchImpl }: TransitParkingSectionProps) {
  const [data, setData] = useState<TransitParking | null>(null);
  const [status, setStatus] = useState<SectionStatus | null>(null);
  const [reload, setReload] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setStatus(null);
    setData(null);
    void (async () => {
      const outcome = await fetchTransitParking(bbl, { fetchImpl });
      if (cancelled) return; // superseded by a newer request; it owns the surface
      if (outcome.kind === "status") {
        setData(outcome.status);
        return;
      }
      if (outcome.kind === "aborted") {
        setStatus({ kind: "aborted" });
        return;
      }
      if (outcome.kind === "not_available") {
        setStatus({ kind: "empty" });
        return;
      }
      const model = transitParkingFailureNotice(outcome);
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
    <section
      className="card architect-empty"
      role="status"
      aria-busy="true"
      data-testid="transit-parking-loading"
    >
      <p className="architect-eyebrow">{TRANSIT_SECTION_TITLE}</p>
      <p>Loading the recorded transit and parking zone…</p>
    </section>
  );
}

function NotConnectedCard() {
  return (
    <section className="card architect-empty" data-testid="transit-parking-unavailable">
      <p className="architect-eyebrow">{TRANSIT_SECTION_TITLE}</p>
      <h2>The transit and parking zone is not connected yet</h2>
      <p>{TRANSIT_NOT_CONNECTED}</p>
    </section>
  );
}

export function TransitParkingSection({ bbl, fetchImpl }: TransitParkingSectionProps) {
  const { status, data, retry } = useTransitParking({ bbl, fetchImpl });

  if (status?.kind === "aborted") return null; // superseded request owns no surface
  if (status?.kind === "error") {
    return (
      <FailureNoticeCard
        model={status.model}
        onRetry={retry}
        heading="h2"
        testId="transit-parking-failure"
      />
    );
  }
  if (status?.kind === "empty") return <NotConnectedCard />;
  if (!data) return <LoadingCard />;

  const view = transitParkingView(data);
  return (
    <section
      className="card transit-parking"
      data-testid="transit-parking"
      aria-label={TRANSIT_SECTION_TITLE}
    >
      <h2>{TRANSIT_SECTION_TITLE}</h2>
      <p className="transit-parking__headline" data-testid="transit-parking-headline">
        {view.headline}
      </p>
      {view.zone ? (
        <p className="transit-parking__zone" data-testid="transit-parking-zone">
          Transit zone: {view.zone}
        </p>
      ) : null}
      {view.missingSource ? (
        <p className="transit-parking__missing" data-testid="transit-parking-missing">
          {view.missingSource}
        </p>
      ) : null}
      <p className="transit-parking__detail" data-testid="transit-parking-detail">
        {view.detail}
      </p>
      {view.source ? (
        <details className="transit-parking__source" data-testid="transit-parking-source">
          <summary>Source</summary>
          <dl>
            <dt>Dataset</dt>
            <dd>{view.source.dataset}</dd>
            {view.source.datasetVersion ? (
              <>
                <dt>Dataset version</dt>
                <dd>{view.source.datasetVersion}</dd>
              </>
            ) : null}
            {view.source.retrievedAt ? (
              <>
                <dt>Retrieved</dt>
                <dd>{view.source.retrievedAt}</dd>
              </>
            ) : null}
            {view.source.requestUrl ? (
              <>
                <dt>Request</dt>
                <dd>{view.source.requestUrl}</dd>
              </>
            ) : null}
          </dl>
        </details>
      ) : null}
    </section>
  );
}
