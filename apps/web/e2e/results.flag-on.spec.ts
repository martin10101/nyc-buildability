import { expect, test, type Page } from "@playwright/test";
import profileFixture from "../../../packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json";
import realLot from "../../../docs/reference-cases/R6B/cases/real-lot.json";
// The regenerated committed results document (M5-T146 part E): the engine's recorded 1.4.0 output.
// The live route serves the same engine, so building B's expected strings for the default run are
// read from this document, never typed from a run.
import journeyDoc from "../../../packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json";

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

    // The floor-area figures appear as conditional results. Ruling V11 (5): the card refers to the
    // shared condition BY NAME ("Condition 1"); the condition's full text is stated once in the
    // shared-conditions block, never repeated in the card.
    const allowance = dialog.getByTestId("answer-floor_area_allowance");
    await expect(allowance).toContainText(`${grouped(FA_STANDARD)} sq ft`);
    await expect(allowance).toContainText(`${grouped(FA_QUALIFYING)} sq ft`);
    await expect(allowance).toContainText("Condition 1");
    await expect(dialog.getByTestId("shared-conditions")).toContainText("recorded lot area of 10,075 sq ft");

    // The height limits appear as the district's limits (Table A), conditional on the unchecked
    // conditions, and NOWHERE called the property's maximum.
    const envelope = dialog.getByTestId("answer-permitted_envelope");
    for (const feet of HEIGHTS) await expect(envelope).toContainText(`${feet} ft`);
    await expect(envelope).toContainText("none of these conditions, which were not checked");
    // Coverage and the rear yard read "not known".
    await expect(envelope).toContainText("Not known");

    // Ruling V11 (2): building B is listed at the default run, so the building-option card reads
    // "Scheduled area: …" with "Site fit not verified" ahead of any caveat — never "Not available"
    // or "shown below".
    const buildingOptionCard = dialog.getByTestId("answer-building_option");
    await expect(buildingOptionCard).toContainText("Scheduled area");
    await expect(buildingOptionCard).toContainText("Site fit not verified");
    await expect(buildingOptionCard).not.toContainText("Not available");
    await expect(buildingOptionCard).not.toContainText("shown below");

    // The worked first-building option appears through the LIVE route (contract 1.4.0) as a labelled
    // alternative with its floor schedule, its conditions, what was not checked, and its preliminary
    // capacity estimate. Building B's expected strings are read from the committed regenerated
    // document (the engine's recorded output), never typed from a run. The coverage-by-portion block
    // is NOT asserted here: whether the harness carries the lot outline varies and the missing-outline
    // behaviour is a server change; the vitest leg covers coverage against the document.
    const buildingB = journeyDoc.building_alternatives?.[0];
    if (!buildingB) throw new Error("fixture changed: the journey must carry building_alternatives");
    if (buildingB.capacity_estimate.label !== "Preliminary capacity estimate") {
      throw new Error("fixture changed: building B's estimate must be the preliminary capacity estimate");
    }
    const options = dialog.getByTestId("first-building-options");
    await expect(options).toBeVisible();
    const buildingBlock = options.getByTestId("building-alternative").first();
    await expect(buildingBlock.getByTestId("building-alternative-label")).toHaveText(buildingB.label);
    // its floor schedule: one body row per worked storey (three storeys).
    await expect(buildingBlock.getByTestId("floor-schedule").getByTestId("floor-schedule-row")).toHaveCount(
      buildingB.storey_count,
    );
    // it is conditional (the marker is a word) and lists what was not checked.
    await expect(buildingBlock.getByTestId("option-conditional-marker")).toHaveText("Conditional");
    await expect(buildingBlock.getByTestId("building-alternative-not-checked")).toContainText(
      buildingB.not_checked[0],
    );
    // the preliminary capacity estimate with its range, read from the document.
    await expect(buildingBlock.getByTestId("capacity-estimate-label")).toHaveText(
      "Preliminary capacity estimate",
    );
    await expect(buildingBlock.getByTestId("capacity-estimate-range")).toContainText(
      buildingB.capacity_estimate.quotient_low.toFixed(2),
    );
    await expect(buildingBlock.getByTestId("capacity-estimate-range")).toContainText(
      buildingB.capacity_estimate.quotient_high.toFixed(2),
    );
    // fit_note beside the building, as plain text.
    await expect(buildingBlock.getByTestId("building-alternative-fit-note")).toHaveText(buildingB.fit_note);
    // nothing is called feasible.
    expect(await options.innerText()).not.toMatch(/feasible|complies|legally correct/i);
    // the legal dwelling-unit limit shows withheld with NO number (it becomes "29 units" only after
    // the special-density statement, asserted later).
    await expect(allowance).toContainText("Legal dwelling-unit limit");
    expect(await dialog.innerText()).not.toContain(`${UNIT_LIMIT_STANDARD} units`);

    // No line the website writes calls a value the maximum for the property (R269).
    expect(await dialog.innerText()).not.toContain("maximum for this property");

    // The starting height is called the default when none is entered (DB-204 a).
    expect(await dialog.innerText()).toContain("10-foot floor-to-floor height is used as the default");

    // Enter 14 ft and press again: the returned line says the height was entered, and the form's
    // program label (Standard residence) is the name in the returned housing-program line (R3). The
    // form folded once results showed (ruling V11 (1)); reopen it with "Change inputs" first.
    await dialog.getByTestId("results-change-inputs").click();
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
    // Building B's floor schedule now shows the entered 14-foot floor-to-floor height, never 10.
    const schedule14 = dialog
      .getByTestId("first-building-options")
      .getByTestId("building-alternative")
      .first()
      .getByTestId("floor-schedule");
    await expect(schedule14).toContainText("14 ft");
    await expect(schedule14).not.toContainText("10 ft");

    // Make the special-density statement and press again: the standard legal unit limit appears as
    // a conditional result naming that statement (reference L6), never as a settled number. Reopen
    // the folded form first (ruling V11 (1)).
    await dialog.getByTestId("results-change-inputs").click();
    await dialog.getByTestId("results-density-statement").check();
    const thirdResponse = waitResults(page);
    await dialog.getByTestId("results-show").click();
    await thirdResponse;
    await expect(dialog.getByTestId("three-answers-panel")).toBeVisible();
    await expect(allowance).toContainText(`${UNIT_LIMIT_STANDARD} units`);
    await expect(allowance).toContainText("special density area");

    // The program-name drift guard for the two OTHER programs: select each, press, and assert the
    // returned housing-program line names the label the form shows — read from the form's selected
    // option in the page, never retyped here (R3).
    const programSelect = dialog.getByTestId("results-housing-program");
    for (const value of ["qualifying_affordable_housing", "qualifying_senior_housing"]) {
      // The form folded after the previous result; reopen it (ruling V11 (1)) before changing it.
      await dialog.getByTestId("results-change-inputs").click();
      await programSelect.selectOption(value);
      const label = await programSelect.evaluate(
        (element) => (element as HTMLSelectElement).selectedOptions[0]?.textContent?.trim() ?? "",
      );
      const response = waitResults(page);
      await dialog.getByTestId("results-show").click();
      await response;
      await expect(dialog.getByTestId("three-answers-panel")).toBeVisible();
      await expect(dialog.getByTestId("three-answers-scope")).toContainText(
        `${label} was selected for this run as the housing program.`,
      );
    }

    // Keyboard: the window closes on Escape and returns focus to its opener (W-6).
    await dialog.getByRole("button", { name: `Close ${WINDOW_NAME} window` }).focus();
    await page.keyboard.press("Escape");
    await expect(dialog).toBeHidden();
    await expect(opener).toBeFocused();
  });

  // M5-T147 walkthrough correction (F1/S9): at 16 ft the step-P6 method works NO building (the
  // fewest-storeys plan exceeds the lowest-coverage bound; the areas disagree keeps building A out),
  // so the live route gives the empty-list state. The Building options section must then NAME each
  // not-worked building with its reason and resolver, show NO lead about worked shapes, and never an
  // empty heading; the single Building option card adds no false reason. Run by the orchestrator.
  test("at 16 ft the Building options section says why each building was not worked, with no worked-shapes lead", async ({
    page,
  }) => {
    await routeApi(page);
    await page.goto(`/property/workspace?ruleeval=on&bbl=${BBL}`);
    await expect(page.getByTestId("connected-dashboard")).toBeVisible({ timeout: 15_000 });
    const opener = page.getByRole("button", { name: WINDOW_NAME, exact: true });
    await opener.click();
    const dialog = page.getByRole("dialog", { name: WINDOW_NAME });
    await expect(dialog).toBeVisible();

    await dialog.getByTestId("results-floor-to-floor").fill("16");
    const response = waitResults(page);
    await dialog.getByTestId("results-show").click();
    await response;
    await expect(dialog.getByTestId("three-answers-panel")).toBeVisible({ timeout: 15_000 });

    const options = dialog.getByTestId("first-building-options");
    await expect(options).toBeVisible();
    // no building is worked, so no alternative block and no worked-shapes lead.
    await expect(options.getByTestId("building-alternative")).toHaveCount(0);
    await expect(options.getByTestId("first-building-options-lead")).not.toContainText(
      "worked from the floor-area allowance",
    );
    // each not-worked building names its reason and what would resolve it; the heading is not empty.
    const notWorked = options.getByTestId("building-not-worked");
    await expect(notWorked.first()).toBeVisible();
    await expect(notWorked.first().getByTestId("building-not-worked-reason")).toContainText("Not known");
    await expect(notWorked.first().getByTestId("building-not-worked-resolved")).toContainText(
      "What would let it be worked:",
    );
    // the Building option card: no building is listed at 16 ft, so it reads "Not known" (ruling
    // V11 (2), one wording) — never "Not available"/"shown below" — and names no machine field.
    const optionCard = dialog.getByTestId("answer-building_option");
    await expect(optionCard).toContainText("Not known");
    await expect(optionCard).not.toContainText("Not available");
    await expect(optionCard).not.toContainText("shown below");
    await expect(optionCard).not.toContainText("below the minimum base height");
    await expect(optionCard).not.toContainText("buildings_not_worked");
  });
});
