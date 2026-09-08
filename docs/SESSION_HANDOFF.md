# Session Handoff - NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume read it live -
`python tools/project_control.py status` - and reconcile; no SHA here is guaranteed current.
Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY: `context-budget` CI fails > ~4000 tok.

## Handoff - seq 89: FIRST PRODUCT FEATURE ACCEPTED (M5-T003, 167th). Loop DOWN - relaunch on next feature.

1. **Generated:** 2026-09-08 ~07:08Z, session ctl24-e5, `/session-handoff` (owner-invoked, reason "").
2. **Identity:** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch `candidate/D-024-mrl-option-b`,
   HEAD `f54a1773`, origin PUBLIC. Tree CLEAN except deliberate untracked `.claude/agent-memory/qa-engineer/*`.
   **Accepted tasks: 167** (M5-T003 accepted this session).

3. **DONE THIS SESSION (D-038 product pivot):** owner directive "run the codex loop nonstop and build the
   software - no more building itself." Diagnosed root cause (product is credential-gated -> loop had turned
   to M0 self-infra). Captured **D-038**; pivoted the loop OFF self-infra onto **M5-T003** (scenario
   endpoint `GET /api/v1/properties/{bbl}/scenario` exposing the built `build_scenario`, flag-gated, OFFLINE,
   no creds). Loop (run persistent-local-19) BUILT it; **accepted 167th** via full T-B gate wave (G0/G1/G3/
   G4/G5 all PASS + directive-compliance-verifier PASS on D-038-R003/R004) at material identity `937de404`.
   Code integrated on the candidate line. **M0-T153/M0-T155 self-infra de-prioritized** (preserved on
   wt-m0t153/wt-m0t155 branches, NOT deleted).

4. **LOOP IS DOWN (killed to freeze the accepted work).** run persistent-local-19 (supervisor pid 12124 +
   worker) was KILLED after M5-T003 UNIT_COMPLETE because the running controller (0.4.0-phase4, no T-B
   auto-accept deployed) kept dispatching over-revise cycles. **Stranded recovery state** at checkout_key
   `9aca7075...`: `CLAUDE_RUNNING`, 0 surviving children, 0 pending effects, **2 pending M5-T003 ASKs** +
   an unreconciled dispatch intent. **NONSTOP DUTY:** the successor RELAUNCHES the loop on the NEXT feature.

5. **EXACT NEXT ACTION (successor):** (a) **Contract the next product feature = Compare (Step 3) UI**
   (e.g. M5-T004 or M2-T021): the Confirm screen dead-ends at "steps 3-4 arrive later"; build `apps/web`
   Compare route + components consuming the accepted scenario endpoint; NO creds (fixtures/offline).
   **Put `documented_test_commands` in the packet** so the loop worker self-verifies (its 3.11 sandbox CAN
   run the API/UI tests; only `app/documents/**` needs 3.12). Bind `directive_refs D-038:ALL`; add the new
   task id to D-038-R003 applicability. (b) Worktree off the candidate HEAD (has scenario.py). (c) **Relaunch
   the loop DETACHED** via `scratchpad/relaunch_m5t003.ps1` pattern (edit task-packet/repo/branch/run-id
   `persistent-local-20`) from cwd `wt-controller-src`, NEVER ctl24. **First apply the task-switch drill**
   (item 7). Re-arm a read-only break watcher.

6. **MODEL - Fable weekly-exhausted; worker PINNED opus-4-8** (`C:\SupervisorController\model_selection.toml`).
   **REVERT to `model="claude-fable-5"` when Fable returns (Thursday 9 PM local, D-036-R001).** opus drops
   the checkpoint ~every 3rd cycle -> run may exit needing restart; work preserved on-branch, just relaunch.

7. **LOOP TASK-SWITCH DRILL (a mid-unit kill trips 3 recovery gates in order):** (a) `pending-approvals
   --checkout C:\SupervisorController` then `deny <req> <digest>` each stale ASK (the 2 M5-T003 asks) -
   clears `pending_requests`; (b) `git -C <new-worktree> reset --hard <candidate HEAD that CONTAINS the new
   packet>` - the `task_authority` probe reads `<--repo>/project-control/tasks/<id>.json` and fails if the
   worktree base predates the packet; (c) reconcile the crashed-mid-unit dispatch intent via
   `recovery.reconcile_dispatch_intent(journal)` (NO CLI verb; run `scratchpad/reconcile_intent.py` after
   read-only evidence) - clears `AMBIGUOUS_EFFECT`. Then `start` reaches SAFE_CHECKPOINT + run_budget_started.
   **LAUNCH BUG:** `--config "C:\Program Files\SupervisorConfig\config.toml"` has a SPACE - MUST be quoted
   inside the Start-Process arg array (autostart-launch.ps1 has the same latent bug). NEVER audit-writing
   operator verbs against a LIVE run.

8. **Sub-agents: none in flight.** All 5 reviewers (data-contract, code, qa, security, directive-compliance)
   COMPLETED + reconciled (reports under `project-control/reports/M5-T003-*`; gates recorded; accept done).
   Watcher stopped (loop down). Evidence-capture division of labor: the worker's 3.11 sandbox + broker can't
   run tests; orchestrator captured them (`M5-T003-orchestrator-captured-evidence.md`) - documented_test_commands
   (item 5) reduces this next time.

9. **Standing restrictions (unchanged):** no push/PR/merge (local-only; GitHub stale, origin/main d8b3899f);
   NEVER merge PR #241; R595 / autostart-activation / continuous-mode owner-only; supervisor SHADOW; expansion
   hold; Bootstrap Gate 0 (cwd=root, `/mcp` empty); supervisor commits cite D-024-R###/AD-093; no bare git
   stash; thin client; R247 recert before NEW supervisor code; launch ONLY from wt-controller-src cwd; owner-
   only = credentials/payment/production/legal (Supabase B-001 + Geoclient B-004 remain the deferred unlock
   for the FULL end-to-end product - surface next session).

10. **Authoritative files:** `project-control/tasks/M5-T003.json` (accepted); `directives/D-038-build-product-
    not-self/` (verification.json v2); `gates/M5-T003-G{0,1,3,4,5}.json`; `reports/M5-T003-*`;
    ledger `state.json`. Ledger wins over this prose.

## COPY INTO THE NEW SESSION

Resume from durable evidence only. Bootstrap Gate 0 (root cwd, `/mcp` empty), branch
`candidate/D-024-mrl-option-b`. Read `CLAUDE.md`, this handoff, then `python tools/project_control.py status`
(ledger wins). Reconcile handoff vs live git + ledger. M5-T003 (scenario endpoint) is ACCEPTED (167th) - do
not redo it. **The loop is DOWN; keep it nonstop:** relaunch DETACHED (run-id `persistent-local-20`) from
`wt-controller-src` on the NEXT product feature = **Compare (Step 3) UI** (contract it first with
`documented_test_commands` + `directive_refs D-038:ALL`; worktree off candidate HEAD). Apply the task-switch
drill (item 7: deny the 2 stranded M5-T003 asks -> reset worktree -> reconcile dispatch intent -> start) and
re-arm a read-only break watcher. Worker on opus-4-8 (revert to Fable Thursday). Do NOT: push/merge/PR #241,
build supervisor self-infra as the loop target (D-038), run audit verbs against a live run, launch from
ctl24-cwd, install new supervisor code without R247 recert, bypass any gate, or require the deferred
credentials. Report READY TO RESUME or BLOCKED.
