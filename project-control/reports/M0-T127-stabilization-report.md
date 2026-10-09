# M0-T127 - Amendment-22 consolidated stabilization report and commissioning package (D-024-R391/R392)

**THE WINDOW STOPS HERE.** This is the ONE consolidated report the owner ordered
(source-022-amendment.md p8). Nothing below activates, launches, or resumes anything.
The commissioning commands in section 7 are PRESENTED ONLY - the orchestrator never executes
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
   but automatic next-packet dispatch (`select_next_packet` / `record_advancement` /
   `advance_and_select`) has ZERO production call sites - deliberately withheld under
   the no-live-launch window and the R595 gate. CONSEQUENCE (Amendment 24): R393
   facts 6 and cross-task 7 are NOT provable by any currently-presented command;
   proving them requires the owner-authorized Stage-3 wiring described in section
   7.4, which re-triggers R247 recertification. Section 7.1 maps every fact honestly.
3. **Carried non-blocking observations:** one runbook digest is owner-machine-local
   (not sandbox-recomputable); runbook sections 2-10 still show `wt-m0t063` in
   EXAMPLES (outside the register's D15 scope - candidate follow-up task); the
   command-doc tooth scans the runbook only, so certification packages re-derive
   their presented commands mechanically (done for section 7 below).
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

## 7. The STAGED commissioning protocol (OWNER-TYPED ONLY - the orchestrator NEVER runs any of these, R392; execution HELD under R397 until the owner decides section 7.4)

REVISED under Amendment 24 (D-024-R397/R398/R399): the owner-relayed review found - and
the orchestrator verified in code - that the original single-command presentation could
not prove all seven R393 facts. The honest mechanics: `select_next_packet`,
`record_advancement`, and `advance_and_select` have ZERO production call sites (only
`plan_close_run` is live-wired, cli.py:2687). Live cross-TASK autonomy is therefore
deliberately unwired at this identity, and NO currently-presentable command can prove
R393 facts 6 and cross-task 7. This section maps every fact to the exact stage,
command, and wiring that proves it (R398).

### 7.1 Seven-fact provability map at the frozen identity

| R393 fact | Provable by | Stage |
|---|---|---|
| 1. Over-ceiling session never contacted | pre-dispatch shed at the launch seam | Stage 1 |
| 2. Fresh Fable 5 worker launches in wt-m0t107 | Stage-1 command | Stage 1 |
| 3. A valid checkpoint reaches Codex | Stage-1 command (the new orientation/cadence/reserved-turn machinery's first live test) | Stage 1 |
| 4. Codex completes an independent review | Stage-1 command | Stage 1 |
| 5. M0-T107 advances exactly once | PARTIAL at Stage 1: a COMPLETE verdict closes the unit and the run (close-to-IDLE on next start via the wired plan_close_run); the new AUDITED exactly-once advancement record (record_advancement) has no live caller yet - its live proof needs the Stage-3 wiring | Stage 1 (partial) / Stage 3 (full) |
| 6. The next bounded task is selected | NOT provable live today - select_next_packet has zero production call sites; requires the Stage-3 wiring | Stage 3 only |
| 7. Multiple successive units, no owner touch | WITHIN one task: Stage 2 (--max-cycles 3; Codex CONTINUE forwards drive successive units with zero owner touches between cycles - pre-existing in-process forwarding plus the new D10 cross-process persistence). ACROSS tasks: Stage 3 only | Stage 2 (in-task) / Stage 3 (cross-task) |

### 7.2 Stage 1 - single bounded cycle (proves facts 1-4 + the unit half of 5)

Both commands dry-run validated against the live `build_parser()` contract, the five
pinned load-bearing flags, and `dispatch_inputs_missing`. Type with `!`-prefix in the
orchestrator session (forward slashes - bash strips unquoted backslashes), in order,
after section 6 passes:

**Step 1 - recovery exit (PAUSED_RECOVERY -> PREFLIGHT; the documented recovery path
for the preserved S14 stop; an owner decision that ends the R374 byte-for-byte
preservation of the live journal state):**

`! python -m tools.agent_supervisor clear-recovery --checkout C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`

**Step 2 - the certified limited-auto start (fully pinned per the D1 tooth; no repin
flag - the CLI identity is undrifted):**

`! python -m tools.agent_supervisor start --mode limited-auto --owner-enable-bounded-auto --checkout C:/Users/MLFLL/Downloads/nyc-zoning/ctl24 --repo C:/Users/MLFLL/Downloads/nyc-zoning/nyc-development-feasibility-claude-pack --branch task/M0-T107-plugin-portability --worktree C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t107 --max-cycles 1 --claude-executable C:/Users/MLFLL/.local/bin/claude.exe --codex-executable C:/Users/MLFLL/AppData/Roaming/npm/codex.cmd --task-packet project-control/tasks/M0-T107.json --config "C:/Program Files/SupervisorConfig/config.toml" --model-selection C:/SupervisorController/model_selection.toml --manifest C:/Users/MLFLL/AppData/Local/NYCBuildabilitySupervisor/ctl24-activation/controller_manifest.json`

### 7.3 Stage 2 - bounded multi-unit on the SAME task (adds the in-task half of fact 7)

Identical to Stage-1 Step 2 with the single delta `--max-cycles 3` (dry-run validated
OK this session). On a Codex CONTINUE verdict the loop forwards the reviewed prompt and
runs the next unit with NO owner touch between cycles; on COMPLETE or any stop
condition it lands fail-closed as certified. Run Stage 2 only after Stage 1 succeeds
and its evidence is reviewed.

### 7.4 Stage 3 - cross-task autonomy (facts 5-full, 6, and cross-task 7) - REQUIRES A NEW OWNER DECISION FIRST (R399)

The orchestrator does not self-authorize either path. The options:

* **Option A - authorize the wiring window now:** one more bounded supervisor task to
  wire `advance_and_select` into the live post-COMPLETE path behind the EXISTING
  bounded-mode owner gate (the machinery, its exactly-once CAS semantics, and its crash
  matrix are already built and simulation-proven at this identity). It is a supervisor
  code change: R247 re-triggers and the recert re-runs (now measured at under a minute
  for golden; the full battery is sub-ten-minutes). Then ONE seven-fact live journey
  becomes presentable. Estimated bounded scope: wiring + dispatch-level tests + recert.
* **Option B (recommended) - de-risk live first:** run Stage 1, review its evidence,
  run Stage 2, review - THEN decide Option A with live behavioral data on the new
  checkpoint machinery. This is the incremental posture every prior live attempt has
  vindicated; nothing about Option B forecloses Option A.
* **Option C - hold everything** (the standing default; nothing runs until you type a
  command).

**What no option changes:** full autonomy is declarable ONLY after the complete
seven-fact live proof (R393); **on ANY live failure at any stage (R394):** stop without
retry, preserve all evidence byte-for-byte, one consolidated system-level assessment
for a new owner decision.

**Standing gates untouched by this package:** never merge PR #241; autostart, C1
canary, Telegram live send, natural-event graduation, OS-ACL hardening, production,
credentials, payments, legal - all owner-only and closed.
