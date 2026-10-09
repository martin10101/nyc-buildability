import type { ReactNode } from "react";
import {
  type ScenarioAbortedOutcome,
  type ScenarioClientTimeoutOutcome,
  type ScenarioInternalErrorOutcome,
  type ScenarioNetworkErrorOutcome,
  type ScenarioNoMatchOutcome,
  type ScenarioOutcome,
  type ScenarioServerContractErrorOutcome,
  type ScenarioUnexpectedResponseOutcome,
  type ScenarioUpstreamFailureOutcome,
  type ScenarioValidationErrorOutcome,
  type ScenarioValidationFailureOutcome,
} from "@/lib/scenario-api";

/**
 * First-class Compare (Step 3) failure / non-document states (task M5-T004).
 *
 * Mirrors src/components/property/FailureState.tsx: every documented scenario
 * outcome has its own honest wording (what failed, whether Retry is safe, what
 * the analyst can do) and NOTHING partial from the response is rendered. All
 * reflected server text arrives already length-capped / control-stripped from
 * the scenario client (src/lib/bounded.ts via scenario-api.ts); the correlation
 * id is token-allowlisted. No raw stack, secret, or invented scenario ever
 * reaches the screen.
 *
 * The single outcome-arrival announcement is emitted by the persistent
 * OutcomeAnnouncer on the CompareScreen — these cards carry NO
 * role="alert"/aria-live, so mounting one can never double-announce (mirrors
 * the property/confirm S1 rule). Each failure title is the deterministic
 * programmatic-focus target (tabIndex -1 + data-outcome-heading).
 */

function FailureTitle({ children }: { children: ReactNode }) {
  return (
    <h2 className="failure-title" tabIndex={-1} data-outcome-heading>
      {children}
    </h2>
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
      Retry compare
    </button>
  );
}

/**
 * The endpoint is flag-gated off (INTERNAL_SCENARIO_ENABLED absent) or
 * unmounted: a generic 404 with no state and no correlation id. Benign — an
 * honest environment note, never an error page (no Retry: retrying cannot turn
 * a disabled feature on).
 */
export function FeatureUnavailableState() {
  return (
    <section className="card failure-state" data-testid="scenario-feature-unavailable">
      <FailureTitle>Scenario comparison is not available here</FailureTitle>
      <p>
        The internal scenario endpoint is not enabled in this environment, so no
        preliminary scenario could be requested. This is an environment note,
        not a failure of your input — nothing was compared, and nothing is wrong
        with the property you selected.
      </p>
    </section>
  );
}

export function ScenarioNoMatchState({ outcome }: { outcome: ScenarioNoMatchOutcome }) {
  return (
    <section className="card failure-state" data-testid="scenario-no-match">
      <FailureTitle>No property record found</FailureTitle>
      <p>
        The BBL{outcome.bbl ? ` ${outcome.bbl}` : ""} is a valid format, but the
        current official dataset has no record for it, so no scenario could be
        built. This is a result from the official source, not a system error.
      </p>
      <p data-testid="scenario-no-match-explanation">{outcome.message}</p>
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

export function ScenarioValidationErrorState({
  outcome,
}: {
  outcome: ScenarioValidationErrorOutcome;
}) {
  return (
    <section className="card failure-state" data-testid="scenario-validation-error">
      <FailureTitle>The API rejected this BBL</FailureTitle>
      <p data-testid="scenario-validation-message">{outcome.message}</p>
      <p className="failure-meta">
        Rejection code:{" "}
        <code data-testid="scenario-validation-code">{outcome.code}</code>
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
      "The official source temporarily limited our requests. Nothing is wrong " +
      "with your input. Retrying shortly is safe.",
  },
  source_unavailable: {
    title: "The official data source is unavailable",
    body:
      "The official source could not be reached after several attempts. " +
      "Nothing is wrong with your input. Retrying is safe.",
  },
  timeout: {
    title: "The official data source timed out",
    body:
      "The official source did not respond in time. Nothing is wrong with " +
      "your input. Retrying is safe.",
  },
  schema_drift: {
    title: "The official dataset changed shape",
    body:
      "The official dataset no longer matches its recorded contract. This " +
      "needs platform attention (it is not a temporary outage). You may retry, " +
      "but the result will likely be the same until the connector is updated.",
  },
};

export function ScenarioUpstreamFailureState({
  outcome,
  onRetry,
}: {
  outcome: ScenarioUpstreamFailureOutcome;
  onRetry: () => void;
}) {
  const copy = UPSTREAM_COPY[outcome.state];
  return (
    <section className="card failure-state" data-testid={`scenario-${outcome.state}`}>
      <FailureTitle>{copy.title}</FailureTitle>
      <p>{copy.body}</p>
      <p className="failure-meta">
        Failure type: <code>{outcome.state}</code> (HTTP {outcome.httpStatus})
      </p>
      <RetryButton onRetry={onRetry} />
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

export function ScenarioInternalErrorState({
  outcome,
  onRetry,
}: {
  outcome: ScenarioInternalErrorOutcome;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="scenario-internal-error">
      <FailureTitle>Something went wrong on our side</FailureTitle>
      <p>
        The platform hit an unexpected internal error while building the
        scenario. Your input was fine. The reference id below identifies this
        exact failure in the server logs.
      </p>
      <RetryButton onRetry={onRetry} />
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

export function ScenarioServerContractErrorState({
  outcome,
  onRetry,
}: {
  outcome: ScenarioServerContractErrorOutcome;
  onRetry: () => void;
}) {
  return (
    <section
      className="card failure-state"
      data-testid="scenario-server-contract-error"
    >
      <FailureTitle>The server refused to deliver an invalid scenario</FailureTitle>
      <p>
        The platform assembled a scenario that failed its own contract checks
        and refused to serve it rather than show unreliable data. Your input was
        fine. This needs platform attention; retrying will likely produce the
        same result until the defect is fixed.
      </p>
      <RetryButton onRetry={onRetry} />
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

/**
 * A 200 body failed CLIENT-side canonical validation (AS-4). Nothing from the
 * invalid payload is rendered — only the bounded problem list, so the mismatch
 * is inspectable without trusting the data.
 */
export function ScenarioValidationFailureState({
  outcome,
  onRetry,
}: {
  outcome: ScenarioValidationFailureOutcome;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="scenario-validation-failure">
      <FailureTitle>The response did not match the published data contract</FailureTitle>
      <p>
        The API returned a scenario that failed this screen&apos;s contract
        validation. Nothing from that response is shown — displaying data that
        fails validation could be misleading. This needs platform attention.
      </p>
      {outcome.problems.length > 0 ? (
        <details className="provenance-details">
          <summary>
            Validation problems ({outcome.problems.length}, bounded)
          </summary>
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

export function ScenarioNetworkErrorState({
  outcome,
  onRetry,
}: {
  outcome: ScenarioNetworkErrorOutcome;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="scenario-network-error">
      <FailureTitle>Could not reach the scenario service</FailureTitle>
      <p>{outcome.message}</p>
      <RetryButton onRetry={onRetry} />
    </section>
  );
}

export function ScenarioClientTimeoutState({
  outcome,
  onRetry,
}: {
  outcome: ScenarioClientTimeoutOutcome;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="scenario-client-timeout">
      <FailureTitle>The scenario took too long</FailureTitle>
      <p>
        The platform API did not answer within{" "}
        {Math.round(outcome.timeoutMs / 1000)} seconds, so the request was
        cancelled. Nothing is wrong with your input, and no partial data is
        shown. Retrying is safe.
      </p>
      <RetryButton onRetry={onRetry} />
    </section>
  );
}

export function ScenarioUnexpectedResponseState({
  outcome,
  onRetry,
}: {
  outcome: ScenarioUnexpectedResponseOutcome;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="scenario-unexpected-response">
      <FailureTitle>Unexpected response from the platform API</FailureTitle>
      <p>
        The API returned HTTP {outcome.httpStatus}
        {outcome.receivedState ? (
          <>
            {" "}with body state{" "}
            <code data-testid="scenario-unexpected-state">
              {outcome.receivedState}
            </code>
            , which is not a documented pairing
          </>
        ) : (
          " without a recognized machine-readable state"
        )}
        . This is not a &quot;no scenario&quot; result — it is an unexpected
        condition worth reporting, and the response body was not trusted or
        rendered.
      </p>
      <RetryButton onRetry={onRetry} />
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

/**
 * Non-document outcome switch. `aborted` (a superseded request) renders
 * nothing: the newer request owns the screen. `scenario` is handled by the
 * CompareScreen success path and never reaches here.
 */
export function ScenarioFailureStates({
  outcome,
  onRetry,
}: {
  outcome: Exclude<ScenarioOutcome, { kind: "scenario" } | ScenarioAbortedOutcome>;
  onRetry: () => void;
}) {
  switch (outcome.kind) {
    case "feature_unavailable":
      return <FeatureUnavailableState />;
    case "no_match":
      return <ScenarioNoMatchState outcome={outcome} />;
    case "validation_error":
      return <ScenarioValidationErrorState outcome={outcome} />;
    case "upstream_failure":
      return <ScenarioUpstreamFailureState outcome={outcome} onRetry={onRetry} />;
    case "internal_error":
      return <ScenarioInternalErrorState outcome={outcome} onRetry={onRetry} />;
    case "server_contract_error":
      return <ScenarioServerContractErrorState outcome={outcome} onRetry={onRetry} />;
    case "validation_failure":
      return <ScenarioValidationFailureState outcome={outcome} onRetry={onRetry} />;
    case "network_error":
      return <ScenarioNetworkErrorState outcome={outcome} onRetry={onRetry} />;
    case "client_timeout":
      return <ScenarioClientTimeoutState outcome={outcome} onRetry={onRetry} />;
    case "unexpected_response":
      return <ScenarioUnexpectedResponseState outcome={outcome} onRetry={onRetry} />;
  }
}
