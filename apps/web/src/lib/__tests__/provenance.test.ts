import { describe, expect, it } from "vitest";
import {
  provenanceById,
  resolveDistrictProvenance,
  resolveFactProvenance,
} from "@/lib/provenance";
import { baseProfile, profileWithDistrictMaps } from "@/test-support/fixtures";

/**
 * S2: district provenance with the 1.1.0 map PRESENT and ABSENT (M1-T006
 * G3 D5 fallback join), including PARTIAL map coverage. Fact provenance_ref
 * joins per PRD sections 9/19.
 */
describe("fact provenance join", () => {
  it("resolves a fact's provenance_ref to its record", () => {
    const profile = baseProfile();
    const byId = provenanceById(profile);
    const record = resolveFactProvenance(
      profile.lot_facts.lotarea.provenance_ref,
      byId,
    );
    expect(record).not.toBeNull();
    expect(record?.original_field_name).toBe("lotarea");
    expect(record?.original_value).toBe("7577714");
    expect(record?.source_id).toBe("nyc-dcp-pluto-soda");
  });

  it("returns null for a dangling ref (rendered as an honest gap)", () => {
    const byId = provenanceById(baseProfile());
    expect(resolveFactProvenance("does-not-exist", byId)).toBeNull();
  });
});

describe("district provenance — contract 1.0.0 (no maps, live API today)", () => {
  it("joins every district via the original_field_name fallback", () => {
    const profile = baseProfile();
    expect(profile.zoning.district_provenance).toBeUndefined();
    const byId = provenanceById(profile);

    const r32 = resolveDistrictProvenance(profile, "districts", "R3-2", byId);
    expect(r32.joinedVia).toBe("original_field_name_fallback");
    expect(r32.records.map((r) => r.original_field_name)).toEqual(["zonedist1"]);

    const c41 = resolveDistrictProvenance(profile, "districts", "C4-1", byId);
    expect(c41.joinedVia).toBe("original_field_name_fallback");
    expect(c41.records.map((r) => r.original_field_name)).toEqual(["zonedist2"]);

    const gi = resolveDistrictProvenance(profile, "special_districts", "GI", byId);
    expect(gi.joinedVia).toBe("original_field_name_fallback");
    expect(gi.records.map((r) => r.original_field_name)).toEqual(["spdist1"]);
  });

  it("returns an explicit 'none' join when nothing is linkable", () => {
    const profile = baseProfile();
    const byId = provenanceById(profile);
    const result = resolveDistrictProvenance(
      profile,
      "commercial_overlays",
      "C1-3",
      byId,
    );
    expect(result.joinedVia).toBe("none");
    expect(result.records).toEqual([]);
  });
});

describe("district provenance — contract 1.1.0 with a PARTIAL map (D5)", () => {
  it("uses the map for mapped values and the fallback for unmapped values", () => {
    const profile = profileWithDistrictMaps();
    const byId = provenanceById(profile);

    // Mapped value -> map join.
    const r32 = resolveDistrictProvenance(profile, "districts", "R3-2", byId);
    expect(r32.joinedVia).toBe("provenance_map");
    expect(r32.records.map((r) => r.original_field_name)).toEqual(["zonedist1"]);

    // Unmapped sibling value -> fallback join (partial linkage is legal).
    const c41 = resolveDistrictProvenance(profile, "districts", "C4-1", byId);
    expect(c41.joinedVia).toBe("original_field_name_fallback");
    expect(c41.records.map((r) => r.original_field_name)).toEqual(["zonedist2"]);

    // Special-district map join.
    const gi = resolveDistrictProvenance(profile, "special_districts", "GI", byId);
    expect(gi.joinedVia).toBe("provenance_map");
    expect(gi.records.map((r) => r.original_field_name)).toEqual(["spdist1"]);
  });

  it("falls back when a map entry holds only unresolvable refs", () => {
    const profile = profileWithDistrictMaps();
    profile.zoning.district_provenance = { "R3-2": ["dangling-ref"] };
    const byId = provenanceById(profile);
    const r32 = resolveDistrictProvenance(profile, "districts", "R3-2", byId);
    expect(r32.joinedVia).toBe("original_field_name_fallback");
    expect(r32.records.map((r) => r.original_field_name)).toEqual(["zonedist1"]);
  });
});
