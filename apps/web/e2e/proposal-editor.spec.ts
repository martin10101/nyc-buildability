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

test("AS-1 pointer: click the lot map to place outline points, then bridge -> adopt -> check the drawn shape", async ({ page }) => {
  // Task M5-T066 (D-082-R001): the POINTER placement journey. The architect
  // clicks the recorded lot map to place drawn outline points, which enter the
  // SAME drawn-outline state the keyboard path fills (one draft model). The
  // stubs are identical to the AS-4 keyboard-draw journey: the bridge asserts a
  // 4326 outline of at least a triangle BEFORE returning the canned 2263
  // correspondence, and the check asserts the ADOPTED 2263 vertices — a wrong or
  // missing request can never be papered over by the response.
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

  // BBL 1000010010 renders a real single-lot polygon; the CI browser has WebGL,
  // so the interactive map paints (the same premise architect-workspace.spec's
  // settledMap relies on).
  await openProposalEditor(page, "1000010010");
  await expect(page.getByRole("heading", { name: "Proposal editor" })).toBeVisible();
  await expect(page.getByTestId("outline-draw-honesty")).toContainText("not a city record");

  // The interactive lot map must render before it can be clicked. Scope to the
  // drawing wrapper so no other map surface is matched.
  const drawSurface = page.getByTestId("proposal-outline-map");
  await expect(drawSurface.getByTestId("lot-outline")).toHaveAttribute(
    "data-parcel-state",
    "rendered",
    { timeout: 15_000 },
  );
  const canvas = drawSurface.getByTestId("lot-outline-map").locator("canvas").first();
  await expect(canvas).toBeVisible();
  const box = await canvas.boundingBox();
  if (!box) throw new Error("the lot-outline map canvas has no layout box");

  // Place three WELL-SEPARATED points by real pointer clicks on empty parcel
  // area (never on a prior vertex circle), so the map runtime PLACES a new drawn
  // point each time — the pointer equivalent of the keyboard Add path.
  await canvas.click({ position: { x: box.width * 0.3, y: box.height * 0.32 } });
  await canvas.click({ position: { x: box.width * 0.72, y: box.height * 0.34 } });
  await canvas.click({ position: { x: box.width * 0.5, y: box.height * 0.72 } });

  // The clicks landed in the drawn-points table (shared state) and enabled
  // Convert at three points.
  await expect(page.getByLabel("Drawn point 0 longitude")).toBeVisible();
  await expect(page.getByLabel("Drawn point 2 longitude")).toBeVisible();
  await expect(page.getByTestId("outline-draw-convert")).toBeEnabled();

  // Convert the drawn outline -> bridge (stubbed) -> adopt into the numeric table.
  await page.getByTestId("outline-draw-convert").click();
  await expect(page.getByTestId("outline-draw-bridged")).toBeVisible();
  await expect(page.getByLabel("Vertex 0 X coordinate")).toHaveValue("1000020");
  await expect(page.getByLabel("Vertex 2 Y coordinate")).toHaveValue("200030");
  await expect(page.getByTestId("outline-draw-status")).toContainText("not a city record");

  // Run the check on the ADOPTED shape; the adopted 2263 vertices were asserted
  // inside the check stub before the canned report was served.
  await page.getByTestId("run-check").click();
  await expect(page.getByTestId("proposal-check-summary")).toBeVisible();
});

/** The fixed server disclosure the panel renders VERBATIM — the EXACT
 * ENVELOPE_DISCLOSURE text from the authoritative serialization
 * (services/api/app/scenario/max_envelope.py :100-108), reproduced char-for-char
 * so the stubbed response body is faithful to MaxEnvelope.as_dict() and the
 * panel's verbatim render is asserted exactly below (a paraphrase or truncation
 * fails). */
const ENVELOPE_DISCLOSURE =
  "This maximum-buildable envelope is a DETERMINISTIC, rules-derived ESTIMATE for the " +
  "rectangle-prism massing class - NOT a city record, a permit, an approval, or a legal " +
  "determination. Each dimension is the tightest applicable draft rule's allowance for this " +
  "lot (the looser rules are automatically satisfied and recorded as out-competed); where " +
  "more than one rule bounds a dimension, which rule governs is a legal determination " +
  "requiring professional review, surfaced here as an advisory rather than resolved. " +
  "Non-commensurable dimensions (residential FAR, rear yard) are disclosed as honest gaps. " +
  "Qualified professional review is required before any reliance.";

/** The Generated building option outline the stub returns — DELIBERATELY DISTINCT
 * from the editor's rectangle seed (5 vertices, vertex 0 X 1000000) so adoption
 * VISIBLY replaces the numeric authority (4 vertices, vertex 0 X 1000200). */
const OPTION_2263: Array<[number, number]> = [
  [1000200, 200500],
  [1000260, 200500],
  [1000260, 200540],
  [1000200, 200540],
];

/** A full MaxEnvelope.as_dict() body: one binding + one gap dimension (gap > 0,
 * so the aggregate stays visibly INCOMPLETE, D-083-R004) and a FITTED, contained
 * candidate (so one-action adoption is offered, D-083-R002/AS-4). Field shape
 * mirrors as_dict() exactly — never guessed (the max-envelope contract input). */
const MAX_ENVELOPE_BODY = {
  massing_class: "rectangle_prism",
  label: "BBL 1000010100 preliminary development limits",
  disclosure: ENVELOPE_DISCLOSURE,
  dimensions: [
    {
      dimension_id: "max_far_floor_area",
      family: "floor_area",
      required_output: "max_floor_area_sq_ft",
      direction: "max",
      unit: "sq_ft",
      label: "Maximum floor area",
      saturating: false,
      binding_value: 20000,
      binding_rule_id: "zr-far-r6",
      binding_rule_version: "2024.1",
      coverage_status: "covered",
      out_competed_rule_ids: ["zr-far-r6-alt"],
      rule_citations: [{ section: "23-142" }, { section: "23-145" }],
      gap_reason: null,
      conflict_advisory: null,
      detail: "The floor-area ratio ceiling for the underlying district.",
    },
    {
      dimension_id: "max_height_ft",
      family: "height",
      required_output: "max_height_ft",
      direction: "max",
      unit: "ft",
      label: "Maximum height",
      saturating: false,
      binding_value: null,
      binding_rule_id: null,
      binding_rule_version: null,
      coverage_status: "uncovered",
      out_competed_rule_ids: [],
      rule_citations: [],
      // [ORCH-CORRECTED per G3-F3/G4-F3] a REAL EnvelopeGapReason token, never prose.
      gap_reason: "allowance_unresolved",
      conflict_advisory: null,
      detail: "The height ceiling depends on a street width this lot has not resolved.",
    },
  ],
  candidate: {
    outline: { srid: 2263, vertices: OPTION_2263 },
    levels: [{ level_index: 0, floor_count: 4, floor_to_floor_ft: 10 }],
    exterior_walls: [
      { id: "W-S", start_vertex_index: 0, end_vertex_index: 1 },
      { id: "W-E", start_vertex_index: 1, end_vertex_index: 2 },
    ],
  },
  candidate_notes: ["Fitted to the recorded lot area; edit every value after adoption."],
  candidate_placement: {
    // ALL five CandidatePlacement fields, in the authoritative as_dict() shape
    // (services/api/app/scenario/max_envelope.py :340-347, :617-621, :891-895): a
    // FITTED placement carries the lot's bounding rectangle and the emitted
    // footprint, each an {anchor_x, anchor_y, width_ft, depth_ft, area_sq_ft}
    // record, and contained=true. Values are self-consistent EPSG:2263 feet.
    status: "fitted",
    detail: "The generated option was fitted inside the lot rectangle and proved contained.",
    lot_rectangle: { anchor_x: 1000200, anchor_y: 200500, width_ft: 300, depth_ft: 200, area_sq_ft: 60000 },
    footprint: { anchor_x: 1000200, anchor_y: 200500, width_ft: 60, depth_ft: 40, area_sq_ft: 2400 },
    contained: true,
  },
  candidate_consistency: { consistent: true },
  summary: { binding: 1, gap: 1, saturating_binding: 0, total: 2 },
  rule_input_bindings: {},
  unmapped_lot_facts: [],
  correlation_id: "e2e-envelope",
};

/** The parts of the serialized max-envelope request this journey asserts (mirrors
 * MaxEnvelopeRequest; typed locally so the spec needs no app import and no `any`). */
interface SerializedMaxEnvelope {
  lot: {
    area_sq_ft: number;
    area_provenance: { source_id: string };
    lot_line_segments: unknown[];
    street_lines: unknown[];
  };
  lot_rule_facts: Record<string, unknown>;
  label: string;
}

test("AS-5: the preliminary-development-limits panel leads from the lot context (no geometry sent) and adopts the option into the editor", async ({ page }) => {
  // Task M5-T070 (D-082-R003 + D-083). DB-050(g): the stub CAPTURES the request and
  // ALWAYS fulfills, then the FULL request contract is asserted EXPLICITLY below —
  // after the panel consumed the canned as_dict() envelope. A wrong or missing body
  // therefore fails with a precise assertion diff, NEVER a timeout-only failure (the
  // former assert-inside-the-handler pattern threw before fulfilling, hanging the page
  // until the panel wait timed out and masking the real contract mismatch). The route
  // stays UNMOUNTED in the app; this is the T065/T066 contract-proof precedent applied
  // to it, hardened so the failure mode is explicit.
  let capturedMethod: string | null = null;
  let capturedBody: SerializedMaxEnvelope | null = null;
  await page.route("**/api/v1/max-envelope", async (route) => {
    capturedMethod = route.request().method();
    capturedBody = route.request().postDataJSON() as SerializedMaxEnvelope;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { "X-Correlation-ID": "e2e-envelope" },
      body: JSON.stringify(MAX_ENVELOPE_BODY),
    });
  });

  await openProposalEditor(page, "1000010100");
  await expect(page.getByRole("heading", { name: "Proposal editor" })).toBeVisible();

  // The panel LEADS the surface (answer-first): the D-083 heading class and the
  // server disclosure render VERBATIM, before any designer input exists.
  const panel = page.getByTestId("max-envelope-panel");
  await expect(panel.getByRole("heading", { name: "Preliminary development limits" })).toBeVisible();
  await expect(page.getByTestId("envelope-disclosure")).toHaveText(ENVELOPE_DISCLOSURE);

  // The COMPLETE request contract, asserted EXPLICITLY now that the panel has consumed
  // the response. BBL 1000010100 is served through the REAL profile builder over the
  // committed official F01 fixture (services/api/tests/fixtures/pluto/
  // F01_single_lot_normal.json: lotarea "23121" -> 23121; single zonedist1 "R3-2"), so
  // the answer-first request carries that exact recorded lot AREA, the fixed provenance
  // source id, the single-district lot_rule_facts, the BBL label, and NO geometry
  // (display CRS is never measured; no client CRS math). toEqual is deep + strict, so it
  // also proves the ABSENCE of any unexpected field, at the top level and inside lot. A
  // mismatch fails HERE with an explicit diff, never a timeout (DB-050(g)).
  expect(capturedMethod, "the max-envelope must be POSTed").toBe("POST");
  expect(
    capturedBody,
    "the answer-first max-envelope request must match the recorded-lot contract exactly (no geometry, no client CRS math)",
  ).toEqual({
    lot: {
      area_sq_ft: 23121,
      area_provenance: { source_id: "architect_surface_lot_context" },
      lot_line_segments: [],
      street_lines: [],
    },
    lot_rule_facts: { zoning_district: "R3-2" },
    label: "BBL 1000010100 preliminary development limits",
  });

  // Explicit answer-first ORDERING: the limits panel precedes the proposal editor
  // in document order (not merely both present) — the computed limits lead the
  // surface, the editor follows.
  const panelLeadsEditor = await page.evaluate(() => {
    const panelEl = document.querySelector('[data-testid="max-envelope-panel"]');
    const editorEl = document.querySelector('[data-testid="proposal-editor"]');
    return Boolean(
      panelEl &&
        editorEl &&
        panelEl.compareDocumentPosition(editorEl) & Node.DOCUMENT_POSITION_FOLLOWING,
    );
  });
  expect(panelLeadsEditor, "the limits panel must render before the editor (answer-first)").toBe(true);

  // A binding dimension shows its value + binding rule; the gap dimension shows a
  // typed gap reason instead of a value; and with gap > 0 the aggregate stays
  // visibly INCOMPLETE — no unrestricted green/complete state (D-083-R004).
  await expect(page.getByTestId("envelope-value-max_far_floor_area")).toContainText("20000");
  await expect(page.getByTestId("envelope-binding-max_far_floor_area")).toContainText("zr-far-r6");
  await expect(page.getByTestId("envelope-gap-max_height_ft")).toContainText("Could not check");
  await expect(page.getByTestId("envelope-aggregate")).toHaveAttribute("data-complete", "false");

  // The editor below starts on the MANUAL rectangle seed (5 numeric vertices,
  // vertex 0 X 1000000): the panel is ADDITIVE and never replaces manual entry.
  await expect(page.getByLabel(/^Vertex \d+ X coordinate$/)).toHaveCount(5);
  await expect(page.getByLabel("Vertex 0 X coordinate")).toHaveValue("1000000");

  // ONE action adopts the Generated building option as the proposed starting
  // draft, seeding the numeric AUTHORITY exactly as if typed (4 vertices, vertex
  // 0 X 1000200); it is announced honestly as PROPOSED and manual entry stays.
  await page.getByTestId("adopt-candidate").click();
  await expect(page.getByLabel(/^Vertex \d+ X coordinate$/)).toHaveCount(4);
  await expect(page.getByLabel("Vertex 0 X coordinate")).toHaveValue("1000200");
  await expect(page.getByTestId("proposal-check-announcer")).toContainText("Adopted the Generated building option");
  await expect(page.getByRole("button", { name: "Add vertex", exact: true })).toBeVisible();
});
