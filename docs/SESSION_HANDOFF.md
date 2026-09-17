# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and reconcile against the remote: **origin may have
advanced; no SHA here is guaranteed current.** This file is orientation only. Operating rules,
gates, and workflow routes live in `CLAUDE.md`.

## Handoff — seq 114: LOOP LIVE on M5-T032 (run 36); monitor-only successor

Turnover reason (owner, VERBATIM): "I want the loop to keep running even after I clear this chat
to start a new season where you monitor just lile now I just like to keep it at around 400k even u"
— i.e. the loop keeps running across the chat clear; the successor monitors exactly as this
session did and itself hands off around 400k context (D-010 R113/R114 rotation ceiling).

Generated 2026-09-17 ~06:20 UTC by session_01SewZxbFqxV3yYhcDb7bMJt. Root
`C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, branch `candidate/D-024-mrl-option-b`,
HEAD `843ab24a` (pushed; CI GREEN after one flaky-test rerun — supervisor-bridge
`test_parallel_requests_never_exceed_limits` failed once on byte-identical code, green on rerun).
Origin `https://github.com/martin10101/nyc-buildability.git`. PR #241 OPEN — NEVER merge.
Dirty at landing: ONLY conventional `.claude/agent-memory/**` + `scratchpad/` (leave them).
Campaign `D-024-fable-codex-loop` active (legacy D-032 campaign files read INVALID — known,
ignore). **214 accepted** (not an MVP percentage — D-059-R006).

## THE LOOP (do not restart it — it is ALREADY RUNNING)

Supervisor pid from `supervisor.lock`, run id **persistent-local-36-m5t032**, worker
claude-opus-4-8 (audit-verified: expected==observed, mismatch False), Codex reviewer gpt-6-astra.
Runtime dir: `%LOCALAPPDATA%\NYCBuildabilitySupervisor\9aca7075…\` (audit.jsonl = event stream).
Launcher: `C:\SupervisorController\autostart-launch.ps1` (orchestrator maintains its ACTIVE-TASK
block; quoting fix + fresh run-id already in the file). Building **M5-T032**: address-search
reliability (handoff §6 defect: distinct 503/429/timeout/no-match/malformed outcomes, bounded
retry, /search action) + ZoLa-first lot links (D-064-R005). Packet already repaired for the five
launch/checkpoint traps — **read `docs/WORKING_KNOWLEDGE.md` "Loop-packet contract for WEB tasks"
BEFORE touching any packet or relaunching.**

## SUCCESSOR DUTIES (this session's exact posture)

1. **Re-arm the loop watcher immediately** (Monitors die with the session): persistent Monitor
   tailing the runtime `audit.jsonl` — grep refused|emergency|halted|unsafe|exhaustion|
   paused_recovery|pending_prompt|hard_deny|final_state|run_complete|task_complete|
   circuit_breaker|budget_exhausted|invalid_checkpoint|undocumented_command|network is denied —
   plus a lock-pid poll and 40-min stall line. Quiet mode: report only breaks/stalls/run-end.
2. **Answer asks fast** (`python -m tools.agent_supervisor pending-approvals|deny|approve-once
   --checkout "C:\SupervisorController"` from `wt-controller-src`; strip \r from digests piped
   via git-bash). Worker should need none after the packet repair; a new undocumented-command or
   WebFetch ask = packet gap, fix the packet (BOTH copies: ctl24 + wt-m5t032), deny, fresh
   run-id if a counter tripped, relaunch.
3. **At the worker's checkpoint/submit seam:** push `task/M5-T032-address-search-links` (worker
   commits locally; CI on the pushed head is the executable authority — thin client, NO local
   npm), capture CI + the dated AS-11 live smoke (GeoSearch autocomplete + /search + one ZoLa
   lot URL) yourself, then normal gates (packet reviewer roster) → accept per the in-regime flow.
4. **Next packet after M5-T032 = spatial diagnosis** (deployed `spatial_intersection_absent`,
   D-059-R004; start BBLs 3052960043 + 3022647515) and it MUST carry the **D-066** wiring:
   regenerate the code graph (`python tools/code_graph/generate.py --repo .`), embed a
   navigation block, tell producer + Codex to use it, record the audited time/token comparison
   vs M5-T032. Then D-045 FAR wiring; D-065 affordable scenarios after that; G6 legal stays owner.
5. Rotate at ~400k with `/session-handoff` (owner standing preference, verbatim above).

## STANDING (unchanged)

D-064: subagents+worker opus-4-8 xhigh, main fable-5, lean comms (CLAUDE.md p19), batched
per-seam testing. B-024 RESOLVED. Open blockers: B-001 (Supabase), B-010, B-011. Holds: PR #241,
expansion §2, Tier D / Section 20. Local full validator starves vs the live worker — use the CI
job for the seam verdict. Deployed services (frontend daca3a0b / backend f0e7d82f on Render,
autoDeploy off) unchanged this session.

## AUTHORITATIVE FILES (smallest set)

`project-control/tasks/M5-T032.json` · `project-control/directives/{D-064,D-065,D-066}-*/` ·
`docs/WORKING_KNOWLEDGE.md` (loop-packet contract) · `.claude/rules/PROGRAM_KNOWLEDGE.md` ·
`C:\SupervisorController\autostart-launch.ps1` (outside repo) · runtime `audit.jsonl`.

## NEXT ACTION (exact)

Verify loop alive (lock pid running) → re-arm the watcher (duty 1) → quiet monitor. Everything
else is event-driven (duties 2–4). Stop for: Tier D items, a repeated identical breaker trip
after one packet fix, or Fable/Opus account exhaustion (open a blocker with the one-line owner
action, never retry past a classifier block).
