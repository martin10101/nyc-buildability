# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` — and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff — M0-T108 ACCEPTED (seq 13); clean seam; NEXT = M0-T104 (unit C) onward

1. **Generated:** 2026-08-27 UTC · Fable 5 orchestrator, `session_01HfptKuEs3RDxaxsSHJjc7t` ·
   reason: owner-invoked `/session-handoff` (no reason arg). **Zero sub-agents in flight** (all
   round-4 reviewers + the DCV landed and are reconciled). Clean seam.
2. **Identity (live):** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `control/D-024-fable-codex-loop`, HEAD `86f521e`; tree clean; pushed == origin. Machine claude
   binary 2.1.247 (this orchestrator process still 2.1.220). Campaign **seq 13**
   (`campaign_continuity --status`; frozen `faa46e3`).
3. **This session:** (a) discharged the D-024-R162/R183 statusLine deferral at observed 2.1.247
   (seq 12, commit `24aa061`; Amendments 4/5/6 = R192..R219); (b) **took M0-T108 through 4
   independent review rounds to ACCEPTANCE** (readonly_agent_guard PowerShell/scripting write-gap
   fix; G5 M0-T102 MEDIUM closed).
4. **M0-T108 = ACCEPTED** (accept commit `faa46e3`; deliverable identity `b6db457`; content-manifest
   `90376158…`). All required gates PASS (G0/G2/G3/G4/G5). 4 rounds (each independent G5 hunt found
   NEW bypasses the prior fix introduced): r1 G3/G5 FAIL → r2 G5 FAIL (COM `-Com` prefix, encoded
   shell) → r3 G3/G5 FAIL (D-R3-1 `-Encoding` FP, NF1 COM `-C/-Co`+reflection, NF2 assignment-fronted
   encoded shell) → **r4 ALL PASS** via one root-cause change: match tokens in COMMAND/SPAWN
   position, not as data (`_effective_command_token` strips a leading `$var=`; `_launches_nested_shell`
   covers powershell/pwsh/cmd + `start`/`saps` `_SPAWN_ALIAS`; COM floor `New-Object -c\w*` +
   `[Activator]::CreateInstance` reflection). PS pack 187/187 (15 RED-on-mutant); Bash 136/136
   byte-unchanged. D-024 applicable set EMPTY — independent DCV PASS (resolver + raw-JSON re-matcher
   + all-28-directive selective-citation cross-check); validator EXIT=0. The extended readonly guard
   now machine-enforces PowerShell + Bash read-only for reviewer roles.
5. **Follow-up M0-T109** (`backlog`, non-blocking, does NOT gate unit C): guard hardening — G5
   ADV-R4-1 (chained-assignment `$a=$b=powershell -enc` residual: loop the `$var=` strip in
   `_effective_command_token`); G4 ADV-4 (the `GetTypeFromProgID` tooth is unreachable behind `::`
   — make reachable or remove as redundant with the reachable `[Activator]::CreateInstance`); G5
   ADV-R4-2 (document `[Type]::GetTypeFromCLSID` and `&(gcm powershell)` open-ended residuals). All
   were documented residuals at accept, covered by the orchestrator-only integration model.
6. **EXACT next action (seq 13 NEXT = M0-T104):** claim **M0-T104** (unit C native runtime adapter)
   → T105 (D) → T106 (E) → T092 (F) → T094 (G) → T093 (H1) → T095 (H2) → T096 (I golden run; R187
   hold after) → T107 (J). **Unit C carries the R162-discharge preconditions:** explicit child-env
   control for background dispatch (`CLAUDE_CODE_CHILD_SESSION` inheritance — Start-Process children
   inherit it and save no transcript); installed-version measured-at-use (machine auto-updated
   2.1.246→2.1.247 mid-session; a **2.1.247 capability re-probe + drift-tooth re-baseline is owed** —
   the local drift tooth is RED against the committed 2.1.246 fixture, CI green via claude-absent
   skip); permission-mode vocabulary accepts `auto` (no literal `default` mode on 2.1.24x). M0-T109
   may be sequenced anytime in parallel (non-blocking). **Unit C–I dispatch is now UNBLOCKED**
   (M0-T108 acceptance was the gate).
7. **Standing restrictions:** NEVER merge PR #241 or any pre-existing PR; continuous-mode
   activation owner-gated (D-024 §18/R595; supervisor SHADOW-ONLY); Amendment-3 prohibitions (no
   SDK/MCP servers/bypass flags/unbounded fan-out; ledger is authority — R146); Bootstrap Gate 0
   every fresh session; supervisor commits cite `D-024-R###`; repo PUBLIC — mask `[HOME]`, dispatch
   writing producers as roster types (generic `general-purpose` cannot Write; never pass `name:` to
   a producer; PowerShell mutations now blocked for reviewer roles by the M0-T108 guard).
8. **Owner-visible (non-blocking):** broken npm shim — owner MAY `npm -g uninstall
   @anthropic-ai/claude-code`; parked session `777b09da` recover via `claude attach/respawn`
   (untouched this session); purge FIVE stale pack-repo agent worktrees; repo-hygiene task
   (worktree field + session-id masking) recommended.
9. **Successor must read:** `CLAUDE.md`; this file; `.claude/session-handoff-profile.md`;
   `project-control/campaigns/D-024-fable-codex-loop.json` (seq 13); `project-control/tasks/M0-T104.json`;
   `project-control/tasks/M0-T109.json`; `docs/LEAN_OPERATING_PROCESS.md`;
   `project-control/reports/M0-T103-R162-discharge-2.1.247.md` (unit-C preconditions).
10. **Stop/change conditions:** Gate-0 failure (no writes, fresh session); validator non-zero;
    reviewer FAIL/BLOCKED (consolidated correction round, re-freeze, delta re-review — this
    session's M0-T108 4-round cycle is the worked example); anything owner-only (credentials,
    payment, production, legal, PR #241, activation, worktree purge).
11. **Successor prompt:** *"Work from durable repository evidence only. Verify root =
    C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, branch control/D-024-fable-codex-loop, HEAD, tree,
    and `/mcp` empty (Bootstrap Gate 0) before any change. Read CLAUDE.md, docs/SESSION_HANDOFF.md,
    .claude/session-handoff-profile.md, and the §9 files. Run `python tools/project_control.py
    status` and `python -m tools.agent_supervisor.campaign_continuity --status`. Reconcile against
    live git + the ledger (they win over prose). Detect stale/duplicated/completed work. Report
    READY TO RESUME or BLOCKED. If ready, continue from the campaign seq-13 NEXT: claim M0-T104
    (unit C native runtime adapter) and proceed through the unit sequence to the M0-T096 golden run
    (R187 hold after), carrying the unit-C preconditions (child-env control, 2.1.247 capability
    re-probe + drift-tooth re-baseline, permission-mode `auto`); M0-T109 guard-hardening is a
    non-blocking parallel follow-up. Do not repeat completed work or broaden scope; stop for
    anything owner-only."*
