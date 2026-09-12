/**
 * Test fixtures for the Compare (Step 3) component/unit tests ONLY (task
 * M5-T004). Nothing here is imported by application code — the app has no
 * mocked success path (acceptance scenario AS-7).
 *
 * Base documents: the COMMITTED M5-T003 scenario contract fixtures under
 * packages/contracts/fixtures/valid/scenario/ (read-only, the same
 * cross-package JSON-import precedent src/test-support/fixtures.ts uses for the
 * property-profile builder output). No official value is invented here.
 *
 * `notFoundResponse` is the generic flag-off 404 {"detail":"Not Found"} which
 * carries NO correlation id and NO state — exactly what an
 * INTERNAL_SCENARIO_ENABLED-off / unmounted endpoint returns.
 *
 * CONTENT-LENGTH. `fetchScenario` fails CLOSED on a response that does not
 * declare a readable body size, so every response built here stamps a
 * byte-accurate `Content-Length` — which is what the real endpoint does
 * (Starlette's JSONResponse sets it on every path) and what `new Response(...)`
 * does NOT do on its own. The shared `jsonResponse` in @/test-support/fixtures
 * omits the header and is out of this packet's scope (it is also consumed by
 * the property and confirm suites, whose clients have no size guard), so it is
 * SHADOWED here rather than modified: same signature, same X-Correlation-ID
 * default, plus the header. Tests that need a response WITHOUT the header
 * build it inline, deliberately.
 */

import preliminaryR5Cap from "../../../../../../packages/contracts/fixtures/valid/scenario/preliminary_r5_cap.json";
import noScenarioProfessionalReview from "../../../../../../packages/contracts/fixtures/valid/scenario/no_scenario_professional_review.json";
import noScenarioConflict from "../../../../../../packages/contracts/fixtures/valid/scenario/no_scenario_conflict.json";
import unsupportedFamily from "../../../../../../packages/contracts/fixtures/valid/scenario/unsupported_family.json";

/** Byte length of a UTF-8 payload — `String.length` is code units, not bytes,
 * and a fixture quote containing a non-ASCII character would under-declare. */
function byteLength(payload: string): string {
  return String(new TextEncoder().encode(payload).byteLength);
}

/**
 * A JSON response carrying Content-Type, a byte-accurate Content-Length, and an
 * X-Correlation-ID. Mirrors @/test-support/fixtures `jsonResponse` exactly,
 * apart from the length header.
 */
export function jsonResponse(
  body: unknown,
  status: number,
  correlationId = "test-correlation-id",
): Response {
  const payload = JSON.stringify(body);
  return new Response(payload, {
    status,
    headers: {
      "Content-Type": "application/json",
      "Content-Length": byteLength(payload),
      "X-Correlation-ID": correlationId,
    },
  });
}

/**
 * The BBL every committed scenario fixture states it was evaluated for
 * (`evaluated_input.bbl`). Tests render the Compare screen with THIS value so
 * the requested identity and the document's own identity agree.
 *
 * They did not agree before the M5-T004 rework: the suite rendered
 * `bbl="1000010100"` over fixtures all stating `1000477501`, and nothing
 * detected it, because the heading was authored from the URL prop and
 * `evaluated_input.bbl` was never read (DCV CRITICAL-2). The disagreement is
 * now asserted explicitly in its own test rather than shipped silently.
 */
export const FIXTURE_BBL = "1000477501";

/** The committed M5-T003 preliminary fixture (200 preliminary, cap 15000). */
export function preliminaryScenarioBody(): Record<string, unknown> {
  return structuredClone(preliminaryR5Cap) as unknown as Record<string, unknown>;
}

/** The committed M5-T003 professional-review fixture (no_scenario, share ranges). */
export function professionalReviewScenarioBody(): Record<string, unknown> {
  return structuredClone(noScenarioProfessionalReview) as unknown as Record<
    string,
    unknown
  >;
}

/** The committed M5-T003 data-conflict fixture (no_scenario). */
export function conflictScenarioBody(): Record<string, unknown> {
  return structuredClone(noScenarioConflict) as unknown as Record<string, unknown>;
}

/**
 * The committed M5-T003 unsupported-family fixture (scenario_kind
 * `unsupported`). It has been committed and UNUSED since M5-T003 — G4's
 * untested-branch 8 and DCV's additional coverage gap — so the `unsupported`
 * render path had never been exercised by anything.
 */
export function unsupportedScenarioBody(): Record<string, unknown> {
  return structuredClone(unsupportedFamily) as unknown as Record<string, unknown>;
}

// ---------------------------------------------------------------------------
// C1 unused-draft-zoning-floor-area (D-041 / M5-T018) LOCAL document variants.
//
// The four SHARED contract fixtures all carry the section in its `not_computable`
// / `missing_existing_building_area` (preliminary) or `no_draft_far_cap`
// (the three no-scenario/unsupported) state — they are M5-T017's files and are
// forbidden to edit here. The `computed` and `over_built` states have no shared
// fixture, so they are constructed LOCALLY, derived from the preliminary
// fixture's OWN draft cap (never an invented official value): the remainder is
// the fixture cap minus a test-chosen existing built floor area.
// ---------------------------------------------------------------------------

type UnusedSection = Record<string, unknown>;

/** A machine-readable ZR 12-10 zoning-lot-extent assumption, the same closed
 * record shape as a scenario assumption. */
function zoningLotExtentAssumption(): Record<string, unknown> {
  return {
    key: "zoning_lot_extent",
    assumption_type: "zoning_lot_extent",
    value: "tax_lot_is_zoning_lot",
    unit: null,
    rationale:
      "The selected tax lot is treated as the zoning lot (ZR 12-10) for this floor-area difference.",
  };
}

/**
 * A `computed` C1 document: the preliminary fixture with a constructed
 * `unused_draft_zoning_floor_area` whose value is the fixture's own draft cap
 * (15,000) minus `existingSqFt`. With the default 10,000 the remainder is a
 * positive 5,000; pass a larger existing area for `over_built`.
 */
export function computedUnusedFloorAreaBody(
  existingSqFt = 10000,
): Record<string, unknown> {
  const body = preliminaryScenarioBody();
  const base = body.unused_draft_zoning_floor_area as UnusedSection;
  const capInput = (base.inputs as Record<string, UnusedSection>)
    .draft_zoning_floor_area_cap;
  const cap = capInput.value_sq_ft as number; // 15,000, from the fixture
  const value = cap - existingSqFt; // DERIVED from the fixture cap, never retyped
  body.unused_draft_zoning_floor_area = {
    ...base,
    state: "computed",
    unused_draft_zoning_floor_area_sq_ft: value,
    unit: "square_feet",
    formula:
      "unused = draft_zoning_floor_area_cap_sq_ft - existing_building_floor_area_sq_ft",
    professional_review_required: false,
    over_built_statement: null,
    not_computable_reason: null,
    inputs: {
      draft_zoning_floor_area_cap: capInput,
      existing_building_floor_area: {
        value_sq_ft: existingSqFt,
        unit: "square_feet",
        coverage_status: "conditional",
        provenance_ref: "prov-bldgarea",
        provenance: {
          provenance_id: "prov-bldgarea",
          source_id: "nyc-dcp-pluto",
          original_field_name: "bldgarea",
        },
      },
    },
    assumptions: [zoningLotExtentAssumption()],
  };
  return body;
}

/**
 * An `over_built` C1 document: the existing built floor area (default 20,000)
 * exceeds the fixture cap (15,000), so the remainder is a NEGATIVE 5,000. The
 * section carries an explicit `over_built_statement` and forces
 * professional-review at the section AND (per the schema OR) the document root.
 */
export function overBuiltUnusedFloorAreaBody(
  existingSqFt = 20000,
): Record<string, unknown> {
  const body = computedUnusedFloorAreaBody(existingSqFt);
  const base = body.unused_draft_zoning_floor_area as UnusedSection;
  body.unused_draft_zoning_floor_area = {
    ...base,
    state: "over_built",
    professional_review_required: true,
    over_built_statement:
      "The existing built floor area exceeds the draft residential zoning floor-area cap; the remainder is negative.",
  };
  // Schema: the document-root professional_review_required is the OR of the
  // section flag and the rule-evaluation fail-safe trigger.
  body.professional_review_required = true;
  return body;
}

/**
 * A `not_computable` C1 document carrying the given typed reason. The
 * preliminary fixture already ships `missing_existing_building_area`; this
 * constructs the other reasons (notably `existing_building_area_unusable`, which
 * no shared fixture carries) from the same base.
 */
export function notComputableUnusedFloorAreaBody(
  reason:
    | "missing_existing_building_area"
    | "existing_building_area_unusable"
    | "no_draft_far_cap",
): Record<string, unknown> {
  const body = preliminaryScenarioBody();
  const base = body.unused_draft_zoning_floor_area as UnusedSection;
  body.unused_draft_zoning_floor_area = {
    ...base,
    state: "not_computable",
    unused_draft_zoning_floor_area_sq_ft: null,
    unit: null,
    formula: null,
    professional_review_required: false,
    over_built_statement: null,
    not_computable_reason: reason,
    assumptions: [],
  };
  return body;
}

/** A fetch stub that always resolves to `response` (offline; no network). */
export function stubFetch(response: Response): typeof fetch {
  return (async () => response.clone()) as unknown as typeof fetch;
}

/**
 * The generic flag-off / unmounted 404: body {"detail":"Not Found"}, NO
 * X-Correlation-ID header, NO machine-readable `state`. Maps to the benign
 * `feature_unavailable` outcome.
 */
export function notFoundResponse(): Response {
  const payload = JSON.stringify({ detail: "Not Found" });
  return new Response(payload, {
    status: 404,
    headers: {
      "Content-Type": "application/json",
      "Content-Length": byteLength(payload),
    },
  });
}

/**
 * A response whose `Content-Length` is absent, blank, or malformed — the
 * framing an actor controlling the response would choose to slip past a size
 * guard that only rejected an over-budget header. `fetchScenario` must reject
 * every one of these before parsing.
 */
export function unmeasuredResponse(
  contentLength: string | null,
  body: unknown = { state: "internal_error" },
  status = 500,
): Response {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (contentLength !== null) {
    headers["Content-Length"] = contentLength;
  }
  return new Response(JSON.stringify(body), { status, headers });
}

/** A documented (status, state) envelope response WITH a correlation id. */
export function stateResponse(
  status: number,
  state: string,
  extra: Record<string, unknown> = {},
  correlationId = "test-correlation-id",
): Response {
  return jsonResponse({ state, ...extra }, status, correlationId);
}
