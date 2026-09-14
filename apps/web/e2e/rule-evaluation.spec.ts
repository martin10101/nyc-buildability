import { expect, test, type Page } from "@playwright/test";
import { expectProfile, tabUntil } from "./helpers";

// Same real fixture API/evaluator journeys as M4-T005. M5-T029 changes only
// the entry/navigation path: the draft result lives under Zoning, with full
// calculation evidence under Evidence. The flag-off suite remains unchanged.
async function lookupWithRuleEval(page: Page, bbl: string): Promise<void> {
  await page.goto("/property?ruleeval=on");
  await page.getByText("Search by tax lot (BBL)", { exact: true }).click();
  await page.getByLabel("BBL", { exact: true }).fill(bbl);
  await page.getByRole("button", { name: "Open property", exact: true }).click();
  await expectProfile(page);
}
async function openDraft(page: Page) {
  await page.getByRole("navigation", { name: "Architect workspace" }).getByRole("link", { name: "Zoning", exact: true }).click();
  await page.getByText("Draft rule result, conflicts and applicability", { exact: true }).click();
}

test("AS-3: applicable-draft journey — DRAFT, never Verified, with provenance", async ({ page }) => {
  await lookupWithRuleEval(page, "1000010100");
  await openDraft(page);
  await expect(page.getByTestId("rule-eval-state-applicable_draft")).toBeVisible({ timeout: 15_000 });
  await expect(page.getByTestId("rule-eval-draft-banner")).toContainText("DRAFT — not a final legal determination");
  await expect(page.getByTestId("rule-eval-result")).toContainText("conditional");
  await expect(page.getByTestId("rule-eval-outputs")).toContainText("max_residential_far");
  await expect(page.getByTestId("rule-eval-outputs")).toContainText("1.5");
  const provenance = page.locator('details[data-testid="rule-eval-provenance"]');
  await provenance.locator("summary").click();
  await expect(provenance).toContainText("Input fingerprint");
  await expect(provenance).toContainText("23-21");
  await expect(page.getByRole("link", { name: "Property facts", exact: true })).toBeVisible();
});

test("AS-8: spatial-uncertainty journey — split-lot share RANGES preserved", async ({ page }) => {
  await lookupWithRuleEval(page, "1000010010");
  await openDraft(page);
  await expect(page.getByTestId("rule-eval-state-spatial_uncertainty")).toBeVisible({ timeout: 15_000 });
  const candidates = page.getByTestId("rule-eval-candidates");
  await expect(candidates).toContainText("R5");
  await expect(candidates).toContainText("0.55–0.65");
  await expect(candidates).toContainText("R6");
  await expect(candidates).toContainText("0.35–0.45");
  await expect(page.getByTestId("rule-eval-result")).toContainText("Spatial uncertainty");
});

test("AS-6: no-substrate journey — professional-review fail-safe, no fabricated value", async ({ page }) => {
  await lookupWithRuleEval(page, "1000010101");
  await openDraft(page);
  await expect(page.getByTestId("rule-eval-state-missing_evidence")).toBeVisible({ timeout: 15_000 });
  await expect(page.getByTestId("rule-eval-result")).toContainText("professional review required");
  await expect(page.getByTestId("rule-eval-outputs")).toHaveCount(0);
});

test("recoverable failure: failed draft evaluation preserves property facts and retries independently", async ({ page }) => {
  let failed = false;
  await page.route("**/rule-evaluation", async route => {
    if (!failed) { failed = true; await route.abort("failed"); return; }
    await route.continue();
  });
  await lookupWithRuleEval(page, "1000010100");
  await expect(page.getByRole("link", { name: "Property facts", exact: true })).toBeVisible();
  await expect(page.getByTestId("rule-eval-state-network_error")).toBeVisible({ timeout: 15_000 });
  const unrelated: string[] = [];
  page.on("request", request => { if (/\/api\/v1\/properties\/\d{10}$|\/scenario$/.test(request.url())) unrelated.push(request.url()); });
  await page.getByRole("button", { name: "Retry draft evaluation" }).click();
  await expect(page.getByTestId("rule-eval-announcer")).toHaveText(/Draft rule evaluation loaded/, { timeout: 15_000 });
  expect(unrelated).toHaveLength(0);
  await openDraft(page);
  await expect(page.getByTestId("rule-eval-result")).toBeVisible();
});

test("a11y: background draft arrival announces politely without stealing profile focus", async ({ page }) => {
  await page.goto("/property?ruleeval=on");
  await tabUntil(page, { textContains: "Search by tax lot (BBL)" });
  await page.keyboard.press("Enter");
  await tabUntil(page, { id: "architect-bbl" });
  await page.keyboard.type("1000010100");
  await page.keyboard.press("Enter");
  await expectProfile(page);
  await expect(page.getByTestId("outcome-announcer")).toHaveText(/profile loaded for BBL 1000010100/);
  await expect(page.getByTestId("rule-eval-announcer")).toHaveText(/Draft rule evaluation loaded/, { timeout: 15_000 });
  expect(await page.evaluate(() => document.activeElement?.hasAttribute("data-outcome-heading") ?? false)).toBe(true);
  // Keyboard reaches the new Evidence navigation, then a native disclosure.
  await tabUntil(page, { textContains: "Evidence" });
  await page.keyboard.press("Enter");
  await expect(page.getByRole("heading", { name: "How this was calculated" })).toBeVisible();
  await tabUntil(page, { textContains: "Full rule-evaluation document" });
  await page.keyboard.press("Enter");
  await expect(page.locator('details:has(> summary:text-is("Full rule-evaluation document"))')).toContainText("input_fingerprint");
});
