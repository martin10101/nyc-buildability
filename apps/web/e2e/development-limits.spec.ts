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
