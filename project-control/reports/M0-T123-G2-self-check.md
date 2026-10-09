# M0-T123 — G2 self-check (orchestrator verification of producer evidence)

Recorded 2026-08-30 at control head `6aada29` (cherry-pick of producer commit `9eba902`;
base `7b78d6c`). VERDICT: **PASS** — every headline claim independently re-executed;
two orchestrator disclosures below.

| # | Check | Result |
|---|---|---|
| 1 | Worktree identity + scope | HEAD `7b78d6c` ✓; changed files exactly the allowed set (+2 agent-memory files) ✓; forbidden paths untouched |
| 2 | Preserved-source integrity (R329/R341) | All four SHA-256 heads byte-identical to the G0 baselines AFTER the producer's fixture derivation: journal `a4acb370f3a23fd5`, audit `e80c057cabc24478`, t1 `3a0d1f30664b1deb`, t2 `3c9185687f12e86a` ✓ — the preserved evidence was only ever read |
| 3 | Imports / seam module | `import tools.agent_supervisor.cli` + `launch_seam` OK ✓ (IDE diagnostics were again a stale mid-write snapshot; disproven by execution) |
| 4 | New suite | **45 passed** — re-run twice by the orchestrator incl. `-p no:randomly` and `--collect-only` (45 collected, deterministic), in the worktree AND on the control checkout at `6aada29` ✓ |
| 5 | Related suites | orchestrator re-run (loop, loop_turnover, session_continuity, claude_runner_env, restart_channel, golden_run): **206 passed** ✓; producer's 12-file "related" list: 533 (producer-verified re-run) |
| 6 | FULL suite | orchestrator's own run in the worktree: **2,870 passed, 2 skipped, 0 failed** (chain: 2,814 T122 baseline + 56 new) ✓ |
| 7 | Count reconciliation (disclosed) | The producer's first return claimed 46/2869; the orchestrator caught both against reality (45/2870) and sent a report-accuracy round. Explanation verified coherent: 46 = a bundled-invocation misattribution (45 + 1 hygiene test); 2869 = measured one increment before the final AS-8 test landed. Both reports now carry the corrected numbers plus explicit correction notes. Every corrected number matches the orchestrator's independent measurements exactly. |
| 8 | Fixture scanner-hygiene (orchestrator edit, disclosed) | The gitleaks pre-commit hook flagged the fixture's `_provenance.runtime_dir_key` (a 64-hex SHA-256 of the canonical checkout path — the runtime-dir naming digest, PUBLIC information already in committed reports, not a secret). The hook was NOT bypassed: the orchestrator renamed the field to `runtime_dir_name` and truncated the value with an explanatory note; no test consumes the field (grep-verified); 45/45 re-verified after the edit. This is the only orchestrator-authored content change to producer files. |
| 9 | Model identity (Amendment-18 discipline) | Producer transcript mid-window: **323/323 events `claude-opus-4-8`**, uniform — the same D-004-R735 authorized bounded assignment; no override passed at dispatch; final re-read owed at accept |
| 10 | R345 window prohibitions | No live `start`/`owner-restart`/`clear-recovery` executed by anyone this window; journal untouched (hash row 2); PR #241 untouched; no budget/audit/policy change in the diff |
| 11 | Terminal-evidence honesty (R343/R344) | The producer RECOVERED the actual terminal event from primary evidence: `max_turns_reached {maxTurns:12, turnCount:13}` (cycle-2 transcript records 92–95) — the worker exhausted its turn budget re-orienting in the wrong cwd; NO `result` record, no stderr. The prior context-limit hypothesis is explicitly contradicted and re-labeled unproven/abandoned in the report. Reviewers should verify the transcript records cited. |
| 12 | Modularity | `modularity_check --check`: failures 0; `launch_seam.py` (338 lines) not among warnings ✓ |

Noted for the gate wave: the root-cause traces (rotation_pending set at audit seq 24 but
unconsumed on the ordinary start path, `loop.py:936-939`/`2587-2589`; `--worktree`
defaulting to the checkout, `cli.py:2642`/`2672`) are the load-bearing claims G3 must
re-trace in code; the three enforcement points (run_unit Popen, _run_loop worktree gate,
pre-first-dispatch shed) and the AST bypass sweep parallel the M0-T121 pattern the
reviewers know first-hand.
