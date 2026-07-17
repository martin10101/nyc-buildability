import { expect, test } from "@playwright/test";
import { expectProfile, lookup } from "./helpers";

/**
 * S5: every documented failure state is a distinct, typed, first-class UI
 * state produced by the REAL API error mapping (harness scripts only the
 * transport layer, exactly like the accepted M1-T005 tests):
 *   3000010001 rate_limited (503)   3000010002 timeout (504)
 *   3000010003 source_unavailable (503)   3000010004 schema_drift (502)
 *   3000010005 internal_error (500, generic + correlation id)
 * plus browser-level connection failure with a working retry.
 */

test("S5: rate_limited renders its typed state with retry", async ({ page }) => {
  await lookup(page, "3000010001");
  const state = page.getByTestId("state-rate_limited");
  await expect(state).toBeVisible();
  await expect(state).toContainText("throttling");
  await expect(state).toContainText("rate_limited");
  await expect(state).toContainText("HTTP 503");
  await expect(state.getByRole("button", { name: "Retry lookup" })).toBeVisible();
});

test("S5: timeout renders its typed state with retry", async ({ page }) => {
  await lookup(page, "3000010002");
  const state = page.getByTestId("state-timeout");
  await expect(state).toBeVisible();
  await expect(state).toContainText("timed out");
  await expect(state).toContainText("HTTP 504");
  await expect(state.getByRole("button", { name: "Retry lookup" })).toBeVisible();
});

test("S5: source_unavailable renders its typed state with retry", async ({ page }) => {
  await lookup(page, "3000010003");
  const state = page.getByTestId("state-source_unavailable");
  await expect(state).toBeVisible();
  await expect(state).toContainText("unavailable");
  await expect(state).toContainText("HTTP 503");
});

test("S5: schema_drift is distinct from a transient outage", async ({ page }) => {
  await lookup(page, "3000010004");
  const state = page.getByTestId("state-schema_drift");
  await expect(state).toBeVisible();
  await expect(state).toContainText("changed shape");
  await expect(state).toContainText("not a temporary outage");
  await expect(state).toContainText("HTTP 502");
});

test("S5: unexpected 500 shows the generic message and the correlation id", async ({
  page,
}) => {
  await lookup(page, "3000010005");
  const state = page.getByTestId("state-internal-error");
  await expect(state).toBeVisible();
  await expect(state).toContainText("Something went wrong on our side");
  const correlation = page.getByTestId("correlation-id");
  await expect(correlation).toBeVisible();
  const id = (await correlation.textContent()) ?? "";
  expect(id.trim().length).toBeGreaterThan(0);
  // Nothing internal leaks to the user.
  await expect(state).not.toContainText("Traceback");
  await expect(state).not.toContainText("RuntimeError");
});

test("S5: connection failure is recoverable — retry succeeds once the API is reachable", async ({
  page,
}) => {
  // Simulate the API being unreachable at the browser network layer.
  await page.route("**/api/v1/properties/**", (route) => route.abort("connectionrefused"));
  await lookup(page, "1000010010");
  const state = page.getByTestId("state-network-error");
  await expect(state).toBeVisible();
  await expect(state).toContainText("could not be reached");

  // The API "comes back": remove the interception and retry.
  await page.unroute("**/api/v1/properties/**");
  await page.getByRole("button", { name: "Retry lookup" }).click();
  await expectProfile(page);
});
