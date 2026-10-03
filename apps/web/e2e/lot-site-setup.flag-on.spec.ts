import { expect, test, type Page } from "@playwright/test";
import profileFixture from "../../../packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json";

/**
 * D-04 (plan M1-13) flag-ON human journey, run by the `chromium-flag-on` project against the
 * :3001 server where INTERNAL_LOT_SITE_SETUP_ENABLED=1. It opens 215-16 Northern Blvd
 * (BBL 4073340070), the single BBL the recorded-fixture harness serves a study SETUP for
 * (e2e/harness/fixture_api.py, through the REAL B-02/B-07 pipeline — no study byte is hand-written),
 * opens the "Lot & site setup" tool, and walks the real surface:
 *   - the lots with their measurement source labels;
 *   - the site facts with their source labels;
 *   - the owner-pinned zoning-lot statement;
 *   - a per-fact edit recorded as "Entered" beside the kept city value, with a plain message on
 *     invalid input (recovery).
 *
 * The property PROFILE for this BBL is served from the committed fixture (the harness PLUTO table
 * has no Northern profile; the study endpoint is a separate recorded seam), while the `/study`
 * request is allowed through to the real harness. Re-pick with `selected` is NOT exercised here:
 * this branch predates the server's `selected` support (PR #320); the re-pick e2e is added after
 * the integration base is merged in. It is unit-tested in the vitest pack.
 *
 * The flag-OFF default stays proven by lot-site-setup.spec.ts on :3000 (untouched).
 */

const BBL = "4073340070";
// Owner-pinned, contract-locked (study.schema.json lot_selection.statement); copied verbatim.
const PINNED_STATEMENT = "Based on the lots you selected — the app does not verify the zoning lot";

async function routeApi(page: Page): Promise<void> {
  await page.route("**/api/v1/properties/**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    // Let the study SETUP request reach the real recorded-fixture harness for the Northern BBL.
    if (path.endsWith(`/${BBL}/study`)) return route.continue();
    const last = path.split("/").at(-1);
    // Serve the base profile from the committed fixture (so the dashboard shell loads); every
    // sub-resource (condo-records, lot-geometry, scenario, rule-evaluation) 404s cleanly.
    if (last !== BBL) return route.fulfill({ status: 404, json: { detail: "not found" } });
    const profile = structuredClone(profileFixture);
    profile.identity.bbl = BBL;
    await route.fulfill({ json: profile });
  });
}

test.describe("D-04 lot & site setup — flag-on journey over the real study setup", () => {
  test("shows the lots, site facts and pinned statement, and records an Entered value beside the city value", async ({ page }) => {
    await routeApi(page);

    await page.goto(`/property/workspace?ruleeval=on&bbl=${BBL}`);
    await expect(page.getByTestId("connected-dashboard")).toBeVisible({ timeout: 15_000 });

    // Open the flag-on tool.
    await page.getByRole("button", { name: /Lot & site setup/ }).click();
    const panel = page.getByTestId("lot-site-setup");
    await expect(panel).toBeVisible({ timeout: 15_000 });

    // The single Northern lot, with its City-records size and source label.
    await expect(panel.getByText("This property has 1 lot.")).toBeVisible();
    await expect(panel.getByText("The site is this one lot.")).toBeVisible();
    await expect(panel.getByTestId(`lot-row-${BBL}`)).toContainText("10,075 sq ft");
    await expect(panel.getByTestId(`lot-row-${BBL}`)).toContainText("City records");

    // Site facts with their sources, and the owner-pinned statement always on the face.
    const lotArea = panel.locator('[data-fact-key="lot_area"]');
    await expect(lotArea).toContainText("10,075 sq ft");
    await expect(lotArea).toContainText("City records");
    await expect(panel.locator('[data-fact-key="zoning_district"]')).toContainText("R6B");
    await expect(panel.getByTestId("lot-site-statement")).toHaveText(PINNED_STATEMENT);

    // Invalid input changes nothing and says why in plain words (recovery).
    await lotArea.getByRole("button", { name: /Enter the value for Lot area/ }).click();
    await lotArea.getByRole("textbox").fill("0");
    await lotArea.getByRole("button", { name: "Save" }).click();
    await expect(lotArea).toContainText("Enter a number greater than zero.");
    await expect(lotArea).not.toContainText("Entered:");

    // A valid value is recorded as "Entered", beside the kept city value.
    await lotArea.getByRole("textbox").fill("10500");
    await lotArea.getByRole("button", { name: "Save" }).click();
    await expect(lotArea).toContainText("Entered");
    await expect(lotArea).toContainText("10,500 sq ft");
    await expect(lotArea).toContainText("10,075 sq ft"); // the city value stays visible beside it

    // No internal code is shown on the face.
    await expect(panel).not.toContainText("architect_entry");
    await expect(panel).not.toContainText("city_dataset");
  });

  test("step 4: keep the building, enter the zoning floor area as a stated assumption, then no existing building", async ({ page }) => {
    await routeApi(page);

    await page.goto(`/property/workspace?ruleeval=on&bbl=${BBL}`);
    await expect(page.getByTestId("connected-dashboard")).toBeVisible({ timeout: 15_000 });
    await page.getByRole("button", { name: /Lot & site setup/ }).click();
    const panel = page.getByTestId("lot-site-setup");
    await expect(panel).toBeVisible({ timeout: 15_000 });

    const step = panel.getByTestId("existing-building-step");
    await expect(step).toBeVisible();
    // Nothing chosen yet: the honest note shows and there is no floor-area entry.
    await expect(panel.getByTestId("existing-building-unchosen")).toBeVisible();
    await expect(panel.getByTestId("existing-floor-area")).toHaveCount(0);

    // Keep the building → the existing zoning floor area is "Unknown — enter" (none established).
    await step.getByRole("radio", { name: "Keep the existing building" }).check();
    const floorArea = panel.getByTestId("existing-floor-area");
    await expect(floorArea).toContainText("Unknown — enter");
    await expect(floorArea).toContainText("Needed for:");

    // Enter a value as a stated assumption → it is listed with the "Assumed" source label.
    await floorArea.getByRole("textbox").fill("6200");
    await floorArea.getByRole("radio", { name: "Stated assumption" }).check();
    await floorArea.getByRole("button", { name: "Save" }).click();
    await expect(panel.getByTestId("existing-floor-area-value")).toContainText("6,200 sq ft");
    await expect(panel.getByTestId("existing-floor-area-source-label")).toContainText("Assumed");

    // No internal enum tokens on the face (the plain word "assumption" in a label is fine).
    await expect(step).not.toContainText("existing_zoning_floor_area");
    await expect(step).not.toContainText("architect_entry");

    // No existing building → the floor-area entry is gone.
    await step.getByRole("radio", { name: "No existing building" }).check();
    await expect(panel.getByTestId("existing-floor-area")).toHaveCount(0);
  });
});
