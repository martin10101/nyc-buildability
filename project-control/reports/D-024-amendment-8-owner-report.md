# D-024 Amendment 8 — owner report (Codex discussion channel + Telegram sink + re-certification)

Recorded 2026-08-28 at capture (unit-I deliverable `5ff7f08`, M0-T096 claimed/in_progress,
pre-submit); the R249 return items. Validator EXIT=0 at capture; rows R231–R249;
verbatim source `source-008-amendment.md`.

## 1. Already authorized, or a new amendment?

**A new amendment was required and is now captured (rows R231–R249).** The two capabilities,
the closed disposition vocabulary, the Telegram secrets/one-way/failure-isolation rules, the
/btw honesty prohibition, and the post-addition re-certification sequencing exist nowhere in
R001–R230. Overlaps are reuse, not authorization: R083/R084/R088/R089 built the `/loop-*`
surface and its honest interception limits; R093/AD-083 bound review packets; R146's
prohibition list is restated by R248 with one addition (no global Claude settings
modification); the prior notification posture (terminal sink only, remote owner-gated) is
narrowed by the explicit one-way Telegram authorization with its own owner-gated live-send
canary (R245). **M0-T096's claimed contract is unchanged (R246)** — the new rows bind only to
the new tasks.

## 2. Proposed bounded task sequence (captured durably as ledger packets)

1. **M0-T096 (in flight, scope unchanged):** finish unit I exactly as contracted — golden run,
   watcher, activation-package DOCUMENT, gates, DCV, accept.
2. **M0-T110 — Codex discussion channel** (R233–R240; depends M0-T096): `/loop-codex`
   new/continue/show/promote/close; thread persistence; bounded per-turn context; closed
   dispositions; owner-gated promotion.
3. **M0-T111 — Telegram sink** (R241–R245; depends M0-T096): one-way, eight conditions,
   secrets in an approved local mechanism, failure isolation; live send stays an owner-gated
   exact-command canary. (T110 and T111 are independent scopes; they run sequentially by
   default — one cohesive writer task at a time, R188 — T110 first.)
4. **M0-T112 — final golden re-certification** (R247; depends M0-T110+M0-T111): re-run the
   golden-run pack + affected suites + whole suite + CI against the FINAL frozen identity;
   refresh the activation package's identity/evidence items; ONLY THEN is the R187/R595
   activation package presented.
5. **M0-T107 (unit J, plugin portability plan)** stays non-blocking and trails after M0-T112
   (or wherever the owner prefers; it gates nothing).

## 3. Existing components reused (no duplicate machinery)

- **Command surface + interception:** the unit-G `/loop-*` architecture — user-only skills
  (`disable-model-invocation: true`), the `loop_command_interceptor.py` UserPromptSubmit hook
  (exact-match, block, user-visible output, prompt erasure), `operator_channel_cli.py`
  wiring, and the measured 2.1.248 detection fixture.
- **Codex invocation:** `codex_reviewer` (read-only argv, forbidden flags, schema-validated
  output, timeouts, identity binding) — the discussion turn is a bounded read-only Codex call
  exactly like `ask`, which already provides the durable `queued_asks` fallback rows.
- **Per-turn context:** `evidence.build_packet` + `review_packet` (AD-083 prohibited-content
  guard + the 0A.4 token budget), `campaign_continuity`/`operator_status` fresh-state facts,
  `redaction`/`telemetry_redaction`, `models.digest_of` frozen identities, and the code-graph
  reference surfaces for symbols/paths/digests (R238).
- **Thread persistence:** `durable_state.state_kv` register rows (the CAS/idempotency
  conventions the watcher just re-proved) — no new database.
- **Telegram:** the `notifications.NotificationSink` boundary (fixed redacted bounded field
  set; a failed delivery leaves the item queued) + `circuit_breakers`/`outage_policy`
  patterns for bounded retry/dedup/failure isolation; stdlib HTTP only — **no new
  dependency**, so no admission cycle is expected (any dependency would trigger the full
  dependency-security policy instead).
- **Certification:** the M0-T096 golden-run pack (`test_agent_supervisor_golden_run.py`) IS
  the re-runnable certification harness M0-T112 re-executes.

## 4. The exact official limitation (same-terminal mid-turn custom commands)

Per current official Claude Code behavior: **an ordinary command submitted while Claude is
responding is QUEUED until the current turn ends; `/btw` is a special BUILT-IN command that
surfaces mid-turn.** Custom skills/hooks (our `/loop-*`, the future `/loop-codex`) are
ordinary commands: their UserPromptSubmit interception fires only when the prompt is actually
submitted/processed, so **mid-turn, same-terminal real-time interaction is NOT available
through them**, and no custom command will be represented as `/btw`-equivalent without a
measured installed-version fixture (R233). The honest real-time path while a producer is
responding remains the second terminal (`status`/`ask`/`pause`/`graceful-stop`/
`emergency-stop`); the zero-context interception proof itself is still pending-owner-C1.

## 5. Certification to re-run after these additions (R247)

Both additions touch `tools/agent_supervisor/**` and the operator channel, so they invalidate
the affected final certification taken at any earlier identity. M0-T112 therefore re-runs, at
the FINAL frozen post-addition identity: the **full golden-run pack** (two-unit golden run,
rotation, controller restart, injected faults, watcher, registers), the **affected packs**
(operator channel, notifications, reviewer, plus the new T110/T111 suites), the **whole
supervisor suite** (freeze-rule baseline), and **CI on the pushed SHA**; then refreshes the
activation package's identity/evidence items (10–12). The R187/R595 activation package is
presented only after M0-T112 is accepted. Independent-review verdicts for T110/T111/T112
each attach to their own frozen identities per the standard gates.
