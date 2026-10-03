import { expect, test, type Page } from "@playwright/test";
import profileFixture from "../../../packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json";

/**
 * D-12 slice 2 (plan M2-06 / L-11, §8a) flag-ON human journey, run by the
 * `chromium-flag-on` project against the :3001 server where
 * INTERNAL_HIDDEN_ISSUE_FLAGS_UI_ENABLED=1 (playwright.config.ts). It opens the
 * architect workspace for 215-16 Northern Blvd (BBL 4073340070) — the one BBL the
 * recorded-fixture harness serves §8a hidden-issue inputs for (e2e/harness/fixture_api.py:
 * `pluto_hidden_issue_flag_inputs_provider` over the recorded 215-16 Northern PLUTO pack,
 * through the REAL B-02/B-07 pipeline behind the INTERNAL_HIDDEN_ISSUE_FLAGS_READ_ENABLED +
 * LANE_B_ENABLED gates — no response byte is hand-written) — opens the "Hidden issues" tool,
 * and walks the real surface served by the mounted W2 read route
 * (GET /api/v1/properties/{bbl}/hidden-issue-flags):
 *   - the read request reaches the REAL API harness (:8000) and answers 200 (not a mock);
 *   - the four §8a groups render, each item once with its status label;
 *   - "No flag" carries the specific-check wording (a not_flagged item is present);
 *   - the §5a status strip has at most three items;
 *   - the "not connected yet" card is NOT shown (the route is mounted and answers);
 *   - no internal code is on the face (no raw <bbl>:<field> fact_ref token, no dotted
 *     item_id token, no dataset id outside an opened "Source" disclosure);
 *   - the "Source" disclosure exists, opens, and only then reveals the dataset id;
 *   - the window is closable by keyboard (Escape), returning focus to its opener.
 *
 * The flag-OFF default (tool absent, no fetch) stays proven by hidden-issues.spec.ts on :3000.
 *
 * The property PROFILE for this BBL is served from the committed fixture (the harness PLUTO
 * table has no Northern base-properties profile — same seam as lot-site-setup.flag-on.spec.ts),
 * while the /hidden-issue-flags request is allowed through to the real harness.
 *
 * Label/wording constants are COPIED verbatim from src (they are NOT imported: no e2e spec
 * imports from `@/`, and the `@/` path alias is not relied on in the Playwright runtime here):
 *   - status labels: app/profile/hidden_issue_flags/model.py LABELS
 *     ("Flag" / "Opportunity" / "Check needed" / "No flag");
 *   - the "No flag" meaning: src/lib/architect/hidden-issue-flags-view.ts
 *     STATUS_MEANINGS.not_flagged = "This check found nothing to flag.";
 *   - group ids/titles: app/profile/hidden_issue_flags/{existing_building,zoning_lot_history,
 *     map_based_rules,site_shape_and_street}.py GROUP_ID / GROUP_TITLE.
 * Forbidden on-face tokens are DERIVED from what the harness serves: the item_id strings are
 * read from each rendered row's data-testid, and the dataset id (64uk-42ks) is the PLUTO
 * DATASET_ID (app/connectors/pluto_soda.py) the map-based group's evidence carries.
 */

const BBL = "4073340070";
const STATUS_LABELS = ["Flag", "Opportunity", "Check needed", "No flag"];
const NOT_FLAGGED_MEANING = "This check found nothing to flag.";
const PLUTO_DATASET_ID = "64uk-42ks";
const GROUPS: ReadonlyArray<{ readonly id: string; readonly title: string }> = [
  { id: "existing_building", title: "Existing building" },
  { id: "zoning_lot_history", title: "Zoning-lot history" },
  { id: "map_based_rules", title: "Map-based rules" },
  { id: "site_shape_and_street", title: "Site shape and street" },
];

async function routeApi(page: Page): Promise<void> {
  await page.route("**/api/v1/properties/**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    // Let the §8a hidden-issue-flags read reach the REAL recorded-fixture harness.
    if (path.endsWith(`/${BBL}/hidden-issue-flags`)) return route.continue();
    const last = path.split("/").at(-1);
    // Serve the base profile from the committed fixture (so the dashboard shell loads); every
    // other sub-resource (condo-records, lot-geometry, scenario, rule-evaluation) 404s cleanly.
    if (last !== BBL) return route.fulfill({ status: 404, json: { detail: "not found" } });
    const profile = structuredClone(profileFixture);
    profile.identity.bbl = BBL;
    await route.fulfill({ json: profile });
  });
}

test.describe("D-12 hidden issues — flag-on journey over the real mounted W2 read route", () => {
  test("renders the four §8a groups from the real 200, keeps internal codes off the face, and closes by keyboard", async ({ page }) => {
    await routeApi(page);

    await page.goto(`/property/workspace?ruleeval=on&bbl=${BBL}`);
    await expect(page.getByTestId("connected-dashboard")).toBeVisible({ timeout: 15_000 });

    const opener = page.getByRole("button", { name: "Hidden issues", exact: true });
    await expect(opener).toBeVisible();

    // Observe the REAL read request to the mounted W2 route; assert a 200 from the API
    // harness origin (:8000), not an interception/mock.
    const flagsResponsePromise = page.waitForResponse(
      (response) =>
        response.url().includes(`/${BBL}/hidden-issue-flags`) &&
        response.request().method() === "GET",
      { timeout: 20_000 },
    );
    await opener.click();

    const dialog = page.getByRole("dialog", { name: "Hidden issues" });
    await expect(dialog).toBeVisible();

    const flagsResponse = await flagsResponsePromise;
    expect(flagsResponse.status()).toBe(200);
    expect(new URL(flagsResponse.url()).port).toBe("8000"); // real cross-origin API, not a page mock

    const panel = dialog.getByTestId("hidden-issues");
    await expect(panel).toBeVisible({ timeout: 15_000 });

    // The route is mounted and answered 200, so the plain "not connected yet" / loading
    // cards are NOT shown.
    await expect(dialog.getByTestId("hidden-issues-unavailable")).toHaveCount(0);
    await expect(dialog.getByTestId("hidden-issues-loading")).toHaveCount(0);

    // The four §8a groups, each with its plain title.
    for (const group of GROUPS) {
      const section = panel.getByTestId(`hidden-issues-group-${group.id}`);
      await expect(section).toBeVisible();
      await expect(section.getByRole("heading", { name: group.title })).toBeVisible();
    }

    // The one §5a status strip carries at most three items.
    await expect(panel.getByTestId("hidden-issues-strip")).toBeVisible();
    const stripText = await panel.getByTestId("hidden-issues-strip-items").innerText();
    const stripItems = stripText.split(" · ").map((item) => item.trim()).filter(Boolean);
    expect(stripItems.length).toBeGreaterThan(0);
    expect(stripItems.length).toBeLessThanOrEqual(3);

    // Each item appears once (unique row data-testids) and carries exactly one status label
    // drawn from the four allowed labels.
    const rowTestIds = await panel
      .locator("li.hidden-issue")
      .evaluateAll((nodes: Element[]) => nodes.map((node) => node.getAttribute("data-testid") ?? ""));
    expect(rowTestIds.length).toBeGreaterThan(0);
    expect(new Set(rowTestIds).size).toBe(rowTestIds.length);

    const statusLabels = await panel.locator(".hidden-issue__status").allInnerTexts();
    expect(statusLabels.length).toBe(rowTestIds.length); // one label per item
    for (const label of statusLabels) expect(STATUS_LABELS).toContain(label.trim());
    // The recorded pack produces at least one real "Flag" (commercial overlay C2-2) and one
    // recorded "No flag" (splitzone false), so a not_flagged item exists.
    expect(statusLabels.map((label) => label.trim())).toContain("Flag");
    expect(statusLabels.map((label) => label.trim())).toContain("No flag");

    // No internal code is on the face BEFORE any disclosure is opened: no dataset id, no raw
    // <bbl>:<field> fact_ref token, and no dotted item_id token.
    const faceText = await panel.innerText();
    expect(faceText).not.toContain(PLUTO_DATASET_ID);
    expect(faceText).not.toContain(`${BBL}:`);
    const itemIds = rowTestIds.map((id) => id.replace(/^hidden-issue-/, ""));
    for (const itemId of itemIds) {
      expect(itemId).toContain("."); // sanity: it is the dotted <group>.<item> internal code
      expect(faceText).not.toContain(itemId);
    }

    // "No flag" reads as the specific check's result, not a clean bill — the wording lives
    // behind the strip disclosure (R082 "say less"), so open the strip to reveal it.
    await panel.getByTestId("hidden-issues-strip").locator("summary").click();
    await expect(panel.getByText(NOT_FLAGGED_MEANING)).toBeVisible();

    // The "Source" disclosure exists and opens; the dataset id is revealed ONLY once opened.
    const mapGroup = panel.getByTestId("hidden-issues-group-map_based_rules");
    const mapSources = mapGroup.locator('details[data-testid^="hidden-issue-source-"]');
    const mapSourceCount = await mapSources.count();
    expect(mapSourceCount).toBeGreaterThan(0);
    for (let index = 0; index < mapSourceCount; index += 1) {
      await mapSources.nth(index).locator("summary").click();
      await expect(mapSources.nth(index)).toHaveAttribute("open", "");
    }
    await expect(mapSources.first().getByText(/Typical source:/)).toBeVisible();
    await expect(panel.getByText(new RegExp(PLUTO_DATASET_ID)).first()).toBeVisible();

    // Keyboard: the window closes on Escape and returns focus to its opener (a11y parity with
    // the other floating tools).
    await dialog.getByRole("button", { name: "Close Hidden issues window" }).focus();
    await page.keyboard.press("Escape");
    await expect(dialog).toBeHidden();
    await expect(opener).toBeFocused();
  });
});
