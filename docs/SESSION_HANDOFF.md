# Session Handoff - NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live -
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` - and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff - seq 49: M0-T132 ACCEPTED (2.1.252 admitted + combined R247 recert); owner-typed commissioning is the only thing left

1. **Generated:** 2026-09-01 by the successor orchestrator (Fable 5). Owner Amendment 35 ("no waiting
   go on i need to start the codex loop even if fable is not available now") resolved **B-020 Option B**
   (proceed on the approved non-capped worker model `claude-opus-4-8`). M0-T132 ran the full standard
   lifecycle and is **ACCEPTED**. Tree clean; zero live agents.
2. **Identity (live at write):** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `control/D-024-fable-codex-loop` (campaign seq **66**), accepted at frozen `d743ad24` (this commit
   advances HEAD with the acceptance records). local == origin before this commit.
3. **ADMITTED: Claude Code 2.1.252 (`e713c5a6`).** Fresh preflight PASS (Bootstrap Gate 0 + R438):
   `/mcp` empty; `DISABLE_AUTOUPDATER=1` inherited; `DISABLE_UPDATES` unset; `claude --version` 2.1.252;
   on-disk `claude.exe` = `e713c5a6`, 217,406,624 B == `versions/2.1.252`; nothing newer staged.
4. **What ran (all evidence committed):** FOUR fixtures at 2.1.252 — `capability_probe` (`--help` sha256
   UNCHANGED `83af8a9a7edc`), `hook_event_catalog` (docs re-fetched: same 33 events, no drift),
   `native_runtime_detection` (identical), and **`shell_routing` measured at `e713c5a6` on
   `claude-opus-4-8`** (`native_preferred`, observed live `can_use_tool` brokering). `event_drift.py`
   re-pointed + four test files. **Whole suite 3,043/2/0** — the admission RESOLVED the exact 3 M0-T131
   CLI-drift failures (3,040+3). **Combined R247 recert PASS:** manifest re-recorded to `c228b7ca`
   binding BOTH `codex_reviewer.py` (M0-T131) AND `event_drift.py` (M0-T132); `verify-controller` +
   non-live `doctor` PASS. Gates: **G0/G2 PASS, G3 code-reviewer PASS, G4 qa-engineer PASS** (clean-room
   3,043/2/0 + red-on-mutant on 4 teeth), **DCV PASS 18/18 (R431–R448), zero violations**. Validator EXIT=0.
5. **Honest disclosures (Fable-cap artifacts, NOT failures — recert §4):** routing captured on opus
   because Fable 5 is under its seven-day cap; `doctor --live` control-response FAILED only because that
   probe hardcodes the capped Fable default (NOT a 2.1.252 protocol break — the routing probe observed a
   live `can_use_tool` on opus — and NOT a start gate); running it refreshed the journal's stale
   control-response probe record, but **`transitions=35`/`audit=85` are unchanged**.
6. **EXACT next actions — owner-typed commissioning (present-only here; parse-validated;
   `project-control/reports/M0-T132-commissioning-presentation.md`):** (1) **`record-manifest --out
   <stored manifest>`** to rebind the certified activation manifest `26a05096…`→`c228b7ca…` (the local
   write classifier blocked the orchestrator, so the OWNER types this); (2) set
   `C:/SupervisorController/model_selection.toml` `[claude] model = "claude-opus-4-8"` (runs under Fable
   unavailability; opus is approved; R447 — the orchestrator can do this one-line edit on the owner's
   say-so, held back only for R146); (3) **`owner-restart --checkout <ctl24>`** (HALTED→IDLE); (4)
   **`start --mode limited-auto --owner-enable-bounded-auto --repin-cli-identity …`** (the `--repin-cli-identity`
   completes the admission at the journal level; the start runs on opus). The start's pre-dispatch relies
   on `cli_capability_manifest` + the digest-keyed `shell_routing` evidence (present at `e713c5a6`), NOT a
   live control-response round-trip.
7. **Preservation:** journal HALTED (transitions 35, audit 85 — only the stale control-response probe
   record refreshed); `wt-m0t107` `c5c6ff7` + two untracked journey-4 drafts; `wt-m0t109` `1c06957`;
   queue digest `11eaa5a7`; owner-touch 3-of-2; budgets; PR #241 OPEN. The orchestrator executed NO
   commissioning command (R444).
8. **Successor must read:** `CLAUDE.md`; this file; `.claude/session-handoff-profile.md`;
   `project-control/campaigns/D-024-fable-codex-loop.json` (seq 66); `project-control/reports/`:
   `M0-T132-recertification.md`, `M0-T132-commissioning-presentation.md`, `M0-T132-DCV.md` (+supplement),
   `M0-T132-G3-code-review.md`, `M0-T132-G4-qa-review.md`, `M0-T132-admission-evidence.md`; directives
   `source-034/035-amendment.md`.
9. **Stop/change conditions:** Gate-0 failure; validator non-zero; any owner-only item (the commissioning
   start IS one — R595 `--owner-enable-bounded-auto`, owner-typed); any live failure (R394: stop, preserve,
   one consolidated assessment); supervisor commits cite `D-024-R###`; producers UNNAMED + roster-typed,
   rotate-at-seam, never resumed after a kill; campaign next_action pure ASCII; registry JSON writes LF.
10. **Successor prompt:** *"Work from durable repository evidence only. Verify root, branch, HEAD, tree,
    and /mcp empty (Bootstrap Gate 0) before any change. Read CLAUDE.md, docs/SESSION_HANDOFF.md, and the
    section-8 files. Run `python tools/project_control.py status` and `python -m
    tools.agent_supervisor.campaign_continuity --status`; reconcile against live git + the ledger (they
    win). M0-T132 is ACCEPTED — Claude Code 2.1.252 (e713c5a6) is admitted and the combined R247 recert
    is complete. The only thing left is the OWNER-TYPED commissioning sequence in
    M0-T132-commissioning-presentation.md (record-manifest rebind, model_selection opus pin, owner-restart,
    start --repin-cli-identity). Do NOT execute the start yourself; present it and wait. Never merge PR
    #241. The D-010 ~400k rotate-at-seam ceiling governs."*
