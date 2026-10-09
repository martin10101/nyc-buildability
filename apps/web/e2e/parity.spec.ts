import { expect, test, type Page } from "@playwright/test";
import profileFixture from "../../../packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json";

/**
 * D-15 flag-OFF default, run by the `chromium` project against the :3000 server where
 * INTERNAL_PARITY_UI_ENABLED is NOT set. New lane behaviour ships off in production, so
 * the parity window ("Comparable sales & floor area") — and with it the comparable-sales,
 * unused-floor-area and (D-15 slice 2) transit/parking sections — must be absent, and the
 * browser must issue NO request to either read route. The browser is proven silent by
 * recording every request URL it makes.
 *
 * The flag-ON journey over the real W3 route is proven by parity.flag-on.spec.ts on :3001.
 */

const BBL = "4073340070";
const WINDOW_NAME = "Comparable sales & floor area";

async function routeApi(page: Page): Promise<void> {
  await page.route("**/api/v1/properties/**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    const last = path.split("/").at(-1);
    // Serve the base profile so the dashboard shell loads; every sub-resource 404s.
    if (last !== BBL) return route.fulfill({ status: 404, json: { detail: "not found" } });
    const profile = structuredClone(profileFixture);
    profile.identity.bbl = BBL;
    await route.fulfill({ json: profile });
  });
}

test("flag off: no parity window opener and zero requests to the parity or transit-parking routes", async ({
  page,
}) => {
  const hits: string[] = [];
  page.on("request", (request) => {
    const path = new URL(request.url()).pathname;
    if (path.endsWith("/parity") || path.endsWith("/transit-parking")) hits.push(path);
  });

  await routeApi(page);
  await page.goto(`/property/workspace?ruleeval=on&bbl=${BBL}`);
  await expect(page.getByTestId("connected-dashboard")).toBeVisible({ timeout: 15_000 });

  // The opener is absent (the server UI flag is off).
  await expect(page.getByRole("button", { name: WINDOW_NAME, exact: true })).toHaveCount(0);

  // Give any stray effect time to fire, then assert total silence on both routes.
  await page.waitForTimeout(500);
  expect(hits, `unexpected parity/transit requests: ${hits.join(", ")}`).toEqual([]);
});
