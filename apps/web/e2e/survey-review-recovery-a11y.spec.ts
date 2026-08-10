import { expect, test } from "@playwright/test";
import { installSurveyReviewMock } from "./survey-review-helpers";

/**
 * SC-S7 recovery + accessibility + responsive (task M2-T016). A recoverable API
 * failure mid-load preserves the way forward and offers a safe retry; the new
 * screens are keyboard-operable with labelled controls and an overlay text
 * alternative; and no critical warning is hidden at a phone viewport.
 */

test("SC-S7: a recoverable read failure offers retry, then recovers", async ({ page }) => {
  // First, make the review API unreachable.
  await page.route("**/api/v1/documents/**", (route) => route.abort());
  await page.goto("/survey/review/doc-pro");
  await expect(page.getByTestId("read-failure-network_error")).toBeVisible();
  const retry = page.getByTestId("read-retry");
  await expect(retry).toBeVisible();

  // Restore the service and retry — the document loads.
  await page.unroute("**/api/v1/documents/**");
  await installSurveyReviewMock(page);
  await retry.click();
  await expect(page.getByTestId("review-topbar")).toBeVisible();
});

test("SC-S7: the correction editor is keyboard-operable with labelled fields", async ({ page }) => {
  await installSurveyReviewMock(page);
  await page.goto("/survey/review/doc-pro");
  await expect(page.getByTestId("focused-item")).toBeVisible();

  // Open the correction editor and reach the fields by their accessible labels.
  await page.getByTestId("action-correct").click();
  await expect(page.getByLabel("Corrected normalized value")).toBeVisible();
  await expect(page.getByLabel("Reason (required)")).toBeVisible();

  // The overlay exposes a non-visual text alternative of its findings.
  await expect(page.getByTestId("overlay-alt-summary")).toContainText("Stated lot area");

  // Keyboard: focus the reason field and type without a mouse.
  await page.getByLabel("Reason (required)").focus();
  await page.keyboard.type("Corrected via keyboard.");
  await expect(page.getByTestId("correction-reason")).toHaveValue("Corrected via keyboard.");
});

test("SC-S7: critical warnings stay visible at a phone viewport", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await installSurveyReviewMock(page);
  await page.goto("/survey/review/doc-pro");

  await expect(page.getByTestId("review-topbar")).toBeVisible();
  // The conflict and the blocked/provisional downstream impact are not hidden to save space.
  await expect(page.getByTestId("check-area_vs_stated")).toContainText("Conflict");
  await expect(page.getByTestId("downstream-impact")).toBeVisible();
  await expect(page.getByTestId("downstream-far_max")).toBeVisible();
});
