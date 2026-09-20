import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  announcementForRuleEvaluation,
  classifyRuleEvaluation,
  fetchRuleEvaluation,
  INTERNAL_RULE_EVAL_DEFAULT_ON_ENV_VAR,
  isDocumentedRulePair,
  ruleEvaluationDefaultOnEnabled,
  ruleEvaluationFlagEnabled,
  ruleEvaluationSurfaceEnabled,
} from "@/lib/rule-evaluation";
import { validateRuleEvaluationDocument } from "@/lib/rule-evaluation-contract";
import { jsonResponse } from "@/test-support/fixtures";
import {
  condoUnresolvedDoc,
  draftApplicableDoc,
  missingEvidenceDoc,
  ruleConflictDoc,
  spatialUncertaintyDoc,
  SUBSTITUTION_ANALYZED_BBL,
  SUBSTITUTION_ENTERED_BBL,
  substitutionStampDoc,
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

// D-057 isolation safety net: guarantee INTERNAL_RULE_EVAL_DEFAULT_ON never
// leaks between tests in this file, regardless of which describe block below
// sets it. This runs around EVERY test (including the pre-D-057 tests above,
// which never touch the var themselves) so they always see it absent — the
// exact byte-for-byte precondition D-057-R002 requires.
let savedDefaultOnAtModuleScope: string | undefined;
beforeEach(() => {
  savedDefaultOnAtModuleScope = process.env[INTERNAL_RULE_EVAL_DEFAULT_ON_ENV_VAR];
  delete process.env[INTERNAL_RULE_EVAL_DEFAULT_ON_ENV_VAR];
});
afterEach(() => {
  if (savedDefaultOnAtModuleScope === undefined) {
    delete process.env[INTERNAL_RULE_EVAL_DEFAULT_ON_ENV_VAR];
  } else {
    process.env[INTERNAL_RULE_EVAL_DEFAULT_ON_ENV_VAR] = savedDefaultOnAtModuleScope;
  }
});

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
  const KEY = "INTERNAL_RULE_EVAL_ENABLED";
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

  // M5-T019 / D-040-R002: the flag name is now the canonical backend-unified
  // INTERNAL_RULE_EVAL_ENABLED. Setting the retired split name
  // INTERNAL_RULE_EVAL_UI must NOT enable the flag — the M5-T015 G5 F-1
  // misconfiguration (env set under the old name) is now inert on the web side.
  it("ignores the retired split name INTERNAL_RULE_EVAL_UI (F-1 now inert)", () => {
    const OLD = "INTERNAL_RULE_EVAL_UI";
    const savedOld = process.env[OLD];
    delete process.env[KEY]; // canonical name absent
    process.env[OLD] = "1"; // only the retired name is set
    try {
      expect(ruleEvaluationFlagEnabled()).toBe(false);
      expect(ruleEvaluationSurfaceEnabled({ ruleeval: "on" })).toBe(false);
    } finally {
      if (savedOld === undefined) delete process.env[OLD];
      else process.env[OLD] = savedOld;
    }
  });
});

// --------------------------------------------------------------------------
// D-057 — optional default-on env var (INTERNAL_RULE_EVAL_DEFAULT_ON).
// ADDITIVE: purely a third input to the existing two-factor gate, gated by
// the SAME TRUE_TOKENS rule. Requirement mapping:
//   R001 — the decision table below (main flag / default-on var / param).
//   R002 — the "zero-regression" describe block proves byte-for-byte
//          equivalence with pre-D-057 semantics whenever the var is unset.
// --------------------------------------------------------------------------

const MAIN_FLAG_KEY = "INTERNAL_RULE_EVAL_ENABLED";

describe("ruleEvaluationDefaultOnEnabled — token classification (same TRUE_TOKENS rule)", () => {
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
    expect(ruleEvaluationDefaultOnEnabled(token)).toBe(expected);
  });

  it("is disabled when the var is absent (fail safe)", () => {
    expect(ruleEvaluationDefaultOnEnabled(undefined)).toBe(false);
  });
});

describe("ruleEvaluationSurfaceEnabled — D-057 full decision matrix (main flag ON)", () => {
  let savedFlag: string | undefined;
  beforeEach(() => {
    savedFlag = process.env[MAIN_FLAG_KEY];
    process.env[MAIN_FLAG_KEY] = "1"; // main flag on for every row in this block
  });
  afterEach(() => {
    if (savedFlag === undefined) delete process.env[MAIN_FLAG_KEY];
    else process.env[MAIN_FLAG_KEY] = savedFlag;
  });

  type ParamValue = string | string[] | undefined;

  // Column 1: the default-on var. "depends" rows resolve per the var; fixed
  // true/false rows are the SAME regardless of the var (proves the kill
  // switch and the true-opt-in path are both var-independent).
  const PARAM_ROWS: ReadonlyArray<[label: string, value: ParamValue, outcome: "depends" | boolean]> = [
    ["absent", undefined, "depends"],
    ["'on'", "on", true],
    ["'ON ' (case + trailing space)", "ON ", true],
    ["'off'", "off", false], // kill switch
    ["'0'", "0", false], // kill switch
    ["'' (present, empty string)", "", false], // kill switch
    ["'banana' (unrecognized)", "banana", false], // kill switch
    ["['on','off'] (array, first element true)", ["on", "off"], true],
    ["['off'] (array, first element non-true)", ["off"], false], // kill switch
    ["[] (present, empty array)", [], false], // kill switch — present, not absent
  ];

  const DEFAULT_ON_ROWS: ReadonlyArray<[label: string, value: string | undefined, isTrueToken: boolean]> = [
    ["unset", undefined, false],
    ["'1'", "1", true],
    ["'true'", "true", true],
    ["'garbage' (unrecognized)", "garbage", false],
    ["'' (empty)", "", false],
  ];

  const MATRIX: Array<[dLabel: string, dValue: string | undefined, pLabel: string, pValue: ParamValue, expected: boolean]> = [];
  for (const [dLabel, dValue, dIsTrue] of DEFAULT_ON_ROWS) {
    for (const [pLabel, pValue, pOutcome] of PARAM_ROWS) {
      const expected = pOutcome === "depends" ? dIsTrue : pOutcome;
      MATRIX.push([dLabel, dValue, pLabel, pValue, expected]);
    }
  }

  it.each(MATRIX)(
    "default-on=%s, ruleeval=%s -> %s",
    (_dLabel, dValue, _pLabel, paramValue, expected) => {
      if (dValue === undefined) delete process.env[INTERNAL_RULE_EVAL_DEFAULT_ON_ENV_VAR];
      else process.env[INTERNAL_RULE_EVAL_DEFAULT_ON_ENV_VAR] = dValue;
      expect(ruleEvaluationSurfaceEnabled({ ruleeval: paramValue })).toBe(expected);
    },
  );
});

describe("ruleEvaluationSurfaceEnabled — main flag OFF always wins (D-057-R001)", () => {
  let savedFlag: string | undefined;
  beforeEach(() => {
    savedFlag = process.env[MAIN_FLAG_KEY];
  });
  afterEach(() => {
    if (savedFlag === undefined) delete process.env[MAIN_FLAG_KEY];
    else process.env[MAIN_FLAG_KEY] = savedFlag;
  });

  // The main flag is checked FIRST and short-circuits before either the
  // default-on var or the param is read — off (or an unrecognized token) must
  // disable the surface unconditionally, even when the default-on var is a
  // true token and/or the param explicitly opts in.
  it.each([
    ["flag unset", undefined],
    ["flag '0'", "0"],
    ["flag 'banana' (unrecognized)", "banana"],
  ] as const)("%s: default-on=1, ruleeval absent -> false", (_label, flagValue) => {
    if (flagValue === undefined) delete process.env[MAIN_FLAG_KEY];
    else process.env[MAIN_FLAG_KEY] = flagValue;
    process.env[INTERNAL_RULE_EVAL_DEFAULT_ON_ENV_VAR] = "1";
    expect(ruleEvaluationSurfaceEnabled()).toBe(false);
  });

  it.each([
    ["flag unset", undefined],
    ["flag '0'", "0"],
  ] as const)("%s: default-on=1, ruleeval=on -> false", (_label, flagValue) => {
    if (flagValue === undefined) delete process.env[MAIN_FLAG_KEY];
    else process.env[MAIN_FLAG_KEY] = flagValue;
    process.env[INTERNAL_RULE_EVAL_DEFAULT_ON_ENV_VAR] = "1";
    expect(ruleEvaluationSurfaceEnabled({ ruleeval: "on" })).toBe(false);
  });

  it.each([
    ["flag unset", undefined],
    ["flag '0'", "0"],
  ] as const)("%s: default-on=1, ruleeval=off -> false", (_label, flagValue) => {
    if (flagValue === undefined) delete process.env[MAIN_FLAG_KEY];
    else process.env[MAIN_FLAG_KEY] = flagValue;
    process.env[INTERNAL_RULE_EVAL_DEFAULT_ON_ENV_VAR] = "1";
    expect(ruleEvaluationSurfaceEnabled({ ruleeval: "off" })).toBe(false);
  });
});

describe("D-057-R002 — zero behavior change where INTERNAL_RULE_EVAL_DEFAULT_ON is unset", () => {
  // Every row here holds the new var explicitly ABSENT and asserts the exact
  // pre-D-057 output for every param shape the old two-factor gate covered.
  // These are equivalence rows, not a rewrite of the existing tests above
  // (which stay unmodified) — this block is the R002 evidence artifact.
  let savedFlag: string | undefined;
  beforeEach(() => {
    savedFlag = process.env[MAIN_FLAG_KEY];
    delete process.env[INTERNAL_RULE_EVAL_DEFAULT_ON_ENV_VAR];
  });
  afterEach(() => {
    if (savedFlag === undefined) delete process.env[MAIN_FLAG_KEY];
    else process.env[MAIN_FLAG_KEY] = savedFlag;
  });

  it("main flag off (any params) -> off, unchanged", () => {
    delete process.env[MAIN_FLAG_KEY];
    expect(ruleEvaluationSurfaceEnabled()).toBe(false);
    expect(ruleEvaluationSurfaceEnabled({ ruleeval: "on" })).toBe(false);
    expect(ruleEvaluationSurfaceEnabled({ ruleeval: "off" })).toBe(false);
  });

  it("main flag on, param absent -> off, unchanged (this is the exact pre-D-057 default)", () => {
    process.env[MAIN_FLAG_KEY] = "1";
    expect(ruleEvaluationSurfaceEnabled()).toBe(false);
    expect(ruleEvaluationSurfaceEnabled({ ruleeval: undefined })).toBe(false);
  });

  it("main flag on, param='off' -> off, unchanged", () => {
    process.env[MAIN_FLAG_KEY] = "1";
    expect(ruleEvaluationSurfaceEnabled({ ruleeval: "off" })).toBe(false);
  });

  it("main flag on, param='on' -> on, unchanged (bookmarks keep working)", () => {
    process.env[MAIN_FLAG_KEY] = "1";
    expect(ruleEvaluationSurfaceEnabled({ ruleeval: "on" })).toBe(true);
    expect(ruleEvaluationSurfaceEnabled({ ruleeval: ["on"] })).toBe(true);
  });

  it("main flag on, param garbage/array forms -> off, unchanged", () => {
    process.env[MAIN_FLAG_KEY] = "1";
    expect(ruleEvaluationSurfaceEnabled({ ruleeval: "0" })).toBe(false);
    expect(ruleEvaluationSurfaceEnabled({ ruleeval: "" })).toBe(false);
    expect(ruleEvaluationSurfaceEnabled({ ruleeval: "banana" })).toBe(false);
    expect(ruleEvaluationSurfaceEnabled({ ruleeval: ["off"] })).toBe(false);
    expect(ruleEvaluationSurfaceEnabled({ ruleeval: [] })).toBe(false);
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

describe("announcementForRuleEvaluation — condo specifics match the visible label (DB-042(c)/HJ-3)", () => {
  // The generic strings the classifier would otherwise announce; the condo
  // announcements must NOT trail them (they must be strictly more specific).
  const GENERIC_MISSING_EVIDENCE = announcementForRuleEvaluation({
    kind: "evaluation",
    document: missingEvidenceDoc(),
    correlationId: null,
  });
  const GENERIC_APPLICABLE_DRAFT = announcementForRuleEvaluation({
    kind: "evaluation",
    document: draftApplicableDoc(),
    correlationId: null,
  });

  it("names the condo/site-confirmation specifics for a condo_base_lot_unresolved fail-safe", () => {
    const message = announcementForRuleEvaluation({
      kind: "evaluation",
      document: condoUnresolvedDoc(),
      correlationId: null,
    });
    // The visible label is "Condo base lot needs site confirmation"; the
    // announcement must carry the same specificity, never the generic string.
    expect(message).toContain("condo billing lot");
    expect(message).toContain("site-definition confirmation");
    expect(message).not.toBe(GENERIC_MISSING_EVIDENCE);
    expect(message).not.toMatch(/\bverified\b/i);
    expect(message).not.toMatch(/\bbest\b/i);
  });

  it("names entered-vs-analyzed base lots for a substrate_substitution stamp", () => {
    const message = announcementForRuleEvaluation({
      kind: "evaluation",
      document: substitutionStampDoc(),
      correlationId: null,
    });
    // The visible record is "analyzed on the base lot"; the announcement names
    // both the recorded base tax lot and the entered condo billing lot.
    expect(message).toContain("base tax lot");
    expect(message).toContain(SUBSTITUTION_ANALYZED_BBL);
    expect(message).toContain(SUBSTITUTION_ENTERED_BBL);
    expect(message).toContain("not a computed allowance");
    expect(message).not.toBe(GENERIC_APPLICABLE_DRAFT);
    expect(message).not.toMatch(/\bverified\b/i);
    expect(message).not.toMatch(/\bbest\b/i);
  });

  // [ORCH-CORRECTED per M5-T063 G3-F1/G4-C-1] The announcer must mirror the
  // visible stampLegitimate correspondence discipline: a stamp whose entered_bbl
  // disagrees with evaluated_input.bbl is IGNORED by the visible record
  // (analysis-identity-substitution.test.tsx pins that), so the announcer must
  // fall through to the generic classifier — never announce a substitution the
  // sighted surface does not show. Mutation-sensitive: removing the
  // entered_bbl === evaluated_input.bbl gate flips this red.
  it("announces the GENERIC string for a non-corresponding stamp (entered_bbl !== evaluated_input.bbl)", () => {
    const doc = substitutionStampDoc();
    // Contract-shape-valid but non-corresponding: the stamp names a different
    // entered lot than the document's evaluated identity.
    doc.substrate_substitution!.entered_bbl = "4000010001";
    const message = announcementForRuleEvaluation({
      kind: "evaluation",
      document: doc,
      correlationId: null,
    });
    expect(message).toBe(GENERIC_APPLICABLE_DRAFT);
    expect(message).not.toContain("base tax lot");
    expect(message).not.toContain("4000010001");
    expect(message).not.toContain(SUBSTITUTION_ANALYZED_BBL);
  });
});
