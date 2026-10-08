import { expect, test, type Page } from "@playwright/test";
import profileFixture from "../../../packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json";
import realLot from "../../../docs/reference-cases/R6B/cases/real-lot.json";

/**
 * W-5 / S16 [LAW] flag-ON human journey (task M5-T140), run by the `chromium-flag-on` project
 * against the :3001 server where INTERNAL_RESULTS_UI_ENABLED=1 (playwright.config.ts). It opens the
 * architect workspace for 215-16 Northern Boulevard (BBL 4073340070), opens the "Results" tool,
 * presses "Show results", and observes the REAL POST to the mounted results route (:8000) —
 * route / engine chain / contract guard are the production code paths, no response byte is
 * hand-written (e2e/harness/fixture_api.py). The journey then enters a 14-foot height and makes
 * the special-density statement with a fresh press each time.
 *
 * EXPECTED VALUES COME FROM the reference case docs/reference-cases/R6B/cases/real-lot.json (step
 * R0), worked out from the law text, NOT from the recorded program answer.
 */

const BBL = "4073340070";
const WINDOW_NAME = "Results";

/** The expected value of one reference-case row (step R0). */
function rowValue(rowId: string): string | number | null {
  const row = realLot.rows.find((entry) => entry.row_id === rowId);
  if (!row) throw new Error(`reference case changed: row ${rowId} missing`);
  return row.expected.value as string | number | null;
}

/** The feet figures a height row states (e.g. "... maximum building 55 ft" -> [30, 45, 55]). */
function heightFeet(rowId: string): number[] {
  const value = String(rowValue(rowId));
  return [...value.matchAll(/(\d+) ft/g)].map((match) => Number(match[1]));
}

const FA_STANDARD = Number(rowValue("L1")); // 20150
const FA_QUALIFYING = Number(rowValue("L2")); // 24180
const UNIT_LIMIT_STANDARD = Number(rowValue("L6")); // 29
const HEIGHTS = [...new Set([...heightFeet("L3"), ...heightFeet("L4")])]; // {30,45,55,65}

function grouped(value: number): string {
  return value.toLocaleString("en-US");
}

async function routeApi(page: Page): Promise<void> {
  await page.route("**/api/v1/properties/**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    // Let the results (POST) read reach the REAL harness; serve the base profile; 404 the rest.
    if (path.endsWith(`/${BBL}/results`)) return route.continue();
    const last = path.split("/").at(-1);
    if (last !== BBL) return route.fulfill({ status: 404, json: { detail: "not found" } });
    const profile = structuredClone(profileFixture);
    profile.identity.bbl = BBL;
    await route.fulfill({ json: profile });
  });
}

async function waitResults(page: Page) {
  return page.waitForResponse(
    (response) => response.url().includes(`/${BBL}/results`) && response.request().method() === "POST",
    { timeout: 20_000 },
  );
}

test.describe("M5-T140 results panel — flag-on journey over the real results route", () => {
  test("shows the district limits conditional (never the property's maximum), carries the user's choices, and closes by keyboard", async ({
    page,
  }) => {
    await routeApi(page);
    await page.goto(`/property/workspace?ruleeval=on&bbl=${BBL}`);
    await expect(page.getByTestId("connected-dashboard")).toBeVisible({ timeout: 15_000 });

    const opener = page.getByRole("button", { name: WINDOW_NAME, exact: true });
    await expect(opener).toBeVisible();
    await opener.click();

    const dialog = page.getByRole("dialog", { name: WINDOW_NAME });
    await expect(dialog).toBeVisible();
    // Ruling R2: nothing is asked of the server until the button is pressed.
    const firstResponse = waitResults(page);
    await dialog.getByTestId("results-show").click();
    const first = await firstResponse;
    expect(first.status()).toBe(200);
    expect(new URL(first.url()).port).toBe("8000"); // real cross-origin API, not a page mock

    await expect(dialog.getByTestId("three-answers-panel")).toBeVisible({ timeout: 15_000 });

    // The floor-area figures appear as conditional results naming the recorded-area condition.
    const allowance = dialog.getByTestId("answer-floor_area_allowance");
    await expect(allowance).toContainText(`${grouped(FA_STANDARD)} sq ft`);
    await expect(allowance).toContainText(`${grouped(FA_QUALIFYING)} sq ft`);
    await expect(allowance).toContainText("recorded lot area of 10,075 sq ft");

    // The height limits appear as the district's limits (Table A), conditional on the unchecked
    // conditions, and NOWHERE called the property's maximum.
    const envelope = dialog.getByTestId("answer-permitted_envelope");
    for (const feet of HEIGHTS) await expect(envelope).toContainText(`${feet} ft`);
    await expect(envelope).toContainText("none of these conditions, which were not checked");
    // Coverage and the rear yard read "not known".
    await expect(envelope).toContainText("Not known");

    // The building option reads "Not available".
    await expect(dialog.getByTestId("answer-building_option")).toContainText("Not available");

    // No line the website writes calls a value the maximum for the property (R269).
    expect(await dialog.innerText()).not.toContain("maximum for this property");

    // The starting height is called the default when none is entered (DB-204 a).
    expect(await dialog.innerText()).toContain("10-foot floor-to-floor height is used as the default");

    // Enter 14 ft and press again: the returned line says the height was entered, and the form's
    // program label (Standard residence) is the name in the returned housing-program line (R3).
    await dialog.getByTestId("results-floor-to-floor").fill("14");
    const secondResponse = waitResults(page);
    await dialog.getByTestId("results-show").click();
    await secondResponse;
    await expect(dialog.getByTestId("three-answers-panel")).toBeVisible();
    await expect(dialog.getByTestId("three-answers-scope")).toContainText(
      "A 14-foot floor-to-floor height was entered for this run.",
    );
    await expect(dialog.getByTestId("three-answers-scope")).toContainText(
      "Standard residence was selected for this run as the housing program.",
    );

    // Make the special-density statement and press again: the standard legal unit limit appears as
    // a conditional result naming that statement (reference L6), never as a settled number.
    await dialog.getByTestId("results-density-statement").check();
    const thirdResponse = waitResults(page);
    await dialog.getByTestId("results-show").click();
    await thirdResponse;
    await expect(dialog.getByTestId("three-answers-panel")).toBeVisible();
    await expect(allowance).toContainText(`${UNIT_LIMIT_STANDARD} units`);
    await expect(allowance).toContainText("special density area");

    // Keyboard: the window closes on Escape and returns focus to its opener (W-6).
    await dialog.getByRole("button", { name: `Close ${WINDOW_NAME} window` }).focus();
    await page.keyboard.press("Escape");
    await expect(dialog).toBeHidden();
    await expect(opener).toBeFocused();
  });
});
