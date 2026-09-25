# M5-T115 — directive-compliance verification (directive-compliance-verifier "dcv-t115", read-only)

> Transmission history: pinned at a054ccf4, delivered as four SendMessage parts (1/4..4/4) ending with END-OF-REPORT;
> no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed only). Part 1 carries the
> blob-level restamp predicate (19 blobs + identity 70ed25ba) with broad disjoint-peer tolerance.

---

M5-T115 DCV Part 1/4 — READ-ONLY (dcv-t115). PIN: HEAD a054ccf4 at start (git rev-parse HEAD).

RESTAMP PRE-AUTHORIZATION (up front):
- Blob-level predicate: this PASS holds at any accept HEAD where _task_git_identity(dr, M5-T115) == 70ed25ba2dd8adb47b249cd76981936ecef3416e45e7faae1fae091dcf007bd8 AND all 19 allowed-path blobs equal — AddressResolutionScreen 1cd66f0f, AddressForm 2f0af0a3, SuggestionChooser 3dc70161, AddressOutcomeCards f7126347, AddressConfirmCard 4e139d5f, LotOutlineMap 6c5d0fe8, address-resolution.test 29ee3626, address-confirm.test a574ff92, lot-outline-map.test 535f7b27, AddressAutocomplete 53e44e55, ArchitectEntry 39979587, autocomplete.test 4ad628c5, entry.test 46eb31b5, architect.css d917ab02, confirm-journey.spec 30ed69f8, lot-outline.spec 60798f12, a11y-announcements.spec 3402bad2, responsive-a11y.spec 3a02a6b4, producer-report c8b11889 — AND evaluate_task_refs stays ok with applicable==cited=={D-066-R001, D-083-R001, D-086-R001/2/3/4, D-087-R001/2}. All 19 blobs reproduced == this list at HEAD.
- Disjoint-peer tolerance (broad): I accept without re-review any peer change leaving the predicate intact — other tasks' files/gates/material (M5-T116/117/118 + new packets), other directives' registry binds, the orchestrator appending MY verification rows to the D-066/D-083/D-086/D-087 verification.json with digest resyncs + audit entries, DISCOVERY_BACKLOG rows/sweep lines, and lifecycle-only packet changes.

MECHANICAL (reproduced myself):
- evaluate_task_refs(task): ok=True; applicable_ids == cited_ids == the 8 ids above; missing=[], invalid_refs=[], unresolved=[]. Applicable == cited.
- _task_git_identity at HEAD a054ccf4 = 70ed25ba… (err None) == reports/M5-T115.json content_manifest_sha256 == the G2/G3/G4 stamps (all 70ed25ba). G0 stamp ee98086f is the pre-material contract-seam manifest (expected different).
- Gates: G0 PASS (orchestrator/administrative @6a712652), G2 PASS (orchestrator/self_check — the producer's self-check; CLI rejects the producer's own name), G3 PASS (code-reviewer/independent @ba48acad), G4 PASS (qa-engineer/independent @ba48acad); human-journey PASS (M5-T115-HJ.md). Independent reviews (G3/G4) are by non-producers; NONE of the four gates was recorded by the producer frontend-engineer. All required gates present + PASS.

END PART 1/4.

---

M5-T115 DCV Part 2/4 — requirement rows (primary evidence reproduced).

D-066-R001 (navigation block) — SATISFIED. tasks/M5-T115.json input line 19 carries the graph-derived navigation block (graph regenerated at the wave-1 seam; 844 files/18356 nodes/7841 edges), names the live flow (ArchitectEntry PropertySearch → AddressAutocomplete/AddressResolutionScreen → AddressConfirmCard → LotOutlineMap), marks PropertyOverview.tsx READ-ONLY, and instructs `python tools/code_graph/query.py --no-regen impact <path>` before sweeps, "graph ADVISORY — verify in actual source." M5-T115-G0.md:30-31 corroborates. Obligation (block present + prompt cites query.py --no-regen) met.

D-083-R001 (no permitted/approved/max-allowed; new strings honest) — SATISFIED. Diff 75c03f25 adds only 5 new user-visible strings: "Internal build"; the env note ("No sign-in or access control yet, the official data shown is unreviewed, and nothing here is a legal determination — do not share…"); the BBL-alternative note; "Preliminary analysis — professional review required before any reliance."; "City-matched address" (ArchitectEntry.tsx:76-100; AddressConfirmCard.tsx:195-199). None assert permission/approval/maximum. `git grep -iE 'permitted|approved|maximum allowed'` on the 8 touched blobs → one pre-existing hit only, AddressConfirmCard.tsx:429, a code comment describing a layout-test fixture ("a long permitted record address"), NOT added by M5-T115, not product copy, not a claim-class term. M5-T115 surfaces no max-envelope numbers. G3 + HJ independently confirm no such wording.

D-086-R001 (assessment = input, not authorization) — SATISFIED. LF-normalized sha256 of docs/UI_DEEP_DIVE_ASSESSMENT.md = c6d1b25779c2dd3fb4699d6a99ca50d9695d82f7afc05986fe58de5cf8504b84 == the digest pinned in D-086-R001 (re-verifiable, byte-exact). Ledger id M5-T115 is orchestrator-assigned; the diff lifts no hold (.claude/ in forbidden_paths; no hold file/assessment edit), launches no expansion pack, releases no capability. MR-1..MR-8 not adopted (producer report §0/§3; HJ line 56).

D-086-R002 (P2 contracted + gated; honest P2-row match) — SATISFIED. Assessment §14 P2 row (line 1158) exit gate = "G0/G2/G3/G4" + the scenario list; packet required_gates=[G0,G2,G3,G4] (exact) + human-journey walkthrough (M5-T115-HJ.md PASS). Sequenced after P1: packet dependencies=["M5-T114"]; D-086 verification.json shows P0 (M5-T080) + P1 (M5-T114) PASS. Delivered slice honestly matches the P2 row — scope (address/confirm/autocomplete + route styles/tests; no-guess matching, raw-warning placement, optional record-address unchanged) matches allowed_paths + objective; all 9 P2 exit-gate scenarios covered by real property-asserting tests green in CI (G4 map). The producer's re-cite-vs-new split is the correct reading under the R003 preservation mandate; HJ-4 (scope calibration) is an expectation note, not a compliance failure.

END PART 2/4.

---

M5-T115 DCV Part 3/4 — requirement rows.

D-086-R003 (preservation) — SATISFIED. Diff is additive: git show 75c03f25 = +428/−6 over 8 files; the 6 "deletions" are in-place attribute-augmenting line rewrites in ArchitectEntry.tsx that PRESERVE id="architect-bbl-error", role="status", aria-describedby, the card/architect-disclosure classes, {error}, and the matched line (G3/G4 confirm). Verified myself: (1) §29 only via REQUIRED_DISCLAIMER — disclaimer.ts is forbidden lib/, untouched; env note is a different string, unit-asserted NOT to contain the §29 opening (entry.test). (2) City warnings verbatim ABOVE Continue — AddressConfirmCard change is only the +12 label at ~:185; warnings block/Continue untouched (HJ: warnings :248-269 above Continue :389; unit S1 asserts DOM order). (3) No presentation-layer math — the 5 new strings are static; no number added. (4) No status remap — data-record-address-status pre-existing, untouched. (5) Env note faithfully carries the InternalBanner meaning (I compared property/InternalBanner.tsx: internal-build / no-access-control / unreviewed-official-data / not-a-legal-determination / do-not-share all preserved) — additive, no removal/conversion, so no new migration row required; producer §3 ledger-proof table present. (6) Expansion hold / D-040/D-076/D-082 / unmounted max-envelope route / PR #241 / phase C-D unchanged (web presentation only; G0 "max-envelope route stays UNMOUNTED"; PR #241 verified OPEN/unmerged). (7) Both meaning-survival AND visibility proofs exist — env badge visible at 360/768/1280 (responsive-a11y e2e green; G4 mutant: a display:none reddens at phone-360) + meaning tests (§29-negative, four bbl.ts verbatim, City-matched label, CTA byte-stability).

D-086-R004 (sequencing) — SATISFIED. Contracted at the D-089 wave-2 seam 6a712652 (seq 130) after accepted P0 (M5-T080, R001-R004 PASS) and P1 (M5-T114, verified); packet dependency=["M5-T114"]. M5-T080 DCV records its seam after accepts #255-#259 and the D-085 Opus 5.5 restart.

D-087-R001 (capacity; normal gated packet) — SATISFIED. G0 @6a712652 (gate record reviewed_sha matches); claimed @01856916 with the FULL worktree path (packet.worktree = C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t115); orchestrator-dispatched subagent (G0 authority note; D-089 loop lanes wait for B-026); gates G0/G2/G3/G4 all PASS; no state/gate skipped (backlog→claimed→in_progress→awaiting_gate). Both seams are ancestors of HEAD.

D-087-R002 (no interference) — SATISFIED. G0 disjointness table: every active neighbor EMPTY overlap except M4-T005 (declared-glob overlap on apps/web/src/app/property/** + apps/web/e2e/**), correctly EXCLUDED as dormant pre-regime. Verified on primary evidence: M4-T005 directive_refs=None (pre-regime), reports/M4-T005.json does NOT exist (no frozen identity), last change 077a3316 = 2026-07-22 (no live writer) — so neither a live nor a frozen writer; the interference hazard the rule guards cannot occur. This is the M5-T077 DCV F1 ruling applied (recorded in M5-T077-DCV: D-087-R002 SATISFIED, dormant-pre-regime = advisory), NOT a waiver. One worktree wt-m5t115; the commit touches exactly 8 of 19 allowed paths, all in-scope, no forbidden path.

END PART 3/4.

---

M5-T115 DCV Part 4/4 — sweep, CI, findings, harness, verdict.

PROHIBITED-ACTION SWEEP (clean): not accepted (status awaiting_gate); no verification row yet (D-086 verification.json holds only M5-T080 + M5-T114; D-083/D-066/D-087 have no verification.json yet); not on main (75c03f25 is NOT an ancestor of origin/main); PR #241 OPEN/unmerged/untouched (headRef task/M5-T002…, mergedAt null) and no PR exists for the M5-T115 branch; no open blocker names M5-T115 (grep of blockers/ = none); zero new dependencies (G0). Nothing merged/accepted/dispatched-to-PR/deployed/installed/purchased/closed for this task.

CI (read-only gh): run 36102902944 = success, headSha bfefd934, event push, workflow "CI"; the three reviewers verified material 75c03f25 byte-identical to bfefd934 (1468 vitest + 124 Playwright + control-plane + modularity green). ba48acad (the G3/G4 head) also CI-green (36103657696). Latest pushed head 7bed25c0 is a descendant of HEAD a054ccf4 and NONE of the 19 allowed paths differ between them — the reviewed identity is byte-unchanged at the pushed head; that head's "CI" run is in_progress on disjoint peer work only.

FINDINGS (all advisory; none undercuts a cited requirement):
- F1 (report accuracy; = HJ-2 / G4-ADVISORY-3): producer report §2/§3 says "map CSS polish" but architect.css has no map selector — actual scope is narrower than described; no map regression, no requirement affected.
- F2 (test adequacy; = G4-ADVISORY-1): the new entry.test asserts aria-invalid only negatively (absent-when-valid), so a "drop the errored aria-invalid" mutant survives. aria-invalid is additive (not a cited requirement); the exit-gate behaviour (four distinct BBL errors, announced via the PRESERVED role=status) IS proven. Recommend adding the positive assertion as follow-up.
- F3 (= G3-A1 / HJ-3, producer OQ-2/OQ-3): env note paraphrases InternalBanner (drift risk) and yields two role=note at ≥768px — meaning preserved and ARIA-legal; consolidation for a later shell-scoped slice.

HARNESS: evaluate_task_refs ok, reproduced (it flags any cited-directive integrity error as invalid_refs — none, so D-066/D-083/D-086/D-087 loaded clean). `python tools/validate_directive_compliance.py --check` (direct exit code, no pipe) → exit 0, no output (clean; source digests match, c14/locked-ids intact). CI's control-plane job additionally ran green at the reviewed head bfefd934. I did NOT run tools/test_directive_compliance.py (prohibited).

All 8 applicable requirements SATISFIED on reproduced primary evidence; frozen identity intact at HEAD; all required gates PASS by non-producers; sweep clean.

M5-T115 DCV VERDICT: PASS 8/8
END-OF-REPORT
