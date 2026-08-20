import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  announcementForScenario,
  classifyScenario,
  fetchScenario,
  isDocumentedScenarioPair,
  scenarioFlagEnabled,
  scenarioSurfaceEnabled,
} from "@/lib/scenario";
import { validateScenarioDocument, type Scenario } from "@/lib/scenario-contract";
import { jsonResponse } from "@/test-support/fixtures";
import preliminaryFixture from "../../../../../packages/contracts/fixtures/valid/scenario/preliminary_r5_cap.json";
import unsupportedFixture from "../../../../../packages/contracts/fixtures/valid/scenario/unsupported_family.json";
import conflictFixture from "../../../../../packages/contracts/fixtures/valid/scenario/no_scenario_conflict.json";
import professionalReviewFixture from "../../../../../packages/contracts/fixtures/valid/scenario/no_scenario_professional_review.json";

/**
 * Task M5-T002, client layer:
 *   - exact (HTTP status, state) pair enforcement mirroring scenario.py,
 *   - runtime canonical validation of every 200 before it can render,
 *   - the two-factor frontend flag (env + per-request opt-in) and the
 *     defense-in-depth no-fetch guarantee,
 *   - deterministic presentation classification from server discriminators.
 *
 * The scenario documents are the COMMITTED canonical contract fixtures from
 * packages/contracts/fixtures/valid/scenario/ (accepted in M5-T001). No body is
 * hand-written; the only synthesized case is the `missing` presentation (there
 * is no committed missing-input fixture), derived from the preliminary fixture.
 */

function clone(doc: unknown): Scenario {
  return structuredClone(doc) as unknown as Scenario;
}

const preliminaryDoc = () => clone(preliminaryFixture);
const unsupportedDoc = () => clone(unsupportedFixture);
const conflictDoc = () => clone(conflictFixture);
const professionalReviewDoc = () => clone(professionalReviewFixture);

function missingDoc(): Scenario {
  const doc = preliminaryDoc();
  doc.scenario_kind = "no_scenario";
  doc.coverage_status = "conditional";
  doc.professional_review_required = false;
  doc.draft_zoning_floor_area_cap_sq_ft = null;
  doc.cap_label = null;
  doc.cap_provenance = null;
  return doc;
}

function stub(response: Response) {
  return { fetchImpl: (async () => response) as typeof fetch };
}

// --------------------------------------------------------------------------
// Frontend feature flag: env gate + per-request opt-in (both required).
// --------------------------------------------------------------------------

describe("frontend flag — env gate", () => {
  it.each([
    ["1", true],
    ["true", true],
    ["on", true],
    ["YES", true],
    ["0", false],
    ["off", false],
    ["", false],
    ["maybe", false],
  ])("token %s -> %s", (token, expected) => {
    expect(scenarioFlagEnabled(token)).toBe(expected);
  });

  it("is disabled when the env var is absent", () => {
    expect(scenarioFlagEnabled(undefined)).toBe(false);
  });
});

describe("frontend flag — surface gate (env AND opt-in)", () => {
  const KEY = "INTERNAL_SCENARIO_UI";
  let saved: string | undefined;
  beforeEach(() => {
    saved = process.env[KEY];
  });
  afterEach(() => {
    if (saved === undefined) delete process.env[KEY];
    else process.env[KEY] = saved;
  });

  it("is OFF by default (no env, no opt-in) — the no-fetch guarantee", () => {
    delete process.env[KEY];
    expect(scenarioSurfaceEnabled()).toBe(false);
    expect(scenarioSurfaceEnabled({ scenario: "on" })).toBe(false);
  });

  it("is OFF with the env on but no opt-in", () => {
    process.env[KEY] = "1";
    expect(scenarioSurfaceEnabled()).toBe(false);
    expect(scenarioSurfaceEnabled({ scenario: "off" })).toBe(false);
  });

  it("is ON only with the env on AND an explicit opt-in", () => {
    process.env[KEY] = "1";
    expect(scenarioSurfaceEnabled({ scenario: "on" })).toBe(true);
    expect(scenarioSurfaceEnabled({ scenario: ["on"] })).toBe(true);
  });
});

// --------------------------------------------------------------------------
// Exact (status, state) pair matrix.
// --------------------------------------------------------------------------

describe("documented scenario (status, state) pairs", () => {
  it("accepts the documented pairs, including BOTH 404 meanings", () => {
    expect(isDocumentedScenarioPair(200, null)).toBe(true);
    expect(isDocumentedScenarioPair(404, null)).toBe(true); // feature unavailable
    expect(isDocumentedScenarioPair(404, "no_match")).toBe(true); // result
    expect(isDocumentedScenarioPair(500, "internal_contract_error")).toBe(true);
  });

  it("rejects an undocumented pair structurally", () => {
    expect(isDocumentedScenarioPair(500, "no_match")).toBe(false);
    expect(isDocumentedScenarioPair(200, "no_match")).toBe(false);
  });
});

// --------------------------------------------------------------------------
// fetchScenario — each documented envelope maps to the right outcome.
// --------------------------------------------------------------------------

describe("fetchScenario — envelope classification", () => {
  it("classifies a valid 200 preliminary scenario and surfaces the cap verbatim", async () => {
    const outcome = await fetchScenario(
      "1000010100",
      stub(jsonResponse(preliminaryDoc(), 200, "corr-1")),
    );
    expect(outcome.kind).toBe("scenario");
    if (outcome.kind === "scenario") {
      expect(outcome.document.coverage_status).toBe("conditional");
      // Cap surfaced verbatim from the committed fixture — never recomputed.
      expect(outcome.document.draft_zoning_floor_area_cap_sq_ft).toBe(
        (preliminaryFixture as { draft_zoning_floor_area_cap_sq_ft: number })
          .draft_zoning_floor_area_cap_sq_ft,
      );
      expect(outcome.correlationId).toBe("corr-1");
    }
  });

  it("rejects a 200 whose coverage_status is verified as validation_failure", async () => {
    const bad = preliminaryDoc();
    (bad as unknown as { coverage_status: string }).coverage_status = "verified";
    const outcome = await fetchScenario("1000010100", stub(jsonResponse(bad, 200)));
    expect(outcome.kind).toBe("validation_failure");
    if (outcome.kind === "validation_failure") {
      expect(outcome.problems.length).toBeGreaterThan(0);
    }
  });

  it("maps the generic 404 {detail:'Not Found'} to feature_unavailable", async () => {
    const outcome = await fetchScenario(
      "1000010100",
      stub(jsonResponse({ detail: "Not Found" }, 404)),
    );
    expect(outcome.kind).toBe("feature_unavailable");
  });

  it("maps 404 state=no_match to a no_match outcome", async () => {
    const body = { state: "no_match", bbl: "5999999999", message: "no record", correlation_id: "c" };
    const outcome = await fetchScenario("5999999999", stub(jsonResponse(body, 404)));
    expect(outcome.kind).toBe("no_match");
  });

  it("maps 422 validation_error with detail.code", async () => {
    const body = {
      state: "validation_error",
      message: "bad bbl",
      detail: { code: "non_numeric", raw_value: "'abc'" },
    };
    const outcome = await fetchScenario("abc", stub(jsonResponse(body, 422)));
    expect(outcome.kind).toBe("validation_error");
    if (outcome.kind === "validation_error") expect(outcome.code).toBe("non_numeric");
  });

  it.each([
    ["rate_limited", 503],
    ["source_unavailable", 503],
    ["timeout", 504],
    ["schema_drift", 502],
  ])("maps upstream state=%s (HTTP %s) to upstream_failure", async (state, status) => {
    const outcome = await fetchScenario(
      "1000010100",
      stub(jsonResponse({ state, message: "upstream" }, status)),
    );
    expect(outcome.kind).toBe("upstream_failure");
    if (outcome.kind === "upstream_failure") expect(outcome.state).toBe(state);
  });

  it("maps 500 internal_error to internal_error", async () => {
    const outcome = await fetchScenario(
      "1000010100",
      stub(jsonResponse({ state: "internal_error", message: "boom" }, 500)),
    );
    expect(outcome.kind).toBe("internal_error");
  });

  it("maps 500 internal_contract_error to server_contract_error", async () => {
    const outcome = await fetchScenario(
      "1000010100",
      stub(jsonResponse({ state: "internal_contract_error", message: "refused" }, 500)),
    );
    expect(outcome.kind).toBe("server_contract_error");
  });

  it("treats an undocumented (500, no_match) pair as unexpected_response", async () => {
    const outcome = await fetchScenario(
      "1000010100",
      stub(jsonResponse({ state: "no_match", message: "incoherent" }, 500)),
    );
    expect(outcome.kind).toBe("unexpected_response");
    if (outcome.kind === "unexpected_response") {
      expect(outcome.httpStatus).toBe(500);
      expect(outcome.receivedState).toBe("no_match");
    }
  });

  it("classifies a browser-level failure as network_error", async () => {
    const outcome = await fetchScenario("1000010100", {
      fetchImpl: (async () => {
        throw new TypeError("connection refused");
      }) as typeof fetch,
    });
    expect(outcome.kind).toBe("network_error");
  });

  it("resolves an externally-aborted request to aborted (dropped by the caller)", async () => {
    const controller = new AbortController();
    controller.abort();
    const outcome = await fetchScenario("1000010100", {
      signal: controller.signal,
      fetchImpl: (async () => jsonResponse(preliminaryDoc(), 200)) as typeof fetch,
    });
    expect(outcome.kind).toBe("aborted");
  });
});

// --------------------------------------------------------------------------
// Presentation classifier — server discriminators only.
// --------------------------------------------------------------------------

describe("classifyScenario", () => {
  it("routes a preliminary scenario to preliminary_cap", () => {
    expect(classifyScenario(preliminaryDoc())).toBe("preliminary_cap");
  });
  it("routes an unsupported family to unsupported", () => {
    expect(classifyScenario(unsupportedDoc())).toBe("unsupported");
  });
  it("routes a data conflict to conflict", () => {
    expect(classifyScenario(conflictDoc())).toBe("conflict");
  });
  it("routes a professional-review no_scenario to professional_review", () => {
    expect(classifyScenario(professionalReviewDoc())).toBe("professional_review");
  });
  it("routes a missing-input no_scenario to missing", () => {
    expect(classifyScenario(missingDoc())).toBe("missing");
  });
});

describe("runtime validation accepts every committed shape and rejects verified", () => {
  it.each<[string, () => Scenario]>([
    ["preliminary", preliminaryDoc],
    ["unsupported", unsupportedDoc],
    ["conflict", conflictDoc],
    ["professional review", professionalReviewDoc],
  ])("validates the %s document", (label, factory) => {
    const result = validateScenarioDocument(factory());
    expect(result.ok, label).toBe(true);
  });

  it("rejects a verified coverage_status (a scenario is never Verified)", () => {
    const bad = preliminaryDoc();
    (bad as unknown as { coverage_status: string }).coverage_status = "verified";
    expect(validateScenarioDocument(bad).ok).toBe(false);
  });
});

describe("announcementForScenario", () => {
  it("never presents verified/best wording and announces nothing for aborted", () => {
    for (const factory of [
      preliminaryDoc,
      unsupportedDoc,
      conflictDoc,
      professionalReviewDoc,
      missingDoc,
    ]) {
      const message = announcementForScenario({
        kind: "scenario",
        document: factory(),
        correlationId: null,
      });
      expect(message).not.toMatch(/\bverified\b/i);
      expect(message).not.toMatch(/\bbest\b/i);
      expect(message.length).toBeGreaterThan(0);
    }
    expect(announcementForScenario({ kind: "aborted" })).toBe("");
  });
});
