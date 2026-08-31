# M0-T127 - Amendment-22 consolidated stabilization report and commissioning package (D-024-R391/R392)

**THE WINDOW STOPS HERE.** This is the ONE consolidated report the owner ordered
(source-022-amendment.md p8). Nothing below activates, launches, or resumes anything.
The commissioning commands in §7 are PRESENTED ONLY - the orchestrator never executes
them (R392), and full autonomy is NOT declared from the tests and simulations herein
(R393): it requires the separate owner-authorized live commissioning journey proving
the seven facts, with the R394 failure protocol (stop without retry, preserve, one
consolidated assessment).

## 1. What was changed (plain language)

The live 12-turn failure - a fresh worker that spent every turn exploring and never
emitted its checkpoint - was the visible tip of seventeen defects across the complete
launch-to-next-task journey. This window surveyed the whole journey first (M0-T125:
17-defect register, complete 94-edge call-graph), then corrected everything at ONE
frozen identity (M0-T126), then recertified once (M0-T127):

* **Workers are now oriented, budgeted, and forced to checkpoint.** Every fresh OR
  rotated worker's first prompt front-loads its task, lineage, worktree, progress,
  relevant files, exact required output, and a sized checkpoint cadence
  (`orientation.py`). Working turns are sized from the workload class under a
  documented hard ceiling of 40 - never a raised constant (`turn_budget.py`); the
  final turn is reserved, and an "emit your mandatory checkpoint NOW" demand is
  genuinely injected as a real follow-up turn through the runner's stdin channel.
  An exhausted worker now yields an honest incomplete-but-resumable checkpoint,
  never a false completion and never silent loss.
* **The journey tail now exists.** A Codex COMPLETE verdict used to strand the
  journal (no close-run caller); ROTATE_SESSION stranded it in a dead state; the
  forwarded CONTINUE prompt was lost across process boundaries. Now: COMPLETE
  closes to IDLE on the next start; ROTATE_SESSION routes through the proven
  rotation seam; the reviewed next-unit prompt is durably persisted and consumed
  exactly once; and `next_task.py` provides audited exactly-once task advancement
  + next-packet selection over a single-winner compare-and-swap.
* **Wrong-tree and wrong-command hazards are fail-closed.** Evidence collection and
  Codex review can no longer silently bind to the orchestrator's primary checkout
  (D2 refusal); every owner-presented command is machine-validated against the live
  CLI contract in CI (the D1 command-document tooth - the class of failure that
  caused the live exit-11 refusal can no longer reach a presented document);
  dispatch-intent journaling closes the crash re-dispatch window; stop/pause/
  graceful/emergency intents are honored between cycles; refused starts no longer
  consume the owner's budget clock; the runbook is regenerated from live sources.

## 2. The full end-to-end proof

* **Sixteen-scenario removal-sensitive matrix** (R386/R387) over the preserved real
  artifacts as read-only replay fixtures - including the preserved 12/12 transcript
  replay that fails the old design and passes the new, live-vs-cumulative token
  fixtures (72,546 real vs 694,251 cumulative), synthesized Codex CONTINUE,
  duplicate AND stale verdicts, and the full interruption sub-matrix (crash after
  Popen / mid-stream / pre-extract; before+after forwarding, verdict persistence,
  and campaign advancement). Full map: `M0-T126-design-record.md`.
* **R388 consecutive simulated advancements:** three tasks advanced in sequence with
  no human intervention, exactly-once each, surviving a genuine process-death
  simulation at the advancement boundary (journal close + reopen), with no
  duplicate, lost, or false advancement.
* **Verification chain:** producer self-checks -> G3 code review (an honest FAIL at
  the first identity, remediated by a FRESH producer, delta PASS) -> G4 QA
  (independent reproduction of every count and fixture figure) -> 18-row DCV, all
  SATISFIED -> acceptance -> this R247 recertification: golden 42/42 (52.2s),
  whole suite 2,990 passed / 2 pre-existing skips / 0 failed, manifest bound
  (125 files `a43f133b...`), verify-controller PASS, doctor PASS, CLI identity
  undrifted, CI 20/20. Details: `M0-T127-recertification.md`.

## 3. Every defect found proactively (beyond the 17-defect register)

1. G3-1 rotated-orientation gap; G3-2 reserved-turn enforcement gap + an
   evidence-map overclaim by the orchestrator (corrected; evidence maps are now
   rebuilt from gate-verified code only); G3-3 incomplete runbook regeneration.
2. G4: producer test-count drift (395 vs the real 391 at that identity), a phantom
   test citation, a scenario mis-attribution - all corrected and re-verified.
3. A golden restart test that passed ONLY because of the D10 bug (rewritten to the
   certified single-cycle shape - the suite got stronger, not weaker).
4. Static-analysis sweep findings triaged: three alleged undefined names proved
   false positives by execution; dead assignments and unused imports cleaned.
5. The "3h13m golden pack" belief: an environmental artifact of one reviewer
   session (the same pack certified at 15.00s in M0-T119 and 52.20s now).
6. A registry-digest CRLF hazard in the orchestrator's own Amendment-23 capture
   (fixed before CI could fail; LF discipline recorded).

## 4. All remaining limitations (honest list)

1. **Property-3 softness:** the reserved-turn demand is a real injected turn, but
   the `--max-turns` streaming model cannot hard-block a worker from spending that
   turn on a tool call; the fail-closed exhaustion net is the backstop
   ("wherever technically enforceable" - the amendment's own hedge).
2. **D9 autonomous tail is simulation-proven only:** `plan_close_run` is live-wired,
   but automatic next-packet dispatch is deliberately NOT wired to a live start -
   that is exactly what the R393 live commissioning journey must prove.
3. **Carried non-blocking observations:** one runbook digest is owner-machine-local
   (not sandbox-recomputable); runbook sections 2-10 still show `wt-m0t063` in
   EXAMPLES (outside the register's D15 scope - candidate follow-up task); the
   command-doc tooth scans the runbook only, so certification packages re-derive
   their presented commands mechanically (done for §7 below).
4. **Live-behavior unknowns:** worker-side quota exhaustion and natural provider
   events remain pending_live_observation under the passive watcher (R224-R228);
   the owner-touch cap for M0-T107 is at excess - any further counted stop is an
   immediate owner matter.

## 5. The exact frozen identity

Material commit `2d46fb0` on `control/D-024-fable-codex-loop`; `tools/agent_supervisor`
tree `46722aa1af8f92f063d74b638a5a04e996a1f52d`; golden pack blob `deeca07b`; launch-seam
blob `0aed4902`; controller manifest 125 files `a43f133b2bf49c0e...` (stored at
`%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json`);
Claude Code 2.1.251, supervisor-native digest `d6f6c29a8ac6b3cf...` (sha256_head+size,
217,360,032 B); codex-cli 0.146.0. Any supervisor/operator-channel change after this
point re-invalidates certification and re-triggers R247.

## 6. The complete preflight (run before any owner-typed attempt; every row must PASS)

1. `git -C C:/Users/MLFLL/Downloads/nyc-zoning/ctl24 status --porcelain` empty; HEAD ==
   origin tip; CI 20/20 at that tip.
2. `git rev-parse HEAD:tools/agent_supervisor` == `46722aa1af8f92f063d74b638a5a04e996a1f52d`.
3. Supervisor-native CLI identity: `executable_identity` of
   `C:/Users/MLFLL/.local/bin/claude.exe` == `d6f6c29a8ac6b3cf...` (2.1.251); codex 0.146.0.
4. `python -m tools.agent_supervisor verify-controller --manifest "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json" --config "C:\Program Files\SupervisorConfig\config.toml"` -> verified.
5. `python -m tools.agent_supervisor doctor --checkout C:\Users\MLFLL\Downloads\nyc-zoning\ctl24 --config "C:\Program Files\SupervisorConfig\config.toml" --model-selection C:\SupervisorController\model_selection.toml --manifest "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json"` -> overall PASS; journal readback `PAUSED_RECOVERY`, transitions 22, audit 53, 0 pending effects.
6. `python tools/supervisor_command_doc_check.py` -> exit 0.
7. `wt-m0t107` clean at `796e18f`; branch `task/M0-T107-plugin-portability`.
8. The orchestrator re-runs and reports this preflight at the then-current tip before
   any owner-typed attempt - presenting this package does not skip that step.

## 7. The exact commands for ONE controlled live commissioning attempt (OWNER-TYPED ONLY - the orchestrator NEVER runs these, R392)

Both commands were dry-run validated this session against the live `build_parser()`
contract, the five pinned load-bearing flags, and `dispatch_inputs_missing` (both OK).
Type them with `!`-prefix in the orchestrator session (forward slashes - bash strips
unquoted backslashes), in order, after §6 passes:

**Step 1 - recovery exit (PAUSED_RECOVERY -> PREFLIGHT; this is the documented
recovery path for the preserved S14 stop, an owner decision that ends the R374
byte-for-byte preservation of the live journal state):**

`! python -m tools.agent_supervisor clear-recovery --checkout C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`

**Step 2 - the certified limited-auto start (fully pinned per the D1 tooth; no repin
flag - the CLI identity is undrifted):**

`! python -m tools.agent_supervisor start --mode limited-auto --owner-enable-bounded-auto --checkout C:/Users/MLFLL/Downloads/nyc-zoning/ctl24 --repo C:/Users/MLFLL/Downloads/nyc-zoning/nyc-development-feasibility-claude-pack --branch task/M0-T107-plugin-portability --worktree C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t107 --max-cycles 1 --claude-executable C:/Users/MLFLL/.local/bin/claude.exe --codex-executable C:/Users/MLFLL/AppData/Roaming/npm/codex.cmd --task-packet project-control/tasks/M0-T107.json --config "C:/Program Files/SupervisorConfig/config.toml" --model-selection C:/SupervisorController/model_selection.toml --manifest C:/Users/MLFLL/AppData/Local/NYCBuildabilitySupervisor/ctl24-activation/controller_manifest.json`

**What the live journey must prove (R393, the seven facts):** the over-ceiling session
is never contacted; a fresh Fable 5 worker launches in `wt-m0t107`; a valid checkpoint
reaches Codex; Codex completes an independent review; M0-T107 advances exactly once;
the next bounded task is selected; multiple successive units operate without an owner
touch. **On ANY live failure (R394):** stop without retry, preserve all evidence
byte-for-byte, one consolidated system-level assessment for a new owner decision.

**Standing gates untouched by this package:** never merge PR #241; autostart, C1
canary, Telegram live send, natural-event graduation, OS-ACL hardening, production,
credentials, payments, legal - all owner-only and closed.
