# M0-T129 - The owner-executed seven-fact commissioning protocol (D-024-R407/R408/R409)

**THE WIRING WINDOW STOPS HERE.** This protocol is PRESENTED ONLY: the orchestrator never
executes any command below (R409), and full autonomy is declarable ONLY after the owner-run
live journey proves all seven R393 facts (any live failure: R394 - stop without retry,
preserve byte-for-byte, one consolidated assessment). This SUPERSEDES the Amendment-24 staged
protocol's Stage-3 placeholder: with M0-T128 accepted, ONE owner-typed start can now prove
all seven facts. The Amendment-24 R397 hold and this window's R403 hold both remain until
the owner personally types the commands.

## 1. Seven-fact provability at the certified identity (all seven, one command)

| R393 fact | Mechanism now live | Proof surface |
|---|---|---|
| 1. Over-ceiling session never contacted | launch-seam pre-dispatch shed (unchanged, live-proven) | audit `over_ceiling_session_shed`; fresh session id |
| 2. Fresh Fable 5 worker in wt-m0t107 | certified launch seam + packet-worktree binding | worker transcript under the wt-m0t107 project slug |
| 3. Valid checkpoint reaches Codex | orientation packet + sized turns + reserved-turn injection (M0-T126) | checkpoint validated + forwarded; audit chain |
| 4. Codex completes an independent review | certified reviewer channel | codex verdict persisted |
| 5. M0-T107 advances exactly once (AUDITED) | `record_advancement` CAS - now LIVE-wired advance-before-select | durable `task_advancement/M0-T107` written exactly once |
| 6. Next bounded task is selected | `run_task_queue`'s ordered-queue iteration + `evaluate_eligibility` (eleven fail-closed categories) + the `is_advanced` already-done skip - LIVE since M0-T128 (`record_advancement` drives exactly-once; the standalone `select_next_packet` helper remains simulation-only with zero production callers, corrected here per the G3 review) | audit `cross_task_dispatch` (or visible skip rows + NO_ELIGIBLE_WORK) |
| 7. Multiple successive units AND tasks, no owner touch | in-task CONTINUE forwarding (--max-cycles) + cross-task driver (--max-tasks) behind the owner gate | >= 2 tasks dispatched in one journey, zero owner interventions between |

## 2. Complete preflight (every row must PASS before the owner types anything; the orchestrator re-runs and reports this at the then-current tip - presenting this package does not skip it)

1. `git -C C:/Users/MLFLL/Downloads/nyc-zoning/ctl24 status --porcelain` empty; HEAD == origin tip; CI green at that tip.
2. `git rev-parse HEAD:tools/agent_supervisor` == `b392100930bd4213cab90eb02aafa6d0d568f849`.
3. Supervisor-native CLI identity: `executable_identity` of `C:/Users/MLFLL/.local/bin/claude.exe` digest `d6f6c29a8ac6b3cf...` (2.1.251, 217,360,032 B); codex-cli 0.146.0.
4. `python -m tools.agent_supervisor verify-controller --manifest "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json" --config "C:\Program Files\SupervisorConfig\config.toml"` -> verified (manifest digest `841ed11c...`, 125 files, binds the post-wiring tree).
5. `python -m tools.agent_supervisor doctor --checkout C:\Users\MLFLL\Downloads\nyc-zoning\ctl24 --config "C:\Program Files\SupervisorConfig\config.toml" --model-selection C:\SupervisorController\model_selection.toml --manifest "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json"` -> overall PASS; journal readback `PAUSED_RECOVERY`, transitions 22, audit 53, 0 pending effects.
6. `python tools/supervisor_command_doc_check.py` -> exit 0.
7. `wt-m0t107` clean at `796e18f`, branch `task/M0-T107-plugin-portability`.
8. The commissioning queue file exists, parses, and every successor entry meets section 3.

## 3. The successor queue (owner-designated work; prepared BEFORE the journey)

The journey needs successors for facts 6-7. The controller NEVER invents work: the owner
designates it via a queue file, and the live eligibility engine (eleven fail-closed visible
categories) re-validates every entry at selection time - an unprepared entry is SKIPPED with
an audited reason, never silently run.

**Queue file format** (`load_task_queue`): a JSON object
`{"tasks": [{"task_id": "...", "packet_path": "...", "worktree": "...", "branch": "...", "repo": "..."}, ...]}`
in listed order. Suggested location: `C:/Users/MLFLL/Downloads/nyc-zoning/commissioning-queue.json`
(matches the presented command; any path works if the command is edited coherently).

**Per-successor prerequisites** (the eligibility engine enforces all of these fail-closed):
packet exists and parses; the queue entry's `task_id` equals the packet's own `task_id`;
`status` is `claimed`; every dependency's packet is `accepted`; no blockers and no owner-gate
field; the declared isolated worktree exists, is not the primary checkout, and binds via the
launch seam; packet content unchanged between queueing and selection. (Worktree
git-CLEANLINESS is a PREPARATION duty, not an eligibility category: leave each successor
worktree clean when preparing it - the orchestrator's preflight report covers this.)

**Preparation step (standard process, before the journey):** the owner names the successor
tasks; the orchestrator prepares them under the NORMAL control process (packet + claim +
isolated worktree per task, Tier A) and writes the queue file; the orchestrator then re-runs
this preflight and reports. Preparing successors changes NO supervisor code (no R247
re-trigger).

## 4. The two owner-typed commands (validated against the live CLI contract this session; OWNER-TYPED ONLY - R409)

Type with `!`-prefix in the orchestrator session (forward slashes), in order, after section 2
passes and section 3 is prepared:

**Step 1 - recovery exit (PAUSED_RECOVERY -> PREFLIGHT; ends the R374-era byte-for-byte
preservation of the live journal state by owner decision):**

`! python -m tools.agent_supervisor clear-recovery --checkout C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`

**Step 2 - the seven-fact limited-auto journey (single command; no repin flag - the CLI
identity is undrifted):**

`! python -m tools.agent_supervisor start --mode limited-auto --owner-enable-bounded-auto --checkout C:/Users/MLFLL/Downloads/nyc-zoning/ctl24 --repo C:/Users/MLFLL/Downloads/nyc-zoning/nyc-development-feasibility-claude-pack --branch task/M0-T107-plugin-portability --worktree C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t107 --max-cycles 3 --max-tasks 3 --packet-queue C:/Users/MLFLL/Downloads/nyc-zoning/commissioning-queue.json --claude-executable C:/Users/MLFLL/.local/bin/claude.exe --codex-executable C:/Users/MLFLL/AppData/Roaming/npm/codex.cmd --task-packet project-control/tasks/M0-T107.json --config "C:/Program Files/SupervisorConfig/config.toml" --model-selection C:/SupervisorController/model_selection.toml --manifest C:/Users/MLFLL/AppData/Local/NYCBuildabilitySupervisor/ctl24-activation/controller_manifest.json`

Semantics: first task = M0-T107 (up to 3 Codex-reviewed cycles); on a COMPLETE verdict the
audited exactly-once advancement records, the run closes, the next ELIGIBLE queue entry is
selected and launched in ITS isolated worktree; at most 3 tasks total; every between-task
seam re-checks stop/pause/emergency/graceful intents, the shared journey budget, and the
rotation ceiling. A conservative first journey MAY use `--max-tasks 2` with a one-entry
queue - facts 1-7 are still all exercised (one cross-task selection); `--max-tasks 3`
exercises two successive selections.

**What can stop the journey early (all fail-closed, all honest):** counted stop or invalid
checkpoint (PAUSED_RECOVERY, preserved); Codex HALT; NO_ELIGIBLE_WORK (visible skip audit
per candidate); budget/rotation/intent stops. **On ANY live failure (R394): stop without
retry, preserve all evidence byte-for-byte, one consolidated system-level assessment for a
new owner decision.** The owner-touch cap for M0-T107 is at excess: any counted stop is an
immediate owner matter.

**Standing gates untouched:** never merge PR #241; autostart, C1 canary, Telegram live send,
natural-event graduation, OS-ACL hardening, production, credentials, payments, legal - all
owner-only and closed. Success of this journey proves the seven facts; any WIDER autonomy
(different queues, larger bounds, unattended operation as a routine) remains a separate owner
decision each time.
