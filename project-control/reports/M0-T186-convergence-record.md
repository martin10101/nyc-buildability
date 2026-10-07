# M0-T186 convergence record — the sub-agent ledger's `_exclusive()` lock on windows-latest (DB-157)

Method: `/deficit-convergence` (loaded before any edit). DB-157; D-090-R093/R094.
Qualifying evidence (supervisor-freeze §2, AD-093): a reproduced defect — CI run 37519342596,
job 112460379795 (supervisor-bridge, windows-latest).

Claim-seam head: `9371c1e4d87e332b42cebd369be88ae210ab838d`. Producer worktree:
`/root/project/nyc-buildability/.claude/worktrees/agent-af69907a37976d578`. This host is Linux
(Python 3.12.3). The Windows behaviour is now DEMONSTRATED on windows-latest by a designed probe
(round 2), not assumed from memory of the Win32 API; this round writes only what the frozen files
show.

Commit lineage (not pushed). Round 1: A (tests) `685ca1f3`, B (repair) `aba18565`, C (reports)
`24aeb949`, cherry-picked onto the task branch as `d3eba6ca` / `7ee6299a` / `6d5899ce`. Round 2:
P (Windows probe) `e3b5417f` — experiment branch only, NEVER merged. Round 3 (this round):
D (the wrong platform test replaced by a real-race test + these reports), and X (experiment only,
NEVER merged — the acquire loop restored to its pre-fix code, the real-platform mutation proof).

---

## 1. Frozen evidence (S1) — cited, not paraphrased from memory

Read-only files under `project-control/reports/M0-T186-ci-evidence/`.

**The original failure — `job-112460379795-windows-failure.txt`:**
- Run **37519342596** (CI, event `pull_request`, attempt **1**; nothing rerun). Job
  **112460379795** — `supervisor-bridge`, **windows-latest** (Python 3.12.10). Head
  `1cdad2c07e825fff3a3344850466cad7d8accf18`, branch `task/M4-T023-zoning-rule-review-register`,
  PR **452** (touches no file under `tools/`). Same head, push run **37519335445**: the job
  **passed** (the race is narrow). Full log **55895 bytes**, sha256
  `5d21679450c65bb9a70775a9cbf12b469bba8e6de7e82c19b3439697f40a52f1`.
- Failing test `TestLedger::test_parallel_requests_never_exceed_limits`; assertion
  `assert (2 == 2 and 5 == 6)`. The lost worker thread's traceback ends at `_exclusive` line 133
  `fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)` →
  `PermissionError: [Errno 13] Permission denied: '…\l.json.lock'`. Summary:
  `1 failed, 3956 passed, 60 skipped in 275.11s`.

Invariants the evidence fixes: (1) exactly **2** admitted against `max_concurrent=2` — no
over-admission, the ledger's locked accounting held; (2) the failure is a hard **unhandled
exception** at the O_EXCL create (`PermissionError [Errno 13]`), so a worker died before appending
its result (7 of 8 results: 2 True, 5 False); (3) it is rare (the same head's push run passed).

**The Windows runs of this change (round 2, quoted in §3 and §8):** commit A alone
(`job-112576500175-run-37554194212-attempt-1-ci-exp-red.txt`); A+B+C
(`jobs-112576591960-112576606545-head-6d5899ce-failed.txt`); the probe P1–P5
(`job-112580543291-run-37555462888-attempt-1-ci-exp-probe.txt`).

## 2. Causal path and candidate adjudication (S2)

### 2.1 The path from the eight threads to the one unhandled exception

8 threads each call `_req(led)` → `SubagentLedger.request(...)` → `with _exclusive(self.path): …`.
`_exclusive()` (pre-fix) acquires by `os.open(lock, O_CREAT|O_EXCL|O_WRONLY)` in a loop that retries
**only** on `FileExistsError`; it `os.close(fd)`, yields, and in its `finally` releases with
`lock.unlink()` under `contextlib.suppress(OSError)`. With `max_concurrent=2, max_total=5` and **no
releases** in the test, at most 2 are ever admitted; 8 threads → 2 admitted, 6 refused expected. On
windows-latest, while one thread's `lock.unlink()` raced another thread's `os.open(...O_EXCL...)`,
the create raised `PermissionError [Errno 13]` (not `FileExistsError`). The pre-fix loop catches only
`FileExistsError`, so the `PermissionError` propagated out and killed one worker → **2 admitted, 5
refused, 1 lost**. No over-admission: the crash is on the ACQUIRE, before any accounting mutation.

### 2.2 Candidate adjudication (rewritten to the probe evidence)

- **(a) the exclusive create meeting a lock file whose removal by another thread is pending (Windows
  reports access denied) — the RACE is PROVED; the kernel reason is NOT ESTABLISHED.** Probe P4 (the
  real 8-thread create/close/unlink race, raw `os` calls, no external process and no third handle)
  shows the O_EXCL create raises `PermissionError(errno=13, winerror=None)` — deciding frozen line:
  `P4 real race (8 threads, 61758 iterations, 20.0s elapsed …): {'create:FileExistsError': 39093,
  'create:PermissionError(errno=13, winerror=None)': 1468, 'create:ok': 21197, 'unlink:ok': 21197}`.
  So the concurrent create/unlink race ALONE reproduces the exact production error (errno-13
  PermissionError at the create), with no external process. The specific kernel reason ("removal is
  pending" / ERROR_ACCESS_DENIED) is NOT ESTABLISHED: `os.open` reports **no winerror** (P4
  `winerror=None`), and neither deliberate delete-pending construction reproduces it — a held
  **share-delete** handle makes the create SUCCEED and the file vanish at once (`P2 … unlink=ok;
  path_exists_after_unlink=False; O_EXCL_create_while_handle_open=ok(created)`), and a held **plain**
  handle makes the UNLINK fail and the create give FileExistsError (`P3 … unlink=PermissionError
  (errno=13, winerror=32); … O_EXCL_create_while_handle_open=FileExistsError(errno=17,
  winerror=None)`).
- **(b) another process holding the file open (antivirus, indexer) — RULED OUT as a necessary
  cause.** P4 reproduces the create's `PermissionError` with no external process and no held handle at
  all, in an isolated `tmp_path` (frozen P4 line above), so an external process is **not needed** to
  explain the failure. What P2/P3 CANNOT exclude: that some external handle also contributed in the
  original 2026-10-06 job — they only show the race alone suffices and that a deliberately held
  handle does **not** reproduce the create's `PermissionError` (P2 create succeeds; P3 create gives
  FileExistsError). So (b) is unnecessary, not positively excluded for all time.
- **(c) a fault of the test itself (shared tmp_path, thread start order) — RULED OUT.** P4 reproduces
  the create `PermissionError` through raw `os` calls in an isolated per-test `tmp_path` (`…
  /test_p4_real_race_raw_os_calls0`), independent of the ledger test; the original production
  traceback is in `_exclusive` line 133. The 2+5+lost count is the consequence of the lost thread.
- **(d) test timing — RULED OUT.** P4 shows the create `PermissionError` is a real OS outcome of the
  race (1,468 genuine occurrences), not a test-timing threshold; a worker dies at the create
  regardless of any timeout (contrast DB-150/M0-T184, a genuine `slot_lock_timeout`).

### 2.3 Classification

**REAL SUPERVISOR DEFECT** in `tools/agent_supervisor/mrl_subagent_contract.py`, `_exclusive()`
acquire loop: on windows-latest a concurrent create/unlink race on one lock path makes the O_EXCL
create raise `PermissionError` errno 13, which the pre-fix loop (`FileExistsError`-only) did not
catch, so it reached the caller and killed a worker thread (demonstrated by P4). The exact Win32
reason is unproven, but the repair does not depend on it — it catches the transient `PermissionError`
on Windows and retries, which probe P5 shows holds under the real race. NOT test timing, NOT a test
fault. Same family as DB-150 (M0-T184, release side) and DB-160
(`locking.SingleInstanceLock.acquire`, same acquire-side pattern, not yet repaired).

**Round-1 statements WITHDRAWN (they did not stand):**
1. "`os.open` shares delete on Windows" and the round-1 platform-fact test that rested on it —
   FALSE. On windows-latest the `os.unlink` of a file a plain `os.open` handle still held raised
   `PermissionError [WinError 32]` at the UNLINK (`test_windows_delete_pending_create_raises…` line
   281, frozen jobs 112576591960 / 112576606545 and the probe), so that test never reached its create
   and demonstrated nothing about the create. P3 confirms the plain-handle unlink is winerror 32, and
   P2 shows an explicit share-delete handle makes the file vanish at once (no delete-pending on this
   NTFS), not a lingering pending delete.
2. Candidate (a) marked "PROVED" as a *delete-pending* mechanism — withdrawn. The RACE is proven
   (P4); the delete-pending kernel reason is NOT established.
3. Candidate (b) marked "RULED OUT" (fully excluded) — corrected to "ruled out as a necessary cause":
   unnecessary to explain the failure, not provably never-occurred.

## 3. What the probe DEMONSTRATED on windows-latest, and what it did not (S3)

Probe run (ci-exp/M0-T186-probe, head `e3b5417f` = commit P, NEVER merged): run **37555462888**
(attempt 1, push), job **112580543291**, windows-latest (Windows Server 2025, image
windows-2025-vs2026). Full log **72219 bytes**, sha256
`1010705af297f7bf36235713d2bce260d2344f8bad7b9bfc23d68c864e1ae6db`. Each probe ends in `pytest.fail`
on purpose, so its observation prints; summary `6 failed, 3961 passed, 60 skipped in 339.00s`.

DEMONSTRATED (quoted):
- **Environment (P1):** `getwindowsversion=(10, 0, 26100, 2, ''); platform=
  Windows-2025Server-10.0.26100-SP0; python=3.12.10; tmp_volume_root='C:\\'; tmp_filesystem='NTFS'`.
- **The real race alone raises the create `PermissionError` (P4):** `{'create:FileExistsError':
  39093, 'create:PermissionError(errno=13, winerror=None)': 1468, 'create:ok': 21197, 'unlink:ok':
  21197}` over 61,758 iterations, 8 threads, 20.0 s, no external process, no held handle — and no
  unlink error at all.
- **The repaired `_exclusive()` holds under that exact race (P5):** `max_concurrent_inside=1 (expect
  1); {'acquired': 32673}` over 32,673 iterations, 15.1 s — no refusal, no escaped exception, never
  more than one thread inside the section.

NOT DEMONSTRATED:
- **The kernel reason for the errno-13 refusal.** `os.open` gives no `winerror` (P4
  `winerror=None`), so whether it is ERROR_ACCESS_DENIED (a pending delete) or another transient is
  unknown. The two deliberate delete-pending constructions do NOT reproduce it: a share-delete handle
  (P2) lets the create succeed and the file disappear at once; a plain handle (P3) makes the UNLINK
  fail (winerror 32) and the create give FileExistsError. The create's `PermissionError` arises only
  from the genuine timing race, and its exact Win32 cause is left open.

## 4. The one bounded repair (S4) — KEPT (the evidence supports it)

`_exclusive()` acquire loop only (the release `finally` and every other function unchanged); a named
`_is_windows()` seam is added so either branch runs deterministically on either host. The O_EXCL
create loop now also catches `PermissionError`: on Windows it is treated as the same transient "busy"
as `FileExistsError` (waited out with `time.sleep(0.02)` to `_LOCK_TIMEOUT_S`, then the module's own
fail-closed `_violation` if it never clears); on POSIX it is re-raised at once (`if not _is_windows():
raise`). A non-`PermissionError` OSError (e.g. EIO) is caught by neither branch and stays loud.

The probe validates the behaviour directly: under the real Windows race P5 shows the repaired lock
acquired 32,673 times with **no escaped exception** and **no over-admission** (max one thread inside),
so the transient create `PermissionError` is correctly waited out and retried. The repair's
correctness therefore rests on catching the transient `PermissionError` (P5), NOT on the exact kernel
reason. The module's own docstrings and inline comment in `_exclusive()` / `_is_windows()` were
corrected (commit E, wording only) to say exactly this — the race raises the create `PermissionError`
(errno 13), the kernel reason is not established, and it is treated as transient "busy" — no longer
naming "delete-pending (ERROR_ACCESS_DENIED)" as fact. Diff of the repair (round 1, unchanged):
`mrl_subagent_contract.py` **37 insertions, 4 deletions**; file **478 lines** (< 600); public
interface unchanged.

## 5. Tests and mutation proof (S5) — rewritten to the final test set

Corrected class `TestExclusiveWindowsRace` in `tools/test_agent_supervisor_mrl_subagent_contract.py`.
The wrong platform-fact test is REMOVED; one real-race test is added in its place.

| Test | Host | What it pins | commit D final head |
|---|---|---|---|
| `test_transient_windows_permission_error_waits_then_succeeds` | any (seam-injected) | a transient create PermissionError on Windows is waited out → served, limits intact | GREEN |
| `test_persistent_windows_permission_error_times_out_fail_closed` | any (seam-injected) | a never-clearing one → bounded, module's typed `fail closed` refusal, no admission | GREEN |
| `test_non_permission_oserror_at_create_stays_loud` | any | a non-PermissionError OSError (EIO) stays loud, not swallowed | GREEN |
| `test_permission_error_on_posix_stays_loud` | any | a PermissionError on POSIX stays loud (real fault) | GREEN |
| `test_real_race_through_exclusive_holds_mutual_exclusion` | **every host** | the REAL 8-thread race through `_exclusive()`: nothing but the typed refusal escapes, and never >1 thread inside the section | GREEN |

**Mutation proof — two layers.**
- *Host-independent (Linux), the seam-injected branch tests:* round 1 showed that reverting
  `_exclusive()` to its pre-fix body makes `test_transient_…` and `test_persistent_…` FAIL
  (`PermissionError [Errno 13]` escapes at `_exclusive` line 133; exit code 1, 2 failed). The new
  real-race test stays GREEN on Linux (POSIX raises `FileExistsError`, already handled) — which is
  exactly why the real-platform mutation below is required.
- *Real platform (Windows):*
  - **Commit A alone** (ci-exp/M0-T186-red, head `685ca1f3`, run **37554194212**, job
    **112576500175**, full log 60574 bytes sha256
    `7031741736ceefd101700bd541cc8baf5a8e20fa2f5b57d64f9c4e71ff334408`): with the tests present and
    the repair absent, `test_transient_…` and `test_persistent_…` are RED on Windows —
    `PermissionError: [Errno 13] delete pending` escaping at `_exclusive` line 133 (frozen FAILURES);
    `3 failed, 3959 passed, 60 skipped` (the third failure is the wrong platform-fact test, WinError
    32 at its unlink). This is the pre-fix code letting the create's PermissionError escape, shown on
    the real platform.
  - **Commit X** (this round, experiment only, NEVER merged): the acquire loop restored to the
    literal pre-fix code (the body at `9371c1e4`), nothing else. On Windows this must turn the new
    `test_real_race_through_exclusive_holds_mutual_exclusion` RED (a `PermissionError` escapes through
    `_exclusive`) while it is GREEN with the repair (P5) — the real-platform mutation proof for the
    race test, which cannot be shown on Linux. `[ORCHESTRATOR TO SUPPLY: commit X run id, job id,
    and the race-test RED result.]`

## 6. No weakening (S6 / R094)

- Every test that existed at the claim head stays **byte-identical**: `git diff 9371c1e4..HEAD --
  <testfile>` is additions only (no pre-existing line removed or changed). `TestLedger::
  test_parallel_requests_never_exceed_limits` keeps `results.count(True) == 2 and
  results.count(False) == 6`, its 8 threads and `max_concurrent=2, max_total=5`.
- No skip remains anywhere in this test file: the removed platform-fact test was the only
  `skipUnless`/`skipif`; the replacement real-race test runs on EVERY host. No test is deleted that
  belonged to the claim head, renamed from the claim head, xfail-marked or loosened.
- The retry is INSIDE the production `_exclusive()` acquire loop (the real lock wait), bounded by
  `_LOCK_TIMEOUT_S` — not a test retry/rerun, no rerun/flaky plugin, no `.github/**` change, no
  pytest-config change, no timeout widened to hide the failure (`_LOCK_TIMEOUT_S` stays 5.0; the
  never-clears branch test monkeypatches 0.2 only within its own scope).

## 7. Siblings (S8) — REPORTED, NOT CHANGED

Allowed path is `mrl_subagent_contract.py` only; every other supervisor file is untouched.

- `review_slots.py` `_SlotLock.acquire` (~L314–330): ALREADY catches a Windows `PermissionError` at
  the O_EXCL create and treats it as busy (the `_is_windows()` seam, wait-to-deadline, then
  `slot_lock_timeout`), from M0-T176/M0-T184. Not exposed; this repair brings `_exclusive` to parity.
  (Its own comment still names "delete-pending (ERROR_ACCESS_DENIED)"; the behaviour is right but the
  named reason is unproven — a sibling wording item, out of this task's allowed path of
  `mrl_subagent_contract.py` only.)
- `locking.py` `SingleInstanceLock.acquire` (L261): catches ONLY `FileExistsError` at its O_EXCL
  create — the SAME acquire-side pattern as the pre-fix `_exclusive` (DB-160). Latent Windows
  race exposure, far lower: one holder per supervisor run, few contenders, not 8 threads hammering
  create/unlink on one path. No failure seen.
- **DB-152** — `locking.py SingleInstanceLock.release()` (L307–310) one-shot `self.path.unlink()`
  inside `except OSError: return False`; the mrl `_exclusive` `finally` (`lock.unlink()` under
  `contextlib.suppress(OSError)`) is the same family. Neither was part of the OBSERVED failure (an
  acquire-side crash, not a stranded lock); repairing a release path would widen beyond the proven
  cluster. Repair only under a reproduced failure (supervisor freeze).
- **DB-153** — a payload-write-after-create stranded lock applies to the two **payload-writing**
  acquires; `_exclusive()` writes no payload, so it has no such exposure. Unchanged from M0-T184.

**Recertification cost:** this change alters the `tools/agent_supervisor/` tree hash → re-establish
the `M0-T039-supervisor-freeze.md` baseline (≥ 1165 tests, 0 failures) under the standard gates. A
recorded cost (D-090-R093); the supervisor stays SHADOW-ONLY (no R595 change).

## 8. Verification (S7) and status (S9)

Linux local (`/root/project/lanes-runtime/venv/bin/python`, 3.12.3), `PYTHONDONTWRITEBYTECODE=1`,
direct exit codes, at commit D:

| Check | Exit | Result |
|---|---|---|
| `pytest -q -p no:cacheprovider tools/test_agent_supervisor_mrl_subagent_contract.py` | 0 | 50 passed (the new real-race test ~2.0 s; no skips) |
| `ruff check` on both files | 0 | All checks passed |
| `tools/supervisor_command_doc_check.py` | 0 | 11 commands checked; 0 failures |
| `tools/modularity_check.py --check` | 0 | pass; `mrl_subagent_contract.py` 478 lines (< 600); warnings pre-existing for other modules |
| `git diff 9371c1e4..HEAD -- <testfile>` | — | additions only (no pre-existing test line removed/changed) |

Windows CI captured (orchestrator):
| Head | Run / job | Result |
|---|---|---|
| commit A alone `685ca1f3` (ci-exp/red) | 37554194212 / 112576500175 | the two branch tests RED (PermissionError errno 13 escapes); 3 failed, 3959 passed, 60 skipped |
| A+B+C `6d5899ce` | 37554223543 / 112576591960 (push) and 37554228069 / 112576606545 (pr) | the four injected tests GREEN; only the wrong platform-fact test failed (WinError 32 at unlink); 1 failed, 3961 passed, 60 skipped each |
| probe P `e3b5417f` (ci-exp/probe) | 37555462888 / 112580543291 | P1–P5 observations (§3); 6 failed (each is an intentional `pytest.fail`), 3961 passed, 60 skipped |

**STATUS: NOT VERIFIED_CLOSED yet.** What is established: the cause is a real supervisor defect in
`_exclusive()`'s acquire loop (the concurrent create/unlink race makes the O_EXCL create raise
`PermissionError` errno 13, uncaught pre-fix — P4); the exact kernel reason is not established (§3);
the repair is correct under the real race (P5) and the pre-fix code is red on the real platform (A
alone). CLOSING CONDITION — the record closes VERIFIED_CLOSED only when BOTH hold:
1. commit D's final-head windows-latest supervisor-bridge job is GREEN in both runs (the wrong
   platform-fact test removed; `test_real_race_through_exclusive_holds_mutual_exclusion` and the four
   injected branch tests GREEN), and
2. the commit-X experiment run shows the race test RED on Windows against the pre-fix acquire loop
   (§5, the real-platform mutation).

`[ORCHESTRATOR TO SUPPLY: final-head runs]` — the run ids, job ids, full-log bytes + sha256 and the
supervisor-bridge suite summary (expect ≥ 1165 tests, 0 failures) for commit D's windows-latest runs,
and the commit-X experiment result. No blocker; the only open item is these Windows runs (the
producer cannot run Windows here). The module-comment wording is now corrected (commit E, §4); the one
remaining wording note is the review_slots.py sibling comment (§7), outside this task's allowed path.
