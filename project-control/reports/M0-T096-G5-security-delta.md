# G5 DELTA Re-Attestation — M0-T096 (D-024 unit I)

> Verbatim reviewer return (security-reviewer agent, SendMessage delta re-attestation over
> `git diff 1a935fb..635fac5`; transport entity-decoding only — `&lt;`/`&gt;` rendered as
> `<`/`>`). Recorded by the orchestrator.

## Identity (verified)
- HEAD (`git rev-parse HEAD`): `6dede159785764ad149ec33dcf1cef76a18bd062` (control tip); corrections commit `635fac5a867cb28b3ef6cd79109e371e59921ae2`.
- Delta reviewed: `git diff 1a935fb..635fac5` — code files `cli.py` (+/−), `golden_run.py`, `live_observation.py`, `test_agent_supervisor_golden_run.py`, plus the 5 new gate-evidence reports under `project-control/reports/`. No `.claude/hooks`, settings, `.github`, or dependency-manifest changes in the delta.
- Executed: delta diff read of all three production files + the test delta; re-read of `build_observation_record`; `python -m pytest tools/test_agent_supervisor_golden_run.py -q` → `40 passed in 18.65s`.

## Delta assessment by item

- **INFO-1 (cli.py finally nesting) — CLOSED, correct, no new hazard.** `cmd_start`'s epilogue (`cli.py:3057-3073`) now wraps the watcher scan in an inner `try:` whose `finally:` runs `lock.release()`/`journal.close()`. A `BaseException` (KeyboardInterrupt/SystemExit) raised inside `record_observations` now propagates through that inner `finally`, so cleanup runs unconditionally before the interrupt continues. Ordinary-`Exception` and normal-path behavior are effect-identical to the reviewed version (scan error → audit → release → close). No masking hazard: `lock.release()` swallows `OSError` internally and is owner-checked (`locking.py:300-312`), and this pattern matches the ~20 existing `finally: journal.close()` sites in the file. Cleanup runs exactly once in every path.

- **INFO-2 (register-boundary sanitization) — SUBSTANTIALLY CLOSED; one residual (non-blocking).** `installed_version_shape` and `applicable_shape` now persist the sanitized values (`live_observation.py:284-285` read `sanitized.value[...]`), and `source_record_key` was added to the `sanitize_structure` input (`:277`) so its redactions feed `redaction_count`. **Residual:** the persisted `source_record_key` field at `live_observation.py:296` still reads the RAW `str(source.get("source_record_key", ""))` rather than `sanitized.value["source_record_key"]`, so the computed sanitized value for that one field is used only for the count, not persisted. This is NOT a security exposure and does not block: `source_record_key` is always controller-generated (a constant key prefix such as `guardrail_refusal/` + a hex sha256 digest, or the literals `usage_limit_record`/`model_change_audit`/`transitions/<int>` — enumerated exhaustively in `discover_events`), never attacker-controllable, and carries no secret, home path, or terminal escape, so its raw and sanitized forms are byte-identical for every real input; the row still lands clean. The task passed at 1a935fb with INFO-2 fully open, so this partial closure cannot regress the verdict. Trivial one-line follow-up: switch `:296` to `sanitized.value["source_record_key"]` for full consistency with the stated intent.

- **G3 MINOR-1 (fake-provider git isolation) — CLOSED.** The inline `git()` in `FAKE_CLAUDE_GOLDEN` now sets `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM=os.devnull` (`golden_run.py:172-173`), mirroring `_GIT_ENV`, so the fake producer's commits no longer read the owner's global git config/template hooks. Test-only template string; no production impact.

- **G4 MINOR-1 (discovery-branch coverage) — CLOSED.** `test_capture_is_idempotent_and_carries_the_five_fields` now seeds all six discovery branches (refusal, usage-limit quota, provider-abort availability, outage-retry availability, model-change turnover, worker-turnover transition), asserts `rows_written == 6`, and asserts the captured `observed_event_type` set equals the full closed `EVENT_TYPES` vocabulary — so a renamed/broken source key can no longer silently un-capture an event kind.

## Unchanged security posture (re-confirmed at delta)
No `verified_live=True` sink introduced (still constant `False` at `:295`); labeling remains fail-closed toward `injected`; the watcher still performs no process/prompt/messaging and writes only its own `pending_live_observation*` keys; the bridge remains record-intent-only with the `assert_actuation_permitted` double gate intact; no secret material in the delta (only the pre-existing synthetic redaction-test literal); production code still never imports `golden_run`; module sizes within thresholds.

The delta closes INFO-1 fully and INFO-2 functionally, adds the requested test/isolation hardening, introduces no regression or new hazard, and leaves only a trivial cosmetic residual on a provably non-sensitive field. Golden pack 40/40 green at the frozen identity.

DELTA VERDICT: PASS
