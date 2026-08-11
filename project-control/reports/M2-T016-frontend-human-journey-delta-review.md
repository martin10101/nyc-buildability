# M2-T016 frontend — human-journey delta re-verification (human-journey-reviewer) — VERDICT: PASS (delta); F1 & F3 RESOLVED

Saved verbatim by the orchestrator (transport only). Reviewer: `human-journey-reviewer` (independent, read-only,
evidence-based; thin client). Delta `99f5cc5` → `dc8c5de` on `worktree-agent-a973a7a01a1a58933`. Follows the
original human-journey gate (`M2-T016-frontend-human-journey-review.md`, PASS with required F1+F3).

---

VERDICT: PASS (delta) — F1 RESOLVED, F3 RESOLVED; F2/F4/F5 addressed; no journey regression

## Required corrections
- **F1 — RESOLVED.** `isOpenItem` now counts only facts with an open deterministic check (`model.ts:61-63`: `check_fail>0 || check_unresolved>0`); a clean-but-`unconfirmed` fact is no longer "open." `dominantAction` (`model.ts:131-146`) flips to "Next: confirm or reject the document below." once `canOfferConfirm` (consumes backend `confirm_precondition_met`, `model.ts:88-94`, never React-computed). Proven by `model.test.ts:99-122`, `survey-review.test.tsx:53-67`, e2e `survey-review-journey.spec.ts:91-92`. Old always-on "resolve N open items" copy gone.
- **F3 — RESOLVED.** Correction editor is parent-controlled: `correcting`/`correctionDraft`/`staleNotice` live in `SurveyReviewScreen` above the `FocusedItem` remount boundary (`:54-57,160-166`). On `concurrent_review_modification` carrying `currentDocument`, the screen reloads fresh state but keeps the editor open, preserves the draft, shows a persistent `role="alert"` notice (`:144-154`; `CorrectionForm.tsx:31-45,89-93,110-143`). The remount re-injects the preserved draft. Proven by `survey-review.test.tsx:105-155` (editor stays open, value=4800, reason preserved, stale-notice visible).

## Advisory
- **F2 — addressed.** Accept shows a visible session affirmation marker with accurate copy ("You affirmed this value this session at {time}. A recalculation … was requested. (Affirmation is recorded in the server audit trail; this marker is a session reminder.)", `FocusedItem.tsx:146-158`); announcement no longer falsely claims completion (`SurveyReviewScreen.tsx:94`). Session-local marker correctly labeled as a reminder (not a durable badge) — acceptable.
- **F4 — addressed.** Overlay marks carry non-color cues: dashed (conflict `6 3`) / dotted (unresolved `2 3`) stroke + per-mark status glyph (≠/?/✕/✓/◐) as SVG text (`DocumentOverlay.tsx:41-54,145-175`); aria-labels + alt-summary retained. e2e `overlay-glyph-<id>` visible.
- **F5 — addressed.** `coerceToSampleType` (`model.ts:115-128`) keeps numeric facts numeric (non-parsing input falls back to raw string, never silent wrong-type); no-op check compares coerced JSON; field annotated "(numeric)" + `inputMode="decimal"`.

## Honesty core intact (no regression; one strengthening)
Two-layer model preserved; no "Verified" (validator rejects it); capability+H5-gated confirm; **rejected material facts now BLOCK confirmation** (strengthened — `confirmation_rejected`+`rejected_fact_ids` surfaced in the confirm panel; `survey-review.test.tsx:177-198`, e2e :66-68); conflicts non-dismissible; blocked/provisional propagation with no silent defaults; post-confirmation edit refused → audited reopen (edge 12).

## New finding (non-blocking, tracked follow-up)
**J1 — Production capability degradation weakens SC-S3 UI CLARITY (not the security property).** The reconciled read model has no server capability surface, so `api.ts` defaults capabilities to enabled with `capabilities_known:false` (`:71-90`); real capabilities used only when the backend returns a principal (`:276-286`). In production an unauthorized user would see enabled actions (incl. Confirm) and learn they can't act only on the server's `unauthorized_review_action` refusal — degraded UI mirroring vs the fixture suite. It does NOT breach the honesty/security core (server fails closed; no unauthorized action succeeds; nothing reads as authoritative); code is explicitly honest (AWAITING-BACKEND + `capabilities_known` guard). Bind the capability surface + review-inbox endpoint to the route/read-model follow-up.

## Delta verdict
F1 + F3 RESOLVED; F2/F4/F5 addressed; honesty core survives (stronger in one respect); every fix encoded in a reproducing test; J1 is the known honestly-degraded, server-fail-closed capability/inbox surface — a tracked follow-up, not a blocker. **PASS (delta).**
