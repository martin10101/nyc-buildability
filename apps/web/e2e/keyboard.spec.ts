import { expect, test } from "@playwright/test";
import { expectProfile, tabUntil } from "./helpers";

/**
 * S8: the S1 primary journey is completable with the KEYBOARD ONLY —
 * no mouse interaction anywhere in this spec.
 */

test("S8: keyboard-only user completes the primary lookup and opens provenance", async ({
  page,
}) => {
  await page.goto("/property");

  // Reach the BBL input with Tab only, type the BBL, submit with Enter.
  await tabUntil(page, { id: "bbl-input" });
  await page.keyboard.type("1000010010");
  await page.keyboard.press("Enter");
  await expectProfile(page);

  // Reach the lot-area provenance disclosure with Tab only and open it
  // with Enter (native <details>/<summary> keyboard behavior).
  await tabUntil(page, { textContains: "Source for Lot area" });
  await page.keyboard.press("Enter");
  const details = page.locator("details", { hasText: "Source for Lot area" });
  await expect(details).toContainText("nyc-dcp-pluto-soda");
  await expect(details).toContainText("26v1");

  // Focus is visible on interactive elements (focus ring token).
  const focusVisible = await page.evaluate(() => {
    const el = document.activeElement as HTMLElement | null;
    if (!el) return false;
    const style = window.getComputedStyle(el);
    return style.boxShadow !== "none" || style.outlineStyle !== "none";
  });
  expect(focusVisible).toBe(true);
});
