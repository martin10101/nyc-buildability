import { expect, test, type Page, type TestInfo } from "@playwright/test";
import profileFixture from "../../../packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json";
import outlineFixture from "../../../packages/contracts/fixtures/valid/lot_geometry/single_lot_polygon.json";

const BBL = "1000010010";
const BILLING = "3022647515";
const LOTS = ["3022640032", "3022640033"];

async function capture(page: Page, info: TestInfo, name: string, fullPage = false) {
  // Persist a named PNG as well as the HTML-report attachment so thin-client
  // reviewers can download pictures without the complete trace archive.
  const path = info.outputPath(`${name}.png`);
  await page.screenshot({ path, fullPage });
  await info.attach(name, { path, contentType: "image/png" });
}

test("address confirmation populates the same dashboard and floating tools retain work", async ({ page }, info) => {
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.route("https://geosearch.planninglabs.nyc/v2/autocomplete?**", route => route.fulfill({ json: { type: "FeatureCollection", features: [{ type: "Feature", properties: { source: "nycpad", housenumber: "100", street: "HOLES ISLAND", borough: "Manhattan", label: "SYNTHETIC JOURNEY ADDRESS", postalcode: "10004" } }] } }));
  await page.goto("/property/workspace?ruleeval=on");
  const search = page.getByRole("combobox", { name: "Street address", exact: true });
  await search.fill("100 Hol");
  await expect(page.getByRole("option", { name: /100 HOLES ISLAND/ })).toBeVisible();
  await search.press("ArrowDown"); await search.press("Enter");
  await expect(page.getByTestId("resolved-bbl")).toHaveText(BBL);
  await expect(page.getByTestId("connected-dashboard")).toHaveCount(0);
  await page.getByTestId("confirm-continue").click();
  await expect(page.getByTestId("connected-dashboard")).toBeVisible({ timeout: 15_000 });
  await expect(page).toHaveURL(new RegExp(`/property/workspace\\?ruleeval=on&bbl=${BBL}$`));
  await expect(search).toBeVisible();
  await expect(page.getByRole("heading", { level: 1 })).toContainText("100 HOLES ISLAND");
  await expect(page.getByTestId("confirm-continue")).toHaveCount(0);
  await expect(page.locator(".bd-map-slot").getByTestId("lot-outline")).toHaveAttribute("data-parcel-state", "rendered", { timeout: 15_000 });
  await expect(page.locator(".bd-map-slot canvas")).toBeVisible();
  await page.getByRole("button", { name: /Draw a proposal/ }).click();
  const editor = page.getByRole("dialog", { name: "Proposal editor" });
  await expect(editor).toBeVisible();
  await editor.getByLabel("Proposal label", { exact: true }).fill("Persistent courtyard sketch");
  await editor.getByRole("button", { name: "Close Proposal editor window" }).click();
  await page.getByRole("button", { name: /Draw a proposal/ }).click();
  await expect(editor.getByLabel("Proposal label", { exact: true })).toHaveValue("Persistent courtyard sketch");
  await editor.getByRole("button", { name: "Close Proposal editor window" }).click();
  await page.getByRole("group", { name: "Development details" }).getByRole("button", { name: "Envelope", exact: true }).click();
  await expect(editor.locator(".dashboard-tool-details")).toHaveAttribute("open", "");
  await editor.locator(".dashboard-tool-details>summary").click();
  await expect(editor.locator(".dashboard-tool-details")).not.toHaveAttribute("open", "");
  await editor.getByRole("button", { name: "Close Proposal editor window" }).click();
  await page.getByRole("group", { name: "Development details" }).getByRole("button", { name: "Envelope", exact: true }).click();
  await expect(editor.locator(".dashboard-tool-details")).toHaveAttribute("open", "");
  await expect(editor.getByLabel("Proposal label", { exact: true })).toHaveValue("Persistent courtyard sketch");
  await editor.getByRole("button", { name: "Close Proposal editor window" }).click();
  await capture(page, info, "connected-dashboard-desktop", true);
  await page.getByRole("region", { name: "Quick actions" }).getByRole("button", { name: /Open map/ }).click();
  const map = page.getByRole("dialog", { name: "Property map" });
  await expect(map.getByTestId("lot-outline")).toHaveAttribute("data-parcel-state", "rendered", { timeout: 15_000 });
  await map.getByRole("button", { name: "Maximize Property map window" }).click();
  await expect(map).toHaveClass(/workspace-window--maximized/);
  await map.getByRole("button", { name: "Restore Property map window" }).click();
  await map.getByRole("button", { name: "Move Property map window" }).focus();
  await page.keyboard.press("ArrowRight");
  await capture(page, info, "connected-floating-map");
  await page.keyboard.press("Escape");
  await expect(map).toBeHidden();
  await page.getByRole("button", { name: /Report preview/ }).click();
  await expect(page.getByRole("dialog", { name: "Property report" }).getByRole("button", { name: "Print property brief" })).toBeVisible();
  expect(new URL(page.url()).pathname).toBe("/property/workspace");
  await page.getByRole("button", { name: "Close Property report window" }).click();
  await page.setViewportSize({ width: 1024, height: 768 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await capture(page, info, "connected-dashboard-tablet", true);
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(search).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await capture(page, info, "connected-dashboard-mobile", true);
  await page.getByRole("button", { name: /Draw a proposal/ }).click();
  await expect(editor.getByLabel("Proposal label", { exact: true })).toHaveValue("Persistent courtyard sketch");
  const frame = await editor.boundingBox();
  expect(frame).not.toBeNull();
  expect(frame!.x).toBeGreaterThanOrEqual(0);
  expect(frame!.x + frame!.width).toBeLessThanOrEqual(390);
  expect(frame!.y + frame!.height).toBeLessThanOrEqual(844);
  const labelField = await editor.getByLabel("Proposal label", { exact: true }).boundingBox();
  expect(labelField!.y + labelField!.height).toBeLessThan(frame!.y + frame!.height);
  await capture(page, info, "connected-proposal-mobile");
});

// Transport scaffolding only: actual fixture shapes, synthetic Wallabout
// identities. Neither dimensions nor geometry here are Wallabout evidence.
async function condoRecords(page: Page) {
  await page.route("**/api/v1/properties/*", async route => {
    const bbl = new URL(route.request().url()).pathname.split("/").at(-1)!;
    if (![BILLING, ...LOTS].includes(bbl)) return route.continue();
    const profile = structuredClone(profileFixture);
    profile.identity.bbl = bbl;
    profile.identity.address.normalized_address = "SYNTHETIC WALLABOUT UI FIXTURE";
    for (const source of profile.provenance) source.bbl = bbl;
    await route.fulfill({ json: profile });
  });
  await page.route(`**/api/v1/properties/${BILLING}/condo-records`, route => route.fulfill({ json: {
    document_kind: "condo_records", bbl: BILLING, outcome: "multi_lot_set", entered_bbl: BILLING,
    entered_lot_class: "billing", billing_bbl: BILLING, billing_bbl_status: "recorded",
    base_lots: LOTS.map(bbl => ({ bbl, recorded_zoning: null, recorded_zoning_status: "unknown" })),
    substitution: null, condo_key: "test-only", condo_number: null,
    provenance: { source_id: "test-only", dataset_ids: [], retrieved_at: null, dataset_version: null, queries: [] },
    site_definition: { status: "unconfirmed", active_confirmation: null, confirmation_count: 0, parcel_discrepancy: null },
  } }));
  await page.route("**/api/v1/properties/*/lot-geometry", route => {
    const bbl = new URL(route.request().url()).pathname.split("/").at(-2)!;
    if (!LOTS.includes(bbl)) return route.continue();
    const outline = structuredClone(outlineFixture); outline.bbl = bbl;
    return route.fulfill({ json: outline });
  });
}

test("multi-parcel dashboard shows source outlines and preserves study choices without inventing combined limits", async ({ page }, info) => {
  await condoRecords(page);
  await page.goto(`/property/workspace?ruleeval=on&bbl=${BILLING}`);
  await expect(page.getByTestId("connected-dashboard")).toBeVisible({ timeout: 15_000 });
  await expect(page.getByTestId("dashboard-cap")).toHaveText("Not calculated");
  await expect(page.getByText("Site definition requires review · allowances withheld")).toBeVisible();
  await expect(page.getByTestId("parcel-study-map-canvas")).toBeVisible({ timeout: 15_000 });
  await page.getByRole("region", { name: "Quick actions" }).getByRole("button", { name: /Parcel study/ }).click();
  const study = page.getByRole("dialog", { name: "Parcel study" });
  await study.getByRole("radio", { name: /Together/ }).check();
  await study.getByLabel("Existing buildings on Lot 32", { exact: true }).selectOption("retain");
  await study.getByRole("button", { name: "Close Parcel study window" }).click();
  await page.getByRole("region", { name: "Quick actions" }).getByRole("button", { name: /Parcel study/ }).click();
  await expect(study.getByRole("radio", { name: /Together/ })).toBeChecked();
  await expect(study.getByLabel("Existing buildings on Lot 32", { exact: true })).toHaveValue("retain");
  await expect(study.getByText("Not established here", { exact: true })).toBeVisible();
  await capture(page, info, "connected-parcel-study");
  await study.getByRole("button", { name: "Close Parcel study window" }).click();
  await page.getByRole("button", { name: /Draw a proposal/ }).click();
  await expect(page.getByRole("dialog", { name: "Proposal editor" }).getByRole("heading", { name: "Site definition required" })).toBeVisible();
});

test("dashboard route keeps the server gate and the explicit kill switch", async ({ page }) => {
  let requests = 0;
  page.on("request", request => { if (new URL(request.url()).pathname.startsWith("/api/v1/properties/")) requests++; });
  const response = await page.goto(`/property/workspace?ruleeval=off&bbl=${BBL}`);
  expect(response?.status()).toBe(404);
  await expect(page.getByTestId("connected-dashboard")).toHaveCount(0);
  expect(requests).toBe(0);
});

// Reproduces the live failure's RESPONSE PATTERN, not Wallabout's geography:
// DTM supplies base IDs, both base geometry/profile reads are empty, and only
// the separate condo billing record has a display outline.
async function missingBaseOutlines(page: Page, mismatchedContext = false) {
  await condoRecords(page);
  for (const bbl of LOTS) await page.route(`**/api/v1/properties/${bbl}`, route => route.fulfill({
    status: 404, json: { state: "no_match", bbl, message: "Synthetic missing base profile" },
  }));
  await page.route("**/api/v1/properties/*/lot-geometry", route => {
    const bbl = new URL(route.request().url()).pathname.split("/").at(-2)!;
    if (![BILLING, ...LOTS].includes(bbl)) return route.continue();
    const fixture = structuredClone(outlineFixture);
    if (bbl === BILLING) return route.fulfill({ json: {
      ...fixture, bbl: mismatchedContext ? "3022647516" : BILLING,
      condo_classification: { classification: "condo_billing_lot", note: "Synthetic billing-record context; not a base parcel." },
    } });
    return route.fulfill({ json: {
      ...fixture, bbl, outcome: "no_outline", geometry: null, feature_count: 0,
      review_required: false, no_outline_reason: "no_feature_for_bbl",
    } });
  });
}

test("missing base outlines retain a separately labeled condo context on dashboard and floating tools", async ({ page }, info) => {
  const requested: string[] = [];
  page.on("request", request => {
    const path = new URL(request.url()).pathname;
    if (path.endsWith("/lot-geometry")) requested.push(path.split("/").at(-2)!);
  });
  await missingBaseOutlines(page);
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.goto(`/property/workspace?ruleeval=on&bbl=${BILLING}`);
  const compact = page.locator(".bd-map-slot");
  await expect(compact.getByTestId("parcel-study-context-outline")).toHaveAttribute("data-context-state", "rendered", { timeout: 15_000 });
  await expect(compact.getByText("Condo tax-map outline · context only", { exact: true })).toBeVisible();
  expect(requested).toEqual(expect.arrayContaining([BILLING, ...LOTS]));
  await expect(page.getByTestId("dashboard-cap")).toHaveText("Not calculated");
  await expect(page.getByRole("button", { name: /2 base parcel records.*Review parcels/ })).toBeVisible();
  await expect(compact.getByText(/No parcel outlines available to draw/)).toHaveCount(0);
  await capture(page, info, "connected-condo-context-desktop", true);
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(compact.getByTestId("parcel-study-context-outline")).toHaveAttribute("data-context-state", "rendered");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  // Canvas pixels prove the context boundary was painted, not merely fetched.
  const png = await compact.getByTestId("parcel-study-map-canvas").locator("canvas").screenshot();
  const boundaryPixels = await page.evaluate(async encoded => {
    const img = new Image(); img.src = `data:image/png;base64,${encoded}`; await img.decode();
    const canvas = document.createElement("canvas"); canvas.width = img.width; canvas.height = img.height;
    const context = canvas.getContext("2d")!; context.drawImage(img, 0, 0);
    const { data } = context.getImageData(0, 0, canvas.width, canvas.height);
    let count = 0;
    for (let i = 0; i < data.length; i += 4) {
      if (Math.abs(data[i] - 36) <= 3 && Math.abs(data[i + 1] - 105) <= 3 && Math.abs(data[i + 2] - 154) <= 3 && data[i + 3] === 255) count++;
    }
    return count;
  }, png.toString("base64"));
  expect(boundaryPixels).toBeGreaterThan(50);
  await capture(page, info, "connected-condo-context-mobile", true);
  await page.getByRole("region", { name: "Quick actions" }).getByRole("button", { name: /Open map/ }).click();
  const map = page.getByRole("dialog", { name: "Property map" });
  await expect(map.getByTestId("parcel-study-context-outline")).toHaveAttribute("data-context-state", "rendered", { timeout: 15_000 });
  await map.getByRole("button", { name: "Close Property map window" }).click();
  await page.getByRole("region", { name: "Quick actions" }).getByRole("button", { name: /Parcel study/ }).click();
  const study = page.getByRole("dialog", { name: "Parcel study" });
  await expect(study.getByTestId("parcel-study-context-outline")).toHaveAttribute("data-context-state", "rendered", { timeout: 15_000 });
  await expect(study.getByRole("list", { name: "Parcel outline availability" }).getByRole("listitem")).toHaveCount(2);
  await expect(study.getByRole("article", { name: `Source records for BBL ${LOTS[0]}` })).toContainText("No property record found");
  await study.getByRole("radio", { name: /Together/ }).check();
  await expect(study.getByText("1 proposed site", { exact: true })).toBeVisible();
  await expect(study.getByText("Not established here", { exact: true })).toBeVisible();
  await expect(study.getByRole("region", { name: "Study comparison" }).getByText("Not calculated", { exact: true })).toHaveCount(3);
  await study.getByRole("button", { name: "Close Parcel study window" }).click();
  await page.getByRole("button", { name: /Draw a proposal/ }).click();
  await expect(page.getByRole("dialog", { name: "Proposal editor" }).getByRole("heading", { name: "Site definition required" })).toBeVisible();
});

test("a foreign condo outline remains withheld instead of filling the missing parcel map", async ({ page }) => {
  await missingBaseOutlines(page, true);
  await page.goto(`/property/workspace?ruleeval=on&bbl=${BILLING}`);
  const compact = page.locator(".bd-map-slot");
  await expect(compact.getByTestId("parcel-study-context-outline")).toHaveAttribute("data-context-state", "unavailable", { timeout: 15_000 });
  await expect(compact.getByTestId("parcel-study-map-canvas")).toHaveCount(0);
  await expect(page.getByTestId("dashboard-cap")).toHaveText("Not calculated");
});
