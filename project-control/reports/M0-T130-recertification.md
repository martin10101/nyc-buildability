# M0-T130 — R247 recertification at the post-fix frozen identity (D-024-R424)

Executed by the orchestrator 2026-08-31 in the PRIMARY control checkout, immediately
after M0-T130's acceptance (`f271fbe9`). ONE recertification at ONE identity;
re-triggered by the M0-T130 supervisor change.

## 1. The new frozen identity

| Anchor | Value |
|---|---|
| Material commit (supervisor content) | `20bfa449` (M0-T130 fix; accepted at `f271fbe9`) |
| `tools/agent_supervisor` tree | `37020c3797ce62659f59c59cf9857990dff67372` (moved from `b3921009...` by the fix: claude_runner.py deferred injection + helper) |
| Golden pack blob | UNCHANGED (no golden edit in this task) |
| Provider CLI | Claude Code 2.1.251 UNDRIFTED — `sha256_head+size` `d6f6c29a8ac6b3cf...`, 217,360,032 B (reproduced this session) |
| Codex CLI | codex-cli 0.146.0 unchanged |
| Controller manifest | RE-RECORDED binding this tree: 125 files, digest `26a05096650cb457...` (prior manifest file sha256 `2f3c22e5...` / internal digest `841ed11c...` recorded pre-overwrite); round-trip verification passed; `verify-controller` PASS including the external config.toml binding |

## 2. Suite evidence at the frozen identity

| Run | Result |
|---|---|
| Golden certification pack | **42 passed** — twice this session at these exact runtime bytes (17.99s and 24.63s) |
| WHOLE supervisor suite (all test files, one process) | **3,039 passed, 2 skipped, 0 failed** (256.5s orchestrator run; **independently reproduced by the G4 reviewer: 3,039/2 in 267.4s**) |
| Runner pack | 78 passed — reproduced independently by G3, G4, and the DCV |

Baseline reconciliation (freeze rule): 3,035 (M0-T129 certification) + 4 new
ReservedTurnDeliveryTests nodes = 3,039; one existing test repurposed in place to the
fixed semantics (disclosed and reviewer-endorsed); no test file removed.

## 3. Teeth and control plane

`modularity_check --check` failures 0 / REAL_EXIT=0 (run UNPIPED; reviewed path-exact
expiring exception for claude_runner.py per G3-C1, validated independently by G3, G4,
and the DCV); `supervisor_command_doc_check.py` exit 0 (12 commands, 0 drift); ruff
clean on touched files; registry validator EXIT=0 at the accepted content (Amendment-28
rows verified: M0-T130 DCV 5/5 PASS at identity `fd4e61d6`/`517895c4`); doctor overall
PASS, config OS-ACL PROTECTED, journal integrity ok.

## 4. Journal / preservation state (journey-3 aftermath, untouched by this task)

`current_state = PAUSED_RECOVERY` (journey-3's counted stop, transition 26); audit
chain verified head 64; `rotation_pending` false; NO `task_advancement/*` keys (M0-T107
never advanced); the CAS-once queue snapshot `task_queue/queued_digest/M0-T109` equals
the live packet digest `371bed1a...` (consistent — a genuine restart reads coherently);
owner-touch ledger 3 of 2 (S16.7 at excess — an owner measurement, unaltered);
`wt-m0t107` clean `c5c6ff7`; `wt-m0t109` clean `1c06957`; PR #241 OPEN untouched.
**Because the journal rests at PAUSED_RECOVERY, the owner's next journey is again the
two-step section-4 sequence: Step 1 `clear-recovery`, then Step 2** (the Option-A
corrected shape, `--repo wt-m0t107`) — both re-validated against the live CLI contract
this session (parse OK; `dispatch_inputs_missing` EMPTY; `task_authority` PASS at
`repo=wt-m0t107`; queue entry ELIGIBLE).

## 5. Verdict

R247 recertification: **PASS at the one post-fix frozen identity** (material
`20bfa449`, supervisor tree `37020c37...`, manifest `26a05096...`). Any
supervisor/operator-channel change after this point re-invalidates certification and
re-triggers R247. Carried non-blocking follow-ups: module split of claude_runner.py on
next substantial growth (exception expires 2026-11-25); C4 flake-hardening of the
absorption test's result-count assertion; next_task.py decomposition; Option B
(task_authority probe-root from --checkout); runbook residuals.
