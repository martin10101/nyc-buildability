import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  announcementForRuleEvaluation,
  classifyRuleEvaluation,
  fetchRuleEvaluation,
  isDocumentedRulePair,
  ruleEvaluationFlagEnabled,
  ruleEvaluationSurfaceEnabled,
} from "@/lib/rule-evaluation";
import { validateRuleEvaluationDocument } from "@/lib/rule-evaluation-contract";
import { jsonResponse } from "@/test-support/fixtures";
import {
  draftApplicableDoc,
  missingEvidenceDoc,
  ruleConflictDoc,
  spatialUncertaintyDoc,
  unsupportedDoc,
} from "@/test-support/rule-evaluation-fixtures";

/**
 * Task M4-T005 phase 3, client layer:
 *   - exact (HTTP status, state) pair enforcement mirroring rule_evaluation.py,
 *   - runtime canonical validation of every 200 before it can render,
 *   - the two-factor frontend flag (env + per-request opt-in) and the
 *     defense-in-depth no-fetch guarantee,
 *   - deterministic presentation classification from server discriminators.
 */

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
    expect(ruleEvaluationFlagEnabled(token)).toBe(expected);
  });

  it("is disabled when the env var is absent", () => {
    expect(ruleEvaluationFlagEnabled(undefined)).toBe(false);
  });
});

describe("frontend flag — surface gate (env AND opt-in)", () => {
  const KEY = "INTERNAL_RULE_EVAL_UI";
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
    expect(ruleEvaluationSurfaceEnabled()).toBe(false);
    expect(ruleEvaluationSurfaceEnabled({ ruleeval: "on" })).toBe(false);
  });

  it("is OFF with the env on but no opt-in", () => {
    process.env[KEY] = "1";
    expect(ruleEvaluationSurfaceEnabled()).toBe(false);
    expect(ruleEvaluationSurfaceEnabled({ ruleeval: "off" })).toBe(false);
  });

  it("is ON only with the env on AND an explicit opt-in", () => {
    process.env[KEY] = "1";
    expect(ruleEvaluationSurfaceEnabled({ ruleeval: "on" })).toBe(true);
    expect(ruleEvaluationSurfaceEnabled({ ruleeval: ["on"] })).toBe(true);
  });
});

// --------------------------------------------------------------------------
// Exact (status, state) pair matrix.
// --------------------------------------------------------------------------

describe("documented rule-eval (status, state) pairs", () => {
  it("accepts the documented pairs, including BOTH 404 meanings", () => {
    expect(isDocumentedRulePair(200, null)).toBe(true);
    expect(isDocumentedRulePair(404, null)).toBe(true); // feature unavailable
    expect(isDocumentedRulePair(404, "no_match")).toBe(true); // result
    expect(isDocumentedRulePair(500, "internal_contract_error")).toBe(true);
  });

  it("rejects an undocumented pair (500 + no_match) structurally", () => {
    expect(isDocumentedRulePair(500, "no_match")).toBe(false);
    expect(isDocumentedRulePair(200, "no_match")).toBe(false);
  });
});

// --------------------------------------------------------------------------
// fetchRuleEvaluation — each documented envelope maps to the right outcome.
// --------------------------------------------------------------------------

describe("fetchRuleEvaluation — envelope classification", () => {
  it("classifies a valid 200 rule_evaluation document", async () => {
    const outcome = await fetchRuleEvaluation(
      "1000010100",
      stub(jsonResponse(draftApplicableDoc(), 200, "corr-1")),
    );
    expect(outcome.kind).toBe("evaluation");
    if (outcome.kind === "evaluation") {
      expect(outcome.document.coverage_status).toBe("conditional");
      expect(outcome.correlationId).toBe("corr-1");
    }
  });

  it("rejects a 200 whose coverage_status is verified as validation_failure", async () => {
    const bad = draftApplicableDoc();
    // A draft result may never be Verified; the client validator must refuse it.
    (bad as unknown as { coverage_status: string }).coverage_status = "verified";
    const outcome = await fetchRuleEvaluation("1000010100", stub(jsonResponse(bad, 200)));
    expect(outcome.kind).toBe("validation_failure");
    if (outcome.kind === "validation_failure") {
      expect(outcome.problems.length).toBeGreaterThan(0);
    }
  });

  it("maps the generic 404 {detail:'Not Found'} to feature_unavailable", async () => {
    const outcome = await fetchRuleEvaluation(
      "1000010100",
      stub(jsonResponse({ detail: "Not Found" }, 404)),
    );
    expect(outcome.kind).toBe("feature_unavailable");
  });

  it("maps 404 state=no_match to a no_match outcome", async () => {
    const body = { state: "no_match", bbl: "5999999999", message: "no record", correlation_id: "c" };
    const outcome = await fetchRuleEvaluation("5999999999", stub(jsonResponse(body, 404)));
    expect(outcome.kind).toBe("no_match");
  });

  it("maps 422 validation_error with detail.code", async () => {
    const body = {
      state: "validation_error",
      message: "bad bbl",
      detail: { code: "non_numeric", raw_value: "'abc'" },
    };
    const outcome = await fetchRuleEvaluation("abc", stub(jsonResponse(body, 422)));
    expect(outcome.kind).toBe("validation_error");
    if (outcome.kind === "validation_error") expect(outcome.code).toBe("non_numeric");
  });

  it.each([
    ["rate_limited", 503],
    ["source_unavailable", 503],
    ["timeout", 504],
    ["schema_drift", 502],
  ])("maps upstream state=%s (HTTP %s) to upstream_failure", async (state, status) => {
    const outcome = await fetchRuleEvaluation(
      "1000010100",
      stub(jsonResponse({ state, message: "upstream" }, status)),
    );
    expect(outcome.kind).toBe("upstream_failure");
    if (outcome.kind === "upstream_failure") expect(outcome.state).toBe(state);
  });

  it("maps 500 internal_error to internal_error", async () => {
    const outcome = await fetchRuleEvaluation(
      "1000010100",
      stub(jsonResponse({ state: "internal_error", message: "boom" }, 500)),
    );
    expect(outcome.kind).toBe("internal_error");
  });

  it("maps 500 internal_contract_error to server_contract_error", async () => {
    const outcome = await fetchRuleEvaluation(
      "1000010100",
      stub(jsonResponse({ state: "internal_contract_error", message: "refused" }, 500)),
    );
    expect(outcome.kind).toBe("server_contract_error");
  });

  it("treats an undocumented (500, no_match) pair as unexpected_response", async () => {
    const outcome = await fetchRuleEvaluation(
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
    const outcome = await fetchRuleEvaluation("1000010100", {
      fetchImpl: (async () => {
        throw new TypeError("connection refused");
      }) as typeof fetch,
    });
    expect(outcome.kind).toBe("network_error");
  });

  it("resolves an externally-aborted request to aborted (dropped by the caller)", async () => {
    const controller = new AbortController();
    controller.abort();
    const outcome = await fetchRuleEvaluation("1000010100", {
      signal: controller.signal,
      fetchImpl: (async () => jsonResponse(draftApplicableDoc(), 200)) as typeof fetch,
    });
    expect(outcome.kind).toBe("aborted");
  });
});

// --------------------------------------------------------------------------
// Presentation classifier — server discriminators only.
// --------------------------------------------------------------------------

describe("classifyRuleEvaluation", () => {
  it("routes an applicable draft to applicable_draft", () => {
    expect(classifyRuleEvaluation(draftApplicableDoc())).toBe("applicable_draft");
  });
  it("routes not_applicable / unsupported to unsupported", () => {
    expect(classifyRuleEvaluation(unsupportedDoc())).toBe("unsupported");
  });
  it("routes an absent-substrate fail-safe to missing_evidence", () => {
    expect(classifyRuleEvaluation(missingEvidenceDoc())).toBe("missing_evidence");
  });
  it("routes a split-lot geometry_uncertain result to spatial_uncertainty", () => {
    expect(classifyRuleEvaluation(spatialUncertaintyDoc())).toBe("spatial_uncertainty");
  });
  it("routes a typed rule conflict to rule_conflict (highest priority)", () => {
    expect(classifyRuleEvaluation(ruleConflictDoc())).toBe("rule_conflict");
  });
});

describe("runtime validation accepts every committed shape", () => {
  it.each<[string, () => import("@/lib/rule-evaluation-contract").RuleEvaluation]>([
    ["applicable draft", draftApplicableDoc],
    ["unsupported", unsupportedDoc],
    ["missing evidence", missingEvidenceDoc],
    ["spatial uncertainty", spatialUncertaintyDoc],
    ["rule conflict", ruleConflictDoc],
  ])("validates the %s document", (label, factory) => {
    const result = validateRuleEvaluationDocument(factory());
    expect(result.ok, label).toBe(true);
  });
});

describe("announcementForRuleEvaluation", () => {
  it("never presents verified/best wording and announces nothing for aborted", () => {
    for (const factory of [
      draftApplicableDoc,
      spatialUncertaintyDoc,
      ruleConflictDoc,
      missingEvidenceDoc,
      unsupportedDoc,
    ]) {
      const message = announcementForRuleEvaluation({
        kind: "evaluation",
        document: factory(),
        correlationId: null,
      });
      expect(message).not.toMatch(/\bverified\b/i);
      expect(message).not.toMatch(/\bbest\b/i);
      expect(message.length).toBeGreaterThan(0);
    }
    expect(announcementForRuleEvaluation({ kind: "aborted" })).toBe("");
  });
});
