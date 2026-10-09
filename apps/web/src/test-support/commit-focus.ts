/**
 * D-flake (a11y-announcements.spec.ts:152) test support: what an outside
 * observer — a screen reader, or a Playwright `document.activeElement`
 * probe — can see the moment a React commit finishes.
 *
 * Call `sampleCommitFocus()` from a `<Profiler onRender>` wrapped around a
 * screen. React calls `onRender` INSIDE each commit, during the layout phase:
 * after the subtree's layout effects and before any passive `useEffect`.
 * A focus move done in a layout effect is therefore visible in the sample; a
 * focus move left to a passive effect is not — that gap (DOM already changed,
 * focus still on `<body>`) is exactly the window the e2e probe hit, because
 * React may let the browser paint and run other tasks before passive effects
 * of a non-discrete commit.
 *
 * A focused element that was removed from the document counts as `body`: a
 * browser moves focus to `<body>` when the focused node is removed (jsdom may
 * keep reporting the detached node, which would hide the regression).
 */
export type CommitActive = "body" | "loading-stages" | "outcome-heading" | "other";

export interface CommitFocus {
  /** The loading card (`data-testid="loading-stages"`) is in the document. */
  loadingMounted: boolean;
  /** An outcome heading (`[data-outcome-heading]`) is in the document. */
  headingMounted: boolean;
  /** Where focus is at this commit. */
  active: CommitActive;
}

export function sampleCommitFocus(): CommitFocus {
  const el = document.activeElement;
  let active: CommitActive = "other";
  if (
    el === null ||
    el === document.body ||
    el === document.documentElement ||
    !el.isConnected
  ) {
    active = "body";
  } else if (el.getAttribute("data-testid") === "loading-stages") {
    active = "loading-stages";
  } else if (el.hasAttribute("data-outcome-heading")) {
    active = "outcome-heading";
  }
  return {
    loadingMounted: document.querySelector('[data-testid="loading-stages"]') !== null,
    headingMounted: document.querySelector("[data-outcome-heading]") !== null,
    active,
  };
}
