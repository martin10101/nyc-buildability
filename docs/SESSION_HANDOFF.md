# Session Handoff - NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live -
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` - and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff - seq 48: M0-T132 authorized (Amendment 34), CREATED + CLAIMED, then BLOCKED (B-020) at the live Fable 5 cap; owner decision required

1. **Generated:** 2026-09-01 by the successor orchestrator (Fable 5). Owner authorized the bounded
   M0-T132 combined 2.1.252 admission + single R247 recert lane (Amendment 34, rows **R437..R445**).
   Preflight PASSED; three fixtures captured; then an **R394 stop** at a live blocker. Tree clean;
   zero live agents.
2. **Identity (live at write):** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `control/D-024-fable-codex-loop` (campaign seq **65**), HEAD `1d4a6212` at capture (this commit
   advances it). local == origin before this commit.
3. **Fresh preflight - PASS (Bootstrap Gate 0 + R438):** `/mcp` empty; `DISABLE_AUTOUPDATER=1`
   inherited; `DISABLE_UPDATES` unset; `claude --version` = **2.1.252**; on-disk `claude.exe` =
   **`e713c5a6`**, 217,406,624 B, byte-identical to `versions/2.1.252`; old renamed binary `d6f6c29a`
   (obsolete 2.1.251); nothing newer installed/staged; this fresh session runs the 2.1.252 image.
   **R433 re-verification passes: 2.1.252 (`e713c5a6`) unmoved as the settled target.**
4. **Three owner-named fixtures - captured live, BENIGN version-only drift:** `capability_probe`
   (`claude --help` sha256 **UNCHANGED** `83af8a9a7edc`; flags/codex unchanged; no failed rows),
   `event_bus`/hook_event_catalog (official docs re-fetched: **same 33 events**, no hook drift),
   `native_adapter` (flags/verbs/`background_host_ready`/gaps identical). 2.1.252 is a benign patch
   bump. Generated fixture files were removed (admission held; content reproducible from the probe
   commands, all in `M0-T132-admission-evidence.md`).
5. **LIVE BLOCKER (B-020, R394 stop):** the **Fable 5 seven-day usage cap is REJECTING model calls**
   (`rate_limit_event` `status:rejected`, `seven_day_overage_included`; assistant text "You've reached
   your Fable 5 limit"; `seven_day` util 0.78). The 4th evidence piece, **shell-routing**
   (`shell_routing/v1`, R292/R295), is a **behavioral** probe folded into `cli_capability_manifest`
   and **digest-keyed**; it needs a working model, so it cannot be honestly measured at `e713c5a6`
   now (two runs = `no_tool_observed`). **Decisive conflict:** R441/R442 require **ONE** combined
   recert at **ONE** identity, and R247 would force a **second** recert if shell-routing is recaptured
   after this one; R221 forbids spending owner allowance to work around the cap; R220 forbids blocking
   the provable work (the three fixtures proceeded). Plus a genuine scope ambiguity: shell-routing is
   a **fourth**, digest-entangled fixture beyond the owner's "three affected fixtures".
6. **What was NOT done (preservation):** NO repin / `--repin-cli-identity`, NO recert, NO fixture
   re-pointing, NO supervisor start, NO journal write, NO reset, NO PR #241 action. Capped-model
   artifact fixture **deleted** (it carried `measured:true`+`e713c5a6` and would **false-green** the
   shell-routing gate, which ignores the verdict). Tree clean.
7. **OWNER DECISION REQUIRED (B-020 A/B/C/D):** **A** (recommended) wait for the cap reset, then run
   the full M0-T132 lane in one pass (3 fixtures + shell-routing at `e713c5a6` + repin + ONE combined
   recert at one identity); **B** authorize a bounded routing recapture on `--model claude-opus-4-8`
   (R221-adjacent, owner-gated); **C** rule shell-routing out of scope and proceed now with the
   standing shell-routing fail-closed caveat on the certified start; **D** anything/HOLD. The exact
   owner-typed `owner-restart` + certified-start commands are **NOT** presented as ready: after any
   repin they would fail closed at the shell-routing fold until routing is recaptured (that is the
   whole point of the decision).
8. **Preserved:** journal HALTED (transitions 35, audit 85); `wt-m0t107` `c5c6ff7` + two untracked
   journey-4 drafts byte-for-byte; `wt-m0t109` `1c06957`; queue digest `11eaa5a7`; owner-touch 3-of-2;
   budgets; every owner gate; PR #241 OPEN. Registry validator EXIT=0; supervisor tree untouched.
9. **Successor must read:** `CLAUDE.md`; this file; `.claude/session-handoff-profile.md`;
   `project-control/campaigns/D-024-fable-codex-loop.json` (seq 65); `project-control/blockers/
   B-020-*.json`; `project-control/reports/M0-T132-admission-evidence.md`,
   `M0-T132-G0-readiness.md`; directive `source-034-amendment.md` (rows R437..R445).
10. **Stop/change conditions:** Gate-0 failure; validator non-zero; any owner-only item (this
    admission lane IS one, now blocked on the owner's B-020 ruling); any live failure (R394: stop,
    preserve, one consolidated assessment - done); supervisor commits cite `D-024-R###`; producers
    UNNAMED + roster-typed, rotate-at-seam, never resumed after a kill; campaign next_action pure
    ASCII; registry JSON writes LF. Do NOT resume M0-T132 (admit/repin/recert/journal) until the
    owner answers B-020. R436 seam prohibitions otherwise remain.
11. **Successor prompt:** *"Work from durable repository evidence only. Verify root, branch, HEAD,
    tree, and /mcp empty (Bootstrap Gate 0) before any change. Read CLAUDE.md, docs/SESSION_HANDOFF.md,
    and the section-9 files. Run `python tools/project_control.py status` and `python -m
    tools.agent_supervisor.campaign_continuity --status`; reconcile against live git + the ledger
    (they win). M0-T132 is BLOCKED (B-020): the owner authorized the admission+recert lane, preflight
    passed and the three fixtures show only benign version drift, but the Fable 5 seven-day cap blocks
    the digest-keyed shell-routing recapture, so the one-combined-recert-at-one-identity requirement
    cannot be met yet. Do NOT repin, recertify, write the journal, re-point fixtures, or start the
    loop. Wait for the owner's B-020 A/B/C/D ruling; then run the chosen path under the standard
    gates. The D-010 ~400k rotate-at-seam ceiling governs."*
