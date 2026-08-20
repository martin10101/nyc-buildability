import { expect, test, type Page } from "@playwright/test";
import { expectProfile } from "./helpers";

/**
 * M5-T002 — the DEFENSE-IN-DEPTH no-call guarantee for the scenario surface.
 *
 * A request that does NOT opt in must render no scenario surface and must issue
 * NO request to the scenario endpoint, even when the web test server has the
 * frontend env flag on and the API's server flag on. The browser is proven
 * silent by recording every request URL it makes.
 *
 * This guarantee holds regardless of the out-of-scope property-screen render
 * wiring: with no opt-in the surface is never mounted and its fetch is never
 * issued.
 */

async function recordScenarioRequests(page: Page): Promise<string[]> {
  const hits: string[] = [];
  page.on("request", (request) => {
    // Match the scenario endpoint only, not the /property page navigation.
    if (/\/properties\/[^/]+\/scenario/.test(request.url())) hits.push(request.url());
  });
  return hits;
}

test("no opt-in: the surface is absent and the browser never calls the scenario endpoint", async ({
  page,
}) => {
  const hits = await recordScenarioRequests(page);

  await page.goto("/property"); // no ?scenario=on
  await page.getByLabel("BBL", { exact: true }).fill("1000010100");
  await page.getByRole("button", { name: "Look up property" }).click();
  await expectProfile(page);

  await page.waitForTimeout(500);
  await expect(page.getByTestId("scenario-panel")).toHaveCount(0);
  expect(hits, `unexpected scenario requests: ${hits.join(", ")}`).toEqual([]);
});

test("explicit ?scenario=off: the kill switch also keeps the surface off and silent", async ({
  page,
}) => {
  const hits = await recordScenarioRequests(page);

  await page.goto("/property?scenario=off");
  await page.getByLabel("BBL", { exact: true }).fill("1000010100");
  await page.getByRole("button", { name: "Look up property" }).click();
  await expectProfile(page);

  await page.waitForTimeout(500);
  await expect(page.getByTestId("scenario-panel")).toHaveCount(0);
  expect(hits, `unexpected scenario requests: ${hits.join(", ")}`).toEqual([]);
});
