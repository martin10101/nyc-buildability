# M0-T056 — G3 DELTA re-review (VERBATIM reviewer return, reviewed_sha a90ac19)

Independent reviewer: `code-reviewer` (read-only; reviewer != producer). Returned via agent channel; saved verbatim.
Supersedes the 8196039 G3 for acceptance at the reworked identity a90ac19.

---

# GATE REPORT — M0-T056 (G3 DELTA re-review)

- **Task:** M0-T056 — R595 production turnover actuation
- **Reviewed SHA:** `a90ac1917fc9baa1a703e388cf726b709eaa4cd6` (HEAD of `control/session16-codex-golive`)
- **Baseline (prior PASS):** `8196039`
- **Scope:** delta only (B, C) + the A (P1) audit. Reviewer read-only; ran no write commands.

## Delta contents
`git diff 8196039 a90ac19 --stat` = **3** files, +76/-4:
- `tools/agent_supervisor/worker_turnover.py` — +4/-3 (docstring only)
- `tools/test_agent_supervisor_r595_actuation.py` — +57 (new `ContainmentVerifiedGateTests`, 3 tests)
- `docs/SESSION_HANDOFF.md` — +16/-1 (orientation-only narrative)

The two **code** files = 61 insertions / 3 deletions, matching the packet. The third is `docs/SESSION_HANDOFF.md`, a non-code orientation doc (ledger wins on conflict). Not material, not a defect — noted for transparency.

## 1. B — new tests are non-vacuous — PASS
- `ContainmentVerifiedGateTests(LoopSeamTestBase)` reuses the proven integration harness. `build()` constructs a **real** `lp.SupervisedLoop`; `loop.run_cycle(...)` invokes the **real** `run_cycle` (`loop.py:1604`). Only the runner (`FakeRunner`, scripted `RunResult`) and reviewer are injected at the correct seam boundary; the `StateMachine`, `DurableJournal` (real sqlite), and `AuditLog` are real. **Not a stub.**
- The unverified test builds `RunResult(returncode=0, checkpoint=valid, containment="job_object", containment_verified_in_job=False)`. Traced: valid checkpoint + `run_result.ok==True` passes the S14 gate (`loop.py:1689`); `achieved=="job_object"` passes the degraded gate (`1770`); then `verified_in_job is False` at `loop.py:1804` → `stop("containment_unverified", …, PAUSED_RECOVERY)` (`1820`). Assertions `stopped=="containment_unverified"` and `reached_state==sm.PAUSED_RECOVERY` are exact.
- Default (field unset → `True` default) and explicit `True` assert **not** tripped.
- **TEETH (confirmed by reasoning):** `"containment_unverified"` as a stop code is produced **only** at `loop.py:1813/1816/1820` (grep-verified; single `stop(...)` call site). Neuter/remove the `if verified_in_job is False:` block and a `verified_in_job=False` cycle falls through to `CHECKPOINT_RECEIVED` (`1822`) → the test FAILS on both assertions. Real teeth, localized to the M0-T060 branch.
- **Reproduced:** `python -m pytest tools/test_agent_supervisor_r595_actuation.py -q` → **19 passed** (Python 3.11.9).

## 2. A audit (P1) — sound; AGREE per site
No termination-path change was made (§4). Independently read all 5 `container.terminate_all()` sites in `claude_runner.py`:
- **1114** (watchdog wall-timeout/cancel): kill of a **recorded** worker; return value discarded; reaped by the finally-block `process.wait()`. No false "terminated" boolean feeds a subsequent `start`. **AGREE.**
- **1198** (graceful-close-failed): kill of the **recorded** worker after the close grace (`process.wait(close_grace)` at 1190), then unbounded `process.wait()` at 1204; record settled only on verified exit. **AGREE.**
- **1311** (record-write-failure refusal — the M0-T058 fix): captures `killed = container.terminate_all()`, bounded `process.wait(CHILD_KILL_REAP_SECONDS)`, raises distinct `child_record_unwritable_orphan_live` (1338) iff neither killed nor reaped — explicitly prevents the next `start` from double-launching. **AGREE.**
- **1522 / 1561** (`_probe_model_launch`, backing `make_launch_probe`): a throwaway probe on a **local** `ProcessContainer` that is **never recorded** and returns a `(available, reason)` tuple, not a live worker/successor; bounded by its watchdog + `process.wait(timeout=10)`; return discarded. A discarded boolean cannot double-launch a worker; off the M0-T056 actuation successor path (pre-existing pin P5 recommendation). **AGREE.**

The actuation successor path (`OrchestratorWatchdog` / worker-turnover controller) gates on containment + the M0-T053 child-accounting probe (`BLOCKED_SURVIVOR`), not on any `terminate_all` boolean. Producer's conclusion is correct.

## 3. C — docstring corrected, code byte-unchanged — PASS
Diff is entirely inside the `default_actuation_authorization` docstring; now names `turnover_actuation_authorized`/`ACTUATION_AUTHORIZATION_ATTR`. Executable body unchanged: `return getattr(config, ACTUATION_AUTHORIZATION_ATTR, False) is True` (`worker_turnover.py:100`).

## 4. loop.py / claude_runner.py byte-unchanged — CONFIRMED
`git diff 8196039 a90ac19 -- tools/agent_supervisor/loop.py tools/agent_supervisor/claude_runner.py` → **empty**.

## Regression / provenance
Freeze-safe (defaulted field True → pre-existing RunResults proceed unchanged; real runner sets it from `containment_report.verified_in_job`). Change stays inside `tools/agent_supervisor/**` + its test.

## Defects
None.

**VERDICT: PASS**
