import { expect, type Page } from "@playwright/test";

/** Navigate to the Property screen and submit one BBL lookup. */
export async function lookup(page: Page, bbl: string): Promise<void> {
  await page.goto("/property");
  await page.getByLabel("BBL", { exact: true }).fill(bbl);
  await page.getByRole("button", { name: "Look up property" }).click();
}

/** Wait for the rendered profile view after a successful lookup. */
export async function expectProfile(page: Page): Promise<void> {
  await expect(page.getByTestId("profile-view")).toBeVisible({ timeout: 15_000 });
}

/**
 * Press Tab until the focused element matches (by id or contained text),
 * for keyboard-only journeys. Fails after `maxTabs` presses.
 */
export async function tabUntil(
  page: Page,
  match: { id?: string; textContains?: string },
  maxTabs = 300,
): Promise<void> {
  for (let i = 0; i < maxTabs; i += 1) {
    await page.keyboard.press("Tab");
    const matched = await page.evaluate(({ id, textContains }) => {
      const el = document.activeElement as HTMLElement | null;
      if (!el) return false;
      if (id && el.id === id) return true;
      if (textContains && (el.textContent ?? "").includes(textContains)) return true;
      return false;
    }, match);
    if (matched) return;
  }
  throw new Error(`tabUntil: no element matched within ${maxTabs} tab presses`);
}
