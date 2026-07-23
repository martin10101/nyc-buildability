import { test, expect } from '@playwright/test';

// Owner Mission-Control dashboard (M0-T022) human journey. The e2e web server
// sets INTERNAL_OWNER_DASHBOARD_ENABLED=1 (playwright.config.ts); the route
// reads the REAL committed project-control ledger at request time. Assertions
// are structural (labels, roles, navigation) rather than exact numbers, since
// the live ledger evolves — but a percentage or an honest "unavailable" must
// always be present (never a blank/fabricated value).

test.describe('owner dashboard', () => {
  test('mission control loads with both progress numbers and the internal banner', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.getByTestId('internal-banner')).toBeVisible();
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    await expect(page.getByText('Engineering completion')).toBeVisible();
    await expect(page.getByText('Launch readiness (architect beta)')).toBeVisible();
    // a real percentage OR an explicit unavailable/partial state — never blank
    await expect(page.locator('.dash-stat-value').first()).toHaveText(/%|Unavailable|Partial/);
  });

  test('"How is this calculated?" reveals a reproducible breakdown', async ({ page }) => {
    await page.goto('/dashboard');
    await page.getByText('How is this calculated?').first().click();
    await expect(page.getByRole('columnheader', { name: 'System' }).first()).toBeVisible();
    await expect(page.getByRole('columnheader', { name: 'Weight' }).first()).toBeVisible();
  });

  test('tabs navigate; product map renders clickable system nodes; drawer opens', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.getByRole('tablist', { name: 'Dashboard views' })).toBeVisible();
    await page.getByRole('tab', { name: 'Product Map' }).click();
    await expect(page.getByRole('group', { name: 'Product system dependency map' })).toBeVisible();
    const nodes = page.locator('.dash-node');
    expect(await nodes.count()).toBeGreaterThan(0);
    await nodes.first().click();
    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible();
    await expect(dialog.getByText('What it does')).toBeVisible();
    await expect(dialog.getByText('Can an architect rely on this today?')).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(dialog).toBeHidden();
  });

  test('current work, roadmap, and activity views render', async ({ page }) => {
    await page.goto('/dashboard');
    await page.getByRole('tab', { name: 'Current Work' }).click();
    await expect(page.getByText("What's being worked on now")).toBeVisible();
    await page.getByRole('tab', { name: 'Roadmap' }).click();
    await expect(page.getByText('Roadmap — by product system')).toBeVisible();
    await page.getByRole('tab', { name: 'What Changed' }).click();
    await expect(page.getByRole('heading', { name: 'What changed' })).toBeVisible();
  });

  test('biggest-things-preventing-beta is present and the honesty note is shown', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.getByText('Biggest things preventing an architect beta')).toBeVisible();
    await expect(page.getByText(/not legally verified/i)).toBeVisible();
  });

  test('tabs are keyboard operable with arrow keys', async ({ page }) => {
    await page.goto('/dashboard');
    await page.getByRole('tab', { name: 'Mission Control' }).focus();
    await page.keyboard.press('ArrowRight');
    await expect(page.getByRole('tab', { name: 'Product Map' })).toBeFocused();
  });
});
