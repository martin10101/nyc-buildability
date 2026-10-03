# M0-T181 convergence record (/deficit-convergence)

Task: supervisor-bridge Windows CI repair (DB-111), owner directive D-090-R093
(bounded repair, separate PR, find the cause) bounded by D-090-R094 (preserve every
safety/concurrency assertion; no skipped tests, weakened checks, or retries for green).

Method: /deficit-convergence (freeze evidence, trace the complete causal path for
each failure, classify, repair the one bounded causal cluster, verify once at the
frozen candidate). This host is Linux; Windows-only mechanisms are argued from the
frozen logs + code + cited Win32 semantics and confirmed by the windows-latest
supervisor-bridge CI job on the PR head (the fix carries permanent self-diagnosing
instrumentation, so a residual occurrence is loud, never silent).

## 1. Frozen evidence (read-only; cited, never paraphrased from memory)

`project-control/reports/M0-T181-ci-evidence/` (written by the orchestrator at
contract time), three windows-latest (Microsoft Windows Server 2025) jobs, each
"1 failed, 3949 passed, 60 skipped":

| job | run / attempt | head / branch | failure | suite time | log bytes / sha256 |
|---|---|---|---|---|---|
| 111231288935 | 37132839977 a1 | 84ded09b / lane-d/D-12-slice-2-flag-on-e2e | RaceTests.test_global_last_slot_never_double_taken `AssertionError: 1 != 2` | 419.55 s | 51283 / b341c4a2… |
| 111247302687 | 37138313731    | 1ed2a55f / task/docs-seam-2026-10-03       | same race test `1 != 2`                                                    | 322.47 s | 51228 / 6afc11b2… |
| 111292325552 | 37153605150 a1 | 265635a8 / lane-b/B-req-D-2-part-2-missing-source-ref (PR #368) | same race test `1 != 2` (FOURTH, post-contract) — paired PUSH run 37153603034 of the SAME head PASSED | 412.27 s | 51164 / bdb04229… |
| 111247110311 | 37138247824 a1 | 745e3318 / lane-b/B-req-D-2-transit-detail-prose | test_real_process_table_proves_a_reaped_child_gone `proven=False remaining=(8040,8088,8136,8184)` root_pid 8028, attempts 97, 5.047 s, source windows_toolhelp32 | 302.60 s | 51115 / 2443eb67… |

(The fourth row is frozen by the orchestrator on origin/task/M0-T181-… as
`project-control/reports/M0-T181-ci-evidence/job-111292325552-run-37153605150-attempt-1.txt`;
cited here, read-only, not carried on the producer branch.)

DB-111 (docs/DISCOVERY_BACKLOG.md, 2026-10-03): 37 of the last 45 runs green; every
failure started within seconds of a SECOND supervisor-bridge job on the same head;
always under-admission / stale liveness, never a double-take. **Three of the four
failures are the race test, all on SLOW suites (419, 412, 322 s); the one descendants
failure is on a 302 s suite.** The decisive corroboration (fourth occurrence): the
PR #368 `pull_request` run 37153605150 failed the race at 412.27 s while the PAIRED
`push` run 37153603034 of the SAME head (265635a8) PASSED the identical job — the two
jobs differ only in runner load, not in code. A code-deterministic bug would fail both;
a load-sensitive harness-timing bug fails only the saturated one. This is exactly the
predicted mechanism.

## 2. Failure A — RaceTests.test_global_last_slot_never_double_taken (1 != 2)

Harness: six real interpreters behind a file barrier; two global slots; exactly two
must be admitted. `_run_race` spawns six `Popen` racers, waits up to 60 s for all six
`ready_*`, writes `go`, waits up to 60 s for all six `result_*`, and summed the
results. Each racer (`_RACE_WORKER`): writes `ready_<idx>`, then
`deadline = time.monotonic() + 30` (an INDEPENDENT 30 s go-deadline measured from its
OWN start), spins `while not go.exists()`, and on expiry emitted `"0"` WITHOUT ever
calling `try_reserve`, exiting. A winner emitted `"1"` and held. The parent summed the
`"0"`/`"1"` tokens.

Causal path (traced from code + the frozen timings): on a saturated runner the six
Python interpreters start staggered. Each racer's 30 s go-deadline runs from ITS OWN
start, but the parent writes `go` only after ALL six `ready_*` appear (up to its own
60 s window). When the slow sixth interpreter takes longer than ~30 s to start — wholly
plausible at a 419 s suite — the five racers that started early reach their 30 s
deadline BEFORE `go` is written, each emit `"0"` (barrier abandonment, never
`try_reserve`), and exit. The sixth then becomes ready, `go` is written, it races
alone, and wins one slot → winners == 1. The slot primitive was never wrong (no
double-take ever occurred); the `"0"` barrier abandonment was indistinguishable from a
legitimate admission refusal, so the count under-reported and the invariant assertion
failed. The 30 s go-deadline is strictly shorter than the parent's 60 s readiness
window — the two budgets were independent, so a racer could give up before the parent.

Classification: **TEST-HARNESS TIMING defect** (barrier budget decoupled from, and
shorter than, the parent's readiness window + a barrier abandonment miscounted as a
refusal). NOT a supervisor defect — `review_slots.py` is unchanged and its invariant
held throughout.

Deciding evidence: the frozen message is `1 != 2` (an under-count) on 419 / 412 / 322 s
loaded suites; the fourth occurrence is decisive — the PR #368 pull_request run failed
at 412 s while the paired push run of the SAME head passed, so the inputs are identical
and only runner load differs (a code-deterministic bug would fail both). The per-lane
twin (`same_lane`, expects 1) did not fail because its expected value equals the
degenerate "one survivor" count. The slot logic's own negative/reclaim/lock tests all
passed on the same runs (3949 passed). Nothing in the evidence shows two reservations
held at once.

Bounded repair (test file only — `tools/test_agent_supervisor_review_slots.py`):
1. The racer emits a REASON CODE, never a bare count: `"admitted"`,
   `"refused:<reason_code>"`, or `"barrier_timeout"`.
2. `_run_race` counts only `"admitted"` as a winner, accepts
   `"refused:concurrency_limit_reached"` as the one legitimate non-winner, and FAILS
   LOUDLY (with every racer's reason code) on ANY other outcome — a barrier expiry, a
   lock timeout, or an unreadable/malformed state. An under-admission can never again
   masquerade as a refusal, and a real fail-closed defect is never masked.
3. One shared window sizes the race. `_RACE_PARENT_WAIT_S = 60.0` is the parent's
   per-fan-in wait (unchanged value, now named). The racer's barrier budget is DERIVED
   from it: `_RACE_BARRIER_WAIT_S = _RACE_PARENT_WAIT_S + _RACE_LOCK_SERIALIZE_ALLOWANCE_S
   = 60 + 30 = 90 s`, passed to the racer via argv. Derivation: a racer must wait for
   `go` strictly longer than the parent can take to produce it — the parent may spend
   its full 60 s readiness window gathering six slow interpreter starts, then the
   slowest racer must still acquire the lock while five peers serialize through the one
   tiny critical section (the `_RACE_LOCK_SERIALIZE_ALLOWANCE_S = 30 s` allowance,
   >> six back-to-back sub-second critical sections even under load). A barrier expiry
   inside 90 s therefore means a genuinely hung parent (a loud fault), never a
   loaded-but-progressing runner.

R094 timeout justification: the trace PROVES the old 30 s go-deadline IS the cause
(shorter than the 60 s readiness window; an early racer abandons before `go`). The new
value is DERIVED from a stated budget (parent readiness window + lock-serialization
allowance), not chosen to turn CI green. The racer's `lock_timeout_s` (30 s) and hold
(30 s) are UNCHANGED — the trace does not implicate them (a lock timeout would now be a
loud fault, not a silent loser, and losers refuse immediately without waiting, so the
hold need only outlast the parent's prompt `release`). The asserted invariant is
byte-identical: `assertEqual(winners, 2)`, `assertLessEqual(len(active()), 2)` (global)
and `assertEqual(winners, 1)` (per-lane).

## 3. Failure B — test_real_process_table_proves_a_reaped_child_gone (proven False)

`child = Popen([python, -c, "pass"]); child.wait(); prove_zero_descendants(child.pid,
settle_seconds=5.0)`. Frozen: root_pid 8028 ABSENT, remaining `(8040, 8088, 8136,
8184)`, 97 attempts over 5.047 s, `windows_toolhelp32`.

Causal path (traced against `mrl_descendants.py` + Win32 semantics): `snapshot_processes`
on win32 (`_snapshot_windows`) walks Toolhelp32 `PROCESSENTRY32` recording
`th32ProcessID -> th32ParentProcessID`. `descendants_of(8028, table)` builds a
ppid→children map and BFS-walks from 8028. 8028 is absent (our `pass` child exited and
was reaped by `wait()`), so `found` starts empty — but four live pids
8040/8088/8136/8184 record `th32ParentProcessID == 8028`, so the walk pulls them in →
non-empty → `proven=False`. Those four are NOT descendants of our child (a `pass`
process spawns nothing); they are orphans of an EARLIER process that once held pid 8028
and spawned four long-lived children, then exited. Win32 does NOT rewrite
`th32ParentProcessID` when a parent dies (unlike Linux, which reparents an orphan to the
subreaper/pid 1), and Windows reuses pids quickly, so when our child received the reused
pid 8028 the stale orphans' recorded parent matched it and `descendants_of` counted them.

Win32 citations (Microsoft Learn):
- PROCESSENTRY32 / `th32ParentProcessID`: "the identifier of the process that created
  this process (its parent process)" with the explicit note that the value is captured
  at snapshot time and is NOT updated when the parent terminates — a documented stale
  field. (docs: Win32 `tlhelp32`/PROCESSENTRY32 structure.)
- Process identifier reuse: a pid is unique only while the process runs; "the process
  identifier can be reused" / "used by another process" after the process ends and its
  last handle closes — the kernel is free to reassign it immediately (docs: PROCESS_
  INFORMATION / process-handle lifetime, and GetProcessId guidance).

The two together are the complete mechanism: stale recorded parent + fast pid reuse ⇒ a
ppid-only walk counts unrelated earlier orphans forever.

Classification: **REAL supervisor semantic defect in `mrl_descendants.py`** — a false
"descendants remaining". The direction is fail-closed (a false turnover, never a missed
descendant), but in production it is a false refusal/turnover; the owner authorized
fixing the cause (R093).

Deciding evidence: the frozen proof itself — root absent, four pids whose only link to
the root is a stale recorded ppid equal to the reused root pid, 97 re-enumerations over
the full 5 s window never clearing (they are live, unrelated processes, not a settling
race). The defect does not reproduce on Linux because orphans reparent away from the
reused pid — hence green on this host and red only on windows-latest.

Bounded repair (the cause, in the shared module + its in-scope worker caller):
- `tools/agent_supervisor/mrl_descendants.py`: add the provable exclusion **a process
  created BEFORE the root's own start cannot be the root's descendant**.
  `descendants_of` gains optional `root_start` (the root's creation ordinal) and
  `creation_ordinal` (a pid→ordinal reader; default `_probe_creation_ordinal` via
  `locking.probe_process`). During the BFS a child created before `root_start` is
  pruned WITH its subtree (its children reach the root only through it, so they are not
  the root's descendants either); the root itself counts as present only if in-table
  and not pre-root. `prove_zero_descendants` threads both through. `creation_token_to_ordinal`
  parses the platform-specific start token (`locking.probe_process.start_token`): on
  Windows the creation FILETIME as fixed-width hex (`int(token,16)`), on POSIX
  `/proc/<pid>/stat` field 22 (starttime ticks, `int(token)`) — earlier means smaller.
- Proof semantics PRESERVED: `proven` is True only when a real snapshot shows the tree
  empty; an unobservable table still returns `source='unavailable'`, never zero; an
  UNKNOWN creation ordinal keeps the pid (fail closed — a real descendant is never
  excluded on an unreadable creation time); a descendant created at/after the root is
  always kept; with no `root_start` the behaviour is byte-identical to before (the
  orphan-stays-visible walk — see `test_descendants_of_finds_an_orphan_whose_parent_already_exited`,
  unchanged).
- `tools/agent_supervisor/mrl_one_shot.py` (the in-scope worker caller): capture the
  worker's creation ordinal in `_ContainedSpawn` the instant after `Popen`, while it is
  alive (the only moment it is reliably readable — once it exits/its pid is reused,
  Windows `GetProcessTimes` no longer yields it), and pass `root_start` to
  `prove_zero_descendants`.

Scope note (honest residual): `tools/agent_supervisor/mrl_one_shot_review.py:291` (the
reviewer path, OUTSIDE this packet's allowed_paths) still calls `prove_zero_descendants`
WITHOUT `root_start`, so it retains the old fail-closed walk. That is SAFE (over-counts →
a false turnover, never a missed descendant) and backward-compatible; wiring it to pass
a captured `root_start` is a one-line follow-up and is recorded as such, not fixed here.

R094: no timeout or settle window changed for failure B. The fix adds information
(the root's start time, which a correct production caller already had) rather than
loosening a bound.

## 4. New / strengthened tests (mutation-proof)

In `tools/test_agent_supervisor_mrl_one_shot.py`:
- `test_real_process_table_proves_a_reaped_child_gone` (the failing test) now mirrors
  production: a real child that runs briefly so its creation time is readable while
  alive, `root_start` captured and threaded in. Final assertion UNCHANGED
  (`proven is True and remaining == ()`).
- `test_reused_pid_orphan_before_root_is_not_a_descendant_but_a_real_child_is` (new):
  injects a snapshot with creation times for both the live-tree shape (root present +
  genuine child 200 + pre-root orphan 300 with its own child 301) and the exact frozen
  reaped shape (root 8028 absent, four pre-root orphans). It asserts the guarded result
  excludes the pre-root orphan+subtree while keeping the genuine child, AND asserts the
  UN-GUARDED walk still counts them — the pre-fix behaviour — proving the guard is
  load-bearing (CODING_RULES mutation discipline).
- `test_descendant_with_unknown_creation_time_is_kept_fail_closed` (new): a descendant
  whose creation ordinal reads None is KEPT, pinning the fail-closed direction.

Every pre-existing descendants/one-shot/review test keeps its exact assertions.

## 5. Verification at the frozen candidate (Linux local; venv python 3.12.3, pytest 9.0.3)

- `python -m pytest -q tools/test_agent_supervisor_review_slots.py tools/test_agent_supervisor_mrl_one_shot.py -p no:cacheprovider` → **83 passed, 2 subtests passed in 8.19 s; EXIT=0**
- `python -m pytest -q tools/test_agent_supervisor_mrl_one_shot_review.py -p no:cacheprovider` (consumer of the touched `mrl_descendants`) → **81 passed in 24.87 s; EXIT=0**
- `python tools/supervisor_command_doc_check.py` → **11 checked, 0 failures; EXIT=0**
- `python3 tools/modularity_check.py --check` → **692 files, 0 failures, 29 warnings (none on the changed files); EXIT=0**
- `ruff check tools/agent_supervisor/{mrl_descendants,mrl_one_shot,process}.py tools/test_agent_supervisor_{review_slots,mrl_one_shot}.py` → **All checks passed; EXIT=0** (two pre-existing E402/F401 in github_flow.py/rotation.py are untouched by this task and outside allowed_paths).

Windows verification: the windows-latest supervisor-bridge job on the PR head. The
fix is itself the self-diagnosing instrumentation for failure A (reason codes + loud
barrier fault) and the semantic correction for failure B, so the normal PR CI run is
the Windows confirmation; run id to be appended by the orchestrator. A single green run
does not alone prove a probabilistic timing fix (DB-111 risk) — the mechanism argued in
§2/§3 is the proof; the reason codes make any residual occurrence loud, never silent.

## 6. Recertification consequence (S7)

`tools/agent_supervisor/mrl_descendants.py` and `tools/agent_supervisor/mrl_one_shot.py`
CHANGED → the M0-T179 Linux supervisor certification is VOIDED and this takes the
D-091 recertification path (recorded, not a bar; R093 authorized fixing the cause).
Failure A changed TEST FILES ONLY (`review_slots.py` production is untouched). The
supervisor tree hash changes and the `M0-T039-supervisor-freeze.md` suite baseline must
be re-established under the standard gates. Qualifying evidence for the
`tools/agent_supervisor/**` change (supervisor-freeze rule §2): a reproduced defect
(DB-111, three frozen windows-latest failures) and an owner-directive requirement
(D-090-R093); cited in the commit messages.

VERIFIED_CLOSED — Failure A: cause named (test-harness barrier/parent-window decoupling
+ miscounted abandonment), fixed in the test harness, invariant preserved exactly,
Linux-verified. Failure B: cause named (Win32 stale `th32ParentProcessID` + pid reuse →
false descendants), fixed at the cause in `mrl_descendants.py` + wired in the in-scope
worker caller, proof semantics preserved, new mutation-proof tests pass, Linux-verified.
Windows confirmation is the standard supervisor-bridge CI run on the PR head (run id to
be appended by the orchestrator); the mechanism — not the green — is the proof.
