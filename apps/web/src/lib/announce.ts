import type { LookupOutcome, UpstreamFailureOutcome } from "@/lib/api";

/**
 * Assistive-technology announcement copy for lookup outcome arrivals
 * (task M2-T005, visual-quality Major D1).
 *
 * WHY A SINGLE MAPPING: both screens announce outcome arrivals through one
 * persistent live region (see OutcomeAnnouncer). The message for a given
 * outcome is derived HERE, deterministically, from the already-classified
 * typed outcome — announcement copy mirrors the visible failure-card
 * titles and adds nothing: no legal semantics, no invented values, no
 * "best"/"verified" wording (PRD sections 6/12 honesty rules).
 *
 * `aborted` maps to the empty string on purpose: a superseded request has
 * no user-visible meaning and must announce nothing (it never reaches the
 * screen either — the outcome state machines drop it before render).
 */

const UPSTREAM_ANNOUNCEMENTS: Record<UpstreamFailureOutcome["state"], string> = {
  rate_limited:
    "Lookup failed: the official data source is throttling requests.",
  source_unavailable:
    "Lookup failed: the official data source is unavailable.",
  timeout: "Lookup failed: the official data source timed out.",
  schema_drift: "Lookup failed: the official dataset changed shape.",
};

export function announcementForOutcome(outcome: LookupOutcome): string {
  switch (outcome.kind) {
    case "profile":
      return `Lookup complete: official property profile loaded for BBL ${outcome.profile.identity.bbl}.`;
    case "no_match":
      return "Lookup complete: no property record found in the official dataset.";
    case "validation_error":
      return "Lookup rejected: the API rejected this BBL.";
    case "upstream_failure":
      return UPSTREAM_ANNOUNCEMENTS[outcome.state];
    case "internal_error":
      return "Lookup failed: something went wrong on our side.";
    case "server_contract_error":
      return "Lookup failed: the server refused to deliver an invalid profile.";
    case "validation_failure":
      return "Lookup failed: the response did not match the published data contract.";
    case "network_error":
      return "Lookup failed: the platform API could not be reached.";
    case "client_timeout":
      return "Lookup failed: the lookup took too long and was cancelled.";
    case "unexpected_response":
      return "Lookup failed: unexpected response from the platform API.";
    case "aborted":
      return "";
  }
}
