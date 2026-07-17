/**
 * Test fixtures for unit/component tests ONLY (task M2-T001). Nothing in
 * this directory is imported by application code — the app has no mocked
 * success path (acceptance scenario S7).
 *
 * Base document: the committed contract fixture
 * packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json
 * — the accepted M1-T005 builder's byte-exact output for the real official
 * PLUTO record of BBL 1000010010 (Governors Island split-zone lot, live
 * capture fixture F05). No official value is invented here.
 *
 * DERIVATIONS (each documented; keys removed or annotated only):
 *
 * - profileWithDistrictMaps(): contract 1.1.0 variant. Sets
 *   profile_version.contract_version to "1.1.0" and adds a PARTIAL
 *   zoning.district_provenance map covering ONLY "R3-2" (ref =
 *   the existing zonedist1 provenance record) plus a
 *   special_district_provenance map for "GI" (ref = the existing spdist1
 *   record). "C4-1" is deliberately left unmapped so tests exercise the
 *   M1-T006 D5 rule that partial linkage is legal and the
 *   original_field_name fallback join must cover unmapped values.
 *
 * - partialProfile(): removes identity.address and identity.geometry
 *   (M1-T005 G3 section 5 tolerance rule: only present-column facts are
 *   emitted; address/geometry may be absent). No other change.
 */

import type { PropertyProfile } from "@/lib/property-profile";
import builderOutput from "../../../../packages/contracts/fixtures/valid/property_profile/builder_output_m1_t005.json";

export function baseProfile(): PropertyProfile {
  // structuredClone so a test can never mutate the shared fixture module.
  return structuredClone(builderOutput) as unknown as PropertyProfile;
}

export function profileWithDistrictMaps(): PropertyProfile {
  const profile = baseProfile();
  profile.profile_version.contract_version = "1.1.0";
  profile.zoning.district_provenance = {
    "R3-2": ["pluto-64uk-42ks-26v1-1000010010-zonedist1"],
    // "C4-1" intentionally unmapped (partial linkage per M1-T006 D5).
  };
  profile.zoning.special_district_provenance = {
    GI: ["pluto-64uk-42ks-26v1-1000010010-spdist1"],
  };
  return profile;
}

export function partialProfile(): PropertyProfile {
  const profile = baseProfile();
  delete profile.identity.address;
  delete profile.identity.geometry;
  return profile;
}

/** Minimal JSON Response helper for fetch stubs in tests. */
export function jsonResponse(
  body: unknown,
  status: number,
  correlationId = "test-correlation-id",
): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json",
      "X-Correlation-ID": correlationId,
    },
  });
}
