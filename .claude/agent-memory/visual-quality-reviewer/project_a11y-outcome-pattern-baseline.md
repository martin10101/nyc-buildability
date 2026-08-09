---
name: a11y-outcome-pattern-baseline
description: Accepted D1 fix pattern (M2-T005) — persistent role=status OutcomeAnnouncer + FailureTitle focus targets; baseline for all future screen reviews
metadata:
  type: project
---

M2-T005 (reviewed at 39c39a5, 2026-07-17) established the project's canonical outcome-arrival a11y pattern, which I endorsed at G4:

- One persistent visually-hidden `role="status" aria-live="polite" aria-atomic` `OutcomeAnnouncer` per screen; message text from `src/lib/announce.ts`; cleared to `""` while loading so repeat outcomes re-announce. Failure cards deliberately carry NO `role="alert"`/`aria-live` (exactly-once at DOM level).
- Focus: outcome headings are `tabIndex={-1}` + `data-outcome-heading` (shared `FailureTitle` in `FailureState.tsx`); retry focuses the loading card (`data-focus-target`, `focusOnMount`); programmatic-focus ring uses `:focus` (not `:focus-visible`) on those attributes in globals.css.
- Focus-ring token: `rgba(31,79,130,0.9)` → blended ~rgb(53,97,143), ~6.4:1 on white (D5 resolved at code level).

**Why:** the original M2-T002 D1 defect was a live region that unmounted before the outcome; a persistent region is structurally immune, and polite status + focus echo is quieter than `role="alert"` on mounting cards.

**How to apply:** future screens (Compare, Evidence, reports) should reuse OutcomeAnnouncer/FailureTitle rather than inventing per-card alerts; flag any new mounting `role="alert"` as a probable double-announce. Open items for the first browser session: CF-1 (real-SR focus-echo + CompletenessBanner mount interplay), CF-2 (focus-ring pixels — new e2e traces have focused-element screenshots), CF-3 (ring inside .table-scroll at 360px). Cosmetic quirks I logged as observations, not defects: mouse-click on an outcome heading paints the focus ring (`:focus` tradeoff); bad-param h1 renders at 1.05rem (.failure-title) vs 1.4rem h1 elsewhere.
