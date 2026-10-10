import { expect, test, type Locator, type Page } from "@playwright/test";
import profileFixture from "../../../packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json";

/**
 * M5-T149 part C — the Results window LAYOUT across the six widths (acceptance UX-07, UX-08, UX-09;
 * packet scenarios S1, S2, S4). Run by the `chromium-flag-on` project against the :3001 server where
 * INTERNAL_RESULTS_UI_ENABLED=1 and the real results route (:8000). The orchestrator runs this file
 * (ruling V6: builders never start a server); no byte of the result is hand-written.
 *
 * It opens the Results tool (a WIDE window in DashboardEntry's wide list), presses "Show results",
 * and measures the rendered layout. The two-column answers/details+comparison grid itself is the
 * three-answers (part A) and building-options (part B) layout; this file verifies the integrated
 * outcome — a wide window, the answers column near 44 % at desktop, one column with no sideways
 * page scroll or clipped text at every width, reflow at 200 % zoom, a text-spacing override, and the
 * tool's focus/Escape behaviour.
 *
 * The answers column is measured through the stable answer-card test id answer-floor_area_allowance:
 * at desktop it sits in the 44 fr grid column, so its width is ~44 % of the window and never the
 * ~100 % it would be stacked. That 40–48 % band therefore also proves the two columns are present.
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

/** Text clipped by overflow:hidden/clip anywhere OUTSIDE a labelled scroll region (role=region with
 * an aria-label). Returns a short sample of each offender's text; an empty list is the pass. */
async function clippedTextOutsideScrollRegions(dialog: Locator): Promise<string[]> {
  return dialog.evaluate((root) => {
    const offenders: string[] = [];
    const regions = Array.from(root.querySelectorAll('[role="region"][aria-label]'));
    for (const element of Array.from(root.querySelectorAll<HTMLElement>("*"))) {
      const overflowX = getComputedStyle(element).overflowX;
      if (overflowX !== "hidden" && overflowX !== "clip") continue;
      if (element.scrollWidth <= element.clientWidth + 1) continue;
      if (regions.some((region) => region.contains(element))) continue;
      offenders.push((element.textContent ?? "").trim().slice(0, 40));
    }
    return offenders;
  });
}

const WIDTHS = [320, 390, 768, 1024, 1440, 1920];

test.describe("M5-T149 results layout — flag-on, the real results route", () => {
  for (const width of WIDTHS) {
    test(`at ${width} px: no sideways page scroll and no clipped text outside labelled scroll regions`, async ({
      page,
    }) => {
      await page.setViewportSize({ width, height: 900 });
      const dialog = await openResults(page);
      expect(await pageHorizontalOverflow(page)).toBeLessThanOrEqual(1);
      expect(await clippedTextOutsideScrollRegions(dialog)).toEqual([]);
    });
  }

  test("at 1440 px the answers column is 40–48 % of the window width and at least 320 px (S1)", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    const dialog = await openResults(page);
    const dialogBox = await dialog.boundingBox();
    const answersBox = await dialog.getByTestId("answer-floor_area_allowance").boundingBox();
    expect(dialogBox).not.toBeNull();
    expect(answersBox).not.toBeNull();
    const ratio = answersBox!.width / dialogBox!.width;
    expect(answersBox!.width).toBeGreaterThanOrEqual(320);
    expect(ratio).toBeGreaterThanOrEqual(0.4);
    expect(ratio).toBeLessThanOrEqual(0.48);
  });

  test("at 1280 px survives a text-spacing override, and reflows at 200 % zoom with no sideways scroll (S2)", async ({
    page,
  }) => {
    // Text-spacing (WCAG 1.4.12) applied to the window content: nothing is lost and the page does
    // not scroll sideways.
    await page.setViewportSize({ width: 1280, height: 900 });
    const dialog = await openResults(page);
    await page.addStyleTag({
      content:
        ".workspace-window__content, .workspace-window__content * {" +
        " line-height: 1.5 !important; letter-spacing: 0.12em !important;" +
        " word-spacing: 0.16em !important; }" +
        " .workspace-window__content p { margin-bottom: 2em !important; }",
    });
    await expect(dialog.getByTestId("answer-floor_area_allowance")).toBeVisible();
    expect(await pageHorizontalOverflow(page)).toBeLessThanOrEqual(1);

    // 200 % zoom of a 1280 px layout reflows to ~640 CSS px: the content must reflow, not scroll.
    await page.setViewportSize({ width: 640, height: 900 });
    const reflowed = await openResults(page);
    await expect(reflowed.getByTestId("answer-floor_area_allowance")).toBeVisible();
    expect(await pageHorizontalOverflow(page)).toBeLessThanOrEqual(1);
  });

  test("keyboard: opening the tool moves focus into it, Escape returns to the opener, and a Details control keeps focus in the window (S4)", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await routeApi(page);
    await page.goto(`/property/workspace?ruleeval=on&bbl=${BBL}`);
    await expect(page.getByTestId("connected-dashboard")).toBeVisible({ timeout: 15_000 });
    const opener = page.getByRole("button", { name: WINDOW_NAME, exact: true });
    await opener.click();
    const dialog = page.getByRole("dialog", { name: WINDOW_NAME });
    await expect(dialog).toBeVisible();
    // Focus moved into the tool (onto its close control).
    await expect(dialog.getByRole("button", { name: `Close ${WINDOW_NAME} window` })).toBeFocused();
    const response = page.waitForResponse(
      (r) => r.url().includes(`/${BBL}/results`) && r.request().method() === "POST",
      { timeout: 20_000 },
    );
    await dialog.getByTestId("results-show").click();
    await response;
    await expect(dialog.getByTestId("three-answers-panel")).toBeVisible({ timeout: 15_000 });

    // A per-result Details control (the three-answers details action, part A) keeps focus inside the
    // window when activated; exact wording is part A's, so this runs only when such a control exists.
    const details = dialog.getByRole("button", { name: /details/i });
    if ((await details.count()) > 0) {
      await details.first().click();
      const focusInside = await dialog.evaluate((root) => root.contains(document.activeElement));
      expect(focusInside).toBe(true);
    }

    // Escape on the window returns focus to the opener (contract §3 focus/return).
    await dialog.getByRole("button", { name: `Close ${WINDOW_NAME} window` }).focus();
    await page.keyboard.press("Escape");
    await expect(dialog).toBeHidden();
    await expect(opener).toBeFocused();
  });
});
