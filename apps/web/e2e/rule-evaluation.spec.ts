import { expect, test, type Page } from "@playwright/test";
import { expectProfile, tabUntil } from "./helpers";

/**
 * M4-T005 phase 3 human journeys against the recorded-official-fixture harness
 * (real API, real profile builder, real deterministic rule evaluator; the only
 * seam is the server-side spatial-substrate provider, overridden with the
 * faithful M2-T013 substrate shapes the accepted phase-2 pack uses). NOT a
 * frontend mock.
 *
 * The frontend flag is enabled for this test server (INTERNAL_RULE_EVAL_UI=1,
 * playwright.config.ts) AND each journey opts in per request with `?ruleeval=on`
 * — so the surface renders here while every unrelated journey (no opt-in) stays
 * untouched. The server flag INTERNAL_RULE_EVAL_ENABLED is on in the harness.
 */

/** Navigate to the Property screen WITH the rule-eval surface opted in, and
 * submit one BBL lookup. */
async function lookupWithRuleEval(page: Page, bbl: string): Promise<void> {
  await page.goto("/property?ruleeval=on");
  await page.getByLabel("BBL", { exact: true }).fill(bbl);
  await page.getByRole("button", { name: "Look up property" }).click();
}

test("AS-3: applicable-draft journey — a DRAFT determination, never Verified, with provenance", async ({
  page,
}) => {
  // BBL 1000010100 (F01) -> confident single R5 district substrate.
  await lookupWithRuleEval(page, "1000010100");
  await expectProfile(page);

  // The optional surface loads and shows the applicable-draft state.
  await expect(page.getByTestId("rule-eval-panel")).toBeVisible();
  await expect(page.getByTestId("rule-eval-state-applicable_draft")).toBeVisible({
    timeout: 15_000,
  });

  // Prominent DRAFT framing; the draft coverage status is shown by value, not
  // color alone; nothing claims Verified/final.
  await expect(page.getByTestId("rule-eval-draft-banner")).toContainText(
    "DRAFT — not a final legal determination",
  );
  await expect(page.getByTestId("rule-eval-result")).toContainText("conditional");

  // The draft computed output is shown, framed as draft (not a final value).
  await expect(page.getByTestId("rule-eval-outputs")).toContainText("max_residential_far");
  await expect(page.getByTestId("rule-eval-outputs")).toContainText("1.5");

  // Provenance drill-down is reachable and carries the legal-source citation.
  const provenance = page.locator(
    'details[data-testid="rule-eval-provenance"]',
  );
  await provenance.locator("summary").click();
  await expect(provenance).toContainText("Input fingerprint");
  await expect(provenance).toContainText("23-21");

  // The property profile above is fully usable alongside the draft surface.
  await expect(page.getByTestId("confirm-link")).toBeVisible();
});

test("AS-8: spatial-uncertainty journey — split-lot share RANGES preserved, never collapsed", async ({
  page,
}) => {
  // BBL 1000010010 (F05, Governors Island split lot) -> split R5/R6 substrate.
  await lookupWithRuleEval(page, "1000010010");
  await expectProfile(page);

  await expect(page.getByTestId("rule-eval-state-spatial_uncertainty")).toBeVisible({
    timeout: 15_000,
  });

  const candidates = page.getByTestId("rule-eval-candidates");
  await expect(candidates).toContainText("R5");
  await expect(candidates).toContainText("0.55–0.65"); // full range, not a point
  await expect(candidates).toContainText("R6");
  await expect(candidates).toContainText("0.35–0.45");

  // No single confident district is asserted.
  await expect(page.getByTestId("rule-eval-result")).toContainText("Spatial uncertainty");
});

test("AS-6: default (no substrate) journey — professional-review fail-safe, no fabricated value", async ({
  page,
}) => {
  // BBL 1000010101 (F04) has no substrate wired -> honest fail-safe.
  await lookupWithRuleEval(page, "1000010101");
  await expectProfile(page);
  await expect(page.getByTestId("rule-eval-state-missing_evidence")).toBeVisible({
    timeout: 15_000,
  });
  await expect(page.getByTestId("rule-eval-result")).toContainText(
    "professional review required",
  );
});

test("recoverable failure: a failed draft evaluation leaves the profile usable and retries", async ({
  page,
}) => {
  // Fail ONLY the rule-evaluation request, and only the first time.
  let failed = false;
  await page.route("**/rule-evaluation", async (route) => {
    if (!failed) {
      failed = true;
      await route.abort("failed");
      return;
    }
    await route.continue();
  });

  await lookupWithRuleEval(page, "1000010100");
  await expectProfile(page);

  // The profile is fully usable despite the draft-surface failure.
  await expect(page.getByTestId("confirm-link")).toBeVisible();
  await expect(page.getByTestId("rule-eval-state-network_error")).toBeVisible({
    timeout: 15_000,
  });

  // Retry re-issues only the draft-evaluation request and reaches the result.
  await page.getByRole("button", { name: "Retry draft evaluation" }).click();
  await expect(page.getByTestId("rule-eval-result")).toBeVisible({ timeout: 15_000 });
});

test("a11y: the draft surface announces itself politely and NEVER steals focus from the profile", async ({
  page,
}) => {
  // Keyboard-only: reach the BBL input, type, submit.
  await page.goto("/property?ruleeval=on");
  await tabUntil(page, { id: "bbl-input" });
  await page.keyboard.type("1000010100");
  await page.keyboard.press("Enter");
  await expectProfile(page);

  // The property-profile announcer and the independent rule-eval announcer are
  // two distinct live regions; the draft arrival announces through its own.
  await expect(page.getByTestId("outcome-announcer")).toHaveText(
    /profile loaded for BBL 1000010100/,
  );
  await expect(page.getByTestId("rule-eval-announcer")).toHaveText(
    /Draft rule evaluation loaded/,
    { timeout: 15_000 },
  );

  // The background draft load did NOT hijack focus: it stays on the profile
  // heading (the property flow's focus target), never the draft panel.
  const onProfileHeading = await page.evaluate(() => {
    const el = document.activeElement as HTMLElement | null;
    return el?.hasAttribute("data-outcome-heading") ?? false;
  });
  expect(onProfileHeading).toBe(true);

  // The draft provenance disclosure is keyboard-reachable and opens with Enter.
  await tabUntil(page, { textContains: "Evaluated input and source provenance" });
  await page.keyboard.press("Enter");
  await expect(
    page.locator('details[data-testid="rule-eval-provenance"]'),
  ).toContainText("Input fingerprint");
});
