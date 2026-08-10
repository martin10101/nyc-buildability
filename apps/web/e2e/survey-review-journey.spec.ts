import { expect, test } from "@playwright/test";
import { DIGEST_PRO, installSurveyReviewMock } from "./survey-review-helpers";

/**
 * SC-S1 primary journey + SC-S2 immutability + SC-S5 downstream honesty +
 * SC-S6 conflict display (task M2-T016 rework). Reconciled to the shipped
 * backend: digest-keyed, per-fact downstream impact, a rejected fact blocks
 * confirmation (confirmation_rejected), and confirm succeeds only once every
 * material fact is resolved. Runs against the mocked review client, no live
 * backend.
 */

const CLEAN = "sev:doc:p1:1";
const AREA = "sev:doc:p1:2";
const NORTH = "sev:doc:p1:3";

function reviewUrl(digest: string): string {
  return `/survey/review/${encodeURIComponent(digest)}`;
}

test("SC-S1: accept, correct, reject with audit, recalculation, and honest blocked confirm", async ({ page }) => {
  await installSurveyReviewMock(page);
  await page.goto(reviewUrl(DIGEST_PRO));

  await expect(page.getByTestId("review-topbar")).toBeVisible();
  await expect(page.getByTestId("document-state-badge")).toContainText("Needs review");

  // Overlay renders geometry; F4: a non-color status glyph accompanies the mark.
  await expect(page.getByTestId(`overlay-mark-${AREA}`)).toBeVisible();
  await expect(page.getByTestId(`overlay-glyph-${AREA}`)).toBeVisible();

  // SC-S6: the conflict is visible, plain-language, and NOT dismissible.
  await expect(page.getByTestId("check-conflict")).toBeVisible();
  await expect(page.getByTestId("conflict-resolve")).toBeVisible();
  await expect(page.getByRole("button", { name: /dismiss|acknowledge|ignore/i })).toHaveCount(0);

  // SC-S5: the area fact blocks a dependent conclusion.
  await expect(page.getByTestId(`downstream-${AREA}`)).toHaveAttribute("data-status", "blocked");

  // Accept a clean fact — visible session affirmation (F2).
  await page.getByTestId(`fact-row-${CLEAN}`).click();
  await page.getByTestId("action-accept").click();
  await expect(page.getByTestId("accept-affirmed")).toBeVisible();

  // Correct the conflict fact with a required reason.
  await page.getByTestId(`fact-row-${AREA}`).click();
  await page.getByTestId("action-correct").click();
  await page.getByTestId("correction-value").fill("4800");
  await page.getByTestId("correction-reason").fill("OCR misread the stated area digit.");
  await page.getByTestId("correction-submit").click();

  // SC-S2: append-only correction history recorded, immutable original preserved.
  await expect(page.getByTestId("correction-chain")).toContainText("OCR misread");
  await expect(page.getByTestId("original-value")).toContainText("5,000 SF");
  await expect(page.getByTestId("current-value")).toContainText("4800");
  // SC-S5: the block clears to provisional through recalculation (re-read).
  await expect(page.getByTestId(`downstream-${AREA}`)).toHaveAttribute("data-status", "provisional");

  // Reject the advisory AI detection with a reason.
  await page.getByTestId(`fact-row-${NORTH}`).click();
  await page.getByTestId("action-reject").click();
  await page.getByTestId("reject-fact-reason").fill("AI north-arrow guess is not usable.");
  await page.getByTestId("reject-fact-submit").click();
  await expect(page.getByTestId(`fact-confirmation-${NORTH}`)).toContainText("Rejected");

  // Honest backend semantics: a rejected material fact BLOCKS confirmation.
  await expect(page.getByTestId("action-confirm-document")).toBeDisabled();
  await expect(page.getByTestId("confirm-blocked-explanation")).toContainText("North arrow orientation");
});

test("SC-S1: confirm succeeds once every fact is resolved, then reopen (edge 12)", async ({ page }) => {
  await installSurveyReviewMock(page);
  await page.goto(reviewUrl(DIGEST_PRO));
  await expect(page.getByTestId("review-topbar")).toBeVisible();

  // Resolve the conflict fact.
  await page.getByTestId(`fact-row-${AREA}`).click();
  await page.getByTestId("action-correct").click();
  await page.getByTestId("correction-value").fill("4800");
  await page.getByTestId("correction-reason").fill("resolve area");
  await page.getByTestId("correction-submit").click();
  await expect(page.getByTestId("correction-chain")).toBeVisible();

  // Resolve the unresolved fact.
  await page.getByTestId(`fact-row-${NORTH}`).click();
  await page.getByTestId("action-correct").click();
  await page.getByTestId("correction-value").fill("15");
  await page.getByTestId("correction-reason").fill("resolve orientation");
  await page.getByTestId("correction-submit").click();

  // F1: the dominant action now points to confirmation.
  await expect(page.getByTestId("dominant-action")).toContainText(/confirm or reject the document/i);

  const confirm = page.getByTestId("action-confirm-document");
  await expect(confirm).toBeEnabled();
  await confirm.click();
  await expect(page.getByTestId("document-state-badge")).toContainText("Professionally confirmed");
  await expect(page.getByTestId("confirmed-note")).toBeVisible();

  // Reopen (edge 12) returns the document to needs_review, visibly and audited.
  await page.getByTestId("action-reopen-document").click();
  await page.getByTestId("reopen-document-reason").fill("post-confirmation boundary contradiction");
  await page.getByTestId("reopen-document-submit").click();
  await expect(page.getByTestId("document-state-badge")).toContainText("Needs review");
});
