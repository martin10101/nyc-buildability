import { expect, test } from "@playwright/test";
import { expectProfile, lookup } from "./helpers";

/**
 * S1 primary human journey against the recorded-official-fixture harness:
 * split-zone BBL 1000010010 (F05 live capture, Governors Island).
 */

test("S1: staged loading is shown while the profile is retrieved", async ({ page }) => {
  // Delay the real API response so the loading state is deterministic.
  await page.route("**/api/v1/properties/**", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 700));
    await route.continue();
  });
  await lookup(page, "1000010010");
  await expect(page.getByTestId("loading-stages")).toBeVisible();
  await expect(page.getByTestId("loading-stages")).toContainText(
    "BBL format checked",
  );
  await expect(page.getByTestId("loading-stages")).toContainText(
    "Retrieving the official property record",
  );
  await expectProfile(page);
});

test("S1: profile shows facts with units, coverage labels, banner, split-zone districts", async ({
  page,
}) => {
  await lookup(page, "1000010010");
  await expectProfile(page);

  // Identity.
  await expect(page.getByTestId("identity-card")).toContainText("BBL 1000010010");
  await expect(page.getByTestId("identity-card")).toContainText("140 CARDER ROAD");

  // Both districts of the split-zone lot plus the special district.
  await expect(page.locator(".zoning-chip-code", { hasText: "R3-2" })).toBeVisible();
  await expect(page.locator(".zoning-chip-code", { hasText: "C4-1" })).toBeVisible();
  await expect(page.locator(".zoning-chip-code", { hasText: "GI" })).toBeVisible();

  // Fact value with units and the exact PRD section 12 coverage wording.
  await expect(page.getByText("7,577,714").first()).toBeVisible();
  await expect(page.getByText("square feet").first()).toBeVisible();
  expect(await page.locator(".status-badge", { hasText: "conditional" }).count()).toBeGreaterThan(0);

  // data_completeness banner with the exact enum value.
  await expect(page.getByTestId("completeness-banner")).toContainText(
    "missing_noncritical",
  );

  // Conflicts section stays visible with an explicit empty state.
  await expect(page.getByText("No cross-source conflicts were detected")).toBeVisible();

  // Missing-inputs total is always shown.
  await expect(
    page.getByRole("heading", { name: /Missing official inputs \(24\)/ }),
  ).toBeVisible();
});

test("S1: provenance drill-down on lot area shows source, dataset, version, original value, retrieved_at", async ({
  page,
}) => {
  await lookup(page, "1000010010");
  await expectProfile(page);

  const details = page.locator("details", { hasText: "Source for Lot area" });
  await details.locator("summary").click();
  await expect(details).toContainText("nyc-dcp-pluto-soda");
  await expect(details).toContainText("lotarea");
  await expect(details).toContainText("7577714"); // original value verbatim
  await expect(details).toContainText("26v1"); // dataset version
  await expect(details).toContainText("2026-07-16T12:00:00Z"); // retrieved_at
  await expect(details).toContainText("64uk-42ks"); // dataset id (reproducibility)
  await expect(details).toContainText("data.cityofnewyork.us"); // request host only
});
