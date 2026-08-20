import type { ReactNode } from "react";
import type {
  ScenarioClientTimeoutOutcome,
  ScenarioInternalErrorOutcome,
  ScenarioNetworkErrorOutcome,
  ScenarioNoMatchOutcome,
  ScenarioOutcome,
  ScenarioServerContractErrorOutcome,
  ScenarioUnexpectedResponseOutcome,
  ScenarioUpstreamFailureOutcome,
  ScenarioValidationErrorOutcome,
  ScenarioValidationFailureOutcome,
} from "@/lib/scenario";

/**
 * The network / server failure states plus the benign feature-unavailable
 * envelope for the draft scenario surface (task M5-T002), mirroring
 * components/rule-evaluation/RuleEvaluationFailure.tsx guarantee-for-guarantee.
 *
 * Every failure here is OPTIONAL-ENRICHMENT failure: the property profile above
 * stays fully usable and is never blocked or unmounted. Recoverable faults carry
 * a Retry that re-issues only the draft-scenario request. No raw backend error
 * dump is shown; all reflected server text arrives already bounded by the client.
 *
 * Headings use `data-scenario-heading` (NOT the profile's `data-outcome-heading`)
 * so this optional surface never competes with the property-profile focus flow;
 * the single scenario live region (the panel's OutcomeAnnouncer) emits the one
 * assistive announcement.
 */

function FailureTitle({ children, testId }: { children: ReactNode; testId: string }) {
  return (
    <h3 className="failure-title" data-testid={testId} data-scenario-heading tabIndex={-1}>
      {children}
    </h3>
  );
}

function Meta({ correlationId }: { correlationId: string | null }) {
  if (!correlationId) return null;
  return (
    <p className="failure-meta">
      Reference id for support and server logs:{" "}
      <code data-testid="scenario-correlation-id">{correlationId}</code>
    </p>
  );
}

function RetryButton({ onRetry }: { onRetry: () => void }) {
  return (
    <button type="button" className="secondary-button" onClick={onRetry}>
      Retry draft scenario
    </button>
  );
}

function FeatureUnavailable() {
  return (
    <section className="card" data-testid="scenario-state-feature_unavailable">
      <FailureTitle testId="scenario-title-feature_unavailable">
        Draft scenario is not available here
      </FailureTitle>
      <p>
        The draft scenario service is not enabled in this environment. The property
        profile above is complete and unaffected — this section simply has nothing to
        add right now.
      </p>
    </section>
  );
}

function NoMatch({ outcome }: { outcome: ScenarioNoMatchOutcome }) {
  return (
    <section className="card" data-testid="scenario-state-no_match">
      <FailureTitle testId="scenario-title-no_match">No record to build a scenario from</FailureTitle>
      <p>{outcome.message}</p>
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

function ValidationError({ outcome }: { outcome: ScenarioValidationErrorOutcome }) {
  return (
    <section className="card failure-state" data-testid="scenario-state-validation_error">
      <FailureTitle testId="scenario-title-validation_error">
        The scenario service rejected this BBL
      </FailureTitle>
      <p>{outcome.message}</p>
      <p className="failure-meta">
        Rejection code: <code>{outcome.code}</code>
      </p>
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

const UPSTREAM_COPY: Record<
  ScenarioUpstreamFailureOutcome["state"],
  { title: string; body: string }
> = {
  rate_limited: {
    title: "The official data source is throttling requests",
    body:
      "The draft scenario could not be produced because NYC Open Data temporarily limited " +
      "our requests. The property profile is unaffected; retrying shortly is safe.",
  },
  source_unavailable: {
    title: "The official data source is unavailable",
    body:
      "NYC Open Data could not be reached to produce the draft scenario. The property profile " +
      "is unaffected; retrying is safe.",
  },
  timeout: {
    title: "The official data source timed out",
    body:
      "NYC Open Data did not respond in time for the draft scenario. The property profile is " +
      "unaffected; retrying is safe.",
  },
  schema_drift: {
    title: "The official dataset changed shape",
    body:
      "The draft scenario could not run because the official dataset no longer matches its " +
      "recorded contract. This needs platform attention; the property profile is unaffected.",
  },
};

function UpstreamFailure({
  outcome,
  onRetry,
}: {
  outcome: ScenarioUpstreamFailureOutcome;
  onRetry: () => void;
}) {
  const copy = UPSTREAM_COPY[outcome.state];
  return (
    <section className="card failure-state" data-testid={`scenario-state-${outcome.state}`}>
      <FailureTitle testId={`scenario-title-${outcome.state}`}>{copy.title}</FailureTitle>
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
  outcome: ScenarioInternalErrorOutcome;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="scenario-state-internal_error">
      <FailureTitle testId="scenario-title-internal_error">
        The draft scenario hit an internal error
      </FailureTitle>
      <p>
        The platform hit an unexpected internal error while producing the draft scenario. Your
        input was fine and the property profile above is unaffected. The reference id below
        identifies this exact failure in the server logs.
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
  outcome: ScenarioServerContractErrorOutcome;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="scenario-state-server_contract_error">
      <FailureTitle testId="scenario-title-server_contract_error">
        The server refused to deliver an invalid draft scenario
      </FailureTitle>
      <p>
        The platform built a draft scenario that failed its own contract checks and refused to
        serve it rather than show unreliable data. The property profile is unaffected. This needs
        platform attention; retrying will likely produce the same result until the defect is fixed.
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
  outcome: ScenarioValidationFailureOutcome;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="scenario-state-validation_failure">
      <FailureTitle testId="scenario-title-validation_failure">
        The draft scenario did not match the published data contract
      </FailureTitle>
      <p>
        The service returned a draft document that failed this screen&apos;s contract validation.
        Nothing from that response is shown — displaying data that fails validation could be
        misleading. The property profile is unaffected.
      </p>
      {outcome.problems.length > 0 ? (
        <details className="provenance-details">
          <summary>Validation problems ({outcome.problems.length}, bounded)</summary>
          <div className="provenance-body">
            <ul className="missing-list" data-testid="scenario-validation-problems">
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
  outcome: ScenarioNetworkErrorOutcome;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="scenario-state-network_error">
      <FailureTitle testId="scenario-title-network_error">
        Could not reach the draft-scenario service
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
  outcome: ScenarioClientTimeoutOutcome;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="scenario-state-client_timeout">
      <FailureTitle testId="scenario-title-client_timeout">
        The draft scenario took too long
      </FailureTitle>
      <p>
        The service did not answer within {Math.round(outcome.timeoutMs / 1000)} seconds, so the
        request was cancelled. The property profile above is unaffected and no partial data is
        shown. Retrying is safe.
      </p>
      <RetryButton onRetry={onRetry} />
    </section>
  );
}

function UnexpectedResponse({
  outcome,
  onRetry,
}: {
  outcome: ScenarioUnexpectedResponseOutcome;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="scenario-state-unexpected_response">
      <FailureTitle testId="scenario-title-unexpected_response">
        Unexpected response from the draft-scenario service
      </FailureTitle>
      <p>
        The service returned HTTP {outcome.httpStatus}
        {outcome.receivedState ? (
          <>
            {" "}with body state{" "}
            <code data-testid="scenario-unexpected-state">{outcome.receivedState}</code>, which is
            not a documented pairing
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
 * Renders every non-`scenario` scenario outcome. `aborted` renders nothing (a
 * superseded request has no user-visible meaning — the newer lookup owns the
 * surface).
 */
export function ScenarioFailure({
  outcome,
  onRetry,
}: {
  outcome: Exclude<ScenarioOutcome, { kind: "scenario" }>;
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
