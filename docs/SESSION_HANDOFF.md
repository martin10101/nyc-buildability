# Session Handoff - NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live -
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` - and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff - seq 81: Amendment 51 done; M0-T144 ACCEPTED, M0-T109 code+5 gates PASS; terminal = BLOCKED_FOR_PERSISTENT_ACTIVATION (one owner-only gate)

1. **Generated:** 2026-09-04 (UTC) by the Amendment-51 campaign-continuation session.
2. **Identity:** root/worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `candidate/D-024-mrl-option-b` (LOCAL ONLY, no upstream), HEAD `903a6819`, tree CLEAN.
   Frozen accepted CODE candidate `3f4cee86` = installed controller (has M0-T133 checkpoint
   envelope, live-proven). Nothing pushed; PR #241 untouched.
3. **Completed this session (durable):** (a) **M0-T144 ACCEPTED** (D-024 Amendment 51 part B:
   deficit-convergence policy - CLAUDE.md principle 18 + `/deficit-convergence` skill, content
   `6aafd5e4`; 6/6 DCV PASS). (b) **M0-T109 guard-hardening code complete + gates G0/G2/G3/G4/G5
   all PASS** (three M0-T108 residuals closed; content `7f075e37` ≡ task tip `67b5b4dc`; both
   guard suites + modularity + ruff green; Bash pack byte-unchanged). G5 found one MEDIUM bypass
   (`${var}=` braced-assignment shell) proven PRE-EXISTING (base 1c069571, untouched) -> tracked
   as backlog **M0-T145** (not worked). (c) Amendment 51 captured (`source-051-amendment.md`,
   R750-R766). (d) Controller capability map + R753 proof plan + terminal report committed.
   Ledger: accepted=157 / awaiting_gate=10 / backlog=18 / rework=1 (M0-T133) / blocked=2 /
   in_progress=1.
4. **TERMINAL OUTCOME = BLOCKED_FOR_PERSISTENT_ACTIVATION** (`D-024-persistent-activation-terminal.md`):
   the seven local-autonomy facts can be proven LIVE only by the first-ever live limited-auto
   autonomous run (`--mode limited-auto --owner-enable-bounded-auto` on the legacy runner) - a
   genuine **owner-only gate** (real Fable+Codex allowance; the persistent-loop start the owner
   reserved). **Architecture viability = POSITIVE**: the installed controller has every mechanism
   (auto-REVISE loop-back, packet-queue auto-advance, pause/resume, unlimited run wall-clock, and
   the M0-T133 checkpoint envelope). Two owner design caveats: fact-7 foreground view is
   wrapper-assembled not controller-streamed; mid-run Codex guidance is NOT implemented
   (`/loop-ask`+`/loop-codex` are between-cycle only). M0-T109 acceptance is correctly coupled to
   this gate via R754 (UNVERIFIABLE until the live run); do NOT force it.
5. **M0-T109 status:** awaiting_gate @ 95%; all five gates + DCV recorded; acceptance pending the
   owner-gated live run (R754). When the owner runs the live limited-auto queue and the seven
   facts are durably evidenced, re-verify R754 (+R759/R760 resolve) and accept M0-T109.
6. **Exact owner activation handover** (in the terminal report §5, generated from live identities):
   the persistent-loop start command (`start --mode limited-auto --owner-enable-bounded-auto
   --packet-queue <ordered.json> --max-tasks 2 --max-cycles 3 --run-id persistent-local-01`, NO
   `--run-wall-clock-seconds`), status/pause/resume/graceful-stop commands, the honest
   no-mid-run-Codex-guidance statement, the post-activation explanation, and the exact
   R595/Option-A + R603-R605 authorization statement for the separate GitHub lifecycle.
7. **Non-blocking follow-ups (ledger hygiene, NOT gates on the live run):** M0-T133 (rework) is
   re-gateable now that M0-T136 resolved its modularity ceiling and its code is already installed +
   live-proven; M0-T145 (braced-variable guard residual) is backlog; the fact-7 foreground-view
   decision is the owner's.
8. **Standing restrictions (unchanged):** exact `claude-fable-5` worker + `gpt-5.6-sol` reviewer;
   no push/PR/merge/deploy/Tranche C; PR #241 never; no controller/model-selection/cwd-guard edit
   unless an authorized task requires it; no guard weakened; supervisor commits cite `D-024-R###`;
   no `name:` on producer spawns; no bare `git stash`; thin client; Bootstrap Gate 0 before writes;
   never execute owner-run scripts; the first live limited-auto run + R595/Option-A + R603-R605
   stay owner-only.
9. **Validation at handoff:** registry validator exit 0 at HEAD `903a6819`. Stop conditions:
   push/remote/PR/merge; credentials/payment/legal; the owner-only live-run gate; ledger-vs-prose
   contradiction (ledger wins).

## COPY INTO THE NEW SESSION

Resume from durable evidence only. Confirm `git rev-parse --show-toplevel` =
`C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch `candidate/D-024-mrl-option-b`, Bootstrap
Gate 0. Read `CLAUDE.md`, this file, `project-control/reports/D-024-persistent-activation-terminal.md`,
and run `python tools/project_control.py status`; the ledger wins. Amendment 51 is complete:
M0-T144 ACCEPTED (deficit-convergence policy), M0-T109 code + all five gates + DCV done with
acceptance correctly BLOCKED by R754. The campaign terminal is BLOCKED_FOR_PERSISTENT_ACTIVATION -
one owner-only gate remains (the first live limited-auto autonomous run) and the architecture is
viable with the exact activation command handed over. Do NOT push/PR/merge, execute owner scripts,
launch the live limited-auto run, edit the controller/model-selection/cwd-guard, or activate
R595/Option-A or R603-R605. When the owner runs the live loop, accept M0-T109 after re-verifying
R754. Stop for owner-only items.
