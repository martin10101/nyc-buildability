import { useLayoutEffect, useRef } from "react";

/**
 * Staged loading indicator (task M2-T001; design system section 12: show
 * the actual pipeline). Stages reflect what genuinely happens — client
 * format validation (already completed when this renders), then one request
 * to the platform API which retrieves the official record and builds the
 * canonical profile. No fake progress percentages, no invented stages.
 *
 * M2-T005 (D1 focus management): the section is a programmatic focus
 * target (`tabIndex={-1}`, `data-focus-target`). When a RETRY unmounts the
 * failure card that held the focused Retry button, the screen mounts this
 * card with `focusOnMount` so focus moves here instead of dropping to
 * `body`; when the outcome arrives, the screen moves focus to the outcome
 * heading. Initial (non-retry) lookups never pass `focusOnMount`, so this
 * card never steals focus from the form.
 *
 * D-flake (a11y-announcements.spec.ts:152): the focus call runs in a LAYOUT
 * effect, i.e. inside the same React commit that inserts this card and
 * removes the failure card holding the focused Retry button — before the
 * browser can paint or run any other task. A passive `useEffect` is not
 * enough: when the commit is not a discrete-input commit (Confirm enters
 * loading from its fetch effect), React may yield to the browser between
 * the DOM change and the effect, so focus sat on `<body>` while this card
 * was already visible. React's own `autoFocus` focuses in this same phase.
 */
export function LoadingStages({
  bbl,
  focusOnMount = false,
}: {
  bbl: string;
  focusOnMount?: boolean;
}) {
  const sectionRef = useRef<HTMLElement | null>(null);

  useLayoutEffect(() => {
    if (focusOnMount) {
      sectionRef.current?.focus();
    }
  }, [focusOnMount]);

  return (
    <section
      ref={sectionRef}
      tabIndex={-1}
      data-focus-target
      className="card"
      aria-live="polite"
      data-testid="loading-stages"
    >
      <h2 className="section-title">Looking up BBL {bbl}</h2>
      <ol className="loading-stages">
        <li className="stage-done">
          <span aria-hidden="true">✓</span> BBL format checked
        </li>
        <li className="stage-active">
          <span aria-hidden="true">…</span> Retrieving the official property
          record and building the canonical profile
        </li>
        <li className="stage-pending">Rendering official facts</li>
      </ol>
    </section>
  );
}
