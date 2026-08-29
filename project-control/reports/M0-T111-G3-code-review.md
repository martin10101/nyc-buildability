VERDICT: PASS

# M0-T111 G3 Code Review — one-way Telegram notification sink (D-024 Amendment 8, unit L)

**Gate:** G3 (independent code review)
**Task:** M0-T111 — D-024 Amendment 8 unit L: one-way Telegram notification sink (owner-gated live send)
**Reviewer role:** read-only, independent (producer = fable-orchestrator-session)
**Reviewed HEAD:** `4ce8131d0f88fa0e2009a2a7049b4df2d6fcafb8` (matches expected reviewed head)
**Deliverable content identity:** `c9b3b9a` (later commits `6ae6155`/`04e3450`/`4ce8131` are control-plane only — verified: the four deliverable files are untouched after `c9b3b9a`)
**Verdict:** **PASS** (no BLOCKING/MAJOR findings; MINOR + INFO advisories below, none acceptance-blocking)

## Commands run and results

| Command | Result |
|---|---|
| `git rev-parse HEAD` | `4ce8131…` — matches expected |
| `python -m pytest tools/test_agent_supervisor_telegram_sink.py -q` | **31 passed** in 1.46s |
| `python -m pytest tools/test_agent_supervisor_adversarial.py tools/test_agent_supervisor_endurance.py -q` | **187 passed** in 6.80s |
| `python tools/modularity_check.py --check` | **failures 0**; new modules not in the 8 pre-existing warnings |
| `ruff check` (v0.13.0) on the 4 changed files | **All checks passed!** |
| `git diff --stat 6662b88..HEAD -- .` (non project-control) | only the 4 allowed files (+1021 lines) |
| `git diff 6662b88..HEAD -- .../cli.py` | exactly one import + one registration line |
| `git diff --name-only 6662b88..HEAD` on notifications/codex_channel/resume_scheduler/redaction/models | empty — **frozen boundary untouched** |

## Scope / policy compliance (verified)

- **Diff scope is exactly the allowed set:** `tools/agent_supervisor/telegram_sink.py` (new, 340 SLOC), `telegram_sink_cli.py` (new, 120 SLOC), `cli.py` (+2 lines), `tools/test_agent_supervisor_telegram_sink.py` (new, 559 lines). No forbidden path touched — `.claude/hooks`, `.claude/settings.json`, `.claude/ORCHESTRATION_POLICY.md`, `apps`, `packages`, `services`, `supabase`, `tools/project_control.py`, `tools/directive_registry.py`, `tools/validate_directive_compliance.py` are all untouched. `.claude/hooks` FORBIDDEN-this-unit constraint honored.
- **`cli.py` delta is exactly one import + one registration line** (`register_telegram_verbs` import at line 226; `register_telegram_verbs(sub, add_common)` call at line 3426), as the contract required.
- **Supervisor-freeze rule:** qualifying evidence D-024-R232/R241 cited in packet + every deliverable commit message + module docstrings. Frozen S13.10 boundary (`notifications.py`) is reused, not modified — the correct posture.
- **Modularity:** new modules are focused, well below thresholds; no dumping-ground; the sink implements `NotificationSink` rather than modifying it. Seven boundary answers in report §5 match the actual diff.

## Correctness (verified against source)

- **Closed vocabularies are genuinely closed.** `CONDITIONS` is an 8-tuple matching the amendment's eight bullets verbatim (verified line-by-line against `source-008-amendment.md` lines 79–86); `CONDITION_RISK` keys `== set(CONDITIONS)` (asserted by L1.1) and every value is a valid `RISK_CLASSES` member. Any other condition → typed `TelegramError("unknown_condition")`, never defaulted (L1.2, and mutation "accept-any-condition"/"drop-a-condition" killed).
- **`notify_condition` flow order is exactly** vocabulary-check (line 282) → dedup-check (288) → build via `build_notification` (296) → `NotificationQueue.deliver(..., unit_can_proceed=True)` (306) → dedup-record only on `result.delivered` (307–308). Confirmed in source; matches the contract.
- **Bounded retry + `last_attempts` accounting** (`TelegramSink.deliver`): `last_attempts` reset to 0; on unconfigured credentials it returns early with `last_attempts=0`; inside the loop `last_attempts=attempt`; success returns at the delivering attempt; exhaustion returns at `max_attempts`. `notify_condition` reads `sink.last_attempts` after delivery. Verified by L5.1 (exactly `MAX_DELIVERY_ATTEMPTS` calls) and L5.3 (`attempts==2` after one failure).
- **FIFO dedup trim** (`_dedup_record`): appends then trims to the last `DEDUP_MAX_ENTRIES` (64). L5's `test_the_dedup_register_is_fifo_bounded` confirms len==64 and oldest survivor is `digest-5` after 69 inserts. Digest is `digest_of({condition, task_id, summary})`.
- **`discover_conditions` is read-only and its filters match production data shapes.** Verified against unit-K writer: attention rows are stored under `ATTENTION_KEY_PREFIX` (`codex_channel/attention/`) with fields `disposition`, `actuated:False`, `message_id` (codex_channel.py lines 346–354) — the filter reads exactly those. `LIMIT_RECORD_KEY="usage_limit_record"` and `CODEX_HOLD_KEY="codex_rate_limit_hold"` (resume_scheduler.py) exist as claimed. Filter excludes actuated and non-`STOP_FOR_OWNER` rows; `all_state()` is only read, never written (L1.3 asserts state unchanged before/after).

## Contracts (verified)

- **`NotificationSink` implemented correctly:** `name="telegram"` + `deliver(notification) -> (bool, str)`. `NotificationQueue.deliver` semantics honored — enqueue-then-deliver, dequeue+record on success, item stays queued on failure. `still_queued`/`delivered` propagate into `NotifyOutcome` faithfully (delivered→`still_queued=False`; failure→`still_queued=True`; dedup/leak-refusal paths enqueue nothing so `still_queued=False`, and L3.1 confirms the unconfigured path leaves exactly 1 queued item because enqueue precedes the credential check).
- **`run_must_pause` is structurally False on every telegram path:** `notify_condition` always passes `unit_can_proceed=True`, so `must_pause = requires_owner_input and not unit_can_proceed` is always False even for `ask`/`synchronous_stop` conditions. Proven behaviorally (L5.5 checks the audit line's `run_must_pause is False` for `unrecovered_controller_failure`) and structurally (source scan asserts `unit_can_proceed=True` present, `unit_can_proceed=False` absent).
- **`build_notification` leak-refusals reused, not re-implemented:** `notify_condition` catches `NotificationError` and surfaces `error_code`/`detail` without delivering or enqueuing (L2.1 across auth-link / raw-command / source-excerpt shapes; mutation "leak-refusals-leak-through" killed).
- **`TelegramError` vs `NotificationError` handled distinctly:** vocabulary/config/gate failures raise/return `TelegramError` codes; composition leaks are `NotificationError` — the two are caught in the correct places.

## Error paths / isolation (verified)

- **`deliver` never raises** — transport exceptions caught by a deliberate `except Exception` (with justified `# noqa: BLE001 - isolation`) into `(False, "transport <ClassName>")`. L5.2 (raising `TimeoutError`) and mutation "transport-exceptions-escape" confirm containment.
- **Typed, secret-free refusals** — `resolve_credentials` refuses with `telegram_not_configured` naming the env vars but no values; L3.3 confirms `repr`/`str` of `Credentials` are redacted, error messages and `DeliveryResult.detail` never contain the token or `api.telegram.org`.
- **Canary refusal-before-transport ordering** — `cmd_telegram` checks `args.live_canary_authorized_by_owner` and emits a refusal *before* `build_real_transport` is ever called (cli.py lines 59–66); L6.2 confirms the CLI refuses with `live_send_owner_gated` and no send.

## Transport (verified)

- **`build_real_transport` is owner-gated:** raises `live_send_owner_gated` (naming R245 + the exact command) unless `live_send_authorized=True`; that flag is only reachable through the owner-typed `--live-canary-authorized-by-owner`. L6.1/L6.3/R245 confirm; mutation "live-send-gate-removed" killed. No test opens a socket (fake transports / injected `opener`).
- **URL/body/status:** token composes only into the `https://api.telegram.org/bot…/sendMessage` URL; body is `urlencode(chat_id,text,disable_web_page_preview)`; status bucketed `status//100` → 2xx success / Nxx failure; `timeout` plumbed into `open_url(request, timeout=timeout)`. L6.3 verifies URL prefix + `chat_id=` in body + timeout==5.0; L6.3-non2xx verifies a 502 → `5xx` bucket with no token in the detail. `# noqa: S310` justified (fixed https host).

## Findings by severity

### BLOCKING — none.
### MAJOR — none.

### MINOR

**MINOR-1 — CLI sources `NotificationQueue` via a `telegram_sink` re-export instead of its owning module.**
`telegram_sink_cli.py` imports `NotificationQueue` from `.telegram_sink` (line 20–30) while importing `build_notification`, `DELIVERED_KEY`, `QUEUE_KEY` directly from `.notifications` (line 17). `NotificationQueue` is defined in `notifications.py`; `telegram_sink` merely re-exports it. This creates an implicit, fragile public-interface obligation on `telegram_sink` (if a future refactor stops `notify_condition` from using the queue, the CLI import breaks) and is inconsistent with the file's own import style. *Why it matters:* import hygiene / hidden coupling across module boundaries. *Smallest sufficient fix:* import `NotificationQueue` from `.notifications` alongside the other notifications symbols in the CLI. Non-blocking; may have been intentional ("single sink surface"), but the direct import is cleaner.

### INFO (advisory; no action required to pass)

- **INFO-1 — dedup digest scope.** The dedup digest covers `(condition, task_id, summary)` only; two notifications differing solely in `run_id`, `checkpoint_id`, or `where_to_review` deduplicate to one send. This is a documented design choice (report §3) and appropriate for an informational sink, but is worth keeping in mind when the seam wiring emits per-run notifications.
- **INFO-2 — `notification_queue` has no FIFO cap (unlike the dedup register's 64).** The dedup digest is recorded only on *successful* delivery, so during a prolonged Telegram outage repeated detection of the same condition would re-enqueue fresh items (each a new `ntf_…` id) without dedup suppression, and the reused `NotificationQueue` never trims. This is inherited S13.10 "queued-not-lost" behavior and the sink is shadow-only with call sites not yet wired, so it is not blocking — but the seam-wiring unit (M0-T112) should confirm the queue depth is bounded or drained.
- **INFO-3 — composed outbound text is not hard-bounded overall.** `build_notification` bounds only `summary` (400 chars); `reason` and `where_to_review` are redacted/leak-checked but not length-bounded, so `compose_text` has no hard total cap. A pathological `where_to_review` could exceed Telegram's 4096-char message limit and be rejected — but it degrades safely (bucketed 4xx, item stays queued, no raise). No hidden default masks it.
- **INFO-4 — no backoff between the 3 in-call retries.** Acceptable for a single-chat informational sink (no thundering-herd risk) and safe under never-raise + queued-not-lost; noted only for completeness.
- **INFO-5 — `discover_conditions` can report `quota_refusal_hold` twice** if both `usage_limit_record` and `codex_rate_limit_hold` durable records exist simultaneously (one per source key). No send-duplication risk downstream (dedup collapses identical `(condition,task_id,summary)`); arguably correct source-level reporting.

## Verified vs. taken on faith

**Independently verified (this review):** all 31 L-pack tests + 187 adversarial/endurance tests reproduced green; ruff clean; modularity failures 0; diff scope and forbidden-path exclusion; `cli.py` one-import-one-registration constraint; frozen-boundary files untouched; the closed CONDITIONS/CONDITION_RISK maps vs the amendment verbatim; `notify_condition` flow order; retry/`last_attempts`/FIFO-dedup logic; `discover_conditions` filters against the real unit-K/resume_scheduler data shapes; owner-gated transport construction and refusal-before-transport ordering; env-only secret resolution and redaction; `run_must_pause` structural falseness.

**Taken on faith (not re-executed here):** the producer's claim of "mutation 13/13 killed" and the full 2,690-test supervisor suite / 559 non-supervisor baseline (I ran only the three named packs the task specified). These do not affect the code-correctness verdict; the mutation classes named in report §6 map to behaviors I independently confirmed present in source and covered by the reproduced L-pack. Directive requirement-to-evidence for D-024 (R231/R232/R241–R245/R246/R248/R249) is the province of the independent `directive-compliance-verifier` (producer ≠ verifier); from the code side I confirmed R241–R245 and the R248 prohibited-surface scan are satisfied in the deliverable.

**Conclusion:** The implementation is correct, contract-faithful, secret-safe, failure-isolated, owner-gated, and modularity-clean. One MINOR import-hygiene nit and five INFO advisories, none acceptance-blocking. **VERDICT: PASS.**

*(Saved verbatim from the reviewer's return by the orchestrator; transport entity-decoding only — `&lt;`/`&gt;` decoded.)*
