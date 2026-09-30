// Server-read, default-off gate for the SET-ASIDE unused-floor-area section
// (queue D-06, plan §3 step 4 and M2-07; RECONCILIATION set-aside item #6, C-3).
//
// Plan §3 step 4: existing floor area is never taken from city-recorded (DOF)
// building area. Until an existing ZONING floor area exists (M2-07), the
// scenario views show "Not available — needs existing zoning floor area" in
// place of the section. The section component (UnusedFloorAreaSection) and its
// tests are kept; it renders only when the non-public runtime flag
// INTERNAL_UNUSED_FLOOR_AREA_SECTION_ENABLED holds an explicit true token.
// Absent, empty or unknown -> off (fail safe). Same pattern as
// INTERNAL_PROPOSAL_EDITOR_ENABLED (./proposal-editor-flag.ts): never prefixed
// NEXT_PUBLIC_, so it is never inlined into the browser bundle. A Server
// Component reads it once per request and passes a plain boolean into the
// client tree; no client value can turn it on.

const TRUE_TOKENS: ReadonlySet<string> = new Set(["1", "true", "yes", "on"]);

export const UNUSED_FLOOR_AREA_SECTION_FLAG = "INTERNAL_UNUSED_FLOOR_AREA_SECTION_ENABLED";

export function unusedFloorAreaSectionEnabled(
  env: Record<string, string | undefined> = process.env,
): boolean {
  const raw = env[UNUSED_FLOOR_AREA_SECTION_FLAG];
  return typeof raw === "string" && TRUE_TOKENS.has(raw.trim().toLowerCase());
}
