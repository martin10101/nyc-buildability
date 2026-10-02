import { describe, expect, it } from "vitest";
import {
  HIDDEN_ISSUE_FLAGS_UI_FLAG,
  hiddenIssueFlagsUiEnabled,
} from "@/lib/architect/hidden-issue-flags-ui-flag";

/**
 * The default-off server gate for the §8a hidden-issue-flags surface (queue D-12).
 * New lane behaviour ships OFF in production: absent / empty / unknown -> off; only
 * an explicit true token enables it. Mirrors the D-04 lot-site flag.
 */
describe("hiddenIssueFlagsUiEnabled — default-off server gate", () => {
  it("is off when the flag is absent (production safety)", () => {
    expect(hiddenIssueFlagsUiEnabled({})).toBe(false);
  });

  it("is off for empty or unknown tokens", () => {
    expect(hiddenIssueFlagsUiEnabled({ [HIDDEN_ISSUE_FLAGS_UI_FLAG]: "" })).toBe(false);
    expect(hiddenIssueFlagsUiEnabled({ [HIDDEN_ISSUE_FLAGS_UI_FLAG]: "maybe" })).toBe(false);
    expect(hiddenIssueFlagsUiEnabled({ [HIDDEN_ISSUE_FLAGS_UI_FLAG]: "0" })).toBe(false);
  });

  it("is on only for an explicit true token", () => {
    for (const token of ["1", "true", "yes", "on", "TRUE", " On "]) {
      expect(hiddenIssueFlagsUiEnabled({ [HIDDEN_ISSUE_FLAGS_UI_FLAG]: token })).toBe(true);
    }
  });

  it("is not a NEXT_PUBLIC_ flag (never inlined into the browser bundle)", () => {
    expect(HIDDEN_ISSUE_FLAGS_UI_FLAG.startsWith("NEXT_PUBLIC_")).toBe(false);
    expect(HIDDEN_ISSUE_FLAGS_UI_FLAG).toBe("INTERNAL_HIDDEN_ISSUE_FLAGS_UI_ENABLED");
  });
});
