import { expect, test } from "@playwright/test";
import { installSurveyReviewMock } from "./survey-review-helpers";

/**
 * SC-S3 authorization + SC-S4 no-auto-verified (task M2-T016). An unauthorized
 * (read-only) principal cannot accept/correct/reject or confirm; the
 * confirm/document-reject actions are offered only to the designated
 * professional role (server-enforced, UI-mirrored). Nothing is labeled
 * "Verified" — auto-extracted facts read "Unconfirmed evidence" everywhere.
 */

test("SC-S3: a read-only consumer cannot act, and the confirm action is not offered", async ({ page }) => {
  await installSurveyReviewMock(page);
  await page.goto("/survey/review/doc-consumer");

  await expect(page.getByTestId("focused-item")).toBeVisible();
  await expect(page.getByTestId("action-accept")).toBeDisabled();
  await expect(page.getByTestId("action-correct")).toBeDisabled();
  await expect(page.getByTestId("action-reject")).toBeDisabled();
  await expect(page.getByTestId("action-disabled-reason")).toBeVisible();

  // The confirm control is not offered; the reason is stated, not silently hidden.
  await expect(page.getByTestId("action-confirm-document")).toHaveCount(0);
  await expect(page.getByTestId("confirm-capability-note")).toBeVisible();
});

test("SC-S3: a preparer can correct facts but cannot confirm the document", async ({ page }) => {
  await installSurveyReviewMock(page);
  await page.goto("/survey/review/doc-user");

  await expect(page.getByTestId("focused-item")).toBeVisible();
  await expect(page.getByTestId("action-correct")).toBeEnabled();
  await expect(page.getByTestId("action-confirm-document")).toHaveCount(0);
  await expect(page.getByTestId("confirm-capability-note")).toBeVisible();
});

test("SC-S4: facts read 'Unconfirmed evidence' and nothing is labeled 'Verified'", async ({ page }) => {
  await installSurveyReviewMock(page);
  await page.goto("/survey/review/doc-pro");

  await expect(page.getByTestId("review-topbar")).toBeVisible();
  await expect(page.getByTestId("fact-confirmation-sev:doc:p1:1")).toContainText("Unconfirmed evidence");
  // No status/label is ever the standalone word "Verified" for a survey fact.
  await expect(page.getByText("Verified", { exact: true })).toHaveCount(0);

  // The professional sees a confirm control, but it is gated by the H5 precondition.
  await expect(page.getByTestId("action-confirm-document")).toBeDisabled();
  await expect(page.getByTestId("confirm-blocked-explanation")).toContainText("Stated lot area");
});
