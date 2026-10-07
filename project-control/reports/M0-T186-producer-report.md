# Producer report — M0-T186

The sub-agent ledger's `_exclusive()` lock on windows-latest (DB-157). DB-157; D-090-R093/R094.
Method: `/deficit-convergence`. Qualifying evidence (supervisor-freeze §2, AD-093): a reproduced
defect — CI run 37519342596, job 112460379795 (supervisor-bridge, windows-latest).

- Producer: backend-engineer, isolated worktree
  `/root/project/nyc-buildability/.claude/worktrees/agent-af69907a37976d578`.
- Claim-seam head (reset target): `9371c1e4d87e332b42cebd369be88ae210ab838d`.
- The convergence record (`M0-T186-convergence-record.md`) carries the frozen evidence, the full
  causal trace, the candidate adjudication, the repair and the pending-Windows closing. This report is
  the files-changed, check-by-check and no-weakening evidence.

## 1. Files changed (producer scope, all within allowed_paths)

- `tools/agent_supervisor/mrl_subagent_contract.py` — the repair: a named `_is_windows()` seam and a
  `PermissionError` branch in `_exclusive()`'s acquire loop. `git diff --numstat 9371c1e4..HEAD`:
  **37 insertions, 4 deletions** (the 4 are the pre-fix one-line docstring and the inline
  deadline/sleep in the old `FileExistsError` branch). No other production code changed; the release
  `finally` and every other function are unchanged.
- `tools/test_agent_supervisor_mrl_subagent_contract.py` — new `TestExclusiveWindowsDeletePending`
  class (5 tests) + the `_failing_lock_open` helper + the `errno`/`os` imports. `git diff --numstat`:
  **124 insertions, 0 deletions** — no existing test touched.
- `project-control/reports/M0-T186-convergence-record.md`, `…-producer-report.md` — commit C.

Three commits (in this worktree; not pushed):
- A `685ca1f374128a17967e10da46605bd5fb754134` — tests only, repair absent.
- B `aba185655755c14c69e2c6224e337b5f22c16a27` — the one bounded repair (carries the supervisor-freeze
  qualifying-evidence line in its body).
- C — these two reports (replacing the placeholders).

## 2. Check commands — DIRECT exit codes and counts

Python = `/root/project/lanes-runtime/venv/bin/python` (3.12.3), `PYTHONDONTWRITEBYTECODE=1`. The whole
`tools/test_agent_supervisor_*.py` glob is NOT run on this Linux server (it runs only in the
windows-latest supervisor-bridge CI job). Commands run one at a time; exit codes read by `echo $?`
directly (never piped through `tail` first).

| Check | When | Exit | Result |
|---|---|---|---|
| (a) `pytest -q -p no:cacheprovider tools/test_agent_supervisor_mrl_subagent_contract.py` | claim head | 0 | 45 passed (baseline) |
| (a) same | commit **A** `685ca1f3` | 1 | 2 failed (`test_transient_windows_permission_error_waits_then_succeeds`, `test_persistent_windows_permission_error_times_out_fail_closed`), 47 passed, 1 skipped |
| (a) same | **final head** (B/C) | 0 | 49 passed, 1 skipped (the nt-only platform-fact test skips on Linux) |
| (b) `ruff check tools/agent_supervisor/mrl_subagent_contract.py tools/test_agent_supervisor_mrl_subagent_contract.py` | final head | 0 | All checks passed |
| (c) `python tools/supervisor_command_doc_check.py` | final head | 0 | 11 presented supervisor command(s) checked; 0 failure(s) |
| (d) `python3 tools/modularity_check.py --check` | final head | 0 | pass; `mrl_subagent_contract.py` **478 lines** (< 600 warn). The printed `warn` lines are pre-existing for other modules (breakeven.py, max_envelope.py, cli.py, codex_reviewer.py, durable_state.py, evidence.py, gate_wave.py, next_task.py) — NOT this file |
| (e) mutation proof (pre-fix restored) | §3 | 1 | 2 failed (both repair-dependent tests) |
| (f) `git diff 9371c1e4..HEAD -- <testfile>` | final head | — | additions only (no deletion lines; 124 insertions, 0 deletions) |

### Windows CI (S3) — PENDING, orchestrator-captured

The producer cannot run Windows here. The orchestrator pushes a `ci-exp/M0-T186-*` branch from commit
A (tests only) and records the before/after Windows runs. Placeholders in convergence record §3.

- Before the repair, commit A `685ca1f3` on `ci-exp/M0-T186-*`: the two repair-dependent S5 tests RED
  on windows-latest, the nt-only platform-fact test PASSED.
  `[ORCHESTRATOR TO SUPPLY: branch, run id, job id, runner image, log bytes + sha256, test names,
  summary.]`
- After the repair, the PR head (A+B+C): supervisor-bridge job green in both runs, those tests GREEN
  on Windows, `test_parallel_requests_never_exceed_limits` green.
  `[ORCHESTRATOR TO SUPPLY: PR head sha, both run/job ids, log bytes + sha256, suite summary (expect
  ≥ 1165, 0 failed).]`

## 3. Mutation proof (S5 / check e) — the fix is load-bearing

With `_exclusive()` reverted to the literal pre-fix body (via
`git checkout 9371c1e4 -- tools/agent_supervisor/mrl_subagent_contract.py`; `grep` confirmed the
`except PermissionError` branch and `_is_windows()` absent), the two repair-dependent tests FAIL:

```
/root/project/lanes-runtime/venv/bin/python -m pytest -p no:cacheprovider \
  "tools/test_agent_supervisor_mrl_subagent_contract.py::TestExclusiveWindowsDeletePending::test_transient_windows_permission_error_waits_then_succeeds" \
  "tools/test_agent_supervisor_mrl_subagent_contract.py::TestExclusiveWindowsDeletePending::test_persistent_windows_permission_error_times_out_fail_closed"
…
tools/agent_supervisor/mrl_subagent_contract.py:133: in _exclusive
    fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
E   PermissionError: [Errno 13] delete pending
…
2 failed in 0.53s
```
Direct exit code: **1**. Failing assertions, named:
- `test_transient_windows_permission_error_waits_then_succeeds` — the injected `PermissionError`
  propagates out of `decision = _req(ledger)`; the test raises **before** `assert decision.allowed is
  True` is reached (the create's error reaches the caller unhandled — the exact production defect).
- `test_persistent_windows_permission_error_times_out_fail_closed` — the raw `PermissionError`
  propagates instead of the module's `ContractError('…fail closed')`, so
  `pytest.raises(ContractError, match="fail closed")` fails to match and the `PermissionError` escapes
  the `with` block.

The source was then restored from HEAD (`git checkout HEAD -- …`); `git status --porcelain` empty; the
repair (`_is_windows` line 126, `except PermissionError` line 162) is back. The mutation was never
committed.

## 4. Which tests are RED/GREEN where

- RED on windows-latest at commit A, GREEN at the final head (and RED/GREEN on Linux too):
  `test_transient_windows_permission_error_waits_then_succeeds`,
  `test_persistent_windows_permission_error_times_out_fail_closed`.
- GREEN at BOTH commit A and the final head: `test_non_permission_oserror_at_create_stays_loud`,
  `test_permission_error_on_posix_stays_loud` (both host-independent; the create's error is not the
  transient Windows case, so it stays loud on either platform regardless of the repair).
- `test_windows_delete_pending_create_raises_permission_error_platform_fact`: SKIPPED off-Windows
  (`os.name != 'nt'`) at both commits; on windows-latest it is GREEN at both (a pure OS fact,
  independent of the repair) and is the deciding platform evidence for candidate (a).
- Production: `test_parallel_requests_never_exceed_limits` is UNCHANGED; it may still flake RED on
  windows-latest at commit A (the live defect) and is GREEN at the final head because of the repair.

## 5. R094 no-weakening statement (S6)

- **No assertion loosened.** `test_parallel_requests_never_exceed_limits` keeps
  `results.count(True) == 2 and results.count(False) == 6`, its 8 threads and `max_concurrent=2,
  max_total=5`. Its green comes from the production repair, not from touching the test.
- **Additions only.** Test-file diff is 124 insertions, 0 deletions; no test deleted, renamed,
  xfail-marked or retried.
- **The only new skip** is the Windows-only platform-fact test, skipped off-Windows with a stated
  reason (`@pytest.mark.skipif(os.name != 'nt', …)`, the pytest form of `skipUnless(os.name == 'nt')`),
  authorized by R094. No existing test is skipped.
- **No retry/rerun of a TEST, no rerun/flaky plugin, no `.github/**` or pytest-config change, no
  timeout raised to hide the failure.** The retry added is INSIDE the production `_exclusive()` acquire
  loop (the real lock wait), bounded by the lock's own `_LOCK_TIMEOUT_S` deadline; `_LOCK_TIMEOUT_S`
  stays 5.0 (the never-clears test monkeypatches it to 0.2 only within its own scope).
- **Only the proven transient Windows case is treated as busy.** An OSError that is not the transient
  `PermissionError` stays loud on both platforms; a `PermissionError` on POSIX stays loud; never an
  admission, never an unbounded loop.
- **Public interface unchanged.** `SubagentLedger.request` and its `ContractError` refusal are
  unchanged; `_is_windows()` is an additive internal seam.

## 6. Sibling surfaces (S8) — reported only, NOT changed

(Full text in the convergence record §7.)
- `review_slots._SlotLock.acquire` — ALREADY handles the Windows delete-pending `PermissionError` as
  busy (M0-T176/M0-T184); not exposed; no change. This repair brings `_exclusive` to parity.
- `locking.SingleInstanceLock.acquire` (line 261) — catches only `FileExistsError`; SAME acquire-side
  pattern as the pre-fix `_exclusive` (DB-160). Lower exposure (one holder/run, few contenders). No
  failure seen; repair only under a reproduced failure (supervisor freeze).
- DB-152 (`locking.SingleInstanceLock.release()` one-shot swallowed `unlink`; the mrl release
  `finally` is the same family) and DB-153 (payload-write-after-create stranded lock, which does NOT
  apply to `_exclusive` — it writes no payload): both weighed in §7, left for a reproduced-failure
  task; neither was part of this observed acquire-side crash.
- Recertification: alters the `tools/agent_supervisor/` tree hash → re-establish the
  `M0-T039-supervisor-freeze.md` baseline (≥ 1165 tests, 0 failures) under the standard gates; a
  recorded cost (D-090-R093), supervisor stays SHADOW-ONLY.

## 7. Classification and closure

- Classification: **real supervisor defect** in `_exclusive()`'s acquire loop (candidate (a): an
  `O_EXCL` create against a delete-pending lock file raises `PermissionError`, caught by neither branch
  pre-fix). (b) ruled out (no external-process signature; not needed), (c) ruled out (production-origin
  exception; test is correct), (d) ruled out (a crash, not a timing under-count) — see convergence
  record §2.2.
- STATUS: **PENDING WINDOWS DEMONSTRATION.** The Linux-side proof is complete (mechanism + mutation
  proof + green focused run); the record closes VERIFIED_CLOSED only after the orchestrator fills §3's
  before/after windows-latest runs. No blocker; the only open item is the Windows evidence, which the
  producer cannot run here.
