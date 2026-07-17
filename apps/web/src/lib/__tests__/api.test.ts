import { describe, expect, it } from "vitest";
import { fetchPropertyProfile } from "@/lib/api";
import { baseProfile, jsonResponse } from "@/test-support/fixtures";

/**
 * Outcome classification for every documented response of
 * GET /api/v1/properties/{bbl} (services/api/app/api/v1/properties.py).
 * `state` is the non-200 discriminator; a routing 404 without a state must
 * NEVER classify as no_match (M1-T005 G3 section 5).
 */
describe("fetchPropertyProfile", () => {
  it("classifies a 200 canonical profile", async () => {
    const fetchStub = async () => jsonResponse(baseProfile(), 200, "corr-200");
    const outcome = await fetchPropertyProfile("1000010010", fetchStub as typeof fetch);
    expect(outcome.kind).toBe("profile");
    if (outcome.kind === "profile") {
      expect(outcome.profile.identity.bbl).toBe("1000010010");
      expect(outcome.correlationId).toBe("corr-200");
    }
  });

  it("classifies 404 state=no_match with the API's explanation text", async () => {
    const body = {
      state: "no_match",
      bbl: "1000041001",
      message:
        "No PLUTO record: condo unit lots are recorded under the BILLING lot (7501-7599).",
      correlation_id: "abc",
    };
    const fetchStub = async () => jsonResponse(body, 404);
    const outcome = await fetchPropertyProfile("1000041001", fetchStub as typeof fetch);
    expect(outcome.kind).toBe("no_match");
    if (outcome.kind === "no_match") {
      expect(outcome.message).toContain("BILLING lot");
      expect(outcome.bbl).toBe("1000041001");
    }
  });

  it("distinguishes a routing 404 (no state) from no_match", async () => {
    const fetchStub = async () => jsonResponse({ detail: "Not Found" }, 404);
    const outcome = await fetchPropertyProfile("1000010010", fetchStub as typeof fetch);
    expect(outcome.kind).toBe("unexpected_response");
  });

  it("classifies 422 validation_error with detail.code", async () => {
    const body = {
      state: "validation_error",
      message: "BBL tax block must be 1-99999; got '00000'",
      detail: { code: "invalid_block", raw_value: "'1000000000'" },
    };
    const fetchStub = async () => jsonResponse(body, 422);
    const outcome = await fetchPropertyProfile("1000000000", fetchStub as typeof fetch);
    expect(outcome.kind).toBe("validation_error");
    if (outcome.kind === "validation_error") {
      expect(outcome.code).toBe("invalid_block");
      expect(outcome.message).toContain("tax block");
    }
  });

  it.each([
    ["rate_limited", 503],
    ["source_unavailable", 503],
    ["timeout", 504],
    ["schema_drift", 502],
  ] as const)("classifies %s (%d) as a typed upstream failure", async (state, status) => {
    const fetchStub = async () => jsonResponse({ state, message: "upstream" }, status);
    const outcome = await fetchPropertyProfile("1000010010", fetchStub as typeof fetch);
    expect(outcome.kind).toBe("upstream_failure");
    if (outcome.kind === "upstream_failure") {
      expect(outcome.state).toBe(state);
      expect(outcome.httpStatus).toBe(status);
    }
  });

  it("classifies 500 internal_error and keeps the correlation id", async () => {
    const body = {
      state: "internal_error",
      message: "unexpected internal error; see server logs by correlation id",
      correlation_id: "corr-500",
    };
    const fetchStub = async () => jsonResponse(body, 500, "corr-500");
    const outcome = await fetchPropertyProfile("1000010010", fetchStub as typeof fetch);
    expect(outcome.kind).toBe("internal_error");
    if (outcome.kind === "internal_error") {
      expect(outcome.correlationId).toBe("corr-500");
    }
  });

  it("classifies a thrown fetch (connection refused) as network_error", async () => {
    const fetchStub = async () => {
      throw new TypeError("fetch failed");
    };
    const outcome = await fetchPropertyProfile("1000010010", fetchStub as typeof fetch);
    expect(outcome.kind).toBe("network_error");
    if (outcome.kind === "network_error") {
      expect(outcome.message).toContain("safe to retry");
    }
  });

  it("classifies non-JSON bodies as unexpected_response", async () => {
    const fetchStub = async () =>
      new Response("<html>gateway</html>", { status: 502 });
    const outcome = await fetchPropertyProfile("1000010010", fetchStub as typeof fetch);
    expect(outcome.kind).toBe("unexpected_response");
  });

  it("classifies a 200 without a profile shape as unexpected_response", async () => {
    const fetchStub = async () => jsonResponse({ hello: "world" }, 200);
    const outcome = await fetchPropertyProfile("1000010010", fetchStub as typeof fetch);
    expect(outcome.kind).toBe("unexpected_response");
  });
});
