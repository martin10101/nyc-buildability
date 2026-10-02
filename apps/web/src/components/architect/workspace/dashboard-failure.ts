/**
 * Plan §5a ("Label on the box") failure notices for the single-page dashboard (queue D-03,
 * M1-17). When the property lookup returns no profile at all — a network fault, a timeout, an
 * official-source outage, a refused or malformed response — the dashboard shows one plain notice
 * in place of the results, not the old multi-page failure card.
 *
 * Presentation only. It reclassifies the already-typed, already-bounded `LookupOutcome` the API
 * client returns (`@/lib/api`): it computes no zoning value, fetches nothing, and never decides a
 * legal result. §5a item 5: the face is plain English with no internal codes. §5a item 4: the
 * reference id, HTTP status, rejection code and response state — the codes support needs — move
 * behind a details disclosure. §5 calculation behavior: nothing from an untrusted response is
 * shown; the notice only says what failed and whether another try can help.
 */
import type { LookupOutcome, UpstreamFailureState } from "@/lib/api";

/** Every lookup outcome except the success profile; the dashboard renders this set as notices. */
export type DashboardFailureOutcome = Exclude<LookupOutcome, { kind: "profile" }>;

/** One internal code kept off the face and shown on tap (§5a item 4). */
export interface FailureDetail {
  label: string;
  value: string;
}

export interface DashboardFailureNoticeModel {
  /** Plain heading: what happened, no code. */
  title: string;
  /** Plain explanation, no code. */
  body: string;
  /** One line on what the architect can do, or why this is not an app fault. */
  recovery: string;
  /** Whether another try can help; drives the "Try again" button. */
  retryable: boolean;
  /** Codes support may need, shown only behind the details disclosure. */
  technical: FailureDetail[];
}

// Shared recovery lines, so the same honest promise is worded once.
const RETRY_SAFE = "The property you entered is fine. Trying again is safe.";
const NEEDS_PLATFORM =
  "This needs the platform team. Trying again will likely give the same result until it is fixed.";
const FROM_SOURCE = "This is an answer from the official city source, not an app error.";

function referenceRow(correlationId: string | null): FailureDetail[] {
  return correlationId ? [{ label: "Reference id for support", value: correlationId }] : [];
}

const UPSTREAM_COPY: Record<UpstreamFailureState, { title: string; body: string; recovery: string }> = {
  rate_limited: {
    title: "The city data source is busy right now",
    body: "The official city source temporarily limited the app's requests, so no record came back.",
    recovery: RETRY_SAFE,
  },
  source_unavailable: {
    title: "The city data source could not be reached",
    body: "The official city source did not answer after several tries, so no record came back.",
    recovery: RETRY_SAFE,
  },
  timeout: {
    title: "The city data source took too long",
    body: "The official city source did not respond in time, so no record came back.",
    recovery: RETRY_SAFE,
  },
  schema_drift: {
    title: "The city dataset changed shape",
    body:
      "The official city dataset no longer matches its recorded format, so the app would not " +
      "trust it.",
    recovery: NEEDS_PLATFORM,
  },
};

/**
 * The plain notice for one failed property lookup, or null when the request was superseded
 * (`aborted`): a cancelled request owns no surface, so the newer lookup's state shows instead.
 */
export function dashboardFailureNotice(
  outcome: DashboardFailureOutcome,
): DashboardFailureNoticeModel | null {
  switch (outcome.kind) {
    case "aborted":
      return null;
    case "no_match":
      return {
        title: "No city record for this property",
        body: outcome.bbl
          ? `BBL ${outcome.bbl} is a valid format, but the official city dataset has no record ` +
            `for it. ${outcome.message}`
          : `The official city dataset has no record for this property. ${outcome.message}`,
        recovery: FROM_SOURCE,
        retryable: false,
        technical: referenceRow(outcome.correlationId),
      };
    case "validation_error":
      return {
        title: "The app could not read this property identifier",
        body: outcome.message,
        recovery: "Check the identifier and try another lot.",
        retryable: false,
        technical: [
          { label: "Rejection code", value: outcome.code },
          ...referenceRow(outcome.correlationId),
        ],
      };
    case "upstream_failure": {
      const copy = UPSTREAM_COPY[outcome.state];
      return {
        title: copy.title,
        body: copy.body,
        recovery: copy.recovery,
        retryable: true,
        technical: [
          { label: "Failure type", value: outcome.state },
          { label: "HTTP status", value: String(outcome.httpStatus) },
          ...referenceRow(outcome.correlationId),
        ],
      };
    }
    case "internal_error":
      return {
        title: "Something went wrong on our side",
        body: "The app hit an unexpected problem while loading this property.",
        recovery: RETRY_SAFE,
        retryable: true,
        technical: referenceRow(outcome.correlationId),
      };
    case "server_contract_error":
      return {
        title: "The app would not show unreliable results",
        body:
          "The app built a property record that failed its own quality checks and held it back " +
          "rather than show data it could not trust.",
        recovery: NEEDS_PLATFORM,
        retryable: true,
        technical: [
          { label: "Failure type", value: outcome.state },
          ...referenceRow(outcome.correlationId),
        ],
      };
    case "validation_failure":
      return {
        title: "The results did not match the published data format",
        body:
          "The service returned a property record that failed this screen's format check. " +
          "Nothing from that response is shown.",
        recovery: NEEDS_PLATFORM,
        retryable: true,
        technical: [
          ...outcome.problems.map(problem => ({ label: "Format problem", value: problem })),
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
        title: "The lookup took too long",
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
        body:
          "The service answered in a way the app does not recognize, so the response was not " +
          "trusted or shown. This is worth reporting.",
        recovery: RETRY_SAFE,
        retryable: true,
        technical: [
          { label: "HTTP status", value: String(outcome.httpStatus) },
          ...(outcome.receivedState
            ? [{ label: "Response state", value: outcome.receivedState }]
            : []),
          ...referenceRow(outcome.correlationId),
        ],
      };
  }
}
