"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type FormEvent,
  type ReactNode,
} from "react";
import { announcementForAddressOutcome } from "@/lib/announce";
import {
  resolveAddress,
  type AddressDocumentOutcome,
  type AddressDocumentView,
  type AddressErrorOutcome,
  type AddressErrorState,
  type AddressOutcome,
  type AddressQuery,
} from "@/lib/address-api";
import { OutcomeAnnouncer } from "@/components/property/OutcomeAnnouncer";
import {
  AddressForm,
  EMPTY_ADDRESS_FORM,
  type AddressFormValues,
} from "./AddressForm";
import { SuggestionChooser } from "./SuggestionChooser";

/**
 * Address entry + resolution outcomes (task M5-T015, Packet 1 of the
 * address-entry/confirm design spec). A deliberate near-clone of the
 * PropertyLookup state machine — same AbortController + monotonic
 * requestSeq guard, same [data-outcome-heading] focus move, same retryFocus
 * hand-off to the loading card, same single persistent OutcomeAnnouncer
 * (its own live region via testId, the M4-T005 coexistence pattern).
 *
 * Branching is on `document.status` for the 200 family (never on field
 * presence) and on the typed error state for the non-200 family — both
 * already discriminated and BOUNDED by src/lib/address-api.ts. This screen
 * never calculates, never normalizes an address, never picks a suggestion
 * (docs/PRODUCT_FLOW_AND_AI_BOUNDARIES.md).
 *
 * Packet boundary: `resolved` renders a STUB handoff (the Address Confirm
 * card, ZoLa link, and /property/confirm handoff are Packet 2). The stub
 * says so explicitly rather than pretending to continue.
 */

interface ResolutionResult {
  query: AddressQuery;
  outcome: AddressOutcome;
}

/* ---------------------------------------------------------------- *
 * Failure primitives — exact idiom clones of FailureState.tsx's
 * module-private FailureTitle/Meta/RetryButton (that file is owned by the
 * property flow and deliberately untouched here; the primitives are three
 * small, stable elements and the shared test contract is the DOM shape:
 * failure-title + data-outcome-heading, data-testid="correlation-id").
 * ---------------------------------------------------------------- */

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

/** Loading card. LoadingStages is BBL-lookup copy, so the address flow has
 * its own minimal equivalent with the same focus contract: on a retry the
 * failure card (and its Retry button) unmounts, so this card takes focus
 * rather than letting it drop to <body>. */
function ResolvingCard({ focusOnMount }: { focusOnMount: boolean }) {
  const headingRef = useRef<HTMLHeadingElement | null>(null);
  useEffect(() => {
    if (focusOnMount) headingRef.current?.focus();
  }, [focusOnMount]);
  return (
    <section className="card" aria-busy="true" data-testid="address-resolving">
      <h2 className="section-title" tabIndex={-1} ref={headingRef}>
        Resolving address…
      </h2>
      <p className="section-note">
        Asking the city&apos;s Geoclient service for the official record.
        Nothing is guessed on this side.
      </p>
    </section>
  );
}

/* ---------------------------------------------------------------- *
 * 200-family cards (branch on document.status)
 * ---------------------------------------------------------------- */

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

function ResolvedCard({ outcome }: { outcome: AddressDocumentOutcome }) {
  const view = outcome.view;
  const line = [
    [view.inputEcho.houseNumber, view.canonical.streetNameNormalized]
      .filter(Boolean)
      .join(" "),
    view.canonical.boroughName,
  ]
    .filter(Boolean)
    .join(", ");
  return (
    <section className="card" data-testid="address-resolved">
      <h2 className="section-title" tabIndex={-1} data-outcome-heading>
        Address resolved to a single lot
      </h2>
      {line ? (
        <p data-testid="resolved-address">
          {line}
          {view.canonical.zipCode ? ` ${view.canonical.zipCode}` : ""}
        </p>
      ) : (
        <p className="section-note">
          The city resolved this address but returned no printable
          normalized street — the lot identifier below is the result.
        </p>
      )}
      {view.status === "resolved_with_warnings" ? (
        <div
          className="completeness-banner"
          role="status"
          data-testid="address-warnings"
        >
          <p>
            The city resolved this address but attached warnings. They are
            shown exactly as received; they do not block continuing.
          </p>
          {view.grcMessage ? (
            <p data-testid="warning-grc-message">{view.grcMessage}</p>
          ) : null}
          {view.grc2Message ? (
            <p data-testid="warning-grc2-message">{view.grc2Message}</p>
          ) : null}
          <p className="failure-meta">
            Geosupport return codes: <code>{view.grc ?? "none"}</code> /{" "}
            <code>{view.grc2 ?? "none"}</code>
          </p>
        </div>
      ) : null}
      {view.canonical.bbl ? (
        <p>
          Tax lot (BBL):{" "}
          <code data-testid="resolved-bbl">{view.canonical.bbl}</code>
          {view.canonical.bin ? (
            <>
              {" "}
              · building (BIN) <code>{view.canonical.bin}</code>
            </>
          ) : null}
        </p>
      ) : (
        <p className="section-note" data-testid="resolved-bbl-absent">
          The city&apos;s answer did not include a lot identifier that passed
          canonical validation, so no BBL is shown.
        </p>
      )}
      {view.sourceFactsNotEmittedReason ? (
        <p className="failure-meta" data-testid="facts-withheld">
          {view.sourceFactsNotEmittedReason}
        </p>
      ) : null}
      {/* Packet-2 handoff point: the Address Confirm card ("is this the
          right lot?"), ZoLa link, and /property/confirm handoff arrive in
          the next increment. An honest stub — disabled, and it says why. */}
      <button
        type="button"
        className="primary-button"
        disabled
        data-testid="stub-continue"
      >
        Continue with this lot (arrives with the confirm-screen increment)
      </button>
      <p className="section-note" data-testid="address-resolved-stub">
        The confirmation step (&quot;is this the right lot?&quot;) ships in
        the next increment. Until then, use the BBL above with the BBL
        lookup on this page — it reaches the same official profile.
      </p>
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

function AmbiguousCard({
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

function NotFoundCard({
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

function RejectedCard({
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

function UnrecognizedStatusCard({
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

function AddressErrorCard({
  outcome,
  onRetry,
}: {
  outcome: AddressErrorOutcome;
  onRetry: () => void;
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
      {copy.retry ? <RetryButton onRetry={onRetry} /> : null}
      <Meta correlationId={outcome.correlationId} />
    </section>
  );
}

/* ---------------------------------------------------------------- *
 * Client-transport cards (no HTTP document arrived)
 * ---------------------------------------------------------------- */

function AddressNetworkErrorCard({
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

function AddressClientTimeoutCard({
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

function AddressUnexpectedResponseCard({
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

/* ---------------------------------------------------------------- *
 * The screen
 * ---------------------------------------------------------------- */

export function AddressResolutionScreen() {
  const [values, setValues] = useState<AddressFormValues>(EMPTY_ADDRESS_FORM);
  /** Query currently being resolved, or null when nothing is in flight. */
  const [loadingQuery, setLoadingQuery] = useState<AddressQuery | null>(null);
  /** Last completed resolution — survives a later inert submit (D5). */
  const [result, setResult] = useState<ResolutionResult | null>(null);
  /** True only between a Retry activation and its outcome (D1 focus). */
  const [retryFocus, setRetryFocus] = useState(false);
  // Monotonic id + abort controller: a stale response can never overwrite
  // a newer resolution, and superseded requests are actively cancelled.
  const requestSeq = useRef(0);
  const abortRef = useRef<AbortController | null>(null);
  /** Wraps the rendered outcome; arrival focus queries inside it (D1). */
  const outcomeRef = useRef<HTMLDivElement | null>(null);
  const streetInputRef = useRef<HTMLInputElement | null>(null);

  // Cancel any in-flight request on unmount.
  useEffect(() => () => abortRef.current?.abort(), []);

  // D1: after an outcome arrives, move focus to the outcome heading.
  // `result` changes ONLY on arrival (an inert submit never calls
  // setResult), so this can never steal focus mid-form-edit.
  useEffect(() => {
    if (result) {
      outcomeRef.current
        ?.querySelector<HTMLElement>("[data-outcome-heading]")
        ?.focus();
    }
  }, [result]);

  const runResolve = useCallback(async (query: AddressQuery) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    const seq = ++requestSeq.current;
    setLoadingQuery(query);
    const outcome = await resolveAddress(query, { signal: controller.signal });
    if (requestSeq.current !== seq || outcome.kind === "aborted") {
      // Superseded: the newer resolution owns the screen.
      return;
    }
    setLoadingQuery(null);
    setRetryFocus(false);
    setResult({ query, outcome });
  }, []);

  const onSubmit = useCallback(
    (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      if (values.houseNumber.trim() === "" && values.street.trim() === "") {
        // The submit button is inert in this state; this guard only makes
        // the same UX nicety deterministic under programmatic submits. It
        // is NOT validation — any non-blank input goes to the connector.
        return;
      }
      void runResolve({
        houseNumber: values.houseNumber,
        street: values.street,
        borough: values.borough === "" ? null : values.borough,
        zip: values.zip === "" ? null : values.zip,
      });
    },
    [values, runResolve],
  );

  const onPickSuggestion = useCallback(
    (rawStreetName: string) => {
      const base = result?.query;
      if (!base) return;
      // The connector's re-query contract: the chosen suggestion's
      // street_name VERBATIM as the new street; same house number, same
      // borough/zip. The form mirrors the pick so what was submitted is
      // visible (and editable) in the street field.
      setValues((current) => ({ ...current, street: rawStreetName }));
      void runResolve({ ...base, street: rawStreetName });
    },
    [result, runResolve],
  );

  const retry = useCallback(() => {
    if (result) {
      // D1: the Retry button is about to unmount with the failure card;
      // the loading card takes focus so it never drops to <body>.
      setRetryFocus(true);
      void runResolve(result.query);
    }
  }, [result, runResolve]);

  const editAddress = useCallback(() => {
    streetInputRef.current?.focus();
  }, []);

  // D1: the single outcome announcement — cleared while resolving so a
  // repeated identical outcome (e.g. retry fails the same way) announces.
  const announcement =
    loadingQuery !== null
      ? ""
      : result
        ? announcementForAddressOutcome(result.outcome)
        : "";

  const renderOutcome = (outcome: AddressOutcome): ReactNode => {
    switch (outcome.kind) {
      case "document":
        switch (outcome.view.status) {
          case "resolved":
          case "resolved_with_warnings":
            return <ResolvedCard outcome={outcome} />;
          case "ambiguous":
            return <AmbiguousCard outcome={outcome} onPick={onPickSuggestion} />;
          case "not_found":
            return <NotFoundCard outcome={outcome} onEditAddress={editAddress} />;
          case "rejected":
            return <RejectedCard outcome={outcome} onEditAddress={editAddress} />;
          default:
            return <UnrecognizedStatusCard outcome={outcome} onRetry={retry} />;
        }
      case "error":
        return <AddressErrorCard outcome={outcome} onRetry={retry} />;
      case "network_error":
        return (
          <AddressNetworkErrorCard message={outcome.message} onRetry={retry} />
        );
      case "client_timeout":
        return (
          <AddressClientTimeoutCard
            timeoutMs={outcome.timeoutMs}
            onRetry={retry}
          />
        );
      case "unexpected_response":
        return (
          <AddressUnexpectedResponseCard
            httpStatus={outcome.httpStatus}
            receivedState={outcome.receivedState}
            correlationId={outcome.correlationId}
            onRetry={retry}
          />
        );
      case "aborted":
        // A superseded request has no user-visible meaning.
        return null;
    }
  };

  return (
    <div data-testid="address-resolution-screen">
      <OutcomeAnnouncer message={announcement} testId="address-outcome-announcer" />
      <section className="card">
        <h2 className="section-title">Address lookup</h2>
        <p className="section-note">
          Enter a street address and the city&apos;s official Geoclient
          service resolves it to a tax lot. The city&apos;s service — not
          this screen — decides what the address means.
        </p>
        <AddressForm
          values={values}
          onChange={setValues}
          onSubmit={onSubmit}
          streetInputRef={streetInputRef}
        />
      </section>

      {loadingQuery !== null ? <ResolvingCard focusOnMount={retryFocus} /> : null}

      <div ref={outcomeRef}>
        {loadingQuery === null && result ? renderOutcome(result.outcome) : null}
      </div>
    </div>
  );
}
