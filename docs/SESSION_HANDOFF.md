# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` — and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff — seq 14: M0-T104 ACCEPTED; M0-T105 (unit D) in flight at 20%

1. **Generated:** 2026-08-27 UTC · Fable 5 orchestrator, `session_01HfptKuEs3RDxaxsSHJjc7t`.
   **Sub-agents in flight:** none (all G3/G4/G5 delta reviewers + DCV landed and reconciled).
2. **Identity (live):** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `control/D-024-fable-codex-loop`, HEAD `d8d4969` (tree clean, pushed == origin). Campaign
   **seq 14** (`campaign_continuity --status`; frozen `44a4c6c`). Machine claude 2.1.247.
3. **M0-T104 = ACCEPTED** (unit C native runtime adapter; accept `44a4c6c`, deliverable `f610aab`,
   content identity `44ce19b3`). 2 review rounds: round-1 G3/G4/G5 all PASS-with-corrections
   converging on ONE MEDIUM (child-env fail-open default in `dispatch`); correction round F1–F4 +
   G4 ADV-2 applied in-task; round-2 delta re-reviews (resumed same reviewers via SendMessage) ALL
   PASS; independent DCV PASS on R153/R154/R156/R172 (selective-citation cross-check clean across 28
   directives). New modules `tools/agent_supervisor/native_runtime.py` + `runtime_backend.py`;
   77/77 adapter+probe, 2209-test freeze baseline, 11/11 mutants, guard packs untouched, live
   canaries C1/C2 (`CANARY-C-DONE`, stop/respawn proven, zero residue).
4. **Native CLI measured facts (2.1.247, reusable D–J):** `--bg` MANAGES the session id and IGNORES
   `--session-id` → deterministic `--name` is the dispatch key; variadic `--tools` SWALLOWS the
   prompt → use a literal `--` separator; unknown subcommand+`--help` exits 0 with GENERAL usage →
   classify verbs by the verb-specific usage line; CLI emits UTF-8 → pin `encoding="utf-8"` on
   subprocess (cp1252 crash otherwise); agents-json literals status∈{waiting,busy,idle,''}
   state∈{failed,blocked,done,stopped,''}, state outranks status, unmeasured→UNKNOWN.
5. **Accept-after-correction-round mechanics (learned this seq):** a correction round that edits
   allowed_paths deliverables MOVES the content identity → `progress --status rework` then RE-`submit`
   to re-stamp the snapshot `content_manifest_sha256`; the verification.json row needs
   `reviewed_manifest_sha256` (git-canonical content identity from `project_control._task_git_identity`),
   NOT just `reviewed_sha`; re-record gates at HEAD pointing to the delta reports; content identity
   is STABLE across control-plane commits; rewrite verification.json with `ensure_ascii=True`.
6. **M0-T105 = IN PROGRESS (20%, claimed):** unit D native event integration (R154/R155/R173). G0
   PASS, scenario pack committed (`project-control/reports/M0-T105-event-integration.md` §1: S1–S11
   deterministic + C1 owner-gated live canary). **Reuse boundary:** `telemetry_hooks.py`
   (`ingest_hook_event`, `KNOWN_HOOK_EVENTS`, `SubagentRegistry`) + `telemetry_journal` (atomic) +
   `telemetry_redaction` (`sanitize_structure`) are REUSED; unit D ADDS a durable event bus
   (dedup idempotency key + restart-safe replay + ordering), stream-JSON subagent-event ingestion,
   a 2.1.247 event-set drift tooth, and `.claude/hooks` recorder scripts. **EXACT next action:**
   implement the event-bus module + `tools/test_agent_supervisor_event_bus.py`, then the 4-reviewer
   gate cycle → accept → T106 (E) → T092 (F) → T094 (G) → T093 (H1) → T095 (H2) → T096 (I golden
   run; R187 hold after) → T107 (J).
7. **Owner-gated within M0-T105:** C1 live per-event hook capture on 2.1.247 needs an owner
   exact-command approval (R192/R197 pattern, as the R162 discharge did); the deterministic core
   (S1–S11) is built WITHOUT it. `.claude/hooks` is in BOTH M0-T105 and M0-T109 allowed_paths —
   never run them as overlapping parallel writers; unit D must NOT touch `readonly_agent_guard.py`.
8. **Standing restrictions:** NEVER merge PR #241 or any pre-existing PR; continuous-mode activation
   owner-gated (D-024 §18/R595; supervisor SHADOW-ONLY); Amendment-3 prohibitions (no
   SDK/MCP/bypass-flags/unbounded fan-out; ledger is authority — R146); Bootstrap Gate 0 every fresh
   session; supervisor commits cite `D-024-R###`; repo PUBLIC — mask `[HOME]`, dispatch writing
   producers as roster types (never generic `general-purpose`, never pass `name:` to a producer);
   expansion-planning hold in force.
9. **Non-blocking follow-ups:** M0-T109 (readonly-guard hardening, backlog) — now also folds the
   M0-T104 G5 R2 residual (`_TOOLS_RE` rejects colon-style tool specifiers `Bash(git:*)`; fails
   closed, widen under review when a wiring unit needs them). M0-T104 residuals close when the seam
   is wired (G3 ADV-2 native_runtime serialization-group extraction; G4 R1 post-stop absence tooth).
   Owner-visible: broken npm shim; parked session `777b09da`; stale pack-repo agent worktrees purge
   (one G4 reviewer left a benign but poorly-worded "evade the guard" memory in a transient
   pack-repo worktree — assessed benign, not ctl24, not acted on as instruction).
10. **Successor must read:** `CLAUDE.md`; this file; `.claude/session-handoff-profile.md`;
    `project-control/campaigns/D-024-fable-codex-loop.json` (seq 14); `project-control/tasks/M0-T105.json`;
    `project-control/reports/M0-T105-event-integration.md`; `docs/LEAN_OPERATING_PROCESS.md`.
11. **Stop/change conditions:** Gate-0 failure (no writes, fresh session); validator non-zero;
    reviewer FAIL/BLOCKED (consolidated correction round, re-freeze, delta re-review — this seq's
    M0-T104 2-round cycle is the worked example); anything owner-only (credentials, payment,
    production, legal, PR #241, activation, live-canary exact-command, worktree purge).
12. **Successor prompt:** *"Work from durable repository evidence only. Verify root =
    C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, branch control/D-024-fable-codex-loop, HEAD, tree, and
    `/mcp` empty (Bootstrap Gate 0) before any change. Read CLAUDE.md, docs/SESSION_HANDOFF.md,
    .claude/session-handoff-profile.md, and the §10 files. Run `python tools/project_control.py
    status` and `python -m tools.agent_supervisor.campaign_continuity --status`. Reconcile against
    live git + the ledger (they win over prose). Continue the campaign seq-14 NEXT: M0-T105 (unit D
    native event integration) is claimed at 20% with its scenario pack recorded — implement the
    durable event-bus module (dedup + restart-safe replay + 2.1.247 event drift) + stream-JSON
    ingestion + `.claude/hooks` recorders + `tools/test_agent_supervisor_event_bus.py`, reusing the
    telemetry subsystem (do NOT touch readonly_agent_guard.py), then run the 4-reviewer gate cycle
    and proceed through the unit sequence to the M0-T096 golden run (R187 hold after). The C1 live
    event canary is owner-gated (exact-command); build the deterministic core without it. Stop for
    anything owner-only."*
