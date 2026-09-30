import { UNUSED_FLOOR_AREA_NOT_AVAILABLE_TEXT } from "@/lib/architect/unused-floor-area";

/**
 * Queue D-06 (plan §3 step 4, M2-07; RECONCILIATION set-aside item #6, C-3).
 *
 * The unused-floor-area section (UnusedFloorAreaSection) is set aside behind the
 * default-off server flag INTERNAL_UNUSED_FLOOR_AREA_SECTION_ENABLED. With the
 * flag off the scenario views show this one plain line instead: no number, no
 * recorded building area, nothing subtracted. The full-site allowance (the cap)
 * still shows in its own card, untouched.
 */

/** The plan's exact words, alone in one element. */
export function UnusedFloorAreaNotAvailableLine() {
  return (
    <p className="fact-value" data-testid="unused-floor-area-not-available">
      {UNUSED_FLOOR_AREA_NOT_AVAILABLE_TEXT}
    </p>
  );
}

/** The card the scenario views mount in place of the set-aside section. */
export function UnusedFloorAreaSetAside() {
  return (
    <section className="card" data-testid="scenario-unused-floor-area-set-aside">
      <h2 className="section-title">Unused floor area on the lot</h2>
      <UnusedFloorAreaNotAvailableLine />
    </section>
  );
}
