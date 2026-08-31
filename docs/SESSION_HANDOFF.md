# Session Handoff - NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live -
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` - and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff - seq 45: Amendment-22/24/25 windows ALL COMPLETE; awaiting the owner's seven-fact commissioning decision

1. **Generated:** 2026-08-31 ~06:5x local by orchestrator session `session_01SfXcRw7emzdojCDJmKxNTM`
   at the natural stop-and-present seam. All sub-agents completed bounded assignments (2 producers
   + reviewers, every producer patch-captured at its seam and retired per R395); nothing in flight;
   tree clean; pushed through the seq-54 campaign advance.
2. **Identity (live at write):** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `control/D-024-fable-codex-loop` (campaign seq **54**), local == origin.
3. **This session end-to-end:** M0-T126 (seven-property checkpoint design + ALL 17 register
   corrections; G3 FAIL -> fresh-producer remediation -> delta PASS; DCV 18/18) -> Amendment 23
   (R395 producer rotate-at-seam patch-capture / R396 never-run-to-exhaustion) -> M0-T127 recert
   (the "3h13m golden" PROVEN an environmental artifact - pack is sub-minute, four datapoints)
   -> Amendment 24 (owner-relayed external review caught the commissioning contradiction;
   staged protocol + R397 hold + R398/R399) -> owner selected OPTION A -> Amendment 25 (R400-R409)
   -> M0-T128 Stage-3 wiring (run_task_queue live at cli.py:3069 behind the owner gate + first-act
   mode guard; eleven-category fail-closed VISIBLE eligibility; CAS advance-before-select;
   --max-tasks/--packet-queue with certified defaults; correction rounds C1/C2/G4-1/O2 closed by a
   fresh producer) -> M0-T129 terminal recert + the seven-fact commissioning protocol (fact-6
   citation corrected via an honest G3 round + dual delta-acks). **T125-T129 ALL ACCEPTED.**
4. **THE FINAL FROZEN IDENTITY:** material `de18f27`, `tools/agent_supervisor` tree
   `b392100930bd4213cab90eb02aafa6d0d568f849`, golden blob `deeca07b`, CLI 2.1.251 supervisor-native
   `d6f6c29a...` (sha256_head+size), codex 0.146.0, activation manifest `841ed11c` (125 files).
   Certified: golden 42/42; whole suite 3035/2/0 (chain 2990+35+10); doctor PASS ACL PROTECTED;
   validator EXIT=0; window DCV summary T126 18/18, T127 22/22+delta, T128 6/6, T129 7/7. Any
   supervisor/operator-channel change re-triggers R247 (now sub-ten-minutes).
5. **EXACT next action - campaign seq-54 NEXT has the full text:** THE OWNER DECIDES. (a) Owner
   names successor task(s) for the commissioning queue; orchestrator prepares packets/claims/
   isolated worktrees under normal Tier A, writes the queue file
   (`{"tasks":[{task_id,packet_path,worktree,branch,repo}...]}`), re-runs the FULL preflight
   (`M0-T129-commissioning-protocol.md` section 2) and reports. (b) Owner personally types the two
   validated commands (protocol section 4: clear-recovery, then the start with `--max-cycles 3
   --max-tasks 3 --packet-queue ...`). The orchestrator NEVER executes them (R409). Any live
   failure: R394 - stop without retry, preserve byte-for-byte, ONE consolidated assessment.
6. **Preservation until the owner acts (R374-era + R401):** journal PAUSED_RECOVERY / transitions
   22 / audit 53 / effects 0; `wt-m0t107` clean @ `796e18f` branch `task/M0-T107-plugin-portability`;
   preserved transcript intact. The owner's Step-1 clear-recovery ENDS this preservation by owner
   decision.
7. **Standing:** never merge PR #241 (OPEN, repeatedly DCV-confirmed untouched); owner-only gates
   unchanged (autostart, C1 canary, Telegram live send, natural-event graduation, OS-ACL,
   production, credentials, payments, legal); R286/287 admission discipline (CLI 2.1.251
   `d6f6c29a` undrifted); Bootstrap Gate 0 every session; supervisor commits cite `D-024-R###`;
   producers UNNAMED + ROSTER-typed, patch-captured at their seam and retired (R395), never run
   toward exhaustion (R396), never resumed after a kill; expansion hold; S16.7 + budgets un-reset.
8. **Successor must read:** `CLAUDE.md`; this file; `.claude/session-handoff-profile.md`;
   `project-control/campaigns/D-024-fable-codex-loop.json` (seq 54 - the full NEXT);
   `project-control/reports/M0-T129-commissioning-protocol.md` (the owner package);
   `M0-T129-recertification.md`; `M0-T128-design-record.md` (the wiring + eligibility rule set);
   `source-025-amendment.md` (R400-R409).
9. **Stop/change conditions:** Gate-0 failure; validator non-zero; any owner-only item; any CLI
   drift (admission event); any live failure (R394 protocol). Campaign next_action text MUST be
   pure ASCII. Registry JSON writes MUST be LF (`newline='\n'`) before digest computation.
   Producer worktree patches: capture via `git -C <wt> add -A; git diff --cached --binary
   --output=<patch>` (NEVER pipe through PowerShell).
10. **Successor prompt:** *"Work from durable repository evidence only. Verify root =
    C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, branch control/D-024-fable-codex-loop, HEAD, tree,
    and /mcp empty (Bootstrap Gate 0) before any change. Read CLAUDE.md, docs/SESSION_HANDOFF.md,
    and the section-8 files. Run `python tools/project_control.py status` and `python -m
    tools.agent_supervisor.campaign_continuity --status`; reconcile against live git + the ledger
    (they win over prose). The Amendment-22/24/25 windows are COMPLETE and M0-T125..M0-T129 are
    all accepted at frozen material de18f27. There is NO pending production work: the campaign
    waits on the OWNER's seven-fact commissioning decision (seq-54 NEXT). If the owner names
    successor tasks, prepare the queue + preflight per M0-T129-commissioning-protocol.md sections
    2-3 and report; NEVER execute the section-4 commands yourself (R409). The standard D-010
    ~400k rotate-at-seam ceiling governs your session."*
