# Owner canary-continuation script — independent read-only review (2026-09-02)

Subject: `%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\run_m0t141_hotfix_and_canary.ps1`
(SHA-256 `77705bc300fa95347ffb7ea646fb0742578a0a2e493e73bedde92796056984ea`; deployed post-acceptance
under D-024 Amendment 44 R680; M0-T140 continuation, R658-style check carried forward from
Amendment 43). Saved VERBATIM by the orchestrator from the reviewer's agent-return channel
(transport entity-decoding only; report-preservation rule 2026-07-16). Reviewer: foreground
read-only `code-reviewer` subagent (never executed the script).

**Orchestrator closure of the review's PROCESS NOTE (its row 1):** the reviewer's sandbox blocks
PowerShell, so it requested orchestrator capture of the literal parser run. Captured at deploy time
in this session: `[System.Management.Automation.Language.Parser]::ParseFile` on the DEPLOYED file →
**parser errors: 0** on Windows PowerShell **5.1.26100.9168**. Row 1 closed. MINOR-1 requires no
change per the reviewer; the §6 observation confirms doctor's `--manifest` check subsumes
`verify-controller` for R680's enumerated list.

---

I have completed a comprehensive read-only review. All cross-checks are done. Here is my gate report.

---

# GATE REPORT — M0-T140 canary-continuation script review

**Task:** Independent read-only review of the external owner-run script
`C:\Users\MLFLL\AppData\Local\NYCBuildabilitySupervisor\ctl24-activation\run_m0t141_hotfix_and_canary.ps1`
**Authority:** D-024 Amendment 44 (R673 / R680 / R681 / R683); vehicle task M0-T140 (claimed); hotfix task M0-T141.
**Reviewed repo identity:** `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24` @ HEAD `e79d7ccc81f7008d11d6324b46ee3b9a48716302`, branch `candidate/D-024-mrl-option-b`.
**Reviewer:** code-reviewer (operationally read-only; never executed the script or any supervisor/updater command).

## VERDICT: PASS

The script faithfully implements the accepted contract (M0-T136 canary package + CONTROLLER_UPDATE_RUNBOOK §§3/4/5/5a/7/9a/10 + D-024 Am.44 R673/R680/R681/R683) and is PS-5.1-clean by static analysis. No BLOCKING defects. Two MINOR/observational notes below. One item (the literal `[Parser]::ParseFile` run) requires orchestrator-captured confirmation because PowerShell is categorically blocked in the reviewer sandbox — my static verification finds it parse-clean.

## Verification results (each with evidence)

**1. PS 5.1 parse — VERIFIED CLEAN (static); parser run to be orchestrator-captured.**
PowerShell is categorically blocked in this read-only sandbox, so I could not run `[Parser]::ParseFile`. Static evidence of parse-cleanliness: no PS7-only syntax (no `??` / `?.` / ternary / `-Parallel`); no `&&`/`||`; no trailing whitespace after any backtick continuation; every multi-line native command has balanced backticks; `do {…} while ($false)` with top-level `break`s is a valid PS 5.1 breakable block; hashtables with int keys, `-contains`, `[pscustomobject]@{}`, and `$script:` scoping are all 5.1-valid. **Request: orchestrator capture the ParseFile error count = 0 to formally close this row.** [Closed above: 0 errors, PS 5.1.26100.9168.]

**2. Task authority — PASS.** P0 reads `project-control\tasks\M0-T140.json` and blocks unless `task_id -eq 'M0-T140'` AND status in {claimed, in_progress, awaiting_gate}. The P7 draft binds `--task-packet …\M0-T140.json`. Cross-check: `M0-T140.json` has `"status": "claimed"` — gate satisfiable and correctly bound.

**3. Frozen-identity guards — PASS.** Before any install: worktree clean; `2245de74…` ancestor of HEAD; `git diff --quiet … -- tools/agent_supervisor` empty; `source_binding.json.commit_sha == 2245de74…`. Independently confirmed all four satisfiable at HEAD `e79d7ccc`.

**4. b5-01 reuse (R673) — PASS.** Item 2 is set PASS only from stored evidence (a `launch_manifest_refused` audit line naming `clean_status` AND no `one_shot_unit.json` under `mrl\canary-b5-01`). No rerun path exists (no `CANARY-UNTRACKED`, no `--run-id canary-b5-01`, no `New-Item -ItemType File`). Stored evidence confirmed present: exactly 1 matching audit record; `mrl\canary-b5-01\` has no `one_shot_unit.json`.

**5. Obsolete park removed / single start — PASS.** No `pending-approvals` / `resume-pending-prompt`. Exactly ONE `start` (`--run-id canary-b5-02r1 --mode supervised --max-cycles 1`); successor id distinct from preserved `canary-b5-02`; P0 refuses if the successor dir already exists (evidence never overwritten). Worker prompt byte-identical to the accepted package Step C prompt.

**6. Ordering (R680) — PASS.** backup → install → record-manifest → verify-manifest → doctor (NOT `--live`) → canonical recovery (`clear-recovery` only inside the PAUSED_RECOVERY branch; refuses on emergency stop / manual pause; HALTED/EMERGENCY_STOPPED/WAIT_FOR_OWNER stop with instructions) → re-draft → the one start → readout → harness → ten-row table + one token. recovery-status regexes match the live output format.

**7. Rollback boundary (R681) — PASS.** `$rolledBack` set ONLY on install / record-manifest / verify-manifest / doctor failure. Backup failure blocks without rollback. Canary-stage failures block, preserve evidence, no rollback. Rollback block runs the §10 post-rollback doctor.

**8. Command-shape fidelity — PASS.** Every invocation matches the live CLI (`record-manifest --config --out`; `doctor` without `--live`; `recovery-status`/`clear-recovery --checkout`; `start --mode --checkout --launch-manifest --run-id --max-cycles --prompt`, `--worktree` correctly omitted in the manifest form; P7 draft flags all exist in `mrl_launch_draft.py` and match Step A verbatim except the packet path). No angle-bracket placeholders; no retyped 64-hex runtime key.

**9. Ten-row reachability — PASS.** Item 2 PASS derives only from stored evidence. Item 7 PASS requires exit 0 AND `stopped=` in {stage_complete, ask_blocking, operator_declined} (loop.py emits exactly these; start report prints `stopped={value}`) AND exactly 1 `mrl_one_shot_launched` record for `canary-b5-02r1` (currently 0 in audit.jsonl). Final token `CANARY_PACKAGE_PASS` only when nothing blocked and 10/10 PASS, else `CANARY_PACKAGE_BLOCKED`.

| Item | PASS at | FAIL / block / NOT-RUN at |
|---|---|---|
| 1 clean-base manifest launch | start exit 0 | FAIL on nonzero exit → block; earlier break leaves NOT-RUN → token BLOCKED |
| 2 reused b5-01 refusal | stored evidence only | block if evidence absent; NOT-RUN on earlier P0 break |
| 3 child authentication | readout | FAIL → block |
| 4 model/version identity | readout | FAIL → block |
| 5 updater disablement | readout | FAIL → block |
| 6 restricted tool denial | readout | FAIL → block |
| 7 one successful one-shot | exit0 + settled stopped + exactly 1 launch | FAIL → block |
| 8 bounded fan-out + denial | ledger | FAIL → block |
| 9 process-tree cleanup | descendant proof | FAIL → block |
| 10 raw exit-code harness | harness exit 0 | FAIL → block |

**10. PS 5.1 pitfalls — PASS.** No `&&`/`||`/ternary/`?.`; `$LASTEXITCODE` captured immediately after every judged native call; no `Sort-Object` newest-backup selection (rollback binds via `controller_backup_evidence.json` inside the updater); `Format-Table` output is display-only.

## Findings

**MINOR-1 (robustness, non-blocking)** — row-7 `stopped=` parse is first-match on the whole output; in practice only the DISPATCHED line emits the literal token. Risk negligible; no change required.

**OBSERVATION (not a defect)** — runbook §6 `verify-controller` is not a discrete step; §7 doctor with `--manifest --config` performs the same check, and R680's enumerated list does not require §6 separately. Coverage intact.

**PROCESS NOTE** — orchestrator to capture the literal parser run (expected 0 errors). [Closed: 0 errors captured at deploy.]

**Recommendation to orchestrator:** record gate result PASS; attach the captured ParseFile error count (expected 0) as the closing evidence for review row 1.
