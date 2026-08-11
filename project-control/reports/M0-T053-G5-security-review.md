# G5 SECURITY REVIEW — M0-T053

> VERBATIM capture of the independent `security-reviewer` return (session 14, 2026-08-11), preserved
> by the orchestrator under `.claude/rules/project-control.md` report-preservation. Transport
> decoding only; no condensation, no editing. (A first write attempt was lost to a shell heredoc
> quoting failure; this is the reviewer's text, written directly.)

VERDICT: PASS

G5 SECURITY REVIEW — M0-T053, commit `a387331` vs base `37667ff`, worktree `.claude/worktrees/M0-T053-child-accounting`. Analysis is COMPLETE (not a partial review). No BLOCKING finding. Three items are REQUIRED-CORRECTION **before M0-T056 actuation**, and explicitly do NOT block acceptance of M0-T053 — recommend pinning them into the ACTIVATION-CHECKLIST exactly as M0-T052's C1/C2 produced this task.

## COMMANDS I RAN, VERBATIM (Python 3.11.9, in the worktree)

```
$ python -m pytest tools/test_agent_supervisor_*.py -q
1493 passed, 2 skipped in 113.85s (0:01:53)

$ python -m pytest tools/test_agent_supervisor_*.py -q -k "not ChildAccountingTests and not ContainmentGateTests"
1477 passed, 2 skipped, 16 deselected in 113.88s (0:01:53)

$ python -m pytest tools/test_agent_supervisor_*.py -q --collect-only      -> 1495 tests collected
$ ... -k ProductionChildAccountingTests --collect-only                     -> 6/68
$ ... -k ContainmentGateTests --collect-only                               -> 6/16
$ ... test_agent_supervisor_recovery.py -k ChildAccountingTests --collect-only -> 4/55
```

Producer's headline (1493/2) REPRODUCED EXACTLY. I did NOT re-run their 5 mutation probes — that needs editing production code, which I may not do; I assessed non-vacuousness by reading assertions instead (finding 10). Did not run services/api (3.12-only).

## Q1 — DOES THE DOUBLE-LAUNCH HOLE CLOSE? YES.

Traced the real path, not the report. `cli.py:2269` is the ONLY non-test `ClaudeRunner(...)` and now passes `journal=journal`. Then `claude_runner.py:1063` Popen -> `:1068` `container.adopt` -> `:1073` record (before the first `write()` at `:1116`) -> `:1207` settle, which early-returns unless `process.poll()` is not None (`:1312`).

It is genuinely non-inert: `loop.py:1673-1677` transitions START_CLAUDE->CLAUDE_RUNNING only AFTER `run_unit` returns, and `loop.py:143` CYCLE_ENTRY_STATES INCLUDES START_CLAUDE — so a kill mid-unit really does leave a legal re-entry that WOULD dispatch a second worker. The record is now what stops it: `recovery.py:267-268` (surviving OR undetermined = unaccounted) -> `:284-295` UNSAFE_OR_DRIFTED -> `cli.py:2433` refuses.

I found NO path where a live child exists with no record, and NO path where a record is cleared while the child is alive, other than: R1 AND R4 (finding 2) and finding 4's compound. Note R1 does not stand alone as the producer frames it — the gate admits only job_object hosts, `process.py:420-433` sets KILL_ON_JOB_CLOSE with `assert_no_breakaway`, the job handle is non-inheritable, so an external kill drops the last handle and the kernel kills the child; on any other host the gate refuses BEFORE Popen. R1 is reachable only via R4.

## Q2 — R4. FIRM SEVERITY: MINOR for M0-T053; REQUIRED-CORRECTION before M0-T056. NOT false assurance.

The deciding fact: if `adopt` degrades honestly to taskkill (`process.py:567-574`), the orphan is STILL RECORDED, because C2 writes the record unconditionally after adopt regardless of achieved containment. The next `start` still refuses. So R4 does not reopen the hole the pin was written for; its residual is only the compound with R1. Not false assurance because the pin text stands unamended, achieved containment is still on `RunResult.containment` and the `claude_process_started` transition (`loop.py:1677`), and `start` now reports `containment.kind` (`cli.py:2423-2424`).

BEFORE M0-T056: achieved per-cycle containment must become a STOP, not a record — a cycle with `run_result.containment != "job_object"` must PAUSE. The reason is specific to R595, not to this task: unattended, nobody reads the audit line.

## NUMBERED FINDINGS

1. [INFO/VERIFIED] C2 wiring closes the hole on the production path — trace above.
2. [INFO] R1 bounded by kernel kill-on-close on every host where a spawn is now permitted; reachable only with R4.
3. [INFO/VERIFIED] C1 gate has NO bypass and is correctly ordered. `cli.py:2189 containment_precondition()` takes no arg, no env, no config, no flag; calls `process.default_containment_kind()` (`process.py:617-621`) = the same source doctor reads. Order: `:2428` missing-inputs -> `:2433` classification -> `:2446` CONTAINMENT -> `:2466` `_run_loop` (whose only caller is cmd_start). Repo-wide grep: one ClaudeRunner, one _run_loop call, no override. Tests patch `cli.default_containment_kind` — an in-process Python seam, not operator-reachable.
4. [REQUIRED-CORRECTION, pre-M0-T056] `claude_runner.py:1283-1298` asserts a termination it never verifies. `container.terminate_all()`'s bool is DISCARDED, exceptions swallowed, no `wait()`/`poll()`, yet the raised message says "the worker was terminated". On the degraded-taskkill path `terminate_process_tree` can legitimately return False (`process.py:587-593`). Compound: degraded containment + journal write fails + kill fails = LIVE UNRECORDED orphan, empty record, traceback exit, and the next `start` reads SAFE_CHECKPOINT and DOUBLE-LAUNCHES. Lands squarely on R347. Fix: capture the bool, bounded `process.wait()`, and raise a DISTINCT code if still alive. (A durable orphan marker is not available as a fallback — it is impossible for the same reason the record was.)
5. [MINOR now / REQUIRED-CORRECTION pre-M0-T056] `recovery.py:190-191` `clear_child_record` is a WHOLE-KEY wipe, so settle clears records it did not create. One recorder today = latent. M0-T056 adds a second: `turnover_adapters.py:434 make_subprocess_command_runner`, the successor-launch seam, currently unwired and spawning via `process.run` with no accounting and no gate. The moment it records, a worker's clean exit ERASES the live successor's record — fail-open on exactly no-duplicate-workers. Fix: remove by (pid, start_token).
6. [MINOR, pre-existing, NOT from this diff] `doctor --live` (`cli.py:1203` -> `preflight.py:126-131`) spawns a real Claude child with no ProcessContainer, no record, no gate; kills only the direct child on timeout. Cannot cause a duplicate worker (temp cwd, denies all tools, never dispatches the loop). Register for the M0-T056 sweep only.
7. [MINOR, recommended pre-M0-T056] R5 confirmed: `RunnerError(Exception)` `claude_runner.py:264` and `LoopError(Exception)` `loop.py:211` are SIBLINGS, so `cli.py:2467` does not catch it and neither `run_cycle` nor `run()` wraps `loop.py:1668`. I checked the three things you asked: **lock RELEASED** (`cli.py:2483-2485` finally runs); **no partial row** (`durable_state.py:371-383` BEGIN IMMEDIATE/COMMIT with ROLLBACK — all-or-nothing); **next start not misled** (machine at START_CLAUDE, a legal entry, but the worker was killed and the record is empty, so it dispatches onto a clean host). Acceptable for M0-T053: loud, fail-closed, no stuck lock. NOT acceptable unattended — no structured refusal record, no audit event, supervisor-of-supervisor sees only a non-zero exit. Fix: catch RunnerError in cmd_start as a `loop_refusal` payload + audited event, as B-2 did for LoopError.
8. [INFO] Audit integrity sound. `audit_log.py:171-216` refuses on a damaged chain, redacts, hash-chains. Cannot be silently dropped: a damaged chain fails `audit_chain` revalidation and stops at `:2433` before the containment elif. Detail = kind/required/mode/fixed reason. NO secret, credential, path, or env newly logged. Gap: the event is written only when containment is the FIRST stop; the comment at `cli.py:2410-2413` claiming it is "in the record" regardless is true of the payload, NOT the audit log. Nothing unsafe (those runs did not dispatch).
9. [INFO] No injection/traversal/growth. `recovery.py:181-187` writes int pid + module constant + probe token + timestamp via canonical_json into a PARAMETERIZED statement (`durable_state.py:375-379`); no path built; at most one entry. Pid-reuse defense `recovery.py:170-173` fails closed on an unknown token.
10. [INFO] Q5 NOTHING ACTIVATES — verified. 7 files total; production = 138 insertions / 2 deletions in exactly 12 hunks in 2 files. `default_mode = shadow` untouched; limited-auto NotImplementedError `cli.py:2371-2376` untouched; no config.example.toml/policy/ACL/hook/permission change; **`C:/SupervisorController/config.toml` is outside the repo and NOT in the diff**. Every change is a new refusal or an added journal write. `journal=None` preserves prior behavior (`:1276`, `:1310`) with a test. Non-code files are only `.claude/agent-memory/backend-engineer/**` — the producer's own permitted scope.
11. [INFO] Tests non-vacuous by construction: `assertEqual(len(spy.child_writes), 2)` with both payloads inspected cannot pass on a path that records nothing; the surviving-child test fails at `assertTrue(recorded)` if recording is removed and independently proves the pid alive via `probe_process` before running the real `recover_boot`; the CLI test spies while delegating to the real functions. Both host shapes exercised on any OS.
12. [INFO] Producer report line 102 says "15 deselected"; the real number is **16** (1477+16+2 = 1495 collected; 12 new + 4 pre-existing recovery ChildAccountingTests). Their baseline 1481 and delta +12 are still CORRECT — a transcription slip, not a wrong conclusion. Freeze baseline (>=1165, 0 failures) re-established.

## MAY M0-T056 BUILD ON THIS? YES — as a FOUNDATION, with findings 4, 5, and the enforcement half of R4 landed inside M0-T056's own scope before its first live actuation.

This converts double-launch protection from "one platform mechanism with the other inert" into "two independent live mechanisms," and opens no path. But M0-T056 changes the threat model in two ways this task did not have to face, and both map onto named findings, not vague caution: (a) it ADDS A SECOND SPAWNER (`turnover_adapters.py:434`), which makes finding 5 a live fail-open the moment it records anything; (b) it REMOVES THE HUMAN — a degraded-but-honestly-recorded containment (R4) and a traceback exit (finding 7) are only acceptable because someone reads them.

I would NOT accept an M0-T056 that treats these residuals as already closed. I WOULD accept M0-T053 now with them pinned.
