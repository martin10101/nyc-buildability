# Producer report — M0-T186

The sub-agent ledger's `_exclusive()` lock on windows-latest (DB-157). DB-157; D-090-R093/R094.
Method: `/deficit-convergence`. Qualifying evidence (supervisor-freeze §2, AD-093): a reproduced
defect — CI run 37519342596, job 112460379795 (supervisor-bridge, windows-latest).

- Producer: backend-engineer, isolated worktree
  `/root/project/nyc-buildability/.claude/worktrees/agent-af69907a37976d578`.
- Claim-seam head: `9371c1e4d87e332b42cebd369be88ae210ab838d`.
- The convergence record carries the frozen evidence, the causal trace, the candidate adjudication
  (rewritten to the probe), what the probe did and did not demonstrate, and the closing condition.
  This report is files-changed, check-by-check, mutation and no-weakening evidence.

## 1. Files changed and commit lineage (all within allowed_paths)

- `tools/agent_supervisor/mrl_subagent_contract.py` — the repair (round 1): a named `_is_windows()`
  seam and a `PermissionError` branch in `_exclusive()`'s acquire loop. `git diff --numstat
  9371c1e4..B`: **37 insertions, 4 deletions**. KEPT unchanged this round (the probe supports it; see
  §3). Not edited in commit D.
- `tools/test_agent_supervisor_mrl_subagent_contract.py` — round 3 corrects the tests: removes the
  wrong platform-fact test, corrects the delete-pending wording of the other new tests to what is
  shown, and adds one real-race test. Diff vs the claim head is additions only (no pre-existing test
  touched).
- `project-control/reports/M0-T186-convergence-record.md`, `…-producer-report.md` — rewritten to the
  Windows evidence (commit D).

Commit lineage (not pushed):
- Round 1: A `685ca1f374128a17967e10da46605bd5fb754134` (tests), B
  `aba185655755c14c69e2c6224e337b5f22c16a27` (repair; carries the supervisor-freeze qualifying line),
  C `24aeb9490757bdf59261d8e01c952f1066c3078c` (reports). Cherry-picked onto the task branch as
  `d3eba6ca` / `7ee6299a` / `6d5899ce`.
- Round 2: P `e3b5417fea2095b0e48bbe079f2fc1e1664a8edc` (Windows probe) — experiment branch only,
  NEVER merged.
- Round 3 (this round): **D** (test correction + these reports, on the task branch, built on
  `e133a971`); **X** (experiment only, NEVER merged — the acquire loop restored to its pre-fix code,
  built on D). Their hashes are returned to the orchestrator and recorded in the task evidence map
  (a report does not carry its own/forward commit hash).

## 2. Check commands — DIRECT exit codes and counts

Python = `/root/project/lanes-runtime/venv/bin/python` (3.12.3), `PYTHONDONTWRITEBYTECODE=1`. The whole
`tools/test_agent_supervisor_*.py` glob is NOT run on this Linux server. Commands one at a time.

| Check | At | Exit | Result |
|---|---|---|---|
| (a) `pytest -q -p no:cacheprovider tools/test_agent_supervisor_mrl_subagent_contract.py` | commit D | 0 | 50 passed (the new `test_real_race_through_exclusive_holds_mutual_exclusion` ~2.0 s; no skips) |
| (b) `ruff check` on both files | commit D | 0 | All checks passed |
| (b) `python tools/supervisor_command_doc_check.py` | commit D | 0 | 11 commands checked; 0 failures |
| (b) `python3 tools/modularity_check.py --check` | commit D | 0 | pass; `mrl_subagent_contract.py` 478 lines (< 600); printed warnings are pre-existing for other modules |
| (c) `git diff 9371c1e4..HEAD -- <testfile>` | commit D | — | additions only (no pre-existing test line removed or changed) |
| (d) `git diff --name-only e133a971..HEAD` | commit D | — | only allowed paths (the test file + the two reports) |
| (d) `git diff --name-only D..X`; `git diff 9371c1e4 X -- mrl_subagent_contract.py` | commit X | — | X changes only the module; and the module at X is byte-identical to the claim head (empty diff) |
| (e) focused file on Linux | commit X | 1 | the two seam-injected branch tests fail here (pre-fix code); `test_real_race_through_exclusive_holds_mutual_exclusion` PASSES on Linux (POSIX raises FileExistsError, already handled) — the race mutation shows only on Windows |

### Windows CI (orchestrator-captured, quoted from the frozen files)

| Head | Run / job | Result |
|---|---|---|
| commit A alone `685ca1f3` (ci-exp/red) | 37554194212 / 112576500175 (log 60574 B, sha256 `70317417…334408`) | `test_transient_…` and `test_persistent_…` RED — `PermissionError: [Errno 13]` escapes at `_exclusive` line 133; 3 failed (the 3rd = the wrong platform-fact test, WinError 32 at its unlink), 3959 passed, 60 skipped |
| A+B+C `6d5899ce` | 37554223543 / 112576591960 (push); 37554228069 / 112576606545 (pr) | the four injected tests GREEN; only the wrong platform-fact test failed (WinError 32 at unlink); 1 failed, 3961 passed, 60 skipped each |
| probe P `e3b5417f` (ci-exp/probe) | 37555462888 / 112580543291 (log 72219 B, sha256 `1010705a…1ae6db`) | P1–P5 (see §3); 6 failed (intentional `pytest.fail`), 3961 passed, 60 skipped |
| commit D final head | — | `[ORCHESTRATOR TO SUPPLY: final-head runs]` — expect the supervisor-bridge job GREEN in both runs (the race test + the four branch tests green, the wrong test gone; ≥ 1165 tests, 0 failures) |
| commit X (experiment) | — | `[ORCHESTRATOR TO SUPPLY]` — expect `test_real_race_through_exclusive_holds_mutual_exclusion` RED on Windows against the pre-fix loop (a PermissionError escapes) |

## 3. Mutation proof — two layers

- **Host-independent (Linux), the seam-injected branch tests.** Round 1 showed that reverting
  `_exclusive()` to its pre-fix body makes `test_transient_…` and `test_persistent_…` FAIL (direct
  exit 1, 2 failed): the injected `PermissionError` escapes at `_exclusive` line 133 — in the transient
  test before `assert decision.allowed`, in the persistent test instead of the typed
  `ContractError('…fail closed')`. The new real-race test stays GREEN on Linux, so it needs the real
  platform.
- **Real platform (Windows).** Commit A alone (job 112576500175) shows the pre-fix code letting the
  create's `PermissionError [Errno 13]` escape — `test_transient_…` and `test_persistent_…` RED on
  Windows. Commit X (this round, experiment only, NEVER merged) restores the pre-fix acquire loop (the
  body at `9371c1e4`) and must turn the new `test_real_race_through_exclusive_holds_mutual_exclusion`
  RED on Windows while it is GREEN with the repair (probe P5: 32,673 acquired, no escape). That is the
  race test's real-platform mutation proof, orchestrator-captured.

## 4. Why the repair is KEPT (the probe supports it)

Probe P5 (frozen job 112580543291) ran the real 8-thread Windows race through the REPAIRED
`_exclusive()`: `max_concurrent_inside=1 (expect 1); {'acquired': 32673}` over 32,673 iterations,
15.1 s — no refusal, no escaped exception, mutual exclusion held. So the repair correctly waits out
and retries the transient create `PermissionError` the race produces (probe P4: 1,468 of 61,758
iterations raised `PermissionError(errno=13, winerror=None)`). The repair's correctness rests on
catching the transient `PermissionError`, not on the exact kernel reason (which the probe leaves
unproven). The module's own `_exclusive()` / `_is_windows()` docstrings and inline comment were
corrected to say exactly this (commit E, wording only — AST with docstrings stripped is identical);
they no longer name "delete-pending (ERROR_ACCESS_DENIED)" as fact.

## 5. R094 no-weakening statement (S6)

- Every test present at the claim head stays byte-identical: `git diff 9371c1e4..HEAD -- <testfile>`
  is additions only. `test_parallel_requests_never_exceed_limits` keeps `results.count(True) == 2 and
  results.count(False) == 6`, its 8 threads and `max_concurrent=2, max_total=5`.
- No skip remains in this file. The removed `test_windows_delete_pending_create_…` was the only
  `skipif`; its replacement runs on EVERY host. No claim-head test deleted, renamed, xfail-marked or
  loosened.
- The retry is INSIDE production `_exclusive()` (the real lock wait), bounded by `_LOCK_TIMEOUT_S` —
  no test retry/rerun, no rerun/flaky plugin, no `.github/**` or pytest-config change, no timeout
  widened to hide the failure (`_LOCK_TIMEOUT_S` stays 5.0).
- Only the transient Windows `PermissionError` is treated as busy; a non-PermissionError OSError stays
  loud on both platforms; a PermissionError on POSIX stays loud. Public interface unchanged.

## 6. Sibling surfaces (S8) — reported only, NOT changed

(Full text in the convergence record §7.) `review_slots._SlotLock.acquire` already catches the Windows
create `PermissionError` as busy (M0-T176/M0-T184) — this repair reaches parity.
`locking.SingleInstanceLock.acquire` (L261) catches only `FileExistsError`, the SAME pre-fix pattern
(DB-160), far lower exposure. DB-152 (release-side one-shot `unlink` swallow; the mrl `_exclusive`
`finally` is the same family) and DB-153 (payload-write stranded lock, which does not apply to
`_exclusive` — it writes no payload): left for a reproduced-failure task; neither was part of this
acquire-side crash. Recertification: alters the `tools/agent_supervisor/` tree hash → re-establish the
`M0-T039-supervisor-freeze.md` baseline (≥ 1165 tests, 0 failures); supervisor stays SHADOW-ONLY.

## 7. Classification and status

- Classification: **real supervisor defect** in `_exclusive()`'s acquire loop. (a) the RACE is PROVED
  (probe P4: 1,468/61,758 create `PermissionError` errno 13, no external process), the kernel reason
  NOT ESTABLISHED (`os.open` gives no winerror; P2 and P3 do not reproduce the create failure). (b)
  RULED OUT as a necessary cause (P4 reproduces it with no external process; P2/P3 cannot exclude an
  external handle ever having contributed). (c) RULED OUT (P4 is raw-`os` in isolated tmp_path; the
  production exception is in `_exclusive`). (d) RULED OUT (a real OS outcome, not a timing threshold).
- Round-1 statements withdrawn: "os.open shares delete on Windows" and the platform-fact test that
  rested on it (false — the unlink raised WinError 32); candidate (a) "PROVED" as delete-pending
  (downgraded: race proven, kernel reason not); candidate (b) "fully excluded" (corrected to
  unnecessary).
- STATUS: **NOT VERIFIED_CLOSED.** Closing condition (convergence record §8): commit D's final-head
  windows-latest job GREEN in both runs AND the commit-X experiment showing the race test RED on
  Windows against the pre-fix loop. Still open: those two Windows runs (the producer cannot run Windows
  here). The module-comment wording is now corrected (commit E). No blocker.
