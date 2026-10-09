# M0-T139 Directive-Compliance Verification (D-024 Amendment 42, R622–R643)

Independent DCV return saved verbatim by the orchestrator (transport entity-decoding only),
followed by a clearly-labeled orchestrating-verifier addendum with this session's own
adversarial reproductions that the DCV rows reconcile against.

---

I have now independently reproduced primary evidence for all 22 requirements. Every check I could run passed; the only items I could not execute myself (the PowerShell fixture-writing ps_tests) are covered by my complete static reading of all 8 test files plus the orchestrator-captured run this session. Here is my per-row verdict.

---

# DCV Report — M0-T139 vs D-024 Amendment 42 (R622–R643)

Scope reviewed at HEAD `71695eb1` / reviewed evidence head `d96f4e9f` (reviewed producer files byte-identical; the four files differing HEAD-vs-reviewed are submission-transition control-plane records only: `gates/M0-T139-G2.json`, `reports/M0-T139.json`, `state.json`, `tasks/M0-T139.json`).

Intake integrity (independently reproduced): `git diff d4f55668..HEAD` touches no `tools/agent_supervisor/**`, no `model_selection*`, no `M0-T136-*`/`M0-T138-*` report. Strict-UTF-8 requirements.json comparison d4f55668↔HEAD: 22 ids appended (R622–R643), 0 removed, 0 pre-existing rows semantically changed (the capture commit re-serialized `\u2014`→literal UTF-8 `—`; bytes `e2 80 94`, valid UTF-8 — no content change; my first locale-decoded diff was an artifact I disproved). `validate_directive_compliance.py --check` rc 0 (source digests + locked ids intact). All 22 outcomes/paragraphs of the amendment map 1:1+ onto rows; no missing/weakened/combined/invented requirement.

---

D-024-R622: PASS
evidence: Single task `tasks/M0-T139.json` (id M0-T139, one packet); `git diff d4f55668..HEAD --name-only` lists no `M0-T136-*`/`M0-T138-*` file and no `tools/agent_supervisor/**`; frozen `1489879e` subtree `79af11a2…` equals `HEAD:tools/agent_supervisor` (unchanged); `manifest.json` audit_log entry (2026-09-02) records "ONE bounded follow-up task M0-T139", not Tranche C / not a supervisor refactor.

D-024-R623: PASS
evidence: `reports/M0-T139-transaction-trace.md` lines 1–87 cluster 17 coupled defects D1–D17 across backup→install→verify→rollback in 5 root-cause clusters (D1 is the $LASTEXITCODE issue, but D2–D17 continue: masking second copy, uniqueness, reparse, digest proof, unbound rollback D10, additive-restore D11, atomicity D14, doc D15–D17). Committed at `87b0a668` (03:12), which `git merge-base --is-ancestor` confirms precedes the implementation commit `78acf086` (03:41).

D-024-R624: PASS
evidence: `update_controller_from_candidate.ps1` lines 503–617 implement a controller-owned `-Phase backup`; runbook §3 (lines 56–73) retires the manual two-robocopy block and presents ONE `-Phase backup` command; `test_runbook_parse.ps1` lines 99–102 assert §3 carries no manual `robocopy`.

D-024-R625: PASS
evidence: `Invoke-Native` (lines 71–93) captures `$global:LASTEXITCODE` immediately and, on null, calls `Exit-Refusal 'native_no_exit_code'`; `Exit-Refusal` (lines 65–69) does `exit 1` (a real terminating failure, not a printed "stop"). Unacceptable robocopy codes refuse via `copy_failed` (lines 549–559). `test_null_exit.ps1` (git-off-PATH) asserts raw exit 1 + `REFUSED native_no_exit_code` under WindowsPowerShell v1.0 (5.1).

D-024-R626: PASS
evidence: In `-Phase backup`, copy-1 (controller) raw code is judged at lines 549–552 (`Exit-Refusal 'copy_failed' … "the second copy was NOT attempted"`) BEFORE copy-2 (runtime, line 554) runs. `test_backup_phase.ps1` B3 (lines 78–90) locks the source, asserts `copy_failed` and zero `runtime-a1` copies; mutant `m_rc1` (`test_mutants_detected.ps1` 180–198) proves disabling that gate lets copy-2 run.

D-024-R627: PASS
evidence: Lines 528–542 build `$runId` (timestamp+GUID), `if (Test-Path $backupDir) { Exit-Refusal 'backup_dir_collision' }`, create it, then assert it is empty. `test_backup_phase.ps1` B2 (70–75) asserts a second run yields a different `run_id`/`backup_dir` and leaves the earlier one intact.

D-024-R628: PASS
evidence: `-Phase backup` lines 504–526 run `Assert-ContainedIn`, the NYCBuildabilitySupervisor `path_not_approved` check, `Assert-NoReparseChain`, `Assert-TreeNoReparse` on both sources and the backup-root chain, before any copy; install repeats them at 658–662, rollback at 817–823. `test_junction_containment.ps1` J1–J4 assert `reparse_point_detected` (junction in tree, junction backup-root) and `path_containment_violation` (escaping destination) with no evidence written.

D-024-R629: PASS
evidence: Lines 561–580 build per-file raw-SHA-256 maps for the controller subtree and the A1 runtime dir and run `Get-DigestCompareFailures` (lines 210–239: bidirectional — missing, extra, and content-differs all fail) against each backup, refusing `backup_verify_failed`. `test_backup_phase.ps1` B1 asserts both digest sets recorded; the `m_reparse` mutant shows the digest proof catches leaked bytes.

D-024-R630: PASS
evidence: Backup evidence is written by `Write-JsonAtomic` (lines 253–262, temp-write+rename) only after verification, at lines 583–610, binding schema `controller_backup_evidence/v1`, `run_id`, `generated_at_utc`, `sources` (exact paths), `backup_dir/backup_paths`, `robocopy_exit_codes` (both raw codes), `pre_update_controller_identity.files_sha256`, `runtime_a1_identity`, and `verdict='PASS'`. B1 asserts schema, PASS-only-after-verify, both raw codes, and digest presence.

D-024-R631: PASS
evidence: `-Phase install` lines 621–643 call `Read-BackupEvidence` (463–498: reads the recorded evidence file — "never a directory listing, never the newest backup"), re-verify tamper (`backup_tampered`) and currency (`backup_stale`), and record `backup_binding.run_id`+`backup_dir`+`backup_evidence_sha256` in `controller_update_evidence.json` (lines 685–690). `test_install_rollback_binding.ps1` I1 (missing→`backup_evidence_missing`, nothing mirrored), I2/I3/I4/I6 refusals, I7 records the exact bound run id.

D-024-R632: PASS
evidence: `-Phase rollback` lines 797–830 use `Read-BackupEvidence` (bound evidence) and restore only `$boundControllerBackup`; runbook §10 (271–281) states the "newest directory" restore is retired; `test_runbook_parse.ps1` 107–109 asserts §10 contains no `Sort-Object`; `test_install_rollback_binding.ps1` R1 plants a decoy `zzzz-99999999-decoy` and asserts the BOUND run is restored and the decoy untouched, R2 asserts `backup_evidence_missing` never guesses.

D-024-R633: PASS
evidence: Rollback mirrors with `/MIR` + `Remove-CacheDirs` (line 831) then proves `Get-DigestCompareFailures` bidirectional equality against the bound evidence (835–841, `rollback_verify_failed`). R1 asserts `half_installed_module.py` and decoy `evil.py` are absent after rollback, `legacy_module.py` restored, and restored `cli.py` SHA-256 equals the bound evidence digest.

D-024-R634: PASS
evidence: Every listed class fails closed with a distinct reproduced tooth — partial/interrupted backup (no PASS evidence ⇒ `Read-BackupEvidence` `backup_verdict_not_pass`, and B3 writes no evidence), decoy newer (R1), tampered backup (I2 / `m_tamper`), wrong evidence file (I6 `evidence_binding_mismatch`), missing/extra file (I3/I4 `backup_tampered`), first-copy-fail-then-second (B3 / `m_rc1`), null exit (`test_null_exit`), junction substitution (J1–J3 / `m_reparse`), partial-install residue (R1). Load-bearing guards each killed by an independent mutant.

D-024-R635: PASS
evidence: Rollback confines the destructive `/MIR` to `$destination` after `Assert-ContainedIn $destination $controllerRoot` + `Assert-NoReparseChain`/`Assert-TreeNoReparse` (lines 815–830); `Remove-CacheDirs` operates only under `$Root=$destination`; stale-record removal (846–854) targets only `$manifestPath`/`$evidencePath`. Comment/policy at lines 39–47 and the containment tests (J1–J4) confirm no delete/mirror outside the controller subtree.

D-024-R636: PASS
evidence: Runbook §§3/4/10 each present exactly one `-Phase` command with no retyped hash/key (lines 71–73, 109–111, 283–285); the 64-hex A1 key lives only in `source_binding.json:24`, machine-validated at ps1 lines 334–337 (`runtime_key_invalid` unless leaf matches `^[0-9a-f]{64}$`). I re-derived `checkout_key('…\wt-m0t063')` via `tools/agent_supervisor/durable_state.py` = `1854a2a4…e5d262`, exactly the binding tail. `test_runbook_parse.ps1` 99–101 asserts §3 retypes no 64-hex key.

D-024-R637: PASS
evidence: Runbook §1 model-selection row (line 20) is de-staled and explicitly "deliberately no pinned expected hash… awaits the owner-only rows R603–R605 / M0-T137, uninterpreted here" — it does not interpret R603–R605; §2 lines 41–48 explain `wt-m0t063` is the A1 historical-journal probe while the M0-T136 canary runs `--checkout C:\SupervisorController`. R603–R605 rows are dict-identical d4f55668↔HEAD (reproduced).

D-024-R638: PASS
evidence: 8 checked-in suites under `tools/controller_update/ps_tests/` provide positive+refusal tests (`test_backup_phase`, `test_install_rollback_binding`, `test_junction_containment`, `test_null_exit`, `test_source_binding`) and 9 independent mutants (`test_mutants_detected`: tree, module, manifest, content + transaction tamper/stale/reparse/rc1/rbtamper), each run through a fresh real `powershell.exe -File` process reading raw `$LASTEXITCODE` (`fixtures.ps1` `Invoke-UpdateScript`; `test_null_exit` uses WindowsPowerShell v1.0). I read every suite and confirmed each mutant disables exactly one load-bearing guard and asserts the behavioral difference; suite re-run this session (orchestrator-captured, my sandbox blocks PowerShell fixture-writes) returned raw exit 0 with all 9 mutants detected.

D-024-R639: PASS
evidence: I reproduced at HEAD (reviewed producer files byte-identical to reviewed head): `validate_directive_compliance.py --check` rc 0; `modularity_check.py --check` 0 failures (controller_update not flagged); `context_budget_check.py` PASS; `supervisor_command_doc_check.py` runbook 11 commands / 0 failures and canary 3 commands / 0 failures. PowerShell/updater ps_tests exit 0 captured by the orchestrator this session; the seven `documented_test_commands` in `tasks/M0-T139.json` enumerate exactly this set.

D-024-R640: PASS
evidence: `tasks/M0-T139.json` status `awaiting_gate` (not accepted), `required_gates`=[G0,G2,G3,G4], `reviewer_agents` include `directive-compliance-verifier` (this DCV pass); commit `a2bccfa4` records "submitted awaiting_gate … G2 self-check PASS". No acceptance recorded.

D-024-R641: PASS
evidence: `git diff d4f55668..HEAD --name-only` is confined to `docs/CONTROLLER_UPDATE_RUNBOOK.md`, `docs/SESSION_HANDOFF.md`, `tools/controller_update/**`, and orchestrator control-plane records (`directives/D-024…`, `gates/M0-T139-*`, `state.json`, `tasks/M0-T139.json`, `reports/M0-T139-*`); no `tools/agent_supervisor/**`, no `model_selection*`, no canary `M0-T136-*` file; R603–R605 rows byte-stable. `HEAD:tools/agent_supervisor` tree unchanged from frozen candidate.

D-024-R642: PASS
evidence: `git rev-parse @{u}` → "no upstream configured"; `git branch -r` shows no remote candidate branch (nothing pushed → no PR/merge). No `-Phase backup/install/rollback`/doctor/canary execution artifact against live roots; the ps_tests operate solely on `$env:TEMP` fixtures (`fixtures.ps1` `New-FixtureWork`). Orchestrator confirms no live-machine mutation this session.

D-024-R643: PASS
evidence: The task took the "successful completion" path — full non-partial implementation exists and status is `awaiting_gate` for independent G3/G4/DCV (verifiable state consistent with `CONTROLLER_UPDATE_TRANSACTION_SUBMITTED` and inconsistent with the BLOCKED "make no partial fix" branch). The token string itself is a producer transcript return item (not a committed artifact); `reports/M0-T139-evidence-map.json:175` records the submission return ending with that token, and commit `a2bccfa4`/task state corroborate the submitted branch.

---

## Verdict

All 22 requirement IDs SATISFIED on reproduced primary evidence. Notes for the orchestrator: (1) I could not execute the PowerShell ps_tests directly — the read-only guard blocks PowerShell fixture file-writes — so R638/R639's PS-execution leg rests on my complete static reading of all 8 suites + the script plus the orchestrator-captured run (raw exit 0, 9/9 mutants); the Python/governance/command-doc/modularity/context/key-derivation legs I ran myself. (2) The apparent "20 changed pre-existing rows" is a non-finding: it was a locale-decoding artifact; the bytes are valid UTF-8 em-dashes and the append-only property holds. (3) R643's return-token string is inherently a transcript artifact, verified indirectly via the submitted state.

DCV_ALL_PASS

---

## Orchestrating-verifier addendum (recorded by the orchestrator, not the DCV agent)

This session's own independent reproductions, which the DCV rows reconcile against
(all raw exit codes observed directly by the orchestrating verifier):

1. Gate 0 identities: root/branch/HEAD `71695eb1`/reviewed `d96f4e9f`/clean tree/no upstream/
   no remote candidate branch//mcp empty/frozen `1489879e` commit with `tools/agent_supervisor`
   tree `79af11a2` byte-identical at HEAD — all match.
2. `d96f4e9f..71695eb1` = submission-transition control-plane only (G2 record, submission
   record, state timestamp, task status/progress); semantic task-packet diff = {status,
   progress_percent, updated_at} only.
3. M0-T136 evidence vs acceptance `e60192ed` and M0-T138 evidence vs acceptance `d4f55668`:
   empty diffs (byte-identical).
4. Full controller_update ps_tests suite re-run: raw exit 0, all 7 suites, every assertion
   PASS, 9/9 mutants detected. Supervisor ps_tests: raw exit 0. Command-doc tooth: rc 0
   (runbook 11 commands) and rc 0 (canary 3 commands). `validate_directive_compliance.py
   --check` rc 0. `modularity_check.py --check` 0 failures (12 pre-existing warnings, none in
   task paths). `context_budget_check.py` PASS.
5. Independent adversarial probe pack (scratchpad `verifier_probes.ps1`, raw exit 0), covering
   refusal codes the checked-in suite exercises only indirectly: V1 truncated evidence JSON →
   `backup_evidence_invalid`; V2 verdict flipped to FAIL → `backup_verdict_not_pass`; V3
   evidence `backup_dir` escaping the bound backup root → `path_containment_violation`; V4
   orphaned same-directory `.tmp` evidence never consumed → `backup_evidence_missing`; V5
   exclusively-locked stale activation record → `stale_record_removal_failed` with NO rollback
   PASS evidence written, planted extra module removed by the bound mirror, clean retry
   succeeding after unlock.
6. A1 runtime key independently re-derived: sha256(normcase(resolve(wt-m0t063 path))) =
   `1854a2a4…e5d262` == binding `a1_runtime_dir` tail (durable_state.checkout_key semantics).
7. Requirements registry semantic diff d4f55668↔HEAD: R622–R643 appended, 0 removed, 0
   pre-existing rows changed; R603–R605 dict-identical.
8. Documented trust boundary (verifier-recorded): the reparse/containment gates execute as
   adjacent in-process statements immediately before each destructive mirror; the residual
   sub-second TOCTOU window, and the local-file trust placed in `controller_backup_evidence.json`
   under `%LOCALAPPDATA%` (a local administrator can rewrite both the evidence and the backup
   consistently), are inherent to an owner-run single-host procedure and are mitigated by the
   digest binding, the `backup_stale` currency gate, and the owner-run context. G3's MINOR
   follow-up (containment-check `evidence.backup_paths.controller`) is queued as a hardening
   candidate for the next controller-update task.
