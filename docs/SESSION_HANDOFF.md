# Session Handoff - NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live -
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` - and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff - seq 50: M0-T133 (checkpoint-envelope fix) AWAITING_GATE; G3/G4/DCV in flight (owner /session-handoff)

1. **Generated:** 2026-09-01 by the orchestrator (Fable 5), owner `/session-handoff` (no reason
   given). New work stopped. Durable state SAFE: tree clean, local == origin.
2. **Identity (live):** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `control/D-024-fable-codex-loop` (campaign seq **69**), HEAD `78f4d675`, origin
   `https://github.com/martin10101/nyc-buildability.git`. Dirty files: **none**.
3. **Where the campaign stands:** M0-T131 + M0-T132 ACCEPTED (Claude Code **2.1.252 `e713c5a6`
   admitted**; combined R247 recert done). Commissioning journey-5 was the FIRST live limited-auto
   dispatch (ran on opus-4-8) and stopped `no_valid_checkpoint` - the opus worker omitted the four
   required git-state checkpoint fields. Owner authorized **M0-T133** (Amendment 37, rows
   `D-024-R460..R471`) to fix it.
4. **M0-T133 = controller-authoritative git-state checkpoint enrichment.** IMPLEMENTED + committed:
   new `tools/agent_supervisor/checkpoint_envelope.py` makes `branch/worktree/starting_sha/current_sha`
   controller-authoritative (filled from the dispatch context + a fresh read-only git measurement
   BEFORE validation; exact match-or-fail-closed for any worker-supplied; worker bytes preserved +
   enrichment audited; scoped to `limited-auto` per the R295 precedent). `claude_runner.py`
   (extract_checkpoint split; run_unit envelope + RunResult fields) + `loop.py` (starting_sha
   measurement, envelope build, audit). `models.py`/ClaudeCheckpoint UNCHANGED (fail-closed integrity
   preserved). Tests: **24 new** (all 8 owner scenarios + removal-sensitivity on the exact journey-5
   shape). Affected packs **477/0**, golden **42**, whole suite **3,067 passed / 2 skipped / 0 failed**
   (3,043 baseline +24). ruff/modularity/command-doc clean.
5. **Gates so far:** G0 PASS, G2 self-check PASS (both committed). **IN FLIGHT (session-bound):** G3
   `code-reviewer`, G4 `qa-engineer`, DCV `directive-compliance-verifier` - all dispatched at
   `78f4d675` on the **opus** fallback (R460). They report to THIS session. **If this session is
   alive, it records their gates when they land; if a successor takes over, RE-DISPATCH all three
   read-only at `78f4d675`** (their in-flight results do not cross sessions). Do NOT kill them for
   turnover.
6. **R247 recert evidence PRE-STAGED (scratch, not yet applied):** the recert re-records the manifest
   to **126 files digest `ba23b3b7`** (adds `checkpoint_envelope.py`; changes `claude_runner.py` +
   `loop.py`); `verify-controller` + non-live `doctor` PASS against it; journal preserved
   (PAUSED_RECOVERY, transitions 40, audit 104). The stored manifest at
   `%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json` is still the
   accepted `c228b7ca` (M0-T132) - the re-record happens AT the recert, after acceptance.
7. **EXACT next action:** when G3/G4 PASS + DCV PASS (18/18-style, R460-R471) at `78f4d675`: record the
   gates + DCV verification.json row; **accept M0-T133**; run the single **R247 recertification**
   (record-manifest to the stored path -> `ba23b3b7`; verify-controller; non-live doctor; cite the
   already-run golden 42 + whole suite 3067/2/0 - do NOT re-run; NEVER `doctor --live` while Fable is
   capped); then **present ONLY** (R470/R471, do NOT execute): the targeted proof, the exact
   owner-typed `clear-recovery --checkout C:/Users/MLFLL/Downloads/nyc-zoning/ctl24` (journal is
   PAUSED_RECOVERY, so clear-recovery NOT owner-restart), and one parse-validated `start ...
   --repin-cli-identity --run-id <fresh-unused>` (the M0-T132 commissioning line with a NEW run id;
   NOT `m0t107-commission-20260901`, already used).
8. **Preservation / standing gates:** journal PAUSED_RECOVERY (transitions 40, audit 104, chain ok);
   owner-touch 1-of-2 on run `m0t107-commission-20260901` (+ exhausted `run_33dfa57d54db`); model pin
   `claude-opus-4-8` (owner-set for commissioning); PR #241 OPEN; wt-m0t107 `c5c6ff7` + 2 untracked
   drafts; wt-m0t109 `1c06957`. **Never merge PR #241.** R394 on any live failure. Do NOT run
   `doctor --live` while Fable 5 is capped (it records a false-negative capability probe that
   fail-closes the start - see `M0-T132-commissioning-start-refusal.md`). Owner-only: credentials,
   payment, production, legal, the commissioning start itself.
9. **Successor must read:** `CLAUDE.md`; this file; `.claude/session-handoff-profile.md`;
   `project-control/campaigns/D-024-fable-codex-loop.json` (seq 69); `project-control/reports/`:
   `M0-T133-producer-report.md`, `M0-T133-G2-self-check.md`, `M0-T133-evidence-map.json`,
   `M0-T107-commissioning-journey-5.md`, `M0-T132-commissioning-presentation.md`,
   `M0-T132-commissioning-start-refusal.md`; directives `source-034..037-amendment.md`.
10. **Stop/change conditions:** Gate-0 failure; validator non-zero; any owner-only item; any live
    failure (R394); supervisor commits cite `D-024-R###`; producers UNNAMED + roster-typed; campaign
    next_action pure ASCII; registry JSON writes LF. If a reviewer returns FAIL, move M0-T133 to
    rework (do NOT accept).
11. **Successor prompt:** *"Work from durable repository evidence only. Verify root =
    C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, branch control/D-024-fable-codex-loop, HEAD, tree clean,
    /mcp empty (Bootstrap Gate 0) before any change. Read CLAUDE.md, docs/SESSION_HANDOFF.md, and the
    section-9 files. Run `python tools/project_control.py status` and `python -m
    tools.agent_supervisor.campaign_continuity --status`; reconcile against live git + the ledger
    (they win). M0-T133 is AWAITING_GATE at 78f4d675 (the checkpoint-envelope fix for journey-5) with
    G0/G2 PASS; its G3/G4/DCV were dispatched in the prior session and do NOT cross sessions -
    RE-DISPATCH code-reviewer + qa-engineer + directive-compliance-verifier read-only at 78f4d675 on
    the opus fallback (R460). On all PASS: record the gates + DCV row, accept M0-T133, run the single
    R247 recert (manifest -> ba23b3b7; verify-controller + non-live doctor; cite golden 42 + whole
    suite 3067/2/0; NEVER doctor --live while Fable is capped), then PRESENT ONLY the clear-recovery +
    fresh-run-id start (do NOT execute). Never merge PR #241. R394 on any live failure. The D-010
    ~400k rotate-at-seam ceiling governs."*
