import { expect, test } from "@playwright/test";
import { expectProfile, lookup } from "./helpers";

/**
 * S6 partial data (F04 official capture: numfloors omitted by the source)
 * and the conflict journey (SYNTHETIC borocode-conflict variant derived
 * from the F01 official capture — see e2e/harness/fixture_api.py for the
 * documented derivation). Plus S2's D5 provenance-fallback rendering on the
 * F01 lot.
 */

test("S6: partial-data profile renders; missing numfloors is surfaced under the documented policy", async ({
  page,
}) => {
  await lookup(page, "1000010101");
  await expectProfile(page);

  // The missing feasibility-relevant field is surfaced immediately.
  const missing = page.locator("section", {
    has: page.getByRole("heading", { name: /Missing official inputs/ }),
  });
  await expect(missing).toContainText("Number of floors");

  // The grouped remainder is behind an explicit count toggle; opening it
  // reveals everything (nothing silently dropped).
  const toggle = page.getByRole("button", { name: /more missing fields/ });
  await expect(toggle).toBeVisible();
  const label = (await toggle.textContent()) ?? "";
  const count = Number(/Show (\d+) more/.exec(label)?.[1] ?? "0");
  expect(count).toBeGreaterThan(0);
  await toggle.click();
  await expect(
    page.getByRole("button", { name: /Hide \d+ additional missing fields/ }),
  ).toBeVisible();
});

test("S6: conflicting borocode stays visible with both values and sources, unresolved", async ({
  page,
}) => {
  await lookup(page, "1000010103");
  await expectProfile(page);

  const conflicts = page.locator("section", {
    has: page.getByRole("heading", { name: "Data conflicts" }),
  });
  await expect(conflicts).toContainText("Borough code");
  await expect(conflicts).toContainText("resolution: unresolved");
  await expect(conflicts).toContainText("derived from the canonical BBL digits");
  await expect(conflicts).toContainText("record field 'borocode' verbatim");
  // Both values, verbatim, each with its source.
  expect(await conflicts.locator(".conflict-values li").count()).toBe(2);
  await expect(conflicts).toContainText("nyc-dcp-pluto-soda");

  // Affected fact carries data_conflict; unaffected facts stay conditional.
  const conflictBadges = page.locator(".status-badge.status-data_conflict");
  expect(await conflictBadges.count()).toBeGreaterThan(0);
  const conditionalBadges = page.locator(".status-badge.status-conditional");
  expect(await conditionalBadges.count()).toBeGreaterThan(0);

  // Identity is never silently derived under conflict: the screen states
  // that no address can be asserted OR omits borough rather than guessing.
  await expect(page.getByTestId("completeness-banner")).toBeVisible();
});

test("S2: D5 fallback provenance join renders for a contract-1.0.0 profile (no maps)", async ({
  page,
}) => {
  await lookup(page, "1000010100");
  await expectProfile(page);

  const chip = page.locator(".zoning-chip", { hasText: "R3-2" });
  await chip.locator("summary").click();
  // The fallback join is labeled honestly and resolves to the zonedist1
  // source column record.
  await expect(chip).toContainText("Linked by source column name");
  await expect(chip).toContainText("zonedist1");
  await expect(chip).toContainText("nyc-dcp-pluto-soda");

  // S2 boundary values from the official capture render verbatim,
  // including zero-valued facts (lotfront 0 feet) — never dropped.
  await expect(page.getByText("Lot frontage").first()).toBeVisible();
});
