import { expect, test, type Locator, type Page, type TestInfo } from "@playwright/test";
import profileFixture from "../../../packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json";
import outlineFixture from "../../../packages/contracts/fixtures/valid/lot_geometry/single_lot_polygon.json";
import dof32 from "../../../packages/contracts/fixtures/valid/lot_geometry/single_lot_dof_base_3022640032.json";
import dof33 from "../../../packages/contracts/fixtures/valid/lot_geometry/single_lot_dof_base_3022640033.json";

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

async function expectLabelsAboveSourceCredit(map: Locator) {
  const credit = await map.locator(".maplibregl-ctrl-attrib").boundingBox();
  expect(credit).not.toBeNull();
  const labels = await map.locator(".parcel-study-map__marker").all();
  expect(labels.length).toBeGreaterThan(0);
  for (const label of labels) {
    const box = await label.boundingBox();
    expect(box).not.toBeNull();
    expect(box!.y + box!.height).toBeLessThan(credit!.y);
  }
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

// Recorded DOF Wallabout geometry, unchanged. Profiles and entitlements are
// synthetic UI scaffolding and prove no Wallabout dimensions or allowances.
async function condoRecords(page: Page, mockOutlines = true) {
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
  if (mockOutlines) await page.route(/\/api\/v1\/properties\/\d{10}\/lot-geometry(?:\?.*)?$/, route => {
    const bbl = new URL(route.request().url()).pathname.split("/").at(-2)!;
    if (!LOTS.includes(bbl)) return route.continue();
    const outline = structuredClone(bbl === LOTS[0] ? dof32 : dof33);
    return route.fulfill({ json: outline });
  });
}

test("multi-parcel dashboard shows source outlines and preserves study choices without inventing combined limits", async ({ page }, info) => {
  await condoRecords(page);
  await page.goto(`/property/workspace?ruleeval=on&bbl=${BILLING}`);
  await expect(page.getByTestId("connected-dashboard")).toBeVisible({ timeout: 15_000 });
  // Plan §5a: the withheld number reads "Not available — <reason>"; the strip names the status.
  await expect(page.getByTestId("dashboard-cap")).toHaveText("Not available — the site needs review first");
  await expect(page.getByTestId("dashboard-status-item").first()).toHaveText("Results withheld");
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

test("recorded Wallabout tax-map polygons can be viewed individually and together", async ({ page }, info) => {
  const taxMapRequests: string[] = [];
  page.on("request", request => {
    const url = new URL(request.url());
    if (url.pathname.endsWith("/lot-geometry") && url.searchParams.get("source") === "tax-map") {
      taxMapRequests.push(url.pathname.split("/").at(-2)!);
    }
  });
  // Use the real backend route/parser over recorded DOF bytes in the harness.
  await condoRecords(page, false);
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.goto(`/property/workspace?ruleeval=on&bbl=${BILLING}`);
  const compact = page.locator(".bd-map-slot").getByTestId("parcel-study-map");
  await expect(compact).toHaveAttribute("data-map-state", "ready", { timeout: 15_000 });
  await expect(compact).toHaveAttribute("data-visible-bbls", LOTS.join(","));
  expect(taxMapRequests).toEqual(expect.arrayContaining(LOTS));
  expect(taxMapRequests).not.toContain(BILLING);
  await compact.getByRole("button", { name: "View Parcel 1, Lot 32" }).click();
  await expect(compact).toHaveAttribute("data-map-focus", LOTS[0]);
  await expect(compact).toHaveAttribute("data-visible-bbls", LOTS[0]);
  await expect(compact).toHaveAttribute("data-map-state", "ready");
  const lot32Pixels = await compact.getByTestId("parcel-study-map-canvas").locator("canvas").screenshot();
  await expectLabelsAboveSourceCredit(compact);
  await capture(page, info, "connected-wallabout-lot32", true);
  await compact.getByRole("button", { name: "View Parcel 2, Lot 33" }).click();
  await expect(compact).toHaveAttribute("data-visible-bbls", LOTS[1]);
  await expect(compact).toHaveAttribute("data-map-state", "ready");
  const lot33Pixels = await compact.getByTestId("parcel-study-map-canvas").locator("canvas").screenshot();
  await expectLabelsAboveSourceCredit(compact);
  expect(lot32Pixels.equals(lot33Pixels)).toBe(false);
  await capture(page, info, "connected-wallabout-lot33", true);
  await compact.getByRole("button", { name: "View all parcels" }).click();
  await expect(compact).toHaveAttribute("data-visible-bbls", LOTS.join(","));
  await expect(compact).toHaveAttribute("data-map-state", "ready");
  await capture(page, info, "connected-wallabout-all-parcels", true);
  await expectLabelsAboveSourceCredit(compact);
  await page.getByRole("region", { name: "Quick actions" }).getByRole("button", { name: /Parcel study/ }).click();
  const study = page.getByRole("dialog", { name: "Parcel study" });
  const map = study.getByTestId("parcel-study-map");
  await study.getByRole("radio", { name: /Separately/ }).check();
  await expect(map).toHaveAttribute("data-visible-bbls", LOTS[0]);
  await expect(map).toHaveAttribute("data-map-state", "ready", { timeout: 15_000 });
  await map.getByRole("button", { name: "View Parcel 2, Lot 33" }).click();
  await expect(map).toHaveAttribute("data-visible-bbls", LOTS[1]);
  await expect(map).toHaveAttribute("data-map-state", "ready");
  await study.getByRole("radio", { name: /Together/ }).check();
  await expect(map).toHaveAttribute("data-visible-bbls", LOTS.join(","));
  await expect(map).toHaveAttribute("data-map-state", "ready");
  await expect(study.getByText("Not established here", { exact: true })).toBeVisible();
  await capture(page, info, "connected-wallabout-study-together");
  await study.getByRole("radio", { name: /Compare/ }).check();
  await expect(map).toHaveAttribute("data-visible-bbls", LOTS.join(","));
  await expect(map).toHaveAttribute("data-map-state", "ready");
  await capture(page, info, "connected-wallabout-study-compare");
  await study.getByRole("button", { name: "Close Parcel study window" }).click();
  await page.setViewportSize({ width: 390, height: 844 });
  await compact.getByRole("button", { name: "View Parcel 2, Lot 33" }).click();
  await expect(compact).toHaveAttribute("data-map-state", "ready");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await capture(page, info, "connected-wallabout-parcel-mobile", true);
  await expectLabelsAboveSourceCredit(compact);
  await expect(page.getByTestId("dashboard-cap")).toHaveText(/^Not available — /);
});

test("dashboard route keeps the server gate and the explicit kill switch", async ({ page }) => {
  let requests = 0;
  page.on("request", request => { if (new URL(request.url()).pathname.startsWith("/api/v1/properties/")) requests++; });
  const response = await page.goto(`/property/workspace?ruleeval=off&bbl=${BBL}`);
  expect(response?.status()).toBe(404);
  await expect(page.getByTestId("connected-dashboard")).toHaveCount(0);
  expect(requests).toBe(0);
});

// Synthetic outage pattern: both DOF base outlines/profile reads are empty
// and only the separate MapPLUTO condo billing record has display context.
// This is not the current observed DOF response for Wallabout.
async function missingBaseOutlines(page: Page, mismatchedContext = false) {
  await condoRecords(page);
  for (const bbl of LOTS) await page.route(`**/api/v1/properties/${bbl}`, route => route.fulfill({
    status: 404, json: { state: "no_match", bbl, message: "Synthetic missing base profile" },
  }));
  await page.route(/\/api\/v1\/properties\/\d{10}\/lot-geometry(?:\?.*)?$/, route => {
    const bbl = new URL(route.request().url()).pathname.split("/").at(-2)!;
    if (![BILLING, ...LOTS].includes(bbl)) return route.continue();
    const fixture = structuredClone(outlineFixture);
    if (bbl === BILLING) return route.fulfill({ json: {
      ...fixture, bbl: mismatchedContext ? "3022647516" : BILLING,
      condo_classification: { classification: "condo_billing_lot", note: "Synthetic billing-record context; not a base parcel." },
    } });
    return route.fulfill({ json: {
      ...dof32, bbl, outcome: "no_outline", geometry: null, feature_count: 0,
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
  await expect(page.getByTestId("dashboard-cap")).toHaveText(/^Not available — /);
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
  await expect(page.getByTestId("dashboard-cap")).toHaveText(/^Not available — /);
});

// Plan §5a item 2, word for word.
const FLOOR_AREA_REMINDER = "Make sure this floor area is available for use. Confirm with the owner or developer that none of it was sold or merged with another lot.";

// Owner directive 2026-10-01, word for word: the tax-lot-only warning on the results and the
// combined-zoning-lot rows that read "Not confirmed".
const TAX_LOT_ONLY_WARNING = "These numbers cover only the tax lot you entered. The full zoning lot may include other lots. The whole-site limit, the room left after existing buildings, and the combined lot's rear yard and coverage are not calculated yet.";
const ZONING_LOT_ROWS = ["Whole-site capacity", "Remaining development capacity", "Combined zoning lot: coverage", "Combined zoning lot: rear yard"];
// Owner wording, settled 2026-10-01 (D-090-R038): the reason line under "Remaining development capacity: Not confirmed".
const REMAINING_REASON = "Needs verified zoning-lot boundaries and existing zoning floor area.";

// The mark on the draft-rule numbers (review B1 of PR #267), and the strip line's one name.
const DRAFT_MARK = "Draft — not reviewed";
const STRIP_NAME = `${DRAFT_MARK}, City-record measurements, Lot you entered. Details`;

// D-03 (M1-17, plan §5a): one status strip at the top of the results with exactly three items,
// the first marking the draft-rule numbers without a tap, standing notices behind it, the
// supported maximum as a large number with no caution chip, at most three notices on screen,
// readable text and no internal codes.
test("the dashboard follows plan §5a: one strip, notices behind it, readable text", async ({ page }, info) => {
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.goto("/property/workspace?ruleeval=on&bbl=1000010100");
  await expect(page.getByTestId("connected-dashboard")).toBeVisible({ timeout: 15_000 });
  await expect(page.getByTestId("dashboard-cap")).toHaveText("15,000 sq ft", { timeout: 15_000 });
  const summary = page.getByRole("region", { name: "Development limits summary" });
  for (const chip of ["Conditional", "DRAFT", "Draft rule"]) await expect(summary).not.toContainText(chip);
  await expect(page.getByRole("region", { name: "Results status" })).toHaveCount(1);
  const strip = page.getByTestId("dashboard-status-strip");
  const items = page.getByTestId("dashboard-status-item");
  // Exactly these three items (a fourth fails), with the draft mark visible before any tap,
  // on the strip line and not beside the number (plan §5a items 1 and 3).
  await expect(items).toHaveText([DRAFT_MARK, "City-record measurements", "Lot you entered"]);
  await expect(strip).toHaveAttribute("aria-expanded", "false");
  await expect(strip.getByText(DRAFT_MARK, { exact: true })).toBeVisible();
  await expect(summary.getByText(DRAFT_MARK)).toHaveCount(0);
  await expect(strip).toHaveAccessibleName(STRIP_NAME);
  // Owner directive 2026-10-01 (overrides §5a items 2 and 3 for this fact): before any tap, the
  // tax-lot-only warning is on the results, the cap carries a plain "Tax-lot-only estimate" line
  // (the number itself is unchanged) and the combined-zoning-lot rows read "Not confirmed".
  const warning = summary.getByTestId("tax-lot-only-warning");
  await expect(warning).toBeVisible();
  await expect(warning).toHaveText(TAX_LOT_ONLY_WARNING);
  await expect(summary.getByTestId("dashboard-cap-scope")).toHaveText("Tax-lot-only estimate");
  await expect(summary.getByTestId("dashboard-cap-scope")).toBeVisible();
  for (const label of ZONING_LOT_ROWS) {
    const row = summary.getByRole("row").filter({ has: page.getByRole("rowheader", { name: label, exact: true }) });
    await expect(row.getByRole("cell")).toHaveText(label === "Remaining development capacity" ? `Not confirmed ${REMAINING_REASON}` : "Not confirmed");
    await expect(row).toBeVisible();
  }
  await expect(summary.getByTestId("dashboard-zoning-lot-remaining-capacity-reason")).toHaveText(REMAINING_REASON);
  await expect(summary.getByTestId("dashboard-zoning-lot-remaining-capacity-reason")).toBeVisible();
  // At most three notices on screen: a fourth list item never appears (auto-retrying).
  await expect(page.getByRole("list", { name: "Needs attention" }).getByRole("listitem").nth(3)).toHaveCount(0);
  const reminder = page.getByText(FLOOR_AREA_REMINDER, { exact: true });
  await expect(reminder).toBeHidden();
  await strip.click();
  await expect(strip).toHaveAttribute("aria-expanded", "true");
  await expect(strip).toHaveAccessibleName(STRIP_NAME);
  await expect(reminder).toBeVisible();
  await expect(page.getByText("This is not a Buildings Department approval.", { exact: true })).toBeVisible();
  // No visible body or note text under 14 px outside the map (plan §5a item 5).
  const small = await page.locator(".buildability-dashboard").evaluate(root => Array.from(root.querySelectorAll<HTMLElement>("*"))
    .filter(element => !element.closest(".bd-map-slot") && element.getClientRects().length > 0
      && Array.from(element.childNodes).some(node => node.nodeType === Node.TEXT_NODE && !!node.textContent?.trim())
      && parseFloat(getComputedStyle(element).fontSize) < 14)
    .map(element => `${element.tagName}.${element.className}: ${element.textContent?.trim().slice(0, 40)}`));
  expect(small).toEqual([]);
  expect(await page.locator(".bd-analysis-column").innerText()).not.toMatch(/\b[a-z0-9]+(?:_[a-z0-9]+)+\b/);
  await capture(page, info, "connected-dashboard-status-strip-open", true);
  // The report preview carries the same warning and labels, once, on its development limits.
  await page.getByRole("region", { name: "Quick actions" }).getByRole("button", { name: /Report preview/ }).click();
  const report = page.getByRole("dialog", { name: "Property report" });
  const limits = report.getByRole("region", { name: "Development limits", exact: true });
  await expect(limits.getByTestId("architect-cap").locator(".architect-metric")).toHaveText("15,000 sq ft", { timeout: 15_000 });
  await expect(report.getByTestId("tax-lot-only-warning")).toHaveCount(1);
  await expect(limits.getByTestId("tax-lot-only-warning")).toBeVisible();
  await expect(limits.getByTestId("tax-lot-only-warning")).toHaveText(TAX_LOT_ONLY_WARNING);
  await expect(limits.getByTestId("architect-cap-scope")).toHaveText("Tax-lot-only estimate");
  for (const label of ZONING_LOT_ROWS) {
    await expect(limits.locator("dt", { hasText: new RegExp(`^${label}$`) }).locator("..").locator("dd").first()).toHaveText("Not confirmed");
  }
  await expect(limits.getByTestId("development-zoning-lot-remaining-capacity-reason")).toHaveText(REMAINING_REASON);
  // D-03 slice 5 (plan §5a item 5): every visible text node in the brief reads at the 14 px floor —
  // no small grey print. Excluded (each still §5a-correct): raw JSON dumps (.architect-raw, §5a
  // item-4 "details"); map attribution (.maplibregl-ctrl-attrib); and screen-reader-only text
  // (.visually-hidden / .sr-only), which is off-screen and not a readability surface.
  const brief = report.locator(".architect-report");
  const smallBrief = await brief.evaluate(root => Array.from(root.querySelectorAll<HTMLElement>("*"))
    .filter(element => !element.closest(".architect-raw, .maplibregl-ctrl-attrib, .visually-hidden, .sr-only")
      && element.getClientRects().length > 0
      && Array.from(element.childNodes).some(node => node.nodeType === Node.TEXT_NODE && !!node.textContent?.trim())
      && parseFloat(getComputedStyle(element).fontSize) < 14)
    .map(element => `${element.tagName}.${element.className}: ${element.textContent?.trim().slice(0, 40)}`));
  expect(smallBrief).toEqual([]);
  // No internal codes on the results face (plan §5a item 5): the development-limits region's visible
  // text carries no snake_case engine identifier; such codes stay behind the evidence disclosures,
  // which innerText (reading only visible text) excludes.
  expect(await limits.innerText()).not.toMatch(/\b[a-z0-9]+(?:_[a-z0-9]+)+\b/);
  // The status strip is a dashboard-panel surface, not part of the brief — the brief never repeats it.
  await expect(brief.getByTestId("dashboard-status-strip")).toHaveCount(0);
  await capture(page, info, "connected-report-tax-lot-only");
  await page.getByRole("button", { name: "Close Property report window" }).click();
});
