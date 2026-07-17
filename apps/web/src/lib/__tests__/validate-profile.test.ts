import { describe, expect, it } from "vitest";
import { validateProfileDocument } from "@/lib/validate-profile";
import { baseProfile, partialProfile, profileWithDistrictMaps } from "@/test-support/fixtures";

/**
 * S3: runtime validation of a 200 profile body against the GENERATED
 * canonical types. Valid committed fixtures pass; every mutation class
 * (missing required key, wrong type, bad enum, unpublished version,
 * broken conflict shape) fails TOTALLY — no partial profile escapes.
 */
describe("validateProfileDocument — valid documents", () => {
  it("accepts the committed real-builder fixture (contract 1.0.0 document)", () => {
    const result = validateProfileDocument(baseProfile());
    expect(result.ok).toBe(true);
  });

  it("accepts the derived 1.1.0 fixture with partial district maps", () => {
    const result = validateProfileDocument(profileWithDistrictMaps());
    expect(result.ok).toBe(true);
  });

  it("accepts a profile without identity.address/geometry (tolerance rules)", () => {
    const result = validateProfileDocument(partialProfile());
    expect(result.ok).toBe(true);
  });

  it("accepts every published contract_version", () => {
    for (const version of ["1.0.0", "1.1.0", "1.2.0", "1.3.0"]) {
      const profile = baseProfile();
      (profile.profile_version as unknown as Record<string, unknown>).contract_version =
        version;
      expect(validateProfileDocument(profile).ok).toBe(true);
    }
  });

  it("tolerates undocumented extra keys (open schemas) without reading them", () => {
    const profile = baseProfile() as unknown as Record<string, unknown>;
    profile.some_future_key = { anything: true };
    expect(validateProfileDocument(profile).ok).toBe(true);
  });
});

function expectProblems(body: unknown, needle: string) {
  const result = validateProfileDocument(body);
  expect(result.ok).toBe(false);
  if (!result.ok) {
    expect(result.problems.join("\n")).toContain(needle);
  }
}

describe("validateProfileDocument — rejection classes", () => {
  it("rejects a non-object body", () => {
    expectProblems([1, 2, 3], "not a JSON object");
    expectProblems("hello", "not a JSON object");
    expectProblems(null, "not a JSON object");
  });

  it("rejects a missing required top-level key", () => {
    const profile = baseProfile() as unknown as Record<string, unknown>;
    delete profile.missing_inputs;
    expectProblems(profile, "missing_inputs");
  });

  it("rejects an unpublished contract_version (closed set, never coerced)", () => {
    const profile = baseProfile();
    (profile.profile_version as unknown as Record<string, unknown>).contract_version = "2.0.0";
    expectProblems(profile, "profile_version.contract_version");
  });

  it("rejects a wrong-typed fact container value", () => {
    const profile = baseProfile();
    (profile.lot_facts as unknown as Record<string, unknown>).lotarea = "just a string";
    expectProblems(profile, "lot_facts.lotarea");
  });

  it("rejects a fact without provenance_ref (provenance is mandatory)", () => {
    const profile = baseProfile();
    delete (profile.lot_facts.lotarea as unknown as Record<string, unknown>).provenance_ref;
    expectProblems(profile, "provenance_ref");
  });

  it("rejects an out-of-enum coverage_status", () => {
    const profile = baseProfile();
    (profile.lot_facts.lotarea as unknown as Record<string, unknown>).coverage_status =
      "definitely_fine";
    expectProblems(profile, "coverage_status");
  });

  it("rejects a provenance record missing a required key", () => {
    const profile = baseProfile();
    delete (profile.provenance[0] as unknown as Record<string, unknown>).retrieved_at;
    expectProblems(profile, "retrieved_at");
  });

  it("rejects a conflict with fewer than 2 values", () => {
    const profile = baseProfile();
    (profile.conflicts as unknown[]).push({
      field: "borocode",
      values: [{ source_id: "nyc-dcp-pluto-soda", value: "1" }],
      resolution: "unresolved",
    });
    expectProblems(profile, "at least 2");
  });

  it("rejects an out-of-enum conflict resolution", () => {
    const profile = baseProfile();
    (profile.conflicts as unknown[]).push({
      field: "borocode",
      values: [
        { source_id: "a", value: "1" },
        { source_id: "b", value: "3" },
      ],
      resolution: "auto_resolved",
    });
    expectProblems(profile, "resolution");
  });

  it("rejects an out-of-enum data_completeness", () => {
    const profile = baseProfile() as unknown as Record<string, unknown>;
    profile.data_completeness = "mostly_fine";
    expectProblems(profile, "data_completeness");
  });

  it("rejects a reproducibility block missing required subfields", () => {
    const profile = baseProfile();
    delete (profile.reproducibility as unknown as Record<string, unknown>).correlation_id;
    expectProblems(profile, "reproducibility.correlation_id");
  });

  it("rejects an out-of-enum status_dimensions value", () => {
    const profile = baseProfile();
    (profile.status_dimensions as unknown as Record<string, unknown>).analysis_readiness =
      "definitely_ready";
    expectProblems(profile, "analysis_readiness");
  });

  it("rejects a district-provenance map whose refs are not non-empty strings", () => {
    const profile = profileWithDistrictMaps();
    (profile.zoning as unknown as Record<string, unknown>).district_provenance = {
      "R3-2": [""],
    };
    expectProblems(profile, "district_provenance");
  });

  it("bounds the reported problem list", () => {
    const result = validateProfileDocument({});
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.problems.length).toBeLessThanOrEqual(21);
    }
  });
});
