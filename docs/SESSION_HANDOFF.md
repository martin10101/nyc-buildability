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
   checkout. **Round-3 deliverable identity `e1f6d4c`** (HEAD moved on: control-plane records +
   this handoff after it — re-derive live). Gate history: G0 PASS, G2 PASS. Round-2 (`f0bdf7a`):
   G3 PASS, G4 PASS, **G5 FAIL** (F1 COM `-Com` prefix → file write; F2 `start`/`saps`-fronted
   encoded shell → DENY→ALLOW regression). Round-3 (`e1f6d4c`) closed F1 (`-Com\w*`), F2, A1 — but
   **G3 round-3 = FAIL (recorded)**: new defect **D-R3-1** — the F2 scoped encoded-check
   (`_PS_ENCODED_CMD` matches `-Encoding` since `-enc` is its prefix; `_PS_HAS_SHELL` matches the
   word `powershell`/`pwsh` anywhere as DATA) newly DENIes pure `-Encoding` reads that mention
   `powershell`/`pwsh` (e.g. `Select-String -Encoding utf8 -Pattern powershell`) — a narrowed
   re-open of the previously-blocking C3 FP. **Fails safe** (over-blocks a read, opens NO write);
   F1/F2/A1 security teeth all correct; verified at `e1f6d4c`. **G4 round-3 = PASS (recorded)** but
   flags **ADV-3 (fail-OPEN, round-4 blocking):** the F1 COM tooth `New-Object -Com\w*` misses the
   shorter valid abbreviations `-c`/`-co` (PowerShell binds them to `-ComObject` — no other
   New-Object param starts with "c"), so `New-Object -c Scripting.FileSystemObject` → ALLOW = the
   same COM file-write bypass class as the round-2 G5 F1 (verified at `e1f6d4c`; pre-existing since
   round-2, strictly narrowed by round-3). G4 also flags fail-safe over-blocks ADV-1 (`start`/`saps`
   alias denies the word "start" as data, e.g. `git log --grep start`) and ADV-2 (= D-R3-1 root
   cause). **G5 round-3 STILL IN FLIGHT.**
5. **M0-T108 evidence (round 3):** PS pack **159/159** (13 RED-on-mutant, all load-bearing); Bash
   pack **136/136 byte-unchanged**; ruff clean; `modularity_check --check` 0 failures (guard 731
   raw lines, not flagged). Only the four packet paths changed.
6. **Exact next action (ROUND-4 required):** (a) collect the G5 round-3 verdict (§7), save
   verbatim, record the gate; fold any further findings into round-4. (b) **Round-4 correction —
   three fixes, all one root cause (match tokens in COMMAND/SPAWN position, not as data):**
   (i) **ADV-3 fail-OPEN (highest priority):** broaden the COM tooth `New-Object\s+-Com\w*\b` →
   `New-Object\s+-c\w*\b` so `-c`/`-co`/`-com…` all DENY (no other New-Object param starts with
   "c"). (ii) **D-R3-1 + ADV-2:** gate the scoped encoded-command check so the `powershell`/`pwsh`
   token is in COMMAND/SPAWN position (segment-first, or right after `start`/`saps`/`Start-Process`/
   `&`), NOT merely argument data — do NOT try to split `-enc` from `-Encoding` by prefix
   (impossible). (iii) **ADV-1:** anchor the `start`/`saps` spawn-alias denial to command-initial
   position (mirror `_launches_nested_shell`) so the word "start" as data (`git log --grep start`)
   ALLOWs. Add RED-on-mutant + no-FP rows: `New-Object -c FSO` DENY; `Select-String -Encoding utf8
   -Pattern powershell` ALLOW; `git log --grep start` ALLOW; while `New-Object -Com…` DENY,
   `start powershell -enc` DENY, `saps cmd /c` DENY all hold. Re-freeze; round-4 re-review (G3 + G5
   must flip to PASS; delta-attest G4). (c) **If all four gates then PASS:** run DCV — M0-T108's
   applicable D-024 set is **EMPTY** (`evaluate_task_refs` ok=true, `D-024:ALL` resolves empty;
   still write the explicit empty-set row in `verification.json`); `accept` (all required gates
   PASS + reviewed_sha == live HEAD), `checkpoint`, **advance campaign to seq 13**
   (`advance(expected_sequence=12, …)`). **DO NOT dispatch any unit C–I work until M0-T108 is
   ACCEPTED** (owner instruction + G5 M0-T102 precondition).
7. **Sub-agents (round-3 re-review at `e1f6d4c`; healthy, mutually blind):** `code-reviewer` G3 —
   **LANDED FAIL, recorded** (D-R3-1). `qa-engineer` G4 — **LANDED PASS, recorded** (flags ADV-3
   fail-open + ADV-1/ADV-2 fail-safe). `security-reviewer` G5 — **STILL IN FLIGHT** (this session's
   background agent; if the session is replaced it dies and its verdict is lost). Resume-or-replace:
   if this session continues, the orchestrator reconciles G5 on return; **if replaced, the successor
   need NOT re-run G3/G4 (recorded) but MUST collect-or-re-dispatch G5 round-3 at `e1f6d4c`.**
   Because D-R3-1 + ADV-3 already force round-4, the G5 verdict is additive input, not independently
   gating — proceed to round-4 with the §6 plan regardless of G5's exact wording.
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
