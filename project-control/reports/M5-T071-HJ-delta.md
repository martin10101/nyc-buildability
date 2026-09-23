# M5-T071 — human-journey DELTA re-verdict (VERBATIM, single transmission)

TRANSMISSION HISTORY (orchestrator note, not reviewer text): delivered complete in one
transmission 2026-09-23 (~04:53Z) with END-OF-REPORT present. Supplements the wave-1 FAIL
report (M5-T071-HJ.md); together they are the full HJ record for this task. The reviewer's
own text follows, unedited.

---

# G3 HUMAN-JOURNEY DELTA RE-VERDICT — M5-T071

**Verdict: PASS** on the corrected identity. Both blocking findings are closed; no new defect introduced.

**Identity verified independently.** The five task files carry identical blob SHAs at `0014ad8f`, at the resubmit-seam head `fb424f2d`, and at the current branch head `86971988` (e.g. `ProposalOutlineMap.tsx` = `0c06195d8022ded8bef04b8e63e227ee55b13d41` at all three). `0014ad8f` is an ancestor of `fb424f2d`, which is an ancestor of `86971988`, so the later commits are disjoint as stated and CI run 35819674425 at `fb424f2d` validated exactly the source I just read. `0014ad8f` touches only the five allowed files — `ProposalEditor.tsx` and `apps/web/e2e/` are absent, so the cross-lane wall still holds.

**B1 — CLOSED.** The gesture invitation now exists in exactly one place: the wrapper's map-state-gated instruction paragraph. The section lead reads "Add points and type them by keyboard in the table below", the context note reads "**Any** reference map shown displays the recorded lot for context only" (a conditional, not a presence claim), and the empty-state row no longer says "over the lot" (that also closes A6). Walking the composed section top-to-bottom on a condo unit lot, there is now no sentence that invites or presumes a map. The new spec in `proposal-outline-draw.test.tsx` asserts on the whole section's `textContent`, which is the right level — it is the assertion that was missing, and restoring the old lead reddens it since that suite's leaf mock always classifies absent.

**B2 — CLOSED, and closed the way that preserves honesty rather than just removing the sentence.** The tri-state seeds "unknown" from the leaf's `lot-outline-loading` node, and the loading copy ("Preparing the reference map — you can start adding points by keyboard…") makes a claim about the current state only, never about the lot. The definite negative now renders only when the leaf has actually resolved to a non-drawable outcome, which is where it is true. First paint is "unknown", so no false negative exists at any point in the load window. The transition spec walks loading → interactive → fallback at a fixed `bbl`, so only the observer can drive it — real teeth, not a tautology. This also covers A4's inverse edge in the safe direction: during "unknown" nothing is invited.

**A8 — CLOSED.** `:568` now waits on the presence of the `proposal-drawn-outline-points` layer rather than an exact `addLayer` tally, which preserves the hit-test precondition the spec needs while removing the last instance of the DB-048 flake class in that file.

**The drift guard is the best addition in this set and it closes a coupling risk I only flagged obliquely.** The wrapper classifies the leaf by two string literals it cannot control; before this commit, a rename in the accepted leaf would have silently degraded the copy to permanent "unknown" or permanent "absent" with every suite still green — fail-safe but invisible. Pinning both signals against the real `LotOutlineMap` makes that failure loud. It also removes the mock-versus-real gap I raised as the knowledge item for the `lot-outline-loading` signal specifically, so what remains unproven in a real browser is narrower than what I originally reported: the `MutationObserver` firing against live MapLibre DOM churn.

**Riders acknowledged as correctly scoped.** A1 (silent drop of untyped rows once three finite points exist), A2 (incomplete rows counted but not identified), A3 (transition not announced), A5 (selection announced inconsistently at zero finite points), A7 (disabled Convert out of tab order), and the real-browser observer check are all genuinely non-blocking and none of them are made worse by this correction set. Routing them to DB-049 on the post-accept drawing-surface packet is the right disposition; none of them needs to hold this increment.

Nothing in the finiteness work moved, and the finite-value flows remain byte-identical.

END-OF-REPORT
