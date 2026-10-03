import { expect, test, type Page } from "@playwright/test";
import profileFixture from "../../../packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json";

/**
 * D-12 slice 2 flag-OFF proof. INTERNAL_HIDDEN_ISSUE_FLAGS_UI_ENABLED is NOT set on the
 * default :3000 server (playwright.config.ts) — the production-default state. This journey,
 * run by the `chromium` project, proves a reviewer cannot reach the "Hidden issues" tool from
 * the dashboard, a deep link gets the plain "not available" view, and NO request is ever made
 * to the hidden-issue-flags endpoint (a client query can never enable a disabled server
 * feature; same contract as D-01/D-04). The flag-ON walkthrough is hidden-issues.flag-on.spec.ts.
 *
 * A fresh spec is added rather than extending an existing flag-off spec: no existing flag-off
 * workspace spec asserts the hiddenissues tool list, and keeping this with the flag-on spec
 * keeps both halves of the D-12 journey in one place.
 */

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

test.describe("D-12 hidden issues are OFF in production by default", () => {
  test("no dashboard opener, a deep link shows the not-available view, and no read is made", async ({ page }) => {
    const flagsRequests: string[] = [];
    page.on("request", (request) => {
      if (request.url().includes("/hidden-issue-flags")) flagsRequests.push(request.url());
    });
    await mockProfile(page);

    await page.goto(`/property/workspace?ruleeval=on&bbl=${BBL}`);
    await expect(page.getByTestId("connected-dashboard")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByRole("button", { name: "Hidden issues", exact: true })).toHaveCount(0);

    await page.goto(`/property/workspace?ruleeval=on&bbl=${BBL}&tool=hiddenissues`);
    await expect(page.getByTestId("connected-dashboard")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText(/Hidden issues is not available in this version/)).toBeVisible();
    // Neither the live panel nor its empty "not connected yet" card is mounted when the flag is off.
    await expect(page.getByTestId("hidden-issues")).toHaveCount(0);
    await expect(page.getByTestId("hidden-issues-unavailable")).toHaveCount(0);

    // The disabled feature never issues the read.
    expect(flagsRequests).toHaveLength(0);
  });
});
