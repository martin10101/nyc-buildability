# M0-T052 — G5 security review (verbatim reviewer return)

Saved verbatim by the orchestrator from the independent security-reviewer agent's return channel
(2026-08-08; reviewer model claude-opus-4-8 effort xhigh; transport entity-decoding only).
Reviewer preamble: "I have completed my independent analysis. All evidence is gathered and
verified. Here is my G5 security gate report."

---

# Gate Report

- **Gate ID:** G5 (security) — M0-T052
- **Task ID:** M0-T052 (B-018 stranded-START_CLAUDE crash-window fix)
- **Reviewer:** security-reviewer (independent, read-only; ADR-005)
- **Producer:** (author of commit 867b1bf; producer ≠ reviewer confirmed)
- **Result:** PASS (with BLOCKING required corrections — see Required rework)
- **Clean environment/worktree used:** Yes. Frozen worktree `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t052`, branch `task/M0-T052-start-reentry`, HEAD `867b1bfbfaeefeabe8be64ebf2f4b808acc56a7d` (verified via `git rev-parse HEAD`). Python 3.11.

## Acceptance criteria reviewed

The change admits `START_CLAUDE` to `CYCLE_ENTRY_STATES` so an externally-killed launch stranded at `START_CLAUDE` can be resumed by an operator `start` through the existing `recover_boot` → `SAFE_CHECKPOINT` gate, instead of being permanently refused with `bad_cycle_entry_state`. I re-derived the root cause and the fix path from source rather than the producer report, and answered the four assigned security questions from the code. Diff scope (`loop.py`, two test files, the producer report) is within the supervisor defect lane and `tools/test_agent_supervisor_*.py`; no out-of-scope files touched.

## Directive/requirement verification

The task packet and control-plane `requirements.json` for source-024 live on `main` and are not present in this worktree (branch cut from `de2e647`, before source-024 capture). I re-derived compliance from the verbatim owner directive in the main checkout at `project-control/directives/D-010-autonomous-engineering-restructure/source-024-amendment.md`. The atomic per-row (D-010-R237..R241) PASS/FAIL is the independent `directive-compliance-verifier`'s responsibility (verification.json); below I verify against the verbatim owner text.

| Requirement (from verbatim source-024) | Reviewed at | Verdict | Reproduced evidence |
|---|---|---|---|
| Narrow root cause of the stranded START_CLAUDE recovery window | 867b1bf | PASS | Root cause confirmed in `loop.py:1604-1611` (entry guard) + `loop.py:1650-1661` (CLAUDE_RUNNING committed only after `run_unit` returns); pre-fix `CYCLE_ENTRY_STATES` omitted `START_CLAUDE`. |
| Smallest durable fix; no supervisor redesign | 867b1bf | PASS | Single constant `loop.py:137` + rationale comment + tests only. No control-flow, authority, or state-table change. |
| Recover through an authorized deterministic path without owner each time | 867b1bf | PASS | Resume flows through operator `start` → `recover_boot` SAFE_CHECKPOINT gate (`cli.py:2351-2374`); no owner-in-the-loop step added. |
| Do not broaden into redesign / no new dispatch authority | 867b1bf | PASS (with SEC-MAJOR residual, below) | Sole production launch path unchanged: `cmd_start`→`_run_loop`→`loop.run`→`run_cycle` (only callers `cli.py:2396`, `cli.py:2304`, `loop.py:2362`). |
| AD-093 qualifying-evidence citation duty (supervisor-freeze §3) | 867b1bf | PASS | B-018 (unresolved crash/recovery) cited in both commit message and `project-control/reports/M0-T052-producer-report.md`. |

## Steps independently executed

- `git show 867b1bf` / `--stat` — reviewed the full diff (4 files, +479/-3).
- `python -m pytest tools/test_agent_supervisor_start_reentry.py tools/test_agent_supervisor_loop.py::CycleEntryStateTests -q` → **13 passed in 0.82s**.
- `python -m pytest tools/test_agent_supervisor_*.py -q` → **1402 passed, 2 skipped in 99.74s** (matches the freeze baseline 1392/2 + exactly the 10 new tests; 0 failures — no regressions).
- Read and traced: `loop.py` (run_cycle 1579-1699, run 2334-2421, entry constant 114-137), `cli.py` (cmd_start 2307-2439, _run_loop 2188-2304, cmd_resume_pending_prompt 1614+), `recovery.py` (full), `process.py` (ProcessContainer 505-621), `claude_runner.py` (run_unit launch 940-1139), `locking.py` (assess/acquire 182-296).
- Grep for `record_launched_child` / `clear_child_record` / `CHILD_PROCESSES_KEY` repo-wide (excluding tests) and `SupervisedLoop(` / `.run(` / `run_cycle` callers.

## Expected versus actual

| Security question | Expected (safe) | Actual (verified from code) |
|---|---|---|
| Q1 double-launch/zombie | All four mechanisms close each sub-window | **Partially.** SAFE_CHECKPOINT gate and single-instance lock are solid and fail-closed. **Child-accounting is inert in production** and **kill-on-close is platform-conditional** → residual double-launch window on non-Job-Object hosts (SEC-MAJOR). |
| Q2 authority surface | No caller reaches a launch without operator start + SAFE_CHECKPOINT; shadow/broker/limited-auto unaffected | **Confirmed.** No new caller; sole path stays gated. limited-auto refused by name (`cli.py:2316`) and excluded from `RUNNABLE_MODES` (`loop.py:106`). Shadow forwards-nothing unchanged (`loop.py:2367-2372`). `cmd_resume_pending_prompt` dispatches nothing. |
| Q3 journal integrity on re-entry | START_CLAUDE resume runs the same integrity/audit-chain verification as any entry | **Confirmed.** `cmd_start` runs `journal.integrity_check()` + `audit.verify_chain()` + `recover_boot` and feeds `.ok` into revalidation **before** `_run_loop`, independent of entry state (`cli.py:2330-2352`). The `if entry == PREFLIGHT` block only does a state transition, not verification. Nothing is skipped. |
| Q4 fail-closed preservation | UNSAFE_OR_DRIFTED / AMBIGUOUS_EFFECT still refuse dispatch from a stranded START_CLAUDE; tests non-vacuous | **Confirmed with one caveat.** `classify()` (`recovery.py:258-330`) + gate (`cli.py:2374`) refuse on failed/missing revalidation, lock failure, competing writer, unaccounted child, and pending effect. Tests prove competing-writer, pending-effect, and the positive control non-vacuously. **Caveat:** the surviving-*recorded*-child fail-closed is proven only for a manually-recorded child, which production never creates (see SEC-MAJOR). |

## Evidence paths

- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t052/tools/agent_supervisor/loop.py` (137, 114-136, 1604-1611, 1625-1628, 1630-1640, 1650-1661, 2334-2362)
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t052/tools/agent_supervisor/cli.py` (2188-2209, 2307-2414 esp. 2374)
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t052/tools/agent_supervisor/recovery.py` (155-191, 258-330, 443-504)
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t052/tools/agent_supervisor/process.py` (521-621)
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t052/tools/agent_supervisor/claude_runner.py` (940-1139)
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t052/tools/agent_supervisor/locking.py` (182-296)
- `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t052/tools/test_agent_supervisor_start_reentry.py`, `.../tools/test_agent_supervisor_loop.py`

## Human-style walkthrough findings

Not a UI task. Behavioral walkthrough (traced through code + tests): a fresh `StateMachine` reads `START_CLAUDE` from the journal after a kill (`test_the_strand_is_durable_and_read_from_the_journal`); `run_cycle` from `START_CLAUDE` dispatches exactly once and transitions to `CLAUDE_RUNNING` (`test_run_cycle_from_start_claude_dispatches_exactly_once`); resume commits no duplicate `preflight_pass` (`test_resume_does_not_re_record_the_preflight_transition`); production entry `loop.run()` completes legally from `START_CLAUDE` in both shadow and supervised paths. All observed as designed.

## Regression/security/provenance findings

**[SEC-MAJOR] Newly-reachable double-launch / duplicate-in-flight-effect window on any host without live kill-on-close containment.**
Anchors: `loop.py:137`, `loop.py:1650-1661`; `recovery.py:155-191`; `process.py:521-608`; `cli.py:2351-2374`.

The resume protection against launching a second worker while a first survives depends, per the producer report and the permanent code comment (`loop.py:129-132`, "a resume can never double-launch or run over an unaccounted worker"), on `recover_boot`'s child-accounting. I verified two facts that break that claim in production:

1. **Child-accounting is inert in production.** `record_launched_child` (`recovery.py:181`) has **no production caller** — repo-wide it is referenced only in `recovery.py`, `test_agent_supervisor_recovery.py`, and `test_agent_supervisor_start_reentry.py`. The runner spawns the worker via `subprocess.Popen` and `container.adopt(pid)` (`claude_runner.py:965-971`) but never records the pid in the journal. Therefore `account_for_children` (`recovery.py:161`) always reads an empty list in production, and `classify()` can never flag a real surviving worker. The test `test_a_surviving_recorded_child_forbids_the_resume` manually records a child that production never records — it validates a code path that production does not exercise.

2. **Kill-on-close is platform-conditional, not fail-closed.** The automatic parent-death kill exists ONLY for the Windows Job Object (`process.py:524-533`, `WindowsJobObject` kill-on-close). The `taskkill` fallback (Windows without job) and the POSIX `process_group` containment (Linux/Render) terminate the worker only via `terminate_all()`/`close()`, which run **inside the runner's `finally` block** (`claude_runner.py:1076-1099`, `process.py:581-599`). An *external* kill of the supervisor (SIGKILL/OOM/taskkill on the process, container restart) skips `finally`, and there is no `PDEATHSIG`, so the worker **survives**. `cmd_start` has **no fail-closed containment gate** — it will build and run the loop under any containment kind.

Consequence: the exact B-018 trigger (external kill during the `START_CLAUDE` window, which spans the entire `run_unit` execution) on a non-Job-Object host leaves a live orphaned worker; the next operator `start` classifies `SAFE_CHECKPOINT` (nothing recorded, stale lock taken over, revalidation passes) and dispatches a **second** worker. Before this change the same scenario was refused (`bad_cycle_entry_state`), so the change is what makes this reachable. Partial mitigations that remain: `AMBIGUOUS_EFFECT` reconciliation catches *modeled* pending external effects (`recovery.py:298-306`), and a broken stdin/stdout pipe will often kill the orphan — but neither is a guarantee, and neither is the mechanism the report claims.

**[SEC-MINOR] Incorrect safety invariant baked into permanent supervisor code and the producer report.** `loop.py:129-132` and the producer report assert child-accounting fails closed "if any recorded child SURVIVED the crash," presented as the live double-launch guarantee. Because no child is ever recorded in production, this clause is dormant; the operative guarantee is platform kill-on-close. A permanent comment on the code that launches the live worker should not assert an invariant the runtime does not hold.

**[INFO] Confirmed-solid, fail-closed layers (no defect).** The `SAFE_CHECKPOINT` gate (`cli.py:2374`), the single-instance lock (`locking.py:191-296`: `assess()` refuses takeover on undetermined liveness and on a live owner; `acquire()` refuses a takeover race), integrity/audit-chain revalidation, and the "missing check is a failed check" rule (`recovery.py:277-280`) all hold. A competing *supervisor* is caught by the lock; the residual is specifically an orphaned *worker*, which holds no lock. `cmd_start` does not pass `competing_writer` to `recover_boot` — correct, since competing-supervisor detection is the lock's job.

## Defects

No functional defect in the diff itself; the fix is minimal and behaves as specified, and the full suite is green (1402/2/0). The SEC-MAJOR finding is a residual safety window that the change *exposes* (does not itself create the wiring/containment gap) plus an inaccurate safety rationale (SEC-MINOR).

## Required rework

Recorded as PASS with corrections; these are BLOCKING for acceptance and for activation of SUPERVISED-AUTO per project-control gate-verdict semantics:

- **C1 (must pin to the M0-T036 activation record):** SUPERVISED-AUTO may run **only** on a host where `doctor`'s `containment_default` check verifies `CONTAINMENT_JOB_OBJECT` (live kill-on-close). On any POSIX host (incl. Render) or a Windows `taskkill` fallback, the `START_CLAUDE` resume can double-launch over an orphaned worker. Add this as a hard, fail-closed precondition (ideally enforced in the `start` launch path, not merely reported by `doctor`).
- **C2 (must pin + follow-up task):** Child-launch accounting is not wired to the production launch path; the `recover_boot` surviving-child fail-closed is therefore inert. Open a bounded follow-up (defect-lane, cites this G5) to call `record_launched_child` at worker spawn and `clear_child_record` on clean exit, so double-launch protection does not rest on kill-on-close alone.
- **C3:** Correct `loop.py:129-132` and the producer report to state the actual operative guarantee (platform kill-on-close) and to stop asserting the dormant child-accounting invariant.

## Reviewer conclusion

The diff is the smallest durable fix the owner ordered (D-010 source-024): one entry-state admission that makes a live-reproduced, previously-unrecoverable crash window recover through the existing operator-`start` + `SAFE_CHECKPOINT` deterministic path, with no redesign. It does **not** widen who may dispatch (Q2), skips **no** integrity/audit-chain verification on re-entry (Q3), and preserves the `UNSAFE_OR_DRIFTED`/`AMBIGUOUS_EFFECT` fail-closed refusals with non-vacuous tests (Q4). The full supervisor suite is green with no regressions. On the sole verified live configuration (owner Windows 11 + Job Object kill-on-close, `doctor` all-conditions PASS), the double-launch window is closed.

However, the four mechanisms named in the assignment do **not** all close each sub-window (Q1): child-accounting is inert in production and kill-on-close is platform-conditional, leaving a real double-launch/duplicate-effect residual on non-Job-Object hosts — a residual the producer report and a permanent code comment misrepresent as covered.

**Residual pinning: YES — required.** C1 and C2 MUST be pinned to the M0-T036 activation record before SUPERVISED-AUTO is used on any host; C3 corrects the record. Because the residual is not reachable on the verified live host and is a pre-existing platform/wiring gap merely exposed by the minimal ordered fix, this does not block the fix itself.

**VERDICT: PASS**

---

# Delta attestation (verbatim reviewer return, 2026-08-08; same G5 reviewer agent; transport entity-decoding only)

Delta verified. Every changed line in `loop.py` is a `#:` comment (the non-comment diff filter returned empty); the operative constant `CYCLE_ENTRY_STATES = frozenset({PREFLIGHT, START_CLAUDE, CLAUDE_RUNNING})` is byte-identical (moved from line 137 to 143 only because 6 comment lines were inserted above it); the report change is a pure append that preserves the original text. Focused tests still pass (13 passed) at 6a61c6b.

---

# Gate Report — Delta Attestation (M0-T052 G5)

- **Gate ID:** G5 (security) — M0-T052, delta attestation for correction commit
- **Reviewer:** security-reviewer (independent, read-only; ADR-005)
- **Frozen reviewed SHA (original):** 867b1bf — verdict PASS-with-corrections
- **Correction SHA attested:** 6a61c6b (current worktree HEAD, confirmed via `git rev-parse HEAD`)
- **Result:** PASS-STANDS

## Delta independently executed

- `git diff 867b1bf..6a61c6b --stat` → 2 files, +25/-3: `loop.py` (+12/-3), producer report (+16).
- `git diff 867b1bf..6a61c6b -- tools/agent_supervisor/loop.py | grep '^[+-]' | grep -v '^[+-]#:'` → **empty** (every added/removed loop.py line is a `#:` comment; zero code lines changed).
- `git show 6a61c6b:tools/agent_supervisor/loop.py | grep CYCLE_ENTRY_STATES` → `CYCLE_ENTRY_STATES: frozenset[str] = frozenset({PREFLIGHT, START_CLAUDE, CLAUDE_RUNNING})` at line 143 — semantics unchanged.
- `python -m pytest tools/test_agent_supervisor_start_reentry.py tools/test_agent_supervisor_loop.py::CycleEntryStateTests -q` at 6a61c6b → **13 passed in 1.03s**.
- Producer-report delta is an appended "## G5 C3 correction" section; original body preserved unchanged (report-preservation rule honored).

## Expected versus actual

- **Expected:** exactly the C3 comment/report correction, zero behavioral change.
- **Actual:** confirmed. No control-flow, constant, state-table, authority, or gate change. The rewritten `loop.py:127-142` comment now states the honest limit accurately: the operative guarantee against resuming over an orphaned worker is platform kill-on-close (Windows Job Object); `recover_boot`'s surviving-child check fails closed for RECORDED children only; the production launch path does not yet record children (M0-T053 follow-up); and on a host without live kill-on-close (POSIX or Windows `taskkill` fallback) a `START_CLAUDE` resume is NOT double-launch-safe and is barred by the activation-record pin. The SEC-MINOR overstated invariant is fully removed.

## Answers to the coordinator

**(a) Verdict at 6a61c6b: PASS-STANDS.** The correction is comment-and-report-only with no behavioral change; the original G5 PASS (fix is minimal, no authority widening, no integrity skip, fail-closed preserved, suite green) is unaffected and the SEC-MINOR (C3) is now resolved.

**(b) C1/C2 handling — satisfies the intent, with one emphasis.**
- **C3:** fully satisfied (verified above).
- **C2:** satisfied — M0-T053 contracted to wire `record_launched_child`/`clear_child_record` plus the fail-closed launch-path containment gate and tests, citing this G5. Correctly bundling the C1 code enforcement into M0-T053 is acceptable.
- **C1:** the intent (bar activation on non-kill-on-close hosts) is met as a *written* precondition backed by live evidence. The one emphasis: my C1 asked that the bar ideally be enforced *in the `start` launch path, not merely reported by `doctor`*. Until M0-T053 lands that code gate, `doctor` is advisory/out-of-band and the only active control is the written pin plus operator discipline. That is adequate for the single verified live Windows host but must not be read as a fail-closed runtime guarantee. This interim state must itself be stated on the pin.

**Wording I would require on the activation-record pin (C1):** key the bar on the *per-launch* audit line, not only the one-time `doctor` snapshot — because `ProcessContainer.adopt` degrades honestly to `taskkill` if `AssignProcessToJobObject` fails at launch time (`process.py:567-574`), so a host that passes `doctor` can still produce a non-job launch. Suggested text:

> SUPERVISED-AUTO — and any run that spawns a live worker — may be activated/run ONLY on a host where BOTH (1) `doctor` reports `containment_default: ok, job_object` AND (2) the run's own worker-launch audit records `containment: job_object` for that cycle. If either the `doctor` snapshot or a live launch reports `taskkill` or `process_group`, activation/continuation is REFUSED. Rationale: a supervisor externally killed during the `START_CLAUDE` window leaves an orphaned worker that `recover_boot` cannot detect (the production launch path does not record child pids until M0-T053), so an operator `start` would double-launch over the live worker. Until M0-T053 lands the fail-closed launch-path containment gate, this bar is a WRITTEN precondition only (not runtime-enforced); the live `containment: job_object` audit line MUST be re-verified on every activation.

The live evidence cited (doctor `containment_default: ok, job_object` + cycle-1 worker-launch audit `containment: job_object`) matches criteria (1) and (2) and is sufficient for the current activation on this host.

**VERDICT: PASS**
