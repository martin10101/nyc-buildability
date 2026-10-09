# M0-T161 — G5 DELTA re-review, required-corrections round 2 (security-reviewer "sec-m0t161", read-only, static)

> Transmission history: pinned at 0c76b136 (delta = 158b5bca, identity 82864416), delivered as three SendMessage parts
> (1/3..3/3) ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed
> only). Verdict PASS: every prior advisory closed, owner touchpoints preserved, injection and /MIR wipe safety hold,
> offline tests isolated. Three LOW residuals (mid-path globs, the precondition's position, lexical dedup) are routed.

---

M0-T161 G5 DELTA re-review (READ-ONLY, static) — Part 1/3

PIN: HEAD 0c76b136 (frozen 82864416). Delta = `git show 158b5bca` (4 files); reviewed in full against the real update script and recert §5. Parser-clean and run_ps_tests green were reported at harvest. Bottom line: every prior G5 advisory is closed, no regressions, no new BLOCKING items.

PRIOR ADVISORIES — all resolved:
- Certified-chain asserts strengthened: Step-Install now also requires the candidate commit tree 82432361 and "204 byte-identical" (commission_lanes.ps1:436-445); Step-VerifyManifest now requires "...at a3f24ff3...", "covered files 146" and "installed files re-compared 204" (488-504). Verified NOT false-STOPs: the update script prints exactly these — update_controller_from_candidate.ps1:697-700 (commit/commit-tree/subtree/"204 byte-identical") and 790-791 ("MANIFEST VERIFIED against the accepted source at <sha>" + "covered files N; installed files re-compared N"). The cfc3d22c/11d43515 wrong-subtree refusal is unchanged and still present (432-434).
- /MIR wipe safety CLOSED: a new Get-TreeFileCount precondition STOPs before ANY robocopy unless the certified source holds exactly 204 files (commission_lanes.ps1:241-249 def; 524-533 check). A missing source returns -1 -> STOP. So a missing/empty/wrong source can no longer wipe a destination; the destructive /MIR is now gated by a positive count check, not just detected post-hoc.
- Rollback pointers ADDED to the 5.5-5.9 STOPs (verify-manifest 490/497/501, robocopy 540, verify-controller 563, doctor 579, doctor-live 595) and to the install commit-tree/count STOPs — "roll back per runbook section 10". The four wrapper-generation throws now also carry "STOP [update 5.6]:" prefixes (622/626/652/661).

Continued in Part 2/3.

---

M0-T161 G5 DELTA — Part 2/3

PLAN-VALIDATOR HARDENING — verified and bypass-resistant:
- Linked-worktree ROOT now required (commission_lanes.ps1:897-923). Two-pronged: (a) `git rev-parse --show-toplevel` must equal the given path (rejects a subdirectory), and (b) `--absolute-git-dir` must differ from `--git-common-dir` (rejects the PRIMARY checkout, whose two dirs are equal). The git-dir!=common-dir test is the canonical primary-vs-linked distinction and is robust even against a junction masking the path, because the primary's git-dir==common-dir regardless of the access path. Uses --absolute-git-dir (not --git-dir), so a relative git output can't confuse the compare.
- Dedup now keys on the RESOLVED top-level (929-932), so two entries under one worktree can't pass as distinct.
- packet_id constrained to ^M\d+-T\d+$ via Assert-PacketId BEFORE any path join — enforced both in Assert-ValidLanePlan (900) and at the top of Start-LaneFirstLaunch (737), so the single-lane, approve and lanes paths are all covered. Kills traversal via packet_id.
- lanes-phase mode now routed through Get-LaneMode (up front at 895 and again at 1011), matching the single-lane fail-closed rule.
- Get-PathOverlap is glob-aware: Get-NormPathBase strips a trailing /** or /* to the covered directory and over-approximates (the SAFE direction), so `dir/**` overlaps any path under `dir` (965-989).
- All external calls remain array-splat through Invoke-Ext (no shell string), no Invoke-Expression, no caller text in any python -c (those still embed only constants). Injection surface unchanged and clean.

OWNER TOUCHPOINTS — preserved (and clearer):
- approve stays owner-typed. The revised owner-guide step 4 is two commands: run approve WITHOUT a digest -> it lists pending-approvals, prints the digest, and STOPs on purpose with the exact "STOP [approve]: pass -PromptDigest ..." line (resume-pending-prompt is NOT reached); the owner copies that digest and re-runs WITH it. No auto-approval, no auto-fetch, WAIT_FOR_OWNER never bypassed. Core logic unchanged: the digest is still verified to be among the held prompts before resume (commission_lanes.ps1 approve phase).
- repin first-start-only and no --owner-enable-bounded-auto on the lane-1 canary are unchanged and now explicitly tested.

Continued in Part 3/3.

---

M0-T161 G5 DELTA — Part 3/3

TESTS — still cannot touch the real machine, and now cover the new guards:
- New sections 6-11 each stub every external/tree/launch/WRITE helper: Invoke-Ext, New-Item (simple-function stub, removed after each use), the new Write-WrapperFile seam, Ensure-ActivationDir, Assert-SameTree, Get-CheckoutKey, Get-TreeFileCount, Get-FileSha256Raw and Start-Detached. $script:Lane3Wrapper is redirected to a %TEMP% fixture; git is stubbed via Resolve-GitStub; all FS ops stay under $env:TEMP and are removed at the end. So no supervisor verb, no lane folder, no wrapper, no /MIR, no start can reach the machine even if a STOP moved (belt-and-braces confirmed).
- Coverage verified by tracing the stubs: robocopy precondition STOPs before any /MIR on a wrong count (section 6); the cfc3d22c wrong-subtree refusal (7); lane-1 rejects non-supervised + the captured start args carry --mode supervised, NO owner-enable-bounded-auto, max-cycles 1, repin (8); approve STOPs and never resumes when the digest is missing or not held (9); the config/model immutability guard STOPs on either change — I traced the Get-FileSha256Raw call order (before x2, after x2 with no intervening call) so the counter mapping is correct (10); and the primary-checkout, subdirectory, glob-overlap/disjoint and bad-packet-id validator paths (11). The install/verify-manifest stubs use the real update-script output shape.

RESIDUAL ADVISORIES (all LOW, non-blocking; input is orchestrator-authored + physically worktree-isolated):
- Get-NormPathBase normalizes only a TRAILING /** or /*, not mid-path wildcards (dir/**/x) or char-classes ([..]/?). A mid-path glob vs a concrete matching path could evade overlap detection. Low: allowed_paths convention is dir/** or exact.
- The /MIR source precondition runs AFTER the lane-4/5 folder+wrapper standup, not before. No data loss (4/5 are new dirs); ideally check the source first.
- Worktree dedup normalizes lexically (GetFullPath), not by resolving junctions/symlinks; two junction aliases of one linked worktree could pass the top-level dedup. Not isolation-breaking (git-dir!=common-dir still guarantees a real linked worktree; allowed_paths disjointness still holds).

All corrections only tightened the helper; no guard was weakened; owner touchpoints, injection safety, /MIR wipe safety and offline-test isolation all hold.

M0-T161 G5 VERDICT: PASS
END-OF-REPORT
