# G3 Independent Code Review — M0-T114 (D-024 residuals R258/R272/R273)

**VERDICT: PASS**

**Frozen review identity:** `5e2c8c3497bf1af1dff333a7f4c9290c9aa86eb7` — verified `git rev-parse HEAD` matches.
**Deliverable commit:** `f89aa29` ("M0-T114: the three pinned residuals …").
**Reviewer:** independent read-only (no writes, no git mutation).

## Scope check — PASS
Deliverable commit `f89aa29 --stat` touches EXACTLY the five allowed paths and nothing else:
`tools/agent_supervisor/telegram_sink.py`, `tools/agent_supervisor/live_observation.py`, `tools/test_agent_supervisor_telegram_sink.py`, `tools/test_agent_supervisor_golden_run.py`, `project-control/reports/M0-T114-residual-fixes.md`.
Full unit diff (`git diff --stat 420dd5c^..5e2c8c3`) adds only those five plus control-plane files (gates/reports/tasks/state.json) — expected for a claim→submit cycle. **M0-T115's files (broker.py, recovery_probes.py, loop_turnover.py) are untouched.** `codex_channel.py` is untouched (relevant to residual 3).

## Residual 1 — telegram_sink queue-growth like-for-like — CORRECT
The `_already_queued` check moved AFTER `build_notification` and now digests `notification.summary` (post-builder) instead of the raw caller `summary` (telegram_sink.py:331-345). Verified against the frozen queue/builder code:
- **(a) like-for-like holds.** `NotificationQueue.enqueue` stores `notification.to_dict()`, so queued items carry the POST-BUILDER `reason`/`summary` (notifications.py:213-217). `_already_queued` recomputes the digest from `item.reason/task_id/summary` (telegram_sink.py:282-286); the new-side operand is now also post-builder. Both sides post-builder → matches even when the builder redacts/truncates (>400 chars → truncated to `MAX_SUMMARY_CHARS`).
- **(b) delivered-dedup unchanged.** `_dedup_seen` (check) and `_dedup_record` (record) both use the raw `digest` and remain raw-vs-raw and consistent (telegram_sink.py:313-320, 349). Untouched by the diff.
- **(c) leak-refusing builder runs BEFORE any enqueue.** `build_notification` (which raises `NotificationError` on leak shapes) executes before the `_already_queued` check and before `queue.deliver` (the only enqueue). ✔
- **(d) failure-path ordering.** `except NotificationError` returns immediately, before the queue check and before enqueue. ✔
- **(e) byte-identical for unaltered summaries.** When raw==built, `queued_digest==digest`; the only other observable difference is that the queue check now runs after build — but an already-queued item implies a prior successful build of identical inputs, and `build_notification` is deterministic, so it cannot both be already-queued and now raise. Net: identical for unaltered summaries; the sole intended difference is the altered-summary class. ✔
- **(f) at-least-once preserved.** Suppression only skips a re-enqueue when an identical post-builder item is already durably queued; that item stays and is not dropped. ✔
- **(g) new seam?** None. `build_notification` is side-effect-free (constructs a dataclass, no journal writes — notifications.py:106-151). Single-threaded CLI; nothing is enqueued between the `_dedup_seen` check and the build. Moving the queue check after the build actually makes leak-refusal take precedence over a spurious `already_queued`, which is safer, not weaker.

**Empirical revert-sensitivity (real helper functions, no repo edit):** for a 990→400-char builder-truncated summary, `_already_queued(raw_digest)=False` (the pre-fix bug: re-enqueues) vs `_already_queued(post_builder_digest)=True` (post-fix: suppresses). Confirms the fix and that the defect test is genuinely revert-proof.

## Residual 2 — live_observation source_record_key — CORRECT (one line)
The record now reads `sanitized.value["source_record_key"]` (live_observation.py:299). Verified: `source_record_key` was ALREADY an input to `sanitize_structure` (line 277) before the fix, and `redaction_count` = `sanitized.count` (line 291) therefore ALREADY counted any redaction of that key. So **count semantics do not change** — the fix only makes the STORED value consistent with the count it was already claiming. Pre-fix, the row could report `redaction_count>=1` while `source_record_key` still held the raw token (a real, checkable inconsistency). Read-side only; follows the established `sanitized.value[...]` pattern (lines 284-290). The source of the key is the journal state key itself (live_observation.py:145), which is why an attacker-shaped key is a genuine boundary; the test embeds a key-shaped token in that journal key, so it is revert-sensitive.

## Residual 3 — unit-K boundary-queue notes — HONEST DISPOSITION
"Inert-by-design, carried as a note, any change needs its own packet" is honest and checkable: `codex_channel.py` is outside allowed_paths, the owner ordered no broadening (R272), and the write-only/inert classification was made at the accepted unit-K contract (promotion/drain is owner-gated future work). Load-bearing verifiable fact — codex_channel.py is untouched by this unit — holds. This is a transparent deferral, not a fix, and the report says so.

## Tests — right boundary, additions-only, revert-proof
- `test_a_builder_altered_summary_still_bounds_queue_growth`: drives a >400-char summary under a permanently-failing transport (`fail_first=99`), asserts the precondition that stored != raw (builder truncated), then 4 repeats all return `already_queued`/`still_queued` and queue depth stays 1. Correct boundary (queue depth under outage with a builder-altered summary). It isolates the queue-growth path from delivered-dedup (delivery never succeeds, so `_dedup_record` never fires).
- `test_the_source_record_key_is_sanitized_not_raw`: asserts the raw `sk-ant-…` token is absent and `[REDACTED` present in the register row. Correct boundary.
- Diff is **additions-only** — no deletion of any existing assertion (`grep '^-[^-]'` on both test diffs returns nothing). No existing test weakened.

## Report honesty — consistent with code and reproduced
Every material claim in `project-control/reports/M0-T114-residual-fixes.md` reproduced independently:
- L-pack telegram: **36 passed**; golden: **41 passed**; combined **77 passed** (report cites 36/36, 41/41).
- Affected 8-pack sweep (adversarial, codex_channel, endurance, golden_run, operator_channel, phase1, reviewer, telegram_sink): **535 passed, 0 failed**.
- `ruff check` on the four touched files: **All checks passed!**
- `python tools/modularity_check.py --check`: **EXIT=0** (warnings listed are pre-existing files; neither touched file appears — telegram_sink.py 381 SLOC, live_observation.py 460 SLOC, both under the 600 warn threshold).
- R273 (no live-journal writes): supported — both fixes are read-side/reorder only, execute only inside notify/observe calls receiving a journal arg; tests use temp journals (`self.journal()` / `tempfile`).
- R247 consequence stated correctly: any supervisor tree change moves material identity; M0-T116 recertifies at the final frozen identity covering this unit and M0-T115.

## Findings
- **BLOCKER:** none
- **MAJOR:** none
- **MINOR:** none
- **INFO-1:** `queued_digest` uses `condition` (raw) as its first operand rather than `notification.reason` (telegram_sink.py:335). Equivalent for the fixed 8-condition vocabulary (those tokens pass `redact_text` unchanged, so `condition == notification.reason`); `notification.reason` would be perfectly symmetric with the summary operand. Not a defect.
- **INFO-2:** Post-fix, suppressed retries neither re-enqueue nor re-attempt delivery of the queued item — this now matches the behavior the unaltered-summary case ALREADY had pre-T114; the fix simply extends that accepted behavior to the altered-summary class. Automatic redelivery/drain of the durable notification queue is not wired in the current shadow-only build (inherited T111 design, out of scope, not worsened by this unit; nothing is dropped).
- **INFO-3:** Residual 3 is a deferral rather than a code fix — correct and transparent under the R272 no-broadening order.

## Commands run
- `git rev-parse HEAD` → 5e2c8c3… (matches frozen identity)
- `git log --oneline b8ea872..5e2c8c3`
- `git show --stat f89aa29`; `git diff --stat 420dd5c^..5e2c8c3`
- `git show f89aa29 -- <each touched file>`
- `python -m pytest tools/test_agent_supervisor_telegram_sink.py tools/test_agent_supervisor_golden_run.py -q` → **77 passed**
- Digest revert-sensitivity via `python -c` using real `telegram_sink`/`notifications` helpers → PRE-FIX False / POST-FIX True
- 8-pack sweep pytest → **535 passed**
- `python -m ruff check <four files>` → All checks passed; `python tools/modularity_check.py --check` → EXIT=0
- Per-pack counts: telegram 36, golden 41

**Verdict: PASS.** The three residuals are correctly implemented (two behavior fixes + one honest deferral), scope is exactly the allowed paths, M0-T115 files untouched, tests are additions-only and revert-proof, and every report evidence claim was independently reproduced.
