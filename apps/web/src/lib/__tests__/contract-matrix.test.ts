import { describe, expect, it } from "vitest";
import {
  DOCUMENTED_STATUS_STATE_PAIRS,
  isDocumentedPair,
} from "@/lib/contract-matrix";

/**
 * The client matrix must mirror the backend STATUS_STATE_MATRIX
 * (services/api/app/api/v1/properties.py) VERBATIM. This test hardcodes
 * the expected set independently so an accidental edit to either the
 * matrix module or this expectation is caught. If the backend matrix ever
 * changes, BOTH the module and this test must change in the same reviewed
 * task.
 */
const EXPECTED_PAIRS: ReadonlySet<string> = new Set([
  "200:",
  "422:validation_error",
  "404:no_match",
  "502:schema_drift",
  "503:rate_limited",
  "503:source_unavailable",
  "504:timeout",
  "500:internal_error",
  "500:internal_contract_error",
  "500:unsupported_contract_version",
]);

describe("DOCUMENTED_STATUS_STATE_PAIRS", () => {
  it("contains exactly the 10 backend-documented pairs", () => {
    const actual = new Set(
      DOCUMENTED_STATUS_STATE_PAIRS.map(([status, state]) => `${status}:${state ?? ""}`),
    );
    expect(actual).toEqual(EXPECTED_PAIRS);
    expect(DOCUMENTED_STATUS_STATE_PAIRS.length).toBe(10);
  });
});

describe("isDocumentedPair", () => {
  it("accepts every documented pair", () => {
    for (const [status, state] of DOCUMENTED_STATUS_STATE_PAIRS) {
      expect(isDocumentedPair(status, state)).toBe(true);
    }
  });

  it("rejects the owner-directed regression pair (500, no_match)", () => {
    expect(isDocumentedPair(500, "no_match")).toBe(false);
  });

  it("rejects documented states on the wrong status", () => {
    expect(isDocumentedPair(503, "timeout")).toBe(false);
    expect(isDocumentedPair(404, "validation_error")).toBe(false);
    expect(isDocumentedPair(200, "no_match")).toBe(false);
    expect(isDocumentedPair(504, "rate_limited")).toBe(false);
  });

  it("rejects a stateless non-200 and a stateful 200", () => {
    expect(isDocumentedPair(404, null)).toBe(false);
    expect(isDocumentedPair(500, null)).toBe(false);
    expect(isDocumentedPair(200, "internal_error")).toBe(false);
  });

  it("rejects unknown states and unknown statuses", () => {
    expect(isDocumentedPair(500, "made_up")).toBe(false);
    expect(isDocumentedPair(418, "no_match")).toBe(false);
  });
});
