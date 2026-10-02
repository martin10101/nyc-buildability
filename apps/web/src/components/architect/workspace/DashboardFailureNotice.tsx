"use client";

import {
  dashboardFailureNotice,
  type DashboardFailureOutcome,
} from "./dashboard-failure";

/**
 * The one failure notice the dashboard shows in place of the results when the property lookup
 * returns no profile (queue D-03, M1-17; plan §5a). Plain title, plain explanation and a single
 * recovery line — no internal code on the face (§5a item 5). A recoverable fault carries one
 * "Try again" button; the reference id, HTTP status and other codes sit behind "Technical
 * details" (§5a item 4). It carries no `role="alert"`/`aria-live`: the dashboard's single
 * persistent OutcomeAnnouncer emits the one assistive announcement, so mounting this card can
 * never double-announce. A superseded (`aborted`) request renders nothing.
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
  return (
    <section className="card bd-failure-notice" data-testid="dashboard-failure-notice">
      <h1 tabIndex={-1} className="bd-failure-title" data-testid="dashboard-failure-title">
        {notice.title}
      </h1>
      <p data-testid="dashboard-failure-body">{notice.body}</p>
      <p className="bd-failure-recovery">{notice.recovery}</p>
      {notice.retryable ? (
        <button
          type="button"
          className="bd-secondary-action"
          data-testid="dashboard-failure-retry"
          onClick={onRetry}
        >
          Try again
        </button>
      ) : null}
      {notice.technical.length ? (
        <details className="bd-failure-technical" data-testid="dashboard-failure-technical">
          <summary>Technical details (for support)</summary>
          <dl className="bd-failure-codes">
            {notice.technical.map((item, index) => (
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
