# M0-T052 — G3 code review (verbatim reviewer return)

Saved verbatim by the orchestrator from the independent code-reviewer agent's return channel
(2026-08-08; reviewer model claude-opus-4-8 effort xhigh; transport entity-decoding only:
`-&gt;` sequences in the transport render as `->`).
Reviewer preamble: "I have completed my independent verification. All claims verified from
source, all tests reproduced. Here is my complete G3 gate report."

---

# Gate Report

- Gate ID: G3
- Task ID: M0-T052
- Reviewer: code-reviewer (independent; not the producer)
- Producer: backend-engineer
- Result: PASS
- Clean environment/worktree used: Yes — frozen review at HEAD `867b1bfbfaeefeabe8be64ebf2f4b808acc56a7d`, branch `task/M0-T052-start-reentry`, worktree `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t052`; Python 3.11.9

## Acceptance criteria reviewed

The task packet (`project-control/tasks/M0-T052.json`, held in the main checkout; not committed to the task branch) carries `acceptance_scenarios: []` and instead names three REQUIRED TESTS in its objective plus the freeze-baseline. All three are satisfied and independently reproduced:

1. Crash-window regression (journal at START_CLAUDE, no recorded/surviving child → restart dispatches exactly-once and reaches CLAUDE_RUNNING with a fake executable) — `CrashWindowResumeTests` PASS.
2. Fail-closed negative (recover_boot classification not SAFE_CHECKPOINT still refuses dispatch from START_CLAUDE) — `FailClosedResumeTests` PASS.
3. Full supervisor suite re-establishes the M0-T039 freeze baseline (0 failures) — 1402 passed / 2 skipped / 0 failed.

## Directive/requirement verification

This task is in-regime (`directive_refs: [{D-010, ALL}]`); the exhaustive per-requirement D-010 pass belongs to the `directive-compliance-verifier` and its `verification.json` (producer ≠ verifier). Within the G3 code-review remit I re-derived the specific owner order governing this packet, D-010 source-024 R237–R241, from the blocker and packet, and verified the code-level constraints it imposes:

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-010 source-024 R237–R241 — smallest durable fix, authorized deterministic recovery path | 867b1bf | PASS | Fix is a one-constant change: `CYCLE_ENTRY_STATES` gains `START_CLAUDE` (loop.py:137) + doc-comment (114–136); recovery is deterministic through the existing operator-`start`→`recover_boot(SAFE_CHECKPOINT)` gate (cli.py:2374) → `_run_loop` (2396) → `loop.run()` (2304) → `run_cycle` from START_CLAUDE. |
| R237–R241 — NO supervisor redesign | 867b1bf | PASS | `git show 867b1bf --stat`: only `tools/agent_supervisor/loop.py` among supervisor modules changed; state machine, recovery, cli, locking untouched. |
| R241 — do not interrupt M2-T015 (disjoint file scope) | 867b1bf | PASS | Diff touches only `tools/agent_supervisor/loop.py` + two test files + own report; `services/**`, `apps/**`, `packages/**` (M2-T015 scope) untouched, and are explicitly listed as forbidden_paths. |

## Steps independently executed

- `git show 867b1bf --stat` — exactly 4 files changed (479 insertions, 3 deletions); no file outside `allowed_paths`.
- Read the production code (not the report) for the crash window: loop.py:1604–1661, state_machine.py:103–137/284–412, recovery.py:155–330/443–504, cli.py:2188–2304 and 2330–2414.
- `python -m pytest tools/test_agent_supervisor_start_reentry.py -q` → `10 passed in 0.72s`.
- `python -m pytest tools/test_agent_supervisor_loop.py -q -k CycleEntryState` → `3 passed, 100 deselected`.
- `python -m pytest tools/test_agent_supervisor_*.py -q` → `1402 passed, 2 skipped in 102.04s`.

## Expected versus actual

1. Crash-window analysis (verified from code, not the report):
   - `preflight_pass → START_CLAUDE` commits durably at loop.py:1626, and the worker launch (`runner.run_unit`) is at loop.py:1651 — i.e. the durable START_CLAUDE commit precedes the launch. Confirmed.
   - `START_CLAUDE → CLAUDE_RUNNING` commits at loop.py:1656–1661, guarded by `if self.machine.current_state == START_CLAUDE`, only after `run_unit` returns a real process/session. Confirmed.
   - The entry guard at loop.py:1605 (`if entry not in CYCLE_ENTRY_STATES: raise LoopError("bad_cycle_entry_state")`) previously made a stranded START_CLAUDE unrecoverable, because state_machine.py:133–136 gives START_CLAUDE only `→CLAUDE_RUNNING`/`→HALTED` and no production path drove those from a stranded journal; `recover_boot` records but never transitions (recovery.py:496, no `machine.transition`). Confirmed the root cause exactly as claimed.

2. Safety of the one-constant fix — every consumer and reachable path walked:
   - Sole production consumer of `CYCLE_ENTRY_STATES` is the run_cycle entry guard (loop.py:1605); grep confirms no other non-test consumer.
   - Resource-trip path (loop.py:1617–1623): from START_CLAUDE returns `stop(..., entry)` with NO state transition (re-strands at a now-recoverable state). Safe.
   - Circuit-breaker path (loop.py:1630–1640): its only transition is gated `if current_state == CLAUDE_RUNNING`; from START_CLAUDE it does not fire, returns stop with no transition. Safe.
   - `if entry == PREFLIGHT` guard (loop.py:1625): skipped on a START_CLAUDE resume, so no duplicate `preflight_pass` is recorded. Confirmed.
   - The only transition driven from START_CLAUDE in run_cycle is the legal `claude_process_started` (loop.py:1656), and independently `StateMachine.transition` refuses any non-table edge via `IllegalTransitionError` (state_machine.py:373–378) — so no transition outside the S7 table can occur regardless of the entry set.
   - FORWARD_PROMPT resume path (loop.py:2346): handled before the cycle loop and leaves the machine at CLAUDE_RUNNING; run_cycle is never entered at START_CLAUDE through it. A stranded START_CLAUDE (≠ FORWARD_PROMPT) correctly skips this branch and enters run_cycle at START_CLAUDE.
   - Rotation seam / shadow mode: unchanged; `_guard`→`assert_can_act` (state_machine.py:405–411) does not block START_CLAUDE (not in BLOCKING_STATES, state_machine.py:75–77).
   - Dispatch authority UNCHANGED: `_run_loop` fires `IDLE→PREFLIGHT` only when `current_state == INITIAL_STATE` (cli.py:2207); a stranded START_CLAUDE skips it and enters `loop.run()` directly, so recover_boot's advisory `next_state=PREFLIGHT` is never illegally applied as a START_CLAUDE→PREFLIGHT transition. Launch remains gated on operator `start` + `recover_boot(...).classification == SAFE_CHECKPOINT` (cli.py:2374) + single-instance lock (cli.py:2351/2414) + child accounting (recovery.py:155–178, 267–295). recover_boot fails closed on a surviving/undetermined child, competing writer, missing/failed revalidation step, or pending external effect (recovery.py:270–306). Confirmed no new dispatch path is opened.

3. Test adequacy — the crash window is genuinely pinned:
   - `strand_at_start_claude` commits the exact real transitions (`start_command` then `preflight_pass`) via a real `DurableJournal`/`StateMachine`; `test_the_strand_is_durable_and_read_from_the_journal` proves a fresh StateMachine reads START_CLAUDE from the journal (real crash condition, not in-memory).
   - `test_run_cycle_from_start_claude_dispatches_exactly_once` and `test_production_run_entry_from_start_claude_completes_legally` assert `len(runner.prompts) == 1` (exactly-once) through both `run_cycle` and the production `loop.run()` entry; `test_resume_does_not_re_record_the_preflight_transition` proves no duplicate `preflight_pass`; `test_supervised_resume_walks_the_rest_of_the_s7_path_once` pins the full supervised tail. These would raise `bad_cycle_entry_state` on the pre-fix constant, so they are non-vacuous regressions.
   - Fail-closed negatives use the REAL `recover_boot`: surviving child via `os.getpid()` → `UNSAFE_OR_DRIFTED` with the pid in `unaccounted_children`; competing writer → `UNSAFE_OR_DRIFTED`; pending external effect → `AMBIGUOUS_EFFECT`. The positive control (`test_a_clean_strand_classifies_safe_checkpoint`) proves the same stranded journal WITHOUT those conditions classifies `SAFE_CHECKPOINT` — establishing the negatives are non-vacuous (they assert `!= SAFE_CHECKPOINT` against a case that otherwise IS SAFE_CHECKPOINT).
   - Modified invariant test (`test_the_only_entry_states_are_preflight_start_claude_and_claude_running`, test_agent_supervisor_loop.py:561) is NOT weakened: it remains an exact-set equality assertion (would fail on any further widening), and the two guarding negatives in the class — IDLE refused by name (554) and no-transition-on-refusal (570) — are unchanged and still pass. The change is the minimal contract update the fix requires.

## Evidence paths

- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t052/tools/agent_supervisor/loop.py` (114–137 constant/doc; 1604–1661 run_cycle; 2334–2421 run)
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t052/tools/agent_supervisor/state_machine.py` (75–77 BLOCKING_STATES; 103–137 table; 373–411 transition/assert)
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t052/tools/agent_supervisor/recovery.py` (155–330, 443–504)
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t052/tools/agent_supervisor/cli.py` (2188–2304, 2330–2414)
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t052/tools/test_agent_supervisor_start_reentry.py`, `.../tools/test_agent_supervisor_loop.py` (551–575)
- `C:/Users/MLFLL/Downloads/nyc-zoning/nyc-development-feasibility-claude-pack/project-control/tasks/M0-T052.json`, `.../project-control/blockers/B-018-supervised-run-stranded-start-claude.json`

## Human-style walkthrough findings

Not a UI task; no walkthrough applicable. The CLI dispatch gate (cli.py:2374) was read and confirmed unchanged.

## Regression/security/provenance findings

- No regressions: full supervisor suite 1402 passed / 2 skipped / 0 failed, exactly baseline 1392/2 + the 10 new tests; the 2 skips are pre-existing and unchanged.
- Security/authority: no widening of who may dispatch; all fail-closed gates intact and independently reproduced.
- Provenance: commit message cites the qualifying evidence (B-018, an unresolved crash/recovery problem — supervisor-freeze §2/§3) and the owner order (D-010 source-024 R237–R241); the packet objective cites the same. Freeze rules 1 (no speculative features), 3 (evidence citation), and 4 (baseline re-established, ≥1165, 0 failures) all satisfied.

## Defects

None (BLOCKING/MAJOR): none found.

INFO only (non-blocking, no rework required):
- INFO — loop.py:121–124 doc-comment and `project-control/reports/M0-T052-producer-report.md` cite approximate line numbers (`~1607`/`~1632`/`~1637`; report also `1586`/`1606`) that are slightly off the actual anchors (entry guard 1605, `preflight_pass` transition 1626, `run_unit` 1651, `CLAUDE_RUNNING` transition 1656). They are marked with `~` as approximate and the behavior is verified from code; no correctness impact.
- INFO — the new fail-closed tests call `recover_boot(lock=None)`, so the single-instance-lock fail-closed branch (recovery.py:461–468, 272–274) is not exercised by these tests; it is unchanged code, covered elsewhere in the recovery suite, and a real lock is passed by `cmd_start` (cli.py:2351). Disclosed by the producer.
- INFO — no live end-to-end `cmd_start` CLI invocation was added; the gate is proven at the `recover_boot` classification boundary (the exact boolean cli.py:2374 branches on) and that CLI branch was read and confirmed unchanged. Disclosed by the producer.

## Required rework

None.

## Reviewer conclusion

The crash-window analysis is correct as verified from source: the durable `START_CLAUDE` commit precedes the launch, `CLAUDE_RUNNING` commits only after a real process, and the omission of START_CLAUDE from `CYCLE_ENTRY_STATES` made a stranded launch unrecoverable. The one-constant fix is the smallest durable change and is safe: no deliberately-unreachable path becomes reachable, no transition outside the S7 table can occur (both the entry guard and the independent table check enforce this), and dispatch authority (operator start + recover_boot SAFE_CHECKPOINT + single-instance lock + child accounting) is unchanged. The 10 new tests genuinely pin the crash window on real journal/state-machine objects with exactly-once dispatch and non-vacuous fail-closed negatives; the single modified invariant test reflects only the intended contract change and is not otherwise weakened. Scope, freeze rules, and evidence citations are all satisfied. All test counts reproduced (10/10 focused; 1402 passed / 2 skipped / 0 failed full suite, matching the claimed baseline+10).

Verdict: PASS

---

# Delta attestation (verbatim reviewer return, 2026-08-08; same G3 reviewer agent)

I have reviewed `git diff 867b1bf..6a61c6b`. The delta is exactly two files with zero behavioral change:

- `tools/agent_supervisor/loop.py`: the changed lines are entirely within the `#:` doc-comment block for `CYCLE_ENTRY_STATES` (the double-launch rationale). The executable constant line `CYCLE_ENTRY_STATES = frozenset({PREFLIGHT, START_CLAUDE, CLAUDE_RUNNING})` is not in the diff — unchanged. Every added/removed line is a comment (`#:` prefix). No code, no test.
- `project-control/reports/M0-T052-producer-report.md`: a single appended "G5 C3 correction" note; the original body above it is preserved unchanged.

# Delta Attestation — M0-T052 G3, 867b1bf → 6a61c6b

- Reviewed base: 867b1bf (my G3 PASS)
- Delta commit: 6a61c6b (G5 C3 correction) on `task/M0-T052-start-reentry`, worktree `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t052`
- Diff scope confirmed: `--stat` = 2 files, 25 insertions / 3 deletions; loop.py change confined to the `#:` comment block (lines ~127–135); report change is an appended note. Zero executable code changed; zero test code changed.

Assessment: The correction improves the honesty of the safety rationale — it withdraws the overstated claim that `recover_boot`'s surviving-child check alone prevents double-launch (correct: `record_launched_child` has no production caller, so that check only covers RECORDED children), and correctly restates the operative guarantee as platform kill-on-close containment (Job Object), with non-Job-Object hosts barred by the C1 activation pin and production child-accounting deferred to the M0-T053 follow-up (C2). This aligns with and tightens my own INFO observation. None of my four G3 code-level conclusions depend on the corrected narrative:

1. Crash-window correctness — verified from unchanged executable code (loop.py:1604–1661, state_machine.py:133–136, recovery.py:496).
2. Safety of the one-constant fix (no illegal transition possible; `transition()` refuses non-table edges; dispatch authority unchanged at cli.py:2207/2374) — unchanged code.
3. Test adequacy — the 10 new tests and the modified invariant test are byte-identical at 6a61c6b; suite result 1402/2/0 remains valid (no executable/test change to invalidate it).
4. Scope discipline — the delta stays within `allowed_paths` (loop.py + own producer report), doc-only.

Because only a comment and a markdown note changed, no re-run is required; the frozen-suite evidence at 867b1bf carries forward to 6a61c6b.

Verdict: PASS-STANDS
