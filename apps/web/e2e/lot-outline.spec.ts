import { expect, test, type Page } from "@playwright/test";

/**
 * M5-T023 (D-040-R001): the display-only lot-outline surface on the address
 * confirm card, walked in a real browser through the RECORDED-OFFICIAL-FIXTURE
 * harness (real FastAPI route + real MapPLUTO outline builder over committed
 * official fixtures; the address resolver is a synthetic test seam — see
 * e2e/harness/fixture_api.py). Assertions are on STABLE copy / attribution /
 * testids, never pixels: headless CI Chromium may lack a WebGL context, so the
 * outline case accepts EITHER the rendered map OR the honest WebGL-unavailable
 * fallback — both keep the +/-20 ft copy, the NYC DCP attribution, and the ZoLa
 * link.
 *
 * The whole address surface (hence this lot-outline surface) is gated by the
 * server-read INTERNAL_RULE_EVAL_ENABLED flag AND the per-request `?ruleeval=on`
 * opt-in (rule-evaluation.ts): the walkthrough opts in explicitly.
 */

/** Resolve a test address to its confirm card. The street name selects the
 * lot-outline outcome via the harness's synthetic resolver + fixture routing. */
async function resolveTo(page: Page, street: string): Promise<void> {
  await page.goto("/property?ruleeval=on");
  // Scope every field to the address form AND use exact label matching:
  // getByLabel matches case-insensitive SUBSTRING by default, so inside the form
  // "Borough" also matched the ZIP input labeled "ZIP code (alternative to
  // borough)" (AddressForm.tsx:130). exact:true pins each of the three unique
  // in-form label texts (form-scoping alone left the ZIP-label collision).
  const form = page.getByTestId("address-form");
  await form.getByLabel("House number", { exact: true }).fill("100");
  await form.getByLabel("Street", { exact: true }).fill(street);
  await form.getByLabel("Borough", { exact: true }).selectOption("Manhattan");
  await form.getByTestId("address-submit").click();
  await expect(page.getByTestId("address-confirm-card")).toBeVisible({
    timeout: 15_000,
  });
}

test("single_lot: the confirm card shows the lot-outline surface (map or honest WebGL fallback), keeping the +/-20 ft copy, DCP attribution, and the ZoLa link", async ({
  page,
}) => {
  await resolveTo(page, "OUTLINE AVENUE");

  const region = page.getByTestId("lot-outline");
  await expect(region).toBeVisible();

  // Either an interactive map OR the honest no-WebGL fallback — never a blank
  // container, never a crash.
  const mapOrFallback = page
    .getByTestId("lot-outline-map")
    .or(page.getByTestId("lot-outline-webgl-unavailable"));
  await expect(mapOrFallback.first()).toBeVisible({ timeout: 15_000 });

  // The source's own accuracy statement (+/-20 ft) and the NYC DCP attribution
  // are on the surface regardless of WebGL.
  await expect(page.getByTestId("lot-outline-accuracy")).toContainText("20 ft");
  await expect(page.getByTestId("lot-outline-attribution")).toContainText(
    "City Planning",
  );

  // The ZoLa link is kept as the authoritative-outline escape hatch.
  await expect(page.getByTestId("zola-link")).toBeVisible();

  // Display-only: no measurement is ever derived from the outline coordinates.
  await expect(region).not.toContainText("square feet");
  await expect(region).not.toContainText("acres");

  // No honest-empty / review / failure state is shown for a drawn outline.
  await expect(page.getByTestId("lot-outline-empty")).toHaveCount(0);
  await expect(page.getByTestId("lot-outline-review")).toHaveCount(0);
});

test("condo unit lot: an honest-empty state names the reason (no polygon of its own); no map is fabricated and the ZoLa link stays", async ({
  page,
}) => {
  await resolveTo(page, "CONDO UNIT WAY");

  const empty = page.getByTestId("lot-outline-empty");
  await expect(empty).toBeVisible({ timeout: 15_000 });
  await expect(empty).toContainText("condominium unit lot");

  // No fabricated map.
  await expect(page.getByTestId("lot-outline-map")).toHaveCount(0);
  // The escape hatch is kept.
  await expect(page.getByTestId("zola-link")).toBeVisible();
});

test("multiple_features: a review posture is shown (never a silent first-pick outline), with the ZoLa link kept", async ({
  page,
}) => {
  await resolveTo(page, "REVIEW PLAZA");

  const review = page.getByTestId("lot-outline-review");
  await expect(review).toBeVisible({ timeout: 15_000 });
  await expect(review).toContainText("more than one parcel");

  await expect(page.getByTestId("lot-outline-map")).toHaveCount(0);
  await expect(page.getByTestId("zola-link")).toBeVisible();
});

test("upstream failure: a typed fallback states the outline is unavailable and keeps the ZoLa link — no crash, no blank container", async ({
  page,
}) => {
  await resolveTo(page, "OUTLINE FAIL ROAD");

  const unavailable = page.getByTestId("lot-outline-unavailable");
  await expect(unavailable).toBeVisible({ timeout: 15_000 });
  await expect(unavailable).toContainText("could not be loaded");

  // The confirm card and its ZoLa link are unaffected by the outline failure.
  await expect(page.getByTestId("zola-link")).toBeVisible();
  await expect(page.getByTestId("lot-outline-map")).toHaveCount(0);
});
