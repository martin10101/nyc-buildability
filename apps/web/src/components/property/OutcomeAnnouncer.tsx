/**
 * Persistent assistive-technology announcer (task M2-T005, visual-quality
 * Major D1).
 *
 * THE DEFECT THIS FIXES: the loading card's own live region unmounts when
 * an outcome arrives, so its replacement content was never announced — a
 * screen-reader user heard "Looking up BBL…" and then silence for every
 * failure state on both screens.
 *
 * THE PATTERN: one visually-hidden `role="status"` region that is ALWAYS
 * mounted (it never unmounts, so updates are reliably announced). The
 * parent screen sets `message` to the outcome announcement on arrival and
 * clears it to "" while a lookup is in flight — clearing guarantees that a
 * repeat of the same outcome (for example a retry that fails the same way)
 * is announced again, because the region's text genuinely changes.
 *
 * EXACTLY-ONCE (scenario S1): this is the only live region that carries
 * outcome-arrival text. The failure cards deliberately do NOT carry
 * `role="alert"`/`aria-live`, so mounting them cannot produce a second
 * announcement of the same event. Focus management (moving focus to the
 * outcome heading) is handled by the screens, not by this component.
 * `aria-atomic` makes each update read as one whole message.
 *
 * M4-T005: an optional `testId` (default "outcome-announcer") lets a SECOND,
 * independent live region coexist on the same screen (the additive
 * rule-evaluation surface mounts its own announcer) without colliding on the
 * default test id — the property/confirm announcers are unchanged.
 */
export function OutcomeAnnouncer({
  message,
  testId = "outcome-announcer",
}: {
  message: string;
  testId?: string;
}) {
  return (
    <div
      className="visually-hidden"
      role="status"
      aria-live="polite"
      aria-atomic="true"
      data-testid={testId}
    >
      {message}
    </div>
  );
}
