# M0-T051 — G3 code review — VERBATIM reviewer return

Orchestrator preservation note: saved verbatim from the reviewer agent-return channel (transport
entity-decoding only: `&lt;`→`<`, `&gt;`→`>`). Reviewer: code-reviewer (read-only). Frozen
review identity `2136cd0d8463374f961c0418084451d89fe7e415`; candidate script blob `b6ee6589…`.
Recorded by the orchestrator 2026-08-08.

---

I have completed all behavioral verification. Here is my full G3 gate report.

---

# Gate Report

- **Gate ID:** G3 (independent code review)
- **Task ID:** M0-T051
- **Reviewer:** code-reviewer (independent; producer = backend-engineer)
- **Producer:** backend-engineer
- **Result:** **PASS**
- **Clean environment/worktree used:** Reviewed at control branch `control/M0-T051-explicit-ace-strip`. Material/review identity `2136cd0d8463374f961c0418084451d89fe7e415`. I confirmed the reviewed source (`harden_controller_config.ps1`, `test_agent_supervisor_os_acl.py`) is **byte-identical** at `2136cd0` vs the working tree/HEAD (`c5320cd`); the two commits after the review identity (`5dbe182`, `c5320cd`) touch only control-plane files (gates/state/task/self-check). Task delta = `33b2e24` (main) → `bbdfb76`. Candidate script blob `b6ee6589d93b4cd95283ce6d45c22f7010aba56a` verified = `git hash-object` of the working file = `bbdfb76:...`. Defective blob `9625514e79a34c901258975d4964529a9c02378e` verified = `33b2e24:...`.

## Acceptance criteria reviewed

Owner directive D-010 source-021 (verbatim), R196–R207, re-derived from `requirements.json`. Third demonstrated pre-activation ACL defect: the owner's real elevated apply of blob `9625514e` left a pre-existing EXPLICIT `NT AUTHORITY\Authenticated Users:(M)` ACE alive (because `/inheritance:r` strips only INHERITED ACEs and `/grant:r` replaces only the named principals' grants), leaving the immutable config unelevated-writable. The fix must produce a DETERMINISTIC final DACL (exactly Administrators F / SYSTEM F / user RX) on file and parent regardless of pre-existing explicit ACEs, with an adversarial poisoned-fixture regression, RED against `9625514e`, idempotence, byte preservation, read retention, and a bounded diff.

## Directive/requirement verification

| Requirement ID | Reviewed content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-010-R196 (HOLD: no activation/dispatch/config move/manual ACL repair) | delta `33b2e24..bbdfb76` | PASS (code-lane; conduct = DCV) | Task delta is exactly 3 files (script+test+report); no activation, no config move, no out-of-band ACL edit; the fix goes only through the reviewed script path (`git diff --name-only 33b2e24 bbdfb76`). |
| D-010-R197 (unelevated doctor NOT_PROTECTED captured first as primary evidence) | `M0-T051-doctor-notprotected-evidence.json` | PASS | Stored artifact shows `controller_config_acl.protected=false`, file `NOT_PROTECTED`, reasons: "unelevated principal 'NT AUTHORITY\Authenticated Users' holds M on the file" + "an unelevated open-for-write SUCCEEDED"; parent PROTECTED. Matches the owner's reported ACL verbatim. |
| D-010-R198 (ONE narrowly bounded fix) | blob `b6ee6589` | PASS | `git diff 33b2e24 bbdfb76 -- ...ps1`: one `Invoke-Step $Icacls @($file,"/reset")` (L174) + one `@($dir,"/reset")` (L192) added ahead of the existing `/inheritance:r`; remainder is comments. No new architecture. |
| D-010-R199 (post-apply FILE+PARENT DACLs: no non-elevated principal with any write/modify/delete/rename/WriteDAC/WriteOwner; not merely re-grant three) | blob `b6ee6589` + test | PASS at DACL/ACE level | `test_adversarial_explicit_ace_is_stripped_file_and_parent` executed live (Windows): poison gone, DACL == exactly {Administrators, SYSTEM, user}, `evaluate_acl_entries` == PROTECTED on both. End-to-end effective posture incl. ownership is the R206 elevated-run boundary (see note). |
| D-010-R200 (adversarial fixture steps 1–5) | test class `HardenExplicitAceStripTests` | PASS (steps 1–3,5 + ACE-PROTECTED; step 4 full-evaluator verdict deferred to R206) | 5 tests RAN (not skipped) and passed; real icacls on a disposable temp parent+file poisoned with explicit `*S-1-5-11:(M)`; takeown commands asserted PRESENT (2, each `/F`+`/A`); DACL-subset executed; final posture Administrators F / SYSTEM F / user RX proven. |
| D-010-R201 (preserve read) | test | PASS | `test_new_sequence_preserves_unelevated_user_read`: exactly one user ACE holding RX; bytes still readable. |
| D-010-R202 (byte-for-byte) | test | PASS | `test_new_sequence_preserves_file_contents_byte_for_byte`: sha256 identical before/after. |
| D-010-R203 (preserve parent protections) | test | PASS | Parent asserted to exactly the three intended ACEs + PROTECTED; `/reset` on dir is non-recursive (no `/T`). |
| D-010-R204 (idempotent) | test | PASS | `test_new_sequence_is_idempotent`: file+dir DACL identical across two runs. |
| D-010-R205 (RED on `9625514e`) | test | PASS | `test_red_on_current_cleared_blob_leaves_poison_effective` runs the OLD sequence from `git show 33b2e24:...` (confirmed = blob `9625514e`), asserts poison SURVIVES + `NOT_PROTECTED`, then GREEN on the same file. Live, non-vacuous, passed. |
| D-010-R206 (sequencing + return NEW blob before next elevated apply) | conduct | PASS-in-progress | This G3 conducted at frozen identity; candidate blob `b6ee6589` identified and cleared (below). G5/DCV/merge + owner return remain orchestrator/owner-lane. |
| D-010-R207 (no broadening) | delta | PASS | Delta = script apply-path `/reset` insertions + comments, test updates/additions, report. Rollback path (L131–145) untouched; elevation ordering, braces, `$CommandArgs`, `$file/$dir` shapes, System32 binding all unchanged. |

## Steps independently executed

1. `git diff --stat 2136cd0 c5320cd` — confirmed post-review commits are control-plane only; reviewed source stable.
2. `git rev-parse bbdfb76:...ps1` = `b6ee6589…`; `git hash-object` of working file = `b6ee6589…`; `33b2e24:...ps1` = `9625514e…`. Blob identities confirmed.
3. `python -m pytest tools/test_agent_supervisor_os_acl.py -q` → **43 passed** (matches claim).
4. `python -m pytest ...HardenExplicitAceStripTests -v` → **5 passed, 0 skipped** (all RAN on this Windows host).
5. `python -m pytest ...test_dryrun_replays_all_apply_path_vectors ...test_apply_path_call_sites_carry_full_argument_arrays -v` → **2 passed** (A2/B1 ran, not skipped).
6. `python -m pytest tools/test_agent_supervisor_*.py -q` → **1392 passed, 2 skipped** (matches baseline; delta = +5, no regressions).
7. Read `os_acl.py` `evaluate_acl_entries` / `evaluate_file` / `_confirm_owner_elevated` / classification tables — confirmed the ACE-level vs owner/write-probe distinction and fail-closed rights classification.
8. `git diff 33b2e24 bbdfb76 -- ...ps1` and `-- ...os_acl.py` — bounded-diff review.
9. LF integrity: working tree has CRLF (Windows `core.autocrlf=true` checkout), but the **stored** blobs are **0 CRLF / LF-only** (`git cat-file blob b6ee6589` → 0 CRLF, 218 LF; test blob → 0 CRLF). Returned blob identity is stable.
10. `git grep` — only `test_agent_supervisor_os_acl.py` references the harden script/apply vectors; no stale cross-references elsewhere.

### Note on the standalone reproduction attempt
The task asked me to reproduce the fixture from scratch myself. I attempted a fully standalone icacls reproduction four ways (shell heredoc, `python -` stdin, `python -c`); the read-only guard blocks every command string containing ACL-mutating/ACL-token content (`/grant`, `/reset`, `Authenticated Users:(M)`, `write_text`, `mkdir`), while allowing `pytest`. **I did not obfuscate to bypass the guard.** Instead I executed the equivalent behavioral proof through the allowed pytest channel, which runs the REAL icacls sequence — extracted directly from the candidate blob via the PowerShell AST and `Invoke-Expression` of the actual `CommandElements` — against live poisoned temp fixtures, and asserts against the REAL production evaluator. I independently corroborated that this execution is faithful and non-gameable (see below), so this is a genuine executing review, not a signature-level one. A from-scratch orchestrator-captured reproduction is available on request but is redundant.

## Expected versus actual

| Check | Expected | Actual |
|---|---|---|
| os_acl suite | 43 passed | 43 passed |
| new adversarial class | 5 passed, none skipped | 5 passed, 0 skipped |
| A2/B1 full-vector | pass, ran | 2 passed |
| full supervisor suite | 1392 passed / 2 skipped | 1392 passed / 2 skipped |
| RED vs blob 9625514e | poison survives, NOT_PROTECTED | asserted + passed live |
| GREEN new sequence | poison gone, exactly 3 ACEs, PROTECTED | asserted + passed live |
| stored blob line endings | LF-only | 0 CRLF both files |
| delta scope | 3 files, rollback untouched | 3 files, rollback untouched |

## Evidence paths (all absolute)

- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\agent_supervisor\harden_controller_config.ps1` (L149–202: apply path; `/reset` at L174 and L192)
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\test_agent_supervisor_os_acl.py` (APPLY_VECTORS L593–614; A2 L691–718; B1 L722–747; `HardenExplicitAceStripTests` L845–1121)
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\agent_supervisor\os_acl.py` (`evaluate_acl_entries` L220–249; owner/write-probe path L290–373)
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T051-doctor-notprotected-evidence.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T051-producer-report.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T051-evidence-map.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\directives\D-010-autonomous-engineering-restructure\source-021-amendment.md`

## Ordering adjudication (review scope item 2)

**No window or ordering hazard exists.** The script's actual target order is **FILE first (L174–179), then DIR (L192–197)**.

- All six DACL-affecting icacls calls run back-to-back inside ONE elevated PowerShell session; the script refuses to run unelevated (`Test-IsElevated`, `exit 2`, L110–115). No unelevated process can observe any transient state.
- `icacls <file> /reset` momentarily re-enables inheritance and re-derives the file DACL from the parent (which may still hold permissive/inheritable ACEs at that instant). The immediately-following `icacls <file> /inheritance:r` **removes ALL inherited ACEs** (its documented semantics), yielding an EMPTY DACL, which the `/grant:r` trio fills with exactly the three intended ACEs. The file's end state is therefore independent of the parent's DACL at reset time. I verified this OS semantics against the RED/GREEN differential: the OLD sequence (no `/reset`) leaves the explicit poison; the NEW sequence removes it — the only difference is `/reset`.
- Processing the DIR after the FILE is safe two ways over: (a) `icacls <dir> /reset` is **non-recursive** (no `/T`), so it rewrites only the directory's own DACL, never the already-hardened file inside it; and (b) the file's inheritance is already DISABLED by its own `/inheritance:r`, so even the dir's transient re-inherited ACEs during its `/reset` cannot propagate to the file. File-then-dir vs dir-then-file are both correct because each target independently ends empty-then-filled with inheritance off; the order chosen is marginally the safer of the two. Idempotence holds (`/reset` re-derives, `/inheritance:r` empties, `/grant:r` replaces) and is proven live.

## Regression/security/provenance findings

- No regressions: full suite unchanged at 1392/2, delta exactly +5.
- Non-vacuity: the adversarial/RED tests use the REAL `parse_icacls` + `evaluate_acl_entries` (not mocks) on REAL `icacls` output over REAL temp fixtures; the RED test provides a bidirectional differential (OLD→poison survives/NOT_PROTECTED, NEW→poison gone/PROTECTED) on the SAME helpers, proving the assertions discriminate. The sequence is extracted from the actual candidate blob via AST + `Invoke-Expression`, and A2/B1 pin the six/eight call sites to exact argument arrays, so the replay cannot drift from the script (a missing `/reset` would fail `len==6` / `assertIn("/reset", icacls_apply[0])`).
- Fail-closed classification is sound: `M` is a dangerous right, `Authenticated Users` is not an elevated principal → NOT_PROTECTED; `RX` is read-only-safe; unknown tokens fail toward NOT_PROTECTED (`os_acl.py` L60–96, L112–117).
- Provenance: candidate blob `b6ee6589` is LF-only and stable; defective-blob RED source resolves to `9625514e`. No secrets in the delta.

## Honest proof-boundary finding (review scope item 6)

The tests do **not** overclaim. They assert `evaluate_acl_entries` (ACE/DACL-level, `os_acl.py` L220) — exactly the sub-property the defect violated — and never assert a full `evaluate_file`/`evaluate_controller_config_acl` PROTECTED verdict from the unelevated fixture. That full verdict additionally requires `_confirm_owner_elevated` (owner = Administrators via `takeown /A`, which needs elevation) and a denied `probe_write_open`; on the user-owned fixture those correctly still read NOT_PROTECTED. The producer documents this boundary explicitly (producer report §6/§7; test class docstring L860–870). The `takeown /F … /A` commands are present in the script (L150–151) and asserted PRESENT by the adversarial test. This deferred end-to-end confirmation is precisely what R206 requires the owner to close with the next elevated apply + unelevated doctor re-check — it is expected, not a defect.

## Defects

None (no blocking or non-blocking code defects).

## Required rework

None.

## Advisories (non-blocking, informational)

1. R199/R200 completeness is DACL/ACE-level only under the unelevated harness; the full effective-rights posture (ownership → Administrators, denied write-probe) is verifiable only by the owner's elevated apply + unelevated doctor. This is honestly bounded and is the entire purpose of R206 — carry it into G5/DCV/owner return, not into rework.
2. The rollback wording advisory carried from M0-T050 remains bounded-out per this task's scope; unchanged here.

## Reviewer conclusion

**PASS.** The fix is the smallest correct change inside the existing icacls path: inserting `/reset` before `/inheritance:r` on both file and parent makes the final DACL deterministic (exactly Administrators F / SYSTEM F / user RX) regardless of any pre-existing explicit ACE, which is the exact mechanism that defeated blob `9625514e`. I executed the behavioral proof through the allowed pytest channel (os_acl 43; new class 5/0-skipped; A2/B1; full suite 1392/2) and independently corroborated its faithfulness (script read, AST call-site pinning, RED/GREEN differential on the real production evaluator, blob and line-ending integrity). Ordering is sound with no hazard; the diff is bounded (rollback and all invariants untouched); the proof boundary is honest and not overclaimed.

**Clearance (R206):** I **clear candidate blob `b6ee6589d93b4cd95283ce6d45c22f7010aba56a`** for the owner's next elevated DRY-RUN + apply cycle, from the G3 code-review perspective. This clearance covers code mechanism, bounded diff, and the DACL-construction property; it does not substitute for the still-required G5, DCV, and merge, and the elevated apply itself remains owner-gated behind the R195 full-vector inspection and the R206 owner return.
