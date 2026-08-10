import { expect, test } from "@playwright/test";
import { DIGEST_PRO, DIGEST_USER, installSurveyReviewMock } from "./survey-review-helpers";

/**
 * SC-S3 authorization + SC-S4 no-auto-verified (task M2-T016 rework). A preparer
 * (human_user) may accept/correct but cannot reject a fact (professional-only in
 * the shipped slice) or take any document decision; a professional can, but the
 * confirm control is H5-gated. Nothing is labelled "Verified".
 */

const CLEAN = "sev:doc:p1:1";

function reviewUrl(digest: string): string {
  return `/survey/review/${encodeURIComponent(digest)}`;
}

test("SC-S3: a preparer cannot reject a fact or confirm the document", async ({ page }) => {
  await installSurveyReviewMock(page);
  await page.goto(reviewUrl(DIGEST_USER));

  await expect(page.getByTestId("focused-item")).toBeVisible();
  await expect(page.getByTestId("action-correct")).toBeEnabled();
  await expect(page.getByTestId("action-reject")).toBeDisabled();
  await expect(page.getByTestId("action-disabled-reason")).toBeVisible();

  // The confirm control is not offered; the reason is stated, not silently hidden.
  await expect(page.getByTestId("action-confirm-document")).toHaveCount(0);
  await expect(page.getByTestId("confirm-capability-note")).toBeVisible();
});

test("SC-S4: facts read 'Unconfirmed evidence'; nothing is labelled 'Verified'; confirm is H5-gated", async ({ page }) => {
  await installSurveyReviewMock(page);
  await page.goto(reviewUrl(DIGEST_PRO));

  await expect(page.getByTestId("review-topbar")).toBeVisible();
  await expect(page.getByTestId(`fact-confirmation-${CLEAN}`)).toContainText("Unconfirmed evidence");
  await expect(page.getByText("Verified", { exact: true })).toHaveCount(0);

  await expect(page.getByTestId("action-confirm-document")).toBeDisabled();
  await expect(page.getByTestId("confirm-blocked-explanation")).toContainText("Stated lot area");
});
