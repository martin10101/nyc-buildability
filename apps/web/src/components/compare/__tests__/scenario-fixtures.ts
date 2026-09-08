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
 * `jsonResponse` is reused from the shared test-support module (it stamps an
 * X-Correlation-ID). `notFoundResponse` is added here for the generic flag-off
 * 404 {"detail":"Not Found"} which carries NO correlation id and NO state —
 * exactly what an INTERNAL_SCENARIO_ENABLED-off / unmounted endpoint returns.
 */

import { jsonResponse } from "@/test-support/fixtures";
import preliminaryR5Cap from "../../../../../../packages/contracts/fixtures/valid/scenario/preliminary_r5_cap.json";
import noScenarioProfessionalReview from "../../../../../../packages/contracts/fixtures/valid/scenario/no_scenario_professional_review.json";
import noScenarioConflict from "../../../../../../packages/contracts/fixtures/valid/scenario/no_scenario_conflict.json";

export { jsonResponse };

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
  return new Response(JSON.stringify({ detail: "Not Found" }), {
    status: 404,
    headers: { "Content-Type": "application/json" },
  });
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
