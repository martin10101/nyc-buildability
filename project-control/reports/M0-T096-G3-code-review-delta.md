# G3 DELTA Re-Attestation — M0-T096 (D-024 unit I)

> Verbatim reviewer return (code-reviewer agent, SendMessage delta re-attestation over
> `git diff 1a935fb..635fac5`; transport entity-decoding only — `&lt;`/`&gt;` rendered as
> `<`/`>`). Recorded by the orchestrator.

## Identity verified
- HEAD = `6dede159785764ad149ec33dcf1cef76a18bd062` (control tip); corrections commit `635fac5a867cb28b3ef6cd79109e371e59921ae2` is an ancestor of HEAD (`merge-base --is-ancestor` = true).
- `git diff --stat 635fac5..HEAD -- tools/agent_supervisor tools/test_agent_supervisor_golden_run.py` is empty → the deliverable code is byte-identical at HEAD to the corrections commit.
- Code delta over my reviewed `1a935fb`: `git diff 1a935fb..635fac5` touches exactly the 4 code files (cli.py, golden_run.py, live_observation.py, test pack) plus report/ledger files.

## What I executed
- `python -m pytest tools/test_agent_supervisor_golden_run.py -q` → **40 passed** (15.59s), including the strengthened `WatcherCaptureTests` (6-branch / full-vocabulary coverage).
- `python -m pytest tools/test_agent_supervisor_start_reentry.py -q` → **16 passed** (9.11s) — exercises the changed `cmd_start` epilogue/nested-finally on the real start path.
- `python tools/modularity_check.py --check` → **failures 0** (cli.py warning-only, unchanged). Line counts: golden_run 409, live_observation 457 (both < 600 warn), cli.py 3504 (pre-existing).

## Per-change assessment
1. **My MINOR-1 (golden_run.py:169–174) — RESOLVED.** The fake claude's inline `git()` now adds `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM=os.devnull`, exactly mirroring the harness `_GIT_ENV`. `os` is imported inside the fake script, so `os.devnull` resolves correctly. The fake now isolates from host global/system git config (gpgsign, hooksPath) just like the harness base commit. Correctly and fully resolved.
2. **G4 MINOR-1 (test pack) — sound, test-only.** The capture test injects one source per discovery branch (refusal, usage-limit, provider-abort, outage RETRY_KEY, model_change_audit, worker-turnover transition), asserts `rows_written == 6`, and asserts `{observed_event_type} == set(EVENT_TYPES)`. Re-derived: 6 distinct sources → 6 rows; the four closed-vocabulary event types are all covered. No production behavior change; strengthens regression coverage. Verified green.
3. **G5 INFO-1 (cli.py:3055–3073) — correct.** The watcher scan is now nested inside an outer `try` whose `finally` runs `lock.release(); journal.close()`, so a `BaseException` inside the scan no longer skips cleanup. Cleanup order (release before close) is preserved; the `Exception`-only audit path is unchanged. start_reentry 16/16 confirms the start path is intact.
4. **G5 INFO-2 (live_observation.py:271–297) — correct.** `installed_version_shape` and `applicable_shape` (the payload-derived scalar) are now stored from `sanitize_structure`. Observation: the record's `source_record_key` is fed through the sanitizer (contributing to `redaction_count`) but the stored field still uses the raw value — harmless, since it is an internal structural key (`guardrail_refusal/<digest>`, `transitions/<seq>`) that is not attacker-controllable, and it is unchanged from before, so no regression. `observation_digest`/CAS identity is unaffected.

## Conclusion
My MINOR-1 is correctly and completely resolved. None of the four changes introduces a new correctness, safety, or modularity concern: the watcher remains fail-closed, `verified_live` stays a hardcoded constant `False`, cleanup is now strictly unconditional, and coverage is broader. The one residual nit (source_record_key stored raw) is immaterial and pre-existing, not a defect in this delta. All prior PASS properties hold.

DELTA VERDICT: PASS
