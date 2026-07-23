import type { ReactNode } from "react";
import type {
  RuleClientTimeoutOutcome,
  RuleEvaluationOutcome,
  RuleInternalErrorOutcome,
  RuleNetworkErrorOutcome,
  RuleNoMatchOutcome,
  RuleServerContractErrorOutcome,
  RuleUnexpectedResponseOutcome,
  RuleUpstreamFailureOutcome,
  RuleValidationErrorOutcome,
  RuleValidationFailureOutcome,
} from "@/lib/rule-evaluation";

/**
 * The SIXTH rule-evaluation UI state — network / server failure — plus the
 * benign feature-unavailable and result envelopes (task M4-T005 phase 3).
 *
 * Every failure here is OPTIONAL-ENRICHMENT failure: the property profile
 * above stays fully usable and is never blocked or unmounted. Recoverable
 * faults carry a Retry that re-issues only the draft-evaluation request. No raw
 * backend error dump is shown; all reflected server text arrives already
 * bounded by the client.
 *
 * Headings use `data-rule-eval-heading` (NOT the profile's
 * `data-outcome-heading`) so this optional surface never competes with the
 * property-profile focus flow; the single rule-eval live region (the panel's
 * OutcomeAnnouncer) emits the one assistive announcement.
 */

function FailureTitle({ children, testId }: { children: ReactNode; testId: string }) {
  return (
    <h3
      className="failure-title"
      data-testid={testId}
      data-rule-eval-heading
      tabIndex={-1}
    >
      {children}
    </h3>
  );
}

function Meta({ correlationId }: { correlationId: string | null }) {
  if (!correlationId) return null;
  return (
    <p className="failure-meta">
      Reference id for support and server logs:{" "}
      <code data-testid="rule-eval-correlation-id">{correlationId}</code>
    </p>
  );
}

function RetryButton({ onRetry }: { onRetry: () => void }) {
  return (
    <button type="button" className="secondary-button" onClick={onRetry}>
      Retry draft evaluation
    </button>
  );
}

function FeatureUnavailable() {
  return (
    <section className="card" data-testid="rule-eval-state-feature_unavailable">
      <FailureTitle testId="rule-eval-title-feature_unavailable">
        Draft rule evaluation is not available here
      </FailureTitle>
      <p>
        The draft rule-evaluation service is not enabled in this environment. The
        property profile above is complete and unaffected — this section simply has
        nothing to add right now.
      </p>
    </section>
  );
}

function NoMatch({ outcome }: { outcome: RuleNoMatchOutcome }) {
  return (
    <section className="card" data-testid="rule-eval-state-no_match">
      <FailureTitle testId="rule-eval-title-no_match">
        No record to evaluate
      </FailureTitle>
      <p>{outcome.message}</p>
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

function ValidationError({ outcome }: { outcome: RuleValidationErrorOutcome }) {
  return (
    <section className="card failure-state" data-testid="rule-eval-state-validation_error">
      <FailureTitle testId="rule-eval-title-validation_error">
        The evaluation service rejected this BBL
      </FailureTitle>
      <p>{outcome.message}</p>
      <p className="failure-meta">
        Rejection code: <code>{outcome.code}</code>
      </p>
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

const UPSTREAM_COPY: Record<RuleUpstreamFailureOutcome["state"], { title: string; body: string }> = {
  rate_limited: {
    title: "The official data source is throttling requests",
    body:
      "The draft evaluation could not be produced because NYC Open Data temporarily " +
      "limited our requests. The property profile is unaffected; retrying shortly is safe.",
  },
  source_unavailable: {
    title: "The official data source is unavailable",
    body:
      "NYC Open Data could not be reached to produce the draft evaluation. The property " +
      "profile is unaffected; retrying is safe.",
  },
  timeout: {
    title: "The official data source timed out",
    body:
      "NYC Open Data did not respond in time for the draft evaluation. The property " +
      "profile is unaffected; retrying is safe.",
  },
  schema_drift: {
    title: "The official dataset changed shape",
    body:
      "The draft evaluation could not run because the official dataset no longer matches " +
      "its recorded contract. This needs platform attention; the property profile is unaffected.",
  },
};

function UpstreamFailure({
  outcome,
  onRetry,
}: {
  outcome: RuleUpstreamFailureOutcome;
  onRetry: () => void;
}) {
  const copy = UPSTREAM_COPY[outcome.state];
  return (
    <section className="card failure-state" data-testid={`rule-eval-state-${outcome.state}`}>
      <FailureTitle testId={`rule-eval-title-${outcome.state}`}>{copy.title}</FailureTitle>
      <p>{copy.body}</p>
      <p className="failure-meta">
        Failure type: <code>{outcome.state}</code> (HTTP {outcome.httpStatus})
      </p>
      <RetryButton onRetry={onRetry} />
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

function InternalError({
  outcome,
  onRetry,
}: {
  outcome: RuleInternalErrorOutcome;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="rule-eval-state-internal_error">
      <FailureTitle testId="rule-eval-title-internal_error">
        The draft evaluation hit an internal error
      </FailureTitle>
      <p>
        The platform hit an unexpected internal error while producing the draft
        evaluation. Your input was fine and the property profile above is unaffected.
        The reference id below identifies this exact failure in the server logs.
      </p>
      <RetryButton onRetry={onRetry} />
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

function ServerContractError({
  outcome,
  onRetry,
}: {
  outcome: RuleServerContractErrorOutcome;
  onRetry: () => void;
}) {
  return (
    <section
      className="card failure-state"
      data-testid="rule-eval-state-server_contract_error"
    >
      <FailureTitle testId="rule-eval-title-server_contract_error">
        The server refused to deliver an invalid draft evaluation
      </FailureTitle>
      <p>
        The platform built a draft evaluation that failed its own contract checks and
        refused to serve it rather than show unreliable data. The property profile is
        unaffected. This needs platform attention; retrying will likely produce the
        same result until the defect is fixed.
      </p>
      <RetryButton onRetry={onRetry} />
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

function ValidationFailure({
  outcome,
  onRetry,
}: {
  outcome: RuleValidationFailureOutcome;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="rule-eval-state-validation_failure">
      <FailureTitle testId="rule-eval-title-validation_failure">
        The draft evaluation did not match the published data contract
      </FailureTitle>
      <p>
        The service returned a draft document that failed this screen&apos;s contract
        validation. Nothing from that response is shown — displaying data that fails
        validation could be misleading. The property profile is unaffected.
      </p>
      {outcome.problems.length > 0 ? (
        <details className="provenance-details">
          <summary>Validation problems ({outcome.problems.length}, bounded)</summary>
          <div className="provenance-body">
            <ul className="missing-list" data-testid="rule-eval-validation-problems">
              {outcome.problems.map((problem) => (
                <li key={problem}>{problem}</li>
              ))}
            </ul>
          </div>
        </details>
      ) : null}
      <RetryButton onRetry={onRetry} />
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

function NetworkError({
  outcome,
  onRetry,
}: {
  outcome: RuleNetworkErrorOutcome;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="rule-eval-state-network_error">
      <FailureTitle testId="rule-eval-title-network_error">
        Could not reach the draft-evaluation service
      </FailureTitle>
      <p>{outcome.message}</p>
      <RetryButton onRetry={onRetry} />
    </section>
  );
}

function ClientTimeout({
  outcome,
  onRetry,
}: {
  outcome: RuleClientTimeoutOutcome;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="rule-eval-state-client_timeout">
      <FailureTitle testId="rule-eval-title-client_timeout">
        The draft evaluation took too long
      </FailureTitle>
      <p>
        The service did not answer within {Math.round(outcome.timeoutMs / 1000)} seconds,
        so the request was cancelled. The property profile above is unaffected and no
        partial data is shown. Retrying is safe.
      </p>
      <RetryButton onRetry={onRetry} />
    </section>
  );
}

function UnexpectedResponse({
  outcome,
  onRetry,
}: {
  outcome: RuleUnexpectedResponseOutcome;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="rule-eval-state-unexpected_response">
      <FailureTitle testId="rule-eval-title-unexpected_response">
        Unexpected response from the draft-evaluation service
      </FailureTitle>
      <p>
        The service returned HTTP {outcome.httpStatus}
        {outcome.receivedState ? (
          <>
            {" "}with body state{" "}
            <code data-testid="rule-eval-unexpected-state">{outcome.receivedState}</code>, which
            is not a documented pairing
          </>
        ) : (
          " without a recognized machine-readable state"
        )}
        . The response body was not trusted or rendered, and the property profile is unaffected.
      </p>
      <RetryButton onRetry={onRetry} />
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

/**
 * Renders every non-`evaluation` rule-eval outcome. `aborted` renders nothing
 * (a superseded request has no user-visible meaning — the newer lookup owns
 * the surface).
 */
export function RuleEvaluationFailure({
  outcome,
  onRetry,
}: {
  outcome: Exclude<RuleEvaluationOutcome, { kind: "evaluation" }>;
  onRetry: () => void;
}) {
  switch (outcome.kind) {
    case "feature_unavailable":
      return <FeatureUnavailable />;
    case "no_match":
      return <NoMatch outcome={outcome} />;
    case "validation_error":
      return <ValidationError outcome={outcome} />;
    case "upstream_failure":
      return <UpstreamFailure outcome={outcome} onRetry={onRetry} />;
    case "internal_error":
      return <InternalError outcome={outcome} onRetry={onRetry} />;
    case "server_contract_error":
      return <ServerContractError outcome={outcome} onRetry={onRetry} />;
    case "validation_failure":
      return <ValidationFailure outcome={outcome} onRetry={onRetry} />;
    case "network_error":
      return <NetworkError outcome={outcome} onRetry={onRetry} />;
    case "client_timeout":
      return <ClientTimeout outcome={outcome} onRetry={onRetry} />;
    case "unexpected_response":
      return <UnexpectedResponse outcome={outcome} onRetry={onRetry} />;
    case "aborted":
      return null;
  }
}
