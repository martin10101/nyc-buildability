import { expect, test } from "@playwright/test";
import { expectProfile, lookup, tabUntil } from "./helpers";

/**
 * BROWSER journeys for the Compare screen (PRODUCT_FLOW step 3), against the
 * recorded-official-fixture harness: the real FastAPI app, the real PLUTO
 * connector over committed official captures, the real profile builder, the
 * real deterministic rule evaluator and the real scenario builder. NOT a
 * frontend mock — the only overridden seams are the PLUTO fetcher and the
 * server-side spatial substrate, both already in place for the accepted
 * rule-evaluation journeys.
 *
 * WHY THIS FILE EXISTS (task M5-T004 rework, G3 finding 3b / G4 MEDIUM-6).
 * None of the 18 existing Playwright specs navigated to /property/compare, and
 * the harness enabled INTERNAL_RULE_EVAL_ENABLED but not
 * INTERNAL_SCENARIO_ENABLED — so no browser could reach this screen ANYWHERE in
 * the repository, in CI or locally, and G3 owed one of its eight steps with no
 * way for anyone to discharge it. The harness flag is now set
 * (e2e/harness/fixture_api.py) and these journeys walk the screen.
 *
 * BBL 1000010100 is the F01 single-lot capture; the harness substrate assigns
 * it a confident single R5 district, which is what the accepted
 * rule-evaluation journey already relies on. Its zoning-floor-area cap is
 * asserted as a real grouped number rather than a hard-coded magnitude: the
 * point of the assertion is that a NUMBER reached the DOM and the absence
 * marker did not, which is what a display-side regression would break.
 */

const COMPARE_BBL = "1000010100";

test("AS-6: Confirm 'Next step' carries the analyst into Compare for the same BBL", async ({
  page,
}) => {
  await lookup(page, COMPARE_BBL);
  await expectProfile(page);

  await page.getByTestId("confirm-link").click();
  await expect(page.getByTestId("confirm-card")).toBeVisible({ timeout: 15_000 });

  // The dead-end is gone: one clear, labelled, keyboard-reachable next action.
  const next = page.getByTestId("confirm-next-compare");
  await expect(next).toBeVisible();
  await next.click();

  await expect(page).toHaveURL(new RegExp(`/property/compare\\?bbl=${COMPARE_BBL}`));
  await expect(page.getByTestId("scenario-result")).toBeVisible({ timeout: 20_000 });

  // IDENTITY IS BOUND TO THE DOCUMENT, not to the URL: the heading shows the
  // BBL the document states it was evaluated for, and no mismatch is reported.
  await expect(page.getByTestId("scenario-heading-bbl")).toHaveText(COMPARE_BBL);
  await expect(page.getByTestId("scenario-bbl-mismatch")).toHaveCount(0);
  await expect(page.getByTestId("scenario-bbl-not-stated")).toHaveCount(0);
});

test("the Compare screen states the document's own completeness, reasons, constraints and gaps", async ({
  page,
}) => {
  await page.goto(`/property/compare?bbl=${COMPARE_BBL}`);
  await expect(page.getByTestId("scenario-result")).toBeVisible({ timeout: 20_000 });

  // The document's OWN data-completeness verdict is on the page that carries
  // the number, not only on Step 1.
  const completeness = page.getByTestId("scenario-completeness");
  await expect(completeness).toBeVisible();
  await expect(completeness).toContainText("official inputs");

  // The engine's own reasons render on the branch that shows a number.
  await expect(page.getByTestId("scenario-reasons-section")).toBeVisible();

  // Constraints render with their notes — including the anti-inference warning
  // that only the note carries.
  await expect(page.getByTestId("scenario-constraints")).toBeVisible();
  await expect(page.getByTestId("scenario-constraints-section")).toContainText(
    "MUST NOT be inferred, defaulted, or estimated",
  );

  // Declared assumptions are stated even when there are none.
  await expect(page.getByTestId("scenario-assumptions-section")).toBeVisible();

  // The integrity check shows the tolerance its method string refers to.
  await expect(page.getByTestId("scenario-integrity-tolerance")).toBeVisible();

  // The full coverage matrix renders, and the missing families are called out.
  await expect(page.getByTestId("coverage-matrix-all")).toBeVisible();
  await expect(page.getByTestId("coverage-gaps")).toBeVisible();

  // Status is text, never color alone.
  await expect(page.getByTestId("coverage-label-data_conflict")).toContainText(
    "data_conflict",
  );
});

test("AS-1: the draft cap renders as a labelled number with a named objective and a citation", async ({
  page,
}) => {
  await page.goto(`/property/compare?bbl=${COMPARE_BBL}`);
  await expect(page.getByTestId("scenario-card-1")).toBeVisible({ timeout: 20_000 });

  // A real grouped number reached the DOM — not the absence marker.
  const cap = page.getByTestId("scenario-cap-value");
  await expect(cap).toHaveText(/^[0-9][0-9,]*(\.[0-9]+)?$/);

  // The draft caveat accompanies it as TEXT.
  await expect(page.getByTestId("scenario-draft-label")).toBeVisible();
  await expect(page.getByTestId("scenario-card-1")).toContainText(
    "Draft maximum residential zoning floor-area cap",
  );

  // The optimized objective is NAMED (never a bare "best"/maximum).
  await expect(page.getByTestId("scenario-objective-name")).toHaveText(
    "max_residential_floor_area_sq_ft",
  );

  // The citation chain for that number is reachable and carries the source.
  const provenance = page.locator('details[data-testid="scenario-provenance"]');
  await provenance.locator("summary").click();
  await expect(provenance).toContainText("Input fingerprint");
  await expect(provenance).toContainText("23-21");
  await expect(page.getByTestId("scenario-citations")).toBeVisible();
});

test("AS-8: the outcome is announced, focus lands on the heading, and the next action is keyboard-reachable", async ({
  page,
}) => {
  await page.goto(`/property/compare?bbl=${COMPARE_BBL}`);
  await expect(page.getByTestId("scenario-result")).toBeVisible({ timeout: 20_000 });

  const announcer = page.getByTestId("compare-announcer");
  await expect(announcer).toHaveAttribute("aria-live", "polite");
  await expect(announcer).toContainText("Compare loaded");

  // Focus was moved to the outcome heading, never dropped to <body>.
  await expect(
    page.locator("[data-outcome-heading]:focus"),
  ).toHaveCount(1);

  // The way back is reachable by keyboard alone.
  await tabUntil(page, { textContains: "Back to the confirmed property" });
});

test("a Compare URL with no BBL is an honest card with a way out, never a blank screen", async ({
  page,
}) => {
  await page.goto("/property/compare");
  await expect(page.getByTestId("compare-bad-param")).toBeVisible({ timeout: 15_000 });
  await expect(page.getByRole("heading", { level: 1 })).toContainText(
    "No property selected",
  );
  await expect(page.getByTestId("scenario-result")).toHaveCount(0);
  await expect(page.getByRole("link", { name: "Go to property lookup" })).toBeVisible();
});
