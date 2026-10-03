import { expect, test, type Page } from "@playwright/test";
import profileFixture from "../../../packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json";

/**
 * D-15 slice 2 (plan §5a / §11b, B-10, check C-8) flag-ON human journey, run by the
 * `chromium-flag-on` project against the :3001 server where INTERNAL_PARITY_UI_ENABLED=1
 * (playwright.config.ts). It opens the architect workspace for 215-16 Northern Blvd
 * (BBL 4073340070) — the one BBL the recorded-fixture harness serves a transit/parking
 * status for (e2e/harness/fixture_api.py: `pluto_transit_parking_provider` over the
 * recorded 215-16 Northern PLUTO pack, through the REAL B-02/B-07 pipeline behind
 * INTERNAL_TRANSIT_PARKING_READ_ENABLED + LANE_B_ENABLED — no response byte is
 * hand-written) — opens the "Comparable sales & floor area" tool, and walks the new
 * "Transit and parking zone" section over the real mounted W3 read route
 * (GET /api/v1/properties/{bbl}/transit-parking):
 *   - the read request reaches the REAL API harness (:8000) and answers 200 (not a mock);
 *   - the section headlines the recorded status label and shows the recorded zone;
 *   - the request URL (the DOF/PLUTO SODA endpoint) is NOT on the face before the
 *     "Source" disclosure opens; opening it reveals the dataset version;
 *   - the window closes on Escape and returns focus to its opener.
 *
 * The real transit/parking values are READ from the recorded pack: the route serializes
 * resolve_transit_parking_status over tests/fixtures/benchmark_215_16_northern/
 * pluto_64uk-42ks_bbl_4073340070.json, which records transitzone "Outer Transit Zone"
 * (asserted in services/api/tests/api/test_transit_parking_api.py:
 * test_recorded_200_from_recorded_pack). The status label "Recorded" and zone
 * "Outer Transit Zone" are therefore the harness truth, not a guess.
 *
 * NB: the server-authored `detail` line is shown VERBATIM (plan §5a) and cites the PLUTO
 * dataset in prose ("PLUTO (64uk-42ks)"), so "64uk-42ks" legitimately appears on the
 * face inside that sentence. The STRUCTURED provenance (dataset version, the request
 * URL host) is what stays behind the "Source" disclosure — that is what this spec
 * asserts is off the face until the disclosure opens.
 *
 * The flag-OFF default (no opener, no request) is proven by parity.spec.ts on :3000.
 */

const BBL = "4073340070";
const WINDOW_NAME = "Comparable sales & floor area";
const SOURCE_REQUEST_HOST = "data.cityofnewyork.us"; // only in source.query_ref (behind Source)

async function routeApi(page: Page): Promise<void> {
  await page.route("**/api/v1/properties/**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    // Let the transit/parking (W3) and parity (W4) reads reach the REAL harness.
    if (path.endsWith(`/${BBL}/transit-parking`)) return route.continue();
    if (path.endsWith(`/${BBL}/parity`)) return route.continue();
    const last = path.split("/").at(-1);
    // Serve the base profile from the committed fixture (so the dashboard shell loads);
    // every other sub-resource 404s cleanly.
    if (last !== BBL) return route.fulfill({ status: 404, json: { detail: "not found" } });
    const profile = structuredClone(profileFixture);
    profile.identity.bbl = BBL;
    await route.fulfill({ json: profile });
  });
}

test.describe("D-15 parity window — transit/parking flag-on journey over the real W3 route", () => {
  test("shows the recorded transit zone from the real 200, keeps the request URL behind Source, and closes by keyboard", async ({
    page,
  }) => {
    await routeApi(page);

    await page.goto(`/property/workspace?ruleeval=on&bbl=${BBL}`);
    await expect(page.getByTestId("connected-dashboard")).toBeVisible({ timeout: 15_000 });

    const opener = page.getByRole("button", { name: WINDOW_NAME, exact: true });
    await expect(opener).toBeVisible();

    // Observe the REAL read to the mounted W3 route; assert a 200 from the API harness
    // origin (:8000), not an interception/mock.
    const transitResponsePromise = page.waitForResponse(
      (response) =>
        response.url().includes(`/${BBL}/transit-parking`) &&
        response.request().method() === "GET",
      { timeout: 20_000 },
    );
    await opener.click();

    const dialog = page.getByRole("dialog", { name: WINDOW_NAME });
    await expect(dialog).toBeVisible();

    const transitResponse = await transitResponsePromise;
    expect(transitResponse.status()).toBe(200);
    expect(new URL(transitResponse.url()).port).toBe("8000"); // real cross-origin API, not a page mock

    const section = dialog.getByTestId("transit-parking");
    await expect(section).toBeVisible({ timeout: 15_000 });

    // The route answered 200, so the loading / not-connected cards are NOT shown.
    await expect(dialog.getByTestId("transit-parking-loading")).toHaveCount(0);
    await expect(dialog.getByTestId("transit-parking-unavailable")).toHaveCount(0);

    // The harness truth: a recorded status headline and the recorded Outer Transit Zone.
    await expect(section.getByTestId("transit-parking-headline")).toHaveText("Recorded");
    await expect(section.getByTestId("transit-parking-zone")).toContainText("Outer Transit Zone");
    // check_needed only; a recorded status shows no "Not available" line.
    await expect(section.getByTestId("transit-parking-missing")).toHaveCount(0);

    // The STRUCTURED provenance is off the face until the "Source" disclosure opens:
    // the request-URL host lives only in source.query_ref, inside the closed <details>.
    const faceBefore = await section.innerText();
    expect(faceBefore).not.toContain(SOURCE_REQUEST_HOST);

    const source = section.getByTestId("transit-parking-source");
    await expect(source).toBeVisible();
    await source.locator("summary").click();
    await expect(source).toHaveAttribute("open", "");
    await expect(source).toContainText("Dataset version");
    await expect(source).toContainText("26v2"); // the recorded PLUTO version, only once opened
    await expect(source).toContainText(SOURCE_REQUEST_HOST);

    // Keyboard: the window closes on Escape and returns focus to its opener.
    await dialog.getByRole("button", { name: `Close ${WINDOW_NAME} window` }).focus();
    await page.keyboard.press("Escape");
    await expect(dialog).toBeHidden();
    await expect(opener).toBeFocused();
  });
});
