import type { LookupOutcome, UpstreamFailureOutcome } from "@/lib/api";
import type { AddressErrorState, AddressOutcome } from "@/lib/address-api";

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

/**
 * Address-resolution announcements (task M5-T015) — ADDITIVE extension:
 * the address screen has its own outcome union (src/lib/address-api.ts)
 * and its own persistent live region (testId="address-outcome-announcer",
 * the M4-T005 coexistence pattern), so it gets its own mapping. The same
 * rules apply: copy mirrors the visible card titles, adds nothing, and
 * `aborted` announces nothing. Everything above is byte-unchanged.
 */

const ADDRESS_ERROR_ANNOUNCEMENTS: Record<AddressErrorState, string> = {
  invalid_input:
    "Address lookup rejected: the city's service could not read this address.",
  key_missing:
    "Address lookup failed: address lookup is not configured on the platform side.",
  auth_failed:
    "Address lookup failed: the platform's access to the city's service was refused.",
  rate_limited:
    "Address lookup failed: the city's address service is throttling requests.",
  source_unavailable:
    "Address lookup failed: the city's address service is unavailable.",
  timeout: "Address lookup failed: the city's address service timed out.",
  malformed_response:
    "Address lookup failed: the city's address service sent an unreadable response.",
  request_budget_exceeded:
    "Address lookup failed: the platform's request budget for this lookup ran out.",
  internal_error:
    "Address lookup failed: something went wrong on our side.",
};

export function announcementForAddressOutcome(outcome: AddressOutcome): string {
  switch (outcome.kind) {
    case "document":
      switch (outcome.view.status) {
        case "resolved":
          return "Address resolved to a single lot.";
        case "resolved_with_warnings":
          return "Address resolved to a single lot, with warnings from the city's service.";
        case "ambiguous":
          return "The city's service returned more than one possible match. Choose the correct one.";
        case "not_found":
          return "The city's service has no record matching this address.";
        case "rejected":
          return "The city's service rejected this address as unresolvable.";
        default:
          return "The city's service answered in a form this platform does not recognize.";
      }
    case "error":
      return ADDRESS_ERROR_ANNOUNCEMENTS[outcome.state];
    case "network_error":
      return "Address lookup failed: the platform API could not be reached.";
    case "client_timeout":
      return "Address lookup failed: the lookup took too long and was cancelled.";
    case "unexpected_response":
      return "Address lookup failed: unexpected response from the platform API.";
    case "aborted":
      return "";
  }
}
