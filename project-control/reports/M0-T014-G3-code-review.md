<!-- Verbatim reviewer return (agent-return channel; agentId aa63b966a97835e5f, code-reviewer, 2026-07-17). Saved by the orchestrator per the report-preservation rule. Contains BOTH the G3 verdict and the G4 integration/regression verdict. -->

# GATE REPORT — M0-T014 G3 (independent walkthrough) + G4 (integration/regression)

- **Task:** M0-T014 — Project-control CLI hardening (owner code-audit P0)
- **Producer:** backend-engineer | **Reviewer:** code-reviewer (independent; did not implement)
- **Target:** branch `task/M0-T014-control-hardening` @ `3e5e6e5`, worktree `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T014`
- **Method:** started from the packet (`project-control/tasks/M0-T014.json`), not the producer report; read every branch of `tools/project_control.py` adversarially; ran the full suite myself; independently re-derived the ledger scans the producer claimed; verified CI read-only via `gh`.
- **Scope check:** diff touches exactly the three allowed paths (`tools/project_control.py`, `tools/test_project_control.py`, `project-control/reports/M0-T014-producer-report.md`). No forbidden path touched. Base is current main (`d61c9b6`).

## Reproduced evidence

| Command | Result |
|---|---|
| `python tools/test_project_control.py` (in worktree) | **EXIT=0** — all 9 groups green: original 15-check workflow, S1–S7, docs honesty; "115 real ledger files parse" |
| `gh pr checks 4` (read-only) | ALL pass: secret-scan, api (ruff+pytest), contracts, **control-plane (workflow regression test, ADR-005)**, web, web-e2e — runs 29595273085 (PR) and 29595249937 (push) |
| Independent ledger scan (my own script, not the producer's) | 30/30 task ids match `^M\d+-T\d{3}(-R\d+)?$`; blocker statuses = {open, resolved, resolved_temporary, closed}; no open blocker (B-001/B-004/B-006/B-008) word-matches any non-accepted task id via the tool's own `_blocker_references` |

## Scenario-by-scenario

| Scen | Expected | Actual | Evidence |
|---|---|---|---|
| S1 transition enum | progress can never set `accepted`/`claimed`; illegal jumps rejected; legal paths + blocked-unblock pass | **PASS.** `PROGRESS_TRANSITIONS` (project_control.py:92–103) is an explicit closed enum; `accepted` excluded from argparse choices (:600) AND in-code defense (:313–315); `claimed` claim-only (:317–318); terminal states immutable across claim/progress/submit/gate (:290, :308, :341, :372). Unblock set `blocked→{backlog,ready,in_progress,awaiting_gate}` (:100) keeps ledger M0-T007/T008 (blocked, producer null — verified in real ledger) resumable. Test: 15 legal + 25 illegal pairs, each asserting status unchanged on rejection (test:220–255) | suite EXIT=0; test_s1_transitions |
| S2 accept preconditions | each of the four individually enforced; no bypass constructible | **PASS.** accept() (:458–523): orchestrator-only (:459), awaiting_gate (:465), every required gate PASS with independence re-check (:474–489), deps accepted incl. missing-file/invalid-id fail-closed (:490–500), blockers open-or-missing-status fail-closed incl. unreadable JSON (:501–513). Bypass attempts I traced: gate-file glob cannot cross-match rework ids (`M0-T005-G*` ∌ `M0-T005-R1-G3.json`); `--gates` garbage at new-task fails closed (unrecordable gate → never acceptable); self-dependency deadlocks closed; only `accept()` in the entire file ever writes `status: accepted` | test_s2 + my code trace |
| S3 gate classes (OWNER-CRITICAL) | G2 = orchestrator/self_check stored honestly; self_check never satisfies independent gates; independent gates need rostered reviewer ≠ producer; NO general bypass | **PASS.** gate() (:377–400) is an exhaustive if/elif/else partition over argparse-restricted G0–G7: SELF_CHECK={G2}, ADMIN={G0,G7}, else=independent — no default-permit, no flag (argparse has no `--force/--skip/--override/--no-check`, asserted test:546–548). G2 stores `role: "self_check"` (:382, verified test:501–503). Independent: empty roster rejected (:394–396), unrostered rejected (:397–399), producer rejected even when rostered (:391, test:474–480). Accept-time: forged `self_check` and `administrative` records both rejected for independent gates (:481–486, test:521–543); the elif chain at :479–489 does evaluate reviewer==producer for both `independent_review` and legacy role-None records — verified by trace | test_s3 + my branch-by-branch read |
| S4 containment | task-id regex; report paths confined; traversal/absolute/drive escapes rejected | **PASS.** `task_path()` refuses unvalidated ids (:171–175); `validate_report_arg` (:181–211) rejects drive (`C:\`, drive-relative `C:x` via `PureWindowsPath.drive`), UNC, POSIX-absolute, any `.`/`..` component, splits on both separators, then double-checks with `resolve().is_relative_to(reports_root)` (catches symlink escape). My mental attacks (`project-control/reports` exactly 2 parts, trailing-slash, case-mismatch, `\\srv\share`) all land in reject branches. 12 bad ids × 6 subcommands + 11 bad report paths tested with task-dir byte-identity assertion (test:567–605) | test_s4 |
| S5 atomicity | temp+`os.replace` on ALL writes; real concurrency test | **PASS.** Single `save()` (:141–159, mkstemp in dest dir → replace-with-retry → unlink on any failure) is the only write path for every JSON write (grep confirms no other `write_text`/`open(...,'w')` in the tool). Concurrency test is real: 8 concurrent OS subprocesses (test:654–667), plus interrupted-replace simulation proving previous bytes intact + temp cleaned (test:669–698). Producer's D1 (Windows read-side PermissionError race) is a genuine find, fixed with bounded read retry (:117–126) | test_s5, EXIT=0 |
| S6 spoofing negatives | all present, each asserting rejection | **PASS.** Producer self-accept, producer self-gate, renamed unrostered reviewer, percent 100, `--status accepted`, terminal demotion via submit/gate/claim — each asserts `returncode != 0` and state-unchanged where relevant (test:709–757) | test_s6 |
| S7 backward compat | full suite green; real ledger parses; 21 accepted unaffected; validate-on-write only | **PASS.** I ran the suite myself: EXIT=0; S7 copies the real ledger to temp (never executes against the live ledger — ADR-005 clean), parses 115 files, `status` shows ≥21 accepted, write-probe on a real backlog task succeeds, legacy role-less records (incl. G3 by an unrostered legacy reviewer, `dependencies: null`, backslash report paths) still accept (test:765–831) | my run, EXIT=0 |

## Producer report §10 — six behavior changes, evaluated against the live ledger

1. **G4 needs rostered reviewer** — correct and safe: M0-T014's own roster (code-reviewer, security-reviewer) covers it; I (code-reviewer) issue G4 below. All backlog packets (M0-T015, M1-T008/T009, M2-T002/003/004) have workable rosters — verified. **Exception: see D-OBS-3.**
2. **Report-path containment** — safe: enforced on write only; stored legacy `docs/research/...` values untouched (S7 proves).
3. **Claim requires ready/rework** — safe: G0 PASS auto-promotes backlog→ready (:425–427), matching current practice.
4. **Submit origin states** — safe; note it still permits `claimed→awaiting_gate`, skipping the self_check *status* (OBS-1 below).
5. **Terminal immutability** — correct (closes a real pre-existing demotion hole), but changes the post-acceptance re-check pattern (OBS-2).
6. **Accept verifies deps/blockers/status** — verified against the live ledger with the tool's own matcher: **no pending task is currently trapped**; the dep chain M1-T009/M2-T002 → M2-T003 → M2-T004 matches the owner-approved critical path and is acceptable in order.

## Defects / observations (owner rule: everything reported)

No contract-breaking or architectural defect found. **Zero BLOCKING defects.** Non-blocking observations:

- **OBS-1 (low):** `SUBMITTABLE_STATUSES` includes `claimed`/`in_progress`, so the `self_check` *status* can be skipped en route to awaiting_gate. The G2 gate record still enforces self-check evidence at accept, and this preserves original-suite semantics. Not a packet violation.
- **OBS-2 (low, operational):** terminal immutability means post-acceptance gate re-checks (the M0-T013/B-007 G5-re-check pattern) can no longer be recorded as gate records on the accepted task — future re-checks need a new task id or checkpoint. Producer flagged this (§10.5); orchestrator should internalize it.
- **OBS-3 (medium, operational — action needed at resume, not at merge):** ledger tasks **M0-T007/M0-T008** are blocked with `reviewer_agents: []` and require G3/G4/G5. After merge, their independent gates **cannot be recorded at all** until the orchestrator amends those packet rosters (no CLI subcommand edits `reviewer_agents` on an existing task). Unblock/claim paths themselves work; only gating is affected. Recommend amending rosters when those tasks resume.
- **OBS-4 (low, disclosed):** accept-time independence checks stored `role`+`reviewer` only; roster membership is write-time-only (deliberate, to avoid retro-rejecting ledger G3/G4 history). A hand-forged gate file with `role: "independent_review"` and an unrostered reviewer would satisfy accept — but no CLI path can produce such a record, and the threat model is explicitly procedural (honestly documented in the tool). Disclosed by producer (§8.2).
- **OBS-5 (low):** `new-task --gates` accepts arbitrary strings (e.g., `G9,X`); fail-closed (such gates are unrecordable, so the task can never be accepted) but a validation message would be cleaner. Blocker status `"reopened"` would NOT block acceptance — reopening must use status `open`.
- **OBS-6 (cosmetic):** corrupted task JSON or NUL-byte arguments surface as raw tracebacks (nonzero exit — still a rejection) rather than clean `fail()` messages.

## Verdicts

**G3 verdict: PASS**
**G4 verdict: PASS** — full local suite EXIT=0 on the worktree at `3e5e6e5` + all PR #4 CI jobs green (push run 29595249937, PR run 29595273085, secret-scan 29595249905/29595274748), including the unchanged `control-plane` job invocation (`python3 tools/test_project_control.py`, `.github/workflows/ci.yml`); S7 proves contract compatibility with all 115 live ledger files and the 21 accepted tasks.

Merge note for the orchestrator (packet risk #2): merge at a quiet ledger point and note OBS-2/OBS-3 before the next gating cycle; M0-T014's own G4 record must be written with reviewer `code-reviewer` (this review) or `security-reviewer`.

Key files: `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T014\tools\project_control.py`, `...\tools\test_project_control.py`, `...\project-control\reports\M0-T014-producer-report.md`.
