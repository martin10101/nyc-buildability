# Producer report — M0-T184

Review-slot race tests on windows-latest: the `slot_lock_timeout` failures in both `RaceTests`.
DB-150; D-090-R093/R094/R337/R338/R339. Method: `/deficit-convergence`. Qualifying evidence
(supervisor-freeze §2): a failed acceptance scenario — the M0-T171 RACE scenario failed on CI in
jobs 112160344138, 112164492630 and 112181006630.

- Producer: backend-engineer, isolated worktree
  `/root/project/nyc-buildability/.claude/worktrees/agent-abb590b9f18c9a516`.
- Claim-seam head (reset target): `06480e1216c0e79b8a4647819efc2052aea137e7`.
- The convergence record (`M0-T184-convergence-record.md`) carries the frozen evidence, the full
  causal trace, the candidate adjudication, the reconciliation with M0-T176 §4 item 4 and M0-T181
  Failure A, and the pending-Windows closing. This report is the verification and no-weakening
  evidence.

## 1. Files changed (producer scope, all within allowed_paths)

- `tools/agent_supervisor/review_slots.py` — the repair (one method, `_SlotLock.release()`), a
  module `logger`, the `logging` import, and a `release_error` attribute on `_SlotLock`.
  `git diff --numstat 06480e12..HEAD`: **60 insertions, 5 deletions**; the 5 deletions are exactly
  the pre-repair `release()` body. No other production code changed.
- `tools/test_agent_supervisor_review_slots.py` — a new `ReleaseLockRemovalTests` class (5 tests + 2
  helpers). `git diff --numstat`: **167 insertions, 0 deletions** — no existing test touched.
- `project-control/reports/M0-T184-convergence-record.md`, `…-producer-report.md` — this commit C.

Three commits:
- A `a83d63bb` — new tests only, no repair (the three defect-pinning tests).
- B `d116940f` — the bounded release repair + the two negative tests.
- C — these two reports (replacing the placeholders).

## 2. Check commands — DIRECT exit codes and counts

Python = `/root/project/lanes-runtime/venv/bin/python` (3.12.3). The whole supervisor glob is NOT
run on this Linux server (S7; ci.yml 2026-08-03 ubuntu starvation). Commands run one at a time.

| Check | When | Exit | Result |
|---|---|---|---|
| `pytest -q -p no:cacheprovider tools/test_agent_supervisor_review_slots.py` | baseline (claim-seam head) | 0 | 17 passed, 2 subtests passed |
| same, at commit **A** (tests only) | commit A | 1 | 1 failed (`test_release_retries_transient_removal_failure_then_succeeds`), 17 passed, 2 skipped, 2 subtests — the host-independent new test is RED on the current release code; the two nt-only tests skip on Linux |
| same, at the **final head** (repair in) | final head | 0 | 20 passed, 2 skipped, 2 subtests passed |
| `ruff check tools/agent_supervisor/review_slots.py tools/test_agent_supervisor_review_slots.py` | final head | 0 | All checks passed |
| `tools/supervisor_command_doc_check.py` | final head | 0 | 11 presented supervisor command(s) checked; 0 failure(s) |
| `tools/modularity_check.py --check` | final head | 0 | pass; `review_slots.py` 578 lines (< 600 warn); printed warnings are pre-existing for codex_reviewer / durable_state / evidence / gate_wave / next_task, not this file |
| `git diff --stat 06480e12..HEAD` | final head | — | only the two allowed code files (+ the two report files in commit C) |

## 3. Mutation proof (S5 iv) — the fix is load-bearing

With the repaired `release()` temporarily reverted to the LITERAL pre-repair body
(`holder = self._read_holder(); if holder is None or holder.get("lock_id") != self._lock_id: return;
with contextlib.suppress(OSError): self.path.unlink()`), the transient test fails:

Command:
```
/root/project/lanes-runtime/venv/bin/python -m pytest -q -p no:cacheprovider \
  "tools/test_agent_supervisor_review_slots.py::ReleaseLockRemovalTests::test_release_retries_transient_removal_failure_then_succeeds"
```
Output (tail):
```
>       self.assertFalse(lock.path.exists())  # removed after the transient failures
E       AssertionError: True is not false

tools/test_agent_supervisor_review_slots.py:533: AssertionError
=========================== short test summary info ============================
FAILED tools/test_agent_supervisor_review_slots.py::ReleaseLockRemovalTests::test_release_retries_transient_removal_failure_then_succeeds
1 failed in 0.28s
```
Direct exit code: **1**. The single swallowed `unlink` leaves the lock file on disk, so the file is
still present after `release()`. The pre-repair body was then restored byte-exact with
`git checkout -- tools/agent_supervisor/review_slots.py` (working tree verified clean via
`git status --porcelain`), and the test file re-ran GREEN (20 passed, 2 skipped). The mutation was
never committed.

## 4. Scenario → test map (positive / negative / mutation / platform)

| Scenario | Test (all in `ReleaseLockRemovalTests`) | Host | Pre-repair | Final head |
|---|---|---|---|---|
| S5(i) transient removal fails N times then succeeds; file gone; next acquire prompt | `test_release_retries_transient_removal_failure_then_succeeds` | any | RED | GREEN |
| S3 platform fact: open reader handle blocks `unlink` (PermissionError), file stays | `test_windows_open_reader_blocks_unlink_platform_fact` | nt only | GREEN (OS fact) | GREEN |
| S5(v) real concurrent handle held briefly during `release()`; file gone after | `test_windows_release_removes_lock_despite_concurrent_reader` | nt only | RED | GREEN |
| S5(ii) never-clears: bounded, fail-closed (file stays), typed + logged, no raise | `test_release_that_never_clears_is_bounded_failclosed_and_observable` | any | n/a (new w/ repair) | GREEN |
| S5(iii) foreign `lock_id` left untouched, byte-identical; decline is not a failure | `test_release_never_removes_a_foreign_lock_id` | any | n/a (new w/ repair) | GREEN |

Which tests must be RED on windows-latest at commit A and GREEN at the final head (for the
orchestrator's ci-exp and PR-head runs):
- RED at commit A, GREEN at final head: `test_release_retries_transient_removal_failure_then_succeeds`
  (also RED/GREEN on Linux) and `test_windows_release_removes_lock_despite_concurrent_reader` (nt).
- GREEN at commit A and final head (the OS fact, independent of the repair):
  `test_windows_open_reader_blocks_unlink_platform_fact` (nt).

## 5. R094 no-weakening statement (S6)

- **No test deleted, renamed away or xfail-marked.** The test-file diff is 167 insertions, 0
  deletions. Every pre-existing test name is present and byte-identical after the change
  (`PrimaryReserveReleaseTests` ×3, `RaceTests` ×2, `PerLaneTests` ×1, `FailureAndReclaimTests` ×7,
  `WindowsSharingViolationTests` ×4).
- **No assertion loosened.** `RaceTests.test_global_last_slot_never_double_taken` keeps
  `assertEqual(winners, 2)` and `assertLessEqual(len(ReviewSlots(self.dir).active()), 2)`;
  `test_per_lane_last_slot_never_double_taken` keeps `assertEqual(winners, 1)`. `_run_race` still
  fails loudly on any non-`admitted`/non-`refused:concurrency_limit_reached` outcome, so a
  `slot_lock_timeout` inside a race is STILL a loud failure (this is what caught the defect).
  `_RACE_LEGITIMATE_REFUSAL = "refused:concurrency_limit_reached"` is unchanged.
- **No timing values widened.** The racers' `lock_timeout_s` (30 s), the hold, `_RACE_PARENT_WAIT_S`
  (60 s), `_RACE_BARRIER_WAIT_S` (90 s) and the barrier budget are UNCHANGED — the record proves the
  cause is the release path, not any of those windows, so none was touched.
- **No retry/rerun of a TEST, no rerun/flaky plugin, no CI or pytest-configuration change.** The
  retry added is INSIDE the production `release()` (the real lock-removal bound), not around a test.
  `.github/**` and all pytest config are untouched (forbidden paths respected).
- **The only skips added are two Windows-only platform skips** (`skipUnless(os.name == "nt", …)`) on
  `test_windows_open_reader_blocks_unlink_platform_fact` and
  `test_windows_release_removes_lock_despite_concurrent_reader`. Both are authorized by S3 ("a
  deterministic Windows-only test … asserts the platform fact directly") and the delivery spec
  ("Windows-only tests are skipped elsewhere with a stated reason"): the Win32 sharing behaviour
  cannot be exercised on POSIX, where `unlink` of an open file succeeds. No existing test is skipped.
- **Public interface unchanged.** `ReviewSlots.try_reserve` / `release` / `reserve` / `active`,
  `Reservation`, `SlotGrant`, `SlotError` codes and `reservation_owner_alive` are unchanged;
  `release()` still returns `None` and never raises; the new `release_error` attribute and `logger`
  are additive and observable.

## 6. Sibling surfaces (S8) — reported only, NOT changed

(Full text in the convergence record §5.)
- `locking.py` `SingleInstanceLock.release()` (~L300–312): the same one-shot `unlink` inside
  `except OSError: return False`; same latent Windows stuck-lock pattern, lower exposure.
- `_SlotLock.acquire` and `SingleInstanceLock.acquire`: a payload-write failure after the O_EXCL
  create leaves an unreadable lock file on disk (others read it as `None` → wait → time out).
- Recertification: this change alters the `tools/agent_supervisor/` tree hash, re-establishing the
  `M0-T039-supervisor-freeze.md` suite baseline (≥ 1165 tests, 0 failures) under the standard gates
  and carrying the D-091 recertification follow-up (M0-T181 already recorded M0-T179 as superseded).
  A recorded cost authorized by D-090-R093, not a bar; the supervisor stays SHADOW-ONLY.

## 7. Classification and open item

- Classification: **real supervisor defect** in `_SlotLock.release()` (candidate (a) primary,
  (b) secondary). (c), (d), (e) ruled out — see convergence record §2.3. The deciding discriminator
  is the reason code: `slot_lock_timeout` (lock acquire deadline inside `try_reserve`), not
  `barrier_timeout` (harness) and not `concurrency_limit_reached` (legitimate).
- M0-T176 §4 item 4 does NOT stand (its World-B dismissal was incomplete); M0-T181 Failure A DOES
  stand (a distinct under-count symptom; its instrumentation exposed this defect).
- Open item (not a blocker): the windows-latest ci-exp run (new tests RED/GREEN before the repair)
  and the repaired-PR-head supervisor-bridge run id + counts are orchestrator-captured; the
  convergence record is marked PENDING WINDOWS EVIDENCE and becomes VERIFIED_CLOSED when those run
  ids are filled in.
