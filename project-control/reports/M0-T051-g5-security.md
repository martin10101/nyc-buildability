# M0-T051 — G5 security review — VERBATIM reviewer return

Orchestrator preservation note: saved verbatim from the reviewer agent-return channel (transport
entity-decoding only: `&amp;`→`&`, `&lt;`→`<`, `&gt;`→`>`). Reviewer: security-reviewer
(read-only). Frozen review identity `2136cd0d8463374f961c0418084451d89fe7e415`; candidate script
blob `b6ee6589…`. Recorded by the orchestrator 2026-08-08.

---

I have completed all independent verification. Here is my full G5 security review report.

---

# Gate Report

- **Gate ID:** G5 (independent security review)
- **Task ID:** M0-T051
- **Reviewer:** security-reviewer (read-only)
- **Producer:** backend-engineer
- **Result:** **PASS**
- **Clean environment/worktree used:** Reviewed at frozen content identity. Control branch `control/M0-T051-explicit-ace-strip`; HEAD `c5320cd`. The load-bearing artifact is the **script blob**, which I confirmed is byte-identical (`b6ee6589d93b4cd95283ce6d45c22f7010aba56a`) across `bbdfb76` (task commit), `2136cd0` (review identity), and HEAD — no drift. Main base `33b2e24` carries the barred blob `9625514e`.

## Acceptance criteria reviewed

Owner directive D-010 source-021 (R196-R207), verbatim at `project-control/directives/D-010-autonomous-engineering-restructure/source-021-amendment.md`. Narrow defect-lane fix to `tools/agent_supervisor/harden_controller_config.ps1`: the elevated apply must produce a deterministic final DACL (exactly Administrators F / SYSTEM F / unelevated-user RX) on file and parent regardless of pre-existing explicit ACEs, with adversarial poisoned-fixture regression, RED-on-9625514e, idempotence, byte-preservation, read-retention, and no broadening.

## Independent behavioral verification (executed by me)

1. **Live config re-verified read-only** — `sha256("C:\Program Files\SupervisorConfig\config.toml") = 29eb765eabce05b81dcbea33fd4d28800479596e9b23fd4d4fa334f6ee7da1cb` (712 bytes). Matches the frozen directive SHA exactly. **Config untouched.**
2. **os_acl suite** — `python -m pytest tools/test_agent_supervisor_os_acl.py -q` → **43 passed, 0 skipped** (baseline 38 → +5).
3. **Adversarial class, verbose** — `HardenExplicitAceStripTests` → **5/5 PASSED, none skipped** (they RAN real `icacls` on disposable poisoned fixtures).
4. **Full supervisor suite** — `python -m pytest tools/test_agent_supervisor_*.py -q` → **1392 passed, 2 skipped in 117s** (matches producer; freeze baseline >=1165 / 0 failures satisfied; the 2 skips are outside os_acl).
5. **Blob identity** — `git hash-object` and `git rev-parse` confirm the candidate `b6ee6589` at HEAD/bbdfb76/2136cd0; `33b2e24:...` = barred `9625514e`.
6. **Stored byte hygiene** — `git cat-file -p` shows the stored blobs are **LF-only** (script 0 CRLF / 218 LF; test 0 CRLF / 1122 LF). Working-tree CRLF is `core.autocrlf=true` checkout conversion only (confirmed), which is why `git hash-object` still matched.
7. **Scope** — `git diff --name-only 33b2e24 bbdfb76` = exactly `harden_controller_config.ps1`, `test_agent_supervisor_os_acl.py`, `M0-T051-producer-report.md` — all within `allowed_paths`. Rollback region unchanged (diff grep for `Rollback|/inheritance:e` = 0 hits).
8. **Consumers** — the script is referenced only by `os_acl.py` (note string) and `cli.py` (doctor guidance); nothing automated executes it. It is an elevated, UAC-gated maintenance tool that refuses to run unelevated. SHADOW-ONLY; nothing activated.

Note on method: the read-only guard blocks any command whose command line contains mutating `icacls` flag tokens (`/grant`, `/reset`, `/deny`, `/inheritance`); it correctly permits `python -m pytest` (those tokens execute *inside* the test process). I confirmed read-only `icacls` and `python -c` with `tempfile` are allowed, but declined to obfuscate flag tokens to force a direct mutation past a safety guard. My behavioral coverage therefore runs through the producer's tests — which are **not** "the producer's conclusion": they AST-extract the REAL script's apply sequence (so the test cannot drift from the script), resolve `$file/$dir/$UnelevatedUser` to the fixture, and drive **real `icacls`** against a poisoned fixture, including a live RED replay of barred blob `9625514e`. I independently re-ran all of them.

## Directive/requirement verification

| Requirement ID | Content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-010-R196 (HOLD: nothing activated; config untouched/unmoved; no manual ACL repair) | blob b6ee6589 | PASS | Live SHA re-verified `29eb765e` (unchanged); delta = 3 allowed files; I performed no ACL mutation on the real config (guard-blocked; my only real-config touch was read-only SHA) |
| D-010-R197 (unelevated doctor NOT_PROTECTED captured first, primary evidence) | reports/M0-T051-doctor-notprotected-evidence.json | PASS | JSON shows `controller_config_acl.protected=false`, reasons "Authenticated Users holds M on the file" + "unelevated open-for-write SUCCEEDED" |
| D-010-R198 (ONE bounded fix inside existing icacls path) | script lines 174, 192 | PASS | `/reset` inserted before `/inheritance:r` on file and parent; one extra flag invocation per target; no architecture change |
| D-010-R199 (post-apply FILE+PARENT DACL: no non-elevated principal with write/modify/delete/rename/WriteDAC/WriteOwner; not merely re-grant three) | script + test | PASS | `test_adversarial_..._file_and_parent` (real icacls): poison gone, DACL == exactly {Administrators, SYSTEM, user}, `evaluate_acl_entries`==PROTECTED on both; construction analysis below |
| D-010-R200 (adversarial fixture, owner steps 1-5, drive REAL behavior) | test class | PASS | 5 tests RAN (Windows+PS gated, not skipped); takeown asserted present (2×, /F+/A); DACL-affecting subset executed |
| D-010-R201 (preserve unelevated READ) | test | PASS | `test_new_sequence_preserves_unelevated_user_read`: exactly one user ACE holding RX; bytes readable |
| D-010-R202 (byte-for-byte contents) | test | PASS | `test_new_sequence_preserves_file_contents_byte_for_byte`: sha256 equal before/after |
| D-010-R203 (preserve dedicated parent protections) | test + script | PASS | parent end-state exactly three ACEs, verdict PROTECTED; dir `/reset` non-recursive (no `/T`) |
| D-010-R204 (idempotent) | test | PASS | `test_new_sequence_is_idempotent`: file+dir DACL identical across two runs |
| D-010-R205 (RED on cleared blob 9625514e) | test | PASS | `test_red_on_current_cleared_blob_leaves_poison_effective` RAN: old sequence (4 icacls, no `/reset`) leaves poison EFFECTIVE, verdict NOT_PROTECTED; new sequence removes it |
| D-010-R206 (sequencing: G3/G5/DCV at frozen identity; new blob returned only after review+merge, before next elevated apply) | conduct | PASS (process) | Review performed at frozen b6ee6589; blob returned to owner only post-merge is an orchestrator/owner-lane obligation restated in pre-apply conditions |
| D-010-R207 (no broadening) | delta | PASS | 3-file delta; no ACL-parsing/enumeration added; rollback untouched; no supervisor redesign |

## Attack analysis of the construction (`/reset` → `/inheritance:r` → 3× `/grant:r`, per target)

The end state is deterministic **by construction**, independent of the starting DACL:

- **Explicit allow ACEs (any principal — Authenticated Users, Everyone, Users, inherit-only):** `icacls /reset` replaces the entire DACL with the parent's default inherited ACL — it removes ALL explicit ACEs regardless of principal or flags. `/inheritance:r` then removes the re-inherited entries, leaving an empty DACL that the three `/grant:r` calls fill. Nothing non-elevated survives. The executed representative case (Authenticated Users:(M) on file and parent) proves this on real icacls.
- **Explicit deny ACEs:** also removed by `/reset` (deny ACEs are explicit). A surviving deny could only *reduce* access (deny never grants write), so it cannot defeat R199; it is removed regardless.
- **SACL / audit entries:** `/reset` and `/grant:r` operate on the DACL; SACL entries grant no access and are irrelevant to the write property.
- **Owner-based (implicit) access:** the file OWNER always holds implicit READ_CONTROL + WRITE_DAC — so if ownership remained the unelevated user, that user could rewrite the DACL. This is exactly why `takeown /F <path> /A` (ownership → Administrators group) is part of the sequence. The tests correctly assert takeown is PRESENT (2 calls, /F + /A) but **do not execute it** (needs elevation); the owner-elevation sub-property is honestly deferred (see proof boundary). Not overclaimed.
- **Mid-sequence failure (owner's explicit question):** the script sets `$ErrorActionPreference="Stop"` and `Invoke-Step` throws on any non-zero exit, so ANY failed step ABORTS the whole run (no "declared success"). Target order is file-block, then dir-block, each `/reset` → `/inheritance:r` → `/grant:r`.
  - *If file `/reset` succeeds and file `/inheritance:r` FAILS:* the file transiently re-inherits the **parent's currently-effective inheritable ACEs**. At that point the dir has NOT yet been reset (later in the sequence) and takeown does not change DACLs, so the parent is in its ORIGINAL state. For the **live remediation target**, the parent is already PROTECTED (Admin `(OI)(CI)(F)`, SYSTEM `(OI)(CI)(F)`, and MLFLL `(RX)` which is **non-inheritable**) — so the file re-inherits only Administrators(F) + SYSTEM(F), both elevated: the transient is **not** unelevated-writable. The script then aborts. **Fail-closed and DACL-safe.**
  - *General case (a permissive/poisoned parent with an inheritable non-elevated write ACE):* the file could be unelevated-writable for the sub-second window between the two back-to-back `icacls` calls, after which the script aborts. This transient is unobservable (script refuses unelevated; single elevated session) and never yields a declared-PROTECTED-but-writable end state, because (a) the run aborts and (b) the owner's MANDATORY post-apply unelevated doctor gate catches any non-PROTECTED result. Fail-closed at the process level.
  - *If `/reset` fails first:* abort before any DACL change; the target keeps its poisoned DACL and the doctor catches it — no false PROTECTED.
  - *If a `/grant:r` fails after `/inheritance:r` emptied the DACL:* the target has an EMPTY DACL (deny-all; only the elevated owner retains implicit access) → over-restrictive, fail-closed.
  - Dir `/reset` is non-recursive, and by the time the dir block runs the file's inheritance is already stripped, so the dir's transient re-inheritance cannot propagate to the already-hardened file.

## RED reproduction (R205)

`test_red_on_current_cleared_blob_leaves_poison_effective` reconstructs the barred sequence via `git show 33b2e24:...` (blob `9625514e`), runs it on a poisoned fixture with real icacls, and asserts the poison SURVIVES and the ACE verdict is NOT_PROTECTED (the old 4-call sequence has no `/reset`), then runs the new script and asserts the poison is GONE / PROTECTED. It RAN (not skipped) and PASSED — the barred sequence is confirmed defective and the new sequence confirmed remediating, on the same fixture, with real icacls. (Minor note: the test `skipTest`s if `33b2e24` is unreachable; in a full checkout it runs — keep full git history in CI so the RED stays load-bearing.)

## Live remediation ruling (owner charge item 3)

Walking the NEW blob elevated against **today's real posture** (owner = Administrators from the prior takeown; DACL = MLFLL:(RX), Authenticated Users:(M), SYSTEM:(F), Administrators:(F), Users:(RX); parent already PROTECTED):

1. `takeown /F file /A` — idempotent (already Admin-owned). OK.
2. `icacls file /reset` — Administrators holds WRITE_DAC in an elevated session, so `/reset` succeeds on the Admin-owned file; DACL is replaced with the parent's inheritable ACEs (Admin(F), SYSTEM(F) only — MLFLL:(RX) on the parent is non-inheritable). **Authenticated Users:(M), Users:(RX), and the explicit MLFLL:(RX) are all removed here.**
3. `icacls file /inheritance:r` — removes the re-inherited entries → empty DACL.
4. `icacls file /grant:r Admin:(F) SYSTEM:(F) MLFLL:(RX)` → exactly three.
5-8. Same for the parent → Admin `(OI)(CI)(F)`, SYSTEM `(OI)(CI)(F)`, MLFLL `(RX)`.

**Ruling: one elevated run of `b6ee6589` will take the file from today's NOT_PROTECTED to PROTECTED.** No residual from the current half-hardened state survives: `/reset` (all explicit) + `/inheritance:r` (all inherited) clear every ACE before `/grant:r` rebuilds exactly the intended three; the surviving Authenticated Users:(M) that defeated `9625514e` is removed at step 2.

## Honest proof boundary (owner charge item 5)

Correctly scoped, not overclaimed. The unelevated fixture tests prove the **ACE-level DACL construction** (the sub-property the defect actually violated). They explicitly defer to the owner's elevated run + unelevated doctor: (a) `takeown /A` transferring ownership to Administrators (so `evaluate_file`'s owner-elevation check and the DENIED write-open probe pass) and (b) the full end-to-end PROTECTED verdict. The tests state that, unelevated, the user-owned fixture stays user-writable, so a full `evaluate_file` verdict correctly still reads NOT_PROTECTED even with the DACL exactly three ACEs. No sub-property is claimed proven that was not.

## Dry-run contract (owner charge item 4)

Verified. `test_dryrun_replays_all_apply_path_vectors` (A2) replays all EIGHT apply vectors through the AST-extracted `Invoke-Step` with `$DryRun=$true` and asserts every element prints, plus a union assertion covering `/F`, `/A`, `/reset`, `/inheritance:r`, `/grant:r`, and every ACL principal. `test_apply_path_call_sites_carry_full_argument_arrays` (B1) pins the real call sites to exactly the 8 arrays including both `/reset`. In the script, every icacls/takeown call — including the two new `/reset` calls — routes through `Invoke-Step`, which returns after printing `[dry-run] ...` before `& $Exe @CommandArgs`. So a `-DryRun` run shows the full 8-step sequence with complete vectors and changes nothing.

## Boundary statement (owner charge item 6 — R196/R207)

- Live config **untouched**: SHA re-verified read-only as `29eb765e...` (unchanged).
- **No manual ACL repair** performed on the real config (all mutating-icacls commands were guard-blocked; my sole real-config interaction was a read-only SHA/stat).
- **No activation**; supervisor remains SHADOW-ONLY; M2-T015/T016 untouched.
- **No broadening**: 3-file delta, apply-path insertion + comments + tests + report only.
- **Rollback untouched** (diff confirms no change to the `-Rollback` block).
- Reviewer wrote nothing outside `.claude/agent-memory/security-reviewer/`; ran no `project_control.py`/git-write/`gh`.

## Findings / severities

- **Critical:** none.
- **High:** none.
- **Medium:** none.
- **Low (advisory, non-blocking):**
  1. *Target ordering.* Hardening the FILE before the PARENT leaves a theoretical sub-second writable transient on the file (post-`/reset`, pre-`/inheritance:r`) only in a *general permissive-parent* scenario. Hardening the parent first would make the file's post-`/reset` re-inheritance elevated-only by construction. Not required for the live target (parent already PROTECTED) and out of the owner's narrow scope; backstopped by abort + the mandatory post-apply doctor. Consider for a future hardening pass.
  2. *`-DryRun` requires elevation* (the elevation refusal precedes DryRun handling — pre-existing, unchanged). The owner's dry-run must be run from an elevated shell.
- **Info:**
  - The RED test `skipTest`s if `33b2e24` is unreachable — keep full git history in CI so it stays load-bearing.
  - `UnelevatedUser` defaults to the elevated session's `$env:USERDOMAIN\$env:USERNAME`; the owner should confirm it equals the ordinary supervisor account at apply time (pre-existing behavior).

## Defects

None (no critical/high/medium). The mandated behavioral pass found no live defect in blob `b6ee6589`.

## Required rework

None blocking. The two Low advisories and Info notes are optional/forward-looking.

## Pre-apply conditions for the owner's next elevated cycle (owner charge item 7)

1. Apply **only the merged blob `b6ee6589d93b4cd95283ce6d45c22f7010aba56a`** (barred: `9625514e`, `0f01d649`, `ca3811cd`).
2. **Dry-run first from an elevated shell** and confirm the FULL 8-step sequence prints with complete vectors: 2× `takeown /F … /A`, then file `/reset`, `/inheritance:r`, `/grant:r (Admin:F, SYSTEM:F, user:RX)`, then dir `/reset`, `/inheritance:r`, `/grant:r (Admin:(OI)(CI)F, SYSTEM:(OI)(CI)F, user:RX)`.
3. Confirm `-UnelevatedUser` resolves to the ordinary supervisor account (visible in the dry-run header/vectors).
4. Capture the config **SHA before and after**; it must remain `29eb765e...` (icacls/takeown never write content).
5. After the real apply, run the **unelevated doctor**; `controller_config_acl.protected` must now be **true / PROTECTED** on BOTH file and parent. **If it does not show PROTECTED, STOP and report** (do not activate, do not proceed).
6. No manual ACL edits outside this reviewed script path; no activation of M2-T015/T016.

## Reviewer conclusion

The delta is the smallest correct fix inside the existing icacls path: inserting `icacls /reset` before `/inheritance:r` on both file and parent makes the final DACL deterministic (exactly Administrators F / SYSTEM F / user RX) regardless of any pre-existing explicit ACE — closing the surviving `Authenticated Users:(M)` that defeated the prior apply. The property holds by construction against explicit allow/deny/inherit-only ACEs and is fail-closed under every mid-sequence failure (abort + mandatory post-apply doctor), and DACL-safe for the live target even on a file-`/inheritance:r` failure. Behaviorally re-verified (43 os_acl / 1392 full suite; adversarial 5/5; RED on `9625514e` live). All R196-R207 satisfied at the frozen identity; boundaries intact; config untouched. One elevated run of `b6ee6589` will take the live config from NOT_PROTECTED to PROTECTED.

**VERDICT: PASS.** The owner is cleared to dry-run and then apply merged blob `b6ee6589` under the pre-apply conditions above; the post-apply unelevated doctor must show PROTECTED or the owner stops.

---

Relevant absolute paths:
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\agent_supervisor\harden_controller_config.ps1` (blob `b6ee6589`)
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\test_agent_supervisor_os_acl.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\directives\D-010-autonomous-engineering-restructure\source-021-amendment.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T051-doctor-notprotected-evidence.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T051-evidence-map.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T051-producer-report.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\tasks\M0-T051.json`

No files were written outside my agent-memory scope; no control-plane, git-write, or `gh` commands were run; the live config was accessed read-only only.
