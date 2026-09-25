# M0-T161 — G3 DELTA re-review, required-corrections round 2 (code-reviewer "cr-m0t161", read-only, static)

> Transmission history: pinned at 0c76b136 (delta = 158b5bca, identity 82864416), delivered as three SendMessage parts
> (1/3..3/3) ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed
> only). Verdict PASS: F1-F5 and the G5 advisories closed; the new assertion strings verified against the real update
> script output (no false-STOP); the owner guide correct end to end, its STOP quote byte-exact to the script.

---

M0-T161 G3 DELTA re-review — PART 1/3

PIN: HEAD 0c76b136 (matches). reviewed_sha 158b5bca; I confirmed `git diff 158b5bca..HEAD` for all 4 files is EMPTY, so the working tree I reviewed == the frozen submission. Static review (sandbox blocks powershell.exe). Nothing loosened vs round 1; every change is a stricter check, an owner-guide fix, a test, or the Write-WrapperFile seam.

F1 CLOSED — and the new assertions match the REAL update-script output (I read update_controller_from_candidate.ps1 to prevent a false-STOP regression):
- Install prints (L697-700): "INSTALLED from immutable commit <sha>" / "commit tree <82432361…>" / "subtree tree <9c0b14ea…>" / "files 204 byte-identical source-to-destination". Helper now also asserts CandidateTree (L436) and `\b204\s+byte-identical` (L440) — both present in that output, so no false STOP.
- Verify-manifest prints (L790-791): "MANIFEST VERIFIED against the accepted source at <sha>" / "covered files 146; installed files re-compared 204". Helper now asserts the full "…at a3f24ff3…" (L490), "covered files 146" (L495) and "installed files re-compared 204" (L499) — all exact substrings of the real output. binding.commit_sha == the candidate is gated by the check phase, so the "…at <sha>" assertion cannot false-STOP on a healthy run.
- Dead pins are now LIVE: CandidateTree 4 occ (was 1), InstalledFileCount 9 (was 1), CoveredFileCount 4 (was 1). ConfigLfHash is correctly removed and replaced by a comment (L82-85) explaining it is covered transitively by the 5.4 manifest digest STOP + 5.7 verify-controller — the right call, since it was never load-bearing.

CRUCIALLY, no false-STOP regression is also PROVEN by the tests: test 10 runs a full good-output update (Get-GoodInstallStdout + a good verify-manifest stub carrying "covered files 146; installed files re-compared 204") all the way THROUGH Step-Install and Step-VerifyManifest without stopping, only tripping the immutability guard at the end. So the added assertions pass on healthy output.

Continued in part 2.

---

M0-T161 G3 DELTA — PART 2/3

F4 CLOSED: every throw now begins "STOP …". The four previously-unprefixed wrapper throws are fixed — New-LaneWrapperContent L622/L627 and Set-NotYetFedBlock L652/L661 all now "STOP [update 5.6]:". I re-scanned all throws in the file; the only non-"[phase step]" ones are the generic Invoke-Ext no-exit-code (L147, still "STOP:") and the dispatcher default (L1032) — both correct.

G5 CLOSED:
- robocopy /MIR source precondition (Step-Propagate L523-532): Get-TreeFileCount on the certified source must == 204 BEFORE any /MIR; else STOP "[update 5.6]… refusing to robocopy /MIR from a missing or wrong source". This prevents a /MIR from an empty/missing source deleting lanes 2-5. Get-TreeFileCount returns -1 when absent (→ STOP). On a healthy run the freshly-installed subtree is exactly 204 (install proved "nothing extra"), so no false-STOP. Proven by test 6 (count 3 → STOP before any robocopy).
- Rollback pointers now on the 5.3/5.5/5.6/5.7/5.8/5.9 STOPs ("roll back per runbook section 10"), joining the existing 5.4 one. ✓

F3 + plan-validator hardening (Assert-ValidLanePlan L864-963):
- Glob-aware overlap: Get-NormPathBase (L965-975) strips a trailing /** or /* to the directory it covers (the SAFE over-approximating direction); Get-PathOverlap (L977-993) then does equal/ancestor on the normalized prefixes. So "services/api/**" now correctly overlaps "services/api/app/x.py". Proven by test 11 (glob overlap REFUSED; glob-disjoint apps/web/** ACCEPTED).
- Linked-worktree ROOT check (L901-924): --show-toplevel must equal the given path (rejects a subdirectory) AND --absolute-git-dir must differ from --git-common-dir (rejects the primary checkout, whose two are equal). Real linked worktrees pass (git-dir=.git/worktrees/<name> ≠ common .git); the primary is refused. Resolve-PathKey normalizes both sides. Proven by test 11 (primary REFUSED "primary checkout"; subdir REFUSED "not a worktree root"); healthy linked worktrees still accepted (clean plan + glob-disjoint plan ACCEPT).
- Dedup now by RESOLVED top-level (L928), so two spellings of one worktree can't pass as distinct.
- Mode routed through Get-LaneMode in validation (L896) AND at start (L1011).
- packet_id constrained to ^M\d+-T\d+$ (Assert-PacketId L687-694), applied in plan validation (L899) and Start-LaneFirstLaunch (L736) — also hardens the tasks-path join against traversal. Proven by test 11 ("bad-id" REFUSED).

Continued in part 3 (F2 + F5 + verdict).

---

M0-T161 G3 DELTA — PART 3/3

F2 CLOSED (owner guide now correct end to end):
- Step 3 (L51-53) now states plainly "This step does NOT print the approval code - the loop starts in the background and parks; step 4 shows you the code." (the false "step 3 prints the digest" claim is gone).
- Step 4 (L57-87) is rewritten as TWO approve commands: first WITHOUT a code — which prints the pending approval + the digest and STOPs on purpose — then again WITH the pasted code. The guide quotes the STOP line, and it is BYTE-EXACT to the script: "STOP [approve]: pass -PromptDigest <the digest printed above> to approve the held prompt" == commission_lanes.ps1 L823. Script flow confirms it: pending-approvals prints (L821), then the empty-digest STOP (L823) BEFORE the Worktree/PacketId check, so the first (code-less) call reaches exactly that STOP with the digest shown just above.
- "The one rule to remember" (L115-118) now documents that single expected STOP as the sole exception; step 4 tells the owner any OTHER STOP means stop and tell the assistant. Plain English, '!' lines correct, order correct.

F5 CLOSED: New-Item and a new Write-WrapperFile seam (L457-462) are stubbed in every test section that could reach a write (2a L104-105, 6 L344-345, 10 L436-437), each restored afterward via Remove-Item Function:New-Item so later sandbox setup still works. So the suite cannot write to the machine even if a STOP regressed — belt-and-braces as claimed.

TEST ADEQUACY: the new sections genuinely prove each new guard — 6 (robocopy precondition STOPs before /MIR), 7 (cfc3d22c wrong-subtree refusal), 8 (canary supervised-only, no bounded-auto, one cycle, repin), 9 (approve digest missing/not-held, resume never called), 10 (immutability guard on config AND model, via a 4-call hash counter through a full good-output update — which also proves the F1 assertions pass on healthy output), 11 (glob overlap/disjoint, primary/subdir refusal, packet-id charset). All machine-changing calls stubbed; writes only under %TEMP%. Harvest evidence: parser 0 errors both files; run_ps_tests 8 files pass incl. sections 6-11.

Faithfulness to recert section 5 remains exact (digests L76-90 unchanged), nothing dropped/reordered/loosened; the round-2 additions only tighten it. F1-F5 and the G5 advisories are all correctly and faithfully closed, with the new assertion strings verified against the real update_controller_from_candidate.ps1 output (no false-STOP regression) and no drift from the reviewed sha. No BLOCKING or ADVISORY findings remain.

M0-T161 G3 VERDICT: PASS

END-OF-REPORT
