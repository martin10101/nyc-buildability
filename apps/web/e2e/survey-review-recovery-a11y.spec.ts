import { expect, test } from "@playwright/test";
import { DIGEST_PRO, installSurveyReviewMock } from "./survey-review-helpers";

/**
 * SC-S7 recovery + accessibility + responsive (task M2-T016 rework). A
 * recoverable API failure mid-load offers a safe retry; the new screens are
 * keyboard-operable with labelled controls and an overlay text alternative; and
 * no critical warning is hidden at a phone viewport.
 */

function reviewUrl(digest: string): string {
  return `/survey/review/${encodeURIComponent(digest)}`;
}

test("SC-S7: a recoverable read failure offers retry, then recovers", async ({ page }) => {
  await page.route("**/api/v1/documents/**", (route) => route.abort());
  await page.goto(reviewUrl(DIGEST_PRO));
  await expect(page.getByTestId("read-failure-network_error")).toBeVisible();
  const retry = page.getByTestId("read-retry");
  await expect(retry).toBeVisible();

  await page.unroute("**/api/v1/documents/**");
  await installSurveyReviewMock(page);
  await retry.click();
  await expect(page.getByTestId("review-topbar")).toBeVisible();
});

test("SC-S7: the correction editor is keyboard-operable with labelled fields", async ({ page }) => {
  await installSurveyReviewMock(page);
  await page.goto(reviewUrl(DIGEST_PRO));
  await expect(page.getByTestId("focused-item")).toBeVisible();

  await page.getByTestId("action-correct").click();
  await expect(page.getByLabel(/Corrected normalized value/)).toBeVisible();
  await expect(page.getByLabel("Reason (required)")).toBeVisible();

  await expect(page.getByTestId("overlay-alt-summary")).toContainText("Stated lot area");

  await page.getByLabel("Reason (required)").focus();
  await page.keyboard.type("Corrected via keyboard.");
  await expect(page.getByTestId("correction-reason")).toHaveValue("Corrected via keyboard.");
});

test("SC-S7: critical warnings stay visible at a phone viewport", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await installSurveyReviewMock(page);
  await page.goto(reviewUrl(DIGEST_PRO));

  await expect(page.getByTestId("review-topbar")).toBeVisible();
  await expect(page.getByTestId("check-conflict")).toBeVisible();
  await expect(page.getByTestId("downstream-impact")).toBeVisible();
});
