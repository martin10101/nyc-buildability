import { expect, test, type Page } from "@playwright/test";
import { expectProfile, tabUntil } from "./helpers";

/**
 * M5-T002 human journeys against the recorded-official-fixture harness (real API,
 * real profile builder, real deterministic rule evaluator, real scenario builder;
 * the only seam is the server-side spatial-substrate provider, overridden with
 * the faithful M2-T013 substrate shapes the accepted M4-T005 pack uses). NOT a
 * frontend mock.
 *
 * The scenario surface renders here only when BOTH (a) the frontend env flag
 * INTERNAL_SCENARIO_UI is on for the web test server AND (b) the request opts in
 * with `?scenario=on`. The server flag INTERNAL_SCENARIO_ENABLED is enabled by
 * the harness (e2e/harness/fixture_api.py build_app).
 *
 * NOTE (documented in the producer report): rendering these journeys additionally
 * requires (1) the property-screen render wiring in
 * apps/web/src/components/property/PropertyLookup.tsx and (2) INTERNAL_SCENARIO_UI=1
 * in playwright.config.ts webServer env — both files are OUTSIDE this task's
 * allowed_paths, so these journeys are gated on that out-of-scope wiring. The
 * flag-off spec (scenario-flag-off.spec.ts) proves the no-render / no-fetch
 * guarantee regardless.
 */

async function lookupWithScenario(page: Page, bbl: string): Promise<void> {
  await page.goto("/property?scenario=on");
  await page.getByLabel("BBL", { exact: true }).fill(bbl);
  await page.getByRole("button", { name: "Look up property" }).click();
}

test("AS-8: preliminary journey — the draft cap is shown VERBATIM, never Verified, with provenance", async ({
  page,
}) => {
  // BBL 1000010100 (F01) -> confident single R5 district substrate -> preliminary.
  await lookupWithScenario(page, "1000010100");
  await expectProfile(page);

  await expect(page.getByTestId("scenario-panel")).toBeVisible();
  await expect(page.getByTestId("scenario-state-preliminary_cap")).toBeVisible({ timeout: 15_000 });

  // Prominent DRAFT / not-an-envelope framing; coverage by value, not color alone.
  await expect(page.getByTestId("scenario-draft-banner")).toContainText(
    "DRAFT — not a final legal determination and not a buildable envelope",
  );
  await expect(page.getByTestId("scenario-result")).toContainText("conditional");

  // The draft cap is surfaced verbatim (15,000 sq ft from the R5 fixture path).
  await expect(page.getByTestId("scenario-cap-value")).toContainText("15,000");
  await expect(page.getByTestId("scenario-cap-label")).toContainText(
    "DRAFT maximum residential ZONING-FLOOR-AREA CAP",
  );

  // Provenance drill-down is reachable and carries the legal-source citation.
  const provenance = page.locator('details[data-testid="scenario-provenance"]');
  await provenance.locator("summary").click();
  await expect(provenance).toContainText("23-21");

  // The property profile above is fully usable alongside the draft surface.
  await expect(page.getByTestId("confirm-link")).toBeVisible();
});

test("AS-9: professional-review journey — no substrate -> honest no_scenario, no fabricated value", async ({
  page,
}) => {
  // BBL 1000010101 (F04) has no substrate wired -> honest professional-review.
  await lookupWithScenario(page, "1000010101");
  await expectProfile(page);
  await expect(page.getByTestId("scenario-state-professional_review")).toBeVisible({
    timeout: 15_000,
  });
  await expect(page.getByTestId("scenario-cap")).toHaveCount(0); // never a fabricated value
});

test("AS-9 recoverable failure: a failed draft scenario leaves the profile usable and retries", async ({
  page,
}) => {
  let failed = false;
  await page.route("**/scenario", async (route) => {
    if (!failed) {
      failed = true;
      await route.abort("failed");
      return;
    }
    await route.continue();
  });

  await lookupWithScenario(page, "1000010100");
  await expectProfile(page);

  await expect(page.getByTestId("confirm-link")).toBeVisible();
  await expect(page.getByTestId("scenario-state-network_error")).toBeVisible({ timeout: 15_000 });

  await page.getByRole("button", { name: "Retry draft scenario" }).click();
  await expect(page.getByTestId("scenario-result")).toBeVisible({ timeout: 15_000 });
});

test("a11y: the draft scenario announces itself politely and NEVER steals focus from the profile", async ({
  page,
}) => {
  await page.goto("/property?scenario=on");
  await tabUntil(page, { id: "bbl-input" });
  await page.keyboard.type("1000010100");
  await page.keyboard.press("Enter");
  await expectProfile(page);

  await expect(page.getByTestId("outcome-announcer")).toHaveText(
    /profile loaded for BBL 1000010100/,
  );
  await expect(page.getByTestId("scenario-announcer")).toHaveText(/Draft scenario loaded/, {
    timeout: 15_000,
  });

  // The background scenario load did NOT hijack focus: it stays on the profile heading.
  const onProfileHeading = await page.evaluate(() => {
    const el = document.activeElement as HTMLElement | null;
    return el?.hasAttribute("data-outcome-heading") ?? false;
  });
  expect(onProfileHeading).toBe(true);
});
