import { expect, test, type Page } from "@playwright/test";
import profileFixture from "../../../packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json";

// D-04 (plan M1-13) lot-choice + site-facts setup is behind
// INTERNAL_LOT_SITE_SETUP_ENABLED, which the e2e web server does NOT set, so the
// feature is OFF — the production-default state. This journey proves a reviewer
// cannot reach it from the dashboard, and a deep link gets the plain
// not-available view (a client query can never enable a disabled server feature,
// same contract as D-01). The flag-ON walkthrough waits on Lane C wiring a study
// into the harness (docs/lanes/requests/D-1.md).

const BBL = "1000010010";

async function mockProfile(page: Page): Promise<void> {
  await page.route("**/api/v1/properties/**", async (route) => {
    const last = new URL(route.request().url()).pathname.split("/").at(-1);
    // Only the base profile fetch; sub-resources (condo-records, lot-geometry) 404 cleanly.
    if (last !== BBL) return route.fulfill({ status: 404, json: { detail: "not found" } });
    const profile = structuredClone(profileFixture);
    profile.identity.bbl = BBL;
    await route.fulfill({ json: profile });
  });
}

test.describe("D-04 lot & site setup is OFF in production by default", () => {
  test("no dashboard opener; a deep link shows the not-available view", async ({ page }) => {
    await mockProfile(page);

    await page.goto(`/property/workspace?ruleeval=on&bbl=${BBL}`);
    await expect(page.getByTestId("connected-dashboard")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByRole("button", { name: /Lot & site setup/ })).toHaveCount(0);

    await page.goto(`/property/workspace?ruleeval=on&bbl=${BBL}&tool=lotsite`);
    await expect(page.getByTestId("connected-dashboard")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText("Lot & site setup is not available in this version")).toBeVisible();
    await expect(page.getByTestId("lot-site-setup")).toHaveCount(0);
  });
});
