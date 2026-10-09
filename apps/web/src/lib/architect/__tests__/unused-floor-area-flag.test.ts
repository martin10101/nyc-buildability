import { describe, expect, it } from "vitest";
import {
  UNUSED_FLOOR_AREA_SECTION_FLAG,
  unusedFloorAreaSectionEnabled,
} from "@/lib/architect/unused-floor-area-flag";

/**
 * D-06 (plan §3 step 4, M2-07; set-aside item #6): the set-aside
 * unused-floor-area section is gated by the non-public, server-read
 * INTERNAL_UNUSED_FLOOR_AREA_SECTION_ENABLED. Fail safe: absent, empty or any
 * unknown value keeps it OFF; only an explicit true token turns it on.
 */
describe("unusedFloorAreaSectionEnabled — default-off, fail-safe server flag", () => {
  it("reads the canonical, non-public variable name", () => {
    expect(UNUSED_FLOOR_AREA_SECTION_FLAG).toBe("INTERNAL_UNUSED_FLOOR_AREA_SECTION_ENABLED");
    expect(UNUSED_FLOOR_AREA_SECTION_FLAG.startsWith("NEXT_PUBLIC_")).toBe(false);
  });

  it("is OFF when the variable is absent", () => {
    expect(unusedFloorAreaSectionEnabled({})).toBe(false);
  });

  it.each(["", " ", "0", "false", "off", "no", "enabled", "2", "tru"])("is OFF for %j", (raw) => {
    expect(unusedFloorAreaSectionEnabled({ [UNUSED_FLOOR_AREA_SECTION_FLAG]: raw })).toBe(false);
  });

  it.each(["1", "true", "TRUE", " yes ", "on", "On"])("is ON only for the explicit true token %j", (raw) => {
    expect(unusedFloorAreaSectionEnabled({ [UNUSED_FLOOR_AREA_SECTION_FLAG]: raw })).toBe(true);
  });

  it("ignores similar variables, including the server's legacy-subtraction flag", () => {
    expect(
      unusedFloorAreaSectionEnabled({
        INTERNAL_LEGACY_UNUSED_FLOOR_AREA_ENABLED: "1",
        INTERNAL_PROPOSAL_EDITOR_ENABLED: "1",
        NEXT_PUBLIC_INTERNAL_UNUSED_FLOOR_AREA_SECTION_ENABLED: "1",
      }),
    ).toBe(false);
  });
});
