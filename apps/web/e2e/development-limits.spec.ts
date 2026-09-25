import { expect, test, type Page } from "@playwright/test";
import type { PropertyProfile } from "../src/lib/contract";

/** Real application paths over the existing recorded-official-fixture API.
 * Its R5 spatial substrate is documented synthetic journey scaffolding;
 * these tests assert presentation and provenance, not real-parcel eligibility. */
async function open(page: Page, view: string, bbl = "1000010010") {
  const profileResponse = page.waitForResponse(response => new URL(response.url()).pathname === `/api/v1/properties/${bbl}`);
  await page.goto(`/property?ruleeval=on&bbl=${bbl}&view=${view}`);
  const response = await profileResponse;
  expect(response.ok()).toBe(true);
  const profile = await response.json() as PropertyProfile;
  await expect(page.getByRole("region", { name: "Development limits" })).toBeVisible();
  await expect(page.getByTestId("rule-eval-announcer")).not.toBeEmpty({ timeout: 15_000 });
  await expect(page.getByText("Loading draft scenario…", { exact: true })).toHaveCount(0, { timeout: 15_000 });
  return profile;
}

for (const view of ["overview", "zoning", "report"]) {
  test(`${view}: visible city reference, explicit uncalculated bulk and complete evidence`, async ({ page }, info) => {
    const profile = await open(page, view);
    const record = profile.provenance.find(item => item.original_field_name === "residfar" && item.source_id === "nyc-dcp-pluto-soda")!;
    const summary = page.getByRole("region", { name: "Development limits" });
    const expected = (record.normalized_value as number).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 20 });
    await expect(summary.getByTestId("development-reference-far")).toHaveText(expected);
    await expect(summary.getByTestId("development-evaluated-far")).toHaveText("Not calculated");
    await expect(summary.getByTestId("architect-cap").locator(".architect-metric")).toHaveText("Not calculated");
    await expect(summary.locator("dt", { hasText: /^Height$/ }).locator("..")).toContainText("Not calculated");
    await expect(summary.locator("dt", { hasText: /^Setbacks and yards$/ }).locator("..")).toContainText("Not calculated");
    await expect(summary.locator("dt", { hasText: /^Lot coverage and open space$/ }).locator("..")).toContainText("Not calculated");
    await expect(summary.getByRole("link", { name: "Rules and calculation →" })).toHaveAttribute("href", `/property?ruleeval=on&bbl=${profile.identity.bbl}&view=evidence`);
    await page.screenshot({ path: info.outputPath(`development-${view}.png`), fullPage: true });
  });
}

test("source drill-down preserves the exact field, original value and record link", async ({ page }) => {
  const profile = await open(page, "overview");
  const source = page.getByRole("button", { name: "Source for residential FAR" });
  await source.focus();
  await page.keyboard.press("Enter");
  const inspector = page.getByRole("complementary", { name: "Contextual evidence inspector" });
  await expect(inspector).toBeFocused();
  await expect(inspector).toContainText("residfar");
  await expect(inspector).toContainText("Original value");
  await expect(inspector.getByRole("link", { name: "Current PLUTO record (JSON)" })).toHaveAttribute("href", `https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=${profile.identity.bbl}`);
  await page.keyboard.press("Escape");
  await expect(source).toBeFocused();
});

test("existing information is retained and keyboard-expandable below development limits", async ({ page }, info) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const profile = await open(page, "overview");
  const existing = page.locator(".architect-existing-building");
  await expect(existing).not.toHaveAttribute("open");
  await existing.locator(":scope > summary").focus();
  await page.keyboard.press("Enter");
  await expect(existing).toHaveAttribute("open");
  await expect(existing.getByRole("rowheader")).toHaveCount(Object.keys(profile.existing_building_facts).length);
  await expect(existing.getByRole("rowheader", { name: "Built FAR", exact: true })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.screenshot({ path: info.outputPath("development-mobile-existing-open.png"), fullPage: true });
});

test("canonical evaluated FAR stays distinct from the PLUTO reference and the square-foot cap", async ({ page }) => {
  await open(page, "overview", "1000010100");
  await expect(page.getByTestId("development-evaluated-far")).toHaveText("1.50");
  await expect(page.getByTestId("architect-cap").locator(".architect-metric")).toHaveText("15,000 sq ft");
  await expect(page.getByRole("region", { name: "Development limits" })).toContainText("PLUTO reference");
  await expect(page.locator(".architect-bulk-rows")).toContainText("Not calculated");
});

// M5-T119 (D-086 P3a, ledger A06): the readable per-cap coverage status renders
// BESIDE the cap value, keeping the "FAR only" scope note.
test("the readable per-cap coverage status renders beside the cap value on the overview", async ({ page }) => {
  await open(page, "overview", "1000010100");
  const cap = page.getByTestId("architect-cap");
  await expect(cap.locator(".architect-metric")).toHaveText("15,000 sq ft");
  await expect(cap).toContainText("FAR only · Buildable envelope not assessed");
  // The status chip sits on the same cap line as the value (A06 "beside the value").
  const line = cap.locator(".architect-cap-line");
  await expect(line.getByTestId("architect-cap-status")).toHaveText("Conditional");
  await expect(line).toContainText("15,000 sq ft");
});

for (const view of ["overview", "zoning", "scenarios", "evidence", "report"]) {
  test(`${view}: malformed accepted trace remains inspectable without promoting numbers`, async ({ page }) => {
    const bbl = "1000010100";
    let returnedRecord: unknown;
    await page.route(`**/api/v1/properties/${bbl}/rule-evaluation`, async route => {
      const response = await route.fetch();
      const body = await response.json();
      delete body.evaluations[0].outputs;
      returnedRecord = body;
      await route.fulfill({ response, json: body });
    });
    await page.goto(`/property?ruleeval=on&bbl=${bbl}&view=${view}`);
    await expect(page.getByRole("heading", { name: "Rule details incomplete" })).toBeVisible();
    await expect(page.getByTestId("rule-eval-announcer")).toContainText("Numerical summaries are unavailable");
    const raw = page.getByText("Captured unusable rule-evaluation record", { exact: true }).locator("..");
    await raw.locator(":scope > summary").click();
    await expect(raw.locator("pre")).toBeVisible();
    expect(JSON.parse((await raw.locator("pre").textContent())!)).toEqual(returnedRecord);
    if (view !== "evidence") await expect(page.getByTestId("architect-cap").locator(".architect-metric")).toHaveText("Not calculated");
    if (view === "report") {
      expect(await raw.evaluate(element => !!element.closest(".architect-report"))).toBe(true);
      await raw.locator(":scope > summary").click();
      const disclosures = page.locator(".architect-report details");
      const before = await disclosures.evaluateAll(elements => elements.map(element => (element as HTMLDetailsElement).open));
      await page.getByRole("checkbox", { name: "Include full audit appendix" }).check();
      await page.evaluate(() => { window.print = () => window.dispatchEvent(new Event("beforeprint")); });
      await page.getByRole("button", { name: "Print property brief" }).click();
      await expect(raw).toHaveAttribute("open");
      expect(JSON.parse((await raw.locator("pre").textContent())!)).toEqual(returnedRecord);
      await page.evaluate(() => window.dispatchEvent(new Event("afterprint")));
      expect(await disclosures.evaluateAll(elements => elements.map(element => (element as HTMLDetailsElement).open))).toEqual(before);
    }
  });
}

test("a missing scenario fingerprint cannot establish a numerical result association", async ({ page }) => {
  const bbl = "1000010100";
  await page.route(`**/api/v1/properties/${bbl}/scenario`, async route => {
    const response = await route.fetch();
    const body = await response.json();
    body.evaluated_input.input_fingerprint = null;
    await route.fulfill({ response, json: body });
  });
  await open(page, "overview", bbl);
  await expect(page.getByTestId("architect-cap").locator(".architect-metric")).toHaveText("Not calculated");
  await expect(page.getByTestId("development-evaluated-far")).toHaveText("Not calculated");
  await expect(page.getByText("Analysis records differ · inspect evidence", { exact: true })).toBeVisible();
});

test("mobile skip link stays above the viewport on scroll and is revealed by keyboard focus", async ({ page }, info) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await open(page, "overview");
  const skip = page.getByRole("link", { name: "Skip to workspace", exact: true });
  await expect(skip).not.toBeFocused();
  await expect(skip).toHaveCSS("top", "0px");
  await expect(skip).toHaveCSS("left", "0px");
  await expect(skip).toHaveCSS("opacity", "0");
  await expect(skip).toHaveCSS("clip-path", "inset(50%)");
  await expect(skip).toHaveCSS("pointer-events", "none");
  expect(await skip.evaluate(element => element.getBoundingClientRect().bottom)).toBeLessThanOrEqual(0);
  await page.locator(".architect-existing-building > summary").scrollIntoViewIfNeeded();
  await expect(skip).toHaveCSS("opacity", "0");
  await expect(skip).toHaveCSS("clip-path", "inset(50%)");
  expect(await skip.evaluate(element => element.getBoundingClientRect().bottom)).toBeLessThanOrEqual(0);
  await page.screenshot({ path: info.outputPath("mobile-scrolled-skip-hidden.png"), fullPage: true });
  // Traverse backwards from the immediately following header link: the skip
  // target must be reachable by keyboard and reveal itself at the viewport top.
  await page.getByRole("link", { name: "NYC Buildability — search", exact: true }).focus();
  await page.keyboard.press("Shift+Tab");
  await expect(skip).toBeFocused();
  await expect(skip).toHaveCSS("opacity", "1");
  await expect(skip).toHaveCSS("clip-path", "none");
  await expect(skip).toHaveCSS("pointer-events", "auto");
  await expect(skip).toBeInViewport();
  const bounds = await skip.boundingBox();
  expect(bounds!.x).toBe(0);
  expect(bounds!.y).toBe(0);
  await page.screenshot({ path: info.outputPath("mobile-skip-keyboard-focus.png") });
  await page.keyboard.press("Tab");
  await expect(skip).not.toBeFocused();
  await expect(skip).toHaveCSS("opacity", "0");
  await expect(skip).toHaveCSS("clip-path", "inset(50%)");
  expect(await skip.evaluate(element => element.getBoundingClientRect().bottom)).toBeLessThanOrEqual(0);
});
