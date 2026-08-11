# M0-T053 producer report — production child accounting + the C1 job-object containment gate

- **Task:** M0-T053 (backend, defect lane, gates G0/G2/G3/G5)
- **Producer:** backend-engineer (worktree-isolated agent session, 2026-08-11)
- **Base commit:** `37667ff` (origin/main)
- **Worktree the work is in:** `C:/Users/MLFLL/Downloads/nyc-zoning/nyc-development-feasibility-claude-pack/.claude/worktrees/agent-a4f689681ef40ec7f`,
  branch `worktree-agent-a4f689681ef40ec7f`. The isolation harness refused every
  command redirected at the `M0-T053-child-accounting` worktree named in the brief
  ("a worktree-isolated agent's git operations must target its own worktree"), so the
  changes are in the agent's own worktree at the same base commit. Nothing is committed
  or pushed; integration is the orchestrator's.

## Qualifying-evidence citation (supervisor-freeze §2/§3)

`project-control/reports/M0-T052-g5-security.md` — **SEC-MAJOR**, a *demonstrated security
risk*, with required corrections **C1** and **C2**, pinned verbatim at
`project-control/reports/M0-T036-ACTIVATION-CHECKLIST.md` → "ACTIVATION-RECORD PIN —
2026-08-08". Two holes were verified in source before any code was written:

- **(C2)** `recovery.record_launched_child` had **no production caller**. `run_unit`
  spawned the worker with `subprocess.Popen` + `container.adopt` and journaled nothing, so
  `account_for_children` always read an empty list in production and `recover_boot`'s
  surviving-child fail-closed was **inert**.
- **(C1)** kill-on-close containment is platform-conditional (Windows Job Object only), and
  `cmd_start` had **no containment gate**, so on a `taskkill` or `process_group` host a
  stranded-`START_CLAUDE` resume (M0-T052) could double-launch over an orphaned worker.

**Commit-message wording (as requested):**

> Qualifying evidence (supervisor-freeze §2/§3): `project-control/reports/M0-T052-g5-security.md`
> SEC-MAJOR — a demonstrated security risk — required corrections C1 (host-containment
> precondition enforced in the start launch path) and C2 (child-launch accounting wired to
> the production launch path), pinned in `project-control/reports/M0-T036-ACTIVATION-CHECKLIST.md`
> "ACTIVATION-RECORD PIN — 2026-08-08". Closes the double-launch residual so protection no
> longer rests on platform kill-on-close alone. Hard dependency of M0-T056 (D-010-R347: no
> duplicate workers, fail-closed, audit-linked). Supervisor stays SHADOW-ONLY; this change
> only ADDS refusals and enables no path.

## Files changed (all inside `allowed_paths`)

| File | Change | Why it is minimal |
|---|---|---|
| `tools/agent_supervisor/claude_runner.py` | `ClaudeRunner.__init__` takes an optional `journal`; `run_unit` calls `self._record_launched_worker(...)` right after `container.adopt(pid)` and `self._settle_worker_record(process)` right after the `finally` block; two new private helpers; one module constant `WORKER_CHILD_ROLE`. | Two call sites and two helpers. No change to argv, stdio loop, parsing, timeout, cancellation, containment, audit, or `RunResult`. Every existing construction without a journal behaves exactly as before. |
| `tools/agent_supervisor/cli.py` | New `containment_precondition()`; `cmd_start` evaluates it, reports it in `payload["containment"]`, and refuses dispatch as the last gate before a spawn (auditing `containment_gate_refused`); `_run_loop` passes `journal=journal` into `ClaudeRunner`. | The gate is one function plus one `elif`; the C2 wiring is one keyword argument. No new flag, env var, config key, or override — there is no way to bypass the gate. |
| `tools/test_agent_supervisor_runner.py` | New `ProductionChildAccountingTests` (6 tests) + `rec` / `probe_process` imports. | — |
| `tools/test_agent_supervisor_start_reentry.py` | New `ContainmentGateTests` (6 tests) + a compact CLI harness. | — |

### Key hunks

`claude_runner.py`, inside `run_unit` (record at spawn, clear only on a verified exit):

```python
        container.adopt(process.pid)
        # M0-T053 (M0-T052 G5 C2): journal the pid the moment it exists AND is
        # contained, before a single byte is written to it. ...
        self._record_launched_worker(process, container)
...
        duration = time.monotonic() - started
        # M0-T053 (M0-T052 G5 C2): the record is cleared only now, and only on a
        # VERIFIED exit - never on the assumption that the finally block above
        # did its job.
        self._settle_worker_record(process)
```

`_settle_worker_record` is the fail-closed half: `if process.poll() is None: return` — the
record is removed only for a pid the OS has actually reaped (`run_unit`'s `finally` always
`wait()`s), which is a stronger fact than a liveness probe a reused pid could fool. An
unwritable journal at record time is a **refusal**: the worker is terminated, its pipes are
closed, and `RunnerError("child_record_unwritable")` is raised rather than running a child
recovery could never account for.

`cli.py`, `cmd_start` (the C1 gate, last gate before a live worker is spawned):

```python
        elif not containment_ok:
            payload["stopped_because"] = f"containment_refused: {containment_detail}"
            audit.append("containment_gate_refused", policy_result="REFUSED",
                         detail={"containment_kind": containment_kind,
                                 "required": CONTAINMENT_JOB_OBJECT, ...})
```

Doctor parity is by construction: `containment_precondition()` reads the same
`process.default_containment_kind()` that `doctor`'s `containment_default` check reads, and
has no config/flag/env input of its own. An exception while determining containment is also
a refusal (`kind: "unknown"`).

**Sole production launch path re-verified from source** (so one gate is enough):
`grep -rn "ClaudeRunner(\|SupervisedLoop(\|_run_loop" tools/agent_supervisor/` →
exactly one `ClaudeRunner(...)` construction (`cli.py:2269`), one `SupervisedLoop(...)`
(`cli.py:2324`), one `_run_loop(...)` call (`cli.py:2466`, inside `cmd_start`).

## Test evidence (all commands run in the worktree above, Python 3.11.9, Windows 11)

```
$ python -m pytest tools/test_agent_supervisor_*.py -q
1493 passed, 2 skipped in 107.60s (0:01:47)

$ python -m pytest tools/test_agent_supervisor_*.py -q      # repeat, determinism
1493 passed, 2 skipped in 106.15s (0:01:46)

$ python -m pytest tools/test_agent_supervisor_*.py -q -k "not ChildAccountingTests and not ContainmentGateTests"
1477 passed, 2 skipped, 15 deselected in 108.47s (0:01:48)
```

The `-k` run also deselects the 4 pre-existing `ChildAccountingTests` in
`test_agent_supervisor_recovery.py`, so the pre-change baseline at `37667ff` is
**1481 passed / 2 skipped** and this change adds **12** tests → **1493 / 2 / 0 failures**.
That re-establishes the `M0-T039-supervisor-freeze.md` baseline (requirement: ≥ 1165 tests,
0 failures) with room to spare. (The M0-T052 report's 1402 is the count at `867b1bf`;
M0-T054/T055 have landed since.)

Focused runs:

```
$ python -m pytest tools/test_agent_supervisor_start_reentry.py -q
16 passed in 1.59s

$ python -m pytest tools/test_agent_supervisor_runner.py -q -k ProductionChildAccountingTests   # x6
6 passed, 62 deselected in 0.73s   (six consecutive runs, all 6 passed)
```

`python tools/test_project_control.py` was **not** run: nothing this task touches is covered
by it (changes are confined to `tools/agent_supervisor/**` and two supervisor test files).

### Lint

`ruff 0.13.0` (the CI-pinned version) is installed locally; no install was needed.

```
$ ruff --version
ruff 0.13.0
$ ruff check tools/agent_supervisor/claude_runner.py tools/agent_supervisor/cli.py \
             tools/test_agent_supervisor_runner.py tools/test_agent_supervisor_start_reentry.py
Found 5 errors.   (F401 x5 — all PRE-EXISTING, see below)
```

The five findings are unused imports on lines this change never touches: `cli.py`
`activation_status`, `NAMED_PIPE_STATUS`, `UNVERIFIED`, `interrupted_turn_resumption`, and
`test_agent_supervisor_runner.py` `import subprocess`. Verified pre-existing:
`git diff -U0 | grep "^+" | grep -E "activation_status|NAMED_PIPE_STATUS|UNVERIFIED|interrupted_turn_resumption|import subprocess"`
returns nothing. CI's only ruff job runs with `working-directory: services/api`
(`.github/workflows/ci.yml:187-211`), so `tools/` has never been ruff-gated. Not fixed:
out of the smallest-durable-set and unauthorized by the qualifying evidence
(supervisor-freeze §1/§3, D-010-R240).

## The required scenarios, and how each is proved non-vacuous

Non-vacuousness was proved by **mutating the guard in production code and observing the
tests fail**, then reverting. Five probes:

| # | Mutation applied to production code | Result |
|---|---|---|
| 1 | `containment_precondition`: `if kind == CONTAINMENT_JOB_OBJECT` → `if kind != "MUTATION-PROBE-M0-T053"` (always permit) | **2 failed**, 4 passed — `test_a_posix_process_group_host_refuses_to_dispatch` (`AssertionError: True is not false` on `dispatched`) and `test_a_windows_taskkill_fallback_host_refuses_to_dispatch` |
| 2 | `run_unit`: delete the `self._record_launched_worker(...)` call | **4 failed**, 7 passed — the clean-unit record test, the surviving-child refusal, the unwritable-journal refusal, and the CLI end-to-end wiring test |
| 3 | `run_unit`: delete the `self._settle_worker_record(...)` call | **3 failed**, 9 passed — the clean-unit clear test, the resume-proceeds test, and the CLI end-to-end test (`AssertionError: 0 != 1 : the verified exit must clear the record`) |
| 4 | `_settle_worker_record`: `if process.poll() is None:` → `if False:` (clear unconditionally) | **1 failed** — `test_a_child_without_a_verified_exit_keeps_the_record` (`AssertionError: 0 != 1 : an unreaped child must stay recorded so the next start refuses`) |
| 5 | `_record_launched_worker`: swallow the write failure instead of raising | **2 failed** — `test_an_unwritable_child_record_refuses_the_unit` (raw `OSError` escapes later instead of the refusal) and the surviving-child test |

All five mutations were reverted; the two clean full-suite runs above are on the reverted
(final) tree.

Two tests were strengthened *because* of probe results rather than left as they were:

- the CLI end-to-end test first asserted only that `launched_child_processes` ended up `[]`
  — probe 2 showed that also passes for a launch path that records nothing and only clears.
  It now spies on `record_launched_child`/`clear_child_record` (delegating to the real
  functions) and asserts a live pid was recorded once and cleared once.
- `test_after_a_clean_unit_the_next_resume_proceeds` did not discriminate under probe 3 (a
  stale *dead* pid does not block a resume anyway), so it now also asserts the record is
  empty.

### Scenario coverage

1. **Surviving recorded child refuses the resume, through the PRODUCTION recording path** —
   `test_a_surviving_recorded_child_makes_the_next_start_refuse`. A launching "supervisor"
   (its own journal connection, own thread) runs the **real** `ClaudeRunner.run_unit`
   against a fake worker that hangs; nothing is recorded by hand. A "restarted" supervisor
   (a second, independent connection to the same journal file) polls until the record
   appears, asserts the pid is genuinely alive via `probe_process`, and runs the real
   `recover_boot` → `UNSAFE_OR_DRIFTED` with that pid in `unaccounted_children`, i.e. the
   exact boolean `cmd_start` gates dispatch on.
2. **Clean exit clears the record and a later resume proceeds** —
   `test_a_clean_unit_records_the_pid_and_then_clears_the_record` (a delegating journal spy
   captures both writes in order: `[{pid, role: claude_worker, ...}]` then `[]`) and
   `test_after_a_clean_unit_the_next_resume_proceeds` (`recover_boot` → `SAFE_CHECKPOINT`,
   `unaccounted_children == ()`).
3. **C1 gate refuses at `cmd_start` on a non-job-object host, permits on a job-object
   host** — `test_a_posix_process_group_host_refuses_to_dispatch` (asserts
   `dispatched is False`, `provider_calls_made == 0`, `containment.ok is False`,
   `containment_refused` and `double-launch` in `stopped_because`, and the
   `containment_gate_refused` audit event), plus the `taskkill` and
   "containment undeterminable" variants, against
   `test_a_job_object_host_permits_the_dispatch` (real dispatch runs, ends at the honest
   `no_valid_checkpoint` stop, no refusal audit event). Both host shapes are simulated by
   patching the gate's single source of truth (`cli.default_containment_kind`), so neither
   branch depends on which OS runs the suite.
4. **Fail-closed extras** — `test_a_child_without_a_verified_exit_keeps_the_record`,
   `test_an_unwritable_child_record_refuses_the_unit`,
   `test_the_gate_reads_the_same_host_source_doctor_reads` (doctor parity),
   `test_a_runner_without_a_journal_keeps_the_previous_behaviour` (no regression for the
   journal-less runners).

One test flake was found and fixed **in the test, not in production**: two connections
performing SQLite's *first* open (schema migration + `PRAGMA journal_mode=WAL`) on the same
brand-new file concurrently intermittently raised `JournalError: unreadable_database:
database is locked` (reproduced 2 of 3 runs). The journal file is now created before either
"process" starts, which is also the faithful shape (a crash resume reads a journal the
crashed run already created). Six consecutive green runs afterwards. This is not a runtime
path: the single-instance lock is what keeps two live supervisors apart.

## What was deliberately NOT changed

- **Nothing was activated.** `default_mode = shadow` and LIMITED-AUTO-off are untouched;
  `limited-auto` is still refused by name before anything is built. This change only ADDS
  refusals — no path is enabled or widened.
- **No second gate inside `_run_loop`.** `_run_loop` has exactly one caller (`cmd_start`,
  re-verified above), so a duplicate check would be unreachable defensive code. The gate
  sits at the operator entry point, which is what C1 asked for.
- **The Codex reviewer child is not accounted for.** `codex_reviewer` spawns through
  `process.run()`, which is a different path; C2 names the *worker* spawn. Out of scope.
- **`probe_model_launch` / `make_launch_probe` are not accounted for.** They construct their
  own `ProcessContainer` and `Popen` (`claude_runner.py:~1360`) for a short-lived
  orchestrator-role availability probe, and hold no journal. Out of scope; see residual R2.
- **Five pre-existing `ruff` F401s and one pre-existing Pyright complaint were left alone.**
  The Pyright item (`model_available`: `make_launch_probe` returns
  `Callable[[str], tuple[bool, str]]`, `SupervisedLoop.__init__` declares
  `Callable[[str], bool] | None`) exists unchanged at `37667ff` —
  `git show 37667ff:tools/agent_supervisor/loop.py | grep -n model_available` → line 905;
  `git diff -U0 | grep model_available` → no matches. The cited line numbers only *moved*
  (cli.py 2277 → 2319, 2302 → 2344) because this change inserted lines above them. There is
  no `# type: ignore` anywhere in this diff. Fixing it would be an unauthorized signature
  change under supervisor-freeze §1/§3 and D-010-R240; the one-line widening is available if
  the orchestrator authorizes a separate defect-lane item.
- No redesign, refactor, drive-by cleanup, or new abstraction; no `project-control/**` edits
  other than this report; no `services/**`, `apps/**`, `packages/**`, `.claude/**`, or
  `C:/SupervisorController/config.toml` edits.

## Residual risk still open (disclosed, not fixed here)

- **R1 — the crash window is narrowed, not eliminated.** A supervisor killed between
  `subprocess.Popen` returning and `record_launched_child` committing (microseconds, two
  statements apart) still leaves an unrecorded orphan. On the pinned job-object host,
  kill-on-close covers it; the two mechanisms are now complementary rather than one being
  inert.
- **R2 — the model launch probe still spawns an unaccounted child.** Orchestrator-role
  sessions only, short-lived, and it never becomes the worker; a kill mid-probe on a
  non-job host could still strand it. Not covered by C1/C2.
- **R3 — journal-less runners keep no accounting.** `journal=None` is still accepted (the
  probe and the stdio unit tests need it). Production is wired at the single construction
  site and a test asserts the wiring end to end, but the runner does not itself refuse to
  run without a journal.
- **R4 — the gate reads the host default, not the achieved per-launch containment.** The G5
  delta attestation asked for *both* the `doctor`-style snapshot **and** the per-cycle
  worker-launch audit line `containment: job_object`, because `ProcessContainer.adopt`
  degrades honestly to `taskkill` if `AssignProcessToJobObject` fails at launch time. This
  task enforces criterion (1) fail-closed at `start`; criterion (2) is still recorded on the
  `claude_process_started` transition (`containment`) and on `RunResult.containment` but is
  **not** enforced as a mid-run stop. Closing that would mean stopping the loop after the
  first cycle whose achieved containment is not `job_object` — a loop-behaviour change
  beyond this packet's "correct nothing else". Recommend it be considered for M0-T056's
  no-duplicate-workers requirement (D-010-R347).
- **R5 — an unwritable journal surfaces as `RunnerError`, which `cmd_start` does not
  catch** (it catches `LoopError`/`IllegalTransitionError`), so it exits as a traceback
  rather than a report. It fails closed (no dispatch continues, and the worker is killed
  first), and a journal that cannot be written is already fatal to every other supervisor
  write, so no new refusal-reporting path was added for it.
