import { describe, expect, it } from "vitest";
import { validateScenarioDocument, type Scenario } from "@/lib/scenario-contract";
import preliminaryFixture from "../../../../../packages/contracts/fixtures/valid/scenario/preliminary_r5_cap.json";

/**
 * Task M5-T002: focused coverage of the runtime scenario contract validator.
 * Every 200 scenario body must pass this before it can render; a body that does
 * not honor the generated contract (or claims Verified) is rejected TOTALLY with
 * only a bounded problem list, so nothing can be drawn from an invalid payload.
 */

function clone(): Scenario {
  return structuredClone(preliminaryFixture) as unknown as Scenario;
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
