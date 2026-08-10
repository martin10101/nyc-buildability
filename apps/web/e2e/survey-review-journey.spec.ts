import { expect, test } from "@playwright/test";
import { installSurveyReviewMock } from "./survey-review-helpers";

/**
 * SC-S1 primary journey + SC-S2 immutability + SC-S5 downstream honesty +
 * SC-S6 conflict display (task M2-T016). A reviewer opens a needs_review survey,
 * sees the overlay + highlighted conflict, accepts a clean fact, corrects the
 * conflict fact with a reason, rejects an advisory detection, watches the
 * dependent conclusions recalculate, and confirms the document — with the audit
 * trail and immutable original intact throughout. Runs against the mocked review
 * client (spec-shaped fixtures), no live backend.
 */

test("SC-S1: full reviewer journey with audit, recalculation, and confirmation", async ({ page }) => {
  await installSurveyReviewMock(page);
  await page.goto("/survey/review/doc-pro");

  await expect(page.getByTestId("review-topbar")).toBeVisible();
  await expect(page.getByTestId("document-state-badge")).toContainText("Needs review");

  // Overlay renders the extracted geometry; the conflict fact is focused first.
  await expect(page.getByTestId("overlay-mark-sev:doc:p1:2")).toBeVisible();
  await expect(page.getByTestId("focused-heading")).toContainText("Stated lot area");

  // SC-S6: the conflict is visible, plain-language, and NOT dismissible.
  await expect(page.getByTestId("check-area_vs_stated")).toContainText("Conflict");
  await expect(page.getByTestId("conflict-resolve-area_vs_stated")).toBeVisible();
  await expect(page.getByRole("button", { name: /dismiss|acknowledge|ignore/i })).toHaveCount(0);

  // SC-S5: downstream conclusions are blocked / provisional on the conflict.
  await expect(page.getByTestId("downstream-far_max")).toHaveAttribute("data-status", "blocked");
  await expect(page.getByTestId("downstream-lot_coverage")).toHaveAttribute("data-status", "provisional");

  // Accept a clean fact.
  await page.getByTestId("fact-row-sev:doc:p1:1").click();
  await page.getByTestId("action-accept").click();

  // Correct the conflict fact with a required reason.
  await page.getByTestId("fact-row-sev:doc:p1:2").click();
  await page.getByTestId("action-correct").click();
  await page.getByTestId("correction-value").fill("4800");
  await page.getByTestId("correction-reason").fill("OCR misread the stated area digit.");
  await page.getByTestId("correction-submit").click();

  // SC-S2: the append-only correction history is recorded and the original is preserved.
  await expect(page.getByTestId("correction-chain")).toContainText("OCR misread");
  await expect(page.getByTestId("original-value")).toContainText("5,000 SF");
  await expect(page.getByTestId("current-value")).toContainText("4800");

  // SC-S5: the dependent conclusions clear THROUGH recalculation.
  await expect(page.getByTestId("downstream-far_max")).toHaveAttribute("data-status", "cleared");
  await expect(page.getByTestId("downstream-lot_coverage")).toHaveAttribute("data-status", "cleared");

  // Reject the advisory AI detection with a reason.
  await page.getByTestId("fact-row-sev:doc:p1:3").click();
  await page.getByTestId("action-reject").click();
  await page.getByTestId("reject-fact-reason").fill("AI north-arrow guess is not usable.");
  await page.getByTestId("reject-fact-submit").click();
  await expect(page.getByTestId("fact-confirmation-sev:doc:p1:3")).toContainText("Rejected");

  // Confirm the document once every material fact promotes.
  const confirm = page.getByTestId("action-confirm-document");
  await expect(confirm).toBeEnabled();
  await confirm.click();
  await expect(page.getByTestId("document-state-badge")).toContainText("Professionally confirmed");
  await expect(page.getByTestId("confirmed-note")).toBeVisible();

  // The audit trail replays the lifecycle to the confirmed state.
  await expect(page.getByTestId("state-history")).toContainText("Professionally confirmed");
});
