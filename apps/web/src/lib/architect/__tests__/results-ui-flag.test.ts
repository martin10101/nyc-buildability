import { describe, expect, it } from "vitest";
import { RESULTS_UI_FLAG, resultsUiEnabled } from "@/lib/architect/results-ui-flag";

/**
 * [WIRING] The default-off server gate for the results panel (task M5-T140, ruling R1).
 * New lane behaviour ships OFF in production: absent / empty / unknown -> off; only an
 * explicit true token enables it. It is DISTINCT from the server read-route flag
 * INTERNAL_RESULTS_ENABLED (services/api), which the route itself reads.
 */
describe("resultsUiEnabled — default-off server gate [WIRING]", () => {
  it("is off when the flag is absent (production safety)", () => {
    expect(resultsUiEnabled({})).toBe(false);
  });

  it("is off for empty or unknown tokens", () => {
    expect(resultsUiEnabled({ [RESULTS_UI_FLAG]: "" })).toBe(false);
    expect(resultsUiEnabled({ [RESULTS_UI_FLAG]: "maybe" })).toBe(false);
    expect(resultsUiEnabled({ [RESULTS_UI_FLAG]: "0" })).toBe(false);
    expect(resultsUiEnabled({ [RESULTS_UI_FLAG]: "off" })).toBe(false);
  });

  it("is on only for an explicit true token", () => {
    for (const token of ["1", "true", "yes", "on", "TRUE", " On "]) {
      expect(resultsUiEnabled({ [RESULTS_UI_FLAG]: token })).toBe(true);
    }
  });

  it("is not a NEXT_PUBLIC_ flag (never inlined into the bundle) and is distinct from the read flag", () => {
    expect(RESULTS_UI_FLAG.startsWith("NEXT_PUBLIC_")).toBe(false);
    expect(RESULTS_UI_FLAG).toBe("INTERNAL_RESULTS_UI_ENABLED");
    expect(RESULTS_UI_FLAG).not.toBe("INTERNAL_RESULTS_ENABLED");
  });
});
