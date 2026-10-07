# M0-T186 convergence record — the sub-agent ledger's `_exclusive()` lock on windows-latest (DB-157)

Method: `/deficit-convergence` (loaded before any edit). DB-157; D-090-R093/R094.
Qualifying evidence (supervisor-freeze §2, AD-093): a reproduced defect — CI run 37519342596,
job 112460379795 (supervisor-bridge, windows-latest).

Claim-seam head (reset target): `9371c1e4d87e332b42cebd369be88ae210ab838d`. Producer worktree:
`/root/project/nyc-buildability/.claude/worktrees/agent-af69907a37976d578`. This host is Linux
(Python 3.12.3); the Windows delete-pending fact is argued from the frozen log + the code and is to
be DEMONSTRATED on windows-latest (S3), never assumed from memory of the Win32 API.

Commits in this worktree (not pushed): A `685ca1f374128a17967e10da46605bd5fb754134` (tests only),
B `aba185655755c14c69e2c6224e337b5f22c16a27` (the repair), C (these two reports).

---

## 1. Frozen evidence (S1) — cited, not paraphrased from memory

Read-only file `project-control/reports/M0-T186-ci-evidence/job-112460379795-windows-failure.txt`
(written by the orchestrator at contract time; unchanged by this producer).

- Run **37519342596** (workflow CI, event `pull_request`, run attempt **1**; nothing was rerun).
- Job **112460379795** — `supervisor-bridge` (`pytest tools/test_agent_supervisor_*.py`),
  **windows-latest** (Python 3.12.10, path `C:\hostedtoolcache\windows\Python\3.12.10`).
- Head **`1cdad2c07e825fff3a3344850466cad7d8accf18`**, branch
  `task/M4-T023-zoning-rule-review-register`, pull request **452** (that change touches no file
  under `tools/`).
- Same head, push run **37519335445**: the same job **passed** (the race is narrow and
  probabilistic).
- Full log **55895 bytes**, sha256 **`5d21679450c65bb9a70775a9cbf12b469bba8e6de7e82c19b3439697f40a52f1`**
  (downloaded 2026-10-06 through the jobs API).

Quoted from the frozen FAILURES section (not paraphrased):

- Failing test: `tools/test_agent_supervisor_mrl_subagent_contract.py::TestLedger::test_parallel_requests_never_exceed_limits`.
- Assertion: `assert (2 == 2 and 5 == 6)` — `results.count(True) == 2` and `results.count(False) == 5`
  (`[True, True, False, False, False, False, ...]`).
- The lost thread's traceback (a `PytestUnhandledThreadExceptionWarning`, "Exception in thread
  Thread-1830 (worker)"):
  `_req(led)` → `ledger.request(**base)` → `with _exclusive(self.path):` (request line 200) →
  contextlib `__enter__` → `_exclusive` line 133
  `fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)` →
  `PermissionError: [Errno 13] Permission denied: 'C:\…\pytest-0\test_parallel_requests_never_e0\l.json.lock'`.
- Suite summary: `1 failed, 3956 passed, 60 skipped in 275.11s`.

Invariants the evidence fixes, which any explanation must satisfy:
1. No request was admitted beyond the limits — exactly **2** admitted against `max_concurrent=2`;
   the ledger's locked accounting held (safety intact).
2. The failure is a hard **unhandled exception** at the O_EXCL create (`PermissionError [Errno 13]`),
   not an under-count and not a `fail closed` refusal — a worker thread died before appending its
   result, so `results` holds 7 of 8 entries (2 True, 5 False).
3. It is rare: the push run on the same head passed the same job; one job in one run shows it.

## 2. Causal path and candidate adjudication (S2)

### 2.1 The path from the eight threads to the one unhandled exception

The test starts 8 threads; each calls `_req(led)` → `SubagentLedger.request(...)`, whose body is
`with _exclusive(self.path): …`. `_exclusive()` (pre-fix) acquires a cross-process lock by
`os.open(lock, O_CREAT|O_EXCL|O_WRONLY)` in a loop that retries **only** on `FileExistsError`
(sleep 0.02 s to the `_LOCK_TIMEOUT_S` deadline, then the module's own fail-closed `_violation`).
On acquire it `os.close(fd)`, yields (reads the ledger, decides, writes it whole), and in its
`finally` releases with `lock.unlink()` under `contextlib.suppress(OSError)`.

With `max_concurrent=2, max_total=5` and **no releases** in the test (workers only request), once two
children are issued and live, every later request is refused by the concurrent limit. So at most 2
can ever be admitted; 8 threads → 2 admitted, 6 refused **expected**. On windows-latest one thread,
while another thread's `lock.unlink()` (its `finally`) was in flight, called `os.open(...O_EXCL...)`
against a **delete-pending** lock file; Windows denied the create with `PermissionError [Errno 13]`
instead of `FileExistsError`. The pre-fix loop catches only `FileExistsError`, so the
`PermissionError` propagated out of `_exclusive` → `request` → `_req` → the worker thread, which
died before appending to `results`. Hence **2 admitted, 5 refused, 1 lost** (7 of 8 results), and the
assertion saw `5 == 6` fail. No over-admission occurred: the crash is on the ACQUIRE, before any
accounting mutation, so the safety invariant (never more than `max_concurrent`/`max_total`) held;
only liveness (one lost worker) broke.

### 2.2 Candidate adjudication

- **(a) the exclusive create meeting a lock file whose removal by another thread is pending
  (Windows reports access denied) — PROVED (the cause).** The frozen traceback shows
  `PermissionError [Errno 13]` raised at exactly `os.open(lock, O_CREAT|O_EXCL|O_WRONLY)` while 8
  threads hammer create/unlink on one `l.json.lock`; the pre-fix loop handles only `FileExistsError`,
  so it escapes. Host-independent mutation proof (§5): with the pre-fix body restored, an injected
  `PermissionError` at that create propagates unhandled and both repair-dependent tests fail. The
  DECIDING PLATFORM FACT — that a delete-pending create raises `PermissionError`, not
  `FileExistsError` — is witnessed by the frozen production traceback and is to be DEMONSTRATED
  deterministically on windows-latest (S3 / §3): the nt-only platform-fact test, and the before/after
  ci-exp and PR-head runs. The sibling `review_slots._SlotLock.acquire` already relies on and (via
  M0-T176/M0-T184) demonstrated the same OS behaviour on windows-latest.
- **(b) another process holding the file open (antivirus, indexer) — RULED OUT as the cause.** The
  lock lives in a per-test `tmp_path` created and destroyed inside the test; the error coincides with
  8 threads racing create/unlink on that one path; there is no external-process signature and the
  mechanism of (a) needs none. (At the OS-error level an external open would surface as the same
  transient create denial, and the repair's bounded retry covers it too — but there is no evidence for
  it and it is not needed to explain the failure.)
- **(c) a fault of the test itself (shared tmp_path, thread start order) — RULED OUT.** `tmp_path` is
  pytest's per-test unique directory (`pytest-0/test_parallel_requests_never_e0`); threads do not
  share it across tests. The exception originates in PRODUCTION code (`_exclusive` line 133), not the
  test; the 2+5+lost count is the CONSEQUENCE of the lost thread, not a test bug. The assertion and
  its limits are correct and are preserved (R094).
- **(d) test timing — RULED OUT.** This is a crash at a syscall, not a timing-sensitive under-count a
  slower/faster runner would shift (contrast DB-150/M0-T184, a genuine `slot_lock_timeout`). Raising a
  timeout cannot help: the thread dies at the create, never reaching the deadline. The same head's
  push run passed only because the race window is narrow; when the `PermissionError` does occur, the
  pre-fix code has no path but to crash the thread.

### 2.3 Classification

**REAL SUPERVISOR DEFECT** in `tools/agent_supervisor/mrl_subagent_contract.py`, `_exclusive()`
acquire loop (candidate (a)). NOT test timing, NOT a test fault. Same family as DB-150 (repaired by
M0-T184, release side) and DB-160 (`locking.SingleInstanceLock.acquire`, same acquire-side pattern,
not yet repaired); this module was not part of either.

## 3. Deciding Windows behaviour, to be demonstrated on windows-latest (S3) — PENDING

The repair rests on one platform fact: on Windows an `O_EXCL` create against a delete-pending lock
file raises `PermissionError` (ERROR_ACCESS_DENIED), not `FileExistsError`. It is witnessed by the
frozen production traceback and is to be DEMONSTRATED deterministically by the orchestrator on
windows-latest:

- The nt-only platform-fact test
  `TestExclusiveWindowsDeletePending::test_windows_delete_pending_create_raises_permission_error_platform_fact`
  (skipped on this Linux host; `os.name != 'nt'`): opens a lock file, unlinks it while a handle is
  still open (delete-pending), and asserts a second `O_EXCL` create raises `PermissionError`.
- Before the repair, on a `ci-exp/M0-T186-*` branch pushed by the orchestrator from commit A
  `685ca1f3` (tests only): `test_transient_windows_permission_error_waits_then_succeeds` and
  `test_persistent_windows_permission_error_times_out_fail_closed` RED, the platform-fact test
  PASSED, `test_parallel_requests_never_exceed_limits` may still flake RED (the live defect).
  `[ORCHESTRATOR TO SUPPLY: ci-exp branch name, run id, job id, runner image, full-log bytes + sha256,
  the failing/passing test names and the suite summary.]`
- After the repair, on the pull-request head (commits A+B+C): the supervisor-bridge job green in both
  runs, with the two repair-dependent tests GREEN on Windows and
  `test_parallel_requests_never_exceed_limits` green.
  `[ORCHESTRATOR TO SUPPLY: PR head sha, both run ids and job ids, full-log bytes + sha256, the
  supervisor-bridge suite summary (expect ≥ 1165 tests, 0 failures — the freeze baseline).]`

## 4. The one bounded repair (S4)

`_exclusive()` acquire loop only (the release `finally` and every other function are unchanged); a
named `_is_windows()` seam (`os.name == 'nt'`) is added so either branch runs deterministically on
either host without patching the global `os.name`.

- The `O_EXCL` create loop now also catches `PermissionError`. On Windows it is treated as the same
  transient "busy" as `FileExistsError`: waited out with the loop's own `time.sleep(0.02)` to the
  lock's own deadline (`time.monotonic() + _LOCK_TIMEOUT_S`), and — if it never clears — ended in the
  module's own fail-closed refusal (`_violation("…held past … refusing (fail closed)")`, the same kind
  as a held lock past the timeout). Bounded; never an unbounded loop; never swallowed into an
  admission.
- On POSIX a `PermissionError` at the `O_EXCL` create is a genuine permission fault and stays loud —
  re-raised at once (`if not _is_windows(): raise`), unchanged.
- An OSError that is NOT the transient `PermissionError` (e.g. EIO) is caught by neither branch and
  reaches the caller at once on both platforms — never waited out.
- The `FileExistsError` path is behaviour-identical to before (wait to the deadline, then the same
  `_violation`); the diff restructures it only to share the deadline/sleep tail with the new branch.

Diff: `tools/agent_supervisor/mrl_subagent_contract.py` **37 insertions, 4 deletions** (the 4 are the
pre-fix one-line docstring and the inline deadline/sleep in the old `FileExistsError` branch). File is
**478 lines** (< 600 warn threshold); nothing extracted; public interface (`SubagentLedger.request`
and its `ContractError` refusal) unchanged.

## 5. Tests and mutation proof (S5)

New class `TestExclusiveWindowsDeletePending` in
`tools/test_agent_supervisor_mrl_subagent_contract.py` (additions only, 124 insertions, 0 deletions),
plus the `_failing_lock_open` helper (injects the Windows error for `.lock` creates on any host) and
the `errno`/`os` imports:

| Scenario | Test | Host | commit A | final head |
|---|---|---|---|---|
| S5(i) transient create fails 2× then succeeds; request served, limits intact | `test_transient_windows_permission_error_waits_then_succeeds` | any | RED | GREEN |
| S5(ii) never-clears → bounded, module's typed `fail closed` refusal, no admission | `test_persistent_windows_permission_error_times_out_fail_closed` | any | RED | GREEN |
| S5(iii) a non-PermissionError OSError (EIO) stays loud, not swallowed | `test_non_permission_oserror_at_create_stays_loud` | any | GREEN | GREEN |
| S5(iii) a PermissionError on POSIX stays loud (real fault) | `test_permission_error_on_posix_stays_loud` | any | GREEN | GREEN |
| S5(iv) Windows platform fact: delete-pending `O_EXCL` create raises `PermissionError` | `test_windows_delete_pending_create_raises_permission_error_platform_fact` | nt only | SKIP (non-nt) | SKIP (non-nt) / GREEN on nt |

**Mutation proof (host-independent).** With the repair reverted to the literal pre-fix body
(`git checkout 9371c1e4 -- tools/agent_supervisor/mrl_subagent_contract.py`; the `except
PermissionError` branch and `_is_windows()` absent, confirmed by grep), the two repair-dependent
tests FAIL:

```
/root/project/lanes-runtime/venv/bin/python -m pytest -p no:cacheprovider \
  "…::TestExclusiveWindowsDeletePending::test_transient_windows_permission_error_waits_then_succeeds" \
  "…::TestExclusiveWindowsDeletePending::test_persistent_windows_permission_error_times_out_fail_closed"
… PermissionError: [Errno 13] delete pending   (raised at _exclusive line 133; request line 200)
2 failed in 0.53s      (direct exit code 1)
```

The failing mechanism: the injected `PermissionError` reaches the caller unhandled at the O_EXCL
create. In (i) the line `decision = _req(ledger)` raises before `assert decision.allowed is True` is
reached; in (ii) the raw `PermissionError` propagates instead of the expected `ContractError('…fail
closed')`, so `pytest.raises(ContractError, match="fail closed")` does not match it. The source was
then restored from HEAD (`git checkout HEAD -- …`), working tree verified clean; the mutation was
never committed.

## 6. No weakening (S6 / R094)

- `test_parallel_requests_never_exceed_limits` is UNCHANGED — keeps `results.count(True) == 2 and
  results.count(False) == 6`, the 8 threads, and `max_concurrent=2, max_total=5`. Its fix comes from
  the production repair, not from touching the test.
- Test-file diff is additions only (124 insertions, 0 deletions; `git diff 9371c1e4..HEAD --
  <testfile>` shows no deletion lines). No test deleted, renamed, xfail-marked or loosened.
- The only new skip is the Windows-only platform-fact test, skipped off-Windows with a stated reason
  (`@pytest.mark.skipif(os.name != 'nt', …)` — the pytest form of `skipUnless(os.name == 'nt')`),
  authorized by R094.
- The retry added is INSIDE the production `_exclusive()` acquire loop (the real lock wait), bounded
  by the lock's own deadline — not a retry/rerun of a test, no rerun/flaky plugin, no `.github/**`
  change, no pytest-config change, no timeout raised to hide the failure (`_LOCK_TIMEOUT_S` is
  unchanged at 5.0; the never-clears test monkeypatches it to 0.2 only within its own scope).

## 7. Siblings (S8) — REPORTED, NOT CHANGED

Allowed path is `mrl_subagent_contract.py` only; every other supervisor file is untouched.

- `tools/agent_supervisor/review_slots.py` `_SlotLock.acquire` (lines ~314–330): ALREADY treats the
  Windows delete-pending `PermissionError` as busy (the `_is_windows()` seam, wait-to-deadline, then
  `slot_lock_timeout`), from M0-T176 and reinforced by M0-T184. Not exposed; no change needed — this
  repair brings `_exclusive` to parity with it.
- `tools/agent_supervisor/locking.py` `SingleInstanceLock.acquire` (line 261): catches ONLY
  `FileExistsError` at its `O_EXCL` create — the SAME acquire-side pattern as the pre-fix `_exclusive`
  (DB-160). Same latent Windows delete-pending exposure, but far lower: one holder per supervisor run
  and few contenders, not 8 threads hammering create/unlink on one path. No failure seen.

DB-152 and DB-153 weighed again:

- **DB-152** — `locking.py SingleInstanceLock.release()` (lines 307–310) issues ONE
  `self.path.unlink()` inside `except OSError: return False`, the same one-shot swallow M0-T184
  repaired in `review_slots._SlotLock.release()`. The mrl module's OWN release path (`lock.unlink()`
  inside `contextlib.suppress(OSError)`, `_exclusive` `finally`) is the same family. Neither was part
  of the OBSERVED failure, which is purely the acquire-side unhandled exception (a crash at the
  create, not a stranded lock); repairing a release path here would widen beyond the proven causal
  cluster. **Recommendation:** repair DB-152 and the mrl release swallow only with a reproduced
  failure or a failed acceptance scenario — the supervisor freeze bars a speculative change; or add
  the bounded-retry release when that lock is next touched under qualifying evidence.
- **DB-153** — a payload-write failure AFTER the `O_EXCL` create leaves an empty/partial lock on disk
  in the two **payload-writing** acquires (`review_slots._SlotLock.acquire`,
  `SingleInstanceLock.acquire`). `_exclusive()` writes NO lock payload (it only creates and closes an
  empty marker), so it has no DB-153 partial-write exposure. **Recommendation:** unchanged from
  M0-T184 — an operator runbook note, or the next defect task that touches those two acquires.

**Recertification cost:** this change alters the `tools/agent_supervisor/` tree hash, so it
re-establishes the `M0-T039-supervisor-freeze.md` suite baseline (≥ 1165 tests, 0 failures) under the
standard gates. A recorded cost authorized by D-090-R093, not a bar; the supervisor stays
SHADOW-ONLY (no R595 change).

## 8. Verification (S7) and status (S9)

Linux local (host Python `/root/project/lanes-runtime/venv/bin/python`, 3.12.3),
`PYTHONDONTWRITEBYTECODE=1`, direct exit codes:

| Check | When | Exit | Result |
|---|---|---|---|
| `pytest -q -p no:cacheprovider tools/test_agent_supervisor_mrl_subagent_contract.py` | claim head (baseline) | 0 | 45 passed |
| same, at commit A `685ca1f3` (tests only) | commit A | 1 | 2 failed (the two repair-dependent S5 tests), 47 passed, 1 skipped |
| same, at the repaired head (B/C) | final head | 0 | 49 passed, 1 skipped (the nt-only platform-fact test) |
| `ruff check` on both files | final head | 0 | All checks passed |
| `tools/supervisor_command_doc_check.py` | final head | 0 | 11 commands checked; 0 failures |
| `tools/modularity_check.py --check` | final head | 0 | pass; `mrl_subagent_contract.py` 478 lines (< 600); printed warnings are pre-existing for other modules, not this file |
| mutation proof (pre-fix restored) | §5 | 1 | 2 failed (both repair-dependent tests) |
| `git diff --stat 9371c1e4..HEAD` | final head | — | only the two allowed code files (test 124/0; source 37/4) |

The whole `tools/test_agent_supervisor_*.py` glob is NOT run on this Linux server (it runs only in the
windows-latest supervisor-bridge CI job). A green Linux run alone proves little; the proof is the
MECHANISM (§2) + the host-independent mutation proof + the before/after Windows demonstration (§3,
pending the orchestrator's runs).

**STATUS: PENDING WINDOWS DEMONSTRATION.** On Linux the cause is named and classified (real supervisor
defect in `_exclusive()`'s acquire loop — an `O_EXCL` create against a delete-pending lock file raises
`PermissionError`, caught by neither branch pre-fix), the repair is in place and bounded, the mutation
proof shows it is load-bearing, and no test is weakened (R094). This record CLOSES to VERIFIED_CLOSED
only after §3's placeholders are filled by the orchestrator: the ci-exp run showing the two
repair-dependent tests RED on windows-latest at commit A with the platform-fact test PASSED, and the
PR-head runs showing the supervisor-bridge job green with those tests GREEN on Windows. No blocker;
the only open item is the Windows evidence, which the producer cannot run here (no Windows host).
