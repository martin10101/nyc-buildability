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
 * results band. Round 2 strengthens the measurement: each value's bounding box must lie WHOLLY inside
 * the Results window's visible scroll area (the `.workspace-window__content` box), not merely intersect
 * the browser viewport — toBeInViewport passes on a one-pixel sliver, which let the round-1 layout
 * (ceiling top 824 px at 1440, below the ~795 px window fold) pass while the figure was not actually
 * visible. At 1440/1920 the ceiling and the estimate carry 40 px of spare below them.
 *
 * Rate limit (round 2): the results route caps requests per window (results_read.py), shared across
 * every spec. Each test here opens the results exactly ONCE and then RESIZES the viewport across the
 * widths, re-measuring after each resize (the floating window re-fits on resize), so the whole file
 * makes only TWO results requests — never one per width — and does not exhaust the limit for the specs
 * that run after it.
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

/** Open the workspace, open the Results tool, press "Show results", and return the window dialog. This
 * is the ONLY call that issues a results (POST) request; each test calls it once (round 2 rate-limit
 * budget), then resizes the viewport to measure every width without a fresh request. */
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

/**
 * The visible bottom edge (px from the top of the browser window) of the Results window's scroll
 * container `.workspace-window__content`: its border box is the clipped region, so a value whose box
 * bottom is at or above this edge is WHOLLY visible in the first screen (the dialog's visible bottom,
 * round 2). This is stronger than toBeInViewport, which only tests the browser viewport.
 */
async function scrollViewportBottom(dialog: Locator): Promise<number> {
  const box = await dialog.locator(".workspace-window__content").boundingBox();
  if (!box) throw new Error("the Results window scroll container has no bounding box");
  return box.y + box.height;
}

/** The bottom edge (y + height) of an element's box, px from the top of the browser window. */
async function boxBottom(locator: Locator): Promise<number> {
  const box = await locator.boundingBox();
  if (!box) throw new Error("the measured element has no bounding box");
  return box.y + box.height;
}

/** The top edge (y) of an element's box, px from the top of the browser window. */
async function boxTop(locator: Locator): Promise<number> {
  const box = await locator.boundingBox();
  if (!box) throw new Error("the measured element has no bounding box");
  return box.y;
}

// Desktop widths (height 900, window fold ~795 px). The results lead the first screen at each; 40 px
// of spare is required below the ceiling and the estimate at 1440/1920. Measured LARGEST -> SMALLEST
// so the floating window only shrinks to fit each width (it tracks min(1100, viewport) and does not
// re-grow once shrunk, so a descending sweep lands the right window size at every step).
const DESKTOP: ReadonlyArray<{ width: number; spare: number }> = [
  { width: 1920, spare: 40 },
  { width: 1440, spare: 40 },
  { width: 1024, spare: 0 },
  { width: 768, spare: 0 },
];

// Phone widths (height 844, window fold ~836 px); the ceiling top must stay under 1.25x the height.
const PHONE: readonly number[] = [390, 320];

test.describe("M5-T181 results first screen — flag-on, the real results route", () => {
  test("S1/S2/S7: at 768–1920 the allowance headline, the legal ceiling and the apartment estimate lead the first screen (one results request, resized across the widths)", async ({
    page,
  }) => {
    await page.setViewportSize({ width: DESKTOP[0].width, height: 900 });
    const dialog = await openResults(page);
    const identity = dialog.getByTestId("three-answers-identity");
    const allowanceHeadline = dialog
      .getByTestId("answer-floor_area_allowance")
      .getByTestId("answer-headline-number")
      .first();
    const ceiling = dialog.getByTestId("apartment-figures-ceiling-value");
    const estimate = dialog.getByTestId("apartment-figures-estimate-value");

    for (const { width, spare } of DESKTOP) {
      await page.setViewportSize({ width, height: 900 });
      // Settle the re-layout at the new width: the identity and the ceiling must render in the browser
      // viewport (web-first retry) before the exact dialog-relative measurements are read.
      await expect(identity, `identity at ${width}`).toBeInViewport();
      await expect(ceiling, `ceiling at ${width}`).toBeInViewport();

      // The allowance headline, the legal ceiling AND the apartment estimate lie WHOLLY inside the
      // Results window's visible scroll area (box bottom at or above the window's visible bottom), with
      // `spare` px to spare at 1440/1920. This is the round-2 target: not a sliver in the browser
      // viewport, but inside the dialog's visible bottom.
      for (const [label, value] of [
        ["allowance headline", allowanceHeadline],
        ["legal ceiling", ceiling],
        ["apartment estimate", estimate],
      ] as const) {
        await expect
          .poll(
            async () => (await boxBottom(value)) - (await scrollViewportBottom(dialog)),
            { message: `${label} must be ${spare}px above the dialog's visible bottom at ${width}` },
          )
          .toBeLessThanOrEqual(-spare);
      }

      // No sideways page scroll, no clipped text in the dialog, and the two figure cells never overlap.
      expect(await pageHorizontalOverflow(page), `overflow at ${width}`).toBeLessThanOrEqual(1);
      expect(await clippedTextInsideDialog(dialog), `clipped at ${width}`).toEqual([]);
      expect(await parityCellsOverlap(dialog), `overlap at ${width}`).toBe(false);

      if (width >= 1440) {
        // S2: the results band leads the assumed conditions — in the DOM and vertically — so the
        // assumed-conditions list no longer occupies the first screen's right half from the top (R151).
        expect(await resultsPrecedeAssumptions(dialog)).toBe(true);
        const figures = await dialog.getByTestId("apartment-figures").boundingBox();
        const scope = await dialog.getByTestId("three-answers-scope").boundingBox();
        expect(figures).not.toBeNull();
        expect(scope).not.toBeNull();
        expect(figures!.y + figures!.height).toBeLessThanOrEqual(scope!.y + 0.5);
        // The distinction line under the ceiling/estimate is in the first screen too at 1440/1920.
        await expect
          .poll(
            async () =>
              (await boxBottom(dialog.getByTestId("apartment-figures-distinction"))) -
              (await scrollViewportBottom(dialog)),
            { message: `the distinction line must be inside the dialog's visible bottom at ${width}` },
          )
          .toBeLessThanOrEqual(0);
      }
    }
  });

  test("S3/S7: at 390 and 320 the allowance headline is in the first screen and the legal ceiling is one short scroll away (one results request, resized)", async ({
    page,
  }) => {
    const height = 844;
    await page.setViewportSize({ width: PHONE[0], height });
    const dialog = await openResults(page);
    const allowanceHeadline = dialog
      .getByTestId("answer-floor_area_allowance")
      .getByTestId("answer-headline-number")
      .first();
    const ceiling = dialog.getByTestId("apartment-figures-ceiling-value");

    for (const width of PHONE) {
      await page.setViewportSize({ width, height });
      await expect(allowanceHeadline, `allowance headline at ${width}`).toBeInViewport();

      // The allowance headline value is WHOLLY inside the Results window's visible area (keeps the S12
      // intent on a phone, strengthened to the dialog's visible bottom rather than a viewport sliver).
      await expect
        .poll(
          async () => (await boxBottom(allowanceHeadline)) - (await scrollViewportBottom(dialog)),
          { message: `the allowance headline must be inside the dialog's visible bottom at ${width}` },
        )
        .toBeLessThanOrEqual(0);

      // The results still precede the assumed conditions in the DOM.
      expect(await resultsPrecedeAssumptions(dialog)).toBe(true);

      // The legal-ceiling figure is at most one short scroll down (its top under 1.25x the viewport).
      await expect
        .poll(async () => boxTop(ceiling), {
          message: `the ceiling top must be under 1.25x the viewport height at ${width}`,
        })
        .toBeLessThan(height * 1.25);

      // No sideways scroll, and no clipped text — the long address wraps and no value ellipsizes.
      expect(await pageHorizontalOverflow(page), `overflow at ${width}`).toBeLessThanOrEqual(1);
      expect(await clippedTextInsideDialog(dialog), `clipped at ${width}`).toEqual([]);
    }
  });
});
