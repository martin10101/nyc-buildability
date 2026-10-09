# M0-T140 — G3 independent closure review, preserved VERBATIM

Returned by the read-only `code-reviewer` agent through the agent-return channel on 2026-09-03;
saved verbatim by the orchestrator (transport entity-decoding only: `&lt;` decoded).

---

# G3 Gate Report — M0-T140 (canary-execution vehicle closure)

**Task:** M0-T140 — dedicated read-only canary-execution vehicle (D-024 Amendment 43/47)
**Reviewed head:** `704df81463b13f0d517ab06f9a635a112e054a24`
**Reviewer:** independent (read-only); producer = orchestrator
**Verdict: PASS** (no BLOCKING findings; four MINOR/advisory notes, all transparency-only)

## Method

Read-only verification against durable artifacts under the runtime dir `9aca7075…` (= `C:\SupervisorController`), the deployed activation dir, and the git repo. Journal read via `sqlite3` `mode=ro`. Per D-024 Amendment 47 (R714/R715) nothing provider-facing was rerun; every conclusion is derived from a preserved artifact.

## Scope confirmation (review item 5)

- `git diff --name-status 704df814 HEAD` → only `project-control/gates/M0-T140-G2.json`, `project-control/reports/M0-T140.json`, `project-control/state.json`, `project-control/tasks/M0-T140.json` (ledger/gate records only). **Confirmed.**
- `git log --name-only 37b2c3b6..704df814` → exactly 2 commits: `704df814` (reports: `M0-T140-canary-execution-evidence.md`, `-evidence-map.json`, `-return-report.md`) and `5811d6d2` (directive registry: D-024 `manifest.json`/`requirements.json`/`source-047-amendment.md`/`verification.json`). **Nothing in `tools/` at all, nothing in accepted packets.** Scope claim is accurate (in fact tighter than "nothing in tools/ outside controller_update" — zero tools/ changes).

## Finding 1 — Ten-item R587 table accuracy (review item 1) — PASS

Every cross-checkable row of §2 verified against `one_shot_unit.json`, `codex_decision.json`, `audit.jsonl` (seq 54–68), the journal, and `subagent_ledger.json`:

- **Item 1 (clean-base launch):** audit seq 54 `launch_manifest_verified` VERIFIED (`head_sha 37b2c3b6…`, `clean_status true`, match true in `launch_verification.json`); transition 27 `PREFLIGHT→START_CLAUDE preflight_pass`. ✓
- **Item 2 (mismatch refusal, REUSED):** canary-b5-01 audit seq 17 `launch_manifest_refused REFUSED`; the `mrl\canary-b5-01\` dir holds only `launch_verification.json`+`profile` (no `one_shot_unit.json`) → never rerun (R673). Legitimate reuse, transparently labeled. ✓
- **Item 3 (child auth, split legs):** Claude leg session `44c7cce4-e58a-4ee3-994e-fc885775dfeb` in `one_shot_unit.json`; Codex leg `codex_decision.json` is exactly **4,430 B** (matches claim), schema `mrl_codex_decision_record/v1`, `reviewer_version 0.146.0`. ✓
- **Item 4 (model/version identity):** `runtime_identity.primary_model=claude-fable-5`; argv `--model claude-fable-5`; `model_mismatch:false`; `auxiliary_models:["claude-haiku-4-5-20251001"]` only; `context_tier_used:false` ([1m] tier off); `launch.version 2.1.252`. ✓
- **Item 5 (updater disabled):** `child_env_updater.DISABLE_AUTOUPDATER="1"`. ✓
- **Item 6 (Bash absent/never run):** argv `--disallowedTools` carries `Bash`; `--allowedTools` excludes it; `main_tool_uses={Agent:4,Glob:1,Read:3,StructuredOutput:1}` (no Bash row); `permission_denials` shows the `general-purpose` Bash attempt denied (R575); worker summary states python --version was "NOT executed." Bash was **refused under a genuine attempt**, not silently done. ✓
- **Item 7 (one settled one-shot):** `returncode 0`, `ok:true`, worker `outcome COMPLETED` via `structured_output`; audit has **exactly one** `mrl_one_shot_launched` for canary-b5-02r3 (seq 57 — the other three launches at seq 22/32/42 belong to prior attempts b5-02/r1/r2); review verdict present (REVISE); stop `operator_declined`. ✓
- **Item 8 (bounded fan-out + over-limit deny):** `accounting issued=2/denied=2/processes_total=3/subagents_live=0`; `subagent_ledger.json` corroborates (2 issued Explore, 2 denials: general-purpose R575, over-limit R567). ✓
- **Item 9 (tree cleanup):** `descendant_proof.proven:true`, source `windows_toolhelp32`, `unreleased_child_ids:[]`. ✓
- **Item 10 (raw PS exit-code):** see MINOR-1 — owner-attested + cross-wave, not r3-local. Transparently stated.

§1 timeline: journal transitions 26–34 match exactly (26 `WAIT_FOR_OWNER→PREFLIGHT owner_answer_validated` … 34 `POLICY_CHECK→WAIT_FOR_OWNER tier_ask_blocking`); `run_budget/canary-b5-02r3` `exit_reason=operator_declined` confirmed in `state_kv`; audit seq 63 `codex_review_decision REVISE / model gpt-5.6-sol / returncode 0`; seq 68 `supervised_approval_answered deny`. §3 live-proven list (items 1–8) is consistent with the same artifacts. **All accurate.**

Note the REVISE verdict does not undercut "all ten PASS": R587 items test machinery (real Claude+Codex auth, tool restriction, subagent bounds, cleanup, schema-valid review present, supervised hold, owner answer), not an APPROVE outcome. The worker honestly reported it could not run a Bash command under the restricted surface; the reviewer correctly returned REVISE; the owner declined; the run closed cleanly. This is a successful commissioning of the loop.

## Finding 2 — §4 GitHub boundary honesty (review item 2) — PASS

Doctor `doctor_live_probe.json`:
- `push_policy` (ok:true): "main and force pushes are hard-denied; … **NO push is executed in this phase**" — matches the report's quote.
- `audit_anchor_option_a` (ok:true): "Option A mechanism present … **NOT ACTIVE: publication needs controller credentials AND an explicit owner activation**" — matches "NOT ACTIVE."

`git status -sb` → `## candidate/D-024-mrl-option-b` with **no upstream** → nothing pushed. The "supervised-loop GitHub surface unproven" claim is accurate and honestly bounded.

## Finding 3 — Journey script safety as code (review item 3) — PASS

`run_first_supervised_journey.ps1` sha256 = `1b636d591dffaba14e1e0cf578eb6f76c7fdbf9ee13291ca15a5ecf5d0e34a65` — **matches the claimed hash exactly.** Reviewed all paths:

- **No install/backup/model-edit/push/PR/merge/deploy in any path.** All git calls are read-only (`status --porcelain`, `merge-base --is-ancestor`, `diff --quiet`). The only updater call is `-Phase verify-manifest` (no install/backup/rollback phase). `model_selection.toml` is only read (`[System.IO.File]::ReadAllText`), never written (J2 verify-only; forbidden-pin + fallback `[]` checks). J7 explicitly performs no push/PR/merge/deploy; produced files stay uncommitted for the orchestrator under normal gates.
- **Verify-before-anything:** J0 preconditions (clean tree, `3f4cee86` ancestor, `tools/agent_supervisor` matches frozen, binding `commit_sha==3f4cee86`, packet task_authority) → J1 verify-manifest → only then J5/J6.
- **Canonical recovery exits only:** WAIT_FOR_OWNER→`resume-after-answer`; PAUSED_RECOVERY→`clear-recovery`; **blocks** on HALTED/EMERGENCY_STOPPED and on emergency-stop/manual-pause; requires settle at PREFLIGHT/IDLE or blocks. Fail-closed on any other state.
- **ONE `start --max-cycles 1`** on run-id `journey-m0t107-01`, manifest drafted against packet `M0-T107.json`.
- **Tool surface:** `--allow-tool Read/Grep/Glob/Agent/Write/Edit`, `--deny-tool Bash` (Bash present in inventory but bare-denied — the same proven pattern as r3). Write/Edit are scoped to M0-T107's two allowed doc paths.
- **Explore-only subagents 2/2:** `--agent Explore --max-concurrent 2 --max-total 2`.
- **Fail-fast + evidence preservation:** every failure sets `$blockNote` and breaks; J6 nonzero exit preserves evidence under `mrl\journey-m0t107-01` ("nothing to roll back").
- **Guards preserved evidence:** J0 requires all four preserved canary `one_shot_unit.json` files to exist and **refuses to overwrite an existing** `mrl\journey-m0t107-01` dir.

No path violates the stated safety properties.

## Finding 4 — Task-selection soundness R720 (review item 4) — PASS

`M0-T107` status = `claimed` (runnable), `allowed_paths` = two documentation files (`docs/D024_PORTABILITY_PLAN.md`, `project-control/reports/M0-T107-portability-plan.md`), dependency `M0-T096` = **accepted**. Alternatives are strictly higher risk or not ready: `M0-T109` (claimed) touches security-critical `.claude/hooks`; `M0-T133` is in **rework** and touches production `tools/agent_supervisor` (checkpoint_envelope/claude_runner/loop); `M0-T135` is **backlog** (not claimed → fails the task_authority pre-gate). M0-T107 is the only claimed, docs-only, accepted-dependency task. The lower-risk claim is fair.

## MINOR / advisory (non-blocking, for the record)

- **MINOR-1:** Ten-item row 10 (raw PowerShell exit-code preservation) is the only row **not** backed by an r3-local durable artifact; it rests on the owner's `CANARY_PACKAGE_PASS` attestation plus the cross-wave M0-T143 `test_runbook_parse.ps1 PS-EXIT=0`. Correct posture under R714/R715 (no rerun) and transparently labeled; noted as the weakest evidentiary leg.
- **MINOR-2:** Row 2 is PASS(REUSED) from b5-01; verified durable (audit seq 17 REFUSED; no b5-01 one_shot_unit). Legitimate under R673.
- **MINOR-3:** The journey script uses `$ErrorActionPreference='Continue'` and relies wholly on explicit `$LASTEXITCODE` checks + `do{}while($false)` breaks. Every material step is checked, so the fail-fast path is sound; flagged only because an unchecked native failure would not auto-throw.
- **MINOR-4 / OBSERVATION:** `launch_verification.json` and the subagent contract record `repo_root = …\nyc-development-feasibility-claude-pack` while the worker actually executed in `worktree = …\ctl24` (per checkpoint.worktree and the denial-prompt cwd). Pre-existing repo_root/worktree split in the canary launch manifest; the report makes no repo_root claim, `head_sha 37b2c3b6` verified clean, so this is not an M0-T140 evidence inaccuracy. Verify-manifest's read-only behavior is inherited from the accepted M0-T142/T143 controller lineage (outside this diff).

## Conclusion

The evidence report's ten-item table, §3 live-proven list, and §4 GitHub boundary are accurate and reproducible against durable artifacts; the deployed journey script matches its claimed hash and is safe as code; task selection is sound; and the diff scope is clean (ledger/reports/directives only). No BLOCKING defects.

**VERDICT: PASS**

### Reproduction (read-only)
- `git -C <wt> diff --name-status 704df814 HEAD` and `git -C <wt> log --name-only 37b2c3b6..704df814`; `git -C <wt> status -sb`
- `sha256sum` of `%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\run_first_supervised_journey.ps1`
- Read `…\9aca7075…\mrl\canary-b5-02r3\{one_shot_unit,codex_decision,subagent_ledger,launch_verification}.json`
- Parse `…\9aca7075…\audit.jsonl` for `mrl_one_shot_launched` seq/run_id and seq 54–68
- `sqlite3` `mode=ro` on `supervisor_journal.sqlite3`: `transitions` 26–34, `state_kv` `run_budget/canary-b5-02r3`
- Parse `…\ctl24-activation\doctor_live_probe.json` checks `push_policy`, `audit_anchor_option_a`
- Read `project-control/tasks/{M0-T096,M0-T107,M0-T109,M0-T133,M0-T135}.json`

Relevant absolute paths:
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T140-canary-execution-evidence.md`
- `C:\Users\MLFLL\AppData\Local\NYCBuildabilitySupervisor\9aca707563cfe6e2cdeeee99e5d153951936dc46edac131889c37c2a9f713b6a\mrl\canary-b5-02r3\one_shot_unit.json` (and `codex_decision.json`, `subagent_ledger.json`, `launch_verification.json`)
- `C:\Users\MLFLL\AppData\Local\NYCBuildabilitySupervisor\9aca707563cfe6e2cdeeee99e5d153951936dc46edac131889c37c2a9f713b6a\audit.jsonl`, `…\supervisor_journal.sqlite3`
- `C:\Users\MLFLL\AppData\Local\NYCBuildabilitySupervisor\ctl24-activation\run_first_supervised_journey.ps1`, `…\doctor_live_probe.json`
