import { expect, test, type Page } from "@playwright/test";
import { expectProfile } from "./helpers";

/**
 * M4-T005 phase 3 — the DEFENSE-IN-DEPTH no-call guarantee.
 *
 * Even though this test server has the frontend env flag ON
 * (INTERNAL_RULE_EVAL_UI=1) and the API's server flag ON, a request that does
 * NOT opt in must render no rule-evaluation surface and must issue NO request
 * to the rule-evaluation endpoint. The browser is proven silent by recording
 * every request URL it makes.
 */

async function recordRuleEvalRequests(page: Page): Promise<string[]> {
  const hits: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/rule-evaluation")) hits.push(request.url());
  });
  return hits;
}

test("no opt-in: the surface is absent and the browser never calls the rule-eval endpoint", async ({
  page,
}) => {
  const hits = await recordRuleEvalRequests(page);

  await page.goto("/property"); // no ?ruleeval=on
  await page.getByLabel("BBL", { exact: true }).fill("1000010100");
  await page.getByRole("button", { name: "Look up property" }).click();
  await expectProfile(page);

  // Give any stray effect time to fire, then assert total silence.
  await page.waitForTimeout(500);
  await expect(page.getByTestId("rule-eval-panel")).toHaveCount(0);
  expect(hits, `unexpected rule-evaluation requests: ${hits.join(", ")}`).toEqual([]);
});

test("explicit ?ruleeval=off: the kill switch also keeps the surface off and silent", async ({
  page,
}) => {
  const hits = await recordRuleEvalRequests(page);

  await page.goto("/property?ruleeval=off");
  await page.getByLabel("BBL", { exact: true }).fill("1000010100");
  await page.getByRole("button", { name: "Look up property" }).click();
  await expectProfile(page);

  await page.waitForTimeout(500);
  await expect(page.getByTestId("rule-eval-panel")).toHaveCount(0);
  expect(hits, `unexpected rule-evaluation requests: ${hits.join(", ")}`).toEqual([]);
});
