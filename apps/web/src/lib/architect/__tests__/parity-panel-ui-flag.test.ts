import { describe, expect, it } from "vitest";
import { PARITY_UI_FLAG, parityUiEnabled } from "@/lib/architect/parity-panel-ui-flag";

/**
 * The default-off server gate for the parity surface (queue D-15, plan §11b).
 * New lane behaviour ships OFF in production: absent / empty / unknown -> off; only
 * an explicit true token enables it. Mirrors the D-12 hidden-issue-flags flag and
 * is DISTINCT from lane C's server read-route flag INTERNAL_PARITY_READ_ENABLED.
 */
describe("parityUiEnabled — default-off server gate", () => {
  it("is off when the flag is absent (production safety)", () => {
    expect(parityUiEnabled({})).toBe(false);
  });

  it("is off for empty or unknown tokens", () => {
    expect(parityUiEnabled({ [PARITY_UI_FLAG]: "" })).toBe(false);
    expect(parityUiEnabled({ [PARITY_UI_FLAG]: "maybe" })).toBe(false);
    expect(parityUiEnabled({ [PARITY_UI_FLAG]: "0" })).toBe(false);
    expect(parityUiEnabled({ [PARITY_UI_FLAG]: "off" })).toBe(false);
  });

  it("is on only for an explicit true token", () => {
    for (const token of ["1", "true", "yes", "on", "TRUE", " On "]) {
      expect(parityUiEnabled({ [PARITY_UI_FLAG]: token })).toBe(true);
    }
  });

  it("is not a NEXT_PUBLIC_ flag (never inlined into the browser bundle) and is distinct from the read flag", () => {
    expect(PARITY_UI_FLAG.startsWith("NEXT_PUBLIC_")).toBe(false);
    expect(PARITY_UI_FLAG).toBe("INTERNAL_PARITY_UI_ENABLED");
    expect(PARITY_UI_FLAG).not.toBe("INTERNAL_PARITY_READ_ENABLED");
  });
});
