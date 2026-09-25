import { expect, test, type Page, type TestInfo } from "@playwright/test";
import { DIGEST_PRO, installSurveyReviewMock } from "./survey-review-helpers";

/** M5-T029 S1–S4. Profile, scenario and rule values come from the real recorded-
 * official-fixture API. The one address suggestion is explicitly synthetic
 * journey scaffolding, matching the existing HOLES ISLAND resolver seam. */
const BBL = "1000010010";
async function screenshot(page: Page, info: TestInfo, name: string) {
  const path = info.outputPath(`${name}.png`);
  await page.screenshot({ path, fullPage: true });
  await info.attach(name, { path, contentType: "image/png" });
}
async function openView(page: Page, view: string, bbl = BBL) {
  const scenarioResponse = page.waitForResponse(response => new URL(response.url()).pathname === `/api/v1/properties/${bbl}/scenario`);
  const evaluationResponse = page.waitForResponse(response => new URL(response.url()).pathname === `/api/v1/properties/${bbl}/rule-evaluation`);
  await page.goto(`/property?ruleeval=on&bbl=${bbl}&view=${view}`);
  await expect(page.getByTestId("profile-view")).toBeVisible({ timeout: 15_000 });
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  const [scenario, evaluation] = await Promise.all([scenarioResponse, evaluationResponse]);
  expect(scenario.ok()).toBe(true);
  expect(evaluation.ok()).toBe(true);
  await expect(page.getByTestId("rule-eval-announcer")).not.toBeEmpty({ timeout: 15_000 });
  await expect(page.getByText("Loading draft scenario…", { exact: true })).toHaveCount(0, { timeout: 15_000 });
  if (view === "overview") {
    await expect(page.getByTestId("architect-cap").locator(".architect-metric")).not.toHaveText("—");
    await settledMap(page);
  }
  if (view === "scenarios") await expect(page.getByTestId("scenario-result")).toBeVisible();
  return { scenario: await scenario.json(), evaluation: await evaluation.json() };
}

async function settledMap(page: Page) {
  await expect(page.getByTestId("lot-outline-loading")).toHaveCount(0, { timeout: 15_000 });
  // This fixture has a real single-lot polygon and the CI browser has WebGL.
  // The state requires a loaded GeoJSON source plus rendered fill AND line
  // features; a raster-only canvas or honest fallback cannot satisfy it.
  await expect(page.getByTestId("lot-outline")).toHaveAttribute("data-parcel-state", "rendered", { timeout: 15_000 });
  // External context sources may fail honestly; wait for their bounded outcome.
  await expect.poll(async () => (await page.locator(".architect-map-status").allTextContents()).every(text => !/loading|Preparing/.test(text)), { timeout: 15_000 }).toBe(true);
  const canvasPng = await page.getByTestId("lot-outline-map").locator("canvas").screenshot();
  const selectedParcelPixels = await page.evaluate(async encoded => {
    const snapshot = new Image();
    snapshot.src = `data:image/png;base64,${encoded}`;
    await snapshot.decode();
    const canvas = document.createElement("canvas");
    canvas.width = snapshot.width; canvas.height = snapshot.height;
    const context = canvas.getContext("2d")!;
    context.drawImage(snapshot, 0, 0);
    const { data } = context.getImageData(0, 0, canvas.width, canvas.height);
    let pixels = 0;
    for (let offset = 0; offset < data.length; offset += 4) {
      // Selected parcel line #a4680c, allowing small rasterization variation.
      if (Math.abs(data[offset] - 164) <= 3 && Math.abs(data[offset + 1] - 104) <= 3 && Math.abs(data[offset + 2] - 12) <= 3 && data[offset + 3] === 255) pixels++;
    }
    return pixels;
  }, canvasPng.toString("base64"));
  expect(selectedParcelPixels, "actual map canvas must paint the selected parcel line, not only the NYC raster").toBeGreaterThan(100);
}

test("one-box keyboard selection resolves the authoritative BBL and preserves searched address", async ({ page }, info) => {
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.route("https://geosearch.planninglabs.nyc/v2/autocomplete?**", async route => route.fulfill({ contentType: "application/json", body: JSON.stringify({ type: "FeatureCollection", features: [{ type: "Feature", properties: { source: "nycpad", housenumber: "100", street: "HOLES ISLAND", borough: "Manhattan", label: "SYNTHETIC JOURNEY ADDRESS", postalcode: "10004", addendum: { pad: { bbl: "5000010001" } } } }] }) }));
  await page.goto("/property?ruleeval=on");
  await expect(page.getByRole("heading", { name: "Find a property" })).toBeVisible();
  await screenshot(page, info, "01-search-desktop");
  const input = page.getByRole("combobox", { name: "Street address", exact: true });
  await input.fill("100 Hol");
  await expect(page.getByRole("listbox", { name: "Official NYC address suggestions" }).getByRole("option", { name: /100 HOLES ISLAND/ })).toBeVisible();
  await input.press("ArrowDown"); await input.press("Enter");
  await expect(page.getByTestId("resolved-bbl")).toHaveText(BBL);
  await page.getByTestId("confirm-continue").click();
  await expect(page.getByTestId("profile-view")).toBeVisible({ timeout: 15_000 });
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(/100 HOLES ISLAND/);
  await expect(page.getByTestId("representative-address")).toContainText("PLUTO representative address");
  await expect(page.getByTestId("lot-outline")).toBeVisible();
  await expect(page.getByText("Loading draft scenario…", { exact: true })).toHaveCount(0, { timeout: 15_000 });
  await expect(page.getByTestId("architect-cap").locator(".architect-metric")).not.toHaveText("—");
  await settledMap(page);
  await screenshot(page, info, "02-overview-confirmed-address");
});

test("an unavailable parcel worker produces a bounded honest map fallback", async ({ page }) => {
  let workerRequests = 0;
  await page.route("**/maplibre/6.7.0/maplibre-gl-worker.mjs", route => { workerRequests++; return route.abort("failed"); });
  await page.goto(`/property?ruleeval=on&bbl=${BBL}&view=overview`);
  await expect(page.getByTestId("profile-view")).toBeVisible({ timeout: 15_000 });
  await expect(page.getByTestId("lot-outline-render-error")).toBeVisible({ timeout: 15_000 });
  expect(workerRequests).toBeGreaterThan(0);
  await expect(page.getByTestId("lot-outline")).toHaveAttribute("data-parcel-state", "unavailable");
  await expect(page.getByTestId("lot-outline-map")).toHaveCount(0);
  await expect(page.getByTestId("lot-outline-summary")).toContainText("interactive map could not be rendered");
  await expect(page.getByTestId("lot-outline-accuracy")).toContainText("±20 ft");
});

const VIEWS = [
  ["overview", "02-overview-desktop"], ["facts", "03-property-facts-desktop"],
  ["zoning", "04-zoning-desktop"], ["scenarios", "05-scenarios-desktop"],
  ["evidence", "06-evidence-desktop"], ["documents", "07-documents-desktop"],
  ["issues", "09-open-issues-desktop"], ["report", "10-property-brief-desktop"],
  ["envelope", "11-envelope-planned"], ["units", "12-units-planned"], ["financials", "13-financials-planned"],
] as const;
for (const [view, name] of VIEWS) {
  test(`architect ${view}: canonical records, reachable navigation and screenshot`, async ({ page }, info) => {
    await page.setViewportSize({ width: 1440, height: 960 });
    await installSurveyReviewMock(page);
    const records = await openView(page, view, ["evidence", "scenarios"].includes(view) ? "1000010100" : BBL);
    await expect(page.getByRole("navigation", { name: "Architect workspace" })).toBeVisible();
    if (view === "evidence") {
      await expect(page.locator(".architect-determination")).toHaveCount(records.evaluation.evaluations.length);
      const applicable = page.locator(".architect-determination[open]").first();
      await expect(applicable.locator(":scope > summary")).toContainText("Applicable determination");
      await expect(applicable.getByText("Full evaluation trace", { exact: true })).toBeVisible();
      await expect(applicable.getByRole("link", { name: "Open current official text ↗" }).first()).toHaveAttribute("href", /^https:\/\/zoningresolution\.planning\.nyc\.gov\/article-/);
    }
    if (view === "facts") {
      await page.getByLabel("Filter facts", { exact: true }).fill("lot area");
      const source = page.getByRole("button", { name: "Source for Lot area", exact: true });
      await source.click();
      const inspector = page.getByRole("complementary", { name: "Contextual evidence inspector" });
      await expect(inspector).toContainText("Original value");
      await expect(inspector).toContainText("lotarea");
      await expect(inspector.getByRole("link", { name: "Current PLUTO record (JSON)" })).toHaveAttribute("href", `https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=${BBL}`);
      await expect(inspector.getByRole("link", { name: "About this dataset" })).toHaveAttribute("href", "https://data.cityofnewyork.us/d/64uk-42ks");
    }
    if (view === "zoning") await expect(page.getByText("Pending land-use actions", { exact: true })).toBeVisible();
    if (view === "documents") await expect(page.getByTestId("inbox-empty")).toBeVisible();
    if (view === "report") {
      await expect(page.getByRole("button", { name: "Print property brief" })).toBeVisible();
      const sources = page.locator("#brief-sources");
      await sources.locator(":scope > summary").click();
      const row = sources.locator("tbody tr").first();
      await expect(row.getByRole("link", { name: "Current PLUTO record (JSON)" })).toHaveAttribute("href", `https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=${BBL}`);
      await expect(row.getByRole("link", { name: "About this dataset" })).toHaveAttribute("href", "https://data.cityofnewyork.us/d/64uk-42ks");
      await expect(row).toContainText("Original:");
      await expect(sources.getByText("address", { exact: true })).toHaveCSS("text-transform", "none");
      const path = info.outputPath("10a-report-captured-source-links.png");
      await row.screenshot({ path });
      await info.attach("report captured source links", { path, contentType: "image/png" });
      await sources.locator(":scope > summary").click();
    }
    if (["envelope", "units", "financials"].includes(view)) {
      await expect(page.getByRole("heading", { name: /is not available in this version/ })).toBeVisible();
      await expect(page.getByTestId("architect-cap")).toHaveCount(0);
    }
    await screenshot(page, info, name);
  });
}

test("mobile source inspector is immediately visible and Escape returns to the source", async ({ page }, info) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await openView(page, "overview");
  const figures = page.getByTestId("development-reference-far");
  await expect(figures).toHaveCount(1);
  await expect(figures).toBeVisible();
  for (const figure of await figures.all()) expect(await figure.evaluate(element => { const range = document.createRange(); range.selectNodeContents(element); return range.getClientRects().length; })).toBe(1);
  await screenshot(page, info, "14-overview-mobile");
  await page.getByRole("button", { name: "Navigation", exact: true }).click();
  await page.getByRole("navigation").getByRole("link", { name: "Property facts", exact: true }).click();
  const source = page.getByRole("button", { name: "Source for Lot area", exact: true });
  await source.click();
  const inspector = page.getByRole("complementary", { name: "Contextual evidence inspector" });
  await expect(inspector).toBeInViewport();
  await expect(inspector).toBeFocused();
  await expect(inspector).toContainText("Original value");
  await expect(inspector.getByRole("link", { name: "Current PLUTO record (JSON)" })).toHaveAttribute("href", `https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=${BBL}`);
  await expect(inspector.getByRole("link", { name: "About this dataset" })).toBeVisible();
  await screenshot(page, info, "15-source-inspector-mobile");
  await page.keyboard.press("Escape");
  await expect(source).toBeFocused();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test("survey review retains document overlays, source facts and decision history in the shared shell", async ({ page }, info) => {
  await page.setViewportSize({ width: 1440, height: 960 });
  await installSurveyReviewMock(page);
  await page.goto(`/survey/review/${encodeURIComponent(DIGEST_PRO)}`);
  await expect(page.getByTestId("review-topbar")).toBeVisible();
  await expect(page.getByTestId("document-state-badge")).toContainText("Needs review");
  await expect(page.getByTestId("check-conflict")).toBeVisible();
  await expect(page.getByTestId("fact-list")).toBeVisible();
  await expect(page.getByTestId("focused-actions")).toBeVisible();
  await screenshot(page, info, "08-survey-review-desktop");
});

test("the closed screen brief prints all readable facts and sources, with an optional audit appendix", async ({ page }) => {
  await openView(page, "report");
  const facts = page.locator("#brief-facts");
  const sources = page.locator("#brief-sources");
  const lotArea = facts.getByRole("rowheader", { name: "Lot area", exact: true });
  const capturedSource = sources.locator("tbody tr").first();
  await expect(facts).not.toHaveAttribute("open");
  await expect(sources).not.toHaveAttribute("open");
  await expect(lotArea).not.toBeVisible();
  await expect(capturedSource).not.toBeVisible();
  // Avoid the native dialog while exercising the actual print button and CSS.
  await page.evaluate(() => { window.print = () => window.dispatchEvent(new Event("beforeprint")); });
  await page.getByRole("button", { name: "Print property brief" }).click();
  await page.emulateMedia({ media: "print" });
  await expect(lotArea).toBeVisible();
  await expect(capturedSource).toBeVisible();
  await expect(capturedSource).toContainText("Original:");
  await expect(page.locator(".architect-audit-appendix")).not.toBeVisible();
  await expect(page.locator(".architect-raw").first()).not.toBeVisible();
  await page.emulateMedia({ media: "screen" });
  await page.evaluate(() => window.dispatchEvent(new Event("afterprint")));
  await expect(facts).not.toHaveAttribute("open");
  await page.getByRole("checkbox", { name: "Include full audit appendix" }).check();
  await page.getByRole("button", { name: "Print property brief" }).click();
  await page.emulateMedia({ media: "print" });
  await expect(page.locator(".architect-audit-appendix")).toBeVisible();
  await expect(page.locator(".architect-audit-appendix pre")).toContainText('"profile_version"');
  await page.emulateMedia({ media: "screen" });
  await page.evaluate(() => window.dispatchEvent(new Event("afterprint")));
});

// M5-T119 (D-086 P3a, AS-2, spec §5.3 / frame O-D): the overview canvas is two
// columns on desktop — the site map/context is the wider LEFT column, the limit
// matrix the RIGHT column.
test("the overview canvas is two side-by-side columns on desktop (map/context left, limit matrix right)", async ({ page }, info) => {
  await page.setViewportSize({ width: 1440, height: 960 });
  await openView(page, "overview");
  await expect(page.locator(".architect-overview-grid")).toBeVisible();
  const mapBox = await page.locator(".architect-map-card").boundingBox();
  const limitsBox = await page.getByRole("region", { name: "Development limits" }).boundingBox();
  expect(mapBox && limitsBox).toBeTruthy();
  if (mapBox && limitsBox) {
    // Side-by-side, not stacked: their vertical extents overlap.
    const overlap = Math.min(mapBox.y + mapBox.height, limitsBox.y + limitsBox.height) - Math.max(mapBox.y, limitsBox.y);
    expect(overlap, "map and matrix must sit on the same row (two columns), not stacked").toBeGreaterThan(0);
    // Map/context is the LEFT column and the wider (~55%) one.
    expect(mapBox.x + mapBox.width).toBeLessThanOrEqual(limitsBox.x + 1);
    expect(mapBox.width).toBeGreaterThan(limitsBox.width);
  }
  await screenshot(page, info, "16-overview-canvas-desktop");
});

// M5-T119 (D-086 P3a, AS-1, ledger A04): the former separate conflict / critical-
// missing alerts fold into ONE role=status exception strip on the overview.
test("active issues fold into ONE exception strip on the overview, no separate alert blocks", async ({ page }) => {
  const bbl = BBL;
  // Match ONLY the profile document (not its /scenario or /rule-evaluation children).
  await page.route(url => new URL(url).pathname === `/api/v1/properties/${bbl}`, async route => {
    const response = await route.fetch();
    const body = await response.json();
    body.conflicts = [...(body.conflicts ?? []), { field: "lotarea", resolution: "unresolved", values: [{ source_id: "nyc-dcp-pluto-soda", value: 3 }, { source_id: "another-source", value: 4 }] }];
    if (Array.isArray(body.missing_inputs) && body.missing_inputs.length) body.missing_inputs[0].criticality = "critical";
    await route.fulfill({ response, json: body });
  });
  await page.goto(`/property?ruleeval=on&bbl=${bbl}&view=overview`);
  await expect(page.getByTestId("profile-view")).toBeVisible({ timeout: 15_000 });
  const strip = page.getByTestId("overview-exception-strip");
  await expect(strip).toBeVisible();
  await expect(strip).toHaveAttribute("role", "status");
  await expect(strip.getByTestId("exception-issue-conflict")).toContainText("Unresolved data conflicts");
  await expect(strip.getByRole("link", { name: "Review conflicting source values →" })).toHaveAttribute("href", `/property?ruleeval=on&bbl=${bbl}&view=issues`);
  await expect(strip.getByTestId("exception-issue-missing")).toContainText("Critical inputs missing");
  await expect(strip.getByRole("link", { name: "Review missing inputs →" })).toHaveAttribute("href", `/property?ruleeval=on&bbl=${bbl}&view=issues`);
  // Folded: no legacy separate `.architect-alert` status blocks remain on the overview.
  await expect(page.locator(".architect-alert")).toHaveCount(0);
});

test("manual and BBL recovery remain reachable when suggestions fail", async ({ page }) => {
  await page.route("https://geosearch.planninglabs.nyc/v2/autocomplete?**", route => route.fulfill({ status: 429, contentType: "application/json", body: "{}" }));
  await page.goto("/property?ruleeval=on");
  await page.getByRole("combobox", { name: "Street address", exact: true }).fill("120 Broadway");
  // [ORCH-CORRECTED per web-e2e CI on 71d4abb3] M5-T032 replaces the single
  // generic "busy" message with distinct typed outcomes; a mocked 429 now
  // renders the rate-limited copy.
  // [ORCH-CORRECTED per web-e2e CI on d94bbcb6] M5-T038 (DB-009) routes the
  // failure copy through the shared FULL_ADDRESS_SEARCH_LABEL constant so the
  // copy names the rendered button; the rate-limited sentence changed with it.
  await expect(page.getByText("Address suggestions are rate-limited right now. Wait a moment, then use the “Search this full address” button below, or use manual entry or BBL.")).toBeVisible();
  await page.getByText("Enter address manually", { exact: true }).click();
  await expect(page.getByTestId("address-form")).toBeVisible();
  await page.getByText("Search by tax lot (BBL)", { exact: true }).click();
  await page.getByLabel("BBL", { exact: true }).fill("invalid");
  await page.getByRole("button", { name: "Open property", exact: true }).click();
  await expect(page.locator("#architect-bbl-error")).not.toBeEmpty();
  await page.getByLabel("BBL", { exact: true }).fill(BBL);
  await page.getByRole("button", { name: "Open property", exact: true }).click();
  await expect(page.getByTestId("profile-view")).toBeVisible({ timeout: 15_000 });
});
