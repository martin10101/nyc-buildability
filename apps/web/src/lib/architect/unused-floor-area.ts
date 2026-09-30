import type { Scenario } from "@/lib/scenario-contract";

/**
 * Display vocabulary for the unused-floor-area line (queue D-06; plan §3 step 4,
 * M2-07; RECONCILIATION set-aside item #6, C-3). No arithmetic lives here.
 */

/** Plan §3 step 4, verbatim: what remaining capacity shows without an existing
 * zoning floor area. The server's A-03 default section carries the same words
 * (services/api/app/scenario/constants.py UNUSED_FLOOR_AREA_NOT_AVAILABLE_TEXT). */
export const UNUSED_FLOOR_AREA_NOT_AVAILABLE_TEXT = "Not available — needs existing zoning floor area";

/** Key of the machine-readable basis record the server puts in the section's
 * `assumptions` when it states no difference because no existing zoning floor
 * area is available (A-03, `unused_floor_area_not_available_assumption`). The
 * closed `not_computable_reason` enum cannot say this yet, so the record is the
 * signal, not the reason. */
export const UNUSED_FLOOR_AREA_NOT_AVAILABLE_KEY = "unused_floor_area_not_available";

/** True when the server says the section needs an existing zoning floor area. */
export function needsExistingZoningFloorArea(
  section: Scenario["unused_draft_zoning_floor_area"],
): boolean {
  return section.assumptions.some(
    (assumption) => assumption.key === UNUSED_FLOOR_AREA_NOT_AVAILABLE_KEY,
  );
}
