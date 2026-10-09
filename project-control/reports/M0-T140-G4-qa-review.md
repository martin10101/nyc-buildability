# M0-T140 — G4 independent QA verification, preserved VERBATIM

Returned by the read-only `qa-engineer` agent through the agent-return channel on 2026-09-03;
saved verbatim by the orchestrator (transport entity-decoding only: `&amp;` decoded).

---

# GATE REPORT — M0-T140 (canary-execution closure), independent G4

**Verdict: PASS**

**Task:** M0-T140 canary-execution closure (D-024 Amendment 47, R714–R724)
**Reviewed content head:** `704df81463b13f0d517ab06f9a635a112e054a24`
**Reviewer:** qa-engineer (read-only; no provider canary launched, no PS harness re-run, no files edited in the repo)
**Runtime dir:** `%LOCALAPPDATA%\NYCBuildabilitySupervisor\9aca7075…` (= `C:\SupervisorController`)

## Frozen-head confirmation
Candidate tip is `8da429c8` (parent = reviewed `704df814`). My review worktree's own HEAD is `d8b3899f` (= divergent `refs/heads/main`) — NOT the comparison target. Diffing the reviewed SHA against the true candidate tip:

```
git diff --name-status 704df814..8da429c8
A  project-control/gates/M0-T140-G2.json
A  project-control/reports/M0-T140.json
M  project-control/state.json
M  project-control/tasks/M0-T140.json
git log --oneline 704df814..8da429c8
8da429c8 M0-T140 G2 PASS + submitted to awaiting_gate
```
The single later commit touches ledger records only. Content is frozen at `704df814`. ✔

## 1. Ten-row R587 table (§2) — each re-derived from durable artifacts

Sources: `mrl\canary-b5-02r3\{one_shot_unit,codex_decision,subagent_ledger,launch_verification}.json`; `audit.jsonl` (hash-chain intact, **0 breaks**, seq 1–68); `supervisor_journal.sqlite3` (transitions 1–34).

| # | Item | Report | My re-derived verdict | Durable basis I checked |
|---|---|---|---|---|
| 1 | clean-base manifest launch | PASS | **PASS** | r3 `launch_verification.json`: `clean_status=true`, `head_sha=37b2c3b6`, `ok=true`; audit seq 54 `launch_manifest_verified`; journal transition 27 `preflight_pass` |
| 2 | live-repo mismatch refusal (REUSED) | PASS | **PASS** | b5-01 `launch_verification.json`: `clean_status=false`, `ok=false`; audit seq 17 `launch_manifest_refused` (clean_status mismatch, `policy_result=REFUSED`); **no `canary-b5-01\one_shot_unit.json`**; `mrl_one_shot_launched` count for b5-01 = **0** |
| 3 | child auth (split legs) | PASS | **PASS** | Claude: `runtime_identity.session_id=44c7cce4…`, `worker_result.outcome=COMPLETED`. Codex: `codex_decision.json` 4430 B, schema `mrl_codex_decision_record/v1`, `reviewer_version=0.146.0`, parses |
| 4 | runtime model/version identity | PASS | **PASS** | `runtime_identity.primary_model=claude-fable-5`; argv `--model claude-fable-5`; `model_mismatch=false`; `auxiliary_models=[claude-haiku-4-5-20251001]`; `context_tier_used=false`; `launch.version=2.1.252` **== manifest `dispatch.claude_version=2.1.252`** (and `launch.chain.combined_sha256 == manifest claude_chain_sha256`) |
| 5 | updater disablement | PASS | **PASS** | `launch.child_env_updater.DISABLE_AUTOUPDATER="1"` |
| 6 | Bash absent & never executed | PASS | **PASS** | argv `--disallowedTools` = `[Bash, mcp__*]`; `main_tool_uses = {Agent:4, Glob:1, Read:3, StructuredOutput:1}` (no Bash); `worker_result.summary` + `permission_denials[0]` show `python --version` delegated to general-purpose subagent and DENIED (R575) |
| 7 | one successful one-shot (post-review settled) | PASS | **PASS** | `returncode=0`, `ok=true`, `worker_result.outcome=COMPLETED` via `result_source=structured_output`; exactly **1** `mrl_one_shot_launched` (audit seq 57); review verdict present (REVISE); `run_budget/canary-b5-02r3.exit_reason=operator_declined` |
| 8 | bounded fan-out + over-limit denial | PASS | **PASS** | `accounting`: issued=2≤2, denied=2≥1, processes_total=3≤3, subagents_live=0; `subagent_ledger.json`: 2 Explore issued+completed, denials R567 (over-limit) + R575 (out-of-inventory) |
| 9 | full process-tree cleanup | PASS | **PASS** | `descendant_proof.proven=true`, `source=windows_toolhelp32`, `unreleased_child_ids=[]` (root_pid 23660) |
| 10 | raw PowerShell exit-code preservation | PASS | **PASS (owner-attested, not artifact-derivable)** | Rests on owner attestation `CANARY_PACKAGE_PASS` + M0-T143 wave; explicitly NOT re-run per R715. See Finding 1 |

## 2. §3 live-proven items 1–8 — exact field checked

1. Fable pin — `one_shot_unit`: `launch.argv[--model]=claude-fable-5`, `runtime_identity.primary_model=claude-fable-5`, `model_mismatch=false`. ✔
2. Claude auth + valid WorkerResult — `session_id=44c7cce4…`, `worker_result.outcome=COMPLETED`, `result_source=structured_output`. ✔
3. Restricted tool surface — `launch.argv` `--allowedTools [Read,Grep,Glob,Agent]`, `--disallowedTools [Bash,mcp__*]`; `main_tool_uses` has no out-of-surface tool. ✔
4. Bounded subagents + over-limit denial — `subagent_ledger.denials` R567/R575; `accounting` caps. ✔
5. Codex auth + valid decision — `codex_decision`: `model_used=gpt-5.6-sol`, `decision=REVISE`, `git.task_head_sha=37b2c3b6`, `observed_base_sha=d8b3899f`, `normalized_remote_url=…/nyc-buildability`. ✔
6. Process-tree cleanup both sides — worker `one_shot_unit.descendant_proof.proven=true` (pid 23660) + reviewer `codex_decision.descendant_proof.proven=true` (pid 15720), both `windows_toolhelp32`, remaining `[]`. ✔
7. Immutable install + manifest binding — `controller_update_evidence.json`: `commit_sha=3f4cee86…`, `commit_tree_sha=04688351…`, `subtree_tree_sha=209026fd…`, `subtree_path=tools/agent_supervisor`, 199 files (matches report exactly). ✔
8. Raw PS exit-code preservation — owner-attested (same basis as row 10). ✔

## 3. Timeline (§1) vs journal/audit
Every §1 row maps to audit seq 51–68 and journal transitions 26–34 with matching timestamps: `owner_answer_validated` (T26, 00:43:14), `preflight_pass` (T27), launch (audit 57, 00:43:18.814Z), settle (audit 58, 00:45:57), evidence packet (T31), `codex_review_decision` REVISE returncode 0 model gpt-5.6-sol (audit 63, 00:46:36.408Z), `tier_ask_blocking` (T34), `supervised_approval_answered` deny (audit 68, 00:46:36.552Z). ✔

## 4. Deployed journey script
- Exists at `…\ctl24-activation\run_first_supervised_journey.ps1`. ✔
- `Get-FileHash SHA256 = 1b636d591dffaba14e1e0cf578eb6f76c7fdbf9ee13291ca15a5ecf5d0e34a65` (== expected). ✔
- `[Parser]::ParseFile` under **PS 5.1.26100.9168 → Parse errors: 0**. ✔
- Read confirms: J1 `-Phase verify-manifest` only (no install/backup); J2 model-pin VERIFY-ONLY via `ReadAllText` (no write to `model_selection.toml` on any path); `--max-cycles 1`; `--deny-tool Bash` with `--allow-tool` excluding Bash; `--agent Explore --max-concurrent 2 --max-total 2`; task packet `M0-T107.json` (`task_id=='M0-T107'` guard); J0 guards for preserved canary evidence + refuses if `journey-m0t107-01` dir exists (fresh run id); only negative-assertion strings for push/PR/merge/deploy (git usage = status/merge-base/diff only). ✔
- **Never executed:** no `mrl\journey-m0t107-01` dir; no `C:\SupervisorController\mrl\journey_launch_manifest.json`. ✔

## 5. No provider rerun in this closure
`audit.jsonl` ends at seq 68 (`supervised_approval_answered`, deny). `mrl_one_shot_launched` totals: b5-02=1, r1=1, r2=1, r3=1 — last launch was r3 (audit 57); nothing after. No new run dir created. ✔ (See Finding 3 re: dir count.)

## 6. M0-T107 readiness
`M0-T107.json` at `704df814`: `status="claimed"`, `dependencies=["M0-T096"]`, `allowed_paths=["docs/D024_PORTABILITY_PLAN.md","project-control/reports/M0-T107-portability-plan.md"]` (exactly two doc paths, no supervisor-code overlap). `M0-T096.json`: `status="accepted"` (accepted 2026-08-28). ✔

## 7. Evidence-map coverage
`M0-T140-evidence-map.json` (schema `directive_evidence_map/v1`) carries **41** requirement rows. verification.json `M0-T140.applicable_requirement_ids` = **41**, and the two sets are **identical** (no diff either direction). Spot-checked 6 rows against cited artifacts: **R657** (r2 one-shot at audit seq 42, r3 at seq 57 — one per successor ✔), **R699** (both r2 and r3 pinned `claude-fable-5`, `model_mismatch=false` ✔), **R715** (audit ends seq 68, `operator_declined` ✔), **R721** (journey script sha + PS 5.1 0 errors ✔), **R722** (no journey run dir ✔), **R724** (`M0-T140-return-report.md` ends with exactly `FIRST_REAL_SUPERVISED_RUN_READY`, single occurrence ✔). R682/R698 (absent from the 41) confirmed as return-token requirements bound to *other* D-024 units (schema hotfix / settlement repair), correctly non-applicable to M0-T140 — not a silent drop. ✔

---

## Numbered findings

1. **MINOR (disclosed limitation).** R587 item 10 (raw PowerShell exit-code preservation) is the only row not re-derivable from the r3 runtime artifacts; it rests on owner attestation `CANARY_PACKAGE_PASS` plus the separately-gated M0-T143 wave, and per R715 the harness is deliberately not re-run. The report states this transparently. No action; noted for completeness.

2. **MINOR (informational — acceptance precondition, not a producer defect).** The `verification.json` M0-T140 row is still a claim-time skeleton (`reviewed_sha`/`verified_at` absent; note: "pending rows verify nothing"). This G4 PASS covers the evidence report and durable artifacts; directive acceptance additionally requires the independent `directive-compliance-verifier` to populate the 41 PASS verdicts at `reviewed_sha == HEAD` (producer ≠ verifier). That pass is a separate, still-pending step the orchestrator sequences before accept.

3. **MINOR (transparency).** Task item 5 says "the four canaries," but the runtime `mrl\` holds five dirs: `canary-b5-01` (the clean-status refusal — never launched a provider) plus the four one-shot-launching runs `canary-b5-02/-02r1/-02r2/-02r3`. This is consistent with the report (b5-01 is the separate refusal canary named in item 1); no new run dir was created in the closure. Not a defect.

No BLOCKING findings. The evidence is internally consistent and matches every durable artifact cross-checked (hash-chained audit, journal transitions/state_kv, per-run MRL unit files, launch manifests, install evidence, deployed script hash + parse). **Verdict: PASS.**

Relevant absolute paths:
- Evidence report: `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T140-canary-execution-evidence.md` (at `704df814`)
- Evidence map: `…\project-control\reports\M0-T140-evidence-map.json`
- Directive verification: `…\project-control\directives\D-024-fable-codex-loop\verification.json`
- Journey script: `C:\Users\MLFLL\AppData\Local\NYCBuildabilitySupervisor\ctl24-activation\run_first_supervised_journey.ps1`
- Runtime artifacts: `C:\Users\MLFLL\AppData\Local\NYCBuildabilitySupervisor\9aca7075…\{audit.jsonl, supervisor_journal.sqlite3, mrl\canary-b5-02r3\*}`
