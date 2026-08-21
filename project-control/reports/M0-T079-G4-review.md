# M0-T079 G4 integration/regression review (verbatim reviewer return)

Saved VERBATIM by the orchestrator from the read-only reviewer agent's return channel
(report-preservation rule). Reviewer: t079-g4-reviewer (independent; reviewer ≠ producer ≠
verifier). Verdict PASS; Finding 1 (medium) is treated as a required correction for the
consolidated T079 rework round; Findings 2-4 recorded.

---

# G4 integration/regression review — M0-T079

## Verdict: PASS — with one finding the orchestrator should rule on before acceptance

The change composes correctly with its real neighbors. No regression anywhere in the tree, every claimed CLI journey reproduces under real subprocess invocation, and both integration risks the producer flagged resolve in the change's favor. One completeness gap in the headline deliverable is undisclosed in the producer report.

---

## 1. Full suite — clean, and it clears the producer's scoped run

```
python -m pytest tools/ -q --no-header
2261 passed, 3 skipped in 2723.73s (0:45:23)   exit 0
```

2261 + 3 = 2264, matching `--collect-only`. Zero failures across the whole `tools/` tree, so the producer's `-k agent_supervisor` run missed no cross-tree regression. The 45-minute wall time is machine contention (three other team agents were running suites concurrently), not a product problem.

I independently reproduced the producer's scoped number exactly: `-k agent_supervisor` gives **1707 passed, 2 skipped, 555 deselected**, and the two new modules together are **116 passed** (53 + 63, as claimed).

The census-sensitive non-supervisor modules — the plausible route for a cross-tree break, since the change adds seven files under `tools/agent_supervisor/` — are green on their own: modularity/subsystem/fingerprint/product-map 72 passed, repo-index/repo-views/code-graph 114 passed.

## 2. Real CLI journeys — all four reproduce

Run as genuine `subprocess` invocations of `python -m tools.agent_supervisor` against throwaway temp directories outside the repo:

- **(a)** `start --mode limited-auto --json` → exit **16**, stdout parses as JSON carrying `schema_version` 1.0.0, `outcome: refused_mode`, `exit_code: 16`, `reason_code: limited_auto_not_enabled`. The payload's `exit_code` equals the actual process exit code.
- **(b)** Same without `--json` → `REFUSED (refused_mode, exit 16): limited_auto_not_enabled` on stderr, no traceback, no `NotImplementedError` in either stream.
- **(c)** `doctor` → exit 0, `overall: PASS`, full refusal contract printed (`halted=10` through `refused_mode=16`). `doctor --json` also exposes it as structured data under `refusal_contract`, with `ok: true`.
- **(d) AS-8** — `start --mode shadow` with every input named, against a temp non-git directory → exit **11**, `missing_inputs: []` (the command line genuinely is complete), `dispatched: false`, `provider_calls_made: 0`, and `probes.failed` naming all four: `task_authority`, `branch`, `worktree`, `git_and_remote_state`. The defect proof holds outside the test harness.

## 3. Exit-code contract integration — no consumer is broken

I found **no wrapper, script, or workflow anywhere that assumes exit 0 means "refused safely."**

- `.github/workflows/ci.yml` only runs `pytest tools/test_agent_supervisor_*.py` (a glob, so both new modules are picked up automatically) and never invokes `start`.
- `docs/CONTROLLER_UPDATE_RUNBOOK.md` §11 is a human-operated PowerShell procedure with no exit-code branching.
- `tools/agent_supervisor/README.md` documents commands only; `services/api/app/documents/gate.py` mentions the supervisor in a comment only.
- `C:\Users\MLFLL\Downloads\nyc-zoning\mission-control.ps1` never invokes the supervisor at all — its only `$LASTEXITCODE` check is on a `git diff`.
- The archived `M0-T045` rehearsal `.cmd` files record `%ERRORLEVEL%` after `start` but never branch on it; their one `if errorlevel 1` follows `resume-pending-prompt`, which this task does not touch.

Two things make producer risk 2 milder than stated. **Success still exits 0** — confirmed empirically with a real dispatching run, and `tools/test_agent_supervisor_loop.py:1244` still asserts `code == 0` for a genuine dispatch. And **a normal supervised/shadow park still exits 0**: `tools/agent_supervisor/start_gate.py:235` returns `None` for any mode other than `limited-auto`, so only `budget_exhausted` changes an attended mode's exit code, and that requires `--run-wall-clock-seconds`, which nothing currently passes. The only behavior change for existing launches is that refusals which used to exit 0 now exit 10–16 — strictly the safe direction.

### FINDING 1 (MEDIUM) — one refusal path still exits 0, and the report does not say so

**Location:** `tools/agent_supervisor/cli.py:2971` (the `if not dispatchable:` branch) and `tools/agent_supervisor/cli.py:3111`.

`start` refusing for a missing required input returns **exit 0** with no `refusal` key and no `refused` flag in the JSON payload — only prose in `stopped_because`. This is deliberate: `cli.py:3111` carries the comment *"Missing-input stops still exit 0."* Every other branch in the chain assigns a typed refusal; `cli.py:2971` is the only one that leaves `refusal = None`. It is pinned by `tools/test_agent_supervisor_loop.py:1146` (`test_start_without_the_required_inputs_does_not_dispatch`, asserting `code == 0`), which the task did not amend even though it amended seven sibling exit-code assertions.

**Consequence:** exactly what `tools/agent_supervisor/refusals.py`'s own docstring names as the defect being fixed — *"reported honestly in the payload text but exited 0, which is indistinguishable from success to anything that reads exit codes."* Concretely, I ran `start --mode limited-auto --owner-enable-bounded-auto` with inputs absent: **exit 0**, `dispatched: false`, `provider_calls_made: 0`. An owner-enabled bounded unattended run whose scheduled-task argv has drifted — a moved config, a renamed executable, a changed packet path — reports success to its launcher while never having run a cycle. That is the highest-frequency refusal an unattended launcher will hit.

**Why this does not fail the gate:** it is not a regression. The behavior is unchanged from baseline, safety holds (`dispatched: false`, `provider_calls_made: 0`), and a JSON-reading caller can still detect it via `missing_inputs` or `dispatched`. But it sits inside deliverable 4's stated scope, and producer report §8 risk 2 describes "four previously-exit-0 refusal paths" in a way that reads as a complete enumeration. It is not.

**Recommendation:** either close it (assign a refusal in that branch plus amend the pinned test) or record it as an explicit documented carve-out. If the latter, the contract `doctor` prints should say so — it currently advertises 10–16 with no mention that a missing input yields 0 or that a failed manifest yields the generic 1.

## 4. Crash-window modules — all green

Run individually: crash **32**, endurance **94**, adversarial **93**, invariants **46**, fuzz **40** — 305 tests, zero failures. The journal the budget record now shares is written through the pre-existing `set_state` primitive (`tools/agent_supervisor/durable_state.py:371`), a single `BEGIN IMMEDIATE`/`COMMIT` with rollback, so a crash mid-write leaves either the old record or the new one, never a torn one.

## 5. Backward compatibility — confirmed two ways

`durable_state.py` is **not in the task diff at all**; `state_kv` is byte-identical to the pre-change tree. A pre-T079 journal simply lacks the `run_budget/<run_id>` row, `get_state` returns its default, and `start()` takes the first-launch branch.

Verified empirically: building a real journal, stripping the `run_budget/*` rows to reproduce the pre-T079 shape, and reopening produced no traceback, no `budget_not_started`, no spurious `budget_conflict`, a clean fresh record, `resumed=False`, `resumes=0` — with all prior state preserved and exactly one key added. A second open is a correct resume that reloads the original start instant. `SupervisedLoop.run_budget` is keyword-only with default `None`, so pre-T079 callers are unchanged, and `restore_counters` returns early when there are no tallies.

The extraction also preserved compatibility facades with **object identity** intact — `loop.OwnerTouchLedger is owner_touch.OwnerTouchLedger` and `loop.LoopError is errors.LoopError` — so cross-module `isinstance` and `except` clauses still work.

## 6. Concurrency — no new write outside the lock

`audit_fork_lock` 7 passed; the broader locking selection 93 passed. At code level the lock is acquired inside `recover_boot` (`tools/agent_supervisor/recovery.py:495`, called from `cli.py:2934`) and released in the `finally` at `cli.py:3065`. `_run_loop` — which constructs and `start()`s the budget ledger at `cli.py:2762–2767` and owns every subsequent `observe`/`persist_counters`/`finalize` — is invoked at `cli.py:3032`, inside that scope. No budget write occurs outside the lock.

`CircuitBreakers.restore` (`tools/agent_supervisor/circuit_breakers.py:194`) is correctly monotonic (`max`), refuses unknown counter names and negatives, and its `_roll_day` only zeroes when a day is already set and differs — so on a fresh post-crash instance the restored per-day tallies survive rather than being wiped.

## 7. Platform — both supervisor skips are pre-existing and conditional

`tools/test_agent_supervisor_policy.py:449` ("cannot create a symlink here: WinError 1314") and `tools/test_agent_supervisor_process.py:448` ("POSIX-only guard"). Neither test module appears in the task diff, so the skips are definitionally unchanged. The full-tree run shows a third skip outside the supervisor scope — `tools/test_repo_fingerprint.py:148` ("symlinks unavailable on this host") — also pre-existing and unrelated to T079.

The POSIX refusal path is amended correctly: `tools/test_agent_supervisor_start_reentry.py:467` now asserts exit **12** / `unsupported_platform` / `containment_refused` while retaining every prior assertion on `dispatched`, `provider_calls_made`, `containment.kind`, and the `containment_gate_refused` audit event. Strengthened, not weakened.

## 8. Windows containment — precondition intact

Containment-related selection: 28 passed, 1 skipped (the POSIX guard). `cli.py:3007` still gates on `elif not containment_ok:` *before* `_run_loop`, in the same position in the chain; only the exit code changed from 0 to a typed 12, and the refusal is still audited. `process_group`, `taskkill`, and an undeterminable host all still refuse to dispatch; `job_object` still permits.

## Additional notes

- **Producer risk 6 is now RESOLVED.** The seven new modules were untracked when the producer ran `modularity_check`, so they were uncensused. Now that they are committed: `python tools/modularity_check.py --check` reports **272 files (up from 265), failures 0, warnings 5** — the same five pre-existing warnings. The new modules pass the census.
- **FINDING 2 (LOW) — `_REVISE_SAFE_RESETS` can silently drift.** `tools/agent_supervisor/loop_breakers.py:53` hardcodes three counter names and is exactly `RESET_ON_PROGRESS` minus `consecutive_revision_loops`; I verified the subset relationship holds today. No test guards it, so adding a fourth `RESET_ON_PROGRESS` counter later would leave it uncleared on a REVISE. Fails safe (a counter accumulates rather than being cleared) but would surface as a surprise breaker trip. The narrowing itself weakens nothing: no counter that previously accumulated is now cleared.
- **FINDING 3 (LOW) — the suite now needs a git that can create commits.** Five fixture sites run `git init` plus `git commit --allow-empty` without `--no-verify` (`tools/test_agent_supervisor_loop.py:1096`, `..._manifest_binding.py:254`, `..._model_chain.py:222`, `..._recovery_probes.py:735`, `..._start_reentry.py:87`). This host has a global `init.templateDir` installing a gitleaks pre-commit hook and the tests still pass; CI's fresh `windows-latest` runner has no such template. Worth knowing if a future runner carries a restrictive git config.
- **FINDING 4 (INFO) — CI runs Python 3.12; all evidence is 3.11.9.** Both the producer's runs and mine used 3.11.9, while `.github/workflows/ci.yml` pins 3.12. The local 3.13 install is broken (no `python.exe`), so I could not bracket it. A static check of all seven new modules found no `utcnow`, `distutils`, `imp`, or other 3.12-removed API — the code uses timezone-aware `datetime.fromtimestamp(x, timezone.utc)`. Risk negligible, but formally unverified until CI runs.

---

## Reviewed identity

`c52613f28732d73085efa71114cddde7a1468614` (task commit `e830c4b`).

Working tree carried only ledger modifications; no source file differed from HEAD. No repo writes, no git mutations, no tools/project_control.py.

## Commands run

(Recorded verbatim in the reviewer return: full-tree pytest, scoped pytest, per-module crash/endurance/adversarial/invariants/fuzz/lock/containment selections, modularity check, four scratchpad subprocess harnesses g4_cli_journeys/g4_compat/g4_compat2/g4_gate, real `python -m tools.agent_supervisor` invocations, read-only git forms.)
