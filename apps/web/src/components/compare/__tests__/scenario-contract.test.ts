import { describe, expect, it } from "vitest";
import { MAX_REFLECTED_TEXT_LENGTH, TRUNCATION_MARKER } from "@/lib/bounded";
import { MAX_RESPONSE_BYTES, boundScenarioDocument } from "@/lib/scenario-bounds";
import {
  MAX_DOCUMENT_ARRAY_LENGTH,
  validateScenarioDocument,
} from "@/lib/scenario-contract";
import {
  conflictScenarioBody,
  preliminaryScenarioBody,
  professionalReviewScenarioBody,
  unsupportedScenarioBody,
} from "./scenario-fixtures";

/**
 * Contract-validator and bounding coverage for the Compare screen (task
 * M5-T004 rework).
 *
 * FILE LOCATION: the repo convention for library tests is
 * `src/lib/__tests__/`, but this packet's `allowed_paths` cover
 * `apps/web/src/lib/scenario-*` (direct children only) and
 * `apps/web/src/components/compare/**`. These tests therefore live beside the
 * other Compare tests, which is also where their fixtures already live.
 *
 * WHAT THEY GUARD. `validateScenarioDocument` is the AS-4 gate: it is the only
 * thing standing between a plausible-but-malformed 200 body and the screen.
 * Before the rework its depth did not match its promises — `cap_provenance` was
 * accepted as "object or null" and then double-cast to a `CapProvenance`
 * (G4-2), `assumptions[].value` / `.unit` were unchecked, unknown keys were
 * never rejected despite a documented "documented key set" claim (G5-3), and no
 * array had any bound at all (G5-1). Each of those holes gets a test that
 * fails if the hole reopens.
 */

function validate(body: unknown) {
  return validateScenarioDocument(body);
}

function problemsFor(body: unknown): string[] {
  const result = validate(body);
  return result.ok ? [] : result.problems;
}

const COMMITTED_FIXTURES: Array<[string, () => Record<string, unknown>]> = [
  ["preliminary_r5_cap", preliminaryScenarioBody],
  ["no_scenario_professional_review", professionalReviewScenarioBody],
  ["no_scenario_conflict", conflictScenarioBody],
  ["unsupported_family", unsupportedScenarioBody],
];

describe("validateScenarioDocument — the committed contract fixtures all pass", () => {
  for (const [name, build] of COMMITTED_FIXTURES) {
    it(`accepts ${name} unchanged`, () => {
      const result = validate(build());
      expect(result.ok).toBe(true);
    });
  }

  it("returns the document itself, byte-identical, on success", () => {
    const body = preliminaryScenarioBody();
    const result = validate(body);
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    // The validator checks SHAPE; it never rewrites a value.
    expect(result.document.draft_zoning_floor_area_cap_sq_ft).toBe(15000);
    expect(result.document as unknown).toBe(body);
  });
});

describe("validateScenarioDocument — cap_provenance is validated, not assumed", () => {
  it("rejects a cap whose provenance names no objective and no rule", () => {
    const body = preliminaryScenarioBody();
    body.cap_provenance = { note: "tbd" };
    const problems = problemsFor(body);
    expect(problems.some((p) => p.startsWith("cap_provenance.output_name"))).toBe(true);
    expect(problems.some((p) => p.startsWith("cap_provenance.rule_id"))).toBe(true);
  });

  it("rejects a rule_status outside the documented 4-value enum", () => {
    const body = preliminaryScenarioBody();
    (body.cap_provenance as Record<string, unknown>).rule_status = "verified";
    expect(problemsFor(body).some((p) => p.startsWith("cap_provenance.rule_status"))).toBe(
      true,
    );
  });

  it("rejects a non-null cap carrying a NULL provenance", () => {
    // A material value may never be surfaced without its provenance.
    const body = preliminaryScenarioBody();
    body.cap_provenance = null;
    expect(problemsFor(body).some((p) => p.startsWith("cap_provenance"))).toBe(true);
  });

  it("accepts a null provenance when there is no cap to justify", () => {
    const body = preliminaryScenarioBody();
    body.cap_provenance = null;
    body.draft_zoning_floor_area_cap_sq_ft = null;
    expect(validate(body).ok).toBe(true);
  });

  it("rejects citations that are not an array, and citation elements missing their source provenance", () => {
    const body = preliminaryScenarioBody();
    (body.cap_provenance as Record<string, unknown>).citations = { snapshot_id: "x" };
    expect(problemsFor(body).some((p) => p.startsWith("cap_provenance.citations"))).toBe(
      true,
    );

    const body2 = preliminaryScenarioBody();
    const provenance2 = body2.cap_provenance as Record<string, unknown>;
    (provenance2.citations as Record<string, unknown>[])[0].provenance = "not an object";
    expect(
      problemsFor(body2).some((p) => p.startsWith("cap_provenance.citations[0].provenance")),
    ).toBe(true);
  });
});

describe("validateScenarioDocument — identifiers must survive display unaltered", () => {
  // boundedToken strips everything outside [A-Za-z0-9._-] and cuts at 64, BOTH
  // silently. Applied to the nine identifier fields that meant a contract-legal
  // id could reach the screen quietly rewritten — and `zr:23-21` and `zr/23-21`,
  // two DISTINCT snapshots, collapsing onto one displayed string. These are the
  // pointers to the legal authority behind the cap.
  it.each([
    ["a colon", "zr:23-21"],
    ["a slash", "zr/23-21"],
    ["a plus", "1.0.0+build.5"],
    ["a space", "zr 23-21"],
    ["only unrepresentable characters", "::::"],
    ["more than 64 characters", "z".repeat(65)],
  ])("rejects a citation snapshot_id containing %s", (_case, snapshotId) => {
    const body = preliminaryScenarioBody();
    const provenance = body.cap_provenance as Record<string, unknown>;
    (provenance.citations as Record<string, unknown>[])[0].snapshot_id = snapshotId;
    expect(
      problemsFor(body).some((p) => p.startsWith("cap_provenance.citations[0].snapshot_id")),
    ).toBe(true);
  });

  it("rejects an altered rule_version rather than displaying a different one", () => {
    const body = preliminaryScenarioBody();
    (body.cap_provenance as Record<string, unknown>).rule_version = "1.0.0+build.5";
    expect(
      problemsFor(body).some((p) => p.startsWith("cap_provenance.rule_version")),
    ).toBe(true);
  });

  it("rejects an altered constraint key and coverage family", () => {
    const body = preliminaryScenarioBody();
    (body.constraints as Record<string, unknown>[])[0].key = "residential far cap";
    (body.coverage_matrix as Record<string, unknown>[])[0].constraint_family =
      "residential/far";
    const problems = problemsFor(body);
    expect(problems.some((p) => p.startsWith("constraints[0].key"))).toBe(true);
    expect(problems.some((p) => p.startsWith("coverage_matrix[0].constraint_family"))).toBe(
      true,
    );
  });

  it("names no offending value in the problem, only the client's own rule", () => {
    const body = preliminaryScenarioBody();
    (body.cap_provenance as Record<string, unknown>).rule_id = "SECRET:MARKER";
    for (const problem of problemsFor(body)) {
      expect(problem).not.toContain("SECRET");
    }
  });

  it("treats an EMPTY identifier as representable — emptiness is a separate question", () => {
    // Otherwise the representability check would silently re-impose the
    // non-empty rule that rule_id / rule_version were deliberately relaxed out
    // of, and a defective rule record would still black out the screen.
    const body = preliminaryScenarioBody();
    const provenance = body.cap_provenance as Record<string, unknown>;
    provenance.rule_id = "";
    provenance.rule_version = "";
    expect(validate(body).ok).toBe(true);
  });
});

describe("validateScenarioDocument — strictness follows where the field comes from", () => {
  it("accepts an empty rule_id / rule_version: a defective rule record is not an outage", () => {
    // Both are propagated from the rule_evaluation trace and both schemas type
    // them as bare strings with no minLength, so the server's own jsonschema
    // gate would ship an empty one. Rejecting here replaced a cap carrying
    // valid citations with a validation-failure card — strictly worse for the
    // reader than a visibly blank rule id.
    const body = preliminaryScenarioBody();
    (body.cap_provenance as Record<string, unknown>).rule_id = "";
    expect(validate(body).ok).toBe(true);

    const body2 = preliminaryScenarioBody();
    (body2.cap_provenance as Record<string, unknown>).rule_version = "";
    expect(validate(body2).ok).toBe(true);
  });

  it("still rejects an empty output_name: it is constant-sourced and names the objective", () => {
    // .claude/rules/frontend-web.md:13 — never show a maximum without naming
    // the optimized objective.
    const body = preliminaryScenarioBody();
    (body.cap_provenance as Record<string, unknown>).output_name = "";
    expect(
      problemsFor(body).some((p) => p.startsWith("cap_provenance.output_name")),
    ).toBe(true);
  });

  it("still rejects an empty note: also constant-sourced, so empty is unreachable", () => {
    const body = preliminaryScenarioBody();
    (body.cap_provenance as Record<string, unknown>).note = "";
    expect(problemsFor(body).some((p) => p.startsWith("cap_provenance.note"))).toBe(true);
  });
});

describe("validateScenarioDocument — the remaining depth holes", () => {
  it("rejects needs_review: false (the schema pins it true)", () => {
    const body = preliminaryScenarioBody();
    body.needs_review = false;
    expect(problemsFor(body).some((p) => p.startsWith("needs_review"))).toBe(true);
  });

  it("rejects an undocumented top-level key", () => {
    const body = preliminaryScenarioBody();
    body.surprise_field = "hello";
    expect(problemsFor(body).some((p) => p.startsWith("scenario:"))).toBe(true);
  });

  it("rejects a constraint value that is an OBJECT rather than a contract scalar", () => {
    // This is the value format.ts would otherwise JSON.stringify into the DOM.
    const body = preliminaryScenarioBody();
    (body.constraints as Record<string, unknown>[])[1].value = { nested: true };
    expect(problemsFor(body).some((p) => p.startsWith("constraints[1].value"))).toBe(true);
  });

  it("checks assumptions[].value and assumptions[].unit", () => {
    const body = preliminaryScenarioBody();
    body.assumptions = [
      {
        key: "utilization_factor",
        assumption_type: "utilization_factor",
        // value key present but of a forbidden type; unit of a forbidden type.
        value: { nested: true },
        unit: 5,
        rationale: "because",
      },
    ];
    const problems = problemsFor(body);
    expect(problems.some((p) => p.startsWith("assumptions[0].value"))).toBe(true);
    expect(problems.some((p) => p.startsWith("assumptions[0].unit"))).toBe(true);
  });

  it("accepts a well-formed assumption", () => {
    const body = preliminaryScenarioBody();
    body.assumptions = [
      {
        key: "utilization_factor",
        assumption_type: "utilization_factor",
        value: 0.85,
        unit: null,
        rationale: "declared explicitly, never applied silently",
      },
    ];
    expect(validate(body).ok).toBe(true);
  });
});

describe("validateScenarioDocument — arrays REJECT at the shared bound, never truncate", () => {
  it("uses one shared constant for every array", () => {
    expect(MAX_DOCUMENT_ARRAY_LENGTH).toBe(64);
  });

  it("accepts exactly the bound and rejects one past it", () => {
    const atBound = preliminaryScenarioBody();
    atBound.reasons = Array.from({ length: MAX_DOCUMENT_ARRAY_LENGTH }, (_, i) => `r${i}`);
    expect(validate(atBound).ok).toBe(true);

    const overBound = preliminaryScenarioBody();
    overBound.reasons = Array.from(
      { length: MAX_DOCUMENT_ARRAY_LENGTH + 1 },
      (_, i) => `r${i}`,
    );
    const result = validate(overBound);
    expect(result.ok).toBe(false);
    // REJECTED, not silently shortened — dropping a `reasons` entry would hide
    // why no scenario could be stated.
    expect(result.ok === false && result.problems.some((p) => p.startsWith("reasons:"))).toBe(
      true,
    );
  });

  it("bounds the weakly-typed provenance arrays the renderers walk", () => {
    const body = professionalReviewScenarioBody();
    const constraints = body.constraints as Record<string, unknown>[];
    const districtProvenance = constraints[2].provenance as Record<string, unknown>;
    districtProvenance.base_district_candidates = Array.from(
      { length: MAX_DOCUMENT_ARRAY_LENGTH + 1 },
      () => ({ district_label: "R5" }),
    );
    expect(
      problemsFor(body).some((p) =>
        p.startsWith("constraints[2].provenance.base_district_candidates"),
      ),
    ).toBe(true);
  });

  it("never leaks a byte of the rejected body into the problem list", () => {
    // The problem list is RENDERED by ScenarioValidationFailureState, so it
    // must stay body-independent (G5 cross-reviewer confirmation 1).
    const body = preliminaryScenarioBody();
    body.contract_version = "9.9.9-SECRET-MARKER";
    body.surprise_SECRET_MARKER = true;
    (body.cap_provenance as Record<string, unknown>).rule_status = "SECRET-MARKER";
    for (const problem of problemsFor(body)) {
      expect(problem).not.toContain("SECRET-MARKER");
    }
  });
});

describe("boundScenarioDocument — strings truncate explicitly, material values never change", () => {
  it("leaves every number exactly as delivered", () => {
    const result = validate(preliminaryScenarioBody());
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    const bounded = boundScenarioDocument(result.document);

    expect(bounded.draft_zoning_floor_area_cap_sq_ft).toBe(15000);
    expect(bounded.integrity_check.tolerance).toBe(1e-6);
    expect(bounded.constraints[0].value).toBe(15000);
    expect(bounded.constraints[1].value).toBe(10000);
  });

  it("leaves the document's own identity untouched so a mismatch cannot be laundered", () => {
    const result = validate(preliminaryScenarioBody());
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    const bounded = boundScenarioDocument(result.document);
    expect(bounded.evaluated_input.bbl).toBe("1000477501");
    expect(bounded.evaluated_input.input_fingerprint).toBe(
      result.document.evaluated_input.input_fingerprint,
    );
  });

  it("truncates over-long free text with the explicit marker", () => {
    const body = preliminaryScenarioBody();
    (body.constraints as Record<string, unknown>[])[0].note = "y".repeat(5000);
    const result = validate(body);
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    const note = boundScenarioDocument(result.document).constraints[0].note;
    expect(note.endsWith(TRUNCATION_MARKER)).toBe(true);
    expect(note.length).toBe(MAX_REFLECTED_TEXT_LENGTH + TRUNCATION_MARKER.length);
  });

  it("does not mutate the document it was given", () => {
    const result = validate(preliminaryScenarioBody());
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    const before = result.document.constraints[0].note;
    boundScenarioDocument(result.document);
    expect(result.document.constraints[0].note).toBe(before);
  });

  it("declares the pre-parse response budget", () => {
    expect(MAX_RESPONSE_BYTES).toBe(256 * 1024);
  });
});
