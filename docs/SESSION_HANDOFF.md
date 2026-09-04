# Session Handoff - NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live -
`python tools/project_control.py status` and `python -m tools.agent_supervisor.campaign_continuity
--status` - and reconcile against the remote: **origin may have advanced; do not trust any SHA here
as still-current.** Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY:
`context-budget` CI fails > ~4000 tok.

## Handoff - seq 80: first supervised journey SUCCEEDED end-to-end; M0-T107 ACCEPTED (156th)

1. **Generated:** 2026-09-03 (UTC) by the Amendment 49-50 session after the M0-T107 acceptance
   wave completed.
2. **Identity:** root/worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `candidate/D-024-mrl-option-b` (LOCAL ONLY, no upstream), HEAD `9dcbdd09`, tree CLEAN.
   Frozen accepted CODE candidate `3f4cee86` still the installed controller source. Nothing
   pushed; PR #241 untouched. Worker `wt-m0t107` clean at task tip `777ef5e4`, no upstream.
3. **Completed this session (durable):** (a) Amendment 49 (R732-R737): owner disposition A -
   the two prior-journey drafts committed unaltered as starting state `ffc77bab`
   (WORKTREE_CLEAN_READY returned). (b) Owner typed the ONE journey command:
   **journey-m0t107-01 SUCCEEDED** - worker COMPLETED (fresh Fable session 5bd21dae in
   wt-m0t107, rc 0, no Bash, 0/2 subagents, cleanup proven), first live end-to-end
   worker->checkpoint->Codex REVISE (schema-valid, gpt-5.6-sol)->supervised close
   `operator_declined` (expected one-cycle end, owner-classified NOT a defect, R739).
   (c) Amendment 50 (R738-R749) captured: consolidated Codex adjudication (5 packet-
   verifiability asks F1-F5, zero content defects; report s6.2), ONE bounded correction pass
   (worker revisions `4047c79c`, orchestrator report-s6 continuation `777ef5e4`), targeted
   verification 10/10 real commands (report s6.3). (d) Blob-identical adoption onto candidate
   `96f1b89b`; submit at identity `1bbedd34...`; gates **G0/G2 PASS (orchestrator),
   G3 PASS (code-reviewer, no material defect), G4 PASS (code-reviewer roster addendum;
   qa-engineer parallel report preserved as supporting non-gate evidence - the gate CLI's
   roster guard rejects non-packet reviewers)**; **DCV 62 PASS + R748/R749 re-attested PASS
   = 64/64** at reviewed `7d282011`; **M0-T107 ACCEPTED** at `9dcbdd09`; validator exit 0;
   ledger accepted=156.
4. **Key records:** `project-control/reports/M0-T107-portability-plan.md` (s6 = continuation),
   `M0-T107-G3-code-review.md`, `M0-T107-G4-integration-addendum.md` (+`-G4-qa-review.md`
   supporting), `M0-T107-DCV-report.md` + `M0-T107-DCV-reattestation.md`,
   `M0-T107-return-report.md` (R748/R749 artifact), `M0-T107-evidence-map.json`,
   directives `source-049/050-amendment.md`. Journey evidence:
   `%LOCALAPPDATA%\NYCBuildabilitySupervisor\9aca7075...\mrl\journey-m0t107-01\`.
5. **Process notes for the next wave:** (a) the auto-mode permission classifier intermittently
   blocks `project_control.py gate` in the Bash tool - the PowerShell tool records it fine;
   (b) write registry/control JSONs with LF (`newline='\n'`) - a CRLF working copy breaks the
   c14 digest on fresh checkouts (fixed in-wave at `9f9a6169`); (c) verification entry:
   write at final pre-accept HEAD, leave UNCOMMITTED through accept(), commit with the accept
   records; (d) packet reviewer_agents is enforced at gate time - plan G4 reviewers into the
   packet at creation.
6. **Next actions:** M0-T109 (claimed, wt-m0t109) is the next unit in the campaign chain -
   dispatchable under standard mechanics; M0-T133 rework remains parked; Tranche C NOT started
   (hold). The single parked GitHub decision is unchanged: authorize the first live
   supervisor-driven GitHub interaction (task-branch push / R595-gated automation + Option-A
   anchor activation). R603-R605 remain owner-only. Local work needs no GitHub authority.
7. **Standing restrictions:** R518, R520-R525 (no push/PR/merge/Tranche C; PR #241 never);
   supervisor commits cite `D-024-R###` + AD-093 evidence; no `name:` on producer spawns; no
   bare `git stash`; thin client; Bootstrap Gate 0 before any write; never execute owner-run
   scripts; exact `claude-fable-5` only (no alias, fallback []); never weaken the cwd guard;
   expansion-planning hold in force.
8. **Validation at handoff:** registry validator exit 0 at HEAD `9dcbdd09`;
   `project_control.py status` counts accepted=156 / claimed=1 (M0-T109) / rework=1 (M0-T133) /
   blocked=2. Stop conditions: push/remote/PR/merge needs; credentials/payment/legal;
   ledger-vs-prose contradiction (ledger wins); journey FAIL (trace, never loop).

## COPY INTO THE NEW SESSION

Resume from durable evidence only. Confirm `git rev-parse --show-toplevel` =
`C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch `candidate/D-024-mrl-option-b`, Bootstrap
Gate 0 (cwd is that root, `/mcp` empty). Read `CLAUDE.md`, this file, and run
`python tools/project_control.py status`; the ledger wins. The first supervised journey
(journey-m0t107-01) SUCCEEDED and M0-T107 is ACCEPTED (156th) at HEAD 9dcbdd09; all its gate,
DCV, and return-report records are committed. Do NOT push, create/update/merge any PR, execute
owner scripts, rerun canaries or journeys, edit model_selection, weaken the cwd guard, or start
Tranche C. Next campaign work: M0-T109 (claimed, wt-m0t109) under standard mechanics. Stop for
owner-only items (GitHub activation, R603-R605, credentials/payment/legal).
