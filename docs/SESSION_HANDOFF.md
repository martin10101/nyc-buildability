# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` — and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff — seq 29: Amendment-12 window COMPLETE (T115+T114+T116 accepted); NEXT = the R276 resume

1. **Generated:** 2026-08-29 ~03:55 local · orchestrator session
   `session_01HfptKuEs3RDxaxsSHJjc7t`. **Turnover reason (verbatim):** owner invoked
   `/session-handoff` with no stated reason; landed at the seq-29 acceptance seam after the
   in-flight M0-T116 reviewer wave completed naturally. **Sub-agents:** twelve reviewer
   spawns this session (t112/t114/t115/t116 × G3/G4/G5/DCV waves) all finished their
   bounded reviews AND delta re-attestations naturally; reports committed verbatim; no
   producer or background task running; no agent was stopped.
2. **Identity (live at write):** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `control/D-024-fable-codex-loop` (campaign seq **29**), accept-time head `b90889b`,
   tip at write `5ba7d44` + this handoff commit. Tree clean; every unit's CI 20/20.
3. **This session end-to-end:** M0-T112 (first re-cert) ACCEPTED → activation package
   PRESENTED (seq 27) → owner AUTHORIZED R187/R595 limited-auto (Amendment 9, capture
   `a87b407`) → Fable-availability correction (Amendment 10: stale opus-4.8 worker pin
   removed after a live probe proved `init_model=claude-fable-5`; `[approved_models]`
   populated by owner admin edit) → ACTIVATION EXECUTED (11/11 probes, 1 provider call);
   first cycle FAIL-CLOSED at 3 ASK-held discovery commands (S14, exit 11) → owner-ordered
   deny+clear+restart (Amendment 11) → restart REFUSED pre-dispatch exposing the
   deny→ask-row seam defect → Amendment 12: **M0-T115** (seam fix: broker answer paths
   resolve `ask_<id>` rows + shared `owner_unanswered_asks()` reconciliation at the S11.5
   probe AND the rotation-seam feed — G3 BLOCKER round found the 4th consumer; 14 tests),
   **M0-T114** (residuals: telegram post-builder queue digest; sanitized
   `source_record_key`; unit-K notes dispositioned; 2 tests), **M0-T116** (second re-cert
   at the post-repair identity: material `f89aa29`, tree `7487901c…`, golden blob
   `cf03caaa`; golden 41/41, affected 705/705, suite 2710/2/0, 2712 = 2696+14+2 exact;
   G3 MAJOR banner correction closed) — ALL ACCEPTED with four-reviewer waves + delta
   re-attestations + DCV rows + validator EXIT=0 each.
4. **EXACT next action — the R276 RESUME SEQUENCE** (campaign seq-29 NEXT carries the full
   ordered list): re-record the controller manifest for the POST-REPAIR tree (the stored
   `%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json`
   still binds the PRE-repair tree and will fail verify) → verify-controller → doctor →
   doctor --live → the complete preflight matrix (M0-T113-activation-preflight.md pattern;
   config digests in the campaign record) → re-run the exact certified item-3 start
   command (`--mode limited-auto --owner-enable-bounded-auto`, packet M0-T107.json,
   worktree `wt-m0t107`, run `run_M0_T107_unitJ`) — the pre-fix journal's 3 denied ask
   rows now reconcile at BOTH live-refused boundaries (this restart IS the R274 end-to-end
   proof) → confirm dispatch/checkpoint progression → complete M0-T113 (evidence → gates →
   accept). ON ANY FAILURE: remain stopped and report (R276); never restart-loop (R270);
   never edit the runtime journal (R273).
5. **Mechanics proven this session (newest):** verification entries are FILLED IN PLACE
   into capture-time skeletons (append = validator c16); stamp `reviewed_manifest_sha256`
   via `project_control._task_git_identity`; skeletons must match the RESOLVER set (build
   them from `evaluate_task_refs`); c17 needs `path_free_governance` for report-only
   packets; commit the CLI's untracked submit-record; awaiting_gate restamp = rework →
   resubmit; PASS-with-required-corrections = ONE consolidated round + delta
   re-attestations from the SAME reviewers (SendMessage; reviewers deliver after an idle
   ping); fake tokens need BOTH `gitleaks:allow` + `secretscan:allow` (the CI credential
   scanner is stricter than local gitleaks); stale packet dependencies may be corrected by
   the orchestrator with an in-packet recorded note.
6. **Standing restrictions:** NEVER merge PR #241 (live-checked OPEN/unmerged repeatedly);
   owner-only: autostart install, C1 canary, Telegram live send (env not configured;
   queue empty), natural-event graduation, OS-ACL hardening, residual-note fixes (three
   carried notes pinned in M0-T116-recertification.md §5 — fixing any re-triggers R247);
   Bootstrap Gate 0 every session; supervisor commits cite `D-024-R###`; repo PUBLIC;
   never `name:` on producers (named REVIEWERS are fine — read-only); expansion hold;
   `.claude/hooks` untouchable sans G5.
7. **Task states:** M0-T112/T114/T115/T116 accepted; M0-T113 in_progress 95% (completes at
   the resume); M0-T107 claimed 10% (the loop's first packet, untouched); M0-T110/T111/
   T096 accepted earlier.
8. **Successor must read:** `CLAUDE.md`; this file; `.claude/session-handoff-profile.md`;
   `project-control/campaigns/D-024-fable-codex-loop.json` (seq 29 — the full resume
   checklist); `project-control/reports/M0-T113-activation-preflight.md` (+ evidence md);
   `project-control/reports/M0-T116-recertification.md`;
   `project-control/reports/M0-T096-activation-package.md`;
   `project-control/directives/D-024-fable-codex-loop/source-009..012-amendment.md`.
9. **Stop/change conditions:** Gate-0 failure; validator non-zero; ANY preflight/manifest/
   doctor/CI failure during the resume (stop + report exactly, R259/R276); reviewer
   FAIL/BLOCKED; anything owner-only (§6). If the start command is denied by the session
   permission classifier, hand the exact command to the owner (`!` prefix) — do not work
   around it.
10. **Successor prompt:** *"Work from durable repository evidence only. Verify root =
    C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, branch control/D-024-fable-codex-loop,
    HEAD, tree, and /mcp empty (Bootstrap Gate 0) before any change. Read CLAUDE.md,
    docs/SESSION_HANDOFF.md, .claude/session-handoff-profile.md, and the §8 files. Run
    `python tools/project_control.py status` and `python -m
    tools.agent_supervisor.campaign_continuity --status`. Reconcile against live git + the
    ledger (they win over prose). The Amendment-12 window is COMPLETE (M0-T115, M0-T114,
    M0-T116 all accepted). Continue the campaign seq-29 NEXT: execute the R276 resume
    sequence IN ORDER — re-record the controller manifest for the post-repair tree,
    verify-controller, doctor, doctor --live, the complete activation preflight, THEN the
    exact certified limited-auto start command on the M0-T107 packet — stopping and
    reporting on ANY failure, never bypassing a gate, never editing the runtime journal,
    never restart-looping. On successful dispatch, confirm run identity / Fable 5 / first
    checkpoint and complete M0-T113 through its gates. Do not merge PR #241 or any
    pre-existing PR; stop for anything owner-only. The standard D-010 R113/R114 ~400k
    rotate-at-seam ceiling governs your session."*
