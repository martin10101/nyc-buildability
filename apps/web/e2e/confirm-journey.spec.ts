import { expect, test } from "@playwright/test";
import { expectProfile, lookup } from "./helpers";

/**
 * S1 (M2-T002): the Confirm screen (PRODUCT_FLOW step 2) is reachable from
 * the Property screen result and renders the compact property card against
 * the recorded-official-fixture harness (real API, real builder): identity,
 * BIN/geometry honesty, lot and building summaries with units and coverage
 * labels, split-zone districts, landmark/flood/pending flags, conflicts,
 * the always-visible coverage legend, only-unanswerable questions, and the
 * honestly-labeled (non-persisting) confirm affordance.
 */

test("S1: Property result leads to the Confirm screen with the full compact card", async ({
  page,
}) => {
  await lookup(page, "1000010010");
  await expectProfile(page);

  // One clear next action on the profile.
  await page.getByTestId("confirm-link").click();
  await expect(page).toHaveURL(/\/property\/confirm\?bbl=1000010010/);
  await expect(page.getByTestId("confirm-card")).toBeVisible({ timeout: 15_000 });

  // Step framing + internal banner + PRD section 29 disclaimer retained.
  await expect(page.getByText("Step 2 — Confirm the property")).toBeVisible();
  await expect(page.getByTestId("internal-banner")).toBeVisible();
  await expect(
    page.getByText(/This platform provides preliminary development and zoning feasibility/),
  ).toBeVisible();

  // Identity: canonical address; BIN and geometry honestly unknown.
  await expect(page.getByTestId("confirm-identity")).toContainText("BBL 1000010010");
  await expect(page.getByTestId("confirm-identity")).toContainText("140 CARDER ROAD");
  await expect(page.getByTestId("confirm-bin")).toContainText("Not yet retrieved");
  await expect(page.getByTestId("confirm-geometry")).toContainText(
    "Geometry of type Point is recorded for this lot from the official source — only recorded geometry is shown; a parcel outline is never drawn from assumptions.",
  );

  // Lot summary with units and human labels.
  await expect(page.getByTestId("confirm-lot")).toContainText("Lot area");
  await expect(page.getByTestId("confirm-lot")).toContainText("7,577,714");
  await expect(page.getByTestId("confirm-lot")).toContainText("square feet");

  // Zoning chips for the split-zone lot.
  await expect(page.locator(".zoning-chip-code", { hasText: "R3-2" })).toBeVisible();
  await expect(page.locator(".zoning-chip-code", { hasText: "C4-1" })).toBeVisible();
  await expect(page.locator(".zoning-chip-code", { hasText: "GI" })).toBeVisible();

  // Flags: landmark/flood values from the official capture; pending
  // land-use honestly declared unretrievable (no connector yet).
  await expect(page.getByTestId("confirm-flags")).toContainText("INDIVIDUAL LANDMARK");
  await expect(page.getByTestId("confirm-flags")).toContainText(
    "2007 FIRM flood flag",
  );
  await expect(page.getByTestId("confirm-pending-flag")).toContainText(
    "never assumed none",
  );

  // Conflicts stay visible with the explicit empty state.
  await expect(page.getByText("No cross-source conflicts were detected")).toBeVisible();

  // D3: the coverage legend is visible WITHOUT hover, with the exact enum
  // and its plain-language gloss.
  const legend = page.getByTestId("coverage-legend");
  await expect(legend).toBeVisible();
  await expect(legend).toContainText("conditional");
  await expect(legend).toContainText("Official source fact, not yet professionally reviewed.");

  // Questions: only what official data cannot answer; honest persistence.
  await expect(page.getByTestId("confirm-questions")).toContainText(
    "What do you intend to build or change?",
  );
  await expect(page.getByTestId("confirm-disabled-button")).toBeDisabled();
  await expect(page.getByTestId("confirm-persistence-note")).toContainText(
    "cannot be saved yet",
  );
});

test("S1: per-fact provenance drill-down works on the Confirm card", async ({ page }) => {
  await page.goto("/property/confirm?bbl=1000010010");
  await expect(page.getByTestId("confirm-card")).toBeVisible({ timeout: 15_000 });

  const details = page
    .getByTestId("confirm-lot")
    .locator("details", { hasText: "Source for Lot area" });
  await details.locator("summary").click();
  await expect(details).toContainText("nyc-dcp-pluto-soda");
  await expect(details).toContainText("lotarea");
  await expect(details).toContainText("26v1");
  await expect(details).toContainText("2026-07-16T12:00:00Z");
});

test("Confirm screen without a valid BBL parameter shows an honest error with the way back", async ({
  page,
}) => {
  await page.goto("/property/confirm");
  await expect(page.getByTestId("confirm-bad-param")).toBeVisible();
  await expect(page.getByTestId("confirm-bad-param")).toContainText("None was provided");

  await page.goto("/property/confirm?bbl=12ab");
  await expect(page.getByTestId("confirm-bad-param")).toBeVisible();
  await expect(page.getByTestId("confirm-bad-param")).toContainText(
    "not a valid BBL",
  );
  // Recovery: the link returns to the Property screen.
  await page.getByRole("link", { name: "Go to property lookup" }).click();
  await expect(page.getByLabel("BBL", { exact: true })).toBeVisible();
});

test("Confirm screen renders API failure states (no_match via real API) with recovery", async ({
  page,
}) => {
  await page.goto("/property/confirm?bbl=5999999999");
  await expect(page.getByTestId("state-no-match")).toBeVisible({ timeout: 15_000 });
  await expect(page.getByTestId("confirm-card")).toHaveCount(0);
  await expect(
    page.getByRole("link", { name: /Back to property lookup/ }),
  ).toBeVisible();
});
