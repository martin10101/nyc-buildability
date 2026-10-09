import type { Scenario } from "@/lib/scenario-contract";
import { NOT_CONFIRMED, REMAINING_CAPACITY_LABEL, REMAINING_CAPACITY_REASON } from "./tax-lot-scope";

/**
 * Display vocabulary for the unused-floor-area line (queue D-06; plan §3 step 4,
 * M2-07; RECONCILIATION set-aside item #6, C-3). No arithmetic lives here.
 */

/** The owner's settled wording (D-090-R038, 2026-10-01; DB-101 option A), which replaces the
 * plan §3 step 4 wording. Line 1 of what remaining development capacity shows without a
 * verified value: the row label and its value. The server's A-03 default section carries the
 * same words (services/api/app/scenario/constants.py UNUSED_FLOOR_AREA_NOT_AVAILABLE_TEXT). */
export const UNUSED_FLOOR_AREA_NOT_AVAILABLE_TEXT = `${REMAINING_CAPACITY_LABEL}: ${NOT_CONFIRMED}`;

/** Line 2: the reason (constants.py UNUSED_FLOOR_AREA_NOT_AVAILABLE_REASON_TEXT). */
export const UNUSED_FLOOR_AREA_NOT_AVAILABLE_REASON = REMAINING_CAPACITY_REASON;

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
