import { expect, test } from "@playwright/test";
import { expectProfile, lookup } from "./helpers";

/**
 * S7 honesty checks: internal/dev banner, PRD section 29 disclaimer,
 * visibly disabled address entry with honest copy, no invented
 * "verified"/"best" wording, and no mocked success path in the app (the
 * only way this suite gets data is the real API process).
 */

test("S7: internal banner and PRD 29 disclaimer are prominent", async ({ page }) => {
  await page.goto("/property");
  const banner = page.getByTestId("internal-banner");
  await expect(banner).toBeVisible();
  await expect(banner).toContainText("INTERNAL DEVELOPMENT BUILD");
  // PRD section 29 disclaimer (shared layout footer).
  await expect(
    page.getByText(
      /This platform provides preliminary development and zoning feasibility/,
    ),
  ).toBeVisible();
  await expect(page.getByText(/not a legal opinion/)).toBeVisible();
});

test("S7: address entry is visibly disabled with honest copy", async ({ page }) => {
  await page.goto("/property");
  const address = page.getByLabel(/Address \(not yet available\)/);
  await expect(address).toBeVisible();
  await expect(address).toBeDisabled();
  await expect(page.getByTestId("address-disabled-copy")).toContainText(
    "credentials are still pending",
  );
});

test("S7: no 'verified' badge and no 'best' claim anywhere on a rendered profile", async ({
  page,
}) => {
  await lookup(page, "1000010010");
  await expectProfile(page);
  expect(await page.locator(".status-badge.status-verified").count()).toBe(0);
  // innerText = rendered text only. The API-delivered coverage_policy quote
  // (inside a collapsed drill-down) legitimately contains the word
  // "verified" while stating it is unreachable; the check here is that the
  // APP never presents "verified"/"best" wording to the user.
  const text = await page.locator("body").innerText();
  expect(text).not.toMatch(/\bbest\b/i);
  expect(text).not.toMatch(/\bverified\b/i);
});

test("S7: the app reaches the profile ONLY through the real API process", async ({
  page,
}) => {
  // Block the API: the app must have no other way to show a profile.
  await page.route("**/api/v1/**", (route) => route.abort("connectionrefused"));
  await lookup(page, "1000010010");
  await expect(page.getByTestId("state-network-error")).toBeVisible();
  expect(await page.getByTestId("profile-view").count()).toBe(0);
});
