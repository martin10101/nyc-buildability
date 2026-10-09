# M0-T139 producer report — controller-update transaction hardening (D-024 Amendment 42)

Producer: orchestrator session, 2026-09-02. Task claimed at capture head `d5be392b`;
implementation committed at `78acf086`. Base: M0-T138 accepted at `d4f55668`; frozen candidate
`1489879e` and its `tools/agent_supervisor` subtree `79af11a2…` untouched (proven: `git diff`
empty on that surface at every commit of this task; the accepted M0-T136/M0-T138 evidence files
were not modified — R622).

## 1. What was delivered (per requirement)

- **R622** ONE bounded task M0-T139; scope limited to `tools/controller_update/`,
  `docs/CONTROLLER_UPDATE_RUNBOOK.md`, `docs/SESSION_HANDOFF.md`, M0-T139 reports. No supervisor
  code, no canary contents, no accepted evidence touched.
- **R623** Consolidated pre-edit trace: `project-control/reports/M0-T139-transaction-trace.md`
  (17 coupled defects D1–D17 in 5 root-cause clusters, file/line anchors at `d4f55668`), written
  and committed BEFORE any implementation edit; all clusters repaired as one package.
- **R624** §3's manual block replaced by `-Phase backup` INSIDE
  `update_controller_from_candidate.ps1`. In-script was chosen over a separate script because
  the phases share exactly the fail-closed plumbing that must not drift (`Exit-Refusal`,
  `Invoke-Native` raw-exit discipline, digest walkers, containment/reparse gates, atomic
  evidence writer); a second script would duplicate it. `.ps1` files are outside the modularity
  CI include rules (`tools/` covers `.py` only); the single security-reviewable operator file
  deliberately continues the accepted M0-T138 design.
- **R625** Every native call runs through `Invoke-Native` (null exit ⇒ typed
  `native_no_exit_code`, exit 1 — proven live by `test_null_exit.ps1`); every robocopy's raw
  code is captured immediately by `Invoke-RobocopyRecorded` and judged by a site-specific guard
  that refuses (exit 1, nothing further executed) on codes <0, ≥4 (fresh-dir backup copies) or
  ≥8 (mirrors, where the extras bit is legitimate).
- **R626** The first backup copy's guard runs before the second copy is attempted; a locked-file
  first-copy failure refuses `copy_failed` with the runtime-a1 copy never created and no
  evidence written (`test_backup_phase.ps1` B3; mutant `m_rc1`).
- **R627** Backup run dir = timestamp-to-ms + 8-hex unique suffix; `Test-Path` collision refusal
  (`backup_dir_collision`), creation without `-Force` (`backup_dir_create_failed`), and an
  emptiness check (`backup_dir_not_empty`). Uniqueness proven by B2 (two runs, two dirs, first
  untouched). The collision branch itself is defensive (guid suffix makes a black-box collision
  practically untriggerable) — disclosed, structurally backed by the no-`-Force` create.
- **R628** `Assert-ContainedIn` (approved-root containment), `Assert-NoReparseChain` (path +
  every ancestor), `Assert-TreeNoReparse` (full recursive scan) run immediately before every
  copy, on every source and destination (backup sources, backup root, mirror destination chain,
  mirror source, bound backup). Junction cases: `test_junction_containment.ps1` J1–J4.
- **R629** Both backups proven by complete bidirectional raw SHA-256 comparison
  (`Get-DigestCompareFailures`: missing + extra + changed all refuse `backup_verify_failed`).
  Controller tree compared at the documented scope (cache/VCS dirs excluded — never copied,
  removed after every mirror); runtime-a1 at FULL inventory, no exclusions.
- **R630** `controller_backup_evidence.json` (schema `controller_backup_evidence/v1`) written
  ONLY after verification, atomically (same-dir temp + rename), binding: run id,
  `generated_at_utc`, exact source and backup paths, pre-update controller identity (complete
  digest map + count), runtime identity, BOTH raw robocopy codes, comparison scope, verdict PASS.
- **R631** Install refuses without evidence (`backup_evidence_missing`), on schema/verdict/key
  problems (`backup_evidence_invalid`, `backup_verdict_not_pass`), on an evidence file for a
  different controller (`evidence_binding_mismatch`), re-verifies the bound backup
  (`backup_tampered`) and the live destination's currency (`backup_stale`), and records
  run id + evidence-file SHA-256 into `controller_update_evidence.json.backup_binding`. No
  directory listing is ever consulted — "newest" cannot exist in the code path.
- **R632** Rollback restores ONLY `backup_paths.controller` from the recorded evidence; the
  decoy-newest scenario (`test_install_rollback_binding.ps1` R1) proves a newer directory is
  ignored and untouched. §10's former `Sort-Object -Descending | Select-Object -First 1` is
  gone; the parse tooth asserts no `Sort-Object` in any §10 block.
- **R633** Rollback mirrors (/MIR) the bound backup, removes cache residue, and proves the
  restored tree bidirectionally digest-equal to the bound evidence
  (`rollback_verify_failed` otherwise): planted partial-install residue and a corrupted file
  are both gone after R1; an extra module cannot survive.
- **R634** Fail-closed matrix, each with a live test: partial/interrupted backup (B3;
  I3 missing file), decoy newer directory (R1), tampered backup (I2 install / mutant `m_rbtamper`
  rollback), wrong evidence file (I6), missing file (I3), extra file (I4), first-copy failure +
  second-copy success (B3 + `m_rc1`), null exit code (`test_null_exit.ps1`), junction
  substitution (J1/J2/J3 + `m_reparse`), partial-install residue (R1).
- **R635** Both destructive mirrors (/MIR install + rollback) are immediately preceded by
  containment (`path_containment_violation`) and reparse gates and can only ever write the
  bound `destination` under `controller_root`; stale-record removal targets exactly the two
  invalidated activation records with checked results (`stale_record_removal_failed`).
- **R636** Runbook §3/§10 are ONE `powershell.exe -File … -Phase backup|rollback` command each;
  the 64-hex A1 runtime key moved into `source_binding.json` (`a1_runtime_dir`,
  machine-validated `^[0-9a-f]{64}$` tail, refusal `runtime_key_invalid`) and was written there
  programmatically from `checkout_key(wt-m0t063)` — never retyped. The parse tooth asserts no
  64-hex string in any §3 block.
- **R637** (a) §1's stale "Expected model-selection SHA-256" row replaced by wording stating the
  file is owner-mutable, digest-recorded, compared by no §3–§8 step, validated by §7's doctor
  against the config allowlists, and pending owner rows R603–R605 / M0-T137 — uninterpreted (no
  deferral needed; governance did not prevent the clarification). (b) §2 now explains
  `wt-m0t063` = the A1 historical-journal probe target (its journal is what §3 backs up and §9
  proves unchanged) while the M0-T136 canary `start` uses `--checkout C:\SupervisorController`,
  and that the §8 probe record is per-checkout, opt-in, never consumed by `start`.
- **R638** 7 ps_tests suites, all PASS (suite exit 0): `test_backup_phase`,
  `test_install_rollback_binding`, `test_junction_containment`, `test_null_exit`,
  `test_mutants_detected` (9 mutants), `test_runbook_parse` (PS 5.1 parse tooth over the script
  and every fenced runbook block), `test_source_binding` (accepted M0-T138 classes, now
  transactional). Every test runs the REAL script in a fresh `powershell.exe -File` process and
  judges raw exit codes.
- **R639** At the evidence head: controller_update ps_tests exit 0; supervisor ps_tests exit 0
  (updater/raw-exit teeth included; frozen surface untouched); command-document tooth rc0
  (runbook 11 presented commands + canary package 3); `validate_directive_compliance.py --check`
  rc0; `modularity_check.py --check` 0 failures (12 pre-existing warnings, none in this task's
  paths); context-budget OK (handoff ≤ budget).
- **R640** Producer ≠ reviewer: this task is SUBMITTED awaiting independent G3 (code-reviewer),
  G4 (qa-engineer) and directive-compliance verification; only G0 (administrative) and G2
  (self-check, never satisfying an independent gate) were recorded by the orchestrator.
- **R641/R642** No live-machine action of any kind was taken: no backup, no install, no
  rollback, no doctor, no canary, no push/PR/merge; `C:\SupervisorController`,
  `model_selection.toml`, R603–R605, GitHub and provider state untouched. All script executions
  ran exclusively against throwaway fixtures under `%TEMP%`.
- **R643** Return token discipline followed (submission message ends with the required token).

## 2. Mutation coverage — detection semantics per mutant (R638)

Clean kills (mutant wrongly exits 0 where the real script refused): `m_tree`, `m_module`,
`m_manifest`, `m_content` (accepted M0-T138 set, still green under the transactional flow),
`m_tamper` (install over a tampered backup), `m_stale` (install over a drifted controller).
Layered-defense detections (a single disabled guard is caught by a deeper layer — the
behavioral difference IS the detection, asserted explicitly): `m_rc1` (first-copy guard off ⇒
second copy runs and the refusal identity changes — both asserted), `m_reparse` (tree-scan off
⇒ robocopy follows the junction while the PS 5.1 digest walk does not, measured on this host ⇒
junction bytes leak into the backup and `backup_verify_failed` fires instead of the typed early
refusal — leak and identity change both asserted), `m_rbtamper` (rollback tamper gate off ⇒
tampered bytes reach the destination and only the post-restore proof refuses — both asserted).

## 3. Robocopy exit-code policy

Fresh-directory backup copies accept raw 0–3 and refuse ≥4 (`4` = mismatches, impossible
against a just-created empty directory unless something is wrong) and <0 (malformed). Mirrors
accept 0–7 and refuse ≥8 (bits 1/2 — copied/extras — are the normal result of mirroring over an
existing tree). Null never reaches a guard: `Invoke-Native` refuses it first. All raw codes are
recorded in the evidence (`robocopy_exit_codes`).

## 4. Design decisions a reviewer should weigh

1. **In-script phases vs separate script (R624)** — see §1/R624 above; the owner's
   "preferably inside" was followed; the alternative was rejected for plumbing-drift risk.
2. **Cache-dir semantics** — `__pycache__`/`.pytest_cache` are never copied, excluded from
   every comparison, and now REMOVED from the destination after both mirrors, so the
   comparison-blind zone cannot hold stale residue (closes the pre-existing gap where /XD left
   old caches behind; the accepted install comparison was blind to them by construction).
3. **Backup currency gate (`backup_stale`)** — stricter than the letter of R631: it also proves
   the backup is a backup OF the tree the mirror will destroy, making backup→install an actual
   transaction. A legitimate intervening change simply requires re-running §3.
4. **Rollback needs no git** — deliberate: it must work in the disaster it exists for
   (source repo gone). It trusts only the evidence file + digests.
5. **Older-run restore** is documented as a manual owner decision (runbook §10 tail); the
   script never offers a selector, keeping "bound backup only" absolute.

## 5. Verification commands (documented_test_commands)

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/controller_update/ps_tests/run_ps_tests.ps1   # exit 0
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/agent_supervisor/ps_tests/run_ps_tests.ps1    # exit 0
python tools/supervisor_command_doc_check.py                                                                # rc 0 (11 commands)
python tools/supervisor_command_doc_check.py --doc project-control/reports/M0-T136-canary-package.md        # rc 0 (3 commands)
python tools/validate_directive_compliance.py --check                                                       # rc 0
python tools/modularity_check.py --check                                                                    # 0 failures
python tools/context_budget_check.py                                                                        # handoff within budget
```

## 6. Files changed

`tools/controller_update/update_controller_from_candidate.ps1` (415→838 lines, 4 phases);
`tools/controller_update/source_binding.json` (schema v2, +5 keys);
`tools/controller_update/ps_tests/` (fixtures extended; 4 new suites; mutants +5; parse tooth
extended); `docs/CONTROLLER_UPDATE_RUNBOOK.md` (§§1/2/3/4/10); `docs/SESSION_HANDOFF.md`
(seq-74); M0-T139 control-plane records and reports.

## 7. Disclosed limitations / follow-ups (none blocks review)

1. The `backup_dir_collision` branch is defensive-only (guid suffix); black-box untriggerable —
   backed by the no-`-Force` create as second layer.
2. Three mutants are layered-defense detections, not wrongly-pass kills (see §2) — each asserts
   the concrete behavioral difference, and the report says so per case.
3. Robocopy-vs-`Get-ChildItem` junction traversal asymmetry is measured host behavior (robocopy
   follows, the PS 5.1 walk did not); the primary reparse gates never rely on it — it is only
   the depth of the layered defense behind them.
4. §1's protected-config LF-normalized hash row is retained (still-correct documentation of the
   manifest's recorded value); only the model-selection expected-hash row was de-staled.
5. Multiple backup runs share ONE evidence path by design: the LATEST verified backup is the
   bound one; older run directories remain on disk but are restorable only by the manual owner
   path (runbook §10 tail).
6. Carried from seq-73 (out of scope here): doc-check DEFAULT_DOCS lacks the MRL runbook;
   ps_tests not wired into CI (workflows forbidden); live CLI permission shapes provable only by
   the owner canary (R579).
