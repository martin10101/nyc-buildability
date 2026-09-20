/**
 * Proposal-check response fixtures (task M5-T060). The 200 bodies mirror the
 * accepted route/engine `ProposalCheckReport.as_dict` shape and the HAND-COMPUTED
 * M5-T054 rectangle case (services/api/tests/rules/fixtures/proposal_checks/
 * rectangle_case.json — coverage FAIL 0.625 vs 0.5 shortfall 0.125; height PASS
 * 30 <= 60; two structurally non-commensurable checks COULD_NOT_CHECK). These are
 * transcribed by hand from the accepted fixture, never produced by running the
 * client — they exist to prove the CLIENT decode + render, not the engine.
 *
 * `checkResponse` sets an explicit Content-Length so the client's fail-closed
 * "bound before parse" branch (a plain digit Content-Length within
 * MAX_RESPONSE_BYTES) is exercised deterministically in every environment.
 */

type Json = Record<string, unknown>;

function provenance(overrides: Json = {}): Json {
  return {
    scenario_label: "scenario-A-baseline",
    proposal_id: "prop-0001",
    source_class: "proposed",
    provided_input_ids: [],
    provided_provenance: null,
    rule_id: null,
    rule_version: null,
    rule_status: null,
    coverage_status: null,
    rule_citations: [],
    ...overrides,
  };
}

const REAR_YARD_GAP =
  "the proposal's minimum wall-to-lot-line setback is not a rear-yard depth: no rear lot line is " +
  "designated in the derivation, so the generic minimum setback across all walls cannot establish " +
  "the rear yard the rule governs";
const RESIDENTIAL_FAR_GAP =
  "the proposal's derived gross floor area is a pure geometric gross and is not a residential zoning " +
  "floor area; the matching square-foot unit is not equivalence";

const FACT_MAPPING: Json[] = [
  { check_id: "lot_coverage_ratio", semantic_gap: null },
  { check_id: "building_height", semantic_gap: null },
  { check_id: "rear_yard_depth", semantic_gap: REAR_YARD_GAP },
  { check_id: "residential_far_floor_area", semantic_gap: RESIDENTIAL_FAR_GAP },
];

function coverageFail(): Json {
  return {
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
    detail: "proposed lot coverage ratio 0.625 ratio vs maximum allowance 0.5 ratio (max_lot_coverage_ratio)",
    provenance: provenance({ rule_id: "pc-lot-coverage-demo", coverage_status: "conditional" }),
  };
}
function rearYardCnc(): Json {
  return {
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
    detail: REAR_YARD_GAP,
    provenance: provenance(),
  };
}
function residentialFarCnc(): Json {
  return {
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
    detail: RESIDENTIAL_FAR_GAP,
    provenance: provenance(),
  };
}

/** The ATTESTED rectangle report: coverage FAIL, height PASS (30 <= 60), two
 * COULD_NOT_CHECK. summary {pass:1, fail:1, could_not_check:2, total:4}. */
export function attestedReportBody(overrides: Json = {}): Json {
  return {
    scenario_label: "scenario-A-baseline",
    proposal_id: "prop-0001",
    source_class: "proposed",
    outline_digest: "sha256:0000000000000000000000000000000000000000000000000000000000000000",
    results: [
      coverageFail(),
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
        detail: "proposed cumulative building height 30 feet vs maximum allowance 60 feet (max_building_height)",
        provenance: provenance({ rule_id: "pc-height-demo", coverage_status: "conditional" }),
      },
      rearYardCnc(),
      residentialFarCnc(),
    ],
    summary: { pass: 1, fail: 1, could_not_check: 2, total: 4 },
    fact_mapping: FACT_MAPPING,
    rule_input_bindings: { lot_area_sq_ft: "lot_context.area_sq_ft", zoning_district: "caller_lot_fact:zoning_district" },
    unmapped_lot_facts: [],
    correlation_id: "test-correlation-id",
    ...overrides,
  };
}

/** The UNATTESTED rectangle report: the height allowance is unresolved (no
 * attested street width), so building_height is COULD_NOT_CHECK. summary
 * {pass:0, fail:1, could_not_check:3, total:4}. */
export function unattestedReportBody(overrides: Json = {}): Json {
  return {
    ...attestedReportBody(),
    results: [
      coverageFail(),
      {
        check_id: "building_height",
        family: "residential_height_setback",
        label: "proposed cumulative building height",
        unit: "feet",
        direction: "maximum",
        outcome: "could_not_check",
        provided_value: 30.0,
        required_value: null,
        shortfall: null,
        could_not_check_reason: "allowance_unresolved",
        detail: "an applicable rule produced no usable allowance (a required input is missing); the allowance is unresolved",
        provenance: provenance({ rule_id: "pc-height-demo", coverage_status: "professional_review_required" }),
      },
      rearYardCnc(),
      residentialFarCnc(),
    ],
    summary: { pass: 0, fail: 1, could_not_check: 3, total: 4 },
    ...overrides,
  };
}

/** A report whose echoed ids/keys carry markup — proves the client bounds them
 * and the renderer shows them as TEXT (DB-039(k)); no raw-HTML injection sink. */
export function markupEchoReportBody(): Json {
  const body = attestedReportBody({
    scenario_label: "proposal <script>alert(1)</script>",
    unmapped_lot_facts: ["<img src=x onerror=alert(1)>"],
  });
  const results = body.results as Json[];
  (results[0].provenance as Json).provided_input_ids = ["<b>W-S</b>"];
  return body;
}

/** Build a Response with an explicit Content-Length so the client's
 * bound-before-parse branch is exercised deterministically. */
export function checkResponse(body: unknown, status: number, correlationId: string | null = "test-correlation-id"): Response {
  const text = JSON.stringify(body);
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "Content-Length": String(new TextEncoder().encode(text).length),
  };
  if (correlationId !== null) headers["X-Correlation-ID"] = correlationId;
  return new Response(text, { status, headers });
}

/** A fetchImpl stub that always resolves to `response`. */
export function stubFetch(response: Response): typeof fetch {
  return (async () => response) as typeof fetch;
}
