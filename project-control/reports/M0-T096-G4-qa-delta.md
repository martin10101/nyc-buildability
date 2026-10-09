# G4 DELTA RE-ATTESTATION — M0-T096 (D-024 unit I)

> Verbatim reviewer return (qa-engineer agent, SendMessage delta re-attestation over
> `git diff 1a935fb..635fac5`). Recorded by the orchestrator.

**New frozen identity:** corrections commit `635fac5a867cb28b3ef6cd79109e371e59921ae2` (control tip `6dede159785764ad149ec33dcf1cef76a18bd062`); both reachable in the shared object store. Read-only throughout — I extracted the frozen tree via `git archive 635fac5 … | tar -x` into the scratchpad (no checkout, no git write, no `gh`/`project_control.py`, no repo file edited).

**Delta inspected:** `git diff 1a935fb..635fac5` = 4 code files (+50/−15) + 5 added gate-evidence artifacts (reviewer reports + `M0-T096.json`). The code diff matches the coordinator's description exactly.

**My MINOR-1 — correctly and completely resolved.** `test_capture_is_idempotent_and_carries_the_five_fields` now injects one source per `discover_events` branch that was previously unexercised:
- guardrail refusal (was covered), usage-limit quota (was covered), provider-abort availability (was covered);
- **outage `RETRY_KEY` availability**, **`model_change_audit` model-turnover**, and a **worker-turnover transition** (`record_transition` with `REASON_TURNOVER_RECORDED` detail) — the three branches I flagged.

It now asserts `rows_written==6`, CAS re-scan `==0`, the five R226 fields on every row, and critically `{row["observed_event_type"] for row in rows} == set(lo.EVENT_TYPES)` — the captured event-type set equals the **full** closed vocabulary `{guardrail_refusal, quota_exhaustion, availability, model_turnover}`. This closes the exact regression scenario I described: a renamed/broken source key can no longer silently un-capture a kind without dropping `rows_written` below 6 or breaking the set-equality assertion. The six injected sources map to six distinct digests (distinct `source_record_key`), so `rows_written==6` is correct. Fully covers the finding as raised.

**Other three corrections — no G4 regression:**
- golden_run.py (G3-M1): fake-provider inline git now adds `GIT_CONFIG_GLOBAL/SYSTEM=os.devnull`, mirroring module-level `_GIT_ENV` — behavior-neutral hermeticity strengthening.
- cli.py (G5-I1): watcher epilogue try/except nested inside an outer try with `finally: lock.release(); journal.close()` — the watcher call stays bounded (inner `except Exception` audits `live_observation_scan_failed`); cleanup now unconditional even under a `BaseException` in the scan. Epilogue behavior unchanged.
- live_observation.py (G5-I2): `installed_version_shape`, `applicable_shape`, `source_record_key` scalars now also pass `sanitize_structure`. The `verified_live: False` constant, CAS write, and closed vocabulary are untouched.

**Reproduced at 635fac5:** `python -m pytest tools/test_agent_supervisor_golden_run.py -q` → **40 passed in 17.32s**. Targeted verify: `test_capture_is_idempotent_and_carries_the_five_fields` PASSED and `test_no_code_path_writes_verified_live_true` PASSED (confirms the scalar-sanitization change introduced no `verified_live=True` path — my prior no-premature-verification guarantee still holds). Producer-reported loop+bounded_mode+start_reentry 209-passed / ruff-clean / modularity-0 remain orchestrator-captured stored evidence, consistent with the clean pack and behavior-neutral diff.

My original PASS stands; the sole MINOR finding is resolved with no new findings.

DELTA VERDICT: PASS
