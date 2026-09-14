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
  await page.goto(`/property?ruleeval=on&bbl=${bbl}&view=${view}`);
  await expect(page.getByTestId("profile-view")).toBeVisible({ timeout: 15_000 });
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
}

test("one-box keyboard selection resolves the authoritative BBL and preserves searched address", async ({ page }, info) => {
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.route("https://geosearch.planninglabs.nyc/v2/autocomplete?**", async route => route.fulfill({ contentType: "application/json", body: JSON.stringify({ type: "FeatureCollection", features: [{ type: "Feature", properties: { source: "nycpad", housenumber: "100", street: "HOLES ISLAND", borough: "Manhattan", label: "SYNTHETIC JOURNEY ADDRESS", postalcode: "10004", addendum: { pad: { bbl: "5000010001" } } } }] }) }));
  await page.goto("/property?ruleeval=on");
  await expect(page.getByRole("heading", { name: "Find a property" })).toBeVisible();
  await screenshot(page, info, "01-search-desktop");
  const input = page.getByRole("combobox", { name: "Street address", exact: true });
  await input.fill("100 Hol");
  await expect(page.getByRole("option")).toContainText("HOLES ISLAND");
  await input.press("ArrowDown"); await input.press("Enter");
  await expect(page.getByTestId("resolved-bbl")).toHaveText(BBL);
  await page.getByTestId("confirm-continue").click();
  await expect(page.getByTestId("profile-view")).toBeVisible({ timeout: 15_000 });
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(/100 HOLES ISLAND/);
  await expect(page.getByTestId("representative-address")).toContainText("PLUTO representative address");
  await expect(page.getByTestId("lot-outline")).toBeVisible();
  await screenshot(page, info, "02-overview-confirmed-address");
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
    await openView(page, view, ["evidence", "scenarios"].includes(view) ? "1000010100" : BBL);
    await expect(page.getByRole("navigation", { name: "Architect workspace" })).toBeVisible();
    if (view === "evidence") {
      await expect(page.getByText("Full evaluation trace", { exact: true })).toBeVisible({ timeout: 15_000 });
      await expect(page.getByRole("link", { name: "Open current official text ↗" }).first()).toHaveAttribute("href", /^https:\/\/zoningresolution\.planning\.nyc\.gov\/article-/);
    }
    if (view === "facts") {
      const source = page.getByRole("button", { name: "Source for Lot area", exact: true });
      await source.click();
      await expect(page.getByRole("complementary", { name: "Contextual evidence inspector" })).toContainText("Original value");
    }
    if (view === "zoning") await expect(page.getByText("Pending land-use actions", { exact: true })).toBeVisible();
    if (view === "documents") await expect(page.getByTestId("inbox-empty")).toBeVisible();
    if (view === "report") await expect(page.getByRole("button", { name: "Print property brief" })).toBeVisible();
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
  await screenshot(page, info, "14-overview-mobile");
  await page.getByRole("button", { name: "Navigation", exact: true }).click();
  await page.getByRole("navigation").getByRole("link", { name: "Property facts", exact: true }).click();
  const source = page.getByRole("button", { name: "Source for Lot area", exact: true });
  await source.click();
  const inspector = page.getByRole("complementary", { name: "Contextual evidence inspector" });
  await expect(inspector).toBeInViewport();
  await expect(inspector).toBeFocused();
  await expect(inspector).toContainText("Original value");
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
  await screenshot(page, info, "08-survey-review-desktop");
});

test("manual and BBL recovery remain reachable when suggestions fail", async ({ page }) => {
  await page.route("https://geosearch.planninglabs.nyc/v2/autocomplete?**", route => route.fulfill({ status: 429, contentType: "application/json", body: "{}" }));
  await page.goto("/property?ruleeval=on");
  await page.getByRole("combobox", { name: "Street address", exact: true }).fill("120 Broadway");
  await expect(page.getByText("Address suggestions are busy. Use manual entry or BBL below.")).toBeVisible();
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
