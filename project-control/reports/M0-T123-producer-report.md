# M0-T123 — Producer report: resume-path defect fix (rotation ceiling + cwd enforcement seam)

Task M0-T123 (governance; D-024 Amendment 19 rows R331–R344). Producer:
supervisor-resume-path-producer. Worktree: `…/.claude/worktrees/agent-afd9fa16ba445dd2a` (isolated,
verified not the primary checkout). Base identity synced to control tip
`7b78d6c49c19225f2ebd8b280b59cd9d0874a80c`. All changes left uncommitted for the orchestrator.

## 1. Root-cause trace (both dimensions, file:line)

**(a) Rotation ceiling never evaluated on the resume/start path.**
- `loop.py:936-939` `_flag_rotation_if_needed` — the ceiling is compared to `run_result.context_tokens`
  only *after* a unit returns, and persists `rotation_pending` durably (`rotation.observe_mid_unit`,
  loop.py:950).
- `loop.py:2587-2589` — the rotation seam fires only *between* cycles when `rotation_pending()` is set;
  `loop.py:2526-2528` covers only the `FORWARD_PROMPT` resume. The ordinary
  `IDLE→PREFLIGHT→first-cycle` `run()` path (loop.py `for index in range(start_index, …)`) dispatched
  `run_cycle → run_unit` (loop.py:1487) with **no pre-first-dispatch ceiling seam**.
- Durable proof: preserved `state_kv` reads `rotation_pending=true`,
  `rotation_pending_reason="context_threshold"`; audit **seq 24** flagged it at 604,772 tokens; the
  run HALTED (seq 30) before the between-cycle seam could act; the `owner-restart`→`start` (seq 34→37)
  dispatched **seq 40** (`context_tokens 640224`, `returncode 1`, no checkpoint) with the flag still
  unconsumed.

**(b) cwd bound to the primary control checkout.**
- `cli.py:2642` `worktree = pathlib.Path(args.worktree or repo).resolve()` with `repo = args.repo or
  checkout` (cli.py:2641) and `--worktree` defaulting to `None` → the worktree defaults to the primary
  checkout when `--worktree` is absent.
- `cli.py:2672` `RunnerConfig(cwd=str(worktree), …)` → `claude_runner.py` `run_unit`
  `subprocess.Popen(argv, … cwd=self.config.cwd or None …)` launched there. No guard bound cwd to the
  packet's declared worktree.
- Primary proof: every cycle-2 transcript record is stamped `cwd = …\ctl24` (incl. a `nested_memory`
  attachment loading `…\ctl24\.claude\rules\code-architecture.md`); cycle-1 is stamped `…\wt-m0t107`.

## 2. The fix — one seam, three enforcement points

`tools/agent_supervisor/launch_seam.py` (NEW) is the single pure decision seam (ceiling + cwd, typed
fail-closed refusals; 400k imported from `RotationThresholds`). Enforced at:

1. **Runner chokepoint** — `ClaudeRunner.run_unit` calls `launch_seam.enforce_launch` immediately
   before its one `subprocess.Popen`; a non-proceed decision raises a typed `RunnerError` carrying the
   seam code. Active when the production path bound `expected_worktree`; unbound (fake-exe test)
   runners defer the cwd guard to the loop/CLI seam.
2. **CLI worktree gate** — `cli._run_loop` calls `launch_seam.evaluate_packet_worktree_binding` and
   raises `LoopError` (rendered as a typed refusal) when the bound worktree is not the packet's
   declared worktree; also binds `expected_worktree`/`primary_checkout` on the runner config.
3. **Loop pre-first-dispatch seam** — `SupervisedLoop._rotate_over_ceiling_before_first_dispatch`
   (routed through `launch_seam.evaluate_ceiling`), called by `run()` before the first cycle, sheds a
   recorded over-ceiling session (or consumes an unconsumed durable `rotation_pending=context_*`) so
   the first unit launches as a fresh, distinct session in the packet worktree.

Supporting additive changes: `RunnerConfig` (`expected_worktree`, `primary_checkout`,
`resume_context_tokens`, `resume_usage_known`) + `with_resume` telemetry; `ProviderSession`
(`context_tokens`, `usage_known`, unknown≠zero) + `record_provider_session`;
`loop_turnover.actuate_resume` telemetry threading; per-unit `record_provider_session` persists tokens.

## 3. Call-site enumeration + same-seam proof (R339)

Mechanical sweep (`ReachabilitySweep`) over the package ASTs — every function that BOTH builds the
worker argv (`build_argv`) and calls `Popen`:

| Site | Kind | Seam-routed? |
|---|---|---|
| `claude_runner.py:run_unit` | worker DISPATCH (brokers permissions, appends the S8.3 checkpoint contract, resumable) | YES — `launch_seam.enforce_launch` precedes the sole `subprocess.Popen` |
| `claude_runner.py:probe_model_launch` | model-availability PROBE (no work unit, no permission broker, no resume) | N/A — non-worker; ceiling/cwd do not apply (classified in-test) |

Production enforcement points, each removal-sensitive:
`run_unit` (Popen chokepoint), `cli._run_loop` (packet-worktree gate + `expected_worktree`),
`SupervisedLoop.run` → `_rotate_over_ceiling_before_first_dispatch` (ceiling shed via the seam).
Rotation/turnover resume actuation (`loop_turnover.actuate_resume` → `runner.with_resume`) carries
telemetry so the runner chokepoint fails an over-ceiling `--resume` closed.

## 4. Red/green bypass proof (trimmed)

Removal sensitivity (R340) prunes the seam STATEMENT via AST unparse (keeping valid Python) and
re-runs the same checker:
- `test_RED_removing_the_seam_statement_uncovers_run_unit` — bypass source has no `enforce_launch`
  call yet still reaches `subprocess.Popen` → RED.
- `test_RED_run_loop_without_the_gate_is_a_bypass` — pruned `_run_loop` no longer calls
  `evaluate_packet_worktree_binding`.
- `test_RED_run_without_the_shed_statement_is_a_bypass` — pruned `run()` no longer calls the shed.
Loop-level RED/GREEN pair: the seeded pre-fix shape holds the over-ceiling session + set flag at first
dispatch; the fixed seam sheds it and consumes the flag.
Runner-level AS-1: a 640,224-token `--resume` raises `over_ceiling_resume_forbidden` before Popen
(fake exe never runs).

## 5. Fixtures (R341) + before/after source hashes

Fixture `tools/agent_supervisor/fixtures/resume_path_defect_2026-08-30_m0t123.json`, DERIVED
read-only from the preserved evidence (sanitized: home prefixes masked to `[HOME]`, load-bearing
shape only; session ids are random UUIDs). SHA-256 of the four sources, recorded BEFORE and AFTER the
derivation — **identical** (sources never written):

| Source | Before | After |
|---|---|---|
| `supervisor_journal.sqlite3` | `a4acb370f3a23fd5193c27d16e729a6b6035c53c368a10c52673de8b5de29255` | *(unchanged)* |
| `audit.jsonl` | `e80c057cabc24478ab67d785e2f903696f6cc1fcf7cbf782db9fd6f284430c83` | *(unchanged)* |
| transcript cycle-1 (`02b014ee`) | `3a0d1f30664b1deba7b6cd47a0a69bdc84906332eb3ed180aea5e74e2f8b9b17` | *(unchanged)* |
| transcript cycle-2 (`798d2f00`) | `3c9185687f12e86a2e066b18e8347a15840be94f981a52af3965f01394adbfaf` | *(unchanged)* |

Fixture contents: the durable over-ceiling state (`rotation_pending=true`,
`rotation_pending_reason=context_threshold`, `provider_session_continuity` with **no** token field →
unknown telemetry); the audit excerpt (seq 24 = 604772/context_threshold; seq 40 = 640224/rc1); the
two transcript shapes (cwds `…/wt-m0t107` vs `…/ctl24`, no `result` record on cycle 2, the recovered
`max_turns_reached` terminal event).

## 6. Terminal-evidence finding (R343/R344) — RECOVERED

The actual terminal event IS recoverable from the primary transcript (session `798d2f00`, records
92–95): `max_turns_reached {maxTurns: 12, turnCount: 13}`, preceded by a `nested_memory` attachment
loading `…\ctl24\.claude\rules\code-architecture.md` and 13 `total_tokens_reminder` attachments, with
the checkpoint-contract prompt as the last queued prompt. There is **no `result` record** and the
audit `claude_unit_completed` (seq 40) carried **no `stderr_tail`**. The honest finding: the worker
**exhausted its 12-turn budget** (turn 13) re-orienting in the primary control checkout before it
could emit a structured checkpoint — this is the recovered terminal event, and it **contradicts** the
earlier "probable provider context-limit rejection" inference (M0-T107 journey §3.3). That
context-limit rejection is **NOT proven** by the primary evidence and is explicitly abandoned; the
recovered cause is turn-budget exhaustion, itself driven by the wrong-cwd defect (b).

## 7. AS → named-test mapping

| AS | Named test(s) |
|---|---|
| AS-1 (reproduced defect red/green) | `RunnerChokepoint::test_AS1_over_ceiling_resume_refuses_before_launch`; `PreDispatchCeilingSeam::test_AS1_pre_fix_path_would_carry_the_over_ceiling_session_forward` (RED) + `::test_AS1_fixed_seam_sheds_before_first_dispatch` (GREEN) + `::test_AS1_sheds_on_durable_flag_even_when_telemetry_unknown` |
| AS-2 (ceiling matrix) | `LaunchSeamUnit::test_AS2_at_threshold_exactly_rotates_never_resumes` / `_above_threshold_rotates` / `_below_threshold_resume_permitted` / `_missing_telemetry_fails_closed_never_assumed_below` / `_fresh_launch_has_no_ceiling` |
| AS-3 (cwd binding + Windows forms) | `LaunchSeamUnit::test_AS3_*`; `RunnerChokepoint::test_AS3_cwd_primary_checkout_refuses_before_launch` / `_cwd_mismatch_refuses`; `FixtureRegression::test_AS3_transcripts_show_the_cwd_isolation_defect` |
| AS-4 (rotation preservation / exactly-once / freeze) | `PreDispatchCeilingSeam::test_AS4_a_below_ceiling_session_is_not_shed` / `_shed_is_idempotent_second_call_is_noop`; the shed clears the provider session (freeze) and consumes the flag exactly once |
| AS-5 (call-site closure + removal sensitivity) | `ReachabilitySweep::test_run_unit_seam_precedes_the_only_worker_popen` / `_the_only_worker_dispatch_popen_is_run_unit_and_it_is_seam_guarded` / `_run_loop_wires_*` / `_run_wires_the_pre_first_dispatch_ceiling_seam` / `_the_shed_routes_through_the_launch_seam` + the three `test_RED_*` |
| AS-6 (lifecycle: recovery/restart/turnover/continuation, provider failure) | `RunnerChokepoint::test_AS1_resume_with_unknown_telemetry_fails_closed` (typed refusal not crash); `CliWorktreeGate::test_packet_worktree_mismatch_is_a_typed_loop_refusal`; `test_agent_supervisor_loop_turnover.py::ActuateResumeTelemetry::*` (resume actuation); concurrent-controller lock unchanged (restart_channel suite) |
| AS-7 (fixtures reproduce defect; before/after hashes) | `FixtureRegression::test_AS7_source_hashes_are_the_recorded_baselines` / `_durable_state_reproduces_the_over_ceiling_shape` / `_audit_excerpt_carries_the_defect_values` |
| AS-8 (terminal-evidence honesty) | `FixtureRegression::test_AS8_cycle2_transcript_has_no_terminal_result_record` / `_recovered_terminal_event_is_max_turns_not_a_provider_rejection` |

## 8. Test totals (per suite, control tip 7b78d6c, Python 3.11 sandbox)

> **Correction (report-accuracy, 2026-08-30).** An earlier draft of this section reported
> `test_agent_supervisor_launch_seam.py — 46 passed` and the full suite as `2869 passed`. Both were
> wrong and are corrected below to independently re-verified numbers. The **46** was a
> transcription/attribution error: it was read from a *bundled* run
> (`launch_seam.py` + the single `subagent_telemetry::test_all_committed_fixtures_free_of_home_prefixes`
> hygiene test = 45 + 1), not the launch-seam suite alone. No test was deleted, merged, or renamed —
> `--collect-only` reports **45 collected** deterministically. The **2869** was measured one increment
> before the AS-8 test `test_AS8_recovered_terminal_event_is_max_turns_not_a_provider_rejection` was
> added; the current full suite is **2870**.

- `test_agent_supervisor_launch_seam.py` — **45 collected, 45 passed** (`--collect-only -q` and `-q`,
  deterministic)
- `test_agent_supervisor_session_continuity.py` (NEW) — **7 passed** (included in the totals below)
- `test_agent_supervisor_loop_turnover.py` (NEW) — **4 passed** (included in the totals below)
- Named related suites together (launch_seam + loop + loop_turnover + session_continuity +
  claude_runner_env + crash + endurance + restart_channel + golden_run + rotation + runner +
  turnover_integration) — **533 passed**
- Full `tools/test_agent_supervisor_*.py` — **2870 passed, 2 skipped** (the 2 skips are pre-existing,
  untouched by this task)
- `modularity_check.py --check` — **selected 329 files; failures 0; warnings 10** (all pre-existing;
  `launch_seam.py` not among them)
- Ruff 0.13.0 on all new/changed files — **all checks passed** (the 5 residual F401s in
  `loop.py`/`cli.py` are pre-existing, not introduced here, and outside the CI ruff path
  `services/api`)

## 9. Files changed

Modified: `tools/agent_supervisor/{session_continuity,claude_runner,loop,loop_turnover,cli}.py`.
New: `tools/agent_supervisor/launch_seam.py`; `tools/agent_supervisor/fixtures/resume_path_defect_2026-08-30_m0t123.json`;
`tools/test_agent_supervisor_{launch_seam,session_continuity,loop_turnover}.py`;
`tools/agent_supervisor/README.md` (+ section), `docs/CONTROLLER_UPDATE_RUNBOOK.md` (+ section);
`project-control/reports/M0-T123-{producer-report,repair-record}.md`. All within allowed_paths.

## 10. Assumptions, limitations, risks

- **Assumption:** the durable `rotation_pending=context_threshold` flag is the authoritative
  cross-process "this session crossed the ceiling" signal (confirmed live in `state_kv`); the new
  per-session `context_tokens` telemetry is a forward-looking reinforcement (the preserved record
  predates it → unknown → fail-closed, which the shed handles via the flag).
- **Limitation (sandbox):** the repo targets Python 3.12; the sandbox is 3.11. These modules use
  `from __future__ import annotations` (no PEP 695), so all suites collect and pass under 3.11; CI
  provides the 3.12 evidence. No live supervisor `start`/`owner-restart`/`clear-recovery` was run
  against the real runtime (R345); every test uses constructed/temp journals and fixture copies.
- **Scope note:** the pre-existing `loop.py`/`cli.py` F401 lint warnings are unrelated to this task
  and were left untouched (not in scope; not on the CI ruff path).
- **Risk (low):** the runner-level cwd guard is active only when `expected_worktree` is bound (the
  production `_run_loop` always binds it); unbound fake-exe runners defer to the CLI/loop seam. This
  keeps the ~2800-test suite byte-for-byte green while the production launch path is fully guarded —
  proven by the reachability sweep and the CLI gate.
- **Process:** this change touches `tools/agent_supervisor/**` → it invalidates the fourth
  certification and requires the R247 recertification (M0-T124), manifest verification, and the R276
  preflight before any further start (R346), then STOP for the owner's separate live-start decision
  (R347). PR #241 untouched.
