"use client";

import type { ReactNode } from "react";
import type {
  AddressDocumentOutcome,
  AddressDocumentView,
  AddressErrorOutcome,
  AddressErrorState,
} from "@/lib/address-api";
import { SuggestionChooser } from "./SuggestionChooser";

/**
 * Address outcome/error cards (task M5-T016, extracted BYTE-PRESERVING from
 * AddressResolutionScreen.tsx per the M5-T015 G3 F4 concurrence — the host
 * screen keeps the state machine, this module keeps the presentation table).
 * Every card's markup, copy, testids, and behavior are the accepted
 * M5-T015 content; only module boundaries moved. The resolved/
 * resolved_with_warnings treatment lives in AddressConfirmCard.tsx (the
 * Packet-2 confirm card that replaced the Packet-1 stub).
 *
 * Failure primitives below are exact idiom clones of FailureState.tsx's
 * module-private FailureTitle/Meta/RetryButton (that file is owned by the
 * property flow and deliberately untouched; the shared test contract is the
 * DOM shape: failure-title + data-outcome-heading,
 * data-testid="correlation-id").
 */

function FailureTitle({ children }: { children: ReactNode }) {
  return (
    <h2 className="failure-title" tabIndex={-1} data-outcome-heading>
      {children}
    </h2>
  );
}

export function Meta({ correlationId }: { correlationId: string | null }) {
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
      Retry address lookup
    </button>
  );
}

/** What the user typed, echoed back as inert text (input_echo is a named
 * unsanitized reflected surface — bounded upstream, text nodes only). */
function EchoLine({ view }: { view: AddressDocumentView }) {
  const echo = view.inputEcho;
  const address = [echo.houseNumber, echo.street].filter(Boolean).join(" ");
  const area = echo.borough ?? echo.zip;
  if (!address && !area) return null;
  return (
    <p data-testid="input-echo">
      You entered: {address}
      {area ? ` (${area})` : ""}
    </p>
  );
}

/** Both Geosupport return codes + messages, never just one, never hidden
 * (design spec section 2: not_found / rejected honesty rules). */
function GrcLines({ view }: { view: AddressDocumentView }) {
  return (
    <div className="failure-meta">
      <p data-testid="grc-line">
        Geosupport return code: <code>{view.grc ?? "none"}</code>
        {view.grcMessage ? <> — {view.grcMessage}</> : null}
      </p>
      <p data-testid="grc2-line">
        Second return code: <code>{view.grc2 ?? "none"}</code>
        {view.grc2Message ? <> — {view.grc2Message}</> : null}
      </p>
    </div>
  );
}

/** Recovery affordances shared by not_found / rejected: never a dead end.
 * The BBL link is a constant fragment href (the BBL form on the same page)
 * — no reflected value is ever placed in a URL context. */
function RecoveryActions({ onEditAddress }: { onEditAddress: () => void }) {
  return (
    <p>
      <button
        type="button"
        className="secondary-button"
        onClick={onEditAddress}
        data-testid="edit-address"
      >
        Edit the address
      </button>{" "}
      <a className="secondary-button" href="#bbl-input" data-testid="bbl-instead">
        Look up by BBL instead
      </a>
    </p>
  );
}

export function AmbiguousCard({
  outcome,
  onPick,
}: {
  outcome: AddressDocumentOutcome;
  onPick: (rawStreetName: string) => void;
}) {
  return (
    <section className="card" data-testid="address-ambiguous">
      <h2 className="section-title" tabIndex={-1} data-outcome-heading>
        Which of these did you mean?
      </h2>
      <p className="section-note">
        The city&apos;s address service returned more than one possible
        match. Choose the correct one — the platform will not guess for you.
      </p>
      <SuggestionChooser suggestions={outcome.view.suggestions} onPick={onPick} />
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

export function NotFoundCard({
  outcome,
  onEditAddress,
}: {
  outcome: AddressDocumentOutcome;
  onEditAddress: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="address-not-found">
      <FailureTitle>No matching address in the city&apos;s records</FailureTitle>
      <p>
        The city&apos;s address service has no record matching what you
        entered. This is an answer from the official source, not a system
        failure.
      </p>
      <EchoLine view={outcome.view} />
      <GrcLines view={outcome.view} />
      <RecoveryActions onEditAddress={onEditAddress} />
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

export function RejectedCard({
  outcome,
  onEditAddress,
}: {
  outcome: AddressDocumentOutcome;
  onEditAddress: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="address-rejected">
      <FailureTitle>
        The city&apos;s address service rejected this address
      </FailureTitle>
      <p>
        The service judged this address unresolvable as entered. The reasons
        below are the source&apos;s own, shown exactly as received.
      </p>
      <EchoLine view={outcome.view} />
      <GrcLines view={outcome.view} />
      <RecoveryActions onEditAddress={onEditAddress} />
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

export function UnrecognizedStatusCard({
  outcome,
  onRetry,
}: {
  outcome: AddressDocumentOutcome;
  onRetry: () => void;
}) {
  return (
    <section
      className="card failure-state"
      data-testid="address-unrecognized-status"
    >
      <FailureTitle>
        The city&apos;s service answered in a form this platform does not
        recognize
      </FailureTitle>
      <p>
        The response was not trusted or interpreted, and it was NOT treated
        as &quot;address not found&quot;. This is an unexpected condition
        worth reporting.
      </p>
      <p className="failure-meta">
        Reported status:{" "}
        <code data-testid="unrecognized-status">{outcome.view.statusToken}</code>
      </p>
      <RetryButton onRetry={onRetry} />
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

/* ---------------------------------------------------------------- *
 * Error-matrix cards (typed non-200 states; design spec section 2 table)
 * ---------------------------------------------------------------- */

const ADDRESS_ERROR_COPY: Record<
  AddressErrorState,
  { title: string; body: string; retry: boolean }
> = {
  invalid_input: {
    title: "That address can't be read yet",
    // The connector's own message renders as the specific reason (it is
    // the single validation authority); this body is the fallback frame.
    body: "",
    retry: false,
  },
  key_missing: {
    title: "Address lookup isn't configured on our side",
    body:
      "The platform is missing its own access credential for the city's " +
      "address service. Nothing is wrong with your input, and retrying " +
      "will not help until the platform side is fixed.",
    retry: false,
  },
  auth_failed: {
    title: "Our access to the city's address service was refused",
    body:
      "The city's service refused the platform's credential. This is a " +
      "server-side problem, not your input. It may be transient — " +
      "retrying is safe.",
    retry: true,
  },
  rate_limited: {
    title: "The city's address service is throttling us",
    body:
      "The city's service temporarily limited the platform's requests. " +
      "Nothing is wrong with your input. Retrying shortly is safe.",
    retry: true,
  },
  source_unavailable: {
    title: "The city's address service is unavailable",
    body:
      "The city's service could not be reached after several attempts. " +
      "Nothing is wrong with your input. Retrying is safe.",
    retry: true,
  },
  timeout: {
    title: "The city's address service timed out",
    body:
      "The city's service did not respond in time. Nothing is wrong with " +
      "your input. Retrying is safe.",
    retry: true,
  },
  malformed_response: {
    title: "The city's address service sent an unreadable response",
    body:
      "The service answered, but not in a form the platform could read " +
      "safely, so nothing from it was trusted. This needs platform " +
      "attention; a retry will likely get the same result.",
    retry: true,
  },
  request_budget_exceeded: {
    title: "The platform's request budget for this lookup ran out",
    // Documented-unreachable from this endpoint (it passes no budget);
    // typed anyway so an arrival renders honestly, never as a surprise.
    body:
      "The platform stopped before finishing this lookup because its own " +
      "per-request budget was exhausted. Nothing is wrong with your " +
      "input. Retrying is safe.",
    retry: true,
  },
  internal_error: {
    title: "Something went wrong on our side",
    body:
      "The platform hit an unexpected internal error. Your input was " +
      "fine. The reference id below identifies this exact failure in the " +
      "server logs.",
    retry: true,
  },
};

export function AddressErrorCard({
  outcome,
  onRetry,
  onEditAddress,
}: {
  outcome: AddressErrorOutcome;
  onRetry: () => void;
  onEditAddress: () => void;
}) {
  const copy = ADDRESS_ERROR_COPY[outcome.state];
  return (
    <section
      className="card failure-state"
      data-testid={`address-error-${outcome.state}`}
    >
      <FailureTitle>{copy.title}</FailureTitle>
      {outcome.state === "invalid_input" ? (
        // The connector is the validation authority: its message IS the
        // specific reason, rendered as inert text (bounded upstream).
        <p data-testid="invalid-input-message">{outcome.message}</p>
      ) : (
        <p>{copy.body}</p>
      )}
      {outcome.state === "rate_limited" && outcome.retryAfter ? (
        <p data-testid="retry-after">
          The service asked us to wait before retrying:{" "}
          <code>{outcome.retryAfter}</code>
        </p>
      ) : null}
      <p className="failure-meta">
        Failure type: <code>{outcome.state}</code> (HTTP {outcome.httpStatus})
      </p>
      {copy.retry ? (
        <RetryButton onRetry={onRetry} />
      ) : outcome.state === "invalid_input" ? (
        // G3 F3: the one error whose fix is on the user's side points back
        // at the form (spec section-2 "edit and resubmit" posture).
        <button
          type="button"
          className="secondary-button"
          onClick={onEditAddress}
          data-testid="edit-address"
        >
          Edit the address
        </button>
      ) : null}
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

/* ---------------------------------------------------------------- *
 * Client-transport cards (no HTTP document arrived)
 * ---------------------------------------------------------------- */

export function AddressNetworkErrorCard({
  message,
  onRetry,
}: {
  message: string;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="address-network-error">
      <FailureTitle>Could not reach the platform API</FailureTitle>
      <p>{message}</p>
      <RetryButton onRetry={onRetry} />
    </section>
  );
}

export function AddressClientTimeoutCard({
  timeoutMs,
  onRetry,
}: {
  timeoutMs: number;
  onRetry: () => void;
}) {
  return (
    <section className="card failure-state" data-testid="address-client-timeout">
      <FailureTitle>The address lookup took too long</FailureTitle>
      <p>
        The platform API did not answer within {Math.round(timeoutMs / 1000)}{" "}
        seconds, so the request was cancelled. Nothing is wrong with your
        input, and no partial result is shown. Retrying is safe.
      </p>
      <RetryButton onRetry={onRetry} />
    </section>
  );
}

export function AddressUnexpectedResponseCard({
  httpStatus,
  receivedState,
  correlationId,
  onRetry,
}: {
  httpStatus: number;
  receivedState: string | null;
  correlationId: string | null;
  onRetry: () => void;
}) {
  return (
    <section
      className="card failure-state"
      data-testid="address-unexpected-response"
    >
      <FailureTitle>Unexpected response from the platform API</FailureTitle>
      <p>
        The API returned HTTP {httpStatus}
        {receivedState ? (
          <>
            {" "}
            with body state{" "}
            <code data-testid="unexpected-state">{receivedState}</code>, which
            is not a documented pairing
          </>
        ) : (
          " without a recognized machine-readable state"
        )}
        . This is not an &quot;address not found&quot; result — the response
        body was not trusted or rendered.
      </p>
      <RetryButton onRetry={onRetry} />
      <Meta correlationId={correlationId} />
    </section>
  );
}
