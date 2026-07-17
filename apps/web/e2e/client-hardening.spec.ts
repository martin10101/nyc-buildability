import { expect, test } from "@playwright/test";
import { expectProfile, lookup } from "./helpers";
import cr500NoMatch from "../../../packages/contracts/fixtures/client_regression/http500_state_no_match.json";

/**
 * S2/S3/S4 (M2-T002): hardened client boundary in a REAL browser.
 *
 * S2 uses the RECORDED adversarial fixture CR-500-no_match (M2-T003
 * scenario S4 artifact) replayed at the network layer — the exact recorded
 * status, headers, and body — to prove the owner-directed regression: the
 * pair (HTTP 500, state=no_match) must NEVER render the no-match screen.
 *
 * S3 mutates REAL API responses (route.fetch then edit) so the malformed
 * 200 is a real builder payload minus/with-broken keys, not an invented
 * document.
 */

test("S2 BLOCKING: recorded HTTP 500 + state=no_match renders unexpected_response with correlation id — never no_match", async ({
  page,
}) => {
  await page.route("**/api/v1/properties/**", (route) =>
    route.fulfill({
      status: cr500NoMatch.http_status,
      headers: {
        "Content-Type": "application/json",
        "X-Correlation-ID": cr500NoMatch.response_headers["X-Correlation-ID"],
      },
      body: JSON.stringify(cr500NoMatch.response_body),
    }),
  );
  await lookup(page, "5999999999");

  const state = page.getByTestId("state-unexpected-response");
  await expect(state).toBeVisible();
  await expect(page.getByTestId("state-no-match")).toHaveCount(0);
  // The mismatch is inspectable: HTTP status, the received state token,
  // and the recorded correlation id.
  await expect(state).toContainText("HTTP 500");
  await expect(page.getByTestId("unexpected-state")).toHaveText("no_match");
  await expect(page.getByTestId("correlation-id")).toHaveText(
    "cr500nomatch00000000000000000000",
  );
  // Nothing from the untrusted body is rendered as a result.
  await expect(page.getByText(/No PLUTO record exists/)).toHaveCount(0);
});

test("S2: any undocumented status/state pair renders unexpected_response", async ({
  page,
}) => {
  await page.route("**/api/v1/properties/**", (route) =>
    route.fulfill({
      status: 503,
      headers: { "Content-Type": "application/json", "X-Correlation-ID": "pair-test-1" },
      body: JSON.stringify({ state: "timeout", message: "wrong status for this state" }),
    }),
  );
  await lookup(page, "1000010010");
  await expect(page.getByTestId("state-unexpected-response")).toBeVisible();
  await expect(page.getByTestId("state-timeout")).toHaveCount(0);
});

test("S3: a REAL 200 profile with a required key removed renders validation-failure with nothing partially rendered", async ({
  page,
}) => {
  await page.route("**/api/v1/properties/**", async (route) => {
    const response = await route.fetch();
    const body = (await response.json()) as Record<string, unknown>;
    delete body.provenance; // break the contract on the REAL payload
    await route.fulfill({
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "X-Correlation-ID": response.headers()["x-correlation-id"] ?? "s3-test",
      },
      body: JSON.stringify(body),
    });
  });
  await lookup(page, "1000010010");

  await expect(page.getByTestId("state-validation-failure")).toBeVisible();
  await expect(page.getByTestId("profile-view")).toHaveCount(0);
  await expect(page.getByTestId("identity-card")).toHaveCount(0);
  // No value from the invalid payload appears (facts, districts).
  await expect(page.getByText("7,577,714")).toHaveCount(0);
  await expect(page.locator(".zoning-chip-code")).toHaveCount(0);
  // The problem list is inspectable.
  const details = page.locator("details", { hasText: "Validation problems" });
  await details.locator("summary").click();
  await expect(page.getByTestId("validation-problems")).toContainText("provenance");
});

test("S3: a REAL 200 declaring an unpublished contract_version renders validation-failure", async ({
  page,
}) => {
  await page.route("**/api/v1/properties/**", async (route) => {
    const response = await route.fetch();
    const body = (await response.json()) as {
      profile_version: Record<string, unknown>;
    };
    body.profile_version.contract_version = "9.9.9";
    await route.fulfill({
      status: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  });
  await lookup(page, "1000010010");
  await expect(page.getByTestId("state-validation-failure")).toBeVisible();
  await expect(page.getByTestId("profile-view")).toHaveCount(0);
});

test("S4/D5: after a successful lookup, an invalid submit keeps the profile rendered with an inline error that clears on retype", async ({
  page,
}) => {
  await lookup(page, "1000010010");
  await expectProfile(page);

  // Client-invalid follow-up submit: NO network call, profile survives.
  let apiCalls = 0;
  await page.route("**/api/v1/**", async (route) => {
    apiCalls += 1;
    await route.continue();
  });
  await page.getByLabel("BBL", { exact: true }).fill("123");
  await page.getByRole("button", { name: "Look up property" }).click();

  await expect(page.getByTestId("client-validation-error")).toContainText(
    "exactly 10 digits",
  );
  await expect(page.getByTestId("profile-view")).toBeVisible();
  await expect(page.getByTestId("identity-card")).toContainText("BBL 1000010010");
  expect(apiCalls).toBe(0);

  // The inline error clears as soon as the user edits the input.
  await page.getByLabel("BBL", { exact: true }).fill("1000");
  await expect(page.getByTestId("client-validation-error")).toHaveCount(0);
  await expect(page.getByTestId("profile-view")).toBeVisible();
});

test("S4: a rapid resubmit cancels the stale request — no late-arrival overwrite", async ({
  page,
}) => {
  // Delay ONLY the first API request long enough that, were it not
  // cancelled, it would resolve AFTER the second lookup and try to
  // overwrite the newer result.
  let first = true;
  await page.route("**/api/v1/properties/**", async (route) => {
    if (first) {
      first = false;
      await new Promise((resolve) => setTimeout(resolve, 3000));
      // The client should have aborted this request by now; continuing may
      // fail harmlessly if the browser has already dropped it.
      await route.continue().catch(() => {});
      return;
    }
    await route.continue();
  });

  await page.goto("/property");
  await page.getByLabel("BBL", { exact: true }).fill("1000010100");
  await page.getByRole("button", { name: "Look up property" }).click();
  // Supersede immediately with a different BBL.
  await page.getByLabel("BBL", { exact: true }).fill("1000010010");
  await page.getByRole("button", { name: "Look up property" }).click();

  await expectProfile(page);
  await expect(page.getByTestId("identity-card")).toContainText("BBL 1000010010");

  // Wait past the stale request's delay: the newer result must still own
  // the screen (no flicker back to the stale BBL).
  await page.waitForTimeout(3500);
  await expect(page.getByTestId("identity-card")).toContainText("BBL 1000010010");
});

test("S4: a hung request hits the client timeout budget and is recoverable via retry", async ({
  page,
}) => {
  test.setTimeout(60_000);
  // Hang the API long past the 12s client budget, once.
  let hang = true;
  await page.route("**/api/v1/properties/**", async (route) => {
    if (hang) {
      hang = false;
      await new Promise((resolve) => setTimeout(resolve, 14_000));
      await route.continue().catch(() => {});
      return;
    }
    await route.continue();
  });

  await lookup(page, "1000010010");
  await expect(page.getByTestId("state-client-timeout")).toBeVisible({
    timeout: 20_000,
  });
  await expect(page.getByTestId("state-client-timeout")).toContainText(
    "Retrying is safe",
  );

  // Recovery: retry reaches the real profile.
  await page.getByRole("button", { name: "Retry lookup" }).click();
  await expectProfile(page);
});
