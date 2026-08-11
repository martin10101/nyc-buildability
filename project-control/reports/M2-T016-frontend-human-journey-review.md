# M2-T016 frontend — human-journey gate (human-journey-reviewer) — VERDICT: PASS (required corrections F1, F3; advisory F2/F4/F5)

Saved verbatim by the orchestrator (transport only). Reviewer: `human-journey-reviewer` (independent, read-only,
evidence-based). Reviewed worktree branch `worktree-agent-a973a7a01a1a58933` @ `99f5cc5`. Thin-client: no runnable
app — journey traced from source + Playwright/vitest specs + fixtures + mock backend. Canonical contract:
`docs/SURVEY_REVIEW_WORKFLOW.md`. Per gate-verdict semantics, F1+F3 are blocking-for-acceptance required corrections.

---

## Summary
The honesty core is faithful: **no place where unconfirmed or rejected evidence reads as authoritative, and no silent default of an unresolved item.** Two state layers kept explicit; "Verified" never appears as a status; confirmation is capability-gated + H5-gated with no automatic/AI path; conflicts non-dismissible; downstream conclusions blocked/provisional, cleared only through recalc. SC-S1..S7 substantially satisfied. Findings are UX-clarity + one recovery/a11y edge — advisory or should-fix, not safety.

## Per-scenario verdicts (file:line evidence)
- **SC-S1 primary journey — SATISFIED (F1, F2).** open needs_review; highest-urgency conflict focused first (`model.ts:45-64`); overlay geometry (`DocumentOverlay.tsx:137-163`); accept/correct(reason)/reject (`FocusedItem.tsx:91-168`, `CorrectionForm.tsx:35-67`); audit visible (`CorrectionHistory.tsx:78-111`, `StateHistory.tsx:12-44`); H5-gated confirm (`ConfirmDocumentPanel.tsx:93-147`); e2e `survey-review-journey.spec.ts:14-70`.
- **SC-S2 immutability — SATISFIED.** original_value immutable in type (`types.ts:144-146`), shown side-by-side + append-only chain (`CorrectionHistory.tsx:23-111`), digest shown; asserted intact after correction.
- **SC-S3 authorization — SATISFIED.** capability-gated, disabled-with-plain-reason never silently absent (`FocusedItem.tsx:98-131`); confirm/reject reserved to confirm-capable role; server re-enforces (mock 403); proven consumer/preparer/professional.
- **SC-S4 no-auto-verified — SATISFIED.** No "Verified" state anywhere (`labels.ts:32-101`); auto_extracted/clean read "Unconfirmed evidence"; confirm gated on server `can_confirm_document` + every material fact's backend `promotion.allowed` (`model.ts:87-105`), never role/confidence; "confidence never promotes a value" (`FocusedItem.tsx:80-83`).
- **SC-S5 downstream honesty — SATISFIED.** blocked/provisional named, no fabricated value for blocked; provisional labeled "(not final)" + assumption (`DownstreamImpact.tsx:47-84`); read-model-driven, no dismiss control, clears only via recalc.
- **SC-S6 conflict display — SATISFIED.** failing checks show "Conflict" + plain-language + expected/observed + explicit "cannot be dismissed"; no acknowledge/ignore control (`ChecksPanel.tsx:44-67`); only correct/reject resolve.
- **SC-S7 recovery + a11y — SATISFIED (F3, F4).** read-failure safe retry; mid-action failure preserves input for common transport cases; always-mounted live region (`OutcomeAnnouncer.tsx:29-47`); keyboard overlay + labels + alt-summary; status quadruple label+symbol+tone+gloss; responsive, critical warnings unhidden at phone width.
- **SC-S8 regression — OUT OF SCOPE** for this reviewer (CI/integration); specs present + self-consistent.

## Findings
- **F1 — required (moderate, non-blocking-to-core).** Dominant-action guidance never points to "Confirm" even when it is the only step: `openItemCount` counts clean-but-`unconfirmed` material facts as open (`model.ts:67-74`), so the strip says "resolve N open items" while `canOfferConfirm` is true and Confirm is enabled (`SurveyReviewScreen.tsx:227-233`) — the `confirmReady` branch is effectively unreachable; contradicts spec §10.3. Fix: exclude clean/resolved-but-unconfirmed material facts from the "open items" count for the dominant-action copy, or flip to the confirm prompt once `canOfferConfirm`.
- **F2 — advisory (moderate).** "Accept" produces no visible/auditable effect yet announces "Decision recorded … recalculated" (`SurveyReviewScreen.tsx:86-90`); read-model unchanged, no per-fact affirmed marker, overstates "recalculated." Fix: visible/audited affirmation affordance + accurate copy.
- **F3 — required (moderate, non-blocking-to-core, untested).** On `stale_history` the screen reloads (`SurveyReviewScreen.tsx:91-97`); `FocusedItem` key includes `correction_history.length`+confirmation state (`:283`) → remount → mode resets to view → CorrectionForm unmounts → typed value/reason lost; the `stale_history` copy never renders. Contradicts spec §10.8. Fix: preserve in-progress input across the reload (lift draft above remount) + persistent visible explanation; add a test.
- **F4 — advisory (moderate).** Overlay rects differentiate status by tone color only (`DocumentOverlay.tsx:148`; css:128-143); text equivalents exist off-mark, but a sighted CVD user reading the overlay relies on color alone — §10.2 forbids color-only for the overlay's uncertain/conflicting marks. Fix: add a per-tone non-color cue on the mark (dashed stroke / status glyph).
- **F5 — advisory (minor).** Corrections always submit `corrected_normalized_value` as a string even for numeric facts (`CorrectionForm.tsx:27-59`); backend re-validates but FE has no type-aware editor. Fix: preserve original JSON type.

## Positive (validated, keep)
Honest two-layer model persists after confirmation (non-material/unconfirmed still read "Unconfirmed evidence" under a "Professionally confirmed" document); disabled-with-reason authorization mirroring; client-side read-model shape guard (`validate.ts`, `api.ts:202-220`); internal-only fail-safe-off route gate (`config.ts`, `page.tsx:20-21`).

## Verdict
No finding lets unconfirmed/rejected evidence read as authoritative or silently defaults an unresolved item. SC-S1..S7 demonstrably satisfied. Record **PASS with required corrections F1, F3** (advisory F2/F4/F5), re-verified before acceptance.
