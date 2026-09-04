# D-024 persistent-local-activation — terminal report (Amendment 51, R759/R760)

Recorded 2026-09-04 (UTC) by the orchestrator at the end of the Amendment-51 campaign-continuation
session. Terminal token: **BLOCKED_FOR_PERSISTENT_ACTIVATION** — the single blocker is a genuine
owner-only gate, and the architecture-viability decision is POSITIVE. All safe local work is done.

## 1. What was completed this session (durable, accepted/gated)

| Item | State |
|---|---|
| Reconciliation (R750) of the expected anchor vs live git/ledger/continuity/worktrees | Zero discrepancies (proof plan §1) |
| M0-T144 deficit-convergence policy (Part B) | **ACCEPTED** (6/6 DCV PASS; CLAUDE.md principle 18 + `/deficit-convergence` skill; content commit 6aafd5e4) |
| M0-T109 guard-hardening code (Part A, item 2) | Code complete; **gates G0/G2/G3/G4/G5 all PASS**; adopted 7f075e37; acceptance coupled to R754 (below) |
| Controller capability map + R753 seven-fact proof plan | Committed (D-024-persistent-loop-proof-plan.md) |
| M0-T145 backlog follow-up (braced-variable guard residual from G5) | Created (tracked, not worked) |

## 2. Why the terminal is BLOCKED, not READY

The seven local-autonomy facts (auto-REVISE loop-back, auto-correct-and-re-review without an owner
"continue", auto-advance to the next ready task, controller task selection, controlled
interruption, checkpoint resume, accurate foreground view) can be proven LIVE only by launching the
**limited-auto autonomous loop** for the first time. That run:

- **Spends the owner's real Fable + Codex allowance** (item-8 owner-only "payment"-class gate).
- Is the **first-ever live exercise** of the `--mode limited-auto --owner-enable-bounded-auto`
  legacy `ClaudeRunner`/`CodexReviewer` path — a different, less-recently-exercised dispatch path
  than the MRL one-shot the journey proved (`mrl_launch_path.py:91-97` forbids the one-shot path
  from looping, so the persistent loop MUST use the legacy path).
- Is the direct precursor to the persistent loop the owner **explicitly reserved** ("do not start
  the persistent loop on my behalf").

Every prior live run in this campaign was owner-typed. The orchestrator does not self-authorize the
first live autonomous provider-spending commissioning run. Therefore the proofs do not converge
autonomously; they converge on this one owner-only gate. `READY` cannot be emitted honestly because
no fact is yet LIVE-proven for the autonomous shape (they are mechanism-verified + unit-tested, and
one live REVISE was observed on journey-m0t107-01).

## 3. Architecture-viability decision: VIABLE

The persistent local Codex-managed loop is architecturally sound and the installed controller
already carries every mechanism needed:

- **Auto-REVISE loop-back (facts 1–2):** `loop.py:2289-2301` (`tier_auto` → `FORWARD_PROMPT`) under
  `--mode limited-auto --owner-enable-bounded-auto`; `forward_exactly_once` delivers Codex's
  `next_claude_prompt` to a fresh Fable unit. In supervised mode this is an owner-held exit instead
  — so limited-auto is required for hands-off REVISE.
- **Auto-advance + task selection (facts 3–4):** `run_task_queue` (`next_task.py:763-900`) with
  `--packet-queue` + `--max-tasks ≥ 2`; exactly-once advancement records in the durable journal;
  crash-safe (already-advanced tasks skipped). The controller **selects** from the owner-supplied
  ordered queue file bound to committed task packets; it never accepts ledger tasks itself
  (`loop.py:2174-2179`) — acceptance stays with the orchestrator's gates.
- **Interruption + resume (facts 5–6):** durable manual-pause flag honored at the between-cycle
  seam (`loop.py:2874-2877`); graceful-stop lands the in-flight unit and survives restart
  (`state_machine.py:290-306`); a stable `--run-id` resumes budgets and skips completed tasks.
- **Checkpoint validity:** M0-T133's controller-authoritative checkpoint envelope is **already
  installed** (present + wired in `C:\SupervisorController`, ancestor of the frozen `3f4cee86`) and
  was live-proven on journey-m0t107-01. (M0-T133's ledger status is `rework` — a hygiene item, its
  code is shipped and working; re-gateable now that M0-T136 resolved the modularity ceiling.)
- **No fixed overall wall-clock:** `--run-wall-clock-seconds` defaults to None = UNLIMITED
  (`run_budget.py:7-13`, `cli.py:3357-3366`); per-turn (`--max-turns`), per-unit
  (`--unit-timeout`), per-cycle (`--max-cycles`), per-task (`--max-tasks`), circuit breakers, and
  owner-touch budget all remain.

**Two design caveats the owner must decide (neither blocks viability):**
1. **Foreground view (fact 7) is wrapper-assembled, not controller-streamed.** The controller prints
   ONE exit report (`start_gate.py:466-511`) with mode/classification/next-state/final `stopped=`
   + `cycles`/`final_state` + budget line — it does NOT print task id, stage, worker model, Codex
   verdict text, or the pending-approval digest. The accurate live view is assembled by the launcher
   wrapper from `--json` output + the durable run artifacts + a real-time `audit.jsonl` tail (the
   honest surface R730 recorded). Meeting fact-7 fully as stated needs either accepting the
   wrapper+audit-tail view, or a small controller enhancement (a separate authorized task) to print
   task/stage/model/verdict/pending-digest per cycle.
2. **Mid-run owner guidance to Codex is NOT implemented.** `/loop-ask` and `/loop-codex` run bounded
   read-only Codex calls in SEPARATE processes whose dispositions land as durable rows consumed
   BETWEEN cycles (`codex_channel.py` writes `"actuated": False` rows with no in-loop consumer);
   nothing injects guidance into an in-progress review. The supported influence points are
   between-cycle only.

## 4. Consolidated blocker (single, owner-only)

**BLOCKER-1 (owner-only gate):** Authorize and personally run the first live limited-auto autonomous
commissioning run over a ≥2-task queue (e.g. `[M0-T109, M0-T025]`) to produce durable live evidence
for facts 1–7. It spends real Fable + Codex allowance and is the first live exercise of the
autonomous path; the orchestrator cannot self-authorize it. Everything else is ready: the installed
controller has the mechanisms; the guard-hardening and policy work are done; the exact command is in
§5.

No other blocker. (M0-T133 ledger re-gate and the fact-7 view decision are non-blocking follow-ups,
not gates on the live run itself.)

## 5. Owner activation handover

Paths below are the live installed identities (from the deployed launcher + controller install).
Run all commands from the controller root.

**Prep once per shell:**
```powershell
Set-Location C:\SupervisorController
```

**(1) Start the durable local Codex-managed loop — NO fixed overall wall-clock (omit
`--run-wall-clock-seconds`); per-turn/per-unit/per-cycle/per-task limits and breakers remain.**
The owner supplies an ordered packet-queue JSON (`$queue`) whose entries bind the committed task
packets in run order, and a stable `$runId`:
```powershell
python -m tools.agent_supervisor start `
  --mode limited-auto --owner-enable-bounded-auto `
  --checkout C:\SupervisorController `
  --claude-executable C:\Users\MLFLL\.local\bin\claude.exe `
  --codex-executable C:\Users\MLFLL\AppData\Roaming\npm\codex.cmd `
  --config "C:\Program Files\SupervisorConfig\config.toml" `
  --model-selection C:\SupervisorController\model_selection.toml `
  --manifest "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json" `
  --packet-queue $queue `
  --max-tasks 2 --max-cycles 3 `
  --run-id persistent-local-01
```
(Worker stays exactly `claude-fable-5` and reviewer `gpt-5.6-sol` per `model_selection.toml`; do
NOT pass `--run-wall-clock-seconds`. A live second window running
`Get-Content -Wait <runtime>\audit.jsonl` gives the real-time event view.)

**(2) Status / pause / resume / stop (single commands):**
```powershell
python -m tools.agent_supervisor status         --checkout C:\SupervisorController
python -m tools.agent_supervisor pause          --checkout C:\SupervisorController
python -m tools.agent_supervisor resume         --checkout C:\SupervisorController
python -m tools.agent_supervisor graceful-stop  --checkout C:\SupervisorController
```
(`emergency-stop` for an immediate durable halt, cleared only by `stop --clear`.)

**(3) Sending Codex new owner guidance while the loop runs — HONEST LIMITATION:** there is NO
supported way to inject guidance into an IN-PROGRESS Codex review. The supported, between-cycle
mechanisms are `python -m tools.agent_supervisor ask "<question>" …` (one bounded read-only Codex
call in a separate process) and `python -m tools.agent_supervisor codex new|continue|show|promote|close`
(durable advisory threads whose dispositions are read at cycle boundaries). Mid-run steering of the
running reviewer is not implemented.

**(4) What happens after you run (1):** the controller runs its pre-dispatch gauntlet (identity/cwd/
manifest/mode gate), then for each queued task launches a fresh `claude-fable-5` worker in that
task's worktree, collects its checkpoint, runs a fresh `gpt-5.6-sol` review; on REVISE it
auto-forwards the reviewer's feedback to a new Fable unit and re-reviews (no "continue" needed);
on an APPROVE that satisfies invariants+gates it records exactly-once advancement and selects the
next queued task from durable state; it never accepts a ledger task or touches GitHub. It stops at
`--max-cycles`/`--max-tasks`, a circuit breaker, a graceful/emergency stop, or an owner-only
`STOP_FOR_OWNER`/`WAIT_FOR_OWNER` decision — and prints the exit report. Acceptance of any advanced
task remains an orchestrator gate action afterward.

**(5) The exact owner-authorization statement required LATER for the GitHub lifecycle** (only if you
choose to enable the separately-proven push→PR→CI→merge path; do NOT run this now):
> "I, the repository owner, authorize D-024 R595/Option-A activation and the R603–R605 GitHub
> lifecycle: the supervised loop may perform task-branch push, PR creation, CI trigger, and merge
> under the Option-A anchor, on the candidate branch only, with PR #241 excluded, effective from
> this message."

## 6. Standing boundaries honored this session

Worker pin `claude-fable-5` unchanged; reviewer `gpt-5.6-sol` unchanged; no controller/model-
selection/cwd-guard/external-config edit; the guard was HARDENED (all M0-T108 denials preserved,
no weakening); one writer per worktree; no push/PR/merge/deploy; PR #241 untouched; no live
provider run launched; R595/Option-A not activated; R603–R605 not decided.
