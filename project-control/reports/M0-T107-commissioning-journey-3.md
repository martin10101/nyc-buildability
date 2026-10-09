# Commissioning journey 3 (corrected Step-2): DISPATCHED, valid checkpoint produced, then a counted stop from real-CLI queued-prompt absorption — one consolidated assessment (D-024-R394)

Recorded by the orchestrator 2026-08-31 (session `session_01SfXcRw7emzdojCDJmKxNTM`).
The owner personally typed the corrected Step-2 (R419 honored; orchestrator executed
nothing). Result: **DISPATCHED** (the Option-A correction is live-proven — the full
pre-dispatch gauntlet PASSED, including `task_authority`), cycle 1 ran, and the run
stopped **`no_valid_checkpoint`**, exit 11, journal `PAUSED_RECOVERY` (transitions 26).
Per R394: no retry, no restart, no clear-recovery, no journal edit; everything preserved;
this is the one consolidated assessment. **Owner touches now 3 of budget 2 — S16.7 is at
excess; disposition is an owner matter.**

## 1. What the journey PROVED (fresh live evidence, all primary)

| Fact | Evidence |
|---|---|
| Option-A `--repo` correction works | recovery classified `SAFE_CHECKPOINT`, re-preflighted, and dispatched — no `task_authority` failure at `--repo wt-m0t107` |
| Fresh Fable 5 worker in `wt-m0t107` (R393 facts 1-2 shape) | transition 25: `claude_process_started`, session `6786b4b0-506f-47bd-9c90-8eec53e0c9fa`, `job_object` containment; transcript under the wt-m0t107 slug |
| **Stage-3 cross-task driver ENGAGED live for the first time** | durable `task_queue/queued_digest/M0-T109` = `371bed1a...` (CAS-once snapshot, byte-equal to the live packet digest — consistent) |
| **The worker emitted a VALID structured checkpoint — the first ever in a live run** | S14 record: "the unit produced a valid checkpoint"; transcript event 30: an honest IN_PROGRESS checkpoint (`M0-T107-run_33dfa57d54db-cp1`) stating exactly what discovery it completed and that no file was changed |

`wt-m0t107` remains clean at `c5c6ff7` (zero worker writes); `wt-m0t109` clean at
`1c06957` (never dispatched); 0 surviving children; 0 pending effects.

## 2. Root cause of the stop (one cause, two symptoms; from the transcript + journal + runner source)

**The real CLI's queued-command semantics absorbed the reserved-final-turn prompt into
the worker's FIRST in-flight turn.** The T126 property-3 design enqueues the reserved
checkpoint prompt at launch, expecting delivery as its own turn when the working budget
is spent. Installed Claude Code 2.1.251 instead delivered it at the first tool-result
boundary: queue-operation `remove` with reason **`absorbed_mid_turn`** at 18:35:01 —
~31 seconds after launch, while the worker was in its first parallel-discovery turn.

- **Symptom A — premature truncation:** the worker (correctly obeying its contract)
  received "your 32 working turns are spent ... emit your mandatory checkpoint NOW"
  after ~4 real turns, stopped all tool use, and emitted the honest IN_PROGRESS
  checkpoint. The unit did discovery only; the packet was never even read.
- **Symptom B — the 900s wall-timeout ride:** the runner wrote TWO stdin prompts
  (orientation + reserved-turn contract) so `expected_results = 2`
  (claude_runner.py:1346/1349), but the CLI merged the absorbed prompt into ONE turn
  and emitted ONE terminal `result` event; `results_seen (1) < expected_results (2)`
  means `unit_complete` never latched (claude_runner.py:1382-1386), the runner waited
  for an EOF the CLI never sends, rode the full `timeout_seconds = 900` wall watchdog
  (18:34:28 -> 18:49:28), and tree-terminated. S14 then counted the stop: "the unit
  produced a valid checkpoint but hit the wall timeout and was tree-terminated; a
  timed-out unit is never success."

Consequently `consecutive_invalid_outputs` reached its hard limit (**3 >= 3**) across
the run lineage, and the touch ledger recorded the third counted stop (3 of 2).

**Why certification missed it:** the golden pack's fake CLI delivers a queued prompt as
its OWN turn with its own terminal result — a fixture-fidelity gap against installed
2.1.251 queue behavior. This is AD-093 qualifying evidence three ways: a reproduced
defect, provider-CLI behavioral drift, and a measured live problem. (The Amendment-8
R233 lesson — "ordinary commands queue until the turn ends" — described idle-time
delivery; `absorbed_mid_turn` during an active turn is the newly measured behavior.)

## 3. Not reached

Codex was never contacted (fact 3-4 not reached); no advancement recorded (fact 5);
M0-T109 never selected or dispatched (facts 6-7). The one-entry queue and its ELIGIBLE
verdict remain valid and unconsumed for a future journey (the CAS-once digest snapshot
equals the live packet digest, so a genuine restart reads consistently).

## 4. The new owner decision (nothing will be retried by the orchestrator)

1. **Bounded defect task (recommended):** an AD-093 defect-lane packet to fix the
   reserved-turn delivery against measured 2.1.251 queue semantics — deliver the
   reserved checkpoint prompt from the RUNNER at the right moment (when its own turn
   accounting reaches the working bound, or at worker-idle) instead of pre-queueing at
   launch, and make `expected_results`/`unit_complete` robust to prompt absorption
   (e.g., latch on the checkpoint event itself once every written prompt's turn has
   settled). Requires a measured installed-version fixture for the queue-absorption
   behavior (R233 discipline), then the sub-ten-minute R247 recert, then a fresh
   owner-typed journey.
2. **S16.7 excess disposition** (3 counted stops vs cap 2) — owner-only.
3. Standing follow-up candidates unchanged: Option B (task_authority probe-root:
   read the ledger from `--checkout` not `--repo`); next_task.py decomposition;
   runbook residuals.

Standing gates untouched: never merge PR #241; all owner-only gates closed; any
supervisor change re-triggers R247; R394 governs any future live failure.
