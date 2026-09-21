import { expect, test, type Page } from "@playwright/test";
import { expectProfile, tabUntil } from "./helpers";

/**
 * Task M5-T060 (D-076 phase B3 slice 2): the KEYBOARD-ONLY proposal-editor
 * journey. Every editor action — editing a coordinate, adding a vertex, adding a
 * level, adding a wall, running the check, and saving a variation — is driven by
 * real focus navigation (Tab to the control, then Enter), never a direct
 * programmatic focus of a single button. The proposal-checks route is flag-gated
 * and POST-only, so the grouped report is served by a route-interception stub
 * that FIRST asserts the intercepted request is a POST carrying the serialized
 * 2263 draft + lot inputs and only THEN returns the accepted M5-T054 rectangle
 * arithmetic (coverage FAIL 0.625 vs 0.5 shortfall 0.125; height PASS 30 <= 60;
 * two COULD_NOT_CHECK). The profile + lot-outline map use the real fixture API.
 * This proves the edit -> check -> read -> save-variation loop, the honesty
 * framing, and the real request contract end-to-end in a browser.
 */

const ATTESTED_REPORT = {
  scenario_label: "scenario-A-baseline",
  proposal_id: "prop-0001",
  source_class: "proposed",
  outline_digest: "sha256:0000000000000000000000000000000000000000000000000000000000000000",
  results: [
    {
      check_id: "lot_coverage_ratio",
      family: "lot_coverage",
      label: "proposed lot coverage ratio",
      unit: "ratio",
      direction: "maximum",
      outcome: "fail",
      provided_value: 0.625,
      required_value: 0.5,
      shortfall: 0.125,
      could_not_check_reason: null,
      detail: "coverage fail",
      provenance: { scenario_label: "scenario-A-baseline", proposal_id: "prop-0001", source_class: "proposed", provided_input_ids: [], provided_provenance: null, rule_id: "pc-lot-coverage-demo", rule_version: null, rule_status: null, coverage_status: "conditional", rule_citations: [] },
    },
    {
      check_id: "building_height",
      family: "residential_height_setback",
      label: "proposed cumulative building height",
      unit: "feet",
      direction: "maximum",
      outcome: "pass",
      provided_value: 30.0,
      required_value: 60.0,
      shortfall: null,
      could_not_check_reason: null,
      detail: "height pass",
      provenance: { scenario_label: "scenario-A-baseline", proposal_id: "prop-0001", source_class: "proposed", provided_input_ids: [], provided_provenance: null, rule_id: "pc-height-demo", rule_version: null, rule_status: null, coverage_status: "conditional", rule_citations: [] },
    },
    {
      check_id: "rear_yard_depth",
      family: "rear_yard",
      label: "proposed minimum wall-to-lot-line setback",
      unit: "feet",
      direction: "minimum",
      outcome: "could_not_check",
      provided_value: 10.0,
      required_value: null,
      shortfall: null,
      could_not_check_reason: "provided_fact_not_commensurate",
      detail: "not a rear-yard depth",
      provenance: { scenario_label: "scenario-A-baseline", proposal_id: "prop-0001", source_class: "proposed", provided_input_ids: [], provided_provenance: null, rule_id: null, rule_version: null, rule_status: null, coverage_status: null, rule_citations: [] },
    },
    {
      check_id: "residential_far_floor_area",
      family: "residential_far",
      label: "proposed gross floor area",
      unit: "square_feet",
      direction: "maximum",
      outcome: "could_not_check",
      provided_value: 15000.0,
      required_value: null,
      shortfall: null,
      could_not_check_reason: "provided_fact_not_commensurate",
      detail: "not a residential zoning floor area",
      provenance: { scenario_label: "scenario-A-baseline", proposal_id: "prop-0001", source_class: "proposed", provided_input_ids: [], provided_provenance: null, rule_id: null, rule_version: null, rule_status: null, coverage_status: null, rule_citations: [] },
    },
  ],
  summary: { pass: 1, fail: 1, could_not_check: 2, total: 4 },
  fact_mapping: [
    { check_id: "lot_coverage_ratio", semantic_gap: null },
    { check_id: "building_height", semantic_gap: null },
    { check_id: "rear_yard_depth", semantic_gap: "the minimum wall-to-lot-line setback is not a rear-yard depth" },
    { check_id: "residential_far_floor_area", semantic_gap: "the geometric gross floor area is not a residential zoning floor area" },
  ],
  rule_input_bindings: { lot_area_sq_ft: "lot_context.area_sq_ft" },
  unmapped_lot_facts: [],
  correlation_id: "e2e-corr",
};

/** The accepted M5-T054 rectangle, as the editor seeds it (proposal-draft.ts
 * rectangleSampleDraft). The journey re-types vertex 0 X to 1000005 and appends
 * one vertex/level/wall, so the serialized POST body must reflect exactly that. */
const RECTANGLE_TAIL: Array<[number, number]> = [
  [1000100, 200000],
  [1000100, 200050],
  [1000000, 200050],
  [1000000, 200000],
];

/** The parts of the serialized route request this journey asserts (mirrors the
 * ProposalCheckRequest contract; typed locally so the spec needs no app-alias
 * import and no `any`). */
interface SerializedProposalCheck {
  proposed_massing: {
    outline: { srid: number; vertices: Array<[number, number]> };
    levels: unknown[];
    exterior_walls: unknown[];
  };
  lot: { area_sq_ft: number | null };
  lot_rule_facts: Record<string, unknown>;
  scenario_label: string;
}

async function openProposalEditor(page: Page, bbl: string): Promise<void> {
  await page.goto("/property?ruleeval=on");
  await page.getByText("Search by tax lot (BBL)", { exact: true }).click();
  await page.getByLabel("BBL", { exact: true }).fill(bbl);
  await page.getByRole("button", { name: "Open property", exact: true }).click();
  await expectProfile(page);
  await page
    .getByRole("navigation", { name: "Architect workspace" })
    .getByRole("link", { name: "Proposal editor", exact: true })
    .click();
}

test("AS-5: keyboard-only proposal edit -> check -> read grouped results -> save variation", async ({ page }) => {
  // The stub asserts the FULL request contract BEFORE returning the canned
  // arithmetic, so a wrong or missing POST body can never be papered over by the
  // response. "Run check" is the only trigger for this route and it is pressed
  // AFTER every keyboard edit below, so the intercepted body already reflects the
  // retyped vertex 0 X plus the appended vertex/level/wall.
  await page.route("**/api/v1/proposal-checks", async (route) => {
    const request = route.request();
    const method = request.method();
    const body = request.postDataJSON() as SerializedProposalCheck;
    expect(method, "the proposal check must be POSTed").toBe("POST");
    expect(body, "the request must carry a JSON body").not.toBeNull();
    expect(body.proposed_massing.outline.srid, "the 2263 numeric authority must be serialized").toBe(2263);
    expect(body.proposed_massing.outline.vertices).toHaveLength(6);
    expect(body.proposed_massing.outline.vertices[0]).toEqual([1000005, 200000]);
    expect(body.proposed_massing.outline.vertices.slice(1, 5)).toEqual(RECTANGLE_TAIL);
    expect(body.proposed_massing.outline.vertices[5]).toEqual([0, 0]);
    expect(body.proposed_massing.levels).toHaveLength(2);
    expect(body.proposed_massing.exterior_walls).toHaveLength(5);
    expect(body.lot.area_sq_ft, "the caller-attested lot area must be serialized").toBe(8000);
    expect(body.scenario_label).toBe("scenario-A-baseline");
    expect(body.lot_rule_facts).toEqual({ zoning_district: "R5", street_width_class: "wide" });
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { "X-Correlation-ID": "e2e-corr" },
      body: JSON.stringify(ATTESTED_REPORT),
    });
  });

  await openProposalEditor(page, "1000010100");
  await expect(page.getByRole("heading", { name: "Proposal editor" })).toBeVisible();
  await expect(page.getByTestId("editor-honesty")).toContainText("not a city record");

  // --- Edit a coordinate by keyboard: reach the field with REAL Tab navigation
  // (never a programmatic focus), assert it actually received focus, then
  // select-all and type. This proves the numeric coordinate input is genuinely
  // keyboard-reachable, exactly like every other control in this journey. ---
  const vertexX = page.getByLabel("Vertex 0 X coordinate");
  for (let i = 0; i < 300; i += 1) {
    if (await vertexX.evaluate((el) => el === document.activeElement)) break;
    await page.keyboard.press("Tab");
  }
  await expect(vertexX).toBeFocused();
  await vertexX.press("Control+a");
  await vertexX.pressSequentially("1000005");
  await expect(vertexX).toHaveValue("1000005");

  // --- Add a vertex by focus navigation (Tab to the control, Enter). ---
  await tabUntil(page, { textContains: "Add vertex" });
  await expect(page.getByRole("button", { name: "Add vertex", exact: true })).toBeFocused();
  await page.keyboard.press("Enter");

  // --- Add a level by focus navigation. ---
  await tabUntil(page, { textContains: "Add level" });
  await expect(page.getByRole("button", { name: "Add level", exact: true })).toBeFocused();
  await page.keyboard.press("Enter");

  // --- Add a wall by focus navigation. ---
  await tabUntil(page, { textContains: "Add wall" });
  await expect(page.getByRole("button", { name: "Add wall", exact: true })).toBeFocused();
  await page.keyboard.press("Enter");

  // --- Run the check by focus navigation (Tab to Run check, Enter). ---
  await tabUntil(page, { textContains: "Run check" });
  await expect(page.getByTestId("run-check")).toBeFocused();
  await page.keyboard.press("Enter");

  await expect(page.getByTestId("proposal-check-summary")).toContainText("1 did not meet an allowance");
  await expect(page.getByTestId("shortfall-lot_coverage_ratio")).toContainText(
    "0.625 ratio provided; 0.5 ratio required; 0.125 ratio short",
  );
  await expect(page.getByTestId("result-building_height")).toContainText("Pass");
  await expect(page.getByTestId("proposal-check-announcer")).toContainText("proposed values you entered");

  // The serialized request contract (POST + the 2263 draft/lot inputs reflecting
  // the keyboard edits: vertex 0 X retyped, one vertex/level/wall appended) was
  // already asserted inside the route stub, BEFORE the canned response was served.

  // --- Save a client-local, ephemeral variation by focus navigation. ---
  await tabUntil(page, { textContains: "Save current proposal as a variation" });
  await expect(page.getByTestId("save-variation")).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.getByTestId("variations-ephemeral")).toContainText("this browser session only");
  await expect(page.getByRole("button", { name: "scenario-A-baseline" })).toBeVisible();
});

/** The 2263 vertices the stubbed bridge returns for the drawn shape. After
 * adoption these become the draft outline, so the subsequent check POST must
 * serialize EXACTLY these (the numeric table is the authority; drawing only
 * fills it). */
const BRIDGED_2263: Array<[number, number]> = [
  [1000020, 200010],
  [1000080, 200010],
  [1000080, 200030],
];

const BRIDGE_BODY = {
  document_kind: "outline_bridge",
  bbl: "1000010100",
  srid: 2263,
  vertices: BRIDGED_2263.map(([x, y]) => ({ x, y })),
  correspondence: {
    method: "affine_least_squares_2d",
    alignment: "forward+offset0",
    alignment_winding: "forward",
    alignment_offset: 0,
    control_point_count: 4,
    candidates_evaluated: 8,
    rms_residual_ft: 0.0004,
    max_residual_ft: 0.0009,
    residual_bound_ft: 2.0,
    runner_up_rms_residual_ft: 55.2,
    alignment_separation_ft: 55.19,
    alignment_separation_min_ft: 2.0,
    source_display_ring: { crs: "EPSG:4326", source_id: "nyc-dcp-mappluto-lot-outline", representation: "lot_outline_display" },
    source_authoritative_ring: { crs: "EPSG:2263", source_id: "nyc-dcp-mappluto-arcgis", representation: "lot_geometry_authoritative" },
  },
  disclosure: "Approximate PROPOSED input for editing, not a survey and not a city record.",
  correlation_id: "e2e-bridge",
};

/** A minimal grouped report the client decodes for the check run AFTER the
 * drawn outline is adopted (one coverage FAIL). */
const DRAWN_REPORT = {
  scenario_label: "scenario-A-baseline",
  proposal_id: "prop-0001",
  source_class: "proposed",
  outline_digest: "sha256:1111111111111111111111111111111111111111111111111111111111111111",
  results: [
    {
      check_id: "lot_coverage_ratio",
      family: "lot_coverage",
      label: "proposed lot coverage ratio",
      unit: "ratio",
      direction: "maximum",
      outcome: "fail",
      provided_value: 0.7,
      required_value: 0.5,
      shortfall: 0.2,
      could_not_check_reason: null,
      detail: "coverage fail",
      provenance: { scenario_label: "scenario-A-baseline", proposal_id: "prop-0001", source_class: "proposed", provided_input_ids: [], provided_provenance: null, rule_id: "pc-lot-coverage-demo", rule_version: null, rule_status: null, coverage_status: "conditional", rule_citations: [] },
    },
  ],
  summary: { pass: 0, fail: 1, could_not_check: 0, total: 1 },
  fact_mapping: [{ check_id: "lot_coverage_ratio", semantic_gap: null }],
  rule_input_bindings: {},
  unmapped_lot_facts: [],
  correlation_id: "e2e-drawn",
};

test("AS-4: draw an outline, bridge it to 2263, adopt into the numeric table, then check the drawn shape", async ({ page }) => {
  // The bridge stub asserts the drawn 4326 outline is POSTed with srid 4326 and
  // at least a triangle BEFORE returning the canned 2263 correspondence — a wrong
  // or missing request can never be papered over by the response.
  await page.route("**/api/v1/outline-bridge", async (route) => {
    const request = route.request();
    const body = request.postDataJSON() as { srid: number; drawn_vertices: Array<[number, number]> };
    expect(request.method(), "the outline bridge must be POSTed").toBe("POST");
    expect(body.srid, "drawn positions are the display 4326 CRS").toBe(4326);
    expect(body.drawn_vertices.length, "an outline is at least a triangle").toBeGreaterThanOrEqual(3);
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { "X-Correlation-ID": "e2e-bridge" },
      body: JSON.stringify(BRIDGE_BODY),
    });
  });

  // The check stub asserts the ADOPTED 2263 vertices are what gets checked — the
  // drawn shape flowed into the numeric authority exactly as if typed.
  await page.route("**/api/v1/proposal-checks", async (route) => {
    const body = route.request().postDataJSON() as { proposed_massing: { outline: { srid: number; vertices: Array<[number, number]> } } };
    expect(route.request().method()).toBe("POST");
    expect(body.proposed_massing.outline.srid).toBe(2263);
    expect(body.proposed_massing.outline.vertices).toEqual(BRIDGED_2263);
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { "X-Correlation-ID": "e2e-drawn" },
      body: JSON.stringify(DRAWN_REPORT),
    });
  });

  await openProposalEditor(page, "1000010100");
  await expect(page.getByRole("heading", { name: "Proposal editor" })).toBeVisible();
  await expect(page.getByTestId("outline-draw-honesty")).toContainText("not a city record");

  // --- Add three drawn points by keyboard focus navigation (Tab to Add, Enter). ---
  await tabUntil(page, { textContains: "Add drawn point" });
  await expect(page.getByRole("button", { name: "Add drawn point" })).toBeFocused();
  await page.keyboard.press("Enter");
  await page.keyboard.press("Enter");
  await page.keyboard.press("Enter");
  await page.getByLabel("Drawn point 0 longitude").fill("-73.9998");
  await page.getByLabel("Drawn point 0 latitude").fill("40.7001");
  await page.getByLabel("Drawn point 1 longitude").fill("-73.9992");
  await page.getByLabel("Drawn point 1 latitude").fill("40.7001");
  await page.getByLabel("Drawn point 2 longitude").fill("-73.9992");
  await page.getByLabel("Drawn point 2 latitude").fill("40.7003");

  // --- Convert the drawn outline to numeric coordinates (keyboard). ---
  await tabUntil(page, { textContains: "Convert to numeric outline" });
  await expect(page.getByTestId("outline-draw-convert")).toBeFocused();
  await page.keyboard.press("Enter");

  // The bridged 2263 vertices land in the numeric authority table as if typed.
  await expect(page.getByTestId("outline-draw-bridged")).toBeVisible();
  await expect(page.getByLabel("Vertex 0 X coordinate")).toHaveValue("1000020");
  await expect(page.getByLabel("Vertex 2 Y coordinate")).toHaveValue("200030");
  await expect(page.getByTestId("outline-draw-status")).toContainText("not a city record");

  // --- Run the check on the ADOPTED shape (keyboard). ---
  await tabUntil(page, { textContains: "Run check" });
  await expect(page.getByTestId("run-check")).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.getByTestId("proposal-check-summary")).toBeVisible();
});
