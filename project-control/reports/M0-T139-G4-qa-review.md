# M0-T139 G4 QA review (independent)

Independent G4 return saved verbatim by the orchestrator (transport entity-decoding only).
Reviewer: qa-engineer (unnamed spawn, role-carrying; ≠ producer). Recorded 2026-09-02.

---

I have completed my independent review: I executed the full suite myself, read every deliverable and test at the reviewed content, independently confirmed fixture hygiene (temp-only; live `C:\SupervisorController` last-written 2026-09-01 unchanged by my run, `C:\SupervisorBackup` absent), and re-derived the requirement coverage. Here is my gate report.

---

# Gate Report

- Gate ID: G4 (QA / independent evidence gate)
- Task ID: M0-T139 (D-024 Amendment 42 — controller-update transaction hardening)
- Reviewer: qa-engineer (independent; not the producer)
- Producer: orchestrator
- Result: **PASS**
- Clean environment/worktree used: reviewed files at HEAD 71695eb1, identical to evidence head d96f4e9f (task diff d4f55668..d96f4e9f). Tests executed against ephemeral `%TEMP%` fixtures only.

## Acceptance criteria reviewed

Task packet `project-control/tasks/M0-T139.json`: outputs (4-phase script, source_binding v2, ps_tests, runbook §§1/2/3/4/10, three evidence reports) and acceptance scenarios AS-TX-1..AS-TX-6. Directive requirements D-024-R622..R643 re-derived from `project-control/directives/D-024-fable-codex-loop/source-042-amendment.md`.

## Steps independently executed (raw exit codes)

| Command | Raw exit | Result |
|---|---|---|
| `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/controller_update/ps_tests/run_ps_tests.ps1` | **0** | 7/7 test files PASS; every individual assertion PASS (0 ASSERT-FAIL) |

Per-file results (all in fresh `powershell.exe -File` child processes, raw `$LASTEXITCODE`): test_backup_phase (23 assertions), test_install_rollback_binding (29), test_junction_containment (7), test_mutants_detected (27, incl. all 9 mutants), test_null_exit (2), test_runbook_parse (37; 14 fenced blocks parse-clean), test_source_binding (25). No ASSERT-FAIL lines anywhere — since the mutant generator emits an ASSERT-FAIL when any mutation pattern matches ≠ 1 time, a clean run proves all 9 patterns are unique (fail-closed generator satisfied).

Named-output existence independently confirmed: script, source_binding.json (schema v2), all 7 named ps_tests + fixtures.ps1 + run_ps_tests.ps1, runbook §§1/2/3/4/5/5a/6/7/8/9/9a/10, transaction-trace, producer-report, G2-self-check, evidence-map.json — all present.

Fixture hygiene independently confirmed: every test derives all paths from `New-FixtureWork` = `%TEMP%\ctl24-srcbind-<guid>`; no test loads the real `source_binding.json` for execution (test_runbook_parse only *reads* it for string assertions). Post-run, `C:\SupervisorBackup` is **absent** (tests never created it) and `C:\SupervisorController` LastWriteTime is 2026-09-01 (pre-dates my 2026-09-02 run — untouched). All junction lure targets resolve under `%TEMP%`, so even a pathological recursive delete stays in temp.

## Directive/requirement verification (QA lens; DCV holds the authoritative pass)

| Req | Verdict | Reproduced evidence |
|---|---|---|
| R622 (no reopen of accepted evidence) | PASS | Diff confined to allowed paths; forbidden_paths bar M0-T136/T138/tools_agent_supervisor |
| R623 (pre-edit consolidated D1-D17 trace) | PASS | M0-T139-transaction-trace.md present, captured before implementation commit |
| R624 (backup phase checked-in, runbook §3 one command) | PASS | `-Phase backup` in script; §3 = one command, no manual robocopy (test_runbook_parse asserts) |
| R625 (raw exit captured immediately; null→typed refusal+terminate) | PASS | Invoke-Native `native_no_exit_code`; test_null_exit exit 1 + typed refusal |
| R626 (first robocopy failure never masked by second) | PASS | B3 (locked cli.py → REFUSED copy_failed, "second copy was NOT attempted", 0 runtime-a1 copies, no evidence); mutant m_rc1 side-effect proof |
| R627 (unique previously-nonexistent dir; collision refused) | PASS | B2 (distinct fresh dir per run, prior untouched); collision guard present |
| R628 (approved-path/containment/reparse before copy) | PASS | J1/J2/J4 typed refusals; m_reparse |
| R629 (bidirectional SHA-256 of BOTH backups) | PASS | B1 (controller + runtime-a1 digest sets, cache excluded); backup_verify_failed path |
| R630 (atomic evidence only after verification) | PASS | B1 asserts schema/verdict/run_id/both codes/digests; Write-JsonAtomic temp+rename |
| R631 (install bound to verified backup, never newest; records identity) | PASS | I1/I2/I5/I7; test_source_binding P1 (reverified PASS, run_id + evidence sha256) |
| R632 (rollback restores bound backup only) | PASS | R1 (decoy zzzz-99999999 ignored, bound run restored); §10 no Sort-Object |
| R633 (exact previous set; no residue; post-restore equality) | PASS | R1 (half_installed_module removed, decoy content absent, digest equality) |
| R634 (all adversarial classes fail closed) | PASS (1 minor gap, see Findings) | 9 of 10 classes have dedicated positive/mutant tests |
| R635 (destructive mirror gated by containment+reparse; checked stale-record removal) | PASS | Both /MIR sites gated; R1 stale install-evidence removed with checked result |
| R636 (owner commands short; hashes/keys from binding not retyped) | PASS | a1_runtime_dir 64-hex machine-validated; §3 blocks retype no 64-hex key |
| R637 (de-stale model-selection wording + wt-m0t063/canary; no R603-R605 interpretation) | PASS | §1 model row de-staled, R603-R605 left to owner; §2 explains wt-m0t063 vs canary |
| R638 (positive tests + independent mutants under real PS 5.1 raw-exit) | PASS | 9 mutants detected; layered trio proven by side-effects |
| R639 (full affected checks green at frozen head) | PASS (controller suite reproduced; others orchestrator-captured) | ps_tests exit 0 reproduced; supervisor/doc-check/modularity per orchestrator evidence |
| R640 (submitted awaiting_gate; producer≠reviewer) | PASS | task awaiting_gate; reviewers named; producer recorded only G0/G2 |
| R641 (scope limits; supervisor/model/canary/R603-R605 untouched) | PASS | Diff scope; live state untouched (verified above) |
| R642 (no live update/backup/rollback/doctor/canary/push/PR/merge) | PASS | All my runs against %TEMP%; live state unmodified (verified) |
| R643 (return token) | PASS (DCV authoritative) | Producer report ends with CONTROLLER_UPDATE_TRANSACTION_SUBMITTED |

## AS-TX-1..6 coverage mapping (each scenario → covering live test case)

- **AS-TX-1 (R625/R626)** — `test_backup_phase.ps1` **B3**: locks `cli.py` exclusively, `-Phase backup` → REFUSED `copy_failed` naming the controller tree, script exit 1, stdout "second copy was NOT attempted", 0 `runtime-a1` copies, no evidence file. Reinforced by mutant **m_rc1**. COVERED.
- **AS-TX-2 (R627/R628)** — `test_junction_containment.ps1` **J1** (junction inside controller tree → `reparse_point_detected`, no evidence), **J2** (backup root is a junction → `reparse_point_detected`), **J4** (destination escapes approved root → `path_containment_violation`); fresh/unique+non-destructive dir by `test_backup_phase.ps1` **B2**. COVERED. (The `backup_dir_collision` guard is present but has no dedicated assertion — effectively unreachable given timestamp+guid naming; see Findings F2.)
- **AS-TX-3 (R629/R630)** — `test_backup_phase.ps1` **B1**: exit 0, schema `controller_backup_evidence/v1`, verdict PASS only after verification, run_id `^\d{8}-\d{9}-[0-9a-f]{8}$`, BOTH raw robocopy codes recorded, controller (≥3) and runtime-a1 (≥2) digest sets, cache dirs never copied. "Altered/deleted/added afterwards refuses next phase" → **I2/I3/I4**. COVERED.
- **AS-TX-4 (R631)** — `test_install_rollback_binding.ps1` **I1** (`backup_evidence_missing`, nothing mirrored), **I2** (`backup_tampered`), **I5** (`backup_stale`), **I7** (records bound run id + mirror raw code + cache residue removed); `test_source_binding.ps1` **P1** (`backup_binding.reverified=PASS`, run_id match, evidence sha256). COVERED.
- **AS-TX-5 (R632/R633/R635)** — `test_install_rollback_binding.ps1` **R1**: decoy `zzzz-99999999-decoy` present, rollback restores the BOUND run (not decoy), decoy untouched, `half_installed_module.py` removed, decoy `evil.py` absent, `legacy_module.py` restored, restored `cli.py` digest == bound evidence, stale install evidence removed with checked result, rollback evidence binds the run; **R2** (missing evidence → `backup_evidence_missing`). COVERED.
- **AS-TX-6 (R638)** — `test_mutants_detected.ps1`: 9 mutants, all detected under fresh `powershell.exe -File` raw exit; 6 clean kills + 3 layered-defense cases with documented per-case semantics. COVERED.

## Per-mutant detection semantics (9 mutants)

Fail-closed generator (`New-Mutant`): each pattern must match the current script **exactly once** or the suite fails; the clean run confirms all 9 are unique load-bearing guards.

Clean kills (mutant wrongly PASSES — exit 0 — where the real script refuses; the isolatable case):
1. **m_tree** — accepted-tree check disabled → wrong commit (shaC) installs. Control refuses; mutant exit 0.
2. **m_module** — required-module gate disabled → module-less commit (shaA) installs. Control refuses; mutant exit 0.
3. **m_manifest** — manifest digest cross-check disabled → wrong-tree manifest passes. Control refuses; mutant exit 0.
4. **m_content** — installed-tree comparison disabled → tampered destination passes. Control refuses; mutant exit 0.
5. **m_tamper** — install backup-tamper gate disabled → installs over a tampered backup. Control REFUSED `backup_tampered`; mutant exit 0.
6. **m_stale** — install currency gate disabled → installs over a stale backup. Control REFUSED `backup_stale`; mutant exit 0.

Layered-defense (deeper guard still catches; detection = changed refusal identity **plus** a proven side-effect that the mutation reached the intended layer):
7. **m_reparse** — tree reparse-scan disabled. Control REFUSED `reparse_point_detected` **before any copy** + no backup dir created. Mutant: refusal identity changes to `backup_verify_failed`, and the side-effect assertion proves **junction bytes (`junction_dir/lured.py`) leaked into the backup** — robocopy `/E` followed the junction while the PS 5.1 digest walk did not, so the bidirectional proof caught the extra file. The mutation demonstrably reached the copy layer.
8. **m_rc1** — first-copy raw-exit gate disabled. Control REFUSED `copy_failed` + `runtime-a1` copy count 0 (second copy never ran). Mutant: refusal identity is no longer `copy_failed`, and the side-effect assertion proves **the second copy ran** (`runtime-a1` count > 0) over a masked first-copy failure. Reached the second-copy layer.
9. **m_rbtamper** — rollback tamper gate disabled. Control REFUSED `backup_tampered` **before restoring** + destination untouched (`mrl_launch_draft.py` still present). Mutant: refusal identity changes to `rollback_verify_failed` (post-restore proof), and the side-effect assertion proves **tampered bytes reached the destination** (`cli.py` contains "rollback backup tampered"). Reached the destructive-mirror layer.

All three layered cases carry the exact side-effect assertions the gate requires (junction bytes in the backup; second copy after a masked failure; tampered bytes at the destination), not a mere "still refused for some reason."

## Coverage-gap list (R634's 10 enumerated classes)

| Class | Covered by | Status |
|---|---|---|
| partial/interrupted backup | design (evidence written atomically only after full verify) + B3 (failed first copy writes no evidence) + I1/R2 (missing evidence refuses) | **Indirect only — see F1** |
| decoy newer directory | R1 | Direct |
| tampered backup | I2, m_tamper, m_rbtamper (+ control) | Direct |
| wrong evidence file | I6 (`evidence_binding_mismatch`) | Direct |
| missing file | I3 | Direct |
| extra file | I4 | Direct |
| first-copy fail + second-copy success | B3 (positive) + m_rc1 (side-effect) | Direct |
| null exit code | test_null_exit | Direct |
| junction substitution | J1/J2/J3 + m_reparse | Direct |
| partial-install residue | R1 | Direct |

## Regression/provenance/environment findings

- Raw-exit discipline is correct: `Invoke-UpdateScript` redirects to temp **files** (not pipes) and reads `$global:LASTEXITCODE`; the runner spawns fresh `powershell.exe -File` with no piping. Refusal assertions are **typed** (`exit_code -ne 0` AND `stdout -match 'REFUSED <exact_code>'`), and the codes are mutually non-overlapping under `-match`, so `backup_evidence_missing` cannot spuriously satisfy a `backup_evidence_invalid` expectation.
- Mutants and positive/refusal cases both exercise the **real** operator script (only mutants use a patched copy); no self-referential projection.
- Modularity: the script is a single 884-line self-contained operator file (deliberate — the owner runs one file); responsibilities are cohesive (helpers + 4 phase blocks). Orchestrator-captured `modularity_check --check` = 0 failures. No finding.

## Defects / Findings with severity

- **F1 — Low (non-blocking observation).** The R634 class "partial/interrupted backup" has no *dedicated* checked-in test that plants a bare backup directory (or an orphaned `.tmp` evidence file) and asserts the next phase ignores it. The behavior is guaranteed by design (evidence is the sole binding; atomic temp+rename) and exercised indirectly by B3/I1/R2; the orchestrator's captured adversarial probe set includes an "orphaned .tmp" case. Recommend a follow-up positive test (plant `<backup_dir>` with no evidence + a leftover `*.tmp-*` → assert `backup_evidence_missing`). Does not block acceptance.
- **F2 — Low (observation).** Several typed refusal codes have no dedicated assertion: `backup_dir_collision`, `backup_verdict_not_pass`, `backup_evidence_invalid` (malformed/incomplete evidence JSON), `residue_removal_failed`, `stale_record_removal_failed`. Some are near-unreachable (collision) or hard to force; they are defense-in-depth. Non-blocking.
- **F3 — Info.** `test_null_exit.ps1` captures output via `2>&1 | Out-String` rather than the file-redirect used elsewhere. It is correct (a cmdlet pipe does not alter `$LASTEXITCODE`, and the assertion validates `code==1` + the typed refusal), but slightly inconsistent with the "never pipe" discipline stated in the fixtures. Non-blocking.
- **F4 — Low (environment).** Fixture cleanup is best-effort (`Remove-Item -ErrorAction SilentlyContinue`); a benign leftover `%TEMP%\ctl24-srcbind-<guid>\repo` remained after my clean run because a git/`.git` handle lingered past cleanup (confined to `%TEMP%`, does not affect correctness). Separately, fixture `git init`/`commit` invoke the owner's global gitleaks pre-commit template hook — current fixture content is secret-free, but a future fixture string resembling a credential could block the commit and fail the whole suite. Non-blocking; worth a note for future maintainers.

## Required rework

None blocking. F1 (dedicated partial/interrupted-backup + orphaned-.tmp test) and F3 (pipe consistency) are recommended as optional follow-ups.

## Reviewer conclusion

I independently executed the controller_update ps_tests suite (raw exit **0**, all 7 files and every assertion PASS), re-derived the R622–R643 requirement coverage from the amendment source, mapped every acceptance scenario AS-TX-1..AS-TX-6 to a named live test, confirmed all 9 mutations are unique load-bearing guards with the three layered-defense cases proven by concrete side-effect assertions, and verified fixture hygiene (temp-only; live controller/backup/runtime state untouched — `C:\SupervisorController` unchanged since 2026-09-01, `C:\SupervisorBackup` absent). Test quality is strong: real operator script in fresh `powershell.exe -File` processes, raw exit codes preserved, typed refusal assertions, fail-closed mutant generator, and side-effect proofs rather than bare nonzero-exit checks. The only gaps are minor and non-blocking.

**Verdict: PASS** (with the non-blocking F1/F3 observations noted for optional follow-up). DCV holds the authoritative full per-requirement pass and the R643 return-token confirmation.

---

Requested status for the orchestrator to record: **G4 = PASS**. The reviewer is read-only; it did not run `project_control.py`, git, or `gh`, and did not modify any repository file or live machine state.

---

## Orchestrating-verifier addendum (recorded by the orchestrator, not the reviewer)

The F2 gap list (`backup_verdict_not_pass`, `backup_evidence_invalid`, `stale_record_removal_failed`
without dedicated checked-in assertions) was covered LIVE this session by the orchestrating
verifier's independent probe pack (scratchpad `verifier_probes.ps1`, raw exit 0): V1 truncated
evidence JSON → `backup_evidence_invalid`; V2 verdict flipped to FAIL → `backup_verdict_not_pass`;
V3 evidence `backup_dir` escaping the backup root → `path_containment_violation`; V4 orphaned
same-directory `.tmp` file never consumed → `backup_evidence_missing` (also discharging the F1
orphaned-temp concern); V5 exclusively-locked stale activation record → `stale_record_removal_failed`
with NO rollback PASS evidence written, planted extra module removed by the bound mirror, and a
clean retry succeeding after unlock. F1/F2/F3/F4 remain recorded as optional follow-up test
candidates for the next controller-update task; none blocks acceptance.
