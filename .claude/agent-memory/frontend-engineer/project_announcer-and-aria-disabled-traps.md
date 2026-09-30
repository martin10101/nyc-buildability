---
name: announcer-and-aria-disabled-traps
description: Review-proven UI traps from the M5-T078 drawing-surface rework - shared announcer state leaking into cards, same-string re-announce, aria-disabled losing :disabled CSS, ungated screen-reader-only clauses
metadata:
  type: feedback
---

Four traps G3/G4/HJ all caught on the drawing surface (M5-T078, 2026-09-24):

1. Never render the shared `announcement` state inside a persistent card. Any second writer
   (e.g. a blocked-button handler) silently rewrites the card. Build card text from the
   outcome itself (e.g. `announcementForOutlineBridge(outcome)`).
2. Setting the same string twice is a React bail-out, so nothing changes in the DOM and a
   repeated reason is never re-announced. Clear it, then set it on a later task (a timer
   cancelled on unmount, on the next press and on conversion start/result). Test with a
   MutationObserver that records the region's textContent: expect "" then the reason.
3. Moving `disabled` to `aria-disabled` (to keep the button in the tab order) drops every
   `button:disabled` CSS rule. Add `[aria-disabled="true"]` to that rule in the same change.
4. Screen-reader-only status text needs the same state gating as the visible instructions.
   Map-click wording must only appear when the map is actually present, and must say "move"
   rather than "place" when a point is selected.

**Why:** each one failed a gate as BLOCKING or a named advisory, and each needed a full rework
round.
**How to apply:** check all four whenever an announcer, aria-disabled, or map-state copy is
touched. Name the literal pre-fix code in every mutation trace. Related:
[[property-profile-frontend-rules]].
