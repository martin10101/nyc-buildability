"use client";

import {
  dashboardFailureNotice,
  type DashboardFailureNoticeModel,
  type DashboardFailureOutcome,
} from "./dashboard-failure";

/**
 * Shared plain-§5a presentation for one failure notice on the single-page dashboard (queue D-03,
 * M1-17). Plain title, plain explanation and a single recovery line — no internal code on the
 * face (§5a item 5). A recoverable fault carries one "Try again" button; the reference id, HTTP
 * status and other codes sit behind a closed "Technical details" (§5a item 4). It carries no
 * `role="alert"`/`aria-live`: the dashboard's persistent OutcomeAnnouncer already emits the one
 * assistive announcement, so mounting a card can never double-announce.
 *
 * `testId` prefixes every hook so two notices on the same screen never collide. `heading` is an
 * `h1` for the main results-area notice (the property lookup replaced the whole result) and an
 * `h2` for a secondary enrichment notice; `focusTitle` makes the heading a programmatic-focus
 * target only for the main notice, so the enrichment notices never compete with the property
 * heading's focus flow.
 */
export function FailureNoticeCard({
  model,
  onRetry,
  heading = "h1",
  testId = "dashboard-failure",
  focusTitle = false,
  retryLabel = "Try again",
}: {
  model: DashboardFailureNoticeModel;
  onRetry: () => void;
  heading?: "h1" | "h2";
  testId?: string;
  focusTitle?: boolean;
  retryLabel?: string;
}) {
  const titleTestId = `${testId}-title`;
  const tabIndex = focusTitle ? -1 : undefined;
  return (
    <section className="card bd-failure-notice" data-testid={`${testId}-notice`}>
      {heading === "h1" ? (
        <h1 className="bd-failure-title" data-testid={titleTestId} tabIndex={tabIndex}>
          {model.title}
        </h1>
      ) : (
        <h2 className="bd-failure-title" data-testid={titleTestId} tabIndex={tabIndex}>
          {model.title}
        </h2>
      )}
      <p data-testid={`${testId}-body`}>{model.body}</p>
      <p className="bd-failure-recovery">{model.recovery}</p>
      {model.retryable ? (
        <button
          type="button"
          className="bd-secondary-action"
          data-testid={`${testId}-retry`}
          onClick={onRetry}
        >
          {retryLabel}
        </button>
      ) : null}
      {model.technical.length ? (
        <details className="bd-failure-technical" data-testid={`${testId}-technical`}>
          <summary>Technical details (for support)</summary>
          <dl className="bd-failure-codes">
            {model.technical.map((item, index) => (
              <div key={`${item.label}-${index}`}>
                <dt>{item.label}</dt>
                <dd>
                  <code>{item.value}</code>
                </dd>
              </div>
            ))}
          </dl>
        </details>
      ) : null}
    </section>
  );
}

/**
 * The one failure notice the dashboard shows in place of the results when the property lookup
 * returns no profile (plan §5a). Its `h1` is the programmatic-focus target for the results area.
 * A superseded (`aborted`) request renders nothing.
 */
export function DashboardFailureNotice({
  outcome,
  onRetry,
}: {
  outcome: DashboardFailureOutcome;
  onRetry: () => void;
}) {
  const notice = dashboardFailureNotice(outcome);
  if (!notice) return null;
  return <FailureNoticeCard model={notice} onRetry={onRetry} focusTitle />;
}
