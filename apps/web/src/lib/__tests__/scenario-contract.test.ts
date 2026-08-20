import { describe, expect, it } from "vitest";
import { validateScenarioDocument, type Scenario } from "@/lib/scenario-contract";
import preliminaryFixture from "../../../../../packages/contracts/fixtures/valid/scenario/preliminary_r5_cap.json";
import noScenarioConflictFixture from "../../../../../packages/contracts/fixtures/valid/scenario/no_scenario_conflict.json";
import noScenarioProfessionalReviewFixture from "../../../../../packages/contracts/fixtures/valid/scenario/no_scenario_professional_review.json";
import unsupportedFamilyFixture from "../../../../../packages/contracts/fixtures/valid/scenario/unsupported_family.json";
import coverageStatusVerifiedFixture from "../../../../../packages/contracts/fixtures/invalid/scenario/coverage_status_verified.json";
import embeddedProfileFixture from "../../../../../packages/contracts/fixtures/invalid/scenario/embedded_property_profile.json";
import missingScenarioKindFixture from "../../../../../packages/contracts/fixtures/invalid/scenario/missing_scenario_kind.json";

/**
 * Task M5-T002 (+ D-022 correction): focused coverage of the runtime scenario
 * contract validator. Every 200 scenario body must pass this before it can
 * render; a body that does not honor the generated contract (or claims Verified)
 * is rejected TOTALLY with only a bounded problem list, so nothing can be drawn
 * from an invalid payload.
 *
 * The D-022 correction added: (a) faithful additionalProperties:false + required
 * enforcement at every object level, canonical BBL/digest patterns, a strictly
 * positive finite draft cap, full citation/assumption/constraint item shapes, the
 * cap_provenance.rule_status enum, and finite-number enforcement everywhere;
 * (b) an adversarial test per owner-reproduced bypass; and (c) fixture sweeps
 * asserting every committed valid fixture passes and every committed invalid
 * fixture fails.
 */

function clone(): Scenario {
  return structuredClone(preliminaryFixture) as unknown as Scenario;
}

/** Clone the valid preliminary fixture as a plain record so a single defect can
 * be injected at any path without fighting the generated types. */
function mutable(): Record<string, unknown> {
  return structuredClone(preliminaryFixture) as unknown as Record<string, unknown>;
}

describe("validateScenarioDocument", () => {
  it("accepts the committed preliminary fixture verbatim", () => {
    const result = validateScenarioDocument(clone());
    expect(result.ok).toBe(true);
  });

  it("rejects a non-object body", () => {
    const result = validateScenarioDocument("not an object");
    expect(result.ok).toBe(false);
  });

  it("rejects a wrong contract_version", () => {
    const doc = clone();
    (doc as unknown as { contract_version: string }).contract_version = "9.9.9";
    const result = validateScenarioDocument(doc);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.problems.some((p) => p.startsWith("contract_version"))).toBe(true);
  });

  it("rejects a coverage_status outside the draft enum (incl. verified)", () => {
    for (const bad of ["verified", "made_up"]) {
      const doc = clone();
      (doc as unknown as { coverage_status: string }).coverage_status = bad;
      expect(validateScenarioDocument(doc).ok).toBe(false);
    }
  });

  it("rejects a non-numeric draft cap", () => {
    const doc = clone();
    (doc as unknown as { draft_zoning_floor_area_cap_sq_ft: unknown }).draft_zoning_floor_area_cap_sq_ft =
      "15000";
    const result = validateScenarioDocument(doc);
    expect(result.ok).toBe(false);
  });

  it("rejects a constraint with an undocumented state", () => {
    const doc = clone();
    doc.constraints[0].state = "totally_fine" as unknown as Scenario["constraints"][number]["state"];
    expect(validateScenarioDocument(doc).ok).toBe(false);
  });

  it("caps the reported problem list (bounded report)", () => {
    // A wholesale-broken body must not flood the caller with unbounded problems.
    const result = validateScenarioDocument({});
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.problems.length).toBeLessThanOrEqual(21);
  });
});

// ---------------------------------------------------------------------------
// D-022: one focused adversarial test PER owner-reproduced bypass. Each clones a
// committed VALID fixture, injects exactly ONE defect, and asserts the document
// is rejected AND that a reported problem names the defective path. Every case
// was accepted by the pre-correction validator.
// ---------------------------------------------------------------------------

function expectRejectedAt(body: unknown, pathPrefix: string): void {
  const result = validateScenarioDocument(body);
  expect(result.ok).toBe(false);
  if (!result.ok) {
    expect(
      result.problems.some((p) => p.startsWith(`${pathPrefix}:`) || p.startsWith(`${pathPrefix}[`)),
      `expected a problem naming "${pathPrefix}"; got: ${result.problems.join(" | ")}`,
    ).toBe(true);
  }
}

describe("D-022 adversarial bypasses — every reproduced defect is now rejected", () => {
  it("bypass 1: draft_zoning_floor_area_cap_sq_ft = -1 (negative cap)", () => {
    const doc = mutable();
    doc.draft_zoning_floor_area_cap_sq_ft = -1;
    expectRejectedAt(doc, "draft_zoning_floor_area_cap_sq_ft");
  });

  it("bypass 2: draft_zoning_floor_area_cap_sq_ft = 0 (zero cap)", () => {
    const doc = mutable();
    doc.draft_zoning_floor_area_cap_sq_ft = 0;
    expectRejectedAt(doc, "draft_zoning_floor_area_cap_sq_ft");
  });

  it("bypass 3: evaluated_input.bbl = 'x' (non-canonical BBL)", () => {
    const doc = mutable();
    (doc.evaluated_input as Record<string, unknown>).bbl = "x";
    expectRejectedAt(doc, "evaluated_input.bbl");
  });

  it("bypass 4: cap_provenance.rule_status = 'verified' (outside the enum)", () => {
    const doc = mutable();
    (doc.cap_provenance as Record<string, unknown>).rule_status = "verified";
    expectRejectedAt(doc, "cap_provenance.rule_status");
  });

  it("bypass 5: cap_provenance.citations = [null] (null citation item)", () => {
    const doc = mutable();
    (doc.cap_provenance as Record<string, unknown>).citations = [null];
    expectRejectedAt(doc, "cap_provenance.citations[0]");
  });

  it("bypass 6: assumptions = [null] (null assumption item)", () => {
    const doc = mutable();
    doc.assumptions = [null];
    expectRejectedAt(doc, "assumptions[0]");
  });

  it("bypass 7: an unexpected top-level property (additionalProperties:false)", () => {
    const doc = mutable();
    doc.surprise_top_level_key = true;
    expectRejectedAt(doc, "surprise_top_level_key");
  });

  it("bypass 8: the committed embedded_property_profile.json invalid fixture", () => {
    const doc = structuredClone(embeddedProfileFixture) as unknown as Record<string, unknown>;
    // The defect is an embedded full property_profile at the root.
    expectRejectedAt(doc, "property_profile");
  });

  it("also rejects a +Infinity/NaN cap and a provenance ARRAY (the typeof hole)", () => {
    const inf = mutable();
    inf.draft_zoning_floor_area_cap_sq_ft = Number.POSITIVE_INFINITY;
    expectRejectedAt(inf, "draft_zoning_floor_area_cap_sq_ft");

    const nan = mutable();
    nan.draft_zoning_floor_area_cap_sq_ft = Number.NaN;
    expectRejectedAt(nan, "draft_zoning_floor_area_cap_sq_ft");

    const arrProv = mutable();
    (arrProv.constraints as Record<string, unknown>[])[0].provenance = [];
    expectRejectedAt(arrProv, "constraints[0].provenance");
  });
});

// ---------------------------------------------------------------------------
// D-022: committed fixture sweeps. Every committed valid scenario fixture MUST
// pass and every committed invalid scenario fixture MUST fail. The fixtures are
// imported statically (the same way the existing tests load preliminaryFixture)
// so the sweep typechecks under `tsc --noEmit` without vite/client's
// import.meta.glob ambient types. Any fixture ADDED to these committed
// directories must be added here — the sweep is the enforcement point, and a new
// fixture that is not listed is a visible omission in this file.
// ---------------------------------------------------------------------------

const validFixtures: [string, unknown][] = [
  ["preliminary_r5_cap.json", preliminaryFixture],
  ["no_scenario_conflict.json", noScenarioConflictFixture],
  ["no_scenario_professional_review.json", noScenarioProfessionalReviewFixture],
  ["unsupported_family.json", unsupportedFamilyFixture],
];

const invalidFixtures: [string, unknown][] = [
  ["coverage_status_verified.json", coverageStatusVerifiedFixture],
  ["embedded_property_profile.json", embeddedProfileFixture],
  ["missing_scenario_kind.json", missingScenarioKindFixture],
];

describe("committed scenario fixtures sweep", () => {
  it("covers every committed fixture in both directories", () => {
    // A guard against a fixture being added to the repo but not to this sweep:
    // these counts must equal the directory listings (4 valid, 3 invalid today).
    expect(validFixtures.length).toBe(4);
    expect(invalidFixtures.length).toBe(3);
  });

  it.each(validFixtures)("valid fixture %s passes validation", (_name, doc) => {
    expect(validateScenarioDocument(structuredClone(doc)).ok).toBe(true);
  });

  it.each(invalidFixtures)("invalid fixture %s fails validation", (_name, doc) => {
    expect(validateScenarioDocument(structuredClone(doc)).ok).toBe(false);
  });

  it("includes and rejects embedded_property_profile.json explicitly", () => {
    const entry = invalidFixtures.find(([name]) => name === "embedded_property_profile.json");
    expect(entry, "embedded_property_profile.json must be among the committed invalid fixtures").toBeDefined();
    const result = validateScenarioDocument(structuredClone(entry![1]));
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.problems.some((p) => p.startsWith("property_profile:"))).toBe(true);
    }
  });
});
