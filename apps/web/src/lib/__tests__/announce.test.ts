import { describe, expect, it } from "vitest";
import { announcementForOutcome } from "@/lib/announce";
import type { LookupOutcome, UpstreamFailureOutcome } from "@/lib/api";
import { baseProfile } from "@/test-support/fixtures";

/**
 * M2-T005 scenario S1 (component level): every documented outcome kind has
 * a deterministic, distinct, non-empty assistive announcement — except
 * `aborted`, which must announce nothing (superseded requests never reach
 * the screen). Copy is honesty-checked: no "best"/"verified" wording.
 */

const UPSTREAM_STATES: UpstreamFailureOutcome["state"][] = [
  "rate_limited",
  "source_unavailable",
  "timeout",
  "schema_drift",
];

function upstream(state: UpstreamFailureOutcome["state"]): LookupOutcome {
  return {
    kind: "upstream_failure",
    state,
    httpStatus: 503,
    message: "upstream",
    correlationId: null,
  };
}

const NON_PROFILE_OUTCOMES: Array<[string, LookupOutcome, RegExp]> = [
  [
    "no_match",
    { kind: "no_match", bbl: "5999999999", message: "m", correlationId: null },
    /^Lookup complete: no property record found/,
  ],
  [
    "validation_error",
    { kind: "validation_error", code: "invalid_block", message: "m", correlationId: null },
    /^Lookup rejected: the API rejected this BBL\.$/,
  ],
  [
    "internal_error",
    { kind: "internal_error", message: "m", correlationId: null },
    /^Lookup failed: something went wrong on our side\.$/,
  ],
  [
    "server_contract_error",
    {
      kind: "server_contract_error",
      state: "internal_contract_error",
      message: "m",
      correlationId: null,
    },
    /^Lookup failed: the server refused to deliver an invalid profile\.$/,
  ],
  [
    "validation_failure",
    { kind: "validation_failure", problems: [], correlationId: null },
    /^Lookup failed: the response did not match the published data contract\.$/,
  ],
  [
    "network_error",
    { kind: "network_error", message: "m" },
    /^Lookup failed: the platform API could not be reached\.$/,
  ],
  [
    "client_timeout",
    { kind: "client_timeout", timeoutMs: 12000 },
    /^Lookup failed: the lookup took too long and was cancelled\.$/,
  ],
  [
    "unexpected_response",
    {
      kind: "unexpected_response",
      httpStatus: 500,
      receivedState: "no_match",
      correlationId: null,
    },
    /^Lookup failed: unexpected response from the platform API\.$/,
  ],
];

describe("announcementForOutcome — one deterministic message per outcome", () => {
  it("announces a successful profile arrival with the BBL", () => {
    const outcome: LookupOutcome = {
      kind: "profile",
      profile: baseProfile(),
      correlationId: null,
    };
    expect(announcementForOutcome(outcome)).toBe(
      "Lookup complete: official property profile loaded for BBL 1000010010.",
    );
  });

  it.each(NON_PROFILE_OUTCOMES)("announces %s", (_kind, outcome, expected) => {
    expect(announcementForOutcome(outcome)).toMatch(expected);
  });

  it.each(UPSTREAM_STATES)("announces upstream state %s distinctly", (state) => {
    const message = announcementForOutcome(upstream(state));
    expect(message).toMatch(/^Lookup failed: /);
    // Distinct from every other upstream state's message.
    for (const other of UPSTREAM_STATES) {
      if (other !== state) {
        expect(message).not.toBe(announcementForOutcome(upstream(other)));
      }
    }
  });

  it("announces NOTHING for a superseded (aborted) request", () => {
    expect(announcementForOutcome({ kind: "aborted" })).toBe("");
  });

  it("honesty: no announcement contains 'best' or 'verified'", () => {
    const all: LookupOutcome[] = [
      ...NON_PROFILE_OUTCOMES.map(([, outcome]) => outcome),
      ...UPSTREAM_STATES.map(upstream),
      { kind: "profile", profile: baseProfile(), correlationId: null },
    ];
    for (const outcome of all) {
      const message = announcementForOutcome(outcome);
      expect(message).not.toMatch(/\bbest\b/i);
      expect(message).not.toMatch(/\bverified\b/i);
    }
  });
});
