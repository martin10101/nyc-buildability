import type {
  ClientTimeoutOutcome,
  InternalErrorOutcome,
  LookupOutcome,
  NetworkErrorOutcome,
  NoMatchOutcome,
  ServerContractErrorOutcome,
  UnexpectedResponseOutcome,
  UpstreamFailureOutcome,
  ValidationErrorOutcome,
  ValidationFailureOutcome,
} from "@/lib/api";

/**
 * First-class failure states (tasks M2-T001/M2-T002). Each documented
 * outcome has its own wording: what failed, whether retry is safe, and
 * what the user can do — never a raw backend error dump
 * (docs/PREMIUM_PRODUCT_DESIGN_SYSTEM.md section 12). All reflected server
 * text arrives already bounded by the API client (src/lib/bounded.ts).
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

/**
 * Documented server-side contract refusal (state=internal_contract_error or
 * unsupported_contract_version, task M2-T003): the SERVER declined to ship
 * a profile that failed its own canonical-contract checks. Distinct from a
 * generic 500 so contract breakage is never mistaken for a random defect.
 */
export function ServerContractErrorState({
  outcome,
  onRetry,
}: {
  outcome: ServerContractErrorOutcome;
  onRetry: () => void;
}) {
  return (
    <section
      className="card failure-state"
      data-testid="state-server-contract-error"
    >
      <h2 className="failure-title">
        The server refused to deliver an invalid profile
      </h2>
      <p>
        The platform built a property profile that failed its own contract
        checks, and refused to serve it rather than show unreliable data.
        Your input was fine. This needs platform attention; retrying will
        likely produce the same result until the defect is fixed.
      </p>
      <p className="failure-meta">
        Failure type: <code>{outcome.state}</code>
      </p>
      <RetryButton onRetry={onRetry} />
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

/**
 * CLIENT-side canonical validation failed on a 200 body (scenario S3).
 * Nothing from the invalid payload is rendered — only the bounded problem
 * list, so the mismatch is inspectable without trusting the data.
 */
export function ValidationFailureState({
  outcome,
  onRetry,
}: {
  outcome: ValidationFailureOutcome;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="state-validation-failure">
      <h2 className="failure-title">
        The response did not match the published data contract
      </h2>
      <p>
        The API returned a profile that failed this screen&apos;s contract
        validation. Nothing from that response is shown — displaying data
        that fails validation could be misleading. This needs platform
        attention.
      </p>
      {outcome.problems.length > 0 ? (
        <details className="provenance-details">
          <summary>
            Validation problems ({outcome.problems.length}, bounded)
          </summary>
          <div className="provenance-body">
            <ul className="missing-list" data-testid="validation-problems">
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

/** Client-side request budget elapsed — a recoverable state (S4). */
export function ClientTimeoutState({
  outcome,
  onRetry,
}: {
  outcome: ClientTimeoutOutcome;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="state-client-timeout">
      <h2 className="failure-title">The lookup took too long</h2>
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
        The API returned HTTP {outcome.httpStatus}
        {outcome.receivedState ? (
          <>
            {" "}with body state{" "}
            <code data-testid="unexpected-state">{outcome.receivedState}</code>
            , which is not a documented pairing
          </>
        ) : (
          " without a recognized machine-readable state"
        )}
        . This is not a &quot;property not found&quot; result — it is an
        unexpected condition worth reporting, and the response body was not
        trusted or rendered.
      </p>
      <RetryButton onRetry={onRetry} />
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

/**
 * Shared non-profile outcome switch used by the Property and Confirm
 * screens. `aborted` intentionally renders nothing: a superseded request
 * has no user-visible meaning (the newer lookup owns the screen).
 */
export function OutcomeFailureStates({
  outcome,
  onRetry,
}: {
  outcome: Exclude<LookupOutcome, { kind: "profile" }>;
  onRetry: () => void;
}) {
  switch (outcome.kind) {
    case "no_match":
      return <NoMatchState outcome={outcome} />;
    case "validation_error":
      return <ValidationErrorState outcome={outcome} />;
    case "upstream_failure":
      return <UpstreamFailureState outcome={outcome} onRetry={onRetry} />;
    case "internal_error":
      return <InternalErrorState outcome={outcome} onRetry={onRetry} />;
    case "server_contract_error":
      return <ServerContractErrorState outcome={outcome} onRetry={onRetry} />;
    case "validation_failure":
      return <ValidationFailureState outcome={outcome} onRetry={onRetry} />;
    case "network_error":
      return <NetworkErrorState outcome={outcome} onRetry={onRetry} />;
    case "client_timeout":
      return <ClientTimeoutState outcome={outcome} onRetry={onRetry} />;
    case "aborted":
      return null;
    case "unexpected_response":
      return <UnexpectedResponseState outcome={outcome} onRetry={onRetry} />;
  }
}
