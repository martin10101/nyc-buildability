import { expect, test, type Page } from "@playwright/test";
import { expectProfile, lookup, tabUntil } from "./helpers";

/**
 * S6 (M2-T002, resolving M2-T001 G3 defects D2/D3/D4):
 * - 360/768/1280 viewports render the Property profile and Confirm card
 *   with NO horizontal page overflow (wide tables scroll inside their own
 *   card instead).
 * - The grouped-missing toggle and the failure-state retry button are
 *   operated KEYBOARD-ONLY.
 * - The coverage legend is visible without hover; the shared missing-reason
 *   is stated once with per-field exceptions still shown.
 */

const VIEWPORTS = [
  { width: 360, height: 740, name: "phone-360" },
  { width: 768, height: 1024, name: "tablet-768" },
  { width: 1280, height: 800, name: "desktop-1280" },
] as const;

async function expectNoHorizontalOverflow(page: Page): Promise<void> {
  const overflow = await page.evaluate(() => {
    const doc = document.documentElement;
    return {
      scrollWidth: doc.scrollWidth,
      clientWidth: doc.clientWidth,
    };
  });
  // Allow 1px of sub-pixel rounding.
  expect(
    overflow.scrollWidth,
    `page scrollWidth ${overflow.scrollWidth} must not exceed viewport ${overflow.clientWidth}`,
  ).toBeLessThanOrEqual(overflow.clientWidth + 1);
}

for (const viewport of VIEWPORTS) {
  test(`S6/D2: Property profile renders without horizontal overflow at ${viewport.name}`, async ({
    page,
  }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await lookup(page, "1000010010");
    await expectProfile(page);
    await expectNoHorizontalOverflow(page);
    // The legend (D3) is visible at every supported width.
    await expect(page.getByTestId("coverage-legend")).toBeVisible();
  });

  test(`S6/D2: Confirm card renders without horizontal overflow at ${viewport.name}`, async ({
    page,
  }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await page.goto("/property/confirm?bbl=1000010010");
    await expect(page.getByTestId("confirm-card")).toBeVisible({ timeout: 15_000 });
    await expectNoHorizontalOverflow(page);
    await expect(page.getByTestId("coverage-legend")).toBeVisible();
  });
}

test("S6/D2: the grouped-missing toggle is operated by KEYBOARD only", async ({
  page,
}) => {
  await lookup(page, "1000010101"); // F04 partial-data capture
  await expectProfile(page);

  const toggle = page.getByRole("button", { name: /more missing fields/ });
  await expect(toggle).toHaveAttribute("aria-expanded", "false");

  // Reach the toggle with Tab only and activate it with Enter.
  await tabUntil(page, { textContains: "more missing fields" });
  await page.keyboard.press("Enter");
  await expect(
    page.getByRole("button", { name: /Hide \d+ additional missing fields/ }),
  ).toHaveAttribute("aria-expanded", "true");

  // Collapse again with the keyboard (Space also activates a button).
  await page.keyboard.press("Space");
  await expect(
    page.getByRole("button", { name: /more missing fields/ }),
  ).toHaveAttribute("aria-expanded", "false");
});

test("S6/D2: the failure-state retry button is operated by KEYBOARD only and re-issues the request", async ({
  page,
}) => {
  let apiCalls = 0;
  await page.route("**/api/v1/properties/**", async (route) => {
    apiCalls += 1;
    await route.continue();
  });
  await lookup(page, "3000010001"); // rate_limited (real error mapping)
  await expect(page.getByTestId("state-rate_limited")).toBeVisible();
  expect(apiCalls).toBe(1);

  await tabUntil(page, { textContains: "Retry lookup" });
  await page.keyboard.press("Enter");
  // The retry re-issued a real request (the harness replays rate_limited
  // for this control BBL, so the same typed state returns).
  await expect(page.getByTestId("state-rate_limited")).toBeVisible();
  await expect
    .poll(() => apiCalls, { message: "retry must issue a second API call" })
    .toBe(2);
});

test("S6/D4: the shared missing-reason is stated once; per-field exceptions stay inline", async ({
  page,
}) => {
  await lookup(page, "1000010101"); // F04: numfloors officially "not available"
  await expectProfile(page);

  // The shared boilerplate reason appears exactly once (the section note).
  const sharedNote = page.getByTestId("shared-missing-reason");
  await expect(sharedNote).toBeVisible();
  await expect(sharedNote).toContainText("null-omission semantics");
  await expect(page.getByText(/null-omission semantics/)).toHaveCount(1);

  // The per-field exception (numfloors official-unknown note) is shown
  // inline, distinct from the shared reason.
  const missingSection = page.locator("section", {
    has: page.getByRole("heading", { name: /Missing official inputs/ }),
  });
  await expect(missingSection).toContainText("Number of floors");
  await expect(missingSection).toContainText("numfloors_not_available");
});

test("S6/D3: coverage legend explains every status present WITHOUT hover", async ({
  page,
}) => {
  await lookup(page, "1000010103"); // synthetic borocode conflict variant
  await expectProfile(page);

  const legend = page.getByTestId("coverage-legend");
  await expect(legend).toBeVisible();
  // The conflicting profile carries both conditional and data_conflict
  // badges; each gloss is readable with no interaction at all.
  await expect(legend).toContainText("conditional");
  await expect(legend).toContainText(
    "Official source fact, not yet professionally reviewed.",
  );
  await expect(legend).toContainText("data_conflict");
  await expect(legend).toContainText(
    "Official sources disagree; both values are shown, nothing was resolved.",
  );
});
