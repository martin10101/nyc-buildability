/**
 * Plan §5a ("Label on the box") failure notices for the single-page dashboard's two OPTIONAL
 * analysis enrichments — the scenario comparison and the draft rule evaluation (queue D-03,
 * M1-17). When either enrichment returns no document, the dashboard shows one plain §5a notice in
 * the analysis region instead of hiding the failure behind a `<details>`.
 *
 * Presentation only. It reclassifies the already-typed, already-bounded outcome the scenario and
 * rule-evaluation clients return (`@/lib/scenario-api`, `@/lib/rule-evaluation`): it computes no
 * zoning value, fetches nothing, and never decides a legal result. These are OPTIONAL-ENRICHMENT
 * failures — the property profile above stays complete and usable, so every notice says so. §5a
 * item 5: the face is plain English with no internal codes. §5a item 4: the reference id, HTTP
 * status, rejection code and response state move behind a closed details disclosure.
 *
 * The notice model and its rendering are shared with the property-lookup notice (slice 2): this
 * maps the enrichment outcomes to the same `DashboardFailureNoticeModel`, and the same
 * `FailureNoticeCard` presents it. Only the copy — worded for an optional enrichment — differs.
 */
import type { ScenarioOutcome, ScenarioUpstreamFailureState } from "@/lib/scenario-api";
import type { RuleEvaluationOutcome } from "@/lib/rule-evaluation";
import {
  referenceRow,
  type DashboardFailureNoticeModel,
} from "./dashboard-failure";

/**
 * Every scenario / rule-evaluation outcome except the success document. `aborted` (a superseded
 * request) is included for type-completeness and maps to null — the newer request owns the surface.
 */
export type EnrichmentFailureOutcome =
  | Exclude<ScenarioOutcome, { kind: "scenario" }>
  | Exclude<RuleEvaluationOutcome, { kind: "evaluation" }>;

/** The plain nouns and testid prefix one surface contributes to otherwise-identical §5a copy. */
export interface EnrichmentSurface {
  /** Lowercase noun used mid-sentence, e.g. "scenario comparison". */
  subject: string;
  /** The same noun capitalized for a sentence start, e.g. "Scenario comparison". */
  Subject: string;
  /** Stable testid prefix for this surface's notice, e.g. "scenario". */
  testId: string;
}

export const SCENARIO_SURFACE: EnrichmentSurface = {
  subject: "scenario comparison",
  Subject: "Scenario comparison",
  testId: "scenario",
};

export const RULE_EVALUATION_SURFACE: EnrichmentSurface = {
  subject: "draft rule evaluation",
  Subject: "Draft rule evaluation",
  testId: "rule-eval",
};

// The property profile above never depends on an enrichment, so every failure says what still works.
const PROFILE_UNAFFECTED = "The rest of this property's facts are complete and unaffected.";
const RETRY_SAFE = "Nothing is wrong with the property you entered. Trying again is safe.";
const NEEDS_PLATFORM =
  "This needs the platform team. Trying again will likely give the same result until it is fixed.";
const FROM_SOURCE = "This is an answer from the official city source, not an app error.";

function upstreamCopy(
  state: ScenarioUpstreamFailureState,
  subject: string,
): { title: string; body: string; recovery: string } {
  switch (state) {
    case "rate_limited":
      return {
        title: "The city data source is busy right now",
        body:
          `The official city source temporarily limited the app's requests, so the ${subject} ` +
          `could not be produced. ${PROFILE_UNAFFECTED}`,
        recovery: RETRY_SAFE,
      };
    case "source_unavailable":
      return {
        title: "The city data source could not be reached",
        body:
          `The official city source did not answer after several tries, so the ${subject} could ` +
          `not be produced. ${PROFILE_UNAFFECTED}`,
        recovery: RETRY_SAFE,
      };
    case "timeout":
      return {
        title: "The city data source took too long",
        body:
          `The official city source did not respond in time, so the ${subject} could not be ` +
          `produced. ${PROFILE_UNAFFECTED}`,
        recovery: RETRY_SAFE,
      };
    case "schema_drift":
      return {
        title: "The city dataset changed shape",
        body:
          `The official city dataset no longer matches its recorded format, so the app would not ` +
          `trust it for the ${subject}. ${PROFILE_UNAFFECTED}`,
        recovery: NEEDS_PLATFORM,
      };
  }
}

/**
 * The plain §5a notice for one failed enrichment on `surface`, or null when the request was
 * superseded (`aborted`).
 */
export function enrichmentFailureNotice(
  outcome: EnrichmentFailureOutcome,
  surface: EnrichmentSurface,
): DashboardFailureNoticeModel | null {
  const { subject, Subject } = surface;
  switch (outcome.kind) {
    case "aborted":
      return null;
    case "feature_unavailable":
      return {
        title: `${Subject} is not available here`,
        body: `This feature is not switched on in this environment, so nothing was produced. ${PROFILE_UNAFFECTED}`,
        recovery: "Nothing to do — this is an environment setting, not a fault.",
        retryable: false,
        technical: [],
      };
    case "no_match":
      return {
        title: `No city record for the ${subject}`,
        body: `${outcome.message} ${PROFILE_UNAFFECTED}`,
        recovery: FROM_SOURCE,
        retryable: false,
        technical: referenceRow(outcome.correlationId),
      };
    case "validation_error":
      return {
        title: `The ${subject} request was not accepted`,
        body: outcome.message,
        recovery: "Check the identifier and try another lot.",
        retryable: false,
        technical: [
          { label: "Rejection code", value: outcome.code },
          ...referenceRow(outcome.correlationId),
        ],
      };
    case "upstream_failure": {
      const copy = upstreamCopy(outcome.state, subject);
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
        title: `Something went wrong producing the ${subject}`,
        body: `The app hit an unexpected problem while producing the ${subject}. ${PROFILE_UNAFFECTED}`,
        recovery: RETRY_SAFE,
        retryable: true,
        technical: referenceRow(outcome.correlationId),
      };
    case "server_contract_error":
      return {
        title: `The app held back an unreliable ${subject}`,
        body:
          `The app built a ${subject} that failed its own quality checks and held it back rather ` +
          `than show data it could not trust. ${PROFILE_UNAFFECTED}`,
        recovery: NEEDS_PLATFORM,
        retryable: true,
        technical: referenceRow(outcome.correlationId),
      };
    case "validation_failure":
      return {
        title: `The ${subject} did not match the published data format`,
        body:
          `The service returned a ${subject} that failed this screen's format check. Nothing from ` +
          `that response is shown. ${PROFILE_UNAFFECTED}`,
        recovery: NEEDS_PLATFORM,
        retryable: true,
        technical: [
          ...outcome.problems.map(problem => ({ label: "Format problem", value: problem })),
          ...referenceRow(outcome.correlationId),
        ],
      };
    case "network_error":
      return {
        title: `Could not reach the ${subject} service`,
        body: outcome.message,
        recovery: RETRY_SAFE,
        retryable: true,
        technical: [],
      };
    case "client_timeout":
      return {
        title: `The ${subject} took too long`,
        body:
          `The service did not answer within ${Math.round(outcome.timeoutMs / 1000)} seconds, so ` +
          `the request was cancelled. No partial data is shown. ${PROFILE_UNAFFECTED}`,
        recovery: RETRY_SAFE,
        retryable: true,
        technical: [],
      };
    case "unexpected_response":
      return {
        title: `Unexpected response from the ${subject} service`,
        body:
          `The service answered in a way the app does not recognize, so the response was not ` +
          `trusted or shown. ${PROFILE_UNAFFECTED} This is worth reporting.`,
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
