# Session Handoff - NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live -
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` - and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff - seq 51: M0-T133 in REWORK - both G3+G4 FAIL on ONE modularity-ceiling defect; logic verified (owner: stop + handoff)

1. **Generated:** 2026-09-01 by the orchestrator (Fable 5), owner "stop and give me the handoff". New
   work stopped. Durable state safe; the ONLY open item is a small, decided modularity fix.
2. **Identity (live):** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `control/D-024-fable-codex-loop` (campaign seq **70**), HEAD (this commit); origin
   `https://github.com/martin10101/nyc-buildability.git`. Reworked code identity to fix: **`78f4d675`**.
3. **Campaign context:** M0-T131 + M0-T132 ACCEPTED (Claude Code **2.1.252 `e713c5a6`** admitted).
   Commissioning journey-5 (first live limited-auto dispatch on opus-4-8) stopped `no_valid_checkpoint`
   because the opus worker omitted the four required git-state checkpoint fields. Owner authorized
   **M0-T133** (Amendment 37, `D-024-R460..R471`) to fix it.
4. **M0-T133 = controller-authoritative git-state checkpoint enrichment (IMPLEMENTED, in REWORK).** New
   `tools/agent_supervisor/checkpoint_envelope.py` fills `branch/worktree/starting_sha/current_sha` from
   the dispatch context + a fresh read-only git measurement BEFORE validation (exact match-or-fail-closed
   for worker-supplied; worker bytes preserved + audited; scoped to limited-auto per R295);
   `claude_runner.py` + `loop.py` wiring; `models.py`/ClaudeCheckpoint UNCHANGED. Committed at `78f4d675`.
5. **The THREE reviews all completed at `78f4d675` (session-bound; already saved as reports):**
   - **G3 code-reviewer: FAIL** - single blocking defect: `claude_runner.py` = **1432 SLOC, 22 over its
     reviewed modularity exception ceiling (1410)**; `python tools/modularity_check.py --check` **exit 1**.
     All six logic focuses PASS. (`M0-T133-G3-code-review.md`)
   - **G4 qa-engineer: FAIL** - SAME modularity defect. But independently reproduced ALL counts (24 / 477
     / 42 / **3067 passed / 2 skipped / 0 failed**), verified all 8 owner scenarios, and proved the tests
     load-bearing with two scratch mutants (enrichment-off → 9 RED incl. the journey-5 anchor; resolve-off
     → 6 RED covering every fail-closed path). (`M0-T133-G4-qa-review.md`)
   - **DCV: implementation PASS** - R460-R469 + R471 independently SATISFIED (R470 not-yet-due, post-accept).
     NOTE: the DCV's R466 "modularity exit 0" sub-claim is WRONG - G3 + G4 + a direct re-run all get exit 1.
     (`M0-T133-DCV.md`)
   - **My error:** the G2 self-check + producer report wrongly recorded "modularity exit 0" (I read the last
     output lines, not the exit code). Both must be corrected.
6. **THE FIX (decided, NOT yet applied - do this next):** the recorded M0-T130 exception says "no growth
   headroom; a module split is the recorded follow-up on the NEXT substantial growth". A clean split is
   blocked because `RunnerError` (the base of `CheckpointError`) is raised in 10+ places across
   `claude_runner.py` and caught by `cli.py` - relocating it is a broader refactor beyond this narrow task.
   **Both reviewers explicitly offered the alternative: RENEW the ceiling.** Recommended fix: (a) add
   `tools/modularity_exceptions.json` to M0-T133 `allowed_paths`; (b) renew the `claude_runner.py` entry
   (bump `max_lines` 1410->~1435, `baseline_sloc`->1432, cite M0-T133 + the RunnerError-coupling
   justification, new `expires`, and **reschedule the module split** - relocate RunnerError/_event_text to
   a shared module + extract a `checkpoint_extraction.py` - as a dedicated follow-up task); (c) re-run
   `modularity_check --check` -> exit 0; (d) CORRECT `M0-T133-G2-self-check.md` + `M0-T133-producer-report.md`
   modularity lines. The CODE (checkpoint_envelope.py/claude_runner.py/loop.py/tests) stays BYTE-IDENTICAL -
   this is a behavior-neutral rework.
7. **Then re-gate + finish:** re-submit; the rework is behavior-neutral, so **delta-attest** via SendMessage
   to the completed G3 (`a857c69b`), G4 (`adaa9d8f`), DCV (`a48b179d`) - OR re-dispatch fresh on the opus
   fallback (R460) at the reworked identity - to confirm modularity now exit 0 + the renewal is justified +
   nothing else changed. On all PASS: record gates + the DCV `verification.json` row (R460-R471), **accept
   M0-T133**, run the single R247 recert (record-manifest to the stored path -> the reworked digest;
   verify-controller + non-live doctor; cite golden 42 + whole suite; **never** `doctor --live` while Fable
   capped), then **present ONLY** the owner-typed `clear-recovery --checkout C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`
   + one parse-validated `start ... --repin-cli-identity --run-id <fresh-unused>` (NOT `m0t107-commission-20260901`).
8. **Preservation / standing gates:** journal PAUSED_RECOVERY (transitions 40, audit 104, chain ok);
   owner-touch 1-of-2 on run `m0t107-commission-20260901`; model pin `claude-opus-4-8`; PR #241 OPEN;
   wt-m0t107 `c5c6ff7` + 2 untracked drafts; wt-m0t109 `1c06957`. **Never merge PR #241.** R394 on any live
   failure. **Do NOT run `doctor --live` while Fable is capped** (records a false-negative capability probe
   that fail-closes the start - see `M0-T132-commissioning-start-refusal.md`). Owner-only: credentials,
   payment, production, legal, the commissioning start.
9. **Successor must read:** `CLAUDE.md`; this file; `.claude/session-handoff-profile.md`;
   `project-control/campaigns/D-024-fable-codex-loop.json` (seq 70); `project-control/reports/`:
   `M0-T133-G3-code-review.md`, `M0-T133-G4-qa-review.md`, `M0-T133-DCV.md`, `M0-T133-producer-report.md`,
   `M0-T133-G2-self-check.md`, `M0-T133-evidence-map.json`, `M0-T107-commissioning-journey-5.md`,
   `M0-T132-commissioning-presentation.md`, `M0-T132-commissioning-start-refusal.md`; `tools/modularity_exceptions.json`
   (claude_runner.py entry); directives `source-034..037-amendment.md`.
10. **Stop/change conditions:** Gate-0 failure; validator non-zero; any owner-only item; any live failure
    (R394); supervisor commits cite `D-024-R###`; producers UNNAMED + roster-typed; campaign next_action
    pure ASCII; registry JSON writes LF. The modularity fix is the ONLY blocker; the logic is verified.
11. **Successor prompt (COPY):** *"Work from durable repository evidence only. Verify root =
    C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, branch control/D-024-fable-codex-loop, HEAD, tree clean, and
    /mcp empty (Bootstrap Gate 0) before any change. Read CLAUDE.md, docs/SESSION_HANDOFF.md, and the
    section-9 files. Run `python tools/project_control.py status` and `python -m
    tools.agent_supervisor.campaign_continuity --status`; reconcile against live git + the ledger (they
    win). M0-T133 (the checkpoint-envelope fix for journey-5) is in REWORK: G3 + G4 both FAIL on ONE defect
    - claude_runner.py is 22 SLOC over its 1410 modularity exception ceiling - while the logic, all 24
    tests, the whole suite (3067/2/0), all 8 scenarios, and the DCV requirements are verified PASS. Apply
    the decided fix in handoff section 6 (renew the claude_runner.py modularity exception with a
    justification + a rescheduled split follow-up; add tools/modularity_exceptions.json to allowed_paths;
    correct the G2 + producer-report modularity lines) - the code stays byte-identical (behavior-neutral).
    Then re-submit and delta-attest G3/G4/DCV (or re-dispatch on the opus fallback, R460) at the reworked
    identity; on all PASS record the gates + DCV row, accept M0-T133, run the single R247 recert (never
    doctor --live while Fable capped), and PRESENT ONLY the clear-recovery + fresh-run-id start (do NOT
    execute). Never merge PR #241. R394 on any live failure. The D-010 ~400k rotate-at-seam ceiling
    governs."*
