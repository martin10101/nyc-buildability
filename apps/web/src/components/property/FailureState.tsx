import type {
  InternalErrorOutcome,
  NetworkErrorOutcome,
  NoMatchOutcome,
  UnexpectedResponseOutcome,
  UpstreamFailureOutcome,
  ValidationErrorOutcome,
} from "@/lib/api";

/**
 * First-class failure states (task M2-T001 output 3). Each documented
 * non-200 outcome has its own wording: what failed, whether retry is safe,
 * and what the user can do — never a raw backend error dump
 * (docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md section 12).
 */

function Meta({ correlationId }: { correlationId: string | null }) {
  if (!correlationId) return null;
  return (
    <p className="failure-meta">
      Reference id for support and server logs:{" "}
      <code data-testid="correlation-id">{correlationId}</code>
    </p>
  );
}

function RetryButton({ onRetry }: { onRetry: () => void }) {
  return (
    <button type="button" className="secondary-button" onClick={onRetry}>
      Retry lookup
    </button>
  );
}

export function NoMatchState({ outcome }: { outcome: NoMatchOutcome }) {
  return (
    <section className="card failure-state" data-testid="state-no-match">
      <h2 className="failure-title">No property record found</h2>
      <p>
        The BBL{outcome.bbl ? ` ${outcome.bbl}` : ""} is a valid format, but
        the current official dataset has no record for it. This is a result
        from the official source, not a system error.
      </p>
      <p data-testid="no-match-explanation">{outcome.message}</p>
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

export function ValidationErrorState({
  outcome,
}: {
  outcome: ValidationErrorOutcome;
}) {
  return (
    <section className="card failure-state" data-testid="state-validation-error">
      <h2 className="failure-title">The API rejected this BBL</h2>
      <p data-testid="validation-message">{outcome.message}</p>
      <p className="failure-meta">
        Rejection code: <code data-testid="validation-code">{outcome.code}</code>
      </p>
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

const UPSTREAM_COPY: Record<
  UpstreamFailureOutcome["state"],
  { title: string; body: string }
> = {
  rate_limited: {
    title: "The official data source is throttling requests",
    body:
      "NYC Open Data temporarily limited our requests. Nothing is wrong " +
      "with your input. Retrying shortly is safe.",
  },
  source_unavailable: {
    title: "The official data source is unavailable",
    body:
      "NYC Open Data could not be reached after several attempts. Nothing " +
      "is wrong with your input. Retrying is safe.",
  },
  timeout: {
    title: "The official data source timed out",
    body:
      "NYC Open Data did not respond in time. Nothing is wrong with your " +
      "input. Retrying is safe.",
  },
  schema_drift: {
    title: "The official dataset changed shape",
    body:
      "The official dataset no longer matches its recorded contract. This " +
      "needs platform attention (it is not a temporary outage). You may " +
      "retry, but the result will likely be the same until the platform " +
      "connector is updated.",
  },
};

export function UpstreamFailureState({
  outcome,
  onRetry,
}: {
  outcome: UpstreamFailureOutcome;
  onRetry: () => void;
}) {
  const copy = UPSTREAM_COPY[outcome.state];
  return (
    <section className="card failure-state" data-testid={`state-${outcome.state}`}>
      <h2 className="failure-title">{copy.title}</h2>
      <p>{copy.body}</p>
      <p className="failure-meta">
        Failure type: <code>{outcome.state}</code> (HTTP {outcome.httpStatus})
      </p>
      <RetryButton onRetry={onRetry} />
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

export function InternalErrorState({
  outcome,
  onRetry,
}: {
  outcome: InternalErrorOutcome;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="state-internal-error">
      <h2 className="failure-title">Something went wrong on our side</h2>
      <p>
        The platform hit an unexpected internal error. Your input was fine.
        The reference id below identifies this exact failure in the server
        logs.
      </p>
      <RetryButton onRetry={onRetry} />
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

export function NetworkErrorState({
  outcome,
  onRetry,
}: {
  outcome: NetworkErrorOutcome;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="state-network-error">
      <h2 className="failure-title">Could not reach the platform API</h2>
      <p>{outcome.message}</p>
      <RetryButton onRetry={onRetry} />
    </section>
  );
}

export function UnexpectedResponseState({
  outcome,
  onRetry,
}: {
  outcome: UnexpectedResponseOutcome;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="state-unexpected-response">
      <h2 className="failure-title">Unexpected response from the platform API</h2>
      <p>
        The API returned HTTP {outcome.httpStatus} without a recognized
        machine-readable state. This is not a &quot;property not found&quot;
        result — it is an unexpected condition worth reporting.
      </p>
      <RetryButton onRetry={onRetry} />
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}
