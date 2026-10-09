import {
  UNUSED_FLOOR_AREA_NOT_AVAILABLE_REASON,
  UNUSED_FLOOR_AREA_NOT_AVAILABLE_TEXT,
} from "@/lib/architect/unused-floor-area";

/**
 * Queue D-06 (plan §3 step 4, M2-07; RECONCILIATION set-aside item #6, C-3).
 *
 * The unused-floor-area section (UnusedFloorAreaSection) is set aside behind the
 * default-off server flag INTERNAL_UNUSED_FLOOR_AREA_SECTION_ENABLED. With the
 * flag off the scenario views show these two plain lines instead: no number, no
 * recorded building area, nothing subtracted. The full-site allowance (the cap)
 * still shows in its own card, untouched.
 *
 * Wording: the owner's settled choice (D-090-R038, 2026-10-01; DB-101 option A),
 * which replaces plan §3 step 4's. The two lines carry their own row label, so no
 * other label ("Unused floor area") names the same quantity.
 */

/** The owner's exact words: line 1 (row label and value), then line 2 (the reason). */
export function UnusedFloorAreaNotAvailableLine() {
  return (
    <>
      <p className="fact-value" data-testid="unused-floor-area-not-available">
        {UNUSED_FLOOR_AREA_NOT_AVAILABLE_TEXT}
      </p>
      <p className="section-note" data-testid="unused-floor-area-not-available-reason">
        {UNUSED_FLOOR_AREA_NOT_AVAILABLE_REASON}
      </p>
    </>
  );
}

/** The card the scenario views mount in place of the set-aside section. */
export function UnusedFloorAreaSetAside() {
  return (
    <section className="card" data-testid="scenario-unused-floor-area-set-aside">
      <UnusedFloorAreaNotAvailableLine />
    </section>
  );
}
