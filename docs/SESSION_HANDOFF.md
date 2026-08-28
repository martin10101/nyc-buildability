# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` — and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff — seq 24: M0-T110 (unit K) ACCEPTED; NEXT = M0-T111 (Telegram sink)

1. **Generated:** 2026-08-28 ~22:10Z · orchestrator session `session_01HfptKuEs3RDxaxsSHJjc7t`
   (the seq-23 successor, same session as the M0-T110 unit). **Seam reason:** task acceptance
   (LEAN trigger e). **Sub-agents in flight:** none (all four reviewers — G3 code-reviewer,
   G4 qa-engineer, G5 security-reviewer, DCV — completed reviews AND delta re-attestations;
   reports committed verbatim).
2. **Identity (live at write):** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `control/D-024-fable-codex-loop` (campaign seq **24**), accept-time head `79098ae`.
3. **M0-T110 (unit K) = ACCEPTED** (deliverable `ba25516`, corrections `c8b38ba`, gate wave
   `237be83`, DCV entry at `79098ae`, manifest `0c97eb77`): `/loop-codex` five-subverb channel —
   `codex_channel.py` (state_kv CAS threads incl. concurrent-writer single-winner; R236 bounded
   turn packet with hard byte ceiling + visible trimming + typed refusal; R239 closed six
   dispositions, NO actuation path, attention rows `actuated:False`; R240 owner-gated promotion
   rows `authorizes_nothing:true`) + `codex_channel_cli.py` + reply schema (disposition enum) +
   interceptor extension (exact-anchored; `_codex_argv` fail-closed; correction-round `_CODEX_ID`
   pre-argv id guard) + user-only skill (honest R233: queued-until-turn-end, NOT `/btw`, 45 s
   interception cap, second terminal = real-time; zero-context canary pending-owner-C1). K-pack
   56/56; supervisor suite 2654/0 (2 skipped); non-supervisor 559/1; mutation 16/16 (two
   first-round survivors honestly closed); CI 20/20 twice; ONE consolidated correction round with
   all four SendMessage delta re-attestations PASS; G0/G2/G3/G4/G5 + DCV 13/13. Reports:
   `project-control/reports/M0-T110-{codex-channel,G0-readiness,G2-self-check,G3-code-review,
   G4-qa,G5-security,DCV}{,-delta}.md` + evidence map.
   **Pinned immaterial residuals:** report line count 632 vs 634 (DCV-flagged, accuracy-only);
   boundary queue write-only/inert this unit (reader wiring = later unit); unit-I
   `live_observation.py:296` raw `source_record_key` one-liner still open.
4. **EXACT next action:** claim M0-T111 (deps: M0-T096 accepted) — Amendment-8 unit L, one-way
   Telegram sink; applicable rows R231/R232/R241–R245/R246/R248/R249 (run `evaluate_task_refs`
   at claim to confirm). Bounded sink for EXACTLY the eight conditions (R241); one-way ONLY
   (R242); **bot token + chat id only in an approved local secret mechanism — never
   Git/packets/logs/telemetry/reports/messages (R243)**; redaction + bounded retries + dedup +
   failure isolation so Telegram downtime never stops the loop (R244); reuse
   `notifications.NotificationSink` + `circuit_breakers`/`outage_policy` patterns; stdlib HTTP
   only — NO new dependency; **the real send is an owner-gated exact-command canary (R245):
   build the path + fake-transport proof, never fire live**. Prove-first → implement →
   4-reviewer gates → DCV (10 rows) → accept. Then M0-T112 (golden re-certification at the
   FINAL frozen post-addition identity, R247) BEFORE any R187/R595 activation-package
   presentation; M0-T107 trails non-blocking.
5. **Mechanics (worked this session):** ONE consolidated correction round + SendMessage delta
   re-attestations from the SAME four reviewers; rework→resubmit moves identity; commit reports
   BEFORE recording gates; gate `--sha` == live HEAD; verification entry REPLACES the pending
   placeholder in place and must be stamped at the **accept-time HEAD** (accept fails closed on
   a stale reviewed_sha; restamp is fine — the material manifest is invariant across
   control-plane commits); registry JSON LF; `modularity_check` after `git add`; gitleaks needs
   its own `gitleaks:allow` besides `secretscan:allow` on fake tokens; a follow-up push
   auto-cancels the prior CI run (judge the tip).
6. **Environment:** long background python runs are externally killed — foreground chunks
   (26-file non-supervisor run in one pytest invocation exceeded 30 min; 3 chunks pass);
   never mutate during a live suite.
7. **Standing restrictions:** NEVER merge PR #241 or any pre-existing PR; continuous-mode
   activation owner-gated (R187/R595; supervisor SHADOW-ONLY); Amendment-3 prohibitions;
   Amendment-7 no-wait/no-provoke + labeling; Amendment-8 sequencing (T111→T112 before the
   activation package is presentable; R232/R247); Telegram one-way/secrets/live-canary
   (R242/R243/R245); Bootstrap Gate 0 every session; supervisor commits cite `D-024-R###`;
   repo PUBLIC; never `name:` on producers; expansion-planning hold; `.claude/hooks`
   untouchable sans G5.
8. **Successor must read:** `CLAUDE.md`; this file; `.claude/session-handoff-profile.md`;
   `project-control/campaigns/D-024-fable-codex-loop.json` (seq 24);
   `project-control/tasks/M0-T111.json`;
   `project-control/directives/D-024-fable-codex-loop/source-008-amendment.md` (+ owner report
   `D-024-amendment-8-owner-report.md`); `tools/agent_supervisor/notifications.py` +
   `circuit_breakers.py`/`outage_policy.py` (the reuse boundary); `docs/LEAN_OPERATING_PROCESS.md`.
9. **Stop/change conditions:** Gate-0 failure; validator non-zero; reviewer FAIL/BLOCKED
   (consolidated round → delta re-attestations; M0-T110 is the freshest worked example);
   anything owner-only (credentials, payment, production, legal, PR #241, activation,
   **Telegram bot token/chat id + live send**, live-canary exact-command).
10. **Successor prompt:** *"Work from durable repository evidence only. Verify root =
    C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, branch control/D-024-fable-codex-loop, HEAD,
    tree, and /mcp empty (Bootstrap Gate 0) before any change. Read CLAUDE.md,
    docs/SESSION_HANDOFF.md, .claude/session-handoff-profile.md, and the §8 files. Run
    `python tools/project_control.py status` and `python -m
    tools.agent_supervisor.campaign_continuity --status`. Reconcile against live git + the
    ledger (they win over prose). Continue the campaign seq-24 NEXT: claim M0-T111
    (Amendment-8 unit L, one-way Telegram sink; rows R241–R245 + shared rows) — prove-first
    over notifications/circuit-breaker machinery; secrets only in an approved local mechanism,
    never committed anywhere; live send owner-gated (fake-transport proof only); then
    4-reviewer gates → DCV → accept; then M0-T112 golden re-certification at the FINAL frozen
    identity before any R187/R595 activation-package presentation. Foreground chunks; never
    mutate during a live suite. Do not merge PR #241 or any pre-existing PR; supervisor stays
    SHADOW-ONLY; guards inside .claude/hooks are untouchable without G5. Stop for anything
    owner-only. The standard D-010 R113/R114 ~400k rotate-at-seam ceiling governs your
    session."*
