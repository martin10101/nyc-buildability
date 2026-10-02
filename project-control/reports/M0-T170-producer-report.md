# Producer report — M0-T170 (D-091 T7): resource fit for 5 loop lanes

- Task: tune the loop's fail-closed resource limits for a shared 4-CPU / 8-GiB
  Linux box running 5 lanes (D-091-R001, D-091-R007; owner rule D-090-R076
  "keep memory under 70%, drop to 4 lanes as it approaches").
- Worktree: /root/project/w-M0-T170, branch task/M0-T170-resource-fit.
- Base (claim-seam) HEAD: 3a5e247bcc5f4b424086a98cffc6695a3d352012
- Producer HEAD: 6d61ceb5dd068c0116145b576cca4209f9c423e2 (differs from base)

## Guard
`git -C /root/project/w-M0-T170 rev-parse --show-toplevel` -> /root/project/w-M0-T170;
branch task/M0-T170-resource-fit; HEAD was 3a5e247b. PASS, worked only in the worktree.

## Files changed (all inside allowed_paths; one commit 6d61ceb5)
- tools/agent_supervisor/resource_sampling.py (+181)
- tools/agent_supervisor/run_budget.py (+88)
- tools/agent_supervisor/config.py (+10)
- tools/agent_supervisor/config.example.toml (+23/-1)
- tools/test_agent_supervisor_resource_fit.py (+379, new)
Report (this file) copied to project-control/reports/M0-T170-producer-report.md by the orchestrator.

## What was built

### (a) Linux memory pause ceiling — derived, fail-closed (resource_sampling.py)
- `MEMORY_PAUSE_FRACTION = 0.70` encodes owner rule D-090-R076. The ceiling in
  BYTES is DERIVED from the MEASURED physical total, never hard-coded 8 GiB.
- `read_proc_meminfo(reader=None)` parses /proc/meminfo kB rows to bytes;
  injectable; raises on any read failure (fail closed).
- `resolve_memory_ceiling_bytes(physical, configured_ceiling_bytes=None,
  fraction=0.70)` = `min(configured, floor(0.70*physical))`. Guarantees the
  ceiling never exceeds 70% of real RAM and respects a tighter owner config.
  On an 8-GiB box -> ~5.6 GiB even if config still names the 8-GiB PC default;
  derivation tracks the box (16-GiB box -> ceiling above 8 GiB; 4-GiB -> below).
- `evaluate_linux_memory(...)` -> `MemoryPauseVerdict(known, pause, used, total,
  ceiling, reason)`. PAUSE at/above the ceiling; PAUSE + known=False when
  /proc/meminfo is unreadable, missing MemAvailable, or implausible
  (available>total). Working memory used = MemTotal - MemAvailable.
- `linux_memory_gauge_sample(reader=None)` emits a `memory_bytes` GaugeSample
  (known=True value=used) that the EXISTING loop gate + CircuitBreakers enforce
  against `max_memory_bytes` with NO edit to loop.py or circuit_breakers.py; a
  read failure returns a sampling OUTAGE (known=False, structural=False), which
  the loop already treats as a conservative pause. The Linux launcher (M0-T166)
  sets `max_memory_bytes = resolve_memory_ceiling_bytes(...)` to wire the 70%.
- The Windows stdlib sampler (`ResourceSampler.sample`, memory_bytes =
  structural-unknown) is UNCHANGED.

### (b) Global + per-lane review/combine admission — fail-closed (run_budget.py)
- `admit_review_or_combine(global_active, lane_active, global_limit, lane_limit,
  lane="")` -> `AdmissionVerdict`. A request starts only when BOTH the lane is
  below its per-lane cap AND the box is below the global cap; per-lane checked
  first so one lane can't take both global slots. `admitted=False` means WAIT
  (never over-subscribe). Fail closed: unreadable/negative/non-int active count
  or a non-positive limit admits nothing. `GLOBAL_REVIEW_OR_COMBINE_DEFAULT = 2`.
  Stateless by design — the caller's own process registry is the authority on
  live children (consistent with resource_sampling's note on process counts).

### (c) Per-lane caps + config (config.py, config.example.toml)
- Two new immutable Limits fields, parsed by the existing positive-int
  validator (no new parse logic): `max_concurrent_reviews_or_combines = 2`,
  `max_concurrent_reviews_or_combines_per_lane = 1`.
- config.example.toml documents the Linux values beside the PC values; the PC
  values (max_memory_bytes 8589934592, max_cpu_percent 90, max_processes 24) are
  UNCHANGED. CPU stays the 90% policy ceiling and stays fail-closed-on-outage
  (not stdlib-measurable). max_processes 24 covers 5 workers + <=2 review/combine.

## Acceptance scenarios -> tests (tools/test_agent_supervisor_resource_fit.py)
- PRIMARY: `MemoryCeilingDerivationTests` + `MemoryCeilingThroughRealBreakerTests`
  — ceiling <= 70% of measured 8-GiB host, derived not hard-coded; at/above ->
  TRIP/pause through the real breaker and real loop gate; below -> dispatches.
- BOUNDARY: `ConcurrencyAdmissionTests` — a third request waits while two run;
  per-lane cap holds even when global has room; both dimensions required.
- MISSING/AMBIGUOUS: `UnreadableGaugeFailClosedTests` +
  `UnreadableGaugePausesLoopTests` — unreadable/missing/implausible meminfo and a
  CPU sampling outage fail closed (pause) through evaluate_linux_memory, the
  gauge sample, and the real loop; bad admission counts/limits admit nothing.
- REGRESSION: `RegressionTests` — PC defaults unchanged, new limits default/parse,
  example still loads, Windows memory gauge still structural-unknown.

## Commands run (venv: /root/project/lanes-runtime/venv/bin/python 3.12.3)
- `pytest -q tools/test_agent_supervisor_resource_fit.py` -> 23 passed.
- `pytest -q tools/test_agent_supervisor_phase1.py
  tools/test_agent_supervisor_resource_sampling.py` -> 92 passed, 3 subtests.
- `pytest -q tools/test_agent_supervisor_bounded_mode.py
  tools/test_agent_supervisor_bounded_contracts.py` -> 144 passed, 48 subtests
  (run_budget coverage).
- `pytest -q tools/test_agent_supervisor_manifest_binding.py
  tools/test_agent_supervisor_golden_run.py` -> manifest_binding all pass;
  golden_run 67 passed, 1 skipped, 7 FAILED.
- `ruff check` on the 4 edited .py files -> All checks passed.
- `python3 tools/modularity_check.py --check` -> exit 0 (no new flags; my files
  not flagged. config.py 700, resource_sampling 325, run_budget 819 lines).

## The 7 golden_run failures are PRE-EXISTING and unrelated to this task
They are platform-containment refusals: `outcome=unsupported_platform`,
`containment_refused` — this Linux host's default containment is `process_group`,
but the start path requires Windows `job_object` (M0-T052 PIN). Proof of
independence: with my 4 source files reverted to base (HEAD~1) in the worktree,
the same golden_run tests FAIL IDENTICALLY (2/2 re-checked), then I restored HEAD
(tree clean at 6d61ceb5). The code I touched (limits fields, run_budget admission,
resource_sampling memory functions, example doc) is not on the containment path.
Those scenarios are Windows-containment integration tests that cannot pass on a
Linux box; they are not in this task's required test set (config, resource_sampling,
run_budget), all of which pass.

## Rules / scope honored
- Edited only allowed_paths. No edits to project-control/, .claude/, .github/,
  services/**, apps/**, loop.py, circuit_breakers.py, launch_seam.py, cli.py, or
  any M0-T166/M0-T169 path. No real controller config touched.
- No dependency added. No new module outside allowed_paths. Did not start/commission
  a loop, push, merge, run gh or tools/project_control.py. Memory kept light (one
  small test batch at a time).
- Every existing fail-closed gauge and the PC/Windows defaults preserved; Windows
  tests pass unchanged.

## Assumptions / limitations
- Runtime WIRING of these primitives into the Linux launch path (setting
  `max_memory_bytes` to the resolved ceiling, calling admit_review_or_combine per
  review/combine spawn, feeding linux_memory_gauge_sample to the loop) belongs to
  M0-T166 (launch_seam.py/cli.py are in this packet's forbidden_paths). This task
  delivers the deterministic, tested primitives + config + documentation.
- CPU is not measured stdlib-only; it keeps the existing structural-unknown /
  fail-closed-on-outage behavior and the 90% policy ceiling (no CPU measurement
  added, per "keep every existing fail-closed gauge").
- 70% is a module constant (MEMORY_PAUSE_FRACTION), not a new config key, to
  minimize immutable-config growth; the "drop to 4 lanes" action is operator/
  launch-side and documented in config.example.toml, not enforced here.
- Recertification: every tools/agent_supervisor/** edit invalidates the frozen
  certification; the one recertification task after all D-091 code tasks covers it
  (packet risk, acknowledged).

## Requested status: awaiting_gate (G0, G2, G3, G4)
Reviewers: code-reviewer, ci-evidence-verifier, directive-compliance-verifier.

END-OF-REPORT
