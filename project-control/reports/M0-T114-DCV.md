# DCV Report — M0-T114 (D-024 residual fixes)

**OVERALL VERDICT: PASS** — 3/3 applicable requirements SATISFIED against primary evidence.

**Frozen review identity:** `5e2c8c3497bf1af1dff333a7f4c9290c9aa86eb7`
**HEAD at review:** `5e2c8c3497bf1af1dff333a7f4c9290c9aa86eb7` (MATCH), branch `control/D-024-fable-codex-loop`, working tree clean (`git status --porcelain` empty).
**Role:** independent read-only verifier ≠ producer (`fable-orchestrator-session`). I judged each row on primary evidence I reproduced myself; the producer's report and evidence-map are treated as claims only.

## Applicable set (re-derived, not taken on trust)
`evaluate_task_refs(M0-T114.json)` →
`ok=true; applicable_ids=[D-024-R258, D-024-R272, D-024-R273]; cited_ids=[same]; missing=[]; invalid_refs=[]; unresolved=[]`.
The set is exactly R258/R272/R273 — no missing/invented rows. My three verdicts cover the full applicable set.

## Per-requirement verdicts

| Row | Verdict | Primary evidence I personally verified |
|---|---|---|
| **D-024-R258** (carry residuals as tracked follow-up; executing re-triggers R247) | **SATISFIED** | Residual 1 & 2 FIXED in code (traced below); residual 3 dispositioned no-code with a checkable justification; R247 re-trigger scheduled via M0-T116, not skipped. |
| **D-024-R272** (same-window, separate, no broadening) | **SATISFIED** | `git diff --name-only b8ea872..HEAD` for broker.py/recovery_probes.py/loop_turnover.py/codex_channel.py = EMPTY; non-control-plane changes = exactly the 5 allowed paths; M0-T115 accepted (b8ea872) before any T114 commit. |
| **D-024-R273** (never manually edit runtime journal) | **SATISFIED** | Both fixes are pure code paths on a passed-in journal (no manual/direct live-journal edit); read-time behavior keeps pre-fix journals truthful; all new/existing tests use `tempfile.TemporaryDirectory()` journals, never live %LOCALAPPDATA%. |

## Evidence detail

### R258 — residual dispositions

**Residual 1 (telegram_sink queue-growth) — FIXED, verified.** In `f89aa29` the `_already_queued` short-circuit moved from *before* `build_notification` to *after* it, now digesting `notification.summary` (post-builder) via `queued_digest = _dedup_digest(condition, task_id, notification.summary)` (telegram_sink.py:335-336). I confirmed the load-bearing invariant independently, not from the report:
- `NotificationQueue.enqueue` stores `notification.to_dict()` (notifications.py:213-216), and that notification is the post-builder object from `build_notification`, which redacts and truncates summary to `MAX_SUMMARY_CHARS` (notifications.py:136-146). So queued items store the **post-builder** summary.
- `_already_queued` recomputes `_dedup_digest(item["reason"], item["task_id"], item["summary"])` over those stored items (telegram_sink.py:282-284). Pre-fix, the caller passed the **raw** summary digest → mismatch on any builder-altered summary → re-enqueue every retry (unbounded growth). Post-fix it is post-builder vs post-builder — like-for-like.
- Closed-vocabulary `condition` survives redaction unchanged (so stored `reason` == `condition`); `task_id` is not redacted. Only the summary operand was wrong, now corrected.
- At-least-once preserved: on match the code returns `already_queued/still_queued=True` without dropping the queued item. The delivered-dedup path (`_dedup_seen`/`_dedup_record` on the raw `digest`, telegram_sink.py:313-314,349) is raw-vs-raw and untouched — verified consistent.

**Residual 2 (live_observation raw source_record_key) — FIXED, verified.** live_observation.py:299 now reads `sanitized.value["source_record_key"]`; the raw key was already fed into `sanitize_structure` at line 277, and every sibling scalar in the record (lines 284,285,288,289,290) already read from `sanitized.value[...]`. The one scalar that bypassed the boundary sanitizer is now consistent; the sanitizer input set is unchanged. Minimal and correct.

**Residual 3 (unit-K boundary queue) — no-code disposition, verified checkable.** `codex_channel.py` is outside this task's `allowed_paths` and was not touched (`git diff --name-only b8ea872..HEAD -- ...codex_channel.py` empty). Disposition recorded in the report as inert-by-design (write-only queue; consumption is owner-gated future work). This is a legitimate no-code carry, not a silent drop.

**R247 re-trigger scheduled, not skipped:** `project-control/tasks/M0-T116.json` exists (status `backlog`); objective: "after M0-T115 … and M0-T114 … are BOTH accepted, re-run the full golden certification at the ONE frozen post-repair identity" (R275 instantiating R247/R271). The certification consequence R258 requires is captured as a real scheduled unit.

### R272 — same window, separate, no broadening
- `git diff --stat b8ea872..HEAD` non-control-plane files = exactly the 5 allowed paths: `tools/agent_supervisor/telegram_sink.py`, `tools/agent_supervisor/live_observation.py`, `tools/test_agent_supervisor_telegram_sink.py`, `tools/test_agent_supervisor_golden_run.py`, `project-control/reports/M0-T114-residual-fixes.md`. The remaining diff entries (gates/, reports/M0-T114-*, state.json, tasks/M0-T114.json) are standard orchestrator-written control-plane lifecycle records, not producer source broadening.
- M0-T115's files (broker.py, recovery_probes.py, loop_turnover.py) and codex_channel.py: **untouched** by this unit (name-only diff empty).
- Separateness: distinct task file, distinct commits (420dd5c/1ef6c86/f89aa29/460daf6/5e2c8c3, all tagged M0-T114), distinct evidence-map/reports/gates. M0-T115 was ACCEPTED at b8ea872 **before** the first M0-T114 commit. Same window; both recertified together only at the one frozen identity in M0-T116.

### R273 — no manual runtime-journal edit
- Neither code change performs a manual/direct edit of the durable journal. `build_observation_record` returns a dict (no journal I/O). `notify_condition` operates only on the passed-in `journal` through the normal code surface. Both execute only in future notify/observe calls.
- Read-time truthfulness for pre-fix journals: the telegram fix only changes notify-time digest computation (correctly matching already-stored post-builder items on read); the live_observation fix only changes the value written into new records. No migration or rewrite of existing journal state.
- Tests use temp journals: `OperatorChannelBase.setUp` (test_agent_supervisor_operator_channel.py:155-156) and the golden `WatcherBase.setUp` (test_agent_supervisor_golden_run.py:74-77) both use `tempfile.TemporaryDirectory()`; `journal()` opens `DurableJournal(self.runtime / DB_FILENAME)` under that temp dir. No live %LOCALAPPDATA% journal is touched.

## Test / harness outputs (reproduced)
- `python -m pytest tools/test_agent_supervisor_telegram_sink.py tools/test_agent_supervisor_golden_run.py -q` → **77 passed in 15.73s** (matches expected 77). Both new defect-named tests present and green: `test_a_builder_altered_summary_still_bounds_queue_growth` (asserts precondition raw != stored, then queue depth stays 1 across 4 retries) and `test_the_source_record_key_is_sanitized_not_raw` (asserts secret token absent and `[REDACTED` present) — both are genuine RED→GREEN behavior tests, not tautologies.
- `python tools/validate_directive_compliance.py --check` → **EXIT 0** (source digests + locked requirement ids intact; amendment 9 R258 and amendment 12 R272/R273 verified).

## Prohibited-action evidence
Task status is `awaiting_gate` (not accepted) — correct for a pre-acceptance gate-wave DCV. Nothing merged/accepted/dispatched/deployed/installed/purchased/closed for this unit. PR #241 remains unmerged (not acted on here).

## Exact commands run
```
git rev-parse HEAD ; git status --porcelain ; git rev-parse --abbrev-ref HEAD
python -c "import json,sys; sys.path.insert(0,'tools'); import directive_registry as m; print(json.dumps(m.load_registry().evaluate_task_refs(json.load(open('project-control/tasks/M0-T114.json'))), default=str))"
git show --stat f89aa29 ; git show f89aa29 -- tools/agent_supervisor/telegram_sink.py tools/agent_supervisor/live_observation.py tools/test_agent_supervisor_telegram_sink.py tools/test_agent_supervisor_golden_run.py
git diff --stat b8ea872 HEAD ; git diff --name-only b8ea872 HEAD -- tools/agent_supervisor/broker.py tools/agent_supervisor/recovery_probes.py tools/agent_supervisor/loop_turnover.py tools/agent_supervisor/codex_channel.py
python -m pytest tools/test_agent_supervisor_telegram_sink.py tools/test_agent_supervisor_golden_run.py -q
python tools/validate_directive_compliance.py --check
```
Plus reads of telegram_sink.py, notifications.py, live_observation.py, the two test bases, and M0-T116.json.

**No UNVERIFIABLE or VIOLATED rows. Nothing blocks acceptance from this DCV.**
