# M0-T123 — RepairRecord (H2 8-predicate gate) + red/green/removal-proof evidence

Task: M0-T123 (governance; D-024 Amendment 19 rows R331–R344). Producer:
supervisor-resume-path-producer. Supervisor-freeze qualifying evidence: **D-024-R330** (the reproduced
cycle-2 counted stop, `project-control/reports/M0-T107-cycle2-live-journey.md`). Reliability standard
sections applied: §2 (smallest fitting change), §3.1/§3.4 (behavior proof, removal sensitivity),
§4/§5 (resume/idempotency surface), §8 (verification contexts), §9 (triage). Frozen identity: control
tip `7b78d6c49c19225f2ebd8b280b59cd9d0874a80c`.

## 1. The defect (reproduced; grounded in the preserved durable evidence)

Two failures reproduced live in cycle 2, both proven from the preserved journal/audit
(sha `a4acb370…` / `e80c057c…`) and transcripts (`3a0d1f30…` / `3c918568…`):

- **(a) Rotation ceiling never evaluated on the resume/start path.** Audit **seq 24**
  `rotation_pending_flagged | context_threshold` ("cumulative context usage 604772 crossed the
  configured threshold 400000") set the durable flag; the run then **HALTED** (seq 30) before the
  between-cycle seam could act. The durable state at the next start still read
  `rotation_pending=true` / `rotation_pending_reason="context_threshold"` (read live from
  `state_kv`). The `owner-restart` → `start` (seq 34→37) dispatched a unit (**seq 40**,
  `context_tokens: 640224`, `returncode: 1`, no checkpoint → seq 42/43 `unsafe_condition` +
  `no_valid_checkpoint`) **without ever consulting that flag**. Root cause: `loop.py` `run()`
  evaluated the ceiling only *after* a unit via `_flag_rotation_if_needed` (loop.py:936-939) and
  acted only at the between-cycle seam (loop.py:2587-2589); the ordinary `IDLE→PREFLIGHT→first-cycle`
  path had **no pre-first-dispatch ceiling seam**.
- **(b) cwd bound to the primary control checkout.** Every content record of the cycle-2 transcript
  (session `798d2f00`) is stamped `cwd = …\ctl24` (the orchestrator's PRIMARY control checkout),
  including a `nested_memory` attachment loading `…\ctl24\.claude\rules\code-architecture.md`; the
  correct cycle-1 transcript (session `02b014ee`) is stamped `…\wt-m0t107`. Root cause:
  `cli._run_loop` defaulted `worktree = args.worktree or repo` to the checkout when `--worktree` was
  absent (cli.py:2642) and bound `RunnerConfig.cwd = str(worktree)` (cli.py:2672) with no guard that
  the cwd was the packet's declared worktree; `run_unit`'s `subprocess.Popen(cwd=self.config.cwd …)`
  (claude_runner.py) then launched there.

**Recovered terminal event (R343/R344).** The cycle-2 transcript's terminal record is
`max_turns_reached {maxTurns: 12, turnCount: 13}` — the worker exhausted its 12-turn budget
re-orienting in the primary checkout before it could emit a checkpoint. There is **no `result`
record** and the audit carried **no stderr**. This CONTRADICTS the earlier "probable provider
context-limit rejection" inference: that hypothesis is not what the primary evidence shows and
remains **unproven**; the recovered terminal event is a turn-budget exhaustion, corroborating the
wrong-cwd mechanism (b) driving the ceiling crossing (a).

## 2. The fix (smallest fitting change, §2)

- **NEW `launch_seam.py`** — the single pure, fail-closed decision seam: `evaluate_cwd`,
  `evaluate_packet_worktree_binding`, `evaluate_ceiling`, `enforce_launch`, `enforce_or_raise`, typed
  refusal codes. No I/O, no journal writes, no provider contact. The 400k ceiling is imported from
  `RotationThresholds` (single source, never a second copy).
- **`claude_runner.py`** — the ironclad chokepoint: `run_unit` calls the seam immediately before its
  one `subprocess.Popen`; four additive `RunnerConfig` fields (`expected_worktree`,
  `primary_checkout`, `resume_context_tokens`, `resume_usage_known`); `with_resume` carries the
  resumed session's ceiling telemetry.
- **`cli._run_loop`** — refuses (typed `LoopError`) when the bound worktree is not the packet's
  declared worktree, and binds `expected_worktree`/`primary_checkout` on the runner config.
- **`loop.py`** — `_rotate_over_ceiling_before_first_dispatch` (routes through
  `launch_seam.evaluate_ceiling`) sheds a recorded over-ceiling session / consumes an unconsumed
  durable `rotation_pending=context_*` flag **before the first dispatch**; wired into `run()`; init
  restores the recorded session's telemetry; the per-unit `record_provider_session` now persists
  `context_tokens`/`usage_known`.
- **`loop_turnover.actuate_resume`** — threads the recorded session's telemetry into `with_resume`.
- **`session_continuity.py`** — additive `context_tokens`/`usage_known` on `ProviderSession`
  (unknown stays `None`, never a below-ceiling zero); legacy records read as unknown.
- **Docs**: README launch-seam section + two safety-rule bullets; `CONTROLLER_UPDATE_RUNBOOK.md`
  operator section with the refusal table. **Fixture**: `resume_path_defect_2026-08-30_m0t123.json`.
- NO policy loosening, NO budget reset, NO audit/journal edit, NO new dependency, NO live-runtime write.

## 3. Red → green → removal-proof (§3.1, §3.4; R340 removal sensitivity)

- **AS-1 red/green (runner):** `RunnerChokepoint::test_AS1_over_ceiling_resume_refuses_before_launch`
  — a `--resume` of a 640,224-token session raises `over_ceiling_resume_forbidden` **before** Popen
  (the fake executable never runs, so no session id is ever parsed). Below-ceiling / correct-cwd
  proceeds.
- **AS-1 red/green (loop):** `PreDispatchCeilingSeam` seeds the exact durable cycle-2 shape
  (`rotation_pending=context_threshold` + recorded session 798d2f00). The **pre-fix** shape (RED) still
  holds the over-ceiling session and the set flag at first dispatch
  (`test_AS1_pre_fix_path_would_carry_the_over_ceiling_session_forward`); the **fixed** seam sheds it
  and consumes the flag (`test_AS1_fixed_seam_sheds_before_first_dispatch`).
- **Removal sensitivity (R340), reachability sweep:** `ReachabilitySweep` derives sites from source
  ASTs and includes three RED reproductions that PRUNE the seam statement (via AST unparse, so the
  bypass source stays valid) and assert the invariant then fails:
  `test_RED_removing_the_seam_statement_uncovers_run_unit`,
  `test_RED_run_loop_without_the_gate_is_a_bypass`,
  `test_RED_run_without_the_shed_statement_is_a_bypass`. The GREEN invariants prove the seam precedes
  the only worker-dispatch Popen, `_run_loop` wires the packet-binding gate + `expected_worktree`, and
  `run()` wires the pre-first-dispatch shed which routes through `launch_seam.evaluate_ceiling`.

## 4. Affected-suite evidence (control tip 7b78d6c)

New suite `test_agent_supervisor_launch_seam.py`: **45 collected, 45 passed** (deterministic;
`--collect-only` confirms 45). Named related suites together
(`launch_seam + loop + loop_turnover + session_continuity + claude_runner_env + crash + endurance +
restart_channel + golden_run + rotation + runner + turnover_integration`): **533 passed**. Full
`tools/test_agent_supervisor_*.py`: **2870 passed, 2 skipped** (2 pre-existing skips, untouched).
(Report-accuracy correction 2026-08-30: an earlier draft cited `46 passed` for the launch-seam suite
— a bundled-run attribution error, 45 + 1 hygiene test — and `2869` full, measured one increment
before the AS-8 terminal-event test was added; both re-verified above.)
`modularity_check.py --check` → **failures 0** (10 pre-existing warnings; `launch_seam.py` not among
them). Ruff (0.13.0) on all new/changed files: **all checks passed** (the 5 residual F401s are
pre-existing in `loop.py`/`cli.py`, not introduced here, and are outside the CI ruff path
`services/api`). Read-only fixture sources re-hashed identical before/after derivation (producer
report §5).

## 5. H2 RepairRecord — the 8 predicates

1. **Wrapper-around-defective-path?** NO — the fix ADDS the missing pre-provider-contact seam the
   launch/resume paths never had; it does not wrap a broken function to hide its output. The real
   rotation path (`decide_continuity` context-shedding reorientation) is reused, not duplicated.
2. **Stale callers?** None left. Every worker-dispatch path funnels to `run_unit`'s single Popen,
   which is now seam-guarded; the reachability sweep proves `run_unit` is the sole worker-dispatch
   Popen and that the availability probe (`probe_model_launch`) is a non-worker path (no work, no
   resume). Existing rotation/turnover call sites are unchanged and still green.
3. **Regression test fails if fix removed?** YES — three AST removal-sensitivity tests go RED when the
   seam statement is pruned from `run_unit`, `_run_loop`, or `run()`; the loop-level RED/GREEN pair
   fails if the shed is removed. Mechanically derived from source, not hand-listed.
4. **Compatibility exception?** NONE — additive. New module + additive `RunnerConfig`/`ProviderSession`
   fields (defaulting to the prior behavior); unbound runners (the many fake-executable tests) defer
   the cwd guard to the CLI/loop seam and are byte-for-byte unchanged; legacy provider-session records
   read as unknown telemetry (fail-closed on resume). Full suite: 2870 passed, 2 skipped.
5. **Root cause vs symptom?** Root cause fixed at the boundary that owns launch/resume: a single seam
   before provider contact (ceiling + cwd), plus the missing pre-first-dispatch seam in `run()` and the
   packet-worktree gate in `_run_loop`. Not a symptom patch (e.g. raising `--max-turns`, which would
   only mask the wrong-cwd balloon).
6. **Defect named in tests?** YES — docstrings and assertions cite the reproduced cycle-2 defect, the
   604,772 → 640,224 token values, the `…/ctl24` vs `wt-m0t107` cwd delta, the `max_turns_reached`
   terminal event, and D-024 R331–R344.
7. **Search for other instances — COMPLETE enumeration of launch/resume sites.** The sweep enumerates
   every package function that BOTH builds the worker argv (`build_argv`) and calls `Popen`: exactly
   `{run_unit, probe_model_launch}`. Only `run_unit` dispatches/resumes a worker unit and it is
   seam-guarded; the probe is classified (no work contract, no resume, ceiling/cwd N/A). The three
   production enforcement points (runner Popen, CLI worktree gate, loop pre-first-dispatch shed) are
   each removal-sensitive. No other worker-launch site exists.
8. **Disposition:** FIXED at root across the complete launch/resume class; no auto-accept — re-review by
   the four independent reviewers (code, qa, security, directive-compliance) at the frozen identity,
   then the R247 frozen-identity recertification (M0-T124), manifest verification, and the R276
   preflight before any further start (R346), then STOP and present the live-start package for a
   separate owner decision (R347).
