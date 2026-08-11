# G3 CODE REVIEW — M0-T053

> VERBATIM capture of the independent `code-reviewer` return (session 14, 2026-08-11), preserved by
> the orchestrator under `.claude/rules/project-control.md` report-preservation. Transport decoding
> only; no condensation, no editing. This report is the evidence behind activation-checklist pins
> **P7** (criterion (1) wording) and **P8** (Windows-Job-Object-only deployment narrowing).

VERDICT: PASS (unconditional — no BLOCKING, no REQUIRED-CORRECTION)

Review complete. Commit a387331 vs 37667ff, worktree .claude/worktrees/M0-T053-child-accounting. PR #218 head OID a3873311d4135663cbaa6a6192b2eceaa42d04f1 == reviewed SHA.

WHAT I RAN (verbatim)
- `python -m pytest tools/test_agent_supervisor_*.py -q` in the worktree -> `1493 passed, 2 skipped in 113.99s`. Independently matches the producer and G5.
- Same command in the primary checkout -> `1481 passed, 2 skipped in 114.19s`. I did NOT take the baseline on faith: main is at a398fe8, but `git diff --stat 37667ff..a398fe8 -- tools` is EMPTY, so that tree is byte-identical to base. +12 tests, 0 failures, freeze bar (>=1165) re-established.
- `-k "ProductionChildAccountingTests or ContainmentGateTests"` -> `12 passed, 72 deselected in 1.55s`.
- ruff 0.13.0 on the 4 changed files: base `Found 6 errors`, branch `Found 5 errors`, branch set a strict subset (`os` became used). Whole tools/ tree 46 -> 45. No new lint; one removed. `tools/**` genuinely ungated: ci.yml:187-211 ruff job is `working-directory: services/api`.

YOUR FOUR PRIORITIES
(1) C1 gate — unbypassable and correctly ordered. `containment_precondition()` (cli.py:2189) takes no args and reads exactly one input, `default_containment_kind()`; no flag/env/config key in it or its caller. Called at cli.py:2414, refusal branch cli.py:2446 is the LAST elif before `_run_loop` at cli.py:2466 — after missing-inputs and after the recovery classification. I re-verified the single-call-site claim myself over all non-test tools/: one `ClaudeRunner(` (cli.py:2269), one `SupervisedLoop(` (cli.py:2324), one `_run_loop(` (cli.py:2466), one `run_unit(` (loop.py:1668). I also checked the adjacent knob: `RunnerConfig.use_job_object` (claude_runner.py:313) defaults True and is set from NO cli arg or config anywhere, so there is no config-side way to pass the gate then spawn uncontained. Drove all four host shapes live: job_object->ok=True; taskkill->False; process_group->False; raising source->(False,'unknown').
(2) Activation — nothing. Grepped every added line under tools/agent_supervisor for limited|default_mode|supervised|activate|enable|hold|MODE_: one hit, a docstring citing the pin at cli.py:2198. Only refusals added.
(3) Minimal — yes. +77/-1 claude_runner.py, +61/-1 cli.py, much of it comment. Two helpers, two call sites, one keyword arg, one function, one elif. Producer correctly left 5 pre-existing F401s and a pre-existing Pyright complaint alone. §3 evidence citation present in BOTH packet objective and commit message.
(4) Non-vacuity — real. My sandbox hook blocked programmatic test-runner invocation, so I could NOT re-run the producer's mutation matrix; I say that plainly and verified the guards from the other side by driving production code in memory instead:
  - settle: pre-seeded [stale_orphan, claude_worker]; poll()=None -> both retained; poll()=0 -> [].
  - unwritable journal: `refused with code: child_record_unwritable`, `container calls: ['terminate_all','close']`, `pipes closed: True True True`, `cause chained: OSError`.
  The surviving-child test is genuinely end-to-end (real run_unit, FAKE_MODE=hang, asserts probe_process(pid).determined and .alive, second independent journal connection, real recover_boot -> UNSAFE_OR_DRIFTED). It cannot pass on an unwired launch path.

FINDINGS THAT COULD CHANGE A DECISION (all MINOR, none blocking)
1. MINOR recovery.py:190 — `clear_child_record` wipes the WHOLE list, not this child's entry. Demonstrated: an unrelated live-orphan record is erased by the worker's settle. Currently unreachable (recover_boot refuses first at recovery.py:283-287; clear-recovery cli.py:1571 does NOT touch the record; RunnerError is uncaught by loop.py so no second cycle follows a failed settle). Pin to M0-T056 if it adds any path that starts a run with a pre-existing record.
2. MINOR claude_runner.py:1265-1298 — the C1 refusal is audited, but killing a live worker for an unjournalable pid writes NOTHING to the audit log, though the runner holds `self.audit` and audit.jsonl is a separate file usually still writable.
3. MINOR test_agent_supervisor_runner.py, `test_an_unwritable_child_record_refuses_the_unit` — asserts only the error code. Deleting `container.terminate_all()` (claude_runner.py:1272) keeps the suite green. Behaviour verified present by me; this is a regression-coverage gap only.

WHERE I PUSH BACK — the one thing worth your context
"Doctor parity is structural" (cli.py:2196-2199 and the commit message) is HALF true and should not be recorded unqualified. The gate and doctor share `default_containment_kind()`, so the reported KIND can never diverge. The VERDICTS do diverge: `_check_containment_default()` (cli.py:1102-1129) returns ok=True on POSIX when kind is process_group (line 1124 sets `expected` per-OS) AND ok=True on a Windows host that refuses a Job Object (lines 1119-1123). So on Linux doctor prints `containment_default: ok` while the gate refuses. Direction is safe (gate is stricter), so not a defect — but the pin's criterion (1) is worded "doctor reports containment_default: ok, job_object", and an operator checking only the ok flag on a non-Windows host would wrongly believe criterion (1) was met. Record it as "same containment source", not "doctor parity".

ON G5: I cannot see its three items verbatim, so I will not rubber-stamp them. If they are the achieved-per-cycle containment (R4), the unaccounted model-probe child (R2), and audit/observability, I concur on all three and add mine 1-3 above. Two things I would want in the pin that G5 may not have covered: the uncontained `doctor --live` preflight probe (preflight.py:126, cleanup is a bare `process.kill()` at 150/184, no ProcessContainer at all — pre-existing, reached only from cli.py:1203, but that is exactly the command an operator runs on the pinned host at activation), and renaming the start payload key `containment` (cli.py:2424) which reads as achieved containment but is the host precondition.

On R4 specifically, I judge deferral DEFENSIBLE, not a false sense of enforcement: the payload and refusal text say "default" containment throughout and never claim an achieved guarantee, and C2 materially covers the gap C1 leaves — if `adopt` degrades (process.py:558-577) and the supervisor is then killed, the worker pid is now journaled so the next start refuses. Before this task neither mechanism worked in production; now they are complementary rather than one inert. Enforcing criterion (2) means stopping the loop mid-run, which is the loop-behaviour change §1 forbids here.

TWO OPERATIONAL NOTES FOR MERGE
- The gate is unconditional on mode, so `start` now hard-refuses on EVERY POSIX host including Render, and including shadow (shadow does spawn a real worker — the new CLI test observes a real record-and-clear in --mode shadow). That matches the pin's "any run that spawns a live worker" and breaks nothing today, but the supervisor is now Windows-job-object-only.
- The commit carries 2 files under .claude/agent-memory/backend-engineer/ while the packet's forbidden_paths lists `.claude/**`. The standing rule in .claude/rules/project-control.md permits agent-memory writes and the content is benign, so I read it as the carve-out — but M0-T057 just landed an allowed_paths guard, so confirm acceptance does not trip on them.
