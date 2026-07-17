import { expect, test } from "@playwright/test";
import { lookup } from "./helpers";

/**
 * S3: malformed BBLs are rejected client-side BEFORE any network call
 * (request counting proves zero API traffic), and the server 422 path stays
 * reachable through the documented client-validation gap (all-zero block).
 */

test("S3: '1-00001-0100' is rejected before any network call", async ({ page }) => {
  let apiCalls = 0;
  await page.route("**/api/v1/**", async (route) => {
    apiCalls += 1;
    await route.continue();
  });
  await lookup(page, "1-00001-0100");
  await expect(page.getByTestId("client-validation-error")).toContainText(
    "digits only",
  );
  expect(apiCalls).toBe(0);
});

test("S3: '123' is rejected before any network call", async ({ page }) => {
  let apiCalls = 0;
  await page.route("**/api/v1/**", async (route) => {
    apiCalls += 1;
    await route.continue();
  });
  await lookup(page, "123");
  await expect(page.getByTestId("client-validation-error")).toContainText(
    "exactly 10 digits",
  );
  expect(apiCalls).toBe(0);
});

test("S3: server 422 path renders detail.code (all-zero block passes the client mirror)", async ({
  page,
}) => {
  // '1000000000' is 10 digits with borough 1, so the client mirror allows
  // it; the REAL server rejects the all-zero tax block with a typed 422.
  await lookup(page, "1000000000");
  await expect(page.getByTestId("state-validation-error")).toBeVisible();
  await expect(page.getByTestId("validation-code")).toHaveText("invalid_block");
  await expect(page.getByTestId("validation-message")).toContainText("tax block");
});
