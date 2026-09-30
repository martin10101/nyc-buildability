import { describe, expect, it } from "vitest";
import { SHARED_STUDY_STORE_FLAG, sharedStudyStoreEnabled } from "../shared-study-flag";

/**
 * C-05 (plan M1-10): surfaces move onto the shared study store only behind the
 * non-public, server-read INTERNAL_SHARED_STUDY_STORE_ENABLED. Fail safe:
 * absent, empty or any unknown value keeps it OFF.
 */
describe("sharedStudyStoreEnabled: default-off, fail-safe server flag", () => {
  it("reads the canonical, non-public variable name", () => {
    expect(SHARED_STUDY_STORE_FLAG).toBe("INTERNAL_SHARED_STUDY_STORE_ENABLED");
    expect(SHARED_STUDY_STORE_FLAG.startsWith("NEXT_PUBLIC_")).toBe(false);
  });

  it("is OFF when the variable is absent", () => {
    expect(sharedStudyStoreEnabled({})).toBe(false);
  });

  it.each(["", " ", "0", "false", "off", "no", "enabled", "2", "tru"])("is OFF for %j", (raw) => {
    expect(sharedStudyStoreEnabled({ [SHARED_STUDY_STORE_FLAG]: raw })).toBe(false);
  });

  it.each(["1", "true", "TRUE", " yes ", "on", "On"])("is ON only for the explicit true token %j", (raw) => {
    expect(sharedStudyStoreEnabled({ [SHARED_STUDY_STORE_FLAG]: raw })).toBe(true);
  });

  it("ignores a public variable of the same name", () => {
    expect(sharedStudyStoreEnabled({ NEXT_PUBLIC_INTERNAL_SHARED_STUDY_STORE_ENABLED: "1" })).toBe(false);
  });
});
