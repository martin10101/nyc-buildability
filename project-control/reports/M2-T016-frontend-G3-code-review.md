# M2-T016 frontend — G3 code-review gate (code-reviewer) — VERDICT: PASS

Saved verbatim by the orchestrator (transport only). Reviewer: `code-reviewer` (independent, read-only).
Reviewed `dc8c5de` (worktree `agent-a973a7a01a1a58933`, base `37667ff`). Scope confirmed `apps/web/**` only (40 files).

---

VERDICT: PASS

## 0. FINGERPRINT FAIL-SAFE DETERMINATION (highest priority)
**The hand-rolled fingerprint is FAIL-SAFE. NOT BLOCKING.** A canonicalization mismatch between `apps/web/src/lib/surveyReview/fingerprint.ts` and backend `history_fingerprint` can only cause a correction to be **spuriously refused with `concurrent_review_modification` (409) before any write** — never corruption, data loss, or concurrency bypass.
- Backend refuses BEFORE persisting (`review_actions.py:742-748`, no `save_fact` on mismatch); matched token still runs the full validator chain. A mismatch is only ever a false negative (over-strict). A false positive would need a SHA-256 collision (infeasible).
- FE handles the refusal safely: `api.ts:441-446` re-reads + attaches `currentDocument`; `SurveyReviewScreen.tsx:144-154` keeps the editor open + preserves the draft + persistent stale-notice; retry submits with the freshly recomputed fingerprint → succeeds. `errorCopy.ts:44-50` "nothing was lost or corrupted."
- **(a) SHA-256 correct — VERIFIED** (FIPS 180-4 vectors pinned in `fingerprint.test.ts`; standard construction).
- **(b) Byte-for-byte canonical-JSON match — NOT guaranteed for all values (the real gap, fail-safe):** `canonicalize` mirrors Python `json.dumps(sort_keys=True, separators=(",",":"), ensure_ascii=False)` for common cases but DIVERGES on number formatting (JS `String(n)` vs Python `repr`): integer-valued floats `5.0`→`"5.0"` (Py) vs `"5"` (JS); `1e16`→`"1e+16"` vs `"10000000000000000"`; `1e-07` vs `1e-7`. Plain ints + typical decimals match. First correction hashes `[]` identically (dominant case); divergence can only bite on a 2nd+ correction with a divergent stored number → still a safe spurious 409.
- **Test caveat:** the mock imports the FE's own `historyFingerprint`, so the suite proves round-trip only within the JS reimplementation — cannot detect Py/JS divergence. Fail-safe conclusion rests on dual code-reading. Follow-up: expose the fingerprint on backend `FactView` + add a Py↔JS CI cross-vector.

## 1. Reconciliation — MATCHES, no drift
Digest-keyed endpoints (colon URL-encoded), `reopen` (edge 12), re-read-after-mutation (`finishMutation`→`reReadAsAction`), all **10** error codes (the 9 summary + `post_confirmation_edit_refused` — FE reconciled against the REAL handler), `confirmation_rejected` decodes `detail.rejected_fact_ids`, flat `FactView` field map 1:1.

## 2. Five AWAITING-BACKEND gaps — all HONEST degradation
Fingerprint (fail-safe §0); display_label/ai_drafted_label (humanized, never authoritative); principal capabilities (default all-enabled + `capabilities_known:false`, server 403 enforces, dominant-action never *claims* success — acceptable-with-followup); inbox (honest empty state); per-check expected/observed (shows counts + reason, no fabricated numbers — advisory partial-§7.4).

## 3. Human-journey fixes — correct; F1/F3 tests genuinely prove behavior
F1 (`isOpenItem` counts only check_fail/unresolved; dominant flips to Confirm via backend `confirm_precondition_met`); F3 (draft lifted to `SurveyReviewScreen` above the remount, preserved on 409 + stale-notice); F2 (accurate affirmation copy); F4 (non-color overlay cues); F5 (`coerceToSampleType` keeps numeric type).

## 4. General FE quality — sound
No `dangerouslySetInnerHTML` (no XSS; user values render as escaped text/aria-label); no secrets (only public `NEXT_PUBLIC_API_BASE_URL` + fail-safe-OFF `INTERNAL_SURVEY_REVIEW_ENABLED`); `api.ts` hardening (AbortController 12s timeout, no-store, shape-validation before render, bounded reflection, typed transport failures); no new dependencies (lockfile unchanged); conventions match the hardened property client. Latent-only: `DocumentOverlay.tsx:135` SVG `<image href>` uses `image_ref` (always null today) — validate URL scheme if the backend later supplies it (advisory).

## Tracked follow-ups (non-blocking)
1. Expose `accepted_history_fingerprint` on backend `FactView` + delete the client derivation (eliminates the Py/JS divergence entirely).
2. Return principal capabilities on the review read so the UI pre-disables (SC-S3 prod clarity).
3. Surface failing-check `expected`/`observed` on `FactView` (full SC-S6 numeric detail).
4. Once (1) lands, add a Python↔JS canonical-string CI cross-vector.

## Orchestrator-captured evidence to add
Run `apps/web` vitest (fingerprint/model/api/survey-review/config) + Playwright e2e on CI; capture a Python-vs-JS canonicalization comparison for `[]`, an integer-valued-float entry, and a typical decimal, to document the divergence boundary empirically.

**VERDICT: PASS.** Fingerprint fail-safe; reconciliation matches; honesty core intact; F1-F5 correct; quality sound; no blocking defects.
