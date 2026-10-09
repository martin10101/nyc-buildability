# M0-T139 G3 code review (independent)

Independent G3 return saved verbatim by the orchestrator (transport entity-decoding only).
Reviewer: code-reviewer (unnamed spawn, role-carrying; ≠ producer). Recorded 2026-09-02.

---

I have completed my independent review. The read-only guard blocked my direct PowerShell execution attempt (expected under ADR-005), so I verified the transaction logic by close reading of the frozen source and the test suites, cross-checked against the requirement text I re-derived from `requirements.json`, and relied on the orchestrator-captured execution evidence (suite exit 0, 9 mutants, adversarial probes) per the reviewer evidence-capture protocol. Static grep confirmed the one structural finding below.

---

# G3 Gate Report — M0-T139 (D-024 Amendment 42: controller-update transaction hardening)

Reviewer: code-reviewer (independent; not the producer). Reviewed content identity: `d96f4e9f` (byte-identical to HEAD `71695eb1` on the reviewed surface). Branch `candidate/D-024-mrl-option-b`. Requirements re-derived from `project-control/directives/D-024-fable-codex-loop/requirements.json` and `source-042-amendment.md`.

## Summary

The change replaces the unverified prose §3 backup block with a fully in-script, fail-closed four-phase transaction (`backup` / `install` / `verify-manifest` / `rollback`) inside `tools/controller_update/update_controller_from_candidate.ps1`, backed by a schema-v2 binding contract, 7 PowerShell test suites, and 9 mutants. The design is genuinely fail-closed: every external process runs through `Invoke-Native` (null exit code refuses with a typed `native_no_exit_code` and a real `exit 1`); each robocopy raw code is captured immediately and judged by a site-specific guard before the next copy; backups are proved by complete bidirectional raw SHA-256 comparison; evidence is written atomically only after verification; and install/rollback bind to the recorded evidence file, never to a directory listing. I traced every fail-closed path looking for a false-green (a phase succeeding when it must refuse) and found none reproducible — the enumeration/comparison helpers all degrade toward refusal, not toward acceptance.

I found one defense-in-depth inconsistency (the rollback mirror source / install tamper-check root is not containment-checked against `backup_root` even though `backup_dir` is) and several observations, none of which is a blocker under the disclosed local-evidence-file trust model. All of R624–R637 are satisfied.

**Verdict: PASS.**

## Per-area findings

### 1. Raw-exit discipline (R625/R626)
- `Invoke-Native` (lines 71–93): sets `$global:LASTEXITCODE = $null`, redirects native stdout/stderr to temp files (never pipes), captures `$code` immediately, and refuses `native_no_exit_code` when `$null -eq $code`. `test_null_exit.ps1` proves this live by removing git from PATH so `& git` throws and no code exists. Correct. **OBSERVATION.**
- `Invoke-RobocopyRecorded` (241–251) records each raw code into `$script:RobocopyExitCodes[$CopyLabel]` and returns it; the **caller** applies the accept-range guard. In backup the first copy's guard (549–552) runs and `exit 1`s before the second copy (554) is reachable — the first failure can never be overwritten. Verified by `test_backup_phase.ps1` B3 (locked `cli.py` → `copy_failed`, no `runtime-a1` dir, no evidence) and mutant `m_rc1`. Correct. **No defect.**

### 2. Containment / reparse / uniqueness (R627/R628/R635)
- Unique backup dir: `yyyyMMdd-HHmmssfff` + 8-hex GUID suffix, `Test-Path` collision refusal, `New-Item … -ErrorAction Stop` **without** `-Force`, plus a post-create emptiness check (529–542). Correct; the collision branch is disclosed as defensive-only, structurally backed by the no-`-Force` create. **No defect.**
- `Assert-ContainedIn` (151–160) canonicalizes with `GetFullPath` (resolves `..`), `ToLowerInvariant` (case), and requires `childCanon -eq rootCanon -or StartsWith(rootCanon + '\')` — correctly rejects the sibling-prefix escape (`C:\SupervisorControllerEvil`). `Assert-NoReparseChain` (162–179) walks every existing ancestor to the drive root; `Assert-TreeNoReparse` (181–196) scans the full subtree. All three run immediately before each copy and at both `/MIR` sites (511/516–519, 659–662, 817–823). Junction/containment cases J1–J4 + mutant `m_reparse` cover it. Correct.

- **MINOR — `backup_paths.controller` is not containment-checked (Read-BackupEvidence, line 496 vs. use at 626/803).** `Read-BackupEvidence` asserts `evidence.backup_dir` is contained in `backup_root` (496), but the value actually used as the install tamper-check root and the **rollback `/MIR` source** is `evidence.backup_paths.controller` (install 626–631, rollback 803, 825), which is never passed to `Assert-ContainedIn`. For any script-written evidence these are consistent (`backup_paths.controller = backup_dir\agent_supervisor`), so this is not exploitable in normal operation and does not violate R635 (whose concern — the mirror **destination** — is containment-checked at 659/817 against `controller_root` from the reviewed binding). It only matters under full compromise of the evidence JSON, which is inside the disclosed local-file trust boundary and where the digest gates already bind restored content to the recorded identity. Still, because the code deliberately containment-checks `backup_dir`, using the un-checked sibling field for the real mirror source undermines that check's intent. Recommend adding `Assert-ContainedIn ([string]$evidence.backup_paths.controller) $backupRoot` in `Read-BackupEvidence`. Low-cost hardening; not blocking.

### 3. Bidirectional digest proof + atomic evidence (R629/R630)
- `Get-DigestCompareFailures` (210–239) is complete and bidirectional: missing (expected∉observed), extra (observed∉expected), and content-differs are all failures. It correctly handles BOTH input shapes — an `[ordered]` hashtable from `Get-TreeDigestMap` (IDictionary branch) and a `PSCustomObject` deserialized from evidence JSON (`PSObject.Properties` branch, 219–223) — so the reviewer-flagged ConvertFrom-Json hashtable/PSCustomObject trap is handled. Backup proves controller (excluded-scope) and runtime (full inventory) separately (562–580). Correct.
- Evidence is `ConvertTo-Json -Depth 8 | Out-File` to a same-dir `.tmp-<guid>` then `Move-Item -Force` (253–262), only reached after all gates pass. The verdict `PASS` is a literal set at the end of the ordered payload. Correct.
- **OBSERVATION — Move-Item overwrite semantics.** PowerShell `Move-Item -Force` onto an existing target may delete-then-move rather than a true `MOVEFILE_REPLACE_EXISTING` atomic replace. The evidence is still always either the prior complete file, briefly absent, or the new complete file — never truncated — so R630's goal ("a crash mid-write can never leave a truncated record") holds. Non-blocking.
- **OBSERVATION — empty runtime tree.** The controller digest set has a non-empty guard (`backup_source_missing`, 563–565); the A1 runtime set does not. An empty (but existing) runtime dir would back up as 0 files and PASS. Low impact (the runtime dir is created/verified to exist at 508), worth a follow-up guard for symmetry.

### 4. Bound install / bound rollback (R631/R632/R633)
- Install: `Read-BackupEvidence` enforces existence (`backup_evidence_missing`), JSON validity + required keys + schema (`backup_evidence_invalid`), `verdict == PASS` (`backup_verdict_not_pass`), and `sources.controller == destination` (`evidence_binding_mismatch`); then re-verifies the bound backup vs. its recorded digests (`backup_tampered`) and the live destination's currency vs. those digests (`backup_stale`), and records `run_id` + evidence-file SHA-256 into `controller_update_evidence.json.backup_binding` (620–705). The `backup_stale` currency gate makes backup→install a real transaction (stricter than R631's letter — a good call). I1–I7 + `m_tamper`/`m_stale` cover it. Correct.
- Rollback (797–881) uses `evidence.backup_paths.controller` as the sole source, re-verifies it against evidence before restoring (`backup_tampered`, a tampered backup is never restored), `/MIR`s only the bound tree, `Remove-CacheDirs`, then proves the restored tree bidirectionally digest-equal to the bound evidence (`rollback_verify_failed`), and removes the two stale activation records with **checked** results (`stale_record_removal_failed`). R1 proves a NEWER decoy dir is ignored and untouched, planted partial-install residue is gone, and the restored digest equals the bound evidence; `m_rbtamper` proves the tamper gate load-bearing. Correct.
- **Confirmed (item 5 of scope): no code path enumerates or sorts `backup_root` to pick a backup.** `Sort-Object` appears only in `Get-TreeFiles`/`Remove-CacheDirs` (file ordering/deletion order), never for backup selection; backup selection is exclusively through the single evidence file path from the binding. The former §10 `Sort-Object -Descending | Select-Object -First 1` is gone, and `test_runbook_parse.ps1` asserts no `Sort-Object` in any §10 block.

### 5. Fail-closed matrix + PS 5.1 semantics (R634/R638)
- Every R634 class has a live test (B3, I2/I3/I4/I6, R1/R2, `test_null_exit`, J1–J3, `m_rc1`/`m_reparse`/`m_rbtamper`). Array-unrolling is handled by consistent `@(…)` wrapping at every call site and `@($failures)` returns. `$LASTEXITCODE` propagation is disciplined in the runner and fixtures. Tests run the REAL script in a fresh `powershell.exe -File` process and judge raw exit codes — real PS 5.1 raw-exit behavior, as required.
- **OBSERVATION — three of nine mutants are layered-defense detections** (`m_rc1`, `m_reparse`, `m_rbtamper`) rather than clean kills. This is disclosed in the producer report §2, and each asserts a concrete behavioral difference (leaked bytes reaching the backup/destination + a changed refusal code), which is a legitimate mutation signal, not a tautology. Acceptable.
- **OBSERVATION — silent-continue enumeration.** `Assert-TreeNoReparse` and `Remove-CacheDirs` use `-ErrorAction SilentlyContinue`; a mid-enumeration error could theoretically skip a later reparse point or cache dir. The digest layer catches any leaked content (proven by `m_reparse`), and cache removal is re-checked and fails closed (`residue_removal_failed`). Non-blocking layered defense.
- **OBSERVATION — TOCTOU.** An inherent window exists between the reparse/containment checks and robocopy; mitigated by the post-copy bidirectional proofs and the `backup_stale` currency gate. Disclosed.

### 6. Runbook accuracy (R632/R636/R637)
- §3 (one `-Phase backup` command), §4 (one `-Phase install`, transactional preconditions described), §5a (`-Phase verify-manifest`), §10 (one `-Phase rollback`, "bound backup only, never newest") all match actual script behavior. Commands default `-BindingFile` to the in-repo contract (script line 63), so no long hash/runtime key is retyped — the 64-hex A1 key lives only in `source_binding.json.a1_runtime_dir` (machine-validated `^[0-9a-f]{64}$` tail, `runtime_key_invalid`). `test_runbook_parse.ps1` enforces no 64-hex in §3, no manual robocopy in §3, no `Sort-Object` in §10, PS-5.1 parse-clean blocks, and no `origin/main`. Correct.
- §1 model-selection row (line 20) states the file is owner-mutable, digest-recorded, compared by no §3–§8 step, and "awaits the owner-only rows R603–R605 / M0-T137, uninterpreted here" — a factual de-staling that does **not** interpret R603–R605. §2 (42–48) explains `wt-m0t063` = the A1 historical-journal probe target vs. the canary's `--checkout C:\SupervisorController`. R637 satisfied without needing the deferral fallback.

### 7. Modularity (R624)
- **OBSERVATION.** The single 883-line `.ps1` is outside the `.py`-scoped modularity CI (confirmed by captured `modularity_check --check` 0 failures). The producer's justification — keeping one security-reviewable operator file so the four phases cannot drift on shared `Exit-Refusal`/`Invoke-Native`/digest/containment/atomic-write plumbing — holds; the owner directive said "preferably inside … unless a separate narrow script is demonstrably safer," and inside is the safer choice against plumbing drift. The phase structure is clear (top-level guarded blocks). Shared helpers could optionally be dot-sourced, but that would split the reviewable unit the producer deliberately preserved. Acceptable.

## Explicit R624–R637 determinations (independently re-derived)

- **R624 — SATISFIED.** `-Phase backup` is in-script (503–617); §3 prose retired; in-script justification is sound.
- **R625 — SATISFIED.** All native calls via `Invoke-Native`; null ⇒ `native_no_exit_code` + `exit 1` (88–91, live-tested); robocopy raw code captured immediately + site guards `exit 1`.
- **R626 — SATISFIED.** First-copy guard (549–552) precedes the second copy (554); B3 + `m_rc1` prove it.
- **R627 — SATISFIED.** Unique ms-timestamp+GUID dir; collision/no-`-Force`/emptiness refusals (529–542); B2 proves fresh dir per run.
- **R628 — SATISFIED.** Containment + chain-reparse + tree-reparse immediately before every copy and both `/MIR` sites; J1–J4 + `m_reparse`.
- **R629 — SATISFIED.** Complete bidirectional raw SHA-256 of both backups; missing/extra/changed refuse (`backup_verify_failed`); runtime at full inventory.
- **R630 — SATISFIED.** Atomic (temp+rename) `controller_backup_evidence/v1` written only post-verification, binding run id, paths, pre-update identity, both raw codes, digest sets, PASS; B1 asserts each field.
- **R631 — SATISFIED.** Install requires + re-verifies the bound evidence (`backup_evidence_missing`/`_invalid`/`backup_verdict_not_pass`/`evidence_binding_mismatch`/`backup_tampered`/`backup_stale`) and records the exact identity; no "newest" path exists.
- **R632 — SATISFIED.** Rollback restores only `evidence.backup_paths.controller`; decoy-newest ignored (R1); no `Sort-Object` in §10. (See MINOR on containment of that field — does not defeat R632 for script-written evidence.)
- **R633 — SATISFIED.** `/MIR` of the bound backup + cache removal + post-restore bidirectional digest equality (`rollback_verify_failed`); residue/new-module cannot survive (R1).
- **R634 — SATISFIED.** Every listed adversarial class fails closed with a dedicated test/mutant.
- **R635 — SATISFIED.** Both destructive mirrors are gated by containment (against `controller_root` from the reviewed binding) + reparse checks immediately before the copy; only the bound `destination` is writable; stale-record removal is checked.
- **R636 — SATISFIED.** Owner §3/§10 commands are one line each; the 64-hex key lives only in the validated binding, machine-validated; parse tooth enforces no retyped key.
- **R637 — SATISFIED.** (a) model-selection row de-staled without interpreting R603–R605; (b) `wt-m0t063` vs. canary checkout explained; no silent misleading prose remains.

(For completeness: R622/R623 — one bounded task + committed D1–D17 pre-edit trace; R638 — 7 suites/9 mutants; R639/R640 — orchestrator-captured green checks + producer≠reviewer submission; R641/R642 — no live action, `%TEMP%` fixtures only, frozen/canary/accepted evidence byte-identical per captured `git diff`; R643 — return token. All consistent with the captured evidence.)

## Reproduction notes

- Re-derived R622–R643 from `requirements.json` via `python -c` (read-only) and confirmed the producer's evidence-map maps all 22 rows.
- Read the full script (884 lines), all 7 test suites + `fixtures.ps1` + `run_ps_tests.ps1`, the binding contract, the runbook, and the three evidence reports; traced each phase's ordering of gates.
- `Grep` confirmed `Assert-ContainedIn` is invoked only on `evidence.backup_dir` and `destination` — never on `evidence.backup_paths.controller` (the finding in §2).
- Direct PowerShell execution (parse check + mutant pattern-uniqueness) was blocked by the read-only guard; I therefore relied on the orchestrator-captured runs (controller_update ps_tests exit 0 incl. `test_runbook_parse` zero-parse-error assertion and all 9 mutants; supervisor ps_tests exit 0; `supervisor_command_doc_check` rc 0; `validate_directive_compliance --check` rc 0; `modularity_check` 0 failures; context budget PASS; frozen subtree `79af11a2` byte-identical; adversarial probes truncated-evidence → `backup_evidence_invalid`, verdict→`backup_verdict_not_pass`, escaping backup_dir → `path_containment_violation`, orphan `.tmp` → `backup_evidence_missing`, locked stale record → `stale_record_removal_failed` with no rollback PASS, planted extra module removed by rollback) and verified the test **logic** that produces them by reading. Per ADR-005 evidence-capture division of labor, inability to execute is not a BLOCKED basis.

## Verdict

**PASS.** No blocker or reproducible false-green defect. One MINOR defense-in-depth item (containment-check `evidence.backup_paths.controller` against `backup_root` in `Read-BackupEvidence`) and the observations above are recommended follow-ups, non-blocking for acceptance. The independent G4 (qa) and directive-compliance verification passes should proceed.

---

The specific MINOR-finding fix site: `Read-BackupEvidence` at line 496 of `update_controller_from_candidate.ps1` (add an `Assert-ContainedIn` on `evidence.backup_paths.controller` alongside the existing `backup_dir` check).

---

## Orchestrating-verifier addendum (recorded by the orchestrator, not the reviewer)

The MINOR finding's factual claim was independently confirmed by the orchestrating verifier
(`Assert-ContainedIn` is applied to `evidence.backup_dir` at line 496 but not to
`evidence.backup_paths.controller` used at lines 626/803/825). Severity concurred as MINOR,
non-blocking: for script-written evidence the two fields are structurally consistent; a
fabricated-evidence attack sits inside the disclosed local-file trust boundary, the mirror
DESTINATION containment (R635's object) is enforced against the reviewed binding at both /MIR
sites, and the orchestrating verifier's own probe V3 proved a `backup_dir` escape refuses
`path_containment_violation`. Recorded as a follow-up hardening candidate for the next
controller-update task; no acceptance mutation depends on it.
