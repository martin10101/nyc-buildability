"use client";

/**
 * The §8a hidden-issue-flags panel (queue D-12, plan M2-06 / L-11, §8a).
 * Presentation only, over the W0 contract fetched through `fetchHiddenIssueFlags`.
 * It shows the four §8a groups, each item once, with its status label ("Flag",
 * "Opportunity", "Check needed", "No flag"), a plain one-line meaning, its detail,
 * and its typical source; each evidence input sits behind a "Source" disclosure.
 *
 * It follows §5a: one status strip with at most three notices (details on tap),
 * readable text (it renders inside the floating window, whose content carries the
 * 14 px readable floor, D-03 slice 5), no internal codes on the face, and a plain
 * "Not available — reason" failure card (the shared FailureNoticeCard) rather than
 * numbers with caution labels.
 *
 * "Beside the affected results": while the zoning-math switch is off there are no
 * result numbers, so each flag is shown in its group; a flag with a `fact_ref`
 * names the site fact it relates to, and `BESIDE_RESULTS_NOTE` says placement
 * beside the number waits on results. The route is not mounted yet (lane C W5),
 * so in the app a 404 shows the plain "not connected yet" card.
 *
 * NO legal logic and NO zoning math live here: the §8a layer reports what the
 * sourced data shows, or 'Check needed'. Nothing here claims a verified zoning lot
 * or decides a rule.
 */

import { useCallback, useEffect, useState } from "react";
import {
  fetchHiddenIssueFlags,
  type HiddenIssueFlagsFetchOutcome,
} from "@/lib/hidden-issue-flags-api";
import type { HiddenIssueFlagsDocument } from "@/lib/hidden-issue-flags-contract-checks";
import {
  BESIDE_RESULTS_NOTE,
  EVERY_PROPERTY_NOTE,
  NOT_A_CLEAN_BILL_NOTE,
  STATUS_GLOSSARY,
  flagStripSummary,
  groupViews,
  type FlagStripSummary,
  type FlagView,
  type GroupView,
} from "@/lib/architect/hidden-issue-flags-view";
import { FailureNoticeCard } from "./workspace/DashboardFailureNotice";
import { referenceRow, type DashboardFailureNoticeModel } from "./workspace/dashboard-failure";

const NEEDS_PLATFORM =
  "This needs the platform team. Trying again will likely give the same result until it is fixed.";
const RETRY_SAFE = "The property you entered is fine. Trying again is safe.";

/**
 * The §5a failure notice for a non-success flags outcome, or null when the panel handles the
 * outcome another way (`flags` is success; `not_available` is the "not connected yet" empty card;
 * `aborted` is a superseded request that owns no surface). Reuses the dashboard failure model so
 * the same honest wording is shared; no internal code appears on the face (§5a items 4-5).
 */
export function hiddenIssueFlagsFailureNotice(
  outcome: HiddenIssueFlagsFetchOutcome,
): DashboardFailureNoticeModel | null {
  switch (outcome.kind) {
    case "flags":
    case "not_available":
    case "aborted":
      return null;
    case "validation_error":
      return {
        title: "The app could not read this property identifier",
        body: outcome.message,
        recovery: "Check the identifier and try another lot.",
        retryable: false,
        technical: [{ label: "Rejection code", value: outcome.code }, ...referenceRow(outcome.correlationId)],
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
        title: "The hidden-issue checks are not available right now",
        body: outcome.message,
        recovery: "The official city source did not return the inputs yet. Trying again is safe.",
        retryable: true,
        technical: referenceRow(outcome.correlationId),
      };
    case "server_contract_error":
      return {
        title: "The app would not show unreliable checks",
        body: "The server built a set of checks that failed its own quality checks and held it back rather than show data it could not trust.",
        recovery: NEEDS_PLATFORM,
        retryable: true,
        technical: [{ label: "Failure type", value: "internal_contract_error" }, ...referenceRow(outcome.correlationId)],
      };
    case "internal_error":
      return {
        title: "Something went wrong on our side",
        body: "The app hit an unexpected problem while loading the hidden-issue checks.",
        recovery: RETRY_SAFE,
        retryable: true,
        technical: referenceRow(outcome.correlationId),
      };
    case "validation_failure":
      return {
        title: "The checks did not match the published data format",
        body: "The service returned checks that failed this screen's format check. Nothing from that response is shown.",
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
        title: "The hidden-issue checks took too long",
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

export interface HiddenIssueFlagsProps {
  bbl: string;
  /** Injection point for tests; defaults to the global fetch (the live path). */
  fetchImpl?: typeof fetch;
}

interface HiddenIssueFlagsState {
  status: PanelStatus | null;
  flagsDoc: HiddenIssueFlagsDocument | null;
  retry: () => void;
}

function useHiddenIssueFlags({ bbl, fetchImpl }: HiddenIssueFlagsProps): HiddenIssueFlagsState {
  const [flagsDoc, setFlagsDoc] = useState<HiddenIssueFlagsDocument | null>(null);
  const [status, setStatus] = useState<PanelStatus | null>(null);
  const [reload, setReload] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setStatus(null);
    setFlagsDoc(null);
    void (async () => {
      const outcome = await fetchHiddenIssueFlags(bbl, { fetchImpl });
      if (cancelled) return;
      if (outcome.kind === "flags") {
        setFlagsDoc(outcome.document);
        return;
      }
      if (outcome.kind === "aborted") return; // superseded; the live request owns the surface
      if (outcome.kind === "not_available") {
        setStatus({ kind: "empty" });
        return;
      }
      const model = hiddenIssueFlagsFailureNotice(outcome);
      setStatus(model ? { kind: "error", model } : { kind: "empty" });
    })();
    return () => {
      cancelled = true;
    };
  }, [bbl, fetchImpl, reload]);

  const retry = useCallback(() => setReload((value) => value + 1), []);
  return { status, flagsDoc, retry };
}

function LoadingCard() {
  return (
    <section className="card architect-empty" role="status" aria-busy="true" data-testid="hidden-issues-loading">
      <p className="architect-eyebrow">Hidden issues</p>
      <p>Checking for hidden issues and opportunities…</p>
    </section>
  );
}

function NotConnectedCard() {
  return (
    <section className="card architect-empty" data-testid="hidden-issues-unavailable">
      <p className="architect-eyebrow">Hidden issues</p>
      <h2>Hidden-issue checks are not connected yet</h2>
      <p>The data service is not wired to this screen. Nothing is guessed, and no result is shown as clear.</p>
    </section>
  );
}

/** The one §5a status strip: the up-to-three summary items, with the standing notes on tap. */
function FlagStatusStrip({ summary }: { summary: FlagStripSummary }) {
  return (
    <details className="card hidden-issues-strip" data-testid="hidden-issues-strip">
      <summary>
        <span className="hidden-issues-strip__items" data-testid="hidden-issues-strip-items">
          {summary.items.join(" · ")}
        </span>
        <span className="hidden-issues-strip__toggle"> — details</span>
      </summary>
      <div className="hidden-issues-strip__detail" data-testid="hidden-issues-strip-detail">
        <p>{NOT_A_CLEAN_BILL_NOTE}</p>
        <dl className="hidden-issues-strip__glossary">
          {STATUS_GLOSSARY.map((entry) => (
            <div key={entry.label}>
              <dt>{entry.label}</dt>
              <dd>{entry.meaning}</dd>
            </div>
          ))}
        </dl>
        <p>{BESIDE_RESULTS_NOTE}</p>
        <p>{EVERY_PROPERTY_NOTE}</p>
      </div>
    </details>
  );
}

function FlagRow({ flag }: { flag: FlagView }) {
  return (
    <li className="hidden-issue" data-testid={`hidden-issue-${flag.key}`} data-status={flag.status}>
      <div className="hidden-issue__head">
        <span className="hidden-issue__title">{flag.title}</span>
        <span
          className={`hidden-issue__status hidden-issue__status--${flag.status}`}
          data-testid={`hidden-issue-status-${flag.key}`}
        >
          {flag.statusLabel}
        </span>
      </div>
      <p className="hidden-issue__detail">{flag.detail}</p>
      {flag.relation ? (
        <p className="hidden-issue__relation" data-testid={`hidden-issue-relation-${flag.key}`}>
          {flag.relation}
        </p>
      ) : null}
      {flag.exceptionLabel ? (
        <p className="hidden-issue__exception">Marked for results: {flag.exceptionLabel}</p>
      ) : null}
      <details className="hidden-issue__source" data-testid={`hidden-issue-source-${flag.key}`}>
        <summary>Source</summary>
        <p className="hidden-issue__typical">Typical source: {flag.typicalSource}</p>
        {flag.evidence.length ? (
          <dl>
            {flag.evidence.map((item, index) => (
              <div key={index}>
                <dt>{item.label}</dt>
                {item.sourceLines.map((line, lineIndex) => (
                  <dd key={lineIndex}>{line}</dd>
                ))}
              </div>
            ))}
          </dl>
        ) : null}
      </details>
    </li>
  );
}

function GroupSection({ group }: { group: GroupView }) {
  return (
    <section className="card hidden-issues-group" data-testid={`hidden-issues-group-${group.key}`} aria-label={group.title}>
      <h2>{group.title}</h2>
      <ul className="hidden-issues-list">
        {group.flags.map((flag) => (
          <FlagRow key={flag.key} flag={flag} />
        ))}
      </ul>
    </section>
  );
}

export function HiddenIssueFlags({ bbl, fetchImpl }: HiddenIssueFlagsProps) {
  const { status, flagsDoc, retry } = useHiddenIssueFlags({ bbl, fetchImpl });

  if (status?.kind === "error") {
    return <FailureNoticeCard model={status.model} onRetry={retry} testId="hidden-issues-failure" focusTitle />;
  }
  if (status?.kind === "empty") return <NotConnectedCard />;
  if (!flagsDoc) return <LoadingCard />;

  const groups = groupViews(flagsDoc);
  const summary = flagStripSummary(flagsDoc);

  return (
    <div className="hidden-issues" data-testid="hidden-issues">
      <FlagStatusStrip summary={summary} />
      {groups.map((group) => (
        <GroupSection key={group.key} group={group} />
      ))}
    </div>
  );
}
