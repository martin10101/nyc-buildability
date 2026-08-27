# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` — and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff — M0-T108 ALL GATES PASS (rounds 1–4); only the DCV verification row remains before accept

1. **Generated:** 2026-08-27 UTC · Fable 5 orchestrator, `session_01HfptKuEs3RDxaxsSHJjc7t` ·
   reason: owner-invoked `/session-handoff` (no reason arg; prior invocation reason verbatim: "make
   it as soon this part is done"). Invoked with **one healthy sub-agent in flight** (the DCV, §7) —
   left running, not killed.
2. **Identity (live):** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `control/D-024-fable-codex-loop`, HEAD `2d3c645f`; tree clean; pushed == origin. Machine claude
   binary 2.1.247 (this orchestrator process still 2.1.220). Campaign **seq 12** (M0-T108 not yet
   accepted).
3. **This session:** discharged the D-024-R162/R183 statusLine deferral at 2.1.247 (seq 12, commit
   `24aa061`; Amendments 4/5/6 = R192..R219); then took **M0-T108** (readonly_agent_guard
   PowerShell/scripting write-gap fix, G5 M0-T102 MEDIUM) through **four independent review rounds**
   to all-gates-PASS.
4. **M0-T108 state:** `awaiting_gate` (95%), claimed by `fable-orchestrator-session`, worktree =
   primary checkout. **Deliverable frozen at `b6db457`** (content-manifest identity
   `90376158eda8b6fc4bec8943dc702d09f896deda7345ce3358885b5c9b7ff972`; HEAD `2d3c645f` = the row is
   control-plane-only after b6db457). **All required gates PASS:** G0, G2, G3 (round-4), G4
   (round-4), G5 (round-4). Round history: r1 G3 FAIL + G5 blocking C1-C4; r2 G5 FAIL (F1 COM
   prefix, F2 encoded shell); r3 G3 FAIL (D-R3-1 -Encoding FP) + G5 FAIL (NF1 COM `-C/-Co` +
   reflection, NF2 assignment-fronted encoded shell); **r4 closed all** via one root-cause change
   (match tokens in COMMAND/SPAWN position, not as data): COM floor `New-Object -c\w*` +
   `[Activator]::CreateInstance`/`GetTypeFromProgID` reflection; `_effective_command_token`
   (assignment-RHS) in `_launches_nested_shell`; `start`/`saps` → command-position `_SPAWN_ALIAS`;
   removed the fragile `_PS_ENCODED_CMD`/`_PS_HAS_SHELL`; honest docstring.
5. **M0-T108 evidence (round 4):** PS pack **187/187** (15 RED-on-mutant); Bash **136/136**
   byte-unchanged; ruff clean; modularity 0 failures (guard 768 raw lines, not flagged). Only the
   four packet paths changed.
6. **EXACT next action — ACCEPT M0-T108 (single remaining precondition = the DCV row):**
   (a) The independent **DCV** (§7) confirms M0-T108's D-024 applicable set is **EMPTY** (already
   computed: `evaluate_task_refs` → `applicable_ids=[]`, ok=True; selective-citation clean).
   (b) Write ONE `task_verification` row into
   `project-control/directives/D-024-fable-codex-loop/verification.json` `task_verifications[]`:
   `{task_id: "M0-T108", directive_id: "D-024", producer: "orchestrator", verifier:
   "directive-compliance-verifier", applicable_requirement_ids: [], requirements: [],
   reviewed_manifest_sha256: <IDENTITY>, reviewed_sha: <HEAD>}`. **RECOMPUTE `<IDENTITY>` and
   `<HEAD>` at accept-time** via `tools.project_control._task_git_identity(reg, M0-T108-packet,
   reviewed_sha=None)` (an uncommitted verification.json does NOT dirty M0-T108's identity — proven
   — so stamp at current HEAD and run accept BEFORE committing the row = capture-commit pattern).
   (c) `python tools/project_control.py accept --task-id M0-T108 --agent orchestrator`.
   (d) Create follow-up **M0-T109** (guard hardening: ADV-R4-1 loop the `$var=` assignment strip in
   `_effective_command_token` to close chained `$a=$b=powershell -enc`; ADV-4 make the
   `GetTypeFromProgID` tooth reachable behind `::` or remove it as redundant with Activator;
   ADV-R4-2 document `GetTypeFromCLSID`/`&(gcm)` residuals) — allowed_paths `.claude/hooks` +
   `tools/test_readonly_agent_guard_powershell.py` + a report; directive-refs `D-024:ALL`.
   (e) `checkpoint`; (f) advance campaign to **seq 13** (`advance(expected_sequence=12,
   next_action={task_id: "M0-T104", …})`); (g) run `validate_directive_compliance.py --check`
   (EXIT=0), commit the capture-commit (verification row + acceptance ledger + M0-T109 + campaign) +
   push. **DO NOT dispatch any unit C–I work until M0-T108 is ACCEPTED.**
7. **Sub-agent in flight — the DCV** (`directive-compliance-verifier`, independent, empty-set
   verification at identity `90376158`/HEAD `2d3c645f`): **this session's background agent — if the
   session is replaced it dies and its attestation is lost.** Resume-or-replace: if this session
   continues, the orchestrator writes the row on its PASS; **if replaced, the successor RE-DISPATCHES
   the DCV** (quick; independently confirm the empty applicable set — the selective-citation guard)
   before writing the row. The three round-4 gate reviewers (G3/G4/G5) already LANDED and are
   recorded — do not re-run them.
8. **After M0-T108 accepted (campaign NEXT, seq 13):** M0-T104 (unit C native runtime adapter) →
   T105 → T106 → T092 → T094 → T093 → T095 → T096 (golden run; R187 hold after) → T107. Carry the
   R162-discharge unit-C preconditions (explicit child-env control for background dispatch; installed
   version measured-at-use — a 2.1.247 capability re-probe + drift-tooth re-baseline is owed to unit
   C; permission-mode vocabulary accepts `auto`).
9. **Standing restrictions:** NEVER merge PR #241 or any pre-existing PR; **no unit C–I dispatch
   until M0-T108 accepted**; continuous-mode owner-gated (D-024 §18/R595); Amendment-3 prohibitions
   (no SDK/MCP/bypass flags/unbounded fan-out; ledger is authority — R146); Bootstrap Gate 0 every
   fresh session; supervisor commits cite `D-024-R###`; repo PUBLIC — mask `[HOME]`; producers as
   roster types (generic `general-purpose` cannot Write; never pass `name:` to a producer).
10. **Owner-visible (non-blocking):** broken npm shim (owner MAY `npm -g uninstall
    @anthropic-ai/claude-code`); parked session `777b09da` recover via `claude attach/respawn`
    (untouched); purge FIVE stale pack-repo agent worktrees; repo-hygiene task (worktree field +
    session-id masking).
11. **Successor must read:** `CLAUDE.md`; this file; `.claude/session-handoff-profile.md`;
    `project-control/campaigns/D-024-fable-codex-loop.json` (seq 12); `project-control/tasks/M0-T108.json`;
    the M0-T108 gate reports (`M0-T108-G{3,4,5}-*-round4.md` + earlier rounds);
    `docs/LEAN_OPERATING_PROCESS.md`; the in-regime accept memory.
12. **Stop/change conditions:** Gate-0 failure (no writes, fresh session); validator non-zero;
    reviewer FAIL/BLOCKED; anything owner-only (credentials, payment, production, legal, PR #241,
    activation, worktree purge).
13. **Successor prompt:** *"Work from durable repository evidence only. Verify root =
    C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, branch control/D-024-fable-codex-loop, HEAD, tree,
    and `/mcp` empty (Bootstrap Gate 0) before any change. Read CLAUDE.md, docs/SESSION_HANDOFF.md,
    .claude/session-handoff-profile.md, and the §11 files. Run `python tools/project_control.py
    status` and `python -m tools.agent_supervisor.campaign_continuity --status`. Reconcile against
    live git + the ledger (they win over prose). M0-T108 has ALL required gates PASS at deliverable
    b6db457; the ONLY remaining accept precondition is the independent D-024 task_verification row
    for its EMPTY applicable set. If the prior DCV agent is gone, RE-DISPATCH the
    directive-compliance-verifier to confirm the empty set, then follow §6 exactly: write the row
    (recompute identity/sha at accept-time; uncommitted verification.json does not dirty the
    identity — accept before committing), accept M0-T108, create follow-up M0-T109, checkpoint,
    advance the campaign to seq 13, run the validator, and commit the capture-commit + push. Then
    continue from the campaign NEXT (M0-T104 onward). Do NOT dispatch any unit C–I work until
    M0-T108 is accepted. Stop for anything owner-only."*
