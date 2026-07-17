<!-- Verbatim reviewer return (agent-return channel; agentId a2dcc7a7d819ff2af, code-reviewer, 2026-07-17). Saved by the orchestrator per the report-preservation rule. Verdicts: G3 PASS, G4 PASS (zero defects; LOW observations O1-O4). -->

# Gate Report — M0-T017 G3 (independent walkthrough) + G4 (integration/regression)

- **Task:** M0-T017 — defect fix: control-plane S7 test must not require a backlog task in the live ledger copy
- **Producer:** backend-engineer | **Reviewer:** code-reviewer (independent; did not produce)
- **Target:** worktree `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T017`, branch `task/M0-T017-s7-ledger-coupling`, HEAD `2aeb3db`
- **Date:** 2026-07-17 | **Mode:** read-only per ADR-005; all executions against disposable temp copies only
- **Inputs read first:** `project-control/tasks/M0-T017.json`, `project-control/reports/M0-T017-G0-readiness.md`, full `main...HEAD` diff, `project-control/reports/M0-T017-producer-report.md` (read last, after independent verification)

## Findings table

| # | Check | Method | Result |
|---|-------|--------|--------|
| 1 | Diff scope | `git diff main...HEAD --stat` / `--name-only`: exactly 2 files — `tools/test_project_control.py` (+75/−11) and `project-control/reports/M0-T017-producer-report.md`. `git diff main...HEAD -- tools/project_control.py` = **0 lines** — enforcement unchanged. Within `allowed_paths` per packet/G0. | PASS |
| 2 | Mechanism | Read line-by-line. `_synthesize_backlog_exemplar(pc)` writes `M9-T700` only into `pc = tmp/project-control` (tmpdir `pc-s7-*`, removed in `finally`). Record is well-formed (all 20 packet fields present, matching real task-packet shape), title explicitly `"SYNTHETIC S7 exemplar - test-only, never a real ledger task"`, docstring cites CI job 87990690868. `REAL_PC` is only ever read (`copy2`/`copytree`); all writes/unlinks target `pc`. M9 namespace cannot collide with real M0–M7 IDs. | PASS |
| 3 | No weakened assertions | Line-by-line diff audit. All prior S7 verifications intact: full real-ledger parse (`parsed >= 60`; 145 today), `status` over the real roster (rc 0), accepted floor `>= 21` (value unchanged; only message text reworded), message-only progress probe still executed and still asserts rc 0, legacy no-role gate-record `accept` tolerance (M9-T701 block byte-unchanged), write-time-only validation semantics. The **only** removed assertion is `assert backlog` — the live-composition coupling that *was* the defect. Coverage is strictly stronger: the permanent zero-backlog sub-check drains the copy, asserts `status` rc 0 + zero backlog remaining, then proves the synthesis probe — on **every** run, so the CI-breaking composition is now always exercised even when the live backlog is non-empty. | PASS |
| 4 | Coupling audit | Independent grep: `REAL_PC` appears at lines 66 (def), 817, 823, 825 — S7 only; all other groups build fully synthetic temp ledgers. Remaining floors verified as monotone-stable: `parsed >= 60` counts master_plan/state/config + tasks + gates + blockers (append-only in practice; reports/checkpoints dirs are created empty, not copied); `accepted >= 21` is monotone because accepted is terminal-immutable (proven by S6 at lines 760–772). No assertion anywhere depends on existence or exact counts of mutable statuses. Producer's "no other couplings" claim **independently confirmed**. | PASS |
| 5 | Suite run (worktree, real ledger AS-IS) | `python tools/test_project_control.py` → **all 10 groups OK, EXIT=0**, including: `OK: S7 backward compatibility (145 real ledger files parse; legacy records accepted; validation is write-time only; zero-backlog composition survived via synthesized exemplar)`. Live worktree composition is `{'accepted': 27, 'blocked': 2, 'claimed': 2}` — **zero backlog**, i.e. the exact composition that failed CI job 87990690868, so my run is itself the regression reproduction on the synthesis branch. | PASS |
| 6 | Boundary: backlog present | Replicated independently (different method from producer's `REAL_PC` monkeypatch): copied the whole worktree tools+ledger into a disposable temp tree, injected backlog task `M9-T900`, ran the full suite there. All 10 groups green, S7 reports **146** files parsed (145+1), real-first probe path (`backlog[0]`) taken, drain then removes `M9-T900`, synthesis sub-check still exercised. EXIT=0; temp tree deleted. | PASS |
| 7 | G4: regression, deps, ledger hygiene, CI | All 10 groups green twice (checks 5, 6). No new imports in the diff (`NO-NEW-IMPORTS`; stdlib-only suite preserved). After my runs, `git status --short` in the worktree is **completely clean** — including `project-control/` — proving the tests wrote nothing to the real ledger (all probes in `finally`-cleaned tmpdirs). No duplicate implementations; no contract/schema/migration surface touched (test-only). Disk footprint KB-scale, cleaned up (low-storage policy). CI on PR #22 all green incl. control-plane per orchestrator attestation in the dispatch (I cannot run `gh` under ADR-005; noted below). | PASS |

## Standing-concern checks (my review mandate)

- **Guessed schemas:** none — the synthetic record mirrors the real packet shape field-for-field (cross-checked against `M0-T017.json`); no external schema involved.
- **Hard-coded legal values:** none — test-fixture values only (`M9-T700`, `reviewer-y`, gates `G0,G3`), consistent with the suite's established synthetic convention.
- **Hidden defaults / silent uncertainty:** none — the synthesis rationale, the CI-job citation, the stable-invariant policy, and the floors' pruning assumption are all explicitly documented in docstrings and the producer report §6.
- **Weak tests:** the opposite — the fix converts a flaky live-composition dependency into a deterministic, always-exercised regression sub-check, and preserves real-record probing when available.
- **Contracts/migrations/RLS:** N/A (test-only; enforcement CLI byte-identical to main).

## Observations (LOW, non-blocking, no action required)

- **O1:** Synthetic record has `task_id: "M9-T700"` with `milestone_id: "M0"` (prefix/milestone mismatch). Deliberate suite convention (legacy exemplar `M9-T701` is identical in this respect) and the file is written directly to disk precisely because S7 tests read-tolerance of records that bypass write-time validation. Not a defect.
- **O2:** The floors (`parsed >= 60`, `accepted >= 21`) assume the ledger is never pruned. Producer disclosed this in report §6; carried forward in reviewer memory for any future ledger-pruning proposal.
- **O3:** The backlog-present branch runs in CI only when the live ledger happens to contain a backlog task (producer disclosed, §6). Acceptable: the probe code path is identical either way, and both this review and the producer proved the branch with disposable augmented copies.
- **O4:** CI-green on PR #22 is accepted as orchestrator-captured evidence per the ADR-005 evidence-capture division of labor; orchestrator should confirm control-plane goes green on main post-merge (producer report §7 already recommends this).

## Defects

None (blocking or otherwise).

## Verdict rationale

The defect (live-composition coupling at old line ~808) is removed with a mechanism that is strictly stronger than the prior assertion: real-first probing preserved, synthetic exemplar clearly labeled and temp-only, and a permanent zero-backlog sub-check that reproduces the exact CI-failing composition on every run. Nothing S7 previously verified was weakened; enforcement code is untouched; no other couplings of the class exist; both compositions verified green by independent execution; real ledger provably untouched.

Key artifacts: `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T017\tools\test_project_control.py` (fix, lines 781–904), `...\project-control\reports\M0-T017-producer-report.md`, `...\project-control\reports\M0-T017-G0-readiness.md`, `...\project-control\tasks\M0-T017.json`.

G3: PASS
G4: PASS
