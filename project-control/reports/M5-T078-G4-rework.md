# M5-T078 + M5-T079 — G4 re-review after the reworks (qa-engineer "qa-web2", read-only; fresh reviewer; joint)

> Transmission history: one joint re-review pinned at 6c79cd88, delivered as four SendMessage parts (1/4..4/4)
> ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed
> only); saved identically as M5-T078-G4-rework.md and M5-T079-G4-rework.md. A separate follow-up message
> asking the orchestrator to write the reviewer's memory is NOT part of this report and was not acted on.
> Verdicts: both PASS (advisory survivors only). CI proof cited: web + web-e2e SUCCESS at 6c79cd88.

---

M5-T078/T079 G4 RE-REVIEW (qa-engineer, read-only) — part 1/4: pin, CI, M5-T078 F1–F3 closure.

PIN: HEAD 6c79cd88b519d2df5ad605a36e600beba82f1360. Rework commits in scope: T078 2e2bd536 (architect.css + ProposalOutlineDraw/Map.tsx + 3 specs + report — no forbidden file), T079 912aa8d2 (MaxEnvelopePanel.tsx, max-envelope-api.ts, 2 specs, report — entry.test/e2e untouched).

EXECUTED EVIDENCE: CI at 6c79cd88 (gh check-runs, job-level; my guard blocks --log): `web (lint+typecheck+build)` = success, `web-e2e (vitest + Playwright)` = success. So every asserted literal matches source and all specs pass at HEAD.

M5-T078 — prior blocking F1–F3, each traced red on the literal pre-fix:

| Finding | New spec | Reddens pre-fix because |
|---|---|---|
| F1 (F7 too-few arm) | draw:443 | too-few arm, 2 finite + 1 lng-only row: `toBe("…1 row still needs a latitude — …(2 of 3 ready).")` + `not "longitude and latitude"`. Blanket revert (S1) → :452/:453/:454 red. |
| F2 (untyped-sel honesty) | map:431 it.each (5 FALLBACK_STATES + loading) | untyped-sel status `toBe("…; type its longitude and latitude in the table.")`; status+instructions `not /click/i`. Ungated ":227 map-click" clause → :449–453 red in all 6 variants. Also catches S3 (readiness gated `!=="unknown"`) at :441. |
| F3 (single predicate) | source + grep | src:326 `rowComplete = isDrawnPointFinite(p)`; my own multiline pair-check grep over architect/ = exactly ONE hit (ProposalOutlineMap:60, the predicate). Draw uses only single-ordinate checks, feeding aria-invalid. |

Source confirms sensitivity: convertHintCopy:75-98 builds F1 via the shared missingOrdinateLabel; selectionSentence:222-228 gates the map-click clause on `mapSurface==="present"`; rowComplete is the shared predicate (per-ordinate lngFinite/latFinite feed only aria-invalid).

F3 note: disclosed grep-only — the pre-fix `lngFinite && latFinite` is byte-equivalent, so no runtime mutant discriminates; the teeth are structural. ADVISORY: no committed source-scan test pins the single-predicate invariant (a CRS-wall-style test could); non-blocking, matches the prior reviewer's own framing.

(part 2 next)

---

M5-T078/T079 G4 RE-REVIEW — part 2/4: M5-T078 survivors, fresh mutants, verdict.

Prior-survivor re-run (S1–S7):
- S1 → CAUGHT (draw:443).
- S2 (untyped sel while not "present") → CAUGHT (map:431 fallback + present-case map:500/:507).
- S3 (readiness `!=="unknown"`) → CAUGHT (map:441).
- S4 (drop `&& !converting`) → CAUGHT (draw:580 deferred-fetch; :596 one fetch, :598 "already in progress").
- S7 (omitted count set only >0) → SURVIVES; advisory (no double-convert / zero-omitted spec).

Requested specs — refusal-card / fallback-status / too-few:
- Refusal card (draw:531 it.each 422 out_of_neighborhood + 404 feature_unavailable; draw:610 retry): card text = `announcementForOutlineBridge(outcome)` (src:464), decoupled from the announcer (src:278). A blocked press writes only the announcer; :574 `toBe(cardText)` + :575 `not "Add 1 more point"` redden the pre-fix `<p>{announcement}</p>`. Non-vacuous (spec first waits for the announcer to change at :567, then asserts the card did NOT). CAUGHT.
- Fallback status (map:431) — CAUGHT (part 1).
- Too-few arm (draw:443) — CAUGHT (part 1).

Three fresh idiomatic weakenings:
1. Swap selectionSentence present/absent branches → present+untyped status flips → map:507 exact `toBe` red. CAUGHT.
2. Drop the `every(l===l[0])` shared-label guard (always use the first label) → a MIX of differently-incomplete rows would mislabel; no hint spec feeds heterogeneous incomplete rows → SURVIVES. ADVISORY.
3. Post-convert counts clause `omittedOnConvert > 0` → `>= 0` (always append) → a zero-omitted convert (draw:189) never asserts the clause is ABSENT → SURVIVES. ADVISORY (= prior A4).

Vacuity: every new T078 assertion is a hardcoded literal (omissionHint/reason are local string consts, not imported) — no by-value tautology. AS-3 whole-section live-region count (draw:501, baseline 2) catches S6; A5 lot-outline Set-equality (lot:550) keeps "only" while tolerating a rebuild; DB-048 presence teeth intact (lot:591 uses `.some(...id===)`, not a tally).

All residual survivors are advisory (A-class); no blocking finding remains open.

M5-T078 G4 VERDICT (rework): PASS

(part 3 next)

---

M5-T078/T079 G4 RE-REVIEW — part 3/4: M5-T079 F1–F2 closure + raw-presence + fake timers.

| Finding | New spec | Reddens pre-fix because |
|---|---|---|
| F1 (AS-1 typed cards) | panel:665 it.each (413 payload_too_large, 422 invalid_request); panel:673 client_timeout | first `<p>` textContent `toBe` the exact literal reason (src announcementForMaxEnvelope:708-724; card `<p>` = announcement, src:329); Retry presence hardcoded AND cross-checked vs `maxEnvelopeOutcomeIsRecoverable`. Mutant 14 (announcement "" for these kinds) → :668/:684 red. |
| F2 (aborted guard, DB-050(c)) | panel:599 MutationObserver | trace below. |

F2 trace (the subtle one): the null branch does NOT bump activeRef (src:270-277), so the FIRST request's `aborted` result passes the token guard (:282) and reaches the guard (:289). Delete `if(result.kind==="aborted") return;` → the re-set's FIRST render commit renders a reasonless `envelope-failure` (`outcome` truthy, effect has not yet set loading); `takeRecords()` captures that transient add → :626 `expect(failureCommitted).toBe(false)` red. With the guard `outcome` stays null → no card ever committed. Rests on deterministic React commit-before-passive-effect ordering; non-vacuous, and CI-green confirms the with-guard pass. OPTIONAL confirmatory executed mutant (delete src:289, run max-envelope-panel) available if you want belt-and-suspenders — my verdict does not require it.

Fake timers (asked): panel:673 = `vi.useFakeTimers()` + `act(advanceTimersByTimeAsync(DEFAULT_TIMEOUT_MS))` + synchronous `getByTestId` (findBy would not advance fake timers) + `useRealTimers` in the describe afterEach. Correct.

Raw-presence XOR table (asked): classify runs on raw-presence flags (boundDimension:354-355, `!==null && !==undefined`, deliberately not truthiness):
- panel:455 value + malformed gap ("", " ", 7, {}) → BOTH; no value testid; `not "20000"`.
- panel:483 single unusable field → "unreadable", never "neither".
- panel:499 binding_value 0 → VALUE row (two-mutant falsy rule — my memory).
- api:590 13-row raw table through the REAL decode; api:601 classify, :602 completeness cross-check.
Classify-on-bounded (mutant 1) → panel:455/api:590 red; truthiness presence (mutant 5) → panel:499/api:515 red; "neither" for unreadable (mutant 6) → panel:494 red.

(part 4 next)

---

M5-T078/T079 G4 RE-REVIEW — part 4/4: M5-T079 survivors, fresh mutants, verdict.

Prior-survivor re-run (5,6,8,10,13,14,19):
- 5 (value leaks into violation branch) → CAUGHT (panel:408 `not "20000"` on the BOTH row).
- 6 (truthy classifier withholds a real 0) → CAUGHT (panel:499, api:515).
- 8 (banned phrase split across JSX {" "} / "a"+"b") → SURVIVES — the claim wall scans SOURCE text; a {" "}-split evades the normalize. Standing advisory (producer "Not closed" A3); non-blocking, never a prior blocking finding.
- 10 (gap copy reworded, no literal pin) → CAUGHT (panel:374 GAP_COPY_LITERALS hardcoded + rendered).
- 13 (aborted guard) → CAUGHT (panel:599).
- 14 (announcement "" for typed kinds) → CAUGHT (panel:665/673).
- 19 (seed "narrow") → CAUGHT (panel:236 `draft.street_width_class).toBe("")`).

Three fresh idiomatic weakenings:
1. classify:612 drop the binding-usability check (always `value`) → a string `binding_value "20000"` alone renders "null ft" → panel:483/api:590 red. CAUGHT.
2. aggregate `notShown > 0` → `>= 0` (reintroduce "Could not check 0 of") → api:664 advisory-only exact line red. CAUGHT.
3. boundDimension:354 treat JSON `null` as present (`!==undefined` only) → a gap-only row misclassifies as BOTH → api:590 "gap only" row red. CAUGHT.

Vacuity: gap-copy pinned as hardcoded literals (panel:374 — honors the M5-T081 by-value lesson); reason strings + aggregate lines hardcoded; Retry tied to the predicate. The lone by-value compare (panel:360 `gapReasonCopy(token).toBe(GAP_REASON_COPY[token])`) is backstopped by the hardcoded literals at panel:374 — acceptable. CRS-marker wall (api:686) comment-safe; gap-vocab mirror intact.

Only survivor 8 remains, advisory. No blocking finding open. The raw-presence table, the three AS-1 cards (fake timers correct), and the MutationObserver aborted-guard spec each fail on their target pre-fix.

M5-T079 G4 VERDICT (rework): PASS

END-OF-REPORT
