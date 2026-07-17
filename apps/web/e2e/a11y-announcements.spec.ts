import { expect, test, type Page } from "@playwright/test";
import { expectProfile, lookup, tabUntil } from "./helpers";

/**
 * M2-T005 (visual-quality Major D1 + minors D2/D3/D4) against the
 * recorded-official-fixture harness (real API, real builder):
 *
 * S1 — outcome arrivals (failure AND success, both screens) are announced
 *      exactly once through the persistent live region; the loading
 *      region's unmount can no longer swallow the announcement.
 * S2 — after outcome arrival and after keyboard retry, focus lands on the
 *      outcome container/heading (document.activeElement asserted); it
 *      never drops to <body>.
 * S3 — D2 disabled styling, D3 bad-param h1, D4 flags exactly once.
 * S6 — a complete keyboard-only lookup-to-confirm journey (no mouse
 *      events) with the announcement/focus behavior active.
 */

interface ActiveElementInfo {
  isBody: boolean;
  isOutcomeHeading: boolean;
  testId: string | null;
  text: string;
}

async function activeElementInfo(page: Page): Promise<ActiveElementInfo> {
  return page.evaluate(() => {
    const el = document.activeElement as HTMLElement | null;
    return {
      isBody: el === document.body || el === null,
      isOutcomeHeading: el?.hasAttribute("data-outcome-heading") ?? false,
      testId: el?.getAttribute("data-testid") ?? null,
      text: (el?.textContent ?? "").slice(0, 120),
    };
  });
}

/** Count live regions whose text contains `needle` (exactly-once check). */
async function liveRegionCount(page: Page, needle: string): Promise<number> {
  return page.evaluate((text) => {
    return Array.from(
      document.querySelectorAll('[aria-live], [role="alert"], [role="status"]'),
    ).filter((el) => (el.textContent ?? "").includes(text)).length;
  }, needle);
}

test("S1/S2: Property failure arrival is announced once and focuses the failure heading", async ({
  page,
}) => {
  await lookup(page, "3000010001"); // rate_limited via real error mapping
  await expect(page.getByTestId("state-rate_limited")).toBeVisible();

  const announcement =
    "Lookup failed: the official data source is throttling requests.";
  await expect(page.getByTestId("outcome-announcer")).toHaveText(announcement);
  expect(await liveRegionCount(page, announcement)).toBe(1);

  const active = await activeElementInfo(page);
  expect(active.isBody).toBe(false);
  expect(active.isOutcomeHeading).toBe(true);
  expect(active.text).toContain("throttling requests");
});

test("S1/S2: Property success arrival is announced once and focuses the profile heading", async ({
  page,
}) => {
  await lookup(page, "1000010010");
  await expectProfile(page);

  await expect(page.getByTestId("outcome-announcer")).toHaveText(
    "Lookup complete: official property profile loaded for BBL 1000010010.",
  );
  expect(await liveRegionCount(page, "profile loaded for BBL 1000010010")).toBe(1);

  const active = await activeElementInfo(page);
  expect(active.isBody).toBe(false);
  expect(active.isOutcomeHeading).toBe(true);
  expect(active.text).toContain("BBL 1000010010");
});

test("S2: KEYBOARD retry on Property — focus moves to the loading card, then the outcome heading, never body", async ({
  page,
}) => {
  // Delay the real API so the loading phase is deterministically observable.
  await page.route("**/api/v1/properties/**", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 800));
    await route.continue();
  });
  await lookup(page, "3000010001");
  await expect(page.getByTestId("state-rate_limited")).toBeVisible({
    timeout: 15_000,
  });

  await tabUntil(page, { textContains: "Retry lookup" });
  await page.keyboard.press("Enter");

  // During the retry's loading phase: focus is on the loading card (the
  // old failure card unmounted with the focused Retry button) and the
  // announcement is cleared so the repeat outcome re-announces.
  await expect(page.getByTestId("loading-stages")).toBeVisible();
  const during = await activeElementInfo(page);
  expect(during.isBody).toBe(false);
  expect(during.testId).toBe("loading-stages");
  await expect(page.getByTestId("outcome-announcer")).toHaveText("");

  // Outcome arrival (same typed failure): focus on the heading, announced.
  await expect(page.getByTestId("state-rate_limited")).toBeVisible({
    timeout: 15_000,
  });
  const after = await activeElementInfo(page);
  expect(after.isBody).toBe(false);
  expect(after.isOutcomeHeading).toBe(true);
  await expect(page.getByTestId("outcome-announcer")).toHaveText(
    "Lookup failed: the official data source is throttling requests.",
  );
});

test("S1/S2: Confirm failure arrival is announced once and focuses the failure heading", async ({
  page,
}) => {
  await page.goto("/property/confirm?bbl=5999999999"); // real 404 no_match
  await expect(page.getByTestId("state-no-match")).toBeVisible({ timeout: 15_000 });

  const announcement =
    "Lookup complete: no property record found in the official dataset.";
  await expect(page.getByTestId("outcome-announcer")).toHaveText(announcement);
  expect(await liveRegionCount(page, announcement)).toBe(1);

  const active = await activeElementInfo(page);
  expect(active.isBody).toBe(false);
  expect(active.isOutcomeHeading).toBe(true);
  expect(active.text).toContain("No property record found");
});

test("S1/S2: Confirm success arrival is announced once and focuses the identity heading", async ({
  page,
}) => {
  await page.goto("/property/confirm?bbl=1000010010");
  await expect(page.getByTestId("confirm-card")).toBeVisible({ timeout: 15_000 });

  await expect(page.getByTestId("outcome-announcer")).toHaveText(
    "Lookup complete: official property profile loaded for BBL 1000010010.",
  );
  expect(await liveRegionCount(page, "profile loaded for BBL 1000010010")).toBe(1);

  const active = await activeElementInfo(page);
  expect(active.isBody).toBe(false);
  expect(active.isOutcomeHeading).toBe(true);
  expect(active.text).toContain("BBL 1000010010");
});

test("S2: KEYBOARD retry on Confirm — focus moves to the loading card, then the outcome heading, never body", async ({
  page,
}) => {
  await page.route("**/api/v1/properties/**", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 800));
    await route.continue();
  });
  await page.goto("/property/confirm?bbl=3000010001");
  await expect(page.getByTestId("state-rate_limited")).toBeVisible({
    timeout: 15_000,
  });

  await tabUntil(page, { textContains: "Retry lookup" });
  await page.keyboard.press("Enter");

  await expect(page.getByTestId("loading-stages")).toBeVisible();
  const during = await activeElementInfo(page);
  expect(during.isBody).toBe(false);
  expect(during.testId).toBe("loading-stages");

  await expect(page.getByTestId("state-rate_limited")).toBeVisible({
    timeout: 15_000,
  });
  const after = await activeElementInfo(page);
  expect(after.isBody).toBe(false);
  expect(after.isOutcomeHeading).toBe(true);
});

test("S6: KEYBOARD-ONLY complete lookup-to-confirm journey with announcements and focus active", async ({
  page,
}) => {
  // No mouse events anywhere in this test.
  await page.goto("/property");
  await tabUntil(page, { id: "bbl-input" });
  await page.keyboard.type("1000010010");
  await page.keyboard.press("Enter");
  await expectProfile(page);

  // Arrival moved focus to the profile heading and announced once.
  let active = await activeElementInfo(page);
  expect(active.isBody).toBe(false);
  expect(active.isOutcomeHeading).toBe(true);
  await expect(page.getByTestId("outcome-announcer")).toHaveText(
    /profile loaded for BBL 1000010010/,
  );

  // Tab forward from the heading to the single next action; Enter follows it.
  await tabUntil(page, { textContains: "Review and confirm this property" });
  await page.keyboard.press("Enter");
  await expect(page).toHaveURL(/\/property\/confirm\?bbl=1000010010/);
  await expect(page.getByTestId("confirm-card")).toBeVisible({ timeout: 15_000 });

  // Confirm arrival: same deterministic focus + single announcement.
  active = await activeElementInfo(page);
  expect(active.isBody).toBe(false);
  expect(active.isOutcomeHeading).toBe(true);
  await expect(page.getByTestId("outcome-announcer")).toHaveText(
    /profile loaded for BBL 1000010010/,
  );

  // The journey continues by keyboard: the disabled confirm affordance is
  // unfocusable (native disabled), and the way back works with Enter.
  await tabUntil(page, { textContains: "Back to property lookup" });
  await page.keyboard.press("Enter");
  await expect(page.getByLabel("BBL", { exact: true })).toBeVisible();
});

test("S3/D2: the disabled confirm affordance is visibly non-interactive (token styling)", async ({
  page,
}) => {
  await page.goto("/property/confirm?bbl=1000010010");
  await expect(page.getByTestId("confirm-card")).toBeVisible({ timeout: 15_000 });

  const button = page.getByTestId("confirm-disabled-button");
  await expect(button).toBeDisabled();
  const style = await button.evaluate((el) => {
    const computed = window.getComputedStyle(el);
    return {
      cursor: computed.cursor,
      backgroundColor: computed.backgroundColor,
      color: computed.color,
    };
  });
  expect(style.cursor).toBe("not-allowed");
  expect(style.backgroundColor).toBe("rgb(244, 244, 241)"); // --surface-inset
  expect(style.color).toBe("rgb(111, 111, 105)"); // --text-tertiary
});

test("S3/D3: the bad-param confirm state renders an h1", async ({ page }) => {
  await page.goto("/property/confirm?bbl=12ab");
  await expect(page.getByTestId("confirm-bad-param")).toBeVisible();
  await expect(
    page.getByRole("heading", { level: 1, name: "No property selected" }),
  ).toBeVisible();
  expect(await page.locator("h1").count()).toBe(1);
});

test("S3/D4: landmark/flood flags render exactly once on Confirm; Property keeps its full table", async ({
  page,
}) => {
  await page.goto("/property/confirm?bbl=1000010010");
  await expect(page.getByTestId("confirm-card")).toBeVisible({ timeout: 15_000 });

  // Each flag label appears exactly once (the dedicated flags section).
  for (const label of [
    "Landmark",
    "Historic district",
    "2007 FIRM flood flag",
    "2015 preliminary FIRM flood flag",
  ]) {
    await expect(page.getByText(label, { exact: true })).toHaveCount(1);
  }

  // Values live in the flags section; the zoning table states where they
  // live and keeps its non-flag features.
  await expect(page.getByTestId("confirm-flags")).toContainText("INDIVIDUAL LANDMARK");
  await expect(page.getByTestId("zoning-section")).not.toContainText(
    "INDIVIDUAL LANDMARK",
  );
  await expect(page.getByTestId("zoning-section")).toContainText(
    "each official value is shown once",
  );
  await expect(page.getByTestId("zoning-section")).toContainText("Zoning map");

  // Property screen regression: the unfiltered table still shows flags.
  await lookup(page, "1000010010");
  await expectProfile(page);
  await expect(page.getByTestId("zoning-section")).toContainText(
    "Mapped features and flags",
  );
  await expect(page.getByTestId("zoning-section")).toContainText("2007 FIRM flood flag");
});
