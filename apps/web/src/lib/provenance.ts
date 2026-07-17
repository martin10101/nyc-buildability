/**
 * Provenance join logic (task M2-T001).
 *
 * Facts: fact.provenance_ref -> provenance[].provenance_id (PRD sections
 * 9/19; referential integrity is enforced by the backend, but the UI still
 * degrades honestly if a ref does not resolve).
 *
 * Zoning district strings (M1-T006 G3 D5): the contract-1.1.0 maps
 * (zoning.district_provenance / commercial_overlay_provenance /
 * special_district_provenance) are OPTIONAL and may be PARTIAL. When a value
 * has no map entry, fall back to joining provenance[].original_field_name
 * against the documented PLUTO source columns for that array, matching the
 * record whose normalized_value equals the district string. The live
 * M1-T005 builder emits contract 1.0.0 (no maps), so the fallback is the
 * production path today; the map path is exercised with derived 1.1.0
 * fixtures in tests.
 */

import type {
  DistrictProvenanceMap,
  PropertyProfile,
  SourceFact,
} from "./contract";

/** PLUTO columns that carry each zoning value family (D5 fallback join). */
const FALLBACK_COLUMNS = {
  districts: ["zonedist1", "zonedist2", "zonedist3", "zonedist4"],
  commercial_overlays: ["overlay1", "overlay2"],
  special_districts: ["spdist1", "spdist2", "spdist3"],
} as const;

export type ZoningArrayName = keyof typeof FALLBACK_COLUMNS;

export interface DistrictProvenance {
  /** Records backing this value; may be empty when nothing is joinable. */
  records: SourceFact[];
  /** Which join produced the records. */
  joinedVia: "provenance_map" | "original_field_name_fallback" | "none";
}

export function provenanceById(
  profile: PropertyProfile,
): Map<string, SourceFact> {
  const byId = new Map<string, SourceFact>();
  for (const record of profile.provenance) {
    byId.set(record.provenance_id, record);
  }
  return byId;
}

/** Resolve a fact's provenance_ref; null = dangling (rendered honestly). */
export function resolveFactProvenance(
  provenanceRef: string,
  byId: Map<string, SourceFact>,
): SourceFact | null {
  return byId.get(provenanceRef) ?? null;
}

function mapForArray(
  profile: PropertyProfile,
  arrayName: ZoningArrayName,
): DistrictProvenanceMap | undefined {
  switch (arrayName) {
    case "districts":
      return profile.zoning.district_provenance;
    case "commercial_overlays":
      return profile.zoning.commercial_overlay_provenance;
    case "special_districts":
      return profile.zoning.special_district_provenance;
  }
}

/**
 * Provenance for one zoning value string. NEVER assumes full map coverage:
 * map entry -> fallback column join -> explicit "none" (still rendered,
 * labeled as not linkable — nothing is hidden or fabricated).
 */
export function resolveDistrictProvenance(
  profile: PropertyProfile,
  arrayName: ZoningArrayName,
  value: string,
  byId: Map<string, SourceFact>,
): DistrictProvenance {
  const map = mapForArray(profile, arrayName);
  const refs = map?.[value];
  if (refs && refs.length > 0) {
    const records = refs
      .map((ref) => byId.get(ref))
      .filter((r): r is SourceFact => r !== undefined);
    if (records.length > 0) {
      return { records, joinedVia: "provenance_map" };
    }
  }

  // D5 fallback: join by original_field_name within the documented columns,
  // keeping only records whose value matches this district string.
  const columns: readonly string[] = FALLBACK_COLUMNS[arrayName];
  const records = profile.provenance.filter(
    (record) =>
      columns.includes(record.original_field_name) &&
      (record.normalized_value === value || record.original_value === value),
  );
  if (records.length > 0) {
    return { records, joinedVia: "original_field_name_fallback" };
  }
  return { records: [], joinedVia: "none" };
}
