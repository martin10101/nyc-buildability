# M0-T173 producer report (D-091 TW3: Linux resource wiring)

Producer: backend-engineer. Worktree: /root/project/w-M0-T173
Branch: task/M0-T173-linux-resource-wiring
Claim-seam base: 12364237f7f32aa0bb3d7916ca31a93371f7283d
Head after work: **7d5ea246bf07900cec9d47c411ec56ec9ef6c981** (differs from claim seam)
Directive refs: D-091-R001 (obligation: move loop to Linux), D-091-R007 (harness: reviewed/certified before use)

## What was built

On POSIX the running controller now enforces the 70% working-memory pause ceiling
through M0-T170's unchanged primitives; Windows behaviour is byte-identical.

1. The resource sampler's memory reading on Linux comes from `/proc/meminfo`
   (`linux_memory_gauge_sample`), fed through the UNCHANGED `loop._check_resources`
   + `CircuitBreakers.gauge` path (loop.py / circuit_breakers.py NOT touched). An
   unreadable gauge returns a sampling OUTAGE (`known=False, structural=False`),
   which the loop already treats as a conservative pause (fail closed).
2. The controller's effective `max_memory_bytes` is resolved at launch to
   `resolve_memory_ceiling_bytes(MemTotal)` = no more than 70% of MEASURED RAM
   (owner rule D-090-R076), never above a tighter configured ceiling, derived from
   the box (not a hard-coded byte count).
3. On Windows nothing changes: `posix_memory_ceiling_bytes` returns None (configured
   ceiling kept byte-for-byte) and `build_resource_sampler` attaches no memory gauge
   (memory_bytes stays a structural unknown).

## Files changed (vs claim seam 12364237)

- `tools/agent_supervisor/resource_sampling.py`  (+64 / -3; stdlib-only preserved)
  - `ResourceSampler.__init__` gains optional injectable `memory_gauge`
    (default None -> unchanged structural-unknown behaviour).
  - `ResourceSampler.sample()` substitutes the live reading for `memory_bytes`
    ONLY when a `memory_gauge` is wired; else unchanged.
  - NEW `posix_memory_ceiling_bytes(configured, *, meminfo_reader, fraction)`:
    None off-POSIX; on POSIX `resolve_memory_ceiling_bytes(MemTotal, ...)`; RAISES
    on unreadable/missing/implausible /proc/meminfo (no launch under an unmeasured
    ceiling, AD-025).
  - NEW `build_resource_sampler(*, disk_path, log_paths, meminfo_reader)`: wires the
    POSIX memory gauge via `functools.partial(linux_memory_gauge_sample, reader)`;
    off-POSIX attaches no gauge.
  - No config import added -> the module stays config-free / stdlib-only as M0-T170
    reviewed it. The config.Limits manipulation lives in cli.py (which already owns it).
- `tools/agent_supervisor/cli.py`  (+9 / -3 raw; **net +3 code lines + 3 comment**;
  modularity baseline SLOC 2685, material-growth trip = max(50, 268) -> far under)
  - import line swapped: `ResourceSampler` -> `build_resource_sampler,
    posix_memory_ceiling_bytes` (net 0).
  - breaker construction: resolve the POSIX ceiling and `dataclasses.replace` it into
    `config.limits` before `CircuitBreakers(...)` (1 line -> 4 code lines + 3 comment).
  - sampler construction: `ResourceSampler(...)` -> `build_resource_sampler(...)`
    (same kwargs; net 0).
  - `dataclasses` and `os` were already imported; no new imports.
- `tools/test_agent_supervisor_linux_gauge.py`  (NEW, 15 tests)

loop.py, circuit_breakers.py, run_budget.py: UNTOUCHED (confirmed by diff).

## Acceptance scenarios -> tests (all drive the REAL sampler/loop/breaker; no live provider)

- PRIMARY (sampler reports from /proc/meminfo; loop pauses at/above resolved 70%
  ceiling, dispatches below):
  `LinuxGaugeThroughRealLoopTests.test_memory_over_ceiling_pauses_the_loop_before_dispatch`
  (stopped == resource_gauge_hard_threshold, runner.prompts == []),
  `...test_memory_under_ceiling_dispatches` (dispatches, prompts == ["first unit"]).
  Paired: disk_path/log_paths identical, ONLY the injected memory reading differs,
  so the trip is provably memory. Plus
  `BuildResourceSamplerTests.test_posix_emits_a_live_known_memory_reading`,
  `CliLaunchWiringTests.test_posix_breaker_ceiling_trips_at_70pct`,
  `PosixMemoryCeilingTests.test_posix_ceiling_is_70pct_of_measured_total` /
  `...test_configured_ceiling_can_only_tighten_the_posix_ceiling`.
- MISSING/AMBIGUOUS (unreadable gauge pauses, fail closed):
  `LinuxGaugeThroughRealLoopTests.test_unreadable_gauge_pauses_the_loop`,
  `BuildResourceSamplerTests.test_posix_unreadable_gauge_is_a_conservative_outage`,
  `PosixMemoryCeilingTests.test_unreadable_meminfo_raises_fail_closed` /
  `...test_missing_memtotal_raises_fail_closed`.
- REGRESSION (Windows/stdlib unchanged):
  `RegressionTests.test_plain_sampler_memory_gauge_stays_structural_unknown`,
  `...test_measurable_gauges_still_present_and_known`,
  `BuildResourceSamplerTests.test_non_posix_attaches_no_gauge_memory_stays_structural_unknown`,
  `PosixMemoryCeilingTests.test_non_posix_returns_none_keeping_configured_ceiling`,
  `CliLaunchWiringTests.test_non_posix_keeps_the_configured_8gib_ceiling`.

Note: POSIX-specific tests patch `os.name="posix"` ONLY around construction (never
around `run_cycle`, whose containment detection is platform-sensitive) and always
inject a synthetic /proc/meminfo reader, so the suite is deterministic and green on
both Linux and Windows CI (supervisor-bridge runs the whole glob on windows-latest).

## Commands run (venv /root/project/lanes-runtime/venv/bin/python 3.12)

- `ruff check` on resource_sampling.py, cli.py, test_agent_supervisor_linux_gauge.py
  -> **All checks passed!** (no ruff config in repo -> defaults E4/E7/E9/F)
- `pytest -q tools/test_agent_supervisor_linux_gauge.py` -> **15 passed** in 1.88s
- `pytest -q tools/test_agent_supervisor_resource_fit.py` -> **23 passed**
- `pytest -q tools/test_agent_supervisor_resource_sampling.py` -> **12 passed, 3 subtests**
- `pytest -q tools/test_agent_supervisor_phase1.py` -> **80 passed** (includes the CLI
  doctor + manifest + breakers posture tests; doctor's `_check_resource_sampling`
  reads only MEASURABLE/STRUCTURAL constants, unchanged)
- `python3 tools/modularity_check.py --check` -> **failures 0**; 28 pre-existing
  warnings, cli.py only the pre-existing `symbol_ceiling` warning (no new flag; no
  material growth).

## Consumer sweep of the changed behaviour contract (cli.cmd_start + ResourceSampler)

- `tools/test_agent_supervisor_mrl_launch_path.py` -> **52 passed**
- `tools/test_agent_supervisor_start_reentry.py` -> **16 passed**
- `tools/test_agent_supervisor_recovery_probes.py` -> **88 passed, 26 subtests**
- `tools/test_agent_supervisor_model_chain.py::CrashResumeTests` -> 5 FAILED, 1 passed.
  PRE-EXISTING Linux-only: these assemble a supervised `start`, which `cmd_start`
  refuses at the C1 host-containment gate (`containment_precondition()`, cli.py:3029)
  because this box's default containment is `process_group`, not `job_object`, so
  `_run_loop` (cli.py:3123, where my edits live) is NEVER reached and the captured
  loop's `resource_sampler` is None. PROVEN pre-existing: checked out the claim-seam
  (12364237) cli.py + resource_sampling.py and re-ran the class -> the IDENTICAL 5
  failures (same assertion line 793/868). These pass on windows-latest (job_object),
  matching the M0-T170 G3/G4 report's documented golden_run/start-path Linux-only
  failures. Working tree restored to HEAD 7d5ea246 afterwards (clean).
- `tools/test_agent_supervisor_model_chain.py` (whole file) was OOM-killed (signal 9)
  by the kernel on this 8-GiB sandbox: its `RealProcess*` classes spawn real
  subprocesses. Environmental, not an assertion failure and not my change. The single
  relevant test (`test_run_loop_wires_a_real_resource_sampler_into_the_loop`) uses a
  CapturingLoop (no spawn) and is compatible with `build_resource_sampler` (it asserts
  `isinstance(sampler, ResourceSampler)` + `log_paths` truthy + capability_report
  live_sampled == free_disk/retained_log — all still true); its failure here is only
  the pre-existing containment refusal above.

## Assumptions / limitations

- The launch ceiling and the runtime gauge both read the SAME /proc/meminfo; a POSIX
  box that cannot read it refuses to launch (fail closed) AND would pause at runtime,
  so there is no window of running under a loose ceiling.
- Did not run the full `tools/test_agent_supervisor_model_chain.py` to green locally
  (OOM-kill from its real-subprocess classes on this sandbox) nor the whole
  supervisor glob; that whole-glob regression is CI's supervisor-bridge job (Windows,
  job_object) where the start-path/containment tests pass.
- Recertification: every tools/agent_supervisor/** edit (incl. this cli.py change)
  invalidates the frozen controller manifest digest (tools/controller_update/
  source_binding.json lists cli.py). This is the packet's declared risk and is handled
  by the later D-091 recertification task (TW4) — NOT in scope here, source_binding.json
  NOT touched.

## Scope / rules honoured

- Edited only allowed_paths (resource_sampling.py, cli.py, new test). Did NOT touch
  project-control/, .claude/, .github/, services/**, apps/**, loop.py,
  circuit_breakers.py, run_budget.py, other D-091 task paths. Did not start/commission
  a loop, push, merge, run gh or project_control.py, or add any dependency.
- No fail-closed check, gate, reviewer-independence rule, or orchestrator authority
  weakened — changes are additive wiring; the breaker/loop/gate path is unchanged.

## Requested status: awaiting_gate (G0, G2, G3, G4; reviewers code-reviewer, ci-evidence-verifier)

END-OF-REPORT
