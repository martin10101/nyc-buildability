import { describe, expect, it } from "vitest";
import { surveyReviewEnabled } from "@/lib/surveyReview/config";

describe("surveyReviewEnabled (internal visibility gate)", () => {
  it("is OFF by default (fail-safe) when the flag is unset", () => {
    expect(surveyReviewEnabled({})).toBe(false);
  });

  it("accepts the documented truthy tokens", () => {
    for (const token of ["1", "true", "yes", "on", "TRUE", " On "]) {
      expect(surveyReviewEnabled({ INTERNAL_SURVEY_REVIEW_ENABLED: token })).toBe(true);
    }
  });

  it("treats anything else as OFF", () => {
    for (const token of ["0", "false", "no", "off", ""]) {
      expect(surveyReviewEnabled({ INTERNAL_SURVEY_REVIEW_ENABLED: token })).toBe(false);
    }
  });
});
