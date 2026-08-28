# M0-T111 — unit L: one-way Telegram notification sink (owner-gated live send)

D-024 Amendment 8, applicable rows **R231, R232, R241–R245, R246, R248, R249** (10).
Supervisor-freeze qualifying evidence: **D-024-R232/R241** (packet + commits).
Producer: fable-orchestrator-session (campaign seq 24). Claim seam: G0 PASS at `c90d9c1`,
claimed at `7db5182`.

## 0. Reuse boundary (R241 "bounded sink"; no duplicate machinery)

| Reused surface | Where | What unit L takes from it |
|---|---|---|
| View-only notification contract | `notifications.build_notification` (S13.10) | fixed field set (no attachment slot), redaction of every text field, `assert_view_only` leak-shape REFUSAL (auth links, raw commands, source excerpts, private paths), hard 400-char summary bound, closed `RISK_CLASSES`. The Telegram sink can only ever carry what this builder admits. |
| Sink boundary + queued-not-lost | `notifications.NotificationSink` + `NotificationQueue.deliver` | the sink interface (deliver → (ok, detail)); a failed delivery LEAVES THE ITEM QUEUED and never loses it; `run_must_pause` stays False for one-way informational delivery — Telegram downtime can never stop the loop (R244). |
| Durable registers | `durable_state` `state_kv` + CAS | the dedup register + queue/delivered rows (existing `notification_queue`/`notification_delivered` keys), same conventions units I/K re-proved. |
| Redaction | `redaction.redact_text` (via the builder) + payload-composition rules here | secrets never compose into any stored/displayed artifact. |
| Backoff shape precedent | `outage_policy.BackoffPolicy` / `RetryState` (pattern) | bounded-attempt discipline; unit L's retries are a small bounded in-call loop (no background scheduler — one-way informational). |
| Audit | `AuditLog` via `NotificationQueue._audit` | delivery/failure events carry ids + sink + risk class, never payload text, never credentials. |
| CLI seam | `register_*_verbs` pattern (units G/K) | a focused `telegram_sink_cli.py` registered by one import + one call in `cli.py`. |
| Transport | **stdlib `urllib.request` only** | NO new dependency (a dependency would trigger the full admission policy; none is taken). |

**Prove-first executions (settled tree at the claim seam):** the packs covering
`build_notification`/`NotificationQueue` — `test_agent_supervisor_adversarial.py` +
`test_agent_supervisor_endurance.py` → **187/187 passed** (leak-shape refusals, queued-not-lost,
pause semantics), plus `test_agent_supervisor_phase1.py` 80/80. The unit-K acceptance re-proved
the `state_kv` CAS conventions the dedup register uses.

## 1. The eight conditions (R241 — closed vocabulary) and their sources

`CONDITIONS` is a closed 8-tuple; any other value is a typed refusal (never defaulted,
mirroring the unit-K disposition rule):

| Condition | Risk class | Source in THIS unit |
|---|---|---|
| `stop_for_owner` | ask | **passively derivable:** unit-K attention rows (`codex_channel/attention/*`, disposition STOP_FOR_OWNER, `actuated: False`) via `discover_conditions(journal)` |
| `quota_refusal_hold` | notify | **passively derivable:** the durable `usage_limit_record` (resume_scheduler) / `codex_rate_limit_hold` via `discover_conditions(journal)` |
| `approval_waiting` | ask | loop-emitted at the seam (`notify_condition`) — WAIT_FOR_OWNER is a state-machine condition, not a single durable key |
| `breaker_open_stuck` | notify | loop-emitted — `CircuitBreakers` is in-memory by design |
| `repeated_ci_failure` | notify | loop-emitted (CI verdicts arrive through the flow, not a durable register) |
| `unrecovered_controller_failure` | synchronous_stop | loop-emitted by recovery |
| `golden_run_complete` | info | loop-emitted at the golden-run epilogue |
| `campaign_complete` | info | loop-emitted at campaign close |

Honest bound (same posture as the unit-K boundary queue): this unit delivers the SINK and its
single entry (`notify_condition`) plus read-only discovery for the two passively-derivable
conditions; emitting call sites inside the (shadow-only) loop are later wiring at the seam.
Nothing here invents an event that did not durably occur.

## 2. Secrets (R243 — hard rule; the repository is PUBLIC)

- The bot token and chat identifier live ONLY in the owner's local environment
  (`SUPERVISOR_TELEGRAM_BOT_TOKEN`, `SUPERVISOR_TELEGRAM_CHAT_ID`) — the same approved
  local mechanism as the provider inputs (`SUPERVISOR_CODEX_EXECUTABLE` etc., unit G):
  set in the owner's shell, never a repository file, never discovered from anywhere else.
- `resolve_credentials()` returns a holder whose `repr`/`str` are redacted placeholders;
  the token/chat id compose ONLY into the HTTPS request itself (Bot API URL + form body)
  and never into: notification fields, queue/delivered/dedup rows, audit lines,
  `DeliveryResult.detail`, exception messages, CLI output (`telegram status` reports
  configured yes/no ONLY), or this report. Error details carry HTTP status classes, never
  URLs (the Bot API URL embeds the token).
- Tests use sentinel fake values and assert their ABSENCE from every stored/displayed/
  audited artifact (leak-absence pattern; sentinels carry the standard scanner pragmas).

## 3. One-way + owner-gated live send (R242/R245) — decision record

- **One-way only (R242):** the module exposes NO receive path — no `getUpdates`, no webhook,
  no command parsing, no approval/merge/execution/config surface; the transport is called
  with the `sendMessage` method only. A source-scan test enforces this permanently.
- **Owner-gated live send (R245):** the REAL transport cannot be constructed without
  `live_send_authorized=True`, which only the owner-typed CLI flag
  `--live-canary-authorized-by-owner` sets; without it construction raises typed
  `live_send_owner_gated` naming R245 and the exact owner command. This unit NEVER fires a
  live send: every test injects a fake transport (or a fake opener into the real transport
  to prove URL/body shape without a socket). The documented owner canary command is:
  `python -m tools.agent_supervisor telegram canary --live-canary-authorized-by-owner`
  (runs ONE fixed, bounded, view-only canary notification; refuses when env is missing).
- **Failure isolation (R244):** `deliver` catches transport exceptions into `(False, class
  name + status class)`; bounded retries (`MAX_DELIVERY_ATTEMPTS = 3`) inside the call with
  a hard per-attempt timeout; after the bound the item REMAINS QUEUED (existing S13.10
  semantics) and the call RETURNS — it never raises into the loop, never pauses it
  (`run_must_pause` is structurally False for the one-way sink).
- **Deduplication (R244):** a digest over (condition, task_id, summary) is CAS-recorded in a
  bounded durable register (`telegram_dedup`, FIFO-trimmed); an exact repeat is skipped with
  a visible `deduplicated` result, never re-sent silently.

## 4. Scenario matrix (executable pack: `tools/test_agent_supervisor_telegram_sink.py`)

| # | Class | Scenario | Kind |
|---|---|---|---|
| L1.1 | conditions | all eight accepted, each mapped to its fixed risk class | primary |
| L1.2 | conditions | unknown condition → typed refusal, never defaulted | failure |
| L1.3 | conditions | `discover_conditions`: STOP_FOR_OWNER attention row + usage-limit record found; empty journal → none; discovery is read-only | primary |
| L2.1 | view-only | notification built via the S13.10 builder; auth-link/raw-command/excerpt/private-path summaries REFUSED | primary |
| L2.2 | view-only | summary hard-bounded; every text field redacted | boundary |
| L3.1 | secrets | missing env → typed `telegram_not_configured`; item queued, loop unaffected | failure (R243) |
| L3.2 | secrets | sentinel token/chat id absent from notification rows, queue/delivered/dedup rows, audit lines, DeliveryResult.detail, CLI output | primary (R243) |
| L3.3 | secrets | credentials holder repr/str redacted; transport error messages carry status classes, never the URL | primary (R243) |
| L4.1 | one-way | source scan: no getUpdates/webhook/receive/approval surface; transport called with sendMessage only | primary (R242) |
| L5.1 | isolation | transport failing all attempts → exactly MAX_DELIVERY_ATTEMPTS calls, item REMAINS QUEUED, call returns (no raise) | primary (R244) |
| L5.2 | isolation | transport RAISING (socket error) → same contained result | failure (R244) |
| L5.3 | isolation | success after one failure → delivered, dequeued, audit records attempts | boundary |
| L5.4 | dedup | identical (condition, task, summary) → second call visibly `deduplicated`, one delivery total; register bounded (FIFO trim) | primary (R244) |
| L5.5 | isolation | `run_must_pause` is False on every telegram path | primary (R244) |
| L6.1 | canary | real transport without the authorization flag → typed `live_send_owner_gated` naming R245 + the exact command | primary (R245) |
| L6.2 | canary | CLI `telegram canary` without the flag → refusal naming the exact command; WITH flag but no env → `telegram_not_configured` (no send) | failure (R245) |
| L6.3 | canary | authorized real transport with an injected fake opener → correct Bot API URL shape + chat_id in body + hard timeout; no socket in tests | primary |
| L7.1 | CLI | `telegram status`: configured yes/no (no values), queue depth, dedup count; registered on the existing surface; output redacted | primary |
| L8 | register | executable requirement register: one row per applicable req (10) | primary (R249 pattern) |

## 5. Module plan (modularity answers)

1. Owning responsibility: outbound owner notification over Telegram — a transport + condition
   vocabulary layer on the EXISTING notification boundary; distinct from composition (stays in
   `notifications.py`) and from event detection (loop's business).
2. Modules: `tools/agent_supervisor/telegram_sink.py` (conditions, credentials, transport,
   dedup, notify_condition, discovery; target < 450 SLOC) + `telegram_sink_cli.py` (status +
   canary verbs; target < 200 SLOC). `cli.py` grows one import + one registration line.
3. Threshold check: far below warn; `modularity_check` after `git add`.
4. Nothing moved; nothing to extract.
5. Stable interface: `register_telegram_verbs(sub, add_common)` + module functions; the
   `NotificationSink` contract is implemented, not modified.
6. Boundary tests: the L-pack; notifications-covering packs must stay green (adversarial +
   endurance 187, phase1 80).
7. CI modularity check must pass before submission.

## 6. Evidence (filled at implementation/submission)

- (pending) L-pack run; affected packs; suites; mutation; ruff; modularity; CI.
