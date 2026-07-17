import { expect, test } from "@playwright/test";
import { lookup } from "./helpers";

/**
 * S4: 404 state=no_match is a RESULT with actionable copy — the condo
 * unit-lot case surfaces the API's billing-lot explanation verbatim,
 * never a generic error page.
 */

test("S4: condo unit lot shows the billing-lot explanation from the API", async ({
  page,
}) => {
  await lookup(page, "1000041001");
  await expect(page.getByTestId("state-no-match")).toBeVisible();
  const explanation = page.getByTestId("no-match-explanation");
  await expect(explanation).toContainText("BILLING lot");
  await expect(explanation).toContainText("7501-7599");
  // It is presented as an official-source result, not a system failure.
  await expect(page.getByTestId("state-no-match")).toContainText(
    "not a system error",
  );
});

test("S2/S4: borough-5 boundary BBL with no record shows the no-match state", async ({
  page,
}) => {
  await lookup(page, "5999999999");
  await expect(page.getByTestId("state-no-match")).toBeVisible();
  await expect(page.getByTestId("state-no-match")).toContainText("5999999999");
});
