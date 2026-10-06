# M0-T184 convergence record — review-slot `slot_lock_timeout` on windows-latest

Method: `/deficit-convergence` (loaded before editing). DB-150; D-090-R093/R094/R337/R338/R339.
Qualifying evidence (supervisor-freeze §2): a failed acceptance scenario — the RACE scenario of
M0-T171 failed on CI in jobs 112160344138, 112164492630 and 112181006630.

Claim-seam head: `06480e1216c0e79b8a4647819efc2052aea137e7`. Producer worktree:
`/root/project/nyc-buildability/.claude/worktrees/agent-abb590b9f18c9a516`. This host is Linux
(Python 3.12.3); the Windows file-sharing fact is argued from the frozen logs + the code and
DEMONSTRATED on windows-latest (S3).

---

## 1. Frozen evidence (S1) — cited, not paraphrased from memory

Three read-only excerpts under `project-control/reports/M0-T184-ci-evidence/` (written by the
orchestrator at contract time; unchanged by this producer). Each is the FAILURES section through
the summary line, with the runner image, head sha, branch, full-log byte count and sha256, and the
two timestamped progress lines bounding the review-slots file.

| Job | Run / attempt / event | Head / branch | Runner | Log bytes / sha256 | Failing test | Suite summary | Review-slots file span |
|---|---|---|---|---|---|---|---|
| 112160344138 | 37430612001 / a1 / pull_request | `486ebe8c…` / task/owner-working-guidance-in-claude-md-2026-10-06 | Microsoft Windows Server 2025 | 52669 / `ed65f6f1…09733` | `test_global_last_slot_never_double_taken` | 1 failed, 3951 passed, 60 skipped in 364.47 s | 07:40:49 → 07:41:51 (~62 s) |
| 112164492630 | 37431907048 / a1 / push | `789f87ce…` / candidate/D-024-mrl-option-b | Microsoft Windows Server 2025 | 51690 / `ad9f375f…c0a71` | `test_global_last_slot_never_double_taken` | 1 failed, 3951 passed, 60 skipped in 355.10 s | 07:52:42 → 07:53:44 (~62 s) |
| 112181006630 | 37436954274 / a1 / push | `4b6a4d8c…` / candidate/D-024-mrl-option-b | Microsoft Windows Server 2025 | 50911 / `d72583fb…1ec86` | `test_per_lane_last_slot_never_double_taken` | 1 failed, 3951 passed, 60 skipped in 497.21 s | 08:41:23 → 08:42:25 (~62 s) |

Racers' reason-code lists, quoted verbatim from the frozen FAILURES sections:

- Job 112160344138 (global, 6 racers / 2 global slots):
  `['refused:slot_lock_timeout', 'refused:slot_lock_timeout', 'refused:slot_lock_timeout', 'admitted', 'admitted', 'refused:slot_lock_timeout']` — 2 admitted, 4 `slot_lock_timeout`.
- Job 112164492630 (global, 6 racers / 2 global slots):
  `['refused:slot_lock_timeout', 'admitted', 'refused:slot_lock_timeout', 'refused:slot_lock_timeout', 'refused:slot_lock_timeout', 'admitted']` — 2 admitted, 4 `slot_lock_timeout`.
- Job 112181006630 (per-lane, 6 racers / one shared lane / lane limit 1):
  `['refused:slot_lock_timeout', 'refused:slot_lock_timeout', 'admitted', 'refused:slot_lock_timeout', 'refused:slot_lock_timeout', 'refused:slot_lock_timeout']` — 1 admitted, 5 `slot_lock_timeout`.

Orchestrator-confirmed facts carried in the G0 report: no other CI run was in progress during the
third failure; the second attempts of both integration runs passed with 3952 passed (jobs
112168039083 and 112184899084). One manual rerun of each integration run passed (3952 passed).

Three invariants the evidence fixes, which any explanation must satisfy:
1. No run shows a last slot taken twice — the slot primitive's safety held (no over-admission).
2. Every non-admitted racer answered `refused:slot_lock_timeout`, never `barrier_timeout` and never
   `refused:concurrency_limit_reached`. The reason code is emitted ONLY by `_SlotLock` when the
   O_EXCL acquire loop runs to its 30 s deadline inside `try_reserve` — so each losing racer DID
   reach `try_reserve` and waited the full lock timeout.
3. The lock stayed unavailable for ~30 s AFTER the admitted racers had written their reservations
   and left their critical sections (the review-slots file still finished in ~62 s).

## 2. Causal path and candidate adjudication (S2)

### 2.1 The code path from racer spawn to `refused:slot_lock_timeout`

`_RACE_WORKER` spawns six real interpreters behind a file barrier (M0-T181). Each writes
`ready_<idx>`, spins until `go`, then calls `slots.try_reserve(lane)` with `lock_timeout_s=30.0`;
a winner emits `admitted` and HOLDS its reservation (not the lock) for up to 30 s or until
`release` appears. `try_reserve` wraps its body in `with self._lock()`:

- `__enter__` → `_SlotLock.acquire()`: `os.open(O_CREAT|O_EXCL|O_WRONLY)`; on `FileExistsError` it
  takes over only a readable, provably dead/reused holder (`_holder_is_stale()` + `_take_over()`),
  otherwise `_wait_or_fail_closed(deadline)` sleeps one poll and, past the deadline, raises
  `SlotError("slot_lock_timeout", …)`.
- body: `_read_live()` → `admit_review_or_combine(...)` → if admitted, `_write([*live, reservation])`.
- `__exit__` → `_SlotLock.release()`.

The lock file is acquired and released once per `try_reserve`. The reservation lives in a SEPARATE
state file, so while an admitted racer holds its reservation the LOCK file is free for the others to
acquire, read the state (reservation counted), and legitimately refuse `concurrency_limit_reached`.

### 2.2 The release defect (pre-repair body)

```
def release(self) -> None:
    holder = self._read_holder()
    if holder is None or holder.get("lock_id") != self._lock_id:
        return  # never remove another process's lock
    with contextlib.suppress(OSError):
        self.path.unlink()
```

Two swallow paths leave the lock file on disk:
- **(a) the single swallowed `unlink`.** `_read_holder()` opens the lock file the way
  `pathlib.Path.read_text` opens it (text-read handle). On Windows CPython opens a file for reading
  WITHOUT `FILE_SHARE_DELETE`, so while a concurrent racer's `_read_holder` (called every poll inside
  that racer's own `acquire` wait) has the lock file open, the holder's `unlink` raises
  `PermissionError` (ERROR_ACCESS_DENIED) rather than marking the file delete-pending. The single
  `contextlib.suppress(OSError)` swallows it and returns. The lock file stays on disk carrying the
  admitted racer's `lock_id`; that racer is ALIVE (holding its reservation up to 30 s).
- **(b) the skipped unlink on a transient `None` read.** If `release`'s own `_read_holder` returns
  `None` transiently while the file is present, the guard returns WITHOUT unlinking — the same stuck
  file, by a different path.

Consequence for every other racer: `acquire` → `FileExistsError` → `_holder_is_stale()` reads a
holder whose pid is the LIVE admitted racer with a matching start token → `probe.alive` True, not
reused → NOT stale → `_wait_or_fail_closed`. The file never clears (nobody retries the lost unlink),
so each waiter polls to its 30 s deadline and raises `slot_lock_timeout`, which `try_reserve` maps
through `_fail_closed` to `refused:slot_lock_timeout`. This reproduces every frozen observation: the
first racers to pass the lock are admitted (global: 2; per-lane: 1); once one admitted racer's
release loses its unlink to a concurrent read, the file is stranded and the remaining racers all
time out; no slot is ever taken twice (safety holds; only liveness breaks).

### 2.3 Candidate adjudication

- **(a) release's swallowed `unlink` leaving a live-owned lock file — PROVED (primary cause).** It is
  the only mechanism consistent with ALL three logs simultaneously: some racers admitted, the rest
  `slot_lock_timeout` (not `concurrency_limit_reached`, not `barrier_timeout`), no double-take, and a
  lock that stays unavailable ~30 s AFTER the critical sections ended. Deciding platform fact: an
  open reader handle (opened as `_read_holder` opens it) blocks `unlink` with `PermissionError` and
  leaves the file on disk — DEMONSTRATED on windows-latest (S3 / §3). Reproduced host-independently
  by `test_release_retries_transient_removal_failure_then_succeeds` (RED on the pre-repair body — see
  the mutation proof in the producer report).
- **(b) release's own `_read_holder` returning `None` → skipped unlink — PLAUSIBLE SECONDARY,
  addressed.** It leaves the identical stuck file, so the logs cannot distinguish it from (a); it is a
  genuine second swallow path in the same body. The repair closes both (it waits out a transient
  unreadable-but-present read instead of skipping the unlink). Not separately needed to explain the
  failure; fixed by the same bounded change.
- **(c) a critical section that really exceeds 30 s — RULED OUT.** The 30 s is the LOCK WAIT, not the
  critical section. The count-check-reserve is sub-second; the admitted racers wrote their
  reservations (safety held), and the whole review-slots file finished in ~62 s — not a single
  30 s+ critical section. `slot_lock_timeout` is raised by the acquire WAIT, not by a slow body.
- **(d) a failed stale takeover or a wrong liveness answer — RULED OUT.** A wrong "dead" verdict on a
  live holder would let two racers take over and BOTH reserve → a slot taken twice. No run shows
  that. `_holder_is_stale` correctly reports the live admitted racer as NOT stale (that is why nobody
  takes the file over); the defect is that the file should not be there at all. Liveness was correct.
- **(e) test-harness timing (barrier / parent window) — RULED OUT.** M0-T181 already removed the
  barrier/parent-window decoupling: `_RACE_BARRIER_WAIT_S` (90 s) strictly exceeds the parent's 60 s
  readiness window, and a barrier abandonment now emits `barrier_timeout`. The frozen reason code is
  `slot_lock_timeout`, emitted only by the LOCK acquire deadline INSIDE `try_reserve` — proving every
  losing racer called `try_reserve` and waited on the lock. This is the decisive discriminator
  between a harness barrier fault and a code-level lock fault: the reason code says lock, not
  barrier.

### 2.4 Classification

**REAL SUPERVISOR DEFECT** in `tools/agent_supervisor/review_slots.py`, `_SlotLock.release()`
(candidate (a) primary, (b) secondary). NOT test timing.

### 2.5 Reconciliation with the two earlier records

- **M0-T176 producer report §4 item 4 ("release's unlink — already correct, no change") — DOES NOT
  STAND.** Item 4 enumerated two worlds. World A (readers share delete → `unlink` succeeds →
  delete-pending → file vanishes when the short read closes) is the world its §2 acquire fix targets.
  World B (readers do NOT share delete → `unlink` raises `PermissionError` → suppressed → "the file
  stays our own lock") it dismissed as benign because, in World B, an O_EXCL create on the still-
  present file raises `FileExistsError`, not `PermissionError`, so the §1 acquire defect would not
  arise. That reasoning was correct as far as it went but INCOMPLETE: it never followed World B's
  stuck-lock to its own consequence — a lock file left on disk owned by a LIVE holder makes every
  other contender time out. The M0-T184 evidence shows World B is the live world (the file stays and
  waiters time out for ~30 s; under World A the file would vanish in microseconds and no 30 s timeout
  would occur). So item 4's conclusion is overturned: the release path DID need a change. (Item 4's
  narrower claim — that release never removes or forges another holder's lock — still holds and is
  preserved by the repair.)
- **M0-T181 convergence record, Failure A (classified TEST-HARNESS TIMING) — STILL STANDS.** Failure
  A was a DIFFERENT symptom: `AssertionError: 1 != 2`, an under-count caused by an early racer
  abandoning the barrier on an independent 30 s go-deadline shorter than the parent's 60 s readiness
  window, miscounted as a refusal. That was a real harness-timing bug and was correctly fixed in the
  test file. M0-T184 is a DISTINCT failure mode (`slot_lock_timeout`, not an under-count). M0-T181's
  own instrumentation — the reason codes it added, and its note that "a lock timeout would now be a
  loud fault, not a silent loser" — is exactly what surfaced this defect loudly. So Failure A's
  classification is not contradicted; its instrumentation worked as designed and exposed a separate,
  code-level cause that M0-T184 now fixes.

## 3. Deciding Windows behaviour, demonstrated on windows-latest (S3)

The classification rests on one platform fact: on Windows, deleting a file that another handle —
opened the way `_read_holder` opens it — still holds open raises `PermissionError` and leaves the
file on disk. It is demonstrated directly, never assumed from memory of the Win32 API, by two
nt-only tests pushed on the ci-exp branch BEFORE the repair:

- `ReleaseLockRemovalTests::test_windows_open_reader_blocks_unlink_platform_fact` — asserts the raw
  platform fact (open reader handle ⇒ `unlink` raises `PermissionError` ⇒ file still present).
- `ReleaseLockRemovalTests::test_windows_release_removes_lock_despite_concurrent_reader` — the
  end-to-end real-handle case: RED before the repair (the single swallowed unlink leaves the lock
  file on disk), GREEN after it.

Windows evidence to be supplied by the orchestrator:
- ci-exp branch `ci-exp/M0-T184-*` run id: **TO BE SUPPLIED BY THE ORCHESTRATOR** (expected at
  commit A: `test_release_retries_transient_removal_failure_then_succeeds` RED and
  `test_windows_release_removes_lock_despite_concurrent_reader` RED;
  `test_windows_open_reader_blocks_unlink_platform_fact` GREEN — the OS fact proven).
- supervisor-bridge (windows-latest) job id + run id on the PR head after the repair: **TO BE
  SUPPLIED BY THE ORCHESTRATOR** (expected: whole `tools/test_agent_supervisor_*.py` suite green,
  ≥ 1165 tests, 0 failures; the two RaceTests pass; the three new ReleaseLockRemovalTests that run on
  nt all green).

## 4. The one bounded repair (S4)

`_SlotLock.release()` only (one method; `acquire`, `_read_holder`, `_take_over`, the state-file
paths, and all three `with self._lock()` call sites are unchanged):

- The removal is RETRIED to the lock's own deadline (`time.monotonic() + self.timeout_s`, polling
  `self.poll_s`) — the colliding reader's handle is short-lived, so a retry within a poll or two
  removes the file. Bounded, derived from the lock's own timeout/poll; never an unbounded loop.
- The file is removed ONLY once `_read_holder` confirms it carries OUR `lock_id`; a holder with a
  different `lock_id` is returned-on untouched (never removed or forged).
- A transient unreadable-but-present read is waited out and re-read (closing candidate (b)) rather
  than mistaken for "not ours" and skipped.
- A removal that cannot complete within the bound leaves the file in place (fail closed — no
  contender over-admits on a guess) and records a typed `SlotError("slot_lock_release_failed", …)`
  on `self.release_error` AND logs it at ERROR — observable, never silently swallowed.
- `release()` never raises, so an already-written ADMITTED reservation is never turned into a refusal
  by a late lock-release problem, and a legitimate `concurrency_limit_reached` refusal keeps its
  reason code. `try_reserve` / `release` / `active` return exactly what they returned before in every
  non-failing case.

Tests pinning the mechanism (positive / negative / mutation): §5 of the producer report.

## 5. Siblings and recertification (S8) — REPORTED, NOT CHANGED

Out of this packet's scope (allowed path is `review_slots.py` only); reported for a follow-up:
- `tools/agent_supervisor/locking.py` `SingleInstanceLock.release()` (lines ~300–312) has the SAME
  one-shot swallow: `self.path.unlink()` inside `try/except OSError: return False`. A Windows reader
  racing its unlink would leave the single-instance lock on disk. Exposure is far lower than
  review-slots (it is held once per supervisor run, not contended by six racers hammering reads every
  poll), but it is the same latent pattern.
- The acquire path in BOTH modules (`_SlotLock.acquire`, `SingleInstanceLock.acquire`) leaves a
  just-created lock file on disk if the payload write (`os.fdopen(...).write/flush/fsync`) raises
  after the O_EXCL create succeeds: the file is then read as unreadable (`None`) by others → wait,
  never steal → time out. A partial-write failure is rare, but the exposure is a stuck empty lock.
- Recertification consequence: this change alters the `tools/agent_supervisor/` tree hash, so it
  re-establishes the `M0-T039-supervisor-freeze.md` suite baseline (≥ 1165 tests, 0 failures) under
  the standard gates and carries the D-091 recertification follow-up (M0-T181 already recorded
  M0-T179 as superseded). A recorded cost authorized by D-090-R093, not a bar; the supervisor stays
  SHADOW-ONLY (no R595 change).

## 6. Verification and closing (S7 / S9)

Linux local (host Python `/root/project/lanes-runtime/venv/bin/python`, 3.12.3), direct exit codes
and counts — full table in the producer report:
- `pytest -q -p no:cacheprovider tools/test_agent_supervisor_review_slots.py` at the final head:
  exit 0 — 20 passed, 2 skipped (the two nt-only tests), 2 subtests passed.
- `tools/supervisor_command_doc_check.py`: exit 0 (11 commands checked, 0 failures).
- `tools/modularity_check.py --check`: exit 0 (`review_slots.py` 578 lines, under the 600 warning
  threshold; the warnings printed are pre-existing for other supervisor modules).
- `ruff check` on both files: exit 0.
- Mutation proof: with the literal pre-repair release body restored,
  `test_release_retries_transient_removal_failure_then_succeeds` fails
  (`AssertionError: True is not false`) — command and output in the producer report.
- `git diff --stat 06480e12..HEAD`: only `tools/agent_supervisor/review_slots.py` and
  `tools/test_agent_supervisor_review_slots.py` (plus these two report files in commit C).

The whole supervisor suite is NOT run on this Linux server (ci.yml records that the whole glob
starved an ubuntu runner on 2026-08-03; M0-T181 ran focused files only). One green run proves
nothing by itself — §2 argues the mechanism and the host-independent + mutation tests prove the
fix is load-bearing.

**STATUS: PENDING WINDOWS EVIDENCE — not yet VERIFIED_CLOSED.** The cause is named and classified
(real supervisor defect in `_SlotLock.release()`), the fix is bounded and verified on Linux with a
mutation proof, and the deciding platform fact is encoded in two nt-only tests. This record becomes
**VERIFIED_CLOSED** when the orchestrator fills in the §3 ci-exp run id (new tests RED/GREEN as
stated before the repair) and the windows-latest supervisor-bridge run id + counts on the repaired
PR head (whole suite green, ≥ 1165 tests, 0 failures, both RaceTests passing). No step is
unprovable; nothing is blocked — the only open item is orchestrator-captured Windows CI evidence.
