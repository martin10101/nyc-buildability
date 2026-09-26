import { expect, test, type Page } from "@playwright/test";
import profileFixture from "../../../packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json";
import dof32 from "../../../packages/contracts/fixtures/valid/lot_geometry/single_lot_dof_base_3022640032.json";
import dof33 from "../../../packages/contracts/fixtures/valid/lot_geometry/single_lot_dof_base_3022640033.json";

// Recorded DOF Wallabout base geometries, unchanged. The property profiles
// and entitlements below remain synthetic UI scaffolding and prove no
// Wallabout dimensions, development allowance or legal-site arrangement.
const BILLING = "3022647515";
const LOTS = ["3022640032", "3022640033"];

async function installStudy(page: Page) {
  await page.route("**/api/v1/properties/*", async route => {
    const bbl = new URL(route.request().url()).pathname.split("/").at(-1)!;
    if (![BILLING, ...LOTS].includes(bbl)) return route.continue();
    const profile = structuredClone(profileFixture);
    profile.identity.bbl = bbl;
    profile.identity.address.normalized_address = "SYNTHETIC PARCEL STUDY FIXTURE";
    profile.identity.address.borough_code = 3;
    profile.identity.address.borough = "Brooklyn";
    for (const source of profile.provenance) source.bbl = bbl;
    await route.fulfill({ json: profile });
  });
  await page.route(`**/api/v1/properties/${BILLING}/condo-records`, route => route.fulfill({ json: {
    document_kind: "condo_records", bbl: BILLING, outcome: "multi_lot_set",
    entered_bbl: BILLING, entered_lot_class: "billing", billing_bbl: BILLING, billing_bbl_status: "recorded",
    base_lots: LOTS.map(bbl => ({ bbl, recorded_zoning: null, recorded_zoning_status: "unknown" })),
    substitution: null, condo_key: "test-only", condo_number: null,
    provenance: { source_id: "test-only", dataset_ids: [], retrieved_at: null, dataset_version: null, queries: [] },
    site_definition: { status: "unconfirmed", active_confirmation: null, confirmation_count: 0, parcel_discrepancy: null },
  } }));
  await page.route(/\/api\/v1\/properties\/\d{10}\/lot-geometry(?:\?.*)?$/, async route => {
    const bbl = new URL(route.request().url()).pathname.split("/").at(-2)!;
    if (!LOTS.includes(bbl)) return route.continue();
    const outline = structuredClone(bbl === LOTS[0] ? dof32 : dof33);
    await route.fulfill({ json: outline });
  });
}

test("architect compares parcel groupings, retains choices and sees honest source/limit distinctions", async ({ page }, info) => {
  await installStudy(page);
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.goto(`/property?ruleeval=on&bbl=${BILLING}&view=overview`);
  const panel = page.getByTestId("parcel-study");
  await expect(panel).toBeVisible({ timeout: 15_000 });
  await expect(panel.getByRole("radio", { name: /Compare/ })).toBeChecked();
  await expect(panel.getByRole("region", { name: "Study comparison" }).getByText("Not calculated", { exact: true })).toHaveCount(6);
  await panel.getByRole("radio", { name: /Together/ }).focus();
  await page.keyboard.press("Space");
  await expect(panel.getByText("1 proposed site", { exact: true })).toBeVisible();
  await panel.getByLabel("Existing buildings on Lot 32", { exact: true }).selectOption("retain");
  await panel.getByRole("radio", { name: "Multiple buildings", exact: true }).check();
  await panel.getByRole("radio", { name: /Separately/ }).check();
  await expect(panel.getByText("2 proposed sites", { exact: true })).toBeVisible();
  await expect(panel.getByLabel("Existing buildings on Lot 32", { exact: true })).toHaveValue("retain");
  await expect(panel.getByText("Not established here", { exact: true })).toBeVisible();
  await expect(panel.getByRole("article", { name: `Source records for BBL ${LOTS[0]}` })).toContainText("PLUTO reference");
  const downloadPromise = page.waitForEvent("download");
  await panel.getByRole("button", { name: "Download study choices" }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe(`parcel-study-${BILLING}.json`);
  const path = await download.path();
  expect(path).not.toBeNull();
  await panel.getByRole("radio", { name: /Together/ }).check();
  await panel.getByLabel("Restore parcel study file").setInputFiles(path!);
  await expect(panel.getByRole("radio", { name: /Separately/ })).toBeChecked();
  await expect(panel.getByText("Not established here", { exact: true })).toBeVisible();
  await panel.getByRole("radio", { name: /Compare/ }).check();
  await info.attach("parcel-study-desktop", { body: await panel.screenshot(), contentType: "image/png" });
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(panel.getByRole("button", { name: "Download study choices" })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await info.attach("parcel-study-mobile", { body: await panel.screenshot(), contentType: "image/png" });
});

test("a failed parcel profile preserves its separately loaded outline and the other parcel records", async ({ page }) => {
  await installStudy(page);
  await page.route(`**/api/v1/properties/${LOTS[1]}`, route => route.fulfill({ status: 404, json: { state: "no_match", bbl: LOTS[1], message: "Synthetic missing source record" } }));
  await page.goto(`/property?ruleeval=on&bbl=${BILLING}&view=overview`);
  const panel = page.getByTestId("parcel-study");
  await expect(panel).toBeVisible({ timeout: 15_000 });
  await expect(panel.getByRole("article", { name: `Source records for BBL ${LOTS[1]}` })).toContainText("No property record found");
  await expect(panel.getByRole("article", { name: `Source records for BBL ${LOTS[1]}` })).toContainText("Display outline available");
  await expect(panel.getByRole("article", { name: `Source records for BBL ${LOTS[0]}` })).toContainText("PLUTO reference");
  await expect(panel.getByRole("radio", { name: /Together/ })).toBeEnabled();
});
