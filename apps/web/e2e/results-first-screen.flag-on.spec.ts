import { expect, test, type Locator, type Page } from "@playwright/test";
import profileFixture from "../../../packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json";

/**
 * M5-T181 — the Results window's FIRST SCREEN leads with the results; the assumed conditions follow
 * (D-094 R151; presentation contract principle 1 and the page-1 order). Run by the `chromium-flag-on`
 * project against the :3001 server where INTERNAL_RESULTS_UI_ENABLED=1 and the real results route
 * (:8000). The orchestrator runs this file (ruling V6: builders never start a server); no byte of the
 * result is hand-written.
 *
 * It opens the Results tool (a WIDE window in DashboardEntry's wide list), presses "Show results", and
 * measures the first screen: the identity, the floor-area allowance's headline and the legal-ceiling /
 * apartment-estimate figures lead; the assumed-conditions list (three-answers-scope) sits BELOW the
 * results band. The packet scenarios here are S1 (results lead the first screen at the desktop
 * widths), S2 (results above the assumptions at 1440), S3 (the figures reach the first screen at the
 * phone widths), and S7 (no sideways scroll and no clipped text at every width).
 *
 * The existing results-layout.flag-on.spec.ts owns the 44:56 split (S1 there) and the S12 identity +
 * allowance first-screen case; its routeApi/openResults/clipped-text helpers are not exported, so this
 * file defines its own (acceptable e2e duplication of the M5-T149 / M5-T171 pattern).
 */

const BBL = "4073340070";
const WINDOW_NAME = "Results";

async function routeApi(page: Page): Promise<void> {
  await page.route("**/api/v1/properties/**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    // Let the results (POST) read reach the REAL harness; serve the base profile; 404 the rest.
    if (path.endsWith(`/${BBL}/results`)) return route.continue();
    const last = path.split("/").at(-1);
    if (last !== BBL) return route.fulfill({ status: 404, json: { detail: "not found" } });
    const profile = structuredClone(profileFixture);
    profile.identity.bbl = BBL;
    await route.fulfill({ json: profile });
  });
}

/** Open the workspace, open the Results tool, press "Show results", and return the window dialog. */
async function openResults(page: Page): Promise<Locator> {
  await routeApi(page);
  await page.goto(`/property/workspace?ruleeval=on&bbl=${BBL}`);
  await expect(page.getByTestId("connected-dashboard")).toBeVisible({ timeout: 15_000 });
  const opener = page.getByRole("button", { name: WINDOW_NAME, exact: true });
  await opener.click();
  const dialog = page.getByRole("dialog", { name: WINDOW_NAME });
  await expect(dialog).toBeVisible();
  const response = page.waitForResponse(
    (r) => r.url().includes(`/${BBL}/results`) && r.request().method() === "POST",
    { timeout: 20_000 },
  );
  await dialog.getByTestId("results-show").click();
  await response;
  await expect(dialog.getByTestId("three-answers-panel")).toBeVisible({ timeout: 15_000 });
  return dialog;
}

/** The page must never scroll sideways: the document is no wider than the viewport. */
async function pageHorizontalOverflow(page: Page): Promise<number> {
  return page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
}

/**
 * Text inside the dialog whose real, visible box is cut off by overflow:hidden/clip OUTSIDE a labelled
 * scroll region (role=region with an aria-label). Returns a short sample of each offender's text; an
 * empty list is the pass. It skips elements hidden-by-design for screen readers (a box of at most
 * 1x1 px, or clipped to nothing), whose audible-only text naturally exceeds its 1 px box — not a
 * visible-clipping defect. This is the M5-T149 / M5-T171 clipped-text helper, defined locally because
 * the existing spec does not export it.
 */
async function clippedTextInsideDialog(dialog: Locator): Promise<string[]> {
  return dialog.evaluate((root) => {
    const offenders: string[] = [];
    const regions = Array.from(root.querySelectorAll('[role="region"][aria-label]'));
    for (const element of Array.from(root.querySelectorAll<HTMLElement>("*"))) {
      const style = getComputedStyle(element);
      if (style.overflowX !== "hidden" && style.overflowX !== "clip") continue;
      if (element.scrollWidth <= element.clientWidth + 1) continue;
      if (regions.some((region) => region.contains(element))) continue;
      const rect = element.getBoundingClientRect();
      const clippedToNothing =
        style.clip === "rect(0px, 0px, 0px, 0px)" ||
        (style.clipPath !== "none" && style.clipPath !== "");
      if ((rect.width <= 1 && rect.height <= 1) || clippedToNothing) continue;
      offenders.push((element.textContent ?? "").trim().slice(0, 40));
    }
    return offenders;
  });
}

/**
 * Whether the legal-ceiling cell and the apartment-estimate cell overlap. Side by side on a wide
 * window or stacked on a narrow one, their boxes must never intersect (UX-07). Returns false when
 * either cell is absent.
 */
async function parityCellsOverlap(dialog: Locator): Promise<boolean> {
  const block = dialog.getByTestId("apartment-figures");
  const ceiling = await block.getByTestId("apartment-figures-ceiling").boundingBox();
  const estimate = await block.getByTestId("apartment-figures-estimate").boundingBox();
  if (!ceiling || !estimate) return false;
  const apart =
    ceiling.x + ceiling.width <= estimate.x + 0.5 ||
    estimate.x + estimate.width <= ceiling.x + 0.5 ||
    ceiling.y + ceiling.height <= estimate.y + 0.5 ||
    estimate.y + estimate.height <= ceiling.y + 0.5;
  return !apart;
}

/** True when apartment-figures (the results band) precedes three-answers-scope (the assumed
 * conditions) in the DOM — the results come before the assumptions in reading order. */
async function resultsPrecedeAssumptions(dialog: Locator): Promise<boolean> {
  return dialog.evaluate((root) => {
    const figures = root.querySelector('[data-testid="apartment-figures"]');
    const scope = root.querySelector('[data-testid="three-answers-scope"]');
    if (!figures || !scope) return false;
    return Boolean(
      figures.compareDocumentPosition(scope) & Node.DOCUMENT_POSITION_FOLLOWING,
    );
  });
}

// S1: at every desktop width the results lead the first screen.
const S1_WIDTHS = [768, 1024, 1440, 1920];
// S7: no sideways scroll and no clipped text at every width (UX-07).
const S7_WIDTHS = [320, 390, 768, 1024, 1440, 1920];

test.describe("M5-T181 results first screen — flag-on, the real results route", () => {
  for (const width of S1_WIDTHS) {
    test(`S1: at ${width} x 900 the identity, the allowance headline and the ceiling/estimate lead the first screen`, async ({
      page,
    }) => {
      await page.setViewportSize({ width, height: 900 });
      const dialog = await openResults(page);
      // The identity and the floor-area allowance's headline value are in the first screen.
      await expect(dialog.getByTestId("three-answers-identity")).toBeInViewport();
      await expect(
        dialog.getByTestId("answer-floor_area_allowance").getByTestId("answer-headline-number").first(),
      ).toBeInViewport();
      // The legal ceiling and the apartment estimate (the page-1 parity block) are in the first screen.
      await expect(dialog.getByTestId("apartment-figures-ceiling-value")).toBeInViewport();
      await expect(dialog.getByTestId("apartment-figures-estimate-value")).toBeInViewport();
      // No sideways page scroll, no clipped text in the dialog, and the two figure cells do not overlap.
      expect(await pageHorizontalOverflow(page)).toBeLessThanOrEqual(1);
      expect(await clippedTextInsideDialog(dialog)).toEqual([]);
      expect(await parityCellsOverlap(dialog)).toBe(false);
    });
  }

  test("S2: at 1440 x 900 the results sit above the assumed conditions, both in the DOM and vertically", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    const dialog = await openResults(page);
    // In the DOM, the results band precedes the assumed-conditions list.
    expect(await resultsPrecedeAssumptions(dialog)).toBe(true);
    // Vertically, the apartment-figures block's bottom is at or above the scope block's top: the
    // results lead and the assumptions follow, so the assumed-conditions list no longer occupies the
    // first screen's right half from the top (R151).
    const figures = await dialog.getByTestId("apartment-figures").boundingBox();
    const scope = await dialog.getByTestId("three-answers-scope").boundingBox();
    expect(figures).not.toBeNull();
    expect(scope).not.toBeNull();
    expect(figures!.y + figures!.height).toBeLessThanOrEqual(scope!.y + 0.5);
  });

  for (const width of [390, 320]) {
    test(`S3: at ${width} x 844 the allowance headline and the ceiling figure reach the first screen`, async ({
      page,
    }) => {
      const height = 844;
      await page.setViewportSize({ width, height });
      const dialog = await openResults(page);
      // The allowance headline value is in the first screen (keeps the S12 intent on a phone).
      await expect(
        dialog.getByTestId("answer-floor_area_allowance").getByTestId("answer-headline-number").first(),
      ).toBeInViewport();
      // The results still precede the assumed conditions in the DOM.
      expect(await resultsPrecedeAssumptions(dialog)).toBe(true);
      // The legal-ceiling figure is at most one short scroll down (its top under 1.25x the viewport).
      const ceiling = await dialog.getByTestId("apartment-figures-ceiling-value").boundingBox();
      expect(ceiling).not.toBeNull();
      expect(ceiling!.y).toBeLessThan(height * 1.25);
      // No sideways scroll, and no clipped text — the long address wraps and no value ellipsizes.
      expect(await pageHorizontalOverflow(page)).toBeLessThanOrEqual(1);
      expect(await clippedTextInsideDialog(dialog)).toEqual([]);
    });
  }

  for (const width of S7_WIDTHS) {
    test(`S7: at ${width} px the page does not scroll sideways and no text is clipped in the dialog`, async ({
      page,
    }) => {
      await page.setViewportSize({ width, height: 900 });
      const dialog = await openResults(page);
      expect(await pageHorizontalOverflow(page)).toBeLessThanOrEqual(1);
      expect(await clippedTextInsideDialog(dialog)).toEqual([]);
    });
  }
});
