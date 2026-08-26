# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` — and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** This file is orientation only; rules/gates live in `CLAUDE.md`; old blocks via
`git log -p docs/SESSION_HANDOFF.md`. CURRENT-ONLY: `context-budget` CI fails > ~4000 tok.

## Handoff — M0-T099 accepted, campaign advanced

1. **Generated:** 2026-08-26 UTC · Fable 5 orchestrator, `session_01HfptKuEs3RDxaxsSHJjc7t` ·
   reason: owner invoked `/session-handoff` (no reason argument) at the clean post-acceptance
   seam · via the GLOBAL personal skill (profile identity verified: origin + markers). Zero
   active sub-agents at generation (all four M0-T099 reviewers completed and reconciled); zero
   uncommitted files; zero unpushed commits.
2. **Identity (live at generation):** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `control/D-024-fable-codex-loop`; acceptance commit `f85ed5b` (+ this seam commit on top),
   pushed. Working tree clean at seam.
3. **Active state:** campaign `project-control/campaigns/D-024-fable-codex-loop.json` **seq 4,
   active, NEXT = M0-T090** (C1 bounded subagent contracts per its packet); no task claimed;
   checkpoint CP-D024-M0-T099. D-023 continues separately (M0-T080, own worktree `wt-m0t080`).
4. **This session ACCEPTED M0-T099** (owner amendment 2, D-024-R129..R138): project statusLine
   handler `telemetry_statusline.py` (ONE feed: sanitized sidecar + compact human row from the
   same record), REAL live-2.1.220 statusline fixture `statusline_live_2026-08-26.json`
   (startup-nulls + post-response-with-rate-limits payloads, home+dash-encoded masking), 23-test
   handler pack, and ALL carried M0-T089 hardening (G5 M1/M2/N1/N2, G3 minor#2+nits#3-5, G4 A2;
   A1 documented). Frozen content `00f2519`, material identity `d6e90bfc`, gates G0/G2/G3/G4/G5
   PASS (none blocking; G4 7/7 mutation teeth), DCV 10/10 PASS, validator EXIT=0 at every seam.
5. **Suite baseline now:** composite full `tools/` = **2595 passed / 3 skipped / 0 failed**
   (directive pack runs chunked: `::NegativeValidatorTests` ~19 min + `--deselect` rest ~9 min;
   each of its registry tests takes ~75 s). Supervisor packs alone: 2041/2/0 (G3-reproduced).
   The 3 skips are named + adjudicated env-conditional in `M0-T099-G2-self-check.md` §2 (owner
   asked mid-session; never report bare skip counts).
6. **Fixture capture method (proven):** `claude -p` does NOT fire statusLine; capture = scratch
   project + settings statusLine tee + live interactive TUI + SendKeys (report §3). New leak
   class fixed in production mask: dash-encoded `C--Users-<name>` projects-dir form.
7. **Repairs beyond task scope (separate commits):** stale synthetic literal "M0-T099" in
   `test_directive_compliance.py::ResolverTests` collided with amendment-2 bindings → id now
   "M0-T9099" (commit `30d9a3c`). Known non-material doc nit: producer report says "21-test"
   pack; actual 23 (all green; correction recorded in `M0-T099-DCV.md` disposition — report NOT
   edited post-submit, identity preservation).
8. **Owner-visible items outstanding (not blockers):** (a) live statusLine wiring per report §4
   (gitignore `.claude/telemetry/` + settings.json command — owner step, never automated);
   (b) purge THREE leftover pack-repo agent worktrees `agent-a97cd976cfb4344f0`,
   `agent-ac83580dbc0f69fce`, `agent-a1e58fd626f4ec1e6` (classifier-denied for this session;
   exact commands in report §8; never merge agent worktree branches); (c) G5 MIN-1 standing
   guidance: neutralize account-usage numbers/epochs + session/prompt UUIDs in FUTURE public
   real-capture fixtures (routed to the live-canary task).
9. **Carried advisory bundle for the next module-touching task** (named in campaign NEXT):
   G3-M1 (completed-first eviction-order test isolation), G5-NIT-1 (dash mask into the
   cross-fixture class scan), G5-NIT-2 (dash-username first-segment limitation, documented).
10. **Environment lessons:** background pytest runs get killed non-deterministically in this
    harness — run long suites FOREGROUND in chunks; reviewers in pack-repo worktrees cannot
    `git checkout` (use `git archive` extraction; expect 5 git-infra failures + 2 extra skips
    there, reconciliation table in `M0-T099-G4-qa-review.md`).
11. **Standing restrictions:** NEVER merge PR #241 or any pre-existing PR; continuous activation
    owner-gated (D-024 §18, R595); Bootstrap Gate 0 every session (primary cwd = this root;
    `/mcp` empty) before any write; supervisor commits cite a `D-024-R###` id; no worker token
    quotas; expansion hold; repo PUBLIC — no secrets/home-path leaks in governed artifacts.
12. **Successor must read:** `CLAUDE.md`; this file; `.claude/session-handoff-profile.md`;
    `project-control/campaigns/D-024-fable-codex-loop.json`; `project-control/tasks/M0-T090.json`;
    `project-control/reports/M0-T099-statusline-handler.md` (§4 wiring, §8 purge).
13. **Exact next action:** claim **M0-T090** (C1 bounded subagent contracts + structural workload
    sizing) per the campaign record: G0 → claim → produce → G2 → submit → independent
    G3/G4/G5+DCV at the frozen identity → accept → advance the record.
14. **Stop/change conditions:** Gate-0 failure (no writes, fresh session); validator non-zero;
    reviewer FAIL/BLOCKED (consolidated correction round, re-freeze, delta re-review); anything
    needing owner authority (credentials, payment, production, legal, PR #241, activation, live
    settings.json wiring, pack-repo worktree purge).
15. **Successor prompt:** *"Work from durable repository evidence only. Verify root =
    C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, branch control/D-024-fable-codex-loop, HEAD, and
    /mcp empty before any change. Read CLAUDE.md, docs/SESSION_HANDOFF.md,
    .claude/session-handoff-profile.md, and the §12 files. Run: python tools/project_control.py
    status and python -m tools.agent_supervisor.campaign_continuity --status. Reconcile against
    live git + the ledger (they win over prose). Detect stale/duplicated/completed work. Report
    READY TO RESUME or BLOCKED. If ready, continue from the campaign record's NEXT action —
    claim M0-T090 (C1 bounded subagent contracts + structural workload sizing, with the carried
    M0-T099 advisory bundle) — without repeating completed work or broadening scope; stop for
    anything requiring owner approval."*
