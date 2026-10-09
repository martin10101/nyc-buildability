# G5 Security Review — M0-T114 (D-024 residual fixes)

**Verdict: PASS**
**Frozen review identity:** `5e2c8c3497bf1af1dff333a7f4c9290c9aa86eb7` — verified == HEAD (branch `control/D-024-fable-codex-loop`). Deliverable commit: `f89aa29`.
**Reviewer:** independent G5 (read-only; no writes, no git mutations).

## Scope confirmed
Deliverable `f89aa29` touches exactly the 5 allowed paths — two prod modules (`tools/agent_supervisor/telegram_sink.py`, `tools/agent_supervisor/live_observation.py`), two test packs (`tools/test_agent_supervisor_telegram_sink.py`, `tools/test_agent_supervisor_golden_run.py`), one report (`project-control/reports/M0-T114-residual-fixes.md`). The remaining files in `b8ea872..5e2c8c3` are orchestrator control-plane (gates, state, task/report JSON). No `.claude/**`, no dependency/lockfile edits, no MCP surface, no PR #241 reference, no activation surface, no one-way-geometry change (no receive/poll/approval code).

## Residual 1 — telegram_sink.notify_condition reordering (`telegram_sink.py:308-353`)

**(a) Leak-refusing builder still runs before any enqueue, and still refuses (never trims).** `build_notification` (`notifications.py:106`) is called at `telegram_sink.py:322` — its `assert_view_only` (`notifications.py:95-103`) *raises* `NotificationError` on any forbidden shape (secret / raw command / auth link / private path / source excerpt); the class docstring is explicit "refused, not trimmed" (`notifications.py:63-64`). On raise, `notify_condition` returns at line 328-330 **before** the moved `_already_queued` check and before `queue.deliver`. The only enqueue is `NotificationQueue.enqueue` inside `deliver` (`notifications.py:213-222`), reached at `telegram_sink.py:347` — strictly after the builder. Reordering did not create any enqueue path that bypasses the builder. PASS.

**(b) No path where an unbuilt/unredacted summary reaches the queue, transport, or audit.** The queue stores `notification.to_dict()` (`notifications.py:215`) — i.e. the post-builder, post-redaction, post-truncation `notification.summary` (built at `notifications.py:131-137`). The moved growth check computes `queued_digest = _dedup_digest(condition, task_id, notification.summary)` (`telegram_sink.py:335`) — the *post-builder* summary — and `_already_queued` (`telegram_sink.py:276-286`) recomputes the digest from the stored queue items' own `summary`, so the comparison is genuinely like-for-like (post-builder vs post-builder). The raw `summary` argument never reaches the queue, the sink, or the audit after this point. PASS.

**(c) Audit detail for `telegram_already_queued` carries a hash, not content.** The relocated `audit.append` (`telegram_sink.py:337-340`) logs `{condition, digest: queued_digest}`. `condition` is closed-vocabulary (validated against `CONDITIONS` at line 308-312); `queued_digest` is `_dedup_digest` → `digest_of` → `sha256_hex(canonical_json(...))` (`telegram_sink.py:266-268`, `models.py:64-66`) — a one-way SHA-256, not reversible content. Safe to log. PASS. (Note this is the *same* audit-append that existed before the change, merely moved after the builder and switched from the raw `digest` to `queued_digest`; it is not a new journal write.)

**(d) One-way geometry untouched.** No receive/poll/approval/inbound surface added; the diff is a pure reordering plus a post-builder digest recompute. PASS.

**(e) Env-only secrets posture untouched.** No new `os.environ`/`getenv` reads or writes in the diff; the bot token never appears in any output path introduced here. PASS.

**Primary defect actually fixed.** Before this unit, `_already_queued` was fed the **raw** notify-time summary digest while the queue stored the **post-builder** summary — so any summary the builder redacted or truncated never matched a queued item and was **re-enqueued on every retry during a sustained outage → unbounded queue growth**. The reordering makes the check post-builder-vs-post-builder, restoring bounded growth (R244). At-least-once is preserved: the first item stays queued and still delivers (`NotificationQueue.deliver` leaves the item on failure, `notifications.py:237-246`). Delivered-dedup (`_dedup_seen`/`_dedup_record`, keyed on the **raw** digest at `telegram_sink.py:313,349`) is correctly left unchanged, because the DELIVERED register stores raw-summary digests — each dedup store is compared against its own representation. This asymmetry is correct, not a bug.

## Residual 2 — live_observation register key sanitization (`live_observation.py:296-299`)

The register row previously wrote `str(source.get("source_record_key",""))` **raw**, bypassing the boundary sanitizer that every other copied scalar passes through — a real persisted leak, since `record_observations` writes rows to the durable journal. The fix reads `sanitized.value["source_record_key"]`, i.e. the value produced by `sanitize_structure` at `live_observation.py:271-278`.

I verified the key name `source_record_key` does **not** match `SENSITIVE_KEY_PATTERN` (`redaction.py:34-37`) — the only "key" alternatives are `api_key`, `session_key`, `private_key`, `access_key`, none a bare `_key` — so the value takes the normal string pipeline (`sanitize_text` → `redact_text`, `telemetry_redaction.py:121-149`) rather than being masked wholesale to a constant. Result: a benign key stays readable, while an embedded token (e.g. `sk-ant-…`) becomes `[REDACTED:anthropic_key]` via the `anthropic_key` pattern (`redaction.py:42`). Correct and non-destructive.

**Full record-dict sweep (`build_observation_record`, `live_observation.py:279-301`) — every source-derived string is now sanitized, a digest, a bool, or a closed-vocab constant:** `schema`/`kind`/`verified_live` = constants; `observation_digest` = `digest_of(...)` one-way hash (`live_observation.py:225-227`, and note it hashes the raw key but emits only a hash); `observed_event_type` = `event_type`, constrained to the closed `EVENT_TYPES` vocabulary (raises `ObservationError` otherwise, `live_observation.py:263-265`); `installed_version_shape`, `applicable_shape`, `classification_decision`, `selected_response`, `sanitized_outcome` = sanitized; `applicable_shape_verified_live` = bool; `redaction_count` = int; `evidence_class` = one of two constants; **`source_record_key` = now sanitized (the fix)**; `observed_at_utc` = timestamp. No other raw scalar remains. PASS.

## Adversarial analysis — collision-driven suppression (Scope item 4)

Craft two distinct source summaries sharing the same redacted 400-char prefix, with identical `condition` and `task_id`. After the builder both collapse to the same `notification.summary`, so `queued_digest` collides and the second is suppressed as `already_queued`. **Severity: INFO (no security impact, honestly disclosed).** Reasons: (1) with identical `condition`+`task_id`+post-builder-`summary`, the delivered message body is byte-identical (`risk_class` is derived from `condition`; the differing fields — `where_to_review`, `run_id`, `checkpoint_id` — were **never** in the dedup digest, so this collision surface is pre-existing for short summaries and is not introduced by this unit); (2) the first item stays queued and delivers, so at-least-once holds; (3) this is the best-effort growth suppression the T111 acceptance already pinned as a known non-blocking residual — the unit improves it (from "never matches → unbounded growth" to "matches like-for-like"), it does not regress leak-refusal or one-way geometry. The only theoretical loss is a second `where_to_review` pointer for two genuinely-distinct events that happen to collide on condition+task_id+400-char-prefix during an active outage — a delivery-completeness edge, not a leak. Recommend leaving the existing pinned follow-up note in place; no action required for this gate.

## Verification performed

- **HEAD == frozen SHA:** `git rev-parse HEAD` = `5e2c8c3497bf1af1dff333a7f4c9290c9aa86eb7`. PASS.
- **Gitleaks over unit commits:** `gitleaks.exe detect --source . --no-banner --redact --log-opts "b8ea872..5e2c8c3"` → `no leaks found`, exit 0 (5 commits, ~19.97 KB scanned). The fake sentinel `sk-ant-api03-FAKEFAKEFAKEFAKE1234567890abcdefg` in the golden-run test was **not** flagged and needed **no** allow pragma — the scan is clean without one. PASS.
- **Targeted tests:** `python -m pytest tools/test_agent_supervisor_telegram_sink.py tools/test_agent_supervisor_golden_run.py -q` → **77 passed** (Python 3.11.9; these packs use no PEP-695 generics so 3.11 collects them). Includes the two defect-named red→green tests: `test_a_builder_altered_summary_still_bounds_queue_growth` (asserts queue depth stays 1 across 4 retries of a builder-truncated summary, with a `raw != stored` precondition) and `test_the_source_record_key_is_sanitized_not_raw` (asserts the `sk-ant-…` token is absent and `[REDACTED` present in the register row). PASS.
- **R273 (no runtime-journal writes):** tests write only to `tempfile.TemporaryDirectory()`/`mkdtemp()` journals (`test_agent_supervisor_golden_run.py:75,631`); the prod diff adds no new `set_state`/`open`/`write` — the sole journal touch is the pre-existing `audit.append("telegram_already_queued", …)` relocated after the builder. PASS.
- **Additions-only tests / no M0-T115 files:** test diffs are new methods only; the only prod files touched are M0-T114's two allowed modules. PASS.

## Commands run
```
git rev-parse HEAD ; git rev-parse --abbrev-ref HEAD
git log --oneline b8ea872..5e2c8c3
git diff --stat b8ea872..5e2c8c3 ; git show --stat f89aa29
git show f89aa29 -- <the 4 code files>
C:/Users/MLFLL/.gitleaks/gitleaks.exe detect --source . --no-banner --redact --log-opts "b8ea872..5e2c8c3"
python -m pytest tools/test_agent_supervisor_telegram_sink.py tools/test_agent_supervisor_golden_run.py -q
```

## Findings summary
- **Critical / High / Medium: none.**
- **Low: none blocking.**
- **Informational (1):** collision-driven `already_queued` suppression is best-effort by design; no leak, no one-way-geometry weakening, at-least-once preserved, delivered content byte-identical on collision. Pre-existing pinned follow-up; no action required for this gate.

Both residuals are correctly and completely fixed: the telegram reordering preserves leak-refusal (builder-before-enqueue), one-way geometry, hash-only audit, and env-only secrets while restoring bounded queue growth; the live_observation one-liner closes a real persisted-key leak and the full record sweep shows no remaining raw source-derived scalar. **G5 verdict: PASS.**

*(Orchestrator note for the record: the CI "Scan repository for credentials" job — a different scanner from local gitleaks — DID flag the unpragma'd sentinel at the frozen tip 5e2c8c3; the standard allow pragmas were added in correction commit a22e34a, consistent with the campaign convention that fake tokens need BOTH gitleaks:allow and secretscan:allow.)*
