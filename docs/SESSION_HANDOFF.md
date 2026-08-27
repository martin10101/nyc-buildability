# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` — and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff — R162 discharge DONE (seq 12); M0-T108 in ROUND-3 review; machine on 2.1.247

1. **Generated:** 2026-08-27 UTC · Fable 5 orchestrator, `session_01HfptKuEs3RDxaxsSHJjc7t` ·
   reason: owner-invoked `/session-handoff` (no reason arg). Invoked mid-review: **three healthy
   round-3 reviewers in flight** (see §7) — left running, not killed.
2. **Identity (live):** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `control/D-024-fable-codex-loop`, HEAD `608609c`; tree clean; pushed == origin. Machine claude
   binary is now **2.1.247** (auto-updated 2.1.246→2.1.247 during the R162 canary; this
   orchestrator process still runs 2.1.220). Campaign **seq 12** (frozen `3ca0026`).
3. **This session did:** (a) **DISCHARGED the D-024-R162/R183 statusLine deferral** at observed
   **2.1.247** — dual owner-approved TUI canaries in isolated scratch (round-1 FAILED TRANSPORT,
   preserved 2.1.246 partial; round-2 full 2.1.247 capture, behavioral PASS, permission_mode=auto,
   CHILD_SESSION transcript-absence recorded honestly); masked fixture
   `tools/agent_supervisor/fixtures/statusline_live_2026-08-27_2_1_247_r162_discharge.json` +
   report `M0-T103-R162-discharge-2.1.247.md`; captured owner steering as **D-024 Amendments 4/5/6
   (R192..R219, sentinel `D-024-R162-DISCHARGE`)**; committed `24aa061`, advanced seq 12.
   (b) **Claimed + built M0-T108** (readonly_agent_guard PowerShell/scripting write-gap fix, G5
   M0-T102 MEDIUM).
4. **M0-T108 state:** `awaiting_gate`, claimed by `fable-orchestrator-session`, worktree = primary
   checkout. **Round-3 deliverable identity `e1f6d4c`** (HEAD `608609c` = control-plane records
   only after it). Gate history: G0 PASS, G2 PASS. Round-2 (at `f0bdf7a`): **G3 PASS, G4 PASS,
   G5 FAIL** (F1 COM `-Com` prefix abbreviation → file write; F2 `start`/`saps`-fronted encoded
   shell → DENY→ALLOW regression). Round-3 (at `e1f6d4c`) closed F1 (`-Com\w*`), F2 (`start`/`saps`
   spawn-deny + scoped `_PS_ENCODED_CMD` requiring a co-occurring powershell/pwsh token, no
   `-Encoding` collision), advisory A1 (all `Invoke-Cim/WmiMethod` + `Set/New/Remove-CimInstance`
   denied, `Get-CimInstance` read allowed), and G3 doc/bookkeeping advisories.
5. **M0-T108 evidence (round 3):** PS pack **159/159** (13 RED-on-mutant, all load-bearing); Bash
   pack **136/136 byte-unchanged**; ruff clean; `modularity_check --check` 0 failures (guard 731
   raw lines, not flagged). Only the four packet paths changed (guard, `.claude/settings.json`
   matcher line, PS test pack, report).
6. **Exact next action:** collect the three round-3 verdicts (§7). Save each **verbatim** to
   `project-control/reports/M0-T108-G{3,4,5}-*-round3.md`, record the gate via
   `project_control.py gate --sha <live HEAD>`. **If all PASS:** run the directive-compliance
   verification (DCV) — M0-T108's applicable D-024 set is **EMPTY** (`evaluate_task_refs` ok=true,
   `D-024:ALL` resolves empty; still needs the explicit empty-set task row in `verification.json`);
   then `accept` (needs all required gates PASS + reviewed_sha == live HEAD), `checkpoint`, and
   **advance the campaign to seq 13** (`campaign_continuity.advance(expected_sequence=12, …)`).
   **If any FAIL:** consolidated correction round → re-freeze → re-review (the worked example is
   this session's M0-T108 rounds 1→2→3). **DO NOT dispatch any unit C–I reviewer/producer until
   M0-T108 is ACCEPTED** (owner instruction + G5 M0-T102 precondition).
7. **In-flight sub-agents (round-3 re-review at `e1f6d4c`; healthy, bounded, mutually blind):**
   `code-reviewer` G3, `qa-engineer` G4, `security-reviewer` G5. **These are THIS session's
   background agents — if the session is replaced they die and their verdicts are lost.**
   Resume-or-replace: if this session continues, the orchestrator finalizes on their return; **if
   replaced, the successor RE-DISPATCHES all three round-3 reviews at `e1f6d4c`** (prompts mirror
   the round-2 delta re-reviews: verify F1/F2/A1 closed, no regression, 13 mutants load-bearing;
   G3/G4 confirm PASS holds; independent, do not share conclusions). Do not accept until all three
   round-3 gates are PASS at one frozen identity.
8. **After M0-T108 accepted (campaign NEXT, seq 13):** M0-T104 (unit C native runtime adapter) →
   T105 → T106 → T092 → T094 → T093 → T095 → T096 (golden run; R187 hold after) → T107. Carry the
   R162-discharge unit-C preconditions: explicit child-env control for background dispatch
   (`CLAUDE_CODE_CHILD_SESSION` inheritance), installed-version measured-at-use (drift tooth is RED
   locally 2.1.246→2.1.247 — a 2.1.247 capability re-probe + tooth re-baseline is owed to unit C),
   permission-mode vocabulary accepts `auto`.
9. **Standing restrictions:** NEVER merge PR #241 or any pre-existing PR; **no unit C–I dispatch
   until M0-T108 accepted**; continuous-mode activation owner-gated (D-024 §18/R595); Amendment-3
   prohibitions (no SDK, no MCP servers, no bypass flags, no unbounded fan-out; ledger is
   authority — R146); Bootstrap Gate 0 every fresh session; supervisor commits cite `D-024-R###`;
   repo PUBLIC — mask `[HOME]`; dispatch writing producers as roster types (generic
   `general-purpose` cannot Write; never pass `name:` to a producer).
10. **Owner-visible (non-blocking):** broken npm shim — owner MAY run
    `npm -g uninstall @anthropic-ai/claude-code`; parked session `777b09da` recover via
    `claude attach/respawn 777b09da` when wanted (untouched this session); purge FIVE stale
    pack-repo agent worktrees; repo-hygiene task (worktree field + session-id masking) recommended.
11. **Successor must read:** `CLAUDE.md`; this file; `.claude/session-handoff-profile.md`;
    `project-control/campaigns/D-024-fable-codex-loop.json` (seq 12);
    `project-control/tasks/M0-T108.json`; the M0-T108 gate reports
    (`M0-T108-G3/G4/G5-*.md` incl. the round-2 delta + round-3 saves); `M0-T104.json`.
12. **Stop/change conditions:** Gate-0 failure (no writes, fresh session); validator non-zero;
    reviewer FAIL/BLOCKED (consolidated correction round, re-freeze, delta re-review); anything
    owner-only (credentials, payment, production, legal, PR #241, activation, worktree purge).
13. **Successor prompt:** *"Work from durable repository evidence only. Verify root =
    C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, branch control/D-024-fable-codex-loop, HEAD, tree,
    and `/mcp` empty (Bootstrap Gate 0) before any change. Read CLAUDE.md, docs/SESSION_HANDOFF.md,
    .claude/session-handoff-profile.md, and the §11 files. Run `python tools/project_control.py
    status` and `python -m tools.agent_supervisor.campaign_continuity --status`. Reconcile against
    live git + the ledger (they win over prose). Detect stale/duplicated/completed work. Report
    READY TO RESUME or BLOCKED. M0-T108 is in round-3 independent review at deliverable e1f6d4c: if
    the three round-3 reviewer verdicts are not recorded and the prior session's reviewer agents
    are gone, RE-DISPATCH the three round-3 reviews (G3 code, G4 qa, G5 security) independently at
    the live deliverable identity; save each verbatim; record the gates. If all PASS, run the DCV
    (M0-T108 applicable D-024 set is empty — write the explicit empty-set row), accept, checkpoint,
    and advance the campaign to seq 13; then continue from the campaign NEXT (M0-T104 onward). Do
    NOT dispatch any unit C–I work until M0-T108 is accepted. Stop for anything owner-only."*
