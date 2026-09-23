# M5-T070 — G3 DELTA attestation (VERBATIM, two-part transmission)

TRANSMISSION HISTORY (orchestrator note, not reviewer text): delivered 2026-09-23 in two
parts (05:33:48Z head; 05:33:59Z the closing fragment joined at "the orchestrator-captured
execution "). Supplements the wave-1 FAIL report (M5-T070-G3.md); together they are the full
G3 record. The reviewer's own text follows, unedited.

---

All four of my blocking findings are closed at this identity. Here is the delta attestation.

## M5-T070 G3 delta attestation — corrected identity

**Identity (verified independently, not accepted on assertion).** All twelve packet files are byte-identical between the resubmit-seam head `395d6727` and the live head `75e14da4`, by git blob SHA. `0625c19b` is an ancestor of `395d6727`, which is an ancestor of HEAD. The three commits after `395d6727` (`197454b4`, `1c468f11`, `75e14da4`) touch no packet path — proven by the twelve MATCH rows, not by reading their messages. The working tree is clean for every packet path. Five of the twelve blobs moved from my wave-1 review and seven are unchanged; the five that moved are exactly the five files `0625c19b` touches.

**Correction scope.** `0625c19b` changes eight files: the five packet files above plus `docs/DISCOVERY_BACKLOG.md`, the evidence map, and the producer report. No production file outside `MaxEnvelopePanel.tsx` was touched, no forbidden path, no dependency change.

**F1 — CLOSED.** Both `no_fit` fixtures now carry `footprint_exceeds_lot`, a real `CandidatePlacementStatus` member (max_envelope.py:168). `grep -rn '"no_fit"' apps/web/` returns nothing. All seven remaining placement-status literals in the web app are real enum values.

**F2 — CLOSED, and closed better than I asked.** The new spec at `max-envelope-panel.test.tsx:203-222` pins the production-reachable state: `candidate: null` plus `status: "lot_geometry_unsupported"`, and the `SERVER_DETAIL` string it asserts is byte-identical to the server's own prose at max_envelope.py:632-637 — I compared it against the source I read in wave 1, not against the comment claiming it. The test asserts the honest card leads with that prose and that `adopt-candidate` is absent. The producer report now carries a named AS-4 limitation section stating plainly that the adopt affordance "CANNOT appear against the real route as currently wired" and that every fitted-candidate fixture models future behavior; the evidence map carries the same under D-082-R001; DB-050(a) records the geometry-threading seam as its own pre-mount packet and correctly identifies server-side derivation from the accepted MapPLUTO connector by BBL as the right design rather than client-sent geometry. The silent over-claim is gone and the dead-affordance risk is now guarded by a committed spec.

**F3 — CLOSED.** All four fixtures carry `allowance_unresolved`; no prose `gap_reason` remains anywhere in `apps/web`. `GAP_REASON_COPY` (MaxEnvelopePanel.tsx:54-65) maps exactly the four real `EnvelopeGapReason` members with no invented fifth key, and `gapReasonCopy` falls back to rendering an unrecognized token verbatim — fail-honest, never fabricated copy. The client still exposes the raw token (`max-envelope-api.test.ts:195` asserts `gapReason === "allowance_unresolved"`), so transport stays verbatim and the mapping is presentation-only, which is the right separation. The panel spec asserts both the mapped copy and `not.toHaveTextContent("allowance_unresolved")` on the headline element — that second assertion is what gives the fix teeth, and it is scoped to the gap-reason span so the server's `detail` below is unaffected.

**F4 — CLOSED.** The AS-2 wall now greps all five changed production files, `ArchitectEntry.tsx` and `ProposalEditor.tsx` included. The new `GAP_REASON_COPY` strings introduce no banned phrasing and sit inside the wall's own scope.

**Residuals, all non-blocking and already recorded.** `gapReasonCopy`'s `token === null` branch is unreachable, since `isGap` requires a non-null reason; harmless defensive code. My eight wave-1 advisories are carried verbatim into DB-050(b)-(m) alongside G4's, including the copy-wall hyphenation seam and the new item (m) to keep the token map in sync if `EnvelopeGapReason` grows — which is the right standing guard for the map I just approved. CI run 35822387368 SUCCESS at `395d6727` is the orchestrator-captured execution evidence, and per the evidence-capture division I verify the stored pin rather than re-running it, and the identity chain above ties it to the code I read.

Nothing was weakened to pass. Each fix moves the fixtures toward the server contract rather than loosening an assertion, and the one production change adds honest copy with a fail-open-to-truth fallback.

**ATTESTED-PASS** — my wave-1 FAIL clears at identity `395d6727` / HEAD `75e14da4`. F1-F4 closed with verified evidence; advisories remain open as DB-050 riders and block nothing.

END-OF-REPORT
