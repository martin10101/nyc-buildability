// M5-T065 placeholder spec (seeded; replaced by the producer). Trivially passing -
// an empty spec file fails vitest with "no suite" (CODING_RULES).
import { describe, expect, it } from "vitest";
import { OUTLINE_BRIDGE_CLIENT_PLACEHOLDER } from "../outline-bridge-api";

describe("M5-T065 seed placeholder (replaced by the producer)", () => {
  it("carries the packet id until the real client lands", () => {
    expect(OUTLINE_BRIDGE_CLIENT_PLACEHOLDER).toBe("M5-T065");
  });
});
