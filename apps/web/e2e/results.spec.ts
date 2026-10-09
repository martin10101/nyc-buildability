import { expect, test, type Page } from "@playwright/test";
import profileFixture from "../../../packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json";

/**
 * S17 flag-OFF default (task M5-T140), run by the `chromium` project against the :3000 server where
 * INTERNAL_RESULTS_UI_ENABLED is NOT set. The results panel ships off in production, so the
 * "Results" opener is absent, a direct `?tool=results` link shows the plain not-available view, and
 * the browser issues NO request to the results route. The browser is proven silent by recording
 * every request URL it makes.
 *
 * The flag-ON journey over the real results route is proven by results.flag-on.spec.ts on :3001.
 */

const BBL = "4073340070";

async function routeApi(page: Page): Promise<void> {
  await page.route("**/api/v1/properties/**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    const last = path.split("/").at(-1);
    if (last !== BBL) return route.fulfill({ status: 404, json: { detail: "not found" } });
    const profile = structuredClone(profileFixture);
    profile.identity.bbl = BBL;
    await route.fulfill({ json: profile });
  });
}

test("flag off: no Results opener, the plain not-available view on a direct link, zero results requests", async ({
  page,
}) => {
  const hits: string[] = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname.endsWith("/results")) hits.push(request.url());
  });

  await routeApi(page);
  // A direct tool link cannot enable a disabled surface: it still shows the plain not-available view.
  await page.goto(`/property/workspace?ruleeval=on&bbl=${BBL}&tool=results`);
  await expect(page.getByTestId("connected-dashboard")).toBeVisible({ timeout: 15_000 });

  // The opener is absent (the website switch is off).
  await expect(page.getByRole("button", { name: "Results", exact: true })).toHaveCount(0);

  // The deep-linked tool window shows the plain not-available view, never the form.
  await expect(
    page.getByRole("heading", { name: "Results is not available in this version" }),
  ).toBeVisible();
  await expect(page.getByTestId("results-form")).toHaveCount(0);

  // Give any stray effect time to fire, then assert total silence on the results route.
  await page.waitForTimeout(500);
  expect(hits, `unexpected results requests: ${hits.join(", ")}`).toEqual([]);
});
