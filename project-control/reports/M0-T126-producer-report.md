# M0-T126 producer report - self-check evidence

Producer: supervisor-stabilization-producer (logical identity). Worktree:
C:/Users/MLFLL/Downloads/nyc-zoning/nyc-development-feasibility-claude-pack/.claude/worktrees/agent-af926a5886c3c4ab3
Built on HEAD 1bb773531bbb3283211de28ffdaf374467e994ab (control/D-024-fable-codex-loop tip; verified
via git rev-parse after `git reset --hard`). Environment: Python 3.11.9, pytest 8.4.2, ruff 0.13.0.
The golden run (test_agent_supervisor_golden_run.py, ~3h13m) was NOT run per the packet (M0-T127
recert covers it; budget note O2).

This report records exact commands and outcomes. The design record (M0-T126-design-record.md) carries
the mechanism map, defect status, and residual limitations.

## 1. Commands run and outcomes (final identity, all 17 defects complete)

Tests (all zero-failure):

- test_agent_supervisor_command_docs.py       -> 17 passed
- test_agent_supervisor_orientation.py        -> 10 passed
- test_agent_supervisor_next_task.py          -> 19 passed (incl. G4-corr-3 verdict/advancement rows)
- test_agent_supervisor_checkpoint_journey.py -> 22 passed
- test_agent_supervisor_launch_seam.py        -> 69 passed (incl. 5 D2 tests)
- test_agent_supervisor_loop.py               -> 121 passed (D8 test updated; D11/D12 + D5-ceiling + D10 cross-process)
- test_agent_supervisor_recovery.py           -> 63 passed (incl. D6 three crash-injection rows + D16 sweep)
- test_agent_supervisor_runner.py             -> 74 passed (incl. D4 three-shape presence test)
- FAST golden_run classes (TwoUnit + InjectedFault + Watcher* + EpochRotation + StartEpilogue) -> 27 passed
- FULL supervisor suite excluding the ~3h R247 recert:
  python -m pytest tools/test_agent_supervisor_*.py -q --ignore=tools/test_agent_supervisor_golden_run.py
  -> 2980 passed, 2 skipped in ~215s   (baseline before this task: 2889 passed, 2 skipped)
  The one golden_run restart test that broke (it relied on the D10 duplicate-suppression bug) was
  updated to the certified single-cycle shape and now passes.

Command-document CI tooth:
- python tools/supervisor_command_doc_check.py  ->  exit 0; "12 presented supervisor command(s)
  checked; 0 failure(s)" against docs/CONTROLLER_UPDATE_RUNBOOK.md (including the section-11 start
  command, now pinning all five load-bearing flags).

Modularity (must stay failures 0):
- python tools/modularity_check.py --check  ->  exit 0; "selected 330 files; failures 0; warnings 10"
  (the 10 warnings are pre-existing, unrelated). Final SLOC vs baseline+10% thresholds: claude_runner.py
  1383/1383, cli.py 2953/2953 (both at limit - D4/D7(a) done as net-zero MODIFICATIONS there), loop.py
  2030/2088, recovery.py 525 (not baselined, under threshold). All new machinery is in the new focused
  modules + loop.py/recovery.py.
- python tools/test_modularity_check.py  ->  exit 0 (proof tests; re-run because I touched
  baseline-tracked files).

Lint (ruff 0.13.0):
- python -m ruff check <all new + edited files, code and tests>  ->  "All checks passed!"
- loop.py is now F401-clean: removed the genuinely-dead `import re` and marked the DELIBERATE
  owner_touch/STOP_FOR_OWNER re-export facade with `# noqa: F401` (lp.TOUCH_NOTIFY is used by a test,
  so the facade is load-bearing and must not be deleted).
- Whole-tree `ruff check .` reports errors ONLY in pre-existing files I never touched
  (tools/test_project_control.py, turnover_live_seam, etc.); CI does not ruff-check tools/.
- Static-analysis items the orchestrator flagged were verified: `_ceiling_context_tokens` (loop.py:554)
  and `_strip_trailing_comment` (command_docs.py:234) ARE module-level-defined and executed by tests
  (Python resolves module-level calls at call time); `live_ctx_tokens/live_ctx_known` ARE consumed
  (RunResult + loop._ceiling_context_tokens); the `.get` is guarded by `usage is None`. The D5 live
  figure is consumed by EVERY ceiling consumer: the mid-unit rotation flag and record_provider_session
  read _ceiling_context_tokens directly, and the pre-dispatch rotate / evaluate_ceiling-on-resume read
  it transitively via the continuity record (which now stores the live figure).

Import smoke:
- python -c "import tools.agent_supervisor.cli, tools.agent_supervisor.loop,
  tools.agent_supervisor.claude_runner"  ->  clean.

## 2. Files created (all inside allowed_paths)

- tools/agent_supervisor/turn_budget.py         (property 5 / D3: workload-sized turns + hard ceiling)
- tools/agent_supervisor/orientation.py         (property 1 / D3: front-loaded orientation packet)
- tools/agent_supervisor/next_task.py           (D9: close-run + selection + exactly-once advancement)
- tools/agent_supervisor/command_docs.py        (D1/D14/D15/D17: command-document validation tooth)
- tools/supervisor_command_doc_check.py         (CI entry for the tooth)
- tools/agent_supervisor/fixtures/m0t107_stream_d5.json     (derived D3/D5 stream fixture)
- tools/agent_supervisor/fixtures/m0t107_journey_facts.json (derived preserved-facts anchor)
- tools/test_agent_supervisor_checkpoint_journey.py (properties + D3/D5 + Codex CONTINUE/stale)
- tools/test_agent_supervisor_command_docs.py
- tools/test_agent_supervisor_next_task.py          (D9 + R388)
- tools/test_agent_supervisor_orientation.py
- project-control/reports/M0-T126-design-record.md
- project-control/reports/M0-T126-producer-report.md (this file)

## 3. Files edited (all inside allowed_paths)

- tools/agent_supervisor/claude_runner.py   (D5: live_context_tokens + field + audit; D4: native-tool
                                             sentinel-PRESENCE field rename)
- tools/agent_supervisor/cli.py             (property 1/5 orientation + sized turns; D2 repo binding;
                                             D9 close-on-start; D13 assert-before-budget; D7(a) epilogue)
- tools/agent_supervisor/loop.py            (D5 _ceiling_context_tokens consumers; D8 ROTATE routing;
                                             D11/D12 between-cycle intent gate; D6 dispatch-intent
                                             record/reconcile; D10 next-unit-prompt pointer + advancing
                                             cycle; removed dead `import re`, noqa'd the re-export facade)
- tools/agent_supervisor/recovery.py        (D6 dispatch-intent + AMBIGUOUS classify branch; D16
                                             dead-child archive sweep; D7(b) safe_auto_resume R595 note)
- tools/agent_supervisor/launch_seam.py     (D2 evaluate_repo_binding + enforce_launch_bindings)
- tools/agent_supervisor/session_continuity.py (D8: rotate_session in CONTEXT_SHEDDING_REASONS)
- .github/workflows/ci.yml                  (wire supervisor_command_doc_check into supervisor-bridge)
- docs/CONTROLLER_UPDATE_RUNBOOK.md         (D15: pin --checkout in the section-11 start command)
- tools/test_agent_supervisor_launch_seam.py (5 D2 tests; AST reachability test -> enforce_launch_bindings)
- tools/test_agent_supervisor_loop.py       (D8 routing test corrected; D11/D12 + D5-ceiling + D10 tests)
- tools/test_agent_supervisor_recovery.py   (D6 three crash-injection rows + control; D16 sweep test)
- tools/test_agent_supervisor_runner.py     (D4 three-shape presence test)
- tools/test_agent_supervisor_golden_run.py (restart row -> certified single-cycle shape; it previously
                                             passed only via the D10 duplicate-suppression bug)

## 4. Out-of-scope needs (record for the orchestrator)

- NO register defect is deferred; all 17 are corrected. No scope extension is required to complete
  R385.
- claude_runner.py and cli.py are at their EXACT baseline+10% modularity limit (0 headroom). D4 and
  D7(a) fit as net-zero MODIFICATIONS. Any FUTURE substantial change to those two files will need a
  reviewed tools/modularity_exceptions.json entry (that file is NOT in my allowed_paths) or a
  decomposition - flagging for future planning, not blocking this task.
- The ~3h13m R247 recertification is the M0-T127 recert (packet budget note O2); not run in-window.
  Every FAST golden_run class passes.
- The D4 append-only note on M0-T107-amendment20-live-journey-2.md is the ORCHESTRATOR's job per the
  packet; I did not touch that report.

## 5. Self-checks against the packet prohibitions

Confirmed: no live launch; no supervisor CLI write verb against any real checkout; no clear-recovery;
no restart; no repin; the live runtime dir and sqlite journal were never opened; no PR #241 touch; no
policy weakening; no owner-gate or R595/bounded-mode gate change (D8 routes through the existing seam;
D6's classify branch is additive; D7 is presentation/annotation only); broker allowlists untouched.
Both report files are pure ASCII (verified: 0 non-ASCII bytes).

## 6. Requested status

awaiting_gate. ALL 17 register defects (D1-D17) corrected at this one frozen identity per R385, plus
the seven-property foundations, the CI-wired command-document tooth, the D9 next-task machinery,
G4 corrections 1-4 (including correction 3's verdict-persistence and campaign-advancement interruption
rows), R388, and the full R387 sixteen-scenario coverage - all green (2980 supervisor tests + 27 fast
golden_run tests, ruff clean, modularity 0, tooth exit 0). No defect deferred. The only work not run
in-window is the ~3h R247 recert (M0-T127). I do not self-accept; the gates and orchestrator judge
acceptance.
