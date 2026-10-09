# M5-T078 + M5-T079 — G3 re-review after the reworks (code-reviewer "cr-web2", read-only; fresh reviewer; joint)

> Transmission history: one joint re-review pinned at 6c79cd88 (rework commits 2e2bd536 / 912aa8d2 verified as
> ancestors with all 12 material blobs byte-identical at HEAD), delivered as three SendMessage parts (1/3..3/3)
> ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed
> only); saved identically as M5-T078-G3-rework.md and M5-T079-G3-rework.md. A FRESH reviewer on the pinned
> Opus 4.8 model (the first-pass cr-web ran on Opus 5.5 - see the D-085 deviation report). Verdicts: both PASS.
> CI proof cited: run 35989704760 at 6c79cd88 (web + web-e2e SUCCESS).

---

G3 RE-REVIEW (code-reviewer, read-only) of M5-T078 + M5-T079 reworks — part 1/3.

PIN: HEAD `6c79cd88b519d2df5ad605a36e600beba82f1360`, branch candidate/D-024-mrl-option-b.

IDENTITY (checked myself with git):
- 2e2bd536 (T078 rework) and 912aa8d2 (T079 rework) are BOTH ancestors of HEAD (git merge-base --is-ancestor, exit 0).
- `git diff <rework>..6c79cd88` over every one of T078's 6 source/test files and T079's 6 is EMPTY — all 12 material blobs are byte-identical at the rework commit and at HEAD. So CI at HEAD proves exactly the code I read.

CI (gh run view 35989704760, headSha 6c79cd88, read-only):
- **web (lint + typecheck + build): SUCCESS**
- **web-e2e (vitest + Playwright): SUCCESS**
- The run is still `in_progress` ONLY because of `supervisor-bridge` (unrelated pytest); every web-relevant job is completed success (also secret-scan, context-budget, modularity, contracts, api all success). The two jobs that prove these packets are already green.

SCOPE:
- T078 rework touches exactly its 7 allowed_paths (ProposalOutlineDraw.tsx, ProposalOutlineMap.tsx, their 2 specs, lot-outline-map.test.tsx, architect.css — added to allowed_paths for the scope correction — and the producer report). No forbidden neighbour (ProposalEditor.tsx, LotOutlineMap.tsx, outline-bridge-api.ts, proposal-editor.test.tsx, entry.test.tsx, e2e) edited; no package.json/lockfile; services/api untouched.
- T079 rework touches 5 of its 7 allowed_paths (MaxEnvelopePanel.tsx, max-envelope-api.ts, their 2 specs, report). entry.test.tsx and e2e/proposal-editor.spec.ts were done in v1 and are unchanged by the rework (byte-identical). services/api untouched; route still UNMOUNTED.

Not run (thin client / rules): npm, npx, node, vitest, playwright, test_directive_compliance.py, project_control.py, no git/gh write verbs. Code-graph impact not consulted (grep + direct Read sweep sufficed).

Findings per task follow in parts 2 and 3.

---

Part 2/3 — M5-T078 (drawing-surface disclosure + accessibility).

EARLIER BLOCKING FINDINGS — all closed:

F1 (blocked press overwrote the refusal card; = HJ-1) CLOSED. The card body now derives from the outcome alone: ProposalOutlineDraw.tsx:464 `<p>{announcementForOutlineBridge(outcome)}</p>`. `outcome` is set ONLY in convert() (:246); a blocked press writes only the announcer (:266/:269) and makes no bridge call. Spec teeth: proposal-outline-draw.test.tsx:531 it.each over 422 out_of_neighborhood AND 404 feature_unavailable (the production-reachable path) — refusal, delete a point, blocked press → card textContent byte-unchanged (:574 toBe(cardText)), not containing "Add 1 more point" (:575), fetch still 1 call, onAdopt never called; :610 covers the pending-retry case (card unchanged, :633). Pins the exact leak.

F2 (status/instruction clauses promised map gestures that don't exist) CLOSED. Every clause is now gated on the same mapSurface × selection × selectedIsFinite state (ProposalOutlineMap.tsx:206-246): (i) the "a map click will place it" status clause is gated on `mapSurface === "present"` (:227), else keyboard wording (:228); (ii) readiness gated on `readyApplicable = mapSurface === "present" && !hasSelection` (:236), never appended while a click would MOVE a selected point; (iii) untyped-selection instruction (:214) replaced "Click the point again to deselect" with "Use its Deselect button in the table". Spec teeth: proposal-outline-map.test.tsx:431 it.each over all 5 FALLBACK_STATES + loading (exact status, no "click", no readiness), :457 (finite selection: no readiness), :500/:512 (untyped/half-typed exact wording). FALLBACK_STATES keys to the leaf's REAL fallback testids.

F3 (duplicate split-line pair predicate) CLOSED. ProposalOutlineDraw.tsx:326 `const rowComplete = isDrawnPointFinite(p);`; the per-ordinate booleans (:328-329) now feed ONLY aria-invalid (:345/:354). The old local pair predicate is gone. Structural fix; grep teeth only (semantically identical today), which is appropriate for a de-duplication.

CSS scope correction: architect.css:45 adds exactly ONE selector — `,.architect-shell button[aria-disabled="true"]` — to the existing `button:disabled` rule; no other CSS line changed. Verified the only other aria-disabled in web source is on a `<Link>`/`<a>` (ArchitectShell.tsx:34), which a `button[...]` selector cannot match, and the only aria-disabled button is Convert (:400). No over-reach.

No regression / no disclosure weakened: honesty paragraph, provenance dl, refusal heading, post-convert counts all intact (producer copy table R1-R11 meaning-preserving); web + web-e2e green means every migrated (disabled→aria-disabled) and pre-existing spec passes.

NEW defects introduced by the rework: none found. The setState-during-render readiness machine (ProposalOutlineMap.tsx:238-246) converges (each branch advances phase or resets on surface change); no render loop.

ADVISORY (non-blocking, carried): G3-A4 second half (link each aria-invalid input to its row marker) and HJ-8 (fresh row aria-invalid) not done — both advisory, disclosed by the producer.

M5-T078 G3 VERDICT (rework): PASS

T079 in part 3.

---

Part 3/3 — M5-T079 (max-surface hardening).

EARLIER BLOCKING FINDINGS — both closed:

F1 (XOR leak on a blank/non-string gap_reason) CLOSED. Raw presence is now recorded BEFORE bounding: max-envelope-api.ts:354-355 `bindingValuePresent`/`gapReasonPresent` use `!== null && !== undefined` (not truthiness, so binding_value 0 is present; "", " ", 7, {} gap_reason is present). classifyDimensionRow (:606-615) runs the XOR on those RAW flags: both present → contract_violation "both"; neither → "neither"; one present but bounded-to-null → "unreadable"; only a present-AND-usable single field is value/gap. So a value beside a blank/non-string gap_reason is contract_violation, never value. Panel renders envelope-contract-violation-<id> and NEVER a value (MaxEnvelopePanel.tsx:121-128). Spec teeth: panel :455 (value + ""/" "/7/{} → withheld BOTH, no "20000", never complete), :483 (blank/non-string alone → "no usable value or reason", never "neither", no "null"), :499 (binding_value 0 → value row); api :590/:605/:515. envelopeAggregateIsComplete (:628-636) also fails on any gap ROW or violation (G3-A1 folded in).

F2 (AS-1 panel cards, boundCandidate rejects, aborted guard untested) CLOSED on all three sub-parts:
- Panel failure cards now tested: max-envelope-panel.test.tsx:665 it.each (payload_too_large 413, invalid_request 422 — exact literal `<p>` reason + Retry presence cross-checked with maxEnvelopeOutcomeIsRecoverable), :673 client_timeout (fake timers, exact literal, Retry present, loading gone).
- boundCandidate non-srid rejects: max-envelope-api.test.ts:337 it.each — 13 probes across vertices/levels/walls, each asserts candidate === null AND candidateIsAdoptable false, plus a control (:358) that a valid candidate survives. Superset of the 7 branches the finding named.
- Aborted guard now has a killing spec: panel :599 renders REQUEST (abort-honoring pending fetch) → rerender null → flush → MutationObserver on the container → rerender REQ2 → takeRecords() asserts no envelope-failure node was committed. MUTATION: deleting `if (result.kind === "aborted") return;` (MaxEnvelopePanel.tsx:289) reddens it. This is exactly the observable the earlier finding said existed.

A2 deliberate non-implementation (bump the token on request→null) — reasoning is SOUND. The .then checks the token (:282) BEFORE the aborted guard (:289). Bumping the token in the null branch would drop the late result at the token check first, making the aborted guard an EQUIVALENT MUTANT — which directly contradicts the blocking F2(3) requirement for a spec that FAILS without the guard. The two cannot both hold; the producer correctly kept the blocking guard load-bearing and routed the A2 residual to D5. The residual (a fetch that IGNORES its abort signal storing state after null) needs a signal-ignoring stub — unreachable in production (route unmounted; real fetch honors abort) — and is honestly disclosed. Advisory, not blocking. Correct call.

No regression / no disclosure weakened: D-083 strings ("Preliminary development limits", "Generated building option", "not a maximum permitted building") intact; adoption seed byte-identical; copy changes (R1-R7) meaning-preserving. web + web-e2e green.

NEW defects introduced by the rework: none found.

M5-T078 G3 VERDICT (rework): PASS
M5-T079 G3 VERDICT (rework): PASS

END-OF-REPORT
