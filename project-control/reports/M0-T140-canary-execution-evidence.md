# M0-T140 — Canary execution evidence: commissioning COMPLETE (canary-b5-02r3, all ten R587 items PASS)

Owner attestation (D-024 Amendment 47, R714): the owner-run commissioning completed with all
ten R587 items PASS and `CANARY_PACKAGE_PASS`. This record derives every row from DURABLE
artifacts (runtime dir `9aca7075…` = `C:\SupervisorController`; audit seq 54–68; journal
transitions 26–34; `mrl\canary-b5-02r3\*`), never from narrative.

## 1. Commissioning timeline (durable)

| When (UTC) | Event |
|---|---|
| 00:43:14 | `WAIT_FOR_OWNER → PREFLIGHT` on `owner_answer_validated` (transition 26 — the canonical `resume-after-answer` exit from the b5-02r2 ask; the owner typing the script was the answer) |
| 00:43:17–18 | launch manifest verified (audit 54); run budget started; preflight PASS (transition 27) |
| 00:43:18 | ONE `mrl_one_shot_launched` for canary-b5-02r3 (audit 57 — exactly one provider launch) |
| 00:45:57 | one-shot settled OK (audit 58); checkpoint valid (transitions 28–30) |
| 00:45:58 | evidence packet built (transition 31) |
| 00:46:36 | **`codex_review_decision` decision REVISE, model gpt-5.6-sol, returncode 0** (audit 63); schema-valid (transitions 32–33); supervised hold (34, `tier_ask_blocking`); `supervised_approval_answered` **deny** (audit 68) |
| 00:46:36 | run closed: `exit_reason = operator_declined` (journal `run_budget/canary-b5-02r3`) — the settled post-review family; per R714/R715 this is the owner's clean close, NOT a defect |

## 2. The ten R587 items, from durable artifacts

| # | Item | Result | Durable basis |
|---|---|---|---|
| 1 | clean-base manifest launch | PASS | audit 54 `launch_manifest_verified` + transition 27 `preflight_pass`; manifest drafted at clean HEAD `37b2c3b6` |
| 2 | live repository mismatch refusal | PASS (REUSED) | preserved b5-01 `launch_manifest_refused`/`clean_status` audit rows; no `mrl\canary-b5-01\one_shot_unit.json` (never rerun, R673) |
| 3 | child authentication (split legs, R708) | PASS | Claude leg: live session `44c7cce4-e58a-4ee3-994e-fc885775dfeb` in `one_shot_unit.json`; Codex leg: `codex_decision.json` (4,430 B) parses — schema `mrl_codex_decision_record/v1`, reviewer_version 0.146.0 |
| 4 | runtime model/version identity | PASS | `runtime_identity.primary_model = claude-fable-5`; argv `--model claude-fable-5`; `model_mismatch: false`; auxiliary `claude-haiku-4-5-20251001` only; `[1m]` tier false; `launch.version 2.1.252` == manifest pin |
| 5 | updater disablement | PASS | `child_env_updater.DISABLE_AUTOUPDATER = "1"` measured from the exact child env |
| 6 | Bash absent and never executed (bare deny) | PASS | argv `--disallowedTools` carries Bash; correlated `main_tool_uses = {Agent:4, Glob:1, Read:3, StructuredOutput:1}` (no Bash row); worker summary confirms the Bash step was refused, not silently done |
| 7 | one successful one-shot result (post-review settled) | PASS | exit 0; `ok: true`; worker outcome COMPLETED via `structured_output`; exactly 1 `mrl_one_shot_launched` (audit 57); **review verdict present** (REVISE); stop `operator_declined` in the settled family |
| 8 | bounded subagent fan-out + over-limit denial | PASS | accounting `issued=2 ≤2, denied=2 ≥1, processes_total=3 ≤3, subagents_live=0`; `subagent_ledger.json` corroborates |
| 9 | full process-tree cleanup | PASS | `descendant_proof.proven: true`, source `windows_toolhelp32`, `unreleased_child_ids: []` |
| 10 | raw PowerShell exit-code preservation | PASS | P10 ran `run_ps_tests.ps1` runner to exit 0 in the owner-typed run (owner-attested `CANARY_PACKAGE_PASS`; the harness is deterministic and was independently green in the M0-T143 wave via `test_runbook_parse.ps1` PS-EXIT=0) — not re-run here per R715 (no repeating completed verification) |

## 3. Live-proven production path (R718 record)

The following are now **live-proven** on this host, each from the named durable artifact:

1. **Exact original Fable 5 pin `claude-fable-5`** — manifest pin + argv + correlation-bound
   transcript primary model, `model_mismatch: false` (one_shot_unit.json).
2. **Claude authentication and valid WorkerResult** — live session `44c7cce4…`; schema-bound
   `worker_result` outcome COMPLETED via `structured_output`.
3. **Restricted tool surface** — explicit allow Read/Grep/Glob/Agent, bare-deny Bash +
   `mcp__*`; tool-use census shows zero out-of-surface executions.
4. **Bounded subagents and over-limit denial** — Explore-only inventory, 2/2 caps enforced,
   third launch + general-purpose launch both denied, ledger-corroborated.
5. **Codex authentication and valid review decision** — a fresh ephemeral read-only
   gpt-5.6-sol child returned a schema-valid REVISE verdict; the controller built the
   git-bound `CodexDecision` (task head `37b2c3b6`, observed base `d8b3899f` via real
   ls-remote) — the M0-T143 repair live-proven end-to-end.
6. **Process-tree cleanup** — descendant-zero proven from a real `windows_toolhelp32`
   snapshot on both the worker and reviewer sides.
7. **Immutable installation and manifest binding** — installed from immutable commit
   `3f4cee86` (tree `04688351`, subtree `209026fd`), byte-verified source-to-destination,
   manifest recorded and re-verified (audit 54; controller_update_evidence.json).
8. **Raw PowerShell exit-code preservation** — P10 harness exit 0 in the owner-typed run.

Additionally live-proven en route: the canonical `resume-after-answer` WAIT_FOR_OWNER exit,
the supervised-mode hold + owner answer surface (`supervised_approval_answered`), and the
R706 observability path (the b5-02r2 failure is now typed with the parsed provider error).

## 4. GitHub boundary — stated honestly (R719)

**NOT live-proven by this commissioning:** any supervisor-driven GitHub push, PR creation,
CI trigger, or merge. The doctor's `push_policy` row states "NO push is executed in this
phase"; `audit_anchor_option_a` is NOT ACTIVE (needs controller credentials AND explicit
owner activation); the candidate branch has no upstream and nothing was pushed. GitHub
push/PR/CI/merge by humans and by this orchestrator session under ADR-006 Tier A remains
proven by ordinary project history — but the SUPERVISED LOOP's own GitHub surface has zero
live evidence and stays unproven until an explicitly authorized live exercise.

## 5. Closure basis

M0-T140's mandate (R644–R663, R673–R674, R679–R685, R697, R699 + Amendment 47 R714–R724) is
discharged: the dedicated canary-execution vehicle stayed claimed through three preserved
attempts and one passing commissioning; every canary deliverable (refusal evidence, causal
traces, corrected scripts, ten-row readouts) is preserved. Acceptance proceeds under the
standard gates with no provider rerun (R715/R716).
