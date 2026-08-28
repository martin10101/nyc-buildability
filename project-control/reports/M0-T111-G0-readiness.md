# M0-T111 — G0 readiness (administrative; recorded at the claim seam)

Task: M0-T111 (unit L: one-way Telegram notification sink, owner-gated live send;
D-024 Amendment 8, rows R231/R232/R241–R245/R246/R248/R249).
Recorded by: orchestrator (fable-orchestrator-session), 2026-08-28, campaign seq 24.
Supervisor-freeze qualifying evidence: **D-024-R232/R241** (packet-named, Amendment 8).

1. **Bootstrap Gate 0 (R125–R128):** passed at session start (primary cwd IS the worktree
   root `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, branch `control/D-024-fable-codex-loop`,
   NO MCP tools attached) and re-verified at this seam: clean tree, local == origin at
   `6662b88` (CI 20/20 green there).
2. **Dependencies:** M0-T096 is `accepted`; M0-T110 (unit K) accepted at seq 24; campaign
   seq 24 names M0-T111 as the authorized NEXT (M0-T112 follows; M0-T107 trails
   non-blocking).
3. **Packet integrity:** outputs/allowed/forbidden paths present; directive_refs `D-024:ALL`;
   `evaluate_task_refs` resolves ok=true, **10 applicable ids** (R231, R232, R241–R245,
   R246, R248, R249), no missing/invalid/unresolved (selective-citation guard satisfied at
   claim). Acceptance scenarios follow the unit-K precedent: executable prove-first pack
   (`tools/test_agent_supervisor_telegram_sink.py`) rather than packet JSON rows.
4. **Scope sanity:** allowed_paths cover `tools/agent_supervisor` (sink module),
   `tools/test_agent_supervisor_telegram_sink.py`, and the report. `.claude/hooks` is a
   FORBIDDEN path this time (no interception work in this unit); no settings, no MCP, no
   dependency manifest — the plan is stdlib-HTTP-only over the existing
   `notifications.NotificationSink` boundary + `circuit_breakers`/`outage_policy` patterns
   (any new dependency would trigger the full admission policy instead and is NOT planned).
5. **Secrets discipline staged (R243 — hard rule):** the bot token and chat id live ONLY in
   an approved local secret mechanism (environment/local config OUTSIDE the repository,
   never a committed file); no secret value ever appears in Git, packets, logs, telemetry,
   reports, or messages; tests use fake values with the standard leak-absence pattern.
   The repository is PUBLIC — doubly enforced by gitleaks + the CI credential scan.
6. **One-way + canary discipline staged (R242/R245):** no Telegram approvals, merges, code
   execution, or configuration changes in this unit; the send path is built and proven
   against a FAKE transport only; a real Telegram send remains an owner-gated
   exact-command canary that this unit never fires.
7. **Failure isolation staged (R244):** redaction before composition, bounded retries,
   deduplication, and failure isolation such that Telegram downtime can never stop or slow
   the coding loop (queued-not-lost semantics on the existing sink boundary).

Verdict: **PASS** (administrative readiness; independent review comes at G3/G4/G5 + DCV).
