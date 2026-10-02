import { expect, test, type Page } from "@playwright/test";
import profileFixture from "../../../../packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json";

// PLACEHOLDER smoke (lane C, request D-1 slice 2). Its ONLY job is to prove the
// flag-ON wiring this packet adds: the `chromium-flag-on` Playwright project runs
// against the SECOND `next start` on :3001, where INTERNAL_LOT_SITE_SETUP_ENABLED=1.
// It asserts the exact INVERSE of the flag-off spec's stable signal — with the flag
// ON the dashboard SHOWS the "Lot & site setup" opener (lot-site-setup.spec.ts
// asserts it is absent with the flag off) — so it depends only on the server flag,
// not on the study store (not wired here). It lives under e2e/harness/ (lane C) so
// it does not touch lane D's e2e paths. Lane D's lot-site-setup.flag-on.spec.ts is
// the real flag-on journey; once it lands, this placeholder can be removed via a
// lane C request. The profile is served the same way the flag-off spec serves it,
// so the only difference between the two is the server flag.

const BBL = "1000010010";

async function mockProfile(page: Page): Promise<void> {
  await page.route("**/api/v1/properties/**", async (route) => {
    const last = new URL(route.request().url()).pathname.split("/").at(-1);
    // Only the base profile fetch; sub-resources (study, lot-geometry) 404 cleanly.
    if (last !== BBL) return route.fulfill({ status: 404, json: { detail: "not found" } });
    const profile = structuredClone(profileFixture);
    profile.identity.bbl = BBL;
    await route.fulfill({ json: profile });
  });
}

test.describe("D-1 slice 2 flag-on project wiring (placeholder; lane D replaces)", () => {
  test("the :3001 flag-on server exposes the Lot & site setup opener", async ({ page }) => {
    await mockProfile(page);

    await page.goto(`/property/workspace?ruleeval=on&bbl=${BBL}`);
    await expect(page.getByTestId("connected-dashboard")).toBeVisible({ timeout: 15_000 });
    // Flag ON: the opener is present (the flag-off spec proves it is absent at :3000).
    await expect(page.getByRole("button", { name: /Lot & site setup/ })).toBeVisible();
  });
});
