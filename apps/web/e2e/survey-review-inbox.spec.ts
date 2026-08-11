import { expect, test } from "@playwright/test";
import { installSurveyReviewMock } from "./survey-review-helpers";

/**
 * G3 F10 (task M2-T016 fix delta). The seven survey-review journey specs all
 * navigate to `/survey/review/<digest>`; none loads the bare inbox. That left
 * `export const dynamic = "force-dynamic"` on `app/survey/review/page.tsx`
 * justified only by analogy — and that route is the one with no dynamic segment
 * and no dynamic API, so it is unambiguously statically prerenderable and the
 * MOST likely to have its `INTERNAL_SURVEY_REVIEW_ENABLED` gate evaluated at
 * build time (flag unset) and baked in as a 404.
 *
 * This spec is deliberately named for the cause rather than for a journey: if
 * `force-dynamic` is removed, the failure says the runtime flag stopped
 * governing the route, instead of surfacing as unrelated-looking journey
 * breakage. CI builds with the flag UNSET and serves with it SET
 * (playwright.config.ts webServer env), so reaching the page at all is the
 * assertion that matters.
 */
test("the review inbox honours the runtime flag at request time, not build time", async ({ page }) => {
  await installSurveyReviewMock(page);
  await page.goto("/survey/review");

  // Rendered at all => the route was not baked as notFound() during the build.
  await expect(page.getByTestId("review-inbox")).toBeVisible();
  await expect(page.getByTestId("internal-banner")).toBeVisible();
  // The mock inbox is an honest empty queue, so the empty state is the settled view.
  await expect(page.getByTestId("inbox-empty")).toBeVisible();
});
