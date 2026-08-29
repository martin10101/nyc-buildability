# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` — and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff — seq 27: M0-T112 ACCEPTED; activation package PRESENTED (activation still owner-gated)

1. **Generated:** 2026-08-28 ~23:30 local (2026-08-29 UTC) · orchestrator session
   `session_01HfptKuEs3RDxaxsSHJjc7t` continuation (fresh context, same session id) at the
   seq-26 acceptance seam. **Sub-agents:** four reviewer spawns (t112-g3-code/g4-qa/g5-sec/dcv)
   all completed their bounded reviews naturally and are idle; no producer or background task
   is running.
2. **Identity (live at write):** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `control/D-024-fable-codex-loop` (campaign seq **26**), accept-time head `73aa587`.
3. **M0-T112 (unit M, final golden re-certification) = ACCEPTED**, completing the Amendment-8
   sequence (T096→T110→T111→T112). Certified at the FINAL frozen post-addition identity
   (supervisor material `8574c58`, tree `132e698c…`, golden pack blob `d2946392…` RE-RUN ONLY,
   run head `a4f94b7`): golden pack **40/40**; affected packs **493/493**; whole supervisor
   suite **2,694 passed / 2 skipped / 0 failed** (2,696 collected; +4 = exactly the four
   accepted L-pack correction tests); **CI 20/20** at certification tip `615f661`. Unit diff
   touched ONLY `project-control/**`. Gates G0/G2/G3/G4/G5 PASS + DCV 6/6 SATISFIED
   (rows R231/R232/R246/R247/R248/R249; validator EXIT=0; manifest `60c1b21e` at `73aa587`).
   Reports: `project-control/reports/M0-T112-*`. Residuals CARRIED not fixed (recert report §5):
   `_already_queued` digest normalization; unit-I `live_observation.py:296`; unit-K notes —
   any supervisor fix re-triggers R247 re-certification.
4. **EXACT next action:** the **R187/R595 activation package was PRESENTED 2026-08-29**
   (owner-typed command at seq 26; campaign seq-27 record; CI 20/20 on acceptance tip
   `88b909d`): `project-control/reports/M0-T096-activation-package.md`. Presentation granted
   NOTHING — the owner decision set is pending (package item 14): activation decision,
   autostart install, C1 live canary, natural-event graduation, ACL hardening; plus weighing
   residual-fix-then-recertify vs activate-then-fix (any supervisor change re-triggers R247).
   Do NOT re-present or nudge. The only remaining non-owner-gated campaign unit is
   **M0-T107** (unit J, plugin portability plan; dep M0-T096 accepted; non-blocking) —
   claim it unless the owner directs otherwise.
5. **Mechanics proven this unit:** verification entries are FILLED IN PLACE into the
   capture-time skeleton (appending a duplicate trips validator c16 fail-closed); stamp
   `reviewed_manifest_sha256` from `project_control._task_git_identity` (accept refuses
   "stale — identity None" without it); fill → validator EXIT=0 → accept → commit together;
   commit reports before gates; gate `--sha` == live HEAD; commit the CLI's untracked
   submit-record `reports/<task>.json` (G4 will flag it); reviewers dispatched as NAMED
   spawns are read-only-safe and deliver reports via SendMessage after an idle notification.
6. **Environment:** long runs foreground-chunked (whole suite = 4 alphabetical chunks of the
   59 `test_agent_supervisor*.py` files); never mutate during a live suite; registry JSON LF;
   validator ~4–5 min (run in background).
7. **Standing restrictions:** NEVER merge PR #241 or any pre-existing PR; activation
   owner-gated (R187/R595; supervisor SHADOW-ONLY); Amendment-3 prohibitions; Amendment-7
   no-wait/no-provoke; Amendment-8 R233 /btw honesty + R242/R243/R245 Telegram one-way/
   secrets/owner-typed live canary; Bootstrap Gate 0 every session; supervisor commits cite
   `D-024-R###`; repo PUBLIC; never `name:` on producers; expansion-planning hold;
   `.claude/hooks` untouchable sans G5.
8. **Successor must read:** `CLAUDE.md`; this file; `.claude/session-handoff-profile.md`;
   `project-control/campaigns/D-024-fable-codex-loop.json` (seq 26);
   `project-control/reports/M0-T096-activation-package.md` (presentable package);
   `project-control/reports/M0-T112-recertification.md`; `project-control/tasks/M0-T107.json`
   (if claiming unit J); `docs/LEAN_OPERATING_PROCESS.md`.
9. **Stop/change conditions:** Gate-0 failure; validator non-zero; reviewer FAIL/BLOCKED;
   anything owner-only (credentials, payment, production, legal, PR #241, activation,
   Telegram secrets/live send, autostart install, residual-fix authorization if it forces
   re-certification).
10. **Successor prompt:** *"Work from durable repository evidence only. Verify root =
    C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, branch control/D-024-fable-codex-loop, HEAD,
    tree, and /mcp empty (Bootstrap Gate 0) before any change. Read CLAUDE.md,
    docs/SESSION_HANDOFF.md, .claude/session-handoff-profile.md, and the §8 files. Run
    `python tools/project_control.py status` and `python -m
    tools.agent_supervisor.campaign_continuity --status`. Reconcile against live git + the
    ledger (they win over prose). The Amendment-8 sequence is COMPLETE (M0-T112 accepted)
    and the R187/R595 activation package was already PRESENTED (seq 27) — do NOT re-present
    it or prompt for the activation decision; the owner decision set in its item 14 is
    pending. Unless the owner directs otherwise, continue with M0-T107 (unit J, plugin
    portability plan) under the standard controlled-task workflow. Do not merge PR #241 or any pre-existing PR;
    supervisor stays SHADOW-ONLY; guards inside .claude/hooks are untouchable without G5.
    Stop for anything owner-only. The standard D-010 R113/R114 ~400k rotate-at-seam ceiling
    governs your session."*
